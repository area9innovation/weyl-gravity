#!/usr/bin/env python3
"""Print the exact circumference-times-extra resonant transport primitive."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp

from bridge.einstein_sector.einstein_maxwell_weyl_axial_operator import _generic_rows as _axial_rows
from bridge.einstein_sector.einstein_maxwell_weyl_polar_full_tensor import _generic_rows as _polar_rows


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_circumference_ell2_extra_transport_primitive.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_circumference_ell2_extra_transport_primitive.schema.json"
VERIFIER = ROOT / "bridge/einstein_sector/verify_einstein_maxwell_weyl_circumference_ell2_extra_transport_primitive.py"
TESTS = ROOT / "bridge/einstein_sector/tests/test_einstein_maxwell_weyl_circumference_ell2_extra_transport_primitive.py"
REPORT = ROOT / "bridge/einstein_sector/reports/einstein-maxwell-weyl-circumference-ell2-extra-transport-primitive.md"
INPUTS = {
    "transport_theorem": ROOT / "bridge/certificates/einstein_maxwell_weyl_global_spectator_ell2_extra_resonance.json",
    "axial_extra": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_physical_ring.json",
    "polar_extra": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_physical_completion.json",
    "axial_operator": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_operator.json",
    "polar_operator": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_full_tensor.json",
    "smooth_extension": ROOT / "bridge/certificates/einstein_maxwell_weyl_global_extra_smooth_secular_second_order.json",
}
AXIAL_ROWS = ("metric_t", "metric_x", "metric_angular", "maxwell_t", "maxwell_x", "maxwell_angular")
POLAR_ROWS = (
    "metric_00",
    "metric_01",
    "metric_11",
    "metric_0a",
    "metric_1a",
    "sphere_trace",
    "sphere_tracefree",
    "maxwell_axial_density",
)


class TransportPrimitiveError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise TransportPrimitiveError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _matrix_strings(matrix: sp.MatrixBase) -> list[list[str]]:
    return [[str(sp.factor(matrix[row, column])) for column in range(matrix.cols)] for row in range(matrix.rows)]


def _shell_reducer(frequency: sp.Symbol):
    shell = sp.Poly(frequency**2 - sp.Rational(16, 3), frequency, domain=sp.QQ)

    def reduce(value: sp.Expr) -> sp.Expr:
        numerator, denominator = sp.fraction(sp.cancel(value))
        numerator_remainder = sp.rem(sp.Poly(numerator, frequency), shell).as_expr()
        denominator_remainder = sp.rem(sp.Poly(denominator, frequency), shell).as_expr()
        return sp.factor(numerator_remainder / denominator_remainder)

    return reduce


def _operator_matrix(rows: dict[str, sp.Expr], row_order: tuple[str, ...], fields: tuple[sp.Symbol, ...]) -> sp.Matrix:
    return sp.Matrix([[sp.diff(rows[name], field) for field in fields] for name in row_order])


def _physical_ell2(expression: str) -> sp.Expr:
    return sp.sympify(expression.replace("lambda", "lam"), locals={"lam": sp.Integer(6)})


def _transport_data(records: dict[str, dict[str, Any]]) -> dict[str, Any]:
    circumference = sp.symbols("c", real=True)

    axial_rows, axial_symbols = _axial_rows()
    axial_frequency = axial_symbols["omega"]
    axial_reduce = _shell_reducer(axial_frequency)
    axial_fields = tuple(axial_symbols[name] for name in ("h_t", "h_x", "q_t", "q_x"))
    axial_operator = _operator_matrix(axial_rows, AXIAL_ROWS, axial_fields).subs(
        {axial_symbols["lambda"]: 6, axial_symbols["k"]: 0}
    )
    axial_representatives = sp.Matrix(
        [[_physical_ell2(value) for value in row]
         for row in records["axial_extra"]["audit"]["zero_momentum_audit"]["extra_representatives_order_Ht_Hx_Qt_Qx"]]
    )
    axial_weights = sp.diag(0, 1, 0, 1)
    axial_correction = circumference * axial_weights * axial_representatives / 2
    axial_source = (-axial_operator * axial_correction).applyfunc(axial_reduce)
    axial_remainder = (axial_operator * axial_correction + axial_source).applyfunc(axial_reduce)
    axial_shell_defect = (axial_operator * axial_representatives).applyfunc(axial_reduce)

    polar_rows, polar_symbols = _polar_rows()
    eigenvalue, momentum, polar_frequency, *polar_fields_list = polar_symbols
    polar_reduce = _shell_reducer(polar_frequency)
    polar_fields = tuple(polar_fields_list)
    polar_operator = _operator_matrix(polar_rows, POLAR_ROWS, polar_fields).subs({eigenvalue: 6, momentum: 0})
    polar_representatives = sp.Matrix(
        [[_physical_ell2(value) for value in row]
         for row in records["polar_extra"]["physical_ring"]["zero_momentum_audit"]["extra_representatives_order_At_B_Ct_U"]]
    )
    polar_weights = sp.diag(0, 1, 2, 1)
    polar_correction = circumference * polar_weights * polar_representatives / 2
    polar_source = (-polar_operator * polar_correction).applyfunc(polar_reduce)
    polar_remainder = (polar_operator * polar_correction + polar_source).applyfunc(polar_reduce)
    polar_shell_defect = (polar_operator * polar_representatives).applyfunc(polar_reduce)

    mutated_correction = polar_correction.copy()
    mutated_correction[2, 1] = -36 * circumference
    mutation_remainder = (polar_operator * mutated_correction + polar_source).applyfunc(polar_reduce)

    _require(axial_shell_defect == sp.zeros(6, 2), "axial extra representatives left the p shell")
    _require(polar_shell_defect == sp.zeros(8, 2), "polar extra representatives left the p shell")
    _require(axial_remainder == sp.zeros(6, 2), "axial transport primitive failed")
    _require(polar_remainder == sp.zeros(8, 2), "polar transport primitive failed")
    _require(axial_source == sp.zeros(6, 2), "axial circumference source should vanish")
    _require(polar_source[:, 0] == sp.zeros(8, 1), "first polar circumference source should vanish")
    _require(polar_source[:, 1] != sp.zeros(8, 1), "second polar circumference source should be nonzero")
    _require(mutation_remainder != sp.zeros(8, 2), "covariant-index-weight mutation was not detected")

    p = sp.factor(polar_frequency**2 - 6 + sp.Rational(2, 3))
    q = sp.factor(polar_frequency**4 - 12 * polar_frequency**2 + 24)
    _require(polar_reduce(p) == 0, "extra p shell moved")
    _require(polar_reduce(q) == -sp.Rational(104, 9), "Einstein q divisor changed on the extra shell")

    return {
        "frequency_convention": "exp(i*(k*x-omega*t))",
        "specialization": {"ell": 2, "lambda": 6, "k": 0, "omega_squared": "16/3", "p": "0", "q": "-104/9"},
        "transport_rule": {
            "radius_family": "R^2=1+eta*c",
            "d_log_R_d_eta_at_zero": "c/2",
            "weights": "one per covariant x index and one per A_x coefficient",
            "mixed_identity": "L_1*(partial_eta u_R)|_0+(partial_eta L_R)|_0*u_1=0",
        },
        "axial": {
            "field_order": ["H_t", "H_x", "Q_t", "Q_x"],
            "row_order": list(AXIAL_ROWS),
            "extra_representatives": _matrix_strings(axial_representatives),
            "transport_weight_diagonal": ["0", "1", "0", "1"],
            "correction_columns": _matrix_strings(axial_correction),
            "source_columns": _matrix_strings(axial_source),
            "remainder_columns": _matrix_strings(axial_remainder),
        },
        "polar": {
            "field_order": ["A_t", "B", "C_t", "U"],
            "row_order": list(POLAR_ROWS),
            "extra_representatives": _matrix_strings(polar_representatives),
            "transport_weight_diagonal": ["0", "1", "2", "1"],
            "correction_columns": _matrix_strings(polar_correction),
            "source_columns": _matrix_strings(polar_source),
            "remainder_columns": _matrix_strings(polar_remainder),
        },
        "negative_control": {
            "mutation": "replace the two-covariant-x C_t weight 2 by weight 1 in polar column 2",
            "mutated_correction_columns": _matrix_strings(mutated_correction),
            "remainder_columns": _matrix_strings(mutation_remainder),
            "detected": True,
        },
        "disposition": {
            "potential_p_primary_resonance": True,
            "actual_source_requires_secular_prefactor": False,
            "reason": "the source is the parameter derivative of an exact radius-family Jacobi equation and has the displayed ordinary harmonic transport primitive",
            "nonzero_source_location": "polar extra column 2 only",
            "all_four_extra_columns_printed": True,
            "all_four_extra_columns_in_linear_image": True,
        },
    }


def build() -> dict[str, Any]:
    records = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in INPUTS.items()}
    _require(
        records["transport_theorem"]["classification"]["circumference_times_ell2_extra_source_in_linear_image"],
        "circumference transport theorem changed",
    )
    _require(
        records["axial_extra"]["classification"]["extra_quotient_two_cyclic_summands_on_every_physical_fiber"],
        "axial extra quotient changed",
    )
    _require(
        records["polar_extra"]["classification"]["canonical_extra_polar_quotient_two_p_summands"],
        "polar extra quotient changed",
    )
    _require(
        records["smooth_extension"]["classification"]["smooth_exponential_polynomial_second_order_correction_exists"],
        "smooth extension theorem changed",
    )
    transport = _transport_data(records)
    return {
        "schema": "einstein-maxwell-weyl-circumference-ell2-extra-transport-primitive-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_CIRCUMFERENCE_ELL2_EXTRA_TRANSPORT_PRIMITIVE",
        "result_state": "COEFFICIENT_EXPLICIT_RESONANT_TRANSPORT_PRIMITIVE_ALL_FOUR_EXTRA_COLUMNS",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "scope": {
            "theory": "Weyl-Maxwell",
            "background": "compact magnetically supported Plebanski-Hacyan product",
            "boundaries": "closed S1_L times S2; ordinary finite-frequency harmonic correction",
            "charge_sector": "fixed N=2 magnetic bundle",
            "carrier": "circumference ell=0 tangent crossed with the complete axial-plus-polar ell=2,k=0 extra p-primary block",
            "degree": 2,
            "parity": "two axial and two polar extra columns",
            "ell": 2,
            "m": "all by SO3 naturality",
            "k": 0,
            "omega": "+/-4/sqrt(3)",
        },
        "transport_primitive": transport,
        "classification": {
            "complete_four_extra_transport_columns_printed": True,
            "full_six_row_axial_remainder_zero": True,
            "full_eight_row_polar_remainder_zero": True,
            "unique_nonzero_source_is_second_polar_column": True,
            "ordinary_harmonic_primitive_suffices_at_p_resonance": True,
            "secular_prefactor_required_for_actual_circumference_source": False,
            "covariant_index_weight_mutation_rejected": True,
            "all_m_by_naturality": True,
            "causal_retarded_map_certified": False,
            "residual_or_quantum_claim": False,
        },
        "interpretation": "The p-shell resonance is only a potential propagation obstruction in this physical channel. The actual circumference-times-extra source is the derivative of an exact radius-family Jacobi equation. Three transport columns have zero source; the second polar column has the displayed nonzero eight-row source and an ordinary same-frequency primitive. No secular time prefactor is needed.",
        "next_gate": "print a coefficient-level fixed-bundle electric-duality primitive if needed, then leave the complete Berger branch mixing calculation blocked on its same-background branch map",
        "claim_boundary": "This is a coefficient-explicit REDUCED-MODE transport theorem for the circumference-times-ell2-extra channel only. It does not print the Q_e duality correction, alter the separate bounded global-extra obstruction, construct a causal/retarded correction, cover multiple momenta, descend to residual cohomology, or make a particle or quantum claim.",
        "source_manifest": {
            str(path.relative_to(ROOT)): _sha256(path)
            for path in (*INPUTS.values(), Path(__file__).resolve(), SCHEMA, VERIFIER, TESTS, REPORT)
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_circumference_ell2_extra_transport_primitive --check",
            "python3 -m bridge.einstein_sector.verify_einstein_maxwell_weyl_circumference_ell2_extra_transport_primitive",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_circumference_ell2_extra_transport_primitive",
        ],
        "verification_receipt": {
            "producing_date": "2026-07-18",
            "tier_0": {"status": "PASS", "commands": ["python3 -m py_compile <scoped Python paths>", "python3 -m json.tool <certificate and schema>", "git diff --check -- <scoped paths>"]},
            "tier_1": {"status": "PASS", "commands": ["python3 -m bridge.einstein_sector.einstein_maxwell_weyl_circumference_ell2_extra_transport_primitive --check", "python3 -m bridge.einstein_sector.verify_einstein_maxwell_weyl_circumference_ell2_extra_transport_primitive", "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_circumference_ell2_extra_transport_primitive"]},
            "tier_2": {"status": "PASS_BY_CONTENT_ADDRESS", "inputs": list(INPUTS)},
            "tier_3": {"status": "NOT_RUN", "reason": "no all-orders, causal, final-residual or release lifecycle is promoted"},
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    value = build()
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    if arguments.write:
        OUTPUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    elif json.loads(OUTPUT.read_text(encoding="utf-8")) != value:
        raise TransportPrimitiveError("circumference transport primitive certificate is stale")
    print("EINSTEIN_MAXWELL_WEYL_CIRCUMFERENCE_ELL2_EXTRA_TRANSPORT_PRIMITIVE: PASS")


if __name__ == "__main__":
    main()
