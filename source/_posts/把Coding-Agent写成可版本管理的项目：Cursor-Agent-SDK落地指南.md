---
title: 把 Coding Agent 写成可版本管理的项目：Cursor Agent SDK 落地指南
date: 2026-10-28 10:30:00
categories:
- 技术实践
tags:
- Agent SDK
- Cursor
- AI Agent
- 自动化
- DevOps
description: Cursor Agent SDK 于 2026-10-20 正式 GA，让 Agent 从"面板配置"变成"文件夹项目"。本文从技术负责人视角，讲清楚为什么需要 Agent as Code、何时选用 SDK 而非 Automations/Grok Bot，以及如何在一周内落地一个可评测、可回归的 PR Agent。
---

2026 年 10 月 20 日，Cursor 在 [Changelog](https://cursor.com/changelog/agent-sdk) 宣布 Agent SDK 正式 GA（General Availability）。这不是又一个"在对话框里调 prompt"的工具，而是把 Agent 变成一个文件夹项目：`instructions.md` 是常驻提示，`tools/*.ts` 一个文件一个 typed tool，`evals/` 写回归测试，`agent-sdk deploy` 一键部署。

作为技术负责人，我们需要回答三个问题：

1. **为什么需要 Agent as Code**？Dashboard 配置不够用吗？
2. **何时选 SDK、何时用 Automations 或 Grok Bot**？
3. **怎么在一周内落地一个生产可用的 Agent**？

本文基于[官方文档](https://cursor.com/docs/agent-sdk)和实战经验，给出技术选型决策表、落地路径和踩坑指南。

<!--more-->

## 一、为什么"Prompt in Dashboard"不够：可审查、可评测、可回归

### 1.1 Dashboard 配置的三个局限

Cursor Automations 让你在面板里选模型、写 prompt、设触发条件，30 秒上线，适合快速验证。但当 Agent 进入生产环境，三个问题会浮现：

- **可审查性不足**：prompt 改动没有 diff，工具调用逻辑散落在对话历史里，Code Review 无从下手。
- **可评测性缺失**：没有固定测试集，每次改 prompt 都要手工验一遍，回归风险高。
- **版本管理困难**：配置在 dashboard 里，无法回滚到"上周五那版 prompt"，也无法 A/B 对比两个策略。

### 1.2 Agent as Code 带来什么

Agent SDK 把 Agent 变成一个 Node.js 项目，核心文件结构如下（来自[官方文档 Project Layout](https://cursor.com/docs/agent-sdk/reference/project-layout)）：

```
my-agent/
├── package.json
├── bot/
│   ├── agent.ts              # defineAgent({ model?, local? })
│   ├── instructions.md       # 常驻系统提示（必需）
│   ├── tools/                # 一个文件一个 typed tool
│   │   └── approve_pr.ts
│   ├── skills/               # 按需加载的流程
│   │   └── pr-review.md
│   ├── mcp-connections/      # MCP 服务器连接
│   │   └── linear.ts
│   ├── subagents/            # 子 Agent 目录
│   │   └── reviewer/
│   │       ├── agent.ts
│   │       └── instructions.md
│   ├── channels/             # 触发入口（GitHub/Slack/Webhook）
│   │   └── github.ts
│   └── hooks/                # 事件订阅（只读）
│       └── audit.ts
└── evals/                    # 回归测试
    ├── evals.config.ts
    └── readiness.eval.ts
```

这带来三个核心能力：

1. **可审查**：每个改动都是 Git diff，PR review 走标准流程。
2. **可评测**：`evals/` 目录下的测试用例固定输入、断言工具调用和回复形态，`agent-sdk eval` 在 CI 里跑回归。
3. **可回归**：`agent-sdk github replay <PR-URL>` 可以把真实 PR 的 webhook payload 保存成 fixture，Agent 改版后重放测试，不需要反复推 commit 触发真实事件。

**技术负债视角**：如果你的 Agent 要在生产环境跑 6 个月以上、需要多人协作维护、或者失误成本高（比如自动合并 PR、发布到生产），那么"prompt in dashboard"就是技术债，迁移到 SDK 是止损。

## 二、选型决策：Automations vs Grok Bot vs Agent SDK

Cursor 生态里有三种 Agent 形态，官方文档给出了[对比表](https://cursor.com/docs/agent-sdk)：

| 维度 | Cursor Automations | Grok Bot | Agent SDK |
| --- | --- | --- | --- |
| **定义方式** | Dashboard 里配置 prompt、模型、触发器 | 在 App 里对话配置指令、技能和连接工具 | 文件夹项目：Markdown + TypeScript |
| **运行位置** | Cursor 托管 | Cursor 托管 | Cursor 托管 或 自有基础设施 |
| **适用场景** | 定时任务或事件触发、一次性验证 | 无需写代码、希望对话式配置 Agent | 需要版本管理、Code Review、回归测试、团队协作 |
| **学习成本** | 最低（5 分钟上手） | 低（自然语言配置） | 中（需要懂 TypeScript 和 Node.js） |
| **长期维护性** | 差（配置无 diff） | 中（技能可沉淀，但非代码化） | 强（完整工程化流程） |

### 2.1 决策树

```
你需要 Agent 做什么？
│
├─ 定时检查 CI 状态、每天汇总 issue
│  └─ 用 Cursor Automations（最快）
│
├─ 个人助理：盯邮件、查提交、定时提醒
│  └─ 用 Grok Bot（常驻、对话友好、能碰桌面/浏览器）
│
└─ PR 自动审查、Security Review、Jira Triager
   ├─ 需要多人协作维护？ YES → Agent SDK
   ├─ 需要回归测试？ YES → Agent SDK
   ├─ 需要 Code Review？ YES → Agent SDK
   └─ 否则先用 Automations 快速验证，验证通过后迁移到 SDK
```

**关键观点**：Automations 和 Grok Bot 不是 SDK 的"低配版"，它们解决不同问题。Automations 适合"跑一次验证想法"，Grok Bot 适合"个人常驻助手"，SDK 适合"生产级 Agent 工程"。不要因为 SDK 更"高级"就盲目选它。

## 三、一周落地路径：从 Init 到 Deploy

假设你要落地一个"PR 准入检查 Agent"：检查 PR 是否符合团队规范（commit message、测试覆盖率、安全扫描），不符合就评论提醒。

### 第 1 天：Init 项目与本地调试

**关键命令（注意包名）**：

```bash
# 安装 CLI（以官方文档为准，旧名 @cursor/bdk）
npm install --global @grok/agent-sdk

# 初始化项目，可选模板：security reviewer / owners-policy approver / 
# PR autofixer / Linear or Jira triager
agent-sdk init ./pr-checker

cd pr-checker
agent-sdk dev  # 启动本地 playground，浏览器打开调试
```

> **注意**：Changelog 里部分命令示例写的是 `npx @cursor/agent-sdk`，但[官方文档](https://cursor.com/docs/agent-sdk)明确说明当前包名为 `@grok/agent-sdk`（旧名 `@cursor/bdk`）。以文档为准。

**本地调试流程**：

1. `agent-sdk dev` 会启动本地服务器并打开 playground，你可以在浏览器里对话测试。
2. 修改 `bot/instructions.md` 后刷新 playground 即可生效。
3. 在 `bot/tools/` 下新建 `check_commit_message.ts`，定义工具的输入输出类型和执行逻辑（SDK 提供类型约束，避免运行时才发现参数错误）。

**实战建议**：先让 Agent 能"读懂一个 PR 的 diff"，再加规则检查，最后加评论能力。逐步验证，不要一次写完。

### 第 2-3 天：接入 GitHub Channel

在 `bot/channels/github.ts` 里定义触发逻辑：

```typescript
import { defineChannel } from "@grok/agent-sdk";

export default defineChannel({
  on: ["pull_request.opened", "pull_request.synchronize"],
  async handle(event, ctx) {
    // event 是标准的 GitHub webhook payload
    const pr = event.pull_request;
    await ctx.send(`请检查 PR #${pr.number}：${pr.title}`);
  },
});
```

**核心特性**（来自[官方文档 Channels](https://cursor.com/changelog/agent-sdk)）：

- **GitHub 事件走 Cursor 账号**：不需要公开 webhook URL，安全性更高。也支持 GitLab、Bitbucket。
- **会话保持**：同一个 PR 的后续评论会恢复原会话上下文，Agent 记得之前说了什么。
- **支持 Slack、Webhook、Cron**：`channels/slack.ts` 定义 mention/DM 响应，`schedules/` 定义定时任务。

**测试方法**：

```bash
# 不需要真推 commit，直接重放真实 PR 的 webhook
agent-sdk github replay https://github.com/your-org/repo/pull/42 \
  --events 'pull_request.opened' \
  --base-url http://localhost:3000
```

这会把 PR #42 的真实 webhook payload 发给你的本地 Agent，观察日志和回复。

### 第 4 天：写 Evals 固化测试用例

在 `evals/pr-readiness.eval.ts` 里写测试：

```typescript
import { defineEval, includes } from "@grok/agent-sdk/evals";

export default defineEval({
  tags: ["smoke"],
  async test(t) {
    // 固定输入
    await t.send("检查 PR #42 是否符合规范", {
      workspaceFiles: {
        "pr/diff.patch": `
diff --git a/src/api.ts b/src/api.ts
+export function getUser() { /* TODO */ }
        `,
      },
    });

    // 断言：必须调用检查工具，必须评论提醒
    t.calledTool("check_commit_message");
    t.calledTool("comment_on_pr");
    
    // 断言回复内容包含关键词
    t.check(t.reply, includes(/commit message|规范/i));
    
    t.succeeded();
  },
});
```

**核心理念**（来自[官方文档 Evals](https://cursor.com/docs/agent-sdk/evals)）：

- **固定输入 + 断言工具调用**：不依赖真实仓库状态，测试可重现。
- **防止副作用**：在工具的 `execute` 里检查 `ctx.session.purpose === "eval"`，eval 时返回模拟结果，不真的发评论。
- **保存 fixtures**：`agent-sdk github replay <PR-URL> --dry-run --fixtures-dir fixtures/` 把真实 PR 的 payload 保存下来，后续直接加载测试。

**测试运行**：

```bash
agent-sdk eval --dir . --tag smoke  # 跑标记为 smoke 的测试
agent-sdk eval --dir . pr-readiness # 跑单个测试
```

在 CI 里加上：

```bash
agent-sdk eval --dir . --json --no-stream \
  --junit reports/evals.xml \
  --artifacts reports/evals
```

### 第 5 天：Deploy 到 Cursor 托管环境

```bash
agent-sdk login  # 浏览器登录 Cursor 账号
agent-sdk deploy --dir .
```

**Deploy 做了什么**：

1. 构建项目，上传到 Cursor 托管环境。
2. 生成一个 URL，可以在 [Deployed Agents Dashboard](https://cursor.com/agents) 管理。
3. 配置密钥（如 GitHub Token）在 dashboard 里填，不写在代码里。
4. 继续使用本地的 logs、evals、playground。

**生产环境配置**：

- **模型选择**：在 `bot/agent.ts` 里 `defineAgent({ model: "claude-sonnet-4" })`，也可以在 dashboard 覆盖。
- **密钥管理**：敏感信息（API Key、Token）在 dashboard 设置，通过环境变量注入，不提交到代码仓库。
- **访问控制**：在 dashboard 设置哪些仓库可以触发这个 Agent，避免滥用。

### 第 6-7 天：监控、迭代与 Hillclimbing

**监控关键指标**：

- **工具调用准确率**：Agent 是否在该评论时评论、不该评论时保持安静？
- **误报/漏报率**：把生产环境的 PR 定期回放到测试环境，对比结果。
- **响应延迟**：从 PR 打开到 Agent 评论的时间。

**Hillclimbing 流程**（来自[官方文档 Hillclimbing](https://cursor.com/docs/agent-sdk/evals)）：

1. **Pin fixtures**：把生产环境的 bad case 保存成 eval fixture。
2. **Measure**：跑一遍现有 evals，记录通过率。
3. **Change one lever**：改一个变量（prompt、工具参数、模型），不要同时改多个。
4. **Remeasure**：再跑 evals，对比通过率。
5. **Lock the win**：通过率提升就合并，下降就回滚，持平就再试下一个 lever。

**关键观点**：没有 evals 的 Agent 迭代是盲人摸象，有 evals 才能量化改进。

## 四、风险与坑：生产环境的五个注意事项

### 4.1 包名混乱问题

**现状**：Changelog 里部分命令示例用 `npx @cursor/agent-sdk`，官方文档用 `@grok/agent-sdk`，旧文档提到 `@cursor/bdk`。

**建议**：以[官方文档](https://cursor.com/docs/agent-sdk)为准，当前包名是 `@grok/agent-sdk`。如果遇到 `@cursor/agent-sdk` 或 `@cursor/bdk`，都视为过时命名。

### 4.2 Eval 副作用泄漏

**风险**：如果 `tools/comment_on_pr.ts` 没有检查 `ctx.session.purpose === "eval"`，跑 evals 时会真的往 GitHub 发评论。

**防护措施**：

```typescript
async execute({ prNumber, comment }, ctx) {
  if (ctx.session.purpose === "eval") {
    return { posted: false, reason: "eval mode" };
  }
  
  await github.issues.createComment({ issue_number: prNumber, body: comment });
  return { posted: true };
}
```

工具调用记录还在 trajectory 里，eval 可以断言"Agent 选择了评论"，但不会真的发出去。

### 4.3 密钥管理的三条铁律

1. **不要把密钥写在代码里**：通过环境变量注入，在 dashboard 配置。
2. **不要把密钥提交到 Git**：`.gitignore` 里加上 `.env*`。
3. **区分本地和生产密钥**：本地调试用个人 Token（权限最小），生产用 Service Account。

### 4.4 会话边界的误解

**常见误区**：以为 Agent 能"记住所有 PR 的历史"。

**实际情况**：

- **同一个 PR/Slack thread 的多轮对话共享一个会话**，有上下文。
- **不同 PR 之间的会话是独立的**，Agent 不记得"上个 PR 怎么处理的"。
- **需要跨会话记忆时，用外部存储（如 KV store）或 skills**。

### 4.5 Channel 与 Subagents 的权限边界

**风险**：GitHub Channel 拿到的 event 是**完整的 webhook payload**，包含仓库敏感信息（如 secrets）。如果 Agent 把 event 直接转发给外部 API，会泄漏信息。

**防护措施**：

- **最小化 event 传递**：只提取需要的字段（PR number、title、author），不要整个 event 往外传。
- **Subagents 无法直接访问父 Agent 的 event**：需要父 Agent 显式传参。

## 五、结论与行动清单

### 5.1 核心观点总结

1. **Agent as Code 不是银弹**：Automations 和 Grok Bot 各有适用场景，不要为了"看起来更专业"而盲目选 SDK。
2. **Evals 是生产环境的必需品**：没有回归测试的 Agent 是定时炸弹。
3. **Hillclimbing 需要工程纪律**：一次只改一个变量，量化对比，记录每次实验。
4. **安全是第一优先级**：密钥管理、权限边界、副作用隔离，缺一不可。

### 5.2 落地行动清单

**如果你打算在团队落地 Agent SDK，建议按以下步骤推进**：

- [ ] **Week 1**：用 `agent-sdk init --template` 启动一个模板项目，本地跑通 playground。
- [ ] **Week 2**：接入一个真实 Channel（GitHub/Slack），用 `github replay` 测试。
- [ ] **Week 3**：写 3-5 个核心场景的 evals，固化 smoke 测试。
- [ ] **Week 4**：Deploy 到 staging 环境，小范围验证（如只对特定仓库生效）。
- [ ] **Month 2**：收集生产 bad cases，回放成 evals，迭代 prompt 和工具逻辑。
- [ ] **Month 3**：全量上线，建立 on-call 机制，定期 review Agent 的决策日志。

**技术选型的最后一个提醒**：如果你的团队还没有稳定的 CI/CD 流程、Code Review 规范、测试文化，那么 Agent SDK 的价值会打折扣。先把基础工程能力建好，再上 Agent，否则只是把"混乱的人工流程"变成了"混乱的自动化流程"。

---

## 参考资料

- [Cursor Agent SDK Changelog (2026-10-20 GA)](https://cursor.com/changelog/agent-sdk)
- [Agent SDK 官方文档](https://cursor.com/docs/agent-sdk)
- [Project Layout 参考](https://cursor.com/docs/agent-sdk/reference/project-layout)
- [Evals 文档](https://cursor.com/docs/agent-sdk/evals)
- [Deployed Agents 管理面板](https://cursor.com/agents)

**说明**：信息截至 2026-10-28，Agent SDK 仍在快速迭代，命令和 API 可能变化，请以[官方文档](https://cursor.com/docs/agent-sdk)为准。文章中的包名、命令、目录结构均基于官方文档核实，若遇冲突请优先采信文档页面（而非 Changelog 里的示例代码）。
