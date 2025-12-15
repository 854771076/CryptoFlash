import os
import sys

# 将项目根目录添加到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.service import CryptoFlashService
if __name__ == "__main__":
    service = CryptoFlashService()
    service.run()