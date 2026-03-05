#!/usr/bin/env python3
"""
快速合规分析工具
Quick Compliance Analysis Tool

无需启动服务器，直接分析应用合规性
"""

import json
from datetime import datetime
from typing import Dict, List, Any

class QuickComplianceAnalyzer:
    """快速合规分析器"""
    
    def __init__(self):
        self.rules = self._load_basic_rules()
    
    def _load_basic_rules(self) -> Dict[str, Any]:
        """加载基础规则"""
        return {
            'age_based_rules': {
                'under_13_us': {
                    'trigger': lambda profile: profile.get('min_user_age', 18) < 13 and 'US' in profile.get('target_markets', []),
                    'severity': 'critical',
                    'message': '美国13岁以下用户需要COPPA家长同意',
                    'requirement': 'COPPA Section 312.5 - 可验证家长同意',
                    'solution': '实现信用卡预授权、数字签名或邮件+电话验证',
                    'region': 'US',
                    'implementation_time': '3-4 weeks',
                    'remediation_cost': '$3000-8000'
                },
                'under_18_china': {
                    'trigger': lambda profile: profile.get('min_user_age', 18) < 18 and 'China' in profile.get('target_markets', []),
                    'severity': 'critical',
                    'message': '中国18岁以下用户需要防沉迷系统',
                    'requirement': '国家新闻出版署防沉迷规定 - 实名认证+时间限制',
                    'solution': '对接NRTA实名认证系统，实现游戏时长和充值限制',
                    'region': 'China',
                    'implementation_time': '4-8 weeks',
                    'remediation_cost': '$5000-15000'
                },
                'under_16_eu': {
                    'trigger': lambda profile: profile.get('min_user_age', 18) < 16 and 'EU' in profile.get('target_markets', []),
                    'severity': 'high',
                    'message': '欧盟16岁以下用户需要特殊保护',
                    'requirement': 'GDPR Article 8 - 儿童信息处理特殊规则',
                    'solution': '实现家长同意机制和儿童数据最小化处理',
                    'region': 'EU',
                    'implementation_time': '2-4 weeks',
                    'remediation_cost': '$2000-5000'
                }
            },
            'feature_based_rules': {
                'in_app_purchases': {
                    'trigger': lambda profile: profile.get('has_in_app_purchases') and profile.get('min_user_age', 18) < 18,
                    'severity': 'high',
                    'message': '未成年人内购功能需要特殊限制',
                    'requirement': '多国法规要求未成年人内购需家长授权或限额',
                    'solution': '实现年龄分层充值限制和家长授权机制',
                    'region': 'Multiple',
                    'implementation_time': '2-3 weeks',
                    'remediation_cost': '$1500-4000'
                },
                'chat_messaging': {
                    'trigger': lambda profile: profile.get('has_chat_messaging') and profile.get('min_user_age', 18) < 13,
                    'severity': 'critical',
                    'message': '儿童聊天功能存在高安全风险',
                    'requirement': '儿童在线安全法规要求严格的内容审核',
                    'solution': '实现实时内容审核、关键词过滤和举报机制',
                    'region': 'Global',
                    'implementation_time': '4-6 weeks',
                    'remediation_cost': '$8000-20000'
                },
                'educational_data': {
                    'trigger': lambda profile: profile.get('collects_educational_data'),
                    'severity': 'medium',
                    'message': '教育数据收集需要FERPA合规',
                    'requirement': 'FERPA要求教育记录保护和家长权利',
                    'solution': '实现教育数据分类保护和家长访问权限',
                    'region': 'US',
                    'implementation_time': '2-4 weeks',
                    'remediation_cost': '$2000-6000'
                },
                'cross_border_data': {
                    'trigger': lambda profile: profile.get('cross_border_data_transfer') and len(profile.get('target_markets', [])) > 1,
                    'severity': 'high',
                    'message': '跨境数据传输需要合规保障',
                    'requirement': 'GDPR、PIPL等要求跨境传输有足够保护措施',
                    'solution': '实施数据本地化或标准合约条款(SCC)',
                    'region': 'Multiple',
                    'implementation_time': '3-6 weeks',
                    'remediation_cost': '$4000-10000'
                }
            },
            'platform_rules': {
                'google_play_kids': {
                    'trigger': lambda profile: 'Android' in profile.get('target_platforms', []) and profile.get('min_user_age', 18) < 13,
                    'severity': 'medium',
                    'message': 'Google Play儿童应用有特殊政策要求',
                    'requirement': 'Google Play儿童和家庭政策',
                    'solution': '遵守儿童定向内容政策，移除不当广告和链接',
                    'region': 'Global',
                    'implementation_time': '1-2 weeks',
                    'remediation_cost': '$500-2000'
                },
                'app_store_kids': {
                    'trigger': lambda profile: 'iOS' in profile.get('target_platforms', []) and profile.get('min_user_age', 18) < 13,
                    'severity': 'medium',
                    'message': 'App Store儿童类别有严格审核标准',
                    'requirement': 'App Store Review Guidelines Section 1.3 - 儿童类别',
                    'solution': '确保内容适龄，实现家长门控功能',
                    'region': 'Global',
                    'implementation_time': '1-2 weeks',
                    'remediation_cost': '$500-2000'
                }
            }
        }
    
    def analyze(self, app_profile: Dict[str, Any]) -> Dict[str, Any]:
        """执行快速合规分析"""
        
        issues = []
        
        # 检查年龄相关规则
        for rule_id, rule in self.rules['age_based_rules'].items():
            if rule['trigger'](app_profile):
                issues.append({
                    'rule_id': rule_id,
                    'severity': rule['severity'],
                    'status': 'failed',
                    'message': rule['message'],
                    'requirement': rule['requirement'],
                    'solution': rule['solution'],
                    'region': rule['region'],
                    'implementation_time': rule['implementation_time'],
                    'remediation_cost': rule['remediation_cost']
                })
        
        # 检查功能相关规则
        for rule_id, rule in self.rules['feature_based_rules'].items():
            if rule['trigger'](app_profile):
                issues.append({
                    'rule_id': rule_id,
                    'severity': rule['severity'],
                    'status': 'failed',
                    'message': rule['message'],
                    'requirement': rule['requirement'],
                    'solution': rule['solution'],
                    'region': rule['region'],
                    'implementation_time': rule['implementation_time'],
                    'remediation_cost': rule['remediation_cost']
                })
        
        # 检查平台规则
        for rule_id, rule in self.rules['platform_rules'].items():
            if rule['trigger'](app_profile):
                issues.append({
                    'rule_id': rule_id,
                    'severity': rule['severity'],
                    'status': 'failed',
                    'message': rule['message'],
                    'requirement': rule['requirement'],
                    'solution': rule['solution'],
                    'region': rule['region'],
                    'implementation_time': rule['implementation_time'],
                    'remediation_cost': rule['remediation_cost']
                })
        
        # 计算风险评估
        risk_assessment = self._calculate_risk_assessment(issues)
        
        # 生成建议
        recommendations = self._generate_recommendations(app_profile, issues)
        
        return {
            'app_profile': app_profile,
            'risk_assessment': risk_assessment,
            'compliance_results': issues,
            'recommendations': recommendations,
            'implementation_guide': {
                'available_templates': [
                    'COPPA家长同意系统 (templates/coppa_parental_consent.py)',
                    '中国防沉迷系统 (templates/china_anti_addiction_system.py)',
                    'GDPR数据权利系统 (templates/gdpr_data_subject_rights.py)'
                ]
            },
            'timestamp': datetime.now().isoformat(),
            'analysis_mode': 'quick_analysis',
            'rules_version': '2.0.0-basic'
        }
    
    def _calculate_risk_assessment(self, issues: List[Dict]) -> Dict[str, Any]:
        """计算风险评估"""
        
        severity_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        total_score = 0
        
        severity_scores = {'critical': 100, 'high': 50, 'medium': 20, 'low': 5}
        
        for issue in issues:
            severity = issue.get('severity', 'low')
            severity_counts[severity] += 1
            total_score += severity_scores.get(severity, 0)
        
        # 确定整体风险等级
        if severity_counts['critical'] > 0:
            overall_risk = 'critical'
        elif severity_counts['high'] > 0:
            overall_risk = 'high'
        elif severity_counts['medium'] > 0:
            overall_risk = 'medium'
        else:
            overall_risk = 'low'
        
        return {
            'risk_level': overall_risk,
            'overall_score': total_score,
            'critical_issues': severity_counts['critical'],
            'high_issues': severity_counts['high'],
            'medium_issues': severity_counts['medium'],
            'low_issues': severity_counts['low'],
            'total_issues': sum(severity_counts.values())
        }
    
    def _generate_recommendations(self, app_profile: Dict, issues: List[Dict]) -> List[Dict]:
        """生成优先建议"""
        
        recommendations = []
        
        # 严重问题优先
        critical_issues = [i for i in issues if i.get('severity') == 'critical']
        if critical_issues:
            recommendations.append({
                'category': '立即行动',
                'priority': 'critical',
                'title': '暂停产品发布直到解决严重问题',
                'description': f'发现{len(critical_issues)}个严重合规问题，建议优先解决后再上架'
            })
        
        # 儿童保护建议
        if app_profile.get('min_user_age', 18) < 13:
            recommendations.append({
                'category': '儿童保护',
                'priority': 'high',
                'title': '实施完整的儿童保护机制',
                'description': '部署COPPA合规系统，包括家长同意验证和数据保护'
            })
        
        # 技术实现建议
        if issues:
            recommendations.append({
                'category': '技术实现',
                'priority': 'high',
                'title': '使用提供的技术模板',
                'description': '系统提供了完整的技术实现代码，可直接部署使用'
            })
        
        # 市场策略建议
        if len(app_profile.get('target_markets', [])) > 2:
            recommendations.append({
                'category': '市场策略',
                'priority': 'medium',
                'title': '考虑分阶段上架策略',
                'description': '多市场合规复杂，建议先在单一市场验证后再扩展'
            })
        
        return recommendations

def quick_analysis_demo():
    """快速分析演示"""
    
    analyzer = QuickComplianceAnalyzer()
    
    # 演示案例1：数学学习游戏
    demo_app = {
        'name': '数学冒险游戏',
        'app_type': 'Educational Gaming',
        'min_user_age': 6,
        'max_user_age': 12,
        'target_markets': ['US', 'China', 'EU'],
        'target_platforms': ['iOS', 'Android'],
        'has_in_app_purchases': True,
        'has_multiplayer': True,
        'has_social_features': True,
        'collects_educational_data': True,
        'cross_border_data_transfer': True,
        'has_parental_controls': False
    }
    
    print("🔍 快速合规分析演示")
    print("=" * 50)
    print(f"分析应用: {demo_app['name']}")
    print(f"用户年龄: {demo_app['min_user_age']}-{demo_app['max_user_age']}岁")
    print(f"目标市场: {', '.join(demo_app['target_markets'])}")
    print("=" * 50)
    
    results = analyzer.analyze(demo_app)
    
    # 显示风险评估
    risk = results['risk_assessment']
    print(f"🎯 风险评估:")
    print(f"   整体风险等级: {risk['risk_level'].upper()}")
    print(f"   风险评分: {risk['overall_score']}")
    print(f"   严重问题: {risk['critical_issues']} 个")
    print(f"   高风险问题: {risk['high_issues']} 个")
    print(f"   中风险问题: {risk['medium_issues']} 个")
    print()
    
    # 显示主要问题
    print("🚨 主要合规问题:")
    for issue in results['compliance_results']:
        severity_icon = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🟢'}.get(issue['severity'], '❓')
        print(f"   {severity_icon} {issue['message']}")
        print(f"      解决方案: {issue['solution']}")
        print(f"      预估成本: {issue['remediation_cost']} | 时间: {issue['implementation_time']}")
        print()
    
    # 显示建议
    print("💡 优先建议:")
    for rec in results['recommendations']:
        priority_icon = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🟢'}.get(rec['priority'], '💭')
        print(f"   {priority_icon} {rec['title']}")
        print(f"      {rec['description']}")
        print()
    
    print("=" * 50)
    print("📋 完整报告已生成，建议部署完整系统获取更详细的分析和可视化报告")
    
    return results

if __name__ == "__main__":
    quick_analysis_demo()