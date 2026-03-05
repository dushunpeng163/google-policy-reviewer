"""
政策监控引擎

职责：
1. 订阅 Apple / Google 官方 RSS，实时感知政策公告
2. 定期抓取官方政策页面，通过 SHA-256 哈希对比检测内容变化
3. 将每条规则的"距上次验证天数"暴露给 API 层
4. 不负责自动解读政策变化 —— 变化发现后须人工（或 LLM）复核并更新规则代码

使用方式：
  python3 engines/policy_monitor.py                  # 新鲜度报告（离线）
  python3 engines/policy_monitor.py --report         # 输出 JSON 报告
  python3 engines/policy_monitor.py --fetch          # 抓取页面并检测哈希变化（需联网）
  python3 engines/policy_monitor.py --rss            # 拉取 RSS 公告，过滤政策相关条目（需联网）
  python3 engines/policy_monitor.py --watch 3600     # 每隔 N 秒自动轮询 RSS + 页面（持续运行）
  python3 engines/policy_monitor.py --mark-verified apple_app_store:iap_3_1_1
  python3 engines/policy_monitor.py --mark-all-verified
"""

import hashlib
import json
import os
import sys
import time
import datetime
import argparse
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Any, Optional, List

try:
    import urllib.request
    import urllib.error
    HAS_URLLIB = True
except ImportError:
    HAS_URLLIB = False

# ── 路径配置 ────────────────────────────────────────────────────────────────
ROOT_DIR = Path(__file__).parent.parent
VERSIONS_FILE = ROOT_DIR / "policy_versions.json"
CACHE_DIR = ROOT_DIR / ".policy_cache"
CACHE_DIR.mkdir(exist_ok=True)

STALENESS_DAYS_DEFAULT = 90   # 超过此天数未验证的规则标记为 potentially_outdated
CRITICAL_STALENESS_DAYS = 180  # 超过此天数标记为 outdated（危险）


# ── 核心工具函数 ────────────────────────────────────────────────────────────
def load_versions() -> Dict[str, Any]:
    if not VERSIONS_FILE.exists():
        return {}
    with open(VERSIONS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_versions(data: Dict[str, Any]) -> None:
    with open(VERSIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def days_since(date_str: Optional[str]) -> Optional[int]:
    """计算距 date_str（YYYY-MM-DD）过了多少天"""
    if not date_str:
        return None
    try:
        d = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        return (datetime.date.today() - d).days
    except ValueError:
        return None


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


_BROWSER_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/122.0.0.0 Safari/537.36"
)

# 已知需要 JS 渲染、urllib 无法有效抓取的页面
_JS_REQUIRED_DOMAINS = [
    "play.google.com",
    "support.google.com",
]


def _is_js_heavy(content: str) -> bool:
    """粗判断页面是否为 JS 渲染壳（正文极少，script 标签很多）"""
    text_len = len(re.sub(r"<[^>]+>", "", content))
    script_count = content.count("<script")
    return text_len < 500 and script_count > 3


def fetch_page_text(url: str, timeout: int = 15) -> Optional[str]:
    """抓取页面文本（向后兼容接口，内部调用 fetch_page_smart）"""
    result = fetch_page_smart(url, timeout=timeout)
    return result.get("content") if result["status"] == "ok" else None


def fetch_page_smart(
    url: str,
    timeout: int = 15,
    etag: Optional[str] = None,
    last_modified: Optional[str] = None,
) -> Dict[str, Any]:
    """
    智能页面抓取，支持 HTTP 缓存协商（ETag / Last-Modified）。

    返回字典：
      status      : 'ok' | 'not_modified' | 'failed' | 'js_required'
      content     : 页面文本（status='ok' 时有值）
      etag        : 响应 ETag（可存储供下次使用）
      last_modified: 响应 Last-Modified
      error       : 错误信息（status='failed' 时有值）
    """
    result: Dict[str, Any] = {
        "status": "failed",
        "content": None,
        "etag": None,
        "last_modified": None,
        "error": None,
    }

    if not HAS_URLLIB:
        result["error"] = "urllib 不可用"
        return result

    # 已知 JS 渲染页面，直接跳过
    from urllib.parse import urlparse
    domain = urlparse(url).netloc
    if any(js_domain in domain for js_domain in _JS_REQUIRED_DOMAINS):
        result["status"] = "js_required"
        result["error"] = "该页面需要 JavaScript 渲染，urllib 无法有效抓取"
        return result

    try:
        headers = {
            "User-Agent": _BROWSER_UA,
            "Accept": "text/html,application/xhtml+xml,*/*",
            "Accept-Language": "en-US,en;q=0.9",
        }
        # 发送缓存协商头，如果服务器支持会返回 304
        if etag:
            headers["If-None-Match"] = etag
        if last_modified:
            headers["If-Modified-Since"] = last_modified

        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            content = resp.read().decode("utf-8", errors="replace")
            resp_etag = resp.getheader("ETag")
            resp_lm = resp.getheader("Last-Modified")

            # 判断是否 JS 渲染壳
            if _is_js_heavy(content):
                result["status"] = "js_required"
                result["error"] = "页面内容为 JS 渲染壳，哈希检测不可靠"
                result["etag"] = resp_etag
                result["last_modified"] = resp_lm
                return result

            result["status"] = "ok"
            result["content"] = content
            result["etag"] = resp_etag
            result["last_modified"] = resp_lm

    except urllib.error.HTTPError as e:
        if e.code == 304:
            result["status"] = "not_modified"
        else:
            result["status"] = "failed"
            result["error"] = f"HTTP {e.code}: {e.reason}"
    except Exception as e:
        result["status"] = "failed"
        result["error"] = str(e)

    return result


def cache_path_for_url(url: str) -> Path:
    safe_name = sha256_text(url)[:16]
    return CACHE_DIR / f"{safe_name}.html"


# ── 新鲜度分析 ──────────────────────────────────────────────────────────────
def analyze_freshness(versions: Dict[str, Any]) -> Dict[str, Any]:
    """
    分析所有规则的新鲜度，返回结构化报告。
    不需要联网，仅基于 last_verified 日期计算。
    """
    meta = versions.get("_meta", {})
    staleness_threshold = meta.get("staleness_days", STALENESS_DAYS_DEFAULT)

    report = {
        "generated_at": datetime.datetime.now().isoformat(),
        "staleness_threshold_days": staleness_threshold,
        "overall_status": "fresh",   # fresh | warning | critical
        "platforms": {},
        "summary": {
            "total_rules": 0,
            "fresh": 0,
            "potentially_outdated": 0,
            "outdated": 0,
            "unknown": 0,
        },
        "page_change_alerts": [],   # 页面哈希变化告警
        "outdated_rules": [],       # 需要人工复核的规则列表
    }

    for platform_key in ("apple_app_store", "google_play_store"):
        platform_data = versions.get(platform_key, {})
        rules = platform_data.get("rules", {})
        platform_report = {
            "rules_total": len(rules),
            "rules_fresh": 0,
            "rules_potentially_outdated": 0,
            "rules_outdated": 0,
            "rules_unknown": 0,
            "rule_details": [],
        }

        for rule_id, rule in rules.items():
            last_verified = rule.get("last_verified")
            age_days = days_since(last_verified)
            report["summary"]["total_rules"] += 1

            if age_days is None:
                status = "unknown"
                report["summary"]["unknown"] += 1
                platform_report["rules_unknown"] += 1
            elif age_days >= CRITICAL_STALENESS_DAYS:
                status = "outdated"
                report["summary"]["outdated"] += 1
                platform_report["rules_outdated"] += 1
                report["outdated_rules"].append({
                    "platform": platform_key,
                    "rule_id": rule_id,
                    "title": rule.get("title", rule_id),
                    "last_verified": last_verified,
                    "age_days": age_days,
                    "source_url": rule.get("source_url", ""),
                    "severity": "critical",
                })
            elif age_days >= staleness_threshold:
                status = "potentially_outdated"
                report["summary"]["potentially_outdated"] += 1
                platform_report["rules_potentially_outdated"] += 1
                report["outdated_rules"].append({
                    "platform": platform_key,
                    "rule_id": rule_id,
                    "title": rule.get("title", rule_id),
                    "last_verified": last_verified,
                    "age_days": age_days,
                    "source_url": rule.get("source_url", ""),
                    "severity": "warning",
                })
            else:
                status = "fresh"
                report["summary"]["fresh"] += 1
                platform_report["rules_fresh"] += 1

            platform_report["rule_details"].append({
                "rule_id": rule_id,
                "title": rule.get("title", rule_id),
                "status": status,
                "last_verified": last_verified,
                "age_days": age_days,
                "guideline_ref": rule.get("guideline_ref", ""),
                "source_url": rule.get("source_url", ""),
                "notes": rule.get("notes", ""),
                "deadline_notes": rule.get("deadline_notes", ""),
            })

        report["platforms"][platform_key] = platform_report

    # 计算整体状态
    if report["summary"]["outdated"] > 0:
        report["overall_status"] = "critical"
    elif report["summary"]["potentially_outdated"] > 0:
        report["overall_status"] = "warning"
    else:
        report["overall_status"] = "fresh"

    return report


# ── 页面变化检测 ─────────────────────────────────────────────────────────────
def check_page_changes(versions: Dict[str, Any], verbose: bool = True) -> List[Dict]:
    """
    抓取官方政策页面，对比哈希，返回发生变化的页面列表。
    - 成功抓取且内容无变化 → 更新 last_verified（确认规则仍有效）
    - 成功抓取且内容变化   → 告警，不更新 last_verified（需人工复核）
    - 抓取失败 / JS页面    → 记录失败状态，不更新任何验证时间
    """
    alerts = []
    now_iso = datetime.datetime.now().isoformat()
    today = datetime.date.today().isoformat()

    for platform_key in ("apple_app_store", "google_play_store"):
        platform_data = versions.get(platform_key, {})
        source_urls = platform_data.get("source_urls", {})
        stored_hashes = platform_data.get("page_hashes", {})
        # 存储每个 URL 的 ETag / Last-Modified / 检查状态
        url_meta = platform_data.setdefault("url_check_meta", {})

        for url_name, url in source_urls.items():
            if verbose:
                print(f"  正在检查: {url_name} ({url[:70]})")

            meta = url_meta.get(url_name, {})
            fetch_res = fetch_page_smart(
                url,
                etag=meta.get("etag"),
                last_modified=meta.get("last_modified"),
            )

            # 记录本次检查时间
            meta["last_check_attempted"] = now_iso
            meta["check_status"] = fetch_res["status"]

            if fetch_res["status"] == "not_modified":
                # 服务器确认内容未变（304），可信赖地更新 last_verified
                meta["etag"] = fetch_res.get("etag") or meta.get("etag")
                meta["last_modified"] = fetch_res.get("last_modified") or meta.get("last_modified")
                _mark_rules_verified(versions, platform_key, today, source="page_304")
                if verbose:
                    print(f"    ✅ 服务器确认未变化（304 Not Modified）→ last_verified 已更新")

            elif fetch_res["status"] == "ok":
                page_text = fetch_res["content"]
                meta["etag"] = fetch_res.get("etag") or meta.get("etag")
                meta["last_modified"] = fetch_res.get("last_modified") or meta.get("last_modified")
                current_hash = sha256_text(page_text)
                stored_hash = stored_hashes.get(url_name)

                if stored_hash is None:
                    stored_hashes[url_name] = current_hash
                    cache_path_for_url(url).write_text(page_text, encoding="utf-8")
                    _mark_rules_verified(versions, platform_key, today, source="page_first")
                    if verbose:
                        print(f"    ✅ 首次记录哈希，last_verified 已设置")
                elif stored_hash == current_hash:
                    _mark_rules_verified(versions, platform_key, today, source="page_hash_match")
                    if verbose:
                        print(f"    ✅ 内容无变化 ({current_hash[:12]}…) → last_verified 已更新")
                else:
                    # 内容变化：告警，不更新 last_verified，等待人工复核
                    old_cache = cache_path_for_url(url)
                    alerts.append({
                        "platform": platform_key,
                        "url_name": url_name,
                        "url": url,
                        "previous_hash": stored_hash,
                        "current_hash": current_hash,
                        "detected_at": now_iso,
                        "action_required": "页面内容已变化，需人工复核后手动调用 --mark-verified 更新",
                    })
                    stored_hashes[url_name] = current_hash
                    old_cache.write_text(page_text, encoding="utf-8")
                    if verbose:
                        print(f"    🚨 内容变化！last_verified 未更新（需人工复核）")

            elif fetch_res["status"] == "js_required":
                meta["check_status"] = "js_required"
                if verbose:
                    print(f"    ⚠️  JS 渲染页面，需浏览器抓取（已跳过）")
            else:
                if verbose:
                    print(f"    ❌ 抓取失败: {fetch_res.get('error', '未知错误')}")

            url_meta[url_name] = meta
        versions[platform_key]["url_check_meta"] = url_meta
        versions[platform_key]["page_hashes"] = stored_hashes

    return alerts


def _mark_rules_verified(versions: Dict, platform_key: str, today: str, source: str = "page") -> None:
    """将平台下所有规则的 last_verified 更新为 today（仅当页面检查确认无变化时调用）"""
    rules = versions.get(platform_key, {}).get("rules", {})
    for rule in rules.values():
        if rule.get("verified_by", "manual") != "manual_bulk_override":
            rule["last_verified"] = today
            rule["verified_by"] = source


# ── RSS 自动监控 ─────────────────────────────────────────────────────────────

# 官方 RSS 订阅源
RSS_SOURCES = [
    {
        "name": "Apple Developer News",
        "platform": "apple_app_store",
        "url": "https://developer.apple.com/news/rss/news.rss",
        "description": "Apple 官方开发者新闻，政策更新会在此发布",
    },
    {
        "name": "Android Developers Blog",
        "platform": "google_play_store",
        "url": "https://feeds.feedburner.com/blogspot/hsDu",
        "description": "Google Android 开发者博客，Play Store 政策变化会在此公告",
    },
    {
        "name": "Google Play Policy Updates",
        "platform": "google_play_store",
        "url": "https://support.google.com/googleplay/android-developer/answer/9904819",
        "description": "Google Play 政策中心（页面哈希监控）",
        "type": "page",  # 非 RSS，走页面哈希检测
    },
]

# 触发"政策相关"判断的关键词（不区分大小写）
POLICY_KEYWORDS = [
    # 英文
    "policy", "policies", "guideline", "guidelines", "review", "billing",
    "privacy", "data safety", "permission", "target api", "sdk", "iap",
    "in-app purchase", "tracking", "att", "coppa", "gdpr", "account deletion",
    "app store", "play store", "compliance", "enforcement", "violation",
    "deceptive", "children", "kids", "family", "age rating", "content rating",
    "subscription", "refund", "developer program",
    # 中文（如果 RSS 支持中文内容）
    "政策", "合规", "指南", "隐私", "权限", "儿童", "订阅", "计费", "审核",
]

RSS_SEEN_FILE = CACHE_DIR / "rss_seen_items.json"


def _load_seen_items() -> set:
    """加载已处理过的 RSS 条目 ID，避免重复告警"""
    if RSS_SEEN_FILE.exists():
        try:
            data = json.loads(RSS_SEEN_FILE.read_text(encoding="utf-8"))
            return set(data)
        except Exception:
            return set()
    return set()


def _save_seen_items(seen: set) -> None:
    RSS_SEEN_FILE.write_text(
        json.dumps(sorted(seen), ensure_ascii=False, indent=2), encoding="utf-8"
    )


def _is_policy_related(title: str, description: str) -> bool:
    """判断 RSS 条目是否与政策相关"""
    text = (title + " " + description).lower()
    return any(kw.lower() in text for kw in POLICY_KEYWORDS)


def _parse_rss(xml_text: str) -> List[Dict]:
    """解析 RSS/Atom XML，返回条目列表"""
    items = []
    try:
        root = ET.fromstring(xml_text)
        ns = {}

        # 尝试 RSS 2.0 格式
        for item in root.iter("item"):
            title_el = item.find("title")
            link_el = item.find("link")
            desc_el = item.find("description")
            pub_el = item.find("pubDate")
            guid_el = item.find("guid")

            title = title_el.text if title_el is not None else ""
            link = link_el.text if link_el is not None else ""
            desc = desc_el.text if desc_el is not None else ""
            pub_date = pub_el.text if pub_el is not None else ""
            guid = guid_el.text if guid_el is not None else link

            items.append({
                "id": guid or link,
                "title": title,
                "link": link,
                "description": desc[:300] if desc else "",
                "pub_date": pub_date,
                "format": "rss2",
            })

        # 尝试 Atom 格式（如果 RSS 没有 item）
        if not items:
            atom_ns = "http://www.w3.org/2005/Atom"
            for entry in root.iter(f"{{{atom_ns}}}entry"):
                title_el = entry.find(f"{{{atom_ns}}}title")
                id_el = entry.find(f"{{{atom_ns}}}id")
                link_el = entry.find(f"{{{atom_ns}}}link")
                summary_el = entry.find(f"{{{atom_ns}}}summary")
                updated_el = entry.find(f"{{{atom_ns}}}updated")

                title = title_el.text if title_el is not None else ""
                guid = id_el.text if id_el is not None else ""
                link = link_el.get("href", "") if link_el is not None else ""
                desc = summary_el.text if summary_el is not None else ""
                pub_date = updated_el.text if updated_el is not None else ""

                items.append({
                    "id": guid or link,
                    "title": title,
                    "link": link,
                    "description": desc[:300] if desc else "",
                    "pub_date": pub_date,
                    "format": "atom",
                })

    except ET.ParseError:
        pass

    return items


def fetch_rss_alerts(verbose: bool = True) -> List[Dict]:
    """
    拉取所有 RSS 源，过滤出政策相关新条目，返回告警列表。
    已处理的条目记录在 .policy_cache/rss_seen_items.json，不重复告警。
    """
    seen = _load_seen_items()
    new_alerts = []

    rss_sources = [s for s in RSS_SOURCES if s.get("type") != "page"]

    for source in rss_sources:
        if verbose:
            print(f"\n  📡 [{source['platform']}] {source['name']}")
            print(f"     {source['url']}")

        xml_text = fetch_page_text(source["url"])
        if xml_text is None:
            if verbose:
                print(f"     ⚠️  无法访问（网络受限或超时）")
            continue

        items = _parse_rss(xml_text)
        if verbose:
            print(f"     获取到 {len(items)} 条条目")

        policy_count = 0
        for item in items:
            if item["id"] in seen:
                continue  # 已处理过

            if _is_policy_related(item["title"], item["description"]):
                policy_count += 1
                alert = {
                    "type": "rss_policy_announcement",
                    "platform": source["platform"],
                    "source_name": source["name"],
                    "title": item["title"],
                    "link": item["link"],
                    "pub_date": item["pub_date"],
                    "summary": item["description"],
                    "detected_at": datetime.datetime.now().isoformat(),
                    "action": "请阅读原文，确认是否需要更新合规规则",
                }
                new_alerts.append(alert)

                if verbose:
                    print(f"\n     🚨 政策相关公告：{item['title']}")
                    print(f"        发布时间: {item['pub_date']}")
                    print(f"        链接: {item['link']}")

            seen.add(item["id"])

        if verbose and policy_count == 0:
            print(f"     ✅ 无新政策相关条目")

    _save_seen_items(seen)
    return new_alerts


def save_alerts_log(alerts: List[Dict]) -> Path:
    """将告警写入日志文件"""
    log_file = CACHE_DIR / "policy_alerts.jsonl"
    with open(log_file, "a", encoding="utf-8") as f:
        for alert in alerts:
            f.write(json.dumps(alert, ensure_ascii=False) + "\n")
    return log_file


def watch_loop(interval_seconds: int, verbose: bool = True) -> None:
    """
    持续轮询模式：每隔 interval_seconds 秒检查一次 RSS + 页面哈希。
    适合在服务器上作为后台进程运行，或用 cron 调度。
    """
    print(f"\n👁  进入持续监控模式（每 {interval_seconds} 秒检查一次）")
    print(f"   RSS 源: {len([s for s in RSS_SOURCES if s.get('type') != 'page'])} 个")
    print(f"   按 Ctrl+C 停止\n")

    versions = load_versions()
    check_count = 0

    while True:
        check_count += 1
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{now}] 第 {check_count} 次检查...")

        # 1. RSS 新公告
        rss_alerts = fetch_rss_alerts(verbose=verbose)

        # 2. 页面哈希变化
        page_alerts = check_page_changes(versions, verbose=verbose)
        versions["_meta"]["last_monitor_run"] = datetime.datetime.now().isoformat()
        save_versions(versions)

        all_alerts = rss_alerts + page_alerts
        if all_alerts:
            log_file = save_alerts_log(all_alerts)
            print(f"\n  ⚠️  发现 {len(all_alerts)} 个新告警，已写入: {log_file}")
            print(f"  📋 建议立即查看并更新相关合规规则\n")
        else:
            print(f"  ✅ 无新变化\n")

        print(f"  下次检查: {interval_seconds} 秒后...")
        try:
            time.sleep(interval_seconds)
        except KeyboardInterrupt:
            print("\n👋 监控已停止")
            break


def print_recent_alerts(limit: int = 20) -> None:
    """打印最近的告警记录"""
    log_file = CACHE_DIR / "policy_alerts.jsonl"
    if not log_file.exists():
        print("  暂无告警记录（运行 --rss 或 --watch 后会生成）")
        return

    lines = log_file.read_text(encoding="utf-8").strip().splitlines()
    recent = lines[-limit:] if len(lines) > limit else lines

    print(f"\n  最近 {len(recent)} 条告警记录：\n")
    for line in reversed(recent):
        try:
            alert = json.loads(line)
            icon = "🚨" if alert.get("type") == "rss_policy_announcement" else "📄"
            print(f"  {icon} [{alert.get('platform', '')}] {alert.get('title', alert.get('url_name', ''))}")
            print(f"     时间: {alert.get('detected_at', '')[:19]}")
            if alert.get("link"):
                print(f"     链接: {alert['link']}")
            print()
        except Exception:
            pass


# ── 人工验证更新 ─────────────────────────────────────────────────────────────
def mark_rule_verified(platform: str, rule_id: str, notes: str = "") -> bool:
    """将指定规则的 last_verified 更新为今天（人工复核后调用）"""
    versions = load_versions()
    platform_data = versions.get(platform, {})
    rules = platform_data.get("rules", {})

    if rule_id not in rules:
        return False

    rules[rule_id]["last_verified"] = datetime.date.today().isoformat()
    rules[rule_id]["verified_by"] = "manual"
    if notes:
        rules[rule_id]["notes"] = notes

    save_versions(versions)
    return True


def mark_all_verified(platform: Optional[str] = None) -> int:
    """批量将规则标记为今天验证（谨慎使用：仅在全面复核后调用）"""
    versions = load_versions()
    today = datetime.date.today().isoformat()
    count = 0

    platforms = [platform] if platform else ["apple_app_store", "google_play_store"]
    for p in platforms:
        for rule_id in versions.get(p, {}).get("rules", {}):
            versions[p]["rules"][rule_id]["last_verified"] = today
            versions[p]["rules"][rule_id]["verified_by"] = "manual_bulk"
            count += 1

    save_versions(versions)
    return count


# ── 格式化输出 ───────────────────────────────────────────────────────────────
def print_freshness_report(report: Dict[str, Any]) -> None:
    status_emoji = {"fresh": "✅", "warning": "⚠️", "critical": "🚨"}.get(
        report["overall_status"], "❓"
    )
    s = report["summary"]
    print(f"\n{'='*60}")
    print(f"  政策规则新鲜度报告  {status_emoji} 整体状态: {report['overall_status'].upper()}")
    print(f"{'='*60}")
    print(f"  生成时间: {report['generated_at'][:19]}")
    print(f"  过期阈值: {report['staleness_threshold_days']} 天")
    print(f"\n  规则统计:")
    print(f"    总计        : {s['total_rules']}")
    print(f"    ✅ 新鲜      : {s['fresh']}")
    print(f"    ⚠️  待复核    : {s['potentially_outdated']}")
    print(f"    🚨 严重过期  : {s['outdated']}")
    print(f"    ❓ 未知      : {s['unknown']}")

    if report["outdated_rules"]:
        print(f"\n  需要复核的规则：")
        for r in report["outdated_rules"]:
            icon = "🚨" if r["severity"] == "critical" else "⚠️"
            age = f"{r['age_days']}天" if r["age_days"] else "未知"
            print(f"\n    {icon} [{r['platform']}] {r['title']}")
            print(f"       最后验证: {r['last_verified']}（{age}前）")
            print(f"       官方来源: {r['source_url']}")
    else:
        print("\n  ✅ 所有规则均在新鲜期内")
    print(f"{'='*60}\n")


# ── CLI 入口 ─────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="政策监控工具 - Apple/Google 政策实时监控与新鲜度管理",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  python3 engines/policy_monitor.py                  # 查看规则新鲜度（离线）
  python3 engines/policy_monitor.py --rss            # 拉取官方 RSS，检测政策公告
  python3 engines/policy_monitor.py --fetch          # 检测政策页面内容变化
  python3 engines/policy_monitor.py --watch 3600     # 每小时自动监控一次（持续运行）
  python3 engines/policy_monitor.py --alerts         # 查看历史告警记录
  python3 engines/policy_monitor.py --mark-verified apple_app_store:iap_3_1_1
        """,
    )
    parser.add_argument("--report", action="store_true", help="输出 JSON 格式报告")
    parser.add_argument("--fetch", action="store_true", help="检测政策页面内容变化（需联网）")
    parser.add_argument("--rss", action="store_true", help="拉取官方 RSS 检测政策公告（需联网）")
    parser.add_argument(
        "--watch",
        metavar="SECONDS",
        type=int,
        nargs="?",
        const=3600,
        help="持续监控模式，每隔 N 秒检查一次（默认 3600 秒）",
    )
    parser.add_argument("--alerts", action="store_true", help="查看历史告警记录")
    parser.add_argument(
        "--mark-verified",
        metavar="PLATFORM:RULE_ID",
        help="将指定规则标记为今天已验证，例如: apple_app_store:iap_3_1_1",
    )
    parser.add_argument(
        "--mark-all-verified",
        metavar="PLATFORM",
        nargs="?",
        const="all",
        help="批量标记所有规则为已验证（可选指定平台）",
    )
    args = parser.parse_args()

    # ── 持续监控模式（优先级最高）────────────────────────────────────
    if args.watch is not None:
        watch_loop(interval_seconds=args.watch, verbose=True)
        return

    # ── 标记验证 ────────────────────────────────────────────────────
    if args.mark_verified:
        parts = args.mark_verified.split(":", 1)
        if len(parts) != 2:
            print("格式错误，应为 PLATFORM:RULE_ID")
            sys.exit(1)
        ok = mark_rule_verified(parts[0], parts[1])
        print("✅ 已更新" if ok else "❌ 未找到该规则")
        return

    if args.mark_all_verified:
        p = None if args.mark_all_verified == "all" else args.mark_all_verified
        count = mark_all_verified(p)
        print(f"✅ 已将 {count} 条规则标记为今天已验证")
        return

    # ── 查看历史告警 ─────────────────────────────────────────────────
    if args.alerts:
        print("\n📋 历史政策告警记录")
        print("=" * 60)
        print_recent_alerts()
        return

    versions = load_versions()
    all_alerts = []

    # ── RSS 监控 ─────────────────────────────────────────────────────
    if args.rss:
        print("\n📡 正在拉取官方 RSS 订阅源（需要联网）...")
        print("=" * 60)
        rss_alerts = fetch_rss_alerts(verbose=True)
        all_alerts.extend(rss_alerts)
        if rss_alerts:
            save_alerts_log(rss_alerts)
            print(f"\n🚨 发现 {len(rss_alerts)} 条新政策相关公告，已记录到告警日志")
            print("   运行 --alerts 查看详情")
        else:
            print("\n✅ 无新政策相关公告")

    # ── 页面哈希检测 ─────────────────────────────────────────────────
    if args.fetch:
        print("\n🌐 正在检测政策页面内容变化（需要联网）...")
        print("=" * 60)
        page_alerts = check_page_changes(versions, verbose=True)
        all_alerts.extend(page_alerts)
        versions["_meta"]["last_monitor_run"] = datetime.datetime.now().isoformat()
        save_versions(versions)
        if page_alerts:
            save_alerts_log(page_alerts)
            print(f"\n🚨 发现 {len(page_alerts)} 个页面内容变化，需要人工复核")
        else:
            print("\n✅ 所有监控页面内容无变化")

    # ── 新鲜度报告（默认展示）───────────────────────────────────────
    freshness = analyze_freshness(versions)
    if args.report:
        print(json.dumps(freshness, ensure_ascii=False, indent=2))
    else:
        print_freshness_report(freshness)

    if not args.rss and not args.fetch:
        print("💡 联网检查命令：")
        print("   RSS 公告监控  : python3 engines/policy_monitor.py --rss")
        print("   页面变化检测  : python3 engines/policy_monitor.py --fetch")
        print("   持续自动监控  : python3 engines/policy_monitor.py --watch 3600\n")


if __name__ == "__main__":
    main()
