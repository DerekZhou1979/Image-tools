@echo off
chcp 65001
cls

echo 🖼️ Image-tools 通用图片下载器
echo =========================

REM 检查Python是否已安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 未找到Python，请先安装Python
    pause
    exit /b 1
)

echo 📦 正在安装依赖包...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ 安装依赖失败，请检查网络连接
    pause
    exit /b 1
)

echo.
echo 🚀 开始运行图片下载器...
echo.

REM 运行下载程序
python image_downloader.py

echo.
echo ✨ 下载完成！请查看images目录中的图片文件。
pause 