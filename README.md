# 游戏开发 AI 工作坊

以 AI 驱动的游戏开发全流程工作坊。7 个专业角色覆盖从设计到上线的完整链路，每个角色都由真实 LLM 提供支持，给出针对你具体游戏的定制分析。

---

## 角色阵容

| 角色 | 职责 | 核心输出 |
|------|------|---------|
| 🏗️ Unity 架构师 | 技术选型与系统设计 | 游戏框架、渲染管线、网络方案、性能预算 |
| 🗺️ 系统策划师 | 玩法骨架设计 | 核心循环、MDA 分析、系统交互图 |
| 📊 数值策划师 | 数值体系建模 | 战斗公式、成长曲线、经济模型、Gacha 概率 |
| 📖 关卡叙事策划师 | 关卡与故事设计 | 叙事结构、关卡序列、难度曲线、教程设计 |
| ⚙️ 技术实现向导 | 代码脚手架生成 | 项目目录、C# 接口、DI 注册、编码规范 |
| 🧪 QA 工程师 | 测试质量保障 | 测试计划、平台专项用例、Bug 矩阵、发布清单 |
| 📈 数据分析师 | 数据驱动迭代 | KPI 体系、埋点方案、留存/付费分析、A/B 测试 |

---

## 快速启动

**第一步：安装依赖**

```bash
pip install -r requirements.txt
```

**第二步：配置 API Key**

```bash
cp .env.example .env
# 编辑 .env，填入：
# ANTHROPIC_API_KEY=sk-ant-你的Key
```

**第三步：启动**

```bash
python launcher.py --mode web
# 浏览器打开 http://localhost:8080
```

---

## 工作方式

```
填写游戏描述（名称 / 类型 / 平台 / 功能）
        ↓
选择角色 → 点击提交
        ↓
LLM 以该角色的专业视角实时分析
        ↓
流式 Markdown 输出（打字机效果）
        ↓
复制结果 → 团队讨论 → 下一个角色
```

每个角色都有专属的系统提示词（知识库），包含该领域的决策框架、行业基准和判断标准——不是通用 AI，是有专业背景的定制角色。

---

## 两种使用方式

### Web 工作坊（本项目）

适合：需要完整报告、团队分享、正式文档

```bash
python launcher.py --mode web
```

### Cursor Agent Skills

适合：开发过程中实时讨论、追问、让 AI 直接动手写代码

7 个 Agent Skills 安装在 `~/.agents/skills/`，在 Cursor 对话中自动激活：

```
unity-architect            → Unity 技术选型
game-system-designer       → 系统策划
game-numerical-designer    → 数值策划
game-level-narrative-designer → 关卡叙事
unity-implementation-wizard → 代码实现
game-qa-engineer           → QA 测试
game-data-analyst          → 数据分析
```

---

## Web 工作坊 vs Agent Skills

| | Web 工作坊 | Agent Skills |
|--|-----------|-------------|
| **场景** | 正式立项、阶段汇报、团队共享 | 开发过程中随时发问 |
| **输出形式** | 完整结构化报告（Markdown）| 对话式，可追问、可深挖 |
| **与代码互动** | 不能直接操作文件 | 可以直接读代码、生成文件、修改实现 |
| **上下文** | 每次填表重新开始 | 保留完整对话历史，可持续迭代 |
| **适合谁看** | 产品、策划、PM | 开发者本人 |

### 推荐配合流程

```
立项阶段
  └─ Web 工作坊：Unity 架构师 → 生成完整技术选型报告（给团队看）

开发阶段
  └─ Cursor Agent Skills：Unity 架构师 / 技术实现向导
       → 边写代码边追问，让 AI 直接生成接口、修改实现

测试阶段
  └─ Web 工作坊：QA 工程师 → 生成正式测试计划文档
  └─ Agent Skills：QA 工程师 → 针对具体代码生成单测、发现边界 case

上线后
  └─ Web 工作坊：数据分析师 → 生成 KPI 体系和埋点方案
  └─ Agent Skills：数据分析师 → 结合真实数据讨论留存下滑原因、调整策略
```

两者共享相同的角色知识库，Web 工作坊适合"出报告"，Agent Skills 适合"做事情"。

---

## 项目结构

```
launcher.py                   启动入口
api/compliance_api.py         Flask API（含 7 个流式 AI 端点）
web_interface.html            Web 界面（单文件）
engines/
  ├── llm_client.py           LLM 统一接口（Claude / OpenAI）
  ├── system_prompts.py       7 个角色系统提示词
  ├── unity_architect_expert.py
  ├── system_designer_expert.py
  ├── numerical_designer_expert.py
  ├── level_narrative_designer_expert.py
  ├── implementation_wizard_expert.py
  ├── qa_engineer_expert.py
  └── data_analyst_expert.py
.env.example                  配置模板
```

---

## AI 端点

服务运行在 `http://localhost:8080`：

| 方法 | 路径 | 角色 |
|------|------|------|
| POST | `/api/v1/ai/architect` | Unity 架构师 |
| POST | `/api/v1/ai/system-designer` | 系统策划师 |
| POST | `/api/v1/ai/numerical-designer` | 数值策划师 |
| POST | `/api/v1/ai/level-narrative` | 关卡叙事策划师 |
| POST | `/api/v1/ai/impl-wizard` | 技术实现向导 |
| POST | `/api/v1/ai/qa-engineer` | QA 工程师 |
| POST | `/api/v1/ai/data-analyst` | 数据分析师 |

所有端点接受 `{"game_profile": {...}}` JSON，返回 `text/event-stream` SSE 流。

**请求示例：**

```bash
curl -X POST http://localhost:8080/api/v1/ai/architect \
  -H "Content-Type: application/json" \
  -d '{
    "game_profile": {
      "game_name": "我的RPG",
      "game_type": "rpg",
      "target_platforms": ["mobile"],
      "features": ["multiplayer", "iap", "gacha"],
      "team_size": "small"
    }
  }'
```

---

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|-------|
| `LLM_PROVIDER` | `anthropic` 或 `openai` | `anthropic` |
| `ANTHROPIC_API_KEY` | Claude API Key | — |
| `OPENAI_API_KEY` | OpenAI API Key | — |
| `LLM_MODEL` | 模型名称 | `claude-sonnet-4-5` / `gpt-4o` |
| `LLM_MAX_TOKENS` | 最大输出 Token | `4096` |

未配置 API Key 时，系统不会崩溃，而是在输出区域显示配置引导。

---

## 依赖

Python 3.8+，详见 [`requirements.txt`](requirements.txt)。
