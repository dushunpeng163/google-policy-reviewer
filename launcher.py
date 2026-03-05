#!/usr/bin/env python3
"""
合规系统启动器
Compliance System Launcher

一键启动合规专家系统的所有组件：
- RESTful API服务器
- 可视化仪表板服务
- 规则引擎热重载
- 数据库初始化

使用方法:
python3 launcher.py [--mode api|dashboard|full] [--port 5000] [--debug]
"""

import os
import sys
import argparse
import asyncio
import subprocess
from pathlib import Path
from typing import Optional
import json
import time

class ComplianceSystemLauncher:
    """合规系统启动器"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.data_dir = self.project_root / "data"
        self.logs_dir = self.project_root / "logs" 
        
        # 确保目录存在
        self.data_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)
    
    def check_dependencies(self) -> bool:
        """检查依赖项"""
        required_packages = [
            'flask', 'flask-cors', 'flask-limiter', 
            'aiohttp', 'sqlite3', 'pyyaml'
        ]
        
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            print(f"❌ 缺少依赖包: {', '.join(missing_packages)}")
            print(f"请运行: pip install {' '.join(missing_packages)}")
            return False
        
        print("✅ 依赖项检查完成")
        return True
    
    def initialize_databases(self):
        """初始化数据库"""
        print("📊 初始化数据库...")
        
        db_files = [
            "compliance.db",
            "anti_addiction.db", 
            "gdpr_rights.db"
        ]
        
        for db_file in db_files:
            db_path = self.data_dir / db_file
            if not db_path.exists():
                print(f"  创建数据库: {db_file}")
                # 数据库会在首次导入相关模块时自动创建
        
        print("✅ 数据库初始化完成")
    
    def start_web_interface(self, port: int = 8080, debug: bool = False):
        """启动Web可视化界面"""
        print(f"🌐 启动Web可视化界面 (端口: {port})")
        print("=" * 50)
        print("📍 访问地址:")
        print(f"   • 主界面: http://localhost:{port}")
        print(f"   • API文档: http://localhost:{port}/docs")
        print(f"   • 演示仪表板: http://localhost:{port}/demo")
        print("=" * 50)
        print("💡 使用说明:")
        print("   1. 在主界面填写应用信息")
        print("   2. 点击'开始智能合规分析'")
        print("   3. 查看详细的合规分析报告")
        print("   4. 获取完整的解决方案代码")
        print("=" * 50)
        
        try:
            # 检查Web界面文件是否存在
            web_interface_file = self.project_root / "web_interface.html"
            if not web_interface_file.exists():
                print("❌ Web界面文件不存在，正在创建...")
                # 这里可以创建基本的Web界面文件
            
            # 启动API服务器（包含Web界面）
            self.start_api_server(port, debug)
            
        except Exception as e:
            print(f"❌ Web界面启动失败: {e}")
            
            # 提供快速分析备选方案
            print("💡 备选方案：使用命令行快速分析")
            try:
                sys.path.insert(0, str(self.project_root))
                from quick_analyzer import quick_analysis_demo
                quick_analysis_demo()
            except Exception as fallback_error:
                print(f"备选方案也失败了: {fallback_error}")
    
    def start_api_server(self, port: int = 8080, debug: bool = False):
        """启动API服务器"""
        print(f"🚀 启动API服务器 (端口: {port})")
        
        api_script = self.project_root / "api" / "compliance_api.py"
        
        if not api_script.exists():
            print("❌ API服务器脚本不存在")
            return False
        
        # 设置环境变量
        env = os.environ.copy()
        env['FLASK_APP'] = str(api_script)
        env['FLASK_ENV'] = 'development' if debug else 'production'
        
        try:
            # 启动Flask应用
            cmd = [
                sys.executable, str(api_script), 
                '--host', '0.0.0.0', 
                '--port', str(port)
            ]
            
            if debug:
                cmd.append('--debug')
            
            print(f"执行命令: {' '.join(cmd)}")
            subprocess.run(cmd, env=env)
            
        except KeyboardInterrupt:
            print("\n🛑 API服务器已停止")
        except Exception as e:
            print(f"❌ API服务器启动失败: {e}")
            return False
        
        return True
    
    def generate_sample_dashboard(self):
        """生成示例仪表板"""
        print("📊 生成示例可视化仪表板...")
        
        try:
            # 导入可视化引擎
            sys.path.insert(0, str(self.project_root))
            from engines.compliance_visualizer import generate_compliance_dashboard
            
            # 创建示例数据
            sample_data = {
                'app_profile': {
                    'name': 'Demo Education Game',
                    'app_type': 'Educational Gaming',
                    'target_age_group': '小学生(6-12岁)',
                    'target_markets': ['US', 'China', 'EU', 'UK']
                },
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'rules_version': '2.0.0',
                'risk_assessment': {
                    'risk_level': 'high',
                    'overall_score': 280.5,
                    'critical_issues': 3,
                    'high_issues': 2,
                    'medium_issues': 4,
                    'low_issues': 1,
                    'market_specific_risks': {
                        'US': 220.2,
                        'China': 380.8,
                        'EU': 180.1,
                        'UK': 150.3
                    }
                },
                'compliance_results': [
                    {
                        'rule_id': 'coppa_parental_consent',
                        'severity': 'critical',
                        'status': 'failed',
                        'message': '缺少COPPA家长同意机制',
                        'requirement': 'COPPA要求可验证的家长同意',
                        'solution': '实现信用卡预授权或数字签名验证',
                        'region': 'US',
                        'remediation_cost': '$3000-8000',
                        'implementation_time': '3-4 weeks'
                    },
                    {
                        'rule_id': 'china_anti_addiction',
                        'severity': 'critical',
                        'status': 'failed',
                        'message': '缺少中国防沉迷系统',
                        'requirement': '必须接入NRTA实名认证系统',
                        'solution': '实现实名认证和时间限制功能',
                        'region': 'China',
                        'remediation_cost': '$5000-15000',
                        'implementation_time': '4-8 weeks'
                    },
                    {
                        'rule_id': 'gdpr_data_protection',
                        'severity': 'high',
                        'status': 'failed',
                        'message': 'GDPR数据保护措施不完整',
                        'requirement': 'GDPR要求数据主体权利实现',
                        'solution': '实现访问、更正、删除等权利',
                        'region': 'EU',
                        'remediation_cost': '$4000-12000',
                        'implementation_time': '3-6 weeks'
                    }
                ],
                'recommendations': [
                    {
                        'category': '立即行动',
                        'priority': 'critical',
                        'title': '暂停产品发布',
                        'description': '发现多个严重合规问题，建议暂停发布直到解决'
                    },
                    {
                        'category': '技术实现',
                        'priority': 'high',
                        'title': '实现COPPA家长同意系统',
                        'description': '使用提供的模板实现信用卡预授权验证'
                    },
                    {
                        'category': '法规合规',
                        'priority': 'high',
                        'title': '建立中国防沉迷系统',
                        'description': '对接NRTA实名认证，实现时间和充值限制'
                    }
                ]
            }
            
            # 生成仪表板
            dashboard_file = generate_compliance_dashboard(sample_data)
            
            print(f"✅ 示例仪表板已生成: {dashboard_file}")
            print(f"🌐 请在浏览器中打开查看: file://{Path(dashboard_file).absolute()}")
            
        except Exception as e:
            print(f"❌ 仪表板生成失败: {e}")
            import traceback
            traceback.print_exc()
    
    def run_compliance_check(self, app_profile: dict = None):
        """运行合规检查"""
        print("🔍 执行合规分析...")
        
        try:
            # 导入编排器
            sys.path.insert(0, str(self.project_root))
            from scripts.orchestrated_compliance_check import run_orchestrated_analysis
            
            # 使用默认示例配置
            if not app_profile:
                app_profile = {
                    "name": "Math Learning Adventure",
                    "app_type": "Educational Gaming",
                    "target_age_group": "小学生(6-12岁)",
                    "min_user_age": 6,
                    "target_markets": ["US", "China", "EU"],
                    "has_multiplayer": True,
                    "has_in_app_purchases": True,
                    "has_social_features": True,
                    "collects_educational_data": True,
                    "has_parental_controls": False,
                    "uses_ai_algorithms": True,
                    "cross_border_data_transfer": True,
                    "advertising_present": False,
                    "data_sharing_third_parties": True,
                    "target_platforms": ["iOS", "Android", "Web"]
                }
            
            print("应用档案:")
            for key, value in app_profile.items():
                print(f"  {key}: {value}")
            print()
            
            # 执行分析
            asyncio.run(run_orchestrated_analysis(app_profile))
            
        except Exception as e:
            print(f"❌ 合规检查失败: {e}")
            import traceback
            traceback.print_exc()
    
    def show_system_info(self):
        """显示系统信息"""
        print("📋 教育游戏应用全球合规专家系统 v2.0")
        print("=" * 60)
        print(f"项目目录: {self.project_root}")
        print(f"数据目录: {self.data_dir}")
        print(f"日志目录: {self.logs_dir}")
        print()
        
        print("🧠 可用专家模块:")
        expert_modules = [
            "儿童保护专家 (COPPA、GDPR儿童条款)",
            "游戏法规专家 (中国防沉迷、韩国游戏法)",
            "教育合规专家 (FERPA、学生隐私法)",
            "隐私法律专家 (GDPR、PIPL、CCPA)",
            "平台政策专家 (Google Play、App Store)"
        ]
        
        for module in expert_modules:
            print(f"  ✅ {module}")
        print()
        
        print("🚀 可用启动模式:")
        print("  web             - 启动Web可视化界面 (推荐)")
        print("  api             - 启动RESTful API服务器")
        print("  dashboard       - 生成可视化仪表板")
        print("  check           - 执行合规分析检查")
        print("  check-policies  - 检查政策规则数据新鲜度")
        print("  full            - 完整系统演示")
        print()
        
        print("📊 技术资产统计:")
        try:
            # 统计代码行数
            py_files = list(self.project_root.glob("**/*.py"))
            total_lines = 0
            for py_file in py_files:
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        total_lines += len(f.readlines())
                except:
                    pass
            
            print(f"  Python代码文件: {len(py_files)} 个")
            print(f"  总代码行数: {total_lines:,} 行")
            print(f"  技术模板: {len(list((self.project_root / 'templates').glob('*.py')))} 个")
            print(f"  专家引擎: {len(list((self.project_root / 'engines').glob('*.py')))} 个")
            
        except Exception as e:
            print(f"  统计失败: {e}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="教育游戏应用全球合规专家系统 v2.0 启动器"
    )
    
    parser.add_argument(
        '--mode', 
        choices=['api', 'dashboard', 'check', 'full', 'info', 'web', 'check-policies'],
        default='info',
        help='启动模式（check-policies: 检查政策规则新鲜度）'
    )
    
    parser.add_argument(
        '--port', 
        type=int, 
        default=8080,
        help='API服务器端口 (默认: 8080)'
    )
    
    parser.add_argument(
        '--debug', 
        action='store_true',
        help='启用调试模式'
    )
    
    args = parser.parse_args()
    
    # 创建启动器实例
    launcher = ComplianceSystemLauncher()
    
    print("🎮📚 教育游戏应用全球合规专家系统 v2.0")
    print("=" * 60)
    
    # 根据模式执行相应操作
    if args.mode == 'info':
        launcher.show_system_info()
    
    elif args.mode == 'web':
        print("🌐 启动Web可视化界面...")
        launcher.start_web_interface(args.port, args.debug)
    
    elif args.mode == 'api':
        if launcher.check_dependencies():
            launcher.initialize_databases()
            launcher.start_api_server(args.port, args.debug)
    
    elif args.mode == 'dashboard':
        launcher.generate_sample_dashboard()
    
    elif args.mode == 'check':
        launcher.run_compliance_check()
    
    elif args.mode == 'check-policies':
        print("🔍 检查政策规则数据新鲜度...\n")
        sys.path.insert(0, str(Path(__file__).parent))
        from engines.policy_monitor import load_versions, analyze_freshness, print_freshness_report
        versions = load_versions()
        if not versions:
            print("❌ policy_versions.json 未找到")
        else:
            report = analyze_freshness(versions)
            print_freshness_report(report)
            if report['outdated_rules']:
                print("📋 复核步骤：")
                print("  1. 访问上方列出的官方来源 URL，确认政策最新内容")
                print("  2. 如政策有变化，更新 engines/platform_policies_expert.py 中的相关规则")
                print("  3. 运行以下命令将规则标记为已验证：")
                print("     python3 engines/policy_monitor.py --mark-verified PLATFORM:RULE_ID")
                print("  4. 或一次性标记所有规则（全面复核后）：")
                print("     python3 engines/policy_monitor.py --mark-all-verified")
            print("\n💡 联网自动监控命令：")
            print("   RSS 公告监控  : python3 engines/policy_monitor.py --rss")
            print("   页面变化检测  : python3 engines/policy_monitor.py --fetch")
            print("   持续自动监控  : python3 engines/policy_monitor.py --watch 3600")
            print("   查看历史告警  : python3 engines/policy_monitor.py --alerts\n")

    elif args.mode == 'full':
        print("🚀 完整系统演示模式")
        print()
        
        # 1. 依赖检查
        if not launcher.check_dependencies():
            return
        
        # 2. 数据库初始化  
        launcher.initialize_databases()
        
        # 3. 执行合规检查
        launcher.run_compliance_check()
        
        # 4. 生成可视化仪表板
        launcher.generate_sample_dashboard()
        
        # 5. 询问是否启动API服务器
        try:
            response = input("\n是否启动API服务器? [y/N]: ").strip().lower()
            if response in ['y', 'yes']:
                launcher.start_api_server(args.port, args.debug)
        except KeyboardInterrupt:
            print("\n👋 再见!")

if __name__ == "__main__":
    main()