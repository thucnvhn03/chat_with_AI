"""Spike T0-07: embedding và truy xuất tiếng Việt.

    python evaluation/spikes/retrieval.py --corpus evaluation/spikes/corpus \
        --models BAAI/bge-m3 intfloat/multilingual-e5-small --chunk-tokens 400 500 600

Với mỗi mô hình × kích thước chunk: trích xuất bằng mô-đun của ứng dụng (pypdf), cắt chunk theo trang bằng
bộ đếm token của chính mô hình, nhúng chunk và câu hỏi, đo tỷ lệ câu hỏi có chunk đúng (đúng tài liệu và
trang) trong top-K (K = 4, 8, 12), MRR, số chiều vector và thời gian nhúng mỗi chunk (CPU).
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.modules.ingestion.chunking import chunk_pages  # noqa: E402
from app.modules.ingestion.extract import ExtractionError, extract_pages  # noqa: E402
from questions import in_scope_questions, load_truth  # noqa: E402

# Mô hình họ E5 cần tiền tố phân biệt câu hỏi và đoạn văn
PREFIXES = {"intfloat/": ("query: ", "passage: ")}
KS = (4, 8, 12)


def prefixes(model_name: str) -> tuple[str, str]:
    for key, value in PREFIXES.items():
        if model_name.startswith(key):
            return value
    return "", ""


def evaluate_model(model_name: str, corpus: Path, chunk_sizes: list[int], overlap: int) -> list[dict[str, Any]]:
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer(model_name, device="cpu")
    q_prefix, p_prefix = prefixes(model_name)

    def count_tokens(texts: list[str]) -> list[int]:
        return [len(ids) for ids in model.tokenizer(texts, add_special_tokens=False)["input_ids"]]

    truth = load_truth(corpus)
    questions = in_scope_questions(truth) + in_scope_questions(truth, variant=1)
    # bỏ trùng câu hỏi (mẫu chỉ có một biến thể)
    seen: set[str] = set()
    questions = [q for q in questions if not (q.question in seen or seen.add(q.question))]
    q_vectors = model.encode([q_prefix + q.question for q in questions], normalize_embeddings=True, batch_size=32)

    documents: dict[str, list[Any]] = {}
    for path in sorted(corpus.glob("*.pdf")):
        try:
            documents[path.name] = extract_pages(path.read_bytes(), 20)
        except ExtractionError:
            continue

    results = []
    for size in chunk_sizes:
        chunk_meta: list[tuple[str, int]] = []
        texts: list[str] = []
        for name, pages in documents.items():
            for c in chunk_pages(pages, count_tokens, size, min(overlap, size - 1)):
                chunk_meta.append((name, c.page))
                texts.append(c.text)
        started = time.perf_counter()
        c_vectors = model.encode([p_prefix + t for t in texts], normalize_embeddings=True, batch_size=16)
        per_chunk_ms = (time.perf_counter() - started) * 1000 / len(texts)
        scores = np.asarray(q_vectors) @ np.asarray(c_vectors).T
        hits = {k: 0 for k in KS}
        reciprocal = 0.0
        top1_scores, wrong_top1 = [], []
        for qi, q in enumerate(questions):
            want = (q.expected_sources[0]["document"], q.expected_sources[0]["page"])
            order = np.argsort(-scores[qi])
            ranks = [r for r, ci in enumerate(order[:50]) if chunk_meta[ci] == want]
            first = ranks[0] + 1 if ranks else None
            if first:
                reciprocal += 1 / first
            for k in KS:
                hits[k] += bool(first and first <= k)
            top1_scores.append(float(scores[qi][order[0]]))
            if first != 1:
                wrong_top1.append(q.id)
        results.append(
            {
                "model": model_name,
                "dimension": int(np.asarray(c_vectors).shape[1]),
                "chunk_tokens": size,
                "chunks": len(texts),
                "questions": len(questions),
                **{f"recall@{k}": round(hits[k] / len(questions), 4) for k in KS},
                "mrr": round(reciprocal / len(questions), 4),
                "ms_per_chunk_cpu": round(per_chunk_ms, 1),
                "top1_score_median": round(float(np.median(top1_scores)), 4),
            }
        )
        print(json.dumps(results[-1], ensure_ascii=False), flush=True)
    return results


def out_of_scope_scores(model_name: str, corpus: Path, size: int) -> dict[str, float]:
    """Điểm cao nhất của câu hỏi ngoài phạm vi so với câu trong phạm vi — gợi ý MIN_RELEVANCE_SCORE ban đầu."""
    from questions import out_of_scope_questions
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer(model_name, device="cpu")
    q_prefix, p_prefix = prefixes(model_name)

    def count_tokens(texts: list[str]) -> list[int]:
        return [len(ids) for ids in model.tokenizer(texts, add_special_tokens=False)["input_ids"]]

    texts = []
    for path in sorted(corpus.glob("*.pdf")):
        try:
            pages = extract_pages(path.read_bytes(), 20)
        except ExtractionError:
            continue
        texts += [c.text for c in chunk_pages(pages, count_tokens, size, 80)]
    c_vectors = np.asarray(model.encode([p_prefix + t for t in texts], normalize_embeddings=True, batch_size=16))
    truth = load_truth(corpus)

    def top(questions: list[str]) -> list[float]:
        v = np.asarray(model.encode([q_prefix + q for q in questions], normalize_embeddings=True))
        return [float(x) for x in (v @ c_vectors.T).max(axis=1)]

    inside = top([q.question for q in in_scope_questions(truth)])
    outside = top([q.question for q in out_of_scope_questions()])
    return {
        "in_scope_top_score_min": round(min(inside), 4),
        "in_scope_top_score_p10": round(float(np.percentile(inside, 10)), 4),
        "out_of_scope_top_score_max": round(max(outside), 4),
        "out_of_scope_top_score_median": round(float(np.median(outside)), 4),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--corpus", type=Path, default=Path("evaluation/spikes/corpus"))
    parser.add_argument("--models", nargs="+", default=["BAAI/bge-m3", "intfloat/multilingual-e5-small"])
    parser.add_argument("--chunk-tokens", nargs="+", type=int, default=[400, 500, 600])
    parser.add_argument("--overlap", type=int, default=80)
    parser.add_argument("--out", type=Path, default=Path("evaluation/spikes/results/retrieval.json"))
    args = parser.parse_args()
    all_results: dict[str, Any] = {"runs": [], "thresholds": {}}
    for model in args.models:
        all_results["runs"] += evaluate_model(model, args.corpus, args.chunk_tokens, args.overlap)
        all_results["thresholds"][model] = out_of_scope_scores(model, args.corpus, 500)
        print(json.dumps({model: all_results["thresholds"][model]}, ensure_ascii=False), flush=True)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(all_results, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
