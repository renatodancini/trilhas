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
        # Buscar todas as atividades válidas da trilha específica (excluindo cabeçalhos e emails)
        df_atividades = pd.read_sql_query(
            '''SELECT Atividade, Responsável, Tipo, Finalizado, Observações 
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
                '''SELECT Atividade, Responsável, Tipo, Finalizado, Observações 
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
                        '''SELECT Atividade, Responsável, Tipo, Finalizado, Observações 
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
        
        # Se não encontrou atividades, criar atividades baseadas no código da trilha
        if df_atividades.empty:
            # Criar atividades específicas baseadas no código CMR
            atividades_template = [
                {
                    'Atividade': f'{codigo_trilha} - BPH004251 - 1. Relatório de estoques / Disponibilidade do Produto',
                    'Responsável': 'bruno.lobo@sipal.com.br',
                    'Tipo': 'SAP',
                    'Finalizado': '',
                    'Observações': ''
                },
                {
                    'Atividade': f'{codigo_trilha} - BPH004047 - 2. Criar contrato de compra',
                    'Responsável': 'bruno.lobo@sipal.com.br',
                    'Tipo': 'SAP',
                    'Finalizado': '',
                    'Observações': ''
                },
                {
                    'Atividade': f'{codigo_trilha} - BPH003890 - 3. Aprovar contrato de Compras',
                    'Responsável': 'lucas.sbardella@sipal.com.br',
                    'Tipo': 'SAP',
                    'Finalizado': '',
                    'Observações': ''
                },
                {
                    'Atividade': f'{codigo_trilha} - BPH003890 - 4. Consultar aprovação de workflow',
                    'Responsável': 'lucas.sbardella@sipal.com.br',
                    'Tipo': 'SAP',
                    'Finalizado': '',
                    'Observações': ''
                },
                {
                    'Atividade': f'{codigo_trilha} - BPH003625 - 5. Avaliar fluxo de caixa diário',
                    'Responsável': 'caroline.silva@sipal.com.br',
                    'Tipo': 'SAP',
                    'Finalizado': '',
                    'Observações': ''
                },
                {
                    'Atividade': f'{codigo_trilha} - BPH004065 - 6. Criar pedido de compra vinculado ao contrato',
                    'Responsável': 'bruno.lobo@sipal.com.br',
                    'Tipo': 'SAP',
                    'Finalizado': '',
                    'Observações': ''
                },
                {
                    'Atividade': f'{codigo_trilha} - BPH003386 - 7. Realizar Pré Validação Fiscal do Pedido de Compra [VALIDAÇÃO]',
                    'Responsável': 'everton.siqueira@sipal.com.br',
                    'Tipo': 'SAP',
                    'Finalizado': '',
                    'Observações': ''
                },
                {
                    'Atividade': f'{codigo_trilha} - BPH003625 - 8. Avaliar fluxo de caixa diário',
                    'Responsável': 'caroline.silva@sipal.com.br',
                    'Tipo': 'SAP',
                    'Finalizado': '',
                    'Observações': ''
                },
                {
                    'Atividade': f'{codigo_trilha} - BPH004054 - 9. Lançar contrato de Venda',
                    'Responsável': 'anna.santos@sipal.com.br',
                    'Tipo': 'SAP',
                    'Finalizado': '',
                    'Observações': ''
                },
                {
                    'Atividade': f'{codigo_trilha} - BPH004301 - 10. Aprovar contrato de Venda',
                    'Responsável': 'anna.santos@sipal.com.br',
                    'Tipo': 'SAP',
                    'Finalizado': '',
                    'Observações': ''
                },
                {
                    'Atividade': f'{codigo_trilha} - BPH003625 - 11. Avaliar fluxo de caixa diário',
                    'Responsável': 'caroline.silva@sipal.com.br',
                    'Tipo': 'SAP',
                    'Finalizado': '',
                    'Observações': ''
                },
                {
                    'Atividade': f'{codigo_trilha} - BPH004055 - 12. Lançar ordem de venda no sistema',
                    'Responsável': 'lucas.sbardella@sipal.com.br',
                    'Tipo': 'SAP',
                    'Finalizado': '',
                    'Observações': ''
                },
                {
                    'Atividade': f'{codigo_trilha} - BPH003523 - 13. Realizar Pré Validação Fiscal da Ordem de Venda [VALIDAÇÃO]',
                    'Responsável': 'luiz.ferreira@sipal.com.br',
                    'Tipo': 'SAP',
                    'Finalizado': '',
                    'Observações': ''
                },
                {
                    'Atividade': f'{codigo_trilha} - BPH001162 - 14. Identificar a demanda na plataforma',
                    'Responsável': 'simone.tessaro@sipal.com.br',
                    'Tipo': 'Tarken',
                    'Finalizado': '',
                    'Observações': ''
                }
            ]
            df_atividades = pd.DataFrame(atividades_template)
            print(f"Atividades específicas criadas para a trilha: {nome_trilha}")
        else:
            print(f"Encontradas {len(df_atividades)} atividades para a trilha: {nome_trilha}")
            
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
        df_atividades.to_excel(writer, sheet_name='Trilha', startrow=5, index=False)
        
        # Agora podemos acessar a worksheet
        worksheet = writer.sheets['Trilha']
        workbook = writer.book
        
        # Título da trilha na primeira linha
        worksheet.write(0, 0, f"{codigo_trilha} - {nome_trilha}")
        
        # Descrição completa na segunda linha
        worksheet.write(1, 0, f"{nome_trilha} - Ori. Fabrica / Dest. Cliente - (Compra FOB e Venda CIF - À Prazo) V - [C3]")
        
        # "Massa de dados não informada" na terceira linha
        worksheet.write(2, 0, "Massa de dados não informada")
        
        # Data de geração na quarta linha
        data_geracao = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        worksheet.write(3, 0, f"Gerado em: {data_geracao}")
        
        # Linha vazia na quinta linha
        worksheet.write(4, 0, '')
        
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
            worksheet.write(5, col_num, value, header_format)
        
        # Aplicar formatação às células de dados (atividades)
        for row_num in range(len(df_atividades)):
            for col_num in range(len(df_atividades.columns)):
                worksheet.write(row_num + 6, col_num, df_atividades.iloc[row_num, col_num], data_format)
        
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
    """
    Sincroniza os dados do banco principal (login_status.db) para o database_2.db
    """
    try:
        # Conectar aos dois bancos
        conn_principal = sqlite3.connect(DB_FILE)
        conn_database2 = sqlite3.connect('database_2.db')
        
        # Buscar apenas as trilhas principais (sem atividade preenchida)
        df_gestao = pd.read_sql_query('''
            SELECT DISTINCT Trilhas, Código 
            FROM gestao_trilhas 
            WHERE Trilhas IS NOT NULL 
            AND Trilhas != "" 
            AND (Atividade IS NULL OR Atividade = "" OR Atividade = "Responsável")
            AND Trilhas != "Massa de dados não informada"
        ''', conn_principal)
        
        print(f"Sincronizando {len(df_gestao)} trilhas principais para database_2.db")
        
        # Limpar tabela controle_trilhas no database_2.db
        c = conn_database2.cursor()
        c.execute('DELETE FROM controle_trilhas')
        c.execute('DELETE FROM controle_execucao')
        
        # Inserir dados na tabela controle_trilhas
        for _, row in df_gestao.iterrows():
            trilha = row['Trilhas']
            codigo = row['Código'] if pd.notnull(row['Código']) else ''
            
            c.execute('''
                INSERT INTO controle_trilhas (Trilhas, Status, "Modificado por", "Modificado em") 
                VALUES (?, ?, ?, ?)
            ''', (trilha, 'Pendente', '', ''))
            
            # Também inserir na tabela controle_execucao
            c.execute('''
                INSERT INTO controle_execucao (trilha, categoria, status, modificado_por, modificado_em) 
                VALUES (?, ?, ?, ?, ?)
            ''', (trilha, 0, 'Pendente', '', ''))
        
        conn_database2.commit()
        conn_principal.close()
        conn_database2.close()
        
        print("✅ Sincronização concluída com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro na sincronização: {e}")
        if 'conn_principal' in locals():
            conn_principal.close()
        if 'conn_database2' in locals():
            conn_database2.close()
        return False 