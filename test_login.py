#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试脚本 - 用于测试NodeLoc自动登录功能
"""

import os
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

# 导入登录模块
sys.path.append('/home/ubuntu/nodeloc_login')
from login import login_nodeloc

def main():
    # 测试登录
    username = "hguh"
    password = "hgu123ccC!"
    
    print(f"开始测试登录功能，用户名: {username}")
    
    # 使用非无头模式进行测试，以便观察登录过程
    success = login_nodeloc(username, password, headless=False)
    
    if success:
        print("✅ 测试成功: 登录成功!")
        return 0
    else:
        print("❌ 测试失败: 登录未成功!")
        return 1

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
