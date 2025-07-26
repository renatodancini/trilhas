import pandas as pd
import sqlite3

USERS_FILE = 'usuarios.csv'
DB_FILE = 'login_status.db'

def inicializa_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS login_status (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE,
        nome TEXT,
        tipo TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS impressao_upload (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        colunas TEXT,
        dados TEXT
    )''')
    conn.commit()
    conn.close()

def salva_login_status(email, nome, tipo):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('DELETE FROM login_status')
    c.execute('INSERT INTO login_status (email, nome, tipo) VALUES (?, ?, ?)', (email, nome, tipo))
    conn.commit()
    conn.close()

def busca_login_status():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('SELECT email, nome, tipo FROM login_status LIMIT 1')
    row = c.fetchone()
    conn.close()
    if row:
        return {'email': row[0], 'nome': row[1], 'tipo': row[2]}
    return None

def remove_login_status():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('DELETE FROM login_status')
    conn.commit()
    conn.close()

def inicializa_usuarios():
    try:
        df = pd.read_csv(USERS_FILE)
    except (FileNotFoundError, pd.errors.EmptyDataError):
        df = pd.DataFrame(columns=['nome', 'email', 'senha', 'tipo'])
        df.to_csv(USERS_FILE, index=False)

def autentica_usuario(email, senha):
    df = pd.read_csv(USERS_FILE)
    usuario = df[(df['email'] == email) & (df['senha'] == senha)]
    if not usuario.empty:
        return True, usuario.iloc[0]['nome'], usuario.iloc[0]['tipo']
    return False, None, None

def cadastra_usuario(nome, email, senha, tipo):
    df = pd.read_csv(USERS_FILE)
    if email in df['email'].values:
        return False
    novo_usuario = pd.DataFrame([[nome, email, senha, tipo]], columns=df.columns)
    df = pd.concat([df, novo_usuario], ignore_index=True)
    df.to_csv(USERS_FILE, index=False)
    return True

def salva_impressao_upload(df):
    import json
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    colunas = list(df.columns)
    dados = df.values.tolist()
    c.execute('INSERT INTO impressao_upload (colunas, dados) VALUES (?, ?)', (json.dumps(colunas), json.dumps(dados)))
    conn.commit()
    conn.close()

def busca_impressao_upload():
    import json
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('SELECT colunas, dados FROM impressao_upload ORDER BY id DESC LIMIT 1')
    row = c.fetchone()
    conn.close()
    if row:
        colunas = json.loads(row[0])
        dados = json.loads(row[1])
        return pd.DataFrame(dados, columns=colunas)
    return None

def salva_gestao_trilhas(df):
    conn = sqlite3.connect(DB_FILE)
    df.to_sql('gestao_trilhas', conn, if_exists='replace', index=False)
    conn.close()

def busca_gestao_trilhas():
    conn = sqlite3.connect(DB_FILE)
    try:
        df = pd.read_sql_query('SELECT * FROM gestao_trilhas', conn)
    except Exception:
        df = None
    conn.close()
    return df

def limpa_gestao_trilhas():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('DROP TABLE IF EXISTS gestao_trilhas')
    conn.commit()
    conn.close()

def atualiza_status_trilha(trilha, status, impresso_por=None, data=None, hora=None, data_hora_download=None):
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query('SELECT * FROM gestao_trilhas', conn)
    idx = df[df['Trilhas'] == trilha].index
    if not idx.empty:
        df.at[idx[0], 'Status'] = status
        if impresso_por is not None:
            df.at[idx[0], 'Impresso por'] = impresso_por
        if data is not None:
            df.at[idx[0], 'Data'] = data
        if hora is not None:
            df.at[idx[0], 'Hora'] = hora
        if data_hora_download is not None:
            df.at[idx[0], 'Data/Hora'] = data_hora_download
        df.to_sql('gestao_trilhas', conn, if_exists='replace', index=False)
    conn.close()

def limpa_coluna_impresso_por():
    """Limpa a coluna 'Impresso por' da tabela gestao_trilhas"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute("UPDATE gestao_trilhas SET 'Responsável' = ''")
        conn.commit()
        print("Coluna 'Impresso por' limpa com sucesso!")
    except Exception as e:
        print(f"Erro ao limpar coluna: {e}")
    finally:
        conn.close()

def gerar_xlsx_trilha(nome_trilha, codigo_trilha):
    """
    Gera um arquivo XLSX para uma trilha específica com as atividades do banco de dados.
    """
    import pandas as pd
    import io
    import datetime
    
    # Buscar atividades da trilha no banco de dados
    conn = sqlite3.connect(DB_FILE)
    try:
        # Buscar todas as atividades da trilha específica
        df_atividades = pd.read_sql_query(
            'SELECT Atividade, Responsável, Tipo, Observações FROM gestao_trilhas WHERE Trilhas = ? ORDER BY rowid', 
            conn, 
            params=[nome_trilha]
        )
        
        # Se não encontrou atividades, criar um DataFrame vazio com as colunas corretas
        if df_atividades.empty:
            df_atividades = pd.DataFrame(columns=['Atividade', 'Responsável', 'Tipo', 'Observações'])
            print(f"Nenhuma atividade encontrada para a trilha: {nome_trilha}")
        else:
            print(f"Encontradas {len(df_atividades)} atividades para a trilha: {nome_trilha}")
            
    except Exception as e:
        print(f"Erro ao buscar atividades: {e}")
        df_atividades = pd.DataFrame(columns=['Atividade', 'Responsável', 'Tipo', 'Observações'])
    finally:
        conn.close()
    
    # Criar buffer para o arquivo
    buffer = io.BytesIO()
    
    # Salvar como XLSX com formatação
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        # Escrever o DataFrame primeiro para criar a worksheet
        df_atividades.to_excel(writer, sheet_name='Trilha', startrow=2, index=False)
        
        # Agora podemos acessar a worksheet
        worksheet = writer.sheets['Trilha']
        workbook = writer.book
        
        # Título da trilha na primeira linha
        worksheet.write(0, 0, f"{codigo_trilha} - {nome_trilha}")
        
        # Linha vazia na segunda linha
        worksheet.write(1, 0, '')
        
        # Formatar o título da trilha (primeira linha)
        title_format = workbook.add_format({
            'bold': True,
            'font_size': 14,
            'align': 'left'
        })
        worksheet.set_row(0, 20, title_format)
        
        # Formatar o cabeçalho (terceira linha) - fundo cinza claro, texto branco em negrito
        header_format = workbook.add_format({
            'bold': True,
            'font_color': 'white',
            'bg_color': '#808080',  # Cinza mais claro
            'align': 'center',
            'valign': 'vcenter',
            'border': 1
        })
        
        # Formato para as células de dados (atividades) - com bordas
        data_format = workbook.add_format({
            'border': 1,
            'align': 'left',
            'valign': 'top',
            'text_wrap': True
        })
        
        # Aplicar formatação ao cabeçalho
        for col_num, value in enumerate(df_atividades.columns.values):
            worksheet.write(2, col_num, value, header_format)
        
        # Aplicar formatação às células de dados (atividades)
        for row_num in range(len(df_atividades)):
            for col_num in range(len(df_atividades.columns)):
                worksheet.write(row_num + 3, col_num, df_atividades.iloc[row_num, col_num], data_format)
        
        # Ajustar largura das colunas
        worksheet.set_column('A:A', 60)  # Atividades
        worksheet.set_column('B:B', 30)  # Responsável
        worksheet.set_column('C:C', 15)  # Tipo
        worksheet.set_column('D:D', 20)  # Observações
    
    buffer.seek(0)
    return buffer.read() 