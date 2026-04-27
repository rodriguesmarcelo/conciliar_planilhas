# -*- coding: utf-8 -*-
import json
import os
import customtkinter as ctk

from core.utils import get_config_path, resource_path, get_user_data_dir
import shutil as _shutil


def _ensure_config():
    """Copia config.json bundled para pasta gravável se não existir ainda."""
    dest = get_config_path()
    if not os.path.exists(dest):
        bundled = resource_path("config.json")
        if os.path.exists(bundled):
            try:
                _shutil.copy2(bundled, dest)
            except Exception:
                pass


# ── Config ───────────────────────────────────────────────────────────────────
def _load_config() -> dict:
    defaults = {
        "appearance_mode": "dark",
        "color_theme": "blue",
        "last_output_dir": "",
        "window_geometry": "1000x660",
    }
    try:
        with open(get_config_path(), encoding="utf-8") as f:
            data = json.load(f)
        defaults.update(data)
    except Exception:
        pass
    return defaults


def _save_config(cfg: dict):
    try:
        with open(get_config_path(), "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


# ── Aplicação principal ──────────────────────────────────────────────────────
class App(ctk.CTk):
    def __init__(self):
        _ensure_config()
        self.config_data = _load_config()

        ctk.set_appearance_mode(self.config_data.get("appearance_mode", "dark"))
        ctk.set_default_color_theme(self.config_data.get("color_theme", "blue"))

        super().__init__()
        self.title("Conciliador de Planilhas")
        self.geometry(self.config_data.get("window_geometry", "1000x660"))
        self.minsize(800, 560)

        # Ícone da janela (opcional)
        icon_path = resource_path(os.path.join("assets", "icon.ico"))
        if os.path.exists(icon_path):
            try:
                self.iconbitmap(icon_path)
            except Exception:
                pass

        self.current_screen = None
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.show_screen("home")

    # ── Navegação ────────────────────────────────────────────────────────────
    def show_screen(self, screen_name: str, **kwargs):
        if self.current_screen is not None:
            self.current_screen.destroy()
            self.current_screen = None

        if screen_name == "home":
            from ui.screen_home import HomeScreen
            self.current_screen = HomeScreen(self, **kwargs)
        elif screen_name == "run":
            from ui.screen_run import RunScreen
            self.current_screen = RunScreen(self, **kwargs)
        elif screen_name == "profile_edit":
            from ui.screen_profile import ProfileScreen
            self.current_screen = ProfileScreen(self, **kwargs)

        if self.current_screen:
            self.current_screen.pack(fill="both", expand=True)

    # ── Cursor de espera ─────────────────────────────────────────────────────
    def set_busy(self, busy: bool):
        """Altera cursor e título para indicar processamento."""
        if busy:
            self.configure(cursor="watch")
            self.title("Conciliador — Processando...")
        else:
            self.configure(cursor="")
            self.title("Conciliador de Planilhas")

    # ── Config helpers ───────────────────────────────────────────────────────
    def get_last_output_dir(self) -> str:
        return self.config_data.get("last_output_dir", "")

    def set_last_output_dir(self, path: str):
        self.config_data["last_output_dir"] = path
        _save_config(self.config_data)

    def _on_close(self):
        self.config_data["window_geometry"] = self.geometry()
        _save_config(self.config_data)
        self.destroy()
