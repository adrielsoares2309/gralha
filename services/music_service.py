import sqlite3
import os

# Aponta para database/musicas.db a partir da raiz do projeto
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "database", "musicas.db")


def buscar_musica(nome):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT artista, album, ano, tablatura, caminho_audio, caminho_partitura
        FROM musicas
        WHERE nome LIKE ?
    """, (f"%{nome}%",))

    resultado = cursor.fetchone()
    conn.close()
    return resultado


def buscar_musica_completa(nome):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, nome, artista, album, ano, cifra, tablatura, caminho_audio, caminho_partitura
        FROM musicas
        WHERE nome LIKE ?
    """, (f"%{nome}%",))

    resultado = cursor.fetchone()
    conn.close()
    return resultado


def add_musica(nome, artista, album, ano, cifra, tablatura, audio, partitura):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO musicas
        (nome, artista, album, ano, cifra, tablatura, caminho_audio, caminho_partitura)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (nome, artista, album, ano, cifra, tablatura, audio, partitura))

    conn.commit()
    conn.close()


def editar_musica(id, nome, artista, album, ano, cifra, tablatura, audio, partitura):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE musicas
        SET nome = ?, artista = ?, album = ?, ano = ?, cifra = ?, tablatura = ?,
            caminho_audio = ?, caminho_partitura = ?
        WHERE id = ?
    """, (nome, artista, album, ano, cifra, tablatura, audio, partitura, id))

    conn.commit()
    conn.close()


def excluir_musica(id):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM musicas WHERE id = ?", (id,))

    conn.commit()
    conn.close()