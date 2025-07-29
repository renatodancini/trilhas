import streamlit as st
from utils import cadastra_usuario, obter_categorias_disponiveis

def tela_registre_se():
    st.write("Entrou na tela de registro")  # Depuração
    col_reg1, col_reg2, col_reg3 = st.columns([2.75,2.5,2.75])
    with col_reg2:
        st.markdown('<h3 style="text-align:center; margin-bottom: 20px; font-size:1.1em; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">Cadastro de Usuário</h3>', unsafe_allow_html=True)
        with st.form("form_registro_usuario"):
            nome = st.text_input("Nome", key="reg_nome")
            email = st.text_input("Email", key="reg_email")
            senha = st.text_input("Senha", type="password", key="reg_senha")
            
            # Seção de categorias
            st.markdown("### 📂 Seleção de Categorias")
            st.info("Selecione as categorias de trilhas que você deseja acessar. As categorias são baseadas nas 3 primeiras letras dos nomes das trilhas.")
            
            # Obter categorias disponíveis
            categorias_disponiveis = obter_categorias_disponiveis()
            
            if categorias_disponiveis:
                # Criar multiselect para categorias
                categorias_selecionadas = st.multiselect(
                    "Categorias disponíveis:",
                    options=categorias_disponiveis,
                    default=categorias_disponiveis[:3] if len(categorias_disponiveis) >= 3 else categorias_disponiveis,
                    help="Selecione quantas categorias desejar. Trilhas que não pertencem às categorias selecionadas não serão visíveis."
                )
                
                # Mostrar preview das categorias selecionadas
                if categorias_selecionadas:
                    st.success(f"✅ {len(categorias_selecionadas)} categoria(s) selecionada(s)")
                    st.write("**Categorias selecionadas:**")
                    for cat in categorias_selecionadas:
                        st.write(f"• {cat}")
                else:
                    st.warning("⚠️ Nenhuma categoria selecionada. Você não terá acesso a nenhuma trilha.")
            else:
                st.warning("⚠️ Nenhuma trilha encontrada no banco de dados. As categorias serão criadas conforme trilhas forem adicionadas.")
                categorias_selecionadas = []
            
            if st.form_submit_button("Cadastrar"):
                try:
                    # Converter lista de categorias para string JSON
                    import json
                    categorias_json = json.dumps(categorias_selecionadas) if categorias_selecionadas else "[]"
                    
                    if cadastra_usuario(nome, email, senha, "Usuário", categorias_json):
                        st.success("Usuário cadastrado com sucesso! Faça login para acessar o sistema.")
                    else:
                        st.error("Email já cadastrado.")
                except Exception as e:
                    st.error(f"Erro ao cadastrar usuário: {e}")
    st.stop() 