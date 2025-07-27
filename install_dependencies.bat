@echo off
echo Instalando dependencias do projeto...
echo.

echo Instalando openpyxl...
pip install openpyxl>=3.1.5

echo.
echo Instalando pandas...
pip install pandas>=2.3.1

echo.
echo Instalando streamlit...
pip install streamlit>=1.47.0

echo.
echo Instalando outras dependencias...
pip install numpy>=2.3.1
pip install altair>=5.5.0
pip install pydeck>=0.9.1

echo.
echo Todas as dependencias foram instaladas!
echo.
pause 