import customtkinter as ctk
from tkinter import filedialog, messagebox
from services.music_service import editar_musica, excluir_musica
import os

# ── Paleta ───────────────────────────────────────────────
AZUL       = "#2B5BA8"
AZUL_HOV   = "#1E4280"
BRANCO     = "#ffffff"
FUNDO      = "#f0f0eb"
CARD_BG    = "#ffffff"
TEXTO      = "#1a1a1a"
SUBTEXTO   = "#666666"
CINZA_BD   = "#e0e0e0"


def abrir_janela_editar(musica, ao_salvar=None):

    # musica = (id, nome, artista, album, ano, cifra, tablatura, caminho_audio, caminho_partitura)
    id_musica      = musica[0]
    novo_audio     = musica[7] or ""
    nova_partitura = musica[8] or ""

    # ════════════════════════════════════════════════════
    # JANELA
    # ════════════════════════════════════════════════════
    janela = ctk.CTkToplevel()
    janela.title("Editar Música")
    janela.geometry("480x720")
    janela.configure(fg_color=FUNDO)
    janela.resizable(False, True)
    janela.grab_set()
    janela.focus_force()

    # ── Header ───────────────────────────────────────────
    header = ctk.CTkFrame(janela, fg_color=BRANCO, corner_radius=0)
    header.pack(fill="x")
    ctk.CTkLabel(
        header, text="Editar Música",
        font=ctk.CTkFont("Segoe UI", 16, "bold"),
        text_color=TEXTO
    ).pack(side="left", padx=24, pady=18)

    # ── Scroll ───────────────────────────────────────────
    scroll = ctk.CTkScrollableFrame(
        janela, fg_color=FUNDO, corner_radius=0,
        scrollbar_button_color=CINZA_BD,
        scrollbar_button_hover_color=SUBTEXTO
    )
    scroll.pack(fill="both", expand=True)

    # ── Helpers ──────────────────────────────────────────
    def secao(pai, titulo):
        ctk.CTkLabel(
            pai, text=titulo,
            font=ctk.CTkFont("Segoe UI", 10, "bold"),
            text_color=SUBTEXTO, anchor="w"
        ).pack(anchor="w", padx=24, pady=(16, 4))

    def campo_entrada(pai, valor="", placeholder=""):
        e = ctk.CTkEntry(
            pai, placeholder_text=placeholder,
            fg_color=BRANCO, border_color=CINZA_BD, border_width=1,
            text_color=TEXTO, placeholder_text_color=SUBTEXTO,
            font=ctk.CTkFont("Segoe UI", 12), corner_radius=8, height=40
        )
        if valor:
            e.insert(0, valor)
        e.pack(fill="x", padx=24, pady=(0, 2))
        return e

    def campo_texto(pai, conteudo="", altura=6):
        frame = ctk.CTkFrame(pai, fg_color=BRANCO, corner_radius=8,
                              border_width=1, border_color=CINZA_BD)
        frame.pack(fill="x", padx=24, pady=(0, 2))
        txt = ctk.CTkTextbox(
            frame, height=altura * 20,
            font=ctk.CTkFont("Courier New", 11),
            fg_color=BRANCO, text_color=TEXTO,
            corner_radius=8, wrap="none"
        )
        if conteudo:
            txt.insert("1.0", conteudo)
        txt.pack(fill="both", expand=True, padx=2, pady=2)
        return txt

    def btn_arquivo(pai, icone, texto, cmd):
        ctk.CTkButton(
            pai, text=f"  {icone}   {texto}", command=cmd,
            fg_color=CINZA_BD, hover_color="#d0d0d0",
            text_color=TEXTO, font=ctk.CTkFont("Segoe UI", 11, "bold"),
            corner_radius=8, height=38, anchor="w"
        ).pack(fill="x", padx=24, pady=(0, 4))

    # ── Card ─────────────────────────────────────────────
    card = ctk.CTkFrame(scroll, fg_color=CARD_BG, corner_radius=16,
                         border_width=1, border_color=CINZA_BD)
    card.pack(fill="x", padx=16, pady=16)

    secao(card, "NOME  *")
    entrada_nome = campo_entrada(card, musica[1] or "", "Nome da música")

    secao(card, "ARTISTA  *")
    entrada_artista = campo_entrada(card, musica[2] or "", "Nome do artista")

    secao(card, "ÁLBUM")
    entrada_album = campo_entrada(card, musica[3] or "", "Nome do álbum")

    secao(card, "ANO")
    entrada_ano = campo_entrada(card, str(musica[4]) if musica[4] else "", "Ex: 2024")

    ctk.CTkFrame(card, fg_color=CINZA_BD, height=1,
                 corner_radius=0).pack(fill="x", padx=24, pady=(16, 0))

    secao(card, "CIFRA  (acordes)")
    entrada_cifra = campo_texto(card, musica[5] or "", altura=5)

    secao(card, "TABLATURA  (ASCII)")
    entrada_tablatura = campo_texto(card, musica[6] or "", altura=6)

    ctk.CTkFrame(card, fg_color=CINZA_BD, height=1,
                 corner_radius=0).pack(fill="x", padx=24, pady=(16, 0))

    # ── Áudio ─────────────────────────────────────────────
    secao(card, "ÁUDIO")
    label_audio = ctk.CTkLabel(
        card,
        text=f"▶  {os.path.basename(musica[7])}" if musica[7] else "Nenhum arquivo selecionado",
        font=ctk.CTkFont("Segoe UI", 10),
        text_color=TEXTO if musica[7] else SUBTEXTO, anchor="w"
    )
    label_audio.pack(anchor="w", padx=24, pady=(0, 6))

    def selecionar_audio():
        nonlocal novo_audio
        arquivo = filedialog.askopenfilename(
            parent=janela, title="Selecionar Áudio",
            filetypes=[("Audio files", "*.mp3 *.wav"), ("All files", "*.*")]
        )
        if arquivo:
            novo_audio = arquivo
            label_audio.configure(
                text=f"▶  {os.path.basename(arquivo)}",
                text_color=TEXTO
            )
        janela.grab_set()
        janela.focus_force()

    btn_arquivo(card, "▶", "TROCAR ÁUDIO", selecionar_audio)

    # ── Partitura ─────────────────────────────────────────
    secao(card, "PARTITURA  (PDF)")
    label_partitura = ctk.CTkLabel(
        card,
        text=f"◉  {os.path.basename(musica[8])}" if musica[8] else "Nenhum arquivo selecionado",
        font=ctk.CTkFont("Segoe UI", 10),
        text_color=TEXTO if musica[8] else SUBTEXTO, anchor="w"
    )
    label_partitura.pack(anchor="w", padx=24, pady=(0, 6))

    def selecionar_partitura():
        nonlocal nova_partitura
        arquivo = filedialog.askopenfilename(
            parent=janela, title="Selecionar Partitura",
            filetypes=[("PDF files", "*.pdf")]
        )
        if arquivo:
            nova_partitura = arquivo
            label_partitura.configure(
                text=f"◉  {os.path.basename(arquivo)}",
                text_color=TEXTO
            )
        janela.grab_set()
        janela.focus_force()

    btn_arquivo(card, "◉", "TROCAR PARTITURA", selecionar_partitura)

    ctk.CTkFrame(card, fg_color=CINZA_BD, height=1,
                 corner_radius=0).pack(fill="x", padx=24, pady=(12, 0))

    # ── Salvar ────────────────────────────────────────────
    def salvar():
        nome      = entrada_nome.get().strip()
        artista   = entrada_artista.get().strip()
        album     = entrada_album.get().strip()
        ano_str   = entrada_ano.get().strip()
        cifra     = entrada_cifra.get("1.0", "end").strip()
        tablatura = entrada_tablatura.get("1.0", "end").strip()

        if not nome or not artista:
            messagebox.showwarning("Atenção", "Nome e Artista são obrigatórios!")
            return

        ano = None
        if ano_str:
            if not ano_str.isdigit() or len(ano_str) != 4:
                messagebox.showwarning("Atenção", "Ano inválido! Use o formato: 2024")
                return
            ano = int(ano_str)

        editar_musica(id_musica, nome, artista, album, ano, cifra, tablatura,
                      novo_audio, nova_partitura)
        messagebox.showinfo("Sucesso", f'"{nome}" atualizada com sucesso!')
        if ao_salvar:
            ao_salvar()
        janela.destroy()

    ctk.CTkButton(
        card, text="✔   SALVAR ALTERAÇÕES", command=salvar,
        fg_color=AZUL, hover_color=AZUL_HOV,
        text_color=BRANCO, font=ctk.CTkFont("Segoe UI", 12, "bold"),
        corner_radius=10, height=44
    ).pack(fill="x", padx=24, pady=(16, 8))

    # ── Excluir ───────────────────────────────────────────
    def excluir():
        nome = entrada_nome.get().strip() or "esta música"
        if messagebox.askyesno("Confirmar exclusão",
                               f'Tem certeza que deseja excluir "{nome}"?'):
            excluir_musica(id_musica)
            messagebox.showinfo("Excluído", f'"{nome}" foi excluída.')
            if ao_salvar:
                ao_salvar()
            janela.destroy()

    ctk.CTkButton(
        card, text="🗑   EXCLUIR MÚSICA", command=excluir,
        fg_color="#cccccc", hover_color="#bbbbbb",
        text_color=TEXTO, font=ctk.CTkFont("Segoe UI", 12, "bold"),
        corner_radius=10, height=44
    ).pack(fill="x", padx=24, pady=(0, 24))