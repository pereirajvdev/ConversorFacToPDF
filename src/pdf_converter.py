""
""

from pathlib import Path
from .fac_decoder import decode_fac

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