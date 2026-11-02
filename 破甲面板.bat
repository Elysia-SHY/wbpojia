@echo off
chcp 65001 >nul 2>&1
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"
cd /d "%~dp0"
title WorkBuddy 破甲 面板

rem 优先用同目录打包好的 exe；面板版没有黑框，控制台版会留一个窗口显示地址
if exist "%~dp0wbpojia-panel.exe" (start "" "%~dp0wbpojia-panel.exe" & exit /b)
if exist "%~dp0wbpojia.exe" ("%~dp0wbpojia.exe" panel %* & pause & exit /b)

set "PYEXE="
if defined WBPOJIA_PYTHON set "PYEXE=%WBPOJIA_PYTHON%"
if not defined PYEXE for /f "delims=" %%P in ('where py 2^>nul') do if not defined PYEXE set "PYEXE=%%P"
if not defined PYEXE for /f "delims=" %%P in ('where python 2^>nul') do if not defined PYEXE set "PYEXE=%%P"
if not defined PYEXE for /f "delims=" %%P in ('where python3 2^>nul') do if not defined PYEXE set "PYEXE=%%P"
if not defined PYEXE (
  echo.
  echo  [!!] 同目录没有 wbpojia.exe，PATH 上也没有 Python 3.9+。
  echo.
  pause
  exit /b 1
)
"%PYEXE%" "%~dp0wbpojia.py" panel %*
echo.
pause
