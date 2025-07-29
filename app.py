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
    if 'email_usuario' not in st.session_state:
        st.session_state['email_usuario'] = ''
    if 'tipo_usuario' not in st.session_state:
        st.session_state['tipo_usuario'] = ''
    if 'show_login' not in st.session_state:
        st.session_state['show_login'] = False
    if 'session_id' not in st.session_state:
        st.session_state['session_id'] = None

inicializa_session_state()

# Diagnóstico: Exibe o session_state no topo da tela para depuração
# Remover painel de debug
# st.write("DEBUG session_state:", dict(st.session_state))

# IMPORTAÇÕES DAS TELAS E UTILITÁRIOS
from controle_trilhas import criar_tabela_controle_execucao
from tela_registre_se import tela_registre_se
from tela_perfil import tela_perfil
from tela_configuracao import tela_configuracao
from banco_de_dados import tela_banco_dados
from utils import (
    USERS_FILE, DB_FILE, inicializa_db, salva_login_status, busca_login_status, remove_login_status,
    inicializa_usuarios, autentica_usuario, cadastra_usuario, salva_impressao_upload, busca_impressao_upload,
    salva_gestao_trilhas, busca_gestao_trilhas, limpa_gestao_trilhas, atualiza_status_trilha, limpa_coluna_impresso_por,
    gerar_xlsx_trilha, gerar_xlsx_trilha_novo_banco, registrar_download_trilha, buscar_controle_downloads, atualizar_status_download,
    verificar_sessao_ativa, limpar_sessao_compartilhada
)

# Verificar se há sessão compartilhada ativa e limpar se necessário
# Isso garante que cada usuário tenha sua própria sessão
if verificar_sessao_ativa() and not st.session_state['autenticado']:
    limpar_sessao_compartilhada()

# Não restaurar login do banco - cada usuário deve fazer login individualmente
# Isso garante que cada sessão seja individual por usuário

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
        if st.button("Logout", key="header_logout_btn", help="Clique para sair", use_container_width=True):
            # Limpar sessão individual
            st.session_state['autenticado'] = False
            st.session_state['usuario'] = ''
            st.session_state['email_usuario'] = ''
            st.session_state['tipo_usuario'] = ''
            st.session_state['session_id'] = None
            st.session_state['show_login'] = False
            
            # Limpar sessão compartilhada no banco (para compatibilidade)
            limpar_sessao_compartilhada()
            
            st.success("Logout realizado com sucesso!")
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
    # Menu para usuários logados
    if st.session_state['autenticado']:
        opcoes_menu.append("Impressão de Trilhas")
        opcoes_menu.append("Perfil")
        opcoes_menu.append("Banco de Dados")
        
        # Descobre tipo do usuário logado
        try:
            df_usuarios = pd.read_csv(USERS_FILE)
            tipo_usuario = df_usuarios[df_usuarios['nome'] == st.session_state['usuario']]['tipo'].values
            if len(tipo_usuario) > 0 and tipo_usuario[0] == 'admin':
                opcoes_menu.append("Controle de Trilhas")
                opcoes_menu.append("Configuração")
        except Exception:
            # Usar tipo armazenado na sessão como fallback
            if st.session_state.get('tipo_usuario') == 'admin':
                opcoes_menu.append("Controle de Trilhas")
                opcoes_menu.append("Configuração")
    else:
        # Menu para usuários não logados
        opcoes_menu.append("Login")
        opcoes_menu.append("Registre-se")
    
    # Se não há opções no menu, adicionar uma opção padrão
    if not opcoes_menu:
        opcoes_menu.append("Login")
    
    pagina = st.radio("", opcoes_menu)
    st.markdown('<div class="sidebar-footer"></div>', unsafe_allow_html=True)
    if st.session_state['autenticado']:
        st.markdown(f'<span style="color:#fff;">Usuário: {st.session_state["usuario"]}</span>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Tela de login
if (st.session_state.get('show_login', False) and not st.session_state['autenticado']) or (pagina == "Login" and not st.session_state['autenticado']):
    col_login1, col_login2, col_login3 = st.columns([2.75,2.5,2.75])
    with col_login2:
        st.markdown('<h2 style="text-align:center; margin-bottom: 20px;">Login</h2>', unsafe_allow_html=True)
        usuario = st.text_input("E-mail", key="login_usuario")
        senha = st.text_input("Senha", type="password", key="login_senha")
        if st.button("Entrar", key="btn_main_entrar"):
            ok, nome, tipo = autentica_usuario(usuario, senha)
            if ok:
                # Configurar sessão individual do usuário
                st.session_state['autenticado'] = True
                st.session_state['usuario'] = nome
                st.session_state['email_usuario'] = usuario
                st.session_state['tipo_usuario'] = tipo
                st.session_state['session_id'] = f"{usuario}_{nome}_{tipo}"
                st.session_state['show_login'] = False
                
                # Limpar sessão compartilhada no banco (para compatibilidade)
                limpar_sessao_compartilhada()
                
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
    
    # Buscar trilhas do novo banco database_trilhas.db
    db_trilhas_path = os.path.join("Impressão de trilhas", "database_trilhas.db")
    
    if os.path.exists(db_trilhas_path):
        conn_trilhas = sqlite3.connect(db_trilhas_path)
        try:
            # Buscar trilhas únicas do novo banco
            df_trilhas_novo = pd.read_sql_query('SELECT DISTINCT Trilhas FROM trilhas WHERE Trilhas IS NOT NULL AND Trilhas != ""', conn_trilhas)
            
            # Se não há trilhas no novo banco, mostrar mensagem
            if df_trilhas_novo.empty:
                st.info("📭 Nenhuma trilha encontrada no banco de dados.")
                st.write("Faça upload de dados na página 'Banco de Dados' para começar.")
            else:
                # Criar combobox com as trilhas do novo banco
                opcoes_combo = []
                for _, row in df_trilhas_novo.iterrows():
                    trilha = row['Trilhas']
                    
                    # Tentar extrair código do nome da trilha
                    import re
                    padrao = r'^(CMR\s*\d+\.?\d*)'
                    match = re.search(padrao, str(trilha), re.IGNORECASE)
                    if match:
                        codigo = match.group(1).strip()
                        opcao = f"{codigo} - {trilha}"
                    else:
                        opcao = trilha
                    
                    opcoes_combo.append(opcao)
                
                # Remover duplicatas das opções
                opcoes_combo = list(dict.fromkeys(opcoes_combo))
                
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
                        if ' - ' in trilha_selecionada:
                            codigo_trilha, nome_trilha = trilha_selecionada.split(' - ', 1)
                        else:
                            codigo_trilha = ''
                            nome_trilha = trilha_selecionada
                        
                        # Gerar arquivo XLSX usando dados do novo banco
                        usuario_logado = st.session_state.get('usuario', 'Usuário Desconhecido')
                        xlsx_bytes = gerar_xlsx_trilha_novo_banco(nome_trilha, codigo_trilha, usuario_logado)
                        
                        # Botão de download
                        st.download_button(
                            label='Download XLSX',
                            data=xlsx_bytes,
                            file_name=f'{codigo_trilha}_{nome_trilha}.xlsx',
                            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                        )
                
                # Exibir tabela com dados do novo banco
                st.write("### Dados das Trilhas")
                
                # Buscar dados de controle de downloads
                df_controle = buscar_controle_downloads()
                
                if not df_controle.empty:
                    # Renomear colunas para melhor apresentação
                    df_controle = df_controle.rename(columns={
                        'Trilhas': 'Trilhas',
                        'Impresso': 'Impresso',
                        'Impresso_por': 'Impresso por',
                        'Modificado_em': 'Modificado em'
                    })
                    
                    # Formatar data/hora se necessário
                    if 'Modificado em' in df_controle.columns:
                        df_controle['Modificado em'] = df_controle['Modificado em'].apply(
                            lambda x: x if x == '' else x.replace('T', ' ').split('.')[0]
                        )
                    
                    # Exibir tabela
                    st.dataframe(df_controle, use_container_width=True)
                    
                    # Estatísticas
                    st.write("### 📊 Estatísticas")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        total_trilhas = len(df_controle)
                        st.metric("Total de Trilhas", total_trilhas)
                    
                    with col2:
                        trilhas_impressas = len(df_controle[df_controle['Impresso'] == 'SIM'])
                        st.metric("Trilhas Impressas", trilhas_impressas)
                    
                    with col3:
                        trilhas_pendentes = len(df_controle[df_controle['Impresso'] == 'NÃO'])
                        st.metric("Trilhas Pendentes", trilhas_pendentes)
                    
                else:
                    st.info("📭 Nenhuma trilha encontrada no banco de dados.")
                    st.write("Faça upload de dados na página 'Banco de Dados' para começar.")
        
        except Exception as e:
            st.error(f"❌ Erro ao acessar banco de dados: {e}")
            st.info("Verifique se o banco de dados foi criado corretamente.")
        
        finally:
            conn_trilhas.close()
    else:
        st.warning("⚠️ Banco de dados não encontrado!")
        st.info("Execute o script 'criar_database_trilhas.py' para criar o banco de dados.")
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
    
    # Verificar se é administrador
    if st.session_state.get('tipo_usuario') != 'admin':
        st.error("Acesso negado. Apenas administradores podem acessar esta página.")
        st.stop()
    
    tela_configuracao()
# Controle de Trilhas
elif pagina == "Controle de Trilhas" and not st.session_state.get('show_login', False):
    if not st.session_state['autenticado']:
        st.warning("Faça login para acessar o controle de trilhas.")
        st.stop()
    
    # Verificar se é administrador
    if st.session_state.get('tipo_usuario') != 'admin':
        st.error("Acesso negado. Apenas administradores podem acessar esta página.")
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

# Banco de Dados
elif pagina == "Banco de Dados" and not st.session_state.get('show_login', False):
    if not st.session_state['autenticado']:
        st.warning("Faça login para acessar o banco de dados.")
        st.stop()
    
    # Chamar a tela do banco de dados
    tela_banco_dados()

# Rodapé
st.markdown("""
    <hr style='margin-top: 50px;'/>
    <div style='text-align: center; color: #888;'>
        &copy; 2024 Impressão de Trilhas. Todos os direitos reservados.
    </div>
""", unsafe_allow_html=True) 