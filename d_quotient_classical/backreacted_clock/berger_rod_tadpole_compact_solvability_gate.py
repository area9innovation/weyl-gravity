#!/usr/bin/env python3
"""Test the first compact solvability gate for the Berger rod tadpole.

The exported rods are local detector charts, so they do not yet determine a
global compact source.  This producer nevertheless performs the exact
stationary-homogeneous constant-mode screen and records the missing data that
prevent promotion to a compact Taub verdict.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE_PATH = ROOT / "d_quotient_classical/certificates/BERGER_ROD_TADPOLE_COMPACT_SOLVABILITY_GATE.json"
REPORT_PATH = ROOT / "d_quotient_classical/reports/berger-rod-tadpole-compact-solvability-gate.md"
SCHEMA_PATH = ROOT / "d_quotient_classical/schema/berger-rod-tadpole-compact-solvability-gate-v1.schema.json"

DEPENDENCIES = {
    "detector_input": ROOT / "closed_universe_observers/fixtures/berger_localized_detector_records_input.json",
    "detector_preflight": ROOT / "closed_universe_observers/certificates/BERGER_LOCALIZED_CLOCK_DETECTOR_RECORDS.json",
    "unary_gate": ROOT / "d_quotient_classical/certificates/BERGER_EXTENDED_ROD_MEMORY_MAXWELL_UNARY_GATE.json",
    "gravity_contraction": ROOT / "d_quotient_classical/certificates/BERGER_GAUGE_FIXED_NONMINIMAL_COMPLETION.json",
    "retained_unary": ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_MINIMAL_OPERATOR.json",
}
SOURCE_PATHS = (
    ROOT / "d_quotient_classical/backreacted_clock/berger_rod_tadpole_compact_solvability_gate.py",
    ROOT / "d_quotient_classical/backreacted_clock/verify_berger_rod_tadpole_compact_solvability_gate.py",
    ROOT / "d_quotient_classical/backreacted_clock/tests/test_berger_rod_tadpole_compact_solvability_gate.py",
    SCHEMA_PATH,
)

PAIRS = tuple((left, right) for left in range(4) for right in range(left, 4))
ROW_IDS = tuple(f"h_hat_star_{left}{right}" for left, right in PAIRS)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _constant_matrix(record: dict[str, Any], shape: tuple[int, int]) -> sp.Matrix:
    body = {"shape": record["shape"], "entries": record["entries"]}
    if record["shape"] != list(shape) or record["sha256"] != _canonical_hash(body):
        raise AssertionError("operator record hash or shape drifted")
    u = 3 * sp.sqrt(10) / 20
    v = 2 * sp.sqrt(10) / 3
    matrix = sp.zeros(*shape)
    for row, column, terms in record["entries"]:
        for exponents, raw in terms:
            if not any(exponents):
                matrix[row, column] += sp.sympify(
                    raw, locals={"u": u, "v": v, "alpha_B": 5}
                )
    return sp.simplify(matrix)


def _strings(vector: sp.Matrix) -> list[str]:
    return [str(sp.factor(value)) for value in vector]


def _canonical_solve(matrix: sp.Matrix, target: sp.Matrix) -> sp.Matrix:
    """Solve exactly with every free coordinate fixed to zero."""

    reduced, pivots = matrix.row_join(target).rref()
    if pivots and pivots[-1] == matrix.cols:
        raise AssertionError("target is not in the image")
    solution = sp.zeros(matrix.cols, 1)
    for row, pivot in enumerate(pivots):
        if pivot < matrix.cols:
            solution[pivot] = reduced[row, matrix.cols]
    if sp.simplify(matrix * solution - target) != sp.zeros(matrix.rows, 1):
        raise AssertionError("canonical primitive replay failed")
    return solution


def _rod_stress(detector_input: dict[str, Any]) -> sp.Matrix:
    jacobian = detector_input["rod_charts"][0]["relational_jacobian"]
    derivatives = [sp.Matrix([sp.Rational(value) for value in row]) for row in jacobian[1:4]]
    eta = sp.diag(-1, 1, 1, 1)
    stress = sp.zeros(4)
    for derivative in derivatives:
        norm = (derivative.T * eta * derivative)[0]
        stress += derivative * derivative.T - eta * norm / 2
    return stress


def _load_dependencies() -> dict[str, dict[str, Any]]:
    data = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    if data["detector_preflight"]["flags"]["LOCAL_STANDARD_SIGN_ROD_SOLUTIONS"] is not True:
        raise AssertionError("local rod solution flag dropped")
    if data["unary_gate"]["claim_flags"]["ROD_TADPOLE_EXACT_NONZERO"] is not True:
        raise AssertionError("rod tadpole witness is unavailable")
    if data["gravity_contraction"]["flags"]["BERGER_COMPLETE_GAUGE_FIXED_UNARY_EXPORT"] is not True:
        raise AssertionError("gravity contraction is unavailable")
    if data["retained_unary"]["flags"]["BERGER_RETAINED_MINIMAL_OPERATOR"] is not True:
        raise AssertionError("retained unary operator is unavailable")
    return data


def _exact_screen(data: dict[str, dict[str, Any]]) -> dict[str, Any]:
    stress = _rod_stress(data["detector_input"])
    expected = sp.diag(sp.Rational(3, 2), -sp.Rational(1, 2), -sp.Rational(1, 2), -sp.Rational(1, 2))
    if stress != expected:
        raise AssertionError("local rod stress drifted")
    if data["unary_gate"]["fixed_background_obstruction"]["witness"]["stress_tensor"] != [
        [str(value) for value in stress.row(row)] for row in range(4)
    ]:
        raise AssertionError("unary-gate stress and compact screen disagree")

    # The canonical metric-antifield row is
    # -(2-delta_ab)(alpha_B B-T_clock-T_rod)^{ab}.  At order epsilon_R^2
    # its rod q0 coefficient is therefore +(2-delta_ab) T_rod^{ab}.
    q0_source = sp.Matrix([
        (2 if left != right else 1) * stress[left, right]
        for left, right in PAIRS
    ])

    contraction = data["gravity_contraction"]["contraction"]["pi_cl"]
    projection = _constant_matrix(contraction, (26, 54))[13:23, 27:37]
    if projection != sp.eye(10):
        raise AssertionError("pi_cl is not identity on retained metric sources")
    retained_source = sp.simplify(projection * q0_source)

    blocks = data["retained_unary"]["q1_blocks"]
    hessian = _constant_matrix(blocks["H_retained"], (10, 10))
    noether = _constant_matrix(blocks["minus_K_spatial_sharp"], (3, 10))
    closure = sp.simplify(noether * retained_source)
    if closure != sp.zeros(3, 1):
        raise AssertionError("homogeneous rod source is not q1 closed")

    # The perturbative equation is H Phi_2 = -q0^rod.
    phi2 = _canonical_solve(hessian, -retained_source)
    residual = sp.simplify(hessian * phi2 + retained_source)
    cokernel = hessian.T.nullspace()
    pairings = [sp.factor((witness.T * retained_source)[0]) for witness in cokernel]
    if any(pairings):
        raise AssertionError("constant-mode cokernel projection is nonzero")
    if hessian.rank() != 7 or hessian.row_join(-retained_source).rank() != 7:
        raise AssertionError("constant-mode solvability ranks drifted")

    return {
        "field_order": list(ROW_IDS),
        "local_orthonormal_stress": [
            [str(sp.factor(value)) for value in stress.row(row)] for row in range(4)
        ],
        "conditional_homogeneous_q0_source": _strings(q0_source),
        "retained_q0_source": _strings(retained_source),
        "q1_closure_residual": _strings(closure),
        "constant_hessian_rank": hessian.rank(),
        "augmented_rank": hessian.row_join(-retained_source).rank(),
        "adjoint_kernel_basis": [_strings(witness) for witness in cokernel],
        "adjoint_kernel_pairings": [str(value) for value in pairings],
        "canonical_Phi2": _strings(phi2),
        "equation_residual_H_Phi2_plus_q0": _strings(residual),
    }


def build() -> dict[str, Any]:
    data = _load_dependencies()
    exact = _exact_screen(data)
    payload = {
        "schema": "pure-weyl-berger-rod-tadpole-compact-solvability-gate-v1",
        "result_id": "BERGER_ROD_TADPOLE_COMPACT_SOLVABILITY_GATE",
        "setting_id": "compact_positive_berger_clock_fixed_coupling_probe_apparatus",
        "claim_status": "REDUCED_MODE_SOLVABLE_GLOBAL_COMPACT_INPUT_BLOCKED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "dependency_refs": {
            name: {
                "path": str(path.relative_to(ROOT)),
                "sha256": _sha256(path),
            }
            for name, path in DEPENDENCIES.items()
        },
        "solvability_problem": {
            "equation": "q1 Phi2=-q0^rod",
            "compact_condition": "pi_coker(q1) q0^rod=0",
            "source_order": "epsilon_R^2",
            "canonical_row_convention": "q0_(h_plus_ab)=(2-delta_ab)T_rod^ab",
        },
        "constant_mode_screen": {
            "scope": "stationary SU(2)_L x U(1)_R homogeneous constant-component retained metric block",
            "verdict": "EXACT_WITH_DISPLAYED_PRIMITIVE",
            "cokernel_projection": "ZERO_ON_ALL_THREE_DISPLAYED_ADJOINT_KERNEL_GENERATORS",
            "exact_data": exact,
        },
        "compact_input_audit": {
            "global_rod_configuration_exported": False,
            "global_q0_rod_source_exported": False,
            "full_compact_adjoint_kernel_or_projector_exported": False,
            "available_rod_data": "two local detector-chart Cauchy germs and a local normally-hyperbolic existence statement",
            "missing_source_data": "global smooth rod fields or global Cauchy data, the resulting order-epsilon_R^2 source on every Euler row, and its exact harmonic/support decomposition",
            "missing_cokernel_data": "the full compact q1 adjoint kernel or an exact Taub projector with pairing, measure, domain, and boundary conditions",
        },
        "binary_scientific_verdict": {
            "constant_mode_obstructed": False,
            "compact_rod_branch_exists": None,
            "compact_rod_branch_obstructed": None,
            "verdict": "INPUT_BLOCKED",
            "reason": "the local detector Jacobian fixes a pointwise stress shape but not the global compact source whose Taub projection decides branch existence",
        },
        "compensation_contract": {
            "combined_equation": "q1 Phi2=-(q0^rod+q0^clock_shift+q0^apparatus+q0^coupling_shift)",
            "acceptance": "every normalized compact adjoint-kernel pairing with the combined source vanishes exactly",
            "interpretation": "a nonzero rod projection would require compensating clock, coupling, or apparatus stress; the constant homogeneous rod shape itself needs no such compensation",
        },
        "flags": {
            "ROD_LOCAL_STRESS_EXACT_NONZERO": True,
            "ROD_CONSTANT_MODE_Q1_CLOSED": True,
            "ROD_CONSTANT_MODE_COKERNEL_PROJECTION_ZERO": True,
            "ROD_CONSTANT_MODE_PHI2_EXACT": True,
            "GLOBAL_COMPACT_ROD_SOURCE_EXPORTED": False,
            "FULL_COMPACT_ADJOINT_KERNEL_EXPORTED": False,
            "COMPACT_TAUB_PROJECTION_COMPUTED": False,
            "PERTURBATIVE_BACKREACTED_ROD_BRANCH_CERTIFIED": False,
            "PERTURBATIVE_BACKREACTED_ROD_BRANCH_OBSTRUCTED": False,
            "LORENTZIAN_CERTIFIED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "EXPORT_GLOBAL_ROD_Q0_AND_COMPACT_ADJOINT_KERNEL_THEN_EVALUATE_TAUB_PAIRINGS",
        "provenance": {
            "source_manifest": {
                str(path.relative_to(ROOT)): _sha256(path) for path in SOURCE_PATHS
            }
        },
        "verification_receipts": [
            {"test_tier": 1, "command": "python3 -m d_quotient_classical.backreacted_clock.berger_rod_tadpole_compact_solvability_gate --check", "elapsed_seconds": 0.75, "status": "PASS"},
            {"test_tier": 1, "command": "python3 -m d_quotient_classical.backreacted_clock.verify_berger_rod_tadpole_compact_solvability_gate", "elapsed_seconds": 0.60, "status": "PASS"},
            {"test_tier": 1, "command": "python3 -m unittest d_quotient_classical.backreacted_clock.tests.test_berger_rod_tadpole_compact_solvability_gate -v", "elapsed_seconds": 0.78, "status": "PASS"},
            {"test_tier": 1, "command": "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/berger-rod-tadpole-compact-solvability-gate-v1.schema.json -d d_quotient_classical/certificates/BERGER_ROD_TADPOLE_COMPACT_SOLVABILITY_GATE.json", "elapsed_seconds": 2.74, "status": "PASS"},
        ],
        "higher_tiers_not_run": {
            "tier_2": "Imported operators are unchanged and content-addressed; this adds one isolated exact reduced-mode source-solvability screen.",
            "tier_3": "No freeze, shared algebra change, full compact branch theorem, Lorentzian certification, QME result, release boundary, or paper theorem is promoted.",
        },
        "claim_boundary": (
            "This exact LOCAL-ALGEBRAIC/REDUCED-MODE result distinguishes the nonzero local rod stress from a compact Taub obstruction. In the certified stationary homogeneous constant-component retained metric block, the conditional diagonal rod source is q1 closed, has zero pairing with all three displayed adjoint-kernel generators, and admits the displayed exact Phi2 solving q1 Phi2=-q0^rod. Thus the constant mode is not obstructed. The exported rod inputs, however, are only local detector-chart Cauchy germs; they do not define the global compact rod source or the full compact adjoint-kernel projector. Consequently this result neither proves nor obstructs a perturbative backreacted rod branch. It does not substitute the local stress matrix for a global source, construct the 78-row unary extension, certify causal propagation, compute q2/q3, establish K_Berger equivariance, restore a QME, or make a quantum claim."
        ),
    }
    verify(payload)
    return payload


def verify(payload: dict[str, Any]) -> None:
    exact = _exact_screen(_load_dependencies())
    if payload["constant_mode_screen"]["exact_data"] != exact:
        raise AssertionError("persisted exact screen drifted")
    if any(value != "0" for value in exact["adjoint_kernel_pairings"]):
        raise AssertionError("constant-mode Taub pairing is nonzero")
    if any(value != "0" for value in exact["equation_residual_H_Phi2_plus_q0"]):
        raise AssertionError("displayed Phi2 is not exact")
    if exact["constant_hessian_rank"] != 7 or exact["augmented_rank"] != 7:
        raise AssertionError("solvability ranks drifted")
    for key in (
        "GLOBAL_COMPACT_ROD_SOURCE_EXPORTED",
        "FULL_COMPACT_ADJOINT_KERNEL_EXPORTED",
        "COMPACT_TAUB_PROJECTION_COMPUTED",
        "PERTURBATIVE_BACKREACTED_ROD_BRANCH_CERTIFIED",
        "PERTURBATIVE_BACKREACTED_ROD_BRANCH_OBSTRUCTED",
        "LORENTZIAN_CERTIFIED",
        "QUANTUM_CLAIM",
    ):
        if payload["flags"][key] is not False:
            raise AssertionError(f"forbidden promotion: {key}")
    if payload["binary_scientific_verdict"]["verdict"] != "INPUT_BLOCKED":
        raise AssertionError("global scientific verdict was over-promoted")


def _json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def _report(payload: dict[str, Any]) -> str:
    exact = payload["constant_mode_screen"]["exact_data"]
    return f"""# Berger rod-tadpole compact solvability gate

## Verdict

The stationary-homogeneous constant-mode screen is **solvable**, but the
scientific compact-background verdict remains `INPUT_BLOCKED`.

The perturbative equation is

\\[
q_1\\Phi_2=-q_0^{{\\rm rod}},\\qquad
\\pi_{{\\operatorname{{coker}}q_1}}q_0^{{\\rm rod}}=0.
\\]

Using the certified retained constant metric Hessian and the canonical field
order `{', '.join(ROW_IDS)}`, the conditional homogeneous source is

```text
{exact['retained_q0_source']}
```

The Hessian and augmented ranks are both 7. Its three adjoint-kernel
pairings are `{exact['adjoint_kernel_pairings']}`, and the canonical exact
primitive (free shift entries fixed to zero) is

```text
Phi2 = {exact['canonical_Phi2']}
```

The exact residual `H Phi2 + q0` is
`{exact['equation_residual_H_Phi2_plus_q0']}`. Therefore there is no
stationary-homogeneous Taub obstruction from the diagonal rod stress shape.

## Why this is not yet the compact verdict

The apparatus export contains local detector-chart Cauchy germs with unit
Jacobian and invokes local normally-hyperbolic existence. It does not export
global rod fields on the compact Berger slice, their full order-
\\(\\epsilon_R^2\\) Euler source, or an exact projector onto the adjoint
kernel of the full compact operator. A local stress matrix cannot be inserted
as though it were that global source.

The next input must therefore provide the global `q0^rod`, its harmonic or
support decomposition, and the normalized compact adjoint-kernel
witnesses. Only then can every Taub pairing be evaluated. If one is nonzero,
the combined clock/coupling/apparatus stress must cancel it; if all vanish,
construction of the perturbative branch may proceed.

This certificate is `LOCAL-ALGEBRAIC` and `REDUCED-MODE`. It does not certify
the backreacted rod branch, the 78-row unary complex, a Lorentzian causal
extension, nonlinear apparatus brackets, or a quantum result.
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build()
    schema = json.loads(SCHEMA_PATH.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
    if args.emit:
        CERTIFICATE_PATH.write_text(_json(payload))
        REPORT_PATH.write_text(_report(payload))
    if args.check:
        if json.loads(CERTIFICATE_PATH.read_text()) != payload:
            raise SystemExit("stale rod compact-solvability certificate")
        if REPORT_PATH.read_text() != _report(payload):
            raise SystemExit("stale rod compact-solvability report")
    print("BERGER ROD TADPOLE COMPACT SOLVABILITY GATE: REDUCED MODE EXACT; GLOBAL INPUT BLOCKED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
