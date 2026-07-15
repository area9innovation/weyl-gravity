"""Canonical sparse export of the compensated flat minimal BV operators.

The source theorem constructs the operators.  This module serializes their
actual entries, rather than only their fingerprints, so a consumer can audit
the chain identities without importing the constructor.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp

from bridge.einstein_sector import compensated_quadratic_minimal_bv as source


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "bridge/certificates/compensated_minimal_bv_operator_export.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/compensated_minimal_bv_operator_export.schema.json"
SOURCE_CERTIFICATE = ROOT / "bridge/certificates/compensated_quadratic_minimal_bv.json"


class OperatorExportError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise OperatorExportError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _record(matrix: sp.MatrixBase) -> dict[str, Any]:
    entries = [
        [row, column, str(sp.factor(value))]
        for (row, column), value in sorted(sp.SparseMatrix(matrix).todok().items())
    ]
    body = {"shape": list(matrix.shape), "entries": entries}
    digest = hashlib.sha256(
        json.dumps(body, separators=(",", ":"), sort_keys=True).encode("utf-8")
    ).hexdigest()
    return {**body, "sha256": digest}


def build_export() -> dict[str, Any]:
    data = source._build_exact_data()
    matrices = {
        name: _record(data[key])
        for name, key in {
            "metric_operator": "metric_operator",
            "field_map": "field_map",
            "original_action_hessian": "original_action_hessian",
            "field_gram": "field_gram",
            "ghost_gram": "ghost_gram",
            "gauge": "gauge",
            "hessian": "hessian",
            "noether": "noether",
            "q": "q",
            "pairing": "pairing",
            "inclusion": "inclusion",
            "pi_cl": "projection",
            "homotopy": "homotopy",
            "reduced_q": "reduced_q",
            "reduced_pairing": "reduced_pairing",
        }.items()
    }
    for name, digest in data["digests"].items():
        _require(matrices[name]["sha256"] == digest, f"source fingerprint changed: {name}")

    payload = {
        "schema": "compensated-minimal-bv-operator-export-v1",
        "schema_path": "bridge/einstein_sector/schema/compensated_minimal_bv_operator_export.schema.json",
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "COMPENSATED_MINIMAL_BV_CANONICAL_OPERATOR_EXPORT",
        "result_state": "CANONICAL_OPERATOR_SNAPSHOT_EXPORTED_INDEPENDENT_VERIFICATION_REQUIRED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "provenance": {
            "input_base_commit": "25364fb760ed869f193983eb179ad3b120b52557",
            "generator_path": "bridge/einstein_sector/compensated_minimal_bv_operator_export.py",
            "generator_sha256": _sha256(Path(__file__)),
        },
        "inputs": {
            "minimal_bv_certificate": {
                "path": str(SOURCE_CERTIFICATE.relative_to(ROOT)),
                "sha256": _sha256(SOURCE_CERTIFICATE),
            },
            "minimal_bv_generator": {
                "path": str(Path(source.__file__).resolve().relative_to(ROOT)),
                "sha256": _sha256(Path(source.__file__).resolve()),
            },
        },
        "coefficient_ring": "Q(c1,alpha,v,v^-1)[p0,p1,p2,p3]",
        "symbols": ["p0", "p1", "p2", "p3", "c1", "alpha", "v"],
        "formal_adjoint": {"p0": "-p0", "p1": "-p1", "p2": "-p2", "p3": "-p3"},
        "coordinate_order": [
            {"name": "ghosts", "start": 0, "stop": 5, "degree": -1},
            {"name": "fields", "start": 5, "stop": 16, "degree": 0},
            {"name": "antifields", "start": 16, "stop": 27, "degree": 1},
            {"name": "ghost_antifields", "start": 27, "stop": 32, "degree": 2},
        ],
        "matrices": matrices,
        "verdict": "ACTUAL_SPARSE_OPERATORS_EXPORTED_WITH_CANONICAL_CONTENT_HASHES",
        "claim_flags": {
            "actual_sparse_entries_exported": True,
            "source_fingerprints_reproduced": True,
            "independent_consumer_verification_in_this_artifact": False,
            "characteristic_cohomology_in_this_artifact": False,
            "physical_symplectic_pairing_in_this_artifact": False,
            "lorentzian_causal_claim": False,
            "quantum_claim": False,
        },
        "scope_guards": [
            "this is a canonical LOCAL-ALGEBRAIC operator snapshot, not a physical state space",
            "the odd BV pairing is not the physical Cauchy or radiative symplectic form",
            "independent verification is a separate certificate and lifecycle gate",
        ],
        "verification_command": "python3 -m bridge.einstein_sector.compensated_minimal_bv_operator_export --verify bridge/certificates/compensated_minimal_bv_operator_export.json",
    }
    return payload


def verify_export(path: Path = DEFAULT_OUTPUT) -> None:
    actual = json.loads(path.read_text(encoding="utf-8"))
    _require(actual == build_export(), f"operator export is stale or altered: {path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    if args.write:
        DEFAULT_OUTPUT.write_text(json.dumps(build_export(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.verify:
        verify_export(args.verify)
    if not args.write and not args.verify:
        parser.error("one of --write or --verify is required")


if __name__ == "__main__":
    main()
