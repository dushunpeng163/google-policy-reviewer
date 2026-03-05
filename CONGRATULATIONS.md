# Unity 游戏全球合规平台 v5.0 — 构建完成

## 系统能力概览

### 双模式工作流
- **Mode A**：新游戏合规开发指南（路线图 + 清单 + 技术要点）
- **Mode B**：现有游戏合规审计（代码扫描 + 法规检查 + 风险报告）

### 政策智能监控
- RSS 监控：Apple Developer News + Android Developers Blog
- 页面哈希检测：22 条核心政策规则实时追踪
- LLM 自动分析：Claude / GPT-4o 解读政策变化含义

### 全流程 Web 界面
- 双模式入口，可视化表单
- GUI 文件夹选择（macOS / Windows / Linux）
- 政策管理弹窗（状态 / 配置 / 检查 三 Tab）
- LLM API Key 界面内配置，即时生效

### 引擎模块
| 引擎 | 职责 |
|------|------|
| dev_guide.py | 新游戏合规路线图生成 |
| unified_audit.py | 综合审计报告 |
| code_scanner.py | Unity / iOS / Android 静态扫描 |
| code_template_generator.py | 合规代码模板（C# / Swift / Kotlin） |
| policy_monitor.py | RSS + 页面哈希监控 |
| policy_diff_analyzer.py | LLM 政策变化解读 |

## 版本历史

| 版本 | 主要内容 |
|------|---------|
| v5.1.0 | 更新 SKILL.md，AI 角色对齐 v5.0 能力 |
| v5.0.0 | 政策管理三 Tab + Web 内 LLM 配置 + 主动检查 |
| v4.0.x | 双模式入口 Web 界面重构 |
| v3.0.0 | 代码扫描引擎 + 模板生成器 |
| v2.x | 企业级 API + 可视化仪表板（历史版本） |
