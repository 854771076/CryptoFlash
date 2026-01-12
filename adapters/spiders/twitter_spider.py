from typing import List, Dict
import xml.etree.ElementTree as ET
import email.utils
from datetime import datetime
from core.base import SpiderBase
from utils.logger import logger
from curl_cffi import requests
import os ,re
class TwitterSpider(SpiderBase):
    """
    Twitter推文爬虫适配器 (通过 Nitter RSS)
    """
    name = 'twitter'

    def __init__(self, config: Dict = None):
        """
        初始化Twitter爬虫
        """
        super().__init__(config)
        self.username = self.config.get("username")
        self.nitter_instance = (self.config.get("nitter_instance") or os.environ['NITTER_INSTANCE']).rstrip('/')
        self.url = self.config.get("url")
        assert self.username or self.url, "必须提供用户名或URL"
        assert self.nitter_instance, "必须提供Nitter实例"
        # 如果没有直接提供URL，则根据用户名和实例构建RSS URL
        if not self.url and self.username:
            self.url = f"{self.nitter_instance}/{self.username}/rss"
            
        self.source = f"twitter_{self.username}" if self.username else "twitter"

    def fetch_data(self) -> List[Dict]:
        """
        爬取Twitter推文数据
        
        :return: 爬取到的推文数据列表
        """
        instances = [
            self.nitter_instance
        ]
        # 去重并保持顺序
        instances = list(dict.fromkeys([i.rstrip('/') for i in instances if i]))

        for instance in instances:
            url = self.url
            if self.username and instance not in url:
                url = f"{instance}/{self.username}/rss"
            
            try:
                response = requests.get(url, impersonate='chrome', timeout=20)
                response.raise_for_status()
                
                # 解析RSS XML
                root = ET.fromstring(response.content)
                items = root.findall('.//item')[:5]
                
                result = []
                for item in items:
                    title_elem = item.find('title')
                    link_elem = item.find('link')
                    pub_date_elem = item.find('pubDate')
                    
                    if title_elem is None or link_elem is None:
                        continue
                        
                    title = title_elem.text or ""
                    link = link_elem.text or ""
                    
                    # 将 Nitter 链接转换为 Twitter 链接
                    if instance in link:
                        link = link.replace(instance, "https://twitter.com")
                    
                    # 解析发布时间
                    publish_time = ""
                    if pub_date_elem is not None:
                        try:
                            pub_date_tuple = email.utils.parsedate_tz(pub_date_elem.text)
                            if pub_date_tuple:
                                dt = datetime.fromtimestamp(email.utils.mktime_tz(pub_date_tuple))
                                publish_time = dt.strftime('%Y-%m-%d %H:%M:%S')
                        except Exception as e:
                            logger.warning(f"解析推文时间失败: {e}")
                    
                    result.append({
                        'id':link,
                        "title": title.split('\n')[0],
                        "url": link,
                        "publish_time": publish_time,
                        "source": self.source
                    })
                
                logger.info(f"成功从 {instance} 爬取 {len(result)} 条推文")
                return result
            except Exception as e:
                logger.warning(f"从实例 {instance} 爬取失败: {e}")
                continue
        
        logger.error("所有Twitter实例均爬取失败")
        return []
