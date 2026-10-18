"""Реестр генераторов: старые модули topic3..6 (алгебра) и новые t_*.py (любой предмет).

Новый модуль t_<имя>.py обязан задать:
    TOPIC    id темы (как в YAML), например "geo-01-quadrilaterals"
    DIR      папка предмета в content/, например "geometry8"
    GROUPS   [(id группы, название, генератор, номер шага урока), ...]
    verify   функция verify(task: dict) -> str | None: независимая проверка ответа (None — всё верно, строка — описание ошибки)
и может задать OLYMPIAD (те же кортежи, группы «со звёздочкой»).
"""
from __future__ import annotations

import importlib
from pathlib import Path
from typing import Callable, NamedTuple

HERE = Path(__file__).parent
ROOT = HERE.parents[1]

LEGACY = [("topic3", "03-roots-compare"), ("topic4", "04-roots-simplify"), ("topic5", "05-quadratic"), ("topic6", "06-fraction-mult")]
LEGACY_OLYMPIAD = [("olymp3", "03-roots-compare"), ("olymp4", "04-roots-simplify"), ("olymp5", "05-quadratic")]


class GenTopic(NamedTuple):
    id: str
    dir: str
    groups: list
    olympiad: list
    # None — проверяет verify_generated.py по старым правилам (только алгебра 8)
    verify: Callable[[dict], str | None] | None


def _load(name: str):
    try:
        return importlib.import_module(name)
    except ModuleNotFoundError:
        return None


def topics() -> list[GenTopic]:
    found: dict[str, dict] = {}
    for name, topic_id in LEGACY:
        mod = _load(name)
        if mod:
            found[topic_id] = {"dir": "algebra8", "groups": mod.GROUPS, "olympiad": [], "verify": None}
    for name, topic_id in LEGACY_OLYMPIAD:
        mod = _load(name)
        if mod and topic_id in found:
            found[topic_id]["olympiad"] = mod.OLYMPIAD
    for path in sorted(HERE.glob("t_*.py")):
        mod = importlib.import_module(path.stem)
        for need in ("TOPIC", "DIR", "GROUPS", "verify"):
            if not hasattr(mod, need):
                raise RuntimeError(f"{path.name}: нет {need}")
        found[mod.TOPIC] = {"dir": mod.DIR, "groups": mod.GROUPS, "olympiad": getattr(mod, "OLYMPIAD", []), "verify": mod.verify}
    return [GenTopic(tid, f["dir"], f["groups"], f["olympiad"], f["verify"]) for tid, f in found.items()]
