# NodeLoc 每日自动登录脚本使用说明

本项目提供了一个自动登录 NodeLoc 网站的解决方案，使用 GitHub Actions 实现每日自动执行，无需本地服务器。

## 功能特点

- 使用 Playwright 自动化登录 NodeLoc 网站
- 通过 GitHub Actions 实现每日定时执行
- 自动保存登录截图和历史记录
- 可配置邮件通知功能
- 支持手动触发和定时执行

## 部署步骤

### 1. 创建 GitHub 仓库

1. 登录您的 GitHub 账号
2. 创建一个新的仓库（可以是私有仓库，推荐）
3. 将本项目文件上传到该仓库

### 2. 配置 GitHub Secrets

在仓库中添加以下 Secrets（敏感信息），路径：仓库 → Settings → Secrets and variables → Actions → New repository secret

必需的 Secrets：
- `NODELOC_USERNAME`: 您的 NodeLoc 用户名
- `NODELOC_PASSWORD`: 您的 NodeLoc 密码

可选的邮件通知 Secrets（如需启用邮件通知）：
- `EMAIL_USERNAME`: 发送通知的邮箱地址
- `EMAIL_PASSWORD`: 邮箱的应用专用密码（不是登录密码）
- `NOTIFICATION_EMAIL`: 接收通知的邮箱地址

### 3. 启用 GitHub Actions

1. 在仓库中点击 "Actions" 选项卡
2. 如果看到提示，点击 "I understand my workflows, go ahead and enable them"
3. 您应该能看到 "NodeLoc 每日自动登录" 工作流

### 4. 测试自动登录

1. 在 Actions 页面找到 "NodeLoc 每日自动登录" 工作流
2. 点击 "Run workflow" → "Run workflow" 手动触发一次
3. 等待工作流执行完成，检查结果

## 工作流说明

- 定时执行：每天北京时间上午 8:30（UTC 时间 0:30）自动运行
- 手动触发：可以随时通过 GitHub Actions 界面手动触发
- 执行结果：每次执行后会上传登录截图和日志，保留 7 天
- 邮件通知：如果配置了邮件相关的 Secrets，将发送执行结果通知

## 文件说明

- `login_playwright.py`: 主要的登录脚本，使用 Playwright 实现自动登录
- `.github/workflows/daily_login.yml`: GitHub Actions 工作流配置文件

## 邮件通知配置说明

如果您想启用邮件通知功能，需要：

1. 创建一个用于发送通知的邮箱（推荐使用 Gmail）
2. 在邮箱设置中生成"应用专用密码"（不是您的登录密码）
3. 将邮箱地址和应用专用密码添加到 GitHub Secrets 中

## 故障排除

如果自动登录失败，请检查：

1. NodeLoc 账号凭据是否正确
2. 网站登录机制是否发生变化
3. GitHub Actions 日志中的详细错误信息

## 注意事项

- 请确保您的 NodeLoc 账号凭据安全，使用私有仓库存储脚本
- 如果 NodeLoc 网站结构发生变化，可能需要更新脚本
- 频繁的自动登录可能会被网站检测为异常行为，请合理使用

## 自定义配置

如需修改执行时间或其他配置，请编辑 `.github/workflows/daily_login.yml` 文件：

- 修改 `cron` 表达式可以更改执行时间
- 调整 `retention-days` 可以更改结果保留天数

## 更新维护

如果脚本不再工作，可能是因为网站结构变化。请检查：

1. 登录表单元素是否变化
2. 登录验证方式是否变化
3. 网站是否添加了新的反爬虫措施

根据需要更新 `login_playwright.py` 文件中的选择器和逻辑。
