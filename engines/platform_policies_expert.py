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
        """Google Play Store政策检查"""
        
        issues = []
        warnings = []
        passed = []
        
        # API级别检查
        target_sdk = app_info.get('target_sdk')
        if target_sdk:
            try:
                api_level = int(target_sdk)
                required_api = self.google_play_requirements['target_api_level']['new_apps']
                
                if api_level < required_api:
                    issues.append({
                        'policy': 'Google Play - Target API Level',
                        'issue': f'目标API级别 {api_level} 低于要求的 {required_api}',
                        'requirement': f'新应用必须使用API Level {required_api}+ (Android 13)',
                        'solution': f'在build.gradle中设置 targetSdkVersion {required_api} 或更高',
                        'region': 'Global',
                        'severity': 'critical'
                    })
                else:
                    passed.append(f'✅ Target API Level: {api_level} (符合要求)')
                    
            except ValueError:
                warnings.append({
                    'policy': 'Google Play - Target API Level',
                    'issue': 'API级别格式无效',
                    'requirement': 'API级别必须为有效数字',
                    'solution': '确认build.gradle中targetSdkVersion设置正确',
                    'region': 'Global',
                    'severity': 'medium'
                })
        else:
            warnings.append({
                'policy': 'Google Play - Target API Level',
                'issue': '未提供目标API级别信息',
                'requirement': '需要设置适当的目标API级别',
                'solution': '在build.gradle中设置targetSdkVersion',
                'region': 'Global',
                'severity': 'medium'
            })
        
        # 64位架构支持检查
        if app_info.get('has_native_code'):
            warnings.append({
                'policy': 'Google Play - 64位支持',
                'issue': '包含原生代码的应用需要支持64位架构',
                'requirement': 'Google Play要求支持64位架构 (arm64-v8a, x86_64)',
                'solution': '在build.gradle的ndk块中添加arm64-v8a和x86_64支持',
                'region': 'Global',
                'severity': 'high',
                'technical_solution': 'android { defaultConfig { ndk { abiFilters "arm64-v8a", "x86_64" } } }'
            })
        
        # 隐私政策检查
        requires_privacy_policy = (
            app_info.get('collects_location') or
            app_info.get('shares_with_third_parties') or
            app_info.get('has_advertising') or
            app_info.get('tracks_learning_progress') or
            app_info.get('cross_border_data')
        )
        
        if requires_privacy_policy:
            if not app_info.get('privacy_policy_url'):
                issues.append({
                    'policy': 'Google Play - 隐私政策',
                    'issue': '应用收集用户数据但未提供隐私政策',
                    'requirement': 'Google Play要求收集个人信息的应用提供隐私政策',
                    'solution': '创建详细的隐私政策并在Play Console中添加URL链接',
                    'region': 'Global',
                    'severity': 'critical'
                })
            else:
                passed.append('✅ 隐私政策: 已提供URL')
        
        # 权限使用检查
        sensitive_permissions = []
        if app_info.get('collects_location'):
            sensitive_permissions.append('位置权限')
        if app_info.get('collects_photos_videos'):
            sensitive_permissions.append('相机/存储权限')
        if app_info.get('collects_biometric'):
            sensitive_permissions.append('生物识别权限')
        
        if sensitive_permissions:
            app_type = app_info.get('app_type', '')
            if app_type not in ['Educational', 'Gaming']:  # 简化的逻辑
                warnings.append({
                    'policy': 'Google Play - 权限使用',
                    'issue': f'使用敏感权限: {", ".join(sensitive_permissions)}',
                    'requirement': '敏感权限的使用必须对应用核心功能必需',
                    'solution': '在权限请求时向用户清楚解释使用目的，确保权限使用的必要性',
                    'region': 'Global',
                    'severity': 'medium'
                })
        
        return {'issues': issues, 'warnings': warnings, 'passed': passed}
    
    def _check_app_store_compliance(self, app_info: Dict) -> Dict:
        """Apple App Store审核指南检查"""
        
        issues = []
        warnings = []
        passed = []
        
        # 基本的App Store指南检查
        if app_info.get('has_in_app_purchases'):
            warnings.append({
                'policy': 'App Store - 应用内购买',
                'issue': '应用内购买需要遵守Apple的IAP指南',
                'requirement': '虚拟商品必须通过Apple的IAP系统，实体商品可使用外部支付',
                'solution': '确认应用内购买类型，虚拟商品使用StoreKit，实体商品可使用第三方支付',
                'region': 'Global',
                'severity': 'medium'
            })
        
        # App Store隐私标签
        if (app_info.get('collects_location') or 
            app_info.get('tracks_learning_progress') or
            app_info.get('has_advertising')):
            warnings.append({
                'policy': 'App Store - 隐私标签',
                'issue': '需要在App Store中配置隐私标签',
                'requirement': 'Apple要求详细说明数据收集和使用情况',
                'solution': '在App Store Connect中准确填写隐私标签，说明所有数据收集类型',
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