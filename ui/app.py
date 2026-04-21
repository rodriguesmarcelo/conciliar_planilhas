# -*- coding: utf-8 -*-
import json
import os
import customtkinter as ctk

# ── Configuração global ──────────────────────────────────────────────────────
_CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json")

def _load_config() -> dict:
    defaults = {
        "appearance_mode": "dark",
        "color_theme": "blue",
        "last_output_dir": "",
        "window_geometry": "1000x660",
    }
    try:
        with open(_CONFIG_PATH, encoding="utf-8") as f:
            data = json.load(f)
        defaults.update(data)
    except Exception:
        pass
    return defaults

def _save_config(cfg: dict):
    try:
        with open(_CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


# ── Aplicação principal ──────────────────────────────────────────────────────
class App(ctk.CTk):
    def __init__(self):
        self.config = _load_config()

        ctk.set_appearance_mode(self.config.get("appearance_mode", "dark"))
        ctk.set_default_color_theme(self.config.get("color_theme", "blue"))

        super().__init__()
        self.title("Conciliador de Planilhas")
        self.geometry(self.config.get("window_geometry", "1000x660"))
        self.minsize(800, 560)

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

    # ── Config helpers ───────────────────────────────────────────────────────
    def get_last_output_dir(self) -> str:
        return self.config.get("last_output_dir", "")

    def set_last_output_dir(self, path: str):
        self.config["last_output_dir"] = path
        _save_config(self.config)

    def _on_close(self):
        # Salvar geometria da janela
        self.config["window_geometry"] = self.geometry()
        _save_config(self.config)
        self.destroy()
