#!/bin/bash

echo "====================================="
echo "   Instalador - Projeto Trilhas"
echo "====================================="
echo ""

# Verificar se o Python 3 está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado. Por favor, instale o Python 3 primeiro."
    exit 1
fi

echo "✅ Python 3 encontrado: $(python3 --version)"

# Verificar se o pip está instalado
if ! command -v pip &> /dev/null; then
    echo "⚠️  pip não encontrado. Tentando instalar..."
    sudo apt update
    sudo apt install -y python3-pip
fi

echo "✅ pip encontrado: $(pip --version)"

# Instalar python3-venv se necessário
echo "📦 Verificando python3-venv..."
if ! python3 -c "import venv" &> /dev/null; then
    echo "⚠️  python3-venv não encontrado. Instalando..."
    sudo apt update
    sudo apt install -y python3-venv
fi

echo "✅ python3-venv disponível"

# Criar ambiente virtual
echo "🔧 Criando ambiente virtual..."
if [ -d "venv_linux" ]; then
    echo "⚠️  Ambiente virtual já existe. Removendo o antigo..."
    rm -rf venv_linux
fi

python3 -m venv venv_linux

# Ativar ambiente virtual e instalar dependências
echo "📦 Instalando dependências..."
source venv_linux/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "✅ Instalação concluída com sucesso!"
echo ""
echo "Para executar o projeto:"
echo "1. Ative o ambiente virtual: source venv_linux/bin/activate"
echo "2. Execute o aplicativo: streamlit run app.py"
echo ""
echo "====================================="