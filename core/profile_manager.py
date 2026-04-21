# -*- coding: utf-8 -*-
import json
import os
import uuid
from typing import Optional


def _profiles_dir() -> str:
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(base, "profiles")
    os.makedirs(path, exist_ok=True)
    return path


def load_all_profiles() -> dict:
    """Retorna dict {id: profile} com todos os perfis da pasta profiles/."""
    profiles = {}
    folder = _profiles_dir()
    for filename in sorted(os.listdir(folder)):
        if filename.endswith(".json"):
            filepath = os.path.join(folder, filename)
            try:
                with open(filepath, encoding="utf-8") as f:
                    profile = json.load(f)
                profile_id = profile.get("id", filename.replace(".json", ""))
                profiles[profile_id] = profile
            except Exception as e:
                print(f"[profile_manager] Erro ao carregar {filename}: {e}")
    return profiles


def load_profile(profile_id: str) -> Optional[dict]:
    """Carrega um perfil pelo id. Retorna None se não encontrado."""
    profiles = load_all_profiles()
    return profiles.get(profile_id)


def save_profile(profile: dict) -> str:
    """
    Salva (cria ou sobrescreve) um perfil na pasta profiles/.
    Gera id se não existir.
    Retorna o id do perfil salvo.
    """
    if "id" not in profile or not profile["id"]:
        profile["id"] = str(uuid.uuid4())

    profile_id = profile["id"]
    safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in profile_id)
    filepath = os.path.join(_profiles_dir(), f"{safe_name}.json")

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(profile, f, ensure_ascii=False, indent=2)

    return profile_id


def delete_profile(profile_id: str) -> bool:
    """Remove o arquivo JSON do perfil. Retorna True se removido."""
    folder = _profiles_dir()
    for filename in os.listdir(folder):
        if not filename.endswith(".json"):
            continue
        filepath = os.path.join(folder, filename)
        try:
            with open(filepath, encoding="utf-8") as f:
                data = json.load(f)
            if data.get("id") == profile_id:
                os.remove(filepath)
                return True
        except Exception:
            continue
    return False


def duplicate_profile(profile_id: str) -> Optional[dict]:
    """
    Cria uma cópia do perfil com novo id e nome 'Cópia de X'.
    Retorna o novo perfil ou None se o original não existir.
    """
    original = load_profile(profile_id)
    if original is None:
        return None

    import copy
    novo = copy.deepcopy(original)
    novo["id"] = str(uuid.uuid4())
    novo["name"] = f"Cópia de {original.get('name', profile_id)}"

    save_profile(novo)
    return novo
