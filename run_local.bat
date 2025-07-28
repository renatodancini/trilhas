@echo off
chcp 65001 >nul
echo 🚀 Sistema de Impressão de Trilhas - Windows
echo ===========================================
echo.

REM Verificar se o ambiente virtual existe
if not exist "venv" (
    echo ❌ Ambiente virtual não encontrado!
    echo Execute primeiro: python install_requirements.py
    echo.
    pause
    exit /b 1
)

REM Verificar se o arquivo app.py existe
if not exist "app.py" (
    echo ❌ Arquivo app.py não encontrado!
    echo.
    pause
    exit /b 1
)

echo 🌐 Iniciando o sistema...
echo 📱 O sistema estará disponível em: http://localhost:8501
echo ⏹️  Para parar o servidor, pressione Ctrl+C
echo.

REM Ativar ambiente virtual e executar Streamlit
call venv\Scripts\activate
streamlit run app.py

echo.
echo 👋 Sistema encerrado.
pause 