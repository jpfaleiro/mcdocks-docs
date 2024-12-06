import streamlit as st  # type: ignore
import sqlite3
import pandas as pd  # type: ignore
import random

# Funções do Banco de Dados
def conectar():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    criar_tabelas(conn, cursor)
    return conn, cursor


def criar_tabelas(conn, cursor):
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT UNIQUE,
            email TEXT,
            senha TEXT)"""
    )

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS livros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT UNIQUE,
            categoria TEXT)"""
    )

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS historico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER,
            livro_id INTEGER,
            avaliacao INTEGER,
            FOREIGN KEY(usuario_id) REFERENCES usuarios(id),
            FOREIGN KEY(livro_id) REFERENCES livros(id))"""
    )

    carregar_livros_iniciais(conn, cursor)


def carregar_livros_iniciais(conn, cursor):
    try:
        livros_df = pd.read_csv("books.csv")
        for _, row in livros_df.iterrows():
            titulo = row["title"]
            categoria = row["genre"]
            cursor.execute(
                "INSERT OR IGNORE INTO livros (titulo, categoria) VALUES (?, ?)",
                (titulo, categoria),
            )
        conn.commit()
    except FileNotFoundError:
        st.warning("Arquivo books.csv não encontrado. Nenhum livro inicial foi carregado.")
    except KeyError as e:
        st.error(f"Coluna não encontrada no CSV: {e}")
        st.stop()


def adicionar_usuario(nome, email, senha):
    conn, cursor = conectar()
    cursor.execute(
        "INSERT INTO usuarios (nome, email, senha) VALUES (?, ?, ?)",
        (nome, email, senha),
    )
    conn.commit()
    conn.close()


def verificar_usuario(nome, senha):
    conn, cursor = conectar()
    cursor.execute("SELECT * FROM usuarios WHERE nome = ? AND senha = ?", (nome, senha))
    user = cursor.fetchone()
    conn.close()
    return user


def adicionar_livro(titulo, categoria="Desconhecida"):
    conn, cursor = conectar()
    cursor.execute(
        "INSERT OR IGNORE INTO livros (titulo, categoria) VALUES (?, ?)",
        (titulo, categoria),
    )
    cursor.execute("SELECT id FROM livros WHERE titulo = ?", (titulo,))
    livro_id = cursor.fetchone()[0]
    conn.commit()
    conn.close()
    return livro_id


def adicionar_historico(usuario_id, livro_id, avaliacao=None):
    conn, cursor = conectar()
    cursor.execute(
        "INSERT INTO historico (usuario_id, livro_id, avaliacao) VALUES (?, ?, ?)",
        (usuario_id, livro_id, avaliacao),
    )
    conn.commit()
    conn.close()


def obter_historico(usuario_id):
    conn, cursor = conectar()
    cursor.execute(
        "SELECT titulo, avaliacao FROM livros JOIN historico ON livros.id = historico.livro_id WHERE historico.usuario_id = ?",
        (usuario_id,),
    )
    historico = cursor.fetchall()
    conn.close()
    return historico


def recomendar_livros(usuario_id):
    conn, cursor = conectar()
    cursor.execute(
        """
        SELECT titulo FROM livros 
        WHERE id NOT IN (SELECT livro_id FROM historico WHERE usuario_id = ?)
        """,
        (usuario_id,),
    )
    livros_disponiveis = [livro[0] for livro in cursor.fetchall()]
    conn.close()
    return random.sample(livros_disponiveis, min(5, len(livros_disponiveis))) if livros_disponiveis else ["Nenhuma recomendação disponível no momento."]

# Interface do Streamlit
st.sidebar.title("Sistema de Recomendações de Livros")
opcao = st.sidebar.selectbox(
    "Escolha uma página",
    ["Autenticação", "Cadastro", "Perfil", "Histórico de Livros", "Recomendação", "Logout"],
)

# Página de Cadastro
if opcao == "Cadastro":
    st.title("Cadastro")
    nome = st.text_input("Nome")
    email = st.text_input("Email")
    senha = st.text_input("Senha", type="password")
    if st.button("Cadastrar"):
        try:
            adicionar_usuario(nome, email, senha)
            st.success("Usuário cadastrado com sucesso!")
        except sqlite3.IntegrityError:
            st.error("O nome de usuário já está cadastrado.")

# Página de Autenticação
elif opcao == "Autenticação":
    st.title("Autenticação")
    nome = st.text_input("Nome")
    senha = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        usuario = verificar_usuario(nome, senha)
        if usuario:
            st.session_state["usuario"] = usuario
            st.success("Login bem-sucedido!")
        else:
            st.error("Credenciais inválidas")

# Página de Perfil
elif opcao == "Perfil":
    st.title("Perfil do Usuário")
    if "usuario" in st.session_state:
        usuario = st.session_state["usuario"]
        st.write(f"Nome: {usuario[1]}")
        st.write(f"Email: {usuario[2]}")
    else:
        st.warning("Faça login para acessar
