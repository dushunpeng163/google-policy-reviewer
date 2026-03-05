#!/usr/bin/env python3
"""
隐私法律专家 (Privacy Laws Expert)

专精领域:
- 全球数据保护法律 (GDPR、PIPL、CCPA等)
- 跨境数据传输合规
- 数据主体权利实现
- 隐私政策和同意管理
- 数据保留和删除要求
"""

from typing import Dict, List
from datetime import datetime

class PrivacyLawsExpert:
    """隐私法律专业专家"""
    
    def __init__(self):
        self.name = "隐私法律专家"
        self.expertise_areas = [
            'GDPR', 'PIPL', 'CCPA', 'PIPEDA', 'LGPD',
            'Cross_Border_Data_Transfer', 'Data_Subject_Rights',
            'Consent_Management', 'Data_Retention_Policies'
        ]
        
        # 全球主要隐私法律
        self.privacy_laws = {
            'GDPR': {
                'region': 'EU',
                'scope': 'comprehensive',
                'max_fine': '4% of global revenue or €20 million',
                'key_principles': ['lawfulness', 'purpose_limitation', 'data_minimization', 'accuracy', 'storage_limitation', 'integrity_confidentiality'],
                'data_subject_rights': ['access', 'rectification', 'erasure', 'restrict_processing', 'data_portability', 'object']
            },
            'PIPL': {
                'region': 'China',
                'scope': 'comprehensive',
                'max_fine': '5% of revenue or 50 million RMB',
                'key_principles': ['lawfulness', 'legitimacy', 'necessity', 'good_faith'],
                'cross_border_restrictions': True,
                'sensitive_data_protection': True
            },
            'CCPA': {
                'region': 'California',
                'scope': 'consumer_rights',
                'max_fine': '$7,500 per violation',
                'consumer_rights': ['know', 'delete', 'opt_out', 'non_discrimination']
            },
            'LGPD': {
                'region': 'Brazil',
                'scope': 'comprehensive',
                'max_fine': '2% of revenue up to 50 million BRL',
                'similar_to': 'GDPR'
            }
        }
        
        # 跨境数据传输机制
        self.data_transfer_mechanisms = {
            'adequacy_decisions': ['Andorra', 'Argentina', 'Canada', 'Faroe Islands', 'Guernsey', 'Isle of Man', 'Israel', 'Japan', 'Jersey', 'New Zealand', 'Switzerland', 'South Korea', 'UK', 'Uruguay'],
            'standard_contractual_clauses': True,
            'binding_corporate_rules': True,
            'certification_schemes': True
        }
    
    def analyze_compliance(self, app_info: Dict, context: Dict = None) -> Dict:
        """分析隐私法律合规性"""
        
        # 检测数据处理活动
        data_processing = self._detect_data_processing_activities(app_info)
        
        if not data_processing:
            return {
                'status': 'minimal_risk',
                'reason': '应用数据处理活动较少，隐私法律风险较低',
                'issues': [],
                'warnings': [],
                'passed': ['✅ 数据处理风险较低']
            }
        
        print(f"    🔒 {self.name}分析中... (检测到{len(data_processing)}类数据处理)")
        
        target_markets = app_info.get('target_markets', [])
        
        issues = []
        warnings = []
        passed = []
        
        # 按地区执行隐私法律检查
        for market in target_markets:
            market_results = self._check_regional_privacy_compliance(app_info, market)
            issues.extend(market_results['issues'])
            warnings.extend(market_results['warnings'])
            passed.extend(market_results['passed'])
        
        # 跨境数据传输检查
        if app_info.get('cross_border_data') and len(target_markets) > 1:
            transfer_results = self._check_cross_border_compliance(app_info, target_markets)
            issues.extend(transfer_results['issues'])
            warnings.extend(transfer_results['warnings'])
            passed.extend(transfer_results['passed'])
        
        # 通用数据保护最佳实践
        universal_results = self._check_universal_privacy_practices(app_info)
        issues.extend(universal_results['issues'])
        warnings.extend(universal_results['warnings'])
        passed.extend(universal_results['passed'])
        
        risk_level = self._assess_privacy_compliance_risk(app_info, issues, warnings)
        
        return {
            'expert': self.name,
            'risk_level': risk_level,
            'detected_data_processing': data_processing,
            'issues': issues,
            'warnings': warnings,
            'passed': passed,
            'specialized_recommendations': self._generate_privacy_recommendations(app_info, issues, warnings)
        }
    
    def _detect_data_processing_activities(self, app_info: Dict) -> List[str]:
        """检测数据处理活动"""
        
        activities = []
        
        if app_info.get('collects_location'):
            activities.append('location_data_processing')
        if app_info.get('collects_biometric'):
            activities.append('biometric_data_processing')
        if app_info.get('tracks_learning_progress'):
            activities.append('learning_analytics')
        if app_info.get('collects_photos_videos'):
            activities.append('media_content_processing')
        if app_info.get('has_advertising'):
            activities.append('advertising_data_processing')
        if app_info.get('shares_with_third_parties'):
            activities.append('third_party_data_sharing')
        if app_info.get('cross_border_data'):
            activities.append('international_data_transfer')
        if app_info.get('has_chat_social'):
            activities.append('communication_data_processing')
        
        return activities
    
    def _check_regional_privacy_compliance(self, app_info: Dict, region: str) -> Dict:
        """检查特定地区的隐私法律合规性"""
        
        issues = []
        warnings = []
        passed = []
        
        if region == 'EU':
            gdpr_results = self._check_gdpr_compliance(app_info)
            issues.extend(gdpr_results['issues'])
            warnings.extend(gdpr_results['warnings'])
            passed.extend(gdpr_results['passed'])
            
        elif region == 'China':
            pipl_results = self._check_pipl_compliance(app_info)
            issues.extend(pipl_results['issues'])
            warnings.extend(pipl_results['warnings'])
            passed.extend(pipl_results['passed'])
            
        elif region == 'US':
            ccpa_results = self._check_ccpa_compliance(app_info)
            issues.extend(ccpa_results['issues'])
            warnings.extend(ccpa_results['warnings'])
            passed.extend(ccpa_results['passed'])
        
        return {'issues': issues, 'warnings': warnings, 'passed': passed}
    
    def _check_gdpr_compliance(self, app_info: Dict) -> Dict:
        """GDPR合规专项检查"""
        
        issues = []
        warnings = []
        passed = []
        
        # 合法依据检查
        has_significant_processing = (
            app_info.get('tracks_learning_progress') or
            app_info.get('collects_biometric') or
            app_info.get('shares_with_third_parties')
        )
        
        if has_significant_processing and not app_info.get('privacy_policy_url'):
            issues.append({
                'law': 'GDPR Article 13/14',
                'issue': '缺少GDPR要求的详细隐私信息',
                'requirement': 'GDPR要求详细说明个人数据处理的合法依据、目的、期限等',
                'solution': '制定符合GDPR的隐私政策，包含所有第13/14条要求的信息',
                'region': 'EU',
                'severity': 'critical'
            })
        
        # 数据主体权利实现
        if has_significant_processing:
            warnings.append({
                'law': 'GDPR Chapter III',
                'issue': '需要实现GDPR规定的数据主体权利',
                'requirement': 'GDPR赋予数据主体访问、更正、删除、限制处理、数据携带等权利',
                'solution': '开发用户数据管理功能：查看个人数据、修改信息、删除账号、导出数据',
                'region': 'EU',
                'severity': 'high'
            })
        
        # 敏感数据处理
        if app_info.get('collects_biometric') or app_info.get('min_user_age', 0) < 16:
            warnings.append({
                'law': 'GDPR Article 9 (Special Categories)',
                'issue': '处理敏感个人数据需要额外保护措施',
                'requirement': 'GDPR对敏感数据有更严格的处理要求',
                'solution': '确保有明确的法律依据，实施额外的技术和组织保护措施',
                'region': 'EU',
                'severity': 'high'
            })
        
        # 数据保护影响评估 (DPIA)
        if (app_info.get('collects_biometric') and 
            app_info.get('cross_border_data') and
            app_info.get('min_user_age', 0) < 16):
            warnings.append({
                'law': 'GDPR Article 35 (DPIA)',
                'issue': '高风险数据处理可能需要进行数据保护影响评估',
                'requirement': 'GDPR要求对高风险处理进行DPIA评估',
                'solution': '进行DPIA评估：识别风险、评估影响、制定缓解措施',
                'region': 'EU',
                'severity': 'medium'
            })
        
        return {'issues': issues, 'warnings': warnings, 'passed': passed}
    
    def _check_pipl_compliance(self, app_info: Dict) -> Dict:
        """PIPL合规专项检查"""
        
        issues = []
        warnings = []
        passed = []
        
        # 个人信息出境检查
        if app_info.get('cross_border_data'):
            issues.append({
                'law': 'PIPL 第38-42条',
                'issue': '个人信息出境需要符合PIPL规定',
                'requirement': 'PIPL要求个人信息出境通过安全评估、认证或标准合同',
                'solution': '申请个人信息保护认证或通过网信办安全评估，建立跨境传输保护措施',
                'region': 'China',
                'severity': 'critical'
            })
        
        # 敏感个人信息处理
        if (app_info.get('collects_biometric') or 
            app_info.get('min_user_age', 0) < 14):
            warnings.append({
                'law': 'PIPL 第28条',
                'issue': '敏感个人信息处理需要特殊保护',
                'requirement': 'PIPL要求处理敏感个人信息具有特定目的和充分必要性',
                'solution': '实现敏感信息单独同意机制，采取严格的技术保护措施',
                'region': 'China', 
                'severity': 'high'
            })
        
        # 个人信息处理规则
        if (app_info.get('tracks_learning_progress') or 
            app_info.get('shares_with_third_parties')):
            warnings.append({
                'law': 'PIPL 第17条',
                'issue': '需要制定个人信息处理规则',
                'requirement': 'PIPL要求个人信息处理者制定内部管理制度和操作规程',
                'solution': '建立个人信息处理内部规则，指定个人信息保护负责人',
                'region': 'China',
                'severity': 'medium'
            })
        
        return {'issues': issues, 'warnings': warnings, 'passed': passed}
    
    def _check_ccpa_compliance(self, app_info: Dict) -> Dict:
        """CCPA合规检查"""
        
        issues = []
        warnings = []
        passed = []
        
        # 仅当涉及加州消费者时适用
        if (app_info.get('shares_with_third_parties') or 
            app_info.get('has_advertising')):
            warnings.append({
                'law': 'CCPA',
                'issue': '可能需要提供CCPA要求的消费者权利',
                'requirement': 'CCPA赋予加州消费者了解、删除、选择退出个人信息销售的权利',
                'solution': '如面向加州用户，需提供：隐私政策更新、用户权利请求处理、选择退出机制',
                'region': 'US (California)',
                'severity': 'medium'
            })
        
        return {'issues': issues, 'warnings': warnings, 'passed': passed}
    
    def _check_cross_border_compliance(self, app_info: Dict, target_markets: List[str]) -> Dict:
        """跨境数据传输合规检查"""
        
        issues = []
        warnings = []
        passed = []
        
        # 高风险跨境组合检查
        involves_china = 'China' in target_markets
        involves_eu = 'EU' in target_markets
        
        if involves_china and involves_eu:
            warnings.append({
                'law': '中欧跨境数据传输',
                'issue': '中国-欧盟跨境数据传输需要同时满足PIPL和GDPR要求',
                'requirement': '需要满足最严格的数据保护要求',
                'solution': '建立数据本地化存储策略，或通过官方认可的跨境传输机制',
                'region': 'China-EU',
                'severity': 'high'
            })
        
        if involves_china and len(target_markets) > 1:
            warnings.append({
                'law': 'PIPL 跨境传输',
                'issue': '从中国向境外传输个人信息需要合规评估',
                'requirement': 'PIPL要求个人信息出境进行安全评估',
                'solution': '评估是否需要通过网信办安全评估或获得个人信息保护认证',
                'region': 'China',
                'severity': 'high'
            })
        
        if involves_eu and len(target_markets) > 1:
            warnings.append({
                'law': 'GDPR 第五章',
                'issue': '从欧盟向第三国传输个人数据需要适当保障措施',
                'requirement': 'GDPR要求国际传输有充足性决定或适当保障措施',
                'solution': '使用标准合同条款(SCCs)或确保传输到充足性决定国家',
                'region': 'EU',
                'severity': 'medium'
            })
        
        return {'issues': issues, 'warnings': warnings, 'passed': passed}
    
    def _check_universal_privacy_practices(self, app_info: Dict) -> Dict:
        """通用隐私保护最佳实践"""
        
        issues = []
        warnings = []
        passed = []
        
        # 数据最小化检查
        data_types = []
        if app_info.get('collects_location'):
            data_types.append('位置数据')
        if app_info.get('collects_biometric'):
            data_types.append('生物识别数据')
        if app_info.get('collects_photos_videos'):
            data_types.append('媒体文件')
        
        if len(data_types) >= 3:
            warnings.append({
                'law': '数据最小化原则',
                'issue': f'收集多种类型的个人数据: {", ".join(data_types)}',
                'requirement': '隐私保护最佳实践要求最小化数据收集',
                'solution': '评估每种数据类型的必要性，仅收集应用核心功能必需的数据',
                'region': 'Universal',
                'severity': 'low'
            })
        
        # 数据保留政策
        if (app_info.get('tracks_learning_progress') or 
            app_info.get('collects_biometric')):
            warnings.append({
                'law': '数据保留最佳实践',
                'issue': '建议建立明确的数据保留和删除政策',
                'requirement': '制定数据保留期限和自动删除机制',
                'solution': '建立数据生命周期管理：定期清理、用户删除请求、账号注销处理',
                'region': 'Universal',
                'severity': 'low'
            })
        
        return {'issues': issues, 'warnings': warnings, 'passed': passed}
    
    def _assess_privacy_compliance_risk(self, app_info: Dict, issues: List, warnings: List) -> str:
        """评估隐私合规风险等级"""
        
        critical_count = len([issue for issue in issues if issue.get('severity') == 'critical'])
        high_count = len([warning for warning in warnings if warning.get('severity') == 'high'])
        
        # 高风险数据组合
        sensitive_data = (app_info.get('collects_biometric') or 
                         app_info.get('min_user_age', 0) < 16)
        cross_border = app_info.get('cross_border_data', False)
        china_market = 'China' in app_info.get('target_markets', [])
        
        if critical_count >= 1 and (china_market or cross_border):
            return 'critical'
        elif critical_count >= 1 or (high_count >= 2 and sensitive_data):
            return 'high'
        elif high_count >= 1 or (sensitive_data and cross_border):
            return 'medium'
        else:
            return 'low'
    
    def _generate_privacy_recommendations(self, app_info: Dict, issues: List, warnings: List) -> List[Dict]:
        """生成隐私法律专业建议"""
        
        recommendations = []
        
        target_markets = app_info.get('target_markets', [])
        
        # 跨境数据传输建议
        if app_info.get('cross_border_data') and len(target_markets) > 1:
            recommendations.append({
                'category': '跨境数据传输合规框架',
                'priority': 'critical',
                'recommendation': '建立全球数据传输合规体系',
                'implementation': [
                    '评估所有跨境数据流',
                    '选择适当的传输机制 (充足性决定/SCCs/BCRs)',
                    '实施数据本地化策略',
                    '建立传输影响评估程序',
                    '制定数据泄露跨地区通知机制'
                ]
            })
        
        # GDPR合规体系建议
        if 'EU' in target_markets:
            recommendations.append({
                'category': 'GDPR全面合规体系',
                'priority': 'high',
                'recommendation': '建立完整的GDPR合规管理体系',
                'implementation': [
                    '实现所有数据主体权利功能',
                    '建立合法依据管理框架',
                    '实施Privacy by Design原则',
                    '建立DPIA评估程序',
                    '指定数据保护官 (如需要)'
                ]
            })
        
        # 中国PIPL合规建议
        if 'China' in target_markets:
            recommendations.append({
                'category': 'PIPL个人信息保护合规',
                'priority': 'high',
                'recommendation': '建立符合PIPL要求的个人信息保护体系',
                'implementation': [
                    '制定个人信息处理规则',
                    '指定个人信息保护负责人',
                    '建立个人信息影响评估机制',
                    '实施敏感信息特殊保护措施',
                    '建立个人信息出境安全评估程序'
                ]
            })
        
        return recommendations
    
    def get_cross_domain_insights(self, app_info: Dict, all_expert_results: Dict) -> List[Dict]:
        """提供跨专家领域的洞察"""
        
        insights = []
        
        # 隐私法 × 儿童保护协调
        children_result = all_expert_results.get('children_protection', {})
        if (app_info.get('cross_border_data') and 
            app_info.get('min_user_age', 0) < 16 and
            children_result):
            
            insights.append({
                'title': '儿童数据跨境传输的双重合规挑战',
                'domains': ['privacy_laws', 'children_protection'],
                'description': '儿童个人数据的跨境传输需要同时满足一般数据保护法和儿童保护法规',
                'recommendation': '采用最严格的保护标准：儿童数据尽量本地化处理，必要时采用额外的加密和访问控制措施'
            })
        
        return insights