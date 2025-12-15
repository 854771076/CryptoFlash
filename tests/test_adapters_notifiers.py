import unittest
from unittest.mock import Mock, patch
from adapters.notifiers.dingtalk_notifier import DingTalkNotifier
from adapters.notifiers.email_notifier import EmailNotifier

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

if __name__ == "__main__":
    unittest.main()
