import unittest
from unittest.mock import Mock, patch
from adapters.notifiers.dingtalk_notifier import DingTalkNotifier
from adapters.notifiers.email_notifier import EmailNotifier
from adapters.notifiers.bark_notifier import BarkNotifier

class TestDingTalkNotifier(unittest.TestCase):
    """
    钉钉通知适配器的单元测试
    """
    
    def setUp(self):
        """
        测试前的准备工作
        """
        self.test_config = {
            "webhook": "https://oapi.dingtalk.com/robot/send?access_token=test",
            "secret": "test_secret"
        }
        
    @patch('requests.post')
    @patch('adapters.notifiers.dingtalk_notifier.datetime')
    @patch('adapters.notifiers.dingtalk_notifier.hmac')
    @patch('adapters.notifiers.dingtalk_notifier.base64')
    def test_send_notification(self, mock_base64, mock_hmac, mock_datetime, mock_post):
        """
        测试发送通知功能
        """
        # 配置模拟
        mock_datetime.now.return_value.timestamp.return_value = 1234567890
        mock_hmac.new.return_value.hexdigest.return_value = "test_signature"
        mock_base64.b64encode.return_value.decode.return_value = "test_encoded_signature"
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"errcode": 0, "errmsg": "ok"}
        mock_post.return_value = mock_response
        
        # 创建通知器实例
        notifier = DingTalkNotifier(self.test_config)
        
        # 测试数据
        test_data = [
            {"title": "Test Announcement", "url": "https://test.com/1", "publish_time": "2023-01-01", "content": "Test content"}
        ]
        
        # 调用send_notification方法
        result = notifier.send_notification(test_data)
        
        # 验证结果
        self.assertTrue(result)
        mock_post.assert_called_once()

class TestEmailNotifier(unittest.TestCase):
    """
    邮件通知适配器的单元测试
    """
    
    def setUp(self):
        """
        测试前的准备工作
        """
        self.test_config = {
            "smtp_server": "smtp.test.com",
            "smtp_port": 587,
            "username": "test@test.com",
            "password": "test_password",
            "recipients": ["recipient1@test.com", "recipient2@test.com"]
        }
        
    @patch('smtplib.SMTP')
    def test_send_notification(self, mock_smtp_class):
        """
        测试发送通知功能
        """
        # 配置模拟
        mock_smtp = Mock()
        mock_smtp_class.return_value.__enter__.return_value = mock_smtp
        
        # 创建通知器实例
        notifier = EmailNotifier(self.test_config)
        
        # 测试数据
        test_data = [
            {"title": "Test Announcement", "url": "https://test.com/1", "publish_time": "2023-01-01", "content": "Test content"}
        ]
        
        # 调用send_notification方法
        result = notifier.send_notification(test_data)
        
        # 验证结果
        self.assertTrue(result)
        mock_smtp_class.assert_called_once_with(self.test_config["smtp_server"], self.test_config["smtp_port"])
        mock_smtp.login.assert_called_once_with(self.test_config["username"], self.test_config["password"])
        mock_smtp.send_message.assert_called_once()

class TestBarkNotifier(unittest.TestCase):
    """
    Bark通知适配器的单元测试
    """
    
    def setUp(self):
        """
        测试前的准备工作
        """
        self.test_config = {
            "api_url": "https://api.day.app",
            "device_key": "test_device_key",
            "group": "crypto_flash"
        }
        
    @patch('requests.post')
    @patch('utils.config.config_loader.get_config')
    def test_send_notification(self, mock_get_config, mock_post):
        """
        测试发送通知功能
        """
        # 配置模拟
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"ok": True}
        mock_post.return_value = mock_response
        
        # 模拟配置加载
        mock_get_config.return_value = self.test_config
        
        # 创建通知器实例
        notifier = BarkNotifier()
        
        # 测试数据
        test_data = [
            {"title": "Test Announcement", "url": "https://test.com/1", "publish_time": "2023-01-01", "content": "Test content"}
        ]
        
        # 调用send_notification方法
        result = notifier.send_notification(test_data)
        
        # 验证结果
        self.assertTrue(result)
        mock_post.assert_called_once()

    @patch('requests.post')
    @patch('utils.config.config_loader.get_config')
    def test_send_notification_large_content(self, mock_get_config, mock_post):
        """
        测试发送超过限制大小的通知内容（分页发送）
        """
        # 配置模拟
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"ok": True}
        mock_post.return_value = mock_response
        
        # 模拟配置加载
        mock_get_config.return_value = self.test_config
        
        # 创建通知器实例
        notifier = BarkNotifier()
        
        # 测试数据
        test_data = [
            {"title": "Test Announcement", "url": "https://test.com/1", "publish_time": "2023-01-01", "content": "Test content"}
        ]
        
        # 创建一个超过2000字节的markdown内容
        large_content = "# 测试标题\n\n" + "这是一行测试内容，用于模拟超过2000字节的情况。\n" * 100
        
        # 调用send_notification方法，传入large_content
        result = notifier.send_notification(test_data, large_content)
        
        # 验证结果
        self.assertTrue(result)
        
        # 验证是否调用了多次post请求（至少2次）
        self.assertGreater(mock_post.call_count, 1)
        
        # 验证每次调用的参数是否正确，特别是标题中的页数信息
        total_calls = mock_post.call_count
        for call_index, call_args in enumerate(mock_post.call_args_list):
            # 获取位置参数和关键字参数
            call_args_tuple = call_args[0]
            call_kwargs = call_args.kwargs
            
            # url可能在位置参数或关键字参数中
            url = call_args_tuple[0] if call_args_tuple else call_kwargs.get('url')
            json_params = call_kwargs.get('json', {})
            
            self.assertEqual(url, f"{self.test_config['api_url']}/push")
            self.assertIn('device_key', json_params)
            self.assertIn('title', json_params)
            self.assertIn('markdown', json_params)
            
            # 验证标题中的页数信息
            title = json_params['title']
            expected_title = f"加密货币资讯 (1 条) - 第{call_index + 1}/{total_calls}页"
            self.assertEqual(title, expected_title)

if __name__ == "__main__":
    unittest.main()
