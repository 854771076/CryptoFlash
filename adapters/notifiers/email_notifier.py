import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict
from core.base import NotifierBase
from utils.logger import logger
from utils.config import config_loader

class EmailNotifier(NotifierBase):
    """
    邮件通知适配器
    """
    name='email'
    def __init__(self):
        """
        初始化邮件通知器
        """
        email_config = config_loader.get_config("notifiers", "email")
        self.smtp_server = email_config.get("smtp_server")
        self.smtp_port = email_config.get("smtp_port", 465)  # 默认465端口
        self.smtp_user = email_config.get("smtp_user")
        self.smtp_password = email_config.get("smtp_password")
        self.to_emails = email_config.get("to_emails", [])
        assert self.smtp_server, "邮件通知器未配置SMTP服务器"
        assert self.smtp_user, "邮件通知器未配置SMTP用户名"
        assert self.smtp_password, "邮件通知器未配置SMTP密码"
        assert self.to_emails, "邮件通知器未配置收件人邮箱"
        assert self.from_email, "邮件通知器未配置发件人邮箱"



    
    def send_notification(self, data: List[Dict], markdown_content: str = None) -> bool:
        """
        发送邮件通知
        
        :param data: 待推送的资讯数据
        :param markdown_content: 预生成的markdown格式通知内容
        :return: 发送成功返回True，失败返回False
        """
        if not data:
            logger.info("没有数据需要发送邮件")
            return True
        
        if not self.to_emails:
            logger.warning("未配置收件人邮箱")
            return False
        
        try:
            # 连接SMTP服务器
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                server.login(self.smtp_user, self.smtp_password)
                
                if markdown_content:
                    # 使用预生成的markdown内容进行批量发送
                    logger.info(f"开始发送 {len(data)} 条数据到邮箱: {', '.join(self.to_emails)}（批量）")
                    
                    # 创建邮件
                    msg = MIMEMultipart()
                    msg['From'] = self.smtp_user
                    msg['To'] = ', '.join(self.to_emails)
                    msg['Subject'] = f"加密货币资讯 ({len(data)} 条)"
                    
                    # 构建邮件内容
                    html_body = f"""
                    <html>
                    <body>
                        <pre style="font-family: Arial, sans-serif; white-space: pre-wrap;">
                            {markdown_content}
                        </pre>
                    </body>
                    </html>
                    """
                    
                    # 同时添加纯文本和HTML格式的内容
                    msg.attach(MIMEText(markdown_content, 'plain', 'utf-8'))
                    msg.attach(MIMEText(html_body, 'html', 'utf-8'))
                    
                    # 发送邮件
                    server.send_message(msg)
                else:
                    # 逐条发送逻辑（兼容旧版）
                    logger.info(f"开始发送 {len(data)} 条数据到邮箱: {', '.join(self.to_emails)}（逐条）")
                    for item in data:
                        # 创建邮件
                        msg = MIMEMultipart()
                        msg['From'] = self.smtp_user
                        msg['To'] = ', '.join(self.to_emails)
                        msg['Subject'] = item.get("title", "")
                        
                        # 构建邮件内容
                        body = f"""
                        【{item.get('source', '')}】{item.get('title', '')}
                        
                        发布时间: {item.get('publish_time', '')}
                        
                        内容摘要:
                        {item.get('content', '')}
                        
                        查看详情: {item.get('url', '')}
                        """
                        
                        msg.attach(MIMEText(body, 'plain', 'utf-8'))
                        
                        # 发送邮件
                        server.send_message(msg)
                
                logger.info("所有数据发送邮件成功")
                return True
        except smtplib.SMTPException as e:
            logger.error(f"SMTP操作失败: {e}")
            return False
        except Exception as e:
            logger.error(f"发送邮件失败: {e}")
            return False
