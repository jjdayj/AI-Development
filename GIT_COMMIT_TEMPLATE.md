# Git 提交模板规范

## 📋 提交格式

```
<type>(<scope>): <subject>

[详细描述]

[关联信息]
```

## 🎯 提交类型 (Type)

| 类型 | 说明 | 示例 |
|------|------|------|
| `feat` | 新功能 | feat(workflow): 新增需求复杂度分析 |
| `fix` | 修复 Bug | fix(workflow/native): 修复询问逻辑错误 |
| `docs` | 文档更新 | docs(readme): 更新快速开始指南 |
| `style` | 代码格式（不影响功能） | style(workflow): 统一代码缩进 |
| `refactor` | 重构（不是新功能也不是修复） | refactor(workflow): 重构选择逻辑 |
| `perf` | 性能优化 | perf(workflow): 优化复杂度分析性能 |
| `test` | 测试相关 | test(workflow): 添加单元测试 |
| `chore` | 构建/工具相关 | chore(deps): 更新依赖版本 |
| `init` | 初始化项目 | init(workflow): 初始化工作流 v2.0 |
| `release` | 发布版本 | release(workflow): 发布 v2.0.1 |
| `revert` | 回滚提交 | revert: 回滚 feat(workflow) |
| `merge` | 合并分支 | merge: 合并 feature/analysis 分支 |

## 🎨 提交范围 (Scope)

### 工作流模块 (Workflow)

| Scope | 中文名称 | 说明 |
|-------|----------|------|
| `workflow` | 工作流模块 | 工作流整体变更 |
| `workflow/main` | 主工作流入口 | workflow_main.md 相关 |
| `workflow/native` | 原生开发流程 | native_development.md 相关 |
| `workflow/secondary` | 二次开发流程 | secondary_development.md 相关 |
| `workflow/config` | 工作流配置 | workflow/config.yaml 相关 |
| `workflow/analysis` | 需求复杂度分析 | 复杂度分析功能相关 |

### 配置文件 (Config)

| Scope | 中文名称 | 说明 |
|-------|----------|------|
| `config` | 全局配置 | kiro/config.yaml 相关 |
| `config/module` | 模块配置 | kiro/kiro.yaml 相关 |

### Steering 规则 (Steering)

| Scope | 中文名称 | 说明 |
|-------|----------|------|
| `steering` | Steering 规则 | Steering 整体变更 |
| `steering/main` | 主入口 Steering | kiro/steering/main.md 相关 |

### 文档 (Docs)

| Scope | 中文名称 | 说明 |
|-------|----------|------|
| `docs/readme` | README 文档 | README.md 相关 |
| `docs/changelog` | 更新日志 | CHANGELOG.md 相关 |
| `docs/structure` | 项目结构文档 | PROJECT_STRUCTURE.md 相关 |
| `docs/guide` | 使用指南 | 使用指南相关 |

### 其他 (Misc)

| Scope | 中文名称 | 说明 |
|-------|----------|------|
| `deps` | 依赖管理 | 依赖更新相关 |
| `build` | 构建相关 | 构建脚本相关 |
| `ci` | CI/CD 相关 | CI/CD 配置相关 |
| `*` | 全局/多个范围 | 影响多个模块 |

## 📝 提交主题 (Subject)

### 规则

1. **使用动词开头**：新增、修复、更新、删除、重构等
2. **简短明了**：不超过 50 个字符
3. **不要句号**：不需要句号结尾
4. **使用中文**：便于团队理解

### 示例

✅ 好的主题：
- `feat(workflow): 新增需求复杂度分析功能`
- `fix(workflow/native): 修复 Phase 2 询问逻辑错误`
- `docs(readme): 更新快速开始指南`

❌ 不好的主题：
- `feat(workflow): 新增了一个需求复杂度分析的功能。` （太长，有句号）
- `update` （不明确，没有 scope）
- `fix bug` （不明确，没有 scope，没有说明修复了什么）

## 📖 详细描述 (Body)

### 规则

1. **使用列表格式**：便于阅读
2. **每行不超过 72 个字符**：便于在终端查看
3. **说明变更内容**：做了什么、为什么做、怎么做
4. **可选**：简单变更可以省略

### 示例

```
feat(workflow): 新增需求复杂度分析功能

- 新增 4 种复杂度情况判断（简单、中等、复杂、过于复杂）
- 支持自动生成需求探索文档
- 支持复杂需求拆分为多个子需求
- 所有询问和分析都使用中文
- 更新 workflow_main.md 添加步骤 3
- 更新 config.yaml 添加复杂度标准配置
```

## 🔗 关联信息 (Footer)

### 可选字段

```
版本: v2.0.1
影响范围: workflow/main, workflow/config
破坏性变更: 否
向后兼容: 是
关联 Issue: #123
关联 PR: #456
```

## 📋 完整示例

### 示例 1：新功能

```
feat(workflow/analysis): 新增需求复杂度分析功能

- 新增 4 种复杂度情况判断
  - 简单：功能点 ≤ 3，文件 ≤ 5
  - 中等：功能点 4-8，文件 6-15
  - 复杂：功能点 > 8，文件 > 15
  - 过于复杂：功能点 > 15，文件 > 30
- 支持自动生成需求探索文档
- 支持复杂需求拆分为多个子需求
- 所有询问和分析都使用中文

版本: v2.0.1
影响范围: workflow/main, workflow/config
破坏性变更: 否
向后兼容: 是
```

### 示例 2：Bug 修复

```
fix(workflow/native): 修复 Phase 2 询问逻辑错误

- 修复询问顺序错误，先询问冲突点再询问 GUI 偏好
- 修复条件判断逻辑，正确识别是否涉及 GUI
- 添加默认值处理，避免用户跳过询问时出错

版本: v2.0.0
影响范围: workflow/native
破坏性变更: 否
向后兼容: 是
```

### 示例 3：文档更新

```
docs(readme): 更新快速开始指南

- 添加需求复杂度分析说明
- 更新工作流程图
- 添加常见问题解答
- 修正错别字和格式问题

版本: v2.0.1
影响范围: docs/readme
```

### 示例 4：重构

```
refactor(workflow): 重构工作流选择逻辑

- 将选择逻辑从 main.md 提取到独立函数
- 简化条件判断，提高可读性
- 统一错误处理方式
- 不改变任何功能行为

版本: v2.0.0
影响范围: workflow/main
破坏性变更: 否
向后兼容: 是
```

### 示例 5：初始化项目

```
init(*): 初始化 VibeCoding 工作流 v2.0

- 创建项目基础结构
- 实现 VibeCoding 工作流核心功能
  - 原生功能开发流程（4 阶段）
  - 二次开发流程（5 阶段）
  - 需求复杂度分析
- 配置模块化架构
- 编写完整文档

版本: v2.0.0
影响范围: *
破坏性变更: 是（全新项目）
向后兼容: 否
```

## 🔧 配置 Git 使用模板

### 方法 1：全局配置

```bash
git config --global commit.template .gitmessage
```

### 方法 2：项目配置

```bash
git config commit.template .gitmessage
```

### 使用方式

配置后，执行 `git commit` 会自动打开编辑器并加载模板。

## ✅ 提交前检查清单

- [ ] 代码已测试，功能正常
- [ ] 代码格式符合规范
- [ ] 没有调试代码（console.log、debugger 等）
- [ ] 提交类型正确（feat/fix/docs 等）
- [ ] 提交范围明确（workflow/config 等）
- [ ] 主题简短明了（≤ 50 字符）
- [ ] 正文详细说明变更内容（如果需要）
- [ ] 相关文档已更新
- [ ] 没有提交敏感信息（密码、密钥等）

## 📚 参考资源

- [Conventional Commits](https://www.conventionalcommits.org/)
- [Angular Commit Guidelines](https://github.com/angular/angular/blob/main/CONTRIBUTING.md#commit)
- [Semantic Versioning](https://semver.org/)

---

**最后更新**: 2026-03-04  
**维护者**: yangzhuo
