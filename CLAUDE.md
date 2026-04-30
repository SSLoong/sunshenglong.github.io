# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

这是一个基于 Hexo 的个人技术博客站点，名为 "Loong's Blog"。使用升级版的 Next 主题，支持评论功能，主要发布 iOS 开发和 AI 编程相关的技术文章。博客已正式部署并可通过 https://devloong.com/ 域名访问。

## 项目架构

### 核心框架
- **Hexo 5.4.0**: 静态站点生成器
- **Next 主题**: 博客主题 (已升级到最新版本)
- **评论系统**: 已集成评论功能
- **Live2D**: 看板娘插件 (hexo-helper-live2d@3.1.1)

### 目录结构
```
├── _config.yml          # Hexo 主配置文件
├── package.json         # 项目依赖和脚本
├── source/              # 源文件目录
│   ├── _posts/          # 博客文章 Markdown 文件
│   ├── about/           # 关于页面
│   ├── categories/      # 分类页面
│   ├── tags/           # 标签页面
│   └── CNAME           # 自定义域名配置
├── themes/next/         # Next 主题文件
├── scaffolds/           # 文章模板
├── public/              # 生成的静态文件
└── .deploy_git/         # Git 部署文件
```

### 内容管理
- **文章位置**: `source/_posts/` 目录下的 Markdown 文件
- **文章模板**: `scaffolds/post.md` 定义新文章的默认格式
- **Front Matter**: 包含标题、日期、分类、标签等元数据
- **分类系统**: 支持分类和标签双重组织方式
- **主要内容方向**: iOS 开发技术、AI 编程实践

## 常用命令

### 开发命令
```bash
# 启动本地开发服务器
npm run server
# 或
hexo server

# 清理缓存和生成的文件
npm run clean
# 或
hexo clean

# 生成静态文件
npm run build
# 或
hexo generate

# 部署到 GitHub Pages
npm run deploy
# 或
hexo deploy
```

### 内容管理
```bash
# 创建新文章
hexo new post "文章标题"

# 创建新页面
hexo new page "页面名"

# 生成并启动服务（常用组合）
hexo clean && hexo generate && hexo server
```

## 配置要点

### 站点配置 (_config.yml)
- **部署配置**: 使用 hexo-deployer-git 部署到 GitHub
- **搜索功能**: 集成 hexo-generator-searchdb 
- **Live2D**: 配置看板娘显示位置和模型
- **permalink**: 使用 `:year/:month/:day/:title/` 格式

### 主题配置
- 使用 Next 主题，位于 `themes/next/`
- 主题配置文件: `themes/next/_config.yml`
- 支持多种布局方案: Muse, Mist, Pisces, Gemini

### 部署流程
1. 文章编写在 `source/_posts/` 目录
2. 使用 `hexo generate` 生成静态文件到 `public/` 
3. 使用 `hexo deploy` 推送到 GitHub Pages 仓库 (master 分支)
4. 博客正式运行在 https://devloong.com/ 域名

## 开发注意事项

- 所有博客文章使用中文编写
- 文章主要聚焦 iOS 开发和 AI 编程技术内容
- 建议的内容分类：iOS开发、Swift编程、AI编程、机器学习、技术实践等
- 新文章需要设置合适的分类和标签
- 评论功能已启用，考虑读者互动体验
- 图片资源需要考虑加载性能（特别是代码截图和架构图）
- 部署前建议本地预览确认效果
- 博客已正式上线，注意内容质量和用户体验