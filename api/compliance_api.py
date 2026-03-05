#!/usr/bin/env python3
"""
合规API服务器
Compliance API Server

功能：
- RESTful API接口
- WebSocket实时分析
- 批量分析支持
- API认证和授权
- 速率限制
- 缓存和性能优化
"""

from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any
import os
import threading
from functools import wraps

from .advanced_rule_engine import AdvancedRuleEngine
from .compliance_visualizer import ComplianceVisualizationEngine

app = Flask(__name__)
CORS(app)

# 配置速率限制
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["100 per hour"]
)

# 全局实例
rule_engine = AdvancedRuleEngine()
visualizer = ComplianceVisualizationEngine()

# API认证装饰器
def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key or not validate_api_key(api_key):
            return jsonify({'error': 'Invalid or missing API key'}), 401
        return f(*args, **kwargs)
    return decorated_function

def validate_api_key(api_key: str) -> bool:
    """验证API密钥"""
    # 这里可以实现更复杂的验证逻辑
    valid_keys = os.getenv('COMPLIANCE_API_KEYS', '').split(',')
    return api_key in valid_keys or api_key == 'demo-key-for-testing'

# API路由定义

@app.route('/api/v1/health', methods=['GET'])
def health_check():
    """健康检查端点"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '2.0.0',
        'rules_version': rule_engine.rules_version
    })

@app.route('/api/v1/compliance/analyze', methods=['POST'])
@limiter.limit("10 per minute")
@require_api_key
def analyze_compliance():
    """合规分析API"""
    try:
        # 获取请求数据
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        app_profile = data.get('app_profile', {})
        options = data.get('options', {})
        
        # 验证必需字段
        required_fields = ['name', 'app_type', 'target_markets']
        missing_fields = [field for field in required_fields if field not in app_profile]
        
        if missing_fields:
            return jsonify({
                'error': 'Missing required fields',
                'missing_fields': missing_fields
            }), 400
        
        # 异步执行分析
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            results = loop.run_until_complete(
                rule_engine.analyze_compliance_async(app_profile)
            )
        finally:
            loop.close()
        
        # 根据选项定制输出
        output_format = options.get('format', 'json')
        
        if output_format == 'summary':
            # 返回简化摘要
            return jsonify({
                'app_name': app_profile.get('name'),
                'risk_level': results.get('risk_assessment', {}).get('risk_level'),
                'critical_issues': results.get('risk_assessment', {}).get('critical_issues', 0),
                'recommendations_count': len(results.get('recommendations', [])),
                'analysis_timestamp': results.get('timestamp')
            })
        
        elif output_format == 'detailed':
            # 返回完整结果
            return jsonify(results)
        
        else:
            # 默认返回标准格式
            return jsonify({
                'status': 'success',
                'results': results,
                'api_version': '1.0'
            })
        
    except Exception as e:
        app.logger.error(f"Analysis error: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@app.route('/api/v1/compliance/batch', methods=['POST'])
@limiter.limit("5 per minute")  
@require_api_key
def batch_analyze():
    """批量分析API"""
    try:
        data = request.get_json()
        app_profiles = data.get('app_profiles', [])
        
        if not app_profiles or not isinstance(app_profiles, list):
            return jsonify({'error': 'app_profiles must be a non-empty list'}), 400
        
        if len(app_profiles) > 10:
            return jsonify({'error': 'Maximum 10 apps per batch'}), 400
        
        # 并行执行批量分析
        def analyze_single_app(app_profile):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(
                    rule_engine.analyze_compliance_async(app_profile)
                )
            finally:
                loop.close()
        
        batch_results = []
        for app_profile in app_profiles:
            try:
                result = analyze_single_app(app_profile)
                batch_results.append({
                    'app_name': app_profile.get('name'),
                    'status': 'success',
                    'results': result
                })
            except Exception as e:
                batch_results.append({
                    'app_name': app_profile.get('name'),
                    'status': 'error',
                    'error': str(e)
                })
        
        return jsonify({
            'batch_id': f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'total_apps': len(app_profiles),
            'successful': len([r for r in batch_results if r['status'] == 'success']),
            'failed': len([r for r in batch_results if r['status'] == 'error']),
            'results': batch_results
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/dashboard/<app_id>', methods=['GET'])
@require_api_key  
def get_dashboard(app_id: str):
    """获取仪表板HTML"""
    try:
        # 从数据库获取最新的分析结果
        # 这里简化处理，实际需要从数据库查询
        
        # 模拟数据
        results = {
            'app_profile': {'name': app_id},
            'risk_assessment': {'risk_level': 'medium', 'overall_score': 150},
            'compliance_results': []
        }
        
        dashboard_html = visualizer.generate_dashboard(results)
        
        return dashboard_html, 200, {'Content-Type': 'text/html; charset=utf-8'}
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/rules/update', methods=['POST'])
@require_api_key
def update_rules():
    """更新规则API"""
    try:
        # 检查并更新规则
        has_updates = rule_engine.check_for_rule_updates()
        
        if has_updates:
            rule_engine.reload_rules()
            return jsonify({
                'status': 'updated',
                'new_rules_version': rule_engine.rules_version,
                'message': 'Rules successfully updated'
            })
        else:
            return jsonify({
                'status': 'no_updates',
                'current_version': rule_engine.rules_version,
                'message': 'Rules are already up to date'
            })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/templates', methods=['GET'])
def get_code_templates():
    """获取代码模板列表"""
    templates = {
        'coppa_parental_consent': {
            'name': 'COPPA家长同意验证',
            'language': 'Python',
            'description': '实现COPPA要求的可验证家长同意机制',
            'complexity': 'High',
            'estimated_implementation': '2-4 weeks'
        },
        'china_realname_auth': {
            'name': '中国实名认证系统',
            'language': 'Python',
            'description': '对接国家新闻出版署实名认证系统',
            'complexity': 'Very High',
            'estimated_implementation': '4-8 weeks'
        },
        'gdpr_data_subject_rights': {
            'name': 'GDPR数据主体权利',
            'language': 'Python/REST API',
            'description': '实现访问、更正、删除等GDPR权利',
            'complexity': 'High',
            'estimated_implementation': '3-6 weeks'
        }
    }
    
    return jsonify({
        'available_templates': templates,
        'total_count': len(templates)
    })

@app.route('/api/v1/templates/<template_id>', methods=['GET'])
@require_api_key
def get_code_template(template_id: str):
    """获取具体的代码模板"""
    try:
        template_path = Path(__file__).parent.parent / "templates" / f"{template_id}.py"
        
        if template_path.exists():
            with open(template_path, 'r', encoding='utf-8') as f:
                template_code = f.read()
            
            return jsonify({
                'template_id': template_id,
                'code': template_code,
                'language': 'python',
                'usage_instructions': f'Please see comments in the code for implementation details'
            })
        else:
            return jsonify({'error': 'Template not found'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/market-intelligence', methods=['GET'])
def get_market_intelligence():
    """获取市场监管情报"""
    intelligence = {
        'regulatory_updates': [
            {
                'region': 'China',
                'law': '游戏防沉迷规定',
                'update_date': '2025-12-15',
                'impact_level': 'high',
                'summary': '进一步收紧未成年人游戏时间限制',
                'action_required': True
            },
            {
                'region': 'EU', 
                'law': 'AI Act',
                'update_date': '2025-08-01',
                'impact_level': 'medium',
                'summary': 'AI系统分类和风险评估要求',
                'action_required': True
            }
        ],
        'enforcement_trends': {
            'GDPR': {
                'total_fines_2025': '€1.2 billion',
                'average_fine': '€8.2 million', 
                'common_violations': ['lack_of_consent', 'inadequate_security', 'data_breach_notification']
            },
            'COPPA': {
                'total_fines_2025': '$180 million',
                'recent_cases': ['TikTok settlement', 'YouTube Kids fine'],
                'enforcement_focus': ['age_verification', 'parental_consent', 'data_minimization']
            }
        },
        'emerging_regulations': [
            {
                'name': 'US Federal Privacy Law',
                'expected_date': '2026-2027',
                'probability': 0.6,
                'impact': 'May supersede state privacy laws'
            },
            {
                'name': 'China AI Law',
                'expected_date': '2026',
                'probability': 0.8,
                'impact': 'New requirements for AI in education'
            }
        ]
    }
    
    return jsonify(intelligence)

@app.route('/api/v1/compliance/quick-check', methods=['POST'])
@limiter.limit("30 per minute")
def quick_compliance_check():
    """快速合规检查 - 无需API key"""
    try:
        data = request.get_json()
        
        # 简化的检查逻辑
        app_type = data.get('app_type', '')
        min_age = data.get('min_user_age', 18)
        target_markets = data.get('target_markets', [])
        
        quick_assessment = {
            'risk_level': 'low',
            'critical_risks': [],
            'key_requirements': [],
            'estimated_compliance_time': '1-4 weeks',
            'next_steps': ['Get detailed analysis with API key']
        }
        
        # 快速风险识别
        if min_age < 13 and 'US' in target_markets:
            quick_assessment['critical_risks'].append('COPPA compliance required')
            quick_assessment['risk_level'] = 'high'
        
        if 'China' in target_markets and 'Gaming' in app_type and min_age < 18:
            quick_assessment['critical_risks'].append('China anti-addiction system required')
            quick_assessment['risk_level'] = 'critical'
        
        if len(target_markets) > 3:
            quick_assessment['key_requirements'].append('Multi-jurisdiction privacy compliance')
        
        return jsonify({
            'quick_assessment': quick_assessment,
            'disclaimer': 'This is a preliminary assessment. Get detailed analysis with your API key.',
            'upgrade_to_full_analysis': '/api/v1/compliance/analyze'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/docs')
def api_documentation():
    """API文档"""
    docs_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Compliance API Documentation</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container mt-5">
            <h1>🎮📚 教育游戏合规API文档</h1>
            
            <div class="alert alert-info">
                <strong>Base URL:</strong> <code>https://your-domain.com/api/v1</code><br>
                <strong>认证方式:</strong> Header中添加 <code>X-API-Key: your-api-key</code>
            </div>
            
            <h2>端点列表</h2>
            
            <div class="card mb-3">
                <div class="card-header">
                    <code>POST /compliance/analyze</code>
                </div>
                <div class="card-body">
                    <p><strong>功能:</strong> 完整的合规分析</p>
                    <p><strong>认证:</strong> 需要API Key</p>
                    <p><strong>速率限制:</strong> 10次/分钟</p>
                    
                    <h6>请求示例:</h6>
                    <pre><code>{
  "app_profile": {
    "name": "Math Learning Game",
    "app_type": "Educational Gaming",
    "min_user_age": 8,
    "target_markets": ["US", "China"],
    "has_multiplayer": true,
    "has_in_app_purchases": true,
    "has_parental_controls": false
  },
  "options": {
    "format": "detailed",
    "include_predictions": true
  }
}</code></pre>
                </div>
            </div>
            
            <div class="card mb-3">
                <div class="card-header">
                    <code>POST /compliance/batch</code>
                </div>
                <div class="card-body">
                    <p><strong>功能:</strong> 批量应用分析</p>
                    <p><strong>限制:</strong> 最多10个应用/次</p>
                    <p><strong>速率限制:</strong> 5次/分钟</p>
                </div>
            </div>
            
            <div class="card mb-3">
                <div class="card-header">
                    <code>POST /compliance/quick-check</code>
                </div>
                <div class="card-body">
                    <p><strong>功能:</strong> 快速风险评估</p>
                    <p><strong>认证:</strong> 无需API Key</p>
                    <p><strong>速率限制:</strong> 30次/分钟</p>
                    <p><strong>说明:</strong> 提供基础风险评估，详细分析需要API Key</p>
                </div>
            </div>
            
            <h2>响应格式</h2>
            <div class="card">
                <div class="card-body">
                    <h6>标准响应结构:</h6>
                    <pre><code>{
  "status": "success",
  "results": {
    "app_profile": { ... },
    "risk_assessment": { ... },
    "compliance_results": [ ... ],
    "recommendations": [ ... ],
    "implementation_guide": { ... }
  },
  "api_version": "1.0"
}</code></pre>
                </div>
            </div>
            
            <h2>错误处理</h2>
            <div class="card">
                <div class="card-body">
                    <ul>
                        <li><code>400</code> - 请求参数错误</li>
                        <li><code>401</code> - API Key无效或缺失</li>
                        <li><code>429</code> - 超出速率限制</li>
                        <li><code>500</code> - 服务器内部错误</li>
                    </ul>
                </div>
            </div>
            
        </div>
    </body>
    </html>
    """
    
    return docs_html

@app.route('/demo')
def demo_dashboard():
    """演示仪表板"""
    demo_results = {
        'app_profile': {
            'name': 'Demo Education Game',
            'app_type': 'Educational Gaming',
            'target_age_group': '小学生(6-12岁)',
            'target_markets': ['US', 'China', 'EU']
        },
        'timestamp': datetime.now().isoformat(),
        'rules_version': rule_engine.rules_version,
        'risk_assessment': {
            'risk_level': 'high',
            'overall_score': 280.5,
            'critical_issues': 3,
            'high_issues': 2,
            'medium_issues': 1,
            'low_issues': 0,
            'market_specific_risks': {
                'US': 200.2,
                'China': 350.8,
                'EU': 180.1
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
            }
        ],
        'recommendations': [
            {
                'category': '立即行动',
                'priority': 'critical',
                'title': '暂停产品发布',
                'description': '发现多个严重合规问题'
            }
        ]
    }
    
    dashboard_html = visualizer.generate_dashboard(demo_results)
    return dashboard_html, 200, {'Content-Type': 'text/html; charset=utf-8'}

def run_api_server(host='0.0.0.0', port=5000, debug=False):
    """运行API服务器"""
    print(f"""
🚀 合规API服务器启动中...

📍 服务地址: http://{host}:{port}
📚 API文档: http://{host}:{port}/docs
🎛️ 演示仪表板: http://{host}:{port}/demo

🔑 API认证: Header中添加 X-API-Key
📊 主要端点:
   • POST /api/v1/compliance/analyze - 完整分析
   • POST /api/v1/compliance/batch - 批量分析
   • POST /api/v1/compliance/quick-check - 快速检查
   • GET  /api/v1/dashboard/<app_id> - 可视化仪表板
   
🎯 专业领域: 教育游戏应用全球合规
    """)
    
    # 设置日志
    if not debug:
        logging.getLogger('werkzeug').setLevel(logging.WARNING)
    
    app.run(host=host, port=port, debug=debug)

if __name__ == "__main__":
    # 设置环境变量中的API密钥
    os.environ['COMPLIANCE_API_KEYS'] = 'demo-key-for-testing,production-key-123'
    
    run_api_server(debug=True)