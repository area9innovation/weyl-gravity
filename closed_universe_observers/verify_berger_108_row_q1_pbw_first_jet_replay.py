#!/usr/bin/env python3
"""Independently replay the decisive Berger 108-row q1 first-jet witness."""

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp

from closed_universe_observers import berger_108_row_q1_pbw_replay as replay


ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
CERTIFICATE = P / "certificates/BERGER_108_ROW_Q1_PBW_FIRST_JET_REPLAY_OBSTRUCTION.json"
SCHEMA = P / "schema/berger-108-row-q1-pbw-first-jet-replay-obstruction-v1.schema.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    value = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    for dependency in value["dependency_refs"].values():
        assert sha256(ROOT / dependency["path"]) == dependency["sha256"]

    q1 = replay.load_q1()
    for degree, operator in q1.items():
        assert replay.summary(operator) == value["composed_q1"]["bidegree_summaries"][str(degree)]
        assert replay.cyclicity_defect(operator) == {}
    squared = replay.q1_squared_coefficients(q1)
    assert squared[(0, 0)] == {}
    assert squared[(0, 1)] == {}
    assert squared[(1, 1)] == {}
    first_jet = squared[(1, 0)]
    assert replay.summary(first_jet) == value["nilpotency_replay"]["bidegree_summaries"]["(1, 0)"]

    evaluator = replay.BackgroundEvaluator()
    normal = replay.sphere_normal_form(evaluator.polynomial(first_jet[(27, 0, ())])[0])
    x0, x1, x2, x3 = replay.background_ideal.X
    selected = sp.Poly(normal, x0, x1, x2, x3).coeff_monomial(x0 * x1)
    sine = replay.TRIG_S
    expected = -sp.Rational(27, 40) * sine**4 + sp.Rational(27, 32) * sine**2 - sp.Rational(2921, 480)
    assert sp.expand(selected - expected) == 0
    strict_upper = sp.Rational(27, 32) * sp.Rational(5, 72) - sp.Rational(2921, 480)
    assert strict_upper < 0
    assert str(strict_upper) == value["nilpotency_replay"]["first_jet_witness"]["coefficient_strict_upper"]
    print("BERGER_108_ROW_Q1_PBW_FIRST_JET_REPLAY_OBSTRUCTION independent replay: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
