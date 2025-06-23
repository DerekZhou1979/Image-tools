#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Image-tools v4.0 健康检查模块
检查系统环境、依赖包、网络连接等状态
"""

import sys
import subprocess
import importlib
import requests
import json
import platform
from pathlib import Path
from typing import Dict, List, Tuple, Optional

class HealthChecker:
    """系统健康检查器"""
    
    def __init__(self):
        self.results = {
            "system": {},
            "python": {},
            "dependencies": {},
            "network": {},
            "engines": {},
            "overall": "unknown"
        }
    
    def check_all(self, verbose: bool = True) -> Dict:
        """执行完整的健康检查"""
        if verbose:
            print("🔍 开始系统健康检查...")
            print("=" * 50)
        
        # 检查系统信息
        self.check_system_info(verbose)
        
        # 检查Python环境
        self.check_python_environment(verbose)
        
        # 检查依赖包
        self.check_dependencies(verbose)
        
        # 检查网络连接
        self.check_network_connectivity(verbose)
        
        # 检查爬取引擎
        self.check_engines(verbose)
        
        # 计算总体状态
        self.calculate_overall_status(verbose)
        
        if verbose:
            print("=" * 50)
            print(f"🏁 健康检查完成，总体状态: {self.get_status_emoji(self.results['overall'])} {self.results['overall'].upper()}")
        
        return self.results
    
    def check_system_info(self, verbose: bool = True):
        """检查系统信息"""
        try:
            self.results["system"] = {
                "platform": platform.system(),
                "platform_version": platform.version(),
                "architecture": platform.machine(),
                "python_version": sys.version,
                "status": "healthy"
            }
            
            if verbose:
                print(f"💻 系统: {self.results['system']['platform']} {self.results['system']['architecture']}")
                print(f"🐍 Python: {sys.version.split()[0]}")
                
        except Exception as e:
            self.results["system"]["status"] = "error"
            self.results["system"]["error"] = str(e)
            if verbose:
                print(f"❌ 系统信息检查失败: {e}")
    
    def check_python_environment(self, verbose: bool = True):
        """检查Python环境"""
        try:
            version_info = sys.version_info
            is_compatible = version_info.major >= 3 and version_info.minor >= 6
            
            self.results["python"] = {
                "version": f"{version_info.major}.{version_info.minor}.{version_info.micro}",
                "executable": sys.executable,
                "compatible": is_compatible,
                "status": "healthy" if is_compatible else "warning"
            }
            
            if verbose:
                status_emoji = "✅" if is_compatible else "⚠️"
                print(f"{status_emoji} Python版本: {self.results['python']['version']} {'(兼容)' if is_compatible else '(需要3.6+)'}")
                
        except Exception as e:
            self.results["python"]["status"] = "error"
            self.results["python"]["error"] = str(e)
            if verbose:
                print(f"❌ Python环境检查失败: {e}")
    
    def check_dependencies(self, verbose: bool = True):
        """检查依赖包"""
        required_packages = {
            "requests": "HTTP客户端",
            "beautifulsoup4": "HTML解析器",
            "pillow": "图片处理",
            "google-generativeai": "Gemini AI (可选)",
            "playwright": "浏览器自动化 (可选)"
        }
        
        self.results["dependencies"] = {}
        missing_critical = []
        missing_optional = []
        
        for package, description in required_packages.items():
            try:
                if package == "beautifulsoup4":
                    importlib.import_module("bs4")
                elif package == "pillow":
                    importlib.import_module("PIL")
                elif package == "google-generativeai":
                    importlib.import_module("google.generativeai")
                else:
                    importlib.import_module(package.replace("-", "_"))
                
                self.results["dependencies"][package] = {
                    "status": "installed",
                    "description": description
                }
                
                if verbose:
                    print(f"✅ {package}: {description}")
                    
            except ImportError:
                self.results["dependencies"][package] = {
                    "status": "missing",
                    "description": description
                }
                
                if package in ["google-generativeai", "playwright"]:
                    missing_optional.append(package)
                    if verbose:
                        print(f"⚠️  {package}: {description} (可选)")
                else:
                    missing_critical.append(package)
                    if verbose:
                        print(f"❌ {package}: {description} (必需)")
        
        # 设置依赖检查的总体状态
        if missing_critical:
            self.results["dependencies"]["overall_status"] = "error"
        elif missing_optional:
            self.results["dependencies"]["overall_status"] = "warning"
        else:
            self.results["dependencies"]["overall_status"] = "healthy"
    
    def check_network_connectivity(self, verbose: bool = True):
        """检查网络连接"""
        test_urls = [
            ("https://www.google.com", "Google"),
            ("https://www.chrono24.cn", "目标网站"),
            ("https://ipapi.co/json", "地理位置API"),
            ("https://generativelanguage.googleapis.com", "Gemini API")
        ]
        
        self.results["network"] = {"tests": {}}
        successful_tests = 0
        
        for url, name in test_urls:
            try:
                response = requests.get(url, timeout=5)
                success = response.status_code == 200
                
                self.results["network"]["tests"][name] = {
                    "url": url,
                    "status_code": response.status_code,
                    "success": success,
                    "response_time": response.elapsed.total_seconds()
                }
                
                if success:
                    successful_tests += 1
                
                if verbose:
                    emoji = "✅" if success else "❌"
                    print(f"{emoji} {name}: {response.status_code} ({response.elapsed.total_seconds():.2f}s)")
                    
            except Exception as e:
                self.results["network"]["tests"][name] = {
                    "url": url,
                    "success": False,
                    "error": str(e)
                }
                
                if verbose:
                    print(f"❌ {name}: 连接失败 ({e})")
        
        # 设置网络检查的总体状态
        if successful_tests == len(test_urls):
            self.results["network"]["overall_status"] = "healthy"
        elif successful_tests >= len(test_urls) // 2:
            self.results["network"]["overall_status"] = "warning"
        else:
            self.results["network"]["overall_status"] = "error"
    
    def check_engines(self, verbose: bool = True):
        """检查爬取引擎状态"""
        self.results["engines"] = {}
        
        # 检查Legacy引擎
        try:
            from engines.legacy_engine import LegacyImageEngine
            self.results["engines"]["legacy"] = {
                "available": True,
                "status": "healthy",
                "description": "传统HTTP爬取引擎"
            }
            if verbose:
                print("✅ Legacy引擎: 可用")
        except Exception as e:
            self.results["engines"]["legacy"] = {
                "available": False,
                "status": "error",
                "error": str(e)
            }
            if verbose:
                print(f"❌ Legacy引擎: 不可用 ({e})")
        
        # 检查Playwright引擎
        try:
            from engines.playwright_engine import PlaywrightImageEngine
            # 尝试检查Playwright浏览器是否已安装
            try:
                result = subprocess.run(
                    [sys.executable, "-m", "playwright", "install", "--dry-run"], 
                    capture_output=True, 
                    text=True, 
                    timeout=10
                )
                browsers_installed = "chromium" in result.stdout.lower()
            except:
                browsers_installed = False
            
            self.results["engines"]["playwright"] = {
                "available": True,
                "browsers_installed": browsers_installed,
                "status": "healthy" if browsers_installed else "warning",
                "description": "浏览器自动化引擎"
            }
            
            if verbose:
                emoji = "✅" if browsers_installed else "⚠️"
                status = "可用" if browsers_installed else "需要安装浏览器"
                print(f"{emoji} Playwright引擎: {status}")
                
        except Exception as e:
            self.results["engines"]["playwright"] = {
                "available": False,
                "status": "error",
                "error": str(e)
            }
            if verbose:
                print(f"❌ Playwright引擎: 不可用 ({e})")
    
    def calculate_overall_status(self, verbose: bool = True):
        """计算总体健康状态"""
        error_count = 0
        warning_count = 0
        
        # 检查各个组件的状态
        for component in ["system", "python", "dependencies", "network", "engines"]:
            if component in self.results:
                if component == "dependencies" or component == "network":
                    status = self.results[component].get("overall_status", "unknown")
                elif component == "engines":
                    # 检查是否至少有一个引擎可用
                    legacy_ok = self.results[component].get("legacy", {}).get("available", False)
                    playwright_ok = self.results[component].get("playwright", {}).get("available", False)
                    
                    if legacy_ok or playwright_ok:
                        status = "healthy"
                    else:
                        status = "error"
                else:
                    status = self.results[component].get("status", "unknown")
                
                if status == "error":
                    error_count += 1
                elif status == "warning":
                    warning_count += 1
        
        # 确定总体状态
        if error_count > 0:
            self.results["overall"] = "error"
        elif warning_count > 0:
            self.results["overall"] = "warning"
        else:
            self.results["overall"] = "healthy"
    
    def get_status_emoji(self, status: str) -> str:
        """获取状态对应的emoji"""
        emoji_map = {
            "healthy": "✅",
            "warning": "⚠️",
            "error": "❌",
            "unknown": "❓"
        }
        return emoji_map.get(status, "❓")
    
    def generate_report(self) -> str:
        """生成详细的健康检查报告"""
        report = []
        report.append("🏥 Image-tools v4.0 健康检查报告")
        report.append("=" * 50)
        
        # 总体状态
        overall_emoji = self.get_status_emoji(self.results["overall"])
        report.append(f"📊 总体状态: {overall_emoji} {self.results['overall'].upper()}")
        report.append("")
        
        # 系统信息
        if "system" in self.results:
            report.append("💻 系统信息:")
            sys_info = self.results["system"]
            report.append(f"   - 平台: {sys_info.get('platform', 'Unknown')}")
            report.append(f"   - 架构: {sys_info.get('architecture', 'Unknown')}")
            report.append(f"   - Python: {self.results.get('python', {}).get('version', 'Unknown')}")
            report.append("")
        
        # 依赖状态
        if "dependencies" in self.results:
            report.append("📦 依赖包状态:")
            for pkg, info in self.results["dependencies"].items():
                if pkg != "overall_status":
                    emoji = "✅" if info["status"] == "installed" else "❌"
                    report.append(f"   {emoji} {pkg}: {info['description']}")
            report.append("")
        
        # 引擎状态
        if "engines" in self.results:
            report.append("🚀 爬取引擎状态:")
            for engine, info in self.results["engines"].items():
                emoji = self.get_status_emoji(info["status"])
                report.append(f"   {emoji} {engine.title()}引擎: {info['description']}")
            report.append("")
        
        # 网络状态
        if "network" in self.results and "tests" in self.results["network"]:
            report.append("🌐 网络连接状态:")
            for name, test in self.results["network"]["tests"].items():
                emoji = "✅" if test["success"] else "❌"
                if test["success"]:
                    report.append(f"   {emoji} {name}: {test['status_code']} ({test['response_time']:.2f}s)")
                else:
                    report.append(f"   {emoji} {name}: 连接失败 ({test['error']})") 