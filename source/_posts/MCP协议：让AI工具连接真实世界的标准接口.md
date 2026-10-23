---
title: MCP协议：让AI工具连接真实世界的标准接口
date: 2026-10-23 14:30:00
categories:
- AI编程
tags:
- MCP
- AI Agent
- 协议标准
- 工具集成
description: 深入解析 Anthropic 推出的 Model Context Protocol (MCP)，从协议设计、实现原理到实战集成，看懂 AI 工具生态如何通过标准化连接器走向互操作。
---

最近在整理 AI 工具栈时，发现一个值得关注的趋势：越来越多的 AI 助手开始支持 MCP（Model Context Protocol）。Cursor、Claude Desktop、Grok Bot 这些产品的设置里都能看到"MCP 连接器"或"MCP 服务器"选项，而 GitHub、Notion、Slack 等第三方服务也陆续提供了 MCP 实现。

这不是又一个"只有自家支持"的私有协议。MCP 由 Anthropic 提出并开源，定位是**让 AI 工具与外部服务对话的标准接口**，就像 HTTP 之于 Web、LSP 之于编辑器那样。它要解决的核心问题是：如何让模型安全、可控、标准化地访问真实世界的数据和能力。

这篇文章会从协议设计、技术实现到实战集成三个层次，拆解 MCP 到底是什么、为什么需要它、以及如何在自己的工具链里用起来。

![MCP 协议架构示意图：客户端、服务器与工具调用流程](/images/mcp-protocol-architecture.jpg)

*概念配图：MCP 的三层架构——宿主应用、MCP 客户端、MCP 服务器与工具提供方。*

<!--more-->

## 一、MCP 要解决什么问题

在 MCP 出现之前，让 AI 助手接入 Gmail、GitHub、数据库、内部 API 通常有三条路：

1. **应用内置集成**：每个 AI 工具自己实现 Gmail SDK、GitHub API，用户在设置里授权。问题是 N 个工具 × M 个服务 = N×M 次重复开发，且用户每换一个工具就要重新授权一遍。
2. **自然语言 + 网页操作**：让模型直接在浏览器里登录 Gmail、点按钮、复制粘�贴。这能覆盖长尾服务，但稳定性差、成本高、容易因页面改版失效。
3. **用户手写工具函数**：部分工具（如 LangChain）允许用户自定义 Python 函数并注册为 tool。灵活但缺乏标准，函数签名、错误处理、权限管理全靠自觉，换个框架就要重写。

MCP 的出发点是：**工具的实现应该与使用工具的 AI 框架解耦。** 就像编辑器不需要为每门语言各实现一套语法高亮和补全，而是通过 LSP 对接语言服务器；AI 助手也不应该为每个服务重复造适配层。

它给出的方案是一个三层模型：

```
AI 应用（Cursor / Claude Desktop）
    ↓  MCP 客户端
MCP 服务器（Gmail / GitHub / Notion...）
    ↓  原生 SDK 或 API
真实服务
```

服务提供方只需实现一次 MCP 服务器，就能被所有支持 MCP 的 AI 工具调用；AI 工具只需实现一次 MCP 客户端，就能接入整个 MCP 生态。用户的授权、配置、审批策略也随服务器配置走，不必在每个工具里重复设置。

## 二、协议设计：并不复杂，但很克制

MCP 的规范托管在 [modelcontextprotocol.io](https://modelcontextprotocol.io)，全文不到几千行，覆盖了协议核心、传输层、安全模型和扩展机制。

### 2.1 三个核心概念

MCP 定义了三种能力类型，服务器可以选择性实现：

| 能力类型 | 作用 | 典型例子 |
| --- | --- | --- |
| **Resources** | 只读数据源，供模型作为上下文 | 文档内容、数据库 schema、项目文件树 |
| **Tools** | 可执行操作，模型可以调用 | 发邮件、创建 Issue、运行测试 |
| **Prompts** | 预定义的提示词模板 | "帮我写周报""分析这个 PR 的改动" |

这个分类很工程化：

- **Resources** 设计为**拉模型**（模型按需读取），防止一次性把几 GB 文档灌进上下文。
- **Tools** 走的是**函数调用**（Function Calling），兼容 OpenAI、Anthropic、Google Gemini 的工具调用格式。
- **Prompts** 更像是"服务器推荐的使用方式"，降低用户编写提示词的门槛。

### 2.2 通信模型：JSON-RPC over stdio / HTTP

MCP 没有重新发明传输协议，而是直接用 JSON-RPC 2.0。服务器可以选择两种传输方式：

- **stdio 模式**：客户端启动服务器进程，通过标准输入输出收发 JSON-RPC 消息。适合本地工具、命令行脚本、需要访问本机文件系统的场景。
- **HTTP/SSE 模式**：服务器独立运行（通常是远程服务），客户端通过 HTTP 请求调用，服务器用 Server-Sent Events 推送通知。适合云端服务、需要多客户端共享的场景。

这个设计让 MCP 能同时覆盖"启动本地 Python 脚本读项目文件"和"连接远程 Notion API"两类场景，而不需要额外的适配层。

### 2.3 权限与审批：留给客户端实现

MCP 规范**刻意不规定权限模型**。协议只定义了工具的 schema（参数、返回值、描述），但哪些工具需要审批、用户如何授权、是否记录调用日志，全由客户端（即 AI 应用）决定。

这个选择有利有弊：

- **好处**：服务器实现简单，不需要处理复杂的权限策略；同一个 MCP 服务器可以适配不同客户端的安全要求（企业版可能强制审批，个人版可能默认信任）。
- **代价**：安全模型碎片化。用户在 Cursor 里设置的审批策略，换到 Claude Desktop 就要重新配置。长期来看，社区可能会推动"审批策略配置"也标准化。

## 三、实现一个 MCP 服务器：以 GitHub 为例

官方提供了 Python、TypeScript、Rust 的 SDK，这里以 TypeScript 为例，看一个最小的 GitHub MCP 服务器怎么写。

### 3.1 初始化项目与依赖

```bash
mkdir mcp-github-server
cd mcp-github-server
npm init -y
npm install @modelcontextprotocol/sdk @octokit/rest
```

### 3.2 定义工具：列出仓库的 Issue

```typescript
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { Octokit } from "@octokit/rest";

const server = new Server(
  {
    name: "mcp-github",
    version: "0.1.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// 定义工具：列出 Issue
server.setRequestHandler("tools/list", async () => {
  return {
    tools: [
      {
        name: "list_issues",
        description: "列出指定仓库的 Issue",
        inputSchema: {
          type: "object",
          properties: {
            owner: { type: "string", description: "仓库所有者" },
            repo: { type: "string", description: "仓库名称" },
            state: {
              type: "string",
              enum: ["open", "closed", "all"],
              description: "Issue 状态",
            },
          },
          required: ["owner", "repo"],
        },
      },
    ],
  };
});

// 实现工具调用
server.setRequestHandler("tools/call", async (request) => {
  if (request.params.name === "list_issues") {
    const { owner, repo, state = "open" } = request.params.arguments;
    
    const octokit = new Octokit({
      auth: process.env.GITHUB_TOKEN,
    });

    const { data: issues } = await octokit.rest.issues.listForRepo({
      owner,
      repo,
      state,
    });

    return {
      content: [
        {
          type: "text",
          text: JSON.stringify(
            issues.map((issue) => ({
              number: issue.number,
              title: issue.title,
              state: issue.state,
              url: issue.html_url,
            })),
            null,
            2
          ),
        },
      ],
    };
  }

  throw new Error(`Unknown tool: ${request.params.name}`);
});

// 启动 stdio 传输
const transport = new StdioServerTransport();
await server.connect(transport);
```

### 3.3 配置到 Cursor / Claude Desktop

在客户端配置文件（通常是 `~/.cursor/mcp_config.json` 或 `~/Library/Application Support/Claude/claude_desktop_config.json`）中注册服务器：

```json
{
  "mcpServers": {
    "github": {
      "command": "node",
      "args": ["/path/to/mcp-github-server/index.js"],
      "env": {
        "GITHUB_TOKEN": "ghp_your_token_here"
      }
    }
  }
}
```

重启客户端后，AI 助手就能调用 `list_issues` 工具了。

## 四、MCP 的工程优势与局限

### 4.1 为什么值得采用

1. **生态复用**：写一次 MCP 服务器，就能被 Cursor、Claude Desktop、Grok Bot、未来更多支持 MCP 的工具调用。不再需要为每个 AI 框架写一套适配器。
2. **权限集中管理**：GitHub Token、数据库凭据、API 密钥存在 MCP 服务器配置里，不会泄漏到 AI 应用的日志或上下文中。
3. **本地 + 云端灵活部署**：stdio 模式适合访问本机文件、数据库；HTTP 模式适合共享服务、企业统一部署。
4. **逐步迁移路径**：可以先用 MCP 包装现有的内部 API 或 SDK，后续再优化。不需要推倒重来。

### 4.2 当前的局限

1. **审批策略未标准化**：每个客户端有自己的审批 UI 和策略，用户体验不一致。
2. **错误处理粗糙**：规范只定义了基本的错误码，工具调用失败时的重试、回退、部分结果处理，全靠客户端自己实现。
3. **上下文窗口管理缺位**：Resources 可以返回任意大小的数据，但如何分块、如何让模型按需读取、如何缓存，协议层没有指导。
4. **生态尚在早期**：虽然官方和社区已有几十个 MCP 服务器实现（参见 [MCP Servers](https://github.com/modelcontextprotocol/servers)），但质量参差不齐，部分服务器长期不维护。

### 4.3 与 OpenAI Plugins / Anthropic Tool Use 的关系

| 维度 | MCP | OpenAI Plugins | Anthropic Tool Use |
| --- | --- | --- | --- |
| 定位 | **工具与 AI 应用之间的协议** | 插件市场 | 模型调用工具的能力 |
| 跨应用 | 是（任何支持 MCP 的客户端） | 否（只能在 ChatGPT 内使用） | 否（只能通过 Anthropic API 调用） |
| 实现位置 | 独立进程或远程服务 | 云端 API | 用户代码或客户端 |
| 典型场景 | AI 助手访问 GitHub、Notion、数据库 | ChatGPT 插件商店 | 让 Claude 调用自定义函数 |

MCP 更偏"协议"而非"平台"。它不关心工具从哪来（可以是官方的、社区的、你自己写的），只关心怎么标准化地调用它们。

## 五、实战场景：什么时候该用 MCP

### 场景一：多个 AI 工具共享同一套能力

你的团队同时用 Cursor 写代码、用 Claude Desktop 处理文档、用 Grok Bot 自动化运维。如果每个工具都单独对接 GitHub、Jira、内部 Wiki，就要维护三套凭据和配置。

**方案**：部署统一的 MCP 服务器（HTTP 模式），三个工具都连到同一个服务器。凭据、审批策略、调用日志集中管理。

### 场景二：访问本地文件系统或专有数据

AI 助手需要读取本机的日志文件、数据库、配置文件，或者调用只能在内网访问的 API。

**方案**：写一个 stdio 模式的 MCP 服务器，限定它只能访问指定目录或端口。客户端启动服务器时，通过环境变量传入凭据，不会泄漏到云端。

### 场景三：标准化内部工具，降低 AI 接入成本

公司有几十个内部服务（发布平台、监控、工单系统），每次上新 AI 工具都要重新写适配器。

**方案**：为每个内部服务写一个 MCP 服务器，发布到内部 npm/pip 仓库。新 AI 工具接入时，只需实现 MCP 客户端，不用重新对接服务。

## 六、如何开始：推荐路径

### 第一步：用现成的 MCP 服务器

不要上来就写代码。先在 [MCP Servers](https://github.com/modelcontextprotocol/servers) 仓库里找一个你常用的服务（GitHub、Notion、Slack、PostgreSQL），按 README 配置到 Cursor 或 Claude Desktop，体验一下工具调用流程。

### 第二步：包装一个已有的 SDK

选一个你熟悉的服务（比如自己公司的内部 API），用官方 SDK 先实现基本的查询和操作，然后用 MCP SDK 包装成工具。不用追求完美，先让它能跑起来。

### 第三步：处理边界情况

补上错误处理、参数校验、结果分页、权限检查。这一步是工程质量的分水岭。观察 AI 调用时常出现的失败模式，针对性加固。

### 第四步：发布与维护

如果你的 MCP 服务器对其他人也有用，可以考虑开源或发布到内部工具库。记得写清楚配置方式、环境变量、权限要求，以及常见问题排查。

## 七、总结：MCP 是基础设施，不是银弹

MCP 不会让 AI 突然变聪明，也不会自动解决工具调用的所有问题。它的价值在于**降低重复劳动**和**提高互操作性**。

就像 LSP 没有让每个编辑器都变成 VS Code，但确实让"支持 100 种语言"从不可能变成可能；MCP 也不会让每个 AI 助手都达到同样的能力，但能让"接入 100 个服务"不再需要 N×M 次重复开发。

对技术负责人而言，MCP 的意义是：

- **降低 AI 工具的接入门槛**：新工具上线不再需要重新对接所有服务。
- **统一凭据与审批管理**：不用担心密钥散落在各个工具的配置文件里。
- **加速内部工具 AI 化**：把现有服务包装成 MCP 服务器，就能快速接入各类 AI 助手。

如果你的团队正在评估 AI 工具栈，或者在考虑如何让 AI 助手安全地访问内部系统，MCP 值得列入技术选型的考虑范围。不是因为它完美，而是因为它正在成为事实标准。

## 参考资料

- [Model Context Protocol 官方规范](https://modelcontextprotocol.io)
- [MCP TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [官方 MCP 服务器实现集合](https://github.com/modelcontextprotocol/servers)
- [Anthropic MCP 公告博客](https://www.anthropic.com/news/model-context-protocol)
- [Cursor MCP 文档](https://docs.cursor.com/advanced/model-context-protocol)

---

*本文基于 MCP 协议当前版本（截至 2026-10-23）撰写。协议仍在快速迭代，部分细节可能随版本更新而变化，请以官方文档为准。*
