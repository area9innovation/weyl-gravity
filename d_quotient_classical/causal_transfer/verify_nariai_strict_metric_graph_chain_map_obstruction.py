#!/usr/bin/env python3
"""Independent consumer for the Nariai strict metric-graph no-go."""

from __future__ import annotations

import json

from jsonschema import Draft202012Validator
import sympy as sp

from d_quotient_classical.causal_transfer.nariai_strict_metric_graph_chain_map_obstruction import (
    INCIDENCE_CERTIFICATE,
    OUTPUT,
    SCHEMA,
)


def _sparse_matrix(value: dict[str, object]) -> sp.Matrix:
    rows, columns = value["shape"]
    matrix = sp.zeros(rows, columns)
    for row, column, coefficient in value["entries"]:
        matrix[row, column] = sp.Rational(coefficient)
    return matrix


def main() -> None:
    value = json.loads(OUTPUT.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)

    # Recheck the global-coordinate Killing statement without calling the
    # producer's coordinate helper.
    t, chi, theta, phi = sp.symbols("t chi theta phi", real=True)
    coordinates = (t, chi, theta, phi)
    metric = sp.diag(-1, sp.cosh(t) ** 2, 1, sp.sin(theta) ** 2)
    xi = sp.Matrix([0, 1, 0, 0])
    lie = sp.zeros(4)
    for a in range(4):
        for b in range(4):
            lie[a, b] = sp.simplify(
                sum(xi[c] * sp.diff(metric[a, b], coordinates[c]) for c in range(4))
                + sum(metric[c, b] * sp.diff(xi[c], coordinates[a]) for c in range(4))
                + sum(metric[a, c] * sp.diff(xi[c], coordinates[b]) for c in range(4))
            )
    if lie != sp.zeros(4):
        raise ValueError("independent partial_chi Killing replay failed")
    if metric.subs({t: 0, theta: sp.pi / 2}) != sp.diag(-1, 1, 1, 1):
        raise ValueError("independent base-frame replay failed")

    # Consume the authoritative incidence table rather than importing its
    # producing function.  This crosses the producer boundary for the actual
    # contradiction witness.
    incidence_certificate = json.loads(INCIDENCE_CERTIFICATE.read_text())
    incidence = _sparse_matrix(
        incidence_certificate["exact_data"]["curvature_incidence"]
    )
    image = incidence * sp.Matrix([0, 1, 0, 0])
    if image[4] != sp.Rational(2, 3) or image == sp.zeros(60, 1):
        raise ValueError("independent curvature-incidence witness failed")
    if sp.Rational(3, 2) * image[4] != 1:
        raise ValueError("normalized witness failed")

    # The logical step is exact and order-independent: differential
    # operators are linear and send the zero section to zero.
    checks = value["exact_checks"]
    if not all(
        checks[key] is True
        for key in (
            "partial_chi_is_global_Killing",
            "K_partial_chi_is_zero_section",
            "I_Omega_partial_chi_is_nonzero",
            "all_order_contradiction",
        )
    ):
        raise ValueError("all-order theorem flags are incomplete")
    if checks["pbw_rank_gaps"] != [4, 4, 4, 4, 4]:
        raise ValueError("PBW regression rank gaps drifted")
    flags = value["flags"]
    if flags["STRICT_CANONICAL_METRIC_GRAPH_CHAIN_MAP_EXISTS"] is not False:
        raise ValueError("strict graph was overpromoted")
    if flags["METRIC_BACH_ENDPOINT_CHAIN_EQUIVALENCE"] is not False:
        raise ValueError("metric endpoint was overpromoted")
    print(f"{value['result_id']}: independently verified")


if __name__ == "__main__":
    main()
