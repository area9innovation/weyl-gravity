#!/usr/bin/env python3
"""Independent verifier for the boundary/corner first obstruction."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

try:
    from local_bv.schema_validation import validate_instance
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from local_bv.schema_validation import validate_instance


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUTPUT = HERE / "certificates/BOUNDARY_CORNER_ANOMALY_OPERATOR_DOMAIN_OBSTRUCTION.json"
SCHEMA = HERE / "schema/boundary-corner-anomaly-operator-domain-obstruction-v1.schema.json"
ELLIPTIC = (
    HERE.parent
    / "spectral/euclidean/certificates/"
    "REPOSITORY_EUCLIDEAN_ELLIPTIC_COMPLEX.json"
)
LOCAL = HERE / "certificates/LOCAL_ANOMALY_ANTIFIELD_COMPLETION_AUDIT.json"
SLAVNOV = (
    HERE.parent
    / "anomalies/certificates/"
    "REGULATED_REPOSITORY_BV_SLAVNOV_BREAKING.json"
)
SOURCES = (
    "boundary_corner_anomaly_operator_domain_obstruction.py",
    "boundary_corner_anomaly_operator_domain_obstruction_certificate.py",
    "verify_boundary_corner_anomaly_operator_domain_obstruction.py",
    "schema/boundary-corner-anomaly-operator-domain-obstruction-v1.schema.json",
    "tests/test_boundary_corner_anomaly_operator_domain_obstruction.py",
    "../reports/boundary-corner-anomaly-operator-domain-obstruction.md",
)
REQUIRED = {
    "boundary_field_ghost_antifield_dictionary",
    "boundary_BV_BFV_differential",
    "corner_edge_mode_complex",
    "full_BV_boundary_condition_projectors",
    "boundary_principal_symbol",
    "lopatinski_shapiro_or_equivalent_complementing_certificate",
    "boundary_corner_heat_kernel_or_resolvent",
    "differentiable_D_generator_with_boundary_charge",
}


def _load(path: Path) -> dict:
    return json.loads(path.read_text())


def verify() -> dict:
    value = _load(OUTPUT)
    errors = validate_instance(value, _load(SCHEMA))
    if errors:
        raise ValueError(f"boundary/corner schema failed: {errors}")

    sources = [_load(ELLIPTIC), _load(LOCAL), _load(SLAVNOV)]
    if (
        sources[0]["background"]["boundary_policy"] != "LOCAL_COMPACT_SUPPORT"
        or sources[1]["claim_flags"]["STRICT_LOCAL_EUCLIDEAN_QME_OBSTRUCTED"]
        is not True
        or {
            row["object_id"] for row in value["required_object_ledger"]
        }
        != REQUIRED
        or any(
            row["present_as_top_level_key"]
            for row in value["required_object_ledger"]
        )
    ):
        raise ValueError("independent missing-object replay failed")

    branch = value["boundary_gauge_branching"]
    if (
        branch["face_preserving_branch"]["closure_checks"][
            "BRST_preserves_normal_ghost_boundary_condition"
        ]
        is not True
        or branch["moving_boundary_branch"]["status"]
        != "NOT_PRESENT_IN_CLASSICAL_IMPORT"
        or value["disposition"]["bulk_QME_status"]
        != "UNCHANGED_STRICT_LOCAL_EUCLIDEAN_BULK_QME_OBSTRUCTED"
    ):
        raise ValueError("independent boundary-branch replay failed")

    for ref in value["dependency_refs"].values():
        path = ROOT / ref["path"]
        source = _load(path)
        if (
            hashlib.sha256(path.read_bytes()).hexdigest() != ref["sha256"]
            or source.get("result_id") != ref["result_id"]
        ):
            raise ValueError("boundary/corner dependency drifted")
    manifest = {
        path: hashlib.sha256((HERE / path).read_bytes()).hexdigest()
        for path in SOURCES
    }
    if value["provenance"]["source_manifest"] != manifest:
        raise ValueError("boundary/corner source manifest drifted")
    print("boundary/corner anomaly independent verification: PASS")
    return value


if __name__ == "__main__":
    verify()
