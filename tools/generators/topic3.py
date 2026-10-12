"""Тема 3: корни и сравнение чисел (КР №3 A1, C1; классная работа №1)."""
from __future__ import annotations

import math
import random
from decimal import Decimal
from fractions import Fraction

import sympy as sp

from common import *  # noqa: F401,F403


def _sign(a, b):
    return "<" if a < b else (">" if a > b else "=")


# ---------- какое число иррациональное ----------

def g_irr(rng: random.Random, level: int):
    if level == 1:
        s = rng.randint(3, 30)
        rat_exps = rng.sample([4, -4, -2, 2, 0], 3)  # 100^k: s²·10^e
        irr_exp = rng.choice([1, -3, 3])
        def num(e):  # s²·10^e
            return Decimal(s * s).scaleb(e)
        opts = [(num(e), True, e) for e in rat_exps] + [(num(irr_exp), False, irr_exp)]
        rng.shuffle(opts)
        options = [f"$\\sqrt{{{dec_tex(v)}}}$" for v, _, _ in opts]
        opt_exprs = [f"sqrt({dec_expr(v)})" for v, _, _ in opts]
        correct = next(i for i, (_, rat, _) in enumerate(opts) if not rat)
        steps = []
        for v, rat, e in opts:
            if rat:
                root = Decimal(s).scaleb(e // 2)
                steps.append(f"$\\sqrt{{{dec_tex(v)}}}={dec_tex(root)}$: рациональное.")
            else:
                steps.append(f"$\\sqrt{{{dec_tex(v)}}}$: число под корнем не точный квадрат, значит корень **иррациональный**.")
        return task(
            "Укажите, какое из чисел является иррациональным.",
            str(correct), "choice",
            "Рациональный корень получается, если под корнем точный квадрат (можно со сдвигом запятой на два знака).",
            steps, ["sqrt-def", "irrational", "decimals"], options=options, optExprs=opt_exprs,
        )
    if level == 2:
        m = rng.choice([x for x in range(2, 60) if not is_square(x)])
        t = rng.randint(11, 30)
        cands = [
            (f"\\sqrt{{{m}}}\\cdot\\sqrt{{{m}}}", True, f"$\\sqrt{{{m}}}\\cdot\\sqrt{{{m}}}={m}$: рациональное.", f"sqrt({m})*sqrt({m})"),
            (f"\\sqrt{{{m}}}-\\sqrt{{{m}}}", True, f"$\\sqrt{{{m}}}-\\sqrt{{{m}}}=0$: рациональное.", f"sqrt({m})-sqrt({m})"),
            (f"\\sqrt{{{t * t}}}", True, f"$\\sqrt{{{t * t}}}={t}$: рациональное.", f"sqrt({t * t})"),
            (f"\\sqrt{{{m}}}+\\sqrt{{{m}}}", False, f"$\\sqrt{{{m}}}+\\sqrt{{{m}}}=2\\sqrt{{{m}}}$: иррациональное, так как {m} не точный квадрат.", f"sqrt({m})+sqrt({m})"),
        ]
        rng.shuffle(cands)
        correct = next(i for i, c in enumerate(cands) if not c[1])
        return task(
            "Укажите, какое из чисел **не является** рациональным.",
            str(correct), "choice",
            "Упрости каждое число: в одних корень «сокращается» (произведение одинаковых, разность одинаковых), в одном остаётся.",
            [c[2] for c in cands], ["sqrt-def", "irrational", "sqrt-ops"], options=[f"${c[0]}$" for c in cands],
            optExprs=[c[3] for c in cands],
        )
    # level 3
    m = rng.choice([x for x in range(2, 20) if not is_square(x)])
    k = rng.randint(2, 5)
    cands = [
        (f"\\sqrt{{{m}}}\\cdot\\sqrt{{{m * k * k}}}", True, f"$\\sqrt{{{m}}}\\cdot\\sqrt{{{m * k * k}}}=\\sqrt{{{m * m * k * k}}}={m * k}$: рациональное.", f"sqrt({m})*sqrt({m * k * k})"),
        (f"\\dfrac{{\\sqrt{{{m * k * k}}}}}{{\\sqrt{{{m}}}}}", True, f"$\\dfrac{{\\sqrt{{{m * k * k}}}}}{{\\sqrt{{{m}}}}}=\\sqrt{{{k * k}}}={k}$: рациональное.", f"sqrt({m * k * k})/sqrt({m})"),
        (f"\\left(\\sqrt{{{m}}}\\right)^2", True, f"$\\left(\\sqrt{{{m}}}\\right)^2={m}$: рациональное.", f"sqrt({m})^2"),
        (f"\\sqrt{{{m}}}\\cdot\\sqrt{{{m + 1}}}", False, f"$\\sqrt{{{m}}}\\cdot\\sqrt{{{m + 1}}}=\\sqrt{{{m * (m + 1)}}}$: между {m}² и {(m + 1)}² нет точного квадрата, значит иррациональное.", f"sqrt({m})*sqrt({m + 1})"),
    ]
    rng.shuffle(cands)
    correct = next(i for i, c in enumerate(cands) if not c[1])
    return task(
        "Укажите, какое из чисел иррациональное.",
        str(correct), "choice",
        "Сначала перемножь или раздели корни: $\\sqrt{a}\\cdot\\sqrt{b}=\\sqrt{ab}$ и посмотри, точный ли квадрат получился.",
        [c[2] for c in cands], ["sqrt-def", "irrational", "sqrt-prod"], options=[f"${c[0]}$" for c in cands],
        optExprs=[c[3] for c in cands],
    )


# ---------- корень и число ----------

def g_rootnum(rng: random.Random, level: int):
    if level == 1:
        b = rng.randint(3, 12)
        d = rng.choice([-7, -5, -3, -2, -1, 1, 2, 3, 5, 7])
        a = b * b + d
        if a < 2:
            return None
        sgn = _sign(a, b * b)
        sol = [f"Запишем {b} корнем: ${b}=\\sqrt{{{b * b}}}$ (так как ${b}\\cdot {b}={b * b}$).",
               f"Сравниваем подкоренные числа: ${a}$ и ${b * b}$.",
               f"${a}{sgn}{b * b}$, значит $\\sqrt{{{a}}}\\ {sgn}\\ {b}$."]
        return task("Сравните числа {expr} и {expr2}.", sgn, "compare",
                    "Превратите целое число в корень: $b=\\sqrt{b^2}$. Дальше больше подкоренное число — больше корень.", sol,
                    ["sqrt-def", "compare-roots"], expr=f"sqrt({a})", expr2=str(b))
    if level == 2:
        tenths = rng.randint(21, 99)  # 2,1 … 9,9
        b = Decimal(tenths) / 10
        b2 = b * b
        a = int(b2) + rng.choice([-2, -1, 1, 2])
        if a < 2 or Decimal(a) == b2:
            return None
        sgn = _sign(Decimal(a), b2)
        sol = [f"Возведём 2-е число в квадрат: ${dec_tex(b)}^2={dec_tex(b2)}$.",
               f"Сравниваем подкоренное ${a}$ и ${dec_tex(b2)}$.",
               f"${a}{sgn}{dec_tex(b2)}$, значит $\\sqrt{{{a}}}\\ {sgn}\\ {dec_tex(b)}$."]
        return task("Сравните числа {expr} и {expr2}.", sgn, "compare",
                    "Возведи десятичное число в квадрат и сравни с числом под корнем.", sol,
                    ["sqrt-def", "compare-roots", "decimals"], expr=f"sqrt({a})", expr2=dec_expr(b))
    # level 3: корень из дроби и целое
    b = rng.randint(4, 11)
    q = rng.choice([2, 3, 4])
    p = q * b * b + rng.choice([-3, -2, -1, 1, 2, 3])
    if math.gcd(p, q) != 1:
        return None
    val = Fraction(p, q)
    sgn = _sign(val, b * b)
    sol = [f"Запишем {b} корнем: ${b}=\\sqrt{{{b * b}}}$.",
           f"Подкоренные числа: $\\dfrac{{{p}}}{{{q}}}={dec_tex(Decimal(p) / Decimal(q)) if q in (2, 4) else tex_num(val)}$ и ${b * b}$.",
           f"${tex_num(val)}\\ {sgn}\\ {b * b}$, значит $\\sqrt{{\\dfrac{{{p}}}{{{q}}}}}\\ {sgn}\\ {b}$."]
    return task("Сравните числа {expr} и {expr2}.", sgn, "compare",
                "Сравни дробь $\\frac{p}{q}$ с числом $b^2$: домножь $b^2$ на $q$.", sol,
                ["sqrt-def", "compare-roots", "fractions"], expr=f"sqrt({p}/{q})", expr2=str(b))


# ---------- a√b и c√d ----------

def _bring(sign, coef, rad):
    return (sign, coef, rad, coef * coef * rad)


def g_cmp(rng: random.Random, level: int):
    nonsq = [x for x in range(2, 12) if not is_square(x)]
    if level == 1:
        a, c = rng.randint(2, 7), rng.randint(2, 7)
        b, d = rng.choice(nonsq), rng.choice(nonsq)
        A, B = a * a * b, c * c * d
        if A == B or (a == c and b == d):
            return None
        sgn = _sign(A, B)
        sol = [f"${a}^2={a}\\cdot {a}={a * a}$, ${c}^2={c}\\cdot {c}={c * c}$.",
               f"Внесём множители под корень: ${a}\\sqrt{{{b}}}=\\sqrt{{{a * a}\\cdot {b}}}=\\sqrt{{{A}}}$, ${c}\\sqrt{{{d}}}=\\sqrt{{{c * c}\\cdot {d}}}=\\sqrt{{{B}}}$.",
               f"${A}\\ {sgn}\\ {B}$, значит ${a}\\sqrt{{{b}}}\\ {sgn}\\ {c}\\sqrt{{{d}}}$."]
        return task("Сравните числа {expr} и {expr2}.", sgn, "compare",
                    "Внеси число перед корнем под корень: $a\\sqrt{b}=\\sqrt{a^2\\cdot b}$, потом сравни подкоренные.", sol,
                    ["compare-roots", "bring-under-root"], expr=f"{a}*sqrt({b})", expr2=f"{c}*sqrt({d})")
    if level == 2:
        kind = rng.choice(["neg", "int", "mixed"])
        a, c = rng.randint(2, 7), rng.randint(2, 7)
        b, d = rng.choice(nonsq), rng.choice(nonsq)
        A, B = a * a * b, c * c * d
        if A == B:
            return None
        if kind == "neg":
            sgn = _sign(-A, -B)
            sol = ["Оба числа отрицательные, значит больше то, у которого **модуль меньше**.",
                   f"Сравним модули: ${a}\\sqrt{{{b}}}=\\sqrt{{{A}}}$ и ${c}\\sqrt{{{d}}}=\\sqrt{{{B}}}$, ${A}\\ {_sign(A, B)}\\ {B}$.",
                   f"Поэтому $-{a}\\sqrt{{{b}}}\\ {sgn}\\ -{c}\\sqrt{{{d}}}$."]
            return task("Сравните числа {expr} и {expr2}.", sgn, "compare",
                        "Сначала сравни числа без минуса, потом переверни знак.", sol,
                        ["compare-roots", "bring-under-root", "negatives"], expr=f"-{a}*sqrt({b})", expr2=f"-{c}*sqrt({d})")
        if kind == "mixed":
            sgn = "<"
            sol = [f"${a}\\sqrt{{{b}}}$ отрицательное, ${c}\\sqrt{{{d}}}$ положительное.",
                   "Отрицательное число всегда меньше положительного: считать ничего не нужно."]
            return task("Сравните числа {expr} и {expr2}.", sgn, "compare",
                        "Посмотри на знаки чисел: считать, возможно, не придётся.", sol,
                        ["compare-roots", "negatives"], expr=f"-{a}*sqrt({b})", expr2=f"{c}*sqrt({d})")
        m = rng.randint(5, 15)
        sgn = _sign(A, m * m)
        if A == m * m:
            return None
        sol = [f"${m}=\\sqrt{{{m * m}}}$, ${a}\\sqrt{{{b}}}=\\sqrt{{{a * a}\\cdot {b}}}=\\sqrt{{{A}}}$.",
               f"${A}\\ {sgn}\\ {m * m}$, значит ${a}\\sqrt{{{b}}}\\ {sgn}\\ {m}$."]
        return task("Сравните числа {expr} и {expr2}.", sgn, "compare",
                    "Превращай оба числа в корни и сравнивай подкоренные.", sol,
                    ["compare-roots", "bring-under-root"], expr=f"{a}*sqrt({b})", expr2=str(m))
    # level 3: суммы корней с одинаковой суммой подкоренных, либо близкие значения
    if rng.random() < 0.5:
        s = rng.randint(10, 24)
        a, c = rng.sample(range(1, s), 2)
        b, d = s - a, s - c
        if a * b == c * d or min(a, b, c, d) < 1:
            return None
        sgn = _sign(a * b, c * d)
        sol = [f"Обе суммы положительные, возведём их в квадрат: $(\\sqrt{{{a}}}+\\sqrt{{{b}}})^2={a}+{b}+2\\sqrt{{{a * b}}}={s}+2\\sqrt{{{a * b}}}$.",
               f"Второе: $(\\sqrt{{{c}}}+\\sqrt{{{d}}})^2={c}+{d}+2\\sqrt{{{c * d}}}={s}+2\\sqrt{{{c * d}}}$.",
               f"Сравниваем ${a * b}$ и ${c * d}$: ${a * b}\\ {sgn}\\ {c * d}$, значит и суммы так же."]
        return task("Сравните числа {expr} и {expr2}.", sgn, "compare",
                    "Возведи обе суммы в квадрат: у них одинаковая часть, сравни остальное.", sol,
                    ["compare-roots", "square-both"], expr=f"sqrt({a})+sqrt({b})", expr2=f"sqrt({c})+sqrt({d})")
    a, c = rng.randint(3, 12), rng.randint(3, 12)
    b, d = rng.choice(nonsq), rng.choice(nonsq)
    A, B = a * a * b, c * c * d
    if A == B or abs(A - B) > 12:
        return None
    sgn = _sign(A, B)
    sol = [f"${a}\\sqrt{{{b}}}=\\sqrt{{{a * a}\\cdot {b}}}=\\sqrt{{{A}}}$, ${c}\\sqrt{{{d}}}=\\sqrt{{{c * c}\\cdot {d}}}=\\sqrt{{{B}}}$.",
           f"${A}\\ {sgn}\\ {B}$, значит ${a}\\sqrt{{{b}}}\\ {sgn}\\ {c}\\sqrt{{{d}}}$."]
    return task("Сравните числа {expr} и {expr2}.", sgn, "compare",
                "Числа близки: считай аккуратно, внося множители под корень.", sol,
                ["compare-roots", "bring-under-root"], expr=f"{a}*sqrt({b})", expr2=f"{c}*sqrt({d})")


# ---------- расставить по порядку ----------

def _order_task(nums, prompt_hint, skills, intro):
    idx = sorted(range(len(nums)), key=lambda i: nums[i].value())
    vals = [n.value() for n in nums]
    if len({round(v, 9) for v in vals}) < len(nums):
        return None
    sol = [intro]
    sol.append("Квадраты чисел: " + ", ".join(f"${n.tex()}$: ${tex_num(n.square)}$" for n in nums) + ".")
    if all(n.sign > 0 for n in nums):
        order = " < ".join(f"${nums[i].tex()}$" for i in idx)
        sol.append("Чем больше число под корнем, тем больше число. Порядок: " + order + ".")
    else:
        order = " < ".join(f"${nums[i].tex()}$" for i in idx)
        sol.append("Числа отрицательные: больше то, у которого меньше модуль. Порядок: " + order + ".")
    return task("Расположите числа в порядке возрастания: {items}.", ",".join(map(str, idx)), "order",
                prompt_hint, sol, skills, items=[n.expr() for n in nums])


def g_ord(rng: random.Random, level: int):
    nonsq = [x for x in range(2, 12) if not is_square(x)]
    if level == 1:
        n = rng.randint(5, 11)
        e1 = rng.choice([-3, -2, -1, 1, 2, 3])
        f = rng.choice([-5, -3, -1, 1, 3, 5])
        p = 2 * n * n + f
        nums = [Sqrt(1, 1, n * n + e1), Sqrt(1, n, 1), Sqrt(1, 1, Fraction(p, 2))]
        rng.shuffle(nums)
        return _order_task(nums, "Запиши все числа корнями и сравни подкоренные: $n=\\sqrt{n^2}$.", ["compare-roots", "sqrt-def"],
                           "Превратим все числа в корни.")
    if level == 2:
        a, c = rng.randint(2, 5), rng.randint(2, 5)
        b, d = rng.choice(nonsq), rng.choice(nonsq)
        m = rng.randint(4, 14)
        nums = [Sqrt(1, a, b), Sqrt(1, c, d), Sqrt(1, m, 1)]
        rng.shuffle(nums)
        return _order_task(nums, "Внеси множители под корень, целое запиши корнем и сравни подкоренные.",
                           ["compare-roots", "bring-under-root"], "Внесём всё под корень.")
    a, c = rng.randint(2, 6), rng.randint(2, 6)
    b, d = rng.choice(nonsq), rng.choice(nonsq)
    m = rng.randint(3, 12)
    nums = [Sqrt(-1, a, b), Sqrt(-1, c, d), Sqrt(-1, m, 1)]
    rng.shuffle(nums)
    return _order_task(nums, "Сравни числа без минусов, потом переверни порядок: у отрицательных чисел наоборот.",
                       ["compare-roots", "negatives", "bring-under-root"], "Числа отрицательные.")


GROUPS = [
    ("irr", "Какое число иррациональное?", g_irr),
    ("rootnum", "Корень и число", g_rootnum),
    ("cmp", "Сравни a√b и c√d", g_cmp),
    ("ord", "Расставь по порядку", g_ord),
]
