"""Олимпиадные задачи темы 4: корень из суммы с корнем, суммы вложенных корней, телескопическая сумма, x + 1/x."""
from __future__ import annotations

import math
import random

from common import *  # noqa: F401,F403
from topic4 import PELL, pell_simple

NS = [2, 3, 5, 6, 7]


def _r(v) -> str:
    return f"\\sqrt{{{v}}}"


def _coef(y: int) -> str:
    return "" if y == 1 else str(y)


def _nest_numbers(rng: random.Random, x_greater: bool | None = None, max_c: int = 60):
    """n, x, y: подкоренное c ± k√n = (x ± y√n)², c = x² + n·y², k = 2xy."""
    for _ in range(200):
        n = rng.choice(NS)
        x, y = rng.randint(1, 7), rng.randint(1, 4)
        c, k = x * x + n * y * y, 2 * x * y
        big = x * x > n * y * y
        if c > max_c or k > 30:
            continue
        if x_greater is not None and big != x_greater:
            continue
        return n, x, y, c, k, big
    return None


def g_o4nest(rng: random.Random, level: int):
    got = _nest_numbers(rng)
    if got is None:
        return None
    n, x, y, c, k, big = got
    plus = rng.random() < 0.5
    op = "+" if plus else "-"
    if rng.random() < 0.5:
        K = k * k * n
        if K > 500:
            return None
        inner, inner_tex = f"sqrt({K})", _r(K)
        pre = [f"Сначала вынесем множитель из-под внутреннего корня: ${_r(K)}={k}{_r(n)}$ (${K}={k * k}\\cdot {n}$), поэтому выражение равно $\\sqrt{{{c}{op}{k}{_r(n)}}}$."]
    else:
        inner, inner_tex = f"{k}*sqrt({n})", f"{k}{_r(n)}"
        pre = []
    expr = f"sqrt({c}{op}{inner})"
    if plus:
        ans_app, ans_tex = (f"{x}+{y}*sqrt({n})" if y != 1 else f"{x}+sqrt({n})"), f"{x}+{_coef(y)}{_r(n)}"
        final = [f"${c}+{k}{_r(n)}=({x}+{_coef(y)}{_r(n)})^2$, а корень из квадрата положительного числа — это само число: ответ ${x}+{_coef(y)}{_r(n)}$."]
    elif big:
        ans_app, ans_tex = (f"{x}-{y}*sqrt({n})" if y != 1 else f"{x}-sqrt({n})"), f"{x}-{_coef(y)}{_r(n)}"
        final = [f"${c}-{k}{_r(n)}=({x}-{_coef(y)}{_r(n)})^2$, и корень из квадрата — это модуль числа: $|{x}-{_coef(y)}{_r(n)}|$.",
                 f"Число ${x}-{_coef(y)}{_r(n)}$ положительное, потому что ${x}^2={x * x}>{n * y * y}=({_coef(y)}{_r(n)})^2$. Значит, ответ ${x}-{_coef(y)}{_r(n)}$."]
    else:
        ans_app, ans_tex = (f"{y}*sqrt({n})-{x}" if y != 1 else f"sqrt({n})-{x}"), f"{_coef(y)}{_r(n)}-{x}"
        final = [f"${c}-{k}{_r(n)}=({x}-{_coef(y)}{_r(n)})^2$, и корень из квадрата — это модуль числа: $|{x}-{_coef(y)}{_r(n)}|$.",
                 f"Число ${x}-{_coef(y)}{_r(n)}$ отрицательное, потому что ${x}^2={x * x}<{n * y * y}=({_coef(y)}{_r(n)})^2$. Модуль — противоположное число, ответ ${_coef(y)}{_r(n)}-{x}$."]
    sol = pre + [
        f"Подкоренное выражение — это квадрат суммы (или разности): $({'x+y' if plus else 'x-y'}{_r(n)})^2=x^2+{n}y^2{op}2xy{_r(n)}$.",
        f"Нужно подобрать $x$ и $y$: $x^2+{n}y^2={c}$ и $2xy={k}$. Подходит $x={x}$, $y={y}$: ${x}^2+{n}\\cdot {y}^2={x * x}+{n * y * y}={c}$ и $2\\cdot {x}\\cdot {y}={k}$.",
    ] + final
    return task("Упростите выражение {expr}.", ans_app, "expr",
                "Подкоренное выражение — квадрат суммы: $c\\pm k\\sqrt{n}=(x\\pm y\\sqrt{n})^2$. Подбери $x$ и $y$ и помни, что $\\sqrt{a^2}=|a|$.",
                sol, ["fsu", "abs-sqrt", "sqrt-ops"], expr=expr, radical=True, answerTex=ans_tex, verify={"op": "self"})


def g_o4sum(rng: random.Random, level: int):
    got = _nest_numbers(rng, x_greater=True)
    if got is None:
        return None
    n, x, y, c, k, _ = got
    kind = rng.choice(["sum", "diff", "prod"])
    A, B = f"sqrt({c}+{k}*sqrt({n}))", f"sqrt({c}-{k}*sqrt({n}))"
    base = [f"Упростим каждый корень: ${c}\\pm {k}{_r(n)}=({x}\\pm {_coef(y)}{_r(n)})^2$.",
            f"$\\sqrt{{{c}+{k}{_r(n)}}}={x}+{_coef(y)}{_r(n)}$ и $\\sqrt{{{c}-{k}{_r(n)}}}={x}-{_coef(y)}{_r(n)}$ (второе число положительное: ${x}^2={x * x}>{n * y * y}=({_coef(y)}{_r(n)})^2$)."]
    if kind == "sum":
        return task("Найдите значение выражения {expr}.", str(2 * x), "expr",
                    "Упрости каждый корень: подкоренное выражение — квадрат суммы или разности. Потом сложи.",
                    base + [f"Складываем: $({x}+{_coef(y)}{_r(n)})+({x}-{_coef(y)}{_r(n)})={2 * x}$ — корни взаимно уничтожаются."],
                    ["fsu", "abs-sqrt", "sqrt-ops"], expr=f"{A}+{B}", verify={"op": "self"})
    if kind == "diff":
        ans_app = f"{2 * y}*sqrt({n})"
        return task("Упростите выражение {expr}.", ans_app, "expr",
                    "Упрости каждый корень: подкоренное выражение — квадрат суммы или разности. Потом вычти.",
                    base + [f"Вычитаем: $({x}+{_coef(y)}{_r(n)})-({x}-{_coef(y)}{_r(n)})={2 * y}{_r(n)}$ — целые части взаимно уничтожаются."],
                    ["fsu", "abs-sqrt", "sqrt-ops"], expr=f"{A}-{B}", radical=True, answerTex=f"{2 * y}{_r(n)}", verify={"op": "self"})
    value = x * x - n * y * y
    return task("Найдите значение выражения {expr}.", str(value), "expr",
                "Упрости каждый корень (квадрат суммы или разности) и перемножь, или перемножь подкоренные выражения по формуле разности квадратов.",
                base + [f"Перемножаем: $({x}+{_coef(y)}{_r(n)})({x}-{_coef(y)}{_r(n)})={x}^2-({_coef(y)}{_r(n)})^2={x * x}-{n * y * y}={value}$.",
                        f"Другой способ: $\\sqrt{{a}}\\cdot\\sqrt{{b}}=\\sqrt{{ab}}$, где $ab=({c}+{k}{_r(n)})({c}-{k}{_r(n)})={c * c}-{k * k * n}={c * c - k * k * n}={value}^2$."],
                ["fsu", "abs-sqrt", "sqrt-ops"], expr=f"{A}*{B}", verify={"op": "self"})


def g_o4tel(rng: random.Random, level: int):
    a = rng.choice([1, 4, 9, 16])
    N = rng.choice([25, 36, 49, 64, 81, 100, 121, 144])
    ra, rn = math.isqrt(a), math.isqrt(N)
    ans_v = rn - ra
    s_tex = (f"\\dfrac{{1}}{{{_r(a)}+{_r(a + 1)}}}+\\dfrac{{1}}{{{_r(a + 1)}+{_r(a + 2)}}}+\\dots+\\dfrac{{1}}{{{_r(N - 1)}+{_r(N)}}}")
    sol = [f"Избавимся от корня в знаменателе у каждой дроби: $\\dfrac{{1}}{{\\sqrt{{k}}+\\sqrt{{k+1}}}}=\\dfrac{{\\sqrt{{k+1}}-\\sqrt{{k}}}}{{(k+1)-k}}=\\sqrt{{k+1}}-\\sqrt{{k}}$.",
           f"Сумма превращается в $({_r(a + 1)}-{_r(a)})+({_r(a + 2)}-{_r(a + 1)})+\\dots+({_r(N)}-{_r(N - 1)})$.",
           "Здесь всё, кроме первого и последнего слагаемых, взаимно уничтожается (минус и плюс одного и того же корня).",
           f"Остаётся ${_r(N)}-{_r(a)}={rn}-{ra}={ans_v}$."]
    return task(f"Найдите значение суммы $\\displaystyle {s_tex}$.", str(ans_v), "expr",
                "Избавься от корня в знаменателе у каждой дроби: каждое слагаемое станет разностью двух корней. Посмотри, что сократится.",
                sol, ["rationalize", "sqrt-ops"], olyCheck={"kind": "telsum", "a": a, "N": N})


def g_o4inv(rng: random.Random, level: int):
    a, q, p = pell_simple(*rng.choice([t for t in PELL if t[1] <= 10]))
    x = f"({q}+{p}*sqrt({a}))"
    kind = rng.choice(["s1", "s2", "s3", "d1"])
    xs = f"{q}+{_coef(p)}{_r(a)}"
    inv = [f"Найдём $\\dfrac{{1}}{{x}}$: умножим числитель и знаменатель на сопряжённое. $\\dfrac{{1}}{{{xs}}}=\\dfrac{{{q}-{_coef(p)}{_r(a)}}}{{{q}^2-{p * p}\\cdot {a}}}=\\dfrac{{{q}-{_coef(p)}{_r(a)}}}{{{q * q - p * p * a}}}={q}-{_coef(p)}{_r(a)}$."]
    if kind == "s1":
        return task(f"Найдите значение выражения $x+\\dfrac{{1}}{{x}}$, если $x={xs}$.", str(2 * q), "expr",
                    "Найди $\\frac1x$, домножив на сопряжённое: получится число, которое «зеркально» к $x$.",
                    inv + [f"$x+\\dfrac{{1}}{{x}}=({xs})+({q}-{_coef(p)}{_r(a)})={2 * q}$."],
                    ["rationalize", "fsu"], expr=f"{x}+1/{x}", verify={"op": "self"})
    if kind == "s2":
        return task(f"Найдите значение выражения $x^2+\\dfrac{{1}}{{x^2}}$, если $x={xs}$.", str(4 * q * q - 2), "expr",
                    "Сначала найди $x+\\frac1x$, потом возведи в квадрат: $(x+\\frac1x)^2=x^2+2+\\frac1{x^2}$.",
                    inv + [f"$x+\\dfrac{{1}}{{x}}={2 * q}$.",
                           f"Возведём в квадрат: $\\left(x+\\dfrac{{1}}{{x}}\\right)^2=x^2+2+\\dfrac{{1}}{{x^2}}$, поэтому $x^2+\\dfrac{{1}}{{x^2}}=({2 * q})^2-2={4 * q * q}-2={4 * q * q - 2}$."],
                    ["rationalize", "fsu"], expr=f"{x}^2+1/{x}^2", verify={"op": "self"})
    if kind == "s3":
        v = 8 * q**3 - 6 * q
        return task(f"Найдите значение выражения $x^3+\\dfrac{{1}}{{x^3}}$, если $x={xs}$.", str(v), "expr",
                    "Возведи $x+\\frac1x$ в куб: $(x+\\frac1x)^3=x^3+3x+\\frac3x+\\frac1{x^3}$.",
                    inv + [f"$x+\\dfrac{{1}}{{x}}={2 * q}$.",
                           f"$\\left(x+\\dfrac{{1}}{{x}}\\right)^3=x^3+3\\left(x+\\dfrac{{1}}{{x}}\\right)+\\dfrac{{1}}{{x^3}}$, значит $x^3+\\dfrac{{1}}{{x^3}}=({2 * q})^3-3\\cdot {2 * q}={8 * q ** 3}-{6 * q}={v}$."],
                    ["rationalize", "fsu"], expr=f"{x}^3+1/{x}^3", verify={"op": "self"})
    return task(f"Найдите значение выражения $x-\\dfrac{{1}}{{x}}$, если $x={xs}$.", f"{2 * p}*sqrt({a})", "expr",
                "Найди $\\frac1x$, домножив на сопряжённое, и вычти.",
                inv + [f"$x-\\dfrac{{1}}{{x}}=({xs})-({q}-{_coef(p)}{_r(a)})={2 * p}{_r(a)}$."],
                ["rationalize", "fsu"], expr=f"{x}-1/{x}", radical=True, answerTex=f"{2 * p}{_r(a)}", verify={"op": "self"})


OLYMPIAD = [
    ("o4nest", "⭐ Корень в корне", g_o4nest, 5),
    ("o4sum", "⭐ Сумма вложенных корней", g_o4sum, 5),
    ("o4tel", "⭐ Сумма дробей", g_o4tel, 5),
    ("o4inv", "⭐ Число и обратное к нему", g_o4inv, 5),
]
