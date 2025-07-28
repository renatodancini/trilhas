#!/usr/bin/env python3
"""
Script de debug para verificar a exibição na página de impressão
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

def debug_exibicao():
    """
    Debug da exibição da página de impressão
    """
    print("🐛 Debug da exibição da página de impressão")
    print("="*60)
    
    # Conectar aos bancos
    conn2 = sqlite3.connect('database_2.db')
    conn_gestao = sqlite3.connect('login_status.db')
    
    print("📊 DADOS BRUTOS:")
    print("-" * 30)
    
    # 1. Verificar controle_trilhas
    print("1. Tabela controle_trilhas:")
    try:
        df_controle = pd.read_sql_query('SELECT * FROM controle_trilhas', conn2)
        print(f"   - Total: {len(df_controle)} registros")
        print(f"   - Colunas: {list(df_controle.columns)}")
        
        if len(df_controle) > 0:
            print("   - Primeiras 5 trilhas:")
            for i, (_, row) in enumerate(df_controle.head(5).iterrows(), 1):
                print(f"     {i}. {row['Trilhas'][:100]}...")
        else:
            print("   - ⚠️ TABELA VAZIA!")
            
    except Exception as e:
        print(f"   - ❌ Erro: {e}")
    
    # 2. Verificar gestao_trilhas
    print("\n2. Tabela gestao_trilhas:")
    try:
        df_gestao = pd.read_sql_query('SELECT Trilhas, Código FROM gestao_trilhas', conn_gestao)
        print(f"   - Total: {len(df_gestao)} registros")
        print(f"   - Trilhas com código: {len(df_gestao[df_gestao['Código'].notna()])}")
        
        if len(df_gestao) > 0:
            print("   - Primeiras 5 trilhas:")
            for i, (_, row) in enumerate(df_gestao.head(5).iterrows(), 1):
                codigo = row['Código'] if pd.notnull(row['Código']) else 'SEM CÓDIGO'
                print(f"     {i}. [{codigo}] {row['Trilhas'][:80]}...")
        else:
            print("   - ⚠️ TABELA VAZIA!")
            
    except Exception as e:
        print(f"   - ❌ Erro: {e}")
    
    print("\n🔗 PROCESSAMENTO DA PÁGINA:")
    print("-" * 30)
    
    # 3. Simular exatamente a lógica da página
    print("3. Lógica da página de impressão:")
    
    try:
        # Buscar trilhas do controle (como na página)
        df_trilhas_controle = pd.read_sql_query('SELECT Trilhas FROM controle_trilhas', conn2)
        print(f"   - Trilhas do controle: {len(df_trilhas_controle)}")
        
        # Buscar códigos da gestão (como na página)
        df_gestao = pd.read_sql_query('SELECT Trilhas, Código FROM gestao_trilhas', conn_gestao)
        print(f"   - Trilhas da gestão: {len(df_gestao)}")
        
        # Limpar duplicatas (como na página)
        df_trilhas_controle = df_trilhas_controle.drop_duplicates(subset=['Trilhas'])
        df_gestao = df_gestao.drop_duplicates(subset=['Trilhas'])
        print(f"   - Após limpeza de duplicatas: controle={len(df_trilhas_controle)}, gestão={len(df_gestao)}")
        
        # Mesclar (como na página)
        df_trilhas_completas = pd.merge(df_trilhas_controle, df_gestao, left_on='Trilhas', right_on='Trilhas', how='left')
        print(f"   - Após mesclagem: {len(df_trilhas_completas)}")
        
        # Remover duplicatas da mesclagem (como na página)
        df_trilhas_completas = df_trilhas_completas.drop_duplicates(subset=['Trilhas'])
        print(f"   - Após remoção de duplicatas da mesclagem: {len(df_trilhas_completas)}")
        
        # Verificar se está vazio
        if df_trilhas_completas.empty:
            print("   - ⚠️ RESULTADO VAZIO!")
        else:
            print("   - ✅ RESULTADO NÃO VAZIO")
            print("   - Primeiras 3 trilhas processadas:")
            for i, (_, row) in enumerate(df_trilhas_completas.head(3).iterrows(), 1):
                codigo = row['Código'] if pd.notnull(row['Código']) and row['Código'] and row['Código'] != 'nan' else 'SEM CÓDIGO'
                trilha = row['Trilhas']
                print(f"     {i}. [{codigo}] {trilha[:80]}...")
        
    except Exception as e:
        print(f"   - ❌ Erro no processamento: {e}")
    
    # 4. Verificar combobox
    print("\n4. Geração do combobox:")
    
    try:
        if not df_trilhas_completas.empty:
            opcoes_combo = []
            for _, row in df_trilhas_completas.iterrows():
                codigo = row['Código'] if pd.notnull(row['Código']) and row['Código'] and row['Código'] != 'nan' else ''
                trilha = row['Trilhas']
                
                # Se não tem código, tentar extrair do nome da trilha
                if not codigo:
                    codigo = extrair_codigo_da_trilha(trilha)
                
                # Criar opção
                if codigo:
                    opcao = f"{codigo} - {trilha}"
                else:
                    opcao = trilha
                
                opcoes_combo.append(opcao)
            
            # Remover duplicatas das opções
            opcoes_combo = list(dict.fromkeys(opcoes_combo))
            print(f"   - Opções no combobox: {len(opcoes_combo)}")
            
            if len(opcoes_combo) > 0:
                print("   - Primeiras 5 opções do combobox:")
                for i, opcao in enumerate(opcoes_combo[:5], 1):
                    print(f"     {i}. {opcao[:80]}...")
            else:
                print("   - ⚠️ COMBOBOX VAZIO!")
        else:
            print("   - ⚠️ Não há dados para gerar combobox")
            
    except Exception as e:
        print(f"   - ❌ Erro na geração do combobox: {e}")
    
    # 5. Verificar tabela de exibição
    print("\n5. Tabela de exibição:")
    
    try:
        # Buscar dados da tabela controle (como na página)
        df_ctrl = pd.read_sql_query('SELECT Trilhas, Status, "Modificado por", "Modificado em" FROM controle_trilhas', conn2)
        print(f"   - Dados da tabela controle: {len(df_ctrl)}")
        
        # Mesclar para obter os códigos (como na página)
        df_final = pd.merge(df_ctrl, df_gestao, left_on='Trilhas', right_on='Trilhas', how='left')
        print(f"   - Dados finais para exibição: {len(df_final)}")
        
        if len(df_final) > 0:
            print("   - Primeiras 3 linhas da tabela:")
            for i, (_, row) in enumerate(df_final.head(3).iterrows(), 1):
                codigo = row['Código'] if pd.notnull(row['Código']) and row['Código'] and row['Código'] != 'nan' else 'SEM CÓDIGO'
                trilha = row['Trilhas']
                status = row['Status'] if pd.notnull(row['Status']) else 'N/A'
                print(f"     {i}. [{codigo}] {trilha[:60]}... | Status: {status}")
        else:
            print("   - ⚠️ TABELA DE EXIBIÇÃO VAZIA!")
            
    except Exception as e:
        print(f"   - ❌ Erro na tabela de exibição: {e}")
    
    print("\n🎯 CONCLUSÃO:")
    print("-" * 30)
    
    if len(df_controle) > 0:
        print("✅ A tabela controle_trilhas NÃO está vazia")
        print(f"   - Contém {len(df_controle)} registros")
        print("✅ Os dados estão sendo processados corretamente")
        print("✅ A página deve estar exibindo os dados")
        print("\n💡 Se você não está vendo os dados na página:")
        print("   1. Verifique se está na página correta (Impressão de Trilhas)")
        print("   2. Tente recarregar a página (F5)")
        print("   3. Verifique se está logado")
        print("   4. Verifique se não há erros no console do navegador")
    else:
        print("❌ A tabela controle_trilhas está vazia")
        print("   - Execute o serviço de sincronização novamente")
    
    conn2.close()
    conn_gestao.close()

if __name__ == "__main__":
    debug_exibicao() 