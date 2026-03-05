"""
政策变化 LLM 分析引擎

当 policy_monitor 检测到官方政策页面内容变化后，
自动调用 LLM（OpenAI / Anthropic Claude）分析：
  1. 这次变化改了什么（人话摘要）
  2. 影响哪些规则（按 policy_versions.json 中的 rule_id 对应）
  3. 对 Unity 游戏开发者的具体影响
  4. 建议的代码修改方向

配置方式（任选一种 LLM）：
  export OPENAI_API_KEY=sk-xxx
  export ANTHROPIC_API_KEY=sk-ant-xxx

使用：
  from engines.policy_diff_analyzer import analyze_policy_diff
  result = analyze_policy_diff(old_text, new_text, platform, url)
"""

import os
import json
import hashlib
import datetime
from pathlib import Path
from typing import Dict, Any, Optional

ROOT_DIR = Path(__file__).parent.parent
ANALYSIS_CACHE_DIR = ROOT_DIR / ".policy_cache" / "llm_analysis"
ANALYSIS_CACHE_DIR.mkdir(parents=True, exist_ok=True)


# ── LLM 调用层 ────────────────────────────────────────────────────────────────

def _call_openai(prompt: str, model: str = "gpt-4o") -> str:
    try:
        import urllib.request
        import json as _json

        api_key = os.environ.get("OPENAI_API_KEY", "")
        if not api_key:
            raise ValueError("未设置 OPENAI_API_KEY 环境变量")

        payload = _json.dumps({
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
            "max_tokens": 1500,
        }).encode("utf-8")

        req = urllib.request.Request(
            "https://api.openai.com/v1/chat/completions",
            data=payload,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = _json.loads(resp.read())
            return data["choices"][0]["message"]["content"]
    except Exception as e:
        raise RuntimeError(f"OpenAI 调用失败: {e}")


def _call_anthropic(prompt: str, model: str = "claude-3-5-sonnet-20241022") -> str:
    try:
        import urllib.request
        import json as _json

        api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        if not api_key:
            raise ValueError("未设置 ANTHROPIC_API_KEY 环境变量")

        payload = _json.dumps({
            "model": model,
            "max_tokens": 1500,
            "messages": [{"role": "user", "content": prompt}],
        }).encode("utf-8")

        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=payload,
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json",
            },
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = _json.loads(resp.read())
            return data["content"][0]["text"]
    except Exception as e:
        raise RuntimeError(f"Anthropic 调用失败: {e}")


def _call_llm(prompt: str) -> Dict[str, Any]:
    """自动选择可用的 LLM，优先 Anthropic Claude"""
    errors = []

    if os.environ.get("ANTHROPIC_API_KEY"):
        try:
            text = _call_anthropic(prompt)
            return {"provider": "anthropic", "text": text}
        except Exception as e:
            errors.append(f"Anthropic: {e}")

    if os.environ.get("OPENAI_API_KEY"):
        try:
            text = _call_openai(prompt)
            return {"provider": "openai", "text": text}
        except Exception as e:
            errors.append(f"OpenAI: {e}")

    raise RuntimeError(
        "未配置可用的 LLM API Key。\n"
        "请设置以下任一环境变量：\n"
        "  export ANTHROPIC_API_KEY=sk-ant-xxx\n"
        "  export OPENAI_API_KEY=sk-xxx\n"
        f"错误详情: {'; '.join(errors)}"
    )


# ── 文本差异提取 ──────────────────────────────────────────────────────────────

def _extract_text_diff(old_text: str, new_text: str, max_chars: int = 4000) -> str:
    """
    提取新旧文本的差异片段，只取变化部分发给 LLM（节省 token）。
    """
    import difflib

    old_lines = old_text.splitlines()
    new_lines = new_text.splitlines()

    diff = list(difflib.unified_diff(old_lines, new_lines, lineterm="", n=3))

    if not diff:
        return "（页面文本内容无明显差异，可能是格式或元数据变化）"

    diff_text = "\n".join(diff)
    if len(diff_text) > max_chars:
        diff_text = diff_text[:max_chars] + "\n...(内容过长已截断)"

    return diff_text


# ── 提示词构建 ────────────────────────────────────────────────────────────────

ANALYSIS_PROMPT = """你是一名专注于移动应用合规的专家，特别熟悉 Apple App Store 和 Google Play Store 的开发者政策。

以下是某官方政策页面的内容变化（unified diff 格式，+ 表示新增，- 表示删除）：

来源页面：{url}
平台：{platform}

--- 变化内容 ---
{diff}
--- 变化内容结束 ---

请用中文分析这次变化，并严格按照以下 JSON 格式输出（不要输出任何其他内容）：

{{
  "has_policy_change": true/false,
  "change_summary": "用1-3句话概括这次实质性变化是什么",
  "affects_unity_games": true/false,
  "impact_level": "critical/high/medium/low/none",
  "affected_areas": ["受影响的方向，如：IAP、广告、隐私、账户删除、儿童合规 等"],
  "developer_impact": "对 Unity 游戏开发者的具体影响是什么，需要做什么改动",
  "action_required": "建议开发者采取的具体行动（如无需行动则写 null）",
  "rule_ids_to_review": ["从以下列表中选出可能需要复核的 rule_id：iap_3_1_1, att_5_1_2, account_deletion_5_1_1v, sign_in_with_apple_4_8, kids_category_1_3, target_api_level, play_billing, data_safety_section, background_location, iarc_content_rating, ads_policy, ugc_policy, android_app_bundle"],
  "confidence": "high/medium/low"
}}

注意：
- 如果变化只是格式调整、链接更新、拼写修正等非实质性变化，has_policy_change 设为 false
- 只关注对开发者有实际影响的政策内容变化
"""


# ── 主接口 ────────────────────────────────────────────────────────────────────

def analyze_policy_diff(
    old_text: str,
    new_text: str,
    platform: str,
    url: str,
) -> Dict[str, Any]:
    """
    分析政策页面新旧文本的差异，返回结构化的影响分析。

    返回：
      {
        has_policy_change: bool,
        change_summary: str,
        affects_unity_games: bool,
        impact_level: str,
        affected_areas: list,
        developer_impact: str,
        action_required: str | null,
        rule_ids_to_review: list,
        confidence: str,
        provider: str,        # 使用的 LLM 提供商
        analyzed_at: str,
        error: str | null,    # 分析失败时的错误信息
      }
    """
    # 缓存 key：基于新旧文本哈希
    cache_key = hashlib.sha256((old_text + new_text).encode()).hexdigest()[:16]
    cache_file = ANALYSIS_CACHE_DIR / f"{cache_key}.json"

    # 命中缓存直接返回
    if cache_file.exists():
        try:
            return json.loads(cache_file.read_text(encoding="utf-8"))
        except Exception:
            pass

    diff_text = _extract_text_diff(old_text, new_text)
    prompt = ANALYSIS_PROMPT.format(
        url=url,
        platform=platform,
        diff=diff_text,
    )

    result = {
        "has_policy_change": False,
        "change_summary": "",
        "affects_unity_games": False,
        "impact_level": "none",
        "affected_areas": [],
        "developer_impact": "",
        "action_required": None,
        "rule_ids_to_review": [],
        "confidence": "low",
        "provider": "",
        "analyzed_at": datetime.datetime.now().isoformat(),
        "error": None,
        "url": url,
        "platform": platform,
    }

    try:
        llm_response = _call_llm(prompt)
        provider = llm_response["provider"]
        text = llm_response["text"].strip()

        # 提取 JSON（LLM 可能在 JSON 外面加了说明文字）
        json_start = text.find("{")
        json_end = text.rfind("}") + 1
        if json_start >= 0 and json_end > json_start:
            parsed = json.loads(text[json_start:json_end])
            result.update(parsed)
            result["provider"] = provider
        else:
            result["error"] = "LLM 返回内容无法解析为 JSON"
            result["raw_response"] = text

    except RuntimeError as e:
        result["error"] = str(e)
    except json.JSONDecodeError as e:
        result["error"] = f"JSON 解析失败: {e}"
    except Exception as e:
        result["error"] = f"分析失败: {e}"

    # 写入缓存
    try:
        cache_file.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass

    return result


def apply_analysis_to_versions(
    analysis: Dict[str, Any],
    versions: Dict[str, Any],
    platform: str,
) -> Dict[str, Any]:
    """
    将 LLM 分析结果写回 policy_versions.json：
    - 对每个受影响的 rule_id，清空 last_verified（使其出现在"需要复核"列表）
    - 附加 change_alert 字段记录变化摘要，供 freshness 报告展示
    返回实际被标记的 rule_id 列表。
    """
    if not analysis.get("has_policy_change"):
        return {"marked": []}
    if analysis.get("impact_level", "none") in ("none", "low"):
        return {"marked": []}

    rule_ids = analysis.get("rule_ids_to_review", [])
    if not rule_ids:
        return {"marked": []}

    # 规则 id 在 policy_versions.json 里可能分属不同平台，搜索两个平台
    platforms_to_search = ["apple_app_store", "google_play_store"]
    if platform and "apple" in platform.lower():
        platforms_to_search = ["apple_app_store", "google_play_store"]
    elif platform and "google" in platform.lower():
        platforms_to_search = ["google_play_store", "apple_app_store"]

    alert = {
        "detected_at": analysis.get("analyzed_at", datetime.datetime.now().isoformat()),
        "change_summary": analysis.get("change_summary", ""),
        "developer_impact": analysis.get("developer_impact", ""),
        "action_required": analysis.get("action_required"),
        "impact_level": analysis.get("impact_level", "medium"),
        "source_url": analysis.get("url", ""),
        "llm_provider": analysis.get("provider", ""),
    }

    marked = []
    for pid in platforms_to_search:
        rules = versions.get(pid, {}).get("rules", {})
        for rule_id in rule_ids:
            if rule_id in rules:
                rules[rule_id]["last_verified"] = None   # 清空 → 出现在 unknown/待复核
                rules[rule_id]["change_alert"] = alert   # 记录变化摘要
                rules[rule_id]["needs_review"] = True
                marked.append(f"{pid}:{rule_id}")

    return {"marked": marked, "alert": alert}


def check_llm_config() -> Dict[str, Any]:
    """检查 LLM 配置状态，返回当前可用的提供商"""
    status = {
        "anthropic": {
            "configured": bool(os.environ.get("ANTHROPIC_API_KEY")),
            "key_prefix": os.environ.get("ANTHROPIC_API_KEY", "")[:12] + "..." if os.environ.get("ANTHROPIC_API_KEY") else None,
            "model": "claude-3-5-sonnet-20241022",
        },
        "openai": {
            "configured": bool(os.environ.get("OPENAI_API_KEY")),
            "key_prefix": os.environ.get("OPENAI_API_KEY", "")[:8] + "..." if os.environ.get("OPENAI_API_KEY") else None,
            "model": "gpt-4o",
        },
        "any_configured": bool(os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("OPENAI_API_KEY")),
        "how_to_configure": [
            "在终端设置环境变量（选一种）：",
            "  export ANTHROPIC_API_KEY=sk-ant-xxx   # Claude（推荐）",
            "  export OPENAI_API_KEY=sk-xxx          # GPT-4o",
            "或在项目根目录创建 .env 文件（需安装 python-dotenv）：",
            "  ANTHROPIC_API_KEY=sk-ant-xxx",
        ],
    }
    return status
