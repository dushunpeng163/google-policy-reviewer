#!/usr/bin/env python3
"""
游戏法规专家 (Gaming Regulations Expert)

专精领域:
- 中国游戏法规 (防沉迷、实名认证、充值限制)
- 韩国游戏法 (深夜限制、概率公示)
- 日本扭蛋法规 (Complete Gacha禁令)
- 全球年龄分级 (ESRB、PEGI、CERO等)
- 游戏内购买和虚拟货币法规
"""

from typing import Dict, List
from datetime import datetime

class GamingRegulationsExpert:
    """游戏法规专业专家"""
    
    def __init__(self):
        self.name = "游戏法规专家"
        self.expertise_areas = [
            'China_Gaming_Regulations', 'Korea_Gaming_Laws', 'Japan_Gaming_Rules',
            'Anti_Addiction_Systems', 'Age_Rating_Systems', 'In_App_Purchase_Regulations',
            'Probability_Disclosure', 'Virtual_Currency_Laws'
        ]
        
        # 中国游戏法规详细配置
        self.china_gaming_rules = {
            'time_limits': {
                'weekdays': 0,      # 工作日禁止游戏
                'weekends': 60,     # 周末每日1小时 (20:00-21:00)
                'holidays': 60      # 节假日每日1小时
            },
            'payment_limits': {
                'under_8': {'single': 0, 'monthly': 0},           # 8岁以下禁止充值
                '8_to_16': {'single': 50, 'monthly': 200},        # 8-16岁限制
                '16_to_18': {'single': 100, 'monthly': 400}       # 16-18岁限制
            },
            'required_systems': [
                'real_name_authentication',   # 实名认证系统
                'anti_addiction_system',       # 防沉迷系统
                'parental_supervision',        # 家长监护
                'time_management'              # 时间管理
            ]
        }
        
        # 全球年龄分级系统
        self.age_rating_systems = {
            'ESRB': {  # 美国娱乐软件分级委员会
                'region': 'North America',
                'ratings': ['E', 'E10+', 'T', 'M', 'AO'],
                'mandatory': False,
                'platform_requirement': True  # 主要平台要求
            },
            'PEGI': {  # 欧洲游戏信息分级系统
                'region': 'Europe', 
                'ratings': ['3', '7', '12', '16', '18'],
                'mandatory': True,
                'content_descriptors': True
            },
            'CERO': {  # 日本电脑娱乐分级机构
                'region': 'Japan',
                'ratings': ['A', 'B', 'C', 'D', 'Z'],
                'mandatory': True
            },
            'GCRB': {  # 韩国游戏分级委员회
                'region': 'South Korea', 
                'ratings': ['ALL', '12', '15', '18'],
                'mandatory': True,
                'probability_disclosure': True
            }
        }
    
    def analyze_compliance(self, app_info: Dict, context: Dict = None) -> Dict:
        """分析游戏法规合规性"""
        
        # 判断是否涉及游戏功能
        has_gaming_features = self._detect_gaming_features(app_info)
        
        if not has_gaming_features:
            return {
                'status': 'not_applicable',
                'reason': '应用不包含游戏功能或游戏化元素',
                'issues': [],
                'warnings': [],
                'passed': ['✅ 不适用游戏法规 - 非游戏应用']
            }
        
        print(f"    🎮 {self.name}分析中... (检测到游戏功能)")
        
        target_markets = app_info.get('target_markets', [])
        min_age = app_info.get('min_user_age', 0)
        
        issues = []
        warnings = []
        passed = []
        
        # 按地区执行游戏法规检查
        for market in target_markets:
            market_results = self._check_regional_gaming_compliance(app_info, market)
            issues.extend(market_results['issues'])
            warnings.extend(market_results['warnings'])
            passed.extend(market_results['passed'])
        
        # 通用游戏法规检查
        universal_results = self._check_universal_gaming_compliance(app_info)
        issues.extend(universal_results['issues'])
        warnings.extend(universal_results['warnings'])
        passed.extend(universal_results['passed'])
        
        # 评估游戏合规风险
        risk_level = self._assess_gaming_compliance_risk(app_info, issues, warnings)
        
        return {
            'expert': self.name,
            'risk_level': risk_level,
            'detected_gaming_features': has_gaming_features,
            'issues': issues,
            'warnings': warnings,
            'passed': passed,
            'specialized_recommendations': self._generate_gaming_recommendations(app_info, issues, warnings)
        }
    
    def _detect_gaming_features(self, app_info: Dict) -> List[str]:
        """检测游戏功能特征"""
        
        gaming_features = []
        
        # 明确的游戏标识
        if 'Gaming' in app_info.get('app_type', ''):
            gaming_features.append('declared_as_game')
        
        # 游戏机制检测
        if app_info.get('has_multiplayer'):
            gaming_features.append('multiplayer_mechanics')
        if app_info.get('has_leaderboards'):
            gaming_features.append('competitive_elements')
        if app_info.get('has_virtual_currency'):
            gaming_features.append('virtual_economy')
        if app_info.get('has_in_app_purchases'):
            gaming_features.append('monetization_mechanics')
        if app_info.get('has_random_rewards'):
            gaming_features.append('lootbox_gacha_mechanics')
        if app_info.get('has_time_pressure'):
            gaming_features.append('addictive_design_patterns')
        
        return gaming_features
    
    def _check_regional_gaming_compliance(self, app_info: Dict, region: str) -> Dict:
        """检查特定地区的游戏法规合规性"""
        
        issues = []
        warnings = []
        passed = []
        
        if region == 'China':
            china_results = self._check_china_gaming_compliance(app_info)
            issues.extend(china_results['issues'])
            warnings.extend(china_results['warnings'])
            passed.extend(china_results['passed'])
            
        elif region == 'Korea':
            korea_results = self._check_korea_gaming_compliance(app_info)
            issues.extend(korea_results['issues'])
            warnings.extend(korea_results['warnings'])
            passed.extend(korea_results['passed'])
            
        elif region == 'Japan':
            japan_results = self._check_japan_gaming_compliance(app_info)
            issues.extend(japan_results['issues'])
            warnings.extend(japan_results['warnings'])
            passed.extend(japan_results['passed'])
        
        return {'issues': issues, 'warnings': warnings, 'passed': passed}
    
    def _check_china_gaming_compliance(self, app_info: Dict) -> Dict:
        """中国游戏法规专项检查"""
        
        issues = []
        warnings = []
        passed = []
        
        min_age = app_info.get('min_user_age', 0)
        has_minors = min_age < 18
        
        if not has_minors:
            passed.append('✅ 中国游戏法规: 仅成人用户，无需防沉迷系统')
            return {'issues': issues, 'warnings': warnings, 'passed': passed}
        
        print(f"      🇨🇳 检查中国防沉迷法规... (涉及{18-min_age}岁以下用户)")
        
        # 实名认证系统检查
        if not app_info.get('has_age_verification'):
            issues.append({
                'law': '中国游戏实名认证法规',
                'issue': '涉及未成年人的游戏应用缺少实名认证系统',
                'requirement': '必须接入国家新闻出版署实名认证系统，验证用户真实身份',
                'solution': '对接国家新闻出版署防沉迷实名认证系统API，实现身份证号码+姓名实名验证',
                'region': 'China',
                'severity': 'critical',
                'technical_requirement': '国家新闻出版署防沉迷实名认证系统',
                'legal_basis': '关于进一步严格管理 切实防止未成年人沉迷网络游戏的通知'
            })
        
        # 防沉迷系统时间限制
        if not app_info.get('has_parental_controls'):
            issues.append({
                'law': '中国防沉迷系统',
                'issue': '未实现防沉迷时间管理系统',
                'requirement': '工作日禁止向未成年人提供游戏服务，休息日和节假日每日20:00-21:00限1小时',
                'solution': '实现防沉迷时间检查：工作日0小时，周末/节假日20:00-21:00共1小时',
                'region': 'China',
                'severity': 'critical',
                'time_limits': self.china_gaming_rules['time_limits']
            })
        
        # 充值限制系统
        if app_info.get('has_in_app_purchases'):
            if not app_info.get('has_parental_controls'):  # 假设家长控制包含充值管理
                issues.append({
                    'law': '中国游戏充值限制',
                    'issue': '未成年人游戏内购买缺少年龄分层限制',
                    'requirement': '8岁以下禁止充值；8-16岁单次≤50元/月≤200元；16-18岁单次≤100元/月≤400元',
                    'solution': '实现年龄验证+充值额度控制系统，家长授权机制',
                    'region': 'China',
                    'severity': 'critical',
                    'payment_limits': self.china_gaming_rules['payment_limits']
                })
            else:
                warnings.append({
                    'law': '中国游戏充值限制',
                    'issue': '请确认充值限制功能符合中国法规要求',
                    'requirement': '验证充值限制是否按年龄段正确实施',
                    'solution': '审核现有充值控制功能，确保符合国家规定的额度限制',
                    'region': 'China',
                    'severity': 'high'
                })
        
        # 随机奖励概率公示
        if app_info.get('has_random_rewards'):
            warnings.append({
                'law': '中国游戏概率公示法规',
                'issue': '随机奖励功能需要概率公示',
                'requirement': '所有随机获得物品的概率信息必须公开展示',
                'solution': '在游戏显眼位置展示所有随机奖励的获得概率，定期公布实际概率统计',
                'region': 'China',
                'severity': 'high'
            })
        
        # 家长监护系统
        warnings.append({
            'law': '中国游戏家长监护',
            'issue': '建议完善家长监护功能',
            'requirement': '提供家长查看未成年人游戏时长、消费记录等功能',
            'solution': '开发家长监护平台：游戏时长查询、消费记录、账号管理、强制下线功能',
            'region': 'China',
            'severity': 'medium'
        })
        
        return {'issues': issues, 'warnings': warnings, 'passed': passed}
    
    def _check_korea_gaming_compliance(self, app_info: Dict) -> Dict:
        """韩国游戏法规检查"""
        
        issues = []
        warnings = []
        passed = []
        
        min_age = app_info.get('min_user_age', 0)
        
        # 深夜时间限制 (신데렐라법)
        if min_age < 16:
            warnings.append({
                'law': '韩国深夜游戏限制法 (신데렐라법)',
                'issue': '16岁以下用户需要实施深夜游戏限制',
                'requirement': '16岁以下用户在00:00-06:00期间禁止提供游戏服务',
                'solution': '实现基于韩国时区的深夜游戏限制功能，需要住民登录番号验证年龄',
                'region': 'Korea',
                'severity': 'medium'
            })
        
        # 概率公示义务
        if app_info.get('has_random_rewards'):
            warnings.append({
                'law': '韩国概率公示义务',
                'issue': '随机物品获得概率必须公开',
                'requirement': '概率信息必须在游戏内显眼位置展示，不得技术操控实际概率',
                'solution': '建立概率展示系统和概率统计监控，确保展示概率与实际概率一致',
                'region': 'Korea',
                'severity': 'medium'
            })
        
        if min_age >= 16 and not app_info.get('has_random_rewards'):
            passed.append('✅ 韩国游戏法规: 成人用户且无随机奖励，合规风险较低')
        
        return {'issues': issues, 'warnings': warnings, 'passed': passed}
    
    def _check_japan_gaming_compliance(self, app_info: Dict) -> Dict:
        """日本游戏法规检查"""
        
        issues = []
        warnings = []
        passed = []
        
        # Complete Gacha (コンプガチャ) 规制检查
        if app_info.get('has_random_rewards') and app_info.get('has_in_app_purchases'):
            warnings.append({
                'law': '日本 Complete Gacha 规制',
                'issue': '随机奖励 + 内购组合需要避免Complete Gacha机制',
                'requirement': '禁止设置需集齐多个特定随机物品才能获得奖励的机制',
                'solution': '确保随机奖励独立有价值，不依赖特定组合；公示所有概率信息',
                'region': 'Japan',
                'severity': 'medium'
            })
        
        # 未成年人保护 (20岁以下)
        if app_info.get('min_user_age', 0) < 20:  # 日本成年年龄为20岁
            warnings.append({
                'law': '日本未成年人游戏保护',
                'issue': '20岁以下用户的游戏消费需要监护人同意',
                'requirement': '未成年人的游戏内购买需要获得监护人同意',
                'solution': '实现监护人同意机制和消费限制功能',
                'region': 'Japan',
                'severity': 'medium'
            })
        
        return {'issues': issues, 'warnings': warnings, 'passed': passed}
    
    def _check_universal_gaming_compliance(self, app_info: Dict) -> Dict:
        """通用游戏合规检查"""
        
        issues = []
        warnings = []
        passed = []
        
        target_markets = app_info.get('target_markets', [])
        
        # 年龄分级要求检查
        rating_requirements = []
        if 'US' in target_markets or 'Canada' in target_markets:
            rating_requirements.append('ESRB (北美)')
        if 'EU' in target_markets:
            rating_requirements.append('PEGI (欧盟)')
        if 'Japan' in target_markets:
            rating_requirements.append('CERO (日本)')
        if 'Korea' in target_markets:
            rating_requirements.append('GCRB (韩国)')
        
        if rating_requirements:
            warnings.append({
                'law': '游戏内容年龄分级',
                'issue': '游戏应用可能需要申请内容年龄分级认证',
                'requirement': '根据目标市场申请相应的游戏内容分级',
                'solution': f'申请以下年龄分级认证: {", ".join(rating_requirements)}',
                'region': 'Multiple',
                'severity': 'medium',
                'rating_systems': rating_requirements
            })
        
        # 虚拟货币和内购透明度
        if app_info.get('has_virtual_currency') or app_info.get('has_in_app_purchases'):
            warnings.append({
                'law': '游戏内购透明度最佳实践',
                'issue': '虚拟货币和内购价格需要透明展示',
                'requirement': '清楚标示所有付费内容的真实货币价值',
                'solution': '实现价格透明展示，提供购买确认步骤，支持退款机制',
                'region': 'Universal',
                'severity': 'low'
            })
        
        # 防沉迷设计建议
        if app_info.get('has_time_pressure') or app_info.get('has_random_rewards'):
            warnings.append({
                'law': '健康游戏设计最佳实践',
                'issue': '检测到可能导致过度使用的设计模式',
                'requirement': '建议实施健康游戏设计原则',
                'solution': '添加休息提醒、合理的进度节奏、避免过度激励机制',
                'region': 'Universal',
                'severity': 'low'
            })
        
        return {'issues': issues, 'warnings': warnings, 'passed': passed}
    
    def _assess_gaming_compliance_risk(self, app_info: Dict, issues: List, warnings: List) -> str:
        """评估游戏合规风险等级"""
        
        critical_count = len([issue for issue in issues if issue.get('severity') == 'critical'])
        high_count = len([warning for warning in warnings if warning.get('severity') == 'high'])
        
        # 高风险组合检测
        china_market = 'China' in app_info.get('target_markets', [])
        has_minors = app_info.get('min_user_age', 0) < 18
        has_monetization = (app_info.get('has_in_app_purchases') or 
                           app_info.get('has_virtual_currency'))
        
        if china_market and has_minors and critical_count >= 1:
            return 'critical'
        elif critical_count >= 2:
            return 'very_high'
        elif critical_count >= 1 or (high_count >= 2 and has_monetization):
            return 'high'
        elif high_count >= 1 or (china_market and has_minors):
            return 'medium'
        else:
            return 'low'
    
    def _generate_gaming_recommendations(self, app_info: Dict, issues: List, warnings: List) -> List[Dict]:
        """生成游戏法规专业建议"""
        
        recommendations = []
        
        target_markets = app_info.get('target_markets', [])
        
        # 中国市场专项建议
        if 'China' in target_markets and app_info.get('min_user_age', 0) < 18:
            recommendations.append({
                'category': '中国防沉迷系统实施',
                'priority': 'critical',
                'recommendation': '建立完整的中国游戏合规体系',
                'implementation': [
                    '对接国家新闻出版署实名认证系统',
                    '实现防沉迷时间管理 (工作日0h, 周末1h)',
                    '建立年龄分层充值限制系统',
                    '开发家长监护平台功能',
                    '实施游戏时长和消费统计'
                ],
                'technical_requirements': [
                    '实名认证API集成',
                    '时间控制服务端逻辑',
                    '支付限制中间件',
                    '家长通知系统'
                ]
            })
        
        # 全球年龄分级建议
        if len(target_markets) > 1:
            recommendations.append({
                'category': '全球年龄分级策略',
                'priority': 'high',
                'recommendation': '制定全球统一的内容分级策略',
                'implementation': [
                    '分析各地区分级标准差异',
                    '设计最严格标准的内容审核',
                    '申请目标市场的分级认证',
                    '建立分级标识展示系统'
                ]
            })
        
        # 健康游戏设计建议
        if (app_info.get('has_time_pressure') or 
            app_info.get('has_random_rewards')):
            recommendations.append({
                'category': '健康游戏设计原则',
                'priority': 'medium',
                'recommendation': '实施负责任的游戏设计实践',
                'implementation': [
                    '添加游戏时长提醒功能',
                    '设计合理的进度节奏',
                    '避免过度刺激的奖励机制',
                    '提供游戏暂停和退出选项',
                    '建立用户反馈和支持系统'
                ]
            })
        
        return recommendations
    
    def get_cross_domain_insights(self, app_info: Dict, all_expert_results: Dict) -> List[Dict]:
        """提供跨专家领域的洞察"""
        
        insights = []
        
        # 游戏 × 儿童保护交叉分析
        children_result = all_expert_results.get('children_protection', {})
        if (app_info.get('has_in_app_purchases') and 
            app_info.get('min_user_age', 0) < 13 and
            children_result):
            
            insights.append({
                'title': '游戏货币化 × 儿童保护法规交叉合规',
                'domains': ['gaming_regulations', 'children_protection'],
                'description': '游戏内购买功能遇到儿童用户时，需要同时满足游戏法规和儿童保护法规',
                'recommendation': '建立双重保护机制：游戏法规的充值限制 + 儿童保护法规的家长同意，实现更严格的保护标准'
            })
        
        # 游戏 × 教育应用交叉
        education_result = all_expert_results.get('education_compliance', {})
        if ('Educational' in app_info.get('app_type', '') and 
            app_info.get('has_virtual_currency') and
            education_result):
            
            insights.append({
                'title': '教育游戏货币化的特殊考量',
                'domains': ['gaming_regulations', 'education_compliance'], 
                'description': '教育应用中的游戏化货币系统可能影响教育公平性和学习动机',
                'recommendation': '设计教育导向的奖励机制，避免单纯的商业化驱动，确保符合教育伦理和游戏法规'
            })
        
        return insights