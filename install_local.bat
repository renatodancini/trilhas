@echo off
chcp 65001 >nul
echo 🚀 Instalador de Dependências - Windows
echo ======================================
echo.

REM Verificar se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python não encontrado!
    echo Instale o Python primeiro: https://python.org
    echo.
    pause
    exit /b 1
)

echo ✅ Python encontrado
python --version

REM Verificar se pip está disponível
pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip não encontrado!
    echo.
    pause
    exit /b 1
)

echo ✅ pip encontrado
echo.

REM Criar ambiente virtual se não existir
if not exist "venv" (
    echo 📦 Criando ambiente virtual...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ Falha ao criar ambiente virtual
        echo.
        pause
        exit /b 1
    )
    echo ✅ Ambiente virtual criado
) else (
    echo ✅ Ambiente virtual já existe
)

echo.

REM Ativar ambiente virtual
echo 🔧 Ativando ambiente virtual...
call venv\Scripts\activate

REM Instalar dependências
echo 📚 Instalando dependências...
echo.

pip install streamlit>=1.47.0
if errorlevel 1 (
    echo ❌ Falha ao instalar streamlit
    pause
    exit /b 1
)

pip install pandas>=2.3.1
if errorlevel 1 (
    echo ❌ Falha ao instalar pandas
    pause
    exit /b 1
)

pip install openpyxl>=3.1.5
if errorlevel 1 (
    echo ❌ Falha ao instalar openpyxl
    pause
    exit /b 1
)

pip install numpy>=2.3.1
if errorlevel 1 (
    echo ❌ Falha ao instalar numpy
    pause
    exit /b 1
)

pip install altair>=5.5.0
if errorlevel 1 (
    echo ❌ Falha ao instalar altair
    pause
    exit /b 1
)

pip install pydeck>=0.9.1
if errorlevel 1 (
    echo ❌ Falha ao instalar pydeck
    pause
    exit /b 1
)

echo.
echo ✅ Todas as dependências foram instaladas com sucesso!
echo.
echo 🎯 Para executar o sistema:
echo    Execute: run_local.bat
echo.
pause 