import os
import webbrowser
import customtkinter as ctk
from tkinter import messagebox

from core.playlist.playlist_search_manager import PlaylistSearchManager
from services.music_service import listar_musicas
from services.playlist_service import (
    add_music_to_playlist,
    delete_playlist,
    get_playlist,
    remove_music_from_playlist,
)


AZUL = "#2B5BA8"
AZUL_HOV = "#1E4280"
BRANCO = "#ffffff"
FUNDO = "#f0f0eb"
CARD_BG = "#ffffff"
TEXTO = "#1a1a1a"
SUBTEXTO = "#666666"
CINZA_BD = "#e0e0e0"
LINHA_ALT = "#fafafa"


class PlaylistWindow(ctk.CTkToplevel):
    def __init__(self, master, playlist_id, on_playlist_updated=None, on_playlist_deleted=None):
        super().__init__(master)
        self.playlist_id = playlist_id
        self.on_playlist_updated = on_playlist_updated
        self.on_playlist_deleted = on_playlist_deleted
        self.playlist = None
        self.musica_atual = None
        self.side_panel_visivel = False
        self.search_manager = PlaylistSearchManager()
        self.search_after_id = None
        self.search_text = ""
        self.music_rows = []
        self.search_entry = None
        self.clear_search_button = None
        self.music_scroll = None
        self.empty_playlist_label = None
        self.no_results_label = None

        self.title("Playlist")
        self.geometry("860x560")
        self.configure(fg_color=FUNDO)
        self.minsize(760, 520)
        self.grab_set()
        self.focus_force()

        header = ctk.CTkFrame(self, fg_color=FUNDO, corner_radius=0, height=72)
        header.pack(fill="x")
        header.pack_propagate(False)

        self.title_label = ctk.CTkLabel(
            header,
            text="PLAYLIST",
            font=ctk.CTkFont("Segoe UI", 18, "bold"),
            text_color=TEXTO,
        )
        self.title_label.pack(side="left", padx=(20, 10), pady=18)

        self.info_label = ctk.CTkLabel(
            header,
            text="",
            font=ctk.CTkFont("Segoe UI", 11),
            text_color=SUBTEXTO,
        )
        self.info_label.pack(side="left", pady=18)

        ctk.CTkButton(
            header,
            text="+",
            command=self.abrir_seletor_musicas,
            width=42,
            height=42,
            corner_radius=21,
            fg_color=AZUL,
            hover_color=AZUL_HOV,
            text_color=BRANCO,
            font=ctk.CTkFont("Segoe UI", 24, "bold"),
        ).pack(side="right", padx=(8, 20), pady=14)

        ctk.CTkButton(
            header,
            text="✏",
            command=self.toggle_side_panel,
            width=42,
            height=42,
            corner_radius=21,
            fg_color=AZUL,
            hover_color=AZUL_HOV,
            text_color=BRANCO,
            font=ctk.CTkFont("Segoe UI", 18, "bold"),
        ).pack(side="right", pady=14)

        self.main_area = ctk.CTkFrame(self, fg_color=FUNDO, corner_radius=0)
        self.main_area.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        self.content_area = ctk.CTkFrame(self.main_area, fg_color=FUNDO, corner_radius=0)
        self.content_area.pack(side="left", fill="both", expand=True)

        self.list_area = ctk.CTkFrame(self.content_area, fg_color=FUNDO, corner_radius=0)
        self.list_area.pack(fill="both", expand=True)

        self.detail_area = ctk.CTkFrame(self.content_area, fg_color=FUNDO, corner_radius=0)
        self.detail_area.pack(fill="x")

        self.side_panel = ctk.CTkFrame(
            self.main_area,
            width=240,
            fg_color=BRANCO,
            corner_radius=16,
            border_width=1,
            border_color=CINZA_BD,
        )

        self.refresh()

    def refresh(self):
        self.playlist = get_playlist(self.playlist_id)
        if not self.playlist:
            messagebox.showwarning("Atencao", "A playlist selecionada nao existe mais.")
            self.destroy()
            return

        self.title_label.configure(text=self.playlist.nome.upper())
        self.info_label.configure(text=f"{len(self.playlist.musicas)} musica(s)")
        self.search_manager.set_musicas(self.playlist.musicas)
        if not self.playlist.musicas:
            self.search_text = ""
        self.render_music_list()
        self.render_side_panel()

        if self.musica_atual:
            musica_id = self.musica_atual.id
            self.musica_atual = next((m for m in self.playlist.musicas if m.id == musica_id), None)

        if self.musica_atual:
            self.render_music_detail()
        else:
            self.clear_detail()

        if self.on_playlist_updated:
            self.on_playlist_updated()

    def render_music_list(self):
        for widget in self.list_area.winfo_children():
            widget.destroy()

        frame_busca = ctk.CTkFrame(
            self.list_area,
            fg_color=BRANCO,
            corner_radius=16,
            border_width=1,
            border_color=CINZA_BD,
        )
        frame_busca.pack(fill="x", padx=8, pady=(0, 8))

        self.search_entry = ctk.CTkEntry(
            frame_busca,
            placeholder_text="Buscar nesta playlist...",
            border_width=0,
            fg_color=BRANCO,
            text_color=TEXTO,
            placeholder_text_color=SUBTEXTO,
            font=ctk.CTkFont("Segoe UI", 12),
            corner_radius=16,
            height=38,
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(14, 4), pady=2)
        self.search_entry.bind("<KeyRelease>", self.schedule_search)
        self.search_entry.bind("<Return>", self.apply_search)

        self.clear_search_button = ctk.CTkButton(
            frame_busca,
            text="X",
            command=self.clear_search,
            width=32,
            height=32,
            corner_radius=10,
            fg_color=FUNDO,
            hover_color=CINZA_BD,
            text_color=SUBTEXTO,
            font=ctk.CTkFont("Segoe UI", 11, "bold"),
        )
        self.clear_search_button.pack(side="right", padx=(4, 8), pady=5)

        if self.search_text:
            self.search_entry.insert(0, self.search_text)

        self.music_scroll = ctk.CTkScrollableFrame(
            self.list_area,
            fg_color=FUNDO,
            corner_radius=0,
            scrollbar_button_color=CINZA_BD,
            scrollbar_button_hover_color=SUBTEXTO,
        )
        self.music_scroll.pack(fill="both", expand=True)

        self.empty_playlist_label = ctk.CTkLabel(
            self.music_scroll,
            text="Nenhuma musica na playlist ainda.\nUse o botao + para adicionar.",
            font=ctk.CTkFont("Segoe UI", 12),
            text_color=SUBTEXTO,
            justify="center",
        )

        self.no_results_label = ctk.CTkLabel(
            self.music_scroll,
            text="No songs found",
            font=ctk.CTkFont("Segoe UI", 12),
            text_color=SUBTEXTO,
            justify="center",
        )

        self.music_rows = []

        if not self.playlist.musicas:
            self.search_entry.configure(state="disabled")
            self.clear_search_button.configure(state="disabled")
            self.empty_playlist_label.pack(pady=40)
            return

        for index, musica in enumerate(self.playlist.musicas):
            cor_linha = CARD_BG if index % 2 == 0 else LINHA_ALT
            selecionada = self.musica_atual and self.musica_atual.id == musica.id
            row_state = {
                "musica": musica,
                "base_color": cor_linha,
                "visible": True,
            }
            linha = ctk.CTkFrame(
                self.music_scroll,
                fg_color=cor_linha,
                corner_radius=10,
                border_width=1 if selecionada else 0,
                border_color=AZUL,
                cursor="hand2",
            )
            linha.pack(fill="x", padx=8, pady=4)

            ctk.CTkLabel(
                linha,
                text=musica.nome,
                font=ctk.CTkFont("Segoe UI", 12, "bold"),
                text_color=TEXTO,
                anchor="w",
            ).pack(fill="x", padx=14, pady=(10, 0))

            subtitulo = musica.artista or "-"
            if musica.album:
                subtitulo = f"{subtitulo}  -  {musica.album}"

            ctk.CTkLabel(
                linha,
                text=subtitulo,
                font=ctk.CTkFont("Segoe UI", 10),
                text_color=SUBTEXTO,
                anchor="w",
            ).pack(fill="x", padx=14, pady=(2, 10))

            def selecionar(event=None, item=musica):
                self.musica_atual = item
                self.update_music_row_styles()
                self.render_music_detail()

            def on_enter(event, frame=linha, item=musica):
                if not self.musica_atual or self.musica_atual.id != item.id:
                    frame.configure(fg_color="#e8eef8")

            def on_leave(event, frame=linha, state=row_state, item=musica):
                frame.configure(
                    fg_color=state["base_color"],
                    border_width=1 if self.musica_atual and self.musica_atual.id == item.id else 0,
                )

            linha.bind("<Button-1>", selecionar)
            linha.bind("<Enter>", on_enter)
            linha.bind("<Leave>", on_leave)
            for child in linha.winfo_children():
                child.bind("<Button-1>", selecionar)
                child.bind("<Enter>", on_enter)
                child.bind("<Leave>", on_leave)

            row_state["frame"] = linha
            self.music_rows.append(row_state)

        self.apply_search()

    def schedule_search(self, event=None):
        if self.search_after_id:
            self.after_cancel(self.search_after_id)
        self.search_after_id = self.after(90, self.apply_search)

    def clear_search(self):
        if not self.search_entry:
            return
        self.search_entry.delete(0, "end")
        self.search_text = ""
        self.apply_search()

    def apply_search(self, event=None):
        if self.search_after_id:
            self.after_cancel(self.search_after_id)
            self.search_after_id = None

        if not self.search_entry:
            return

        self.search_text = self.search_entry.get().strip()
        resultados = self.search_manager.filter(self.search_text)
        ids_visiveis = {musica.id for musica in resultados}
        encontrou_resultados = False
        indice_visivel = 0

        for item in self.music_rows:
            frame = item["frame"]
            visivel = item["musica"].id in ids_visiveis

            if visivel:
                nova_cor = CARD_BG if indice_visivel % 2 == 0 else LINHA_ALT
                item["base_color"] = nova_cor
                frame.configure(fg_color=nova_cor)
                if not item["visible"]:
                    frame.pack(fill="x", padx=8, pady=4)
                item["visible"] = True
                indice_visivel += 1
                encontrou_resultados = True
            else:
                if item["visible"]:
                    frame.pack_forget()
                item["visible"] = False

        self.update_music_row_styles()
        self.update_search_controls()

        if self.empty_playlist_label:
            self.empty_playlist_label.pack_forget()

        if self.no_results_label:
            if self.playlist.musicas and not encontrou_resultados:
                self.no_results_label.pack(pady=40)
            else:
                self.no_results_label.pack_forget()

        musica_visivel = (
            self.musica_atual is not None
            and self.musica_atual.id in ids_visiveis
        )
        if musica_visivel:
            if not self.detail_area.winfo_children():
                self.render_music_detail()
        else:
            self.clear_detail()

    def update_search_controls(self):
        if not self.clear_search_button:
            return

        possui_texto = bool(self.search_text)
        self.clear_search_button.configure(
            state="normal" if possui_texto else "disabled",
            text_color=TEXTO if possui_texto else SUBTEXTO,
        )

    def update_music_row_styles(self):
        for item in self.music_rows:
            if not item["visible"]:
                continue

            musica = item["musica"]
            frame = item["frame"]
            selecionada = self.musica_atual and self.musica_atual.id == musica.id
            frame.configure(
                fg_color=item["base_color"],
                border_width=1 if selecionada else 0,
            )

    def render_music_detail(self):
        self.clear_detail()
        if not self.musica_atual:
            return

        card = ctk.CTkFrame(
            self.detail_area,
            fg_color=CARD_BG,
            corner_radius=16,
            border_width=1,
            border_color=CINZA_BD,
        )
        card.pack(fill="x", padx=8, pady=(8, 0))

        cab = ctk.CTkFrame(card, fg_color="transparent")
        cab.pack(fill="x", padx=20, pady=(18, 8))

        ctk.CTkLabel(
            cab,
            text=(self.musica_atual.nome or "").upper(),
            font=ctk.CTkFont("Segoe UI", 16, "bold"),
            text_color=TEXTO,
            anchor="w",
        ).pack(anchor="w")

        ctk.CTkLabel(
            cab,
            text=self.musica_atual.artista or "-",
            font=ctk.CTkFont("Segoe UI", 11, "bold"),
            text_color=SUBTEXTO,
            anchor="w",
        ).pack(anchor="w", pady=(2, 0))

        partes = []
        if self.musica_atual.album:
            partes.append(self.musica_atual.album)
        if self.musica_atual.ano:
            partes.append(str(self.musica_atual.ano))
        if partes:
            ctk.CTkLabel(
                cab,
                text="  .  ".join(partes),
                font=ctk.CTkFont("Segoe UI", 10),
                text_color=SUBTEXTO,
                anchor="w",
            ).pack(anchor="w", pady=(2, 0))

        ctk.CTkFrame(card, fg_color=CINZA_BD, height=1, corner_radius=0).pack(fill="x", padx=20, pady=(8, 8))

        botoes = ctk.CTkFrame(card, fg_color="transparent")
        botoes.pack(fill="x", padx=20, pady=(0, 18))

        self._create_action_button(
            botoes,
            "CIFRA",
            lambda: self.abrir_viewer("Cifra", self.musica_atual.cifra),
            ativo=bool(self.musica_atual.cifra),
        )
        self._create_action_button(
            botoes,
            "TABLATURA",
            lambda: self.abrir_viewer("Tablatura", self.musica_atual.tablatura),
            ativo=bool(self.musica_atual.tablatura),
        )
        self._create_action_button(
            botoes,
            "PARTITURA",
            self.visualizar_partitura,
            ativo=bool(self.musica_atual.caminho_partitura),
        )
        self._create_action_button(
            botoes,
            "AUDIO",
            self.tocar_audio,
            ativo=bool(self.musica_atual.caminho_audio),
        )
        self._create_action_button(
            botoes,
            "LINK EXTERNO",
            self.abrir_link_externo,
            ativo=bool(self.musica_atual.link_externo),
        )

    def clear_detail(self):
        for widget in self.detail_area.winfo_children():
            widget.destroy()

    def _create_action_button(self, master, texto, command, ativo=True):
        cor = AZUL if ativo else "#cccccc"
        hover = AZUL_HOV if ativo else "#bbbbbb"
        ctk.CTkButton(
            master,
            text=texto,
            command=command if ativo else (lambda: None),
            fg_color=cor,
            hover_color=hover,
            text_color=BRANCO,
            font=ctk.CTkFont("Segoe UI", 11, "bold"),
            corner_radius=10,
            height=40,
        ).pack(fill="x", pady=4)

    def toggle_side_panel(self):
        self.side_panel_visivel = not self.side_panel_visivel
        if self.side_panel_visivel:
            self.side_panel.pack(side="right", fill="y", padx=(12, 0))
        else:
            self.side_panel.pack_forget()

    def render_side_panel(self):
        for widget in self.side_panel.winfo_children():
            widget.destroy()

        ctk.CTkLabel(
            self.side_panel,
            text="EDITAR PLAYLIST",
            font=ctk.CTkFont("Segoe UI", 13, "bold"),
            text_color=TEXTO,
        ).pack(anchor="w", padx=16, pady=(16, 10))

        ctk.CTkLabel(
            self.side_panel,
            text="Remover musicas desta playlist",
            font=ctk.CTkFont("Segoe UI", 10),
            text_color=SUBTEXTO,
        ).pack(anchor="w", padx=16)

        scroll = ctk.CTkScrollableFrame(
            self.side_panel,
            fg_color=BRANCO,
            corner_radius=0,
            scrollbar_button_color=CINZA_BD,
            scrollbar_button_hover_color=SUBTEXTO,
        )
        scroll.pack(fill="both", expand=True, padx=12, pady=(12, 12))

        if not self.playlist.musicas:
            ctk.CTkLabel(
                scroll,
                text="Sem musicas para remover.",
                font=ctk.CTkFont("Segoe UI", 11),
                text_color=SUBTEXTO,
            ).pack(pady=16)
        else:
            for musica in self.playlist.musicas:
                item = ctk.CTkFrame(
                    scroll,
                    fg_color=FUNDO,
                    corner_radius=10,
                    border_width=1,
                    border_color=CINZA_BD,
                )
                item.pack(fill="x", pady=4)

                ctk.CTkLabel(
                    item,
                    text=musica.nome,
                    font=ctk.CTkFont("Segoe UI", 11, "bold"),
                    text_color=TEXTO,
                    anchor="w",
                ).pack(fill="x", padx=10, pady=(8, 0))

                ctk.CTkLabel(
                    item,
                    text=musica.artista or "-",
                    font=ctk.CTkFont("Segoe UI", 10),
                    text_color=SUBTEXTO,
                    anchor="w",
                ).pack(fill="x", padx=10, pady=(2, 8))

                ctk.CTkButton(
                    item,
                    text="X",
                    width=28,
                    height=28,
                    corner_radius=8,
                    fg_color=AZUL,
                    hover_color=AZUL_HOV,
                    command=lambda music_id=musica.id: self.remover_musica(music_id),
                ).place(relx=1.0, x=-10, y=10, anchor="ne")

        ctk.CTkButton(
            self.side_panel,
            text="EXCLUIR PLAYLIST",
            command=self.excluir_playlist,
            fg_color="#cccccc",
            hover_color="#bbbbbb",
            text_color=TEXTO,
            font=ctk.CTkFont("Segoe UI", 12, "bold"),
            corner_radius=10,
            height=42,
        ).pack(fill="x", padx=12, pady=(0, 12))

    def abrir_seletor_musicas(self):
        janela = ctk.CTkToplevel(self)
        janela.title("Adicionar musica")
        janela.geometry("420x480")
        janela.configure(fg_color=FUNDO)
        janela.grab_set()
        janela.focus_force()

        ctk.CTkLabel(
            janela,
            text="Adicionar musica a playlist",
            font=ctk.CTkFont("Segoe UI", 15, "bold"),
            text_color=TEXTO,
        ).pack(anchor="w", padx=18, pady=(18, 8))

        scroll = ctk.CTkScrollableFrame(
            janela,
            fg_color=FUNDO,
            corner_radius=0,
            scrollbar_button_color=CINZA_BD,
            scrollbar_button_hover_color=SUBTEXTO,
        )
        scroll.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        musicas = listar_musicas()
        ids_existentes = {musica.id for musica in self.playlist.musicas}
        musicas_disponiveis = [musica for musica in musicas if musica[0] not in ids_existentes]

        if not musicas_disponiveis:
            ctk.CTkLabel(
                scroll,
                text="Todas as musicas ja estao nesta playlist.",
                font=ctk.CTkFont("Segoe UI", 11),
                text_color=SUBTEXTO,
            ).pack(pady=30)
            return

        for musica in musicas_disponiveis:
            item = ctk.CTkFrame(
                scroll,
                fg_color=BRANCO,
                corner_radius=10,
                border_width=1,
                border_color=CINZA_BD,
            )
            item.pack(fill="x", padx=4, pady=4)

            ctk.CTkLabel(
                item,
                text=musica[1],
                font=ctk.CTkFont("Segoe UI", 11, "bold"),
                text_color=TEXTO,
                anchor="w",
            ).pack(fill="x", padx=12, pady=(10, 0))

            ctk.CTkLabel(
                item,
                text=musica[2] or "-",
                font=ctk.CTkFont("Segoe UI", 10),
                text_color=SUBTEXTO,
                anchor="w",
            ).pack(fill="x", padx=12, pady=(2, 10))

            ctk.CTkButton(
                item,
                text="Adicionar",
                command=lambda music_id=musica[0]: self.adicionar_musica(music_id, janela),
                fg_color=AZUL,
                hover_color=AZUL_HOV,
                text_color=BRANCO,
                corner_radius=8,
                width=84,
                height=30,
            ).place(relx=1.0, x=-12, rely=0.5, anchor="e")

    def adicionar_musica(self, music_id, janela):
        try:
            add_music_to_playlist(self.playlist_id, music_id)
        except ValueError as exc:
            messagebox.showwarning("Atencao", str(exc))
            return

        janela.destroy()
        self.refresh()

    def remover_musica(self, music_id):
        remove_music_from_playlist(self.playlist_id, music_id)
        if self.musica_atual and self.musica_atual.id == music_id:
            self.musica_atual = None
        self.refresh()

    def excluir_playlist(self):
        nome = self.playlist.nome if self.playlist else "esta playlist"
        if not messagebox.askyesno("Confirmar exclusao", f'Tem certeza que deseja excluir "{nome}"?'):
            return

        delete_playlist(self.playlist_id)
        if self.on_playlist_deleted:
            self.on_playlist_deleted()
        self.destroy()

    def abrir_viewer(self, titulo, conteudo):
        viewer = ctk.CTkToplevel(self)
        viewer.title(titulo)
        viewer.geometry("500x440")
        viewer.configure(fg_color=FUNDO)
        viewer.grab_set()
        viewer.focus_force()

        ctk.CTkLabel(
            viewer,
            text=titulo.upper(),
            font=ctk.CTkFont("Segoe UI", 14, "bold"),
            text_color=TEXTO,
        ).pack(pady=(20, 10))

        frame_txt = ctk.CTkFrame(viewer, fg_color=BRANCO, corner_radius=12, border_width=1, border_color=CINZA_BD)
        frame_txt.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        txt = ctk.CTkTextbox(
            frame_txt,
            font=ctk.CTkFont("Courier New", 12),
            fg_color=BRANCO,
            text_color=TEXTO,
            wrap="none",
            corner_radius=12,
        )
        txt.pack(fill="both", expand=True, padx=4, pady=4)
        txt.insert("1.0", conteudo or "")
        txt.configure(state="disabled")

    def tocar_audio(self):
        caminho_audio = self.musica_atual.caminho_audio if self.musica_atual else ""
        if not caminho_audio:
            return
        if os.path.exists(caminho_audio):
            os.startfile(caminho_audio)
        else:
            messagebox.showwarning("Aviso", f"Arquivo de audio nao encontrado:\n{caminho_audio}")

    def abrir_link_externo(self):
        link_externo = self.musica_atual.link_externo if self.musica_atual else ""
        if not link_externo:
            return
        try:
            webbrowser.open(link_externo)
        except Exception:
            messagebox.showwarning("Aviso", f"Nao foi possivel abrir o link:\n{link_externo}")

    def visualizar_partitura(self):
        partitura = self.musica_atual.caminho_partitura if self.musica_atual else ""
        if not partitura:
            return
        if os.path.exists(partitura):
            os.startfile(partitura)
        else:
            messagebox.showwarning("Aviso", f"Arquivo de partitura nao encontrado:\n{partitura}")


def abrir_janela_playlist(master, playlist_id, on_playlist_updated=None, on_playlist_deleted=None):
    return PlaylistWindow(
        master=master,
        playlist_id=playlist_id,
        on_playlist_updated=on_playlist_updated,
        on_playlist_deleted=on_playlist_deleted,
    )
