"""Xuất tài liệu OpenAPI của backend ra tệp JSON (frontend sinh kiểu TypeScript từ tệp này).

    python scripts/export_openapi.py ../frontend/src/api/openapi.json
"""

import json
import sys

from app.main import create_app


def main() -> None:
    target = sys.argv[1] if len(sys.argv) > 1 else "openapi.json"
    schema = create_app(lambda: None).openapi()  # type: ignore[arg-type, return-value]
    with open(target, "w", encoding="utf-8") as f:
        json.dump(schema, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")


if __name__ == "__main__":
    main()
