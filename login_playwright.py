#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import argparse
import logging
from datetime import datetime
from playwright.sync_api import sync_playwright

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def login_nodeloc(username, password, headless=True):
    """
    使用Playwright自动登录NodeLoc网站
    
    Args:
        username (str): 用户名或邮箱
        password (str): 密码
        headless (bool): 是否使用无头模式
        
    Returns:
        bool: 登录是否成功
    """
    try:
        logger.info("启动Playwright...")
        with sync_playwright() as playwright:
            # 启动浏览器
            browser_type = playwright.chromium
            browser = browser_type.launch(headless=headless)
            
            # 创建新的上下文和页面
            context = browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = context.new_page()
            
            # 访问登录页面
            logger.info("访问NodeLoc网站...")
            page.goto("https://www.nodeloc.com/")
            
            # 点击登录按钮打开登录窗口
            logger.info("打开登录窗口...")
            page.click('button:has-text("登录")')
            
            # 等待登录表单加载
            page.wait_for_selector('input[placeholder="用户名或邮箱"]')
            
            # 输入用户名和密码
            logger.info(f"输入用户名: {username[:2]}***...")
            page.fill('input[placeholder="用户名或邮箱"]', username)
            
            logger.info("输入密码...")
            page.fill('input[placeholder="密码"]', password)
            
            # 勾选"记住我的登录状态"
            checkbox = page.locator('input[type="checkbox"]')
            if not checkbox.is_checked():
                checkbox.check()
                logger.info("已勾选'记住我的登录状态'")
            
            # 点击登录按钮提交表单
            logger.info("提交登录表单...")
            # 使用JavaScript点击登录按钮，避免被不可见层拦截
            page.evaluate('''() => {
                const loginButtons = Array.from(document.querySelectorAll('button')).filter(btn => 
                    btn.textContent.trim() === '登录' && btn.offsetParent !== null);
                if (loginButtons.length > 0) {
                    loginButtons[0].click();
                }
            }''')
            
            # 等待登录成功
            try:
                # 等待一段时间让登录处理完成
                logger.info("等待登录处理完成...")
                time.sleep(5)
                
                # 等待页面加载完成
                page.wait_for_load_state("networkidle")
                
                # 验证登录状态
                page_content = page.content().lower()
                if "登录" not in page_content or username.lower() in page_content:
                    logger.info("登录成功!")
                    
                    # 截图保存登录成功的页面
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    screenshot_path = f"nodeloc_login_{timestamp}.png"
                    page.screenshot(path=screenshot_path)
                    logger.info(f"已保存登录成功截图: {screenshot_path}")
                    
                    # 访问任务页面以完成每日签到
                    try:
                        logger.info("尝试访问任务页面...")
                        page.goto("https://www.nodeloc.com/tasks")
                        page.wait_for_load_state("networkidle")
                        logger.info("已访问任务页面，可能已完成每日签到")
                        
                        # 再次截图
                        tasks_screenshot_path = f"nodeloc_tasks_{timestamp}.png"
                        page.screenshot(path=tasks_screenshot_path)
                        logger.info(f"已保存任务页面截图: {tasks_screenshot_path}")
                    except Exception as e:
                        logger.warning(f"访问任务页面时出错: {str(e)}")
                    
                    # 关闭浏览器
                    browser.close()
                    return True
                else:
                    logger.error("登录可能失败，未检测到登录成功的标志")
                    browser.close()
                    return False
                    
            except Exception as e:
                logger.error(f"等待登录成功时出错: {str(e)}")
                browser.close()
                return False
                
    except Exception as e:
        logger.error(f"登录过程中发生错误: {str(e)}")
        return False

def main():
    """主函数，处理命令行参数并执行登录"""
    parser = argparse.ArgumentParser(description='NodeLoc自动登录脚本')
    parser.add_argument('--username', type=str, help='NodeLoc用户名或邮箱')
    parser.add_argument('--password', type=str, help='NodeLoc密码')
    parser.add_argument('--no-headless', action='store_true', help='不使用无头模式（显示浏览器界面）')
    
    args = parser.parse_args()
    
    # 从环境变量或命令行参数获取凭据
    username = args.username or os.environ.get('NODELOC_USERNAME')
    password = args.password or os.environ.get('NODELOC_PASSWORD')
    
    if not username or not password:
        logger.error("错误: 未提供用户名或密码。请通过命令行参数或环境变量提供。")
        return 1
    
    # 执行登录
    success = login_nodeloc(username, password, not args.no_headless)
    
    if success:
        # 记录登录时间
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"登录成功 - {timestamp}"
        
        # 保存登录记录
        with open("login_history.log", "a") as f:
            f.write(f"{log_message}\n")
            
        logger.info(f"登录记录已保存")
        return 0
    else:
        logger.error("登录失败")
        return 1

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
