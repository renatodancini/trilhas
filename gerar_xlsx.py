import pandas as pd
import io

def gerar_xlsx_para_trilha(nome_trilha, codigo, df_completo):
    """
    Gera um arquivo XLSX para uma trilha específica, removendo colunas desnecessárias.
    """
    # Filtrar dados da trilha selecionada
    df_trilha = df_completo[df_completo['Trilhas'] == nome_trilha].copy()
    
    if df_trilha.empty:
        return None
    
    # Remover colunas desnecessárias
    colunas_para_remover = ['Código', 'Trilhas', 'Status', 'Modificado em']
    colunas_existentes = [col for col in colunas_para_remover if col in df_trilha.columns]
    df_trilha = df_trilha.drop(columns=colunas_existentes)
    
    # Criar buffer para o arquivo
    buffer = io.BytesIO()
    
    # Salvar como XLSX
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df_trilha.to_excel(writer, sheet_name='Trilha', index=False)
    
    buffer.seek(0)
    return buffer.read() 