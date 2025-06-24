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
    async def extract_image_urls(self, url: str) -> List[ImageInfo]:
        """
        从指定URL提取所有图片信息
        
        Args:
            url: 目标网页URL
            
        Returns:
            List[ImageInfo]: 图片信息列表
        """
        pass
    
    @abstractmethod
    async def download_image(self, image_info: ImageInfo, save_dir: str) -> bool:
        """
        下载单张图片
        
        Args:
            image_info: 图片信息
            save_dir: 保存目录
            
        Returns:
            bool: 下载是否成功
        """
        pass
    
    async def batch_download(self, image_infos: List[ImageInfo], save_dir: str, 
                           max_concurrent: int = 5) -> Dict:
        """
        批量下载图片（默认实现）
        
        Args:
            image_infos: 图片信息列表
            save_dir: 保存目录
            max_concurrent: 最大并发数
            
        Returns:
            Dict: 下载结果统计
        """
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def download_with_semaphore(image_info):
            async with semaphore:
                return await self.download_image(image_info, save_dir)
        
        tasks = [download_with_semaphore(info) for info in image_infos]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 更新统计信息
        successful = sum(1 for r in results if r is True)
        failed = len(results) - successful
        
        self.stats['images_downloaded'] = successful
        self.stats['images_failed'] = failed
        
        return {
            'successful': successful,
            'failed': failed,
            'total_size': self.stats['total_size']
        }
    
    @abstractmethod
    async def cleanup(self):
        """清理资源"""
        pass
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return self.stats.copy()
    
    def update_config(self, config: Dict):
        """更新配置"""
        self.config.update(config) 