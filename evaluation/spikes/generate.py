"""Spike T0-08: sinh câu trả lời có trích dẫn với Claude trên dữ liệu KHÔNG nhạy cảm (bộ PDF tổng hợp).

    ANTHROPIC_API_KEY=... python evaluation/spikes/generate.py --corpus evaluation/spikes/corpus

Kiểm tra:
  (a) citation trỏ đúng chunk (`document_index` → tài liệu, trang mong đợi);
  (b) câu hỏi ngoài phạm vi có nhận câu từ chối cố định không;
  (c) `effort` "low" so với "medium": tỷ lệ đúng nguồn, độ trễ, số token đầu ra;
  (d) `usage.cache_read_input_tokens` ở lượt thứ hai (chỉ dẫn hệ thống có `cache_control`; nếu chỉ dẫn ngắn
      hơn ngưỡng tối thiểu của bộ nhớ đệm thì luôn bằng 0 — không phải lỗi).
Ghi chi phí ước tính mỗi câu hỏi (đầu vào RSK-005). Đơn giá đọc từ tham số dòng lệnh để cập nhật khi đổi.
Dùng đúng chỉ dẫn hệ thống, cách dựng khối `document` và cách đọc phản hồi của adapter thật.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.adapters.claude_llm import FALLBACK_BETA, SYSTEM_PROMPT, build_documents, parse_response  # noqa: E402
from app.adapters.hash_embedding import HashEmbeddingProvider  # noqa: E402
from app.modules.ingestion.chunking import chunk_pages  # noqa: E402
from app.modules.ingestion.extract import ExtractionError, extract_pages  # noqa: E402
from app.modules.qa.service import is_not_found_sentence  # noqa: E402
from app.ports.ai import SourceChunk  # noqa: E402
from questions import in_scope_questions, load_truth, out_of_scope_questions  # noqa: E402


def corpus_chunks(corpus: Path) -> list[SourceChunk]:
    counter = HashEmbeddingProvider(8).count_tokens
    chunks: list[SourceChunk] = []
    for path in sorted(corpus.glob("*.pdf")):
        try:
            pages = extract_pages(path.read_bytes(), 20)
        except ExtractionError:
            continue
        for c in chunk_pages(pages, counter, 500, 80):
            chunks.append(SourceChunk(f"{path.name}#{c.ordinal}", path.name, c.page, c.text))
    return chunks


def candidates(chunks: list[SourceChunk], question: str, k: int) -> list[SourceChunk]:
    """Truy xuất đơn giản theo từ chung (đủ cho spike sinh câu trả lời; spike T0-07 đo truy xuất thật)."""
    q = set(question.lower().split())
    return sorted(chunks, key=lambda c: -len(q & set(c.text.lower().split())))[:k]


def call(client: Any, model: str, effort: str, question: str, sources: list[SourceChunk]) -> tuple[Any, float]:
    started = time.perf_counter()
    response = client.beta.messages.create(
        model=model,
        max_tokens=16000,
        betas=[FALLBACK_BETA],
        fallbacks="default",
        output_config={"effort": effort},
        system=[{"type": "text", "text": SYSTEM_PROMPT, "cache_control": {"type": "ephemeral"}}],
        messages=[{"role": "user", "content": [*build_documents(sources), {"type": "text", "text": question}]}],
    )
    return response, time.perf_counter() - started


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--corpus", type=Path, default=Path("evaluation/spikes/corpus"))
    parser.add_argument("--model", default="claude-opus-5-5")
    parser.add_argument("--efforts", nargs="+", default=["low", "medium"])
    parser.add_argument("--questions", type=int, default=12)
    parser.add_argument("--top-k", type=int, default=8)
    parser.add_argument("--price-input", type=float, default=4.0, help="USD / 1 triệu token đầu vào")
    parser.add_argument("--price-output", type=float, default=20.0, help="USD / 1 triệu token đầu ra")
    parser.add_argument("--price-cache-read", type=float, default=0.20)
    parser.add_argument("--out", type=Path, default=Path("evaluation/spikes/results/generation.json"))
    args = parser.parse_args()

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("Thiếu ANTHROPIC_API_KEY: spike T0-08 cần khóa API (không commit khóa).", file=sys.stderr)
        return 2
    import anthropic

    client = anthropic.Anthropic(max_retries=2, timeout=120)
    truth = load_truth(args.corpus)
    chunks = corpus_chunks(args.corpus)
    in_scope = in_scope_questions(truth)[: args.questions]
    out_scope = out_of_scope_questions()[: max(3, args.questions // 3)]

    summary: dict[str, Any] = {"model": args.model, "efforts": {}}
    for effort in args.efforts:
        rows = []
        for q in in_scope + out_scope:
            sources = candidates(chunks, q.question, args.top_k)
            response, seconds = call(client, args.model, effort, q.question, sources)
            answer = parse_response(response)
            usage = response.usage
            cost = (
                (usage.input_tokens or 0) * args.price_input
                + (usage.output_tokens or 0) * args.price_output
                + (getattr(usage, "cache_read_input_tokens", 0) or 0) * args.price_cache_read
            ) / 1_000_000
            cited = [(sources[i].document_name, sources[i].page) for i, _ in answer.citations if 0 <= i < len(sources)]
            expected = {(s["document"], s["page"]) for s in q.expected_sources}
            rows.append(
                {
                    "id": q.id,
                    "type": q.type,
                    "refused": answer.refused,
                    "not_found_sentence": is_not_found_sentence(answer.text),
                    "citations": cited,
                    "citation_correct": bool(expected & set(cited)) if expected else None,
                    "seconds": round(seconds, 2),
                    "output_tokens": usage.output_tokens,
                    "cache_read_input_tokens": getattr(usage, "cache_read_input_tokens", None),
                    "cost_usd": round(cost, 5),
                }
            )
            print(json.dumps(rows[-1], ensure_ascii=False), flush=True)
        ins = [r for r in rows if r["type"] == "in_scope"]
        outs = [r for r in rows if r["type"] == "out_of_scope"]
        summary["efforts"][effort] = {
            "citation_correct_ratio": sum(bool(r["citation_correct"]) for r in ins) / len(ins),
            "out_of_scope_refusal_sentence_ratio": sum(r["not_found_sentence"] for r in outs) / len(outs),
            "median_seconds": sorted(r["seconds"] for r in rows)[len(rows) // 2],
            "mean_cost_usd": sum(r["cost_usd"] for r in rows) / len(rows),
            "cache_read_after_first": any((r["cache_read_input_tokens"] or 0) > 0 for r in rows[1:]),
            "rows": rows,
        }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {k: {kk: vv for kk, vv in v.items() if kk != "rows"} for k, v in summary["efforts"].items()},
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
