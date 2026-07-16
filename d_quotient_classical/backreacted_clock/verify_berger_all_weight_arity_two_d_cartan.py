#!/usr/bin/env python3
"""Independent exact audit of the all-weight homogeneous Berger Cartan SDR."""

from __future__ import annotations

import json
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "d_quotient_classical/certificates/BERGER_ALL_WEIGHT_ARITY_TWO_D_CARTAN.json"
Q2_CERTIFICATE = ROOT / "d_quotient_classical/certificates/BERGER_RATIONAL_FIXTURE_Q2_D_BLOCK.json"


def verify_certificate() -> dict[str, object]:
    payload = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    base = json.loads(Q2_CERTIFICATE.read_text(encoding="utf-8"))
    hessian = sp.Matrix([[sp.Rational(value) for value in row[:3]] for row in base["classical_unary_q1"]["matrix"][3:6]])
    inverse = sp.Matrix([[sp.Rational(value) for value in row] for row in payload["coefficients"]["H_inverse"]])
    assert hessian * inverse == sp.eye(3)
    cubic = [[[sp.S.Zero for _ in range(3)] for _ in range(3)] for _ in range(3)]
    for entry in base["classical_binary_q2"]["entries"]:
        output, left, right = entry["output"] - 3, entry["left"], entry["right"]
        value = sp.Rational(entry["coefficient"])
        cubic[output][left][right] = value
        cubic[output][right][left] = value

    mixed = {}
    for entry in payload["arity_two_Cartan_homotopy"]["mixed_sparse_entries"]:
        key = (entry["output_field"], entry["equation_input"], entry["field_input"])
        assert key not in mixed
        mixed[key] = (sp.Rational(entry["coefficient_equation_weight"]), sp.Rational(entry["coefficient_field_weight"]))
    equation = {}
    for entry in payload["arity_two_Cartan_homotopy"]["equation_sparse_entries"]:
        key = (entry["output_equation"], entry["left_equation"], entry["right_equation"])
        assert key not in equation
        equation[key] = (sp.Rational(entry["coefficient_left_weight"]), sp.Rational(entry["coefficient_right_weight"]))

    k, ell = sp.symbols("k ell")
    for output in range(3):
        for equation_input in range(3):
            for field_input in range(3):
                base_value = sp.factor(sum(
                    inverse[output, equation_index]
                    * cubic[equation_index][field_index][field_input]
                    * inverse[field_index, equation_input]
                    for equation_index in range(3)
                    for field_index in range(3)
                ))
                expected = (-sp.Rational(2, 3) * base_value, -sp.Rational(1, 3) * base_value)
                assert mixed.get((output, equation_input, field_input), (sp.S.Zero, sp.S.Zero)) == expected
        for left_equation in range(3):
            for right_equation in range(3):
                base_value = sp.factor(sum(
                    cubic[output][first][second]
                    * inverse[first, left_equation]
                    * inverse[second, right_equation]
                    for first in range(3)
                    for second in range(3)
                ))
                expected = (sp.Rational(1, 3) * base_value, -sp.Rational(1, 3) * base_value)
                assert equation.get((output, left_equation, right_equation), (sp.S.Zero, sp.S.Zero)) == expected

    # Check the three nontrivial input-type cases directly for every index.
    for left in range(3):
        for right in range(3):
            # field-field: mixed terms after q1 must cancel the Cartan source.
            for output in range(3):
                source = (k + ell) * sum(inverse[output, equation_index] * cubic[equation_index][left][right] for equation_index in range(3))
                first = sum(
                    hessian[equation_input, left]
                    * ((mixed.get((output, equation_input, right), (0, 0))[0] * k) + (mixed.get((output, equation_input, right), (0, 0))[1] * ell))
                    for equation_input in range(3)
                )
                second = sum(
                    hessian[equation_input, right]
                    * ((mixed.get((output, equation_input, left), (0, 0))[0] * ell) + (mixed.get((output, equation_input, left), (0, 0))[1] * k))
                    for equation_input in range(3)
                )
                assert sp.factor(source + first + second) == 0

            # equation-field and field-equation cases include the eq-eq row.
            for equation_input in range(3):
                for output_equation in range(3):
                    source = k * sum(cubic[output_equation][field][right] * inverse[field, equation_input] for field in range(3))
                    post = sum(
                        hessian[output_equation, field_output]
                        * (
                            mixed.get((field_output, equation_input, right), (0, 0))[0] * k
                            + mixed.get((field_output, equation_input, right), (0, 0))[1] * ell
                        )
                        for field_output in range(3)
                    )
                    pre = -sum(
                        hessian[second_equation, right]
                        * (
                            equation.get((output_equation, equation_input, second_equation), (0, 0))[0] * k
                            + equation.get((output_equation, equation_input, second_equation), (0, 0))[1] * ell
                        )
                        for second_equation in range(3)
                    )
                    assert sp.factor(source + post + pre) == 0

    checks = payload["exact_checks"]
    assert checks["arity_two_Cartan_identity"] is True
    assert checks["iota2_graded_cyclic"] is True
    assert payload["flags"]["BERGER_ALL_WEIGHT_ARITY_TWO_D_CARTAN"] is True
    assert payload["flags"]["NONZERO_WEIGHT_D_CARTAN_TESTED"] is True
    assert payload["flags"]["FULL_4D_SUPPORT_LOCAL_Q2"] is False
    assert payload["flags"]["COMPLETE_54_ROW_ARITY_TWO_D_CARTAN"] is False
    return payload


def main() -> None:
    verify_certificate()
    print("BERGER_ALL_WEIGHT_ARITY_TWO_D_CARTAN_INDEPENDENT: PASS")
    print("nonzero-weight homogeneous arity-two Cartan contraction: CERTIFIED")
    print("full 4D support-local and complete 54-row contractions: OPEN")


if __name__ == "__main__":
    main()
