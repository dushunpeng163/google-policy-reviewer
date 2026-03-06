#!/usr/bin/env python3
"""
数值策划师 (Numerical Designer Expert)

职责:
- 输出完整可实现的战斗公式（含变量定义和示例计算）
- 生成属性成长曲线数值表（逐级数据）
- 建立经济模型（水龙头/水槽平衡）
- 设计掉落率与概率系统（含保底）
- 输出难度曲线（分区域数值倍率）
- 提供平衡性自检清单

所有输出均面向程序员可直接实现的标准。
"""

import math
from typing import Dict, List, Any, Optional
from datetime import datetime


class NumericalDesignerExpert:
    """数值策划师 — 游戏数值体系设计专家"""

    def __init__(self):
        self.name = "数值策划师"
        self.version = "1.0.0"

    # ─────────────────────────────────────────────────────────────
    # 主分析入口
    # ─────────────────────────────────────────────────────────────

    def analyze(self, game_profile: Dict) -> Dict:
        """
        game_profile:
        {
            game_name:         str,
            game_type:         str,
            max_level:         int,   # 角色最高等级
            combat_style:      str,   # realtime / turnbased / action
            monetization_type: str,   # premium / f2p / hybrid
            has_gacha:         bool,
            has_pvp:           bool,
            session_length:    str,   # short(5-15) / medium(20-40) / long(60+) 分钟
            num_classes:       int,   # 职业/角色数量
            has_equipment:     bool,
            economy_currency:  str,   # 主货币名称
        }
        """
        p = self._normalize(game_profile)

        combat      = self._build_combat_system(p)
        growth      = self._build_growth_curves(p)
        economy     = self._build_economy(p)
        drops       = self._build_drop_system(p)
        difficulty  = self._build_difficulty_curve(p)
        gacha       = self._build_gacha_system(p) if p['has_gacha'] else None
        pvp         = self._build_pvp_balance(p) if p['has_pvp'] else None
        checklist   = self._build_balance_checklist(p)

        return {
            'status': 'success',
            'generated_at': datetime.now().isoformat(),
            'designer': self.name,
            'game_info': {
                'name': p['game_name'],
                'type': p['game_type'],
                'max_level': p['max_level'],
                'combat_style': p['combat_style'],
                'monetization': p['monetization_type'],
            },
            'combat_system':   combat,
            'growth_curves':   growth,
            'economy_model':   economy,
            'drop_system':     drops,
            'difficulty_curve': difficulty,
            'gacha_system':    gacha,
            'pvp_balance':     pvp,
            'balance_checklist': checklist,
        }

    # ─────────────────────────────────────────────────────────────
    # 战斗系统
    # ─────────────────────────────────────────────────────────────

    def _build_combat_system(self, p: Dict) -> Dict:
        gt    = p['game_type']
        style = p['combat_style']
        ml    = p['max_level']

        if gt in ['rpg', 'action_rpg', 'action_adventure', 'open_world']:
            return self._combat_rpg(p)
        elif gt in ['fps', 'tps', 'battle_royale']:
            return self._combat_fps(p)
        elif gt in ['strategy', 'top_down', 'rts']:
            return self._combat_strategy(p)
        elif gt in ['roguelike', 'top_down_rpg']:
            return self._combat_roguelike(p)
        elif gt == 'fighting':
            return self._combat_fighting(p)
        elif gt in ['casual', 'puzzle', 'simulation']:
            return self._combat_casual(p)
        else:
            return self._combat_rpg(p)

    def _combat_rpg(self, p: Dict) -> Dict:
        ml = p['max_level']
        base_atk = 20
        base_def = 10
        base_hp  = 500
        def_const = max(100, ml * 20)   # 防御常数，控制满级约50%减伤上限

        # 示例计算
        ex_atk  = base_atk * 10    # 满级约 ATK
        ex_def  = base_def * 10
        ex_skill = 2.5
        def_rate = ex_def / (ex_def + def_const)
        ex_dmg_raw  = round(ex_atk * ex_skill, 1)
        ex_dmg_after_def = round(ex_dmg_raw * (1 - def_rate), 1)
        ex_crit_dmg = round(ex_dmg_after_def * 1.5, 1)

        return {
            'system_name': 'RPG 战斗公式系统',
            'formulas': [
                {
                    'name': '物理伤害公式',
                    'formula': 'Final_DMG = ATK × Skill_Multiplier × (1 - DEF_Rate) × Crit_Multi × Buff_Multi',
                    'sub_formulas': [
                        f'DEF_Rate = DEF / (DEF + DEF_Constant)  [DEF_Constant = {def_const}，控制满级最大减伤约50%]',
                        'Crit_Multi = (1 + CRIT_DMG/100) 若 random() < CRIT_RATE，否则 = 1.0',
                        'Buff_Multi = Σ(所有增益倍率乘积)',
                    ],
                    'variables': {
                        'ATK':           f'攻击力，基础值={base_atk}，满级约={base_atk*10}',
                        'Skill_Multiplier': '技能倍率，普攻=1.0×，重击=2.5×，必杀技=6.0×',
                        'DEF':           f'防御力，基础值={base_def}，满级约={base_def*10}',
                        'DEF_Constant':  f'{def_const}（可调参，值越大防御效果越弱）',
                        'CRIT_RATE':     '暴击率，基础值=5%，装备可叠加至最高60%',
                        'CRIT_DMG':      '暴击伤害，基础值=50%（即1.5倍），装备可叠加至最高200%',
                    },
                    'example': (
                        f'场景：满级战士普攻一个满级普通怪\n'
                        f'  ATK={ex_atk}, Skill=1.0, DEF={ex_def}, DEF_Constant={def_const}\n'
                        f'  DEF_Rate={ex_def}/{ex_def+def_const}={round(def_rate,3)}\n'
                        f'  Raw DMG = {ex_atk} × 1.0 = {ex_atk}\n'
                        f'  After DEF = {ex_atk} × (1 - {round(def_rate,3)}) = {ex_dmg_after_def}\n'
                        f'  普通命中最终伤害 ≈ {ex_dmg_after_def}\n'
                        f'  暴击命中最终伤害 ≈ {ex_crit_dmg}'
                    ),
                    'tuning_notes': f'DEF_Constant 建议设为 {def_const}，使满级防御上限约50%减伤；如需更强防御体验可降至 {def_const//2}',
                },
                {
                    'name': '技能倍率表（参考）',
                    'formula': '按技能强度从低到高定义倍率',
                    'sub_formulas': [],
                    'variables': {},
                    'table': [
                        {'技能类型': '普通攻击', '倍率': '1.0×', '冷却': '无', '备注': '主要输出来源'},
                        {'技能类型': '快速技能', '倍率': '1.8×', '冷却': '4秒', '备注': '频繁使用的技能'},
                        {'技能类型': '强力技能', '倍率': '3.5×', '冷却': '12秒', '备注': '战术技能'},
                        {'技能类型': '终极技能', '倍率': '6.0×', '冷却': '30秒', '备注': '高CD高爆发'},
                        {'技能类型': '被动词条', '倍率': '触发加成', '冷却': '—', '备注': '额外伤害/效果'},
                    ],
                    'example': '',
                    'tuning_notes': '确保 DPS 主要来自普攻+快速技能，终极技能是爽点而非日常核心。',
                },
                {
                    'name': 'HP 伤害比例基准',
                    'formula': '玩家对同级怪物的击杀预期回合数（DPS 参考）',
                    'sub_formulas': [
                        '普通怪物 HP = 玩家输出期望 × 5回合（即约5秒实时）',
                        '精英怪物 HP = 普通怪 × 3',
                        'Boss HP    = 普通怪 × 20～50（按战斗强度设计）',
                    ],
                    'variables': {},
                    'example': (
                        f'满级玩家期望DPS≈{int(ex_dmg_after_def * 2)}/秒\n'
                        f'  普通怪HP ≈ {int(ex_dmg_after_def * 2 * 5)}\n'
                        f'  精英怪HP ≈ {int(ex_dmg_after_def * 2 * 15)}\n'
                        f'  Boss HP ≈ {int(ex_dmg_after_def * 2 * 5 * 30)}（约30秒战斗）'
                    ),
                    'tuning_notes': '关卡Boss战设计目标：玩家血量消耗50%-80%，保持紧张感但不过分挫败。',
                },
            ],
            'attribute_summary': [
                {'属性': 'HP',      '基础值': base_hp,   '满级值': base_hp * ml // 5,    '成长类型': '线性+指数混合'},
                {'属性': 'ATK',     '基础值': base_atk,  '满级值': base_atk * 10,        '成长类型': '指数成长'},
                {'属性': 'DEF',     '基础值': base_def,  '满级值': base_def * 10,        '成长类型': '指数成长（上限受DEF_Constant限制）'},
                {'属性': 'CRIT_RATE','基础值': '5%',     '满级值': '最高60%（装备叠加）', '成长类型': '装备驱动'},
                {'属性': 'CRIT_DMG', '基础值': '50%',    '满级值': '最高200%（装备叠加）','成长类型': '装备驱动'},
                {'属性': 'SPD',     '基础值': 100,       '满级值': '100-150',            '成长类型': '线性，影响行动顺序/移速'},
            ],
        }

    def _combat_fps(self, p: Dict) -> Dict:
        return {
            'system_name': 'FPS 伤害系统',
            'formulas': [
                {
                    'name': 'TTK（Time to Kill）设计公式',
                    'formula': 'TTK = MAX_HP / DPS_per_second',
                    'sub_formulas': [
                        'DPS = (Damage_per_shot × Fire_rate) × (1 + HeadShot_bonus × HeadShot_rate)',
                        '伤害衰减: Final_DMG = Base_DMG × max(0.3, 1 - Distance/Max_Range × Falloff)',
                    ],
                    'variables': {
                        'MAX_HP':       '玩家生命值，推荐100（方便百分比计算）',
                        'Fire_rate':    '射速（发/秒），步枪约8-10，手枪约4-6，狙击1-2',
                        'HeadShot_bonus': '爆头额外倍率，建议1.5×～2.5×（避免过高导致秒杀）',
                        'Falloff':      '距离衰减系数，超过有效射程后生效',
                    },
                    'example': (
                        '突击步枪示例：\n'
                        '  每发伤害=12，射速=8发/秒，爆头倍率=1.8×\n'
                        '  正常DPS = 12 × 8 = 96/秒\n'
                        '  全爆头DPS = 12 × 1.8 × 8 = 172.8/秒\n'
                        '  玩家HP=100，正常TTK≈1.04秒（约8发命中）\n'
                        '  目标TTK范围建议：0.5-2秒（太短无反应时间，太长手感拖沓）'
                    ),
                    'tuning_notes': 'TTK建议设计目标：近战1-1.5秒，中距离1.5-2.5秒，远距离2-4秒。',
                },
                {
                    'name': '武器平衡矩阵（参考）',
                    'formula': '每种武器在不同距离的DPS应互相制衡',
                    'sub_formulas': [],
                    'variables': {},
                    'table': [
                        {'武器类型': '手枪',   'DPS_近': '高', 'DPS_中': '中', 'DPS_远': '低', '弹匣': '12-15', '特点': '副武器，不占主武器格'},
                        {'武器类型': '突击步枪','DPS_近': '中', 'DPS_中': '高', 'DPS_远': '中', '弹匣': '25-30', '特点': '全能武器，平衡各距离'},
                        {'武器类型': '冲锋枪', 'DPS_近': '极高','DPS_中': '中','DPS_远': '低', '弹匣': '30-40', '特点': '近距离专项'},
                        {'武器类型': '狙击枪', 'DPS_近': '低', 'DPS_中': '高', 'DPS_远': '极高','弹匣': '5-8',  '特点': '高风险高回报，一击制敌'},
                        {'武器类型': '霰弹枪', 'DPS_近': '极高','DPS_中': '低','DPS_远': '极低','弹匣': '6-8',  '特点': '极近距离专项'},
                    ],
                    'example': '',
                    'tuning_notes': '武器应各有擅长的场景，避免一种武器在所有情况下都是最优解。',
                },
            ],
            'attribute_summary': [
                {'属性': 'HP',   '基础值': 100,  '满级值': 100,  '成长类型': '固定（FPS通常无成长）'},
                {'属性': 'Armor','基础值': 0,    '满级值': 50,   '成长类型': '装备驱动（减伤但不增HP）'},
                {'属性': 'Speed','基础值': 5,    '满级值': '4-6','成长类型': '武器决定移速'},
            ],
        }

    def _combat_strategy(self, p: Dict) -> Dict:
        return {
            'system_name': '策略战斗单位系统',
            'formulas': [
                {
                    'name': '单位战斗公式',
                    'formula': 'Net_DMG = ATK × ATK_Multiplier × (1 - DEF / (DEF + 100))',
                    'sub_formulas': [
                        '克制加成: if counter_type: Net_DMG × 1.5',
                        '地形加成: if high_ground: Net_DMG × 1.2',
                        '士气系统（可选）: Morale_Bonus = (当前HP/最大HP) × 0.2 + 0.8',
                    ],
                    'variables': {
                        'ATK':            '单位攻击力',
                        'ATK_Multiplier': '攻击类型倍率（远程vs近战 = 0.8，同类=1.0）',
                        'DEF':            '单位防御力',
                        'counter_type':   '是否属于克制关系（步兵>弓兵>骑兵>步兵等）',
                    },
                    'example': '步兵(ATK=50, DEF=60) 攻击 弓兵(DEF=20)：\n  Net_DMG = 50 × 1.5（克制）× (1 - 20/120) = 50 × 1.5 × 0.833 = 62.5',
                    'tuning_notes': '设计克制三角保证没有绝对最强单位。',
                },
            ],
            'attribute_summary': [
                {'属性': 'HP',   '基础值': 100, '满级值': '按单位类型',  '成长类型': '固定（由单位等级决定）'},
                {'属性': 'ATK',  '基础值': 30,  '满级值': '按科技等级', '成长类型': '科技树升级'},
                {'属性': 'DEF',  '基础值': 20,  '满级值': '按科技等级', '成长类型': '科技树升级'},
                {'属性': 'Range','基础值': 1,   '满级值': '1-6格',      '成长类型': '单位类型固定'},
            ],
        }

    def _combat_roguelike(self, p: Dict) -> Dict:
        return {
            'system_name': 'Roguelike 战斗系统',
            'formulas': [
                {
                    'name': '基础伤害公式（词条叠加型）',
                    'formula': 'Final_DMG = Base_DMG × (1 + Flat_Bonus) × Multiplier_Chain',
                    'sub_formulas': [
                        'Flat_Bonus = Σ(所有加法词条)，如+20%、+35%等',
                        'Multiplier_Chain = Π(所有乘法词条)，如×1.5、×2.0等',
                        '设计关键：加法词条叠加上限，避免无限放大',
                    ],
                    'variables': {
                        'Base_DMG':       '基础伤害（随关卡深度线性增长）',
                        'Flat_Bonus':     '平层词条总和（建议单项上限200%，总计上限500%）',
                        'Multiplier_Chain': '乘法词条（稀有词条，2-3个即可产生质变）',
                    },
                    'example': (
                        '普通构筑：Base=50, Flat_Bonus=1.5(+150%), Multiplier=1.2\n'
                        '  Final = 50 × 2.5 × 1.2 = 150\n'
                        'S级构筑（神话）：Base=50, Flat=4.0(+400%), Multiplier=3.0\n'
                        '  Final = 50 × 5.0 × 3.0 = 750（15倍，符合神话级体验）'
                    ),
                    'tuning_notes': '保证普通玩家通关同时允许强力构筑带来10-20倍伤害差距（爽快感来源）。',
                },
            ],
            'attribute_summary': [
                {'属性': 'HP',      '基础值': 80,  '满级值': '词条决定', '成长类型': '每层+固定量+词条加成'},
                {'属性': 'Base_DMG','基础值': 10,  '满级值': '词条决定', '成长类型': '层数×1.1 每层'},
                {'属性': 'Speed',   '基础值': 5,   '满级值': '词条决定', '成长类型': '词条驱动'},
            ],
        }

    def _combat_fighting(self, p: Dict) -> Dict:
        return {
            'system_name': '格斗游戏帧数据系统',
            'formulas': [
                {
                    'name': '技能帧数设计规范',
                    'formula': 'Move_Frame = Startup + Active + Recovery',
                    'sub_formulas': [
                        '优势帧数（On-hit Advantage）= Hit_Stun - Recovery（正值=强势）',
                        '劣势帧数（On-block Disadvantage）= Block_Stun - Recovery（负值=被反击风险）',
                        '伤害公式: DMG = Base_DMG × Counter_Hit_Bonus（若逆风则×1.25）',
                    ],
                    'variables': {
                        'Startup':    '起始帧（出招前摇），1帧≈1/60秒。速攻技3-5帧，大招15-25帧',
                        'Active':     '判定帧（实际命中窗口），通常2-8帧',
                        'Recovery':   '后摇帧（动作结束恢复），速攻技10-15帧，大招25-40帧',
                        'Hit_Stun':   '对手被命中的僵直帧数，决定连招可能性',
                        'Block_Stun': '对手格挡时的僵直帧数，通常比Hit_Stun少3-5帧',
                    },
                    'example': (
                        '速攻拳：Startup=4f, Active=3f, Recovery=12f\n'
                        '  Hit_Stun=18f → 优势帧=18-12=+6f（可继续连段）\n'
                        '  Block_Stun=13f → 劣势帧=13-12=+1f（安全出招）\n\n'
                        '大招：Startup=18f, Active=5f, Recovery=35f\n'
                        '  Hit_Stun=40f → 优势帧=40-35=+5f\n'
                        '  Block_Stun=25f → 劣势帧=25-35=-10f（被格挡后危险！）'
                    ),
                    'tuning_notes': '每个角色应有速攻安全技（低劣势）、中等连段技、高风险大招（负帧）的完整体系。',
                },
            ],
            'attribute_summary': [
                {'属性': 'HP',     '基础值': 1000, '满级值': '1000（固定）', '成长类型': '固定，通过连招减少'},
                {'属性': '超必杀槽','基础值': '3格','满级值': '3格（固定）', '成长类型': '受击/攻击积累'},
            ],
        }

    def _combat_casual(self, p: Dict) -> Dict:
        return {
            'system_name': '休闲游戏评分系统',
            'formulas': [
                {
                    'name': '关卡评分公式',
                    'formula': 'Score = (Base_Score × Combo_Multiplier + Time_Bonus) × Accuracy_Rate',
                    'sub_formulas': [
                        'Combo_Multiplier = 1 + (Combo_Count × 0.1)，最高×5.0',
                        'Time_Bonus = max(0, Time_Left × 10)',
                        'Accuracy_Rate = Hit_Count / Total_Actions（区间0.5-1.0）',
                    ],
                    'variables': {
                        'Base_Score':      '每次成功操作的基础分，建议100-500',
                        'Combo_Count':     '连续成功次数',
                        'Time_Left':       '剩余时间（秒），若有计时限制',
                        'Accuracy_Rate':   '操作准确率，失误太多降低最终评分',
                    },
                    'example': '连击20次，用时30秒（剩余10秒），准确率90%：\n  Score = (100×100×3.0 + 10×10) × 0.9 = (30000+100)×0.9 = 27,090分',
                    'tuning_notes': '三星标准建议覆盖玩家人数的60-70%；设计时先确定三星目标分再反推连击要求。',
                },
            ],
            'attribute_summary': [
                {'属性': '生命/机会', '基础值': '3次', '满级值': '3-5次', '成长类型': '道具购买增加'},
            ],
        }

    # ─────────────────────────────────────────────────────────────
    # 成长曲线
    # ─────────────────────────────────────────────────────────────

    def _build_growth_curves(self, p: Dict) -> Dict:
        ml = p['max_level']
        gt = p['game_type']

        # 属性基础参数（按游戏类型调整）
        if gt in ['fps', 'battle_royale']:
            return {'note': 'FPS类游戏通常无等级成长，角色能力固定，通过武器和装备区分强度。'}

        base_hp  = 500
        base_atk = 20
        base_def = 10

        # 生成每5级的数值表
        def hp_at(lv):
            if lv <= 20:
                return int(base_hp + (lv-1) * 80)
            elif lv <= 50:
                return int((base_hp + 19*80) * (1.05 ** (lv-20)))
            else:
                cap = (base_hp + 19*80) * (1.05**30)
                return int(cap + (lv-50) * cap * 0.02)

        def atk_at(lv):
            return int(base_atk * (1.08 ** (lv-1)))

        def def_at(lv):
            return int(base_def * (1.07 ** (lv-1)))

        def exp_needed(lv):
            return int(100 * (lv ** 1.85))

        checkpoints = [1] + list(range(5, ml+1, max(1, ml//10))) + [ml]
        checkpoints = sorted(set(checkpoints))

        attr_table = []
        for lv in checkpoints:
            attr_table.append({
                '等级':     lv,
                'HP':       hp_at(lv),
                'ATK':      atk_at(lv),
                'DEF':      def_at(lv),
                '升级所需EXP': exp_needed(lv) if lv < ml else '—（满级）',
            })

        # 敌人对应数值（同级敌人）
        enemy_table = []
        for lv in checkpoints:
            enemy_table.append({
                '等级':       lv,
                '普通怪HP':   int(hp_at(lv) * 0.6),
                '精英怪HP':   int(hp_at(lv) * 2.0),
                'Boss_HP':    int(hp_at(lv) * 15),
                '普通怪ATK':  int(atk_at(lv) * 0.7),
            })

        return {
            'formulas': {
                'hp':  f'HP(lv) = {base_hp} + (lv-1)×80（1-20级线性）→ 1.05^(lv-20)指数（20-50级）',
                'atk': f'ATK(lv) = {base_atk} × 1.08^(lv-1)（全程指数）',
                'def': f'DEF(lv) = {base_def} × 1.07^(lv-1)（全程指数，受DEF_Constant限制实际减伤）',
                'exp': f'EXP_needed(lv) = 100 × lv^1.85（指数加速，确保后期每级需要明显更多努力）',
            },
            'player_attribute_table': attr_table,
            'enemy_reference_table':  enemy_table,
            'design_notes': [
                f'满级({ml}级)HP约为1级的{hp_at(ml)//base_hp}倍，ATK约为{atk_at(ml)//base_atk}倍',
                '敌人HP = 玩家同级HP × 系数：普通怪×0.6，精英×2.0，Boss×15（可按关卡调整）',
                '升级体验：前20级较快（教学期），20-60%进度适中（主要游玩期），最后20%明显减慢（消耗期）',
            ],
        }

    # ─────────────────────────────────────────────────────────────
    # 经济模型
    # ─────────────────────────────────────────────────────────────

    def _build_economy(self, p: Dict) -> Dict:
        mt       = p['monetization_type']
        currency = p['economy_currency']
        gt       = p['game_type']
        session  = p['session_length']

        session_mult = {'short': 0.5, 'medium': 1.0, 'long': 2.0}.get(session, 1.0)

        # 日收益基准
        base_daily = int(1000 * session_mult)

        sources = [
            {'来源': '主线任务/关卡通关', '日收益': int(base_daily * 0.40), '频率': '每日1-3次', '备注': '最稳定的主要来源'},
            {'来源': '日常任务',          '日收益': int(base_daily * 0.25), '频率': '每日重置', '备注': '驱动日活的核心机制'},
            {'来源': '战斗掉落',          '日收益': int(base_daily * 0.20), '频率': '持续游玩', '备注': '鼓励游玩时长的奖励'},
            {'来源': '成就/里程碑',       '日收益': int(base_daily * 0.10), '频率': '一次性', '备注': '长期目标奖励'},
            {'来源': '活动/赛季奖励',     '日收益': int(base_daily * 0.05), '频率': '活动期间', '备注': '回访激励'},
        ]
        total_income = sum(s['日收益'] for s in sources)

        if mt == 'f2p':
            sinks = [
                {'消耗项': '装备强化/升级',    '日消耗': int(total_income * 0.35), '是否必要': '是', '备注': '核心成长消耗，持续存在'},
                {'消耗项': '技能解锁',          '日消耗': int(total_income * 0.20), '是否必要': '是', '备注': '一次性但金额较大'},
                {'消耗项': '商店购买',          '日消耗': int(total_income * 0.25), '是否必要': '否', '备注': '玩家主动决策消耗'},
                {'消耗项': '复活/续关',         '日消耗': int(total_income * 0.10), '是否必要': '否', '备注': '失败时的软变现点'},
                {'消耗项': '加速/体力恢复',     '日消耗': int(total_income * 0.10), '是否必要': '否', '备注': '时间稀缺性变现'},
            ]
            premium_note = '虚拟货币（高级）：内购获取，用于稀有装备/外观，不影响核心游玩公平性'
        elif mt == 'premium':
            sinks = [
                {'消耗项': '装备强化',    '日消耗': int(total_income * 0.50), '是否必要': '是', '备注': '主要消耗'},
                {'消耗项': '建筑/科技升级','日消耗': int(total_income * 0.30), '是否必要': '是', '备注': '进度消耗'},
                {'消耗项': '商店',        '日消耗': int(total_income * 0.20), '是否必要': '否', '备注': '非必须消耗'},
            ]
            premium_note = '买断制游戏无内购变现，货币系统专注于游戏内数值意义'
        else:  # hybrid
            sinks = [
                {'消耗项': '装备强化',  '日消耗': int(total_income * 0.40), '是否必要': '是', '备注': '核心消耗'},
                {'消耗项': 'DLC内容',   '日消耗': int(total_income * 0.20), '是否必要': '否', '备注': '额外内容'},
                {'消耗项': '外观道具',  '日消耗': int(total_income * 0.40), '是否必要': '否', '备注': '美观变现'},
            ]
            premium_note = '混合模式：基础内容买断，外观/DLC追加变现'

        total_sink = sum(s['日消耗'] for s in sinks)
        balance_ratio = total_sink / total_income if total_income else 1.0

        if balance_ratio < 0.75:
            balance_status = '⚠️ 偏宽松（玩家大量积累，通货膨胀风险）'
        elif balance_ratio > 1.15:
            balance_status = '⚠️ 偏紧张（玩家资源不足，体验压力大）'
        else:
            balance_status = '✅ 基本平衡（建议目标：收支比0.85-1.1）'

        return {
            'currency_name': currency,
            'monetization_type': mt,
            'daily_income': {
                'sources': sources,
                'total': total_income,
                'note': f'基于每日游玩{session_mult}倍标准时长估算',
            },
            'daily_sinks': {
                'sinks': sinks,
                'total': total_sink,
            },
            'balance': {
                'ratio': round(balance_ratio, 2),
                'status': balance_status,
                'target': '收支比建议 0.85-1.1，让玩家保持轻微积累感',
            },
            'premium_currency': premium_note,
            'economy_rules': [
                '关键原则1：货币产出要有明确来源，玩家能预期每日收入',
                '关键原则2：每一个主要消耗项都要有对应的玩法意义',
                '关键原则3：定期通过活动/赛季引入额外消耗，防止长期通货膨胀',
                '关键原则4：初期给玩家充足资源（前3天宽松），让其感受到系统深度',
            ],
        }

    # ─────────────────────────────────────────────────────────────
    # 掉落系统
    # ─────────────────────────────────────────────────────────────

    def _build_drop_system(self, p: Dict) -> Dict:
        gt = p['game_type']

        if gt in ['casual', 'puzzle', 'simulation']:
            return {
                'note': '休闲/模拟类游戏通常使用固定奖励而非随机掉落，建议按关卡设置固定奖励池',
                'tiers': [],
            }

        tiers = [
            {'品质': '普通（白）',  '颜色': '#9d9d9d', '掉落率': '60.0%', '累计概率': '60.0%',  '期望掉落间隔': '每2次掉落约1件', '示例用途': '基础材料、消耗品'},
            {'品质': '非凡（绿）',  '颜色': '#1eff00', '掉落率': '25.0%', '累计概率': '85.0%',  '期望掉落间隔': '每4次掉落约1件', '示例用途': '基础装备、配件'},
            {'品质': '稀有（蓝）',  '颜色': '#0070dd', '掉落率': '10.0%', '累计概率': '95.0%',  '期望掉落间隔': '每10次掉落约1件','示例用途': '有效属性装备'},
            {'品质': '史诗（紫）',  '颜色': '#a335ee', '掉落率': '4.0%',  '累计概率': '99.0%',  '期望掉落间隔': '每25次掉落约1件','示例用途': '强力装备、技能书'},
            {'品质': '传说（橙）',  '颜色': '#ff8000', '掉落率': '1.0%',  '累计概率': '100.0%', '期望掉落间隔': '每100次掉落约1件','示例用途': '顶级装备、稀有外观'},
        ]

        pity = None
        if p['has_gacha'] or gt in ['rpg', 'action_rpg']:
            pity = {
                'soft_pity_start': 70,
                'soft_pity_boost': '每次+4%传说概率',
                'hard_pity':       100,
                'description':     '第70次未出传说后，每次额外+4%概率；第100次必出传说',
                'expected_pulls':  '期望约75次出1件传说',
            }

        return {
            'tiers': tiers,
            'pity_system': pity,
            'design_rules': [
                '普通+非凡品质应占总掉落85%以上，避免玩家产生"什么都没掉"的感受',
                '传说装备1%概率来自Boss/精英怪掉落，普通怪不掉传说',
                '保底系统（Pity）是玩家心理安全感的关键，即使玩家不触发也会感到放心',
                '装备需要有属性多样性，同品质下有2-4种随机属性词条，增加追求深度',
            ],
            'anti_farming_tips': [
                '每日限制传说掉落次数（建议每日最多1次）防止脚本刷取',
                '引入"熔炼"系统：X件非凡/稀有装备合成1件更高品质',
            ],
        }

    # ─────────────────────────────────────────────────────────────
    # 难度曲线
    # ─────────────────────────────────────────────────────────────

    def _build_difficulty_curve(self, p: Dict) -> Dict:
        ml = p['max_level']
        gt = p['game_type']

        if gt in ['fps', 'battle_royale', 'fighting']:
            return {
                'note': '此类游戏难度主要来自玩家对抗而非数值设计，难度曲线体现为段位/匹配机制。',
                'matchmaking_principle': 'ELO/MMR系统使玩家始终匹配到约50%胜率的对手',
            }

        # 按百分比划分区域
        zones = [
            {'区域': '教学区',   '关卡范围': f'1-{ml//10}级',           '敌人ATK倍率': 0.6,  '敌人HP倍率': 0.6,  '预期玩家胜率': '95%+', '设计目标': '零失败体验，建立核心操作信心'},
            {'区域': '新手区',   '关卡范围': f'{ml//10+1}-{ml//4}级',   '敌人ATK倍率': 0.8,  '敌人HP倍率': 0.8,  '预期玩家胜率': '85%',  '设计目标': '引入更多机制，允许偶尔失败'},
            {'区域': '成长区',   '关卡范围': f'{ml//4+1}-{ml//2}级',   '敌人ATK倍率': 1.0,  '敌人HP倍率': 1.0,  '预期玩家胜率': '70%',  '设计目标': '主要游玩区段，挑战感和成就感并存'},
            {'区域': '挑战区',   '关卡范围': f'{ml//2+1}-{ml*3//4}级', '敌人ATK倍率': 1.25, '敌人HP倍率': 1.3,  '预期玩家胜率': '55%',  '设计目标': '需要好装备和一定技术，筛选核心玩家'},
            {'区域': '精英区',   '关卡范围': f'{ml*3//4+1}-{ml-1}级',  '敌人ATK倍率': 1.6,  '敌人HP倍率': 1.8,  '预期玩家胜率': '40%',  '设计目标': '高难度内容，面向硬核玩家'},
            {'区域': '终局内容', '关卡范围': f'{ml}级+（终局）',         '敌人ATK倍率': 2.0,  '敌人HP倍率': 2.5,  '预期玩家胜率': '25%',  '设计目标': '极限挑战，长期目标内容'},
        ]

        return {
            'zones': zones,
            'pacing_pattern': [
                '教学→正常→挑战→休息关（Boss前休息）→Boss→放松→循环',
                '每5-10关设置一个"奖励关"，降低难度提升掉落，制造正向情绪爆发点',
                'Boss 战前1-2关的难度应略低（"呼吸空间"），让玩家在挑战Boss前放松',
            ],
            'difficulty_knobs': [
                '敌人ATK/HP倍率（主要调节手段）',
                '敌人数量（在ATK不变的情况下增加压力）',
                '敌人AI行为复杂度（新攻击模式引入）',
                '资源稀缺度（药品/子弹等补给频率）',
                '时间限制（增加决策压力）',
            ],
        }

    # ─────────────────────────────────────────────────────────────
    # 抽卡系统
    # ─────────────────────────────────────────────────────────────

    def _build_gacha_system(self, p: Dict) -> Dict:
        return {
            'overview': '抽卡/转蛋系统设计规范',
            'ssr_rates': [
                {'活动类型': '普通池',   '基础SSR率': '0.6%', '软保底': '60抽后每抽+6%', '硬保底': '90抽必出', '期望抽数': '~65抽'},
                {'活动类型': '限定池',   '基础SSR率': '0.6%', '软保底': '60抽后每抽+6%', '硬保底': '90抽必出', '期望抽数': '~65抽（50%概率出限定）'},
                {'活动类型': '精选池',   '基础SSR率': '1.5%', '软保底': '40抽后每抽+6%', '硬保底': '60抽必出', '期望抽数': '~38抽'},
            ],
            'probability_table': [
                {'抽数': 1,  '单次出率': '0.60%', '累计不出率': '99.40%'},
                {'抽数': 10, '单次出率': '0.60%', '累计不出率': '94.13%'},
                {'抽数': 30, '单次出率': '0.60%', '累计不出率': '83.40%'},
                {'抽数': 60, '单次出率': '0.60%→+6%/抽', '累计不出率': '69.76%'},
                {'抽数': 75, '单次出率': '90.60%（软保底）', '累计不出率': '~3%'},
                {'抽数': 90, '单次出率': '100%（硬保底）', '累计不出率': '0%'},
            ],
            'design_rules': [
                '软保底必须从概率上可见（UI显示"距保底N抽"）',
                '限定池的"50%机制"：首次出SSR有50%是限定，否则下次必出限定（歪了保底）',
                '单价建议：160元人民币约10抽（参考行业标准），硬保底约1440元',
                '每月首充双倍、每日小额抽卡包是重要的付费切入点',
            ],
            'compliance_note': '⚠️ 中国大陆市场要求：必须公示每种道具的精确概率；未成年人充值限额（8岁以下禁止，8-16岁月上限200元）',
        }

    # ─────────────────────────────────────────────────────────────
    # PvP 平衡
    # ─────────────────────────────────────────────────────────────

    def _build_pvp_balance(self, p: Dict) -> Dict:
        return {
            'matchmaking': {
                'system': 'ELO/MMR 天梯系统',
                'formula': "MMR_change = K × (Actual_outcome - Expected_outcome)\n  Expected_outcome = 1 / (1 + 10^((Opponent_MMR - Player_MMR) / 400))\n  K因子建议：新玩家K=40，中段K=20，顶级K=10",
                'example': 'MMR=1500玩家胜MMR=1600对手：Expected=0.36，Actual=1\n  MMR变化 = 20 × (1-0.36) = +12.8 ≈ +13',
            },
            'balance_principles': [
                '能力（P2W）与外观（F2P）严格隔离，付费不提升战斗属性',
                '英雄/角色平衡：胜率目标45%-55%（±5%视为正常方差）',
                '超过55%胜率触发削弱，低于45%触发强化（每两周一次数据分析）',
                '新内容引入后的"蜜月期"（前2周）允许±10%偏差，再收紧',
            ],
            'anti_cheat': [
                '服务端权威：关键战斗逻辑在服务端计算，客户端仅做预测',
                '延迟补偿：记录客户端输入时间戳，服务端回溯验证',
                '异常检测：每秒输入频率、移动速度超出阈值自动标记',
            ],
        }

    # ─────────────────────────────────────────────────────────────
    # 平衡性自检清单
    # ─────────────────────────────────────────────────────────────

    def _build_balance_checklist(self, p: Dict) -> List[Dict]:
        return [
            {'类别': '战斗公式', '检查项': '同级玩家对同级普通怪的期望战斗时长是否在5-15秒？',          '风险': '太短=无手感，太长=无聊'},
            {'类别': '战斗公式', '检查项': 'Boss战是否设计为玩家血量损耗50-80%才能击败？',            '风险': '太简单=无挑战，太难=沮丧'},
            {'类别': '成长曲线', '检查项': '每个等级的属性提升是否可以被玩家感知（≥3-5%每级）？',     '风险': '低于3%玩家感受不到成长'},
            {'类别': '成长曲线', '检查项': '满级属性与1级的差距是否合理（建议10-30倍，过大导致新区域秒杀）？', '风险': '差距过大破坏跨区对战体验'},
            {'类别': '经济系统', '检查项': '新玩家第一天是否能获得足够资源体验核心强化系统？',         '风险': '新手资源不足导致流失'},
            {'类别': '经济系统', '检查项': '老玩家是否有持续的资源消耗目标（避免资源积压过多）？',      '风险': '资源过剩导致内容枯竭感'},
            {'类别': '掉落系统', '检查项': '玩家连续游玩30分钟是否必然获得至少1件有意义的奖励？',      '风险': '长时间无奖励导致离开游戏'},
            {'类别': '掉落系统', '检查项': '传说装备的掉落是否有保底机制避免极端坏运气？',             '风险': '无保底导致极少数玩家长期无传说'},
            {'类别': '难度曲线', '检查项': '前10%的关卡新手失败率是否低于20%？',                     '风险': '新手区过难导致早期流失'},
            {'类别': '难度曲线', '检查项': '是否每5-10关有一个"奖励关/休息关"作为情绪爆发点？',       '风险': '连续高难度不设喘息导致疲惫'},
            {'类别': 'PvP平衡',  '检查项': '各英雄/职业的胜率方差是否在5%以内？',                   '风险': '胜率偏差>10%表明严重失衡'},
        ]

    # ─────────────────────────────────────────────────────────────
    # 辅助
    # ─────────────────────────────────────────────────────────────

    def _normalize(self, raw: Dict) -> Dict:
        p = dict(raw)
        p.setdefault('game_name', '未命名游戏')
        p.setdefault('game_type', 'rpg')
        p.setdefault('max_level', 30)
        p.setdefault('combat_style', 'realtime')
        p.setdefault('monetization_type', 'f2p')
        p.setdefault('has_gacha', False)
        p.setdefault('has_pvp', False)
        p.setdefault('session_length', 'medium')
        p.setdefault('num_classes', 1)
        p.setdefault('has_equipment', True)
        p.setdefault('economy_currency', '金币')
        # 标准化max_level
        p['max_level'] = max(5, min(200, int(p['max_level'])))
        return p
