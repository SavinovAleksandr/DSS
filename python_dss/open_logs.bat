@echo off
REM Скрипт для открытия директории с логами StabLimit на Windows

python show_logs_path.py

echo.
echo Нажмите любую клавишу для открытия директории с логами...
pause >nul

python -c "import sys; from pathlib import Path; sys.path.insert(0, '.'); from utils.config import config; import os; log_dir = config.get_path('paths.logs_dir'); os.startfile(str(log_dir.absolute()))"

