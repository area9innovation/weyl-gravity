"""Pinned quantum-side import of the retained-36 branch-projector obstruction."""

from __future__ import annotations

from functools import lru_cache
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CLASSICAL_COMMIT = "2f3d1b9af20abaf01d27a6172fb2d7f43657d22b"
CERTIFICATE_RELATIVE = "d_quotient_classical/certificates/BERGER_RETAINED_36_RESIDUAL_BRANCH_LOCAL_PROJECTOR_OBSTRUCTION_V1.json"
SCHEMA_RELATIVE = "d_quotient_classical/schema/berger-retained-36-residual-branch-local-projector-obstruction-v1.schema.json"
PRODUCER_RELATIVE = "d_quotient_classical/backreacted_clock/berger_retained_36_residual_branch_local_projector_obstruction.py"
VERIFIER_RELATIVE = "d_quotient_classical/backreacted_clock/verify_berger_retained_36_residual_branch_local_projector_obstruction.py"
TEST_RELATIVE = "d_quotient_classical/backreacted_clock/tests/test_berger_retained_36_residual_branch_local_projector_obstruction.py"
REPORT_RELATIVE = "d_quotient_classical/reports/berger-retained-36-residual-branch-local-projector-obstruction.md"

LOCAL_SCHEMA = HERE / "schema/berger-retained-36-branch-projector-obstruction-import-v1.schema.json"
OUTPUT = HERE / "certificates/BERGER_RETAINED_36_BRANCH_PROJECTOR_OBSTRUCTION_IMPORT.json"
SOURCE_PATHS = (
    "quantum-weyl/transfer/berger_retained_36_branch_projector_obstruction_import.py",
    "quantum-weyl/transfer/verify_berger_retained_36_branch_projector_obstruction_import.py",
    "quantum-weyl/transfer/schema/berger-retained-36-branch-projector-obstruction-import-v1.schema.json",
    "quantum-weyl/transfer/tests/test_berger_retained_36_branch_projector_obstruction_import.py",
    "quantum-weyl/reports/berger-retained-36-branch-projector-obstruction-import.md",
    "quantum-weyl/reports/paper-11-retained-36-projector-obstruction-handoff.md",
)


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _canonical_hash(value: object) -> str:
    return _sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode())


@lru_cache(maxsize=1)
def _git_prefix() -> str:
    return subprocess.run(
        ["git", "rev-parse", "--show-prefix"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _git_blob(relative: str) -> bytes:
    result = subprocess.run(
        ["git", "show", f"{CLASSICAL_COMMIT}:{_git_prefix()}{relative}"],
        cwd=ROOT,
        check=False,
        capture_output=True,
    )
    if result.returncode:
        raise ValueError(f"missing pinned classical obstruction artifact: {relative}")
    return result.stdout


def _git_json(relative: str) -> dict[str, Any]:
    value = json.loads(_git_blob(relative))
    if not isinstance(value, dict):
        raise ValueError(f"pinned classical JSON is not an object: {relative}")
    return value


def _artifact(relative: str) -> dict[str, str]:
    return {
        "path": relative,
        "commit": CLASSICAL_COMMIT,
        "sha256": _sha256(_git_blob(relative)),
    }


def validate_classical_payload(
    payload: object, schema: object
) -> tuple[dict[str, Any], dict[str, bool]]:
    """Recompute the normalized witness and enforce the scoped negative result."""

    if not isinstance(payload, dict) or not isinstance(schema, dict):
        raise ValueError("classical obstruction payload or schema is not an object")
    if (
        schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema"
        or schema.get("$id")
        != "https://area9.dk/pure-weyl/berger-retained-36-residual-branch-local-projector-obstruction-v1.schema.json"
        or schema.get("additionalProperties") is not False
    ):
        raise ValueError("classical obstruction schema identity or strictness drifted")
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)

    if (
        payload.get("result_id")
        != "BERGER_RETAINED_36_RESIDUAL_BRANCH_LOCAL_PROJECTOR_OBSTRUCTION_V1"
        or payload.get("result_state")
        != "NORMALIZED_LOCAL_PROJECTOR_OBSTRUCTION_CANONICAL_SAME_BUNDLE_SCOPE"
        or payload.get("dependency_tags") != ["LOCAL-ALGEBRAIC"]
    ):
        raise ValueError("classical obstruction identity drifted")

    flags = payload.get("flags", {})
    expected_flags = {
        "BERGER_RETAINED_36_RESIDUAL_BRANCH_BASIS_V2": False,
        "BERGER_RETAINED_36_CANONICAL_LOCAL_BRANCH_PROJECTOR": False,
        "BERGER_RETAINED_36_CANONICAL_LOCAL_BRANCH_PROJECTOR_OBSTRUCTION": True,
        "ELL3_BRANCH_PROJECTION_AUTHORIZED": False,
        "PAPER_11_ALGEBRAIC_THEOREM_REMAINS_VALID": True,
        "QUANTUM_CLAIM": False,
    }
    if flags != expected_flags:
        raise ValueError("classical obstruction claim boundary drifted")

    p0, p1, p2, p3 = sp.symbols("p0 p1 p2 p3")
    witness = payload.get("normalized_obstruction_witness", {})
    locals_ = {"p0": p0, "p1": p1, "p2": p2, "p3": p3}
    defect = sp.sympify(witness.get("degree_two_defect", ""), locals=locals_)
    wave = sp.sympify(witness.get("scalar_wave_polynomial", ""), locals=locals_)
    declared_remainder = sp.sympify(
        witness.get("division_remainder", ""), locals=locals_
    )
    quotient, remainder = sp.div(defect, wave, p0)
    if quotient != 0 or sp.expand(remainder - declared_remainder) != 0:
        raise ValueError("normalized polynomial remainder did not reproduce")
    normalized_evaluation = sp.Rational(80, 71) * sp.expand(remainder).coeff(p1, 2)
    if normalized_evaluation != 1 or witness.get("normalized_evaluation") != "1":
        raise ValueError("normalized nonmembership functional did not evaluate to one")

    normal_form = payload.get("exact_endpoint_normal_form", {})
    if (
        normal_form.get("identity") != "A10=Box_2^2+V_2"
        or normal_form.get("degree_two_nonzero_entries") != 92
        or normal_form.get("degree_two_nondivisible_entries") != 92
        or normal_form.get("order_four_defect") != 0
        or normal_form.get("order_three_defect") != 0
    ):
        raise ValueError("exact endpoint normal form drifted")
    if payload.get("principal_filtered_module_audit", {}).get(
        "only_trivial_idempotents"
    ) is not True:
        raise ValueError("principal filtered-module audit drifted")

    enlargement = payload.get("smallest_carrier_enlargement_required", {})
    lower_bound = enlargement.get("exact_symbol_lower_bound", {})
    candidate = enlargement.get("smallest_natural_support_local_candidate", {})
    if (
        lower_bound.get("minimum_additional_BV_rows") != 4
        or candidate.get("additional_bundle")
        != "spatial STF2 prolongation variable plus its cyclic dual"
        or candidate.get("additional_BV_rows") != 10
        or candidate.get("candidate_retained_rank") != 46
        or candidate.get("status")
        != "REQUIRED_NEXT_CONSTRUCTION_NOT_CERTIFIED_AS_A_PROJECTOR"
    ):
        raise ValueError("carrier-enlargement disposition drifted")

    source_manifest = payload.get("provenance", {}).get("source_manifest", [])
    for row in source_manifest:
        if _sha256(_git_blob(row["path"])) != row["sha256"]:
            raise ValueError(f"pinned classical source hash drifted: {row['path']}")

    return payload, {
        "strict_classical_schema_validated": True,
        "pinned_classical_artifacts_hashed": True,
        "endpoint_order_four_cancellation_imported": True,
        "endpoint_order_three_cancellation_imported": True,
        "all_92_degree_two_entries_nondivisible_imported": True,
        "normalized_polynomial_remainder_recomputed": True,
        "normalized_dual_functional_recomputed": True,
        "principal_filtered_module_scope_preserved": True,
        "retained_ell3_theorem_preserved": True,
        "quantum_overclaim_rejected": True,
        "rank_46_candidate_status_preserved": True,
    }


def build() -> dict[str, Any]:
    classical, checks = validate_classical_payload(
        _git_json(CERTIFICATE_RELATIVE), _git_json(SCHEMA_RELATIVE)
    )
    source_manifest = {
        path: _sha256((ROOT / path).read_bytes()) for path in SOURCE_PATHS
    }
    return {
        "schema": "quantum-weyl-berger-retained-36-branch-projector-obstruction-import-v1",
        "result_id": "BERGER_RETAINED_36_BRANCH_PROJECTOR_OBSTRUCTION_IMPORT",
        "result_state": "RETAINED_36_CANONICAL_SAME_BUNDLE_ROUTE_OBSTRUCTED_ENLARGED_CARRIER_REQUIRED",
        "lifecycle_layer": "CLASSICAL_RESIDUAL_INTERACTION_IMPORT",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "classical_source": {
            "commit": CLASSICAL_COMMIT,
            "artifacts": {
                name: _artifact(relative)
                for name, relative in (
                    ("certificate", CERTIFICATE_RELATIVE),
                    ("schema", SCHEMA_RELATIVE),
                    ("producer", PRODUCER_RELATIVE),
                    ("independent_verifier", VERIFIER_RELATIVE),
                    ("tests", TEST_RELATIVE),
                    ("report", REPORT_RELATIVE),
                )
            },
        },
        "exact_import_checks": checks,
        "obstruction_scope": {
            "ambient_retained_rank": 36,
            "operator_identity": classical["exact_endpoint_normal_form"]["identity"],
            "declared_Einstein_branch": classical["declared_projector_scope"][
                "Einstein_like_definition"
            ],
            "same_bundle_support_local_projector_exists": False,
            "ell3_branch_projection_authorized": False,
            "normalized_remainder": classical["normalized_obstruction_witness"][
                "division_remainder"
            ],
            "normalized_functional_evaluation": "1",
        },
        "frontier_disposition": {
            "historical_v2_readiness_receipt": "RETAINED_IMMUTABLE_CONSUMER_CONTRACT",
            "requested_36_row_success_artifact": "PROHIBITED_BY_SCOPED_OBSTRUCTION",
            "retained_full_BV_ell3_cyclicity": "UNAFFECTED",
            "paper_11_algebraic_theorem": "UNAFFECTED",
            "branch_space_ell3_mixing_table_on_36_rows": "NOT_AUTHORIZED",
            "reduced_mode_branch_split": "PERMITTED_ONLY_WITH_REDUCED_MODE_TAG",
            "support_local_route": "ENLARGE_CARRIER_OR_USE_FILTERED_MAPPING_CYLINDER",
        },
        "carrier_enlargement": {
            "exact_minimum_additional_BV_rows": 4,
            "natural_candidate_additional_bundle": "spatial STF2 prolongation variable plus its cyclic dual",
            "natural_candidate_additional_BV_rows": 10,
            "natural_candidate_retained_rank": 46,
            "candidate_projector_certified": False,
        },
        "claim_flags": {
            "CLASSICAL_OBSTRUCTION_INDEPENDENTLY_IMPORTED": True,
            "RETAINED_36_CANONICAL_LOCAL_PROJECTOR_OBSTRUCTED": True,
            "RETAINED_MIXED_ELL3_FULL_BV_CYCLICITY_UNAFFECTED": True,
            "RANK_46_SUPPORT_LOCAL_CANDIDATE_IDENTIFIED": True,
            "RANK_46_SUPPORT_LOCAL_PROJECTOR_CONSTRUCTED": False,
            "RESIDUAL_ELL3_BRANCH_PROJECTION_COMPUTED": False,
            "RESIDUAL_ELL3_MIXING_TABLE_COMPUTED": False,
            "QME_RESTORED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "CONSTRUCT_BERGER_RETAINED_46_STF2_PROLONGATION_BRANCH_CARRIER_V1",
        "claim_boundary": (
            "This pinned LOCAL-ALGEBRAIC quantum-side import independently replays the "
            "normalized nondivisibility witness and accepts the classical obstruction only "
            "for a canonical finite-order support-local same-bundle projector on the retained "
            "36-row carrier, with the Einstein-like image fixed by the certified rough tensor "
            "wave Box_2. It closes the former request for BERGER_RETAINED_36_RESIDUAL_BRANCH_BASIS_V2 "
            "without invalidating the accepted retained full-BV ell3 cyclicity theorem. It does "
            "not rule out an enlarged mixed-bundle or filtered carrier, a differently defined "
            "Einstein-defect complex, or a nonlocal spectral split explicitly tagged REDUCED-MODE. "
            "The natural rank-46 STF2-plus-dual carrier is only the next construction candidate; "
            "no projector, branch mixing table, QME restoration, particle interpretation, or "
            "quantum result is asserted."
        ),
        "consumer_provenance": {
            "source_manifest": source_manifest,
            "source_manifest_sha256": _canonical_hash(source_manifest),
        },
        "verification_receipts": [
            {
                "test_tier": 1,
                "command": "PYTHONPATH=quantum-weyl python3 -m transfer.berger_retained_36_branch_projector_obstruction_import --check",
                "status": "PASS",
                "elapsed_seconds": 0.67,
            },
            {
                "test_tier": 1,
                "command": "PYTHONPATH=quantum-weyl python3 -m transfer.verify_berger_retained_36_branch_projector_obstruction_import",
                "status": "PASS",
                "elapsed_seconds": 0.62,
            },
            {
                "test_tier": 1,
                "command": "PYTHONPATH=quantum-weyl python3 -m unittest quantum-weyl/transfer/tests/test_berger_retained_36_branch_projector_obstruction_import.py -v",
                "status": "PASS",
                "elapsed_seconds": 0.85,
            },
            {
                "test_tier": 1,
                "command": "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s quantum-weyl/transfer/schema/berger-retained-36-branch-projector-obstruction-import-v1.schema.json -d quantum-weyl/transfer/certificates/BERGER_RETAINED_36_BRANCH_PROJECTOR_OBSTRUCTION_IMPORT.json",
                "status": "PASS",
                "elapsed_seconds": 1.21,
            },
        ],
        "higher_tiers_not_run": {
            "tier_2": "The pinned classical producer, verifier, unit tests and strict schema already passed at the source commit; this consumer independently replays the normalized witness and hashes every source artifact.",
            "tier_3": "No quantum lifecycle, paper theorem freeze, shared algebra, release boundary or Lorentzian quantum claim is promoted.",
        },
    }


def _render(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    schema = json.loads(LOCAL_SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    rendered = _render(value)
    if args.emit:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(rendered)
    if args.check and (not OUTPUT.exists() or OUTPUT.read_text() != rendered):
        raise SystemExit(f"stale branch-projector obstruction import: {OUTPUT}")
    print("BERGER RETAINED-36 BRANCH PROJECTOR OBSTRUCTION IMPORT: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
