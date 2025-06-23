#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Image-tools v4.0 引擎测试模块
用于测试各个爬取引擎的功能和性能
"""

import asyncio
import time
import json
from pathlib import Path
from typing import Dict, List

# 导入引擎
try:
    from engines.legacy_engine import LegacyImageEngine
    from engines.playwright_engine import PlaywrightImageEngine
    from engines.base_engine import ImageInfo
    ENGINES_AVAILABLE = True
except ImportError as e:
    ENGINES_AVAILABLE = False
    print(f"❌ 引擎导入失败: {e}")


class EngineTestSuite:
    """引擎测试套件"""
    
    def __init__(self, config_path: str = "image_download_config.json"):
        self.config_path = config_path
        self.test_results = {}
        
        # 加载配置
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except Exception as e:
            print(f"❌ 配置文件加载失败: {e}")
            self.config = {}
    
    def run_all_tests(self, test_url: str = None) -> Dict:
        """运行所有引擎测试"""
        print("🧪 开始引擎测试套件...")
        print("=" * 60)
        
        test_url = test_url or self.config.get("base_url", "https://www.chrono24.cn/")
        
        # 测试Legacy引擎
        self.test_legacy_engine(test_url)
        
        # 测试Playwright引擎
        asyncio.run(self.test_playwright_engine(test_url))
        
        # 性能对比
        self.compare_engines()
        
        # 保存测试结果
        self.save_test_results()
        
        print("=" * 60)
        print("🏁 引擎测试完成")
        
        return self.test_results
    
    def test_legacy_engine(self, test_url: str):
        """测试Legacy引擎"""
        print("🔧 测试Legacy引擎...")
        
        start_time = time.time()
        
        try:
            engine = LegacyImageEngine(self.config)
            
            # 测试页面获取
            print(f"📄 获取页面: {test_url}")
            html_content = engine.fetch_page(test_url)
            
            if html_content:
                # 测试图片提取
                print("🖼️  提取图片URL...")
                images = engine.extract_image_urls(html_content, test_url)
                
                # 记录结果
                elapsed_time = time.time() - start_time
                self.test_results["legacy"] = {
                    "status": "success",
                    "page_fetch": True,
                    "images_found": len(images),
                    "execution_time": elapsed_time,
                    "images": [
                        {
                            "url": img.url,
                            "alt_text": img.alt_text,
                            "category": img.category
                        } 
                        for img in images[:5]  # 只保存前5个作为示例
                    ]
                }
                
                print(f"✅ Legacy引擎测试成功")
                print(f"   - 找到图片: {len(images)}张")
                print(f"   - 执行时间: {elapsed_time:.2f}秒")
                
            else:
                self.test_results["legacy"] = {
                    "status": "failed",
                    "error": "页面获取失败",
                    "execution_time": time.time() - start_time
                }
                print("❌ Legacy引擎: 页面获取失败")
                
        except Exception as e:
            self.test_results["legacy"] = {
                "status": "error",
                "error": str(e),
                "execution_time": time.time() - start_time
            }
            print(f"❌ Legacy引擎测试失败: {e}")
        
        print()
    
    async def test_playwright_engine(self, test_url: str):
        """测试Playwright引擎"""
        print("🎭 测试Playwright引擎...")
        
        start_time = time.time()
        
        try:
            # 检查Playwright是否可用
            try:
                from playwright.async_api import async_playwright
            except ImportError:
                self.test_results["playwright"] = {
                    "status": "not_available",
                    "error": "Playwright未安装"
                }
                print("⚠️  Playwright引擎: 未安装，跳过测试")
                return
            
            engine = PlaywrightImageEngine(self.config)
            
            # 测试浏览器初始化
            print("🌐 启动浏览器...")
            await engine.initialize()
            
            # 测试页面导航
            print(f"📄 导航到页面: {test_url}")
            page_content = await engine.fetch_page(test_url)
            
            if page_content:
                # 测试图片提取
                print("🖼️  提取图片URL...")
                images = await engine.extract_image_urls(page_content, test_url)
                
                # 关闭浏览器
                await engine.cleanup()
                
                # 记录结果
                elapsed_time = time.time() - start_time
                self.test_results["playwright"] = {
                    "status": "success",
                    "page_fetch": True,
                    "images_found": len(images),
                    "execution_time": elapsed_time,
                    "images": [
                        {
                            "url": img.url,
                            "alt_text": img.alt_text,
                            "category": img.category
                        } 
                        for img in images[:5]  # 只保存前5个作为示例
                    ]
                }
                
                print(f"✅ Playwright引擎测试成功")
                print(f"   - 找到图片: {len(images)}张")
                print(f"   - 执行时间: {elapsed_time:.2f}秒")
                
            else:
                await engine.cleanup()
                self.test_results["playwright"] = {
                    "status": "failed",
                    "error": "页面获取失败",
                    "execution_time": time.time() - start_time
                }
                print("❌ Playwright引擎: 页面获取失败")
                
        except Exception as e:
            self.test_results["playwright"] = {
                "status": "error",
                "error": str(e),
                "execution_time": time.time() - start_time
            }
            print(f"❌ Playwright引擎测试失败: {e}")
        
        print()
    
    def compare_engines(self):
        """对比引擎性能"""
        print("📊 引擎性能对比:")
        print("-" * 40)
        
        for engine_name, results in self.test_results.items():
            if results.get("status") == "success":
                images_count = results.get("images_found", 0)
                exec_time = results.get("execution_time", 0)
                
                print(f"{engine_name.title()}引擎:")
                print(f"  - 图片数量: {images_count}")
                print(f"  - 执行时间: {exec_time:.2f}秒")
                print(f"  - 效率: {images_count/exec_time:.1f} 图片/秒")
                print()
            elif results.get("status") in ["failed", "error"]:
                print(f"{engine_name.title()}引擎: ❌ {results.get('error', '测试失败')}")
                print()
            else:
                print(f"{engine_name.title()}引擎: ⚠️  不可用")
                print()
    
    def save_test_results(self):
        """保存测试结果"""
        output_path = Path("test_results.json")
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.test_results, f, ensure_ascii=False, indent=2)
            print(f"📋 测试结果已保存到: {output_path}")
        except Exception as e:
            print(f"❌ 保存测试结果失败: {e}")


def main():
    """主函数"""
    if not ENGINES_AVAILABLE:
        print("❌ 引擎模块不可用，请检查项目结构")
        return
    
    # 创建测试套件
    test_suite = EngineTestSuite()
    
    # 运行测试
    results = test_suite.run_all_tests()
    
    # 输出总结
    successful_engines = [
        name for name, result in results.items() 
        if result.get("status") == "success"
    ]
    
    print(f"\n🎯 测试总结:")
    print(f"   - 可用引擎: {len(successful_engines)}/{len(results)}")
    print(f"   - 成功引擎: {', '.join(successful_engines)}")
    
    if not successful_engines:
        print("⚠️  警告: 没有可用的引擎，请检查依赖安装")
    
    return results


if __name__ == "__main__":
    main() 