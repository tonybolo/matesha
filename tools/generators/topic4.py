"""Тема 4: упрощение выражений с корнями (КР №3 A2, КР №4, классная работа №2, КР №2)."""
from __future__ import annotations

import math
import random
from decimal import Decimal
from fractions import Fraction

import sympy as sp

from common import *  # noqa: F401,F403

NONSQ = [x for x in range(2, 20) if not is_square(x)]


def _coprime_pair(rng, pmax=9, qmax=15):
    while True:
        p, q = rng.randint(1, pmax), rng.randint(2, qmax)
        if math.gcd(p, q) == 1:
            return p, q


# ---------- КР №3 A2: корни из дробей ----------

def g_val(rng: random.Random, level: int):
    def root(p, q):
        return f"sqrt({p * p}/{q * q})", Fraction(p, q), f"$\\sqrt{{\\frac{{{p * p}}}{{{q * q}}}}}=\\frac{{{p}}}{{{q}}}$"

    if level == 1:
        k = rng.randint(2, 5)
        (p1, q1), (p2, q2) = _coprime_pair(rng), _coprime_pair(rng)
        e1, v1, s1 = root(p1, q1)
        e2, v2, s2 = root(p2, q2)
        total = k * v1 - v2
        expr = f"{k}*{e1} - {e2}"
        sol = [s1, s2, f"${k}\\cdot{tex_num(v1)}-{tex_num(v2)}={tex_num(total)}$."]
    elif level == 2:
        k1, k2 = rng.randint(2, 4), rng.randint(2, 4)
        (p1, q1), (p2, q2), (p3, q3) = (_coprime_pair(rng) for _ in range(3))
        e1, v1, s1 = root(p1, q1)
        e2, v2, s2 = root(p2, q2)
        e3, v3, s3 = root(p3, q3)
        sg = rng.choice(["+", "-"])
        total = k1 * v1 + (k2 * v2 if sg == "+" else -k2 * v2) - v3
        expr = f"{k1}*{e1} {sg} {k2}*{e2} - {e3}"
        sol = [s1, s2, s3, f"Подставляем и считаем: ${k1}\\cdot{tex_num(v1)}{sg}{k2}\\cdot{tex_num(v2)}-{tex_num(v3)}={tex_num(total)}$."]
    else:
        (p1, q1), (p2, q2) = _coprime_pair(rng, 7, 9), _coprime_pair(rng, 7, 9)
        e1, v1, s1 = root(p1, q1)
        e2, v2, s2 = root(p2, q2)
        s = rng.randint(2, 12)
        total = v1 * v2 + s
        expr = f"{e1}*{e2} + sqrt({s * s})"
        sol = [s1, s2, f"$\\sqrt{{{s * s}}}={s}$.", f"${tex_num(v1)}\\cdot{tex_num(v2)}+{s}={tex_num(total)}$."]
    return task("Найдите значение выражения {expr}.", ans(total), "expr",
                "Найди значение каждого корня отдельно: $\\sqrt{\\frac{a^2}{b^2}}=\\frac{a}{b}$, потом выполни действия с дробями.",
                sol, ["sqrt-frac", "fractions"], expr=expr, verify={"op": "self"})


# ---------- КР №4 A2: корни, √(a·b), √a/√b, √(−n)² ----------

def g_val2(rng: random.Random, level: int):
    squares = [4, 9, 16, 25, 36, 49, 64, 81, 100]
    u, v = rng.sample(squares, 2)
    c = rng.choice([2, 3, 5, 6, 7])
    m = rng.randint(2, 6)
    k, n = rng.randint(2, 4), rng.randint(2, 5)
    sol = [f"$\\sqrt{{{u}\\cdot{v}}}=\\sqrt{{{u}}}\\cdot\\sqrt{{{v}}}={math.isqrt(u)}\\cdot{math.isqrt(v)}={math.isqrt(u) * math.isqrt(v)}$.",
           f"$\\dfrac{{\\sqrt{{{c * m * m}}}}}{{\\sqrt{{{c}}}}}=\\sqrt{{{m * m}}}={m}$.",
           f"${k}\\sqrt{{(-{n})^2}}={k}\\cdot{n}={k * n}$ (корень не бывает отрицательным: $\\sqrt{{a^2}}=|a|$)."]
    base = math.isqrt(u) * math.isqrt(v)
    if level == 1:
        total = base - m
        expr = f"sqrt({u}*{v}) - sqrt({c * m * m})/sqrt({c})"
        sol = sol[:2] + [f"${base}-{m}={total}$."]
    elif level == 2:
        total = base - m + k * n
        expr = f"sqrt({u}*{v}) - sqrt({c * m * m})/sqrt({c}) + {k}*sqrt((-{n})^2)"
        sol = sol + [f"${base}-{m}+{k * n}={total}$."]
    else:
        w = rng.choice([4, 9, 16, 25])
        z = rng.randint(2, 5)
        total = base - m + k * n - z * math.isqrt(w)
        expr = f"sqrt({u}*{v}) - sqrt({c * m * m})/sqrt({c}) + {k}*sqrt((-{n})^2) - {z}*sqrt({w})"
        sol = sol + [f"${z}\\sqrt{{{w}}}={z}\\cdot{math.isqrt(w)}={z * math.isqrt(w)}$.", f"${base}-{m}+{k * n}-{z * math.isqrt(w)}={total}$."]
    return task("Найдите значение выражения {expr}.", ans(total), "expr",
                "Вычисли каждое слагаемое отдельно: корень из произведения, корень из дроби, корень из квадрата.",
                sol, ["sqrt-prod", "sqrt-ops", "abs-sqrt"], expr=expr, verify={"op": "self"})


# ---------- классная работа №2: корни из больших чисел и десятичных ----------

def g_dec(rng: random.Random, level: int):
    def sq_dec(root: Decimal) -> Decimal:
        return root * root

    if level == 1:
        p, q = rng.sample([10, 20, 25, 30, 40, 50, 60], 2)
        r, s = rng.sample([6, 8, 9, 12, 15, 18, 20, 24, 25], 2)
        val = Fraction(p * q, r * s)
        expr = f"sqrt({p * p}*{q * q})/(sqrt({r * r})*sqrt({s * s}))"
        sol = [f"$\\sqrt{{{p * p}\\cdot{q * q}}}=\\sqrt{{{p * p}}}\\cdot\\sqrt{{{q * q}}}={p}\\cdot{q}={p * q}$.",
               f"$\\sqrt{{{r * r}}}\\cdot\\sqrt{{{s * s}}}={r}\\cdot{s}={r * s}$.",
               f"$\\dfrac{{{p * q}}}{{{r * s}}}={tex_num(val)}$."]
    else:
        roots = lambda: Decimal(rng.choice([2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 15, 25])).scaleb(-rng.choice([0, 1, 2]))
        a, b, c, d = roots(), roots(), roots(), roots()
        if level == 2:
            val = Fraction(a) * Fraction(b) / (Fraction(c) * Fraction(d))
        else:
            val = Fraction(a) * Fraction(b) / (Fraction(c) * Fraction(d))
        A, B, C, D = sq_dec(a), sq_dec(b), sq_dec(c), sq_dec(d)
        expr = f"sqrt({dec_expr(A)})*sqrt({dec_expr(B)})/(sqrt({dec_expr(C)})*sqrt({dec_expr(D)}))"
        if level == 3:
            expr = f"sqrt({dec_expr(A)}*{dec_expr(B)})/(sqrt({dec_expr(C)})*sqrt({dec_expr(D)}))"
        sol = [f"$\\sqrt{{{dec_tex(A)}}}={dec_tex(a)}$, $\\sqrt{{{dec_tex(B)}}}={dec_tex(b)}$ (сдвигаем запятую: два знака под корнем — один в ответе).",
               f"$\\sqrt{{{dec_tex(C)}}}={dec_tex(c)}$, $\\sqrt{{{dec_tex(D)}}}={dec_tex(d)}$.",
               f"$\\dfrac{{{dec_tex(a)}\\cdot{dec_tex(b)}}}{{{dec_tex(c)}\\cdot{dec_tex(d)}}}={tex_num(val)}$."]
    return task("Найдите значение выражения {expr}.", ans(val), "expr",
                "Извлеки каждый корень отдельно (корень из произведения — произведение корней), потом посчитай дробь.",
                sol, ["sqrt-prod", "decimals", "fractions"], expr=expr, verify={"op": "self"})


# ---------- вынести множитель, упростить ----------

def g_out(rng: random.Random, level: int):
    def finish(expr, hint, sol, skills):
        e = sp.expand(parse_app(expr))
        assert radical_ok(e), (expr, e)
        return task("Упростите выражение {expr}.", sym_to_app(e), "expr", hint, sol + [f"Ответ: ${sp.latex(e)}$."],
                    skills, expr=expr, radical=True, verify={"op": "self"})

    if level == 1:
        k, m = rng.randint(2, 9), rng.choice([2, 3, 5, 6, 7, 10, 11])
        n = k * k * m
        fs = sp.factorint(n)
        fx = "·".join(str(p) for p, e in sorted(fs.items()) for _ in range(e))
        sol = [f"${n}={fx.replace('·', '\\cdot ')}$, пары одинаковых множителей выходят из-под корня."]
        return finish(f"sqrt({n})", "Разложи число под корнем на множители и найди пары одинаковых.", sol, ["sqrt-extract"])
    if level == 2:
        m = rng.choice([2, 3, 5])
        k = [rng.randint(1, 5) for _ in range(3)]
        cf = [rng.randint(1, 3) for _ in range(3)]
        sg = ["+", rng.choice(["+", "-"]), rng.choice(["+", "-"])]
        if sum(((-1) ** (s == "-")) * c * kk for s, c, kk in zip(sg, cf, k)) == 0:
            return None
        parts = []
        for s, c, kk in zip(sg, cf, k):
            body = (f"{c}*" if c != 1 else "") + f"sqrt({kk * kk * m})"
            parts.append((" - " if s == "-" else (" + " if parts else "")) + body)
        expr = "".join(parts)
        sol = ["Вынесем множители из-под каждого корня: " + ", ".join(f"$\\sqrt{{{kk * kk * m}}}={kk}\\sqrt{{{m}}}$" for kk in k) + ".",
               "Теперь у всех слагаемых одинаковый корень, складываем и вычитаем «как подобные»."]
        return finish(expr, "Сначала упрости каждый корень, потом приведи подобные слагаемые.", sol, ["sqrt-extract", "like-terms"])
    kind = rng.choice(["prod", "square", "diff"])
    if kind == "prod":
        k, m = rng.randint(2, 6), rng.choice([2, 3, 5, 6, 7])
        divisors = [d for d in range(2, k * k * m) if (k * k * m) % d == 0 and d != 1 and d != k * k * m]
        a = rng.choice(divisors)
        b = (k * k * m) // a
        sol = [f"$\\sqrt{{{a}}}\\cdot\\sqrt{{{b}}}=\\sqrt{{{a}\\cdot {b}}}=\\sqrt{{{a * b}}}$.", f"${a * b}={k * k}\\cdot {m}$, значит корень равен ${k}\\sqrt{{{m}}}$."]
        return finish(f"sqrt({a})*sqrt({b})", "Перемножь числа под корнями, потом вынеси множители.", sol, ["sqrt-prod", "sqrt-extract"])
    if kind == "square":
        m, k = rng.choice([2, 3, 5, 6, 7, 10, 11]), rng.randint(1, 4)
        sol = [f"$(\\sqrt{{{m}}}+{k})^2=({m})+2\\cdot{k}\\sqrt{{{m}}}+{k * k}$ (квадрат суммы)."]
        return finish(f"(sqrt({m})+{k})^2", "Квадрат суммы: $(a+b)^2=a^2+2ab+b^2$, помни $(\\sqrt{m})^2=m$.", sol, ["fsu", "sqrt-ops"])
    m, k = rng.choice([2, 3, 5, 6, 7, 10, 11]), rng.randint(1, 5)
    if k * k == m:
        return None
    sol = [f"$(\\sqrt{{{m}}}+{k})(\\sqrt{{{m}}}-{k})=({m})-{k * k}$ (разность квадратов)."]
    return finish(f"(sqrt({m})+{k})*(sqrt({m})-{k})", "Разность квадратов: $(a+b)(a-b)=a^2-b^2$.", sol, ["fsu", "sqrt-ops"])


# ---------- КР №4 B1: (√a−2q)²−a ... ----------

def g_sq(rng: random.Random, level: int):
    a = rng.choice([x for x in NONSQ if x >= 5])
    q = rng.randint(1, 4)
    if level == 1:
        s = rng.choice([-1, 1])
        sg, s2 = ("-", "-") if s < 0 else ("+", "+")
        expr = f"((sqrt({a}){sg}{2 * q})^2-{a})/(sqrt({a}){s2}{q})"
        total = -4 * q if s < 0 else 4 * q
        sol = [f"$(\\sqrt{{{a}}}{sg}{2 * q})^2={a}{'-' if s < 0 else '+'}{4 * q}\\sqrt{{{a}}}+{4 * q * q}$.",
               f"Числитель: ${a}{'-' if s < 0 else '+'}{4 * q}\\sqrt{{{a}}}+{4 * q * q}-{a}={4 * q * q}{'-' if s < 0 else '+'}{4 * q}\\sqrt{{{a}}}={'-' if s < 0 else ''}{4 * q}(\\sqrt{{{a}}}{sg}{q})$.",
               f"Сокращаем на $(\\sqrt{{{a}}}{sg}{q})$: получаем ${total}$."]
        hint = "Раскрой квадрат в числителе, вынеси общий множитель и сократи на скобку из знаменателя."
        skills = ["fsu", "sqrt-ops", "cancel"]
    elif level == 2:
        if rng.random() < 0.5:
            expr = f"((sqrt({a})+{q})^2-(sqrt({a})-{q})^2)/sqrt({a})"
            total = 4 * q
            sol = [f"$(\\sqrt{{{a}}}+{q})^2-(\\sqrt{{{a}}}-{q})^2=4\\cdot{q}\\sqrt{{{a}}}$ (разность квадратов или раскрытие скобок).",
                   f"Делим на $\\sqrt{{{a}}}$: ${total}$."]
        else:
            b = rng.choice([x for x in NONSQ if x != a])
            expr = f"((sqrt({a})+sqrt({b}))^2-{a}-{b})/sqrt({a}*{b})"
            total = 2
            sol = [f"$(\\sqrt{{{a}}}+\\sqrt{{{b}}})^2={a}+{b}+2\\sqrt{{{a * b}}}$.", f"Числитель равен $2\\sqrt{{{a * b}}}$, знаменатель $\\sqrt{{{a * b}}}$. Ответ ${total}$."]
        hint = "Раскрой скобки по формуле квадрата суммы и приведи подобные."
        skills = ["fsu", "sqrt-ops", "cancel"]
    else:
        expr = f"({a}-{q * q})/(sqrt({a})+{q})+({a}-{q * q})/(sqrt({a})-{q})"
        if a == q * q:
            return None
        e = sp.simplify(parse_app(expr))
        sol = [f"$\\dfrac{{{a}-{q * q}}}{{\\sqrt{{{a}}}+{q}}}$: числитель $={a}-{q * q}=(\\sqrt{{{a}}}-{q})(\\sqrt{{{a}}}+{q})$ (разность квадратов), сокращаем: $\\sqrt{{{a}}}-{q}$.",
               f"Аналогично второе слагаемое равно $\\sqrt{{{a}}}+{q}$.", f"Сумма: $(\\sqrt{{{a}}}-{q})+(\\sqrt{{{a}}}+{q})=2\\sqrt{{{a}}}$."]
        return task("Упростите выражение {expr}.", sym_to_app(e), "expr", "Числитель — разность квадратов: $a-q^2=(\\sqrt{a}-q)(\\sqrt{a}+q)$.", sol,
                    ["fsu", "sqrt-ops", "cancel"], expr=expr, radical=True, verify={"op": "self"})
    return task("Упростите выражение {expr}.", str(total), "expr", hint, sol, skills, expr=expr, verify={"op": "self"})


# ---------- КР №4 C2: корень в знаменателе ----------

def _rat_terms(rng, a, n_terms):
    for _ in range(300):
        cs = [rng.choice([-3, -2, -1, 1, 2, 3]) for _ in range(n_terms - 1)]
        last = -sum(cs)
        if last == 0 or abs(last) > 3:
            continue
        cs.append(last)
        terms, total, ok = [], sp.Integer(0), True
        for c in cs:
            t = rng.choice([-4, -3, -2, -1, 1, 2, 3, 4])
            if t * t == a:
                ok = False
                break
            form = rng.choice(["A", "C"])
            if form == "A":  # k/(√a + t)
                k = c * (a - t * t)
                den = f"sqrt({a})+{t}" if t > 0 else f"sqrt({a})-{-t}"
                total += -c * t
            else:  # k/(t − √a)
                k = c * (t * t - a)
                den = f"{t}-sqrt({a})"
                total += c * t
            if abs(k) > 45 or k == 0:
                ok = False
                break
            terms.append((k, den))
        if not ok:
            continue
        expr = ""
        for i, (k, den) in enumerate(terms):
            body = f"{abs(k)}/({den})"
            expr += (("-" if k < 0 else "+") if i else ("-" if k < 0 else "")) + (" " if i else "") + body + " "
            expr = expr.replace("- -", "- ")
        expr = expr.strip().replace("+ -", "- ")
        return expr, total
    return None


def g_rat(rng: random.Random, level: int):
    a = rng.choice([2, 3, 5, 6, 7, 10, 11])
    if level == 1:
        if rng.random() < 0.5:
            m = rng.randint(2, 6)
            k = m * a
            expr = f"{k}/sqrt({a})"
            e = parse_app(f"{m}*sqrt({a})")
            sol = [f"Умножаем верх и низ на $\\sqrt{{{a}}}$: $\\dfrac{{{k}\\sqrt{{{a}}}}}{{\\sqrt{{{a}}}\\cdot\\sqrt{{{a}}}}}=\\dfrac{{{k}\\sqrt{{{a}}}}}{{{a}}}={m}\\sqrt{{{a}}}$."]
            return task("Избавьтесь от корня в знаменателе: {expr}.", sym_to_app(e), "expr",
                        "Умножь числитель и знаменатель на $\\sqrt{a}$: тогда в знаменателе получится $a$.", sol,
                        ["rationalize"], expr=expr, radical=True, verify={"op": "self"})
        t = rng.randint(1, 4)
        if t * t == a:
            return None
        c = rng.choice([1, -1, 2, -2])
        k = c * (a - t * t)
        if k < 0:
            c, k = -c, -k  # k>0
            k = c * (a - t * t)
        if k <= 0 or k > 40:
            return None
        expr = f"{k}/(sqrt({a})+{t})"
        e = sp.expand(c * (sp.sqrt(a) - t))
        sol = [f"Умножаем верх и низ на $\\sqrt{{{a}}}-{t}$.",
               f"Знаменатель: $(\\sqrt{{{a}}}+{t})(\\sqrt{{{a}}}-{t})={a}-{t * t}={a - t * t}$.",
               f"${k}(\\sqrt{{{a}}}-{t})/{a - t * t}={sp.latex(e)}$."]
        return task("Избавьтесь от корня в знаменателе: {expr}.", sym_to_app(e), "expr",
                    "Умножь верх и низ на «двойника» $\\sqrt{a}-t$: в знаменателе получится разность квадратов.", sol,
                    ["rationalize", "fsu"], expr=expr, radical=True, verify={"op": "self"})
    n = 2 if level == 2 else 3
    r = _rat_terms(rng, a, n)
    if r is None:
        return None
    expr, total = r
    e = sp.Integer(total)
    sol = ["Избавимся от корня в знаменателе у каждой дроби: умножаем верх и низ на «двойника» знаменателя (меняем знак перед одним слагаемым).",
           "Разность квадратов в знаменателе даёт целое число, дроби сокращаются.",
           f"Слагаемые с $\\sqrt{{{a}}}$ взаимно уничтожаются. Остаётся ${sp.latex(e)}$."]
    return task("Упростите выражение {expr}.", str(total), "expr",
                "У каждой дроби умножь числитель и знаменатель на выражение, которое даёт в знаменателе разность квадратов.", sol,
                ["rationalize", "fsu"], expr=expr, verify={"op": "self"})


# ---------- КР №4 C1: пара обратных/противоположных ----------

PELL = [(2, 3, 2), (3, 7, 4), (5, 9, 4), (6, 5, 2), (7, 8, 3), (8, 3, 1), (10, 19, 6), (11, 10, 3), (12, 7, 2), (15, 4, 1), (24, 5, 1), (35, 6, 1)]


def g_conj(rng: random.Random, level: int):
    a, q, p = rng.choice(PELL)
    inverse = level == 1 or rng.random() < 0.5
    x = (f"{p}\\sqrt{{{a}}}-{q}" if p != 1 else f"\\sqrt{{{a}}}-{q}", f"{p}*sqrt({a})-{q}")
    if inverse:
        y = (f"-{p}\\sqrt{{{a}}}-{q}" if p != 1 else f"-\\sqrt{{{a}}}-{q}", f"-{p}*sqrt({a})-{q}")
        z = (f"\\dfrac{{1}}{{{p}\\sqrt{{{a}}}+{q}}}" if p != 1 else f"\\dfrac{{1}}{{\\sqrt{{{a}}}+{q}}}", f"1/({p}*sqrt({a})+{q})")
        pair = (0, 1)  # x и y взаимно обратны
        kind, word = "inverse", "взаимно обратных"
        sol = [f"Произведение $({x[0]})({y[0]})=({q})^2-({p}\\sqrt{{{a}}})^2={q * q}-{p * p * a}=1$.", "Произведение равно 1, значит числа взаимно обратные."]
    else:
        y = (f"{p}\\sqrt{{{a}}}+{q}" if p != 1 else f"\\sqrt{{{a}}}+{q}", f"{p}*sqrt({a})+{q}")
        z = (f"\\dfrac{{1}}{{{p}\\sqrt{{{a}}}+{q}}}" if p != 1 else f"\\dfrac{{1}}{{\\sqrt{{{a}}}+{q}}}", f"1/({p}*sqrt({a})+{q})")
        pair = (0, 2)  # x и z противоположны
        kind, word = "opposite", "противоположных"
        sol = [f"$(\\sqrt{{{a}}}\\cdot{p}+{q})({p}\\sqrt{{{a}}}-{q})={p * p * a}-{q * q}=-1$, поэтому $\\dfrac{{1}}{{{p}\\sqrt{{{a}}}+{q}}}=-({p}\\sqrt{{{a}}}-{q})$.",
               "Значит первое и третье числа противоположны."]
    nums = [x, y, z]
    order = [0, 1, 2]
    rng.shuffle(order)
    shown = [nums[i] for i in order]
    pos = {orig: new for new, orig in enumerate(order)}
    pairs = [(0, 1), (0, 2), (1, 2)]
    correct_pair = tuple(sorted((pos[pair[0]], pos[pair[1]])))
    options = [f"${shown[i][0]}$ и ${shown[j][0]}$" for i, j in pairs]
    correct = pairs.index(correct_pair)
    items = ";  ".join(f"${s[0]}$" for s in shown)
    return task(f"Среди чисел {items} найдите пару {word} чисел.", str(correct), "choice",
                "Перемножь пары чисел (для обратных нужно получить 1) или сложи (для противоположных нужен 0).",
                sol, ["rationalize", "fsu"], options=options,
                pairCheck={"kind": kind, "exprs": [s[1] for s in shown], "pair": list(correct_pair)})


# ---------- КР №2: произведение и частное дробей ----------

def _app(e) -> str:
    return sym_to_app(e)


def g_prd(rng: random.Random, level: int):
    a, b, x = SYMS["a"], SYMS["b"], SYMS["x"]
    if level == 1:
        p, q, r = rng.randint(2, 4), rng.randint(2, 6), rng.randint(2, 5)
        m, n = rng.randint(1, 3), rng.randint(1, 4)
        # (p a^2 / x^m) · (x^(m+n) / (q a))
        expr = f"(({p}*a^2)/x^{m})*(x^{m + n}/({q}*a))"
        quotient = rng.random() < 0.4
        if quotient:
            expr = f"(({p}*a^2)/x^{m})/(({q}*a)/x^{m + n})"
    elif level == 2:
        p, q, s, n = rng.randint(2, 6), rng.randint(2, 5), rng.randint(1, 3), rng.randint(3, 6)
        m = rng.randint(1, 2)
        if rng.random() < 0.5:
            expr = f"((a^2+{p}*a)/x^{m})*((a^{s}*x^{n})/({q}*a+{q * p}))"
        else:
            c1, c2 = rng.randint(1, 3), rng.randint(2, 5)
            u, v = rng.randint(2, 6), rng.randint(2, 6)
            if u == v:
                return None
            expr = f"(({u * c1}*a+{u * c2}*b)/(a^{rng.randint(3, 9)}*x))/(({v * c1}*a+{v * c2}*b)/(a^{rng.randint(2, 4)}*x^{rng.randint(3, 6)}))"
    else:
        p, q = rng.randint(2, 7), rng.randint(2, 7)
        if p == q:
            return None
        if rng.random() < 0.5:
            expr = f"((a^2-{p * p})/(x^2-{q * q}))*((x+{q})/(a+{p}))"
        else:
            expr = f"((a^2-{p * p})/(x^2-{q * q}))/((a+{p})/(x-{q}))"
    e = sp.cancel(parse_app(expr))
    num, den = sp.fraction(e)
    app = _app(sp.factor(e)) if level == 3 else _app(e)
    sol = ["Деление заменяем умножением на перевёрнутую дробь (если оно есть).",
           "Раскладываем числители и знаменатели на множители, сокращаем общие.", f"Получаем ${sp.latex(e)}$."]
    return task("Упростите выражение {expr}.", app, "expr",
                "Разложи на множители числители и знаменатели, потом сократи. Деление — это умножение на перевёрнутую дробь.", sol,
                ["fraction-mult", "cancel", "fsu"], expr=expr, reduce=True, verify={"op": "self"})


# ---------- КР №2 C1: выразить переменную ----------

def g_frm(rng: random.Random, level: int):
    letters = ["x", "y", "z"]
    rng.shuffle(letters)
    A, B, C = letters
    p, q, r = rng.randint(1, 5), rng.randint(1, 5), rng.randint(1, 5)
    target = rng.choice(letters if level > 1 else [B])
    SA, SB, SC = SYMS[A], SYMS[B], SYMS[C]
    eq_l = sp.Rational(p) / SA
    sign = rng.choice(["-", "+"])
    eq_r = sp.Rational(q) / SB + (-1 if sign == "-" else 1) * sp.Rational(r) / SC
    sol_t = sp.solve(sp.Eq(eq_l, eq_r), SYMS[target])
    if len(sol_t) != 1:
        return None
    ans_e = sp.factor(sp.cancel(sol_t[0]))
    others = [l for l in letters if l != target]
    frac = lambda n, v: f"\\frac{{{n}}}{{{v}}}"
    tex_eq = f"{frac(p, A)}={frac(q, B)}{sign}{frac(r, C)}"
    sol = ["Приведём дроби к общему знаменателю и избавимся от знаменателей.", f"Выражаем ${target}$ и упрощаем: ${target}={sp.latex(ans_e)}$."]
    return task(f"Из формулы ${tex_eq}$ выразите ${target}$ через ${others[0]}$ и ${others[1]}$. Ответ упростите.", _app(ans_e), "expr",
                "Сложи (вычти) дроби с другой стороны, приведя к общему знаменателю, потом переверни обе части.", sol,
                ["fraction-add", "formula"], reduce=True,
                formula={"lhs": f"{p}/{A}", "rhs": f"{q}/{B}{sign}{r}/{C}", "solveFor": target})


GROUPS = [
    ("val", "Значение: корни из дробей", g_val),
    ("val2", "Значение с корнями", g_val2),
    ("dec", "Корни из больших и десятичных", g_dec),
    ("out", "Вынеси множитель", g_out),
    ("sq", "Квадрат суммы с корнем", g_sq),
    ("rat", "Корень в знаменателе", g_rat),
    ("conj", "Пара чисел", g_conj),
    ("prd", "Дроби: умножить и делить", g_prd),
    ("frm", "Выразить из формулы", g_frm),
]
