#!/usr/bin/env python3
"""
Script para limpar duplicações finais e aplicar códigos
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

def limpar_duplicacoes_finais():
    """
    Limpa duplicações finais e aplica códigos
    """
    print("🧹 Limpando duplicações finais")
    print("="*40)
    
    conn2 = sqlite3.connect('database_2.db')
    conn_gestao = sqlite3.connect('login_status.db')
    
    # Buscar trilhas do controle
    df_controle = pd.read_sql_query('SELECT * FROM controle_trilhas', conn2)
    print(f"📊 Total de trilhas no controle: {len(df_controle)}")
    
    # Buscar códigos da gestão
    df_gestao = pd.read_sql_query('SELECT Trilhas, Código FROM gestao_trilhas', conn_gestao)
    
    # Identificar duplicações (nomes que se repetem)
    nomes_duplicados = df_controle[df_controle.duplicated(subset=['Trilhas'], keep=False)]
    print(f"📊 Trilhas com nomes duplicados: {len(nomes_duplicados)}")
    
    if len(nomes_duplicados) > 0:
        print("\n📝 Exemplos de duplicações:")
        for i, (_, row) in enumerate(nomes_duplicados.head(3).iterrows(), 1):
            print(f"  {i}. {row['Trilhas'][:80]}...")
        
        # Remover duplicações mantendo apenas a primeira ocorrência
        df_controle_limpo = df_controle.drop_duplicates(subset=['Trilhas'], keep='first')
        df_controle_limpo.to_sql('controle_trilhas', conn2, if_exists='replace', index=False)
        
        print(f"✅ Duplicações removidas! Registros restantes: {len(df_controle_limpo)}")
    
    # Recarregar dados limpos
    df_controle = pd.read_sql_query('SELECT * FROM controle_trilhas', conn2)
    
    # Identificar trilhas sem código
    trilhas_sem_codigo = []
    for idx, row in df_controle.iterrows():
        nome_trilha = row['Trilhas']
        codigo_extraido = extrair_codigo_da_trilha(nome_trilha)
        
        if not codigo_extraido:
            trilhas_sem_codigo.append({
                'id': idx,
                'trilha': nome_trilha
            })
    
    print(f"\n❌ Trilhas sem código após limpeza: {len(trilhas_sem_codigo)}")
    
    if len(trilhas_sem_codigo) > 0:
        print("\n📝 Exemplos de trilhas sem código:")
        for i, item in enumerate(trilhas_sem_codigo[:3], 1):
            print(f"  {i}. {item['trilha'][:80]}...")
        
        # Tentar encontrar códigos baseados em correspondências inteligentes
        correcoes = []
        cursor = conn2.cursor()
        
        for item in trilhas_sem_codigo:
            trilha = item['trilha']
            
            # Remover duplicações do nome da trilha
            trilha_limpa = trilha
            if trilha.count(trilha.split(' - ')[0]) > 1:
                # Se há duplicação, pegar apenas a primeira parte
                trilha_limpa = trilha.split(' - ')[0] + ' - ' + ' - '.join(trilha.split(' - ')[1:])
            
            # Buscar na gestão com o nome limpo
            match_gestao = df_gestao[df_gestao['Trilhas'] == trilha_limpa]
            
            if not match_gestao.empty:
                codigo_gestao = match_gestao.iloc[0]['Código']
                if pd.notnull(codigo_gestao) and codigo_gestao and codigo_gestao != 'nan':
                    correcoes.append({
                        'id': item['id'],
                        'trilha': trilha,
                        'trilha_limpa': trilha_limpa,
                        'codigo': codigo_gestao
                    })
            else:
                # Tentar correspondência parcial mais inteligente
                for _, row_gestao in df_gestao.iterrows():
                    trilha_gestao = row_gestao['Trilhas']
                    codigo_gestao = row_gestao['Código']
                    
                    # Verificar se a trilha da gestão contém palavras-chave da trilha do controle
                    palavras_chave = trilha_limpa.split(' - ')[0:2]  # Primeiras duas partes
                    if (pd.notnull(codigo_gestao) and codigo_gestao and codigo_gestao != 'nan' and
                        all(palavra in trilha_gestao for palavra in palavras_chave if len(palavra) > 3)):
                        
                        correcoes.append({
                            'id': item['id'],
                            'trilha': trilha,
                            'trilha_limpa': trilha_limpa,
                            'codigo': codigo_gestao,
                            'trilha_gestao': trilha_gestao
                        })
                        break
        
        print(f"\n🔍 Correções encontradas: {len(correcoes)}")
        
        if len(correcoes) > 0:
            print("\n📋 Aplicando correções:")
            
            for correcao in correcoes:
                # Criar novo nome com código
                novo_nome = f"{correcao['codigo']} - {correcao['trilha_limpa']}"
                
                # Atualizar na tabela controle_trilhas
                cursor.execute(
                    'UPDATE controle_trilhas SET "Trilhas" = ? WHERE rowid = ?',
                    (novo_nome, correcao['id'] + 1)
                )
                
                print(f"  ✅ {correcao['codigo']} - {correcao['trilha_limpa'][:50]}...")
            
            conn2.commit()
            print(f"\n✅ {len(correcoes)} correções aplicadas!")
        else:
            print("❌ Nenhuma correção encontrada.")
    
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
    conn_gestao.close()

if __name__ == "__main__":
    limpar_duplicacoes_finais() 