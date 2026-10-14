@echo off
chcp 65001 >nul
title 手机声音 -^> 电脑音箱
cd /d "%~dp0"

echo.
echo  ==================================================
echo    通过 USB 数据线，把手机声音播放到电脑
echo  ==================================================
echo.
echo  正在等待手机就绪...
echo.
echo  如果手机弹出「允许 USB 调试吗？」：
echo    勾选「一律允许使用这台计算机进行调试」，再点「允许」。
echo.
echo  运行中按 Ctrl+C 停止。
echo.

"%~dp0adb.exe" wait-for-device

echo  手机已就绪，开始传输音频...
echo.

"%~dp0scrcpy.exe" --no-video --audio-buffer=50 %*

echo.
echo  已退出，按任意键关闭窗口。
pause >nul
