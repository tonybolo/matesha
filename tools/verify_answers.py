#!/usr/bin/env python3
"""Независимая проверка ответов к задачам через SymPy.

Для каждой задачи с полем `verify` считаем эталон из `expr` и сравниваем с `answer`.
Запуск:  python3 tools/verify_answers.py   (из корня репозитория)
Нужно:   pip install sympy pyyaml
"""
import glob
import re
import sys

import sympy as sp
import yaml
from sympy.parsing.sympy_parser import (
    convert_xor,
    implicit_multiplication_application,
    parse_expr,
    standard_transformations,
)

TRANSFORMS = standard_transformations + (implicit_multiplication_application, convert_xor)
SYMS = {c: sp.Symbol(c) for c in "abcdefghijklmnopqrstuvwxyz" if c not in "eiIEOSNQ"}


def parse(text: str, evaluate: bool = True):
    text = text.replace(",", ".")
    # abc -> a*b*c для переменных; sqrt оставляем
    text = re.sub(r"[a-z]+", lambda m: m.group(0) if m.group(0) in ("sqrt", "abs") else "*".join(m.group(0)), text)
    return parse_expr(text, local_dict=SYMS, transformations=TRANSFORMS, evaluate=evaluate)


def denominators_roots(expr_text: str):
    """Нули всех знаменателей исходного выражения (ОДЗ)."""
    expr = parse(expr_text, evaluate=False)
    roots = set()
    for node in sp.preorder_traversal(expr):
        if isinstance(node, sp.Pow) and node.exp.is_negative:
            base = node.base
            for v in sp.solve(base, dict=False):
                if v.is_real:
                    roots.add(sp.nsimplify(v))
    return roots


def parse_set(answer: str):
    a = answer.strip().lower()
    if a in ("нет", "нет корней", "none", "-", "∅"):
        return set()
    return {sp.nsimplify(parse(p.strip())) for p in a.split(";") if p.strip()}


def expected_for(task):
    v = task.get("verify")
    if not v:
        return None
    op = v["op"]
    expr_text = task.get("expr")
    if op == "odz":
        return denominators_roots(expr_text)
    if op == "custom":
        return sp.sympify(v["sympy"], locals=SYMS)
    expr = parse(expr_text)
    if op == "reduce":
        return sp.cancel(expr)
    if op == "simplify":
        return sp.cancel(sp.together(expr))
    if op == "value":
        subs = {SYMS[k]: parse(val) for k, val in v["subs"].items()}
        return sp.nsimplify(expr.subs(subs))
    raise ValueError(f"неизвестная операция {op}")


def total_degree(e) -> int:
    e = sp.expand(e)
    if not e.free_symbols:
        return 0
    return sp.Poly(e, *sorted(e.free_symbols, key=str)).total_degree()


def fraction_size(e) -> int:
    n, d = sp.fraction(sp.together(e))
    return total_degree(n) + total_degree(d)


def check_task(task):
    exp = expected_for(task)
    if exp is None:
        return None
    if task["answerKind"] == "roots":
        got = parse_set(task["answer"])
        return got == {sp.nsimplify(e) for e in exp}, f"ожидалось {sorted(map(str, exp))}, в ответе {sorted(map(str, got))}"
    got = parse(task["answer"])
    if sp.simplify(got - exp) != 0:
        return False, f"ожидалось {exp}, в ответе {got}"
    if task.get("reduce") and fraction_size(got) > fraction_size(sp.cancel(got)):
        return False, f"ответ {got} сократим до {sp.cancel(got)}"
    return True, ""


def main() -> int:
    bad = 0
    checked = 0
    for path in sorted(glob.glob("content/algebra8/*.yaml")):
        topic = yaml.safe_load(open(path, encoding="utf-8"))
        for task in topic["tasks"]:
            res = check_task(task)
            if res is None:
                print(f"  ?  {task['id']}: нет verify")
                continue
            checked += 1
            ok, msg = res
            if not ok:
                bad += 1
                print(f"FAIL {task['id']}: {msg}")
        # проверочные вопросы с вводом
        for q in topic["check"]:
            if q["kind"] == "input" and q["answerKind"] == "expr":
                try:
                    parse(q["answer"])
                except Exception as e:  # noqa: BLE001
                    bad += 1
                    print(f"FAIL {q['id']}: {e}")
    print(f"Проверено задач: {checked}, ошибок: {bad}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
