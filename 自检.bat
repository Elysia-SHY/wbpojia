@echo off
chcp 65001 >nul 2>&1
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"
cd /d "%~dp0"
title WorkBuddy 破甲 自检

rem 同目录有打包好的 exe 就直接用它，不需要装 Python
if exist "%~dp0wbpojia.exe" (
  "%~dp0wbpojia.exe" doctor %*
  echo.
  pause
  exit /b
)

set "PYEXE="
if defined WBPOJIA_PYTHON set "PYEXE=%WBPOJIA_PYTHON%"
if not defined PYEXE for /f "delims=" %%P in ('where py 2^>nul') do if not defined PYEXE set "PYEXE=%%P"
if not defined PYEXE for /f "delims=" %%P in ('where python 2^>nul') do if not defined PYEXE set "PYEXE=%%P"
if not defined PYEXE for /f "delims=" %%P in ('where python3 2^>nul') do if not defined PYEXE set "PYEXE=%%P"
if not defined PYEXE (
  echo.
  echo  [!!] 同目录没有 wbpojia.exe，PATH 上也没有 Python 3.9+。
  echo       装 Python，或设 WBPOJIA_PYTHON 指向 python.exe。
  echo.
  pause
  exit /b 1
)
"%PYEXE%" "%~dp0wbpojia.py" doctor %*
echo.
pause
