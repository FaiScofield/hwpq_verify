---
alwaysApply: true
scene: skill_router
---

# Skill 强制路由规则（通用版 · 适用于任何项目的 `.trae/rules/`）

> 本文件是**硬性约束**，不是建议。任何模型（默认 / 自定义 / DeepSeek 等）在响应用户请求前都必须先完成下面的路由检查，否则视为违规。
> 本文件**不绑定任何特定项目**，复制到任意仓库的 `.trae/rules/skill-router.md` 即可生效。
> 项目专属信息（路径、技术栈、不适用 skill）请在 `project-profile.md` 中单独维护。

## 0. 路由前置自检（必做，缺一不可）

在生成任何回复之前，按顺序回答以下 4 个问题，并在回复**最开头**显式输出（即使只是几行）：

```
[Skill 路由]
- 命中 skill: <name> | 无
- 任务类型: <代码编辑 / 构建系统 / 脚本 / 文档 / 问答 / 其它>
- 涉及文件: <相对路径列表> | 无
- 准备使用的辅助 skill: <list> | 无
```

> 这一段不能省略。DeepSeek 类模型都必须**先输出上面这段，再做其它事**。

## 1. 文件类型 → Skill 通用映射

按文件后缀匹配（不绑定具体项目路径）：

| 类别 | 常见后缀 | 适用 skill |
| --- | --- | --- |
| 通用编程语言源码 | `*.cpp` `*.h` `*.hpp` `*.c` `*.java` `*.go` `*.rs` `*.ts` `*.tsx` `*.js` `*.jsx` `*.py` `*.m` 等 | `incremental-implementation`, `code-review-and-quality`, `code-simplification`, `debugging-and-error-recovery` |
| 着色器 / GPU kernel | `*.cl` `*.glsl` `*.fs` `*.vs` `*.compute` | `performance-optimization`, `code-review-and-quality` |
| 构建系统 | `CMakeLists.txt` `*.cmake` `Makefile` `*.mk` `package.json` `Cargo.toml` `go.mod` `pom.xml` `build.gradle*` | `incremental-implementation`（多文件改动时） |
| 脚本 | `*.sh` `*.bat` `*.cmd` `*.ps1` `*.py` | `incremental-implementation`, `code-simplification`, `debugging-and-error-recovery` |
| 配置 / 数据 | `*.json` `*.yaml` `*.yml` `*.toml` `*.ini` `*.xml` | `incremental-implementation`（如影响代码行为） |
| 文档 | `*.md` `*.rst` `*.txt` | `documentation-and-adrs`（如涉及接口 / ADR 变更） |
| 跨多文件改动 | 同时改 ≥2 个目录下的文件 | **强制**先调 `incremental-implementation` |

> **项目特定的"不适用 skill 列表"放到 `project-profile.md`，不要写在本文件里。** 本文件只描述**通用机制**。

## 2. 任务 → Skill 命中规则（按优先级匹配，命中即停）

| 触发关键词 / 场景 | 必触发 skill | 备注 |
| --- | --- | --- |
| 修 bug / 报错 / 不通过 / crash / 段错误 / 内存泄漏 / 性能回退 | `debugging-and-error-recovery` | 配合 `code-review-and-quality` 自检 |
| 重构 / 清理 / 简化 / 抽取函数 / 消除重复 | `code-simplification` | 改完跑 `code-review-and-quality` |
| 添加 / 修改 / 重写源码 | `incremental-implementation` | 多文件时强制；单文件也建议 |
| 性能 / 耗时 / 优化 / 跑得慢 / 帧率下降 | `performance-optimization` | 算法 + 关键路径双重检查 |
| 评审 / 合并 / review / 自检 | `code-review-and-quality` | |
| 安全 / 输入校验 / buffer 越界 / 注入 / 鉴权 | `security-and-hardening` | |
| git commit / 提交代码 / 生成提交信息 | `git-commit`（消息生成）+ `git-workflow-and-versioning` | 遵循仓库内的 `git-commit-message.md`（如有） |
| 写新接口 / 改公共头 / API 签名变更 | `api-and-interface-design` + `documentation-and-adrs` | |
| 涉及仓库架构 / 文件关系 / "在哪 / 怎么调" 类问题 | **先调 `graphify`**（如本仓库有 `AGENTS.md` 或 `graphify-out/`） | 否则退化为 Grep / Glob |
| 写测试 / 跑测试 / TDD | `test-driven-development` | 弱触发，看项目惯例 |
| 涉及 Git 协作流程（分支策略、rebase、cherry-pick） | `git-workflow-and-versioning` | |
| 涉及复杂架构决策（多方案对比、影响面广） | `brainstorming` | 创建新项目 / 大改前用 |

> **不强制触发的 skill（按需使用）**：
> `idea-refine`、`writing-plans`、`spec-driven-development`、`test-driven-development`、
> `performance-optimization`（无性能诉求时不调）、
> `context-engineering`（只在 agent 输出质量明显下降时调）。

## 3. 强制工作流（任何代码改动都必须按这个顺序）

1. **路由声明**：按 §0 输出 4 行 `[Skill 路由]`
2. **调用 skill**（如果命中）：先调 `Skill` 工具，让 skill 引导后续动作
3. **阅读现有代码**：用 Read / Grep 找相关上下文，**不要凭空生成**
4. **修改时遵守最小改动原则**：
   - 只改必要的代码和注释
   - **不删除已存在的注释**（除非与新代码逻辑明显冲突）
   - 风格遵循仓库已有的 `.clang-format` / `.editorconfig` / 语言 lint 配置（**不要发明新风格**）
5. **改完自检**：调 `code-review-and-quality` skill 过一遍
6. **git 提交**：调 `git-commit` skill 生成 message（遵循仓库内 `git-commit-message.md`）

## 4. 禁止行为

- ❌ 禁止跳过 §0 的 4 行 `[Skill 路由]` 直接回答
- ❌ 禁止以"这不是 creative work"为由拒绝调 skill（**任何代码改动都算 creative work**）
- ❌ 禁止复述 skill 描述但不实际调用
- ❌ 禁止在回复中删除已有注释（除非与新代码逻辑明显冲突且已在 commit message 中说明）
- ❌ 禁止触发与项目无关的 skill（如本项目无 React 时不要硬触发 `vercel-composition-patterns`）—— **本规则不写死名单，请在 `project-profile.md` 中维护**

## 5. 不命中时的回复模板

如果扫描完表格确实没有匹配的 skill，按下面模板回复（**不要直接跳过**）：

```
[Skill 路由]
- 命中 skill: 无
- 任务类型: <类型>
- 涉及文件: <列表>
- 准备使用的辅助 skill: 无

> 已扫描 §2 路由表，无匹配项。下面按通用模式回答：
<正常回答>
```

## 6. 自检方法（验证本规则是否生效）

下次发请求时，要求模型"逐字复述 §0 的 4 行模板"——
- 能复述 + 实际按模板输出 = 规则被注入且生效
- 能复述但不做 = 模型 instruction-following 偏弱，需在用户消息中显式 trigger
- 完全复述不出 = 客户端没把 `.trae/rules/` 注入到当前模型，需检查 Trae 设置

## 7. 项目定制（推荐：把项目特有信息拆到 `project-profile.md`）

为了让本文件可复用，**不要**把项目特定信息直接写进 `skill-router.md`，而是另建一个 `project-profile.md`：

```markdown
---
alwaysApply: true
scene: project_profile
---

# 项目 Profile（被 skill-router.md 引用）

## 技术栈
- 主要语言:
- 框架 / 平台:
- 构建系统:
- 风格配置: <例如 .clang-format 路径>

## 不适用本项目的 skill（黑名单）
- <skill-name>: <原因>

## 其它项目特定约束
- <例如：所有 API 改动必须同步 doc/>
```

模型在执行 §0 路由前应**先 read `project-profile.md`（如存在）**，把里面的黑名单叠加到 §2 命中表上。

## 8. 相关规则文件

- `project-profile.md` — 项目特定配置（推荐配套使用）
- `AGENTS.md` — graphify 知识图谱使用规则（如果项目有）
- `git-commit-message.md` — 提交信息风格（如果项目有）
