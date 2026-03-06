#!/usr/bin/env python3
"""
QA 工程师 (QA Engineer Expert)

职责:
- 生成完整测试计划（按系统分解）
- 输出平台专项测试用例（iOS/Android/PC/主机）
- 生成性能测试基准和压力测试方案
- 输出常见 Unity Bug 回归检查表
- 生成上线前发布清单（按平台）
- 定义 Bug 严重等级矩阵和优先级规则
- 生成自动化测试建议
"""

from typing import Dict, List, Any
from datetime import datetime


class QAEngineerExpert:
    """QA 工程师 — 游戏质量保证与测试规划专家"""

    def __init__(self):
        self.name = "QA 工程师"
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
            target_platforms: list,   # mobile / pc / console / webgl
            features:         list,   # multiplayer / iap / hot_update / narrative / combat / inventory / quest
            team_size:        str,    # solo / small / medium / large
            has_multiplayer:  bool,
            has_iap:          bool,
            has_gacha:        bool,
            max_level:        int,
            monetization_type: str,   # f2p / premium / hybrid
            has_hot_update:   bool,
        }
        """
        p = self._normalize(game_profile)

        test_strategy    = self._build_test_strategy(p)
        feature_tests    = self._build_feature_tests(p)
        platform_tests   = self._build_platform_tests(p)
        performance_tests = self._build_performance_tests(p)
        regression_list  = self._build_unity_regression_list(p)
        bug_matrix       = self._build_bug_matrix()
        release_checklist = self._build_release_checklist(p)
        automation_plan  = self._build_automation_plan(p)

        return {
            'status':           'success',
            'generated_at':     datetime.now().isoformat(),
            'engineer':         self.name,
            'game_info': {
                'name':         p['game_name'],
                'type':         p['game_type'],
                'platforms':    p['target_platforms'],
                'has_iap':      p['has_iap'],
                'has_multiplayer': p['has_multiplayer'],
            },
            'test_strategy':    test_strategy,
            'feature_tests':    feature_tests,
            'platform_tests':   platform_tests,
            'performance_tests': performance_tests,
            'unity_regression': regression_list,
            'bug_matrix':       bug_matrix,
            'release_checklist': release_checklist,
            'automation_plan':  automation_plan,
        }

    # ─────────────────────────────────────────────────────────────
    # 测试策略总览
    # ─────────────────────────────────────────────────────────────

    def _build_test_strategy(self, p: Dict) -> Dict:
        gt       = p['game_type']
        team     = p['team_size']
        platforms = p['target_platforms']

        # 各测试类型推荐覆盖率
        coverage_by_team = {
            'solo':   {'unit': '20%', 'integration': '基本流程', 'manual': '核心路径', 'automated': '极少'},
            'small':  {'unit': '40%', 'integration': '主系统', 'manual': '完整功能', 'automated': '冒烟测试'},
            'medium': {'unit': '60%', 'integration': '全系统', 'manual': '全覆盖', 'automated': '回归套件'},
            'large':  {'unit': '80%', 'integration': '全系统', 'manual': '探索测试', 'automated': '完整CI/CD'},
        }
        cov = coverage_by_team.get(team, coverage_by_team['small'])

        risk_areas = []
        if p['has_multiplayer']:
            risk_areas.append('网络同步：延迟/断线/作弊是最高风险区域')
        if p['has_iap']:
            risk_areas.append('内购：支付流程是法律风险区，必须 100% 测试所有支付路径')
        if p['has_gacha']:
            risk_areas.append('抽卡概率：概率计算错误是玩家投诉高发区，须独立验证')
        if 'hot_update' in p.get('features', []):
            risk_areas.append('热更新：更新失败/回滚/兼容性是上线后最常见事故源')
        if 'mobile' in platforms:
            risk_areas.append('移动端适配：碎片化设备（低端机/刘海屏/折叠屏）是移动QA核心')
        if gt in ['fps', 'battle_royale'] and p['has_multiplayer']:
            risk_areas.append('反作弊：速度修改/穿墙/伤害注入是竞技游戏生死攸关的风险')

        return {
            'philosophy': '质量内建（Quality Built-in）：QA 在设计阶段介入，而非开发完成后才测试',
            'test_pyramid': {
                'unit':        f'单元测试覆盖率目标：{cov["unit"]}（纯逻辑函数，如伤害计算、概率函数）',
                'integration': f'集成测试：{cov["integration"]}（系统间交互，如背包→装备→属性联动）',
                'e2e':         f'手动测试：{cov["manual"]}（完整用户路径，如新手引导→第一关→Boss）',
                'automated':   f'自动化测试：{cov["automated"]}（PlayMode Tests + Unity Test Framework）',
            },
            'high_risk_areas': risk_areas,
            'qa_phases': [
                {'phase': 'Alpha',  'goal': '功能可用性，核心路径无崩溃', 'exit_criteria': 'P0 Bug 全部修复，P1 Bug < 5个'},
                {'phase': 'Beta',   'goal': '性能达标，平台合规，完整流程', 'exit_criteria': 'P1 Bug 全部修复，P2 Bug < 20个，FPS 达标'},
                {'phase': 'RC',     'goal': '发布就绪，0新P0/P1', 'exit_criteria': '72小时无新增 P0/P1，发布清单全部通过'},
            ],
            'team_note': f'当前团队规模（{team}）建议：{self._team_qa_advice(team)}',
        }

    def _team_qa_advice(self, team: str) -> str:
        advice = {
            'solo':   '开发者自测为主，建立每日冒烟测试习惯，上线前找3-5名外部测试者',
            'small':  '至少1名专职QA或开发兼职QA，建立 Bug 跟踪系统（Linear/Jira/Notion）',
            'medium': '2-3名QA工程师，分系统负责，引入自动化回归测试',
            'large':  '完整QA团队，功能QA+性能QA+自动化QA分工，严格门禁流程',
        }
        return advice.get(team, advice['small'])

    # ─────────────────────────────────────────────────────────────
    # 功能测试用例
    # ─────────────────────────────────────────────────────────────

    def _build_feature_tests(self, p: Dict) -> List[Dict]:
        gt       = p['game_type']
        features = p.get('features', [])
        tests    = []

        # 核心游戏循环（所有类型）
        tests.append({
            'system': '核心游戏循环',
            'priority': 'P0',
            'cases': [
                {'id': 'CORE-001', 'title': '游戏正常启动到主菜单',           'steps': '冷启动游戏 → 观察加载', 'expected': '30秒内进入主菜单，无崩溃，无ANR'},
                {'id': 'CORE-002', 'title': '新游戏创建并进入第一关',         'steps': '主菜单 → 新游戏 → 选择角色 → 进入', 'expected': '正常加载，新手引导触发'},
                {'id': 'CORE-003', 'title': '游戏进度保存与读取',             'steps': '游戏中存档 → 退出 → 重启 → 读档', 'expected': '所有进度（等级/物品/任务）完整恢复'},
                {'id': 'CORE-004', 'title': '后台切换不崩溃',                'steps': '游戏中 → 按Home键 → 等待30秒 → 返回', 'expected': '正常恢复，无黑屏，无数据丢失'},
                {'id': 'CORE-005', 'title': '来电打断后恢复',                'steps': '游戏中 → 模拟来电 → 通话结束 → 返回', 'expected': '游戏正常恢复，战斗状态保留（仅移动端）'},
            ],
        })

        # 战斗系统
        if 'combat' in features or gt in ['rpg', 'action_rpg', 'fps', 'fighting', 'roguelike']:
            tests.append({
                'system': '战斗系统',
                'priority': 'P0',
                'cases': [
                    {'id': 'COMBAT-001', 'title': '基础攻击命中伤害正确',      'steps': '玩家攻击已知DEF的敌人，记录伤害数字', 'expected': f'伤害值符合公式：Final=ATK×Multiplier×(1-DEF/(DEF+常数))，偏差<1'},
                    {'id': 'COMBAT-002', 'title': '暴击触发概率符合设计',      'steps': '攻击1000次，统计暴击次数', 'expected': '实际暴击率与设计值偏差<±2%（概率测试）'},
                    {'id': 'COMBAT-003', 'title': '技能冷却计时正确',          'steps': '使用技能 → 计时CD结束', 'expected': 'CD时间与配置值一致，误差<100ms'},
                    {'id': 'COMBAT-004', 'title': '角色死亡流程正确',          'steps': '将玩家HP减至0', 'expected': '死亡动画播放 → 死亡界面出现 → 无僵尸状态'},
                    {'id': 'COMBAT-005', 'title': '多个状态效果叠加正确',      'steps': '同时施加3个Buff/Debuff', 'expected': '效果正确叠加（加法/乘法区间符合设计），无负值伤害'},
                    {'id': 'COMBAT-006', 'title': '击杀奖励正确结算',          'steps': '击杀指定敌人', 'expected': '经验/金币/掉落物正确，数值符合数值策划文档'},
                ],
            })

        # 背包/装备系统
        if 'inventory' in features or gt in ['rpg', 'action_rpg']:
            tests.append({
                'system': '背包&装备系统',
                'priority': 'P0',
                'cases': [
                    {'id': 'INV-001', 'title': '物品拾取添加到背包',          'steps': '接触掉落物品', 'expected': '物品正确添加，数量+1，背包UI更新'},
                    {'id': 'INV-002', 'title': '背包满时拾取处理',            'steps': '背包满载后尝试拾取', 'expected': '提示"背包已满"，物品不消失（保留在地面/自动丢弃提示）'},
                    {'id': 'INV-003', 'title': '装备属性正确应用',            'steps': '装备一件+10ATK的武器', 'expected': '角色ATK增加10，战斗中伤害对应提升'},
                    {'id': 'INV-004', 'title': '卸下装备属性正确移除',        'steps': '卸下已装备武器', 'expected': '属性恢复到装备前数值，无残留加成'},
                    {'id': 'INV-005', 'title': '物品使用消耗（消耗品）',      'steps': '使用一个血瓶', 'expected': 'HP恢复正确数值，血瓶数量-1，HP不超过上限'},
                    {'id': 'INV-006', 'title': '物品排序与筛选',              'steps': '背包内触发排序', 'expected': '排序结果符合规则（品质/类型/名称），无物品丢失'},
                ],
            })

        # 任务系统
        if 'quest' in features:
            tests.append({
                'system': '任务系统',
                'priority': 'P1',
                'cases': [
                    {'id': 'QUEST-001', 'title': '任务接取与追踪',            'steps': '对话NPC接取任务 → 检查任务日志', 'expected': '任务出现在日志，目标正确，地图标记出现'},
                    {'id': 'QUEST-002', 'title': '任务目标进度更新',          'steps': '击杀任务目标怪物', 'expected': '进度实时更新（如3/5），无重复计数'},
                    {'id': 'QUEST-003', 'title': '任务完成与奖励发放',        'steps': '完成所有目标 → 回报NPC', 'expected': '奖励正确发放，任务标记为完成，NPC对话变化'},
                    {'id': 'QUEST-004', 'title': '存档后任务进度保留',        'steps': '进行中任务 → 存档 → 读档', 'expected': '任务状态和进度完整恢复'},
                    {'id': 'QUEST-005', 'title': '任务链触发正确',            'steps': '完成主线任务A', 'expected': '主线任务B自动解锁/可接取，无任务链断裂'},
                ],
            })

        # IAP
        if p.get('has_iap'):
            tests.append({
                'system': '内购系统 (IAP)',
                'priority': 'P0',
                'cases': [
                    {'id': 'IAP-001', 'title': '正常购买流程完整',            'steps': '进入商城 → 选择商品 → 支付 → 检查发货', 'expected': '支付成功，道具/货币立即到账，收据有效'},
                    {'id': 'IAP-002', 'title': '支付取消后不扣款不发货',      'steps': '进入支付 → 取消', 'expected': '不扣款，道具不发放，UI正确回退'},
                    {'id': 'IAP-003', 'title': '网络中断后重启补单',          'steps': '支付成功但断网 → 重启游戏', 'expected': '游戏恢复后自动补偿道具（补单机制）'},
                    {'id': 'IAP-004', 'title': '重复购买非消耗品拦截',        'steps': '尝试二次购买已拥有的永久商品', 'expected': '提示"已拥有"，不允许重复购买'},
                    {'id': 'IAP-005', 'title': 'iOS/Android 沙盒环境测试',   'steps': '测试账号在测试环境购买所有商品', 'expected': '所有商品ID正确，价格显示正确，发货正确'},
                    {'id': 'IAP-006', 'title': '未成年人充值限额',            'steps': '设置未成年账号，尝试超额充值', 'expected': '充值被拦截（中国大陆：8-16岁月限200元）'},
                ],
            })

        # 抽卡
        if p.get('has_gacha'):
            tests.append({
                'system': '抽卡系统',
                'priority': 'P0',
                'cases': [
                    {'id': 'GACHA-001', 'title': '单抽概率符合设计值',        'steps': '服务端单抽10000次，统计各品质出现率', 'expected': 'SSR: 0.6%±0.1%，SR: 5%±0.3%，R: 94.4%±0.5%'},
                    {'id': 'GACHA-002', 'title': '软保底计数正确',            'steps': '连抽60次不出SSR，第61-89次观察概率提升', 'expected': '第61次起每抽+6%，概率曲线符合设计'},
                    {'id': 'GACHA-003', 'title': '硬保底第N抽必出',           'steps': '连抽至第90次不出SSR', 'expected': '第90次100%出SSR，不可能更多'},
                    {'id': 'GACHA-004', 'title': '保底计数跨会话保留',        'steps': '抽60次 → 关闭游戏 → 重启 → 继续抽', 'expected': '保底计数从60开始，不重置'},
                    {'id': 'GACHA-005', 'title': '概率公示与实际一致',        'steps': '对比界面显示概率与服务端概率表', 'expected': '显示数值与实际计算一致，误差0（法规要求）'},
                    {'id': 'GACHA-006', 'title': '限定池50%机制',            'steps': '连抽直至出SSR，记录是否限定', 'expected': '保底歪了后下次必出限定（歪了保底正确触发）'},
                ],
            })

        # 多人联机
        if p.get('has_multiplayer'):
            tests.append({
                'system': '多人网络',
                'priority': 'P0',
                'cases': [
                    {'id': 'NET-001', 'title': '正常连接与断开',              'steps': 'Host启动 → Client加入 → 观察同步 → Client断开', 'expected': '连接建立<3秒，断开后Host检测到，其他Client正常'},
                    {'id': 'NET-002', 'title': '弱网环境下同步稳定性',        'steps': '模拟200ms延迟+10%丢包，游玩5分钟', 'expected': '游戏可进行，无明显位置跳变，无崩溃'},
                    {'id': 'NET-003', 'title': 'Host断线后游戏处理',          'steps': 'Host断开网络', 'expected': '所有Client收到断线通知，正确返回主菜单，进度不丢失'},
                    {'id': 'NET-004', 'title': '满员房间加入拦截',            'steps': '房间满员时尝试加入', 'expected': '提示"房间已满"，不可加入'},
                    {'id': 'NET-005', 'title': '数据一致性验证',              'steps': '两台设备同时操作，观察结果', 'expected': '关键状态（血量/位置/资源）在两端一致，无偏差'},
                    {'id': 'NET-006', 'title': '作弊检测基础验证',            'steps': '修改客户端速度值，观察服务端响应', 'expected': '服务端拒绝异常数据，玩家被标记或踢出'},
                ],
            })

        # 叙事/对话
        if 'narrative' in features:
            tests.append({
                'system': '叙事&对话系统',
                'priority': 'P1',
                'cases': [
                    {'id': 'NARR-001', 'title': '对话触发与显示',             'steps': '与NPC交互', 'expected': '对话框正确弹出，文字显示完整，无截断'},
                    {'id': 'NARR-002', 'title': '分支选项功能',               'steps': '选择不同对话选项', 'expected': '每个选项触发对应分支，剧情走向正确'},
                    {'id': 'NARR-003', 'title': '语言本地化显示正确',         'steps': '切换语言设置', 'expected': '所有文本正确切换，无乱码，无字符截断，UI布局自适应'},
                    {'id': 'NARR-004', 'title': '过场动画与跳过',             'steps': '触发过场 → 尝试跳过', 'expected': '跳过后正确跳至过场后状态，无剧情错乱'},
                ],
            })

        return tests

    # ─────────────────────────────────────────────────────────────
    # 平台专项测试
    # ─────────────────────────────────────────────────────────────

    def _build_platform_tests(self, p: Dict) -> List[Dict]:
        platforms = p.get('target_platforms', ['mobile'])
        results   = []

        if 'mobile' in platforms:
            results.append({
                'platform': 'iOS & Android 移动端',
                'test_devices': [
                    '低端机（Redmi 9 / iPhone 8）：验证最低配置可运行',
                    '中端机（Redmi Note 12 / iPhone 12）：主要目标设备',
                    '高端机（Pixel 8 / iPhone 15 Pro）：验证高配效果',
                    '折叠屏（Galaxy Fold / Flip）：UI 适配验证',
                    '平板（iPad / Galaxy Tab）：UI 布局验证',
                ],
                'cases': [
                    {'id': 'MOB-001', 'title': '刘海/打孔屏适配',            'expected': 'UI元素不被遮挡，使用 SafeArea 处理'},
                    {'id': 'MOB-002', 'title': '低端设备不崩溃',             'expected': '2GB RAM 设备可运行，FPS>25（目标最低配置）'},
                    {'id': 'MOB-003', 'title': '长时间游玩不过热',           'expected': '30分钟游玩后设备温度可接受，无强制降频崩溃'},
                    {'id': 'MOB-004', 'title': '弱网/断网提示',              'expected': '网络断开有明确提示，重连后正常恢复'},
                    {'id': 'MOB-005', 'title': '横竖屏切换',                 'expected': '如支持双方向，切换时UI不错位，游戏状态保留'},
                    {'id': 'MOB-006', 'title': '系统通知覆盖',               'expected': '收到推送通知时游戏不崩溃，通知栏展开后恢复'},
                    {'id': 'MOB-007', 'title': 'Android 返回键处理',         'expected': '返回键触发"暂停/返回上级"，不直接退出游戏'},
                    {'id': 'MOB-008', 'title': 'iOS 权限请求时序',           'expected': '通知/相机/相册权限在首次需要时请求，不在启动时一次性请求'},
                    {'id': 'MOB-009', 'title': 'iPad 分屏模式',              'expected': 'iOS Slide Over / Split View 不崩溃，UI可用'},
                    {'id': 'MOB-010', 'title': '深色模式兼容',               'expected': '系统深色模式不影响游戏UI颜色（或已处理）'},
                ],
            })

        if 'pc' in platforms:
            results.append({
                'platform': 'PC (Windows/macOS)',
                'test_devices': [
                    '最低配置：GTX 1060 / i5-8400 / 8GB RAM',
                    '推荐配置：RTX 2070 / i7-9700 / 16GB RAM',
                    '超高配置：RTX 4090 / i9-13900K',
                    'macOS：M1 MacBook Air（验证 ARM 兼容性）',
                ],
                'cases': [
                    {'id': 'PC-001', 'title': '分辨率切换',                  'expected': '支持 1280×720 到 4K，UI 自适应，无拉伸'},
                    {'id': 'PC-002', 'title': '全屏/窗口模式切换',           'expected': 'Alt+Enter / 设置切换，无黑屏，分辨率保持'},
                    {'id': 'PC-003', 'title': '画质设置效果',                'expected': '低/中/高/超高每档有明显差异，低配 FPS 达标'},
                    {'id': 'PC-004', 'title': '多显示器支持',                'expected': '拖动到第二显示器正常运行，无UI位置异常'},
                    {'id': 'PC-005', 'title': '键鼠/手柄混用',               'expected': '支持切换输入方式，提示图标实时切换（键鼠↔手柄图标）'},
                    {'id': 'PC-006', 'title': 'Alt+Tab 不崩溃',              'expected': '切出/切回不崩溃，音频正确暂停/恢复'},
                    {'id': 'PC-007', 'title': '防病毒软件兼容',              'expected': 'Windows Defender 不误报，Steam 反作弊不冲突'},
                    {'id': 'PC-008', 'title': '手柄震动效果',                'expected': 'Xbox/PS 手柄震动在正确时机触发，强度合适'},
                ],
            })

        if 'console' in platforms:
            results.append({
                'platform': '主机 (PS5/Xbox/Switch)',
                'test_devices': ['PS5（必须在开发者主机上测试）', 'Xbox Series X', 'Nintendo Switch + Switch OLED'],
                'cases': [
                    {'id': 'CON-001', 'title': '首认证合规（TRC/XR/LOTCHECK）', 'expected': '所有平台认证要求通过（保存数据容量/成就/截图功能等）'},
                    {'id': 'CON-002', 'title': '加载时间（主机SSD）',           'expected': 'PS5/Xbox 冷启动<5秒，关卡切换<3秒'},
                    {'id': 'CON-003', 'title': 'HDR 显示正确',                 'expected': 'HDR 开启后画面不过曝，UI 可读性不下降'},
                    {'id': 'CON-004', 'title': 'Trophy/Achievement 解锁',      'expected': '成就在正确条件下解锁，不重复，不遗漏'},
                    {'id': 'CON-005', 'title': 'Switch 续航（便携模式）',       'expected': '便携模式电量消耗合理，不触发系统降频警告'},
                    {'id': 'CON-006', 'title': 'Switch 睡眠唤醒',               'expected': '盖上/打开 Switch，游戏正确暂停/恢复，无数据丢失'},
                    {'id': 'CON-007', 'title': 'Cross-save（若有）',            'expected': '云存档在各平台间正确同步'},
                ],
            })

        if 'webgl' in platforms:
            results.append({
                'platform': 'WebGL / 浏览器',
                'test_devices': ['Chrome 最新版', 'Firefox 最新版', 'Safari 16+（iOS/macOS）', 'Edge 最新版'],
                'cases': [
                    {'id': 'WEB-001', 'title': '首次加载时间',               'expected': '4G网络下3分钟内完全加载（包体压缩到合理大小）'},
                    {'id': 'WEB-002', 'title': 'Safari 音频自动播放',         'expected': '首次用户交互后才播放音频（浏览器限制）'},
                    {'id': 'WEB-003', 'title': '内存限制（浏览器4GB上限）',   'expected': '运行中内存不超过 2GB，无因内存不足崩溃'},
                    {'id': 'WEB-004', 'title': '全屏模式',                   'expected': 'F11/全屏按钮触发全屏，ESC正确退出'},
                    {'id': 'WEB-005', 'title': '页面刷新数据处理',            'expected': '刷新后正确回到菜单，不丢失已存档进度'},
                ],
            })

        return results

    # ─────────────────────────────────────────────────────────────
    # 性能测试
    # ─────────────────────────────────────────────────────────────

    def _build_performance_tests(self, p: Dict) -> Dict:
        platforms = p.get('target_platforms', ['mobile'])
        gt        = p['game_type']

        # 按平台的性能目标
        targets = {}
        if 'mobile' in platforms:
            targets['mobile'] = {
                'fps_target':   '≥30 FPS（稳定，低端机），≥60 FPS（中高端机）',
                'draw_calls':   '≤200（URP + SRP Batcher 后的实际值）',
                'memory_peak':  '≤1.2 GB（RAM 使用峰值，含 Unity + 系统）',
                'load_time':    '关卡加载 ≤10 秒（4G 网络 + 低端机）',
                'battery':      '1小时游玩电量消耗 ≤20%（低端机）',
                'size':         'iOS ≤4GB（商店限制），首次下载包≤200MB（OTA限制）',
            }
        if 'pc' in platforms:
            targets['pc'] = {
                'fps_target':   '≥60 FPS（推荐配置），≥30 FPS（最低配置）',
                'draw_calls':   '≤1000（PC 容忍度更高）',
                'memory_peak':  '≤4 GB（推荐配置 RAM 使用）',
                'load_time':    '关卡加载 ≤5 秒（SSD）',
                'vram':         '≤4 GB（GTX 1060 6GB 下 VRAM 使用 ≤4GB）',
            }

        # 压力测试方案
        stress_tests = [
            {
                'name': 'FPS 下限测试',
                'method': '在游戏最复杂场景（最多敌人/特效/UI同时显示）运行10分钟',
                'tool': 'Unity Profiler + 设备自带 GPU Profiler',
                'pass_criteria': f'最低帧率 ≥ {"25" if "mobile" in platforms else "30"} FPS，无超过1秒的卡顿',
            },
            {
                'name': '内存稳定性测试',
                'method': '游玩2小时（覆盖所有场景/关卡），每15分钟记录内存快照',
                'tool': 'Unity Memory Profiler',
                'pass_criteria': '内存无持续增长趋势（无内存泄漏），峰值不超过目标值',
            },
            {
                'name': '长时间运行稳定性',
                'method': '游戏连续运行4小时（可用Bot自动操作）',
                'tool': 'Automated QA / Unity Device Simulator',
                'pass_criteria': '无崩溃，无ANR，无内存溢出，FPS 无衰减',
            },
            {
                'name': '热更新性能影响',
                'method': '执行热更新 → 对比更新前后 FPS/内存/加载时间',
                'tool': '自定义脚本',
                'pass_criteria': '热更后性能指标与更新前偏差 < 10%',
                'applicable': 'hot_update' in p.get('features', []),
            },
        ]
        if p.get('has_multiplayer'):
            stress_tests.append({
                'name': '最大并发玩家压力测试',
                'method': '模拟最大房间人数同时进行高频操作，持续5分钟',
                'tool': '自定义网络压测脚本',
                'pass_criteria': '服务器 CPU < 80%，延迟 < 200ms，无玩家异常掉线',
            })

        return {
            'platform_targets': targets,
            'stress_tests': stress_tests,
            'profiling_guide': [
                'Unity Profiler：Deep Profile 找 CPU 热点，重点看 Update/Render/Physics',
                'Memory Profiler：找大对象和未释放引用，重点看 Texture/Mesh 占用',
                'Frame Debugger：分析 DrawCall 来源，找可合批对象',
                'Rendering Statistics：Draw Calls / Batches / Vertices 对照平台预算',
                '移动端专项：Android Studio Profiler (CPU/GPU/Memory) | Xcode Instruments',
            ],
            'optimization_priority': [
                '1. 减少 DrawCall：使用 SRP Batcher + GPU Instancing + Static Batching',
                '2. 纹理优化：使用 Sprite Atlas，移动端 ASTC 压缩，Mipmaps 开启',
                '3. 对象池：子弹/特效/掉落物不要每次 Instantiate/Destroy',
                '4. 协程/UniTask：避免每帧创建新任务，使用 CancellationToken 正确取消',
                '5. GC 优化：List 预分配容量，StringBuilder 复用，避免 LINQ 在热路径',
            ],
        }

    # ─────────────────────────────────────────────────────────────
    # Unity 常见 Bug 回归清单
    # ─────────────────────────────────────────────────────────────

    def _build_unity_regression_list(self, p: Dict) -> List[Dict]:
        items = [
            # 渲染
            {'category': '渲染', 'bug': 'Z-Fighting（深度冲突）', 'check': '相机近处两个面重叠时闪烁', 'fix': '调大相机 Near Clip Plane，或偏移其中一个物体'},
            {'category': '渲染', 'bug': 'GPU Skinning 导致 T-Pose', 'check': '特定设备角色呈 T-Pose', 'fix': '低端设备关闭 GPU Skinning，改用 CPU Skinning'},
            {'category': '渲染', 'bug': 'URP 材质粉红色', 'check': '换项目/平台后材质失效', 'fix': '确认 Shader 为 URP 兼容，运行 Edit → Render Pipeline → Upgrade Materials'},
            {'category': '渲染', 'bug': 'Sprite 渲染顺序错误', 'check': '2D 游戏中 Sprite 覆盖关系错误', 'fix': '使用 Sorting Layer + Order in Layer，避免依赖 Z 轴'},

            # 物理
            {'category': '物理', 'bug': '碰撞器穿透（高速物体）', 'check': '高速子弹穿过薄墙', 'fix': 'Collision Detection 改为 Continuous，或使用 Raycast 代替物理弹丸'},
            {'category': '物理', 'bug': 'Rigidbody 抖动', 'check': '在斜面或角落 Rigidbody 不停微颤', 'fix': '调大 Solver Iterations，或使用 Physics Material 调整摩擦力'},
            {'category': '物理', 'bug': '触发器漏检', 'check': 'OnTriggerEnter 偶尔不触发', 'fix': '检查 Layer Collision Matrix，确保两个物体的 Layer 有碰撞'},

            # 动画
            {'category': '动画', 'bug': 'Animator 状态机卡死', 'check': '动画停在某帧无法切换', 'fix': '检查 Transition 条件是否设置了永远不满足的参数，重置 Trigger'},
            {'category': '动画', 'bug': 'Root Motion 位移偏移', 'check': '启用 Root Motion 角色漂移', 'fix': '确认 Animator.applyRootMotion 设置，或在 OnAnimatorMove 中手动控制'},

            # 音频
            {'category': '音频', 'bug': '音频后台不静音', 'check': '切出游戏后仍有声音（移动端）', 'fix': 'Application.focusChanged 回调中暂停 AudioListener'},
            {'category': '音频', 'bug': '音频延迟（移动端）', 'check': 'Android 音频延迟>200ms', 'fix': 'Android Player Settings → DSP Buffer Size 改为 Best Latency'},

            # 内存
            {'category': '内存', 'bug': '场景切换内存未释放', 'check': '切换场景后内存持续增长', 'fix': '确认 Addressables.ReleaseInstance/Release，Resources.UnloadUnusedAssets() 调用'},
            {'category': '内存', 'bug': '事件订阅内存泄漏', 'check': '对象销毁后仍响应事件', 'fix': 'OnDisable/OnDestroy 中取消所有事件订阅'},
            {'category': '内存', 'bug': 'Texture 重复加载', 'check': '同一纹理在内存中有多份副本', 'fix': '使用 AssetLoader 缓存 Handle，避免重复 LoadAssetAsync'},

            # 移动端专项
            {'category': '移动端', 'bug': 'iOS App Transport Security 拦截', 'check': 'HTTP 请求被拒绝', 'fix': 'Info.plist 添加 NSAppTransportSecurity，或改用 HTTPS'},
            {'category': '移动端', 'bug': 'Android 权限崩溃', 'check': '访问文件/相机前未检查权限', 'fix': '运行时动态请求权限，处理拒绝情况'},
            {'category': '移动端', 'bug': 'IL2CPP 代码剥离导致崩溃', 'check': 'Release 包中某功能在 Editor 正常但 Build 后崩溃', 'fix': '添加 link.xml 保护被错误剥离的类型'},
        ]

        # 多人专项
        if p.get('has_multiplayer'):
            items += [
                {'category': '网络', 'bug': '竞态条件（Race Condition）', 'check': '两个客户端同时操作同一对象导致状态不一致', 'fix': '服务端权威，仅 Host 修改状态，Client 发送请求'},
                {'category': '网络', 'bug': 'NetworkObject 重复 Spawn', 'check': '同一个对象在某些客户端显示两次', 'fix': '确认 Spawn/Despawn 仅在 Server 端调用'},
            ]

        if p.get('has_iap'):
            items.append({'category': 'IAP', 'bug': '沙盒收据在 Production 环境验证', 'check': '测试环境的购买在生产后台出现错误', 'fix': '分离沙盒/生产验证逻辑，服务端自动区分环境'})

        return items

    # ─────────────────────────────────────────────────────────────
    # Bug 严重等级矩阵
    # ─────────────────────────────────────────────────────────────

    def _build_bug_matrix(self) -> Dict:
        return {
            'severity_levels': [
                {
                    'level': 'P0 — 致命',
                    'color': 'red',
                    'definition': '游戏崩溃 / 数据丢失 / 支付异常 / 法规违规',
                    'examples': ['启动崩溃', '存档数据被清空', '付款成功但道具未到账', '未成年人绕过充值限制'],
                    'response': '立即停止当前迭代，全员 Fix，24小时内发布热更',
                    'max_open_to_release': 0,
                },
                {
                    'level': 'P1 — 严重',
                    'color': 'orange',
                    'definition': '核心功能完全不可用，无合理绕过方案',
                    'examples': ['主线任务无法推进', '登录功能失效', 'Boss 战无法开始/结束'],
                    'response': '当前 Sprint 必须修复，48-72小时内',
                    'max_open_to_release': 0,
                },
                {
                    'level': 'P2 — 中等',
                    'color': 'yellow',
                    'definition': '功能有缺陷但有绕过方案，影响体验但不阻塞游戏',
                    'examples': ['UI 元素重叠', '音频偶尔缺失', '动画过渡有跳帧'],
                    'response': '下个 Sprint 修复',
                    'max_open_to_release': 20,
                },
                {
                    'level': 'P3 — 轻微',
                    'color': 'green',
                    'definition': '视觉瑕疵、文案错误、轻微体验问题',
                    'examples': ['拼写错误', '边缘情况下视觉穿插', '非主流程中的UI间距不对'],
                    'response': '积累到优化版本统一处理',
                    'max_open_to_release': '无限制',
                },
            ],
            'bug_report_template': {
                '标题':     '[系统][严重度] 简洁描述问题',
                '环境':     '设备型号 / OS版本 / 游戏版本 / 网络环境',
                '步骤':     '1.xxx 2.xxx 3.xxx（最少步骤复现）',
                '实际结果': '发生了什么（截图/视频必须附上）',
                '期望结果': '应该发生什么',
                '复现率':   '10/10 必现 / 3/10 偶现 / 1/10 罕见',
                '日志':     '崩溃日志/控制台报错（粘贴相关行）',
            },
        }

    # ─────────────────────────────────────────────────────────────
    # 发布清单
    # ─────────────────────────────────────────────────────────────

    def _build_release_checklist(self, p: Dict) -> List[Dict]:
        platforms = p.get('target_platforms', ['mobile'])
        checklists = []

        # 通用
        checklists.append({
            'category': '通用发布前检查',
            'items': [
                {'item': '所有 P0/P1 Bug 关闭', 'owner': 'QA', 'critical': True},
                {'item': 'Build 版本号递增（Version + Build Number）', 'owner': '开发', 'critical': True},
                {'item': 'Debug 日志关闭（Debug.Log 不输出到发布版本）', 'owner': '开发', 'critical': False},
                {'item': 'Cheat/Debug 工具在发布版本中关闭', 'owner': '开发', 'critical': True},
                {'item': '所有开发测试账号从发布版本移除', 'owner': '开发', 'critical': True},
                {'item': '隐私政策/用户协议链接有效且最新', 'owner': '产品', 'critical': True},
                {'item': 'GDPR / COPPA 合规实现已测试', 'owner': 'QA', 'critical': True},
                {'item': '崩溃上报工具接入并验证（Firebase / Sentry）', 'owner': '开发', 'critical': False},
                {'item': '数据分析事件打点验证（注册/付款/关卡完成等核心事件）', 'owner': '开发', 'critical': False},
                {'item': '所有第三方 SDK 已更新到最新稳定版本', 'owner': '开发', 'critical': False},
            ],
        })

        if 'mobile' in platforms:
            checklists.append({
                'category': 'App Store (iOS) 提审清单',
                'items': [
                    {'item': 'Bundle ID 与证书匹配', 'owner': '开发', 'critical': True},
                    {'item': '所有屏幕尺寸截图已准备（iPhone 6.5" / iPad 12.9"）', 'owner': '产品', 'critical': True},
                    {'item': 'App Store Connect 填写：年龄评级、内容描述（含 IAP）', 'owner': '产品', 'critical': True},
                    {'item': '隐私数据声明（NSPrivacyUsageDescription）已填写', 'owner': '开发', 'critical': True},
                    {'item': 'App Tracking Transparency (ATT) 实现（iOS 14.5+）', 'owner': '开发', 'critical': True},
                    {'item': 'TestFlight 内测已完成，Beta 测试者反馈已处理', 'owner': 'QA', 'critical': False},
                    {'item': '应用内购商品在 App Store Connect 已配置并激活', 'owner': '产品', 'critical': True},
                ],
            })

            checklists.append({
                'category': 'Google Play (Android) 提审清单',
                'items': [
                    {'item': 'keystore 文件已备份（丢失则无法更新）', 'owner': '开发', 'critical': True},
                    {'item': 'AAB (Android App Bundle) 格式打包（非 APK）', 'owner': '开发', 'critical': True},
                    {'item': '目标 API Level ≥ 34（Google Play 2024年要求）', 'owner': '开发', 'critical': True},
                    {'item': '内容评级问卷已填写（IARC）', 'owner': '产品', 'critical': True},
                    {'item': '数据安全表单（Data Safety）已填写', 'owner': '产品', 'critical': True},
                    {'item': '权限声明已最小化（仅申请实际需要的权限）', 'owner': '开发', 'critical': False},
                    {'item': '中国大陆版本：版号/ICP备案/防沉迷系统验证', 'owner': '产品', 'critical': True},
                ],
            })

        if 'pc' in platforms:
            checklists.append({
                'category': 'Steam 发布清单',
                'items': [
                    {'item': 'Steam App ID 已配置到游戏中', 'owner': '开发', 'critical': True},
                    {'item': 'Steam 成就已实现并测试', 'owner': '开发', 'critical': False},
                    {'item': 'Steam Cloud 存档（可选但推荐）', 'owner': '开发', 'critical': False},
                    {'item': '所有 Store 资产已上传（主图/截图/预告片/Capsule 图）', 'owner': '产品', 'critical': True},
                    {'item': 'Steam 页面描述/标签/系统要求已填写', 'owner': '产品', 'critical': True},
                    {'item': 'Steam 发布前 Release Check 已通过', 'owner': 'QA', 'critical': True},
                    {'item': '价格已设置，所有地区价格已审核', 'owner': '产品', 'critical': True},
                ],
            })

        if p.get('has_iap'):
            checklists.append({
                'category': 'IAP 发布清单',
                'items': [
                    {'item': '所有商品 ID 在平台后台已配置并激活', 'owner': '产品', 'critical': True},
                    {'item': '支付服务端验证已部署并测试', 'owner': '后端', 'critical': True},
                    {'item': '补单机制已测试（断网→重启→补偿）', 'owner': 'QA', 'critical': True},
                    {'item': '价格显示格式符合各地区本地化（¥/$/€）', 'owner': '产品', 'critical': False},
                    {'item': '中国大陆：未成年人充值限制已实现并测试', 'owner': '开发/QA', 'critical': True},
                ],
            })

        return checklists

    # ─────────────────────────────────────────────────────────────
    # 自动化测试建议
    # ─────────────────────────────────────────────────────────────

    def _build_automation_plan(self, p: Dict) -> Dict:
        team = p['team_size']
        return {
            'recommendation': self._auto_recommendation(team),
            'unit_tests': {
                'framework': 'Unity Test Framework (NUnit)',
                'targets': [
                    '伤害计算函数（输入ATK/DEF/倍率，验证输出伤害）',
                    '经济公式（日收益计算、收支平衡验证）',
                    '存档序列化/反序列化（存入→读出→对比）',
                    '背包操作（添加/删除/堆叠/满载）',
                    '概率函数（大数量验证分布是否符合设计）',
                ],
                'example': '''[Test]
public void DamageCalculation_WithCrit_ReturnsCorrectValue()
{
    var ctx = new DamageContext
    {
        ATK = 100, SkillMultiplier = 2.5f,
        DEF = 50, CritRate = 1f, CritDmgBonus = 0.5f  // 100% crit, +50% crit dmg
    };
    float dmg = CombatSystem.CalculateDamage(ctx);
    // Expected: 100 × 2.5 × (1 - 50/(50+600)) × 1.5 ≈ 288.46
    Assert.AreApproximatelyEqual(288.46f, dmg, delta: 1f);
}''',
            },
            'playmode_tests': {
                'framework': 'Unity Test Framework PlayMode + Automated QA',
                'targets': [
                    '冒烟测试：启动→主菜单→新游戏→加载完成→不崩溃',
                    '主流程：完成前3个教学步骤',
                    '存读档：保存→退出→读取→状态一致',
                ],
            },
            'ci_recommendation': {
                'tool':    'GitHub Actions / Jenkins / Unity Cloud Build',
                'trigger': 'Push 到 develop/main 分支',
                'steps': [
                    '1. 运行所有 EditMode Unit Tests',
                    '2. 构建 Development Build（iOS/Android/PC）',
                    '3. 运行 PlayMode 冒烟测试',
                    '4. 生成测试报告，失败则阻断合并',
                ],
            },
        }

    def _auto_recommendation(self, team: str) -> str:
        recs = {
            'solo':   '仅建议手写核心计算函数的单元测试（伤害/概率），自动化成本不值得',
            'small':  '建立冒烟测试（每次Build自动运行），核心计算函数单元测试，覆盖率目标40%',
            'medium': '完整单元测试套件 + CI/CD 集成，每次PR自动跑测试，目标60%覆盖率',
            'large':  '完整自动化体系：单元测试 + 集成测试 + UI 自动化 + 性能基准，目标80%',
        }
        return recs.get(team, recs['small'])

    # ─────────────────────────────────────────────────────────────
    # 辅助
    # ─────────────────────────────────────────────────────────────

    def _normalize(self, raw: Dict) -> Dict:
        p = dict(raw)
        p.setdefault('game_name', 'My Game')
        p.setdefault('game_type', 'rpg')
        p.setdefault('target_platforms', ['mobile'])
        p.setdefault('features', [])
        p.setdefault('team_size', 'small')
        p.setdefault('has_multiplayer', False)
        p.setdefault('has_iap', False)
        p.setdefault('has_gacha', False)
        p.setdefault('max_level', 30)
        p.setdefault('monetization_type', 'f2p')
        p.setdefault('has_hot_update', 'hot_update' in p.get('features', []))
        # 标准化
        if 'multiplayer' in p.get('features', []):
            p['has_multiplayer'] = True
        if 'iap' in p.get('features', []):
            p['has_iap'] = True
        return p
