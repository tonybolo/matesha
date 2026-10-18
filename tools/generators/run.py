#!/usr/bin/env python3
"""Генерация заданий (из корня репозитория):
    python3 tools/generators/run.py              все темы
    python3 tools/generators/run.py <id темы>…   только указанные
Результат — content/<предмет>8/generated/<id темы>.json."""
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from common import build_group  # noqa: E402
from registry import ROOT, topics  # noqa: E402


def main(only: list[str]) -> None:
    known = topics()
    for name in only:
        if name not in {t.id for t in known}:
            raise SystemExit(f"Нет генератора для темы {name}")
    for t in known:
        if only and t.id not in only:
            continue
        out = ROOT / "content" / t.dir / "generated"
        out.mkdir(parents=True, exist_ok=True)
        groups, tasks = [], []
        for gid, title, gen, lesson in t.groups:
            rng = random.Random(f"{t.id}/{gid}")
            groups.append({"id": gid, "title": title, "lessonStep": lesson})
            tasks += build_group(gen, rng, gid)
        # олимпиадные группы («со звёздочкой»): все задания третьего уровня, в тренажёре идут после обычных групп
        for gid, title, gen, lesson in t.olympiad:
            rng = random.Random(f"{t.id}/{gid}")
            groups.append({"id": gid, "title": title, "lessonStep": lesson, "star": True})
            tasks += build_group(gen, rng, gid, pattern=[3], label="⭐ Олимпиада")
        (out / f"{t.id}.json").write_text(
            json.dumps({"topic": t.id, "groups": groups, "tasks": tasks}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
        )
        print(t.id, len(groups), "групп,", len(tasks), "заданий")


if __name__ == "__main__":
    main(sys.argv[1:])
