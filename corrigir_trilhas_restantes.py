#!/usr/bin/env python3
"""
Script para corrigir trilhas restantes que não foram encontradas na gestão
"""

import sqlite3
import pandas as pd
import re

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

def corrigir_trilhas_restantes():
    """
    Corrige trilhas restantes que não foram encontradas na gestão
    """
    print("🔧 Corrigindo trilhas restantes")
    print("="*40)
    
    conn2 = sqlite3.connect('database_2.db')
    conn_gestao = sqlite3.connect('login_status.db')
    
    # Buscar trilhas do controle
    df_controle = pd.read_sql_query('SELECT * FROM controle_trilhas', conn2)
    
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
    
    if len(trilhas_sem_codigo) > 0:
        print("\n📝 Exemplos de trilhas sem código:")
        for i, item in enumerate(trilhas_sem_codigo[:3], 1):
            print(f"  {i}. {item['trilha'][:80]}...")
        
        # Tentar encontrar correspondências parciais
        correcoes = []
        cursor = conn2.cursor()
        
        for item in trilhas_sem_codigo:
            trilha = item['trilha']
            
            # Buscar correspondências parciais na gestão
            for _, row_gestao in df_gestao.iterrows():
                trilha_gestao = row_gestao['Trilhas']
                codigo_gestao = row_gestao['Código']
                
                # Verificar se a trilha da gestão contém a trilha do controle
                if (pd.notnull(codigo_gestao) and codigo_gestao and codigo_gestao != 'nan' and
                    trilha in trilha_gestao and len(trilha) > 20):  # Evitar correspondências muito curtas
                    
                    correcoes.append({
                        'id': item['id'],
                        'trilha': trilha,
                        'codigo': codigo_gestao,
                        'trilha_gestao': trilha_gestao
                    })
                    break
        
        print(f"\n🔍 Correspondências parciais encontradas: {len(correcoes)}")
        
        if len(correcoes) > 0:
            print("\n📋 Aplicando correções:")
            
            for correcao in correcoes:
                # Criar novo nome com código
                novo_nome = f"{correcao['codigo']} - {correcao['trilha']}"
                
                # Atualizar na tabela controle_trilhas
                cursor.execute(
                    'UPDATE controle_trilhas SET "Trilhas" = ? WHERE rowid = ?',
                    (novo_nome, correcao['id'] + 1)
                )
                
                print(f"  ✅ {correcao['codigo']} - {correcao['trilha'][:50]}...")
            
            conn2.commit()
            print(f"\n✅ {len(correcoes)} correções aplicadas!")
        else:
            print("❌ Nenhuma correspondência parcial encontrada.")
    
    # Verificar resultado final
    df_controle_final = pd.read_sql_query('SELECT * FROM controle_trilhas', conn2)
    
    # Contar trilhas com código
    trilhas_com_codigo = 0
    for _, row in df_controle_final.iterrows():
        nome_trilha = row['Trilhas']
        if extrair_codigo_da_trilha(nome_trilha):
            trilhas_com_codigo += 1
    
    print(f"\n📊 Resultado final:")
    print(f"  - Total de trilhas: {len(df_controle_final)}")
    print(f"  - Trilhas com código: {trilhas_com_codigo}")
    print(f"  - Trilhas sem código: {len(df_controle_final) - trilhas_com_codigo}")
    
    # Mostrar exemplos de trilhas com código
    print(f"\n📝 Exemplos de trilhas com código:")
    count = 0
    for _, row in df_controle_final.iterrows():
        if count >= 5:
            break
        nome_trilha = row['Trilhas']
        if extrair_codigo_da_trilha(nome_trilha):
            print(f"  {count + 1}. {nome_trilha}")
            count += 1
    
    # Mostrar trilhas que ainda estão sem código
    trilhas_sem_codigo_final = []
    for _, row in df_controle_final.iterrows():
        nome_trilha = row['Trilhas']
        if not extrair_codigo_da_trilha(nome_trilha):
            trilhas_sem_codigo_final.append(nome_trilha)
    
    if trilhas_sem_codigo_final:
        print(f"\n⚠️ Trilhas que ainda estão sem código:")
        for i, trilha in enumerate(trilhas_sem_codigo_final[:3], 1):
            print(f"  {i}. {trilha}")
    
    conn2.close()
    conn_gestao.close()

if __name__ == "__main__":
    corrigir_trilhas_restantes() 