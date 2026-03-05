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
import sys
from datetime import datetime
from typing import Dict, Any, Optional
import os
import threading
from functools import wraps
from pathlib import Path

# 确保项目根目录在 sys.path 中（以脚本方式运行时 api/ 目录会成为 sys.path[0]）
_PROJECT_ROOT = str(Path(__file__).parent.parent)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

try:
    from engines.advanced_rule_engine import AdvancedRuleEngine
    from engines.compliance_visualizer import ComplianceVisualizationEngine
except ImportError as _e1:
    print(f"[WARNING] engines import failed: {_e1}", flush=True)
    # 如果在engines目录中运行，使用相对导入
    try:
        from advanced_rule_engine import AdvancedRuleEngine
        from compliance_visualizer import ComplianceVisualizationEngine
    except ImportError as _e2:
        print(f"[WARNING] fallback import failed: {_e2}", flush=True)
        # 如果都失败，提供简化版本
        class AdvancedRuleEngine:
            def __init__(self):
                self.rules_version = "2.0.0"
            
            async def analyze_compliance_async(self, app_profile):
                return self._generate_mock_analysis(app_profile)
            
            def _generate_mock_analysis(self, app_profile):
                return {
                    'app_profile': app_profile,
                    'risk_assessment': {
                        'risk_level': 'high',
                        'overall_score': 250.0,
                        'critical_issues': 2,
                        'high_issues': 1,
                        'medium_issues': 1,
                        'low_issues': 0
                    },
                    'compliance_results': [
                        {
                            'rule_id': 'demo_rule',
                            'severity': 'critical',
                            'status': 'failed',
                            'message': '这是一个演示分析结果',
                            'requirement': '请部署完整系统获取真实分析',
                            'solution': '参考技术实现模板',
                            'region': 'Global',
                            'remediation_cost': 'TBD',
                            'implementation_time': 'TBD'
                        }
                    ],
                    'recommendations': [
                        {
                            'category': '系统部署',
                            'priority': 'high',
                            'title': '部署完整合规系统',
                            'description': '当前为演示模式，请部署完整的专家引擎'
                        }
                    ],
                    'timestamp': datetime.now().isoformat()
                }
        
        class ComplianceVisualizationEngine:
            def generate_dashboard(self, results):
                return """
                <html>
                <head><title>演示模式</title></head>
                <body style="font-family: Arial; padding: 20px;">
                    <h1>🎮📚 合规分析演示结果</h1>
                    <div style="background: #f0f8ff; padding: 20px; border-radius: 10px;">
                        <h2>当前为演示模式</h2>
                        <p>要获取完整的可视化仪表板，请部署完整的系统组件。</p>
                        <p>演示分析结果:</p>
                        <pre>{}</pre>
                    </div>
                </body>
                </html>
                """.format(json.dumps(results, indent=2, ensure_ascii=False))

app = Flask(__name__)
CORS(app)

# 配置速率限制
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["100 per hour"]
)

# 全局实例
rule_engine = AdvancedRuleEngine()
visualizer = ComplianceVisualizationEngine()

# API认证装饰器
def _build_freshness_warning() -> Optional[Dict]:
    """检查政策数据新鲜度，若有过期规则则返回警告信息"""
    try:
        _monitor_dir = str(Path(__file__).parent.parent)
        if _monitor_dir not in sys.path:
            sys.path.insert(0, _monitor_dir)
        from engines.policy_monitor import load_versions, analyze_freshness
        versions = load_versions()
        if not versions:
            return None
        report = analyze_freshness(versions)
        if report['overall_status'] == 'fresh':
            return None
        outdated_count = report['summary']['potentially_outdated'] + report['summary']['outdated']
        return {
            'status': report['overall_status'],
            'message': (
                f"⚠️ 有 {outdated_count} 条合规规则距上次人工验证已超过 "
                f"{report['staleness_threshold_days']} 天，分析结果可能不反映最新政策。"
                f" 建议查阅 /api/v1/policies/freshness 获取详情。"
            ),
            'outdated_rules_count': outdated_count,
            'freshness_report_url': '/api/v1/policies/freshness',
        }
    except Exception:
        return None


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
        
        # 附加政策新鲜度警告
        freshness_warning = _build_freshness_warning()

        # 根据选项定制输出
        output_format = options.get('format', 'json')
        
        if output_format == 'summary':
            summary = {
                'app_name': app_profile.get('name'),
                'risk_level': results.get('risk_assessment', {}).get('risk_level'),
                'critical_issues': results.get('risk_assessment', {}).get('critical_issues', 0),
                'recommendations_count': len(results.get('recommendations', [])),
                'analysis_timestamp': results.get('timestamp')
            }
            if freshness_warning:
                summary['policy_data_warning'] = freshness_warning
            return jsonify(summary)
        
        elif output_format == 'detailed':
            if freshness_warning:
                results['policy_data_warning'] = freshness_warning
            return jsonify(results)
        
        else:
            response = {
                'status': 'success',
                'results': results,
                'api_version': '1.0'
            }
            if freshness_warning:
                response['policy_data_warning'] = freshness_warning
            return jsonify(response)
        
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

@app.route('/api/v1/rules/update', methods=['GET', 'POST'])
def update_rules():
    """
    GET  - 查询当前规则版本 & 热更新配置（无需 API Key）
    POST - 触发规则热更新检查（无需 API Key，方便 Web UI 调用）
    """
    import os as _os
    remote_url = _os.environ.get("RULES_UPDATE_URL", "").strip()

    if request.method == 'GET':
        return jsonify({
            'current_version': rule_engine.rules_version,
            'rules_file': str(rule_engine.config_path),
            'remote_url_configured': bool(remote_url),
            'remote_url_preview': (remote_url[:40] + '…') if len(remote_url) > 40 else remote_url,
            'hot_reload_support': True,
        })

    # POST：触发检查
    try:
        old_version = rule_engine.rules_version
        has_updates = rule_engine.check_for_rule_updates()

        if has_updates:
            new_version = rule_engine.reload_rules()
            return jsonify({
                'status': 'updated',
                'old_version': old_version,
                'new_version': new_version or rule_engine.rules_version,
                'source': 'remote_url' if remote_url else 'local_file',
                'message': f'规则已热重载：{old_version} → {rule_engine.rules_version}',
            })
        else:
            return jsonify({
                'status': 'no_updates',
                'current_version': rule_engine.rules_version,
                'source': 'remote_url' if remote_url else 'local_file',
                'message': '规则文件无变化，当前版本已是最新',
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

@app.route('/')
def web_interface():
    """Web可视化界面 - 首页"""
    try:
        # 读取Web界面HTML文件
        web_interface_path = Path(__file__).parent.parent / "web_interface.html"
        with open(web_interface_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        return html_content, 200, {'Content-Type': 'text/html; charset=utf-8'}
        
    except FileNotFoundError:
        return """
        <html>
        <body style="font-family: Arial; text-align: center; padding: 50px;">
            <h1>🎮📚 教育游戏应用全球合规专家系统</h1>
            <p>Web界面文件未找到。请确保 web_interface.html 文件存在。</p>
            <p><a href="/docs">查看API文档</a> | <a href="/demo">演示仪表板</a></p>
        </body>
        </html>
        """, 200, {'Content-Type': 'text/html; charset=utf-8'}

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

@app.route('/api/v1/compliance/generate-templates', methods=['POST'])
def generate_code_templates():
    """
    根据 App 功能和目标平台生成合规代码模板（Swift / Kotlin / Unity C#）
    请求体：
      {
        "features": ["iap", "att", "kids", "social_login", "privacy", "account_deletion"],
        "platforms": ["ios", "android", "unity"],
        "min_user_age": 6
      }
    """
    try:
        data = request.get_json() or {}
        features = data.get('features', ['iap', 'privacy', 'account_deletion'])
        platforms = data.get('platforms', ['ios', 'android', 'unity'])
        min_user_age = data.get('min_user_age', 18)

        _gen_dir = str(Path(__file__).parent.parent)
        if _gen_dir not in sys.path:
            sys.path.insert(0, _gen_dir)
        from engines.code_template_generator import generate_templates

        result = generate_templates(
            features=features,
            platforms=platforms,
            min_user_age=min_user_age,
        )
        return jsonify({'status': 'success', 'data': result})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/v1/compliance/scan-project', methods=['POST'])
def scan_existing_project():
    """
    静态扫描本地项目目录，检测合规缺项（iOS / Android / Unity）
    请求体：
      { "project_path": "/path/to/your/project" }
    注意：project_path 必须是运行此 API 服务器的机器上的本地路径
    """
    try:
        data = request.get_json() or {}
        project_path = data.get('project_path', '')
        if not project_path:
            return jsonify({'status': 'error', 'message': 'project_path 不能为空'}), 400

        _scan_dir = str(Path(__file__).parent.parent)
        if _scan_dir not in sys.path:
            sys.path.insert(0, _scan_dir)
        from engines.code_scanner import scan_project

        report = scan_project(project_path)
        if 'error' in report:
            return jsonify({'status': 'error', 'message': report['error']}), 400

        return jsonify({'status': 'success', 'data': report})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/v1/guide/new-game', methods=['POST'])
def guide_new_game():
    """Mode A：生成 Unity 游戏合规开发向导（路线图 + 代码模板 + 平台清单 + 法规要点）"""
    try:
        data = request.get_json() or {}
        _root = str(Path(__file__).parent.parent)
        if _root not in sys.path:
            sys.path.insert(0, _root)
        from engines.dev_guide import generate_dev_guide
        result = generate_dev_guide(
            game_name=data.get('game_name', 'My Unity Game'),
            game_type=data.get('game_type', 'casual'),
            features=data.get('features', []),
            min_user_age=data.get('min_user_age', 13),
            target_markets=data.get('target_markets', ['US', 'EU']),
            target_platforms=data.get('target_platforms', ['ios', 'android']),
        )
        # 保存到审计历史
        try:
            roadmap = result.get('roadmap', {})
            total_tasks = sum(len(phase.get('tasks', [])) for phase in roadmap.get('phases', []))
            _save_audit_history({
                'mode': 'guide',
                'scanned_at': datetime.now().isoformat(),
                'game_name': data.get('game_name', 'My Unity Game'),
                'project_path': '',
                'target_markets': data.get('target_markets', []),
                'target_platforms': data.get('target_platforms', []),
                'total_findings': total_tasks,
                'critical': 0,
                'high': 0,
                'medium': 0,
                'low': 0,
                'risk_level': 'guide',
            })
        except Exception:
            pass
        return jsonify({'status': 'success', 'data': result})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


def _load_dotenv():
    """加载项目根目录的 .env 文件到 os.environ（无需 python-dotenv）"""
    env_file = Path(__file__).parent.parent / ".env"
    if not env_file.exists():
        return
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        if key and val:
            os.environ[key] = val

# 启动时加载 .env
_load_dotenv()

# ── 审计历史 ─────────────────────────────────────────────────────────────────

_ROOT = Path(__file__).parent.parent
_AUDIT_HISTORY_FILE = _ROOT / "data" / "audit_history.jsonl"
_AUDIT_HISTORY_FILE.parent.mkdir(exist_ok=True)


def _save_audit_history(entry: dict) -> None:
    """追加一条审计记录到 JSONL 文件"""
    with open(_AUDIT_HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def _load_audit_history(limit: int = 50) -> list:
    """读取最近 limit 条审计记录（最新在前）"""
    if not _AUDIT_HISTORY_FILE.exists():
        return []
    lines = _AUDIT_HISTORY_FILE.read_text(encoding="utf-8").strip().splitlines()
    records = []
    for line in reversed(lines[-limit:]):
        try:
            records.append(json.loads(line))
        except Exception:
            pass
    return records


@app.route('/api/v1/audit/history', methods=['GET'])
def audit_history():
    """返回最近 50 条审计历史记录"""
    limit = min(int(request.args.get('limit', 50)), 200)
    return jsonify({'history': _load_audit_history(limit)})


# ── 通知系统 ─────────────────────────────────────────────────────────────────

_notification_store: list = []          # 内存中的未读通知列表
_notification_lock = threading.Lock()


def _push_notification(msg: str, level: str = "warning", source: str = "") -> None:
    with _notification_lock:
        _notification_store.append({
            "id": len(_notification_store),
            "message": msg,
            "level": level,      # info / warning / critical
            "source": source,
            "created_at": datetime.now().isoformat(),
            "read": False,
        })
        # 最多保留 100 条
        if len(_notification_store) > 100:
            _notification_store.pop(0)


@app.route('/api/v1/notifications', methods=['GET'])
def get_notifications():
    """返回未读通知列表和未读数"""
    with _notification_lock:
        unread = [n for n in _notification_store if not n["read"]]
    return jsonify({"unread_count": len(unread), "notifications": unread})


@app.route('/api/v1/notifications/read', methods=['POST'])
def mark_notifications_read():
    """标记所有通知为已读"""
    with _notification_lock:
        for n in _notification_store:
            n["read"] = True
    return jsonify({"status": "ok"})


# ── 定时监控调度器 ────────────────────────────────────────────────────────────

_scheduler_thread: threading.Thread = None
_scheduler_stop = threading.Event()


def _run_scheduled_check():
    """后台定时检查线程：每隔 POLICY_CHECK_INTERVAL 秒执行一次政策检查"""
    import time as _time
    _root = str(_ROOT)
    if _root not in sys.path:
        sys.path.insert(0, _root)

    interval = int(os.environ.get("POLICY_CHECK_INTERVAL", "3600"))  # 默认1小时
    # 启动后等待 30 秒再首次运行（给服务器初始化留时间）
    _scheduler_stop.wait(30)

    while not _scheduler_stop.is_set():
        try:
            from engines.policy_monitor import (
                load_versions, save_versions, fetch_rss_alerts,
                check_page_changes, save_alerts_log, cache_path_for_url, fetch_page_text
            )
            from engines.policy_diff_analyzer import analyze_policy_diff, apply_analysis_to_versions
            import datetime as _dt

            versions = load_versions()
            all_alerts = []
            versions_dirty = False

            # ── RSS 公告检测 ──────────────────────────────────────────
            rss_alerts = fetch_rss_alerts(verbose=False)
            all_alerts.extend(rss_alerts)

            # ── 页面哈希变化检测 ──────────────────────────────────────
            page_alerts = check_page_changes(versions, verbose=False)
            all_alerts.extend(page_alerts)
            if page_alerts:
                versions_dirty = True

            # ── LLM 分析：自动把受影响规则标为待复核 ─────────────────
            llm_ready = bool(os.environ.get('ANTHROPIC_API_KEY') or os.environ.get('OPENAI_API_KEY'))
            marked_rules_total = 0
            if page_alerts and llm_ready:
                for alert in page_alerts[:3]:
                    url = alert.get('url', '')
                    platform = alert.get('platform', '')
                    cache_file = cache_path_for_url(url)
                    old_text = cache_file.read_text(encoding='utf-8', errors='replace') if cache_file.exists() else ''
                    new_text = fetch_page_text(url) or ''
                    if old_text and new_text:
                        try:
                            analysis = analyze_policy_diff(old_text, new_text, platform, url)
                            if analysis.get('has_policy_change'):
                                apply_res = apply_analysis_to_versions(analysis, versions, platform)
                                marked = apply_res.get('marked', [])
                                marked_rules_total += len(marked)
                                if marked:
                                    versions_dirty = True
                        except Exception:
                            pass

            versions["_meta"]["last_monitor_run"] = _dt.datetime.now().isoformat()
            save_versions(versions)

            if all_alerts:
                save_alerts_log(all_alerts)
                parts = [f"RSS {len(rss_alerts)} 条" if rss_alerts else "",
                         f"页面变化 {len(page_alerts)} 个" if page_alerts else ""]
                detail = "、".join(p for p in parts if p)
                if marked_rules_total:
                    detail += f"，{marked_rules_total} 条规则已自动标为待复核"
                msg = f"⚠️ 发现政策变化（{detail}）"
                level = "critical" if page_alerts else "warning"
                _push_notification(msg, level=level, source="scheduler")
            elif not llm_ready and page_alerts:
                _push_notification(
                    "检测到页面变化，但未配置 LLM Key，无法自动分析影响范围。请在「配置」Tab 设置 API Key。",
                    level="warning", source="scheduler"
                )

        except Exception as e:
            _push_notification(f"定时检查出错: {e}", level="info", source="scheduler")

        _scheduler_stop.wait(interval)


def start_scheduler():
    """启动后台定时监控线程"""
    global _scheduler_thread
    if _scheduler_thread and _scheduler_thread.is_alive():
        return
    _scheduler_stop.clear()
    _scheduler_thread = threading.Thread(target=_run_scheduled_check, daemon=True, name="PolicyScheduler")
    _scheduler_thread.start()


@app.route('/api/v1/policies/scheduler', methods=['GET', 'POST'])
def scheduler_control():
    """查询或控制定时监控调度器"""
    if request.method == 'GET':
        alive = _scheduler_thread is not None and _scheduler_thread.is_alive()
        interval = int(os.environ.get("POLICY_CHECK_INTERVAL", "3600"))
        return jsonify({
            "running": alive,
            "interval_seconds": interval,
            "interval_label": _seconds_to_label(interval),
        })
    # POST：更新调度间隔
    data = request.get_json() or {}
    new_interval = data.get("interval_seconds")
    if new_interval:
        os.environ["POLICY_CHECK_INTERVAL"] = str(int(new_interval))
        # 更新 .env 持久化
        env_file = _ROOT / ".env"
        lines = []
        replaced = False
        if env_file.exists():
            for line in env_file.read_text(encoding="utf-8").splitlines():
                if line.startswith("POLICY_CHECK_INTERVAL="):
                    lines.append(f"POLICY_CHECK_INTERVAL={new_interval}")
                    replaced = True
                else:
                    lines.append(line)
        if not replaced:
            lines.append(f"POLICY_CHECK_INTERVAL={new_interval}")
        env_file.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return jsonify({"status": "ok", "interval_seconds": int(os.environ.get("POLICY_CHECK_INTERVAL", "3600"))})


def _seconds_to_label(s: int) -> str:
    if s < 3600:
        return f"{s // 60} 分钟"
    if s < 86400:
        return f"{s // 3600} 小时"
    if s < 604800:
        return f"{s // 86400} 天"
    return f"{s // 604800} 周"


# 启动时自动开启调度器
start_scheduler()


@app.route('/api/v1/policies/save-config', methods=['POST'])
def save_llm_config():
    """保存 LLM API Key 到 .env 文件并即时生效（无需重启服务器）"""
    data = request.get_json() or {}
    env_file = Path(__file__).parent.parent / ".env"

    updates = {}
    if data.get('anthropic_key'):
        updates['ANTHROPIC_API_KEY'] = data['anthropic_key'].strip()
    if data.get('openai_key'):
        updates['OPENAI_API_KEY'] = data['openai_key'].strip()
    if 'rules_update_url' in data:
        updates['RULES_UPDATE_URL'] = data['rules_update_url'].strip()
    # 允许清空某个 key
    if data.get('clear_anthropic'):
        updates['ANTHROPIC_API_KEY'] = ''
    if data.get('clear_openai'):
        updates['OPENAI_API_KEY'] = ''
    if data.get('clear_rules_url'):
        updates['RULES_UPDATE_URL'] = ''

    if not updates:
        return jsonify({'status': 'error', 'message': '未提供任何配置项'}), 400

    # 读取现有 .env
    existing = {}
    if env_file.exists():
        for line in env_file.read_text(encoding='utf-8').splitlines():
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, _, v = line.partition('=')
                existing[k.strip()] = v.strip().strip('"').strip("'")

    # 合并更新
    existing.update(updates)

    # 写回 .env
    lines = [f"# Unity 游戏合规系统配置 - 自动生成，请勿手动修改\n"]
    for k, v in existing.items():
        if v:
            lines.append(f'{k}={v}\n')

    env_file.write_text(''.join(lines), encoding='utf-8')

    # 即时生效（更新当前进程 os.environ）
    for k, v in updates.items():
        if v:
            os.environ[k] = v
        elif k in os.environ:
            del os.environ[k]

    # 返回最新配置状态
    _root = str(Path(__file__).parent.parent)
    if _root not in sys.path:
        sys.path.insert(0, _root)
    from engines.policy_diff_analyzer import check_llm_config
    return jsonify({'status': 'success', 'config': check_llm_config()})


@app.route('/api/v1/policies/run-check', methods=['POST'])
def run_policy_check():
    """
    触发政策检查任务（RSS / 页面哈希 / LLM 分析），实时返回结果。
    请求体：{ "check_type": "rss" | "pages" | "both" }
    """
    data = request.get_json() or {}
    check_type = data.get('check_type', 'both')

    _root = str(Path(__file__).parent.parent)
    if _root not in sys.path:
        sys.path.insert(0, _root)

    from engines.policy_monitor import (
        load_versions, save_versions, fetch_rss_alerts,
        check_page_changes, save_alerts_log, analyze_freshness
    )
    import datetime as _dt

    versions = load_versions()
    results = {
        'check_type': check_type,
        'checked_at': _dt.datetime.now().isoformat(),
        'rss_alerts': [],
        'page_alerts': [],
        'llm_analyses': [],
        'summary': '',
    }

    if check_type in ('rss', 'both'):
        try:
            rss_alerts = fetch_rss_alerts(verbose=False)
            results['rss_alerts'] = rss_alerts
            if rss_alerts:
                save_alerts_log(rss_alerts)
        except Exception as e:
            results['rss_error'] = str(e)

    if check_type in ('pages', 'both'):
        try:
            page_alerts = check_page_changes(versions, verbose=False)
            results['page_alerts'] = page_alerts
            versions['_meta']['last_monitor_run'] = _dt.datetime.now().isoformat()
            save_versions(versions)

            # 如果有页面变化且 LLM 已配置，自动分析并写回规则版本文件
            if page_alerts and (os.environ.get('ANTHROPIC_API_KEY') or os.environ.get('OPENAI_API_KEY')):
                from engines.policy_diff_analyzer import analyze_policy_diff, apply_analysis_to_versions
                from engines.policy_monitor import cache_path_for_url, fetch_page_text

                for alert in page_alerts[:3]:  # 最多分析3个
                    url = alert.get('url', '')
                    platform = alert.get('platform', '')
                    cache_file = cache_path_for_url(url)
                    # 旧内容在 cache 里，新内容重新抓
                    old_text = cache_file.read_text(encoding='utf-8', errors='replace') if cache_file.exists() else ''
                    new_text = fetch_page_text(url) or ''
                    if old_text and new_text:
                        try:
                            analysis = analyze_policy_diff(old_text, new_text, platform, url)
                            results['llm_analyses'].append(analysis)
                            # ← 新增：把受影响规则写回 policy_versions.json
                            if analysis.get('has_policy_change'):
                                apply_res = apply_analysis_to_versions(analysis, versions, platform)
                                analysis['auto_marked_rules'] = apply_res.get('marked', [])
                                if apply_res.get('marked'):
                                    save_versions(versions)
                        except Exception as e:
                            results['llm_analyses'].append({'url': url, 'error': str(e)})

            if page_alerts:
                save_alerts_log(page_alerts)
        except Exception as e:
            results['page_error'] = str(e)

    total = len(results['rss_alerts']) + len(results['page_alerts'])
    if total == 0:
        results['summary'] = '✅ 未发现新变化，所有监控项正常'
    else:
        results['summary'] = f'⚠️ 发现 {total} 个新变化（RSS {len(results["rss_alerts"])} 条，页面 {len(results["page_alerts"])} 个）'

    return jsonify(results)


@app.route('/api/v1/policies/llm-config', methods=['GET'])
def llm_config_status():
    """检查 LLM API Key 配置状态"""
    try:
        _root = str(Path(__file__).parent.parent)
        if _root not in sys.path:
            sys.path.insert(0, _root)
        from engines.policy_diff_analyzer import check_llm_config
        return jsonify(check_llm_config())
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v1/policies/analyze-change', methods=['POST'])
def analyze_policy_change():
    """
    用 LLM 分析政策页面变化。
    请求体：{ "url": "...", "platform": "apple_app_store" }
    会从缓存中读取旧页面，抓取新页面，发给 LLM 分析。
    """
    try:
        data = request.get_json() or {}
        url = data.get('url', '')
        platform = data.get('platform', '')
        if not url:
            return jsonify({'error': 'url 不能为空'}), 400

        _root = str(Path(__file__).parent.parent)
        if _root not in sys.path:
            sys.path.insert(0, _root)
        from engines.policy_monitor import fetch_page_text, cache_path_for_url, sha256_text
        from engines.policy_diff_analyzer import analyze_policy_diff

        cache_file = cache_path_for_url(url)
        old_text = cache_file.read_text(encoding='utf-8', errors='replace') if cache_file.exists() else ''

        new_text = fetch_page_text(url)
        if new_text is None:
            return jsonify({'error': '无法访问该页面，请检查网络连接'}), 502

        if not old_text:
            # 首次抓取，存缓存但无法分析差异
            cache_file.write_text(new_text, encoding='utf-8')
            return jsonify({
                'status': 'first_fetch',
                'message': '首次抓取页面，已存入缓存。下次检查时才能对比差异。',
                'url': url,
            })

        if sha256_text(old_text) == sha256_text(new_text):
            return jsonify({
                'status': 'no_change',
                'message': '页面内容无变化',
                'url': url,
            })

        # 有变化，调 LLM 分析
        result = analyze_policy_diff(old_text, new_text, platform, url)
        cache_file.write_text(new_text, encoding='utf-8')
        return jsonify({'status': 'analyzed', 'data': result})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v1/browse-folder', methods=['GET'])
def browse_folder():
    """打开系统原生文件夹选择对话框，返回所选路径（仅限本地使用）"""
    try:
        import subprocess
        import platform

        system = platform.system()

        if system == 'Darwin':
            # macOS：用 osascript 调起原生 Finder 文件夹选择框
            script = 'tell application "Finder" to POSIX path of (choose folder with prompt "选择 Unity 项目根目录")'
            result = subprocess.run(['osascript', '-e', script],
                                    capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                path = result.stdout.strip()
                # osascript 返回的路径末尾有斜杠，去掉
                path = path.rstrip('/')
                return jsonify({'status': 'success', 'path': path})
            else:
                # 用户取消选择
                return jsonify({'status': 'cancelled', 'path': ''})

        elif system == 'Windows':
            script = (
                'Add-Type -AssemblyName System.Windows.Forms;'
                '$f = New-Object System.Windows.Forms.FolderBrowserDialog;'
                '$f.Description = "选择 Unity 项目根目录";'
                'if ($f.ShowDialog() -eq "OK") { $f.SelectedPath }'
            )
            result = subprocess.run(['powershell', '-Command', script],
                                    capture_output=True, text=True, timeout=60)
            path = result.stdout.strip()
            if path:
                return jsonify({'status': 'success', 'path': path})
            return jsonify({'status': 'cancelled', 'path': ''})

        elif system == 'Linux':
            # 尝试 zenity（GNOME）或 kdialog（KDE）
            for cmd in [['zenity', '--file-selection', '--directory', '--title=选择 Unity 项目目录'],
                        ['kdialog', '--getexistingdirectory', '.']]:
                try:
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                    if result.returncode == 0:
                        return jsonify({'status': 'success', 'path': result.stdout.strip()})
                except FileNotFoundError:
                    continue
            return jsonify({'status': 'error', 'message': '未找到可用的文件夹选择工具（需要 zenity 或 kdialog）'})

        else:
            return jsonify({'status': 'error', 'message': f'不支持的操作系统: {system}'})

    except subprocess.TimeoutExpired:
        return jsonify({'status': 'cancelled', 'path': ''})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})


@app.route('/api/v1/audit/game', methods=['POST'])
def audit_game():
    """Mode B：统一游戏合规审计（平台政策 + 法规 + 代码扫描合并报告）"""
    try:
        data = request.get_json() or {}
        _root = str(Path(__file__).parent.parent)
        if _root not in sys.path:
            sys.path.insert(0, _root)
        from engines.unified_audit import audit_game as _audit
        result = _audit(
            game_info=data.get('game_info', {}),
            project_path=data.get('project_path'),
            target_markets=data.get('target_markets', ['US', 'EU']),
            target_platforms=data.get('target_platforms', ['ios', 'android']),
        )
        # 保存审计历史
        summary = result.get('summary', {})
        _save_audit_history({
            'mode': 'audit',
            'scanned_at': datetime.now().isoformat(),
            'game_name': data.get('game_info', {}).get('name', '未命名'),
            'project_path': data.get('project_path', ''),
            'target_markets': data.get('target_markets', []),
            'target_platforms': data.get('target_platforms', []),
            'total_findings': summary.get('total_findings', 0),
            'critical': summary.get('critical', 0),
            'high': summary.get('high', 0),
            'medium': summary.get('medium', 0),
            'low': summary.get('low', 0),
            'risk_level': summary.get('overall_risk', ''),
        })
        return jsonify({'status': 'success', 'data': result})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/v1/policies/freshness', methods=['GET'])
def policy_freshness():
    """返回所有政策规则的新鲜度报告（无需 API Key）"""
    try:
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from engines.policy_monitor import load_versions, analyze_freshness
        versions = load_versions()
        if not versions:
            return jsonify({'error': 'policy_versions.json 未找到'}), 404
        report = analyze_freshness(versions)
        return jsonify(report)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v1/policies/mark-verified', methods=['POST'])
def mark_rule_verified():
    """人工标记单条规则已复核（清除 change_alert / needs_review，更新 last_verified）"""
    try:
        data = request.get_json() or {}
        platform = data.get('platform', '').strip()
        rule_id  = data.get('rule_id', '').strip()
        if not platform or not rule_id:
            return jsonify({'error': '缺少 platform 或 rule_id'}), 400

        from engines.policy_monitor import load_versions, save_versions
        from datetime import date
        versions = load_versions()

        platform_data = versions.get(platform, {})
        rules = platform_data.get('rules', {})
        if rule_id not in rules:
            return jsonify({'error': f'规则 {rule_id} 不存在于 {platform}'}), 404

        rule = rules[rule_id]
        today = date.today().isoformat()
        rule['last_verified'] = today
        rule['verified_by']   = 'manual_ui'
        rule.pop('change_alert', None)
        rule.pop('needs_review', None)

        save_versions(versions)
        return jsonify({'ok': True, 'rule_id': rule_id, 'platform': platform, 'last_verified': today})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v1/compliance/platform-matrix', methods=['POST'])
def platform_engineering_matrix():
    """跨平台工程合规矩阵 - 返回 iOS/Android 各自需要实现的具体工程项"""
    data = request.get_json() or {}

    features = data.get('features', [])   # e.g. ['iap','ads','kids','social_login','location']
    app_type = data.get('app_type', 'general')
    target_ages = data.get('target_ages', [18])

    min_age = min(target_ages) if target_ages else 18
    has_kids = min_age < 13
    has_iap = 'iap' in features
    has_ads = 'ads' in features
    has_social_login = 'social_login' in features
    has_location = 'location' in features
    has_ugc = 'ugc' in features
    has_analytics = 'analytics' in features

    # ── iOS 工程项 ──────────────────────────────────────────────────
    ios_items = []

    if has_iap:
        ios_items.append({
            'category': '应用内购买',
            'priority': 'critical',
            'guideline': 'App Store 3.1.1',
            'what': '所有虚拟商品/订阅必须使用 StoreKit',
            'how': 'import StoreKit; Product.purchase() / Transaction.updates 监听',
            'server_side': '苹果收据验证：POST https://buy.itunes.apple.com/verifyReceipt',
            'pitfall': '不得绕过 IAP 提供替代支付（包括引导用户到网页购买）'
        })

    ios_items.append({
        'category': '隐私追踪授权 ATT',
        'priority': 'critical',
        'guideline': 'App Store 5.1.2 / iOS 14.5+',
        'what': '使用 IDFA 或跨 App 追踪前必须请求用户授权',
        'how': 'ATTrackingManager.requestTrackingAuthorization(completionHandler:)',
        'server_side': '服务端须区分已授权/未授权用户，未授权时不得传 IDFA',
        'pitfall': '弹出 ATT 前可先展示自定义预热页提升同意率；儿童 App 禁止弹出'
    })

    ios_items.append({
        'category': '账户删除',
        'priority': 'critical',
        'guideline': 'App Store 5.1.1(v)，2022年6月起强制',
        'what': 'App 内必须提供账户删除入口（不只是注销）',
        'how': '设置页 → "删除账户" → 二次确认 → 调用后端 DELETE /api/user → 30天内彻底删除',
        'server_side': '同步删除所有关联数据（含第三方服务）；保留法务必要数据需说明',
        'pitfall': '账户删除≠注销；Apple 审核会专门测试此流程'
    })

    if has_social_login:
        ios_items.append({
            'category': 'Sign in with Apple',
            'priority': 'critical',
            'guideline': 'App Store 4.8',
            'what': '提供任何第三方登录时，必须同时提供 Sign in with Apple',
            'how': 'ASAuthorizationAppleIDProvider + ASAuthorizationController',
            'server_side': '后端用 Apple 公钥验证 identity_token（JWT）；处理 email relay 隐藏邮箱',
            'pitfall': '游戏中心登录不触发此要求；但 Google/Facebook 登录会触发'
        })

    if has_kids:
        ios_items.append({
            'category': '儿童类别合规',
            'priority': 'critical',
            'guideline': 'App Store 1.3',
            'what': '家长门控、禁止行为追踪广告、禁止外部链接',
            'how': '所有外部跳转前显示"家长门控"（随机数学题/复杂操作）；广告 SDK 启用儿童模式',
            'server_side': 'COPPA：13岁以下用户不采集可识别个人信息',
            'pitfall': '第三方 SDK（含分析/广告）须是 Apple 批准的 Families 适用版本'
        })

    if has_ads:
        ios_items.append({
            'category': '广告 SDK 配置',
            'priority': 'high',
            'guideline': 'App Store 1.3 / COPPA',
            'what': '儿童用户禁止个性化广告',
            'how': 'GADMobileAds.sharedInstance().requestConfiguration.tagForChildDirectedTreatment = true',
            'server_side': '请求广告时传 tag_for_child_directed_treatment=1',
            'pitfall': '全屏插屏广告在儿童 App 中完全禁止'
        })

    if has_location:
        ios_items.append({
            'category': '位置权限',
            'priority': 'high',
            'guideline': 'App Store 5.1.1',
            'what': 'Info.plist 声明用途字符串，仅在需要时请求',
            'how': 'NSLocationWhenInUseUsageDescription（前台）\nNSLocationAlwaysAndWhenInUseUsageDescription（后台，须充分理由）',
            'server_side': '无',
            'pitfall': '"始终允许"权限在审核中须演示真实后台使用场景'
        })

    ios_items.append({
        'category': '隐私营养标签',
        'priority': 'high',
        'guideline': 'App Store Connect 必填',
        'what': '上架前在 App Store Connect 填写数据收集声明',
        'how': '登录 App Store Connect → App 隐私 → 按数据类型（位置/联系方式/标识符等）逐项声明',
        'server_side': '声明须与代码实际行为完全一致，Apple 随机抽查',
        'pitfall': '第三方 SDK 采集的数据也须在此声明'
    })

    # ── Android 工程项 ──────────────────────────────────────────────
    android_items = []

    if has_iap:
        android_items.append({
            'category': '应用内购买',
            'priority': 'critical',
            'guideline': 'Google Play 结算政策',
            'what': '所有数字商品必须使用 Google Play Billing Library',
            'how': 'implementation "com.android.billingclient:billing-ktx:6.x"\nBillingClient → launchBillingFlow() → PurchasesUpdatedListener',
            'server_side': 'Google Play Developer API 验证购买令牌：GET purchases.products.get',
            'pitfall': '不允许引导用户到外部网页购买（违规会下架）；实物商品无需走 Play Billing'
        })

    android_items.append({
        'category': 'Target API Level',
        'priority': 'critical',
        'guideline': 'Google Play Target API 要求',
        'what': '新应用须 targetSdkVersion ≥ 35（2025年要求）',
        'how': 'build.gradle: targetSdkVersion 35\n同步更新 compileSdkVersion',
        'server_side': '无',
        'pitfall': '升级 targetSdk 后须全面测试权限、通知、后台限制等行为变化'
    })

    android_items.append({
        'category': '账户删除',
        'priority': 'critical',
        'guideline': 'Google Play 账户删除政策，2024年5月强制',
        'what': 'App 内提供删除入口，且必须提供网页版删除链接（供卸载后使用）',
        'how': '应用内：设置 → 删除账户 → 调用后端 API\n网页：公开可访问的账户删除页（在 Play Console 填写 URL）',
        'server_side': '彻底删除数据；在 Play Console 的"应用内容"填写网页删除链接',
        'pitfall': '比 iOS 多一个网页删除链接要求，且需在 Play Console 填写'
    })

    android_items.append({
        'category': '数据安全表单',
        'priority': 'critical',
        'guideline': 'Google Play 数据安全政策',
        'what': 'Play Console 必须填写数据采集、共享、安全实践声明',
        'how': 'Play Console → 应用内容 → 数据安全 → 按数据类型填写',
        'server_side': '与实际代码行为保持一致；第三方 SDK 数据也须包含',
        'pitfall': '与 iOS 的"隐私营养标签"类似但表单字段不同，需分别填写'
    })

    android_items.append({
        'category': '隐私政策',
        'priority': 'critical',
        'guideline': 'Google Play 用户数据政策',
        'what': '必须提供公开可访问的隐私政策 URL',
        'how': 'Play Console → 商店设置 → 隐私权政策；App 内也须提供入口',
        'server_side': '隐私政策页须 HTTPS、无登录门控、始终可访问',
        'pitfall': '隐私政策须涵盖所有第三方 SDK 的数据行为'
    })

    if has_location:
        android_items.append({
            'category': '位置权限',
            'priority': 'critical',
            'guideline': 'Google Play 位置权限政策',
            'what': 'AndroidManifest 声明，后台位置须额外申请且须充分理由',
            'how': 'ACCESS_FINE_LOCATION（前台）\nACCESS_BACKGROUND_LOCATION（后台，Android 10+须单独请求）',
            'server_side': '无',
            'pitfall': '后台位置仅限导航/家庭安全等合理场景；需向 Google 提交说明表单'
        })

    android_items.append({
        'category': 'IARC 内容分级',
        'priority': 'high',
        'guideline': 'Google Play 内容分级政策',
        'what': '所有新应用必须完成 IARC 内容分级问卷',
        'how': 'Play Console → 应用内容 → 内容分级 → 完成问卷获取分级',
        'server_side': '无',
        'pitfall': '与 iOS 的年龄分级问卷独立，需分别完成；问卷答案须与实际内容一致'
    })

    if has_ads:
        android_items.append({
            'category': '广告 SDK 配置',
            'priority': 'high',
            'guideline': 'Google Play 广告政策 / COPPA',
            'what': '儿童用户禁止个性化广告',
            'how': 'RequestConfiguration.Builder().setTagForChildDirectedTreatment(TAG_FOR_CHILD_DIRECTED_TREATMENT_TRUE)\n全屏插屏广告须有 X 关闭按钮（≥5秒后可关）',
            'server_side': '广告请求添加 tag_for_child_directed_treatment=1',
            'pitfall': '模拟系统 UI 的广告（如伪造通知栏）违规；全屏插屏不能在游戏关卡加载时弹出'
        })

    if has_ugc:
        android_items.append({
            'category': '用户生成内容 (UGC)',
            'priority': 'high',
            'guideline': 'Google Play 用户生成内容政策',
            'what': '须有内容审核机制和举报功能',
            'how': '实现举报按钮（每条 UGC 旁）；后台审核队列；AI 预过滤',
            'server_side': '保留内容审核日志；响应举报须有 SLA',
            'pitfall': 'iOS App Store 无此专项要求（但同样不允许违规内容）'
        })

    android_items.append({
        'category': 'Android App Bundle',
        'priority': 'medium',
        'guideline': 'Google Play 技术要求，2021年8月起强制',
        'what': '新应用须上传 .aab 而非 .apk',
        'how': 'Android Studio: Build → Generate Signed Bundle/APK → Android App Bundle',
        'server_side': '无',
        'pitfall': 'iOS 对应无需操作（iOS 本身就是类似机制）'
    })

    if has_kids:
        android_items.append({
            'category': '儿童家庭政策',
            'priority': 'critical',
            'guideline': 'Google Play 家庭政策',
            'what': '面向儿童 App 须遵守家庭政策；广告 SDK 须在 Families Approved 列表内',
            'how': 'Play Console → 应用内容 → 目标受众 → 选儿童年龄段\n仅使用 Google 认证的儿童友好广告 SDK',
            'server_side': 'COPPA/COPPA 等效合规',
            'pitfall': '用了未经认证的 SDK（如某些分析 SDK）会导致下架'
        })

    # ── 共同需要的工程项 ────────────────────────────────────────────
    shared_items = []

    if has_iap:
        shared_items.append({
            'category': '收据/订单验证',
            'what': '两个平台的收据均须在后端服务器验证，不能只在客户端验证',
            'ios': 'POST https://buy.itunes.apple.com/verifyReceipt（沙盒：sandbox.itunes.apple.com）',
            'android': 'Google Play Developer API：purchases.subscriptions.get / purchases.products.get',
            'pitfall': '纯客户端验证易被破解；服务端须幂等处理重复通知'
        })

    shared_items.append({
        'category': '隐私政策与条款',
        'what': '两个平台均要求可公开访问的隐私政策',
        'ios': 'App Store Connect 填写 URL + App 内入口',
        'android': 'Play Console 填写 URL + App 内入口',
        'pitfall': '同一份隐私政策文本须覆盖两个平台的数据行为'
    })

    shared_items.append({
        'category': '账户删除',
        'what': 'App 内删除账户流程',
        'ios': 'App 内入口即可（无需网页版）',
        'android': 'App 内入口 + 公开网页删除链接（在 Play Console 填写）',
        'pitfall': 'Android 比 iOS 多一个网页版要求'
    })

    result = {
        'summary': {
            'total_ios_items': len(ios_items),
            'total_android_items': len(android_items),
            'shared_items': len(shared_items),
            'critical_ios': sum(1 for i in ios_items if i['priority'] == 'critical'),
            'critical_android': sum(1 for i in android_items if i['priority'] == 'critical'),
        },
        'ios_engineering': ios_items,
        'android_engineering': android_items,
        'shared_engineering': shared_items,
        'key_differences': [
            {
                'area': '追踪授权',
                'ios': 'ATT 弹窗强制（iOS 14.5+），儿童 App 完全禁止',
                'android': 'Privacy Sandbox 逐步推进，目前 Advertising ID 仍可访问'
            },
            {
                'area': '登录要求',
                'ios': '有第三方登录必须同时提供 Sign in with Apple',
                'android': '推荐 Google Sign-In，无强制第三方登录要求'
            },
            {
                'area': '安装包格式',
                'ios': 'Xcode 自动处理，上传 .ipa',
                'android': '2021年后必须上传 .aab（非 .apk）'
            },
            {
                'area': '账户删除',
                'ios': 'App 内入口即可',
                'android': 'App 内 + 网页版（卸载后仍可使用）'
            },
            {
                'area': '儿童 SDK 审核',
                'ios': 'Apple 无官方 Parental Gate SDK，需自实现数学题验证',
                'android': 'Google Play 提供 Families Approved SDK 列表，须从中选用'
            },
            {
                'area': 'UGC 政策',
                'ios': '无专项 UGC 审核要求（违规内容不允许）',
                'android': '有明确 UGC 政策，须实现举报+审核机制'
            }
        ]
    }

    return jsonify(result)


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
   • POST /api/v1/compliance/platform-matrix - 跨平台工程合规矩阵
   • POST /api/v1/compliance/generate-templates - 生成 Swift/Kotlin/Unity 合规代码模板
   • POST /api/v1/compliance/scan-project - 扫描现有项目合规缺项
   • GET  /api/v1/policies/freshness - 政策规则新鲜度报告
   • GET  /api/v1/dashboard/<app_id> - 可视化仪表板
   
🎯 专业领域: 教育游戏应用全球合规
    """)
    
    # 设置日志
    if not debug:
        logging.getLogger('werkzeug').setLevel(logging.WARNING)
    
    app.run(host=host, port=port, debug=debug)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='0.0.0.0')
    parser.add_argument('--port', type=int, default=8080)
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()

    os.environ['COMPLIANCE_API_KEYS'] = 'demo-key-for-testing,production-key-123'
    run_api_server(host=args.host, port=args.port, debug=args.debug)
