# 爬虫适配器初始化文件
from .binance_spider import BinanceSpider
from .foresight_news_spider import ForesightNewsSpider
from .okx_boost import OkxBoostSpider
from .twitter_spider import TwitterSpider

__all__ = ['BinanceSpider', 'ForesightNewsSpider','OkxBoostSpider','TwitterSpider']
