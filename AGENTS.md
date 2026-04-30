# Repository Guidelines

## 项目结构与模块组织

本仓库是基于 Hexo 5.4 和 NexT 主题的静态博客。源内容位于 `source/`：文章放在 `source/_posts/`，独立页面位于 `source/about/`、`source/categories/` 和 `source/tags/`，自定义域名配置在 `source/CNAME`。站点主配置文件是 `_config.yml`，主题配置和模板在 `themes/next/`，文章模板在 `scaffolds/`。生成后的静态文件会写入 `public/`，同时仓库根目录也包含 `index.html`、`archives/`、`tags/`、`categories/`、`css/`、`js/` 等已生成内容。除非明确需要修改发布产物，否则优先修改源文件和配置文件。

## 构建、测试与本地开发命令

- `npm install`：安装 Hexo 和插件依赖。
- `npm run server`：启动本地预览服务，通常访问 `http://localhost:4000`。
- `npm run clean`：清理 Hexo 缓存和已生成文件。
- `npm run build`：生成静态站点到 `public/`。
- `npm run deploy`：通过 `hexo-deployer-git` 部署到 GitHub Pages。
- `npx hexo new post "文章标题"`：基于 `scaffolds/post.md` 创建新文章。

## 编码风格与命名约定

文章使用 Markdown 编写，并包含 YAML Front Matter。中文文章标题和文件名应保持一致，例如 `source/_posts/Dart语言基础三：运算符.md`。YAML 文件使用两个空格缩进，并延续现有 Hexo/NexT 配置风格。仓库中的 JavaScript 和 CSS 多数是生成文件、主题文件或第三方资源；能通过 Hexo 配置、主题配置或 Markdown 内容完成的改动，不要直接修改构建产物。

## 测试指南

本仓库未配置自动化测试。提交前建议运行 `npm run clean` 和 `npm run build`，再使用 `npm run server` 本地检查页面导航、文章渲染、标签/分类、搜索数据、Live2D 展示和自定义页面是否正常。

## 提交与 Pull Request 规范

近期提交历史使用简短的中文说明，例如 `添加项目README文档`，部署生成提交常见格式为 `Site updated: YYYY-MM-DD HH:mm:ss`。提交应保持聚焦，尽量一个内容或配置变更对应一个提交；只有在发布需要时才包含生成后的站点文件。PR 应说明改动内容，列出已执行的验证命令，必要时关联 issue；涉及主题、布局或页面视觉变化时，请附截图。

## 安全与配置提示

不要提交私有凭据、分析服务密钥或本地环境文件。部署前检查 `_config.yml`、`themes/next/_config.yml` 和 `source/CNAME`，这些配置会直接影响线上站点 `devloong.com`。
