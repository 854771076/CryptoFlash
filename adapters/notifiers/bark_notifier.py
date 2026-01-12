import requests
from typing import List, Dict
from core.base import NotifierBase
from utils.logger import logger
from utils.config import config_loader

class BarkNotifier(NotifierBase):
    """
    Bark通知适配器，用于向iOS设备发送推送通知
    """
    name='bark'
    
    def __init__(self, config: Dict = None):
        """
        初始化Bark通知器
        """
        super().__init__(config)
        self.api_url = self.config.get("api_url") or "https://api.day.app"
        self.device_key = self.config.get("device_key") 
        self.group = self.config.get("group") or "crypto_flash"
        
        assert self.device_key, "Bark通知器未配置device_key"
    
    def send_notification(self, data: List[Dict], markdown_content: str = None) -> bool:
        """
        发送Bark通知
        
        :param data: 待推送的资讯数据
        :param markdown_content: 预生成的markdown格式通知内容
        :return: 发送成功返回True，失败返回False
        """
        if not data:
            logger.info("没有数据需要推送到Bark")
            return True
        
        try:
            if markdown_content:
                # 使用预生成的markdown内容进行批量发送
                logger.info(f"开始推送 {len(data)} 条数据到Bark（批量）")
                
                # Bark API有内容大小限制（约2000字节），需要分页发送
                max_content_size = 1900  # 留100字节作为安全余量
                content_bytes = markdown_content.encode('utf-8')
                
                if len(content_bytes) > max_content_size:
                    # 需要分页发送
                    logger.info(f"内容大小 {len(content_bytes)} 字节超过限制，开始分页发送")
                    
                    # 将markdown内容按行分割
                    lines = markdown_content.split('\n')
                    
                    # 先将内容分割成多个页面
                    pages = []
                    current_page = []
                    current_size = 0
                    
                    for line in lines:
                        line_size = len((line + '\n').encode('utf-8'))
                        
                        # 如果加上当前行后超过限制，完成当前页
                        if current_size + line_size > max_content_size:
                            # 构建当前页的内容
                            page_content = '\n'.join(current_page)
                            pages.append(page_content)
                            
                            # 开始新页面
                            current_page = [line]
                            current_size = line_size
                        else:
                            # 继续添加到当前页
                            current_page.append(line)
                            current_size += line_size
                    
                    # 添加最后一页
                    if current_page:
                        page_content = '\n'.join(current_page)
                        pages.append(page_content)
                    
                    # 发送所有页面
                    total_pages = len(pages)
                    for page_number, page_content in enumerate(pages, 1):
                        # 构建消息内容
                        msg = {
                            "device_key": self.device_key,
                            "title": f"加密货币资讯 ({len(data)} 条) - 第{page_number}/{total_pages}页",
                            "markdown": page_content,
                            "group": self.group
                        }
                        
                        # 发送请求
                        response = requests.post(
                            f"{self.api_url}/push",
                            json=msg,
                            headers={"Content-Type": "application/json; charset=utf-8"}
                        )
                        response.raise_for_status()
                        
                        # 检查返回结果
                        result = response.json()
                        # 支持两种返回格式：{"ok": true} 和 {"code": 200}
                        if not (result.get("ok") or result.get("code")==200):
                            logger.error(f"批量推送数据到Bark（第{page_number}页）失败: {result}")
                            return False
                        logger.info(f"批量推送数据到Bark（第{page_number}页）成功")
                        
                        # 防止发送过快，添加延时
                        import time
                        time.sleep(1)
                else:
                    # 内容大小未超过限制，直接发送
                    # 构建消息内容
                    msg = {
                        "device_key": self.device_key,
                        "title": f"加密货币资讯 ({len(data)} 条)",
                        "markdown": markdown_content,
                        "group": self.group
                    }
                    
                    # 发送请求
                    response = requests.post(
                        f"{self.api_url}/push",
                        json=msg,
                        headers={"Content-Type": "application/json; charset=utf-8"}
                    )
                    response.raise_for_status()
                    
                    # 检查返回结果
                    result = response.json()
                    # 支持两种返回格式：{"ok": true} 和 {"code": 200}
                    if not (result.get("ok") or result.get("code")==200):
                        logger.error(f"批量推送数据到Bark失败: {result}")
                        return False
            else:
                # 逐条发送逻辑（兼容旧版）
                logger.info(f"开始推送 {len(data)} 条数据到Bark（逐条）")
                for item in data:
                    # 构建消息内容
                    msg = {
                        "device_key": self.device_key,
                        "title": item.get("title", ""),
                        "body": f"来源: {item.get('source', '')}\n"\
                               f"发布时间: {item.get('publish_time', '')}\n"\
                               f"内容: {item.get('content', '')}\n"\
                               f"查看详情: {item.get('url', '')}",
                        "group": self.group,
                        "url": item.get("url", "")
                    }
                    
                    # 发送请求
                    response = requests.post(
                        f"{self.api_url}/push",
                        json=msg,
                        headers={"Content-Type": "application/json; charset=utf-8"}
                    )
                    response.raise_for_status()
                    
                    # 检查返回结果
                    result = response.json()
                    # 支持两种返回格式：{"ok": true} 和 {"code": 200}
                    if not (result.get("ok") or result.get("code")==200):
                        logger.error(f"推送单条数据到Bark失败: {result}")
                        return False
                    
                    # 防止发送过快，添加延时
                    import time
                    time.sleep(1)
            
            logger.info("所有数据推送Bark成功")
            return True
        except requests.RequestException as e:
            logger.error(f"请求Bark API失败: {e}")
            return False
        except Exception as e:
            logger.error(f"推送数据到Bark失败: {e}")
            return False
