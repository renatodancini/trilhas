import streamlit as st
import pandas as pd
import sqlite3
from utils import busca_gestao_trilhas, atualizar_status_impressao, atualizar_status_controle_trilhas
from gerar_xlsx import gerar_xlsx_para_trilha

def home():
    # Sem título e sem frase inicial
    df_trilhas_banco = busca_gestao_trilhas()
    tipo_usuario = st.session_state.get('tipo', 'Usuário')
    
    if df_trilhas_banco is not None and 'Trilhas' in df_trilhas_banco.columns:
        trilhas_cod_nome = []
        trilhas_unicas = df_trilhas_banco[['Trilhas', 'Código']].drop_duplicates().dropna(subset=['Trilhas'])
        
        for _, row in trilhas_unicas.iterrows():
            nome = row['Trilhas']
            codigo = row['Código'] if 'Código' in row and row['Código'] else ''
            label = f"{codigo} - {nome}" if codigo else nome
            trilhas_cod_nome.append(label)
        
        trilha_selecionada = st.selectbox('Selecione uma trilha para impressão:', trilhas_cod_nome, key='combo_trilha_home')
        
        if trilha_selecionada:
            if ' - ' in trilha_selecionada:
                codigo, nome_trilha = trilha_selecionada.split(' - ', 1)
            else:
                codigo, nome_trilha = '', trilha_selecionada
            
            chave_impresso = f'imprimiu_{nome_trilha}'
            bloqueado = st.session_state.get(chave_impresso, False)
            pode_imprimir = (tipo_usuario == 'Administrador') or not bloqueado
            
            if st.button('Imprimir', disabled=not pode_imprimir):
                usuario_logado = st.session_state.get('usuario', 'Usuário')
                atualizar_status_impressao(nome_trilha, usuario_logado)
                atualizar_status_controle_trilhas(nome_trilha, usuario_logado)
                xlsx_bytes = gerar_xlsx_para_trilha(nome_trilha, codigo, df_trilhas_banco)
                st.download_button(
                    label='Download XLSX',
                    data=xlsx_bytes,
                    file_name=f'{codigo}_{nome_trilha}.xlsx',
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
                if tipo_usuario != 'Administrador':
                    st.session_state[chave_impresso] = True
    
    # Exibir tabela completa igual à da tela Controle de Trilhas
    conn_gestao = sqlite3.connect('login_status.db')
    try:
        df_gestao = pd.read_sql_query('SELECT Trilhas, Código FROM gestao_trilhas', conn_gestao)
    except Exception:
        df_gestao = pd.DataFrame(columns=['Trilhas', 'Código'])
    conn_gestao.close()
    
    df_gestao = df_gestao.drop_duplicates(subset=['Trilhas'])
    
    conn2 = sqlite3.connect('database_2.db')
    try:
        df_ctrl = pd.read_sql_query('SELECT Trilhas, Status, "Modificado por", "Modificado em" FROM controle_trilhas', conn2)
    except Exception:
        df_ctrl = pd.DataFrame(columns=['Trilhas', 'Status', 'Modificado por', 'Modificado em'])
    conn2.close()
    
    df_ctrl = pd.merge(df_ctrl, df_gestao, left_on='Trilhas', right_on='Trilhas', how='left')
    df_ctrl['Trilha'] = df_ctrl['Código'].apply(lambda x: f'{x} - ' if pd.notnull(x) and x else '') + df_ctrl['Trilhas'].astype(str)
    
    colunas_exibir = ['Trilha', 'Status', 'Modificado por', 'Modificado em']
    colunas_existentes = [col for col in colunas_exibir if col in df_ctrl.columns]
    
    st.write('### Controle de Trilhas')
    st.dataframe(df_ctrl[colunas_existentes]) 