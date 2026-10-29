"""Движок Виноваторника.

Главный инвариант: виновник и обоснование никак не связаны со словами
из описания проблемы. Выбор детерминирован: один и тот же ввод всегда
даёт один и тот же ответ.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import asdict, dataclass

from .data import CATEGORIES, FORBIDDEN_WORDS, LEVEL_NAMES, REASONS

MIN_LEVEL = 1
MAX_LEVEL = 5
DEFAULT_LEVEL = 3

STEM_LEN = 5  # слова с одинаковым началом из 5 букв считаем родственными
MIN_WORD_LEN = 3  # предлоги и частицы в сравнении не участвуют

_WORD_RE = re.compile(r"[a-zа-яё0-9]+", re.IGNORECASE)


class BlameError(ValueError):
    """Некорректный ввод (пустой текст или неверный уровень)."""


@dataclass(frozen=True)
class Verdict:
    culprit: str
    category: str
    confidence: int
    reason: str
    level: int

    def render(self) -> str:
        return (
            f"Виноват: {self.culprit}\n"
            f"Категория: {self.category} (уровень {self.level}/{MAX_LEVEL}, "
            f"{LEVEL_NAMES[self.level]})\n"
            f"Уверенность: {self.confidence}%\n"
            f"Обоснование: {self.reason}"
        )

    def to_dict(self) -> dict:
        return asdict(self)


def tokens(text: str) -> list[str]:
    """Слова в нижнем регистре, ё приведена к е."""
    return _WORD_RE.findall(text.lower().replace("ё", "е"))


def stems(text: str) -> set[str]:
    """Основы слов (первые STEM_LEN букв), короткие слова отбрасываются."""
    return {w[:STEM_LEN] for w in tokens(text) if len(w) >= MIN_WORD_LEN}


def is_related(candidate: str, input_stems: set[str]) -> bool:
    """True, если в candidate есть слово, родственное слову из ввода."""
    return bool(stems(candidate) & input_stems)


def _capitalize(text: str) -> str:
    return text[:1].upper() + text[1:]


def blame(text: str, level: int = DEFAULT_LEVEL) -> Verdict:
    """Назвать виновного. Ответ не связан с текстом проблемы."""
    if not isinstance(level, int) or isinstance(level, bool):
        raise BlameError("уровень должен быть целым числом")
    if not MIN_LEVEL <= level <= MAX_LEVEL:
        raise BlameError(f"уровень должен быть от {MIN_LEVEL} до {MAX_LEVEL}")

    words = tokens(text)
    if not words:
        raise BlameError("опиши проблему: пустой ввод виноватого не найдёт")

    # Нормализованный ключ: регистр, пунктуация и пробелы не влияют на результат.
    digest = hashlib.sha256(f"{level}|{' '.join(words)}".encode("utf-8")).digest()
    input_stems = stems(text)

    pool = [
        (category, culprit)
        for category, culprits in CATEGORIES[:level]
        for culprit in culprits
        if not (set(tokens(culprit)) & FORBIDDEN_WORDS)
        and not is_related(culprit, input_stems)
    ]
    if not pool:
        raise BlameError("не нашлось виновного, не связанного с вводом")

    category, culprit = pool[int.from_bytes(digest[0:4], "big") % len(pool)]

    reasons = [
        _capitalize(template.format(culprit=culprit))
        for template in REASONS
        if not is_related(template.format(culprit=culprit), input_stems)
    ]
    if not reasons:
        raise BlameError("не нашлось обоснования, не связанного с вводом")

    reason = reasons[int.from_bytes(digest[4:8], "big") % len(reasons)]
    confidence = 51 + digest[8] % 49  # 51..99

    return Verdict(
        culprit=_capitalize(culprit),
        category=category,
        confidence=confidence,
        reason=reason,
        level=level,
    )
