"""Tiến trình worker nền (R-03, ADR-003): `python -m app.worker.run`.

- Lấy việc từ bảng `jobs` bằng `UPDATE … FOR UPDATE SKIP LOCKED` (an toàn khi chạy nhiều worker).
- Bộ xử lý đăng ký theo `kind` (`ingest`, `purge`).
- Lỗi tạm thời: thử lại với thời gian chờ tăng dần tới JOB_MAX_ATTEMPTS; quá số lần → `failed` kèm
  `last_error`, và gọi hook `on_give_up` của bộ xử lý (ví dụ đặt tài liệu `failed/internal`).
- Chạy WORKER_CONCURRENCY luồng song song; tắt êm khi nhận SIGTERM/SIGINT (việc đang chạy được làm xong).
- Việc định kỳ: số liệu hàng đợi, cảnh báo tài liệu `deleting` quá hạn, dọn bản ghi kiểm toán cũ.
"""

import signal
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from prometheus_client import start_http_server

from app.db import transaction
from app.modules.jobs import queue
from app.observability.logging import configure_logging, get_logger
from app.observability.metrics import JOBS_PROCESSED, JOBS_QUEUED, OLDEST_QUEUED_JOB_AGE
from app.runtime import Runtime

log = get_logger("worker")

Handler = Callable[[Runtime, dict[str, Any]], None]
GiveUpHook = Callable[[Runtime, dict[str, Any]], None]


@dataclass
class JobHandler:
    run: Handler
    on_give_up: GiveUpHook | None = None


class Worker:
    def __init__(self, runtime: Runtime, handlers: dict[str, JobHandler]) -> None:
        self.runtime = runtime
        self.handlers = handlers
        self.stop = threading.Event()

    def run_once(self) -> bool:
        """Lấy và xử lý một việc. Trả False nếu hàng đợi không có việc sẵn sàng."""
        settings = self.runtime.settings
        with transaction(self.runtime.sessions) as db:
            job = queue.claim(db)
        if job is None:
            return False

        handler = self.handlers.get(job.kind)
        bound = log.bind(job_id=job.id, kind=job.kind, attempt=job.attempts)
        try:
            if handler is None:
                raise RuntimeError(f"không có bộ xử lý cho kind={job.kind}")
            handler.run(self.runtime, job.payload)
        except Exception as exc:
            error = f"{type(exc).__name__}: {exc}"[:500]
            with transaction(self.runtime.sessions) as db:
                gave_up = queue.retry_or_fail(
                    db, job, error, settings.job_max_attempts, settings.job_retry_base_s
                )
            outcome = "failed" if gave_up else "retry"
            JOBS_PROCESSED.labels(job.kind, outcome).inc()
            bound.warning("job_error", outcome=outcome, error_type=type(exc).__name__)
            if gave_up and handler is not None and handler.on_give_up is not None:
                try:
                    handler.on_give_up(self.runtime, job.payload)
                except Exception as hook_exc:
                    bound.error("job_give_up_hook_failed", error_type=type(hook_exc).__name__)
            return True

        with transaction(self.runtime.sessions) as db:
            queue.mark_done(db, job.id)
        JOBS_PROCESSED.labels(job.kind, "done").inc()
        bound.info("job_done")
        return True

    def drain(self, max_jobs: int = 1000) -> int:
        """Xử lý tới khi hết việc sẵn sàng (dùng trong kiểm thử)."""
        count = 0
        while count < max_jobs and self.run_once():
            count += 1
        return count

    def _loop(self) -> None:
        idle = self.runtime.settings.worker_poll_interval_s
        while not self.stop.is_set():
            try:
                worked = self.run_once()
            except Exception as exc:  # mất kết nối cơ sở dữ liệu...: chờ rồi thử lại
                log.error("worker_loop_error", error_type=type(exc).__name__)
                worked = False
            if not worked:
                self.stop.wait(idle)

    def run_forever(self, maintenance: Callable[[], None] | None = None) -> None:
        settings = self.runtime.settings
        threads = [
            threading.Thread(target=self._loop, name=f"worker-{i}", daemon=True)
            for i in range(settings.worker_concurrency)
        ]
        for t in threads:
            t.start()
        log.info("worker_started", concurrency=settings.worker_concurrency)
        next_maintenance = 0.0
        while not self.stop.is_set():
            if maintenance is not None and time.monotonic() >= next_maintenance:
                try:
                    maintenance()
                except Exception as exc:
                    log.error("maintenance_failed", error_type=type(exc).__name__)
                next_maintenance = time.monotonic() + settings.maintenance_interval_s
            self.update_queue_metrics()
            self.stop.wait(min(15.0, settings.maintenance_interval_s))
        for t in threads:
            t.join()
        log.info("worker_stopped")

    def update_queue_metrics(self) -> None:
        try:
            with self.runtime.sessions() as db:
                depth = queue.queue_depth(db)
                age = queue.oldest_queued_age_s(db)
        except Exception:
            return
        for kind in ("ingest", "purge"):
            JOBS_QUEUED.labels(kind).set(depth.get(kind, 0))
        OLDEST_QUEUED_JOB_AGE.set(age)


def default_handlers() -> dict[str, JobHandler]:
    from app.modules.documents.purge import purge_document
    from app.modules.ingestion.pipeline import ingest_document, mark_ingest_failed

    return {
        queue.KIND_INGEST: JobHandler(ingest_document, mark_ingest_failed),
        queue.KIND_PURGE: JobHandler(purge_document),
    }


def main() -> None:
    from app.config import get_settings
    from app.container import build_runtime
    from app.worker.maintenance import run_maintenance

    settings = get_settings()
    configure_logging(settings.log_level)
    runtime = build_runtime(settings, role="worker")
    worker = Worker(runtime, default_handlers())

    def _handle_stop(signum: int, _frame: object) -> None:
        log.info("worker_stop_requested", signal=signum)
        worker.stop.set()

    signal.signal(signal.SIGTERM, _handle_stop)
    signal.signal(signal.SIGINT, _handle_stop)
    start_http_server(settings.worker_metrics_port)
    worker.run_forever(maintenance=lambda: run_maintenance(runtime))


if __name__ == "__main__":
    main()
