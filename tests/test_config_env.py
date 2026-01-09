import os
import unittest
from utils.config import ConfigLoader

class TestConfigEnvMerge(unittest.TestCase):
    def test_merge_into_list(self):
        # Mock environment variables
        os.environ["DINGTALK_WEBHOOK"] = "http://test-webhook1,http://test-webhook2"
        os.environ["DINGTALK_SOURCES"] = "['source1','source2'],['source1']"
        os.environ["BINANCE_URL"] = "http://test-binance"
        
        # Initial config with list structure
        initial_config = {
            "notifiers": [
                {"type": "dingtalk", "webhook": "old-webhook"}
            ],
            "spiders": [
                {"type": "binance", "url": "old-url"}
            ]
        }
        
        loader = ConfigLoader()
        loader.config = initial_config
        
        # Trigger merge (get_config with no args merges env vars)
        merged_config = loader.get_config()
        
        # Check notifiers
        notifiers = merged_config.get("notifiers", [])
        dingtalk_notifiers = [n for n in notifiers if n.get("type") == "dingtalk"]
        self.assertEqual(len(dingtalk_notifiers), 2)
        
        # Instance 1
        self.assertEqual(dingtalk_notifiers[0].get("webhook"), "http://test-webhook1")
        self.assertEqual(dingtalk_notifiers[0].get("sources"), ["source1", "source2"])
        
        # Instance 2
        self.assertEqual(dingtalk_notifiers[1].get("webhook"), "http://test-webhook2")
        self.assertEqual(dingtalk_notifiers[1].get("sources"), ["source1"])
        
        # Check spiders
        spiders = merged_config.get("spiders", [])
        binance = next((s for s in spiders if s.get("type") == "binance"), None)
        self.assertIsNotNone(binance)
        self.assertEqual(binance.get("url"), "http://test-binance")

    def test_merge_new_item(self):
        # Mock environment variables for a non-existent notifier in YAML
        os.environ["BARK_DEVICE_KEY"] = "test-device-key"
        
        initial_config = {
            "notifiers": []
        }
        
        loader = ConfigLoader()
        loader.config = initial_config
        
        merged_config = loader.get_config()
        
        notifiers = merged_config.get("notifiers", [])
        bark = next((n for n in notifiers if n.get("type") == "bark"), None)
        self.assertIsNotNone(bark)
        self.assertEqual(bark.get("device_key"), "test-device-key")

if __name__ == '__main__':
    unittest.main()
