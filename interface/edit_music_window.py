import tkinter as tk
from tkinter import filedialog, messagebox
from services.music_service import editar_musica, excluir_musica
import os

BG        = "#000000"
BG2       = "#111111"
BG3       = "#222222"
DESTAQUE  = "#ffffff"
DEST_HOV  = "#cccccc"
BRANCO    = "#ffffff"
CINZA     = "#888888"
PERIGO    = "#555555"
PERIGO_HOV = "#333333"
FONTE     = ("Courier New", 10)
FONTE_T   = ("Courier New", 11, "bold")
FONTE_TIT = ("Courier New", 16, "bold")


def estilo_botao(btn, cor=DESTAQUE, hover=DEST_HOV):
    btn.config(bg=cor, fg=BG, relief="flat",
               activebackground=hover, activeforeground=BG,
               cursor="hand2", font=FONTE_T, bd=0, padx=10, pady=6)
    btn.bind("<Enter>", lambda e: btn.config(bg=hover))
    btn.bind("<Leave>", lambda e: btn.config(bg=cor))


def estilo_botao_secundario(btn):
    btn.config(bg=BG3, fg=BRANCO, relief="flat",
               activebackground="#333333", activeforeground=BRANCO,
               cursor="hand2", font=FONTE_T, bd=0, padx=10, pady=6)
    btn.bind("<Enter>", lambda e: btn.config(bg="#333333"))
    btn.bind("<Leave>", lambda e: btn.config(bg=BG3))


def estilo_entrada(entry):
    entry.config(bg=BG2, fg=BRANCO, insertbackground=BRANCO,
                 relief="flat", font=FONTE_T, bd=0)


def abrir_janela_editar(musica, ao_salvar=None):

    # musica = (id, nome, artista, album, ano, tablatura, caminho_audio, caminho_partitura)
    id_musica      = musica[0]
    novo_audio     = musica[6] or ""
    nova_partitura = musica[7] or ""

    def selecionar_audio():
        nonlocal novo_audio
        arquivo = filedialog.askopenfilename(
            parent=janela, title="Selecionar Áudio",
            filetypes=[("Audio files", "*.mp3 *.wav"), ("All files", "*.*")]
        )
        if arquivo:
            novo_audio = arquivo
            label_audio.config(text=f"▶  {os.path.basename(arquivo)}", fg=BRANCO)
        janela.grab_set()
        janela.focus_force()

    def selecionar_partitura():
        nonlocal nova_partitura
        arquivo = filedialog.askopenfilename(
            parent=janela, title="Selecionar Partitura",
            filetypes=[("PDF files", "*.pdf")]
        )
        if arquivo:
            nova_partitura = arquivo
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

        editar_musica(id_musica, nome, artista, album, ano, tablatura, novo_audio, nova_partitura)
        messagebox.showinfo("Sucesso", f'"{nome}" atualizada com sucesso!')
        if ao_salvar:
            ao_salvar()
        janela.destroy()

    def excluir():
        nome = entrada_nome.get().strip() or "esta música"
        if messagebox.askyesno("Confirmar exclusão",
                                f'Tem certeza que deseja excluir "{nome}"?'):
            excluir_musica(id_musica)
            messagebox.showinfo("Excluído", f'"{nome}" foi excluída.')
            if ao_salvar:
                ao_salvar()
            janela.destroy()

    # ── Janela com scroll ────────────────────────────────
    janela = tk.Toplevel()
    janela.title("Editar Música")
    janela.geometry("440x600")
    janela.configure(bg=BG)
    janela.resizable(False, True)
    janela.grab_set()
    janela.focus_force()

    canvas = tk.Canvas(janela, bg=BG, highlightthickness=0)
    scrollbar = tk.Scrollbar(janela, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    frame = tk.Frame(canvas, bg=BG)
    frame_id = canvas.create_window((0, 0), window=frame, anchor="nw")

    def atualizar_scroll(event=None):
        canvas.configure(scrollregion=canvas.bbox("all"))
        canvas.itemconfig(frame_id, width=canvas.winfo_width())

    frame.bind("<Configure>", atualizar_scroll)
    canvas.bind("<Configure>", lambda e: canvas.itemconfig(frame_id, width=e.width))
    canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

    def lbl(texto):
        tk.Label(frame, text=texto, bg=BG, fg=CINZA,
                 font=("Courier New", 8, "bold")).pack(anchor="w", padx=40, pady=(10, 2))

    def entrada_campo(valor=""):
        e = tk.Entry(frame, width=36)
        estilo_entrada(e)
        e.insert(0, valor)
        e.pack(padx=40, ipady=6, fill="x")
        return e

    tk.Label(frame, text="EDITAR MÚSICA", bg=BG, fg=BRANCO,
             font=FONTE_TIT).pack(pady=(24, 2))
    tk.Label(frame, text="─" * 36, bg=BG, fg=BG3).pack(pady=(0, 8))

    lbl("NOME")
    entrada_nome = entrada_campo(musica[1] or "")

    lbl("ARTISTA")
    entrada_artista = entrada_campo(musica[2] or "")

    lbl("ÁLBUM")
    entrada_album = entrada_campo(musica[3] or "")

    lbl("ANO")
    entrada_ano = entrada_campo(str(musica[4]) if musica[4] else "")

    lbl("TABLATURA (ASCII)")
    texto_tablatura = tk.Text(frame, height=7, width=36,
                               font=("Courier New", 10),
                               bg=BG2, fg=BRANCO, insertbackground=BRANCO,
                               relief="flat", bd=0, padx=8, pady=8)
    texto_tablatura.insert("1.0", musica[5] or "")
    texto_tablatura.pack(padx=40, fill="x")

    tk.Label(frame, text="─" * 36, bg=BG, fg=BG3).pack(pady=(12, 6))

    btn_audio = tk.Button(frame, text="♪  TROCAR ÁUDIO", command=selecionar_audio)
    estilo_botao_secundario(btn_audio)
    btn_audio.pack(padx=40, pady=(0, 4), fill="x")

    label_audio = tk.Label(
        frame,
        text=f"▶  {os.path.basename(musica[6])}" if musica[6] else "Nenhum áudio selecionado",
        bg=BG, fg=BRANCO if musica[6] else CINZA, font=FONTE
    )
    label_audio.pack(padx=40, anchor="w")

    btn_partitura = tk.Button(frame, text="◉  TROCAR PARTITURA", command=selecionar_partitura)
    estilo_botao_secundario(btn_partitura)
    btn_partitura.pack(padx=40, pady=(8, 4), fill="x")

    label_partitura = tk.Label(
        frame,
        text=f"◉  {os.path.basename(musica[7])}" if musica[7] else "Nenhuma partitura selecionada",
        bg=BG, fg=BRANCO if musica[7] else CINZA, font=FONTE
    )
    label_partitura.pack(padx=40, anchor="w")

    tk.Label(frame, text="─" * 36, bg=BG, fg=BG3).pack(pady=(12, 6))

    btn_salvar = tk.Button(frame, text="✔  SALVAR ALTERAÇÕES", command=salvar)
    estilo_botao(btn_salvar)
    btn_salvar.pack(padx=40, pady=(0, 6), fill="x")

    btn_excluir = tk.Button(frame, text="✖  EXCLUIR MÚSICA", command=excluir)
    btn_excluir.config(bg=PERIGO, fg=BRANCO, relief="flat",
                       activebackground=PERIGO_HOV, activeforeground=BRANCO,
                       cursor="hand2", font=FONTE_T, bd=0, padx=10, pady=6)
    btn_excluir.bind("<Enter>", lambda e: btn_excluir.config(bg=PERIGO_HOV))
    btn_excluir.bind("<Leave>", lambda e: btn_excluir.config(bg=PERIGO))
    btn_excluir.pack(padx=40, pady=(0, 30), fill="x")