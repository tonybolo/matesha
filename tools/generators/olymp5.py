"""Олимпиадные задачи темы 5: теорема Виета, параметры, числа по сумме и произведению, биквадратные уравнения."""
from __future__ import annotations

import math
import random
from decimal import Decimal
from fractions import Fraction

from common import *  # noqa: F401,F403

RES = "Если корней несколько, запишите их через «;», если корней нет — напишите «нет»."
RES_SOME = "Если значений несколько, запишите их через «;»."
NZ = [i for i in range(-9, 10) if i != 0]


def _fr(v: Fraction) -> str:
    t = tex_num(v)
    return f"({t})" if v < 0 else t


def _dec_or_frac(v: Fraction) -> str:
    if v.denominator in (1, 2, 4, 5, 8, 10):
        return dec_tex(Decimal(v.numerator) / Decimal(v.denominator))
    return tex_num(v)


def _bterm(b: int, v: str = "x") -> str:
    return ("+" if b > 0 else "-") + ("" if abs(b) == 1 else str(abs(b))) + v


# ---------- теорема Виета: не решая уравнения ----------

VIETA = [
    ("x_1^2+x_2^2", "x1**2+x2**2", lambda s, p: s * s - 2 * p,
     "(x_1+x_2)^2-2x_1x_2", lambda s, p: f"{_fr(s)}^2-2\\cdot {_fr(p)}"),
    ("\\dfrac{1}{x_1}+\\dfrac{1}{x_2}", "1/x1+1/x2", lambda s, p: s / p,
     "\\dfrac{x_1+x_2}{x_1x_2}", lambda s, p: f"\\dfrac{{{tex_num(s)}}}{{{tex_num(p)}}}"),
    ("(x_1-x_2)^2", "(x1-x2)**2", lambda s, p: s * s - 4 * p,
     "(x_1+x_2)^2-4x_1x_2", lambda s, p: f"{_fr(s)}^2-4\\cdot {_fr(p)}"),
    ("x_1^3+x_2^3", "x1**3+x2**3", lambda s, p: s**3 - 3 * s * p,
     "(x_1+x_2)^3-3x_1x_2(x_1+x_2)", lambda s, p: f"{_fr(s)}^3-3\\cdot {_fr(p)}\\cdot {_fr(s)}"),
    ("\\dfrac{x_1}{x_2}+\\dfrac{x_2}{x_1}", "x1/x2+x2/x1", lambda s, p: (s * s - 2 * p) / p,
     "\\dfrac{x_1^2+x_2^2}{x_1x_2}=\\dfrac{(x_1+x_2)^2-2x_1x_2}{x_1x_2}", lambda s, p: f"\\dfrac{{{_fr(s)}^2-2\\cdot {_fr(p)}}}{{{_fr(p)}}}"),
    ("x_1^2x_2+x_1x_2^2", "x1**2*x2+x1*x2**2", lambda s, p: s * p,
     "x_1x_2(x_1+x_2)", lambda s, p: f"{_fr(p)}\\cdot {_fr(s)}"),
]


def g_o5vie(rng: random.Random, level: int):
    tex, f_sym, f, formula, subst = rng.choice(VIETA)
    a = rng.choice([1, 1, 2, 3])
    b = rng.choice(NZ)
    c = rng.choice(NZ)
    D = b * b - 4 * a * c
    if D <= 0:
        return None
    if is_square(D) and rng.random() < 0.75:
        return None  # чаще корни иррациональные: решать «в лоб» неудобно, нужна теорема Виета
    s, p = Fraction(-b, a), Fraction(c, a)
    value = f(s, p)
    if value.denominator > 30 or abs(value) > 300:
        return None
    sol = disc_steps(a, b, c)[1:] + [
        "$D>0$, значит корни есть. Искать их не нужно.",
        f"По теореме Виета: $x_1+x_2=-\\dfrac{{b}}{{a}}={tex_num(s)}$ и $x_1x_2=\\dfrac{{c}}{{a}}={tex_num(p)}$.",
        f"${tex}={formula}={subst(s, p)}={tex_num(value)}$.",
    ]
    return task(f"Не решая уравнения ${poly_tex(a, b, c)}=0$, найдите значение выражения ${tex}$, где $x_1$ и $x_2$ — корни этого уравнения.",
                ans(value), "expr",
                "Запиши $x_1+x_2=-\\frac{b}{a}$ и $x_1x_2=\\frac{c}{a}$, а нужное выражение выразь через сумму и произведение корней.",
                sol, ["vieta", "discriminant"], vieta={"abc": [a, b, c], "f": f_sym})


# ---------- параметры ----------

def g_o5par(rng: random.Random, level: int):
    kind = rng.choice(["p_root", "other", "one", "one", "dmax", "dmax"])
    if kind == "p_root":
        x0 = rng.choice(NZ)
        x1 = rng.choice([i for i in NZ if i != x0 and i != -x0])
        b, pp = -(x0 + x1), x0 * x1
        eq_t = f"x^2{_bterm(b)}+p=0"
        eq_app = f"x^2{'+' if b > 0 else '-'}{abs(b)}*x+p"
        sol = [f"Корень обращает уравнение в верное равенство, поэтому подставим $x={x0}$.",
               f"${par(x0)}^2{'+' if b > 0 else '-'}{abs(b)}\\cdot {par(x0)}+p=0$, то есть ${x0 * x0 + b * x0}+p=0$, откуда $p={-(x0 * x0 + b * x0)}$.",
               f"Проверка по теореме Виета: второй корень ${x1}$ и произведение корней ${par(x0)}\\cdot {par(x1)}={pp}$."]
        return task(f"Один из корней уравнения ${eq_t}$ равен ${x0}$. Найдите $p$.", str(pp), "expr",
                    "Подставь известный корень вместо $x$ и реши получившееся уравнение относительно $p$.",
                    sol, ["vieta", "quad-formula"], paramCheck={"kind": "subs", "eq": eq_app, "x0": x0, "param": "p"})
    if kind == "other":
        x0 = rng.choice(NZ)
        x1 = rng.choice([i for i in NZ if i != x0])
        c, pc = x0 * x1, -(x0 + x1)
        eq_t = f"x^2+px{'+' if c > 0 else '-'}{abs(c)}=0"
        eq_app = f"x^2+p*x{'+' if c > 0 else '-'}{abs(c)}"
        sol = [f"По теореме Виета произведение корней равно свободному члену: $x_1x_2={c}$.",
               f"Один корень равен ${x0}$, поэтому второй равен ${c}:{par(x0)}={x1}$.",
               f"(Заодно $p=-(x_1+x_2)=-({x0}+{par(x1)})={pc}$, но для ответа это не нужно.)"]
        return task(f"Один из корней уравнения ${eq_t}$ равен ${x0}$. Найдите второй корень.", str(x1), "expr",
                    "Не обязательно искать $p$: произведение корней равно свободному члену (теорема Виета).",
                    sol, ["vieta"], paramCheck={"kind": "other", "eq": eq_app, "x0": x0, "param": "p"})
    if kind == "one":
        form = rng.choice(["A", "B", "C"])
        if form == "A":
            b = rng.choice([-12, -10, -8, -6, -4, -2, 2, 4, 6, 8, 10, 12])
            kv = (b // 2) ** 2
            sol = ["Квадратное уравнение имеет ровно один корень, когда $D=0$.",
                   f"$D={b}^2-4\\cdot 1\\cdot k={b * b}-4k$. Приравниваем к нулю: ${b * b}-4k=0$.",
                   f"$4k={b * b}$, откуда $k={kv}$."]
            return task(f"При каком значении $k$ уравнение $x^2{_bterm(b)}+k=0$ имеет ровно один корень?", str(kv), "expr",
                        "Один корень — это $D=0$. Выпиши $D$ как выражение с $k$ и приравняй к нулю.",
                        sol, ["discriminant"], paramCheck={"kind": "D0", "a": "1", "b": str(b), "c": "k"})
        if form == "B":
            pairs = [(b, c) for b in (-12, -10, -8, -6, -4, 4, 6, 8, 10, 12) for c in (-9, -8, -6, -4, -3, -2, 1, 2, 3, 4, 6, 8, 9)
                     if (b * b) % (4 * c) == 0 and 1 <= abs(b * b // (4 * c)) <= 16 and b * b // (4 * c) != 1]
            b, c = rng.choice(pairs)
            kv = b * b // (4 * c)
            sol = ["Уравнение квадратное ($k\\ne 0$) и имеет ровно один корень, когда $D=0$.",
                   f"$D={b}^2-4\\cdot k\\cdot {par(c)}={b * b}{'+' if c < 0 else '-'}{abs(4 * c)}k$. Приравниваем к нулю.",
                   f"${abs(4 * c)}k={b * b}$, откуда $k={kv}$." if c > 0 else f"${abs(4 * c)}k=-{b * b}$, откуда $k={kv}$.",
                   f"Значение $k={kv}$ не равно нулю, значит уравнение действительно квадратное."]
            return task(f"При каком значении $k$ уравнение $kx^2{_bterm(b)}{'+' if c > 0 else '-'}{abs(c)}=0$ имеет ровно один корень?", str(kv), "expr",
                        "Один корень — это $D=0$; при этом коэффициент при $x^2$ не должен быть нулём.",
                        sol, ["discriminant"], paramCheck={"kind": "D0", "a": "k", "b": str(b), "c": str(c)})
        m = rng.randint(2, 9)
        sol = ["Один корень — это $D=0$.",
               f"$D=k^2-4\\cdot 1\\cdot {m * m}=k^2-{4 * m * m}$. Приравниваем к нулю: $k^2={4 * m * m}$.",
               f"$k={2 * m}$ или $k=-{2 * m}$ (подходят оба значения)."]
        return task(f"При каких значениях $k$ уравнение $x^2+kx+{m * m}=0$ имеет ровно один корень? {RES_SOME}", f"{2 * m}; {-2 * m}", "roots",
                    "Один корень — это $D=0$. Уравнение $k^2=$ число имеет два решения.",
                    sol, ["discriminant"], paramCheck={"kind": "D0", "a": "1", "b": "k", "c": str(m * m)})
    # dmax: наибольшее целое, при котором два корня; или (не) имеет корней
    form = rng.choice(["A", "A", "B"])
    if form == "A":
        a = rng.choice([1, 1, 2])
        b = rng.choice([i for i in range(-10, 11) if abs(i) >= 3])
        bound = Fraction(b * b, 4 * a)
        kmax = math.ceil(bound) - 1
        lead = "" if a == 1 else str(a)
        sol = ["Два различных корня бывают, когда $D>0$.",
               f"$D={b}^2-4\\cdot {a}\\cdot k={b * b}-{4 * a}k>0$, откуда ${4 * a}k<{b * b}$ и $k<{_dec_or_frac(bound)}$.",
               f"Наибольшее целое число, которое **строго меньше** ${_dec_or_frac(bound)}$, это ${kmax}$."]
        return task(f"Найдите наибольшее целое значение $k$, при котором уравнение ${lead}x^2{_bterm(b)}+k=0$ имеет два различных корня.", str(kmax), "expr",
                    "Два корня — это $D>0$. Реши неравенство относительно $k$ и выбери наибольшее целое (неравенство строгое!).",
                    sol, ["discriminant"], paramCheck={"kind": "Dgt", "a": str(a), "b": str(b), "c": "k", "cmp": ">", "ask": "max"})
    c = rng.randint(5, 40)
    m = math.isqrt(4 * c - 1)
    ask = rng.choice(["min", "max", "count"])
    word = {"min": "Найдите наименьшее целое значение $k$", "max": "Найдите наибольшее целое значение $k$", "count": "Сколько целых значений может принимать $k$"}[ask]
    ans_v = {"min": -m, "max": m, "count": 2 * m + 1}[ask]
    sol = ["Корней нет, когда $D<0$.",
           f"$D=k^2-4\\cdot 1\\cdot {c}=k^2-{4 * c}<0$, откуда $k^2<{4 * c}$.",
           f"Ближайшие квадраты: ${m}^2={m * m}<{4 * c}$, а ${m + 1}^2={(m + 1) ** 2}>{4 * c}$. Значит, подходят целые $k$ от $-{m}$ до ${m}$.",
           {"min": f"Наименьшее из них $-{m}$.", "max": f"Наибольшее из них ${m}$.", "count": f"Их ${m}+{m}+1={2 * m + 1}$ (от $-{m}$ до ${m}$ и ещё ноль)."}[ask]]
    return task(f"{word}, при которых уравнение $x^2+kx+{c}=0$ не имеет корней{'?' if ask == 'count' else '.'}", str(ans_v), "expr",
                "Нет корней — это $D<0$. Получится $k^2<$ число: подумай, какие целые $k$ подходят, не забудь отрицательные.",
                sol, ["discriminant"], paramCheck={"kind": "Dgt", "a": "1", "b": "k", "c": str(c), "cmp": "<", "ask": ask})


# ---------- два числа по сумме и произведению ----------

def g_o5two(rng: random.Random, level: int):
    kind = rng.choice(["sumprod", "sumsq", "diffprod"])
    if kind in ("sumprod", "sumsq"):
        u, v = sorted(rng.sample([i for i in range(-12, 13) if i != 0], 2))
        S, P = u + v, u * v
        if S == 0:
            return None
        head = []
        if kind == "sumprod":
            story = f"Сумма двух чисел равна ${S}$, а их произведение равно ${P}$. Найдите эти числа. {RES_SOME}"
            check = {"kind": "sumprod", "S": S, "P": P}
        else:
            Q = u * u + v * v
            story = f"Сумма двух чисел равна ${S}$, а сумма их квадратов равна ${Q}$. Найдите эти числа. {RES_SOME}"
            check = {"kind": "sumsq", "S": S, "Q": Q}
            head = [f"Из $(x+y)^2=x^2+y^2+2xy$ получаем $2xy={par(S)}^2-{Q}={S * S - Q}$, то есть произведение равно ${P}$."]
        sol = head + [
            f"Пусть одно число $x$, тогда другое ${S}-x$ (их сумма равна ${S}$).",
            f"Произведение: $x({S}-x)={P}$. После раскрытия скобок и переноса получаем ${poly_tex(1, -S, P)}=0$.",
        ] + disc_steps(1, -S, P)[1:] + [
            f"$\\sqrt{{D}}={abs(u - v)}$, корни $x={u}$ и $x={v}$.",
            f"Значит, числа ${u}$ и ${v}$ (второе число — это ${S}-{par(u)}={v}$).",
        ]
        return task(story, f"{u}; {v}", "roots", "Обозначь одно число за $x$, другое выразим через сумму и составь уравнение по произведению.",
                    sol, ["word-to-equation", "vieta", "quad-formula"], equation=[f"x*({S}-x)", str(P)], twoCheck=check)
    v = rng.randint(1, 12)
    u = rng.randint(v + 1, 14)
    d, P = u - v, u * v
    sol = [f"Пусть меньшее число $x$, тогда большее $x+{d}$ (разность равна ${d}$).",
           f"Произведение: $x(x+{d})={P}$, то есть $x^2+{d}x-{P}=0$.",
           f"$D={d}^2+4\\cdot {P}={d * d + 4 * P}={u + v}^2$, поэтому $x=\\dfrac{{-{d}\\pm {u + v}}}{{2}}$: $x={v}$ или $x=-{u}$.",
           f"Числа натуральные, поэтому меньшее число ${v}$, а большее ${v}+{d}={u}$."]
    return task(f"Разность двух натуральных чисел равна ${d}$, а их произведение равно ${P}$. Найдите эти числа. {RES_SOME}", f"{v}; {u}", "roots",
                "Обозначь меньшее число за $x$, большее будет $x+d$. Составь уравнение по произведению. Помни: числа натуральные.",
                sol, ["word-to-equation", "quad-formula"], twoCheck={"kind": "diffprod", "d": d, "P": P})


# ---------- биквадратные уравнения ----------

def _qtex(a: int, b: int, c: int) -> str:
    out = ""
    for coef, p in ((a, "x^4"), (b, "x^2"), (c, "")):
        if coef == 0:
            continue
        mag = abs(coef)
        out += ("-" if coef < 0 else ("+" if out else "")) + (str(mag) if (mag != 1 or p == "") else "") + p
    return out


def _qexpr(a: int, b: int, c: int) -> str:
    parts = []
    for coef, p in ((a, "x^4"), (b, "x^2"), (c, "")):
        if coef == 0:
            continue
        mag = abs(coef)
        term = f"{mag}*{p}" if p and mag != 1 else (p if p else str(mag))
        parts.append(("-" if coef < 0 else ("+" if parts else "")) + term)
    return "".join(parts)


def g_o5bq(rng: random.Random, level: int):
    kind = rng.choice(["four", "four", "two", "none"])
    mult = rng.choice([1, 1, 1, 2, 3])
    if kind == "four":
        u, v = sorted(rng.sample(range(1, 7), 2))
        t1, t2, roots = u * u, v * v, [-v, -u, u, v]
    elif kind == "two":
        u, w = rng.randint(1, 6), rng.randint(1, 30)
        t1, t2, roots = u * u, -w, [-u, u]
    else:
        w1, w2 = sorted(rng.sample(range(1, 13), 2))
        t1, t2, roots = -w2, -w1, []
    a, b, c = mult, -mult * (t1 + t2), mult * t1 * t2
    sol = [f"Сделаем замену $t=x^2$ (помни, что $t\\ge 0$). Получим обычное квадратное уравнение ${poly_tex(a, b, c, 't')}=0$."]
    sol += disc_steps(a, b, c)[1:]
    sol.append(f"$t_1={t1}$ и $t_2={t2}$.")
    for t in (t1, t2):
        if t > 0:
            r = math.isqrt(t)
            sol.append(f"$x^2={t}$, откуда $x={r}$ или $x=-{r}$.")
        else:
            sol.append(f"$x^2={t}$: квадрат не бывает отрицательным, решений нет.")
    sol.append("Ответ: " + (", ".join(f"${r}$" for r in roots) if roots else "корней нет") + ".")
    return task(f"Решите уравнение ${_qtex(a, b, c)}=0$. {RES}", "; ".join(map(str, roots)) if roots else "нет", "roots",
                "Замена $t=x^2$ приводит к квадратному уравнению. Отрицательные значения $t$ не подходят: квадрат не бывает отрицательным.",
                sol, ["quad-formula", "discriminant"], equation=[_qexpr(a, b, c), "0"])


OLYMPIAD = [
    ("o5vie", "⭐ Виета: не решая", g_o5vie, 6),
    ("o5par", "⭐ Параметр", g_o5par, 6),
    ("o5two", "⭐ Найди два числа", g_o5two, 6),
    ("o5bq", "⭐ Биквадратные", g_o5bq, 6),
]
