import tkinter as tk
import os
from services.music_service import buscar_musica_completa
from interface.add_music_window import abrir_janela_adicionar
from interface.edit_music_window import abrir_janela_editar

# ── Paleta Preto e Branco ────────────────────────────────
BG        = "#000000"
BG2       = "#111111"
BG3       = "#222222"
DESTAQUE  = "#ffffff"
DEST_HOV  = "#cccccc"
BRANCO    = "#ffffff"
CINZA     = "#888888"
CINZA2    = "#555555"
FONTE     = ("Courier New", 10)
FONTE_T   = ("Courier New", 11, "bold")
FONTE_TIT = ("Courier New", 16, "bold")

tablatura    = ""
cifra        = ""
audio        = ""
partitura    = ""
musica_atual = None


def estilo_botao(btn, cor=DESTAQUE, hover=DEST_HOV):
    btn.config(bg=cor, fg=BG, relief="flat",
               activebackground=hover, activeforeground=BG,
               cursor="hand2", font=FONTE_T, bd=0, padx=12, pady=6)
    btn.bind("<Enter>", lambda e: btn.config(bg=hover))
    btn.bind("<Leave>", lambda e: btn.config(bg=cor))


def estilo_botao_secundario(btn):
    btn.config(bg=BG3, fg=BRANCO, relief="flat",
               activebackground="#333333", activeforeground=BRANCO,
               cursor="hand2", font=FONTE_T, bd=0, padx=12, pady=6)
    btn.bind("<Enter>", lambda e: btn.config(bg="#333333"))
    btn.bind("<Leave>", lambda e: btn.config(bg=BG3))


def iniciar_interface():

    global tablatura, audio, partitura, musica_atual

    def buscar():
        global tablatura, cifra, audio, partitura, musica_atual

        nome = entrada.get()
        resultado = buscar_musica_completa(nome)

        for widget in frame_resultado.winfo_children():
            widget.destroy()

        if resultado:
            musica_atual = resultado
            _, nome_r, artista, album, ano, cifra, tablatura, audio, partitura = resultado

            def info_linha(icone, label, valor):
                f = tk.Frame(frame_resultado, bg=BG2)
                f.pack(fill="x", padx=16, pady=2)
                tk.Label(f, text=icone, bg=BG2, fg=BRANCO,
                         font=FONTE_T, width=2).pack(side="left")
                tk.Label(f, text=label, bg=BG2, fg=CINZA,
                         font=("Courier New", 9)).pack(side="left", padx=(4, 8))
                tk.Label(f, text=valor or "—", bg=BG2, fg=BRANCO,
                         font=FONTE_T, anchor="w").pack(side="left", fill="x", expand=True)

            tk.Label(frame_resultado, text="─" * 34, bg=BG2, fg=BG3).pack(pady=(10, 6))
            info_linha("♪", "NOME",    nome_r)
            info_linha("★", "ARTISTA", artista)
            info_linha("◈", "ÁLBUM",   album)
            info_linha("◷", "ANO",     str(ano) if ano else "—")

            if cifra:
                tk.Label(frame_resultado, text="CIFRA", bg=BG2, fg=CINZA,
                         font=("Courier New", 8, "bold")).pack(anchor="w", padx=16, pady=(10, 2))
                txt_cifra = tk.Text(frame_resultado, height=6, font=("Courier New", 10),
                              bg=BG3, fg=BRANCO, relief="flat", bd=0,
                              padx=10, pady=8, state="normal")
                txt_cifra.insert("1.0", cifra)
                txt_cifra.config(state="disabled")
                txt_cifra.pack(padx=16, fill="x", pady=(0, 4))

            if tablatura:
                tk.Label(frame_resultado, text="TABLATURA", bg=BG2, fg=CINZA,
                         font=("Courier New", 8, "bold")).pack(anchor="w", padx=16, pady=(10, 2))
                txt = tk.Text(frame_resultado, height=8, font=("Courier New", 10),
                              bg=BG3, fg=BRANCO, relief="flat", bd=0,
                              padx=10, pady=8, state="normal")
                txt.insert("1.0", tablatura)
                txt.config(state="disabled")
                txt.pack(padx=16, fill="x", pady=(0, 4))

            if audio:
                tk.Label(frame_resultado, text="ÁUDIO", bg=BG2, fg=CINZA,
                         font=("Courier New", 8, "bold")).pack(anchor="w", padx=16, pady=(6, 2))
                tk.Label(frame_resultado, text=f"▶  {os.path.basename(audio)}",
                         bg=BG2, fg=BRANCO, font=FONTE).pack(anchor="w", padx=16)

            if partitura:
                tk.Label(frame_resultado, text="PARTITURA", bg=BG2, fg=CINZA,
                         font=("Courier New", 8, "bold")).pack(anchor="w", padx=16, pady=(6, 2))
                tk.Label(frame_resultado, text=f"◉  {os.path.basename(partitura)}",
                         bg=BG2, fg=BRANCO, font=FONTE).pack(anchor="w", padx=16)

            tk.Label(frame_resultado, text="─" * 34, bg=BG2, fg=BG3).pack(pady=(10, 10))

        else:
            musica_atual = None
            tablatura = cifra = audio = partitura = ""
            tk.Label(frame_resultado, text="Música não encontrada",
                     bg=BG, fg=CINZA, font=FONTE).pack(pady=10)

        canvas.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))

    def abrir_cifra():
        if not cifra:
            return
        jan = tk.Toplevel(janela)
        jan.title("Cifra")
        jan.geometry("460x400")
        jan.configure(bg=BG)
        jan.grab_set()

        tk.Label(jan, text="── CIFRA ──", bg=BG, fg=BRANCO,
                 font=FONTE_TIT).pack(pady=(16, 8))

        frame = tk.Frame(jan, bg=BG2)
        frame.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        txt = tk.Text(frame, font=("Courier New", 12), bg=BG2, fg=BRANCO,
                      insertbackground=BRANCO, relief="flat",
                      state="normal", bd=0, padx=10, pady=10)
        txt.insert("1.0", cifra)
        txt.config(state="disabled")
        txt.pack(fill="both", expand=True)

    def abrir_tablatura():
        if not tablatura:
            return
        jan = tk.Toplevel(janela)
        jan.title("Tablatura")
        jan.geometry("460x340")
        jan.configure(bg=BG)
        jan.grab_set()

        tk.Label(jan, text="── TABLATURA ──", bg=BG, fg=BRANCO,
                 font=FONTE_TIT).pack(pady=(16, 8))

        frame = tk.Frame(jan, bg=BG2)
        frame.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        txt = tk.Text(frame, font=("Courier New", 12), bg=BG2, fg=BRANCO,
                      insertbackground=BRANCO, relief="flat",
                      state="normal", bd=0, padx=10, pady=10)
        txt.insert("1.0", tablatura)
        txt.config(state="disabled")
        txt.pack(fill="both", expand=True)

    def tocar_audio():
        if audio:
            caminho = os.path.join(os.path.dirname(__file__), "..", audio)
            if os.path.exists(caminho):
                os.startfile(caminho)

    def visualizar_partitura():
        if partitura:
            caminho = os.path.join(os.path.dirname(__file__), "..", partitura)
            if os.path.exists(caminho):
                os.startfile(caminho)

    def editar():
        if not musica_atual:
            return
        abrir_janela_editar(musica_atual, ao_salvar=buscar)

    # ── Janela principal ─────────────────────────────────
    janela = tk.Tk()
    janela.title("Guitar Library")
    janela.geometry("440x620")
    janela.configure(bg=BG)
    janela.resizable(False, True)

    canvas = tk.Canvas(janela, bg=BG, highlightthickness=0)
    scrollbar = tk.Scrollbar(janela, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    frame_main = tk.Frame(canvas, bg=BG)
    frame_id = canvas.create_window((0, 0), window=frame_main, anchor="nw")

    def atualizar_scroll(event=None):
        canvas.configure(scrollregion=canvas.bbox("all"))
        canvas.itemconfig(frame_id, width=canvas.winfo_width())

    frame_main.bind("<Configure>", atualizar_scroll)
    canvas.bind("<Configure>", lambda e: canvas.itemconfig(frame_id, width=e.width))
    canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

    tk.Label(frame_main, text="GUITAR LIBRARY", bg=BG, fg=BRANCO,
             font=("Courier New", 20, "bold")).pack(pady=(28, 2))
    tk.Label(frame_main, text="─" * 36, bg=BG, fg=BG3).pack()

    tk.Label(frame_main, text="BUSCAR MÚSICA", bg=BG, fg=CINZA,
             font=("Courier New", 8, "bold")).pack(pady=(20, 4))

    frame_busca = tk.Frame(frame_main, bg=BG2)
    frame_busca.pack(padx=40, fill="x")

    entrada = tk.Entry(frame_busca, font=FONTE_T, bg=BG2, fg=BRANCO,
                       insertbackground=BRANCO, relief="flat", bd=0, width=22)
    entrada.pack(side="left", padx=(12, 0), pady=10, fill="x", expand=True)
    entrada.bind("<Return>", lambda e: buscar())

    btn_buscar = tk.Button(frame_busca, text="BUSCAR", command=buscar)
    estilo_botao(btn_buscar)
    btn_buscar.pack(side="right", padx=6, pady=6)

    frame_resultado = tk.Frame(frame_main, bg=BG2)
    frame_resultado.pack(padx=40, pady=(10, 0), fill="x")

    tk.Label(frame_main, text="─" * 36, bg=BG, fg=BG3).pack(pady=(16, 12))

    def btn(texto, cmd, secundario=False):
        b = tk.Button(frame_main, text=texto, command=cmd)
        if secundario:
            estilo_botao_secundario(b)
        else:
            estilo_botao(b)
        b.pack(padx=40, pady=4, fill="x")

    btn("▶  TOCAR ÁUDIO",          tocar_audio)
    btn("♩  ABRIR TABLATURA",      abrir_tablatura)
    btn("≡  VISUALIZAR CIFRA",     abrir_cifra)
    btn("◉  VISUALIZAR PARTITURA", visualizar_partitura)

    tk.Label(frame_main, text="─" * 36, bg=BG, fg=BG3).pack(pady=(8, 8))

    btn("✎  EDITAR MÚSICA",          editar,                 secundario=True)
    btn("＋  ADICIONAR MÚSICA",       abrir_janela_adicionar, secundario=True)

    tk.Label(frame_main, text="", bg=BG).pack(pady=10)

    janela.mainloop()