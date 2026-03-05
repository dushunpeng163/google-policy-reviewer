#!/usr/bin/env python3
"""
🎮📚 教育游戏应用全球合规专家系统 - Python安装脚本
Educational Game Compliance Expert System - Python Installation Script

一键安装所有依赖，检查环境，创建必要目录
"""

import sys
import subprocess
import os
import platform
from pathlib import Path

def print_header():
    """打印安装头部信息"""
    print("🎮📚 教育游戏应用全球合规专家系统")
    print("=" * 60)
    print("系统信息:")
    print(f"  Python版本: {sys.version}")
    print(f"  操作系统: {platform.system()} {platform.release()}")
    print(f"  架构: {platform.machine()}")
    print("=" * 60)

def check_python_version():
    """检查Python版本"""
    print("📋 检查Python版本...")
    
    if sys.version_info < (3, 8):
        print("❌ 错误: 需要Python 3.8或更高版本")
        print(f"   当前版本: {sys.version}")
        print("💡 请访问 https://www.python.org/downloads/ 下载最新版本")
        return False
    
    print(f"✅ Python版本检查通过: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    return True

def check_pip():
    """检查pip是否可用"""
    print("📋 检查pip...")
    
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "--version"], 
                              capture_output=True, text=True, check=True)
        print(f"✅ pip可用: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError:
        print("❌ 错误: pip不可用")
        print("💡 请重新安装Python并确保勾选pip选项")
        return False

def upgrade_pip():
    """升级pip到最新版本"""
    print("⬆️ 升级pip到最新版本...")
    
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], 
                      check=True)
        print("✅ pip升级完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"⚠️ pip升级失败: {e}")
        print("继续使用当前pip版本...")
        return True

def install_requirements():
    """安装依赖包"""
    print("📦 安装核心依赖包...")
    
    # 核心依赖列表
    core_packages = [
        "flask>=2.0.0",
        "flask-cors>=3.0.0",
        "flask-limiter>=2.0.0", 
        "aiohttp>=3.8.0",
        "pyyaml>=6.0.0",
        "requests>=2.28.0",
        "python-dateutil>=2.8.0",
        "cryptography>=3.4.0"
    ]
    
    # 检查是否有requirements文件
    requirements_files = ["requirements-minimal.txt", "requirements.txt"]
    requirements_file = None
    
    for req_file in requirements_files:
        if Path(req_file).exists():
            requirements_file = req_file
            break
    
    try:
        if requirements_file:
            print(f"📋 使用 {requirements_file} 安装依赖...")
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", requirements_file], 
                          check=True)
        else:
            print("📋 手动安装核心依赖...")
            for package in core_packages:
                print(f"  安装 {package}...")
                subprocess.run([sys.executable, "-m", "pip", "install", package], 
                              check=True)
        
        print("✅ 核心依赖安装完成")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖安装失败: {e}")
        return False

def install_optional_dependencies():
    """安装可选依赖"""
    print("\n🤔 可选依赖安装 (可提供额外功能):")
    print("   • PDF报告导出 (reportlab)")
    print("   • HTML转PDF (weasyprint)")  
    print("   • Redis缓存支持 (redis)")
    print("   • PostgreSQL支持 (psycopg2-binary)")
    
    choice = input("\n是否安装可选依赖? (y/N): ").strip().lower()
    
    if choice in ['y', 'yes']:
        optional_packages = [
            "reportlab>=3.6.0",
            "redis>=4.3.0", 
            "psycopg2-binary>=2.9.0"
            # 注意: weasyprint在某些系统上可能需要额外的系统依赖
        ]
        
        print("📦 安装可选依赖...")
        for package in optional_packages:
            try:
                print(f"  安装 {package}...")
                subprocess.run([sys.executable, "-m", "pip", "install", package], 
                              check=True)
            except subprocess.CalledProcessError as e:
                print(f"⚠️ {package} 安装失败，跳过: {e}")
        
        print("✅ 可选依赖安装完成")

def create_directories():
    """创建必要目录"""
    print("📁 创建必要目录...")
    
    directories = ["data", "logs", "config", "reports"]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"  ✅ {directory}/")
    
    print("✅ 目录创建完成")

def verify_installation():
    """验证安装结果"""
    print("\n🧪 验证安装结果...")
    print("-" * 50)
    
    # 要检查的核心包
    core_modules = [
        ("flask", "Flask Web框架"),
        ("aiohttp", "异步HTTP客户端"), 
        ("yaml", "YAML解析器"),
        ("requests", "HTTP请求库"),
        ("cryptography", "加密库")
    ]
    
    success_count = 0
    
    for module_name, description in core_modules:
        try:
            __import__(module_name)
            print(f"✅ {module_name} - {description}")
            success_count += 1
        except ImportError:
            print(f"❌ {module_name} - {description} (导入失败)")
    
    print("-" * 50)
    
    if success_count == len(core_modules):
        print("🎉 所有核心依赖验证成功！")
        return True
    else:
        print(f"⚠️ {success_count}/{len(core_modules)} 个依赖验证成功")
        return False

def show_quick_start():
    """显示快速开始指南"""
    print("\n🚀 快速开始:")
    print("-" * 30)
    print("1. Web可视化界面 (推荐新手):")
    print("   python3 launcher.py --mode web")
    print("   然后访问: http://localhost:5000")
    print()
    print("2. 快速命令行分析:")
    print("   python3 quick_analyzer.py")
    print()
    print("3. 完整系统演示:")
    print("   python3 launcher.py --mode full")
    print()
    print("4. API服务器:")
    print("   python3 launcher.py --mode api")
    print()
    print("📚 更多帮助:")
    print("   • README.md - 详细使用说明")
    print("   • WEB_GUIDE.md - Web界面指南")
    print("   • CONGRATULATIONS.md - 功能总览")
    print()
    print("🎯 现在就可以开始分析你的应用合规性了！")

def main():
    """主安装流程"""
    print_header()
    
    # 检查环境
    if not check_python_version():
        sys.exit(1)
    
    if not check_pip():
        sys.exit(1)
    
    # 升级pip
    if not upgrade_pip():
        print("pip升级失败，但继续安装...")
    
    # 安装核心依赖
    if not install_requirements():
        print("❌ 核心依赖安装失败")
        sys.exit(1)
    
    # 安装可选依赖
    install_optional_dependencies()
    
    # 创建目录
    create_directories()
    
    # 验证安装
    if verify_installation():
        print("\n" + "=" * 60)
        print("🎉 安装完成！系统已准备就绪！")
        show_quick_start()
        print("=" * 60)
    else:
        print("\n⚠️ 安装过程中出现一些问题，但系统可能仍然可用")
        print("🔧 如遇问题请检查错误信息，或查看README.md获取帮助")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ 安装被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 安装过程中发生未知错误: {e}")
        print("🔧 请检查错误信息，或手动安装依赖:")
        print("   python3 -m pip install flask flask-cors flask-limiter aiohttp pyyaml requests")
        sys.exit(1)