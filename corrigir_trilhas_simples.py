#!/usr/bin/env python3
"""
Script simples para corrigir trilhas sem código na tabela controle_trilhas
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

def corrigir_trilhas_simples():
    """
    Corrige trilhas sem código de forma simples
    """
    print("🔧 Corrigindo trilhas de forma simples")
    print("="*45)
    
    # Conectar ao database_2.db
    conn2 = sqlite3.connect('database_2.db')
    
    # Buscar todas as trilhas do controle
    df_controle = pd.read_sql_query('SELECT * FROM controle_trilhas', conn2)
    print(f"📊 Total de trilhas no controle: {len(df_controle)}")
    
    # Identificar trilhas sem código no nome
    trilhas_sem_codigo = []
    for idx, row in df_controle.iterrows():
        nome_trilha = row['Trilhas']
        codigo_extraido = extrair_codigo_da_trilha(nome_trilha)
        
        if not codigo_extraido:
            trilhas_sem_codigo.append({
                'id': idx,
                'trilha': nome_trilha
            })
    
    print(f"❌ Trilhas sem código no nome: {len(trilhas_sem_codigo)}")
    
    if len(trilhas_sem_codigo) > 0:
        print("\n📝 Exemplos de trilhas sem código:")
        for i, item in enumerate(trilhas_sem_codigo[:3], 1):
            print(f"  {i}. {item['trilha'][:80]}...")
        
        # Buscar códigos correspondentes no banco de gestão
        conn_gestao = sqlite3.connect('login_status.db')
        df_gestao = pd.read_sql_query('SELECT Trilhas, Código FROM gestao_trilhas', conn_gestao)
        conn_gestao.close()
        
        # Tentar encontrar códigos correspondentes
        correcoes = []
        for item in trilhas_sem_codigo:
            trilha = item['trilha']
            
            # Buscar na tabela de gestão (busca exata)
            match_gestao = df_gestao[df_gestao['Trilhas'] == trilha]
            
            if not match_gestao.empty:
                codigo_gestao = match_gestao.iloc[0]['Código']
                if pd.notnull(codigo_gestao) and codigo_gestao and codigo_gestao != 'nan':
                    correcoes.append({
                        'id': item['id'],
                        'trilha': trilha,
                        'codigo': codigo_gestao,
                        'fonte': 'gestao'
                    })
        
        print(f"\n🔍 Correções encontradas: {len(correcoes)}")
        
        if len(correcoes) > 0:
            print("\n📋 Aplicando correções:")
            cursor = conn2.cursor()
            
            for correcao in correcoes:
                # Criar novo nome com código
                novo_nome = f"{correcao['codigo']} - {correcao['trilha']}"
                
                # Atualizar na tabela controle_trilhas
                cursor.execute(
                    'UPDATE controle_trilhas SET "Trilhas" = ? WHERE rowid = ?',
                    (novo_nome, correcao['id'] + 1)  # +1 porque rowid começa em 1
                )
                
                print(f"  ✅ {correcao['codigo']} - {correcao['trilha'][:50]}... ({correcao['fonte']})")
            
            conn2.commit()
            print(f"\n✅ {len(correcoes)} correções aplicadas!")
        else:
            print("❌ Nenhuma correção pôde ser aplicada.")
    
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
    
    conn2.close()

if __name__ == "__main__":
    corrigir_trilhas_simples() 