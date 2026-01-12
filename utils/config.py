import yaml
import os
import json
import re
import ast
from typing import Dict, Any, List

class ConfigLoader:
    """
    配置文件加载工具类
    """
    
    # 配置项与环境变量的映射关系
    CONFIG_ENV_MAP = {
        # 钉钉通知配置
        "spiders.twitter.nitter_instance": "NITTER_INSTANCE",
        "spiders.twitter.username": "TWITTER_USERNAME",
        "notifiers.dingtalk.webhook": "DINGTALK_WEBHOOK",
        "notifiers.dingtalk.secret": "DINGTALK_SECRET",
        "notifiers.dingtalk.sources": "DINGTALK_SOURCES",
        # 邮件通知配置
        "notifiers.email.smtp_server": "EMAIL_SMTP_SERVER",
        "notifiers.email.smtp_port": "EMAIL_SMTP_PORT",
        "notifiers.email.smtp_user": "EMAIL_SMTP_USER",
        "notifiers.email.smtp_password": "EMAIL_SMTP_PASSWORD",
        "notifiers.email.to_emails": "EMAIL_TO_EMAILS",
        "notifiers.email.sources": "EMAIL_SOURCES",
        # Bark通知配置
        "notifiers.bark.api_url": "BARK_API_URL",
        "notifiers.bark.device_key": "BARK_DEVICE_KEY",
        "notifiers.bark.group": "BARK_GROUP",
        "notifiers.bark.sources": "BARK_SOURCES",
        # 爬虫配置 (示例，可以根据需要添加更多)
        "spiders.binance.url": "BINANCE_URL",
        "spiders.foresight_news.url": "FORESIGHT_NEWS_URL",
        "spiders.okx_boost.url": "OKX_BOOST_URL",
        
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
                    self._merge_config(self.config, config_path, env_value)
            return self.config
        except yaml.YAMLError as e:
            print(f"配置文件解析错误: {e}")
            raise
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            raise
    
    def _get_from_env(self, config_path: str) -> Any:
        """
        从环境变量获取配置值，支持逗号分隔的多实例配置
        """
        env_var = self.CONFIG_ENV_MAP.get(config_path)
        if env_var:
            value = os.environ.get(env_var)
            if value is not None:
                # 按照不在中括号内的逗号进行分割
                parts = re.split(r',(?![^\[]*\])', value)
                parsed_parts = []
                for part in parts:
                    part = part.strip()
                    if not part:
                        continue
                    
                    # 尝试解析为 Python 字面量（如列表）
                    if part.startswith('[') and part.endswith(']'):
                        try:
                            parsed_parts.append(ast.literal_eval(part))
                            continue
                        except (ValueError, SyntaxError):
                            pass
                    
                    # 特殊处理某些类型的环境变量
                    if config_path.endswith(".smtp_port") or config_path.endswith(".max_workers"):
                        try:
                            parsed_parts.append(int(part))
                        except ValueError:
                            parsed_parts.append(part)
                    elif config_path.endswith(".to_emails") or config_path.endswith(".sources"):
                        # 如果不是以 [ 开头但又是列表字段，且没有被 re.split 分割（即只有一个值且没带括号）
                        # 或者已经被分割了但没带括号，我们需要确保它是个列表
                        if isinstance(part, str):
                             parsed_parts.append([item.strip() for item in part.split(",") if item.strip()])
                        else:
                             parsed_parts.append(part)
                    else:
                        parsed_parts.append(part)
                
                if not parsed_parts:
                    return None
                
                # 如果只有一个值，且不是列表字段（或者列表字段已经包装好了），则返回单个值
                # 但为了支持多实例，如果原始字符串包含逗号（且不在括号内），我们应该返回列表
                if len(parsed_parts) == 1 and ',' not in value:
                    return parsed_parts[0]
                
                return parsed_parts
        return None

    def _merge_config(self, config_dict: Dict, config_path: str, value: Any):
        """
        将配置项合并到字典中，支持列表结构和多实例
        """
        parts = config_path.split(".")
        
        # 如果 value 不是列表，但我们想要支持多实例，我们需要将其包装一下
        # 除非它本身就是某个字段的列表值（如 sources）
        # 这里的逻辑是：如果 _get_from_env 返回了列表，说明有多个实例的值
        values = value if isinstance(value, list) and not config_path.endswith((".sources", ".to_emails")) else [value]
        
        # 如果是 sources 或 to_emails，且 _get_from_env 返回的是列表的列表，说明是多实例
        if config_path.endswith((".sources", ".to_emails")) and isinstance(value, list) and len(value) > 0 and isinstance(value[0], list):
            values = value

        for idx, val in enumerate(values):
            current = config_dict
            for i, part in enumerate(parts[:-1]):
                if isinstance(current, list):
                    # 寻找第 idx 个类型为 part 的项
                    found_count = 0
                    target_item = None
                    for item in current:
                        if isinstance(item, dict) and item.get('type') == part:
                            if found_count == idx:
                                target_item = item
                                break
                            found_count += 1
                    
                    if target_item:
                        current = target_item
                    else:
                        # 如果没找到，创建新的项直到达到 idx
                        while found_count <= idx:
                            new_item = {'type': part}
                            current.append(new_item)
                            if found_count == idx:
                                current = new_item
                            found_count += 1
                else:
                    if part not in current:
                        if part in ['spiders', 'notifiers']:
                            current[part] = []
                        else:
                            current[part] = {}
                    current = current[part]
            
            # 设置值
            if not isinstance(current, list):
                current[parts[-1]] = val
    
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
                    self._merge_config(config, config_path, env_value)
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
