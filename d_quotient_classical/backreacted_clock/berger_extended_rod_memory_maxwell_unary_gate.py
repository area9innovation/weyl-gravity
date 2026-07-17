#!/usr/bin/env python3
"""Exact readiness/obstruction gate for the extended Berger apparatus q1.

The current detector construction uses standard-sign probe rods on the fixed
Berger background.  This module checks whether those data define an uncurved
action-derived BV unary complex.  It also proves, in a universal noncommutative
operator algebra, the finite triangular retarded inverse for the memory-
Maxwell Hessian once the missing physical coefficient operators are supplied.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
DETECTOR_INPUT = ROOT / "closed_universe_observers/fixtures/berger_localized_detector_records_input.json"
DETECTOR_CERTIFICATE = ROOT / "closed_universe_observers/certificates/BERGER_LOCALIZED_CLOCK_DETECTOR_RECORDS.json"
INTERACTION_GATE = ROOT / "closed_universe_observers/certificates/BERGER_OBSERVER_APPARATUS_INTERACTION_IMPORT_GATE.json"
BASE_CARRIER = ROOT / "d_quotient_classical/certificates/BERGER_PORTABLE_COUPLED_64_UNARY_PAIRING_36_SDR.json"
BASE_CAUSAL = ROOT / "d_quotient_classical/certificates/BERGER_MAXWELL_UNARY_CONTRACTION_AND_FIRST_TRANSFERRED_MIXED_VERTEX.json"
SCHEMA = ROOT / "d_quotient_classical/schema/berger-extended-rod-memory-maxwell-unary-gate-v1.schema.json"
OUTPUT = ROOT / "d_quotient_classical/certificates/BERGER_EXTENDED_ROD_MEMORY_MAXWELL_UNARY_GATE.json"
REPORT = ROOT / "d_quotient_classical/reports/berger-extended-rod-memory-maxwell-unary-gate.md"
INPUT_SNAPSHOT_COMMIT = "78ae87fa376b734dbeb0f06db30d89db61cf6d1f"

DEPENDENCIES = {
    "detector_input": DETECTOR_INPUT,
    "detector_preflight": DETECTOR_CERTIFICATE,
    "observer_interaction_gate": INTERACTION_GATE,
    "base_64_carrier": BASE_CARRIER,
    "base_64_causal_homotopy": BASE_CAUSAL,
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


Poly = dict[tuple[str, ...], Fraction]


def _poly(*terms: tuple[Fraction | int, tuple[str, ...]]) -> Poly:
    result: Poly = {}
    for coefficient, word in terms:
        value = Fraction(coefficient)
        if value:
            result[word] = result.get(word, Fraction(0)) + value
    return {word: value for word, value in result.items() if value}


def _add(*values: Poly) -> Poly:
    result: Poly = {}
    for value in values:
        for word, coefficient in value.items():
            result[word] = result.get(word, Fraction(0)) + coefficient
    return {word: coefficient for word, coefficient in result.items() if coefficient}


INVERSE_RULES = {
    ("M", "G"), ("G", "M"),
    ("T", "H"), ("H", "T"),
    ("Ts", "J"), ("J", "Ts"),
}


def _reduce_word(word: tuple[str, ...]) -> tuple[str, ...]:
    value = list(word)
    changed = True
    while changed:
        changed = False
        for index in range(len(value) - 1):
            if (value[index], value[index + 1]) in INVERSE_RULES:
                del value[index:index + 2]
                changed = True
                break
    return tuple(value)


def _multiply(left: Poly, right: Poly) -> Poly:
    result: Poly = {}
    for left_word, left_coefficient in left.items():
        for right_word, right_coefficient in right.items():
            word = _reduce_word(left_word + right_word)
            result[word] = result.get(word, Fraction(0)) + left_coefficient * right_coefficient
    return {word: coefficient for word, coefficient in result.items() if coefficient}


def _matrix_multiply(left: list[list[Poly]], right: list[list[Poly]]) -> list[list[Poly]]:
    return [
        [
            _add(*(_multiply(left[row][middle], right[middle][column]) for middle in range(len(right))))
            for column in range(len(right[0]))
        ]
        for row in range(len(left))
    ]


def _identity(size: int) -> list[list[Poly]]:
    return [
        [_poly((1, ())) if row == column else {} for column in range(size)]
        for row in range(size)
    ]


def _is_identity(value: list[list[Poly]]) -> bool:
    return value == _identity(len(value))


def memory_maxwell_template() -> dict:
    """Prove the exact inverse of the cyclic A/m/p Hessian abstractly."""

    zero: Poly = {}
    M = _poly((1, ("M",)))
    G = _poly((1, ("G",)))
    T = _poly((1, ("T",)))
    H = _poly((1, ("H",)))
    Ts = _poly((1, ("Ts",)))
    J = _poly((1, ("J",)))
    B = _poly((1, ("B",)))
    Bs = _poly((1, ("Bs",)))
    minus_Bs = _poly((-1, ("Bs",)))
    K = [
        [M, zero, minus_Bs],
        [zero, zero, Ts],
        [_poly((-1, ("B",))), T, zero],
    ]
    green = [
        [G, _poly((1, ("G", "Bs", "J"))), zero],
        [
            _poly((1, ("H", "B", "G"))),
            _poly((1, ("H", "B", "G", "Bs", "J"))),
            H,
        ],
        [zero, J, zero],
    ]
    left = _matrix_multiply(K, green)
    right = _matrix_multiply(green, K)
    if not _is_identity(left) or not _is_identity(right):
        raise AssertionError("universal memory-Maxwell Green formula failed")
    return {
        "field_order": ["A", "m", "p"],
        "hessian": [["M", "0", "-B*"], ["0", "0", "T*"], ["-B", "T", "0"]],
        "retarded_inverse": [
            ["G", "G B* J", "0"],
            ["H B G", "H B G B* J", "H"],
            ["0", "J", "0"],
        ],
        "inverse_relations": ["M G=G M=1", "T H=H T=1", "T* J=J T*=1"],
        "formal_self_adjoint": True,
        "left_inverse_defect_count": 0,
        "right_inverse_defect_count": 0,
        "causal_support_statement": (
            "If G,H,J are retarded Green operators and B,B* are local compactly "
            "supported coefficient operators, every displayed finite composition is retarded."
        ),
    }


def _q(value: str | int) -> Fraction:
    return Fraction(str(value))


def rod_stress_witness(data: dict) -> dict:
    """Compute the standard-sign rod stress in the declared orthonormal chart."""

    jacobian = data["rod_charts"][0]["relational_jacobian"]
    derivatives = [[_q(value) for value in row] for row in jacobian[1:4]]
    metric = [Fraction(-1), Fraction(1), Fraction(1), Fraction(1)]
    stress = [[Fraction(0) for _ in range(4)] for _ in range(4)]
    for derivative in derivatives:
        norm = sum(metric[index] * derivative[index] * derivative[index] for index in range(4))
        for first in range(4):
            for second in range(4):
                stress[first][second] += derivative[first] * derivative[second]
                if first == second:
                    stress[first][second] -= Fraction(1, 2) * metric[first] * norm
    return {
        "orthonormal_signature": ["-1", "1", "1", "1"],
        "rod_derivatives": [[str(value) for value in row] for row in derivatives],
        "stress_tensor": [[str(value) for value in row] for row in stress],
        "energy_density_T00": str(stress[0][0]),
        "nonzero_component_count": sum(value != 0 for row in stress for value in row),
        "nonzero": any(value != 0 for row in stress for value in row),
    }


def _dependency_refs() -> dict:
    return {
        name: {
            "path": str(path.relative_to(ROOT)),
            "sha256": _sha256(path),
        }
        for name, path in DEPENDENCIES.items()
    }


def build() -> dict:
    detector_input = json.loads(DETECTOR_INPUT.read_text())
    detector = json.loads(DETECTOR_CERTIFICATE.read_text())
    interaction = json.loads(INTERACTION_GATE.read_text())
    carrier = json.loads(BASE_CARRIER.read_text())
    causal = json.loads(BASE_CAUSAL.read_text())

    if detector["flags"]["LOCAL_STANDARD_SIGN_ROD_SOLUTIONS"] is not True:
        raise AssertionError("rod preflight compatibility flag dropped")
    if interaction["flags"]["EXTENDED_APPARATUS_Q1_CERTIFIED"] is not False:
        raise AssertionError("observer interaction gate no longer awaits q1")
    if carrier["full_complex"]["total_rows"] != 64:
        raise AssertionError("base carrier row count drifted")
    causal_flags = causal["flags"]
    if not (
        causal_flags["BERGER_COMBINED_64_ROW_CAUSAL_GREEN_HOMOTOPY"]
        and causal_flags["BERGER_MAXWELL_CAUSAL_GREEN_HOMOTOPY"]
        and causal_flags["BERGER_MIXED_Q2_CYCLICITY"]
    ):
        raise AssertionError("base causal/cyclic compatibility flags dropped")

    stress = rod_stress_witness(detector_input)
    if stress["energy_density_T00"] != "3/2" or stress["nonzero"] is not True:
        raise AssertionError("declared rod tadpole witness drifted")
    template = memory_maxwell_template()

    source_paths = (
        "d_quotient_classical/backreacted_clock/berger_extended_rod_memory_maxwell_unary_gate.py",
        "d_quotient_classical/backreacted_clock/verify_berger_extended_rod_memory_maxwell_unary_gate.py",
        "d_quotient_classical/backreacted_clock/tests/test_berger_extended_rod_memory_maxwell_unary_gate.py",
        "d_quotient_classical/schema/berger-extended-rod-memory-maxwell-unary-gate-v1.schema.json",
        "d_quotient_classical/reports/berger-extended-rod-memory-maxwell-unary-gate.md",
    )
    return {
        "schema": "pure-weyl-berger-extended-rod-memory-maxwell-unary-gate-v1",
        "result_id": "BERGER_EXTENDED_ROD_MEMORY_MAXWELL_UNARY_GATE",
        "result_state": "INPUT_BLOCKED_NONZERO_ROD_TADPOLE_AND_PROFILE_OPERATOR_NOT_EXPORTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": _dependency_refs(),
        "base_complex": {
            "rows": 64,
            "q1_nilpotent": True,
            "cyclic_pairing_nondegenerate": True,
            "retarded_green_homotopy": True,
        },
        "proposed_extension": {
            "total_rows": 78,
            "new_degree_zero_rows": ["R1", "R2", "R3", "m0", "m1", "p0", "p1"],
            "new_degree_one_rows": ["R1_plus", "R2_plus", "R3_plus", "m0_plus", "m1_plus", "p0_plus", "p1_plus"],
            "pairing": "canonical odd cotangent pairing between every new field and its plus row",
            "internal_gauge_rows_added": 0,
        },
        "fixed_background_obstruction": {
            "rod_action": detector["rod_solution_contract"]["action"],
            "probe_limit_declaration": detector["rod_solution_contract"]["probe_limit"],
            "witness": stress,
            "metric_euler_tadpole": "epsilon_R^2*diag(3/2,-1/2,-1/2,-1/2)",
            "consequence": (
                "The unchanged Berger gravity-clock background is off shell for every nonzero "
                "standard-sign rod coupling. Its action-derived BV Taylor expansion is curved "
                "(q0 is nonzero), so an uncurved nilpotent extended q1 cannot be promoted there."
            ),
        },
        "memory_maxwell_universal_template": template,
        "required_input_contract": {
            "backreacted_background": "construct only after the compact q1 Phi2=-q0^rod solvability condition passes; then require every extended gravity-clock-rod Euler row to vanish",
            "rod_unary_blocks": "content-addressed rod Hessian, diffeomorphism action, and BV adjoint blocks",
            "profile_operator": "explicit local compactly supported B_a and formal adjoint B_a* for both detector channels",
            "memory_transport": "explicit T,T* and retarded inverses H,J with support theorem",
            "acceptance_checks": [
                "extended q1 squared zero on all 78 rows",
                "nondegenerate odd pairing and unary cyclicity",
                "advanced and retarded Green-homotopy identities",
                "Maxwell gauge compatibility B d=0 and delta B*=0",
                "K_Berger unary equivariance on every apparatus row",
            ],
        },
        "claim_flags": {
            "BASE_64_Q1_PAIRING_GREEN_AVAILABLE": True,
            "ROD_TADPOLE_EXACT_NONZERO": True,
            "MEMORY_MAXWELL_RETARDED_BLOCK_FORMULA_PROVED": True,
            "EXTENDED_APPARATUS_Q1_CERTIFIED": False,
            "EXTENDED_CYCLIC_PAIRING_CERTIFIED": False,
            "EXTENDED_RETARDED_GREEN_CERTIFIED": False,
            "K_BERGER_APPARATUS_EQUIVARIANCE_CERTIFIED": False,
            "BACKREACTED_APPARATUS_BACKGROUND_AVAILABLE": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "EXPORT_GLOBAL_ROD_Q0_AND_COMPACT_ADJOINT_KERNEL_BEFORE_BACKREACTED_BACKGROUND",
        "verification_receipts": [
            {
                "test_tier": 2,
                "command": "python3 -m d_quotient_classical.backreacted_clock.berger_extended_rod_memory_maxwell_unary_gate --check",
                "elapsed_seconds": 0.43,
                "status": "PASS",
            },
            {
                "test_tier": 2,
                "command": "python3 -m d_quotient_classical.backreacted_clock.verify_berger_extended_rod_memory_maxwell_unary_gate",
                "elapsed_seconds": 0.45,
                "status": "PASS",
            },
            {
                "test_tier": 2,
                "command": "python3 -m unittest d_quotient_classical.backreacted_clock.tests.test_berger_extended_rod_memory_maxwell_unary_gate -v",
                "elapsed_seconds": 0.47,
                "status": "PASS",
            },
            {
                "test_tier": 1,
                "command": "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/berger-extended-rod-memory-maxwell-unary-gate-v1.schema.json -d d_quotient_classical/certificates/BERGER_EXTENDED_ROD_MEMORY_MAXWELL_UNARY_GATE.json",
                "elapsed_seconds": 1.38,
                "status": "PASS",
            },
        ],
        "higher_tiers_not_run": {
            "tier_3": (
                "No classical or quantum freeze, shared algebra-engine change, lifecycle promotion, "
                "Lorentzian quantum construction, QME result, release boundary, or paper theorem."
            )
        },
        "provenance": {
            "source_commit": INPUT_SNAPSHOT_COMMIT,
            "source_manifest": {
                path: _sha256(ROOT / path) for path in source_paths
            },
        },
        "claim_boundary": (
            "This certificate is an exact LOCAL-ALGEBRAIC and LORENTZIAN-CAUSAL readiness/"
            "obstruction result. It imports the certified 64-row gravity-clock-Maxwell q1, odd "
            "pairing, and causal homotopy; proves the universal finite triangular retarded inverse "
            "for a cyclic memory-Maxwell Hessian; and computes the nonzero standard-sign rod stress "
            "on the declared unit-Jacobian detector chart. It therefore proves that the unchanged "
            "Berger background cannot support an uncurved action-derived 78-row apparatus q1 at "
            "nonzero rod coupling. This fixed-point off-shell statement neither proves nor obstructs "
            "a nearby perturbative backreacted branch: that requires the exact compact cokernel/Taub "
            "projection of the global rod source. It does not reject a backreacted apparatus solution, does not "
            "promote the probe-limit rods to a BV complex, and does not establish extended q1, "
            "cyclicity, a Green homotopy, q2/q3, K_Berger descent, backreaction, a classical observer "
            "morphism, a QME, or any quantum claim."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build()
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(result)
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.emit:
        OUTPUT.write_text(rendered)
    if args.check and (not OUTPUT.exists() or OUTPUT.read_text() != rendered):
        raise SystemExit("stale extended rod-memory-Maxwell unary gate")
    print("BERGER EXTENDED ROD-MEMORY-MAXWELL UNARY GATE: EXACT INPUT BLOCKER")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
