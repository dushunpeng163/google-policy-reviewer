@echo off
rem 🎮📚 教育游戏应用全球合规专家系统 - Windows安装脚本
rem Educational Game Compliance Expert System - Windows Installation Script

echo 🎮📚 教育游戏应用全球合规专家系统 - 开始安装...
echo =======================================================

rem 检查Python
echo 📋 检查Python版本...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到Python，请先安装Python 3.8或更高版本
    echo 💡 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

rem 检查pip
echo 📋 检查pip...
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到pip，请重新安装Python并勾选pip选项
    pause
    exit /b 1
)

rem 升级pip
echo ⬆️ 升级pip到最新版本...
python -m pip install --upgrade pip

rem 安装核心依赖
echo 📦 安装核心依赖包...
if exist requirements-minimal.txt (
    python -m pip install -r requirements-minimal.txt
    echo ✅ 核心依赖安装完成
) else (
    echo 📦 手动安装核心依赖...
    python -m pip install flask flask-cors flask-limiter aiohttp pyyaml requests python-dateutil cryptography
    echo ✅ 核心依赖安装完成
)

rem 创建必要目录
echo 📁 创建必要目录...
if not exist data mkdir data
if not exist logs mkdir logs  
if not exist config mkdir config
if not exist reports mkdir reports

rem 检查安装结果
echo.
echo 🧪 检查安装结果...
echo ------------------------------------------------------

python -c "import flask; print('✅ flask - 已安装')" 2>nul || echo ❌ flask - 安装失败
python -c "import aiohttp; print('✅ aiohttp - 已安装')" 2>nul || echo ❌ aiohttp - 安装失败  
python -c "import yaml; print('✅ yaml - 已安装')" 2>nul || echo ❌ yaml - 安装失败
python -c "import requests; print('✅ requests - 已安装')" 2>nul || echo ❌ requests - 安装失败
python -c "import cryptography; print('✅ cryptography - 已安装')" 2>nul || echo ❌ cryptography - 安装失败

echo.
echo 🎉 安装完成！
echo =======================================================
echo.
echo 🚀 快速开始:
echo    # Web界面 (推荐)
echo    python launcher.py --mode web
echo    # 然后访问: http://localhost:5000
echo.
echo    # 快速分析  
echo    python quick_analyzer.py
echo.
echo    # 完整演示
echo    python launcher.py --mode full
echo.
echo 📚 更多帮助:
echo    • 查看 README.md 了解详细使用方法
echo    • 查看 WEB_GUIDE.md 了解Web界面使用
echo.
echo 🎯 现在就可以开始分析你的应用合规性了！
echo =======================================================
pause