"""HTTP API Виноваторника: POST /blame.

Запрос:  {"text": "в меня врезался грузовик", "level": 3}
Ответ:   {"culprit": ..., "category": ..., "confidence": ..., "reason": ..., "level": ...}

Только стандартная библиотека. Запуск: python -m vinovatornik.api [порт]
"""

from __future__ import annotations

import json
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

from .engine import DEFAULT_LEVEL, BlameError, blame


def handle_blame(payload: object) -> tuple[int, dict]:
    """Чистая функция: тело запроса -> (HTTP-код, ответ). Её проще тестировать."""
    if not isinstance(payload, dict) or "text" not in payload:
        return 400, {"error": "ожидается JSON с полем text"}
    text = payload["text"]
    if not isinstance(text, str):
        return 400, {"error": "поле text должно быть строкой"}
    try:
        verdict = blame(text, payload.get("level", DEFAULT_LEVEL))
    except BlameError as err:
        return 400, {"error": str(err)}
    return 200, verdict.to_dict()


class Handler(BaseHTTPRequestHandler):
    def _send(self, status: int, body: dict) -> None:
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/blame":
            self._send(404, {"error": "не найдено"})
            return
        length = int(self.headers.get("Content-Length") or 0)
        try:
            payload = json.loads(self.rfile.read(length) or b"null")
        except json.JSONDecodeError:
            self._send(400, {"error": "некорректный JSON"})
            return
        self._send(*handle_blame(payload))

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/health":
            self._send(200, {"status": "ok"})
        else:
            self._send(404, {"error": "не найдено"})


def main(port: int = 8000) -> None:
    server = HTTPServer(("127.0.0.1", port), Handler)
    print(f"Виноваторник слушает на http://127.0.0.1:{port}")
    server.serve_forever()


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 8000)
