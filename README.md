# Unity 游戏全球合规平台 v5.3

帮助 Unity 游戏开发者在 **App Store + Google Play** 双平台合规上架，覆盖美国、欧盟、英国等主流市场，并持续跟踪平台政策变化。

[English Documentation](README_EN.md)

---

## 快速启动

```bash
# 安装依赖
pip3 install flask

# 启动 Web 界面
python3 launcher.py --mode web
# 浏览器打开 http://localhost:8080
```

---

## 两大核心功能

### 模式 A · 新游戏开发合规指南

输入游戏基本信息，生成完整合规开发路线图：

- 适用法规分析（GDPR / COPPA / CCPA / UK AADC）
- 分阶段实现清单（法律 → 账号 → 隐私 → 内购 → 广告 → 测试）
- App Store Connect 和 Google Play Console 配置指南
- Unity C# / iOS Swift / Android Kotlin 技术实现要点

### 模式 B · 现有游戏合规审计

扫描现有 Unity 项目代码，输出合规问题报告：

- 代码级问题定位（文件路径 + 行号 + 修复建议）
- 法规符合性检查（数据收集、儿童保护、用户权利）
- 平台政策检查（22 条核心规则）
- 风险分级报告（critical / high / medium / low）

---

## 政策管理

点击 Web 界面右上角「📋 政策管理」，共四个 Tab：

| Tab | 功能 |
|-----|------|
| 📊 状态 | 22 条政策规则新鲜度；LLM 检测到变化时显示告警卡片 |
| ⚙️ 配置 | 设置 LLM API Key 和远程规则更新 URL（热生效，无需重启） |
| 🔍 检查 | 触发 RSS + 页面哈希监控 + LLM 自动分析（后台运行，切 Tab 不中断） |
| ⏰ 定时 | 配置自动定时检查频率；查看通知历史 |

### 政策变化追踪闭环

```
RSS / 页面哈希检测到变化
        ↓
LLM 分析变化内容，识别受影响的规则
        ↓
受影响规则自动标记为「待复核」，在状态 Tab 显示告警
        ↓
开发者查看告警，点击「标记已复核」
        ↓
告警清除，规则新鲜度恢复
```

此闭环按照你设定的频率（每小时 / 每天 / 每周）自动运行。  
未配置 LLM 时，仍可检测页面变化，但无法自动标记受影响规则。

---

## LLM 配置（可选）

在「配置」Tab 中直接填写，或在项目根目录创建 `.env` 文件：

```bash
ANTHROPIC_API_KEY=sk-ant-xxx   # 推荐（Claude）
OPENAI_API_KEY=sk-xxx          # 备选（GPT-4o）
```

保存后立即生效，无需重启服务器。

---

## 规则热更新

无需重启即可更新合规规则：

- **本地模式**：直接编辑 `config/compliance-rules.yaml`，系统自动检测文件变化并重载
- **远程模式**：在「配置」Tab 设置 `RULES_UPDATE_URL`，系统自动拉取远端 YAML 文件并应用更新

---

## CLI 使用

```bash
# 新游戏合规指南
python3 launcher.py --mode guide

# 现有项目审计
python3 launcher.py --mode audit --path /your/unity/project

# 政策监控
python3 launcher.py --mode check-policies --rss
python3 launcher.py --mode check-policies --watch

# 仅启动 Web 服务器
python3 launcher.py --mode web
```

---

## API 接口

服务运行在 8080 端口（默认）：

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/health` | 服务健康状态和规则版本 |
| POST | `/api/v1/guide/new-game` | 生成新游戏合规指南 |
| POST | `/api/v1/audit/game` | 审计现有游戏项目 |
| GET | `/api/v1/policies/freshness` | 获取 22 条规则新鲜度报告 |
| POST | `/api/v1/policies/run-check` | 触发政策检查（异步，返回 `job_id`） |
| GET | `/api/v1/policies/check-status/<job_id>` | 轮询异步检查结果 |
| POST | `/api/v1/policies/mark-verified` | 人工标记规则已复核（清除告警） |
| GET/POST | `/api/v1/rules/update` | 查询或触发规则热更新 |
| GET/POST | `/api/v1/policies/scheduler` | 查询或配置定时检查 |
| GET | `/api/v1/notifications` | 获取通知列表和未读数量 |
| POST | `/api/v1/notifications/read` | 标记通知为已读 |
| POST | `/api/v1/policies/save-config` | 保存 LLM Key / 规则 URL 到 `.env` |

---

## 项目结构

```
launcher.py                      主入口
api/compliance_api.py            Flask API 服务器
web_interface.html               Web 界面（单文件）
engines/
  ├── dev_guide.py               新游戏合规路线图
  ├── unified_audit.py           现有游戏综合审计
  ├── code_scanner.py            静态代码扫描
  ├── code_template_generator.py 合规代码模板
  ├── advanced_rule_engine.py    核心合规规则引擎
  ├── policy_monitor.py          RSS + 页面哈希监控
  └── policy_diff_analyzer.py   LLM 政策变化解读
config/
  └── compliance-rules.yaml     规则定义（支持热更新）
references/                      政策知识库
policy_versions.json             22 条规则版本追踪（含变化告警）
.env                             API Keys（手动创建，不提交 Git）
```

---

## 覆盖范围

**法规**：GDPR · COPPA · CCPA · UK AADC

**平台**：App Store（Apple）· Google Play（Google）

**市场**：美国 · 欧盟 · 英国 · 加拿大 · 澳大利亚

**技术栈**：Unity C# · iOS Swift · Android Kotlin

---

## 依赖

- Python 3.8+
- Flask（`pip3 install flask`）
- 可选：`anthropic` 或 `openai`（LLM 功能）
- 可选：`python-dotenv`（`.env` 文件支持）

```bash
pip3 install -r requirements.txt
```

---

## 许可证

MIT License — 详见 [LICENSE](LICENSE)
