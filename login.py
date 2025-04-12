#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import argparse
import logging
from datetime import datetime
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def login_nodeloc(username, password, headless=True):
    """
    使用Selenium自动登录NodeLoc网站
    
    Args:
        username (str): 用户名或邮箱
        password (str): 密码
        headless (bool): 是否使用无头模式
        
    Returns:
        bool: 登录是否成功
    """
    try:
        # 设置Chrome选项
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # 添加唯一的用户数据目录
        import tempfile
        import uuid
        user_data_dir = os.path.join(tempfile.gettempdir(), f"chrome_profile_{uuid.uuid4().hex}")
        chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
        
        # 在GitHub Actions环境中
        if os.environ.get('GITHUB_ACTIONS') == 'true':
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-setuid-sandbox")
            
        # 初始化WebDriver
        logger.info("初始化WebDriver...")
        # 使用Service对象明确指定ChromeDriver路径
        from webdriver_manager.chrome import ChromeDriverManager
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # 访问登录页面
        logger.info("访问NodeLoc网站...")
        driver.get("https://www.nodeloc.com/")
        
        # 等待页面加载完成
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//button[contains(text(), '登录')]"))
        )
        
        # 点击登录按钮打开登录窗口
        logger.info("打开登录窗口...")
        login_button = driver.find_element(By.XPATH, "//button[contains(text(), '登录')]")
        login_button.click()
        
        # 等待登录表单加载
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@placeholder='用户名或邮箱']"))
        )
        
        # 输入用户名和密码
        logger.info(f"输入用户名: {username[:2]}***...")
        username_input = driver.find_element(By.XPATH, "//input[@placeholder='用户名或邮箱']")
        username_input.send_keys(username)
        
        logger.info("输入密码...")
        password_input = driver.find_element(By.XPATH, "//input[@placeholder='密码']")
        password_input.send_keys(password)
        
        # 勾选"记住我的登录状态"
        try:
            remember_checkbox = driver.find_element(By.XPATH, "//input[@type='checkbox']")
            if not remember_checkbox.is_selected():
                remember_checkbox.click()
                logger.info("已勾选'记住我的登录状态'")
        except NoSuchElementException:
            logger.warning("未找到'记住我的登录状态'复选框")
        
        # 点击登录按钮提交表单
        logger.info("提交登录表单...")
        submit_button = driver.find_element(By.XPATH, "//button[text()='登录']")
        submit_button.click()
        
        # 等待登录成功
        try:
            WebDriverWait(driver, 15).until(
                EC.invisibility_of_element_located((By.XPATH, "//button[text()='登录']"))
            )
            
            # 验证登录状态
            time.sleep(3)  # 等待页面完全加载
            if "登录" not in driver.page_source and username.lower() in driver.page_source.lower():
                logger.info("登录成功!")
                
                # 截图保存登录成功的页面
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                screenshot_path = f"nodeloc_login_{timestamp}.png"
                driver.save_screenshot(screenshot_path)
                logger.info(f"已保存登录成功截图: {screenshot_path}")
                
                driver.quit()
                return True
            else:
                logger.error("登录可能失败，未检测到登录成功的标志")
                driver.quit()
                return False
                
        except TimeoutException:
            logger.error("登录超时，可能遇到验证码或其他问题")
            driver.quit()
            return False
            
    except Exception as e:
        logger.error(f"登录过程中发生错误: {str(e)}")
        try:
            driver.quit()
        except:
            pass
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
    
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
