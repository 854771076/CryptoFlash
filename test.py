#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CryptoFlash程序入口
"""

from core.service import CryptoFlashService
from utils.logger import logger
import os
os.environ['NITTER_INSTANCE']='http://156.229.162.55:8081/'
os.environ['TWITTER_USERNAME']='elonmusk,elonmusk2'
# os.environ["DINGTALK_WEBHOOK"] = "http://test-webhook1,http://test-webhook2"
# os.environ["DINGTALK_SECRET"] = "test-secret1,test-secret2"
# os.environ["DINGTALK_SOURCES"] = "['source1','source2'],['source1']"
# # 邮箱
# os.environ["EMAIL_SMTP_SERVER"] = "smtp.example.com"
# os.environ["EMAIL_SMTP_PORT"] = "465"
# os.environ["EMAIL_SMTP_USER"] = "user@example.com"
# os.environ["EMAIL_SMTP_PASSWORD"] = "password"
# os.environ["EMAIL_TO_EMAILS"] = "user1@example.com"
# # bark
# os.environ["BARK_DEVICE_KEY"] = "device_key1,device_key2"
# os.environ["BARK_GROUP"] = "crypto_flash1,crypto_flash2"
# os.environ["BARK_SOURCES"] = "['source1','source2'],['source1']"
def main():
    """
    主函数
    """
    logger.info("启动CryptoFlash应用...")
    
    try:
        # 初始化服务
        service = CryptoFlashService()
        
        print(service.config)
    except KeyboardInterrupt:
        logger.info("用户中断程序")
        return 0
    except Exception as e:
        logger.error(f"程序运行异常: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
