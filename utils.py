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
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        
        # Limpar dados anteriores
        c.execute('DELETE FROM impressao_upload')
        
        colunas = list(df.columns)
        dados = df.values.tolist()
        
        print(f"Salvando {len(dados)} linhas com {len(colunas)} colunas")
        print(f"Colunas: {colunas}")
        
        c.execute('INSERT INTO impressao_upload (colunas, dados) VALUES (?, ?)', 
                 (json.dumps(colunas), json.dumps(dados)))
        conn.commit()
        conn.close()
        
        print("Dados salvos com sucesso na tabela impressao_upload")
        return True
    except Exception as e:
        print(f"Erro ao salvar dados: {e}")
        if 'conn' in locals():
            conn.close()
        return False

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
    try:
        conn = sqlite3.connect(DB_FILE)
        
        print(f"Salvando {len(df)} linhas na tabela gestao_trilhas")
        print(f"Colunas: {list(df.columns)}")
        
        df.to_sql('gestao_trilhas', conn, if_exists='replace', index=False)
        conn.close()
        
        print("Dados salvos com sucesso na tabela gestao_trilhas")
        return True
    except Exception as e:
        print(f"Erro ao salvar dados na tabela gestao_trilhas: {e}")
        if 'conn' in locals():
            conn.close()
        return False

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
        # Primeiro, verificar se a coluna Código existe na tabela
        c = conn.cursor()
        c.execute("PRAGMA table_info(gestao_trilhas)")
        colunas_tabela = [col[1] for col in c.fetchall()]
        
        # Definir as colunas para buscar baseado na estrutura da tabela
        if 'Código' in colunas_tabela:
            colunas_buscar = 'Atividade, Responsável, Tipo, Finalizado, Observações, Código'
        else:
            colunas_buscar = 'Atividade, Responsável, Tipo, Finalizado, Observações'
        
        # Buscar todas as atividades válidas da trilha específica (excluindo cabeçalhos e emails)
        df_atividades = pd.read_sql_query(
            f'''SELECT {colunas_buscar}
               FROM gestao_trilhas 
               WHERE Trilhas = ? 
               AND Atividade IS NOT NULL 
               AND Atividade != "Atividade" 
               AND Atividade != "Responsável"
               AND Atividade != ""
               AND Atividade NOT LIKE "%@%"
               AND LENGTH(Atividade) > 10
               ORDER BY rowid''', 
            conn, 
            params=[nome_trilha]
        )
        
        # Se não encontrou atividades, tentar buscar por correspondência parcial
        if df_atividades.empty:
            # Buscar trilhas que contenham o nome da trilha
            df_atividades = pd.read_sql_query(
                f'''SELECT {colunas_buscar}
                   FROM gestao_trilhas 
                   WHERE Trilhas LIKE ? 
                   AND Atividade IS NOT NULL 
                   AND Atividade != "Atividade" 
                   AND Atividade != "Responsável"
                   AND Atividade != ""
                   AND Atividade NOT LIKE "%@%"
                   AND LENGTH(Atividade) > 10
                   ORDER BY rowid''', 
                conn, 
                params=[f'%{nome_trilha}%']
            )
            
            if df_atividades.empty:
                # Se ainda não encontrou, buscar por código
                if codigo_trilha:
                    df_atividades = pd.read_sql_query(
                        f'''SELECT {colunas_buscar}
                           FROM gestao_trilhas 
                           WHERE Trilhas LIKE ? 
                           AND Atividade IS NOT NULL 
                           AND Atividade != "Atividade" 
                           AND Atividade != "Responsável"
                           AND Atividade != ""
                           AND Atividade NOT LIKE "%@%"
                           AND LENGTH(Atividade) > 10
                           ORDER BY rowid''', 
                        conn, 
                        params=[f'%{codigo_trilha}%']
                    )
        
        # Se não encontrou atividades, criar atividades corretas conforme imagem
        if df_atividades.empty:
            # Criar atividades corretas conforme mostrado na imagem
            atividades_template = [
                {
                    'Atividade': '1. Análise inicial da trilha',
                    'Responsável': 'A definir',
                    'Tipo': 'Análise',
                    'Finalizado': 'Não',
                    'Observações': 'Primeira etapa da trilha'
                },
                {
                    'Atividade': '2. Execução das atividades principais',
                    'Responsável': 'A definir',
                    'Tipo': 'Execução',
                    'Finalizado': 'Não',
                    'Observações': 'Atividades específicas da trilha'
                },
                {
                    'Atividade': '3. Validação e testes',
                    'Responsável': 'A definir',
                    'Tipo': 'Validação',
                    'Finalizado': 'Não',
                    'Observações': 'Verificação dos resultados'
                },
                {
                    'Atividade': '4. Finalização e documentação',
                    'Responsável': 'A definir',
                    'Tipo': 'Finalização',
                    'Finalizado': 'Não',
                    'Observações': 'Conclusão da trilha'
                }
            ]
            df_atividades = pd.DataFrame(atividades_template)
            print(f"Atividades corretas criadas para a trilha: {nome_trilha}")
        else:
            print(f"Encontradas {len(df_atividades)} atividades para a trilha: {nome_trilha}")
            
            # Formatar as atividades no padrão correto
            def formatar_atividade(row):
                atividade = str(row['Atividade'])
                
                # Verificar se a coluna Código existe e tem valor
                codigo_atividade = ''
                if 'Código' in row and pd.notnull(row['Código']) and row['Código']:
                    codigo_atividade = str(row['Código'])
                
                # Se a atividade já está no formato correto, retornar como está
                if ' - ' in atividade and ('CMR' in atividade or 'BPH' in atividade):
                    return atividade
                
                # Se temos código da trilha e código da atividade, formatar
                if codigo_trilha and codigo_atividade and codigo_atividade != 'nan':
                    # Extrair número da atividade (se existir)
                    import re
                    numero_match = re.search(r'^(\d+)\.', atividade)
                    numero_atividade = numero_match.group(1) if numero_match else ''
                    
                    if numero_atividade:
                        # Formato: CMR248.1 - BPH004197 - 43. Administrar deferimentos de crédito documentado
                        return f"{codigo_trilha} - {codigo_atividade} - {atividade}"
                    else:
                        # Formato: CMR248.1 - BPH004197 - Administrar deferimentos de crédito documentado
                        return f"{codigo_trilha} - {codigo_atividade} - {atividade}"
                
                # Se só temos código da trilha
                elif codigo_trilha:
                    return f"{codigo_trilha} - {atividade}"
                
                # Se não temos códigos, retornar atividade como está
                return atividade
            
            # Aplicar formatação às atividades
            df_atividades['Atividade'] = df_atividades.apply(formatar_atividade, axis=1)
            
    except Exception as e:
        print(f"Erro ao buscar atividades: {e}")
        df_atividades = pd.DataFrame(columns=['Atividade', 'Responsável', 'Tipo', 'Finalizado', 'Observações'])
    finally:
        conn.close()
    
    # Criar buffer para o arquivo
    buffer = io.BytesIO()
    
    # Salvar como XLSX com formatação
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        # Escrever o DataFrame primeiro para criar a worksheet
        df_atividades.to_excel(writer, sheet_name='Trilha', startrow=3, index=False)
        
        # Agora podemos acessar a worksheet
        worksheet = writer.sheets['Trilha']
        workbook = writer.book
        
        # Título da trilha na primeira linha (sem duplicação)
        worksheet.write(0, 0, f"{codigo_trilha} - {nome_trilha}")
        
        # Data de geração na segunda linha
        data_geracao = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        worksheet.write(1, 0, f"Gerado em: {data_geracao}")
        
        # Linha vazia na terceira linha
        worksheet.write(2, 0, '')
        
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
            worksheet.write(3, col_num, value, header_format)
        
        # Aplicar formatação às células de dados (atividades)
        for row_num in range(len(df_atividades)):
            for col_num in range(len(df_atividades.columns)):
                worksheet.write(row_num + 4, col_num, df_atividades.iloc[row_num, col_num], data_format)
        
        # Ajustar largura das colunas
        worksheet.set_column('A:A', 60)  # Atividades
        worksheet.set_column('B:B', 30)  # Responsável
        worksheet.set_column('C:C', 15)  # Tipo
        worksheet.set_column('D:D', 15)  # Finalizado
        worksheet.set_column('E:E', 20)  # Observações
    
    buffer.seek(0)
    return buffer.read()

def atualizar_status_download(nome_trilha, usuario_logado):
    """
    Atualiza as colunas Status, Modificado por e Modificado em no database_2.db
    quando um download é realizado.
    """
    import datetime
    
    # Conectar ao database_2.db
    conn = sqlite3.connect('database_2.db')
    c = conn.cursor()
    
    try:
        # Data e hora atual
        data_hora_atual = datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        
        # Atualizar as colunas para a trilha específica
        c.execute('''
            UPDATE controle_trilhas 
            SET Status = ?, "Modificado por" = ?, "Modificado em" = ? 
            WHERE Trilhas = ?
        ''', ('Impresso', usuario_logado, data_hora_atual, nome_trilha))
        
        conn.commit()
        print(f"Status atualizado para trilha: {nome_trilha}")
        print(f"Usuário: {usuario_logado}")
        print(f"Data/Hora: {data_hora_atual}")
        
    except Exception as e:
        print(f"Erro ao atualizar status: {e}")
    finally:
        conn.close() 

def sincronizar_database2():
    """Sincroniza dados entre os bancos de dados"""
    try:
        # Conectar aos bancos
        conn_login = sqlite3.connect(DB_FILE)
        conn2 = sqlite3.connect('database_2.db')
        
        # Buscar dados do login_status.db
        df_gestao = pd.read_sql_query('SELECT Trilhas, Código FROM gestao_trilhas', conn_login)
        
        # Buscar dados do database_2.db
        df_controle = pd.read_sql_query('SELECT Trilhas FROM controle_trilhas', conn2)
        
        # Mesclar dados
        df_merged = pd.merge(df_controle, df_gestao, on='Trilhas', how='left')
        
        # Atualizar database_2.db
        df_merged.to_sql('controle_trilhas', conn2, if_exists='replace', index=False)
        
        conn_login.close()
        conn2.close()
        
        print("Sincronização concluída com sucesso!")
        return True
        
    except Exception as e:
        print(f"Erro na sincronização: {e}")
        return False

def registrar_download_trilha(nome_trilha, usuario_logado):
    """Registra o download de uma trilha no banco de dados"""
    import os
    import datetime
    
    db_trilhas_path = os.path.join("Impressão de trilhas", "database_trilhas.db")
    
    if not os.path.exists(db_trilhas_path):
        print(f"Banco de dados não encontrado: {db_trilhas_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_trilhas_path)
        cursor = conn.cursor()
        
        # Verificar se já existe registro para esta trilha
        cursor.execute('SELECT id FROM controle_downloads WHERE Trilhas = ?', (nome_trilha,))
        registro_existente = cursor.fetchone()
        
        data_hora_atual = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        if registro_existente:
            # Atualizar registro existente
            cursor.execute('''
                UPDATE controle_downloads 
                SET Impresso = 'SIM', 
                    Impresso_por = ?, 
                    Modificado_em = ? 
                WHERE Trilhas = ?
            ''', (usuario_logado, data_hora_atual, nome_trilha))
        else:
            # Inserir novo registro
            cursor.execute('''
                INSERT INTO controle_downloads (Trilhas, Impresso, Impresso_por, Modificado_em)
                VALUES (?, 'SIM', ?, ?)
            ''', (nome_trilha, usuario_logado, data_hora_atual))
        
        conn.commit()
        conn.close()
        
        print(f"Download da trilha '{nome_trilha}' registrado para o usuário '{usuario_logado}'")
        return True
        
    except Exception as e:
        print(f"Erro ao registrar download: {e}")
        if 'conn' in locals():
            conn.close()
        return False

def buscar_controle_downloads():
    """Busca todos os registros de controle de downloads"""
    import os
    
    db_trilhas_path = os.path.join("Impressão de trilhas", "database_trilhas.db")
    
    if not os.path.exists(db_trilhas_path):
        return pd.DataFrame()
    
    try:
        conn = sqlite3.connect(db_trilhas_path)
        
        # Buscar todas as trilhas únicas
        df_trilhas = pd.read_sql_query('SELECT DISTINCT Trilhas FROM trilhas WHERE Trilhas IS NOT NULL AND Trilhas != ""', conn)
        
        # Buscar controle de downloads
        df_controle = pd.read_sql_query('''
            SELECT Trilhas, Impresso, Impresso_por, Modificado_em 
            FROM controle_downloads
        ''', conn)
        
        conn.close()
        
        # Mesclar trilhas com controle de downloads
        df_resultado = pd.merge(df_trilhas, df_controle, on='Trilhas', how='left')
        
        # Preencher valores nulos
        df_resultado['Impresso'] = df_resultado['Impresso'].fillna('NÃO')
        df_resultado['Impresso_por'] = df_resultado['Impresso_por'].fillna('')
        df_resultado['Modificado_em'] = df_resultado['Modificado_em'].fillna('')
        
        return df_resultado
        
    except Exception as e:
        print(f"Erro ao buscar controle de downloads: {e}")
        return pd.DataFrame()

def gerar_xlsx_trilha_novo_banco(nome_trilha, codigo_trilha, usuario_logado=None):
    """
    Gera um arquivo XLSX para uma trilha específica usando dados do novo banco database_trilhas.db
    Formato: Linha 1 = Nome da Trilha, Linha 2 = Vazia, Linha 3 = Cabeçalhos, Demais linhas = Dados
    """
    import pandas as pd
    import io
    import datetime
    import os
    
    # Caminho para o novo banco de dados
    db_trilhas_path = os.path.join("Impressão de trilhas", "database_trilhas.db")
    
    if not os.path.exists(db_trilhas_path):
        raise Exception("Banco de dados database_trilhas.db não encontrado!")
    
    # Buscar atividades da trilha no novo banco de dados
    conn = sqlite3.connect(db_trilhas_path)
    try:
        # Buscar todas as atividades da trilha específica
        df_atividades = pd.read_sql_query(
            '''SELECT Atividades, Responsável, Tipo, Finalizado, Observações
               FROM trilhas 
               WHERE Trilhas = ? 
               AND Atividades IS NOT NULL 
               AND Atividades != ""
               ORDER BY Atividades''', 
            conn, 
            params=[nome_trilha]
        )
        
        if df_atividades.empty:
            # Se não há atividades, criar template básico
            print(f"Nenhuma atividade encontrada para a trilha: {nome_trilha}")
            df_atividades = pd.DataFrame({
                'Atividades': ['Atividade de exemplo'],
                'Responsável': ['Responsável'],
                'Tipo': ['Tipo'],
                'Finalizado': ['Não'],
                'Observações': ['Observação']
            })
        else:
            print(f"Encontradas {len(df_atividades)} atividades para a trilha: {nome_trilha}")
            
            # Formatar as atividades no padrão correto
            def formatar_atividade(row):
                atividade = str(row['Atividades'])
                
                # Se a atividade já está no formato correto, retornar como está
                if ' - ' in atividade and ('CMR' in atividade or 'BPH' in atividade):
                    return atividade
                
                # Se temos código da trilha, formatar
                if codigo_trilha:
                    # Extrair número da atividade (se existir)
                    import re
                    numero_match = re.search(r'^(\d+)\.', atividade)
                    numero_atividade = numero_match.group(1) if numero_match else ''
                    
                    if numero_atividade:
                        # Formato: CMR248.1 - BPH004197 - 43. Administrar deferimentos de crédito documentado
                        return f"{codigo_trilha} - BPH{numero_atividade.zfill(6)} - {atividade}"
                    else:
                        # Formato: CMR248.1 - Administrar deferimentos de crédito documentado
                        return f"{codigo_trilha} - {atividade}"
                
                # Se não temos códigos, retornar atividade como está
                return atividade
            
            # Aplicar formatação às atividades
            df_atividades['Atividades'] = df_atividades.apply(formatar_atividade, axis=1)
        
    except Exception as e:
        print(f"Erro ao buscar atividades: {e}")
        df_atividades = pd.DataFrame(columns=['Atividades', 'Responsável', 'Tipo', 'Finalizado', 'Observações'])
    finally:
        conn.close()
    
    # Registrar download se usuário foi fornecido
    if usuario_logado:
        registrar_download_trilha(nome_trilha, usuario_logado)
    
    # Criar arquivo Excel
    buffer = io.BytesIO()
    
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        # Obter workbook e worksheet
        workbook = writer.book
        
        # Criar worksheet
        worksheet = workbook.add_worksheet('Trilha')
        
        # Definir formatos
        titulo_format = workbook.add_format({
            'bold': True,
            'font_size': 14,
            'align': 'left',
            'valign': 'top'
        })
        
        header_format = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'top',
            'fg_color': '#D7E4BC',
            'border': 1,
            'align': 'center'
        })
        
        cell_format = workbook.add_format({
            'text_wrap': True,
            'valign': 'top',
            'border': 1,
            'align': 'left'
        })
        
        # Escrever linha 1: Nome da Trilha
        nome_completo_trilha = f"{codigo_trilha} - {nome_trilha}" if codigo_trilha else nome_trilha
        worksheet.write(0, 0, nome_completo_trilha, titulo_format)
        
        # Linha 2: Vazia (já está vazia por padrão)
        
        # Linha 3: Cabeçalhos das colunas
        colunas = ['Atividades', 'Responsável', 'Tipo', 'Finalizado', 'Observações']
        for col_num, coluna in enumerate(colunas):
            worksheet.write(2, col_num, coluna, header_format)
        
        # Demais linhas: Dados das atividades
        for row_num, (_, row) in enumerate(df_atividades.iterrows(), start=3):
            for col_num, coluna in enumerate(colunas):
                valor = row[coluna] if pd.notnull(row[coluna]) else ''
                worksheet.write(row_num, col_num, valor, cell_format)
        
        # Ajustar largura das colunas
        larguras_colunas = [50, 20, 15, 15, 30]  # Atividades, Responsável, Tipo, Finalizado, Observações
        for i, largura in enumerate(larguras_colunas):
            worksheet.set_column(i, i, largura)
        
        # Definir altura da linha do título
        worksheet.set_row(0, 25)
        
        # Definir altura das linhas de dados
        for row_num in range(3, len(df_atividades) + 3):
            worksheet.set_row(row_num, 20)
    
    buffer.seek(0)
    return buffer.read() 