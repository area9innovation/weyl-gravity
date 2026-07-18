"""Readiness certificate for the round-S4 TT Hessian dictionary receiver."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any, Callable

from jsonschema import Draft202012Validator

try:
    from .tt_hessian_dictionary_receiver import (
        SCHEMA as INPUT_SCHEMA,
        synthetic_payload,
        validate_tt_hessian_dictionary,
    )
except ImportError:
    from tt_hessian_dictionary_receiver import (
        SCHEMA as INPUT_SCHEMA,
        synthetic_payload,
        validate_tt_hessian_dictionary,
    )


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = HERE / "certificates/REPOSITORY_ROUND_S4_TT_HESSIAN_DICTIONARY_RECEIVER_READINESS.json"
SCHEMA = HERE / "schema/repository-round-s4-tt-hessian-dictionary-receiver-readiness-v1.schema.json"
MISSING_CARRIER = HERE / "certificates/REPOSITORY_TT_HESSIAN_NORMALIZATION_READINESS.json"

SOURCE_PATHS = (
    "quantum-weyl/spectral/euclidean/tt_hessian_dictionary_receiver.py",
    "quantum-weyl/spectral/euclidean/tt_hessian_dictionary_receiver_readiness.py",
    "quantum-weyl/spectral/euclidean/verify_tt_hessian_dictionary_receiver_readiness.py",
    "quantum-weyl/spectral/euclidean/schema/repository-round-s4-tt-hessian-dictionary-input-v1.schema.json",
    "quantum-weyl/spectral/euclidean/schema/repository-round-s4-tt-hessian-dictionary-receiver-readiness-v1.schema.json",
    "quantum-weyl/spectral/euclidean/tests/test_tt_hessian_dictionary_receiver.py",
    "quantum-weyl/reports/repository-round-s4-tt-hessian-dictionary-receiver-readiness.md",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _rejects(payload: dict[str, Any], expected_commit: str) -> bool:
    try:
        validate_tt_hessian_dictionary(payload, repository_root=ROOT, expected_classical_commit=expected_commit)
    except Exception:
        return True
    return False


def mutation_receipts(payload: dict[str, Any], expected_commit: str) -> list[dict[str, Any]]:
    mutations: tuple[tuple[str, Callable[[dict[str, Any]], None]], ...] = (
        ("kappa_2_over_3", lambda row: row["action_normalization"].update(kappa={"numerator": 2, "denominator": 3})),
        ("upper_shift_5", lambda row: row["operator_dictionary"].update(upper_factor="Delta_2_perp(5)")),
        ("bad_nested_hash", lambda row: row["proof_artifacts"][0].update(sha256="0" * 64)),
        ("wrong_classical_commit", lambda row: row.update(classical_commit="1" * 40)),
    )
    receipts = []
    for name, mutate in mutations:
        mutant = deepcopy(payload)
        mutate(mutant)
        receipts.append({"mutation": name, "rejected": _rejects(mutant, expected_commit)})
    return receipts


def build() -> dict[str, Any]:
    missing = json.loads(MISSING_CARRIER.read_text())
    if (
        missing.get("next_gate") != "SUPPLY_REPOSITORY_ROUND_S4_TT_HESSIAN_DICTIONARY_V1"
        or missing["claim_flags"]["REPOSITORY_PHYSICAL_HESSIAN_NORMALIZED"] is not False
    ):
        raise ValueError("TT Hessian missing-carrier dependency drifted")
    classical_commit = missing["classical_commit"]
    fixture = synthetic_payload(classical_commit=classical_commit)
    receipt = validate_tt_hessian_dictionary(
        fixture, repository_root=ROOT, expected_classical_commit=classical_commit
    )
    mutations = mutation_receipts(fixture, classical_commit)
    if receipt["status"] != "SEMANTIC_RECEIVER_ACCEPTED" or not all(row["rejected"] for row in mutations):
        raise AssertionError("TT Hessian dictionary receiver mutation battery failed")
    contract = {
        "required_result_id": "REPOSITORY_ROUND_S4_TT_HESSIAN_DICTIONARY_V1",
        "input_schema_path": str(INPUT_SCHEMA.relative_to(ROOT)),
        "required_kappa": {"numerator": 1, "denominator": 2},
        "required_operator": "(1/2) Delta_2_perp(2) Delta_2_perp(4)",
        "required_proof_artifacts": ["content-addressed producer", "content-addressed independent verifier"],
        "physical_input_status": "NOT_SUPPLIED",
    }
    proof_payload = {
        "missing": _sha256(MISSING_CARRIER),
        "input_schema": _sha256(INPUT_SCHEMA),
        "receipt": receipt,
        "mutations": mutations,
        "contract": contract,
    }
    value = {
        "schema": "quantum-weyl-repository-round-s4-tt-hessian-dictionary-receiver-readiness-v1",
        "result_id": "REPOSITORY_ROUND_S4_TT_HESSIAN_DICTIONARY_RECEIVER_READINESS",
        "result_state": "SEMANTIC_RECEIVER_READY_PHYSICAL_TT_DICTIONARY_INPUT_NOT_SUPPLIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "classical_commit": classical_commit,
        "dependency_hashes": {"missing_carrier_certificate": _sha256(MISSING_CARRIER), "input_schema": _sha256(INPUT_SCHEMA)},
        "accepted_contract": contract,
        "receiver_mechanics": {"scope": "SYNTHETIC_EXACT_RECEIVER_MECHANICS_ONLY", "synthetic_receipt": receipt, "mutation_receipts": mutations},
        "claim_flags": {
            "TT_HESSIAN_DICTIONARY_SEMANTIC_RECEIVER_READY": True,
            "KAPPA_HALF_AND_FACTOR_SHIFTS_ENFORCED": True,
            "CONTENT_ADDRESSED_PROOF_ARTIFACTS_ENFORCED": True,
            "PHYSICAL_TT_DICTIONARY_INPUT_SUPPLIED": False,
            "REPOSITORY_PHYSICAL_HESSIAN_NORMALIZED": False,
            "REPOSITORY_FULL_BV_MULTIPLICITY_LEDGER_ACCEPTED": False,
            "REPOSITORY_ANOMALY_COEFFICIENT_COMPUTED": False,
            "QME_DISPOSITION": False,
        },
        "proof_sha256": _canonical_hash(proof_payload),
        "next_gate": "SUPPLY_AND_ACCEPT_REPOSITORY_ROUND_S4_TT_HESSIAN_DICTIONARY_V1",
        "claim_boundary": (
            "This LOCAL-ALGEBRAIC plus EUCLIDEAN-SPECTRAL artifact supplies a strict semantic receiver for the missing repository round-S4 TT Hessian dictionary. The input contract enforces the fixed round-unit-S4 background, repository S_red normalization, flat-TT leading-symbol coefficient kappa=1/2, exact factors Delta_2_perp(2) and Delta_2_perp(4), formal self-adjointness, ellipticity on the real TT bundle, zero physical kernel, and content-addressed producer/verifier artifacts. A synthetic fixture exercises the complete receiver surface, while mutations of kappa, the upper factor shift, a nested hash, and the classical commit are rejected. The synthetic receipt is not scientific evidence for the operator identity. No physical producer input has been supplied or accepted, so the repository Hessian, full-BV multiplicity ledger, anomaly coefficients, Slavnov breaking, QME disposition, D-Cartan class, residual transfer, and Lorentzian quantum theory remain open."
        ),
        "provenance": {"source_sha256": {path: _sha256(ROOT / path) for path in SOURCE_PATHS}},
    }
    validate_claim_boundary(value)
    return value


def validate_claim_boundary(value: dict[str, Any]) -> None:
    flags = value.get("claim_flags", {})
    if not all(flags.get(name) is True for name in (
        "TT_HESSIAN_DICTIONARY_SEMANTIC_RECEIVER_READY",
        "KAPPA_HALF_AND_FACTOR_SHIFTS_ENFORCED",
        "CONTENT_ADDRESSED_PROOF_ARTIFACTS_ENFORCED",
    )) or any(flags.get(name) is not False for name in (
        "PHYSICAL_TT_DICTIONARY_INPUT_SUPPLIED",
        "REPOSITORY_PHYSICAL_HESSIAN_NORMALIZED",
        "REPOSITORY_FULL_BV_MULTIPLICITY_LEDGER_ACCEPTED",
        "REPOSITORY_ANOMALY_COEFFICIENT_COMPUTED",
        "QME_DISPOSITION",
    )):
        raise ValueError("TT Hessian dictionary receiver claim boundary crossed")


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
        raise SystemExit(f"stale TT Hessian dictionary receiver readiness: {OUTPUT}")
    print("repository round-S4 TT Hessian dictionary receiver readiness: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
