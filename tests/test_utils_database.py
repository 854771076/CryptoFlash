#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库工具类单元测试
"""

import unittest
import os
from utils.database import DatabaseManager

class TestDatabaseManager(unittest.TestCase):
    """DatabaseManager类的单元测试"""
    
    def setUp(self):
        """设置测试环境，创建临时数据库"""
        self.temp_db_path = "test_crypto_flash.db"
        # 确保临时数据库不存在
        if os.path.exists(self.temp_db_path):
            os.remove(self.temp_db_path)
        # 创建数据库管理器实例
        self.db_manager = DatabaseManager(db_path=self.temp_db_path)
    
    def tearDown(self):
        """清理测试环境，删除临时数据库"""
        if hasattr(self, 'db_manager'):
            # 关闭数据库连接
            self.db_manager.close()
        # 删除临时数据库文件
        if os.path.exists(self.temp_db_path):
            os.remove(self.temp_db_path)
    
    def test_calculate_md5(self):
        """测试计算标题的md5值"""
        title = "测试标题"
        md5_value = self.db_manager._get_md5(title)
        # 验证md5值的格式
        self.assertEqual(len(md5_value), 32)
        # 验证相同标题的md5值相同
        self.assertEqual(md5_value, self.db_manager._get_md5(title))
        # 验证不同标题的md5值不同
        self.assertNotEqual(md5_value, self.db_manager._get_md5("不同的测试标题"))
    
    def test_title_exists(self):
        """测试检查标题是否存在"""
        title = "测试标题"
        # 初始状态下标题不存在
        self.assertFalse(self.db_manager.exists(title))
        # 插入标题后标题应该存在
        self.db_manager.insert_batch([title])
        self.assertTrue(self.db_manager.exists(title))
    
    def test_insert_title(self):
        """测试插入单个标题"""
        title = "测试标题"
        # 插入标题
        self.db_manager.insert_batch([title])
        # 验证标题存在
        self.assertTrue(self.db_manager.exists(title))
    
    def test_insert_titles(self):
        """测试批量插入标题"""
        titles = ["测试标题1", "测试标题2", "测试标题3"]
        # 批量插入标题
        self.db_manager.insert_batch(titles)
        # 验证所有标题都存在
        for title in titles:
            self.assertTrue(self.db_manager.exists(title))
    
    def test_get_all_hashes(self):
        """测试获取所有哈希值"""
        titles = ["测试标题1", "测试标题2", "测试标题3"]
        # 批量插入标题
        self.db_manager.insert_batch(titles)
        # 获取所有哈希值
        hashes = self.db_manager.get_all_hashes()
        # 验证哈希值的数量正确
        self.assertEqual(len(hashes), len(titles))
        # 验证每个标题的哈希值都在返回结果中
        for title in titles:
            expected_hash = self.db_manager._get_md5(title)
            self.assertIn(expected_hash, hashes)

if __name__ == '__main__':
    unittest.main()
