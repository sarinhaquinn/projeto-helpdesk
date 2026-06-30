import sqlite3
import pandas as pd

def criar_tabela():
    conexao = sqlite3.connect("chamados.db")
    cursor = conexao.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chamados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT,
            descricao TEXT
        )
    """)
    conexao.commit()
    conexao.close()

def exibir_menu():
    print("\n" + "="*30)
    print("       SISTEMA HELP DESK")
    print("="*30)
    print("1 - Cadastrar Novo Chamado")
    print("2 - Listar Chamados")
    print("3 - Exportar para Excel")
    print("4 - Sair do Sistema")
    print("="*30)

def cadastrar_chamado():
    print("\n--- NOVO CHAMADO ---")
    titulo = input("Título do problema: ")
    descricao = input("Descrição detalhada: ")
    
    conexao = sqlite3.connect("chamados.db")
    cursor = conexao.cursor()
    
    # CORREÇÃO: Os valores (titulo, descricao) entram como segundo argumento do execute
    cursor.execute(
        "INSERT INTO chamados (titulo, descricao) VALUES (?, ?)", 
        (titulo, descricao)
    )
    
    conexao.commit()
    conexao.close()
    print("\n✅ [Sucesso] Chamado cadastrado no Banco de Dados!")

def listar_chamados():
    print("\n--- LISTA DE CHAMADOS ---")
    
    conexao = sqlite3.connect("chamados.db")
    cursor = conexao.cursor()
    
    # CORREÇÃO: Fechamento correto dos parênteses
    cursor.execute("SELECT id, titulo, descricao FROM chamados")
    dados = cursor.fetchall()
    conexao.close()
    
    if not dados:
        print("ℹ️ Nenhum chamado cadastrado ainda.")
        return
        
    for linha in dados:
        # CORREÇÃO: Índices numéricos sem aspas
        print(f"\n🎫 ID: {linha[0]}")
        print(f"📌 Título: {linha[1]}")
        print(f"📝 Descrição: {linha[2]}")
        print("-" * 20)

def exportar_para_excel():
    print("\n📊 --- Exportando para Excel ---")
    
    conexao = sqlite3.connect("chamados.db")
    
    # O pandas lê o banco e joga direto em um DataFrame
    df = pd.read_sql_query("SELECT id, titulo, descricao FROM chamados", conexao)
    conexao.close()
    
    if df.empty:
        print("⚠️ [Aviso] Não há chamados para exportar.")
        return
        
    # Salva o arquivo na mesma pasta do projeto
    df.to_excel("relatorio_chamados.xlsx", index=False)
    print("🚀 [Sucesso] Arquivo 'relatorio_chamados.xlsx' criado na pasta do projeto!")

def iniciar_sistema():
    criar_tabela()
    
    while True:
        exibir_menu()
        opcao = input("Escolha uma opção (1-4): ").strip()
        
        if opcao == "1":
            cadastrar_chamado()
        elif opcao == "2":
            listar_chamados()
        elif opcao == "3":
            exportar_para_excel()
        elif opcao == "4":
            print("\n👋 Obrigado por usar o sistema! Encerrando...")
            break
        else:
            print("\n❌ [Erro] Opção inválida! Digite 1, 2, 3 ou 4.")

if __name__ == "__main__":
    iniciar_sistema()