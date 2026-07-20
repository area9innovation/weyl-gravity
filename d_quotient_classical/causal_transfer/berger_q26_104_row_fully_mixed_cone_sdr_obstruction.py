#!/usr/bin/env python3
"""Close the fully mixed evolution branch of the 104-row Berger cone.

The earlier upper-triangular cone evolution is obstructed, but the same
nilpotent doubled differential admits the fully mixed evolution

    Q = N tensor q,       A_mix = N tensor A,
    N = [[1,-1],[1,-1]], N^2 = 0.

Thus both Q^2 and [A_mix,Q] vanish without assuming any relation between q
and A.  This is not yet the requested carrier: an SDR onto retained q26 is
impossible.  A rational multiplicative specialization gives different
degreewise cohomology dimensions for the cone and retained complexes.
"""

from __future__ import annotations

import argparse
from functools import lru_cache
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp

from d_quotient_classical.causal_transfer import (
    berger_q26_104_row_canonical_cone_lift_obstruction as cone,
)


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "d_quotient_classical/causal_transfer"
RESULT_ID = "BERGER_Q26_104_ROW_FULLY_MIXED_CONE_SDR_OBSTRUCTION_V1"
OUTPUT = ROOT / f"d_quotient_classical/certificates/{RESULT_ID}.json"
PAYLOAD = (
    ROOT
    / "d_quotient_classical/generated/"
    "berger_q26_104_row_fully_mixed_cone_sdr_obstruction_v1/"
    "rational_cohomology_witness.json"
)
REPORT = (
    ROOT
    / "d_quotient_classical/reports/"
    "berger-q26-104-row-fully-mixed-cone-sdr-obstruction-v1.md"
)
SCHEMA = (
    ROOT
    / "d_quotient_classical/schema/"
    "berger-q26-104-row-fully-mixed-cone-sdr-obstruction-v1.schema.json"
)
VERIFIER = (
    HERE
    / "verify_berger_q26_104_row_fully_mixed_cone_sdr_obstruction.py"
)
TESTS = (
    HERE
    / "tests/test_berger_q26_104_row_fully_mixed_cone_sdr_obstruction.py"
)
RETAINED = (
    ROOT
    / "d_quotient_classical/certificates/"
    "BERGER_RETAINED_MINIMAL_OPERATOR.json"
)
LAYOUT = (
    ROOT
    / "d_quotient_classical/certificates/"
    "BERGER_RETAINED_MINIMAL_LAYOUT.json"
)
CANONICAL_CONE = (
    ROOT
    / "d_quotient_classical/certificates/"
    "BERGER_Q26_104_ROW_CANONICAL_CONE_LIFT_OBSTRUCTION_V1.json"
)
NEXT_DEFECT = (
    ROOT
    / "d_quotient_classical/certificates/"
    "BERGER_Q26_104_ROW_CONE_NEXT_DEFECT_MODULE_V1.json"
)

DEGREES_104 = tuple(
    [-1] * 6 + [0] * 20 + [1] * 20 + [2] * 6
) * 2
DEGREES_26 = tuple([-1] * 3 + [0] * 10 + [1] * 10 + [2] * 3)
SPECIALIZATION = {"alpha_B": 2, "u": 1, "v": 3}
EXPECTED_Q104_RANKS = {-1: 11, 0: 12, 1: 11, 2: 0}
EXPECTED_CONE_H = {-1: 13, 0: 57, 1: 57, 2: 13}
EXPECTED_Q26_RANKS = {-1: 2, 0: 7, 1: 2, 2: 0}
EXPECTED_RETAINED_H = {-1: 1, 0: 1, 1: 1, 2: 1}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise TypeError(f"expected JSON object: {path}")
    return value


def _constant_record_matrix(record: dict[str, Any]) -> sp.Matrix:
    shape = record.get("shape")
    if (
        not isinstance(shape, list)
        or len(shape) != 2
        or any(type(value) is not int for value in shape)
    ):
        raise ValueError("matrix shape missing")
    result = sp.zeros(*shape)
    alpha_B, u, v = sp.symbols("alpha_B u v")
    substitutions = {
        alpha_B: sp.Rational(SPECIALIZATION["alpha_B"]),
        u: sp.Rational(SPECIALIZATION["u"]),
        v: sp.Rational(SPECIALIZATION["v"]),
    }
    for row, column, terms in record.get("entries", []):
        for exponents, coefficient_text in terms:
            if sum(exponents):
                continue
            result[row, column] += sp.sympify(
                coefficient_text,
                locals={"alpha_B": alpha_B, "u": u, "v": v},
            ).subs(substitutions)
    return result


def _degree_ranks(
    matrix: sp.Matrix, degrees: tuple[int, ...]
) -> dict[int, int]:
    ranks: dict[int, int] = {}
    for degree in (-1, 0, 1, 2):
        columns = [
            index for index, value in enumerate(degrees) if value == degree
        ]
        rows = [
            index
            for index, value in enumerate(degrees)
            if value == degree + 1
        ]
        ranks[degree] = (
            int(matrix.extract(rows, columns).rank()) if rows else 0
        )
    return ranks


def _homology_dimensions(
    dimensions: dict[int, int], ranks: dict[int, int]
) -> dict[int, int]:
    return {
        degree: dimensions[degree]
        - ranks[degree]
        - ranks.get(degree - 1, 0)
        for degree in (-1, 0, 1, 2)
    }


def _retained_matrix() -> sp.Matrix:
    retained = _load(RETAINED)
    blocks = retained.get("q1_blocks", {})
    names = (
        "K_spatial",
        "H_retained",
        "minus_K_spatial_sharp",
    )
    matrices = [_constant_record_matrix(blocks[name]) for name in names]
    q26 = sp.zeros(26)
    q26[3:13, 0:3] = matrices[0]
    q26[13:23, 3:13] = matrices[1]
    q26[23:26, 13:23] = matrices[2]
    return q26


@lru_cache(maxsize=1)
def exact_audit() -> dict[str, Any]:
    q104 = cone._load_constant_matrix(cone.Q_PATH)
    a104 = cone._load_constant_matrix(cone.A_PATH)
    q26 = _retained_matrix()
    flavor = sp.Matrix([[1, -1], [1, -1]])
    q_cone = sp.kronecker_product(flavor, q104)
    a_mixed = sp.kronecker_product(flavor, a104)
    q104_ranks = _degree_ranks(q104, DEGREES_104)
    q26_ranks = _degree_ranks(q26, DEGREES_26)
    cone_h = _homology_dimensions(
        {
            -1: 24,
            0: 80,
            1: 80,
            2: 24,
        },
        q104_ranks,
    )
    retained_h = _homology_dimensions(
        {-1: 3, 0: 10, 1: 10, 2: 3}, q26_ranks
    )
    checks = {
        "flavor_square_zero": flavor * flavor == sp.zeros(2),
        "q_cone_square_zero": q_cone * q_cone == sp.zeros(208),
        "fully_mixed_evolution_commutes": (
            a_mixed * q_cone - q_cone * a_mixed == sp.zeros(208)
        ),
        "q26_square_zero": q26 * q26 == sp.zeros(26),
        "q104_degree_ranks_match": q104_ranks == EXPECTED_Q104_RANKS,
        "q26_degree_ranks_match": q26_ranks == EXPECTED_Q26_RANKS,
        "cone_homology_matches": cone_h == EXPECTED_CONE_H,
        "retained_homology_matches": retained_h == EXPECTED_RETAINED_H,
        "homology_dimensions_differ": cone_h != retained_h,
    }
    if not all(checks.values()):
        raise AssertionError(f"mixed cone SDR audit drifted: {checks}")
    return {
        "schema": (
            "pure-weyl-berger-q26-104-row-fully-mixed-cone-"
            "rational-cohomology-witness-v1"
        ),
        "result_id": (
            "BERGER_Q26_104_ROW_FULLY_MIXED_CONE_"
            "RATIONAL_COHOMOLOGY_WITNESS_V1"
        ),
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "representation": {
            "coefficient_field": "QQ",
            "specialization": SPECIALIZATION,
            "derivative_generators": {
                "e0": 0,
                "e1": 0,
                "e2": 0,
                "e3": 0,
            },
            "multiplicative": True,
        },
        "flavor_matrix": [[1, -1], [1, -1]],
        "q104_degree_ranks": {
            str(key): value for key, value in q104_ranks.items()
        },
        "cone_degree_dimensions": {
            "-1": 24,
            "0": 80,
            "1": 80,
            "2": 24,
        },
        "cone_homology_dimensions": {
            str(key): value for key, value in cone_h.items()
        },
        "q26_degree_ranks": {
            str(key): value for key, value in q26_ranks.items()
        },
        "retained_degree_dimensions": {
            "-1": 3,
            "0": 10,
            "1": 10,
            "2": 3,
        },
        "retained_homology_dimensions": {
            str(key): value for key, value in retained_h.items()
        },
        "checks": checks,
    }


def _artifact(path: Path, artifact_id: str) -> dict[str, str]:
    return {
        "artifact_id": artifact_id,
        "path": str(path.relative_to(ROOT)),
        "sha256": _sha(path),
    }


def build() -> dict[str, Any]:
    prior = _load(CANONICAL_CONE)
    next_defect = _load(NEXT_DEFECT)
    if (
        prior.get("result_id")
        != "BERGER_Q26_104_ROW_CANONICAL_CONE_LIFT_OBSTRUCTION_V1"
        or next_defect.get("result_id")
        != "BERGER_Q26_104_ROW_CONE_NEXT_DEFECT_MODULE_V1"
    ):
        raise AssertionError("cone predecessor identity drifted")
    audit = exact_audit()
    payload_text = json.dumps(audit, indent=2, sort_keys=True) + "\n"
    sources = {
        str(path.relative_to(ROOT)): _sha(path)
        for path in (Path(__file__).resolve(), VERIFIER, TESTS, SCHEMA)
    }
    return {
        "schema": (
            "pure-weyl-berger-q26-104-row-fully-mixed-cone-"
            "sdr-obstruction-v1"
        ),
        "result_id": RESULT_ID,
        "result_state": (
            "FULLY_MIXED_CONE_EVOLUTION_EXISTS_BUT_RETAINED_SDR_IS_"
            "COHOMOLOGICALLY_OBSTRUCTED"
        ),
        "lifecycle_status": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "scope": {
            "theory": "retained minimal pure-Weyl Berger BV complex",
            "background": "fixed rational positive Berger clock",
            "boundaries": "R_t x compact Berger S3; no spatial boundary",
            "charge_sector": (
                "unquotiented retained-26 formal companion/Cauchy carrier"
            ),
            "carrier": (
                "canonical same-profile doubled cone with fully mixed "
                "evolution"
            ),
            "degree": "-1,0,1,2",
            "parity": (
                "inherited BV parity; pairing not reached because SDR fails"
            ),
            "ell": "not harmonic-reduced",
            "m": "not harmonic-reduced",
            "k": "all finite-order Berger PBW derivatives",
            "omega": "stationary A104 formal evolution; no spectral split",
        },
        "pinned_inputs": {
            "canonical_cone_obstruction": _artifact(
                CANONICAL_CONE,
                "BERGER_Q26_104_ROW_CANONICAL_CONE_LIFT_OBSTRUCTION_V1",
            ),
            "cone_next_defect": _artifact(
                NEXT_DEFECT,
                "BERGER_Q26_104_ROW_CONE_NEXT_DEFECT_MODULE_V1",
            ),
            "q_Cauchy": _artifact(
                cone.Q_PATH, "rejected_candidate_q_Cauchy_104"
            ),
            "A104": _artifact(cone.A_PATH, "global_A104"),
            "retained_q26": _artifact(
                RETAINED, "BERGER_RETAINED_MINIMAL_OPERATOR"
            ),
            "retained_layout": _artifact(
                LAYOUT, "BERGER_RETAINED_MINIMAL_LAYOUT"
            ),
        },
        "fully_mixed_cone": {
            "flavor_matrix": "N=[[1,-1],[1,-1]]",
            "flavor_identity": "N^2=0",
            "q_ext": "Q=N tensor q_Cauchy",
            "A_ext": "A_mix=N tensor A104",
            "old_old_q_block": "q_Cauchy",
            "old_old_A_block": "A104",
            "q_ext_squared_zero": True,
            "A_ext_q_ext_commutator_zero": True,
            "support_local": True,
            "degree_profile_added": {
                "degree_minus1": 12,
                "degree_0": 40,
                "degree_plus1": 40,
                "degree_plus2": 12,
            },
        },
        "sdr_obstruction": {
            "exact_payload": {
                "artifact_id": audit["result_id"],
                "path": str(PAYLOAD.relative_to(ROOT)),
                "sha256": hashlib.sha256(
                    payload_text.encode()
                ).hexdigest(),
            },
            "specialized_cone_homology_dimensions": [
                13,
                57,
                57,
                13,
            ],
            "specialized_retained_homology_dimensions": [1, 1, 1, 1],
            "proof": (
                "A PBW-linear SDR specializes under every multiplicative "
                "rational representation to an SDR of rational complexes. "
                "An SDR induces degreewise cohomology isomorphisms, but the "
                "displayed specialized dimensions differ."
            ),
            "status": "INCONSISTENT",
        },
        "classification": {
            "fully_mixed_cone_evolution_lift_exists": True,
            "fully_mixed_cone_nilpotent": True,
            "retained_q26_SDR_exists": False,
            "cyclic_pairing_and_real_structure_reached": False,
            "all_non_cone_104_row_completions_obstructed": False,
            "minimum_208_row_physical_carrier_constructed": False,
            "Hadamard_or_quantum_claim": False,
        },
        "next_gate": (
            "SOLVE_THE_GENERAL_NON_CONE_104_ROW_BLOCK_SYSTEM_WITH_"
            "RETAINED_COHOMOLOGY_FIXED_FROM_THE_OUTSET"
        ),
        "claim_boundary": (
            "This exact rational theorem closes the fully mixed evolution "
            "branch of the canonical same-profile doubled cone: a commuting "
            "evolution lift exists, but no support-local SDR to the retained "
            "26-row complex can exist because a multiplicative rational "
            "specialization has different degreewise cohomology. It does not "
            "obstruct general non-cone 104-row factorizations, raise the "
            "global row lower bound, construct a cyclic Cauchy/Krein pairing "
            "or real involution, or establish Hadamard, positivity, QME or "
            "quantum data."
        ),
        "provenance": {
            "source_manifest": sources,
            "verification_commands": [
                (
                    "PYTHONPATH=. python3 -m d_quotient_classical."
                    "causal_transfer."
                    "berger_q26_104_row_fully_mixed_cone_sdr_obstruction "
                    "--check --guards"
                ),
                (
                    "PYTHONPATH=. python3 -m d_quotient_classical."
                    "causal_transfer."
                    "verify_berger_q26_104_row_fully_mixed_cone_sdr_"
                    "obstruction"
                ),
                (
                    "PYTHONPATH=. python3 -m unittest "
                    "d_quotient_classical.causal_transfer.tests."
                    "test_berger_q26_104_row_fully_mixed_cone_sdr_"
                    "obstruction"
                ),
                (
                    "npx --yes ajv-cli@5 validate --spec=draft2020 "
                    "--strict=true -s d_quotient_classical/schema/"
                    "berger-q26-104-row-fully-mixed-cone-sdr-obstruction-"
                    "v1.schema.json -d d_quotient_classical/certificates/"
                    f"{RESULT_ID}.json"
                ),
            ],
        },
    }


def report_text() -> str:
    return r"""# Berger q26 fully mixed cone: retained-SDR obstruction

The upper-triangular evolution lift of the canonical doubled cone is
obstructed, but this does not mean that the cone has no commuting evolution.
With

\[
N=\begin{pmatrix}1&-1\\1&-1\end{pmatrix},\qquad N^2=0,
\]

the operators

\[
Q_{\rm cone}=N\otimes q_{\rm Cauchy},\qquad
A_{\rm mix}=N\otimes A_{104}
\]

obey \(Q_{\rm cone}^2=0\) and
\([A_{\rm mix},Q_{\rm cone}]=0\) identically.  They preserve the old-old
blocks and use exactly one same-profile 104-row copy.

This formal lift does not contract to the certified retained complex.  In the
rational multiplicative specialization
\(e_0=e_1=e_2=e_3=0\),
\((\alpha_B,u,v)=(2,1,3)\), the cone has degreewise cohomology dimensions

\[
(13,57,57,13),
\]

while the retained 26-row complex has

\[
(1,1,1,1).
\]

Any PBW-linear SDR would specialize to an SDR of rational complexes and hence
would induce equal degreewise cohomology.  The mismatch is therefore an exact
obstruction before cyclic pairing and real-structure equations are imposed.

This closes the fully mixed canonical-cone branch only.  General non-cone
104-row block factorizations remain open.
"""


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    payload = exact_audit()
    certificate = build()
    payload_text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    certificate_text = json.dumps(
        certificate, indent=2, sort_keys=True
    ) + "\n"
    if args.check:
        if PAYLOAD.read_text() != payload_text:
            raise AssertionError("payload drifted")
        if OUTPUT.read_text() != certificate_text:
            raise AssertionError("certificate drifted")
        if REPORT.read_text() != report_text():
            raise AssertionError("report drifted")
    else:
        _write(PAYLOAD, payload_text)
        _write(OUTPUT, certificate_text)
        _write(REPORT, report_text())
    Draft202012Validator(_load(SCHEMA)).validate(certificate)
    if args.guards:
        mutated = json.loads(certificate_text)
        mutated["classification"]["retained_q26_SDR_exists"] = True
        try:
            Draft202012Validator(_load(SCHEMA)).validate(mutated)
        except Exception:
            pass
        else:
            raise AssertionError("schema accepted false SDR promotion")
    print(
        f"{RESULT_ID}: PASS "
        f"cone_h={list(EXPECTED_CONE_H.values())} "
        f"retained_h={list(EXPECTED_RETAINED_H.values())}"
    )


if __name__ == "__main__":
    main()
