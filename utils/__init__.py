"""
Image-tools v4.0 工具模块

包含各种辅助工具和配置管理器：
- BrowserConfig: 浏览器反检测配置
- ProxyManager: 代理管理器  
- ImageAnalyzer: 图片分析工具
"""

from .browser_config import BrowserConfig
from .image_analyzer import ImageAnalyzer
from .proxy_manager import ProxyManager

__version__ = "4.0.0"
__all__ = ["BrowserConfig", "ImageAnalyzer", "ProxyManager"]

# ProxyManager延迟导入
def get_proxy_manager():
    """获取代理管理器"""
    from .proxy_manager import ProxyManager 