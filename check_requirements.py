#!/usr/bin/env python3
"""
依赖检查器
Requirements Checker

快速检查系统依赖是否已正确安装
"""

import sys
import importlib
from typing import List, Tuple

def check_dependencies() -> Tuple[bool, List[str]]:
    """检查所有依赖"""
    
    # 核心依赖列表
    required_modules = [
        ("flask", "Flask Web框架", "pip install flask"),
        ("flask_cors", "Flask CORS支持", "pip install flask-cors"),  
        ("flask_limiter", "Flask速率限制", "pip install flask-limiter"),
        ("aiohttp", "异步HTTP客户端", "pip install aiohttp"),
        ("yaml", "YAML解析器", "pip install pyyaml"),
        ("requests", "HTTP请求库", "pip install requests"),
        ("dateutil", "日期处理", "pip install python-dateutil"),
        ("cryptography", "加密库", "pip install cryptography")
    ]
    
    # 内置模块（应该总是可用）
    builtin_modules = [
        ("json", "JSON处理"),
        ("sqlite3", "SQLite数据库"),
        ("asyncio", "异步编程"),
        ("pathlib", "路径处理"),
        ("datetime", "日期时间"),
        ("os", "操作系统接口"),
        ("sys", "系统参数"),
        ("logging", "日志记录")
    ]
    
    print("🧪 检查系统依赖...")
    print("=" * 50)
    
    missing_packages = []
    
    # 检查核心依赖
    print("📦 核心依赖:")
    for module_name, description, install_cmd in required_modules:
        try:
            importlib.import_module(module_name)
            print(f"  ✅ {module_name:<15} - {description}")
        except ImportError:
            print(f"  ❌ {module_name:<15} - {description} (缺失)")
            missing_packages.append((module_name, install_cmd))
    
    # 检查内置模块
    print("\n🐍 Python内置模块:")
    for module_name, description in builtin_modules:
        try:
            importlib.import_module(module_name)
            print(f"  ✅ {module_name:<15} - {description}")
        except ImportError:
            print(f"  ❌ {module_name:<15} - {description} (异常)")
    
    print("=" * 50)
    
    if missing_packages:
        print(f"❌ 发现 {len(missing_packages)} 个缺失的依赖包:")
        print()
        for package, install_cmd in missing_packages:
            print(f"   {install_cmd}")
        
        print("\n🚀 快速安装所有缺失依赖:")
        install_commands = [cmd for _, cmd in missing_packages]
        print(f"   {' && '.join(install_commands)}")
        
        print("\n💡 或使用安装脚本:")
        if sys.platform.startswith('win'):
            print("   install.bat")
        else:
            print("   ./install.sh")
        print("   # 或")
        print("   python3 setup.py")
        
        return False, missing_packages
    else:
        print("🎉 所有依赖检查通过！系统已准备就绪！")
        return True, []

def show_next_steps():
    """显示后续步骤"""
    print("\n🚀 现在你可以:")
    print("   # Web界面 (推荐)")
    print("   python3 launcher.py --mode web")
    print("   # 然后访问: http://localhost:5000")
    print()
    print("   # 快速分析")  
    print("   python3 quick_analyzer.py")
    print()
    print("   # 完整演示")
    print("   python3 launcher.py --mode full")

def main():
    """主函数"""
    print("🎮📚 教育游戏应用全球合规专家系统")
    print("依赖检查器 v2.1.0")
    print()
    
    # 检查Python版本
    if sys.version_info < (3, 8):
        print("❌ 需要Python 3.8或更高版本")
        print(f"当前版本: {sys.version}")
        sys.exit(1)
    
    # 检查依赖
    all_good, missing = check_dependencies()
    
    if all_good:
        show_next_steps()
    else:
        print(f"\n⚠️ 请先安装缺失的 {len(missing)} 个依赖包")
        
        # 询问是否立即安装
        if len(missing) <= 5:  # 如果依赖不多，询问是否立即安装
            choice = input("\n是否立即安装缺失依赖? (y/N): ").strip().lower()
            if choice in ['y', 'yes']:
                try:
                    import subprocess
                    for _, install_cmd in missing:
                        print(f"执行: {install_cmd}")
                        subprocess.run(install_cmd.split(), check=True)
                    
                    print("\n✅ 依赖安装完成！重新检查...")
                    all_good, _ = check_dependencies()
                    if all_good:
                        show_next_steps()
                        
                except Exception as e:
                    print(f"❌ 自动安装失败: {e}")
                    print("请手动执行上述安装命令")

if __name__ == "__main__":
    main()