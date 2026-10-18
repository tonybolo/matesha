"""Тема 0 «Сложение и вычитание рациональных чисел» (повторение перед рациональными дробями):
числа со знаками — целые, десятичные, обыкновенные дроби и смешанные числа; модуль, сравнение,
вычитание как сложение с противоположным, цепочки со скобками, пропущенное число; ⭐ модули и расстояния.

verify() не пользуется вычислениями генератора. Значение условия считается заново двумя путями:
SymPy по записи для компьютера (`expr`) и собственным разбором TeX — того, что видит ребёнок.
Тем же разбором TeX проверяется каждое равенство и неравенство в решении. Олимпиадные задачи — перебором."""
from __future__ import annotations

import math
import random
import re
from decimal import Decimal
from fractions import Fraction as F

import sympy as sp

from common import dec_str, task

TOPIC = "00-rational-numbers"
DIR = "algebra8"

# ======================================================================
# Числа: запись для ребёнка (TeX) и для компьютера (mathjs)
# ======================================================================


def _is_dec(v: F) -> bool:
    d = F(v).denominator
    for p in (2, 5):
        while d % p == 0:
            d //= p
    return d == 1


def _dec_s(v: F) -> str:
    """Конечная десятичная дробь для компьютера: 3.25, -0.05 (без лишних нулей)."""
    v = F(v)
    if not _is_dec(v):
        raise ValueError(f"{v} — не конечная десятичная дробь")
    s = dec_str(Decimal(v.numerator) / Decimal(v.denominator))
    assert F(s) == v, (s, v)
    return s


def _places(v: F) -> int:
    s = _dec_s(abs(F(v)))
    return len(s.split(".")[1]) if "." in s else 0


def mod_tex(v, st: str = "int", places: int = 0) -> str:
    """Модуль числа для ребёнка: 7; 3{,}25; \\dfrac{3}{4}; 2\\dfrac{1}{3}. places — дописать нули (3{,}70)."""
    a = abs(F(v))
    if st == "dec":
        s = f"{Decimal(a.numerator) / Decimal(a.denominator):.{places}f}" if places else _dec_s(a)
        return s.replace(".", "{,}")
    if a.denominator == 1:
        return str(a.numerator)
    if st == "mixed" and a > 1:
        n, r = divmod(a.numerator, a.denominator)
        return f"{n}\\dfrac{{{r}}}{{{a.denominator}}}"
    return f"\\dfrac{{{a.numerator}}}{{{a.denominator}}}"


def T(v, st: str = "int", wrap: bool = False, places: int = 0) -> str:
    """Число со знаком для ребёнка; wrap — отрицательное число в скобках (когда оно стоит после знака действия)."""
    v = F(v)
    s = mod_tex(v, st, places)
    if v < 0:
        s = "-" + s
        if wrap:
            s = f"\\left({s}\\right)"
    return s


def A(v, st: str = "int", wrap: bool = False) -> str:
    """То же число для компьютера: -3/4, -2.5, -(2+1/3)."""
    v = F(v)
    a = abs(v)
    if a.denominator == 1:
        s = str(a.numerator)
    elif st == "dec":
        s = _dec_s(a)
    elif st == "mixed" and a > 1:
        n, r = divmod(a.numerator, a.denominator)
        s = f"({n}+{r}/{a.denominator})"
    else:
        s = f"{a.numerator}/{a.denominator}"
    if v < 0:
        s = "-" + s
        if wrap:
            s = f"({s})"
    return s


def ans_of(v, st: str = "int") -> str:
    """Ответ для компьютера: -5; -2.45 (десятичные); -5/12 (обыкновенные)."""
    v = F(v)
    if v.denominator == 1:
        return str(v.numerator)
    if st == "dec":
        return _dec_s(v)
    return f"{v.numerator}/{v.denominator}"


def ans_tex(v) -> str | None:
    """Красивая запись ответа-дроби: -\\frac{5}{12} (иначе приложение покажет (−5)/12)."""
    v = F(v)
    if v.denominator == 1:
        return None
    return f"{'-' if v < 0 else ''}\\frac{{{abs(v.numerator)}}}{{{v.denominator}}}"


def steps_word(n) -> str:
    """1 шаг, 2 шага, 5 шагов, 2,5 шага."""
    n = F(n)
    if n.denominator != 1:
        return "шага"
    k = abs(n.numerator)
    if k % 10 == 1 and k % 100 != 11:
        return "шаг"
    if k % 10 in (2, 3, 4) and k % 100 not in (12, 13, 14):
        return "шага"
    return "шагов"


# ---------- выражения: цепочка «знак действия + слагаемое» ----------


class Num:
    __slots__ = ("v", "st")

    def __init__(self, v, st: str = "int"):
        self.v, self.st = F(v), st


class Grp:
    """Скобки (kind='par') или модуль (kind='abs') вокруг цепочки."""

    __slots__ = ("terms", "kind")

    def __init__(self, terms, kind: str = "par"):
        self.terms, self.kind = terms, kind


def c_val(terms) -> F:
    s = F(0)
    for op, it in terms:
        if isinstance(it, Num):
            v = it.v
        else:
            v = c_val(it.terms)
            if it.kind == "abs":
                v = abs(v)
        s = s - v if op == "-" else s + v
    return s


def _render(terms, num, grp) -> str:
    out = ""
    for i, (op, it) in enumerate(terms):
        pre = ("-" if op == "-" else "") if i == 0 else op
        wrap = i > 0 or op == "-"
        out += pre + (num(it, wrap) if isinstance(it, Num) else grp(it))
    return out


def c_tex(terms) -> str:
    return _render(
        terms,
        lambda n, w: T(n.v, n.st, w),
        lambda g: f"\\left({c_tex(g.terms)}\\right)" if g.kind == "par" else f"\\left|{c_tex(g.terms)}\\right|",
    )


def c_app(terms) -> str:
    return _render(
        terms,
        lambda n, w: A(n.v, n.st, w),
        lambda g: f"({c_app(g.terms)})" if g.kind == "par" else f"abs({c_app(g.terms)})",
    )


def two(x, op: str, y, st: str = "int", st2: str | None = None):
    return [("", Num(x, st)), (op, Num(y, st2 or st))]


def sum_tex(vals, st: str = "int") -> str:
    """Слагаемые со знаками без скобок: -12-5+8+4."""
    out = ""
    for i, v in enumerate(vals):
        t = T(v, st)
        out += t if (i == 0 or v < 0) else "+" + t
    return out


# ---------- решения: правила знаков ----------


def add_lines(x, y, st: str = "int", places: int = 0) -> list[str]:
    """Решение x + y по правилам знаков; последняя строка — равенство с ответом."""
    x, y = F(x), F(y)
    s = x + y
    lhs = f"{T(x, st)}+{T(y, st, True)}"

    def M(v):
        return mod_tex(v, st, places)

    if x == 0:
        return [f"К нулю прибавляем число — получается само это число: ${lhs}={T(s, st)}$."]
    if y == 0:
        return [f"Прибавить ноль — число не изменится: ${lhs}={T(s, st)}$."]
    if x > 0 and y > 0:
        return [f"Оба числа положительные: ${lhs}={T(s, st)}$."]
    if x < 0 and y < 0:
        return [
            f"Оба числа отрицательные — знаки одинаковые. Складываем модули: ${M(x)}+{M(y)}={mod_tex(s, st)}$.",
            f"Знак общий — минус: ${lhs}={T(s, st)}$.",
        ]
    if abs(x) == abs(y):
        return [f"Модули одинаковые: $\\left|{T(x, st)}\\right|={M(x)}$ и $\\left|{T(y, st)}\\right|={M(y)}$, а знаки разные.",
                f"Числа ${T(x, st)}$ и ${T(y, st)}$ противоположные, а сумма противоположных чисел равна нулю: ${lhs}=0$."]
    big = x if abs(x) > abs(y) else y
    hi, lo = max(abs(x), abs(y)), min(abs(x), abs(y))
    return [
        f"Знаки разные. Из большего модуля вычитаем меньший: ${M(hi)}-{M(lo)}={mod_tex(hi - lo, st)}$.",
        f"Больше модуль у числа ${T(big, st)}$, поэтому у ответа знак «{'+' if big > 0 else '−'}»: ${lhs}={T(s, st)}$.",
    ]


def sub_line(x, y, st: str = "int", st2: str | None = None) -> str:
    st2 = st2 or st
    return (f"Вычитание заменяем сложением с противоположным числом: "
            f"${T(x, st)}-{T(y, st2, True)}={T(x, st)}+{T(-F(y), st2, True)}$.")


def _over(n: int, L: int) -> str:
    """n/L без сокращения, минус перед дробью: -\\dfrac{9}{12}."""
    if L == 1:
        return str(n)
    return f"{'-' if n < 0 else ''}\\dfrac{{{abs(n)}}}{{{L}}}"


def _over_w(n: int, L: int) -> str:
    return f"\\left({_over(n, L)}\\right)" if n < 0 else _over(n, L)


def frac_lines(x, y) -> list[str]:
    """Решение x + y для обыкновенных дробей: общий знаменатель, числители по правилам знаков, сокращение."""
    x, y = F(x), F(y)
    d1, d2 = x.denominator, y.denominator
    L = math.lcm(d1, d2)
    lines = []
    if d1 == d2:
        lines.append(f"Знаменатели одинаковые (${L}$), складываем числители по правилам знаков.")
    else:
        lo, hi = sorted((d1, d2))
        why = f"${hi}$ делится на ${lo}$" if hi % lo == 0 and lo > 1 else (
            f"любое целое число — это дробь со знаменателем ${hi}$" if lo == 1 else
            f"наименьшее число, которое делится и на ${d1}$, и на ${d2}$")
        conv = []
        for v in (x, y):
            m = L // v.denominator
            if m == 1:
                continue
            n = abs(v.numerator)
            if v.denominator == 1:
                conv.append(f"${n}=\\dfrac{{{n * L}}}{{{L}}}$")
            else:
                conv.append(f"$\\dfrac{{{n}}}{{{v.denominator}}}=\\dfrac{{{n}\\cdot {m}}}{{{v.denominator}\\cdot {m}}}=\\dfrac{{{n * m}}}{{{L}}}$")
        if lo == 1:
            lines.append(f"Целое число запишем дробью со знаменателем ${L}$: " + ", ".join(conv) + ".")
        else:
            lines.append(f"Общий знаменатель — ${L}$: {why}. Домножаем на дополнительные множители: " + ", ".join(conv) + ".")
    nx, ny = int(x * L), int(y * L)
    tot = nx + ny
    par_ny = f"\\left({ny}\\right)" if ny < 0 else str(ny)
    lines.append(f"${_over(nx, L)}+{_over_w(ny, L)}=\\dfrac{{{nx}+{par_ny}}}{{{L}}}={_over(tot, L)}$.")
    g = math.gcd(abs(tot), L)
    if tot != 0 and g > 1:
        lines.append(f"Сокращаем на ${g}$: ${_over(tot, L)}={T(x + y, 'frac')}$.")
    return lines


def frac_chain(x, op: str, y) -> str:
    """Одна строка вычисления x ± y через общий знаменатель: -\\dfrac{1}{3}-\\dfrac{1}{2}=-\\dfrac{2}{6}-\\dfrac{3}{6}=-\\dfrac{5}{6}."""
    x, y = F(x), F(y)
    L = math.lcm(x.denominator, y.denominator)
    res = x + y if op == "+" else x - y
    head = f"{T(x, 'frac')}{op}{T(y, 'frac', True)}"
    mid = f"{_over(int(x * L), L)}{op}{_over_w(int(y * L), L)}"
    parts = [head]
    if mid != head:
        parts.append(mid)
    unred = int(res * L)
    if math.gcd(abs(unred), L) > 1 and unred != 0:
        parts.append(_over(unred, L))
    parts.append(T(res, "frac"))
    return "=".join(parts)


# ======================================================================
# Генераторы (level: 1 — как в учебнике, 2 — посложнее, 3 — с подвохом)
# ======================================================================


def _nz(rng: random.Random, lo: int, hi: int) -> int:
    while True:
        v = rng.randint(lo, hi)
        if v:
            return v


HINT_ADD = ("Посмотри на знаки. Одинаковые — сложи модули и оставь общий знак. Разные — из большего модуля "
            "вычти меньший и поставь знак того числа, у которого модуль больше.")
HINT_SUB = ("Замени вычитание сложением с противоположным числом: $a-b=a+(-b)$. "
            "Дальше — правила сложения чисел со знаками.")


def _value_task(prompt, terms, st, hint, sol, skills, level, placeholder=None, reduce=False):
    v = c_val(terms)
    extra = dict(expr=c_app(terms), tex=c_tex(terms), verify={"op": "self"})
    if reduce:
        extra["reduce"] = True
    at = ans_tex(v) if st in ("frac", "mixed") else None
    if at:
        extra["answerTex"] = at
    if placeholder:
        extra["placeholder"] = placeholder
    return task(prompt, ans_of(v, st), "expr", hint, sol, skills, **extra)


# ---------- iadd: сумма целых чисел ----------


def g_iadd(rng: random.Random, level: int):
    if level == 1:
        a, b = _nz(rng, -10, 10), _nz(rng, -10, 10)
        if (a > 0 and b > 0) or abs(a) == abs(b) or abs(a + b) > 15:
            return None
    elif level == 2:
        a, b = rng.randint(11, 99) * rng.choice([-1, 1]), rng.randint(11, 99) * rng.choice([-1, 1])
        if (a > 0 and b > 0) or abs(a) == abs(b) or (a % 10 == 0 and b % 10 == 0):
            return None
    else:
        kind = rng.choice(["opp", "swap", "swap", "hundred"])
        if kind == "opp":  # противоположные: сумма 0
            n = rng.randint(13, 99)
            a, b = rng.choice([(-n, n), (n, -n)])
        elif kind == "swap":  # 27 + (−72): цифры те же, модуль больше у второго
            p, q = rng.sample(range(1, 10), 2)
            u, v = 10 * p + q, 10 * q + p
            a, b = rng.choice([(u, -v), (-u, v)])
        elif rng.random() < 0.5:  # через сотню
            a, b = -rng.randint(101, 125), rng.randint(81, 99)
        else:
            a, b = rng.randint(101, 140), -rng.randint(141, 199)
    terms = two(a, "+", b)
    sol = []
    if level == 1:
        sol.append(f"На прямой: стоим в точке ${a}$ и прыгаем на ${abs(b)}$ {'вправо' if b > 0 else 'влево'}.")
    sol += add_lines(a, b)
    if a == -b:
        skills = ["rn-opposite", "rn-add-diff"]
    else:
        skills = ["rn-add-same"] if (a < 0) == (b < 0) else ["rn-add-diff"]
    if level == 1:
        skills.append("rn-number-line")
    return _value_task("Найдите сумму: {expr}", terms, "int", HINT_ADD, sol, skills, level)


# ---------- isub: разность целых чисел ----------


def g_isub(rng: random.Random, level: int):
    if level < 3:
        lo, hi = (1, 9) if level == 1 else (11, 99)

        def m():
            return rng.randint(lo, hi)

        kind = rng.choice(["cross", "negpos", "subneg", "negneg"])
        if kind == "cross":  # 3 − 8: из меньшего вычитаем большее
            a, b = m(), m()
            if a >= b:
                return None
        elif kind == "negpos":  # −2 − 5
            a, b = -m(), m()
        elif kind == "subneg":  # 4 − (−3), −4 − (−3)
            a, b = m() * rng.choice([1, -1]), -m()
        else:  # −6 − (−2)
            a, b = -m(), -m()
        if a == b or (level == 2 and a % 10 == 0 and b % 10 == 0):
            return None
    else:
        kind = rng.choice(["zero", "fromzero", "flip", "flip", "swap"])
        if kind == "zero":  # −n − (−n) = 0
            n = rng.randint(12, 99)
            a, b = -n, -n
        elif kind == "fromzero":  # 0 − (−n) = n
            a, b = 0, -rng.randint(12, 99)
        elif kind == "flip":  # −15 − (−30) = 15: «минус на минус» даёт плюс
            u = rng.randint(11, 60)
            a, b = -u, -rng.randint(u + 5, 99)
        else:  # 19 − 91
            p, q = sorted(rng.sample(range(1, 10), 2))
            a, b = 10 * p + q, 10 * q + p
    terms = two(a, "-", b)
    sol = [sub_line(a, b)] + add_lines(a, -b)
    skills = ["rn-sub", "rn-add-same" if (a < 0) == (-b < 0) else "rn-add-diff"]
    return _value_task("Найдите разность: {expr}", terms, "int", HINT_SUB, sol, skills, level)


# ---------- dec: десятичные дроби ----------


def _rdec(rng: random.Random, max_int: int, places: int) -> F:
    """Положительная десятичная дробь меньше max_int с ровно places знаками после запятой."""
    k = 10**places
    while True:
        n = rng.randint(1, max_int * k - 1)
        if n % 10:
            return F(n, k)


DEC_PH = "десятичной дробью (через запятую)"


def _dec_task(x: F, op: str, y: F, level: int, skills_extra=()):
    terms = two(x, op, y, "dec")
    v = c_val(terms)
    p = max(_places(x), _places(y))
    sol = []
    if _places(x) != _places(y):
        sol.append(f"Чтобы запятая стояла под запятой, допишем нули: ${mod_tex(x, 'dec', p)}$ и ${mod_tex(y, 'dec', p)}$.")
    if op == "-":
        sol.append(sub_line(x, y, "dec"))
        sol += add_lines(x, -y, "dec", p)
        skills = ["rn-decimal", "rn-sub"]
    else:
        sol += add_lines(x, y, "dec", p)
        skills = ["rn-decimal"]
    if v == 0:
        return None
    return _value_task("Вычислите: {expr}", terms, "dec",
                       "Знаки — по тем же правилам, что у целых чисел. Модули складывай или вычитай столбиком: запятая под запятой.",
                       sol, skills + list(skills_extra), level, placeholder=DEC_PH)


def _signs_matter(x: F, op: str, y: F) -> bool:
    """В примере есть работа со знаками: отрицательное число или результат меньше нуля."""
    return x < 0 or y < 0 or (op == "-" and x < y)


def g_dec(rng: random.Random, level: int):
    if level < 3:
        x = _rdec(rng, 9, 1)
        y = _rdec(rng, 9, 1 if level == 1 else 2)
        if level == 2 and rng.random() < 0.5:
            x, y = y, x
        x, y = x * rng.choice([1, -1]), y * rng.choice([1, -1])
        op = rng.choice("+-")
        if not _signs_matter(x, op, y) or abs(x) == abs(y):
            return None
        return _dec_task(x, op, y, level)
    kind = rng.choice(["int", "tiny", "len", "dneg"])
    if kind == "int":  # −7 + 2,35: целое тоже «с запятой» (7,00)
        a, b = F(rng.randint(2, 9)), _rdec(rng, 9, 2)
        if int(b) == a:
            return None
        form = rng.choice(["-a+b", "a-b", "-a-b"])
        if form == "a-b" and b < a:
            return None
        x, op, y = {"-a+b": (-a, "+", b), "a-b": (a, "-", b), "-a-b": (-a, "-", b)}[form]
    elif kind == "tiny":  # 1,2 − 1,25 = −0,05
        u = _rdec(rng, 9, 1)
        w = u + F(rng.randint(1, 9), 100)
        x, op, y = rng.choice([(u, "-", w), (-w, "+", u), (-u, "+", w)])
    elif kind == "len":  # −4,3 + 4,25: 4,3 = 4,30 больше, чем 4,25
        n, t, r = rng.randint(0, 9), rng.randint(2, 9), rng.randint(1, 9)
        u = n + F(t, 10)
        w = n + F(10 * t - r, 100)
        x, op, y = rng.choice([(-u, "+", w), (w, "-", u), (-w, "+", u)])
    else:  # −2 − (−0,75)
        x = -F(rng.randint(1, 9)) if rng.random() < 0.4 else _rdec(rng, 9, 1) * rng.choice([1, -1])
        y = -_rdec(rng, 9, 2)
        op = "-"
    return _dec_task(x, op, y, level)


# ---------- frac: обыкновенные дроби ----------


def _proper(rng: random.Random, den: int) -> F:
    while True:
        n = rng.randint(1, den - 1)
        if math.gcd(n, den) == 1:
            return F(n, den)


FRAC_PH = "дробью через «/», например 2/3"
HINT_FRAC = ("Приведи дроби к общему знаменателю, потом сложи числители по правилам знаков. "
             "Вычитание замени сложением с противоположным. Не забудь сократить ответ.")


def g_frac(rng: random.Random, level: int):
    if level == 1:
        d1 = rng.choice([2, 3, 4, 5])
        d2 = d1 * rng.choice([2, 3] if d1 < 5 else [2])
        x, y = _proper(rng, d1), _proper(rng, d2)
        if rng.random() < 0.5:
            x, y = y, x
    else:
        d1, d2 = rng.sample(range(2, 13), 2)
        L = math.lcm(d1, d2)
        if level == 2 and (d1 % d2 == 0 or d2 % d1 == 0 or L > 36):
            return None
        if level == 3 and L > 48:
            return None
        x, y = _proper(rng, d1), _proper(rng, d2)
    op = rng.choice("+-")
    x, y = x * rng.choice([1, -1]), y * rng.choice([1, -1])
    v = x + y if op == "+" else x - y
    if v == 0 or not _signs_matter(x, op, y) or F(2, 3) == v:
        return None
    if level == 3:
        yy = y if op == "+" else -y
        trap_reduce = v.denominator < math.lcm(x.denominator, yy.denominator)
        trap_dneg = op == "-" and y < 0
        if not (trap_reduce or trap_dneg):
            return None
    terms = two(x, op, y, "frac")
    sol = []
    if op == "-":
        sol.append(sub_line(x, y, "frac"))
    sol += frac_lines(x, y if op == "+" else -y)
    skills = ["rn-common-denom"] + (["rn-sub"] if op == "-" else [])
    return _value_task("Вычислите: {expr}", terms, "frac", HINT_FRAC, sol, skills, level, placeholder=FRAC_PH, reduce=True)


# ---------- mixed: смешанные числа и вперемешку ----------


MIXED_PH = "неправильной дробью, например -7/3"


def _to_frac_lines(nums) -> list[str]:
    """Переводим смешанные числа и десятичные дроби в обыкновенные (модули)."""
    out = []
    for n in nums:
        a = abs(n.v)
        if n.st == "mixed" and a.denominator > 1 and a > 1:
            w, r = divmod(a.numerator, a.denominator)
            out.append(f"${mod_tex(a, 'mixed')}=\\dfrac{{{w}\\cdot {a.denominator}+{r}}}{{{a.denominator}}}=\\dfrac{{{a.numerator}}}{{{a.denominator}}}$")
        elif n.st == "dec" and a.denominator > 1:
            k = 10 ** _places(a)
            raw = f"\\dfrac{{{int(a * k)}}}{{{k}}}"
            simple = mod_tex(a, "frac")
            out.append(f"${mod_tex(a, 'dec')}={raw}" + (f"={simple}$" if raw != simple else "$"))
    return out


def g_mixed(rng: random.Random, level: int):
    def mixed(den, lo=1, hi=4):
        return rng.randint(lo, hi) + _proper(rng, den)

    if level == 1:
        if rng.random() < 0.55:  # −2⅓ + 1⅔: знаменатели одинаковые
            d = rng.choice([2, 3, 4, 5, 6, 8])
            p, q = mixed(d), mixed(d)
            x, op, y = rng.choice([(-p, "+", q), (p, "+", -q), (p, "-", q), (-p, "-", q)])
            if p == q:
                return None
            nums = [Num(x, "mixed"), Num(y, "mixed")]
        else:  # −3½ + 5
            d = rng.choice([2, 3, 4, 5])
            p, n = mixed(d, 1, 5), F(rng.randint(1, 9))
            x, op, y = rng.choice([(-p, "+", n), (p, "-", n), (-n, "+", p), (-p, "-", n)])
            if abs(x + y if op == "+" else x - y) > 8:
                return None
            nums = [Num(x, "mixed" if x.denominator > 1 else "int"), Num(y, "mixed" if y.denominator > 1 else "int")]
    elif level == 2:
        if rng.random() < 0.5:  # −1½ + 2⅓: знаменатели разные
            d1, d2 = rng.sample([2, 3, 4, 5, 6], 2)
            if math.lcm(d1, d2) > 24:
                return None
            p, q = mixed(d1, 1, 3), mixed(d2, 1, 3)
            x, op, y = rng.choice([(-p, "+", q), (p, "-", q), (-p, "-", -q), (p, "+", -q)])
            nums = [Num(x, "mixed"), Num(y, "mixed")]
        else:  # −0,5 + ⅓: десятичная и обыкновенная вперемешку
            dv = rng.choice([F(1, 2), F(1, 4), F(3, 4), F(1, 5), F(2, 5), F(3, 5), F(4, 5), F(6, 5), F(3, 2), F(5, 4)])
            fv = _proper(rng, rng.choice([3, 6, 7, 9, 12]))
            pairs = [(-dv, "+", fv, "dec", "frac"), (fv, "-", dv, "frac", "dec"), (-fv, "-", dv, "frac", "dec"), (dv, "-", fv, "dec", "frac")]
            x, op, y, s1, s2 = rng.choice(pairs)
            if s1 == "dec" and op == "-" and x > y:
                return None
            nums = [Num(x, s1), Num(y, s2)]
    else:
        kind = rng.choice(["whole", "intres", "third", "opp"])
        d = rng.choice([2, 4, 5])
        n = rng.randint(1, 6)
        r = _proper(rng, d)
        if kind == "whole":  # −2⅓ + 2 = −⅓ (минус относится ко всему смешанному числу)
            dd = rng.choice([3, 4, 5, 6, 7, 8])
            r = _proper(rng, dd)
            nums = [Num(-(n + r), "mixed"), Num(n, "int")]
            op = "+"
        elif kind == "intres":  # −1¾ − (−0,75) = −1
            nums = [Num(-(n + r), "mixed"), Num(-r, "dec")]
            op = "-"
        elif kind == "third":  # ⅓ − 0,5: ⅓ не записать конечной десятичной дробью
            fv = _proper(rng, rng.choice([3, 6, 7, 9]))
            dv = rng.choice([F(1, 2), F(1, 4), F(3, 4), F(1, 5), F(2, 5), F(3, 5), F(4, 5)])
            if fv > dv:
                return None
            nums = [Num(fv, "frac"), Num(dv, "dec")]
            op = "-"
        else:  # −3⅕ + 3,2 = 0
            nums = [Num(-(n + r), "mixed"), Num(n + r, "dec")]
            op = "+"
        x, y = nums[0].v, nums[1].v
    terms = [("", nums[0]), (op, nums[1])]
    v = c_val(terms)
    if v == F(-7, 3) or (level < 3 and v == 0):
        return None
    xs, ys = nums[0].v, nums[1].v if op == "+" else -nums[1].v
    conv = _to_frac_lines(nums)
    sol = []
    if conv:
        sol.append("Переводим в обыкновенные дроби: " + ", ".join(conv) + ".")
    sol.append(f"Получаем: ${c_tex(terms)}={T(xs, 'frac')}+{T(ys, 'frac', True)}$.")
    sol += frac_lines(xs, ys)
    skills = ["rn-mixed", "rn-common-denom"] + (["rn-decimal"] if any(n.st == "dec" for n in nums) else []) + (["rn-sub"] if op == "-" else [])
    hint = ("Переведи смешанные числа и десятичные дроби в обыкновенные. Минус перед смешанным числом относится ко всему числу: "
            "$-2\\frac{1}{3}=-\\frac{7}{3}$. Потом общий знаменатель и правила знаков.")
    return _value_task("Вычислите: {expr}", terms, "frac", hint, sol, skills, level, placeholder=MIXED_PH, reduce=True)


# ---------- chain: цепочки со скобками ----------


def _flat(terms, sign: int = 1) -> list[F]:
    """Слагаемые после раскрытия скобок (со знаками)."""
    out = []
    for op, it in terms:
        s = -sign if op == "-" else sign
        if isinstance(it, Num):
            out.append(s * it.v)
        else:
            assert it.kind == "par"
            out += _flat(it.terms, s)
    return out


def g_chain(rng: random.Random, level: int):
    st = "int"
    if level == 1:  # −7 + 12 − 8: слева направо
        a = _nz(rng, -15, 15)
        b, c = rng.randint(1, 15), rng.randint(1, 15)
        o1, o2 = rng.choice("+-"), rng.choice("+-")
        terms = [("", Num(a)), (o1, Num(b)), (o2, Num(c))]
        first = a + b if o1 == "+" else a - b
        v = c_val(terms)
        if a > 0 and first >= 0 and v >= 0:
            return None
        sol = [f"Считаем слева направо. Сначала ${a}{o1}{b}={first}$.", f"Потом ${first}{o2}{c}={v}$."]
        return _value_task("Вычислите: {expr}", terms, st, "Считай слева направо или сложи отдельно все «плюсы» и все «минусы».",
                           sol, ["rn-chain", "rn-add-diff"], level)
    if level == 2:
        kind = rng.choice(["minus_br", "minus_br", "four"])
        if kind == "minus_br":  # −12 − (5 − 8) + 4
            a, b, c, d = _nz(rng, -20, 20), rng.randint(2, 15), rng.randint(2, 15), _nz(rng, -12, 12)
            inner = [("", Num(b)), (rng.choice("+-"), Num(c))]
            terms = [("", Num(a)), ("-", Grp(inner))]
            if rng.random() < 0.6:
                terms.append(("+" if d > 0 else "-", Num(abs(d))))
        else:  # −3 + 8 − (−6) − 11
            terms = [("", Num(-rng.randint(1, 15))), ("+", Num(rng.randint(2, 15))), ("-", Num(-rng.randint(2, 15))), ("-", Num(rng.randint(2, 20)))]
            rng.shuffle(terms[1:])
            terms = [terms[0]] + terms[1:]
    else:
        kind = rng.choice(["two_br", "cancel", "negbr", "dec"])
        if kind == "two_br":  # −(7 − 12) − (−3 + 8)
            a, b, c, d = rng.sample(range(2, 16), 4)
            terms = [("-", Grp([("", Num(a)), ("-", Num(b))])), ("-", Grp([("", Num(-c)), ("+", Num(d))]))]
        elif kind == "cancel":  # 24 − (13 + 24) − (−13) = 0: удобно сгруппировать
            a, b = rng.sample(range(11, 60), 2)
            terms = [("", Num(a)), ("-", Grp([("", Num(b)), ("+", Num(a))])), ("-", Num(-b))]
        elif kind == "negbr":  # −(−5 − 3) − 8
            a, b = rng.randint(2, 15), rng.randint(2, 15)
            c = a + b + rng.randint(-3, 3)
            terms = [("-", Grp([("", Num(-a)), ("-", Num(b))])), ("-", Num(c))]
        else:  # −2,5 + (1,5 − 4) − (−3)
            st = "dec"
            a, b = _rdec(rng, 6, 1), _rdec(rng, 6, 1)
            c, d = F(rng.randint(2, 9)), F(rng.randint(1, 9))
            terms = [("", Num(-a, st)), ("+", Grp([("", Num(b, st)), ("-", Num(c, st))])), ("-", Num(-d, st))]
    v = c_val(terms)
    flat = _flat(terms)
    sol = []
    tex0 = c_tex(terms)
    flat_tex = sum_tex(flat, st)
    if any(isinstance(it, Grp) for _, it in terms):
        sol.append(f"Раскрываем скобки: минус перед скобкой меняет знак каждого слагаемого внутри, плюс — не меняет: ${tex0}={flat_tex}$.")
    else:
        sol.append(f"Вычесть отрицательное — то же, что прибавить положительное: ${tex0}={flat_tex}$.")
    pos, neg = [f for f in flat if f > 0], [f for f in flat if f < 0]
    P, N = sum(pos, F(0)), sum(neg, F(0))
    if pos and neg:
        def part(vals):
            return f"${sum_tex(vals, st)}={T(sum(vals, F(0)), st)}$" if len(vals) > 1 else f"${T(vals[0], st)}$"
        sol.append(f"Складываем отдельно положительные: {part(pos)}, и отрицательные: {part(neg)}.")
        sol.append(f"${T(P, st)}+{T(N, st, True)}={T(v, st)}$.")
    else:
        sol.append(f"Все слагаемые одного знака: ${flat_tex}={T(v, st)}$.")
    skills = ["rn-chain", "rn-brackets"] if any(isinstance(it, Grp) for _, it in terms) else ["rn-chain", "rn-sub"]
    if st == "dec":
        skills.append("rn-decimal")
    hint = ("Раскрой скобки: минус перед скобкой меняет знаки всех слагаемых внутри. "
            "Потом сложи отдельно все положительные и все отрицательные числа.")
    return _value_task("Вычислите: {expr}", terms, st, hint, sol, skills, level,
                       placeholder=DEC_PH if st == "dec" else None)


# ---------- sign: какой знак у результата ----------


SIGN_OPTS = ["больше нуля (знак «+»)", "меньше нуля (знак «−»)", "равно нулю"]


def _sign_index(v: F) -> int:
    return 0 if v > 0 else (1 if v < 0 else 2)


def _mod_cmp(x: F, y: F, st: str) -> str:
    """Сравнение модулей для решения: |x| и |y| в удобной записи."""
    ax, ay = abs(x), abs(y)
    rel = ">" if ax > ay else ("<" if ax < ay else "=")
    if st == "dec":
        p = max(_places(x), _places(y))
        return f"${mod_tex(ax, 'dec', p)}{rel}{mod_tex(ay, 'dec', p)}$"
    if st == "frac" and ax.denominator != ay.denominator:
        L = math.lcm(ax.denominator, ay.denominator)
        return f"${mod_tex(ax, 'frac')}={_over(int(ax * L), L)}{rel}{_over(int(ay * L), L)}={mod_tex(ay, 'frac')}$"
    return f"${mod_tex(ax, st)}{rel}{mod_tex(ay, st)}$"


def g_sign(rng: random.Random, level: int):
    if level == 1:
        x, y = F(_nz(rng, -30, 30)), F(_nz(rng, -30, 30))
        op = "+" if rng.random() < 0.75 else "-"
        if abs(x) == abs(y) or not _signs_matter(x, op, y) or (x > 0 and y > 0):
            return None
        terms, st = two(x, op, y), "int"
    elif level == 2:
        if rng.random() < 0.5:
            st = "dec"
            x = _rdec(rng, 9, rng.choice([1, 2]))
            y = x + F(rng.randint(-60, 60), 100)
            if y <= 0 or y == x or not _is_dec(y):
                return None
        else:
            st = "frac"
            d1, d2 = rng.sample(range(2, 10), 2)
            x, y = _proper(rng, d1), _proper(rng, d2)
            if x == y or abs(x - y) > F(1, 4):
                return None
        op = rng.choice("+-")
        x, y = x * rng.choice([1, -1]), y * rng.choice([1, -1])
        if (op == "+" and (x > 0) == (y > 0)) or (op == "-" and (x > 0) != (y > 0)):
            return None  # нужны «разные знаки» по сути, иначе знак виден сразу
        terms = two(x, op, y, st)
    else:
        st = "int"
        kind = rng.choice(["negabs", "absabs", "absdiff", "declen"])
        if kind == "negabs":  # −|−7| + 5
            a, b = rng.randint(2, 20), rng.randint(2, 20)
            terms = [("-", Grp([("", Num(-a))], "abs")), ("+", Num(b))]
        elif kind == "absabs":  # |−3| − |−5|
            a, b = rng.randint(2, 20), rng.randint(2, 20)
            terms = [("", Grp([("", Num(-a))], "abs")), ("-", Grp([("", Num(b * rng.choice([1, -1])))], "abs"))]
        elif kind == "absdiff":  # −|2 − 9| + 7
            a, b = rng.sample(range(1, 16), 2)
            c = abs(a - b) + rng.choice([-2, -1, 0, 0, 1, 2])
            if c <= 0:
                return None
            terms = [("-", Grp([("", Num(a)), ("-", Num(b))], "abs")), ("+", Num(c))]
        else:  # |−4,25| − 4,3: 4,3 = 4,30 больше
            st = "dec"
            n, t, r = rng.randint(1, 9), rng.randint(2, 9), rng.randint(1, 9)
            u, w = n + F(t, 10), n + F(10 * t - r, 100)
            terms = rng.choice([
                [("", Grp([("", Num(-w, st))], "abs")), ("-", Num(u, st))],
                [("-", Grp([("", Num(-u, st))], "abs")), ("+", Num(w, st))],
            ])
    v = c_val(terms)
    sol = []
    if level == 3:
        mods = []
        for op_, it in terms:
            if isinstance(it, Grp):
                inner = c_tex(it.terms)
                mods.append(f"$\\left|{inner}\\right|={mod_tex(c_val(it.terms), st)}$")
        sol.append("Сначала модули: " + ", ".join(mods) + ".")
        flat = []
        for op_, it in terms:
            val = abs(c_val(it.terms)) if isinstance(it, Grp) else it.v
            flat.append(-val if op_ == "-" else val)
        x, y = flat
        sol.append(f"Получаем ${c_tex(terms)}={sum_tex(flat, st)}$.")
    else:
        x, y = (terms[0][1].v, terms[1][1].v if terms[1][0] == "+" else -terms[1][1].v)
        if terms[1][0] == "-":
            sol.append(sub_line(terms[0][1].v, terms[1][1].v, st))
    if v == 0:
        sol.append(f"Числа ${T(x, st)}$ и ${T(y, st)}$ противоположные: модули равны, сумма равна нулю.")
    elif (x > 0) == (y > 0):
        sol.append(f"Оба слагаемых {'положительные' if x > 0 else 'отрицательные'}, значит, и сумма {'положительная' if x > 0 else 'отрицательная'}.")
    else:
        big = x if abs(x) > abs(y) else y
        sol.append(f"Знаки разные — у суммы знак того числа, у которого модуль больше. Сравним модули: {_mod_cmp(x, y, st)}.")
        sol.append(f"Больше модуль у ${T(big, st)}$, поэтому результат {'положительный' if big > 0 else 'отрицательный'}.")
    rel = ">" if v > 0 else ("<" if v < 0 else "=")
    sol.append(f"Проверка вычислением: ${c_tex(terms)}={T(v, st)}{rel}0$." if v != 0 else f"Проверка вычислением: ${c_tex(terms)}=0$.")
    skills = ["rn-add-diff"] + (["rn-abs"] if level == 3 else []) + (["rn-sub"] if any(o == "-" for o, _ in terms[1:]) else [])
    return task("Не вычисляя до конца, определите знак результата: {expr}", str(_sign_index(v)), "choice",
                "Сравни модули. Если знаки разные, у суммы знак того числа, у которого модуль больше. "
                "Вычитание сначала замени сложением с противоположным.",
                sol, skills, options=list(SIGN_OPTS), expr=c_app(terms), tex=c_tex(terms))


# ---------- gap: пропущенное число ----------


BOX = "\\boxed{?}"


def g_gap(rng: random.Random, level: int):
    st = "int"
    if level == 1:
        X, k = _nz(rng, -12, 12), _nz(rng, -12, 12)
        form = rng.choice(["a+?", "?+b", "a-?", "?-b"])
    elif level == 2:
        if rng.random() < 0.6:
            X, k = _nz(rng, -60, 60), _nz(rng, -60, 60)
            if abs(X) < 11 and abs(k) < 11:
                return None
        else:
            st = "dec"
            X, k = _rdec(rng, 9, 1) * rng.choice([1, -1]), _rdec(rng, 9, 1) * rng.choice([1, -1])
        form = rng.choice(["a+?", "?+b", "a-?", "?-b"])
    else:
        kind = rng.choice(["minusbox", "dneg", "frac", "frac"])
        if kind == "frac":
            st = "frac"
            X = _proper(rng, rng.choice([2, 3, 4, 5, 6])) * rng.choice([1, -1])
            k = _proper(rng, rng.choice([2, 3, 4, 6, 8])) * rng.choice([1, -1])
            if X.denominator == k.denominator:
                return None
            form = rng.choice(["a+?", "?+b", "a-?", "?-b"])
        elif kind == "minusbox":  # −? + 5 = 9
            X, k = _nz(rng, -25, 25), _nz(rng, -25, 25)
            form = "-?+b"
        else:  # ? − (−8) = −3
            X, k = _nz(rng, -25, 25), -rng.randint(2, 25)
            form = "?-b"
    X, k = F(X), F(k)
    if form == "a+?":
        c = k + X
        eq, lhs = f"{T(k, st)}+{BOX}", f"{A(k, st)}+x"
    elif form == "?+b":
        c = X + k
        eq, lhs = f"{BOX}+{T(k, st, True)}", f"x+{A(k, st, True)}"
    elif form == "a-?":
        c = k - X
        eq, lhs = f"{T(k, st)}-{BOX}", f"{A(k, st)}-x"
    elif form == "?-b":
        c = X - k
        eq, lhs = f"{BOX}-{T(k, st, True)}", f"x-{A(k, st, True)}"
    else:
        c = -X + k
        eq, lhs = f"-{BOX}+{T(k, st, True)}", f"-x+{A(k, st, True)}"
    if c == 0 or X == k or not (X < 0 or k < 0 or c < 0):
        return None
    if st == "frac" and (c.denominator > 24 or F(2, 3) == X):
        return None
    eq_tex = f"{eq}={T(c, st)}"

    def calc(p, op, q):
        """Строка вычисления p op q (с правилами знаков) для решения."""
        if st == "frac":
            return f"${frac_chain(p, op, q)}$"
        r = p + q if op == "+" else p - q
        head = f"{T(p, st)}{op}{T(q, st, True)}"
        if op == "-" and q < 0:
            return f"${head}={T(p, st)}+{T(-q, st)}={T(r, st)}$"
        return f"${head}={T(r, st)}$"

    if form in ("a+?", "?+b"):
        sol = [f"Неизвестное слагаемое: из суммы вычитаем известное слагаемое: {calc(c, '-', k)}."]
    elif form == "a-?":
        sol = [f"Неизвестное вычитаемое: из уменьшаемого вычитаем разность: {calc(k, '-', c)}."]
    elif form == "?-b":
        sol = [f"Неизвестное уменьшаемое: к разности прибавляем вычитаемое: {calc(c, '+', k)}."]
    else:
        sol = [f"Сначала найдём слагаемое $-{BOX}$: из суммы вычитаем известное слагаемое: {calc(c, '-', k)}.",
               f"Число в окошке — противоположное: ${T(-X, st)}$ меняем на ${T(X, st)}$."]
    check = eq_tex.replace(BOX, T(X, st, wrap=not eq.startswith(BOX)), 1)
    sol.append(f"Проверка: ${check}$ ✓")
    hint = {
        "a+?": "Неизвестное слагаемое = сумма минус известное слагаемое.",
        "?+b": "Неизвестное слагаемое = сумма минус известное слагаемое.",
        "a-?": "Неизвестное вычитаемое = уменьшаемое минус разность.",
        "?-b": "Неизвестное уменьшаемое = разность плюс вычитаемое.",
        "-?+b": "Сначала найди, чему равно $-\\square$ (это неизвестное слагаемое), а потом возьми противоположное число.",
    }[form]
    extra = dict(gap={"lhs": lhs, "rhs": A(c, st)})
    if st == "frac":
        extra.update(reduce=True, placeholder=FRAC_PH, answerTex=ans_tex(X))
    elif st == "dec":
        extra.update(placeholder=DEC_PH)
    skills = ["rn-missing", "rn-sub"] + (["rn-decimal"] if st == "dec" else []) + (["rn-common-denom"] if st == "frac" else [])
    prompt = f"Какое число нужно вписать в окошко, чтобы получилось верное равенство? $\\displaystyle {eq_tex}$"
    return task(prompt, ans_of(X, st), "expr", hint, sol, skills, **extra)


# ---------- cmp: что больше ----------


def _cmp_task(ta, tb, ea, eb, sol, skills, exprs: bool):
    """Варианты в одном и том же порядке «<», «=», «>»: форма не выдаёт ответ."""
    va, vb = _sym_value(ea), _sym_value(eb)
    idx = 0 if va < vb else (1 if va == vb else 2)
    what = "значения выражений" if exprs else "числа"
    return task(f"Сравните {what} ${ta}$ и ${tb}$.", str(idx), "choice",
                "На прямой больше то число, которое правее. Из двух отрицательных больше то, у которого модуль меньше (оно ближе к нулю). "
                "Если есть действия, сначала вычисли.",
                sol, skills, options=[f"${ta}<{tb}$", f"${ta}={tb}$", f"${ta}>{tb}$"], expr=ea, expr2=eb,
                cmp={"a": ta, "b": tb})


def _rel(a: F, b: F) -> str:
    return "<" if a < b else ("=" if a == b else ">")


def _neg_rule(a: F, b: F) -> str:
    if a < 0 and b < 0:
        return "Оба числа отрицательные: больше то, у которого модуль меньше — оно ближе к нулю и правее на прямой."
    if a == 0 or b == 0:
        return "Ноль больше любого отрицательного числа и меньше любого положительного."
    if (a > 0) != (b > 0):
        return "Любое положительное число больше любого отрицательного."
    return "Оба числа положительные: больше то, у которого модуль больше."


def g_cmp(rng: random.Random, level: int):
    if level == 1:
        kind = rng.choice(["negint", "negdec", "negfrac", "zero"])
        if kind == "negint":
            a, b = -F(rng.randint(1, 20)), -F(rng.randint(1, 20))
            st = "int"
        elif kind == "negdec":
            a, b = -_rdec(rng, 9, 1), -_rdec(rng, 9, 1)
            st = "dec"
        elif kind == "negfrac":
            d = rng.choice([5, 7, 9, 11])
            a, b = -_proper(rng, d), -_proper(rng, d)
            st = "frac"
        else:
            a = -_rdec(rng, 5, 1)
            b = rng.choice([F(0), F(rng.randint(1, 9))])
            st = "dec"
        if a == b:
            return None
        if rng.random() < 0.5:
            a, b = b, a
        ta, tb = T(a, st), T(b, st)
        sol = [_neg_rule(a, b)]
        if a < 0 and b < 0:
            sol.append(f"Модули: {_mod_cmp(a, b, st)}.")
        sol.append(f"Значит, ${ta}{_rel(a, b)}{tb}$.")
        return _cmp_task(ta, tb, A(a, st), A(b, st), sol, ["rn-compare"], False)
    if level == 2:
        kind = rng.choice(["expr_num", "frac_dec", "same_num", "two_expr"])
        if kind == "expr_num":  # −7 + 4 и −2
            x, y = -F(rng.randint(3, 15)), F(rng.randint(1, 12))
            s = x + y
            c = s + rng.choice([-2, -1, 1, 2])
            ta, tb = c_tex(two(x, "+", y)), T(c)
            ea, eb = c_app(two(x, "+", y)), A(c)
            sol = [f"Вычислим: ${ta}={T(s)}$.", _neg_rule(s, c), f"${T(s)}{_rel(s, c)}{T(c)}$, значит, ${ta}{_rel(s, c)}{tb}$."]
            return _cmp_task(ta, tb, ea, eb, sol, ["rn-compare", "rn-add-diff"], True)
        if kind == "frac_dec":  # −¾ и −0,7
            fv = rng.choice([F(1, 4), F(3, 4), F(1, 5), F(2, 5), F(3, 5), F(4, 5), F(1, 2), F(1, 8), F(3, 8)])
            dv = fv + F(rng.choice([-1, 1]) * rng.randint(1, 9), 100 if rng.random() < 0.5 else 10)
            if dv <= 0 or dv >= 1:
                return None
            a, b = -fv, -dv
            if rng.random() < 0.5:
                a, b = b, a
            sa = "frac" if a == -fv else "dec"
            sb = "dec" if sa == "frac" else "frac"
            ta, tb = T(a, sa), T(b, sb)
            sol = [f"Запишем дробь десятичной: ${mod_tex(fv, 'frac')}={mod_tex(fv, 'dec')}$.",
                   f"Модули: {_mod_cmp(a, b, 'dec')}.", _neg_rule(a, b), f"Значит, ${ta}{_rel(a, b)}{tb}$."]
            return _cmp_task(ta, tb, A(a, sa), A(b, sb), sol, ["rn-compare", "rn-decimal"], False)
        if kind == "same_num":  # −2/5 и −2/3
            n = rng.randint(1, 4)
            d1, d2 = rng.sample([d for d in range(n + 1, 13) if math.gcd(n, d) == 1], 2)
            a, b = -F(n, d1), -F(n, d2)
            ta, tb = T(a, "frac"), T(b, "frac")
            sol = [f"Числители одинаковые: у какой дроби знаменатель больше, у той кусочки мельче, и модуль меньше: {_mod_cmp(a, b, 'frac')}.",
                   _neg_rule(a, b), f"Значит, ${ta}{_rel(a, b)}{tb}$."]
            return _cmp_task(ta, tb, A(a, "frac"), A(b, "frac"), sol, ["rn-compare"], False)
        # два выражения: −3 − 5 и −3 + (−5)
        x, y = -F(rng.randint(2, 15)), F(rng.randint(2, 15))
        e1, e2 = two(x, "-", y), rng.choice([two(x, "+", -y), two(x, "+", y), two(-x, "-", y)])
        v1, v2 = c_val(e1), c_val(e2)
        ta, tb = c_tex(e1), c_tex(e2)
        sol = [f"Вычислим: ${ta}={T(v1)}$ и ${tb}={T(v2)}$.", _neg_rule(v1, v2) if v1 != v2 else "Значения одинаковые.",
               f"${T(v1)}{_rel(v1, v2)}{T(v2)}$, значит, ${ta}{_rel(v1, v2)}{tb}$."]
        return _cmp_task(ta, tb, c_app(e1), c_app(e2), sol, ["rn-compare", "rn-sub"], True)
    kind = rng.choice(["approx", "mixed_dec", "eq", "absx", "neg_abs", "len"])
    if kind in ("approx", "mixed_dec", "eq", "len"):
        if kind == "approx":  # −2/3 и −0,67: 2/3 = 0,666…
            fv = rng.choice([F(1, 3), F(2, 3), F(1, 6), F(5, 6), F(1, 7), F(4, 9), F(5, 9), F(7, 9), F(1, 9), F(2, 7)])
            k = 100
            dv = F(round(fv * k), k)
            if rng.random() < 0.4:
                dv = F(int(fv * 10), 10) if rng.random() < 0.5 else F(int(fv * 10) + 1, 10)
            a, b, sa, sb = -fv, -dv, "frac", "dec"
        elif kind == "mixed_dec":  # −1¼ и −1,2
            n = rng.randint(1, 5)
            fv = n + rng.choice([F(1, 4), F(3, 4), F(1, 5), F(2, 5), F(1, 2), F(1, 8)])
            dv = fv + F(rng.choice([-1, 1]) * rng.randint(1, 9), rng.choice([10, 100]))
            if dv <= n or dv >= n + 1 or not _is_dec(dv):
                return None
            a, b, sa, sb = -fv, -dv, "mixed", "dec"
        elif kind == "eq":  # −3/5 и −0,6
            fv = rng.choice([F(3, 5), F(1, 4), F(3, 4), F(2, 5), F(7, 20), F(1, 8), F(4, 5), F(9, 20)])
            a, b, sa, sb = -fv, -fv, "frac", "dec"
        else:  # −4,25 и −4,3
            n, t, r = rng.randint(0, 9), rng.randint(2, 9), rng.randint(1, 9)
            a, b, sa, sb = -(n + F(t, 10)), -(n + F(10 * t - r, 100)), "dec", "dec"
        if rng.random() < 0.5:
            a, b, sa, sb = b, a, sb, sa
        ta, tb = T(a, sa), T(b, sb)
        sol = []
        if "frac" in (sa, sb) or "mixed" in (sa, sb):
            fr_v = a if sa != "dec" else b
            dc_v = b if sa != "dec" else a
            L = math.lcm(abs(fr_v).denominator, abs(dc_v).denominator)
            sol.append(f"Приведём модули к общему знаменателю ${L}$: ${mod_tex(fr_v, 'mixed' if 'mixed' in (sa, sb) else 'frac')}={_over(int(abs(fr_v) * L), L)}$ "
                       f"и ${mod_tex(dc_v, 'dec')}={_over(int(abs(dc_v) * L), L)}$.")
        else:
            p = max(_places(a), _places(b))
            sol.append(f"Допишем нули, чтобы знаков после запятой было поровну: ${mod_tex(a, 'dec', p)}$ и ${mod_tex(b, 'dec', p)}$.")
        sol.append(_neg_rule(a, b) if a != b else "Модули равны — значит, и числа равны.")
        sol.append(f"Значит, ${ta}{_rel(a, b)}{tb}$.")
        return _cmp_task(ta, tb, A(a, sa), A(b, sb), sol, ["rn-compare", "rn-decimal"], False)
    if kind == "absx":  # |−8| − |3| и |−8 − 3|
        a, b = rng.randint(2, 15), rng.randint(2, 15)
        sa_ = rng.choice([1, -1])
        e1 = [("", Grp([("", Num(-a))], "abs")), ("-", Grp([("", Num(b * sa_))], "abs"))]
        e2 = [("", Grp([("", Num(-a)), ("-", Num(b))], "abs"))]
        if rng.random() < 0.5:
            e1, e2 = e2, e1
    else:  # −|−6| и −(−6)
        a = rng.randint(2, 20)
        e1 = [("-", Grp([("", Num(-a))], "abs"))]
        e2 = [("-", Grp([("", Num(-a))]))]
        if rng.random() < 0.5:
            e1, e2 = e2, e1
    v1, v2 = c_val(e1), c_val(e2)
    ta, tb = c_tex(e1), c_tex(e2)
    sol = [f"Вычислим: ${ta}={T(v1)}$ и ${tb}={T(v2)}$.", _neg_rule(v1, v2) if v1 != v2 else "Значения одинаковые.",
           f"${T(v1)}{_rel(v1, v2)}{T(v2)}$, значит, ${ta}{_rel(v1, v2)}{tb}$."]
    return _cmp_task(ta, tb, c_app(e1), c_app(e2), sol, ["rn-compare", "rn-abs"], True)


# ---------- ⭐ abs: модули и расстояния ----------


def _x_minus(a) -> str:
    """x − a в записи для ребёнка: x-3, x+4, x-1{,}5."""
    a = F(a)
    if a == 0:
        return "x"
    st = "dec" if a.denominator > 1 else "int"
    return f"x-{mod_tex(a, st)}" if a > 0 else f"x+{mod_tex(a, st)}"


def _absx(a) -> str:
    return f"\\left|{_x_minus(a)}\\right|"


def _pt(a) -> str:
    a = F(a)
    return T(a, "dec" if a.denominator > 1 else "int")


ROOTS_RES = "Если корней несколько, запишите их через «;», если корней нет — напишите «нет»."


def g_abs(rng: random.Random, level: int):
    kind = rng.choice(["cnt", "cnt", "sum", "min2", "min3", "arg3", "eqcnt", "roots", "mid"])
    dist_hint = "Модуль разности $|x-a|$ — это расстояние от точки $x$ до точки $a$ на числовой прямой. Нарисуй прямую и отметь точки."
    check = {"kind": kind}
    if kind == "cnt":
        variant = rng.choice(["int", "int", "half", "zero"])
        strict = rng.random() < 0.6
        rel = "<" if strict else "\\le"
        if variant == "zero":  # |x| < 4,5
            a, d = F(0), F(rng.randint(2, 9)) + F(1, 2)
        else:
            a = F(_nz(rng, -9, 9)) + (F(1, 2) * rng.choice([1, -1]) if variant == "half" else 0)
            d = F(rng.randint(2, 9))
        lo, hi = a - d, a + d
        good = [x for x in range(math.floor(lo) - 1, math.ceil(hi) + 2) if (lo < x < hi if strict else lo <= x <= hi)]
        prompt = f"Сколько целых чисел $x$ удовлетворяют неравенству ${_absx(a)}{rel}{_pt(d)}$?"
        ends = "концы не подходят (неравенство строгое)" if strict else "концы подходят, если они целые (неравенство нестрогое)"
        sol = [f"${_absx(a)}$ — расстояние от $x$ до ${_pt(a)}$. Нужны точки на расстоянии {'меньше' if strict else 'не больше'} ${_pt(d)}$ от ${_pt(a)}$.",
               f"Это отрезок от ${_pt(a)}-{_pt(d)}={_pt(lo)}$ до ${_pt(a)}+{_pt(d)}={_pt(hi)}$, {ends}.",
               f"Целые числа: от ${good[0]}$ до ${good[-1]}$. Их ${good[-1]}-{T(good[0], wrap=True)}+1={len(good)}$."]
        return task(prompt, str(len(good)), "expr", dist_hint, sol, ["rn-distance", "rn-abs"], absCheck=check)
    if kind == "sum":
        a, d = _nz(rng, -9, 9), rng.randint(2, 7)
        strict = rng.random() < 0.5
        lo, hi = (a - d + 1, a + d - 1) if strict else (a - d, a + d)
        cnt = hi - lo + 1
        prompt = f"Найдите сумму всех целых чисел $x$, для которых ${_absx(a)}{'<' if strict else '\\le'}{d}$."
        sol = [f"${_absx(a)}$ — расстояние от $x$ до ${a}$. Подходят целые числа от ${lo}$ до ${hi}$ — всего ${hi}-{T(lo, wrap=True)}+1={cnt}$ чисел.",
               f"Они стоят симметрично относительно ${a}$: числа ${lo}$ и ${hi}$, ${lo + 1}$ и ${hi - 1}$ и так далее в паре дают ${lo}+{T(hi, wrap=True)}={2 * a}$.",
               f"Значит, сумма равна ${cnt}\\cdot {T(a, wrap=True)}={cnt * a}$."]
        return task(prompt, str(cnt * a), "expr", dist_hint + " Числа, симметричные относительно точки, удобно складывать парами.",
                    sol, ["rn-distance", "rn-abs"], absCheck=check)
    if kind == "min2":
        a, b = rng.sample(range(-12, 13), 2)
        lo, hi = sorted((a, b))
        prompt = f"Найдите наименьшее значение выражения ${_absx(a)}+{_absx(b)}$."
        sol = [f"${_absx(a)}$ — расстояние от $x$ до ${a}$, а ${_absx(b)}$ — расстояние от $x$ до ${b}$.",
               f"Если $x$ лежит между ${lo}$ и ${hi}$, сумма двух расстояний — это ровно длина отрезка: ${hi}-{T(lo, wrap=True)}={hi - lo}$.",
               "Если $x$ снаружи отрезка, путь получается длиннее.",
               f"Наименьшее значение: ${hi - lo}$."]
        return task(prompt, str(hi - lo), "expr", dist_hint, sol, ["rn-distance", "rn-abs"], absCheck=check)
    if kind in ("min3", "arg3"):
        p, q, r = sorted(rng.sample(range(-10, 11), 3))
        pts = [p, q, r]
        rng.shuffle(pts)
        expr = "+".join(_absx(t) for t in pts)
        sol = [f"Это сумма расстояний от $x$ до трёх точек: ${p}$, ${q}$ и ${r}$.",
               f"Расстояния до крайних точек ${p}$ и ${r}$ вместе не меньше длины отрезка: ${r}-{T(p, wrap=True)}={r - p}$ (равны ей, когда $x$ между ними).",
               f"Расстояние до средней точки ${q}$ наименьшее, когда $x={q}$: тогда оно равно нулю."]
        if kind == "min3":
            sol.append(f"Наименьшее значение: ${r - p}+0={r - p}$ (при $x={q}$).")
            return task(f"Найдите наименьшее значение выражения ${expr}$.", str(r - p), "expr", dist_hint, sol,
                        ["rn-distance", "rn-abs"], absCheck=check)
        sol.append(f"Значит, наименьшее значение получается при $x={q}$ (оно равно ${r - p}$).")
        return task(f"При каком значении $x$ выражение ${expr}$ принимает наименьшее значение?", str(q), "expr", dist_hint, sol,
                    ["rn-distance", "rn-abs"], absCheck=check)
    if kind == "eqcnt":
        a, b = rng.sample(range(-9, 10), 2)
        lo, hi = sorted((a, b))
        prompt = f"Сколько целых решений имеет уравнение ${_absx(a)}+{_absx(b)}={hi - lo}$?"
        sol = [f"Слева — сумма расстояний от $x$ до точек ${a}$ и ${b}$, а справа ${hi - lo}$ — это ровно длина отрезка: ${hi}-{T(lo, wrap=True)}={hi - lo}$.",
               f"Сумма расстояний равна длине отрезка, только когда $x$ лежит на этом отрезке: от ${lo}$ до ${hi}$ (концы подходят).",
               f"Целых точек на нём: ${hi}-{T(lo, wrap=True)}+1={hi - lo + 1}$."]
        return task(prompt, str(hi - lo + 1), "expr", dist_hint, sol, ["rn-distance", "rn-abs"], absCheck=check)
    if kind == "roots":
        a = _nz(rng, -9, 9)
        d = rng.randint(1, 9) if rng.random() < 0.8 else -rng.randint(1, 9)
        prompt = f"Решите уравнение ${_absx(a)}={d}$. {ROOTS_RES}"
        if d < 0:
            sol = [f"Модуль — это расстояние, он не бывает отрицательным: ${_absx(a)}\\ge 0$ при любом $x$.",
                   f"А справа ${d}<0$. Значит, корней нет."]
            return task(prompt, "нет", "roots", dist_hint, sol, ["rn-abs"], absCheck=check)
        r1, r2 = a - d, a + d
        sol = [f"${_absx(a)}$ — расстояние от $x$ до ${a}$. Нужны точки на расстоянии ${d}$ от ${a}$.",
               f"Таких точек две: левее на ${d}$ и правее на ${d}$: ${a}-{d}={r1}$ и ${a}+{d}={r2}$.",
               f"Проверка: $\\left|{r1}{'-' if a > 0 else '+'}{abs(a)}\\right|={d}$ и $\\left|{r2}{'-' if a > 0 else '+'}{abs(a)}\\right|={d}$ ✓"]
        return task(prompt, f"{r1}; {r2}", "roots", dist_hint, sol, ["rn-distance", "rn-abs"], absCheck=check)
    # mid: середина отрезка
    a, b = rng.sample(range(-15, 16), 2)
    if abs(a - b) < 3:
        return None
    lo, hi = sorted((a, b))
    m = F(a + b, 2)
    L = hi - lo
    prompt = (f"Концы отрезка на координатной прямой — точки ${a}$ и ${b}$. "
              f"Найдите координату середины отрезка (точки, равноудалённой от его концов).")
    st = "dec" if m.denominator > 1 else "int"
    sol = [f"Длина отрезка: ${hi}-{T(lo, wrap=True)}={L}$.",
           f"Половина длины: ${L}:2={mod_tex(F(L, 2), st)}$.",
           f"От левого конца отступаем вправо на половину: ${lo}+{mod_tex(F(L, 2), st)}={T(m, st)}$."]
    extra = {"placeholder": DEC_PH} if st == "dec" else {}
    return task(prompt, ans_of(m, st), "expr", dist_hint + " Середина — точка, до которой от обоих концов одинаковое расстояние.",
                sol, ["rn-distance"], absCheck=check, **extra)


# ======================================================================
# Группы
# ======================================================================

GROUPS = [
    ("iadd", "Сумма целых чисел", g_iadd, 2),
    ("isub", "Разность целых чисел", g_isub, 3),
    ("dec", "Десятичные дроби", g_dec, 4),
    ("frac", "Обыкновенные дроби", g_frac, 5),
    ("mixed", "Смешанные числа и вперемешку", g_mixed, 5),
    ("chain", "Цепочки со скобками", g_chain, 6),
    ("sign", "Какой знак у результата?", g_sign, 2),
    ("gap", "Пропущенное число", g_gap, 3),
    ("cmp", "Что больше?", g_cmp, 1),
]
OLYMPIAD = [("abs", "⭐ Модули и расстояния", g_abs, 7)]


# ======================================================================
# Независимая проверка (не пользуется функциями генератора выше)
# ======================================================================


class TexError(Exception):
    pass


def _sym_value(s: str) -> F:
    """Точное значение записи для компьютера через SymPy (десятичные дроби — точно)."""
    v = sp.nsimplify(sp.sympify(s.replace("^", "**"), rational=True))
    if not v.is_Rational:
        raise TexError(f"не число: {s}")
    return F(int(v.p), int(v.q))


_SKIP_CMDS = {"displaystyle", "quad", "qquad", ",", ";", " ", "!", "boxed"}


def _tokens(s: str) -> list[tuple]:
    out, i = [], 0
    while i < len(s):
        c = s[i]
        if c.isspace():
            i += 1
            continue
        if c == "\\":
            m = re.match(r"\\([a-zA-Z]+|.)", s[i:])
            name = m.group(1)
            i += len(m.group(0))
            if name in _SKIP_CMDS:
                continue
            if name in ("dfrac", "frac"):
                out.append(("frac",))
            elif name in ("left", "right"):
                d = s[i]
                i += 1
                if d in "()":
                    out.append((d,))
                elif d == "|":
                    out.append(("|L",) if name == "left" else ("|R",))
                else:
                    raise TexError(f"\\{name}{d}")
            elif name == "cdot":
                out.append(("*",))
            elif name in ("ge", "geq"):
                out.append(("rel", ">="))
            elif name in ("le", "leq"):
                out.append(("rel", "<="))
            elif name in ("ne", "neq"):
                out.append(("rel", "!="))
            else:
                raise TexError(f"\\{name}")
            continue
        if c.isdigit():
            m = re.match(r"\d+(?:\{,\}\d+)?", s[i:])
            txt = m.group(0)
            out.append(("num", F(txt.replace("{,}", ".")), "{,}" not in txt))
            i += len(txt)
            continue
        if c in "+-":
            out.append(("op", c))
        elif c in "<>=":
            out.append(("rel", c))
        elif c == ":":
            out.append(("/",))
        elif c in "(){}|":
            out.append((c,))
        elif c in "x?":
            out.append(("var", c))
        else:
            raise TexError(c)
        i += 1
    return out


class _TexParser:
    """Разбор TeX из условий и решений: числа, \\dfrac, смешанные числа, скобки, модули, \\cdot, «:»."""

    def __init__(self, s: str, env: dict | None = None):
        self.t, self.i, self.env = _tokens(s), 0, env or {}
        self.atoms, self.depth = 0, 0

    def peek(self):
        return self.t[self.i] if self.i < len(self.t) else ("end",)

    def take(self, kind=None):
        tok = self.peek()
        if kind and tok[0] != kind:
            raise TexError(f"ждали {kind}, а там {tok}")
        self.i += 1
        return tok

    def expr(self) -> F:
        v = self.term()
        while self.peek()[0] == "op":
            op = self.take()[1]
            r = self.term()
            v = v + r if op == "+" else v - r
        return v

    def term(self) -> F:
        v = self.unary()
        while self.peek()[0] in ("*", "/"):
            k = self.take()[0]
            r = self.unary()
            if k == "/" and r == 0:
                raise TexError("деление на ноль")
            v = v * r if k == "*" else v / r
        return v

    def unary(self) -> F:
        if self.peek()[0] == "op":
            op = self.take()[1]
            v = self.unary()
            return -v if op == "-" else v
        return self.atom()

    def frac(self) -> F:
        self.take("frac")
        self.depth += 1
        self.take("{")
        n = self.expr()
        self.take("}")
        self.take("{")
        d = self.expr()
        self.take("}")
        self.depth -= 1
        if d == 0:
            raise TexError("знаменатель 0")
        return n / d

    def atom(self) -> F:
        k = self.peek()[0]
        if k == "num":
            _, v, is_int = self.take()
            if self.depth == 0:
                self.atoms += 1
            if is_int and self.peek()[0] == "frac":  # смешанное число: 2\dfrac{1}{3} = 2 + 1/3
                part = self.frac()
                if not (0 < part < 1):
                    raise TexError("дробная часть смешанного числа")
                return v + part
            return v
        if k == "frac":
            if self.depth == 0:
                self.atoms += 1
            return self.frac()
        if k in ("(", "{"):
            close = ")" if k == "(" else "}"
            self.take()
            v = self.expr()
            self.take(close)
            return v
        if k == "|L":
            self.take()
            v = self.expr()
            self.take("|R")
            return abs(v)
        if k == "|":
            self.take()
            v = self.expr()
            self.take("|")
            return abs(v)
        if k == "var":
            name = self.take()[1]
            if name not in self.env:
                raise TexError(f"неизвестная {name}")
            return F(self.env[name])
        raise TexError(f"не понял {self.peek()}")

    def relation(self):
        vals, rels = [self.expr()], []
        while self.peek()[0] == "rel":
            rels.append(self.take()[1])
            vals.append(self.expr())
        if self.peek()[0] != "end":
            raise TexError(f"лишнее в конце: {self.peek()}")
        return vals, rels


def tex_value(s: str, env: dict | None = None) -> F:
    p = _TexParser(s, env)
    vals, rels = p.relation()
    if rels:
        raise TexError("ждали число, а тут сравнение")
    return vals[0]


def tex_atoms(s: str) -> int:
    p = _TexParser(s)
    p.relation()
    return p.atoms


def _holds(a: F, r: str, b: F) -> bool:
    return {"=": a == b, "<": a < b, ">": a > b, "<=": a <= b, ">=": a >= b, "!=": a != b}[r]


def tex_true(s: str, env: dict | None = None) -> bool:
    vals, rels = _TexParser(s, env).relation()
    if not rels:
        raise TexError("нет сравнения")
    return all(_holds(a, r, b) for a, r, b in zip(vals, rels, vals[1:]))


_MATH = re.compile(r"\$([^$]+)\$")


def _math(s: str) -> list[str]:
    return _MATH.findall(s)


def check_solution(lines: list[str]) -> tuple[str | None, int]:
    """Каждое равенство и неравенство из чисел в решении должно быть верным. Возвращает (ошибка, сколько проверено)."""
    checked = 0
    for line in lines:
        for seg in _math(line):
            try:
                vals, rels = _TexParser(seg).relation()
            except (TexError, ZeroDivisionError):
                continue
            if not rels:
                continue
            for a, r, b in zip(vals, rels, vals[1:]):
                if not _holds(a, r, b):
                    return f"в решении неверно: ${seg}$ ({a} {r} {b})", checked
            checked += 1
    return None, checked


def _answer_format(t: dict) -> str | None:
    a = t["answer"]
    if t["answerKind"] == "roots":
        return None
    if t.get("reduce"):
        m = re.fullmatch(r"-?(\d+)(?:/(\d+))?", a)
        if not m:
            return f"ответ «{a}» не дробь p/q"
        if m.group(2) and (math.gcd(int(m.group(1)), int(m.group(2))) != 1 or int(m.group(2)) < 2):
            return f"ответ «{a}» можно сократить"
        return None
    if not re.fullmatch(r"-?\d+(\.\d*[1-9])?", a):
        return f"ответ «{a}» не целое и не десятичная дробь без лишних нулей"
    return None


def _v_value(t: dict) -> str | None:
    if "{expr}" not in t["prompt"]:
        return "в условии нет формулы {expr}"
    v_app = _sym_value(t["expr"])
    v_tex = tex_value(t["tex"])
    v_ans = _sym_value(t["answer"])
    if not (v_app == v_tex == v_ans):
        return f"значение по expr {v_app}, по TeX {v_tex}, в ответе {v_ans}"
    if t.get("answerTex") and tex_value(t["answerTex"]) != v_ans:
        return f"answerTex {t['answerTex']} не равен ответу"
    if t["level"] == 1 and t["group"] != "chain" and tex_atoms(t["tex"]) != 2:
        return "на первом уровне должно быть одно действие (два числа)"
    return _answer_format(t)


def _v_sign(t: dict) -> str | None:
    v1, v2 = _sym_value(t["expr"]), tex_value(t["tex"])
    if v1 != v2:
        return f"expr {v1} и TeX {v2} не совпадают"
    if t["options"] != SIGN_OPTS:
        return "варианты не те"
    want = 0 if v1 > 0 else (1 if v1 < 0 else 2)
    return None if int(t["answer"]) == want else f"знак результата {v1}: вариант {want}, в ответе {t['answer']}"


def _v_cmp(t: dict) -> str | None:
    ta, tb = t["cmp"]["a"], t["cmp"]["b"]
    if f"${ta}$" not in t["prompt"] or f"${tb}$" not in t["prompt"]:
        return "в условии не те выражения"
    a1, b1 = _sym_value(t["expr"]), _sym_value(t["expr2"])
    a2, b2 = tex_value(ta), tex_value(tb)
    if (a1, b1) != (a2, b2):
        return f"expr ({a1}, {b1}) и TeX ({a2}, {b2}) не совпадают"
    true_opts = [i for i, o in enumerate(t["options"]) if tex_true(_math(o)[0])]
    return None if true_opts == [int(t["answer"])] else f"верные варианты {true_opts}, в ответе {t['answer']}"


def _v_gap(t: dict) -> str | None:
    seg = next(s for s in _math(t["prompt"]) if "boxed" in s)
    X = _sym_value(t["answer"])
    vals, rels = _TexParser(seg, {"?": X}).relation()
    if rels != ["="] or vals[0] != vals[1]:
        return f"с ответом {X} равенство неверно: {vals}"
    v2, _ = _TexParser(seg, {"?": X + 1}).relation()
    if v2[0] == v2[1]:
        return "в окошко подходит не одно число"
    x = sp.Symbol("x")
    lhs = sp.sympify(t["gap"]["lhs"], locals={"x": x}, rational=True)
    rhs = sp.sympify(t["gap"]["rhs"], rational=True)
    sols = sp.solve(sp.Eq(lhs, rhs), x)
    if sols != [sp.Rational(X.numerator, X.denominator)]:
        return f"SymPy: решения {sols}, в ответе {X}"
    return _answer_format(t)


def _v_abs(t: dict) -> str | None:
    kind = t["absCheck"]["kind"]
    segs = _math(t["prompt"])
    with_x = [s for s in segs if "x" in s and s != "x"]
    if kind in ("cnt", "sum", "eqcnt"):
        cond = with_x[0]
        good = [x for x in range(-300, 301) if tex_true(cond, {"x": x})]
        if not good or good[0] == -300 or good[-1] == 300:
            return "перебор: решений нет или бесконечно много"
        got = F(sum(good)) if kind == "sum" else F(len(good))
        return None if got == _sym_value(t["answer"]) else f"перебор даёт {got}, в ответе {t['answer']}"
    if kind in ("min2", "min3", "arg3"):
        e = with_x[0]
        grid = [F(k, 4) for k in range(-240, 241)]  # x от −60 до 60 через 1/4: все изломы — целые
        vals = [(tex_value(e, {"x": x}), x) for x in grid]
        low = min(v for v, _ in vals)
        args = [x for v, x in vals if v == low]
        if kind == "arg3":
            if len(args) != 1:
                return f"наименьшее значение при нескольких x: {args[:5]}"
            got = args[0]
        else:
            got = low
        return None if got == _sym_value(t["answer"]) else f"перебор даёт {got}, в ответе {t['answer']}"
    if kind == "roots":
        eq = with_x[0]
        grid = [F(k, 4) for k in range(-240, 241)]
        roots = [x for x in grid if tex_true(eq, {"x": x})]
        for r1, r2 in zip(roots, roots[1:]):
            if r2 - r1 == F(1, 4):
                return "решений бесконечно много"
        want = [] if t["answer"] == "нет" else sorted(_sym_value(p.strip()) for p in t["answer"].split(";"))
        return None if roots == want else f"перебор даёт {roots}, в ответе {t['answer']}"
    if kind == "mid":
        nums = []
        for s in segs:
            try:
                nums.append(tex_value(s))
            except TexError:
                pass
        if len(nums) != 2:
            return f"в условии не два числа: {nums}"
        a, b = nums
        mids = [F(k, 4) for k in range(-240, 241) if abs(F(k, 4) - a) == abs(F(k, 4) - b)]
        if len(mids) != 1:
            return f"равноудалённых точек {len(mids)}"
        return None if mids[0] == _sym_value(t["answer"]) else f"перебор даёт {mids[0]}, в ответе {t['answer']}"
    return f"неизвестная проверка {kind}"


_VERIFY = {
    "iadd": _v_value, "isub": _v_value, "dec": _v_value, "frac": _v_value, "mixed": _v_value, "chain": _v_value,
    "sign": _v_sign, "gap": _v_gap, "cmp": _v_cmp, "abs": _v_abs,
}


def verify(t: dict) -> str | None:
    """Независимая проверка задания: None — всё верно, строка — что не так."""
    try:
        msg = _VERIFY[t["group"]](t)
        if msg:
            return msg
        if not t.get("skills") or not all(s.startswith("rn-") for s in t["skills"]):
            return f"навыки {t.get('skills')}"
        err, n = check_solution(t["solution"])
        if err:
            return err
        if n == 0:
            return "в решении нет ни одной проверяемой выкладки"
        if not 2 <= len(t["solution"]) <= 5:
            return f"в решении {len(t['solution'])} строк"
    except (TexError, ZeroDivisionError, StopIteration, KeyError, IndexError, ValueError, sp.SympifyError) as e:
        return f"проверка не смогла разобрать задание: {e!r}"
    return None
