"""Spike T0-06: so sánh `pypdf` và `pdfplumber` khi trích xuất văn bản PDF theo trang.

    python evaluation/spikes/extract.py --corpus evaluation/spikes/corpus [--real-dir /duong/dan/pdf-that]

Đo trên mỗi thư viện:
- tỷ lệ trang có văn bản (≥ MIN_TEXT_CHARS ký tự);
- độ giống văn bản gốc (chỉ với bộ tổng hợp có `ground_truth.json`), sau chuẩn hóa NFC và khoảng trắng;
- giữ dấu tiếng Việt: tỷ lệ ký tự có dấu của văn bản gốc còn nguyên trong văn bản trích xuất;
- bảng: tỷ lệ dòng của bảng giá còn nằm trên một dòng, đúng thứ tự cột;
- bố cục hai cột: hai câu chứa sự kiện của hai cột có còn liền mạch (không bị trộn cột) hay không;
- thời gian trích xuất mỗi trang.
`--real-dir` chạy thêm trên thư mục PDF thật (DEP-001) — chỉ đo các chỉ số không cần đáp án.
"""

from __future__ import annotations

import argparse
import difflib
import io
import json
import re
import statistics
import time
import unicodedata
from collections.abc import Callable
from pathlib import Path

import pdfplumber
from pypdf import PdfReader

MIN_TEXT_CHARS = 20
VI_DIACRITICS = set(
    unicodedata.normalize(
        "NFC",
        "àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ"
        "ÀÁẠẢÃÂẦẤẬẨẪĂẰẮẶẲẴÈÉẸẺẼÊỀẾỆỂỄÌÍỊỈĨÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠÙÚỤỦŨƯỪỨỰỬỮỲÝỴỶỸĐ",
    )
)


def squash(text: str) -> str:
    return re.sub(r"\s+", " ", unicodedata.normalize("NFC", text)).strip()


def extract_pypdf(data: bytes) -> list[str]:
    reader = PdfReader(io.BytesIO(data))
    if reader.is_encrypted and not reader.decrypt(""):
        raise PermissionError("encrypted")
    return [page.extract_text() or "" for page in reader.pages]


def extract_pdfplumber(data: bytes) -> list[str]:
    with pdfplumber.open(io.BytesIO(data)) as pdf:
        return [page.extract_text() or "" for page in pdf.pages]


LIBRARIES: dict[str, Callable[[bytes], list[str]]] = {"pypdf": extract_pypdf, "pdfplumber": extract_pdfplumber}


def diacritic_recall(truth: str, got: str) -> float | None:
    want = [c for c in unicodedata.normalize("NFC", truth) if c in VI_DIACRITICS]
    if not want:
        return None
    have = list(unicodedata.normalize("NFC", got))
    pool: dict[str, int] = {}
    for c in have:
        pool[c] = pool.get(c, 0) + 1
    hit = 0
    for c in want:
        if pool.get(c, 0) > 0:
            pool[c] -= 1
            hit += 1
    return hit / len(want)


def run(corpus: Path, real_dir: Path | None) -> dict:  # type: ignore[type-arg]
    truth = json.loads((corpus / "ground_truth.json").read_text(encoding="utf-8"))
    docs = {d["file_name"]: d for d in truth["documents"]}
    facts = truth["facts"]
    files = sorted(corpus.glob("*.pdf")) + (sorted(real_dir.glob("*.pdf")) if real_dir else [])
    results: dict[str, dict] = {}  # type: ignore[type-arg]
    for lib, fn in LIBRARIES.items():
        pages_total = pages_text = 0
        similarities: list[float] = []
        diacritics: list[float] = []
        per_page_ms: list[float] = []
        errors: dict[str, str] = {}
        table_rows_ok = table_rows = 0
        columns_ok = columns_total = 0
        for path in files:
            data = path.read_bytes()
            started = time.perf_counter()
            try:
                pages = fn(data)
            except Exception as exc:  # thư viện báo lỗi: ghi loại lỗi
                errors[path.name] = type(exc).__name__
                continue
            elapsed = (time.perf_counter() - started) * 1000
            if pages:
                per_page_ms.append(elapsed / len(pages))
            pages_total += len(pages)
            pages_text += sum(len(squash(p)) >= MIN_TEXT_CHARS for p in pages)
            info = docs.get(path.name)
            if not info or not info["pages"]:
                continue
            joined = squash("\n".join(pages))
            for i, truth_page in enumerate(info["pages"]):
                if i < len(pages):
                    similarities.append(difflib.SequenceMatcher(None, squash(truth_page), squash(pages[i])).ratio())
                    rec = diacritic_recall(truth_page, pages[i])
                    if rec is not None:
                        diacritics.append(rec)
            if info["kind"] == "quote":
                lines = [squash(line) for p in pages for line in p.splitlines()]
                for f in (f for f in facts if f["document"] == path.name and f["key"] == "tier_price"):
                    table_rows += 1
                    tier, price = f["extra"]["tier"], f["value"].split()[0]
                    pattern = re.compile(rf"Gói {re.escape(tier)}\s+{price}\b")
                    table_rows_ok += any(pattern.search(line) for line in lines)
            if info["kind"] == "proposal":
                for f in (f for f in facts if f["document"] == path.name):
                    columns_total += 1
                    columns_ok += squash(f["sentence"]) in joined
        results[lib] = {
            "files": len(files),
            "files_failed": errors,
            "pages": pages_total,
            "pages_with_text_ratio": round(pages_text / pages_total, 4) if pages_total else None,
            "text_similarity_mean": round(statistics.mean(similarities), 4) if similarities else None,
            "text_similarity_min": round(min(similarities), 4) if similarities else None,
            "diacritic_recall_mean": round(statistics.mean(diacritics), 4) if diacritics else None,
            "table_rows_intact": f"{table_rows_ok}/{table_rows}",
            "two_column_sentences_intact": f"{columns_ok}/{columns_total}",
            "ms_per_page_median": round(statistics.median(per_page_ms), 1) if per_page_ms else None,
        }
    return results


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--corpus", type=Path, default=Path("evaluation/spikes/corpus"))
    parser.add_argument("--real-dir", type=Path)
    parser.add_argument("--out", type=Path, default=Path("evaluation/spikes/results/extract.json"))
    args = parser.parse_args()
    results = run(args.corpus, args.real_dir)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
