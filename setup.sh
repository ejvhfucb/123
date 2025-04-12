#!/bin/bash
# 安装脚本 - 用于在新环境中设置NodeLoc自动登录

# 安装依赖
echo "安装依赖..."
pip install playwright requests

# 安装Playwright浏览器
echo "安装Playwright浏览器..."
playwright install chromium

echo "安装完成！"
echo "请按照README.md中的说明配置GitHub仓库和Secrets。"
