---
title: 把 Agent 拆成可替换的零件：DeepSeek Harness 源码解读
date: 2026-08-24 21:00:00
categories:
- AI编程
tags:
- AI Agent
- DeepSeek
- 源码解读
- TypeScript
---

最近 DeepSeek 开源了 [DeepSeek Harness](https://github.com/deepseek-ai/deepseek-harness)。它的官方主路径是 `npx @deepseek-ai/dsh web`：启动本地 Web UI，而不是提供一个类似传统 REPL 的终端对话界面。但顺着源码走一遍会发现，它更像一个 Agent 运行时：`dsh` 命令负责启动 profile、管理插件和导出配置，Web UI 则是其中一个前端，真正的核心是如何把模型、工具、会话、沙箱、记忆和调度组织起来。

这篇文章基于仓库 `b150a551b8d4`（2026-08-21，`0.1.1-rc.2`）阅读。项目仍处于 Developer Preview，目录和接口迭代很快；因此本文讨论的是它的设计方法，而不是保证长期稳定的 API 教程。

![DeepSeek Harness 模块化 Agent 架构示意图](/images/deepseek-harness-hero.png)

<!--more-->

## 先给结论：Harness 才是 Agent 的“操作系统”

模型本身只会根据输入输出 token。一个能在真实工程里持续工作的 Agent，还需要知道：当前在哪个目录、有哪些工具、工具是否要审批、执行后的结果如何回到上下文、会话如何恢复、用户中途插话怎么办。

DeepSeek Harness 给出的拆法是：**模型负责推理，Harness 负责运行时，能力全部以插件提供。**

```text
用户 / Web UI / Headless 调用
       │
       ▼
  Agent Loop ──── System Prompt + Tool Schema
       │                     │
       ▼                     ▼
  Session Event Log ◀── LLM / Tools / Hooks
       │
       ├── 持久化、回放、fork、transcript、遥测
       └── UI 根据同一条事件流渲染
```

这里最重要的不是“插件多”，而是没有一个特权业务内核。源码在 `packages/core/` 中把 session、tools、system-prompt、agent、agent-loop 拆成独立包；模型适配器、文件系统、沙箱、子 Agent、Web UI 也都只是向同一个运行时挂载能力。

这里的 **Cordis 不是 DeepSeek Harness 对自家底座起的名字**，而是一个独立的开源框架（仓库为 [cordiverse/cordis](https://github.com/cordiverse/cordis)）。DeepSeek Harness 以 Cordis 作为底层框架：插件向共享 `Context` 注册 service、类型化事件和可逆副作用，卸载时这些注册也随之撤销。Harness 做的是在这个框架上，把 Agent 需要的领域能力组装出来。

这比在一个 `Agent` 类里持续加 `if (enableX)` 更适合 Agent 产品。因为“换模型”“把本地文件系统换成远程沙箱”“为某类任务换一套工具”，最终都是替换一段组合，而不是侵入主循环。

## 从启动看设计：运行态是一棵配置出来的插件树

入口 `apps/cli/src/bin.ts` 很薄。`@deepseek-ai/dsh` 的 `bin` 字段把 `dsh` 注册为命令行入口；它解析 `web`、`plugin`、`--profile`、`--dump-config` 等命令，再按模式加载对应模块。真正决定程序拥有什么能力的是 profile 与 bundle：基础 bundle 提供模型路由、持久化、沙箱、审批和设置；`web-app` 再挂上浏览器应用；`headless` 则是没有服务器的一次性运行器。

它们会按顺序叠加 Cordis 配置，随后再应用 profile、home 目录和命令行 `--patch` 的 patch。也就是说，用户看到的 `dsh` 不是一个固定产品，而是“最终配置树”运行出来的一个实例。

这个细节很工程化：patch 按配置项 id 替换整段配置，因此同一份发行版可以在不改源码的情况下，换 LLM、关 Web 搜索、增加工具，甚至替换某个 service 的实现。想看自己机器实际启动的树，项目提供了：

```bash
dsh --profile web --dump-config
```

这也解释了它为什么把“Everything is a Plugin”写得很重：不是营销标语，而是启动模型。需要强调的是，CLI 在这里是**启动与运维界面**，不是它目前面向用户的主要聊天界面；官方 README 展示的默认体验仍是 Web UI。源码的 help 示例还给出了 `dsh --profile headless "run the tests"`，用于一次性执行任务后打印结果并退出。

## 四种 Agent 模式，实质是四份组合配置

`apps/cli/config/agent-presets/` 里有四个预置：`standard`、`code`、`minimal`、`cordis`。它们不是同一条循环上的几个布尔开关，而是不同的 Agent-plane composition。

| 预置 | 源码上的关键差异 | 适合什么场景 |
| --- | --- | --- |
| `standard` | 文件、Shell、搜索、技能、计划、目标、子 Agent、workflow 等完整工具集 | 默认编码 Agent |
| `code`（PTC） | 继承标准能力，但增加工具呈现层，让模型用 TypeScript 程序组合多步调用 | 降低多轮工具调用开销 |
| `minimal` | 固定 prompt，只保留持久 shell 与 `str_replace_editor`，没有 compaction | 做极简环境的模型评测 |
| `cordis` | 面向创建 preset 与试验 Cordis 插件，附带对应技能 | 自定义 Harness |

`minimal/agent.cordis.yml` 很能说明问题：它明确把 persona 设成 `complete: true`，关闭运行时上下文注入，并且只装持久终端和编辑器。这个模式不是“功能缩水版标准模式”，而是刻意收紧变量，方便评估模型在有限工具与提示词下的真实能力。

另一个值得注意的细节是隔离。预置里的 service 往往放进 `cordis:group`，并用 `isolate` 创建私有 realm。源码在 `packages/preset/agent-presets/src/mount.ts` 会审计泄漏到 root realm 的 service：如果一个本该按会话隔离的服务错误地注册为进程全局，第二个会话挂载同一预置就可能碰撞。这个 guard 很朴素，却正好击中插件系统最容易出现的生命周期 bug。

## Agent Loop：不是 `while (true)`，而是一套可插拔的状态机

默认驱动器在 `packages/core/agent-loop/src/agent.ts`，类名叫 `ReactLoopAgent`。这里的 React 不是前端框架，而是“对输入和事件作出反应”的意思。

每个 Agent 有一个 inbox，并将输入分成两类：

- `followup()` 进入下一轮；
- `steer()` 进入当前工具步骤结束后的下一步；
- `inject()` 也进入下一步，但不会主动唤醒循环。

因此用户在模型执行过程中补充一句“先别改，告诉我方案”，不是粗暴取消并重新发起请求，而是能在下一个步骤边界被接走。这个 inbox 语义是长任务交互体验的基础。

一轮执行的大致顺序如下：

```text
turn/start
  领取 inbox 输入
  agent/pre-step（可改写或拒绝输入）
  step/start
  组装 prompt 与工具 schema
  LLM 流式输出 assistant/chunk
  固化 assistant/message
  执行 tool/call 与 tool/result
  step/end
  还有工具结果上下文或 steering？继续下一 step
turn/end
```

有两个实现选择特别值得借鉴。

第一，`agent/pre-step`、`agent/request`、`llm/stream` 以及工具前中后钩子都是 waterfall 事件：监听者必须调用 `next()` 才会放行后续处理。这给 compaction、提示词注入、重试、审批等横切能力提供了明确挂点，而不需要修改 loop。

第二，loop 对取消和错误的收口很严格。每个 turn 都会先追加 `turn/start`，无论正常、被拦截、取消还是报错，最终都会尝试追加带原因的 `turn/end`。这让“用户看到的执行状态”和“磁盘上的可恢复事实”保持一致。

## 会话不是聊天记录，而是事件源

`packages/core/session/src/index.ts` 的注释直接定义了它：append-only session log、内存 store，以及从日志派生出的 LLM history。

换句话说，模型并不直接拿一份可变的 messages 数组继续聊；请求历史是从 `SessionEvent` 投影出来的。`user/message`、`assistant/message`、`tool/result` 会进入模型可见历史，而流式 chunk、轮次开始结束、工具调用等事件则保留完整运行轨迹。

这样做会带来几个连锁收益：

1. UI 与模型不再各存一份“真相”。UI 订阅 `session/event` 渲染 chunk，模型从同一日志派生历史。
2. fork、resume、transcript、遥测和持久化都可以消费同一个事件流，不必为每个功能造一套状态同步。
3. 发生故障时能区分“模型输出过什么”“哪个工具已开始”“哪个结果已写入”，而不是只剩最终文本。

它也付出了代价：所有模型可见输入都必须被记录。项目文档甚至把这条写成运行时不变量——如果给模型额外注入了内容，就应该扩展 session event，并让它能从日志重新渲染。这个约束有些“较真”，但能防止恢复会话后上下文悄悄漂移。

## 工具调度比想象中复杂：并发执行，按模型顺序提交

工具调用调度在 `packages/core/agent-loop/src/tool-calls.ts`。它没有简单地 `Promise.all()`，而是把调用分成 exclusive barrier 和 bounded rolling pool。

核心策略可以概括为：

```text
模型按 A、B、C 的顺序发起调用
        │
        ├── 可并行的调用同时 dispatch，最多 maxParallelToolCalls 个
        ├── 独占调用成为屏障，等待前面的池排空
        └── 结果始终按 A、B、C 的模型顺序写回 session
```

为什么不让“谁先完成谁先回模型”？因为工具结果本身会成为下一步上下文。若文件搜索、编辑、测试的结果因网络或 CPU 抖动随机重排，同一个请求就可能得到不同轨迹，回放也不可靠。

更细的一层在工具流水线：`tools/pre-execute` 可以做权限、hook 和 sandbox 判断；随后才到工具 body；`tools/post-execute` 可以重写结果或注入额外上下文；最后才落为不可变的 `tool/result` 事件。被拒绝的调用也会有结构化结果，而不是静默消失。对 Agent 而言，这等于把“安全策略”和“工具实现”分开了。

## 真正的可替换单元：能力 seam

DeepSeek Harness 文档里有个很有用的词：capability seam。它不是泛泛的“接口”，而是三件套：service definition、service provider、consumer。

以 shell 为例：模型面对的是 shell tool；tool 依赖一个 shell service；shell service 再可能委托本地 subprocess 或远程 sandbox。把 provider 从本地替换为远程，并不需要 fork 出一套 Bash、PTY、LSP 的工具实现——消费方继续依赖同一个 seam 即可。

这也是这个项目最值得学习的地方：

- 不把“工具”与某个本地实现绑死；
- 不把“运行循环”与某个模型供应商绑死；
- 不把“持久化”与 UI 绑死；
- 不把扩展点藏在难以追踪的 monkey patch 里，而是放在有名称的 service 和事件上。

代价也很真实：仓库非常碎，配置与运行时作用域的概念门槛不低。第一次读源码时，不要从 Web 页面一路点进去；更有效的路线是先读 `docs/architecture.zh.md`，再看 `agent-loop`、`session` 与一个 preset 配置文件。先建立事件与作用域的心智模型，后面看几十个 package 才不会迷路。

## 写在最后

DeepSeek Harness 最有意思的地方，不是它又提供了多少工具，而是把一个 Agent 拆成了可以观察、替换、组合和回放的运行时部件。

如果你正在做内部编码助手、自动化工作流，或者只是想理解 Claude Code / Codex 这类工具为什么不只是“模型 + prompt”，这个项目都很值得读。尤其是它对 session event、工具顺序、作用域隔离和组合配置的处理，几乎就是 Agent 工程从 demo 走向可维护产品时必须补的四门课。

源码与文档入口：

- [DeepSeek Harness 仓库](https://github.com/deepseek-ai/deepseek-harness)
- [架构文档](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/architecture.zh.md)
- [Agent 生命周期时序图](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/agent-lifecycle.zh.md)
- [工具执行流水线](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/tool-execution-pipeline.zh.md)
