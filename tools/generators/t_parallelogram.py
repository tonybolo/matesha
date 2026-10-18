"""Геометрия 8 класс (Атанасян, гл. V): «Задачи по теме «Параллелограмм, трапеция»».

Каждое задание строится из настоящей фигуры:
  параллелограмм  A(0;0), D(a;0), B = b·(cos α; sin α), C = B + (a;0)   (a = AD, b = AB, α = ∠A);
  трапеция        A(0;0), D(a;0), B(s;h), C(s+b;h)                    (основания AD = a и BC = b).
В поле geo лежат координаты вершин, вспомогательные точки (def: пересечение диагоналей, основание биссектрисы,
основание высоты, середины), условие на «языке измерений» (facts) и вопрос (ask).

verify() ничего не берёт у генератора: сама строит вспомогательные точки, меряет длины (расстояния), углы
(atan2 векторного и скалярного произведений), площади (формула шнурка), сверяет числа и формулировки условия
с текстом, проверяет вид фигуры и перебором других фигур (сетки углов и длин, сдвиги параметров) убеждается,
что ответ единственный. Признаки параллелограмма проверяются теоремами и библиотекой контрпримеров.
"""
from __future__ import annotations

import itertools
import math
import random
import re
from decimal import Decimal
from fractions import Fraction

from common import task

TOPIC = "geo-02-parallelogram-trapezoid"
DIR = "geometry8"

VERT = "ABCD"
NICE = [v for v in range(30, 151, 5) if v != 90]  # «красивые» углы параллелограмма
PH_DEG = "ответ в градусах, например 40"
PH_LEN = "ответ числом, например 12 или 7,5"
NB = {"A": "DB", "B": "AC", "C": "BD", "D": "CA"}  # соседи вершины в ABCD
OPP = {"A": "C", "B": "D", "C": "A", "D": "B"}
SIDE_OF = {frozenset("AB"): "AB", frozenset("BC"): "BC", frozenset("CD"): "CD", frozenset("AD"): "AD"}
OPP_SIDE = {"AB": "CD", "CD": "AB", "BC": "AD", "AD": "BC"}
ADJ_SIDES = {"AB": ["BC", "AD"], "CD": ["BC", "AD"], "BC": ["AB", "CD"], "AD": ["AB", "CD"]}


# ====================================================================== числа

def Fr(x) -> Fraction:
    return x if isinstance(x, Fraction) else Fraction(x)


def _finite(f: Fraction) -> bool:
    d = f.denominator
    for p in (2, 5):
        while d % p == 0:
            d //= p
    return d == 1


def dstr(x) -> str:
    f = Fr(x)
    if f.denominator == 1:
        return str(f.numerator)
    if not _finite(f):
        raise ValueError(f"не конечная десятичная дробь: {f}")
    s = format(Decimal(f.numerator) / Decimal(f.denominator), "f")
    return s.rstrip("0").rstrip(".")


def tn(x) -> str:
    """Число для TeX: 7, 3{,}5."""
    return dstr(x).replace(".", "{,}")


def fl(x) -> str:
    """Число для подписи на рисунке: 7, 3,5."""
    return dstr(x).replace(".", ",")


def an(x) -> str:
    """Ответ и значения в geo: 7, 3.5, 2/3."""
    f = Fr(x)
    return dstr(f) if _finite(f) else f"{f.numerator}/{f.denominator}"


def dg(x) -> str:
    return f"{tn(x)}^\\circ"


def raz(k: int) -> str:
    return "раза" if k % 10 in (2, 3, 4) and k % 100 not in (12, 13, 14) else "раз"


def parts(n: int) -> str:
    return f"{n} часть" if n == 1 else (f"{n} части" if n in (2, 3, 4) else f"{n} частей")


# ====================================================================== фигуры

def par_V(a, b, al):
    r = math.radians(float(al))
    bx, by = float(b) * math.cos(r), float(b) * math.sin(r)
    return {"A": (0.0, 0.0), "B": (bx, by), "C": (bx + float(a), by), "D": (float(a), 0.0)}


def trap_V(a, b, h, s):
    a, b, h, s = (float(v) for v in (a, b, h, s))
    return {"A": (0.0, 0.0), "B": (s, h), "C": (s + b, h), "D": (a, 0.0)}


def cot(deg) -> float:
    return 1 / math.tan(math.radians(float(deg)))


def trap_angles(a, b, angA, angD):
    """Трапеция с основаниями AD = a > BC = b и углами A, D при большем основании."""
    k = cot(angA) + cot(angD)
    if k <= 1e-9:
        return None
    h = (float(a) - float(b)) / k
    return trap_V(a, b, h, h * cot(angA))


def iso_V(a, b, h):
    return trap_V(a, b, h, (float(a) - float(b)) / 2)


def _shape(V):
    """Длины и угол реальной фигуры: a = AD, b = AB, α = ∠A (для рисунка)."""
    A, B, D = V["A"], V["B"], V["D"]
    a = math.dist(A, D)
    b = math.dist(A, B)
    u, w = (D[0] - A[0], D[1] - A[1]), (B[0] - A[0], B[1] - A[1])
    al = math.degrees(math.atan2(abs(u[0] * w[1] - u[1] * w[0]), u[0] * w[0] + u[1] * w[1]))
    return a, b, al


def par_from_diags(d1, d2, phi):
    """Параллелограмм с диагоналями AC = d1, BD = d2 и углом phi между ними (в градусах): возвращает a, b, α."""
    p, q = float(d1) / 2, float(d2) / 2
    r = math.radians(float(phi))
    v = (q * math.cos(r), q * math.sin(r))
    V = {"A": (-p, 0.0), "C": (p, 0.0), "B": (-v[0], -v[1]), "D": v}
    return _shape(V)


def par_from_diag_side(d1, d2, side, which):
    """Параллелограмм с диагоналями d1, d2 и стороной which (AB или BC) = side: возвращает a, b, α или None."""
    p, q = float(d1) / 2, float(d2) / 2
    c = (p * p + q * q - side * side) / (2 * p * q) if which in ("AB", "CD") else (side * side - p * p - q * q) / (2 * p * q)
    if not -0.92 < c < 0.92:
        return None
    return par_from_diags(d1, d2, math.degrees(math.acos(c)))


def _r(x: float) -> float:
    return float(f"{x:.13g}")


def geo(typ, V, facts, ask, defs=None):
    return {"type": typ, "V": {k: [_r(x), _r(y)] for k, (x, y) in V.items()}, "def": defs or {}, "facts": facts, "ask": ask}


def fx(m, v, say="tex"):
    return {"m": m, "v": an(v), "say": say}


def fs(m, vs):
    return {"m": m, "v": [an(v) for v in vs], "say": "words"}


def frel(*r):
    return {"rel": list(r)}


def par_fig(a, b, al, **kw):
    p = {"a": round(float(a), 3), "b": round(float(b), 3), "ang": round(float(al), 2)}
    p.update({k: v for k, v in kw.items() if v not in (None, False, [], "")})
    return {"id": "par", "props": p}


def trap_fig(V, **kw):
    p = {"a": round(V["D"][0], 3), "b": round(V["C"][0] - V["B"][0], 3), "h": round(V["B"][1], 3), "s": round(V["B"][0], 3)}
    p.update({k: v for k, v in kw.items() if v not in (None, False, [], "")})
    return {"id": "trap", "props": p}


def Q(ask, typ) -> str:
    """Вопрос в конце условия (verify сверяет его со своей таблицей)."""
    k = ask[0]
    fig = "параллелограмма" if typ == "par" else "трапеции"
    if k == "len":
        return f"Найдите ${ask[1]}$."
    if k == "ang":
        return f"Найдите $\\angle {ask[1]}$."
    if k == "per":
        return f"Найдите периметр {fig}." if len(ask[1]) == 4 else f"Найдите периметр треугольника ${ask[1]}$."
    if k == "area":
        return f"Найдите площадь {fig}." if len(ask[1]) == 4 else f"Найдите площадь треугольника ${ask[1]}$."
    return {
        "mline": "Найдите среднюю линию трапеции.",
        "lat": "Найдите боковую сторону трапеции.",
        "bigbase": "Найдите большее основание трапеции.",
        "smallbase": "Найдите меньшее основание трапеции.",
        "other": "Найдите другое основание.",
        "bigside": "Найдите большую сторону параллелограмма.",
        "smallside": "Найдите меньшую сторону параллелограмма.",
        "bigang": "Найдите больший угол параллелограмма." if typ == "par" else "Найдите наибольший угол трапеции.",
        "smallang": "Найдите меньший угол параллелограмма." if typ == "par" else "Найдите наименьший угол трапеции.",
        "acute": "Найдите острый угол трапеции.",
        "hsmall": "Найдите высоту, проведённую к меньшей стороне.",
    }[k] if k != "hto" else f"Найдите высоту параллелограмма, проведённую к стороне ${ask[1]}$."


def T(prompt, ans, hint, sol, skills, g, fig, ph=PH_LEN):
    extra = {} if Fr(ans).denominator == 1 else {"answerTex": tn(ans)}  # дробный ответ показываем с запятой: 4{,}5
    return task(prompt, an(ans), "expr", hint, sol, skills, fig=fig, placeholder=ph, geo=g, **extra)


def side_of(X, Y) -> str:
    return SIDE_OF[frozenset(X + Y)]


def _two_sides(rng, lo=2, hi=12, ratio=3.0):
    while True:
        a, b = rng.sample(range(lo, hi + 1), 2)
        if max(a, b) / min(a, b) <= ratio:
            return a, b


def _len_of(a, b):
    return {"AB": b, "CD": b, "BC": a, "AD": a}


# ====================================================================== параллелограмм: стороны и периметр

SK_SIDE = ["geo-p-sides", "geo-p-perimeter"]


def g_pside(rng: random.Random, level: int):
    al = rng.choice(NICE)
    if level == 1:
        a, b = sorted(_two_sides(rng), reverse=True)
        L = _len_of(a, b)
        S1, S2 = rng.choice([("AB", "BC"), ("BC", "CD"), ("CD", "AD"), ("AB", "AD")])
        facts = [fx(["len", S1], L[S1]), fx(["len", S2], L[S2])]
        head = f"В параллелограмме $ABCD$ ${S1}={L[S1]}$, ${S2}={L[S2]}$. "
        if rng.random() < 0.55:
            ask, ans = ["per", "ABCD"], 2 * (a + b)
            sol = [f"Противоположные стороны параллелограмма равны: ${OPP_SIDE[S1]}={S1}={L[S1]}$, ${OPP_SIDE[S2]}={S2}={L[S2]}$.",
                   f"Периметр — сумма всех четырёх сторон: $P=2\\cdot({L[S1]}+{L[S2]})={ans}$."]
            hint = "Периметр — длина «забора» вокруг фигуры: сложи все четыре стороны. Какие из них равны?"
            marks = [f"{S1}={L[S1]}", f"{S2}={L[S2]}"]
        else:
            Y = rng.choice([OPP_SIDE[S1], OPP_SIDE[S2]])
            src = S1 if OPP_SIDE[S1] == Y else S2
            ask, ans = ["len", Y], L[Y]
            sol = [f"Стороны ${Y}$ и ${src}$ лежат друг напротив друга — это противоположные стороны.",
                   f"Противоположные стороны параллелограмма равны: ${Y}={src}={ans}$."]
            hint = "Найди на рисунке сторону, которая лежит напротив искомой."
            marks = [f"{S1}={L[S1]}", f"{S2}={L[S2]}", f"{Y}=?"]
        return T(head + Q(ask, "par"), ans, hint, sol, SK_SIDE, geo("par", par_V(a, b, al), facts, ask), par_fig(a, b, al, marks=marks))

    if level == 2:
        kind = rng.choice(["side", "diff", "ratio", "times"])
        if kind == "side":
            a, b = sorted(_two_sides(rng, 2, 15), reverse=True)
            L, P = _len_of(a, b), 2 * (a + b)
            S1 = rng.choice(list(L))
            Y = rng.choice(ADJ_SIDES[S1])
            ask, ans = ["len", Y], L[Y]
            facts = [fx(["per", "ABCD"], P, "words"), fx(["len", S1], L[S1])]
            prompt = f"Периметр параллелограмма $ABCD$ равен ${P}$, ${S1}={L[S1]}$. " + Q(ask, "par")
            sol = [f"Противоположные стороны равны, поэтому периметр — это две соседние стороны, взятые дважды: ${S1}+{Y}={P}:2={P // 2}$.",
                   f"${Y}={P // 2}-{L[S1]}={ans}$."]
            hint = "Сумма двух соседних сторон параллелограмма равна половине периметра."
            marks = [f"{S1}={L[S1]}", f"{Y}=?"]
        elif kind == "diff":
            b, d = rng.randint(3, 12), rng.randint(1, 8)
            a = b + d
            P = 2 * (a + b)
            X = rng.choice(["AD", "BC"])
            Y = rng.choice(ADJ_SIDES[X])
            Z = rng.choice([X, Y])
            ask, ans = ["len", Z], (a if Z == X else b)
            facts = [fx(["per", "ABCD"], P, "words"), fx(["-", ["len", X], ["len", Y]], d, "words")]
            prompt = f"Периметр параллелограмма $ABCD$ равен ${P}$, сторона ${X}$ на ${d}$ больше стороны ${Y}$. " + Q(ask, "par")
            sol = [f"Сумма соседних сторон — половина периметра: ${X}+{Y}={P}:2={P // 2}$.",
                   f"Пусть ${Y}=x$, тогда ${X}=x+{d}$, и $x+x+{d}={P // 2}$, $2x={P // 2 - d}$, $x={b}$.",
                   f"${Y}={b}$, ${X}={b}+{d}={a}$. Ответ: ${Z}={ans}$."]
            hint = "Обозначь меньшую сторону через $x$; сумма соседних сторон — половина периметра."
            marks = [f"{Z}=?"]
        elif kind == "ratio":
            p, q = rng.choice([(1, 2), (2, 3), (3, 4), (2, 5), (3, 5), (1, 3), (4, 5), (1, 4)])
            x = rng.randint(1, 5)
            X = rng.choice(["AB", "CD"] if p < q else ["AD", "BC"])
            Y = rng.choice(ADJ_SIDES[X])
            lx, ly = p * x, q * x
            a, b = (ly, lx) if X in ("AB", "CD") else (lx, ly)
            P = 2 * (p + q) * x
            Z = rng.choice([X, Y])
            ask, ans = ["len", Z], (lx if Z == X else ly)
            facts = [fx(["per", "ABCD"], P, "words"), fx(["/", ["len", X], ["len", Y]], Fraction(p, q))]
            prompt = f"Периметр параллелограмма $ABCD$ равен ${P}$, ${X}:{Y}={p}:{q}$. " + Q(ask, "par")
            sol = [f"Сумма соседних сторон — половина периметра: ${X}+{Y}={P}:2={P // 2}$.",
                   f"На ${X}$ приходится {parts(p)}, на ${Y}$ — {parts(q)}, всего {parts(p + q)}. Одна часть: ${P // 2}:{p + q}={x}$.",
                   f"${X}={p}\\cdot {x}={lx}$, ${Y}={q}\\cdot {x}={ly}$. Ответ: ${Z}={ans}$."]
            hint = "Сумму соседних сторон (половину периметра) раздели на части в данном отношении."
            marks = [f"{Z}=?"]
        else:
            k, small = rng.choice([2, 3, 4]), rng.randint(2, 9)
            big = k * small
            X = rng.choice(["AD", "BC"])
            Y = rng.choice(ADJ_SIDES[X])
            a, b = (small, big) if X in ("AB", "CD") else (big, small)
            P = 2 * (big + small)
            Z = rng.choice([X, Y])
            ask, ans = ["len", Z], (big if Z == X else small)
            facts = [fx(["per", "ABCD"], P, "words"), fx(["/", ["len", X], ["len", Y]], k, "words")]
            prompt = f"Периметр параллелограмма $ABCD$ равен ${P}$, сторона ${X}$ в ${k}$ {raz(k)} больше стороны ${Y}$. " + Q(ask, "par")
            sol = [f"Сумма соседних сторон — половина периметра: ${X}+{Y}={P}:2={P // 2}$.",
                   f"Пусть ${Y}=x$, тогда ${X}={k}x$: $x+{k}x={P // 2}$, ${k + 1}x={P // 2}$, $x={small}$.",
                   f"${Y}={small}$, ${X}={big}$. Ответ: ${Z}={ans}$."]
            hint = "Обозначь меньшую сторону через $x$, тогда большая равна $kx$. Их сумма — половина периметра."
            marks = [f"{Z}=?"]
        return T(prompt, ans, hint, sol, SK_SIDE + ["geo-p-parts"], geo("par", par_V(a, b, al), facts, ask), par_fig(a, b, al, marks=marks))

    kind = rng.choice(["diff2", "sum2", "sum3", "ratio2"])
    big_or_small = rng.choice(["bigside", "smallside"])
    if kind == "diff2":
        while True:
            p, d = rng.randint(9, 30), rng.randint(1, 20)
            a, b = Fraction(p + d, 2), Fraction(p - d, 2)
            if b >= 2 and a / b <= 4:
                break
        P = 2 * p
        phrase = rng.choice([f"разность двух его сторон равна ${d}$", f"одна из его сторон на ${d}$ больше другой"])
        facts = [fx(["per", "ABCD"], P, "words"), fx(["diff2side"], d, "words")]
        sol = [f"Противоположные стороны параллелограмма равны, их разность $0$. Значит, речь о соседних сторонах.",
               f"Сумма соседних сторон — половина периметра: ${P}:2={p}$, а разность — ${d}$.",
               f"Меньшая сторона: $({p}-{d}):2={tn(b)}$, большая: ${tn(b)}+{d}={tn(a)}$."]
        hint = "Подумай, какие стороны параллелограмма могут быть разными: противоположные или соседние?"
    elif kind == "sum2":
        x1, x2 = _two_sides(rng, 3, 15)  # x1 — длина пары сторон, сумма которых названа в условии; x2 — длина другой пары
        S2, P = 2 * x1, 2 * (x1 + x2)
        a, b = max(x1, x2), min(x1, x2)
        phrase = f"сумма двух его сторон равна ${S2}$"
        facts = [fx(["per", "ABCD"], P, "words"), fx(["sum2side"], S2, "words")]
        sol = [f"Две соседние стороны в сумме дают половину периметра: ${P}:2={P // 2}$. А у нас ${S2}\\ne {P // 2}$ — значит, это противоположные стороны.",
               f"Противоположные стороны равны: каждая ${S2}:2={x1}$.",
               f"Две другие стороны вместе ${P}-{S2}={P - S2}$, каждая ${P - S2}:2={x2}$. Стороны: ${x1}$ и ${x2}$."]
        hint = "Сравни данную сумму с половиной периметра: это соседние стороны или противоположные?"
    elif kind == "sum3":
        a, b = _two_sides(rng, 3, 12)
        P, S3 = 2 * (a + b), 2 * (a + b) - a
        phrase = f"сумма трёх его сторон равна ${S3}$"
        facts = [fx(["per", "ABCD"], P, "words"), fx(["sum3side"], S3, "words")]
        sol = [f"Периметр — сумма четырёх сторон. Без одной стороны получилось ${S3}$, значит, эта сторона равна ${P}-{S3}={a}$.",
               f"Соседняя с ней сторона: ${P}:2-{a}={P // 2}-{a}={b}$.",
               f"Стороны параллелограмма: ${a}$ и ${b}$."]
        hint = "Чем отличается периметр от суммы трёх сторон?"
    else:
        k, small = rng.choice([2, 3, 4]), rng.randint(2, 8)
        a, b = k * small, small
        P = 2 * (a + b)
        phrase = f"одна из его сторон в ${k}$ {raz(k)} больше другой"
        facts = [fx(["per", "ABCD"], P, "words"), fx(["ratio2side"], k, "words")]
        sol = [f"Противоположные стороны равны, поэтому разные стороны — соседние, и их сумма ${P}:2={P // 2}$.",
               f"Пусть меньшая сторона $x$, тогда большая ${k}x$: ${k + 1}x={P // 2}$, $x={small}$.",
               f"Стороны: ${small}$ и ${k * small}$."]
        hint = "Разные стороны параллелограмма — соседние. Обозначь меньшую через $x$."
    ask = [big_or_small]
    ans = max(Fr(a), Fr(b)) if big_or_small == "bigside" else min(Fr(a), Fr(b))
    sol.append(f"Ответ: {'большая' if big_or_small == 'bigside' else 'меньшая'} сторона равна ${tn(ans)}$.")
    prompt = f"Периметр параллелограмма $ABCD$ равен ${P}$, а {phrase}. " + Q(ask, "par")
    return T(prompt, ans, hint, sol, SK_SIDE + ["geo-p-parts"], geo("par", par_V(a, b, al), facts, ask), par_fig(a, b, al))


# ====================================================================== параллелограмм: углы

SK_ANG = ["geo-p-angles", "geo-p-parallel-angles"]


def _alA(X, v):
    return v if X in "AC" else 180 - v


def g_pangle(rng: random.Random, level: int):
    a, b = sorted(_two_sides(rng, 4, 10, 2.5), reverse=True)
    if level == 1:
        X, v = rng.choice(VERT), rng.choice(NICE)
        Y = OPP[X] if rng.random() < 0.3 else rng.choice(NB[X])
        al = _alA(X, v)
        ans = v if Y == OPP[X] else 180 - v
        if Y == OPP[X]:
            sol = [f"Углы ${X}$ и ${Y}$ — противоположные: они не прилежат к одной стороне.",
                   f"Противоположные углы параллелограмма равны: $\\angle {Y}=\\angle {X}={dg(v)}$."]
        else:
            sol = [f"Углы ${X}$ и ${Y}$ прилежат к одной стороне ${side_of(X, Y)}$ — это соседние углы.",
                   f"Сумма соседних углов параллелограмма $180^\\circ$: $\\angle {Y}=180^\\circ-{dg(v)}={dg(ans)}$."]
        ask = ["ang", Y]
        prompt = f"В параллелограмме $ABCD$ $\\angle {X}={dg(v)}$. " + Q(ask, "par")
        hint = "Найди на рисунке оба угла. Они соседние (сумма $180^\\circ$) или противоположные (равны)?"
        return T(prompt, ans, hint, sol, SK_ANG, geo("par", par_V(a, b, al), [fx(["ang", X], v)], ask),
                 par_fig(a, b, al, marks=[f"{X}={v}°", f"{Y}=?"]), PH_DEG)

    if level == 2:
        kind = rng.choice(["diff", "sumopp", "ratio", "times"])
        X = rng.choice(VERT)
        Y = rng.choice(NB[X])
        if kind == "diff":
            small = rng.choice(range(30, 86, 5))
            big, d = 180 - small, 180 - 2 * small
            angs = {X: big, OPP[X]: big, Y: small, OPP[Y]: small}
            facts = [fx(["-", ["ang", X], ["ang", Y]], d, "words")]
            head = f"В параллелограмме $ABCD$ угол ${X}$ на ${dg(d)}$ больше угла ${Y}$. "
            sol = [f"Углы ${X}$ и ${Y}$ соседние, их сумма $180^\\circ$.",
                   f"Пусть $\\angle {Y}=x$, тогда $\\angle {X}=x+{dg(d)}$: $x+x+{d}^\\circ=180^\\circ$, $2x={dg(180 - d)}$, $x={dg(small)}$.",
                   f"$\\angle {Y}=\\angle {OPP[Y]}={dg(small)}$, $\\angle {X}=\\angle {OPP[X]}={dg(big)}$."]
            hint = "Соседние углы в сумме дают $180^\\circ$. Обозначь меньший угол через $x$."
        elif kind == "sumopp":
            v = rng.choice(NICE)
            X1, X2 = sorted([X, OPP[X]])
            angs = {X: v, OPP[X]: v, Y: 180 - v, OPP[Y]: 180 - v}
            facts = [fx(["+", ["ang", X1], ["ang", X2]], 2 * v)]
            head = f"В параллелограмме $ABCD$ $\\angle {X1}+\\angle {X2}={dg(2 * v)}$. "
            sol = [f"Углы ${X1}$ и ${X2}$ противоположные, они равны: каждый ${dg(2 * v)}:2={dg(v)}$.",
                   f"Два других угла — соседние с ними: $180^\\circ-{dg(v)}={dg(180 - v)}$."]
            hint = f"Углы ${X1}$ и ${X2}$ — противоположные. Что про них известно?"
        elif kind == "ratio":
            p, q = rng.choice([(1, 2), (1, 3), (2, 3), (1, 4), (1, 5), (2, 7), (4, 5), (3, 7), (5, 7), (5, 13), (7, 11), (4, 11), (7, 8)])
            if rng.random() < 0.5:
                p, q = q, p
            t = Fraction(180, p + q)
            angs = {X: p * t, OPP[X]: p * t, Y: q * t, OPP[Y]: q * t}
            facts = [fx(["/", ["ang", X], ["ang", Y]], Fraction(p, q))]
            head = f"В параллелограмме $ABCD$ $\\angle {X}:\\angle {Y}={p}:{q}$. "
            sol = [f"Углы ${X}$ и ${Y}$ соседние: $\\angle {X}+\\angle {Y}=180^\\circ$.",
                   f"Всего {parts(p + q)}, одна часть: $180^\\circ:{p + q}={dg(t)}$.",
                   f"$\\angle {X}={p}\\cdot {dg(t)}={dg(p * t)}$, $\\angle {Y}={q}\\cdot {dg(t)}={dg(q * t)}$."]
            hint = "Сумма соседних углов $180^\\circ$. Раздели её на части в данном отношении."
        else:
            k = rng.choice([2, 3, 4, 5])
            small = Fraction(180, k + 1)
            angs = {X: k * small, OPP[X]: k * small, Y: small, OPP[Y]: small}
            facts = [fx(["/", ["ang", X], ["ang", Y]], k, "words")]
            head = f"В параллелограмме $ABCD$ угол ${X}$ в ${k}$ {raz(k)} больше угла ${Y}$. "
            sol = [f"Углы ${X}$ и ${Y}$ соседние, их сумма $180^\\circ$.",
                   f"Пусть $\\angle {Y}=x$, тогда $\\angle {X}={k}x$: ${k + 1}x=180^\\circ$, $x={dg(small)}$.",
                   f"$\\angle {Y}=\\angle {OPP[Y]}={dg(small)}$, $\\angle {X}=\\angle {OPP[X]}={dg(k * small)}$."]
            hint = "Соседние углы в сумме $180^\\circ$. Обозначь меньший через $x$, больший будет $kx$."
        Z = rng.choice(VERT)
        ask, ans = ["ang", Z], angs[Z]
        sol.append(f"Ответ: $\\angle {Z}={dg(ans)}$.")
        al = angs["A"]
        return T(head + Q(ask, "par"), ans, hint, sol, SK_ANG + ["geo-p-parts"], geo("par", par_V(a, b, al), facts, ask),
                 par_fig(a, b, al, marks=[f"{Z}=?"]), PH_DEG)

    kind = rng.choice(["sum2", "diff2", "ratio2", "sum3", "diag", "height"])
    if kind in ("sum2", "diff2", "ratio2", "sum3"):
        ask = [rng.choice(["bigang", "smallang"])]
        if kind == "sum2":
            v = rng.choice(NICE)
            al = v
            facts = [fx(["sum2ang"], 2 * v, "words")]
            phrase = f"сумма двух его углов равна ${dg(2 * v)}$"
            sol = [f"Соседние углы дают в сумме $180^\\circ$, а у нас ${dg(2 * v)}$. Значит, это противоположные углы, а они равны: по ${dg(2 * v)}:2={dg(v)}$.",
                   f"Два других угла: по $180^\\circ-{dg(v)}={dg(180 - v)}$."]
            hint = "Могут ли эти два угла быть соседними? Сколько дают в сумме соседние углы?"
        elif kind == "diff2":
            small = rng.choice(range(30, 86, 5))
            al, d = small, 180 - 2 * small
            facts = [fx(["diff2ang"], d, "words")]
            phrase = f"один из его углов на ${dg(d)}$ больше другого"
            sol = [f"Противоположные углы равны, поэтому разные углы — соседние, их сумма $180^\\circ$.",
                   f"Меньший угол $x$, больший $x+{dg(d)}$: $2x+{dg(d)}=180^\\circ$, $x={dg(small)}$; больший ${dg(180 - small)}$."]
            hint = "Разные углы параллелограмма могут быть только соседними."
        elif kind == "ratio2":
            k = rng.choice([2, 3, 4, 5])
            small = Fraction(180, k + 1)
            al = small
            facts = [fx(["ratio2ang"], k, "words")]
            phrase = f"один из его углов в ${k}$ {raz(k)} больше другого"
            sol = [f"Противоположные углы равны, поэтому разные углы — соседние, их сумма $180^\\circ$.",
                   f"Меньший угол $x$, больший ${k}x$: ${k + 1}x=180^\\circ$, $x={dg(small)}$; больший ${dg(k * small)}$."]
            hint = "Разные углы параллелограмма могут быть только соседними. Обозначь меньший через $x$."
        else:
            v4 = rng.choice(NICE)
            al = v4
            S = 360 - v4
            facts = [fx(["sum3ang"], S, "words")]
            phrase = f"сумма трёх его углов равна ${dg(S)}$"
            sol = [f"Сумма всех четырёх углов параллелограмма $360^\\circ$, поэтому четвёртый угол $360^\\circ-{dg(S)}={dg(v4)}$.",
                   f"Соседний с ним угол $180^\\circ-{dg(v4)}={dg(180 - v4)}$. Углы параллелограмма: ${dg(v4)}$ и ${dg(180 - v4)}$."]
            hint = "Сумма всех углов четырёхугольника $360^\\circ$. Найди четвёртый угол."
        ans = max(Fr(al), 180 - Fr(al)) if ask[0] == "bigang" else min(Fr(al), 180 - Fr(al))
        sol.append(f"Ответ: ${dg(ans)}$.")
        prompt = f"В параллелограмме $ABCD$ {phrase}. " + Q(ask, "par")
        return T(prompt, ans, hint, sol, SK_ANG + ["geo-p-parts"], geo("par", par_V(a, b, al), facts, ask), par_fig(a, b, al), PH_DEG)

    if kind == "diag":
        while True:
            x, y = rng.randint(15, 45), rng.randint(20, 110)
            if x != y and 45 <= x + y <= 135 and x + y != 90:
                ad = rng.randint(6, 10)
                ac = ad * math.sin(math.radians(x + y)) / math.sin(math.radians(y))
                C = (ac * math.cos(math.radians(x)), ac * math.sin(math.radians(x)))
                V = {"A": (0.0, 0.0), "D": (float(ad), 0.0), "C": C, "B": (C[0] - ad, C[1])}
                aa, bb, al = _shape(V)
                if 0.35 <= bb / aa <= 1.7:
                    break
        Z = rng.choice(VERT)
        angs = {"A": x + y, "C": x + y, "B": 180 - x - y, "D": 180 - x - y}
        ask, ans = ["ang", Z], angs[Z]
        facts = [fx(["ang", "CAD"], x), fx(["ang", "ACD"], y)]
        prompt = f"В параллелограмме $ABCD$ $\\angle CAD={dg(x)}$, $\\angle ACD={dg(y)}$. " + Q(ask, "par")
        if Z in "BD":
            sol = [f"Сумма углов треугольника $ACD$ равна $180^\\circ$: $\\angle D=180^\\circ-{dg(x)}-{dg(y)}={dg(180 - x - y)}$.",
                   f"Противоположные углы параллелограмма равны: $\\angle B=\\angle D={dg(180 - x - y)}$."]
        else:
            sol = [f"$\\angle BAC=\\angle ACD={dg(y)}$ — накрест лежащие углы при $AB\\parallel CD$ и секущей $AC$.",
                   f"$\\angle A=\\angle BAC+\\angle CAD={dg(y)}+{dg(x)}={dg(x + y)}$, и $\\angle C=\\angle A$."]
        sol.append(f"Ответ: $\\angle {Z}={dg(ans)}$.")
        hint = "Посмотри на треугольник $ACD$ и вспомни про накрест лежащие углы при $AB\\parallel CD$ и секущей $AC$."
        return T(prompt, ans, hint, sol, SK_ANG + ["geo-p-triangle"], geo("par", V, facts, ask),
                 par_fig(aa, bb, al, diag="AC", marks=[f"CAD={x}°", f"ACD={y}°", f"{Z}=?"]), PH_DEG)

    al = rng.choice(range(35, 81, 5))
    beta = 90 - al
    Z = rng.choice(VERT)
    angs = {"A": al, "C": al, "B": 180 - al, "D": 180 - al}
    ask, ans = ["ang", Z], angs[Z]
    facts = [fx(["ang", "ABH"], beta)]
    prompt = f"В параллелограмме $ABCD$ проведена высота $BH$ к стороне $AD$, $\\angle ABH={dg(beta)}$. " + Q(ask, "par")
    sol = [f"Треугольник $ABH$ прямоугольный ($\\angle H=90^\\circ$), сумма его острых углов $90^\\circ$: $\\angle A=90^\\circ-{dg(beta)}={dg(al)}$."]
    sol.append(f"$\\angle C=\\angle A={dg(al)}$ (противоположные)." if Z in "AC" else f"$\\angle {Z}=180^\\circ-{dg(al)}={dg(180 - al)}$ (соседний с углом $A$ угол; противоположные углы равны).")
    hint = "Высота образует прямой угол. Сколько градусов в сумме острых углов прямоугольного треугольника?"
    return T(prompt, ans, hint, sol, SK_ANG + ["geo-p-triangle"], geo("par", par_V(a, b, al), facts, ask, {"H": ["foot", "B", "AD"]}),
             par_fig(a, b, al, ht="B>AD:H", marks=[f"ABH={beta}°", f"{Z}=?"]), PH_DEG)


# ====================================================================== параллелограмм: диагонали

SK_DIAG = ["geo-p-diag"]
HALF = {"AC": ("AO", "OC"), "BD": ("BO", "OD")}
TRI_SIDE = {"AOB": "AB", "BOC": "BC", "COD": "CD", "AOD": "AD"}
TRI_HALVES = {"AOB": ("AO", "BO"), "BOC": ("BO", "OC"), "COD": ("OC", "OD"), "AOD": ("AO", "OD")}
DIAG_INTRO = "Диагонали параллелограмма $ABCD$ пересекаются в точке $O$"
DEF_O = {"O": ["x", "AC", "BD"]}


def g_pdiag(rng: random.Random, level: int):
    if level == 1:
        d1, d2 = rng.sample(range(6, 21, 2), 2)
        aa, bb, al = par_from_diags(d1, d2, rng.choice([55, 60, 65, 70, 75, 105, 110, 115, 120]))
        D = rng.choice(["AC", "BD"])
        dv = d1 if D == "AC" else d2
        H = rng.choice(HALF[D])
        if rng.random() < 0.6:
            facts, ask, ans = [fx(["len", D], dv)], ["len", H], Fraction(dv, 2)
            prompt = f"{DIAG_INTRO}, ${D}={dv}$. " + Q(ask, "par")
            sol = [f"Точка пересечения делит каждую диагональ параллелограмма пополам: ${HALF[D][0]}={HALF[D][1]}$.",
                   f"${H}={dv}:2={tn(ans)}$."]
            marks = [f"{H}=?"]
            legend = f"{D} = {dv}"
        else:
            facts, ask, ans = [fx(["len", H], Fraction(dv, 2))], ["len", D], dv
            prompt = f"{DIAG_INTRO}, ${H}={tn(Fraction(dv, 2))}$. " + Q(ask, "par")
            sol = [f"Точка пересечения делит каждую диагональ параллелограмма пополам, значит, ${D}$ вдвое длиннее ${H}$.",
                   f"${D}=2\\cdot {tn(Fraction(dv, 2))}={dv}$."]
            marks = [f"{H}={fl(Fraction(dv, 2))}"]
            legend = f"{D} = ?"
        hint = "Где лежит точка $O$ на каждой диагонали?"
        return T(prompt, ans, hint, sol, SK_DIAG, geo("par", par_V(aa, bb, al), facts, ask, DEF_O),
                 par_fig(aa, bb, al, diag=True, marks=marks, legend=legend))

    if level == 2:
        kind = rng.choice(["per", "side", "mixed"])
        while True:
            d1, d2 = rng.sample(range(6, 21, 2), 2)
            tri = rng.choice(list(TRI_SIDE))
            S = TRI_SIDE[tri]
            lo, hi = abs(d1 - d2) // 2 + 1, (d1 + d2) // 2 - 1
            if hi < lo:
                continue
            L = rng.randint(lo, hi)
            sh = par_from_diag_side(d1, d2, L, S)
            if sh:
                break
        aa, bb, al = sh
        h1, h2 = TRI_HALVES[tri]
        hv = {"AO": Fraction(d1, 2), "OC": Fraction(d1, 2), "BO": Fraction(d2, 2), "OD": Fraction(d2, 2)}
        Pt = hv[h1] + hv[h2] + L
        if kind == "per":
            facts, ask, ans = [fx(["len", "AC"], d1), fx(["len", "BD"], d2), fx(["len", S], L)], ["per", tri], Pt
            prompt = f"{DIAG_INTRO}, $AC={d1}$, $BD={d2}$, ${S}={L}$. " + Q(ask, "par")
            sol = [f"Диагонали точкой пересечения делятся пополам: ${h1}={tn(hv[h1])}$, ${h2}={tn(hv[h2])}$.",
                   f"Периметр треугольника ${tri}$: ${h1}+{h2}+{S}={tn(hv[h1])}+{tn(hv[h2])}+{L}={tn(Pt)}$."]
            marks, legend = [f"{S}={L}"], f"AC = {d1}, BD = {d2}"
            hint = "Стороны треугольника — половинки диагоналей и сторона параллелограмма."
        elif kind == "side":
            facts, ask, ans = [fx(["len", "AC"], d1), fx(["len", "BD"], d2), fx(["per", tri], Pt, "words")], ["len", S], L
            prompt = f"{DIAG_INTRO}, $AC={d1}$, $BD={d2}$, а периметр треугольника ${tri}$ равен ${tn(Pt)}$. " + Q(ask, "par")
            sol = [f"Диагонали делятся пополам: ${h1}={tn(hv[h1])}$, ${h2}={tn(hv[h2])}$.",
                   f"${S}=P_{{{tri}}}-{h1}-{h2}={tn(Pt)}-{tn(hv[h1])}-{tn(hv[h2])}={L}$."]
            marks, legend = [f"{S}=?"], f"AC = {d1}, BD = {d2}"
            hint = "Вычти из периметра треугольника две его стороны — половинки диагоналей."
        else:
            diag_of = {"AO": "AC", "OC": "AC", "BO": "BD", "OD": "BD"}
            given_half, oh = h1, h2
            other = diag_of[oh]
            ov = d1 if other == "AC" else d2
            facts = [fx(["len", given_half], hv[given_half]), fx(["len", other], ov), fx(["len", S], L)]
            ask, ans = ["per", tri], Pt
            prompt = f"{DIAG_INTRO}, ${given_half}={tn(hv[given_half])}$, ${other}={ov}$, ${S}={L}$. " + Q(ask, "par")
            sol = [f"Диагональ ${other}$ делится точкой $O$ пополам: ${oh}={ov}:2={tn(hv[oh])}$.",
                   f"Периметр треугольника ${tri}$: ${tn(hv[h1])}+{tn(hv[h2])}+{L}={tn(Pt)}$."]
            marks, legend = [f"{given_half}={fl(hv[given_half])}", f"{S}={L}"], f"{other} = {ov}"
            hint = "Одна сторона треугольника дана, другую найди как половину диагонали."
        return T(prompt, ans, hint, sol, SK_DIAG, geo("par", par_V(aa, bb, al), facts, ask, DEF_O),
                 par_fig(aa, bb, al, diag=True, marks=marks, legend=legend))

    kind = rng.choice(["perdiff", "persum", "Pperdiff"])
    if kind in ("perdiff", "Pperdiff"):
        b, d = rng.randint(3, 10), rng.randint(1, 8)
        a = b + d
        al = rng.choice(NICE)
        if kind == "perdiff":
            T1, T2, S1, S2 = rng.choice([("AOD", "AOB", "AD", "AB"), ("BOC", "AOB", "BC", "AB"), ("BOC", "COD", "BC", "CD"), ("AOD", "COD", "AD", "CD")])
            facts = [fx(["-", ["per", T1], ["per", T2]], d, "words"), fx(["len", S2], b)]
            ask, ans = ["len", S1], a
            common = "AO" if "A" in T1 and "A" in T2 else ("BO" if "B" in T1 and "B" in T2 else ("OC" if "C" in T1 and "C" in T2 else "OD"))
            prompt = f"{DIAG_INTRO}. Периметр треугольника ${T1}$ на ${d}$ больше периметра треугольника ${T2}$, ${S2}={b}$. " + Q(ask, "par")
            sol = [f"У треугольников ${T1}$ и ${T2}$ общая сторона ${common}$, а ещё стороны-половинки второй диагонали равны (диагонали делятся пополам).",
                   f"Значит, периметры отличаются только сторонами ${S1}$ и ${S2}$: $P_{{{T1}}}-P_{{{T2}}}={S1}-{S2}={d}$.",
                   f"${S1}={b}+{d}={a}$."]
            marks = [f"{S2}={b}", f"{S1}=?"]
            hint = "Сравни стороны двух треугольников: какие у них одинаковые, а какие разные?"
        else:
            P = 2 * (a + b)
            facts = [fx(["per", "ABCD"], P, "words"), fx(["-", ["per", "AOD"], ["per", "AOB"]], d, "words")]
            Z = rng.choice(["AD", "AB"])
            ask, ans = ["len", Z], (a if Z == "AD" else b)
            prompt = f"{DIAG_INTRO}. Периметр параллелограмма $ABCD$ равен ${P}$, а периметр треугольника $AOD$ на ${d}$ больше периметра треугольника $AOB$. " + Q(ask, "par")
            sol = [f"У треугольников $AOD$ и $AOB$ общая сторона $AO$, а $OD=OB$. Поэтому $P_{{AOD}}-P_{{AOB}}=AD-AB={d}$.",
                   f"Сумма соседних сторон: $AD+AB={P}:2={P // 2}$.",
                   f"$AB=({P // 2}-{d}):2={b}$, $AD={b}+{d}={a}$. Ответ: ${Z}={ans}$."]
            marks = [f"{Z}=?"]
            hint = "Разность периметров треугольников $AOD$ и $AOB$ равна разности сторон $AD$ и $AB$."
        return T(prompt, ans, hint, sol, SK_DIAG + ["geo-p-sides"], geo("par", par_V(a, b, al), facts, ask, DEF_O),
                 par_fig(a, b, al, diag=True, marks=marks))

    while True:
        L = rng.randint(4, 12)
        d1, d2 = rng.sample(range(4, 30, 2), 2)
        if abs(d1 - d2) < 2 * L - 2 and d1 + d2 > 2 * L + 2:
            sh = par_from_diag_side(d1, d2, L, "AB")
            if sh:
                break
    aa, bb, al = sh
    S = d1 + d2
    tri, side, asked = rng.choice([("AOB", "AB", "CD"), ("COD", "CD", "AB")])
    Pt = L + S // 2
    facts = [fx(["+", ["len", "AC"], ["len", "BD"]], S), fx(["per", tri], Pt, "words")]
    ask = ["len", asked]
    prompt = f"{DIAG_INTRO}, $AC+BD={S}$, а периметр треугольника ${tri}$ равен ${Pt}$. " + Q(ask, "par")
    h1, h2 = TRI_HALVES[tri]
    sol = [f"Диагонали делятся пополам, поэтому ${h1}+{h2}=\\dfrac{{AC+BD}}{{2}}={S}:2={S // 2}$.",
           f"${side}=P_{{{tri}}}-({h1}+{h2})={Pt}-{S // 2}={L}$.",
           f"Противоположные стороны равны: ${asked}={side}={L}$."]
    hint = "Две стороны треугольника — половинки диагоналей. Чему равна их сумма?"
    return T(prompt, L, hint, sol, SK_DIAG + ["geo-p-sides"], geo("par", par_V(aa, bb, al), facts, ask, DEF_O),
             par_fig(aa, bb, al, diag=True, marks=[f"{asked}=?"], legend=f"AC + BD = {S}"))


# ====================================================================== параллелограмм: биссектриса

SK_BIS = ["geo-p-bisector", "geo-p-parallel-angles"]
BIS_WHY = ["$\\angle BAM=\\angle MAD$, потому что $AM$ — биссектриса.",
           "$\\angle BMA=\\angle MAD$ — накрест лежащие углы при $BC\\parallel AD$ и секущей $AM$.",
           "Значит, $\\angle BAM=\\angle BMA$, и треугольник $ABM$ равнобедренный: $BM=AB$."]


def _bis_task(rng, prompt, ans, hint, sol, a, b, al, facts, ask, defs, bis, marks, ph=PH_LEN, extra_sk=()):
    return T(prompt, ans, hint, sol, SK_BIS + list(extra_sk), geo("par", par_V(a, b, al), facts, ask, defs),
             par_fig(a, b, al, bis=bis, marks=marks), ph)


def g_bis(rng: random.Random, level: int):
    al = rng.choice(NICE)
    intro = "Биссектриса угла $A$ параллелограмма $ABCD$ пересекает сторону $BC$ в точке $M$"
    dM = {"M": ["bis", "A", "BC"]}
    if level == 1:
        b = rng.randint(3, 9)
        a = b + rng.randint(2, 6)
        kind = rng.choice(["AB2BM", "BM2CD", "BM2AB"])
        if kind == "AB2BM":
            facts, ask = [fx(["len", "AB"], b)], ["len", "BM"]
            marks = [f"AB={b}", "BM=?"]
            last = f"Ответ: $BM=AB={b}$."
        else:
            Z = "CD" if kind == "BM2CD" else "AB"
            facts, ask = [fx(["len", "BM"], b)], ["len", Z]
            marks = [f"BM={b}", f"{Z}=?"]
            last = f"$AB=BM={b}$" + (f", а $CD=AB={b}$ (противоположные стороны)." if Z == "CD" else ".")
        prompt = f"{intro}, ${facts[0]['m'][1]}={b}$. " + Q(ask, "par")
        hint = "Найди на рисунке два равных угла при точке $M$ и $A$: какой треугольник получился?"
        return _bis_task(rng, prompt, b, hint, BIS_WHY + [last], a, b, al, facts, ask, dM, ["A>BC:M"], marks)

    if level == 2:
        kind = rng.choice(["MC", "AD", "angle"])
        b = rng.randint(3, 10)
        a = b + rng.randint(1, min(7, int(1.5 * b)))
        if kind == "MC":
            facts, ask = [fx(["len", "AB"], b), fx(["len", "AD"], a)], ["len", "MC"]
            prompt = f"{intro}, $AB={b}$, $AD={a}$. " + Q(ask, "par")
            sol = BIS_WHY + [f"$BC=AD={a}$, поэтому $MC=BC-BM={a}-{b}={a - b}$."]
            return _bis_task(rng, prompt, a - b, "Сначала найди $BM$: какой треугольник отсекает биссектриса?", sol, a, b, al, facts, ask, dM,
                             ["A>BC:M"], [f"AB={b}", f"AD={a}", "MC=?"])
        if kind == "AD":
            c = a - b
            Z = rng.choice(["AD", "per"])
            facts = [fx(["len", "AB"], b), fx(["len", "MC"], c)]
            ask = ["len", "AD"] if Z == "AD" else ["per", "ABCD"]
            ans = a if Z == "AD" else 2 * (a + b)
            prompt = f"{intro}, $AB={b}$, $MC={c}$. " + Q(ask, "par")
            sol = BIS_WHY + [f"$BC=BM+MC={b}+{c}={a}$, и $AD=BC={a}$."]
            if Z == "per":
                sol.append(f"$P=2\\cdot({b}+{a})={ans}$.")
            return _bis_task(rng, prompt, ans, "Биссектриса отсекает равнобедренный треугольник $ABM$. Найди $BM$, потом $BC$.", sol, a, b, al, facts, ask, dM,
                             ["A>BC:M"], [f"AB={b}", f"MC={c}"] + (["AD=?"] if Z == "AD" else []))
        beta = rng.choice([20, 25, 30, 35, 40, 50, 55, 60, 65, 70])
        al = 2 * beta
        Z = rng.choice(VERT)
        angs = {"A": al, "C": al, "B": 180 - al, "D": 180 - al}
        facts, ask = [fx(["ang", "AMB"], beta)], ["ang", Z]
        prompt = f"{intro}, $\\angle AMB={dg(beta)}$. " + Q(ask, "par")
        sol = [f"$\\angle MAD=\\angle AMB={dg(beta)}$ — накрест лежащие углы при $BC\\parallel AD$ и секущей $AM$.",
               f"$AM$ — биссектриса, поэтому $\\angle A=2\\cdot {dg(beta)}={dg(al)}$."]
        sol.append(f"$\\angle C=\\angle A={dg(al)}$." if Z in "AC" else f"$\\angle {Z}=180^\\circ-{dg(al)}={dg(180 - al)}$.")
        return _bis_task(rng, prompt, angs[Z], "Найди угол, накрест лежащий с углом $AMB$.", sol, a, b, al, facts, ask, dM,
                         ["A>BC:M"], [f"AMB={beta}°", f"{Z}=?"], PH_DEG, ["geo-p-angles"])

    kind = rng.choice(["A", "D", "B", "C", "two", "MCP", "ratio"])
    b = rng.randint(3, 15)
    c = rng.randint(1, min(10, int(1.5 * b)))
    a = b + c
    if kind in ("A", "D", "B", "C"):
        P = 2 * (a + b)
        if kind == "A":
            defs, bis = {"M": ["bis", "A", "BC"]}, "A>BC:M"
            s1, s2, v1, v2 = "BM", "MC", b, c
            why = BIS_WHY
            rest = f"$AB=BM={b}$, $BC={b}+{c}={a}$."
        elif kind == "D":
            defs, bis = {"M": ["bis", "D", "BC"]}, "D>BC:M"
            s1, s2, v1, v2 = "BM", "MC", c, b
            why = ["$\\angle CDM=\\angle MDA$, потому что $DM$ — биссектриса угла $D$.",
                   "$\\angle CMD=\\angle MDA$ — накрест лежащие углы при $BC\\parallel AD$ и секущей $DM$.",
                   "Значит, треугольник $DCM$ равнобедренный: $CM=CD$ (а не $BM$!)."]
            rest = f"$CD=CM={b}$, $BC={c}+{b}={a}$."
        elif kind == "B":
            defs, bis = {"K": ["bis", "B", "AD"]}, "B>AD:K"
            s1, s2, v1, v2 = "AK", "KD", b, c
            why = ["$\\angle ABK=\\angle KBC$, потому что $BK$ — биссектриса угла $B$.",
                   "$\\angle AKB=\\angle KBC$ — накрест лежащие углы при $AD\\parallel BC$ и секущей $BK$.",
                   "Значит, треугольник $ABK$ равнобедренный: $AK=AB$."]
            rest = f"$AB=AK={b}$, $AD={b}+{c}={a}$."
        else:
            defs, bis = {"K": ["bis", "C", "AD"]}, "C>AD:K"
            s1, s2, v1, v2 = "AK", "KD", c, b
            why = ["$\\angle DCK=\\angle KCB$, потому что $CK$ — биссектриса угла $C$.",
                   "$\\angle DKC=\\angle KCB$ — накрест лежащие углы при $AD\\parallel BC$ и секущей $CK$.",
                   "Значит, треугольник $CDK$ равнобедренный: $DK=CD$."]
            rest = f"$CD=DK={b}$, $AD={c}+{b}={a}$."
        X = bis[0]
        side = bis[2:4]
        facts = [fx(["len", s1], v1), fx(["len", s2], v2)]
        ask = ["per", "ABCD"]
        prompt = f"Биссектриса угла ${X}$ параллелограмма $ABCD$ делит сторону ${side}$ на отрезки ${s1}={v1}$ и ${s2}={v2}$. " + Q(ask, "par")
        sol = why + [rest, f"$P=2\\cdot({b}+{a})={P}$."]
        hint = f"Из какого угла проведена биссектриса? Найди треугольник, который она отсекает, и его равные стороны."
        return _bis_task(rng, prompt, P, hint, sol, a, b, al, facts, ask, defs, [bis], [f"{s1}={v1}", f"{s2}={v2}"])
    if kind == "two":
        b = rng.randint(3, 9)
        a = rng.choice([v for v in range(b + 1, 3 * b) if v != 2 * b])
        facts, ask = [fx(["len", "AB"], b), fx(["len", "AD"], a)], ["len", "MK"]
        ans = abs(a - 2 * b)
        prompt = f"Биссектрисы углов $A$ и $D$ параллелограмма $ABCD$ пересекают сторону $BC$ в точках $M$ и $K$, $AB={b}$, $AD={a}$. " + Q(ask, "par")
        sol = [f"Биссектриса угла $A$ отсекает равнобедренный треугольник $ABM$: $BM=AB={b}$.",
               f"Биссектриса угла $D$ отсекает равнобедренный треугольник $DCK$: $CK=CD={b}$.",
               (f"$BC={a}$, и $BM+CK={2 * b}<{a}$: отрезки не перекрываются, $MK={a}-{2 * b}={ans}$." if a > 2 * b else
                f"$BC={a}$, а $BM+CK={2 * b}>{a}$: отрезки $BM$ и $CK$ перекрываются, и $MK={2 * b}-{a}={ans}$.")]
        hint = "Найди $BM$ и $CK$. Нарисуй, где лежат точки $M$ и $K$ на отрезке $BC$."
        return _bis_task(rng, prompt, ans, hint, sol, a, b, al, facts, ask, {"M": ["bis", "A", "BC"], "K": ["bis", "D", "BC"]},
                         ["A>BC:M", "D>BC:K"], [f"AB={b}", f"AD={a}", "MK=?"])
    if kind == "MCP":
        P = 2 * (a + b)
        facts, ask = [fx(["per", "ABCD"], P, "words"), fx(["len", "MC"], c)], ["len", "AB"]
        prompt = f"Периметр параллелограмма $ABCD$ равен ${P}$. {intro}, $MC={c}$. " + Q(ask, "par")
        sol = BIS_WHY + [f"Пусть $AB=BM=x$, тогда $BC=x+{c}$, и $AB+BC={P}:2={P // 2}$.",
                         f"$x+x+{c}={P // 2}$, $2x={P // 2 - c}$, $x={b}$."]
        return _bis_task(rng, prompt, b, "Обозначь $AB$ через $x$: чему тогда равны $BM$ и $BC$?", sol, a, b, al, facts, ask, dM,
                         ["A>BC:M"], [f"MC={c}", "AB=?"], extra_sk=["geo-p-perimeter"])
    p, q = rng.choice([(1, 2), (2, 1), (2, 3), (3, 2), (3, 4), (4, 3), (5, 3), (3, 5), (1, 3), (3, 1), (5, 2), (2, 5)])
    x = rng.randint(1, 4)
    b, c = p * x, q * x
    a = b + c
    P = 2 * (a + b)
    Z = rng.choice(["AD", "AB"])
    facts, ask = [fx(["/", ["len", "BM"], ["len", "MC"]], Fraction(p, q)), fx(["per", "ABCD"], P, "words")], ["len", Z]
    prompt = f"Периметр параллелограмма $ABCD$ равен ${P}$. {intro}, $BM:MC={p}:{q}$. " + Q(ask, "par")
    sol = BIS_WHY + [f"Пусть $BM={p}x$, $MC={q}x$. Тогда $AB={p}x$, $BC={p + q}x$, и $AB+BC={2 * p + q}x={P}:2={P // 2}$.",
                     f"$x={x}$: $AB={b}$, $AD=BC={a}$. Ответ: ${Z}={a if Z == 'AD' else b}$."]
    return _bis_task(rng, prompt, a if Z == "AD" else b, "Выбери одну часть за $x$ и вырази через $x$ стороны $AB$ и $BC$.", sol, a, b, al, facts, ask, dM,
                     ["A>BC:M"], [f"{Z}=?"], extra_sk=["geo-p-parts"])


# ====================================================================== признаки параллелограмма

GOOD = [
    ([("par", "AB", "CD"), ("eq", "AB", "CD")], "две стороны ($AB$ и $CD$) параллельны и равны — признак 1"),
    ([("par", "BC", "AD"), ("eq", "BC", "AD")], "две стороны ($BC$ и $AD$) параллельны и равны — признак 1"),
    ([("eq", "AB", "CD"), ("eq", "BC", "AD")], "противоположные стороны попарно равны — признак 2"),
    ([("eq", "AO", "OC"), ("eq", "BO", "OD")], "диагонали точкой пересечения делятся пополам — признак 3"),
    ([("par", "AB", "CD"), ("par", "BC", "AD")], "противоположные стороны попарно параллельны — это определение параллелограмма"),
]
BAD_EASY = [
    ([("par", "AB", "CD")], "трапеция с основаниями $AB$ и $CD$"),
    ([("eq", "AB", "CD")], "равнобедренная трапеция с боковыми сторонами $AB$ и $CD$"),
    ([("eq", "AC", "BD")], "равнобедренная трапеция: у неё диагонали равны"),
    ([("perp", "AC", "BD")], "«воздушный змей» (дельтоид): у него диагонали перпендикулярны"),
    ([("eq", "AB", "BC"), ("eq", "CD", "DA")], "«воздушный змей» (дельтоид): равны соседние стороны, а не противоположные"),
    ([("eq", "AO", "OC")], "«воздушный змей»: одна диагональ делится пополам, другая — нет"),
    ([("eqang", "A", "C")], "«воздушный змей»: углы $A$ и $C$ равны, а $B$ и $D$ — нет"),
    ([("sup", "A", "B")], "трапеция с основаниями $AD$ и $BC$"),
    ([("eq", "AC", "BD"), ("perp", "AC", "BD")], "«воздушный змей» с равными перпендикулярными диагоналями"),
]
BAD_TRICKY = [
    ([("par", "AB", "CD"), ("eq", "BC", "AD")], "равнобедренная трапеция с основаниями $AB$ и $CD$: одна пара сторон параллельна, а равна — другая пара"),
    ([("eq", "AB", "CD"), ("eq", "AC", "BD")], "равнобедренная трапеция с основаниями $BC$ и $AD$"),
    ([("eq", "AO", "OC"), ("perp", "AC", "BD")], "«воздушный змей»: диагональ $AC$ делится пополам, а $BD$ — нет"),
    ([("par", "AB", "CD"), ("eq", "AC", "BD")], "равнобедренная трапеция с основаниями $AB$ и $CD$"),
    ([("eq", "AO", "BO"), ("eq", "CO", "DO")], "равнобедренная трапеция с основаниями $AB$ и $CD$: равны не половинки одной диагонали, а куски разных диагоналей"),
    ([("sup", "A", "B"), ("sup", "C", "D")], "трапеция с основаниями $AD$ и $BC$: оба условия говорят одно и то же ($AD\\parallel BC$)"),
]


def atom_tex(at) -> str:
    k = at[0]
    if k == "par":
        return f"${at[1]}\\parallel {at[2]}$"
    if k == "eq":
        return f"${at[1]}={at[2]}$"
    if k == "perp":
        return f"${at[1]}\\perp {at[2]}$"
    if k == "eqang":
        return f"$\\angle {at[1]}=\\angle {at[2]}$"
    return f"$\\angle {at[1]}+\\angle {at[2]}=180^\\circ$"


def opt_text(atoms) -> str:
    return " и ".join(atom_tex(a) for a in atoms)


def g_psign(rng: random.Random, level: int):
    if level < 3:
        good = rng.choice(GOOD)
        while True:
            if level == 1:
                bad = rng.sample(BAD_EASY, 3)
            else:
                bad = rng.sample(BAD_EASY, 2) + rng.sample(BAD_TRICKY, 1)
            if sum(len(x[0]) == 2 for x in bad) >= 1:
                break
        opts = [good] + bad
        neg = False
    else:
        opts = rng.sample(GOOD, 3) + rng.sample(BAD_TRICKY, 1)
        neg = True
    order = list(range(4))
    rng.shuffle(order)
    shown = [opts[i] for i in order]
    answer = order.index(0) if not neg else order.index(3)
    uses_o = any("O" in s for at, _ in shown for at2 in at for s in at2[1:])
    note = " ($O$ — точка пересечения диагоналей.)" if uses_o else ""
    if neg:
        prompt = f"Какое из условий НЕ гарантирует, что четырёхугольник $ABCD$ — параллелограмм?{note}"
        right = shown[answer]
        sol = [f"«{opt_text(right[0])}» не гарантирует параллелограмм. Пример фигуры, у которой это выполнено, но она не параллелограмм: {right[1]}."]
        sol += [f"«{opt_text(o[0])}» гарантирует: {o[1]}." for i, o in enumerate(shown) if i != answer]
        hint = "Для каждого условия попробуй нарисовать НЕ параллелограмм, у которого оно выполнено. Вспомни равнобедренную трапецию."
    else:
        prompt = f"Какое из условий гарантирует, что четырёхугольник $ABCD$ — параллелограмм?{note}"
        right = shown[answer]
        sol = [f"«{opt_text(right[0])}»: {right[1]}."]
        sol += [f"«{opt_text(o[0])}» не гарантирует. Пример: {o[1]}." for i, o in enumerate(shown) if i != answer]
        hint = "Вспомни три признака параллелограмма. Для остальных условий попробуй нарисовать фигуру, которая не параллелограмм."
    g = {"type": "signs", "neg": neg, "opts": [[list(a) for a in o[0]] for o in shown]}
    return task(prompt, str(answer), "choice", hint, sol, ["geo-p-signs"], options=[opt_text(o[0]) for o in shown],
                fig={"id": "par", "props": {"a": 7, "b": 4, "ang": 60, "quad": True, "diag": uses_o}}, geo=g)


# ====================================================================== трапеция: углы

SK_TRAP = ["geo-p-trap", "geo-p-parallel-angles"]
TRAP_INTRO = "В трапеции $ABCD$ с основаниями $AD$ и $BC$"
ISO_INTRO = "В равнобедренной трапеции $ABCD$ с основаниями $AD$ и $BC$"
LAT_PAIR = {"A": "B", "B": "A", "C": "D", "D": "C"}
MIRROR = {"A": "D", "D": "A", "B": "C", "C": "B"}


def _trap_angles_dict(A_, D_):
    return {"A": A_, "B": 180 - A_, "C": 180 - D_, "D": D_}


def _rand_trap_by_angles(rng, A_, D_):
    for _ in range(200):
        a = rng.randint(8, 14)
        b = rng.randint(2, a - 3)
        V = trap_angles(a, b, A_, D_)
        if V and 0.15 * a <= V["B"][1] <= 0.9 * a:
            return V
    return None


def g_tangle(rng: random.Random, level: int):
    if level == 1:
        A_, D_ = rng.sample(range(40, 81, 5), 2)
        V = _rand_trap_by_angles(rng, A_, D_)
        if V is None:
            return None
        angs = _trap_angles_dict(A_, D_)
        X = rng.choice(VERT)
        Y = LAT_PAIR[X]
        ask, ans = ["ang", Y], angs[Y]
        side = side_of(X, Y)
        prompt = f"{TRAP_INTRO} известно, что $\\angle {X}={dg(angs[X])}$. " + Q(ask, "trap")
        sol = [f"Углы ${X}$ и ${Y}$ прилежат к боковой стороне ${side}$. Прямые $AD$ и $BC$ параллельны, ${side}$ — секущая, поэтому это односторонние углы.",
               f"Сумма односторонних углов $180^\\circ$: $\\angle {Y}=180^\\circ-{dg(angs[X])}={dg(ans)}$."]
        hint = "Какие два угла трапеции прилежат к одной боковой стороне? Чему равна их сумма?"
        return T(prompt, ans, hint, sol, SK_TRAP, geo("trap", V, [fx(["ang", X], angs[X])], ask),
                 trap_fig(V, marks=[f"{X}={angs[X]}°", f"{Y}=?"]), PH_DEG)

    if level == 2:
        kind = rng.choice(["AC", "right", "diff", "iso"])
        if kind == "AC":
            A_, D_ = rng.sample(range(30, 86), 2)
            V = _rand_trap_by_angles(rng, A_, D_)
            if V is None:
                return None
            angs = _trap_angles_dict(A_, D_)
            G1, G2 = rng.choice([("A", "C"), ("B", "D")])
            Z = rng.choice([LAT_PAIR[G1], LAT_PAIR[G2]])
            facts = [fx(["ang", G1], angs[G1]), fx(["ang", G2], angs[G2])]
            ask, ans = ["ang", Z], angs[Z]
            G = G1 if LAT_PAIR[G1] == Z else G2
            prompt = f"{TRAP_INTRO} известно, что $\\angle {G1}={dg(angs[G1])}$, $\\angle {G2}={dg(angs[G2])}$. " + Q(ask, "trap")
            sol = [f"Угол ${Z}$ прилежит к боковой стороне ${side_of(G, Z)}$ вместе с углом ${G}$: это односторонние углы при $AD\\parallel BC$.",
                   f"$\\angle {Z}=180^\\circ-{dg(angs[G])}={dg(ans)}$."]
            hint = "Найди угол, который прилежит к той же боковой стороне, что и искомый."
            return T(prompt, ans, hint, sol, SK_TRAP, geo("trap", V, facts, ask), trap_fig(V, marks=[f"{G1}={angs[G1]}°", f"{G2}={angs[G2]}°", f"{Z}=?"]), PH_DEG)
        if kind == "right":
            D_ = rng.randint(35, 80)
            a = rng.randint(9, 14)
            b = rng.randint(3, a - 4)
            V = trap_V(a, b, (a - b) * math.tan(math.radians(D_)), 0)
            if V["B"][1] > 1.1 * a:
                return None
            give_C = rng.random() < 0.5
            facts = [fx(["ang", "A"], 90), fx(["ang", "C"] if give_C else ["ang", "D"], 180 - D_ if give_C else D_)]
            ask = ["ang", "D"] if give_C else ["ang", "C"]
            ans = D_ if give_C else 180 - D_
            gv = 180 - D_ if give_C else D_
            prompt = f"В прямоугольной трапеции $ABCD$ с основаниями $AD$ и $BC$ известно, что $\\angle A=90^\\circ$, $\\angle {'C' if give_C else 'D'}={dg(gv)}$. " + Q(ask, "trap")
            sol = ["Прямой угол $A$ и угол $B$ прилежат к боковой стороне $AB$, поэтому и $\\angle B=180^\\circ-90^\\circ=90^\\circ$.",
                   f"Углы $C$ и $D$ прилежат к боковой стороне $CD$, их сумма $180^\\circ$: $\\angle {ask[1]}=180^\\circ-{dg(gv)}={dg(ans)}$."]
            return T(prompt, ans, "Углы при боковой стороне $CD$ — односторонние.", sol, SK_TRAP, geo("rtrap", V, facts, ask),
                     trap_fig(V, right=True, marks=[f"{'C' if give_C else 'D'}={gv}°", f"{ask[1]}=?"]), PH_DEG)
        if kind == "diff":
            A_ = rng.choice(range(50, 86, 5))
            D_ = rng.choice([v for v in range(40, 86, 5) if v != A_])
            V = _rand_trap_by_angles(rng, A_, D_)
            if V is None:
                return None
            angs = _trap_angles_dict(A_, D_)
            big, small = rng.choice([("B", "A"), ("C", "D")])
            d = angs[big] - angs[small]
            Z = rng.choice([big, small])
            facts = [fx(["-", ["ang", big], ["ang", small]], d, "words")]
            ask, ans = ["ang", Z], angs[Z]
            prompt = f"{TRAP_INTRO} угол ${big}$ на ${dg(d)}$ больше угла ${small}$. " + Q(ask, "trap")
            sol = [f"Углы ${small}$ и ${big}$ прилежат к боковой стороне ${side_of(big, small)}$, их сумма $180^\\circ$.",
                   f"Пусть $\\angle {small}=x$, тогда $x+x+{dg(d)}=180^\\circ$, $x={dg(angs[small])}$, а $\\angle {big}={dg(angs[big])}$.",
                   f"Ответ: $\\angle {Z}={dg(ans)}$."]
            return T(prompt, ans, "Сумма углов при боковой стороне $180^\\circ$. Обозначь меньший угол через $x$.", sol, SK_TRAP + ["geo-p-parts"],
                     geo("trap", V, facts, ask), trap_fig(V, marks=[f"{Z}=?"]), PH_DEG)
        A_ = rng.choice(range(40, 86, 5))
        a = rng.randint(9, 14)
        b = rng.randint(3, a - 4)
        V = iso_V(a, b, (a - b) / 2 * math.tan(math.radians(A_)))
        if V["B"][1] > 1.0 * a:
            return None
        angs = {"A": A_, "D": A_, "B": 180 - A_, "C": 180 - A_}
        X = rng.choice(VERT)
        Y = rng.choice([v for v in VERT if v != X and angs[v] != angs[X]] or [MIRROR[X]])
        ask, ans = ["ang", Y], angs[Y]
        prompt = f"{ISO_INTRO} известно, что $\\angle {X}={dg(angs[X])}$. " + Q(ask, "isotrap")
        sol = [f"В равнобедренной трапеции углы при каждом основании равны: $\\angle A=\\angle D$, $\\angle B=\\angle C$.",
               f"Углы при боковой стороне в сумме $180^\\circ$: $180^\\circ-{dg(angs[X])}={dg(180 - angs[X])}$.",
               f"Ответ: $\\angle {Y}={dg(ans)}$."]
        return T(prompt, ans, "В равнобедренной трапеции углы при основании равны, а углы при боковой стороне в сумме дают $180^\\circ$.", sol,
                 SK_TRAP + ["geo-p-iso"], geo("isotrap", V, [fx(["ang", X], angs[X])], ask), trap_fig(V, ticks=True, marks=[f"{X}={angs[X]}°", f"{Y}=?"]), PH_DEG)

    kind = rng.choice(["baseangs", "bisdiag", "diagtri", "isodiff", "rightsome"])
    if kind == "baseangs":
        A_, D_ = rng.sample(range(35, 86, 5), 2)
        V = _rand_trap_by_angles(rng, A_, D_)
        if V is None:
            return None
        ask = [rng.choice(["bigang", "smallang"])]
        ans = 180 - min(A_, D_) if ask[0] == "bigang" else min(A_, D_)
        x, y = sorted([A_, D_]) if rng.random() < 0.5 else sorted([A_, D_], reverse=True)
        prompt = f"{TRAP_INTRO} углы при основании $AD$ равны ${dg(x)}$ и ${dg(y)}$. " + Q(ask, "trap")
        sol = [f"Углы при каждой боковой стороне в сумме $180^\\circ$, поэтому два других угла: $180^\\circ-{dg(x)}={dg(180 - x)}$ и $180^\\circ-{dg(y)}={dg(180 - y)}$.",
               f"Углы трапеции: ${dg(x)}$, ${dg(y)}$, ${dg(180 - x)}$, ${dg(180 - y)}$. Ответ: ${dg(ans)}$."]
        return T(prompt, ans, "Не забудь про углы при меньшем основании: каждый дополняет до $180^\\circ$ угол при той же боковой стороне.", sol, SK_TRAP,
                 geo("trap", V, [fs(["baseangs", "AD"], [x, y])], ask), trap_fig(V, marks=[f"A={A_}°", f"D={D_}°"]), PH_DEG)
    if kind == "bisdiag":
        A_ = rng.choice([40, 50, 60, 70, 80])
        while True:
            l = rng.randint(4, 8)
            D_ = rng.choice([v for v in range(45, 86, 5) if v != 180 - A_])
            B = (l * math.cos(math.radians(A_)), l * math.sin(math.radians(A_)))
            C = (B[0] + l, B[1])
            Dx = C[0] + B[1] * cot(D_)
            V = {"A": (0.0, 0.0), "B": B, "C": C, "D": (Dx, 0.0)}
            if Dx > C[0] + 0.5:
                break
        Z = rng.choice(["ACB", "CAD", "BAC"])
        ask, ans = ["ang", Z], Fraction(A_, 2)
        facts = [fx(["ang", "B"], 180 - A_), frel("bisects", "AC", "A")]
        prompt = f"{TRAP_INTRO} диагональ $AC$ является биссектрисой угла $A$, $\\angle B={dg(180 - A_)}$. " + Q(ask, "trap")
        sol = [f"Углы $A$ и $B$ прилежат к боковой стороне $AB$: $\\angle A=180^\\circ-{dg(180 - A_)}={dg(A_)}$.",
               f"$AC$ — биссектриса: $\\angle BAC=\\angle CAD={dg(A_)}:2={dg(ans)}$."]
        if Z == "ACB":
            sol.append(f"$\\angle ACB=\\angle CAD={dg(ans)}$ — накрест лежащие углы при $BC\\parallel AD$ и секущей $AC$.")
        return T(prompt, ans, "Сначала найди угол $A$, потом раздели его пополам. Вспомни про накрест лежащие углы.", sol, SK_TRAP + ["geo-p-bisector"],
                 geo("trap", V, facts, ask), trap_fig(V, diag="AC", arcs=["BAC", "CAD"], marks=[f"B={180 - A_}°", f"{Z}=?"]), PH_DEG)
    if kind == "diagtri":
        while True:
            x, y = rng.randint(20, 45), rng.randint(60, 120)
            dd = 180 - x - y
            if 30 <= dd <= 85:
                break
        a = rng.randint(8, 12)
        ac = a * math.sin(math.radians(dd)) / math.sin(math.radians(y))
        C = (ac * math.cos(math.radians(x)), ac * math.sin(math.radians(x)))
        bl = C[0] * rng.uniform(0.45, 0.8)
        if abs(bl - a) < 0.5:
            return None
        V = {"A": (0.0, 0.0), "B": (C[0] - bl, C[1]), "C": C, "D": (float(a), 0.0)}
        Z = rng.choice(["BCD", "BCD", "D"])
        ask = ["ang", Z]
        ans = x + y if Z == "BCD" else dd
        facts = [fx(["ang", "CAD"], x), fx(["ang", "ACD"], y)]
        prompt = f"{TRAP_INTRO} известно, что $\\angle CAD={dg(x)}$, $\\angle ACD={dg(y)}$. " + Q(ask, "trap")
        if Z == "BCD":
            sol = [f"$\\angle ACB=\\angle CAD={dg(x)}$ — накрест лежащие углы при $BC\\parallel AD$ и секущей $AC$.",
                   f"$\\angle BCD=\\angle ACB+\\angle ACD={dg(x)}+{dg(y)}={dg(ans)}$."]
        else:
            sol = [f"Сумма углов треугольника $ACD$ равна $180^\\circ$: $\\angle D=180^\\circ-{dg(x)}-{dg(y)}={dg(dd)}$."]
        return T(prompt, ans, "Посмотри на треугольник $ACD$ и на накрест лежащие углы при $BC\\parallel AD$ и секущей $AC$.", sol, SK_TRAP + ["geo-p-triangle"],
                 geo("trap", V, facts, ask), trap_fig(V, diag="AC", marks=[f"CAD={x}°", f"ACD={y}°", f"{Z}=?"]), PH_DEG)
    if kind == "isodiff":
        A_ = rng.choice(range(40, 86, 5))
        d = 180 - 2 * A_
        a = rng.randint(9, 14)
        b = rng.randint(3, a - 4)
        V = iso_V(a, b, (a - b) / 2 * math.tan(math.radians(A_)))
        if V["B"][1] > 1.0 * a:
            return None
        ask = [rng.choice(["bigang", "smallang"])]
        ans = 180 - A_ if ask[0] == "bigang" else A_
        prompt = f"В равнобедренной трапеции $ABCD$ один из углов на ${dg(d)}$ больше другого. " + Q(ask, "isotrap")
        sol = ["В равнобедренной трапеции углы при основании равны, а углы при боковой стороне в сумме $180^\\circ$. Значит, у неё два угла по $x$ и два угла по $180^\\circ-x$.",
               f"Разные углы: $x$ и $x+{dg(d)}$, их сумма $180^\\circ$: $2x={dg(180 - d)}$, $x={dg(A_)}$.",
               f"Углы трапеции: ${dg(A_)}$ и ${dg(180 - A_)}$. Ответ: ${dg(ans)}$."]
        return T(prompt, ans, "Сколько разных по величине углов у равнобедренной трапеции?", sol, SK_TRAP + ["geo-p-iso", "geo-p-parts"],
                 geo("isotrap", V, [fx(["diff2ang"], d, "words")], ask), trap_fig(V, ticks=True), PH_DEG)
    D_ = rng.randint(35, 80)
    a = rng.randint(9, 14)
    b = rng.randint(3, a - 4)
    V = trap_V(a, b, (a - b) * math.tan(math.radians(D_)), 0)
    if V["B"][1] > 1.1 * a:
        return None
    ask = ["acute"]
    prompt = f"Один из углов прямоугольной трапеции $ABCD$ равен ${dg(180 - D_)}$. " + Q(ask, "rtrap")
    sol = ["У прямоугольной трапеции два прямых угла: при боковой стороне, перпендикулярной основаниям.",
           f"Угол ${dg(180 - D_)}$ тупой, он прилежит к другой боковой стороне вместе с острым углом; их сумма $180^\\circ$.",
           f"Острый угол: $180^\\circ-{dg(180 - D_)}={dg(D_)}$."]
    return T(prompt, D_, "Сколько прямых углов у прямоугольной трапеции? А какие углы в сумме дают $180^\\circ$?", sol, SK_TRAP,
             geo("rtrap", V, [fx(["someang"], 180 - D_, "words")], ask), trap_fig(V, right=True), PH_DEG)


# ====================================================================== трапеция: средняя линия

SK_MID = ["geo-p-midline"]


def _rand_trap(rng, a, b, h=None):
    a, b = float(a), float(b)
    h = h if h is not None else max(2.0, round(rng.uniform(0.25, 0.55) * a * 2) / 2)
    gap = a - b
    s = rng.uniform(0.2 * gap, 0.8 * gap) if gap > 0 else rng.uniform(0.2, 1.5)
    s = round(s * 2) / 2
    if not 0 < s < gap:
        s = gap / 2
    return trap_V(a, b, h, s)


def g_tmid(rng: random.Random, level: int):
    if level == 1:
        while True:
            a = rng.randint(6, 18)
            b = rng.randint(2, a - 2)
            if (a + b) % 2 == 0:
                break
        V = _rand_trap(rng, a, b)
        x, y = (b, a) if rng.random() < 0.6 else (a, b)
        m = Fraction(a + b, 2)
        prompt = f"Основания трапеции $ABCD$ равны ${x}$ и ${y}$. " + Q(["mline"], "trap")
        sol = ["Средняя линия трапеции равна полусумме оснований: $m=\\dfrac{a+b}{2}$.",
               f"$m=\\dfrac{{{x}+{y}}}{{2}}={tn(m)}$."]
        return T(prompt, m, "Средняя линия — среднее арифметическое оснований.", sol, SK_MID,
                 geo("trap", V, [fs(["bases"], [x, y])], ["mline"]), trap_fig(V, mid=True, marks=[f"AD={a}", f"BC={b}", "MN=?"]))

    if level == 2:
        kind = rng.choice(["other", "diff", "ratio", "dec"])
        if kind == "other":
            a = rng.randint(6, 20)
            b = rng.randint(2, a - 2)
            m = Fraction(a + b, 2)
            V = _rand_trap(rng, a, b)
            gb, Z = rng.choice([("BC", "AD"), ("AD", "BC")])
            gv, ans = (b, a) if gb == "BC" else (a, b)
            facts = [fx(["mline"], m, "words"), fx(["len", gb], gv)]
            ask = ["len", Z]
            prompt = f"{TRAP_INTRO} средняя линия равна ${tn(m)}$, ${gb}={gv}$. " + Q(ask, "trap")
            sol = [f"Средняя линия — полусумма оснований: $\\dfrac{{AD+BC}}{{2}}={tn(m)}$, значит, $AD+BC=2\\cdot {tn(m)}={a + b}$.",
                   f"${Z}={a + b}-{gv}={ans}$."]
            return T(prompt, ans, "Если полусумма оснований равна $m$, то их сумма равна $2m$.", sol, SK_MID, geo("trap", V, facts, ask),
                     trap_fig(V, mid=True, marks=[f"{gb}={gv}", f"MN={fl(m)}", f"{Z}=?"]))
        if kind == "diff":
            while True:
                b, d = rng.randint(2, 12), rng.randint(1, 10)
                a = b + d
                if (a + b) % 2 == 0 or rng.random() < 0.3:
                    break
            m = Fraction(a + b, 2)
            V = _rand_trap(rng, a, b)
            ask = [rng.choice(["bigbase", "smallbase"])]
            ans = a if ask[0] == "bigbase" else b
            facts = [fx(["mline"], m, "words"), fx(["diff2base"], d, "words")]
            prompt = f"Средняя линия трапеции $ABCD$ равна ${tn(m)}$, а одно из оснований больше другого на ${d}$. " + Q(ask, "trap")
            sol = [f"Сумма оснований — удвоенная средняя линия: $2\\cdot {tn(m)}={a + b}$.",
                   f"Меньшее основание $x$, большее $x+{d}$: $2x+{d}={a + b}$, $x={b}$.",
                   f"Основания ${b}$ и ${a}$. Ответ: ${ans}$."]
            return T(prompt, ans, "Найди сумму оснований, а потом обозначь меньшее основание через $x$.", sol, SK_MID + ["geo-p-parts"],
                     geo("trap", V, facts, ask), trap_fig(V, mid=True, marks=[f"MN={fl(m)}"]))
        if kind == "ratio":
            p, q = rng.choice([(1, 2), (2, 3), (3, 4), (1, 3), (2, 5), (3, 5), (1, 4), (4, 5)])
            x = rng.randint(1, 4)
            b, a = p * x, q * x
            m = Fraction(a + b, 2)
            V = _rand_trap(rng, a, b)
            ask = [rng.choice(["bigbase", "smallbase"])]
            ans = a if ask[0] == "bigbase" else b
            facts = [fx(["ratio2base"], Fraction(p, q), "words"), fx(["mline"], m, "words")]
            prompt = f"Основания трапеции $ABCD$ относятся как ${p}:{q}$, а средняя линия равна ${tn(m)}$. " + Q(ask, "trap")
            sol = [f"Сумма оснований: $2\\cdot {tn(m)}={a + b}$.",
                   f"Всего {parts(p + q)}, одна часть: ${a + b}:{p + q}={x}$.",
                   f"Основания: ${p}\\cdot {x}={b}$ и ${q}\\cdot {x}={a}$. Ответ: ${ans}$."]
            return T(prompt, ans, "Сумма оснований равна удвоенной средней линии. Раздели её на части.", sol, SK_MID + ["geo-p-parts"],
                     geo("trap", V, facts, ask), trap_fig(V, mid=True, marks=[f"MN={fl(m)}"]))
        while True:
            a = rng.randint(5, 19)
            b = rng.randint(2, a - 2)
            if (a + b) % 2 == 1:
                break
        V = _rand_trap(rng, a, b)
        m = Fraction(a + b, 2)
        prompt = f"Основания трапеции $ABCD$ равны ${b}$ и ${a}$. " + Q(["mline"], "trap")
        sol = ["Средняя линия трапеции равна полусумме оснований.", f"$m=\\dfrac{{{b}+{a}}}{{2}}=\\dfrac{{{a + b}}}{{2}}={tn(m)}$."]
        return T(prompt, m, "Средняя линия — среднее арифметическое оснований; ответ может быть дробным.", sol, SK_MID,
                 geo("trap", V, [fs(["bases"], [b, a])], ["mline"]), trap_fig(V, mid=True, marks=[f"AD={a}", f"BC={b}", "MN=?"]))

    kind = rng.choice(["some", "parts", "isoP", "partsdiff", "PQ"])
    if kind == "some":
        a = rng.randint(5, 16)
        b = rng.randint(1, a - 2)
        m = Fraction(a + b, 2)
        if not _finite(m):
            return None
        V = _rand_trap(rng, a, b)
        given_big = rng.random() < 0.7
        g, ans = (a, b) if given_big else (b, a)
        facts = [fx(["somebase"], g, "words"), fx(["mline"], m, "words")]
        prompt = f"Одно из оснований трапеции $ABCD$ равно ${g}$, а средняя линия равна ${tn(m)}$. " + Q(["other"], "trap")
        sol = [f"Средняя линия — полусумма оснований: $\\dfrac{{{g}+x}}{{2}}={tn(m)}$, где $x$ — другое основание.",
               f"${g}+x={a + b}$, $x={a + b}-{g}={ans}$."]
        if given_big:
            sol.append(f"Заметь: данное основание ${g}$ оказалось большим, а искомое — меньшим (средняя линия ${tn(m)}$ меньше ${g}$).")
        return T(prompt, ans, "Средняя линия лежит между основаниями по длине: она больше меньшего основания и меньше большего.", sol, SK_MID,
                 geo("trap", V, facts, ["other"]), trap_fig(V, mid=True, marks=[f"MN={fl(m)}"]))
    if kind == "parts":
        a = rng.randint(6, 24)
        b = rng.randint(2, a - 2)
        V = _rand_trap(rng, a, b)
        p1, p2 = Fraction(b, 2), Fraction(a, 2)
        x, y = (p1, p2) if rng.random() < 0.5 else (p2, p1)
        ask = [rng.choice(["bigbase", "smallbase"])]
        ans = a if ask[0] == "bigbase" else b
        prompt = f"Средняя линия трапеции $ABCD$ делится диагональю на отрезки ${tn(x)}$ и ${tn(y)}$. " + Q(ask, "trap")
        sol = ["Диагональ $AC$ режет трапецию на треугольники $ABC$ и $ACD$. Кусочки средней линии — средние линии этих треугольников.",
               "Средняя линия треугольника равна половине стороны, которой она параллельна: кусок в треугольнике $ABC$ равен $BC:2$, кусок в треугольнике $ACD$ равен $AD:2$.",
               f"Основания: $2\\cdot {tn(p1)}={b}$ и $2\\cdot {tn(p2)}={a}$. Ответ: ${ans}$."]
        return T(prompt, ans, "Диагональ делит трапецию на два треугольника. Чем для них являются кусочки средней линии?", sol, SK_MID + ["geo-p-tri-midline"],
                 geo("trap", V, [fs(["midparts"], [x, y])], ask), trap_fig(V, mid=True, diag="AC", midx=True, marks=[f"MP={fl(p1)}", f"PN={fl(p2)}"]))
    if kind == "isoP":
        while True:
            l = rng.randint(4, 10)
            o = rng.randint(1, l - 1)
            b = rng.randint(2, 10)
            a = b + 2 * o
            if a <= 26:
                break
        V = iso_V(a, b, math.sqrt(l * l - o * o))
        P = a + b + 2 * l
        m = Fraction(a + b, 2)
        facts = [fx(["per", "ABCD"], P, "words"), fx(["lat"], l, "words")]
        prompt = f"Периметр равнобедренной трапеции $ABCD$ равен ${P}$, а боковая сторона равна ${l}$. " + Q(["mline"], "isotrap")
        sol = [f"Боковые стороны равнобедренной трапеции равны, вместе они $2\\cdot {l}={2 * l}$.",
               f"Сумма оснований: ${P}-{2 * l}={a + b}$.",
               f"Средняя линия — полусумма оснований: ${a + b}:2={tn(m)}$."]
        return T(prompt, m, "Вычти из периметра обе боковые стороны — останется сумма оснований.", sol, SK_MID + ["geo-p-iso"],
                 geo("isotrap", V, facts, ["mline"]), trap_fig(V, mid=True, ticks=True, marks=[f"AB={l}", "MN=?"]))
    if kind == "partsdiff":
        while True:
            m, d = rng.randint(5, 16), rng.randint(1, 8)
            if m - d >= 2:
                break
        b, a = m - d, m + d
        V = _rand_trap(rng, a, b)
        ask = [rng.choice(["bigbase", "smallbase"])]
        ans = a if ask[0] == "bigbase" else b
        facts = [fx(["mline"], m, "words"), fx(["midpartsdiff"], d, "words")]
        prompt = f"Средняя линия трапеции $ABCD$ равна ${m}$ и делится диагональю на два отрезка, один из которых на ${d}$ больше другого. " + Q(ask, "trap")
        sol = ["Кусочки средней линии — средние линии треугольников $ABC$ и $ACD$, то есть половинки оснований: $\\dfrac{BC}{2}$ и $\\dfrac{AD}{2}$.",
               f"Меньший кусок $x$, больший $x+{d}$: $2x+{d}={m}$, $x={tn(Fraction(m - d, 2))}$.",
               f"Основания: $2x={b}$ и $2(x+{d})={a}$. Ответ: ${ans}$."]
        return T(prompt, ans, "Каждый кусок средней линии — половина одного из оснований.", sol, SK_MID + ["geo-p-tri-midline", "geo-p-parts"],
                 geo("trap", V, facts, ask), trap_fig(V, mid=True, diag="AC", midx=True, marks=[f"MN={m}"]))
    a = rng.randint(6, 20)
    b = rng.randint(2, a - 2)
    V = _rand_trap(rng, a, b)
    ans = Fraction(a - b, 2)
    defs = {"M": ["mid", "AB"], "N": ["mid", "CD"], "P": ["x", "MN", "AC"], "Q": ["x", "MN", "BD"]}
    prompt = f"Основания трапеции $ABCD$ равны ${b}$ и ${a}$. Средняя линия $MN$ пересекает диагонали $AC$ и $BD$ в точках $P$ и $Q$. " + Q(["len", "PQ"], "trap")
    sol = [f"$MP$ — средняя линия треугольника $ABC$: $MP=BC:2={tn(Fraction(b, 2))}$.",
           f"$MQ$ — средняя линия треугольника $ABD$: $MQ=AD:2={tn(Fraction(a, 2))}$.",
           f"$PQ=MQ-MP={tn(Fraction(a, 2))}-{tn(Fraction(b, 2))}={tn(ans)}$."]
    return T(prompt, ans, "Кусочки средней линии от точки $M$ до диагоналей — средние линии треугольников $ABC$ и $ABD$.", sol, SK_MID + ["geo-p-tri-midline"],
             geo("trap", V, [fs(["bases"], [b, a])], ["len", "PQ"], defs), trap_fig(V, mid=True, diag=True, midx=True, marks=[f"AD={a}", f"BC={b}", "PQ=?"]))


# ====================================================================== равнобедренная трапеция

SK_ISO = ["geo-p-iso"]


def _iso_by_lat(rng, lo_l=4, hi_l=10, hi_b=12):
    while True:
        l = rng.randint(lo_l, hi_l)
        o = rng.randint(1, l - 1)
        b = rng.randint(2, hi_b)
        a = b + 2 * o
        if 0.2 * a <= math.sqrt(l * l - o * o) <= 0.85 * a:
            return l, o, b, a


def g_tiso(rng: random.Random, level: int):
    if level == 1:
        kind = rng.choice(["per", "diag", "ang"])
        if kind == "per":
            l, o, b, a = _iso_by_lat(rng)
            V = iso_V(a, b, math.sqrt(l * l - o * o))
            ans = a + b + 2 * l
            facts = [fx(["len", "AB"], l), fx(["len", "BC"], b), fx(["len", "AD"], a)]
            prompt = f"{ISO_INTRO} известно, что $AB={l}$, $BC={b}$, $AD={a}$. " + Q(["per", "ABCD"], "isotrap")
            sol = [f"Боковые стороны равнобедренной трапеции равны: $CD=AB={l}$.", f"$P=AB+BC+CD+AD={l}+{b}+{l}+{a}={ans}$."]
            return T(prompt, ans, "Какая сторона в условии не названа? Чему она равна в равнобедренной трапеции?", sol, SK_ISO,
                     geo("isotrap", V, facts, ["per", "ABCD"]), trap_fig(V, ticks=True, marks=[f"AB={l}", f"BC={b}", f"AD={a}"]))
        if kind == "diag":
            d = rng.randint(5, 16)
            th = math.radians(rng.uniform(25, 45))
            sab = 2 * d * math.cos(th)
            b = sab * rng.uniform(0.25, 0.42)
            a = sab - b
            V = iso_V(a, b, d * math.sin(th))
            Z = rng.choice(["BD"])
            prompt = f"{ISO_INTRO} известно, что $AC={d}$. " + Q(["len", Z], "isotrap")
            sol = ["У равнобедренной трапеции диагонали равны (трапеция симметрична, диагонали — отражения друг друга).", f"$BD=AC={d}$."]
            return T(prompt, d, "Вспомни свойства равнобедренной трапеции: что можно сказать про её диагонали?", sol, SK_ISO,
                     geo("isotrap", V, [fx(["len", "AC"], d)], ["len", Z]), trap_fig(V, ticks=True, diag=True, legend=f"AC = {d}, BD = ?"))
        A_ = rng.choice(range(40, 86, 5))
        a = rng.randint(9, 14)
        b = rng.randint(3, a - 4)
        V = iso_V(a, b, (a - b) / 2 * math.tan(math.radians(A_)))
        if V["B"][1] > 1.0 * a:
            return None
        angs = {"A": A_, "D": A_, "B": 180 - A_, "C": 180 - A_}
        X = rng.choice(VERT)
        Y = rng.choice([MIRROR[X], LAT_PAIR[X]])
        ans = angs[Y]
        prompt = f"{ISO_INTRO} известно, что $\\angle {X}={dg(angs[X])}$. " + Q(["ang", Y], "isotrap")
        if Y == MIRROR[X]:
            sol = [f"В равнобедренной трапеции углы при каждом основании равны: $\\angle {Y}=\\angle {X}={dg(ans)}$."]
        else:
            sol = [f"Углы ${X}$ и ${Y}$ прилежат к боковой стороне ${side_of(X, Y)}$, их сумма $180^\\circ$: $\\angle {Y}=180^\\circ-{dg(angs[X])}={dg(ans)}$."]
        return T(prompt, ans, "Углы при одном основании равнобедренной трапеции равны, а при боковой стороне — в сумме $180^\\circ$.", sol, SK_ISO + ["geo-p-trap"],
                 geo("isotrap", V, [fx(["ang", X], angs[X])], ["ang", Y]), trap_fig(V, ticks=True, marks=[f"{X}={angs[X]}°", f"{Y}=?"]), PH_DEG)

    if level == 2:
        kind = rng.choice(["lat", "some", "twostep"])
        if kind == "lat":
            l, o, b, a = _iso_by_lat(rng)
            V = iso_V(a, b, math.sqrt(l * l - o * o))
            P = a + b + 2 * l
            x, y = (b, a) if rng.random() < 0.6 else (a, b)
            facts = [fx(["per", "ABCD"], P, "words"), fs(["bases"], [x, y])]
            prompt = f"Периметр равнобедренной трапеции $ABCD$ равен ${P}$, а её основания равны ${x}$ и ${y}$. " + Q(["lat"], "isotrap")
            sol = [f"На две боковые стороны приходится ${P}-{a}-{b}={2 * l}$.", f"Боковые стороны равны: каждая ${2 * l}:2={l}$."]
            return T(prompt, l, "Вычти основания из периметра. Сколько остаётся на каждую боковую сторону?", sol, SK_ISO,
                     geo("isotrap", V, facts, ["lat"]), trap_fig(V, ticks=True, marks=[f"AD={a}", f"BC={b}", "AB=?"]))
        A_ = rng.choice(range(40, 86, 5))
        a = rng.randint(9, 14)
        b = rng.randint(3, a - 4)
        V = iso_V(a, b, (a - b) / 2 * math.tan(math.radians(A_)))
        if V["B"][1] > 1.0 * a:
            return None
        if kind == "some":
            v = rng.choice([A_, 180 - A_])
            ask = [rng.choice(["bigang", "smallang"])]
            ans = 180 - A_ if ask[0] == "bigang" else A_
            prompt = f"Один из углов равнобедренной трапеции $ABCD$ равен ${dg(v)}$. " + Q(ask, "isotrap")
            sol = ["У равнобедренной трапеции два угла по $x$ (при одном основании) и два угла по $180^\\circ-x$ (при другом).",
                   f"Углы трапеции: ${dg(v)}$ и $180^\\circ-{dg(v)}={dg(180 - v)}$. Ответ: ${dg(ans)}$."]
            return T(prompt, ans, "Какие ещё углы трапеции можно найти по одному углу?", sol, SK_ISO + ["geo-p-trap"],
                     geo("isotrap", V, [fx(["someang"], v, "words")], ask), trap_fig(V, ticks=True), PH_DEG)
        X, Y = rng.choice([("B", "D"), ("C", "A"), ("A", "C"), ("D", "B")])
        angs = {"A": A_, "D": A_, "B": 180 - A_, "C": 180 - A_}
        prompt = f"{ISO_INTRO} известно, что $\\angle {X}={dg(angs[X])}$. " + Q(["ang", Y], "isotrap")
        sol = [f"Угол ${LAT_PAIR[X]}$ прилежит с углом ${X}$ к боковой стороне: $\\angle {LAT_PAIR[X]}=180^\\circ-{dg(angs[X])}={dg(angs[LAT_PAIR[X]])}$.",
               f"Углы при основании равнобедренной трапеции равны: $\\angle {Y}=\\angle {LAT_PAIR[X]}={dg(angs[Y])}$."]
        return T(prompt, angs[Y], "Сначала найди угол при той же боковой стороне, потом вспомни про углы при основании.", sol, SK_ISO + ["geo-p-trap"],
                 geo("isotrap", V, [fx(["ang", X], angs[X])], ["ang", Y]), trap_fig(V, ticks=True, marks=[f"{X}={angs[X]}°", f"{Y}=?"]), PH_DEG)

    kind = rng.choice(["foot", "sixty", "bisdiag", "obtuse", "Pm"])
    if kind == "foot":
        o, b = rng.randint(2, 9), rng.randint(3, 20)
        a = b + 2 * o
        V = iso_V(a, b, rng.randint(3, 8))
        ask = [rng.choice(["smallbase", "bigbase", "mline"])]
        ans = {"smallbase": b, "bigbase": a, "mline": b + o}[ask[0]]
        x, y = (o, b + o) if rng.random() < 0.6 else (b + o, o)
        prompt = f"В равнобедренной трапеции $ABCD$ высота, проведённая из вершины тупого угла, делит большее основание на отрезки ${x}$ и ${y}$. " + Q(ask, "isotrap")
        sol = ["Опустим высоты $BH$ и $CK$ на большее основание $AD$. Получится прямоугольник $HBCK$ (в нём $HK=BC$) и два одинаковых прямоугольных треугольника по краям: $AH=KD$.",
               f"Меньший отрезок $AH={o}$, больший $HD=HK+KD=BC+{o}={b + o}$.",
               f"$BC={b + o}-{o}={b}$, $AD={o}+{b + o}={a}$."]
        if ask[0] == "mline":
            sol.append(f"Средняя линия: $\\dfrac{{{a}+{b}}}{{2}}={b + o}$ — ровно больший отрезок!")
        return T(prompt, ans, "Опусти из вершин тупых углов две высоты: на какие части они делят большее основание?", sol, SK_ISO + (["geo-p-midline"] if ask[0] == "mline" else []),
                 geo("isotrap", V, [fs(["footparts"], [x, y])], ask), trap_fig(V, ticks=True, ht=["B>AD:H"], marks=[f"AH={o}", f"HD={b + o}"]))
    if kind == "sixty":
        l = rng.randint(2, 10)
        a = rng.randint(l + 2, l + 14)
        b = a - l
        V = iso_V(a, b, l * math.sqrt(3) / 2)
        facts = [fx(["bigbase"], a, "words"), fx(["lat"], l, "words"), fx(["bigbaseang"], 60, "words")]
        prompt = f"Большее основание равнобедренной трапеции $ABCD$ равно ${a}$, боковая сторона равна ${l}$, а угол между ними равен $60^\\circ$. " + Q(["smallbase"], "isotrap")
        sol = ["Опустим высоты $BH$ и $CK$ на большее основание $AD$. В прямоугольном треугольнике $ABH$ $\\angle A=60^\\circ$, значит, $\\angle ABH=30^\\circ$.",
               f"Катет против угла $30^\\circ$ равен половине гипотенузы: $AH=AB:2={tn(Fraction(l, 2))}$. Так же $KD={tn(Fraction(l, 2))}$.",
               f"$BC=HK=AD-AH-KD={a}-{tn(Fraction(l, 2))}-{tn(Fraction(l, 2))}={b}$."]
        return T(prompt, b, "Опусти высоты из вершин меньшего основания. Вспомни про катет против угла $30^\\circ$.", sol, SK_ISO + ["geo-p-leg30"],
                 geo("isotrap", V, facts, ["smallbase"]), trap_fig(V, ticks=True, ht=["B>AD:H", "C>AD:K"], marks=[f"AD={a}", f"AB={l}", "A=60°", "BC=?"]))
    if kind == "bisdiag":
        b = rng.randint(3, 9)
        a = rng.randint(b + 1, 3 * b - 1)
        V = iso_V(a, b, math.sqrt(b * b - ((a - b) / 2) ** 2))
        ans = a + 3 * b
        facts = [fx(["len", "BC"], b), fx(["len", "AD"], a), frel("bisects", "AC", "A")]
        prompt = f"{ISO_INTRO} диагональ $AC$ является биссектрисой угла $A$, $BC={b}$, $AD={a}$. " + Q(["per", "ABCD"], "isotrap")
        sol = ["$\\angle BCA=\\angle CAD$ — накрест лежащие углы при $BC\\parallel AD$ и секущей $AC$; $\\angle CAD=\\angle BAC$, потому что $AC$ — биссектриса.",
               f"Значит, $\\angle BCA=\\angle BAC$, треугольник $ABC$ равнобедренный: $AB=BC={b}$.",
               f"Трапеция равнобедренная: $CD=AB={b}$. $P={b}+{b}+{b}+{a}={ans}$."]
        return T(prompt, ans, "Найди в треугольнике $ABC$ два равных угла.", sol, SK_ISO + ["geo-p-bisector", "geo-p-parallel-angles"],
                 geo("isotrap", V, facts, ["per", "ABCD"]), trap_fig(V, ticks=True, diag="AC", arcs=["BAC", "CAD"], marks=[f"BC={b}", f"AD={a}"]))
    if kind == "obtuse":
        l, b = rng.randint(4, 10), rng.randint(2, 10)
        a = b + l
        V = iso_V(a, b, l * math.sqrt(3) / 2)
        facts = [fx(["obtuse"], 120, "words"), fx(["lat"], l, "words"), fx(["smallbase"], b, "words")]
        prompt = f"Тупой угол равнобедренной трапеции $ABCD$ равен $120^\\circ$, боковая сторона равна ${l}$, а меньшее основание равно ${b}$. " + Q(["bigbase"], "isotrap")
        sol = ["Острый угол трапеции: $180^\\circ-120^\\circ=60^\\circ$.",
               f"Опустим высоты $BH$ и $CK$. В треугольнике $ABH$ $\\angle ABH=90^\\circ-60^\\circ=30^\\circ$, и катет против него — половина боковой стороны: $AH={tn(Fraction(l, 2))}$.",
               f"$AD=AH+HK+KD={tn(Fraction(l, 2))}+{b}+{tn(Fraction(l, 2))}={a}$."]
        return T(prompt, a, "Найди острый угол и опусти высоты из вершин тупых углов.", sol, SK_ISO + ["geo-p-leg30"],
                 geo("isotrap", V, facts, ["bigbase"]), trap_fig(V, ticks=True, ht=["B>AD:H", "C>AD:K"], marks=["B=120°", f"AB={l}", f"BC={b}", "AD=?"]))
    l, o, b, a = _iso_by_lat(rng)
    V = iso_V(a, b, math.sqrt(l * l - o * o))
    m, P = Fraction(a + b, 2), a + b + 2 * l
    facts = [fx(["per", "ABCD"], P, "words"), fx(["mline"], m, "words")]
    prompt = f"Периметр равнобедренной трапеции $ABCD$ равен ${P}$, а её средняя линия равна ${tn(m)}$. " + Q(["lat"], "isotrap")
    sol = [f"Сумма оснований — удвоенная средняя линия: $AD+BC=2\\cdot {tn(m)}={a + b}$.",
           f"На две равные боковые стороны остаётся ${P}-{a + b}={2 * l}$, на одну — ${l}$."]
    return T(prompt, l, "Сумма оснований равна удвоенной средней линии.", sol, SK_ISO + ["geo-p-midline"],
             geo("isotrap", V, facts, ["lat"]), trap_fig(V, ticks=True, mid=True, marks=[f"MN={fl(m)}", "AB=?"]))


# ====================================================================== ⭐ площади

SK_AREA = ["geo-p-area"]
SK_AREA_T = ["geo-p-area-trap"]


def g_area(rng: random.Random, level: int):
    kind = rng.choice(["ah", "Sh", "30", "two", "tri", "trap", "trapS", "trapm", "isoPy", "iso45", "right"])
    if kind in ("ah", "Sh"):
        a = rng.randint(5, 15)
        h = rng.randint(2, max(3, min(9, int(0.7 * a))))
        al = rng.choice([45, 50, 55, 60, 65, 70, 75])
        b = h / math.sin(math.radians(al))
        if b * math.cos(math.radians(al)) >= a - 0.5:
            return None
        V = par_V(a, b, al)
        if kind == "ah":
            facts, ask = [fx(["len", "AD"], a), fx(["len", "BH"], h)], ["area", "ABCD"]
            prompt = f"В параллелограмме $ABCD$ к стороне $AD$ проведена высота $BH$, $AD={a}$, $BH={h}$. " + Q(ask, "par")
            sol = ["Площадь параллелограмма — основание, умноженное на высоту, проведённую к этому основанию: $S=AD\\cdot BH$.", f"$S={a}\\cdot {h}={a * h}$."]
            return T(prompt, a * h, "Площадь параллелограмма: основание на высоту.", sol, SK_AREA, geo("par", V, facts, ask, {"H": ["foot", "B", "AD"]}),
                     par_fig(a, b, al, ht="B>AD:H", marks=[f"AD={a}", f"BH={h}"]))
        S = a * h
        facts, ask = [fx(["area", "ABCD"], S, "words"), fx(["len", "AD"], a)], ["hto", "AD"]
        prompt = f"Площадь параллелограмма $ABCD$ равна ${S}$, $AD={a}$. " + Q(ask, "par")
        sol = ["$S=AD\\cdot h$, где $h$ — высота, проведённая к стороне $AD$.", f"$h=S:AD={S}:{a}={h}$."]
        return T(prompt, h, "Площадь равна основанию, умноженному на высоту. Значит, высота — площадь, делённая на основание.", sol, SK_AREA,
                 geo("par", V, facts, ask), par_fig(a, b, al, ht="B>AD:H", marks=[f"AD={a}", "BH=?"]))
    if kind == "30":
        a, b = rng.randint(4, 14), rng.randint(2, 12)
        if b * math.cos(math.radians(30)) >= a - 0.5 or b < 0.4 * a:
            return None
        X = rng.choice(["A", "B", "C", "D"])
        v = 30 if X in "AC" else 150
        V = par_V(a, b, 30)
        S = Fraction(a * b, 2)
        prompt = f"В параллелограмме $ABCD$ $AB={b}$, $AD={a}$, $\\angle {X}={dg(v)}$. " + Q(["area", "ABCD"], "par")
        sol = ([f"Углы $A$ и ${X}$ {'соседние' if X in 'BD' else 'противоположные'}, поэтому $\\angle A={'180^\\circ-150^\\circ=' if X in 'BD' else ''}30^\\circ$."] if X != "A" else []) + [
            "Проведём высоту $BH$ к стороне $AD$. В прямоугольном треугольнике $ABH$ $\\angle A=30^\\circ$.",
            f"Катет против угла $30^\\circ$ равен половине гипотенузы: $BH=AB:2={tn(Fraction(b, 2))}$.",
            f"$S=AD\\cdot BH={a}\\cdot {tn(Fraction(b, 2))}={tn(S)}$."]
        return T(prompt, S, "Проведи высоту из вершины $B$. Вспомни, чему равен катет против угла $30^\\circ$.", sol, SK_AREA + ["geo-p-leg30"],
                 geo("par", V, [fx(["len", "AB"], b), fx(["len", "AD"], a), fx(["ang", X], v)], ["area", "ABCD"]),
                 par_fig(a, b, 30, ht="B>AD:H", marks=[f"AB={b}", f"AD={a}", f"{X}={v}°"]))
    if kind == "two":
        a, b = rng.randint(5, 15), rng.randint(3, 12)
        if b >= a:
            return None
        L = a * b // math.gcd(a, b)
        options = [S for S in range(L, a * b, L)]
        if not options:
            return None
        S = rng.choice(options)
        h1, h2 = S // a, S // b
        al = math.degrees(math.asin(h1 / b))
        V = par_V(a, b, al)
        facts = [fs(["sides"], [b, a]), fx(["hbig"], h1, "words")]
        prompt = f"Стороны параллелограмма $ABCD$ равны ${b}$ и ${a}$, а высота, проведённая к большей стороне, равна ${h1}$. " + Q(["hsmall"], "par")
        sol = ["Площадь параллелограмма можно посчитать двумя способами: через любую сторону и высоту к ней.",
               f"$S={a}\\cdot {h1}={S}$.", f"Высота к меньшей стороне: $S:{b}={S}:{b}={h2}$."]
        return T(prompt, h2, "Сначала найди площадь, а потом раздели её на меньшую сторону.", sol, SK_AREA,
                 geo("par", V, facts, ["hsmall"]), par_fig(a, b, al, ht="B>AD:H", marks=[f"AD={a}", f"AB={b}", f"BH={h1}"]))
    if kind == "tri":
        to_o = rng.random() < 0.5
        S = rng.randint(3, 20) * (4 if to_o else 2)
        a = rng.randint(5, 12)
        h = Fraction(S, a)
        al = rng.choice([50, 60, 70])
        b = float(h) / math.sin(math.radians(al))
        V = par_V(a, b, al)
        if to_o:
            ask, ans = ["area", "AOB"], Fraction(S, 4)
            prompt = f"Площадь параллелограмма $ABCD$ равна ${S}$, $O$ — точка пересечения его диагоналей. " + Q(ask, "par")
            sol = [f"Диагональ $BD$ делит параллелограмм на два равных треугольника: $S_{{ABD}}={S}:2={S // 2}$.",
                   "У треугольников $AOB$ и $AOD$ равные основания $BO=OD$ и общая высота из вершины $A$, поэтому их площади равны.",
                   f"$S_{{AOB}}={S // 2}:2={tn(ans)}$."]
            defs, fig = {"O": ["x", "AC", "BD"]}, par_fig(a, b, al, diag=True)
        else:
            ask, ans = ["area", "ABD"], Fraction(S, 2)
            prompt = f"Площадь параллелограмма $ABCD$ равна ${S}$. " + Q(ask, "par")
            sol = ["Диагональ $BD$ делит параллелограмм на два равных треугольника $ABD$ и $CDB$ (у них три стороны соответственно равны).",
                   f"$S_{{ABD}}={S}:2={tn(ans)}$."]
            defs, fig = {}, par_fig(a, b, al, diag="BD")
        return T(prompt, ans, "На какие равные части делят параллелограмм диагонали?", sol, SK_AREA + ["geo-p-diag"],
                 geo("par", V, [fx(["area", "ABCD"], S, "words")], ask, defs), fig)
    if kind in ("trap", "trapS", "trapm"):
        a = rng.randint(5, 16)
        b = rng.randint(2, a - 2)
        h = rng.randint(2, max(3, min(9, int(0.7 * a))))
        V = _rand_trap(rng, a, b, h)
        S = Fraction((a + b) * h, 2)
        m = Fraction(a + b, 2)
        if kind == "trap":
            facts = [fs(["bases"], [b, a]), fx(["height"], h, "words")]
            prompt = f"Основания трапеции $ABCD$ равны ${b}$ и ${a}$, а высота равна ${h}$. " + Q(["area", "ABCD"], "trap")
            sol = ["Площадь трапеции — полусумма оснований, умноженная на высоту: $S=\\dfrac{a+b}{2}\\cdot h$.",
                   f"$S=\\dfrac{{{a}+{b}}}{{2}}\\cdot {h}={tn(m)}\\cdot {h}={tn(S)}$."]
            return T(prompt, S, "Площадь трапеции: средняя линия на высоту.", sol, SK_AREA_T, geo("trap", V, facts, ["area", "ABCD"]),
                     trap_fig(V, ht=["B>AD:H"], marks=[f"AD={a}", f"BC={b}", f"BH={h}"]))
        if kind == "trapm":
            facts = [fx(["mline"], m, "words"), fx(["height"], h, "words")]
            prompt = f"Средняя линия трапеции $ABCD$ равна ${tn(m)}$, а высота равна ${h}$. " + Q(["area", "ABCD"], "trap")
            sol = ["$S=\\dfrac{a+b}{2}\\cdot h$, а $\\dfrac{a+b}{2}$ — это и есть средняя линия.", f"$S={tn(m)}\\cdot {h}={tn(S)}$."]
            return T(prompt, S, "Посмотри внимательно на формулу площади трапеции: где в ней средняя линия?", sol, SK_AREA_T + ["geo-p-midline"],
                     geo("trap", V, facts, ["area", "ABCD"]), trap_fig(V, mid=True, ht=["B>AD:H"], marks=[f"MN={fl(m)}", f"BH={h}"]))
        if not _finite(S):
            return None
        g = rng.choice([a, b])
        ans = a + b - g
        facts = [fx(["area", "ABCD"], S, "words"), fx(["height"], h, "words"), fx(["somebase"], g, "words")]
        prompt = f"Площадь трапеции $ABCD$ равна ${tn(S)}$, высота равна ${h}$, а одно из оснований равно ${g}$. " + Q(["other"], "trap")
        sol = [f"$S=\\dfrac{{a+b}}{{2}}\\cdot h$, поэтому $\\dfrac{{a+b}}{{2}}=S:h={tn(S)}:{h}={tn(m)}$, а $a+b={a + b}$.",
               f"Другое основание: ${a + b}-{g}={ans}$."]
        return T(prompt, ans, "Из формулы площади найди сначала полусумму оснований.", sol, SK_AREA_T, geo("trap", V, facts, ["other"]),
                 trap_fig(V, ht=["B>AD:H"], marks=[f"BH={h}"]))
    if kind == "isoPy":
        o, h, l = rng.choice([(3, 4, 5), (4, 3, 5), (6, 8, 10), (8, 6, 10), (5, 12, 13), (12, 5, 13), (9, 12, 15), (12, 9, 15)])
        b = rng.randint(2, 10)
        a = b + 2 * o
        V = iso_V(a, b, h)
        S = Fraction((a + b) * h, 2)
        facts = [fs(["bases"], [b, a]), fx(["lat"], l, "words")]
        prompt = f"Основания равнобедренной трапеции $ABCD$ равны ${b}$ и ${a}$, а боковая сторона равна ${l}$. " + Q(["area", "ABCD"], "isotrap")
        sol = [f"Опустим высоту $BH$ на $AD$: $AH=\\dfrac{{AD-BC}}{{2}}=\\dfrac{{{a}-{b}}}{{2}}={o}$.",
               f"По теореме Пифагора из треугольника $ABH$: $BH=\\sqrt{{{l}^2-{o}^2}}=\\sqrt{{{l * l - o * o}}}={h}$.",
               f"$S=\\dfrac{{{a}+{b}}}{{2}}\\cdot {h}={tn(S)}$."]
        return T(prompt, S, "Найди высоту: опусти её из вершины $B$ и посмотри на прямоугольный треугольник.", sol, SK_AREA_T + ["geo-p-iso", "geo-p-pythagoras"],
                 geo("isotrap", V, facts, ["area", "ABCD"]), trap_fig(V, ticks=True, ht=["B>AD:H"], marks=[f"AD={a}", f"BC={b}", f"AB={l}"]))
    if kind == "iso45":
        o = rng.randint(2, 8)
        b = rng.randint(2, 2 * o + 4)
        a = b + 2 * o
        V = iso_V(a, b, o)
        S = Fraction((a + b) * o, 2)
        x, y = (o, b + o) if rng.random() < 0.6 else (b + o, o)
        facts = [fx(["obtuse"], 135, "words"), fs(["footparts"], [x, y])]
        prompt = f"Тупой угол равнобедренной трапеции $ABCD$ равен $135^\\circ$, а высота, проведённая из вершины этого угла, делит большее основание на отрезки ${x}$ и ${y}$. " + Q(["area", "ABCD"], "isotrap")
        sol = [f"Острый угол трапеции $180^\\circ-135^\\circ=45^\\circ$. В прямоугольном треугольнике $ABH$ оба острых угла по $45^\\circ$, он равнобедренный: $BH=AH={o}$.",
               f"Большее основание ${o}+{b + o}={a}$, меньшее ${b + o}-{o}={b}$ (как в задаче про высоту равнобедренной трапеции).",
               f"$S=\\dfrac{{{a}+{b}}}{{2}}\\cdot {o}={tn(S)}$."]
        return T(prompt, S, "Найди острый угол: какой получится треугольник у края трапеции?", sol, SK_AREA_T + ["geo-p-iso"],
                 geo("isotrap", V, facts, ["area", "ABCD"]), trap_fig(V, ticks=True, ht=["B>AD:H"], marks=["B=135°", f"AH={o}", f"HD={b + o}"]))
    a = rng.randint(5, 16)
    b = rng.randint(2, a - 2)
    h = rng.randint(2, max(3, min(9, int(0.7 * a))))
    V = trap_V(a, b, h, 0)
    S = Fraction((a + b) * h, 2)
    facts = [fs(["bases"], [b, a]), fx(["minlat"], h, "words")]
    prompt = f"Основания прямоугольной трапеции $ABCD$ равны ${b}$ и ${a}$, а меньшая боковая сторона равна ${h}$. " + Q(["area", "ABCD"], "rtrap")
    sol = ["В прямоугольной трапеции меньшая боковая сторона перпендикулярна основаниям — это и есть высота.",
           f"$S=\\dfrac{{{a}+{b}}}{{2}}\\cdot {h}={tn(S)}$."]
    return T(prompt, S, "Какая боковая сторона прямоугольной трапеции перпендикулярна основаниям?", sol, SK_AREA_T,
             geo("rtrap", V, facts, ["area", "ABCD"]), trap_fig(V, right=True, marks=[f"AD={a}", f"BC={b}", f"AB={h}"]))


GROUPS = [
    ("pside", "Стороны и периметр параллелограмма", g_pside, 0),
    ("pangle", "Углы параллелограмма", g_pangle, 1),
    ("pdiag", "Диагонали параллелограмма", g_pdiag, 2),
    ("bis", "Биссектриса параллелограмма", g_bis, 3),
    ("psign", "Признаки параллелограмма", g_psign, 4),
    ("tangle", "Углы трапеции", g_tangle, 5),
    ("tiso", "Равнобедренная трапеция", g_tiso, 5),
    ("tmid", "Средняя линия трапеции", g_tmid, 6),
]
OLYMPIAD = [("area", "Площадь", g_area, 7)]


# ######################################################################
# НЕЗАВИСИМАЯ ПРОВЕРКА. Ниже ничего не берётся из генератора выше: свои точки, меры, тексты и перебор.
# ######################################################################

class _Bad(Exception):
    pass


_VV = "ABCD"
_NBR = {"A": ("D", "B"), "B": ("A", "C"), "C": ("B", "D"), "D": ("C", "A")}


def _cl(x: float, y: float, tol: float = 1e-9) -> bool:
    return abs(x - y) <= tol * max(1.0, abs(x), abs(y))


def _sb(p, q):
    return (p[0] - q[0], p[1] - q[1])


def _cr(u, v):
    return u[0] * v[1] - u[1] * v[0]


def _dt(u, v):
    return u[0] * v[0] + u[1] * v[1]


def _ln(u):
    return math.hypot(u[0], u[1])


def _ds(p, q):
    return _ln(_sb(p, q))


def _an(p, o, q):
    """Угол POQ в градусах через atan2(|векторное|, скалярное)."""
    u, v = _sb(p, o), _sb(q, o)
    return math.degrees(math.atan2(abs(_cr(u, v)), _dt(u, v)))


def _cut(p1, p2, p3, p4):
    d1, d2 = _sb(p2, p1), _sb(p4, p3)
    den = _cr(d1, d2)
    if abs(den) < 1e-12 * max(1.0, _ln(d1) * _ln(d2)):
        return None
    w = _sb(p3, p1)
    t, u = _cr(w, d2) / den, _cr(w, d1) / den
    return (p1[0] + t * d1[0], p1[1] + t * d1[1]), t, u


def _inn(t: float) -> bool:
    return 1e-9 < t < 1 - 1e-9


def _shoelace(pts) -> float:
    s = 0.0
    for i in range(len(pts)):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % len(pts)]
        s += x1 * y2 - x2 * y1
    return abs(s) / 2


def _mid(p, q):
    return ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2)


def _derive(P0, defs):
    P = dict(P0)
    for name, spec in defs.items():
        k = spec[0]
        if k == "x":
            s1, s2 = spec[1], spec[2]
            r = _cut(P[s1[0]], P[s1[1]], P[s2[0]], P[s2[1]])
            if r is None or not (_inn(r[1]) and _inn(r[2])):
                raise _Bad(f"{name}: отрезки {s1} и {s2} не пересекаются")
            P[name] = r[0]
        elif k == "bis":
            X, side = spec[1], spec[2]
            n1, n2 = _NBR[X]
            u1, u2 = _sb(P[n1], P[X]), _sb(P[n2], P[X])
            d = (u1[0] / _ln(u1) + u2[0] / _ln(u2), u1[1] / _ln(u1) + u2[1] / _ln(u2))
            r = _cut(P[X], (P[X][0] + d[0], P[X][1] + d[1]), P[side[0]], P[side[1]])
            if r is None or r[1] <= 0 or not _inn(r[2]):
                raise _Bad(f"{name}: биссектриса угла {X} не попадает внутрь стороны {side}")
            P[name] = r[0]
        elif k == "foot":
            X, side = spec[1], spec[2]
            p1, p2 = P[side[0]], P[side[1]]
            d = _sb(p2, p1)
            t = _dt(_sb(P[X], p1), d) / _dt(d, d)
            if not _inn(t):
                raise _Bad(f"{name}: основание высоты из {X} не на стороне {side}")
            P[name] = (p1[0] + t * d[0], p1[1] + t * d[1])
        elif k == "mid":
            P[name] = _mid(P[spec[1][0]], P[spec[1][1]])
        else:
            raise _Bad(f"неизвестная точка {spec}")
    return P


def _iang(P, X) -> float:
    n1, n2 = _NBR[X]
    return _an(P[n1], P[X], P[n2])


def _all_angs(P):
    return [_iang(P, X) for X in _VV]


def _all_sides(P):
    return [_ds(P["A"], P["B"]), _ds(P["B"], P["C"]), _ds(P["C"], P["D"]), _ds(P["D"], P["A"])]


def _line_dist(p, a, b) -> float:
    return abs(_cr(_sb(b, a), _sb(p, a))) / _ds(a, b)


def _distinct2(vals):
    out = []
    for v in vals:
        if not any(_cl(v, w, 1e-7) for w in out):
            out.append(v)
    return out


def _fact_val(v):
    return [float(Fraction(x)) for x in v] if isinstance(v, list) else float(Fraction(v))


def _somebase_value(g):
    for f in g["facts"]:
        if f.get("m") == ["somebase"]:
            return float(Fraction(f["v"]))
    raise _Bad("нет условия «одно из оснований»")


def _meas(m, P, g):
    k = m[0]
    if k == "len":
        return _ds(P[m[1][0]], P[m[1][1]])
    if k == "ang":
        s = m[1]
        return _iang(P, s) if len(s) == 1 else _an(P[s[0]], P[s[1]], P[s[2]])
    if k == "per":
        s = m[1]
        return sum(_ds(P[s[i]], P[s[(i + 1) % len(s)]]) for i in range(len(s)))
    if k == "area":
        return _shoelace([P[c] for c in m[1]])
    if k in ("+", "-", "/"):
        vals = [_meas(x, P, g) for x in m[1:]]
        if k == "+":
            return sum(vals)
        if k == "-":
            return vals[0] - vals[1]
        return vals[0] / vals[1]
    AB, BC, CD, AD = _ds(P["A"], P["B"]), _ds(P["B"], P["C"]), _ds(P["C"], P["D"]), _ds(P["A"], P["D"])
    if k == "mline":
        return _ds(_mid(P["A"], P["B"]), _mid(P["C"], P["D"]))
    if k == "lat":
        if not _cl(AB, CD):
            raise _Bad("боковые стороны не равны")
        return AB
    if k in ("bigbase", "smallbase"):
        if _cl(AD, BC):
            raise _Bad("основания равны")
        return max(AD, BC) if k == "bigbase" else min(AD, BC)
    if k in ("bigside", "smallside"):
        if _cl(AB, AD, 1e-7):
            raise _Bad("стороны равны: «большая сторона» не имеет смысла")
        return max(AB, AD) if k == "bigside" else min(AB, AD)
    if k in ("bigang", "smallang"):
        angs = _all_angs(P)
        if len(_distinct2(angs)) < 2:
            raise _Bad("все углы равны")
        return max(angs) if k == "bigang" else min(angs)
    if k == "acute":
        ac = [x for x in _all_angs(P) if x < 90 - 1e-7]
        if len(ac) != 1:
            raise _Bad(f"острых углов {len(ac)}, а не один")
        return ac[0]
    if k == "obtuse":
        ob = [x for x in _all_angs(P) if x > 90 + 1e-7]
        if not ob or len(_distinct2(ob)) != 1:
            raise _Bad("тупые углы не одинаковые")
        return ob[0]
    if k == "hto":
        s = m[1]
        others = [c for c in _VV if c not in s]
        h1, h2 = (_line_dist(P[c], P[s[0]], P[s[1]]) for c in others)
        if not _cl(h1, h2):
            raise _Bad(f"противоположная сторона не параллельна {s}")
        return h1
    if k == "height":
        h1, h2 = _line_dist(P["B"], P["A"], P["D"]), _line_dist(P["C"], P["A"], P["D"])
        if not _cl(h1, h2):
            raise _Bad("основания не параллельны")
        return h1
    if k in ("hbig", "hsmall"):
        if _cl(AB, AD, 1e-7):
            raise _Bad("стороны равны")
        big, small = ("AD", "AB") if AD > AB else ("AB", "AD")
        return _meas(["hto", big if k == "hbig" else small], P, g)
    if k == "bigbaseang":
        base = "AD" if AD > BC else "BC"
        a1, a2 = _iang(P, base[0]), _iang(P, base[1])
        if not _cl(a1, a2):
            raise _Bad("углы при большем основании разные")
        return a1
    if k == "minlat":
        return min(AB, CD)
    if k == "other":
        gv = _somebase_value(g)
        hit = [x for x, y in ((AD, BC), (BC, AD)) if _cl(x, gv)]
        if len(hit) != 1:
            raise _Bad("данное основание не найдено или основания равны")
        return BC if _cl(AD, gv) else AD
    raise _Bad(f"неизвестная величина {m}")


def _midline_cuts(P):
    M, N = _mid(P["A"], P["B"]), _mid(P["C"], P["D"])
    out = []
    for d in ("AC", "BD"):
        r = _cut(M, N, P[d[0]], P[d[1]])
        if r is None or not (_inn(r[1]) and _inn(r[2])):
            raise _Bad("средняя линия не пересекает диагональ")
        out.append(sorted([_ds(M, r[0]), _ds(r[0], N)]))
    return out


def _same_set(xs, ys) -> bool:
    return len(xs) == len(ys) and all(_cl(a, b) for a, b in zip(sorted(xs), sorted(ys)))


def _holds(f, P, g) -> bool:
    if "rel" in f:
        r = f["rel"]
        if r[0] == "bisects":
            d, X = r[1], r[2]
            Y = d[1] if d[0] == X else d[0]
            n1, n2 = _NBR[X]
            return _cl(_an(P[n1], P[X], P[Y]), _an(P[Y], P[X], P[n2])) and _cl(_an(P[n1], P[X], P[Y]) * 2, _iang(P, X))
        raise _Bad(f"неизвестное отношение {r}")
    m, v = f["m"], _fact_val(f["v"])
    k = m[0]
    pairs = list(itertools.combinations(range(4), 2))
    if k in ("someang", "sum2ang", "diff2ang", "ratio2ang", "sum3ang"):
        A = _all_angs(P)
        if k == "someang":
            return any(_cl(x, v) for x in A)
        if k == "sum2ang":
            return any(_cl(A[i] + A[j], v) for i, j in pairs)
        if k == "diff2ang":
            return any(_cl(abs(A[i] - A[j]), v) for i, j in pairs)
        if k == "ratio2ang":
            return any(_cl(max(A[i], A[j]) / min(A[i], A[j]), v) for i, j in pairs)
        return any(_cl(sum(A[i] for i in c), v) for c in itertools.combinations(range(4), 3))
    if k in ("sum2side", "diff2side", "ratio2side", "sum3side", "sides"):
        S = _all_sides(P)
        if k == "sides":
            return _same_set(_distinct2(S), v)
        if k == "sum2side":
            return any(_cl(S[i] + S[j], v) for i, j in pairs)
        if k == "diff2side":
            return any(_cl(abs(S[i] - S[j]), v) for i, j in pairs)
        if k == "ratio2side":
            return any(_cl(max(S[i], S[j]) / min(S[i], S[j]), v) for i, j in pairs)
        return any(_cl(sum(S[i] for i in c), v) for c in itertools.combinations(range(4), 3))
    AD, BC = _ds(P["A"], P["D"]), _ds(P["B"], P["C"])
    if k == "bases":
        return _same_set([AD, BC], v)
    if k == "somebase":
        return _cl(AD, v) or _cl(BC, v)
    if k == "diff2base":
        return _cl(abs(AD - BC), v)
    if k == "ratio2base":
        return _cl(min(AD, BC) / max(AD, BC), v)
    if k == "baseangs":
        return _same_set([_iang(P, m[1][0]), _iang(P, m[1][1])], v)
    if k == "midparts":
        return all(_same_set(c, v) for c in _midline_cuts(P))
    if k == "midpartsdiff":
        return all(_cl(c[1] - c[0], v) for c in _midline_cuts(P))
    if k == "footparts":
        big, small = ("AD", "BC") if AD > BC else ("BC", "AD")
        found = 0
        for X in small:
            if _iang(P, X) > 90 + 1e-7:
                p1, p2 = P[big[0]], P[big[1]]
                d = _sb(p2, p1)
                t = _dt(_sb(P[X], p1), d) / _dt(d, d)
                if not _inn(t):
                    return False
                H = (p1[0] + t * d[0], p1[1] + t * d[1])
                if not _same_set([_ds(p1, H), _ds(H, p2)], v):
                    return False
                found += 1
        return found > 0
    return _cl(_meas(m, P, g), v)


def _check_type(P, typ):
    pts = [P[c] for c in _VV]
    cr = [_cr(_sb(pts[(i + 1) % 4], pts[i]), _sb(pts[(i + 2) % 4], pts[(i + 1) % 4])) for i in range(4)]
    if not (all(c > 1e-9 for c in cr) or all(c < -1e-9 for c in cr)):
        raise _Bad("четырёхугольник не выпуклый")
    A, B, C, D = pts

    def par(p1, p2, p3, p4):
        u, w = _sb(p2, p1), _sb(p4, p3)
        return abs(_cr(u, w)) <= 1e-9 * _ln(u) * _ln(w)

    if typ == "par":
        if not (_cl(B[0] - A[0], C[0] - D[0]) and _cl(B[1] - A[1], C[1] - D[1])):
            raise _Bad("не параллелограмм: AB и DC не равны и не параллельны")
        return
    if not par(A, D, B, C) or _dt(_sb(D, A), _sb(C, B)) <= 0:
        raise _Bad("AD не параллельна BC")
    if par(A, B, D, C):
        raise _Bad("AB параллельна CD — это не трапеция")
    if typ == "isotrap" and not _cl(_ds(A, B), _ds(C, D)):
        raise _Bad("трапеция не равнобедренная")
    if typ == "rtrap" and not _cl(_iang(P, "A"), 90.0):
        raise _Bad("угол A не прямой")
    if typ not in ("trap", "isotrap", "rtrap"):
        raise _Bad(f"неизвестный вид фигуры {typ}")


# ---------- текст условия ↔ данные

_NUM = re.compile(r"\d+(?:\{,\}\d+)?")


def _vt(v) -> str:
    f = Fraction(v)
    if f.denominator == 1:
        return str(f.numerator)
    s = format(Decimal(f.numerator) / Decimal(f.denominator), "f")
    return s.rstrip("0").rstrip(".").replace(".", "{,}")


def _nums(text: str):
    return [Fraction(s.replace("{,}", ".")) for s in _NUM.findall(text)]


def _fact_nums(f):
    if "rel" in f:
        return []
    v = f["v"]
    if isinstance(v, list):
        return [Fraction(x) for x in v]
    val = Fraction(v)
    if (f["m"][0] == "/" and f["say"] == "tex") or f["m"][0] == "ratio2base":
        return [Fraction(val.numerator), Fraction(val.denominator)]
    return [val]


def _esc(s: str) -> str:
    return re.escape(s.lower())


def _say_patterns(f):
    """Как это условие обязано звучать в тексте (регулярные выражения по тексту в нижнем регистре)."""
    m, v, k = f["m"], f["v"], f["m"][0]
    V = None if isinstance(v, list) else _vt(v)
    num = lambda x: r"\$" + _esc(_vt(x)) + r"\$"
    deg = lambda x: r"\$" + _esc(_vt(x)) + r"\^\\circ\$"
    if f["say"] == "tex":
        if k == "len":
            return [_esc(f"{m[1]}={V}")]
        if k == "ang":
            return [_esc(f"\\angle {m[1]}={V}^\\circ")]
        if k == "+" and all(x[0] == "len" for x in m[1:]):
            return [_esc("+".join(x[1] for x in m[1:]) + f"={V}")]
        if k == "+" and all(x[0] == "ang" for x in m[1:]):
            return [_esc("+".join(f"\\angle {x[1]}" for x in m[1:]) + f"={V}^\\circ")]
        if k == "/":
            fv = Fraction(v)
            if m[1][0] == "len":
                return [_esc(f"{m[1][1]}:{m[2][1]}={fv.numerator}:{fv.denominator}")]
            return [_esc(f"\\angle {m[1][1]}:\\angle {m[2][1]}={fv.numerator}:{fv.denominator}")]
        raise _Bad(f"нет записи формулой для {m}")
    if k == "per" and len(m[1]) == 4:
        return [r"периметр (?:равнобедренной )?(?:параллелограмма|трапеции) \$abcd\$ равен " + num(v)]
    if k == "per":
        return [r"периметр треугольника \$" + m[1].lower() + r"\$ равен " + num(v)]
    if k == "area":
        return [r"площадь (?:параллелограмма|трапеции) \$abcd\$ равна " + num(v)]
    if k == "-":
        a, b = m[1], m[2]
        if a[0] == "ang":
            return [r"угол \$" + a[1].lower() + r"\$ на " + deg(v) + r" больше угла \$" + b[1].lower() + r"\$"]
        if a[0] == "len":
            return [r"сторона \$" + a[1].lower() + r"\$ на " + num(v) + r" больше стороны \$" + b[1].lower() + r"\$"]
        return [r"периметр треугольника \$" + a[1].lower() + r"\$ на " + num(v) + r" больше периметра треугольника \$" + b[1].lower() + r"\$"]
    if k == "/":
        a, b = m[1], m[2]
        word = "угол" if a[0] == "ang" else "сторона"
        word2 = "угла" if a[0] == "ang" else "стороны"
        return [word + r" \$" + a[1].lower() + r"\$ в " + num(v) + r" раза? больше " + word2 + r" \$" + b[1].lower() + r"\$"]
    table = {
        "mline": [r"средняя линия[^.]*? равна " + num(v)] if V else [],
        "lat": [r"боковая сторона равна " + num(v)] if V else [],
        "height": [r"высота равна " + num(v)] if V else [],
        "somebase": [r"одно из оснований (?:трапеции \$abcd\$ )?равно " + num(v)] if V else [],
        "bigbase": [r"большее основание[^.]*? равно " + num(v)] if V else [],
        "smallbase": [r"меньшее основание равно " + num(v)] if V else [],
        "minlat": [r"меньшая боковая сторона равна " + num(v)] if V else [],
        "obtuse": [r"тупой угол[^.]*? равен " + deg(v)] if V else [],
        "bigbaseang": [r"угол между ними равен " + deg(v)] if V else [],
        "someang": [r"один из углов[^.]*? равен " + deg(v)] if V else [],
        "sum2ang": [r"сумма двух (?:его )?углов[^.]*? равна " + deg(v)] if V else [],
        "diff2ang": [r"один из (?:его )?углов[^.]*? на " + deg(v) + r" больше другого"] if V else [],
        "ratio2ang": [r"один из (?:его )?углов[^.]*? в " + num(v) + r" раза? больше другого"] if V else [],
        "sum3ang": [r"сумма трёх (?:его )?углов[^.]*? равна " + deg(v)] if V else [],
        "sum2side": [r"сумма двух (?:его )?сторон[^.]*? равна " + num(v)] if V else [],
        "diff2side": [r"разность двух (?:его )?сторон[^.]*? равна " + num(v), r"одна из (?:его )?сторон[^.]*? на " + num(v) + r" больше другой"] if V else [],
        "ratio2side": [r"одна из (?:его )?сторон[^.]*? в " + num(v) + r" раза? больше другой"] if V else [],
        "sum3side": [r"сумма трёх (?:его )?сторон[^.]*? равна " + num(v)] if V else [],
        "diff2base": [r"одно из оснований больше другого на " + num(v)] if V else [],
        "midpartsdiff": [r"один из которых на " + num(v) + r" больше другого"] if V else [],
        "hbig": [r"высота, проведённая к большей стороне, равна " + num(v)] if V else [],
    }
    if k == "ratio2base":
        fv = Fraction(v)
        return [r"основания[^.]*? относятся как \$" + f"{fv.numerator}:{fv.denominator}" + r"\$"]
    if isinstance(v, list):
        x, y = v
        both = lambda pre, fmt: [pre + fmt(x) + " и " + fmt(y), pre + fmt(y) + " и " + fmt(x)]
        if k == "bases":
            return both(r"основания[^.]*? равны ", num)
        if k == "sides":
            return both(r"стороны параллелограмма[^.]*? равны ", num)
        if k == "baseangs":
            return both(r"углы при основании \$" + m[1].lower() + r"\$ равны ", deg)
        if k == "midparts":
            return both(r"делится диагональю на отрезки ", num)
        if k == "footparts":
            return both(r"делит большее основание на отрезки ", num)
    if table.get(k):
        return table[k]
    raise _Bad(f"нет словесной формулировки для {m}")


def _question(ask, typ) -> str:
    k = ask[0]
    fig = "параллелограмма" if typ == "par" else "трапеции"
    if k == "len":
        return f"Найдите ${ask[1]}$."
    if k == "ang":
        return f"Найдите $\\angle {ask[1]}$."
    if k in ("per", "area"):
        word = "периметр" if k == "per" else "площадь"
        return f"Найдите {word} {fig}." if len(ask[1]) == 4 else f"Найдите {word} треугольника ${ask[1]}$."
    if k == "hto":
        return f"Найдите высоту параллелограмма, проведённую к стороне ${ask[1]}$."
    big = {"par": ("больший", "меньший"), "trap": ("наибольший", "наименьший")}["par" if typ == "par" else "trap"]
    return {
        "mline": "Найдите среднюю линию трапеции.", "lat": "Найдите боковую сторону трапеции.",
        "bigbase": "Найдите большее основание трапеции.", "smallbase": "Найдите меньшее основание трапеции.",
        "other": "Найдите другое основание.", "bigside": "Найдите большую сторону параллелограмма.",
        "smallside": "Найдите меньшую сторону параллелограмма.", "bigang": f"Найдите {big[0]} угол {fig}.",
        "smallang": f"Найдите {big[1]} угол {fig}.", "acute": "Найдите острый угол трапеции.",
        "hsmall": "Найдите высоту, проведённую к меньшей стороне.",
    }[k]


_TYPE_WORD = {"par": "параллелограмм", "trap": "трапеци", "isotrap": "равнобедренн", "rtrap": "прямоугольн"}


def _ties(t, g, typ):
    prompt = t["prompt"]
    low = prompt.lower()
    if _TYPE_WORD[typ] not in low:
        raise _Bad(f"в тексте не сказано, что это {_TYPE_WORD[typ]}…")
    if typ in ("isotrap", "rtrap", "trap") and "трапеци" not in low:
        raise _Bad("в тексте не сказано, что это трапеция")
    if not prompt.endswith(_question(g["ask"], typ)):
        raise _Bad(f"вопрос в тексте не совпадает с вопросом в данных: {_question(g['ask'], typ)}")
    in_text = _nums(prompt)
    explained = [x for f in g["facts"] for x in _fact_nums(f)]
    for x in in_text:
        if x not in explained:
            raise _Bad(f"в тексте число {x}, которого нет в условии-данных")
    for x in explained:
        if x not in in_text:
            raise _Bad(f"в данных число {x}, которого нет в тексте")
    for f in g["facts"]:
        if "rel" in f:
            r = f["rel"]
            if r[0] == "bisects" and not (f"диагональ ${r[1]}$ является биссектрисой угла ${r[2]}$" in prompt):
                raise _Bad("не сказано, что диагональ — биссектриса")
            continue
        if not any(re.search(p, low) for p in _say_patterns(f)):
            raise _Bad(f"условие {f['m']} = {f['v']} не найдено в тексте")
    for name, spec in g["def"].items():
        if not re.search(r"\$[^$]*" + name + r"[^$]*\$", prompt):
            raise _Bad(f"точка {name} не названа в тексте")
        if spec[0] == "bis" and not (re.search(r"[Бб]иссектрис[аы] угл(?:а|ов) [^.]*?\$" + spec[1] + r"\$", prompt) and f"сторону ${spec[2]}$" in prompt):
            raise _Bad(f"не сказано, что {name} — точка на стороне {spec[2]} от биссектрисы угла {spec[1]}")
        if spec[0] == "foot" and f"высота ${spec[1]}{name}$" not in prompt.replace("проведена высота", "высота"):
            raise _Bad(f"не сказано про высоту {spec[1]}{name}")
    fig = t.get("fig", {}).get("props", {})
    shown = [x for mk in fig.get("marks", []) for x in _nums(mk.split("=", 1)[1].replace(",", "{,}"))]
    shown += _nums(str(fig.get("legend", "")).replace(",", "{,}"))
    for x in shown:
        if x not in in_text:
            raise _Bad(f"на рисунке подписано {x}, а в условии этого числа нет (рисунок подсказывает ответ?)")


# ---------- единственность ответа: другие фигуры с тем же условием

def _params(P, typ):
    A, D = P["A"], P["D"]
    a = _ds(A, D)
    ux = ((D[0] - A[0]) / a, (D[1] - A[1]) / a)
    uy = (-ux[1], ux[0])
    loc = lambda p: (_dt(_sb(p, A), ux), _dt(_sb(p, A), uy))
    B = loc(P["B"])
    sgn = 1 if B[1] > 0 else -1
    if typ == "par":
        return {"a": a, "b": _ds(A, P["B"]), "al": _an(D, A, P["B"])}
    C = loc(P["C"])
    return {"a": a, "b": C[0] - B[0], "h": sgn * B[1], "s": B[0]}


def _build(typ, q):
    if typ == "par":
        r = math.radians(q["al"])
        B = (q["b"] * math.cos(r), q["b"] * math.sin(r))
        return {"A": (0.0, 0.0), "B": B, "C": (B[0] + q["a"], B[1]), "D": (q["a"], 0.0)}
    s = (q["a"] - q["b"]) / 2 if typ == "isotrap" else (0.0 if typ == "rtrap" else q["s"])
    return {"A": (0.0, 0.0), "B": (s, q["h"]), "C": (s + q["b"], q["h"]), "D": (q["a"], 0.0)}


def _half(x: float) -> bool:
    return abs(2 * x - round(2 * x)) < 1e-9


def _ctg(d: float) -> float:
    return 1 / math.tan(math.radians(d))


def _variants(typ, q):
    top = int(2 * max(q["a"], q["b"])) * 2 + 8
    ab_ok = _half(q["a"]) and _half(q["b"])
    if typ == "par":
        for g in range(1, 180):
            yield dict(q, al=float(g))
        if ab_ok:
            for i in range(1, top):
                for j in range(1, top):
                    yield dict(q, a=i / 2, b=j / 2)
        for dq in ({"al": q["al"] + 3.7}, {"al": q["al"] - 2.9}, {"a": q["a"] * 1.07}, {"b": q["b"] * 1.09},
                   {"a": q["a"] + 0.3, "b": q["b"] - 0.3}, {"a": q["a"] * 1.05, "b": q["b"] * 1.05}, {"a": q["a"] + 0.4, "b": q["b"] + 0.4}):
            yield dict(q, **dq)
        # поворот диагоналей: AC и BD те же, угол между ними другой
        r = math.radians(q["al"])
        B, D = (q["b"] * math.cos(r), q["b"] * math.sin(r)), (q["a"], 0.0)
        u, v = _mid(B, D), _sb(D, _mid(B, D))  # O − A и половина BD
        p1, p2 = _ln(u), _ln(v)
        phi = math.degrees(math.atan2(_cr(u, v), _dt(u, v)))
        for dphi in (-13.0, -7.0, 7.0, 13.0):
            f = math.radians(phi + dphi)
            uu, vv = (p1, 0.0), (p2 * math.cos(f), p2 * math.sin(f))
            AD, AB = (uu[0] + vv[0], uu[1] + vv[1]), (uu[0] - vv[0], uu[1] - vv[1])
            if _ln(AB) > 1e-6 and abs(_cr(AD, AB)) > 1e-6:
                yield dict(q, a=_ln(AD), b=_ln(AB), al=_an(AD, (0.0, 0.0), AB))
        return
    a, h = q["a"], q["h"]
    if typ == "trap":
        for A_ in range(1, 180):
            for D_ in range(1, 180):
                s = h * _ctg(A_)
                b = a - s - h * _ctg(D_)
                if b > 1e-6:
                    yield dict(q, s=s, b=b)
    elif typ == "isotrap":
        for A_ in range(1, 90):
            b = a - 2 * h * _ctg(A_)
            if b > 1e-6:
                yield dict(q, b=b)
    else:
        for D_ in range(1, 180):
            b = a - h * _ctg(D_)
            if b > 1e-6:
                yield dict(q, b=b)
    if ab_ok:
        for i in range(1, top):
            for j in range(1, top):
                yield dict(q, a=i / 2, b=j / 2)
    for dq in ({"s": q["s"] + 0.37}, {"h": h * 1.08}, {"a": a + 0.3, "b": q["b"] - 0.3}, {"a": a + 0.3, "b": q["b"] + 0.3},
               {"a": a * 1.06, "b": q["b"] * 1.06, "h": h * 1.06, "s": q["s"] * 1.06}):
        yield dict(q, **dq)


def _unique(P0, typ, g, want):
    q = _params(P0, typ)
    Pq = _build(typ, q)
    for x, y in itertools.combinations(_VV, 2):
        if not _cl(_ds(P0[x], P0[y]), _ds(Pq[x], Pq[y]), 1e-8):
            raise _Bad("фигура не восстанавливается по своим размерам")
    hits = 0
    for q2 in _variants(typ, q):
        try:
            P = _derive(_build(typ, q2), g["def"])
            if not all(_holds(f, P, g) for f in g["facts"]):
                continue
            _check_type(P, typ)
        except _Bad:
            continue
        except (ZeroDivisionError, ValueError):
            continue
        v = _meas(g["ask"], P, g)
        if not _cl(v, want, 1e-8):
            raise _Bad(f"ответ не единственный: фигура {({k: round(x, 4) for k, x in q2.items()})} с тем же условием даёт {v:.6g}")
        hits += 1
    return hits


# ---------- признаки параллелограмма: теоремы и контрпримеры

def _norm_seg(s: str) -> str:
    return "".join(sorted(s))


def _norm_atom(at):
    k = at[0]
    if k in ("par", "eq", "perp"):
        return (k,) + tuple(sorted([_norm_seg(at[1]), _norm_seg(at[2])]))
    return (k,) + tuple(sorted(at[1:]))


_THEOREMS = [
    {("par", "AB", "CD"), ("par", "AD", "BC")},   # определение
    {("par", "AB", "CD"), ("eq", "AB", "CD")},    # признак 1
    {("par", "AD", "BC"), ("eq", "AD", "BC")},    # признак 1
    {("eq", "AB", "CD"), ("eq", "AD", "BC")},     # признак 2
    {("eq", "AO", "CO"), ("eq", "BO", "DO")},     # признак 3
]

# выпуклые четырёхугольники, которые НЕ параллелограммы
_CE = [
    {"A": (0, 0), "B": (2, 3), "C": (5, 3), "D": (7, 0)},      # равнобедренная трапеция, основания AD и BC
    {"A": (0, 0), "B": (7, 0), "C": (5, 3), "D": (2, 3)},      # равнобедренная трапеция, основания AB и CD
    {"A": (0, 0), "B": (1, 3), "C": (4, 3), "D": (8, 0)},      # трапеция AD ∥ BC
    {"A": (0, 0), "B": (8, 0), "C": (5, 3), "D": (1, 3)},      # трапеция AB ∥ CD
    {"A": (-2, 0), "B": (0, 3), "C": (2, 0), "D": (0, -5)},    # дельтоид, ось BD
    {"A": (-3, 0), "B": (0, 2), "C": (5, 0), "D": (0, -2)},    # дельтоид, ось AC
    {"A": (-2, 0), "B": (0, 1), "C": (2, 0), "D": (0, -3)},    # дельтоид с равными перпендикулярными диагоналями
    {"A": (-3, 0), "B": (-1, 4), "C": (1, 4), "D": (3, 0)},    # равнобедренная трапеция с перпендикулярными диагоналями
    {"A": (0, 0), "B": (1, 4), "C": (6, 5), "D": (7, 1)},      # произвольный
]


def _atom_ok(at, P) -> bool:
    k = at[0]
    if k in ("par", "eq", "perp"):
        u, w = _sb(P[at[1][1]], P[at[1][0]]), _sb(P[at[2][1]], P[at[2][0]])
        if k == "par":
            return abs(_cr(u, w)) <= 1e-9 * _ln(u) * _ln(w)
        if k == "perp":
            return abs(_dt(u, w)) <= 1e-9 * _ln(u) * _ln(w)
        return _cl(_ln(u), _ln(w))
    if k == "eqang":
        return _cl(_iang(P, at[1]), _iang(P, at[2]))
    if k == "sup":
        return _cl(_iang(P, at[1]) + _iang(P, at[2]), 180.0)
    raise _Bad(f"неизвестное условие {at}")


def _render_atom(at) -> str:
    k = at[0]
    return {"par": f"${at[1]}\\parallel {at[2]}$", "eq": f"${at[1]}={at[2]}$", "perp": f"${at[1]}\\perp {at[2]}$",
            "eqang": f"$\\angle {at[1]}=\\angle {at[2]}$", "sup": f"$\\angle {at[1]}+\\angle {at[2]}=180^\\circ$"}[k]


def _verify_signs(t, g):
    opts = g["opts"]
    if t["answerKind"] != "choice" or len(opts) != len(t["options"]) or len(opts) < 3:
        raise _Bad("варианты не совпадают с данными")
    for i, atoms in enumerate(opts):
        if t["options"][i] != " и ".join(_render_atom(a) for a in atoms):
            raise _Bad(f"вариант {i} в тексте не совпадает с данными")
    neg = "НЕ гарантирует" in t["prompt"]
    if neg != g["neg"] or "гарантирует, что четырёхугольник $ABCD$ — параллелограмм" not in t["prompt"]:
        raise _Bad("вопрос не совпадает с данными")
    for Qd in _CE:
        Pq = {k: (float(x), float(y)) for k, (x, y) in Qd.items()}
        _check_ce(Pq)
    verdict = []
    for atoms in opts:
        norm = {_norm_atom(a) for a in atoms}
        thm = any(th <= norm for th in _THEOREMS)
        ce = False
        for Qd in _CE:
            Pq = _derive({k: (float(x), float(y)) for k, (x, y) in Qd.items()}, {"O": ["x", "AC", "BD"]})
            if all(_atom_ok(a, Pq) for a in atoms):
                ce = True
        if thm == ce:
            raise _Bad(f"вариант {atoms}: теорема {thm}, контрпример {ce} — не могу решить")
        verdict.append(thm)
    right = [i for i, ok in enumerate(verdict) if ok != neg]
    if right != [int(t["answer"])]:
        raise _Bad(f"верные варианты {right}, в ответе {t['answer']}")
    if any("O" in s for atoms in opts for a in atoms for s in a[1:]) and "точка пересечения диагоналей" not in t["prompt"]:
        raise _Bad("в вариантах есть точка O, а в тексте не сказано, что это")


def _check_ce(P):
    pts = [P[c] for c in _VV]
    cr = [_cr(_sb(pts[(i + 1) % 4], pts[i]), _sb(pts[(i + 2) % 4], pts[(i + 1) % 4])) for i in range(4)]
    if not (all(c > 0 for c in cr) or all(c < 0 for c in cr)):
        raise _Bad("контрпример не выпуклый")
    A, B, C, D = pts
    if _cl(B[0] - A[0], C[0] - D[0]) and _cl(B[1] - A[1], C[1] - D[1]):
        raise _Bad("контрпример оказался параллелограммом")


def _verify(t):
    g = t.get("geo")
    if not g:
        raise _Bad("нет поля geo")
    if not t.get("fig") or t["fig"]["id"] not in ("par", "trap"):
        raise _Bad("нет рисунка par/trap")
    if g["type"] == "signs":
        _verify_signs(t, g)
        return
    typ = g["type"]
    if t["answerKind"] != "expr":
        raise _Bad("ответ должен быть числом")
    P0 = {k: (float(x), float(y)) for k, (x, y) in g["V"].items()}
    P = _derive(P0, g["def"])
    _check_type(P, typ)
    for f in g["facts"]:
        if not _holds(f, P, g):
            raise _Bad(f"в фигуре не выполняется условие {f}")
    _ties(t, g, typ)
    want = _meas(g["ask"], P, g)
    got = Fraction(t["answer"])
    if not _cl(want, float(got)):
        raise _Bad(f"по координатам {want:.12g}, в ответе {t['answer']}")
    if g["ask"][0] in ("ang", "bigang", "smallang", "acute"):
        if abs(want - round(want * 2) / 2) > 1e-9:
            raise _Bad(f"угол {want} не «красивый»")
    for name, spec in g["def"].items():
        if spec[0] == "bis":
            X, side = spec[1], spec[2]
            Y = side[0] if side[0] in _NBR[X] else side[1]
            if not _cl(_ds(P[X], P[Y]), _ds(P[Y], P[name])):
                raise _Bad(f"треугольник {X}{Y}{name} не равнобедренный")
    fp = t["fig"]["props"]
    if typ == "par":
        q = _params(P0, typ)
        if not fp.get("quad") and not (abs(fp["a"] - q["a"]) < 0.01 and abs(fp["b"] - q["b"]) < 0.01 and abs(fp["ang"] - q["al"]) < 0.05):
            raise _Bad("рисунок не похож на фигуру из условия")
    else:
        q = _params(P0, typ)
        if not all(abs(fp[k] - q[k]) < 0.01 for k in ("a", "b", "h", "s")):
            raise _Bad("рисунок не похож на фигуру из условия")
    _unique(P0, typ, g, want)


def verify(t):
    try:
        _verify(t)
    except _Bad as e:
        return str(e)
    return None
