"""Readiness certificate for the repository Euclidean elliptic BV complex."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any, Callable

from jsonschema import Draft202012Validator

from .elliptic_complex_receiver import (
    RESULT_IDS,
    SCHEMA as INPUT_SCHEMA,
    synthetic_payload,
    validate_euclidean_elliptic_complex,
)


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = HERE / "certificates/REPOSITORY_EUCLIDEAN_ELLIPTIC_COMPLEX_READINESS.json"
SCHEMA = HERE / "schema/repository-euclidean-elliptic-complex-readiness-v1.schema.json"
DEPENDENCIES = {
    "physical_round_S4_ledger": HERE / "certificates/REPOSITORY_FULL_BV_MULTIPLICITY_LEDGER.json",
    "gauge_fixed_local_BV": ROOT / "quantum-weyl/local_bv/certificates/GENERAL_NONMINIMAL_GAUGE_FIXED_CONTRACTION.json",
    "Nariai_metric_Bach_complex": ROOT / "d_quotient_classical/certificates/NARIAI_METRIC_BACH_CYCLIC_BV_COMPLEX_V1.json",
    "standard_auxiliary_match": HERE / "certificates/STANDARD_SPIN2_AUXILIARY_FOURTH_ORDER_MATCH.json",
}
SOURCE_PATHS = (
    "quantum-weyl/spectral/euclidean/elliptic_complex_receiver.py",
    "quantum-weyl/spectral/euclidean/elliptic_complex_readiness.py",
    "quantum-weyl/spectral/euclidean/verify_elliptic_complex_readiness.py",
    "quantum-weyl/spectral/euclidean/schema/repository-euclidean-elliptic-complex-input-v1.schema.json",
    "quantum-weyl/spectral/euclidean/schema/repository-euclidean-elliptic-complex-readiness-v1.schema.json",
    "quantum-weyl/spectral/euclidean/tests/test_elliptic_complex_readiness.py",
    "quantum-weyl/reports/repository-euclidean-elliptic-complex-readiness.md",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _rehashed(payload: dict[str, Any]) -> None:
    payload["proof_sha256"] = _canonical_hash(
        {
            key: payload[key]
            for key in (
                "classical_commit",
                "analytic_route",
                "background",
                "formulation",
                "cotangent_orbit_reduction",
                "principal_symbol_exactness",
                "gauge_fixed_kinetic_blocks",
                "coverage",
                "proof_artifacts",
            )
        }
    )


def mutation_receipts(payload: dict[str, Any]) -> list[dict[str, Any]]:
    mutations: tuple[tuple[str, Callable[[dict[str, Any]], None], bool], ...] = (
        (
            "nonzero_symbol_composition",
            lambda row: row["principal_symbol_exactness"][0]["outgoing_symbol"][
                "entries"
            ][0].update(column=0),
            True,
        ),
        (
            "rank_ledger",
            lambda row: row["principal_symbol_exactness"][0].update(incoming_rank=0),
            True,
        ),
        (
            "zero_principal_scalar",
            lambda row: row["gauge_fixed_kinetic_blocks"][0][
                "principal_scalar"
            ].update(numerator=0),
            True,
        ),
        (
            "out_of_bounds_sparse_coordinate",
            lambda row: row["principal_symbol_exactness"][0]["incoming_symbol"][
                "entries"
            ][0].update(row=2),
            True,
        ),
        ("proof_digest", lambda row: row.update(proof_sha256="0" * 64), False),
    )
    receipts = []
    for name, mutate, rehash in mutations:
        mutant = deepcopy(payload)
        mutate(mutant)
        if rehash:
            _rehashed(mutant)
        try:
            validate_euclidean_elliptic_complex(
                mutant, repository_root=ROOT, allow_synthetic_fixture=True
            )
        except Exception:
            rejected = True
        else:
            rejected = False
        receipts.append({"mutation": name, "rejected": rejected})
    return receipts


def _candidate_audit(values: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    ledger = values["physical_round_S4_ledger"]
    local = values["gauge_fixed_local_BV"]
    nariai = values["Nariai_metric_Bach_complex"]
    auxiliary = values["standard_auxiliary_match"]
    if (
        ledger.get("result_state") != "REPOSITORY_FULL_BV_MULTIPLICITY_LEDGER_ACCEPTED"
        or local.get("result_state")
        != "FULL_LOCAL_BV_G2_COMPLETE_ON_REGULAR_BACH_LOCUS_ANALYTIC_QME_OPEN"
        or nariai.get("result_state")
        != "ACTION_PAIRED_FOUR_ROW_METRIC_BACH_COMPLEX_EXACT"
        or auxiliary.get("result_state")
        != "STANDARD_PHYSICAL_TT_SCHUR_AND_LOCAL_JACOBIAN_IDENTITY_VERIFIED_REPOSITORY_MATCH_OPEN"
    ):
        raise ValueError("elliptic-complex candidate dependency drifted")
    return [
        {
            "candidate_id": ledger["result_id"],
            "Euclidean": True,
            "full_BV_rows": True,
            "principal_symbol_exactness": False,
            "gauge_fixed_ellipticity": False,
            "disposition": "REDUCED_DETERMINANT_LEDGER_NOT_FULL_SYMBOL_COMPLEX",
            "proof_sha256": _sha256(DEPENDENCIES["physical_round_S4_ledger"]),
        },
        {
            "candidate_id": local["result_id"],
            "Euclidean": False,
            "full_BV_rows": True,
            "principal_symbol_exactness": False,
            "gauge_fixed_ellipticity": False,
            "disposition": "LOCAL_BV_CONTRACTION_WITHOUT_ANALYTIC_SYMBOL_CERTIFICATE",
            "proof_sha256": _sha256(DEPENDENCIES["gauge_fixed_local_BV"]),
        },
        {
            "candidate_id": nariai["result_id"],
            "Euclidean": False,
            "full_BV_rows": False,
            "principal_symbol_exactness": False,
            "gauge_fixed_ellipticity": False,
            "disposition": "LORENTZIAN_CLASSICAL_COMPLEX_NOT_EUCLIDEAN_ELLIPTIC",
            "proof_sha256": _sha256(DEPENDENCIES["Nariai_metric_Bach_complex"]),
        },
        {
            "candidate_id": auxiliary["result_id"],
            "Euclidean": True,
            "full_BV_rows": False,
            "principal_symbol_exactness": False,
            "gauge_fixed_ellipticity": False,
            "disposition": "STANDARD_TT_BLOCK_IDENTITY_NOT_REPOSITORY_FULL_COMPLEX",
            "proof_sha256": _sha256(DEPENDENCIES["standard_auxiliary_match"]),
        },
    ]


def build() -> dict[str, Any]:
    fixture = synthetic_payload(repository_root=ROOT)
    receipt = validate_euclidean_elliptic_complex(
        fixture, repository_root=ROOT, allow_synthetic_fixture=True
    )
    mutations = mutation_receipts(fixture)
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    candidates = _candidate_audit(values)
    if receipt["status"] != "SEMANTIC_RECEIVER_ACCEPTED" or not all(
        row["rejected"] for row in mutations
    ):
        raise AssertionError("elliptic-complex receiver mechanics failed")
    contract = {
        "required_result_id": "REPOSITORY_EUCLIDEAN_ELLIPTIC_COMPLEX",
        "input_schema_path": str(INPUT_SCHEMA.relative_to(ROOT)),
        "required_analytic_route": "EUCLIDEAN_ELLIPTIC",
        "required_symbol_orbit_group": "SO(4)",
        "required_proof_result_ids": RESULT_IDS,
        "physical_input_status": "NOT_SUPPLIED",
    }
    proof_payload = {
        "dependency_hashes": {name: _sha256(path) for name, path in DEPENDENCIES.items()},
        "contract": contract,
        "receipt": receipt,
        "mutations": mutations,
        "candidates": candidates,
    }
    return {
        "schema": "quantum-weyl-repository-euclidean-elliptic-complex-readiness-v1",
        "result_id": "REPOSITORY_EUCLIDEAN_ELLIPTIC_COMPLEX_READINESS",
        "result_state": "SYMBOL_EXACTNESS_RECEIVER_READY_PHYSICAL_COMPLEX_NOT_SUPPLIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "dependency_hashes": proof_payload["dependency_hashes"],
        "accepted_contract": contract,
        "receiver_mechanics": {
            "scope": "SYNTHETIC_EXACT_SPARSE_SYMBOL_SEQUENCE_ONLY",
            "synthetic_receipt": receipt,
            "mutation_receipts": mutations,
        },
        "current_candidate_audit": candidates,
        "minimal_missing_carrier_theorem": {
            "status": "FULL_COVARIANT_SYMBOL_SEQUENCE_ABSENT",
            "reduced_round_S4_ledger_is_not_enough": True,
            "local_BV_contraction_is_not_analytic_ellipticity": True,
            "Lorentzian_Green_hyperbolicity_is_not_Euclidean_ellipticity": True,
            "required_artifact": "REPOSITORY_EUCLIDEAN_ELLIPTIC_COMPLEX",
        },
        "claim_flags": {
            "EUCLIDEAN_ELLIPTIC_COMPLEX_RECEIVER_READY": True,
            "EXACT_SPARSE_SYMBOL_REPLAY_READY": True,
            "CURRENT_CANDIDATES_AUDITED": True,
            "REPOSITORY_EUCLIDEAN_ELLIPTIC_COMPLEX_CERTIFIED": False,
            "REGULATED_SLAVNOV_BREAKING_COMPUTED": False,
            "QME_DISPOSITION": False,
        },
        "proof_sha256": _canonical_hash(proof_payload),
        "next_gate": "REPOSITORY_EUCLIDEAN_ELLIPTIC_COMPLEX",
        "claim_boundary": (
            "This LOCAL-ALGEBRAIC plus EUCLIDEAN-SPECTRAL readiness certificate "
            "defines an exact sparse principal-symbol receiver for the complete "
            "gauge-fixed repository BV complex. It recomputes symbol compositions, "
            "ranks, kernel-image equality, nonzero kinetic principal scalars, full-row "
            "coverage, proof roles, multiplicity, and snapshot compatibility. The "
            "physical round-S4 determinant ledger is reduced and does not provide the "
            "full covariant symbol sequence; the local BV contraction is not an analytic "
            "ellipticity theorem; Nariai is Lorentzian; and the standard auxiliary TT "
            "identity is not a repository full complex. The synthetic sequence tests "
            "receiver mechanics only. No physical elliptic complex, coefficient vector, "
            "Slavnov breaking, QME disposition, or Lorentzian quantum theory is claimed."
        ),
        "provenance": {
            "source_sha256": {path: _sha256(ROOT / path) for path in SOURCE_PATHS}
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    schema = json.loads(SCHEMA.read_text())
    input_schema = json.loads(INPUT_SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator.check_schema(input_schema)
    Draft202012Validator(schema).validate(value)
    rendered = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if args.emit:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(rendered)
    if args.check and (not OUTPUT.exists() or OUTPUT.read_text() != rendered):
        raise SystemExit(f"stale elliptic-complex readiness: {OUTPUT}")
    print("repository Euclidean elliptic-complex readiness: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
