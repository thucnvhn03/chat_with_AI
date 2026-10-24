#!/usr/bin/env bash
# Chạy lệnh của backend trong ảnh dev (không cần cài Python trên máy), gắn vào mạng Docker Compose
# để kiểm thử tích hợp dùng PostgreSQL và kho S3 của compose.
#
#   scripts/backend-docker.sh                       # ruff + mypy + import-linter + toàn bộ pytest
#   scripts/backend-docker.sh pytest tests/unit -q  # lệnh tùy ý
#
# Cần: docker compose -f deploy/docker-compose.yml up -d postgres objectstore
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
IMAGE="${BACKEND_DEV_IMAGE:-cwd-backend-dev}"

if ! docker image inspect "$IMAGE" >/dev/null 2>&1; then
  docker build -f "$ROOT/deploy/Dockerfile.backend" --build-arg INSTALL_EXTRAS=dev -t "$IMAGE" "$ROOT"
fi

if [ $# -eq 0 ]; then
  set -- sh -c "ruff check app tests alembic && ruff format --check app tests alembic && mypy && lint-imports && pytest -q -p no:cacheprovider"
fi

export MSYS_NO_PATHCONV=1
exec docker run --rm -u root --network chat-with-docs_default \
  -v "$ROOT/backend:/app" \
  -e TEST_DATABASE_URL=postgresql+psycopg://chat:chat_dev_password@postgres:5432/chat \
  -e TEST_S3_ENDPOINT_URL=http://objectstore:9000 \
  -e TEST_S3_ACCESS_KEY=chat_s3 -e TEST_S3_SECRET_KEY=chat_s3_dev_password \
  -e ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY:-}" \
  "$IMAGE" "$@"
