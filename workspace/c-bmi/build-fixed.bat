@echo off
call "D:\Microsoft Visual Studio main\VC\Auxiliary\Build\vcvars64.bat" >nul 2>&1
cd /d "C:\Users\BossYu\Documents\deepseek-harness\default-workspace\c-bmi"
cl /nologo /utf-8 /W4 bmi_fixed.c
