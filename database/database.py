import sqlite3
import os

# Caminho absoluto para musicas.db dentro da pasta database/
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "musicas.db")


def conectar_banco():
    conn = sqlite3.connect(DB_PATH)
    return conn


def criar_tabela():
    conn = conectar_banco()
    cursor = conn.cursor()

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

    conn.commit()
    conn.close()