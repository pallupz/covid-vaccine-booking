@echo off
REM This script is automatically executed on console start
Title Portable Python 3.8.9 Console
REM PRINT python --version
python -c "import sys; print('Python' + sys.version)"
doskey pip=python -m pip $*
REM Add Scripts Path
REM SET PATH=%PYTHONPATH%\Scripts;%PATH%