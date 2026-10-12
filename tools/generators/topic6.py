"""Тема «Произведение и частное дробей» (КР №2): умножение и деление дробей, степень дроби,
обратная пропорциональность, длинное выражение, графическое решение k/x = mx + c, выражение переменной из формулы."""
from __future__ import annotations

import math
import random
from fractions import Fraction

import sympy as sp

from common import *  # noqa: F401,F403

RES = "Если корней несколько, запишите их через «;», если корней нет — напишите «нет»."
X, A, B = SYMS["x"], SYMS["a"], SYMS["b"]


def mono(c: int, v: str, e: int) -> str:
    """Одночлен для TeX: 2a^{3}, a, 3x."""
    return ("" if c == 1 else str(c)) + v + ("" if e == 1 else f"^{{{e}}}")


def amono(c: int, v: str, e: int) -> str:
    """Тот же одночлен в записи приложения: 2*a^3."""
    parts = [] if c == 1 else [str(c)]
    parts.append(v if e == 1 else f"{v}^{e}")
    return "*".join(parts)


def _frac_tex(n: str, d: str) -> str:
    return f"\\dfrac{{{sp.latex(parse_app(n))}}}{{{sp.latex(parse_app(d))}}}"


# ---------- умножение и деление ----------

def _prod_task(n1: str, d1: str, n2: str, d2: str, op: str, level: int):
    e1, e2 = f"({n1})/({d1})", f"({n2})/({d2})"
    expr = f"({e1})*({e2})" if op == "mul" else f"({e1})/({e2})"
    tex = _frac_tex(n1, d1) + ("\\cdot " if op == "mul" else ":") + _frac_tex(n2, d2)
    e = sp.cancel(parse_app(expr))
    nn1, dd1, nn2, dd2 = (parse_app(v) for v in (n1, d1, n2, d2))
    flip = (dd2, nn2) if op == "div" else (nn2, dd2)
    fx = lambda z: sp.latex(sp.factor(z))
    sol = []
    if op == "div":
        sol.append(f"Деление заменяем умножением на перевёрнутую дробь: $\\dfrac{{{sp.latex(nn1)}}}{{{sp.latex(dd1)}}}\\cdot\\dfrac{{{sp.latex(flip[0])}}}{{{sp.latex(flip[1])}}}$.")
    parts = (nn1, dd1, flip[0], flip[1])
    if all(fx(z) == sp.latex(z) for z in parts):
        sol.append("Числители и знаменатели — одночлены, раскладывать нечего. Сокращаем одинаковые множители (у степеней с одним основанием показатели вычитаем).")
        sol.append(f"Получаем ${sp.latex(sp.factor(e))}$.")
    else:
        sol.append(f"Раскладываем на множители: $\\dfrac{{{fx(nn1)}}}{{{fx(dd1)}}}\\cdot\\dfrac{{{fx(flip[0])}}}{{{fx(flip[1])}}}$.")
        sol.append(f"Сокращаем одинаковые множители: ${sp.latex(sp.factor(e))}$.")
    answer = sym_to_app(sp.factor(e)) if level == 3 else sym_to_app(e)
    return task("Упростите выражение {expr}.", answer, "expr",
                "Если есть деление, замени его умножением на перевёрнутую дробь. Потом разложи на множители и сократи.", sol,
                ["fraction-mult", "cancel", "fsu"] if op == "mul" else ["fraction-div", "fraction-mult", "cancel"],
                expr=expr, tex=tex, reduce=True, verify={"op": "self"})


def g_mul(rng: random.Random, level: int):
    if level == 1:
        p, q = rng.randint(2, 4), rng.randint(2, 6)
        m, n = rng.randint(1, 3), rng.randint(1, 4)
        n1, d1, n2, d2 = f"{p}*a^2", f"x^{m}", f"x^{m + n}", f"{q}*a"
    elif level == 2:
        sg = rng.choice(["+", "-"])
        p, q, s, m = rng.randint(2, 6), rng.randint(2, 5), rng.randint(1, 2), rng.randint(2, 3)
        n = m + rng.randint(3, 9)
        n1, d1, n2, d2 = f"a^2{sg}{p}*a", f"x^{m}", f"{'a' if s == 1 else f'a^{s}'}*x^{n}", f"{q}*a{sg}{q * p}"
    else:
        p, q = rng.sample(range(2, 8), 2)
        n1, d1, n2, d2 = f"a^2-{p * p}", f"x^2-{q * q}", f"x+{q}", f"a+{p}"
    return _prod_task(n1, d1, n2, d2, "mul", level)


def g_div(rng: random.Random, level: int):
    if level == 1:
        p, q = rng.randint(2, 4), rng.randint(2, 6)
        m, n = rng.randint(1, 3), rng.randint(1, 4)
        n1, d1, n2, d2 = f"{p}*a^2", f"x^{m}", f"{q}*a", f"x^{m + n}"
    elif level == 2:
        sg = rng.choice(["+", "-"])
        c1, c2 = rng.randint(1, 3), rng.randint(2, 5)
        u, v = rng.sample(range(2, 7), 2)
        low = rng.randint(2, 4)
        high = low + rng.randint(1, 6)
        j = rng.randint(3, 6)
        n1, d1 = f"{u * c1}*a{sg}{u * c2}*b", f"a^{high}*x"
        n2, d2 = f"{v * c1}*a{sg}{v * c2}*b", f"a^{low}*x^{j}"
    else:
        p, q = rng.sample(range(2, 8), 2)
        n1, d1, n2, d2 = f"a^2-{p * p}", f"x^2-{q * q}", f"a+{p}", f"x-{q}"
    return _prod_task(n1, d1, n2, d2, "div", level)


# ---------- степень дроби ----------

def g_pw(rng: random.Random, level: int):
    for _ in range(300):
        p, q = rng.choice([(1, 2), (2, 3), (3, 2), (1, 3), (3, 4), (2, 5), (4, 3), (1, 4)])
        m, n = rng.randint(1, 3), rng.randint(1, 3)
        k = 2 if level < 3 else rng.choice([2, 3])
        base_app = f"({amono(p, 'a', m)})/({amono(q, 'x', n)})"
        base_tex = f"\\dfrac{{{mono(p, 'a', m)}}}{{{mono(q, 'x', n)}}}"
        raised_tex = f"\\dfrac{{{mono(p ** k, 'a', m * k)}}}{{{mono(q ** k, 'x', n * k)}}}"
        step1 = f"Возводим в степень и числитель, и знаменатель: $\\left({base_tex}\\right)^{{{k}}}={raised_tex}$ (показатели степеней умножаем)."
        if level == 1:
            expr = f"({base_app})^{k}"
            tex = f"\\left({base_tex}\\right)^{{{k}}}"
            sol = [step1]
        else:
            c1, c2 = rng.randint(1, 3), rng.randint(1, 3)
            r, s = rng.randint(1, 2 * n * k + 2), rng.randint(1, 2 * m * k)
            if level == 2:
                oc1, oc2 = q ** 2 * c1, p ** 2 * c2
                other_app = f"({amono(oc1, 'x', r)})/({amono(oc2, 'a', s)})"
                other_tex = f"\\dfrac{{{mono(oc1, 'x', r)}}}{{{mono(oc2, 'a', s)}}}"
                expr = f"({base_app})^{k}*({other_app})"
                tex = f"\\left({base_tex}\\right)^{{{k}}}\\cdot {other_tex}"
                op_line = "Перемножаем и сокращаем"
            else:
                oc1, oc2 = p ** k * c1, q ** k * c2
                other_app = f"({amono(oc1, 'a', s)})/({amono(oc2, 'x', r)})"
                other_tex = f"\\dfrac{{{mono(oc1, 'a', s)}}}{{{mono(oc2, 'x', r)}}}"
                expr = f"({base_app})^{k}/({other_app})"
                tex = f"\\left({base_tex}\\right)^{{{k}}}:{other_tex}"
                op_line = "Деление заменяем умножением на перевёрнутую дробь, перемножаем и сокращаем"
        e = sp.cancel(parse_app(expr))
        num, den = sp.fraction(e)
        deg = sp.Poly(num, A, X).total_degree(), sp.Poly(den, A, X).total_degree()
        coefs = [abs(c) for c in sp.Poly(num, A, X).coeffs() + sp.Poly(den, A, X).coeffs()]
        if max(deg) > 12 or max(coefs) > 60 or e == 0:
            continue
        if level > 1:
            sol = [step1, f"{op_line}: ${sp.latex(e)}$."]
        return task("Упростите выражение {expr}.", sym_to_app(e), "expr",
                    "Сначала возведи дробь в степень (и числитель, и знаменатель), потом умножай (делить — значит умножать на перевёрнутую) и сокращай.",
                    sol, ["fraction-power", "fraction-mult", "cancel"], expr=expr, tex=tex, reduce=True, verify={"op": "self"})
    return None


# ---------- обратная пропорциональность ----------

def _inv_opt(c: int) -> tuple[str, str]:
    tex = f"y={'-' if c < 0 else ''}\\dfrac{{{abs(c)}}}{{x}}"
    return f"${tex}$", f"{c}/x"


def _lin_opt(c: int) -> tuple[str, str]:
    return f"$y={c}x$", f"{c}*x"


def g_inv(rng: random.Random, level: int):
    if level < 3:
        x0 = rng.choice([2, 3, 4, 5, 6]) * (1 if level == 1 else rng.choice([-1, 1]))
        m = rng.choice([2, 3, 4]) * (1 if level == 1 else rng.choice([-1, 1]))
        y0 = m * x0
        k = x0 * y0
        pt_tex = f"({x0};\\ {y0})"
        sol_k = f"Для обратной пропорциональности $y=\\dfrac{{k}}{{x}}$ число $k$ равно произведению $x\\cdot y$: $k={par(x0)}\\cdot {par(y0)}={k}$."
        x0f = Fraction(x0)
    else:
        s = rng.choice([-1, 1])
        q = rng.choice([2, 3, 4, 5])
        t = rng.choice([1, 2, 3, 4]) * rng.choice([-1, 1])
        x0f = Fraction(s, q)
        y0 = q * t
        k = s * t
        m = s * q * q * t
        xt = tex_num(x0f)
        pt_tex = f"({xt};\\ {y0})"
        sol_k = f"$k=x\\cdot y={_fr_par(x0f)}\\cdot {par(y0)}={k}$."
    opts = [_inv_opt(k), _inv_opt(-k), _inv_opt(m), _lin_opt(m)]
    order = list(range(4))
    rng.shuffle(order)
    shown = [opts[i] for i in order]
    answer = order.index(0)
    sol = [sol_k, f"Формула: $y={'-' if k < 0 else ''}\\dfrac{{{abs(k)}}}{{x}}$.",
           f"Проверка: при $x={tex_num(x0f)}$ получаем $y={'-' if k < 0 else ''}\\dfrac{{{abs(k)}}}{{{tex_num(x0f)}}}={y0}$ ✓.",
           f"Обрати внимание: прямая $y={m}x$ тоже проходит через эту точку, но это **прямая** пропорциональность, а в условии нужна обратная."]
    return task(f"Задайте формулой обратную пропорциональность, если её график проходит через точку $M{pt_tex}$.", str(answer), "choice",
                "У обратной пропорциональности $y=\\frac{k}{x}$ произведение $x\\cdot y$ всегда равно $k$. Найди $k$ по координатам точки.",
                sol, ["inverse-prop"], options=[o[0] for o in shown],
                invCheck={"pt": [str(x0f), str(y0)], "opts": [o[1] for o in shown], "answer": answer})


def _fr_par(v: Fraction) -> str:
    t = tex_num(v)
    return f"({t})" if v < 0 else t


# ---------- длинное выражение (КР №2, В1) ----------

def _long_params():
    out = []
    for p in range(1, 5):
        for q in range(2, 5):
            for r in range(2, 7):
                for s in range(1, 5):
                    A_, B_, C_ = q * s - 1, 2 * p + q * s * r, p * p
                    g = math.gcd(math.gcd(A_, B_), C_)
                    if g > 1:
                        out.append((p, q, r, s, g))
    return out


LONG_PARAMS = _long_params()
POINT_VALUES = [Fraction(n, d) for d in (2, 3, 6, 9) for n in range(-14, 15) if n != 0 and math.gcd(abs(n), d) == 1]


def g_long(rng: random.Random, level: int):
    for _ in range(300):
        p, q, r, s, g = rng.choice(LONG_PARAMS)
        Wa, Wb, Wc = (q * s - 1) // g, (2 * p + q * s * r) // g, p * p // g  # W = Wa·a² − Wb·ab − Wc·b²
        W_app = f"{Wa}*a^2-{Wb}*a*b-{Wc}*b^2"
        W_tex = sp.latex(sp.expand(Wa * A**2 - Wb * A * B - Wc * B**2))
        W_tex = f"{Wa if Wa != 1 else ''}a^2-{Wb}ab-{Wc if Wc != 1 else ''}b^2"
        a_val, b_val = rng.choice(POINT_VALUES), rng.choice(POINT_VALUES)
        if a_val - r * b_val == 0 or a_val + r * b_val == 0:
            continue
        Wv = Wa * a_val**2 - Wb * a_val * b_val - Wc * b_val**2
        if Wv == 0:
            continue
        first_app = f"((a+{p}*b)^2/({q}*(a-{r}*b))-{s}*a)"
        first_tex = f"\\left(\\dfrac{{(a+{p if p != 1 else ''}b)^2}}{{{q}(a-{r}b)}}-{s if s != 1 else ''}a\\right)"
        mid_app = f"(a^2-{r * r}*b^2)/({W_app})"
        mid_tex = f"\\dfrac{{a^2-{r * r}b^2}}{{{W_tex}}}"
        sol = [f"Скобка. Общий знаменатель ${q}(a-{r}b)$: $\\dfrac{{(a+{p if p != 1 else ''}b)^2-{q * s}a(a-{r}b)}}{{{q}(a-{r}b)}}=\\dfrac{{-{g}\\,({W_tex})}}{{{q}(a-{r}b)}}$ (раскрыли скобки и вынесли ${g}$).",
               f"Умножаем на $\\dfrac{{a^2-{r * r}b^2}}{{{W_tex}}}$, где $a^2-{r * r}b^2=(a-{r}b)(a+{r}b)$: сокращаем $({W_tex})$ и $(a-{r}b)$. Получаем $-\\dfrac{{{g}(a+{r}b)}}{{{q}}}$."]
        if level == 1:
            expr_app = f"{first_app}*{mid_app}"
            tex = f"{first_tex}\\cdot {mid_tex}"
            value = -Fraction(g) * (a_val + r * b_val) / q
            sol.append(f"Подставляем $a={tex_num(a_val)}$, $b={tex_num(b_val)}$: $-\\dfrac{{{g}\\cdot\\left({tex_num(a_val + r * b_val)}\\right)}}{{{q}}}={tex_num(value)}$.")
            if value.denominator > 6 or abs(value) > 40 or value == 0:
                continue
        else:
            e, f = rng.choice([3, 6, 9, 12]), rng.randint(1, 9)
            if (e * a_val).denominator != 1:
                continue
            value = f - e * a_val
            if value == 0 or e * a_val - f == 0 or abs(value) > 40:
                continue
            div_app = f"({g}*a+{g * r}*b)/({q * e}*a-{q * f})"
            div_tex = f"\\dfrac{{{g}a+{g * r}b}}{{{q * e}a-{q * f}}}"
            expr_app = f"{first_app}*{mid_app}/({div_app})"
            tex = f"{first_tex}\\cdot {mid_tex}:{div_tex}"
            sol += [f"Делим на $\\dfrac{{{g}(a+{r}b)}}{{{q}({e}a-{f})}}$ — умножаем на перевёрнутую дробь: $-\\dfrac{{{g}(a+{r}b)}}{{{q}}}\\cdot\\dfrac{{{q}({e}a-{f})}}{{{g}(a+{r}b)}}=-({e}a-{f})={f}-{e}a$.",
                    f"Переменная $b$ «исчезла» — хороший знак. Подставляем $a={tex_num(a_val)}$: ${f}-{e}\\cdot {_fr_par(a_val)}={tex_num(value)}$."]
        expr_sym = parse_app(expr_app)
        got = sp.simplify(expr_sym.subs({A: sp.Rational(a_val.numerator, a_val.denominator), B: sp.Rational(b_val.numerator, b_val.denominator)}))
        if got != sp.Rational(value.numerator, value.denominator):
            raise AssertionError((expr_app, a_val, b_val, got, value))
        prompt = f"Упростите выражение $\\displaystyle {tex}$ и найдите его значение при $a={tex_num(a_val)}$, $b={tex_num(b_val)}$."
        return task(prompt, ans(value), "expr",
                    "Действуй по порядку: скобка (общий знаменатель, раскрыть скобки, вынести множитель), потом умножение с сокращением, потом деление (умножь на перевёрнутую).",
                    sol, ["fraction-add", "fraction-mult", "fraction-div", "cancel", "fsu"],
                    longCheck={"expr": expr_app, "a": str(a_val), "b": str(b_val)})
    return None


# ---------- графически: k/x = mx + c ----------

def _lin_app(m: int, c: int) -> str:
    head = "" if m == 1 else ("-" if m == -1 else f"{m}*")
    return f"{head}x" + (f"+{c}" if c > 0 else (f"-{-c}" if c < 0 else ""))


def _lin_tex(m: int, c: int) -> str:
    head = "" if m == 1 else ("-" if m == -1 else str(m))
    return f"{head}x" + (f"+{c}" if c > 0 else (f"-{-c}" if c < 0 else ""))


def g_ghyp(rng: random.Random, level: int):
    for _ in range(400):
        if level == 1:
            x1, x2 = rng.sample([i for i in range(-6, 7) if i != 0], 2)
            m, c, k = 1, -(x1 + x2), -x1 * x2
            roots = sorted({x1, x2})
        elif level == 2:
            if rng.random() < 0.35:
                m = rng.choice([2, 3, 4, -2, -3, -4])
                t = 1
                c, k = 0, m * t * t
                roots = [-t, t]
            else:
                m = rng.choice([1, -1, 2, -2])
                x1, x2 = rng.sample([i for i in range(-5, 6) if i != 0], 2)
                c, k = -m * (x1 + x2), -m * x1 * x2
                roots = sorted({x1, x2})
        else:
            kind = rng.choice(["tangent", "none", "tangent"])
            if kind == "tangent":
                m = rng.choice([1, -1, 2, -2])
                x1 = rng.choice([i for i in range(-4, 5) if i != 0])
                c, k = -2 * m * x1, -m * x1 * x1
                roots = [x1]
            else:
                m = rng.choice([1, -1, 2, -2])
                c = rng.randint(-3, 3)
                k = rng.choice([i for i in range(-6, 7) if i != 0])
                if c * c + 4 * m * k >= 0:
                    continue
                roots = []
        if k == 0 or abs(k) > 12 or abs(c) > 9:
            continue
        # точки гиперболы с целыми координатами
        hx = sorted({x for d in range(1, 7) if k % d == 0 for x in (d, -d)})
        hy = [(x, k // x) for x in hx]
        if len(hy) < 4:
            continue
        line_x = sorted({0, 1} | set(roots))[:4]
        lpts = [(x, m * x + c) for x in line_x if -9 <= m * x + c <= 9] or [(0, c), (1, m + c)]
        ans_s = "; ".join(str(r) for r in roots) if roots else "нет"
        hyp = ", ".join(f"$({x};\\ {y})$" for x, y in hy[:8])
        lp = ", ".join(f"$({x};\\ {y})$" for x, y in lpts[:3])
        sol = [f"Построим график $y=\\dfrac{{{k}}}{{x}}$ — это гипербола. Точки: {hyp}.",
               f"Построим график $y={_lin_tex(m, c)}$ — прямая. Она проходит через точки {lp}."]
        if roots:
            inter = ", ".join(f"$({r};\\ {m * r + c})$" for r in roots)
            sol.append(f"Графики {'касаются' if len(roots) == 1 else 'пересекаются'} в {'точке' if len(roots) == 1 else 'точках'} {inter}. Корни — абсциссы этих точек: ${';\\ '.join(str(r) for r in roots)}$.")
            sol.append("Проверка: подставь каждое значение в обе части уравнения.")
        else:
            sol.append("Графики не пересекаются, значит, у уравнения нет корней.")
        return task("Решите графически уравнение {expr}={expr2}. " + RES, ans_s, "roots",
                    "Построй график $y=\\frac{k}{x}$ (две ветки гиперболы) и график правой части. Корни — абсциссы точек пересечения; сделай проверку подстановкой.",
                    sol, ["hyperbola-graph", "inverse-prop"], expr=f"{k}/x", expr2=_lin_app(m, c), equation=[f"{k}/x", _lin_app(m, c)])
    return None


# ---------- выразить переменную из формулы (КР №2, С1) ----------

def g_frm(rng: random.Random, level: int):
    letters = ["x", "y", "z"]
    rng.shuffle(letters)
    A_, B_, C_ = letters
    p, q, r = rng.randint(1, 5), rng.randint(1, 5), rng.randint(1, 5)
    target = rng.choice(letters if level > 1 else [B_])
    SA, SB, SC = SYMS[A_], SYMS[B_], SYMS[C_]
    sign = rng.choice(["-", "+"])
    lhs = sp.Rational(p) / SA
    rest_terms = {A_: None, B_: sp.Rational(q) / SB, C_: (-1 if sign == "-" else 1) * sp.Rational(r) / SC}
    rhs = rest_terms[B_] + rest_terms[C_]
    sols = sp.solve(sp.Eq(lhs, rhs), SYMS[target])
    if len(sols) != 1:
        return None
    ans_e = sp.factor(sp.cancel(sols[0]))
    others = [l for l in letters if l != target]
    frac = lambda n, v: f"\\frac{{{n}}}{{{v}}}"
    tex_eq = f"{frac(p, A_)}={frac(q, B_)}{sign}{frac(r, C_)}"
    if target == A_:
        combined = sp.together(rhs)
        N, Dn = sp.fraction(combined)
        sol = [f"Правую часть приводим к общему знаменателю: $\\dfrac{{{p}}}{{{A_}}}={sp.latex(combined)}$.",
               f"Переворачиваем обе части (дробь равна дроби): ${A_}=\\dfrac{{{p}\\cdot {sp.latex(Dn)}}}{{{sp.latex(N)}}}$.",
               f"Упрощаем: ${A_}={sp.latex(ans_e)}$."]
    else:
        other = rest_terms[B_ if target == C_ else C_]
        isolated = sp.together(lhs - other)
        sign_t = "-" if (target == C_ and sign == "-") else ""
        lhs_tex = f"{sign_t}\\dfrac{{{r if target == C_ else q}}}{{{target}}}"
        sol = [f"Оставим дробь с ${target}$ в одной части, остальное перенесём: ${lhs_tex}={sp.latex(lhs - other)}$.",
               f"Правую часть приведём к общему знаменателю: ${lhs_tex}={sp.latex(isolated)}$.",
               f"Выразим ${target}$ (перевернём дроби и учтём числитель слева): ${target}={sp.latex(ans_e)}$."]
    return task(f"Из формулы ${tex_eq}$ выразите ${target}$ через ${others[0]}$ и ${others[1]}$. Ответ упростите.", sym_to_app(ans_e), "expr",
                "Сложи (вычти) дроби с другой стороны, приведя их к общему знаменателю, потом переверни обе части.", sol,
                ["fraction-add", "formula"], reduce=True,
                formula={"lhs": f"{p}/{A_}", "rhs": f"{q}/{B_}{sign}{r}/{C_}", "solveFor": target})


GROUPS = [
    ("mul", "Умножение дробей", g_mul, 1),
    ("div", "Деление дробей", g_div, 2),
    ("pw", "Степень дроби", g_pw, 3),
    ("inv", "Обратная пропорциональность", g_inv, 4),
    ("long", "Длинное выражение", g_long, 7),
    ("ghyp", "Графически: k/x = mx + c", g_ghyp, 5),
    ("frm", "Выразить из формулы", g_frm, 6),
]
