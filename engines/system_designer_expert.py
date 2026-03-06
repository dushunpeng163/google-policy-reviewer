#!/usr/bin/env python3
"""
系统策划师 (System Designer Expert)

理论基础:
- MDA 框架 (Mechanics / Dynamics / Aesthetics) — Hunicke, LeBlanc, Zubek
- Jesse Schell《游戏设计艺术》100 透镜体系
- Marc LeBlanc 8 种乐趣分类
- Bartle 玩家类型理论 (Achiever / Explorer / Socializer / Killer)
- 心流理论 (Flow) — Csikszentmihalyi

职责:
- 根据游戏概念生成核心循环架构
- 定义系统清单与依赖关系
- 输出 MDA 分析与设计支柱
- 为架构师提供技术可行性评估标记
"""

from typing import Dict, List, Any
from datetime import datetime


class SystemDesignerExpert:
    """系统策划师 — 游戏机制与系统架构设计专家"""

    def __init__(self):
        self.name = "系统策划师"
        self.version = "1.0.0"
        self._build_knowledge_base()

    # ─────────────────────────────────────────────────────────────
    # 知识库
    # ─────────────────────────────────────────────────────────────

    def _build_knowledge_base(self):
        self._build_core_loops()
        self._build_systems_library()
        self._build_design_principles()

    def _build_core_loops(self):
        """各游戏类型的标准核心循环模板"""
        self.core_loops = {
            'rpg': {
                'primary': [
                    {'step': 1, 'action': '探索世界', 'feedback': '发现新地点、NPC、隐藏事件', 'duration': '5–15 分钟'},
                    {'step': 2, 'action': '遭遇战斗', 'feedback': '即时伤害反馈、技能特效、敌人反应', 'duration': '1–5 分钟'},
                    {'step': 3, 'action': '获得战利品', 'feedback': '掉落动画、稀有度高亮、拾取音效', 'duration': '30 秒'},
                    {'step': 4, 'action': '角色成长', 'feedback': '升级特效、属性提升浮字、技能解锁提示', 'duration': '1–3 分钟'},
                    {'step': 5, 'action': '挑战更强内容', 'feedback': '解锁新区域、Boss 预告、剧情推进', 'duration': '回到步骤 1'},
                ],
                'secondary': [
                    {'name': '任务循环', 'cycle': '20–60 分钟', 'purpose': '提供即时方向感和阶段性成就'},
                    {'name': '装备养成', 'cycle': '1–3 天游玩', 'purpose': '中期成就感和数值持续提升'},
                    {'name': '主线叙事', 'cycle': '整个游戏', 'purpose': '长期留存动力和情感投入'},
                ],
                'tertiary': {'name': '世界叙事弧线', 'description': '玩家在整个游戏历程中构建的情感连接和世界认知'},
                'session_length': '30–90 分钟',
                'engagement_driver': '成长感 + 探索欲 + 叙事悬念',
            },
            'action_rpg': {
                'primary': [
                    {'step': 1, 'action': '进入战斗区域', 'feedback': '敌人出现动画、环境氛围', 'duration': '30 秒'},
                    {'step': 2, 'action': '技能连携战斗', 'feedback': '连击数、技能特效、打击音效、僵直反馈', 'duration': '1–3 分钟'},
                    {'step': 3, 'action': '击败敌人/Boss', 'feedback': '击杀特效、掉落飞出、经验条增长', 'duration': '10 秒'},
                    {'step': 4, 'action': '拾取装备/材料', 'feedback': '品质高亮、属性对比提示', 'duration': '30 秒'},
                    {'step': 5, 'action': '强化/更换装备', 'feedback': '角色变强的数字感和外观变化', 'duration': '2–5 分钟'},
                    {'step': 6, 'action': '挑战更高难度', 'feedback': '新区域解锁、新技能/Boss 预告', 'duration': '回到步骤 1'},
                ],
                'secondary': [
                    {'name': '装备循环', 'cycle': '30–90 分钟', 'purpose': '持续的数值追求和视觉成长'},
                    {'name': '技能成长', 'cycle': '3–7 天游玩', 'purpose': '操作深度和构筑多样性'},
                    {'name': '世界探索', 'cycle': '整个游戏', 'purpose': '内容发现和成就感'},
                ],
                'tertiary': {'name': '构筑体系', 'description': '玩家长期追求最优装备/技能组合的深度系统'},
                'session_length': '20–60 分钟',
                'engagement_driver': '爽快的战斗手感 + 装备追求 + 构筑探索',
            },
            'fps': {
                'primary': [
                    {'step': 1, 'action': '进图/出生', 'feedback': '地图概览、队友位置', 'duration': '30 秒'},
                    {'step': 2, 'action': '移动侦察', 'feedback': '脚步声、环境线索、小地图', 'duration': '1–3 分钟'},
                    {'step': 3, 'action': '交火/击杀', 'feedback': '爆头特效、击杀提示、音效', 'duration': '5–30 秒'},
                    {'step': 4, 'action': '获得资源/据点', 'feedback': '得分增加、语音播报', 'duration': '10 秒'},
                    {'step': 5, 'action': '下一轮/复活', 'feedback': '死亡回放（可选）、选择武器', 'duration': '10–30 秒'},
                ],
                'secondary': [
                    {'name': '一局对战', 'cycle': '10–20 分钟', 'purpose': '胜负的完整体验弧'},
                    {'name': '武器/装备解锁', 'cycle': '数天游玩', 'purpose': '成长感和个性化'},
                    {'name': '赛季/排名', 'cycle': '数月', 'purpose': '长期竞技目标'},
                ],
                'tertiary': {'name': '段位/声望', 'description': '玩家在社区中的长期竞技地位追求'},
                'session_length': '20–60 分钟',
                'engagement_driver': '竞技刺激 + 技术成长 + 社交竞争',
            },
            '2d_platformer': {
                'primary': [
                    {'step': 1, 'action': '进入关卡', 'feedback': '关卡主题视觉、背景音乐', 'duration': '5 秒'},
                    {'step': 2, 'action': '移动跳跃', 'feedback': '手感响应、音效、粒子', 'duration': '持续'},
                    {'step': 3, 'action': '遇到障碍/敌人', 'feedback': '死亡惩罚（轻/重）、尝试欲望', 'duration': '10–60 秒'},
                    {'step': 4, 'action': '克服关卡', 'feedback': '通关特效、隐藏物品提示', 'duration': '1–10 分钟'},
                    {'step': 5, 'action': '进入下一关', 'feedback': '关卡地图推进感', 'duration': '回到步骤 1'},
                ],
                'secondary': [
                    {'name': '世界探索', 'cycle': '1–3 小时', 'purpose': '完美通关和隐藏内容发现'},
                    {'name': '能力解锁', 'cycle': '游戏中期', 'purpose': '玩法多样性和世界重探索'},
                    {'name': '叙事主线', 'cycle': '整个游戏', 'purpose': '情感投入和完成动力'},
                ],
                'tertiary': {'name': '速通/精通', 'description': '高技术玩家的极限挑战和社区展示'},
                'session_length': '15–45 分钟',
                'engagement_driver': '手感爽快 + 挑战克服 + 探索满足',
            },
            'roguelike': {
                'primary': [
                    {'step': 1, 'action': '开始新一局', 'feedback': '随机初始状态、期待感', 'duration': '30 秒'},
                    {'step': 2, 'action': '探索随机房间', 'feedback': '未知内容惊喜、地图探索感', 'duration': '2–5 分钟'},
                    {'step': 3, 'action': '战斗/遭遇事件', 'feedback': '即时战斗反馈、随机事件结果', 'duration': '1–3 分钟'},
                    {'step': 4, 'action': '选择升级/道具', 'feedback': '构筑成形的正反馈', 'duration': '30 秒'},
                    {'step': 5, 'action': '死亡/通关', 'feedback': '死亡原因回顾、元进度解锁', 'duration': '1–3 分钟'},
                ],
                'secondary': [
                    {'name': '单局流程', 'cycle': '20–60 分钟', 'purpose': '完整的高低起伏体验'},
                    {'name': '元进度解锁', 'cycle': '数次游玩', 'purpose': '永久成长感和内容解锁'},
                    {'name': '构筑探索', 'cycle': '长期', 'purpose': '理解系统深度和优化策略'},
                ],
                'tertiary': {'name': '精通深度', 'description': '玩家掌握所有系统后对构筑极限的追求'},
                'session_length': '20–60 分钟',
                'engagement_driver': '随机惊喜 + 策略深度 + 永久成长',
            },
            'strategy': {
                'primary': [
                    {'step': 1, 'action': '评估局势', 'feedback': '清晰的信息面板、当前差距', 'duration': '1–3 分钟'},
                    {'step': 2, 'action': '收集资源', 'feedback': '资源增长数字、进度条', 'duration': '持续'},
                    {'step': 3, 'action': '建设/研究', 'feedback': '建设动画、科技解锁提示', 'duration': '按实时/回合'},
                    {'step': 4, 'action': '扩张/攻击', 'feedback': '战斗结果、领土变化', 'duration': '3–10 分钟'},
                    {'step': 5, 'action': '调整策略', 'feedback': '敌人应对、新威胁出现', 'duration': '回到步骤 1'},
                ],
                'secondary': [
                    {'name': '发展阶段', 'cycle': '30–90 分钟', 'purpose': '从弱到强的成长弧'},
                    {'name': '战役/章节', 'cycle': '数小时', 'purpose': '叙事推进和新挑战'},
                    {'name': '多周目', 'cycle': '长期', 'purpose': '不同策略和难度探索'},
                ],
                'tertiary': {'name': '战略深度', 'description': '玩家掌握各种策略体系后的极限博弈追求'},
                'session_length': '30–180 分钟',
                'engagement_driver': '掌控感 + 策略博弈 + 成长历程',
            },
            'simulation': {
                'primary': [
                    {'step': 1, 'action': '设置/规划', 'feedback': '规划视图、预期收益', 'duration': '5–15 分钟'},
                    {'step': 2, 'action': '系统运行', 'feedback': '自动运营动画、数字增长', 'duration': '实时'},
                    {'step': 3, 'action': '处理事件', 'feedback': '突发事件提醒、决策需求', 'duration': '1–5 分钟'},
                    {'step': 4, 'action': '优化调整', 'feedback': '效率提升、新问题出现', 'duration': '3–10 分钟'},
                    {'step': 5, 'action': '扩张规模', 'feedback': '新内容解锁、成就达成', 'duration': '回到步骤 1'},
                ],
                'secondary': [
                    {'name': '单次会话', 'cycle': '30–120 分钟', 'purpose': '优化和解决问题的满足感'},
                    {'name': '里程碑成就', 'cycle': '数小时', 'purpose': '长期目标感'},
                    {'name': '全内容解锁', 'cycle': '数十小时', 'purpose': '深度玩家的完成感'},
                ],
                'tertiary': {'name': '极限优化', 'description': '追求系统效率极限的深度玩法'},
                'session_length': '30–120 分钟',
                'engagement_driver': '掌控感 + 优化满足 + 系统探索',
            },
            'casual': {
                'primary': [
                    {'step': 1, 'action': '开始关卡', 'feedback': '目标清晰、关卡预览', 'duration': '5 秒'},
                    {'step': 2, 'action': '执行操作', 'feedback': '即时视觉音效反馈', 'duration': '30 秒–2 分钟'},
                    {'step': 3, 'action': '成功/失败', 'feedback': '星级评分、激励失败信息', 'duration': '5 秒'},
                    {'step': 4, 'action': '获得奖励', 'feedback': '金币/道具弹出动画', 'duration': '5 秒'},
                    {'step': 5, 'action': '进入下一关', 'feedback': '关卡地图推进', 'duration': '5 秒'},
                ],
                'secondary': [
                    {'name': '关卡组', 'cycle': '10–30 分钟', 'purpose': '持续进度感'},
                    {'name': '活动/限时内容', 'cycle': '周/月', 'purpose': '回访动力'},
                    {'name': '社交互动', 'cycle': '持续', 'purpose': '社交留存'},
                ],
                'tertiary': {'name': '收集/装扮', 'description': '长期玩家的个性化表达'},
                'session_length': '5–20 分钟',
                'engagement_driver': '低压力放松 + 简单满足感 + 持续进度',
            },
            'survival': {
                'primary': [
                    {'step': 1, 'action': '评估需求', 'feedback': '饥饿/生命值/温度等状态显示', 'duration': '30 秒'},
                    {'step': 2, 'action': '收集资源', 'feedback': '拾取音效、背包填充', 'duration': '3–10 分钟'},
                    {'step': 3, 'action': '建造/制作', 'feedback': '建造完成动画、配方解锁', 'duration': '5–15 分钟'},
                    {'step': 4, 'action': '应对威胁', 'feedback': '战斗/逃跑紧张感', 'duration': '1–5 分钟'},
                    {'step': 5, 'action': '扩大基地', 'feedback': '安全区扩张、更强装备', 'duration': '回到步骤 1'},
                ],
                'secondary': [
                    {'name': '每日存活', 'cycle': '30–90 分钟', 'purpose': '紧张感和成就感'},
                    {'name': '基地建设', 'cycle': '数天游玩', 'purpose': '永久进度感'},
                    {'name': '世界探索', 'cycle': '长期', 'purpose': '发现感和内容解锁'},
                ],
                'tertiary': {'name': '顶级装备', 'description': '最终达到统治世界的强大感'},
                'session_length': '30–120 分钟',
                'engagement_driver': '生存压力 + 建造满足 + 探索发现',
            },
            'fighting': {
                'primary': [
                    {'step': 1, 'action': '选择角色', 'feedback': '角色介绍、差异化展示', 'duration': '30 秒'},
                    {'step': 2, 'action': '对战开始', 'feedback': '气氛铺垫、计时', 'duration': '5 秒'},
                    {'step': 3, 'action': '输出/防御', 'feedback': '打击感、连招视觉、伤害数字', 'duration': '持续'},
                    {'step': 4, 'action': '胜负结算', 'feedback': '胜利/失败动画、连击展示', 'duration': '10 秒'},
                    {'step': 5, 'action': '再战/选择', 'feedback': '积分变化、对手排名', 'duration': '回到步骤 1'},
                ],
                'secondary': [
                    {'name': '单场对战', 'cycle': '1–5 分钟', 'purpose': '胜负博弈的完整体验'},
                    {'name': '角色精通', 'cycle': '数十小时', 'purpose': '操作深度探索'},
                    {'name': '赛季/段位', 'cycle': '数月', 'purpose': '长期竞技目标'},
                ],
                'tertiary': {'name': '顶级竞技', 'description': '在社区中成为高手的认可感'},
                'session_length': '10–30 分钟',
                'engagement_driver': '竞技博弈 + 技术精进 + 社区认可',
            },
            'open_world': {
                'primary': [
                    {'step': 1, 'action': '自由探索', 'feedback': '地标发现、环境叙事、随机事件', 'duration': '5–30 分钟'},
                    {'step': 2, 'action': '接受任务/挑战', 'feedback': '任务接受动画、目标标记', 'duration': '1 分钟'},
                    {'step': 3, 'action': '完成目标', 'feedback': '任务完成特效、奖励发放', 'duration': '5–30 分钟'},
                    {'step': 4, 'action': '角色/装备成长', 'feedback': '升级特效、新能力提示', 'duration': '2–5 分钟'},
                    {'step': 5, 'action': '探索更多区域', 'feedback': '新区域解锁、世界感扩张', 'duration': '回到步骤 1'},
                ],
                'secondary': [
                    {'name': '支线任务', 'cycle': '30–90 分钟', 'purpose': '世界深度和角色成长'},
                    {'name': '主线章节', 'cycle': '数小时', 'purpose': '叙事推进和关键里程碑'},
                    {'name': '世界完成度', 'cycle': '数十小时', 'purpose': '完美主义玩家目标'},
                ],
                'tertiary': {'name': '世界沉浸', 'description': '玩家对游戏世界的深度情感认同'},
                'session_length': '30–120 分钟',
                'engagement_driver': '探索自由 + 世界沉浸 + 成长叙事',
            },
        }

        # 未明确列出的类型默认映射
        self.type_fallback = {
            'action_adventure': 'action_rpg',
            'metroidvania': '2d_platformer',
            'top_down': 'roguelike',
            'top_down_rpg': 'rpg',
            'top_down_shooter': 'fps',
            'twin_stick': 'roguelike',
            'puzzle': 'casual',
            'card': 'strategy',
            'battle_royale': 'fps',
            'narrative': 'rpg',
            'racing': 'casual',
        }

    def _build_systems_library(self):
        """按游戏类型的系统清单"""
        self.systems_by_type = {
            'rpg': [
                {'name': '角色系统',     'purpose': '属性、等级、职业、成长管理', 'priority': 'must', 'complexity': 'high',      'depends_on': []},
                {'name': '战斗系统',     'purpose': '回合制/即时战斗计算与流程', 'priority': 'must', 'complexity': 'very_high', 'depends_on': ['角色系统']},
                {'name': '背包/装备系统', 'purpose': '物品获取、存储、装备、对比', 'priority': 'must', 'complexity': 'medium',    'depends_on': ['角色系统']},
                {'name': '技能系统',     'purpose': '主动/被动技能管理、技能树', 'priority': 'must', 'complexity': 'high',      'depends_on': ['角色系统', '战斗系统']},
                {'name': '任务系统',     'purpose': '目标追踪、任务链、奖励发放', 'priority': 'must', 'complexity': 'medium',    'depends_on': []},
                {'name': '对话/NPC系统', 'purpose': '剧情推进、分支对话、关系度', 'priority': 'must', 'complexity': 'medium',    'depends_on': []},
                {'name': '地图/探索系统', 'purpose': '世界地图、区域解锁、快速移动', 'priority': 'must', 'complexity': 'medium',  'depends_on': []},
                {'name': '存档系统',     'purpose': '进度保存、多存档槽', 'priority': 'must', 'complexity': 'low',       'depends_on': []},
                {'name': '商店系统',     'purpose': 'NPC 商人、物品买卖', 'priority': 'should', 'complexity': 'low',      'depends_on': ['背包/装备系统']},
                {'name': '成就系统',     'purpose': '里程碑记录、玩家激励', 'priority': 'could', 'complexity': 'low',       'depends_on': []},
            ],
            'action_rpg': [
                {'name': '角色控制系统',  'purpose': '流畅的移动、闪避、攻击手感', 'priority': 'must', 'complexity': 'very_high', 'depends_on': []},
                {'name': '战斗系统',     'purpose': '连招、技能、伤害计算', 'priority': 'must', 'complexity': 'very_high', 'depends_on': ['角色控制系统']},
                {'name': '装备系统',     'purpose': '装备掉落、强化、套装效果', 'priority': 'must', 'complexity': 'high',      'depends_on': ['战斗系统']},
                {'name': '技能系统',     'purpose': '主动技能、被动词条、构筑多样性', 'priority': 'must', 'complexity': 'high',   'depends_on': ['战斗系统']},
                {'name': '地图/关卡系统', 'purpose': '区域划分、Boss 门、传送点', 'priority': 'must', 'complexity': 'medium',    'depends_on': []},
                {'name': '背包系统',     'purpose': '物品管理、快速装备', 'priority': 'must', 'complexity': 'medium',    'depends_on': ['装备系统']},
                {'name': '任务系统',     'purpose': '主支线任务引导', 'priority': 'should', 'complexity': 'medium',   'depends_on': []},
                {'name': '存档系统',     'purpose': '检查点、手动存档', 'priority': 'must', 'complexity': 'low',       'depends_on': []},
                {'name': '掉落系统',     'purpose': '随机掉落、保底机制', 'priority': 'must', 'complexity': 'medium',    'depends_on': ['装备系统']},
            ],
            'fps': [
                {'name': '角色控制系统',  'purpose': '第一/三人称移动、瞄准手感', 'priority': 'must', 'complexity': 'very_high', 'depends_on': []},
                {'name': '武器系统',     'purpose': '武器种类、弹道、后座力', 'priority': 'must', 'complexity': 'very_high', 'depends_on': ['角色控制系统']},
                {'name': '伤害系统',     'purpose': '命中判定、部位伤害、护甲', 'priority': 'must', 'complexity': 'high',      'depends_on': ['武器系统']},
                {'name': '对战系统',     'purpose': '局次管理、胜负判定、计分', 'priority': 'must', 'complexity': 'high',      'depends_on': []},
                {'name': 'AI/Bot 系统',  'purpose': '敌人/队友 AI 行为', 'priority': 'must', 'complexity': 'very_high', 'depends_on': []},
                {'name': '地图系统',     'purpose': '场景加载、碰撞、遮掩点', 'priority': 'must', 'complexity': 'high',      'depends_on': []},
                {'name': '成长/解锁系统', 'purpose': '武器皮肤、配件、段位', 'priority': 'should', 'complexity': 'medium',   'depends_on': []},
                {'name': '网络同步系统',  'purpose': '多人延迟补偿、作弊防护', 'priority': 'must', 'complexity': 'very_high', 'depends_on': ['角色控制系统']},
            ],
            'roguelike': [
                {'name': '随机生成系统',  'purpose': '房间/地图随机组合', 'priority': 'must', 'complexity': 'very_high', 'depends_on': []},
                {'name': '战斗系统',     'purpose': '即时/回合战斗', 'priority': 'must', 'complexity': 'high',      'depends_on': []},
                {'name': '道具/升级系统', 'purpose': '单局内临时增益选择', 'priority': 'must', 'complexity': 'high',      'depends_on': []},
                {'name': '元进度系统',   'purpose': '跨局永久解锁', 'priority': 'must', 'complexity': 'medium',    'depends_on': []},
                {'name': '遭遇/事件系统', 'purpose': '随机事件、商店、精英房', 'priority': 'must', 'complexity': 'medium',    'depends_on': ['随机生成系统']},
                {'name': '死亡系统',     'purpose': '死亡惩罚、回顾、元进度结算', 'priority': 'must', 'complexity': 'low',      'depends_on': []},
                {'name': 'Boss 系统',   'purpose': 'Boss 机制设计', 'priority': 'must', 'complexity': 'high',      'depends_on': ['战斗系统']},
            ],
            'strategy': [
                {'name': '资源系统',     'purpose': '多种资源收集、消耗、上限', 'priority': 'must', 'complexity': 'high',      'depends_on': []},
                {'name': '建设系统',     'purpose': '建筑建造、升级、占地', 'priority': 'must', 'complexity': 'high',      'depends_on': ['资源系统']},
                {'name': '科技系统',     'purpose': '科技树研究、解锁', 'priority': 'must', 'complexity': 'medium',    'depends_on': ['资源系统']},
                {'name': '战斗系统',     'purpose': '单位控制、战术', 'priority': 'must', 'complexity': 'very_high', 'depends_on': []},
                {'name': 'AI 对手系统',  'purpose': '电脑对手策略', 'priority': 'must', 'complexity': 'very_high', 'depends_on': []},
                {'name': '地图系统',     'purpose': '地形、视野、领土', 'priority': 'must', 'complexity': 'high',      'depends_on': []},
                {'name': '外交系统',     'purpose': '联盟、贸易、宣战', 'priority': 'should', 'complexity': 'medium',   'depends_on': []},
            ],
        }

        # 通用系统（所有类型都可能需要）
        self.universal_systems = [
            {'name': '音频系统',  'purpose': '背景音乐、音效、动态音频', 'priority': 'must', 'complexity': 'low', 'depends_on': []},
            {'name': 'UI 系统',   'purpose': '主菜单、HUD、弹窗、过场', 'priority': 'must', 'complexity': 'medium', 'depends_on': []},
            {'name': '设置系统',  'purpose': '画质、音量、按键映射', 'priority': 'should', 'complexity': 'low', 'depends_on': []},
            {'name': '本地化系统', 'purpose': '多语言文本管理', 'priority': 'could', 'complexity': 'low', 'depends_on': []},
        ]

    def _build_design_principles(self):
        """Jesse Schell 关键透镜 + 8 种乐趣 + Bartle 类型"""
        self.fun_types = {
            'sensation':   {'cn': '感官体验', 'desc': '视觉、音效、手感的即时满足'},
            'fantasy':     {'cn': '幻想代入', 'desc': '成为另一个人/角色的幻想'},
            'narrative':   {'cn': '叙事沉浸', 'desc': '被故事和世界观吸引'},
            'challenge':   {'cn': '挑战博弈', 'desc': '通过技术和策略克服困难'},
            'fellowship':  {'cn': '社交连接', 'desc': '与他人合作或竞争'},
            'discovery':   {'cn': '探索发现', 'desc': '发现新内容、新规律'},
            'expression':  {'cn': '自我表达', 'desc': '定制化、创作、个性展示'},
            'submission':  {'cn': '放松消遣', 'desc': '低压力、打发时间的体验'},
        }

        self.fun_by_type = {
            'rpg':           ['narrative', 'challenge', 'discovery', 'fantasy'],
            'action_rpg':    ['sensation', 'challenge', 'discovery', 'expression'],
            'fps':           ['challenge', 'sensation', 'fellowship', 'sensation'],
            '2d_platformer': ['challenge', 'sensation', 'discovery'],
            'roguelike':     ['challenge', 'discovery', 'expression'],
            'strategy':      ['challenge', 'discovery', 'fellowship'],
            'simulation':    ['expression', 'discovery', 'submission'],
            'casual':        ['submission', 'sensation', 'fellowship'],
            'survival':      ['challenge', 'discovery', 'expression'],
            'fighting':      ['challenge', 'sensation', 'fellowship'],
            'open_world':    ['discovery', 'fantasy', 'narrative', 'expression'],
        }

        self.bartle_by_type = {
            'rpg':           {'primary': 'explorer',  'secondary': 'achiever'},
            'action_rpg':    {'primary': 'achiever',  'secondary': 'explorer'},
            'fps':           {'primary': 'killer',    'secondary': 'achiever'},
            '2d_platformer': {'primary': 'achiever',  'secondary': 'explorer'},
            'roguelike':     {'primary': 'explorer',  'secondary': 'achiever'},
            'strategy':      {'primary': 'achiever',  'secondary': 'killer'},
            'simulation':    {'primary': 'explorer',  'secondary': 'achiever'},
            'casual':        {'primary': 'achiever',  'secondary': 'socializer'},
            'survival':      {'primary': 'explorer',  'secondary': 'achiever'},
            'fighting':      {'primary': 'killer',    'secondary': 'achiever'},
            'open_world':    {'primary': 'explorer',  'secondary': 'achiever'},
        }

        self.key_lenses_by_type = {
            'rpg':        ['叙事透镜：故事和游戏机制是否相互强化？', '进步透镜：玩家能持续感受到成长吗？', '经济透镜：资源系统是否有趣且平衡？'],
            'action_rpg': ['手感透镜：每次攻击是否有满足感？', '惊喜透镜：掉落是否总能带来期待？', '技能透镜：操作深度是否值得钻研？'],
            'fps':        ['乐趣透镜：每一局是否都有紧张刺激时刻？', '公平透镜：玩家死亡是否感到是自己的错？', '挑战透镜：难度是否与技术成长匹配？'],
            'roguelike':  ['惊喜透镜：每局是否有独特体验？', '选择透镜：每次升级选择是否都有意义？', '死亡透镜：死亡是否推动玩家继续尝试？'],
            'casual':     ['可及性透镜：新玩家能在 30 秒内理解游戏吗？', '进度透镜：每次游玩是否都有明显推进？', '社交透镜：是否有自然的社交分享时机？'],
        }

    # ─────────────────────────────────────────────────────────────
    # 主分析入口
    # ─────────────────────────────────────────────────────────────

    def analyze(self, game_profile: Dict) -> Dict:
        """
        game_profile:
        {
            game_name: str,
            description: str,
            game_type: str,
            tone: str,           # dark/neutral/light/comedic
            target_audience: str, # casual/core/hardcore
            has_multiplayer: bool,
            has_narrative: bool,
            has_monetization: bool,
            has_iap: bool,
            features: list,
            target_platforms: list,
            team_size: str,
        }
        """
        profile = self._normalize(game_profile)
        gt = profile['game_type']

        core_loop     = self._get_core_loop(profile)
        systems       = self._get_systems(profile)
        mda           = self._build_mda(profile, core_loop)
        pillars       = self._build_design_pillars(profile)
        feature_list  = self._build_feature_list(profile, systems)
        player_types  = self._analyze_player_types(profile)
        fun_profile   = self._analyze_fun(profile)
        tech_flags    = self._generate_tech_flags(profile, systems)
        lenses        = self._get_lenses(profile)

        return {
            'status': 'success',
            'generated_at': datetime.now().isoformat(),
            'designer': self.name,
            'game_concept': {
                'name': profile['game_name'],
                'type': gt,
                'type_display': self._type_display(gt),
                'tone': profile['tone'],
                'target_audience': profile['target_audience'],
                'summary': self._summarize(profile),
            },
            'core_loop': core_loop,
            'systems': systems,
            'mda_analysis': mda,
            'design_pillars': pillars,
            'feature_list': feature_list,
            'player_types': player_types,
            'fun_profile': fun_profile,
            'design_lenses': lenses,
            'technical_flags': tech_flags,
        }

    # ─────────────────────────────────────────────────────────────
    # 核心循环
    # ─────────────────────────────────────────────────────────────

    def _get_core_loop(self, profile: Dict) -> Dict:
        gt = profile['game_type']
        resolved = self.type_fallback.get(gt, gt)
        template = self.core_loops.get(resolved, self.core_loops['rpg'])

        # 根据功能调整
        loop = dict(template)
        loop['game_type'] = self._type_display(gt)

        # 多人游戏修改次级循环
        if profile.get('has_multiplayer'):
            loop['secondary'] = loop['secondary'] + [
                {'name': '社交循环', 'cycle': '持续', 'purpose': '好友互动、协作目标、竞争排名'},
            ]

        return loop

    # ─────────────────────────────────────────────────────────────
    # 系统清单
    # ─────────────────────────────────────────────────────────────

    def _get_systems(self, profile: Dict) -> List[Dict]:
        gt = profile['game_type']
        resolved = self.type_fallback.get(gt, gt)
        base = list(self.systems_by_type.get(resolved, self.systems_by_type['rpg']))
        extra = list(self.universal_systems)

        features = profile.get('features', [])

        if profile.get('has_multiplayer') or 'multiplayer' in features:
            base.append({'name': '网络同步系统',   'purpose': '多人状态同步、延迟补偿', 'priority': 'must',   'complexity': 'very_high', 'depends_on': []})
            base.append({'name': '匹配/大厅系统',  'purpose': '玩家匹配、房间管理',    'priority': 'must',   'complexity': 'high',      'depends_on': ['网络同步系统']})

        if profile.get('has_monetization') or profile.get('has_iap') or 'iap' in features:
            base.append({'name': '内购/商城系统',  'purpose': 'IAP 流程、商品展示、购买验证', 'priority': 'must', 'complexity': 'medium', 'depends_on': []})
            base.append({'name': '虚拟货币系统',   'purpose': '货币获取、消耗、防作弊',        'priority': 'must', 'complexity': 'medium', 'depends_on': ['内购/商城系统']})

        if 'hot_update' in features:
            base.append({'name': '热更新系统', 'purpose': '内容热更、版本管理', 'priority': 'should', 'complexity': 'high', 'depends_on': []})

        if 'leaderboard' in features or 'live_ops' in features:
            base.append({'name': '排行榜/运营系统', 'purpose': '排名展示、赛季活动、奖励发放', 'priority': 'should', 'complexity': 'medium', 'depends_on': []})

        if profile.get('has_narrative') or 'narrative' in features:
            if not any(s['name'] == '对话/NPC系统' for s in base):
                base.append({'name': '叙事/剧情系统', 'purpose': '过场、对话、分支剧情管理', 'priority': 'must', 'complexity': 'medium', 'depends_on': []})

        return base + extra

    # ─────────────────────────────────────────────────────────────
    # MDA 分析
    # ─────────────────────────────────────────────────────────────

    def _build_mda(self, profile: Dict, core_loop: Dict) -> Dict:
        gt   = profile['game_type']
        res  = self.type_fallback.get(gt, gt)

        mechanics_map = {
            'rpg':        ['角色属性与成长规则', '战斗伤害计算公式', '掉落率与概率系统', '任务触发与完成条件'],
            'action_rpg': ['角色控制输入响应', '攻击碰撞箱与伤害判定', '技能冷却与资源消耗', '装备属性叠加规则'],
            'fps':        ['弹道物理模型', '命中判定与部位伤害', '移动速度与精准度关系', '武器后座力模式'],
            'roguelike':  ['房间随机生成算法', '道具概率池系统', '元进度解锁条件', 'Boss 阶段触发规则'],
            'strategy':   ['资源产出速率公式', '建设时间与队列系统', '战斗单位属性计算', 'AI 决策权重系统'],
            'casual':     ['关卡目标判断逻辑', '道具效果触发条件', '星级评分计算规则', '体力/生命值恢复机制'],
        }
        dynamics_map = {
            'rpg':        ['玩家形成装备收集习惯', '主线剧情驱动长期游玩', '经济系统产生资源管理决策', '社群形成装备评价体系'],
            'action_rpg': ['玩家追求最优 DPS 构筑', '反复挑战 Boss 直至成功', '装备掉落驱动持续游玩', '连招技术带来表演欲望'],
            'fps':        ['玩家形成战术习惯和路线记忆', '队伍协作产生社交纽带', '段位竞争激发长期投入', '武器偏好形成玩家个性'],
            'roguelike':  ['每局独特的构筑路线探索', '死亡后立即想要重试', '玩家分享极限通关构筑', '逐渐掌握系统的成就感'],
            'strategy':   ['玩家制定并调整长期策略', '资源竞争产生博弈张力', '科技树选择形成风格差异', '失败推动策略反思'],
            'casual':     ['碎片时间填充习惯', '闯关进度产生日常动力', '社交功能带来好友互动', '广告后复活降低沮丧感'],
        }
        aesthetics_map = {
            'rpg':        ['成为强大英雄的幻想感', '沉浸在精心构建的世界中', '探索带来的持续惊喜', '叙事情感投入'],
            'action_rpg': ['击败强敌的爽快感', '装备升级的视觉成长感', '构筑完成时的满足感', '连招成功的技术自豪感'],
            'fps':        ['精准击杀的刺激感', '团队配合获胜的荣耀感', '技术进步的成就感', '竞技胜利的愉悦感'],
            'roguelike':  ['每局独特体验的新鲜感', '险象环生的紧张刺激', '构筑成形的策略满足', '意外发现的惊喜感'],
            'strategy':   ['统治地图的掌控感', '精密计划执行的成就', '战略逆转的戏剧感', '慢慢做大的积累满足'],
            'casual':     ['轻松愉快的消遣体验', '小小成功的持续正反馈', '进度累积的满足感', '与好友比较的社交乐趣'],
        }

        return {
            'mechanics':  mechanics_map.get(res, mechanics_map.get('rpg', [])),
            'dynamics':   dynamics_map.get(res, dynamics_map.get('rpg', [])),
            'aesthetics': aesthetics_map.get(res, aesthetics_map.get('rpg', [])),
            'note': 'Mechanics（规则）→ 产生 Dynamics（玩家行为）→ 形成 Aesthetics（情感体验）。设计时从 Aesthetics 出发反向推导 Mechanics。',
        }

    # ─────────────────────────────────────────────────────────────
    # 设计支柱
    # ─────────────────────────────────────────────────────────────

    def _build_design_pillars(self, profile: Dict) -> List[Dict]:
        gt  = profile['game_type']
        res = self.type_fallback.get(gt, gt)

        pillars_map = {
            'rpg': [
                {'name': '成长感', 'description': '每次游玩都要让玩家感受到变强，数值、技能、装备三条线并行'},
                {'name': '世界沉浸', 'description': '环境、NPC、音乐共同构建可信的世界，任务要有情感重量'},
                {'name': '选择自由', 'description': '多条路线、多种构建，玩家的决策要产生真实差异'},
            ],
            'action_rpg': [
                {'name': '打击手感', 'description': '每次攻击都有充分的视觉/音效/震动反馈，让打击感成为核心享受'},
                {'name': '装备追求', 'description': '掉落系统设计保持玩家永远有下一个追求目标'},
                {'name': '构筑深度', 'description': '技能和装备的组合产生丰富的策略可能性'},
            ],
            'fps': [
                {'name': '竞技公平', 'description': '胜负取决于技术而非运气，死亡时玩家理解死因'},
                {'name': '动态战场', 'description': '每局战场情况不同，永远有新战术可以尝试'},
                {'name': '技术成长', 'description': '新玩家感受到进步空间，老玩家感受到技术壁垒'},
            ],
            'roguelike': [
                {'name': '随机惊喜', 'description': '每局都有独特发现，玩家不能完全预测下一步'},
                {'name': '构筑乐趣', 'description': '道具选择产生有意义的策略多样性'},
                {'name': '死而复生', 'description': '死亡带来学习而非纯粹挫败，元进度保证进步感'},
            ],
            'casual': [
                {'name': '即时满足', 'description': '30 秒内给玩家第一个积极反馈'},
                {'name': '平滑曲线', 'description': '难度循序渐进，挫败时提供辅助道具而非强制重来'},
                {'name': '随时放下', 'description': '每个会话 5 分钟内可以有意义的结束点'},
            ],
        }

        base = pillars_map.get(res, pillars_map.get('rpg', []))

        if profile.get('has_multiplayer'):
            base.append({'name': '社交纽带', 'description': '多人功能增强而非取代单人体验，合作和竞争都有意义'})
        if profile.get('has_monetization'):
            base.append({'name': '公平变现', 'description': '付费内容不影响核心公平性，美观和便利优先于能力提升'})

        return base

    # ─────────────────────────────────────────────────────────────
    # 功能优先级 (MoSCoW)
    # ─────────────────────────────────────────────────────────────

    def _build_feature_list(self, profile: Dict, systems: List[Dict]) -> List[Dict]:
        feature_list = []
        for sys in systems:
            moscow = {'must': 'Must Have', 'should': 'Should Have', 'could': 'Could Have', 'wont': "Won't Have"}.get(sys['priority'], 'Should Have')
            complexity_label = {'very_high': '极高', 'high': '高', 'medium': '中', 'low': '低'}.get(sys['complexity'], '中')
            feature_list.append({
                'feature':     sys['name'],
                'moscow':      moscow,
                'complexity':  complexity_label,
                'description': sys['purpose'],
                'depends_on':  sys.get('depends_on', []),
            })
        return feature_list

    # ─────────────────────────────────────────────────────────────
    # 玩家类型分析
    # ─────────────────────────────────────────────────────────────

    def _analyze_player_types(self, profile: Dict) -> Dict:
        gt  = profile['game_type']
        res = self.type_fallback.get(gt, gt)
        bt  = self.bartle_by_type.get(res, {'primary': 'achiever', 'secondary': 'explorer'})

        bartle_desc = {
            'achiever':  '成就型玩家——追求完成目标、收集奖励、达成里程碑',
            'explorer':  '探索型玩家——热爱发现新内容、测试系统边界',
            'socializer':'社交型玩家——重视与他人的互动和合作',
            'killer':    '竞争型玩家——享受战胜他人和展示实力',
        }

        design_tips = {
            'achiever':  ['清晰的成就/收集系统', '进度追踪仪表板', '稀有成就激励极限玩家'],
            'explorer':  ['隐藏内容和彩蛋', '系统交互的边界效应', '百科/图鉴收集系统'],
            'socializer':['好友系统和公会', '协作任务和组队奖励', '社交分享功能'],
            'killer':    ['排行榜和段位系统', 'PvP 模式', '展示性皮肤和称号'],
        }

        return {
            'primary_type':    bt['primary'],
            'secondary_type':  bt.get('secondary', ''),
            'primary_desc':    bartle_desc.get(bt['primary'], ''),
            'secondary_desc':  bartle_desc.get(bt.get('secondary', ''), ''),
            'design_tips':     {
                'for_primary':   design_tips.get(bt['primary'], []),
                'for_secondary': design_tips.get(bt.get('secondary', ''), []),
            },
        }

    def _analyze_fun(self, profile: Dict) -> List[Dict]:
        gt  = profile['game_type']
        res = self.type_fallback.get(gt, gt)
        funs = self.fun_by_type.get(res, ['challenge', 'discovery'])
        result = []
        for f in funs:
            fd = self.fun_types.get(f, {})
            result.append({'type': f, 'cn': fd.get('cn', f), 'desc': fd.get('desc', ''), 'primary': f == funs[0]})
        return result

    # ─────────────────────────────────────────────────────────────
    # 技术可行性标记（供架构师审查）
    # ─────────────────────────────────────────────────────────────

    def _generate_tech_flags(self, profile: Dict, systems: List[Dict]) -> List[Dict]:
        flags = []
        for sys in systems:
            if sys['complexity'] == 'very_high':
                flags.append({
                    'system':     sys['name'],
                    'complexity': '极高',
                    'flag':       '⚠️ 需架构师评估实现方案',
                    'note':       f"{sys['name']} 是高复杂度系统，建议在立项初期做技术原型验证",
                })

        if profile.get('has_multiplayer'):
            flags.append({
                'system':     '多人网络',
                'complexity': '极高',
                'flag':       '🚨 架构决策关键项',
                'note':       '网络框架选型（FishNet/Photon/NGO）必须在系统设计阶段确定，影响整体架构',
            })

        return flags

    def _get_lenses(self, profile: Dict) -> List[str]:
        gt  = profile['game_type']
        res = self.type_fallback.get(gt, gt)
        base = self.key_lenses_by_type.get(res, self.key_lenses_by_type.get('rpg', []))
        base.append('新手体验透镜：玩家在前 10 分钟内能理解并享受核心玩法吗？')
        base.append('留存透镜：玩家在第 3 天、第 7 天还有什么理由回来？')
        return base

    # ─────────────────────────────────────────────────────────────
    # 辅助
    # ─────────────────────────────────────────────────────────────

    def _normalize(self, raw: Dict) -> Dict:
        p = dict(raw)
        p.setdefault('game_name', '未命名游戏')
        p.setdefault('game_type', 'rpg')
        p.setdefault('description', '')
        p.setdefault('tone', 'neutral')
        p.setdefault('target_audience', 'core')
        p.setdefault('has_multiplayer', False)
        p.setdefault('has_narrative', False)
        p.setdefault('has_monetization', False)
        p.setdefault('has_iap', False)
        p.setdefault('features', [])
        p.setdefault('target_platforms', ['pc'])
        p.setdefault('team_size', 'small')
        return p

    def _summarize(self, profile: Dict) -> str:
        aud = {'casual': '休闲玩家', 'core': '核心玩家', 'hardcore': '硬核玩家'}.get(profile['target_audience'], '核心玩家')
        tone = {'dark': '黑暗风格', 'neutral': '中性风格', 'light': '轻松风格', 'comedic': '喜剧风格'}.get(profile['tone'], '中性风格')
        mp = '，含多人模式' if profile.get('has_multiplayer') else ''
        return f"{self._type_display(profile['game_type'])}，面向{aud}，{tone}{mp}"

    def _type_display(self, gt: str) -> str:
        m = {
            'rpg': 'RPG', 'action_rpg': '动作 RPG', 'fps': 'FPS 射击', 'tps': 'TPS 射击',
            '2d_platformer': '2D 平台跳跃', 'metroidvania': '银河恶魔城', 'roguelike': 'Roguelike',
            'strategy': '策略', 'simulation': '模拟经营', 'casual': '休闲', 'puzzle': '益智',
            'survival': '生存', 'fighting': '格斗', 'racing': '赛车', 'open_world': '开放世界',
            'action_adventure': '动作冒险', 'narrative': '叙事', 'card': '卡牌', 'top_down': '俯视角',
            'top_down_rpg': '俯视角 RPG', 'battle_royale': '大逃杀', 'twin_stick': '双摇杆射击',
        }
        return m.get(gt, gt)
