#!/usr/bin/env python3
"""
技术实现向导 (Implementation Wizard Expert)

职责:
- 根据架构师选型生成 Unity 项目目录骨架
- 生成各系统的 C# 接口定义和空类模板
- 生成框架初始化引导代码（VContainer / GC2 / FishNet 等）
- 将数值设计转化为 ScriptableObject 配置模板
- 输出 Unity 项目设置检查清单
- 输出 Assembly Definition 建议结构

输出定位：产物供程序员直接复制进项目，不做完整逻辑实现。
"""

from typing import Dict, List, Any
from datetime import datetime


class ImplementationWizardExpert:
    """技术实现向导 — Unity 项目骨架与代码模板生成专家"""

    def __init__(self):
        self.name = "技术实现向导"
        self.version = "1.0.0"

    # ─────────────────────────────────────────────────────────────
    # 主入口
    # ─────────────────────────────────────────────────────────────

    def analyze(self, game_profile: Dict) -> Dict:
        """
        game_profile:
        {
            game_name:        str,
            game_type:        str,
            team_size:        str,      # solo / small / medium / large
            render_pipeline:  str,      # urp / hdrp / builtin
            main_framework:   str,      # gc2 / ucc / corgi / top_down / scratch
            network_framework:str,      # fishnet / photon_fusion / ngo / none
            di_framework:     str,      # vcontainer / zenject / none
            save_system:      str,      # easy_save3 / custom_json / playerprefs
            ui_system:        str,      # ugui / uitoolkit / fairygui
            architecture_pattern: str, # scriptableobject / mvc / ecs
            features:         list,    # multiplayer / iap / hot_update / complex_ai / narrative
            target_platforms: list,    # mobile / pc / console / webgl
            max_level:        int,
            has_gacha:        bool,
        }
        """
        p = self._normalize(game_profile)

        folder_structure  = self._build_folder_structure(p)
        asmdef_plan       = self._build_asmdef_plan(p)
        system_interfaces = self._build_system_interfaces(p)
        bootstrap_code    = self._build_bootstrap_code(p)
        so_templates      = self._build_so_templates(p)
        unity_settings    = self._build_unity_settings(p)
        coding_standards  = self._build_coding_standards(p)
        implementation_order = self._build_implementation_order(p)

        return {
            'status':               'success',
            'generated_at':         datetime.now().isoformat(),
            'wizard':               self.name,
            'game_info': {
                'name':             p['game_name'],
                'type':             p['game_type'],
                'render_pipeline':  p['render_pipeline'],
                'main_framework':   p['main_framework'],
                'di_framework':     p['di_framework'],
                'architecture':     p['architecture_pattern'],
            },
            'folder_structure':     folder_structure,
            'asmdef_plan':          asmdef_plan,
            'system_interfaces':    system_interfaces,
            'bootstrap_code':       bootstrap_code,
            'so_templates':         so_templates,
            'unity_settings':       unity_settings,
            'coding_standards':     coding_standards,
            'implementation_order': implementation_order,
        }

    # ─────────────────────────────────────────────────────────────
    # 项目目录结构
    # ─────────────────────────────────────────────────────────────

    def _build_folder_structure(self, p: Dict) -> Dict:
        base = {
            'Assets/': {
                '_Project/': {
                    'Scripts/': {
                        'Core/':          '核心基础设施：GameManager、ServiceLocator、EventBus',
                        'Systems/':       '各大系统（战斗、背包、任务等），每个系统一个子文件夹',
                        'Data/':          'ScriptableObject 数据定义',
                        'UI/':            'UI 控制器和视图，按界面分子文件夹',
                        'Gameplay/':      '玩法逻辑（角色控制、技能、相机等）',
                        'Utils/':         '工具类、扩展方法、常量',
                        'Generated/':     '自动生成代码（如地址、枚举），不要手动修改',
                    },
                    'Scenes/':    '按模块分：Boot、MainMenu、Gameplay_XXX、Loading',
                    'Prefabs/':   '按系统分子文件夹：UI、Characters、VFX、Environment',
                    'Resources/': '⚠️ 仅存放必须动态加载且无法用 Addressables 的资源',
                    'Art/':       '美术资源（Textures/Models/Animations/Audio），按类型分子文件夹',
                    'Settings/':  'URP/HDRP Renderer Assets、Input Actions、Project Settings',
                },
                'Plugins/':       '第三方插件（勿修改）',
                'StreamingAssets/': '热更资源、语言包等需要文件系统直接访问的资源',
                'AddressableAssetsData/': 'Addressables 配置（自动生成）',
            }
        }

        # 按特性追加
        scripts = base['Assets/']['_Project/']['Scripts/']
        if 'multiplayer' in p.get('features', []):
            scripts['Network/'] = '网络同步、消息定义、RPCHandler'
        if 'iap' in p.get('features', []):
            scripts['Monetization/'] = 'IAP 管理、商城逻辑、货币系统'
        if 'hot_update' in p.get('features', []):
            scripts['HotUpdate/'] = '热更入口、包管理（对应 HybridCLR/xLua）'
        if p.get('has_gacha'):
            scripts['Gacha/'] = '抽卡逻辑、概率池、保底计数'

        fw = p['main_framework']
        if fw == 'gc2':
            scripts['GC2Integration/'] = 'GameCreator2 扩展：自定义 Actions/Conditions/Properties'
        elif fw in ['ucc', 'corgi', 'top_down']:
            scripts['CharacterExtensions/'] = f'{fw.upper()} 扩展代码'

        return {
            'tree': base,
            'notes': [
                '以 _Project 作为根前缀，确保项目资产排在第三方插件前面（字母序）',
                'Scripts 按"系统"而非"类型"组织（不要建 Managers/ Controllers/ 大目录）',
                'Resources 文件夹越小越好，优先使用 Addressables',
                'Art 目录下每种资源类型有统一命名规范（见 Coding Standards）',
            ],
        }

    # ─────────────────────────────────────────────────────────────
    # Assembly Definition 计划
    # ─────────────────────────────────────────────────────────────

    def _build_asmdef_plan(self, p: Dict) -> List[Dict]:
        asdefs = [
            {
                'name':     f'{self._namespace(p)}.Core',
                'path':     'Assets/_Project/Scripts/Core/',
                'references': [],
                'purpose':  '核心基础设施，零外部依赖，其他所有 asmdef 可以引用它',
                'autoref':  False,
            },
            {
                'name':     f'{self._namespace(p)}.Data',
                'path':     'Assets/_Project/Scripts/Data/',
                'references': [f'{self._namespace(p)}.Core'],
                'purpose':  'ScriptableObject 数据定义，供 Systems 和 Gameplay 引用',
                'autoref':  False,
            },
            {
                'name':     f'{self._namespace(p)}.Systems',
                'path':     'Assets/_Project/Scripts/Systems/',
                'references': [f'{self._namespace(p)}.Core', f'{self._namespace(p)}.Data'],
                'purpose':  '各大系统实现，可细分为每系统独立 asmdef',
                'autoref':  False,
            },
            {
                'name':     f'{self._namespace(p)}.UI',
                'path':     'Assets/_Project/Scripts/UI/',
                'references': [f'{self._namespace(p)}.Core', f'{self._namespace(p)}.Systems'],
                'purpose':  'UI 层，依赖 Systems 但 Systems 不依赖 UI（单向依赖）',
                'autoref':  False,
            },
            {
                'name':     f'{self._namespace(p)}.Gameplay',
                'path':     'Assets/_Project/Scripts/Gameplay/',
                'references': [f'{self._namespace(p)}.Core', f'{self._namespace(p)}.Systems', f'{self._namespace(p)}.Data'],
                'purpose':  '玩法逻辑层，角色控制、相机、技能等',
                'autoref':  False,
            },
            {
                'name':     f'{self._namespace(p)}.Tests',
                'path':     'Assets/_Project/Tests/',
                'references': [f'{self._namespace(p)}.Core', f'{self._namespace(p)}.Systems'],
                'purpose':  '单元测试，仅编辑器模式',
                'autoref':  False,
                'editor_only': True,
            },
        ]

        if 'multiplayer' in p.get('features', []):
            asdefs.append({
                'name':     f'{self._namespace(p)}.Network',
                'path':     'Assets/_Project/Scripts/Network/',
                'references': [f'{self._namespace(p)}.Core', f'{self._namespace(p)}.Systems'],
                'purpose':  '网络系统，按需引用 FishNet/NGO 程序集',
                'autoref':  False,
            })

        return asdefs

    # ─────────────────────────────────────────────────────────────
    # 系统接口定义
    # ─────────────────────────────────────────────────────────────

    def _build_system_interfaces(self, p: Dict) -> List[Dict]:
        ns   = self._namespace(p)
        arch = p['architecture_pattern']
        gt   = p['game_type']
        di   = p['di_framework']

        base_interface = f"""using System;
using System.Threading;
using Cysharp.Threading.Tasks;  // 若未用 UniTask 可改为 System.Threading.Tasks.Task

namespace {ns}.Core
{{
    /// <summary>所有游戏系统必须实现此接口</summary>
    public interface IGameSystem
    {{
        UniTask InitializeAsync(CancellationToken ct = default);
        void Dispose();
    }}
}}"""

        event_bus = f"""using System;
using System.Collections.Generic;
using UnityEngine;

namespace {ns}.Core
{{
    /// <summary>
    /// 轻量级类型安全事件总线。
    /// 用法：EventBus.Subscribe<PlayerDiedEvent>(OnPlayerDied);
    ///       EventBus.Publish(new PlayerDiedEvent {{ Reason = "落水" }});
    /// </summary>
    public static class EventBus
    {{
        private static readonly Dictionary<Type, List<Delegate>> _handlers = new();

        public static void Subscribe<T>(Action<T> handler)
        {{
            var type = typeof(T);
            if (!_handlers.ContainsKey(type)) _handlers[type] = new List<Delegate>();
            _handlers[type].Add(handler);
        }}

        public static void Unsubscribe<T>(Action<T> handler)
        {{
            if (_handlers.TryGetValue(typeof(T), out var list)) list.Remove(handler);
        }}

        public static void Publish<T>(T eventData)
        {{
            if (!_handlers.TryGetValue(typeof(T), out var list)) return;
            foreach (var h in list.ToArray()) ((Action<T>)h)?.Invoke(eventData);
        }}

        public static void Clear() => _handlers.Clear();
    }}

    // ─── 事件结构体示例（在各 System 命名空间下定义对应事件）───
    // public readonly struct PlayerDiedEvent {{ public string Reason; }}
    // public readonly struct LevelUpEvent {{ public int NewLevel; public int OldLevel; }}
    // public readonly struct ItemPickedUpEvent {{ public int ItemId; public int Count; }}
}}"""

        game_manager = f"""using System;
using System.Threading;
using Cysharp.Threading.Tasks;
using UnityEngine;

namespace {ns}.Core
{{
    /// <summary>
    /// GameManager —— 游戏生命周期管理器。
    /// 负责系统初始化顺序、场景切换、全局状态。
    /// 所有系统通过 VContainer/ServiceLocator 获取，不直接持有引用。
    /// </summary>
    public class GameManager : MonoBehaviour
    {{
        public static GameManager Instance {{ get; private set; }}

        [Header("启动配置")]
        [SerializeField] private bool _showLoadingOnStart = true;

        private CancellationTokenSource _cts;

        private void Awake()
        {{
            if (Instance != null) {{ Destroy(gameObject); return; }}
            Instance = this;
            DontDestroyOnLoad(gameObject);
            _cts = new CancellationTokenSource();
        }}

        private async void Start()
        {{
            try
            {{
                await InitializeAllSystemsAsync(_cts.Token);
            }}
            catch (OperationCanceledException)
            {{
                // 正常取消
            }}
            catch (Exception e)
            {{
                Debug.LogError($"[GameManager] 系统初始化失败: {{e}}");
            }}
        }}

        private async UniTask InitializeAllSystemsAsync(CancellationToken ct)
        {{
            // TODO: 按依赖顺序初始化各系统
            // await serviceLocator.Get<ISaveSystem>().InitializeAsync(ct);
            // await serviceLocator.Get<IInventorySystem>().InitializeAsync(ct);
            // await serviceLocator.Get<IQuestSystem>().InitializeAsync(ct);
            Debug.Log("[GameManager] 所有系统初始化完成");
        }}

        private void OnDestroy()
        {{
            _cts?.Cancel();
            _cts?.Dispose();
            EventBus.Clear();
        }}
    }}
}}"""

        # 按游戏类型生成关键系统接口
        system_interfaces = self._get_system_interfaces_for_type(p)

        # DI 注册模板
        di_code = self._build_di_registration(p)

        return [
            {'name': 'IGameSystem（基础接口）',       'language': 'csharp', 'path': f'Assets/_Project/Scripts/Core/IGameSystem.cs',   'code': base_interface},
            {'name': 'EventBus（事件总线）',           'language': 'csharp', 'path': f'Assets/_Project/Scripts/Core/EventBus.cs',       'code': event_bus},
            {'name': 'GameManager（生命周期管理）',    'language': 'csharp', 'path': f'Assets/_Project/Scripts/Core/GameManager.cs',    'code': game_manager},
            {'name': 'DI 注册（依赖注入）',            'language': 'csharp', 'path': f'Assets/_Project/Scripts/Core/GameInstaller.cs', 'code': di_code},
        ] + system_interfaces

    def _get_system_interfaces_for_type(self, p: Dict) -> List[Dict]:
        ns = self._namespace(p)
        gt = p['game_type']
        interfaces = []

        # 存档系统（所有类型）
        interfaces.append({
            'name': 'ISaveSystem',
            'language': 'csharp',
            'path': f'Assets/_Project/Scripts/Systems/Save/ISaveSystem.cs',
            'code': f"""using Cysharp.Threading.Tasks;
using System.Threading;

namespace {ns}.Systems.Save
{{
    public interface ISaveSystem : Core.IGameSystem
    {{
        UniTask SaveAsync(string slotKey, CancellationToken ct = default);
        UniTask<T> LoadAsync<T>(string slotKey, T defaultValue = default, CancellationToken ct = default);
        bool HasSave(string slotKey);
        void DeleteSave(string slotKey);
    }}

    // ── {p['save_system']} 实现提示 ─────────────────────────────────
    // Easy Save 3:  ES3.Save(key, value); ES3.Load<T>(key, defaultVal);
    // Custom JSON:  File.WriteAllText(path, JsonUtility.ToJson(data));
    // PlayerPrefs:  仅适合极简配置，不推荐存游戏进度
}}"""
        })

        # RPG/动作RPG/开放世界 → 战斗、背包、角色
        if gt in ['rpg', 'action_rpg', 'open_world', 'action_adventure', 'top_down_rpg']:
            interfaces.append({
                'name': 'ICombatSystem',
                'language': 'csharp',
                'path': f'Assets/_Project/Scripts/Systems/Combat/ICombatSystem.cs',
                'code': f"""using UnityEngine;
using Cysharp.Threading.Tasks;
using System.Threading;

namespace {ns}.Systems.Combat
{{
    public interface ICombatSystem : Core.IGameSystem
    {{
        float CalculateDamage(DamageContext ctx);
        UniTask<CombatResult> ExecuteSkillAsync(SkillUseContext ctx, CancellationToken ct = default);
        void ApplyStatusEffect(GameObject target, StatusEffectData effect);
    }}

    [System.Serializable]
    public struct DamageContext
    {{
        public float ATK;           // 攻击方攻击力
        public float SkillMultiplier; // 技能倍率（普攻=1.0, 技能=2.5等）
        public float DEF;           // 防御方防御力
        public float CritRate;      // 暴击率 0-1
        public float CritDmgBonus;  // 暴击伤害加成（额外）0=无额外，0.5=150%暴击
        public float[] BuffMultipliers; // 所有buff乘区
    }}

    [System.Serializable]
    public struct CombatResult
    {{
        public float FinalDamage;
        public bool IsCritical;
        public bool IsKill;
    }}
}}"""
            })

            interfaces.append({
                'name': 'IInventorySystem',
                'language': 'csharp',
                'path': f'Assets/_Project/Scripts/Systems/Inventory/IInventorySystem.cs',
                'code': f"""using System.Collections.Generic;
using Cysharp.Threading.Tasks;

namespace {ns}.Systems.Inventory
{{
    public interface IInventorySystem : Core.IGameSystem
    {{
        bool AddItem(int itemId, int count = 1);
        bool RemoveItem(int itemId, int count = 1);
        bool HasItem(int itemId, int count = 1);
        int GetItemCount(int itemId);
        IReadOnlyList<ItemStack> GetAllItems();
        void EquipItem(int itemId, EquipSlot slot);
        void UnequipSlot(EquipSlot slot);
    }}

    [System.Serializable]
    public struct ItemStack {{ public int ItemId; public int Count; }}
    public enum EquipSlot {{ Weapon, Offhand, Helmet, Chest, Legs, Boots, Ring1, Ring2, Necklace }}
}}"""
            })

            if gt in ['rpg', 'open_world', 'top_down_rpg'] or 'quest' in p.get('features', []):
                interfaces.append({
                    'name': 'IQuestSystem',
                    'language': 'csharp',
                    'path': f'Assets/_Project/Scripts/Systems/Quest/IQuestSystem.cs',
                    'code': f"""using System.Collections.Generic;

namespace {ns}.Systems.Quest
{{
    public interface IQuestSystem : Core.IGameSystem
    {{
        void StartQuest(string questId);
        void CompleteQuest(string questId);
        void FailQuest(string questId);
        void UpdateProgress(string questId, string objectiveId, int delta);
        QuestState GetQuestState(string questId);
        IReadOnlyList<string> GetActiveQuestIds();
    }}

    public enum QuestState {{ NotStarted, InProgress, Completed, Failed }}
}}"""
                })

        # FPS/TPS → 武器系统
        if gt in ['fps', 'tps', 'battle_royale']:
            interfaces.append({
                'name': 'IWeaponSystem',
                'language': 'csharp',
                'path': f'Assets/_Project/Scripts/Systems/Weapon/IWeaponSystem.cs',
                'code': f"""using UnityEngine;

namespace {ns}.Systems.Weapon
{{
    public interface IWeaponSystem : Core.IGameSystem
    {{
        void Equip(WeaponData weaponData);
        void Fire(Ray aimRay);
        void Reload();
        void AltFire(Ray aimRay);   // 瞄准/副功能
        WeaponState GetCurrentState();
    }}

    [System.Serializable]
    public struct WeaponData
    {{
        public string WeaponId;
        public float BaseDamage;
        public float FireRate;      // 发/秒
        public int MagazineSize;
        public float ReloadTime;    // 秒
        public float HeadshotMultiplier;
        public AnimationClip FireAnim;
    }}

    public enum WeaponState {{ Idle, Firing, Reloading, Empty }}
}}"""
            })

        # 多人游戏 → 网络接口
        if 'multiplayer' in p.get('features', []):
            net_fw = p.get('network_framework', 'fishnet')
            interfaces.append({
                'name': 'INetworkSystem',
                'language': 'csharp',
                'path': f'Assets/_Project/Scripts/Network/INetworkSystem.cs',
                'code': f"""using System;
using Cysharp.Threading.Tasks;
using System.Threading;

namespace {ns}.Network
{{
    /// <summary>网络系统抽象层 — 当前选型: {net_fw}</summary>
    public interface INetworkSystem : Core.IGameSystem
    {{
        bool IsHost {{ get; }}
        bool IsConnected {{ get; }}
        int LocalClientId {{ get; }}

        UniTask StartHostAsync(ushort port = 7777, CancellationToken ct = default);
        UniTask StartClientAsync(string address, ushort port = 7777, CancellationToken ct = default);
        void Disconnect();

        event Action<int> OnClientConnected;
        event Action<int> OnClientDisconnected;
    }}

    // ── {net_fw} 注意事项 ─────────────────────────────────────────
    // FishNet:   使用 [ServerRpc] / [ObserversRpc] 特性标记网络方法
    //            NetworkObject + NetworkBehaviour 替代普通 MonoBehaviour
    // NGO:       NetworkManager.Singleton.StartHost() / StartClient()
    //            使用 NetworkVariable<T> 做自动同步
    // Photon Fusion: Runner.StartGame(GameMode.Host/Client)
    //               [Networked] 属性自动同步
}}"""
            })

        # UI 系统
        interfaces.append({
            'name': 'IUISystem',
            'language': 'csharp',
            'path': f'Assets/_Project/Scripts/UI/IUISystem.cs',
            'code': f"""using Cysharp.Threading.Tasks;
using System.Threading;
using UnityEngine;

namespace {ns}.UI
{{
    public interface IUISystem : Core.IGameSystem
    {{
        UniTask<T> ShowAsync<T>(object args = null, CancellationToken ct = default) where T : UIPanel;
        UniTask HideAsync<T>(CancellationToken ct = default) where T : UIPanel;
        void HideAll();
        T GetPanel<T>() where T : UIPanel;
    }}

    /// <summary>所有UI面板的基类</summary>
    public abstract class UIPanel : MonoBehaviour
    {{
        public virtual UniTask OnShowAsync(object args, CancellationToken ct) => UniTask.CompletedTask;
        public virtual UniTask OnHideAsync(CancellationToken ct) => UniTask.CompletedTask;
    }}
}}"""
        })

        return interfaces

    def _build_di_registration(self, p: Dict) -> str:
        ns  = self._namespace(p)
        di  = p['di_framework']
        gt  = p['game_type']

        if di == 'vcontainer':
            combat_reg = "builder.Register<CombatSystem>(Lifetime.Singleton).As<ICombatSystem>();" if gt in ['rpg', 'action_rpg', 'open_world'] else '// 按需注册战斗系统'
            net_reg    = "builder.Register<NetworkSystem>(Lifetime.Singleton).As<INetworkSystem>();" if 'multiplayer' in p.get('features', []) else '// 无多人，跳过网络系统'
            return f"""using VContainer;
using VContainer.Unity;
using {ns}.Core;
using {ns}.Systems.Save;
using {ns}.UI;

namespace {ns}.Core
{{
    /// <summary>
    /// VContainer 根容器配置。
    /// 所有系统在此注册，运行时通过构造函数注入获取依赖。
    /// </summary>
    public class GameInstaller : LifetimeScope
    {{
        protected override void Configure(IContainerBuilder builder)
        {{
            // ── 核心系统 ──────────────────────────────────────────
            builder.RegisterEntryPoint<GameBootstrap>();  // 启动序列
            builder.Register<SaveSystem>(Lifetime.Singleton).As<ISaveSystem>();
            builder.Register<UISystem>(Lifetime.Singleton).As<IUISystem>();

            // ── 游戏系统 ──────────────────────────────────────────
            {combat_reg}
            builder.Register<InventorySystem>(Lifetime.Singleton).As<IInventorySystem>();
            builder.Register<QuestSystem>(Lifetime.Singleton).As<IQuestSystem>();

            // ── 网络 ───────────────────────────────────────────────
            {net_reg}

            // ── 数据层（ScriptableObject 注入）────────────────────
            // builder.RegisterInstance(Resources.Load<GameConfigSO>("GameConfig")).As<IGameConfig>();
        }}
    }}

    /// <summary>系统初始化启动序列（替代 GameManager.Start）</summary>
    public class GameBootstrap : IAsyncStartable
    {{
        private readonly ISaveSystem _save;
        private readonly IInventorySystem _inventory;

        public GameBootstrap(ISaveSystem save, IInventorySystem inventory)
        {{
            _save      = save;
            _inventory = inventory;
        }}

        public async System.Threading.Tasks.Task StartAsync(System.Threading.CancellationToken ct)
        {{
            await _save.InitializeAsync(ct);
            await _inventory.InitializeAsync(ct);
            // 按依赖顺序添加其他系统...
            UnityEngine.Debug.Log("[Bootstrap] 所有系统启动完成");
        }}
    }}
}}"""

        elif di == 'zenject':
            return f"""using Zenject;
using {ns}.Core;
using {ns}.Systems.Save;

namespace {ns}.Core
{{
    public class GameInstaller : MonoInstaller
    {{
        public override void InstallBindings()
        {{
            Container.Bind<ISaveSystem>().To<SaveSystem>().AsSingle();
            Container.Bind<IUISystem>().To<UISystem>().AsSingle();
            // Container.Bind<ICombatSystem>().To<CombatSystem>().AsSingle();
        }}
    }}
}}"""

        else:  # none — 简单 ServiceLocator
            return f"""using System;
using System.Collections.Generic;
using UnityEngine;

namespace {ns}.Core
{{
    /// <summary>
    /// 轻量级 ServiceLocator（无 DI 框架时使用）。
    /// 推荐替换为 VContainer 以获得更好的可测试性。
    /// </summary>
    public static class ServiceLocator
    {{
        private static readonly Dictionary<Type, object> _services = new();

        public static void Register<T>(T instance) => _services[typeof(T)] = instance;
        public static T Get<T>() => _services.TryGetValue(typeof(T), out var s) ? (T)s
            : throw new InvalidOperationException($"Service {{typeof(T).Name}} not registered");
        public static bool TryGet<T>(out T service)
        {{
            if (_services.TryGetValue(typeof(T), out var s)) {{ service = (T)s; return true; }}
            service = default; return false;
        }}
        public static void Clear() => _services.Clear();
    }}

    // 用法:
    // void Awake() => ServiceLocator.Register<ISaveSystem>(new SaveSystem());
    // var save = ServiceLocator.Get<ISaveSystem>();
}}"""

    # ─────────────────────────────────────────────────────────────
    # 框架引导代码
    # ─────────────────────────────────────────────────────────────

    def _build_bootstrap_code(self, p: Dict) -> List[Dict]:
        results = []
        fw = p['main_framework']
        ns = self._namespace(p)

        if fw == 'gc2':
            results.append({
                'name': 'Game Creator 2 — 自定义 Action 模板',
                'language': 'csharp',
                'path': 'Assets/_Project/Scripts/GC2Integration/Action_CustomAction.cs',
                'code': f"""using System;
using System.Threading.Tasks;
using GameCreator.Runtime.Common;
using GameCreator.Runtime.Characters;
using UnityEngine;

namespace {ns}.GC2Integration
{{
    [Version(0, 1, 0)]
    [Title("Custom: 自定义动作名称")]
    [Description("描述这个 Action 的作用")]
    [Category("{ns}/Category/ActionName")]
    [Parameter("Target", "目标角色")]
    [Keywords("custom", "action")]
    [Image(typeof(IconCharacter), ColorTheme.Type.Green)]
    [Serializable]
    public class Action_CustomAction : Instruction
    {{
        [SerializeField] private PropertyGetGameObject _target = GetGameObjectPlayer.Create();
        [SerializeField] private float _value = 1f;

        public override string Title => $"Custom Action on {{_target}}";

        protected override async Task Run(Args args)
        {{
            GameObject target = _target.Get(args);
            if (target == null) return;

            // TODO: 实现具体逻辑
            // 例：获取自定义组件并调用方法
            // var component = target.Get<MyComponent>(args);
            // component?.DoSomething(_value);

            await Task.Yield(); // 若是同步操作可直接 return;
        }}
    }}
}}"""
            })

            results.append({
                'name': 'Game Creator 2 — 自定义 Property 模板',
                'language': 'csharp',
                'path': 'Assets/_Project/Scripts/GC2Integration/Property_CustomStat.cs',
                'code': f"""using GameCreator.Runtime.Common;
using GameCreator.Runtime.Stats;
using UnityEngine;

namespace {ns}.GC2Integration
{{
    // 自定义数值属性（Stat）：在 GC2 Stats 模块中注册后可在 Inspector 和 Visual Scripting 中使用
    // 使用方式：在 StatsAsset ScriptableObject 中添加此 Stat ID
    public static class CustomStatIds
    {{
        // 建议用 const string 统一管理所有 Stat ID，避免拼写错误
        public const string STRENGTH   = "strength";
        public const string AGILITY    = "agility";
        public const string INTELLIGENCE = "intelligence";
        public const string STAMINA    = "stamina";
        public const string LUCK       = "luck";

        // 战斗衍生属性（通过 Stat Formula 计算）
        public const string ATK_TOTAL  = "atk_total";
        public const string DEF_TOTAL  = "def_total";
        public const string HP_MAX     = "hp_max";
    }}
}}"""
            })

        elif fw in ['ucc']:
            results.append({
                'name': 'UCC — 自定义能力模板',
                'language': 'csharp',
                'path': 'Assets/_Project/Scripts/CharacterExtensions/Ability_Custom.cs',
                'code': f"""using Opsive.UltimateCharacterController.Character.Abilities;
using UnityEngine;

namespace {ns}.CharacterExtensions
{{
    /// <summary>
    /// UCC 自定义能力模板。
    /// 在 Character Inspector > Abilities 列表中添加。
    /// </summary>
    [System.Serializable]
    public class Ability_Custom : Ability
    {{
        // 能力优先级（数字越小优先级越高）
        public override int AbilityPriority => 100;

        // 何时可以激活
        public override bool CanStartAbility() => base.CanStartAbility() && /* 条件 */ true;

        // 激活时调用
        protected override void AbilityStarted()
        {{
            base.AbilityStarted();
            // TODO: 能力开始逻辑
        }}

        // 每帧更新
        public override void Update()
        {{
            base.Update();
            // TODO: 持续逻辑
        }}

        // 结束时调用
        protected override void AbilityStopped(bool force)
        {{
            base.AbilityStopped(force);
            // TODO: 清理逻辑
        }}
    }}
}}"""
            })

        # Addressables 资源加载封装（所有项目都需要）
        results.append({
            'name': 'Addressables — 资源管理封装',
            'language': 'csharp',
            'path': 'Assets/_Project/Scripts/Core/AssetLoader.cs',
            'code': f"""using System;
using System.Collections.Generic;
using System.Threading;
using Cysharp.Threading.Tasks;
using UnityEngine;
using UnityEngine.AddressableAssets;
using UnityEngine.ResourceManagement.AsyncOperations;

namespace {ns}.Core
{{
    /// <summary>
    /// Addressables 封装：统一资源加载、实例化和释放。
    /// 追踪所有 handle 防止内存泄漏。
    /// </summary>
    public static class AssetLoader
    {{
        private static readonly Dictionary<string, AsyncOperationHandle> _handles = new();

        /// <summary>加载资源（带缓存，同一 key 只加载一次）</summary>
        public static async UniTask<T> LoadAsync<T>(string address, CancellationToken ct = default)
        {{
            if (_handles.TryGetValue(address, out var cached))
                return (T)cached.Result;

            var handle = Addressables.LoadAssetAsync<T>(address);
            _handles[address] = handle;
            await handle.ToUniTask(cancellationToken: ct);

            if (handle.Status != AsyncOperationStatus.Succeeded)
            {{
                _handles.Remove(address);
                throw new Exception($"[AssetLoader] 加载失败: {{address}}");
            }}
            return handle.Result;
        }}

        /// <summary>实例化 Prefab（不缓存，每次创建新实例）</summary>
        public static async UniTask<GameObject> InstantiateAsync(
            string address, Transform parent = null, CancellationToken ct = default)
        {{
            var handle = Addressables.InstantiateAsync(address, parent);
            await handle.ToUniTask(cancellationToken: ct);
            return handle.Result;
        }}

        /// <summary>释放指定地址的缓存</summary>
        public static void Release(string address)
        {{
            if (!_handles.TryGetValue(address, out var handle)) return;
            Addressables.Release(handle);
            _handles.Remove(address);
        }}

        /// <summary>释放所有缓存（场景卸载时调用）</summary>
        public static void ReleaseAll()
        {{
            foreach (var h in _handles.Values) Addressables.Release(h);
            _handles.Clear();
        }}
    }}
}}"""
        })

        return results

    # ─────────────────────────────────────────────────────────────
    # ScriptableObject 模板
    # ─────────────────────────────────────────────────────────────

    def _build_so_templates(self, p: Dict) -> List[Dict]:
        ns = self._namespace(p)
        templates = []

        # 角色/装备数值配置
        if p['game_type'] in ['rpg', 'action_rpg', 'open_world', 'action_adventure', 'top_down_rpg', 'roguelike']:
            templates.append({
                'name': 'CharacterStatsSO（角色属性配置）',
                'language': 'csharp',
                'path': 'Assets/_Project/Scripts/Data/CharacterStatsSO.cs',
                'code': f"""using UnityEngine;

namespace {ns}.Data
{{
    [CreateAssetMenu(fileName = "CharacterStats_XXX", menuName = "{ns}/Data/Character Stats")]
    public class CharacterStatsSO : ScriptableObject
    {{
        [Header("基础属性")]
        public int   BaseHP         = 500;
        public int   BaseATK        = 20;
        public int   BaseDEF        = 10;
        public float BaseCritRate   = 0.05f;  // 5%
        public float BaseCritDmgBonus = 0.5f; // +50%（即150%总倍率）
        public float BaseSpeed      = 5f;

        [Header("成长参数")]
        [Tooltip("HP 线性成长：HP(lv) = BaseHP + (lv-1) × HPPerLevel（1-20级）")]
        public int   HPPerLevel     = 80;
        [Tooltip("ATK 指数系数：ATK(lv) = BaseATK × GrowthRate^(lv-1)")]
        public float ATKGrowthRate  = 1.08f;
        public float DEFGrowthRate  = 1.07f;

        [Header("战斗常数")]
        [Tooltip("DEF 减伤公式：DEF_Rate = DEF / (DEF + DefConstant)")]
        public float DefConstant    = 600f;
        public int   MaxLevel       = {p.get('max_level', 30)};

        [Header("暴击上限")]
        public float MaxCritRate    = 0.60f;   // 60%
        public float MaxCritDmgBonus = 2.00f;  // +200%

        /// <summary>计算指定等级的 HP</summary>
        public int GetHP(int level)
        {{
            level = Mathf.Clamp(level, 1, MaxLevel);
            if (level <= 20) return BaseHP + (level - 1) * HPPerLevel;
            float l20HP = BaseHP + 19f * HPPerLevel;
            return Mathf.RoundToInt(l20HP * Mathf.Pow(1.05f, level - 20));
        }}

        public int GetATK(int level) =>
            Mathf.RoundToInt(BaseATK * Mathf.Pow(ATKGrowthRate, level - 1));

        public int GetDEF(int level) =>
            Mathf.RoundToInt(BaseDEF * Mathf.Pow(DEFGrowthRate, level - 1));
    }}
}}"""
            })

            templates.append({
                'name': 'SkillDataSO（技能配置）',
                'language': 'csharp',
                'path': 'Assets/_Project/Scripts/Data/SkillDataSO.cs',
                'code': f"""using UnityEngine;

namespace {ns}.Data
{{
    [CreateAssetMenu(fileName = "Skill_XXX", menuName = "{ns}/Data/Skill")]
    public class SkillDataSO : ScriptableObject
    {{
        [Header("基本信息")]
        public string SkillId;
        public string DisplayName;
        [TextArea] public string Description;
        public Sprite Icon;

        [Header("战斗参数")]
        [Tooltip("伤害倍率：Final_DMG = ATK × DamageMultiplier × (1 - DEF_Rate)")]
        public float  DamageMultiplier  = 1.0f;
        public float  Cooldown          = 0f;   // 秒，0=无冷却
        public float  ManaCost          = 0f;   // 0=无消耗
        public int    HitCount          = 1;    // 多段伤害

        [Header("范围")]
        public SkillRange RangeType     = SkillRange.Single;
        public float  AreaRadius        = 2f;   // RangeType=Area 时生效

        [Header("效果")]
        public StatusEffectData[] ApplyEffects;  // 附加状态效果

        [Header("动画 & 特效")]
        public AnimationClip CastAnimation;
        public GameObject    HitVFXPrefab;
        public AudioClip     CastSFX;
    }}

    public enum SkillRange {{ Single, Area, Line, Self }}

    [System.Serializable]
    public struct StatusEffectData
    {{
        public string EffectId;
        public float  Duration;
        public float  Value;      // 效果强度（因效果类型而异）
        public float  ApplyChance; // 触发概率 0-1
    }}
}}"""
            })

        # 经济/物品数据
        templates.append({
            'name': 'ItemDataSO（物品配置）',
            'language': 'csharp',
            'path': 'Assets/_Project/Scripts/Data/ItemDataSO.cs',
            'code': f"""using UnityEngine;

namespace {ns}.Data
{{
    [CreateAssetMenu(fileName = "Item_XXX", menuName = "{ns}/Data/Item")]
    public class ItemDataSO : ScriptableObject
    {{
        [Header("基础")]
        public string   ItemId;
        public string   DisplayName;
        [TextArea(2,4)] public string Description;
        public Sprite   Icon;
        public ItemRarity Rarity      = ItemRarity.Common;
        public ItemType   Type        = ItemType.Consumable;

        [Header("堆叠")]
        public bool     Stackable     = true;
        public int      MaxStackSize  = 99;

        [Header("经济")]
        public int      BuyPrice      = 100;   // 商店购买价格（0=无法购买）
        public int      SellPrice     = 30;    // 出售价格（0=无法出售）

        [Header("装备属性（仅 Type=Equipment 时生效）")]
        public EquipSlotType EquipSlot;
        public StatBonus[]   StatBonuses;
    }}

    [System.Serializable]
    public struct StatBonus
    {{
        public string StatId;     // 对应 CharacterStatsSO 的属性 ID
        public float  FlatBonus;  // 固定值加成
        public float  PercentBonus; // 百分比加成（0.1 = +10%）
    }}

    public enum ItemRarity  {{ Common, Uncommon, Rare, Epic, Legendary }}
    public enum ItemType    {{ Consumable, Equipment, Material, QuestItem, Currency }}
    public enum EquipSlotType {{ Weapon, Offhand, Helmet, Chest, Legs, Boots, Ring, Necklace }}
}}"""
        })

        return templates

    # ─────────────────────────────────────────────────────────────
    # Unity 项目设置清单
    # ─────────────────────────────────────────────────────────────

    def _build_unity_settings(self, p: Dict) -> List[Dict]:
        rp       = p['render_pipeline']
        platforms = p.get('target_platforms', ['mobile'])
        settings  = []

        # 渲染管线
        if rp == 'urp':
            settings.append({
                'category': '渲染管线 (URP)',
                'items': [
                    'Edit → Project Settings → Graphics → Scriptable Render Pipeline Asset：指定你的 URP Asset',
                    'URP Asset：关闭 HDR（移动端），MSAA 选 2x（移动）或 4x（PC）',
                    'Renderer → 添加 ScreenSpaceAmbientOcclusion（PC端），移动端禁用',
                    'Quality Settings：多平台建议设置至少 Low/Medium/High 三档 URP Asset',
                    '推荐：开启 SRP Batcher，大幅降低 DrawCall',
                ],
            })

        # 平台优化
        if 'mobile' in platforms:
            settings.append({
                'category': '移动端设置 (iOS/Android)',
                'items': [
                    'Player Settings → Other Settings → Scripting Backend：IL2CPP（移动端必须）',
                    'API Compatibility Level：.NET Standard 2.1',
                    'Managed Stripping Level：High（减小包体，需配合 link.xml）',
                    'Architecture：ARM64（仅此，废弃 ARMv7）',
                    'Android → Minimum API Level：Android 7.0 (API 24) 以上',
                    'iOS → Target minimum iOS version：14.0 以上',
                    'Texture Compression：Android=ASTC，iOS=ASTC（Unity 2022+）',
                    '开启 GPU Instancing（在材质中勾选）',
                ],
            })

        if 'pc' in platforms:
            settings.append({
                'category': 'PC 设置',
                'items': [
                    'Player Settings → PC → Default Screen Width/Height：1920×1080',
                    'Fullscreen Mode：Fullscreen Window（非独占，兼容性最好）',
                    'Texture Compression：DXT（PC默认）',
                    '开启 MSAA 4x 和 Post Processing',
                ],
            })

        # 通用设置
        settings.append({
            'category': '通用项目设置',
            'items': [
                'Physics → Layer Collision Matrix：关闭不需要的层碰撞对，减少物理开销',
                'Tags & Layers：提前定义所有 Layer，用常量类替代字符串（避免拼写错误）',
                'Time → Fixed Timestep：0.02（默认），物理密集游戏可降至 0.01',
                'Input System Package：确认使用 New Input System，Legacy 已不推荐',
                'Script Execution Order：GameManager 设置为 -100（最先执行）',
                'Version Control：添加 .gitignore，排除 Library/ Temp/ Logs/',
            ],
        })

        # Addressables
        settings.append({
            'category': 'Addressables 配置',
            'items': [
                'Window → Asset Management → Addressables → Groups：Create 默认组',
                '所有运行时资源移入 Addressables Groups（Prefabs/Art/Audio）',
                'Build & Load Paths：Use Asset Database（开发）→ Remote（发布热更时）',
                'Profile：建议至少 Default（本地开发）和 Remote（线上热更）两个 Profile',
                'Build → New Build → Default Build Script，生成 catalog.json',
            ],
        })

        if 'hot_update' in p.get('features', []):
            settings.append({
                'category': '热更新配置 (HybridCLR)',
                'items': [
                    'HybridCLR → Settings → Enable：开启 IL2CPP 热更支持',
                    '热更程序集：创建独立 asmdef 放在 HotUpdate/ 目录',
                    'AOT 泛型收集：运行时前执行 HybridCLR Generate All',
                    '热更包打包：Build HotUpdate DLL → 上传 CDN → Addressables 更新',
                ],
            })

        return settings

    # ─────────────────────────────────────────────────────────────
    # 编码规范
    # ─────────────────────────────────────────────────────────────

    def _build_coding_standards(self, p: Dict) -> Dict:
        ns = self._namespace(p)
        return {
            'namespace':    ns,
            'naming': [
                {'类型': '类/接口/枚举',   '规范': 'PascalCase',  '示例': 'CombatSystem, IInventorySystem, ItemRarity'},
                {'类型': '方法/属性',      '规范': 'PascalCase',  '示例': 'GetDamage(), IsAlive, MaxHealth'},
                {'类型': '私有字段',       '规范': '_camelCase',  '示例': '_currentHP, _inventoryItems'},
                {'类型': '参数/局部变量',  '规范': 'camelCase',   '示例': 'targetEnemy, damageAmount'},
                {'类型': 'const常量',     '规范': 'UPPER_SNAKE',  '示例': 'MAX_LEVEL, BASE_HP'},
                {'类型': 'ScriptableObject', '规范': 'TypeName_ID', '示例': 'Skill_Fireball, Item_HealthPotion'},
                {'类型': 'Prefab',        '规范': 'PFB_Name',    '示例': 'PFB_Player, PFB_EnemySkeleton'},
                {'类型': 'Material',      '规范': 'MAT_Name',    '示例': 'MAT_Player_Skin, MAT_Rock'},
                {'类型': 'Scene',         '规范': 'SCN_Name',    '示例': 'SCN_Boot, SCN_MainMenu, SCN_Level01'},
                {'类型': '动画 Clip',     '规范': 'ANM_Name',    '示例': 'ANM_Player_Run, ANM_Enemy_Attack'},
            ],
            'anti_patterns': [
                'FindObjectOfType<T>() 在 Update/FixedUpdate 中调用 → 改用注入或缓存引用',
                'GameObject.Find("name") → 改用 Addressables 或 DI 注入',
                'SendMessage() → 改用 EventBus 或接口方法',
                'Resources.Load() 大量使用 → 改用 Addressables',
                '每帧 GetComponent<T>() → Awake 中缓存',
                '字符串比较 tag/layer → 改用常量整数 Layer Mask',
            ],
            'performance_rules': [
                '对象池：频繁创建销毁的物体（子弹、特效、掉落物）必须使用 ObjectPool<T>',
                '事件取消注册：OnDisable 中 Unsubscribe 所有事件，防止内存泄漏',
                'Coroutine vs UniTask：新代码统一使用 UniTask，Coroutine 仅遗留代码保留',
                'struct vs class：高频创建的小数据类型（Vector3、DamageContext 等）用 struct',
                'Profiler 优先：优化前先 Profile，不要凭感觉优化',
            ],
        }

    # ─────────────────────────────────────────────────────────────
    # 实现顺序建议
    # ─────────────────────────────────────────────────────────────

    def _build_implementation_order(self, p: Dict) -> List[Dict]:
        gt = p['game_type']

        base_order = [
            {
                'phase': 1,
                'name': '项目初始化（Day 1-3）',
                'tasks': [
                    '创建目录结构，设置 Assembly Definitions',
                    '配置 VContainer/ServiceLocator 根容器',
                    '实现 GameManager 和 EventBus',
                    '配置渲染管线（URP Asset）和 Quality Settings',
                    '建立 Git 仓库，写 .gitignore，做第一次提交',
                ],
                'deliverable': '可以运行的空白项目，框架骨架就位',
            },
            {
                'phase': 2,
                'name': '核心玩法原型（Week 1-2）',
                'tasks': [
                    '实现角色控制器（移动/跳跃/基础交互）',
                    '实现最小化战斗系统（仅伤害公式，无技能）',
                    '实现存档系统（至少能存一个变量）',
                    '建立第一个测试场景验证手感',
                ],
                'deliverable': 'Vertical Slice：30秒可玩的核心循环',
            },
            {
                'phase': 3,
                'name': '系统扩展（Week 3-6）',
                'tasks': [
                    '按系统策划师文档，逐系统实现（背包→任务→技能→对话）',
                    '每个系统实现后写最小化单元测试',
                    '实现 ScriptableObject 数据管道，数值策划师可以直接填表',
                    '实现基础 UI 框架（Panel 基类 + UISystem）',
                ],
                'deliverable': '所有核心系统可以独立运行',
            },
            {
                'phase': 4,
                'name': '内容填充（Week 7-10）',
                'tasks': [
                    '对接美术资产，替换 Placeholder 素材',
                    '按关卡策划师文档搭建前3个关卡',
                    '实现音频系统，接入背景音乐和音效',
                    '实现存读档完整流程',
                ],
                'deliverable': '可以完整游玩前3关的 Alpha 版本',
            },
            {
                'phase': 5,
                'name': '打磨与优化（Week 11-14）',
                'tasks': [
                    'Profiler 分析，解决性能热点',
                    '实现对象池，优化高频创建对象',
                    '接入崩溃上报（Firebase Crashlytics 或 Sentry）',
                    'QA 测试，修复 P0/P1 Bug',
                    '提审材料准备（隐私政策/年龄评级/截图）',
                ],
                'deliverable': 'Beta 版本，准备小规模测试',
            },
        ]

        if 'multiplayer' in p.get('features', []):
            base_order.insert(2, {
                'phase': '2b',
                'name': '网络层验证（在原型阶段并行）',
                'tasks': [
                    '搭建本地 Host/Client 连接测试',
                    '验证最核心的同步数据（角色位置/血量）',
                    '测试延迟补偿效果（100ms 模拟）',
                    '确认选型是否满足需求，否则此时切换框架成本最低',
                ],
                'deliverable': '两台设备可以连接并看到对方',
            })

        return base_order

    # ─────────────────────────────────────────────────────────────
    # 辅助
    # ─────────────────────────────────────────────────────────────

    def _normalize(self, raw: Dict) -> Dict:
        p = dict(raw)
        p.setdefault('game_name', 'MyGame')
        p.setdefault('game_type', 'rpg')
        p.setdefault('team_size', 'small')
        p.setdefault('render_pipeline', 'urp')
        p.setdefault('main_framework', 'gc2')
        p.setdefault('network_framework', 'none')
        p.setdefault('di_framework', 'vcontainer')
        p.setdefault('save_system', 'easy_save3')
        p.setdefault('ui_system', 'ugui')
        p.setdefault('architecture_pattern', 'scriptableobject')
        p.setdefault('features', [])
        p.setdefault('target_platforms', ['mobile'])
        p.setdefault('max_level', 30)
        p.setdefault('has_gacha', False)
        return p

    def _namespace(self, p: Dict) -> str:
        name = p.get('game_name', 'MyGame')
        # 转 PascalCase，去除非字母数字字符
        parts = ''.join(c if c.isalnum() or c == ' ' else ' ' for c in name).split()
        return ''.join(w.capitalize() for w in parts) if parts else 'MyGame'
