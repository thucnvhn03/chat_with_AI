"""Dựng `v1.jsonl` — bộ câu hỏi chuẩn phiên bản 1 (T2-13) trên bộ PDF tổng hợp.

    python evaluation/datasets/build_v1.py --corpus evaluation/spikes/corpus --out evaluation/datasets/v1.jsonl

Gồm ≥ 10 câu mỗi loại `in_scope`, `out_of_scope`, `multi_doc`, `follow_up`. Đây là BẢN NHÁP trên dữ liệu
tổng hợp, không nhạy cảm: business owner phải duyệt đáp án mẫu và thay/bổ sung câu hỏi trên tài liệu thật
(DEP-001, ASM-005) trước khi dùng kết quả cho cổng launch.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "spikes"))

from questions import (  # noqa: E402
    follow_up_questions,
    in_scope_questions,
    load_truth,
    multi_doc_questions,
    out_of_scope_questions,
)

SEED = 11
PER_TYPE = {"in_scope": 24, "out_of_scope": 12, "multi_doc": 11, "follow_up": 12}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--corpus", type=Path, default=Path("evaluation/spikes/corpus"))
    parser.add_argument("--out", type=Path, default=Path("evaluation/datasets/v1.jsonl"))
    args = parser.parse_args()
    truth = load_truth(args.corpus)
    rng = random.Random(SEED)

    in_scope = in_scope_questions(truth) + in_scope_questions(truth, variant=1)
    seen: set[str] = set()
    in_scope = [q for q in in_scope if not (q.question in seen or seen.add(q.question))]
    # Lấy đều các loại sự kiện, giữ đủ câu tiếng Anh để báo cáo theo ngôn ngữ (US-012)
    english = [q for q in in_scope if q.lang == "en"]
    vietnamese = [q for q in in_scope if q.lang == "vi"]
    picked = english + rng.sample(vietnamese, PER_TYPE["in_scope"] - len(english))

    groups = {
        "in_scope": picked,
        "out_of_scope": out_of_scope_questions()[: PER_TYPE["out_of_scope"]],
        "multi_doc": multi_doc_questions(truth)[: PER_TYPE["multi_doc"]],
        "follow_up": rng.sample(follow_up_questions(truth), PER_TYPE["follow_up"]),
    }
    lines = []
    for kind, questions in groups.items():
        if len(questions) < 10:
            raise SystemExit(f"Thiếu câu loại {kind}: {len(questions)}")
        for i, q in enumerate(questions):
            q.id = f"v1-{kind}-{i:02d}"
            lines.append(json.dumps(q.to_json(), ensure_ascii=False))
    header = (
        "// Bộ câu hỏi chuẩn v1 — BẢN NHÁP trên bộ PDF tổng hợp (evaluation/spikes/corpus). "
        "Chờ business owner duyệt đáp án (DEP-001, ASM-005)."
    )
    args.out.write_text("\n".join([header, *lines]) + "\n", encoding="utf-8")
    print(f"Đã ghi {len(lines)} câu vào {args.out}: " + ", ".join(f"{k}={len(v)}" for k, v in groups.items()))


if __name__ == "__main__":
    main()
