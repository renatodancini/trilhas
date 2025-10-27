# Projeto Trilhas

Sistema de gestão e impressão de trilhas desenvolvido em Python com Streamlit.

## 📋 Requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

## 🚀 Instalação

### Windows

1. Certifique-se de ter o Python instalado
2. Execute o script de instalação:
   ```bash
   install_dependencies.bat
   ```

### Linux/Ubuntu

1. Certifique-se de ter o Python 3 instalado
2. Execute o script de instalação:
   ```bash
   ./install_linux.sh
   ```
   
   Ou execute manualmente:
   ```bash
   # Instalar dependências do sistema
   sudo apt update
   sudo apt install python3-venv python3-pip
   
   # Criar ambiente virtual
   python3 -m venv venv_linux
   
   # Ativar ambiente virtual
   source venv_linux/bin/activate
   
   # Instalar dependências Python
   pip install -r requirements.txt
   ```

### Instalação Manual

Se os scripts automáticos não funcionarem, você pode instalar manualmente:

1. Clone o repositório:
   ```bash
   git clone https://github.com/renatodancini/trilhas.git
   cd trilhas
   ```

2. Crie um ambiente virtual:
   ```bash
   python -m venv venv
   ```

3. Ative o ambiente virtual:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`

4. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

## 🎯 Como Executar

### Windows
```bash
# Ativar ambiente virtual
venv\Scripts\activate

# Executar aplicação
streamlit run app.py
```

### Linux
```bash
# Ativar ambiente virtual
source venv_linux/bin/activate

# Executar aplicação
streamlit run app.py
```

## 📦 Dependências

- streamlit>=1.47.0
- pandas>=2.3.1
- openpyxl>=3.1.5
- numpy>=2.3.1
- altair>=5.5.0
- pydeck>=0.9.1

## 🔧 Resolução de Problemas

### Erro "externally-managed-environment"

Se você receber este erro ao tentar instalar as dependências, significa que você está em um sistema Linux com gerenciamento externo de pacotes Python. Use um ambiente virtual:

```bash
python3 -m venv venv_linux
source venv_linux/bin/activate
pip install -r requirements.txt
```

### Erro com sqlite3

O `sqlite3` é uma biblioteca padrão do Python e não deve estar no requirements.txt. Se você encontrar erros relacionados, certifique-se de que o requirements.txt não inclui esta dependência.

## 🤝 Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 👨‍💻 Autor

Renato Dancini - [GitHub](https://github.com/renatodancini)