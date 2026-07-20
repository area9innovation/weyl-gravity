#!/usr/bin/env python3
"""Independent replay of the retained C26 support-profile non-definition.

This verifier imports neither the producer nor its certificate emitter.  It
rechecks the decisive exports directly and rejects any promotion of an
undefined representative-dependent property.
"""

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
OUTPUT = (
    HERE
    / "certificates/BERGER_C26_BIKERNEL_SUPPORT_PROFILE_NONDEFINITION.json"
)
SCHEMA = (
    HERE
    / "schema/berger-c26-bikernel-support-profile-nondefinition-v1.schema.json"
)
DEPENDENCIES = {
    "ward_reduction": (
        HERE / "certificates/BERGER_RETAINED26_HADAMARD_WARD_REDUCTION.json"
    ),
    "ghost_identity_pair": (
        HERE / "certificates/BERGER_GHOST_IDENTITY_GLOBAL_HADAMARD_PAIR.json"
    ),
    "metric_endpoint_pair": (
        HERE
        / "certificates/"
        "BERGER_REGULAR_GRAPH_INTERTWINER_OBSTRUCTION_AND_ENDPOINT_DESCENT.json"
    ),
    "free_dilation_pair": (
        HERE
        / "certificates/BERGER_FREE_DILATION_KREIN_CCR_COVARIANCE.json"
    ),
    "classical_support_gate": (
        ROOT
        / "d_quotient_classical/certificates/"
        "BERGER_26_ROW_SMOOTH_BIKERNEL_HOMOTOPY_SUPPORT_GATE_V1.json"
    ),
}
SOURCE_PATHS = (
    "berger_c26_bikernel_support_profile_nondefinition.py",
    "berger_c26_bikernel_support_profile_nondefinition_certificate.py",
    "verify_berger_c26_bikernel_support_profile_nondefinition.py",
    "schema/berger-c26-bikernel-support-profile-nondefinition-v1.schema.json",
    "tests/test_berger_c26_bikernel_support_profile_nondefinition.py",
    "../reports/berger-c26-bikernel-support-profile-nondefinition.md",
)
UNDEFINED = "UNDEFINED_NO_NORMALIZED_SERIALIZED_H26_REPRESENTATIVE"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify() -> dict:
    value = _load(OUTPUT)
    errors = validate_instance(value, _load(SCHEMA))
    if errors:
        raise ValueError(f"C26 support schema failed: {errors}")

    inputs = {name: _load(path) for name, path in DEPENDENCIES.items()}
    for name, path in DEPENDENCIES.items():
        ref = value["dependency_refs"][name]
        if (
            ref["path"] != path.relative_to(ROOT).as_posix()
            or ref["result_id"] != inputs[name]["result_id"]
            or ref["sha256"] != _sha256(path)
        ):
            raise ValueError(f"dependency drift: {name}")

    ward = inputs["ward_reduction"]
    if (
        ward["candidate_status"]["Ward_defect_vanishes"] != "NOT_DECIDED"
        or not ward["candidate_status"]["Ward_defect_is_smooth"]
        or ward["candidate_status"]["retained_26_BRST_Hadamard"]
        or ward["ward_reduction"]["smooth_defect"]
        != "C26=[H26_plus,q26] is a smooth kernel"
    ):
        raise ValueError("independent Ward-boundary replay failed")

    ghost = inputs["ghost_identity_pair"]
    metric = inputs["metric_endpoint_pair"]
    free = inputs["free_dilation_pair"]
    formulas = {
        "ghost_identity": ghost["global_pair"]["kernel"],
        "metric_metric_adjoint": metric["direct_metric_endpoint_descent"][
            "kernel_pullback"
        ],
        "free_dilation_seed": free["covariance"]["distribution"],
    }
    blocks = {
        block["block_id"]: block
        for block in value["representation_audit"]["blocks"]
    }
    if set(blocks) != set(formulas):
        raise ValueError("endpoint block coverage drifted")
    for block_id, formula in formulas.items():
        block = blocks[block_id]
        if (
            block["declared_formula"] != formula
            or block["serialized_bikernel"]
            or block["stationary_mode_table"]
            or block["executable_distribution_evaluator"]
            or block["smooth_part_normalization_fixed"]
        ):
            raise ValueError("symbolic endpoint was promoted to serialized data")

    support = inputs["classical_support_gate"]
    if (
        support["C26_import_boundary"]["typed_need"]
        != "C26_BIKERNEL_SUPPORT_PROFILE_OR_SERIALIZED_SMOOTH_REMAINDER"
        or support["classification"][
            "C26_in_positive_extension_domain_certified"
        ]
        or not support["classification"][
            "full_smooth_factorized_extension_obstructed"
        ]
    ):
        raise ValueError("independent classical support replay failed")

    profile = value["support_profile"]
    undecided = (
        "x_past_compact",
        "x_future_compact",
        "x_time_compact",
        "y_past_compact",
        "y_future_compact",
        "y_time_compact",
        "stationary_harmonic_support",
        "pairing_null_on_closed_exact_pairs",
    )
    if any(profile[name] != UNDEFINED for name in undecided):
        raise ValueError("undefined support or pairing status was promoted")
    if (
        profile["full_smooth_class_membership"]
        != "CERTIFIED_BY_SMOOTHNESS"
        or profile["full_smooth_factorized_homotopy"]
        != "OBSTRUCTED_BY_CLASSICAL_CUTOFF_ESCAPE_THEOREM"
    ):
        raise ValueError("known smooth-class disposition drifted")

    flags = value["claim_flags"]
    if (
        not flags["C26_SMOOTH"]
        or flags["C26_SERIALIZED"]
        or flags["C26_X_SUPPORT_PROFILE_CERTIFIED"]
        or flags["C26_Y_SUPPORT_PROFILE_CERTIFIED"]
        or flags["C26_PAIRING_NULL_CERTIFIED"]
        or flags["NORMALIZED_H26_REPRESENTATIVE_SUPPLIED"]
        or flags["RETAINED_26_BRST_HADAMARD"]
        or flags["PHYSICAL_POSITIVITY_CERTIFIED"]
        or flags["LORENTZIAN_QME_RESTORED"]
        or flags["QUANTUM_CLAIM"]
    ):
        raise ValueError("claim flags crossed the non-definition boundary")

    manifest = {path: _sha256(HERE / path) for path in SOURCE_PATHS}
    if value["provenance"]["source_manifest"] != manifest:
        raise ValueError("source manifest drifted")
    return value


if __name__ == "__main__":
    verify()
    print("BERGER C26 independent support non-definition replay: PASS")
