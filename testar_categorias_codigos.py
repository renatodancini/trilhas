#!/usr/bin/env python3
"""
Script para testar a extração de categorias baseada nos códigos das trilhas
"""

import pandas as pd
import re

def extrair_codigo_categoria(trilha):
    """Função para extrair código de categoria de uma trilha"""
    if not trilha or len(trilha) < 3:
        return None
    
    # Padrão para códigos de trilha: 3 letras seguidas de números
    padrao = r'^([A-Z]{3})\d+'
    match = re.search(padrao, str(trilha).upper())
    if match:
        return match.group(1)  # Retorna as 3 letras do código
    else:
        # Fallback: usar as 3 primeiras letras
        return trilha[:3].upper()

def testar_extracao_categorias():
    """Testa a extração de categorias com dados de exemplo"""
    
    # Dados de teste com diferentes formatos de trilhas
    trilhas_teste = [
        "CMR205.1 - Trilha de Compras",
        "ORG123 - Trilha Organizacional", 
        "SUP456 - Trilha de Suporte",
        "ADM789 - Trilha Administrativa",
        "FIN101 - Trilha Financeira",
        "RH202 - Trilha de Recursos Humanos",
        "TEC303 - Trilha Técnica",
        "LOG404 - Trilha de Logística",
        "MKT505 - Trilha de Marketing",
        "VND606 - Trilha de Vendas"
    ]
    
    print("=== TESTE DE EXTRAÇÃO DE CATEGORIAS ===")
    print("\n📋 Trilhas de teste:")
    for i, trilha in enumerate(trilhas_teste, 1):
        print(f"{i}. {trilha}")
    
    print("\n🔍 Extração de códigos de categoria:")
    print("=" * 60)
    
    categorias_extraidas = set()
    for trilha in trilhas_teste:
        codigo = extrair_codigo_categoria(trilha)
        categorias_extraidas.add(codigo)
        print(f"Trilha: {trilha}")
        print(f"Código: {codigo}")
        print("-" * 40)
    
    print(f"\n📂 Categorias únicas encontradas: {sorted(list(categorias_extraidas))}")
    
    # Testar filtro por categoria
    print("\n🧪 Teste de filtro por categoria:")
    print("=" * 60)
    
    # Simular DataFrame
    df_teste = pd.DataFrame({'Trilhas': trilhas_teste})
    
    # Testar filtro para categoria CMR
    categorias_usuario = ['CMR']
    df_filtrado = df_teste[df_teste['Trilhas'].apply(
        lambda x: extrair_codigo_categoria(x) in categorias_usuario
    )]
    
    print(f"Filtro para categoria 'CMR':")
    for _, row in df_filtrado.iterrows():
        print(f"  ✅ {row['Trilhas']}")
    
    # Testar filtro para múltiplas categorias
    categorias_usuario = ['CMR', 'ORG', 'SUP']
    df_filtrado = df_teste[df_teste['Trilhas'].apply(
        lambda x: extrair_codigo_categoria(x) in categorias_usuario
    )]
    
    print(f"\nFiltro para categorias 'CMR', 'ORG', 'SUP':")
    for _, row in df_filtrado.iterrows():
        print(f"  ✅ {row['Trilhas']}")
    
    print(f"\n✅ Teste concluído! {len(categorias_extraidas)} categorias únicas encontradas.")
    
    return sorted(list(categorias_extraidas))

if __name__ == "__main__":
    categorias = testar_extracao_categorias() 