# 个人博客项目

这是一个基于 Hexo 框架构建的个人博客网站，使用 Next 主题。

## 项目信息

- **框架**: Hexo
- **主题**: Next
- **部署平台**: GitHub Pages
- **自定义域名**: devloong.com
- **仓库地址**: https://github.com/SSLoong/sunshenglong.github.io

## 本地开发

### 环境要求

- Node.js (推荐 v14 或更高版本)
- npm 或 yarn

### 安装依赖

```bash
npm install
```

### 本地预览

```bash
# 启动本地服务器
hexo server
# 或简写
hexo s
```

访问 http://localhost:4000 预览博客。

### 创建新文章

```bash
# 创建新文章
hexo new "文章标题"
# 创建新页面
hexo new page "页面名称"
```

### 生成静态文件

```bash
# 清理缓存
hexo clean
# 生成静态文件
hexo generate
# 或简写
hexo g
```

## 部署

### 自动部署到 GitHub Pages

```bash
# 部署到 GitHub Pages
hexo deploy
# 或简写
hexo d
```

### 一键生成并部署

```bash
hexo g -d
```

## 项目结构

```
├── _config.yml          # Hexo 配置文件
├── package.json         # 项目依赖
├── source/             # 源文件目录
│   ├── _posts/         # 文章目录
│   ├── about/          # 关于页面
│   ├── categories/     # 分类页面
│   ├── tags/           # 标签页面
│   └── CNAME           # 自定义域名配置
├── themes/             # 主题目录
│   └── next/           # Next 主题
├── public/             # 生成的静态文件
└── .deploy_git/        # Git 部署目录
```

## 配置说明

### 网站基本信息

在 `_config.yml` 中配置网站的基本信息：

- `title`: 网站标题
- `subtitle`: 网站副标题
- `description`: 网站描述
- `author`: 作者信息
- `url`: 网站 URL

### 部署配置

```yaml
deploy:
  type: git
  repo: https://github.com/SSLoong/sunshenglong.github.io.git
  branch: master
```

### 自定义域名

在 `source/CNAME` 文件中配置自定义域名：
```
devloong.com
```

## 主题配置

本项目使用 Next 主题，主题配置文件位于 `themes/next/_config.yml`。

主要配置项：
- 网站图标和头像
- 菜单导航
- 社交链接
- 评论系统
- 搜索功能
- Live2D 看板娘

## 文章管理

### 文章格式

文章使用 Markdown 格式编写，文件头部需要包含 Front Matter：

```markdown
---
title: 文章标题
date: 2021-07-01 10:00:00
categories: 分类
tags:
  - 标签1
  - 标签2
---

文章内容...
```

### 已发布文章

- Dart语言概览
- Dart语言基础一：变量与类型
- Dart语言基础二：函数
- Dart语言基础三：运算符

## 访问地址

- **GitHub Pages**: https://ssloong.github.io/sunshenglong.github.io/
- **自定义域名**: https://devloong.com (配置完成后)
- **本地预览**: http://localhost:4000

## 注意事项

1. 每次修改配置文件后，需要重启本地服务器
2. 部署前建议先在本地预览确认无误
3. 自定义域名需要在域名服务商处配置 DNS 解析
4. GitHub Pages 部署可能需要几分钟时间生效

## 许可证

本项目采用 MIT 许可证。