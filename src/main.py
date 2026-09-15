#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FAC -> DOCX/PDF converter

The FAC files used by the old system are binary files containing text records.
This converter was built to handle the FAC samples supplied with this project.

Dependencies:
    pip install python-docx reportlab
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


# Bytes used by the old FAC format as record/formatting markers.
RECORD_SEPARATOR = b"\x01"
END_OF_FILE = b"\x1a"


def decode_fac(data: bytes) -> str:
    """Extract and decode the textual portion of a FAC file.

    The supplied FAC samples use a legacy IBM PC character set close to
    CP860 for Portuguese text, while some bytes are formatting/spacing
    markers rather than characters. The parser therefore works at byte level
    before decoding.
    """
    pos = data.find(b"PORTARIA")
    if pos < 0:
        raise ValueError("Não encontrei o início textual 'PORTARIA' no arquivo FAC.")

    data = data[pos:]

    # Remove EOF and convert FAC record separators into real line breaks.
    data = data.replace(END_OF_FILE, b"")
    data = data.replace(RECORD_SEPARATOR, b"\n")

    # FAC formatting markers observed in the supplied files.
    data = data.replace(b"\x1e", b"")   # print/format marker
    data = data.replace(b"\x02", b"")   # print/format marker
    data = data.replace(b"\x8d", b"")   # continuation marker
    data = data.replace(b"\xfe", b"")   # line-break/hyphenation marker
    data = data.replace(b"\xa0", b" ")  # fixed/non-breaking spacing marker

    # Decode Portuguese text. CP860 correctly represents characters such as
    # ã/õ/ç in the supplied FAC files.
    text = data.decode("cp860", errors="replace")

    # Normalize line endings and remove remaining non-printing controls.
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)

    # Remove trailing whitespace only; keep leading spaces because they carry
    # the original FAC indentation/alignment.
    lines = [line.rstrip() for line in text.split("\n")]

    # Avoid a huge empty tail caused by binary/formatting records.
    while lines and not lines[-1].strip():
        lines.pop()

    return "\n".join(lines)


def convert_to_docx(fac_path: Path, output_path: Path) -> None:
    from docx import Document
    from docx.shared import Cm, Pt
    from docx.enum.text import WD_LINE_SPACING

    text = decode_fac(fac_path.read_bytes())

    doc = Document()
    section = doc.sections[0]
    section.top_margin = Cm(2.0)
    section.bottom_margin = Cm(2.0)
    section.left_margin = Cm(2.0)
    section.right_margin = Cm(2.0)

    # Monospace keeps the spaces/indentation from the original FAC layout.
    style = doc.styles["Normal"]
    style.font.name = "Courier New"
    style.font.size = Pt(9.5)

    for line in text.split("\n"):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
        run = p.add_run(line if line else " ")
        run.font.name = "Courier New"
        run.font.size = Pt(9.5)

    doc.save(output_path)


def convert_to_pdf(fac_path: Path, output_path: Path) -> None:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfbase.pdfmetrics import stringWidth
    from reportlab.pdfgen import canvas

    text = decode_fac(fac_path.read_bytes())

    c = canvas.Canvas(str(output_path), pagesize=A4)
    width, height = A4

    font = "Courier"
    font_size = 8.5
    leading = 10
    x = 45
    y = height - 45

    c.setFont(font, font_size)

    for line in text.split("\n"):
        # FAC lines are normally short, but wrap defensively if needed.
        max_width = width - 2 * x
        if stringWidth(line, font, font_size) <= max_width:
            chunks = [line]
        else:
            max_chars = max(1, int(max_width / stringWidth("M", font, font_size)))
            chunks = [line[i:i + max_chars] for i in range(0, len(line), max_chars)]

        for chunk in chunks:
            if y < 45:
                c.showPage()
                c.setFont(font, font_size)
                y = height - 45
            c.drawString(x, y, chunk)
            y -= leading

    c.save()


def main() -> None:
    parser = argparse.ArgumentParser(description="Converte arquivos .FAC antigos para DOCX ou PDF.")
    parser.add_argument("files", nargs="*", type=Path, help="Um ou mais arquivos .FAC")
    parser.add_argument("--pdf", action="store_true", help="Gera PDF em vez de DOCX")
    parser.add_argument("--out", type=Path, default=None, help="Pasta de saída")
    args = parser.parse_args()

    input_dir = Path("data/input")
    output_dir = args.out or Path("data/output")

    files = args.files

    if not files:
        files = list(input_dir.glob("*.fac"))

    output_dir = args.out or Path("data/output")
    output_dir.mkdir(parents=True, exist_ok=True)

    for fac in args.files:
        if fac.suffix.lower() != ".fac":
            print(f"[AVISO] Ignorado (não é .FAC): {fac}")
            continue
        if not fac.is_file():
            print(f"[ERRO] Arquivo não encontrado: {fac}")
            continue

        extension = ".pdf" if args.pdf else ".docx"
        destination = output_dir / (fac.stem + extension)

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
