---
title: Cursor Projects 现已支持多人协作：技术负责人该怎么定共享边界
date: 2026-11-13 10:00:00
categories:
  - AI编程
tags:
  - Cursor
  - Projects
  - Cloud Agents
  - 团队协作
  - 技术负责人
description: 基于 2026-11-10 Cursor 官方博客与现行文档，给技术负责人的决策指南：什么时候该把团队放进一个共享 Project，共享的是任务看板与团队上下文而不是个人 store，计费按何人跑，以及 agent-to-agent 通讯的安全边界。
---

2026 年 11 月 10 日，Cursor 官方宣布：Projects 现已支持多人协作（multiplayer），beta 向所有 Cursor 用户推出。[官方博客](https://cursor.com/blog/projects-multiplayer)

对技术负责人来说，这个变化的决策意义在于：**从单人多 Agent 到团队共享工作区**。不是简单地"多几个人用 Agent"，而是同一个 Project 里，每个人都有自己的 coordinator 会话和 workers，同时共享任务看板与团队上下文层。官方举例的场景包括 on-call 交接、设计师与工程师重叠的工作、以及跨多 PR 的特性开发。

本文依据截至 **2026-11-13** 的 [Cursor Projects 文档](https://cursor.com/docs/agent/projects)、[帮助页面](https://cursor.com/help/ai-features/projects) 与官方博客整理，**非本机完整实测**。重点是把能用的硬门槛、共享边界、计费规则与决策清单钉死，而不是重复产品说明书。

![封面：多人围着共享任务板与上下文层协作](/images/cursor-projects-multiplayer-hero_7caf.jpg)

*概念配图：团队成员各自拥有 coordinator 会话，共享一套任务看板与团队上下文，同时保留个人 store。*

<!--more-->

## 先把能用的硬门槛钉死

不是所有用户都能直接开启分享。文档与博客同时存在的要求必须分层说清楚：

| 门槛维度 | 要求 | 来源 |
| --- | --- | --- |
| 套餐 | Projects 需要**包含 Cloud Agents 的套餐**：Premium and higher、Teams、Enterprise，以及 legacy paid plans | [Cloud Agents 帮助页](https://cursor.com/help/ai-features/cloud-agents) |
| 不可用套餐 | Free、Plus、legacy Hobby（这些不含 Cloud Agents） | 同上 |
| 团队账号 | 分享 Project 需要 **team account** | [Projects 文档](https://cursor.com/docs/agent/projects) |
| 客户端版本 | 分享需要 **Cursor 3.26.13 or later** | 同上 |
| Enterprise 版本要求 | Enterprise teams 使用 Projects 本身需要 **3.21.9+**；分享另需 **3.26.13+** | 同上 |
| 仓库访问权限 | 队友需要有该 Project **仓库的访问权限**才能加入 | 同上 |
| 明确排除 | **Privacy Mode (Legacy)**、跑在 **self-hosted machine** 上的 Project、已 **archived** 的 Project | 同上 |

注意分层理解：官方博客写 beta 向所有用户推出，指的是功能在推出；但文档同时要求套餐包含 Cloud Agents、team account、客户端版本与仓库权限。**不要把「beta 推出」写成「所有套餐都能分享」**。

另外，当前 Privacy Mode（非 Legacy）下，Cloud Agents **可以使用**（官方明确："Does Privacy Mode work with Cloud Agents? Yes."）。只有 **Privacy Mode (Legacy)** 被明确排除。不要混为一谈。

个人账号或另一个 team 的人不能加入。邀请通过 Project 顶部 Invite 发起，搜索姓名或邮箱；队友点击 Accept Invite 后获得自己在该 Project 的聊天。owner 和任何已加入的人都可以邀请队友；也可通过 Copy link 分享 Project 链接，但只有已在 Project 里的人能复制链接。owner 可用 Reset Share Link 让先前的拷贝失效。

## 共享了什么、没共享什么：两套 store

这是理解决策边界的第一个关键。每位加入者在该 Project 里拥有**自己的聊天**、**自己的 coordinator 和 workers**。**对方的会话以其本人身份运行并计费**（Their chat runs and bills as them）。

成员之间共享两块：

1. **Task board**：所有人使用同一份任务列表/看板。
2. **Shared context（Project store）**：应用里显示为 Context，路径是 `/cursor/stores/self`，是一个所有成员的 agents 都会读写的 Agent Store。

同时，每个人还有一套 **Personal user store**，路径是 `/cursor/stores/user`，**队友的 agents 永远看不到你的个人 store**。

![架构：共享 vs 个人上下文](/images/cursor-projects-shared-context_5bb1.jpg)

*示意：Teammate A 和 B 各有自己的 chat、coordinator、worker 和 personal store；中间共享 task board 与 Project store；agent-to-agent 消息标记为 untrusted。*

| Store | 路径 | 谁读写 | 放什么 |
| --- | --- | --- | --- |
| Project store (Context) | `/cursor/stores/self` | 每位成员的 agents | 需求文档、图、技术规格、mockups、团队决策、共享上下文 |
| Personal user store | `/cursor/stores/user` | 仅你自己的 agents | Preferences 和 skills，会跟着你在不同 Project 之间走，但不会到达队友 |

官方强调：个人 store 放 preferences 和 skills，会跟着你在不同 Project 之间走，但不会到达队友。队友加入时，你的 coordinator 可以提议把描述「如何在本 Project 工作」的 preference 条目拷进 Project rules；**只拷贝你批准的内容**。

这意味着：**共享 Project 不等于把个人偏好、技能或历史全部暴露给队友**。技术负责人需要在 Project 设置初期，主动决定哪些上下文应该进入 Project store，哪些应该留在个人 store。

## Agent-to-agent 通讯的真实边界

官方举例的场景之一是：你的功能在读库、队友在改 schema 时，agents 先约定工作顺序。听上去很理想，但文档同时给出了严格的安全边界。

当你的 coordinator 需要队友工作中的信息时，它会直接向对方的 coordinator 发消息，你不必传话。每条消息都被投递，并遵守这些规则：

1. **消息被标记为 agent input**。接收方被告知是哪位队友的 agent 发来的。它把文本当作 **untrusted input** 来权衡，而不是当作它所服务的那个人发出的请求；在分享该人的 **personal files 或 connector data** 之前会先询问。
2. **不会打断你的主聊天**。队友消息进入从你聊天分叉出的侧边聊天，名为 `Chat with {name}'s agent`。它根据你聊天已知的内容作答，回复回到发送方聊天，你的主聊天会在下一轮收到关于这次交换的说明。
3. **侧边聊天只能回答**。你可以读、停止或归档，但不能向它发消息。它 **never shares secrets, credentials, or tokens**。它可以读 task board 但不能改，也不能问你问题、请求访问、连接 source control、或管理 routines。

这三条规则直接回答了安全团队最关心的问题：**Agent 能不能随便互相指挥或自主执行对方仓库的任意操作？答案是不能**。

- **不分享密钥**：侧边聊天 never shares secrets, credentials, or tokens。
- **不改看板**：侧边聊天可以读 task board 但不能改。
- **untrusted input**：接收方将消息标记为 untrusted agent input，分享个人文件或连接器数据前会询问。
- **只回答，不执行**：侧边聊天不能问你问题、请求访问、连接 source control、或管理 routines。

官方博客里的 agent-to-agent 协作示例（工程师给产品页加 reviews、设计师同时在改版时，双方 coordinator 能提前发现重叠并对齐；或功能在读库、队友在改 schema 时约定工作顺序）是**官方自我描述**，不是独立评测。写给团队的策略时，应该先标明这些是官方举例，再基于上述三条规则判断实际风险接受度。

简单总结：**不要把「coordinator 互发消息」写成「Agent 可以自主执行对方仓库的任意操作」或「没有审批」。文档写的是 untrusted input、分享个人文件/连接器数据前会询问、侧边聊天不能改 task board、不分享密钥。**

## 计费怎么算：按何人跑

官方明确：**每位加入者的聊天以其本人身份运行并计费**（Their chat runs and bills as them）。不要写成"全算在 Project owner 头上"。

Cloud Agents 用量与编辑器/CLI 里的 Agent **使用同一套 plan usage**，按所选模型费率计费。更大的 context window 可能增加 token 用量与费用。[Cloud Agents 帮助页](https://cursor.com/help/ai-features/cloud-agents)

The X Subscription 公开标价（[官方定价页](https://cursor.com/help/account-and-billing/pricing)，价格不含税，**以官方页面为准**）：

- Free $0，有限用量
- Plus $8/mo（Base）；年付 $80/yr
- Premium $30/mo（4x Plus）；年付 $300/yr
- Super $100/mo（15x Plus）；年付 $1,000/yr
- Ultra $200/mo（50x Plus）；年付 $2,000/yr
- Teams：$30、$100 或 $200 per seat/mo，用量与对应席位档一致

补充：
- 每个付费套餐包含 Cursor models（Grok 4.7、Grok 4.6、Grok 4.5、Composer 2.5）的 weekly pool，Cursor 与 Grok 共享。
- Plus 在固定设置下运行这些模型（Fast off, medium effort），**不含** Auto、Cloud Agents、Automations、Bugbot、Origin 或第三方模型。
- Premium and above 包含上述能力；第三方模型按 API list price，从 prepaid credit 支付。

Teams 席位补充（[Teams 定价页](https://cursor.com/docs/account/teams/pricing)）：
- Teams 席位档：Premium $30、Super $100、Ultra $200 per user/mo；另有 Free seat $0（无团队用量额度，走个人套餐或免费少量额度）。
- 付费席位各有自己的 weekly pool，**席位之间不共享 weekly pool，用量不在成员间转移**。
- 第三方模型不包含在内，按 list API prices 加上 Cursor Token Rate（$0.25 per million tokens），从团队 prepaid balance 支付。

这意味着：**多人场景下，每个人的 coordinator 和 workers 消耗的是各自的 weekly pool。不要寄希望于「大家共用一个池子」**。如果团队有 5 个人加入同一个 Project，5 个人各自的聊天消耗各自的 weekly pool。Owner 不会被扣掉所有人的用量。

旧的 request-based 套餐上仍从 included requests 扣除，但 Cloud Agents 总是以 Max Mode 运行，按 API rates 加 Max Mode upcharge 计价，并以 request-equivalents 计入 included requests。超额后走 on-demand。详见官方 Models & Pricing。

**禁止**：使用过时的 fast/slow requests 叙述；把套餐差异写成「某一方不能自主执行」；编造未在官网上的 Projects 单独加价。不要把 2026 年 6 月旧文里的 Teams Standard $40 / Premium $120 当作现行 The X Subscription 标价（那是 legacy Teams seats）。

## 技术负责人决策清单：什么时候该开共享 Project

明确了硬门槛、共享边界、agent-to-agent 规则和计费方式之后，可以进入决策清单了。

![决策清单：前提与决策要点](/images/cursor-projects-decision_1604.jpg)

*示意：Prerequisites（Team account, Cursor 3.26.13+, Repo access, Not Legacy Privacy Mode）与 Decide first（Who owns the context, Billing runs as each person, What stays in personal store, Who may invite）*

### Prerequisites（前提）

在考虑"该不该开"之前，先确认这些条件：

- **Team account**：必须有团队账号。
- **Cursor 3.26.13+**：客户端版本到位。Enterprise teams 还需先确认 Projects 本身可用（3.21.9+）。
- **Repo access**：队友需要有该 Project 仓库的访问权限。
- **Not Legacy Privacy Mode**：不在 Legacy Privacy Mode、不在 self-hosted machine、不是 archived 的 Project。

### Decide first（先决策）

官方并没有给出"什么工作适合共享 Project"的标准清单。下面是基于文档与博客示例，结合技术负责人视角的建议：

#### 1. Who owns the context（谁拥有上下文）

- **适合共享 Project 的场景**：跨多 PR 的特性、迁移、on-call 交接、设计师与工程师重叠的工作、跨月维护的需求。这些场景的共同点是：**上下文需要跨人传递，且持续时间较长**。
- **不适合共享 Project 的场景**：个人探索性任务、快速修 bug、临时脚本、敏感代码审查、个人实验。这些场景的共同点是：**上下文不需要传给别人，或者涉及个人隐私、敏感信息**。

官方举例：他们多个团队把 on-call 放在共享 Project 里；交接时新工程师的 coordinator 会先 check in，再从现状接手——进行中的工作、未处理的问题、需要交接的 incidents 与笔记、以及要盯着的 channels / Linear boards / threads。进行中的工作甚至可以直接移交：新来的人的 agent 接着做。

这是官方自我描述，不是本机实测，但它揭示了一个决策标准：**当工作需要交接，且交接成本高时，共享 Project 的价值最大**。

#### 2. Billing runs as each person（计费按各人跑）

- **每个人的聊天消耗各自的 weekly pool**。团队需要提前规划：如果 5 个人都在同一个 Project 里高频使用 coordinator，5 个人各自的 weekly pool 都会被消耗。
- **不要寄希望于「大家共用一个池子」**。也不要把用量全算在 owner 头上。

#### 3. What stays in personal store（什么留在个人 store）

- **个人 store（`/cursor/stores/user`）**：Preferences、skills、个人历史、个人实验、敏感信息。队友的 agents 永远看不到。
- **Project store（`/cursor/stores/self`）**：需求文档、图、技术规格、mockups、团队决策、共享上下文。所有成员的 agents 都会读写。

技术负责人应该在 Project 设置初期，主动决定哪些上下文应该进入 Project store，哪些应该留在个人 store。队友加入时，coordinator 可以提议把 preference 拷进 Project rules，但只拷贝你批准的内容。

#### 4. Who may invite（谁可以邀请）

- **Owner 和任何已加入的人都可以邀请队友**。
- **也可通过 Project 链接加入**：只有已在 Project 里的人能复制链接。owner 可用 Reset Share Link 让先前的拷贝失效。

这意味着：**邀请权不是 owner 独享的**。如果团队需要严格控制谁能加入，需要在 Project 设置初期就明确规则，并定期 review 成员列表。

### 一个决策流程示例

假设技术负责人要决定是否为一个跨三个月的数据迁移开一个共享 Project：

1. **确认前提**：团队有 team account，客户端版本 3.26.13+，仓库权限到位，不在 Legacy Privacy Mode。
2. **判断上下文归属**：迁移涉及数据库、API、前端、测试，需要多人接力，且跨月维护。**适合共享 Project**。
3. **计费规划**：参与的 5 个人各自消耗各自的 weekly pool。预估每人每周 10-20 次 coordinator 交互，在 Premium 档位内。**可接受**。
4. **划定 store 边界**：迁移脚本、数据 schema、API 文档、测试计划进 Project store；个人调试脚本、临时测试数据留在个人 store。
5. **邀请规则**：只有 owner 和指定的 tech lead 可以邀请新成员。其他人需要先请示。定期 review 成员列表。

如果判断结果是"不适合"，那就让每个人各自开个人 Project，通过 PR comments 或 Slack 同步进度，而不是强行把所有人塞进一个共享 Project。

## 和近期热点怎么错开看

- **Cursor Live Apps / Build live apps**：那是从 localhost 到可分享托管链接、内部工具托管，是另一条产品线。本篇讲的是团队 Agent 工作区，不是工具托管。仓库里已有待审 PR #14《Cursor Live Apps：从 localhost 到可分享链接》。
- **AI Agent 为什么越聊越糊涂？上下文工程实践**：那篇讲的是个人会话上下文失效原理与管理策略。本篇重点是团队级上下文治理与共享边界。
- 不要把扩展能写 `authorized_keys` 误写成「Agent 默认就能自主执行任意系统配置」——那是**扩展进程权限 + 分发完整性**问题，不是 Agent 产品的审批开关文案。本篇也不涉及这类供应链安全话题。

## 小结

Cursor Projects 现已支持多人协作，但不是所有用户、所有工作都适合开共享 Project。技术负责人的决策清单应该包括：

1. **确认硬门槛**：套餐、团队账号、客户端版本、仓库权限、不在 Legacy Privacy Mode。
2. **理解共享边界**：共享的是 task board 与 Project store（`/cursor/stores/self`），不共享个人 store（`/cursor/stores/user`）。每个人有自己的 chat、coordinator 和 workers。
3. **明确 agent-to-agent 规则**：消息标记为 untrusted input，侧边聊天只能回答，不分享密钥，不改看板。
4. **计费规则**：每位加入者的聊天以其本人身份运行并计费，消耗各自的 weekly pool，席位之间不共享。
5. **决策清单**：谁拥有上下文、计费按各人跑、什么留在个人 store、谁可以邀请。

**适合共享 Project 的场景**：跨多 PR 的特性、迁移、on-call 交接、设计师与工程师重叠的工作、跨月维护的需求。**不适合的场景**：个人探索性任务、快速修 bug、临时脚本、敏感代码审查、个人实验。

官方博客里的 agent-to-agent 协作示例是官方自我描述，不是独立评测。真正落地时，应该基于文档明确的 untrusted input、侧边聊天只读回答、不分享密钥等规则，判断实际风险接受度。

最后，**不要把「beta 推出」写成「所有套餐都能分享」**。功能在推出，但套餐、团队账号、客户端版本和仓库权限仍是硬门槛。也不要把「coordinator 互发消息」写成「Agent 可以自主执行对方仓库的任意操作」。

*核验说明：本文主要依据 [Cursor Projects 文档](https://cursor.com/docs/agent/projects)、[帮助页面](https://cursor.com/help/ai-features/projects)、[官方博客](https://cursor.com/blog/projects-multiplayer)、[Cloud Agents 帮助页](https://cursor.com/help/ai-features/cloud-agents)、[官方定价页](https://cursor.com/help/account-and-billing/pricing) 与 [Teams 定价页](https://cursor.com/docs/account/teams/pricing) 整理；非本机完整实测。发布前请以官方文档最新版为准。*
