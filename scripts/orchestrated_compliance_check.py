#!/usr/bin/env python3
"""
教育游戏应用全球合规专家 - 智能编排器
Orchestrator for Education Gaming Compliance Experts

外部：统一的专业入口
内部：模块化专家系统 + 智能编排
"""

import json
import sys
import argparse
from datetime import datetime
from typing import Dict, List, Tuple
import importlib

class ComplianceOrchestrator:
    """智能合规编排器 - 根据应用特征选择和协调专家模块"""
    
    def __init__(self):
        self.available_experts = {
            'children_protection': 'engines.children_protection_expert',
            'education_compliance': 'engines.education_compliance_expert', 
            'gaming_regulations': 'engines.gaming_regulations_expert',
            'privacy_laws': 'engines.privacy_laws_expert',
            'platform_policies': 'engines.platform_policies_expert'
        }
        
        self.expert_instances = {}
        self.analysis_results = {}
    
    def load_expert(self, expert_name: str):
        """动态加载专家模块"""
        if expert_name in self.expert_instances:
            return self.expert_instances[expert_name]
        
        try:
            module_path = self.available_experts[expert_name]
            module = importlib.import_module(module_path)
            expert_class = getattr(module, self.get_expert_class_name(expert_name))
            
            expert_instance = expert_class()
            self.expert_instances[expert_name] = expert_instance
            return expert_instance
        except Exception as e:
            print(f"警告: 无法加载专家模块 {expert_name}: {e}")
            return None
    
    def get_expert_class_name(self, expert_name: str) -> str:
        """根据专家名称获取类名"""
        name_mapping = {
            'children_protection': 'ChildrenProtectionExpert',
            'education_compliance': 'EducationComplianceExpert',
            'gaming_regulations': 'GamingRegulationsExpert', 
            'privacy_laws': 'PrivacyLawsExpert',
            'platform_policies': 'PlatformPoliciesExpert'
        }
        return name_mapping.get(expert_name, 'BaseExpert')
    
    def analyze_app_profile(self, app_info: Dict) -> Dict:
        """分析应用档案，确定需要的专家"""
        
        needed_experts = set()
        risk_factors = []
        
        # 基于年龄确定儿童保护需求
        min_age = app_info.get('min_user_age', 0)
        if min_age < 18:
            needed_experts.add('children_protection')
            if min_age < 13:
                risk_factors.append('coppa_critical')
            if min_age < 16:
                risk_factors.append('gdpr_children_protection')
        
        # 基于应用类型确定专业领域
        app_type = app_info.get('app_type', '')
        if 'Educational' in app_type:
            needed_experts.add('education_compliance')
            if app_info.get('integrates_with_schools'):
                risk_factors.append('ferpa_critical')
        
        if ('Gaming' in app_type or 
            app_info.get('has_multiplayer') or
            app_info.get('has_in_app_purchases')):
            needed_experts.add('gaming_regulations')
            if 'China' in app_info.get('target_markets', []):
                risk_factors.append('china_gaming_critical')
        
        # 基于目标市场确定隐私法专家需求
        target_markets = app_info.get('target_markets', [])
        if target_markets:
            needed_experts.add('privacy_laws')
            if len(target_markets) > 2:
                risk_factors.append('multi_jurisdiction_complex')
        
        # 平台政策始终需要检查
        needed_experts.add('platform_policies')
        
        return {
            'needed_experts': list(needed_experts),
            'risk_factors': risk_factors,
            'complexity_level': self.assess_complexity(needed_experts, risk_factors),
            'recommended_sequence': self.get_expert_sequence(needed_experts, risk_factors)
        }
    
    def assess_complexity(self, experts: set, risks: list) -> str:
        """评估案例复杂度"""
        if len(risks) >= 3 or 'china_gaming_critical' in risks:
            return 'very_high'
        elif len(experts) >= 4 or any('critical' in risk for risk in risks):
            return 'high' 
        elif len(experts) >= 3:
            return 'medium'
        else:
            return 'low'
    
    def get_expert_sequence(self, experts: set, risks: list) -> list:
        """确定专家检查顺序 - 高风险优先"""
        
        # 定义优先级
        priority_order = {
            'children_protection': 1 if any('coppa' in risk or 'children' in risk for risk in risks) else 3,
            'gaming_regulations': 1 if 'china_gaming_critical' in risks else 4,
            'education_compliance': 2 if 'ferpa_critical' in risks else 4,
            'privacy_laws': 3,
            'platform_policies': 5  # 最后检查，因为可能依赖其他结果
        }
        
        # 按优先级排序
        sorted_experts = sorted(experts, key=lambda x: priority_order.get(x, 10))
        return sorted_experts
    
    def coordinate_expert_analysis(self, app_info: Dict) -> Dict:
        """协调多个专家进行分析"""
        
        profile_analysis = self.analyze_app_profile(app_info)
        needed_experts = profile_analysis['needed_experts']
        expert_sequence = profile_analysis['recommended_sequence']
        
        print(f"🧠 智能分析：检测到需要 {len(needed_experts)} 个专业领域")
        print(f"📋 专家序列：{' → '.join(expert_sequence)}")
        print(f"🎯 复杂度等级：{profile_analysis['complexity_level']}")
        
        consolidated_results = {
            'profile_analysis': profile_analysis,
            'expert_results': {},
            'cross_expert_insights': []
        }
        
        # 按序列执行专家分析
        for expert_name in expert_sequence:
            print(f"🔍 调用 {expert_name} 专家...")
            
            expert = self.load_expert(expert_name)
            if expert:
                try:
                    # 传递之前专家的结果作为上下文
                    context = {
                        'previous_results': consolidated_results['expert_results'],
                        'profile_analysis': profile_analysis
                    }
                    
                    result = expert.analyze_compliance(app_info, context)
                    consolidated_results['expert_results'][expert_name] = result
                    
                    # 专家间交叉洞察
                    cross_insights = expert.get_cross_domain_insights(
                        app_info, consolidated_results['expert_results']
                    )
                    if cross_insights:
                        consolidated_results['cross_expert_insights'].extend(cross_insights)
                        
                except Exception as e:
                    print(f"⚠️ {expert_name} 专家分析出错: {e}")
                    consolidated_results['expert_results'][expert_name] = {
                        'status': 'error',
                        'message': str(e)
                    }
        
        return consolidated_results
    
    def synthesize_final_report(self, consolidated_results: Dict, app_info: Dict) -> str:
        """综合各专家结果生成最终报告"""
        
        profile = consolidated_results['profile_analysis']
        expert_results = consolidated_results['expert_results']
        cross_insights = consolidated_results['cross_expert_insights']
        
        # 统计问题严重程度
        all_issues = []
        all_warnings = []
        
        for expert_name, result in expert_results.items():
            if isinstance(result, dict) and 'issues' in result:
                all_issues.extend(result.get('issues', []))
                all_warnings.extend(result.get('warnings', []))
        
        # 按严重程度排序
        critical_issues = [issue for issue in all_issues if issue.get('severity') == 'critical']
        high_warnings = [warning for warning in all_warnings if warning.get('severity') == 'high']
        
        report = f"""
# 🎮📚 教育游戏应用合规专家系统分析报告

## 🧠 智能分析概览

### 📊 应用复杂度档案
- **应用名称**: {app_info.get('name', 'N/A')}
- **复杂度等级**: {profile['complexity_level'].upper()}
- **涉及专家**: {len(profile['needed_experts'])} 个专业领域
- **风险因子**: {len(profile['risk_factors'])} 项
- **目标市场**: {', '.join(app_info.get('target_markets', []))}

### 🎯 专家协作分析
调用专家序列: {' → '.join(profile['recommended_sequence'])}

**检测到的关键风险**:
"""
        
        for risk in profile['risk_factors']:
            risk_descriptions = {
                'coppa_critical': '🚨 COPPA关键合规 - 13岁以下儿童保护',
                'gdpr_children_protection': '🛡️ GDPR儿童条款 - 16岁以下特殊保护',
                'ferpa_critical': '📚 FERPA关键合规 - 教育记录保护',
                'china_gaming_critical': '🎮 中国游戏法规 - 防沉迷系统必需',
                'multi_jurisdiction_complex': '🌍 多司法管辖区复杂性'
            }
            description = risk_descriptions.get(risk, risk)
            report += f"- {description}\n"
        
        report += f"""
## 🔍 专家分析结果

### 📈 问题统计总览
- 🔴 **严重问题**: {len(critical_issues)} 项
- 🟠 **高风险警告**: {len(high_warnings)} 项
- 🟡 **一般建议**: {len(all_warnings) - len(high_warnings)} 项
"""
        
        # 显示各专家的核心发现
        expert_names = {
            'children_protection': '👶 儿童保护专家',
            'education_compliance': '📚 教育合规专家',
            'gaming_regulations': '🎮 游戏法规专家',
            'privacy_laws': '🔒 隐私法律专家',
            'platform_policies': '📱 平台政策专家'
        }
        
        for expert_key, result in expert_results.items():
            if isinstance(result, dict) and result.get('status') != 'error':
                expert_name = expert_names.get(expert_key, expert_key)
                report += f"\n### {expert_name}\n"
                
                # 显示该专家的关键发现
                expert_issues = result.get('issues', [])
                expert_warnings = result.get('warnings', [])
                expert_passed = result.get('passed', [])
                
                if expert_issues:
                    report += "**🔴 严重问题:**\n"
                    for issue in expert_issues[:3]:  # 只显示前3个最重要的
                        report += f"- {issue.get('law', 'Unknown')}: {issue.get('issue', 'N/A')}\n"
                
                if expert_warnings:
                    report += "**🟡 重要建议:**\n"
                    for warning in expert_warnings[:2]:  # 只显示前2个
                        report += f"- {warning.get('law', 'Unknown')}: {warning.get('issue', 'N/A')}\n"
                
                if expert_passed:
                    report += f"**✅ 合规项目**: {len(expert_passed)} 项\n"
        
        # 跨专家洞察
        if cross_insights:
            report += "\n## 🔗 跨领域专家洞察\n"
            for insight in cross_insights:
                report += f"""
**{insight.get('title', 'Cross-Domain Insight')}**
- 涉及领域: {', '.join(insight.get('domains', []))}
- 洞察内容: {insight.get('description', 'N/A')}
- 建议行动: {insight.get('recommendation', 'N/A')}
"""
        
        # 综合行动建议
        report += f"""
## 🚀 综合行动方案

### 🔴 紧急处理 (必须立即解决)
"""
        
        if critical_issues:
            for i, issue in enumerate(critical_issues[:5], 1):  # 前5个最重要
                report += f"{i}. **{issue.get('law', 'Unknown')}**: {issue.get('solution', 'N/A')}\n"
        else:
            report += "✅ 无需紧急处理的问题\n"
        
        report += "\n### 🟡 重点优化 (建议尽快处理)\n"
        
        if high_warnings:
            for i, warning in enumerate(high_warnings[:5], 1):
                report += f"{i}. **{warning.get('law', 'Unknown')}**: {warning.get('solution', 'N/A')}\n"
        else:
            report += "✅ 无重点优化项目\n"
        
        # 根据复杂度给出专业建议
        complexity_advice = {
            'very_high': [
                "🏢 强烈建议咨询专业法律团队",
                "🔄 建立专职合规岗位",
                "📋 实施分阶段合规策略",
                "⏱️ 预计合规周期: 3-6个月"
            ],
            'high': [
                "👨‍💼 建议咨询法律顾问",
                "🎯 优先处理儿童保护和隐私合规",
                "📅 建立月度合规检查",
                "⏱️ 预计合规周期: 1-3个月"
            ],
            'medium': [
                "📚 深入学习相关法规要求",
                "🛠️ 逐步实施合规功能",
                "📊 建立合规检查清单"
            ],
            'low': [
                "✅ 当前合规性良好",
                "🔄 保持定期检查",
                "📈 关注法规更新"
            ]
        }
        
        advice_list = complexity_advice.get(profile['complexity_level'], complexity_advice['medium'])
        
        report += f"""
### 💡 基于复杂度的专业建议 ({profile['complexity_level'].upper()})

"""
        
        for advice in advice_list:
            report += f"- {advice}\n"
        
        report += f"""
## 📞 持续支持

本专家系统可以为您提供：

1. **深度技术指导**: 
   - "请帮我实现COPPA家长同意验证系统"
   - "中国防沉迷系统的具体技术方案"

2. **法规最新解读**:
   - "GDPR最新修订对教育应用的影响"
   - "各国儿童保护法规对比分析"

3. **最佳实践分享**:
   - "教育游戏隐私政策模板"
   - "多地区年龄验证解决方案"

---
**专家系统**: 教育游戏合规智能编排器 v2.0
**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC
**专家协作**: {len(expert_results)} 个专业模块
**免责声明**: 本报告基于AI专家系统分析，具体实施请咨询当地法律专家
"""
        
        return report

    def collect_app_info(self) -> Dict:
        """收集应用基本信息"""
        print("=== 🎮📚 教育游戏合规专家系统 ===\n")
        print("🧠 智能编排器将根据您的应用特征自动选择相关专家\n")
        
        app_info = {}
        
        # 基本信息
        app_info['name'] = input("应用名称: ").strip()
        app_info['version'] = input("版本号 (可选): ").strip()
        
        # 应用类型快速识别
        print("\n📱 应用类型:")
        print("1. 纯教育应用")
        print("2. 纯游戏应用") 
        print("3. 教育游戏")
        print("4. 游戏化学习平台")
        
        type_choice = input("选择类型 (1-4): ").strip()
        type_map = {
            '1': 'Educational', '2': 'Gaming',
            '3': 'Educational Gaming', '4': 'Gamified Learning'
        }
        app_info['app_type'] = type_map.get(type_choice, 'Educational Gaming')
        
        # 关键年龄信息
        print(f"\n👶 目标年龄群体 (影响儿童保护法规):")
        print("1. 学前(3-5岁)")
        print("2. 小学(6-12岁)")
        print("3. 中学(13-17岁)")
        print("4. 成人(18+岁)")
        print("5. 全年龄")
        
        age_choice = input("选择年龄群体 (1-5): ").strip()
        age_groups = {
            '1': '学前(3-5岁)', '2': '小学(6-12岁)', '3': '中学(13-17岁)',
            '4': '成人(18+岁)', '5': '全年龄'
        }
        app_info['target_age_group'] = age_groups.get(age_choice, '全年龄')
        
        # 最小年龄用于法规判断
        min_age_map = {'1': 3, '2': 6, '3': 13, '4': 18, '5': 0}
        app_info['min_user_age'] = min_age_map.get(age_choice, 0)
        
        # 目标市场
        print(f"\n🌍 目标市场 (多选，空格分隔):")
        print("1-US  2-EU  3-UK  4-China  5-Korea  6-Japan")
        
        market_input = input("输入数字 (如: 1 2 4): ").strip()
        market_map = {
            '1': 'US', '2': 'EU', '3': 'UK', '4': 'China',
            '5': 'Korea', '6': 'Japan'
        }
        app_info['target_markets'] = [
            market_map[choice] for choice in market_input.split() 
            if choice in market_map
        ]
        
        # 关键功能快速勾选
        print(f"\n🔍 关键功能 (y/n):")
        key_features = [
            ('tracks_learning_progress', '学习进度追踪'),
            ('integrates_with_schools', '学校系统集成'),
            ('has_multiplayer', '多人游戏'),
            ('has_chat_social', '聊天社交'),
            ('has_in_app_purchases', '应用内购买'),
            ('has_advertising', '广告展示'),
            ('cross_border_data', '跨境数据传输'),
            ('has_parental_controls', '家长控制 (已实现)'),
            ('has_age_verification', '年龄验证 (已实现)')
        ]
        
        for key, description in key_features:
            app_info[key] = input(f"{description}: ").lower().startswith('y')
        
        app_info['privacy_policy_url'] = input("\n隐私政策URL (必需): ").strip()
        
        return app_info

    def main(self):
        """主程序入口"""
        parser = argparse.ArgumentParser(description='教育游戏应用合规专家系统')
        parser.add_argument('--orchestrated-analysis', action='store_true',
                          help='启用智能编排分析')
        
        args = parser.parse_args()
        
        try:
            # 收集应用信息
            app_info = self.collect_app_info()
            
            print(f"\n🧠 启动智能合规专家系统...")
            print(f"📊 应用档案: {app_info.get('app_type')} | {app_info.get('target_age_group')} | {len(app_info.get('target_markets', []))}个市场")
            
            # 协调专家分析
            consolidated_results = self.coordinate_expert_analysis(app_info)
            
            # 生成综合报告
            final_report = self.synthesize_final_report(consolidated_results, app_info)
            
            # 输出报告
            print(final_report)
            
            # 保存报告
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            app_name = app_info.get('name', 'app').replace(' ', '_')
            filename = f"expert_system_report_{app_name}_{timestamp}.md"
            
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(final_report)
                print(f"\n📄 专家系统报告已保存: {filename}")
            except Exception as e:
                print(f"⚠️ 无法保存报告: {e}")
                
        except KeyboardInterrupt:
            print("\n\n⏹️ 分析已取消")
            sys.exit(0)
        except Exception as e:
            print(f"\n❌ 专家系统出错: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

if __name__ == "__main__":
    orchestrator = ComplianceOrchestrator()
    orchestrator.main()