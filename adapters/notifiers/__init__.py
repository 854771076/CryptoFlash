# 通知适配器初始化文件
from .dingtalk_notifier import DingTalkNotifier
from .email_notifier import EmailNotifier

__all__ = ['DingTalkNotifier', 'EmailNotifier']
