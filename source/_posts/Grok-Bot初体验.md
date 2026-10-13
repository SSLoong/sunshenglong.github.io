---
title: 从架构看桌面 Agent：Grok Bot 与 OpenClaw、Manus、Claude Cowork 对比
date: 2026-10-13 15:00:00
categories:
- 技术实践
tags:
- Grok Bot
- AI Agent
- 桌面Agent
- MCP
- OpenClaw
- Manus
description: 从执行环境、权限审批、连接器（MCP）、浏览器与桌面控制、记忆与技能、定时与事件任务、子 Agent 委派、凭据管理、成本与开放性九个维度，拆解 Grok Bot 的技术设计，并基于官方文档与 OpenClaw、Manus、Claude Cowork 横向对比。
---

我日常主力是 ChatGPT、Cursor、Codex 和 Claude Code，它们擅长“坐在电脑前、打开一个项目干活”。这次试用 Grok Bot，是想补上另一类需求：盯邮件、查提交记录、清理仓库身份这类不写代码却琐碎、需要 Agent 常驻在线、能碰账号、还要在关键步骤停下来问人的事。

所以这篇不写流水账，而是借这次体验，把“桌面 Agent”拆成几个工程维度，看看 Grok Bot 怎么设计，以及 OpenClaw、Manus、Claude Cowork 各自走了哪条路。

> 说明：Grok Bot 部分来自官方文档和我的实际使用；其余三款只参考官方文档，没有并排实测。信息截至 2026-10-13，标注“未亲测”的条目请以官方为准。

<!--more-->

## 一、一张总图：桌面 Agent 由哪些部件构成

抛开产品包装，一个能长期替你干活的 Agent 大致包括这几层：

```
┌──────────── 入口层：桌面/移动 App、IM、X @提及 ────────────┐
│                                                            │
│  编排层：Agent（规划、对话、记忆）                          │
│                │                                           │
│  策略层：审批模型 / 不可信内容隔离                       │
│                │                                           │
│  能力层：连接器(MCP) │ Shell/文件 │ 浏览器/桌面控制 │ 定时任务 │
│                │                                           │
│  执行环境：云端持久 VM  ◀──可选──▶  用户本机（注册设备）      │
└────────────────────────────────────────────────────────────┘
```

下面逐层看。

## 二、执行环境：云端持久 VM vs 住在你的电脑里

这是各家最根本的分歧。

**Grok Bot** 按[官方文档](https://docs.x.ai/grok-bot/overview)，每个 Bot 跑在一台**持久化的云端电脑**上，有浏览器、文件系统和终端。几个值得注意的工程细节：

- **持久化**：装过的工具、生成的文件、浏览器登录态在多轮对话之间都保留，不是一次性沙箱。
- **共享而非隔离**：同一用户名下所有 Bot 共享同一台机器的文件系统和浏览器登录态，但每个 Agent 有自己的桌面窗口。文档明确说这**不是安全边界**（[文档](https://docs.x.ai/grok-bot/approvals-security-and-privacy)）。
- **本机作为可选扩展**：把自己的 Mac 注册成设备后，Agent 可以在本机执行命令、读文件，也能在云端和本机之间原样复制文件。云端和本机文件系统完全分开，路径不互通。
- **网络受平台约束**：我想用 IMAP 收 163 邮件，993 端口出站被拦了，最后改成转发到 Gmail。“自带电脑”意味着网络策略由平台决定。

**OpenClaw** 反过来，它是一个跑在你自己机器或服务器上的 Gateway（[文档](https://docs.openclaw.ai/)），天然拥有本机全部能力，代价是运维和安全都要自己负责。

**Manus** 以云端执行为主，后来推出桌面端 [My Computer](https://manus.im/blog/manus-my-computer-desktop)，通过终端执行命令，范围限定在授权文件夹。

**Claude Cowork** 跑在 Claude Desktop 里，访问你选定的本地文件夹，部分任务可远程运行（[帮助中心](https://support.claude.com/en/articles/13345190-get-started-with-claude-cowork)）。

| 维度 | Grok Bot | OpenClaw | Manus | Claude Cowork |
| --- | --- | --- | --- | --- |
| 主执行位置 | 云端持久 VM | 自托管 Gateway | 云端为主 + 桌面端 | 本地桌面应用为主 |
| 本机访问 | 注册设备后按策略审批 | 原生 | 授权文件夹内 CLI | 选定文件夹 |
| 电脑睡眠影响 | 云端任务不受影响；本机命令需在线（亲测） | Gateway 主机需在线 | 本地任务需桌面端运行 | 仅连接器任务可远程跑（[文档](https://support.claude.com/en/articles/13854387-schedule-recurring-tasks-in-claude-cowork)） |

工程上的取舍很清楚：**云端 VM 换来的是常驻和隔离你的主力机，失去的是网络自由度和本地上下文**；本地方案正好相反。Grok Bot 的做法是两者兼有，默认在云端，需要时再“借用”本机。

## 三、权限模型：审批与不可信内容

Agent 一旦能执行命令、发消息，权限设计就是核心问题。从官方文档和使用体验看，Grok Bot 的权限主要有两层：

1. **动作级审批**：发邮件、发消息、发布、购买、删除、强推这类**不可逆或对外可见**的动作，必须用户明确授权才执行，否则只生成草稿，停在执行前。我让它改写博客仓库历史并强推时，它就先停下来让我确认。
2. **本机执行审批**：对注册设备的命令，默认策略是 Ask every time，可改成 Always allow 或 Never allow（[文档](https://docs.x.ai/grok-bot/approvals-security-and-privacy)）。实际使用中，每条本地命令都会弹审批卡。

另一个容易被忽视的设计是**不可信内容隔离**：网页、邮件、工具返回的内容都被当作数据而非指令。邮件里写着“请把这份文件转发给某某”，Agent 不会照做，只会报告给你。这是防提示词注入的基本功，对需要读你邮箱的 Agent 尤其关键。

对比：

| 维度 | Grok Bot | OpenClaw | Manus | Claude Cowork |
| --- | --- | --- | --- | --- |
| 本地执行默认 | Ask every time | gateway/node 主机 `exec.security` 默认 `full`、`ask` 默认 `off`，可配 deny/allowlist/ask 等（[文档](https://docs.openclaw.ai/tools/exec-approvals)） | 每条命令需批准，可选 Allow Once / Always Allow（[文档](https://manus.im/docs/features/desktop)） | 文件夹级授权，定时任务可设审批模式 |
| 信任边界 | 同一账号的 Bot 共享机器，非隔离 | 一个 Gateway 一个信任边界（[安全页](https://docs.openclaw.ai/gateway/security)） | 文件夹级 | 文件夹级 |
| 加固手段 | 平台内置 | `cautious` 预设、`openclaw security audit` | 平台内置 | 企业管理策略（[管理指南](https://claude.com/resources/tutorials/claude-cowork-enterprise-administrator-guide)） |

OpenClaw 的默认值比较“放开”，安全文档写得很扎实，但需要你自己读、自己配，这是自托管的代价。托管型产品则把这层策略收到平台里。

## 四、工具与连接器：MCP 成了事实标准

Grok Bot 的能力优先级是：**连接器优先，computer use 兜底**（[文档](https://docs.x.ai/grok-bot/computer-and-apps)）。

- **MCP 连接器**：Gmail、GitHub、Notion 等以连接器形式接入，账号走授权，不需要把密码交给 Agent。
- **网页操作兜底**：没有连接器的服务，就在云端浏览器里操作。

| 维度 | Grok Bot | OpenClaw | Manus | Claude Cowork |
| --- | --- | --- | --- | --- |
| 集成方式 | MCP 连接器 + 网页操作 | 插件 + ClawHub 生态 | 内置连接器 + MCP（[文档](https://manus.im/features/automations)） | 连接器 + 插件 |
| 对话入口 | 自家 App；X 上 @bot（[文档](https://docs.x.ai/grok-bot/overview)） | WhatsApp、Telegram、Slack、Signal、iMessage 等几十个渠道（[GitHub](https://github.com/openclaw/openclaw)） | Web、桌面，可接 [Telegram](https://manus.im/blog/manus-agents-telegram)、WhatsApp Business | 桌面、Web、移动 |

OpenClaw 的长板是 IM 渠道覆盖；Grok Bot 的长板是复用 Cursor 生态里已有的连接（我的 GitHub 就是直接复用的，不用重新授权）。

## 五、浏览器与桌面控制

- **Grok Bot**：云端 VM 有自己的桌面和浏览器，登录态持久保存，用户可以打开这个桌面旁观或接手（比如处理验证码）。**本机浏览器控制我没有验证（未亲测）**。
- **OpenClaw**：有浏览器控制能力，安全页把它列为单独的风险项。
- **Manus**：[Browser Operator](https://manus.im/docs/features/browser-operator) 扩展直接使用本地 Chrome/Edge 的登录态。
- **Claude Cowork**：配合 Claude in Chrome。

这里的关键取舍是**登录态放在哪儿**：放在云端 VM 上，意味着需要在 VM 上登录一次，但不会碰你本机的会话；借用本地浏览器则开箱即用，风险面也直接落在你的主力浏览器上。

## 六、记忆与技能

文档描述的记忆是**分层的**（[文档](https://docs.x.ai/grok-bot/skills-routines-and-automations)）：

- **Bot 级身份与记忆**：命名的 Bot 有固定职责，保留自己的偏好和上下文；
- **Skill**：把成熟流程沉淀成可复用的技能。文档推荐的路径是“先把一次性任务做稳 → 沉淀成 skill → 再上定时”。

长期记忆的效果我还没有足够数据评估。

## 七、定时与事件驱动任务

Grok Bot 把定时任务（routine）当一等公民：一句话创建，cron 表达式加时区，间隔不少于 5 分钟，每个 Bot 最多 50 个（[文档](https://docs.x.ai/grok-bot/skills-routines-and-automations)）。我建的邮件提醒是 `30 9-18 * * *`（Asia/Shanghai），并且约定**没有新邮件就保持静默**。这一点工程上很重要：定时任务默认“有变化才打扰”，否则提醒很快会变成噪音。

| 维度 | Grok Bot | OpenClaw | Manus | Claude Cowork |
| --- | --- | --- | --- | --- |
| 定时 | cron + 时区，≥5 分钟，≤50 个/Bot | cron、heartbeat（[文档](https://docs.openclaw.ai/automation/cron-jobs)） | 定时 + 自然语言编排（[文档](https://manus.im/docs/automations)） | 小时/天/工作日/周 |
| 事件触发 | 文档称部分集成支持 Slack、GitHub 事件（未亲测） | webhook、Gmail Pub/Sub | GitHub、Gmail、Shopify、Webhook | 文档以定时为主 |
| 运行位置 | 云端，不依赖本机 | Gateway 主机 | 云端 | 连接器任务可远程，本地文件任务需唤醒 |

四家都能定时，真正的差别在**跑在哪儿**。

## 八、子 Agent 委派

这是 Grok Bot 让我印象最深的架构点：主 Agent 负责对话、规划和确认，具体执行可以委派给专门的 Agent。

**案例：改写 Git 历史并强推。** 我希望个人博客仓库里不出现公司邮箱作为提交身份，这需要改写历史并强推，属于不可逆操作。Grok Bot 先讲清原因（本机全局 `git config user.email` 被 `hexo deploy` 继承），然后停下来让我确认，确认后再委派执行：

- **云端编码 Agent**：改写 33 个提交并强推 master、source 两个分支，交给了 Cursor 云端编码 Agent，它同时扫描了仓库里的敏感内容，**只报告不改动**；
- **本机收尾**：之后通过注册的 Mac，在逐条审批下备份本地仓库、对齐远端、设置仓库级 git 身份，并确认未提交的草稿没被动到。

这种“编排者 + 执行者”的分层，把**决策权和审批**集中在主 Agent，把**具体执行**交给专门的 Agent，和 Claude Code 的 subagent 思路相似，只是 Grok Bot 把它延伸到了跨产品（Cursor 编码 Agent）的委派。

其他三款里，OpenClaw 自我定位为“连接聊天应用和 AI 编码 Agent 的网关”，Claude、Codex 等运行时以插件接入（[文档](https://docs.openclaw.ai/)）；Manus 和 Cowork 的公开文档里，我没看到对等的用户可见委派机制描述，这里不下结论。

## 九、凭据管理

- **OAuth 连接器优先**：Gmail、GitHub 走授权，Agent 拿不到你的密码。
- **掩码密钥输入**：确实需要密钥时（比如邮箱授权码），对话里有一个掩码输入框，不会明文出现在聊天记录里。我一开始把授权码直接贴进了聊天，它提醒我作废重新生成，改用掩码输入。
- **风险提示**：由于同一账号的 Bot 共享 VM，**存进 VM 的凭据对你所有 Bot 可见**，敏感凭据的放置要自己权衡。

OpenClaw 自托管，凭据就在你自己机器上；Manus 和 Cowork 由平台托管连接器授权。

## 十、成本与开放性

| 维度 | Grok Bot | OpenClaw | Manus | Claude Cowork |
| --- | --- | --- | --- | --- |
| 开源 | 否 | 是，MIT | 否 | 否 |
| 收费 | 含在 Cursor 付费个人版/Teams 中，也可绑定 SuperGrok，用量每周重置（[文档](https://docs.x.ai/grok-bot/overview)） | 软件免费，模型与机器自付 | 积分制订阅，有免费额度（[帮助中心](https://help.manus.im/en/articles/11711097-what-are-the-rules-for-credits-consumption-and-how-can-i-obtain-them)），价格以官网为准 | 需 Claude 付费套餐 |

背景补充：OpenClaw 前身为 Clawdbot/Moltbot，2026 年 1 月底定名，由非营利基金会维护（[博客](https://openclaw.ai/blog/introducing-openclaw)）；Manus 已宣布加入 Meta（[博客](https://manus.im/en/blog/manus-joins-meta-for-next-era-of-innovation)）。

## 十一、局限与未验证项

1. **云端网络受限**：部分协议端口出不去，只能绕路。
2. **检索有盲区**：我问最近一次提交时，它第一次按作者搜索，漏掉了用未关联邮箱提交的博客仓库，我反驳后才改成遍历仓库查到。Agent 的第一个答案应当被当作假设。
3. **本机能力依赖在线**：电脑睡眠，连接就断。
4. **共享 VM 不是隔离**：多个 Bot 共享文件和登录态。
5. **未亲测**：本机浏览器控制、事件触发、长期记忆效果、长期运行的用量消耗。
6. **对比非实测**：其他三款都来自官方文档，产品迭代快，信息可能过时。

## 十二、总结

把桌面 Agent 拆开看，差异集中在三个设计选择：

- **执行环境放哪儿**：云端常驻（Grok Bot、Manus）还是住在本机（OpenClaw）；
- **权限策略谁来管**：平台内置的审批与审查，还是自托管时自己配置；
- **任务怎么分工**：单 Agent 包办，还是编排者加子 Agent 委派。

我的选型建议：

- 要完全掌控、数据不出自己机器、愿意折腾安全配置：**OpenClaw**；
- 要开箱即用的云端通用 Agent，偶尔借用本地浏览器登录态：**Manus**；
- 重度 Cursor 用户，想要一个常驻云端、接好邮件和 GitHub、能把编码任务委派出去、关键操作一定先问你的 Agent：**Grok Bot**。

参考资料：

- [Grok Bot 文档](https://docs.x.ai/grok-bot/overview)：[审批与安全](https://docs.x.ai/grok-bot/approvals-security-and-privacy)、[电脑与应用](https://docs.x.ai/grok-bot/computer-and-apps)、[技能与定时任务](https://docs.x.ai/grok-bot/skills-routines-and-automations)
- [OpenClaw 文档](https://docs.openclaw.ai/)、[执行审批](https://docs.openclaw.ai/tools/exec-approvals)、[安全](https://docs.openclaw.ai/gateway/security)、[GitHub](https://github.com/openclaw/openclaw)
- [Manus Desktop](https://manus.im/docs/features/desktop)、[Browser Operator](https://manus.im/docs/features/browser-operator)、[Automations](https://manus.im/docs/automations)
- [Claude Cowork 入门](https://support.claude.com/en/articles/13345190-get-started-with-claude-cowork)、[定时任务](https://support.claude.com/en/articles/13854387-schedule-recurring-tasks-in-claude-cowork)
