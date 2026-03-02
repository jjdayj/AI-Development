# Steering 配置说明

此目录包含 Kiro 的 steering 文件，用于自定义 AI 助手的行为规则。

## 重要更新（2026-03-02）

本项目已采用模块化目录结构，steering 文件已迁移到模块目录：
- `doc_save_rules.md` → `.kiro/modules/doc-save/v1.0/steering/doc_save_rules.md`
- `ai_dev.md` → `.kiro/modules/ai-dev/v1.0/steering/ai_dev.md`

详细信息请参考：`doc/project/20260302_prompt基座架构设计/00-快速参考.md`

---

## 文件列表

### doc_save_rules.md（已迁移）
会话文档自动保存规则。此规则定义了如何自动保存每次对话的操作文档和对话记录。

**新位置**: `.kiro/modules/doc-save/v1.0/steering/doc_save_rules.md`

**当前状态**: 已禁用

**如何启用**:
1. 打开 `.kiro/modules/doc-save/v1.0/steering/doc_save_rules.md`
2. 修改文件头部的 front-matter:
   - 将 `enabled: false` 改为 `enabled: true`
   - 将 `inclusion: manual` 改为 `inclusion: always`
3. 保存文件后，规则将在下次对话时自动生效

**如何禁用**:
1. 打开 `.kiro/modules/doc-save/v1.0/steering/doc_save_rules.md`
2. 将 `enabled: true` 改为 `enabled: false`
3. 或将 `inclusion: always` 改为 `inclusion: manual`
