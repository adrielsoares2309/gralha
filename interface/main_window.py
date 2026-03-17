import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import os
from services.music_service import buscar_musica_completa, excluir_musica
from interface.add_music_window import abrir_janela_adicionar
from interface.edit_music_window import abrir_janela_editar

# ── Tema global ──────────────────────────────────────────
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

VERMELHO   = "#e8514a"
VERM_HOV   = "#c0392b"
BRANCO     = "#ffffff"
FUNDO      = "#f0f0eb"
CARD_BG    = "#ffffff"
SIDEBAR_BG = "#ffffff"
TEXTO      = "#1a1a1a"
SUBTEXTO   = "#666666"
CINZA_BD   = "#e0e0e0"

cifra        = ""
tablatura    = ""
audio        = ""
partitura    = ""
musica_atual = None

# ── Caminho base dos ícones ──────────────────────────────
# Sobe da pasta interface/ até a raiz, depois entra em assets/icons/
ICONS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "..", "assets", "icons")


def carregar_icone(nome_arquivo, tamanho=(20, 20)):
    """
    Carrega um PNG de assets/icons/ e retorna um CTkImage.
    Se o arquivo não existir, retorna None sem quebrar o app.
    """
    caminho = os.path.join(ICONS_DIR, nome_arquivo)
    if not os.path.exists(caminho):
        return None
    try:
        img = Image.open(caminho).convert("RGBA").resize(tamanho, Image.LANCZOS)
        return ctk.CTkImage(light_image=img, dark_image=img, size=tamanho)
    except Exception:
        return None


def iniciar_interface():

    global cifra, tablatura, audio, partitura, musica_atual

    # ════════════════════════════════════════════════════
    # JANELA PRINCIPAL
    # ════════════════════════════════════════════════════
    janela = ctk.CTk()
    janela.title("Guitar Library")
    janela.geometry("680x560")
    janela.configure(fg_color=FUNDO)
    janela.resizable(True, True)

    sidebar_visivel = False

    # ── Pré-carrega todos os ícones ──────────────────────
    # Sidebar
    ic_add     = carregar_icone("add.png",     (18, 18))
    ic_edit    = carregar_icone("edit.png",    (18, 18))
    ic_delete  = carregar_icone("delete.png",  (18, 18))
    # Card de resultado
    ic_cifra      = carregar_icone("cifra.png",      (20, 20))
    ic_tablatura  = carregar_icone("tablatura.png",  (20, 20))
    ic_partitura  = carregar_icone("partitura.png",  (20, 20))
    ic_audio      = carregar_icone("audio.png",      (20, 20))

    # ════════════════════════════════════════════════════
    # SIDEBAR
    # ════════════════════════════════════════════════════
    def criar_sidebar():
        sidebar = ctk.CTkFrame(
            janela, width=170, corner_radius=0,
            fg_color=SIDEBAR_BG,
            border_width=1, border_color=CINZA_BD
        )

        ctk.CTkLabel(
            sidebar, text="MENU",
            font=ctk.CTkFont("Segoe UI", 11, "bold"),
            text_color=SUBTEXTO
        ).pack(pady=(28, 16), padx=20, anchor="w")

        def btn_sidebar(texto, comando, icone_ctk=None):
            # Se o ícone existir usa CTkImage, senão usa só texto
            ctk.CTkButton(
                sidebar,
                text=f"  {texto}",
                image=icone_ctk,
                compound="left",        # ícone à esquerda do texto
                command=comando,
                fg_color=VERMELHO, hover_color=VERM_HOV,
                text_color=BRANCO,
                font=ctk.CTkFont("Segoe UI", 12, "bold"),
                corner_radius=10,
                height=42,
                anchor="w"
            ).pack(fill="x", padx=12, pady=5)

        btn_sidebar("ADICIONAR", lambda: abrir_janela_adicionar(), ic_add)
        btn_sidebar("EDITAR",    lambda: editar(),                  ic_edit)
        btn_sidebar("EXCLUIR",   lambda: excluir(),                 ic_delete)

        return sidebar

    sidebar_frame = criar_sidebar()

    # ════════════════════════════════════════════════════
    # CONTEÚDO PRINCIPAL
    # ════════════════════════════════════════════════════
    frame_conteudo = ctk.CTkFrame(janela, fg_color=FUNDO, corner_radius=0)
    frame_conteudo.pack(side="left", fill="both", expand=True)

    def toggle_sidebar():
        nonlocal sidebar_visivel
        if sidebar_visivel:
            sidebar_frame.pack_forget()
            sidebar_visivel = False
        else:
            sidebar_frame.pack(side="left", fill="y", before=frame_conteudo)
            sidebar_visivel = True

    # ── Topbar ───────────────────────────────────────────
    topbar = ctk.CTkFrame(frame_conteudo, fg_color=FUNDO,
                           corner_radius=0, height=64)
    topbar.pack(fill="x")
    topbar.pack_propagate(False)

    ctk.CTkButton(
        topbar, text="☰",
        command=toggle_sidebar,
        width=44, height=44,
        corner_radius=10,
        fg_color=VERMELHO, hover_color=VERM_HOV,
        text_color=BRANCO,
        font=ctk.CTkFont("Segoe UI", 18, "bold")
    ).pack(side="left", padx=(14, 0), pady=10)

    # ── Barra de busca ───────────────────────────────────
    frame_busca = ctk.CTkFrame(
        topbar, fg_color=BRANCO,
        corner_radius=25,
        border_width=1, border_color=CINZA_BD
    )
    frame_busca.pack(side="left", padx=14, pady=10, fill="x", expand=True)

    entrada = ctk.CTkEntry(
        frame_busca,
        placeholder_text="Buscar música...",
        border_width=0,
        fg_color=BRANCO,
        text_color=TEXTO,
        placeholder_text_color=SUBTEXTO,
        font=ctk.CTkFont("Segoe UI", 12),
        corner_radius=25,
        height=38
    )
    entrada.pack(side="left", fill="x", expand=True, padx=(14, 4), pady=2)
    entrada.bind("<Return>", lambda e: buscar())

    ctk.CTkButton(
        frame_busca, text="🔍",
        command=lambda: buscar(),
        width=42, height=38,
        corner_radius=20,
        fg_color=VERMELHO, hover_color=VERM_HOV,
        text_color=BRANCO,
        font=ctk.CTkFont("Segoe UI", 14)
    ).pack(side="right", padx=4, pady=2)

    # ── Área scrollável ───────────────────────────────────
    scroll_area = ctk.CTkScrollableFrame(
        frame_conteudo, fg_color=FUNDO,
        corner_radius=0,
        scrollbar_button_color=CINZA_BD,
        scrollbar_button_hover_color=SUBTEXTO
    )
    scroll_area.pack(fill="both", expand=True)

    card_ref = {"frame": None}

    # ════════════════════════════════════════════════════
    # AÇÕES
    # ════════════════════════════════════════════════════
    def editar():
        if not musica_atual:
            messagebox.showwarning("Atenção", "Busque uma música primeiro!")
            return
        abrir_janela_editar(musica_atual, ao_salvar=buscar)

    def excluir():
        if not musica_atual:
            messagebox.showwarning("Atenção", "Busque uma música primeiro!")
            return
        nome = musica_atual[1]
        if messagebox.askyesno("Confirmar exclusão",
                               f'Tem certeza que deseja excluir "{nome}"?'):
            excluir_musica(musica_atual[0])
            messagebox.showinfo("Excluído", f'"{nome}" foi excluída.')
            limpar_card()

    def limpar_card():
        global musica_atual, cifra, tablatura, audio, partitura
        musica_atual = None
        cifra = tablatura = audio = partitura = ""
        if card_ref["frame"]:
            card_ref["frame"].destroy()
            card_ref["frame"] = None

    def abrir_viewer(titulo, conteudo):
        jan = ctk.CTkToplevel(janela)
        jan.title(titulo)
        jan.geometry("500x440")
        jan.configure(fg_color=FUNDO)
        jan.grab_set()
        jan.focus_force()

        ctk.CTkLabel(
            jan, text=f"── {titulo.upper()} ──",
            font=ctk.CTkFont("Segoe UI", 14, "bold"),
            text_color=TEXTO
        ).pack(pady=(20, 10))

        frame_txt = ctk.CTkFrame(jan, fg_color=BRANCO, corner_radius=12,
                                  border_width=1, border_color=CINZA_BD)
        frame_txt.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        txt = ctk.CTkTextbox(
            frame_txt,
            font=ctk.CTkFont("Courier New", 12),
            fg_color=BRANCO,
            text_color=TEXTO,
            wrap="none",
            corner_radius=12
        )
        txt.pack(fill="both", expand=True, padx=4, pady=4)
        txt.insert("1.0", conteudo)
        txt.configure(state="disabled")

    def tocar_audio():
        if audio:
            caminho = os.path.join(os.path.dirname(__file__), "..", audio)
            if os.path.exists(caminho):
                os.startfile(caminho)
            else:
                messagebox.showwarning("Aviso", "Arquivo de áudio não encontrado.")

    def visualizar_partitura():
        if partitura:
            caminho = os.path.join(os.path.dirname(__file__), "..", partitura)
            if os.path.exists(caminho):
                os.startfile(caminho)
            else:
                messagebox.showwarning("Aviso", "Arquivo de partitura não encontrado.")

    # ════════════════════════════════════════════════════
    # BUSCA + CARD
    # ════════════════════════════════════════════════════
    def buscar():
        global cifra, tablatura, audio, partitura, musica_atual

        nome = entrada.get().strip()
        if not nome:
            return

        resultado = buscar_musica_completa(nome)

        if card_ref["frame"]:
            card_ref["frame"].destroy()
            card_ref["frame"] = None

        if not resultado:
            musica_atual = None
            cifra = tablatura = audio = partitura = ""
            card_vazio = ctk.CTkFrame(scroll_area, fg_color=CARD_BG,
                                       corner_radius=16,
                                       border_width=1, border_color=CINZA_BD)
            card_vazio.pack(padx=24, pady=20, fill="x")
            card_ref["frame"] = card_vazio
            ctk.CTkLabel(
                card_vazio,
                text="Música não encontrada.",
                font=ctk.CTkFont("Segoe UI", 12),
                text_color=SUBTEXTO
            ).pack(pady=30)
            return

        musica_atual = resultado
        _, nome_r, artista, album, ano, cifra, tablatura, audio, partitura = resultado

        # ── Card ──────────────────────────────────────────
        card = ctk.CTkFrame(scroll_area, fg_color=CARD_BG,
                             corner_radius=16,
                             border_width=1, border_color=CINZA_BD)
        card.pack(padx=24, pady=20, fill="x")
        card_ref["frame"] = card

        # cabeçalho
        cab = ctk.CTkFrame(card, fg_color="transparent")
        cab.pack(fill="x", padx=24, pady=(20, 6))

        ctk.CTkLabel(
            cab, text=nome_r.upper(),
            font=ctk.CTkFont("Segoe UI", 16, "bold"),
            text_color=TEXTO, anchor="w"
        ).pack(anchor="w")

        ctk.CTkLabel(
            cab, text=artista or "—",
            font=ctk.CTkFont("Segoe UI", 11, "bold"),
            text_color=SUBTEXTO, anchor="w"
        ).pack(anchor="w", pady=(2, 0))

        partes = []
        if album: partes.append(album)
        if ano:   partes.append(str(ano))
        if partes:
            ctk.CTkLabel(
                cab, text="  ·  ".join(partes),
                font=ctk.CTkFont("Segoe UI", 10),
                text_color=SUBTEXTO, anchor="w"
            ).pack(anchor="w", pady=(2, 0))

        # separador
        ctk.CTkFrame(card, fg_color=CINZA_BD, height=1,
                     corner_radius=0).pack(fill="x", padx=24, pady=(12, 8))

        # ── Botões de ação com ícones ──────────────────────
        frame_btns = ctk.CTkFrame(card, fg_color="transparent")
        frame_btns.pack(fill="x", padx=24, pady=(0, 20))

        def btn_acao(texto, cmd, icone_ctk=None, ativo=True):
            cor   = VERMELHO if ativo else "#cccccc"
            hover = VERM_HOV if ativo else "#bbbbbb"
            ctk.CTkButton(
                frame_btns,
                text=f"  {texto}",
                image=icone_ctk,
                compound="left",        # ícone à esquerda do texto
                command=cmd if ativo else lambda: None,
                fg_color=cor, hover_color=hover,
                text_color=BRANCO,
                font=ctk.CTkFont("Segoe UI", 11, "bold"),
                corner_radius=10,
                height=42,
                anchor="w"
            ).pack(fill="x", pady=4)

        btn_acao("CIFRA",
                 lambda: abrir_viewer("Cifra", cifra),
                 ic_cifra,
                 ativo=bool(cifra))

        btn_acao("TABLATURA",
                 lambda: abrir_viewer("Tablatura", tablatura),
                 ic_tablatura,
                 ativo=bool(tablatura))

        btn_acao("PARTITURA",
                 visualizar_partitura,
                 ic_partitura,
                 ativo=bool(partitura))

        btn_acao("ÁUDIO",
                 tocar_audio,
                 ic_audio,
                 ativo=bool(audio))

    janela.mainloop()