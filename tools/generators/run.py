#!/usr/bin/env python3
"""Генерация заданий: python3 tools/generators/run.py  (из корня репозитория). Результат — content/algebra8/generated/*.json."""
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from common import build_group  # noqa: E402

OUT = Path(__file__).resolve().parents[2] / "content/algebra8/generated"

TOPICS = {}
for name, topic_id in [("topic3", "03-roots-compare"), ("topic4", "04-roots-simplify"), ("topic5", "05-quadratic"), ("topic6", "06-fraction-mult")]:
    try:
        TOPICS[topic_id] = __import__(name)
    except ModuleNotFoundError:
        pass

# олимпиадные группы («со звёздочкой»): все задания третьего уровня, в тренажёре идут после обычных групп
OLYMPIAD = {}
for name, topic_id in [("olymp3", "03-roots-compare"), ("olymp4", "04-roots-simplify"), ("olymp5", "05-quadratic")]:
    try:
        OLYMPIAD[topic_id] = __import__(name)
    except ModuleNotFoundError:
        pass


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for topic_id, mod in TOPICS.items():
        groups, tasks = [], []
        for gid, title, gen, lesson in mod.GROUPS:
            rng = random.Random(f"{topic_id}/{gid}")
            groups.append({"id": gid, "title": title, "lessonStep": lesson})
            tasks += build_group(gen, rng, gid)
        if topic_id in OLYMPIAD:
            for gid, title, gen, lesson in OLYMPIAD[topic_id].OLYMPIAD:
                rng = random.Random(f"{topic_id}/{gid}")
                groups.append({"id": gid, "title": title, "lessonStep": lesson, "star": True})
                tasks += build_group(gen, rng, gid, pattern=[3], label="⭐ Олимпиада")
        (OUT / f"{topic_id}.json").write_text(
            json.dumps({"topic": topic_id, "groups": groups, "tasks": tasks}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
        )
        print(topic_id, len(groups), "групп,", len(tasks), "заданий")


if __name__ == "__main__":
    main()
