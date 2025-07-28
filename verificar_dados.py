#!/usr/bin/env python3
import sqlite3
import pandas as pd

print("Verificando atividades reais na tabela gestao_trilhas...")

conn = sqlite3.connect('login_status.db')

# Buscar atividades que não são emails e têm mais de 10 caracteres
df = pd.read_sql_query('''SELECT Trilhas, Atividade, Responsável, Tipo 
                          FROM gestao_trilhas 
                          WHERE Atividade IS NOT NULL 
                          AND Atividade != "Atividade" 
                          AND Atividade != "Responsável"
                          AND Atividade != ""
                          AND Atividade NOT LIKE "%@%"
                          AND LENGTH(Atividade) > 10
                          LIMIT 10''', conn)

print("Atividades reais encontradas:")
print(df)
print(f"\nTotal de atividades reais: {len(df)}")

# Verificar se há dados na tabela controle_execucao
print("\nVerificando tabela controle_execucao...")
conn2 = sqlite3.connect('database_2.db')
df_exec = pd.read_sql_query('SELECT * FROM controle_execucao LIMIT 5', conn2)
print("Primeiras 5 linhas de controle_execucao:")
print(df_exec)
print(f"Colunas: {list(df_exec.columns)}")
conn2.close()

conn.close() 