#!/usr/bin/env python3
"""
Script para testar se as trilhas estão sendo exibidas corretamente com os códigos
"""

import sqlite3
import pandas as pd
from utils import DB_FILE

def testar_exibicao_trilhas():
    """
    Testa se as trilhas estão sendo exibidas corretamente com os códigos
    """
    print("🧪 Testando exibição das trilhas")
    print("="*40)
    
    # Testar dados do database_2.db
    print("\n📊 Dados do database_2.db (controle_trilhas):")
    conn2 = sqlite3.connect('database_2.db')
    try:
        df_trilhas_controle = pd.read_sql_query('SELECT Trilhas FROM controle_trilhas', conn2)
        print(f"  - Total de trilhas no controle: {len(df_trilhas_controle)}")
        
        if not df_trilhas_controle.empty:
            print("  - Primeiras 5 trilhas:")
            for i, (_, row) in enumerate(df_trilhas_controle.head(5).iterrows(), 1):
                print(f"    {i}. {row['Trilhas']}")
    except Exception as e:
        print(f"  - Erro ao ler controle_trilhas: {e}")
    conn2.close()
    
    # Testar dados do login_status.db
    print("\n📊 Dados do login_status.db (gestao_trilhas):")
    conn_gestao = sqlite3.connect('login_status.db')
    try:
        df_gestao = pd.read_sql_query('SELECT Trilhas, Código FROM gestao_trilhas', conn_gestao)
        print(f"  - Total de trilhas na gestão: {len(df_gestao)}")
        
        # Trilhas principais (sem atividade)
        trilhas_principais = df_gestao[df_gestao['Atividade'].isna() | (df_gestao['Atividade'] == '')]
        print(f"  - Trilhas principais: {len(trilhas_principais)}")
        
        if not trilhas_principais.empty:
            print("  - Primeiras 5 trilhas principais com código:")
            for i, (_, row) in enumerate(trilhas_principais.head(5).iterrows(), 1):
                codigo = row['Código'] if pd.notnull(row['Código']) and row['Código'] else 'SEM CÓDIGO'
                print(f"    {i}. {codigo} - {row['Trilhas']}")
    except Exception as e:
        print(f"  - Erro ao ler gestao_trilhas: {e}")
    conn_gestao.close()
    
    # Testar mesclagem (como na página de impressão)
    print("\n🔗 Testando mesclagem (como na página de impressão):")
    try:
        # Buscar trilhas do controle
        conn2 = sqlite3.connect('database_2.db')
        df_trilhas_controle = pd.read_sql_query('SELECT Trilhas FROM controle_trilhas', conn2)
        conn2.close()
        
        # Buscar códigos das trilhas
        conn_gestao = sqlite3.connect('login_status.db')
        df_gestao = pd.read_sql_query('SELECT Trilhas, Código FROM gestao_trilhas', conn_gestao)
        conn_gestao.close()
        
        # Mesclar
        df_trilhas_completas = pd.merge(df_trilhas_controle, df_gestao, left_on='Trilhas', right_on='Trilhas', how='left')
        
        print(f"  - Total após mesclagem: {len(df_trilhas_completas)}")
        
        # Verificar trilhas sem código
        trilhas_sem_codigo = df_trilhas_completas[
            df_trilhas_completas['Código'].isna() | 
            (df_trilhas_completas['Código'] == '') | 
            (df_trilhas_completas['Código'] == 'nan')
        ]
        
        print(f"  - Trilhas sem código após mesclagem: {len(trilhas_sem_codigo)}")
        
        if len(trilhas_sem_codigo) > 0:
            print("  - Trilhas sem código:")
            for i, (_, row) in enumerate(trilhas_sem_codigo.head(5).iterrows(), 1):
                print(f"    {i}. {row['Trilhas']}")
        
        # Mostrar exemplos de trilhas com código
        trilhas_com_codigo = df_trilhas_completas[
            df_trilhas_completas['Código'].notna() & 
            (df_trilhas_completas['Código'] != '') & 
            (df_trilhas_completas['Código'] != 'nan')
        ]
        
        print(f"  - Trilhas com código: {len(trilhas_com_codigo)}")
        
        if not trilhas_com_codigo.empty:
            print("  - Exemplos de trilhas com código:")
            for i, (_, row) in enumerate(trilhas_com_codigo.head(5).iterrows(), 1):
                codigo = row['Código']
                trilha = row['Trilhas']
                print(f"    {i}. {codigo} - {trilha}")
        
    except Exception as e:
        print(f"  - Erro na mesclagem: {e}")

def verificar_formato_exibicao():
    """
    Verifica como as trilhas serão exibidas na interface
    """
    print("\n🎨 Verificando formato de exibição:")
    
    try:
        # Buscar dados como na página de impressão
        conn2 = sqlite3.connect('database_2.db')
        df_trilhas_controle = pd.read_sql_query('SELECT Trilhas FROM controle_trilhas', conn2)
        conn2.close()
        
        conn_gestao = sqlite3.connect('login_status.db')
        df_gestao = pd.read_sql_query('SELECT Trilhas, Código FROM gestao_trilhas', conn_gestao)
        conn_gestao.close()
        
        # Mesclar
        df_trilhas_completas = pd.merge(df_trilhas_controle, df_gestao, left_on='Trilhas', right_on='Trilhas', how='left')
        
        # Simular criação das opções do combobox
        opcoes_combo = []
        for _, row in df_trilhas_completas.iterrows():
            codigo = row['Código'] if pd.notnull(row['Código']) and row['Código'] else ''
            trilha = row['Trilhas']
            opcao = f"{codigo} - {trilha}" if codigo else trilha
            opcoes_combo.append(opcao)
        
        print(f"  - Total de opções no combobox: {len(opcoes_combo)}")
        
        # Mostrar exemplos das opções
        print("  - Primeiras 5 opções do combobox:")
        for i, opcao in enumerate(opcoes_combo[:5], 1):
            print(f"    {i}. {opcao}")
        
        # Verificar se há opções sem código
        opcoes_sem_codigo = [op for op in opcoes_combo if not op.startswith(('CMR', 'cmr'))]
        print(f"  - Opções sem código no início: {len(opcoes_sem_codigo)}")
        
        if opcoes_sem_codigo:
            print("  - Exemplos de opções sem código:")
            for i, opcao in enumerate(opcoes_sem_codigo[:3], 1):
                print(f"    {i}. {opcao}")
        
    except Exception as e:
        print(f"  - Erro ao verificar formato: {e}")

if __name__ == "__main__":
    testar_exibicao_trilhas()
    verificar_formato_exibicao() 