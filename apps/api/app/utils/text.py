import math
import re
from collections import Counter


def slugify_filename(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "-", value).strip("-")
    return cleaned[:200] or "document.txt"


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 100) -> list[str]:
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(len(text), start + chunk_size)
        chunks.append(text[start:end])
        start = end if end == len(text) else max(0, end - overlap)
    return chunks


def simple_embedding(text: str) -> list[float]:
    counts = Counter(token.lower() for token in re.findall(r"[A-Za-z0-9_]+", text))
    vector = [0.0] * 12
    for idx, (token, value) in enumerate(sorted(counts.items())[:12]):
        vector[idx] = float((len(token) * value) % 11) / 10.0
    return vector


def cosine_similarity(left: list[float], right: list[float]) -> float:
    if not left or not right:
        return 0.0
    dot = sum(a * b for a, b in zip(left, right, strict=False))
    left_norm = math.sqrt(sum(a * a for a in left))
    right_norm = math.sqrt(sum(b * b for b in right))
    if not left_norm or not right_norm:
        return 0.0
    return dot / (left_norm * right_norm)
