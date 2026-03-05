#!/usr/bin/env python3
"""
平台政策专家 (Platform Policies Expert)

专精领域:
- Google Play Store政策
- Apple App Store审核指南
- 平台技术要求 (API级别、架构等)
- 平台儿童应用政策
- 平台隐私和数据政策
"""

from typing import Dict, List
from datetime import datetime

class PlatformPoliciesExpert:
    """平台政策专业专家"""
    
    def __init__(self):
        self.name = "平台政策专家"
        self.expertise_areas = [
            'Google_Play_Policies', 'App_Store_Guidelines',
            'Platform_Technical_Requirements', 'Platform_Family_Policies',
            'Platform_Privacy_Requirements'
        ]
        
        # Google Play当前技术要求
        self.google_play_requirements = {
            'target_api_level': {
                'new_apps': 33,      # API Level 33 (Android 13)
                'app_updates': 33,   # 现有应用更新
                'minimum': 23        # 最低支持API Level
            },
            'architecture_support': ['arm64-v8a', 'x86_64'],  # 64位架构必需
            'app_bundle': True,      # 推荐使用App Bundle
            'permissions': {
                'dangerous_permissions': ['CAMERA', 'LOCATION', 'MICROPHONE', 'STORAGE'],
                'requires_justification': True
            }
        }
        
        # 平台儿童应用政策
        self.family_policies = {
            'google_play': {
                'target_audience': ['children_under_13', 'mixed_audience'],
                'prohibited': [
                    'behavioral_advertising',
                    'location_based_features', 
                    'social_networking_features',
                    'sharing_personal_info'
                ],
                'required': [
                    'privacy_policy',
                    'parental_gate',
                    'age_appropriate_content'
                ]
            },
            'app_store': {
                'kids_category': True,
                'prohibited': [
                    'external_links',
                    'in_app_purchases_without_parental_gate',
                    'behavioral_advertising',
                    'sharing_location'
                ],
                'content_requirements': 'educational_or_entertaining'
            }
        }
    
    def analyze_compliance(self, app_info: Dict, context: Dict = None) -> Dict:
        """分析平台政策合规性"""
        
        print(f"    📱 {self.name}分析中... (检查平台技术和政策要求)")
        
        issues = []
        warnings = []
        passed = []
        
        # Google Play政策检查
        google_play_results = self._check_google_play_compliance(app_info)
        issues.extend(google_play_results['issues'])
        warnings.extend(google_play_results['warnings'])
        passed.extend(google_play_results['passed'])
        
        # Apple App Store检查 (如果相关)
        app_store_results = self._check_app_store_compliance(app_info)
        issues.extend(app_store_results['issues'])
        warnings.extend(app_store_results['warnings'])
        passed.extend(app_store_results['passed'])
        
        # 平台儿童应用政策检查
        if app_info.get('min_user_age', 0) < 13:
            family_results = self._check_family_policies_compliance(app_info)
            issues.extend(family_results['issues'])
            warnings.extend(family_results['warnings'])
            passed.extend(family_results['passed'])
        
        risk_level = self._assess_platform_compliance_risk(app_info, issues, warnings)
        
        return {
            'expert': self.name,
            'risk_level': risk_level,
            'issues': issues,
            'warnings': warnings,
            'passed': passed,
            'specialized_recommendations': self._generate_platform_recommendations(app_info, issues, warnings)
        }
    
    def _check_google_play_compliance(self, app_info: Dict) -> Dict:
        """Google Play Store 政策检查 (Google Play Policy 2024)"""

        issues = []
        warnings = []
        passed = []

        platforms = app_info.get('target_platforms', [])
        is_android = 'Android' in platforms or not platforms

        if not is_android:
            return {'issues': issues, 'warnings': warnings, 'passed': passed}

        min_age = app_info.get('min_user_age', 18)

        # ── 1. Target API Level ──
        target_sdk = app_info.get('target_sdk')
        required_api = self.google_play_requirements['target_api_level']['new_apps']
        if target_sdk:
            try:
                api_level = int(target_sdk)
                if api_level < required_api:
                    issues.append({
                        'policy': f'Google Play - Target API Level (必须 ≥ {required_api})',
                        'issue': f'目标 API 级别 {api_level} 低于 Google Play 要求的 {required_api}',
                        'requirement': f'2024 年 8 月起，新应用和更新必须以 API Level {required_api}+ (Android 13) 为目标；'
                                       f'不符合要求的更新将被拒绝上传',
                        'solution': f'在 build.gradle 中设置 targetSdkVersion {required_api}；'
                                    f'适配 Android 13 的运行时权限、精确闹钟权限和媒体权限变更',
                        'region': 'Global',
                        'severity': 'critical',
                        'reference': 'https://developer.android.com/google/play/requirements/target-sdk'
                    })
                else:
                    passed.append(f'✅ Target API Level: {api_level}（符合要求）')
            except ValueError:
                warnings.append({
                    'policy': 'Google Play - Target API Level',
                    'issue': 'API 级别格式无效',
                    'requirement': '必须为整数',
                    'solution': '确认 build.gradle 中 targetSdkVersion 设置正确',
                    'region': 'Global', 'severity': 'medium'
                })
        else:
            warnings.append({
                'policy': 'Google Play - Target API Level',
                'issue': '未提供目标 API 级别信息',
                'requirement': f'新应用必须使用 API Level {required_api}+',
                'solution': '在 build.gradle 中设置 targetSdkVersion',
                'region': 'Global', 'severity': 'high'
            })

        # ── 2. 64 位架构 ──
        if app_info.get('has_native_code'):
            issues.append({
                'policy': 'Google Play - 64 位架构支持',
                'issue': '包含原生代码的应用必须支持 64 位架构',
                'requirement': 'Google Play 要求所有含原生代码的应用同时提供 arm64-v8a 和 x86_64 ABI',
                'solution': 'build.gradle: android { defaultConfig { ndk { abiFilters "arm64-v8a", "x86_64" } } }',
                'region': 'Global',
                'severity': 'critical'
            })

        # ── 3. Google Play 结算系统（强制要求）──
        if app_info.get('has_in_app_purchases'):
            issues.append({
                'policy': 'Google Play 结算政策 - 强制使用 Play Billing',
                'issue': '应用内销售数字商品必须使用 Google Play 结算系统，不得绕过或引导外部支付',
                'requirement': '所有应用内虚拟商品（游戏道具、虚拟货币、解锁内容、订阅等）必须通过 '
                               'Google Play Billing Library 处理；违规将导致应用被下架',
                'solution': '集成 Play Billing Library 5.x+；使用 BillingClient 实现购买流程；'
                            '实物商品和线下服务可使用第三方支付',
                'region': 'Global',
                'severity': 'critical',
                'reference': 'https://support.google.com/googleplay/android-developer/answer/9858738'
            })

        # ── 4. 数据安全表单（Data Safety Section）──
        data_types = []
        if app_info.get('collects_educational_data'):
            data_types.append('应用活动数据')
        if app_info.get('cross_border_data_transfer'):
            data_types.append('个人信息（跨境传输）')
        if app_info.get('advertising_present') or app_info.get('uses_ai_algorithms'):
            data_types.append('设备或其他标识符')
        if app_info.get('uses_location_services'):
            data_types.append('位置信息')
        if app_info.get('biometric_data'):
            data_types.append('生物特征识别信息')
        if app_info.get('data_sharing_third_parties'):
            data_types.append('与第三方共享的数据')

        if data_types:
            issues.append({
                'policy': 'Google Play - 数据安全表单（Data Safety Section）',
                'issue': f'以下数据类型必须在 Play Console 数据安全表单中准确申报：{", ".join(data_types)}',
                'requirement': '2022 年起，所有应用必须在 Play Console 填写数据安全表单，声明：'
                               '收集的数据类型、用途、是否与第三方共享、是否加密传输、用户是否可删除；'
                               '表单内容与实际行为不符将导致应用被下架',
                'solution': '登录 Play Console → 应用内容 → 数据安全；逐项填写数据收集类型；'
                            '确保第三方 SDK 的数据收集行为也被纳入申报范围',
                'region': 'Global',
                'severity': 'critical',
                'reference': 'https://support.google.com/googleplay/android-developer/answer/10787469'
            })
        else:
            passed.append('✅ 数据安全表单：数据收集范围较小，低风险')

        # ── 5. 隐私政策（必须可公开访问）──
        collects_any_data = (
            app_info.get('collects_educational_data') or
            app_info.get('advertising_present') or
            app_info.get('data_sharing_third_parties') or
            app_info.get('uses_location_services') or
            app_info.get('cross_border_data_transfer')
        )
        if collects_any_data:
            if not app_info.get('privacy_policy_url'):
                issues.append({
                    'policy': 'Google Play - 隐私政策（必须公开可访问）',
                    'issue': '应用收集用户数据但未提供隐私政策 URL',
                    'requirement': 'Google Play 要求所有收集个人或敏感数据的应用提供隐私政策；'
                                   '必须在 Play Console 和应用内均可访问；不得设置登录墙',
                    'solution': '创建符合 GDPR/CCPA/COPPA 要求的隐私政策；'
                                '在 Play Console → 应用内容 → 隐私政策 中填写 URL；'
                                '在应用设置页面内嵌隐私政策入口',
                    'region': 'Global',
                    'severity': 'critical'
                })
            else:
                passed.append('✅ 隐私政策：已提供 URL')

        # ── 6. 后台位置权限（特殊限制）──
        if app_info.get('uses_location_services'):
            issues.append({
                'policy': 'Google Play - 后台位置权限限制',
                'issue': '使用位置服务的应用需要说明是否需要后台位置权限',
                'requirement': 'ACCESS_BACKGROUND_LOCATION 是受限权限，需要填写声明表单说明使用理由；'
                               '儿童应用（Family Policy）完全禁止后台位置权限；'
                               '不必要的后台位置权限将导致应用被拒',
                'solution': '仅在用户主动使用期间请求前台位置权限（ACCESS_FINE_LOCATION）；'
                            '如确需后台位置，提交声明并在 Play Console 填写使用理由表单',
                'region': 'Global',
                'severity': 'high' if min_age >= 13 else 'critical'
            })

        # ── 7. 权限最小化原则 ──
        sensitive_permissions = []
        if app_info.get('uses_camera_microphone'):
            sensitive_permissions.append('CAMERA / RECORD_AUDIO')
        if app_info.get('biometric_data'):
            sensitive_permissions.append('USE_BIOMETRIC')

        if sensitive_permissions:
            warnings.append({
                'policy': 'Google Play - 敏感权限最小化',
                'issue': f'应用请求高风险权限：{", ".join(sensitive_permissions)}',
                'requirement': '所有敏感权限必须仅用于核心功能；权限请求时机必须在用户触发相关功能时；'
                               '不得在应用启动时批量请求权限',
                'solution': '在用户触发相关功能时才请求权限；说明使用目的；'
                            '用户拒绝后优雅降级，不得强制要求权限才能使用基本功能',
                'region': 'Global',
                'severity': 'medium'
            })

        # ── 8. IARC 内容分级（所有应用必须完成）──
        warnings.append({
            'policy': 'Google Play - IARC 内容分级',
            'issue': '所有应用必须完成 IARC 内容分级评估',
            'requirement': 'Google Play 要求所有应用完成 IARC（国际年龄分级联盟）问卷；'
                           '分级必须准确反映应用内容；错误分级将被 Google 强制更正或下架',
            'solution': '在 Play Console → 应用内容 → 内容分级 中完成 IARC 问卷；'
                        '如实填写暴力、色情、毒品、赌博等内容的存在情况；'
                        '儿童应用预期分级应为 ESRB E (Everyone) 或以下' if min_age < 13 else '根据实际内容选择适当分级',
            'region': 'Global',
            'severity': 'high'
        })

        # ── 9. 广告政策 ──
        if app_info.get('advertising_present'):
            warnings.append({
                'policy': 'Google Play 广告政策',
                'issue': '广告展示必须符合 Google Play 广告规范',
                'requirement': '① 插屏广告必须有明确可点击的关闭按钮（出现 5 秒内）；'
                               '② 广告不得模仿系统通知、下载提示或应用按钮；'
                               '③ 不得在游戏加载/过场动画中强制展示无法跳过的广告；'
                               '④ 广告不得遮挡应用核心功能',
                'solution': '使用 Google AdMob 并遵循其格式要求；实现插屏广告的关闭计时器；'
                            '在用户完成自然任务节点（关卡结束）后展示广告',
                'region': 'Global',
                'severity': 'high'
            })

        # ── 10. 用户生成内容审核（UGC）──
        if app_info.get('user_generated_content') or app_info.get('has_chat_messaging'):
            issues.append({
                'policy': 'Google Play - 用户生成内容（UGC）政策',
                'issue': '允许用户生成/分享内容的应用必须实现有效的内容审核机制',
                'requirement': '必须提供：① 举报/屏蔽不当内容的功能；'
                               '② 人工或自动审核机制；③ 针对违规用户的封禁系统；'
                               '④ 聊天功能需要防止骚扰、欺凌和不当接触（尤其涉及儿童）',
                'solution': '集成内容审核 API（Google Cloud Natural Language / Perspective API）；'
                            '实现用户举报流程；建立运营团队处理投诉；'
                            '儿童应用禁止开放式聊天功能',
                'region': 'Global',
                'severity': 'critical' if min_age < 18 else 'high'
            })

        # ── 11. 欺骗性行为 ──
        warnings.append({
            'policy': 'Google Play - 欺骗性行为和元数据政策',
            'issue': '应用描述、截图、图标必须准确反映实际功能',
            'requirement': '① 应用图标/截图不得展示应用内不存在的功能；'
                           '② 应用标题和描述不得包含误导性关键词；'
                           '③ 不得操控评分（刷好评、诱导评价）；'
                           '④ 不得在应用外展示误导性广告',
            'solution': '使用真实截图和实际游戏画面；'
                        '描述中清楚说明核心功能；不得在应用内弹出评分请求超过一次',
            'region': 'Global',
            'severity': 'medium'
        })

        # ── 12. Android App Bundle（推荐，部分场景强制）──
        if not app_info.get('uses_app_bundle'):
            warnings.append({
                'policy': 'Google Play - Android App Bundle',
                'issue': '建议使用 Android App Bundle 替代 APK 发布',
                'requirement': '2023 年起新应用强制使用 AAB 格式提交；'
                               'AAB 支持按需功能模块，可减少用户下载包体积',
                'solution': '在 Android Studio 中选择 Build → Generate Signed Bundle/APK → Android App Bundle；'
                            '旧 APK 方式仍可更新已有应用，但新应用必须用 AAB',
                'region': 'Global',
                'severity': 'high'
            })

        return {'issues': issues, 'warnings': warnings, 'passed': passed}
    
    def _check_app_store_compliance(self, app_info: Dict) -> Dict:
        """Apple App Store审核指南检查 (App Store Review Guidelines 2024)"""

        issues = []
        warnings = []
        passed = []

        platforms = app_info.get('target_platforms', [])
        is_ios = 'iOS' in platforms or not platforms  # 默认包含iOS检查

        if not is_ios:
            return {'issues': issues, 'warnings': warnings, 'passed': passed}

        min_age = app_info.get('min_user_age', 18)

        # ── 1. 应用内购买 (IAP) - Guideline 3.1 ──
        if app_info.get('has_in_app_purchases'):
            issues.append({
                'policy': 'App Store Review Guidelines 3.1.1 - IAP',
                'issue': '虚拟商品/数字内容必须使用 Apple In-App Purchase 系统',
                'requirement': '所有应用内数字商品（虚拟货币、解锁关卡、订阅等）必须通过 StoreKit；'
                               '不得引导用户使用外部支付渠道购买数字内容',
                'solution': '使用 StoreKit 2 (Swift) 或 StoreKit 1 (Objective-C) 实现 IAP；'
                            '实体商品和服务型应用可使用第三方支付',
                'region': 'Global',
                'severity': 'critical',
                'reference': 'https://developer.apple.com/app-store/review/guidelines/#payments'
            })

        # ── 2. 订阅披露要求 - Guideline 3.1.2 ──
        if app_info.get('subscription_model') or app_info.get('has_in_app_purchases'):
            warnings.append({
                'policy': 'App Store Review Guidelines 3.1.2 - 订阅披露',
                'issue': '自动续费订阅必须在购买前明确披露价格、周期和取消方式',
                'requirement': '必须在 paywall 页面清晰展示：订阅价格、计费频率、免费试用期限（如有）、'
                               '取消说明；不得在用户不知情的情况下扣款',
                'solution': '在订阅页面添加标准披露文本：自动续费说明、价格、管理订阅链接 '
                            '(Settings → Apple ID → Subscriptions)',
                'region': 'Global',
                'severity': 'high',
                'reference': 'https://developer.apple.com/app-store/review/guidelines/#subscriptions'
            })

        # ── 3. App 追踪透明度 (ATT) - iOS 14.5+ ──
        if (app_info.get('advertising_present') or
                app_info.get('uses_ai_algorithms') or
                app_info.get('data_sharing_third_parties')):
            issues.append({
                'policy': 'App Store - App Tracking Transparency (ATT) / iOS 14.5+',
                'issue': '跨 App 追踪用户行为必须通过 ATT 框架获得明确授权',
                'requirement': 'iOS 14.5 起，使用 IDFA 或跨应用追踪用户前必须弹出系统级权限请求；'
                               '未授权时不得追踪用户',
                'solution': '在 Info.plist 添加 NSUserTrackingUsageDescription；'
                            '调用 ATTrackingManager.requestTrackingAuthorization()；'
                            '仅在用户授权后使用 IDFA',
                'region': 'Global',
                'severity': 'critical',
                'reference': 'https://developer.apple.com/documentation/apptrackingtransparency'
            })
        else:
            passed.append('✅ ATT: 无跨应用追踪行为，无需 ATT 授权')

        # ── 4. 账户删除要求 (2022年6月起强制) - Guideline 5.1.1(v) ──
        if app_info.get('has_user_accounts', True):  # 默认假设有用户账户
            issues.append({
                'policy': 'App Store Review Guidelines 5.1.1(v) - 账户删除',
                'issue': '提供账户注册功能的应用必须允许用户在应用内删除账户',
                'requirement': '自 2022 年 6 月起，所有含账户功能的新应用和更新必须在应用内提供账户删除入口；'
                               '删除必须是完整的数据删除，不仅是停用',
                'solution': '在设置页面添加"删除账户"功能；实现完整的数据删除流程；'
                            '若有法律原因需保留数据，需向用户说明保留期限',
                'region': 'Global',
                'severity': 'critical',
                'reference': 'https://developer.apple.com/news/updates/2022-01-22.html'
            })

        # ── 5. Sign in with Apple - Guideline 4.8 ──
        if (app_info.get('has_social_features') or
                app_info.get('has_third_party_login')):
            issues.append({
                'policy': 'App Store Review Guidelines 4.8 - Sign in with Apple',
                'issue': '提供第三方登录（Google、Facebook 等）的应用必须同时提供 Sign in with Apple',
                'requirement': '当应用支持任何第三方或社交账号登录时，必须将 Sign in with Apple '
                               '作为同等选项提供给用户',
                'solution': '集成 AuthenticationServices 框架；在登录界面添加 ASAuthorizationAppleIDButton；'
                            '处理凭据状态变化 (revoked/transferred)',
                'region': 'Global',
                'severity': 'critical',
                'reference': 'https://developer.apple.com/app-store/review/guidelines/#sign-in-with-apple'
            })

        # ── 6. 隐私营养标签 (Privacy Nutrition Labels) ──
        data_collected = []
        if app_info.get('collects_educational_data'):
            data_collected.append('使用数据 (学习进度)')
        if app_info.get('cross_border_data_transfer'):
            data_collected.append('其他数据 (跨境传输)')
        if app_info.get('advertising_present'):
            data_collected.append('标识符 (广告追踪)')
        if app_info.get('uses_location_services'):
            data_collected.append('位置信息')
        if app_info.get('biometric_data'):
            data_collected.append('生物特征识别信息')

        if data_collected:
            issues.append({
                'policy': 'App Store Connect - 隐私营养标签',
                'issue': f'应用收集以下数据类别必须在 App Store 隐私标签中完整声明：{", ".join(data_collected)}',
                'requirement': 'Apple 要求在 App Store Connect 中准确填写所有数据收集类型、用途和'
                               '是否与用户身份关联；虚报或漏报将导致应用被拒',
                'solution': '登录 App Store Connect → App Information → App Privacy；'
                            '逐项声明数据类型（联系信息/位置/敏感信息等）、使用目的和关联方式；'
                            '更新隐私政策与标签内容保持一致',
                'region': 'Global',
                'severity': 'high',
                'reference': 'https://developer.apple.com/app-store/app-privacy-details/'
            })
        else:
            passed.append('✅ 隐私标签：无高风险数据收集')

        # ── 7. Kids Category 专项要求 (Guideline 1.3) ──
        if min_age < 13:
            # 7a. 禁止外部链接
            issues.append({
                'policy': 'App Store Review Guidelines 1.3 - Kids Category 外部链接',
                'issue': 'Kids Category 应用内不得包含指向 App Store 以外的外部链接、社交媒体或网站',
                'requirement': '所有外部链接（包括网站链接、客服邮箱、社交媒体）必须通过家长门控隐藏；'
                               '应用内浏览器必须限制为仅展示教育内容',
                'solution': '移除所有直接外部链接；如需保留，须通过 Parental Gate（家长门控）验证后才可访问',
                'region': 'Global',
                'severity': 'critical',
                'reference': 'https://developer.apple.com/app-store/review/guidelines/#kids'
            })

            # 7b. 禁止行为广告
            if app_info.get('advertising_present'):
                issues.append({
                    'policy': 'App Store Review Guidelines 1.3 - Kids Category 广告限制',
                    'issue': 'Kids Category 应用禁止展示行为广告或定向广告',
                    'requirement': '面向儿童的应用不得使用行为追踪数据投放广告；'
                                   '若展示广告，必须为上下文广告且内容适合儿童',
                    'solution': '移除所有行为广告 SDK；如需广告收入，使用支持 COPPA 合规的儿童安全广告网络，'
                                '如 AdMob Kids Ads (child_directed=true)',
                    'region': 'Global',
                    'severity': 'critical',
                    'reference': 'https://developer.apple.com/app-store/review/guidelines/#kids'
                })

            # 7c. Parental Gate 要求
            if (app_info.get('has_in_app_purchases') or
                    app_info.get('has_social_features') or
                    app_info.get('advertising_present')):
                issues.append({
                    'policy': 'App Store Review Guidelines 1.3 - Parental Gate',
                    'issue': 'Kids Category 应用在访问付费内容、外部链接或社交功能前必须实现 Parental Gate',
                    'requirement': 'Parental Gate 必须是家长能理解但儿童无法独立完成的验证（如数学题、'
                                   '认知验证），不能使用简单 PIN 码',
                    'solution': '实现符合 Apple 标准的 Parental Gate：展示仅成人能回答的随机数学题或'
                                '文字验证；通过后方可访问受控功能；每次会话需重新验证',
                    'region': 'Global',
                    'severity': 'critical',
                    'reference': 'https://developer.apple.com/app-store/review/guidelines/#kids'
                })

            # 7d. 第三方 SDK 限制
            if app_info.get('data_sharing_third_parties'):
                warnings.append({
                    'policy': 'App Store Review Guidelines 1.3 - Kids Category SDK 限制',
                    'issue': 'Kids Category 应用中的第三方 SDK 必须经 Apple 审核并符合儿童数据保护要求',
                    'requirement': '所有第三方 SDK 必须仅用于应用核心功能；禁止分析、崩溃报告以外的数据收集 SDK',
                    'solution': '审核所有第三方 SDK；移除不必要的分析/广告 SDK；'
                                '仅保留 Firebase Crashlytics 等核心工具，并确保其 COPPA 合规配置',
                    'region': 'Global',
                    'severity': 'high',
                    'reference': 'https://developer.apple.com/app-store/review/guidelines/#kids'
                })

        # ── 8. 内容分级 (Age Rating) ──
        if min_age < 4:
            warnings.append({
                'policy': 'App Store - 内容年龄分级',
                'issue': '应用年龄分级必须与实际内容和目标用户年龄一致',
                'requirement': 'App Store Connect 年龄分级必须准确填写；儿童应用最高分级通常为 4+；'
                               '不得通过低分级绕过 Kids Category 审核要求',
                'solution': '在 App Store Connect 中认真填写内容描述；如面向 4 岁以下儿童，选择 4+ 分级；'
                            '如含有暴力、恐怖等元素，必须如实申报',
                'region': 'Global',
                'severity': 'medium'
            })

        # ── 9. 应用完整性要求 - Guideline 2.1 ──
        warnings.append({
            'policy': 'App Store Review Guidelines 2.1 - 应用完整性',
            'issue': '提交审核前需确保应用功能完整、无明显 Bug 和崩溃',
            'requirement': 'Apple 要求提交的应用必须是完整可用的产品；演示版、Beta 版或功能残缺的应用会被拒绝；'
                           '所有宣传截图必须与实际功能一致',
            'solution': '提交前进行完整的 QA 测试；使用 TestFlight 进行 Beta 测试；'
                        '准备真实的演示账号供审核人员测试（如需登录）',
            'region': 'Global',
            'severity': 'medium'
        })

        return {'issues': issues, 'warnings': warnings, 'passed': passed}
    
    def _check_family_policies_compliance(self, app_info: Dict) -> Dict:
        """平台儿童应用政策检查"""
        
        issues = []
        warnings = []
        passed = []
        
        min_age = app_info.get('min_user_age', 0)
        
        # Google Play Family Policy
        if min_age < 13:
            # 行为广告检查
            if app_info.get('has_advertising'):
                warnings.append({
                    'policy': 'Google Play - 家庭政策',
                    'issue': '面向儿童的应用不得展示行为广告',
                    'requirement': 'Google Play禁止向13岁以下儿童展示个性化广告',
                    'solution': '在AdMob中设置child_directed_treatment=true，禁用个性化广告',
                    'region': 'Global',
                    'severity': 'high',
                    'technical_solution': 'AdMob配置: setChildDirectedTreatment(true)'
                })
            
            # 第三方SDK限制
            if app_info.get('shares_with_third_parties'):
                warnings.append({
                    'policy': 'Google Play - 家庭政策',
                    'issue': '儿童应用需要限制第三方SDK的使用',
                    'requirement': 'Google Play要求儿童应用禁用分析和跟踪功能',
                    'solution': '审核所有第三方SDK，禁用不必要的分析、跟踪和广告SDK',
                    'region': 'Global',
                    'severity': 'high'
                })
            
            # 社交功能限制
            if app_info.get('has_chat_social') or app_info.get('has_multiplayer'):
                warnings.append({
                    'policy': 'Google Play - 家庭政策',
                    'issue': '儿童应用的社交功能需要严格限制',
                    'requirement': 'Google Play限制儿童应用的社交网络和用户生成内容功能',
                    'solution': '移除或严格限制社交功能，实施内容审核和家长监督',
                    'region': 'Global',
                    'severity': 'high'
                })
            
            # Apple Kids Category要求 (如果适用)
            warnings.append({
                'policy': 'App Store - Kids Category',
                'issue': '儿童应用需要遵守Apple Kids Category指南',
                'requirement': 'Apple对儿童应用有严格的内容和功能要求',
                'solution': '确保应用内容教育性或娱乐性，移除外部链接，实施家长门控',
                'region': 'Global',
                'severity': 'medium'
            })
        
        return {'issues': issues, 'warnings': warnings, 'passed': passed}
    
    def _assess_platform_compliance_risk(self, app_info: Dict, issues: List, warnings: List) -> str:
        """评估平台合规风险等级"""
        
        critical_count = len([issue for issue in issues if issue.get('severity') == 'critical'])
        high_count = len([warning for warning in warnings if warning.get('severity') == 'high'])
        
        # 平台特有的高风险因素
        api_level_issue = any('Target API Level' in issue.get('policy', '') for issue in issues)
        children_app = app_info.get('min_user_age', 0) < 13
        
        if critical_count >= 2 or (api_level_issue and children_app):
            return 'critical'
        elif critical_count >= 1:
            return 'high'
        elif high_count >= 2 or (high_count >= 1 and children_app):
            return 'medium'
        else:
            return 'low'
    
    def _generate_platform_recommendations(self, app_info: Dict, issues: List, warnings: List) -> List[Dict]:
        """生成平台政策专业建议"""
        
        recommendations = []
        
        # API级别升级建议
        if any('Target API Level' in issue.get('policy', '') for issue in issues):
            recommendations.append({
                'category': 'Android技术合规升级',
                'priority': 'critical',
                'recommendation': '升级应用到最新Android API级别',
                'implementation': [
                    '更新targetSdkVersion到API 33+',
                    '测试应用在新API级别下的兼容性',
                    '适配新的权限模型和行为变更',
                    '更新第三方依赖库到兼容版本'
                ],
                'technical_steps': [
                    'android { compileSdkVersion 33; targetSdkVersion 33 }',
                    '测试运行时权限请求',
                    '检查网络安全配置',
                    '验证后台任务限制'
                ]
            })
        
        # 儿童应用平台优化
        if app_info.get('min_user_age', 0) < 13:
            recommendations.append({
                'category': '儿童应用平台政策优化',
                'priority': 'high',
                'recommendation': '全面优化儿童应用的平台合规性',
                'implementation': [
                    '配置AdMob儿童导向设置',
                    '移除或限制第三方分析SDK',
                    '实施家长门控功能',
                    '优化应用商店元数据和分类'
                ],
                'platform_specific': {
                    'google_play': [
                        '设置Target Audience为Children',
                        '禁用个性化广告',
                        '限制权限使用'
                    ],
                    'app_store': [
                        '申请Kids Category',
                        '配置隐私标签',
                        '实施家长门控'
                    ]
                }
            })
        
        # 隐私政策和权限透明度
        if (app_info.get('collects_location') or
                app_info.get('tracks_learning_progress')):
            recommendations.append({
                'category': '隐私透明度和权限管理',
                'priority': 'high',
                'recommendation': '建立透明的隐私和权限管理体系',
                'implementation': [
                    '制定详细的隐私政策',
                    '实施运行时权限最佳实践',
                    '配置应用商店隐私标签',
                    '建立用户数据控制功能'
                ]
            })

        # Apple App Store 专项合规建议
        platforms = app_info.get('target_platforms', [])
        if 'iOS' in platforms or not platforms:
            ios_actions = []

            if app_info.get('has_in_app_purchases'):
                ios_actions.append('迁移至 StoreKit 2 实现 IAP（支持更好的事务恢复和退款处理）')
            if app_info.get('advertising_present') or app_info.get('data_sharing_third_parties'):
                ios_actions.append('集成 ATT 框架，在适当时机请求追踪权限，授权率通常在 40-60%')
            ios_actions.append('在 App Store Connect 完整填写隐私营养标签（所有数据类型/用途/关联方式）')
            ios_actions.append('实现应用内账户删除功能（Settings → Delete Account），附带数据删除说明')

            if app_info.get('has_social_features') or app_info.get('has_third_party_login'):
                ios_actions.append('添加 Sign in with Apple 按钮（AuthenticationServices 框架）')

            if app_info.get('min_user_age', 18) < 13:
                ios_actions.extend([
                    '申请 Kids Category 分类，选择对应年龄段（5岁以下 / 6-8岁 / 9-11岁）',
                    '实现 Parental Gate（随机数学题验证），保护 IAP 和外部链接访问',
                    '移除 Kids Category 应用内所有行为广告和第三方追踪 SDK',
                    '删除所有未经家长门控的外部链接和社交媒体入口',
                ])

            if ios_actions:
                recommendations.append({
                    'category': 'Apple App Store 合规清单',
                    'priority': 'critical',
                    'recommendation': '完成 App Store Review Guidelines 关键合规项',
                    'implementation': ios_actions,
                    'reference': 'https://developer.apple.com/app-store/review/guidelines/'
                })

        return recommendations
    
    def get_cross_domain_insights(self, app_info: Dict, all_expert_results: Dict) -> List[Dict]:
        """提供跨专家领域的洞察"""
        
        insights = []
        
        # 平台政策 × 儿童保护协调
        children_result = all_expert_results.get('children_protection', {})
        if (app_info.get('min_user_age', 0) < 13 and children_result):
            
            insights.append({
                'title': '平台儿童应用政策与法规合规协调',
                'domains': ['platform_policies', 'children_protection'],
                'description': '平台的儿童应用政策通常比法律要求更严格，需要同时满足两方面要求',
                'recommendation': '采用最严格的标准：同时满足平台政策和儿童保护法规，优先考虑儿童安全和隐私保护'
            })
        
        # 平台政策 × 游戏法规
        gaming_result = all_expert_results.get('gaming_regulations', {})
        if (app_info.get('has_in_app_purchases') and gaming_result):
            
            insights.append({
                'title': '平台内购政策与游戏法规整合',
                'domains': ['platform_policies', 'gaming_regulations'],
                'description': '游戏内购买需要同时满足平台政策和各地区游戏法规要求',
                'recommendation': '建立统一的内购管理系统，既符合平台政策又满足地区游戏法规的充值限制'
            })
        
        return insights