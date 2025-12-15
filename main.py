#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CryptoFlash程序入口
"""

from core.service import CryptoFlashService
from utils.logger import logger

def main():
    """
    主函数
    """
    logger.info("启动CryptoFlash应用...")
    
    try:
        # 初始化服务
        service = CryptoFlashService()
        
        # 运行服务
        success = service.run()
        
        if success:
            logger.info("CryptoFlash应用运行成功")
            return 0
        else:
            logger.error("CryptoFlash应用运行失败")
            return 1
    except KeyboardInterrupt:
        logger.info("用户中断程序")
        return 0
    except Exception as e:
        logger.error(f"程序运行异常: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
