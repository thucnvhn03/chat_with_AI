"""T1-10 (kho tệp S3) và T1-12 (hàng đợi việc, vòng lặp worker)."""

import io
import threading
import uuid

import pytest
from sqlalchemy import select

from app.db import transaction
from app.modules.jobs import queue
from app.modules.jobs.models import Job
from app.worker.run import JobHandler, Worker

pytestmark = pytest.mark.integration


def test_file_store_put_get_delete_twice(runtime) -> None:  # type: ignore[no-untyped-def]
    store = runtime.file_store
    key = f"documents/test/{uuid.uuid4()}.pdf"
    store.put(key, io.BytesIO(b"%PDF-1.7 noi dung"))
    assert store.exists(key)
    assert store.get(key) == b"%PDF-1.7 noi dung"
    store.delete(key)
    assert not store.exists(key)
    store.delete(key)  # lần hai không lỗi
    store.check()


def _enqueue(runtime, n: int, kind: str = "ingest") -> None:  # type: ignore[no-untyped-def]
    with transaction(runtime.sessions) as db:
        for i in range(n):
            queue.enqueue(db, kind, {"n": i})


def test_two_workers_never_claim_the_same_job(runtime) -> None:  # type: ignore[no-untyped-def]
    _enqueue(runtime, 40)
    claimed: list[int] = []
    lock = threading.Lock()

    def handler(_rt, payload) -> None:  # type: ignore[no-untyped-def]
        with lock:
            claimed.append(payload["n"])

    workers = [Worker(runtime, {"ingest": JobHandler(handler)}) for _ in range(4)]
    threads = [threading.Thread(target=w.drain) for w in workers]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert sorted(claimed) == list(range(40))
    with runtime.sessions() as db:
        assert set(db.scalars(select(Job.status))) == {"done"}


def test_transient_error_is_retried_then_succeeds(runtime) -> None:  # type: ignore[no-untyped-def]
    _enqueue(runtime, 1)
    calls = {"n": 0}

    def flaky(_rt, _payload) -> None:  # type: ignore[no-untyped-def]
        calls["n"] += 1
        if calls["n"] < 2:
            raise ConnectionError("kho tạm thời không truy cập được")

    Worker(runtime, {"ingest": JobHandler(flaky)}).drain()
    with runtime.sessions() as db:
        job = db.scalar(select(Job))
    assert calls["n"] == 2 and job.status == "done" and job.attempts == 2


def test_job_fails_after_max_attempts_and_calls_give_up(runtime) -> None:  # type: ignore[no-untyped-def]
    _enqueue(runtime, 1)
    gave_up: list[dict] = []  # type: ignore[type-arg]

    def broken(_rt, _payload) -> None:  # type: ignore[no-untyped-def]
        raise RuntimeError("luôn lỗi")

    Worker(runtime, {"ingest": JobHandler(broken, lambda _rt, p: gave_up.append(p))}).drain()
    with runtime.sessions() as db:
        job = db.scalar(select(Job))
    assert job.status == "failed"
    assert job.attempts == runtime.settings.job_max_attempts
    assert "RuntimeError" in (job.last_error or "")
    assert gave_up == [{"n": 0}]


def test_backoff_delays_next_attempt(runtime) -> None:  # type: ignore[no-untyped-def]
    runtime.settings = runtime.settings.model_copy(update={"job_retry_base_s": 3600})
    _enqueue(runtime, 1)

    def broken(_rt, _payload) -> None:  # type: ignore[no-untyped-def]
        raise RuntimeError("lỗi")

    worker = Worker(runtime, {"ingest": JobHandler(broken)})
    assert worker.run_once() is True
    assert worker.run_once() is False  # việc đang chờ tới lượt sau, chưa lấy lại
    with runtime.sessions() as db:
        assert db.scalar(select(Job.status)) == "queued"
