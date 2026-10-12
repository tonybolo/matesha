"""Тема 3: корни и сравнение чисел (КР №3 A1, C1; классная работа №1)."""
from __future__ import annotations

import math
import random
from decimal import Decimal
from fractions import Fraction

from common import *  # noqa: F401,F403

SQF = [2, 3, 5, 6, 7, 10, 11, 13]  # числа без квадратных множителей


def _sign(a, b):
    return "<" if a < b else (">" if a > b else "=")


def _flip(sgn):
    return {"<": ">", ">": "<", "=": "="}[sgn]


def _small_frac_tex(v: Fraction) -> str:
    """Дробь в TeX: десятичной, если знаменатель 2, 4, 5, 8, 10; иначе обыкновенной."""
    if v.denominator in (1, 2, 4, 5, 8, 10):
        return dec_tex(Decimal(v.numerator) / Decimal(v.denominator))
    return tex_num(v)


# ---------- какое число иррациональное ----------

def g_irr(rng: random.Random, level: int):
    if level == 1:
        s = rng.randint(3, 30)
        rat_exps = rng.sample([4, -4, -2, 2, 0], 3)
        irr_exp = rng.choice([1, -3, 3])
        opts = [(Decimal(s * s).scaleb(e), True, e) for e in rat_exps] + [(Decimal(s * s).scaleb(irr_exp), False, irr_exp)]
        rng.shuffle(opts)
        options = [f"$\\sqrt{{{dec_tex(v)}}}$" for v, _, _ in opts]
        opt_exprs = [f"sqrt({dec_expr(v)})" for v, _, _ in opts]
        correct = next(i for i, (_, rat, _) in enumerate(opts) if not rat)
        steps = []
        for v, rat, e in opts:
            if rat:
                steps.append(f"$\\sqrt{{{dec_tex(v)}}}={dec_tex(Decimal(s).scaleb(e // 2))}$: число рациональное.")
            else:
                steps.append(f"$\\sqrt{{{dec_tex(v)}}}$: число под корнем не точный квадрат, значит корень **иррациональный**.")
        return task("Укажите, какое из чисел является иррациональным.", str(correct), "choice",
                    "Корень рациональный, если под корнем точный квадрат (можно со сдвигом запятой на два знака).",
                    steps, ["sqrt-def", "irrational", "decimals"], options=options, optExprs=opt_exprs)
    if level == 2:
        m = rng.choice([x for x in range(2, 60) if not is_square(x)])
        t = rng.randint(11, 30)
        cands = [
            (f"\\sqrt{{{m}}}\\cdot\\sqrt{{{m}}}", True, f"$\\sqrt{{{m}}}\\cdot\\sqrt{{{m}}}={m}$: рациональное.", f"sqrt({m})*sqrt({m})"),
            (f"\\sqrt{{{m}}}-\\sqrt{{{m}}}", True, "$\\sqrt{%d}-\\sqrt{%d}=0$: рациональное." % (m, m), f"sqrt({m})-sqrt({m})"),
            (f"\\sqrt{{{t * t}}}", True, f"$\\sqrt{{{t * t}}}={t}$: рациональное.", f"sqrt({t * t})"),
            (f"\\sqrt{{{m}}}+\\sqrt{{{m}}}", False, f"$\\sqrt{{{m}}}+\\sqrt{{{m}}}=2\\sqrt{{{m}}}$: иррациональное, потому что {m} не точный квадрат.", f"sqrt({m})+sqrt({m})"),
        ]
        rng.shuffle(cands)
        correct = next(i for i, c in enumerate(cands) if not c[1])
        return task("Укажите, какое из чисел **не является** рациональным.", str(correct), "choice",
                    "Упрости каждое число: в одних корень «исчезает» (произведение одинаковых корней, разность одинаковых), в одном остаётся.",
                    [c[2] for c in cands], ["sqrt-def", "irrational", "sqrt-ops"],
                    options=[f"${c[0]}$" for c in cands], optExprs=[c[3] for c in cands])
    m = rng.choice([x for x in range(2, 20) if not is_square(x)])
    k = rng.randint(2, 5)
    n = m * (m + 1)
    cands = [
        (f"\\sqrt{{{m}}}\\cdot\\sqrt{{{m * k * k}}}", True, f"$\\sqrt{{{m}}}\\cdot\\sqrt{{{m * k * k}}}=\\sqrt{{{m * m * k * k}}}={m * k}$: рациональное.", f"sqrt({m})*sqrt({m * k * k})"),
        (f"\\dfrac{{\\sqrt{{{m * k * k}}}}}{{\\sqrt{{{m}}}}}", True, f"$\\dfrac{{\\sqrt{{{m * k * k}}}}}{{\\sqrt{{{m}}}}}=\\sqrt{{{k * k}}}={k}$: рациональное.", f"sqrt({m * k * k})/sqrt({m})"),
        (f"\\left(\\sqrt{{{m}}}\\right)^2", True, f"$\\left(\\sqrt{{{m}}}\\right)^2={m}$: рациональное.", f"sqrt({m})^2"),
        (f"\\sqrt{{{m}}}\\cdot\\sqrt{{{m + 1}}}", False,
         f"$\\sqrt{{{m}}}\\cdot\\sqrt{{{m + 1}}}=\\sqrt{{{n}}}$: число ${n}$ лежит между соседними квадратами ${m}^2={m * m}$ и ${m + 1}^2={(m + 1) ** 2}$, значит не является точным квадратом, и корень иррациональный.",
         f"sqrt({m})*sqrt({m + 1})"),
    ]
    rng.shuffle(cands)
    correct = next(i for i, c in enumerate(cands) if not c[1])
    return task("Укажите, какое из чисел иррациональное.", str(correct), "choice",
                "Сначала перемножь или раздели корни: $\\sqrt{a}\\cdot\\sqrt{b}=\\sqrt{ab}$, и посмотри, точный ли квадрат получился.",
                [c[2] for c in cands], ["sqrt-def", "irrational", "sqrt-prod"],
                options=[f"${c[0]}$" for c in cands], optExprs=[c[3] for c in cands])


# ---------- корень и число ----------

def g_rootnum(rng: random.Random, level: int):
    if level == 1:
        b = rng.randint(3, 12)
        d = rng.choice([-7, -5, -3, -2, -1, 1, 2, 3, 5, 7])
        a = b * b + d
        if a < 2:
            return None
        swap = rng.random() < 0.5
        sgn = _sign(a, b * b)
        root_first = f"\\sqrt{{{a}}}\\ {sgn}\\ {b}"
        final = root_first if not swap else f"{b}\\ {_flip(sgn)}\\ \\sqrt{{{a}}}"
        sol = [f"Запишем {b} корнем: ${b}=\\sqrt{{{b * b}}}$ (так как ${b}\\cdot {b}={b * b}$).",
               f"Сравниваем числа под корнем: ${a}$ и ${b * b}$.",
               f"${a}\\ {sgn}\\ {b * b}$, значит ${final}$."]
        e1, e2 = (f"sqrt({a})", str(b)) if not swap else (str(b), f"sqrt({a})")
        return task("Сравните числа {expr} и {expr2}.", sgn if not swap else _flip(sgn), "compare",
                    "Превратите целое число в корень: $b=\\sqrt{b^2}$. Дальше больше число под корнем — больше корень.", sol,
                    ["sqrt-def", "compare-roots"], expr=e1, expr2=e2)
    if level == 2:
        tenths = rng.choice([t for t in range(21, 100) if t % 10 != 0])
        b = Decimal(tenths) / 10
        b2 = b * b
        a = int(b2) + rng.choice([-2, -1, 1, 2])
        if a < 2 or Decimal(a) == b2:
            return None
        swap = rng.random() < 0.5
        sgn = _sign(Decimal(a), b2)
        final = f"\\sqrt{{{a}}}\\ {sgn}\\ {dec_tex(b)}" if not swap else f"{dec_tex(b)}\\ {_flip(sgn)}\\ \\sqrt{{{a}}}"
        sol = [f"Возведём {dec_tex(b)} в квадрат: ${dec_tex(b)}^2={dec_tex(b2)}$, значит ${dec_tex(b)}=\\sqrt{{{dec_tex(b2)}}}$.",
               f"Сравниваем числа под корнем: ${a}$ и ${dec_tex(b2)}$.",
               f"${a}\\ {sgn}\\ {dec_tex(b2)}$, значит ${final}$."]
        e1, e2 = (f"sqrt({a})", dec_expr(b)) if not swap else (dec_expr(b), f"sqrt({a})")
        return task("Сравните числа {expr} и {expr2}.", sgn if not swap else _flip(sgn), "compare",
                    "Возведи десятичное число в квадрат и сравни с числом под корнем.", sol,
                    ["sqrt-def", "compare-roots", "decimals"], expr=e1, expr2=e2)
    b = rng.randint(4, 11)
    q = rng.choice([2, 3, 4])
    p = q * b * b + rng.choice([-3, -2, -1, 1, 2, 3])
    if math.gcd(p, q) != 1:
        return None
    sgn = _sign(p, q * b * b)
    sol = [f"Запишем {b} корнем: ${b}=\\sqrt{{{b * b}}}$.",
           f"Сравним дробь $\\dfrac{{{p}}}{{{q}}}$ с числом ${b * b}$. Домножим ${b * b}$ на ${q}$: ${b * b}\\cdot {q}={b * b * q}$.",
           f"${p}\\ {sgn}\\ {b * b * q}$, значит $\\dfrac{{{p}}}{{{q}}}\\ {sgn}\\ {b * b}$, и $\\sqrt{{\\dfrac{{{p}}}{{{q}}}}}\\ {sgn}\\ {b}$."]
    return task("Сравните числа {expr} и {expr2}.", sgn, "compare",
                "Сравни дробь $\\frac{p}{q}$ с числом $b^2$: умножь $b^2$ на $q$ и сравни числители.", sol,
                ["sqrt-def", "compare-roots", "fractions"], expr=f"sqrt({p}/{q})", expr2=str(b))


# ---------- a√b и c√d ----------

def g_cmp(rng: random.Random, level: int):
    if level == 1:
        a, c = rng.randint(2, 7), rng.randint(2, 7)
        b, d = rng.choice(SQF), rng.choice(SQF)
        A, B = a * a * b, c * c * d
        if A == B or (a == c and b == d):
            return None
        sgn = _sign(A, B)
        sol = [f"${a}^2={a}\\cdot {a}={a * a}$ и ${c}^2={c}\\cdot {c}={c * c}$.",
               f"Внесём множители под корень: ${a}\\sqrt{{{b}}}=\\sqrt{{{a * a}\\cdot {b}}}=\\sqrt{{{A}}}$, ${c}\\sqrt{{{d}}}=\\sqrt{{{c * c}\\cdot {d}}}=\\sqrt{{{B}}}$.",
               f"${A}\\ {sgn}\\ {B}$, значит ${a}\\sqrt{{{b}}}\\ {sgn}\\ {c}\\sqrt{{{d}}}$."]
        return task("Сравните числа {expr} и {expr2}.", sgn, "compare",
                    "Внеси число перед корнем под корень: $a\\sqrt{b}=\\sqrt{a^2\\cdot b}$, потом сравни числа под корнем.", sol,
                    ["compare-roots", "bring-under-root"], expr=f"{a}*sqrt({b})", expr2=f"{c}*sqrt({d})")
    if level == 2:
        kind = rng.choice(["neg", "mixed", "int"])
        a, c = rng.randint(2, 7), rng.randint(2, 7)
        b, d = rng.choice(SQF), rng.choice(SQF)
        A, B = a * a * b, c * c * d
        if A == B:
            return None
        if kind == "neg":
            sgn = _sign(-A, -B)
            sol = ["Оба числа отрицательные: больше то, у которого **модуль меньше**.",
                   f"Сравним модули: ${a}\\sqrt{{{b}}}=\\sqrt{{{A}}}$ и ${c}\\sqrt{{{d}}}=\\sqrt{{{B}}}$, и ${A}\\ {_sign(A, B)}\\ {B}$.",
                   f"Поэтому $-{a}\\sqrt{{{b}}}\\ {sgn}\\ -{c}\\sqrt{{{d}}}$."]
            return task("Сравните числа {expr} и {expr2}.", sgn, "compare",
                        "Сначала сравни числа без минуса, потом переверни знак.", sol,
                        ["compare-roots", "bring-under-root", "negatives"], expr=f"-{a}*sqrt({b})", expr2=f"-{c}*sqrt({d})")
        if kind == "mixed":
            swap = rng.random() < 0.5
            sol = [f"$-{a}\\sqrt{{{b}}}$ отрицательное, а ${c}\\sqrt{{{d}}}$ положительное.",
                   "Отрицательное число всегда меньше положительного: считать ничего не нужно."]
            e1, e2 = (f"-{a}*sqrt({b})", f"{c}*sqrt({d})") if not swap else (f"{c}*sqrt({d})", f"-{a}*sqrt({b})")
            return task("Сравните числа {expr} и {expr2}.", "<" if not swap else ">", "compare",
                        "Посмотри на знаки чисел: возможно, считать не придётся.", sol,
                        ["compare-roots", "negatives"], expr=e1, expr2=e2)
        m = rng.randint(5, 15)
        if A == m * m:
            return None
        sgn = _sign(A, m * m)
        sol = [f"${m}=\\sqrt{{{m * m}}}$ и ${a}\\sqrt{{{b}}}=\\sqrt{{{a * a}\\cdot {b}}}=\\sqrt{{{A}}}$.",
               f"${A}\\ {sgn}\\ {m * m}$, значит ${a}\\sqrt{{{b}}}\\ {sgn}\\ {m}$."]
        return task("Сравните числа {expr} и {expr2}.", sgn, "compare",
                    "Превращай оба числа в корни и сравнивай числа под корнем.", sol,
                    ["compare-roots", "bring-under-root"], expr=f"{a}*sqrt({b})", expr2=str(m))
    if rng.random() < 0.5:
        # две суммы корней с одинаковой суммой подкоренных чисел
        s = rng.randint(10, 24)
        a, c = rng.sample(range(1, s), 2)
        b, d = s - a, s - c
        if a * b == c * d or any(is_square(x) for x in (a, b, c, d)):
            return None
        sgn = _sign(a * b, c * d)
        first = "первая сумма больше" if sgn == ">" else "первая сумма меньше"
        sol = [f"Обе суммы положительные, поэтому можно сравнить их квадраты: $(\\sqrt{{{a}}}+\\sqrt{{{b}}})^2={a}+{b}+2\\sqrt{{{a * b}}}={s}+2\\sqrt{{{a * b}}}$.",
               f"Для второй суммы: $(\\sqrt{{{c}}}+\\sqrt{{{d}}})^2={c}+{d}+2\\sqrt{{{c * d}}}={s}+2\\sqrt{{{c * d}}}$.",
               f"Одинаковую часть ${s}$ отбрасываем и сравниваем ${a * b}$ и ${c * d}$: ${a * b}\\ {sgn}\\ {c * d}$, то есть {first}."]
        return task("Сравните числа {expr} и {expr2}.", sgn, "compare",
                    "Возведи обе суммы в квадрат: часть, которая не отличается, можно отбросить.", sol,
                    ["compare-roots", "square-both"], expr=f"sqrt({a})+sqrt({b})", expr2=f"sqrt({c})+sqrt({d})")
    a, c = rng.randint(3, 12), rng.randint(3, 12)
    b, d = rng.choice(SQF), rng.choice(SQF)
    A, B = a * a * b, c * c * d
    if A == B or abs(A - B) > 12:
        return None
    sgn = _sign(A, B)
    sol = [f"${a}\\sqrt{{{b}}}=\\sqrt{{{a * a}\\cdot {b}}}=\\sqrt{{{A}}}$ и ${c}\\sqrt{{{d}}}=\\sqrt{{{c * c}\\cdot {d}}}=\\sqrt{{{B}}}$.",
           f"${A}\\ {sgn}\\ {B}$, значит ${a}\\sqrt{{{b}}}\\ {sgn}\\ {c}\\sqrt{{{d}}}$."]
    return task("Сравните числа {expr} и {expr2}.", sgn, "compare",
                "Числа близки по значению: считай аккуратно, внося множители под корень.", sol,
                ["compare-roots", "bring-under-root"], expr=f"{a}*sqrt({b})", expr2=f"{c}*sqrt({d})")


# ---------- расставить по порядку ----------

def _square_line(nums) -> str:
    parts = []
    for n in nums:
        v = n.square
        parts.append(f"$\\left({n.tex()}\\right)^2={_small_frac_tex(v)}$")
    return "Возведём числа в квадрат: " + "; ".join(parts) + "."


def _order_task(nums, hint, skills, intro):
    idx = sorted(range(len(nums)), key=lambda i: nums[i].value())
    vals = [n.value() for n in nums]
    if len({round(v, 9) for v in vals}) < len(nums):
        return None
    order = " < ".join(f"${nums[i].tex()}$" for i in idx)
    sol = [intro, _square_line(nums)]
    if all(n.sign > 0 for n in nums):
        sol.append("Чем больше число под корнем, тем больше само число. Порядок: " + order + ".")
    else:
        sol.append("Все числа отрицательные: больше то, у которого меньше модуль (квадрат меньше). Порядок: " + order + ".")
    return task("Расположите числа в порядке возрастания: {items}.", ",".join(map(str, idx)), "order",
                hint, sol, skills, items=[n.expr() for n in nums])


def g_ord(rng: random.Random, level: int):
    if level == 1:
        n = rng.randint(5, 11)
        e1 = rng.choice([-3, -2, -1, 1, 2, 3])
        f = rng.choice([-5, -3, -1, 1, 3, 5])
        nums = [Sqrt(1, 1, n * n + e1), Sqrt(1, n, 1), Sqrt(1, 1, Fraction(2 * n * n + f, 2))]
        rng.shuffle(nums)
        return _order_task(nums, "Запиши все числа корнями и сравни числа под корнем: $n=\\sqrt{n^2}$.", ["compare-roots", "sqrt-def"],
                           "Сравнивать удобнее, когда числа записаны одинаково: сравним их квадраты.")
    if level == 2:
        a, c = rng.randint(2, 5), rng.randint(2, 5)
        b, d = rng.choice(SQF), rng.choice(SQF)
        m = rng.randint(4, 14)
        nums = [Sqrt(1, a, b), Sqrt(1, c, d), Sqrt(1, m, 1)]
        rng.shuffle(nums)
        return _order_task(nums, "Внеси множители под корень, целое число запиши корнем и сравни числа под корнем.",
                           ["compare-roots", "bring-under-root"], "Внесём всё под корень: для этого возведём числа в квадрат.")
    a, c = rng.randint(2, 6), rng.randint(2, 6)
    b, d = rng.choice(SQF), rng.choice(SQF)
    m = rng.randint(3, 12)
    nums = [Sqrt(-1, a, b), Sqrt(-1, c, d), Sqrt(-1, m, 1)]
    rng.shuffle(nums)
    return _order_task(nums, "Сравни числа без минусов, потом переверни порядок: у отрицательных чисел всё наоборот.",
                       ["compare-roots", "negatives", "bring-under-root"], "Числа отрицательные.")


GROUPS = [
    ("irr", "Какое число иррациональное?", g_irr, 1),
    ("rootnum", "Корень и число", g_rootnum, 2),
    ("cmp", "Сравни a√b и c√d", g_cmp, 3),
    ("ord", "Расставь по порядку", g_ord, 2),
]
