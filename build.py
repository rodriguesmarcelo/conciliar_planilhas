#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build.py — Script de empacotamento do Conciliador de Planilhas.

Uso:
    python build.py

Gera o executável em dist/Conciliador.exe (Windows) ou dist/Conciliador (Linux/macOS).
"""
import os
import sys
import subprocess
import shutil


def main():
    print("=" * 60)
    print("  Conciliador de Planilhas — Build Script")
    print("=" * 60)

    # Verificar PyInstaller
    try:
        import PyInstaller
        print(f"✅ PyInstaller {PyInstaller.__version__} encontrado")
    except ImportError:
        print("❌ PyInstaller não encontrado. Instalando...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    # Separador de dados (Windows usa ;, outros usam :)
    sep = ";" if sys.platform == "win32" else ":"

    icon_path = os.path.join("assets", "icon.ico")
    icon_args = ["--icon", icon_path] if os.path.exists(icon_path) else []

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--name", "Conciliador",
        "--add-data", f"profiles{sep}profiles",
        "--add-data", f"config.json{sep}.",
        "--hidden-import", "openpyxl",
        "--hidden-import", "pandas",
        "--hidden-import", "customtkinter",
        "--clean",
        "--noconfirm",
    ] + icon_args + ["main.py"]

    print(f"\n🔨 Executando PyInstaller...")
    print(f"   Comando: {' '.join(cmd)}\n")

    result = subprocess.run(cmd)
    if result.returncode != 0:
        print("\n❌ Build falhou!")
        sys.exit(1)

    # Resultado
    exe_name = "Conciliador.exe" if sys.platform == "win32" else "Conciliador"
    exe_path = os.path.join("dist", exe_name)

    if os.path.exists(exe_path):
        size_mb = os.path.getsize(exe_path) / (1024 * 1024)
        print(f"\n✅ Build concluído com sucesso!")
        print(f"   Arquivo: {os.path.abspath(exe_path)}")
        print(f"   Tamanho: {size_mb:.1f} MB")
    else:
        print(f"\n⚠️  Executável não encontrado em {exe_path}")

    print("\nPara distribuir, copie o arquivo 'dist/Conciliador.exe' para a máquina destino.")
    print("Nenhuma instalação de Python é necessária no destino.")


if __name__ == "__main__":
    main()
