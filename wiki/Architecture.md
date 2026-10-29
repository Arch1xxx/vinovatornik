# Архитектура

## Модули

| Модуль | Ответственность |
|---|---|
| `vinovatornik/data.py` | Категории виновников, шаблоны обоснований, запрещённые слова |
| `vinovatornik/engine.py` | Выбор виновника: хеш, фильтр, уверенность |
| `vinovatornik/cli.py` | Разбор аргументов, вывод текста или JSON |
| `tests/` | Автотесты engine и CLI |

## Поток данных

```mermaid
flowchart LR
    U([Пользователь]) -->|текст проблемы| CLI[cli.py]
    CLI --> E[engine.blame]
    D[(data.py)] --> E
    E -->|Verdict| CLI
    CLI -->|текст или JSON| U
```

## Что происходит внутри `blame`

```mermaid
sequenceDiagram
    participant C as CLI
    participant E as engine
    participant D as data
    C->>E: blame(text, level)
    E->>E: проверка ввода и уровня
    E->>E: sha256 нормализованного текста
    E->>D: категории 1..level
    E->>E: убрать виновных, связанных с вводом
    E->>E: выбрать виновного и обоснование по хешу
    E-->>C: Verdict
```

## Модель данных

```mermaid
classDiagram
    class Verdict {
        +str culprit
        +str category
        +int confidence
        +str reason
        +int level
        +render() str
        +to_dict() dict
    }
    class BlameError
    BlameError --|> ValueError
```

## Решения

- **Без внешних зависимостей** в коде: только стандартная библиотека. Зависит от `pytest` только тестовая часть.
- **Хеш вместо `random`**: результат воспроизводим, а значит тестируем.
- **Данные отдельно от логики**: список виновников расширяется без правки алгоритма.
