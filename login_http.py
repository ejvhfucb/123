#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import argparse
import logging
import json
import requests
from datetime import datetime

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

class NodeLocLogin:
    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://www.nodeloc.com"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Origin": "https://www.nodeloc.com",
            "Referer": "https://www.nodeloc.com/"
        }
        
    def login(self, username, password):
        """
        登录NodeLoc网站
        
        Args:
            username (str): 用户名或邮箱
            password (str): 密码
            
        Returns:
            bool: 登录是否成功
        """
        try:
            # 第1步: 访问首页获取cookies
            logger.info("访问NodeLoc网站首页...")
            response = self.session.get(
                self.base_url,
                headers=self.headers
            )
            response.raise_for_status()
            
            # 第2步: 尝试直接登录
            logger.info(f"尝试登录，用户名: {username[:2]}***...")
            login_data = {
                "username": username,
                "password": password,
                "remember": "true"
            }
            
            # 尝试常见的登录API端点
            login_endpoints = [
                "/api/v1/login",
                "/api/login",
                "/login",
                "/user/login",
                "/auth/login"
            ]
            
            login_success = False
            for endpoint in login_endpoints:
                try:
                    login_url = f"{self.base_url}{endpoint}"
                    logger.info(f"尝试登录端点: {endpoint}")
                    
                    login_response = self.session.post(
                        login_url,
                        json=login_data,
                        headers=self.headers
                    )
                    
                    # 检查登录是否成功
                    if login_response.status_code == 200:
                        try:
                            result = login_response.json()
                            if result.get("success") or result.get("code") == 0 or result.get("status") == "success":
                                logger.info(f"登录成功! 使用端点: {endpoint}")
                                login_success = True
                                break
                        except:
                            # 如果不是JSON响应，检查cookies或其他标志
                            if "token" in self.session.cookies or "auth" in self.session.cookies:
                                logger.info(f"登录可能成功! 使用端点: {endpoint}")
                                login_success = True
                                break
                    
                    logger.warning(f"端点 {endpoint} 登录失败，状态码: {login_response.status_code}")
                except Exception as e:
                    logger.warning(f"尝试端点 {endpoint} 时出错: {str(e)}")
            
            # 第3步: 验证登录状态
            if login_success:
                logger.info("验证登录状态...")
                profile_response = self.session.get(
                    f"{self.base_url}/api/user/profile",
                    headers=self.headers
                )
                
                if profile_response.status_code == 200:
                    try:
                        profile_data = profile_response.json()
                        if profile_data.get("username") or profile_data.get("user"):
                            logger.info("验证成功: 已登录状态")
                            return True
                    except:
                        pass
            
            # 如果上述方法都失败，尝试模拟表单提交
            logger.info("尝试模拟表单提交...")
            form_data = {
                "username": username,
                "password": password,
                "remember": "on"
            }
            
            form_login_response = self.session.post(
                f"{self.base_url}/login",
                data=form_data,
                headers=self.headers,
                allow_redirects=True
            )
            
            # 检查登录后的页面是否包含用户名
            if username.lower() in form_login_response.text.lower():
                logger.info("表单登录成功!")
                return True
                
            logger.error("所有登录尝试均失败")
            return False
            
        except Exception as e:
            logger.error(f"登录过程中发生错误: {str(e)}")
            return False
    
    def check_daily_task(self):
        """
        检查每日任务状态
        
        Returns:
            bool: 是否成功检查了每日任务
        """
        try:
            logger.info("检查每日任务状态...")
            
            # 访问首页或任务页面
            response = self.session.get(
                f"{self.base_url}/tasks",
                headers=self.headers
            )
            
            if response.status_code == 200:
                logger.info("成功访问任务页面")
                return True
            else:
                logger.warning(f"访问任务页面失败，状态码: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"检查每日任务时发生错误: {str(e)}")
            return False

def main():
    """主函数，处理命令行参数并执行登录"""
    parser = argparse.ArgumentParser(description='NodeLoc自动登录脚本')
    parser.add_argument('--username', type=str, help='NodeLoc用户名或邮箱')
    parser.add_argument('--password', type=str, help='NodeLoc密码')
    
    args = parser.parse_args()
    
    # 从环境变量或命令行参数获取凭据
    username = args.username or os.environ.get('NODELOC_USERNAME')
    password = args.password or os.environ.get('NODELOC_PASSWORD')
    
    if not username or not password:
        logger.error("错误: 未提供用户名或密码。请通过命令行参数或环境变量提供。")
        return 1
    
    # 执行登录
    client = NodeLocLogin()
    login_success = client.login(username, password)
    
    if login_success:
        # 登录成功后检查每日任务
        task_check_success = client.check_daily_task()
        
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
