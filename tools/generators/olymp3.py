"""Олимпиадные задачи темы 3: подсчёты, сравнения «с хитростью», оценки корней. Все задания третьего уровня."""
from __future__ import annotations

import math
import random
from decimal import Decimal

from common import *  # noqa: F401,F403

SQF = [2, 3, 5, 6, 7, 10, 11, 13]
NONSQ = [x for x in range(2, 80) if not is_square(x)]


def _list(nums, limit=7) -> str:
    return ", ".join(str(v) for v in nums[:limit]) + (", \\dots" if len(nums) > limit else "")


def _r(v) -> str:
    return f"\\sqrt{{{v}}}"


# ---------- сколько чисел: иррациональных, рациональных, целых x ----------

def g_o3cnt(rng: random.Random, level: int):
    kind = rng.choice(["irr", "rat", "between"])
    if kind == "irr":
        n = rng.randint(30, 150)
        k = math.isqrt(n)
        sq = [i * i for i in range(1, k + 1)]
        sol = ["Корень из натурального числа рационален (на самом деле целый) только тогда, когда число под корнем — точный квадрат.",
               f"Точные квадраты не больше ${n}$: ${_list(sq)}$. Их ${k}$ штук, потому что ${k}^2={k * k}\\le {n}<{(k + 1) ** 2}={k + 1}^2$.",
               f"Всего чисел ${n}$, значит иррациональных ${n}-{k}={n - k}$."]
        return task(f"Сколько иррациональных чисел среди ${_r(1)},{_r(2)},{_r(3)},\\dots,{_r(n)}$?", str(n - k), "expr",
                    "Рациональны только корни из точных квадратов. Посчитай, сколько точных квадратов среди чисел от 1 до N, и вычти из общего количества.",
                    sol, ["sqrt-def", "irrational"], olyCheck={"kind": "irrCount", "a": 1, "b": n})
    if kind == "rat":
        a = rng.randint(10, 80)
        b = a + rng.randint(40, 200)
        lo, hi = math.isqrt(a - 1) + 1, math.isqrt(b)
        cnt = hi - lo + 1
        if not 3 <= cnt <= 10:
            return None
        sq = [i * i for i in range(lo, hi + 1)]
        sol = [f"Рациональны корни из точных квадратов. Выпишем квадраты от ${a}$ до ${b}$: ${_list(sq, 8)}$.",
               f"Первый подходящий: ${lo}^2={lo * lo}$ (а ${lo - 1}^2={(lo - 1) ** 2}$ меньше ${a}$). Последний: ${hi}^2={hi * hi}$ (а ${hi + 1}^2={(hi + 1) ** 2}$ больше ${b}$).",
               f"Это квадраты чисел от ${lo}$ до ${hi}$, их ${hi}-{lo}+1={cnt}$."]
        return task(f"Сколько рациональных чисел среди ${_r(a)},{_r(a + 1)},{_r(a + 2)},\\dots,{_r(b)}$?", str(cnt), "expr",
                    "Рациональны только корни из точных квадратов. Найди первый и последний квадрат в этом промежутке.",
                    sol, ["sqrt-def", "irrational"], olyCheck={"kind": "ratCount", "a": a, "b": b})
    p = rng.randint(2, 8)
    q = rng.randint(p + 2, 12)
    cnt = q * q - p * p - 1
    sol = [f"Все числа положительные, поэтому неравенство можно возвести в квадрат: ${p}^2<x<{q}^2$, то есть ${p * p}<x<{q * q}$.",
           f"Целые $x$ — от ${p * p + 1}$ до ${q * q - 1}$.",
           f"Их ${q * q - 1}-{p * p + 1}+1={cnt}$."]
    return task(f"Сколько целых значений может принимать $x$, если ${p}<\\sqrt{{x}}<{q}$?", str(cnt), "expr",
                "Возведи все три части в квадрат: корень пропадёт, и останется двойное неравенство для $x$.",
                sol, ["sqrt-def", "square-both"], olyCheck={"kind": "intBetween", "lo": p * p, "hi": q * q})


# ---------- сколько целых чисел между a√b и c√d ----------

def g_o3btw(rng: random.Random, level: int):
    a, c = rng.randint(2, 5), rng.randint(2, 6)
    b, d = rng.choice(SQF), rng.choice(SQF)
    A, B = a * a * b, c * c * d
    if A >= B:
        return None
    lo, hi = math.isqrt(A) + 1, math.isqrt(B)
    cnt = hi - lo + 1
    if not 2 <= cnt <= 7:
        return None
    ns = list(range(lo, hi + 1))
    sol = [f"Внесём множители под корень: ${a}{_r(b)}=\\sqrt{{{a * a}\\cdot {b}}}={_r(A)}$ и ${c}{_r(d)}=\\sqrt{{{c * c}\\cdot {d}}}={_r(B)}$.",
           f"Целое число $n$ лежит между ними, когда ${A}<n^2<{B}$ (числа положительные, поэтому квадраты сравнивать можно).",
           f"Подходят $n={_list(ns, 8)}$: ${lo}^2={lo * lo}>{A}$ и ${hi}^2={hi * hi}<{B}$, а ${lo - 1}^2={(lo - 1) ** 2}$ уже мало, ${hi + 1}^2={(hi + 1) ** 2}$ уже много.",
           f"Таких чисел ${cnt}$."]
    return task(f"Сколько целых чисел расположено между числами ${a}{_r(b)}$ и ${c}{_r(d)}$?", str(cnt), "expr",
                "Внеси множители под корень и найди, какие квадраты целых чисел лежат между получившимися подкоренными числами.",
                sol, ["compare-roots", "bring-under-root"], olyCheck={"kind": "intBetweenExpr", "lo": f"{a}*sqrt({b})", "hi": f"{c}*sqrt({d})"})


# ---------- сравнить хитро ----------

def g_o3dif(rng: random.Random, level: int):
    kind = rng.choice(["diff", "sumint", "concave"])
    if kind == "diff":
        k = rng.choice([1, 1, 2, 3])
        n = rng.randint(1, 80)
        a, b, c = n, n + k, n + 2 * k
        if any(is_square(v) for v in (a, b, c)):
            return None
        sol = [f"Умножим и разделим первую разность на сопряжённое выражение: ${_r(c)}-{_r(b)}=\\dfrac{{({_r(c)}-{_r(b)})({_r(c)}+{_r(b)})}}{{{_r(c)}+{_r(b)}}}=\\dfrac{{{c}-{b}}}{{{_r(c)}+{_r(b)}}}=\\dfrac{{{k}}}{{{_r(c)}+{_r(b)}}}$.",
               f"Так же для второй: ${_r(b)}-{_r(a)}=\\dfrac{{{k}}}{{{_r(b)}+{_r(a)}}}$.",
               f"Числители одинаковые (${k}$), а знаменатель первой дроби ${_r(c)}+{_r(b)}$ больше знаменателя второй ${_r(b)}+{_r(a)}$, потому что ${c}>{a}$. Значит, первая дробь меньше.",
               "Поэтому первая разность меньше второй: чем дальше от нуля, тем «ближе друг к другу» стоят корни."]
        return task("Сравните числа {expr} и {expr2}.", "<", "compare",
                    "Каждую разность корней превращай в дробь с числителем 1 (или $k$): умножь и раздели на сумму тех же корней.",
                    sol, ["compare-roots", "rationalize"], expr=f"sqrt({c})-sqrt({b})", expr2=f"sqrt({b})-sqrt({a})")
    if kind == "sumint":
        m = rng.randint(4, 9)
        for _ in range(200):
            a, b = rng.sample([v for v in range(2, m * m - 2) if not is_square(v)], 2)
            D = m * m - a - b
            if D <= 0:
                continue
            X, Y = 4 * a * b, D * D
            if X == Y or abs(X - Y) > 0.35 * max(X, Y):
                continue
            break
        else:
            return None
        sgn = ">" if X > Y else "<"
        sol = [f"Обе части положительные, поэтому сравним их квадраты: $({_r(a)}+{_r(b)})^2={a}+{b}+2{_r(a * b)}={a + b}+2{_r(a * b)}$ и ${m}^2={m * m}$.",
               f"Вычтем ${a + b}$ из обеих частей: сравниваем $2{_r(a * b)}$ и ${D}$.",
               f"Обе части положительные, возведём в квадрат ещё раз: $4\\cdot {a * b}={X}$ и ${D}^2={Y}$.",
               f"${X}\\ {sgn}\\ {Y}$, значит ${_r(a)}+{_r(b)}\\ {sgn}\\ {m}$."]
        return task("Сравните числа {expr} и {expr2}.", sgn, "compare",
                    "Возводи в квадрат обе части (они положительные), пока корни не пропадут: сначала сумма, потом оставшийся корень.",
                    sol, ["compare-roots", "square-both"], expr=f"sqrt({a})+sqrt({b})", expr2=str(m))
    m = rng.randint(30, 3000)
    k = rng.randint(1, 5)
    first = rng.random() < 0.5
    M = m * m - k * k
    sol = [f"Обе части положительные, возведём в квадрат: $({_r(m - k)}+{_r(m + k)})^2={m - k}+{m + k}+2\\sqrt{{{m - k}\\cdot {m + k}}}={2 * m}+2{_r(M)}$.",
           f"$(2{_r(m)})^2=4\\cdot {m}={4 * m}$.",
           f"Сравним ${2 * m}+2{_r(M)}$ и ${4 * m}$, то есть $2{_r(M)}$ и ${2 * m}$, то есть ${_r(M)}$ и ${m}$.",
           f"${M}<{m * m}={m}^2$ (разность квадратов $m^2-k^2$ меньше $m^2$), значит ${_r(M)}<{m}$ и сумма корней **меньше**, чем $2{_r(m)}$."]
    e1, e2 = f"sqrt({m - k})+sqrt({m + k})", f"2*sqrt({m})"
    if not first:
        e1, e2 = e2, e1
    return task("Сравните числа {expr} и {expr2}.", "<" if first else ">", "compare",
                "Возведи обе части в квадрат. Помни: $(a-b)(a+b)=a^2-b^2$ — под одним корнем получится число чуть меньше $m^2$.",
                sol, ["compare-roots", "square-both", "fsu"], expr=e1, expr2=e2)


# ---------- целая часть суммы корней ----------

def g_o3int(rng: random.Random, level: int):
    for _ in range(300):
        a, b = sorted(rng.sample(NONSQ, 2))
        ta, tb = math.isqrt(100 * a), math.isqrt(100 * b)
        lo10, hi10 = ta + tb, ta + tb + 2
        m = lo10 // 10
        if hi10 > 10 * (m + 1):
            continue

        def line(v, t):
            lo, hi = Decimal(t) / 10, Decimal(t + 1) / 10
            return (f"${dec_tex(lo)}^2={dec_tex(lo * lo)}<{v}<{dec_tex(hi * hi)}={dec_tex(hi)}^2$, значит ${dec_tex(lo)}<{_r(v)}<{dec_tex(hi)}$.")

        sol = ["Оценим каждый корень с точностью до десятых: найдём два соседних числа с одним знаком после запятой, между квадратами которых лежит подкоренное число.",
               line(a, ta), line(b, tb),
               f"Складываем неравенства: ${dec_tex(Decimal(lo10) / 10)}<{_r(a)}+{_r(b)}<{dec_tex(Decimal(hi10) / 10)}$.",
               f"Число больше ${m}$ и меньше ${m + 1}$, значит его целая часть равна ${m}$."]
        return task(f"Найдите целую часть числа ${_r(a)}+{_r(b)}$.", str(m), "expr",
                    "Оцени каждый корень с точностью до десятых (возводи в квадрат числа вида 4,1; 4,2; …) и сложи оценки.",
                    sol, ["sqrt-def", "compare-roots"], olyCheck={"kind": "floor", "expr": f"sqrt({a})+sqrt({b})"})
    return None


OLYMPIAD = [
    ("o3cnt", "⭐ Сколько чисел", g_o3cnt, 7),
    ("o3btw", "⭐ Сколько целых между", g_o3btw, 7),
    ("o3dif", "⭐ Сравни хитро", g_o3dif, 7),
    ("o3int", "⭐ Целая часть суммы", g_o3int, 7),
]
