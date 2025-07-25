import sqlite3

def criar_tabela_controle_execucao(db_path='database_2.db'):
    """
    Cria a tabela controle_execucao no banco de dados especificado.
    """
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS controle_execucao (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        trilha TEXT,
        categoria INTEGER,
        status TEXT,
        modificado_por TEXT,
        modificado_em TEXT
    )''')
    
    conn.commit()
    conn.close() 