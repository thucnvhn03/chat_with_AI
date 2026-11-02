#!/usr/bin/env bash
# Chạy kiểm thử tuần tự từng tầng, ghi JUnit + log vào test-results/<run>/ và run-meta.json.
#
#   .claude/skills/test-run/scripts/run_layers.sh [--run run-YYYY-MM-DD] [--build] [--keep-up] <tầng...>
#
# Tầng: frontend | backend | e2e | eval | alerts | all (= theo đúng thứ tự đó).
# Chạy lại cùng ngày thì ghi đè tầng đó và giữ các tầng khác, nên có thể chạy từng tầng ở nhiều lệnh.
# Mã thoát: 0 mọi tầng đạt; 1 có tầng lỗi kiểm thử; 3 môi trường chưa sẵn sàng (Docker, ảnh, cổng).
set -uo pipefail

# Dạng D:/... trên Git Bash: dùng được cho cả bash lẫn công cụ Windows (node, git, docker) khi đã tắt
# chuyển đổi đường dẫn MSYS bên dưới. Dạng /d/... sẽ bị node hiểu thành D:\d\...
ROOT="$(cd "$(dirname "$0")/../../../.." && (pwd -W 2>/dev/null || pwd))"
SKILL="$ROOT/.claude/skills/test-run"
RUN="run-$(date +%Y-%m-%d)"
BUILD=0
KEEP_UP=0
LAYERS=()
while [ $# -gt 0 ]; do
  case "$1" in
    --run) RUN="$2"; shift 2 ;;
    --build) BUILD=1; shift ;;
    --keep-up) KEEP_UP=1; shift ;;
    all) LAYERS+=(frontend backend e2e eval alerts); shift ;;
    frontend|backend|e2e|eval|alerts) LAYERS+=("$1"); shift ;;
    *) echo "Tham số không hợp lệ: $1" >&2; exit 2 ;;
  esac
done
[ ${#LAYERS[@]} -eq 0 ] && { echo "Cần ít nhất một tầng: frontend backend e2e eval alerts all" >&2; exit 2; }

OUT="$ROOT/test-results/$RUN"
mkdir -p "$OUT"
META="$OUT/run-meta.json"
COMPOSE=(docker compose -f "$ROOT/deploy/docker-compose.yml")
COMPOSE_E2E=(docker compose -f "$ROOT/deploy/docker-compose.yml" -f "$ROOT/deploy/docker-compose.e2e.yml")
# Giữ nguyên đường dẫn trong container (/ev, /m) thay vì để Git Bash đổi thành C:/Program Files/Git/...
export MSYS_NO_PATHCONV=1

# Ghi một mục vào run-meta.json (giữ mục của các lần chạy tầng khác)
meta() {
  node -e '
    const fs = require("fs"); const [f, k, v] = process.argv.slice(1);
    const m = fs.existsSync(f) ? JSON.parse(fs.readFileSync(f, "utf8")) : {};
    const keys = k.split("."); let o = m;
    for (const x of keys.slice(0, -1)) o = o[x] ??= {};
    o[keys.at(-1)] = JSON.parse(v);
    fs.writeFileSync(f, JSON.stringify(m, null, 2));' "$META" "$1" "$2"
}
log() { echo "[test-run] $*"; }

need_docker() {
  if ! docker info >/dev/null 2>&1; then
    log "Docker chưa chạy. Mở Docker Desktop rồi chạy lại."
    exit 3
  fi
  local mem
  mem=$(docker info --format '{{.MemTotal}}' 2>/dev/null || echo 0)
  meta docker "{\"server\":\"$(docker info --format '{{.ServerVersion}}')\",\"cpus\":$(docker info --format '{{.NCPU}}'),\"mem_gb\":$(node -e "console.log((${mem}/2**30).toFixed(1))")}"
  if [ "$mem" -lt $((3 * 1024 * 1024 * 1024)) ]; then
    log "Cảnh báo: Docker chỉ có $(node -e "console.log((${mem}/2**30).toFixed(1))") GB RAM — tầng E2E có thể chậm hoặc lỗi."
  fi
}

wait_healthy() { # dịch vụ...
  for _ in $(seq 1 60); do
    local ok=1
    for s in "$@"; do
      "${COMPOSE[@]}" ps --format '{{.Service}} {{.Status}}' 2>/dev/null | grep -q "^$s .*healthy" || ok=0
    done
    [ $ok -eq 1 ] && return 0
    sleep 3
  done
  log "Hết thời gian chờ: $* chưa healthy"; return 1
}

wait_http() { # url
  for _ in $(seq 1 60); do
    [ "$(curl -s -o /dev/null -w '%{http_code}' "$1")" = "200" ] && return 0
    sleep 3
  done
  log "Hết thời gian chờ $1 trả 200"; return 1
}

record() { # tầng, mã thoát, giây bắt đầu, ghi chú
  meta "layers.$1" "{\"exit\":$2,\"seconds\":$(( $(date +%s) - $3 )),\"finished\":\"$(date -Iseconds)\",\"note\":$(node -e 'console.log(JSON.stringify(process.argv[1]))' "$4")}"
}

FAILED=0
meta commit "\"$(git -C "$ROOT" rev-parse --short HEAD)\""
meta branch "\"$(git -C "$ROOT" rev-parse --abbrev-ref HEAD)\""
meta dirty "$( [ -n "$(git -C "$ROOT" status --short -- backend frontend e2e evaluation deploy)" ] && echo true || echo false)"

for layer in "${LAYERS[@]}"; do
  start=$(date +%s)
  case "$layer" in
    frontend)
      log "Frontend (Vitest)…"
      (cd "$ROOT/frontend" && npx vitest run --reporter=default --reporter=junit \
        --outputFile.junit="$OUT/frontend-vitest.xml") >"$OUT/frontend-vitest.log" 2>&1
      rc=$?; record frontend $rc "$start" ""
      ;;

    backend)
      need_docker
      log "Backend (pytest) — khởi động postgres, objectstore…"
      "${COMPOSE[@]}" up -d postgres objectstore >/dev/null 2>&1 && wait_healthy postgres objectstore || exit 3
      rm -f "$ROOT/backend/test-results/backend.xml"
      "$ROOT/scripts/backend-docker.sh" pytest -q -p no:cacheprovider -rs \
        --junitxml=test-results/backend.xml >"$OUT/backend-pytest.log" 2>&1
      rc=$?
      [ -f "$ROOT/backend/test-results/backend.xml" ] && mv "$ROOT/backend/test-results/backend.xml" "$OUT/backend-pytest.xml"
      record backend $rc "$start" "$(grep -E '^SKIPPED' "$OUT/backend-pytest.log" | head -5 | tr '\n' ' ')"
      ;;

    e2e)
      need_docker
      # Ảnh Docker phải mới hơn commit mã cuối, nếu không kết quả không phản ánh mã hiện tại
      last_code=$(git -C "$ROOT" log -1 --format=%ct -- backend frontend deploy)
      img=$(docker image inspect chat-with-docs-backend --format '{{.Created}}' 2>/dev/null || true)
      if [ -z "$img" ] && [ $BUILD -eq 0 ]; then
        log "Chưa có ảnh chat-with-docs-*. Chạy lại với --build (build nặng, vài phút)."; exit 3
      fi
      if [ -n "$img" ] && [ $BUILD -eq 0 ]; then
        img_ts=$(node -e "console.log(Math.floor(Date.parse('$img')/1000))")
        if [ "$img_ts" -lt "$last_code" ]; then
          log "Ảnh Docker ($img) cũ hơn commit mã cuối. Chạy lại với --build để kiểm thử mã hiện tại."; exit 3
        fi
      fi
      meta image_created "\"${img:-mới build}\""
      log "E2E — dựng stack…"
      if [ $BUILD -eq 1 ]; then "${COMPOSE_E2E[@]}" up -d --build >"$OUT/e2e-stack.log" 2>&1
      else "${COMPOSE_E2E[@]}" up -d >"$OUT/e2e-stack.log" 2>&1; fi
      wait_http http://localhost:5173/ || exit 3
      cp "$SKILL/scripts/playwright.evidence.config.ts" "$ROOT/e2e/playwright.evidence.config.ts"
      rm -rf "$OUT/pw-output"
      log "E2E (Playwright, chụp ảnh mọi ca)…"
      (cd "$ROOT/e2e" && EVIDENCE_DIR="$OUT" npx playwright test --config playwright.evidence.config.ts) \
        >"$OUT/e2e-playwright.log" 2>&1
      rc=$?
      rm -f "$ROOT/e2e/playwright.evidence.config.ts"
      record e2e $rc "$start" ""
      ;;

    eval)
      need_docker
      log "Bộ đánh giá — công thức chỉ số (pytest trong ảnh cwd-backend-dev)…"
      docker image inspect cwd-backend-dev >/dev/null 2>&1 || { log "Chưa có ảnh cwd-backend-dev — chạy tầng backend trước."; exit 3; }
      docker run --rm -u root -v "$ROOT/evaluation:/ev" -w /ev cwd-backend-dev \
        pytest -q -p no:cacheprovider --junitxml=/ev/.evaluation-pytest.xml >"$OUT/evaluation-pytest.log" 2>&1
      rc=$?
      mv -f "$ROOT/evaluation/.evaluation-pytest.xml" "$OUT/evaluation-pytest.xml" 2>/dev/null
      record eval $rc "$start" ""
      ;;

    alerts)
      need_docker
      log "Luật cảnh báo (promtool)…"
      docker run --rm -v "$ROOT/deploy/monitoring:/m" --entrypoint promtool prom/prometheus:v3.1.0 \
        test rules /m/alerts_test.yml >"$OUT/ops-promtool.log" 2>&1
      rc=$?; record alerts $rc "$start" ""
      ;;
  esac
  [ "$rc" -ne 0 ] && FAILED=1
  log "$layer: mã thoát $rc ($(( $(date +%s) - start ))s)"
done

if [ $KEEP_UP -eq 0 ] && docker info >/dev/null 2>&1; then
  "${COMPOSE_E2E[@]}" stop >/dev/null 2>&1 && log "Đã dừng container (dữ liệu giữ nguyên)."
fi
log "Kết quả thô: test-results/$RUN"
exit $FAILED
