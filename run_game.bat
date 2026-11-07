@echo off
setlocal
cd /d "%~dp0"
python maze_game.py
if errorlevel 1 (
  echo.
  echo Maze Quest stopped with an error.
  pause
)
endlocal
