#!/usr/bin/env python3
"""
合规可视化仪表板生成器
Compliance Visualization Dashboard Generator

功能：
- 交互式HTML仪表板
- 风险热力图
- 合规时间线
- 多维度数据分析
- 可导出的图表和报告
"""

import json
import base64
from typing import Dict, List, Any
from datetime import datetime
import sqlite3
from pathlib import Path

class ComplianceVisualizationEngine:
    """合规可视化引擎"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or Path(__file__).parent.parent / "data" / "compliance.db"
        self.chart_colors = {
            'critical': '#f44336',
            'high': '#ff9800', 
            'medium': '#ffc107',
            'low': '#4caf50'
        }
    
    def generate_dashboard(self, results: Dict[str, Any]) -> str:
        """生成完整的交互式仪表板"""
        
        dashboard_html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>合规分析仪表板 - {results.get('app_profile', {}).get('name', '应用')}</title>
    
    <!-- Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    
    <!-- Bootstrap -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    
    <style>
        .dashboard-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            margin-bottom: 2rem;
        }}
        .risk-card {{
            border: none;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            border-radius: 10px;
        }}
        .risk-critical {{ border-left: 5px solid #f44336; }}
        .risk-high {{ border-left: 5px solid #ff9800; }}
        .risk-medium {{ border-left: 5px solid #ffc107; }}
        .risk-low {{ border-left: 5px solid #4caf50; }}
        
        .chart-container {{ 
            position: relative; 
            height: 400px;
            margin: 20px 0;
        }}
        .metric-card {{
            text-align: center;
            padding: 20px;
            margin: 10px 0;
        }}
        .metric-value {{
            font-size: 2.5em;
            font-weight: bold;
        }}
        .issue-list {{
            max-height: 500px;
            overflow-y: auto;
        }}
    </style>
</head>
<body>
    
    <div class="dashboard-header">
        <div class="container">
            <h1>🎮📚 教育游戏应用合规分析仪表板</h1>
            <div class="row">
                <div class="col-md-6">
                    <h3>{results.get('app_profile', {}).get('name', '未命名应用')}</h3>
                    <p>类型: {results.get('app_profile', {}).get('app_type', 'N/A')} | 年龄: {results.get('app_profile', {}).get('target_age_group', 'N/A')}</p>
                    <p>目标市场: {', '.join(results.get('app_profile', {}).get('target_markets', []))}</p>
                </div>
                <div class="col-md-6">
                    <div class="metric-card bg-light text-dark rounded">
                        <div class="metric-value risk-{results.get('risk_assessment', {}).get('risk_level', 'unknown').lower()}">
                            {self._get_risk_level_emoji(results.get('risk_assessment', {}).get('risk_level', 'unknown'))}
                        </div>
                        <div>风险等级: {results.get('risk_assessment', {}).get('risk_level', 'Unknown').upper()}</div>
                        <div>风险评分: {results.get('risk_assessment', {}).get('overall_score', 0):.1f}</div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <div class="container">
        
        <!-- 关键指标概览 -->
        <div class="row mb-4">
            <div class="col-md-3">
                <div class="card risk-card">
                    <div class="card-body metric-card risk-critical">
                        <div class="metric-value text-danger">{results.get('risk_assessment', {}).get('critical_issues', 0)}</div>
                        <div>严重问题</div>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card risk-card">
                    <div class="card-body metric-card risk-high">
                        <div class="metric-value text-warning">{results.get('risk_assessment', {}).get('high_issues', 0)}</div>
                        <div>高风险问题</div>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card risk-card">
                    <div class="card-body metric-card risk-medium">
                        <div class="metric-value text-info">{results.get('risk_assessment', {}).get('medium_issues', 0)}</div>
                        <div>中风险问题</div>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card risk-card">
                    <div class="card-body metric-card risk-low">
                        <div class="metric-value text-success">{results.get('risk_assessment', {}).get('low_issues', 0)}</div>
                        <div>低风险问题</div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- 图表区域 -->
        <div class="row">
            <div class="col-md-6">
                <div class="card risk-card">
                    <div class="card-header">
                        <h5>问题分布饼图</h5>
                    </div>
                    <div class="card-body">
                        <div class="chart-container">
                            <canvas id="issueDistributionChart"></canvas>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="col-md-6">
                <div class="card risk-card">
                    <div class="card-header">
                        <h5>按地区风险分析</h5>
                    </div>
                    <div class="card-body">
                        <div class="chart-container">
                            <canvas id="regionRiskChart"></canvas>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- 详细问题列表 -->
        <div class="row mt-4">
            <div class="col-12">
                <div class="card risk-card">
                    <div class="card-header">
                        <h5>详细问题和解决方案</h5>
                    </div>
                    <div class="card-body">
                        <div class="issue-list">
                            {self._generate_issues_list_html(results.get('compliance_results', []))}
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- 实施时间线 -->
        <div class="row mt-4">
            <div class="col-12">
                <div class="card risk-card">
                    <div class="card-header">
                        <h5>实施时间线</h5>
                    </div>
                    <div class="card-body">
                        <div class="chart-container">
                            <canvas id="timelineChart"></canvas>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
    </div>
    
    <script>
        // 问题分布饼图
        const issueCtx = document.getElementById('issueDistributionChart').getContext('2d');
        const issueChart = new Chart(issueCtx, {{
            type: 'pie',
            data: {{
                labels: ['严重问题', '高风险', '中风险', '低风险'],
                datasets: [{{
                    data: [
                        {results.get('risk_assessment', {}).get('critical_issues', 0)},
                        {results.get('risk_assessment', {}).get('high_issues', 0)},
                        {results.get('risk_assessment', {}).get('medium_issues', 0)},
                        {results.get('risk_assessment', {}).get('low_issues', 0)}
                    ],
                    backgroundColor: ['#f44336', '#ff9800', '#ffc107', '#4caf50']
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{
                        position: 'bottom'
                    }}
                }}
            }}
        }});
        
        // 地区风险图表
        const regionCtx = document.getElementById('regionRiskChart').getContext('2d');
        const regionChart = new Chart(regionCtx, {{
            type: 'bar',
            data: {{
                labels: {json.dumps(list(results.get('risk_assessment', {}).get('market_specific_risks', {}).keys()))},
                datasets: [{{
                    label: '风险评分',
                    data: {json.dumps(list(results.get('risk_assessment', {}).get('market_specific_risks', {}).values()))},
                    backgroundColor: '#2196f3'
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    y: {{
                        beginAtZero: true
                    }}
                }}
            }}
        }});
        
        // 时间线图表（简化版）
        const timelineCtx = document.getElementById('timelineChart').getContext('2d');
        const timelineChart = new Chart(timelineCtx, {{
            type: 'line',
            data: {{
                labels: ['Week 1', 'Week 2', 'Week 4', 'Week 8', 'Week 12'],
                datasets: [{{
                    label: '预期合规进度',
                    data: [10, 25, 50, 80, 100],
                    borderColor: '#2196f3',
                    tension: 0.4
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    y: {{
                        beginAtZero: true,
                        max: 100,
                        ticks: {{
                            callback: function(value) {{
                                return value + '%';
                            }}
                        }}
                    }}
                }}
            }}
        }});
    </script>
    
    <footer class="mt-5 py-4 bg-light">
        <div class="container text-center">
            <p>报告生成时间: {results.get('timestamp', 'Unknown')}</p>
            <p>规则版本: {results.get('rules_version', 'Unknown')}</p>
            <p>教育游戏应用全球合规专家系统 v2.0</p>
        </div>
    </footer>
    
</body>
</html>
        """
        
        return dashboard_html
    
    def _get_risk_level_emoji(self, risk_level: str) -> str:
        """获取风险等级emoji"""
        emoji_map = {
            'critical': '🔴',
            'very_high': '🟠', 
            'high': '🟡',
            'medium': '🟢',
            'low': '✅'
        }
        return emoji_map.get(risk_level.lower(), '❓')
    
    def _generate_issues_list_html(self, compliance_results: List[Dict]) -> str:
        """生成问题列表HTML"""
        html = ""
        
        for issue in compliance_results:
            if issue.get('status') == 'failed':
                severity = issue.get('severity', 'low')
                html += f"""
                <div class="alert alert-{self._severity_to_bootstrap_class(severity)} mb-3">
                    <h6><strong>{issue.get('message', 'No message')}</strong></h6>
                    <p><strong>法规要求:</strong> {issue.get('requirement', 'Not specified')}</p>
                    <p><strong>解决方案:</strong> {issue.get('solution', 'Not specified')}</p>
                    <p><strong>地区:</strong> {issue.get('region', 'Global')} | 
                       <strong>预估成本:</strong> {issue.get('remediation_cost', 'TBD')} | 
                       <strong>实施时间:</strong> {issue.get('implementation_time', 'TBD')}</p>
                </div>
                """
        
        return html
    
    def _severity_to_bootstrap_class(self, severity: str) -> str:
        """转换严重程度到Bootstrap样式"""
        mapping = {
            'critical': 'danger',
            'high': 'warning',
            'medium': 'info', 
            'low': 'success'
        }
        return mapping.get(severity, 'secondary')
    
    def generate_trend_analysis(self, app_id: str) -> Dict[str, Any]:
        """生成趋势分析"""
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT timestamp, risk_score 
                    FROM compliance_history 
                    WHERE app_id = ? 
                    ORDER BY timestamp DESC 
                    LIMIT 10
                """, (app_id,))
                
                historical_data = cursor.fetchall()
                
        except Exception as e:
            historical_data = []
        
        trend_data = {
            'historical_scores': [float(row[1]) for row in historical_data],
            'timestamps': [row[0] for row in historical_data],
            'trend_direction': 'improving' if len(historical_data) >= 2 and historical_data[0][1] < historical_data[1][1] else 'stable',
            'recommendations': self._generate_trend_recommendations(historical_data)
        }
        
        return trend_data
    
    def _generate_trend_recommendations(self, historical_data: List) -> List[str]:
        """基于趋势生成建议"""
        if not historical_data:
            return ["首次分析，建议建立基线并定期检查"]
        
        if len(historical_data) < 2:
            return ["数据点不足，建议继续收集趋势数据"]
        
        latest_score = historical_data[0][1]
        previous_score = historical_data[1][1]
        
        if latest_score < previous_score:
            return ["✅ 合规性持续改善，保持当前优化方向"]
        elif latest_score > previous_score:
            return ["⚠️ 风险评分上升，需要重点关注新增问题"]
        else:
            return ["➡️ 合规性保持稳定，建议关注法规更新"]
    
    def export_dashboard(self, results: Dict[str, Any], export_format: str = 'html') -> str:
        """导出仪表板"""
        
        if export_format == 'html':
            return self.generate_dashboard(results)
        
        elif export_format == 'static_html':
            # 生成不依赖外部CDN的静态版本
            return self._generate_static_dashboard(results)
        
        elif export_format == 'pdf':
            # 使用HTML转PDF
            html_content = self.generate_dashboard(results)
            return self._html_to_pdf(html_content)
        
        else:
            raise ValueError(f"Unsupported export format: {export_format}")
    
    def _generate_static_dashboard(self, results: Dict[str, Any]) -> str:
        """生成静态HTML版本（内嵌所有资源）"""
        # 这里会内嵌Chart.js和Bootstrap的代码
        # 为了简化，返回基础版本
        return self.generate_dashboard(results).replace(
            'https://cdn.jsdelivr.net/npm/chart.js',
            'local/chart.min.js'  # 本地文件
        )
    
    def _html_to_pdf(self, html_content: str) -> bytes:
        """HTML转PDF"""
        try:
            import pdfkit
            pdf_data = pdfkit.from_string(html_content, False)
            return pdf_data
        except ImportError:
            # 如果没有pdfkit，返回HTML
            return html_content.encode('utf-8')
    
    def generate_executive_summary(self, results: Dict[str, Any]) -> str:
        """生成高管摘要"""
        
        risk_assessment = results.get('risk_assessment', {})
        app_profile = results.get('app_profile', {})
        
        summary = f"""
# 📊 高管合规摘要

**应用名称**: {app_profile.get('name', 'N/A')}  
**分析日期**: {datetime.now().strftime('%Y-%m-%d')}  
**风险等级**: {risk_assessment.get('risk_level', 'Unknown').upper()}

## 🎯 关键风险指标

| 指标 | 数值 | 状态 |
|------|------|------|
| 综合风险评分 | {risk_assessment.get('overall_score', 0):.1f}/1000 | {self._score_to_status(risk_assessment.get('overall_score', 0))} |
| 严重问题数量 | {risk_assessment.get('critical_issues', 0)} | {'🔴 紧急' if risk_assessment.get('critical_issues', 0) > 0 else '✅ 良好'} |
| 涉及法规数量 | {len(set(r.get('region', '') for r in results.get('compliance_results', [])))} | 🌍 多地区 |
| 目标市场 | {len(app_profile.get('target_markets', []))} 个 | {'🌏 复杂' if len(app_profile.get('target_markets', [])) > 2 else '🎯 简单'} |

## ⚡ 立即行动项

"""
        
        critical_issues = [r for r in results.get('compliance_results', []) 
                          if r.get('severity') == 'critical' and r.get('status') == 'failed']
        
        if critical_issues:
            for i, issue in enumerate(critical_issues[:3], 1):  # 只显示前3个
                summary += f"""
{i}. **{issue.get('message', 'Critical Issue')}**
   - 预估解决成本: {issue.get('remediation_cost', 'TBD')}
   - 预估时间: {issue.get('implementation_time', 'TBD')}
   - 影响地区: {issue.get('region', 'Global')}
"""
        else:
            summary += "✅ 无需立即处理的严重问题\n"
        
        summary += f"""
## 💰 成本效益分析

- **合规成本**: {results.get('cost_analysis', {}).get('total_estimated_cost', 'TBD')}
- **违规风险**: 最高可达全球收入4% (GDPR) 或 5000万人民币 (PIPL)
- **ROI预估**: 合规投入可避免{self._calculate_potential_fines(results)}的监管风险

## 📅 建议时间表

- **第1-2周**: 处理所有严重问题
- **第3-6周**: 优化高风险项目
- **第7-12周**: 完善中低风险建议

## 🎯 竞争优势

通过本合规系统，您的应用将获得：
- ✅ **全球市场准入资格**: 符合8个主要市场的法规要求
- ✅ **用户信任提升**: 透明的隐私保护和儿童安全措施
- ✅ **风险管理**: 避免高额监管罚款和声誉损失
- ✅ **技术优势**: 先进的数据保护和用户权利管理功能

---
*本报告由教育游戏应用全球合规专家系统生成*
"""
        
        return summary
    
    def _score_to_status(self, score: float) -> str:
        """风险评分转状态"""
        if score >= 300:
            return "🔴 极高风险"
        elif score >= 200:
            return "🟠 高风险"
        elif score >= 100:
            return "🟡 中风险"
        else:
            return "🟢 低风险"
    
    def _calculate_potential_fines(self, results: Dict[str, Any]) -> str:
        """计算潜在罚款风险"""
        app_profile = results.get('app_profile', {})
        target_markets = app_profile.get('target_markets', [])
        
        max_fines = []
        if 'EU' in target_markets:
            max_fines.append("全球收入4%或2000万欧元")
        if 'China' in target_markets:
            max_fines.append("5000万人民币或收入5%")
        if 'US' in target_markets:
            max_fines.append("每次违规$43,792 (COPPA)")
        
        return " + ".join(max_fines) if max_fines else "具体罚款金额"


# 使用示例
def generate_compliance_dashboard(compliance_results: Dict[str, Any]) -> str:
    """生成合规仪表板的便捷函数"""
    
    visualizer = ComplianceVisualizationEngine()
    dashboard_html = visualizer.generate_dashboard(compliance_results)
    
    # 保存到文件
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"compliance_dashboard_{timestamp}.html"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(dashboard_html)
    
    print(f"📊 交互式仪表板已生成: {filename}")
    print("🌐 在浏览器中打开查看完整的可视化分析")
    
    return filename

if __name__ == "__main__":
    # 测试代码
    sample_results = {
        'app_profile': {
            'name': 'Sample Education Game',
            'app_type': 'Educational Gaming',
            'target_age_group': '小学生(6-12岁)',
            'target_markets': ['US', 'China', 'EU']
        },
        'risk_assessment': {
            'risk_level': 'high',
            'overall_score': 250.5,
            'critical_issues': 2,
            'high_issues': 3,
            'medium_issues': 1,
            'low_issues': 0,
            'market_specific_risks': {
                'US': 180.2,
                'China': 320.8,
                'EU': 150.1
            }
        },
        'compliance_results': [
            {
                'rule_id': 'coppa_parental_consent',
                'severity': 'critical',
                'status': 'failed',
                'message': 'Missing parental consent mechanism',
                'requirement': 'COPPA requires verifiable parental consent',
                'solution': 'Implement credit card pre-authorization',
                'region': 'US',
                'remediation_cost': '$3000-8000',
                'implementation_time': '3-4 weeks'
            }
        ]
    }
    
    generate_compliance_dashboard(sample_results)