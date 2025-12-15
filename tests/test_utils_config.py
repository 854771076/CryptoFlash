import unittest
import os
import yaml
from utils.config import ConfigLoader

class TestConfigLoader(unittest.TestCase):
    """
    配置加载工具类的单元测试
    """
    
    def setUp(self):
        """
        测试前的准备工作
        """
        # 创建临时配置文件
        self.temp_config_path = "temp_test_config.yml"
        self.test_config = {
            "spiders": {
                "binance": {
                    "url": "https://test.binance.com"
                }
            },
            "notifiers": {
                "dingtalk": {
                    "webhook": "https://oapi.dingtalk.com/robot/send?access_token=test"
                }
            }
        }
        
        # 写入临时配置文件
        with open(self.temp_config_path, 'w', encoding='utf-8') as f:
            yaml.dump(self.test_config, f)
    
    def tearDown(self):
        """
        测试后的清理工作
        """
        # 删除临时配置文件
        if os.path.exists(self.temp_config_path):
            os.remove(self.temp_config_path)
    
    def test_load_config(self):
        """
        测试加载配置文件
        """
        config_loader = ConfigLoader(self.temp_config_path)
        config = config_loader.load_config()
        
        self.assertEqual(config, self.test_config)
    
    def test_get_config(self):
        """
        测试获取配置项
        """
        config_loader = ConfigLoader(self.temp_config_path)
        
        # 获取整个配置
        full_config = config_loader.get_config()
        self.assertEqual(full_config, self.test_config)
        
        # 获取配置节
        spiders_config = config_loader.get_config("spiders")
        self.assertEqual(spiders_config, self.test_config["spiders"])
        
        # 获取配置项
        binance_url = config_loader.get_config("spiders", "binance")
        self.assertEqual(binance_url, self.test_config["spiders"]["binance"])

if __name__ == "__main__":
    unittest.main()
