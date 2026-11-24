# Календарь бега и вело — репозиторий

Исходник опубликованного Artifact «Календарь бега и вело» + резервные выгрузки его базы.
Владелец: Alex (Вильнюс). Язык общения — русский, максимально плотно.
Календарь — только **отображение** плана («План: горы 2026–2027», документ Docs): при изменении сессий или потолка в плане базу календаря обновляют вслед за планом; сам по себе календарь правил не задаёт.

## Идентификаторы
- URL: https://claude.ai/artifact/BhXZ3CHpmMG9RLjx6G6Ujc
- slug (UUID, для db_* и publish): `56a3f749-deaf-44df-86b9-1917398c0b0b`
- runtime-контракт 0.2.96; capabilities страницы: `db`, `downloads` (страница базу только читает)
- `.published-version` — id последней опубликованной из этого репозитория версии

## Что где
- `calendar.html` — полный документ страницы (побайтная копия живой версии). Единственный источник кода.
- `data/sessions/ГГГГ-ММ-ДД.json` — выгрузка коллекции `sessions` (по документу на день; `id` внутри — `ДД-ММ-ГГГГ`).
- `data/meta/config.json` — документ `meta/config` (`easyCap` — потолок лёгких, `easyCapNote`).
- `tools/jsonl_to_data.py`, `tools/verify_export.py`.

## Правка и публикация кода
1. `get_artifact(slug)` → сверить `version` с `.published-version`. Если отличается — страницу правили вне репозитория. Точная копия живой версии на диск без пересказа: `read_file(slug, paths=["index.html"])` (клиент сохраняет файл побайтно; скопировать его в `calendar.html`), затем править.
2. Править `calendar.html` точечно. Проверка: вынуть `<script>…</script>` во временный файл → `node --check`.
3. Публикация: `publish_files(slug, base_version=<live>, files=[{as:"index.html", path:"calendar.html"}])` (перед первой публикацией за сессию — `guide(topic="pages")`). Данные базы публикация не затрагивает.
4. Новый `version` — в `.published-version`, коммит.

## Схема базы
- `sessions/{ДД-ММ-ГГГГ}`: `date`, `dow`, `sort` (ГГГГ-ММ-ДД), `sport` (run|hike|stairs|trip), `kind` (easy|long|quality|test|checkpoint|trip), `phase`, `week` (null вне недель плана), `dur` (мин, null у походов), `title`, `notes[]`, `cond`, `steps[]` (`{label,sec,target,type,z,note?}` или `{repeat,steps[]}`; `{cap}` в `target` подставляет `meta/config.easyCap`), `alt`/`altDur`/`altSteps` (вело-вариант), `deload`, `src:"plan"`, `updatedAt` (ДД.ММ.ГГГГ).
- `meta/config`: `easyCap` (сейчас 128), `easyCapNote`, `updatedAt`.
- Изменение сессий и потолка — только после согласования с Alex и согласно «Плану» (правило проекта). Документ `sessions/…` не удалять: удаление в базе необратимо.

## Выгрузка базы
1. `db_list(slug,"sessions",limit=1000)` и `db_list(slug,"meta",limit=100)`; `nextCursor` не пуст — дочитать.
2. Скопировать документы построчно в `/home/claude/raw-cal/sessions.jsonl` и `/home/claude/raw-cal/meta.jsonl` (вне репозитория); затем `python3 -I tools/jsonl_to_data.py /home/claude/raw-cal/sessions.jsonl /home/claude/raw-cal/meta.jsonl`.
3. `python3 -I tools/verify_export.py --sessions N --meta M` (N, M — `count` из db_list).
4. Нет изменений (`git status --porcelain` пуст) → не коммитить. Иначе коммит `export: ГГГГ-ММ-ДД, N сессий` и push.

### Надёжность выгрузки
Копирование документов моделью — не побайтное: при первой выгрузке 24.11.2026 в 4 из 65 документов были найдены и исправлены искажения (заголовок, число в заметке, две пропущенные строки `note`). `verify_export.py` ловит только структурные расхождения. Поэтому снимок из чата — «примерный», а точный — выгрузка из самой страницы (кнопка «Экспорт JSON», добавлена 24.11.2026) или `db_get` по документу при сомнении. Перед восстановлением из выгрузки сверять документы с планом.

## Точная выгрузка (кнопка «Экспорт JSON» на странице)
Кнопка в шапке страницы читает базу напрямую (побайтно, без копирования моделью), сохраняет файл (capability `downloads`, viewer подтверждает) и копирует JSON в буфер. Файл `{exportedAt, collections:{...}}`; раскладка: `python3 -I tools/page_export_to_data.py ФАЙЛ.json`, затем `verify_export.py` с числами из файла. `version`/`updatedAt` страница не отдаёт: у неизменившихся документов они сохраняются, у изменившихся не пишутся. Страница базу только читает; кнопка ничего не пишет. Это основной способ точной выгрузки; db_list-копирование — «примерное».

## Восстановление
`db_write` по документам из JSON (по одному, `id` и `data` как в файле).

## Безопасность
Репозиторий приватный. Ключи, токены, пароли не хранить и не выводить.

## В терминальном Claude Code
Инструментов `publish_files`, `get_artifact`, `read_file`, `db_*` здесь нет; соответствие:

| Выше в документе | Терминальный Claude Code |
|---|---|
| `get_artifact(slug)` | `Artifact` `action:"read"`, `url` (версию сверять с `.published-version`) |
| `read_file(slug, paths=["index.html"])` | `Artifact` `read` с `path:"index.html"` и `out_dir` (файл сохраняется побайтно) → скопировать в `calendar.html` |
| `publish_files(slug, base_version, files)` | `Artifact` `publish`, `url`, `file_path:"calendar.html"` (или `edits`); конфликт версий сервер ловит сам (читать живую версию → слить → повторить); `guide(topic="pages")` не нужен |
| `db_list` | `ArtifactData` `list`, `collection:"sessions"` / `"meta"`, `query.limit` ≤1000, `query.cursor` ← `next_cursor` |
| `db_get` | `ArtifactData` `get`, `collection`, `doc_id` |
| `db_write` | `ArtifactData` `set` (замена) / `update` (слияние) с `if_version` = `version` прочитанного документа; несколько документов — `batch` (≤50, атомарно) |

- `url` для `ArtifactData` и `Artifact` — https://claude.ai/artifact/BhXZ3CHpmMG9RLjx6G6Ujc (slug-UUID не нужен).
- `list`/`get` с `out_dir` пишут каждый документ в `<out_dir>/<collection>/<doc_id>.json` побайтно (без копирования моделью); `doc_id` сессий — `ДД-ММ-ГГГГ`, не `ГГГГ-ММ-ДД`, и порядок выдачи не по датам. Формат файла — `{id, data, version, updatedAt}`, под `jsonl_to_data.py` нужна раскладка по `sort`.
- Проверено 24.11.2026 (только чтение): `list` для `sessions` (есть `next_cursor`) и `meta`, `get` для `meta/config` работают. `set`/`update`/`batch` по схеме есть, на практике не проверялись (в базу не писали).
- Запись и `delete` — только по согласованию с Alex (см. «Схему базы»); документы `sessions/…` не удалять.
