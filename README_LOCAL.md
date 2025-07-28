# 🚀 Sistema de Impressão de Trilhas - Execução Local

Este documento contém instruções para executar o sistema localmente.

## 📋 Pré-requisitos

- **Python 3.8 ou superior**
- **Git** (para clonar o repositório)
- **Navegador web** (Chrome, Firefox, Edge, etc.)

## 🔧 Instalação

### Windows

1. **Clone o repositório** (se ainda não fez):
   ```bash
   git clone https://github.com/renatodancini/trilhas.git
   cd trilhas
   ```

2. **Execute o instalador**:
   - Duplo clique em `install_local.bat`
   - Ou execute no terminal: `install_local.bat`

3. **Aguarde a instalação**:
   - O script criará um ambiente virtual
   - Instalará todas as dependências necessárias
   - Aguarde até ver "✅ Todas as dependências foram instaladas com sucesso!"

### Linux/Mac

1. **Clone o repositório** (se ainda não fez):
   ```bash
   git clone https://github.com/renatodancini/trilhas.git
   cd trilhas
   ```

2. **Execute o instalador**:
   ```bash
   python install_requirements.py
   ```

3. **Aguarde a instalação**:
   - O script criará um ambiente virtual
   - Instalará todas as dependências necessárias

## 🎯 Execução

### Windows

**Opção 1 - Script automático:**
- Duplo clique em `run_local.bat`

**Opção 2 - Terminal:**
```bash
run_local.bat
```

### Linux/Mac

```bash
python run_local.py
```

## 🌐 Acesso ao Sistema

Após executar o script:

1. **O navegador abrirá automaticamente**
2. **URL local**: http://localhost:8501
3. **Se não abrir automaticamente**, copie e cole a URL no navegador

## ⏹️ Parando o Sistema

- **No terminal**: Pressione `Ctrl+C`
- **No Windows**: Feche a janela do terminal

## 🔍 Solução de Problemas

### Erro: "Python não encontrado"
- **Solução**: Instale o Python em https://python.org
- **Importante**: Marque "Add Python to PATH" durante a instalação

### Erro: "pip não encontrado"
- **Solução**: Reinstale o Python com a opção "Add Python to PATH"

### Erro: "Ambiente virtual não encontrado"
- **Solução**: Execute novamente `install_local.bat` ou `python install_requirements.py`

### Erro: "Porta 8501 já em uso"
- **Solução**: 
  1. Pare outros processos Streamlit
  2. Ou aguarde alguns segundos e tente novamente

### Erro: "Dependências não instaladas"
- **Solução**: 
  1. Delete a pasta `venv`
  2. Execute novamente o instalador

## 📁 Estrutura de Arquivos

```
trilhas/
├── app.py                    # Aplicação principal
├── requirements.txt          # Dependências
├── install_local.bat         # Instalador Windows
├── install_requirements.py   # Instalador Python
├── run_local.bat            # Executor Windows
├── run_local.py             # Executor Python
├── venv/                    # Ambiente virtual (criado automaticamente)
└── ...                      # Outros arquivos do sistema
```

## 🆘 Suporte

Se encontrar problemas:

1. **Verifique os pré-requisitos**
2. **Execute o instalador novamente**
3. **Verifique se não há outros processos usando a porta 8501**
4. **Consulte os logs no terminal para mais detalhes**

## 🔄 Atualizações

Para atualizar o sistema:

1. **Pare o sistema** (Ctrl+C)
2. **Atualize o código**:
   ```bash
   git pull origin master
   ```
3. **Reinstale as dependências** (se necessário):
   ```bash
   install_local.bat  # Windows
   python install_requirements.py  # Linux/Mac
   ```
4. **Execute novamente**:
   ```bash
   run_local.bat  # Windows
   python run_local.py  # Linux/Mac
   ``` 