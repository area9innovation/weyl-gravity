#!/usr/bin/env python3
"""Independent verifier of the relative QME non-definition."""

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
OUTPUT = HERE / "certificates/RELATIVE_EINSTEIN_WEYL_QME_DEFECT_NONDEFINITION.json"
SCHEMA = HERE / "schema/relative-einstein-weyl-qme-defect-nondefinition-v1.schema.json"
SOURCES = (
    "relative_einstein_weyl_qme_defect_nondefinition.py",
    "relative_einstein_weyl_qme_defect_nondefinition_certificate.py",
    "verify_relative_einstein_weyl_qme_defect_nondefinition.py",
    "schema/relative-einstein-weyl-qme-defect-nondefinition-v1.schema.json",
    "tests/test_relative_einstein_weyl_qme_defect_nondefinition.py",
    "../reports/relative-einstein-weyl-qme-defect-nondefinition.md",
)
REQUIRED_MISSING = {
    "MATCHED_EINSTEIN_MAXWELL_RENORMALIZED_QME_INSERTION",
    "MATCHED_WEYL_MAXWELL_RENORMALIZED_QME_INSERTION",
    "RENORMALIZED_RELATIVE_OBSERVABLE_PULLBACK",
    "ACTION_COMPATIBLE_CYCLIC_IOTA_PUSH",
    "RENORMALIZED_ANTIFIELD_MEASURE_ZERO_MODE_MAPS",
    "COMMON_TAUB_ZERO_DERIVED_SECTOR_AND_NULL_QUOTIENT",
}


def _load(path: Path) -> dict:
    return json.loads(path.read_text())


def verify() -> dict:
    value = _load(OUTPUT)
    errors = validate_instance(value, _load(SCHEMA))
    if errors:
        raise ValueError(f"relative QME schema failed: {errors}")

    if (
        value["relative_anomaly_complex"]["formal_complex"]
        != "Cone(iota_star:C_WM->C_EM)[-1]"
        or value["requested_subtraction"]["contravariant_map_available"]
        is not True
        or value["requested_subtraction"][
            "covariant_action_compatible_iota_push_available"
        ]
        is not False
        or value["coefficient_ledger"]["relative_vector"] != "UNDEFINED"
        or {
            row["object_id"] for row in value["missing_object_ledger"]
        }
        != REQUIRED_MISSING
        or value["verdict"]["relative_anomaly_class"] != "NOT_DEFINED"
    ):
        raise ValueError("independent relative non-definition replay failed")

    refs = value["dependency_refs"]
    for ref in refs.values():
        path = ROOT / ref["path"]
        source = _load(path)
        if (
            hashlib.sha256(path.read_bytes()).hexdigest() != ref["sha256"]
            or source.get("result_id") != ref["result_id"]
        ):
            raise ValueError("relative QME dependency drifted")
    readiness = _load(ROOT / refs["quantum_relative_readiness"]["path"])
    triangle = refs["relative_linear_triangle"]
    observable = refs["relative_observable_functor"]
    if (
        readiness["dependency_refs"]["relative_linear_triangle"]["sha256"]
        != triangle["sha256"]
        or readiness["dependency_refs"]["relative_observable_functor"]["sha256"]
        != observable["sha256"]
        or readiness["qme_and_transfer_gate"]["Einstein_QME"]
        != "NOT_COMPUTED"
        or readiness["framework_ledger"]["EUCLIDEAN_SPECTRAL"]["status"]
        != "NOT_COMPUTED_RELATIVELY"
    ):
        raise ValueError("independent readiness join failed")

    manifest = {
        path: hashlib.sha256((HERE / path).read_bytes()).hexdigest()
        for path in SOURCES
    }
    if value["provenance"]["source_manifest"] != manifest:
        raise ValueError("relative QME source manifest drifted")
    print("relative Einstein--Weyl QME independent verification: PASS")
    return value


if __name__ == "__main__":
    verify()
