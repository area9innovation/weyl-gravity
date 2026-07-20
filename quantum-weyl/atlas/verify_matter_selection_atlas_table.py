#!/usr/bin/env python3
"""Independent verifier for the matter-selection atlas table."""

from __future__ import annotations

import hashlib
import json

from .generate_matter_selection_atlas_table import (
    JOINT_SOURCE,
    OUTPUT,
    PANEITZ_SOURCE,
    ROOT,
    SOURCE,
    STATUSES,
)


def verify() -> dict:
    value = json.loads(OUTPUT.read_text(encoding="utf-8"))
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    joint = json.loads(JOINT_SOURCE.read_text(encoding="utf-8"))
    paneitz = json.loads(PANEITZ_SOURCE.read_text(encoding="utf-8"))
    if (
        value["status_vocabulary"] != STATUSES
        or value["source"]["sha256"]
        != hashlib.sha256(SOURCE.read_bytes()).hexdigest()
        or value["source"]["result_id"] != source["result_id"]
        or value["joint_gauge_selection_source"]["sha256"]
        != hashlib.sha256(JOINT_SOURCE.read_bytes()).hexdigest()
        or value["joint_gauge_selection_source"]["result_id"]
        != joint["result_id"]
        or value["Paneitz_higher_derivative_source"]["sha256"]
        != hashlib.sha256(PANEITZ_SOURCE.read_bytes()).hexdigest()
        or value["Paneitz_higher_derivative_source"]["result_id"]
        != paneitz["result_id"]
    ):
        raise ValueError("matter-selection atlas provenance failed")
    rows = {row["candidate"]: row for row in value["rows"]}
    healthy = [
        "real_conformal_scalar",
        "ordinary_homogeneous_conformal_compensator_scalar",
        "left_Weyl_fermion",
        "right_Weyl_fermion",
        "Dirac_fermion",
        "Abelian_gauge_vector",
        "healthy_chiral_gauge_representation_assignment",
        "Yang_Mills_adjoint_vector",
    ]
    if any(
        rows[name]["strict_cancellation_status"] != "OBSTRUCTED"
        or rows[name]["healthy_standard_sign"] is not True
        for name in healthy
    ):
        raise ValueError("healthy matter atlas promotion detected")
    if (
        rows["shifting_Wess_Zumino_compensator"][
            "strict_cancellation_status"
        ]
        != "NOT_APPLICABLE"
        or rows["real_Paneitz_scalar_P4"]["coefficient_status"]
        != "CERTIFIED"
        or rows["real_Paneitz_scalar_P4"]["healthy_standard_sign"] is not False
        or rows["standard_plus_Paneitz_projected_cancellation"][
            "strict_cancellation_status"
        ]
        != "CERTIFIED"
        or rows["standard_plus_Paneitz_projected_cancellation"][
            "healthy_standard_sign"
        ]
        is not False
        or rows["higher_derivative_conformal_gauge_field"]["coefficient_status"]
        != "NO_CERTIFIED_MAP"
        or any(
            row["Lorentzian_QME_status"] != "NO_CERTIFIED_MAP"
            for row in rows.values()
        )
    ):
        raise ValueError("matter-selection lifecycle boundary failed")
    generator = ROOT / value["generated_by"]
    if value["generated_by_sha256"] != hashlib.sha256(generator.read_bytes()).hexdigest():
        raise ValueError("matter-selection generator drifted")
    print("quantum matter-selection atlas independent verification: PASS")
    return value


if __name__ == "__main__":
    verify()
