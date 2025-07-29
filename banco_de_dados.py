#!/usr/bin/env python3
"""
Módulo para gerenciar o banco de dados database_trilhas
"""

import streamlit as st
import pandas as pd
import sqlite3
import os
import io

# Caminho para o banco de dados
DB_TRILHAS_FILE = os.path.join("Impressão de trilhas", "database_trilhas.db")

def inicializar_banco():
    """Inicializa o banco de dados se não existir"""
    if not os.path.exists(DB_TRILHAS_FILE):
        conn = sqlite3.connect(DB_TRILHAS_FILE)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trilhas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                Trilhas TEXT,
                Atividades TEXT NOT NULL,
                Responsável TEXT,
                Tipo TEXT,
                Finalizado TEXT,
                Observações TEXT
            )
        ''')
        conn.commit()
        conn.close()
        st.success("Banco de dados inicializado com sucesso!")
    else:
        # Verificar se a coluna Trilhas existe, se não, adicionar
        conn = sqlite3.connect(DB_TRILHAS_FILE)
        cursor = conn.cursor()
        
        # Verificar estrutura atual da tabela
        cursor.execute("PRAGMA table_info(trilhas)")
        colunas_existentes = [col[1] for col in cursor.fetchall()]
        
        # Se a coluna Trilhas não existe, adicionar
        if 'Trilhas' not in colunas_existentes:
            try:
                cursor.execute("ALTER TABLE trilhas ADD COLUMN Trilhas TEXT")
                conn.commit()
                st.success("✅ Coluna 'Trilhas' adicionada ao banco de dados!")
            except Exception as e:
                st.warning(f"⚠️ Aviso: {e}")
        
        conn.close()

def carregar_dados_excel(arquivo):
    """Carrega dados de um arquivo Excel"""
    try:
        if arquivo.name.endswith('.xlsx'):
            df = pd.read_excel(arquivo)
        elif arquivo.name.endswith('.csv'):
            df = pd.read_csv(arquivo)
        else:
            st.error("Formato de arquivo não suportado. Use .xlsx ou .csv")
            return None
        
        # Verificar se as colunas necessárias existem
        colunas_necessarias = ['Trilhas', 'Atividades', 'Responsável', 'Tipo', 'Finalizado', 'Observações']
        colunas_faltantes = [col for col in colunas_necessarias if col not in df.columns]
        
        if colunas_faltantes:
            st.error(f"Colunas faltantes no arquivo: {colunas_faltantes}")
            st.info("As colunas necessárias são: Trilhas, Atividades, Responsável, Tipo, Finalizado, Observações")
            return None
        
        # Garantir que a coluna Trilhas esteja presente
        if 'Trilhas' not in df.columns:
            st.warning("⚠️ Coluna 'Trilhas' não encontrada. Será criada com valores vazios.")
            df['Trilhas'] = ''
        
        return df
    
    except Exception as e:
        st.error(f"Erro ao carregar arquivo: {e}")
        return None

def fazer_backup_banco():
    """Faz backup dos dados atuais do banco"""
    try:
        conn = sqlite3.connect(DB_TRILHAS_FILE)
        df_backup = pd.read_sql_query("SELECT * FROM trilhas ORDER BY id", conn)
        conn.close()
        
        if not df_backup.empty:
            # Criar nome do arquivo com timestamp
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_arquivo = f"backup_banco_{timestamp}.xlsx"
            
            # Salvar backup
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df_backup.to_excel(writer, sheet_name='Backup', index=False)
            buffer.seek(0)
            
            return buffer.read(), nome_arquivo
        else:
            return None, None
            
    except Exception as e:
        st.error(f"❌ Erro ao fazer backup: {e}")
        return None, None

def salvar_dados_banco(df):
    """Salva dados do DataFrame no banco de dados"""
    try:
        conn = sqlite3.connect(DB_TRILHAS_FILE)
        
        # Verificar quantos registros existem atualmente
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM trilhas")
        registros_atuais = cursor.fetchone()[0]
        
        # Fazer backup se existem dados
        backup_data = None
        backup_filename = None
        if registros_atuais > 0:
            backup_data, backup_filename = fazer_backup_banco()
        
        # Limpar dados existentes
        conn.execute("DELETE FROM trilhas")
        
        # Inserir novos dados
        df.to_sql('trilhas', conn, if_exists='append', index=False)
        
        conn.commit()
        conn.close()
        
        # Mensagem detalhada sobre a operação
        if registros_atuais > 0:
            st.success(f"✅ Banco de dados atualizado com sucesso!")
            st.info(f"📊 {registros_atuais} registros antigos foram removidos")
            st.success(f"📈 {len(df)} novos registros foram inseridos")
            
            # Oferecer download do backup
            if backup_data and backup_filename:
                st.warning("💾 Backup dos dados antigos disponível:")
                st.download_button(
                    label=f"📥 Download Backup: {backup_filename}",
                    data=backup_data,
                    file_name=backup_filename,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        else:
            st.success(f"✅ Dados salvos com sucesso! {len(df)} registros inseridos.")
        
        return True
    
    except Exception as e:
        st.error(f"❌ Erro ao salvar dados no banco: {e}")
        return False

def buscar_dados_banco():
    """Busca todos os dados do banco de dados"""
    try:
        conn = sqlite3.connect(DB_TRILHAS_FILE)
        df = pd.read_sql_query("SELECT * FROM trilhas ORDER BY id", conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Erro ao buscar dados do banco: {e}")
        return pd.DataFrame()

def limpar_banco():
    """Limpa todos os dados do banco"""
    try:
        conn = sqlite3.connect(DB_TRILHAS_FILE)
        conn.execute("DELETE FROM trilhas")
        conn.commit()
        conn.close()
        st.success("Banco de dados limpo com sucesso!")
        return True
    except Exception as e:
        st.error(f"Erro ao limpar banco: {e}")
        return False

def tela_banco_dados():
    """Tela principal do gerenciamento do banco de dados"""
    
    st.title("📊 Gerenciamento do Banco de Dados")
    st.markdown("---")
    
    # Inicializar banco se necessário
    inicializar_banco()
    
    # Criar abas
    aba1, aba2, aba3 = st.tabs(["📤 Upload de Dados", "📋 Visualizar Dados", "⚙️ Configurações"])
    
    with aba1:
        st.header("📤 Upload de Planilha Excel")
        
        # Aviso importante sobre a regra de substituição
        st.warning("""
        ⚠️ **ATENÇÃO:** Cada novo upload substituirá completamente os dados existentes no banco!
        
        - Todos os dados atuais serão removidos
        - Apenas os dados do novo arquivo ficarão no banco
        - Esta operação não pode ser desfeita
        """)
        
        st.info("Faça upload de uma planilha Excel com as colunas: Trilhas, Atividades, Responsável, Tipo, Finalizado, Observações")
        
        # Mostrar informações do banco atual
        df_banco_atual = buscar_dados_banco()
        if not df_banco_atual.empty:
            st.info(f"📊 Banco atual: {len(df_banco_atual)} registros existentes")
        
        # Upload de arquivo
        arquivo = st.file_uploader(
            "Selecione um arquivo Excel ou CSV",
            type=["xlsx", "csv"],
            help="O arquivo deve conter as colunas: Trilhas, Atividades, Responsável, Tipo, Finalizado, Observações"
        )
        
        if arquivo is not None:
            # Mostrar informações do arquivo
            st.write(f"**Arquivo selecionado:** {arquivo.name}")
            st.write(f"**Tamanho:** {arquivo.size} bytes")
            
            # Carregar dados
            df = carregar_dados_excel(arquivo)
            
            if df is not None:
                st.write("**Prévia dos dados:**")
                st.dataframe(df.head(10), use_container_width=True)
                
                st.write(f"**Total de registros no arquivo:** {len(df)}")
                
                # Comparação com dados atuais
                if not df_banco_atual.empty:
                    st.info(f"📊 **Comparação:** {len(df_banco_atual)} registros atuais → {len(df)} novos registros")
                
                # Botões de ação
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("💾 Salvar no Banco (Substituir)", type="primary"):
                        # Confirmação adicional
                        if st.session_state.get('confirmar_substituicao', False):
                            if salvar_dados_banco(df):
                                st.session_state['confirmar_substituicao'] = False
                                st.rerun()
                        else:
                            st.session_state['confirmar_substituicao'] = True
                            st.warning("⚠️ Clique novamente para confirmar a substituição dos dados!")
                
                with col2:
                    if st.button("📥 Download como CSV"):
                        csv = df.to_csv(index=False)
                        st.download_button(
                            label="📥 Download CSV",
                            data=csv,
                            file_name="dados_exportados.csv",
                            mime="text/csv"
                        )
                
                with col3:
                    if st.button("📊 Download como Excel"):
                        buffer = io.BytesIO()
                        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                            df.to_excel(writer, sheet_name='Dados', index=False)
                        buffer.seek(0)
                        st.download_button(
                            label="📊 Download Excel",
                            data=buffer.read(),
                            file_name="dados_exportados.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
    
    with aba2:
        st.header("📋 Dados do Banco")
        
        # Buscar dados do banco
        df_banco = buscar_dados_banco()
        
        if not df_banco.empty:
            st.write(f"**Total de registros no banco:** {len(df_banco)}")
            
            # Filtros
            st.subheader("🔍 Filtros")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                filtro_trilhas = st.selectbox(
                    "Filtrar por Trilhas:",
                    options=["Todas"] + list(df_banco['Trilhas'].unique()) if 'Trilhas' in df_banco.columns else ["Todas"]
                )
            
            with col2:
                filtro_tipo = st.selectbox(
                    "Filtrar por Tipo:",
                    options=["Todos"] + list(df_banco['Tipo'].unique()) if 'Tipo' in df_banco.columns else ["Todos"]
                )
            
            with col3:
                filtro_finalizado = st.selectbox(
                    "Filtrar por Status:",
                    options=["Todos"] + list(df_banco['Finalizado'].unique()) if 'Finalizado' in df_banco.columns else ["Todos"]
                )
            
            # Aplicar filtros
            df_filtrado = df_banco.copy()
            
            if filtro_trilhas != "Todas":
                df_filtrado = df_filtrado[df_filtrado['Trilhas'] == filtro_trilhas]
            
            if filtro_tipo != "Todos":
                df_filtrado = df_filtrado[df_filtrado['Tipo'] == filtro_tipo]
            
            if filtro_finalizado != "Todos":
                df_filtrado = df_filtrado[df_filtrado['Finalizado'] == filtro_finalizado]
            
            st.write(f"**Registros filtrados:** {len(df_filtrado)}")
            
            # Exibir tabela
            st.dataframe(df_filtrado, use_container_width=True)
            
            # Estatísticas
            st.subheader("📊 Estatísticas")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if 'Trilhas' in df_banco.columns:
                    st.write("**Por Trilhas:**")
                    trilhas_counts = df_banco['Trilhas'].value_counts().head(5)
                    for trilha, count in trilhas_counts.items():
                        st.write(f"  • {trilha}: {count}")
            
            with col2:
                if 'Tipo' in df_banco.columns:
                    st.write("**Por Tipo:**")
                    tipo_counts = df_banco['Tipo'].value_counts()
                    for tipo, count in tipo_counts.items():
                        st.write(f"  • {tipo}: {count}")
            
            with col3:
                if 'Finalizado' in df_banco.columns:
                    st.write("**Por Status:**")
                    finalizado_counts = df_banco['Finalizado'].value_counts()
                    for status, count in finalizado_counts.items():
                        st.write(f"  • {status}: {count}")
            
            with col4:
                if 'Responsável' in df_banco.columns:
                    st.write("**Por Responsável:**")
                    responsavel_counts = df_banco['Responsável'].value_counts().head(5)
                    for responsavel, count in responsavel_counts.items():
                        st.write(f"  • {responsavel}: {count}")
        
        else:
            st.info("📭 Nenhum dado encontrado no banco de dados.")
            st.write("Faça upload de uma planilha na aba 'Upload de Dados' para começar.")
    
    with aba3:
        st.header("⚙️ Configurações do Banco")
        
        # Informações do banco
        st.subheader("📁 Informações do Banco")
        
        if os.path.exists(DB_TRILHAS_FILE):
            tamanho = os.path.getsize(DB_TRILHAS_FILE)
            st.write(f"**Localização:** {os.path.abspath(DB_TRILHAS_FILE)}")
            st.write(f"**Tamanho:** {tamanho} bytes")
            
            # Contar registros
            df_banco = buscar_dados_banco()
            st.write(f"**Total de registros:** {len(df_banco)}")
        else:
            st.warning("Banco de dados não encontrado!")
        
        st.markdown("---")
        
        # Ações de manutenção
        st.subheader("🔧 Ações de Manutenção")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🗑️ Limpar Banco", type="secondary"):
                if st.session_state.get('confirmar_limpeza', False):
                    if limpar_banco():
                        st.rerun()
                else:
                    st.session_state['confirmar_limpeza'] = True
                    st.warning("Clique novamente para confirmar a limpeza do banco!")
        
        with col2:
            if st.button("💾 Fazer Backup", type="secondary"):
                backup_data, backup_filename = fazer_backup_banco()
                if backup_data and backup_filename:
                    st.success("✅ Backup criado com sucesso!")
                    st.download_button(
                        label=f"📥 Download Backup: {backup_filename}",
                        data=backup_data,
                        file_name=backup_filename,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                else:
                    st.warning("⚠️ Nenhum dado para fazer backup!")
        
        with col3:
            if st.button("🔄 Recarregar Dados"):
                st.rerun()
        
        # Template de planilha
        st.markdown("---")
        st.subheader("📋 Template de Planilha")
        
        st.info("Use este template como base para sua planilha:")
        
        template_data = {
            'Trilhas': [
                'Trilha de Crédito CMR248.1',
                'Trilha de Crédito CMR248.1',
                'Trilha de Crédito CMR248.1'
            ],
            'Atividades': [
                'CMR248.1 - BPH004197 - 43. Administrar deferimentos de crédito documentado',
                'CMR248.1 - BPH004198 - 44. Validar documentação',
                'CMR248.1 - BPH004199 - 45. Aprovar crédito'
            ],
            'Responsável': ['João Silva', 'Maria Santos', 'Pedro Costa'],
            'Tipo': ['Análise', 'Validação', 'Aprovação'],
            'Finalizado': ['Não', 'Não', 'Não'],
            'Observações': [
                'Primeira etapa da trilha',
                'Verificação dos documentos',
                'Decisão final sobre o crédito'
            ]
        }
        
        df_template = pd.DataFrame(template_data)
        st.dataframe(df_template, use_container_width=True)
        
        # Download do template
        if st.button("📥 Download Template"):
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df_template.to_excel(writer, sheet_name='Template', index=False)
            buffer.seek(0)
            st.download_button(
                label="📥 Download Template Excel",
                data=buffer.read(),
                file_name="template_trilhas.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

if __name__ == "__main__":
    tela_banco_dados()