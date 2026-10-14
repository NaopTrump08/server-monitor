@echo off
chcp 65001 >nul
title 检查手机连接状态
cd /d "%~dp0"

echo.
echo  正在检测通过 USB 连接的设备...
echo.

"%~dp0adb.exe" devices -l

echo.
echo  --------------------------------------------------
echo   device        = 正常，可以运行「1-播放手机声音.bat」
echo   unauthorized  = 手机屏幕上点「允许 USB 调试」（勾选始终允许）
echo   offline       = 拔插一次数据线，或重启 adb
echo   列表为空      = 数据线是纯充电线 / USB 口问题 / 缺驱动
echo  --------------------------------------------------
pause
