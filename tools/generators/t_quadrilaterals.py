"""Тема «Определения четырёхугольников» (геометрия 8, Атанасян, гл. V «Четырёхугольники»).

Группы заданий: name (назови фигуру по описанию), tf (верно ли утверждение), which (какие утверждения верны),
angle4 (сумма углов), perim (периметр), coord (фигура по координатам вершин) и ⭐ subtle (тонкие вопросы).

Как устроено:
  * генератор держит таблицу «фигура → свойства» (ATOMS, DEF) и строит из неё утверждения и описания;
  * verify() ничего не берёт из таблицы: утверждения и описания она РАЗБИРАЕТ ПО ТЕКСТУ условия, а истинность считает
    на модели из всех выпуклых четырёхугольников с вершинами в узлах решётки 5×5 (точная целочисленная арифметика:
    векторные произведения, квадраты длин, скалярные произведения). Углы и периметры пересчитываются по геометрии
    (построение фигуры по координатам, перебор), а не по формулам генератора.
"""
from __future__ import annotations

import itertools
import math
import random
import re
import zlib
from fractions import Fraction

from common import task

TOPIC = "geo-01-quadrilaterals"
DIR = "geometry8"

# ====================================================================================================
# 1. Словарь и таблица «фигура → свойства» (модель генератора)
# ====================================================================================================

# ключ: (именительный, родительный, творительный, творительный мн.ч., род)
NAME = {
    "quad": ("четырёхугольник", "четырёхугольника", "четырёхугольником", "четырёхугольниками", "m"),
    "trap": ("трапеция", "трапеции", "трапецией", "трапециями", "f"),
    "iso": ("равнобедренная трапеция", "равнобедренной трапеции", "равнобедренной трапецией", "равнобедренными трапециями", "f"),
    "rtrap": ("прямоугольная трапеция", "прямоугольной трапеции", "прямоугольной трапецией", "прямоугольными трапециями", "f"),
    "par": ("параллелограмм", "параллелограмма", "параллелограммом", "параллелограммами", "m"),
    "rect": ("прямоугольник", "прямоугольника", "прямоугольником", "прямоугольниками", "m"),
    "rhomb": ("ромб", "ромба", "ромбом", "ромбами", "m"),
    "square": ("квадрат", "квадрата", "квадратом", "квадратами", "m"),
}
KEYS = list(NAME)
TRAPF = {"trap", "iso", "rtrap"}
PARF = {"par", "rect", "rhomb", "square"}

QUANT = {"m": ["Всякий", "Каждый", "Любой"], "f": ["Всякая", "Каждая", "Любая"]}
QUANT_GEN = {"m": ["всякого", "каждого", "любого"], "f": ["всякой", "каждой", "любой"]}
NONE_W = {"m": "Ни один", "f": "Ни одна"}
WHICH_W = {"m": "которого", "f": "которой"}
PRON = {"m": "он", "f": "она"}

# свойства
#   P2 — обе пары противоположных сторон параллельны; P1 — параллельна ровно одна пара; P0 — параллельных сторон нет;
#   EQ — все стороны равны; RA — все углы прямые; R1 — есть прямой угол; OPS — противоположные стороны равны;
#   OPA — противоположные углы равны; LEG — боковые стороны равны (у трапеции); ADJ — есть две равные соседние стороны
PH = {
    "P2": "противоположные стороны попарно параллельны",
    "P1": "ровно одна пара сторон параллельна",
    "P0": "нет параллельных сторон",
    "EQ": "все стороны равны",
    "RA": "все углы прямые",
    "R1": "есть прямой угол",
    "OPS": "противоположные стороны равны",
    "OPA": "противоположные углы равны",
    "LEG": "боковые стороны равны",
    "ADJ": "есть две равные соседние стороны",
}

# родители в «семейном дереве»
PARENTS = {
    "quad": [], "par": ["quad"], "trap": ["quad"], "rect": ["par"], "rhomb": ["par"],
    "square": ["rect", "rhomb"], "iso": ["trap"], "rtrap": ["trap"],
}
# определяющие свойства
DEF = {
    "quad": set(), "par": {"P2"}, "rect": {"P2", "RA"}, "rhomb": {"P2", "EQ"}, "square": {"P2", "RA", "EQ"},
    "trap": {"P1"}, "iso": {"P1", "LEG"}, "rtrap": {"P1", "R1"},
}
# «атомы» — виды фигур, которые уже нельзя разбить на именованные подвиды; у каждого указаны свойства, которые есть ВСЕГДА
ATOMS = {
    "q0": {"P0"},
    "t0": {"P1"},
    "iso": {"P1", "LEG"},
    "rt": {"P1", "R1"},
    "p0": {"P2", "OPS", "OPA"},
    "re": {"P2", "OPS", "OPA", "RA", "R1"},
    "rh": {"P2", "OPS", "OPA", "EQ", "ADJ"},
    "sq": {"P2", "OPS", "OPA", "RA", "R1", "EQ", "ADJ"},
}
ATOM_TEXT = {
    "q0": "обычный четырёхугольник без параллельных сторон",
    "t0": "обычная трапеция, не равнобедренная и не прямоугольная",
    "iso": "равнобедренная трапеция",
    "rt": "прямоугольная трапеция",
    "p0": "«косой» параллелограмм с разными соседними сторонами",
    "re": "прямоугольник с разными соседними сторонами",
    "rh": "ромб с непрямыми углами",
    "sq": "квадрат",
}
PRIORITY = ["q0", "p0", "t0", "re", "rh", "iso", "rt", "sq"]  # какими примерами пользуемся первыми


def first(atoms):
    """Самый наглядный пример из набора «атомов»."""
    return sorted(atoms, key=PRIORITY.index)[0]


SKILL_OF = {
    "quad": "geo-q-parts", "par": "geo-q-parallelogram", "rect": "geo-q-rectangle", "rhomb": "geo-q-rhombus",
    "square": "geo-q-square", "trap": "geo-q-trapezoid", "iso": "geo-q-trapezoid", "rtrap": "geo-q-trapezoid",
}


def members(x: str) -> set[str]:
    """Какие «атомы» входят в класс x."""
    return {a for a, ps in ATOMS.items() if DEF[x] <= ps}


def common(x: str) -> set[str]:
    """Свойства, которые есть у всякой фигуры класса x."""
    return set.intersection(*(ATOMS[a] for a in members(x)))


def nom(k): return NAME[k][0]
def gen_(k): return NAME[k][1]
def ins(k): return NAME[k][2]
def insp(k): return NAME[k][3]
def gender(k): return NAME[k][4]


def pick_word(struct, words):
    """Слово-связка выбираем по структуре утверждения, чтобы одно и то же утверждение всегда звучало одинаково."""
    return words[zlib.crc32(repr(struct).encode()) % len(words)]


def skills_for(*keys) -> list[str]:
    return sorted({SKILL_OF[k] for k in keys if k in SKILL_OF} | {"geo-q-family"})


def num(x) -> str:
    """Число для TeX: десятичная запятая в фигурных скобках."""
    f = Fraction(x)
    if f.denominator == 1:
        return str(f.numerator)
    s = format(float(f), "g")
    return s.replace(".", "{,}")


def dec(x) -> str:
    """Число для записи ответа (точка): 14.5, 7."""
    f = Fraction(x)
    if f.denominator == 1:
        return str(f.numerator)
    return format(float(f), "g")


def txt(x) -> str:
    """Число для обычного текста: 14,5."""
    return dec(x).replace(".", ",")


# ---------------------------------------------------------------------------------------------------
# утверждения: ("all", X, Y) | ("none", X, Y) | ("prop", X, p) | ("exists", X, p) | ("if", X, c, Y, truth) | ("sum", X, N)
# ---------------------------------------------------------------------------------------------------

def stmt_text(s) -> str:
    k = s[0]
    if k == "all":
        g = gender(s[1])
        return f"{pick_word(s, QUANT[g])} {nom(s[1])} является {ins(s[2])}."
    if k == "none":
        return f"{NONE_W[gender(s[1])]} {nom(s[1])} не является {ins(s[2])}."
    if k == "prop":
        g = gender(s[1])
        return f"У {pick_word(s, QUANT_GEN[g])} {gen_(s[1])} {PH[s[2]]}."
    if k == "exists":
        return f"Существует {nom(s[1])}, у {WHICH_W[gender(s[1])]} {PH[s[2]]}."
    if k == "if":
        return f"Если у {gen_(s[1])} {PH[s[2]]}, то {PRON[gender(s[1])]} является {ins(s[3])}."
    if k == "sum":
        g = gender(s[1])
        word = "любого" if g == "m" else "любой"
        convex = "выпуклого " if s[1] == "quad" else ""
        return f"Сумма углов {word} {convex}{gen_(s[1])} равна {s[2]}°."
    raise ValueError(s)


# «если…, то…»: (X, условие, Y, истинно?, уровень, объяснение)
IFS = [
    ("par", "RA", "rect", True, 1, "Это определение прямоугольника: параллелограмм с прямыми углами."),
    ("par", "EQ", "rhomb", True, 1, "Это определение ромба: параллелограмм с равными сторонами."),
    ("quad", "P2", "par", True, 1, "Это определение параллелограмма."),
    ("quad", "P1", "trap", True, 1, "Это определение трапеции: параллельна только одна пара сторон."),
    ("rect", "EQ", "square", True, 1, "Это определение квадрата: прямоугольник с равными сторонами."),
    ("rhomb", "RA", "square", True, 1, "Ромб с прямыми углами — прямоугольник с равными сторонами, то есть квадрат."),
    ("trap", "LEG", "iso", True, 1, "Это определение равнобедренной трапеции."),
    ("trap", "R1", "rtrap", True, 1, "Это определение прямоугольной трапеции."),
    ("par", "R1", "rect", True, 2, "В параллелограмме соседние углы вместе дают 180°, поэтому рядом с прямым углом тоже прямой, а противоположные им — равны им. Все четыре угла прямые, значит, это прямоугольник."),
    ("rect", "ADJ", "square", True, 2, "У прямоугольника противоположные стороны равны. Если ещё две соседние равны, то равны все четыре: это квадрат."),
    ("rhomb", "R1", "square", True, 2, "Ромб — параллелограмм, а у параллелограмма с одним прямым углом все углы прямые. Ромб с прямыми углами — квадрат."),
    ("rect", "EQ", "rhomb", True, 2, "Прямоугольник — параллелограмм, а если у него все стороны равны, то это ромб."),
    ("par", "EQ", "square", False, 2, "Параллелограмм с равными сторонами — это ромб, а углы у него могут быть непрямыми."),
    ("par", "RA", "square", False, 2, "Параллелограмм с прямыми углами — прямоугольник, а стороны у него могут быть разной длины."),
    ("par", "ADJ", "rhomb", True, 3, "Противоположные стороны параллелограмма равны, поэтому при двух равных соседних сторонах равны все четыре: это ромб."),
    ("par", "ADJ", "square", False, 3, "Равные соседние стороны делают из параллелограмма ромб, а ромб бывает с непрямыми углами."),
    ("par", "R1", "square", False, 3, "Один прямой угол делает из параллелограмма прямоугольник, а стороны у него могут быть разными."),
    ("quad", "EQ", "rhomb", True, 3, "Если у четырёхугольника все четыре стороны равны, то он сам оказывается параллелограммом, а значит, ромбом."),
    ("quad", "RA", "rect", True, 3, "Если все углы четырёхугольника прямые, то противоположные стороны параллельны (соседние углы вместе дают 180°). Получился параллелограмм с прямыми углами — прямоугольник."),
    ("quad", "ADJ", "rhomb", False, 3, "У «воздушного змея» (дельтоида) две пары равных соседних сторон, а параллельных сторон нет: это не ромб."),
    ("quad", "R1", "rect", False, 3, "Один прямой угол есть и у прямоугольной трапеции, и у многих «обычных» четырёхугольников — они не прямоугольники."),
    ("trap", "LEG", "par", False, 3, "Боковые стороны равны у равнобедренной трапеции, а она не параллелограмм: у неё параллельна только одна пара сторон."),
    ("trap", "R1", "rect", False, 3, "Прямой угол есть у прямоугольной трапеции, но прямых углов у неё только два, это не прямоугольник."),
]


def truth(s) -> bool:
    k = s[0]
    if k == "all":
        return members(s[1]) <= members(s[2])
    if k == "none":
        return not (members(s[1]) & members(s[2]))
    if k == "prop":
        return s[2] in common(s[1])
    if k == "exists":
        return any(s[2] in ATOMS[a] for a in members(s[1]))
    if k == "if":
        return s[4]
    if k == "sum":
        return s[2] == 360
    raise ValueError(s)


def chain(x: str, y: str) -> list[str] | None:
    """Путь x → … → y по «семейному дереву» (вверх к родителям)."""
    if x == y:
        return [x]
    for p in PARENTS[x]:
        c = chain(p, y)
        if c:
            return [x] + c
    return None


DEFTEXT = {
    "quad": "фигура из четырёх вершин и четырёх сторон",
    "par": "четырёхугольник, у которого противоположные стороны попарно параллельны",
    "rect": "параллелограмм, у которого все углы прямые",
    "rhomb": "параллелограмм, у которого все стороны равны",
    "square": "прямоугольник, у которого все стороны равны",
    "trap": "четырёхугольник, у которого две стороны параллельны, а две другие нет",
    "iso": "трапеция, у которой боковые стороны равны",
    "rtrap": "трапеция, у которой один из углов прямой",
}


def why_prop(x: str, p: str) -> str:
    """Почему у каждой фигуры класса x есть свойство p."""
    if p in DEF[x]:
        return f"Это прямо входит в определение: {nom(x)} — {DEFTEXT[x]}."
    if p == "R1" and "RA" in DEF[x]:
        return f"У {gen_(x)} все углы прямые, значит, прямой угол точно есть."
    if p in ("OPS", "OPA") and x in PARF:
        return f"{nom(x).capitalize()} — это параллелограмм, а у параллелограмма так и есть (это свойство мы докажем в следующей теме)."
    if p == "ADJ" and "EQ" in DEF[x]:
        return f"У {gen_(x)} все стороны равны, поэтому и две соседние равны."
    return f"Так и есть: это следует из определения {gen_(x)}."


def why_not_exists(x: str, p: str) -> str:
    if x in TRAPF and p in ("P2", "EQ", "RA"):
        return "У трапеции параллельна ровно одна пара сторон. А такое свойство делает параллельными обе пары: получился бы параллелограмм, а это уже не трапеция."
    if x in PARF and p == "P1":
        return "У параллелограмма параллельны обе пары сторон, а не ровно одна."
    if x in PARF and p == "P0":
        return "У параллелограмма параллельны обе пары противоположных сторон, поэтому параллельные стороны есть."
    if {x, p} & {"iso", "rtrap"} and p in ("R1", "LEG"):
        return "У прямоугольной трапеции одна боковая сторона перпендикулярна основаниям, а другая наклонная, значит, они разной длины. Поэтому прямоугольная трапеция никогда не равнобедренная."
    return f"Такой фигуры не бывает: свойство «{PH[p]}» не сочетается с определением ({nom(x)})."


def why_none(x: str, y: str) -> str:
    t, q = (x, y) if x in TRAPF else (y, x)
    if t in TRAPF and q in PARF:
        return f"У трапеции параллельна ровно одна пара сторон, а у {gen_(q)} параллельны обе пары. Одна фигура не может быть сразу и тем и другим."
    if {x, y} == {"iso", "rtrap"}:
        return "У прямоугольной трапеции боковые стороны разной длины (одна перпендикулярна основаниям, другая наклонная), а у равнобедренной они равны."
    return "Требования к этим фигурам несовместимы."


def explain(s) -> str:
    """Короткое объяснение, почему утверждение верно или неверно (для решения)."""
    k, ok = s[0], truth(s)
    if k == "all":
        x, y = s[1], s[2]
        if ok:
            c = chain(x, y)
            if c and len(c) > 1:
                return "Идём вверх по семейному дереву: " + " → ".join(nom(i) for i in c) + ". Значит, это верно."
            return f"По определению: каждый {nom(x)} подходит под «{nom(y)}»."
        bad = first(members(x) - members(y))
        if (x in TRAPF and y in PARF) or (x in PARF and y in TRAPF):
            return f"Контрпример: {ATOM_TEXT[bad]}. У трапеции параллельна ровно одна пара сторон, у параллелограмма — две, поэтому одно с другим не совпадает."
        return f"Контрпример: {ATOM_TEXT[bad]}. Это {nom(x)}, но не {nom(y)}."
    if k == "none":
        x, y = s[1], s[2]
        if ok:
            return why_none(x, y)
        both = first(members(x) & members(y))
        return f"Бывает и то и другое сразу, например: {ATOM_TEXT[both]}."
    if k == "prop":
        x, p = s[1], s[2]
        if ok:
            return why_prop(x, p)
        bad = first({a for a in members(x) if p not in ATOMS[a]})
        return f"Свойство «{PH[p]}» бывает не у всех. Например, у такой фигуры его нет: {ATOM_TEXT[bad]}."
    if k == "exists":
        x, p = s[1], s[2]
        if ok:
            good = first({a for a in members(x) if p in ATOMS[a]})
            return f"Такая фигура бывает: {ATOM_TEXT[good]}."
        return why_not_exists(x, p)
    if k == "if":
        return s[5] if len(s) > 5 else ""
    if k == "sum":
        return ("Диагональ режет четырёхугольник на два треугольника по 180°, поэтому сумма углов равна 360° у любого выпуклого четырёхугольника."
                if ok else f"У четырёхугольника сумма углов 360°, а не {s[2]}° (180° — это у треугольника).")
    raise ValueError(s)


# «ни один … не является …»: только осмысленные пары (истина — ради «трапеция не параллелограмм», ложь — ради «а квадрат?»)
NONE_PAIRS = [(t, q) for t in sorted(TRAPF) for q in ("par", "rect", "rhomb", "square")] + [("iso", "rtrap"), ("rtrap", "iso")] + \
    [("rect", "rhomb"), ("rhomb", "rect"), ("par", "square"), ("trap", "iso"), ("trap", "rtrap")]


def _build_statements():
    """Все утверждения с уровнями сложности: список (структура, уровень)."""
    out = []
    for x in KEYS:
        for y in KEYS:
            if x == y:
                continue
            if (x in TRAPF and y in PARF) or (x in PARF and y in TRAPF) or {x, y} == {"iso", "rtrap"}:
                lv = 3
            elif y in PARENTS[x] or x in PARENTS[y]:
                lv = 1
            else:
                lv = 2
            out.append((("all", x, y), lv))
    for x in KEYS:
        for p in ("P2", "P1", "EQ", "RA", "R1", "OPS", "OPA", "LEG"):
            if p == "LEG" and x not in TRAPF:
                continue
            if p == "P1" and x == "quad":
                continue
            if x in TRAPF and p in ("P2", "EQ", "RA", "OPS", "OPA"):
                lv = 3
            elif p in ("OPS", "OPA", "R1", "LEG", "P1"):
                lv = 2
            else:
                lv = 1
            out.append((("prop", x, p), lv))
    for x in KEYS:
        for p in ("P2", "P1", "EQ", "RA", "R1", "LEG", "P0"):
            if p == "LEG" and x not in TRAPF:
                continue
            if p == "P0" and x != "quad":
                continue  # «трапеция без параллельных сторон» — бессмыслица
            if p in common(x):
                continue  # «существует прямоугольник с прямыми углами» — слишком очевидно
            if p == "R1" and x == "quad":
                continue  # у обычных четырёхугольников прямой угол встречается «иногда»: утверждение нечёткое
            out.append((("exists", x, p), 3 if (x in TRAPF or p in ("P1", "P0")) else 2))
    for x, y in NONE_PAIRS:
        out.append((("none", x, y), 3 if truth(("none", x, y)) else 2))
    for x in KEYS:
        out.append((("sum", x, 360), 1))
        for n in (180, 270, 540, 720):
            out.append((("sum", x, n), 1))
    for (x, c, y, tr, lv, why) in IFS:
        out.append((("if", x, c, y, tr, why), lv))
    return out


STATEMENTS = _build_statements()


def conv_note(stmts) -> bool:
    """Нужно ли напомнить, что у трапеции параллельна ровно одна пара сторон (утверждение зависит от этого соглашения)."""
    for s in stmts:
        keys = set()
        props = set()
        if s[0] in ("all", "none"):
            keys = {s[1], s[2]}
        elif s[0] in ("prop", "exists"):
            keys, props = {s[1]}, {s[2]}
        elif s[0] == "if":
            keys, props = {s[1], s[3]}, {s[2]}
        if keys & TRAPF and (keys & PARF or props & {"P2", "EQ", "RA", "OPS", "OPA"}):
            return True
        if keys & PARF and "P1" in props:
            return True
    return False


CONV = "Напоминание: у трапеции параллельна ровно одна пара сторон."


def statements_of(level: int, want: bool | None = None):
    return [s for s, lv in STATEMENTS if lv == level and (want is None or truth(s) == want)]


CATEGORY_WEIGHTS = {
    1: {"all": 45, "prop": 30, "sum": 10, "if": 15},
    2: {"all": 25, "prop": 20, "exists": 20, "none": 15, "if": 20},
    3: {"all": 30, "none": 20, "exists": 15, "if": 25, "prop": 10},
}


def pick_statement(rng: random.Random, level: int, want: bool, avoid=(), avoid_x=()):
    pool: dict[str, list] = {}
    for s in statements_of(level, want):
        if s in avoid or s[1] in avoid_x:
            continue
        pool.setdefault(s[0], []).append(s)
    if not pool:
        return None
    cats = [c for c in CATEGORY_WEIGHTS[level] if c in pool]
    if not cats:
        cats = list(pool)
    cat = rng.choices(cats, weights=[CATEGORY_WEIGHTS[level].get(c, 5) for c in cats])[0]
    return rng.choice(pool[cat])


def stmt_classes(s):
    """Классы, о которых говорит утверждение (для навыков)."""
    if s[0] in ("all", "none"):
        return [s[1], s[2]]
    if s[0] == "if":
        return [s[1], s[3]]
    return [s[1]]


# ====================================================================================================
# 2. name — «Назови фигуру по описанию»
# ====================================================================================================

# (описание, правильный ответ, пояснение для решения)
DESCS = {
    1: [
        ("Четырёхугольник, у которого противоположные стороны попарно параллельны", "par", "Это и есть определение параллелограмма."),
        ("Параллелограмм, у которого все углы прямые", "rect", "Это определение прямоугольника."),
        ("Параллелограмм, у которого все стороны равны", "rhomb", "Это определение ромба."),
        ("Прямоугольник, у которого все стороны равны", "square", "Это определение квадрата."),
        ("Четырёхугольник, у которого две стороны параллельны, а две другие не параллельны", "trap", "Это определение трапеции."),
        ("Четырёхугольник, у которого ровно одна пара сторон параллельна", "trap", "Ровно одна пара параллельных сторон — это трапеция."),
        ("Трапеция, у которой боковые стороны равны", "iso", "Трапеция с равными боковыми сторонами называется равнобедренной."),
        ("Трапеция, у которой есть прямой угол", "rtrap", "Трапеция с прямым углом называется прямоугольной."),
        ("Параллелограмм, у которого все стороны равны и все углы прямые", "square", "Прямые углы дают прямоугольник, равные стороны — ромб. Обе особенности сразу — квадрат."),
        ("Ромб, у которого все углы прямые", "square", "Ромб с прямыми углами — это прямоугольник с равными сторонами, то есть квадрат."),
        ("Параллелограмм с четырьмя прямыми углами", "rect", "Это определение прямоугольника."),
        ("Параллелограмм с четырьмя равными сторонами", "rhomb", "Это определение ромба."),
    ],
    2: [
        ("Четырёхугольник, у которого все стороны равны", "rhomb", "Если у четырёхугольника равны все четыре стороны, то противоположные стороны сами оказываются параллельными. Значит, это параллелограмм с равными сторонами — ромб."),
        ("Четырёхугольник, у которого все углы прямые", "rect", "Если все углы прямые, то соседние углы вместе дают 180°, и противоположные стороны параллельны. Значит, это параллелограмм с прямыми углами — прямоугольник."),
        ("Четырёхугольник, у которого все стороны равны и все углы прямые", "square", "Равные стороны дают ромб, прямые углы — прямоугольник. И то и другое сразу — квадрат."),
        ("Четырёхугольник, у которого противоположные стороны попарно параллельны и все стороны равны", "rhomb", "Параллельные противоположные стороны — параллелограмм, а с равными сторонами — ромб."),
        ("Четырёхугольник, у которого противоположные стороны попарно параллельны и все углы прямые", "rect", "Это параллелограмм с прямыми углами — прямоугольник."),
        ("Четырёхугольник, у которого противоположные стороны попарно параллельны, все стороны равны и все углы прямые", "square", "Параллелограмм с равными сторонами и прямыми углами — квадрат."),
        ("Четырёхугольник с четырьмя равными сторонами и четырьмя прямыми углами", "square", "Равные стороны и прямые углы сразу — квадрат."),
        ("Прямоугольник с четырьмя равными сторонами", "square", "Прямоугольник с равными сторонами — квадрат."),
        ("Ромб с четырьмя прямыми углами", "square", "Ромб с прямыми углами — квадрат."),
        ("Четырёхугольник с четырьмя прямыми углами", "rect", "Четыре прямых угла — это прямоугольник (противоположные стороны сами параллельны)."),
        ("Четырёхугольник с четырьмя равными сторонами", "rhomb", "Четыре равные стороны — это ромб (противоположные стороны сами параллельны)."),
        ("Четырёхугольник, у которого одна пара сторон параллельна и есть прямой угол", "rtrap", "Одна пара параллельных сторон — трапеция, а с прямым углом — прямоугольная трапеция."),
    ],
    3: [
        ("Параллелограмм, у которого есть прямой угол", "rect", "Соседние углы параллелограмма вместе дают 180°, поэтому рядом с прямым углом тоже прямой, а противоположные углы им равны. Все четыре угла прямые — прямоугольник. Стороны при этом могут быть разными, поэтому «квадрат» сказать нельзя."),
        ("Ромб, у которого есть прямой угол", "square", "Ромб — параллелограмм, а у параллелограмма с одним прямым углом все углы прямые. Ромб с прямыми углами — квадрат."),
        ("Параллелограмм, у которого один угол прямой", "rect", "Один прямой угол в параллелограмме делает прямыми все четыре (соседние дают 180°, противоположные равны). Стороны могут быть разными — это прямоугольник."),
        ("Параллелограмм, у которого есть две равные соседние стороны", "rhomb", "Противоположные стороны параллелограмма равны, поэтому при двух равных соседних сторонах равны все четыре. Углы могут быть любыми — это ромб, но не обязательно квадрат."),
        ("Прямоугольник, у которого есть две равные соседние стороны", "square", "У прямоугольника противоположные стороны равны, поэтому с двумя равными соседними сторонами равны все четыре. Это квадрат."),
        ("Четырёхугольник, у которого только одна пара параллельных сторон, а боковые стороны равны", "iso", "Одна пара параллельных сторон — трапеция, а равные боковые стороны делают её равнобедренной."),
        ("Четырёхугольник, который одновременно является ромбом и прямоугольником", "square", "Ромб — все стороны равны, прямоугольник — все углы прямые. Обе особенности сразу — квадрат."),
        ("Четырёхугольник, у которого ровно одна пара сторон параллельна и есть прямой угол", "rtrap", "Ровно одна пара параллельных сторон — трапеция, а с прямым углом — прямоугольная трапеция."),
        ("Параллелограмм, у которого один угол прямой и две соседние стороны равны", "square", "Прямой угол даёт прямоугольник, равные соседние стороны — ромб. Обе особенности сразу — квадрат."),
        ("Фигура, которая одновременно является и прямоугольником, и ромбом", "square", "Прямоугольник — все углы прямые, ромб — все стороны равны. Обе особенности сразу — квадрат."),
    ],
}

CLOSE = {
    "par": ["rect", "rhomb", "trap", "square"],
    "rect": ["par", "rhomb", "square", "trap"],
    "rhomb": ["par", "rect", "square", "trap"],
    "square": ["rect", "rhomb", "par", "trap"],
    "trap": ["par", "rect", "rhomb", "square"],
    "iso": ["trap", "rtrap", "par"],
    "rtrap": ["trap", "iso", "rect"],
}


def g_name(rng: random.Random, level: int):
    text, ans, why = rng.choice(DESCS[level])
    prompt = f"Какую фигуру описывает определение: «{text}»? Выберите самое точное название."
    lrng = random.Random(prompt)
    opts = [ans] + lrng.sample(CLOSE[ans], 3)
    lrng.shuffle(opts)
    options = [nom(k) for k in opts]
    right = opts.index(ans)
    # самопроверка по таблице: набор «атомов» описания совпадает с классом ответа
    sol = ["Выпишем, что сказано в описании, и вспомним определения.", why, f"Ответ: **{nom(ans)}**."]
    return task(prompt, str(right), "choice",
                "Вспомни «семейное дерево»: с чего начинается определение и что к нему добавили. Нужно самое точное название.",
                sol, skills_for(ans), options=options, geo={"kind": "name"})


# ====================================================================================================
# 3. tf и which
# ====================================================================================================

def g_tf(rng: random.Random, level: int):
    want = rng.random() < 0.5
    s = pick_statement(rng, level, want)
    if s is None:
        return None
    note = " " + CONV if conv_note([s]) else ""
    prompt = f"Верно ли утверждение: «{stmt_text(s)[:-1]}»?{note}"
    sol = [f"Утверждение: «{stmt_text(s)}»", explain(s), "Ответ: **" + ("да, верно" if truth(s) else "нет, неверно") + "**."]
    return task(prompt, "0" if truth(s) else "1", "choice",
                "Если утверждение начинается со слов «всякий», «каждый» или «любой», то достаточно найти один пример, который ему противоречит.",
                sol, skills_for(*stmt_classes(s)), options=["Да, верно", "Нет, неверно"], geo={"kind": "tf"})


def subset_text(sub: tuple[int, ...], n: int) -> str:
    if not sub:
        return "ни одно"
    if len(sub) == n:
        return "все три" if n == 3 else "все четыре"
    if len(sub) == 1:
        return f"только {sub[0]}"
    if len(sub) == 2:
        return f"{sub[0]} и {sub[1]}"
    return f"{', '.join(map(str, sub[:-1]))} и {sub[-1]}"


def g_which(rng: random.Random, level: int):
    n = 3 if level < 3 else 4
    k_true = rng.choice([1, 2] if n == 3 else [1, 2, 3])
    if level == 2 and n == 3:
        k_true = rng.choice([1, 2, 2, 3])
    chosen: list = []
    for want, cnt in ((True, k_true), (False, n - k_true)):
        for _ in range(cnt):
            # утверждения берём того же уровня, а для разнообразия на уровне 3 подмешиваем второй уровень
            lv = level if (level < 3 or rng.random() < 0.75) else 2
            s = pick_statement(rng, lv, want, avoid=chosen, avoid_x={c[1] for c in chosen})
            if s is None or any(s[:3] == c[:3] for c in chosen):
                return None
            chosen.append(s)
    order = list(range(n))
    rng.shuffle(order)
    stmts = [chosen[i] for i in order]
    true_idx = tuple(i + 1 for i, s in enumerate(stmts) if truth(s))
    note = CONV + " " if conv_note(stmts) else ""
    body = " ".join(f"**{i + 1})** {stmt_text(s)}" for i, s in enumerate(stmts))
    prompt = f"Какие из утверждений верны? {note}{body}"
    # варианты ответа: верный и три правдоподобных (отличаются от верного одним утверждением)
    allsets = [tuple(c) for r in range(0, n + 1) for c in itertools.combinations(range(1, n + 1), r)]
    near = [c for c in allsets if c != true_idx and len(set(c) ^ set(true_idx)) == 1 and c != ()]
    far = [c for c in allsets if c != true_idx and c not in near and c != ()]
    lrng = random.Random(prompt)
    lrng.shuffle(near)
    lrng.shuffle(far)
    wrong = (near + far)[:3]
    opts = sorted([true_idx] + wrong, key=lambda c: (len(c), c))
    options = [subset_text(c, n) for c in opts]
    right = opts.index(true_idx)
    sol = []
    for i, s in enumerate(stmts):
        sol.append(f"**{i + 1})** {'верно' if truth(s) else 'неверно'}. {explain(s)}")
    sol.append(f"Верные утверждения: **{subset_text(true_idx, n)}**.")
    cls = [c for s in stmts for c in stmt_classes(s)]
    return task(prompt, str(right), "choice", "Проверяй утверждения по одному, отдельно друг от друга. Для «неверно» ищи пример, который ему противоречит.",
                sol, skills_for(*cls), options=options, geo={"kind": "which"})


# ====================================================================================================
# 4. рисунки: координаты фигур для QuadFig
# ====================================================================================================

def r2(x: float) -> float:
    return round(x + 0.0, 2)


def flat(pts) -> list:
    return [r2(c) for p in pts for c in p]


def fig_quad(pts, **props):
    p = {"pts": flat(pts)}
    p.update(props)
    return {"id": "quad", "props": p}


def poly_from_angles(angs):
    """Выпуклый четырёхугольник с заданными углами (в градусах, сумма 360): список из 4 точек или None."""
    a, b, c, d = (math.radians(x) for x in angs)
    th = [0.0, math.pi - b, 2 * math.pi - b - c, 3 * math.pi - b - c - d]
    u = [(math.cos(t), math.sin(t)) for t in th]
    best = None
    for t in (0.5, 0.65, 0.8, 1.0, 1.25, 1.6, 2.0, 2.5):
        rx, ry = -(u[0][0] + t * u[1][0]), -(u[0][1] + t * u[1][1])
        det = u[2][0] * u[3][1] - u[2][1] * u[3][0]
        if abs(det) < 1e-9:
            continue
        x = (rx * u[3][1] - ry * u[3][0]) / det
        y = (u[2][0] * ry - u[2][1] * rx) / det
        if x <= 0.2 or y <= 0.2:
            continue
        lens = [1.0, t, x, y]
        score = min(lens) / max(lens)
        if best is None or score > best[0]:
            best = (score, lens)
    if best is None:
        return None
    lens = best[1]
    pts = [(0.0, 0.0)]
    for i in range(3):
        pts.append((pts[-1][0] + lens[i] * u[i][0], pts[-1][1] + lens[i] * u[i][1]))
    return [(4 * x, 4 * y) for x, y in pts]


def par_pts(a: float, b: float, ang: float):
    """Параллелограмм ABCD: AB = a, AD = b, угол A = ang (в градусах)."""
    t = math.radians(ang)
    d = (b * math.cos(t), b * math.sin(t))
    return [(0.0, 0.0), (a, 0.0), (a + d[0], d[1]), (d[0], d[1])]


def trap_pts(b1: float, b2: float, c: float, d: float):
    """Трапеция: нижнее основание AD = b1 (длиннее), верхнее BC = b2, боковые AB = c, CD = d. Порядок вершин A, B, C, D."""
    e = b1 - b2
    xb = (c * c - d * d + e * e) / (2 * e)
    h2 = c * c - xb * xb
    if h2 <= 1e-9:
        return None
    h = math.sqrt(h2)
    return [(0.0, 0.0), (xb, h), (xb + b2, h), (b1, 0.0)]


def trap_by_angles(a_deg: float, d_deg: float, top: float = 2.6, h: float = 3.0):
    """Трапеция ABCD (основания AD снизу и BC сверху) с углами A и D при нижнем основании. Порядок вершин A, B, C, D."""
    a, d = math.radians(a_deg), math.radians(d_deg)
    b_len, c_len = h / math.sin(a), h / math.sin(d)
    bx = b_len * math.cos(a)
    dx = top + bx + c_len * math.cos(d)
    return [(0.0, 0.0), (bx, h), (bx + top, h), (dx, 0.0)]


# ====================================================================================================
# 5. angle4 — «Сумма углов четырёхугольника»
# ====================================================================================================

def g_angle4(rng: random.Random, level: int):
    kinds = {1: ["gen", "gen", "gen3", "eq3"], 2: ["par", "rhomb", "rtrap", "ratio", "two90", "par"], 3: ["trap", "par_sum", "par_diff", "par_k", "par_sum3", "ap", "ratio3"]}[level]
    kind = rng.choice(kinds)
    ABCD = "ABCD"
    if kind == "gen":
        a, b, c = (rng.randrange(60, 131, 5) for _ in range(3))
        d = 360 - a - b - c
        if not 40 <= d <= 150:
            return None
        angs = [a, b, c, d]
        ask = rng.choice([3, 3, 3, 0, 1, 2])
        known = [i for i in range(4) if i != ask]
        pts = poly_from_angles(angs)
        if pts is None:
            return None
        labels = [f"{angs[i]}°" if i != ask else "?" for i in range(4)]
        given = ", ".join(f"$\\angle {ABCD[i]}={angs[i]}^\\circ$" for i in known)
        prompt = f"В четырёхугольнике $ABCD$ {given}. Найдите $\\angle {ABCD[ask]}$."
        sol = [f"Сумма углов четырёхугольника равна $360^\\circ$.",
               f"Три угла вместе: ${'+'.join(str(angs[i]) for i in known)}={sum(angs[i] for i in known)}$ (градусов).",
               f"Четвёртый угол: $\\angle {ABCD[ask]}=360^\\circ-{sum(angs[i] for i in known)}^\\circ={angs[ask]}^\\circ$."]
        geo = {"kind": "gen", "angles": [angs[i] if i != ask else 0 for i in range(4)], "ask": ask}
        return task(prompt, str(angs[ask]), "expr", "Сумма всех четырёх углов четырёхугольника равна 360°. Сложи три известных угла и вычти из 360°.",
                    sol, ["geo-q-anglesum"], placeholder="ответ в градусах", fig=fig_quad(pts, angs=labels), geo=geo)
    if kind == "gen3":
        a, b, c = (rng.randrange(60, 131, 5) for _ in range(3))
        d = 360 - a - b - c
        if not 40 <= d <= 150:
            return None
        three = [a, b, c]
        rng.shuffle(three)
        prompt = f"Три угла выпуклого четырёхугольника равны ${three[0]}^\\circ$, ${three[1]}^\\circ$ и ${three[2]}^\\circ$. Найдите четвёртый угол."
        sol = ["Сумма углов четырёхугольника равна $360^\\circ$.", f"${three[0]}+{three[1]}+{three[2]}={a + b + c}$ (градусов).",
               f"Четвёртый угол: $360^\\circ-{a + b + c}^\\circ={d}^\\circ$."]
        geo = {"kind": "gen", "angles": three + [0], "ask": 3}
        return task(prompt, str(d), "expr", "Сумма всех четырёх углов четырёхугольника равна 360°.", sol, ["geo-q-anglesum"], placeholder="ответ в градусах", geo=geo)
    if kind == "eq3":
        a = rng.randrange(70, 111, 5)
        d = 360 - 3 * a
        if not 40 <= d <= 150 or a == d:
            return None
        prompt = f"Три угла четырёхугольника равны по ${a}^\\circ$. Найдите четвёртый угол."
        sol = ["Сумма углов четырёхугольника равна $360^\\circ$.", f"Три угла вместе: $3\\cdot {a}^\\circ={3 * a}^\\circ$.",
               f"Четвёртый угол: $360^\\circ-{3 * a}^\\circ={d}^\\circ$."]
        return task(prompt, str(d), "expr", "Сначала найди сумму трёх одинаковых углов, потом вычти её из 360°.", sol, ["geo-q-anglesum"],
                    placeholder="ответ в градусах", geo={"kind": "gen", "angles": [a, a, a, 0], "ask": 3})
    if kind == "two90":
        c = rng.randrange(50, 131, 5)
        d = 360 - 180 - c
        prompt = f"Два угла четырёхугольника прямые, третий угол равен ${c}^\\circ$. Найдите четвёртый угол."
        sol = ["Сумма углов четырёхугольника равна $360^\\circ$.", f"Два прямых угла: $90^\\circ+90^\\circ=180^\\circ$, третий ${c}^\\circ$.",
               f"Четвёртый угол: $360^\\circ-180^\\circ-{c}^\\circ={d}^\\circ$."]
        return task(prompt, str(d), "expr", "Сумма углов четырёхугольника равна 360°. Два прямых угла — это 180°.", sol, ["geo-q-anglesum"],
                    placeholder="ответ в градусах", geo={"kind": "gen", "angles": [90, 90, c, 0], "ask": 3})
    if kind in ("par", "rhomb"):
        al = rng.randrange(40, 86, 5) if rng.random() < 0.6 else rng.randrange(95, 141, 5)
        ask = rng.choice([1, 2, 3])
        other = 180 - al
        val = {1: other, 2: al, 3: other}[ask]
        if kind == "par":
            pts = par_pts(4, 2.6, al)
            what, skill = "параллелограмме", "geo-q-parallelogram"
            fig = fig_quad(pts, angs=[f"{al}°"] + ["?" if i == ask else "" for i in (1, 2, 3)], par1=[0, 2], par2=[1, 3])
        else:
            pts = par_pts(3, 3, al)
            what, skill = "ромбе", "geo-q-rhombus"
            fig = fig_quad(pts, angs=[f"{al}°"] + ["?" if i == ask else "" for i in (1, 2, 3)], eq1=[0, 1, 2, 3])
        prompt = f"В {what} $ABCD$ угол $A$ равен ${al}^\\circ$. Найдите угол ${ABCD[ask]}$."
        if ask == 2:
            sol = [f"Противоположные углы параллелограмма равны: $\\angle C=\\angle A={al}^\\circ$.",
                   f"Проверка по сумме: ${al}+{other}+{al}+{other}=360$."]
        else:
            sol = [f"Соседние углы параллелограмма вместе дают $180^\\circ$ (стороны параллельны): $\\angle B=180^\\circ-{al}^\\circ={other}^\\circ$.",
                   ("Противоположные углы равны, поэтому $\\angle D=\\angle B$." if ask == 3 else "Проверим по сумме углов: $" + f"{al}+{other}+{al}+{other}=360$."),
                   f"Ответ: ${val}^\\circ$."]
        if kind == "rhomb":
            sol.insert(0, "Ромб — это параллелограмм, значит, у него те же свойства углов.")
        return task(prompt, str(val), "expr",
                    "Ромб и параллелограмм — «родственники»: соседние углы вместе дают 180°, противоположные равны. Можно проверить по сумме 360°." if kind == "rhomb"
                    else "Соседние углы параллелограмма вместе дают 180°, противоположные углы равны. Проверь суммой 360°.",
                    sol, ["geo-q-anglesum", skill], placeholder="ответ в градусах", fig=fig,
                    geo={"kind": kind, "A": al, "ask": ask})
    if kind == "rtrap":
        dd = rng.randrange(40, 86, 5)
        cc = 180 - dd
        c_len = 3.0
        base_d = 5.0
        pts = [(0.0, 0.0), (0.0, c_len * math.sin(math.radians(dd))), (base_d - c_len * math.cos(math.radians(dd)), c_len * math.sin(math.radians(dd))), (base_d, 0.0)]
        # порядок вершин A, B, C, D: AB — боковая сторона, перпендикулярная основаниям AD и BC
        prompt = f"$ABCD$ — прямоугольная трапеция с основаниями $AD$ и $BC$, углы $A$ и $B$ прямые. Угол $D$ равен ${dd}^\\circ$. Найдите угол $C$."
        sol = ["Два угла прямые: $\\angle A=\\angle B=90^\\circ$.", f"Сумма углов равна $360^\\circ$, поэтому $\\angle C=360^\\circ-90^\\circ-90^\\circ-{dd}^\\circ={cc}^\\circ$.",
               f"Другой способ: основания параллельны, поэтому $\\angle C+\\angle D=180^\\circ$, то есть $\\angle C={cc}^\\circ$."]
        return task(prompt, str(cc), "expr", "Два угла по 90° уже известны, сумма всех углов 360°.", sol, ["geo-q-anglesum", "geo-q-trapezoid"], placeholder="ответ в градусах",
                    fig=fig_quad(pts, rt=[0, 1], par1=[1, 3], angs=["", "", "?", f"{dd}°"]), geo={"kind": "rtrap", "D": dd})
    if kind == "ratio":
        w = rng.choice([[1, 2, 3, 4], [2, 3, 3, 4], [1, 1, 2, 2], [1, 2, 4, 5], [2, 3, 4, 6], [1, 3, 4, 4], [3, 4, 5, 6]])
        if 360 % sum(w):
            return None
        ask = rng.choice(["max", "min"])
        x = 360 // sum(w)
        val = x * (max(w) if ask == "max" else min(w))
        ratio = ":".join(map(str, w))
        prompt = f"Углы выпуклого четырёхугольника относятся как ${ratio}$. Найдите {'наибольший' if ask == 'max' else 'наименьший'} угол."
        sol = [f"Пусть на одну часть приходится $x$ градусов. Тогда сумма углов: ${'+'.join(str(i) + 'x' for i in w)}={sum(w)}x=360^\\circ$.",
               f"Отсюда $x=360^\\circ:{sum(w)}={x}^\\circ$.",
               f"{'Наибольший' if ask == 'max' else 'Наименьший'} угол: ${max(w) if ask == 'max' else min(w)}\\cdot {x}^\\circ={val}^\\circ$."]
        return task(prompt, str(val), "expr", "Сумма всех «частей» — это 360°. Найди, сколько градусов приходится на одну часть.", sol, ["geo-q-anglesum"],
                    placeholder="ответ в градусах", geo={"kind": "ratio", "w": w, "ask": ask})
    if kind == "trap":
        a_, d_ = rng.randrange(55, 91, 5), rng.randrange(60, 101, 5)
        ask = rng.choice(["B", "C"])
        val = 180 - a_ if ask == "B" else 180 - d_
        prompt = f"В трапеции $ABCD$ основания $AD$ и $BC$. Угол $A$ равен ${a_}^\\circ$, угол $D$ равен ${d_}^\\circ$. Найдите угол ${ask}$."
        near, nearv = ("A", a_) if ask == "B" else ("D", d_)
        sol = ["Основания $AD$ и $BC$ параллельны, а боковая сторона — секущая. Поэтому два угла при одной боковой стороне вместе дают $180^\\circ$.",
               f"Угол ${ask}$ стоит рядом с углом ${near}$ у боковой стороны {'$AB$' if ask == 'B' else '$CD$'}: $\\angle {ask}=180^\\circ-{nearv}^\\circ={val}^\\circ$.",
               "Сумма $360^\\circ$ здесь сразу не поможет: из четырёх углов известны только два."]
        pts = trap_by_angles(a_, d_)
        return task(prompt, str(val), "expr", "Основания параллельны, значит, два угла при одной боковой стороне вместе дают 180°.", sol, ["geo-q-anglesum", "geo-q-trapezoid"],
                    placeholder="ответ в градусах", fig=fig_quad(pts, par1=[1, 3], angs=[f"{a_}°", "?" if ask == "B" else "", "?" if ask == "C" else "", f"{d_}°"]),
                    geo={"kind": "trap", "A": a_, "D": d_, "ask": ask})
    if kind == "par_sum":
        s = rng.randrange(60, 161, 20)
        val = (360 - s) // 2
        prompt = f"Сумма двух противоположных углов параллелограмма равна ${s}^\\circ$. Найдите один из двух других углов."
        sol = ["Противоположные углы параллелограмма равны, поэтому каждый из двух данных углов равен " + f"${s}^\\circ:2={s // 2}^\\circ$.",
               f"Все четыре угла вместе дают $360^\\circ$, на два других остаётся $360^\\circ-{s}^\\circ={360 - s}^\\circ$.",
               f"Они тоже равны друг другу: ${360 - s}^\\circ:2={val}^\\circ$."]
        return task(prompt, str(val), "expr", "Противоположные углы параллелограмма равны. Вся сумма — 360°.", sol, ["geo-q-anglesum", "geo-q-parallelogram"],
                    placeholder="ответ в градусах", geo={"kind": "par_sum", "s": s})
    if kind == "par_diff":
        d = rng.randrange(20, 101, 10)
        val = (180 - d) // 2
        prompt = f"Разность двух соседних углов параллелограмма равна ${d}^\\circ$. Найдите меньший угол."
        sol = ["Соседние углы параллелограмма вместе дают $180^\\circ$.", f"Пусть меньший угол $x$, тогда больший $x+{d}^\\circ$ и $x+(x+{d}^\\circ)=180^\\circ$.",
               f"$2x=180^\\circ-{d}^\\circ={180 - d}^\\circ$, значит, $x={val}^\\circ$."]
        return task(prompt, str(val), "expr", "Два соседних угла вместе дают 180°. Если один на d больше другого, вычти d из суммы и раздели пополам.", sol,
                    ["geo-q-anglesum", "geo-q-parallelogram"], placeholder="ответ в градусах", geo={"kind": "par_diff", "d": d})
    if kind == "par_k":
        k = rng.choice([2, 3, 4, 5, 8, 9])
        small = 180 // (k + 1)
        if 180 % (k + 1):
            return None
        val = small * k
        word = {2: "вдвое", 3: "втрое", 4: "в 4 раза", 5: "в 5 раз", 8: "в 8 раз", 9: "в 9 раз"}[k]
        prompt = f"Один угол параллелограмма {word} меньше соседнего с ним. Найдите больший угол."
        sol = ["Соседние углы параллелограмма вместе дают $180^\\circ$.", f"Пусть меньший угол $x$, тогда больший ${k}x$ и $x+{k}x={k + 1}x=180^\\circ$.",
               f"$x=180^\\circ:{k + 1}={small}^\\circ$, больший угол ${k}\\cdot {small}^\\circ={val}^\\circ$."]
        return task(prompt, str(val), "expr", "Соседние углы вместе дают 180°. Меньший угол — одна часть, больший — несколько таких частей.", sol,
                    ["geo-q-anglesum", "geo-q-parallelogram"], placeholder="ответ в градусах", geo={"kind": "par_k", "k": k})
    if kind == "par_sum3":
        al = rng.randrange(50, 86, 5)
        s = 180 + al if rng.random() < 0.5 else 180 + (180 - al)
        val = max(s - 180, 360 - s)
        prompt = f"Сумма трёх углов параллелограмма равна ${s}^\\circ$. Найдите наибольший угол этого параллелограмма."
        x = s - 180
        sol = ["Углы параллелограмма: два равных острых (или прямых) и два равных тупых; соседние углы вместе дают $180^\\circ$.",
               f"Из трёх названных углов два равны друг другу (противоположные), третий — их «сосед». Если равные углы по $x$, то третий $180^\\circ-x$, и сумма $2x+180^\\circ-x=180^\\circ+x$.",
               f"Значит, $x={s}^\\circ-180^\\circ={x}^\\circ$, а оставшиеся два угла по $180^\\circ-{x}^\\circ={180 - x}^\\circ$.",
               f"Наибольший угол: ${val}^\\circ$."]
        return task(prompt, str(val), "expr", "В параллелограмме два разных значения угла: x и 180° − x. Из трёх углов два обязательно одинаковые.", sol,
                    ["geo-q-anglesum", "geo-q-parallelogram"], placeholder="ответ в градусах", geo={"kind": "par_sum3", "s": s})
    if kind == "ap":
        step = rng.choice([10, 20, 30])
        x = (360 - 6 * step) // 4
        if (360 - 6 * step) % 4 or x < 20:
            return None
        ask = rng.choice(["min", "max"])
        val = x if ask == "min" else x + 3 * step
        prompt = f"Углы выпуклого четырёхугольника идут в порядке возрастания, и каждый следующий на ${step}^\\circ$ больше предыдущего. Найдите {'наименьший' if ask == 'min' else 'наибольший'} угол."
        sol = [f"Пусть наименьший угол $x$. Тогда углы: $x$, $x+{step}^\\circ$, $x+{2 * step}^\\circ$, $x+{3 * step}^\\circ$.",
               f"Их сумма: $4x+{6 * step}^\\circ=360^\\circ$, значит, $4x={360 - 6 * step}^\\circ$ и $x={x}^\\circ$.",
               f"{'Наименьший' if ask == 'min' else 'Наибольший'} угол равен ${val}^\\circ$."]
        return task(prompt, str(val), "expr", "Обозначь наименьший угол за x и выпиши все четыре угла через x. Их сумма равна 360°.", sol, ["geo-q-anglesum"],
                    placeholder="ответ в градусах", geo={"kind": "ap", "step": step, "ask": ask})
    if kind == "ratio3":
        w = rng.choice([[1, 2, 4, 5], [2, 3, 3, 4], [1, 3, 4, 4], [2, 2, 3, 5], [3, 4, 5, 6]])
        if 360 % sum(w):
            return None
        x = 360 // sum(w)
        ask = rng.choice(["max", "min"])
        val = x * (max(w) if ask == "max" else min(w))
        pair = rng.choice([(0, 1), (1, 2), (2, 3)])
        prompt = f"Углы четырёхугольника $ABCD$ относятся как $\\angle A:\\angle B:\\angle C:\\angle D={':'.join(map(str, w))}$. Найдите {'наибольший' if ask == 'max' else 'наименьший'} угол."
        sol = [f"Пусть $\\angle A={w[0]}x$, $\\angle B={w[1]}x$, $\\angle C={w[2]}x$, $\\angle D={w[3]}x$.", f"${sum(w)}x=360^\\circ$, отсюда $x={x}^\\circ$.",
               f"{'Наибольший' if ask == 'max' else 'Наименьший'} угол: ${max(w) if ask == 'max' else min(w)}\\cdot {x}^\\circ={val}^\\circ$."]
        _ = pair
        return task(prompt, str(val), "expr", "Сумма частей даёт 360°. Найди одну часть, потом нужный угол.", sol, ["geo-q-anglesum"], placeholder="ответ в градусах",
                    geo={"kind": "ratio", "w": w, "ask": ask})
    return None


# ====================================================================================================
# 6. perim — «Периметр»
# ====================================================================================================

def _val(rng, lo, hi, dec_ok):
    """Целое или с «,5»."""
    v = rng.randint(lo, hi)
    if dec_ok and rng.random() < 0.4:
        return Fraction(2 * v + 1, 2)
    return Fraction(v)


def g_perim(rng: random.Random, level: int):
    kinds = {1: ["rhomb", "rect", "quad", "square", "rect"], 2: ["rhomb_rev", "rect_rev", "par", "par_rev", "trap", "rect", "rhomb"],
             3: ["par_diag", "iso", "rect_ratio", "rhomb_diag", "par_mult", "sq_eq_rect", "rect_cut", "trap_rev"]}[level]
    kind = rng.choice(kinds)
    dec_ok = level >= 2
    if kind == "rhomb":
        a = _val(rng, 3, 12, dec_ok)
        P = 4 * a
        prompt = f"Сторона ромба равна ${num(a)}$ см. Найдите периметр ромба."
        pts = par_pts(3, 3, 70)
        sol = ["У ромба все четыре стороны равны.", f"$P=4\\cdot {num(a)}={num(P)}$ (см)."]
        return task(prompt, dec(P), "expr", "Периметр — сумма длин всех сторон. У ромба все стороны равны.", sol, ["geo-q-perimeter", "geo-q-rhombus"],
                    placeholder="ответ в сантиметрах", fig=fig_quad(pts, eq1=[0, 1, 2, 3], sides=[f"{txt(a)} см", "", "", ""]), geo={"kind": "rhomb", "a": str(a)})
    if kind == "square":
        a = _val(rng, 3, 12, dec_ok)
        P = 4 * a
        prompt = f"Сторона квадрата равна ${num(a)}$ см. Найдите периметр квадрата."
        sol = ["У квадрата все четыре стороны равны.", f"$P=4\\cdot {num(a)}={num(P)}$ (см)."]
        return task(prompt, dec(P), "expr", "У квадрата все стороны равны.", sol, ["geo-q-perimeter", "geo-q-square"], placeholder="ответ в сантиметрах",
                    fig=fig_quad([(0, 0), (3, 0), (3, 3), (0, 3)], eq1=[0, 1, 2, 3], rt=[0, 1, 2, 3], sides=[f"{txt(a)} см", "", "", ""]), geo={"kind": "square", "a": str(a)})
    if kind == "rect":
        a, b = _val(rng, 3, 12, dec_ok), _val(rng, 2, 9, dec_ok)
        if a == b:
            return None
        P = 2 * (a + b)
        prompt = f"Стороны прямоугольника равны ${num(a)}$ см и ${num(b)}$ см. Найдите периметр прямоугольника."
        sol = ["У прямоугольника противоположные стороны равны, поэтому в периметр входят по две стороны каждой длины.",
               f"$P=2\\cdot ({num(a)}+{num(b)})={num(P)}$ (см)."]
        w, h = (3.6, 2.2) if a > b else (2.2, 3.6)
        return task(prompt, dec(P), "expr", "Периметр — сумма всех четырёх сторон. Противоположные стороны прямоугольника равны.", sol, ["geo-q-perimeter", "geo-q-rectangle"],
                    placeholder="ответ в сантиметрах", fig=fig_quad([(0, 0), (w, 0), (w, h), (0, h)], rt=[0, 1, 2, 3], sides=[f"{txt(a)} см", f"{txt(b)} см", "", ""]),
                    geo={"kind": "rect", "a": str(a), "b": str(b)})
    if kind == "quad":
        s = [rng.randint(3, 9) for _ in range(4)]
        if max(s) >= sum(s) - max(s):
            return None
        P = sum(s)
        prompt = f"Стороны четырёхугольника $ABCD$: $AB={s[0]}$ см, $BC={s[1]}$ см, $CD={s[2]}$ см, $DA={s[3]}$ см. Найдите периметр."
        sol = ["Периметр — сумма длин всех сторон.", f"$P={'+'.join(map(str, s))}={P}$ (см)."]
        return task(prompt, str(P), "expr", "Сложи длины всех четырёх сторон.", sol, ["geo-q-perimeter"], placeholder="ответ в сантиметрах",
                    fig=fig_quad(poly_from_angles([85, 100, 80, 95]), sides=[f"{x} см" for x in s]), geo={"kind": "quad", "s": s})
    if kind == "par":
        a, b = _val(rng, 4, 12, dec_ok), _val(rng, 2, 8, dec_ok)
        if a == b:
            return None
        P = 2 * (a + b)
        prompt = f"В параллелограмме $ABCD$ сторона $AB$ равна ${num(a)}$ см, а сторона $AD$ равна ${num(b)}$ см. Найдите периметр параллелограмма."
        sol = ["У параллелограмма противоположные стороны равны: $CD=AB$ и $BC=AD$.", f"$P=2\\cdot (AB+AD)=2\\cdot ({num(a)}+{num(b)})={num(P)}$ (см)."]
        return task(prompt, dec(P), "expr", "Противоположные стороны параллелограмма равны, поэтому нужно удвоить сумму двух соседних сторон.", sol,
                    ["geo-q-perimeter", "geo-q-parallelogram"], placeholder="ответ в сантиметрах",
                    fig=fig_quad(par_pts(4, 2.2, 65), par1=[0, 2], par2=[1, 3], sides=[f"{txt(a)} см", "", "", f"{txt(b)} см"]), geo={"kind": "par", "a": str(a), "b": str(b)})
    if kind == "rhomb_rev":
        a = _val(rng, 3, 15, True)
        P = 4 * a
        prompt = f"Периметр ромба равен ${num(P)}$ см. Найдите сторону ромба."
        sol = ["У ромба все четыре стороны равны, поэтому периметр в 4 раза больше стороны.", f"$a=P:4={num(P)}:4={num(a)}$ (см)."]
        return task(prompt, dec(a), "expr", "Периметр ромба — это четыре равные стороны.", sol, ["geo-q-perimeter", "geo-q-rhombus"], placeholder="ответ в сантиметрах",
                    fig=fig_quad(par_pts(3, 3, 70), eq1=[0, 1, 2, 3], sides=["?", "", "", ""]), geo={"kind": "rhomb_rev", "P": str(P)})
    if kind == "rect_rev":
        a, b = _val(rng, 4, 12, dec_ok), _val(rng, 2, 8, dec_ok)
        if a == b:
            return None
        P = 2 * (a + b)
        prompt = f"Периметр прямоугольника равен ${num(P)}$ см, одна из его сторон равна ${num(a)}$ см. Найдите другую сторону."
        sol = ["Периметр прямоугольника равен удвоенной сумме двух соседних сторон.", f"${num(a)}+x={num(P)}:2={num(P / 2)}$, значит, $x={num(b)}$ (см)."]
        return task(prompt, dec(b), "expr", "Раздели периметр пополам — получится сумма двух соседних сторон.", sol, ["geo-q-perimeter", "geo-q-rectangle"],
                    placeholder="ответ в сантиметрах", fig=fig_quad([(0, 0), (3.4, 0), (3.4, 2.2), (0, 2.2)], rt=[0, 1, 2, 3], sides=[f"{txt(a)} см", "?", "", ""]),
                    geo={"kind": "rect_rev", "P": str(P), "a": str(a)})
    if kind == "par_rev":
        a, b = _val(rng, 4, 12, dec_ok), _val(rng, 2, 9, dec_ok)
        if a == b:
            return None
        P = 2 * (a + b)
        prompt = f"Периметр параллелограмма $ABCD$ равен ${num(P)}$ см, сторона $AB$ равна ${num(a)}$ см. Найдите сторону $BC$."
        sol = ["У параллелограмма противоположные стороны равны, поэтому $P=2\\cdot (AB+BC)$.", f"$AB+BC={num(P)}:2={num(P / 2)}$, значит, $BC={num(P / 2)}-{num(a)}={num(b)}$ (см)."]
        return task(prompt, dec(b), "expr", "Раздели периметр пополам — получится сумма двух соседних сторон.", sol, ["geo-q-perimeter", "geo-q-parallelogram"],
                    placeholder="ответ в сантиметрах", fig=fig_quad(par_pts(4, 2.2, 65), par1=[0, 2], par2=[1, 3], sides=[f"{txt(a)} см", "?", "", ""]),
                    geo={"kind": "par_rev", "P": str(P), "a": str(a)})
    if kind == "trap":
        b1, b2 = rng.randint(8, 16), rng.randint(3, 7)
        c, d = rng.randint(4, 9), rng.randint(4, 9)
        e = b1 - b2
        if not (abs(c - d) < e < c + d):
            return None
        P = b1 + b2 + c + d
        prompt = f"Основания трапеции равны ${b1}$ см и ${b2}$ см, а боковые стороны — ${c}$ см и ${d}$ см. Найдите периметр трапеции."
        sol = ["Периметр — сумма длин всех четырёх сторон: двух оснований и двух боковых сторон.", f"$P={b1}+{b2}+{c}+{d}={P}$ (см)."]
        pts = trap_pts(b1, b2, c, d)
        if pts is None:
            return None
        return task(prompt, str(P), "expr", "Сложи основания и боковые стороны.", sol, ["geo-q-perimeter", "geo-q-trapezoid"], placeholder="ответ в сантиметрах",
                    fig=fig_quad(pts, par1=[1, 3], sides=[f"{c} см", f"{b2} см", f"{d} см", f"{b1} см"]), geo={"kind": "trap", "bases": [b1, b2], "legs": [c, d]})
    if kind == "trap_rev":
        b1, b2 = rng.randint(8, 16), rng.randint(3, 7)
        c, d = rng.randint(4, 9), rng.randint(4, 9)
        if c == d or not (abs(c - d) < b1 - b2 < c + d):
            return None
        P = b1 + b2 + c + d
        prompt = f"Периметр трапеции равен ${P}$ см, её основания равны ${b1}$ см и ${b2}$ см, а одна из боковых сторон равна ${c}$ см. Найдите другую боковую сторону."
        sol = ["Периметр — сумма двух оснований и двух боковых сторон.", f"Основания и одна боковая сторона вместе: ${b1}+{b2}+{c}={b1 + b2 + c}$ (см).",
               f"На вторую боковую сторону остаётся ${P}-{b1 + b2 + c}={d}$ (см)."]
        return task(prompt, str(d), "expr", "Из периметра вычти всё, что уже известно: два основания и одну боковую сторону.", sol, ["geo-q-perimeter", "geo-q-trapezoid"],
                    placeholder="ответ в сантиметрах", fig=fig_quad(trap_pts(b1, b2, c, d), par1=[1, 3], sides=[f"{c} см", f"{b2} см", "?", f"{b1} см"]),
                    geo={"kind": "trap_rev", "P": P, "bases": [b1, b2], "leg": c})
    if kind == "par_diag":
        a, b = rng.randint(4, 10), rng.randint(5, 12)
        if a == b:
            return None
        d = rng.randint(abs(a - b) + 1, a + b - 1)
        P = 2 * (a + b)
        prompt = f"В параллелограмме $ABCD$ известно: $AB={a}$ см, $BC={b}$ см, диагональ $AC={d}$ см. Найдите периметр параллелограмма."
        sol = ["Периметр параллелограмма — сумма всех его сторон. Диагональ — не сторона, в периметр она не входит.",
               "Противоположные стороны равны: $CD=AB$, $AD=BC$.", f"$P=2\\cdot ({a}+{b})={P}$ (см)."]
        return task(prompt, str(P), "expr", "Диагональ в периметр не входит. Противоположные стороны параллелограмма равны.", sol, ["geo-q-perimeter", "geo-q-parallelogram"],
                    placeholder="ответ в сантиметрах", fig=fig_quad(par_pts(4, 2.4, 62), par1=[0, 2], par2=[1, 3], diag=[0, 2], sides=[f"{a} см", f"{b} см", "", ""]),
                    geo={"kind": "par_diag", "a": a, "b": b, "d": d})
    if kind == "iso":
        h = rng.choice([(3, 4, 5), (6, 8, 10), (5, 12, 13)])
        half, hh, leg = h
        b2 = rng.randint(3, 8)
        b1 = b2 + 2 * half
        P = b1 + b2 + 2 * leg
        prompt = f"Основания равнобедренной трапеции равны ${b2}$ см и ${b1}$ см, а боковая сторона равна ${leg}$ см. Найдите периметр трапеции."
        sol = [f"У равнобедренной трапеции боковые стороны равны, значит, вторая боковая сторона тоже ${leg}$ см.",
               f"$P={b1}+{b2}+{leg}+{leg}={P}$ (см)."]
        pts = trap_pts(b1, b2, leg, leg)
        return task(prompt, str(P), "expr", "Боковых сторон у трапеции две. В условии названа только одна, а про другую подумай.", sol, ["geo-q-perimeter", "geo-q-trapezoid"],
                    placeholder="ответ в сантиметрах", fig=fig_quad(pts, par1=[1, 3], eq1=[0, 2], sides=["", f"{b2} см", f"{leg} см", f"{b1} см"]),
                    geo={"kind": "iso", "bases": [b2, b1], "leg": leg})
    if kind == "rect_ratio":
        x = rng.randint(2, 9)
        w = rng.choice([(2, 3), (3, 4), (2, 5), (1, 3), (3, 5)])
        P = 2 * x * (w[0] + w[1])
        prompt = f"Стороны прямоугольника относятся как ${w[0]}:{w[1]}$, а периметр равен ${P}$ см. Найдите большую сторону."
        val = x * w[1]
        sol = [f"Пусть стороны ${w[0]}x$ и ${w[1]}x$. Периметр: $2\\cdot ({w[0]}x+{w[1]}x)={2 * (w[0] + w[1])}x={P}$.", f"Отсюда $x={P}:{2 * (w[0] + w[1])}={x}$.",
               f"Большая сторона: ${w[1]}\\cdot {x}={val}$ (см)."]
        return task(prompt, str(val), "expr", "Полупериметр — это сумма двух соседних сторон, то есть всех «частей» вместе.", sol, ["geo-q-perimeter", "geo-q-rectangle"],
                    placeholder="ответ в сантиметрах", geo={"kind": "rect_ratio", "P": P, "w": list(w)})
    if kind == "rhomb_diag":
        t = rng.choice([(3, 4, 5), (6, 8, 10), (5, 12, 13)])
        d1, d2, a = 2 * t[0], 2 * t[1], t[2]
        P = 4 * a
        prompt = f"Диагонали ромба равны ${d1}$ см и ${d2}$ см, а его сторона равна ${a}$ см. Найдите периметр ромба."
        sol = ["Диагонали в периметр не входят: периметр состоит из сторон.", "У ромба все четыре стороны равны.", f"$P=4\\cdot {a}={P}$ (см)."]
        return task(prompt, str(P), "expr", "Диагонали — лишние данные: периметр — это четыре стороны ромба.", sol, ["geo-q-perimeter", "geo-q-rhombus"], placeholder="ответ в сантиметрах",
                    geo={"kind": "rhomb_diag", "a": a, "d1": d1, "d2": d2})
    if kind == "par_mult":
        k = rng.choice([2, 3, 4])
        a = rng.randint(3, 9)
        P = 2 * (a + k * a)
        word = {2: "вдвое", 3: "втрое", 4: "в 4 раза"}[k]
        prompt = f"Периметр параллелограмма равен ${P}$ см. Одна его сторона {word} больше соседней. Найдите меньшую сторону."
        sol = [f"Пусть меньшая сторона $x$, тогда соседняя ${k}x$.", f"Периметр: $2\\cdot (x+{k}x)={2 * (k + 1)}x={P}$.", f"$x={P}:{2 * (k + 1)}={a}$ (см)."]
        return task(prompt, str(a), "expr", "Периметр — это две меньшие и две большие стороны. Сначала найди сумму двух соседних сторон.", sol,
                    ["geo-q-perimeter", "geo-q-parallelogram"], placeholder="ответ в сантиметрах", geo={"kind": "par_mult", "P": P, "k": k})
    if kind == "sq_eq_rect":
        a, b = rng.choice([(12, 6), (10, 6), (14, 6), (15, 9), (9, 3), (11, 5)])
        P = 2 * (a + b)
        if P % 4:
            return None
        s = P // 4
        prompt = f"Периметр квадрата равен периметру прямоугольника со сторонами ${a}$ см и ${b}$ см. Найдите сторону квадрата."
        sol = [f"Периметр прямоугольника: $2\\cdot ({a}+{b})={P}$ (см).", f"У квадрата все стороны равны, поэтому его сторона ${P}:4={s}$ (см)."]
        return task(prompt, str(s), "expr", "Сначала найди периметр прямоугольника, потом раздели на 4.", sol, ["geo-q-perimeter", "geo-q-square"], placeholder="ответ в сантиметрах",
                    geo={"kind": "sq_eq_rect", "a": a, "b": b})
    if kind == "rect_cut":
        a = rng.choice([6, 8, 10, 12, 14])
        b = rng.randint(3, 9)
        if a == b:
            return None
        P = a + 2 * b
        prompt = f"Прямоугольник со сторонами ${a}$ см и ${b}$ см разрезали на два равных прямоугольника, разделив пополам сторону длиной ${a}$ см. Найдите периметр одного из двух получившихся прямоугольников."
        sol = [f"Каждая часть — прямоугольник со сторонами ${a}:2={a // 2}$ см и ${b}$ см.", f"$P=2\\cdot ({a // 2}+{b})={P}$ (см).",
               f"Заметь: это не половина периметра исходного прямоугольника, ведь появилась новая сторона разреза."]
        return task(prompt, str(P), "expr", "Нарисуй обе части: у каждой появилась новая сторона — линия разреза.", sol, ["geo-q-perimeter", "geo-q-rectangle"], placeholder="ответ в сантиметрах",
                    geo={"kind": "rect_cut", "a": a, "b": b})
    return None


# ====================================================================================================
# 7. coord — «Какая это фигура по координатам вершин»
# ====================================================================================================

COORD_NAMES = ["параллелограмм", "прямоугольник", "ромб", "квадрат", "трапеция", "просто четырёхугольник"]
COORD_KEY = {"par": 0, "rect": 1, "rhomb": 2, "square": 3, "trap": 4, "quad": 5}


def classify_gen(P) -> str:
    """Самое точное название по угловым коэффициентам и квадратам длин (способ генератора)."""
    def slope(a, b):
        dx, dy = b[0] - a[0], b[1] - a[1]
        return None if dx == 0 else Fraction(dy, dx)

    def perp(s1, s2):
        if s1 is None or s2 is None:
            return (s1 is None and s2 == 0) or (s2 is None and s1 == 0)
        return s1 * s2 == -1

    sl = [slope(P[i], P[(i + 1) % 4]) for i in range(4)]
    ln = [(P[(i + 1) % 4][0] - P[i][0]) ** 2 + (P[(i + 1) % 4][1] - P[i][1]) ** 2 for i in range(4)]
    p02, p13 = sl[0] == sl[2], sl[1] == sl[3]
    if p02 and p13:
        right = perp(sl[0], sl[1])
        eq = ln[0] == ln[1]
        return "square" if right and eq else "rect" if right else "rhomb" if eq else "par"
    if p02 != p13:
        return "trap"
    return "quad"


def convex_gen(P) -> bool:
    """Выпуклость: диагонали пересекаются внутри (способ генератора)."""
    def side(a, b, c):
        v = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
        return (v > 0) - (v < 0)

    a, b, c, d = P
    return side(a, c, b) * side(a, c, d) < 0 and side(b, d, a) * side(b, d, c) < 0


def _rot(u):
    """Поворот «шага» (a; b) на 90° против часовой стрелки: (−b; a)."""
    return (-u[1], u[0])


def _shape(rng: random.Random, kind: str):
    """Точки фигуры нужного вида (обход против часовой стрелки)."""
    if kind == "rect":
        w, h = rng.sample(range(2, 7), 2)
        return [(0, 0), (w, 0), (w, h), (0, h)]
    if kind == "square":
        s = rng.randint(2, 5)
        return [(0, 0), (s, 0), (s, s), (0, s)]
    if kind == "par_h":
        w, h = rng.randint(3, 6), rng.randint(2, 4)
        k = rng.choice([-2, -1, 1, 2, 3])
        return None if w * w == k * k + h * h else [(0, 0), (w, 0), (w + k, h), (k, h)]
    if kind == "trap_h":
        b1 = rng.randint(4, 8)
        b2 = rng.randint(2, b1 - 1)
        s = rng.randint(0, b1 - b2)
        h = rng.randint(2, 4)
        return [(0, 0), (b1, 0), (s + b2, h), (s, h)]
    if kind == "rhomb_diag":
        p, q = rng.sample(range(1, 5), 2)
        return [(p, 0), (2 * p, q), (p, 2 * q), (0, q)]
    if kind == "rhomb_shear":
        w, k, h = rng.choice([(5, 3, 4), (5, 4, 3), (10, 6, 8), (5, -3, 4), (5, -4, 3)])
        return [(0, 0), (w, 0), (w + k, h), (k, h)]
    if kind == "square_tilt":
        u = rng.choice([(2, 1), (1, 2), (3, 1), (1, 3), (3, 2), (2, 3)])
        v = _rot(u)
        return [(0, 0), u, (u[0] + v[0], u[1] + v[1]), v]
    if kind == "rect_tilt":
        u = rng.choice([(2, 1), (1, 2), (3, 1), (1, 3)])
        m = rng.choice([2, 3])
        v = (m * _rot(u)[0], m * _rot(u)[1])
        return [(0, 0), u, (u[0] + v[0], u[1] + v[1]), v]
    if kind == "par_slant":
        u = rng.choice([(3, 1), (2, 1), (4, 1), (3, 2), (4, -1)])
        v = rng.choice([(1, 3), (-1, 2), (1, 2), (-2, 3), (1, 4)])
        if u[0] * v[1] - u[1] * v[0] == 0 or u[0] ** 2 + u[1] ** 2 == v[0] ** 2 + v[1] ** 2 or u[0] * v[0] + u[1] * v[1] == 0:
            return None
        return [(0, 0), u, (u[0] + v[0], u[1] + v[1]), v]
    if kind == "trap_slant":
        u = rng.choice([(2, 1), (3, 1), (1, 1), (2, -1), (1, 2)])
        v = rng.choice([(-1, 3), (1, 3), (0, 3), (-2, 2), (1, 2), (-1, 2)])
        m1, m2 = rng.sample([1, 2, 3], 2)
        return [(0, 0), (m1 * u[0], m1 * u[1]), (v[0] + m2 * u[0], v[1] + m2 * u[1]), v]
    if kind == "kite":  # «воздушный змей»: две пары равных соседних сторон, параллельных сторон нет
        a, b = rng.randint(1, 3), rng.randint(1, 3)
        c = rng.randint(b + 1, b + 4)
        return None if c == 2 * b else [(a, 0), (2 * a, b), (a, c), (0, b)]
    if kind == "quad_rand":
        for _ in range(60):
            P = [(rng.randint(0, 7), rng.randint(0, 6)) for _ in range(4)]
            if len(set(P)) == 4 and convex_gen(P) and classify_gen(P) == "quad":
                return P
        return None
    if kind == "par_look_trap":  # параллелограмм, очень «скошенный»: на трапецию похож
        w, h, k = rng.randint(4, 7), rng.randint(2, 3), rng.randint(3, 5)
        return None if w * w == k * k + h * h else [(0, 0), (w, 0), (w + k, h), (k, h)]
    if kind == "trap_look_par":  # трапеция, похожая на параллелограмм: основания отличаются на единицу
        b1 = rng.randint(5, 8)
        s = rng.randint(1, 3)
        h = rng.randint(2, 3)
        return [(0, 0), (b1, 0), (s + b1 - 1, h), (s, h)]
    if kind == "rect_look_sq":
        s = rng.randint(3, 5)
        return [(0, 0), (s, 0), (s, s + 1), (0, s + 1)]
    if kind == "rhomb_look_sq":
        p = rng.randint(2, 4)
        return [(p, 0), (2 * p, p + 1), (p, 2 * p + 2), (0, p + 1)]
    return None


# (вид фигуры, правильное название, вес)
KINDS_BY_LEVEL = {
    1: [("rect", "rect", 2), ("square", "square", 2), ("par_h", "par", 2), ("trap_h", "trap", 2), ("quad_rand", "quad", 1)],
    2: [("rhomb_diag", "rhomb", 2), ("square_tilt", "square", 1), ("rect_tilt", "rect", 2), ("par_slant", "par", 2), ("trap_slant", "trap", 2), ("quad_rand", "quad", 1),
        ("rhomb_shear", "rhomb", 1)],
    3: [("square_tilt", "square", 2), ("rhomb_shear", "rhomb", 1), ("kite", "quad", 2), ("par_look_trap", "par", 2), ("trap_look_par", "trap", 2), ("rect_look_sq", "rect", 2),
        ("rhomb_look_sq", "rhomb", 2), ("rect_tilt", "rect", 1), ("trap_slant", "trap", 1)],
}

HOW = {
    "par": "Обе пары противоположных сторон параллельны, углы не прямые и соседние стороны разные: это **параллелограмм**.",
    "rect": "Параллелограмм с прямыми углами, у которого соседние стороны разные: это **прямоугольник**.",
    "rhomb": "Параллелограмм с равными сторонами и непрямыми углами: это **ромб**.",
    "square": "Параллелограмм с прямыми углами и равными сторонами: это **квадрат**.",
    "trap": "Параллельна ровно одна пара сторон: это **трапеция**.",
    "quad": "Нет ни одной пары параллельных сторон: это **просто четырёхугольник**.",
}


def _par_line(steps, i, j, names) -> str:
    """Фраза о том, параллельны ли стороны i и j, по их «шагам»."""
    u, v = steps[i], steps[j]
    n1, n2 = names[i], names[j]
    if u[0] * v[1] - u[1] * v[0] != 0:
        return f"${n1}$ и ${n2}$: шаги $({u[0]};{u[1]})$ и $({v[0]};{v[1]})$ идут в разные стороны, стороны **не параллельны**."
    k = Fraction(v[0], u[0]) if u[0] != 0 else Fraction(v[1], u[1])
    if k == -1:
        return f"${n1}$ и ${n2}$: шаги $({u[0]};{u[1]})$ и $({v[0]};{v[1]})$ отличаются только знаками, стороны **параллельны** (и равны)."
    return f"${n1}$ и ${n2}$: шаги $({u[0]};{u[1]})$ и $({v[0]};{v[1]})$ — один получается из другого умножением на ${num(k)}$, стороны **параллельны**."


def g_coord(rng: random.Random, level: int):
    options_ = KINDS_BY_LEVEL[level]
    shape_kind, ans, _w = rng.choices(options_, weights=[o[2] for o in options_])[0]
    P = _shape(rng, shape_kind)
    if P is None or len(set(P)) != 4:
        return None
    if classify_gen(P) != ans or not convex_gen(P):
        return None
    # случайный перенос в [-3; 8], сдвиг номеров вершин и зеркало
    xs, ys = [p[0] for p in P], [p[1] for p in P]
    if max(xs) - min(xs) > 10 or max(ys) - min(ys) > 10:
        return None
    ox = rng.randint(-3 - min(xs), 8 - max(xs))
    oy = rng.randint(-3 - min(ys), 8 - max(ys))
    P = [(x + ox, y + oy) for x, y in P]
    r = rng.randint(0, 3)
    P = P[r:] + P[:r]
    if rng.random() < 0.5:
        P = [P[0]] + P[1:][::-1]
    ab = "ABCD"
    pts_txt = ", ".join(f"${ab[i]}({P[i][0]};{P[i][1]})$" for i in range(4))
    prompt = f"Четырёхугольник $ABCD$ задан координатами вершин: {pts_txt}. Какая это фигура? Выберите самое точное название."
    steps = [(P[(i + 1) % 4][0] - P[i][0], P[(i + 1) % 4][1] - P[i][1]) for i in range(4)]
    names = ["AB", "BC", "CD", "DA"]
    sol = ["Найдём «шаги» от вершины к вершине (на сколько вправо и на сколько вверх): " +
           ", ".join(f"${names[i]}$: $({steps[i][0]};{steps[i][1]})$" for i in range(4)) + "."]
    cr = lambda a, b: a[0] * b[1] - a[1] * b[0]
    sol.append("Параллельность. " + _par_line(steps, 0, 2, names) + " " + _par_line(steps, 1, 3, names))
    sq = [s[0] ** 2 + s[1] ** 2 for s in steps]
    sol.append("Квадраты длин сторон (сумма квадратов шагов): " + ", ".join(f"${names[i]}^2={steps[i][0] ** 2}+{steps[i][1] ** 2}={sq[i]}$" for i in range(4)) + ".")
    if cr(steps[0], steps[2]) == 0 and cr(steps[1], steps[3]) == 0:
        d0 = steps[0][0] * steps[1][0] + steps[0][1] * steps[1][1]
        sol.append(f"Угол $B$: шаги $AB$ и $BC$, $({steps[0][0]})\\cdot ({steps[1][0]})+({steps[0][1]})\\cdot ({steps[1][1]})={d0}$ — "
                   + ("ноль, значит, угол прямой." if d0 == 0 else "не ноль, значит, угол не прямой."))
    sol.append(HOW[ans])
    return task(prompt, str(COORD_KEY[ans]), "choice",
                "Выпиши «шаги» от каждой вершины к следующей. У параллельных сторон шаги «в одну линию». Квадрат длины стороны — сумма квадратов её шагов.",
                sol, ["geo-q-coords", SKILL_OF[ans], "geo-q-family"], options=COORD_NAMES, fig=fig_quad(P, grid=True), geo={"kind": "coord"})


# ====================================================================================================
# 8. ⭐ subtle — «Тонкие вопросы»
# ====================================================================================================

def g_subtle(rng: random.Random, level: int):
    kind = rng.choices(["count", "opp_sum", "diff", "k", "sum3", "grid_sq", "grid_rect", "tri_per", "tri_rev", "rhomb60", "rtrap"],
                       weights=[34, 8, 6, 6, 6, 6, 6, 8, 6, 2, 2])[0]
    if kind == "count":
        k = rng.choice([5, 5, 6])
        items = rng.sample(KEYS, k)
        y = rng.choice(["par", "rect", "rhomb", "trap", "square", "quad"])
        good = [x for x in items if members(x) <= members(y)]
        if not 1 <= len(good) <= k - 1:
            return None
        names = ", ".join(nom(x) for x in items)
        note = " " + CONV if (y in TRAPF and any(x in PARF for x in items)) else ""
        prompt = (f"Даны фигуры: {names}. Сколько из них обязательно являются {insp(y)}? "
                  f"(«Обязательно» — значит, что подойдёт любая фигура такого вида.){note}")
        sol = ["Для каждой фигуры спрашиваем: верно ли, что **любая** такая фигура — " + nom(y) + "? Идём вверх по семейному дереву.",
               "Подходят: " + ", ".join(nom(x) for x in items if x in good) + ".", "Не подходят: " + ", ".join(nom(x) for x in items if x not in good) + ".",
               f"Всего подходит: {len(good)}."]
        return task(prompt, str(len(good)), "expr", "Для каждой фигуры мысленно проверь: есть ли хоть один пример такой фигуры, который не подходит? Если есть, она не считается.",
                    sol, skills_for(y, *items) + ["geo-q-subtle"], placeholder="ответ числом", geo={"kind": "count"})
    if kind == "opp_sum":
        s = rng.randrange(60, 161, 20)
        val = 360 - s
        prompt = f"Сумма двух противоположных углов параллелограмма равна ${s}^\\circ$. Чему равна сумма двух других его углов?"
        sol = ["Противоположные углы параллелограмма равны: два данных угла по " + f"${s // 2}^\\circ$.", f"Сумма всех углов $360^\\circ$, поэтому на два других приходится $360^\\circ-{s}^\\circ={val}^\\circ$.",
               "Они тоже равны друг другу (по " + f"${val // 2}^\\circ$), но спрашивают про их сумму: ${val}^\\circ$."]
        return task(prompt, str(val), "expr", "Вся сумма углов — 360°. Сколько осталось на оставшиеся два угла?", sol, ["geo-q-anglesum", "geo-q-parallelogram", "geo-q-subtle"],
                    placeholder="ответ в градусах", geo={"kind": "opp_sum", "s": s})
    if kind == "diff":
        d = rng.randrange(20, 101, 10)
        val = (180 + d) // 2
        prompt = f"Разность двух соседних углов параллелограмма равна ${d}^\\circ$. Найдите больший угол."
        sol = ["Соседние углы параллелограмма вместе дают $180^\\circ$.", f"Пусть меньший $x$, больший $x+{d}^\\circ$: $2x+{d}^\\circ=180^\\circ$, $x={(180 - d) // 2}^\\circ$.",
               f"Больший угол: ${(180 - d) // 2}^\\circ+{d}^\\circ={val}^\\circ$."]
        return task(prompt, str(val), "expr", "Два соседних угла вместе дают 180°, а разность известна.", sol, ["geo-q-anglesum", "geo-q-parallelogram", "geo-q-subtle"],
                    placeholder="ответ в градусах", geo={"kind": "par_diff_big", "d": d})
    if kind == "k":
        k = rng.choice([2, 3, 4, 5, 8])
        small = 180 // (k + 1)
        if 180 % (k + 1):
            return None
        word = {2: "вдвое", 3: "втрое", 4: "в 4 раза", 5: "в 5 раз", 8: "в 8 раз"}[k]
        prompt = f"Один из углов параллелограмма {word} больше другого. Найдите острый угол этого параллелограмма."
        sol = ["Углы у параллелограмма двух видов: острые (или прямые) и тупые; соседние вместе дают $180^\\circ$.",
               f"Пусть острый угол $x$, тупой ${k}x$: $x+{k}x=180^\\circ$, значит, $x={small}^\\circ$."]
        return task(prompt, str(small), "expr", "Не забудь, что соседние углы вместе дают 180°, а «другие» два угла в параллелограмме им равны.", sol,
                    ["geo-q-anglesum", "geo-q-parallelogram", "geo-q-subtle"], placeholder="ответ в градусах", geo={"kind": "par_k_small", "k": k})
    if kind == "sum3":
        al = rng.randrange(40, 86, 5)
        s = 180 + al
        prompt = f"Сумма трёх углов параллелограмма равна ${s}^\\circ$. Найдите его острый угол."
        sol = ["В параллелограмме два разных значения угла: $x$ и $180^\\circ-x$, каждое встречается дважды.",
               f"Три угла — это $x$, $x$ и $180^\\circ-x$ (или наоборот). Сумма $180^\\circ+x={s}^\\circ$ при $x={al}^\\circ$ (острый угол).",
               f"Проверка: углы ${al}^\\circ$, ${180 - al}^\\circ$, ${al}^\\circ$, ${180 - al}^\\circ$, три из них дают ${al + 180 - al + al}^\\circ$."]
        return task(prompt, str(al), "expr", "Из трёх углов два обязательно равны (противоположные). Пусть они по x, третий — 180° − x.", sol,
                    ["geo-q-anglesum", "geo-q-parallelogram", "geo-q-subtle"], placeholder="ответ в градусах", geo={"kind": "par_sum3_acute", "s": s})
    if kind == "grid_sq":
        m, n = rng.randint(2, 5), rng.randint(2, 5)
        if m > n:
            m, n = n, m
        if m == n and rng.random() < 0.5:
            return None
        total = sum((m - i) * (n - i) for i in range(m))
        prompt = f"Прямоугольник составлен из ${m}\\times {n}$ клеток (единичных квадратиков). Сколько всего квадратов (любых размеров) можно найти на этом рисунке?"
        parts = " + ".join(f"{(m - i) * (n - i)}" for i in range(m))
        sol = ["Считаем квадраты по длине стороны (в клетках): " + f"со стороной 1 — ${m * n}$ шт." + "".join(f"; со стороной {i + 1} — ${(m - i) * (n - i)}$ шт." for i in range(1, m)),
               f"Всего: ${parts}={total}$."]
        return task(prompt, str(total), "expr", "Считай по порядку: сначала самые маленькие квадраты, потом со стороной 2 клетки, и так далее.", sol,
                    ["geo-q-square", "geo-q-subtle"], placeholder="ответ числом", geo={"kind": "grid_sq", "m": m, "n": n})
    if kind == "grid_rect":
        m, n = rng.randint(2, 4), rng.randint(2, 4)
        if m > n:
            m, n = n, m
        total = (m * (m + 1) // 2) * (n * (n + 1) // 2)
        prompt = f"Прямоугольник составлен из ${m}\\times {n}$ клеток (единичных квадратиков). Сколько всего прямоугольников можно найти на этом рисунке? (Квадрат тоже прямоугольник.)"
        sol = ["Прямоугольник задаётся двумя вертикальными и двумя горизонтальными линиями сетки.",
               f"Выбрать две вертикальные линии из ${m + 1}$ можно ${m * (m + 1) // 2}$ способами, две горизонтальные из ${n + 1}$ — ${n * (n + 1) // 2}$ способами.",
               f"Всего: ${m * (m + 1) // 2}\\cdot {n * (n + 1) // 2}={total}$."]
        return task(prompt, str(total), "expr", "Прямоугольник задают две вертикальные и две горизонтальные линии сетки.", sol, ["geo-q-rectangle", "geo-q-square", "geo-q-subtle"],
                    placeholder="ответ числом", geo={"kind": "grid_rect", "m": m, "n": n})
    if kind == "tri_per":
        a, b = rng.randint(4, 12), rng.randint(5, 14)
        if a == b:
            return None
        d = rng.randint(abs(a - b) + 1, a + b - 1)
        P = 2 * (a + b)
        val = a + b + d
        prompt = f"Периметр параллелограмма $ABCD$ равен ${P}$ см, а диагональ $AC$ равна ${d}$ см. Найдите периметр треугольника $ABC$."
        sol = ["Стороны треугольника $ABC$: $AB$, $BC$ и диагональ $AC$.", f"У параллелограмма $AB+BC$ — это половина периметра: ${P}:2={P // 2}$ см.", f"$P_{{ABC}}=AB+BC+AC={P // 2}+{d}={val}$ (см)."]
        return task(prompt, str(val), "expr", "Две стороны треугольника ABC — соседние стороны параллелограмма, вместе они составляют половину периметра.", sol,
                    ["geo-q-perimeter", "geo-q-parallelogram", "geo-q-subtle"], placeholder="ответ в сантиметрах", geo={"kind": "tri_per", "a": a, "b": b, "d": d, "P": P})
    if kind == "tri_rev":
        a, b = rng.randint(4, 12), rng.randint(5, 14)
        if a == b:
            return None
        d = rng.randint(abs(a - b) + 1, a + b - 1)
        T = a + b + d
        prompt = f"В параллелограмме $ABCD$ стороны $AB={a}$ см и $AD={b}$ см. Периметр треугольника $ABD$ равен ${T}$ см. Найдите диагональ $BD$."
        sol = ["Стороны треугольника $ABD$: $AB$, $AD$ и диагональ $BD$.", f"$BD=P_{{ABD}}-AB-AD={T}-{a}-{b}={d}$ (см)."]
        return task(prompt, str(d), "expr", "Периметр треугольника ABD — это AB + AD + BD.", sol, ["geo-q-perimeter", "geo-q-parallelogram", "geo-q-subtle"],
                    placeholder="ответ в сантиметрах", geo={"kind": "tri_rev", "a": a, "b": b, "T": T})
    if kind == "rhomb60":
        prompt = "В ромбе $ABCD$ диагональ $BD$ равна стороне ромба. Найдите тупой угол ромба."
        sol = ["Треугольник $ABD$ имеет стороны $AB=AD=BD$: он равносторонний, поэтому $\\angle A=60^\\circ$.", "Соседние углы ромба (как и параллелограмма) вместе дают $180^\\circ$.",
               "Тупой угол: $180^\\circ-60^\\circ=120^\\circ$."]
        return task(prompt, "120", "expr", "Посмотри на треугольник ABD: какие у него стороны?", sol, ["geo-q-rhombus", "geo-q-anglesum", "geo-q-subtle"], placeholder="ответ в градусах", geo={"kind": "rhomb60"})
    if kind == "rtrap":
        prompt = "Сколько прямых углов у прямоугольной трапеции?"
        sol = ["Один прямой угол при боковой стороне. Основания параллельны, поэтому второй угол при этой же боковой стороне тоже $90^\\circ$ (вместе они дают $180^\\circ$).",
               "Углы при другой боковой стороне вместе дают $180^\\circ$, но по отдельности они не прямые (иначе получился бы прямоугольник).", "Итого прямых углов два."]
        return task(prompt, "2", "expr", "Основания параллельны. Что можно сказать про второй угол при той же боковой стороне?", sol, ["geo-q-trapezoid", "geo-q-subtle"],
                    placeholder="ответ числом", geo={"kind": "rtrap_count"})
    return None


GROUPS = [
    ("name", "Назови фигуру по описанию", g_name, 7),
    ("tf", "Верно ли утверждение?", g_tf, 7),
    ("which", "Какие утверждения верны?", g_which, 7),
    ("angle4", "Сумма углов четырёхугольника", g_angle4, 1),
    ("perim", "Периметр", g_perim, 0),
    ("coord", "Фигура по координатам вершин", g_coord, 7),
]
OLYMPIAD = [("subtle", "Тонкие вопросы", g_subtle, 8)]


# ====================================================================================================
# 9. verify — НЕЗАВИСИМАЯ проверка
# ====================================================================================================
# Ничего из таблицы фигур (ATOMS, DEF, PARENTS), из функций truth/explain/classify_gen здесь не используется.
#   * утверждения и описания разбираются по тексту условия;
#   * истина считается на модели: все выпуклые четырёхугольники с вершинами в узлах решётки 5×5
#     (целочисленные векторы: параллельность — векторное произведение, равенство сторон — квадраты длин, прямой угол — скалярное произведение);
#   * углы и периметры пересчитываются построением фигуры по координатам и перебором.

_MODEL: list | None = None


def _features(q):
    n = 4
    s = [(q[(i + 1) % n][0] - q[i][0], q[(i + 1) % n][1] - q[i][1]) for i in range(n)]
    turn = [s[i][0] * s[(i + 1) % n][1] - s[i][1] * s[(i + 1) % n][0] for i in range(n)]
    if not (all(t > 0 for t in turn) or all(t < 0 for t in turn)):
        return None  # не выпуклый (или вырожденный) четырёхугольник
    l2 = [v[0] ** 2 + v[1] ** 2 for v in s]
    dt = [s[i][0] * s[(i + 1) % n][0] + s[i][1] * s[(i + 1) % n][1] for i in range(n)]  # dt[i] == 0 — прямой угол в вершине i+1
    p02 = s[0][0] * s[2][1] - s[0][1] * s[2][0] == 0
    p13 = s[1][0] * s[3][1] - s[1][1] * s[3][0] == 0

    def same_angle(a, b):  # углы в вершинах a и b равны (косинусы сравниваем без корней)
        da, db = -dt[(a - 1) % n], -dt[(b - 1) % n]
        if (da > 0) - (da < 0) != (db > 0) - (db < 0):
            return False
        return da * da * l2[(b - 1) % n] * l2[b] == db * db * l2[(a - 1) % n] * l2[a]

    total = 0.0
    for j in range(n):
        c = -dt[(j - 1) % n] / math.sqrt(l2[(j - 1) % n] * l2[j])
        total += math.degrees(math.acos(max(-1.0, min(1.0, c))))
    return {
        "P2": p02 and p13, "P1": p02 != p13, "P0": not p02 and not p13,
        "EQ": len(set(l2)) == 1, "RA": all(d == 0 for d in dt), "R1": any(d == 0 for d in dt),
        "RC": sum(1 for d in dt if d == 0),
        "OPS": l2[0] == l2[2] and l2[1] == l2[3],
        "OPA": same_angle(0, 2) and same_angle(1, 3),
        "ADJ": any(l2[i] == l2[(i + 1) % n] for i in range(n)),
        "LEG": (p02 != p13) and ((l2[1] == l2[3]) if p02 else (l2[0] == l2[2])),
        "SUM": total,
    }


def _pred(name: str, f) -> bool:
    if name == "quad":
        return True
    if name == "par":
        return f["P2"]
    if name == "rect":
        return f["P2"] and f["RA"]
    if name == "rhomb":
        return f["P2"] and f["EQ"]
    if name == "square":
        return f["P2"] and f["RA"] and f["EQ"]
    if name == "trap":
        return f["P1"]
    if name == "iso":
        return f["P1"] and f["LEG"]
    if name == "rtrap":
        return f["P1"] and f["R1"]
    return f[name]


def _model() -> list:
    global _MODEL
    if _MODEL is None:
        n = 5
        pts = [(x, y) for x in range(n) for y in range(n)]
        figs = []
        for q in itertools.permutations(pts, 4):
            if q[0] != min(q) or q[1] > q[3]:  # один представитель из 8 (повороты нумерации и обход в другую сторону)
                continue
            f = _features(q)
            if f is not None:
                figs.append(f)
        # самопроверка модели: все виды встречаются и друг от друга отличаются
        sets = {k: frozenset(i for i, f in enumerate(figs) if _pred(k, f)) for k in ("quad", "par", "rect", "rhomb", "square", "trap", "iso", "rtrap")}
        if any(not v for v in sets.values()) or len(set(sets.values())) != len(sets):
            raise RuntimeError("модель решётки слишком бедная: какие-то виды фигур не встречаются или совпадают")
        if not any(f["P0"] and f["ADJ"] for f in figs):
            raise RuntimeError("в модели нет «воздушного змея»")
        _MODEL = figs
    return _MODEL


# ---- разбор текста ----

_CLS_RE = [
    (r"равнобедренн\w+ трапеци\w+", "iso"),
    (r"прямоугольн\w+ трапеци\w+", "rtrap"),
    (r"трапеци\w+", "trap"),
    (r"параллелограмм\w*", "par"),
    (r"прямоугольник\w*", "rect"),
    (r"ромб\w*", "rhomb"),
    (r"квадрат\w*", "square"),
    (r"(?:просто |выпуклого )?четырёхугольник\w*", "quad"),
]
_PROP_RE = [
    (r"противоположные стороны попарно параллельны", "P2"),
    (r"ровно одна пара сторон параллельна", "P1"),
    (r"все стороны равны", "EQ"),
    (r"все углы прямые", "RA"),
    (r"есть прямой угол", "R1"),
    (r"противоположные стороны равны", "OPS"),
    (r"противоположные углы равны", "OPA"),
    (r"боковые стороны равны", "LEG"),
    (r"есть две равные соседние стороны", "ADJ"),
    (r"нет параллельных сторон", "P0"),
]
_DESC_RE = [  # свободные формулировки в описаниях фигур
    (r"противоположные стороны попарно параллельны", "P2"),
    (r"две стороны параллельны, а две другие не параллельны", "P1"),
    (r"одна пара сторон параллельна", "P1"),
    (r"только одна пара параллельных сторон", "P1"),
    (r"все стороны равны", "EQ"),
    (r"четырьмя равными сторонами", "EQ"),
    (r"все углы прямые", "RA"),
    (r"четырьмя прямыми углами", "RA"),
    (r"есть прямой угол", "R1"),
    (r"один угол прямой", "R1"),
    (r"есть две равные соседние стороны", "ADJ"),
    (r"две соседние стороны равны", "ADJ"),
    (r"боковые стороны равны", "LEG"),
]


def _cls_full(s: str) -> str:
    s = s.strip().rstrip(".")
    for pat, key in _CLS_RE:
        if re.fullmatch(pat, s):
            return key
    raise ValueError(f"не разобрал название фигуры «{s}»")


def _cls_start(s: str):
    for pat, key in _CLS_RE:
        m = re.match(pat, s)
        if m:
            return key, s[m.end():].strip()
    raise ValueError(f"не разобрал начало «{s[:30]}»")


def _prop_full(s: str) -> str:
    s = s.strip().rstrip(".")
    for pat, key in _PROP_RE:
        if re.fullmatch(pat, s):
            return key
    raise ValueError(f"не разобрал свойство «{s}»")


def _sel(conds):
    return [f for f in _model() if all(_pred(c, f) for c in conds)]


def _forall(conds, concl) -> bool:
    sel = _sel(conds)
    if not sel:
        raise ValueError(f"в модели нет фигур с условием {conds}")
    return all(_pred(concl, f) for f in sel)


def _eval_stmt(text: str) -> bool:
    """Истинность одного утверждения: разбираем текст и считаем на модели."""
    text = text.strip()
    m = re.fullmatch(r"(?:Всякий|Всякая|Каждый|Каждая|Любой|Любая) (.+?) является (.+?)\.?", text)
    if m:
        return _forall([_cls_full(m.group(1))], _cls_full(m.group(2)))
    m = re.fullmatch(r"Ни (?:один|одна) (.+?) не является (.+?)\.?", text)
    if m:
        a, b = _cls_full(m.group(1)), _cls_full(m.group(2))
        if not _sel([a]):
            raise ValueError("пустой класс")
        return not _sel([a, b])
    m = re.fullmatch(r"У (?:всякого|всякой|каждого|каждой|любого|любой) (.+)", text)
    if m:
        x, rest = _cls_start(m.group(1))
        return _forall([x], _prop_full(rest))
    m = re.fullmatch(r"Существует (.+?), у (?:которого|которой) (.+?)\.?", text)
    if m:
        return bool(_sel([_cls_full(m.group(1)), _prop_full(m.group(2))]))
    m = re.fullmatch(r"Если у (.+?), то (?:он|она) является (.+?)\.?", text)
    if m:
        x, rest = _cls_start(m.group(1))
        return _forall([x, _prop_full(rest)], _cls_full(m.group(2)))
    m = re.fullmatch(r"Сумма углов (?:любого|любой) (.+?) равна (\d+)°\.?", text)
    if m:
        x = _cls_full(m.group(1))
        n_ = int(m.group(2))
        sel = _sel([x])
        if not sel:
            raise ValueError("пустой класс")
        return all(abs(f["SUM"] - n_) < 1e-9 for f in sel)
    raise ValueError(f"не разобрал утверждение «{text}»")


def _find_classes(text: str) -> list[str]:
    work = text
    found = []
    for pat, key in _CLS_RE:
        for m in re.finditer(pat, work, flags=re.I):
            found.append((m.start(), key))
            work = work[:m.start()] + " " * (m.end() - m.start()) + work[m.end():]
    return [k for _, k in sorted(found)]


def _require_choice(t, n_opts=None):
    if t.get("answerKind") != "choice":
        return "ожидался выбор ответа"
    opts = t.get("options") or []
    if n_opts and len(opts) != n_opts:
        return f"вариантов {len(opts)}, ожидали {n_opts}"
    if len(set(opts)) != len(opts):
        return "варианты ответа повторяются"
    if not (t["answer"].isdigit() and int(t["answer"]) < len(opts)):
        return f"ответ {t['answer']} вне списка вариантов"
    return None


def _v_name(t):
    bad = _require_choice(t)
    if bad:
        return bad
    m = re.search(r"«(.+?)»", t["prompt"])
    classes = _find_classes(m.group(1))
    props = [key for pat, key in _DESC_RE if re.search(pat, m.group(1))]
    conds = classes + props
    s = frozenset(i for i, f in enumerate(_model()) if all(_pred(c, f) for c in conds))
    if not s:
        return "описание задаёт пустое множество"
    keys = [_cls_full(o) for o in t["options"]]
    sets = [frozenset(i for i, f in enumerate(_model()) if _pred(k, f)) for k in keys]
    got = int(t["answer"])
    if s != sets[got]:
        return f"описание «{m.group(1)}» не совпадает с классом «{t['options'][got]}»"
    # «самое точное» название: среди вариантов, которым подходит каждая такая фигура, верный — самый маленький, и он один
    fits = [i for i, c in enumerate(sets) if s <= c]
    smallest = [i for i in fits if all(sets[i] <= sets[j] for j in fits)]
    if smallest != [got]:
        return f"самое точное название — вариант(ы) {smallest}, в ответе {got}"
    if len([i for i in range(len(sets)) if sets[i] == s]) != 1:
        return "два варианта означают одно и то же"
    return None


def _v_tf(t):
    bad = _require_choice(t, 2)
    if bad:
        return bad
    if t["options"] != ["Да, верно", "Нет, неверно"]:
        return "неожиданные варианты"
    stmt = re.search(r"«(.+?)»", t["prompt"]).group(1)
    tr = _eval_stmt(stmt + ".")
    want = "0" if tr else "1"
    return None if t["answer"] == want else f"«{stmt}»: на модели {'верно' if tr else 'неверно'}, в ответе {t['answer']}"


def _opt_set(text: str, n: int) -> frozenset:
    if text == "ни одно":
        return frozenset()
    if text.startswith("все"):
        if (text, n) not in (("все три", 3), ("все четыре", 4)):
            return frozenset({-1})
        return frozenset(range(1, n + 1))
    return frozenset(int(d) for d in re.findall(r"\d", text))


def _v_which(t):
    bad = _require_choice(t, 4)
    if bad:
        return bad
    stmts = re.findall(r"\*\*(\d)\)\*\*\s*(.+?)(?=\s*\*\*\d\)\*\*|$)", t["prompt"], flags=re.S)
    if [int(i) for i, _ in stmts] != list(range(1, len(stmts) + 1)) or len(stmts) not in (3, 4):
        return "утверждения пронумерованы неверно"
    truth_set = frozenset(int(i) for i, s in stmts if _eval_stmt(s))
    sets = [_opt_set(o, len(stmts)) for o in t["options"]]
    if len(set(sets)) != len(sets) or frozenset({-1}) in sets:
        return "варианты ответа повторяются или записаны неверно"
    if sets.count(truth_set) != 1:
        return f"верный набор {sorted(truth_set)}, подходящих вариантов {sets.count(truth_set)}"
    return None if sets[int(t["answer"])] == truth_set else f"верный набор {sorted(truth_set)}, в ответе вариант {t['answer']}: {t['options'][int(t['answer'])]}"


# ---- координаты ----

_V_COORD_NAMES = ["параллелограмм", "прямоугольник", "ромб", "квадрат", "трапеция", "просто четырёхугольник"]


def _v_coord(t):
    bad = _require_choice(t, 6)
    if bad:
        return bad
    if t["options"] != _V_COORD_NAMES:
        return "варианты ответа не те"
    pts = re.findall(r"([ABCD])\((-?\d+);(-?\d+)\)", t["prompt"])
    if [p[0] for p in pts] != list("ABCD"):
        return "в условии не четыре вершины"
    P = [(int(x), int(y)) for _, x, y in pts]
    fp = t.get("fig", {}).get("props", {}).get("pts")
    if fp != [float(c) for p in P for c in p]:
        return f"рисунок {fp} не совпадает с координатами в условии"
    f = _features(P)
    if f is None:
        return "четырёхугольник невыпуклый или вырожденный"
    if f["P2"]:
        name = "квадрат" if f["RA"] and f["EQ"] else "прямоугольник" if f["RA"] else "ромб" if f["EQ"] else "параллелограмм"
    elif f["P1"]:
        name = "трапеция"
    else:
        name = "просто четырёхугольник"
    return None if t["options"][int(t["answer"])] == name else f"по координатам это «{name}», в ответе «{t['options'][int(t['answer'])]}»"


# ---- углы ----

def _angle_at(P, j):
    p, q, r = P[(j - 1) % 4], P[j], P[(j + 1) % 4]
    ux, uy, vx, vy = p[0] - q[0], p[1] - q[1], r[0] - q[0], r[1] - q[1]
    c = (ux * vx + uy * vy) / (math.hypot(ux, uy) * math.hypot(vx, vy))
    return math.degrees(math.acos(max(-1.0, min(1.0, c))))


def _is_convex(P) -> bool:
    tr = []
    for i in range(4):
        a, b, c = P[i], P[(i + 1) % 4], P[(i + 2) % 4]
        tr.append((b[0] - a[0]) * (c[1] - b[1]) - (b[1] - a[1]) * (c[0] - b[0]))
    return all(x > 1e-9 for x in tr) or all(x < -1e-9 for x in tr)


def _measure_given_three(known):
    """Строим выпуклый четырёхугольник по трём известным углам V0, V1, V2 и измеряем угол при V3. None — такого нет."""
    a, b, c = (math.radians(x) for x in known)
    for tlen in (0.4, 0.6, 0.8, 1.0, 1.3, 1.7, 2.2, 3.0, 4.0):
        v0 = (0.0, 0.0)
        v1 = (1.0, 0.0)
        th1 = math.pi - b
        v2 = (v1[0] + tlen * math.cos(th1), v1[1] + tlen * math.sin(th1))
        th2 = th1 + math.pi - c
        # v0 + s*(cos a, sin a) = v2 + r*(cos th2, sin th2)
        d1, d2 = (math.cos(a), math.sin(a)), (math.cos(th2), math.sin(th2))
        det = d1[0] * (-d2[1]) - d1[1] * (-d2[0])
        if abs(det) < 1e-9:
            continue
        rx, ry = v2[0] - v0[0], v2[1] - v0[1]
        s_ = (rx * (-d2[1]) - ry * (-d2[0])) / det
        r_ = (d1[0] * ry - d1[1] * rx) / det
        if s_ <= 1e-6 or r_ <= 1e-6:
            continue
        v3 = (v0[0] + s_ * d1[0], v0[1] + s_ * d1[1])
        P = [v0, v1, v2, v3]
        if _is_convex(P):
            return _angle_at(P, 3)
    return None


def _par_angles(A_deg, a=4.0, b=2.6):
    t = math.radians(A_deg)
    d = (b * math.cos(t), b * math.sin(t))
    P = [(0.0, 0.0), (a, 0.0), (a + d[0], d[1]), d]
    return [_angle_at(P, j) for j in range(4)]


def _num_ok(x, want) -> bool:
    return abs(float(x) - float(want)) < 1e-6


def has_nums(t, *vals) -> bool:
    nums = _prompt_numbers(t["prompt"])
    return all(Fraction(v) in nums for v in vals)


_K_WORD = {2: "вдвое", 3: "втрое", 4: "в 4 раза", 5: "в 5 раз", 8: "в 8 раз", 9: "в 9 раз"}


def _v_angle4(t):
    g = t.get("geo") or {}
    k = g.get("kind")
    ans = Fraction(t["answer"])
    if k == "gen":
        ask = g["ask"]
        order = [(ask + 1) % 4, (ask + 2) % 4, (ask + 3) % 4]
        known = [g["angles"][i] for i in order]
        got = _measure_given_three(known)
        if got is None:
            return f"выпуклого четырёхугольника с углами {known} не построить"
        if not _num_ok(got, ans):
            return f"построение даёт {got:.3f}, в ответе {ans}"
        for angle in known:  # прямой угол в условии может быть назван словом
            if not (has_nums(t, angle) or (angle == 90 and "прям" in t["prompt"])):
                return "углы из условия не совпадают с данными задания"
        return None
    if k in ("par", "rhomb"):
        angs = _par_angles(g["A"], 4.0, 2.6 if k == "par" else 4.0)
        return None if _num_ok(angs[g["ask"]], ans) and has_nums(t, g["A"]) else f"построение даёт {angs[g['ask']]:.3f}, в ответе {ans}"
    if k == "rtrap":
        dd = math.radians(g["D"])
        L = 3.0
        h = L * math.sin(dd)
        P = [(0.0, 0.0), (0.0, h), (5.0 - L * math.cos(dd), h), (5.0, 0.0)]
        if not _is_convex(P) or abs(_angle_at(P, 0) - 90) > 1e-6 or abs(_angle_at(P, 1) - 90) > 1e-6 or abs(_angle_at(P, 3) - g["D"]) > 1e-6:
            return "построение прямоугольной трапеции не удалось"
        return None if _num_ok(_angle_at(P, 2), ans) and has_nums(t, g["D"]) else f"построение даёт {_angle_at(P, 2):.3f}, в ответе {ans}"
    if k == "trap":
        a_, d_ = math.radians(g["A"]), math.radians(g["D"])
        h = 3.0
        bx = h / math.sin(a_) * math.cos(a_)
        dx = h / math.sin(d_) * math.cos(d_)
        P = [(0.0, 0.0), (bx, h), (bx + 2.5, h), (bx + 2.5 + dx, 0.0)]
        if not _is_convex(P) or abs(_angle_at(P, 0) - g["A"]) > 1e-6 or abs(_angle_at(P, 3) - g["D"]) > 1e-6:
            return "построение трапеции не удалось"
        j = {"B": 1, "C": 2}[g["ask"]]
        return None if _num_ok(_angle_at(P, j), ans) and has_nums(t, g["A"], g["D"]) else f"построение даёт {_angle_at(P, j):.3f}, в ответе {ans}"
    if k == "ratio":
        x = Fraction(360, sum(g["w"]))
        want = x * (max(g["w"]) if g["ask"] == "max" else min(g["w"]))
        return None if want == ans and has_nums(t, *g["w"]) else f"пересчёт даёт {want}, в ответе {ans}"
    if k == "ap":
        x = (360 - 6 * Fraction(g["step"])) / 4
        want = x if g["ask"] == "min" else x + 3 * g["step"]
        return None if want == ans and has_nums(t, g["step"]) else f"пересчёт даёт {want}, в ответе {ans}"
    # параллелограмм: перебор угла A по построению, измеряем все четыре угла
    cands = []
    for A in range(1, 180):
        a4 = _par_angles(A)
        if k in ("par_sum", "opp_sum"):  # два противоположных угла (A и C) дают s
            if abs(a4[0] + a4[2] - g["s"]) < 1e-6:
                cands.append(a4[1] if k == "par_sum" else a4[1] + a4[3])
        elif k in ("par_diff", "par_diff_big"):
            if abs(abs(a4[0] - a4[1]) - g["d"]) < 1e-6:
                cands.append(min(a4[0], a4[1]) if k == "par_diff" else max(a4[0], a4[1]))
        elif k in ("par_k", "par_k_small"):
            small, big = min(a4[0], a4[1]), max(a4[0], a4[1])
            if abs(big - g["k"] * small) < 1e-6:
                cands.append(big if k == "par_k" else small)
        elif k in ("par_sum3", "par_sum3_acute"):
            if any(abs(sum(a4) - a4[drop] - g["s"]) < 1e-6 for drop in range(4)):
                cands.append(max(a4) if k == "par_sum3" else min(a4))
        else:
            return f"неизвестный вид {k}"
    cands = sorted({round(c, 6) for c in cands})
    if len(cands) != 1:
        return f"перебор даёт значения {cands}"
    if k in ("par_k", "par_k_small"):
        given_ok = _K_WORD[g["k"]] in t["prompt"]
    else:
        given_ok = has_nums(t, g.get("s", g.get("d")))
    return None if _num_ok(cands[0], ans) and given_ok else f"перебор даёт {cands[0]}, в ответе {ans}"


# ---- периметр и тонкие вопросы ----

def _prompt_numbers(text: str) -> list[Fraction]:
    clean = text.replace("{,}", ".").replace(",", ".")
    return [Fraction(x) for x in re.findall(r"\d+(?:\.\d+)?", clean)]


def _search(pred, lo=Fraction(1, 2), hi=200, step=Fraction(1, 2)):
    """Все x из [lo; hi] с шагом step, для которых pred(x). Перебор вместо формулы."""
    out = []
    x = lo
    while x <= hi:
        if pred(x):
            out.append(x)
        x += step
    return out


def _v_perim(t):
    g = t.get("geo") or {}
    k = g.get("kind")
    ans = Fraction(t["answer"])
    if k in ("rhomb", "square"):
        a = Fraction(g["a"])
        return None if has_nums(t, a) and sum([a, a, a, a]) == ans else f"сумма сторон {sum([a] * 4)}, в ответе {ans}"
    if k in ("rect", "par"):
        a, b = Fraction(g["a"]), Fraction(g["b"])
        return None if has_nums(t, a, b) and sum([a, b, a, b]) == ans else f"сумма сторон {sum([a, b, a, b])}, в ответе {ans}"
    if k == "quad":
        s = g["s"]
        if max(s) >= sum(s) - max(s):
            return "четырёхугольник с такими сторонами не существует"
        return None if has_nums(t, *s) and sum(s) == ans else f"сумма сторон {sum(s)}, в ответе {ans}"
    if k == "rhomb_rev":
        P = Fraction(g["P"])
        sols = _search(lambda a: 4 * a == P)
        return None if has_nums(t, P) and sols == [ans] else f"перебор даёт {sols}, в ответе {ans}"
    if k == "rect_rev":
        P, a = Fraction(g["P"]), Fraction(g["a"])
        sols = _search(lambda b: a + b + a + b == P)
        return None if has_nums(t, P, a) and sols == [ans] else f"перебор даёт {sols}, в ответе {ans}"
    if k == "par_rev":
        P, a = Fraction(g["P"]), Fraction(g["a"])
        sols = _search(lambda b: sum([a, b, a, b]) == P)
        return None if has_nums(t, P, a) and sols == [ans] else f"перебор даёт {sols}, в ответе {ans}"
    if k == "trap":
        b1, b2 = g["bases"]
        c, d = g["legs"]
        e = abs(b1 - b2)
        if not (abs(c - d) < e < c + d):
            return "трапеции с такими сторонами не существует"
        return None if has_nums(t, b1, b2, c, d) and b1 + b2 + c + d == ans else f"сумма сторон {b1 + b2 + c + d}, в ответе {ans}"
    if k == "trap_rev":
        P, (b1, b2), c = g["P"], g["bases"], g["leg"]
        e = abs(b1 - b2)
        sols = [d for d in range(1, 200) if abs(c - d) < e < c + d and b1 + b2 + c + d == P]  # такая трапеция должна существовать
        return None if has_nums(t, P, b1, b2, c) and sols == [ans] else f"перебор даёт {sols}, в ответе {ans}"
    if k == "iso":
        b2, b1 = g["bases"]
        leg = g["leg"]
        if not ((b1 - b2) / 2 < leg):
            return "равнобедренной трапеции с такими сторонами не существует"
        return None if has_nums(t, b1, b2, leg) and b1 + b2 + leg + leg == ans else f"сумма сторон {b1 + b2 + 2 * leg}, в ответе {ans}"
    if k == "par_diag":
        a, b, d = g["a"], g["b"], g["d"]
        if not (abs(a - b) < d < a + b):
            return "треугольник ABC не существует"
        return None if has_nums(t, a, b, d) and a + b + a + b == ans else f"сумма сторон {2 * (a + b)}, в ответе {ans}"
    if k == "rect_ratio":
        P, (w1, w2) = g["P"], g["w"]
        sols = _search(lambda x: 2 * (w1 * x + w2 * x) == P, Fraction(1, 2), 200)
        return None if has_nums(t, P, w1, w2) and len(sols) == 1 and sols[0] * max(w1, w2) == ans else f"перебор даёт {sols}, в ответе {ans}"
    if k == "rhomb_diag":
        a, d1, d2 = g["a"], g["d1"], g["d2"]
        if Fraction(d1, 2) ** 2 + Fraction(d2, 2) ** 2 != a * a:
            return "диагонали не согласуются со стороной"
        return None if has_nums(t, a, d1, d2) and 4 * a == ans else f"периметр {4 * a}, в ответе {ans}"
    if k == "par_mult":
        P, kk = g["P"], g["k"]
        sols = _search(lambda a: 2 * (a + kk * a) == P)
        return None if has_nums(t, P) and sols == [ans] else f"перебор даёт {sols}, в ответе {ans}"
    if k == "sq_eq_rect":
        a, b = g["a"], g["b"]
        sols = _search(lambda s: 4 * s == 2 * (a + b))
        return None if has_nums(t, a, b) and sols == [ans] else f"перебор даёт {sols}, в ответе {ans}"
    if k == "rect_cut":
        a, b = g["a"], g["b"]
        part = [Fraction(a, 2), Fraction(b), Fraction(a, 2), Fraction(b)]  # режем пополам сторону a: часть — прямоугольник (a/2) × b
        return None if has_nums(t, a, b) and sum(part) == ans else f"периметр части {sum(part)}, в ответе {ans}"
    return f"неизвестный вид периметра {k}"


def _v_subtle(t):
    g = t.get("geo") or {}
    k = g.get("kind")
    ans = Fraction(t["answer"])
    if k == "count":
        m = re.search(r"Даны фигуры: (.+?)\. Сколько из них обязательно являются (\w+(?: \w+)?)\?", t["prompt"])
        items = [_cls_full(x) for x in m.group(1).split(", ")]
        y, _ = _cls_start(m.group(2))
        got = sum(1 for x in items if _forall([x], y))
        return None if got == ans else f"на модели подходит {got}, в ответе {ans}"
    if k in ("opp_sum", "par_diff_big", "par_k_small", "par_sum3_acute"):
        return _v_angle4(t)
    if k == "grid_sq":
        m_, n_ = g["m"], g["n"]
        cnt = sum(1 for x0 in range(m_) for y0 in range(n_) for s in range(1, min(m_, n_) + 1) if x0 + s <= m_ and y0 + s <= n_)
        return None if cnt == ans and has_nums(t, m_, n_) else f"перебор даёт {cnt}, в ответе {ans}"
    if k == "grid_rect":
        m_, n_ = g["m"], g["n"]
        cnt = sum(1 for x0 in range(m_ + 1) for x1 in range(x0 + 1, m_ + 1) for y0 in range(n_ + 1) for y1 in range(y0 + 1, n_ + 1))
        return None if cnt == ans and has_nums(t, m_, n_) else f"перебор даёт {cnt}, в ответе {ans}"
    if k == "tri_per":
        a, b, d, P = g["a"], g["b"], g["d"], g["P"]
        if not (abs(a - b) < d < a + b) or 2 * (a + b) != P or not has_nums(t, P, d):
            return "данные не согласованы"
        return None if a + b + d == ans else f"периметр треугольника {a + b + d}, в ответе {ans}"
    if k == "tri_rev":
        a, b, T = g["a"], g["b"], g["T"]
        cands = [d for d in range(1, 200) if abs(a - b) < d < a + b and a + b + d == T]
        return None if cands == [ans] and has_nums(t, a, b, T) else f"перебор даёт {cands}, в ответе {ans}"
    if k == "rhomb60":
        cands = []
        for A in range(1, 180):
            t_ = math.radians(A)
            P = [(0.0, 0.0), (1.0, 0.0), (1.0 + math.cos(t_), math.sin(t_)), (math.cos(t_), math.sin(t_))]  # ромб со стороной 1 и углом A
            bd = math.hypot(P[3][0] - P[1][0], P[3][1] - P[1][1])  # диагональ BD
            if abs(bd - 1.0) < 1e-9:
                cands.append(max(_angle_at(P, 0), _angle_at(P, 1)))
        return None if len(cands) == 1 and _num_ok(cands[0], ans) else f"перебор даёт {cands}, в ответе {ans}"
    if k == "rtrap_count":
        counts = {f["RC"] for f in _model() if _pred("rtrap", f)}
        return None if counts == {int(ans)} else f"у прямоугольных трапеций в модели {counts} прямых углов, в ответе {ans}"
    return f"неизвестный вид {k}"


_V = {"name": _v_name, "tf": _v_tf, "which": _v_which, "coord": _v_coord, "angle4": _v_angle4, "perim": _v_perim, "subtle": _v_subtle}


def verify(t):
    """Независимая проверка одного задания: None — верно, строка — описание ошибки."""
    try:
        for key in ("prompt", "answer", "answerKind", "hint", "solution", "skills", "group", "level"):
            if key not in t:
                return f"нет поля {key}"
        if t["answerKind"] == "expr":
            Fraction(t["answer"])
        fn = _V.get(t["group"])
        if fn is None:
            return f"неизвестная группа {t['group']}"
        return fn(t)
    except (ValueError, KeyError, AttributeError, TypeError, ZeroDivisionError) as e:
        return f"не удалось проверить: {type(e).__name__}: {e}"
