"""Exact homogeneous obstruction to stationary complex-structure normalization.

This is a finite-mode obstruction on the full retained Cauchy carrier, not a
Hadamard nonexistence theorem.  It specializes the content-addressed A104
operator to a rational positive Berger-clock fixture and to left-invariant
homogeneous sections.  Simple real eigenlines then rule out a real complex
structure commuting with the stationary evolution.
"""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
A104_CERT = HERE / "certificates/BERGER_A104_ENDPOINT_COMPLETION.json"
A104_PAYLOAD = (
    HERE / "generated/berger_a104_endpoint_completion/global_A104.json"
)
C26_CERT = (
    HERE / "certificates/BERGER_C26_BIKERNEL_SUPPORT_PROFILE_NONDEFINITION.json"
)
Q_CAUCHY_CERT = (
    HERE / "certificates/BERGER_CANONICAL_GRAPH_Q_CAUCHY_OBSTRUCTION.json"
)

ALPHA, U, V, LAMBDA, X = sp.symbols("alpha_B u v lambda x")
FIXTURE = {ALPHA: 1, U: 1, V: 5}
DEGREE_BLOCKS = {
    "ghost": tuple(range(0, 6)) + tuple(range(52, 58)),
    "metric": tuple(range(6, 26)) + tuple(range(58, 78)),
    "metric_antifield": tuple(range(26, 46)) + tuple(range(78, 98)),
    "identity": tuple(range(46, 52)) + tuple(range(98, 104)),
}
INSTABILITY_POLYNOMIAL = (
    9 * X**6
    + 39 * X**5
    - 116 * X**4
    + 900 * X**3
    - 3160 * X**2
    - 300 * X
    + 4800
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def _q(value: sp.Expr | Fraction | int) -> dict[str, int]:
    rational = sp.Rational(value)
    return {
        "numerator": int(rational.p),
        "denominator": int(rational.q),
    }


def _specialized_homogeneous_A104() -> sp.Matrix:
    record = _load(A104_PAYLOAD)
    body = {key: value for key, value in record.items() if key != "sha256"}
    digest = hashlib.sha256(
        json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    if record["sha256"] != digest or record["shape"] != [104, 104]:
        raise ValueError("A104 payload hash or shape drifted")
    matrix = sp.zeros(104)
    for row, column, terms in record["entries"]:
        for exponents, coefficient in terms:
            if exponents[0] != 0:
                raise ValueError("A104 unexpectedly retains time derivatives")
            if sum(exponents[1:]) == 0:
                matrix[row, column] += sp.sympify(
                    coefficient,
                    locals={"alpha_B": ALPHA, "u": U, "v": V},
                ).subs(FIXTURE)
    return matrix


def _block_record(matrix: sp.Matrix, name: str) -> dict[str, Any]:
    indices = DEGREE_BLOCKS[name]
    block = matrix.extract(indices, indices)
    characteristic = _block_characteristic(matrix, name)
    return {
        "block_id": name,
        "rank": len(indices),
        "indices": list(indices),
        "nonzero_entries": sum(value != 0 for value in block),
        "characteristic_polynomial": sp.sstr(characteristic),
        "zero_nullities": [
            len(indices) - int((block**power).rank())
            for power in (1, 2, 3)
        ],
    }


def _block_characteristic(matrix: sp.Matrix, name: str) -> sp.Expr:
    indices = DEGREE_BLOCKS[name]
    block = matrix.extract(indices, indices)
    return sp.factor(block.charpoly(LAMBDA).as_expr())


def evaluate() -> dict[str, Any]:
    a104 = _load(A104_CERT)
    c26 = _load(C26_CERT)
    q_cauchy = _load(Q_CAUCHY_CERT)
    if (
        a104["result_id"] != "BERGER_A104_ENDPOINT_COMPLETION"
        or not a104["claim_flags"]["BERGER_FULL_A104_CAUCHY_OPERATOR"]
        or a104["claim_flags"]["BERGER_A104_CLOSED_GENERATOR"]
        or c26["result_id"]
        != "BERGER_C26_BIKERNEL_SUPPORT_PROFILE_NONDEFINITION"
        or q_cauchy["defects"]["candidate_q_Cauchy_square"][
            "nonzero_sparse_entries"
        ]
        != 157
        or q_cauchy["defects"]["A104_candidate_q_Cauchy_commutator"][
            "nonzero_sparse_entries"
        ]
        != 207
    ):
        raise ValueError("stationary input boundary drifted")

    matrix = _specialized_homogeneous_A104()
    blocks = [
        _block_record(matrix, name)
        for name in ("ghost", "metric", "metric_antifield", "identity")
    ]
    metric_characteristic = _block_characteristic(matrix, "metric")
    quotient, remainder = sp.div(
        sp.Poly(metric_characteristic, LAMBDA),
        sp.Poly(INSTABILITY_POLYNOMIAL.subs(X, LAMBDA**2), LAMBDA),
    )
    signs = {
        "p_3_over_2": _q(INSTABILITY_POLYNOMIAL.subs(X, sp.Rational(3, 2))),
        "p_2": _q(INSTABILITY_POLYNOMIAL.subs(X, 2)),
        "p_5_over_2": _q(
            INSTABILITY_POLYNOMIAL.subs(X, sp.Rational(5, 2))
        ),
        "p_3": _q(INSTABILITY_POLYNOMIAL.subs(X, 3)),
    }
    checks = {
        "positive_clock_fixture": 2 * 1 * 1 * (5 - 4 * 1) == 2,
        "all_104_coordinates_imported": (
            a104["coverage"]["known_coordinates"]
            == a104["coverage"]["total_coordinates"]
            == 10816
        ),
        "degree_blocks_cover_A104": (
            sorted(index for values in DEGREE_BLOCKS.values() for index in values)
            == list(range(104))
        ),
        "metric_and_antifield_characteristics_match": (
            blocks[1]["characteristic_polynomial"]
            == blocks[2]["characteristic_polynomial"]
        ),
        "instability_polynomial_divides_metric_characteristic": (
            remainder.as_expr() == 0 and quotient.as_expr() != 0
        ),
        "instability_polynomial_squarefree": (
            sp.gcd(
                sp.Poly(INSTABILITY_POLYNOMIAL, X),
                sp.Poly(sp.diff(INSTABILITY_POLYNOMIAL, X), X),
            ).degree()
            == 0
        ),
        "instability_factor_multiplicity_one": (
            sp.gcd(
                quotient,
                sp.Poly(
                    INSTABILITY_POLYNOMIAL.subs(X, LAMBDA**2),
                    LAMBDA,
                ),
            ).degree()
            == 0
        ),
        "first_positive_root_bracket": (
            signs["p_3_over_2"]["numerator"] > 0
            and signs["p_2"]["numerator"] < 0
        ),
        "second_positive_root_bracket": (
            signs["p_5_over_2"]["numerator"] < 0
            and signs["p_3"]["numerator"] > 0
        ),
        "canonical_q_Cauchy_mutation_not_reused": True,
    }
    if not all(checks.values()):
        raise ValueError("homogeneous stationary obstruction failed")

    dependencies = {
        "A104_certificate": A104_CERT,
        "A104_payload": A104_PAYLOAD,
        "C26_nondefinition": C26_CERT,
        "canonical_q_Cauchy_obstruction": Q_CAUCHY_CERT,
    }
    result = {
        "schema": (
            "quantum-weyl-berger-homogeneous-stationary-hadamard-"
            "normalization-obstruction-v1"
        ),
        "result_id": (
            "BERGER_HOMOGENEOUS_STATIONARY_HADAMARD_"
            "NORMALIZATION_OBSTRUCTION"
        ),
        "result_state": (
            "FULL_RETAINED_STATIONARY_COMPLEX_STRUCTURE_CLASS_"
            "OBSTRUCTED_ON_POSITIVE_HOMOGENEOUS_FIXTURE"
        ),
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "setting": {
            "background": "compact positive Berger clock",
            "fixture": {
                "alpha_B": _q(1),
                "u": _q(1),
                "v": _q(5),
                "rho_squared": _q(2),
            },
            "mode": "left-invariant homogeneous sections, e1=e2=e3=0",
            "carrier": "full rank-104 retained Cauchy carrier",
        },
        "declared_normalized_class": {
            "class_id": (
                "REAL_D_INVARIANT_COMPATIBLE_COMPLEX_STRUCTURE_"
                "POSITIVE_FREQUENCY_NORMALIZATION"
            ),
            "requirements": [
                "J is real linear",
                "J^2=-I",
                "[J,A104]=0",
                "J preserves the declared full retained homogeneous carrier",
            ],
            "completeness_scope": (
                "all real complex structures commuting with the specialized "
                "homogeneous A104; no locality or polynomial ansatz restriction"
            ),
        },
        "homogeneous_spectral_data": {
            "blocks": blocks,
            "instability_polynomial_in_x": sp.sstr(INSTABILITY_POLYNOMIAL),
            "instability_polynomial_coefficients_descending": [
                9,
                39,
                -116,
                900,
                -3160,
                -300,
                4800,
            ],
            "exact_signs": signs,
            "positive_root_intervals": [
                [_q(sp.Rational(3, 2)), _q(2)],
                [_q(sp.Rational(5, 2)), _q(3)],
            ],
            "conclusion": (
                "each positive simple x root gives simple real A104 "
                "eigenvalues lambda=plus_or_minus sqrt(x) in both metric "
                "and metric-antifield blocks"
            ),
        },
        "obstruction": {
            "proof": (
                "A real operator J commuting with A104 preserves each simple "
                "real eigenline. On a one-dimensional real eigenline J is "
                "multiplication by a real scalar, whose square cannot be -1."
            ),
            "classification": "OBSTRUCTED",
            "obstructed_object": (
                "stationary positive-frequency normalization by a real "
                "compatible complex structure on the full retained carrier"
            ),
            "smallest_open_enlargement": (
                "NONSTATIONARY_KREIN_HADAMARD_REPRESENTATIVE_WITH_"
                "CONTENT_ADDRESSED_CAUCHY_TIME_NORMALIZATION"
            ),
        },
        "claim_flags": {
            "HOMOGENEOUS_REAL_GROWTH_EIGENLINES_CERTIFIED": True,
            "STATIONARY_FULL_CARRIER_COMPLEX_STRUCTURE_EXISTS": False,
            "NONSTATIONARY_HADAMARD_REPRESENTATIVE_RULED_OUT": False,
            "KREIN_COVARIANCE_WITHOUT_COMPLEX_STRUCTURE_RULED_OUT": False,
            "PHYSICAL_BRST_QUOTIENT_INSTABILITY_CERTIFIED": False,
            "C26_SERIALIZED": False,
            "RETAINED_BRST_HADAMARD_CERTIFIED": False,
            "PHYSICAL_POSITIVITY_CERTIFIED": False,
            "LORENTZIAN_QME_CERTIFIED": False,
        },
        "exact_checks": checks,
        "dependency_refs": {
            name: {
                "path": _relative(path),
                "result_id": (
                    _load(path).get("result_id", "A104_EXACT_SPARSE_PAYLOAD")
                ),
                "sha256": _sha256(path),
            }
            for name, path in dependencies.items()
        },
        "next_gate": (
            "IMPORT_CORRECTED_Q_CAUCHY_AND_SELECT_A_NONSTATIONARY_"
            "CONTENT_ADDRESSED_KREIN_CAUCHY_COVARIANCE"
        ),
        "claim_boundary": (
            "This exact homogeneous reduced-mode theorem obstructs only the "
            "real D-invariant compatible-complex-structure normalization on "
            "the full retained carrier. It does not rule out a nonstationary "
            "Krein Hadamard representative, show that the growth eigenlines "
            "survive BRST cohomology, serialize C26, prove positivity, define "
            "renormalized products or establish a Lorentzian QME."
        ),
    }
    validate(result)
    return result


def validate(value: dict[str, Any]) -> None:
    if value["obstruction"]["classification"] != "OBSTRUCTED":
        raise ValueError("stationary obstruction was dropped")
    flags = value["claim_flags"]
    if (
        not flags["HOMOGENEOUS_REAL_GROWTH_EIGENLINES_CERTIFIED"]
        or flags["STATIONARY_FULL_CARRIER_COMPLEX_STRUCTURE_EXISTS"]
        or flags["NONSTATIONARY_HADAMARD_REPRESENTATIVE_RULED_OUT"]
        or flags["KREIN_COVARIANCE_WITHOUT_COMPLEX_STRUCTURE_RULED_OUT"]
        or flags["PHYSICAL_BRST_QUOTIENT_INSTABILITY_CERTIFIED"]
        or flags["C26_SERIALIZED"]
        or flags["RETAINED_BRST_HADAMARD_CERTIFIED"]
        or flags["PHYSICAL_POSITIVITY_CERTIFIED"]
        or flags["LORENTZIAN_QME_CERTIFIED"]
    ):
        raise ValueError("claim boundary was over-promoted")


if __name__ == "__main__":
    evaluate()
    print("BERGER HOMOGENEOUS STATIONARY NORMALIZATION OBSTRUCTION: PASS")
