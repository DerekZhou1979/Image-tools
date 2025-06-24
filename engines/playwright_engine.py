"""
基于Playwright的高级图片爬取引擎

专门设计用于应对现代网站的反爬虫机制，包括：
- Cloudflare保护
- JavaScript动态加载
- 懒加载图片
- 会话验证和防盗链
"""

import asyncio
import os
import re
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse

try:
    from playwright.async_api import async_playwright, Browser, BrowserContext, Page, Response
    PLAYWRIGHT_IMPORTED = True
except ImportError:
    PLAYWRIGHT_IMPORTED = False

from .base_engine import BaseImageEngine, ImageInfo
from utils.browser_config import BrowserConfig

class PlaywrightImageEngine(BaseImageEngine):
    """基于Playwright的图片爬取引擎"""
    
    def __init__(self):
        super().__init__()
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        
    async def initialize(self, config: Dict) -> bool:
        """初始化Playwright浏览器"""
        if not PLAYWRIGHT_IMPORTED:
            self.log_error("Playwright未安装，请运行: pip install playwright && python -m playwright install chromium")
            return False
        
        try:
            self.config = config
            engine_settings = config.get('engine_settings', {})
            
            self.playwright = await async_playwright().start()
            browser_type = engine_settings.get('browser_type', 'chromium')
            browser_launcher = getattr(self.playwright, browser_type)
            
            launch_options = {
                'headless': engine_settings.get('headless', True),
                'args': BrowserConfig.get_stealth_launch_args() if engine_settings.get('stealth_mode', True) else []
            }
            
            self.browser = await browser_launcher.launch(**launch_options)
            context_options = BrowserConfig.get_stealth_context_options()
            
            proxy_settings = config.get('proxy_settings', {})
            if proxy_settings.get('enabled', False):
                proxy_config = BrowserConfig.get_proxy_config(proxy_settings)
                if proxy_config:
                    context_options['proxy'] = proxy_config
            
            self.context = await self.browser.new_context(**context_options)
            
            if engine_settings.get('stealth_mode', True):
                await self._inject_stealth_scripts()
            
            self.page = await self.context.new_page()
            await self._setup_page_handlers()
            
            self.log_info("Playwright引擎初始化成功")
            return True
            
        except Exception as e:
            self.log_error("Playwright引擎初始化失败", e)
            await self.cleanup()
            return False
    
    async def _inject_stealth_scripts(self):
        stealth_scripts = BrowserConfig.get_stealth_scripts()
        for script in stealth_scripts:
            await self.context.add_init_script(script)
    
    async def _setup_page_handlers(self):
        self.page.on('dialog', lambda dialog: asyncio.create_task(dialog.dismiss()))
        self.page.on('pageerror', lambda error: self.log_error(f"页面错误: {error}"))
    
    async def extract_image_urls(self, url: str) -> List[ImageInfo]:
        try:
            self.log_info(f"正在访问页面: {url}")
            response = await self.page.goto(url, wait_until='networkidle', timeout=60000)
            
            if not response or not response.ok:
                self.log_error(f"页面加载失败: {response.status if response else 'No response'}")
                return []
            
            await self._handle_cookie_consent()
            await self._enhanced_lazy_load_scroll()
            await self._wait_for_all_images_loaded()
            
            image_infos = await self._extract_all_images()
            self.stats['images_found'] = len(image_infos)
            self.log_info(f"成功提取到 {len(image_infos)} 张图片")
            return image_infos
            
        except Exception as e:
            self.log_error("提取图片URL失败", e)
            return []
    
    async def _handle_cookie_consent(self):
        consent_selectors = ['button:has-text("Accept")', 'button:has-text("同意")']
        for selector in consent_selectors:
            try:
                await self.page.click(selector, timeout=2000)
                self.log_info("已处理Cookie同意弹窗")
                return
            except:
                pass
    
    async def _smart_scroll(self):
        scroll_config = BrowserConfig.get_scroll_behavior_config(self.config)
        if not scroll_config.get('enabled', True): return

        self.log_info("开始智能滚动...")
        last_height = 0
        for _ in range(scroll_config.get('max_scroll_attempts', 10)):
            current_height = await self.page.evaluate('document.body.scrollHeight')
            await self.page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            await self.page.wait_for_timeout(int(scroll_config.get('scroll_pause_time', 2.0) * 1000))
            if current_height == last_height:
                break
            last_height = current_height

    async def _enhanced_lazy_load_scroll(self):
        """增强的懒加载滚动策略 - 专门针对Chrono24等电商网站"""
        scroll_config = BrowserConfig.get_scroll_behavior_config(self.config)
        if not scroll_config.get('enabled', True): 
            return

        self.log_info("开始增强懒加载滚动策略...")
        
        # 第一阶段：渐进式滚动，触发懒加载
        self.log_info("阶段1: 渐进式滚动触发懒加载")
        viewport_height = await self.page.evaluate('window.innerHeight')
        total_height = await self.page.evaluate('document.body.scrollHeight')
        
        # 小步滚动，每次滚动一个视口的高度
        current_position = 0
        scroll_step = viewport_height * 0.8  # 每次滚动80%视口高度，确保重叠
        
        while current_position < total_height:
            await self.page.evaluate(f'window.scrollTo(0, {current_position})')
            await self.page.wait_for_timeout(1500)  # 等待懒加载触发
            
            # 等待网络空闲，确保图片请求发出
            try:
                await self.page.wait_for_load_state('networkidle', timeout=3000)
            except:
                pass
                
            current_position += scroll_step
            # 重新获取总高度，因为可能有动态内容加载
            total_height = await self.page.evaluate('document.body.scrollHeight')
        
        # 第二阶段：滚动到底部，确保所有内容都被触发
        self.log_info("阶段2: 滚动到页面底部")
        await self.page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
        await self.page.wait_for_timeout(3000)
        
        # 第三阶段：再次从顶部到底部滚动，确保所有懒加载都被触发
        self.log_info("阶段3: 二次扫描滚动")
        await self.page.evaluate('window.scrollTo(0, 0)')
        await self.page.wait_for_timeout(2000)
        
        final_height = await self.page.evaluate('document.body.scrollHeight')
        current_position = 0
        scroll_step = viewport_height
        
        while current_position < final_height:
            await self.page.evaluate(f'window.scrollTo(0, {current_position})')
            await self.page.wait_for_timeout(800)  # 更快的二次扫描
            current_position += scroll_step
            
        # 最后滚动到底部
        await self.page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
        self.log_info("增强懒加载滚动完成")

    async def _wait_for_all_images_loaded(self):
        """等待所有图片完全加载完成"""
        self.log_info("等待所有图片加载完成...")
        
        # 等待所有图片元素都有真实的src属性
        max_wait_time = 30  # 最多等待30秒
        wait_interval = 2   # 每2秒检查一次
        waited_time = 0
        
        while waited_time < max_wait_time:
            # 检查页面中的图片加载状态
            image_status = await self.page.evaluate('''() => {
                const images = Array.from(document.querySelectorAll('img'));
                let total = images.length;
                let loaded = 0;
                let withSrc = 0;
                
                images.forEach(img => {
                    if (img.src && !img.src.startsWith('data:')) {
                        withSrc++;
                    }
                    if (img.complete && img.naturalWidth > 0) {
                        loaded++;
                    }
                });
                
                return { total, loaded, withSrc };
            }''')
            
            self.log_info(f"图片加载状态: {image_status['loaded']}/{image_status['total']} 加载完成, {image_status['withSrc']} 个有有效src")
            
            # 如果大部分图片都已加载，就可以继续
            if image_status['total'] > 0:
                load_ratio = image_status['loaded'] / image_status['total']
                src_ratio = image_status['withSrc'] / image_status['total']
                
                if load_ratio > 0.8 and src_ratio > 0.9:  # 80%加载完成，90%有src
                    self.log_info("图片加载达到阈值，继续处理")
                    break
            
            await self.page.wait_for_timeout(wait_interval * 1000)
            waited_time += wait_interval
        
        # 最后等待网络空闲
        try:
            await self.page.wait_for_load_state('networkidle', timeout=5000)
            self.log_info("网络已空闲，图片加载完成")
        except:
            self.log_info("网络等待超时，继续处理")
        
        # 额外等待确保所有懒加载都完成
        await self.page.wait_for_timeout(3000)

    async def _extract_all_images(self) -> List[ImageInfo]:
        self.log_info("正在从DOM中提取图片...")
        images_data = await self.page.evaluate('''() => {
            return Array.from(document.querySelectorAll('img')).map(img => ({
                url: img.currentSrc || img.src,
                alt: img.alt || '',
                width: img.naturalWidth,
                height: img.naturalHeight
            }));
        }''')

        image_infos = []
        for data in images_data:
            if not data['url'] or data['url'].startswith('data:'): continue
            if data['width'] < 50 or data['height'] < 50: continue
            
            absolute_url = urljoin(self.page.url, data['url'])
            image_infos.append(ImageInfo(url=absolute_url, metadata=data))
        
        self.log_info(f"DOM中提取到 {len(image_infos)} 张有效图片")
        return image_infos

    async def download_image(self, image_info: ImageInfo, save_dir: str) -> bool:
        """下载单张图片 - 使用Playwright浏览器会话"""
        save_path = os.path.join(save_dir, image_info.filename)
        os.makedirs(save_dir, exist_ok=True)
        
        try:
            # 使用Playwright页面的会话来下载，包含cookies和headers
            response = await self.page.request.get(image_info.url)
            
            if response.status == 200:
                content = await response.body()
                with open(save_path, 'wb') as f:
                    f.write(content)
                self.stats['total_size'] += len(content)
                self.log_info(f"✅ 下载成功: {image_info.filename}")
                return True
            else:
                self.log_error(f"下载失败 ({response.status}): {image_info.url}")
                return False
                
        except Exception as e:
            self.log_error(f"下载异常: {image_info.url}", e)
            return False

    async def cleanup(self):
        try:
            if self.page: await self.page.close()
            if self.context: await self.context.close()
            if self.browser: await self.browser.close()
            if self.playwright: await self.playwright.stop()
            self.log_info("Playwright引擎清理成功")
        except Exception as e:
            self.log_error("Playwright引擎清理失败", e)
    
    def get_stats(self) -> Dict:
        return self.stats

    def log_info(self, message: str):
        print(f"ℹ️  [Playwright] {message}")

    def log_error(self, message: str, exception: Exception = None):
        if exception:
            print(f"❌ [Playwright] {message}: {exception}")
        else:
            print(f"❌ [Playwright] {message}") 