#!/usr/bin/env python3
"""
儿童保护专家 (Children Protection Expert)

专精领域:
- COPPA (美国儿童在线隐私保护法)
- GDPR 儿童条款 (欧盟)
- PIPL 未成年人保护 (中国)
- 英国儿童设计准则
- 各国儿童保护法规

这是教育游戏应用最关键的合规专家
"""

from typing import Dict, List
from datetime import datetime

class ChildrenProtectionExpert:
    """儿童保护法规专家"""
    
    def __init__(self):
        self.name = "儿童保护专家"
        self.expertise_areas = [
            'COPPA', 'GDPR_Children', 'PIPL_Minors',  
            'UK_Children_Code', 'Age_Verification', 'Parental_Consent'
        ]
        
        # 各地区儿童保护年龄阈值
        self.age_thresholds = {
            'US': {'coppa': 13, 'teen': 13, 'adult': 18},
            'EU': {'gdpr_consent': 16, 'teen': 16, 'adult': 18},
            'UK': {'children_code': 18, 'teen': 13, 'adult': 18},
            'China': {'pipl_minor': 14, 'teen': 14, 'adult': 18},
            'Korea': {'youth_protection': 16, 'adult': 19},
            'Japan': {'minor_protection': 20}  # 日本成年年龄为20岁
        }
        
        # 严重违规模式识别
        self.critical_violation_patterns = [
            'coppa_no_parental_consent',
            'gdpr_no_child_consent_mechanism', 
            'china_no_guardian_authorization',
            'behavioral_advertising_to_children',
            'sensitive_data_from_children',
            'social_features_unmoderated'
        ]
    
    def analyze_compliance(self, app_info: Dict, context: Dict = None) -> Dict:
        """分析儿童保护合规性"""
        
        min_age = app_info.get('min_user_age', 0)
        target_markets = app_info.get('target_markets', [])
        
        # 如果不涉及儿童，快速通过
        if min_age >= 18:
            return {
                'status': 'not_applicable',
                'reason': '应用仅面向成人用户',
                'issues': [],
                'warnings': [],
                'passed': ['✅ 不适用儿童保护法规 - 仅成人用户']
            }
        
        print(f"    🔍 {self.name}分析中... (涉及{18-min_age}岁年龄段的儿童保护)")
        
        issues = []
        warnings = []
        passed = []
        
        # 按地区执行专项检查
        for market in target_markets:
            market_results = self._check_regional_compliance(app_info, market)
            issues.extend(market_results['issues'])
            warnings.extend(market_results['warnings']) 
            passed.extend(market_results['passed'])
        
        # 跨地区通用检查
        universal_results = self._check_universal_child_protection(app_info)
        issues.extend(universal_results['issues'])
        warnings.extend(universal_results['warnings'])
        passed.extend(universal_results['passed'])
        
        # 生成风险评级
        risk_level = self._assess_child_protection_risk(app_info, issues, warnings)
        
        return {
            'expert': self.name,
            'risk_level': risk_level,
            'issues': issues,
            'warnings': warnings,
            'passed': passed,
            'specialized_recommendations': self._generate_child_protection_recommendations(app_info, issues, warnings)
        }
    
    def _check_regional_compliance(self, app_info: Dict, region: str) -> Dict:
        """检查特定地区的儿童保护合规性"""
        
        min_age = app_info.get('min_user_age', 0)
        issues = []
        warnings = []
        passed = []
        
        if region == 'US':
            # COPPA专项检查
            coppa_results = self._check_coppa_compliance(app_info)
            issues.extend(coppa_results['issues'])
            warnings.extend(coppa_results['warnings'])
            passed.extend(coppa_results['passed'])
            
        elif region == 'EU':
            # GDPR儿童条款检查
            gdpr_results = self._check_gdpr_children_compliance(app_info)
            issues.extend(gdpr_results['issues'])
            warnings.extend(gdpr_results['warnings'])
            passed.extend(gdpr_results['passed'])
            
        elif region == 'UK':
            # 英国儿童设计准则
            uk_results = self._check_uk_children_code(app_info)
            issues.extend(uk_results['issues'])
            warnings.extend(uk_results['warnings'])
            passed.extend(uk_results['passed'])
            
        elif region == 'China':
            # 中国未成年人保护
            china_results = self._check_china_minor_protection(app_info)
            issues.extend(china_results['issues'])
            warnings.extend(china_results['warnings'])
            passed.extend(china_results['passed'])
        
        return {'issues': issues, 'warnings': warnings, 'passed': passed}
    
    def _check_coppa_compliance(self, app_info: Dict) -> Dict:
        """COPPA专项合规检查 - 美国13岁以下儿童保护"""
        
        min_age = app_info.get('min_user_age', 0)
        issues = []
        warnings = []
        passed = []
        
        if min_age >= 13:
            passed.append('✅ COPPA: 不涉及13岁以下儿童')
            return {'issues': issues, 'warnings': warnings, 'passed': passed}
        
        # 严重违规检查
        if not app_info.get('has_parental_controls'):
            issues.append({
                'law': 'COPPA',
                'issue': '13岁以下儿童应用缺少可验证的家长同意机制',
                'requirement': 'COPPA要求13岁以下儿童数据收集需要可验证的家长同意',
                'solution': '实现以下家长同意方法之一: 信用卡预授权验证、数字签名、邮件+电话双重验证、视频通话确认',
                'region': 'US',
                'severity': 'critical',
                'law_reference': 'COPPA Section 312.5',
                'max_fine': '$43,792 per violation'
            })
        
        if not app_info.get('has_age_verification'):
            issues.append({
                'law': 'COPPA',
                'issue': '缺少年龄验证机制无法识别13岁以下儿童',
                'requirement': '必须可靠识别13岁以下用户并触发COPPA保护措施',
                'solution': '实现多层年龄验证: 生日输入 + 行为分析 + 家长确认',
                'region': 'US', 
                'severity': 'critical'
            })
        
        # 数据收集限制检查
        prohibited_data_collection = []
        if app_info.get('collects_location'):
            prohibited_data_collection.append('地理位置信息')
        if app_info.get('collects_biometric'):
            prohibited_data_collection.append('生物识别数据')
        if app_info.get('collects_photos_videos'):
            prohibited_data_collection.append('照片和视频')
        
        if prohibited_data_collection:
            warnings.append({
                'law': 'COPPA - 数据最小化',
                'issue': f'儿童应用收集敏感数据: {", ".join(prohibited_data_collection)}',
                'requirement': 'COPPA要求最小化儿童个人信息收集',
                'solution': '评估数据收集必要性，仅收集应用核心功能必需的信息',
                'region': 'US',
                'severity': 'high'
            })
        
        # 广告和商业化检查
        if app_info.get('has_advertising'):
            warnings.append({
                'law': 'COPPA - 广告限制',
                'issue': '13岁以下儿童应用展示广告',
                'requirement': '禁止向13岁以下儿童展示行为广告',
                'solution': '配置AdMob儿童导向设置(child_directed_treatment=true)，禁用个性化广告和用户跟踪',
                'region': 'US',
                'severity': 'high',
                'technical_solution': 'AdMob SDK配置: requestConfiguration.setChildDirectedTreatment(true)'
            })
        
        # 社交功能风险
        if app_info.get('has_chat_social') or app_info.get('has_multiplayer'):
            warnings.append({
                'law': 'COPPA - 社交互动限制',
                'issue': '儿童应用包含社交互动功能存在隐私泄露风险',
                'requirement': '限制儿童与陌生人交流，防止个人信息泄露',
                'solution': '实现严格内容审核、预设回复选项、禁止自由文本输入、家长监督功能',
                'region': 'US',
                'severity': 'high'
            })
        
        if app_info.get('has_parental_controls') and app_info.get('has_age_verification'):
            passed.append('✅ COPPA: 已实现基础年龄验证和家长控制框架')
        
        return {'issues': issues, 'warnings': warnings, 'passed': passed}
    
    def _check_gdpr_children_compliance(self, app_info: Dict) -> Dict:
        """GDPR儿童条款检查 - 欧盟16岁以下保护"""
        
        min_age = app_info.get('min_user_age', 0)
        issues = []
        warnings = []
        passed = []
        
        if min_age >= 16:
            passed.append('✅ GDPR儿童条款: 不涉及16岁以下儿童')
            return {'issues': issues, 'warnings': warnings, 'passed': passed}
        
        # GDPR儿童同意机制
        if not app_info.get('has_parental_controls'):
            issues.append({
                'law': 'GDPR Article 8',
                'issue': '16岁以下儿童数据处理缺少家长同意机制',
                'requirement': 'GDPR第8条要求16岁以下儿童数据处理需获得家长/监护人同意',
                'solution': '实现符合GDPR的家长同意机制，包括同意撤回功能和数据主体权利实现',
                'region': 'EU',
                'severity': 'critical',
                'max_fine': '4% of global revenue or €20 million'
            })
        
        # 数据保护设计原则
        if (app_info.get('has_advertising') or 
            app_info.get('collects_location') or 
            app_info.get('shares_with_third_parties')):
            warnings.append({
                'law': 'GDPR - Privacy by Design',
                'issue': '儿童应用未实现默认隐私保护设计',
                'requirement': 'GDPR要求儿童应用实施Privacy by Design和Privacy by Default',
                'solution': '默认最高隐私设置：禁用定位、禁用个性化广告、最小化数据共享',
                'region': 'EU',
                'severity': 'high'
            })
        
        return {'issues': issues, 'warnings': warnings, 'passed': passed}
    
    def _check_uk_children_code(self, app_info: Dict) -> Dict:
        """英国儿童设计准则检查 - 18岁以下特殊保护"""
        
        min_age = app_info.get('min_user_age', 0)
        issues = []
        warnings = []
        passed = []
        
        if min_age >= 18:
            passed.append('✅ UK儿童设计准则: 不涉及18岁以下用户')
            return {'issues': issues, 'warnings': warnings, 'passed': passed}
        
        # 年龄适宜设计评估
        age_inappropriate_features = []
        if app_info.get('has_time_pressure'):
            age_inappropriate_features.append('时间压力/紧迫感设计')
        if app_info.get('has_random_rewards'):
            age_inappropriate_features.append('随机奖励机制')
        
        if age_inappropriate_features:
            warnings.append({
                'law': 'UK Age Appropriate Design Code',
                'issue': f'检测到可能不适合儿童的设计: {", ".join(age_inappropriate_features)}',
                'requirement': '英国儿童设计准则要求避免可能有害儿童的设计模式',
                'solution': '评估并修改可能导致儿童过度使用或成瘾的设计元素',
                'region': 'UK',
                'severity': 'medium'
            })
        
        return {'issues': issues, 'warnings': warnings, 'passed': passed}
    
    def _check_china_minor_protection(self, app_info: Dict) -> Dict:
        """中国未成年人保护检查"""
        
        min_age = app_info.get('min_user_age', 0)
        issues = []
        warnings = []
        passed = []
        
        if min_age >= 18:
            passed.append('✅ 中国未成年人保护: 不涉及未成年人')
            return {'issues': issues, 'warnings': warnings, 'passed': passed}
        
        # 14岁以下敏感个人信息检查
        if min_age < 14:
            sensitive_data_types = []
            if app_info.get('collects_biometric'):
                sensitive_data_types.append('生物识别信息')
            if app_info.get('tracks_learning_progress'):
                sensitive_data_types.append('学习行为数据')
            
            if sensitive_data_types:
                warnings.append({
                    'law': 'PIPL - 未成年人保护',
                    'issue': f'收集14岁以下儿童敏感个人信息: {", ".join(sensitive_data_types)}',
                    'requirement': 'PIPL要求处理敏感个人信息需具有特定目的和充分必要性，取得个人单独同意',
                    'solution': '实现敏感信息单独同意机制，采取严格的技术和管理保护措施',
                    'region': 'China',
                    'severity': 'high'
                })
        
        return {'issues': issues, 'warnings': warnings, 'passed': passed}
    
    def _check_universal_child_protection(self, app_info: Dict) -> Dict:
        """通用儿童保护最佳实践检查"""
        
        issues = []
        warnings = []
        passed = []
        
        # 家长控制功能完整性检查
        if app_info.get('has_parental_controls'):
            # 检查家长控制功能的完整性
            missing_parental_features = []
            
            # 基于应用功能推断需要的家长控制
            if app_info.get('has_in_app_purchases') and not app_info.get('purchase_limits'):
                missing_parental_features.append('购买限制和审批')
            if app_info.get('has_chat_social') and not app_info.get('social_controls'):
                missing_parental_features.append('社交功能开关')
            if app_info.get('tracks_learning_progress') and not app_info.get('data_access_controls'):
                missing_parental_features.append('学习数据查看权限')
            
            if missing_parental_features:
                warnings.append({
                    'law': '儿童保护最佳实践',
                    'issue': f'家长控制功能不完整，缺少: {", ".join(missing_parental_features)}',
                    'requirement': '全面的家长控制应包含所有可能影响儿童的功能管理',
                    'solution': '完善家长控制面板，提供细粒度的功能开关和监督工具',
                    'region': 'Universal',
                    'severity': 'medium'
                })
            else:
                passed.append('✅ 家长控制: 功能较为完整')
        
        # 年龄验证可靠性评估
        if app_info.get('has_age_verification'):
            # 简单的年龄验证可能不够可靠
            if app_info.get('min_user_age', 0) < 13:
                warnings.append({
                    'law': '年龄验证最佳实践',
                    'issue': '13岁以下儿童的年龄验证需要更高可靠性',
                    'requirement': '准确识别儿童用户对于合规至关重要',
                    'solution': '考虑多层验证: 生日+行为分析+家长确认+设备指纹',
                    'region': 'Universal',
                    'severity': 'medium'
                })
            else:
                passed.append('✅ 年龄验证: 基础功能已实现')
        
        return {'issues': issues, 'warnings': warnings, 'passed': passed}
    
    def _assess_child_protection_risk(self, app_info: Dict, issues: List, warnings: List) -> str:
        """评估儿童保护风险等级"""
        
        critical_count = len([issue for issue in issues if issue.get('severity') == 'critical'])
        high_count = len([warning for warning in warnings if warning.get('severity') == 'high'])
        
        min_age = app_info.get('min_user_age', 0)
        has_sensitive_features = (app_info.get('has_chat_social') or 
                                 app_info.get('collects_biometric') or
                                 app_info.get('cross_border_data'))
        
        if critical_count >= 2:
            return 'critical'
        elif critical_count >= 1 and has_sensitive_features:
            return 'very_high'
        elif critical_count >= 1 or high_count >= 3:
            return 'high'
        elif high_count >= 1 or (min_age < 13 and not app_info.get('has_parental_controls')):
            return 'medium'
        else:
            return 'low'
    
    def _generate_child_protection_recommendations(self, app_info: Dict, issues: List, warnings: List) -> List[Dict]:
        """生成儿童保护专业建议"""
        
        recommendations = []
        
        min_age = app_info.get('min_user_age', 0)
        
        # 基于年龄段的建议
        if min_age < 13:
            recommendations.append({
                'category': 'COPPA合规框架',
                'priority': 'critical',
                'recommendation': '建立完整的COPPA合规框架：可验证家长同意 + 数据最小化 + 安全删除机制',
                'implementation': [
                    '设计多种家长同意验证方法',
                    '实现儿童数据的自动识别和隔离',
                    '建立家长数据管理dashboard',
                    '实施定期合规审计'
                ]
            })
        
        if 13 <= min_age < 16:
            recommendations.append({
                'category': '青少年保护增强',
                'priority': 'high',
                'recommendation': '实施青少年特殊保护措施，平衡隐私保护和功能可用性',
                'implementation': [
                    '设计年龄分层的隐私设置',
                    '实现渐进式功能解锁',
                    '提供青少年隐私教育内容'
                ]
            })
        
        # 基于功能特性的建议
        if app_info.get('has_chat_social'):
            recommendations.append({
                'category': '社交安全设计',
                'priority': 'high', 
                'recommendation': '实现全面的社交安全保护机制',
                'implementation': [
                    '实时内容审核和过滤',
                    '预设安全回复选项',
                    '陌生人交流限制',
                    '不当内容举报系统',
                    '家长监督和通知'
                ]
            })
        
        if app_info.get('collects_biometric') or app_info.get('tracks_learning_progress'):
            recommendations.append({
                'category': '敏感数据保护',
                'priority': 'high',
                'recommendation': '建立敏感儿童数据的特殊保护体系',
                'implementation': [
                    '实施数据加密和访问控制',
                    '建立数据保留期限管理',
                    '提供数据导出和删除功能',
                    '定期数据安全审计'
                ]
            })
        
        return recommendations
    
    def get_cross_domain_insights(self, app_info: Dict, all_expert_results: Dict) -> List[Dict]:
        """提供跨专家领域的洞察"""
        
        insights = []
        
        # 如果游戏专家检测到内购功能 + 儿童用户
        gaming_result = all_expert_results.get('gaming_regulations', {})
        if (app_info.get('has_in_app_purchases') and 
            app_info.get('min_user_age', 0) < 18 and
            gaming_result):
            
            insights.append({
                'title': '儿童保护 × 游戏内购合规交叉风险',
                'domains': ['children_protection', 'gaming_regulations'],
                'description': '检测到儿童用户 + 游戏内购组合，需要同时满足儿童保护法规和游戏监管要求',
                'recommendation': '实施家长授权购买机制，设置年龄分层的消费限制，建立退款和争议处理流程'
            })
        
        # 如果教育专家检测到学校集成 + 儿童数据
        education_result = all_expert_results.get('education_compliance', {})
        if (app_info.get('integrates_with_schools') and 
            app_info.get('min_user_age', 0) < 18 and
            education_result):
            
            insights.append({
                'title': '儿童保护 × 教育数据合规协调',
                'domains': ['children_protection', 'education_compliance'],
                'description': '学校教育环境中的儿童数据处理涉及COPPA、FERPA等多重法规交叉',
                'recommendation': '建立学校-家长双重同意机制，明确教育记录和个人信息的界限和处理方式'
            })
        
        return insights