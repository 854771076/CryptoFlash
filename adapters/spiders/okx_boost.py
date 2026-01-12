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
    def __init__(self, config: Dict = None):
        """
        初始化爬虫
        """
        super().__init__(config)
        self.url = self.config.get("url")
        if not self.url:
            self.url = config_loader.get_config("spiders", "okx_boost").get("url")
        self.source = "okx_boost"
        self.user_agent = UserAgent()
        self.default_headers={
            'User-Agent': self.user_agent.random,
        }
        self.default_cookies={
        }

    def bnb_chain(self):
        html=requests.get(self.url,headers=self.default_headers,cookies=self.default_cookies,impersonate='chrome').text
        soup=BeautifulSoup(html,'html.parser')
        # class="table-responsive"
        table=soup.find('table')
        rows=table.find_all('tr')
        result=[]
        for row in rows[1:]:
            cols=row.find_all('td')
            result.append({
                'title':f'Okx_Boost活动部署(BNB)-{cols[1].text.strip()}',
                'url':f'https://bscscan.com/tx/{cols[1].text.strip()}',
                'publish_time':datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'source':self.source
            })
        return result
    def arb_chain(self):
        html=requests.get('https://arbiscan.io/address/0x000310fa98e36191ec79de241d72c6ca093eafd3',headers=self.default_headers,cookies=self.default_cookies,impersonate='chrome').text
        soup=BeautifulSoup(html,'html.parser')
        # class="table-responsive"
        table=soup.find('table')
        rows=table.find_all('tr')
        result=[]
        for row in rows[1:]:
            cols=row.find_all('td')
            result.append({
                'title':f'Okx_Boost活动部署(ARB)-{cols[1].text.strip()}',
                'url':f'https://https://arbiscan.io/tx/{cols[1].text.strip()}',
                'publish_time':datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'source':self.source
            })
        return result
    def base_chain(self):
        html=requests.get('https://basescan.org/address/0x000310fa98e36191ec79de241d72c6ca093eafd3',headers=self.default_headers,cookies=self.default_cookies,impersonate='chrome').text
        soup=BeautifulSoup(html,'html.parser')
        # class="table-responsive"
        table=soup.find('table')
        rows=table.find_all('tr')
        result=[]
        for row in rows[1:]:
            cols=row.find_all('td')
            result.append({
                'title':f'Okx_Boost活动部署(BASE)-{cols[1].text.strip()}',
                'url':f'https://basescan.org/tx/{cols[1].text.strip()}',
                'publish_time':datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'source':self.source
            })
        return result
    def fetch_data(self) -> List[Dict]:
          results=[]
          results.extend(self.bnb_chain())
          results.extend(self.arb_chain())
          results.extend(self.base_chain())
          return results

