#!/usr/bin/env python3
"""
数据分析师 (Data Analyst Expert)

理论基础:
- AARRR 海盗指标框架 (Acquisition / Activation / Retention / Revenue / Referral)
- LTV 生命周期价值模型
- 留存曲线分析（Day-N Retention）
- 付费漏斗与转化分析
- 关卡/内容漏斗分析
- A/B 测试统计方法
- Dave McClure 增长框架

职责:
- 定义完整的 KPI 体系（分层、有基准值）
- 设计埋点方案（事件 + 属性 + 时机）
- 输出留存/付费/内容分析框架（含行业基准）
- 制定 A/B 测试优先级和方案
- 推荐数据工具栈
- 提供数据驱动的迭代决策框架

所有基准值来自行业公开数据（Adjust / AppsFlyer / GameAnalytics 报告）
"""

from typing import Dict, List, Any
from datetime import datetime


class DataAnalystExpert:
    """数据分析师 — 游戏数据体系与增长分析专家"""

    def __init__(self):
        self.name = "数据分析师"
        self.version = "1.0.0"
        self._build_benchmarks()

    # ─────────────────────────────────────────────────────────────
    # 行业基准数据库
    # ─────────────────────────────────────────────────────────────

    def _build_benchmarks(self):
        """行业基准数据（来源：GameAnalytics 2023/2024 年度报告）"""

        # 各游戏类型 Day-N 留存基准
        self.retention_benchmarks = {
            'casual': {
                'day1': {'poor': '<25%', 'avg': '32%', 'good': '40%', 'excellent': '>50%'},
                'day7': {'poor': '<8%',  'avg': '12%', 'good': '18%', 'excellent': '>25%'},
                'day30':{'poor': '<2%',  'avg': '4%',  'good': '7%',  'excellent': '>10%'},
            },
            'rpg': {
                'day1': {'poor': '<30%', 'avg': '38%', 'good': '48%', 'excellent': '>55%'},
                'day7': {'poor': '<12%', 'avg': '18%', 'good': '25%', 'excellent': '>33%'},
                'day30':{'poor': '<5%',  'avg': '8%',  'good': '13%', 'excellent': '>18%'},
            },
            'action_rpg': {
                'day1': {'poor': '<28%', 'avg': '36%', 'good': '46%', 'excellent': '>52%'},
                'day7': {'poor': '<10%', 'avg': '16%', 'good': '23%', 'excellent': '>30%'},
                'day30':{'poor': '<4%',  'avg': '7%',  'good': '11%', 'excellent': '>16%'},
            },
            'fps': {
                'day1': {'poor': '<25%', 'avg': '33%', 'good': '42%', 'excellent': '>50%'},
                'day7': {'poor': '<10%', 'avg': '16%', 'good': '24%', 'excellent': '>32%'},
                'day30':{'poor': '<4%',  'avg': '7%',  'good': '12%', 'excellent': '>18%'},
            },
            'roguelike': {
                'day1': {'poor': '<35%', 'avg': '43%', 'good': '52%', 'excellent': '>60%'},
                'day7': {'poor': '<15%', 'avg': '22%', 'good': '30%', 'excellent': '>38%'},
                'day30':{'poor': '<6%',  'avg': '10%', 'good': '16%', 'excellent': '>22%'},
            },
            'strategy': {
                'day1': {'poor': '<30%', 'avg': '38%', 'good': '47%', 'excellent': '>55%'},
                'day7': {'poor': '<12%', 'avg': '19%', 'good': '28%', 'excellent': '>35%'},
                'day30':{'poor': '<5%',  'avg': '9%',  'good': '15%', 'excellent': '>20%'},
            },
            'simulation': {
                'day1': {'poor': '<28%', 'avg': '36%', 'good': '45%', 'excellent': '>53%'},
                'day7': {'poor': '<10%', 'avg': '16%', 'good': '24%', 'excellent': '>31%'},
                'day30':{'poor': '<4%',  'avg': '7%',  'good': '12%', 'excellent': '>18%'},
            },
        }

        # 付费指标基准（F2P 移动端）
        self.monetization_benchmarks = {
            'casual': {
                'conversion_rate': {'avg': '1.5%',  'good': '3%',   'excellent': '>5%'},
                'arpu_monthly':    {'avg': '$0.3',  'good': '$0.8', 'excellent': '>$2'},
                'arppu_monthly':   {'avg': '$8',    'good': '$15',  'excellent': '>$30'},
                'ltv_6m':          {'avg': '$0.5',  'good': '$1.5', 'excellent': '>$4'},
            },
            'rpg': {
                'conversion_rate': {'avg': '3%',    'good': '6%',   'excellent': '>10%'},
                'arpu_monthly':    {'avg': '$1.2',  'good': '$3',   'excellent': '>$8'},
                'arppu_monthly':   {'avg': '$25',   'good': '$50',  'excellent': '>$100'},
                'ltv_6m':          {'avg': '$3',    'good': '$8',   'excellent': '>$20'},
            },
            'strategy': {
                'conversion_rate': {'avg': '2.5%',  'good': '5%',   'excellent': '>8%'},
                'arpu_monthly':    {'avg': '$2',    'good': '$5',   'excellent': '>$12'},
                'arppu_monthly':   {'avg': '$40',   'good': '$80',  'excellent': '>$150'},
                'ltv_6m':          {'avg': '$5',    'good': '$15',  'excellent': '>$40'},
            },
        }

        # 关键漏斗节点流失率
        self.funnel_benchmarks = {
            'tutorial_completion': {'poor': '<40%', 'avg': '60%', 'good': '75%', 'excellent': '>85%'},
            'level1_completion':   {'poor': '<50%', 'avg': '65%', 'good': '80%', 'excellent': '>88%'},
            'first_iap_click':     {'poor': '<3%',  'avg': '8%',  'good': '15%', 'excellent': '>20%'},
            'first_iap_complete':  {'poor': '<30%', 'avg': '50%', 'good': '65%', 'excellent': '>75%'},
            'pvp_first_match':     {'poor': '<20%', 'avg': '35%', 'good': '50%', 'excellent': '>65%'},
        }

    # ─────────────────────────────────────────────────────────────
    # 主入口
    # ─────────────────────────────────────────────────────────────

    def analyze(self, game_profile: Dict) -> Dict:
        """
        game_profile:
        {
            game_name:         str,
            game_type:         str,
            monetization_type: str,    # f2p / premium / hybrid
            target_platforms:  list,
            features:          list,
            has_multiplayer:   bool,
            has_iap:           bool,
            has_gacha:         bool,
            launch_stage:      str,    # pre_launch / soft_launch / full_launch / live_ops
            expected_dau:      str,    # <1k / 1k-10k / 10k-100k / 100k+
            team_size:         str,
        }
        """
        p = self._normalize(game_profile)

        kpi_system       = self._build_kpi_system(p)
        tracking_plan    = self._build_tracking_plan(p)
        retention_model  = self._build_retention_model(p)
        monetization_model = self._build_monetization_model(p)
        content_funnel   = self._build_content_funnel(p)
        ab_testing       = self._build_ab_testing(p)
        tool_stack       = self._build_tool_stack(p)
        iteration_framework = self._build_iteration_framework(p)

        return {
            'status':              'success',
            'generated_at':        datetime.now().isoformat(),
            'analyst':             self.name,
            'game_info': {
                'name':            p['game_name'],
                'type':            p['game_type'],
                'monetization':    p['monetization_type'],
                'stage':           p['launch_stage'],
                'expected_dau':    p['expected_dau'],
            },
            'kpi_system':          kpi_system,
            'tracking_plan':       tracking_plan,
            'retention_model':     retention_model,
            'monetization_model':  monetization_model,
            'content_funnel':      content_funnel,
            'ab_testing':          ab_testing,
            'tool_stack':          tool_stack,
            'iteration_framework': iteration_framework,
        }

    # ─────────────────────────────────────────────────────────────
    # KPI 体系
    # ─────────────────────────────────────────────────────────────

    def _build_kpi_system(self, p: Dict) -> Dict:
        gt  = p['game_type']
        mt  = p['monetization_type']
        has_iap = p['has_iap']

        tier1 = [
            {
                'metric': 'DAU（日活跃用户数）',
                'formula': '当日有过至少一次会话的唯一用户数',
                'why': '最基础的健康度指标，用于判断游戏是否在增长/衰退',
                'benchmark': '- 软发布：关注趋势，不看绝对值\n- 正式发布后第1个月：持续增长信号',
                'alert': 'DAU 连续7天下跌 > 10% → 立即分析原因',
            },
            {
                'metric': 'Day-1 / Day-7 / Day-30 留存率',
                'formula': 'Day-N 留存 = 第N天仍活跃的用户 / 安装当天用户数',
                'why': '游戏生命力最核心指标。D1 < 30% 基本宣告失败，D30 > 10% 才有长期价值',
                'benchmark': self._format_benchmark(self.retention_benchmarks.get(
                    self._type_key(gt), self.retention_benchmarks['rpg'])),
                'alert': 'D1 < 25% → 新手引导有严重问题，优先修',
            },
        ]

        if has_iap:
            tier1 += [
                {
                    'metric': 'ARPU（每日活跃用户平均收入）',
                    'formula': 'ARPU = 当日总收入 / DAU',
                    'why': '判断每个活跃用户创造的价值，衡量变现效率',
                    'benchmark': self._format_monetization_benchmark(
                        self.monetization_benchmarks.get(self._type_key(gt), self.monetization_benchmarks['rpg']), 'arpu_monthly'),
                    'alert': 'ARPU 持续低于行业均值 → 价格/商品/触达点需要优化',
                },
                {
                    'metric': 'ARPPU（付费用户平均收入）',
                    'formula': 'ARPPU = 当月总收入 / 当月付费用户数',
                    'why': '衡量付费用户的消费深度，过低说明高价值商品未被购买',
                    'benchmark': self._format_monetization_benchmark(
                        self.monetization_benchmarks.get(self._type_key(gt), self.monetization_benchmarks['rpg']), 'arppu_monthly'),
                    'alert': 'ARPPU 高但付费率低 → 存在大R少量消费，长期不健康',
                },
                {
                    'metric': '付费转化率',
                    'formula': '付费用户数 / 总活跃用户数',
                    'why': '衡量免费用户转化为付费用户的能力',
                    'benchmark': self._format_monetization_benchmark(
                        self.monetization_benchmarks.get(self._type_key(gt), self.monetization_benchmarks['rpg']), 'conversion_rate'),
                    'alert': '转化率 < 1% → 内购定价或展示时机有问题',
                },
            ]

        tier2 = [
            {'metric': 'MAU（月活跃用户）',      'formula': '30天内有活跃的唯一用户数', 'why': '衡量游戏的月度用户规模'},
            {'metric': 'Stickiness（粘性）',     'formula': 'DAU / MAU，目标>20%',    'why': '衡量用户每月平均来几天'},
            {'metric': '平均会话时长',            'formula': '总游玩时长 / 会话数',    'why': '衡量单次游玩深度，过短=不好玩，过长=可能流失点太晚'},
            {'metric': '新增用户数 (New Install)', 'formula': '当日首次安装的用户数',  'why': '增长来源，需与留存率配合分析'},
            {'metric': '卸载率',                  'formula': '7天内卸载 / 安装数',    'why': 'Android 可测量，过高说明新手体验差'},
        ]

        if p.get('has_multiplayer'):
            tier2.append({'metric': '匹配成功率', 'formula': '成功匹配 / 尝试匹配次数', 'why': '过低说明玩家基数不足或匹配算法问题'})
            tier2.append({'metric': 'PvP 局均时长', 'formula': '对战总时长 / 对战局数', 'why': '是否在设计目标范围内'})

        if p.get('has_gacha'):
            tier2.append({'metric': '抽卡转化漏斗', 'formula': '点击抽卡界面→查看概率→实际抽卡→复购', 'why': '识别抽卡流程的流失节点'})

        tier3 = [
            {'metric': 'LTV（生命周期价值）',  'formula': 'LTV = ARPU × 平均留存天数（或用模型预测）', 'why': '决定获客成本上限：CAC < LTV 才赚钱'},
            {'metric': 'ROI（投资回报率）',   'formula': 'ROI = (LTV - CAC) / CAC',               'why': '衡量买量是否值得'},
            {'metric': 'K 因子（病毒传播）', 'formula': 'K = 每用户邀请人数 × 被邀请者转化率',      'why': 'K > 1 表示病毒增长，游戏自我驱动扩张'},
        ]

        return {
            'framework': 'AARRR 海盗指标框架',
            'framework_desc': 'Acquisition（获客）→ Activation（激活）→ Retention（留存）→ Revenue（变现）→ Referral（传播）',
            'tier1_north_star': tier1,
            'tier2_health_metrics': tier2,
            'tier3_growth_metrics': tier3,
            'review_cadence': {
                'daily':   'DAU、新增、收入、崩溃率（运营值班必看）',
                'weekly':  'D1/D7留存、ARPU、付费转化、主要漏斗',
                'monthly': 'D30留存、LTV模型更新、用户分层分析、A/B结果',
                'quarterly': 'K因子、获客成本、版本ROI复盘',
            },
        }

    def _format_benchmark(self, b: Dict) -> str:
        if not b:
            return '无行业数据'
        lines = []
        for day, vals in b.items():
            lines.append(f'{day}: 低于{vals["poor"]}=危险 | 均值{vals["avg"]} | 优秀>{vals["excellent"]}')
        return '\n'.join(lines)

    def _format_monetization_benchmark(self, b: Dict, key: str) -> str:
        if not b or key not in b:
            return '无行业数据'
        vals = b[key]
        return f'行业均值: {vals["avg"]} | 良好: {vals["good"]} | 优秀: >{vals["excellent"]}'

    # ─────────────────────────────────────────────────────────────
    # 埋点方案
    # ─────────────────────────────────────────────────────────────

    def _build_tracking_plan(self, p: Dict) -> Dict:
        gt = p['game_type']

        # 基础事件（所有游戏必须）
        base_events = [
            {
                'event': 'app_open',
                'trigger': '每次游戏启动时',
                'properties': ['session_id', 'platform', 'app_version', 'device_model', 'os_version', 'network_type'],
                'purpose': '计算 DAU、会话数、设备分布',
            },
            {
                'event': 'app_close / session_end',
                'trigger': '游戏退出或切到后台超过30秒',
                'properties': ['session_id', 'session_duration_sec', 'screens_visited'],
                'purpose': '计算会话时长、用户行为路径',
            },
            {
                'event': 'user_registration',
                'trigger': '新用户首次注册',
                'properties': ['user_id', 'registration_method', 'country', 'install_source'],
                'purpose': '新增用户统计、注册漏斗分析',
            },
            {
                'event': 'tutorial_step_complete',
                'trigger': '完成教学的每个关键步骤',
                'properties': ['step_id', 'step_name', 'time_to_complete_sec', 'retry_count'],
                'purpose': '找到教学流失节点，优化新手引导',
            },
            {
                'event': 'tutorial_complete / tutorial_skip',
                'trigger': '教学全部完成或玩家选择跳过',
                'properties': ['total_tutorial_time_sec', 'skip_at_step'],
                'purpose': '计算教学完成率，是 D1 留存的最强预测指标',
            },
        ]

        # 进度事件
        progress_events = [
            {
                'event': 'level_start',
                'trigger': '玩家开始一个关卡/章节',
                'properties': ['level_id', 'level_name', 'attempt_number', 'player_level', 'equipment_power'],
                'purpose': '分析玩家进度分布，识别卡关点',
            },
            {
                'event': 'level_complete',
                'trigger': '玩家成功通过关卡',
                'properties': ['level_id', 'time_to_complete_sec', 'stars', 'moves_used', 'boosters_used'],
                'purpose': '计算通过率，分析关卡难度是否合理',
            },
            {
                'event': 'level_fail',
                'trigger': '玩家失败',
                'properties': ['level_id', 'fail_reason', 'attempt_number', 'time_played_sec', 'hp_remaining'],
                'purpose': '识别关卡数值问题，与数值策划联动调整',
            },
        ]

        if gt in ['rpg', 'action_rpg', 'open_world']:
            progress_events += [
                {
                    'event': 'character_level_up',
                    'trigger': '角色升级',
                    'properties': ['new_level', 'time_since_last_levelup_sec', 'exp_source'],
                    'purpose': '分析成长速度是否符合设计，过快/过慢都是问题',
                },
                {
                    'event': 'item_acquired',
                    'trigger': '获得物品（掉落/购买/任务奖励）',
                    'properties': ['item_id', 'item_rarity', 'acquisition_source', 'quantity'],
                    'purpose': '分析掉落分布，验证数值策划的掉落率设计',
                },
                {
                    'event': 'equipment_enhanced',
                    'trigger': '强化/升级装备',
                    'properties': ['item_id', 'from_level', 'to_level', 'material_spent', 'success'],
                    'purpose': '分析强化消耗，验证经济模型平衡性',
                },
            ]

        # 社交/多人事件
        social_events = []
        if p.get('has_multiplayer'):
            social_events = [
                {
                    'event': 'pvp_match_start',
                    'trigger': '对战开始',
                    'properties': ['match_id', 'mode', 'player_mmr', 'opponent_mmr', 'map'],
                    'purpose': '分析匹配质量，MMR差距是否合理',
                },
                {
                    'event': 'pvp_match_end',
                    'trigger': '对战结束',
                    'properties': ['match_id', 'result', 'duration_sec', 'mmr_change', 'quit_early'],
                    'purpose': '计算胜率分布，识别平衡性问题',
                },
            ]

        # 付费事件
        iap_events = []
        if p['has_iap']:
            iap_events = [
                {
                    'event': 'store_open',
                    'trigger': '玩家打开商城界面',
                    'properties': ['entry_point', 'player_currency_balance', 'player_level', 'days_since_install'],
                    'purpose': '分析商城触达率，哪个入口最有效',
                },
                {
                    'event': 'iap_initiated',
                    'trigger': '玩家点击购买按钮',
                    'properties': ['product_id', 'price_usd', 'entry_point', 'is_first_purchase'],
                    'purpose': '计算购买意向，购买放弃率',
                },
                {
                    'event': 'iap_complete',
                    'trigger': '支付成功并发货',
                    'properties': ['product_id', 'price_usd', 'currency', 'is_first_purchase', 'payment_method'],
                    'purpose': '计算转化率、ARPU，追踪付费漏斗',
                },
                {
                    'event': 'iap_failed',
                    'trigger': '支付失败',
                    'properties': ['product_id', 'fail_reason', 'step_failed'],
                    'purpose': '找到支付失败原因，优化支付流程',
                },
                {
                    'event': 'currency_spent',
                    'trigger': '消费游戏内货币',
                    'properties': ['amount', 'item_id', 'context', 'balance_before', 'balance_after'],
                    'purpose': '追踪货币流向，验证经济模型',
                },
            ]

        if p.get('has_gacha'):
            iap_events.append({
                'event': 'gacha_pull',
                'trigger': '每次抽卡',
                'properties': ['pool_id', 'pull_count', 'results', 'pity_count_before', 'pity_count_after', 'cost'],
                'purpose': '验证概率实现正确性，分析付费深度',
            })

        return {
            'implementation_guide': [
                '埋点原则1：事件名用 snake_case，全局统一（如 level_start 不要写成 LevelStart）',
                '埋点原则2：每个事件必须有 user_id + session_id + timestamp（服务端时间）',
                '埋点原则3：先定义事件字典，再开发，避免上线后无法回溯历史数据',
                '埋点原则4：金钱相关事件（iap_complete）必须在服务端埋点，不信任客户端',
                '埋点原则5：测试埋点时用"调试模式"，验证每个事件属性是否完整',
            ],
            'base_events':     base_events,
            'progress_events': progress_events,
            'social_events':   social_events,
            'iap_events':      iap_events,
            'event_summary': {
                'total_events': len(base_events) + len(progress_events) + len(social_events) + len(iap_events),
                'priority_order': '1.基础事件 → 2.教程事件 → 3.进度事件 → 4.付费事件 → 5.社交事件',
            },
        }

    # ─────────────────────────────────────────────────────────────
    # 留存分析模型
    # ─────────────────────────────────────────────────────────────

    def _build_retention_model(self, p: Dict) -> Dict:
        gt    = p['game_type']
        stage = p['launch_stage']
        bench = self.retention_benchmarks.get(self._type_key(gt), self.retention_benchmarks['rpg'])

        return {
            'benchmarks': bench,
            'analysis_methods': [
                {
                    'method': '留存曲线分析',
                    'how': '按安装日期分组（Cohort），追踪每组用户在后续N天的留存率',
                    'insight': '曲线趋于水平 = 有硬核玩家基础；持续下降不停 = 没有留住任何用户',
                    'tool': 'Firebase Analytics / GameAnalytics / 自建 SQL',
                },
                {
                    'method': '流失节点分析',
                    'how': '识别留存骤降的具体节点（如D3→D4留存大幅低于D2→D3）',
                    'insight': '骤降点意味着玩家在该阶段遇到了"放弃"事件',
                    'tool': '查询该时间段内 level_fail + app_close 事件的集中分布',
                },
                {
                    'method': '流失用户调研',
                    'how': '对30天内流失的用户推送问卷（3题以内）',
                    'insight': '数据告诉你"何时流失"，用户告诉你"为何流失"',
                    'tool': 'SurveyMonkey / Typeform（App内推送）',
                },
                {
                    'method': 'Player Segmentation（用户分层）',
                    'how': '按行为分层：新手（D1-7）/ 成长期（D8-30）/ 核心（D30+）/ 鲸鱼付费用户',
                    'insight': '不同层次用户需要不同的留存策略',
                    'tool': 'Amplitude / Mixpanel 用户分群功能',
                },
            ],
            'retention_drivers': self._get_retention_drivers(gt),
            'alert_thresholds': {
                'D1': f'< {bench["day1"]["poor"]}：新手引导紧急优化',
                'D7': f'< {bench["day7"]["poor"]}：中期内容量或成长感有问题',
                'D30': f'< {bench["day30"]["poor"]}：长期核心玩法需要重新审视',
            },
            'improvement_levers': [
                {
                    'lever': '新手引导优化',
                    'impact': 'D1 留存 +5~15%',
                    'method': '缩短教程至10分钟内，确保首次"爽点"在5分钟内出现',
                },
                {
                    'lever': '推送通知策略',
                    'impact': 'D7 留存 +3~8%',
                    'method': '个性化推送（"你的装备快制作完成了"），不要群发',
                },
                {
                    'lever': '每日任务/签到',
                    'impact': 'D30 留存 +5~12%',
                    'method': '每日有明确的"今天应该做什么"目标',
                },
                {
                    'lever': '关卡/内容难度校准',
                    'impact': '减少因挫败流失，+3~10%',
                    'method': '将失败率 > 60% 的关卡降低难度（或加入软救助机制）',
                },
                {
                    'lever': '社交功能',
                    'impact': 'D30 留存 +8~20%',
                    'method': '有好友的玩家留存率通常是无好友玩家的2倍',
                },
            ],
        }

    def _get_retention_drivers(self, gt: str) -> List[str]:
        drivers = {
            'rpg':        ['主线剧情进度（玩家想知道故事结局）', '装备成长系统（每天有可追求的目标）', '任务重置（日常任务驱动回访）'],
            'action_rpg': ['新装备/Boss（持续的内容更新）', '构筑深度（每次游玩都想尝试新构筑）', '挑战模式（极限挑战驱动高技术玩家）'],
            'fps':        ['赛季内容（皮肤/武器/排名重置）', '好友约战（社交驱动）', '技术进步感（段位提升）'],
            'roguelike':  ['解锁深度（每次新的永久解锁）', '随机性（永远有新的构筑可以尝试）', '极限挑战（击败最终Boss）'],
            'strategy':   ['资源积累（挂机感）', '联盟战争（社交竞争）', '科技树探索（长期目标）'],
            'casual':     ['新关卡（持续发布）', '活动限时（稀缺感）', '好友比较（超越邻居）'],
        }
        return drivers.get(self._type_key(gt), drivers['rpg'])

    # ─────────────────────────────────────────────────────────────
    # 付费分析模型
    # ─────────────────────────────────────────────────────────────

    def _build_monetization_model(self, p: Dict) -> Dict:
        if not p['has_iap']:
            return {
                'note': '买断制游戏的核心货币化指标是销量和评价，而非传统F2P付费漏斗',
                'premium_kpis': [
                    '总下载量 / 总销量',
                    '退款率（<5% 为健康）',
                    '评分（4.0+目标）和评价情感分析',
                    'DLC 转化率（若有扩展内容）',
                ],
            }

        gt    = p['game_type']
        bench = self.monetization_benchmarks.get(self._type_key(gt), self.monetization_benchmarks['rpg'])

        return {
            'benchmarks': bench,
            'payment_funnel': {
                'stages': [
                    {'stage': '1. 游戏安装',       'rate': '100%',    'note': '基准'},
                    {'stage': '2. 完成新手引导',    'rate': '55-75%',  'note': '未完成教程的用户极少付费'},
                    {'stage': '3. 达到付费触发点',  'rate': '20-40%',  'note': '典型触发：资源不足/特惠弹窗/关卡卡关'},
                    {'stage': '4. 打开商城',        'rate': '8-20%',   'note': '打开商城 = 有付费意向'},
                    {'stage': '5. 首次付费',        'rate': '1.5-6%',  'note': '行业付费转化率'},
                    {'stage': '6. 二次付费（复购）', 'rate': '40-60% of 首付', 'note': '首次付费是最难的，成功后大幅提升复购可能'},
                ],
                'optimization_tips': [
                    '首次付费价格建议≤$1.99（降低心理门槛）',
                    '付费触发时机：关卡失败第2-3次时展示软货币广告/道具',
                    '限时特惠：首充双倍是最有效的首次转化手段',
                    '付费展示时机：D3-D7是付费转化最佳窗口期',
                ],
            },
            'user_segments': [
                {
                    'segment': '🐟 鱼（免费用户）',
                    'proportion': '94-98%',
                    'strategy': '广告变现（视频激励广告），不强制付费',
                    'clv': '低，但数量大，广告收入可观',
                },
                {
                    'segment': '🐬 海豚（小R付费用户）',
                    'proportion': '2-5%',
                    'strategy': '月卡/通行证/首充特惠，持续提供物超所值感',
                    'clv': '中，$5-50/月，数量多',
                },
                {
                    'segment': '🐋 鲸鱼（大R付费用户）',
                    'proportion': '0.1-0.5%',
                    'strategy': '专属礼包/VIP特权/1对1客服/高价值社交展示（称号/皮肤）',
                    'clv': '极高，$100-10000+/月，产生20-50%总收入',
                },
            ],
            'ltv_model': {
                'simple_formula': 'LTV = ARPU × 平均活跃天数',
                'example': f'若 ARPU = $1/天，平均活跃 30 天，则 LTV ≈ $30',
                'advanced': '使用指数平滑留存曲线积分：LTV = Σ(Day-N 留存率 × ARPU)',
                'acquisition_rule': 'CAC（获客成本）< LTV × 0.3 时，买量才有ROI',
            },
            'gacha_analysis': {
                'apply': p.get('has_gacha', False),
                'metrics': [
                    '抽卡转化率（看过抽卡界面→实际抽卡）：目标>30%',
                    '平均每用户抽卡次数/月',
                    '保底消耗率（在软保底前出SSR的比例）',
                    '复购间隔（两次抽卡的平均天数）',
                    '放弃率（打开抽卡界面但未抽就离开）',
                ],
            } if p.get('has_gacha') else None,
        }

    # ─────────────────────────────────────────────────────────────
    # 内容漏斗分析
    # ─────────────────────────────────────────────────────────────

    def _build_content_funnel(self, p: Dict) -> Dict:
        gt = p['game_type']

        difficulty_analysis = {
            'metric': '关卡失败率',
            'healthy_range': '20-45%（太低=太简单，太高=太难）',
            'alert_high': '失败率 > 60% → 该关卡数值过难，通知数值策划调整',
            'alert_low': '失败率 < 10% → 该关卡无挑战性，可能后续关卡跳得太慢',
            'sql_example': '''-- 关卡失败率统计（伪代码）
SELECT
    level_id,
    level_name,
    COUNT(*) as total_attempts,
    SUM(CASE WHEN result = "fail" THEN 1 ELSE 0 END) as fails,
    SUM(CASE WHEN result = "fail" THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as fail_rate
FROM level_events
WHERE date >= DATE_SUB(NOW(), INTERVAL 7 DAY)
GROUP BY level_id
ORDER BY fail_rate DESC
LIMIT 20;  -- 找出失败率最高的20个关卡''',
        }

        progression_funnel = {
            'description': '追踪玩家在内容中的进度分布，识别"卡墙"',
            'metrics': [
                '各关卡/区域的玩家到达率（相对于总用户）',
                '各关卡的平均尝试次数',
                '首次通关所需时间',
                '使用道具/续命的关卡分布',
            ],
            'typical_dropoff': [
                '教学结束后：10-30% 玩家在此流失（新手引导过长）',
                '首个难度跳升点：20-40% 玩家流失（难度曲线不平滑）',
                '付费墙前：10-25% 玩家流失（如果强制付费才能继续）',
                '中后期内容：老玩家自然流失（无新内容驱动）',
            ],
        }

        if gt in ['rpg', 'action_rpg', 'open_world']:
            economy_analysis = {
                'metrics': [
                    '每日金币/宝石净流通量（产出 - 消耗）',
                    '资源余额分布（玩家平均持有量）',
                    '高价值消耗触发率（花大量资源强化/抽卡的频率）',
                    '资源积压警报（持有量 > 7天消耗 = 可能无意义了）',
                ],
                'balance_signals': {
                    '通胀信号': '玩家平均余额持续增长且增长率 > 月收益20%',
                    '通缩信号': '玩家平均余额接近0，消耗频率降低',
                    '健康状态': '平均余额稳定，消耗有规律，无大量囤积',
                },
            }
        else:
            economy_analysis = None

        return {
            'difficulty_analysis': difficulty_analysis,
            'progression_funnel':  progression_funnel,
            'economy_analysis':    economy_analysis,
            'session_analysis': {
                'target_session': self._get_target_session(gt),
                'metrics': [
                    '平均会话时长（目标：接近设计值）',
                    '每日会话次数分布（休闲游戏应>1次/天）',
                    '中断点分析（玩家在哪个界面退出最多）',
                ],
            },
        }

    def _get_target_session(self, gt: str) -> str:
        sessions = {
            'rpg': '30-90 分钟/次',
            'action_rpg': '20-60 分钟/次',
            'fps': '20-60 分钟/次',
            'roguelike': '20-60 分钟/次',
            'casual': '5-20 分钟/次（多次/天）',
            'strategy': '30-120 分钟/次',
            'simulation': '30-120 分钟/次',
        }
        return sessions.get(gt, '20-60 分钟/次')

    # ─────────────────────────────────────────────────────────────
    # A/B 测试方案
    # ─────────────────────────────────────────────────────────────

    def _build_ab_testing(self, p: Dict) -> Dict:
        gt = p['game_type']

        priority_tests = [
            {
                'priority': 1,
                'name': '新手引导时长优化',
                'hypothesis': '缩短教程长度可以提升 D1 留存',
                'variants': ['当前版本（对照）', '缩短30%（实验A）', '加入更多互动（实验B）'],
                'metric': 'D1 留存率',
                'sample_size': '各组至少1000用户',
                'duration': '7天',
            },
            {
                'priority': 2,
                'name': '新手引导爽点前置',
                'hypothesis': '让玩家在5分钟内体验到"爽点"可以提升 D1 留存',
                'variants': ['当前顺序（对照）', '将第一个Boss战前置到5分钟内'],
                'metric': 'D1 留存率 + 教程完成率',
                'sample_size': '各组2000用户',
                'duration': '7天',
            },
        ]

        if p['has_iap']:
            priority_tests += [
                {
                    'priority': 3,
                    'name': '首充价格测试',
                    'hypothesis': '调整首充价格和内容性价比可以提升转化率',
                    'variants': ['$0.99（门槛最低）', '$1.99（当前）', '$4.99（高价值包）'],
                    'metric': '首次付费转化率 + 首周ARPU',
                    'sample_size': '各组5000用户',
                    'duration': '14天',
                },
                {
                    'priority': 4,
                    'name': '付费触发时机测试',
                    'hypothesis': '在关卡失败第N次时展示付费提示的最佳时机',
                    'variants': ['第1次失败', '第2次失败（当前）', '第3次失败'],
                    'metric': '付费转化率 + 用户满意度（差评率）',
                    'sample_size': '各组3000用户',
                    'duration': '14天',
                },
            ]

        stat_guide = {
            'minimum_sample': '每组至少1000用户（流量少时可放宽，但结论置信度低）',
            'significance_level': '置信度 ≥ 95%（p < 0.05）时才认为实验有效',
            'duration_rule': '至少运行完整7天（排除周末/工作日效应），且每组样本量达标',
            'common_mistakes': [
                '提前停止实验（看到好结果就停止，但可能是随机噪声）',
                '同时运行多个重叠实验（结果相互干扰）',
                '忘记考虑新用户 vs 老用户差异（新用户测试≠老用户行为）',
                '只看短期指标（D1提升但D7下降是常见陷阱）',
            ],
        }

        return {
            'priority_tests': priority_tests,
            'stat_significance_guide': stat_guide,
            'what_not_to_ab_test': [
                '核心游戏机制（变化太大，影响所有指标）',
                '流量极少时（<500用户/天不适合做AB）',
                '已知危险的功能（先灰度发布，不要AB）',
            ],
        }

    # ─────────────────────────────────────────────────────────────
    # 工具栈推荐
    # ─────────────────────────────────────────────────────────────

    def _build_tool_stack(self, p: Dict) -> List[Dict]:
        dau = p['expected_dau']
        team = p['team_size']
        has_iap = p['has_iap']
        platforms = p.get('target_platforms', ['mobile'])

        tools = []

        # 游戏分析主平台
        if dau in ['<1k', '1k-10k'] or team in ['solo', 'small']:
            tools.append({
                'category': '游戏分析平台（核心）',
                'recommended': 'GameAnalytics',
                'why': '免费、游戏专用、自带留存/关卡/漏斗分析，小团队首选',
                'cost': '免费（高级功能付费）',
                'setup': 'Unity SDK 接入约半天，提供开箱即用的游戏指标面板',
                'alternative': 'Firebase Analytics（Google生态）',
            })
        else:
            tools.append({
                'category': '游戏分析平台（核心）',
                'recommended': 'Amplitude 或 Mixpanel',
                'why': '强大的用户行为分析、留存曲线、漏斗分析、用户分群',
                'cost': 'Amplitude 免费版支持10M事件/月，付费版$995+/月',
                'setup': 'Unity SDK + 完整埋点方案约1周',
                'alternative': 'Firebase Analytics（免费，但功能较基础）',
            })

        # Unity内置选项
        tools.append({
            'category': 'Unity 官方分析',
            'recommended': 'Unity Analytics（Unity Dashboard 内置）',
            'why': 'Unity 项目原生集成，不需要额外SDK，基础指标免费',
            'cost': '免费（基础）/ $2000+/月（UGS Pro）',
            'setup': 'Unity Project Settings → Services 中一键开启',
            'alternative': '与 GameAnalytics 并用，互补',
        })

        # 崩溃监控
        tools.append({
            'category': '崩溃监控',
            'recommended': 'Firebase Crashlytics',
            'why': '免费、实时崩溃报告、堆栈追踪、ANR 检测、移动端最佳选择',
            'cost': '免费',
            'setup': 'Firebase SDK 接入，约2小时',
            'alternative': 'Sentry（跨平台，PC游戏友好）',
        })

        if has_iap and 'mobile' in platforms:
            tools.append({
                'category': '移动端归因（买量必备）',
                'recommended': 'AppsFlyer',
                'why': '最主流的移动归因平台，追踪广告→安装→付费的完整链路',
                'cost': '$0.05-0.07 per attribution（有免费tier）',
                'setup': 'Unity SDK + 配置广告平台',
                'alternative': 'Adjust（同等水平，价格相近）',
            })

            tools.append({
                'category': 'A/B 测试平台',
                'recommended': 'Firebase Remote Config + A/B Testing',
                'why': '免费、与 Firebase Analytics 深度集成，无需客户端发版即可调整参数',
                'cost': '免费',
                'setup': '接入 Firebase SDK 后约1天配置',
                'alternative': 'GameAnalytics 内置 A/B（更简单）',
            })

        tools.append({
            'category': '数据仓库（中大型项目）',
            'recommended': 'BigQuery（GCP）或 Snowflake',
            'why': '将所有事件存储到数仓，进行自定义 SQL 查询，突破第三方工具限制',
            'cost': 'BigQuery: 前1TB查询免费，$5/TB后续',
            'setup': 'Firebase → BigQuery 自动导出，配置约1天',
            'alternative': 'Redshift（AWS生态）',
            'note': f'{"DAU < 1万时暂不需要，用第三方工具足够" if dau in ["<1k","1k-10k"] else "DAU > 1万时强烈推荐，自建查询灵活性无可替代"}',
        })

        return tools

    # ─────────────────────────────────────────────────────────────
    # 迭代决策框架
    # ─────────────────────────────────────────────────────────────

    def _build_iteration_framework(self, p: Dict) -> Dict:
        return {
            'decision_tree': [
                {
                    'signal': 'D1 留存 < 行业均值',
                    'priority': 'P0 — 立即行动',
                    'investigation': [
                        '查看教程完成率（< 60% → 教程太长/无聊）',
                        '查看教程流失节点（哪一步大量退出）',
                        '查看首次会话时长（< 5分钟 → 第一个爽点太晚）',
                    ],
                    'action': '优先优化新手引导，这是所有指标的根基',
                },
                {
                    'signal': 'D7 留存正常但 D30 急剧下降',
                    'priority': 'P1 — 本周处理',
                    'investigation': [
                        '查看中期内容进度分布（是否大量玩家在同一位置停止）',
                        '查看关卡失败率（中期是否有数值墙）',
                        '查看每日任务/活动完成率（驱动回访的机制是否有效）',
                    ],
                    'action': '中期内容扩充或难度调整，与关卡策划师联动',
                },
                {
                    'signal': '付费转化率 < 1%',
                    'priority': 'P1 — 本周处理',
                    'investigation': [
                        '查看商城打开率（玩家有没有找到商城入口）',
                        '查看付费触发时机（是否在玩家无需求时展示）',
                        '查看首充商品性价比（与竞品对比）',
                    ],
                    'action': '优化付费展示时机和首充方案，联系数值策划调整价格策略',
                },
                {
                    'signal': '某关卡失败率 > 60%',
                    'priority': 'P1 — 通知数值策划',
                    'investigation': [
                        '查看该关卡的具体失败原因（hp_remaining 分布）',
                        '查看该关卡是否是自然流失节点',
                        '查看使用续命道具的比例',
                    ],
                    'action': '将数据报告发给数值策划师，请求关卡数值调整',
                },
                {
                    'signal': 'ARPU 持续增长但 DAU 下降',
                    'priority': 'P2 — 观察',
                    'investigation': [
                        '检查是否是付费玩家在支撑，免费玩家大量流失',
                        '确认是否因为限时活动导致短期付费激增',
                    ],
                    'action': '长期警惕：依赖少数大R的游戏生命周期短，需要扩大付费基础',
                },
                {
                    'signal': '崩溃率 > 1%（iOS）或 > 2%（Android）',
                    'priority': 'P0 — 立即修复',
                    'investigation': [
                        '查看 Crashlytics 崩溃堆栈',
                        '定位崩溃设备型号/OS版本',
                    ],
                    'action': '立即发热更修复，同时在商店评分会受到重大影响',
                },
            ],
            'weekly_review_template': [
                '本周 DAU 趋势（↑↓%）',
                'D1/D7 留存对比上周（新增用户队列）',
                '本周收入 & ARPU（对比上周）',
                '本周排名最高的关卡失败率（Top5）',
                '本周崩溃率（对比上周）',
                '本周用户评分变化',
                '本周 P0/P1 数据问题列表',
                '下周优化计划（基于本周数据）',
            ],
            'data_to_design_loop': {
                'description': '数据分析师如何与其他角色协作形成闭环',
                'flow': [
                    {'step': 1, 'from': '数据分析师', 'to': '关卡策划师', 'trigger': '关卡失败率报告', 'action': '调整难度曲线'},
                    {'step': 2, 'from': '数据分析师', 'to': '数值策划师', 'trigger': '经济模型失衡信号', 'action': '调整货币产出/消耗比'},
                    {'step': 3, 'from': '数据分析师', 'to': '系统策划师', 'trigger': '功能使用率报告', 'action': '优化/砍掉低使用率功能'},
                    {'step': 4, 'from': '数据分析师', 'to': 'QA工程师',   'trigger': '崩溃率/ANR报告', 'action': '定向测试问题设备'},
                    {'step': 5, 'from': '所有角色',   'to': '数据分析师', 'trigger': '新版本上线',      'action': '监控新版本数据是否改善目标指标'},
                ],
            },
        }

    # ─────────────────────────────────────────────────────────────
    # 辅助
    # ─────────────────────────────────────────────────────────────

    def _normalize(self, raw: Dict) -> Dict:
        p = dict(raw)
        p.setdefault('game_name', 'My Game')
        p.setdefault('game_type', 'rpg')
        p.setdefault('monetization_type', 'f2p')
        p.setdefault('target_platforms', ['mobile'])
        p.setdefault('features', [])
        p.setdefault('has_multiplayer', 'multiplayer' in p.get('features', []))
        p.setdefault('has_iap', 'iap' in p.get('features', []) or p.get('monetization_type') == 'f2p')
        p.setdefault('has_gacha', 'gacha' in p.get('features', []))
        p.setdefault('launch_stage', 'full_launch')
        p.setdefault('expected_dau', '1k-10k')
        p.setdefault('team_size', 'small')
        if p.get('monetization_type') == 'premium':
            p['has_iap'] = False
        return p

    def _type_key(self, gt: str) -> str:
        mapping = {
            'action_rpg': 'action_rpg', 'open_world': 'rpg', 'action_adventure': 'action_rpg',
            'top_down_rpg': 'rpg', 'metroidvania': 'roguelike', 'top_down': 'roguelike',
            'survival': 'roguelike', 'tps': 'fps', 'battle_royale': 'fps',
            'fighting': 'casual', 'racing': 'casual', 'puzzle': 'casual',
            'card': 'strategy', '2d_platformer': 'casual', 'narrative': 'rpg',
        }
        if gt in self.retention_benchmarks:
            return gt
        return mapping.get(gt, 'rpg')
