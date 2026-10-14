from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
import warnings


@dataclass(frozen=True)
class Note:
    name: str
    content: str


def _read_single_file(path: Path) -> tuple[Path, Note | Exception]:
    try:
        raw_content = path.read_bytes()
        content = _decode_content(raw_content)
        return path, Note(name=path.name, content=content)
    except (UnicodeDecodeError, OSError, ValueError) as exc:
        return path, exc


def read_notes(folder_path: str | Path) -> list[Note]:
    source = Path(folder_path)

    if not source.exists():
        raise FileNotFoundError(f"Kaynak klasor bulunamadi: {source}")

    if not source.is_dir():
        raise NotADirectoryError(f"Kaynak yol bir klasor degil: {source}")

    candidates = sorted(
        [
            path
            for path in source.iterdir()
            if path.is_file() and path.suffix.lower() in {".md", ".txt"}
        ],
        key=lambda path: path.name.casefold(),
    )

    if not candidates:
        raise ValueError(f"Klasorde .md veya .txt dosyasi bulunamadi: {source}")

    if len(candidates) == 1:
        path, result = _read_single_file(candidates[0])
        if isinstance(result, Exception):
            warnings.warn(
                f"Dosya okunamadi, atlandi: {path.name} ({result})",
                category=UserWarning,
                stacklevel=2,
            )
            return []
        return [result]

    notes: list[Note] = []
    max_workers = min(16, len(candidates))
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(_read_single_file, candidates))

    for path, result in results:
        if isinstance(result, Exception):
            warnings.warn(
                f"Dosya okunamadi, atlandi: {path.name} ({result})",
                category=UserWarning,
                stacklevel=2,
            )
            continue
        notes.append(result)

    return notes


def _decode_content(raw_content: bytes) -> str:
    for encoding in ("utf-8", "cp1254"):
        try:
            content = raw_content.decode(encoding)
        except UnicodeDecodeError:
            continue

        if "\x00" in content:
            raise ValueError("dosya ikili veya bozuk gorunuyor")
        return content

    raise UnicodeDecodeError(
        "supported encodings",
        raw_content,
        0,
        min(len(raw_content), 1),
        "UTF-8 veya Windows-1254 olarak cozumlenemedi",
    )