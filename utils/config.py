import yaml
import os
import json
from typing import Dict, Any

class ConfigLoader:
    """
    配置文件加载工具类
    """
    
    # 配置项与环境变量的映射关系
    CONFIG_ENV_MAP = {
        # 钉钉通知配置
        "notifiers.dingtalk.webhook": "DINGTALK_WEBHOOK",
        "notifiers.dingtalk.secret": "DINGTALK_SECRET",
        # 邮件通知配置
        "notifiers.email.smtp_server": "EMAIL_SMTP_SERVER",
        "notifiers.email.smtp_port": "EMAIL_SMTP_PORT",
        "notifiers.email.smtp_user": "EMAIL_SMTP_USER",
        "notifiers.email.smtp_password": "EMAIL_SMTP_PASSWORD",
        "notifiers.email.to_emails": "EMAIL_TO_EMAILS",
        # Bark通知配置
        "notifiers.bark.api_url": "BARK_API_URL",
        "notifiers.bark.device_key": "BARK_DEVICE_KEY",
        "notifiers.bark.group": "BARK_GROUP",
        "pool.max_workers": "POOL_MAX_WORKERS",
        "logger.level": "LOG_LEVEL",
    }
    
    def __init__(self, config_path: str = None):
        """
        初始化配置加载器
        
        :param config_path: 配置文件路径，如果不指定则使用默认路径
        """
        self.config_path = config_path or os.path.join(os.path.dirname(__file__), "..", "config", "custom-conf-sample.yml")
        self.config = None
        self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """
        加载配置文件
        
        :return: 配置字典
        """
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
                return self.config
        except FileNotFoundError:
            # 配置文件不存在时，从环境变量构建配置
            print(f"配置文件未找到: {self.config_path}，将从环境变量获取配置")
            self.config = {}
            # 合并环境变量中的配置到配置字典
            for config_path, env_var in self.CONFIG_ENV_MAP.items():
                env_value = self._get_from_env(config_path)
                if env_value is not None:
                    # 将配置路径转换为嵌套字典
                    parts = config_path.split(".")
                    current = self.config
                    for part in parts[:-1]:
                        if part not in current:
                            current[part] = {}
                        current = current[part]
                    current[parts[-1]] = env_value
            return self.config
        except yaml.YAMLError as e:
            print(f"配置文件解析错误: {e}")
            raise
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            raise
    
    def _get_from_env(self, config_path: str) -> Any:
        """
        从环境变量获取配置值
        
        :param config_path: 配置路径，如 "notifiers.dingtalk.webhook"
        :return: 环境变量中的配置值，如果不存在则返回None
        """
        env_var = self.CONFIG_ENV_MAP.get(config_path)
        if env_var:
            value = os.environ.get(env_var)
            if value is not None:
                # 特殊处理某些类型的环境变量
                if config_path.endswith(".to_emails"):
                    # 将逗号分隔的字符串转换为列表
                    return [email.strip() for email in value.split(",")]
                elif config_path.endswith(".smtp_port"):
                    # 将字符串转换为整数
                    try:
                        return int(value)
                    except ValueError:
                        pass
            return value
        return None
    
    def get_config(self, section: str = None, key: str = None) -> Any:
        """
        获取配置项
        
        :param section: 配置节
        :param key: 配置键
        :return: 配置值
        """
        # 先尝试从环境变量获取完整配置
        if section is None and key is None:
            config = self.config.copy() if self.config else {}
            # 合并环境变量中的配置到配置字典
            for config_path, env_var in self.CONFIG_ENV_MAP.items():
                env_value = self._get_from_env(config_path)
                if env_value is not None:
                    # 将配置路径转换为嵌套字典
                    parts = config_path.split(".")
                    current = config
                    for part in parts[:-1]:
                        if part not in current:
                            current[part] = {}
                        current = current[part]
                    current[parts[-1]] = env_value
            return config
        
        # 构建完整配置路径
        config_path = section
        if key:
            config_path = f"{section}.{key}"
        
        # 先从环境变量获取
        env_value = self._get_from_env(config_path)
        if env_value is not None:
            return env_value
        
        # 如果环境变量中没有，再从配置文件获取
        if self.config is None:
            self.load_config()
        
        if section is None:
            return self.config
        
        if section not in self.config:
            # 尝试从环境变量构建整个section
            section_value = {}
            for path, env_var in self.CONFIG_ENV_MAP.items():
                if path.startswith(f"{section}."):
                    parts = path.split(".")[1:]
                    current = section_value
                    for part in parts[:-1]:
                        if part not in current:
                            current[part] = {}
                        current = current[part]
                    env_val = self._get_from_env(path)
                    if env_val is not None:
                        current[parts[-1]] = env_val
            if section_value:
                return section_value
            raise KeyError(f"配置节不存在: {section}")
        
        if key is None:
            return self.config[section]
        
        if key not in self.config[section]:
            raise KeyError(f"配置键不存在: {key}")
        
        return self.config[section][key]

# 全局配置实例
config_loader = ConfigLoader()
