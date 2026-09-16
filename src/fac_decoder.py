""

""

import re

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