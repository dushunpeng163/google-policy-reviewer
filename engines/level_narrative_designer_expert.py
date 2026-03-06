#!/usr/bin/env python3
"""
关卡&叙事策划师 (Level & Narrative Designer Expert)

理论基础:
- 约瑟夫·坎贝尔《千面英雄》— 英雄旅程 (Hero's Journey) 结构
- 三幕式结构 (Three-Act Structure)
- Flow 理论 — Csikszentmihalyi（难度曲线设计依据）
- 任天堂"引入-展开-转折-高潮"关卡设计公式
- 空间叙事 (Environmental Storytelling)
- 编剧理论：麦基《故事》、波哲尔《写作电影》

职责:
- 生成世界观/设定简报
- 输出三幕式故事结构（含关键情节点）
- 生成完整关卡序列表（含机制、叙事、难度标注）
- 设计难度曲线（含可视化）
- 制定教学设计方案（Tutorial Flow）
- 提供核心叙事场景清单
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import math


class LevelNarrativeDesignerExpert:
    """关卡&叙事策划师 — 叙事结构与关卡体验设计专家"""

    def __init__(self):
        self.name = "关卡&叙事策划师"
        self.version = "1.0.0"
        self._build_knowledge_base()

    # ─────────────────────────────────────────────────────────────
    # 知识库
    # ─────────────────────────────────────────────────────────────

    def _build_knowledge_base(self):
        self._build_narrative_templates()
        self._build_level_archetypes()
        self._build_pacing_patterns()

    def _build_narrative_templates(self):
        """英雄旅程 + 按游戏类型的叙事模板"""
        # 英雄旅程12个阶段（坎贝尔）
        self.hero_journey = [
            {'stage': 1,  'name': '平凡世界',     'en': 'Ordinary World',     'desc': '主角日常生活，建立对照基础'},
            {'stage': 2,  'name': '冒险召唤',     'en': 'Call to Adventure',  'desc': '触发事件打破平静，提出挑战'},
            {'stage': 3,  'name': '拒绝召唤',     'en': 'Refusal of the Call','desc': '主角犹豫或拒绝（增加人物真实感）'},
            {'stage': 4,  'name': '导师登场',     'en': 'Meeting the Mentor', 'desc': '给予力量/智慧/工具的引导者'},
            {'stage': 5,  'name': '跨越门槛',     'en': 'Crossing the Threshold', 'desc': '正式进入冒险世界，无法回头'},
            {'stage': 6,  'name': '试炼与盟友',   'en': 'Tests & Allies',     'desc': '建立团队、面对考验、了解规则'},
            {'stage': 7,  'name': '深入洞穴',     'en': 'Approach Inmost Cave','desc': '逼近核心挑战，紧张感上升'},
            {'stage': 8,  'name': '生死考验',     'en': 'The Ordeal',         'desc': '最大危机，象征性死亡与重生'},
            {'stage': 9,  'name': '获得奖励',     'en': 'The Reward',         'desc': '克服考验后获得宝物/知识/成长'},
            {'stage': 10, 'name': '归途之路',     'en': 'The Road Back',      'desc': '携带奖励返回，面临新威胁'},
            {'stage': 11, 'name': '最终复活',     'en': 'The Resurrection',   'desc': '最终决战，彻底转化与胜利'},
            {'stage': 12, 'name': '归返精灵',     'en': 'Return with Elixir', 'desc': '回到平凡世界，带来改变'},
        ]

        # 三幕式关键情节点
        self.three_act_beats = {
            'act1': {
                'proportion': '25%',
                'beats': [
                    {'name': '开场钩子',    'position': '第1-2%',  'purpose': '立刻抓住玩家/观众注意力'},
                    {'name': '世界建立',    'position': '第2-15%', 'purpose': '建立规则、角色、世界观'},
                    {'name': '触发事件',    'position': '第15-20%','purpose': '打破现状的关键事件，故事真正开始'},
                    {'name': '进入第二幕',  'position': '第25%',   'purpose': '主角做出关键决定，进入冲突世界'},
                ],
            },
            'act2': {
                'proportion': '50%',
                'beats': [
                    {'name': '新世界适应',  'position': '第25-35%','purpose': '学习新规则，建立关系'},
                    {'name': '小胜与进步',  'position': '第35-45%','purpose': '一系列挑战和小胜，推进目标'},
                    {'name': '中间点',      'position': '第50%',   'purpose': '假胜利或假失败，态度从被动转主动'},
                    {'name': '麻烦升级',    'position': '第50-65%','purpose': '对手反击，事情变得更糟'},
                    {'name': '一切皆输',    'position': '第70-75%','purpose': '最低点，失去一切（盟友/工具/希望）'},
                ],
            },
            'act3': {
                'proportion': '25%',
                'beats': [
                    {'name': '内省重燃',    'position': '第75-80%','purpose': '重新发现内在动力，新的解决方案'},
                    {'name': '最终决战',    'position': '第80-95%','purpose': '面对最终Boss/冲突，全力以赴'},
                    {'name': '结局释放',    'position': '第95-100%','purpose': '故事收尾，新世界建立'},
                ],
            },
        }

        # 按游戏类型的叙事框架
        self.narrative_by_type = {
            'rpg': {
                'structure': '英雄旅程 + 三幕式',
                'protagonist_arc': '平凡青年/平民 → 命运选中者 → 改变世界的英雄',
                'key_themes': ['命运与选择', '成长与牺牲', '善恶对立', '友谊与羁绊'],
                'world_pillars': ['清晰的势力划分（王国/组织/种族）', '历史背景（战争/神话/遗迹）', '魔法/科技体系的规则'],
                'narrative_devices': ['导师（早期死去以激励主角）', '信使（推进情节的NPC）', '守门人（测试主角资格）'],
            },
            'action_rpg': {
                'structure': '目标导向型叙事',
                'protagonist_arc': '孤独猎手/复仇者 → 逐渐揭开真相 → 超越原始目标的成长',
                'key_themes': ['复仇与救赎', '力量的代价', '孤独与同伴'],
                'world_pillars': ['末世/衰落的世界', '不同区域有独特氛围', '怪物有世界观意义'],
                'narrative_devices': ['环境叙事（通过场景和道具讲故事）', 'Boss的悲剧背景', '碎片化叙事（笔记/对话/环境）'],
            },
            'fps': {
                'structure': '线性战役 + 任务目标',
                'protagonist_arc': '士兵/特工执行任务 → 发现背叛/阴谋 → 揭露真相、消灭威胁',
                'key_themes': ['战争与牺牲', '忠诚与背叛', '代价与荣耀'],
                'world_pillars': ['清晰的敌我阵营', '写实或科幻的战场环境', '队友有各自性格'],
                'narrative_devices': ['任务简报建立目标', '无线电对话推进情节', '战场环境叙事'],
            },
            'open_world': {
                'structure': '多线并行叙事',
                'protagonist_arc': '外来者/失忆者/野心家 → 深入世界理解各方势力 → 做出影响世界的选择',
                'key_themes': ['自由与归属', '道德灰色地带', '世界的代价'],
                'world_pillars': ['有历史深度的地图', '各区域有独特文化和冲突', '玩家选择影响世界状态'],
                'narrative_devices': ['分支叙事（选择影响结局）', '动态世界事件', '可选的深度支线'],
            },
            'roguelike': {
                'structure': '元叙事 + 跑局叙事',
                'protagonist_arc': '不断失败的挑战者 → 每次死亡揭示更多世界秘密 → 最终突破诅咒/循环',
                'key_themes': ['宿命与反抗', '重复中的变化', '记忆与遗忘'],
                'world_pillars': ['每次游玩有新的叙事片段', 'NPC随游玩次数解锁新对话', '死亡有叙事意义'],
                'narrative_devices': ['逐渐解锁的元故事', '随机事件中的叙事碎片', '死亡台词和回响'],
            },
            'casual': {
                'structure': '极简框架叙事',
                'protagonist_arc': '角色有简单可爱的目标，通过关卡达成',
                'key_themes': ['轻松愉快', '友情', '小小的胜利'],
                'world_pillars': ['鲜明的视觉风格', '简单易懂的世界规则', '可爱的角色'],
                'narrative_devices': ['过场动画讲故事（不依赖文字）', '角色表情传达情感', '关卡主题有变化'],
            },
        }

    def _build_level_archetypes(self):
        """关卡类型模板"""
        self.level_types = {
            'tutorial':       {'name': '教学关', '难度': 1, '目标': '教授核心机制，成功率100%', '时长': '3-5分钟'},
            'exploration':    {'name': '探索关', '难度': 2, '目标': '发现世界和奖励', '时长': '10-20分钟'},
            'combat':         {'name': '战斗关', '难度': 4, '目标': '测试战斗技能', '时长': '5-15分钟'},
            'stealth':        {'name': '潜行关', '难度': 4, '目标': '另一种玩法风味', '时长': '10-20分钟'},
            'puzzle':         {'name': '谜题关', '难度': 3, '目标': '测试解谜思维', '时长': '5-15分钟'},
            'boss':           {'name': 'Boss 关', '难度': 7, '目标': '高潮对决，检验成长', '时长': '10-20分钟'},
            'narrative':      {'name': '叙事关', '难度': 1, '目标': '剧情推进，情感铺垫', '时长': '5-10分钟'},
            'reward':         {'name': '奖励关', '难度': 2, '目标': '情绪爆发点，大量奖励', '时长': '3-8分钟'},
            'challenge':      {'name': '挑战关', '难度': 8, '目标': '硬核玩家的可选挑战', '时长': '10-30分钟'},
            'open':           {'name': '开放区', '难度': 3, '目标': '自由探索和支线内容', '时长': '30-120分钟'},
        }

    def _build_pacing_patterns(self):
        """节奏模式"""
        self.pacing_by_type = {
            'rpg':        ['tutorial', 'exploration', 'combat', 'narrative', 'combat', 'reward', 'boss', 'exploration', 'combat', 'combat', 'narrative', 'boss'],
            'action_rpg': ['tutorial', 'combat', 'combat', 'exploration', 'boss', 'reward', 'combat', 'combat', 'challenge', 'boss', 'combat', 'boss'],
            'fps':        ['tutorial', 'combat', 'stealth', 'combat', 'narrative', 'boss', 'combat', 'combat', 'challenge', 'boss'],
            'roguelike':  ['tutorial', 'exploration', 'combat', 'combat', 'reward', 'boss', 'combat', 'combat', 'challenge', 'boss'],
            'casual':     ['tutorial', 'reward', 'combat', 'puzzle', 'combat', 'reward', 'boss', 'puzzle', 'combat', 'reward', 'boss'],
            'open_world': ['tutorial', 'open', 'narrative', 'combat', 'boss', 'open', 'exploration', 'narrative', 'boss'],
        }

        # 难度节奏序列（0-10分）
        self.difficulty_sequence_by_type = {
            'rpg':        [1, 2, 3, 2, 4, 3, 5, 4, 6, 5, 6, 7, 5, 7, 8, 6, 9, 8, 10],
            'action_rpg': [1, 3, 4, 3, 5, 4, 6, 5, 7, 6, 8, 7, 9, 8, 10],
            'fps':        [2, 3, 4, 3, 5, 4, 6, 5, 7, 6, 8, 8, 10],
            'roguelike':  [2, 3, 4, 5, 6, 7, 7, 8, 9, 10],
            'casual':     [1, 1, 2, 2, 3, 2, 4, 3, 5, 4, 5, 5, 6, 5, 7, 6, 8, 7, 8, 8, 9, 8, 10],
        }

    # ─────────────────────────────────────────────────────────────
    # 主分析入口
    # ─────────────────────────────────────────────────────────────

    def analyze(self, game_profile: Dict) -> Dict:
        """
        game_profile:
        {
            game_name:         str,
            game_type:         str,
            description:       str,
            world_setting:     str,  # fantasy/scifi/modern/historical/post_apocalyptic/fairy_tale
            tone:              str,  # dark/neutral/light/comedic
            content_hours:     int,  # 预计总游玩时长（小时）
            num_levels:        int,  # 关卡/区域数量
            has_main_story:    bool,
            has_side_quests:   bool,
            tutorial_style:    str,  # explicit/implicit/none
            player_choice:     bool, # 玩家选择影响剧情
            has_multiplayer:   bool,
        }
        """
        p = self._normalize(game_profile)

        world_brief    = self._build_world_brief(p)
        story          = self._build_story(p)
        level_sequence = self._build_level_sequence(p)
        difficulty     = self._build_difficulty_pacing(p, level_sequence)
        tutorial       = self._build_tutorial(p)
        narrative_moments = self._build_narrative_moments(p, story)

        return {
            'status': 'success',
            'generated_at': datetime.now().isoformat(),
            'designer': self.name,
            'game_info': {
                'name': p['game_name'],
                'type': p['game_type'],
                'setting': p['world_setting'],
                'tone': p['tone'],
                'content_hours': p['content_hours'],
            },
            'world_brief':        world_brief,
            'story_structure':    story,
            'level_sequence':     level_sequence,
            'difficulty_pacing':  difficulty,
            'tutorial_design':    tutorial,
            'narrative_moments':  narrative_moments,
            'design_principles':  self._get_design_principles(p),
        }

    # ─────────────────────────────────────────────────────────────
    # 世界简报
    # ─────────────────────────────────────────────────────────────

    def _build_world_brief(self, p: Dict) -> Dict:
        setting = p['world_setting']
        tone    = p['tone']
        gt      = p['game_type']

        setting_themes = {
            'fantasy': {
                'atmosphere': '魔法与剑的奇幻世界，有古老传说、强大魔法和英雄传承',
                'factions': ['人类王国（科技与政治）', '精灵/仙族（古老与自然）', '黑暗势力（腐败与毁灭）', '中立商会（利益优先）'],
                'world_rules': ['魔法有代价（消耗生命/精神力）', '古神器是权力象征', '不同种族各有禁忌'],
                'visual_cues': '光影反差鲜明，人类城市暖色，黑暗势力领地冷色、腐化贴图',
            },
            'scifi': {
                'atmosphere': '星际文明、AI与人类共存的未来，科技高度发达但道德隐患丛生',
                'factions': ['星际联邦（秩序）', '自由殖民地（独立）', '企业集团（利益）', 'AI觉醒势力（未知）'],
                'world_rules': ['FTL跳跃需消耗稀有资源', 'AI有行为限制协议', '各星球有独立生态规则'],
                'visual_cues': '霓虹+金属+全息投影，人口密集区vs荒芜星球的视觉落差',
            },
            'modern': {
                'atmosphere': '现实世界的隐秘层——组织、秘密和阴谋在日常表面下运作',
                'factions': ['政府机构（权力）', '黑市组织（资源）', '平民社区（人情）', '神秘团体（真相）'],
                'world_rules': ['超能力/秘密必须隐藏于公众', '金钱和信息是真正的权力', '手机/网络是双刃剑'],
                'visual_cues': '现实地标+超自然元素的反差，灰暗日常与鲜明危险的对比',
            },
            'historical': {
                'atmosphere': '历史特定时期的真实感与戏剧化，史实背景与虚构冲突交织',
                'factions': ['历史真实势力（参考真实战争/朝代）', '隐秘组织（历史背后的推手）', '民间力量（平民视角）'],
                'world_rules': ['遵循历史大事件节点', '生产力/科技受时代限制', '身份阶层是主要约束'],
                'visual_cues': '历史考据的服装/建筑，配以戏剧化的战场和政治场景',
            },
            'post_apocalyptic': {
                'atmosphere': '文明崩溃后的废土世界，幸存者在废墟中重建秩序',
                'factions': ['幸存者聚居地（生存优先）', '强盗团伙（掠夺）', '旧时代遗留军事组织', '异变生物群落'],
                'world_rules': ['资源极度稀缺，一切皆可交换', '武力是基本话语权', '旧世界科技是宝贵遗产'],
                'visual_cues': '生锈+植物侵蚀+旧世界建筑，混合着幸存者拼凑的临时设施',
            },
            'fairy_tale': {
                'atmosphere': '童话寓言世界，表象简单纯真，内核可以是深刻或黑暗的',
                'factions': ['王国皇室', '森林精灵/动物王国', '邪恶女巫/巫师', '普通村民'],
                'world_rules': ['魔法有明确的规则和代价', '诅咒可以被打破但需满足条件', '善恶有明确标志'],
                'visual_cues': '高饱和度色彩，夸张比例，魔法特效浪漫化',
            },
        }

        tone_modifiers = {
            'dark':    {'color': '灰暗、血腥、沉重', 'emotion': '恐惧、绝望中的希望、道德复杂', 'note': '确保黑暗服务于故事意义而非纯粹猎奇'},
            'neutral': {'color': '平衡的明暗对比', 'emotion': '冒险、成长、挑战', 'note': '经典叙事基调，受众最广'},
            'light':   {'color': '明亮温暖', 'emotion': '希望、友谊、乐观克服困难', 'note': '适合全年龄受众'},
            'comedic': {'color': '鲜艳夸张', 'emotion': '轻松愉快、讽刺幽默、意外笑点', 'note': '保持幽默一致性，避免突然变沉重'},
        }

        st    = setting_themes.get(setting, setting_themes['fantasy'])
        tmod  = tone_modifiers.get(tone, tone_modifiers['neutral'])

        return {
            'setting':     setting,
            'tone':        tone,
            'atmosphere':  st['atmosphere'],
            'tone_style': {
                'visual_tone': tmod['color'],
                'emotional_range': tmod['emotion'],
                'design_note': tmod['note'],
            },
            'core_factions': st['factions'],
            'world_rules':   st['world_rules'],
            'visual_language': st['visual_cues'],
            'pillars': [
                '一致性：世界的规则在所有地方一致适用',
                '可读性：玩家第一眼就能判断友好/危险区域',
                '历史感：场景传达"在玩家到来之前就有历史"的感觉',
            ],
        }

    # ─────────────────────────────────────────────────────────────
    # 故事结构
    # ─────────────────────────────────────────────────────────────

    def _build_story(self, p: Dict) -> Dict:
        gt      = p['game_type']
        setting = p['world_setting']
        tone    = p['tone']
        hours   = p['content_hours']
        choice  = p.get('player_choice', False)

        # 获取叙事框架
        res = self._type_fallback(gt)
        nf  = self.narrative_by_type.get(res, self.narrative_by_type['rpg'])

        setting_context = {
            'fantasy':          '一个魔法渐渐消失的王国',
            'scifi':            '一个AI开始质疑自身存在的星际联邦',
            'modern':           '一座隐藏着古老秘密的现代都市',
            'historical':       '一个历史转折点上的帝国',
            'post_apocalyptic': '文明崩溃后第三代幸存者的定居地',
            'fairy_tale':       '诅咒笼罩的魔法王国',
        }.get(setting, '充满未知的世界')

        conflict_by_tone = {
            'dark':    '一场以大多数人的牺牲为代价的生死抉择',
            'neutral': '阻止一个试图颠覆现有秩序的强大敌人',
            'light':   '用友谊和勇气打败黑暗势力，让光明重归',
            'comedic': '一场始料未及的荒诞冒险，最终却拯救了世界',
        }.get(tone, '克服强大的外部威胁')

        act1_hours  = round(hours * 0.25, 1)
        act2_hours  = round(hours * 0.50, 1)
        act3_hours  = round(hours * 0.25, 1)

        story = {
            'narrative_framework': nf['structure'],
            'protagonist_arc':     nf['protagonist_arc'],
            'key_themes':          nf['key_themes'],
            'world_context':       setting_context,
            'central_conflict':    conflict_by_tone,
            'three_act': {
                'act1': {
                    'title':    '建立 — 平凡世界的裂缝',
                    'duration': f'约{act1_hours}小时',
                    'content':  f'玩家扮演{nf["protagonist_arc"].split("→")[0].strip()}，生活在{setting_context}。一次偶然事件（可以是战斗/发现/失去）打破平静，揭示更大的威胁或秘密，迫使主角踏上旅途。',
                    'key_beat': '触发事件：无法回头的一个选择或失去',
                    'gameplay': '教程关卡、世界观建立、第一批机制引入',
                    'emotion':  '好奇 → 期待 → 决心',
                    'beats': self.three_act_beats['act1']['beats'],
                },
                'act2': {
                    'title':    '对抗 — 深入险境',
                    'duration': f'约{act2_hours}小时',
                    'content':  f'主角深入冒险世界，结识盟友，面对一系列挑战。中段出现假胜利（玩家认为快要成功），随后急转直下，主角跌至最低点（失去盟友/工具/信念）。最终在绝境中找到内在突破口。',
                    'key_beat': '最低点：一切似乎都失去，但内心力量被激活',
                    'gameplay': '主要区域探索、核心玩法展开、重要Boss挑战',
                    'emotion':  '挑战 → 小胜 → 危机 → 绝望 → 重燃',
                    'beats': self.three_act_beats['act2']['beats'],
                },
                'act3': {
                    'title':    '解决 — 最终决战',
                    'duration': f'约{act3_hours}小时',
                    'content':  f'玩家重新振作，整合所有成长，直面最终Boss。最终决战是整个故事的情感与玩法高潮，主角在胜利中完成内在弧线的转变，{conflict_by_tone}，世界迎来新的可能。',
                    'key_beat': '最终决战：所有机制、叙事、情感汇聚的顶点',
                    'gameplay': '最终区域、终Boss战、叙事收尾',
                    'emotion':  '紧张 → 绝地反击 → 胜利 → 释然',
                    'beats': self.three_act_beats['act3']['beats'],
                },
            },
            'player_choice_note': '⭐ 玩家选择将影响部分对话和次要结局，核心主线保持一致' if choice else '主线叙事固定，玩家选择体现在支线和关系系统中',
            'narrative_devices':  nf['narrative_devices'],
            'world_pillars':      nf['world_pillars'],
        }

        if p.get('has_side_quests'):
            story['side_quest_philosophy'] = [
                '支线任务须有独立的小故事弧，不只是"收集X个/杀Y个"',
                '每条支线揭示世界的不同侧面（某势力历史、某NPC背景）',
                '最好的支线让玩家在完成后重新审视主线的某个角度',
                '支线难度低于同期主线，提供放松和世界探索的机会',
            ]

        return story

    # ─────────────────────────────────────────────────────────────
    # 关卡序列
    # ─────────────────────────────────────────────────────────────

    def _build_level_sequence(self, p: Dict) -> List[Dict]:
        gt         = p['game_type']
        num_levels = p['num_levels']
        hours      = p['content_hours']
        res        = self._type_fallback(gt)

        # 获取节奏模板并扩展/压缩到目标关卡数
        base_pattern = self.pacing_by_type.get(res, self.pacing_by_type['rpg'])
        difficulty_seq = self.difficulty_sequence_by_type.get(res, self.difficulty_sequence_by_type['rpg'])

        # 将模板缩放到 num_levels
        pattern   = self._scale_list(base_pattern, num_levels)
        diff_vals = self._scale_list(difficulty_seq, num_levels)

        # 故事位置标签
        act_labels = self._distribute_acts(num_levels)

        # 区域/章节归属
        zones = self._distribute_zones(num_levels, p)

        avg_level_min = round(hours * 60 / num_levels, 0)

        # 机制引入序列
        mechanic_intro = self._mechanic_intro_sequence(gt, num_levels)

        sequence = []
        for i, (lt, dv, act, zone, mech) in enumerate(
                zip(pattern, diff_vals, act_labels, zones, mechanic_intro), 1):
            ltype = self.level_types.get(lt, self.level_types['combat'])
            diff_label = self._diff_label(dv)
            sequence.append({
                'no':          i,
                'type':        ltype['name'],
                'type_key':    lt,
                'act':         act,
                'zone':        zone,
                'difficulty':  dv,
                'diff_label':  diff_label,
                'mechanic':    mech,
                'est_minutes': int(avg_level_min),
                'design_goal': ltype['目标'],
                'notes':       self._level_notes(lt, i, num_levels, dv),
            })

        return sequence

    def _level_notes(self, level_type: str, idx: int, total: int, diff: int) -> str:
        is_first = idx == 1
        is_last  = idx == total
        progress = idx / total

        if is_first:
            return '第一关：零失败体验，确保100%玩家可以完成并产生兴趣'
        if is_last:
            return '最终关：汇聚所有已学机制，叙事和玩法双重高潮'
        if level_type == 'boss':
            return f'Boss战：新Boss引入1-2个新机制，需要玩家运用前几关所学'
        if level_type == 'reward':
            return '奖励关：难度降低，掉落大幅提升，制造情绪爆发点（玩家会主动推荐游戏时提到的时刻）'
        if level_type == 'tutorial':
            return '教学关：展示机制→让玩家尝试→场景形成正向反馈，不使用弹窗教程'
        if progress > 0.8 and diff >= 8:
            return '后期高难度区：仅高阶玩家有意愿挑战，确保有足够奖励驱动'
        return ''

    def _mechanic_intro_sequence(self, gt: str, n: int) -> List[str]:
        mechanics_by_type = {
            'rpg':        ['移动与交互', '基础战斗', '背包系统', '对话与任务', '地图导航', '技能系统', '装备系统', '强化系统', 'Boss机制', '高级技能', '多敌AI', '终局机制'],
            'action_rpg': ['移动与闪避', '轻重攻击', '连击系统', '技能使用', '装备对比', '属性克制', '精英怪机制', 'Boss阶段', '构筑系统', '高级连携', '精英构筑', '终局挑战'],
            'fps':        ['移动与射击', '武器切换', '掩体系统', '投掷物使用', '特殊武器', '车辆操作', '侦察机制', 'Boss弱点', '策略配合', '高难战术', '最终关联机制', '决战场景'],
            'roguelike':  ['基础移动战斗', '道具拾取', '房间选择', 'Boss机制', '元进度解锁', '构筑协同', '精英房挑战', '隐藏房间', '特殊词条', '极限构筑', 'Boss二阶段', '最终Boss'],
            'casual':     ['核心操作', '障碍回避', '道具使用', '连击系统', '时间限制', '关卡特殊规则', 'Boss1介绍', '新障碍类型', '速度加快', '组合挑战', 'Boss2', '最终挑战'],
        }
        gt_res = self._type_fallback(gt)
        base   = mechanics_by_type.get(gt_res, mechanics_by_type['rpg'])
        return self._scale_list(base, n)

    # ─────────────────────────────────────────────────────────────
    # 难度曲线
    # ─────────────────────────────────────────────────────────────

    def _build_difficulty_pacing(self, p: Dict, level_sequence: List[Dict]) -> Dict:
        diffs  = [lv['difficulty'] for lv in level_sequence]
        n      = len(diffs)

        # 文字版难度曲线可视化
        max_d = max(diffs) if diffs else 10
        rows  = []
        bar_chars = ['▁', '▂', '▃', '▄', '▅', '▆', '▇', '█']
        bar_line  = ''
        for d in diffs:
            idx = min(7, int(d / max_d * 8))
            bar_line += bar_chars[idx]
        rows.append(f'难度 ↑  {bar_line}  → 关卡')

        # 节奏分析
        boss_positions = [i+1 for i, lv in enumerate(level_sequence) if lv['type_key'] == 'boss']
        reward_positions = [i+1 for i, lv in enumerate(level_sequence) if lv['type_key'] == 'reward']

        avg_d = round(sum(diffs)/n, 1) if n else 0

        return {
            'visualization': bar_line,
            'description': (
                f'全程共{n}关，平均难度{avg_d}/10。'
                f'Boss关卡位于第{boss_positions}关，'
                f'奖励关卡位于第{reward_positions}关。'
            ),
            'pacing_principles': [
                '每5-7关设置一个奖励关（难度突降），制造情绪释放爆发点',
                'Boss战前1关难度应略低（"呼吸空间"），让玩家在挑战Boss前放松',
                '整体难度呈上升趋势，但避免连续5关以上的高难度',
                '教学机制：遇到新机制的前两次接触应在低风险环境，第三次才在高压场景测试',
            ],
            'flow_theory_note': (
                '心流区间：挑战难度略高于玩家当前技能约10-15%时产生最佳体验。'
                '难度过高→焦虑；难度过低→无聊。'
                '通过渐进式机制引入和即时反馈维持玩家在心流区间。'
            ),
            'boss_positions': boss_positions,
            'reward_positions': reward_positions,
        }

    # ─────────────────────────────────────────────────────────────
    # 教学设计
    # ─────────────────────────────────────────────────────────────

    def _build_tutorial(self, p: Dict) -> Dict:
        style = p['tutorial_style']
        gt    = p['game_type']

        if style == 'none':
            return {
                'style': '无引导',
                'philosophy': '玩家通过探索和失败自学，适合Roguelike等高难度类型',
                'risk': '新手流失率高，须通过关卡设计隐性引导',
                'steps': [],
            }

        steps_by_type = {
            'rpg': [
                {'step': 1, 'teaches': '移动与镜头控制', 'method': '空旷安全区域，无敌人，仅环境提示', 'duration': '1分钟', 'principle': '让玩家先感受到自由'},
                {'step': 2, 'teaches': '基础攻击', 'method': '1个稻草人/弱小怪物，必然成功', 'duration': '1分钟', 'principle': '首次战斗必须胜利，建立信心'},
                {'step': 3, 'teaches': '技能使用', 'method': '地面发光提示，触发后播放技能', 'duration': '1分钟', 'principle': '视觉引导优于文字说明'},
                {'step': 4, 'teaches': '背包系统', 'method': '捡起显眼掉落物品，自动打开背包界面', 'duration': '1分钟', 'principle': '操作行为触发教学而非反过来'},
                {'step': 5, 'teaches': '任务接取与追踪', 'method': '遇到第一个NPC，对话后自动接任务', 'duration': '2分钟', 'principle': '教学任务的奖励要诱人'},
                {'step': 6, 'teaches': '地图与传送', 'method': '到达区域边界后弹出地图', 'duration': '1分钟', 'principle': '在需要时才教学（JIT）'},
            ],
            'fps': [
                {'step': 1, 'teaches': '移动与视角', 'method': '室内训练场，标靶练习', 'duration': '2分钟', 'principle': '熟悉控制器前不引入敌人'},
                {'step': 2, 'teaches': '射击与命中反馈', 'method': '静止标靶→移动标靶', 'duration': '2分钟', 'principle': '夸大命中反馈（音效+视觉+震动）'},
                {'step': 3, 'teaches': '掩体系统', 'method': '少量弱敌，掩体有发光提示', 'duration': '2分钟', 'principle': '错误行为立刻有可见后果（受到伤害）'},
                {'step': 4, 'teaches': '武器切换', 'method': '特定场景设计只有副武器才有效', 'duration': '1分钟', 'principle': '不是"教你换武器"，而是"让你需要换武器"'},
                {'step': 5, 'teaches': '投掷物使用', 'method': '门后有敌人，旁边有发光手雷', 'duration': '1分钟', 'principle': '环境暗示而非弹窗提示'},
            ],
            'roguelike': [
                {'step': 1, 'teaches': '移动与攻击', 'method': '第一个房间只有1个弱敌', 'duration': '30秒', 'principle': '极简开始，立刻进入游戏状态'},
                {'step': 2, 'teaches': '道具拾取效果', 'method': '强力道具放在明显位置', 'duration': '30秒', 'principle': '让玩家发现而非被告知'},
                {'step': 3, 'teaches': '房间选择', 'method': '路口展示两个房间标记（战斗/商店）', 'duration': '30秒', 'principle': '信息量渐进释放'},
                {'step': 4, 'teaches': 'Boss战', 'method': '第一个Boss明显降低难度，但保留完整机制', 'duration': '3分钟', 'principle': '失败也是教学的一部分'},
            ],
        }

        gt_res = self._type_fallback(gt)
        steps  = steps_by_type.get(gt_res, steps_by_type['rpg'])

        return {
            'style': '显式教学' if style == 'explicit' else '隐式教学',
            'philosophy': (
                '显式教学：简短UI提示+强制练习，适合复杂机制游戏' if style == 'explicit'
                else '隐式教学：关卡设计自然引导玩家发现机制，无弹窗提示——适合沉浸感高的游戏'
            ),
            'core_principles': [
                '展示 > 告知：让玩家看到效果，而不是读文字描述',
                'JIT（即时教学）：在玩家需要技能的瞬间教，而非游戏开始时一次性教完',
                '安全练习区：新机制首次出现时周围环境必须是低风险的',
                '正向强化：首次成功使用新技能给予额外奖励',
                '失败宽容：教学阶段的失败不应有严厉惩罚（无死亡/自动回血）',
            ],
            'steps': steps,
            'avoid': [
                '避免游戏开始时的长篇文字说明（玩家会跳过）',
                '避免一次教超过2个新机制',
                '避免在玩家尝试新技能前就有惩罚性后果',
                '避免假设玩家会记住很久前看到的提示',
            ],
        }

    # ─────────────────────────────────────────────────────────────
    # 关键叙事场景
    # ─────────────────────────────────────────────────────────────

    def _build_narrative_moments(self, p: Dict, story: Dict) -> List[Dict]:
        gt      = p['game_type']
        setting = p['world_setting']
        tone    = p['tone']
        hours   = p['content_hours']

        moments = [
            {
                'order':     1,
                'name':      '开场钩子',
                'trigger':   '游戏启动后第1-3分钟',
                'purpose':   '立刻建立情感连接，让玩家想知道"接下来会发生什么"',
                'craft_tip': '从动作中开始（不要从角色睡觉/日常开始）；引入悬念比完整背景更重要',
                'avoid':     '避免以长篇文字或静态对话开场——动态场景开场',
                'emotion':   '好奇 / 惊喜',
            },
            {
                'order':     2,
                'name':      '触发事件',
                'trigger':   f'约{round(hours*0.15,1)}小时游玩时',
                'purpose':   '打破主角的日常，赋予旅程意义——主角无法回到原来的生活',
                'craft_tip': '触发事件要有个人代价（失去某人/某物/身份）',
                'avoid':     '避免纯粹的外部压迫——主角要有内心动机的成分',
                'emotion':   '震惊 / 决心 / 悲伤',
            },
            {
                'order':     3,
                'name':      '第一个盟友/导师',
                'trigger':   f'约{round(hours*0.20,1)}小时游玩时',
                'purpose':   '提供力量/工具/情感支持，同时揭示世界更多信息',
                'craft_tip': '导师不能太完美——有弱点和秘密才有戏剧空间；经典结构：导师在恰当时刻死去激励主角',
                'avoid':     '避免导师角色只是"教程NPC"，要赋予完整的角色弧',
                'emotion':   '信任 / 希望',
            },
            {
                'order':     4,
                'name':      '中间点：假胜利或假失败',
                'trigger':   f'约{round(hours*0.50,1)}小时游玩时（游戏中点）',
                'purpose':   '让玩家认为目标近在咫尺，随后意外反转推高戏剧张力',
                'craft_tip': '假胜利：任务看似完成→敌人比想象更强大/更多；假失败：一切似乎结束→意外转机',
                'avoid':     '避免中点过于平淡——这是Act 2最重要的情节点',
                'emotion':   '短暂喜悦 → 突然惊变',
            },
            {
                'order':     5,
                'name':      '最低点',
                'trigger':   f'约{round(hours*0.70,1)}小时游玩时',
                'purpose':   '主角失去最重要的东西（盟友/工具/信念），但内在力量被激活',
                'craft_tip': '最低点越深，最终胜利越有价值；失去要有情感重量而非随意发生',
                'avoid':     '避免最低点后立刻反弹——给玩家一点时间感受低落',
                'emotion':   '失望 / 绝望 → 内在觉醒',
            },
            {
                'order':     6,
                'name':      '最终决战前的宁静',
                'trigger':   f'约{round(hours*0.85,1)}小时游玩时',
                'purpose':   '在最终高潮前的情感积累——主角整合成长，准备最终挑战',
                'craft_tip': '给玩家/主角一个短暂的"喘息"：回忆、团聚、做出最终选择',
                'avoid':     '避免从最低点直接跳到最终决战——缺少这个节拍会使胜利感觉空洞',
                'emotion':   '平静 / 决心 / 怀念',
            },
            {
                'order':     7,
                'name':      '最终决战与结局',
                'trigger':   f'约{round(hours*0.90,1)}小时游玩时',
                'purpose':   '所有主题、机制、情感的汇聚高潮，主角内在弧线完成',
                'craft_tip': '最终Boss战要在玩法和叙事上同时具有意义；结局场景要给主角弧线一个明确的"画上句号"时刻',
                'avoid':     '避免结局草草了事——玩家花了数十小时到达这里，值得一个有分量的结局',
                'emotion':   '紧张 → 全力以赴 → 胜利释放 → 满足感',
            },
        ]

        return moments

    # ─────────────────────────────────────────────────────────────
    # 设计原则
    # ─────────────────────────────────────────────────────────────

    def _get_design_principles(self, p: Dict) -> List[Dict]:
        return [
            {
                'source': '任天堂关卡设计公式',
                'principle': '引入 → 展开 → 转折 → 高潮',
                'application': '每个新机制经历四个阶段：安全引入、基础应用、挑战性变体、终极考验',
            },
            {
                'source': 'Flow 理论 (Csikszentmihalyi)',
                'principle': '挑战与技能的动态平衡',
                'application': '持续监控玩家失败率：失败率>60%降低难度，失败率<20%增加挑战',
            },
            {
                'source': '空间叙事 (Environmental Storytelling)',
                'principle': '让场景自己讲故事',
                'application': '每个区域至少有3-5处环境细节暗示这里的历史；玩家无需读文字也能感受到世界的厚度',
            },
            {
                'source': '教学设计原则',
                'principle': '"失败是老师，但惩罚要轻"',
                'application': '教学阶段允许失败但无严厉惩罚；失败后提供提示但不剥夺玩家的发现感',
            },
            {
                'source': 'Jesse Schell《游戏设计艺术》',
                'principle': '惊喜的节奏感',
                'application': '在玩家认为已经理解规则时，引入意外的机制或叙事转折——每15-20分钟设置一个"哇"时刻',
            },
        ]

    # ─────────────────────────────────────────────────────────────
    # 辅助方法
    # ─────────────────────────────────────────────────────────────

    def _normalize(self, raw: Dict) -> Dict:
        p = dict(raw)
        p.setdefault('game_name', '未命名游戏')
        p.setdefault('game_type', 'rpg')
        p.setdefault('description', '')
        p.setdefault('world_setting', 'fantasy')
        p.setdefault('tone', 'neutral')
        p.setdefault('content_hours', 20)
        p.setdefault('num_levels', 20)
        p.setdefault('has_main_story', True)
        p.setdefault('has_side_quests', True)
        p.setdefault('tutorial_style', 'implicit')
        p.setdefault('player_choice', False)
        p.setdefault('has_multiplayer', False)
        p['content_hours'] = max(2, min(200, int(p['content_hours'])))
        p['num_levels']    = max(5, min(200, int(p['num_levels'])))
        return p

    def _type_fallback(self, gt: str) -> str:
        mapping = {
            'action_rpg': 'rpg', 'action_adventure': 'rpg',
            'open_world': 'rpg', 'top_down_rpg': 'rpg',
            'metroidvania': 'roguelike', 'top_down': 'roguelike',
            'survival': 'roguelike', 'tps': 'fps',
            'battle_royale': 'fps', 'fighting': 'casual',
            'racing': 'casual', 'puzzle': 'casual',
            'simulation': 'casual', 'card': 'casual',
            '2d_platformer': 'casual', 'narrative': 'rpg',
        }
        return mapping.get(gt, gt if gt in self.narrative_by_type else 'rpg')

    def _scale_list(self, src: list, target_len: int) -> list:
        """将任意长度的列表缩放到 target_len"""
        if not src:
            return ['combat'] * target_len
        n   = len(src)
        if n == target_len:
            return src
        return [src[int(i * n / target_len)] for i in range(target_len)]

    def _distribute_acts(self, n: int) -> List[str]:
        acts = []
        for i in range(n):
            pct = i / n
            if pct < 0.25:
                acts.append('第一幕')
            elif pct < 0.75:
                acts.append('第二幕')
            else:
                acts.append('第三幕')
        return acts

    def _distribute_zones(self, n: int, p: Dict) -> List[str]:
        gt = p['game_type']
        zone_names_by_type = {
            'rpg':        ['新手村-序章', '荒野区域', '第一城镇', '危险森林', '中部大陆', '废墟遗迹', '深渊边缘', '敌人要塞', '最终圣地'],
            'action_rpg': ['入口区域', '浅层区域', '暗处境地', '精英区域', '深渊核心', '禁忌领域', '神圣之地', '最终领域'],
            'fps':        ['训练营', '城市外围', '工业区', '地下设施', '军事基地', '总部核心', '最终据点'],
            'casual':     ['第一章', '第二章', '第三章', '第四章', '第五章', '最终关'],
            'roguelike':  ['第1层', '第2层', '第3层', '第4层', '第5层', '最终层'],
        }
        gt_res = self._type_fallback(p['game_type'])
        names  = zone_names_by_type.get(gt_res, zone_names_by_type['rpg'])
        return self._scale_list(names, n)

    def _diff_label(self, d: int) -> str:
        if d <= 2:  return '简单'
        if d <= 4:  return '普通'
        if d <= 6:  return '挑战'
        if d <= 8:  return '困难'
        return '极难'
