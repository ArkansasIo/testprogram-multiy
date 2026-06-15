@echo off
echo ========================================
echo IDE Compiler Manager - Setup
echo ========================================
echo.

echo Installing dependencies...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo To start the IDE, run:
echo   python main.py
echo.
echo Or use CLI mode:
echo   python src/cli.py --help
echo.
pause

@REM Made with Bob
