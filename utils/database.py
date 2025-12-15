import sqlite3
import hashlib
import os
from utils.logger import logger

class DatabaseManager:
    """
    SQLite数据库管理类，用于存储文章标题的MD5值以实现去重功能
    """
    
    def __init__(self, db_path='data/article_hashes.db'):
        """
        初始化数据库连接
        
        Args:
            db_path (str): 数据库文件路径，默认为'data/article_hashes.db'
        """
        self.db_path = db_path
        self._ensure_directory_exists()
        self._initialize_database()
    
    def _ensure_directory_exists(self):
        """
        确保数据库文件所在的目录存在
        """
        dir_path = os.path.dirname(self.db_path)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path)
            logger.info(f"创建数据库目录: {dir_path}")
    
    def _initialize_database(self):
        """
        初始化数据库，创建文章哈希表
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 创建文章哈希表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS article_hashes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title_hash TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info(f"数据库初始化成功: {self.db_path}")
        except sqlite3.Error as e:
            logger.error(f"数据库初始化失败: {e}")
            raise
    
    def _get_md5(self, title):
        """
        计算字符串的MD5哈希值
        
        Args:
            title (str): 文章标题
            
        Returns:
            str: MD5哈希值
        """
        return hashlib.md5(title.encode('utf-8')).hexdigest()
    
    def exists(self, title):
        """
        检查文章标题是否已存在（通过MD5哈希值）
        
        Args:
            title (str): 文章标题
            
        Returns:
            bool: 如果存在返回True，否则返回False
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            title_hash = self._get_md5(title)
            cursor.execute('SELECT id FROM article_hashes WHERE title_hash = ?', (title_hash,))
            result = cursor.fetchone()
            
            conn.close()
            return result is not None
        except sqlite3.Error as e:
            logger.error(f"检查标题存在性失败: {e}")
            return False
    
    def insert(self, title):
        """
        插入文章标题的MD5哈希值到数据库
        
        Args:
            title (str): 文章标题
            
        Returns:
            bool: 插入成功返回True，否则返回False
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            title_hash = self._get_md5(title)
            cursor.execute('INSERT OR IGNORE INTO article_hashes (title_hash) VALUES (?)', (title_hash,))
            affected_rows = cursor.rowcount
            
            conn.commit()
            conn.close()
            
            if affected_rows > 0:
                logger.debug(f"插入标题哈希成功: {title_hash}")
                return True
            else:
                logger.debug(f"标题哈希已存在: {title_hash}")
                return False
        except sqlite3.Error as e:
            logger.error(f"插入标题哈希失败: {e}")
            return False
    
    def get_all_hashes(self):
        """
        获取所有已存储的文章标题哈希值
        
        Returns:
            list: 哈希值列表
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT title_hash FROM article_hashes')
            hashes = [row[0] for row in cursor.fetchall()]
            
            conn.close()
            return hashes
        except sqlite3.Error as e:
            logger.error(f"获取所有哈希值失败: {e}")
            return []
    
    def insert_batch(self, titles):
        """
        批量插入文章标题的MD5哈希值
        
        Args:
            titles (list): 文章标题列表
            
        Returns:
            int: 成功插入的数量
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 计算所有标题的MD5哈希值
            title_hashes = [(self._get_md5(title),) for title in titles]
            
            # 使用批量插入
            cursor.executemany('INSERT OR IGNORE INTO article_hashes (title_hash) VALUES (?)', title_hashes)
            affected_rows = cursor.rowcount
            
            conn.commit()
            conn.close()
            
            logger.info(f"批量插入成功: {affected_rows} 条记录")
            return affected_rows
        except sqlite3.Error as e:
            logger.error(f"批量插入失败: {e}")
            return 0
    
    def close(self):
        """
        关闭数据库连接（当前实现为文件数据库，此方法主要用于兼容）
        """
        logger.debug("数据库连接已关闭")

# 创建全局数据库管理器实例
db_manager = DatabaseManager()
