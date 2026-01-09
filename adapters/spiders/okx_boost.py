from typing import List, Dict
from core.base import SpiderBase,time
from utils.logger import logger
from utils.config import config_loader
from fake_useragent import UserAgent
from curl_cffi import requests
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
from datetime import datetime
class OkxBoostSpider(SpiderBase):
    """
    okx_boost爬虫适配器
    """
    name='okx_boost'
    def __init__(self):
        """
        初始化爬虫
        """
        self.url = config_loader.get_config("spiders", "okx_boost").get("url")
        self.source = "okx_boost"
        self.user_agent = UserAgent()
        self.default_headers={
            'User-Agent': self.user_agent.random,
        }
        self.default_cookies={
        }

    

    def fetch_data(self) -> List[Dict]:
        html=requests.get(self.url,headers=self.default_headers,cookies=self.default_cookies,impersonate='chrome').text
        soup=BeautifulSoup(html,'html.parser')
        # class="table-responsive"
        table=soup.find('table')
        rows=table.find_all('tr')
        result=[]
        for row in rows[1:]:
            cols=row.find_all('td')
            result.append({
                'name':f'okx_boost活动部署-{cols[1].text.strip()}',
                'url':f'https://bscscan.com/tx/{cols[1].text.strip()}',
                'publish_time':datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'source':self.source
            })
        return result  


