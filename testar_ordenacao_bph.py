#!/usr/bin/env python3
"""
Script para testar a ordenação BPH das atividades
"""

import pandas as pd
import re

def extrair_numero_bph(atividade):
    """Função para extrair número BPH para ordenação"""
    # Procurar por BPH seguido de números
    match = re.search(r'BPH(\d+)', atividade)
    if match:
        return int(match.group(1))
    return 0  # Se não encontrar BPH, colocar no início

def testar_ordenacao_bph():
    """Testa a ordenação BPH com dados de exemplo"""
    
    # Dados de teste
    atividades_teste = [
        "CMR248.1 - BPH000816 - 43. Administrar deferimentos de crédito documentado",
        "CMR248.1 - BPH000123 - 12. Validar documentos",
        "CMR248.1 - BPH000999 - 99. Finalizar processo",
        "CMR248.1 - BPH000001 - 1. Iniciar processo",
        "CMR248.1 - BPH000456 - 45. Analisar crédito",
        "CMR248.1 - BPH000789 - 78. Aprovar solicitação"
    ]
    
    # Criar DataFrame de teste
    df_teste = pd.DataFrame({
        'Atividades': atividades_teste,
        'Responsável': ['João', 'Maria', 'Pedro', 'Ana', 'Carlos', 'Lucia'],
        'Tipo': ['A', 'B', 'C', 'A', 'B', 'C'],
        'Finalizado': ['Não', 'Sim', 'Não', 'Sim', 'Não', 'Sim'],
        'Observações': ['Obs 1', 'Obs 2', 'Obs 3', 'Obs 4', 'Obs 5', 'Obs 6']
    })
    
    print("=== TESTE DE ORDENAÇÃO BPH ===")
    print("\n📋 Atividades ANTES da ordenação:")
    for i, atividade in enumerate(df_teste['Atividades'], 1):
        print(f"{i}. {atividade}")
    
    # Aplicar ordenação BPH
    df_teste['numero_bph'] = df_teste['Atividades'].apply(extrair_numero_bph)
    df_teste = df_teste.sort_values('numero_bph')
    df_teste = df_teste.drop('numero_bph', axis=1)
    
    print("\n📋 Atividades DEPOIS da ordenação:")
    for i, atividade in enumerate(df_teste['Atividades'], 1):
        print(f"{i}. {atividade}")
    
    print("\n✅ Teste de ordenação BPH concluído!")
    
    # Verificar se a ordenação está correta
    numeros_bph = [extrair_numero_bph(atividade) for atividade in df_teste['Atividades']]
    print(f"\n🔢 Números BPH extraídos: {numeros_bph}")
    
    if numeros_bph == sorted(numeros_bph):
        print("✅ Ordenação está CORRETA!")
    else:
        print("❌ Ordenação está INCORRETA!")
    
    return df_teste

if __name__ == "__main__":
    df_resultado = testar_ordenacao_bph() 