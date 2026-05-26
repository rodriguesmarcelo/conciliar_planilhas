@echo off
REM Inicia a plataforma barelli.automacao (FastAPI + SPA) na intranet.
cd /d "%~dp0"
if exist ".venv\Scripts\activate.bat" (
    call ".venv\Scripts\activate.bat"
) else (
    echo [aviso] .venv nao encontrado; usando o python do sistema.
)
python run_web.py
pause
