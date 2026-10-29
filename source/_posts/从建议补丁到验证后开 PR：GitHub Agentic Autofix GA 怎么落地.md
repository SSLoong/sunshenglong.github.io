---
title: GitHub Agentic Autofix：修复能力、验证边界与试点方法
date: 2026-10-26 10:00:00
updated: 2026-10-29 00:00:00
categories:
  - AI编程
tags:
  - GitHub
  - Code Scanning
  - Agentic Autofix
  - Copilot
  - 安全
  - 技术负责人
description: 区分 GitHub 两种 Autofix 的修复流程，说明验证、启用与计费边界，并给出一份可记录人工返工和实际成本的试点方法。
---

GitHub 在 2026 年 10 月 15 日宣布 Agentic Autofix 正式可用。它会调查代码、尝试修复 code scanning 告警、运行验证，再提交 PR 供人审查。[GA 公告](https://github.blog/changelog/2026-10-15-agentic-autofix-for-code-scanning-alerts-general-availability/)

决定是否启用它时，最容易看错两件事：旧 Copilot Autofix 已经可以一键生成修复 PR；Agentic Autofix 开出 PR，也不代表修复已经验证成功。真正值得评估的是，它多承担的调查和迭代工作，能否减少团队的修复与返工时间。

本文是截至 **2026-10-29** 的官方资料解读和试点建议，没有实际运行 Agentic Autofix，也没有本团队的修复成功率或成本数据。

<!--more-->

## 从告警到 PR，两种流程差在哪里

Copilot Autofix 为支持的单条告警生成建议。点击 **Create PR with fix**，GitHub 会从默认分支建新分支、提交修复，并创建 draft PR。开发者继续测试、编辑和审查。因此，把它描述为“只能给建议，提交和开 PR 都靠手工”并不准确。[修复告警的操作说明](https://docs.github.com/en/code-security/how-tos/manage-security-alerts/manage-code-scanning-alerts/resolve-alerts)

Agentic Autofix 则从 **Assign to Copilot** 开始一个 Agent 会话，由它探索相关代码、生成修复、尝试验证，并根据需要迭代。一次分配可以包含最多 25 条告警，产生一个会话和一个 PR。当前入口针对默认分支上的积压告警；只出现在其他分支或 PR 上的告警不在这个范围内。[GA 公告的工作流与范围](https://github.blog/changelog/2026-10-15-agentic-autofix-for-code-scanning-alerts-general-availability/)

| 要比较的事情 | Copilot Autofix | Agentic Autofix |
| --- | --- | --- |
| 交给工具的任务 | 为单条支持的告警生成建议 | 调查并尝试修复一条或多条告警 |
| 创建 PR | 用户点击按钮后自动完成 | Agent 会话生成 draft PR |
| 后续验证 | 团队测试和审查建议 | Agent 尝试验证，团队仍需复核 |
| AI credits | 建议修复不消耗 | 会话消耗 Code Security AI credits |

启用 Agentic Autofix 后，单条告警上的 Generate Fix 入口会被替换。规划试点时，应记录仓库开关状态，不要假设同一个入口能随时选择两种流程。[功能对比](https://docs.github.com/en/code-security/concepts/code-scanning/autofix-for-code-scanning)

## PR 是待审结果，验证证据要另看

Agentic Autofix 的验证是 best-effort。它使用 code scanning query suite 重跑 CodeQL，但不能确认来自自定义 CodeQL 查询、`security-extended` suite 或第三方扫描工具的告警是否已修复。[官方验证限制](https://docs.github.com/en/code-security/concepts/code-scanning/autofix-for-code-scanning)

即使无法验证，或者认为告警可能是误报，它也可能在 PR 中说明情况。因此，流程不能简化成“验证通过才开 PR”。[PR 结果说明](https://docs.github.com/en/code-security/how-tos/manage-security-alerts/manage-code-scanning-alerts/resolve-alerts)

我建议审查时分开回答三个问题：

1. **它改了什么？** 检查输入处理、数据流和调用方是否一起改对，有没有删除校验、压制告警或扩大修改范围。
2. **它实际验证了什么？** 看执行日志里的查询、扫描范围和结果。没有运行、运行失败、运行后通过，必须分别记录。
3. **应用行为有没有退化？** 为原漏洞补回归用例，同时验证合法输入、错误处理和兼容性。静态扫描结果无法覆盖所有业务行为。

对验证范围之外的告警，可以补跑原扫描器或对应查询。是否接受修复取决于补充证据；“Agent 不能确认”不能直接推导为“只能人工写修复”，也不能据此把 PR 当作已通过检查。

## 启用前先确认仓库归属

当前访问文档覆盖 GitHub.com 公开仓库，以及具有 GitHub Code Security 或 GitHub Advanced Security 的组织仓库。使用者不必单独持有 Copilot 许可证。企业托管用户（EMU）个人命名空间下的仓库不支持此功能，这不等于所有使用 EMU 的企业组织仓库都不支持。

| 仓库归属 | 启用路径 |
| --- | --- |
| 企业所属组织 | 企业允许配置，再由组织启用；仓库可在上级允许范围内退出或重新启用 |
| 独立组织 | 从组织设置开始，不需要企业策略步骤 |
| 符合条件的个人公开仓库 | 仓库管理员直接在 Code Security 设置中启用 |

组织启用会默认覆盖符合条件的仓库；企业“允许配置”本身不会启用各仓库。试点前要和仓库管理员确定排除范围，避免把一次评估变成全组织推广。以上按[当前访问管理文档](https://docs.github.com/en/code-security/how-tos/manage-security-alerts/manage-code-scanning-alerts/managing-access-to-agentic-autofix-for-code-scanning)整理，不能把 GA 公告里的企业流程当作所有账号的统一前置条件。

## 用量和新增账单要分开记录

Agentic Autofix 消耗 Code Security AI credits 和 GitHub Actions minutes。对于有合资格 Copilot 权益所含 AI credits 的计费账号，符合条件的用量先使用包含额度，耗尽后再按量计费；没有包含额度的账号，则按量计费。公开仓库也不因此免除 AI credits 消耗。经典 Copilot Autofix 的建议修复不消耗 AI credits。[计费说明](https://docs.github.com/en/billing/concepts/product-billing/github-advanced-security#code-security-ai-credits)

所以不宜用“每开一个 PR 固定多少钱”估算，也不能把所有用量都当成新增账单。试点要分别记录额度消耗、实际收费和 Actions 用量，并请账单管理员为 **Code Security AI credits SKU** 配置限制按量使用的 hard budget。它与按活跃提交者计算的许可证预算不同，也不替代 Actions 的费用控制。

## 一次能回答问题的小规模试点

下面是建议方案，不是已经完成的实践。

先选一个有人负责审查、测试可运行的仓库。从同一类、有明确修复目标的少量告警开始，按独立修复单元分配。25 条是产品上限，不是推荐批次大小；把没有关联的问题塞进一个 PR，会增加评审和回退难度。

每个会话保留一行记录，附上 PR、日志和扫描结果：

| 字段 | 要记录的内容 |
| --- | --- |
| 输入 | 仓库、起始 commit、告警 ID、规则 ID、查询或扫描器版本 |
| 分配 | 批次内容、开始时间、会话链接、仓库开关状态 |
| 输出 | PR、修改范围、是否需要拆分或重做 |
| 验证 | Agent 实际运行的检查；独立复核的工具、结果和未覆盖项 |
| 人工投入 | 初审、补测试、改代码、再次审查各花多久 |
| 资源 | AI credits、Actions minutes、实际新增费用 |
| 最终处置 | 接受、返工后接受、拒绝，及具体原因 |

评估时，分别统计直接接受、人工返工后接受和拒绝的比例。成功口径应由团队的独立检查决定，不能用“创建了 PR”代替。计算单个接受修复的成本时，把失败会话的费用也计入分子；若没有接受结果，就报告总投入，不计算一个没有意义的均价。

如果队列超过审查能力、预算触及事先约定的上限，或者反复出现删除校验、改坏业务行为等同类问题，就暂停新增分配，先分析失败样本。关闭开关只是停止后续使用策略，已生成的 PR 仍应逐个处理。只有当日志和人工记录能证明节省了总修复时间，才值得扩大范围。

*核验说明：本文核对了 GitHub 当前文档与 GA 公告；试点方法属于作者建议。未启用任何仓库设置、未分配真实告警、未测量修复质量或账单。发布前应再次确认访问与计费页面是否有变更。*
