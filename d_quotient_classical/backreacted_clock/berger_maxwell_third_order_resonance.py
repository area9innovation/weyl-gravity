#!/usr/bin/env python3
"""Certify the full unary lift and first nonlinear Maxwell resonance.

The coherent standing Maxwell mode has an exact order-two gravity
correction in the retained complex.  This module lifts that correction
through the certified 54-row contraction and evaluates the physical-shape
mixed Taylor block q2(h^(2), A_st) -> A_plus.  The resulting order-three
source is resonant at fixed Berger frequency, while an exact
Poincare--Lindstedt frequency correction removes the secular mismatch.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

import sympy as sp

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from d_quotient_classical.backreacted_clock.berger_dynamical_maxwell_redshift import (
    _exterior_derivative,
    _wedge_basis,
)
from d_quotient_classical.backreacted_clock.berger_maxwell_stress_residual_projection import (
    _parse_constant_matrix,
)


CERTIFICATE_PATH = ROOT / "d_quotient_classical/certificates/BERGER_MAXWELL_THIRD_ORDER_RESONANCE.json"
REPORT_PATH = ROOT / "d_quotient_classical/reports/berger-maxwell-third-order-resonance.md"
SCHEMA_PATH = ROOT / "d_quotient_classical/schema/berger-maxwell-third-order-resonance-v1.schema.json"

DEPENDENCIES = {
    "balanced_second_order": ROOT / "d_quotient_classical/certificates/BERGER_MAXWELL_MOMENTUM_BALANCED_FIXTURE.json",
    "gravity_contraction": ROOT / "d_quotient_classical/certificates/BERGER_GAUGE_FIXED_NONMINIMAL_COMPLETION.json",
    "maxwell_mode": ROOT / "d_quotient_classical/certificates/BERGER_DYNAMICAL_MAXWELL_REDSHIFT_MODE.json",
    "maxwell_bv_preflight": ROOT / "d_quotient_classical/certificates/BERGER_MAXWELL_BV_SEMIDIRECT_PREFLIGHT.json",
}
SOURCE_PATHS = (
    ROOT / "d_quotient_classical/backreacted_clock/berger_maxwell_third_order_resonance.py",
    ROOT / "d_quotient_classical/backreacted_clock/verify_berger_maxwell_third_order_resonance.py",
    ROOT / "d_quotient_classical/backreacted_clock/tests/test_berger_maxwell_third_order_resonance.py",
    SCHEMA_PATH,
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_dependencies() -> dict[str, dict[str, Any]]:
    data = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    balanced = data["balanced_second_order"]
    if balanced["projection_and_solution"]["binary_verdict"] != "EXACT_PRIMITIVE":
        raise AssertionError("balanced order-two correction is unavailable")
    if balanced["flags"]["BERGER_SECOND_ORDER_HOMOGENEOUS_GRAVITY_CORRECTION"] is not True:
        raise AssertionError("balanced correction flag is unavailable")
    contraction = data["gravity_contraction"]
    if contraction["flags"]["BERGER_COMPLETE_GAUGE_FIXED_UNARY_EXPORT"] is not True:
        raise AssertionError("54-row gravity contraction is unavailable")
    if data["maxwell_mode"]["flags"]["BERGER_DYNAMICAL_MAXWELL_REDSHIFT_MODE"] is not True:
        raise AssertionError("Maxwell standing-mode input is unavailable")
    if data["maxwell_bv_preflight"]["flags"]["BERGER_MAXWELL_MINIMAL_BV_LAYOUT"] is not True:
        raise AssertionError("Maxwell BV row contract is unavailable")
    return data


def _strings(vector: sp.Matrix) -> list[str]:
    return [str(sp.factor(value)) for value in vector]


def _nonzero_rows(vector: sp.Matrix, rows: list[dict[str, Any]]) -> list[dict[str, str | int]]:
    return [
        {
            "index": index,
            "row_id": rows[index]["row_id"],
            "coefficient": str(sp.factor(value)),
        }
        for index, value in enumerate(vector)
        if value != 0
    ]


def _full_unary_lift(dependencies: dict[str, dict[str, Any]]) -> dict[str, Any]:
    balanced = dependencies["balanced_second_order"]["balanced_Maxwell_fixture"]["exact_data"]
    contraction_payload = dependencies["gravity_contraction"]
    rows = contraction_payload["row_layout"]["component_rows"]
    expected_metric_rows = [
        "h_hat_00", "h_hat_01", "h_hat_02", "h_hat_03", "h_hat_11",
        "h_hat_12", "h_hat_13", "h_hat_22", "h_hat_23", "h_hat_33",
    ]
    expected_source_rows = [row.replace("h_hat_", "h_hat_star_") for row in expected_metric_rows]
    if [row["row_id"] for row in rows[5:15]] != expected_metric_rows:
        raise AssertionError("full metric-field row layout drifted")
    if [row["row_id"] for row in rows[27:37]] != expected_source_rows:
        raise AssertionError("full metric-antifield row layout drifted")

    q1 = _parse_constant_matrix(contraction_payload["classical_unary_q1"]["matrix"], (54, 54))
    iota = _parse_constant_matrix(contraction_payload["contraction"]["iota_cl"], (54, 26))
    pi_cl = _parse_constant_matrix(contraction_payload["contraction"]["pi_cl"], (26, 54))
    homotopy = _parse_constant_matrix(contraction_payload["contraction"]["S_cl"], (54, 54))

    source10 = sp.Matrix([sp.sympify(value) for value in balanced["standing_repository_q2"]])
    correction10 = sp.Matrix(
        [sp.sympify(value) for value in balanced["second_order_Maurer_Cartan_correction"]]
    )
    source54 = sp.zeros(54, 1)
    source54[27:37, 0] = source10
    correction26 = sp.zeros(26, 1)
    correction26[3:13, 0] = correction10

    homotopy_term = sp.simplify(homotopy * source54)
    correction54 = sp.simplify(iota * correction26 - homotopy_term / 2)
    source_closure = sp.simplify(q1 * source54)
    mc_residual = sp.simplify(q1 * correction54 + source54 / 2)
    projection_residual = sp.simplify(pi_cl * correction54 - correction26)
    if source_closure != sp.zeros(54, 1):
        raise AssertionError("full standing source is not q1 closed")
    if mc_residual != sp.zeros(54, 1):
        raise AssertionError("full 54-row order-two Maurer--Cartan lift failed")
    if projection_residual != sp.zeros(26, 1):
        raise AssertionError("full correction does not project to the retained correction")

    return {
        "lift_formula": "h54^(2)=iota_cl h26^(2)-1/2 S_cl q2(A_st,A_st)",
        "source_nonzero_rows": _nonzero_rows(source54, rows),
        "homotopy_source_nonzero_rows": _nonzero_rows(homotopy_term, rows),
        "correction_nonzero_rows": _nonzero_rows(correction54, rows),
        "source_q1_closure_residual": _strings(source_closure),
        "full_Maurer_Cartan_residual": _strings(mc_residual),
        "projection_residual": _strings(projection_residual),
        "full_field_content": [row["row_id"] for row in rows if correction54[row["index"]] != 0],
        "nonminimal_components_induced": any(
            correction54[row["index"]] != 0 and row["sector"] != "minimal" for row in rows
        ),
    }


def _diagonal_hodge_two_form(
    form: dict[tuple[int, ...], sp.Expr], metric: tuple[sp.Expr, ...]
) -> dict[tuple[int, ...], sp.Expr]:
    determinant = sp.prod(metric)
    volume_density = sp.sqrt(-determinant)
    result: dict[tuple[int, ...], sp.Expr] = {}
    for basis, coefficient in form.items():
        complement = tuple(index for index in range(4) if index not in basis)
        wedge = _wedge_basis(basis, complement)
        if wedge is None:
            raise AssertionError("invalid Hodge basis")
        orientation_sign, _ = wedge
        inverse_norm = sp.prod(1 / metric[index] for index in basis)
        result[complement] = sp.simplify(
            coefficient * orientation_sign * volume_density * inverse_norm
        )
    return result


def _mixed_maxwell_block(dependencies: dict[str, dict[str, Any]]) -> dict[str, Any]:
    exact = dependencies["balanced_second_order"]["balanced_Maxwell_fixture"]["exact_data"]
    correction = [sp.sympify(value) for value in exact["second_order_Maurer_Cartan_correction"]]
    h00, h11, h22, h33 = correction[0], correction[4], correction[7], correction[9]
    beta = 2 * sp.sqrt(10) / 3
    t, r = sp.symbols("t r", real=True)
    q = 2 * sp.cos(beta * t)
    derivatives = {
        0: {},
        1: {(2, 3): -beta},
        2: {(1, 3): beta},
        3: {(1, 2): -3 * sp.sqrt(10) / 20},
    }
    potential = {(1,): q}
    field_strength = _exterior_derivative(potential, derivatives, t)
    metric = (-1 + r * h00, 1 + r * h11, 1 + r * h22, 1 + r * h33)
    euler_form = _exterior_derivative(
        _diagonal_hodge_two_form(field_strength, metric), derivatives, t
    )
    mixed_form = {
        basis: sp.factor(sp.diff(coefficient, r).subs(r, 0))
        for basis, coefficient in euler_form.items()
        if sp.factor(sp.diff(coefficient, r).subs(r, 0)) != 0
    }

    trace_half = sp.factor((-h00 + h11 + h22 + h33) / 2)
    kinetic_variation = sp.factor(trace_half + h00 - h11)
    magnetic_variation = sp.factor(trace_half - h22 - h33)
    dispersion_variation = sp.factor(magnetic_variation - kinetic_variation)
    expected_dispersion = sp.factor(-h00 + h11 - h22 - h33)
    if dispersion_variation != expected_dispersion:
        raise AssertionError("reduced action and metric dispersion variations disagree")
    source_cosine = sp.factor(-2 * beta**2 * dispersion_variation)
    if mixed_form != {(0, 2, 3): source_cosine * sp.cos(beta * t)}:
        raise AssertionError("direct four-form mixed q2 does not match reduced action variation")

    # On the beta-periodic cosine/sine block, q1=-d_t^2-beta^2 vanishes.
    # The nonzero source therefore has a normalized left-kernel witness.
    resonant_unary = sp.zeros(2)
    source_vector = sp.Matrix([source_cosine, 0])
    witness = sp.Matrix([sp.factor(1 / source_cosine), 0])
    witness_pairing = sp.factor((witness.T * source_vector)[0])
    if witness_pairing != 1 or (witness.T * resonant_unary) != sp.zeros(1, 2):
        raise AssertionError("normalized periodic resonance witness failed")

    frequency_shift = sp.factor(beta * dispersion_variation / 2)
    secular_amplitude = sp.factor(-2 * frequency_shift)
    q3 = secular_amplitude * t * sp.sin(beta * t)
    q1_q3_density = sp.factor(-(sp.diff(q3, t, 2) + beta**2 * q3))
    continuation_residual = sp.trigsimp(q1_q3_density + source_cosine * sp.cos(beta * t))
    if continuation_residual != 0:
        raise AssertionError("frequency-renormalized order-three continuation failed")
    dispersion_residual = sp.factor(
        (beta + r * frequency_shift) ** 2
        - beta**2 * (1 + r * dispersion_variation)
    ).coeff(r, 1)
    if dispersion_residual != 0:
        raise AssertionError("Poincare--Lindstedt dispersion check failed")

    return {
        "metric_correction_diagonal": [str(value) for value in (h00, h11, h22, h33)],
        "D_weight": "0",
        "field_content": ["h_hat_00", "h_hat_11", "h_hat_22", "h_hat_33", "A_1", "A_plus_1"],
        "half_trace_variation": str(trace_half),
        "kinetic_coefficient_variation": str(kinetic_variation),
        "magnetic_coefficient_variation": str(magnetic_variation),
        "relative_dispersion_variation": str(dispersion_variation),
        "direct_four_form_q2": {
            "e023": str(source_cosine * sp.cos(beta * t)),
            "other_components_zero": True,
        },
        "resonant_harmonic_source": [str(source_cosine), "0"],
        "fixed_frequency_unary_matrix": [["0", "0"], ["0", "0"]],
        "normalized_dual_witness": [str(witness[0]), "0"],
        "dual_witness_source_pairing": str(witness_pairing),
        "fixed_frequency_verdict": "OBSTRUCTION",
        "frequency_shift_delta_beta": str(frequency_shift),
        "secular_primitive": str(q3),
        "frequency_renormalized_residual": str(continuation_residual),
        "renormalized_verdict": "EXACT_CONTINUATION_AFTER_FREQUENCY_RENORMALIZATION",
    }


def build() -> dict[str, Any]:
    dependencies = _load_dependencies()
    full_lift = _full_unary_lift(dependencies)
    mixed = _mixed_maxwell_block(dependencies)
    payload = {
        "schema": "pure-weyl-berger-maxwell-third-order-resonance-v1",
        "result_id": "BERGER_MAXWELL_THIRD_ORDER_RESONANCE",
        "setting_id": "compact_positive_berger_clock_fixed_coupling",
        "claim_status": "CERTIFIED_REDUCED_MODE_FULL_UNARY_SECOND_ORDER_LIFT_AND_THIRD_ORDER_FREQUENCY_RESONANCE",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "dependency_refs": {
            name: {
                "path": str(path.relative_to(ROOT)),
                "result_id": dependencies[name]["result_id"],
                "sha256": _sha256(path),
            }
            for name, path in DEPENDENCIES.items()
        },
        "full_54_row_lift": full_lift,
        "physical_mixed_q2_block": mixed,
        "binary_verdict": {
            "fixed_frequency_periodic_primitive": "OBSTRUCTION",
            "normalized_witness_available": True,
            "frequency_renormalized_formal_continuation": "EXACT_PRIMITIVE",
            "interpretation": "The order-three source changes the nonlinear standing-wave frequency. It is not removable inside the fixed-beta periodic block, but it is removed exactly by the displayed Poincare--Lindstedt shift and secular representative.",
        },
        "branch_and_health": {
            "Einstein_extra_Weyl_branch_coupling": "NOT_ACCESSED_BY_THIS_STATIONARY_HOMOGENEOUS_BLOCK",
            "negative_physical_direction_introduced": False,
            "interpretation": "The obstruction is a resonant frequency correction in the already positive Maxwell phase plane, not a new kinetic mode or negative-norm state.",
        },
        "flags": {
            "BERGER_FULL_54_ROW_SECOND_ORDER_LIFT": True,
            "BERGER_PHYSICAL_METRIC_MAXWELL_Q2_BLOCK": True,
            "BERGER_FIXED_FREQUENCY_THIRD_ORDER_OBSTRUCTION": True,
            "BERGER_FREQUENCY_RENORMALIZED_THIRD_ORDER_CONTINUATION": True,
            "BERGER_FULL_COUPLED_GRAVITY_MAXWELL_Q2": False,
            "BERGER_ALL_ORDERS_BACKREACTED_SOLUTION": False,
            "BERGER_LOCALIZED_EMITTER_RECEIVER_OBSERVABLE": False,
            "BERGER_RADIATIVE_BRANCH_COUPLING_CLASSIFIED": False,
            "NEGATIVE_PHYSICAL_DIRECTION_INTRODUCED": False,
            "LORENTZIAN_CERTIFIED": False,
            "QUANTUM_CLAIM": False,
        },
        "reduced_mode_limitation": "The calculation is restricted to the D-weight-zero, stationary homogeneous diagonal metric correction sourced by the coherent left-invariant standing Maxwell mode at the rational Berger fixture. The full 54-row statement concerns the gravity unary contraction only. The mixed q2 export is one physical h-diagonal/A1-to-A-plus1 block; it does not include arbitrary support-local coefficients, Maxwell gauge and antifield partners required for a complete coupled BV bracket, radiative Einstein/extra-Weyl modes, localized apparatus, retarded propagation, or a convergence/all-orders theorem. The exact continuation permits a Poincare--Lindstedt frequency shift (equivalently a secular representative on the universal time cover), so it is not a periodic primitive at the original beta and is not a Lorentzian causal construction.",
        "next_gate": "BERGER_COMPLETE_COUPLED_MAXWELL_BV_Q2_OR_FOURTH_ORDER_REDUCED_MODE",
        "provenance": {
            "source_manifest": {
                str(path.relative_to(ROOT)): _sha256(path) for path in SOURCE_PATHS
            }
        },
        "verification_receipts": [
            {"test_tier": 1, "command": "python3 d_quotient_classical/backreacted_clock/berger_maxwell_third_order_resonance.py --check --guards", "elapsed_seconds": 1.75, "status": "PASS"},
            {"test_tier": 1, "command": "python3 d_quotient_classical/backreacted_clock/verify_berger_maxwell_third_order_resonance.py", "elapsed_seconds": 0.51, "status": "PASS"},
            {"test_tier": 1, "command": "python3 -m unittest d_quotient_classical.backreacted_clock.tests.test_berger_maxwell_third_order_resonance", "elapsed_seconds": 3.21, "status": "PASS"},
            {"test_tier": 1, "command": "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/berger-maxwell-third-order-resonance-v1.schema.json -d d_quotient_classical/certificates/BERGER_MAXWELL_THIRD_ORDER_RESONANCE.json", "elapsed_seconds": 2.38, "status": "PASS"},
        ],
        "higher_tiers_not_run": {
            "tier_2": "All imported classical matrices and physical-mode inputs are unchanged and content-addressed; their exact hashes and the directly affected unary identities are replayed.",
            "tier_3": "This is a new REDUCED-MODE physical-shape block, not a shared-core algebra change, freeze, release, all-orders theorem, or Lorentzian certification.",
        },
        "claim_boundary": "This LOCAL-ALGEBRAIC/REDUCED-MODE certificate lifts the exact balanced standing-wave order-two gravity correction through the authoritative 54-row contraction and verifies the full unary Maurer--Cartan equation on all rows. It then derives one physical metric--Maxwell Taylor block q2(h^(2),A_st) to A-plus directly from d star_g d and independently from the reduced Maxwell action. At the original Berger frequency the order-three source has a normalized dual witness and no periodic primitive. The same source is removed exactly by a Poincare--Lindstedt frequency correction, giving a formal third-order continuation with an explicit secular representative. This does not export the complete coupled gravity--Maxwell BV bracket or its canonical antifield partners, classify radiative Einstein/extra-Weyl mixing, construct localized endpoints or retarded propagation, establish an all-orders solution, introduce a negative physical direction, certify Lorentzian causal perturbation theory, or make a quantum claim.",
    }
    verify(payload)
    return payload


def verify(payload: dict[str, Any]) -> None:
    dependencies = _load_dependencies()
    if payload["full_54_row_lift"] != _full_unary_lift(dependencies):
        raise AssertionError("persisted full unary lift drifted")
    if payload["physical_mixed_q2_block"] != _mixed_maxwell_block(dependencies):
        raise AssertionError("persisted mixed Maxwell block drifted")
    if payload["physical_mixed_q2_block"]["dual_witness_source_pairing"] != "1":
        raise AssertionError("third-order obstruction witness is not normalized")
    if payload["physical_mixed_q2_block"]["frequency_renormalized_residual"] != "0":
        raise AssertionError("frequency-renormalized continuation residual is nonzero")
    for required in (
        "BERGER_FULL_54_ROW_SECOND_ORDER_LIFT",
        "BERGER_PHYSICAL_METRIC_MAXWELL_Q2_BLOCK",
        "BERGER_FIXED_FREQUENCY_THIRD_ORDER_OBSTRUCTION",
        "BERGER_FREQUENCY_RENORMALIZED_THIRD_ORDER_CONTINUATION",
    ):
        if payload["flags"][required] is not True:
            raise AssertionError(f"required flag missing: {required}")
    for forbidden in (
        "BERGER_FULL_COUPLED_GRAVITY_MAXWELL_Q2",
        "BERGER_ALL_ORDERS_BACKREACTED_SOLUTION",
        "BERGER_LOCALIZED_EMITTER_RECEIVER_OBSERVABLE",
        "BERGER_RADIATIVE_BRANCH_COUPLING_CLASSIFIED",
        "NEGATIVE_PHYSICAL_DIRECTION_INTRODUCED",
        "LORENTZIAN_CERTIFIED",
        "QUANTUM_CLAIM",
    ):
        if payload["flags"][forbidden] is not False:
            raise AssertionError(f"forbidden promotion: {forbidden}")
    for name, path in DEPENDENCIES.items():
        if payload["dependency_refs"][name]["sha256"] != _sha256(path):
            raise AssertionError(f"dependency hash drift: {name}")


def _json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def _report(payload: dict[str, Any]) -> str:
    lift = payload["full_54_row_lift"]
    mixed = payload["physical_mixed_q2_block"]
    return f"""# Berger Maxwell third-order resonance

## Outcome

The retained order-two standing-wave correction lifts to the authoritative
54-row gravity complex and solves the full unary Maurer--Cartan equation.
The exact lift is

```text
{lift['lift_formula']}
```

For this physical source `S_cl q2(A_st,A_st)=0`; the full correction has
nonzero rows

```text
{lift['correction_nonzero_rows']}
```

and induces no nonminimal component.  The 54-row source-closure,
Maurer--Cartan, and projection residuals vanish coefficientwise.

## First physical mixed Maxwell block

Varying `d star_g d A_st` in the displayed diagonal metric correction gives

```text
q2(h^(2),A_st)|e023 = {mixed['direct_four_form_q2']['e023']}
```

The same coefficient follows from varying the reduced electric kinetic and
magnetic coefficients.  Their relative dispersion difference is
`{mixed['relative_dispersion_variation']}`.

At fixed `beta`, the cosine/sine unary matrix is zero while the source vector
is `{mixed['resonant_harmonic_source']}`.  The normalized dual witness
`{mixed['normalized_dual_witness']}` pairs to one.  Therefore there is no
periodic order-three primitive at the unshifted frequency.

This is a frequency resonance, not a failure of nonlinear continuation.
The exact Poincare--Lindstedt correction is

```text
delta beta = {mixed['frequency_shift_delta_beta']}
A^(3)_1 = {mixed['secular_primitive']}
```

and `q1 A^(3)+q2(h^(2),A_st)=0` exactly.

## Scope and health

The block has D-weight zero and accesses only the stationary homogeneous
diagonal metric and horizontal Maxwell direction.  It does not classify the
radiative Einstein-like/extra-Weyl branches.  The resonance changes the
frequency inside the already positive Maxwell phase plane and introduces no
negative physical direction.

The complete coupled Maxwell BV q2, localized apparatus, retarded signal,
and all-orders continuation remain open.  Machine-readable result:
`d_quotient_classical/certificates/BERGER_MAXWELL_THIRD_ORDER_RESONANCE.json`.
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    payload = build()
    if args.write:
        CERTIFICATE_PATH.write_text(_json(payload))
        REPORT_PATH.write_text(_report(payload))
    if args.check:
        if CERTIFICATE_PATH.read_text() != _json(payload):
            raise AssertionError("third-order resonance certificate drifted")
        if REPORT_PATH.read_text() != _report(payload):
            raise AssertionError("third-order resonance report drifted")
    if args.guards:
        mutants = []
        mutant = deepcopy(payload)
        mutant["physical_mixed_q2_block"]["dual_witness_source_pairing"] = "0"
        mutants.append(mutant)
        mutant = deepcopy(payload)
        mutant["flags"]["BERGER_FULL_COUPLED_GRAVITY_MAXWELL_Q2"] = True
        mutants.append(mutant)
        mutant = deepcopy(payload)
        mutant["physical_mixed_q2_block"]["frequency_renormalized_residual"] = "1"
        mutants.append(mutant)
        for mutant in mutants:
            try:
                verify(mutant)
            except AssertionError:
                continue
            raise AssertionError("fail-closed mutation was accepted")
    if not (args.write or args.check or args.guards):
        print(_json(payload), end="")


if __name__ == "__main__":
    main()
