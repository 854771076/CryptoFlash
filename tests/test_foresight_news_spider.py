import os
import sys

# 将项目根目录添加到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from adapters.spiders.foresight_news_spider import ForesightNewsSpider

if __name__ == "__main__":
    spider = ForesightNewsSpider()
    data = spider.fetch_data()
    print(data)