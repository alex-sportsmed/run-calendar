#!/usr/bin/env python3
"""Проверка выгрузки календаря: python3 -I tools/verify_export.py --sessions N --meta M
Структура и внутренняя согласованность (дата↔имя файла↔sort↔день недели, длительность↔шаги).
Не сверяет тексты с базой посимвольно — см. CLAUDE.md, «Надёжность выгрузки».
"""
import argparse, datetime, json, pathlib, sys

root = pathlib.Path(__file__).resolve().parent.parent
ap = argparse.ArgumentParser()
ap.add_argument("--sessions", type=int, required=True)
ap.add_argument("--meta", type=int, required=True)
a = ap.parse_args()
err, warn = [], []
DOW = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]

def load(p):
    try:
        return json.loads(p.read_text(encoding="utf8"))
    except Exception as e:
        err.append(f"{p.name}: не JSON ({e})")

def total(steps):
    return sum(s["sec"] if "sec" in s else s["repeat"] * total(s["steps"]) for s in steps)

sfiles = sorted((root / "data" / "sessions").glob("*.json"))
if len(sfiles) != a.sessions:
    err.append(f"sessions: файлов {len(sfiles)}, ожидалось {a.sessions}")
for f in sfiles:
    d = load(f)
    if not d:
        continue
    yy, mm, dd = f.stem.split("-")
    v = d.get("data", {})
    if d.get("id") != f"{dd}-{mm}-{yy}":
        err.append(f"{f.name}: id={d.get('id')}")
    if v.get("date") != f"{dd}.{mm}.{yy}" or v.get("sort") != f"{yy}-{mm}-{dd}":
        err.append(f"{f.name}: date/sort не соответствуют имени")
    try:
        if DOW[datetime.date(int(yy), int(mm), int(dd)).weekday()] != v.get("dow"):
            err.append(f"{f.name}: dow={v.get('dow')}")
    except ValueError:
        err.append(f"{f.name}: некорректная дата")
    for k in ("title", "kind", "sport", "phase"):
        if not v.get(k):
            err.append(f"{f.name}: нет {k}")
    if v.get("steps") and v.get("dur") is not None and abs(round(total(v["steps"]) / 60) - v["dur"]) > 6:
        warn.append(f"{f.name}: dur={v['dur']} ≠ сумма шагов {round(total(v['steps'])/60)}")
    if v.get("altSteps") and abs(round(total(v["altSteps"]) / 60) - v.get("altDur", -99)) > 1:
        warn.append(f"{f.name}: altDur не сходится с altSteps")

mfiles = sorted((root / "data" / "meta").glob("*.json"))
if len(mfiles) != a.meta:
    err.append(f"meta: файлов {len(mfiles)}, ожидалось {a.meta}")
for f in mfiles:
    d = load(f)
    if d and f.stem == "config" and not isinstance(d.get("data", {}).get("easyCap"), (int, float)):
        err.append("meta/config: нет числового easyCap")

for w in warn:
    print("WARN", w)
for e in err:
    print("ERR ", e)
print(f"sessions={len(sfiles)} meta={len(mfiles)} errors={len(err)} warnings={len(warn)}")
sys.exit(1 if err else 0)
