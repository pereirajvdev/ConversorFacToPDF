#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FAC -> DOCX/PDF converter

The FAC files used by the old system are binary files containing text records.
This converter was built to handle the FAC samples supplied with this project.

Dependencies:
    pip install python-docx reportlab
"""

import argparse
from pathlib import Path

from .docx_converter import convert_to_docx
from .pdf_converter import convert_to_pdf
from .file_manager import (
    find_fac_files,
    create_output_dir,
    get_output_path,
)

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Converte arquivos .FAC antigos para DOCX ou PDF."
    )

    parser.add_argument(
        "files",
        nargs="*",
        type=Path,
        help="Um ou mais arquivos .FAC"
    )

    parser.add_argument(
        "--pdf",
        action="store_true",
        help="Gera PDF em vez de DOCX"
    )

    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Pasta de saída"
    )

    args = parser.parse_args()

    # Raiz do projeto
    project_dir = Path(__file__).resolve().parent.parent

    # Pastas padrão
    input_dir = project_dir / "data" / "input"
    output_dir = args.out or project_dir / "data" / "output"

    # Refatoração do files
    files = find_fac_files(args.files, input_dir)

    # Garante que a pasta de saída exista
    create_output_dir(output_dir)

    for fac in files:
        if fac.suffix.lower() != ".fac":
            print(f"[AVISO] Ignorado (não é .FAC): {fac}")
            continue

        if not fac.is_file():
            print(f"[ERRO] Arquivo não encontrado: {fac}")
            continue

        extension = ".pdf" if args.pdf else ".docx"
        destination = get_output_path(fac, output_dir, extension)

        try:
            if args.pdf:
                convert_to_pdf(fac, destination)
            else:
                convert_to_docx(fac, destination)

            print(f"[OK] {fac.name} -> {destination}")

        except Exception as exc:
            print(f"[ERRO] {fac.name}: {exc}")


if __name__ == "__main__":
    main()
