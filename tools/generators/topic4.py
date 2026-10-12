"""Тема 4: упрощение выражений с корнями (КР №3 A2, КР №4, классная работа №2, КР №2)."""
from __future__ import annotations

import math
import random
from decimal import Decimal
from fractions import Fraction

import sympy as sp

from common import *  # noqa: F401,F403

NONSQ = [x for x in range(2, 20) if not is_square(x)]
SQF = [2, 3, 5, 6, 7, 10, 11, 13]
DEN_POOL = [2, 3, 4, 5, 6, 9, 10, 12, 15]


def _frac_root(rng, qs=DEN_POOL):
    q = rng.choice(qs)
    p = rng.choice([x for x in range(1, 2 * q) if math.gcd(x, q) == 1 and x != q][:8] or [1])
    return p, q


def _root_line(p, q):
    return f"$\\sqrt{{\\frac{{{p * p}}}{{{q * q}}}}}=\\frac{{{p}}}{{{q}}}$"


# ---------- КР №3 A2: корни из дробей ----------

def g_val(rng: random.Random, level: int):
    limit = {1: 15, 2: 20, 3: 30}[level]
    for _ in range(300):
        if level == 1:
            k = rng.randint(2, 5)
            (p1, q1), (p2, q2) = _frac_root(rng), _frac_root(rng)
            total = k * Fraction(p1, q1) - Fraction(p2, q2)
            expr = f"{k}*sqrt({p1 * p1}/{q1 * q1}) - sqrt({p2 * p2}/{q2 * q2})"
            sol = [_root_line(p1, q1) + ", " + _root_line(p2, q2) + ".",
                   f"${k}\\cdot{tex_num(Fraction(p1, q1))}-{tex_num(Fraction(p2, q2))}={tex_num(total)}$."]
        elif level == 2:
            k1, k2 = rng.randint(2, 4), rng.randint(2, 4)
            (p1, q1), (p2, q2), (p3, q3) = (_frac_root(rng) for _ in range(3))
            sg = rng.choice(["+", "-"])
            total = k1 * Fraction(p1, q1) + (k2 if sg == "+" else -k2) * Fraction(p2, q2) - Fraction(p3, q3)
            expr = f"{k1}*sqrt({p1 * p1}/{q1 * q1}) {sg} {k2}*sqrt({p2 * p2}/{q2 * q2}) - sqrt({p3 * p3}/{q3 * q3})"
            sol = [", ".join(_root_line(p, q) for p, q in ((p1, q1), (p2, q2), (p3, q3))) + ".",
                   f"${k1}\\cdot{tex_num(Fraction(p1, q1))}{sg}{k2}\\cdot{tex_num(Fraction(p2, q2))}-{tex_num(Fraction(p3, q3))}={tex_num(total)}$."]
        else:
            (p1, q1), (p2, q2) = _frac_root(rng, [2, 3, 4, 5, 6, 8, 9]), _frac_root(rng, [2, 3, 4, 5, 6, 8, 9])
            s = rng.randint(2, 12)
            total = Fraction(p1, q1) * Fraction(p2, q2) + s
            expr = f"sqrt({p1 * p1}/{q1 * q1})*sqrt({p2 * p2}/{q2 * q2}) + sqrt({s * s})"
            sol = [_root_line(p1, q1) + ", " + _root_line(p2, q2) + f", $\\sqrt{{{s * s}}}={s}$.",
                   f"${tex_num(Fraction(p1, q1))}\\cdot{tex_num(Fraction(p2, q2))}+{s}={tex_num(total)}$."]
        if fr(total).denominator <= limit and abs(total) < 40 and total != 0:
            return task("Найдите значение выражения {expr}.", ans(total), "expr",
                        "Найди значение каждого корня отдельно: $\\sqrt{\\frac{a^2}{b^2}}=\\frac{a}{b}$, потом выполни действия с дробями.",
                        sol, ["sqrt-frac", "fractions"], expr=expr, verify={"op": "self"})
    return None


# ---------- КР №4 A2: √(a·b), √a/√b, √((−n)²) ----------

def g_val2(rng: random.Random, level: int):
    squares = [4, 9, 16, 25, 36, 49, 64, 81, 100]
    u, v = rng.sample(squares, 2)
    c = rng.choice([2, 3, 5, 6, 7])
    m = rng.randint(2, 6)
    k, n = rng.randint(2, 4), rng.randint(2, 5)
    base = math.isqrt(u) * math.isqrt(v)
    s1 = f"$\\sqrt{{{u}\\cdot{v}}}=\\sqrt{{{u}}}\\cdot\\sqrt{{{v}}}={math.isqrt(u)}\\cdot{math.isqrt(v)}={base}$."
    s2 = f"$\\dfrac{{\\sqrt{{{c * m * m}}}}}{{\\sqrt{{{c}}}}}=\\sqrt{{{m * m}}}={m}$."
    s3 = f"${k}\\sqrt{{(-{n})^2}}={k}\\cdot{n}={k * n}$ (корень не бывает отрицательным: $\\sqrt{{a^2}}=|a|$)."
    if level == 1:
        total = base - m
        expr = f"sqrt({u}*{v}) - sqrt({c * m * m})/sqrt({c})"
        sol = [s1, s2, f"${base}-{m}={total}$."]
    elif level == 2:
        total = base - m + k * n
        expr = f"sqrt({u}*{v}) - sqrt({c * m * m})/sqrt({c}) + {k}*sqrt((-{n})^2)"
        sol = [s1, s2, s3, f"${base}-{m}+{k * n}={total}$."]
    else:
        w = rng.choice([4, 9, 16, 25])
        z = rng.randint(2, 5)
        total = base - m + k * n - z * math.isqrt(w)
        expr = f"sqrt({u}*{v}) - sqrt({c * m * m})/sqrt({c}) + {k}*sqrt((-{n})^2) - {z}*sqrt({w})"
        sol = [s1, s2, s3, f"${z}\\sqrt{{{w}}}={z}\\cdot{math.isqrt(w)}={z * math.isqrt(w)}$.",
               f"${base}-{m}+{k * n}-{z * math.isqrt(w)}={total}$."]
    return task("Найдите значение выражения {expr}.", ans(total), "expr",
                "Вычисли каждое слагаемое отдельно: корень из произведения, корень из дроби, корень из квадрата.",
                sol, ["sqrt-prod", "sqrt-ops", "abs-sqrt"], expr=expr, verify={"op": "self"})


# ---------- классная работа №2: большие числа и десятичные ----------

def g_dec(rng: random.Random, level: int):
    if level == 1:
        p, q = rng.sample([10, 20, 25, 30, 40, 50, 60], 2)
        r, s = rng.sample([6, 8, 9, 12, 15, 18, 20, 24, 25], 2)
        val = Fraction(p * q, r * s)
        expr = f"sqrt({p * p}*{q * q})/(sqrt({r * r})*sqrt({s * s}))"
        sol = [f"$\\sqrt{{{p * p}\\cdot{q * q}}}=\\sqrt{{{p * p}}}\\cdot\\sqrt{{{q * q}}}={p}\\cdot{q}={p * q}$.",
               f"$\\sqrt{{{r * r}}}\\cdot\\sqrt{{{s * s}}}={r}\\cdot{s}={r * s}$.",
               f"$\\dfrac{{{p * q}}}{{{r * s}}}={tex_num(val)}$."]
        return task("Найдите значение выражения {expr}.", ans(val), "expr",
                    "Извлеки каждый корень отдельно (корень из произведения — произведение корней), потом посчитай дробь.",
                    sol, ["sqrt-prod", "decimals", "fractions"], expr=expr, verify={"op": "self"})
    pool = [2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 15, 25]
    vals = rng.sample(pool, 4)
    a, b, c, d = (Decimal(v).scaleb(-rng.choice([0, 1, 2])) for v in vals)
    if len({a, b, c, d}) < 4:
        return None
    val = Fraction(a) * Fraction(b) / (Fraction(c) * Fraction(d))
    if val.denominator > 400:
        return None
    A, B, C, D = a * a, b * b, c * c, d * d
    if level == 2:
        expr = f"sqrt({dec_expr(A)})*sqrt({dec_expr(B)})/(sqrt({dec_expr(C)})*sqrt({dec_expr(D)}))"
    else:
        expr = f"sqrt({dec_expr(A)}*{dec_expr(B)})/(sqrt({dec_expr(C)})*sqrt({dec_expr(D)}))"
    sol = [f"$\\sqrt{{{dec_tex(A)}}}={dec_tex(a)}$, $\\sqrt{{{dec_tex(B)}}}={dec_tex(b)}$ (два знака после запятой под корнем — один знак в ответе).",
           f"$\\sqrt{{{dec_tex(C)}}}={dec_tex(c)}$, $\\sqrt{{{dec_tex(D)}}}={dec_tex(d)}$.",
           f"$\\dfrac{{{dec_tex(a)}\\cdot{dec_tex(b)}}}{{{dec_tex(c)}\\cdot{dec_tex(d)}}}={tex_num(val)}$."]
    return task("Найдите значение выражения {expr}.", ans(val), "expr",
                "Извлеки каждый корень отдельно (корень из произведения — произведение корней), потом посчитай дробь.",
                sol, ["sqrt-prod", "decimals", "fractions"], expr=expr, verify={"op": "self"})


# ---------- вынести множитель, упростить ----------

def _pairs_text(n: int) -> str:
    fs = sp.factorint(n)
    outside, rest = 1, 1
    pair_list = []
    for p, e in sorted(fs.items()):
        outside *= p ** (e // 2)
        rest *= p ** (e % 2)
        pair_list += [f"{p}\\cdot{p}" for _ in range(e // 2)]
    fx = "\\cdot ".join(str(p) for p, e in sorted(fs.items()) for _ in range(e))
    pairs = ", ".join(f"$({x})$" for x in pair_list)
    res = f"{outside}\\sqrt{{{rest}}}" if rest > 1 else str(outside)
    return f"${n}={fx}$. Пары одинаковых множителей: {pairs}. Каждая пара выходит из-под корня одним числом: $\\sqrt{{{n}}}={res}$."


def g_out(rng: random.Random, level: int):
    def finish(expr, hint, sol, skills, answer_tex=None):
        e = sp.expand(parse_app(expr))
        assert radical_ok(e), (expr, e)
        return task("Упростите выражение {expr}.", sym_to_app(e), "expr", hint, sol + [f"Ответ: ${answer_tex or lin_rad_tex(e)}$."],
                    skills, expr=expr, radical=True, verify={"op": "self"})

    if level == 1:
        k, m = rng.randint(2, 9), rng.choice([2, 3, 5, 6, 7, 10, 11])
        return finish(f"sqrt({k * k * m})", "Разложи число под корнем на множители и найди пары одинаковых.",
                      [_pairs_text(k * k * m)], ["sqrt-extract"])
    if level == 2:
        for _ in range(100):
            m = rng.choice([2, 3, 5, 6, 7])
            ks = rng.sample(range(2, 7), 3)
            cf = [rng.randint(1, 3) for _ in range(3)]
            sg = ["+", rng.choice(["+", "-"]), rng.choice(["+", "-"])]
            if sum(((-1) ** (sgn == "-")) * c * kk for sgn, c, kk in zip(sg, cf, ks)) == 0:
                continue
            parts = []
            for sgn, c, kk in zip(sg, cf, ks):
                body = (f"{c}*" if c != 1 else "") + f"sqrt({kk * kk * m})"
                parts.append((" - " if sgn == "-" else (" + " if parts else "")) + body)
            expr = "".join(parts)
            sol = ["Вынесем множители из-под каждого корня: " + ", ".join(f"$\\sqrt{{{kk * kk * m}}}={kk}\\sqrt{{{m}}}$" for kk in ks) + ".",
                   "Теперь у всех слагаемых одинаковый корень, и их можно складывать и вычитать «как подобные»."]
            return finish(expr, "Сначала упрости каждый корень, потом приведи подобные слагаемые.", sol, ["sqrt-extract", "like-terms"])
        return None
    kind = rng.choice(["prod", "square", "diff"])
    if kind == "prod":
        k, m = rng.randint(2, 6), rng.choice([2, 3, 5, 6, 7])
        N = k * k * m
        divisors = [d for d in range(2, N) if N % d == 0 and d != N // d]
        a = rng.choice(divisors)
        b = N // a
        sol = [f"$\\sqrt{{{a}}}\\cdot\\sqrt{{{b}}}=\\sqrt{{{a}\\cdot {b}}}=\\sqrt{{{N}}}$.", _pairs_text(N)]
        return finish(f"sqrt({a})*sqrt({b})", "Перемножь числа под корнями, потом вынеси множители.", sol, ["sqrt-prod", "sqrt-extract"])
    if kind == "square":
        m, k = rng.choice([2, 3, 5, 6, 7, 10, 11]), rng.randint(1, 4)
        e = sp.expand((sp.sqrt(m) + k) ** 2)
        sol = [f"Квадрат суммы: $(\\sqrt{{{m}}}+{k})^2=(\\sqrt{{{m}}})^2+2\\cdot{k}\\cdot\\sqrt{{{m}}}+{k}^2={m}+{2 * k}\\sqrt{{{m}}}+{k * k}$."]
        return finish(f"(sqrt({m})+{k})^2", "Квадрат суммы: $(a+b)^2=a^2+2ab+b^2$, помни $(\\sqrt{m})^2=m$.", sol, ["fsu", "sqrt-ops"], lin_rad_tex(e))
    m, k = rng.choice([2, 3, 5, 6, 7, 10, 11]), rng.randint(1, 5)
    if k * k == m:
        return None
    sol = [f"Разность квадратов: $(\\sqrt{{{m}}}+{k})(\\sqrt{{{m}}}-{k})=(\\sqrt{{{m}}})^2-{k}^2={m}-{k * k}={m - k * k}$."]
    return finish(f"(sqrt({m})+{k})*(sqrt({m})-{k})", "Разность квадратов: $(a+b)(a-b)=a^2-b^2$.", sol, ["fsu", "sqrt-ops"])


# ---------- КР №4 B1 и родственные ----------

def g_sq(rng: random.Random, level: int):
    a = rng.choice([x for x in SQF if x >= 5])
    q = rng.randint(1, 4)
    if level == 1:
        s = rng.choice([-1, 1])
        sg = "-" if s < 0 else "+"
        expr = f"((sqrt({a}){sg}{2 * q})^2-{a})/(sqrt({a}){sg}{q})"
        total = -4 * q if s < 0 else 4 * q
        sol = [f"$(\\sqrt{{{a}}}{sg}{2 * q})^2={a}{sg}{4 * q}\\sqrt{{{a}}}+{4 * q * q}$.",
               f"Числитель: ${a}{sg}{4 * q}\\sqrt{{{a}}}+{4 * q * q}-{a}={4 * q * q}{sg}{4 * q}\\sqrt{{{a}}}={'-' if s < 0 else ''}{4 * q}(\\sqrt{{{a}}}{sg}{q})$.",
               f"Сокращаем на $(\\sqrt{{{a}}}{sg}{q})$: получаем ${total}$."]
        return task("Упростите выражение {expr}.", str(total), "expr",
                    "Раскрой квадрат в числителе, вынеси общий множитель и сократи на скобку из знаменателя.", sol,
                    ["fsu", "sqrt-ops", "cancel"], expr=expr, verify={"op": "self"})
    if level == 2:
        if rng.random() < 0.5:
            expr = f"((sqrt({a})+{q})^2-(sqrt({a})-{q})^2)/sqrt({a})"
            total = 4 * q
            sol = [f"Раскроем скобки: $(\\sqrt{{{a}}}+{q})^2-(\\sqrt{{{a}}}-{q})^2=({a}+{2 * q}\\sqrt{{{a}}}+{q * q})-({a}-{2 * q}\\sqrt{{{a}}}+{q * q})={4 * q}\\sqrt{{{a}}}$.",
                   f"Делим на $\\sqrt{{{a}}}$: ${total}$."]
        else:
            b = rng.choice([x for x in SQF if x != a])
            expr = f"((sqrt({a})+sqrt({b}))^2-{a}-{b})/sqrt({a}*{b})"
            total = 2
            sol = [f"$(\\sqrt{{{a}}}+\\sqrt{{{b}}})^2={a}+{b}+2\\sqrt{{{a * b}}}$.",
                   f"Числитель: ${a}+{b}+2\\sqrt{{{a * b}}}-{a}-{b}=2\\sqrt{{{a * b}}}$, знаменатель $\\sqrt{{{a * b}}}$. Ответ ${total}$."]
        return task("Упростите выражение {expr}.", str(total), "expr", "Раскрой скобки по формуле квадрата суммы и приведи подобные.", sol,
                    ["fsu", "sqrt-ops", "cancel"], expr=expr, verify={"op": "self"})
    form = rng.choice(["ratio", "sumsq", "diffsq"])
    if form == "ratio":
        b = rng.choice([x for x in SQF if x != a])
        expr = f"((sqrt({a})+sqrt({b}))^2+(sqrt({a})-sqrt({b}))^2)/({a}+{b})"
        sol = [f"$(\\sqrt{{{a}}}+\\sqrt{{{b}}})^2+(\\sqrt{{{a}}}-\\sqrt{{{b}}})^2=2\\cdot({a}+{b})$: слагаемые с корнем уничтожаются.",
               f"$\\dfrac{{2({a}+{b})}}{{{a}+{b}}}=2$."]
        return task("Упростите выражение {expr}.", "2", "expr", "В сумме квадратов суммы и разности слагаемые $2\\sqrt{ab}$ сокращаются.", sol,
                    ["fsu", "sqrt-ops", "cancel"], expr=expr, verify={"op": "self"})
    if form == "sumsq":
        total = 2 * a + 2 * q * q
        expr = f"(sqrt({a})+{q})^2+(sqrt({a})-{q})^2"
        sol = [f"$(\\sqrt{{{a}}}+{q})^2={a}+{2 * q}\\sqrt{{{a}}}+{q * q}$ и $(\\sqrt{{{a}}}-{q})^2={a}-{2 * q}\\sqrt{{{a}}}+{q * q}$.",
               f"Складываем: корни уничтожаются, остаётся ${a}+{q * q}+{a}+{q * q}={total}$."]
        return task("Найдите значение выражения {expr}.", str(total), "expr", "Раскрой обе скобки: слагаемые с корнем взаимно уничтожатся.", sol,
                    ["fsu", "sqrt-ops"], expr=expr, verify={"op": "self"})
    b = rng.choice([x for x in SQF if x != a and math.gcd(x, a) == 1])
    e = 4 * sp.sqrt(a * b)
    expr = f"(sqrt({a})+sqrt({b}))^2-(sqrt({a})-sqrt({b}))^2"
    sol = [f"$(\\sqrt{{{a}}}+\\sqrt{{{b}}})^2={a}+{b}+2\\sqrt{{{a * b}}}$ и $(\\sqrt{{{a}}}-\\sqrt{{{b}}})^2={a}+{b}-2\\sqrt{{{a * b}}}$.",
           f"Вычитаем: $4\\sqrt{{{a * b}}}$."]
    return task("Упростите выражение {expr}.", sym_to_app(e), "expr", "Раскрой скобки и вычти: остаётся удвоенное $2\\cdot 2\\sqrt{ab}$.", sol,
                ["fsu", "sqrt-ops"], expr=expr, radical=True, verify={"op": "self"})


# ---------- корень в знаменателе (КР №4 B1/C2) ----------

def _den_tex(form: str, a: int, t: int) -> tuple[str, str, str, str, str]:
    """(знаменатель в app, TeX знаменателя, TeX «двойника», TeX произведения, значение произведения)."""
    if form == "A":
        app = f"sqrt({a})+{t}" if t > 0 else f"sqrt({a})-{-t}"
        tex = f"\\sqrt{{{a}}}{'+' if t > 0 else '-'}{abs(t)}"
        conj = f"\\sqrt{{{a}}}{'-' if t > 0 else '+'}{abs(t)}"
        prod = f"{a}-{t * t}"
        return app, tex, conj, prod, str(a - t * t)
    app = f"{t}-sqrt({a})"
    tex = f"{t}-\\sqrt{{{a}}}"
    conj = f"{t}+\\sqrt{{{a}}}"
    return app, tex, conj, f"{t * t}-{a}", str(t * t - a)


def _rat_terms(rng, a, n_terms):
    for _ in range(400):
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
            if form == "A":
                d0 = a - t * t
                k = c * d0
                total += -c * t
            else:
                d0 = t * t - a
                k = c * d0
                total += c * t
            if abs(k) > 45 or k == 0:
                ok = False
                break
            terms.append((k, form, t, c))
        if not ok:
            continue
        return terms, total
    return None


def g_rat(rng: random.Random, level: int):
    a = rng.choice([2, 3, 5, 6, 7, 10, 11])
    if level == 1:
        if rng.random() < 0.4:
            m = rng.randint(2, 6)
            k = m * a
            e = sp.sqrt(a) * m
            sol = [f"Умножаем числитель и знаменатель на $\\sqrt{{{a}}}$: $\\dfrac{{{k}}}{{\\sqrt{{{a}}}}}=\\dfrac{{{k}\\sqrt{{{a}}}}}{{\\sqrt{{{a}}}\\cdot\\sqrt{{{a}}}}}=\\dfrac{{{k}\\sqrt{{{a}}}}}{{{a}}}={m}\\sqrt{{{a}}}$."]
            return task("Избавьтесь от корня в знаменателе: {expr}.", sym_to_app(e), "expr",
                        "Умножь числитель и знаменатель на $\\sqrt{a}$: в знаменателе получится $a$.", sol,
                        ["rationalize"], expr=f"{k}/sqrt({a})", radical=True, verify={"op": "self"})
        t = rng.randint(1, 4)
        if t * t == a:
            return None
        form = rng.choice(["A", "C"])
        app, tex, conj, prod, pval = _den_tex(form, a, t)
        d0 = int(pval)
        mult = rng.randint(1, 3)
        k = mult * abs(d0)
        c = mult * (1 if d0 > 0 else -1)
        res = sp.expand(c * (sp.sqrt(a) - t)) if form == "A" else sp.expand(c * (t + sp.sqrt(a)))
        sol = [f"Умножаем числитель и знаменатель на «двойника» знаменателя ${conj}$.",
               f"Знаменатель: $({tex})({conj})={prod}={d0}$ (разность квадратов).",
               f"$\\dfrac{{{k}}}{{{tex}}}=\\dfrac{{{k}({conj})}}{{{d0}}}={lin_rad_tex(res)}$."]
        return task("Избавьтесь от корня в знаменателе: {expr}.", sym_to_app(res), "expr",
                    "Умножь верх и низ на «двойника» знаменателя: в знаменателе получится разность квадратов.", sol,
                    ["rationalize", "fsu"], expr=f"{k}/({app})", radical=True, verify={"op": "self"})
    n = 2 if level == 2 else 3
    r = _rat_terms(rng, a, n)
    if r is None:
        return None
    terms, total = r
    pieces, expr = [], ""
    for i, (k, form, t, c) in enumerate(terms):
        app, tex, conj, prod, pval = _den_tex(form, a, t)
        res = sp.expand(c * (sp.sqrt(a) - t)) if form == "A" else sp.expand(c * (t + sp.sqrt(a)))
        sgn = "-" if k < 0 else "+"
        expr += (f" {sgn} " if i else ("-" if k < 0 else "")) + f"{abs(k)}/({app})"
        pieces.append(f"$\\dfrac{{{k}}}{{{tex}}}=\\dfrac{{{k}({conj})}}{{{pval}}}={lin_rad_tex(res)}$")
    sol = ["Избавимся от корня в знаменателе у каждой дроби, домножив числитель и знаменатель на «двойника» знаменателя (разность квадратов даёт целое число):"]
    sol += pieces
    sol.append(f"Складываем: слагаемые с $\\sqrt{{{a}}}$ взаимно уничтожаются, остаётся ${sp.latex(total)}$.")
    return task("Упростите выражение {expr}.", str(total), "expr",
                "У каждой дроби умножь числитель и знаменатель на выражение, которое даёт в знаменателе разность квадратов.", sol,
                ["rationalize", "fsu"], expr=expr, verify={"op": "self"})


# ---------- КР №4 C1: пара обратных/противоположных ----------

PELL = [(2, 3, 2), (3, 7, 4), (5, 9, 4), (6, 5, 2), (7, 8, 3), (8, 3, 1), (10, 19, 6), (11, 10, 3), (12, 7, 2), (15, 4, 1), (24, 5, 1), (35, 6, 1)]


def pell_simple(a: int, q: int, p: int):
    """q² − p²a = 1; приводим p√a к виду с корнем из числа без квадратных множителей: (8, 3, 1) → (2, 3, 2)."""
    s = max(d for d in range(1, math.isqrt(a) + 1) if a % (d * d) == 0)
    return a // (s * s), q, p * s


def g_conj(rng: random.Random, level: int):
    a, q, p = pell_simple(*rng.choice(PELL))
    inverse = level == 1 or rng.random() < 0.5
    r = f"{p}\\sqrt{{{a}}}" if p != 1 else f"\\sqrt{{{a}}}"
    x = (f"{r}-{q}", f"{p}*sqrt({a})-{q}")
    z = (f"\\dfrac{{1}}{{{r}+{q}}}", f"1/({p}*sqrt({a})+{q})")
    if inverse:
        y = (f"-{r}-{q}", f"-{p}*sqrt({a})-{q}")
        pair, kind, word = (0, 1), "inverse", "взаимно обратных"
        sol = [f"Перемножим первое и второе: $({r}-{q})(-{r}-{q})=-({r}-{q})({r}+{q})=-({p * p * a}-{q * q})=1$.",
               "Произведение равно 1, значит эти числа взаимно обратные."]
    else:
        y = (f"{r}+{q}", f"{p}*sqrt({a})+{q}")
        pair, kind, word = (0, 2), "opposite", "противоположных"
        sol = [f"$({r}+{q})({r}-{q})={p * p * a}-{q * q}=-1$, поэтому $\\dfrac{{1}}{{{r}+{q}}}=-({r}-{q})$.",
               f"Значит число $\\dfrac{{1}}{{{r}+{q}}}$ противоположно числу ${r}-{q}$."]
    nums = [x, y, z]
    order = [0, 1, 2]
    rng.shuffle(order)
    shown = [nums[i] for i in order]
    pos = {orig: new for new, orig in enumerate(order)}
    pairs = [(0, 1), (0, 2), (1, 2)]
    correct_pair = tuple(sorted((pos[pair[0]], pos[pair[1]])))
    options = [f"${shown[i][0]}$ и ${shown[j][0]}$" for i, j in pairs]
    items = ";  ".join(f"${s[0]}$" for s in shown)
    return task(f"Среди чисел {items} найдите пару {word} чисел.", str(pairs.index(correct_pair)), "choice",
                "Перемножь числа попарно: у взаимно обратных произведение равно 1, у противоположных сумма равна 0.",
                sol, ["rationalize", "fsu"], options=options,
                pairCheck={"kind": kind, "exprs": [s[1] for s in shown], "pair": list(correct_pair)})


# ---------- КР №2: произведение и частное дробей ----------

def g_prd(rng: random.Random, level: int):
    def build(n1, d1, n2, d2, op):
        """n1/d1 (·|:) n2/d2 — строки в записи приложения; возвращает expr и TeX."""
        e1, e2 = f"({n1})/({d1})", f"({n2})/({d2})"
        expr = f"({e1})*({e2})" if op == "mul" else f"({e1})/({e2})"
        # дроби в TeX берём «как введено», без автоматического сокращения SymPy
        def frac_tex(n, d):
            return f"\\dfrac{{{sp.latex(parse_app(n))}}}{{{sp.latex(parse_app(d))}}}"
        tex = frac_tex(n1, d1) + ("\\cdot " if op == "mul" else ":") + frac_tex(n2, d2)
        return expr, tex

    if level == 1:
        p, q = rng.randint(2, 4), rng.randint(2, 6)
        m, n = rng.randint(1, 3), rng.randint(1, 4)
        op = rng.choice(["mul", "div"])
        n1, d1, n2, d2 = f"{p}*a^2", f"x^{m}", f"x^{m + n}", f"{q}*a"
        if op == "div":
            n2, d2 = f"{q}*a", f"x^{m + n}"
    elif level == 2:
        if rng.random() < 0.5:
            p, q, s, n, m = rng.randint(2, 6), rng.randint(2, 5), rng.randint(1, 3), rng.randint(3, 6), rng.randint(1, 2)
            op = "mul"
            n1, d1, n2, d2 = f"a^2+{p}*a", f"x^{m}", f"a^{s}*x^{n}", f"{q}*a+{q * p}"
        else:
            c1, c2 = rng.randint(1, 3), rng.randint(2, 5)
            u, v = rng.sample(range(2, 7), 2)
            op = "div"
            n1, d1 = f"{u * c1}*a+{u * c2}*b", f"a^{rng.randint(3, 9)}*x"
            n2, d2 = f"{v * c1}*a+{v * c2}*b", f"a^{rng.randint(2, 4)}*x^{rng.randint(3, 6)}"
    else:
        p, q = rng.sample(range(2, 8), 2)
        op = rng.choice(["mul", "div"])
        n1, d1 = f"a^2-{p * p}", f"x^2-{q * q}"
        n2, d2 = (f"x+{q}", f"a+{p}") if op == "mul" else (f"a+{p}", f"x-{q}")
    expr, tex = build(n1, d1, n2, d2, op)
    e = sp.cancel(parse_app(expr))
    nn1, dd1, nn2, dd2 = (parse_app(x) for x in (n1, d1, n2, d2))
    flip = (dd2, nn2) if op == "div" else (nn2, dd2)
    fx = lambda z: sp.latex(sp.factor(z))
    sol = []
    if op == "div":
        sol.append(f"Деление заменяем умножением на перевёрнутую дробь: $\\dfrac{{{sp.latex(nn1)}}}{{{sp.latex(dd1)}}}\\cdot\\dfrac{{{sp.latex(flip[0])}}}{{{sp.latex(flip[1])}}}$.")
    sol.append(f"Раскладываем на множители: $\\dfrac{{{fx(nn1)}}}{{{fx(dd1)}}}\\cdot\\dfrac{{{fx(flip[0])}}}{{{fx(flip[1])}}}$.")
    sol.append(f"Сокращаем одинаковые множители: ${sp.latex(sp.factor(e))}$.")
    return task("Упростите выражение {expr}.", sym_to_app(sp.factor(e)) if level == 3 else sym_to_app(e), "expr",
                "Если есть деление, замени его умножением на перевёрнутую дробь. Потом разложи на множители и сократи.", sol,
                ["fraction-mult", "cancel", "fsu"], expr=expr, tex=tex, reduce=True, verify={"op": "self"})


# ---------- КР №2 C1: выразить переменную ----------

def g_frm(rng: random.Random, level: int):
    letters = ["x", "y", "z"]
    rng.shuffle(letters)
    A, B, C = letters
    p, q, r = rng.randint(1, 5), rng.randint(1, 5), rng.randint(1, 5)
    target = rng.choice(letters if level > 1 else [B])
    SA, SB, SC = SYMS[A], SYMS[B], SYMS[C]
    sign = rng.choice(["-", "+"])
    lhs = sp.Rational(p) / SA
    rest_terms = {A: None, B: sp.Rational(q) / SB, C: (-1 if sign == "-" else 1) * sp.Rational(r) / SC}
    rhs = rest_terms[B] + rest_terms[C]
    sols = sp.solve(sp.Eq(lhs, rhs), SYMS[target])
    if len(sols) != 1:
        return None
    ans_e = sp.factor(sp.cancel(sols[0]))
    others = [l for l in letters if l != target]
    frac = lambda n, v: f"\\frac{{{n}}}{{{v}}}"
    tex_eq = f"{frac(p, A)}={frac(q, B)}{sign}{frac(r, C)}"
    St = SYMS[target]
    # шаги: оставить дробь с target одну, остальное перенести
    if target == A:
        combined = sp.together(rhs)
        N, Dn = sp.fraction(combined)
        sol = [f"Правую часть приводим к общему знаменателю: $\\dfrac{{{p}}}{{{A}}}={sp.latex(combined)}$.",
               f"Переворачиваем обе части (дробь равна дроби): ${A}=\\dfrac{{{p}\\cdot {sp.latex(Dn)}}}{{{sp.latex(N)}}}$.",
               f"Упрощаем: ${A}={sp.latex(ans_e)}$."]
    else:
        term = rest_terms[target]
        other = rest_terms[B if target == C else C]
        isolated = sp.together(lhs - other)
        sign_t = "-" if (target == C and sign == "-") else ""
        N, Dn = sp.fraction(isolated)
        lhs_tex = f"{sign_t}\\dfrac{{{r if target == C else q}}}{{{target}}}"
        sol = [f"Оставим дробь с ${target}$ в одной части, остальное перенесём: ${lhs_tex}={sp.latex(lhs - other)}$.",
               f"Правую часть приведём к общему знаменателю: ${lhs_tex}={sp.latex(isolated)}$.",
               f"Выразим ${target}$ (перевернём дроби и учтём числитель слева): ${target}={sp.latex(ans_e)}$."]
    return task(f"Из формулы ${tex_eq}$ выразите ${target}$ через ${others[0]}$ и ${others[1]}$. Ответ упростите.", sym_to_app(ans_e), "expr",
                "Сложи (вычти) дроби с другой стороны, приведя их к общему знаменателю, потом переверни обе части.", sol,
                ["fraction-add", "formula"], reduce=True,
                formula={"lhs": f"{p}/{A}", "rhs": f"{q}/{B}{sign}{r}/{C}", "solveFor": target})


GROUPS = [
    ("val", "Значение: корни из дробей", g_val, 2),
    ("val2", "Значение с корнями", g_val2, 2),
    ("dec", "Корни из больших и десятичных", g_dec, 0),
    ("out", "Вынеси множитель", g_out, 1),
    ("sq", "Квадрат суммы с корнем", g_sq, 3),
    ("rat", "Корень в знаменателе", g_rat, 4),
    ("conj", "Пара чисел", g_conj, 4),
    ("prd", "Дроби: умножить и делить", g_prd, 0),
    ("frm", "Выразить из формулы", g_frm, 0),
]
