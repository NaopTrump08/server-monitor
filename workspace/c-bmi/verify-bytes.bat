@echo off
call "D:\Microsoft Visual Studio main\VC\Auxiliary\Build\vcvars64.bat" >nul 2>&1
cd /d "C:\Users\BossYu\Documents\deepseek-harness\default-workspace\c-bmi"
echo ===== A) EXACT bytes as you sent (contains U+00A0), default code page =====
cl /nologo /W4 user_bytes.c
echo [exit code = %ERRORLEVEL%]
echo.
echo ===== B) EXACT bytes as you sent, with /utf-8 =====
cl /nologo /utf-8 /W4 user_bytes.c
echo [exit code = %ERRORLEVEL%]
echo.
echo ===== C) only NBSP replaced by normal spaces, with /utf-8 =====
cl /nologo /utf-8 /W4 user_fixed_spaces.c
echo [exit code = %ERRORLEVEL%]
