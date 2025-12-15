from typing import List, Dict
from core.base import SpiderBase, NotifierBase
from adapters.spiders import BinanceSpider, ForesightNewsSpider
from adapters.notifiers import DingTalkNotifier, EmailNotifier
from utils.logger import logger
from utils.database import db_manager
from utils.config import config_loader
from concurrent.futures import ThreadPoolExecutor
import requests
class CryptoFlashService:
    """
    CryptoFlash核心服务类
    负责协调爬虫适配器和通知适配器，实现数据的爬取、处理和推送
    """
    
    def __init__(self):
        """
        初始化核心服务
        """
        self.spiders = []  # 爬虫适配器列表
        self.notifiers = []  # 通知适配器列表
        self.data = []  # 爬取到的数据
        self.config=config_loader.get_config()
        logger.debug(f"{self.config}")
        logger.info(f"最大线程数：{self.config.get('pool', {}).get('max_workers', 5)}")
        self.init_spiders()
        self.init_notifiers()
        
        
    def init_spiders(self):
        """
        初始化所有爬虫适配器
        """
        logger.info("初始化爬虫适配器...")
        try:
            # 添加所有爬虫适配器
            for spider_cls in SpiderBase.__subclasses__():
                self.spiders.append(spider_cls())
            logger.info(f"成功初始化 {len(self.spiders)} 个爬虫适配器")
        except Exception as e:
            logger.exception(f"初始化爬虫适配器失败: {e}")
            raise
    
    def init_notifiers(self):
        """
        初始化所有通知适配器
        """
        logger.info("初始化通知适配器...")
        try:
            # 添加所有通知适配器
            for notifier_cls in NotifierBase.__subclasses__():
                try:
                    self.notifiers.append(notifier_cls())
                except Exception as e:
                    logger.exception(f"初始化通知适配器 {notifier_cls.__name__} 失败: {e}")
            logger.info(f"成功初始化 {len(self.notifiers)} 个通知适配器")
        except Exception as e:
            logger.exception(f"初始化通知适配器失败: {e}")
            raise
    
    def fetch_data(self) -> List[Dict]:
        """
        统一调度所有爬虫进行数据爬取
        
        :return: 所有爬取到的数据列表
        """
        logger.info("开始爬取数据...")
        self.data = []
        with ThreadPoolExecutor(max_workers=int(self.config.get('pool', {}).get('max_workers', 5))) as executor:
            for spider in self.spiders:
                future = executor.submit(spider.fetch_data)
                try:
                    self.data.extend(future.result())
                except Exception as e:
                    logger.exception(f"爬虫 {spider.__class__.__name__} 爬取失败: {e}")
                    continue
        
        logger.info(f"数据爬取完成，共获取 {len(self.data)} 条数据")
        return self.data
    
    def process_data(self, data: List[Dict] = None) -> List[Dict]:
        """
        处理爬取到的数据，使用sqlite数据库进行去重
        
        :param data: 待处理的数据，如果不提供则使用self.data
        :return: 处理后的数据列表（仅包含增量数据）
        """
        if data is None:
            data = self.data
        
        if not data:
            logger.info("没有数据需要处理")
            return []
        
        logger.info(f"开始处理 {len(data)} 条数据...")
        
        try:
            # 使用sqlite数据库进行去重
            processed_data = []
            new_titles = []
            
            for item in data:
                title = item.get("title", "")
                if title:
                    # 检查标题是否已存在于数据库中
                    if not db_manager.exists(title):
                        processed_data.append(item)
                        new_titles.append(title)
                else:
                    logger.warning(f"数据项缺少标题字段: {item}")
            
            # 将新标题的md5值保存到数据库中
            if new_titles:
                db_manager.insert_batch(new_titles)
                logger.info(f"成功将 {len(new_titles)} 个新标题的md5值保存到数据库")
            
            logger.info(f"数据处理完成，处理后剩余 {len(processed_data)} 条新数据")
            return processed_data
        except Exception as e:
            logger.exception(f"数据处理失败: {e}")
            return []
    
    def send_notification(self, data: List[Dict] = None, markdown_content: str = None) -> bool:
        """
        统一调度所有通知适配器进行数据推送
        
        :param data: 待推送的数据，如果不提供则使用self.data
        :param markdown_content: 预生成的markdown格式通知内容
        :return: 所有通知发送成功返回True，否则返回False
        """
        if data is None:
            data = self.data
        
        if not data:
            logger.info("没有数据需要推送")
            return True
        
        logger.info(f"开始推送 {len(data)} 条数据...")
        
        all_success = True
        for notifier in self.notifiers:
            try:
                # 调用通知器的send_notification方法，传递预生成的markdown内容
                success = notifier.send_notification(data, markdown_content)
                if not success:
                    all_success = False
                    logger.exception(f"通知器 {notifier.__class__.__name__} 发送失败")
                else:
                    logger.info(f"通知器 {notifier.__class__.__name__} 发送成功")
            except Exception as e:
                all_success = False
                logger.exception(f"通知器 {notifier.__class__.__name__} 发送异常: {e}")
                continue
        
        return all_success
    
    def generate_notification_content(self, data: List[Dict]) -> str:
        """
        生成markdown格式的通知内容，按照source分类，为有url的条目生成超链接
        
        :param data: 待处理的数据
        :return: markdown格式的通知内容
        """
        if not data:
            return ""
        
        # 按source分类数据
        data_by_source = {}
        for item in data:
            source = item.get("source", "未知来源")
            if source not in data_by_source:
                data_by_source[source] = []
            data_by_source[source].append(item)
        
        # 生成markdown内容
        markdown_content = "# CryptoFlash 最新资讯\n\n"
        
        for source, items in data_by_source.items():
            markdown_content += f"### {source}\n\n"
            
            for index,item in enumerate(items):
                title = item.get("title", "无标题")
                url = item.get("url", "")
                publish_time = item.get("publish_time") or item.get("pub_time", "未知时间")
                
                # 生成带超链接的标题
                if url:
                    markdown_content += f"{index+1}. [{title}]({url})\n"
                else:
                    markdown_content += f"{index+1}. {title}\n"

            markdown_content += "------ \n"
        
        return markdown_content
    
    def run(self) -> bool:
        """
        执行完整的流程：爬取数据 -> 处理数据 -> 生成通知内容 -> 推送通知
        
        :return: 整个流程执行成功返回True，否则返回False
        """
        logger.info("开始执行CryptoFlash服务...")
        
        try:
            # 1. 爬取数据
            self.fetch_data()
            
            # 2. 处理数据
            processed_data = self.process_data()
            
            # 3.生成通知内容
            if processed_data:
                notification_content = self.generate_notification_content(processed_data)
                logger.info(f"成功生成通知内容: {notification_content[:100]}...")  # 只记录前100个字符
            else:
                notification_content = ""
                logger.info("没有数据需要生成通知内容")
            
            # 4. 推送通知
            if processed_data:
                # 将生成的markdown内容作为额外参数传递给通知适配器
                success = self.send_notification(processed_data, notification_content)
            else:
                logger.info("没有数据需要推送")
                success = True
            
            logger.info("CryptoFlash服务执行完成")
            return success
        except Exception as e:
            logger.exception(f"CryptoFlash服务执行失败: {e}")
            return False
