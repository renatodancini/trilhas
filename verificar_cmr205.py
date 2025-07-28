#!/usr/bin/env python3
import sqlite3
import pandas as pd

conn = sqlite3.connect('login_status.db')
df = pd.read_sql_query('SELECT * FROM gestao_trilhas LIMIT 10', conn)
print('Estrutura da tabela gestao_trilhas:')
print(df)
print(f'\nColunas: {list(df.columns)}')
print(f'Total de registros: {len(df)}')

# Verificar valores únicos na coluna Atividade
print('\nValores únicos na coluna Atividade:')
atividades_unicas = pd.read_sql_query('SELECT DISTINCT Atividade FROM gestao_trilhas WHERE Atividade IS NOT NULL', conn)
print(atividades_unicas)

conn.close() 