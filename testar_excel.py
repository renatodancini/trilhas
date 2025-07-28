#!/usr/bin/env python3
"""
Script para testar a função de geração do Excel corrigida
"""

import sqlite3
import pandas as pd
from utils import gerar_xlsx_trilha

def testar_geracao_excel():
    """
    Testa a geração do Excel para algumas trilhas
    """
    print("🧪 Testando geração do Excel")
    print("="*40)
    
    # Conectar ao banco
    conn = sqlite3.connect('login_status.db')
    
    # Buscar algumas trilhas para testar
    print("📊 Buscando trilhas para teste:")
    try:
        trilhas_teste = pd.read_sql_query(
            '''SELECT DISTINCT Trilhas 
               FROM gestao_trilhas 
               WHERE Trilhas LIKE "CMR%" 
               AND Atividade IS NOT NULL 
               AND Atividade != "Atividade" 
               AND Atividade != ""
               LIMIT 3''',
            conn
        )
        
        print(f"  - Trilhas encontradas para teste: {len(trilhas_teste)}")
        
        if len(trilhas_teste) > 0:
            for i, (_, row) in enumerate(trilhas_teste.iterrows(), 1):
                trilha = row['Trilhas']
                print(f"  {i}. {trilha[:80]}...")
                
                # Extrair código da trilha
                import re
                padrao = r'^(CMR\s*\d+\.?\d*)'
                match = re.search(padrao, trilha, re.IGNORECASE)
                codigo = match.group(1).strip() if match else ''
                
                # Testar geração do Excel
                print(f"    - Código extraído: {codigo}")
                print(f"    - Testando geração do Excel...")
                
                try:
                    xlsx_bytes = gerar_xlsx_trilha(trilha, codigo)
                    print(f"    - ✅ Excel gerado com sucesso! Tamanho: {len(xlsx_bytes)} bytes")
                    
                    # Salvar arquivo de teste
                    nome_arquivo = f"teste_trilha_{i}.xlsx"
                    with open(nome_arquivo, 'wb') as f:
                        f.write(xlsx_bytes)
                    print(f"    - 📁 Arquivo salvo como: {nome_arquivo}")
                    
                except Exception as e:
                    print(f"    - ❌ Erro ao gerar Excel: {e}")
                
                print()
        else:
            print("  - ⚠️ Nenhuma trilha válida encontrada para teste")
            
    except Exception as e:
        print(f"  - ❌ Erro ao buscar trilhas: {e}")
    
    # Testar com uma trilha específica do controle
    print("📊 Testando com trilha do controle:")
    try:
        conn2 = sqlite3.connect('database_2.db')
        trilha_controle = pd.read_sql_query(
            'SELECT Trilhas FROM controle_trilhas WHERE Trilhas LIKE "CMR%" LIMIT 1',
            conn2
        )
        
        if len(trilha_controle) > 0:
            trilha = trilha_controle.iloc[0]['Trilhas']
            print(f"  - Trilha do controle: {trilha[:80]}...")
            
            # Extrair código
            import re
            padrao = r'^(CMR\s*\d+\.?\d*)'
            match = re.search(padrao, trilha, re.IGNORECASE)
            codigo = match.group(1).strip() if match else ''
            
            print(f"  - Código extraído: {codigo}")
            print(f"  - Testando geração do Excel...")
            
            try:
                xlsx_bytes = gerar_xlsx_trilha(trilha, codigo)
                print(f"  - ✅ Excel gerado com sucesso! Tamanho: {len(xlsx_bytes)} bytes")
                
                # Salvar arquivo de teste
                nome_arquivo = "teste_trilha_controle.xlsx"
                with open(nome_arquivo, 'wb') as f:
                    f.write(xlsx_bytes)
                print(f"  - 📁 Arquivo salvo como: {nome_arquivo}")
                
            except Exception as e:
                print(f"  - ❌ Erro ao gerar Excel: {e}")
        
        conn2.close()
        
    except Exception as e:
        print(f"  - ❌ Erro ao testar trilha do controle: {e}")
    
    conn.close()

if __name__ == "__main__":
    testar_geracao_excel() 