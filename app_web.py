import streamlit as st
import sqlite3
import pandas as pd


st.set_page_config(page_title="Helpdesk Web", page_icon="🎫", layout="centered")


def criar_tabela():
    conexao = sqlite3.connect("chamados.db")
    cursor = conexao.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chamados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT,
            descricao TEXT, 
            status TEXT DEFAULT 'Aberto'
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            username TEXT PRIMARY KEY,
            senha TEXT,
            perfil TEXT
        )
    """)
    
    cursor.execute("INSERT OR IGNORE INTO usuarios VALUES ('joao', '123', 'usuario')")
    cursor.execute("INSERT OR IGNORE INTO usuarios VALUES ('maria_ti', '123', 'tecnico')")
    
    conexao.commit()
    conexao.close()

criar_tabela() 


if "logado" not in st.session_state:
    st.session_state.logado = False
    st.session_state.usuario_atual = None
    st.session_state.perfil_atual = None

st.markdown(
    """
    <div style="
        background-color: #1E1035; 
        padding: 20px; 
        border-radius: 10px; 
        border: 3px solid #FFFFFF; 
        text-align: center;
        box-shadow: 0px 0px 25px #8A2BE2;
    ">
        <h1 style="
            color: #FFFFFF; 
            margin: 0; 
            font-family: Arial, sans-serif;
            font-weight: bold;
        ">
            Sistema Helpdesk - By Sarinha
        </h1>
    </div>
    """, 
    unsafe_allow_html=True
)


if not st.session_state.logado:
    st.subheader("Área de Acesso")
    campo_usuario = st.text_input("Usuário").strip().lower()
    campo_senha = st.text_input("Senha", type="password")

    if st.button("Entrar", type="primary"):
        conexao = sqlite3.connect("chamados.db")
        cursor = conexao.cursor()

        cursor.execute("SELECT perfil FROM usuarios WHERE username = ? AND senha = ?", (campo_usuario, campo_senha))
        resultado = cursor.fetchone()
        conexao.close()

        if resultado:
            st.session_state.logado = True
            st.session_state.usuario_atual = campo_usuario
            st.session_state.perfil_atual = resultado[0]
            st.rerun()  
        else: 
            st.error("❌ Usuário ou senha incorretos!")


else:
    
    col1, col2 = st.columns([4, 1])
    with col1:
        st.write(f"Olá, **{st.session_state.usuario_atual}** ({st.session_state.perfil_atual.upper()})")
        
    with col2:
        if st.button("Sair 🚪"):
            st.session_state.logado = False
            st.session_state.usuario_atual = None
            st.session_state.perfil_atual = None
            st.rerun()

        
    if "usuario" in st.session_state.perfil_atual.lower():
        
        aba_cadastro, = st.tabs(["📝 Novo Chamado"])
        aba_listagem = None
    else:
        
        aba_listagem, = st.tabs(["📋 Visualizar Chamados"])
        aba_cadastro = None

   
    if aba_cadastro:
        with aba_cadastro:
            st.subheader("Registrar uma nova ocorrência")
            
            titulo_chamado = st.text_input("Título do Problema", placeholder="Ex: Sistema fora do ar")
            descricao_chamado = st.text_area("Descrição detalhada", placeholder="Descreva o erro...")
            
            if st.button("Salvar Chamado", type="primary"):
                if titulo_chamado.strip() == "" or descricao_chamado.strip() == "":
                    st.warning("⚠️ Por favor, preencha todos os campos!")
                else:
                    conexao = sqlite3.connect("chamados.db")
                    cursor = conexao.cursor()
                    cursor.execute(
                        "INSERT INTO chamados (titulo, descricao) VALUES (?, ?)", 
                        (titulo_chamado, descricao_chamado)
                    )
                    conexao.commit()
                    conexao.close()
                    st.success("✅ Chamado registrado com sucesso!")

    
    if aba_listagem:
        with aba_listagem:
            st.subheader("Chamados Registrados")
            
            conexao = sqlite3.connect("chamados.db")
            dados = pd.read_sql_query("SELECT id AS 'Código', titulo AS 'Título', descricao AS 'Descrição', status AS 'Status' FROM chamados", conexao)
            conexao.close()
            
            if not dados.empty:
                st.dataframe(dados, use_container_width=True, hide_index=True)
                
                st.markdown("---")
                st.subheader("🛠️ Painel de Controle do Técnico")
                
                lista_ids = dados['Código'].tolist()
                id_selecionado = st.selectbox("Selecione o Código do chamado:", lista_ids)
                
                col_resolver, col_apagar = st.columns(2)
                
                with col_resolver:
                    conexao_status = sqlite3.connect("chamados.db")
                    cursor_status = conexao_status.cursor()
                    cursor_status.execute("SELECT status FROM chamados WHERE id = ?", (id_selecionado,))
                    status_atual_tupla = cursor_status.fetchone()
                    conexao_status.close()
                    
                    status_atual = status_atual_tupla[0] if status_atual_tupla else "Aberto"
                    
                    texto_botao = "🔄 Reabrir Chamado" if status_atual == "Resolvido" else "✅ Marcar como Resolvido"
                    
                    if st.button(texto_botao, use_container_width=True):
                        novo_status = "Aberto" if status_atual == "Resolvido" else "Resolvido"
                        
                        conexao_btn = sqlite3.connect("chamados.db")
                        cursor_btn = conexao_btn.cursor()
                        cursor_btn.execute("UPDATE chamados SET status = ? WHERE id = ?", (novo_status, id_selecionado))
                        conexao_btn.commit()
                        conexao_btn.close()
                        
                        st.success(f"Status do chamado № {id_selecionado} alterado para {novo_status}!")
                        st.rerun()
                
                with col_apagar:
                    if st.button("🗑️ Apagar Chamado", type="secondary", use_container_width=True):
                        conexao_btn = sqlite3.connect("chamados.db")
                        cursor_btn = conexao_btn.cursor()
                        cursor_btn.execute("DELETE FROM chamados WHERE id = ?", (id_selecionado,))
                        conexao_btn.commit()
                        conexao_btn.close()
                        
                        st.error(f"Chamado № {id_selecionado} foi apagado do sistema!")
                        st.rerun()
            else:
                st.info("ℹ️ Nenhum chamado cadastrado até o momento.")
