"""Вероятность и статистика: «Математическое ожидание. Дисперсия» (курс Высоцкого и Ященко, 7–9 классы).

Набор чисел: среднее арифметическое, отклонения, дисперсия (среднее квадратов отклонений), стандартное отклонение.
Случайная величина: таблица распределения, математическое ожидание, справедливая игра, дисперсия, свойства
E(aX+b), D(aX+b) и сумма независимых величин.

Генератор считает ответ «по учебнику» (через отклонения, x·p, готовые свойства). verify() идёт другим путём:
среднее — как точка равновесия (уравнение «сумма отклонений равна 0» в SymPy), дисперсия — через попарные
разности, ожидание — через «урну» из равновероятных билетов, обратные задачи — перебором, свойства — на конкретных
двухточечных величинах с нужными E и D, суммы независимых величин — свёрткой распределений.
"""
from __future__ import annotations

import random
from fractions import Fraction as Fr

import sympy as sp

from common import task

TOPIC = "st-01-expectation-variance"
DIR = "stats8"

PH = "число, например 3, 2,5 или 7/12"
DEF_D = "(дисперсия — среднее арифметическое квадратов отклонений от среднего)"

DAYS = ("день", "дня", "дней")
TIMES = ("раз", "раза", "раз")
PUPILS = ("ученик", "ученика", "учеников")
POINTS = ("очко", "очка", "очков")
CANDY = ("конфету", "конфеты", "конфет")
GRADES = ("оценка", "оценки", "оценок")
NUMS = ("число", "числа", "чисел")


def plural(n, forms) -> str:
    n = abs(int(n)) % 100
    if 11 <= n <= 14:
        return forms[2]
    n %= 10
    return forms[0] if n == 1 else (forms[1] if 2 <= n <= 4 else forms[2])


# ---------- числа: запись ответа и TeX ----------

def _term(q: Fr) -> bool:
    """Конечная десятичная дробь: в знаменателе только двойки и пятёрки."""
    d = q.denominator
    for p in (2, 5):
        while d % p == 0:
            d //= p
    return d == 1


def _dec(q: Fr) -> str:
    """Конечная десятичная дробь с точкой: 2.75, -0.05."""
    sign = "-" if q < 0 else ""
    q = abs(q)
    k = 0
    while (q * 10**k).denominator != 1:
        k += 1
    digits = str(q.numerator * 10**k // q.denominator).rjust(k + 1, "0")
    return sign + (digits[:-k] + "." + digits[-k:] if k else digits)


def ans(q) -> str:
    """Ответ для приложения: 7, 2.75, -0.3 или 35/12."""
    q = Fr(q)
    if q.denominator == 1:
        return str(q.numerator)
    return _dec(q) if _term(q) else f"{q.numerator}/{q.denominator}"


def tx(q, frac: bool = False) -> str:
    """TeX числа: 7, 2{,}75, \\frac{35}{12}; frac=True — обыкновенной дробью даже 1/2."""
    q = Fr(q)
    if q.denominator == 1:
        return str(q.numerator)
    if _term(q) and not frac:
        return _dec(q).replace(".", "{,}")
    sign = "-" if q < 0 else ""
    return f"{sign}\\frac{{{abs(q.numerator)}}}{{{q.denominator}}}"


def txf(q) -> str:
    """Обыкновенная дробь, а если она конечная — ещё и десятичная запись: \\frac{5}{2}=2{,}5."""
    a, b = tx(q, True), tx(q)
    return a if a == b else f"{a}={b}"


def mt(q, frac: bool = False) -> str:
    return f"${tx(q, frac)}$"


def lst(qs, frac: bool = False) -> str:
    """Список чисел для условия: $1$; $2{,}5$; $p$ (строки уже готовые)."""
    return "; ".join(q if isinstance(q, str) else mt(q, frac) for q in qs)


def pt(q, frac: bool = False) -> str:
    """Отрицательное число в скобках: (-3)."""
    s = tx(q, frac)
    return f"({s})" if Fr(q) < 0 else s


def ssum(qs, frac: bool = False) -> str:
    """Сумма со знаками без «+−»: -3+1+4-2."""
    out = []
    for i, q in enumerate(qs):
        q = Fr(q)
        out.append(tx(q, frac) if i == 0 else ("-" if q < 0 else "+") + tx(abs(q), frac))
    return "".join(out)


def pstr(p, frac: bool = False) -> str:
    """Вероятность для рисунка и проверки: 0.25 или 1/4."""
    p = Fr(p)
    if p.denominator == 1 or not frac:
        return ans(p)
    return f"{p.numerator}/{p.denominator}"


def dist_fig(xs, ps, frac: bool = False, **extra) -> dict:
    """Рисунок «таблица распределения»: xs — значения, ps — вероятности (строки «p», «2p» — неизвестные)."""
    props = {"xs": [x if isinstance(x, str) else ans(x) for x in xs], "ps": [p if isinstance(p, str) else pstr(p, frac) for p in ps]}
    props.update(extra)
    return {"id": "dist", "props": props}


def parts(rng: random.Random, k: int, total: int, lo: int = 1):
    """k долей с суммой 1, каждая — целое число k_i/total, k_i ≥ lo."""
    if k * lo > total:
        return None
    for _ in range(200):
        cuts = sorted(rng.sample(range(1, total), k - 1))
        sizes = [b - a for a, b in zip([0] + cuts, cuts + [total])]
        if min(sizes) >= lo:
            return [Fr(s, total) for s in sizes]
    return None


def zero_sum(rng: random.Random, n: int, maxd: int, need=None):
    """n целых отклонений из [−maxd; maxd] с суммой 0, последнее не 0 (порядок не перемешан)."""
    for _ in range(1500):
        d = [rng.randint(-maxd, maxd) for _ in range(n - 1)]
        last = -sum(d)
        if last == 0 or abs(last) > maxd:
            continue
        d.append(last)
        if need is None or need(d):
            return d
    return None


def T(prompt, answer, hint, sol, skills, chk, **extra):
    return task(prompt, ans(answer), "expr", hint, sol, skills, reduce=True, placeholder=PH, chk=chk, **extra)


# ---------- среднее арифметическое ----------

def _mean_task(prompt, xs, extra_sol=()):
    xs = [Fr(x) for x in xs]
    S, n = sum(xs), len(xs)
    mean = S / n
    sol = [f"Сумма: ${ssum(xs)}={tx(S)}$.",
           f"Чисел {n}, поэтому среднее арифметическое равно ${tx(S)}:{n}={tx(mean)}$.",
           *extra_sol,
           f"Проверка: среднее лежит между наименьшим числом ${tx(min(xs))}$ и наибольшим ${tx(max(xs))}$ ✓."]
    return T(prompt, mean, "Сложи все числа и раздели сумму на их количество.", sol, ["st-mean"],
             {"kind": "mean", "data": [ans(x) for x in xs]})


def g_mean(rng: random.Random, level: int):
    if level == 1:
        kind = rng.choice(["plain", "plain", "tasks", "pages", "grades"])
        n = rng.choice([4, 5]) if kind == "grades" else rng.choice([3, 4, 5])
        lo, hi = {"plain": (1, 15), "tasks": (2, 12), "pages": (8, 30), "grades": (2, 5)}[kind]
        xs = next((c for c in ([rng.randint(lo, hi) for _ in range(n)] for _ in range(300)) if sum(c) % n == 0 and len(set(c)) > 1), None)
        if xs is None:
            return None
        nd = f"{n} {plural(n, DAYS)}"
        prompt = {
            "plain": f"Найди среднее арифметическое чисел {lst(xs)}.",
            "tasks": f"Петя {nd} решал задачи: по дням получилось {lst(xs)} задач. Сколько задач в среднем он решал за день?",
            "pages": f"Даша {nd} читала книгу: по дням {lst(xs)} страниц. Сколько страниц в среднем она прочитывала за день?",
            "grades": f"Оценки Маши за неделю: {lst(xs)}. Найди её средний балл.",
        }[kind]
        return _mean_task(prompt, xs)
    if level == 2:
        if rng.random() < 0.5:
            n = rng.choice([4, 5, 6])
            for _ in range(500):
                xs = [rng.randint(-9, 9) for _ in range(n)]
                if sum(x < 0 for x in xs) >= 2 and sum(x > 0 for x in xs) >= 1 and (Fr(sum(xs), n) * 100).denominator == 1:
                    break
            else:
                return None
            prompt = (f"Зимой {n} {plural(n, DAYS)} подряд в 8 утра термометр показывал (в градусах): {lst(xs)}. "
                      "Найди среднюю температуру за эти дни.")
            return _mean_task(prompt, xs, ("Отрицательные температуры складываем со знаком минус: мороз «вычитается».",))
        n = rng.choice([4, 5])
        for _ in range(300):
            xs = [Fr(rng.randint(85, 125), 10) for _ in range(n)]
            if len(set(xs)) == n and (sum(xs) / n * 100).denominator == 1:
                break
        else:
            return None
        who = {4: "Четверо", 5: "Пятеро"}[n]
        return _mean_task(f"{who} ребят пробежали 60 метров. Их время (в секундах): {lst(xs)}. Найди среднее время.", xs)

    kind = rng.choice(["freq", "freq", "removed", "added"])
    if kind == "freq":
        grades = sorted(rng.sample([2, 3, 4, 5], rng.choice([3, 4])), reverse=True)
        for _ in range(400):
            cnts = [rng.randint(1, 9) for _ in grades]
            N = sum(cnts)
            mean = Fr(sum(g * c for g, c in zip(grades, cnts)), N)
            if 8 <= N <= 30 and (mean * 100).denominator == 1 and mean.denominator != 1:
                break
        else:
            return None
        S = sum(g * c for g, c in zip(grades, cnts))
        said = [f"«{g}» получили ${c}$ {plural(c, PUPILS)}" if i == 0 else f"«{g}» — ${c}$" for i, (g, c) in enumerate(zip(grades, cnts))]
        prompt = f"За контрольную {', '.join(said)}. Найди средний балл класса."
        prods = "+".join(f"{g}\\cdot {c}" for g, c in zip(grades, cnts))
        sol = [f"Сумма всех оценок: ${prods}={'+'.join(str(g * c) for g, c in zip(grades, cnts))}={S}$.",
               f"Всего учеников: ${'+'.join(map(str, cnts))}={N}$.",
               f"Средний балл: ${S}:{N}={tx(mean)}$.",
               f"Подвох: делим на число учеников (${N}$), а не на число разных оценок (${len(grades)}$)."]
        return T(prompt, mean, "Каждую оценку умножь на число учеников, которые её получили, сложи и раздели на число **всех** учеников.",
                 sol, ["st-mean", "st-mean-freq"], {"kind": "freq", "vals": grades, "cnts": cnts},
                 fig=dist_fig(grades, cnts, xh="оценка", ph="учеников"))
    if kind == "removed":
        for _ in range(300):
            n = rng.randint(4, 9)
            m1 = rng.randint(4, 15)
            m2 = m1 + rng.choice([-3, -2, -1, 1, 2, 3])
            r = n * m1 - (n - 1) * m2
            if m2 > 0 and 0 < r <= 60 and r != m1:
                break
        else:
            return None
        prompt = (f"Среднее арифметическое ${n}$ чисел равно ${m1}$. Одно число вычеркнули, и среднее арифметическое "
                  f"оставшихся стало равно ${m2}$. Какое число вычеркнули?")
        sol = [f"Сумма всех ${n}$ чисел равна среднему, умноженному на количество: ${n}\\cdot {m1}={n * m1}$.",
               f"Сумма оставшихся ${n - 1}$ чисел: ${n - 1}\\cdot {m2}={(n - 1) * m2}$.",
               f"Вычеркнули число ${n * m1}-{(n - 1) * m2}={r}$.",
               f"Подвох: ответ — не разность средних ${m1}-{m2}$, а разность сумм."]
        return T(prompt, r, "Средние не вычитают. Найди сумму всех чисел и сумму оставшихся: среднее, умноженное на количество.",
                 sol, ["st-mean"], {"kind": "removed", "n": n, "m1": ans(m1), "m2": ans(m2)})
    for _ in range(500):
        n = rng.randint(3, 9)
        S1 = rng.randint(2 * n, 5 * n)
        m1 = Fr(S1, n)
        a = rng.randint(3, 5)
        m2 = Fr(S1 + a, n + 1)
        if (m1 * 10).denominator == 1 and a > m1 and (m2 * 100).denominator == 1 and m2 != m1:
            break
    else:
        return None
    prompt = (f"У Пети ${n}$ {plural(n, GRADES)}, их среднее арифметическое равно {mt(m1)}. "
              f"Какую оценку ему нужно получить, чтобы среднее стало равно {mt(m2)}?")
    sol = [f"Сейчас сумма оценок ${n}\\cdot {tx(m1)}={S1}$.",
           f"Чтобы среднее ${n + 1}$ оценок было ${tx(m2)}$, их сумма должна быть ${n + 1}\\cdot {tx(m2)}={S1 + a}$.",
           f"Новая оценка: ${S1 + a}-{S1}={a}$.",
           "Подвох: нужная оценка — не разность средних, а разность сумм."]
    return T(prompt, a, "Найди сумму оценок сейчас и сумму, которая нужна (среднее, умноженное на новое количество оценок).",
             sol, ["st-mean"], {"kind": "added", "n": n, "m1": ans(m1), "m2": ans(m2), "grade": True})


# ---------- отклонения от среднего ----------

def _numfind(rng: random.Random, n: int, lo: int, hi: int, mean_den: int, need_neg: bool):
    for _ in range(800):
        known = [rng.randint(lo, hi) for _ in range(n - 1)]
        M = Fr(rng.randint(lo * mean_den, hi * mean_den), mean_den)
        a = n * M - sum(known)
        if a.denominator != 1 or not (lo - 5 <= a <= hi + 5) or a in known:
            continue
        if need_neg and (min(known) >= 0 or M.denominator == 1):
            continue
        break
    else:
        return None
    pos = rng.randrange(n)
    items = [mt(k) for k in known]
    items.insert(pos, "$a$")
    K = sum(known)
    prompt = f"Среднее арифметическое чисел {'; '.join(items)} равно {mt(M)}. Найди $a$."
    sol = [f"Сумма всех ${n}$ чисел равна среднему, умноженному на их количество: ${n}\\cdot {pt(M)}={tx(n * M)}$.",
           f"Сумма известных чисел: ${ssum(known)}={tx(K)}$.",
           f"$a={tx(n * M)}-{pt(K)}={tx(a)}$.",
           f"Проверка: среднее чисел {lst(sorted(known + [a]))} равно ${tx(M)}$ ✓."]
    return T(prompt, a, "Сумма всех чисел равна среднему, умноженному на их количество. Вычти из неё известные числа.", sol,
             ["st-mean", "st-deviation"], {"kind": "numfind", "known": [ans(k) for k in known], "n": n, "mean": ans(M)})


def g_dev(rng: random.Random, level: int):
    if level == 1:
        n = rng.choice([3, 4, 5])
        xs = next((c for c in ([rng.randint(1, 15) for _ in range(n)] for _ in range(300)) if sum(c) % n == 0 and len(set(c)) > 1), None)
        if xs is None:
            return None
        M = sum(xs) // n
        x = rng.choice([v for v in xs if v != M])
        d = x - M
        side = "меньше среднего — отклонение отрицательное" if d < 0 else "больше среднего — отклонение положительное"
        prompt = f"Среднее арифметическое набора {lst(xs)} равно ${M}$. Найди отклонение числа ${x}$ от среднего."
        sol = [f"Отклонение = число − среднее: ${x}-{M}={d}$.", f"Число ${x}$ {side}."]
        return T(prompt, d, "Отклонение — это число минус среднее. Следи за знаком.", sol, ["st-deviation"],
                 {"kind": "dev1", "data": [ans(v) for v in xs], "mean": ans(M), "x": ans(x)})
    if level == 2:
        if rng.random() < 0.5:
            n = rng.choice([4, 5])
            d = zero_sum(rng, n, 6)
            if d is None:
                return None
            shown, hidden = d[:-1], d[-1]
            rng.shuffle(shown)
            prompt = f"Отклонения ${n}$ чисел от их среднего арифметического равны {lst(shown)} и ещё одному, неизвестному числу. Найди неизвестное отклонение."
            sol = ["Сумма всех отклонений от среднего всегда равна $0$.",
                   f"Сумма известных отклонений: ${ssum(shown)}={tx(sum(shown))}$.",
                   f"Значит, неизвестное отклонение равно ${tx(hidden)}$: тогда вся сумма станет $0$."]
            return T(prompt, hidden, "Вспомни, чему всегда равна сумма всех отклонений от среднего.", sol, ["st-deviation"],
                     {"kind": "devmiss", "devs": [ans(v) for v in shown]})
        return _numfind(rng, rng.choice([4, 5]), 1, 20, 1, False)

    kind = rng.choice(["sum", "num", "find"])
    if kind == "sum":
        n = rng.choice([4, 5])
        xs = [Fr(rng.randint(10, 150), 10) for _ in range(n)]
        if len(set(xs)) < n:
            return None
        M = sum(xs) / n
        devs = [x - M for x in xs]
        sol = ["Можно ничего не считать: сумма отклонений от среднего **всегда** равна $0$.",
               "Числа меньше среднего «недобирают» до него ровно столько, сколько числа больше среднего «перебирают» (вспомни линейку с опорой)."]
        if (M * 100).denominator == 1:
            sol.append(f"Проверка: среднее равно ${tx(M)}$, отклонения {lst(devs)}, их сумма $0$ ✓.")
        return T(f"Найди сумму отклонений чисел {lst(xs)} от их среднего арифметического.", 0,
                 "Не спеши считать среднее: вспомни, какое свойство есть у отклонений от среднего.", sol, ["st-deviation"],
                 {"kind": "devsum", "data": [ans(x) for x in xs]})
    if kind == "num":
        n = rng.choice([4, 5])
        d = zero_sum(rng, n, 6)
        if d is None:
            return None
        M = rng.randint(5, 30)
        shown, hidden = d[:-1], d[-1]
        rng.shuffle(shown)
        x = M + hidden
        prompt = (f"Среднее арифметическое ${n}$ чисел равно ${M}$. Отклонения ${n - 1}$ из них от среднего равны {lst(shown)}. "
                  "Найди оставшееся число (само число, а не его отклонение).")
        sol = ["Сумма всех отклонений от среднего равна $0$.",
               f"Сумма известных: ${ssum(shown)}={tx(sum(shown))}$, значит, у оставшегося числа отклонение ${tx(hidden)}$.",
               f"Само число = среднее + отклонение: ${M}+{pt(hidden)}={x}$.",
               "Подвох: спрашивают число, а не отклонение."]
        return T(prompt, x, "Сначала найди недостающее отклонение (сумма всех отклонений равна 0), потом само число: среднее плюс отклонение.",
                 sol, ["st-deviation"], {"kind": "devnum", "mean": ans(M), "devs": [ans(v) for v in shown]})
    return _numfind(rng, rng.choice([4, 5, 6]), -10, 15, rng.choice([2, 4, 5]), True)


# ---------- дисперсия набора чисел ----------

def _var_solution(xs, shown_mean: str | None = None):
    xs = [Fr(x) for x in xs]
    n = len(xs)
    M = sum(xs) / n
    devs = [x - M for x in xs]
    sq = [v * v for v in devs]
    D = sum(sq) / n
    sol = [shown_mean or f"Среднее: $({ssum(xs)}):{n}={tx(M)}$.",
           f"Отклонения от среднего: {lst(devs)} (их сумма $0$ ✓).",
           f"Квадраты отклонений: {lst(sq)}.",
           f"Дисперсия — среднее квадратов: $({ssum(sq)}):{n}={tx(D)}$."]
    return D, sol


HINT_D = "Четыре шага: найди среднее, потом отклонения от него, потом квадраты отклонений, потом среднее этих квадратов."
SQUARES = {1: 1, 4: 2, 9: 3, 16: 4, 25: 5}


def g_vard(rng: random.Random, level: int):
    if level in (1, 2):
        if level == 1:
            n = rng.choice([3, 4, 5])
            d = zero_sum(rng, n, 4, lambda v: sum(t * t for t in v) % n == 0 and sum(t * t for t in v) // n <= 12)
            M = rng.randint(4, 12)
        else:
            n = rng.choice([4, 5, 6])
            d = zero_sum(rng, n, 5, lambda v: (Fr(sum(t * t for t in v), n) * 100).denominator == 1 and Fr(sum(t * t for t in v), n).denominator != 1)
            M = rng.randint(-2, 12)
        if d is None:
            return None
        xs = [M + t for t in d]
        rng.shuffle(xs)
        D, sol = _var_solution(xs)
        return T(f"Найди дисперсию набора чисел {lst(xs)} {DEF_D}.", D, HINT_D, sol, ["st-variance"], {"kind": "var", "data": [ans(x) for x in xs]})

    kind = rng.choice(["freq", "sigma", "shift"])
    if kind == "freq":
        k = rng.choice([2, 3])
        for _ in range(600):
            vals = sorted(rng.sample(range(0, 13), k))
            cnts = [rng.randint(1, 5) for _ in range(k)]
            N = sum(cnts)
            M = Fr(sum(v * c for v, c in zip(vals, cnts)), N)
            D = sum(c * (v - M) ** 2 for v, c in zip(vals, cnts)) / N
            if 4 <= N <= 12 and (M * 2).denominator == 1 and (D * 100).denominator == 1 and 0 < D <= 30:
                break
        else:
            return None
        said = [f"число ${v}$ встречается ${c}$ {plural(c, TIMES)}" if i == 0 else f"число ${v}$ — ${c}$ {plural(c, TIMES)}" for i, (v, c) in enumerate(zip(vals, cnts))]
        prompt = f"В наборе ${N}$ {plural(N, NUMS)}: {', '.join(said)}. Найди дисперсию набора {DEF_D}."
        msum = "+".join(f"{v}\\cdot {c}" for v, c in zip(vals, cnts))
        ssq = "+".join(f"{tx((v - M) ** 2)}\\cdot {c}" for v, c in zip(vals, cnts))
        sol = [f"Среднее: $({msum}):{N}={tx(M)}$.",
               "Отклонения: " + ", ".join(f"у числа ${v}$ — ${tx(v - M)}$" for v in vals) + ".",
               "Квадраты отклонений: " + ", ".join(f"${tx((v - M) ** 2)}$ (${c}$ {plural(c, TIMES)})" for v, c in zip(vals, cnts)) + ".",
               f"Дисперсия: $({ssq}):{N}={tx(D)}$.",
               "Подвох: каждое число учитываем столько раз, сколько оно встречается."]
        return T(prompt, D, "Распиши набор полностью: каждое число столько раз, сколько оно встречается. Дальше — как обычно.",
                 sol, ["st-variance", "st-mean-freq"], {"kind": "varfreq", "vals": vals, "cnts": cnts},
                 fig=dist_fig(vals, cnts, xh="число", ph="сколько раз"))
    if kind == "sigma":
        n = rng.choice([4, 5, 6])
        d = zero_sum(rng, n, 7, lambda v: Fr(sum(t * t for t in v), n) in SQUARES)
        if d is None:
            return None
        M = rng.randint(6, 20)
        xs = [M + t for t in d]
        rng.shuffle(xs)
        D, sol = _var_solution(xs)
        s = SQUARES[int(D)]
        sol += [f"Стандартное отклонение — корень из дисперсии: $\\sigma=\\sqrt{{{tx(D)}}}={s}$.",
                "Подвох: спросили не дисперсию, а стандартное отклонение — в конце извлекаем корень."]
        return T(f"Найди стандартное отклонение $\\sigma$ набора чисел {lst(xs)}.", s,
                 "Сначала найди дисперсию — среднее квадратов отклонений от среднего, потом извлеки из неё квадратный корень.",
                 sol, ["st-variance", "st-sigma"], {"kind": "sigma", "data": [ans(x) for x in xs]})
    B = rng.choice([100, 200, 500, 1000, 2000])
    n = rng.choice([3, 4, 5])
    d = zero_sum(rng, n, 4, lambda v: (Fr(sum(t * t for t in v), n) * 100).denominator == 1)
    if d is None:
        return None
    m0 = rng.randint(1, 9)
    xs = [B + m0 + t for t in d]
    rng.shuffle(xs)
    shown_mean = f"Среднее удобно искать так: вычтем из всех чисел ${B}$, получим {lst([x - B for x in xs])} со средним ${m0}$; значит, среднее набора ${B + m0}$."
    D, sol = _var_solution(xs, shown_mean)
    sol.append("Подвох: числа большие, а дисперсия маленькая — она зависит только от того, насколько числа далеко от среднего.")
    return T(f"Найди дисперсию набора чисел {lst(xs)} {DEF_D}.", D,
             "Числа большие, но отличаются от среднего совсем немного. Найди среднее и посмотри, на сколько каждое число от него отличается.",
             sol, ["st-variance"], {"kind": "var", "data": [ans(x) for x in xs]})


# ---------- таблица распределения: недостающая вероятность ----------

def _ptex(u, frac: bool) -> str:
    return f"${u}$" if isinstance(u, str) else mt(u, frac)


def _peq(shown, frac: bool) -> str:
    """0{,}2+p+0{,}3 для уравнения «сумма вероятностей равна 1»."""
    return "+".join(u if isinstance(u, str) else tx(u, frac) for u in shown)


def _values(rng: random.Random, k: int, lo: int, hi: int, need_neg: bool = False):
    for _ in range(100):
        xs = sorted(rng.sample(range(lo, hi + 1), k))
        if not need_neg or xs[0] < 0:
            return xs
    return None


def _dist_prompt(xs, shown, frac: bool, name: str = "X") -> str:
    return f"Случайная величина ${name}$ принимает значения {lst(xs)} с вероятностями {'; '.join(_ptex(u, frac) for u in shown)} соответственно."


def g_pfill(rng: random.Random, level: int):
    frac = False
    if level == 1:
        xs = _values(rng, 3, 0, 10)
        ps = parts(rng, 3, 10)
    elif level == 2:
        if rng.random() < 0.5:
            xs, ps = _values(rng, 4, -3, 10), parts(rng, 4, 20)
        else:
            frac = True
            k = rng.choice([3, 4])
            xs, ps = _values(rng, k, 0, 10), parts(rng, k, rng.choice([6, 8, 12]))
    else:
        return _pfill3(rng)
    if not xs or not ps:
        return None
    pos = rng.randrange(len(xs))
    shown = list(ps)
    shown[pos] = "p"
    known = [q for i, q in enumerate(ps) if i != pos]
    p = ps[pos]
    sol = [f"Сумма всех вероятностей в таблице равна $1$: ${_peq(shown, frac)}=1$.",
           f"$p=1-({ssum(known, frac)})=1-{tx(sum(known), frac)}={tx(p, frac)}$."]
    if frac and _term(p) and p.denominator != 1:
        sol.append(f"Можно записать и десятичной дробью: $p={tx(p)}$.")
    return T(f"{_dist_prompt(xs, shown, frac)} Найди $p$.", p, "Сумма всех вероятностей в таблице распределения равна 1.", sol,
             ["st-distribution"], {"kind": "pfill", "xs": xs, "ps": [u if isinstance(u, str) else pstr(u, frac) for u in shown], "frac": frac},
             fig=dist_fig(xs, shown, frac))


OPS = {">": ("больше", ">"), "<": ("меньше", "<"), ">=": ("не меньше", "\\ge "), "<=": ("не больше", "\\le ")}


def _holds(x, op, t) -> bool:
    return {">": x > t, "<": x < t, ">=": x >= t, "<=": x <= t}[op]


def _pfill3(rng: random.Random):
    kind = rng.choice(["twin", "ratio", "event"])
    if kind == "twin":
        xs = _values(rng, 4, 0, 10)
        for _ in range(100):
            k1, k2 = rng.randint(1, 6), rng.randint(1, 6)
            rest = 10 - k1 - k2
            if rest >= 2 and rest % 2 == 0:
                break
        else:
            return None
        p = Fr(rest, 20)
        pos = sorted(rng.sample(range(4), 2))
        it = iter([Fr(k1, 10), Fr(k2, 10)])
        shown = ["p" if i in pos else next(it) for i in range(4)]
        known = [u for u in shown if not isinstance(u, str)]
        sol = [f"Сумма вероятностей равна $1$: ${_peq(shown, False)}=1$.",
               f"$2p=1-({ssum(known)})={tx(2 * p)}$.",
               f"$p={tx(2 * p)}:2={tx(p)}$.",
               "Подвох: неизвестная вероятность $p$ встречается в таблице два раза, поэтому остаток делим пополам."]
        return T(f"{_dist_prompt(xs, shown, False)} Найди $p$.", p, "Сумма всех вероятностей равна 1. Сколько раз в эту сумму входит $p$?", sol,
                 ["st-distribution"], {"kind": "pfill", "xs": xs, "ps": [u if isinstance(u, str) else pstr(u) for u in shown], "frac": False},
                 fig=dist_fig(xs, shown))
    if kind == "ratio":
        xs = _values(rng, 3, 0, 10)
        for _ in range(200):
            q = Fr(rng.randint(1, 7), 10)
            c = rng.choice([2, 3, 4])
            p = (1 - q) / (1 + c)
            if (p * 100).denominator == 1:
                break
        else:
            return None
        order = [q, "p", f"{c}p"]
        rng.shuffle(order)
        sol = [f"Сумма вероятностей равна $1$: ${_peq(order, False)}=1$.",
               f"Все $p$ вместе: $p+{c}p={c + 1}p$, значит, ${c + 1}p=1-{tx(q)}={tx(1 - q)}$.",
               f"$p={tx(1 - q)}:{c + 1}={tx(p)}$.",
               f"Подвох: одна вероятность в ${c}$ раза больше другой, поэтому $p$ входит в сумму ${c + 1}$ раза."]
        return T(f"{_dist_prompt(xs, order, False)} Найди $p$.", p,
                 f"Сумма всех вероятностей равна 1. Сложи все слагаемые с $p$: $p+{c}p$.", sol, ["st-distribution"],
                 {"kind": "pfill", "xs": xs, "ps": [u if isinstance(u, str) else pstr(u) for u in order], "frac": False},
                 fig=dist_fig(xs, order))
    xs = _values(rng, 4, -2, 9)
    ps = parts(rng, 4, rng.choice([10, 20]))
    if not xs or not ps:
        return None
    pos = rng.randrange(4)
    shown = list(ps)
    shown[pos] = "p"
    op = rng.choice(list(OPS))
    t = rng.choice(xs[1:3])
    good = [i for i, x in enumerate(xs) if _holds(x, op, t)]
    if not good or len(good) == 4:
        return None
    want = sum(ps[i] for i in good)
    word, sym = OPS[op]
    known = [q for i, q in enumerate(ps) if i != pos]
    sol = []
    if pos in good:
        sol.append(f"Сначала найдём $p$: $p=1-({ssum(known)})={tx(ps[pos])}$.")
    else:
        sol.append(f"Неизвестная вероятность $p$ относится к значению ${xs[pos]}$, а оно условию не подходит, поэтому $p$ можно даже не искать.")
    sol += [f"Условию «$X$ {word} ${t}$» подходят значения {lst([xs[i] for i in good])}.",
            f"$P(X{sym}{t})={ssum([ps[i] for i in good])}={tx(want)}$."]
    if pos in good:
        sol.append("Подвох: сначала нужна недостающая вероятность, а потом — сумма вероятностей подходящих значений.")
    prompt = f"{_dist_prompt(xs, shown, False)} Найди вероятность того, что $X$ {word} ${t}$, то есть $P(X{sym}{t})$."
    return T(prompt, want, "Вероятность события равна сумме вероятностей значений, которые ему подходят. Неизвестную $p$ найди из того, что сумма всех вероятностей равна 1.",
             sol, ["st-distribution"], {"kind": "pevent", "xs": xs, "ps": [u if isinstance(u, str) else pstr(u) for u in shown], "op": op, "t": t},
             fig=dist_fig(xs, shown))


# ---------- математическое ожидание по таблице ----------

def _ex_lines(xs, ps, frac: bool, name: str = "X"):
    prods = [Fr(x) * p for x, p in zip(xs, ps)]
    E = sum(prods)
    terms = "+".join(f"{pt(x)}\\cdot {tx(p, frac)}" for x, p in zip(xs, ps))
    lines = [f"${'E(' + name + ')'}={terms}$", f"$={ssum(prods, frac)}={txf(E) if frac else tx(E)}$."]
    return E, lines


HINT_E = "Умножь каждое значение на его вероятность и сложи все произведения."


def _e_line(xs, ps, name: str = "X") -> str:
    """Одной строкой: $E(X)=0\\cdot 0{,}4+3\\cdot 0{,}6=0+1{,}8=1{,}8$."""
    prods = [Fr(x) * p for x, p in zip(xs, ps)]
    terms = "+".join(f"{pt(x)}\\cdot {tx(p)}" for x, p in zip(xs, ps))
    return f"$E({name})={terms}={ssum(prods)}={tx(sum(prods))}$."


def g_ex(rng: random.Random, level: int):
    frac = False
    pct = False
    unknown = None
    if level == 1:
        k = rng.choice([2, 3, 3])
        xs, ps = _values(rng, k, 0, 10), parts(rng, k, 10)
    elif level == 2:
        if rng.random() < 0.5:
            k = rng.choice([3, 4])
            xs, ps = _values(rng, k, -5, 10, need_neg=True), parts(rng, k, 20)
        else:
            frac = True
            k = rng.choice([3, 4])
            xs, ps = _values(rng, k, 0, 12), parts(rng, k, rng.choice([4, 6, 8, 12]))
    else:
        if rng.random() < 0.5:
            k = rng.choice([3, 4])
            xs, ps = _values(rng, k, -4, 10), parts(rng, k, rng.choice([10, 20]))
            unknown = rng.randrange(k) if ps else None
        else:
            pct = True
            k = 3
            xs, ps = _values(rng, k, -5, 10), parts(rng, k, 20)
    if not xs or not ps:
        return None
    E, lines = _ex_lines(xs, ps, frac)
    if pct:
        shown = [f"${int(p * 100)}\\%$" for p in ps]
        prompt = f"Случайная величина $X$ принимает значения {lst(xs)} с вероятностями {'; '.join(shown)} соответственно. Найди математическое ожидание $E(X)$."
        sol = ["Переведём проценты в доли: " + ", ".join(f"${int(p * 100)}\\%={tx(p)}$" for p in ps) + ".", *lines,
               "Подвох: вероятности даны в процентах, а умножать нужно на доли (иначе ответ выйдет в 100 раз больше)."]
        return T(prompt, E, "Сначала переведи проценты в доли: $25\\%=0{,}25$. Потом умножь значения на вероятности и сложи.", sol,
                 ["st-expectation"], {"kind": "ex", "xs": xs, "ps": [f"{int(p * 100)}%" for p in ps], "pct": True},
                 fig=dist_fig(xs, [f"{int(p * 100)}%" for p in ps]))
    shown = list(ps)
    sol = list(lines)
    hint = HINT_E
    skills = ["st-expectation"]
    if unknown is not None:
        shown[unknown] = "p"
        known = [q for i, q in enumerate(ps) if i != unknown]
        sol = [f"Сначала недостающая вероятность: $p=1-({ssum(known)})={tx(ps[unknown])}$.", *lines,
               "Подвох: без $p$ ожидание не посчитать, поэтому сначала находим её из того, что сумма вероятностей равна $1$."]
        hint = "В таблице есть неизвестная вероятность $p$: найди её из того, что сумма вероятностей равна 1. Потом считай $E(X)$."
        skills = ["st-expectation", "st-distribution"]
    return T(f"{_dist_prompt(xs, shown, frac)} Найди математическое ожидание $E(X)$.", E, hint, sol, skills,
             {"kind": "ex", "xs": xs, "ps": [u if isinstance(u, str) else pstr(u, frac) for u in shown], "frac": frac},
             fig=dist_fig(xs, shown, frac))


# ---------- игры: средний выигрыш и справедливая цена ----------

DIE_EVENTS = [("шестёрка", 1), ("единица", 1), ("пятёрка или шестёрка", 2), ("число меньше $3$", 2),
              ("число, кратное $3$", 2), ("чётное число", 3), ("нечётное число", 3), ("число больше $2$", 4)]


def g_game(rng: random.Random, level: int):
    sk = ["st-fair-game", "st-expectation"]
    if level == 1:
        kind = rng.choice(["coin", "die", "lottery"])
        if kind == "coin":
            k = rng.choice([2, 4, 6, 8, 10, 12, 20, 30, 40, 50, 60, 100, 5, 15, 25])
            E = Fr(k, 2)
            prompt = (f"Игра: бросаем монету. Если выпадет орёл, ты получаешь ${k}$ {plural(k, POINTS)}, если решка — ничего. "
                      "Сколько очков в среднем приносит одна игра? Найди математическое ожидание выигрыша.")
            sol = [f"Выигрыш $X$ равен ${k}$ (орёл) или $0$ (решка), каждый с вероятностью $0{{,}}5$.",
                   f"$E(X)={k}\\cdot 0{{,}}5+0\\cdot 0{{,}}5={tx(E)}$.",
                   f"За много игр в среднем выходит ${tx(E)}$ за игру, хотя в одной игре так никогда не бывает: там ${k}$ или $0$."]
            return T(prompt, E, "Умножь выигрыш на вероятность орла и прибавь ноль, умноженный на вероятность решки.", sol, sk,
                     {"kind": "game", "xs": [k, 0], "ps": ["1/2", "1/2"], "ask": "E"})
        if kind == "die":
            k = 6 * rng.randint(1, 10)
            prompt = f"Бросаем игральный кубик. Если выпадет шестёрка, ты получаешь ${k}$ {plural(k, CANDY)}, иначе ничего. Сколько конфет в среднем приходится на один бросок?"
            sol = ["Шестёрка выпадает с вероятностью $\\frac{1}{6}$, остальные грани — с вероятностью $\\frac{5}{6}$.",
                   f"$E(X)={k}\\cdot\\frac{{1}}{{6}}+0\\cdot\\frac{{5}}{{6}}={k // 6}$.",
                   f"Проверка «на пальцах»: за $600$ бросков шестёрка выпадет примерно $100$ раз — это $100\\cdot {k}$ конфет, по ${k // 6}$ на бросок."]
            return T(prompt, k // 6, "Математическое ожидание: выигрыш, умноженный на вероятность шестёрки.", sol, sk,
                     {"kind": "game", "xs": [k, 0], "ps": ["1/6", "5/6"], "ask": "E"})
        N = rng.choice([10, 20, 50, 100, 200, 500, 1000])
        P = N * rng.choice([1, 2, 3, 4, 5, 10, 20]) // rng.choice([1, 1, 2])
        if P > 20000:
            return None
        E = Fr(P, N)
        prompt = f"В лотерее ${N}$ билетов, и только $1$ из них выигрышный: приз ${P}$ руб. При какой цене билета игра будет справедливой?"
        sol = ["Справедливая цена равна математическому ожиданию выигрыша $E(X)$.",
               f"Выигрыш ${P}$ руб. выпадает с вероятностью $\\frac{{1}}{{{N}}}$, иначе выигрыш $0$.",
               f"$E(X)={P}\\cdot\\frac{{1}}{{{N}}}={tx(E)}$ руб.",
               f"Проверка «на пальцах»: если раскупят все ${N}$ билетов по ${tx(E)}$ руб., соберут ровно ${P}$ руб. — столько стоит приз."]
        return T(prompt, E, "Справедливая цена — это средний выигрыш на один билет: призовой фонд, делённый на число билетов.", sol, sk,
                 {"kind": "lottery", "N": N, "prizes": [[P, 1]], "ask": "fair"})
    if level == 2:
        if rng.random() < 0.5:
            for _ in range(300):
                P1, P2 = rng.choice([100, 200, 500, 1000]), rng.choice([10, 20, 30, 50])
                a, b = Fr(rng.randint(1, 5), 100), Fr(rng.randint(1, 6), 20)
                C = rng.choice(range(5, 55, 5))
                E = P1 * a + P2 * b
                if P2 < P1 and a + b < 1 and E != C and abs(E - C) <= 30 and (E * 100).denominator == 1:
                    break
            else:
                return None
            net = E - C
            prompt = (f"Лотерейный билет стоит ${C}$ руб. С вероятностью {mt(a)} на билет выпадает выигрыш ${P1}$ руб., "
                      f"с вероятностью {mt(b)} — выигрыш ${P2}$ руб., иначе выигрыша нет. Найди средний чистый выигрыш "
                      "с одного билета (выигрыш минус цена билета). Если в среднем игрок теряет деньги, ответ отрицательный.")
            sol = [f"Средний выигрыш: $E(X)={P1}\\cdot {tx(a)}+{P2}\\cdot {tx(b)}+0\\cdot {tx(1 - a - b)}={tx(E)}$ руб.",
                   f"Чистый выигрыш: ${tx(E)}-{C}={tx(net)}$ руб.",
                   "Минус значит: в среднем игрок теряет деньги, игра выгодна устроителю лотереи." if net < 0 else "Плюс значит: в среднем игрок остаётся в выигрыше."]
            return T(prompt, net, "Найди средний выигрыш $E(X)$, потом вычти цену билета.", sol, sk,
                     {"kind": "game", "xs": [P1, P2, 0], "ps": [pstr(a), pstr(b), pstr(1 - a - b)], "price": C, "ask": "net"})
        for _ in range(300):
            N = rng.choice([100, 200, 500, 1000])
            P1, c1 = rng.choice([500, 1000, 2000, 5000]), rng.randint(1, 3)
            P2, c2 = rng.choice([50, 100, 200]), rng.choice([2, 4, 5, 10, 20])
            fund = P1 * c1 + P2 * c2
            E = Fr(fund, N)
            if (E * 10).denominator == 1 and c1 + c2 < N:
                break
        else:
            return None
        prompt = f"Выпущено ${N}$ лотерейных билетов: на ${c1}$ из них выигрыш ${P1}$ руб., на ${c2}$ — выигрыш ${P2}$ руб., остальные без выигрыша. Какая цена билета справедлива?"
        sol = [f"Все выигрыши вместе: ${c1}\\cdot {P1}+{c2}\\cdot {P2}={fund}$ руб.",
               f"На один билет в среднем приходится ${fund}:{N}={tx(E)}$ руб. — это и есть $E(X)$.",
               "Справедливая цена билета равна $E(X)$: тогда в среднем никто не выигрывает и не проигрывает."]
        return T(prompt, E, "Сложи все выигрыши и раздели на число билетов: столько в среднем «приходится» на один билет.", sol, sk,
                 {"kind": "lottery", "N": N, "prizes": [[P1, c1], [P2, c2]], "ask": "fair"})

    kind = rng.choice(["loss", "prize", "mixed"])
    if kind == "loss":
        for _ in range(300):
            N = rng.choice([100, 200, 500, 1000])
            P1, c1 = rng.choice([500, 1000, 2000]), rng.randint(1, 3)
            P2, c2 = rng.choice([50, 100, 200]), rng.choice([2, 4, 5, 10])
            E = Fr(P1 * c1 + P2 * c2, N)
            C = int(E) + rng.choice([1, 2, 3, 5, 10])
            k = rng.choice([10, 20, 50, 100])
            if (E * 10).denominator == 1 and c1 + c2 < N:
                break
        else:
            return None
        loss = k * (C - E)
        prompt = (f"Выпущено ${N}$ лотерейных билетов: на ${c1}$ из них выигрыш ${P1}$ руб., на ${c2}$ — ${P2}$ руб., остальные без "
                  f"выигрыша. Билет стоит ${C}$ руб. Сколько рублей в среднем потеряет игрок, если купит ${k}$ билетов?")
        sol = [f"Средний выигрыш на билет: $E(X)=({c1}\\cdot {P1}+{c2}\\cdot {P2}):{N}={tx(E)}$ руб.",
               f"С каждого билета игрок в среднем теряет ${C}-{tx(E)}={tx(C - E)}$ руб.",
               f"За ${k}$ билетов: ${k}\\cdot {tx(C - E)}={tx(loss)}$ руб.",
               "Подвох: спрашивают про много билетов и про потерю, поэтому умножаем, а ответ — положительное число."]
        return T(prompt, loss, "Найди средний выигрыш на один билет, сравни с ценой и умножь разницу на число билетов.", sol, sk,
                 {"kind": "lottery", "N": N, "prizes": [[P1, c1], [P2, c2]], "price": C, "k": k, "ask": "loss"})
    if kind == "prize":
        name, k = rng.choice(DIE_EVENTS)
        C = rng.randint(2, 30)
        p = Fr(k, 6)
        prize = C / p
        if prize.denominator > 2:
            return None
        frac_s = f"\\frac{{{k}}}{{6}}" + (f"=\\frac{{{p.numerator}}}{{{p.denominator}}}" if p.denominator != 6 else "")
        prompt = (f"Игра: бросают игральный кубик. Если выпадет {name}, игрок получает приз, иначе ничего. Участие в игре стоит "
                  f"${C}$ {plural(C, POINTS)}. Каким должен быть приз, чтобы игра была справедливой?")
        sol = [f"Подходящих граней ${k}$ из $6$, вероятность выигрыша ${frac_s}$.",
               f"Игра справедлива, если средний выигрыш равен цене участия. Обозначим приз буквой $x$: $x\\cdot {tx(p, True)}={C}$.",
               f"$x={C}:{tx(p, True)}={tx(prize)}$.",
               f"Проверка: $E(X)={tx(prize)}\\cdot {tx(p, True)}={C}$ — ровно цена участия ✓."]
        return T(prompt, prize, "В справедливой игре средний выигрыш (приз, умноженный на вероятность выигрыша) равен цене участия.", sol, sk,
                 {"kind": "prize", "faces": k, "price": C})
    for _ in range(200):
        a = rng.randint(2, 20) * 3
        b = rng.randint(1, 10) * 3
        if a != b:
            break
    E = Fr(a - b, 6)
    prompt = (f"Игра с кубиком: если выпадет $6$, ты получаешь ${a}$ руб., если выпадет $1$ — сам платишь ${b}$ руб., "
              "в остальных случаях ничего. Найди средний выигрыш за одну игру.")
    sol = [f"Выигрыш $X$ принимает значения ${a}$, ${-b}$ (заплатить — это отрицательный выигрыш) и $0$ с вероятностями $\\frac{{1}}{{6}}$, $\\frac{{1}}{{6}}$ и $\\frac{{4}}{{6}}$.",
           f"$E(X)={a}\\cdot\\frac{{1}}{{6}}+(-{b})\\cdot\\frac{{1}}{{6}}+0\\cdot\\frac{{4}}{{6}}=\\frac{{{a}-{b}}}{{6}}={tx(E)}$.",
           "Минус значит: в среднем игра невыгодна." if E < 0 else "Плюс значит: в среднем игра выгодна.",
           "Подвох: проигрыш входит в математическое ожидание со знаком минус."]
    return T(prompt, E, "Проигрыш — это отрицательный выигрыш. Каждое значение умножь на вероятность и сложи.", sol, sk,
             {"kind": "game", "xs": [a, -b, 0], "ps": ["1/6", "1/6", "2/3"], "ask": "E"})


# ---------- дисперсия случайной величины ----------

def _varx_lines(xs, ps):
    E = sum(Fr(x) * p for x, p in zip(xs, ps))
    devs = [Fr(x) - E for x in xs]
    terms = "+".join(f"{pt(d)}^2\\cdot {tx(p)}" for d, p in zip(devs, ps))
    D = sum(d * d * p for d, p in zip(devs, ps))
    lines = [_e_line(xs, ps),
             "Отклонения от $E(X)$: " + "; ".join(f"${x}-{pt(E)}={tx(d)}$" for x, d in zip(xs, devs)) + ".",
             f"$D(X)={terms}={ssum([d * d * p for d, p in zip(devs, ps)])}={tx(D)}$."]
    return E, D, lines


HINT_DX = "Сначала найди $E(X)$. Потом каждое отклонение $x-E(X)$ возведи в квадрат, умножь на вероятность и сложи."


def g_varx(rng: random.Random, level: int):
    sk = ["st-variance-x", "st-expectation"]
    if level == 1:
        a, h = rng.randint(0, 8), rng.randint(1, 5)
        b = a + 2 * h
        E = a + h
        prompt = f"Случайная величина $X$ принимает значения ${a}$ и ${b}$ с вероятностями $0{{,}}5$ и $0{{,}}5$. Найди дисперсию $D(X)$."
        sol = [f"$E(X)={a}\\cdot 0{{,}}5+{b}\\cdot 0{{,}}5={E}$.",
               f"Отклонения от $E(X)$: ${a}-{E}={-h}$ и ${b}-{E}={h}$, их квадраты ${h * h}$ и ${h * h}$.",
               f"$D(X)={h * h}\\cdot 0{{,}}5+{h * h}\\cdot 0{{,}}5={h * h}$."]
        return T(prompt, h * h, HINT_DX, sol, sk, {"kind": "varx", "xs": [a, b], "ps": ["0.5", "0.5"]},
                 fig=dist_fig([a, b], [Fr(1, 2), Fr(1, 2)]))
    if level == 2:
        if rng.random() < 0.6:
            for _ in range(500):
                xs, ps = _values(rng, 3, 0, 10), parts(rng, 3, 10)
                if sum(Fr(x) * p for x, p in zip(xs, ps)).denominator == 1:
                    break
            else:
                return None
            E, D, lines = _varx_lines(xs, ps)
            return T(f"{_dist_prompt(xs, ps, False)} Найди дисперсию $D(X)$.", D, HINT_DX, lines, sk,
                     {"kind": "varx", "xs": xs, "ps": [pstr(p) for p in ps]}, fig=dist_fig(xs, ps))
        E, D = rng.randint(1, 6), rng.randint(1, 12)
        EX2 = E * E + D
        sol = ["Удобная формула: $D(X)=E(X^2)-\\big(E(X)\\big)^2$ — среднее квадратов минус квадрат среднего.",
               f"$D(X)={EX2}-{E}^2={EX2}-{E * E}={D}$."]
        return T(f"Известно, что $E(X)={E}$ и $E(X^2)={EX2}$. Найди $D(X)$.", D,
                 "Вспомни удобную формулу: дисперсия равна среднему квадратов минус квадрат среднего.", sol, ["st-variance-x"],
                 {"kind": "mom", "E": ans(E), "EX2": ans(EX2)})

    kind = rng.choice(["sigma", "mom", "miss"])
    if kind == "sigma":
        if rng.random() < 0.5:
            p = rng.choice([Fr(1, 10), Fr(1, 5), Fr(1, 2)])
            a, gap = rng.randint(0, 10), rng.choice([5, 10]) if p != Fr(1, 2) else rng.choice([2, 4, 6, 8, 10])
            xs, ps = [a, a + gap], [1 - p, p]
        else:
            for _ in range(2000):
                xs, ps = _values(rng, 3, 0, 10), parts(rng, 3, 10)
                E = sum(Fr(x) * q for x, q in zip(xs, ps))
                D = sum(q * (x - E) ** 2 for x, q in zip(xs, ps))
                if E.denominator == 1 and D in SQUARES:
                    break
            else:
                return None
        E, D, lines = _varx_lines(xs, ps)
        s = Fr(sp.Rational(sp.sqrt(sp.Rational(D.numerator, D.denominator))).p, sp.Rational(sp.sqrt(sp.Rational(D.numerator, D.denominator))).q)
        if s * s != D:
            return None
        lines += [f"$\\sigma(X)=\\sqrt{{D(X)}}=\\sqrt{{{tx(D)}}}={tx(s)}$.",
                  "Подвох: спросили стандартное отклонение, а не дисперсию — в конце извлекаем корень."]
        return T(f"{_dist_prompt(xs, ps, False)} Найди стандартное отклонение $\\sigma(X)$.", s,
                 "Найди $E(X)$, потом дисперсию $D(X)$, а потом извлеки из неё корень.", lines, ["st-variance-x", "st-sigma"],
                 {"kind": "sigmax", "xs": xs, "ps": [pstr(q) for q in ps]}, fig=dist_fig(xs, ps))
    if kind == "mom":
        E = rng.choice([Fr(-1), Fr(-2), Fr(-3), Fr(-4), Fr(-1, 2), Fr(-3, 2), Fr(-5, 2)])
        D = Fr(rng.randint(1, 15)) if rng.random() < 0.7 else Fr(rng.randint(1, 9), 4)
        EX2 = E * E + D
        sol = ["$D(X)=E(X^2)-\\big(E(X)\\big)^2$.",
               f"$\\big(E(X)\\big)^2=({tx(E)})^2={tx(E * E)}$ — квадрат отрицательного числа положителен.",
               f"$D(X)={tx(EX2)}-{tx(E * E)}={tx(D)}$.",
               f"Подвох: $({tx(E)})^2$ — это ${tx(E * E)}$, а не ${tx(-E * E)}$; дисперсия не бывает отрицательной."]
        return T(f"Известно, что $E(X)={tx(E)}$ и $E(X^2)={tx(EX2)}$. Найди $D(X)$.", D,
                 "Дисперсия равна среднему квадратов минус квадрат среднего. Аккуратно с квадратом отрицательного числа.", sol,
                 ["st-variance-x"], {"kind": "mom", "E": ans(E), "EX2": ans(EX2)})
    for _ in range(500):
        xs, ps = _values(rng, 3, 0, 10), parts(rng, 3, 10)
        if sum(Fr(x) * q for x, q in zip(xs, ps)).denominator == 1:
            break
    else:
        return None
    pos = rng.randrange(3)
    shown = list(ps)
    shown[pos] = "p"
    known = [q for i, q in enumerate(ps) if i != pos]
    E, D, lines = _varx_lines(xs, ps)
    sol = [f"Сначала недостающая вероятность: $p=1-({ssum(known)})={tx(ps[pos])}$.", *lines]
    return T(f"{_dist_prompt(xs, shown, False)} Найди дисперсию $D(X)$.", D,
             "Найди $p$ (сумма вероятностей равна 1), потом $E(X)$, потом $D(X)$.", sol, sk + ["st-distribution"],
             {"kind": "varx", "xs": xs, "ps": [u if isinstance(u, str) else pstr(u) for u in shown]}, fig=dist_fig(xs, shown))


# ---------- свойства: X → aX + b ----------

def lin_tex(a: int, b, v: str = "X", lead_b: bool = False) -> str:
    """aX+b для TeX: 2X+3, -X+1, X-4, 3X; lead_b=True — «b−aX»: 5-2X."""
    co = "" if a == 1 else ("-" if a == -1 else str(a))
    if lead_b and b != 0:
        co2 = "" if abs(a) == 1 else str(abs(a))
        return f"{tx(b)}{'-' if a < 0 else '+'}{co2}{v}"
    tail = "" if b == 0 else (f"+{tx(b)}" if b > 0 else f"-{tx(-b)}")
    return f"{co}{v}{tail}"


def g_lin(rng: random.Random, level: int):
    sk = ["st-linear"]
    e = Fr(rng.randint(-5, 10)) if rng.random() < 0.8 else Fr(rng.randint(-9, 19), 2)
    d = Fr(rng.randint(1, 12)) if rng.random() < 0.8 else Fr(rng.randint(1, 19), 2)
    if level == 1:
        form = rng.choice(["E+b", "E-b", "Ea"])
        a, b = (1, rng.randint(1, 9)) if form == "E+b" else ((1, -rng.randint(1, 9)) if form == "E-b" else (rng.randint(2, 5), 0))
        Y = lin_tex(a, b)
        want = a * e + b
        if a == 1:
            sol = [f"Если ко всем значениям прибавить ${tx(b)}$, среднее сдвинется на столько же." if b > 0 else f"Если из всех значений вычесть ${tx(-b)}$, среднее уменьшится на столько же.",
                   f"$E({Y})=E(X){'+' if b > 0 else '-'}{tx(abs(b))}={tx(e)}{'+' if b > 0 else '-'}{tx(abs(b))}={tx(want)}$."]
        else:
            sol = [f"Если все значения умножить на ${a}$, среднее тоже умножится на ${a}$.", f"$E({Y})={a}\\cdot E(X)={a}\\cdot {pt(e)}={tx(want)}$."]
        return T(f"Известно, что $E(X)={tx(e)}$. Найди $E({Y})$.", want,
                 "Сдвиг всех значений сдвигает и среднее, умножение всех значений умножает среднее.", sol, sk,
                 {"kind": "lin", "E": ans(e), "a": a, "b": ans(b), "ask": "E"})
    if level == 2:
        form = rng.choice(["E", "Da", "Db"])
        if form == "E":
            a, b = rng.choice([2, 3, 4, 5, -2, -3]), rng.choice([i for i in range(-9, 10) if i])
            Y = lin_tex(a, b)
            want = a * e + b
            sol = ["$E(aX+b)=a\\cdot E(X)+b$.", f"$E({Y})={a}\\cdot {pt(e)}{'+' if b > 0 else '-'}{abs(b)}={tx(a * e)}{'+' if b > 0 else '-'}{abs(b)}={tx(want)}$."]
            return T(f"Известно, что $E(X)={tx(e)}$. Найди $E({Y})$.", want, "Математическое ожидание: $E(aX+b)=a\\cdot E(X)+b$.", sol, sk,
                     {"kind": "lin", "E": ans(e), "a": a, "b": ans(b), "ask": "E"})
        if form == "Da":
            a = rng.randint(2, 5)
            want = a * a * d
            sol = [f"Когда все значения умножаем на ${a}$, все отклонения тоже умножаются на ${a}$, а их квадраты — на ${a}^2={a * a}$.",
                   f"$D({a}X)={a}^2\\cdot D(X)={a * a}\\cdot {tx(d)}={tx(want)}$."]
            return T(f"Известно, что $D(X)={tx(d)}$. Найди $D({a}X)$.", want, "При умножении на число дисперсия умножается на квадрат этого числа.", sol, sk,
                     {"kind": "lin", "D": ans(d), "a": a, "b": "0", "ask": "D"})
        b = rng.choice([i for i in range(-9, 10) if i])
        Y = lin_tex(1, b)
        sol = ["Если ко всем значениям прибавить одно и то же число, вся таблица просто сдвигается: отклонения от среднего не меняются.",
               f"$D({Y})=D(X)={tx(d)}$."]
        return T(f"Известно, что $D(X)={tx(d)}$. Найди $D({Y})$.", d, "Подумай: меняется ли разброс, если все значения сдвинуть на одно и то же число?", sol, sk,
                 {"kind": "lin", "D": ans(d), "a": 1, "b": ans(b), "ask": "D"})

    form = rng.choice(["Dab", "S", "Eneg", "Dinv"])
    if form == "Dab":
        a, b = -rng.randint(2, 5), rng.choice([i for i in range(-9, 10) if i])
        Y = lin_tex(a, b)
        want = a * a * d
        sol = [f"$D(aX+b)=a^2\\cdot D(X)$: число $b$ на разброс не влияет.", f"$D({Y})=({a})^2\\cdot {tx(d)}={a * a}\\cdot {tx(d)}={tx(want)}$.",
               f"Подвох: минус при $X$ исчезает при возведении в квадрат, а ${tx(b)}$ вообще не важно."]
        return T(f"Известно, что $D(X)={tx(d)}$. Найди $D({Y})$.", want, "Сдвиг на число не меняет дисперсию, а множитель выходит из-под $D$ в квадрате.", sol, sk,
                 {"kind": "lin", "D": ans(d), "a": a, "b": ans(b), "ask": "D"})
    if form == "S":
        s = Fr(rng.randint(1, 9)) if rng.random() < 0.7 else Fr(rng.randint(1, 9), 2)
        a, b = -rng.randint(2, 5), rng.choice([i for i in range(-9, 10) if i])
        Y = lin_tex(a, b)
        want = abs(a) * s
        sol = [f"Дисперсия умножается на $a^2$, поэтому стандартное отклонение — на $\\sqrt{{a^2}}=|a|$.",
               f"$\\sigma({Y})=|{a}|\\cdot {tx(s)}={tx(want)}$.",
               "Подвох: стандартное отклонение не бывает отрицательным, поэтому множитель берём без минуса, а сдвиг не влияет."]
        return T(f"Известно, что $\\sigma(X)={tx(s)}$. Найди $\\sigma({Y})$.", want, "Подумай, во сколько раз растягиваются все отклонения от среднего. Может ли расстояние быть отрицательным?", sol,
                 ["st-linear", "st-sigma"], {"kind": "lin", "S": ans(s), "a": a, "b": ans(b), "ask": "S"})
    if form == "Eneg":
        a, b = -rng.randint(1, 5), rng.randint(1, 15)
        Y = lin_tex(a, b, lead_b=True)
        want = a * e + b
        sol = [f"${Y}={lin_tex(a, b)}$, поэтому $E({Y})={a}\\cdot E(X)+{b}$.",
               f"$E({Y})={b}-{-a if a != -1 else ''}{'' if a == -1 else '\\cdot '}{pt(e)}={tx(want)}$.",
               "Подвох: минус перед $X$ меняет знак у $E(X)$ — следи за скобками, если $E(X)$ отрицательно."]
        return T(f"Известно, что $E(X)={tx(e)}$. Найди $E({Y})$.", want, "Запиши выражение в виде $aX+b$ и используй $E(aX+b)=a\\cdot E(X)+b$.", sol, sk,
                 {"kind": "lin", "E": ans(e), "a": a, "b": ans(b), "ask": "E"})
    a, b = rng.choice([2, 3, 4, 5, -2, -3]), rng.choice([i for i in range(-9, 10) if i])
    Y = lin_tex(a, b)
    V = a * a * d
    sol = [f"$D({Y})={a * a}\\cdot D(X)$, потому что $({a})^2={a * a}$ (сдвиг на ${tx(b)}$ дисперсию не меняет)." if a < 0 else f"$D({Y})={a}^2\\cdot D(X)={a * a}\\cdot D(X)$ (сдвиг на ${tx(b)}$ дисперсию не меняет).",
           f"${a * a}\\cdot D(X)={tx(V)}$, значит, $D(X)={tx(V)}:{a * a}={tx(d)}$."]
    return T(f"Известно, что $D({Y})={tx(V)}$. Найди $D(X)$.", d, "Сначала выясни, во сколько раз $D(aX+b)$ больше $D(X)$, потом раздели.", sol, sk,
             {"kind": "lin", "V": ans(V), "a": a, "b": ans(b), "ask": "Dinv"})


# ---------- ⭐ сумма независимых величин ----------

def _kx(k: int, v, first: bool = False) -> str:
    """Слагаемое «k·v» со знаком: 2\\cdot (-4), -(-5), +3\\cdot 2."""
    body = pt(v) if abs(k) == 1 else f"{abs(k)}\\cdot {pt(v)}"
    if k < 0:
        return "-" + body
    return body if first else "+" + body


def g_indep(rng: random.Random, level: int):
    sk = ["st-independent"]
    kind = rng.choice(["diceE", "diceD", "coin", "combo", "combo", "tables", "games"])
    if kind in ("diceE", "diceD"):
        n = rng.randint(2, 12)
        if kind == "diceE":
            E = Fr(7 * n, 2)
            sol = [f"Сумма очков — это сумма ${n}$ величин, по одной на каждый кубик.", "Для одного кубика $E=3{,}5$.",
                   f"Математические ожидания складываются всегда: $E={n}\\cdot 3{{,}}5={tx(E)}$."]
            return T(f"Бросают ${n}$ игральных кубиков. Найди математическое ожидание суммы выпавших очков.", E,
                     "Сумма очков — сумма очков отдельных кубиков. Чему равно $E$ для одного кубика?", sol, sk, {"kind": "dice", "n": n, "ask": "E"})
        D = Fr(35 * n, 12)
        sol = ["Для одного кубика $D=\\frac{35}{12}$ (мы считали это в уроке: $\\frac{91}{6}-3{,}5^2$).",
               "Кубики независимы, поэтому дисперсии складываются.",
               f"$D={n}\\cdot\\frac{{35}}{{12}}={txf(D)}$."]
        return T(f"Бросают ${n}$ игральных кубиков. Найди дисперсию суммы выпавших очков.", D,
                 "Кубики независимы: дисперсия суммы равна сумме дисперсий. Чему равна дисперсия для одного кубика?", sol, sk,
                 {"kind": "dice", "n": n, "ask": "D"})
    if kind == "coin":
        n = rng.randint(2, 40)
        ask = rng.choice(["E", "D"])
        want = Fr(n, 2) if ask == "E" else Fr(n, 4)
        one = "$E(X_i)=0{,}5$" if ask == "E" else "$E(X_i)=0{,}5$, $D(X_i)=(0-0{,}5)^2\\cdot 0{,}5+(1-0{,}5)^2\\cdot 0{,}5=0{,}25$"
        sol = ["Каждый бросок даёт величину $X_i$: $1$ (орёл) или $0$ (решка) с вероятностями $0{,}5$. Число орлов $X$ — сумма всех $X_i$.",
               f"Для одного броска: {one}.",
               (f"$E(X)={n}\\cdot 0{{,}}5={tx(want)}$." if ask == "E" else f"Броски независимы, дисперсии складываются: $D(X)={n}\\cdot 0{{,}}25={tx(want)}$.")]
        what = "математическое ожидание $E(X)$" if ask == "E" else "дисперсию $D(X)$"
        return T(f"Монету бросают ${n}$ {plural(n, TIMES)}. $X$ — число выпавших орлов. Найди {what}.", want,
                 "Разложи $X$ в сумму: каждый бросок даёт $1$ или $0$. Найди $E$ и $D$ для одного броска.", sol, sk,
                 {"kind": "coins", "n": n, "ask": ask})
    if kind == "combo":
        ex, ey = rng.randint(-5, 6), rng.randint(-5, 6)
        dx, dy = rng.randint(1, 9), rng.randint(1, 9)
        a, b = rng.choice([1, 2, 3, -1, -2]), rng.choice([1, 2, 3, -1, -2, -3])
        c = rng.choice([0, 0, 1, 2, -3, 4, -5, 7])
        if b > 0 and rng.random() < 0.6:
            b = -b
        expr = lin_tex(a, 0) + ("+" if b > 0 else "-") + ("" if abs(b) == 1 else str(abs(b))) + "Y" + ("" if c == 0 else (f"+{c}" if c > 0 else f"-{-c}"))
        ask = rng.choice(["D", "D", "E"])
        given = f"Случайные величины $X$ и $Y$ независимы, $E(X)={ex}$, $D(X)={dx}$, $E(Y)={ey}$, $D(Y)={dy}$."
        if ask == "E":
            want = Fr(a * ex + b * ey + c)
            sol = ["Математическое ожидание суммы равно сумме ожиданий, множители и числа «выносятся»: $E(aX+bY+c)=aE(X)+bE(Y)+c$.",
                   f"$E({expr})={_kx(a, ex, True)}{_kx(b, ey)}{'' if c == 0 else (f'+{c}' if c > 0 else f'-{-c}')}={tx(want)}$."]
            return T(f"{given} Найди $E({expr})$.", want, "Используй $E(aX+bY+c)=aE(X)+bE(Y)+c$; дисперсии здесь не нужны.", sol, sk,
                     {"kind": "combo", "EX": ex, "DX": dx, "EY": ey, "DY": dy, "a": a, "b": b, "c": c, "ask": "E"})
        want = Fr(a * a * dx + b * b * dy)
        sol = ["Для независимых величин $D(aX+bY+c)=a^2D(X)+b^2D(Y)$: число $c$ не влияет, а множители возводятся в квадрат.",
               f"$D({expr})={a * a}\\cdot {dx}+{b * b}\\cdot {dy}={tx(want)}$.",
               "Подвох: даже при минусе перед $Y$ дисперсии складываются — разброс от вычитания не уменьшается."]
        return T(f"{given} Найди $D({expr})$.", want, "Для независимых величин дисперсии складываются, а множитель выходит в квадрате.", sol, sk,
                 {"kind": "combo", "EX": ex, "DX": dx, "EY": ey, "DY": dy, "a": a, "b": b, "c": c, "ask": "D"})
    if kind == "tables":
        xs, ps = [0, rng.randint(1, 4)], parts(rng, 2, 10)
        ys, qs = _values(rng, rng.choice([2, 3]), 0, 6), None
        qs = parts(rng, len(ys), 10)
        if not ps or not qs:
            return None
        ask = rng.choice(["D", "D", "E"])
        Ex, Dx, _ = _varx_lines(xs, ps)
        Ey, Dy, _ = _varx_lines(ys, qs)
        want = Dx + Dy if ask == "D" else Ex + Ey
        prompt = (f"Независимые случайные величины $X$ и $Y$ заданы таблицами: $X$ принимает значения {lst(xs)} с вероятностями {lst(ps)}, "
                  f"а $Y$ — значения {lst(ys)} с вероятностями {lst(qs)}. Найди ${'D' if ask == 'D' else 'E'}(X+Y)$.")
        if ask == "D":
            sol = [f"$E(X)={tx(Ex)}$, $D(X)={tx(Dx)}$.", f"$E(Y)={tx(Ey)}$, $D(Y)={tx(Dy)}$.",
                   f"$X$ и $Y$ независимы, поэтому $D(X+Y)=D(X)+D(Y)={tx(Dx)}+{tx(Dy)}={tx(want)}$."]
        else:
            sol = [_e_line(xs, ps), _e_line(ys, qs, "Y"),
                   f"$E(X+Y)=E(X)+E(Y)={tx(Ex)}+{tx(Ey)}={tx(want)}$."]
        return T(prompt, want, "Посчитай нужную характеристику для каждой величины отдельно, а потом сложи.", sol, sk,
                 {"kind": "tables", "xs": xs, "ps": [pstr(p) for p in ps], "ys": ys, "qs": [pstr(q) for q in qs], "ask": ask},
                 fig=dist_fig(xs, ps, name="X", xs2=[ans(y) for y in ys], ps2=[pstr(q) for q in qs], name2="Y"))
    xs, ps = _values(rng, rng.choice([2, 3]), -3, 6), parts(rng, 3, 10)
    if not xs or not ps:
        return None
    ps = ps[: len(xs)] if len(xs) == 3 else [ps[0], 1 - ps[0]]
    k = rng.randint(2, 10)
    E, D, lines = _varx_lines(xs, ps)
    if D == 0:
        return None
    want = k * D
    prompt = (f"Выигрыш в одной партии — случайная величина $X$: значения {lst(xs)} с вероятностями {lst(ps)}. "
              f"Сыграли ${k}$ {plural(k, ('независимую партию', 'независимые партии', 'независимых партий'))}. Найди дисперсию суммарного выигрыша.")
    sol = [*lines, f"Партии независимы, дисперсии складываются: $D={k}\\cdot {tx(D)}={tx(want)}$.",
           f"Подвох: это не $D({k}X)={k}^2D(X)$ — одна партия, умноженная на ${k}$, разбросана сильнее, чем ${k}$ разных партий."]
    return T(prompt, want, "Суммарный выигрыш — сумма выигрышей в отдельных партиях, а они независимы.", sol, sk,
             {"kind": "games", "xs": xs, "ps": [pstr(p) for p in ps], "k": k}, fig=dist_fig(xs, ps))


GROUPS = [
    ("mean", "Среднее арифметическое", g_mean, 0),
    ("dev", "Отклонения от среднего", g_dev, 2),
    ("vard", "Дисперсия набора чисел", g_vard, 2),
    ("pfill", "Недостающая вероятность в таблице", g_pfill, 4),
    ("ex", "Математическое ожидание по таблице", g_ex, 5),
    ("game", "Выигрыш и справедливая цена игры", g_game, 5),
    ("varx", "Дисперсия случайной величины по таблице", g_varx, 6),
    ("lin", "Как меняются E и D при X → aX+b", g_lin, 7),
]
OLYMPIAD = [("indep", "Сумма независимых величин", g_indep, 7)]


# ---------- независимая проверка ----------

R = sp.Rational
HALF = R(1, 2)
GRID = [Fr(k, 2) for k in range(-600, 601)]  # перебор: целые и половинки от −300 до 300


def _R(s) -> sp.Rational:
    return R(str(s))


def tok(s, frac: bool = False) -> str:
    return f"${tx(Fr(str(s)), frac)}$"


def _balance(xs) -> sp.Rational:
    """Среднее как точка равновесия: единственное a, при котором сумма отклонений (x − a) равна нулю."""
    a = sp.Symbol("a")
    sol = sp.solve(sp.Add(*[_R(x) - a for x in xs]), a)
    assert len(sol) == 1, "нет единственной точки равновесия"
    return sol[0]


def _pair_var(xs) -> sp.Rational:
    """Дисперсия через попарные разности: D = Σᵢ Σⱼ (xᵢ − xⱼ)² / (2n²) (точно, в Fraction)."""
    xs = [Fr(str(x)) for x in xs]
    n = len(xs)
    D = sum(((a - b) ** 2 for a in xs for b in xs), Fr(0)) / (2 * n * n)
    return R(D.numerator, D.denominator)


def _centered(xs, m) -> bool:
    """m — точка равновесия набора: сумма отклонений от m равна нулю."""
    return sum((Fr(x) - m for x in xs), Fr(0)) == 0


def _mean_fr(xs) -> Fr:
    return sum(xs, Fr(0)) / len(xs)


def _sample_set(k: int, m: Fr) -> list[Fr]:
    """Какой-нибудь набор из k чисел со средним m (арифметическая прогрессия вокруг m)."""
    return [m + j - Fr(k - 1, 2) for j in range(k)]


def _search(pred) -> Fr:
    found = [x for x in GRID if pred(x)]
    assert len(found) == 1, f"подходящих чисел {len(found)}"
    return found[0]


def _probs(ps, pct: bool = False):
    """Строки вероятностей → SymPy (p и 2p — неизвестная); неизвестную находим из суммы = 1."""
    p = sp.Symbol("p")
    vals = [R(int(s[:-1]), 100) if pct else (sp.sympify(s.replace("p", "*p").lstrip("*"), locals={"p": p}) if "p" in s else _R(s)) for s in ps]
    if any(v.has(p) for v in vals):
        sol = sp.solve(sp.Add(*vals) - 1, p)
        assert len(sol) == 1, "неизвестная p не единственна"
        vals = [v.subs(p, sol[0]) for v in vals]
    assert all(0 <= v <= 1 for v in vals), f"вероятности вне [0; 1]: {vals}"
    assert sp.Add(*vals) == 1, "сумма вероятностей не 1"
    return vals


def _urn(xs, ps):
    """Распределение → «урна» из N равновероятных билетов (N — общий знаменатель вероятностей)."""
    N = sp.ilcm(*[v.q for v in ps]) if len(ps) > 1 else ps[0].q
    tickets = []
    for x, v in zip(xs, ps):
        tickets += [_R(x)] * int(v * N)
    assert len(tickets) == N
    return tickets


def _avg(tickets) -> sp.Rational:
    return sp.Add(*tickets) / len(tickets)


def _two_point(E, D):
    """Величина, равная E − √D или E + √D с вероятностями 1/2: у неё ровно такие E и D."""
    E, D = (v if isinstance(v, sp.Basic) else _R(v) for v in (E, D))
    r = sp.sqrt(D)
    return [(E - r, HALF), (E + r, HALF)]


def _Ed(dist):
    return sp.simplify(sp.expand(sp.Add(*[x * p for x, p in dist])))


def _Dd(dist):
    m = sp.Add(*[x * p for x, p in dist])
    return sp.simplify(sp.expand(sp.Add(*[p * (x - m) ** 2 for x, p in dist])))


def _convolve(dists):
    out = {sp.Integer(0): sp.Integer(1)}
    for d in dists:
        nxt: dict = {}
        for s, q in out.items():
            for x, p in d:
                nxt[s + x] = nxt.get(s + x, 0) + q * p
        out = nxt
    return list(out.items())


def _tab(xs, ps):
    return [(_R(x), v) for x, v in zip(xs, _probs(ps))]


def ck(c):
    """Пересчёт ответа и список чисел, которые обязаны быть в условии."""
    k = c["kind"]
    if k == "mean":
        return _balance(c["data"]), [tok(x) for x in c["data"]]
    if k == "freq":
        xs = [v for v, n in zip(c["vals"], c["cnts"]) for _ in range(n)]
        return _balance(xs), [f"${n}$" for n in c["cnts"]]
    if k == "removed":
        n, m1, m2 = c["n"], Fr(c["m1"]), Fr(c["m2"])
        rest = _sample_set(n - 1, m2)
        return _search(lambda x: _mean_fr(rest + [x]) == m1), [f"${n}$", tok(m1), tok(m2)]
    if k == "added":
        n, m1, m2 = c["n"], Fr(c["m1"]), Fr(c["m2"])
        old = _sample_set(n, m1)
        x = _search(lambda x: _mean_fr(old + [x]) == m2)
        assert x in (2, 3, 4, 5), "оценка не от 2 до 5"
        return x, [f"${n}$", tok(m1), tok(m2)]
    if k == "dev1":
        assert _balance(c["data"]) == _R(c["mean"]), "в условии неверное среднее"
        assert c["x"] in c["data"]
        return _R(c["x"]) - _R(c["mean"]), [tok(x) for x in c["data"]] + [tok(c["mean"])]
    if k == "devmiss":
        shown = [Fr(v) for v in c["devs"]]
        return _search(lambda d: _centered([10 + v for v in shown + [d]], Fr(10))), [tok(v) for v in shown]
    if k == "numfind":
        known, M = [Fr(v) for v in c["known"]], Fr(c["mean"])
        assert len(known) == c["n"] - 1
        return _search(lambda a: _mean_fr(known + [a]) == M), [tok(v) for v in known] + [tok(M)]
    if k == "devsum":
        m = _balance(c["data"])
        return sp.Add(*[_R(x) - m for x in c["data"]]), [tok(x) for x in c["data"]]
    if k == "devnum":
        M, shown = Fr(c["mean"]), [Fr(v) for v in c["devs"]]
        return _search(lambda x: _centered([M + v for v in shown] + [x], M)), [tok(M)] + [tok(v) for v in shown]
    if k == "var":
        return _pair_var(c["data"]), [tok(x) for x in c["data"]]
    if k == "sigma":
        s = sp.sqrt(_pair_var(c["data"]))
        assert s.is_rational, "корень из дисперсии не рациональный"
        return s, [tok(x) for x in c["data"]]
    if k == "varfreq":
        xs = [v for v, n in zip(c["vals"], c["cnts"]) for _ in range(n)]
        return _pair_var(xs), [f"${v}$" for v in c["vals"]] + [f"${n}$" for n in c["cnts"]]
    if k == "pfill":
        vals = _probs(c["ps"])
        i = c["ps"].index("p")
        return vals[i], [tok(x) for x in c["xs"]] + [tok(s, c["frac"]) for s in c["ps"] if "p" not in s]
    if k == "pevent":
        vals = _probs(c["ps"])
        holds = {">": lambda x: x > c["t"], "<": lambda x: x < c["t"], ">=": lambda x: x >= c["t"], "<=": lambda x: x <= c["t"]}[c["op"]]
        want = sp.Add(*[v for x, v in zip(c["xs"], vals) if holds(x)])
        return want, [tok(x) for x in c["xs"]] + [tok(s) for s in c["ps"] if "p" not in s]
    if k == "ex":
        pct = c.get("pct", False)
        vals = _probs(c["ps"], pct)
        toks = [tok(x) for x in c["xs"]] + ([f"${s[:-1]}\\%$" for s in c["ps"]] if pct else [tok(s, c.get("frac", False)) for s in c["ps"] if "p" not in s])
        return _avg(_urn(c["xs"], vals)), toks
    if k == "game":
        E = _avg(_urn(c["xs"], _probs(c["ps"])))
        toks = [f"${abs(int(x))}$" for x in c["xs"] if x]
        if c["ask"] == "net":
            toks += [f"${c['price']}$"] + [tok(s) for s in c["ps"][:2]]
            return E - c["price"], toks
        return E, toks
    if k == "lottery":
        N = c["N"]
        tickets = [R(P) for P, n in c["prizes"] for _ in range(n)]
        tickets += [R(0)] * (N - len(tickets))
        E = _avg(tickets)
        toks = [f"${N}$"] + [f"${v}$" for P, n in c["prizes"] for v in (P, n)]
        if c["ask"] == "loss":
            return c["k"] * (c["price"] - E), toks + [f"${c['price']}$", f"${c['k']}$"]
        return E, toks
    if k == "prize":
        C, faces = Fr(c["price"]), c["faces"]
        return _search(lambda x: _mean_fr([x] * faces + [Fr(0)] * (6 - faces)) == C), [f"${c['price']}$"]
    if k in ("varx", "sigmax"):
        vals = _probs(c["ps"])
        D = _pair_var(_urn(c["xs"], vals))
        toks = [tok(x) for x in c["xs"]] + [tok(s) for s in c["ps"] if "p" not in s]
        if k == "sigmax":
            s = sp.sqrt(D)
            assert s.is_rational, "σ не рациональное"
            return s, toks
        return D, toks
    if k == "mom":
        E, EX2 = _R(c["E"]), _R(c["EX2"])
        D = EX2 - E**2
        assert D > 0, "дисперсия не положительна"
        # конкретная величина с таким E и найденной D: её E(X²) должно совпасть с данным
        assert _Ed([(x**2, p) for x, p in _two_point(E, D)]) == EX2
        return D, [f"E(X)={tx(Fr(c['E']))}$", f"E(X^2)={tx(Fr(c['EX2']))}$"]
    if k == "lin":
        a, b = _R(c["a"]), _R(c["b"])
        toks = []
        if c["ask"] == "E":
            X = _two_point(c["E"], 1)
            toks.append(f"E(X)={tx(Fr(c['E']))}$")
            return _Ed([(a * x + b, p) for x, p in X]), toks
        if c["ask"] == "D":
            X = _two_point(0, c["D"])
            toks.append(f"D(X)={tx(Fr(c['D']))}$")
            return _Dd([(a * x + b, p) for x, p in X]), toks
        if c["ask"] == "S":
            X = _two_point(0, _R(c["S"]) ** 2)
            toks.append(f"\\sigma(X)={tx(Fr(c['S']))}$")
            return sp.sqrt(_Dd([(a * x + b, p) for x, p in X])), toks
        V = _R(c["V"])
        toks.append(f")={tx(Fr(c['V']))}$")
        x = sp.Symbol("x", positive=True)
        sol = sp.solve(sp.Eq(_Dd([(a * v + b, p) for v, p in _two_point(0, x)]), V), x)
        assert len(sol) == 1, "D(X) не единственна"
        return sol[0], toks
    if k == "dice":
        dist = _convolve([[(R(f), R(1, 6)) for f in range(1, 7)]] * c["n"])
        assert sp.Add(*[p for _, p in dist]) == 1
        return (_Ed(dist) if c["ask"] == "E" else _Dd(dist)), [f"${c['n']}$"]
    if k == "coins":
        dist = _convolve([[(R(0), HALF), (R(1), HALF)]] * c["n"])
        return (_Ed(dist) if c["ask"] == "E" else _Dd(dist)), [f"${c['n']}$"]
    if k == "combo":
        X, Y = _two_point(c["EX"], c["DX"]), _two_point(c["EY"], c["DY"])
        Z = [(c["a"] * x + c["b"] * y + c["c"], p * q) for x, p in X for y, q in Y]
        return (_Ed(Z) if c["ask"] == "E" else _Dd(Z)), [f"{key[0]}({key[1]})={c[key]}$" for key in ("EX", "DX", "EY", "DY")]
    if k == "tables":
        X, Y = _tab(c["xs"], c["ps"]), _tab(c["ys"], c["qs"])
        Z = [(x + y, p * q) for x, p in X for y, q in Y]
        toks = [tok(v) for v in c["xs"] + c["ys"]] + [tok(s) for s in c["ps"] + c["qs"]]
        return (_Ed(Z) if c["ask"] == "E" else _Dd(Z)), toks
    if k == "games":
        dist = _convolve([_tab(c["xs"], c["ps"])] * c["k"])
        return _Dd(dist), [tok(v) for v in c["xs"]] + [tok(s) for s in c["ps"]] + [f"${c['k']}$"]
    raise AssertionError(f"неизвестный вид {k}")


def _fig_ok(t: dict) -> str | None:
    fig, c = t.get("fig"), t["chk"]
    if not fig:
        return None
    if fig["id"] != "dist":
        return f"неизвестный рисунок {fig['id']}"
    props = fig["props"]
    xs = c.get("xs", c.get("vals"))
    ps = c.get("ps", c.get("cnts"))
    if [str(Fr(str(v))) for v in props["xs"]] != [str(Fr(str(v))) for v in xs]:
        return f"значения на рисунке {props['xs']} не совпадают с данными {xs}"
    norm = lambda s: s if ("p" in str(s) or "%" in str(s)) else str(Fr(str(s)))  # noqa: E731
    if [norm(v) for v in props["ps"]] != [norm(v) for v in ps]:
        return f"вероятности на рисунке {props['ps']} не совпадают с данными {ps}"
    return None


def verify(t: dict) -> str | None:
    c = t.get("chk")
    if not c:
        return "нет данных для проверки (chk)"
    try:
        want, toks = ck(c)
    except AssertionError as e:
        return f"{c['kind']}: {e}"
    got = R(t["answer"])
    if sp.simplify(got - want) != 0:
        return f"{c['kind']}: пересчёт даёт {want}, в ответе {t['answer']}"
    miss = [s for s in toks if s not in t["prompt"]]
    if miss:
        return f"{c['kind']}: в условии нет чисел {miss}"
    return _fig_ok(t)
