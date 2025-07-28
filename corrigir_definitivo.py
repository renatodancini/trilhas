#!/usr/bin/env python3
"""
Script definitivo para corrigir todos os problemas restantes
- Trilhas sem código
- Duplicações
- Códigos duplicados nos nomes
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

def limpar_nome_trilha(nome_trilha):
    """
    Remove códigos duplicados e limpa o nome da trilha
    """
    if pd.isna(nome_trilha) or not nome_trilha:
        return nome_trilha
    
    nome = str(nome_trilha)
    
    # Remover códigos duplicados no início
    codigo = extrair_codigo_da_trilha(nome)
    if codigo:
        # Remover o código do início
        nome_sem_codigo = re.sub(r'^CMR\s*\d+\.?\d*\s*-\s*', '', nome, flags=re.IGNORECASE)
        
        # Remover códigos duplicados no meio ou fim
        nome_limpo = re.sub(r'\s*CMR\s*\d+\.?\d*\s*-\s*', ' - ', nome_sem_codigo, flags=re.IGNORECASE)
        
        return nome_limpo.strip()
    
    return nome.strip()

def corrigir_definitivo():
    """
    Corrige definitivamente todos os problemas
    """
    print("🔧 Correção definitiva das trilhas")
    print("="*45)
    
    conn2 = sqlite3.connect('database_2.db')
    conn_gestao = sqlite3.connect('login_status.db')
    
    # Buscar trilhas do controle
    df_controle = pd.read_sql_query('SELECT * FROM controle_trilhas', conn2)
    print(f"📊 Total de trilhas no controle: {len(df_controle)}")
    
    # Buscar códigos da gestão
    df_gestao = pd.read_sql_query('SELECT Trilhas, Código FROM gestao_trilhas', conn_gestao)
    
    # Processar cada trilha
    correcoes = []
    cursor = conn2.cursor()
    
    for idx, row in df_controle.iterrows():
        nome_trilha = row['Trilhas']
        codigo_atual = extrair_codigo_da_trilha(nome_trilha)
        
        # Limpar o nome da trilha
        nome_limpo = limpar_nome_trilha(nome_trilha)
        
        # Se não tem código, tentar encontrar na gestão
        if not codigo_atual:
            # Buscar correspondência exata
            match_gestao = df_gestao[df_gestao['Trilhas'] == nome_limpo]
            
            if not match_gestao.empty:
                codigo_gestao = match_gestao.iloc[0]['Código']
                if pd.notnull(codigo_gestao) and codigo_gestao and codigo_gestao != 'nan':
                    codigo_atual = codigo_gestao
            else:
                # Buscar correspondência parcial
                for _, row_gestao in df_gestao.iterrows():
                    trilha_gestao = row_gestao['Trilhas']
                    codigo_gestao = row_gestao['Código']
                    
                    # Verificar se a trilha da gestão contém palavras-chave da trilha do controle
                    palavras_chave = nome_limpo.split(' - ')[0:2]  # Primeiras duas partes
                    if (pd.notnull(codigo_gestao) and codigo_gestao and codigo_gestao != 'nan' and
                        all(palavra in trilha_gestao for palavra in palavras_chave if len(palavra) > 3)):
                        codigo_atual = codigo_gestao
                        break
        
        # Se encontrou código, criar novo nome
        if codigo_atual:
            novo_nome = f"{codigo_atual} - {nome_limpo}"
            correcoes.append({
                'id': idx,
                'nome_original': nome_trilha,
                'nome_novo': novo_nome,
                'codigo': codigo_atual
            })
    
    print(f"🔍 Correções encontradas: {len(correcoes)}")
    
    if len(correcoes) > 0:
        print("\n📋 Aplicando correções:")
        
        for correcao in correcoes:
            # Atualizar na tabela controle_trilhas
            cursor.execute(
                'UPDATE controle_trilhas SET "Trilhas" = ? WHERE rowid = ?',
                (correcao['nome_novo'], correcao['id'] + 1)
            )
            
            print(f"  ✅ {correcao['codigo']} - {correcao['nome_novo'][:50]}...")
        
        conn2.commit()
        print(f"\n✅ {len(correcoes)} correções aplicadas!")
    
    # Remover duplicatas finais
    df_controle_final = pd.read_sql_query('SELECT * FROM controle_trilhas', conn2)
    duplicatas = len(df_controle_final[df_controle_final.duplicated(subset=['Trilhas'], keep=False)])
    
    if duplicatas > 0:
        print(f"\n🧹 Removendo {duplicatas} duplicatas finais...")
        df_controle_limpo = df_controle_final.drop_duplicates(subset=['Trilhas'], keep='first')
        df_controle_limpo.to_sql('controle_trilhas', conn2, if_exists='replace', index=False)
        print(f"✅ Duplicatas removidas! Registros restantes: {len(df_controle_limpo)}")
    
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
    corrigir_definitivo() 