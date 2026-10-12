"""Тема 5: квадратные уравнения (КР №3 B1, КР №5, КР №2 C2, классная работа №3)."""
from __future__ import annotations

import math
import random

import sympy as sp

from common import *  # noqa: F401,F403

X = SYMS["x"]
RES = "Если корней несколько, запишите их через «;», если корней нет — напишите «нет»."


def lin_tex(p, q, v="x"):
    out = ("" if p == 1 else "-" if p == -1 else str(p)) + v
    if q:
        out += ("+" if q > 0 else "-") + str(abs(q))
    return out


def lin_expr(p, q, v="x"):
    return (f"{p}*{v}" if abs(p) != 1 else (v if p == 1 else f"-{v}")) + (f"+{q}" if q > 0 else (f"-{-q}" if q < 0 else ""))


def roots_str(a, b, c):
    D = b * b - 4 * a * c
    if D < 0:
        return "нет", D
    uniq = []
    for r in sp.solve(a * X**2 + b * X + c, X):
        if r not in uniq:
            uniq.append(r)
    return "; ".join(sym_to_app(r) for r in uniq), D


def answer_tex(a, b, c):
    """Красивая запись иррациональных корней: x₁=(−b+√D)/2a; x₂=(−b−√D)/2a. None, если корни рациональные или их нет."""
    D = b * b - 4 * a * c
    if D <= 0 or is_square(D):
        return None
    return f"x_1=\\dfrac{{{-b}+\\sqrt{{{D}}}}}{{{2 * a}}};\\ x_2=\\dfrac{{{-b}-\\sqrt{{{D}}}}}{{{2 * a}}}"


def solution_dsc(a, b, c):
    D = b * b - 4 * a * c
    steps = disc_steps(a, b, c)
    if D < 0:
        steps.append("$D<0$: корней нет.")
        return steps
    if D == 0:
        x0 = sp.Rational(-b, 2 * a)
        steps.append(f"$D=0$: корень один: $x=\\dfrac{{-b}}{{2a}}=\\dfrac{{{-b}}}{{{2 * a}}}={sp.latex(x0)}$.")
        return steps
    r = math.isqrt(D)
    if r * r == D:
        steps.append(f"$\\sqrt{{D}}={r}$. Формула корней: $x_{{1,2}}=\\dfrac{{-b\\pm\\sqrt{{D}}}}{{2a}}=\\dfrac{{{-b}\\pm {r}}}{{{2 * a}}}$.")
    else:
        steps.append(f"$\\sqrt{{D}}=\\sqrt{{{D}}}$ (нацело не извлекается, так и оставляем). Формула корней: $x_{{1,2}}=\\dfrac{{-b\\pm\\sqrt{{D}}}}{{2a}}=\\dfrac{{{-b}\\pm\\sqrt{{{D}}}}}{{{2 * a}}}$.")
    rts = sp.solve(a * X**2 + b * X + c, X)
    at = answer_tex(a, b, c)
    steps.append("Ответ: " + (f"${at}$" if at else "; ".join(f"${sp.latex(x)}$" for x in rts)) + ".")
    return steps


# ---------- x² = число ----------

def g_inc(rng: random.Random, level: int):
    if level == 1:
        k, r = rng.randint(2, 6), rng.randint(2, 12)
        eq = f"{k}x^2-{k * r * r}=0"
        return task(f"Решите уравнение ${eq}$. {RES}", f"{r}; -{r}", "roots",
                    "Перенеси число вправо и раздели на коэффициент: получится $x^2=$ число. Не забудь, что корней два.",
                    [f"${k}x^2={k * r * r}$.", f"$x^2={r * r}$.", f"$x={r}$ или $x=-{r}$."], ["quad-incomplete", "sqrt-def"],
                    equation=[f"{k}*x^2-{k * r * r}", "0"])
    if level == 2:
        k, r, d = rng.randint(2, 6), rng.randint(2, 9), rng.randint(5, 40)
        c = d + k * r * r
        return task(f"Решите уравнение ${c}-{k}y^2={d}$. {RES}", f"{r}; -{r}", "roots",
                    "Перенеси $y^2$ в одну сторону, а числа в другую.",
                    [f"${k}y^2={c}-{d}={c - d}$.", f"$y^2={r * r}$.", f"$y={r}$ или $y=-{r}$."], ["quad-incomplete", "sqrt-def"],
                    equation=[f"{c}-{k}*y^2", str(d)], var="y")
    kind = rng.choice(["irr", "none", "shift"])
    if kind == "irr":
        a, m = rng.choice([2, 3, 5]), rng.choice([2, 3, 5, 6, 7, 10])
        return task(f"Решите уравнение ${a}x^2-{a * m}=0$. {RES}", f"sqrt({m}); -sqrt({m})", "roots",
                    "Получится $x^2=$ число, которое не является точным квадратом: корень так и оставляем в ответе.",
                    [f"${a}x^2={a * m}$, $x^2={m}$.", f"$x=\\sqrt{{{m}}}$ или $x=-\\sqrt{{{m}}}$."], ["quad-incomplete", "irrational"],
                    equation=[f"{a}*x^2-{a * m}", "0"])
    if kind == "none":
        a, c = rng.randint(1, 5), rng.randint(2, 30)
        return task(f"Решите уравнение ${a if a != 1 else ''}x^2+{c}=0$. {RES}", "нет", "roots",
                    "Квадрат числа не бывает отрицательным.",
                    [f"${a if a != 1 else ''}x^2=-{c}$.", "Слева неотрицательное число, справа отрицательное: корней нет."], ["quad-incomplete"],
                    equation=[f"{a}*x^2+{c}", "0"])
    p, q = rng.randint(1, 9), rng.randint(2, 9)
    return task(f"Решите уравнение $(x-{p})^2={q * q}$. {RES}", f"{p + q}; {p - q}", "roots",
                "Если квадрат выражения равен числу, то само выражение равно плюс-минус корню из этого числа.",
                [f"$x-{p}={q}$ или $x-{p}=-{q}$.", f"$x={p + q}$ или $x={p - q}$."], ["quad-incomplete", "sqrt-def"],
                equation=[f"(x-{p})^2", str(q * q)])


# ---------- ax² + bx = 0 ----------

def g_nbx(rng: random.Random, level: int):
    if level == 1:
        b = rng.randint(2, 9)
        s = rng.choice(["+", "-"])
        return task(f"Решите уравнение $x^2{s}{b}x=0$. {RES}", f"0; {-b if s == '+' else b}", "roots",
                    "Вынеси $x$ за скобку: произведение равно нулю, когда один из множителей равен нулю.",
                    [f"$x(x{s}{b})=0$.", f"$x=0$ или $x{s}{b}=0$.", f"$x=0$ или $x={-b if s == '+' else b}$."], ["quad-incomplete", "factor-common"],
                    equation=[f"x^2{s}{b}*x", "0"])
    if level == 2:
        a, b = rng.randint(2, 5), rng.randint(1, 15)
        s = rng.choice(["+", "-"])
        root = sp.Rational(-b if s == "+" else b, a)
        return task(f"Решите уравнение ${a}x^2{s}{b}x=0$. {RES}", f"0; {sym_to_app(root)}", "roots",
                    "Вынеси $x$ за скобку и приравняй каждый множитель к нулю.",
                    [f"$x({a}x{s}{b})=0$.", f"$x=0$ или ${a}x{s}{b}=0$.", f"$x=0$ или $x={sp.latex(root)}$."], ["quad-incomplete", "factor-common"],
                    equation=[f"{a}*x^2{s}{b}*x", "0"])
    a, d = rng.randint(2, 6), rng.randint(1, 4)
    b, e = rng.randint(1, 9), rng.randint(1, 9)
    if a == d or b == e:
        return None
    root = sp.Rational(e - b, a - d)
    bb = b - e
    first = f"{a - d}x^2{'+' if bb > 0 else '-'}{abs(bb)}x=0" if bb != 0 else f"{a - d}x^2=0"
    inner = f"{a - d}x{'+' if bb > 0 else '-'}{abs(bb)}"
    return task(f"Решите уравнение ${a}x^2+{b}x={d}x^2+{e}x$. {RES}", f"0; {sym_to_app(root)}", "roots",
                "Перенеси всё в левую часть и приведи подобные: получится неполное уравнение.",
                [f"Переносим всё влево и приводим подобные: ${first}$.", f"Выносим $x$: $x({inner})=0$.", f"$x=0$ или $x={sp.latex(root)}$."],
                ["quad-incomplete", "factor-common", "like-terms"], equation=[f"{a}*x^2+{b}*x", f"{d}*x^2+{e}*x"])


# ---------- полные уравнения через D ----------

def g_dsc(rng: random.Random, level: int):
    if level == 1:
        r1, r2 = rng.sample([i for i in range(-9, 10) if i != 0], 2)
        a, b, c = 1, -(r1 + r2), r1 * r2
    elif level == 2:
        a = rng.randint(2, 5)
        n1 = rng.choice([i for i in range(-12, 13) if i != 0 and i % a != 0])
        r2 = rng.choice([i for i in range(-6, 7) if i != 0])
        b, c = -(n1 + a * r2), n1 * r2
    else:
        cat = rng.choice(["zero", "neg", "irr", "big"])
        if cat == "zero":
            u, v = rng.randint(1, 6), rng.choice([i for i in range(-7, 8) if i != 0])
            a, b, c = u * u, -2 * u * v, v * v
        elif cat == "neg":
            a, b, c = rng.randint(1, 4), rng.randint(-5, 5), rng.randint(6, 12)
            if b * b - 4 * a * c >= 0:
                return None
        elif cat == "irr":
            a, b, c = rng.randint(1, 4), rng.randint(-9, 9), rng.randint(-9, 9)
            D = b * b - 4 * a * c
            if D <= 0 or is_square(D) or not squarefree(D) or c == 0 or b == 0:
                return None
        else:
            r1, r2 = rng.randint(-15, 15), rng.randint(-15, 15)
            a = rng.choice([-3, -2, 2, 3, 4])
            if r1 == r2 or r1 == 0 or r2 == 0:
                return None
            b, c = -a * (r1 + r2), a * r1 * r2
    ans_s, D = roots_str(a, b, c)
    if level == 1 and D <= 0:
        return None
    return task(f"Решите уравнение ${poly_tex(a, b, c)}=0$. {RES}", ans_s, "roots",
                "Найди $a$, $b$, $c$, посчитай $D=b^2-4ac$, потом по формуле $x=\\frac{-b\\pm\\sqrt{D}}{2a}$.",
                solution_dsc(a, b, c), ["quad-formula", "discriminant"], equation=[poly_expr(a, b, c), "0"],
                answerTex=answer_tex(a, b, c))


# ---------- сколько корней ----------

def g_cnt(rng: random.Random, level: int):
    cat = rng.choice(["neg", "zero", "pos"])
    if level == 1:
        a = 1
        if cat == "zero":
            u = rng.randint(1, 6)
            b, c = 2 * u * rng.choice([-1, 1]), u * u
        else:
            b, c = rng.randint(-6, 6), rng.randint(-8, 9)
    elif level == 2:
        a = rng.randint(2, 4)
        if cat == "zero":
            u = rng.randint(1, 4)
            b, c = 2 * a * u * rng.choice([-1, 1]), a * u * u
        else:
            b, c = rng.randint(-9, 9), rng.randint(-8, 9)
    else:
        if cat == "zero":
            u, v = rng.randint(2, 9), rng.randint(1, 7)
            a, b, c = u * u, -2 * u * v * rng.choice([-1, 1]), v * v
        else:
            a, b, c = rng.randint(2, 12), rng.randint(-40, 40), rng.randint(1, 12)
    D = b * b - 4 * a * c
    if (cat == "neg" and D >= 0) or (cat == "pos" and D <= 0) or (cat == "zero" and D != 0) or c == 0 or b == 0:
        return None
    correct = 0 if D < 0 else (1 if D == 0 else 2)
    sol = disc_steps(a, b, c)[1:] + ["$D<0$: красный свет, корней нет." if D < 0 else ("$D=0$: жёлтый свет, один корень." if D == 0 else "$D>0$: зелёный свет, два корня.")]
    return task(f"Не решая уравнения ${poly_tex(a, b, c)}=0$, найдите количество его корней.", str(correct), "choice",
                "Посчитай дискриминант $D=b^2-4ac$: красный, жёлтый или зелёный свет?", sol, ["discriminant"],
                options=["Нет корней", "Один корень", "Два корня"], quad=[a, b, c])


# ---------- со скобками ----------

def g_brk(rng: random.Random, level: int):
    lim = {1: 3, 2: 5, 3: 7}[level]
    for _ in range(300):
        p, q = rng.randint(1, lim), rng.randint(-lim, lim)
        if q == 0:
            continue
        if level == 1 and rng.random() < 0.6:
            r, s = rng.randint(1, lim * 2), rng.randint(-lim * 3, lim * 3)
            A, B, C = p * p, 2 * p * q - r, q * q - s
            rhs_tex, rhs_expr = lin_tex(r, s), lin_expr(r, s)
        else:
            r, s, t, u = (rng.randint(1, lim) for _ in range(4))
            s, u = rng.choice([-1, 1]) * s, rng.choice([-1, 1]) * u
            A, B, C = p * p - r * t, 2 * p * q - (r * u + t * s), q * q - s * u
            rhs_tex, rhs_expr = f"({lin_tex(r, s)})({lin_tex(t, u)})", f"({lin_expr(r, s)})*({lin_expr(t, u)})"
        if A <= 0 or B == 0 or C == 0:
            continue
        D = B * B - 4 * A * C
        if D <= 0:
            continue
        good = is_square(D) if level < 3 else (is_square(D) or squarefree(D))
        if not good:
            continue
        if level == 3 and rng.random() < 0.4 and is_square(D):
            continue
        ans_s, _ = roots_str(A, B, C)
        eq_tex = f"({lin_tex(p, q)})^2={rhs_tex}"
        steps = ["Раскроем скобки и перенесём всё в левую часть.", f"Получим ${poly_tex(A, B, C)}=0$."] + solution_dsc(A, B, C)[1:]
        return task(f"Решите уравнение ${eq_tex}$. {RES}", ans_s, "roots",
                    "Раскрой скобки (квадрат суммы и произведение двучленов), перенеси всё влево, приведи подобные и решай через $D$.",
                    steps, ["quad-formula", "discriminant", "fsu"], equation=[f"({lin_expr(p, q)})^2", rhs_expr],
                    answerTex=answer_tex(A, B, C))
    return None


# ---------- текстовые задачи ----------

TRIPLES = [(3, 4, 5), (5, 12, 13), (8, 15, 17), (7, 24, 25), (20, 21, 29)]


def g_wrd(rng: random.Random, level: int):
    kind = rng.choice(["bush", "rect"]) if level == 2 else (rng.choice(["bush", "num"]) if level == 1 else rng.choice(["bush2", "peri", "sumsq"]))
    if kind in ("bush", "bush2"):
        x, d = rng.randint(8, 25), rng.randint(2, 9)
        less = kind == "bush"
        N = x * (x + d) if less else x * (x - d)
        if not less and x <= d:
            return None
        rows = f"x+{d}" if less else f"x-{d}"
        txt = "меньше" if less else "больше"
        quad = f"x^2+{d}x-{N}=0" if less else f"x^2-{d}x-{N}=0"
        b = d if less else -d
        D = b * b + 4 * N
        r = math.isqrt(D)
        assert r * r == D
        roots = [(-b + r) // 2, (-b - r) // 2]
        assert x in roots
        return task(f"Фермер высадил {N} кустов малины в несколько рядов. В каждом ряду кустов на {d} {txt}, чем рядов. Сколько кустов в каждом ряду?",
                    str(x), "expr", "Обозначь за $x$ число кустов в ряду, выразим число рядов и составим уравнение «кустов в ряду · число рядов = всего».",
                    [f"Пусть в ряду $x$ кустов, тогда рядов ${rows}$.", f"$x({rows})={N}$, то есть ${quad}$.",
                     f"$D={D}$, $\\sqrt{{D}}={r}$, $x={roots[0]}$ или $x={roots[1]}$.", "Число кустов не может быть отрицательным.", f"**Ответ: {x}.**"],
                    ["word-to-equation", "quad-formula"])
    if kind == "num":
        x = rng.randint(6, 30)
        N = x * (x + 1)
        return task(f"Произведение двух последовательных натуральных чисел равно {N}. Найдите меньшее из них.", str(x), "expr",
                    "Пусть меньшее число $x$, тогда следующее $x+1$.",
                    [f"Числа $x$ и $x+1$: $x(x+1)={N}$, $x^2+x-{N}=0$.", f"$D=1+4\\cdot {N}={1 + 4 * N}={2 * x + 1}^2$.",
                     f"$x=\\dfrac{{-1\\pm{2 * x + 1}}}{{2}}$: $x={x}$ или $x=-{x + 1}$.", f"Натуральное число положительное. **Ответ: {x}.**"],
                    ["word-to-equation", "quad-formula"])
    if kind == "rect":
        p, q, rr = rng.choice(TRIPLES)
        k = rng.randint(2, 7)
        diag = rr * k
        per = 2 * k * (p + q)
        return task(f"Диагональ прямоугольника равна {diag} см. Найдите периметр прямоугольника, если одна из его сторон составляет $\\frac{{{p}}}{{{q}}}$ другой. Ответ запишите числом (в сантиметрах).",
                    str(per), "expr", "Пусть стороны $px$ и $qx$ (в нужном отношении), диагональ найдём по теореме Пифагора.",
                    [f"Пусть стороны ${p}x$ и ${q}x$. По теореме Пифагора $({p}x)^2+({q}x)^2={diag}^2$.", f"${p * p + q * q}x^2={diag * diag}$, $x^2={k * k}$, $x={k}$ (длина положительна).",
                     f"Стороны ${p * k}$ см и ${q * k}$ см, периметр $2({p * k}+{q * k})={per}$. **Ответ: {per}.**"],
                    ["word-to-equation", "pythagoras", "quad-incomplete"])
    if kind == "peri":
        u, v = rng.randint(6, 25), rng.randint(2, 20)
        if u <= v:
            return None
        P, S = 2 * (u + v), u * v
        return task(f"Периметр прямоугольника равен {P} см, а площадь {S} см². Найдите длину его большей стороны (в сантиметрах).", str(u), "expr",
                    "Если одна сторона $x$, то другая $\\frac{P}{2}-x$. Площадь равна произведению сторон.",
                    [f"Полупериметр ${u + v}$. Пусть одна сторона $x$, другая ${u + v}-x$.", f"$x({u + v}-x)={S}$, то есть $x^2-{u + v}x+{S}=0$.",
                     f"$D=({u + v})^2-4\\cdot {S}={(u + v) ** 2 - 4 * S}=({u - v})^2$, $x=\\dfrac{{{u + v}\\pm{u - v}}}{{2}}$: ${u}$ и ${v}$.", f"Большая сторона ${u}$. **Ответ: {u}.**"],
                    ["word-to-equation", "quad-formula", "vieta"])
    x = rng.randint(2, 12)
    N = x * x + (x + 1) ** 2
    return task(f"Сумма квадратов двух последовательных натуральных чисел равна {N}. Найдите меньшее из них.", str(x), "expr",
                "Пусть меньшее число $x$, следующее $x+1$: составь уравнение «сумма квадратов равна N».",
                [f"$x^2+(x+1)^2={N}$, $2x^2+2x+1={N}$, $2x^2+2x-{N - 1}=0$, $x^2+x-{(N - 1) // 2}=0$.",
                 f"$D=1+4\\cdot{(N - 1) // 2}={1 + 2 * (N - 1)}=({2 * x + 1})^2$, $x={x}$ или $x=-{x + 1}$.", f"Натуральное число положительное. **Ответ: {x}.**"],
                ["word-to-equation", "quad-formula", "fsu"])


# ---------- уравнение с дробью (КР №2 C2) ----------

def g_frac(rng: random.Random, level: int):
    if level == 1:
        r1, r2 = rng.randint(1, 9), -rng.randint(1, 6)
        m, k = r1 + r2, -r1 * r2
        rhs_tex = f"x-{m}" if m > 0 else (f"x+{-m}" if m < 0 else "x")
        eq_tex = f"\\frac{{{k}}}{{x}}={rhs_tex}"
        eqs = [f"{k}/x", f"x-({m})"]
        if m != 0:
            steps = [f"Умножим обе части на $x$ ($x\\ne 0$): ${k}=x^2{'-' if m > 0 else '+'}{abs(m)}x$.",
                     f"Перенесём всё влево: $x^2{'-' if m > 0 else '+'}{abs(m)}x-{k}=0$."]
        else:
            steps = [f"Умножим на $x$ ($x\\ne 0$): ${k}=x^2$.", f"$x^2-{k}=0$."]
        steps += solution_dsc(1, -m, -k)[1:]
    elif level == 2:
        a = rng.randint(2, 5)
        r = rng.randint(1, 7)
        k = a * r * r
        eq_tex = f"\\frac{{{k}}}{{x}}={a}x"
        eqs = [f"{k}/x", f"{a}*x"]
        r1, r2 = r, -r
        steps = [f"Умножим на $x$ ($x\\ne 0$): ${k}={a}x^2$, $x^2={r * r}$.", f"$x={r}$ или $x=-{r}$."]
    else:
        r1, r2 = rng.randint(1, 9), rng.randint(1, 9)
        if r1 == r2:
            return None
        eq_tex = f"x+\\frac{{{r1 * r2}}}{{x}}={r1 + r2}"
        eqs = [f"x+{r1 * r2}/x", str(r1 + r2)]
        steps = [f"Умножим на $x$ ($x\\ne 0$): $x^2+{r1 * r2}={r1 + r2}x$.", f"Перенесём всё влево: $x^2-{r1 + r2}x+{r1 * r2}=0$."] + solution_dsc(1, -(r1 + r2), r1 * r2)[1:]
    return task(f"Решите уравнение ${eq_tex}$. {RES}", f"{r1}; {r2}", "roots",
                "Умножь обе части на $x$ (помни, что $x\\ne 0$) и реши квадратное уравнение.", steps, ["quad-formula", "fraction-eq"],
                equation=eqs)


GROUPS = [
    ("inc", "x² = число", g_inc, 0),
    ("nbx", "Неполные уравнения", g_nbx, 1),
    ("dsc", "Через дискриминант", g_dsc, 3),
    ("cnt", "Сколько корней", g_cnt, 3),
    ("brk", "Со скобками", g_brk, 4),
    ("wrd", "Задачи", g_wrd, 5),
    ("frac", "С дробью", g_frac, 3),
]
