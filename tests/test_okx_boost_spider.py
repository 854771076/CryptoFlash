import os
import sys

# 将项目根目录添加到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from adapters.spiders.okx_boost import OkxBoostSpider
from utils.config import config_loader
if __name__ == "__main__":
    configs=config_loader.get_config("spiders")
    for i in configs:
        if i.get("type") == "okx_boost":
            config=i
    spider = OkxBoostSpider(config)
    data = spider.base_chain()
    print(data)