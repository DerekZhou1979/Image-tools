@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: Image-tools v4.0 Windows启动脚本

echo.
echo 🖼️  Image-tools v4.0 - 智能图片下载器
echo ======================================

:: 检查Python环境
echo ℹ️  检查Python环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 未找到Python，请先安装Python 3.6+
    pause
    exit /b 1
)

:: 检查项目结构
echo ℹ️  检查项目结构...
if not exist "engines\" (
    echo ❌ 缺少必要目录: engines
    pause
    exit /b 1
)

if not exist "utils\" (
    echo ❌ 缺少必要目录: utils
    pause
    exit /b 1
)

if not exist "image_downloader.py" (
    echo ❌ 主程序文件不存在: image_downloader.py
    pause
    exit /b 1
)

:: 安装依赖
echo ℹ️  检查并安装Python依赖...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

:: 检查Playwright
echo ℹ️  检查Playwright浏览器...
python -c "import playwright" >nul 2>&1
if %errorlevel% equ 0 (
    echo ℹ️  安装Playwright浏览器驱动...
    python -m playwright install chromium
    echo ✅ Playwright浏览器驱动已更新
) else (
    echo ⚠️  Playwright未安装，将使用传统引擎
)

:: 解析参数
set MODE=all
if "%1" neq "" set MODE=%1

:: 设置API密钥（如果需要）
if "%MODE%"=="gemini" (
    if "%GEMINI_API_KEY%"=="" (
        echo ⚠️  未配置Gemini API密钥
        echo 💡 请设置环境变量: set GEMINI_API_KEY=your_key_here
        echo 获取API密钥: https://makersuite.google.com/app/apikey
    )
)

echo.
echo ℹ️  启动模式: %MODE%
echo.

:: 运行主程序
if "%MODE%"=="all" (
    python image_downloader.py
) else if "%MODE%"=="match" (
    python image_downloader.py --match
) else if "%MODE%"=="manual" (
    python image_downloader.py --manual
) else if "%MODE%"=="rename" (
    python image_downloader.py --rename
) else if "%MODE%"=="gemini" (
    python image_downloader.py --gemini
) else if "%MODE%"=="legacy" (
    python image_downloader.py --legacy
) else (
    echo ❌ 不支持的模式: %MODE%
    echo.
    echo 支持的模式:
    echo   all      - 下载所有图片 ^(默认^)
    echo   match    - 智能匹配模式
    echo   manual   - 手动选择模式
    echo   rename   - 基础智能重命名
    echo   gemini   - Gemini AI智能重命名
    echo   legacy   - 强制使用传统引擎
    pause
    exit /b 1
)

echo.
echo ✅ 任务执行完成！
echo ℹ️  图片保存在 .\images\ 目录中
pause 