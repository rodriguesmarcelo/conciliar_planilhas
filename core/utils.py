# -*- coding: utf-8 -*-
"""
Utilitários de caminho — funciona tanto em desenvolvimento quanto empacotado com PyInstaller.

Separação clara de responsabilidades:
  - resource_path()    → recursos somente-leitura bundled no .exe (sys._MEIPASS)
  - get_user_data_dir() → pasta gravável ao lado do .exe (ou raiz do projeto em dev)
  - get_profiles_dir() → pasta de perfis GRAVÁVEL do usuário
  - ensure_default_profiles() → copia perfis bundled para pasta do usuário na 1ª execução
"""
import os
import sys
import shutil


def resource_path(relative_path: str) -> str:
    """
    Resolve caminho para recursos somente-leitura bundled.
    Dentro do .exe usa sys._MEIPASS; em dev usa o diretório do projeto.
    """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(_project_root(), relative_path)


def get_user_data_dir() -> str:
    """
    Retorna a pasta gravável para dados do usuário.
    - Dentro do .exe: pasta onde o executável está localizado
    - Em dev: raiz do projeto
    """
    if hasattr(sys, '_MEIPASS'):
        return os.path.dirname(sys.executable)
    return _project_root()


def get_profiles_dir() -> str:
    """
    Retorna o caminho da pasta de perfis GRAVÁVEL do usuário.
    Cria a pasta se não existir e copia os perfis default na primeira execução.
    """
    path = os.path.join(get_user_data_dir(), "profiles")
    os.makedirs(path, exist_ok=True)

    # Na primeira execução (pasta vazia), copiar perfis default bundled
    existing = [f for f in os.listdir(path) if f.endswith(".json")]
    if not existing:
        _copy_default_profiles(path)

    return path


def get_config_path() -> str:
    """Retorna o caminho do config.json gravável do usuário."""
    return os.path.join(get_user_data_dir(), "config.json")


def _copy_default_profiles(dest_dir: str):
    """
    Copia os perfis default (bundled) para a pasta gravável do usuário.
    Chamado automaticamente na primeira execução.
    """
    bundled_profiles = resource_path("profiles")
    if not os.path.isdir(bundled_profiles):
        return
    for filename in os.listdir(bundled_profiles):
        if not filename.endswith(".json"):
            continue
        src = os.path.join(bundled_profiles, filename)
        dst = os.path.join(dest_dir, filename)
        if not os.path.exists(dst):
            try:
                shutil.copy2(src, dst)
            except Exception as e:
                print(f"[utils] Erro ao copiar perfil default '{filename}': {e}")


def _project_root() -> str:
    """Raiz do projeto (pasta que contém main.py)."""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
