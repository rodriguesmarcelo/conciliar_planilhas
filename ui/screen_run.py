# -*- coding: utf-8 -*-
"""
Task 08 — Tela de Execução da Conciliação
"""
import os
import sys
import threading
import traceback
from datetime import datetime
from tkinter import filedialog, messagebox

import customtkinter as ctk

from core.reader import read_sheet, validate_columns, ColumnNotFoundError, InvalidFileError
from core.engine import run as engine_run
from core.exporter import export_result

# ── Paleta ───────────────────────────────────────────────────────────────────
_ACCENT        = "#1F6FEB"
_ACCENT_HOVER  = "#1558C0"
_SUCCESS       = "#238636"
_SUCCESS_HOVER = "#196127"
_DANGER        = "#F85149"
_PAGE_BG       = "#0D1117"
_HEADER_BG     = "#161B22"
_CARD_BG       = "#1E2128"
_CARD_BORDER   = "#30363D"
_INPUT_BG      = "#161B22"
_TEXT_MUTED    = "#848D97"
_TEXT_NORMAL   = "#C9D1D9"
_PROGRESS_BG   = "#21262D"
_PROGRESS_FG   = "#1F6FEB"


# ── Widget de seleção de arquivo ─────────────────────────────────────────────
class FileSelector(ctk.CTkFrame):
    """Linha com label, caixa de path e botão Selecionar."""

    def __init__(self, master, label: str, **kwargs):
        super().__init__(master, fg_color=_CARD_BG, corner_radius=10, **kwargs)
        self._path = ""
        self._build(label)

    def _build(self, label: str):
        # Label da planilha
        ctk.CTkLabel(
            self, text=label,
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w",
        ).pack(fill="x", padx=16, pady=(12, 6))

        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", padx=16, pady=(0, 12))
        row.columnconfigure(0, weight=1)

        # Path display
        self._path_var = ctk.StringVar(value="Nenhum arquivo selecionado")
        self._path_entry = ctk.CTkEntry(
            row, textvariable=self._path_var,
            height=34, state="readonly",
            fg_color=_INPUT_BG,
            text_color=_TEXT_MUTED,
            font=ctk.CTkFont(size=11),
        )
        self._path_entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        # Botão selecionar
        ctk.CTkButton(
            row, text="📂  Selecionar",
            width=120, height=34,
            font=ctk.CTkFont(size=12),
            fg_color=_INPUT_BG,
            hover_color=_HEADER_BG,
            border_width=1, border_color=_CARD_BORDER,
            command=self._pick,
        ).grid(row=0, column=1)

    def _pick(self):
        path = filedialog.askopenfilename(
            title="Selecionar planilha",
            filetypes=[("Excel / CSV", "*.xlsx *.xls *.csv"), ("Todos", "*.*")],
        )
        if path:
            # Detectar .xls (formato legado) e solicitar conversão
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
            self._path = path
            self._path_var.set(os.path.basename(path))
            self._path_entry.configure(text_color=_TEXT_NORMAL)

    @property
    def path(self) -> str:
        return self._path

    @path.setter
    def path(self, value: str):
        self._path = value
        if value:
            self._path_var.set(os.path.basename(value))
            self._path_entry.configure(text_color=_TEXT_NORMAL)


# ── Tela de Execução ─────────────────────────────────────────────────────────
class RunScreen(ctk.CTkFrame):
    """Tela principal de execução da conciliação."""

    def __init__(self, master, profile: dict = None, **kwargs):
        super().__init__(master, fg_color=_PAGE_BG, **kwargs)
        self.master   = master
        self.profile  = profile or {}
        self._running = False
        self._result  = None
        self._output_path = ""
        self._build()

    # ── Layout ───────────────────────────────────────────────────────────────
    def _build(self):
        mode  = self.profile.get("mode", "dual")
        nome  = self.profile.get("name", "")
        sheets = self.profile.get("sheets", [])

        # Header
        header = ctk.CTkFrame(self, fg_color=_HEADER_BG, height=60, corner_radius=0)
        header.pack(fill="x")
        header.pack_propagate(False)

        self._back_btn = ctk.CTkButton(
            header, text="← Voltar", width=90, height=32,
            fg_color="transparent", hover_color=_CARD_BG,
            font=ctk.CTkFont(size=12),
            border_width=1, border_color=_CARD_BORDER,
            command=self._go_back,
        )
        self._back_btn.pack(side="left", padx=16, pady=14)

        ctk.CTkLabel(
            header,
            text=f"⚙️  Executar Conciliação — {nome}",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(side="left", padx=8)

        # Corpo
        body = ctk.CTkScrollableFrame(self, fg_color=_PAGE_BG)
        body.pack(fill="both", expand=True)
        self._body = body

        # ── Seletores de arquivo ──
        files_card = ctk.CTkFrame(body, fg_color="transparent")
        files_card.pack(fill="x", padx=32, pady=(20, 8))

        label_a = sheets[0]["label"] if sheets else "Planilha A"
        self._sel_a = FileSelector(files_card, f"Planilha A — {label_a}")
        self._sel_a.pack(fill="x", pady=(0, 8))

        self._sel_b = None
        if mode == "dual":
            label_b = sheets[1]["label"] if len(sheets) > 1 else "Planilha B"
            self._sel_b = FileSelector(files_card, f"Planilha B — {label_b}")
            self._sel_b.pack(fill="x")

        # ── Área de status + progresso ──
        self._status_card = ctk.CTkFrame(body, fg_color=_CARD_BG, corner_radius=10)
        self._status_card.pack(fill="x", padx=32, pady=8)

        self._status_lbl = ctk.CTkLabel(
            self._status_card,
            text="Aguardando arquivos...",
            font=ctk.CTkFont(size=12),
            text_color=_TEXT_MUTED,
            anchor="w",
        )
        self._status_lbl.pack(fill="x", padx=16, pady=(12, 6))

        self._progress = ctk.CTkProgressBar(
            self._status_card,
            height=8,
            progress_color=_PROGRESS_FG,
            fg_color=_PROGRESS_BG,
            corner_radius=4,
        )
        self._progress.set(0)
        self._progress.pack(fill="x", padx=16, pady=(0, 12))

        # ── Botão Executar ──
        btn_frame = ctk.CTkFrame(body, fg_color="transparent")
        btn_frame.pack(fill="x", padx=32, pady=(4, 24))

        self._exec_btn = ctk.CTkButton(
            btn_frame,
            text="▶  Executar Conciliação",
            height=44,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=_ACCENT, hover_color=_ACCENT_HOVER,
            corner_radius=8,
            command=self._on_execute,
        )
        self._exec_btn.pack(fill="x")

        # ── Painel de resultado (oculto inicialmente) ──
        self._result_card = ctk.CTkFrame(body, fg_color=_CARD_BG, corner_radius=10)
        # Não empacotado ainda — aparece após conclusão

    # ── Ações ────────────────────────────────────────────────────────────────
    def _go_back(self):
        if self._running:
            if not messagebox.askyesno(
                "Processamento em andamento",
                "Um processamento está em andamento. Deseja cancelar e sair?",
            ):
                return
        self.master.show_screen("home")

    def _on_execute(self):
        if self._running:
            return

        # Passo 1 — validar arquivos
        if not self._sel_a.path:
            messagebox.showwarning("Arquivo não selecionado",
                                   "Selecione o arquivo da Planilha A antes de executar.")
            return
        if self._sel_b is not None and not self._sel_b.path:
            messagebox.showwarning("Arquivo não selecionado",
                                   "Selecione o arquivo da Planilha B antes de executar.")
            return

        # Passo 2 — validar colunas
        sheets = self.profile.get("sheets", [])
        try:
            validate_columns(self._sel_a.path, sheets[0])
            if self._sel_b and len(sheets) > 1:
                validate_columns(self._sel_b.path, sheets[1])
        except ColumnNotFoundError as e:
            messagebox.showerror("Coluna não encontrada", str(e))
            return
        except InvalidFileError as e:
            messagebox.showerror("Arquivo inválido", str(e))
            return

        # Passo 4 — solicitar onde salvar (ANTES de processar)
        nome_perfil = self.profile.get("name", "resultado").replace(" ", "_")
        data_hoje   = datetime.now().strftime("%d-%m-%Y")
        sugerido    = f"Resultado_{nome_perfil}_{data_hoje}.xlsx"

        last_dir = self.master.get_last_output_dir() if hasattr(self.master, "get_last_output_dir") else ""
        output_path = filedialog.asksaveasfilename(
            title="Salvar resultado como...",
            defaultextension=".xlsx",
            filetypes=[("Excel", "*.xlsx")],
            initialfile=sugerido,
            initialdir=last_dir or os.path.expanduser("~"),
        )
        if not output_path:
            return  # usuário cancelou

        self._output_path = output_path

        # Salvar último diretório
        if hasattr(self.master, "set_last_output_dir"):
            self.master.set_last_output_dir(os.path.dirname(output_path))

        # Passo 3 — executar em thread
        self._running = True
        self._exec_btn.configure(state="disabled", text="⏳  Processando...")
        self._hide_result()
        # Cursor de espera
        if hasattr(self.master, "set_busy"):
            self.master.set_busy(True)

        thread = threading.Thread(target=self._run_process, daemon=True)
        thread.start()

    # ── Thread de processamento ───────────────────────────────────────────────
    def _run_process(self):
        try:
            sheets   = self.profile.get("sheets", [])
            mode     = self.profile.get("mode", "dual")
            date_fmt = self.profile.get("date_format", "dd/mm/yyyy")

            # 10% — Lendo planilha A
            self._set_status(f"Lendo Planilha A ({sheets[0]['label']})...", 0.10)
            df_a = read_sheet(self._sel_a.path, sheets[0], date_fmt)

            df_b = None
            if mode == "dual" and self._sel_b:
                # 30% — Lendo planilha B
                self._set_status(f"Lendo Planilha B ({sheets[1]['label']})...", 0.30)
                df_b = read_sheet(self._sel_b.path, sheets[1], date_fmt)

            # 50% — Conciliação
            self._set_status("Executando conciliação...", 0.50)
            result = engine_run(self.profile, df_a, df_b)

            # 80% — Exportando
            self._set_status("Gerando arquivo de resultado...", 0.80)
            file_b_path = self._sel_b.path if self._sel_b else None
            export_result(
                result, self.profile, self._output_path,
                file_a=self._sel_a.path,
                file_b=file_b_path,
            )

            # 100% — Concluído
            self._set_status("Concluído!", 1.0)
            self._result = result
            if hasattr(self.master, "set_busy"):
                self.after(0, lambda: self.master.set_busy(False))
            self.after(0, self._show_result)

        except ColumnNotFoundError as e:
            self.after(0, lambda: self._on_error(str(e)))
        except InvalidFileError as e:
            self.after(0, lambda: self._on_error(str(e)))
        except FileNotFoundError:
            msg = "O arquivo selecionado não foi encontrado. Selecione novamente."
            self.after(0, lambda m=msg: self._on_error(m))
        except PermissionError:
            msg = "Não foi possível salvar o resultado. Verifique se o arquivo não está aberto em outro programa."
            self.after(0, lambda m=msg: self._on_error(m))
        except Exception as e:
            traceback.print_exc()
            msg = f"Erro inesperado durante o processamento:\n{type(e).__name__}: {e}"
            self.after(0, lambda m=msg: self._on_error(m))
        finally:
            self._running = False
            if hasattr(self.master, "set_busy"):
                self.after(0, lambda: self.master.set_busy(False))

    def _set_status(self, text: str, progress: float):
        """Atualiza status e barra de progresso de forma thread-safe."""
        def _update():
            self._status_lbl.configure(text=text, text_color=_TEXT_NORMAL)
            self._progress.set(progress)
        self.after(0, _update)

    # ── Painel de resultado ───────────────────────────────────────────────────
    def _show_result(self):
        self._exec_btn.configure(state="disabled", text="✅  Concluído")

        # Limpar painel anterior
        for w in self._result_card.winfo_children():
            w.destroy()

        result = self._result
        mode   = self.profile.get("mode", "dual")
        sheets = self.profile.get("sheets", [])

        # Título
        ctk.CTkLabel(
            self._result_card,
            text="✅  Conciliação concluída!",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#3FB950",
        ).pack(anchor="w", padx=20, pady=(16, 12))

        # Contagens
        counts_frame = ctk.CTkFrame(self._result_card, fg_color=_INPUT_BG, corner_radius=8)
        counts_frame.pack(fill="x", padx=20, pady=(0, 12))

        def _stat_row(label, value, color=_TEXT_NORMAL):
            row = ctk.CTkFrame(counts_frame, fg_color="transparent")
            row.pack(fill="x", padx=12, pady=3)
            ctk.CTkLabel(row, text=label,
                         font=ctk.CTkFont(size=12), text_color=_TEXT_MUTED,
                         anchor="w").pack(side="left")
            ctk.CTkLabel(row, text=str(value),
                         font=ctk.CTkFont(size=12, weight="bold"), text_color=color,
                         anchor="e").pack(side="right")

        def _safe_len(df):
            if df is None:
                return 0
            try:
                return len(df)
            except Exception:
                return 0

        if mode == "single":
            n_norm = _safe_len(result.get("normalizados"))
            _stat_row("Registros normalizados:", n_norm, "#3FB950")
        else:
            n_conc = _safe_len(result.get("conciliados"))
            n_nca  = _safe_len(result.get("nao_conciliados_a"))
            n_ncb  = _safe_len(result.get("nao_conciliados_b"))
            label_a = sheets[0]["label"] if sheets else "A"
            label_b = sheets[1]["label"] if len(sheets) > 1 else "B"

            _stat_row("Registros conciliados:", n_conc, "#3FB950")
            _stat_row(f"Não conciliados ({label_a}):", n_nca,
                      _DANGER if n_nca > 0 else _TEXT_NORMAL)
            _stat_row(f"Não conciliados ({label_b}):", n_ncb,
                      _DANGER if n_ncb > 0 else _TEXT_NORMAL)

        # Caminho do arquivo
        ctk.CTkLabel(
            self._result_card,
            text="Arquivo salvo em:",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=_TEXT_MUTED, anchor="w",
        ).pack(anchor="w", padx=20, pady=(4, 2))

        ctk.CTkLabel(
            self._result_card,
            text=self._output_path,
            font=ctk.CTkFont(size=11),
            text_color=_TEXT_NORMAL, anchor="w",
            wraplength=600,
        ).pack(anchor="w", padx=20, pady=(0, 12))

        # Botões
        btns = ctk.CTkFrame(self._result_card, fg_color="transparent")
        btns.pack(fill="x", padx=20, pady=(0, 16))

        ctk.CTkButton(
            btns, text="📂  Abrir arquivo",
            width=160, height=38,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=_SUCCESS, hover_color=_SUCCESS_HOVER,
            command=self._open_file,
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            btns, text="↺  Nova conciliação",
            width=160, height=38,
            font=ctk.CTkFont(size=12),
            fg_color="transparent",
            border_width=1, border_color=_CARD_BORDER,
            command=lambda: self.master.show_screen("home"),
        ).pack(side="left")

        # Exibir o painel de resultado
        self._result_card.pack(fill="x", padx=32, pady=(0, 24))

    def _hide_result(self):
        self._result_card.pack_forget()

    def _on_error(self, message: str):
        self._exec_btn.configure(state="normal", text="▶  Executar Conciliação")
        self._status_lbl.configure(
            text=f"❌  Erro: {message.splitlines()[0]}", text_color=_DANGER)
        self._progress.set(0)
        messagebox.showerror("Erro durante a execução", message)

    def _open_file(self):
        path = self._output_path
        if not path or not os.path.exists(path):
            messagebox.showwarning("Arquivo não encontrado",
                                   "O arquivo de resultado não foi encontrado.")
            return
        try:
            if sys.platform == "win32":
                os.startfile(path)
            elif sys.platform == "darwin":
                import subprocess
                subprocess.run(["open", path])
            else:
                import subprocess
                subprocess.run(["xdg-open", path])
        except Exception as e:
            messagebox.showerror("Erro ao abrir arquivo", str(e))
