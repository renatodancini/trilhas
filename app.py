import streamlit as st
import os
import pandas as pd
import sqlite3

# Inicialização do session_state antes de qualquer uso
def inicializa_session_state():
    if 'autenticado' not in st.session_state:
        st.session_state['autenticado'] = False
    if 'usuario' not in st.session_state:
        st.session_state['usuario'] = ''
    if 'show_login' not in st.session_state:
        st.session_state['show_login'] = False
inicializa_session_state()

# Diagnóstico: Exibe o session_state no topo da tela para depuração
# Remover painel de debug
# st.write("DEBUG session_state:", dict(st.session_state))

# IMPORTAÇÕES DAS TELAS E UTILITÁRIOS
from controle_trilhas import criar_tabela_controle_execucao
from tela_registre_se import tela_registre_se
from tela_perfil import tela_perfil
from tela_configuracao import tela_configuracao
from utils import (
    USERS_FILE, DB_FILE, inicializa_db, salva_login_status, busca_login_status, remove_login_status,
    inicializa_usuarios, autentica_usuario, cadastra_usuario, salva_impressao_upload, busca_impressao_upload,
    salva_gestao_trilhas, busca_gestao_trilhas, limpa_gestao_trilhas, atualiza_status_trilha, limpa_coluna_impresso_por,
    gerar_xlsx_trilha
)

# Ao iniciar, tenta restaurar login
if not st.session_state['autenticado']:
    login_info = busca_login_status()
    if login_info:
        st.session_state['autenticado'] = True
        st.session_state['usuario'] = login_info['nome']
        st.session_state['tipo'] = login_info['tipo']

# Função para aplicar estilo customizado ao menu lateral
def estilo_menu_lateral():
    st.markdown('''
        <style>
            section[data-testid="stSidebar"] {
                background-color: #003366;
                border-right: 1px solid #003366;
            }
            section[data-testid="stSidebar"] * {
                color: #FFFFFF !important;
            }
            div[data-baseweb="radio"] label {
                font-size: 1.1em;
                font-weight: bold;
            }
            section[data-testid="stSidebar"] > div:first-child {
                margin-top: 30px;
            }
            .sidebar-footer {
                position: absolute;
                bottom: 30px;
                left: 0;
                width: 100%;
                text-align: center;
            }
        </style>
    ''', unsafe_allow_html=True)

# Configuração da página
st.set_page_config(page_title="Impressão de Trilhas", layout="wide")

# Aplica o estilo customizado ao menu lateral
estilo_menu_lateral()

# Reduzir margens laterais para 10px
st.markdown('''
    <style>
    .main .block-container {
        padding-left: 10px !important;
        padding-right: 10px !important;
    }
    </style>
''', unsafe_allow_html=True)

# Remover header azul, manter só o botão Login/Logoff no topo
header_col, header_btn_col = st.columns([10, 1])
with header_col:
    st.markdown("""
        <style>
            .main .block-container {
                padding-top: 20px !important;
            }
        </style>
    """, unsafe_allow_html=True)

with header_btn_col:
    if not st.session_state['autenticado']:
        if st.button("Login", key="header_login_btn", help="Clique para logar", use_container_width=True):
            st.session_state['show_login'] = True
    else:
        if st.button("Logout", key="header_logoff_btn", help="Clique para sair", use_container_width=True):
            st.session_state['autenticado'] = False
            st.session_state['usuario'] = ''
            remove_login_status()  # Remove do banco
            st.success('Logout realizado com sucesso!')
            try:
                st.rerun()
            except AttributeError:
                st.experimental_rerun()

# Sessão de autenticação
# if 'autenticado' not in st.session_state:
#     st.session_state['autenticado'] = False
# if 'usuario' not in st.session_state:
#     st.session_state['usuario'] = ''
# if 'show_login' not in st.session_state:
#     st.session_state['show_login'] = False

# Menu lateral
with st.sidebar:
    opcoes_menu = []
    # Só mostra Impressão de Trilhas e Configuração para usuários logados
    if st.session_state['autenticado']:
        opcoes_menu.append("Impressão de Trilhas")
        opcoes_menu.append("Perfil")
        opcoes_menu.append("Controle de Trilhas")
        # Descobre tipo do usuário logado
        try:
            df_usuarios = pd.read_csv(USERS_FILE)
            tipo_usuario = df_usuarios[df_usuarios['nome'] == st.session_state['usuario']]['tipo'].values
            if len(tipo_usuario) > 0 and tipo_usuario[0] == 'Administrador':
                opcoes_menu.append("Configuração")
        except Exception:
            pass
    else:
        opcoes_menu.append("Registre-se")
    
    # Se não há opções no menu, adicionar uma opção padrão
    if not opcoes_menu:
        opcoes_menu.append("Registre-se")
    
    pagina = st.radio("", opcoes_menu)
    st.markdown('<div class="sidebar-footer"></div>', unsafe_allow_html=True)
    if st.session_state['autenticado']:
        st.markdown(f'<span style="color:#fff;">Usuário: {st.session_state["usuario"]}</span>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Tela de login
if st.session_state.get('show_login', False) and not st.session_state['autenticado']:
    col_login1, col_login2, col_login3 = st.columns([2.75,2.5,2.75])
    with col_login2:
        st.markdown('<h2 style="text-align:center; margin-bottom: 20px;">Login</h2>', unsafe_allow_html=True)
        usuario = st.text_input("Usuário", key="login_usuario")
        senha = st.text_input("Senha", type="password", key="login_senha")
        if st.button("Entrar", key="btn_main_entrar"):
            ok, nome, tipo = autentica_usuario(usuario, senha)
            if ok:
                st.session_state['autenticado'] = True
                st.session_state['usuario'] = nome
                st.session_state['tipo'] = tipo
                salva_login_status(usuario, nome, tipo) # Salva status no banco
                st.session_state['show_login'] = False
                st.success(f"Bem-vindo, {nome}!")
                try:
                    st.rerun()
                except AttributeError:
                    st.experimental_rerun()
            else:
                st.error("Usuário ou senha inválidos.")
    st.stop()

# Conteúdo principal de acordo com o menu
# IMPORTAÇÕES DAS TELAS
# SUBSTITUIR OS BLOCOS DAS TELAS POR CHAMADAS
# Impressão de Trilhas
if pagina == "Impressão de Trilhas" and not st.session_state.get('show_login', False):
    st.write('### Gestão das Trilhas')
    df_trilhas_banco = busca_gestao_trilhas()
    
    # Criar combobox com as trilhas
    if df_trilhas_banco is not None and 'Trilhas' in df_trilhas_banco.columns:
        # Buscar trilhas únicas com código
        trilhas_unicas = df_trilhas_banco[['Código', 'Trilhas']].drop_duplicates().dropna(subset=['Trilhas'])
        opcoes_combo = [f"{row['Código']} - {row['Trilhas']}" for _, row in trilhas_unicas.iterrows()]
        
        # Combobox para seleção de trilha
        trilha_selecionada = st.selectbox(
            'Selecione uma trilha:',
            options=[''] + opcoes_combo,
            key='combo_trilhas'
        )
        
        if trilha_selecionada:
            # Botão Imprimir
            if st.button('Imprimir', key='btn_imprimir'):
                # Extrair código e nome da trilha
                codigo_trilha, nome_trilha = trilha_selecionada.split(' - ', 1)
                
                # Gerar arquivo XLSX
                xlsx_bytes = gerar_xlsx_trilha(nome_trilha, codigo_trilha)
                
                # Botão de download
                st.download_button(
                    label='Download XLSX',
                    data=xlsx_bytes,
                    file_name=f'{codigo_trilha}_{nome_trilha}.xlsx',
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
    
    # Exibir tabela completa com todos os dados
    if df_trilhas_banco is not None and 'Trilhas' in df_trilhas_banco.columns:
        # Buscar dados diretamente do database_2.db
        conn2 = sqlite3.connect('database_2.db')
        try:
            df_ctrl = pd.read_sql_query('SELECT Trilhas, Status, "Modificado por", "Modificado em" FROM controle_trilhas', conn2)
        except Exception:
            df_ctrl = pd.DataFrame(columns=['Trilhas', 'Status', 'Modificado por', 'Modificado em'])
        conn2.close()
        
        # Remover duplicatas da tabela controle_trilhas
        df_ctrl = df_ctrl.drop_duplicates(subset=['Trilhas'])
        
        # Formatar trilhas com código
        df_ctrl['Trilha'] = df_ctrl['Trilhas'].apply(lambda x: x if pd.notnull(x) and x else '')
        
        # Buscar códigos das trilhas do login_status.db
        conn_gestao = sqlite3.connect('login_status.db')
        try:
            df_gestao = pd.read_sql_query('SELECT Trilhas, Código FROM gestao_trilhas', conn_gestao)
        except Exception:
            df_gestao = pd.DataFrame(columns=['Trilhas', 'Código'])
        conn_gestao.close()
        
        # Remover duplicatas da tabela gestao_trilhas
        df_gestao = df_gestao.drop_duplicates(subset=['Trilhas'])
        
        # Mesclar para obter os códigos
        df_final = pd.merge(df_ctrl, df_gestao, left_on='Trilhas', right_on='Trilhas', how='left')
        df_final['Trilha'] = df_final['Código'].apply(lambda x: f'{x} - ' if pd.notnull(x) and x else '') + df_final['Trilhas'].astype(str)
        
        # Definir colunas para exibir
        colunas_exibir = ['Trilha', 'Status', 'Modificado por', 'Modificado em']
        colunas_existentes = [col for col in colunas_exibir if col in df_final.columns]
        
        st.write('### Controle de Trilhas')
        st.dataframe(df_final[colunas_existentes])
# Registre-se
elif pagina == "Registre-se" and not st.session_state['autenticado']:
    tela_registre_se()
# Perfil
elif pagina == "Perfil" and not st.session_state.get('show_login', False):
    tela_perfil()
# Configuração
elif pagina == "Configuração" and not st.session_state.get('show_login', False):
    if not st.session_state['autenticado']:
        st.warning("Faça login para acessar a página de configuração.")
        st.stop()
    tela_configuracao()
# Controle de Trilhas
elif pagina == "Controle de Trilhas" and not st.session_state.get('show_login', False):
    if not st.session_state['autenticado']:
        st.warning("Faça login para acessar o controle de trilhas.")
        st.stop()
    
    st.title('Controle de Execução das Trilhas')
    st.info('Aqui você poderá categorizar e acompanhar a execução das trilhas.')
    
    # Criar tabela se não existir
    criar_tabela_controle_execucao()
    
    # Funções auxiliares
    def get_df():
        conn = sqlite3.connect('database_2.db')
        df = pd.read_sql_query('SELECT * FROM controle_execucao', conn)
        conn.close()
        return df
    
    def atualizar_categoria(trilha, nova_categoria):
        conn2 = sqlite3.connect('database_2.db')
        conn2.execute('UPDATE controle_execucao SET categoria = ? WHERE trilha = ?', (nova_categoria, trilha))
        conn2.commit()
        conn2.close()
    
    # Criar abas
    aba1, aba2 = st.tabs(["Editar Categoria", "Tabela Completa"])
    
    with aba1:
        df = get_df()
        if not df.empty:
            # Ocultar coluna id
            df_edit = df.drop(columns=['id']) if 'id' in df.columns else df
            
            # Formatar trilha com código
            conn_gestao = sqlite3.connect('login_status.db')
            try:
                df_gestao = pd.read_sql_query('SELECT Trilhas, Código FROM gestao_trilhas', conn_gestao)
            except Exception:
                df_gestao = pd.DataFrame(columns=['Trilhas', 'Código'])
            conn_gestao.close()
            
            df_gestao = df_gestao.drop_duplicates(subset=['Trilhas'])
            df_edit = pd.merge(df_edit, df_gestao, left_on='trilha', right_on='Trilhas', how='left')
            df_edit['trilha_formatada'] = df_edit['Código'].apply(lambda x: f'{x} - ' if pd.notnull(x) and x else '') + df_edit['trilha'].astype(str)
            
            # Criar editor de dados
            edited_df = st.data_editor(
                df_edit[['trilha_formatada', 'categoria']],
                column_config={
                    "trilha_formatada": st.column_config.TextColumn("Trilha", disabled=True),
                    "categoria": st.column_config.NumberColumn("Categoria", min_value=1, max_value=10)
                },
                hide_index=True
            )
            
            # Detectar mudanças e atualizar
            if not edited_df.equals(df_edit[['trilha_formatada', 'categoria']]):
                for idx, row in edited_df.iterrows():
                    trilha_original = df_edit.iloc[idx]['trilha']
                    nova_categoria = row['categoria']
                    atualizar_categoria(trilha_original, nova_categoria)
                st.success("Categorias atualizadas com sucesso!")
                st.rerun()
        else:
            st.warning("Nenhuma trilha encontrada na tabela de controle.")
    
    with aba2:
        df_exec = get_df()
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
        
        df_merged = pd.merge(df_exec, df_gestao, left_on='trilha', right_on='Trilhas', how='left')
        df_merged = pd.merge(df_merged, df_ctrl, left_on='trilha', right_on='Trilhas', how='left', suffixes=('', '_ctrl'))
        df_merged['Trilha'] = df_merged['Código'].apply(lambda x: f'{x} - ' if pd.notnull(x) and x else '') + df_merged['trilha'].astype(str)
        
        colunas_exibir = ['Trilha', 'Status', 'Modificado por', 'Modificado em']
        colunas_existentes = [col for col in colunas_exibir if col in df_merged.columns]
        st.dataframe(df_merged[colunas_existentes])

# Rodapé
st.markdown("""
    <hr style='margin-top: 50px;'/>
    <div style='text-align: center; color: #888;'>
        &copy; 2024 Impressão de Trilhas. Todos os direitos reservados.
    </div>
""", unsafe_allow_html=True) 