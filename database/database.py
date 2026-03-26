import sqlite3 #iblioteca nativa do Python pra trabalhar com banco de dados SQLite (arquivo .db)
import os #usada pra mexer com arquivos, pastas e caminhos do sistema

def get_caminho_banco():
   #encontra o caminho da pasta appdata, e cria a pasta "gralha"
    pasta = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "Gralha") 
    #Cria a pasta "Gralha" se ela não existir
    os.makedirs(pasta, exist_ok=True)
    #Retorna o caminho completo do banco 
    return os.path.join(pasta, "musicas.db")

def conectar_banco():
    #Cria (ou abre) o banco SQLite no caminho definido antes
    conn = sqlite3.connect(get_caminho_banco())
    #Retorna a conexão pra ser usada em outras partes do código
    return conn

def criar_tabela():
    #abre a conexão com o banco de dados
    conn = conectar_banco()
    #Cria um cursor (Cursor é o objeto que executa comandos SQL)
    cursor = conn.cursor()
    #O cursor executa a query
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS musicas ( #Cria a tabela musicas se ela não existir
        id INTEGER PRIMARY KEY AUTOINCREMENT, #responsável por atribuir um id único a linha
        nome TEXT, #cria coluna nome com o tipo de variável text
        artista TEXT, #cria coluna artista com o tipo de variável text
        album TEXT, #cria coluna album com o tipo de variável text
        ano INTEGER, #cria coluna album com o tipo de variável integer
        cifra TEXT, #cria coluna cifra com o tipo de variável text
        tablatura TEXT, #cria coluna tablatura com o tipo de variável text
        caminho_audio TEXT, #cria coluna caminho_audio com o tipo de variável text
        caminho_partitura TEXT #cria coluna caminho_partitura com o tipo de variável text
    )
    """)
    conn.commit() #salva as alterações no banco de dados
    conn.close() #fecha a conexão com o banco