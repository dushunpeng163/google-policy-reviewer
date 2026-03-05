"""
Unity 游戏合规开发向导引擎（Mode A）

输入：游戏基本信息（类型、功能、年龄、目标市场、目标平台）
输出：
  1. 合规开发路线图（有序步骤）
  2. Unity C# 代码模板（按功能分类）
  3. 平台配置清单（App Store Connect / Play Console）
  4. 法规要点（GDPR / COPPA / 市场专项）
  5. 高风险预警

目标市场：美国、欧盟、英国、澳洲等（不含中国）
目标平台：iOS App Store + Google Play
引擎：Unity
"""

from typing import Dict, Any, List


# ── 市场法规映射 ──────────────────────────────────────────────────────────────

MARKET_REGULATIONS = {
    "US": {
        "name": "美国",
        "key_laws": ["COPPA", "CCPA (加州)"],
        "coppa_applies": True,
        "gdpr_applies": False,
        "notes": "13岁以下用户受 COPPA 约束；加州用户受 CCPA 约束",
    },
    "EU": {
        "name": "欧盟",
        "key_laws": ["GDPR", "DSA"],
        "coppa_applies": False,
        "gdpr_applies": True,
        "notes": "所有年龄用户均受 GDPR 约束；需同意管理平台（CMP）",
    },
    "UK": {
        "name": "英国",
        "key_laws": ["UK GDPR", "Children's Code (AADC)"],
        "coppa_applies": False,
        "gdpr_applies": True,
        "notes": "UK GDPR 与 EU GDPR 高度相似；儿童须额外符合 AADC",
    },
    "AU": {
        "name": "澳大利亚",
        "key_laws": ["Privacy Act", "APP"],
        "coppa_applies": False,
        "gdpr_applies": False,
        "notes": "相对宽松，隐私政策和数据安全为主要要求",
    },
    "CA": {
        "name": "加拿大",
        "key_laws": ["PIPEDA", "Quebec Law 25"],
        "coppa_applies": False,
        "gdpr_applies": False,
        "notes": "魁北克省法规近似 GDPR，建议参照 GDPR 标准执行",
    },
    "JP": {
        "name": "日本",
        "key_laws": ["APPI"],
        "coppa_applies": False,
        "gdpr_applies": False,
        "notes": "APPI 与 GDPR 有类似概念，需隐私政策和用户同意机制",
    },
    "KR": {
        "name": "韩国",
        "key_laws": ["PIPA"],
        "coppa_applies": False,
        "gdpr_applies": False,
        "notes": "PIPA 要求严格，14岁以下须家长同意；需本地化隐私政策",
    },
}


# ── 路线图步骤库 ─────────────────────────────────────────────────────────────

def _build_roadmap(features: List[str], min_age: int, markets: List[str], platforms: List[str]) -> List[Dict]:
    steps = []
    has_kids = min_age < 13
    has_teens = min_age < 18
    needs_gdpr = any(MARKET_REGULATIONS.get(m, {}).get("gdpr_applies") for m in markets)
    needs_coppa = "US" in markets and has_kids

    # Step 1: 隐私政策（所有游戏必须）
    steps.append({
        "step": 1,
        "phase": "法务准备",
        "title": "起草隐私政策 & 服务条款",
        "priority": "critical",
        "effort": "1-3天",
        "desc": "所有上架游戏必须有公开可访问的隐私政策。GDPR 市场还需数据处理协议（DPA）。",
        "items": [
            "隐私政策须涵盖：收集哪些数据、为何收集、如何使用、第三方共享、用户权利",
            "服务条款须涵盖：用户年龄限制、IAP 退款政策、账户终止条款",
            "儿童游戏须额外说明：COPPA/GDPR 儿童条款、家长权利",
            "建议使用：Termly、iubenda 等工具生成初稿，再由律师审核",
        ],
        "platforms": ["ios", "android"],
        "markets": markets,
    })

    # Step 2: 账户系统设计
    if "social_login" in features or "multiplayer" in features or "leaderboard" in features:
        steps.append({
            "step": 2,
            "phase": "账户系统",
            "title": "设计合规账户系统",
            "priority": "critical",
            "effort": "1-2周",
            "desc": "有账户系统就必须支持账户删除（iOS 2022年6月起强制，Android 2024年5月起强制）",
            "items": [
                "账户删除：游戏内入口 + Android 需提供网页版删除链接",
                "数据最小化：只收集必要的用户数据",
                "Sign in with Apple：iOS 有第三方登录时必须同时提供",
                f"{'儿童账户须有家长同意机制（COPPA/GDPR）' if has_kids else '建议支持 Guest 模式降低注册门槛'}",
            ],
            "platforms": platforms,
            "markets": markets,
            "code_templates": ["AccountDeletionUI.cs"],
        })

    # Step 3: 隐私同意
    if needs_gdpr or needs_coppa:
        title = "GDPR 同意管理平台（CMP）" if needs_gdpr else "COPPA 家长同意机制"
        items = []
        if needs_gdpr:
            items += [
                "集成 CMP（如 Google UMP SDK / Usercentrics / OneTrust）",
                "首次启动时展示同意弹窗（Before any data collection）",
                "用户可随时撤回同意（设置页入口）",
                "记录同意时间戳和版本（用于审计）",
            ]
        if needs_coppa:
            items += [
                "13岁以下用户须获得可验证的家长同意（信用卡验证 / 邮件确认）",
                "未获同意前禁止收集任何个人信息",
                "禁止对儿童展示行为定向广告",
            ]
        steps.append({
            "step": 3,
            "phase": "隐私合规",
            "title": title,
            "priority": "critical",
            "effort": "3-7天",
            "desc": f"覆盖市场：{', '.join(markets)}",
            "items": items,
            "platforms": platforms,
            "markets": markets,
            "code_templates": ["PrivacyPolicyUI.cs"],
        })

    # Step 4: IAP
    if "iap" in features:
        steps.append({
            "step": len(steps) + 1,
            "phase": "核心功能",
            "title": "Unity IAP 集成",
            "priority": "critical",
            "effort": "3-5天",
            "desc": "App Store 和 Google Play 均要求所有虚拟商品必须通过官方支付系统",
            "items": [
                "安装：Window > Package Manager > In App Purchasing",
                "在 App Store Connect 创建商品（Product ID 须与代码一致）",
                "在 Play Console 创建应用内商品或订阅",
                "后端服务器验证收据（不能只在客户端验证）",
                "订阅游戏须在购买前明确展示价格、周期、续费条款",
                f"{'儿童游戏：禁止诱导儿童消费，须家长确认' if has_kids else ''}",
            ],
            "platforms": platforms,
            "markets": markets,
            "code_templates": ["IAPManager.cs"],
        })

    # Step 5: 广告
    if "ads" in features:
        steps.append({
            "step": len(steps) + 1,
            "phase": "核心功能",
            "title": "广告 SDK 合规配置",
            "priority": "critical" if has_kids else "high",
            "effort": "2-4天",
            "desc": "广告是最容易触发合规问题的模块",
            "items": [
                "iOS：集成 ATT（App Tracking Transparency），在使用 IDFA 前请求授权",
                "推荐广告 SDK：Unity Ads / IronSource / AppLovin（均支持 GDPR/COPPA）",
                "GDPR 市场：在展示广告前须获得用户同意（通过 CMP）",
                "COPPA：13岁以下用户必须使用非个性化广告（tagForChildDirectedTreatment = true）",
                "全屏插屏广告：须有关闭按钮（iOS 和 Android 均要求，关闭按钮 ≥5秒后出现）",
                "禁止：模拟系统通知的广告、诱导点击的广告",
                f"{'儿童游戏：禁止插屏广告，只能使用横幅广告（且须为儿童安全内容）' if has_kids else ''}",
            ],
            "platforms": platforms,
            "markets": markets,
            "code_templates": ["ATTHandler.cs", "ParentalGate.cs"],
        })

    # Step 6: 家长门控（儿童游戏）
    if has_kids:
        steps.append({
            "step": len(steps) + 1,
            "phase": "儿童合规",
            "title": "家长门控（Parental Gate）",
            "priority": "critical",
            "effort": "1-2天",
            "desc": "App Store 1.3 强制要求：儿童 App 的所有外部跳转前必须通过家长门控",
            "items": [
                "所有外部链接（网页、社交媒体、其他 App）前展示家长门控",
                "家长门控须为随机数学题或同等难度操作（不能是简单点击）",
                "禁止在儿童 App 中加入社交网络功能（除非有专门的儿童版）",
                "禁止通过推送通知收集用户数据",
                "第三方 SDK 须在 Apple Families Approved 列表内",
            ],
            "platforms": ["ios"],
            "markets": markets,
            "code_templates": ["ParentalGate.cs"],
        })

    # Step 7: 多人游戏 / UGC
    if "multiplayer" in features or "ugc" in features:
        steps.append({
            "step": len(steps) + 1,
            "phase": "核心功能",
            "title": "多人游戏 / UGC 内容审核",
            "priority": "high",
            "effort": "1-3周",
            "desc": "Google Play 明确要求 UGC 功能须有举报和审核机制",
            "items": [
                "实现举报功能（每条 UGC 或聊天消息旁）",
                "后端内容审核队列（可先用 AI 预过滤，人工复核边缘案例）",
                "儿童游戏禁止开放聊天功能（只能有预设选项）",
                "违规内容须能快速删除（SLA 建议 24 小时内）",
                "保留内容审核日志（法务需要）",
            ],
            "platforms": platforms,
            "markets": markets,
        })

    # Step 8: 技术合规
    steps.append({
        "step": len(steps) + 1,
        "phase": "技术配置",
        "title": "平台技术要求",
        "priority": "high",
        "effort": "1-3天",
        "desc": "上架前必须满足的技术硬性要求",
        "items": [
            "Android：Player Settings > Target API Level ≥ 35（2025年要求）",
            "Android：构建 .aab 而非 .apk（2021年起强制）",
            "iOS：最低 iOS 版本建议 ≥ iOS 16",
            "64位架构：确保 IL2CPP 构建（不使用 Mono）",
            "Unity 版本：建议 2022 LTS 或 2023 LTS（更好的平台支持）",
        ],
        "platforms": platforms,
        "markets": markets,
    })

    # Step 9: 平台配置表单
    steps.append({
        "step": len(steps) + 1,
        "phase": "平台配置",
        "title": "App Store Connect & Play Console 配置",
        "priority": "high",
        "effort": "1-2天",
        "desc": "上架前必须在各平台完成的表单填写",
        "items": [
            "[iOS] App Store Connect > 应用隐私 > 填写隐私营养标签（数据类型逐项声明）",
            "[iOS] App Store Connect > 应用信息 > 内容分级问卷",
            "[Android] Play Console > 应用内容 > 数据安全表单",
            "[Android] Play Console > 应用内容 > 内容分级 > 完成 IARC 问卷",
            "[Android] Play Console > 应用内容 > 目标受众（选择年龄范围）",
            f"{'[Android] Play Console > 应用内容 > 账户删除 > 填写网页版删除 URL' if 'social_login' in features or 'multiplayer' in features else ''}",
            "[双平台] 隐私政策 URL 填写到对应平台控制台",
        ],
        "platforms": platforms,
        "markets": markets,
    })

    # Step 10: 测试
    steps.append({
        "step": len(steps) + 1,
        "phase": "上线前验证",
        "title": "合规测试 Checklist",
        "priority": "high",
        "effort": "2-4天",
        "desc": "模拟审核员视角，逐项验证",
        "items": [
            "GDPR：从 EU 网络访问游戏，确认同意弹窗第一时间出现",
            "ATT（iOS）：新安装后确认 ATT 弹窗出现（非儿童游戏）",
            "账户删除：走完整删除流程，确认数据真实删除",
            "IAP：购买 → 退出 → 重新进入 → 确认购买状态恢复",
            "隐私政策链接：点击确认页面可访问且非空",
            f"{'家长门控：每个外部链接前确认数学题弹出' if has_kids else ''}",
            "内容分级：游戏内容与提交的年龄分级一致",
        ],
        "platforms": platforms,
        "markets": markets,
    })

    return [s for s in steps if s.get("title")]


# ── 法规要点摘要 ─────────────────────────────────────────────────────────────

def _build_legal_summary(min_age: int, markets: List[str]) -> Dict[str, Any]:
    has_kids = min_age < 13
    needs_gdpr = any(MARKET_REGULATIONS.get(m, {}).get("gdpr_applies") for m in markets)
    needs_coppa = "US" in markets and has_kids

    summary = {
        "applicable_laws": [],
        "key_requirements": [],
        "data_retention": "建议用户数据保留不超过必要期限，GDPR 要求可被遗忘权",
        "dpo_required": needs_gdpr and "large_scale" in [],  # 简化判断
        "privacy_policy_languages": [],
    }

    for market in markets:
        reg = MARKET_REGULATIONS.get(market)
        if reg:
            summary["applicable_laws"].extend(reg["key_laws"])

    summary["applicable_laws"] = list(set(summary["applicable_laws"]))

    if needs_gdpr:
        summary["key_requirements"].append({
            "law": "GDPR（欧盟）",
            "requirements": [
                "合法处理依据：游戏须基于用户同意（或合同必要性）处理数据",
                "数据主体权利：访问权、更正权、删除权、可携带权（须有技术实现）",
                "同意必须：明确、可撤回、记录存档",
                "数据泄露：72小时内向监管机构报告",
                "隐私政策：须有 EU 本地语言版本（至少英语）",
            ]
        })
        summary["privacy_policy_languages"].extend(["en", "de", "fr", "es", "it"])

    if needs_coppa:
        summary["key_requirements"].append({
            "law": "COPPA（美国，13岁以下）",
            "requirements": [
                "须获得可验证的家长同意（信用卡验证 / 邮件确认 / 电话）",
                "禁止收集：真实姓名、地址、电话、邮件、位置、照片",
                "不得以任何方式向儿童推销或展示行为定向广告",
                "家长可要求查看、删除子女数据",
                "FTC 违规罚款：每次违规最高 $5万",
            ]
        })

    if "UK" in markets:
        summary["key_requirements"].append({
            "law": "UK Children's Code (AADC)",
            "requirements": [
                "默认设置须对儿童最友好（默认关闭非必要数据收集）",
                "禁止使用黑暗模式设计引导儿童消费",
                "位置数据默认关闭",
            ]
        })

    return summary


# ── 平台配置清单 ─────────────────────────────────────────────────────────────

def _build_platform_checklist(features: List[str], min_age: int, markets: List[str]) -> Dict[str, List]:
    has_kids = min_age < 13
    has_account = any(f in features for f in ["social_login", "multiplayer", "leaderboard"])

    ios_items = [
        {"item": "Xcode → Signing & Capabilities → 配置 Bundle ID 和证书", "category": "基础配置"},
        {"item": "App Store Connect → 创建 App 记录，填写基本信息", "category": "基础配置"},
        {"item": "App Store Connect → 应用隐私 → 填写所有数据类型的隐私营养标签", "category": "隐私"},
        {"item": "App Store Connect → 应用信息 → 完成内容分级问卷", "category": "内容分级"},
        {"item": "Info.plist → 添加所有使用权限的描述字符串（NSXxx​UsageDescription）", "category": "权限"},
    ]

    if "ads" in features:
        ios_items.append({"item": "Info.plist → 添加 NSUserTrackingUsageDescription（ATT 必须）", "category": "广告/隐私"})
        ios_items.append({"item": "Xcode → Signing & Capabilities → 添加 Push Notifications（如需）", "category": "广告"})

    if "iap" in features:
        ios_items.append({"item": "App Store Connect → 功能 → App 内购买 → 创建商品（Product ID）", "category": "IAP"})
        ios_items.append({"item": "App Store Connect → 协议税务和银行业务 → 完成银行账户设置", "category": "IAP"})

    if "social_login" in features:
        ios_items.append({"item": "Xcode → Signing & Capabilities → 添加 Sign In with Apple", "category": "登录"})

    if has_account:
        ios_items.append({"item": "App Store Connect → 填写账户删除流程说明（审核员会测试）", "category": "账户"})

    if has_kids:
        ios_items.append({"item": "App Store Connect → 选择儿童类别，确认无第三方广告 SDK", "category": "儿童"})

    android_items = [
        {"item": "Player Settings → Android → Package Name（格式：com.company.gamename）", "category": "基础配置"},
        {"item": "Player Settings → Android → Target API Level ≥ 35", "category": "技术要求"},
        {"item": "构建设置 → 选择 Android App Bundle (.aab)", "category": "技术要求"},
        {"item": "Play Console → 创建应用，完成商店信息（截图、描述、分类）", "category": "基础配置"},
        {"item": "Play Console → 应用内容 → 数据安全表单（必填）", "category": "隐私"},
        {"item": "Play Console → 应用内容 → 内容分级 → 完成 IARC 问卷", "category": "内容分级"},
        {"item": "Play Console → 应用内容 → 目标受众 → 选择年龄范围", "category": "内容分级"},
        {"item": "Play Console → 商店设置 → 隐私权政策 → 填写隐私政策 URL", "category": "隐私"},
    ]

    if "iap" in features:
        android_items.append({"item": "Play Console → 应用内商品 → 创建商品（与 Unity IAP Product ID 对应）", "category": "IAP"})
        android_items.append({"item": "Play Console → 收益 → 设置付款信息", "category": "IAP"})

    if has_account:
        android_items.append({"item": "Play Console → 应用内容 → 账户删除 → 填写网页版账户删除 URL", "category": "账户"})

    if has_kids:
        android_items.append({"item": "Play Console → 应用内容 → 目标受众 → 选择儿童，并确认家庭政策合规", "category": "儿童"})

    return {"ios": ios_items, "android": android_items}


# ── Unity 专属技术要点 ────────────────────────────────────────────────────────

def _build_unity_tech_notes(features: List[str], min_age: int) -> List[Dict]:
    notes = [
        {
            "category": "构建设置",
            "items": [
                "Scripting Backend：IL2CPP（必须，Mono 不满足 64位要求）",
                "API Compatibility Level：.NET Standard 2.1",
                "Android：Target Architecture 选 ARM64（64位强制）",
                "iOS：Minimum iOS Version 建议 16.0+",
            ]
        },
        {
            "category": "推荐 Package",
            "items": [
                "com.unity.purchasing — Unity IAP（如有付费功能）",
                "com.unity.ugui — UI Toolkit 替代旧版 UGUI",
                "com.unity.localization — 多语言支持（GDPR 市场需要）",
                "com.unity.analytics — 若需分析，须在 GDPR 弹窗后才能启用",
            ]
        },
    ]

    if "ads" in features:
        notes.append({
            "category": "广告 SDK 推荐（支持 GDPR/COPPA）",
            "items": [
                "Unity Ads（com.unity.ads）—— 最易集成，Unity 原生",
                "IronSource / LevelPlay —— 聚合平台，支持多网络",
                "AppLovin MAX —— 高 eCPM，GDPR/COPPA 合规",
                "⚠️ 儿童游戏必须向 SDK 传入 COPPA 标记，禁用行为定向广告",
            ]
        })

    if min_age < 13:
        notes.append({
            "category": "儿童游戏特别注意",
            "items": [
                "Unity Analytics：需在获得家长同意后才能初始化",
                "Firebase：需配置 COPPA 模式",
                "所有第三方 SDK 须确认在 Apple Families Approved 列表内",
                "不得使用 IDFA / 广告 ID（即使获得授权）",
            ]
        })

    return notes


# ── 公开接口 ─────────────────────────────────────────────────────────────────

def generate_dev_guide(
    game_name: str = "My Unity Game",
    game_type: str = "casual",
    features: List[str] = None,
    min_user_age: int = 18,
    target_markets: List[str] = None,
    target_platforms: List[str] = None,
) -> Dict[str, Any]:
    """
    生成 Unity 游戏合规开发向导。

    参数：
      game_name       - 游戏名称
      game_type       - 游戏类型（casual/puzzle/rpg/strategy/action/simulation）
      features        - 功能列表（iap/ads/social_login/multiplayer/leaderboard/ugc/push/analytics）
      min_user_age    - 最小用户年龄（影响儿童法规适用）
      target_markets  - 目标市场代码列表（US/EU/UK/AU/CA/JP/KR）
      target_platforms - 目标平台（ios/android，默认两者）

    返回：
      完整的合规开发向导字典
    """
    features = features or []
    target_markets = target_markets or ["US", "EU"]
    target_platforms = target_platforms or ["ios", "android"]

    has_kids = min_user_age < 13
    has_teens = min_user_age < 18
    needs_gdpr = any(MARKET_REGULATIONS.get(m, {}).get("gdpr_applies") for m in target_markets)
    needs_coppa = "US" in target_markets and has_kids

    # 自动添加隐式需要的功能
    effective_features = list(features)
    if "multiplayer" in features and "leaderboard" not in features:
        pass  # leaderboard 是可选的

    risk_level = "low"
    warnings = []

    if has_kids:
        risk_level = "high"
        warnings.append("🚨 目标用户含13岁以下儿童，触发 COPPA（美国）/ GDPR 儿童条款（欧盟）" if needs_coppa or needs_gdpr else "🚨 目标用户含13岁以下儿童，须实现家长门控")
    if "ads" in features and has_kids:
        warnings.append("⚠️ 儿童游戏含广告：必须禁用行为定向广告，禁止插屏广告")
    if needs_gdpr:
        warnings.append("⚠️ 欧盟市场：游戏启动时须第一时间展示 GDPR 同意弹窗，任何数据收集（含广告 SDK）须在同意后才能初始化")
    if "iap" in features:
        warnings.append("⚠️ IAP：绝对不能引导用户通过外部网页购买虚拟商品（会被下架）")
    if "social_login" in features and "ios" in target_platforms:
        warnings.append("⚠️ iOS 有第三方登录（Google/Facebook 等）时，必须同时提供 Sign in with Apple")

    roadmap = _build_roadmap(effective_features, min_user_age, target_markets, target_platforms)
    legal = _build_legal_summary(min_user_age, target_markets)
    checklist = _build_platform_checklist(effective_features, min_user_age, target_markets)
    tech_notes = _build_unity_tech_notes(effective_features, min_user_age)

    # 代码模板引用
    from engines.code_template_generator import generate_templates, TEMPLATE_CATALOG
    template_features = [f for f in effective_features if f in TEMPLATE_CATALOG]
    if template_features:
        templates = generate_templates(
            features=template_features,
            platforms=["unity"],  # Unity 游戏只需要 Unity 模板
            min_user_age=min_user_age,
        )
    else:
        templates = {"templates": [], "project_checklist": [], "warnings": [], "meta": {}}

    return {
        "game_info": {
            "name": game_name,
            "type": game_type,
            "features": effective_features,
            "min_user_age": min_user_age,
            "target_markets": target_markets,
            "target_platforms": target_platforms,
            "has_kids": has_kids,
            "needs_gdpr": needs_gdpr,
            "needs_coppa": needs_coppa,
        },
        "risk_level": risk_level,
        "warnings": warnings,
        "roadmap": roadmap,
        "unity_templates": templates,
        "platform_checklist": checklist,
        "legal_summary": legal,
        "unity_tech_notes": tech_notes,
        "market_details": {
            m: MARKET_REGULATIONS.get(m, {"name": m, "key_laws": [], "notes": ""})
            for m in target_markets
        },
        "estimated_compliance_effort": _estimate_effort(effective_features, min_user_age, needs_gdpr),
    }


def _estimate_effort(features: List[str], min_age: int, needs_gdpr: bool) -> Dict:
    days = 5  # base: privacy policy + platform config
    if "iap" in features: days += 5
    if "ads" in features: days += 4
    if "social_login" in features: days += 3
    if "multiplayer" in features: days += 10
    if "ugc" in features: days += 7
    if min_age < 13: days += 7
    if needs_gdpr: days += 5

    return {
        "min_days": days,
        "max_days": days * 2,
        "note": "以上为纯合规工程量估算，不含游戏核心功能开发时间"
    }
