import hmac
import hashlib
import base64
import urllib.parse
import time
from typing import List, Dict
from core.base import NotifierBase
from utils.logger import logger
from utils.config import config_loader
import requests
class DingTalkNotifier(NotifierBase):
    """
    钉钉通知适配器
    """
    name='dingtalk'
    def __init__(self, config: Dict = None):
        """
        初始化钉钉通知器
        """
        super().__init__(config)
        self.webhook = self.config.get("webhook")
        self.secret = self.config.get("secret") 
        assert self.webhook, "钉钉通知器未配置webhook"
        assert self.secret, "钉钉通知器未配置secret"
    
    def _generate_signature(self) -> str:
        """
        生成钉钉签名
        
        :return: 签名后的URL
        """
        if not self.secret:
            return self.webhook
        
        timestamp = str(round(time.time() * 1000))
        secret_enc = self.secret.encode('utf-8')
        string_to_sign = '{}\n{}'.format(timestamp, self.secret)
        string_to_sign_enc = string_to_sign.encode('utf-8')
        hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
        sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
        return f"{self.webhook}&timestamp={timestamp}&sign={sign}"
    
    def send_notification(self, data: List[Dict], markdown_content: str = None) -> bool:
        """
        发送钉钉通知
        
        :param data: 待推送的资讯数据
        :param markdown_content: 预生成的markdown格式通知内容
        :return: 发送成功返回True，失败返回False
        """
        if not data:
            logger.info("没有数据需要推送到钉钉")
            return True
        
        # 生成带签名的webhook
        webhook_url = self._generate_signature()
        
        try:
            if markdown_content:
                # 使用预生成的markdown内容进行批量发送
                logger.info(f"开始推送 {len(data)} 条数据到钉钉（批量）")
                
                # 构建消息内容
                msg = {
                    "msgtype": "markdown",
                    "markdown": {
                        "title": f"加密货币资讯 ({len(data)} 条)",
                        "text": markdown_content
                    }
                }
                
                # 发送请求
                response = requests.post(
                    webhook_url,
                    json=msg,
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
                
                # 检查返回结果
                result = response.json()
                if result.get("errcode") != 0:
                    logger.error(f"批量推送数据到钉钉失败: {result.get('errmsg')}")
                    return False
            else:
                # 逐条发送逻辑（兼容旧版）
                logger.info(f"开始推送 {len(data)} 条数据到钉钉（逐条）")
                for item in data:
                    # 构建消息内容
                    msg = {
                        "msgtype": "markdown",
                        "markdown": {
                            "title": item.get("title", ""),
                            "text": f"### {item.get('title', '')}\n"
                                    f"**来源**: {item.get('source', '')}\n"
                                    f"**发布时间**: {item.get('publish_time', '')}\n"
                                    f"**内容**: {item.get('content', '')}\n"
                                    f"[查看详情]({item.get('url', '')})"
                        }
                    }
                    
                    # 发送请求
                    response = requests.post(
                        webhook_url,
                        json=msg,
                        headers={"Content-Type": "application/json"}
                    )
                    response.raise_for_status()
                    
                    # 检查返回结果
                    result = response.json()
                    if result.get("errcode") != 0:
                        logger.error(f"推送单条数据到钉钉失败: {result.get('errmsg')}")
                        return False
                    
                    # 防止发送过快，添加延时
                    time.sleep(1)
            
            logger.info("所有数据推送钉钉成功")
            return True
        except requests.RequestException as e:
            logger.error(f"请求钉钉API失败: {e}")
            return False
        except Exception as e:
            logger.error(f"推送数据到钉钉失败: {e}")
            return False
