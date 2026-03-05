#!/usr/bin/env python3
"""
Web界面启动器
Web Interface Launcher

快速启动可视化Web界面的专用脚本
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from api.compliance_api import run_api_server
    
    print("🌐 启动合规系统Web界面...")
    print("=" * 50)
    print("📍 访问地址:")
    print("   • 主界面: http://localhost:8080")
    print("   • API文档: http://localhost:8080/docs") 
    print("   • 演示仪表板: http://localhost:8080/demo")
    print("=" * 50)
    print("💡 使用说明:")
    print("   1. 在主界面填写应用信息")
    print("   2. 点击'开始智能合规分析'")
    print("   3. 查看详细的合规分析报告")
    print("   4. 获取完整的解决方案代码")
    print("=" * 50)
    
    # 启动服务器
    run_api_server(host='0.0.0.0', port=8080, debug=True)
    
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    print("请确保安装了必要的依赖:")
    print("pip install flask flask-cors flask-limiter")
    sys.exit(1)
    
except Exception as e:
    print(f"❌ 启动失败: {e}")
    sys.exit(1)