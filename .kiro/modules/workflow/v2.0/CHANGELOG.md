# VibeCoding 工作流更新日志

## v2.0.1 (2026-03-04)

### 新增功能

#### 需求复杂度分析阶段
在用户选择工作流类型（A 或 B）后，新增强制执行的需求复杂度分析。

**分析维度**：
- 需求规模（功能点数量、涉及文件数量）
- 需求清晰度（不确定点数量）
- 需求独立性（是否需要拆分）
- 技术复杂度

**四种情况**：
1. **简单清晰**：直接进入工作流
2. **较复杂但单一**：建议生成需求探索文档
3. **复杂需拆分**：建议拆分为多个子需求
4. **过于复杂**：通知用户不适合此工作流

**需求探索文档**：
- 路径：`requirements/exploration/{需求名称}_exploration.md`
- 内容：需求概述、功能点列表、不确定点、技术方案、对话追踪

**语言**：所有询问和分析都使用中文

### 配置更新

新增 `complexity_analysis` 配置：
```yaml
complexity_analysis:
  simple:
    function_points: 3
    files: 5
    uncertain_points: 2
  
  medium:
    function_points: 8
    files: 15
    uncertain_points: 5
  
  complex:
    function_points: 15
    files: 30
  
  too_complex:
    function_points: 15
    files: 30
```

新增 `exploration_doc` 配置：
```yaml
exploration_doc:
  path_template: "requirements/exploration/{requirement_name}_exploration.md"
  sections:
    - "需求概述"
    - "功能点列表"
    - "不确定点列表"
    - "技术方案初步思路"
    - "子需求列表（如果需要拆分）"
    - "依赖关系图（如果需要拆分）"
    - "开发顺序建议（如果需要拆分）"
    - "后续对话追踪记录"
```

### 文件更新

- ✅ `steering/workflow_main.md`：新增步骤 3（需求复杂度分析）
- ✅ `config.yaml`：新增复杂度分析标准和探索文档模板
- ✅ `README.md`：更新工作流程说明
- ✅ `CHANGELOG.md`：本文件

### 影响

- **向后兼容**：不影响现有功能
- **用户体验**：提前发现需求复杂度问题
- **需求管理**：支持复杂需求拆分和追踪

---

## v2.0 (2026-03-04)

### 初始版本

**核心特性**：
- 轻量化工作流（4-5 阶段）
- 支持原生开发和二次开发
- 改一点测一点的迭代方式
- 测试和文档可选
- 保留核心资产（状态管理、目录规范）

**工作流类型**：
1. 原生功能开发流程（4 阶段）
2. 二次开发流程（5 阶段，含评估）

**替代版本**：
- 完全替代 v1.0、v1.0-simple、v1.0-complex

---

**维护者**: yangzhuo  
**最后更新**: 2026-03-04
