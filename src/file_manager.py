from pathlib import Path

def find_fac_files(paths: list[Path], input_dir: Path) -> list[Path]:
    """Localiza os arquivos .FAC que serão convertidos."""

    files = []

    for path in paths:
        if path.is_dir():
            files.extend(
                item
                for item in path.iterdir()
                if item.is_file() and item.suffix.lower() == ".fac"
            )

        elif path.is_file():
            files.append(path)

        else:
            print(f"[ERRO] Caminho não encontrado: {path}")

    if not files:
        files = list(input_dir.glob("*.fac"))

    return files

def create_output_dir(output_dir: Path) -> None:
    """Garante que a pasta de saída exista."""
    output_dir.mkdir(parents=True, exist_ok=True)

def get_output_path(
    fac_path: Path,
    output_dir: Path,
    extension: str
) -> Path:
    """Monta o caminho do arquivo convertido."""
    return output_dir / (fac_path.stem + extension)