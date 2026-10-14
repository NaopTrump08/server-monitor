@echo off
chcp 65001 >nul
title 手机画面 + 声音 投到电脑
cd /d "%~dp0"

echo.
echo  投屏 + 音频，鼠标键盘也能反向控制手机。
echo  运行中按 Ctrl+C 可以停止。
echo.

"%~dp0scrcpy.exe" --audio-buffer=50 %*

pause
