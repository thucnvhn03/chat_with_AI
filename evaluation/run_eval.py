"""Bộ đánh giá chất lượng hỏi đáp (M-12, US-016; implement_plan.md mục 9.4).

Đọc bộ câu hỏi chuẩn `datasets/*.jsonl`, gọi một hàm hỏi trừu tượng `ask(question, history)`, tính các
chỉ số và ghi báo cáo JSON + Markdown.

    # Chạy thử không cần AI thật (bộ gọi giả trả lời theo đáp án mẫu)
    python evaluation/run_eval.py --dataset evaluation/datasets/sample.jsonl --fake --out evaluation/reports

    # Chạy với hệ thống thật qua API (cần tài khoản BD đã có tài liệu của bộ câu hỏi)
    EVAL_LOGIN=... EVAL_PASSWORD=... python evaluation/run_eval.py \
        --dataset evaluation/datasets/v1.jsonl --api http://localhost:8000 --out evaluation/reports

Chỉ số (mục 9.4):
- MET-002 "đúng và có nguồn": câu `in_scope` trả lời đúng VÀ có ≥ 1 nguồn khớp `expected_sources`.
- Tỷ lệ bịa: câu `out_of_scope` nhận câu trả lời có nội dung (không phải "không tìm thấy").
- Độ phủ nguồn: câu `multi_doc` có nguồn từ TẤT CẢ tài liệu mong đợi.
- Đúng trang: citation có `cited_text` nằm trong trang được nêu ÷ tổng citation kiểm tra được.
- Độ trễ: phân vị thời gian phản hồi.
- Câu hỏi tiếp theo (`follow_up`, AC-008): tỷ lệ trả lời đúng.

Chấm "đúng" mặc định bằng từ khóa (`expected_keywords`, nếu không có thì độ phủ từ của `expected_answer`).
Kết quả chấm tự động phải được đối chiếu với chấm tay trên một mẫu ngẫu nhiên (xuất bằng --review-sample)
trước khi dùng cho cổng launch.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import random
import re
import subprocess
import sys
import time
import unicodedata
from collections.abc import Callable, Iterable
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Protocol

QUESTION_TYPES = ("in_scope", "out_of_scope", "multi_doc", "follow_up")
NOT_FOUND_SENTENCE = "Không tìm thấy thông tin này trong các tài liệu đã tải lên."


# ----------------------------------------------------------------------------- dữ liệu


@dataclass
class ExpectedSource:
    document: str
    page: int | None = None


@dataclass
class Question:
    id: str
    type: str
    question: str
    lang: str = "vi"
    expected_answer: str | None = None
    expected_keywords: list[str] = field(default_factory=list)
    expected_sources: list[ExpectedSource] = field(default_factory=list)
    history: list[str] = field(default_factory=list)


@dataclass
class Citation:
    document: str
    page: int
    cited_text: str | None = None
    # True/False khi đã kiểm tra đoạn trích có trong trang; None khi không kiểm tra được
    in_page: bool | None = None


@dataclass
class Answer:
    text: str
    not_found: bool
    citations: list[Citation]
    latency_ms: float
    error: str | None = None


class Asker(Protocol):
    def ask(self, question: str, history: list[str]) -> Answer: ...


def load_dataset(path: Path) -> list[Question]:
    questions: list[Question] = []
    seen: set[str] = set()
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip() or line.lstrip().startswith("//"):
            continue
        raw = json.loads(line)
        q = Question(
            id=str(raw["id"]),
            type=raw["type"],
            question=raw["question"],
            lang=raw.get("lang", "vi"),
            expected_answer=raw.get("expected_answer"),
            expected_keywords=list(raw.get("expected_keywords", [])),
            expected_sources=[ExpectedSource(s["document"], s.get("page")) for s in raw.get("expected_sources", [])],
            history=list(raw.get("history", [])),
        )
        if q.type not in QUESTION_TYPES:
            raise ValueError(f"{path}:{line_no}: loại câu hỏi không hợp lệ: {q.type}")
        if q.id in seen:
            raise ValueError(f"{path}:{line_no}: trùng id {q.id}")
        seen.add(q.id)
        questions.append(q)
    return questions


# ----------------------------------------------------------------------------- chấm điểm


_WORD = re.compile(r"\w+", re.UNICODE)
# Từ phổ biến không mang thông tin (bỏ khi đo độ phủ đáp án)
_STOPWORDS = frozenset(
    [
        "là",
        "của",
        "và",
        "có",
        "các",
        "những",
        "được",
        "cho",
        "trong",
        "với",
        "này",
        "đó",
        "thì",
        "mà",
        "một",
        "không",
        "theo",
        "về",
        "từ",
        "khi",
        "để",
        "đã",
        "sẽ",
        "the",
        "a",
        "an",
        "of",
        "and",
        "or",
        "to",
        "is",
        "are",
        "in",
        "on",
        "for",
        "by",
        "with",
    ]
)


def normalize(text: str) -> str:
    return unicodedata.normalize("NFC", text).lower()


def content_words(text: str) -> set[str]:
    return {w for w in _WORD.findall(normalize(text)) if w not in _STOPWORDS}


def is_correct(question: Question, answer: Answer, overlap_threshold: float = 0.6) -> bool:
    """Chấm tự động: mọi từ khóa xuất hiện, hoặc ≥ ngưỡng từ nội dung của đáp án mẫu có trong câu trả lời."""
    if answer.not_found or answer.error:
        return False
    text = normalize(answer.text)
    if question.expected_keywords:
        return all(normalize(k) in text for k in question.expected_keywords)
    if not question.expected_answer:
        return False
    expected = content_words(question.expected_answer)
    if not expected:
        return False
    return len(expected & content_words(answer.text)) / len(expected) >= overlap_threshold


def source_matches(expected: ExpectedSource, citation: Citation) -> bool:
    same_doc = normalize(expected.document) == normalize(citation.document)
    return same_doc and (expected.page is None or expected.page == citation.page)


def has_expected_source(question: Question, answer: Answer) -> bool:
    return any(source_matches(e, c) for e in question.expected_sources for c in answer.citations)


def covers_all_documents(question: Question, answer: Answer) -> bool:
    expected = {normalize(s.document) for s in question.expected_sources}
    cited = {normalize(c.document) for c in answer.citations}
    return bool(expected) and expected <= cited


def percentile(values: list[float], p: float) -> float | None:
    """Phân vị theo phương pháp nội suy tuyến tính (giống numpy mặc định)."""
    if not values:
        return None
    ordered = sorted(values)
    k = (len(ordered) - 1) * p / 100
    lo, hi = math.floor(k), math.ceil(k)
    if lo == hi:
        return ordered[lo]
    return ordered[lo] + (ordered[hi] - ordered[lo]) * (k - lo)


def ratio(numerator: int, denominator: int) -> float | None:
    return round(numerator / denominator, 4) if denominator else None


@dataclass
class Row:
    question: Question
    answer: Answer
    correct: bool
    source_ok: bool
    covers_all: bool


def compute_metrics(rows: list[Row]) -> dict[str, Any]:
    def of(kind: str) -> list[Row]:
        return [r for r in rows if r.question.type == kind]

    in_scope, out_scope, multi, follow = of("in_scope"), of("out_of_scope"), of("multi_doc"), of("follow_up")
    citations = [c for r in rows for c in r.answer.citations if c.in_page is not None]
    latencies = [r.answer.latency_ms for r in rows if r.answer.error is None]
    answered_with_content = [r for r in rows if not r.answer.not_found and not r.answer.error]
    return {
        "counts": {
            "total": len(rows),
            **{k: len(of(k)) for k in QUESTION_TYPES},
            "errors": sum(1 for r in rows if r.answer.error),
        },
        "correct_with_source": ratio(sum(r.correct and r.source_ok for r in in_scope), len(in_scope)),
        "correct_only": ratio(sum(r.correct for r in in_scope), len(in_scope)),
        "hallucination_rate": ratio(
            sum(not r.answer.not_found and not r.answer.error for r in out_scope), len(out_scope)
        ),
        "source_coverage": ratio(sum(r.covers_all for r in multi), len(multi)),
        "follow_up_correct": ratio(sum(r.correct for r in follow), len(follow)),
        "correct_page": ratio(sum(bool(c.in_page) for c in citations), len(citations)),
        "citations_checked": len(citations),
        # BR-012: mọi câu trả lời có nội dung phải có ít nhất một nguồn
        "answers_with_content_having_source": ratio(
            sum(bool(r.answer.citations) for r in answered_with_content), len(answered_with_content)
        ),
        "latency_ms": {
            "p50": percentile(latencies, 50),
            "p90": percentile(latencies, 90),
            "p95": percentile(latencies, 95),
            "max": max(latencies) if latencies else None,
        },
    }


def evaluate(
    questions: list[Question],
    asker: Asker,
    grader: Callable[[Question, Answer], bool] = is_correct,
    progress: Callable[[int, int], None] | None = None,
) -> list[Row]:
    rows: list[Row] = []
    for i, q in enumerate(questions, start=1):
        answer = asker.ask(q.question, q.history)
        rows.append(
            Row(
                question=q,
                answer=answer,
                correct=grader(q, answer),
                source_ok=has_expected_source(q, answer),
                covers_all=covers_all_documents(q, answer),
            )
        )
        if progress:
            progress(i, len(questions))
    return rows


def metrics_by_language(rows: list[Row]) -> dict[str, dict[str, Any]]:
    langs = sorted({r.question.lang for r in rows})
    return {lang: compute_metrics([r for r in rows if r.question.lang == lang]) for lang in langs}


# ----------------------------------------------------------------------------- bộ gọi


class FakeAsker:
    """Bộ gọi giả để chạy thử khung đánh giá: trả lời đúng theo dữ liệu mẫu, từ chối câu ngoài phạm vi.

    `wrong_ids` cho phép giả lập câu trả lời sai / bịa để kiểm thử công thức chỉ số.
    """

    def __init__(self, questions: Iterable[Question], wrong_ids: Iterable[str] = ()) -> None:
        self._by_text = {q.question: q for q in questions}
        self._wrong = set(wrong_ids)

    def ask(self, question: str, history: list[str]) -> Answer:
        q = self._by_text[question]
        latency = 100.0 + 10 * len(question)
        if q.id in self._wrong:
            if q.type == "out_of_scope":
                return Answer("Một câu trả lời bịa.", False, [Citation("Bia.pdf", 1, "bịa", False)], latency)
            return Answer("Câu trả lời sai.", False, [Citation("Khac.pdf", 99, "sai", False)], latency)
        if q.type == "out_of_scope":
            return Answer(NOT_FOUND_SENTENCE, True, [], latency)
        text = q.expected_answer or " ".join(q.expected_keywords)
        cites = [Citation(s.document, s.page or 1, text, True) for s in q.expected_sources]
        return Answer(text, False, cites, latency)


class ApiAsker:
    """Gọi hệ thống thật qua API: đăng nhập bằng tài khoản BD, mỗi câu hỏi một hội thoại mới; câu hỏi
    `follow_up` được hỏi sau các câu trong `history` trong cùng hội thoại. Kiểm tra đúng trang bằng cách
    đọc văn bản trang qua GET /documents/{id}/pages/{page}."""

    def __init__(self, base_url: str, login: str, password: str, timeout_s: float = 120) -> None:
        import httpx

        self._base = base_url.rstrip("/")
        origin = os.environ.get("EVAL_ORIGIN", "http://localhost:5173")
        self._http = httpx.Client(base_url=f"{self._base}/api/v1", timeout=timeout_s, headers={"Origin": origin})
        response = self._http.post("/auth/login", json={"login": login, "password": password})
        response.raise_for_status()
        self._page_cache: dict[tuple[str, int], str | None] = {}

    def _page_text(self, document_id: str, page: int) -> str | None:
        key = (document_id, page)
        if key not in self._page_cache:
            r = self._http.get(f"/documents/{document_id}/pages/{page}")
            self._page_cache[key] = r.json()["text"] if r.status_code == 200 else None
        return self._page_cache[key]

    def _ask_once(self, conversation: str, question: str) -> tuple[Any, float]:
        started = time.perf_counter()
        r = self._http.post(f"/conversations/{conversation}/messages", json={"question": question})
        elapsed = (time.perf_counter() - started) * 1000
        return r, elapsed

    def ask(self, question: str, history: list[str]) -> Answer:
        conversation = self._http.post("/conversations").json()["id"]
        for previous in history:
            self._ask_once(conversation, previous)
        response, elapsed = self._ask_once(conversation, question)
        if response.status_code != 200:
            code = response.json().get("error", {}).get("code", str(response.status_code))
            return Answer("", False, [], elapsed, error=code)
        body = response.json()
        citations = []
        for c in body["citations"]:
            page_text = self._page_text(c["document_id"], c["page"])
            cited = c.get("cited_text")
            in_page = None
            if page_text is not None and cited:
                in_page = _squash(cited) in _squash(page_text)
            citations.append(Citation(c["document_name"], c["page"], cited, in_page))
        return Answer(body["answer"], body["not_found"], citations, elapsed)


def _squash(text: str) -> str:
    return re.sub(r"\s+", " ", unicodedata.normalize("NFC", text)).strip()


# ----------------------------------------------------------------------------- báo cáo


def git_revision() -> str | None:
    try:
        return subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, check=True
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def fmt(value: Any, percent: bool = True) -> str:
    if value is None:
        return "—"
    if percent:
        return f"{value * 100:.1f}%"
    return f"{value:.0f}"


def render_markdown(report: dict[str, Any]) -> str:
    m = report["metrics"]
    lat = m["latency_ms"]
    lines = [
        f"# Báo cáo đánh giá — {report['dataset']}",
        "",
        f"- Thời điểm: {report['generated_at']}",
        f"- Phiên bản mã: {report.get('git_revision') or 'không rõ'}",
        f"- Bộ gọi: {report['asker']}",
        f"- Ghi chú cấu hình: {report.get('config_note') or '—'}",
        f"- Số câu: {m['counts']['total']} (lỗi gọi: {m['counts']['errors']})",
        "",
        "| Chỉ số | Giá trị | Số câu | Tiêu chí |",
        "|---|---|---|---|",
        f"| Đúng và có nguồn (MET-002) | {fmt(m['correct_with_source'])} | {m['counts']['in_scope']} | ≥ [TBD: OQ-002] (LG-02) |",
        f"| Đúng (không xét nguồn) | {fmt(m['correct_only'])} | {m['counts']['in_scope']} | tham khảo |",
        f"| Tỷ lệ bịa | {fmt(m['hallucination_rate'])} | {m['counts']['out_of_scope']} | ≤ [TBD: OQ-002] (LG-03) |",
        f"| Độ phủ nguồn (nhiều tài liệu) | {fmt(m['source_coverage'])} | {m['counts']['multi_doc']} | báo cáo (AC-007) |",
        f"| Câu hỏi tiếp theo đúng | {fmt(m['follow_up_correct'])} | {m['counts']['follow_up']} | báo cáo (AC-008) |",
        f"| Đúng trang | {fmt(m['correct_page'])} | {m['citations_checked']} citation | 100% (LG-04) |",
        f"| Câu trả lời có nội dung có nguồn | {fmt(m['answers_with_content_having_source'])} | — | 100% (BR-012) |",
        f"| Độ trễ p50 / p90 / p95 (ms) | {fmt(lat['p50'], False)} / {fmt(lat['p90'], False)} / {fmt(lat['p95'], False)} | — | ≤ [TBD: OQ-002] (LG-05) |",
        "",
    ]
    if len(report["by_language"]) > 1:
        lines += ["## Theo ngôn ngữ", "", "| Ngôn ngữ | MET-002 | Tỷ lệ bịa | Đúng trang |", "|---|---|---|---|"]
        for lang, lm in report["by_language"].items():
            lines.append(
                f"| {lang} | {fmt(lm['correct_with_source'])} | {fmt(lm['hallucination_rate'])} | {fmt(lm['correct_page'])} |"
            )
        lines.append("")
    failures = [r for r in report["rows"] if not r["passed"]]
    lines += ["## Câu chưa đạt", ""]
    if not failures:
        lines.append("Không có.")
    for r in failures:
        lines.append(f"- `{r['id']}` ({r['type']}): {r['reason']}")
    lines.append("")
    return "\n".join(lines)


def row_summary(row: Row) -> dict[str, Any]:
    q, a = row.question, row.answer
    if q.type == "out_of_scope":
        passed, reason = a.not_found, "trả lời có nội dung cho câu ngoài phạm vi (bịa)"
    elif q.type == "multi_doc":
        passed, reason = row.covers_all, "thiếu nguồn từ một số tài liệu mong đợi"
    elif q.type == "follow_up":
        passed, reason = row.correct, "trả lời câu hỏi tiếp theo chưa đúng"
    else:
        passed = row.correct and row.source_ok
        reason = "sai nội dung" if not row.correct else "không có nguồn khớp tài liệu/trang mong đợi"
    if a.error:
        passed, reason = False, f"lỗi gọi: {a.error}"
    return {
        "id": q.id,
        "type": q.type,
        "lang": q.lang,
        "passed": passed,
        "reason": "" if passed else reason,
        "correct": row.correct,
        "source_ok": row.source_ok,
        "not_found": a.not_found,
        "latency_ms": round(a.latency_ms, 1),
        "citations": [asdict(c) for c in a.citations],
    }


def build_report(
    rows: list[Row], dataset: str, asker: str, config_note: str | None, cost_usd: float | None = None
) -> dict[str, Any]:
    return {
        "dataset": dataset,
        "asker": asker,
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "git_revision": git_revision(),
        "config_note": config_note,
        "cost_usd": cost_usd,
        "metrics": compute_metrics(rows),
        "by_language": metrics_by_language(rows),
        "rows": [row_summary(r) for r in rows],
    }


def write_review_sample(rows: list[Row], path: Path, fraction: float, seed: int) -> int:
    """Mẫu ngẫu nhiên để chấm tay, đối chiếu với chấm tự động (mục 9.4: 20%)."""
    candidates = [r for r in rows if r.question.type != "out_of_scope"]
    k = max(1, round(len(candidates) * fraction)) if candidates else 0
    sample = random.Random(seed).sample(candidates, k)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "question", "expected_answer", "answer", "auto_correct", "human_correct"])
        for r in sample:
            writer.writerow(
                [r.question.id, r.question.question, r.question.expected_answer or "", r.answer.text, r.correct, ""]
            )
    return k


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dataset", type=Path, required=True)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--fake", action="store_true", help="dùng bộ gọi giả (không cần AI thật)")
    source.add_argument("--api", help="địa chỉ backend, ví dụ http://localhost:8000")
    parser.add_argument("--out", type=Path, default=Path("evaluation/reports"))
    parser.add_argument("--config-note", help="mô tả cấu hình đang đánh giá (CHUNK_TOKENS, TOP_K...)")
    parser.add_argument("--cost-usd", type=float, help="chi phí gọi dịch vụ AI của lần chạy (RSK-005)")
    parser.add_argument("--review-sample", type=float, default=0.0, help="tỷ lệ câu xuất ra để chấm tay")
    parser.add_argument("--seed", type=int, default=7)
    args = parser.parse_args(argv)

    questions = load_dataset(args.dataset)
    if args.fake:
        asker: Asker = FakeAsker(questions)
        asker_name = "fake"
    else:
        login, password = os.environ.get("EVAL_LOGIN"), os.environ.get("EVAL_PASSWORD")
        if not login or not password:
            parser.error("cần biến môi trường EVAL_LOGIN và EVAL_PASSWORD")
        asker = ApiAsker(args.api, login, password)
        asker_name = f"api:{args.api}"

    def progress(i: int, n: int) -> None:
        print(f"\r{i}/{n}", end="", file=sys.stderr, flush=True)

    rows = evaluate(questions, asker, progress=progress)
    print(file=sys.stderr)
    report = build_report(rows, args.dataset.name, asker_name, args.config_note, args.cost_usd)

    args.out.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    base = args.out / f"{args.dataset.stem}-{stamp}"
    base.with_suffix(".json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    base.with_suffix(".md").write_text(render_markdown(report), encoding="utf-8")
    if args.review_sample > 0:
        n = write_review_sample(rows, base.with_name(base.name + "-review.csv"), args.review_sample, args.seed)
        print(f"Mẫu chấm tay: {n} câu", file=sys.stderr)
    print(render_markdown(report))
    print(f"Đã ghi {base}.json và {base}.md", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
