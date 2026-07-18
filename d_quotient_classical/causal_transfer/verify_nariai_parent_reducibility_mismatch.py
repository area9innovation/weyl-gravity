#!/usr/bin/env python3
"""Independent consumer of the Nariai reducibility mismatch theorem."""

from __future__ import annotations

import json

from jsonschema import Draft202012Validator
import sympy as sp

from d_quotient_classical.causal_transfer.nariai_parent_reducibility_mismatch import (
    OUTPUT,
    SCHEMA,
)
from d_quotient_classical.causal_transfer.nariai_yang_mills_middle_compression import (
    fixture as middle_fixture,
)


def _lie(metric, coordinates, vector):
    return sp.Matrix(
        4,
        4,
        lambda a, b: sp.simplify(
            sum(
                vector[c] * sp.diff(metric[a, b], coordinates[c])
                + metric[c, b] * sp.diff(vector[c], coordinates[a])
                + metric[a, c] * sp.diff(vector[c], coordinates[b])
                for c in range(4)
            )
        ),
    )


def main() -> None:
    value = json.loads(OUTPUT.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)

    # Reconstruct all six product Killing fields independently of the
    # producer's fixture and check their first-jet independence.
    t, x, th, ph = sp.symbols("t x th ph", real=True)
    coordinates = (t, x, th, ph)
    metric = sp.diag(-1, sp.cosh(t) ** 2, 1, sp.sin(th) ** 2)
    vectors = (
        sp.Matrix([0, 1, 0, 0]),
        sp.Matrix([sp.cos(x), -sp.tanh(t) * sp.sin(x), 0, 0]),
        sp.Matrix([sp.sin(x), sp.tanh(t) * sp.cos(x), 0, 0]),
        sp.Matrix([0, 0, 0, 1]),
        sp.Matrix([0, 0, sp.cos(ph), -sp.cot(th) * sp.sin(ph)]),
        sp.Matrix([0, 0, sp.sin(ph), sp.cot(th) * sp.cos(ph)]),
    )
    if any(_lie(metric, coordinates, vector) != sp.zeros(4) for vector in vectors):
        raise ValueError("independent product Killing replay failed")
    base = {t: 0, x: 0, th: sp.pi / 2, ph: 0}
    jets = []
    for vector in vectors:
        entries = [entry.subs(base) for entry in vector]
        entries.extend(
            sp.diff(vector[component], coordinate).subs(base)
            for component in range(4)
            for coordinate in coordinates
        )
        jets.append(sp.Matrix(entries))
    if sp.Matrix.hstack(*jets).rank() != 6:
        raise ValueError("independent product Killing jets lost rank")

    curvature = middle_fixture()["normal_tractor_square"][()]
    if curvature.shape != (90, 15) or curvature.rank() != 14:
        raise ValueError("independent normal-tractor curvature rank replay failed")
    if len(curvature.nullspace()) != 1:
        raise ValueError("independent common curvature kernel replay failed")

    obstruction = value["obstruction"]
    if obstruction["metric_H_minus_1_lower_bound"] != 6:
        raise ValueError("metric reducibility lower bound drifted")
    if obstruction["parent_H_minus_1_upper_bound"] != 1:
        raise ValueError("parent reducibility upper bound drifted")
    if obstruction["missing_reducibility_dimension_lower_bound"] != 5:
        raise ValueError("reducibility mismatch witness drifted")
    flags = value["flags"]
    if flags["CURRENT_NORMAL_TRACTOR_PARENT_METRIC_QUASI_ISOMORPHISM"] is not False:
        raise ValueError("parent/metric quasi-isomorphism was overpromoted")
    if flags["CURVATURE_CORRECTED_AUTOMORPHISM_PROLONGATION_REQUIRED"] is not True:
        raise ValueError("required automorphism prolongation was not recorded")
    if flags["NARIAI_GREEN_HOMOTOPY"] is not False:
        raise ValueError("Nariai Green homotopy was overpromoted")
    print(f"{value['result_id']}: independently verified")


if __name__ == "__main__":
    main()
