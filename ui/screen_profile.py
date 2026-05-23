# -*- coding: utf-8 -*-
"""
Task 07 — Tela de Criação e Edição de Perfis
"""
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import customtkinter as ctk

from core.profile_manager import load_profile, save_profile
from core.reader import preview_sheet, InvalidFileError

# ── Paleta ───────────────────────────────────────────────────────────────────
_ACCENT        = "#1F6FEB"
_ACCENT_HOVER  = "#1558C0"
_DANGER        = "#F85149"
_PAGE_BG       = "#0D1117"
_HEADER_BG     = "#161B22"
_CARD_BG       = "#1E2128"
_CARD_BORDER   = "#30363D"
_INPUT_BG      = "#161B22"
_TEXT_MUTED    = "#848D97"
_TEXT_NORMAL   = "#C9D1D9"
_ROW_ODD       = "#1A1F27"
_ROW_EVEN      = "#1E2128"

FIELD_OPTIONS = [
    "data", "valor", "valor_debito", "valor_credito",
    "historico", "numero_cheque", "numero_nota",
    "cnpj", "fornecedor", "cpf_cnpj",
    "valor_parcela", "valor_juros", "valor_desconto",
    "documento", "(personalizado...)",
]

ALL_TRANSFORMS = [
    ("remove_newlines",      "Remover quebras de linha"),
    ("remove_semicolons",    "Remover ponto-e-vírgula (;)"),
    ("remove_dots",          "Remover pontos (.)"),
    ("remove_commas",        "Converter vírgula em ponto"),
    ("remove_special_chars", "Manter apenas dígitos"),
    ("to_int",               "Converter para inteiro"),
    ("remove_cd_suffix",     "Remover sufixo C/D (extrato)"),
    ("absolute_value",       "Valor absoluto"),
    ("strip_after_dash",     "Cortar após hífen (-)"),
    ("strip_after_slash",    "Cortar após barra (/)"),
    ("lstrip_zeros",         "Remover zeros à esquerda"),
    ("apply_cnpj_mask",      "Aplicar máscara CNPJ"),
]

DATE_FORMATS = ["dd/mm/yyyy", "mm/dd/yyyy", "yyyy-mm-dd"]


# ─────────────────────────────────────────────────────────────────────────────
class TransformPopup(ctk.CTkToplevel):
    def __init__(self, master, current: list, callback):
        super().__init__(master)
        self.title("Transformações")
        self.geometry("400x460")
        self.resizable(False, False)
        self.grab_set()
        self.configure(fg_color=_CARD_BG)
        self.callback = callback
        self.vars = {}

        ctk.CTkLabel(self, text="Selecione as transformações:",
                     font=ctk.CTkFont(size=13, weight="bold")).pack(
            pady=(16, 8), padx=20, anchor="w")

        scroll = ctk.CTkScrollableFrame(self, fg_color=_INPUT_BG, corner_radius=8)
        scroll.pack(fill="both", expand=True, padx=16, pady=(0, 12))

        for key, label in ALL_TRANSFORMS:
            var = tk.BooleanVar(value=(key in current))
            self.vars[key] = var
            row = ctk.CTkFrame(scroll, fg_color="transparent")
            row.pack(fill="x", pady=2)
            ctk.CTkCheckBox(row, text=label, variable=var,
                            font=ctk.CTkFont(size=12),
                            fg_color=_ACCENT, hover_color=_ACCENT_HOVER).pack(
                anchor="w", padx=8)

        btns = ctk.CTkFrame(self, fg_color="transparent")
        btns.pack(fill="x", padx=16, pady=(0, 16))
        ctk.CTkButton(btns, text="Cancelar", width=100,
                      fg_color="transparent", border_width=1, border_color=_CARD_BORDER,
                      command=self.destroy).pack(side="right", padx=(8, 0))
        ctk.CTkButton(btns, text="Confirmar", width=100,
                      fg_color=_ACCENT, hover_color=_ACCENT_HOVER,
                      command=self._confirm).pack(side="right")

    def _confirm(self):
        selected = [k for k, v in self.vars.items() if v.get()]
        self.callback(selected)
        self.destroy()


# ─────────────────────────────────────────────────────────────────────────────
class ColumnRow(ctk.CTkFrame):
    def __init__(self, master, col_cfg: dict, on_remove, row_index: int, **kwargs):
        bg = _ROW_ODD if row_index % 2 == 0 else _ROW_EVEN
        super().__init__(master, fg_color=bg, corner_radius=0, **kwargs)
        self.col_cfg   = col_cfg.copy()
        self.on_remove = on_remove
        self._transforms = list(col_cfg.get("transformations", []))
        self._build()

    def _build(self):
        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=3)
        self.columnconfigure(3, weight=1)
        self.columnconfigure(4, weight=1)
        self.columnconfigure(5, weight=1)
        self.columnconfigure(6, weight=0)

        field_val = self.col_cfg.get("field", "data")
        if field_val not in FIELD_OPTIONS:
            FIELD_OPTIONS.append(field_val)

        self._field_var = tk.StringVar(value=field_val)
        ctk.CTkOptionMenu(self, variable=self._field_var, values=FIELD_OPTIONS,
                          width=140, height=28, font=ctk.CTkFont(size=11),
                          fg_color=_INPUT_BG,
                          command=self._on_field_change).grid(
            row=0, column=0, padx=(4, 2), pady=4, sticky="ew")

        self._col_var = tk.StringVar(value=str(self.col_cfg.get("col_index", 1)))
        ctk.CTkEntry(self, textvariable=self._col_var, width=52, height=28,
                     font=ctk.CTkFont(size=11), fg_color=_INPUT_BG).grid(
            row=0, column=1, padx=2, pady=4)

        self._trans_btn = ctk.CTkButton(self, text=self._trans_label(),
                                         width=130, height=28,
                                         font=ctk.CTkFont(size=11),
                                         fg_color=_INPUT_BG, hover_color=_HEADER_BG,
                                         border_width=1, border_color=_CARD_BORDER,
                                         command=self._open_transforms)
        self._trans_btn.grid(row=0, column=2, padx=2, pady=4, sticky="ew")

        self._mult_var = tk.BooleanVar(value=self.col_cfg.get("multiply_minus_one", False))
        ctk.CTkCheckBox(self, text="", variable=self._mult_var, width=28, height=28,
                        fg_color=_ACCENT, hover_color=_ACCENT_HOVER,
                        checkbox_width=18, checkbox_height=18).grid(
            row=0, column=3, padx=2)

        self._skip_empty_var = tk.BooleanVar(value=self.col_cfg.get("skip_if_empty", False))
        ctk.CTkCheckBox(self, text="", variable=self._skip_empty_var, width=28, height=28,
                        fg_color=_ACCENT, hover_color=_ACCENT_HOVER,
                        checkbox_width=18, checkbox_height=18).grid(
            row=0, column=4, padx=2)

        self._skip_date_var = tk.BooleanVar(value=self.col_cfg.get("skip_if_invalid_date", False))
        self._skip_date_cb = ctk.CTkCheckBox(self, text="", variable=self._skip_date_var,
                                              width=28, height=28,
                                              fg_color=_ACCENT, hover_color=_ACCENT_HOVER,
                                              checkbox_width=18, checkbox_height=18)
        self._skip_date_cb.grid(row=0, column=5, padx=2)
        self._update_date_visibility()

        ctk.CTkButton(self, text="✕", width=28, height=28,
                      font=ctk.CTkFont(size=12),
                      fg_color="transparent", text_color=_DANGER,
                      hover_color="#2D1A1A",
                      command=self.on_remove).grid(row=0, column=6, padx=(2, 4))

    def _trans_label(self):
        n = len(self._transforms)
        if n == 0: return "Nenhuma"
        if n == 1: return self._transforms[0]
        return f"{n} selecionadas"

    def _open_transforms(self):
        TransformPopup(self, self._transforms, self._set_transforms)

    def _set_transforms(self, selected):
        self._transforms = selected
        self._trans_btn.configure(text=self._trans_label())

    def _on_field_change(self, _=None):
        self._update_date_visibility()

    def _update_date_visibility(self):
        if self._field_var.get() == "data":
            self._skip_date_cb.configure(state="normal")
        else:
            self._skip_date_var.set(False)
            self._skip_date_cb.configure(state="disabled")

    def get_config(self):
        try:
            col_idx = int(self._col_var.get())
        except ValueError:
            col_idx = 1
        return {
            "field": self._field_var.get(),
            "col_index": col_idx,
            "transformations": list(self._transforms),
            "multiply_minus_one": bool(self._mult_var.get()),
            "is_fallback_of": self.col_cfg.get("is_fallback_of"),
            "skip_if_empty": bool(self._skip_empty_var.get()),
            "skip_if_invalid_date": bool(self._skip_date_var.get()),
        }


# ─────────────────────────────────────────────────────────────────────────────
class SheetPanel(ctk.CTkFrame):
    def __init__(self, master, sheet_cfg: dict, **kwargs):
        super().__init__(master, fg_color=_PAGE_BG, **kwargs)
        self._sheet_cfg = sheet_cfg
        self._col_rows = []
        self._build()
        self._load_columns()

    def _build(self):
        scroll = ctk.CTkScrollableFrame(self, fg_color=_PAGE_BG)
        scroll.pack(fill="both", expand=True)
        self._scroll = scroll

        # Metadados
        meta = ctk.CTkFrame(scroll, fg_color=_CARD_BG, corner_radius=10)
        meta.pack(fill="x", padx=2, pady=(8, 6))
        meta.columnconfigure(1, weight=1)
        meta.columnconfigure(3, weight=1)

        ctk.CTkLabel(meta, text="Nome da planilha:", font=ctk.CTkFont(size=12)).grid(
            row=0, column=0, padx=(14, 6), pady=10, sticky="w")
        self._label_var = tk.StringVar(value=self._sheet_cfg.get("label", ""))
        ctk.CTkEntry(meta, textvariable=self._label_var, height=30,
                     fg_color=_INPUT_BG).grid(
            row=0, column=1, padx=(0, 20), pady=10, sticky="ew")

        ctk.CTkLabel(meta, text="Iniciar na linha:", font=ctk.CTkFont(size=12)).grid(
            row=0, column=2, padx=(0, 6), pady=10, sticky="w")
        self._start_var = tk.StringVar(value=str(self._sheet_cfg.get("start_row", 1)))
        ctk.CTkEntry(meta, textvariable=self._start_var, width=60, height=30,
                     fg_color=_INPUT_BG).grid(
            row=0, column=3, padx=(0, 14), pady=10, sticky="w")

        # Pré-visualização
        prev_frame = ctk.CTkFrame(scroll, fg_color=_CARD_BG, corner_radius=10)
        prev_frame.pack(fill="x", padx=2, pady=(0, 6))

        prev_top = ctk.CTkFrame(prev_frame, fg_color="transparent")
        prev_top.pack(fill="x", padx=14, pady=8)
        ctk.CTkButton(prev_top, text="📂  Selecionar arquivo para pré-visualização",
                      height=32, font=ctk.CTkFont(size=12),
                      fg_color=_INPUT_BG, hover_color=_HEADER_BG,
                      border_width=1, border_color=_CARD_BORDER,
                      command=self._pick_preview).pack(side="left")
        self._preview_lbl = ctk.CTkLabel(prev_top, text="Nenhum arquivo selecionado",
                                          font=ctk.CTkFont(size=11), text_color=_TEXT_MUTED)
        self._preview_lbl.pack(side="left", padx=12)

        tree_frame = ctk.CTkFrame(prev_frame, fg_color=_INPUT_BG, corner_radius=6)
        tree_frame.pack(fill="x", padx=14, pady=(0, 12))

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Preview.Treeview",
                        background=_INPUT_BG, foreground=_TEXT_NORMAL,
                        fieldbackground=_INPUT_BG, rowheight=22,
                        font=("Consolas", 10))
        style.configure("Preview.Treeview.Heading",
                        background=_HEADER_BG, foreground=_TEXT_MUTED,
                        font=("Consolas", 10, "bold"))
        style.map("Preview.Treeview", background=[("selected", "#264F78")])

        self._tree = ttk.Treeview(tree_frame, style="Preview.Treeview",
                                   height=8, show="headings")
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self._tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self._tree.xview)
        self._tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self._tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        # Tabela de colunas
        cols_frame = ctk.CTkFrame(scroll, fg_color=_CARD_BG, corner_radius=10)
        cols_frame.pack(fill="x", padx=2, pady=(0, 6))
        self._cols_container = cols_frame

        hdr = ctk.CTkFrame(cols_frame, fg_color=_HEADER_BG, corner_radius=0)
        hdr.pack(fill="x")
        hdr.columnconfigure(0, weight=3); hdr.columnconfigure(1, weight=1)
        hdr.columnconfigure(2, weight=3); hdr.columnconfigure(3, weight=1)
        hdr.columnconfigure(4, weight=1); hdr.columnconfigure(5, weight=1)
        hdr.columnconfigure(6, weight=0)

        hs = dict(font=ctk.CTkFont(size=10, weight="bold"),
                  text_color=_TEXT_MUTED, fg_color="transparent")
        ctk.CTkLabel(hdr, text="Campo", **hs).grid(row=0, column=0, padx=(8,2), pady=6, sticky="w")
        ctk.CTkLabel(hdr, text="Col.",  **hs).grid(row=0, column=1, padx=2, pady=6)
        ctk.CTkLabel(hdr, text="Transformações", **hs).grid(row=0, column=2, padx=2, pady=6, sticky="w")
        ctk.CTkLabel(hdr, text="×(-1)",**hs).grid(row=0, column=3, padx=2, pady=6)
        ctk.CTkLabel(hdr, text="Vazio?",**hs).grid(row=0, column=4, padx=2, pady=6)
        ctk.CTkLabel(hdr, text="Data?", **hs).grid(row=0, column=5, padx=2, pady=6)
        ctk.CTkLabel(hdr, text="", width=36, **hs).grid(row=0, column=6)

        self._rows_frame = ctk.CTkFrame(cols_frame, fg_color="transparent")
        self._rows_frame.pack(fill="x")

        ctk.CTkButton(cols_frame, text="＋  Adicionar Campo",
                      height=30, font=ctk.CTkFont(size=12),
                      fg_color="transparent", border_width=1, border_color=_ACCENT,
                      text_color=_ACCENT, hover_color="#0D2040",
                      command=self._add_column_row).pack(anchor="w", padx=14, pady=10)

    def _load_columns(self):
        for col_cfg in self._sheet_cfg.get("columns", []):
            self._add_column_row(col_cfg)

    def _add_column_row(self, col_cfg=None):
        if col_cfg is None:
            col_cfg = {"field": "data", "col_index": 1, "transformations": [],
                       "multiply_minus_one": False, "is_fallback_of": None,
                       "skip_if_empty": False, "skip_if_invalid_date": False}
        idx = len(self._col_rows)
        row_widget = ColumnRow(self._rows_frame, col_cfg,
                               on_remove=lambda rw=None: self._remove_row(row_widget),
                               row_index=idx)
        row_widget.pack(fill="x")
        self._col_rows.append(row_widget)

    def _remove_row(self, row_widget):
        row_widget.destroy()
        if row_widget in self._col_rows:
            self._col_rows.remove(row_widget)
        for i, r in enumerate(self._col_rows):
            r.configure(fg_color=_ROW_ODD if i % 2 == 0 else _ROW_EVEN)

    def _pick_preview(self):
        path = filedialog.askopenfilename(
            title="Selecionar planilha para pré-visualização",
            filetypes=[("Excel / CSV", "*.xlsx *.xls *.csv"), ("Todos", "*.*")])
        if not path:
            return
        # Detectar .xls e solicitar conversão
        if path.lower().endswith(".xls"):
            messagebox.showwarning(
                "Formato não suportado — .xls",
                "O arquivo selecionado está no formato antigo '.xls'.\n\n"
                "Por favor:\n"
                "  1. Abra o arquivo no Excel\n"
                "  2. Clique em Arquivo → Salvar Como\n"
                "  3. Escolha o formato 'Pasta de Trabalho do Excel (*.xlsx)'\n"
                "  4. Salve e selecione o novo arquivo aqui.\n\n"
                "O sistema aceita apenas arquivos .xlsx ou .csv."
            )
            return
        import os
        self._preview_lbl.configure(text=os.path.basename(path), text_color=_TEXT_NORMAL)
        try:
            rows = preview_sheet(path, max_rows=20)
        except Exception as e:
            messagebox.showerror("Erro na pré-visualização", str(e))
            return
        if not rows or len(rows) < 2:
            return
        self._tree.delete(*self._tree.get_children())
        headers = [str(h) for h in rows[0]]
        self._tree["columns"] = headers
        for h in headers:
            w = 70 if h == "Col" else 100
            self._tree.heading(h, text=h)
            self._tree.column(h, width=w, minwidth=50, anchor="center")
        for data_row in rows[1:]:
            self._tree.insert("", "end", values=[str(v) if v is not None else "" for v in data_row])

    def get_config(self):
        try:
            start = int(self._start_var.get())
        except ValueError:
            start = 1
        return {
            "label": self._label_var.get().strip(),
            "start_row": start,
            "columns": [r.get_config() for r in self._col_rows],
        }


# ─────────────────────────────────────────────────────────────────────────────
class ProfileScreen(ctk.CTkFrame):
    def __init__(self, master, mode="new", profile_id=None, **kwargs):
        super().__init__(master, fg_color=_PAGE_BG, **kwargs)
        self.master     = master
        self.mode       = mode
        self.profile_id = profile_id
        self._profile   = {}
        self._panels    = []
        self._tab_btns  = []
        self._active_tab = 0

        if mode in ("edit", "duplicate") and profile_id:
            self._profile = load_profile(profile_id) or {}

        self._build()
        self._prefill()

    def _build(self):
        titulos = {"new": "Novo Perfil", "edit": "Editar Perfil", "duplicate": "Duplicar Perfil"}

        # Header
        header = ctk.CTkFrame(self, fg_color=_HEADER_BG, height=60, corner_radius=0)
        header.pack(fill="x")
        header.pack_propagate(False)
        ctk.CTkButton(header, text="← Voltar", width=90, height=32,
                      fg_color="transparent", hover_color=_CARD_BG,
                      font=ctk.CTkFont(size=12),
                      border_width=1, border_color=_CARD_BORDER,
                      command=lambda: self.master.show_screen("home")).pack(
            side="left", padx=16, pady=14)
        ctk.CTkLabel(header, text=f"📝  {titulos.get(self.mode,'Perfil')}",
                     font=ctk.CTkFont(size=16, weight="bold")).pack(side="left", padx=8)

        # Corpo scrollável
        body = ctk.CTkScrollableFrame(self, fg_color=_PAGE_BG)
        body.pack(fill="both", expand=True)
        self._body = body

        # Seção geral
        gen = ctk.CTkFrame(body, fg_color=_CARD_BG, corner_radius=10)
        gen.pack(fill="x", padx=24, pady=(16, 8))
        gen.columnconfigure(1, weight=1)

        ctk.CTkLabel(gen, text="Nome do Perfil:", font=ctk.CTkFont(size=12, weight="bold")).grid(
            row=0, column=0, padx=(16, 8), pady=(14, 8), sticky="w")
        self._name_var = tk.StringVar()
        ctk.CTkEntry(gen, textvariable=self._name_var, height=32,
                     placeholder_text="Ex: Meu Perfil",
                     fg_color=_INPUT_BG).grid(row=0, column=1, padx=(0, 16), pady=(14, 8), sticky="ew")

        ctk.CTkLabel(gen, text="Modo:", font=ctk.CTkFont(size=12, weight="bold")).grid(
            row=1, column=0, padx=(16, 8), pady=8, sticky="w")
        mf = ctk.CTkFrame(gen, fg_color="transparent")
        mf.grid(row=1, column=1, padx=(0, 16), pady=8, sticky="w")
        self._mode_var = tk.StringVar(value="dual")
        ctk.CTkRadioButton(mf, text="Duas planilhas", variable=self._mode_var, value="dual",
                           font=ctk.CTkFont(size=12), fg_color=_ACCENT, hover_color=_ACCENT_HOVER,
                           command=self._on_mode_change).pack(side="left", padx=(0, 20))
        ctk.CTkRadioButton(mf, text="Uma planilha", variable=self._mode_var, value="single",
                           font=ctk.CTkFont(size=12), fg_color=_ACCENT, hover_color=_ACCENT_HOVER,
                           command=self._on_mode_change).pack(side="left")

        ctk.CTkLabel(gen, text="Formato de Data:", font=ctk.CTkFont(size=12, weight="bold")).grid(
            row=2, column=0, padx=(16, 8), pady=(8, 14), sticky="w")
        self._date_fmt_var = tk.StringVar(value="dd/mm/yyyy")
        ctk.CTkOptionMenu(gen, variable=self._date_fmt_var, values=DATE_FORMATS,
                          width=160, height=30, fg_color=_INPUT_BG,
                          font=ctk.CTkFont(size=12)).grid(
            row=2, column=1, padx=(0, 16), pady=(8, 14), sticky="w")

        # Seção de Comparação
        comp = ctk.CTkFrame(body, fg_color=_CARD_BG, corner_radius=10)
        comp.pack(fill="x", padx=24, pady=(0, 8))
        self._comp_section = comp
        
        ctk.CTkLabel(comp, text="Critérios de Comparação:", font=ctk.CTkFont(size=12, weight="bold")).grid(
            row=0, column=0, padx=(16, 8), pady=(14, 4), sticky="w")
        
        self._match_vars = {}
        fields_to_match = ["data", "valor", "numero_cheque", "numero_nota", "documento"]
        
        mf_frame = ctk.CTkFrame(comp, fg_color="transparent")
        mf_frame.grid(row=1, column=0, columnspan=2, padx=16, pady=(0, 8), sticky="w")
        
        for f in fields_to_match:
            var = tk.BooleanVar(value=False)
            self._match_vars[f] = var
            cb = ctk.CTkCheckBox(mf_frame, text=f.replace("_", " ").title(), variable=var,
                                 font=ctk.CTkFont(size=11), fg_color=_ACCENT, hover_color=_ACCENT_HOVER)
            cb.pack(side="left", padx=(0, 15))
            
        self._one_to_one_var = tk.BooleanVar(value=False)
        ctk.CTkCheckBox(comp, text="Conciliação Um-para-Um (Recomendado para Cheques)", 
                        variable=self._one_to_one_var,
                        font=ctk.CTkFont(size=11), fg_color=_ACCENT, hover_color=_ACCENT_HOVER).grid(
            row=2, column=0, columnspan=2, padx=16, pady=(0, 14), sticky="w")

        # Seção abas
        self._tabs_section = ctk.CTkFrame(body, fg_color=_CARD_BG, corner_radius=10)
        self._tabs_section.pack(fill="both", expand=True, padx=24, pady=(0, 8))

        self._tab_bar = ctk.CTkFrame(self._tabs_section, fg_color=_HEADER_BG,
                                      height=40, corner_radius=0)
        self._tab_bar.pack(fill="x")
        self._tab_bar.pack_propagate(False)

        self._panels_container = ctk.CTkFrame(self._tabs_section, fg_color=_PAGE_BG, height=520)
        self._panels_container.pack(fill="both", expand=True)
        self._panels_container.pack_propagate(False)

        # Rodapé
        footer = ctk.CTkFrame(body, fg_color="transparent")
        footer.pack(fill="x", padx=24, pady=(4, 20))
        ctk.CTkButton(footer, text="Cancelar", width=120, height=38,
                      fg_color="transparent", border_width=1, border_color=_CARD_BORDER,
                      font=ctk.CTkFont(size=13),
                      command=lambda: self.master.show_screen("home")).pack(side="right", padx=(8, 0))
        ctk.CTkButton(footer, text="💾  Salvar Perfil", width=150, height=38,
                      fg_color=_ACCENT, hover_color=_ACCENT_HOVER,
                      font=ctk.CTkFont(size=13, weight="bold"),
                      command=self._save).pack(side="right")

    def _create_tabs(self):
        for w in self._tab_bar.winfo_children():
            w.destroy()
        for p in self._panels:
            p.destroy()
        self._panels.clear()
        self._tab_btns.clear()

        mode = self._mode_var.get()
        n    = 2 if mode == "dual" else 1
        existing = self._profile.get("sheets", [])

        for i in range(n):
            cfg = existing[i] if i < len(existing) else {
                "label": "Planilha " + ("A" if i == 0 else "B"),
                "start_row": 1, "columns": []}
            panel = SheetPanel(self._panels_container, cfg)
            panel.place(x=0, y=0, relwidth=1, relheight=1)
            self._panels.append(panel)

            label = cfg.get("label") or ("Planilha " + ("A" if i == 0 else "B"))
            btn = ctk.CTkButton(self._tab_bar, text=f"  {label}  ",
                                height=38, corner_radius=0,
                                font=ctk.CTkFont(size=12, weight="bold"),
                                fg_color=_ACCENT if i == 0 else _HEADER_BG,
                                hover_color=_ACCENT_HOVER if i == 0 else _CARD_BG,
                                command=lambda idx=i: self._switch_tab(idx))
            btn.pack(side="left")
            self._tab_btns.append(btn)

        self._switch_tab(0)

    def _switch_tab(self, idx):
        self._active_tab = idx
        for i, (p, b) in enumerate(zip(self._panels, self._tab_btns)):
            if i == idx:
                p.lift()
                b.configure(fg_color=_ACCENT, hover_color=_ACCENT_HOVER)
            else:
                b.configure(fg_color=_HEADER_BG, hover_color=_CARD_BG)

    def _on_mode_change(self):
        if self._mode_var.get() == "single":
            self._comp_section.pack_forget()
        else:
            self._comp_section.pack(after=self._body.winfo_children()[0], fill="x", padx=24, pady=(0, 8))
        self._create_tabs()

    def _prefill(self):
        if not self._profile:
            self._create_tabs()
            return
        self._name_var.set(self._profile.get("name", ""))
        self._mode_var.set(self._profile.get("mode", "dual"))
        self._date_fmt_var.set(self._profile.get("date_format", "dd/mm/yyyy"))
        
        comp = self._profile.get("comparison", {})
        mfs = comp.get("match_fields", [])
        for f, var in self._match_vars.items():
            var.set(f in mfs)
        self._one_to_one_var.set(comp.get("one_to_one", False))

        if self.mode == "duplicate":
            self._name_var.set(f"Cópia de {self._profile.get('name','')}")
        
        self._on_mode_change() # Atualiza visibilidade da seção de comparação
        self._create_tabs()

    def _validate(self):
        name = self._name_var.get().strip()
        if not name:
            return "O nome do perfil não pode estar vazio."

        # Caracteres proibidos no Windows para nomes de arquivo
        invalid_chars = set('/\\|:*?"<>')
        found = [c for c in name if c in invalid_chars]
        if found:
            chars_str = "  ".join(f"'{c}'" for c in sorted(set(found)))
            return (
                f"O nome do perfil contém caracteres inválidos: {chars_str}\n\n"
                f"Esses caracteres não são permitidos em nomes de arquivo no Windows.\n"
                f"Por favor, remova-os e tente novamente."
            )

        for i, panel in enumerate(self._panels):
            cfg = panel.get_config()
            if not cfg["columns"]:
                lbl = cfg.get("label") or f"Planilha {'A' if i==0 else 'B'}"
                return f"A planilha '{lbl}' deve ter ao menos 1 campo configurado."
            for col in cfg["columns"]:
                try:
                    if int(col["col_index"]) < 1:
                        raise ValueError
                except (ValueError, TypeError):
                    return f"Índice de coluna inválido no campo '{col['field']}'."
        return None

    def _collect(self):
        import uuid
        mode   = self._mode_var.get()
        sheets = [p.get_config() for p in self._panels]

        if mode == "single":
            comparison = {"enabled": False, "match_fields": [], "one_to_one": False}
        else:
            mf = [f for f, var in self._match_vars.items() if var.get()]
            oto = self._one_to_one_var.get()
            comparison = {"enabled": True, "match_fields": mf, "one_to_one": oto}

        # Preservar output se editando perfil existente
        if self.mode == "edit" and self._profile.get("output"):
            output = self._profile["output"]
        else:
            output = _default_output(mode, sheets)

        pid = self._profile.get("id", str(uuid.uuid4())) if self.mode == "edit" else str(uuid.uuid4())

        return {
            "id": pid,
            "name": self._name_var.get().strip(),
            "mode": mode,
            "date_format": self._date_fmt_var.get(),
            "sheets": sheets,
            "comparison": comparison,
            "output": output,
        }

    def _save(self):
        err = self._validate()
        if err:
            messagebox.showerror("Dados inválidos", err)
            return
        profile = self._collect()
        save_profile(profile)
        messagebox.showinfo("Perfil salvo", f"Perfil '{profile['name']}' salvo com sucesso!")
        self.master.show_screen("home")


# ─────────────────────────────────────────────────────────────────────────────
def _default_output(mode, sheets):
    if mode == "single":
        cols = [{"header": c["field"].replace("_"," ").title(),
                 "field": c["field"], "fixed_value": None}
                for c in (sheets[0].get("columns",[]) if sheets else [])]
        return {"tabs": [{"name": "Dados Normalizados", "source": "normalizados", "columns": cols}]}

    la = sheets[0].get("label","A") if sheets else "A"
    lb = sheets[1].get("label","B") if len(sheets)>1 else "B"

    def _cols(sh):
        return [{"header": c["field"].replace("_"," ").title(),
                 "field": c["field"], "fixed_value": None}
                for c in sh.get("columns",[])]

    cc = _cols(sheets[0]) + [
        {"header": f"Linha {la}", "field": "__linha___a", "fixed_value": None},
        {"header": f"Linha {lb}", "field": "__linha___b", "fixed_value": None}]

    return {"tabs": [
        {"name": "Dados Conciliados",          "source": "conciliados",       "columns": cc},
        {"name": f"Não Conciliados - {la}",    "source": "nao_conciliados_a",
         "columns": _cols(sheets[0]) + [{"header": f"Linha {la}", "field": "__linha__", "fixed_value": None}]},
        {"name": f"Não Conciliados - {lb}",    "source": "nao_conciliados_b",
         "columns": _cols(sheets[1] if len(sheets)>1 else {}) + [{"header": f"Linha {lb}", "field": "__linha__", "fixed_value": None}]},
    ]}
