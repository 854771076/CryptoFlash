from typing import List, Dict
from core.base import SpiderBase,time
from utils.logger import logger
from utils.config import config_loader
from fake_useragent import UserAgent
from curl_cffi import requests
from concurrent.futures import ThreadPoolExecutor
class BinanceSpider(SpiderBase):
    """
    币安公告爬虫适配器
    """
    name='binance'
    def __init__(self):
        """
        初始化币安爬虫
        """
        self.url = config_loader.get_config("spiders", "binance").get("url")
        self.source = "binance"
        self.user_agent = UserAgent()
        self.default_headers={
            'bnc-location':'CN',
            'bnc-time-zone':'Asia/Shanghai','referer':'https://www.binance.com/zh-CN/support/announcement',
            'User-Agent': self.user_agent.random,
            'lang': 'zh-CN'
        }
        self.default_cookies={
            'lang': 'zh-CN',
            'BNC-Location': 'CN'
        }
    # 交易对公告
    def token_pair_announcement_list(self) -> List[Dict]:
        """
        获取币安交易对公告列表
        
        :return: 交易对公告列表
        """
        url='https://www.binance.com/bapi/apex/v1/public/apex/cms/article/list/query?type=1&pageNo=1&pageSize=10&catalogId=48'
        response = requests.get(url, headers=self.default_headers,cookies=self.default_cookies,impersonate='chrome')
        response.raise_for_status()  # 检查请求是否成功
        data = response.json()
        articles=data.get('data', {} ).get('catalogs', [{}])[0].get('articles', [])
        # 提取公告信息
        result = []
        for article in articles:
            result.append({
                "title": article.get('title', ''),
                "url": 'https://www.binance.com/zh-CN/support/announcement/detail/'+article.get('code', ''),
                "publish_time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(article.get('releaseDate', 0)/1000)),
                'source':f'{self.source}交易对公告'
            })
        
        return result
    
    def activity_announcement_list(self) -> List[Dict]:
        """
        获取币安活动公告列表
        
        :return: 活动公告列表
        """
        url='https://www.binance.com/bapi/apex/v1/public/apex/cms/article/list/query?type=1&pageNo=1&pageSize=10&catalogId=93'
        response = requests.get(url, headers=self.default_headers,cookies=self.default_cookies,impersonate='chrome')
        response.raise_for_status()  # 检查请求是否成功
        data = response.json()
        articles=data.get('data', {} ).get('catalogs', [{}])[0].get('articles', [])
        # 提取公告信息
        result = []
        for article in articles:
            result.append({
                "title": article.get('title', ''),
                "url": 'https://www.binance.com/zh-CN/support/announcement/detail/'+article.get('code', ''),
                "publish_time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(article.get('releaseDate', 0)/1000)),
                'source':f'{self.source}活动公告'
            })
        
        return result

    def last_news_announcement_list(self) -> List[Dict]:
        """
        获取币安最新动态公告列表
        
        :return: 最新动态公告列表
        """
        url='https://www.binance.com/bapi/apex/v1/public/apex/cms/article/list/query?type=1&pageNo=1&pageSize=10&catalogId=49'
        response = requests.get(url, headers=self.default_headers,cookies=self.default_cookies,impersonate='chrome')
        response.raise_for_status()  # 检查请求是否成功
        data = response.json()
        articles=data.get('data', {} ).get('catalogs', [{}])[0].get('articles', [])
        # 提取公告信息
        result = []
        for article in articles:
            result.append({
                "title": article.get('title', ''),
                "url": 'https://www.binance.com/zh-CN/support/announcement/detail/'+article.get('code', ''),
                "publish_time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(article.get('releaseDate', 0)/1000)),
                'source':f'{self.source}最新动态公告'
            })
        
        return result

    def airdrops_announcement_list(self) -> List[Dict]:
        """
        获取币安空投公告列表
        
        :return: 空投公告列表
        """
        url='https://www.binance.com/bapi/apex/v1/public/apex/cms/article/list/query?type=1&pageNo=1&pageSize=10&catalogId=128'
        response = requests.get(url, headers=self.default_headers,cookies=self.default_cookies,impersonate='chrome')
        response.raise_for_status()  # 检查请求是否成功
        data = response.json()
        articles=data.get('data', {} ).get('catalogs', [{}])[0].get('articles', [])
        # 提取公告信息
        result = []
        for article in articles:
            result.append({
                "title": article.get('title', ''),
                "url": 'https://www.binance.com/zh-CN/support/announcement/detail/'+article.get('code', ''),
                "publish_time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(article.get('releaseDate', 0)/1000)),
                'source':f'{self.source}最新空投公告'
            })
        
        return result

    def fetch_data(self) -> List[Dict]:
        """
        爬取币安公告数据
        
        :return: 爬取到的公告数据列表
        """
        logger.info(f"开始爬取币安公告: {self.url}")
        with ThreadPoolExecutor(max_workers=4) as executor:
            token_pair_announcements = executor.submit(self.token_pair_announcement_list)
            activity_announcements = executor.submit(self.activity_announcement_list)
            last_news_announcements = executor.submit(self.last_news_announcement_list)
            airdrops_announcements = executor.submit(self.airdrops_announcement_list)
        
        # 合并所有结果
        all_announcements = (token_pair_announcements.result() + activity_announcements.result() + 
                             last_news_announcements.result() + airdrops_announcements.result())
        
        logger.info(f"成功爬取 {len(all_announcements)} 条币安公告")
        return all_announcements

