"""
代码静态扫描引擎

扫描已有项目目录，自动识别合规缺项：
- iOS 项目：检查 Info.plist / AppDelegate / Swift 源码
- Android 项目：检查 AndroidManifest.xml / build.gradle / Kotlin 源码
- Unity 项目：检查 ProjectSettings / Packages/manifest.json / C# 源码

使用方式：
  python3 engines/code_scanner.py /path/to/your/project
  python3 engines/code_scanner.py /path/to/your/project --json
"""

import os
import re
import json
import sys
import argparse
import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple


# ── 项目类型检测 ─────────────────────────────────────────────────────────────

def detect_project_type(project_path: Path) -> List[str]:
    """自动检测项目类型，可同时返回多种（如 Unity 项目同时包含 iOS/Android 导出）"""
    types = []

    # Unity：ProjectSettings/ProjectSettings.asset 是特征文件
    if (project_path / "ProjectSettings" / "ProjectSettings.asset").exists():
        types.append("unity")

    # iOS：存在 .xcodeproj 或 Info.plist
    has_xcodeproj = any(project_path.rglob("*.xcodeproj"))
    has_infoplist = any(project_path.rglob("Info.plist"))
    if has_xcodeproj or has_infoplist:
        types.append("ios")

    # Android：存在 AndroidManifest.xml 且有 build.gradle
    has_manifest = any(project_path.rglob("AndroidManifest.xml"))
    has_gradle = any(project_path.rglob("build.gradle")) or any(project_path.rglob("build.gradle.kts"))
    if has_manifest and has_gradle:
        types.append("android")

    # 纯 Android（无 Unity）
    if not types and has_manifest:
        types.append("android")

    return types if types else ["unknown"]


# ── 文件读取工具 ─────────────────────────────────────────────────────────────

def read_file_safe(path: Path, max_bytes: int = 500_000) -> str:
    """安全读取文件，超过 max_bytes 截断"""
    try:
        content = path.read_bytes()[:max_bytes]
        return content.decode("utf-8", errors="replace")
    except Exception:
        return ""


def find_files(project_path: Path, patterns: List[str], exclude_dirs: List[str] = None) -> List[Path]:
    """在项目中查找符合 glob 模式的文件"""
    exclude = set(exclude_dirs or ["node_modules", ".git", "build", "DerivedData", "Library", "Temp"])
    results = []
    for pattern in patterns:
        for f in project_path.rglob(pattern):
            if not any(part in exclude for part in f.parts):
                results.append(f)
    return results


def grep_in_files(files: List[Path], pattern: str, flags: int = re.IGNORECASE) -> List[Tuple[Path, str]]:
    """在文件列表中搜索正则模式，返回 (文件路径, 匹配行) 列表"""
    matches = []
    regex = re.compile(pattern, flags)
    for f in files:
        content = read_file_safe(f)
        for line in content.splitlines():
            if regex.search(line):
                matches.append((f, line.strip()))
                break  # 每个文件只记录第一次匹配
    return matches


# ── 扫描结果构建 ─────────────────────────────────────────────────────────────

def make_finding(
    rule_id: str,
    title: str,
    severity: str,  # critical / high / medium / low / pass
    status: str,    # found / missing / warning / skipped
    detail: str,
    platform: str,
    guideline: str = "",
    fix: str = "",
    file_path: str = "",
) -> Dict:
    return {
        "rule_id": rule_id,
        "platform": platform,
        "title": title,
        "severity": severity,
        "status": status,
        "detail": detail,
        "guideline": guideline,
        "fix": fix,
        "file_path": file_path,
    }


# ── iOS 扫描 ─────────────────────────────────────────────────────────────────

def scan_ios(project_path: Path) -> List[Dict]:
    findings = []

    # 找 Info.plist（跳过 build 产物）
    plists = find_files(project_path, ["Info.plist"],
                        exclude_dirs=["DerivedData", "build", ".git", "Pods"])
    plist_texts = [(p, read_file_safe(p)) for p in plists]

    swift_files = find_files(project_path, ["*.swift", "*.m"],
                             exclude_dirs=["DerivedData", "build", ".git", "Pods"])

    # ── Info.plist 权限描述字符串 ─────────────────────────────────

    permission_keys = {
        "NSUserTrackingUsageDescription": {
            "rule_id": "ios_att_usage_desc",
            "title": "ATT 追踪权限描述（NSUserTrackingUsageDescription）",
            "guideline": "App Store 5.1.2 / iOS 14.5+",
            "fix": "Info.plist 中添加 NSUserTrackingUsageDescription 键，说明追踪用途",
            "severity": "critical",
        },
        "NSLocationWhenInUseUsageDescription": {
            "rule_id": "ios_location_when_in_use",
            "title": "前台位置权限描述",
            "guideline": "App Store 5.1.1",
            "fix": "Info.plist 中添加 NSLocationWhenInUseUsageDescription",
            "severity": "critical",
        },
        "NSLocationAlwaysAndWhenInUseUsageDescription": {
            "rule_id": "ios_location_always",
            "title": "后台位置权限描述",
            "guideline": "App Store 5.1.1",
            "fix": "Info.plist 中添加 NSLocationAlwaysAndWhenInUseUsageDescription，并准备向 Apple 说明后台使用场景",
            "severity": "critical",
        },
        "NSCameraUsageDescription": {
            "rule_id": "ios_camera_desc",
            "title": "摄像头权限描述",
            "guideline": "App Store 5.1.1",
            "fix": "Info.plist 中添加 NSCameraUsageDescription",
            "severity": "high",
        },
        "NSMicrophoneUsageDescription": {
            "rule_id": "ios_mic_desc",
            "title": "麦克风权限描述",
            "guideline": "App Store 5.1.1",
            "fix": "Info.plist 中添加 NSMicrophoneUsageDescription",
            "severity": "high",
        },
        "NSPhotoLibraryUsageDescription": {
            "rule_id": "ios_photos_desc",
            "title": "相册权限描述",
            "guideline": "App Store 5.1.1",
            "fix": "Info.plist 中添加 NSPhotoLibraryUsageDescription",
            "severity": "medium",
        },
    }

    all_plist_content = " ".join(text for _, text in plist_texts)

    for key, meta in permission_keys.items():
        if key in all_plist_content:
            findings.append(make_finding(
                rule_id=meta["rule_id"], platform="ios",
                title=meta["title"], severity="pass", status="found",
                detail=f"✅ {key} 已声明",
                guideline=meta["guideline"],
            ))
        # 如果源码中使用了该权限但 plist 未声明，标记缺失
        elif key == "NSUserTrackingUsageDescription":
            att_usage = grep_in_files(swift_files, r"ATTrackingManager|requestTrackingAuthorization|IDFA")
            if att_usage:
                findings.append(make_finding(
                    rule_id=meta["rule_id"], platform="ios",
                    title=meta["title"], severity=meta["severity"], status="missing",
                    detail=f"源码中使用了 ATT 相关 API，但 Info.plist 缺少 {key}",
                    guideline=meta["guideline"], fix=meta["fix"],
                    file_path=str(att_usage[0][0].relative_to(project_path)),
                ))

    # ── StoreKit / IAP ────────────────────────────────────────────

    storekit_usage = grep_in_files(swift_files, r"import StoreKit|StoreKit|SKPayment|Product\.purchase")
    if storekit_usage:
        findings.append(make_finding(
            rule_id="ios_storekit_found", platform="ios",
            title="StoreKit 使用检测", severity="pass", status="found",
            detail=f"✅ 检测到 StoreKit 使用（{storekit_files_summary(storekit_usage, project_path)}）",
            guideline="App Store 3.1.1",
        ))
    else:
        # 检查是否有购买相关关键词但没用 StoreKit
        purchase_hints = grep_in_files(swift_files, r"purchase|payment|buy|checkout|subscription", re.IGNORECASE)
        if purchase_hints:
            findings.append(make_finding(
                rule_id="ios_iap_no_storekit", platform="ios",
                title="检测到购买相关代码但未使用 StoreKit",
                severity="critical", status="warning",
                detail="源码中有 purchase/payment 关键词，但未发现 StoreKit import。如有虚拟商品必须使用 StoreKit。",
                guideline="App Store 3.1.1",
                fix="import StoreKit，使用 Product.purchase() 处理所有虚拟商品购买",
            ))

    # ── ATT 请求 ──────────────────────────────────────────────────

    att_request = grep_in_files(swift_files, r"requestTrackingAuthorization")
    if att_request:
        findings.append(make_finding(
            rule_id="ios_att_request", platform="ios",
            title="ATT 授权请求", severity="pass", status="found",
            detail="✅ 检测到 ATTrackingManager.requestTrackingAuthorization 调用",
            guideline="App Store 5.1.2",
        ))

    # ── Sign in with Apple ────────────────────────────────────────

    siwa = grep_in_files(swift_files, r"ASAuthorizationAppleID|SignInWithApple|authorizationController")
    third_party_login = grep_in_files(swift_files, r"GIDSignIn|FBSDKLoginKit|LoginManager|TwitterKit")
    if third_party_login and not siwa:
        findings.append(make_finding(
            rule_id="ios_sign_in_apple_missing", platform="ios",
            title="Sign in with Apple 缺失",
            severity="critical", status="missing",
            detail="检测到第三方登录（Google/Facebook 等），但未发现 Sign in with Apple 实现",
            guideline="App Store 4.8",
            fix="添加 Sign in with Apple（ASAuthorizationAppleIDProvider），详见 AppleSignIn.swift 模板",
            file_path=str(third_party_login[0][0].relative_to(project_path)),
        ))
    elif siwa:
        findings.append(make_finding(
            rule_id="ios_sign_in_apple_found", platform="ios",
            title="Sign in with Apple", severity="pass", status="found",
            detail="✅ 检测到 Sign in with Apple 实现",
            guideline="App Store 4.8",
        ))

    # ── 账户删除 ──────────────────────────────────────────────────

    delete_account = grep_in_files(swift_files, r"delete.*account|deleteAccount|account.*delet",
                                   re.IGNORECASE)
    if delete_account:
        findings.append(make_finding(
            rule_id="ios_account_deletion_found", platform="ios",
            title="账户删除功能", severity="pass", status="found",
            detail="✅ 检测到账户删除相关代码",
            guideline="App Store 5.1.1(v)",
        ))
    else:
        findings.append(make_finding(
            rule_id="ios_account_deletion_missing", platform="ios",
            title="账户删除功能缺失",
            severity="critical", status="missing",
            detail="未发现账户删除相关代码（deleteAccount / delete account）",
            guideline="App Store 5.1.1(v)，2022年6月起强制",
            fix="在设置页添加账户删除入口，参见 AccountDeletionView.swift 模板",
        ))

    return findings


def storekit_files_summary(matches: List[Tuple[Path, str]], base: Path) -> str:
    files = list({str(f.relative_to(base)) for f, _ in matches[:3]})
    return ", ".join(files)


# ── Android 扫描 ─────────────────────────────────────────────────────────────

def scan_android(project_path: Path) -> List[Dict]:
    findings = []

    manifests = find_files(project_path, ["AndroidManifest.xml"],
                           exclude_dirs=[".git", "build", ".gradle"])
    gradle_files = find_files(project_path, ["build.gradle", "build.gradle.kts", "*.gradle"],
                              exclude_dirs=[".git", "build"])
    kotlin_files = find_files(project_path, ["*.kt", "*.java"],
                              exclude_dirs=[".git", "build", ".gradle"])

    manifest_content = " ".join(read_file_safe(m) for m in manifests)
    gradle_content = " ".join(read_file_safe(g) for g in gradle_files)

    # ── Target SDK Version ────────────────────────────────────────

    target_sdk_match = re.search(r"targetSdkVersion\s*[=:]\s*(\d+)", gradle_content)
    if target_sdk_match:
        target_sdk = int(target_sdk_match.group(1))
        if target_sdk >= 35:
            findings.append(make_finding(
                rule_id="android_target_sdk", platform="android",
                title=f"Target SDK Version: {target_sdk}",
                severity="pass", status="found",
                detail=f"✅ targetSdkVersion = {target_sdk}（≥ 35，符合 2025年要求）",
                guideline="Google Play Target API Level Policy",
            ))
        elif target_sdk >= 34:
            findings.append(make_finding(
                rule_id="android_target_sdk", platform="android",
                title=f"Target SDK Version: {target_sdk}（偏低）",
                severity="high", status="warning",
                detail=f"targetSdkVersion = {target_sdk}，2025年新应用要求 ≥ 35",
                guideline="Google Play Target API Level Policy",
                fix="build.gradle: targetSdkVersion 35",
            ))
        else:
            findings.append(make_finding(
                rule_id="android_target_sdk", platform="android",
                title=f"Target SDK Version 过低: {target_sdk}",
                severity="critical", status="missing",
                detail=f"targetSdkVersion = {target_sdk}，不符合 Google Play 要求（需 ≥ 34，建议 35）",
                guideline="Google Play Target API Level Policy",
                fix="build.gradle: targetSdkVersion 35，compileSdkVersion 35",
            ))
    else:
        findings.append(make_finding(
            rule_id="android_target_sdk", platform="android",
            title="未检测到 targetSdkVersion",
            severity="high", status="warning",
            detail="未能从 build.gradle 中解析到 targetSdkVersion",
            guideline="Google Play Target API Level Policy",
            fix="确认 build.gradle 中存在 targetSdkVersion 设置",
        ))

    # ── Play Billing ──────────────────────────────────────────────

    billing_in_gradle = "billing" in gradle_content.lower()
    billing_in_code = bool(grep_in_files(kotlin_files, r"BillingClient|billingclient|launchBillingFlow"))
    purchase_hints = grep_in_files(kotlin_files, r"purchase|payment|buy|checkout", re.IGNORECASE)

    if billing_in_gradle and billing_in_code:
        findings.append(make_finding(
            rule_id="android_play_billing", platform="android",
            title="Google Play Billing", severity="pass", status="found",
            detail="✅ 检测到 Play Billing Library 依赖和 BillingClient 使用",
            guideline="Google Play 结算政策",
        ))
    elif purchase_hints and not billing_in_code:
        findings.append(make_finding(
            rule_id="android_play_billing_missing", platform="android",
            title="检测到购买代码但未使用 Play Billing",
            severity="critical", status="warning",
            detail="源码中有购买相关关键词，但未发现 BillingClient。如有数字商品必须使用 Play Billing。",
            guideline="Google Play 结算政策",
            fix="添加依赖：implementation 'com.android.billingclient:billing-ktx:6.2.1'，参见 BillingManager.kt 模板",
        ))

    # ── 后台位置权限 ──────────────────────────────────────────────

    if "ACCESS_BACKGROUND_LOCATION" in manifest_content:
        findings.append(make_finding(
            rule_id="android_background_location", platform="android",
            title="后台位置权限（ACCESS_BACKGROUND_LOCATION）",
            severity="high", status="warning",
            detail="检测到 ACCESS_BACKGROUND_LOCATION 声明。此权限受严格限制，须向 Google 提交使用说明表单。",
            guideline="Google Play 位置权限政策",
            fix="确认后台位置使用场景合规（仅限导航/家庭安全等），并在 Play Console 提交说明",
        ))

    # ── 危险权限 ──────────────────────────────────────────────────

    sensitive_permissions = {
        "READ_CONTACTS": ("android_contacts_perm", "medium"),
        "READ_CALL_LOG": ("android_call_log_perm", "high"),
        "PROCESS_OUTGOING_CALLS": ("android_call_perm", "high"),
        "RECORD_AUDIO": ("android_audio_perm", "medium"),
        "READ_SMS": ("android_sms_perm", "high"),
        "CAMERA": ("android_camera_perm", "medium"),
    }

    for perm, (rule_id, severity) in sensitive_permissions.items():
        if f'"{perm}"' in manifest_content or f"android.permission.{perm}" in manifest_content:
            findings.append(make_finding(
                rule_id=rule_id, platform="android",
                title=f"敏感权限声明：{perm}",
                severity=severity, status="warning",
                detail=f"声明了 {perm} 权限，须确保仅在必要时请求，并向用户说明用途",
                guideline="Google Play 权限政策",
                fix="确保在使用功能时（非启动时）请求权限，并提供清晰的用途说明",
            ))

    # ── 账户删除 ──────────────────────────────────────────────────

    delete_account = grep_in_files(kotlin_files, r"delete.*account|deleteAccount|account.*delet",
                                   re.IGNORECASE)
    if delete_account:
        findings.append(make_finding(
            rule_id="android_account_deletion", platform="android",
            title="账户删除功能", severity="pass", status="found",
            detail="✅ 检测到账户删除相关代码",
            guideline="Google Play 账户删除政策",
        ))
    else:
        findings.append(make_finding(
            rule_id="android_account_deletion_missing", platform="android",
            title="账户删除功能缺失",
            severity="critical", status="missing",
            detail="未发现账户删除相关代码",
            guideline="Google Play 账户删除政策，2024年5月起强制",
            fix="添加账户删除入口，参见 AccountDeletionActivity.kt 模板；还需在 Play Console 填写网页版删除 URL",
        ))

    # ── 隐私政策 ──────────────────────────────────────────────────

    privacy_url = grep_in_files(kotlin_files, r"privacy.*policy|privacyPolicy|privacy_policy",
                                re.IGNORECASE)
    if privacy_url:
        findings.append(make_finding(
            rule_id="android_privacy_policy", platform="android",
            title="隐私政策入口", severity="pass", status="found",
            detail="✅ 检测到隐私政策相关引用",
            guideline="Google Play 用户数据政策",
        ))
    else:
        findings.append(make_finding(
            rule_id="android_privacy_policy_missing", platform="android",
            title="App 内隐私政策入口缺失",
            severity="high", status="missing",
            detail="未在源码中发现隐私政策链接",
            guideline="Google Play 用户数据政策",
            fix="在设置页添加隐私政策链接，并在 Play Console → 商店设置 → 隐私权政策填写 URL",
        ))

    return findings


# ── Unity 扫描 ───────────────────────────────────────────────────────────────

def scan_unity(project_path: Path) -> List[Dict]:
    findings = []

    # ProjectSettings/ProjectSettings.asset（包含 targetApiLevel、bundleId 等）
    project_settings_path = project_path / "ProjectSettings" / "ProjectSettings.asset"
    settings_content = read_file_safe(project_settings_path) if project_settings_path.exists() else ""

    # Packages/manifest.json（已安装的 Unity 包）
    manifest_path = project_path / "Packages" / "manifest.json"
    manifest_content = read_file_safe(manifest_path) if manifest_path.exists() else ""

    cs_files = find_files(project_path, ["*.cs"],
                          exclude_dirs=[".git", "Library", "Temp", "Build", "Builds"])

    # ── Unity IAP ────────────────────────────────────────────────

    has_unity_iap = "com.unity.purchasing" in manifest_content
    iap_usage = grep_in_files(cs_files, r"UnityEngine\.Purchasing|IStoreListener|IDetailedStoreListener|InitiatePurchase")
    purchase_hints = grep_in_files(cs_files, r"purchase|payment|buy|coin|gem|credit", re.IGNORECASE)

    if has_unity_iap and iap_usage:
        findings.append(make_finding(
            rule_id="unity_iap_found", platform="unity",
            title="Unity IAP", severity="pass", status="found",
            detail="✅ 已安装 com.unity.purchasing 且检测到 IAPManager 实现",
            guideline="App Store 3.1.1 / Google Play 结算政策",
        ))
    elif purchase_hints and not has_unity_iap:
        findings.append(make_finding(
            rule_id="unity_iap_missing", platform="unity",
            title="检测到购买逻辑但未安装 Unity IAP",
            severity="critical", status="warning",
            detail="C# 源码中有购买相关关键词，但 Packages/manifest.json 中未发现 com.unity.purchasing",
            guideline="App Store 3.1.1 / Google Play 结算政策",
            fix="Window > Package Manager > 搜索 In App Purchasing 并安装（com.unity.purchasing）",
        ))

    # ── ATT（iOS）────────────────────────────────────────────────

    att_usage = grep_in_files(cs_files, r"ATTrackingStatusBinding|RequestAuthorizationTracking|unity\.advertisement\.ios")
    if att_usage:
        findings.append(make_finding(
            rule_id="unity_att_found", platform="unity",
            title="ATT 请求实现（iOS）", severity="pass", status="found",
            detail="✅ 检测到 ATTrackingStatusBinding 相关代码",
            guideline="App Store 5.1.2",
        ))
    else:
        ads_usage = grep_in_files(cs_files, r"Advertisement|UnityAds|AdMob|GoogleMobileAds", re.IGNORECASE)
        if ads_usage:
            findings.append(make_finding(
                rule_id="unity_att_missing", platform="unity",
                title="ATT 请求缺失（有广告 SDK 时必须）",
                severity="critical", status="missing",
                detail="检测到广告 SDK 使用，但未发现 ATT 请求代码（iOS 14.5+ 强制要求）",
                guideline="App Store 5.1.2",
                fix="安装 com.unity.advertisement.ios.support，使用 ATTrackingStatusBinding.RequestAuthorizationTracking()，参见 ATTHandler.cs 模板",
            ))

    # ── 儿童广告合规 ──────────────────────────────────────────────

    child_directed = grep_in_files(cs_files, r"user-non-behavioral|tagForChildDirectedTreatment|SetTagForChildDirectedTreatment|child.*directed",
                                   re.IGNORECASE)
    ads_sdk = grep_in_files(cs_files, r"Advertisement|MobileAds|AdRequest|UnityAds", re.IGNORECASE)

    if ads_sdk and not child_directed:
        findings.append(make_finding(
            rule_id="unity_kids_ads", platform="unity",
            title="广告 SDK 未配置儿童合规模式",
            severity="high", status="warning",
            detail="检测到广告 SDK，但未发现儿童定向广告配置。若目标用户含儿童，必须禁用个性化广告。",
            guideline="App Store 1.3 / Google Play 家庭政策 / COPPA",
            fix="参见 ParentalGate.cs 中的 AdsPrivacyConfig.ConfigureChildDirectedAds() 实现",
        ))

    # ── 账户删除 ──────────────────────────────────────────────────

    delete_account = grep_in_files(cs_files, r"delete.*account|deleteAccount|account.*delet|DeleteAccount",
                                   re.IGNORECASE)
    if delete_account:
        findings.append(make_finding(
            rule_id="unity_account_deletion", platform="unity",
            title="账户删除功能", severity="pass", status="found",
            detail="✅ 检测到账户删除相关代码",
            guideline="App Store 5.1.1(v) / Google Play 账户删除政策",
        ))
    else:
        findings.append(make_finding(
            rule_id="unity_account_deletion_missing", platform="unity",
            title="账户删除功能缺失",
            severity="critical", status="missing",
            detail="未发现账户删除相关代码（iOS 和 Android 均要求）",
            guideline="App Store 5.1.1(v) / Google Play 账户删除政策",
            fix="参见 AccountDeletionUI.cs 模板",
        ))

    # ── 家长门控 ──────────────────────────────────────────────────

    parental_gate = grep_in_files(cs_files, r"ParentalGate|parental.*gate|parent.*verify|parent.*control",
                                  re.IGNORECASE)
    external_url = grep_in_files(cs_files, r"Application\.OpenURL", re.IGNORECASE)

    if external_url and not parental_gate:
        findings.append(make_finding(
            rule_id="unity_parental_gate_missing", platform="unity",
            title="检测到外部链接但无家长门控",
            severity="high", status="warning",
            detail="发现 Application.OpenURL 调用，儿童 App 须在外部跳转前展示家长门控",
            guideline="App Store 1.3",
            fix="参见 ParentalGate.cs 模板，在 Application.OpenURL 前调用 ParentalGate.Show()",
        ))

    # ── 隐私政策 ──────────────────────────────────────────────────

    privacy = grep_in_files(cs_files, r"privacy.*policy|PrivacyPolicy|privacy_policy|privacyUrl",
                            re.IGNORECASE)
    if privacy:
        findings.append(make_finding(
            rule_id="unity_privacy_policy", platform="unity",
            title="隐私政策入口", severity="pass", status="found",
            detail="✅ 检测到隐私政策相关引用",
            guideline="App Store 5.1 / Google Play 用户数据政策",
        ))
    else:
        findings.append(make_finding(
            rule_id="unity_privacy_policy_missing", platform="unity",
            title="App 内隐私政策入口缺失",
            severity="high", status="missing",
            detail="未发现隐私政策链接",
            guideline="App Store 5.1 / Google Play 用户数据政策",
            fix="参见 PrivacyPolicyUI.cs 模板",
        ))

    # ── Target API Level（Android 导出）──────────────────────────

    target_api_match = re.search(r"AndroidTargetSdkVersion:\s*(\d+)", settings_content)
    if target_api_match:
        target_api = int(target_api_match.group(1))
        status = "pass" if target_api >= 35 else ("warning" if target_api >= 34 else "missing")
        severity = "pass" if target_api >= 35 else ("high" if target_api >= 34 else "critical")
        findings.append(make_finding(
            rule_id="unity_android_target_api", platform="unity",
            title=f"Android Target API Level: {target_api}",
            severity=severity, status=status,
            detail=f"ProjectSettings.asset 中 AndroidTargetSdkVersion = {target_api}",
            guideline="Google Play Target API Level Policy",
            fix="Player Settings → Android → Other Settings → Target API Level → 35",
        ))

    return findings


# ── 汇总报告 ─────────────────────────────────────────────────────────────────

def build_report(project_path: Path, findings: List[Dict], project_types: List[str]) -> Dict[str, Any]:
    total = len(findings)
    critical = [f for f in findings if f["severity"] == "critical" and f["status"] != "pass"]
    high = [f for f in findings if f["severity"] == "high" and f["status"] != "pass"]
    passed = [f for f in findings if f["status"] == "pass"]
    warnings = [f for f in findings if f["status"] == "warning"]

    if critical:
        risk_level = "critical"
    elif high:
        risk_level = "high"
    elif warnings:
        risk_level = "medium"
    else:
        risk_level = "low"

    return {
        "scan_time": datetime.datetime.now().isoformat(),
        "project_path": str(project_path),
        "project_types": project_types,
        "risk_level": risk_level,
        "summary": {
            "total_checks": total,
            "passed": len(passed),
            "critical": len(critical),
            "high": len(high),
            "warnings": len(warnings),
        },
        "findings": findings,
        "platform_summary": _platform_summary(findings),
        "note": "扫描基于静态代码分析，部分合规项（如 App Store Connect 表单、IARC 分级）需在平台侧手动完成",
    }


def _platform_summary(findings: List[Dict]) -> Dict:
    summary = {}
    for f in findings:
        p = f["platform"]
        if p not in summary:
            summary[p] = {"passed": 0, "issues": 0}
        if f["status"] == "pass":
            summary[p]["passed"] += 1
        elif f["severity"] in ("critical", "high"):
            summary[p]["issues"] += 1
    return summary


def print_report(report: Dict) -> None:
    risk_icon = {"critical": "🚨", "high": "⚠️", "medium": "⚡", "low": "✅"}.get(report["risk_level"], "❓")
    s = report["summary"]
    print(f"\n{'='*65}")
    print(f"  代码合规扫描报告  {risk_icon} 风险等级: {report['risk_level'].upper()}")
    print(f"{'='*65}")
    print(f"  项目路径  : {report['project_path']}")
    print(f"  项目类型  : {', '.join(report['project_types'])}")
    print(f"  扫描时间  : {report['scan_time'][:19]}")
    print(f"\n  统计：")
    print(f"    检查项总计  : {s['total_checks']}")
    print(f"    ✅ 通过      : {s['passed']}")
    print(f"    🚨 严重缺陷  : {s['critical']}")
    print(f"    ⚠️  高风险    : {s['high']}")
    print(f"    ⚡ 警告      : {s['warnings']}")

    issues = [f for f in report["findings"] if f["status"] != "pass"]
    if issues:
        print(f"\n  ── 需要处理的问题 {'─'*40}")
        for f in sorted(issues, key=lambda x: {"critical": 0, "high": 1, "medium": 2, "low": 3}.get(x["severity"], 9)):
            icon = {"critical": "🚨", "high": "⚠️", "medium": "⚡", "low": "💡"}.get(f["severity"], "•")
            print(f"\n  {icon} [{f['platform'].upper()}] {f['title']}")
            print(f"     {f['detail']}")
            if f.get("fix"):
                print(f"     修复建议: {f['fix']}")
            if f.get("guideline"):
                print(f"     参考: {f['guideline']}")
    else:
        print("\n  🎉 未发现明显合规问题")

    print(f"\n  ⚠️  {report['note']}")
    print(f"{'='*65}\n")


# ── 公开接口 ─────────────────────────────────────────────────────────────────

def scan_project(project_path: str) -> Dict[str, Any]:
    """
    扫描项目目录，返回合规扫描报告。

    参数：
      project_path - 项目根目录路径

    返回：
      结构化扫描报告（risk_level, findings, summary 等）
    """
    path = Path(project_path).expanduser().resolve()
    if not path.exists():
        return {"error": f"路径不存在: {project_path}"}
    if not path.is_dir():
        return {"error": f"路径不是目录: {project_path}"}

    project_types = detect_project_type(path)
    findings = []

    if "unity" in project_types:
        findings.extend(scan_unity(path))
    if "ios" in project_types:
        findings.extend(scan_ios(path))
    if "android" in project_types and "unity" not in project_types:
        findings.extend(scan_android(path))
    if "unknown" in project_types:
        return {"error": "无法识别项目类型（不是 Unity / iOS / Android 项目）"}

    return build_report(path, findings, project_types)


# ── CLI 入口 ─────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="代码静态合规扫描工具")
    parser.add_argument("project_path", help="项目根目录路径")
    parser.add_argument("--json", action="store_true", help="输出 JSON 格式报告")
    args = parser.parse_args()

    report = scan_project(args.project_path)

    if "error" in report:
        print(f"❌ 错误: {report['error']}")
        sys.exit(1)

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_report(report)


if __name__ == "__main__":
    main()
