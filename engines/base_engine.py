"""
图片爬取引擎抽象基类

定义了所有爬取引擎必须实现的接口，确保不同引擎之间的一致性。
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
import asyncio
from pathlib import Path


class ImageInfo:
    """图片信息数据类"""
    
    def __init__(self, url: str, filename: str = "", metadata: Dict = None):
        self.url = url
        self.filename = filename or self._extract_filename_from_url(url)
        self.metadata = metadata or {}
        self.size = None
        self.format = None
    
    def _extract_filename_from_url(self, url: str) -> str:
        """从URL中提取文件名"""
        try:
            from urllib.parse import urlparse
            path = urlparse(url).path
            return Path(path).name if path else "unknown_image"
        except:
            return "unknown_image"
    
    def __str__(self):
        return f"ImageInfo(url={self.url[:50]}..., filename={self.filename})"


class BaseImageEngine(ABC):
    """图片爬取引擎抽象基类"""
    
    def __init__(self):
        self.config = {}
        self.session_data = {}
        self.stats = {
            'images_found': 0,
            'images_downloaded': 0,
            'images_failed': 0,
            'total_size': 0
        }
    
    @abstractmethod
    async def initialize(self, config: Dict) -> bool:
        """
        初始化引擎
        
        Args:
            config: 配置字典
            
        Returns:
            bool: 初始化是否成功
        """
        pass
    
    @abstractmethod
    async def extract_image 