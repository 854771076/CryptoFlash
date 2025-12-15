import unittest
from unittest.mock import Mock, patch
from core.service import CryptoFlashService

class TestCryptoFlashService(unittest.TestCase):
    """
    核心服务层的单元测试
    """
    
    def setUp(self):
        """
        测试前的准备工作
        """
        # 创建模拟的爬虫和通知器
        self.mock_spider1 = Mock()
        self.mock_spider2 = Mock()
        self.mock_notifier1 = Mock()
        self.mock_notifier2 = Mock()
        
        # 配置模拟返回值
        self.test_data1 = [
            {"title": "测试公告1", "url": "https://test.com/1", "publish_time": "2023-01-01", "content": "测试内容1"}
        ]
        self.test_data2 = [
            {"title": "测试公告2", "url": "https://test.com/2", "publish_time": "2023-01-02", "content": "测试内容2"}
        ]
        
        self.mock_spider1.fetch_data.return_value = self.test_data1
        self.mock_spider2.fetch_data.return_value = self.test_data2
        
        # 创建服务实例
        self.service = CryptoFlashService(
            spiders=[self.mock_spider1, self.mock_spider2],
            notifiers=[self.mock_notifier1, self.mock_notifier2]
        )
    
    def test_fetch_data(self):
        """
        测试数据爬取功能
        """
        # 调用fetch_data方法
        result = self.service.fetch_data()
        
        # 验证爬虫的fetch_data方法被调用
        self.mock_spider1.fetch_data.assert_called_once()
        self.mock_spider2.fetch_data.assert_called_once()
        
        # 验证结果包含两个爬虫的数据
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], self.test_data1)
        self.assertEqual(result[1], self.test_data2)
    
    def test_process_data(self):
        """
        测试数据处理功能（去重）
        """
        # 创建包含重复数据的测试数据
        test_data = [
            [
                {"title": "重复公告", "url": "https://test.com/duplicate", "publish_time": "2023-01-01", "content": "重复内容"},
                {"title": "公告1", "url": "https://test.com/1", "publish_time": "2023-01-01", "content": "内容1"}
            ],
            [
                {"title": "重复公告", "url": "https://test.com/duplicate", "publish_time": "2023-01-01", "content": "重复内容"},
                {"title": "公告2", "url": "https://test.com/2", "publish_time": "2023-01-02", "content": "内容2"}
            ]
        ]
        
        # 调用process_data方法
        result = self.service.process_data(test_data)
        
        # 验证结果去重后只有3条数据
        self.assertEqual(len(result), 3)
        
        # 验证重复数据被去重
        titles = [item["title"] for item in result]
        self.assertEqual(titles.count("重复公告"), 1)
    
    @patch('core.service.datetime')
    def test_send_notification(self, mock_datetime):
        """
        测试发送通知功能
        """
        # 配置模拟时间
        mock_datetime.now.return_value.strftime.return_value = "2023-01-01 12:00:00"
        
        # 创建测试数据
        test_data = [
            {"title": "测试公告", "url": "https://test.com/1", "publish_time": "2023-01-01", "content": "测试内容"}
        ]
        
        # 调用send_notification方法
        self.service.send_notification(test_data)
        
        # 验证每个通知器的send_notification方法被调用
        self.mock_notifier1.send_notification.assert_called_once_with(test_data)
        self.mock_notifier2.send_notification.assert_called_once_with(test_data)

if __name__ == "__main__":
    unittest.main()
