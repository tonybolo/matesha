#!/usr/bin/env python3
"""Независимая проверка сгенерированных заданий (python3 tools/generators/verify_generated.py из корня репозитория).

Пересчитывает ответ из условия через SymPy и сравнивает с записанным в JSON.
"""
import json
import sys
from pathlib import Path

import sympy as sp

sys.path.insert(0, str(Path(__file__).parent))
from common import SYMS, parse_app  # noqa: E402

GEN = Path(__file__).resolve().parents[2] / "content/algebra8/generated"


def exact(s: str):
    return sp.sympify(s.replace("^", "**"), locals=SYMS, rational=True)


def num(s: str) -> float:
    return float(sp.N(exact(s), 30))


def sgn(a: float, b: float) -> str:
    return "<" if a < b - 1e-12 else (">" if a > b + 1e-12 else "=")


def check(t: dict) -> str | None:
    k = t["answerKind"]
    if k == "compare":
        want = sgn(num(t["expr"]), num(t["expr2"]))
        return None if want == t["answer"] else f"знак: {want}, в ответе {t['answer']}"
    if k == "order":
        vals = [num(i) for i in t["items"]]
        want = ",".join(map(str, sorted(range(len(vals)), key=lambda i: vals[i])))
        return None if want == t["answer"] else f"порядок {want}, в ответе {t['answer']}"
    if k == "choice" and t.get("optExprs"):
        irr = [i for i, e in enumerate(t["optExprs"]) if not sp.simplify(exact(e)).is_rational]
        return None if irr == [int(t["answer"])] else f"иррациональные варианты {irr}, в ответе {t['answer']}"
    if t.get("domSpec"):
        d = t["domSpec"]
        x = SYMS["x"]
        inner = d["a"] * x + d["b"]
        sol = sp.solve_univariate_inequality(inner > 0 if d["strict"] else inner >= 0, x, relational=False)

        def as_set(op, r):
            r = sp.Rational(r)
            return {">=": sp.Interval(r, sp.oo), ">": sp.Interval.open(r, sp.oo), "<=": sp.Interval(-sp.oo, r), "<": sp.Interval.open(-sp.oo, r)}[op]

        good = [i for i, (op, r) in enumerate(d["opts"]) if as_set(op, r) == sol]
        return None if good == [int(t["answer"])] else f"верные варианты {good}, в ответе {t['answer']}, решение {sol}"
    if t.get("argSpec"):
        a_ = t["argSpec"]
        a, c, v = sp.Integer(a_["a"]), sp.Integer(a_["c"]), sp.Rational(a_["v"])
        base = (v - c) / a
        if base < 0:
            return "нет решения"
        x0 = base**2
        if x0 != sp.Rational(a_["x0"]):
            return f"x0 в данных {a_['x0']}, на самом деле {x0}"
        good = [i for i, o in enumerate(a_["options"]) if "|pm" not in o and sp.Rational(o) == x0]
        return None if good == [int(t["answer"])] else f"верные варианты {good}, в ответе {t['answer']}"
    if t.get("mkCheck"):
        m = t["mkCheck"]
        x = SYMS["x"]
        x0 = sp.Rational(m["x0"])
        holds = [i for i, (l, r) in enumerate(m["eqs"]) if sp.simplify(exact(l).subs(x, x0) - exact(r).subs(x, x0)) == 0]
        return None if holds == [int(t["answer"])] else f"при x={x0} выполняются варианты {holds}, в ответе {t['answer']}"
    if t.get("diffOf"):
        lhs, rhs = t["diffOf"]
        x = SYMS["x"]
        roots = [r for r in sp.solve(sp.Eq(exact(lhs), exact(rhs)), x) if r.is_real]
        if len(roots) < 2:
            return "нужно минимум два корня"
        diff = max(roots) - min(roots)
        if t["answerKind"] == "choice":
            want = sp.Rational(t["optValues"][int(t["answer"])])
            same_vals = [i for i, o in enumerate(t["optValues"]) if sp.Rational(o) == diff]
            return None if (want == diff and same_vals == [int(t["answer"])]) else f"разность {diff}, в ответе вариант {t['answer']}"
        return None if sp.simplify(diff - exact(t["answer"])) == 0 else f"разность {diff}, в ответе {t['answer']}"
    if t.get("pairCheck"):
        pc = t["pairCheck"]
        e = [exact(x) for x in pc["exprs"]]
        i, j = pc["pair"]
        value = sp.simplify(e[i] * e[j] - 1) if pc["kind"] == "inverse" else sp.simplify(e[i] + e[j])
        if value != 0:
            return f"пара {pc['pair']} не {pc['kind']}: {value}"
        if t["options"].__len__() != 3 or [(0, 1), (0, 2), (1, 2)].index(tuple(pc["pair"])) != int(t["answer"]):
            return "номер варианта не совпадает с парой"
        others = [(0, 1), (0, 2), (1, 2)]
        for pair in others:
            if list(pair) == pc["pair"]:
                continue
            v = sp.simplify(e[pair[0]] * e[pair[1]] - 1) if pc["kind"] == "inverse" else sp.simplify(e[pair[0]] + e[pair[1]])
            if v == 0:
                return f"неоднозначно: ещё подходит пара {pair}"
        return None
    if t.get("formula"):
        f = t["formula"]
        eq = sp.Eq(exact(f["lhs"]), exact(f["rhs"]))
        sols = sp.solve(eq, SYMS[f["solveFor"]])
        if len(sols) != 1:
            return f"решений {len(sols)}"
        return None if sp.simplify(sols[0] - exact(t["answer"])) == 0 else f"ответ {t['answer']} не совпадает с {sols[0]}"
    if t.get("verify", {}).get("op") == "self":
        d = sp.simplify(exact(t["expr"]) - exact(t["answer"]))
        return None if d == 0 else f"ответ {t['answer']} не равен выражению (разность {d})"
    if k == "roots" and t.get("equation"):
        lhs, rhs = t["equation"]
        x = SYMS[t.get("var", "x")]
        if t["answer"].strip() in ("нет", "нет корней"):
            sols = [r for r in sp.solve(sp.Eq(exact(lhs), exact(rhs)), x) if r.is_real]
            return None if not sols else f"корни есть: {sols}"
        roots = [exact(r.strip()) for r in t["answer"].split(";")]
        for r in roots:
            if abs(sp.N((exact(lhs) - exact(rhs)).subs(x, r), 30)) > 1e-12:
                return f"корень {r} не подходит"
        real = [s for s in sp.solve(sp.Eq(exact(lhs), exact(rhs)), x) if s.is_real]
        if len(real) != len({sp.N(r, 20) for r in roots}):
            return f"корней {len(real)}, в ответе {len(roots)}"
        return None
    return None  # остальные типы проверяются самим генератором


def main() -> int:
    bad = total = 0
    for f in sorted(GEN.glob("*.json")):
        data = json.loads(f.read_text(encoding="utf-8"))
        for t in data["tasks"]:
            total += 1
            msg = check(t)
            if msg:
                bad += 1
                print(f"FAIL {t['id']}: {msg}")
    print(f"Проверено заданий: {total}, ошибок: {bad}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
