# Web3资讯推送系统需求文档

## 一、系统概述

Web3资讯推送系统是一个基于适配器模式的爬虫推送系统，用于自动爬取加密货币相关资讯，并通过多种通知渠道推送给用户。系统支持灵活拓展爬虫源和通知源，实现“新增源无需修改核心代码”的设计目标。

## 二、系统架构

### 1. 设计模式
- **适配器模式**：定义统一的爬虫接口和通知接口，让不同的爬虫源/通知源通过适配器类实现接口。

### 2. 模块划分

| 模块 | 职责 | 文件路径 |
|------|------|----------|
| 抽象接口层 | 定义爬虫和通知的基类接口 | core/base.py |
| 适配器层 | 实现具体的爬虫和通知适配器 | adapters/spiders/、adapters/notifiers/ |
| 工具类层 | 数据库操作、配置读取、日志处理等通用工具 | utils/ |
| 核心服务层 | 协调爬虫采集、数据存储、通知推送的业务逻辑 | core/service.py |
| 调度层 | GitHub Action Workflow 定时触发任务 | .github/workflows/ |
| 配置层 | 统一管理系统配置 | config/custom-conf.yml |

## 三、核心功能模块

### 1. 爬虫模块

#### 1.1 抽象爬虫接口
- 定义统一的`fetch_data()`方法，用于爬取资讯数据
- 返回格式：`[{"title": str, "content": str, "url": str, "source": str, "publish_time": str}]`

#### 1.2 具体爬虫实现
- **币安爬虫**：爬取币安交易所公告
- **FORESIGHTNEWS爬虫**：爬取FORESIGHTNEWS资讯

### 2. 通知模块

#### 2.1 抽象通知接口
- 定义统一的`send_notification()`方法，用于发送通知
- 参数：待推送的资讯数据列表
- 返回：发送成功返回True，失败返回False

#### 2.2 具体通知实现
- **钉钉机器人通知**：通过钉钉机器人发送文本通知
- **邮箱通知**：通过SMTP发送HTML格式邮件

### 3. 数据存储模块
- 使用SQLite数据库进行数据持久化
- 实现资讯去重功能（通过URL判断）
- 记录资讯的标题、URL、来源、发布时间等信息

### 4. 配置管理模块
- 使用YAML格式配置文件
- 支持多级配置项读取
- 实现单例模式的配置工具类

### 5. 日志管理模块
- 支持控制台和文件日志输出
- 彩色日志格式，方便调试
- 记录系统运行状态和错误信息

### 6. 核心服务模块
- 协调爬虫采集、数据过滤、数据库存储、通知推送流程
- 实现异常处理和资源清理

## 四、技术栈

| 技术/库 | 版本 | 用途 |
|---------|------|------|
| Python | 3.8+ | 开发语言 |
| requests | 2.31.0 | 网络请求 |
| beautifulsoup4 | 4.12.2 | HTML解析 |
| lxml | 4.9.3 | HTML解析器 |
| PyYAML | 6.0.1 | YAML配置解析 |
| pycryptodome | 3.19.0 | 钉钉机器人签名 |
| colorlog | 6.7.0 | 彩色日志 |
| python-dotenv | 1.0.0 | 环境变量管理 |

## 五、接口设计

### 1. SpiderBase（爬虫基类）
```python
class SpiderBase(ABC):
    @abstractmethod
    def fetch_data(self) -> List[Dict]:
        """
        爬取数据的核心方法
        返回格式：[{"title": str, "content": str, "url": str, "source": str, "publish_time": str}]
        """
        pass
```

### 2. NotifierBase（通知基类）
```python
class NotifierBase(ABC):
    @abstractmethod
    def send_notification(self, data: List[Dict]) -> bool:
        """
        发送通知的核心方法
        :param data: 待推送的资讯数据
        :return: 发送成功返回True，失败返回False
        """
        pass
```

### 3. NewsPushService（核心服务）
```python
class NewsPushService:
    def __init__(self, spiders: List[Type[SpiderBase]], notifiers: List[Type[NotifierBase]]):
        """
        初始化服务
        :param spiders: 爬虫类列表
        :param notifiers: 通知类列表
        """
        pass
    
    def run(self):
        """执行资讯采集和推送"""
        pass
```

## 六、数据库设计

### 1. news表

| 字段名 | 数据类型 | 约束 | 描述 |
|--------|----------|------|------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | 自增主键 |
| title | TEXT | NOT NULL | 资讯标题 |
| url | TEXT | NOT NULL UNIQUE | 资讯链接（唯一，用于去重） |
| source | TEXT | NOT NULL | 资讯来源 |
| publish_time | TEXT | NOT NULL | 发布时间 |
| create_time | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 创建时间 |

## 七、配置文件设计

### 1. 配置文件结构

```yaml
# 爬虫配置
spiders:
  binance:
    url: "https://www.binance.com/cn/support/announcement/c-48"
  foresight_news:
    url: "https://www.foresightnews.pro/"

# 通知配置
notifiers:
  dingtalk:
    webhook: "https://oapi.dingtalk.com/robot/send?access_token=your-token"
    secret: "your-secret"  # 可选
  email:
    smtp_server: "smtp.163.com"
    smtp_port: 465
    smtp_user: "your-email@163.com"
    smtp_password: "your-password"
    to_emails: ["recipient1@example.com", "recipient2@example.com"]
```

### 2. 配置工具类
- 实现单例模式
- 支持多级配置项读取（如`spiders.binance.url`）

## 八、部署方案

### 1. 本地部署
- 安装依赖：`pip install -r requirements.txt`
- 配置环境：复制`config/custom-conf-sample.yml`为`config/custom-conf.yml`并修改配置
- 运行程序：`python main.py`

### 2. GitHub Actions 自动化部署
- 创建定时触发器，定期运行爬虫任务
- 配置环境变量和密钥
- 实现自动错误通知

## 九、开发进度

| 阶段 | 进度 | 预计完成时间 |
|------|------|--------------|
| 需求分析与设计 | 100% | 2025-12-15 |
| 系统架构设计 | 100% | 2025-12-15 |
| 代码实现 | 0% | 2025-12-17 |
| 测试与调试 | 0% | 2025-12-18 |
| 部署上线 | 0% | 2025-12-19 |

## 十、风险与解决方案

### 1. 爬虫被反爬
- **风险**：目标网站可能会限制爬虫访问
- **解决方案**：
  - 使用合理的请求头（User-Agent）
  - 实现请求延迟
  - 考虑使用代理IP池

### 2. 通知发送失败
- **风险**：通知服务可能不可用或配置错误
- **解决方案**：
  - 实现重试机制
  - 记录详细的错误日志
  - 支持多种通知渠道 fallback

### 3. 数据格式变更
- **风险**：目标网站的HTML结构可能会变更，导致爬虫失效
- **解决方案**：
  - 定期检查爬虫状态
  - 实现自适应解析（减少对特定DOM结构的依赖）
  - 提供详细的错误报警
