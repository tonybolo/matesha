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


# ---------- КР №3 A3: при каких x имеет смысл √(kx) ----------

OPS = [(">=", "\\ge"), (">", ">"), ("<=", "\\le"), ("<", "<")]


def _r_tex(r: Fraction) -> str:
    return _small_frac_tex(r) if r != 0 else "0"


def _dom_options(rng, r: Fraction, correct_op: str):
    pairs = [(op, f"x\\ {tex}\\ {_r_tex(r)}") for op, tex in OPS]
    order = list(range(4))
    rng.shuffle(order)
    shown = [pairs[i] for i in order]
    idx = next(i for i, (op, _) in enumerate(shown) if op == correct_op)
    return [f"${t}$" for _, t in shown], str(idx), [[op, str(r)] for op, _ in shown]


def g_dom(rng: random.Random, level: int):
    if level == 1:
        k = rng.choice([-81, -64, -49, -36, -25, -16, -9, -4, 4, 9, 16, 25, 36, 49, 64, 81])
        kt = f"{k}x"
        op = ">=" if k > 0 else "<="
        options, answer, spec = _dom_options(rng, Fraction(0), op)
        if k > 0:
            sol = [f"Под корнем не может быть отрицательное число: нужно ${kt}\\ge 0$.",
                   f"Число ${k}$ положительное, поэтому произведение ${kt}$ неотрицательно, когда $x\\ge 0$.",
                   "Ноль подходит: $\\sqrt{0}=0$. Строгого неравенства не нужно."]
        else:
            sol = [f"Под корнем не может быть отрицательное число: нужно ${kt}\\ge 0$.",
                   f"Число ${k}$ отрицательное. Произведение отрицательного числа на $x$ неотрицательно, когда $x$ тоже отрицательное или равно нулю: $x\\le 0$.",
                   "Ноль подходит: $\\sqrt{0}=0$."]
        return task("Найдите все значения переменной, при которых имеет смысл выражение {expr}.", answer, "choice",
                    "Выражение под корнем должно быть неотрицательным. Подумай про знак числа перед $x$.", sol,
                    ["sqrt-def", "sqrt-domain"], expr=f"sqrt({k}*x)", options=options,
                    domSpec={"a": k, "b": 0, "strict": False, "opts": spec, "answer": int(answer)})
    a = rng.choice([-5, -4, -3, -2, -1, 1, 2, 3, 4, 5])
    b = rng.choice([x for x in range(-12, 13) if x != 0])
    strict = level == 3
    r = Fraction(-b, a)
    if a > 0:
        op = ">" if strict else ">="
    else:
        op = "<" if strict else "<="
    options, answer, spec = _dom_options(rng, r, op)
    inner_tex = poly_tex(0, a, b)
    inner_app = poly_expr(0, a, b)
    need = ">" if strict else "\\ge"
    flip = "Делим на отрицательное число, поэтому знак неравенства меняется." if a < 0 else f"Делим на положительное число ${a}$, знак не меняется."
    rhs = f"{-b}"
    sol = [f"Под корнем должно быть {'положительное число' if strict else 'неотрицательное число'}: ${inner_tex}{need}0$." if not strict else
           f"Выражение $\\dfrac{{1}}{{\\sqrt{{{inner_tex}}}}}$ имеет смысл, если $\\sqrt{{{inner_tex}}}$ существует **и не равен нулю**: ${inner_tex}>0$.",
           f"Переносим число: ${poly_tex(0, a, 0)}{need}{rhs}$.",
           f"{flip} Получаем $x\\ {'>' if (a > 0 and strict) else ('\\ge' if a > 0 else ('<' if strict else '\\le'))}\\ {_r_tex(r)}$."]
    expr = f"sqrt({inner_app})" if not strict else f"1/sqrt({inner_app})"
    return task("Найдите все значения переменной, при которых имеет смысл выражение {expr}.", answer, "choice",
                "Составь неравенство для выражения под корнем. Если делишь на отрицательное число, знак неравенства меняется. В знаменателе ноль недопустим.", sol,
                ["sqrt-def", "sqrt-domain"], expr=expr, options=options,
                domSpec={"a": a, "b": b, "strict": strict, "opts": spec, "answer": int(answer)})


# ---------- КР №4 A3: при каком x значение функции y = √x равно v ----------

def _num_tex(v: Fraction) -> str:
    return _small_frac_tex(v)


def g_arg(rng: random.Random, level: int):
    if level in (1, 2):
        if level == 1:
            v = Fraction(rng.randint(2, 15))
        else:
            v = rng.choice([Fraction(1, 2), Fraction(2, 3), Fraction(3, 2), Fraction(3, 10), Fraction(7, 10), Fraction(5, 4), Fraction(1, 5), Fraction(6, 5), Fraction(5, 3)])
        x0 = v * v
        cands = [(x0, f"{_num_tex(x0)}"), (x0, f"\\pm {_num_tex(x0)}"), (v, f"{_num_tex(v)}"), (v, f"\\pm {_num_tex(v)}")]
        right = 0
        sol = [f"Функция $y=\\sqrt{{x}}$ принимает значение ${_num_tex(v)}$, когда $\\sqrt{{x}}={_num_tex(v)}$.",
               f"Возводим обе части в квадрат: $x=({_num_tex(v)})^2={_num_tex(x0)}$.",
               "Минус не нужен: подкоренное число $x$ не может быть отрицательным."]
        task_expr = f"sqrt(x)={_num_tex(v)}".replace("\\", "")
        info = {"a": 1, "c": 0, "v": str(v), "x0": str(x0), "ok": [True, False, False, False]}
        prompt = f"Найдите значение аргумента, при котором значение функции $y=\\sqrt{{x}}$ равно ${_num_tex(v)}$."
    else:
        t = rng.randint(2, 9)
        a = rng.randint(2, 5)
        c = rng.choice([-6, -5, -4, -3, -2, 2, 3, 4, 5, 6])
        v = a * t + c
        x0 = t * t
        wrong = [a * a * t * t, v * v, t]
        cands = [(x0, f"{x0}"), (wrong[0], f"{wrong[0]}"), (wrong[1], f"{wrong[1]}"), (wrong[2], f"{wrong[2]}")]
        if len({str(x) for x, _ in cands}) < 4:
            return None
        sol = [f"Подставим в формулу: ${a}\\sqrt{{x}}{'+' if c > 0 else '-'}{abs(c)}={v}$.",
               f"${a}\\sqrt{{x}}={v - c}$, значит $\\sqrt{{x}}={t}$.", f"Возводим в квадрат: $x={t}^2={x0}$."]
        prompt = f"Найдите значение аргумента, при котором значение функции $y={a}\\sqrt{{x}}{'+' if c > 0 else '-'}{abs(c)}$ равно ${v}$."
        info = {"a": a, "c": c, "v": str(v), "x0": str(x0), "ok": [True, False, False, False]}
        right = 0
    order = list(range(4))
    rng.shuffle(order)
    shown = [cands[i] for i in order]
    answer = order.index(right)
    options = [f"${tex}$" for _, tex in shown]
    return task(prompt, str(answer), "choice",
                "Подставь значение функции в формулу и реши получившееся уравнение. Корень не бывает отрицательным.", sol,
                ["sqrt-def", "function-value"], options=options,
                argSpec={"a": info["a"], "c": info["c"], "v": info["v"], "x0": info["x0"], "answer": answer,
                         "options": [str(x) + ("|pm" if "pm" in tex else "") for x, tex in shown]})


# ---------- КР №3 C2: решить графически √x = kx + b ----------

_GSQ_KS = sorted({Fraction(sg * a, b) for a, b in [(1, 2), (1, 3), (1, 4), (2, 3), (3, 4), (1, 1), (3, 2), (2, 1), (1, 5), (1, 6)] for sg in (1, -1)})


def g_gsq(rng: random.Random, level: int):
    max_den = {1: 2, 2: 4, 3: 6}[level]
    x0s = {1: [1, 4, 9], 2: [1, 4, 9, 16], 3: [1, 4, 9, 16, 25]}[level]
    t = sp.symbols("t")
    for _ in range(300):
        x0 = rng.choice(x0s)
        k = rng.choice(_GSQ_KS)
        b = Fraction(math.isqrt(x0)) - k * x0
        if b.denominator > max_den or b == 0 or abs(b) > 9:
            continue
        sols = [r for r in sp.solve(sp.Rational(k.numerator, k.denominator) * t**2 - t + sp.Rational(b.numerator, b.denominator), t) if r.is_real and r >= 0]
        xs = sorted({sp.nsimplify(r * r) for r in sols})
        if not xs or any(not x.is_integer for x in xs) or len(xs) > 2:
            continue
        if level == 1 and len(xs) > 1:
            continue
        # запись прямой «b + kx» как в книге: 4 − x/2
        if k.denominator == 1:
            kx = ("-" if k < 0 else "+") + ("" if abs(k) == 1 else f"{abs(k).numerator}*") + "x"
        else:
            kx = ("-" if k < 0 else "+") + ("" if abs(k.numerator) == 1 else f"{abs(k.numerator)}*") + "x" + f"/{k.denominator}"
        b_str = f"{b.numerator}/{b.denominator}" if b.denominator != 1 else str(b.numerator)
        if b > 0:
            line_expr = f"{b_str}{kx}"
        else:
            line_expr = f"{kx.lstrip('+')}-{abs(b).numerator}" + (f"/{b.denominator}" if b.denominator != 1 else "")
        ans_s = "; ".join(str(x) for x in xs)
        pts = [(x, k * x + b) for x in range(0, 17) if (k * x + b).denominator == 1 and 0 <= k * x + b <= 8][:3]
        pts_txt = ", ".join(f"$({x};\\ {int(y)})$" for x, y in pts)
        sq_txt = ", ".join(f"$({i * i};\\ {i})$" for i in range(0, 5))
        inter = "; ".join(f"$({int(x)};\\ {int(math.isqrt(int(x)))})$" for x in xs)
        many = len(xs) > 1
        sol = [f"Построим график $y=\\sqrt{{x}}$ по точкам: {sq_txt}.",
               f"Построим график $y={sp.latex(parse_app(line_expr))}$: это прямая, она проходит через точки {pts_txt}.",
               f"Графики пересекаются в {'точках' if many else 'точке'} {inter}. Ответ — {'абсциссы этих точек' if many else 'абсцисса этой точки'}: ${ans_s.replace(';', ';\\ ')}$.",
               "Проверка: подставь найденное значение в обе части уравнения."]
        return task("Решите графически уравнение {expr}={expr2}. " + RES_ROOTS, ans_s, "roots",
                    "Нарисуй график $y=\\sqrt{x}$ и график правой части. Корень уравнения — абсцисса точки пересечения. Сделай проверку подстановкой.",
                    sol, ["sqrt-graph", "linear-function"], expr="sqrt(x)", expr2=line_expr,
                    equation=["sqrt(x)", line_expr])
    return None


RES_ROOTS = "Если корней несколько, запишите их через «;»."


GROUPS = [
    ("irr", "Какое число иррациональное?", g_irr, 1),
    ("rootnum", "Корень и число", g_rootnum, 2),
    ("cmp", "Сравни a√b и c√d", g_cmp, 3),
    ("ord", "Расставь по порядку", g_ord, 2),
    ("dom", "Когда корень имеет смысл", g_dom, 5),
    ("arg", "Найди аргумент (y = √x)", g_arg, 6),
    ("gsq", "Графически: √x = kx + b", g_gsq, 6),
]
