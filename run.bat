@echo off
chcp 65001 >nul
cd /d "%~dp0"

:: Force window positioning and disable high DPI scaling
set SDL_VIDEO_WINDOW_POS=100,100
set SDL_VIDEO_CENTERED=1
set SDL_VIDEO_HIGHDPI_DISABLED=1

:: Launch the game
call .venv\Scripts\python.exe main.py

pause
