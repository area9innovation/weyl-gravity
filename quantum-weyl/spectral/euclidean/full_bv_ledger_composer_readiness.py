"""Readiness certificate for the round-S4 full-BV multiplicity composer."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

try:
    from .full_bv_ledger_composer import (
        DEPENDENCIES,
        compose_repository_multiplicity_export,
        mutation_receipts,
        validate_composed_repository_multiplicity_export,
    )
    from .tt_hessian_dictionary_receiver import synthetic_payload
except ImportError:
    from full_bv_ledger_composer import (
        DEPENDENCIES,
        compose_repository_multiplicity_export,
        mutation_receipts,
        validate_composed_repository_multiplicity_export,
    )
    from tt_hessian_dictionary_receiver import synthetic_payload


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = HERE / "certificates/REPOSITORY_FULL_BV_LEDGER_COMPOSER_READINESS.json"
SCHEMA = HERE / "schema/repository-full-bv-ledger-composer-readiness-v1.schema.json"
EXPORT_SCHEMA = HERE / "schema/repository-full-bv-multiplicity-export-v1.schema.json"
TT_READINESS = HERE / "certificates/REPOSITORY_ROUND_S4_TT_HESSIAN_DICTIONARY_RECEIVER_READINESS.json"
FIXTURE = HERE / "fixtures/SYNTHETIC_ROUND_S4_TT_HESSIAN_DICTIONARY.json"

SOURCE_PATHS = (
    "quantum-weyl/spectral/euclidean/full_bv_ledger_composer.py",
    "quantum-weyl/spectral/euclidean/full_bv_ledger_composer_readiness.py",
    "quantum-weyl/spectral/euclidean/verify_full_bv_ledger_composer_readiness.py",
    "quantum-weyl/spectral/euclidean/schema/repository-full-bv-ledger-composer-readiness-v1.schema.json",
    "quantum-weyl/spectral/euclidean/tests/test_full_bv_ledger_composer.py",
    "quantum-weyl/spectral/euclidean/fixtures/SYNTHETIC_ROUND_S4_TT_HESSIAN_DICTIONARY.json",
    "quantum-weyl/reports/repository-full-bv-ledger-composer-readiness.md",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _artifact(path: Path) -> dict[str, str]:
    return {
        "format": "JSON_DATA",
        "path": str(path.relative_to(ROOT)),
        "sha256": _sha256(path),
    }


def _expected_fixture() -> dict[str, Any]:
    readiness = json.loads(TT_READINESS.read_text())
    return synthetic_payload(classical_commit=readiness["classical_commit"])


def emit_fixture() -> None:
    FIXTURE.parent.mkdir(parents=True, exist_ok=True)
    FIXTURE.write_text(json.dumps(_expected_fixture(), indent=2, sort_keys=True) + "\n")


def build() -> dict[str, Any]:
    tt_readiness = json.loads(TT_READINESS.read_text())
    if (
        tt_readiness.get("result_state")
        != "SEMANTIC_RECEIVER_READY_PHYSICAL_TT_DICTIONARY_INPUT_NOT_SUPPLIED"
        or tt_readiness.get("claim_flags", {}).get(
            "TT_HESSIAN_DICTIONARY_SEMANTIC_RECEIVER_READY"
        )
        is not True
    ):
        raise ValueError("TT dictionary receiver readiness drifted")
    expected_fixture = _expected_fixture()
    fixture = json.loads(FIXTURE.read_text())
    if fixture != expected_fixture:
        raise ValueError("synthetic TT dictionary fixture is stale")
    classical_commit = tt_readiness["classical_commit"]
    fixture_artifact = _artifact(FIXTURE)
    payload = compose_repository_multiplicity_export(
        fixture,
        tt_dictionary_artifact=fixture_artifact,
        expected_classical_commit=classical_commit,
    )
    receipt = validate_composed_repository_multiplicity_export(
        payload,
        tt_payload=fixture,
        tt_dictionary_artifact=fixture_artifact,
        expected_classical_commit=classical_commit,
    )
    mutations = mutation_receipts(
        payload,
        tt_payload=fixture,
        tt_dictionary_artifact=fixture_artifact,
        expected_classical_commit=classical_commit,
    )
    if (
        receipt["status"] != "COMPOSED_LEDGER_SEMANTICALLY_ACCEPTED"
        or not all(row["rejected"] for row in mutations)
    ):
        raise AssertionError("full-BV composer mutation battery failed")
    dependency_hashes = {
        name: _sha256(path) for name, path in DEPENDENCIES.items()
    }
    dependency_hashes.update(
        {
            "TT_dictionary_receiver_readiness": _sha256(TT_READINESS),
            "multiplicity_export_schema": _sha256(EXPORT_SCHEMA),
            "synthetic_TT_input": _sha256(FIXTURE),
        }
    )
    contract = {
        "required_input_result_id": "REPOSITORY_ROUND_S4_TT_HESSIAN_DICTIONARY_V1",
        "produced_result_id": "REPOSITORY_FULL_BV_MULTIPLICITY_LEDGER",
        "analytic_route": "EUCLIDEAN_ELLIPTIC",
        "integration_stage": "REDUCED_AFTER_EXACT_YORK_HODGE_SCALAR_FP_AND_NONMINIMAL_CANCELLATIONS",
        "standard_factor_operators": [
            "Delta_2_perp(4)",
            "Delta_0(-4)",
            "Delta_2_perp(2)",
            "Delta_1_perp(-3)",
        ],
        "physical_input_status": "NOT_SUPPLIED",
    }
    proof_payload = {
        "dependencies": dependency_hashes,
        "contract": contract,
        "receipt": receipt,
        "mutations": mutations,
    }
    value = {
        "schema": "quantum-weyl-repository-full-bv-ledger-composer-readiness-v1",
        "result_id": "REPOSITORY_FULL_BV_LEDGER_COMPOSER_READINESS",
        "result_state": "ALL_STANDARD_ROWS_BOUND_COMPOSER_READY_PHYSICAL_TT_INPUT_NOT_SUPPLIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "classical_commit": classical_commit,
        "dependency_hashes": dependency_hashes,
        "closed_standard_inputs": {
            "scalar_Diff_Weyl_rank_two_to_one": True,
            "York_Hodge_measure": True,
            "nonminimal_quartet_Berezinian": True,
            "round_S4_zero_modes_0_5_0_10": True,
            "standard_Z_exponents_minus_half_plus_half_minus_half_plus_half": True,
        },
        "accepted_contract": contract,
        "composer_mechanics": {
            "scope": "SYNTHETIC_TT_INPUT_WITH_REAL_NON_TT_CERTIFICATES",
            "synthetic_receipt": receipt,
            "mutation_receipts": mutations,
        },
        "claim_flags": {
            "FULL_BV_LEDGER_COMPOSER_READY": True,
            "ALL_NON_TT_STANDARD_ROWS_BOUND": True,
            "COMPOSER_EXACT_EXPONENT_AND_ZERO_MODE_POLICY_ENFORCED": True,
            "PHYSICAL_TT_DICTIONARY_INPUT_SUPPLIED": False,
            "REPOSITORY_FULL_BV_MULTIPLICITY_LEDGER_ACCEPTED": False,
            "GLOBAL_DETERMINANT_PHASE_FIXED": False,
            "FINITE_CONFORMAL_GROUP_VOLUME_NORMALIZED": False,
            "REPOSITORY_ANOMALY_COEFFICIENT_COMPUTED": False,
            "REGULATED_SLAVNOV_BREAKING_COMPUTED": False,
            "QME_DISPOSITION": False,
        },
        "proof_sha256": _canonical_hash(proof_payload),
        "next_gate": "SUPPLY_PHYSICAL_REPOSITORY_ROUND_S4_TT_HESSIAN_DICTIONARY_V1_AND_COMPOSE_LEDGER",
        "claim_boundary": (
            "This LOCAL-ALGEBRAIC plus EUCLIDEAN-SPECTRAL readiness artifact "
            "proves that the exact scalar Diff-Weyl reduction, York/Hodge measure, "
            "nonminimal quartet Berezinian, round-S4 zero modes, and four standard "
            "local heat-kernel determinant exponents can be composed mechanically "
            "with one accepted repository TT Hessian dictionary into a complete "
            "REPOSITORY_FULL_BV_MULTIPLICITY_LEDGER. The synthetic TT input tests "
            "composer mechanics only; it is not evidence for the repository Hessian. "
            "No physical TT input or repository multiplicity ledger has therefore "
            "been accepted. The result also does not fix the global determinant "
            "phase, conformal-group volume, regulated Slavnov breaking, QME, "
            "residual transfer, or Lorentzian quantum theory."
        ),
        "provenance": {
            "source_sha256": {path: _sha256(ROOT / path) for path in SOURCE_PATHS}
        },
    }
    validate_claim_boundary(value)
    return value


def validate_claim_boundary(value: dict[str, Any]) -> None:
    flags = value.get("claim_flags", {})
    if not all(
        flags.get(name) is True
        for name in (
            "FULL_BV_LEDGER_COMPOSER_READY",
            "ALL_NON_TT_STANDARD_ROWS_BOUND",
            "COMPOSER_EXACT_EXPONENT_AND_ZERO_MODE_POLICY_ENFORCED",
        )
    ) or any(
        flags.get(name) is not False
        for name in (
            "PHYSICAL_TT_DICTIONARY_INPUT_SUPPLIED",
            "REPOSITORY_FULL_BV_MULTIPLICITY_LEDGER_ACCEPTED",
            "GLOBAL_DETERMINANT_PHASE_FIXED",
            "FINITE_CONFORMAL_GROUP_VOLUME_NORMALIZED",
            "REPOSITORY_ANOMALY_COEFFICIENT_COMPUTED",
            "REGULATED_SLAVNOV_BREAKING_COMPUTED",
            "QME_DISPOSITION",
        )
    ):
        raise ValueError("full-BV composer readiness crossed its claim boundary")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.emit:
        emit_fixture()
    value = build()
    schema = json.loads(SCHEMA.read_text())
    export_schema = json.loads(EXPORT_SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator.check_schema(export_schema)
    Draft202012Validator(schema).validate(value)
    rendered = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if args.emit:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(rendered)
    if args.check and (not OUTPUT.exists() or OUTPUT.read_text() != rendered):
        raise SystemExit(f"stale full-BV ledger composer readiness: {OUTPUT}")
    print("repository full-BV ledger composer readiness: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
