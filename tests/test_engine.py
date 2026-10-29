import re

import pytest

from vinovatornik import BlameError, blame
from vinovatornik.data import CATEGORIES, FORBIDDEN_WORDS, REASONS

SAMPLES = [
    "в меня врезался грузовик",
    "упал прод",
    "DNS не резолвится, пользователи в панике",
    "соседский перфоратор разбудил меня в семь утра",
    "кот опять уронил кружку",
    "Сломался лифт!!!",
    "забыл зонт и промок",
    "ночной деплой в пятницу всё сломал",
]


def _stems(text: str) -> set[str]:
    """Независимая от движка проверка родства слов (первые 5 букв)."""
    words = re.findall(r"[a-zа-яё0-9]+", text.lower().replace("ё", "е"))
    return {w[:5] for w in words if len(w) >= 3}


@pytest.mark.parametrize("text", SAMPLES)
def test_verdict_is_deterministic(text):
    assert blame(text) == blame(text)


def test_case_spaces_and_punctuation_do_not_matter():
    assert blame("В меня врезался грузовик!!!") == blame("  в  меня врезался   грузовик ")


@pytest.mark.parametrize("text", SAMPLES)
@pytest.mark.parametrize("level", [1, 2, 3, 4, 5])
def test_culprit_and_reason_are_unrelated_to_input(text, level):
    verdict = blame(text, level)
    assert not _stems(text) & _stems(verdict.culprit)
    assert not _stems(text) & _stems(verdict.reason.replace(verdict.culprit, ""))


def test_every_culprit_can_be_blamed_for_itself_but_never_is():
    """Если ввести самого виновного, он не должен оказаться обвиняемым."""
    for _, culprits in CATEGORIES:
        for culprit in culprits:
            verdict = blame(culprit, level=5)
            assert not _stems(culprit) & _stems(verdict.culprit)


def test_user_is_never_blamed():
    for _, culprits in CATEGORIES:
        for culprit in culprits:
            words = set(re.findall(r"[а-яё]+", culprit.lower()))
            assert not words & FORBIDDEN_WORDS


@pytest.mark.parametrize("text", SAMPLES)
def test_confidence_range(text):
    assert 51 <= blame(text).confidence <= 99


def test_level_limits_categories():
    allowed = {name for name, _ in CATEGORIES[:1]}
    for text in SAMPLES:
        assert blame(text, level=1).category in allowed


def test_different_inputs_give_different_culprits():
    culprits = {blame(f"проблема номер {i}").culprit for i in range(50)}
    assert len(culprits) > 5


def test_reasons_mention_culprit():
    assert all("{culprit}" in template for template in REASONS)


@pytest.mark.parametrize("bad_level", [0, 6, -1])
def test_bad_level_rejected(bad_level):
    with pytest.raises(BlameError):
        blame("что-то случилось", bad_level)


def test_non_integer_level_rejected():
    with pytest.raises(BlameError):
        blame("что-то случилось", "3")  # type: ignore[arg-type]


@pytest.mark.parametrize("text", ["", "   ", "!!!"])
def test_empty_input_rejected(text):
    with pytest.raises(BlameError):
        blame(text)


def test_render_contains_all_fields():
    rendered = blame("в меня врезался грузовик").render()
    for label in ("Виноват:", "Категория:", "Уверенность:", "Обоснование:"):
        assert label in rendered
