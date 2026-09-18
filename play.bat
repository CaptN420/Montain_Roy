@echo off
chcp 65001 >nul
cd /d "%~dp0"

:: Set environment variables for better display
set SDL_VIDEO_HIGHDPI_DISABLED=1
set SDL_VIDEO_WINDOW_POS=100,100

:: Launch the game
call .venv\Scripts\python.exe main.py

pause
