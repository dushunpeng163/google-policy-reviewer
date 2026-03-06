#!/usr/bin/env python3
"""
Unity 架构师专家 (Unity Architect Expert)

职责:
- 根据游戏描述进行技术选型
- 设计系统架构方案
- 推荐 Asset Store 资源包
- 生成实施路线图
- 提供风险评估与备选方案

知识库覆盖:
- 渲染管线: URP / HDRP / Built-in
- 游戏框架: Game Creator 2 / Opsive UCC / Corgi Engine / Top Down Engine / Feel / 自研
- 网络框架: FishNet / Mirror / Photon Fusion / Photon Quantum / NGO / Nakama / PlayFab
- 系统选型: 存档/UI/音频/AI/摄像机/输入/架构模式/热更新
- 资源包:   Synty Studios / Infinity PBR / NatureManufacture / Seaside Studio / Hovl Studio / Gaia
- 架构模式: ScriptableObject 架构 / VContainer DI / DOTS ECS / 事件总线
"""

from typing import Dict, List, Optional, Any
from datetime import datetime


class UnityArchitectExpert:
    """Unity 架构师 - 游戏技术选型与系统设计专家"""

    def __init__(self):
        self.name = "Unity 架构师"
        self.version = "1.0.0"
        self._build_knowledge_base()

    # ─────────────────────────────────────────────────────────────
    # 知识库构建
    # ─────────────────────────────────────────────────────────────

    def _build_knowledge_base(self):
        self._build_frameworks()
        self._build_render_pipelines()
        self._build_network_frameworks()
        self._build_systems()
        self._build_asset_packs()

    def _build_frameworks(self):
        self.frameworks = {
            'game_creator_2': {
                'name': 'Game Creator 2',
                'publisher': 'Catsoft Works',
                'url': 'https://gamecreator.io',
                'type': 'comprehensive_framework',
                'license': 'paid_modular',
                'cost_estimate': '$80–400+（Core + 模块）',
                'best_for': ['rpg', 'action_rpg', 'action_adventure', 'narrative', 'open_world', 'metroidvania'],
                'not_for': ['fighting', 'racing', 'casual_puzzle', 'hyper_casual', 'card_game'],
                'platform_support': ['pc', 'mobile', 'console'],
                'team_sizes': ['solo', 'small', 'medium'],
                'core_strengths': [
                    'Action / Condition / Trigger 可视化逻辑系统，无需大量代码',
                    '丰富模块生态：背包/任务/对话/属性/近战/射击/骑乘/伙伴',
                    'ScriptableObject 驱动，数据与逻辑高度分离',
                    '相比自研节省 60–80% 基础系统开发时间',
                    '文档完善、社区活跃、持续更新',
                ],
                'weaknesses': [
                    '自带角色控制器深度定制困难，与自研物理玩法冲突风险高',
                    '模块费用叠加后成本不低，需提前规划',
                    '不适合超大规模实体场景（数千以上需 ECS）',
                ],
                'key_modules': {
                    'Core':       '必需，含 Action/Condition/Trigger/Camera/Character 基础',
                    'Inventory':  '背包、装备、掉落系统',
                    'Quests':     '任务、目标、奖励系统',
                    'Dialogue':   '对话树、分支、条件对话',
                    'Stats':      '属性、战斗公式、Buff/Debuff',
                    'Shooter':    '射击、弹道、武器系统',
                    'Melee':      '近战、连击、格挡系统',
                    'Traversal':  '攀爬、翻越、跑酷',
                    'Horses':     '骑乘系统',
                    'Companions': '伙伴 AI、跟随、指令',
                },
            },
            'opsive_ucc': {
                'name': 'Opsive Ultimate Character Controller',
                'publisher': 'Opsive',
                'url': 'https://opsive.com',
                'type': 'character_framework',
                'license': 'paid',
                'cost_estimate': '$100–200',
                'best_for': ['fps', 'tps', 'action', 'survival', 'battle_royale'],
                'not_for': ['casual', 'puzzle', 'card_game', 'strategy', '2d_platformer'],
                'platform_support': ['pc', 'mobile', 'console'],
                'team_sizes': ['small', 'medium', 'large'],
                'core_strengths': [
                    '最强的第一/三人称角色控制器，无缝视角切换',
                    '丰富移动能力系统（游泳、爬行、蹲伏、翻滚）',
                    '配套完整武器系统与伤害处理系统',
                    '主机手柄适配完善',
                ],
                'weaknesses': [
                    '学习曲线较陡，配置复杂',
                    '与 Game Creator 2 存在角色控制器冲突风险',
                ],
            },
            'corgi_engine': {
                'name': 'Corgi Engine',
                'publisher': 'More Mountains',
                'url': 'https://corgi-engine.moremountains.com',
                'type': 'platformer_framework',
                'license': 'paid',
                'cost_estimate': '$65',
                'best_for': ['2d_platformer', 'metroidvania', 'run_and_gun'],
                'not_for': ['3d_tps', 'fps', 'top_down', 'strategy'],
                'platform_support': ['pc', 'mobile', 'console'],
                'team_sizes': ['solo', 'small', 'medium'],
                'core_strengths': [
                    '2D 横板游戏手感极佳，久经生产验证',
                    '内置大量角色能力（跳跃/攀爬/滑行/冲刺/双段跳）',
                    '配套 Feel 插件提供强烈游戏反馈',
                    '文档和示例完整',
                ],
                'weaknesses': ['仅适合横板平台类游戏，3D 支持有限'],
            },
            'top_down_engine': {
                'name': 'Top Down Engine',
                'publisher': 'More Mountains',
                'url': 'https://top-down-engine.moremountains.com',
                'type': 'topdown_framework',
                'license': 'paid',
                'cost_estimate': '$75',
                'best_for': ['top_down', 'top_down_rpg', 'top_down_shooter', 'twin_stick', 'roguelike'],
                'not_for': ['3d_tps', 'fps', '2d_platformer'],
                'platform_support': ['pc', 'mobile', 'console'],
                'team_sizes': ['solo', 'small', 'medium'],
                'core_strengths': [
                    '俯视角系统完整（含 AI / 武器 / 关卡管理）',
                    '2D / 2.5D 均支持',
                    '同样具备 Feel 插件支持',
                ],
                'weaknesses': ['深度定制需修改核心代码'],
            },
            'feel': {
                'name': 'Feel',
                'publisher': 'More Mountains',
                'url': 'https://feel.moremountains.com',
                'type': 'game_feel_library',
                'license': 'paid',
                'cost_estimate': '$35',
                'best_for': ['all'],
                'not_for': [],
                'platform_support': ['pc', 'mobile', 'console'],
                'team_sizes': ['solo', 'small', 'medium', 'large'],
                'core_strengths': [
                    '专项游戏"手感"和 Juice 效果库',
                    '屏幕震动、相机抖动、闪光、慢动作、粒子爆发',
                    '几乎适合所有类型游戏，作为增强层无痛集成',
                    'Corgi Engine / Top Down Engine 购买者有折扣',
                ],
                'weaknesses': ['是增强层而非独立框架，需搭配其他系统'],
            },
            'scratch': {
                'name': '完全自研',
                'publisher': None,
                'url': None,
                'type': 'custom',
                'license': 'free',
                'cost_estimate': '$0（开发时间成本高）',
                'best_for': ['fighting', 'racing', 'sports', 'simulation', 'highly_custom', 'hyper_casual', 'card_game'],
                'not_for': [],
                'platform_support': ['pc', 'mobile', 'console', 'webgl'],
                'team_sizes': ['medium', 'large'],
                'core_strengths': [
                    '完全控制每个系统，无框架约束',
                    '性能最优化空间最大，技术债最低',
                    '无第三方依赖风险，长期维护成本可控',
                ],
                'weaknesses': [
                    '开发周期最长，适合有完整技术团队的项目',
                    '需要自行维护所有基础系统',
                ],
            },
        }

    def _build_render_pipelines(self):
        self.render_pipelines = {
            'urp': {
                'name': 'Universal Render Pipeline (URP)',
                'best_for': ['mobile', 'stylized', 'performance_critical', 'webgl', 'cross_platform'],
                'not_for': ['photorealistic_pc_exclusive'],
                'platform_support': ['pc', 'mobile', 'console', 'webgl'],
                'strengths': [
                    '跨平台支持最广，移动端性能优先',
                    'Shader Graph 支持完整，VFX Graph 支持良好',
                    'Asset Store 资源优先支持 URP，生态最完整',
                    '渲染特性持续追赶 HDRP',
                ],
                'weaknesses': ['高端光照效果不及 HDRP'],
            },
            'hdrp': {
                'name': 'High Definition Render Pipeline (HDRP)',
                'best_for': ['pc_highend', 'console', 'photorealistic', 'arch_viz'],
                'not_for': ['mobile', 'webgl', 'casual', 'low_end_device'],
                'platform_support': ['pc', 'console'],
                'strengths': [
                    '顶级光照质量（体积光、SSGI、光线追踪）',
                    '电影级渲染效果，适合高端 PC / 主机游戏',
                    'Shader Graph 与光照系统深度集成',
                ],
                'weaknesses': [
                    '不支持移动端，硬件要求高',
                    '部分 Asset Store 资源需手动升级材质',
                    '包体积和显存占用更大',
                ],
            },
            'builtin': {
                'name': 'Built-in Render Pipeline',
                'best_for': ['legacy_maintenance'],
                'not_for': ['new_projects'],
                'note': '⚠️ 新项目禁止使用。Unity 已明确该管线进入维护模式，不再添加新功能。',
            },
        }

    def _build_network_frameworks(self):
        self.network_frameworks = {
            'none': {
                'name': '单机（无网络框架）',
                'best_for': ['singleplayer', 'offline'],
                'cost': 'free',
                'description': '无需任何网络框架',
            },
            'fishnet': {
                'name': 'FishNet',
                'type': 'open_source',
                'cost': 'free',
                'url': 'https://fish-networking.gitbook.io',
                'best_for': ['coop', 'mmo_prototype', 'indie_multiplayer', 'small_competitive'],
                'not_for': ['ultra_low_latency_competitive'],
                'strengths': [
                    '2024 年增长最快的开源网络框架，正在取代 Mirror',
                    '功能丰富：预测插值 / AOI 兴趣管理 / 场景管理',
                    '社区活跃，文档持续完善，完全免费',
                ],
                'weaknesses': ['相比 Mirror 历史积累稍短，生产案例仍在积累中'],
            },
            'mirror': {
                'name': 'Mirror',
                'type': 'open_source',
                'cost': 'free',
                'best_for': ['mmo_prototype', 'coop', 'moba', 'legacy_unet_migration'],
                'not_for': ['new_competitive_fps'],
                'strengths': [
                    '开源成熟，5000+ GitHub Stars，大量生产案例',
                    '从 UNET 迁移路径清晰',
                ],
                'weaknesses': ['已进入维护期，新项目建议优先考虑 FishNet'],
            },
            'photon_fusion': {
                'name': 'Photon Fusion',
                'type': 'managed_service',
                'cost': 'freemium（按 CCU 计费）',
                'url': 'https://www.photonengine.com/fusion',
                'best_for': ['competitive_fps', 'battle_royale', 'sports', 'fast_paced_action'],
                'not_for': ['mmo_large_scale', 'budget_limited'],
                'strengths': [
                    '支持 Rollback Netcode，竞技类低延迟首选',
                    '托管服务，无需运维服务器',
                    '低延迟体验经过大量商业游戏验证',
                ],
                'weaknesses': [
                    '有费用，按 CCU 计费，规模大时成本显著',
                    '国内访问延迟需实测（建议提前验证）',
                ],
            },
            'photon_quantum': {
                'name': 'Photon Quantum',
                'type': 'managed_service',
                'cost': 'paid',
                'best_for': ['rts', 'fighting', 'replay_required', 'deterministic_simulation'],
                'not_for': ['casual', 'small_team_budget', 'simple_coop'],
                'strengths': [
                    'ECS + 确定性物理，支持完美帧同步',
                    '录像/回放功能原生支持，适合格斗/RTS',
                    '技术上限最高的联机方案',
                ],
                'weaknesses': ['技术复杂度高，学习成本大', '费用较高，适合有预算的团队'],
            },
            'netcode_for_gameobjects': {
                'name': 'Netcode for GameObjects (NGO)',
                'type': 'unity_official',
                'cost': 'free',
                'best_for': ['simple_coop', 'small_scale_multiplayer', 'relay_lobby_integration'],
                'not_for': ['mmo', 'high_performance_competitive'],
                'strengths': [
                    'Unity 官方支持，与 Relay/Lobby 服务深度集成',
                    '上手门槛低，适合简单合作类游戏',
                ],
                'weaknesses': ['功能仍在持续完善，大规模场景有待验证'],
            },
            'nakama': {
                'name': 'Nakama',
                'type': 'open_source_backend',
                'cost': 'free（自托管）/ Heroic Labs 云服务',
                'best_for': ['social_game', 'live_ops', 'leaderboard', 'full_backend_needed'],
                'not_for': ['realtime_action_low_latency', 'no_backend_team'],
                'strengths': [
                    '完整游戏后端：排行榜/社交/存储/聊天/匹配/实时',
                    '开源可自托管，数据主权在自己',
                    '支持多语言客户端（Unity / Unreal / Web）',
                ],
                'weaknesses': ['需要后端运维能力', '实时对战延迟不及 Photon'],
            },
            'playfab': {
                'name': 'PlayFab (Microsoft Azure)',
                'type': 'baas',
                'cost': 'freemium',
                'best_for': ['live_ops', 'analytics_heavy', 'economy_system', 'azure_ecosystem'],
                'not_for': ['realtime_action', 'china_data_compliance_sensitive'],
                'strengths': [
                    '微软背书，服务稳定，免费额度较高',
                    '丰富运营功能：A/B测试、细分推送、虚拟经济、实验',
                ],
                'weaknesses': ['数据存储在微软云，中国合规需额外评估', '国内访问速度一般'],
            },
        }

    def _build_systems(self):
        self.systems = {
            'save': {
                'easy_save_3': {
                    'name': 'Easy Save 3 (ES3)',
                    'cost': '~$35',
                    'best_for': ['most_single_player', 'quick_integration'],
                    'strengths': ['Asset Store 最成熟存档方案', '支持加密/压缩/云同步', '极少代码即可使用'],
                    'weaknesses': ['大型复杂数据结构需提前规划序列化格式'],
                },
                'custom_json': {
                    'name': '自研 JSON 存档',
                    'cost': 'free',
                    'best_for': ['custom_format_required', 'no_third_party_dependency'],
                    'strengths': ['完全控制数据格式', '无第三方依赖风险'],
                    'weaknesses': ['需自行实现加密、版本迁移、错误恢复'],
                },
                'sqlite': {
                    'name': 'SQLite',
                    'cost': 'free',
                    'best_for': ['complex_data_queries', 'mmorpg', 'large_dataset'],
                    'strengths': ['关系型查询能力强', '适合大量结构化数据'],
                    'weaknesses': ['移动端性能需验证', '比 ES3 集成复杂'],
                },
            },
            'ui': {
                'ugui_tmp': {
                    'name': 'UGUI + TextMeshPro',
                    'cost': 'free',
                    'best_for': ['most_projects', 'mobile', 'all_platforms'],
                    'strengths': ['最成熟，生态最完整', 'Asset Store UI 资源全部支持', '教程和案例最多'],
                    'note': '当前几乎所有项目的首选',
                },
                'ui_toolkit': {
                    'name': 'UI Toolkit',
                    'cost': 'free',
                    'best_for': ['editor_tools', 'pc_complex_ui', 'future_proof'],
                    'strengths': ['CSS-like 样式系统，布局更强', 'Unity 长期战略方向', '复杂数据绑定更容易'],
                    'weaknesses': ['移动端性能还在追赶 UGUI', '资源生态不如 UGUI'],
                },
                'fairygui': {
                    'name': 'FairyGUI',
                    'cost': 'free',
                    'best_for': ['large_team', 'designer_friendly', 'chinese_market', 'complex_ui'],
                    'strengths': ['设计师可独立制作 UI 无需编程', '动态图集自动管理', '国内大厂广泛验证'],
                    'weaknesses': ['需要额外工作流培训，引入新工具链'],
                },
            },
            'audio': {
                'unity_audio': {
                    'name': 'Unity 原生 Audio',
                    'cost': 'free',
                    'best_for': ['simple_needs', 'short_timeline', 'prototype'],
                    'strengths': ['无需额外依赖，上手即用'],
                    'weaknesses': ['动态音频、空间音频设计能力弱'],
                },
                'fmod': {
                    'name': 'FMOD Studio',
                    'cost': '独立游戏免费 / 商业项目按收入授权',
                    'best_for': ['commercial_game', 'dynamic_audio', 'most_cases'],
                    'strengths': ['商业游戏标准音频中间件', '音效设计师可独立工作', '动态/自适应音频系统'],
                    'weaknesses': ['需要学习 FMOD Studio 工具（音频设计师通常已会）'],
                },
                'wwise': {
                    'name': 'Wwise (Audiokinetic)',
                    'cost': '独立游戏免费 / 商业项目按平台授权',
                    'best_for': ['console_game', 'aaa_level', 'dedicated_audio_engineer'],
                    'strengths': ['主机级项目标准，功能最强大', '与 Unreal 同等水准'],
                    'weaknesses': ['比 FMOD 更复杂，适合有专职音频工程师的团队'],
                },
            },
            'pathfinding': {
                'unity_navmesh': {
                    'name': 'Unity NavMesh',
                    'cost': 'free',
                    'best_for': ['simple_ai', 'static_terrain', 'small_ai_count'],
                    'strengths': ['内置无需安装', '满足基础寻路需求'],
                    'weaknesses': ['动态障碍物支持弱', '2D 支持有限'],
                },
                'astar': {
                    'name': 'A* Pathfinding Project',
                    'cost': 'free / Pro ~$100',
                    'best_for': ['complex_terrain', 'dynamic_obstacles', 'high_performance_ai', '2d_top_down'],
                    'strengths': ['动态障碍物完善支持', '2D/3D 均支持', '高性能可替代 NavMesh'],
                    'weaknesses': ['Pro 版有费用'],
                },
                'behavior_designer': {
                    'name': 'Behavior Designer',
                    'cost': '~$80',
                    'best_for': ['complex_ai', 'boss_ai', 'npc_behavior_tree'],
                    'strengths': ['可视化行为树编辑器', '配合任何寻路方案', '大量内置 Action 节点'],
                },
            },
            'hot_update': {
                'hybridclr': {
                    'name': 'HybridCLR（原华佗）',
                    'cost': 'free / Pro 版付费',
                    'best_for': ['china_market', 'mobile_live_ops', 'android_hot_fix'],
                    'strengths': ['C# 原生热更无需 Lua', '国内验证最充分', '成本最低'],
                    'note': '国内移动游戏热更新首选方案',
                },
                'xlua': {
                    'name': 'xLua',
                    'cost': 'free',
                    'best_for': ['existing_lua_team', 'tencent_ecosystem'],
                    'strengths': ['腾讯出品，稳定可靠', 'Lua 热更历史积累最长'],
                },
                'addressables': {
                    'name': 'Addressables（Unity 官方）',
                    'cost': 'free',
                    'best_for': ['asset_hot_update'],
                    'note': '资源热更必配，与代码热更方案（HybridCLR/xLua）配合使用',
                },
                'yooasset': {
                    'name': 'YooAsset',
                    'cost': 'free',
                    'best_for': ['advanced_asset_management', 'china_team'],
                    'strengths': ['Addressables 的成熟替代方案', '分包/热更功能更完整', '国内团队广泛使用'],
                },
            },
            'input': {
                'new_input_system': {
                    'name': 'Unity New Input System',
                    'cost': 'free',
                    'best_for': ['most_projects', 'cross_platform'],
                    'strengths': ['官方支持，多平台统一', '手柄/键鼠/触屏统一处理', '动作映射系统灵活'],
                    'note': '新项目标准选择',
                },
                'rewired': {
                    'name': 'Rewired',
                    'cost': '~$50',
                    'best_for': ['console_game', 'complex_input_remapping', 'gamepad_heavy'],
                    'strengths': ['最完整的手柄设备支持', '自定义键位映射系统最强'],
                    'note': '主机游戏或需要复杂键位映射时使用',
                },
            },
            'camera': {
                'cinemachine': {
                    'name': 'Cinemachine',
                    'cost': 'free',
                    'best_for': ['all'],
                    'strengths': ['Unity 官方，功能全面', '与 Timeline 深度集成', '几乎所有项目的标准选择'],
                    'note': '推荐所有项目使用，不建议手动写相机控制器',
                },
            },
            'dependency_injection': {
                'scriptable_object_arch': {
                    'name': 'ScriptableObject 架构',
                    'cost': 'free',
                    'best_for': ['solo', 'small_team', 'small_medium_project'],
                    'strengths': ['无框架依赖，原生 Unity', 'Ryan Hipple 最佳实践', '设计师可直接编辑数据'],
                    'note': '小中型项目轻量首选',
                },
                'vcontainer': {
                    'name': 'VContainer',
                    'cost': 'free',
                    'best_for': ['medium_team', 'large_team', 'complex_project'],
                    'strengths': ['高性能 DI 容器，专为 Unity 设计', '比 Zenject 更轻量', '单元测试友好'],
                    'note': '中大型项目推荐',
                },
                'zenject': {
                    'name': 'Zenject (Extenject)',
                    'cost': 'free',
                    'best_for': ['large_project', 'experienced_team'],
                    'strengths': ['功能最完整的 Unity DI 框架', '大量生产案例'],
                    'weaknesses': ['比 VContainer 更重，学习成本更高'],
                },
            },
        }

    def _build_asset_packs(self):
        self.asset_packs = {
            'synty_studios': {
                'name': 'Synty Studios',
                'url': 'https://syntystore.com',
                'style': 'low_poly_stylized',
                'price_range': '$20–70/pack',
                'strengths': [
                    '最成熟的低多边形风格化系列，几十个场景主题包',
                    '风格极度统一，不同包之间无缝搭配',
                    '频繁更新，URP/HDRP 均支持，DrawCall 极友好',
                    '适合中小型团队快速建立高质量画面',
                ],
                'best_for': ['stylized_rpg', 'casual', 'mobile', 'prototype', 'quick_visual'],
                'caution': '⚠️ 市场辨识度高，同款游戏多，需在角色/UI/特效上做差异化',
            },
            'infinity_pbr': {
                'name': 'Infinity PBR',
                'url': 'https://infinitypbr.gitbook.io',
                'style': 'realistic_pbr',
                'price_range': '$15–60/pack',
                'strengths': [
                    '最全面的 PBR 角色/怪物库（500+ 角色）',
                    '高质量动画包含，含变形/死亡/攻击动画',
                    '模块化设计，持续更新维护',
                ],
                'best_for': ['rpg_realistic', 'survival', 'action', 'horror'],
                'caution': '写实风格，文件体积较大，移动端需缩减 LOD',
            },
            'nature_manufacture': {
                'name': 'NatureManufacture',
                'style': 'realistic_nature',
                'price_range': '$30–100/pack',
                'strengths': [
                    '高质量写实自然环境（森林/草地/水体/岩石）',
                    '含 SpeedTree 植被，LOD 体系完善',
                    'URP/HDRP 均支持',
                ],
                'best_for': ['open_world', 'survival', 'realistic_rpg', 'exploration'],
                'caution': '面数较高，移动端必须使用降质量版本并验证性能',
            },
            'seaside_studio': {
                'name': 'Seaside Studio',
                'style': 'environment_packs',
                'strengths': [
                    '专注高质量环境/场景资源',
                    '适合自然、建筑、沿海类场景',
                ],
                'best_for': ['ocean_theme', 'coastal', 'island', 'environment_heavy'],
                'evaluation_checklist': [
                    '确认 URP/HDRP 兼容性（查看 Asset Store 描述页面）',
                    '验证目标平台面数预算（移动端严格限制）',
                    '确认与整体美术风格（写实/风格化）的匹配度',
                    '检查授权条款是否允许商业发布',
                    '查看最近一次更新时间，确认与当前 Unity LTS 兼容',
                ],
                'note': '⚠️ 使用前请完成上述评估清单，避免引入后期难以替换',
            },
            'hovl_studio': {
                'name': 'Hovl Studio VFX 系列',
                'style': 'vfx_shaders',
                'price_range': '$20–60/pack',
                'strengths': [
                    '高质量魔法/技能特效，风格系列统一',
                    'URP 支持完善，Shader Graph 制作',
                    '风格化和写实两种路线均有产品',
                ],
                'best_for': ['rpg', 'action', 'action_rpg', 'skill_based'],
                'caution': '特效资产，不含游戏逻辑，需配合动画事件触发',
            },
            'gaia_procedural_worlds': {
                'name': 'Gaia / Procedural Worlds',
                'style': 'terrain_generation',
                'price_range': '$40–150',
                'strengths': [
                    '最强的 Unity 地形生成工具',
                    '一键生成高质量地形，含植被/水体/天空盒',
                    '与多种资源包生态兼容',
                ],
                'best_for': ['open_world', 'exploration', 'rpg', 'survival'],
                'note': '开放世界类游戏地形工具首选',
            },
        }

    # ─────────────────────────────────────────────────────────────
    # 主分析入口
    # ─────────────────────────────────────────────────────────────

    def analyze(self, game_profile: Dict) -> Dict:
        """
        根据游戏档案生成完整架构方案

        game_profile 结构:
        {
            'game_name':         str,   # 游戏名称
            'description':       str,   # 游戏描述（自由文本）
            'game_type':         str,   # 类型: rpg/fps/platformer/casual/…
            'perspective':       str,   # 视角: 3d_tps/3d_fps/2d/top_down
            'target_platforms':  list,  # ['mobile','pc','console','webgl']
            'team_size':         str,   # solo/small/medium/large
            'timeline_months':   int,   # 预计开发周期（月）
            'art_style':         str,   # stylized/realistic/cartoon/pixel
            'features':          list,  # ['multiplayer','narrative','iap',…]
            'has_multiplayer':   bool,
            'has_narrative':     bool,
            'has_iap':           bool,
            'has_hot_update':    bool,
            'budget_level':      str,   # budget/normal/premium
        }
        """
        profile = self._normalize_profile(game_profile)

        render_pipeline  = self._select_render_pipeline(profile)
        main_framework   = self._select_main_framework(profile)
        network          = self._select_network(profile)
        systems          = self._select_systems(profile, main_framework)
        arch_pattern     = self._select_architecture_pattern(profile)
        asset_recs       = self._recommend_assets(profile)
        conflicts        = self._check_conflicts(main_framework, network, systems, profile)
        risks            = self._generate_risks(profile, main_framework, network, systems)
        roadmap          = self._generate_roadmap(profile, main_framework, systems)
        alternatives     = self._generate_alternatives(profile, main_framework, network)
        perf_budget      = self._generate_performance_budget(profile)

        return {
            'status': 'success',
            'generated_at': datetime.now().isoformat(),
            'architect_version': self.version,
            'game_understanding': {
                'name': profile.get('game_name', '未命名'),
                'summary': self._summarize_game(profile),
                'detected_type': profile.get('game_type'),
                'complexity': self._assess_complexity(profile),
            },
            'tech_stack': {
                'render_pipeline': render_pipeline,
                'main_framework':  main_framework,
                'architecture_pattern': arch_pattern,
                'network': network,
            },
            'systems': systems,
            'asset_recommendations': asset_recs,
            'conflicts': conflicts,
            'risks': risks,
            'roadmap': roadmap,
            'alternatives': alternatives,
            'performance_budget': perf_budget,
        }

    # ─────────────────────────────────────────────────────────────
    # 档案标准化
    # ─────────────────────────────────────────────────────────────

    def _normalize_profile(self, raw: Dict) -> Dict:
        profile = dict(raw)
        profile.setdefault('game_name', '未命名游戏')
        profile.setdefault('game_type', 'rpg')
        profile.setdefault('perspective', '3d_tps')
        profile.setdefault('target_platforms', ['pc'])
        profile.setdefault('team_size', 'small')
        profile.setdefault('timeline_months', 12)
        profile.setdefault('art_style', 'stylized')
        profile.setdefault('features', [])
        profile.setdefault('has_multiplayer', False)
        profile.setdefault('has_narrative', False)
        profile.setdefault('has_iap', False)
        profile.setdefault('has_hot_update', False)
        profile.setdefault('budget_level', 'normal')
        profile.setdefault('description', '')

        platforms = [p.lower() for p in profile['target_platforms']]
        profile['is_mobile']      = any(p in ['android', 'ios', 'mobile'] for p in platforms)
        profile['is_pc']          = any(p in ['pc', 'windows', 'mac', 'linux', 'steam'] for p in platforms)
        profile['is_console']     = any(p in ['console', 'ps5', 'xbox', 'switch', 'nintendo'] for p in platforms)
        profile['is_webgl']       = 'webgl' in platforms
        profile['is_mobile_only'] = profile['is_mobile'] and not profile['is_pc'] and not profile['is_console']

        size_map = {'solo': 1, 'small': 3, 'medium': 10, 'large': 30}
        profile['team_size_num'] = size_map.get(profile['team_size'], 3)

        # 功能标记方便下游使用
        features = [f.lower() for f in profile.get('features', [])]
        profile['has_multiplayer']  = profile.get('has_multiplayer') or 'multiplayer' in features
        profile['has_narrative']    = profile.get('has_narrative')    or 'narrative' in features or 'dialogue' in features
        profile['has_iap']          = profile.get('has_iap')          or 'iap' in features
        profile['has_hot_update']   = profile.get('has_hot_update')   or 'hot_update' in features

        return profile

    # ─────────────────────────────────────────────────────────────
    # 渲染管线选择
    # ─────────────────────────────────────────────────────────────

    def _select_render_pipeline(self, profile: Dict) -> Dict:
        if profile['is_mobile'] or profile['is_webgl']:
            pipeline = 'urp'
            reason = '移动端 / WebGL 项目，URP 是唯一正确选择，跨平台性能最优，DrawCall 管理更高效'
        elif profile['art_style'] in ['photorealistic', 'realistic'] and profile['is_pc'] and not profile['is_mobile']:
            pipeline = 'hdrp'
            reason = '写实画风 + PC/主机专属，HDRP 提供电影级光照质量（体积光/SSGI/光线追踪）'
        else:
            pipeline = 'urp'
            reason = '风格化 / 跨平台项目，URP 是最广泛支持的选择，Asset Store 生态最完整'

        rp = self.render_pipelines[pipeline]
        return {
            'choice': pipeline,
            'display_name': rp['name'],
            'reason': reason,
            'key_strengths': rp.get('strengths', [])[:3],
            'warning': rp.get('note', ''),
        }

    # ─────────────────────────────────────────────────────────────
    # 主框架选择
    # ─────────────────────────────────────────────────────────────

    def _select_main_framework(self, profile: Dict) -> Dict:
        game_type = profile.get('game_type', 'rpg')
        has_narrative = profile.get('has_narrative', False)

        if game_type in ['2d_platformer', 'platformer', 'metroidvania', 'run_and_gun']:
            fw_key = 'corgi_engine'
            reason = '2D 横板 / 银河恶魔城类型，Corgi Engine 专为此类游戏设计，手感精准，久经商业验证'

        elif game_type in ['top_down', 'top_down_rpg', 'top_down_shooter', 'twin_stick', 'roguelike']:
            fw_key = 'top_down_engine'
            reason = '俯视角类型，Top Down Engine 专项支持，含完整 AI / 武器 / 关卡管理系统'

        elif game_type in ['fps', 'tps', 'survival', 'battle_royale']:
            fw_key = 'opsive_ucc'
            reason = 'FPS/TPS 类型，Opsive UCC 拥有最强的第一/三人称角色控制器，第一/三人称无缝切换，武器系统完整'

        elif game_type in ['rpg', 'action_rpg', 'action_adventure', 'open_world', 'narrative'] or has_narrative:
            fw_key = 'game_creator_2'
            reason = 'RPG / 动作冒险 / 叙事类型，Game Creator 2 的模块生态（背包/任务/对话/属性）覆盖此类游戏 90% 的基础需求，显著缩短开发周期'

        elif game_type in ['fighting', 'racing', 'sports']:
            fw_key = 'scratch'
            reason = '此类游戏核心玩法高度定制（物理/帧数据/碰撞），第三方框架的角色控制器会成为约束，自研更合适'

        elif game_type in ['casual', 'hyper_casual', 'puzzle', 'match3', 'idle', 'card', 'simulation']:
            fw_key = 'scratch'
            reason = '休闲/益智类游戏逻辑相对简单，不需要重量级框架，自研保持轻量，避免不必要的依赖'

        else:
            fw_key = 'game_creator_2'
            reason = '游戏含多种系统需求，Game Creator 2 的模块化生态能快速覆盖大部分需求，建议原型阶段验证是否满足核心玩法'

        fw = self.frameworks[fw_key]
        result = {
            'choice': fw_key,
            'display_name': fw['name'],
            'publisher': fw.get('publisher', ''),
            'reason': reason,
            'strengths': fw['core_strengths'][:3],
            'weaknesses': fw['weaknesses'][:2],
            'cost_estimate': fw['cost_estimate'],
            'url': fw.get('url', ''),
        }

        if fw_key == 'game_creator_2':
            result['recommended_modules'] = self._recommend_gc2_modules(profile)

        # 所有项目都建议搭配 Feel
        if fw_key in ['corgi_engine', 'top_down_engine']:
            result['companion'] = {
                'name': 'Feel (More Mountains)',
                'reason': '与 Corgi/Top Down Engine 同厂，深度集成，大幅提升游戏手感和 Juice 效果',
                'cost': '~$35（同厂购买有折扣）',
            }

        return result

    def _recommend_gc2_modules(self, profile: Dict) -> List[Dict]:
        modules = [{'name': 'Core', 'reason': '必需基础模块（角色/摄像机/Action 系统）', 'priority': 'required'}]
        game_type = profile.get('game_type', '')
        features  = [f.lower() for f in profile.get('features', [])]

        if profile.get('has_narrative') or game_type in ['narrative', 'rpg', 'action_adventure']:
            modules.append({'name': 'Dialogue', 'reason': '对话树、分支叙事、条件对话', 'priority': 'recommended'})

        if 'inventory' in features or game_type in ['rpg', 'action_rpg', 'survival']:
            modules.append({'name': 'Inventory', 'reason': '背包、装备、掉落系统', 'priority': 'recommended'})

        if 'quest' in features or game_type in ['rpg', 'action_rpg', 'open_world']:
            modules.append({'name': 'Quests', 'reason': '任务、目标、奖励系统', 'priority': 'recommended'})

        if 'combat' in features or game_type in ['rpg', 'action_rpg', 'action_adventure']:
            modules.append({'name': 'Stats', 'reason': '属性、战斗公式、Buff/Debuff', 'priority': 'recommended'})
            modules.append({'name': 'Melee', 'reason': '近战战斗系统', 'priority': 'optional'})

        if 'shooting' in features or game_type in ['tps']:
            modules.append({'name': 'Shooter', 'reason': '射击、弹道、武器切换', 'priority': 'optional'})

        if 'mount' in features or 'horses' in features:
            modules.append({'name': 'Horses', 'reason': '骑乘系统', 'priority': 'optional'})

        return modules

    # ─────────────────────────────────────────────────────────────
    # 网络框架选择
    # ─────────────────────────────────────────────────────────────

    def _select_network(self, profile: Dict) -> Dict:
        if not profile.get('has_multiplayer', False):
            return {
                'choice': 'none',
                'display_name': '单机（无需网络框架）',
                'reason': '游戏不包含多人联机功能',
                'note': '若后续需要增加多人功能，推荐 FishNet 作为首选接入方案',
            }

        game_type = profile.get('game_type', '')
        features  = profile.get('features', [])
        team_size = profile.get('team_size', 'small')

        if game_type in ['fps', 'battle_royale', 'competitive', 'sports']:
            choice = 'photon_fusion'
            reason = '竞技 / FPS 类型需要 Rollback Netcode 保证低延迟同步，Photon Fusion 是行业验证方案'

        elif game_type in ['rts', 'fighting'] and team_size in ['medium', 'large']:
            choice = 'photon_quantum'
            reason = 'RTS / 格斗类需要确定性物理保证完美帧同步，支持录像回放，Photon Quantum 是此场景唯一成熟选择'

        elif 'social' in features or 'leaderboard' in features or 'live_ops' in features:
            choice = 'nakama'
            reason = '需要完整后台服务（排行榜/社交/聊天/存储），Nakama 提供全栈游戏后端，可自托管'

        else:
            choice = 'fishnet'
            reason = '合作类多人游戏，FishNet 是当前增长最快的开源框架，功能完整、社区活跃、完全免费'

        fw = self.network_frameworks[choice]
        return {
            'choice': choice,
            'display_name': fw['name'],
            'reason': reason,
            'cost': fw.get('cost', ''),
            'strengths': fw.get('strengths', [])[:3],
        }

    # ─────────────────────────────────────────────────────────────
    # 各系统选择
    # ─────────────────────────────────────────────────────────────

    def _select_systems(self, profile: Dict, main_framework: Dict) -> Dict:
        is_mobile   = profile.get('is_mobile', False)
        is_console  = profile.get('is_console', False)
        team_size   = profile.get('team_size', 'small')
        timeline    = profile.get('timeline_months', 12)
        game_type   = profile.get('game_type', '')
        features    = profile.get('features', [])

        # ── 存档 ──
        save_choice  = 'easy_save_3'
        save_reason  = 'Asset Store 最成熟存档方案，极少代码即可使用，支持加密/压缩/云同步'

        # ── UI ──
        ui_choice    = 'ugui_tmp'
        ui_reason    = 'UGUI + TextMeshPro 生态最完整，Asset Store UI 资源全部支持，教程最多'

        # ── 音频 ──
        if timeline < 6:
            audio_choice = 'unity_audio'
            audio_reason = '短周期项目先用 Unity 原生 Audio 节省集成时间，后期按需迁移至 FMOD'
        else:
            audio_choice = 'fmod'
            audio_reason = '商业游戏标准音频中间件，音效设计师可独立工作，动态/自适应音频能力强'

        # ── 寻路/AI ──
        if 'complex_ai' in features or game_type in ['rts', 'open_world', 'strategy']:
            ai_choice  = 'astar'
            ai_reason  = '复杂地形 / 动态障碍物场景，A* Pathfinding Project 性能和灵活性远超 NavMesh'
        elif game_type in ['rpg', 'action_rpg', 'open_world'] and team_size in ['medium', 'large']:
            ai_choice  = 'behavior_designer'
            ai_reason  = '中大型团队 + 复杂 NPC 行为，可视化行为树大幅降低 AI 维护难度'
        else:
            ai_choice  = 'unity_navmesh'
            ai_reason  = '基础 AI 需求，Unity 内置 NavMesh 完全满足，无需额外依赖'

        # ── 输入 ──
        if is_console:
            input_choice  = 'rewired'
            input_reason  = '主机平台需要 Rewired 提供最完整的手柄支持与自定义键位映射系统'
        else:
            input_choice  = 'new_input_system'
            input_reason  = 'Unity 新输入系统，多平台统一，手柄/键鼠/触屏统一处理'

        # ── 架构模式/DI ──
        if team_size in ['medium', 'large']:
            di_choice  = 'vcontainer'
            di_reason  = '中大型团队推荐 VContainer 依赖注入，提升代码可测试性和系统间解耦'
        else:
            di_choice  = 'scriptable_object_arch'
            di_reason  = '小团队 / 独立开发，ScriptableObject 架构无框架依赖，学习成本低，设计师友好'

        # ── 热更新 ──
        hot_update = None
        if profile.get('has_hot_update', False):
            hot_update = {
                'choice': 'hybridclr',
                'display_name': 'HybridCLR + YooAsset',
                'reason': 'C# 原生热更，国内验证最充分，YooAsset 负责资源分包与热更版本管理',
                'warning': '⚠️ iOS 不得热更核心玩法逻辑（App Store 审核政策），热更范围限定在 UI/文本/数值配置',
            }

        return {
            'save': {
                'choice': save_choice,
                'display_name': self.systems['save'][save_choice]['name'],
                'reason': save_reason,
                'cost': self.systems['save'][save_choice].get('cost', ''),
            },
            'ui': {
                'choice': ui_choice,
                'display_name': self.systems['ui'][ui_choice]['name'],
                'reason': ui_reason,
            },
            'audio': {
                'choice': audio_choice,
                'display_name': self.systems['audio'][audio_choice]['name'],
                'reason': audio_reason,
                'cost': self.systems['audio'][audio_choice].get('cost', ''),
            },
            'pathfinding': {
                'choice': ai_choice,
                'display_name': self.systems['pathfinding'][ai_choice]['name'],
                'reason': ai_reason,
            },
            'camera': {
                'choice': 'cinemachine',
                'display_name': 'Cinemachine',
                'reason': 'Unity 官方，功能全面，与 Timeline 深度集成，几乎所有项目的标准选择',
            },
            'input': {
                'choice': input_choice,
                'display_name': self.systems['input'][input_choice]['name'],
                'reason': input_reason,
            },
            'architecture': {
                'choice': di_choice,
                'display_name': self.systems['dependency_injection'][di_choice]['name'],
                'reason': di_reason,
            },
            'hot_update': hot_update,
        }

    # ─────────────────────────────────────────────────────────────
    # 架构模式选择
    # ─────────────────────────────────────────────────────────────

    def _select_architecture_pattern(self, profile: Dict) -> Dict:
        team_size = profile.get('team_size', 'small')

        if team_size in ['medium', 'large']:
            pattern = 'di_vcontainer'
            desc    = 'VContainer 依赖注入'
            reason  = '中大型团队协作频繁，依赖注入确保系统间解耦，便于单元测试和重构'
            event_sys = 'MessagePipe（高性能事件总线）'
        else:
            pattern = 'scriptable_object'
            desc    = 'ScriptableObject 驱动架构'
            reason  = '小团队 / 独立开发，原生 Unity 方案，无需学习额外框架，设计师可直接编辑数据'
            event_sys = 'ScriptableObject Events（轻量事件系统）'

        return {
            'choice':        pattern,
            'display_name':  desc,
            'reason':        reason,
            'event_system':  event_sys,
        }

    # ─────────────────────────────────────────────────────────────
    # 资源包推荐
    # ─────────────────────────────────────────────────────────────

    def _recommend_assets(self, profile: Dict) -> List[Dict]:
        recs      = []
        art_style = profile.get('art_style', 'stylized')
        game_type = profile.get('game_type', '')
        desc      = profile.get('description', '').lower()
        features  = profile.get('features', [])

        # Feel 几乎适合所有游戏
        recs.append({
            'name':     'Feel (More Mountains)',
            'category': '游戏手感 / Juice',
            'priority': 'recommended',
            'reason':   '屏幕震动、相机抖动、粒子爆发、慢动作——显著提升游戏体验，适合几乎所有游戏',
            'cost':     '~$35',
        })

        # 美术风格资产
        if art_style in ['stylized', 'cartoon', 'low_poly']:
            recs.append({
                'name':     'Synty Studios 系列',
                'category': '场景 / 角色美术',
                'priority': 'recommended',
                'reason':   '最成熟的低多边形风格化资源，风格高度统一，DrawCall 极友好，移动端性能优秀',
                'cost':     '$20–70/pack',
                'caution':  '⚠️ 市场辨识度高，需在角色/UI/特效上做差异化',
            })
        elif art_style in ['realistic', 'photorealistic']:
            recs.append({
                'name':     'Infinity PBR 角色库',
                'category': '角色 / 怪物',
                'priority': 'optional',
                'reason':   '500+ 高质量 PBR 角色/怪物，含动画，节省大量角色制作时间',
                'cost':     '$15–60/pack',
            })
            recs.append({
                'name':     'NatureManufacture 自然环境',
                'category': '场景美术',
                'priority': 'optional',
                'reason':   '高质量写实自然场景，含 SpeedTree 植被，LOD 体系完善',
                'cost':     '$30–100/pack',
                'caution':  '移动端需使用降质量版本并验证性能预算',
            })

        # 开放世界地形
        if game_type in ['open_world', 'rpg', 'survival', 'exploration']:
            recs.append({
                'name':     'Gaia / Procedural Worlds',
                'category': '地形生成',
                'priority': 'recommended',
                'reason':   '开放世界必备工具，一键生成高质量地形（含植被/水体/天空），大幅节省场景搭建时间',
                'cost':     '$40–150',
            })

        # 技能特效
        if game_type in ['rpg', 'action_rpg', 'action_adventure', 'action']:
            recs.append({
                'name':     'Hovl Studio VFX 系列',
                'category': '技能特效',
                'priority': 'optional',
                'reason':   '高质量魔法/技能特效，风格系列统一，URP 支持完善',
                'cost':     '$20–60/pack',
            })

        # Seaside Studio 仅在相关场景推荐
        ocean_keywords = ['ocean', 'sea', 'coast', 'island', 'naval', '海洋', '海岛', '航海', '海岸']
        if any(kw in desc for kw in ocean_keywords) or game_type in ['exploration']:
            recs.append({
                'name':     'Seaside Studio 系列',
                'category': '海洋 / 海岸场景',
                'priority': 'optional',
                'reason':   '海洋/岛屿/沿海题材的专项环境资产',
                'cost':     '根据具体产品而定',
                'caution':  '⚠️ 使用前需完成: URP/HDRP 兼容性验证 + 目标平台面数预算确认 + 整体美术风格匹配度评估',
            })

        return recs

    # ─────────────────────────────────────────────────────────────
    # 冲突检查
    # ─────────────────────────────────────────────────────────────

    def _check_conflicts(self, main_framework: Dict, network: Dict, systems: Dict, profile: Dict) -> List[Dict]:
        conflicts = []
        fw_key = main_framework.get('choice', '')

        # GC2 + Opsive UCC 角色控制器冲突
        if fw_key == 'game_creator_2' and systems.get('pathfinding', {}).get('choice') == 'opsive_ucc':
            conflicts.append({
                'severity':    'critical',
                'title':       'Game Creator 2 与 Opsive UCC 角色控制器冲突',
                'description': '两套框架都有独立的角色控制器，不可同时驱动同一个角色',
                'solution':    '选择其中一套作为角色控制层：RPG/冒险 → GC2；FPS/TPS → Opsive UCC',
            })

        # HDRP + 移动端冲突（理论上在渲染管线选择时已避免，双重保险）
        rp = profile.get('_render_pipeline', '')
        if 'hdrp' in rp and profile.get('is_mobile', False):
            conflicts.append({
                'severity':    'critical',
                'title':       'HDRP 不支持移动端',
                'description': 'HDRP 渲染管线不支持 Android / iOS 平台',
                'solution':    '改用 URP，移动端没有其他选项',
            })

        # 热更新 iOS 风险
        if systems.get('hot_update') and profile.get('is_mobile', False):
            conflicts.append({
                'severity':    'medium',
                'title':       'iOS 热更新政策风险',
                'description': 'App Store 禁止热更核心游戏逻辑，违规会导致被拒或下架',
                'solution':    '热更范围严格限定在 UI / 文本 / 数值配置，不热更核心玩法代码；Android 无此限制',
            })

        return conflicts

    # ─────────────────────────────────────────────────────────────
    # 风险清单
    # ─────────────────────────────────────────────────────────────

    def _generate_risks(self, profile: Dict, main_framework: Dict, network: Dict, systems: Dict) -> List[Dict]:
        risks  = []
        fw_key = main_framework.get('choice', '')

        if fw_key == 'game_creator_2':
            risks.append({
                'level':      'medium',
                'area':       'GC2 框架约束',
                'risk':       '角色控制器和核心玩法手感难以深度定制',
                'mitigation': '在原型阶段（第1个月）充分验证 GC2 角色控制器是否满足手感需求，确认后再开始全面开发',
            })
            risks.append({
                'level':      'low',
                'area':       '许可费用',
                'risk':       'GC2 模块按需购买，叠加后成本可能超出预期',
                'mitigation': '提前列出所需模块清单并核算总费用，优先采购 Core + 最关键的 2–3 个模块',
            })

        if fw_key == 'scratch':
            risks.append({
                'level':      'high',
                'area':       '开发周期',
                'risk':       '自研基础系统开发量大，极易低估工作量',
                'mitigation': '细化 Milestone 计划，基础系统阶段保留 20–30% Buffer；优先实现核心玩法，其余系统迭代完善',
            })

        if profile.get('has_multiplayer'):
            risks.append({
                'level':      'high',
                'area':       '网络同步',
                'risk':       '多人同步逻辑复杂度远超单机（延迟补偿/状态预测/作弊防护）',
                'mitigation': '网络架构在第 1 个月单独做原型验证；选择服务端权威模型；引入 Lag Compensation；早期测试真实网络环境',
            })

        if profile.get('is_mobile'):
            risks.append({
                'level':      'medium',
                'area':       '移动端性能',
                'risk':       '移动设备性能差异巨大，中低端机型是最大挑战',
                'mitigation': '第一个月建立性能预算（DrawCall / 面数 / 内存），持续在中低端真机上用 Unity Profiler 验证',
            })

        if profile.get('has_hot_update'):
            risks.append({
                'level':      'medium',
                'area':       '热更新合规',
                'risk':       'iOS App Store 审核可能拒绝含热更新机制的 App',
                'mitigation': '热更范围限定在资源/配置，保留完整版本发布能力；Android 端无此风险',
            })

        if profile.get('timeline_months', 12) < 6:
            risks.append({
                'level':      'high',
                'area':       '开发周期',
                'risk':       '6 个月以内的游戏开发周期极为紧张，范围蔓延是最大风险',
                'mitigation': '严格 MVP 范围控制，优先核心玩法循环，辅助系统后续迭代；禁止在原型验证前引入复杂第三方框架',
            })

        return risks

    # ─────────────────────────────────────────────────────────────
    # 实施路线图
    # ─────────────────────────────────────────────────────────────

    def _generate_roadmap(self, profile: Dict, main_framework: Dict, systems: Dict) -> List[Dict]:
        fw_name   = main_framework.get('display_name', '框架')
        timeline  = profile.get('timeline_months', 12)

        phase1_weeks = '2–3 周'
        phase2_weeks = '4–6 周'
        phase3_weeks = f'{max(4, timeline * 4 - 10)} 周'
        phase4_weeks = '2–4 周'
        phase5_weeks = '2–3 周'

        return [
            {
                'phase':    1,
                'name':     '环境搭建 & 核心原型',
                'duration': phase1_weeks,
                'priority': 'critical',
                'tasks': [
                    '创建 Unity 项目，选定 LTS 版本（推荐 Unity 6 LTS）',
                    '配置渲染管线（URP/HDRP），导入基础包',
                    f'引入 {fw_name} 并完成基础配置',
                    '实现最小可玩原型，验证核心玩法手感（重要：框架适配性在此阶段确认）',
                    '搭建 Git 版本控制工作流，配置 Git LFS 管理大文件',
                    '制定性能预算（DrawCall / 面数 / 内存目标）',
                ],
            },
            {
                'phase':    2,
                'name':     '核心系统搭建',
                'duration': phase2_weeks,
                'priority': 'high',
                'tasks': [
                    '角色控制、动画状态机、基础移动手感',
                    '摄像机系统（Cinemachine）',
                    '存档系统（Easy Save 3）',
                    'UI 基础框架（UGUI + TextMeshPro）',
                    '输入系统（New Input System / Rewired）',
                    'Addressables / YooAsset 资源管理与分包流程',
                    '场景加载管理（Additive Loading 避免卡顿）',
                ],
            },
            {
                'phase':    3,
                'name':     '游戏系统完善',
                'duration': phase3_weeks,
                'priority': 'high',
                'tasks': [
                    '实现游戏主要机制（战斗/关卡/经济/叙事等）',
                    '集成音频系统（FMOD / Unity Audio）',
                    '实现 AI 行为（NavMesh / A* / Behavior Designer）',
                    '美术资产导入与性能优化（LOD / Atlas / 压缩格式）',
                    '多人联机功能开发（如有，先做网络原型）',
                    '内购系统与广告 SDK 接入（如有）',
                ],
            },
            {
                'phase':    4,
                'name':     '性能优化 & 体验打磨',
                'duration': phase4_weeks,
                'priority': 'medium',
                'tasks': [
                    'Unity Profiler 全面分析：DrawCall / GC / 帧时间',
                    '中低端目标设备真机测试（必须，不可省略）',
                    '集成 Feel 插件提升游戏手感和 Juice 效果',
                    '音效和视觉反馈细节打磨',
                    'Crash 监控接入（Firebase Crashlytics / Bugsnag）',
                    '本地化文本处理（如有多语言需求）',
                ],
            },
            {
                'phase':    5,
                'name':     '合规 & 上线准备',
                'duration': phase5_weeks,
                'priority': 'medium',
                'tasks': [
                    '接入合规系统（隐私政策 / GDPR / COPPA / 中国防沉迷）',
                    '构建自动化流程（Build Pipeline / CI-CD）',
                    'App Store & Google Play 商店资料准备',
                    '提交审核，响应审核反馈',
                    '运营系统就绪（数据分析 / 热更新 / 客服通道）',
                ],
            },
        ]

    # ─────────────────────────────────────────────────────────────
    # 备选方案
    # ─────────────────────────────────────────────────────────────

    def _generate_alternatives(self, profile: Dict, main_framework: Dict, network: Dict) -> List[Dict]:
        alts   = []
        fw_key = main_framework.get('choice', '')

        if fw_key == 'game_creator_2':
            alts.append({
                'scenario':  '如果 GC2 角色控制器无法满足核心玩法手感需求',
                'solution':  '改用 Opsive UCC 负责角色控制，GC2 模块（Inventory/Quest/Dialogue）通过自定义接口桥接',
                'tradeoff':  '开发成本增加约 1–2 周，但获得更强大的角色控制能力',
            })
            alts.append({
                'scenario':  '如果预算不足以购买所有所需 GC2 模块',
                'solution':  '仅购买 Core + 最关键 1–2 个模块，其余系统自研；或完全改为自研',
                'tradeoff':  '节省版权费用，但增加 4–8 周开发时间',
            })

        if fw_key == 'corgi_engine':
            alts.append({
                'scenario':  '如果需要在 2D 横板基础上加入大量 RPG 元素（背包/对话/任务）',
                'solution':  '改用 Game Creator 2（含 Corgi 兼容层），或在 Corgi Engine 基础上自研 RPG 层',
                'tradeoff':  '选 GC2 需要迁移角色控制器；自研更灵活但周期更长',
            })

        if network.get('choice') == 'fishnet':
            alts.append({
                'scenario':  '后期如果需要支持强竞技对战功能',
                'solution':  '迁移至 Photon Fusion（Rollback Netcode），FishNet 架构迁移成本可控',
                'tradeoff':  '产生 CCU 费用，但获得更好的低延迟同步体验',
            })

        if network.get('choice') == 'photon_fusion':
            alts.append({
                'scenario':  '如果国内用户延迟测试不达标或预算不允许',
                'solution':  '改用 FishNet + 自建服务器（或腾讯/阿里云游戏服务器）',
                'tradeoff':  '需要运维能力，但数据主权在自己，国内延迟更可控',
            })

        return alts

    # ─────────────────────────────────────────────────────────────
    # 性能预算
    # ─────────────────────────────────────────────────────────────

    def _generate_performance_budget(self, profile: Dict) -> Dict:
        if profile.get('is_mobile_only'):
            return {
                'target':        '移动端（兼顾中低端设备）',
                'draw_calls':    '< 100（推荐 < 80）',
                'triangles':     '< 500,000 三角面/帧',
                'texture_size':  '最大 1024×1024，UI 推荐 512×512',
                'memory_budget': '< 512 MB（推荐 < 350 MB）',
                'fps_target':    '30 FPS 基准 / 高端设备 60 FPS',
                'key_rules': [
                    '使用 Sprite Atlas 合并 UI 贴图，减少 DrawCall',
                    'LOD 系统必须启用（LOD0 / LOD1 / LOD2 / Cull）',
                    '启用 GPU Instancing 和 Static Batching',
                    '使用 Object Pool 避免频繁 GC 分配',
                    '纹理格式：Android → ETC2，iOS → ASTC',
                ],
            }
        elif profile.get('is_pc') and not profile.get('is_mobile'):
            return {
                'target':        'PC 平台',
                'draw_calls':    '< 1000（视场景复杂度）',
                'triangles':     '视场景复杂度，无严格限制',
                'texture_size':  '最大 4K，一般 2K',
                'memory_budget': '< 4 GB',
                'fps_target':    '60 FPS（推荐支持 120 FPS 解锁）',
                'key_rules': [
                    '关注 CPU 瓶颈（Update 函数过多调用、大量 GetComponent）',
                    '启用 Async Loading 避免场景加载卡顿',
                    '开启 GPU Skinning 减轻 CPU 蒙皮压力',
                ],
            }
        else:
            return {
                'target':        '多平台（以移动端为最低标准）',
                'draw_calls':    '< 150',
                'triangles':     '< 800,000 三角面/帧',
                'texture_size':  'PC: 2048×2048 / 移动端: 1024×1024',
                'memory_budget': '< 1 GB',
                'fps_target':    '移动端 30 FPS / PC 60 FPS',
                'key_rules': [
                    '通过 Quality Settings 实现分级质量，自动适配不同设备',
                    '移动端必须在真机（中低端设备）上通过 Unity Profiler 验证',
                    '资源包双版本：PC 高质量 + 移动端降质量',
                ],
            }

    # ─────────────────────────────────────────────────────────────
    # 辅助方法
    # ─────────────────────────────────────────────────────────────

    def _summarize_game(self, profile: Dict) -> str:
        type_map = {
            'rpg': 'RPG 角色扮演', 'action_rpg': '动作 RPG', 'fps': '第一人称射击',
            'tps': '第三人称射击', '2d_platformer': '2D 平台跳跃', 'platformer': '2D 平台跳跃',
            'metroidvania': '银河恶魔城', 'casual': '休闲游戏', 'puzzle': '益智游戏',
            'strategy': '策略游戏', 'simulation': '模拟经营', 'top_down': '俯视角游戏',
            'roguelike': 'Roguelike', 'fighting': '格斗游戏', 'racing': '赛车游戏',
            'survival': '生存游戏', 'open_world': '开放世界', 'narrative': '叙事游戏',
            'card': '卡牌游戏', 'action_adventure': '动作冒险', 'battle_royale': '大逃杀',
        }
        team_map = {
            'solo': '独立开发者', 'small': '小团队（2–5人）',
            'medium': '中型团队（5–20人）', 'large': '大团队（20人+）',
        }
        game_type = type_map.get(profile.get('game_type', ''), profile.get('game_type', '未知类型'))
        platforms = ' / '.join(profile.get('target_platforms', []))
        team      = team_map.get(profile.get('team_size', 'small'), '')
        timeline  = profile.get('timeline_months', 12)
        return f"{game_type}，目标平台：{platforms}，{team}，开发周期约 {timeline} 个月"

    def _assess_complexity(self, profile: Dict) -> str:
        score = 0
        if profile.get('has_multiplayer'):  score += 3
        if profile.get('has_narrative'):    score += 1
        if profile.get('has_hot_update'):   score += 2
        if profile.get('is_mobile') and profile.get('is_pc'): score += 1
        score += len(profile.get('features', []))
        if score >= 8:   return 'very_high'
        elif score >= 5: return 'high'
        elif score >= 3: return 'medium'
        else:            return 'low'
