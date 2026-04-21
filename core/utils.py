# -*- coding: utf-8 -*-
"""
Utilitários de caminho — funciona tanto em desenvolvimento quanto empacotado com PyInstaller.
"""
import os
import sys


def resource_path(relative_path: str) -> str:
    """
    Resolve caminho para recursos somente-leitura (perfis default, config bundled).
    Dentro do .exe usa sys._MEIPASS; em dev usa o diretório do projeto.
    """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(_project_root(), relative_path)


def get_user_data_dir() -> str:
    """
    Retorna a pasta gravável para dados do usuário (perfis criados, config).
    Dentro do .exe usa a pasta do executável; em dev usa o diretório do projeto.
    """
    if hasattr(sys, '_MEIPASS'):
        return os.path.dirname(sys.executable)
    return _project_root()


def get_profiles_dir() -> str:
    """Retorna o caminho da pasta de perfis do usuário (gravável)."""
    path = os.path.join(get_user_data_dir(), "profiles")
    os.makedirs(path, exist_ok=True)
    return path


def get_config_path() -> str:
    """Retorna o caminho do config.json do usuário."""
    return os.path.join(get_user_data_dir(), "config.json")


def _project_root() -> str:
    """Raiz do projeto (pasta que contém main.py)."""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
