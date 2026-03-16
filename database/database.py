import sqlite3

def conectar_banco():
    #Conecta ao banco de dados SQLite localizado no diretório database/musicas.db
    conn = sqlite3.connect("database/musicas.db") 
    return conn


def criar_tabela():
    conn = conectar_banco() # Variavel que usa a conexão conn, para criar um cursor para executar comandos SQL
    cursor = conn.cursor() # Cria um cursor a partir da conexão com o banco de dados e guarda esse cursor na variável cursor

    # Executa um comando SQL no banco de dados para criar a tabela "musicas"
    # caso ela ainda não exista
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS musicas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        artista TEXT,
        album TEXT,
        ano INTEGER,
        cifra TEXT,
        tablatura TEXT,
        caminho_audio TEXT,
        caminho_partitura TEXT
    )
    """)
    # Salva (confirma) as alterações feitas no banco de dados
    conn.commit()
    # Fecha a conexão com o banco de dados
    conn.close()