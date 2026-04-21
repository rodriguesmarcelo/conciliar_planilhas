# -*- coding: utf-8 -*-
import tkinter as tk
import customtkinter as ctk
from core.profile_manager import load_all_profiles, duplicate_profile, delete_profile

# ── Paleta de cores ──────────────────────────────────────────────────────────
_ACCENT       = "#1F6FEB"   # azul GitHub-style
_ACCENT_HOVER = "#1558C0"
_CARD_DARK    = "#1E2128"
_CARD_HOVER   = "#252B35"
_CARD_BORDER  = "#30363D"
_TAG_DUAL_BG  = "#0D2340"
_TAG_DUAL_FG  = "#58A6FF"
_TAG_SING_BG  = "#0D2D1F"
_TAG_SING_FG  = "#3FB950"
_TEXT_MUTED   = "#848D97"
_HEADER_BG    = "#161B22"
_PAGE_BG      = "#0D1117"


# ── Card de perfil ───────────────────────────────────────────────────────────
class ProfileCard(ctk.CTkFrame):
    """Card clicável que representa um perfil."""

    def __init__(self, master, profile: dict, on_select, on_edit, on_duplicate, on_delete, **kwargs):
        super().__init__(
            master,
            fg_color=_CARD_DARK,
            border_color=_CARD_BORDER,
            border_width=1,
            corner_radius=10,
            **kwargs,
        )
        self.profile = profile
        self.on_select    = on_select
        self.on_edit      = on_edit
        self.on_duplicate = on_duplicate
        self.on_delete    = on_delete

        self._build()
        self._bind_hover(self)

    def _build(self):
        mode = self.profile.get("mode", "dual")
        name = self.profile.get("name", "—")

        # ── Linha superior: ícone + nome + tag ──
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=14, pady=(14, 4))

        # Ícone de arquivo (emoji simples como substituto)
        icon_lbl = ctk.CTkLabel(top, text="📊", font=ctk.CTkFont(size=20))
        icon_lbl.pack(side="left", padx=(0, 8))

        name_lbl = ctk.CTkLabel(
            top, text=name,
            font=ctk.CTkFont(size=15, weight="bold"),
            anchor="w",
        )
        name_lbl.pack(side="left", fill="x", expand=True)

        # Tag modo
        if mode == "dual":
            tag_bg, tag_fg, tag_txt = _TAG_DUAL_BG, _TAG_DUAL_FG, "Dual"
        else:
            tag_bg, tag_fg, tag_txt = _TAG_SING_BG, _TAG_SING_FG, "Single"

        tag = ctk.CTkLabel(
            top, text=tag_txt,
            font=ctk.CTkFont(size=10, weight="bold"),
            fg_color=tag_bg, text_color=tag_fg,
            corner_radius=4, padx=6, pady=2,
        )
        tag.pack(side="right")

        # ── Subtítulo: número de planilhas ──
        n_sheets = len(self.profile.get("sheets", []))
        sub_txt = f"{n_sheets} planilha{'s' if n_sheets != 1 else ''}"
        sub = ctk.CTkLabel(
            self, text=sub_txt,
            font=ctk.CTkFont(size=11),
            text_color=_TEXT_MUTED, anchor="w",
        )
        sub.pack(fill="x", padx=52, pady=(0, 10))

        # ── Separador ──
        sep = ctk.CTkFrame(self, height=1, fg_color=_CARD_BORDER)
        sep.pack(fill="x", padx=14)

        # ── Botões de ação ──
        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.pack(fill="x", padx=10, pady=6)

        btn_cfg = dict(
            height=26, corner_radius=6,
            font=ctk.CTkFont(size=11),
            fg_color="transparent",
            hover_color=_CARD_HOVER,
            border_width=0,
        )
        edit_btn = ctk.CTkButton(
            actions, text="✏ Editar", width=70, **btn_cfg,
            command=lambda: self.on_edit(self.profile["id"]),
        )
        edit_btn.pack(side="left", padx=(0, 4))

        dup_btn = ctk.CTkButton(
            actions, text="⧉ Duplicar", width=80, **btn_cfg,
            command=lambda: self.on_duplicate(self.profile["id"]),
        )
        dup_btn.pack(side="left")

        del_btn = ctk.CTkButton(
            actions, text="🗑", width=36,
            **{**btn_cfg, "hover_color": "#2D1A1A"},
            text_color="#F85149",            
            command=lambda: self.on_delete(self.profile["id"]),
        )
        del_btn.pack(side="right")

        # Bind clique no card inteiro → selecionar perfil
        self.bind("<Button-1>", lambda e: self.on_select(self.profile))
        for w in (top, name_lbl, icon_lbl, sub):
            w.bind("<Button-1>", lambda e: self.on_select(self.profile))

    def _bind_hover(self, widget):
        widget.bind("<Enter>", self._on_enter)
        widget.bind("<Leave>", self._on_leave)
        for child in widget.winfo_children():
            self._bind_hover(child)

    def _on_enter(self, _=None):
        self.configure(fg_color=_CARD_HOVER)

    def _on_leave(self, _=None):
        self.configure(fg_color=_CARD_DARK)


# ── Tela Home ────────────────────────────────────────────────────────────────
class HomeScreen(ctk.CTkFrame):
    """Tela principal de seleção de perfil."""

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=_PAGE_BG, **kwargs)
        self.master = master
        self._build()
        self.refresh_profiles()

    def _build(self):
        # ── Header ──
        header = ctk.CTkFrame(self, fg_color=_HEADER_BG, height=60, corner_radius=0)
        header.pack(fill="x")
        header.pack_propagate(False)

        title_lbl = ctk.CTkLabel(
            header,
            text="  📋  Conciliador de Planilhas",
            font=ctk.CTkFont(size=18, weight="bold"),
            anchor="w",
        )
        title_lbl.pack(side="left", padx=20)

        # ── Corpo ──
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=32, pady=24)

        # Linha: título da seção + botões
        toolbar = ctk.CTkFrame(body, fg_color="transparent")
        toolbar.pack(fill="x", pady=(0, 16))

        section_lbl = ctk.CTkLabel(
            toolbar,
            text="Selecione um Perfil",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=_TEXT_MUTED,
            anchor="w",
        )
        section_lbl.pack(side="left")

        # Botões de ação globais
        btn_style = dict(
            height=34, corner_radius=7,
            font=ctk.CTkFont(size=12, weight="bold"),
        )
        new_btn = ctk.CTkButton(
            toolbar, text="＋  Novo Perfil",
            fg_color=_ACCENT, hover_color=_ACCENT_HOVER,
            command=self._novo_perfil, **btn_style,
        )
        new_btn.pack(side="right", padx=(8, 0))

        # ── Grid de cards (scrollável) ──
        scroll = ctk.CTkScrollableFrame(body, fg_color="transparent")
        scroll.pack(fill="both", expand=True)
        scroll.grid_columnconfigure(0, weight=1)
        scroll.grid_columnconfigure(1, weight=1)
        self._cards_frame = scroll

    # ── Carregamento de perfis ───────────────────────────────────────────────
    def refresh_profiles(self):
        # Limpar cards existentes
        for w in self._cards_frame.winfo_children():
            w.destroy()

        profiles = load_all_profiles()

        if not profiles:
            empty = ctk.CTkLabel(
                self._cards_frame,
                text="Nenhum perfil encontrado.\nClique em '＋ Novo Perfil' para criar um.",
                font=ctk.CTkFont(size=13),
                text_color=_TEXT_MUTED,
            )
            empty.grid(row=0, column=0, columnspan=2, pady=60)
            return

        for i, (pid, profile) in enumerate(profiles.items()):
            row, col = divmod(i, 2)
            card = ProfileCard(
                self._cards_frame,
                profile=profile,
                on_select=self._selecionar_perfil,
                on_edit=self._editar_perfil,
                on_duplicate=self._duplicar_perfil,
                on_delete=self._deletar_perfil,
            )
            card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")

    # ── Ações ────────────────────────────────────────────────────────────────
    def _selecionar_perfil(self, profile: dict):
        self.master.show_screen("run", profile=profile)

    def _novo_perfil(self):
        self.master.show_screen("profile_edit", mode="new")

    def _editar_perfil(self, profile_id: str):
        self.master.show_screen("profile_edit", mode="edit", profile_id=profile_id)

    def _duplicar_perfil(self, profile_id: str):
        novo = duplicate_profile(profile_id)
        if novo:
            self.refresh_profiles()

    def _deletar_perfil(self, profile_id: str):
        from tkinter import messagebox
        profiles = load_all_profiles()
        nome = profiles.get(profile_id, {}).get("name", profile_id)
        confirmar = messagebox.askyesno(
            "Confirmar exclusão",
            f"Deseja realmente excluir o perfil '{nome}'?\nEsta ação não pode ser desfeita.",
            icon="warning",
        )
        if confirmar:
            delete_profile(profile_id)
            self.refresh_profiles()
