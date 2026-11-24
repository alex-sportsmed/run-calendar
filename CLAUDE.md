# Календарь бега и вело — репозиторий

Исходник опубликованного Artifact «Календарь бега и вело» + резервные выгрузки его базы.
Владелец: Alex (Вильнюс). Язык общения — русский, максимально плотно.
Календарь — только **отображение** плана («План: горы 2026–2027», документ Docs): при изменении сессий или потолка в плане базу календаря обновляют вслед за планом; сам по себе календарь правил не задаёт.

## Идентификаторы
- URL: https://claude.ai/artifact/BhXZ3CHpmMG9RLjx6G6Ujc
- slug (UUID, для db_* и publish): `56a3f749-deaf-44df-86b9-1917398c0b0b`
- runtime-контракт 0.2.96; capabilities страницы: только `db` (страница базу только читает)
- `.published-version` — id последней опубликованной из этого репозитория версии

## Что где
- `calendar.html` — полный документ страницы (21 913 байт на 24.11.2026; побайтная копия живой версии). Единственный источник кода.
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
Копирование документов моделью — не побайтное: при первой выгрузке 24.11.2026 в 4 из 65 документов были найдены и исправлены искажения (заголовок, число в заметке, две пропущенные строки `note`). `verify_export.py` ловит только структурные расхождения. Поэтому снимок из чата — «примерный», а точный — выгрузка из самой страницы (кнопка «Экспорт JSON», если она добавлена) или `db_get` по документу при сомнении. Перед восстановлением из выгрузки сверять документы с планом.

## Восстановление
`db_write` по документам из JSON (по одному, `id` и `data` как в файле).

## Безопасность
Репозиторий приватный. Ключи, токены, пароли не хранить и не выводить.
