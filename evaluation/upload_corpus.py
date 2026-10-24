"""Tải bộ tài liệu của bộ câu hỏi chuẩn lên hệ thống qua API rồi chờ tới khi xử lý xong.

    EVAL_LOGIN=... EVAL_PASSWORD=... python evaluation/upload_corpus.py \
        --api http://localhost:8000 --dir evaluation/spikes/corpus

Bỏ qua tệp đã có (cùng tên, trạng thái ready). In trạng thái cuối của từng tệp.
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

import httpx


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--api", required=True)
    parser.add_argument("--dir", type=Path, required=True)
    parser.add_argument("--timeout", type=float, default=1800, help="giây chờ tối đa để xử lý xong")
    args = parser.parse_args()
    login, password = os.environ.get("EVAL_LOGIN"), os.environ.get("EVAL_PASSWORD")
    if not login or not password:
        parser.error("cần EVAL_LOGIN và EVAL_PASSWORD")

    origin = os.environ.get("EVAL_ORIGIN", "http://localhost:5173")
    http = httpx.Client(base_url=f"{args.api.rstrip('/')}/api/v1", timeout=300, headers={"Origin": origin})
    http.post("/auth/login", json={"login": login, "password": password}).raise_for_status()

    existing = {d["file_name"]: d for d in http.get("/documents").json()}
    for path in sorted(args.dir.glob("*.pdf")):
        if existing.get(path.name, {}).get("status") == "ready":
            continue
        with path.open("rb") as f:
            result = http.post("/documents", files=[("files", (path.name, f, "application/pdf"))]).json()[0]
        print(f"{path.name}: {result['status']} {result.get('failure_reason') or ''}", file=sys.stderr)

    deadline = time.monotonic() + args.timeout
    while time.monotonic() < deadline:
        docs = http.get("/documents").json()
        if not any(d["status"] == "processing" for d in docs):
            break
        time.sleep(3)
    for d in sorted(http.get("/documents").json(), key=lambda d: d["file_name"]):
        print(f"{d['file_name']}: {d['status']} {d['failure_reason'] or ''}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
