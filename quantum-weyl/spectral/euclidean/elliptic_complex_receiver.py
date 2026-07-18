"""Semantic receiver for a complete repository Euclidean elliptic BV complex."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from classical_import.classical_snapshot_compatibility_receiver import (
    validate_classical_snapshot_compatibility,
)
from spectral.euclidean.multiplicity_export_receiver import (
    validate_repository_multiplicity_export,
)


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SCHEMA = HERE / "schema/repository-euclidean-elliptic-complex-input-v1.schema.json"
FROZEN_IMPORT = ROOT / "quantum-weyl/classical_import/certificates/CLASSICAL_MINIMAL_BV_ANTIFIELD_IMPORT_V2.json"
RESULT_IDS = {
    "field_dictionary": "CLASSICAL_MINIMAL_BV_ANTIFIELD_IMPORT_V2",
    "multiplicity": "REPOSITORY_FULL_BV_MULTIPLICITY_LEDGER",
    "snapshot_compatibility": "REPOSITORY_CLASSICAL_SNAPSHOT_COMPATIBILITY",
    "action_normalization": "REPOSITORY_ROUND_S4_TT_HESSIAN_DICTIONARY_V1",
    "gauge_fixing": "REPOSITORY_EUCLIDEAN_GAUGE_FIXING",
    "formal_adjoint": "REPOSITORY_EUCLIDEAN_FORMAL_ADJOINT_COMPLEX",
}
PHYSICAL_SECTORS = (
    "minimal_conformal_deformation",
    "minimal_cotangent_formal_adjoint",
    "nonminimal_diffeomorphism_doublet",
    "nonminimal_weyl_doublet",
)
PHYSICAL_BLOCKS = (
    ("repository_physical_upper_Delta2perp4", 5, 2, Fraction(1, 2)),
    ("repository_scalar_ghost_Delta0minus4", 1, 2, Fraction(-12)),
    ("repository_physical_lower_Delta2perp2", 5, 2, Fraction(1)),
    ("repository_vector_ghost_Delta1perpminus3", 3, 2, Fraction(1)),
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _q(value: object, label: str) -> Fraction:
    if (
        not isinstance(value, dict)
        or set(value) != {"numerator", "denominator"}
        or not isinstance(value["numerator"], int)
        or not isinstance(value["denominator"], int)
        or value["denominator"] <= 0
    ):
        raise ValueError(f"{label} is not an exact rational")
    return Fraction(value["numerator"], value["denominator"])


def _matrix(value: dict[str, Any], label: str) -> list[list[Fraction]]:
    rows, columns = value["shape"]
    matrix = [[Fraction(0) for _ in range(columns)] for _ in range(rows)]
    seen: set[tuple[int, int]] = set()
    for index, entry in enumerate(value["entries"]):
        coordinate = (entry["row"], entry["column"])
        if not (0 <= coordinate[0] < rows and 0 <= coordinate[1] < columns):
            raise ValueError(f"{label} sparse coordinate is out of bounds")
        if coordinate in seen:
            raise ValueError(f"{label} has duplicate sparse coordinate")
        seen.add(coordinate)
        matrix[coordinate[0]][coordinate[1]] = _q(
            entry["coefficient"], f"{label}[{index}]"
        )
    return matrix


def _rank(matrix: list[list[Fraction]]) -> int:
    if not matrix:
        return 0
    work = [row[:] for row in matrix]
    rows, columns = len(work), len(work[0])
    rank = pivot_column = 0
    while rank < rows and pivot_column < columns:
        pivot = next(
            (row for row in range(rank, rows) if work[row][pivot_column]), None
        )
        if pivot is None:
            pivot_column += 1
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        scale = work[rank][pivot_column]
        work[rank] = [value / scale for value in work[rank]]
        for row in range(rows):
            if row != rank and work[row][pivot_column]:
                factor = work[row][pivot_column]
                work[row] = [
                    left - factor * right
                    for left, right in zip(work[row], work[rank])
                ]
        rank += 1
        pivot_column += 1
    return rank


def _multiply(
    left: list[list[Fraction]], right: list[list[Fraction]]
) -> list[list[Fraction]]:
    if not left or not right:
        return []
    return [
        [sum((left[i][k] * right[k][j] for k in range(len(right))), Fraction(0))
         for j in range(len(right[0]))]
        for i in range(len(left))
    ]


def _artifact(value: object, *, repository_root: Path, label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != {"format", "path", "sha256"}:
        raise ValueError(f"{label} artifact fields drifted")
    path = (repository_root / value["path"]).resolve()
    try:
        path.relative_to(repository_root.resolve())
    except ValueError as exc:
        raise ValueError(f"{label} artifact escapes repository") from exc
    if not path.is_file() or _sha256(path) != value["sha256"]:
        raise ValueError(f"{label} artifact hash mismatch")
    payload = json.loads(path.read_text())
    if not isinstance(payload, dict):
        raise ValueError(f"{label} artifact is not a JSON object")
    return payload


def validate_euclidean_elliptic_complex(
    payload: object,
    *,
    repository_root: Path = ROOT,
    allow_synthetic_fixture: bool = False,
) -> dict[str, Any]:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
    if not isinstance(payload, dict):
        raise ValueError("Euclidean elliptic complex payload is not an object")

    checks = payload["principal_symbol_exactness"]
    if not allow_synthetic_fixture and tuple(row["sector_id"] for row in checks) != PHYSICAL_SECTORS:
        raise ValueError("physical elliptic symbol-sector coverage drifted")
    for check in checks:
        incoming = _matrix(check["incoming_symbol"], f"{check['sector_id']}.incoming")
        outgoing = _matrix(check["outgoing_symbol"], f"{check['sector_id']}.outgoing")
        if (
            len(incoming) != check["middle_dimension"]
            or (incoming and len(incoming[0]) != check["domain_dimension"])
            or len(outgoing) != check["codomain_dimension"]
            or (outgoing and len(outgoing[0]) != check["middle_dimension"])
        ):
            raise ValueError("elliptic symbol dimension ledger drifted")
        product = _multiply(outgoing, incoming)
        incoming_rank = _rank(incoming)
        outgoing_rank = _rank(outgoing)
        if any(value for row in product for value in row):
            raise ValueError("elliptic symbol composition is nonzero")
        if (
            incoming_rank != check["incoming_rank"]
            or outgoing_rank != check["outgoing_rank"]
            or check["kernel_outgoing_dimension"]
            != check["middle_dimension"] - outgoing_rank
            or incoming_rank != check["kernel_outgoing_dimension"]
            or check["exact_at_middle"] is not True
        ):
            raise ValueError("elliptic symbol exactness rank identity drifted")

    blocks = payload["gauge_fixed_kinetic_blocks"]
    if not allow_synthetic_fixture:
        observed_blocks = tuple(
            (
                row["block_id"], row["bundle_rank"], row["differential_order"],
                _q(row["principal_scalar"], row["block_id"]),
            )
            for row in blocks
        )
        if observed_blocks != PHYSICAL_BLOCKS:
            raise ValueError("physical gauge-fixed kinetic-block coverage drifted")
    for block in blocks:
        if not _q(block["principal_scalar"], block["block_id"]):
            raise ValueError("gauge-fixed kinetic block has zero principal scalar")
        if block["elliptic"] is not True:
            raise ValueError("gauge-fixed kinetic block is not elliptic")

    artifacts = {
        role: _artifact(value, repository_root=repository_root, label=role)
        for role, value in payload["proof_artifacts"].items()
    }
    if not allow_synthetic_fixture:
        for role, expected in RESULT_IDS.items():
            if artifacts[role].get("result_id") != expected:
                raise ValueError(f"elliptic-complex {role} proof role drifted")
        validate_repository_multiplicity_export(
            artifacts["multiplicity"],
            repository_root=repository_root,
            expected_classical_commit=payload["classical_commit"],
            expected_analytic_route="EUCLIDEAN_ELLIPTIC",
        )
        frozen = json.loads(FROZEN_IMPORT.read_text())
        validate_classical_snapshot_compatibility(
            artifacts["snapshot_compatibility"],
            repository_root=repository_root,
            expected_local_commit=frozen["classical_commit"],
            expected_local_hashes=frozen["independent_replay"]["canonical_hashes"],
            expected_analytic_commit=payload["classical_commit"],
        )

    proof_payload = {
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
    if payload["proof_sha256"] != _canonical_hash(proof_payload):
        raise ValueError("elliptic-complex proof digest drifted")
    return {
        "result_id": payload["result_id"],
        "classical_commit": payload["classical_commit"],
        "symbol_sector_count": len(checks),
        "kinetic_block_count": len(payload["gauge_fixed_kinetic_blocks"]),
        "status": "SEMANTIC_RECEIVER_ACCEPTED",
    }


def synthetic_payload(*, repository_root: Path = ROOT) -> dict[str, Any]:
    fixture_path = (
        repository_root
        / "quantum-weyl/spectral/euclidean/certificates/REPOSITORY_ROUND_S4_EULER_COEFFICIENT.json"
    )
    artifact = {
        "format": "JSON_PROOF",
        "path": str(fixture_path.relative_to(repository_root)),
        "sha256": _sha256(fixture_path),
    }
    value = {
        "schema": "quantum-weyl-repository-euclidean-elliptic-complex-input-v1",
        "result_id": "REPOSITORY_EUCLIDEAN_ELLIPTIC_COMPLEX",
        "result_state": "COMPLETE_GAUGE_FIXED_BV_PRINCIPAL_SYMBOL_SEQUENCE_EXACT_AND_ELLIPTIC",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "classical_commit": "0" * 40,
        "analytic_route": "EUCLIDEAN_ELLIPTIC",
        "background": {
            "geometry": "synthetic flat Euclidean receiver fixture",
            "dimension": 4,
            "signature": "EUCLIDEAN",
            "boundary_policy": "LOCAL_COMPACT_SUPPORT",
        },
        "formulation": "FOURTH_ORDER_METRIC",
        "cotangent_orbit_reduction": {
            "representative": "k=(1,0,0,0)",
            "group": "SO(4)",
            "all_nonzero_covectors_covered": True,
        },
        "principal_symbol_exactness": [
            {
                "sector_id": "fixture_middle",
                "domain_dimension": 1,
                "middle_dimension": 2,
                "codomain_dimension": 1,
                "incoming_symbol": {
                    "shape": [2, 1],
                    "entries": [
                        {"row": 0, "column": 0, "coefficient": {"numerator": 1, "denominator": 1}}
                    ],
                },
                "outgoing_symbol": {
                    "shape": [1, 2],
                    "entries": [
                        {"row": 0, "column": 1, "coefficient": {"numerator": 1, "denominator": 1}}
                    ],
                },
                "incoming_rank": 1,
                "outgoing_rank": 1,
                "kernel_outgoing_dimension": 1,
                "exact_at_middle": True,
            }
        ],
        "gauge_fixed_kinetic_blocks": [
            {
                "block_id": "fixture_scalar_biwave",
                "bundle_rank": 1,
                "differential_order": 4,
                "principal_scalar": {"numerator": 1, "denominator": 2},
                "elliptic": True,
            }
        ],
        "coverage": {
            "all_minimal_nonminimal_and_auxiliary_rows_accounted": True,
            "all_symbol_sectors_covered": True,
            "formal_adjoint_complex_verified": True,
            "gauge_fixed_operator_elliptic": True,
        },
        "proof_artifacts": {role: artifact for role in RESULT_IDS},
        "claim_flags": {
            "REPOSITORY_EUCLIDEAN_ELLIPTIC_COMPLEX_CERTIFIED": True,
            "FULL_BV_SYMBOL_EXACTNESS_CERTIFIED": True,
            "REGULATED_SLAVNOV_BREAKING_COMPUTED": False,
            "QME_DISPOSITION": False,
            "LORENTZIAN_CERTIFIED": False,
        },
        "claim_boundary": "Synthetic receiver fixture only. The exact two-step sequence and scalar biwave exercise sparse symbol, rank, ellipticity and proof-role mechanics but do not certify the Weyl-gravity operator.",
    }
    value["proof_sha256"] = _canonical_hash(
        {
            key: value[key]
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
    return value
