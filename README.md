# Unity 游戏全球合规平台 v5.0

帮助 Unity 游戏开发者在 **App Store + Google Play** 双平台合规上架，覆盖美国、欧盟、英国等主流市场。

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
- Unity 技术实现要点

### 模式 B · 现有游戏合规审计

扫描现有 Unity 项目代码，输出合规问题报告：

- 代码级问题定位（文件路径 + 行号 + 修复建议）
- 法规符合性检查（数据收集、儿童保护、用户权利）
- 平台政策检查（22 条核心规则）
- 风险分级报告（critical / high / medium / low）

---

## 政策管理

点击 Web 界面右上角「📋 政策管理」：

| Tab | 功能 |
|-----|------|
| 📊 状态 | 查看 22 条政策规则的新鲜度 |
| ⚙️ 配置 | 输入 LLM API Key（即时生效，无需重启） |
| 🔍 检查 | 一键触发 RSS + 页面变化检测 + LLM 自动分析 |

**LLM 配置**（可选，用于自动解读政策变化含义）：

```bash
# 在项目根目录创建 .env 文件
ANTHROPIC_API_KEY=sk-ant-xxx   # 推荐
OPENAI_API_KEY=sk-xxx          # 备选
```

---

## 项目结构

```
launcher.py                   主入口
api/compliance_api.py         Flask API 服务器
web_interface.html            Web 界面
engines/
  ├── dev_guide.py            新游戏合规路线图
  ├── unified_audit.py        现有游戏综合审计
  ├── code_scanner.py         静态代码扫描
  ├── code_template_generator.py  合规代码模板
  ├── policy_monitor.py       RSS + 页面哈希监控
  └── policy_diff_analyzer.py LLM 政策变化解读
references/                   政策知识库
policy_versions.json          22 条规则版本记录
SKILL.md                      Cursor AI 角色定义
```

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
```

---

## 覆盖范围

**法规**：GDPR · COPPA · CCPA · UK AADC

**平台**：App Store · Google Play

**市场**：美国 · 欧盟 · 英国 · 加拿大 · 澳大利亚

**技术栈**：Unity C# · iOS Swift · Android Kotlin
