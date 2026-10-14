@echo off
call "D:\Microsoft Visual Studio main\VC\Auxiliary\Build\vcvars64.bat" >nul 2>&1
cd /d "C:\Users\BossYu\Documents\deepseek-harness\default-workspace\c-bmi"
echo ===== COMPILE (cl /utf-8 /W4) =====
cl /nologo /utf-8 /W4 bmi_fixed.c
if errorlevel 1 goto :eof
echo.
echo ===== A: Alice / 20 / 70 / 175 =====
bmi_fixed.exe < inA.txt
echo.
echo ===== B: "Bob 20" / 70 / 175  [name and age on the same line] =====
bmi_fixed.exe < inB.txt
echo.
echo ===== C: Cara / abc / 70 / 175  [age not a number] =====
bmi_fixed.exe < inC.txt
echo.
echo ===== D: Dan / abc / 30 / 80 / 180  [bad then good values] =====
bmi_fixed.exe < inD.txt
echo.
echo ===== E: Fay / 20 / 70 / 0  [height = 0] =====
bmi_fixed.exe < inE.txt
