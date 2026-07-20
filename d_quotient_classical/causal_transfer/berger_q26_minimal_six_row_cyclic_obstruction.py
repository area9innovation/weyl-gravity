#!/usr/bin/env python3
"""Exact cyclic-rank obstruction to the minimal six-row Berger extension.

The prior frozen-carrier theorem forces at least five new degree-zero rows and
one new degree-one row.  This consumer asks whether the rank-minimal six-row
profile can also carry the required nondegenerate BV odd pairing of
cohomological degree one.  The answer is no, independently of all PBW
coefficients and differential-order bounds.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "d_quotient_classical/causal_transfer"
RESULT_ID = "BERGER_Q26_MINIMAL_SIX_ROW_CYCLIC_OBSTRUCTION_V1"
OUTPUT = ROOT / f"d_quotient_classical/certificates/{RESULT_ID}.json"
PAYLOAD = ROOT / "d_quotient_classical/generated/berger_q26_minimal_six_row_cyclic_obstruction_v1/degree_and_sparse_control.json"
REPORT = ROOT / "d_quotient_classical/reports/berger-q26-minimal-six-row-cyclic-obstruction-v1.md"
SCHEMA = ROOT / "d_quotient_classical/schema/berger-q26-minimal-six-row-cyclic-obstruction-v1.schema.json"
VERIFIER = HERE / "verify_berger_q26_minimal_six_row_cyclic_obstruction.py"
TESTS = HERE / "tests/test_berger_q26_minimal_six_row_cyclic_obstruction.py"

PINNED_COMMIT = "988f8ee6c59b539ae516eb8a8f882a57a95f71e0"
PINNED_CERTIFICATE_PATH = (
    "physics/symplectic-reconstruction/d_quotient_classical/certificates/"
    "BERGER_Q26_CAUCHY_BV_CARRIER_OBSTRUCTION_V1.json"
)
PINNED_CERTIFICATE_SHA256 = (
    "24d2db35fb3dc696081d1e93208fdbd0b8f31922cdac7a063033650a9e686a01"
)

DEPENDENCIES = {
    "working_obstruction": ROOT / "d_quotient_classical/certificates/BERGER_Q26_CAUCHY_BV_CARRIER_OBSTRUCTION_V1.json",
    "working_obstruction_receipt": ROOT / "d_quotient_classical/receipts/BERGER_Q26_CAUCHY_BV_CARRIER_OBSTRUCTION_V1_TIER_RECEIPT.json",
    "rejected_q_Cauchy_104": ROOT / "quantum-weyl/lorentzian/generated/berger_canonical_graph_q_cauchy_obstruction/rejected_candidate_q_Cauchy_104.json",
    "full_A104_operator": ROOT / "quantum-weyl/lorentzian/generated/berger_a104_endpoint_completion/global_A104.json",
}

BASE_DEGREES = [-1, 0, 1, 2]
BASE_RANKS = [12, 40, 40, 12]


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


def _git_blob(commit: str, path: str) -> bytes:
    result = subprocess.run(
        ["git", "show", f"{commit}:{path}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    return result.stdout


def _artifact(path: Path, value: dict[str, Any]) -> dict[str, str]:
    return {
        "artifact_id": str(
            value.get("result_id", value.get("schema", path.name))
        ),
        "path": str(path.relative_to(ROOT)),
        "sha256": _sha(path),
    }


def _operator_record(path: Path, expected_shape: list[int]) -> dict[str, Any]:
    value = _load(path)
    body = {key: item for key, item in value.items() if key != "sha256"}
    if value.get("sha256") != _digest(body):
        raise AssertionError(f"internal sparse hash drifted: {path}")
    if value.get("shape") != expected_shape:
        raise AssertionError(f"sparse shape drifted: {path}")
    return value


def exact_rank_audit() -> dict[str, Any]:
    """Enumerate the complete six-row profile and the next cyclic lower bound."""
    obstruction = _load(DEPENDENCIES["working_obstruction"])
    lower = obstruction["extension_lower_bound"]
    if (
        lower["degree_0_added_rows_at_least"],
        lower["degree_plus1_added_rows_at_least"],
        lower["total_added_rows_at_least"],
        lower["status"],
    ) != (5, 1, 6, "NECESSARY_NOT_SUFFICIENT"):
        raise AssertionError("imported degreewise factorization bound drifted")

    six_row_profiles = []
    for n_minus1 in range(7):
        for n_zero in range(7 - n_minus1):
            for n_plus1 in range(7 - n_minus1 - n_zero):
                n_plus2 = 6 - n_minus1 - n_zero - n_plus1
                if n_zero >= 5 and n_plus1 >= 1:
                    six_row_profiles.append(
                        [n_minus1, n_zero, n_plus1, n_plus2]
                    )
    if six_row_profiles != [[0, 5, 1, 0]]:
        raise AssertionError("complete six-row grading enumeration drifted")

    additions = six_row_profiles[0]
    extended = [
        BASE_RANKS[index] + additions[index] for index in range(4)
    ]
    paired = [
        {
            "degree": -1,
            "dual_degree": 2,
            "rank": extended[0],
            "dual_rank": extended[3],
            "minimum_radical_dimension": abs(extended[0] - extended[3]),
        },
        {
            "degree": 0,
            "dual_degree": 1,
            "rank": extended[1],
            "dual_rank": extended[2],
            "minimum_radical_dimension": abs(extended[1] - extended[2]),
        },
    ]
    if extended != [12, 45, 41, 12] or paired[1][
        "minimum_radical_dimension"
    ] != 4:
        raise AssertionError("six-row odd-pairing deficit drifted")

    # A degree-one nondegenerate pairing requires n_0=n_1 and
    # n_-1=n_2.  Together with n_0>=5 this gives total additions >=10.
    minimum_cyclic_additions = [0, 5, 5, 0]
    if sum(minimum_cyclic_additions) != 10:
        raise AssertionError("next cyclic row bound drifted")
    return {
        "degrees": BASE_DEGREES,
        "base_ranks": BASE_RANKS,
        "factorization_lower_bounds": {
            "degree_0": 5,
            "degree_1": 1,
        },
        "complete_six_row_profiles": six_row_profiles,
        "unique_six_row_additions": additions,
        "six_row_extended_ranks": extended,
        "odd_pairing_degree": 1,
        "dual_degree_rule": "d_dual=1-d",
        "dual_pair_audit": paired,
        "minimum_pairing_radical_dimension": 4,
        "minimum_total_additions_after_cyclic_rank_completion": 10,
        "unique_rank_minimal_cyclic_additions": minimum_cyclic_additions,
        "additional_rows_beyond_six_required_at_least": 4,
    }


def build_payload() -> dict[str, Any]:
    audit = exact_rank_audit()
    q_record = _operator_record(
        DEPENDENCIES["rejected_q_Cauchy_104"], [104, 104]
    )
    a_record = _operator_record(
        DEPENDENCIES["full_A104_operator"], [104, 104]
    )
    return {
        "schema": "pure-weyl-berger-q26-six-row-degree-sparse-control-v1",
        "result_id": "BERGER_Q26_SIX_ROW_DEGREE_SPARSE_CONTROL_V1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "row_ordering": {
            "old_rows": {"start": 0, "stop_exclusive": 104},
            "new_rows": [
                {
                    "row": 104 + index,
                    "id": f"factorization_constraint_{index + 1}",
                    "degree": 0,
                    "forced_role": "intermediate carrier for inherited degree -1 to +1 square defect",
                }
                for index in range(5)
            ]
            + [
                {
                    "row": 109,
                    "id": "factorization_identity_1",
                    "degree": 1,
                    "forced_role": "intermediate carrier for inherited degree 0 to +2 square defect",
                }
            ],
        },
        "decoupled_sparse_control": {
            "shape": [110, 110],
            "q_old_old": {
                "path": str(
                    DEPENDENCIES["rejected_q_Cauchy_104"].relative_to(ROOT)
                ),
                "sha256": _sha(DEPENDENCIES["rejected_q_Cauchy_104"]),
                "internal_sha256": q_record["sha256"],
                "nonzero_sparse_entries": len(q_record["entries"]),
            },
            "A_old_old": {
                "path": str(
                    DEPENDENCIES["full_A104_operator"].relative_to(ROOT)
                ),
                "sha256": _sha(DEPENDENCIES["full_A104_operator"]),
                "internal_sha256": a_record["sha256"],
                "nonzero_sparse_entries": len(a_record["entries"]),
            },
            "old_new_blocks": "ZERO",
            "new_old_blocks": "ZERO",
            "new_new_blocks": "ZERO",
            "q_square_nonzero_sparse_entries": 157,
            "A_q_commutator_nonzero_sparse_entries": 207,
            "status": "MUTATION_CONTROL_NOT_A_SOLUTION",
        },
        "rank_audit": audit,
    }


def build() -> dict[str, Any]:
    pinned_blob = _git_blob(PINNED_COMMIT, PINNED_CERTIFICATE_PATH)
    if hashlib.sha256(pinned_blob).hexdigest() != PINNED_CERTIFICATE_SHA256:
        raise AssertionError("pinned 988f8ee6c obstruction hash drifted")
    pinned = json.loads(pinned_blob)
    working = _load(DEPENDENCIES["working_obstruction"])
    if (
        pinned["result_id"] != working["result_id"]
        or pinned["exact_replay"] != working["exact_replay"]
        or pinned["extension_lower_bound"] != working["extension_lower_bound"]
        or pinned["claim_flags"] != working["claim_flags"]
    ):
        raise AssertionError("close-out repair changed scientific input")
    replay = working["exact_replay"]
    if (
        replay["q_Cauchy_square_nonzero_sparse_entries"],
        replay["A104_q_Cauchy_commutator_nonzero_sparse_entries"],
    ) != (157, 207):
        raise AssertionError("157/207 decoupled controls drifted")

    dependencies = {
        name: _load(path) for name, path in DEPENDENCIES.items()
    }
    payload = build_payload()
    payload_text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    audit = payload["rank_audit"]
    sources = {
        str(path.relative_to(ROOT)): _sha(path)
        for path in (Path(__file__).resolve(), VERIFIER, TESTS, SCHEMA)
    }
    return {
        "schema": "pure-weyl-berger-q26-minimal-six-row-cyclic-obstruction-v1",
        "result_id": RESULT_ID,
        "result_state": "EXACT_SIX_ROW_EXTENSION_HAS_UNAVOIDABLE_FOUR_DIMENSIONAL_PAIRING_RADICAL",
        "lifecycle_status": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "scope": {
            "theory": "retained minimal pure-Weyl Berger BV complex",
            "background": "fixed rational positive Berger clock",
            "boundaries": "R_t x compact Berger S3; no spatial boundary",
            "charge_sector": "unquotiented retained-26 formal companion/Cauchy carrier",
            "carrier": "frozen 104 rows plus exactly six support-local rows",
            "degree": "-1,0,1,2",
            "parity": "BV parity fixed by cohomological degree",
            "ell": "not harmonic-reduced",
            "m": "not harmonic-reduced",
            "k": "all finite-order Berger PBW derivatives",
            "omega": "stationary formal A_ext evolution; no frequency split",
        },
        "pinned_input": {
            "commit": PINNED_COMMIT,
            "path": PINNED_CERTIFICATE_PATH,
            "sha256": PINNED_CERTIFICATE_SHA256,
            "working_repair_sha256": _sha(
                DEPENDENCIES["working_obstruction"]
            ),
            "scientific_fields_identical": True,
        },
        "dependencies": {
            name: _artifact(path, dependencies[name])
            for name, path in DEPENDENCIES.items()
        },
        "complete_declared_six_row_class": {
            "row_count": 110,
            "new_row_count": 6,
            "grading_profiles": "all nonnegative integer profiles of total six satisfying the certified degreewise factorization bounds",
            "coefficient_class": "all finite-order support-local Berger-equivariant PBW differential blocks over QQ[alpha_B,u,v]",
            "q_blocks": "all degree-plus-one old/new incidence blocks",
            "evolution_blocks": "all degree-preserving old/new A_ext blocks",
            "gauge_constraint_meanings": "all assignments of the five degree-zero rows as support-local constraint/equation carriers and the degree-one row as their identity/antifield carrier; the rank contradiction precedes and is invariant under these semantic assignments",
            "companion_changes": "all support-local degree-preserving changes compatible with the retained q26 solution map and fixed old-row identification",
            "pairing_blocks": "all bilinear degree-one odd-pairing blocks, including old/new mixing",
            "real_involution": "all degree-preserving real involutions compatible with the old-row real form",
            "graded_adjointness": "all adjoint identities induced by a nondegenerate degree-one odd pairing",
            "admissible_redefinitions": "all invertible degree-preserving support-local row and field redefinitions",
            "excluded": [
                "quotients or projections that hide old defects",
                "degree-changing regradings",
                "nonlocal inverses",
                "infinite-order operators",
            ],
            "completeness_reason": "the obstruction depends only on degree ranks, which are invariant under every admitted coefficient choice, PBW order, companion change, real involution and invertible degree-preserving redefinition",
        },
        "rank_audit": audit,
        "obstruction": {
            "necessary_factorization_profile": [0, 5, 1, 0],
            "extended_degree_ranks": [12, 45, 41, 12],
            "pairing_requirement": "rank(C^d)=rank(C^(1-d)) for a nondegenerate degree-one pairing",
            "failed_pair": [0, 1],
            "rank_deficit": 4,
            "conclusion": "every degree-one bilinear pairing on the exact six-row carrier has radical dimension at least four",
            "simultaneous_system_status": "INCONSISTENT_BEFORE_PBW_COEFFICIENT_SOLVE",
        },
        "next_lower_bound": {
            "total_added_rows_at_least": 10,
            "degree_minus1": 0,
            "degree_0": 5,
            "degree_plus1": 5,
            "degree_plus2": 0,
            "additional_cyclic_dual_rows_beyond_six_at_least": 4,
            "status": "NECESSARY_NOT_SUFFICIENT",
            "sufficiency_warning": "no ten-row q-square, evolution, solution-map, cyclicity, real or graded-adjoint solve is supplied",
        },
        "decoupled_control": payload["decoupled_sparse_control"],
        "exact_payload": {
            "artifact_id": payload["result_id"],
            "path": str(PAYLOAD.relative_to(ROOT)),
            "sha256": hashlib.sha256(payload_text.encode()).hexdigest(),
        },
        "classification": {
            "complete_six_row_grading_enumerated": True,
            "frozen_157_207_decoupled_control_preserved": True,
            "nondegenerate_degree_one_pairing_on_six_row_extension": False,
            "six_row_cyclic_BV_extension_exists": False,
            "minimum_total_row_addition_lower_bound": 10,
            "ten_row_extension_sufficient": False,
            "noncyclic_or_presymplectic_six_row_extension_obstructed": False,
            "larger_cyclic_extension_obstructed": False,
            "Hadamard_or_quantum_claim": False,
        },
        "next_gate": "CLASSIFY_AND_SOLVE_THE_RANK_MINIMAL_TEN_ROW_PROFILE_5_DEGREE_ZERO_PLUS_5_DEGREE_ONE",
        "claim_boundary": (
            "This exact LOCAL-ALGEBRAIC obstruction applies to the complete "
            "class of exactly six added finite-order support-local rows with "
            "the frozen grading and a required nondegenerate BV odd pairing "
            "of degree one. It proves that the unique factorization-minimal "
            "profile leaves a four-dimensional pairing radical and raises the "
            "necessary row lower bound from six to ten. It does not obstruct "
            "noncyclic or presymplectic six-row operators, prove that ten rows "
            "suffice, obstruct larger carriers or changed gradings, or provide "
            "a Cauchy/Krein form, real Hadamard state, positivity, QME, particle, "
            "scattering or unitarity theorem."
        ),
        "provenance": {
            "source_manifest": sources,
            "verification_commands": [
                "PYTHONPATH=. python3 -m d_quotient_classical.causal_transfer.berger_q26_minimal_six_row_cyclic_obstruction --check --guards",
                "PYTHONPATH=. python3 -m d_quotient_classical.causal_transfer.verify_berger_q26_minimal_six_row_cyclic_obstruction",
                "python3 -m unittest d_quotient_classical.causal_transfer.tests.test_berger_q26_minimal_six_row_cyclic_obstruction",
                "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/berger-q26-minimal-six-row-cyclic-obstruction-v1.schema.json -d d_quotient_classical/certificates/BERGER_Q26_MINIMAL_SIX_ROW_CYCLIC_OBSTRUCTION_V1.json",
            ],
        },
    }


def validate(value: dict[str, Any]) -> None:
    schema = _load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)


def _render(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def _report() -> str:
    return r"""# Minimal six-row Berger Cauchy BV extension: cyclic obstruction

The previous frozen-carrier theorem proves that nilpotence repair requires at
least five new degree-zero rows and one new degree-\(+1\) row.  With exactly
six added rows, this is the unique grading profile:

\[
(n_{-1},n_0,n_1,n_2)=(0,5,1,0).
\]

The frozen 104-row carrier has degree ranks

\[
(12,40,40,12)_{-1,0,1,2},
\]

so the rank-minimal extension has

\[
(12,45,41,12).
\]

A nondegenerate BV odd pairing of degree one pairs degree \(d\) with degree
\(1-d\).  Consequently degree zero and degree one must have equal rank.
Here \(45\ne41\): every such pairing has a radical of dimension at least four.

This no-go is independent of every PBW coefficient, finite differential-order
bound, degree-preserving companion change, real involution, adjoint convention
and invertible support-local row redefinition.  The simultaneous six-row
system is inconsistent before coefficient solving.

The next necessary cyclic rank profile adds

\[
(0,5,5,0),
\]

so at least ten rows are required—four more degree-\(+1\) cyclic partners than
the factorization-only lower bound supplied.  Ten rows are not claimed to be
sufficient.

The exact decoupled mutation control preserves the frozen 1018-entry
\(q_C\), 470-entry \(A_{104}\), 157 square defects and 207 evolution
commutator defects.  No quotient or projection hides them.

This theorem does not obstruct a noncyclic or presymplectic six-row operator,
construct the ten-row extension, or supply a Krein form, Hadamard state,
positivity, QME or quantum theory.

CLOSE-OUT: OBSTRUCTED — every exactly six-row extension in the complete declared cyclic class has a pairing radical of dimension at least four.
EVIDENCE: d_quotient_classical/certificates/BERGER_Q26_MINIMAL_SIX_ROW_CYCLIC_OBSTRUCTION_V1.json
"""


def _guards(value: dict[str, Any]) -> None:
    mutations = [
        ("rank_audit", "minimum_pairing_radical_dimension", 0),
        ("next_lower_bound", "total_added_rows_at_least", 9),
        ("classification", "ten_row_extension_sufficient", True),
        ("classification", "Hadamard_or_quantum_claim", True),
    ]
    for section, field, replacement in mutations:
        mutant = deepcopy(value)
        mutant[section][field] = replacement
        try:
            validate(mutant)
        except Exception:
            continue
        raise AssertionError(f"mutation survived: {section}.{field}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    payload = build_payload()
    value = build()
    validate(value)
    if args.write:
        PAYLOAD.parent.mkdir(parents=True, exist_ok=True)
        PAYLOAD.write_text(_render(payload))
        OUTPUT.write_text(_render(value))
        REPORT.write_text(_report())
    if args.check:
        if PAYLOAD.read_text() != _render(payload):
            raise AssertionError("six-row sparse control payload drifted")
        if OUTPUT.read_text() != _render(value):
            raise AssertionError("six-row obstruction certificate drifted")
        if REPORT.read_text() != _report():
            raise AssertionError("six-row obstruction report drifted")
    if args.guards:
        _guards(value)
    print(f"{RESULT_ID}: PASS")


if __name__ == "__main__":
    main()
