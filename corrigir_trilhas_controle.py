#!/usr/bin/env python3
"""
Script para corrigir trilhas sem código na tabela controle_trilhas
Adiciona códigos extraídos dos nomes das trilhas
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

def corrigir_trilhas_controle():
    """
    Corrige trilhas sem código na tabela controle_trilhas
    """
    print("🔧 Corrigindo trilhas na tabela controle_trilhas")
    print("="*50)
    
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
        for i, item in enumerate(trilhas_sem_codigo[:5], 1):
            print(f"  {i}. {item['trilha']}")
        
        # Buscar códigos correspondentes no banco de gestão
        conn_gestao = sqlite3.connect('login_status.db')
        df_gestao = pd.read_sql_query('SELECT Trilhas, Código FROM gestao_trilhas', conn_gestao)
        conn_gestao.close()
        
        # Tentar encontrar códigos correspondentes
        correcoes = []
        for item in trilhas_sem_codigo:
            trilha = item['trilha']
            
            # Buscar na tabela de gestão
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
            else:
                # Tentar extrair código do nome
                codigo_extraido = extrair_codigo_da_trilha(trilha)
                if codigo_extraido:
                    correcoes.append({
                        'id': item['id'],
                        'trilha': trilha,
                        'codigo': codigo_extraido,
                        'fonte': 'extraido'
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
                
                print(f"  ✅ {correcao['trilha']} → {novo_nome} ({correcao['fonte']})")
            
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

def verificar_duplicatas():
    """
    Verifica e remove duplicatas na tabela controle_trilhas
    """
    print("\n🧹 Verificando duplicatas na tabela controle_trilhas")
    print("="*55)
    
    conn2 = sqlite3.connect('database_2.db')
    df_controle = pd.read_sql_query('SELECT * FROM controle_trilhas', conn2)
    
    # Identificar duplicatas
    duplicatas = df_controle[df_controle.duplicated(subset=['Trilhas'], keep=False)]
    
    if len(duplicatas) > 0:
        print(f"📊 Duplicatas encontradas: {len(duplicatas)}")
        print("📝 Exemplos de duplicatas:")
        for i, (_, row) in enumerate(duplicatas.head(5).iterrows(), 1):
            print(f"  {i}. {row['Trilhas']}")
        
        # Remover duplicatas
        df_controle_limpo = df_controle.drop_duplicates(subset=['Trilhas'], keep='first')
        df_controle_limpo.to_sql('controle_trilhas', conn2, if_exists='replace', index=False)
        
        print(f"✅ Duplicatas removidas! Registros restantes: {len(df_controle_limpo)}")
    else:
        print("✅ Nenhuma duplicata encontrada!")
    
    conn2.close()

if __name__ == "__main__":
    verificar_duplicatas()
    corrigir_trilhas_controle() 