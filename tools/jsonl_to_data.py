#!/usr/bin/env python3
"""Раскладка построчного вывода db_list в data/.
Использование: python3 -I tools/jsonl_to_data.py SESSIONS.jsonl META.jsonl
Строка = один документ {data,id,updatedAt,version} дословно, как вернул db_list (без обёртки untrusted-document).
Пишет data/sessions/ГГГГ-ММ-ДД.json и data/meta/<id>.json; файлы, которых нет в снимке, удаляет (выгрузка — полный снимок).
"""
import json, pathlib, sys

root = pathlib.Path(__file__).resolve().parent.parent

def read(p):
    out = []
    for i, line in enumerate(pathlib.Path(p).read_text(encoding="utf8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            out.append(json.loads(line))
        except Exception as e:
            sys.exit(f"{p}:{i}: не JSON ({e})")
    return out

def dump(o):
    return json.dumps(o, ensure_ascii=False, indent=1, sort_keys=True) + "\n"

def put(dirname, docs, name_of):
    d = root / "data" / dirname
    d.mkdir(parents=True, exist_ok=True)
    keep = set()
    for doc in docs:
        n = name_of(doc)
        keep.add(n)
        (d / n).write_text(dump(doc), encoding="utf8")
    for f in d.glob("*.json"):
        if f.name not in keep:
            f.unlink()

sessions = read(sys.argv[1])
meta = read(sys.argv[2])
put("sessions", sessions, lambda d: "{2}-{1}-{0}.json".format(*d["id"].split("-")))
put("meta", meta, lambda d: d["id"] + ".json")
print(f"sessions={len(sessions)} meta={len(meta)}")
