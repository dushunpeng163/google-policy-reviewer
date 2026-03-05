"""
Unity 游戏统一合规审计引擎（Mode B）

合并三条分析线为一份完整报告：
  1. 代码静态扫描（Unity 项目目录）
  2. App Store + Google Play 平台政策检测
  3. 目标市场法规检测（GDPR / COPPA 等）

目标市场：美国、欧盟、英国、澳洲等（不含中国）
"""

from typing import Dict, Any, List, Optional


MARKET_LEGAL_CHECKS = {
    "GDPR": {
        "markets": ["EU", "UK"],
        "checks": [
            {
                "id": "gdpr_consent",
                "title": "GDPR 用户同意机制（CMP）",
                "severity": "critical",
                "detail": "游戏启动时须第一时间展示同意弹窗，任何 SDK 初始化须在获得同意后",
                "fix": "集成 Google UMP SDK / Usercentrics，在 Start() 最开始调用 CMP，获得回调后再初始化广告/分析 SDK",
            },
            {
                "id": "gdpr_privacy_policy",
                "title": "GDPR 隐私政策",
                "severity": "critical",
                "detail": "须有 EU 用户可读的隐私政策，涵盖数据处理目的、用户权利、数据控制者信息",
                "fix": "在游戏内提供隐私政策链接；App Store Connect 和 Play Console 均须填写 URL",
            },
            {
                "id": "gdpr_data_rights",
                "title": "GDPR 数据主体权利",
                "severity": "high",
                "detail": "须提供：查看我的数据、更正、删除账户及所有数据的入口",
                "fix": "设置页 > 隐私设置 > 数据权利入口",
            },
            {
                "id": "gdpr_consent_withdrawal",
                "title": "GDPR 同意可撤回",
                "severity": "high",
                "detail": "用户须能随时撤回同意，且操作须与给予同意同样便捷",
                "fix": "设置页 > 隐私设置 > 修改同意选项，触发 SDK 相应配置更新",
            },
        ],
    },
    "COPPA": {
        "markets": ["US"],
        "kids_only": True,
        "checks": [
            {
                "id": "coppa_parental_consent",
                "title": "COPPA 家长同意机制",
                "severity": "critical",
                "detail": "13岁以下须获得可验证的家长同意，违规最高罚款 $5万/次",
                "fix": "年龄门控 + 家长邮件确认或信用卡预授权验证",
            },
            {
                "id": "coppa_no_behavioral_ads",
                "title": "COPPA 禁止行为定向广告",
                "severity": "critical",
                "detail": "禁止向 13 岁以下用户展示行为追踪广告",
                "fix": "所有广告 SDK 传入 COPPA 标记：tagForChildDirectedTreatment = true",
            },
            {
                "id": "coppa_no_pii",
                "title": "COPPA 禁止收集儿童个人信息",
                "severity": "critical",
                "detail": "禁止收集儿童的姓名、邮件、位置、照片等 PII",
                "fix": "儿童模式下禁用账户注册（含邮件）、位置、相机权限",
            },
        ],
    },
    "CCPA": {
        "markets": ["US"],
        "checks": [
            {
                "id": "ccpa_do_not_sell",
                "title": "CCPA 不出售个人信息选项",
                "severity": "medium",
                "detail": "须为加州用户提供退出数据销售的选项",
                "fix": "隐私设置中添加 'Do Not Sell My Personal Information' 开关",
            },
        ],
    },
    "AADC": {
        "markets": ["UK"],
        "checks": [
            {
                "id": "aadc_default_privacy",
                "title": "UK 儿童行为守则（AADC）默认隐私",
                "severity": "high",
                "detail": "位置默认关闭、个人资料默认私密、推送通知默认关闭",
                "fix": "所有数据收集功能默认 OFF，由用户主动开启",
            },
        ],
    },
}

# finding id -> 推荐库（简短，用于优先清单展示）
_FINDING_PACKAGES = {
    "ios_att":              "📦 com.unity.advertisement.ios.support（免费官方）",
    "gdpr_consent":         "📦 com.google.ump — Google UMP SDK（免费官方）",
    "gdpr_privacy_policy":  "📝 人工操作：在 App Store Connect / Play Console 填写 URL",
    "ccpa_do_not_sell":     "📝 UI 自写（隐私设置页加开关）+ UMP SDK 支持",
    "aadc_default_privacy": "📝 代码默认值：数据收集功能初始设为 false",
    "ios_iap_storekit":     "📦 com.unity.purchasing — Unity IAP（免费官方）",
    "android_play_billing": "📦 com.unity.purchasing — Unity IAP（免费官方）",
    "ios_parental_gate":    "📝 自写 UI（~80行 C#，无现成开源方案）",
    "ios_kids_sdk":         "📋 核对 Apple Families Approved 列表（无代码）",
    "android_kids_policy":  "📋 Play Console 后台设置 + 核对 SDK 列表（无代码）",
    "coppa_parental_consent":"📝 年龄门控 + 家长邮件确认（自写，约200行）",
    "coppa_no_behavioral_ads":"📦 AdMob: tagForChildDirectedTreatment=true（1行）",
    "coppa_no_pii":         "📝 儿童模式下禁用相关权限请求（代码开关）",
    "ios_account_deletion": "📝 自写后端 DELETE API + 游戏内设置页入口",
    "android_account_deletion":"📝 自写后端 API + 公开网页删除入口（Android 强制）",
    "ios_sign_in_apple":    "📦 com.lupidan.apple-signin-unity（开源免费，GitHub）",
    "gdpr_data_rights":     "📝 设置页入口 + 后端数据导出/删除 API（自写）",
    "gdpr_consent_withdrawal":"📦 UMP SDK: ConsentForm.loadAndPresentFromViewController",
    "android_data_safety":  "📋 Play Console → 应用内容 → 数据安全（人工填写）",
    "android_privacy_policy":"📋 Play Console → 商店设置（人工填写）",
    "ios_privacy_labels":   "📋 App Store Connect → 应用隐私（人工填写）",
    "android_iarc":         "📋 Play Console → 内容分级问卷（人工填写）",
    "android_aab":          "📦 Unity Build Settings → Export as AAB（内置，改一个选项）",
    "android_target_api":   "📦 Unity Player Settings → Target API Level: 35（改一个选项）",
    "android_ads_policy":   "📦 com.google.ads.mobile — AdMob SDK（免费官方）",
    "android_privacy_policy":"📋 Play Console → 商店设置（人工填写）",
}


PLATFORM_CHECKS = {
    "ios": [
        {
            "id": "ios_att",
            "title": "iOS ATT（App Tracking Transparency）",
            "severity": "critical",
            "guideline": "App Store 5.1.2 / iOS 14.5+",
            "detail": "使用广告或追踪前须请求 ATT 授权，未实现直接拒审",
            "fix": "Unity：安装 com.unity.advertisement.ios.support，调用 ATTrackingStatusBinding.RequestAuthorizationTracking()",
            "applies_when": lambda f, age, _: True,
        },
        {
            "id": "ios_account_deletion",
            "title": "iOS 账户删除",
            "severity": "critical",
            "guideline": "App Store 5.1.1(v)，2022年6月强制",
            "detail": "必须是完全删除账户及数据，非仅注销",
            "fix": "设置页 > 删除账户 > 二次确认 > 后端 DELETE API，30天内彻底删除",
            "applies_when": lambda f, age, _: any(x in f for x in ["social_login", "multiplayer", "leaderboard"]),
        },
        {
            "id": "ios_sign_in_apple",
            "title": "Sign in with Apple（有第三方登录时必须）",
            "severity": "critical",
            "guideline": "App Store 4.8",
            "detail": "提供 Google/Facebook 等登录时，必须同时提供 Sign in with Apple",
            "fix": "Unity：apple-signin-unity 插件；Xcode Capabilities 添加 Sign In with Apple",
            "applies_when": lambda f, age, _: "social_login" in f,
        },
        {
            "id": "ios_iap_storekit",
            "title": "iOS IAP 必须用 StoreKit（Unity IAP）",
            "severity": "critical",
            "guideline": "App Store 3.1.1",
            "detail": "所有虚拟商品须通过 Unity IAP，不得引导外部支付",
            "fix": "Window > Package Manager > In App Purchasing",
            "applies_when": lambda f, age, _: "iap" in f,
        },
        {
            "id": "ios_parental_gate",
            "title": "家长门控（儿童 App 强制）",
            "severity": "critical",
            "guideline": "App Store 1.3",
            "detail": "所有外部链接前须展示随机数学题（不能是简单点击）",
            "fix": "参见 ParentalGate.cs 模板",
            "applies_when": lambda f, age, _: age < 13,
        },
        {
            "id": "ios_privacy_labels",
            "title": "App Store 隐私营养标签",
            "severity": "high",
            "guideline": "App Store Connect 必填",
            "detail": "所有数据类型（含第三方 SDK）须在 App Store Connect 逐项声明",
            "fix": "App Store Connect → 应用隐私 → 按类型填写",
            "applies_when": lambda f, age, _: True,
        },
        {
            "id": "ios_kids_sdk",
            "title": "儿童类别 SDK 限制",
            "severity": "critical",
            "guideline": "App Store 1.3",
            "detail": "儿童 App 只能使用 Apple Families Approved 列表内的 SDK",
            "fix": "访问 developer.apple.com 确认所用 SDK 是否批准",
            "applies_when": lambda f, age, _: age < 13,
        },
    ],
    "android": [
        {
            "id": "android_target_api",
            "title": "Android Target API Level",
            "severity": "critical",
            "guideline": "Google Play Target API Level 政策",
            "detail": "2025年新应用须 targetSdkVersion ≥ 35",
            "fix": "Unity → Player Settings → Android → Other Settings → Target API Level: 35",
            "applies_when": lambda f, age, _: True,
        },
        {
            "id": "android_play_billing",
            "title": "Google Play Billing（Unity IAP）",
            "severity": "critical",
            "guideline": "Google Play 结算政策",
            "detail": "所有数字商品须通过 Play Billing，不得引导外部支付",
            "fix": "Window > Package Manager > In App Purchasing",
            "applies_when": lambda f, age, _: "iap" in f,
        },
        {
            "id": "android_data_safety",
            "title": "Google Play 数据安全表单",
            "severity": "critical",
            "guideline": "Google Play 数据安全政策，2022年7月强制",
            "detail": "须与实际代码行为一致，第三方 SDK 数据也须包含",
            "fix": "Play Console → 应用内容 → 数据安全",
            "applies_when": lambda f, age, _: True,
        },
        {
            "id": "android_account_deletion",
            "title": "Android 账户删除（含网页版）",
            "severity": "critical",
            "guideline": "Google Play 账户删除政策，2024年5月强制",
            "detail": "游戏内入口 + 必须提供网页版删除链接（卸载后仍可用）",
            "fix": "游戏内入口 + 公开网页 URL；Play Console → 应用内容 → 账户删除",
            "applies_when": lambda f, age, _: any(x in f for x in ["social_login", "multiplayer", "leaderboard"]),
        },
        {
            "id": "android_privacy_policy",
            "title": "Google Play 隐私政策 URL",
            "severity": "critical",
            "guideline": "Google Play 用户数据政策",
            "detail": "须 HTTPS、无登录门控、始终可访问",
            "fix": "Play Console → 商店设置 → 隐私权政策",
            "applies_when": lambda f, age, _: True,
        },
        {
            "id": "android_iarc",
            "title": "IARC 内容分级",
            "severity": "high",
            "guideline": "Google Play 内容分级政策",
            "detail": "所有新应用强制，未完成无法发布",
            "fix": "Play Console → 应用内容 → 内容分级 → 完成问卷",
            "applies_when": lambda f, age, _: True,
        },
        {
            "id": "android_aab",
            "title": "Android App Bundle (.aab)",
            "severity": "high",
            "guideline": "Google Play 技术要求，2021年8月强制",
            "detail": "新应用必须上传 .aab 而非 .apk",
            "fix": "Unity → Build Settings → Export as AAB",
            "applies_when": lambda f, age, _: True,
        },
        {
            "id": "android_kids_policy",
            "title": "Google Play 家庭政策（儿童）",
            "severity": "critical",
            "guideline": "Google Play 家庭政策",
            "detail": "只能使用 Families Approved 列表内的 SDK",
            "fix": "Play Console → 应用内容 → 目标受众 → 选儿童；仅使用认证 SDK",
            "applies_when": lambda f, age, _: age < 13,
        },
        {
            "id": "android_ads_policy",
            "title": "Google Play 广告政策",
            "severity": "high",
            "guideline": "Google Play 广告政策",
            "detail": "插屏须有关闭按钮，不得模拟系统通知",
            "fix": "检查广告 SDK 插屏配置，确认关闭按钮合规",
            "applies_when": lambda f, age, _: "ads" in f,
        },
    ],
}


# ── 每个系统的推荐实现方案（免费/开源优先）────────────────────────────────
_SYSTEM_SOLUTIONS = {
    "privacy_consent": {
        "solutions": [
            {
                "name": "Google UMP SDK",
                "type": "免费官方",
                "covers": ["GDPR 同意弹窗", "CCPA", "同意状态管理"],
                "unity_package": "com.google.ump",
                "url": "https://developers.google.com/admob/unity/privacy",
                "note": "Google 官方，与 AdMob 配套使用，一行代码初始化",
            },
            {
                "name": "iOS ATT 原生 API",
                "type": "平台内置",
                "covers": ["iOS ATT 弹窗"],
                "unity_package": "com.unity.advertisement.ios.support",
                "url": "https://developer.apple.com/documentation/apptrackingtransparency",
                "note": "苹果原生，零成本，Unity 插件直接调用",
            },
        ],
        "custom_code_needed": "无——UMP SDK 覆盖全部同意流程",
    },
    "child_protection": {
        "solutions": [
            {
                "name": "广告 SDK COPPA 标记",
                "type": "平台内置",
                "covers": ["禁止行为定向广告", "COPPA 标记"],
                "unity_package": None,
                "url": "https://developers.google.com/admob/unity/targeting",
                "note": "AdMob/各广告 SDK 均内置，传入 tagForChildDirectedTreatment=true 即可",
            },
            {
                "name": "Apple Families Approved SDK 列表",
                "type": "审核要求",
                "covers": ["儿童类别 SDK 合规"],
                "unity_package": None,
                "url": "https://developer.apple.com/support/third-party-SDK-requirements/",
                "note": "需逐一核对自用 SDK 是否在列表内，无代码工作量",
            },
        ],
        "custom_code_needed": "家长门控 UI（约 80-100 行 C#，逻辑简单）；COPPA 年龄判断路由",
    },
    "iap": {
        "solutions": [
            {
                "name": "Unity IAP",
                "type": "免费官方",
                "covers": ["iOS StoreKit", "Google Play Billing", "统一购买/恢复流程"],
                "unity_package": "com.unity.purchasing",
                "url": "https://docs.unity3d.com/Packages/com.unity.purchasing@latest",
                "note": "Unity 官方包，Package Manager 直接安装，双平台统一 API",
            },
            {
                "name": "RevenueCat（免费版）",
                "type": "免费第三方",
                "covers": ["收据验证", "订阅管理", "跨平台用户购买状态"],
                "unity_package": "com.revenuecat.purchases-unity",
                "url": "https://www.revenuecat.com/",
                "note": "免费版足够独立游戏，省去自建收据验证后端的工作量",
            },
        ],
        "custom_code_needed": "商品 ID 配置；购买成功后的游戏内发货逻辑",
    },
    "ads": {
        "solutions": [
            {
                "name": "Google AdMob",
                "type": "免费官方",
                "covers": ["广告展示", "儿童模式", "COPPA 标记", "iOS/Android 双平台"],
                "unity_package": "com.google.ads.mobile",
                "url": "https://developers.google.com/admob/unity/start",
                "note": "与 UMP SDK 深度集成，同意回调后自动初始化广告请求",
            },
        ],
        "custom_code_needed": "广告初始化时序控制（等 UMP 同意回调后再调用 MobileAds.Initialize，约 20 行）",
    },
    "account": {
        "solutions": [
            {
                "name": "apple-signin-unity",
                "type": "开源免费",
                "covers": ["Sign in with Apple"],
                "unity_package": "com.lupidan.apple-signin-unity",
                "url": "https://github.com/lupidan/apple-signin-unity",
                "note": "GitHub 开源，Star 数高，社区活跃，直接从 Package Manager 安装",
            },
            {
                "name": "Google Play Games Plugin for Unity",
                "type": "免费官方",
                "covers": ["Google 登录（Android）"],
                "unity_package": "com.google.play.games",
                "url": "https://github.com/playgameservices/play-games-plugin-for-unity",
                "note": "Google 官方，Android 社交登录首选",
            },
        ],
        "custom_code_needed": "账户删除后端 API（DELETE /user，含30天软删除逻辑）；删除网页入口（Android 强制要求）",
    },
    "user_rights": {
        "solutions": [
            {
                "name": "Google UMP SDK（同意撤回）",
                "type": "免费官方",
                "covers": ["GDPR 同意撤回", "重新展示同意弹窗"],
                "unity_package": "com.google.ump",
                "url": "https://developers.google.com/admob/unity/privacy",
                "note": "调用 UMPConsentForm.loadAndPresentFromViewController 即可重新弹出",
            },
        ],
        "custom_code_needed": "设置页数据权利入口 UI；调用后端「导出我的数据」和「删除我的数据」接口",
    },
    "platform_config": {
        "solutions": [
            {
                "name": "App Store Connect（人工）",
                "type": "平台后台",
                "covers": ["隐私营养标签", "App 隐私声明"],
                "unity_package": None,
                "url": "https://appstoreconnect.apple.com/",
                "note": "代码无法替代，须在其他系统全部实现后再填写，否则声明与实现不符",
            },
            {
                "name": "Google Play Console（人工）",
                "type": "平台后台",
                "covers": ["数据安全表单", "IARC 内容分级", "账户删除 URL 填写"],
                "unity_package": None,
                "url": "https://play.google.com/console/",
                "note": "代码无法替代，最后统一在 Play Console 逐项填写",
            },
        ],
        "custom_code_needed": "无代码工作量，全为平台后台人工操作",
    },
}


def _platform_findings(game_info: Dict, platforms: List[str]) -> List[Dict]:
    features = game_info.get("features", [])
    min_age = game_info.get("min_user_age", 18)
    results = []
    for platform in platforms:
        for chk in PLATFORM_CHECKS.get(platform, []):
            try:
                if not chk["applies_when"](features, min_age, None):
                    continue
            except Exception:
                pass
            results.append({
                "id": chk["id"],
                "platform": platform,
                "category": "platform_policy",
                "title": chk["title"],
                "severity": chk["severity"],
                "detail": chk["detail"],
                "fix": chk["fix"],
                "guideline": chk.get("guideline", ""),
            })
    return results


def _legal_findings(game_info: Dict, markets: List[str]) -> List[Dict]:
    features = game_info.get("features", [])
    min_age = game_info.get("min_user_age", 18)
    results = []
    for law, data in MARKET_LEGAL_CHECKS.items():
        if not any(m in data.get("markets", []) for m in markets):
            continue
        if data.get("kids_only") and min_age >= 13:
            continue
        for chk in data.get("checks", []):
            results.append({
                "id": chk["id"],
                "platform": "all",
                "category": "legal",
                "law": law,
                "title": chk["title"],
                "severity": chk["severity"],
                "detail": chk["detail"],
                "fix": chk.get("fix", ""),
            })
    return results


# ── 系统架构映射 ─────────────────────────────────────────────────────────────
# 每个系统定义：id / 名称 / 描述 / 对应 finding ids / 依赖的其他系统id
_SYSTEM_DEFS = [
    {
        "id": "privacy_consent",
        "name": "隐私与同意系统",
        "icon": "🔐",
        "description": "在任何数据收集或广告行为之前，向用户展示同意弹窗并记录同意状态。所有其他系统的前置条件。",
        "finding_ids": ["ios_att", "gdpr_consent", "gdpr_privacy_policy", "ccpa_do_not_sell",
                        "aadc_default_privacy", "android_privacy_policy"],
        "depends_on": [],
        "required_before": ["ads", "analytics", "account", "iap"],
    },
    {
        "id": "child_protection",
        "name": "儿童保护系统",
        "icon": "👶",
        "description": "面向 13 岁以下用户的强制合规层：家长门控、COPPA 同意、禁止追踪广告、儿童认证 SDK。",
        "finding_ids": ["ios_parental_gate", "ios_kids_sdk", "android_kids_policy",
                        "coppa_parental_consent", "coppa_no_behavioral_ads", "coppa_no_pii"],
        "depends_on": ["privacy_consent"],
        "required_before": ["ads", "iap"],
    },
    {
        "id": "iap",
        "name": "内购系统",
        "icon": "💳",
        "description": "通过平台官方支付渠道（StoreKit / Play Billing）处理所有虚拟商品购买，禁止引导外部支付。",
        "finding_ids": ["ios_iap_storekit", "android_play_billing"],
        "depends_on": ["privacy_consent"],
        "required_before": [],
    },
    {
        "id": "ads",
        "name": "广告系统",
        "icon": "📢",
        "description": "合规展示广告：ATT 授权后才可个性化，儿童用户必须关闭行为追踪，插屏须有关闭按钮。",
        "finding_ids": ["ios_att", "coppa_no_behavioral_ads", "android_ads_policy"],
        "depends_on": ["privacy_consent", "child_protection"],
        "required_before": [],
    },
    {
        "id": "account",
        "name": "账户与身份系统",
        "icon": "👤",
        "description": "用户注册 / 第三方登录 / 账户彻底删除（含数据）。有第三方登录时必须提供 Sign in with Apple。",
        "finding_ids": ["ios_account_deletion", "android_account_deletion", "ios_sign_in_apple"],
        "depends_on": ["privacy_consent"],
        "required_before": ["user_rights"],
    },
    {
        "id": "user_rights",
        "name": "用户数据权利系统",
        "icon": "⚖️",
        "description": "GDPR 要求的查看 / 更正 / 删除数据入口，及随时撤回同意的机制。",
        "finding_ids": ["gdpr_data_rights", "gdpr_consent_withdrawal", "coppa_no_pii"],
        "depends_on": ["account", "privacy_consent"],
        "required_before": [],
    },
    {
        "id": "platform_config",
        "name": "平台配置与发布合规",
        "icon": "🏪",
        "description": "在 App Store Connect / Play Console 填写的表单类合规：数据安全、内容分级、隐私营养标签等。必须在其他系统全部实现后再填写，否则声明内容与实际不符。",
        "finding_ids": ["android_data_safety", "ios_privacy_labels", "android_iarc",
                        "android_aab", "android_target_api"],
        "depends_on": ["privacy_consent", "iap", "ads", "account", "child_protection", "user_rights"],
        "required_before": [],
    },
]


def _build_required_systems(findings: List[Dict]) -> List[Dict]:
    """
    把 findings 按「必要系统」分组，标注依赖关系和优先级。
    只输出至少有一条 finding 命中的系统。
    """
    finding_ids_in_report = {f.get("id") for f in findings}
    systems = []
    for sdef in _SYSTEM_DEFS:
        matched = [f for f in findings if f.get("id") in sdef["finding_ids"]]
        if not matched:
            continue
        critical_count = sum(1 for f in matched if f.get("severity") == "critical")
        high_count = sum(1 for f in matched if f.get("severity") == "high")
        # 系统整体严重程度
        if critical_count:
            system_severity = "critical"
        elif high_count:
            system_severity = "high"
        else:
            system_severity = "medium"
        systems.append({
            "id": sdef["id"],
            "name": sdef["name"],
            "icon": sdef["icon"],
            "description": sdef["description"],
            "severity": system_severity,
            "issue_count": len(matched),
            "critical_count": critical_count,
            "high_count": high_count,
            "depends_on": [
                {
                    "id": dep_id,
                    "name": next((sd["name"] for sd in _SYSTEM_DEFS if sd["id"] == dep_id), dep_id),
                    "icon": next((sd["icon"] for sd in _SYSTEM_DEFS if sd["id"] == dep_id), ""),
                }
                for dep_id in sdef["depends_on"]
                if dep_id in {
                    sd["id"] for sd in _SYSTEM_DEFS
                    if any(f.get("id") in sd["finding_ids"] for f in findings)
                }
            ],
            "findings": [
                {"id": f.get("id"), "title": f.get("title"), "severity": f.get("severity")}
                for f in matched
            ],
            "recommended_solutions": _SYSTEM_SOLUTIONS.get(sdef["id"], {}).get("solutions", []),
            "custom_code_needed": _SYSTEM_SOLUTIONS.get(sdef["id"], {}).get("custom_code_needed", ""),
        })
    # 按依赖顺序排序（depends_on 现在是对象列表，用 dep["id"] 比较）
    ordered, remaining = [], list(systems)
    visited = set()
    max_iter = len(systems) * 2
    i = 0
    while remaining and i < max_iter:
        i += 1
        for s in list(remaining):
            dep_ids = [d["id"] for d in s["depends_on"]]
            if all(dep_id in visited for dep_id in dep_ids):
                ordered.append(s)
                visited.add(s["id"])
                remaining.remove(s)
    ordered.extend(remaining)
    return ordered


def audit_game(
    game_info: Dict,
    project_path: Optional[str] = None,
    target_markets: Optional[List[str]] = None,
    target_platforms: Optional[List[str]] = None,
) -> Dict[str, Any]:
    target_markets = target_markets or ["US", "EU"]
    target_platforms = target_platforms or ["ios", "android"]

    pf = _platform_findings(game_info, target_platforms)
    lf = _legal_findings(game_info, target_markets)

    code_findings = []
    scan_performed = False
    if project_path:
        try:
            from engines.code_scanner import scan_project
            sr = scan_project(project_path)
            if "findings" in sr:
                code_findings = [
                    {
                        "id": f.get("rule_id", ""),
                        "platform": f.get("platform", "unity"),
                        "category": "code_scan",
                        "title": f.get("title", ""),
                        "severity": f.get("severity", "medium"),
                        "detail": f.get("detail", ""),
                        "fix": f.get("fix", ""),
                        "file_path": f.get("file_path", ""),
                    }
                    for f in sr["findings"] if f.get("status") != "pass"
                ]
                scan_performed = True
        except Exception:
            pass

    order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    seen = set()
    all_findings = []
    for f in pf + lf + code_findings:
        fid = f.get("id", "")
        if fid and fid in seen:
            continue
        if fid:
            seen.add(fid)
        all_findings.append(f)
    all_findings.sort(key=lambda x: order.get(x.get("severity", "low"), 9))

    critical = [f for f in all_findings if f.get("severity") == "critical"]
    high = [f for f in all_findings if f.get("severity") == "high"]
    medium = [f for f in all_findings if f.get("severity") == "medium"]

    risk_level = "critical" if critical else ("high" if high else ("medium" if medium else "low"))

    required_systems = _build_required_systems(all_findings)

    # fix_priority_list：按系统实现顺序排列（依赖顺序），同系统内按 severity 排
    # 目的：开发者按照优先清单顺序推进，不会出现"先做最后才能做的步骤"
    sev_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    finding_to_system: Dict[str, int] = {}   # finding_id -> 系统在 required_systems 中的位置
    for sys_idx, sys in enumerate(required_systems):
        for fitem in sys.get("findings", []):
            finding_to_system.setdefault(fitem["id"], sys_idx)

    def _priority_key(f: Dict):
        sys_idx = finding_to_system.get(f.get("id", ""), 999)
        sev_idx = sev_order.get(f.get("severity", "low"), 9)
        return (sys_idx, sev_idx)

    priority_findings = sorted(all_findings, key=_priority_key)

    fix_priority_list = []
    for i, f in enumerate(priority_findings[:15]):   # 最多 15 条，覆盖更多
        sys_idx = finding_to_system.get(f.get("id", ""), None)
        sys_name = required_systems[sys_idx]["name"] if sys_idx is not None and sys_idx < len(required_systems) else ""
        sys_icon = required_systems[sys_idx]["icon"] if sys_idx is not None and sys_idx < len(required_systems) else ""
        fix_priority_list.append({
            "priority": i + 1,
            "system": f"{sys_icon} {sys_name}".strip(),
            "title": f["title"],
            "severity": f["severity"],
            "platform": f["platform"],
            "category": f["category"],
            "fix": f.get("fix", ""),
            "detail": f.get("detail", ""),
            "recommended_package": _FINDING_PACKAGES.get(f.get("id", ""), ""),
        })

    return {
        "audit_summary": {
            "risk_level": risk_level,
            "total_issues": len(all_findings),
            "critical": len(critical),
            "high": len(high),
            "medium": len(medium),
            "scan_performed": scan_performed,
            "project_path": project_path or "未提供（仅问卷式检测）",
            "target_markets": target_markets,
            "target_platforms": target_platforms,
        },
        "required_systems": required_systems,
        "findings": all_findings,
        "fix_priority_list": fix_priority_list,
        "note": "平台配置类问题（App Store Connect / Play Console 表单）无法通过代码扫描检测，须手动核查",
    }
