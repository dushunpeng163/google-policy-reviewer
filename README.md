# Google Policy Reviewer

一个专业的Google开发者政策集成审核员技能，帮助Android应用开发者确保应用符合Google的各项政策要求。

## 🎯 功能特色

### 📋 全面政策覆盖
- **Google Play Store政策** - 应用内容、安全、技术要求
- **AdSense广告政策** - 广告展示规范、用户体验标准  
- **数据隐私合规** - GDPR、COPPA、中国个人信息保护法
- **技术合规检查** - API级别、64位架构、权限使用

### 🤖 智能审核流程
- **交互式信息收集** - 根据应用特点定制检查
- **自动合规性验证** - 基于最新政策规则检查
- **风险等级评估** - 按严重程度分类问题
- **具体整改建议** - 提供可操作的解决方案

### 📊 专业报告输出
- 详细的Markdown格式审核报告
- 按政策类型分类的问题清单
- 优先级排序的整改建议
- 风险评估和后续跟进计划

## 🚀 快速开始

### 安装方法

#### 方法一：OpenClaw用户
```bash
# 下载技能文件
curl -O https://github.com/yourusername/google-policy-reviewer/releases/latest/download/google-policy-reviewer.skill

# 安装技能（复制到OpenClaw技能目录）
cp google-policy-reviewer.skill ~/.openclaw/skills/
```

#### 方法二：通用AI Agent
```bash
# 克隆仓库
git clone https://github.com/yourusername/google-policy-reviewer.git

# 使用 skills CLI 安装
npx skills add ./google-policy-reviewer -a openclaw
# 或安装到其他支持的AI agents
npx skills add ./google-policy-reviewer -a cursor -a claude-code
```

### 使用方法

#### 场景一：新应用发布前审核
```
"我开发了一个社交分享应用，包含用户生成内容和广告变现，请帮我做Google政策合规审核。"
```

#### 场景二：违规通知整改
```
"我的应用收到了Google的政策违规通知，提到目标API级别问题，如何解决？"
```

#### 场景三：定期合规检查
```
"请帮我检查现有应用是否符合最新的Google隐私政策要求。"
```

## 📁 项目结构

```
google-policy-reviewer/
├── SKILL.md                           # 技能主文档
├── scripts/
│   └── pre_submission_check.py        # 自动化检查脚本
├── references/
│   ├── play-store-policies.md          # Play Store政策详解
│   ├── adsense-policies.md             # AdSense广告政策
│   └── privacy-compliance.md           # 数据隐私合规指南
├── README.md                          # 项目说明（本文件）
└── LICENSE                            # 开源许可证
```

## 🛡️ 支持的合规检查

### Google Play Store
- ✅ 应用内容政策（仇恨言论、暴力、成人内容）
- ✅ 隐私和数据政策  
- ✅ 恶意软件和安全政策
- ✅ 知识产权政策
- ✅ 货币化和广告政策
- ✅ 技术要求（API级别、64位架构）

### AdSense广告
- ✅ 广告展示标准
- ✅ 用户体验要求
- ✅ 点击欺诈预防
- ✅ 儿童应用特殊要求

### 数据隐私
- ✅ GDPR合规性
- ✅ COPPA儿童隐私保护
- ✅ 中国个人信息保护法
- ✅ 隐私政策完整性检查

## 📋 使用示例

运行审核脚本：

```bash
python3 scripts/pre_submission_check.py
```

程序会引导你输入应用信息，然后生成详细的合规性报告：

```markdown
# Google政策合规性审核报告

## 基本信息
- 应用名称: 我的应用
- 应用类型: 社交应用
- 目标用户: 青少年和成人
- 审核时间: 2026-03-05 11:52:00

## 合规性评估

### ✅ 通过项目
- Target API Level: 符合要求
- Privacy Policy: 已提供隐私政策URL

### ⚠️ 风险提醒
- 位置权限使用需要合理解释
- 儿童应用的广告展示有严格限制

### ❌ 违规问题
(无严重违规问题)

## 风险等级评估
**风险等级**: 🟡 低风险
```

## 🔄 政策更新

本技能会定期更新以跟进Google政策变化：

- **重大政策更新**: 每年2-3次
- **技术要求更新**: 每年1-2次  
- **安全政策调整**: 不定期但会提前通知

关注项目 [Releases](https://github.com/yourusername/google-policy-reviewer/releases) 获取最新更新。

## 🤝 贡献指南

欢迎贡献代码和政策更新！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/new-policy`)
3. 提交更改 (`git commit -am 'Add new policy check'`)
4. 推送到分支 (`git push origin feature/new-policy`)
5. 创建 Pull Request

## 🐛 问题反馈

如果遇到问题或有建议：

- [提交 Issue](https://github.com/yourusername/google-policy-reviewer/issues)
- [讨论区](https://github.com/yourusername/google-policy-reviewer/discussions)
- 邮箱：your.email@example.com

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- Google开发者政策团队提供的详细文档
- OpenClaw社区的技能开发框架
- 所有贡献者和用户的反馈

---

**免责声明**: 本工具仅供参考，不能替代对Google官方政策文档的详细阅读。政策解释可能存在滞后，请以Google官方最新政策为准。