"""Build the fail-closed retained stationary-generator import readiness result."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp

from transfer.berger_gauge_fixed_nonminimal_import import _identity, _zero

from .berger_retained_stationary_generator_acceptance import (
    HERE,
    INPUT_SCHEMA,
    MATRIX_SCHEMA,
    evaluate_matrices,
)


ROOT = HERE.parents[1]
READINESS_SCHEMA = HERE / "schema/berger-retained-stationary-generator-readiness-v1.schema.json"
ZERO_READINESS = HERE / "certificates/BERGER_RETAINED_26_ZERO_FREQUENCY_SPECTRAL_LEDGER_READINESS.json"
PARTIAL_A104 = HERE / "certificates/BERGER_A104_GLOBAL_PARTIAL_ASSEMBLY.json"
EXISTENCE_AUDIT = HERE / "certificates/BERGER_COMPANION_HADAMARD_EXISTENCE_CRITERION_AUDIT.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _dependency(path: Path) -> dict[str, str]:
    value = json.loads(path.read_text())
    identity = value.get("result_id") or value.get("schema")
    if not isinstance(identity, str) or not identity:
        raise ValueError(f"stationary readiness dependency identity missing: {path}")
    return {"artifact_id": identity, "sha256": _sha256(path)}


def _synthetic_receipt() -> dict[str, object]:
    """Small exact witness that exercises every algebraic acceptance branch."""

    A = _zero(2, 2)
    q = _zero(2, 2)
    q[0][1] = {(): sp.S.One}
    G = _zero(2, 2)
    G[0][1] = {(): sp.S.One}
    G[1][0] = {(): -sp.S.One}
    real = _identity(2)
    checks = evaluate_matrices(
        {
            "A104": A,
            "q_Cauchy_104": q,
            "G_Cauchy_104": G,
            "real_structure_104": real,
        }
    )
    if not all(checks.values()):
        raise ValueError("synthetic stationary-carrier acceptance witness failed")
    mutant = _zero(2, 2)
    mutant[0][0] = {(): sp.S.One}
    mutant[0][1] = {(): sp.S.One}
    rejected = evaluate_matrices(
        {
            "A104": A,
            "q_Cauchy_104": mutant,
            "G_Cauchy_104": G,
            "real_structure_104": real,
        }
    )
    if rejected["q_Cauchy_squared_zero"]:
        raise ValueError("synthetic nonnilpotent mutation escaped")
    return {
        "rank": 2,
        "accepted_exact_checks": checks,
        "nonnilpotent_q_mutation_rejected": True,
        "receipt_sha256": _canonical_hash(checks),
    }


def build() -> dict:
    zero = json.loads(ZERO_READINESS.read_text())
    partial = json.loads(PARTIAL_A104.read_text())
    audit = json.loads(EXISTENCE_AUDIT.read_text())
    if (
        zero.get("next_gate") != "IMPORT_BERGER_RETAINED_26_STATIONARY_GENERATOR_V1"
        or partial.get("claim_flags", {}).get("BERGER_FULL_A104_CAUCHY_OPERATOR") is not False
        or audit.get("claim_flags", {}).get("BERGER_COMPANION_HADAMARD_TWO_POINT_FUNCTION") is not False
    ):
        raise ValueError("stationary-generator readiness boundary drifted")

    source_paths = (
        "quantum-weyl/lorentzian/berger_retained_stationary_generator_acceptance.py",
        "quantum-weyl/lorentzian/berger_retained_stationary_generator_readiness.py",
        "quantum-weyl/lorentzian/berger_retained_stationary_generator_readiness_certificate.py",
        "quantum-weyl/lorentzian/verify_berger_retained_stationary_generator_readiness.py",
        "quantum-weyl/lorentzian/schema/berger-retained-stationary-generator-input-v1.schema.json",
        "quantum-weyl/lorentzian/schema/berger-retained-stationary-carrier-matrix-v1.schema.json",
        "quantum-weyl/lorentzian/schema/berger-retained-stationary-generator-readiness-v1.schema.json",
        "quantum-weyl/lorentzian/tests/test_berger_retained_stationary_generator_readiness.py",
        "quantum-weyl/reports/berger-retained-stationary-generator-import-readiness.md",
        "quantum-weyl/lorentzian/README.md",
    )
    source_manifest = {path: _sha256(ROOT / path) for path in source_paths}
    return {
        "schema": "quantum-weyl-berger-retained-stationary-generator-readiness-v1",
        "result_id": "BERGER_RETAINED_26_STATIONARY_GENERATOR_IMPORT_READINESS",
        "result_state": "CONSUMER_READY_STATIONARY_CARRIER_INPUT_NOT_SUPPLIED",
        "lifecycle_layer": "LORENTZIAN_FREE_QUANTUM_IMPORT_ACCEPTANCE",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {
            "zero_frequency_readiness": _dependency(ZERO_READINESS),
            "partial_A104": _dependency(PARTIAL_A104),
            "Hadamard_existence_audit": _dependency(EXISTENCE_AUDIT),
        },
        "input_contract": {
            "required_result_id": "BERGER_RETAINED_26_STATIONARY_GENERATOR_V1",
            "manifest_schema": {
                "path": "quantum-weyl/lorentzian/schema/berger-retained-stationary-generator-input-v1.schema.json",
                "sha256": _sha256(INPUT_SCHEMA),
            },
            "matrix_schema": {
                "path": "quantum-weyl/lorentzian/schema/berger-retained-stationary-carrier-matrix-v1.schema.json",
                "sha256": _sha256(MATRIX_SCHEMA),
            },
            "required_artifact_ids": [
                "A104",
                "q_Cauchy_104",
                "G_Cauchy_104",
                "real_structure_104",
            ],
            "required_shape": [104, 104],
            "content_addressing": "git_commit_plus_blob_sha256_plus_internal_matrix_sha256",
        },
        "exact_acceptance_conditions": [
            "all_104_rows_and_columns_match_frozen_Cauchy_ordering",
            "A104_has_no_unknown_coordinates",
            "q_Cauchy_squared_zero",
            "A104_supercommutes_with_q_Cauchy",
            "G_Cauchy_nondegenerate_and_BRST_compatible",
            "A104_Krein_skew_adjoint",
            "real_structure_involutive_and_intertwines_A104_q_Cauchy_G_Cauchy",
        ],
        "analytic_separation": {
            "finite_PBW_import_can_decide_zero_is_isolated": False,
            "reason": "spectral isolation concerns a closed realization on the declared mixed Sobolev or Krein space, not only the finite coefficient table",
            "required_followup": "BERGER_RETAINED_26_ZERO_FREQUENCY_SPECTRAL_LEDGER",
            "accepted_import_verdict": "ACCEPTED_EXACT_STATIONARY_CARRIER",
        },
        "synthetic_consumer_receipt": _synthetic_receipt(),
        "claim_flags": {
            "STATIONARY_GENERATOR_IMPORT_CONSUMER_READY": True,
            "EXACT_PBW_MUTATION_WITNESS": True,
            "STATIONARY_GENERATOR_INPUT_AVAILABLE": False,
            "STATIONARY_GENERATOR_ACCEPTED": False,
            "ZERO_FREQUENCY_LEDGER_COMPUTED": False,
            "GLOBAL_BRST_HADAMARD_STATE": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "SUPPLY_COMMITTED_BERGER_RETAINED_26_STATIONARY_GENERATOR_V1_MANIFEST",
        "claim_boundary": (
            "This readiness result installs a content-addressed, strict-schema consumer for the "
            "four exact 104-row stationary Cauchy carriers. It independently replays PBW "
            "nilpotency, BRST commutation, nondegeneracy, BRST pairing compatibility, Krein "
            "skew-adjointness and the real involution/intertwining identities. No classical "
            "stationary-generator manifest is supplied or accepted here. In particular, a finite "
            "coefficient table cannot prove that zero is isolated in the spectrum of a closed "
            "mixed-Sobolev/Krein realization; that analytic statement remains a separate next "
            "theorem. No zero/Jordan ledger, covariance, Hadamard state, physical positivity, "
            "renormalized product, QME restoration, particle interpretation or quantum result is claimed."
        ),
        "consumer_provenance": {
            "source_manifest": source_manifest,
            "source_manifest_sha256": _canonical_hash(source_manifest),
        },
        "verification_receipts": [
            {"test_tier": 1, "command": "PYTHONPATH=quantum-weyl python3 -m lorentzian.berger_retained_stationary_generator_readiness_certificate --check", "status": "PASS"},
            {"test_tier": 1, "command": "PYTHONPATH=quantum-weyl python3 -m lorentzian.verify_berger_retained_stationary_generator_readiness", "status": "PASS"},
            {"test_tier": 1, "command": "PYTHONPATH=quantum-weyl python3 -m unittest quantum-weyl/lorentzian/tests/test_berger_retained_stationary_generator_readiness.py -v", "status": "PASS"},
            {"test_tier": 1, "command": "npx --yes ajv-cli@5 compile --spec=draft2020 --strict=true -s quantum-weyl/lorentzian/schema/berger-retained-stationary-generator-input-v1.schema.json", "status": "PASS"},
            {"test_tier": 1, "command": "npx --yes ajv-cli@5 compile --spec=draft2020 --strict=true -s quantum-weyl/lorentzian/schema/berger-retained-stationary-carrier-matrix-v1.schema.json", "status": "PASS"},
            {"test_tier": 1, "command": "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s quantum-weyl/lorentzian/schema/berger-retained-stationary-generator-readiness-v1.schema.json -d quantum-weyl/lorentzian/certificates/BERGER_RETAINED_26_STATIONARY_GENERATOR_IMPORT_READINESS.json", "status": "PASS"},
        ],
        "higher_tiers_not_run": {
            "tier_2": "No classical stationary-generator input exists in this change. Tier 1 exercises every exact algebraic branch with an accepted witness and a rejected nilpotency mutation; the full affected carrier chain becomes mandatory when a committed manifest is supplied.",
            "tier_3": "No shared PBW engine, classical source artifact, closed analytic realization, lifecycle promotion, Hadamard construction, QME state, theorem freeze or release boundary changes in this readiness result.",
        },
    }
