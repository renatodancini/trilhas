#!/usr/bin/env python3
"""
Serviço de Sincronização de Tabelas
Sincroniza todas as tabelas do sistema conforme as regras implementadas
"""

import sqlite3
import pandas as pd
import re
from datetime import datetime

def extrair_codigo_da_trilha(nome_trilha):
    """
    Extrai o código da trilha do nome
    """
    if pd.isna(nome_trilha) or not nome_trilha:
        return None
    
    # Padrão para encontrar códigos CMR seguidos de números
    padrao = r'^(CMR\s*\d+\.?\d*)'
    match = re.search(padrao, str(nome_trilha), re.IGNORECASE)
    
    if match:
        return match.group(1).strip()
    
    return None

def sincronizar_gestao_trilhas():
    """
    Sincroniza a tabela gestao_trilhas com códigos extraídos dos nomes
    """
    print("🔄 Sincronizando gestao_trilhas")
    print("="*40)
    
    conn_gestao = sqlite3.connect('login_status.db')
    
    # Buscar todas as trilhas da gestão
    df_gestao = pd.read_sql_query('SELECT * FROM gestao_trilhas', conn_gestao)
    print(f"📊 Total de trilhas na gestão: {len(df_gestao)}")
    
    # Identificar trilhas sem código
    trilhas_sem_codigo = df_gestao[
        df_gestao['Código'].isna() | 
        (df_gestao['Código'] == '') | 
        (df_gestao['Código'] == 'nan') |
        (df_gestao['Código'].astype(str).str.lower() == 'nan')
    ]
    
    print(f"❌ Trilhas sem código: {len(trilhas_sem_codigo)}")
    
    # Aplicar códigos extraídos
    correcoes = 0
    cursor = conn_gestao.cursor()
    
    for idx, row in trilhas_sem_codigo.iterrows():
        nome_trilha = row['Trilhas']
        codigo_extraido = extrair_codigo_da_trilha(nome_trilha)
        
        if codigo_extraido:
            cursor.execute(
                'UPDATE gestao_trilhas SET "Código" = ? WHERE rowid = ?',
                (codigo_extraido, idx + 1)
            )
            correcoes += 1
    
    conn_gestao.commit()
    conn_gestao.close()
    
    print(f"✅ {correcoes} códigos aplicados na gestão")
    return correcoes

def sincronizar_controle_trilhas():
    """
    Sincroniza a tabela controle_trilhas com códigos da gestão
    """
    print("\n🔄 Sincronizando controle_trilhas")
    print("="*40)
    
    conn2 = sqlite3.connect('database_2.db')
    conn_gestao = sqlite3.connect('login_status.db')
    
    # Buscar trilhas do controle
    df_controle = pd.read_sql_query('SELECT * FROM controle_trilhas', conn2)
    print(f"📊 Total de trilhas no controle: {len(df_controle)}")
    
    # Buscar códigos da gestão
    df_gestao = pd.read_sql_query('SELECT Trilhas, Código FROM gestao_trilhas', conn_gestao)
    
    # Identificar trilhas sem código no controle
    trilhas_sem_codigo = []
    for idx, row in df_controle.iterrows():
        nome_trilha = row['Trilhas']
        codigo_extraido = extrair_codigo_da_trilha(nome_trilha)
        
        if not codigo_extraido:
            trilhas_sem_codigo.append({
                'id': idx,
                'trilha': nome_trilha
            })
    
    print(f"❌ Trilhas sem código no controle: {len(trilhas_sem_codigo)}")
    
    # Aplicar códigos da gestão
    correcoes = 0
    cursor = conn2.cursor()
    
    for item in trilhas_sem_codigo:
        trilha = item['trilha']
        
        # Buscar código na gestão
        match_gestao = df_gestao[df_gestao['Trilhas'] == trilha]
        
        if not match_gestao.empty:
            codigo_gestao = match_gestao.iloc[0]['Código']
            if pd.notnull(codigo_gestao) and codigo_gestao and codigo_gestao != 'nan':
                # Atualizar nome da trilha com código
                novo_nome = f"{codigo_gestao} - {trilha}"
                cursor.execute(
                    'UPDATE controle_trilhas SET "Trilhas" = ? WHERE rowid = ?',
                    (novo_nome, item['id'] + 1)
                )
                correcoes += 1
    
    conn2.commit()
    conn2.close()
    conn_gestao.close()
    
    print(f"✅ {correcoes} trilhas atualizadas no controle")
    return correcoes

def sincronizar_controle_execucao():
    """
    Sincroniza a tabela controle_execucao com códigos
    """
    print("\n🔄 Sincronizando controle_execucao")
    print("="*40)
    
    conn2 = sqlite3.connect('database_2.db')
    conn_gestao = sqlite3.connect('login_status.db')
    
    # Buscar trilhas da execução
    df_exec = pd.read_sql_query('SELECT * FROM controle_execucao', conn2)
    print(f"📊 Total de trilhas na execução: {len(df_exec)}")
    
    # Buscar códigos da gestão
    df_gestao = pd.read_sql_query('SELECT Trilhas, Código FROM gestao_trilhas', conn_gestao)
    
    # Identificar trilhas sem código na execução
    trilhas_sem_codigo = []
    for idx, row in df_exec.iterrows():
        nome_trilha = row['trilha']
        codigo_extraido = extrair_codigo_da_trilha(nome_trilha)
        
        if not codigo_extraido:
            trilhas_sem_codigo.append({
                'id': idx,
                'trilha': nome_trilha
            })
    
    print(f"❌ Trilhas sem código na execução: {len(trilhas_sem_codigo)}")
    
    # Aplicar códigos da gestão
    correcoes = 0
    cursor = conn2.cursor()
    
    for item in trilhas_sem_codigo:
        trilha = item['trilha']
        
        # Buscar código na gestão
        match_gestao = df_gestao[df_gestao['Trilhas'] == trilha]
        
        if not match_gestao.empty:
            codigo_gestao = match_gestao.iloc[0]['Código']
            if pd.notnull(codigo_gestao) and codigo_gestao and codigo_gestao != 'nan':
                # Atualizar nome da trilha com código
                novo_nome = f"{codigo_gestao} - {trilha}"
                cursor.execute(
                    'UPDATE controle_execucao SET trilha = ? WHERE rowid = ?',
                    (novo_nome, item['id'] + 1)
                )
                correcoes += 1
    
    conn2.commit()
    conn2.close()
    conn_gestao.close()
    
    print(f"✅ {correcoes} trilhas atualizadas na execução")
    return correcoes

def limpar_duplicatas():
    """
    Remove duplicatas de todas as tabelas
    """
    print("\n🧹 Removendo duplicatas")
    print("="*30)
    
    # Limpar duplicatas do controle_trilhas
    conn2 = sqlite3.connect('database_2.db')
    df_controle = pd.read_sql_query('SELECT * FROM controle_trilhas', conn2)
    duplicatas_controle = len(df_controle[df_controle.duplicated(subset=['Trilhas'], keep=False)])
    
    if duplicatas_controle > 0:
        df_controle_limpo = df_controle.drop_duplicates(subset=['Trilhas'], keep='first')
        df_controle_limpo.to_sql('controle_trilhas', conn2, if_exists='replace', index=False)
        print(f"✅ {duplicatas_controle} duplicatas removidas do controle_trilhas")
    
    # Limpar duplicatas do controle_execucao
    df_exec = pd.read_sql_query('SELECT * FROM controle_execucao', conn2)
    duplicatas_exec = len(df_exec[df_exec.duplicated(subset=['trilha'], keep=False)])
    
    if duplicatas_exec > 0:
        df_exec_limpo = df_exec.drop_duplicates(subset=['trilha'], keep='first')
        df_exec_limpo.to_sql('controle_execucao', conn2, if_exists='replace', index=False)
        print(f"✅ {duplicatas_exec} duplicatas removidas do controle_execucao")
    
    conn2.close()
    
    # Limpar duplicatas da gestao_trilhas
    conn_gestao = sqlite3.connect('login_status.db')
    df_gestao = pd.read_sql_query('SELECT * FROM gestao_trilhas', conn_gestao)
    duplicatas_gestao = len(df_gestao[df_gestao.duplicated(subset=['Trilhas'], keep=False)])
    
    if duplicatas_gestao > 0:
        df_gestao_limpo = df_gestao.drop_duplicates(subset=['Trilhas'], keep='first')
        df_gestao_limpo.to_sql('gestao_trilhas', conn_gestao, if_exists='replace', index=False)
        print(f"✅ {duplicatas_gestao} duplicatas removidas da gestao_trilhas")
    
    conn_gestao.close()

def verificar_consistencia():
    """
    Verifica a consistência entre as tabelas
    """
    print("\n🔍 Verificando consistência")
    print("="*30)
    
    conn2 = sqlite3.connect('database_2.db')
    conn_gestao = sqlite3.connect('login_status.db')
    
    # Estatísticas do controle_trilhas
    df_controle = pd.read_sql_query('SELECT * FROM controle_trilhas', conn2)
    trilhas_com_codigo_controle = 0
    for _, row in df_controle.iterrows():
        if extrair_codigo_da_trilha(row['Trilhas']):
            trilhas_com_codigo_controle += 1
    
    # Estatísticas do controle_execucao
    df_exec = pd.read_sql_query('SELECT * FROM controle_execucao', conn2)
    trilhas_com_codigo_exec = 0
    for _, row in df_exec.iterrows():
        if extrair_codigo_da_trilha(row['trilha']):
            trilhas_com_codigo_exec += 1
    
    # Estatísticas da gestao_trilhas
    df_gestao = pd.read_sql_query('SELECT * FROM gestao_trilhas', conn_gestao)
    trilhas_com_codigo_gestao = 0
    for _, row in df_gestao.iterrows():
        if pd.notnull(row['Código']) and row['Código'] and row['Código'] != 'nan':
            trilhas_com_codigo_gestao += 1
    
    print(f"📊 Controle de Trilhas:")
    print(f"  - Total: {len(df_controle)}")
    print(f"  - Com código: {trilhas_com_codigo_controle}")
    print(f"  - Sem código: {len(df_controle) - trilhas_com_codigo_controle}")
    
    print(f"\n📊 Controle de Execução:")
    print(f"  - Total: {len(df_exec)}")
    print(f"  - Com código: {trilhas_com_codigo_exec}")
    print(f"  - Sem código: {len(df_exec) - trilhas_com_codigo_exec}")
    
    print(f"\n📊 Gestão de Trilhas:")
    print(f"  - Total: {len(df_gestao)}")
    print(f"  - Com código: {trilhas_com_codigo_gestao}")
    print(f"  - Sem código: {len(df_gestao) - trilhas_com_codigo_gestao}")
    
    conn2.close()
    conn_gestao.close()

def sincronizar_todas_tabelas():
    """
    Executa a sincronização completa de todas as tabelas
    """
    print("🚀 Iniciando sincronização completa das tabelas")
    print("="*55)
    print(f"⏰ Início: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    # Limpar duplicatas primeiro
    limpar_duplicatas()
    
    # Sincronizar cada tabela
    correcoes_gestao = sincronizar_gestao_trilhas()
    correcoes_controle = sincronizar_controle_trilhas()
    correcoes_exec = sincronizar_controle_execucao()
    
    # Verificar consistência final
    verificar_consistencia()
    
    total_correcoes = correcoes_gestao + correcoes_controle + correcoes_exec
    
    print(f"\n🎉 Sincronização concluída!")
    print(f"⏰ Fim: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"📊 Total de correções aplicadas: {total_correcoes}")
    
    if total_correcoes == 0:
        print("✅ Todas as tabelas já estão sincronizadas!")
    else:
        print("✅ Sincronização realizada com sucesso!")

if __name__ == "__main__":
    sincronizar_todas_tabelas() 