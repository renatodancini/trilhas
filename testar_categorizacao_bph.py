#!/usr/bin/env python3
"""
Script para testar a categorização BPH das atividades
"""

import pandas as pd
import re

def extrair_codigo_bph(atividade):
    """Função para extrair código BPH completo"""
    import re
    # Procurar por BPH seguido de números
    match = re.search(r'BPH(\d+)', atividade)
    if match:
        return f"BPH{match.group(1)}"
    return "Sem BPH"

def extrair_numero_bph(atividade):
    """Função para extrair número BPH para ordenação"""
    import re
    # Procurar por BPH seguido de números
    match = re.search(r'BPH(\d+)', atividade)
    if match:
        return int(match.group(1))
    return 0  # Se não encontrar BPH, colocar no início

def testar_categorizacao_bph():
    """Testa a categorização BPH com dados de exemplo"""
    
    # Dados de teste baseados no exemplo da imagem
    atividades_teste = [
        "CMR205.1 - BPH003890 - 1. Aprovar contrato de Compras",
        "CMR205.1 - BPH003890 - 2. Consultar aprovação de workflow",
        "CMR205.1 - BPH004040 - 3. Validar dados da nota fiscal",
        "CMR205.1 - BPH003890 - 4. Verificar documentação",
        "CMR205.1 - BPH004040 - 5. Processar pagamento",
        "CMR205.1 - BPH005123 - 6. Finalizar processo"
    ]
    
    # Criar DataFrame de teste
    df_teste = pd.DataFrame({
        'Atividades': atividades_teste,
        'Responsável': ['João', 'Maria', 'Pedro', 'Ana', 'Carlos', 'Lucia'],
        'Tipo': ['A', 'B', 'C', 'A', 'B', 'C'],
        'Finalizado': ['Não', 'Sim', 'Não', 'Sim', 'Não', 'Sim'],
        'Observações': ['Obs 1', 'Obs 2', 'Obs 3', 'Obs 4', 'Obs 5', 'Obs 6']
    })
    
    print("=== TESTE DE CATEGORIZAÇÃO BPH ===")
    print("\n📋 Atividades ANTES da categorização:")
    for i, atividade in enumerate(df_teste['Atividades'], 1):
        print(f"{i}. {atividade}")
    
    # Aplicar categorização BPH
    df_teste['codigo_bph'] = df_teste['Atividades'].apply(extrair_codigo_bph)
    df_teste['numero_bph'] = df_teste['Atividades'].apply(extrair_numero_bph)
    
    # Ordenar por código BPH e depois por número BPH
    df_teste = df_teste.sort_values(['codigo_bph', 'numero_bph'])
    
    print("\n📋 Atividades DEPOIS da categorização:")
    print("=" * 80)
    
    # Agrupar e mostrar por categoria
    grupos_bph = df_teste.groupby('codigo_bph')
    
    for codigo_bph, grupo in grupos_bph:
        if codigo_bph != "Sem BPH":
            print(f"\n🏷️  CATEGORIA: {codigo_bph}")
            print("-" * 50)
        else:
            print(f"\n📝 ATIVIDADES SEM BPH")
            print("-" * 50)
        
        for i, (_, row) in enumerate(grupo.iterrows(), 1):
            print(f"{i}. {row['Atividades']}")
    
    print("\n✅ Teste de categorização BPH concluído!")
    
    # Verificar se a categorização está correta
    categorias_esperadas = ['BPH003890', 'BPH004040', 'BPH005123']
    categorias_encontradas = list(grupos_bph.groups.keys())
    
    print(f"\n🔍 Categorias encontradas: {categorias_encontradas}")
    
    if all(cat in categorias_encontradas for cat in categorias_esperadas):
        print("✅ Categorização está CORRETA!")
    else:
        print("❌ Categorização está INCORRETA!")
    
    return df_teste

if __name__ == "__main__":
    df_resultado = testar_categorizacao_bph() 