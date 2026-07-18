"""Readiness and current-candidate audit for the repository C2 coefficient gate."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any, Callable

from jsonschema import Draft202012Validator

from .nonconformal_coefficient_match_receiver import (
    RESULT_IDS,
    SCHEMA as INPUT_SCHEMA,
    synthetic_payload,
    validate_nonconformal_coefficient_match,
)


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = HERE / "certificates/REPOSITORY_NONCONFORMAL_COEFFICIENT_MATCH_READINESS.json"
SCHEMA = HERE / "schema/repository-nonconformal-coefficient-match-readiness-v1.schema.json"
DEPENDENCIES = {
    "Nariai_metric_Bach_complex": ROOT / "d_quotient_classical/certificates/NARIAI_METRIC_BACH_CYCLIC_BV_COMPLEX_V1.json",
    "positive_Berger_clock": ROOT / "d_quotient_classical/certificates/POSITIVE_BERGER_CLOCK_BACKGROUND.json",
    "standard_coefficient_vector": ROOT / "quantum-weyl/spectral/euclidean/certificates/WEYL_GRAVITON_ANOMALY_COEFFICIENTS_D_DESCENT.json",
    "repository_round_S4_Euler": ROOT / "quantum-weyl/spectral/euclidean/certificates/REPOSITORY_ROUND_S4_EULER_COEFFICIENT.json",
}
SOURCE_PATHS = (
    "quantum-weyl/spectral/euclidean/nonconformal_coefficient_match_receiver.py",
    "quantum-weyl/spectral/euclidean/nonconformal_coefficient_match_readiness.py",
    "quantum-weyl/spectral/euclidean/verify_nonconformal_coefficient_match_readiness.py",
    "quantum-weyl/spectral/euclidean/schema/repository-nonconformal-coefficient-match-input-v1.schema.json",
    "quantum-weyl/spectral/euclidean/schema/repository-nonconformal-coefficient-match-readiness-v1.schema.json",
    "quantum-weyl/spectral/euclidean/tests/test_nonconformal_coefficient_match_readiness.py",
    "quantum-weyl/reports/repository-nonconformal-coefficient-match-readiness.md",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _rehashed(payload: dict[str, Any]) -> dict[str, Any]:
    payload["proof_sha256"] = _canonical_hash(
        {
            key: payload[key]
            for key in (
                "classical_commit",
                "analytic_route",
                "background",
                "operator_and_measure",
                "coefficient_result",
                "consistency",
                "classical_snapshot_compatibility_artifact",
            )
        }
    )
    return payload


def mutation_receipts(payload: dict[str, Any]) -> list[dict[str, Any]]:
    mutations: tuple[tuple[str, Callable[[dict[str, Any]], None], bool], ...] = (
        (
            "factor_sum",
            lambda row: row["coefficient_result"]["coefficients"]["C2"].update(
                numerator=4
            ),
            True,
        ),
        (
            "C2_visibility",
            lambda row: row["background"].update(C2_visibility="INVISIBLE"),
            False,
        ),
        (
            "spurious_auxiliary_proof",
            lambda row: row["operator_and_measure"].update(
                auxiliary_fourth_order_match_artifact=row["operator_and_measure"][
                    "local_measure_artifact"
                ]
            ),
            True,
        ),
        (
            "proof_digest",
            lambda row: row.update(proof_sha256="0" * 64),
            False,
        ),
    )
    receipts = []
    for name, mutate, rehash in mutations:
        mutant = deepcopy(payload)
        mutate(mutant)
        if rehash:
            _rehashed(mutant)
        try:
            validate_nonconformal_coefficient_match(
                mutant, repository_root=ROOT, allow_synthetic_fixture=True
            )
        except Exception:
            rejected = True
        else:
            rejected = False
        receipts.append({"mutation": name, "rejected": rejected})
    return receipts


def _candidate_audit(values: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    nariai = values["Nariai_metric_Bach_complex"]
    berger = values["positive_Berger_clock"]
    standard = values["standard_coefficient_vector"]
    sphere = values["repository_round_S4_Euler"]
    if (
        nariai.get("result_id") != "NARIAI_METRIC_BACH_CYCLIC_BV_COMPLEX_V1"
        or nariai.get("result_state")
        != "ACTION_PAIRED_FOUR_ROW_METRIC_BACH_COMPLEX_EXACT"
        or berger.get("result_id") != "POSITIVE_BERGER_CLOCK_BACKGROUND"
        or standard.get("result_state")
        != "STANDARD_SPIN2_BACKGROUND_COEFFICIENTS_COMPUTED_D_PULLBACK_CERTIFIED"
        or sphere.get("result_state")
        != "REPOSITORY_EUCLIDEAN_S4_EULER_COEFFICIENT_MATCHED_C_COEFFICIENT_OPEN"
    ):
        raise ValueError("nonconformal coefficient candidate dependency drifted")
    return [
        {
            "candidate_id": nariai["result_id"],
            "C2_visible": True,
            "repository_operator": True,
            "Euclidean_elliptic_full_BV": False,
            "measure_and_regulator": False,
            "coefficient_vector": False,
            "disposition": "INELIGIBLE_LORENTZIAN_CLASSICAL_COMPLEX_ONLY",
            "proof_sha256": _sha256(DEPENDENCIES["Nariai_metric_Bach_complex"]),
        },
        {
            "candidate_id": berger["result_id"],
            "C2_visible": True,
            "repository_operator": False,
            "Euclidean_elliptic_full_BV": False,
            "measure_and_regulator": False,
            "coefficient_vector": False,
            "disposition": "INELIGIBLE_COUPLED_REDUCED_MODE_CLASSICAL_BACKGROUND",
            "proof_sha256": _sha256(DEPENDENCIES["positive_Berger_clock"]),
        },
        {
            "candidate_id": standard["result_id"],
            "C2_visible": True,
            "repository_operator": False,
            "Euclidean_elliptic_full_BV": False,
            "measure_and_regulator": False,
            "coefficient_vector": True,
            "disposition": "INELIGIBLE_STANDARD_VECTOR_NOT_REPOSITORY_MATCHED",
            "proof_sha256": _sha256(DEPENDENCIES["standard_coefficient_vector"]),
        },
        {
            "candidate_id": sphere["result_id"],
            "C2_visible": False,
            "repository_operator": True,
            "Euclidean_elliptic_full_BV": True,
            "measure_and_regulator": True,
            "coefficient_vector": False,
            "disposition": "INELIGIBLE_C2_INVISIBLE_ON_CONFORMALLY_FLAT_BACKGROUND",
            "proof_sha256": _sha256(DEPENDENCIES["repository_round_S4_Euler"]),
        },
    ]


def build() -> dict[str, Any]:
    fixture = synthetic_payload(repository_root=ROOT)
    receipt = validate_nonconformal_coefficient_match(
        fixture, repository_root=ROOT, allow_synthetic_fixture=True
    )
    mutations = mutation_receipts(fixture)
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    candidates = _candidate_audit(values)
    if (
        receipt["status"] != "SEMANTIC_RECEIVER_ACCEPTED"
        or not all(row["rejected"] for row in mutations)
        or any(
            row["C2_visible"]
            and row["repository_operator"]
            and row["Euclidean_elliptic_full_BV"]
            and row["measure_and_regulator"]
            and row["coefficient_vector"]
            for row in candidates
        )
    ):
        raise AssertionError("nonconformal coefficient readiness boundary failed")
    contract = {
        "required_result_id": "REPOSITORY_NONCONFORMALLY_FLAT_OR_RICCI_FLAT_FULL_BV_OPERATOR_MEASURE_COEFFICIENT_MATCH",
        "input_schema_path": str(INPUT_SCHEMA.relative_to(ROOT)),
        "required_analytic_route": "EUCLIDEAN_ELLIPTIC",
        "required_basis": ["C2", "E4", "CdualC", "BoxR"],
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
    value = {
        "schema": "quantum-weyl-repository-nonconformal-coefficient-match-readiness-v1",
        "result_id": "REPOSITORY_NONCONFORMAL_COEFFICIENT_MATCH_READINESS",
        "result_state": "RECEIVER_READY_CURRENT_CANDIDATES_FAIL_COMPLEMENTARY_GATES",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "dependency_hashes": proof_payload["dependency_hashes"],
        "accepted_contract": contract,
        "receiver_mechanics": {
            "scope": "SYNTHETIC_EXACT_ARITHMETIC_AND_ROLE_MECHANICS_ONLY",
            "synthetic_receipt": receipt,
            "mutation_receipts": mutations,
        },
        "current_candidate_audit": candidates,
        "minimal_missing_carrier_theorem": {
            "status": "NO_CURRENT_CANDIDATE_SATISFIES_INTERSECTION",
            "required_intersection": [
                "C2_VISIBLE",
                "REPOSITORY_OPERATOR",
                "EUCLIDEAN_ELLIPTIC_FULL_BV",
                "MEASURE_AND_REGULATOR",
                "EXACT_COEFFICIENT_VECTOR",
            ],
            "minimal_next_artifact": contract["required_result_id"],
            "Nariai_is_not_silently_promotable": True,
            "Berger_is_not_silently_promotable": True,
            "round_S4_is_not_C2_visible": True,
        },
        "claim_flags": {
            "NONCONFORMAL_COEFFICIENT_MATCH_RECEIVER_READY": True,
            "CURRENT_CANDIDATES_AUDITED": True,
            "PHYSICAL_C2_CARRIER_SUPPLIED": False,
            "REPOSITORY_C2_COEFFICIENT_COMPUTED": False,
            "REGULATED_SLAVNOV_BREAKING_COMPUTED": False,
            "QME_DISPOSITION": False,
        },
        "proof_sha256": _canonical_hash(proof_payload),
        "next_gate": contract["required_result_id"],
        "claim_boundary": (
            "This LOCAL-ALGEBRAIC plus EUCLIDEAN-SPECTRAL readiness theorem "
            "defines a strict semantic receiver for a C2-visible physical full-BV "
            "coefficient match and audits every current nearby carrier. Nariai is "
            "non-conformally-flat and has an action-paired classical Bach complex, "
            "but no Euclidean elliptic determinant, BV measure, regulator, or local "
            "coefficient vector. The Berger clock is a coupled reduced-mode classical "
            "background. The standard vector is not repository matched, while round "
            "S4 is repository matched but C2-invisible. The synthetic fixture tests "
            "receiver mechanics only. No repository c coefficient, Slavnov breaking, "
            "QME disposition, residual transfer, or Lorentzian quantum theory is claimed."
        ),
        "provenance": {
            "source_sha256": {path: _sha256(ROOT / path) for path in SOURCE_PATHS}
        },
    }
    return value


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
        raise SystemExit(f"stale nonconformal coefficient readiness: {OUTPUT}")
    print("repository nonconformal coefficient match readiness: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
