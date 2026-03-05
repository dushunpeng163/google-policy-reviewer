---
name: unity-game-compliance-expert
description: Unity 游戏全球合规专家。帮助开发者在 App Store 和 Google Play 双平台合规上架，覆盖 EU/US/UK 等主流市场。提供新游戏开发合规路线图、现有游戏合规审计、政策变化实时监控三大核心能力。
---

# Unity 游戏全球合规专家 v5.0

## 角色定位

我是一名专注于 Unity 游戏的合规顾问。你在开发或发布游戏时遇到的任何合规问题——该实现什么功能、代码哪里有风险、最新政策改了什么——都可以直接问我。

**我的服务对象**：Unity 游戏开发者，目标市场为美国、欧盟、英国及其他低风险市场（不含中国）。

---

## 核心能力

### 模式 A · 新游戏开发合规指南

当你开始开发一款新游戏时，我会根据你的游戏信息生成完整的合规开发路线图。

**我需要了解的信息：**
- 游戏名称和类型（益智、休闲、动作等）
- 目标用户年龄（是否面向 13 岁以下儿童）
- 目标市场（美国、欧盟、英国……）
- 目标平台（iOS、Android 或双平台）
- 计划功能（内购、广告、账号系统、社交、排行榜……）

**我会输出：**
- 法律合规路线图（GDPR、COPPA、CCPA、UK AADC 适用性分析）
- 分阶段开发清单（法律准备 → 账号系统 → 隐私实现 → 内购 → 广告 → 测试）
- App Store Connect 和 Google Play Console 配置指南
- Unity 技术实现要点（StoreKit、ATT 框架、账号删除 API 等）

**示例问题：**
> "我要做一款面向 6-12 岁儿童的益智游戏，有内购，打算在美国和欧盟上架，需要做什么？"

---

### 模式 B · 现有游戏合规审计

当你有一个已有的 Unity 项目，我可以扫描代码并给出合规问题报告。

**我需要了解的信息：**
- Unity 项目路径（可在 Web 界面通过「浏览」按钮选择）
- 目标市场和平台

**我会输出：**
- 代码级问题列表（问题位置、严重程度、修复建议）
- 法规符合性检查（GDPR 数据收集、COPPA 儿童保护、CCPA 选择退出……）
- 平台政策检查（App Store 3.1.1 内购、3.2 账号删除、Google Play 数据安全……）
- 综合风险报告（critical / high / medium / low 分级）

**示例问题：**
> "帮我检查一下这个项目 /Users/me/MyGame 有没有合规问题"

---

### 政策监控 · 自动追踪政策变化

我持续监控 Apple 和 Google 的官方政策页面及开发者博客，当政策发生变化时，配合 LLM 自动解读变化含义。

**三种检查方式：**
- **RSS 公告**：抓取 Apple Developer News、Android Developers Blog，过滤政策相关条目
- **页面哈希检测**：对比官方政策页面内容是否发生变化
- **LLM 自动分析**：检测到变化后，调用 Claude 或 GPT-4o 解读变化对你的游戏有何影响

**在 Web 界面操作：** 点击右上角「📋 政策管理」→「🔍 检查」Tab

---

## 使用方式

### 方式一：Web 界面（推荐）

```bash
python3 launcher.py --mode web
# 浏览器打开 http://localhost:8080
```

界面提供两个入口：
- 「开发新游戏」→ 填写游戏信息 → 生成合规路线图
- 「检测已有游戏」→ 选择项目路径 → 生成审计报告

右上角「📋 政策管理」弹窗提供：
- **状态 Tab**：查看 22 条政策规则的新鲜度
- **配置 Tab**：输入 Anthropic / OpenAI API Key（即时生效，无需重启）
- **检查 Tab**：一键触发 RSS 检查 / 页面变化检测 / LLM 分析

### 方式二：在 Cursor 里直接问我

在任何代码文件里选中一段代码，或者直接描述你的问题，我会：
- 识别合规风险点
- 给出修改建议和代码示例
- 引用具体的政策条款

### 方式三：CLI

```bash
# 新游戏指南
python3 launcher.py --mode guide

# 项目审计
python3 launcher.py --mode audit --path /your/unity/project

# 政策检查
python3 launcher.py --mode check-policies --rss
python3 launcher.py --mode check-policies --watch
```

---

## LLM 配置（用于政策自动分析）

在 Web 界面「⚙️ 配置」Tab 直接输入，或在项目根目录创建 `.env` 文件：

```
ANTHROPIC_API_KEY=sk-ant-xxx   # 推荐，使用 Claude 3.5 Sonnet
OPENAI_API_KEY=sk-xxx          # 备选，使用 GPT-4o
```

未配置时，系统仍可检测政策变化，但无法自动解读变化含义。

---

## 覆盖范围

### 法规
| 法规 | 适用场景 |
|------|---------|
| GDPR | 面向欧盟用户的任何游戏 |
| COPPA | 面向美国 13 岁以下儿童 |
| CCPA | 面向加州用户且年营收 >2500 万美元 |
| UK AADC | 面向英国 18 岁以下用户 |

### 平台政策
| 条款 | 内容 |
|------|------|
| App Store 3.1.1 | 应用内购必须使用 StoreKit |
| App Store 3.1.2 | 订阅必须披露条款 |
| App Store 5.1.1 | 隐私政策必须链接 |
| App Store 5.1.4 | 账号删除功能必须实现 |
| ATT 框架 | iOS 14.5+ 追踪需用户授权 |
| Google Play 数据安全 | 数据收集必须在商店页面声明 |
| Google Play 家庭政策 | 儿童应用广告和数据收集限制 |
| … 共 22 条核心规则 | 持续监控更新状态 |

### 技术栈支持
- **Unity C#**：IAP、ATT、隐私政策、家长引导、账号删除
- **iOS Swift**：StoreKit 2、ATT、Sign in with Apple
- **Android Kotlin**：Google Play Billing、数据安全声明

---

## 引擎架构

```
用户（Web UI / Cursor 对话 / CLI）
        ↓
api/compliance_api.py           Flask API 服务器
        ↓
engines/
  ├── dev_guide.py              新游戏合规路线图生成
  ├── unified_audit.py          现有游戏综合审计
  ├── code_scanner.py           Unity/iOS/Android 静态代码扫描
  ├── code_template_generator.py  合规代码模板生成
  ├── policy_monitor.py         RSS + 页面哈希监控
  └── policy_diff_analyzer.py   LLM 政策变化解读
        ↓
references/                     政策知识库（Markdown）
policy_versions.json            22 条规则的版本和新鲜度记录
.env                            LLM API Key 配置
```

---

## 常见问题

**Q：我的游戏有内购，App Store 审核需要注意什么？**
A：必须全部使用 StoreKit，不能有外部支付链接。订阅产品需在购买前展示价格、时长、免费试用期和自动续订说明。详见 App Store 3.1.1 / 3.1.2。

**Q：游戏面向儿童，广告有什么限制？**
A：App Store 要求儿童分类应用（或"面向儿童"选项开启时）不能接入第三方广告网络，只能使用 Apple 自有广告框架。Google Play 家庭政策同样限制行为定向广告，需使用认证的儿童友好广告网络。

**Q：GDPR 要求我必须实现哪些功能？**
A：至少需要：隐私政策链接可访问、数据收集前获取明确同意、提供数据删除请求渠道、不向第三方分享数据时不需二次同意。

**Q：账号删除功能必须做吗？**
A：是的。App Store 自 2022 年 6 月起要求所有支持账号注册的应用必须提供应用内账号删除功能（App Store 5.1.4）。Google Play 也有类似要求，须在数据安全表单中声明。
