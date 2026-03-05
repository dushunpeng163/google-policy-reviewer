#!/usr/bin/env python3
"""
全球应用合规检查工具
根据应用信息和目标市场生成详细的合规性报告和整改建议
支持Google政策 + 全球数据保护法律 + 行业特定法规
"""

import json
import sys
import argparse
from datetime import datetime
from typing import Dict, List, Tuple

class GlobalComplianceChecker:
    def __init__(self):
        self.report_data = {
            'app_info': {},
            'target_markets': [],
            'compliance_status': {},
            'risk_assessment': {},
            'recommendations': []
        }
        
        # 地区法规映射
        self.regional_laws = {
            'EU': ['GDPR', 'ePrivacy', 'DSA'],
            'US': ['COPPA', 'CCPA', 'FERPA'],
            'China': ['PIPL', 'Cybersecurity_Law', 'Data_Security_Law'],
            'India': ['DPDP_Act_2023'],
            'Brazil': ['LGPD'],
            'Singapore': ['PDPA'],
            'Canada': ['PIPEDA', 'Bill_C27'],
            'Australia': ['Privacy_Act_1988'],
            'Japan': ['Personal_Information_Protection_Act'],
            'South_Korea': ['Personal_Information_Protection_Act_KR']
        }
        
        # 行业特定法规
        self.industry_laws = {
            'Healthcare': ['HIPAA', 'MDR', 'FDA_Software'],
            'Finance': ['PCI_DSS', 'SOX', 'Basel_III'],
            'Education': ['FERPA', 'COPPA_Education'],
            'Gaming': ['Gambling_Laws', 'Age_Rating_Systems'],
            'Social': ['Content_Moderation_Laws', 'Platform_Liability']
        }
    
    def collect_app_info(self) -> Dict:
        """收集应用基本信息和目标市场"""
        print("=== 全球应用合规性检查 ===\n")
        
        app_info = {}
        
        # 基本信息
        app_info['name'] = input("应用名称: ").strip()
        app_info['package'] = input("包名 (可选): ").strip()
        app_info['version'] = input("版本号: ").strip()
        
        # 目标市场选择
        print("\n🌍 目标发布市场 (可多选，空格分隔):")
        print("1. US (美国)")
        print("2. EU (欧盟)")
        print("3. China (中国)")
        print("4. India (印度)")
        print("5. Brazil (巴西)")
        print("6. Singapore (新加坡)")
        print("7. Canada (加拿大)")
        print("8. Australia (澳大利亚)")
        print("9. Japan (日本)")
        print("10. South_Korea (韩国)")
        
        market_choices = input("选择目标市场 (如: 1 2 3): ").strip().split()
        market_map = {
            '1': 'US', '2': 'EU', '3': 'China', '4': 'India', '5': 'Brazil',
            '6': 'Singapore', '7': 'Canada', '8': 'Australia', '9': 'Japan', '10': 'South_Korea'
        }
        
        app_info['target_markets'] = [market_map.get(choice, 'Unknown') for choice in market_choices]
        
        # 应用类型和行业
        print("\n应用行业类型:")
        print("1. 社交应用 (Social)")
        print("2. 游戏应用 (Gaming)")
        print("3. 工具应用 (Utility)")
        print("4. 教育应用 (Education)")
        print("5. 健康医疗 (Healthcare)")
        print("6. 金融应用 (Finance)")
        print("7. 购物电商 (Shopping)")
        print("8. 其他 (Other)")
        
        industry_choice = input("选择行业类型 (1-8): ").strip()
        industry_map = {
            '1': 'Social', '2': 'Gaming', '3': 'Utility', '4': 'Education',
            '5': 'Healthcare', '6': 'Finance', '7': 'Shopping', '8': 'Other'
        }
        app_info['industry'] = industry_map.get(industry_choice, 'Other')
        
        # 目标用户群体
        print("\n目标用户年龄群体:")
        print("1. 仅成人 (18+)")
        print("2. 青少年和成人 (13+)")
        print("3. 包含儿童 (13岁以下)")
        print("4. 主要面向儿童 (13岁以下)")
        
        age_choice = input("选择目标年龄群体 (1-4): ").strip()
        age_groups = {
            '1': '仅成人', '2': '青少年和成人', 
            '3': '包含儿童', '4': '主要面向儿童'
        }
        app_info['target_age'] = age_groups.get(age_choice, '未指定')
        
        # 功能特性
        print("\n🔍 应用功能特性检查 (y/n):")
        app_info['has_ads'] = input("包含广告展示: ").lower().startswith('y')
        app_info['has_iap'] = input("应用内购买: ").lower().startswith('y')
        app_info['collects_location'] = input("收集位置数据: ").lower().startswith('y')
        app_info['collects_biometric'] = input("收集生物识别数据 (指纹/人脸): ").lower().startswith('y')
        app_info['collects_health'] = input("收集健康数据: ").lower().startswith('y')
        app_info['user_generated_content'] = input("用户生成内容: ").lower().startswith('y')
        app_info['social_features'] = input("社交功能: ").lower().startswith('y')
        app_info['cross_border_data'] = input("跨境数据传输: ").lower().startswith('y')
        app_info['third_party_sharing'] = input("第三方数据分享: ").lower().startswith('y')
        
        # 技术信息
        print("\n🔧 技术信息:")
        app_info['target_sdk'] = input("目标API级别 (如: 33): ").strip()
        app_info['has_native_code'] = input("包含原生代码 (y/n): ").lower().startswith('y')
        app_info['privacy_policy_url'] = input("隐私政策URL (可选): ").strip()
        app_info['data_retention_period'] = input("数据保留期限 (如: 3年): ").strip()
        
        self.report_data['app_info'] = app_info
        self.report_data['target_markets'] = app_info['target_markets']
        return app_info
    
    def get_applicable_laws(self, app_info: Dict) -> List[str]:
        """根据目标市场和行业确定适用法规"""
        applicable_laws = set()
        
        # 添加地区法规
        for market in app_info.get('target_markets', []):
            if market in self.regional_laws:
                applicable_laws.update(self.regional_laws[market])
        
        # 添加行业特定法规
        industry = app_info.get('industry', 'Other')
        if industry in self.industry_laws:
            applicable_laws.update(self.industry_laws[industry])
        
        # Google政策始终适用
        applicable_laws.add('Google_Play_Store')
        if app_info.get('has_ads'):
            applicable_laws.add('AdSense_Policy')
        
        return list(applicable_laws)
    
    def check_google_play_compliance(self, app_info: Dict) -> Dict:
        """检查Google Play Store政策合规性"""
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
                        'solution': '更新build.gradle中的targetSdkVersion到33或更高',
                        'region': 'Global'
                    })
                else:
                    passed.append('Target API Level: 符合要求')
            except ValueError:
                warnings.append('无法验证API级别，请确保输入数字')
        
        # 隐私政策检查
        if not app_info.get('privacy_policy_url'):
            if (app_info.get('collects_location') or 
                app_info.get('third_party_sharing') or 
                app_info.get('has_ads')):
                issues.append({
                    'policy': 'Privacy Policy',
                    'issue': '应用收集用户数据但未提供隐私政策',
                    'requirement': '收集个人信息的应用必须提供隐私政策',
                    'solution': '创建符合多地区要求的隐私政策并在Play Console中添加URL',
                    'region': 'Global'
                })
        else:
            passed.append('Privacy Policy: 已提供隐私政策URL')
        
        # 儿童应用检查
        if app_info.get('target_age') in ['包含儿童', '主要面向儿童']:
            if app_info.get('has_ads'):
                warnings.append({
                    'policy': 'Children\'s Apps - Advertising',
                    'issue': '儿童应用的广告展示需要特别注意',
                    'requirement': '儿童应用不得展示行为广告',
                    'solution': '使用AdMob的儿童导向设置，禁用个性化广告',
                    'region': 'Global'
                })
            
            if app_info.get('social_features'):
                warnings.append({
                    'policy': 'Children\'s Apps - Social Features',
                    'issue': '儿童应用的社交功能需要限制',
                    'requirement': '限制儿童与陌生人的交流',
                    'solution': '实现家长控制和内容审核机制',
                    'region': 'Global'
                })
        
        return {
            'issues': issues,
            'warnings': warnings,
            'passed': passed
        }
    
    def check_gdpr_compliance(self, app_info: Dict) -> Dict:
        """检查GDPR合规性 (欧盟)"""
        if 'EU' not in app_info.get('target_markets', []):
            return {'issues': [], 'warnings': [], 'passed': ['不适用 - 未面向欧盟市场']}
        
        issues = []
        warnings = []
        passed = []
        
        # 用户权利实现检查
        if app_info.get('third_party_sharing') or app_info.get('cross_border_data'):
            warnings.append({
                'policy': 'GDPR - User Rights',
                'issue': '需要实现GDPR要求的用户权利功能',
                'requirement': '访问权、更正权、删除权、数据携带权等',
                'solution': '开发用户数据管理功能：查看、修改、删除、导出个人数据',
                'region': 'EU'
            })
        
        # 合法依据检查
        if not app_info.get('privacy_policy_url'):
            issues.append({
                'policy': 'GDPR - Legal Basis',
                'issue': '缺乏GDPR要求的详细隐私说明',
                'requirement': '必须说明数据处理的合法依据',
                'solution': '在隐私政策中详细说明每种数据处理的合法依据（同意、合同等）',
                'region': 'EU'
            })
        
        # 跨境传输检查
        if app_info.get('cross_border_data'):
            warnings.append({
                'policy': 'GDPR - Cross-border Transfer',
                'issue': '跨境数据传输需要适当保障措施',
                'requirement': '确保数据传输到欧盟外有适当保障',
                'solution': '使用欧盟委员会认可的标准合同条款(SCCs)或充足性决定地区',
                'region': 'EU'
            })
        
        return {
            'issues': issues,
            'warnings': warnings,
            'passed': passed
        }
    
    def check_pipl_compliance(self, app_info: Dict) -> Dict:
        """检查PIPL合规性 (中国)"""
        if 'China' not in app_info.get('target_markets', []):
            return {'issues': [], 'warnings': [], 'passed': ['不适用 - 未面向中国市场']}
        
        issues = []
        warnings = []
        passed = []
        
        # 敏感个人信息检查
        sensitive_data = (app_info.get('collects_biometric') or 
                         app_info.get('collects_health') or
                         app_info.get('target_age') in ['包含儿童', '主要面向儿童'])
        
        if sensitive_data:
            warnings.append({
                'policy': 'PIPL - Sensitive Personal Information',
                'issue': '处理敏感个人信息需要特殊保护措施',
                'requirement': '具有特定目的、充分必要性，取得个人单独同意',
                'solution': '实现敏感信息单独同意机制，采取严格保护技术措施',
                'region': 'China'
            })
        
        # 跨境传输检查
        if app_info.get('cross_border_data'):
            issues.append({
                'policy': 'PIPL - Cross-border Transfer',
                'issue': '个人信息出境需要符合PIPL要求',
                'requirement': '通过安全评估、认证或标准合同',
                'solution': '申请个人信息保护认证或通过网信办安全评估',
                'region': 'China'
            })
        
        # 数据本地化
        if app_info.get('industry') in ['Finance', 'Healthcare']:
            warnings.append({
                'policy': 'PIPL - Data Localization',
                'issue': '关键行业可能需要数据本地化存储',
                'requirement': '重要数据和个人信息境内存储',
                'solution': '评估是否属于关键信息基础设施，如是则需境内存储',
                'region': 'China'
            })
        
        return {
            'issues': issues,
            'warnings': warnings,
            'passed': passed
        }
    
    def check_coppa_compliance(self, app_info: Dict) -> Dict:
        """检查COPPA合规性 (美国儿童隐私)"""
        if ('US' not in app_info.get('target_markets', []) or
            app_info.get('target_age') not in ['包含儿童', '主要面向儿童']):
            return {'issues': [], 'warnings': [], 'passed': ['不适用 - 非美国市场或不面向儿童']}
        
        issues = []
        warnings = []
        passed = []
        
        # 家长同意机制
        if app_info.get('target_age') in ['包含儿童', '主要面向儿童']:
            warnings.append({
                'policy': 'COPPA - Parental Consent',
                'issue': '需要实现可验证的家长同意机制',
                'requirement': '13岁以下儿童个人信息收集需要家长同意',
                'solution': '实现年龄验证和家长同意流程（邮件+信用卡/数字签名等）',
                'region': 'US'
            })
        
        # 数据收集限制
        if app_info.get('collects_location') or app_info.get('social_features'):
            warnings.append({
                'policy': 'COPPA - Data Collection',
                'issue': '儿童应用的数据收集需要最小化',
                'requirement': '不得收集超过必要的儿童个人信息',
                'solution': '禁用位置收集、限制社交功能、关闭行为广告',
                'region': 'US'
            })
        
        return {
            'issues': issues,
            'warnings': warnings,
            'passed': passed
        }
    
    def check_industry_compliance(self, app_info: Dict) -> Dict:
        """检查行业特定法规合规性"""
        industry = app_info.get('industry', 'Other')
        issues = []
        warnings = []
        passed = []
        
        if industry == 'Healthcare':
            # HIPAA检查 (如果面向美国市场)
            if 'US' in app_info.get('target_markets', []) and app_info.get('collects_health'):
                warnings.append({
                    'policy': 'HIPAA - Healthcare Data',
                    'issue': '健康数据处理需要符合HIPAA要求',
                    'requirement': '受保护健康信息(PHI)需要特殊保护',
                    'solution': '实现HIPAA合规措施：加密、访问控制、审计日志、业务伙伴协议',
                    'region': 'US'
                })
        
        elif industry == 'Finance':
            # PCI DSS检查
            if app_info.get('has_iap'):
                warnings.append({
                    'policy': 'PCI DSS - Payment Security',
                    'issue': '支付处理需要符合PCI DSS标准',
                    'requirement': '支付卡数据安全标准合规',
                    'solution': '使用PCI DSS合规的支付处理商，避免直接存储支付卡数据',
                    'region': 'Global'
                })
        
        elif industry == 'Education':
            # FERPA检查 (如果面向美国市场)
            if 'US' in app_info.get('target_markets', []):
                warnings.append({
                    'policy': 'FERPA - Education Records',
                    'issue': '教育记录需要符合FERPA保护要求',
                    'requirement': '学生教育记录隐私保护',
                    'solution': '实现家长/学生查看和修正记录权利，限制记录披露',
                    'region': 'US'
                })
        
        if not warnings and not issues:
            passed.append(f'行业合规: {industry} - 无特殊要求或已覆盖')
        
        return {
            'issues': issues,
            'warnings': warnings,
            'passed': passed
        }
    
    def generate_comprehensive_report(self, app_info: Dict) -> str:
        """生成全球合规综合报告"""
        
        # 执行各项检查
        google_result = self.check_google_play_compliance(app_info)
        gdpr_result = self.check_gdpr_compliance(app_info)
        pipl_result = self.check_pipl_compliance(app_info)
        coppa_result = self.check_coppa_compliance(app_info)
        industry_result = self.check_industry_compliance(app_info)
        
        all_results = {
            'Google Play Store': google_result,
            'GDPR (欧盟)': gdpr_result,
            'PIPL (中国)': pipl_result,
            'COPPA (美国儿童)': coppa_result,
            '行业特定法规': industry_result
        }
        
        # 统计问题数量
        total_issues = sum(len(result.get('issues', [])) for result in all_results.values())
        total_warnings = sum(len(result.get('warnings', [])) for result in all_results.values())
        
        # 生成报告
        report = f"""
# 🌍 全球应用合规性审核报告

## 📋 基本信息
- **应用名称**: {app_info.get('name', 'N/A')}
- **行业类型**: {app_info.get('industry', 'N/A')}
- **目标市场**: {', '.join(app_info.get('target_markets', ['N/A']))}
- **目标用户**: {app_info.get('target_age', 'N/A')}
- **审核时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 🎯 适用法规范围
"""
        
        # 显示适用法规
        applicable_laws = self.get_applicable_laws(app_info)
        for law in applicable_laws:
            report += f"- ✅ {law}\n"
        
        report += """
## 🔍 功能特性概览
"""
        features = [
            ('广告展示', app_info.get('has_ads')),
            ('应用内购买', app_info.get('has_iap')),
            ('位置数据', app_info.get('collects_location')),
            ('生物识别', app_info.get('collects_biometric')),
            ('健康数据', app_info.get('collects_health')),
            ('用户内容', app_info.get('user_generated_content')),
            ('社交功能', app_info.get('social_features')),
            ('跨境数据', app_info.get('cross_border_data'))
        ]
        
        for feature, enabled in features:
            status = '✓' if enabled else '✗'
            report += f"- {feature}: {status}\n"
        
        report += "\n## 🌏 分地区合规性评估\n"
        
        # 按法规分类显示结果
        for law_name, result in all_results.items():
            if not result['issues'] and not result['warnings'] and len(result['passed']) == 1 and '不适用' in result['passed'][0]:
                continue
            
            report += f"\n### {law_name}\n"
            
            # 显示严重问题
            for issue in result['issues']:
                report += f"""
🔴 **{issue['policy']}** [{issue.get('region', 'Global')}]
- **问题**: {issue['issue']}
- **要求**: {issue['requirement']}
- **解决方案**: {issue['solution']}
"""
            
            # 显示警告
            for warning in result['warnings']:
                report += f"""
🟡 **{warning['policy']}** [{warning.get('region', 'Global')}]
- **风险**: {warning['issue']}
- **要求**: {warning['requirement']}
- **建议**: {warning['solution']}
"""
            
            # 显示通过项
            for passed in result['passed']:
                report += f"✅ {passed}\n"
        
        # 风险评估
        report += f"""
## 📊 综合风险评估

### 风险统计
- 🔴 **严重问题**: {total_issues} 项
- 🟡 **潜在风险**: {total_warnings} 项
- ✅ **合规项目**: {sum(len(result.get('passed', [])) for result in all_results.values())} 项

### 风险等级判定
"""
        
        if total_issues >= 5:
            risk_level = "🔴 极高风险"
            risk_desc = "存在多个严重违规问题，强烈建议暂停发布直至问题解决"
        elif total_issues >= 3:
            risk_level = "🟠 高风险"
            risk_desc = "存在严重违规问题，可能影响应用上架或面临法律风险"
        elif total_issues >= 1:
            risk_level = "🟡 中风险"
            risk_desc = "存在明确违规问题，需要在发布前解决"
        elif total_warnings >= 5:
            risk_level = "🟡 中低风险"
            risk_desc = "存在较多潜在风险，建议优化以避免未来问题"
        elif total_warnings >= 1:
            risk_level = "🟢 低风险"
            risk_desc = "合规性良好，存在少量优化建议"
        else:
            risk_level = "🟢 极低风险"
            risk_desc = "合规性优秀，建议继续保持并定期审查"
        
        report += f"""
**当前风险等级**: {risk_level}

**风险说明**: {risk_desc}

## 🚀 整改建议

### 🔴 立即处理 (必须)
"""
        
        priority_issues = []
        for result in all_results.values():
            for issue in result.get('issues', []):
                priority_issues.append(f"- **{issue['policy']}**: {issue['solution']}")
        
        if priority_issues:
            report += "\n".join(priority_issues) + "\n"
        else:
            report += "- 无严重违规问题需要立即处理\n"
        
        report += "\n### 🟡 短期优化 (建议)\n"
        
        priority_warnings = []
        for result in all_results.values():
            for warning in result.get('warnings', []):
                priority_warnings.append(f"- **{warning['policy']}**: {warning['solution']}")
        
        if priority_warnings:
            report += "\n".join(priority_warnings[:5]) + "\n"  # 只显示前5个
        else:
            report += "- 无重要优化建议\n"
        
        report += f"""
### 📋 长期维护 (持续)
- 🔄 **定期审查**: 每季度进行合规性检查
- 📰 **法规监控**: 关注目标市场法规更新
- 🛡️ **安全加固**: 持续改进数据安全措施
- 👥 **团队培训**: 定期进行隐私安全培训
- 🤝 **供应商管理**: 确保第三方服务合规

## 📚 相关资源

### 法规官方文档
- [GDPR官方文本](https://gdpr-info.eu/)
- [中国个人信息保护法](http://www.npc.gov.cn/npc/c30834/202108/a8c4e3672c74491a80b53a172bb753fe.shtml)
- [COPPA合规指南](https://www.ftc.gov/enforcement/rules/rulemaking-regulatory-reform-proceedings/childrens-online-privacy-protection-rule)

### 技术实现参考
- [Privacy by Design最佳实践](references/privacy-compliance.md)
- [跨境数据传输解决方案](references/global-privacy-laws.md)
- [行业特定合规要求](references/global-privacy-laws.md#行业特定法规)

---
**报告生成**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC
**工具版本**: Global Compliance Reviewer v2.0
**免责声明**: 本报告仅供参考，具体合规要求请咨询当地法律专家
"""
        
        return report
    
    def main(self):
        """主程序入口"""
        parser = argparse.ArgumentParser(description='全球应用合规检查工具')
        parser.add_argument('--global-compliance', action='store_true',
                          help='启用全球法规合规检查')
        parser.add_argument('--export-json', action='store_true',
                          help='导出JSON格式报告')
        
        args = parser.parse_args()
        
        try:
            # 收集应用信息
            app_info = self.collect_app_info()
            
            print("\n🔍 正在分析全球合规性...")
            
            # 生成综合报告
            report = self.generate_comprehensive_report(app_info)
            
            # 输出报告
            print(report)
            
            # 保存报告到文件
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            app_name = app_info.get('name', 'app').replace(' ', '_')
            
            # 保存Markdown报告
            md_filename = f"global_compliance_{app_name}_{timestamp}.md"
            try:
                with open(md_filename, 'w', encoding='utf-8') as f:
                    f.write(report)
                print(f"\n📄 报告已保存到: {md_filename}")
            except Exception as e:
                print(f"\n⚠️ 无法保存Markdown报告: {e}")
            
            # 保存JSON报告 (如果requested)
            if args.export_json:
                json_filename = f"global_compliance_{app_name}_{timestamp}.json"
                try:
                    self.report_data['timestamp'] = timestamp
                    self.report_data['summary'] = {
                        'total_issues': sum(len(result.get('issues', [])) for result in [
                            self.check_google_play_compliance(app_info),
                            self.check_gdpr_compliance(app_info),
                            self.check_pipl_compliance(app_info),
                            self.check_coppa_compliance(app_info),
                            self.check_industry_compliance(app_info)
                        ]),
                        'applicable_laws': self.get_applicable_laws(app_info)
                    }
                    
                    with open(json_filename, 'w', encoding='utf-8') as f:
                        json.dump(self.report_data, f, ensure_ascii=False, indent=2)
                    print(f"📊 JSON报告已保存到: {json_filename}")
                except Exception as e:
                    print(f"⚠️ 无法保存JSON报告: {e}")
            
            print(f"""
🎯 **后续步骤建议**:
1. 📋 按优先级处理上述合规问题
2. 👨‍💼 咨询当地法律专家确认具体要求
3. 🔄 建立定期合规检查机制
4. 📚 团队学习相关法规知识

💬 **需要帮助?** 
- 在应用中询问: "请帮我解决GDPR用户权利实现问题"
- 获取更多技术实现细节和代码示例
""")
            
        except KeyboardInterrupt:
            print("\n\n⏹️ 操作已取消")
            sys.exit(0)
        except Exception as e:
            print(f"\n❌ 程序执行出错: {e}")
            sys.exit(1)

if __name__ == "__main__":
    checker = GlobalComplianceChecker()
    checker.main()