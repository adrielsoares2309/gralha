import tkinter as tk
from tkinter import filedialog, messagebox
from services.music_service import add_musica
import os

BG        = "#0a0a0a"
BG2       = "#141414"
BG3       = "#1e1e1e"
VERMELHO  = "#cc0000"
VERM_HOV  = "#ff1a1a"
BRANCO    = "#f0f0f0"
CINZA     = "#888888"
FONTE     = ("Courier New", 10)
FONTE_T   = ("Courier New", 11, "bold")
FONTE_TIT = ("Courier New", 16, "bold")

caminho_audio     = ""
caminho_partitura = ""


def estilo_botao(btn, cor=VERMELHO, hover=VERM_HOV):
    btn.config(bg=cor, fg=BRANCO, relief="flat",
               activebackground=hover, activeforeground=BRANCO,
               cursor="hand2", font=FONTE_T, bd=0, padx=10, pady=6)
    btn.bind("<Enter>", lambda e: btn.config(bg=hover))
    btn.bind("<Leave>", lambda e: btn.config(bg=cor))


def estilo_botao_secundario(btn):
    estilo_botao(btn, cor=BG3, hover="#2a2a2a")


def estilo_entrada(entry):
    entry.config(bg=BG2, fg=BRANCO, insertbackground=BRANCO,
                 relief="flat", font=FONTE_T, bd=0)


def label_campo(pai, texto):
    tk.Label(pai, text=texto, bg=BG, fg=CINZA,
             font=("Courier New", 8, "bold")).pack(anchor="w", padx=40, pady=(10, 2))


def abrir_janela_adicionar():

    global caminho_audio, caminho_partitura
    caminho_audio = ""
    caminho_partitura = ""

    def selecionar_audio():
        global caminho_audio
        arquivo = filedialog.askopenfilename(
            parent=janela, title="Selecionar Áudio",
            filetypes=[("Audio files", "*.mp3 *.wav"), ("All files", "*.*")]
        )
        if arquivo:
            caminho_audio = arquivo
            label_audio.config(text=f"▶  {os.path.basename(arquivo)}", fg=BRANCO)
        janela.grab_set()
        janela.focus_force()

    def selecionar_partitura():
        global caminho_partitura
        arquivo = filedialog.askopenfilename(
            parent=janela, title="Selecionar Partitura",
            filetypes=[("PDF files", "*.pdf")]
        )
        if arquivo:
            caminho_partitura = arquivo
            label_partitura.config(text=f"◉  {os.path.basename(arquivo)}", fg=BRANCO)
        janela.grab_set()
        janela.focus_force()

    def salvar():
        nome      = entrada_nome.get().strip()
        artista   = entrada_artista.get().strip()
        album     = entrada_album.get().strip()
        ano_str   = entrada_ano.get().strip()
        tablatura = texto_tablatura.get("1.0", "end").strip()

        if not nome or not artista:
            messagebox.showwarning("Atenção", "Nome e Artista são obrigatórios!")
            return

        ano = None
        if ano_str:
            if not ano_str.isdigit() or len(ano_str) != 4:
                messagebox.showwarning("Atenção", "Ano inválido! Use o formato: 2024")
                return
            ano = int(ano_str)

        add_musica(nome, artista, album, ano, tablatura, caminho_audio, caminho_partitura)
        messagebox.showinfo("Sucesso", f'"{nome}" salva com sucesso!')
        janela.destroy()

    # ── Janela ──────────────────────────────────────────
    janela = tk.Toplevel()
    janela.title("Adicionar Música")
    janela.geometry("420x700")
    janela.configure(bg=BG)
    janela.resizable(False, False)
    janela.grab_set()
    janela.focus_force()

    tk.Label(janela, text="ADICIONAR MÚSICA", bg=BG, fg=VERMELHO,
             font=FONTE_TIT).pack(pady=(24, 2))
    tk.Label(janela, text="─" * 36, bg=BG, fg=BG3).pack(pady=(0, 8))

    label_campo(janela, "NOME")
    entrada_nome = tk.Entry(janela, width=36)
    estilo_entrada(entrada_nome)
    entrada_nome.pack(padx=40, ipady=6, fill="x")

    label_campo(janela, "ARTISTA")
    entrada_artista = tk.Entry(janela, width=36)
    estilo_entrada(entrada_artista)
    entrada_artista.pack(padx=40, ipady=6, fill="x")

    label_campo(janela, "ÁLBUM")
    entrada_album = tk.Entry(janela, width=36)
    estilo_entrada(entrada_album)
    entrada_album.pack(padx=40, ipady=6, fill="x")

    label_campo(janela, "ANO")
    entrada_ano = tk.Entry(janela, width=36)
    estilo_entrada(entrada_ano)
    entrada_ano.pack(padx=40, ipady=6, fill="x")

    label_campo(janela, "TABLATURA (ASCII)")
    exemplo = (
        "E|--0--| (Mi aguda)\n"
        "B|--2--|\n"
        "G|--2--|\n"
        "D|--2--|\n"
        "A|--0--|\n"
        "E|-----| (Mi grave)"
    )
    texto_tablatura = tk.Text(janela, height=7, width=36,
                               font=("Courier New", 10),
                               bg=BG2, fg=BRANCO, insertbackground=BRANCO,
                               relief="flat", bd=0, padx=8, pady=8)
    texto_tablatura.insert("1.0", exemplo)
    texto_tablatura.pack(padx=40, fill="x")

    tk.Label(janela, text="─" * 36, bg=BG, fg=BG3).pack(pady=(12, 6))

    btn_audio = tk.Button(janela, text="♪  SELECIONAR ÁUDIO", command=selecionar_audio)
    estilo_botao_secundario(btn_audio)
    btn_audio.pack(padx=40, pady=(0, 4), fill="x")

    label_audio = tk.Label(janela, text="Nenhum áudio selecionado",
                            bg=BG, fg=CINZA, font=FONTE)
    label_audio.pack(padx=40, anchor="w")

    btn_partitura = tk.Button(janela, text="◉  SELECIONAR PARTITURA", command=selecionar_partitura)
    estilo_botao_secundario(btn_partitura)
    btn_partitura.pack(padx=40, pady=(8, 4), fill="x")

    label_partitura = tk.Label(janela, text="Nenhuma partitura selecionada",
                                bg=BG, fg=CINZA, font=FONTE)
    label_partitura.pack(padx=40, anchor="w")

    tk.Label(janela, text="─" * 36, bg=BG, fg=BG3).pack(pady=(12, 6))

    btn_salvar = tk.Button(janela, text="✔  SALVAR MÚSICA", command=salvar)
    estilo_botao(btn_salvar)
    btn_salvar.pack(padx=40, pady=(0, 20), fill="x")