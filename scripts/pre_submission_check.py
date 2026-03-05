#!/usr/bin/env python3
"""
Google 政策合规检查工具
根据应用信息生成详细的合规性报告和整改建议
"""

import json
import sys
from datetime import datetime
from typing import Dict, List, Tuple

class GooglePolicyChecker:
    def __init__(self):
        self.report_data = {
            'app_info': {},
            'compliance_status': {},
            'risk_assessment': {},
            'recommendations': []
        }
    
    def collect_app_info(self) -> Dict:
        """收集应用基本信息"""
        print("=== Google政策合规性检查 ===\n")
        
        app_info = {}
        
        # 基本信息
        app_info['name'] = input("应用名称: ").strip()
        app_info['package'] = input("包名 (可选): ").strip()
        app_info['version'] = input("版本号: ").strip()
        
        # 应用类型
        print("\n应用类型选择:")
        print("1. 社交应用")
        print("2. 游戏应用") 
        print("3. 工具应用")
        print("4. 教育应用")
        print("5. 健康应用")
        print("6. 金融应用")
        print("7. 其他")
        
        app_type_choice = input("选择应用类型 (1-7): ").strip()
        app_types = {
            '1': '社交应用', '2': '游戏应用', '3': '工具应用',
            '4': '教育应用', '5': '健康应用', '6': '金融应用', '7': '其他'
        }
        app_info['type'] = app_types.get(app_type_choice, '其他')
        
        # 目标用户群体
        print("\n目标用户年龄群体:")
        print("1. 仅成人 (18+)")
        print("2. 青少年和成人 (13+)")
        print("3. 包含儿童 (13岁以下)")
        print("4. 主要面向儿童")
        
        age_choice = input("选择目标年龄群体 (1-4): ").strip()
        age_groups = {
            '1': '仅成人', '2': '青少年和成人', 
            '3': '包含儿童', '4': '主要面向儿童'
        }
        app_info['target_age'] = age_groups.get(age_choice, '未指定')
        
        # 功能特性
        print("\n应用包含以下功能吗? (y/n)")
        app_info['has_ads'] = input("广告展示: ").lower().startswith('y')
        app_info['has_iap'] = input("应用内购买: ").lower().startswith('y')
        app_info['collects_location'] = input("位置数据收集: ").lower().startswith('y')
        app_info['user_generated_content'] = input("用户生成内容: ").lower().startswith('y')
        app_info['social_features'] = input("社交功能: ").lower().startswith('y')
        app_info['data_sharing'] = input("第三方数据分享: ").lower().startswith('y')
        
        # 技术信息
        print("\n技术信息:")
        app_info['target_sdk'] = input("目标API级别 (如: 33): ").strip()
        app_info['has_native_code'] = input("包含原生代码? (y/n): ").lower().startswith('y')
        app_info['privacy_policy_url'] = input("隐私政策URL (可选): ").strip()
        
        self.report_data['app_info'] = app_info
        return app_info
    
    def check_play_store_compliance(self, app_info: Dict) -> Dict:
        """检查Play Store政策合规性"""
        issues = []
        warnings = []
        passed = []
        
        # API级别检查
        if app_info.get('target_sdk'):
            try:
                api_level = int(app_info['target_sdk'])
                if api_level < 33:
                    issues.append({
                        'policy': 'Target API Level',
                        'issue': f'目标API级别 {api_level} 不符合要求',
                        'requirement': '新应用必须使用API Level 33+',
                        'solution': '更新build.gradle中的targetSdkVersion到33或更高'
                    })
                else:
                    passed.append('Target API Level: 符合要求')
            except ValueError:
                warnings.append('无法验证API级别，请确保输入数字')
        
        # 隐私政策检查
        if not app_info.get('privacy_policy_url'):
            if (app_info.get('collects_location') or 
                app_info.get('data_sharing') or 
                app_info.get('has_ads')):
                issues.append({
                    'policy': 'Privacy Policy',
                    'issue': '应用收集用户数据但未提供隐私政策',
                    'requirement': '收集个人信息的应用必须提供隐私政策',
                    'solution': '创建隐私政策并在Play Console中添加URL链接'
                })
        else:
            passed.append('Privacy Policy: 已提供隐私政策URL')
        
        # 儿童应用检查
        if app_info.get('target_age') in ['包含儿童', '主要面向儿童']:
            if app_info.get('has_ads'):
                warnings.append({
                    'policy': 'Children\'s Apps',
                    'issue': '儿童应用包含广告需要特别注意',
                    'requirement': '儿童应用不得展示行为广告',
                    'solution': '使用AdMob的儿童导向设置，禁用个性化广告'
                })
            
            if app_info.get('social_features'):
                warnings.append({
                    'policy': 'Children\'s Apps',
                    'issue': '儿童应用的社交功能需要限制',
                    'requirement': '限制儿童与陌生人的交流',
                    'solution': '实现家长控制和内容审核机制'
                })
        
        # 权限使用检查
        if app_info.get('collects_location'):
            if app_info['type'] not in ['地图导航', '出行', '健康']:
                warnings.append({
                    'policy': 'Permissions',
                    'issue': '位置权限使用需要合理解释',
                    'requirement': '位置权限必须对应用核心功能必需',
                    'solution': '在权限请求时向用户解释使用位置的具体原因'
                })
        
        # 64位架构检查
        if app_info.get('has_native_code'):
            warnings.append({
                'policy': '64-bit Requirement',
                'issue': '请确认已支持64位架构',
                'requirement': '包含原生代码的应用必须支持64位',
                'solution': '在build.gradle中添加arm64-v8a和x86_64的ABI支持'
            })
        
        return {
            'issues': issues,
            'warnings': warnings, 
            'passed': passed
        }
    
    def check_adsense_compliance(self, app_info: Dict) -> Dict:
        """检查AdSense广告政策合规性"""
        if not app_info.get('has_ads'):
            return {'issues': [], 'warnings': [], 'passed': ['Not applicable - 应用不包含广告']}
        
        issues = []
        warnings = []
        passed = []
        
        # 儿童应用广告检查
        if app_info.get('target_age') in ['包含儿童', '主要面向儿童']:
            warnings.append({
                'policy': 'Child-Directed Apps',
                'issue': '儿童应用的广告展示有严格限制',
                'requirement': '不得展示行为广告和不当内容',
                'solution': '使用AdMob的TFCD标签，设置child_directed_treatment'
            })
        
        # 应用内广告最佳实践
        warnings.append({
            'policy': 'Ad Placement',
            'issue': '确保广告展示符合用户体验标准',
            'requirement': '广告不得影响应用核心功能使用',
            'solution': '避免在操作按钮旁边放置广告，提供清晰的广告关闭选项'
        })
        
        return {
            'issues': issues,
            'warnings': warnings,
            'passed': passed
        }
    
    def assess_privacy_compliance(self, app_info: Dict) -> Dict:
        """评估隐私合规性"""
        issues = []
        warnings = []
        passed = []
        
        # GDPR相关检查
        if app_info.get('data_sharing') and not app_info.get('privacy_policy_url'):
            issues.append({
                'policy': 'GDPR Data Sharing',
                'issue': '分享用户数据但未提供详细的隐私政策',
                'requirement': 'GDPR要求详细说明数据分享情况',
                'solution': '在隐私政策中详细说明与哪些第三方分享数据及目的'
            })
        
        # COPPA检查
        if app_info.get('target_age') in ['包含儿童', '主要面向儿童']:
            warnings.append({
                'policy': 'COPPA Compliance',
                'issue': '儿童应用需要特殊的隐私保护措施',
                'requirement': '13岁以下儿童的数据收集需要家长同意',
                'solution': '实现年龄验证和家长同意机制，限制数据收集范围'
            })
        
        # 位置数据特殊要求
        if app_info.get('collects_location'):
            warnings.append({
                'policy': 'Location Data',
                'issue': '位置数据收集需要特别注意',
                'requirement': '明确说明位置数据的使用目的和保护措施',
                'solution': '在隐私政策中详细说明位置数据收集、使用和保护措施'
            })
        
        return {
            'issues': issues,
            'warnings': warnings,
            'passed': passed
        }
    
    def generate_recommendations(self, compliance_results: Dict) -> List[str]:
        """生成整改建议"""
        recommendations = []
        
        # 统计问题严重程度
        total_issues = sum(len(result.get('issues', [])) for result in compliance_results.values())
        total_warnings = sum(len(result.get('warnings', [])) for result in compliance_results.values())
        
        if total_issues > 0:
            recommendations.append(f"🚨 发现 {total_issues} 个严重违规问题，需要立即处理")
            
        if total_warnings > 0:
            recommendations.append(f"⚠️ 发现 {total_warnings} 个潜在风险，建议优化")
        
        # 通用建议
        recommendations.extend([
            "📋 建议建立定期政策审查机制，每季度检查一次",
            "🔄 关注Google Play Console的政策更新通知",
            "🛡️ 实施数据安全和隐私保护最佳实践",
            "📝 保持隐私政策的及时更新",
            "🧪 在发布前进行充分的测试，包括权限使用测试"
        ])
        
        return recommendations
    
    def generate_report(self) -> str:
        """生成完整的合规性报告"""
        app_info = self.report_data['app_info']
        
        # 执行各项检查
        play_store_result = self.check_play_store_compliance(app_info)
        adsense_result = self.check_adsense_compliance(app_info)
        privacy_result = self.assess_privacy_compliance(app_info)
        
        compliance_results = {
            'play_store': play_store_result,
            'adsense': adsense_result,
            'privacy': privacy_result
        }
        
        recommendations = self.generate_recommendations(compliance_results)
        
        # 生成报告
        report = f"""
# Google政策合规性审核报告

## 基本信息
- **应用名称**: {app_info.get('name', 'N/A')}
- **应用类型**: {app_info.get('type', 'N/A')}
- **目标用户**: {app_info.get('target_age', 'N/A')}
- **审核时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 功能特性
- 广告展示: {'✓' if app_info.get('has_ads') else '✗'}
- 应用内购买: {'✓' if app_info.get('has_iap') else '✗'}
- 位置数据: {'✓' if app_info.get('collects_location') else '✗'}
- 用户内容: {'✓' if app_info.get('user_generated_content') else '✗'}
- 社交功能: {'✓' if app_info.get('social_features') else '✗'}

## 合规性评估

### Google Play Store政策
"""
        
        # 添加Play Store检查结果
        for issue in play_store_result['issues']:
            report += f"""
❌ **{issue['policy']}**
- 问题: {issue['issue']}
- 要求: {issue['requirement']}
- 解决: {issue['solution']}
"""
        
        for warning in play_store_result['warnings']:
            report += f"""
⚠️ **{warning['policy']}**
- 提醒: {warning['issue']}
- 要求: {warning['requirement']}
- 建议: {warning['solution']}
"""
        
        for passed_item in play_store_result['passed']:
            report += f"✅ {passed_item}\n"
        
        # 添加AdSense检查结果
        report += "\n### AdSense广告政策\n"
        for issue in adsense_result['issues']:
            report += f"""
❌ **{issue['policy']}**
- 问题: {issue['issue']}
- 要求: {issue['requirement']}
- 解决: {issue['solution']}
"""
        
        for warning in adsense_result['warnings']:
            report += f"""
⚠️ **{warning['policy']}**
- 提醒: {warning['issue']}
- 要求: {warning['requirement']}
- 建议: {warning['solution']}
"""
        
        for passed_item in adsense_result['passed']:
            report += f"✅ {passed_item}\n"
        
        # 添加隐私合规检查结果
        report += "\n### 数据隐私合规\n"
        for issue in privacy_result['issues']:
            report += f"""
❌ **{issue['policy']}**
- 问题: {issue['issue']}
- 要求: {issue['requirement']}
- 解决: {issue['solution']}
"""
        
        for warning in privacy_result['warnings']:
            report += f"""
⚠️ **{warning['policy']}**
- 提醒: {warning['issue']}
- 要求: {warning['requirement']}
- 建议: {warning['solution']}
"""
        
        for passed_item in privacy_result['passed']:
            report += f"✅ {passed_item}\n"
        
        # 添加建议
        report += "\n## 整改建议\n\n"
        for rec in recommendations:
            report += f"- {rec}\n"
        
        report += f"""
## 风险等级评估

"""
        
        # 计算风险等级
        total_issues = sum(len(result.get('issues', [])) for result in compliance_results.values())
        total_warnings = sum(len(result.get('warnings', [])) for result in compliance_results.values())
        
        if total_issues >= 3:
            risk_level = "🔴 高风险"
            risk_desc = "存在多个严重违规问题，可能影响应用上架或导致下架"
        elif total_issues >= 1:
            risk_level = "🟠 中风险" 
            risk_desc = "存在明确违规问题，需要在发布前解决"
        elif total_warnings >= 3:
            risk_level = "🟡 低风险"
            risk_desc = "存在潜在风险点，建议优化以避免未来问题"
        else:
            risk_level = "🟢 低风险"
            risk_desc = "合规性良好，建议继续保持并定期审查"
        
        report += f"""
**风险等级**: {risk_level}

**评估说明**: {risk_desc}

## 后续跟进

1. **立即处理**: 解决所有❌标记的严重违规问题
2. **短期优化**: 处理⚠️标记的潜在风险
3. **长期维护**: 建立定期政策审查机制

---
*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*工具版本: Google Policy Reviewer v1.0*
"""
        
        return report

def main():
    checker = GooglePolicyChecker()
    
    try:
        # 收集应用信息
        app_info = checker.collect_app_info()
        
        print("\n正在分析合规性...")
        
        # 生成报告
        report = checker.generate_report()
        
        # 输出报告
        print(report)
        
        # 保存报告到文件
        filename = f"policy_review_{app_info.get('name', 'app')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"\n📄 报告已保存到: {filename}")
        except Exception as e:
            print(f"\n⚠️ 无法保存报告文件: {e}")
        
    except KeyboardInterrupt:
        print("\n\n操作已取消")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 程序执行出错: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()