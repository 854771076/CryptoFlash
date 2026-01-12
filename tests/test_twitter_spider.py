import sys
import os
from typing import Dict

# 添加项目根目录到 sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from adapters.spiders.twitter_spider import TwitterSpider
from curl_cffi import requests

def test_twitter_spider():
    # 测试配置
    config = {
        "username": "Wuming_Mr_",
        "nitter_instance": "http://xxx/"
    }
    
    print(f"正在测试 TwitterSpider, 用户名: {config['username']}...")
    spider = TwitterSpider(config)
    print(spider.fetch_data())

if __name__ == "__main__":
    test_twitter_spider()
