"""Общие помощники генераторов: формулы для приложения (mathjs) и TeX, проверки через SymPy."""
from __future__ import annotations

import math
import random
import re
from decimal import Decimal
from fractions import Fraction

import sympy as sp

LEVEL_PATTERN = [1, 1, 2, 1, 2, 3, 2, 3]  # первые 8 заданий группы: цель по типу
N_PER_GROUP = 24  # три круга по 8

SYMS = {c: sp.Symbol(c) for c in "abcdefghijklmnopqrstuvwxyz" if c not in "eiIEOSNQ"}


def parse_app(expr: str):
    """Запись приложения (mathjs) → выражение SymPy."""
    s = expr.replace("^", "**")
    return sp.sympify(s, locals=SYMS)


def same(a: str, b: str) -> bool:
    d = parse_app(a) - parse_app(b)
    if not d.free_symbols:
        return abs(sp.N(d, 30)) < 1e-12
    return sp.simplify(d) == 0


def is_square(n: int) -> bool:
    return n >= 0 and math.isqrt(n) ** 2 == n


def squarefree(n: int) -> bool:
    d = 2
    while d * d <= n:
        if n % (d * d) == 0:
            return False
        d += 1
    return True


# ---------- числа и TeX ----------

def fr(x) -> Fraction:
    return Fraction(x).limit_denominator(10**9)


def ans(x) -> str:
    """Fraction/int → строка ответа 'p/q' или 'n'."""
    f = fr(x)
    return str(f.numerator) if f.denominator == 1 else f"{f.numerator}/{f.denominator}"


def tex_num(x) -> str:
    f = fr(x)
    if f.denominator == 1:
        return str(f.numerator)
    sign = "-" if f < 0 else ""
    return f"{sign}\\frac{{{abs(f.numerator)}}}{{{f.denominator}}}"


def dec_str(d: Decimal) -> str:
    s = format(d.normalize(), "f")
    if "." not in s:
        return s
    return s.rstrip("0").rstrip(".") if "." in s else s


def dec_expr(d: Decimal) -> str:
    """Десятичное для записи приложения (точка)."""
    return dec_str(d)


def dec_tex(d: Decimal) -> str:
    return dec_str(d).replace(".", "{,}")


def sq_tex(n) -> str:
    return f"\\sqrt{{{n}}}"


def poly_tex(a, b, c, v="x") -> str:
    """ax²+bx+c без лишних единиц и нулей."""
    out = ""
    for coef, p in ((a, f"{v}^2"), (b, v), (c, "")):
        if coef == 0:
            continue
        mag = abs(coef)
        term = (str(mag) if (mag != 1 or p == "") else "") + p
        out += ("-" if coef < 0 else ("+" if out else "")) + term
    return out or "0"


def poly_expr(a, b, c, v="x") -> str:
    parts = []
    for coef, p in ((a, f"{v}^2"), (b, v), (c, "")):
        if coef == 0:
            continue
        mag = abs(coef)
        term = f"{mag}*{p}" if p and mag != 1 else (p if p else str(mag))
        parts.append(("-" if coef < 0 else ("+" if parts else "")) + term)
    return "".join(parts) or "0"


def par(v) -> str:
    """Число в скобках, если оно отрицательное: 5 → 5, -5 → (-5)."""
    return str(v) if v >= 0 else f"({v})"


def sgn_term(v, first: bool = False) -> str:
    """Слагаемое со знаком для TeX: +3, -2 (для первого слагаемого плюс не пишем)."""
    return (str(v) if v < 0 else (str(v) if first else f"+{v}"))


def lin_rad_tex(e) -> str:
    """Сумма «число + число·корень» в порядке «сначала число»: 19+8\\sqrt{3}."""
    e = sp.expand(e)
    const, rest = e.as_coeff_Add()
    if rest == 0:
        return sp.latex(const)
    r = sp.latex(rest)
    if const == 0:
        return r
    return f"{sp.latex(const)}{r if r.startswith('-') else '+' + r}"


def disc_steps(a: int, b: int, c: int) -> list[str]:
    """Аккуратная запись D = b² − 4ac без двойных минусов."""
    D = b * b - 4 * a * c
    ac4 = 4 * a * c
    mid = f"{b * b}+{-ac4}" if ac4 < 0 else f"{b * b}-{ac4}"
    first = f"$D=b^2-4ac={par(b)}^2-4\\cdot{par(a)}\\cdot{par(c)}={mid}={D}$."
    return [f"$a={a}$, $b={b}$, $c={c}$.", first]


def sym_to_app(e) -> str:
    """Выражение SymPy → запись приложения."""
    return str(e).replace("**", "^")


def sym_to_tex(e) -> str:
    return sp.latex(e)


def pick_distinct(rng: random.Random, pool, k):
    return rng.sample(list(pool), k)


class Sqrt:
    """Число sign·coef·√rad (rad — Fraction), для сравнений и порядка."""

    def __init__(self, sign: int, coef: int, rad):
        self.sign, self.coef, self.rad = sign, coef, fr(rad)

    @property
    def square(self) -> Fraction:
        return self.coef**2 * self.rad

    def value(self) -> float:
        return self.sign * self.coef * math.sqrt(float(self.rad))

    def expr(self) -> str:
        rad = self.rad
        if rad == 1:
            body = str(self.coef)
        else:
            r = f"sqrt({rad.numerator})" if rad.denominator == 1 else f"sqrt({rad.numerator}/{rad.denominator})"
            body = r if self.coef == 1 else f"{self.coef}*{r}"
        return ("-" if self.sign < 0 else "") + body

    def tex(self) -> str:
        rad = self.rad
        if rad == 1:
            body = str(self.coef)
        else:
            r = sq_tex(rad.numerator if rad.denominator == 1 else f"\\frac{{{rad.numerator}}}{{{rad.denominator}}}")
            body = r if self.coef == 1 else f"{self.coef}{r}"
        return ("-" if self.sign < 0 else "") + body


def radical_ok(e) -> bool:
    """Те же правила, что в приложении: корень из свободного от квадратов целого, без корня в знаменателе."""
    for sub in sp.preorder_traversal(e):
        if isinstance(sub, sp.Pow) and sub.exp == sp.Rational(1, 2):
            base = sub.base
            if not base.is_Integer or int(base) < 2 or not squarefree(int(base)):
                return False
        if isinstance(sub, sp.Pow) and sub.exp.is_negative:
            if any(isinstance(s2, sp.Pow) and s2.exp == sp.Rational(1, 2) for s2 in sp.preorder_traversal(sub.base)):
                return False
    return True


def task(prompt, answer, kind, hint, solution, skills, **extra):
    d = dict(prompt=prompt, answer=answer, answerKind=kind, hint=hint, solution=solution, skills=skills)
    d.update(extra)
    return d


def build_group(gen, rng: random.Random, group_id: str, limit: int = N_PER_GROUP):
    """24 заданий группы: уровни идут по LEVEL_PATTERN, повторов по условию нет."""
    out, seen, attempts = [], set(), 0
    while len(out) < limit and attempts < limit * 400:
        attempts += 1
        level = LEVEL_PATTERN[len(out) % len(LEVEL_PATTERN)]
        t = gen(rng, level)
        if t is None:
            continue
        key = (t["prompt"], t.get("expr"), t.get("expr2"), tuple(t.get("items") or ()), tuple(t.get("options") or ()))
        if key in seen:
            continue
        seen.add(key)
        t["group"] = group_id
        t["level"] = level
        t["id"] = f"g-{group_id}-{len(out) + 1:02d}"
        t["source"] = "генератор"
        out.append(t)
    if len(out) < limit:
        raise RuntimeError(f"Группа {group_id}: получилось только {len(out)} из {limit}")
    return out
