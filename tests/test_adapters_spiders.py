import unittest
from unittest.mock import Mock, patch
from adapters.spiders.binance_spider import BinanceSpider
from adapters.spiders.foresight_news_spider import ForesightNewsSpider

class TestBinanceSpider(unittest.TestCase):
    """
    币安爬虫适配器的单元测试
    """
    
    @patch('requests.get')
    def test_fetch_data(self, mock_get):
        """
        测试爬取数据功能
        """
        # 配置模拟响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '''
        <div class="article-list">
            <div class="article-item">
                <a class="title" href="https://www.binance.com/en/support/announcement/test1">Test Announcement 1</a>
                <div class="publish-time">2023-01-01</div>
                <div class="content">This is a test announcement 1.</div>
            </div>
            <div class="article-item">
                <a class="title" href="https://www.binance.com/en/support/announcement/test2">Test Announcement 2</a>
                <div class="publish-time">2023-01-02</div>
                <div class="content">This is a test announcement 2.</div>
            </div>
        </div>
        '''
        mock_get.return_value = mock_response
        
        # 创建爬虫实例
        spider = BinanceSpider()
        
        # 调用fetch_data方法
        result = spider.fetch_data()
        
        # 验证请求被正确发送
        mock_get.assert_called_once()
        
        # 验证结果格式正确
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["title"], "Test Announcement 1")
        self.assertEqual(result[0]["url"], "https://www.binance.com/en/support/announcement/test1")
        self.assertEqual(result[0]["publish_time"], "2023-01-01")
        self.assertEqual(result[0]["content"], "This is a test announcement 1.")

class TestForesightNewsSpider(unittest.TestCase):
    """
    ForesightNews爬虫适配器的单元测试
    """
    
    @patch('requests.get')
    def test_fetch_data(self, mock_get):
        """
        测试爬取数据功能
        """
        # 配置模拟响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '''
        <div class="article-list">
            <div class="article-item">
                <h2 class="article-title">
                    <a href="https://foresightnews.pro/news/test1">Test News 1</a>
                </h2>
                <div class="article-meta">
                    <span class="article-time">2023-01-01</span>
                </div>
                <div class="article-content">This is a test news 1.</div>
            </div>
            <div class="article-item">
                <h2 class="article-title">
                    <a href="https://foresightnews.pro/news/test2">Test News 2</a>
                </h2>
                <div class="article-meta">
                    <span class="article-time">2023-01-02</span>
                </div>
                <div class="article-content">This is a test news 2.</div>
            </div>
        </div>
        '''
        mock_get.return_value = mock_response
        
        # 创建爬虫实例
        spider = ForesightNewsSpider()
        
        # 调用fetch_data方法
        result = spider.fetch_data()
        
        # 验证请求被正确发送
        mock_get.assert_called_once()
        
        # 验证结果格式正确
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["title"], "Test News 1")
        self.assertEqual(result[0]["url"], "https://foresightnews.pro/news/test1")
        self.assertEqual(result[0]["publish_time"], "2023-01-01")
        self.assertEqual(result[0]["content"], "This is a test news 1.")

if __name__ == "__main__":
    unittest.main()
