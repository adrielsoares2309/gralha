import customtkinter as ctk


AZUL = "#2B5BA8"
BRANCO = "#ffffff"
FUNDO = "#f0f0eb"
CARD_BG = "#ffffff"
TEXTO = "#1a1a1a"
SUBTEXTO = "#666666"
CINZA_BD = "#e0e0e0"
LINHA_ALT = "#fafafa"


class SpotifySearchWindow(ctk.CTkToplevel):
    def __init__(self, master, resultados, on_select):
        super().__init__(master)
        self.resultados = resultados or []
        self.on_select = on_select

        self.title("Resultados Spotify")
        self.geometry("560x420")
        self.configure(fg_color=FUNDO)
        self.minsize(480, 360)
        self.grab_set()
        self.focus_force()

        header = ctk.CTkFrame(self, fg_color=FUNDO, corner_radius=0, height=58)
        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkLabel(
            header,
            text="RESULTADOS SPOTIFY",
            font=ctk.CTkFont("Segoe UI", 15, "bold"),
            text_color=TEXTO,
        ).pack(anchor="w", padx=20, pady=(18, 4))

        ctk.CTkLabel(
            header,
            text=f"{len(self.resultados)} resultado(s)",
            font=ctk.CTkFont("Segoe UI", 11),
            text_color=SUBTEXTO,
        ).pack(anchor="w", padx=20)

        scroll = ctk.CTkScrollableFrame(
            self,
            fg_color=FUNDO,
            corner_radius=0,
            scrollbar_button_color=CINZA_BD,
            scrollbar_button_hover_color=SUBTEXTO,
        )
        scroll.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        if not self.resultados:
            ctk.CTkLabel(
                scroll,
                text="Nenhuma musica encontrada.",
                font=ctk.CTkFont("Segoe UI", 12),
                text_color=SUBTEXTO,
            ).pack(pady=40)
            return

        for indice, item in enumerate(self.resultados):
            cor_linha = CARD_BG if indice % 2 == 0 else LINHA_ALT
            card = ctk.CTkFrame(
                scroll,
                fg_color=cor_linha,
                corner_radius=12,
                border_width=1,
                border_color=CINZA_BD,
                cursor="hand2",
            )
            card.pack(fill="x", padx=4, pady=4)

            ctk.CTkLabel(
                card,
                text=item.get("nome", "") or "-",
                font=ctk.CTkFont("Segoe UI", 12, "bold"),
                text_color=TEXTO,
                anchor="w",
            ).pack(fill="x", padx=14, pady=(10, 0))

            detalhes = [
                item.get("artista", "") or "-",
                item.get("album", "") or "-",
                item.get("ano", "") or "-",
            ]
            ctk.CTkLabel(
                card,
                text="  -  ".join(detalhes),
                font=ctk.CTkFont("Segoe UI", 10),
                text_color=SUBTEXTO,
                anchor="w",
            ).pack(fill="x", padx=14, pady=(4, 10))

            def selecionar(event=None, resultado=item):
                if self.on_select:
                    self.on_select(resultado)
                self.destroy()

            def on_enter(event, frame=card):
                frame.configure(border_color=AZUL)

            def on_leave(event, frame=card):
                frame.configure(border_color=CINZA_BD)

            card.bind("<Button-1>", selecionar)
            card.bind("<Enter>", on_enter)
            card.bind("<Leave>", on_leave)
            for child in card.winfo_children():
                child.bind("<Button-1>", selecionar)
                child.bind("<Enter>", on_enter)
                child.bind("<Leave>", on_leave)
