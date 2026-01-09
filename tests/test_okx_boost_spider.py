import os
import sys

# 将项目根目录添加到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from adapters.spiders.okx_boost import OkxBoostSpider

if __name__ == "__main__":
    spider = OkxBoostSpider()
    data = spider.fetch_data()
    print(data)