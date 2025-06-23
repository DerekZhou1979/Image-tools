"""
代理管理器

提供代理服务器的配置和管理功能
"""

import asyncio
import aiohttp
from typing import Dict, List, Optional, Tuple
import random
import time


class ProxyManager:
    """代理管理器类"""
    
    def __init__(self, proxy_config: Dict):
        self.proxy_config = proxy_config
        self.proxy_list = []
        self.current_proxy = None
        self.failed_proxies = set()
        
    def is_enabled(self) -> bool:
        """检查代理是否启用"""
        return self.proxy_config.get('enabled', False)
    
    def get_proxy_url(self) -> Optional[str]:
        """获取代理URL"""
        if not self.is_enabled():
            return None
        
        server = self.proxy_config.get('server', '')
        if not server:
            return None
        
        proxy_type = self.proxy_config.get('type', 'http')
        username = self.proxy_config.get('username', '')
        password = self.proxy_config.get('password', '')
        
        if username and password:
            return f"{proxy_type}://{username}:{password}@{server}"
        elif username:
            return f"{proxy_type}://{username}@{server}"
        else:
            return f"{proxy_type}://{server}" 