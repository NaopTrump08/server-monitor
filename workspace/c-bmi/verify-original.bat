@echo off
call "D:\Microsoft Visual Studio main\VC\Auxiliary\Build\vcvars64.bat" >nul 2>&1
cd /d "C:\Users\BossYu\Documents\deepseek-harness\default-workspace\c-bmi"
echo ===== COMPILE original.c (cl /W4) =====
cl /nologo /W4 original.c
echo [compile exit code = %ERRORLEVEL%]
echo.
echo ===== RUN: Alice / 20 / 70 / 175 =====
original.exe < inA.txt
echo [run exit code = %ERRORLEVEL%]
