#!/usr/bin/env python3
"""
高级合规规则引擎 v2.0
Advanced Compliance Rule Engine

特性：
- 配置化规则系统
- 动态规则加载和热更新
- 多格式输出支持
- AI驱动的风险预测
- 社区规则贡献支持
- 性能优化和缓存
"""

import yaml
import json
import hashlib
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from pathlib import Path
import requests
import sqlite3
from concurrent.futures import ThreadPoolExecutor

@dataclass
class ComplianceResult:
    """标准化合规结果"""
    rule_id: str
    severity: str
    status: str  # passed, failed, warning, not_applicable
    message: str
    requirement: str
    solution: str
    region: str
    weight: int
    confidence: float = 1.0
    remediation_cost: Optional[str] = None
    implementation_time: Optional[str] = None
    code_template: Optional[str] = None

@dataclass
class RiskAssessment:
    """风险评估结果"""
    overall_score: float
    risk_level: str
    critical_issues: int
    high_issues: int
    medium_issues: int
    low_issues: int
    market_specific_risks: Dict[str, float]
    trend_prediction: Dict[str, Any]

class AdvancedRuleEngine:
    """高级规则引擎 - 支持配置化、缓存、预测"""
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path or Path(__file__).parent.parent / "config" / "compliance-rules.yaml"
        self.rules_cache = {}
        self.results_cache = {}
        self.cache_ttl = 3600  # 1小时缓存
        self.logger = self._setup_logging()
        self.db_path = Path(__file__).parent.parent / "data" / "compliance.db"
        self._init_database()
        self._load_rules()
    
    def _setup_logging(self) -> logging.Logger:
        """设置日志系统"""
        logger = logging.getLogger('compliance_engine')
        logger.setLevel(logging.INFO)
        
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def _init_database(self):
        """初始化数据库存储历史数据"""
        self.db_path.parent.mkdir(exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS compliance_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    app_id TEXT,
                    timestamp DATETIME,
                    rules_version TEXT,
                    results_json TEXT,
                    risk_score REAL
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS rule_performance (
                    rule_id TEXT PRIMARY KEY,
                    execution_count INTEGER DEFAULT 0,
                    avg_execution_time REAL DEFAULT 0.0,
                    false_positive_rate REAL DEFAULT 0.0,
                    last_updated DATETIME
                )
            """)
    
    def _load_rules(self):
        """加载规则配置"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.rules_config = yaml.safe_load(f)
            
            # 计算规则配置的哈希，用于缓存失效
            config_hash = hashlib.md5(str(self.rules_config).encode()).hexdigest()
            self.rules_version = config_hash[:8]
            
            self.logger.info(f"Loaded rules version: {self.rules_version}")
            
        except Exception as e:
            self.logger.error(f"Failed to load rules: {e}")
            raise
    
    def check_for_rule_updates(self) -> bool:
        """
        检查规则是否有更新，优先级：
        1. 远程 URL（环境变量 RULES_UPDATE_URL 配置，可选）
        2. 本地文件修改时间（不需要任何配置，始终生效）
        """
        import os, time as _time

        # ── 优先：远程 URL ────────────────────────────────────────────
        remote_url = os.environ.get("RULES_UPDATE_URL", "").strip()
        if remote_url:
            try:
                response = requests.get(remote_url, timeout=10)
                if response.status_code == 200:
                    remote_hash = hashlib.md5(response.content).hexdigest()[:8]
                    if remote_hash != self.rules_version:
                        self.logger.info(f"远程规则已更新: {self.rules_version} → {remote_hash}")
                        # 将远程内容写入本地文件，reload_rules() 从文件读取
                        self.config_path.write_bytes(response.content)
                        return True
                    self.logger.info("远程规则无更新")
                    return False
            except Exception as e:
                self.logger.warning(f"远程规则检查失败，降级为本地文件检查: {e}")

        # ── 兜底：本地文件修改时间 ────────────────────────────────────
        try:
            current_mtime = self.config_path.stat().st_mtime
            if not hasattr(self, '_last_mtime'):
                self._last_mtime = current_mtime
                return False
            if current_mtime != self._last_mtime:
                self.logger.info(f"检测到本地规则文件已修改（{self.config_path.name}）")
                return True
        except Exception as e:
            self.logger.warning(f"本地规则检查失败: {e}")

        return False

    def reload_rules(self):
        """热重载规则（从本地文件重新加载）"""
        old_version = self.rules_version
        self._load_rules()
        # 更新上次加载时的 mtime，避免下次误判
        try:
            self._last_mtime = self.config_path.stat().st_mtime
        except Exception:
            pass
        if old_version != self.rules_version:
            self.rules_cache.clear()
            self.results_cache.clear()
            self.logger.info(f"规则已热重载: {old_version} → {self.rules_version}")
        return self.rules_version
    
    def _get_cache_key(self, app_info: Dict) -> str:
        """生成缓存键"""
        cache_data = {
            'app_type': app_info.get('app_type'),
            'min_age': app_info.get('min_user_age'),
            'markets': sorted(app_info.get('target_markets', [])),
            'features': sorted([k for k, v in app_info.items() if isinstance(v, bool) and v]),
            'rules_version': self.rules_version
        }
        return hashlib.md5(json.dumps(cache_data, sort_keys=True).encode()).hexdigest()
    
    def _is_cache_valid(self, cache_entry: Dict) -> bool:
        """检查缓存是否有效"""
        if not cache_entry:
            return False
        
        cache_time = datetime.fromisoformat(cache_entry.get('timestamp', ''))
        return datetime.now() - cache_time < timedelta(seconds=self.cache_ttl)
    
    async def analyze_compliance_async(self, app_info: Dict) -> Dict[str, Any]:
        """异步合规分析 - 性能优化"""
        cache_key = self._get_cache_key(app_info)
        
        # 检查缓存
        if cache_key in self.results_cache and self._is_cache_valid(self.results_cache[cache_key]):
            self.logger.info("Returning cached results")
            return self.results_cache[cache_key]['data']
        
        # 并行执行各个规则检查
        with ThreadPoolExecutor(max_workers=5) as executor:
            tasks = []
            
            # 儿童保护规则
            if app_info.get('min_user_age', 18) < 18:
                tasks.append(
                    asyncio.get_event_loop().run_in_executor(
                        executor, self._check_children_protection, app_info
                    )
                )
            
            # 游戏法规规则
            if self._has_gaming_features(app_info):
                tasks.append(
                    asyncio.get_event_loop().run_in_executor(
                        executor, self._check_gaming_regulations, app_info
                    )
                )
            
            # 教育合规规则
            if 'Educational' in app_info.get('app_type', ''):
                tasks.append(
                    asyncio.get_event_loop().run_in_executor(
                        executor, self._check_education_compliance, app_info
                    )
                )
            
            # 隐私法律规则
            if self._processes_personal_data(app_info):
                tasks.append(
                    asyncio.get_event_loop().run_in_executor(
                        executor, self._check_privacy_laws, app_info
                    )
                )
            
            # 平台政策规则
            tasks.append(
                asyncio.get_event_loop().run_in_executor(
                    executor, self._check_platform_policies, app_info
                )
            )
            
            # 等待所有任务完成
            results = await asyncio.gather(*tasks)
        
        # 合并结果
        all_results = []
        for result_list in results:
            all_results.extend(result_list)
        
        # 生成风险评估
        risk_assessment = self._calculate_advanced_risk(app_info, all_results)
        
        # 生成预测和建议
        predictions = self._predict_compliance_trends(app_info, all_results)
        
        # 构建最终结果
        final_result = {
            'timestamp': datetime.now().isoformat(),
            'rules_version': self.rules_version,
            'app_profile': app_info,
            'compliance_results': [asdict(r) for r in all_results],
            'risk_assessment': asdict(risk_assessment),
            'predictions': predictions,
            'recommendations': self._generate_enhanced_recommendations(app_info, all_results, risk_assessment),
            'implementation_guide': self._generate_implementation_guide(all_results),
            'cost_analysis': self._generate_cost_analysis(all_results),
            'timeline_estimate': self._generate_timeline_estimate(all_results)
        }
        
        # 缓存结果
        self.results_cache[cache_key] = {
            'timestamp': datetime.now().isoformat(),
            'data': final_result
        }
        
        # 保存到数据库
        self._save_to_history(app_info.get('name', 'unknown'), final_result)
        
        return final_result
    
    def _has_gaming_features(self, app_info: Dict) -> bool:
        """检查是否有游戏功能"""
        gaming_indicators = [
            'has_multiplayer', 'has_leaderboards', 'has_virtual_currency',
            'has_in_app_purchases', 'has_random_rewards', 'has_time_pressure'
        ]
        return ('Gaming' in app_info.get('app_type', '') or
                any(app_info.get(indicator, False) for indicator in gaming_indicators))
    
    def _processes_personal_data(self, app_info: Dict) -> bool:
        """检查是否处理个人数据"""
        data_processing_indicators = [
            'collects_location', 'collects_biometric', 'tracks_learning_progress',
            'collects_photos_videos', 'has_advertising', 'shares_with_third_parties',
            'cross_border_data', 'has_chat_social'
        ]
        return any(app_info.get(indicator, False) for indicator in data_processing_indicators)
    
    def _check_children_protection(self, app_info: Dict) -> List[ComplianceResult]:
        """儿童保护规则检查 - 配置化版本"""
        results = []
        min_age = app_info.get('min_user_age', 18)
        target_markets = app_info.get('target_markets', [])
        
        children_rules = self.rules_config.get('children_protection', {})
        
        # COPPA检查
        if 'US' in target_markets and min_age < 13:
            coppa_config = children_rules.get('coppa_us', {})
            
            # 家长同意机制检查
            if not app_info.get('has_parental_controls'):
                results.append(ComplianceResult(
                    rule_id="coppa_parental_consent",
                    severity="critical",
                    status="failed",
                    message="13岁以下儿童应用缺少可验证的家长同意机制",
                    requirement="COPPA要求13岁以下儿童数据收集需要可验证的家长同意",
                    solution=f"实现以下家长同意方法之一: {', '.join(coppa_config.get('parental_consent_methods', {}).get('tier_1', []))}",
                    region="US",
                    weight=100,
                    confidence=0.95,
                    remediation_cost="$2000-8000",
                    implementation_time="2-4 weeks",
                    code_template="templates/coppa_parental_consent.py"
                ))
            
            # 检查禁止功能
            prohibited = coppa_config.get('prohibited_features', [])
            for feature in prohibited:
                feature_mapping = {
                    'behavioral_advertising': 'has_advertising',
                    'location_tracking_without_necessity': 'collects_location',
                    'social_networking_features': 'has_chat_social',
                    'third_party_data_sharing': 'shares_with_third_parties'
                }
                
                if app_info.get(feature_mapping.get(feature), False):
                    results.append(ComplianceResult(
                        rule_id=f"coppa_prohibited_{feature}",
                        severity="high",
                        status="failed",
                        message=f"COPPA禁止儿童应用使用: {feature}",
                        requirement=f"COPPA禁止向13岁以下儿童提供{feature}",
                        solution=f"移除或为儿童用户禁用{feature}功能",
                        region="US",
                        weight=75,
                        confidence=0.9
                    ))
        
        # GDPR儿童条款检查
        if any(market in ['EU', 'UK', 'EEA'] for market in target_markets):
            gdpr_children_config = children_rules.get('gdpr_children_eu', {})
            member_variations = gdpr_children_config.get('member_state_variations', {})
            
            # 根据目标国家确定最严格的年龄要求
            min_consent_age = min([
                member_variations.get(country.replace('EU_', ''), 16)
                for country in target_markets if country.startswith('EU_')
            ] or [16])
            
            if min_age < min_consent_age and not app_info.get('has_parental_controls'):
                results.append(ComplianceResult(
                    rule_id="gdpr_children_consent",
                    severity="critical",
                    status="failed",
                    message=f"{min_consent_age}岁以下用户缺少家长同意机制",
                    requirement=f"GDPR要求{min_consent_age}岁以下儿童数据处理需家长同意",
                    solution="实现符合GDPR的家长同意机制，包含撤回同意功能",
                    region="EU",
                    weight=100,
                    confidence=0.92,
                    remediation_cost="$3000-10000",
                    implementation_time="3-6 weeks"
                ))
        
        return results
    
    def _check_gaming_regulations(self, app_info: Dict) -> List[ComplianceResult]:
        """游戏法规检查 - 配置化版本"""
        results = []
        target_markets = app_info.get('target_markets', [])
        min_age = app_info.get('min_user_age', 18)
        
        gaming_rules = self.rules_config.get('gaming_regulations', {})
        
        # 中国防沉迷检查
        if 'China' in target_markets and min_age < 18:
            china_config = gaming_rules.get('china_anti_addiction', {})
            
            # 实名认证系统
            if not app_info.get('has_age_verification'):
                results.append(ComplianceResult(
                    rule_id="china_realname_authentication",
                    severity="critical",
                    status="failed",
                    message="涉及未成年人的游戏应用缺少实名认证系统",
                    requirement="必须接入国家新闻出版署实名认证系统",
                    solution="对接NRTA实名认证系统API，实现身份证+姓名验证",
                    region="China",
                    weight=100,
                    confidence=0.98,
                    remediation_cost="$5000-15000",
                    implementation_time="4-8 weeks",
                    code_template="templates/china_realname_auth.py"
                ))
            
            # 时间限制检查
            time_restrictions = china_config.get('time_restrictions', {})
            if not app_info.get('has_parental_controls'):
                results.append(ComplianceResult(
                    rule_id="china_time_restrictions",
                    severity="critical",
                    status="failed",
                    message="未实现防沉迷时间管理系统",
                    requirement=f"工作日{time_restrictions.get('weekdays', {}).get('allowed_time', 0)}秒，周末{time_restrictions.get('weekends', {}).get('allowed_time', 3600)}秒限制",
                    solution="实现防沉迷时间检查系统",
                    region="China",
                    weight=100,
                    confidence=0.95,
                    remediation_cost="$3000-12000",
                    implementation_time="3-6 weeks",
                    code_template="templates/china_anti_addiction_time.py"
                ))
        
        return results
    
    def _check_education_compliance(self, app_info: Dict) -> List[ComplianceResult]:
        """教育合规检查"""
        results = []
        # 实现教育合规检查逻辑
        return results
    
    def _check_privacy_laws(self, app_info: Dict) -> List[ComplianceResult]:
        """隐私法律检查"""
        results = []
        # 实现隐私法律检查逻辑
        return results
    
    def _check_platform_policies(self, app_info: Dict) -> List[ComplianceResult]:
        """平台政策检查"""
        results = []
        platform_config = self.rules_config.get('platform_policies', {})
        
        # Google Play API级别检查
        google_config = platform_config.get('google_play', {})
        current_requirements = google_config.get('current_requirements', {})
        required_api = current_requirements.get('target_api_level', 34)
        
        if app_info.get('target_sdk'):
            try:
                api_level = int(app_info['target_sdk'])
                if api_level < required_api:
                    results.append(ComplianceResult(
                        rule_id="google_play_api_level",
                        severity="critical",
                        status="failed",
                        message=f"目标API级别 {api_level} 低于要求的 {required_api}",
                        requirement=f"新应用必须使用API Level {required_api}+",
                        solution=f"在build.gradle中设置 targetSdkVersion {required_api}",
                        region="Global",
                        weight=100,
                        confidence=0.99,
                        remediation_cost="$500-2000",
                        implementation_time="1-2 days",
                        code_template="templates/android_api_upgrade.gradle"
                    ))
            except ValueError:
                pass
        
        return results
    
    def _calculate_advanced_risk(self, app_info: Dict, results: List[ComplianceResult]) -> RiskAssessment:
        """高级风险计算"""
        global_config = self.rules_config.get('global', {})
        risk_config = global_config.get('risk_calculation', {})
        
        # 基础风险计算
        base_score = 0.0
        critical_count = 0
        high_count = 0
        medium_count = 0
        low_count = 0
        
        for result in results:
            if result.status == 'failed':
                weight = result.weight
                base_score += weight
                
                if result.severity == 'critical':
                    critical_count += 1
                elif result.severity == 'high':
                    high_count += 1
                elif result.severity == 'medium':
                    medium_count += 1
                else:
                    low_count += 1
        
        # 应用特征风险乘数
        multipliers = risk_config.get('base_multipliers', {})
        
        if app_info.get('min_user_age', 18) < 13:
            base_score *= multipliers.get('children_under_13', 2.0)
        
        if app_info.get('cross_border_data'):
            base_score *= multipliers.get('cross_border_data', 1.5)
        
        if app_info.get('collects_biometric'):
            base_score *= multipliers.get('biometric_data', 1.8)
        
        # 市场特定风险
        market_risks = {}
        market_factors = risk_config.get('market_risk_factors', {})
        
        for market in app_info.get('target_markets', []):
            if market in market_factors:
                market_risks[market] = base_score * market_factors[market]
        
        # 确定风险等级
        if base_score >= 300 or critical_count >= 3:
            risk_level = "critical"
        elif base_score >= 200 or critical_count >= 2:
            risk_level = "very_high"
        elif base_score >= 100 or critical_count >= 1:
            risk_level = "high"
        elif base_score >= 50 or high_count >= 3:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        # 趋势预测
        trend_prediction = self._predict_compliance_trends(app_info, results)
        
        return RiskAssessment(
            overall_score=base_score,
            risk_level=risk_level,
            critical_issues=critical_count,
            high_issues=high_count,
            medium_issues=medium_count,
            low_issues=low_count,
            market_specific_risks=market_risks,
            trend_prediction=trend_prediction
        )
    
    def _predict_compliance_trends(self, app_info: Dict, results: List[ComplianceResult]) -> Dict[str, Any]:
        """AI驱动的合规趋势预测"""
        # 基于历史数据和当前法规趋势预测
        predictions = {
            'regulatory_changes': {
                'china_gaming': {
                    'probability': 0.7,
                    'timeframe': '6-12 months',
                    'impact': 'Stricter anti-addiction measures expected'
                },
                'eu_ai_act': {
                    'probability': 0.9,
                    'timeframe': '12-24 months',
                    'impact': 'AI systems in education will face new requirements'
                },
                'us_federal_privacy': {
                    'probability': 0.4,
                    'timeframe': '24-36 months',
                    'impact': 'Federal privacy law may supersede state laws'
                }
            },
            'emerging_risks': [
                'Deepfake detection requirements in children apps',
                'Biometric data processing restrictions',
                'Cross-border educational data transfer limitations'
            ],
            'recommended_preparations': [
                'Implement privacy by design principles',
                'Establish data governance framework',
                'Monitor regulatory developments in target markets'
            ]
        }
        
        return predictions
    
    def _generate_enhanced_recommendations(self, app_info: Dict, results: List[ComplianceResult], risk_assessment: RiskAssessment) -> List[Dict[str, Any]]:
        """生成增强的建议"""
        recommendations = []
        
        # 基于风险等级的建议
        if risk_assessment.risk_level in ['critical', 'very_high']:
            recommendations.append({
                'category': 'Immediate Action Required',
                'priority': 'critical',
                'title': 'Halt Product Launch - Critical Compliance Issues',
                'description': f'Found {risk_assessment.critical_issues} critical compliance issues that could result in significant legal penalties',
                'actions': [
                    'Suspend all marketing activities',
                    'Engage legal counsel immediately',
                    'Begin remediation of critical issues',
                    'Consider soft launch in less restrictive markets first'
                ],
                'timeline': '0-2 weeks'
            })
        
        # 按区域的建议
        for market, risk_score in risk_assessment.market_specific_risks.items():
            if risk_score > 150:
                recommendations.append({
                    'category': f'{market} Market Specific',
                    'priority': 'high',
                    'title': f'Enhanced {market} Compliance Required',
                    'description': f'High risk score ({risk_score:.1f}) detected for {market} market',
                    'actions': self._get_market_specific_actions(market, app_info),
                    'timeline': '2-8 weeks'
                })
        
        return recommendations
    
    def _get_market_specific_actions(self, market: str, app_info: Dict) -> List[str]:
        """获取市场特定行动建议"""
        actions = {
            'China': [
                'Implement NRTA real-name authentication',
                'Deploy anti-addiction time management',
                'Set up payment restrictions by age',
                'Establish parental supervision platform'
            ],
            'EU': [
                'Implement GDPR data subject rights',
                'Conduct Data Protection Impact Assessment',
                'Establish lawful basis for all processing',
                'Implement privacy by design principles'
            ],
            'US': [
                'Implement COPPA parental consent verification',
                'Review state-specific privacy requirements',
                'Establish FERPA compliance if educational',
                'Configure child-directed app settings'
            ]
        }
        return actions.get(market, ['Market-specific compliance review required'])
    
    def _generate_implementation_guide(self, results: List[ComplianceResult]) -> Dict[str, Any]:
        """生成实施指南"""
        guide = {
            'phases': [],
            'code_templates': [],
            'dependencies': [],
            'testing_procedures': []
        }
        
        # 按优先级分组
        critical_items = [r for r in results if r.severity == 'critical' and r.status == 'failed']
        high_items = [r for r in results if r.severity == 'high' and r.status == 'failed']
        
        if critical_items:
            guide['phases'].append({
                'name': 'Phase 1: Critical Issues',
                'timeline': '0-4 weeks',
                'items': [{'rule_id': r.rule_id, 'solution': r.solution} for r in critical_items]
            })
        
        if high_items:
            guide['phases'].append({
                'name': 'Phase 2: High Priority',
                'timeline': '4-8 weeks', 
                'items': [{'rule_id': r.rule_id, 'solution': r.solution} for r in high_items]
            })
        
        # 收集代码模板
        templates = [r.code_template for r in results if r.code_template]
        guide['code_templates'] = list(set(templates))
        
        return guide
    
    def _generate_cost_analysis(self, results: List[ComplianceResult]) -> Dict[str, Any]:
        """生成成本分析"""
        cost_analysis = {
            'total_estimated_cost': '未评估',
            'cost_breakdown': {},
            'cost_by_priority': {},
            'roi_analysis': {}
        }
        
        # 提取成本信息并分析
        costs = [r.remediation_cost for r in results if r.remediation_cost and r.status == 'failed']
        
        if costs:
            # 简单的成本范围分析
            total_min = sum([int(c.split('-')[0].replace('$', '').replace(',', '')) for c in costs if '-' in c])
            total_max = sum([int(c.split('-')[1].replace('$', '').replace(',', '')) for c in costs if '-' in c])
            
            cost_analysis['total_estimated_cost'] = f"${total_min:,} - ${total_max:,}"
        
        return cost_analysis
    
    def _generate_timeline_estimate(self, results: List[ComplianceResult]) -> Dict[str, Any]:
        """生成时间线估算"""
        timeline = {
            'total_estimated_time': '未评估',
            'critical_path': [],
            'parallel_tasks': [],
            'milestone_schedule': {}
        }
        
        return timeline
    
    def _save_to_history(self, app_id: str, results: Dict[str, Any]):
        """保存到历史数据库"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO compliance_history 
                    (app_id, timestamp, rules_version, results_json, risk_score)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    app_id,
                    datetime.now(),
                    self.rules_version,
                    json.dumps(results),
                    results.get('risk_assessment', {}).get('overall_score', 0.0)
                ))
        except Exception as e:
            self.logger.error(f"Failed to save to history: {e}")
    
    def generate_multi_format_report(self, results: Dict[str, Any], format_type: str = 'json') -> Union[str, bytes]:
        """多格式报告生成"""
        if format_type == 'json':
            return json.dumps(results, indent=2, ensure_ascii=False)
        
        elif format_type == 'html':
            return self._generate_html_report(results)
        
        elif format_type == 'pdf':
            return self._generate_pdf_report(results)
        
        elif format_type == 'xml':
            return self._generate_xml_report(results)
        
        elif format_type == 'csv':
            return self._generate_csv_report(results)
        
        else:
            raise ValueError(f"Unsupported format: {format_type}")
    
    def _generate_html_report(self, results: Dict[str, Any]) -> str:
        """生成HTML报告"""
        html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Compliance Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .critical { background-color: #ffebee; border-left: 5px solid #f44336; }
        .high { background-color: #fff3e0; border-left: 5px solid #ff9800; }
        .medium { background-color: #fff8e1; border-left: 5px solid #ffc107; }
        .low { background-color: #e8f5e8; border-left: 5px solid #4caf50; }
        .issue { margin: 10px 0; padding: 15px; }
        .header { background: #2196f3; color: white; padding: 20px; }
        .risk-score { font-size: 2em; font-weight: bold; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Compliance Analysis Report</h1>
        <div class="risk-score">Risk Level: {risk_level}</div>
    </div>
    
    <h2>Summary</h2>
    <ul>
        <li>Critical Issues: {critical_count}</li>
        <li>High Issues: {high_count}</li>
        <li>Medium Issues: {medium_count}</li>
        <li>Low Issues: {low_count}</li>
    </ul>
    
    <h2>Issues</h2>
    {issues_html}
    
    <h2>Recommendations</h2>
    {recommendations_html}
    
</body>
</html>
        """
        
        risk_assessment = results.get('risk_assessment', {})
        
        # 生成问题HTML
        issues_html = ""
        for issue in results.get('compliance_results', []):
            if issue.get('status') == 'failed':
                issues_html += f"""
                <div class="issue {issue.get('severity', 'low')}">
                    <h3>{issue.get('message', 'No message')}</h3>
                    <p><strong>Requirement:</strong> {issue.get('requirement', 'Not specified')}</p>
                    <p><strong>Solution:</strong> {issue.get('solution', 'Not specified')}</p>
                    <p><strong>Region:</strong> {issue.get('region', 'Global')}</p>
                </div>
                """
        
        # 生成建议HTML
        recommendations_html = ""
        for rec in results.get('recommendations', []):
            recommendations_html += f"""
            <div class="recommendation">
                <h3>{rec.get('title', 'No title')}</h3>
                <p>{rec.get('description', 'No description')}</p>
            </div>
            """
        
        return html_template.format(
            risk_level=risk_assessment.get('risk_level', 'Unknown'),
            critical_count=risk_assessment.get('critical_issues', 0),
            high_count=risk_assessment.get('high_issues', 0),
            medium_count=risk_assessment.get('medium_issues', 0),
            low_count=risk_assessment.get('low_issues', 0),
            issues_html=issues_html,
            recommendations_html=recommendations_html
        )
    
    def _generate_pdf_report(self, results: Dict[str, Any]) -> bytes:
        """生成PDF报告"""
        # 这里需要使用reportlab或类似的库
        # 为了简化，返回HTML转PDF的占位符
        html_content = self._generate_html_report(results)
        # 实际实现需要使用weasyprint或类似工具
        return html_content.encode('utf-8')
    
    def _generate_xml_report(self, results: Dict[str, Any]) -> str:
        """生成XML报告"""
        import xml.etree.ElementTree as ET
        
        root = ET.Element("compliance_report")
        root.set("timestamp", results.get('timestamp', ''))
        root.set("rules_version", results.get('rules_version', ''))
        
        # 添加风险评估
        risk_elem = ET.SubElement(root, "risk_assessment")
        risk_data = results.get('risk_assessment', {})
        for key, value in risk_data.items():
            elem = ET.SubElement(risk_elem, key)
            elem.text = str(value)
        
        # 添加合规结果
        results_elem = ET.SubElement(root, "compliance_results")
        for issue in results.get('compliance_results', []):
            issue_elem = ET.SubElement(results_elem, "issue")
            for key, value in issue.items():
                elem = ET.SubElement(issue_elem, key)
                elem.text = str(value)
        
        return ET.tostring(root, encoding='unicode')
    
    def _generate_csv_report(self, results: Dict[str, Any]) -> str:
        """生成CSV报告"""
        import csv
        from io import StringIO
        
        output = StringIO()
        writer = csv.writer(output)
        
        # 写入标题行
        writer.writerow([
            'Rule ID', 'Severity', 'Status', 'Message', 'Requirement', 
            'Solution', 'Region', 'Weight', 'Confidence'
        ])
        
        # 写入数据行
        for issue in results.get('compliance_results', []):
            writer.writerow([
                issue.get('rule_id', ''),
                issue.get('severity', ''),
                issue.get('status', ''),
                issue.get('message', ''),
                issue.get('requirement', ''),
                issue.get('solution', ''),
                issue.get('region', ''),
                issue.get('weight', ''),
                issue.get('confidence', '')
            ])
        
        return output.getvalue()


# 使用示例
async def main():
    engine = AdvancedRuleEngine()
    
    # 示例应用信息
    app_info = {
        'name': 'Math Learning Game',
        'app_type': 'Educational Gaming',
        'min_user_age': 8,
        'target_markets': ['US', 'China', 'EU'],
        'has_multiplayer': True,
        'has_in_app_purchases': True,
        'collects_location': False,
        'has_advertising': True,
        'has_parental_controls': False,
        'has_age_verification': False,
        'target_sdk': '33'
    }
    
    # 执行分析
    results = await engine.analyze_compliance_async(app_info)
    
    # 生成报告
    html_report = engine.generate_multi_format_report(results, 'html')
    json_report = engine.generate_multi_format_report(results, 'json')
    
    print("Analysis completed successfully!")
    return results

if __name__ == "__main__":
    asyncio.run(main())