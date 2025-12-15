import logging
import os
from logging.handlers import RotatingFileHandler
from utils.config import config_loader
class Logger:
    """
    日志工具类
    """
    
    def __init__(self, name: str = "CryptoFlash", level: int = logging.INFO):
        """
        初始化日志记录器
        
        :param name: 日志名称
        :param level: 日志级别
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        # 创建日志目录
        log_dir = os.path.join(os.path.dirname(__file__), "..", "logs")
        os.makedirs(log_dir, exist_ok=True)
        
        # 配置日志格式
        formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            

        )
        
        # 控制台处理器 - 设置UTF-8编码
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        # 在Windows上强制控制台输出使用UTF-8
        import sys
        if sys.platform == "win32":
            console_handler.stream = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
        
        # 文件处理器（按大小分割，保留5个备份）
        file_handler = RotatingFileHandler(
            filename=os.path.join(log_dir, "crypto_flash.log"),
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'  # 设置文件编码为UTF-8
        )
        file_handler.setFormatter(formatter)
        
        # 添加处理器
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
    
    def get_logger(self) -> logging.Logger:
        """
        获取日志记录器实例
        
        :return: 日志记录器
        """
        return self.logger

# 全局日志实例
logger_config = config_loader.get_config().get('logger', {})
logger_level = logger_config.get('level', logging.INFO)
logger = Logger(level=logger_level).get_logger()
