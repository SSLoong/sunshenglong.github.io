---
title: Cursor Live Apps：从 localhost 到可分享链接，技术负责人该怎么定边界
date: 2026-11-09 10:00:00
categories:
  - AI编程
tags:
  - Cursor
  - Cloud Agent
  - Live Apps
  - 内部工具
  - 技术负责人
description: 基于 2026-11-05 官方发布的 Cursor Live Apps 能力，拆清从 localhost 到可分享应用的完整闭环、安全边界与团队策略，帮助技术负责人决定哪些内部工具该上、哪些不该上。
---

2026 年 11 月 5 日，Cursor 正式发布 [Build Live Apps in Cursor](https://cursor.com/changelog/build-live-apps)，允许 Cloud Agents 构建可工作的 web 应用——dashboard、portal、microsite——并处理 hosting、database、auth 和 secrets。[官方文档](https://cursor.com/docs/cloud-agent/apps)

对技术负责人来说，真正要先想清楚的不是「Agent 写代码又快了多少」，而是：**从 localhost 到外部可访问的 URL，中间补上了哪些闭环，又打开了哪些治理缺口。**

本文依据截至 **2026-11-09** 的 Cursor 官方 changelog 与文档整理，**不是**实际部署的性能测试或安全审计报告，也没有单独的 hosting 计费数据。

![封面：从 localhost 到可分享应用的完整链路](/images/cursor-live-apps-hero.jpg)

*概念配图：Agent 写代码只是第一步，Live Apps 要补的是从构建、数据库、鉴权到发布的闭环。*

<!--more-->

## 先把能力边界钉死：能做什么，不能指望什么

| 维度 | 结论 | 依据 |
| --- | --- | --- |
| 必须通过什么运行 | **必须** Cloud Agent；**本地 Agent 不支持** | Cursor 官方文档明确说明 |
| 支持的代码托管平台 | Origin 仓库（可从零创建）；GitHub 仓库；GitLab / Bitbucket **即将支持** | Changelog / Docs |
| 自带的基础设施 | Hosting、Postgres（按需）、Cursor SSO auth、Secrets 管理 | Docs |
| 默认鉴权方式 | Private/Team apps：Cursor sign-in；Individual 可公开分享（无 auth） | Docs |
| Teams/Enterprise 能否公开分享 | **默认关闭** Public，管理员可在 Apps dashboard 开启 | Docs |
| 安全检查 | 四项**始终开启**的确定性检查（secrets、credentials、.env、source maps）+ AI security review | Docs |
| 管理员权限 | 开关 Apps、允许/禁止 Public、批准发布、unpublish 任意 app、audit log | Docs |
| Hosting 保证 | **不提供** SLA；as is / as available；可因违规或业务/法律原因撤销 | Terms（官方免责声明） |
| 可用性 | 所有**已开通 Cloud Agents 的付费计划** | Docs（未单列 hosting 价格） |

先说一遍边界：这**不是**让你把生产级 SaaS 直接迁过来的方案，也**不是**任意自定义基础设施的 PaaS；它是给 Cloud Agent 写出来的内部工具、demo、小型 dashboard 快速上线的闭环。本地 agent 写不出来能发布的 app，GitLab 仓库暂时接不进来，想要自己的 Redis / ElasticSearch / custom VPC 也不在这个范围内。

## 工作流拆解：从需求到上线的五个环节

![架构流程：Agent → Scaffold → Postgres → SSO → Security Checks → Publish](/images/cursor-live-apps-architecture.jpg)

*Live Apps 的五步流程：每一步都是能力闭环的一部分，也是治理策略的切入点。*

### 1. Cloud Agent Scaffold

你明确说「我要 build an app」后，Agent 会 scaffold 出项目结构。可以从零开始（新建 Cursor Origin 仓库）或从已有 GitHub 仓库部署。官方文档明确：**必须用 cloud agent**，本地不支持。

这一步决定了技术栈和目录结构。Agent 会根据需求选框架（React、Next.js、Vite 等），但不会帮你做容量规划、多区域部署或灰度发布——那些是生产级基础设施的活儿，不在 Live Apps 范围内。

### 2. Postgres Database（按需）

需要数据持久化时，Agent 会提示并配置 Postgres。数据库与 hosting account 关联，团队/个人之间彼此隔离。

这不是托管数仓，也不是让你把 TB 级业务数据迁进来。适用场景是内部工具的状态、小型 dashboard 的查询缓存、demo 的用户输入记录。需要接企业数仓、ClickHouse、Snowflake 时，你要自己提供连接凭据（下面会讲 secrets）。

### 3. Cursor SSO Auth

默认鉴权方式：
- **Private apps**：只有创建者可访问，需 Cursor sign-in
- **Team apps**：团队成员可访问，需 Cursor sign-in
- **Individual apps（公开分享）**：无需 Cursor auth，任何人可访问

Teams/Enterprise **默认关闭** Public 权限，管理员可在 Apps dashboard 打开。这是第一道治理闸门：不是「Agent 想发就发」，而是「管理员允许该类型发布，且用户显式 publish，且安全检查通过」才上线。

这套 SSO 不替代应用内的细粒度权限。比如你的内部工具需要区分「查看者」和「审批者」，那部分逻辑要在应用代码里实现，Cursor SSO 只保证「这人是你团队成员」。

### 4. Security Checks（始终开启 + AI Review）

发布前**始终运行**的四项确定性检查，**即使管理员关掉 AI security review 也跑**：

1. **Block secrets written in app files**：扫描代码文件中硬编码的 API key、密码等
2. **Block credential files**：拦截 `.pem`、`.key`、`.crt` 等凭据文件
3. **Never publish .env files**：禁止发布环境变量文件
4. **Never publish source maps**：避免暴露前端源码结构

其上还有 **AI security review**，用模型检查恶意代码、凭据暴露等风险。Team admin 可加**自定义 review 指令**（比如「禁止使用 eval」），但**不能去掉**内置的四项检查。

这是第二道治理闸门：不是「看起来没问题就过」，而是「硬性规则挡住了明显风险，AI 又看了一遍，admin 的补充指令也满足了」才放行。

检查失败时，admin 可批准发布（除非是恶意代码/硬编码密钥/暴露凭据这类不可豁免的情况），变更进 **audit log**。

### 5. 用户显式 Publish

预览 tray 里可以看到应用效果，选择 URL（team 下是统一域名下的路径），**确认后才发布**。不是「Agent 跑完就上线」，而是「用户看过预览、选好 URL、点了 publish」才生效。

这是第三道治理闸门：不是自动部署，而是用户主动决策。

发布后，admin 可随时 **unpublish** 任意 app，变更进 audit log。

## 安全与治理：secrets 不进 agent 视野

### Secrets 管理

需要接外部 API（比如 OpenAI、Datadog、企业数仓）时，Agent 会提示用户提供 secret。**Agent 看不到 secret 值**，只能引用 secret 名称。

团队 secret 多由 **admin 在 dashboard 创建**，成员在 app 里引用。这避免了「每个人自己贴 token」的混乱，也减少了泄漏面。

但这不等于万无一失：
- Secret 在运行时注入到应用环境，应用代码**如果恶意**仍可能通过日志、外部请求等方式泄露
- 四项确定性检查挡的是「硬编码到文件」，不是「运行时打印到 console 再截屏」
- 团队成员能发布 app，就能引用团队 secret；需要更细粒度的权限（哪些 app 可用哪些 secret）时，要靠 admin 的审批和自定义 review 指令

### API Key：给自动化开的后门

Live Apps 支持 **API key**（`x-cursor-app-token` header）访问。Personal key 和 team key 权限不同，用于 Grok Bot、脚本、CI 等场景。

Team admin 可设置「是否允许 API key 打开 apps」。这是另一个治理决策点：允许了，自动化流程可以无人值守调用；不允许，就只能人工在浏览器里打开。

对技术负责人来说，这是「内部工具的 API 化」与「人工审批闸门」的权衡。我的建议：
- 只读 dashboard（比如 CI 构建结果汇总）可以给 API key
- 会触发变更的工具（比如审批流、发布开关）先走人工，确认稳定后再评估 API key

## 可见性策略：Invite、Team、Public 怎么选

![团队决策清单：可见性、安全控制、团队策略](/images/cursor-live-apps-team-checklist.jpg)

*技术负责人落地清单：何时允许业务同学用、哪些内部工具适合、哪些必须自建托管。*

### Visibility（可见性）

| 类型 | 谁能访问 | 适用场景 | 治理重点 |
| --- | --- | --- | --- |
| Private | 创建者 | 个人实验、临时分析 | 定期清理过期 app |
| Team | 团队成员（需 Cursor sign-in） | 内部工具、团队 dashboard | Admin 审查 app 列表；audit log 追踪发布者 |
| Public | 任何人（无需 auth） | 对外 demo、公开文档页 | **默认关闭**；开启前评估数据暴露面；考虑 rate limit |

Teams/Enterprise 默认**禁止 Public**，这是 Cursor 的保守设定。开启前，技术负责人要问：
- 这个 app 会不会成为攻击面（比如未限速的表单、可枚举的内部 URL）
- 数据来源是否适合公开（哪怕是聚合后的统计）
- 下线流程是否明确（admin 能 unpublish，但已分享的链接怎么召回）

我的建议：
- **Private**：个人随便试，但定期清理（比如 30 天未访问自动归档）
- **Team**：内部工具的主力；admin 定期审查 app 列表，确认每个都有明确 owner 和用途
- **Public**：只在明确的对外场景开启（比如开源项目文档、公开 demo）；开启后在 dashboard 设 allowlist（哪些 app 可以 public），而不是「全员可发公开 app」

### Security Controls（安全控制）

| 检查项 | 作用 | 管理员能做什么 |
| --- | --- | --- |
| 四项确定性检查 | 挡住硬编码 secrets、凭据文件、.env、source maps | **不能关闭** |
| AI security review | 检查恶意代码、暴露风险 | 可关闭（不建议）；可加自定义指令 |
| Admin 审批 | 对被 review 挡住的发布做人工判断 | 可批准（除恶意代码等不可豁免情况） |

自定义 review 指令示例：
- 「禁止使用 `eval()` 或 `Function()` 动态执行代码」
- 「禁止在客户端存储 PII（个人身份信息）」
- 「所有外部 API 调用必须走团队 secret，不接受参数传入的 token」

这些指令是给 AI review 看的，不是强制执行的代码规则。真要硬性拦截，还得在 CI 里加 linter / scanner。

### Team Policy（团队策略）

| 决策点 | 建议 | 原因 |
| --- | --- | --- |
| 是否允许业务同学发布 Team apps | 允许，但要培训 + 审查 | Live Apps 的价值就是降低内部工具门槛；全卡在研发会成为瓶颈 |
| 是否允许 API key 访问 | 按 app 分类：只读允许，写操作人工 | 自动化提效 vs 人工闸门的权衡 |
| Audit log 谁看、多久看一次 | Admin 月度审查；安全团队可随时查 | 及时发现异常发布、过期 app、权限滥用 |

关键是**先小范围试点**：
1. 选一个低风险场景（比如 CI 构建结果 dashboard）
2. 业务同学在 Cloud Agent 里让 Agent 写完，发布成 Team app
3. Admin 在 dashboard 看发布记录、审查代码、确认没有硬编码 secret、没有 PII 暴露
4. 稳定一周后，再放开给更多人

## 与近稿错开看：写代码工具链 ≠ 上线闭环

- **Cursor Marketplace 投毒**（2026-11-04）谈的是 **IDE 扩展供应链**被打穿；本篇是 **Agent 构建并发布应用**的闭环，决策对象不同。
- **Agent SDK 落地指南**（2026-10-28）谈的是把 Agent 行为写成**可版本管理的项目**；Live Apps 是「Agent 写完代码后怎么上线」，是闭环的后半段。
- **Flutter Skills / MCP** 等近稿谈的是 Agent **工具链扩展**；Live Apps 是把 Agent 写的代码变成可访问 URL，是能力边界的另一个维度。

不要把「Agent 能写代码」和「Agent 写的东西能上线」混在一起。前者是模型 + 工具能力，后者是 **hosting + auth + secrets + 安全检查 + 发布审批** 的完整链路。Live Apps 补的是后者。

## 技术负责人落地清单：哪些该上，哪些不该上

### 适合 Live Apps 的场景

| 场景 | 为什么适合 | 注意事项 |
| --- | --- | --- |
| CI/CD 构建结果 dashboard | 只读、团队内、数据不敏感 | 确认数据源 token 是团队 secret，不是个人 PAT |
| 内部工具原型（审批流、配置面板） | 快速验证需求、迭代周期短 | 稳定后评估是否迁到自建平台；保留迁移路径 |
| 对外 demo / 文档页 | 公开分享、无敏感数据 | 评估攻击面（表单、URL 枚举）；考虑 rate limit |
| 数据分析小工具（SQL 查询界面） | 团队内、临时需求 | 数据库连接用团队 secret；审查 SQL 注入风险 |

### 不适合 Live Apps 的场景

| 场景 | 为什么不适合 | 替代方案 |
| --- | --- | --- |
| 生产级 SaaS | 无 SLA、无多区域、无自定义基础设施 | 自建 Kubernetes / 云托管服务 |
| 大规模数据处理 | Postgres 不是数仓；无自定义计算资源 | Snowflake / BigQuery / Databricks |
| 需要细粒度权限的多租户应用 | Cursor SSO 只到「团队成员」粒度 | 自建 auth + RBAC |
| 合规要求严格的金融/医疗应用 | Hosting 条款是 as is；无 SOC 2 / HIPAA 等认证 | 合规云平台 |

关键判断标准：
- **能容忍偶尔下线吗？** 能 → Live Apps；不能 → 自建高可用
- **数据敏感度多高？** 团队内可见 → Live Apps；涉及客户 PII → 合规平台
- **会不会成为关键路径？** 辅助工具 → Live Apps；业务主链路 → 生产基础设施

## 计费与成本：官方未单列价格，但有隐含成本

官方文档写明：Live Apps 对所有**已开通 Cloud Agents 的付费计划**可用，**未单列 hosting 价格**。Hosting 条款写明 **as is / as available**，与主服务分开。

这不意味着「免费无限用」。隐含成本：
- **Cloud Agent 运行费用**：构建 app 时 agent 在跑，tokens 在烧
- **Postgres 存储与查询**：官方未公布容量与 IOPS 限制，但肯定有
- **Hosting 带宽与请求数**：大流量 public app 可能触发限制或额外计费（未明确公开定价）

我的建议：
- 在 dashboard 看 app 的访问量、数据库大小
- 对高频访问的 public app，评估是否迁到自建 CDN
- 定期清理过期 app，避免「僵尸应用」占资源

不要把 Live Apps 当成「无限免费 hosting」，也不要因为「暂时没收费通知」就放任团队发布几十个无人维护的 app。

## 小结：能力闭环有了，治理策略要跟上

Cursor Live Apps 把「Agent 写代码」和「代码上线」之间的 **hosting、database、auth、secrets、安全检查、发布审批** 全串起来了。这是能力闭环，不是银弹。

技术负责人要做的决策：
1. **允许谁发布**：业务同学可以，但要培训 + 审查
2. **允许发布什么**：内部工具、demo、小型 dashboard；生产级 SaaS 不行
3. **允许谁访问**：Private / Team / Public 三档，默认禁 Public
4. **安全检查加什么**：四项确定性检查不能关，AI review 可加自定义指令
5. **API key 给不给**：只读工具可以，写操作先人工
6. **多久审查一次**：admin 月度看 audit log 和 app 列表

最后一句：Live Apps 补的是「从 localhost 到 URL」的闭环，不是「从 idea 到上市」的全链路。**别把内部工具平台的期待，全压在一个 Agent 写出来的 app 上。**

---

*核验说明：本文主要依据 [Cursor Changelog: Build Live Apps](https://cursor.com/changelog/build-live-apps)（2026-11-05）和 [官方文档](https://cursor.com/docs/cloud-agent/apps) 整理，截至 2026-11-09。官方未单列 hosting 单价，本文未编造具体月费数字。文中治理建议为作者观点，非 Cursor 官方指引。*
