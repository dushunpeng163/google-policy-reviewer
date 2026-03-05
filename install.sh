#!/bin/bash
# 🎮📚 教育游戏应用全球合规专家系统 - 一键安装脚本
# Educational Game Compliance Expert System - Installation Script

echo "🎮📚 教育游戏应用全球合规专家系统 - 开始安装..."
echo "======================================================="

# 检查Python版本
echo "📋 检查Python版本..."
python3 --version || {
    echo "❌ 错误: 未找到Python 3，请先安装Python 3.8或更高版本"
    exit 1
}

# 检查pip
echo "📋 检查pip..."
python3 -m pip --version || {
    echo "❌ 错误: 未找到pip，请先安装pip"
    exit 1
}

# 升级pip
echo "⬆️ 升级pip到最新版本..."
python3 -m pip install --upgrade pip

# 安装核心依赖
echo "📦 安装核心依赖包..."
if [ -f "requirements-minimal.txt" ]; then
    python3 -m pip install -r requirements-minimal.txt
    echo "✅ 核心依赖安装完成"
else
    echo "📦 手动安装核心依赖..."
    python3 -m pip install flask flask-cors flask-limiter aiohttp pyyaml requests python-dateutil cryptography
    echo "✅ 核心依赖安装完成"
fi

# 可选依赖询问
echo ""
echo "🤔 是否安装可选功能依赖? (推荐)"
echo "   • PDF报告导出"
echo "   • Redis缓存支持"
echo "   • PostgreSQL数据库支持"
read -p "安装可选依赖? (y/N): " install_optional

if [[ $install_optional =~ ^[Yy]$ ]]; then
    echo "📦 安装可选依赖..."
    python3 -m pip install reportlab weasyprint redis psycopg2-binary
    echo "✅ 可选依赖安装完成"
fi

# 创建必要目录
echo "📁 创建必要目录..."
mkdir -p data logs config reports

# 检查安装结果
echo ""
echo "🧪 检查安装结果..."
echo "------------------------------------------------------"

# 检查核心包
packages=("flask" "aiohttp" "yaml" "requests" "cryptography")
all_good=true

for package in "${packages[@]}"; do
    if python3 -c "import ${package}" 2>/dev/null; then
        echo "✅ ${package} - 已安装"
    else
        echo "❌ ${package} - 安装失败"
        all_good=false
    fi
done

echo ""

if [ "$all_good" = true ]; then
    echo "🎉 安装成功！"
    echo "======================================================="
    echo ""
    echo "🚀 快速开始:"
    echo "   # Web界面 (推荐)"
    echo "   python3 launcher.py --mode web"
    echo "   # 然后访问: http://localhost:5000"
    echo ""
    echo "   # 快速分析"
    echo "   python3 quick_analyzer.py"
    echo ""
    echo "   # 完整演示"
    echo "   python3 launcher.py --mode full"
    echo ""
    echo "📚 更多帮助:"
    echo "   • 查看 README.md 了解详细使用方法"
    echo "   • 查看 WEB_GUIDE.md 了解Web界面使用"
    echo "   • 访问 http://localhost:5000/docs 查看API文档"
    echo ""
    echo "🎯 现在就可以开始分析你的应用合规性了！"
else
    echo "⚠️ 安装过程中出现问题，请检查错误信息并重试"
    echo ""
    echo "🔧 常见解决方案:"
    echo "   • 确保Python 3.8+版本"
    echo "   • 更新pip: python3 -m pip install --upgrade pip"  
    echo "   • 使用虚拟环境: python3 -m venv venv && source venv/bin/activate"
    echo "   • 手动安装: python3 -m pip install flask flask-cors flask-limiter"
fi

echo "======================================================="