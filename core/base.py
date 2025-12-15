from abc import ABC, abstractmethod
from typing import List, Dict
import time
# 爬虫抽象基类
class SpiderBase(ABC):
    """
    所有爬虫适配器的基类，定义统一的爬取接口
    """
    
    @abstractmethod
    def fetch_data(self) -> List[Dict]:
        """
        爬取数据的核心方法
        
        返回格式：[
            {
                "title": 资讯标题,
                "content": 资讯内容,
                "url": 资讯链接,
                "source": 数据源（如binance/foresightnews）,
                "publish_time": 发布时间（字符串，如2025-12-15 10:00:00）
            }
        ]
        
        :return: 爬取到的资讯数据列表
        """
        pass

# 通知抽象基类
class NotifierBase(ABC):
    """
    所有通知适配器的基类，定义统一的发送接口
    """
    
    @abstractmethod
    def send_notification(self, data: List[Dict], markdown_content: str = None) -> bool:
        """
        发送通知的核心方法
        
        :param data: 待推送的资讯数据（同fetch_data的返回格式）
        :param markdown_content: 预生成的markdown格式通知内容
        :return: 发送成功返回True，失败返回False
        """
        pass
