#!/usr/bin/env bash
# Создаёт метки и 15 issues в репозитории (задачи 1-10, потом эпик и Feature 11-15).
# Требуется GitHub CLI: brew install gh && gh auth login
# Запуск из корня проекта: bash create_issues.sh
set -euo pipefail

REPO="Arch1xxx/vinovatornik"

if ! command -v gh >/dev/null 2>&1; then
  echo "Не найден gh. Установи: brew install gh, затем gh auth login" >&2
  exit 1
fi

echo "Метки..."
gh label create feature    --color 1d76db --description "Новая функциональность" --repo "$REPO" --force
gh label create chore      --color 6e7781 --description "Сборка, CI, инфраструктура" --repo "$REPO" --force
gh label create dependency --color fbca04 --description "Зависит от другой команды" --repo "$REPO" --force
gh label create epic       --color 8250df --description "Эпик" --repo "$REPO" --force
gh label create data       --color f0883e --description "Данные" --repo "$REPO" --force

new_issue() {
  # аргументы: название, метки (через запятую), текст
  gh issue create --repo "$REPO" --title "$1" --label "$2" --assignee "@me" --body "$3"
}

echo "Задачи 1-10..."
new_issue "Список виновников по категориям" "feature,data" \
"Сделать data.py с категориями от бытовых до абстрактных.

Критерий: минимум 10 виновников в категории.
Оценка: 2 ч. Ticket ID: VIN-1"

new_issue "Детерминированный выбор виновного по хешу" "feature" \
"Выбор по SHA-256 нормализованного текста.

Критерий: один ввод даёт один ответ независимо от регистра и пунктуации.
Оценка: 3 ч. Ticket ID: VIN-2"

new_issue "Фильтр «ответ не связан с вводом»" "feature" \
"Исключать виновных и обоснования с общими основами слов.

Критерий: тест на каждом виновном из базы.
Оценка: 3 ч. Ticket ID: VIN-3"

new_issue "Процент уверенности и обоснование" "feature" \
"Уверенность 51-99%, шаблоны обоснований.

Критерий: обоснование упоминает виновного.
Оценка: 2 ч. Ticket ID: VIN-4"

new_issue "Уровни абсурда 1-5" "feature" \
"Уровень N использует первые N категорий.

Критерий: ошибка при уровне вне диапазона.
Оценка: 1 ч. Ticket ID: VIN-5"

new_issue "CLI и вывод в JSON" "feature" \
"python -m vinovatornik [--level N] [--json] текст

Критерий: код возврата 2 при ошибке.
Оценка: 2 ч. Ticket ID: VIN-6"

new_issue "CI на self-hosted runner" "chore" \
"Workflow .github/workflows/ci.yml, раннер на своей машине.

Критерий: зелёный прогон с тестами во вкладке Actions.
Оценка: 3 ч. Ticket ID: VIN-7"

new_issue "Страницы вики (Mermaid, формулы, таблицы)" "documentation" \
"Минимум 5 страниц: Home, Architecture, Algorithm, Process, Testing-and-Deploy, плюс Roadmap и Team.

Критерий: диаграммы и формулы отрисовываются.
Оценка: 4 ч. Ticket ID: VIN-8"

new_issue "HTTP API" "feature" \
"Эндпоинт POST /blame с JSON {\"text\": \"...\", \"level\": 3}.

Зависит от стабильного формата Verdict. Делается в ветке feature/9-http-api через PR.
Оценка: 5 ч. Ticket ID: VIN-9"

new_issue "Dockerfile и релиз v1.0.0" "chore,dependency" \
"Образ с запуском CLI, тег v1.0.0, GitHub Release.

Зависит от Docker-среды команды «Платформа» (см. роадмап в вики).
Оценка: 4 ч. Ticket ID: VIN-10"

echo "Эпик и Feature (11-15)..."
new_issue "Эпик: Виноваторник v1.0" "epic" \
"Выпуск версии 1.0 Виноваторника: движок, интерфейсы, CI/CD и документация."

new_issue "Feature: Движок виноватого" "feature" \
"Подзадачи: #1, #2, #3, #4, #5."

new_issue "Feature: Интерфейсы (CLI и API)" "feature" \
"Подзадачи: #6, #9."

new_issue "Feature: Инфраструктура и CI/CD" "chore" \
"Подзадачи: #7, #10."

new_issue "Feature: Документация" "documentation" \
"Подзадачи: #8."

echo "Готово."
