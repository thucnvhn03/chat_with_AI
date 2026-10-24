"""Số liệu Prometheus dùng chung giữa ứng dụng và worker (M-13)."""

from prometheus_client import Counter, Gauge, Histogram

HTTP_REQUESTS = Counter("http_requests_total", "Số yêu cầu HTTP", ["method", "route", "status"])
HTTP_LATENCY = Histogram(
    "http_request_duration_seconds", "Thời gian xử lý yêu cầu HTTP", ["method", "route"]
)

ANSWER_LATENCY = Histogram(
    "answer_latency_seconds",
    "Thời gian trả lời một câu hỏi, từ lúc nhận tới lúc có kết quả",
    buckets=(0.5, 1, 2, 3, 5, 8, 13, 20, 30, 45, 60, 90),
)
QA_STEP_LATENCY = Histogram(
    "qa_step_seconds",
    "Thời gian từng bước hỏi đáp",
    ["step"],
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1, 2, 5, 10, 20, 40, 60),
)
ANSWERS = Counter("answers_total", "Số câu trả lời theo kết quả", ["outcome"])

JOBS_QUEUED = Gauge("jobs_queued", "Số việc đang chờ trong hàng đợi", ["kind"])
JOBS_PROCESSED = Counter("jobs_processed_total", "Số việc đã xử lý", ["kind", "outcome"])
INGEST_DURATION = Histogram(
    "ingest_duration_seconds",
    "Thời gian nạp một tài liệu",
    buckets=(1, 2, 5, 10, 20, 40, 60, 120, 300, 600),
)
DOCUMENTS_DELETING_OVERDUE = Gauge(
    "documents_deleting_overdue", "Số tài liệu ở trạng thái deleting quá PURGE_SLA_HOURS"
)
OLDEST_QUEUED_JOB_AGE = Gauge(
    "jobs_oldest_queued_age_seconds", "Tuổi của việc chờ lâu nhất trong hàng đợi"
)
COMPONENT_UP = Gauge(
    "component_up", "Kết quả kiểm tra thành phần của /health/ready (1 = hoạt động)", ["component"]
)
