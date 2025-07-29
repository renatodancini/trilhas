#!/usr/bin/env python3
"""
Script para testar se as categorias estão sendo buscadas corretamente do banco database_trilhas.db
"""

import pandas as pd
import sqlite3
import os
import re

def testar_categorias_banco():
    """Testa a busca de categorias no banco database_trilhas.db"""
    
    print("=== TESTE DE CATEGORIAS NO BANCO DE DADOS ===")
    
    # Caminho do banco
    db_path = os.path.join("Impressão de trilhas", "database_trilhas.db")
    
    if not os.path.exists(db_path):
        print(f"❌ Banco de dados não encontrado: {db_path}")
        return False
    
    print(f"✅ Banco encontrado: {db_path}")
    
    try:
        # Conectar ao banco
        conn = sqlite3.connect(db_path)
        
        # Verificar se a tabela trilhas existe
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='trilhas'")
        if not cursor.fetchone():
            print("❌ Tabela 'trilhas' não encontrada no banco")
            conn.close()
            return False
        
        print("✅ Tabela 'trilhas' encontrada")
        
        # Buscar trilhas
        df = pd.read_sql_query('SELECT DISTINCT Trilhas FROM trilhas WHERE Trilhas IS NOT NULL AND Trilhas != ""', conn)
        conn.close()
        
        if df.empty:
            print("❌ Nenhuma trilha encontrada no banco")
            return False
        
        print(f"✅ {len(df)} trilhas únicas encontradas")
        
        # Mostrar trilhas
        print("\n📋 Trilhas encontradas:")
        for i, trilha in enumerate(df['Trilhas'], 1):
            print(f"{i}. {trilha}")
        
        # Extrair categorias
        print("\n🔍 Extração de categorias:")
        categorias = set()
        for trilha in df['Trilhas']:
            if trilha and len(trilha) >= 3:
                # Padrão para códigos de trilha: 3 letras seguidas de números
                padrao = r'^([A-Z]{3})\d+'
                match = re.search(padrao, str(trilha).upper())
                if match:
                    categoria = match.group(1)
                    categorias.add(categoria)
                    print(f"  {trilha} → {categoria}")
                else:
                    # Fallback
                    categoria = trilha[:3].upper()
                    categorias.add(categoria)
                    print(f"  {trilha} → {categoria} (fallback)")
        
        categorias_ordenadas = sorted(list(categorias))
        print(f"\n📂 Categorias únicas encontradas: {categorias_ordenadas}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao acessar banco: {e}")
        return False

def testar_funcao_obter_categorias():
    """Testa a função obter_categorias_disponiveis"""
    
    print("\n=== TESTE DA FUNÇÃO obter_categorias_disponiveis ===")
    
    try:
        from utils import obter_categorias_disponiveis
        
        categorias = obter_categorias_disponiveis()
        
        if categorias:
            print(f"✅ Função retornou {len(categorias)} categorias:")
            for cat in categorias:
                print(f"  • {cat}")
        else:
            print("❌ Função não retornou categorias")
            
        return categorias
        
    except Exception as e:
        print(f"❌ Erro ao testar função: {e}")
        return []

if __name__ == "__main__":
    # Testar acesso direto ao banco
    sucesso_banco = testar_categorias_banco()
    
    # Testar função
    categorias_funcao = testar_funcao_obter_categorias()
    
    if sucesso_banco and categorias_funcao:
        print("\n🎉 Teste concluído com sucesso!")
        print("✅ Categorias estão sendo buscadas corretamente do banco database_trilhas.db")
    else:
        print("\n❌ Teste falhou!")
        print("⚠️ Verifique se o banco database_trilhas.db existe e contém trilhas") 