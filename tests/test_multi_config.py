import unittest
from unittest.mock import MagicMock, patch
from core.service import CryptoFlashService
from core.base import SpiderBase, NotifierBase

class MockSpider(SpiderBase):
    name = 'mock_spider'
    def fetch_data(self):
        return [{
            "title": f"Test Title from {self.config.get('id')}",
            "source": self.config.get('id'),
            "publish_time": "2025-01-01 10:00:00",
            "url": "http://example.com"
        }]

class MockNotifier(NotifierBase):
    name = 'mock_notifier'
    def __init__(self, config=None):
        super().__init__(config)
        self.sent_data = []

    def send_notification(self, data, markdown_content=None):
        self.sent_data.extend(data)
        return True

class TestMultiConfig(unittest.TestCase):
    def setUp(self):
        # Register mock classes
        # This is a bit hacky as we are modifying the subclasses of the base classes
        # In a real scenario we might want to use a registry or mock the __subclasses__ method
        pass

    @patch('core.service.SpiderBase.__subclasses__')
    @patch('core.service.NotifierBase.__subclasses__')
    @patch('core.service.config_loader')
    @patch('core.service.db_manager')
    def test_multi_config_and_filtering(self, mock_db, mock_config_loader, mock_notifier_subclasses, mock_spider_subclasses):
        # Setup mocks
        mock_spider_subclasses.return_value = [MockSpider]
        mock_notifier_subclasses.return_value = [MockNotifier]
        
        # Mock config
        mock_config = {
            "spiders": [
                {"type": "mock_spider", "id": "source1"},
                {"type": "mock_spider", "id": "source2"}
            ],
            "notifiers": [
                {"type": "mock_notifier", "id": "notifier1", "sources": ["source1"]},
                {"type": "mock_notifier", "id": "notifier2", "sources": []} # All sources
            ],
            "pool": {"max_workers": 1}
        }
        
        service = CryptoFlashService()
        service.config = mock_config
        # Re-init to use the mocked config
        service.spiders = []
        service.notifiers = []
        service.init_spiders()
        service.init_notifiers()
        
        # Test fetch_data
        data = service.fetch_data()
        self.assertEqual(len(data), 2)
        sources = set(d['source'] for d in data)
        self.assertEqual(sources, {'source1', 'source2'})
        
        # Test send_notification
        service.send_notification(data)
        
        notifier1 = service.notifiers[0]
        notifier2 = service.notifiers[1]
        
        # Verify notifier1 only got source1
        self.assertEqual(len(notifier1.sent_data), 1)
        self.assertEqual(notifier1.sent_data[0]['source'], 'source1')
        
        # Verify notifier2 got all
        self.assertEqual(len(notifier2.sent_data), 2)

if __name__ == '__main__':
    unittest.main()
