"""T0-09: kiểm thử đơn vị cho từng công thức chỉ số của bộ đánh giá."""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import run_eval as ev  # noqa: E402  (cần sys.path ở trên)

DATASET = Path(__file__).resolve().parents[1] / "datasets" / "sample.jsonl"


def q(qid: str, kind: str, **kw):  # type: ignore[no-untyped-def]
    return ev.Question(id=qid, type=kind, question=f"câu {qid}", **kw)


def row(question, answer):  # type: ignore[no-untyped-def]
    return ev.Row(
        question,
        answer,
        ev.is_correct(question, answer),
        ev.has_expected_source(question, answer),
        ev.covers_all_documents(question, answer),
    )


SRC_A = ev.ExpectedSource("A.pdf", 5)
SRC_B = ev.ExpectedSource("B.pdf", 2)


def test_correct_with_source_requires_both() -> None:
    qs = [q(f"q{i}", "in_scope", expected_keywords=["30 ngày"], expected_sources=[SRC_A]) for i in range(4)]
    rows = [
        row(qs[0], ev.Answer("Là 30 ngày.", False, [ev.Citation("A.pdf", 5)], 100)),  # đúng + nguồn
        row(qs[1], ev.Answer("Là 30 ngày.", False, [ev.Citation("A.pdf", 6)], 100)),  # đúng, sai trang
        row(qs[2], ev.Answer("Là 45 ngày.", False, [ev.Citation("A.pdf", 5)], 100)),  # sai nội dung
        row(qs[3], ev.Answer(ev.NOT_FOUND_SENTENCE, True, [], 100)),  # không tìm thấy
    ]
    m = ev.compute_metrics(rows)
    assert m["correct_with_source"] == 0.25
    assert m["correct_only"] == 0.5


def test_hallucination_rate() -> None:
    qs = [q(f"o{i}", "out_of_scope") for i in range(4)]
    rows = [
        row(qs[0], ev.Answer(ev.NOT_FOUND_SENTENCE, True, [], 1)),
        row(qs[1], ev.Answer(ev.NOT_FOUND_SENTENCE, True, [], 1)),
        row(qs[2], ev.Answer(ev.NOT_FOUND_SENTENCE, True, [], 1)),
        row(qs[3], ev.Answer("Canberra.", False, [], 1)),
    ]
    assert ev.compute_metrics(rows)["hallucination_rate"] == 0.25


def test_source_coverage_needs_all_expected_documents() -> None:
    qs = [q(f"m{i}", "multi_doc", expected_sources=[SRC_A, SRC_B]) for i in range(2)]
    rows = [
        row(qs[0], ev.Answer("x", False, [ev.Citation("A.pdf", 1), ev.Citation("b.PDF", 9)], 1)),
        row(qs[1], ev.Answer("x", False, [ev.Citation("A.pdf", 5)], 1)),
    ]
    assert ev.compute_metrics(rows)["source_coverage"] == 0.5


def test_correct_page_counts_only_checked_citations() -> None:
    question = q("p", "in_scope", expected_keywords=["x"])
    answer = ev.Answer(
        "x",
        False,
        [ev.Citation("A.pdf", 1, "a", True), ev.Citation("A.pdf", 2, "b", False), ev.Citation("A.pdf", 3, None, None)],
        1,
    )
    m = ev.compute_metrics([row(question, answer)])
    assert m["correct_page"] == 0.5 and m["citations_checked"] == 2


def test_latency_percentiles() -> None:
    question = q("l", "out_of_scope")
    rows = [row(question, ev.Answer("", True, [], ms)) for ms in [100, 200, 300, 400, 500]]
    lat = ev.compute_metrics(rows)["latency_ms"]
    assert lat["p50"] == 300 and lat["p90"] == pytest.approx(460) and lat["max"] == 500
    assert ev.percentile([], 50) is None


def test_errors_count_and_are_excluded_from_latency() -> None:
    question = q("e", "in_scope", expected_keywords=["x"])
    rows = [row(question, ev.Answer("", False, [], 999, error="answer_timeout"))]
    m = ev.compute_metrics(rows)
    assert m["counts"]["errors"] == 1 and m["latency_ms"]["p50"] is None and m["correct_only"] == 0


def test_answers_with_content_must_have_source() -> None:
    question = q("c", "in_scope", expected_keywords=["x"])
    rows = [
        row(question, ev.Answer("x", False, [ev.Citation("A.pdf", 1)], 1)),
        row(question, ev.Answer("x", False, [], 1)),
        row(question, ev.Answer(ev.NOT_FOUND_SENTENCE, True, [], 1)),
    ]
    assert ev.compute_metrics(rows)["answers_with_content_having_source"] == 0.5


def test_grader_by_answer_overlap_when_no_keywords() -> None:
    question = q("g", "in_scope", expected_answer="Thời hạn thanh toán là ba mươi ngày làm việc")
    good = ev.Answer("Thanh toán trong thời hạn ba mươi ngày làm việc.", False, [], 1)
    bad = ev.Answer("Giá gói tiêu chuẩn là 12 triệu.", False, [], 1)
    assert ev.is_correct(question, good) and not ev.is_correct(question, bad)


def test_empty_categories_give_none() -> None:
    m = ev.compute_metrics([])
    assert m["correct_with_source"] is None and m["hallucination_rate"] is None


def test_dataset_validation(tmp_path: Path) -> None:
    bad = tmp_path / "bad.jsonl"
    bad.write_text(json.dumps({"id": "1", "type": "khac", "question": "?"}) + "\n", encoding="utf-8")
    with pytest.raises(ValueError):
        ev.load_dataset(bad)
    dup = tmp_path / "dup.jsonl"
    line = json.dumps({"id": "1", "type": "in_scope", "question": "?"})
    dup.write_text(f"{line}\n{line}\n", encoding="utf-8")
    with pytest.raises(ValueError):
        ev.load_dataset(dup)


def test_end_to_end_with_fake_asker(tmp_path: Path) -> None:
    code = ev.main(["--dataset", str(DATASET), "--fake", "--out", str(tmp_path), "--review-sample", "0.2"])
    assert code == 0
    report = json.loads(next(tmp_path.glob("*.json")).read_text(encoding="utf-8"))
    m = report["metrics"]
    assert m["counts"]["total"] == 5
    assert m["correct_with_source"] == 1.0 and m["hallucination_rate"] == 0.0
    assert m["source_coverage"] == 1.0 and m["follow_up_correct"] == 1.0 and m["correct_page"] == 1.0
    markdown = next(tmp_path.glob("*.md")).read_text(encoding="utf-8")
    assert "Đúng và có nguồn (MET-002) | 100.0%" in markdown
    assert next(tmp_path.glob("*-review.csv")).exists()


def test_fake_asker_wrong_answers_lower_metrics() -> None:
    questions = ev.load_dataset(DATASET)
    rows = ev.evaluate(questions, ev.FakeAsker(questions, wrong_ids=["s001", "s101"]))
    m = ev.compute_metrics(rows)
    assert m["correct_with_source"] == 0.5 and m["hallucination_rate"] == 1.0
