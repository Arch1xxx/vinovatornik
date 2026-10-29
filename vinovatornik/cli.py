"""Командная строка Виноваторника."""

from __future__ import annotations

import argparse
import json
import sys

from . import __version__
from .engine import DEFAULT_LEVEL, MAX_LEVEL, MIN_LEVEL, BlameError, blame


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="vinovatornik",
        description="Назовёт виноватого. К вашей проблеме он не имеет отношения.",
    )
    parser.add_argument("problem", nargs="*", help="описание проблемы")
    parser.add_argument(
        "-l",
        "--level",
        type=int,
        default=DEFAULT_LEVEL,
        help=f"уровень абсурда от {MIN_LEVEL} до {MAX_LEVEL} (по умолчанию {DEFAULT_LEVEL})",
    )
    parser.add_argument("--json", action="store_true", help="вывести ответ в JSON")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    text = " ".join(args.problem)
    if not text and not sys.stdin.isatty():
        text = sys.stdin.read()

    try:
        verdict = blame(text, args.level)
    except BlameError as err:
        print(f"Ошибка: {err}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(verdict.to_dict(), ensure_ascii=False, indent=2))
    else:
        print(verdict.render())
    return 0


if __name__ == "__main__":
    sys.exit(main())
