# -*- coding: utf-8 -*-
"""Registro plugável de módulos da plataforma.

Cada módulo expõe um MANIFEST (metadados para o Hub) e um APIRouter.
Para adicionar um módulo novo:

    from web.modules.meu_modulo.router import router as meu_router, MANIFEST as meu_manifest
    ALL_MODULES.append(Module(manifest=meu_manifest, router=meu_router))

O endpoint GET /api/modules expõe os manifestos para o frontend montar os cards.
"""
from dataclasses import dataclass

from fastapi import APIRouter
from pydantic import BaseModel


class ModuleManifest(BaseModel):
    id: str
    title: str
    description: str
    icon: str  # nome de ícone lucide-react (ex.: "file-spreadsheet")


@dataclass
class Module:
    manifest: ModuleManifest
    router: APIRouter


# Vazio nesta fase — o módulo Conciliador é registrado na Task 02.
ALL_MODULES: list[Module] = []


def get_manifests() -> list[ModuleManifest]:
    return [m.manifest for m in ALL_MODULES]
