#!/usr/bin/env python3
"""Generate the fail-closed quantum matter-selection atlas table."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
QROOT = HERE.parent
ROOT = QROOT.parent
SOURCE = (
    QROOT
    / "anomalies/certificates/MATTER_CONTENT_ANOMALY_CANCELLATION_LATTICE.json"
)
JOINT_SOURCE = (
    QROOT
    / "anomalies/certificates/"
    "MATTER_GAUGE_REPRESENTATION_JOINT_HEALTHY_EMPTY_BY_PROJECTION.json"
)
PANEITZ_SOURCE = (
    QROOT
    / "anomalies/certificates/PANEITZ_HIGHER_DERIVATIVE_ANOMALY_COLUMN.json"
)
OUTPUT = HERE / "matter-selection-atlas-table.json"
STATUSES = ["CERTIFIED", "OBSTRUCTED", "OPEN", "NOT_APPLICABLE", "NO_CERTIFIED_MAP"]


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> dict[str, Any]:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    joint = json.loads(JOINT_SOURCE.read_text(encoding="utf-8"))
    paneitz = json.loads(PANEITZ_SOURCE.read_text(encoding="utf-8"))
    if (
        source.get("result_id") != "MATTER_CONTENT_ANOMALY_CANCELLATION_LATTICE"
        or source["claim_flags"]["HEALTHY_NONNEGATIVE_CANCELLATION_EXISTS"]
        is not False
        or source["claim_flags"]["COMPENSATOR_IS_STRICT_CANCELLATION"] is not False
    ):
        raise ValueError("matter-selection source boundary drifted")
    if (
        joint.get("result_id")
        != "MATTER_GAUGE_REPRESENTATION_JOINT_HEALTHY_EMPTY_BY_PROJECTION"
        or joint["claim_flags"]["JOINT_HEALTHY_WEYL_GAUGE_SOLUTION_EXISTS"]
        is not False
        or joint["claim_flags"][
            "BOUNDED_REPRESENTATION_CLASSIFICATION_PERFORMED"
        ]
        is not False
    ):
        raise ValueError("joint matter/gauge projection boundary drifted")
    if (
        paneitz.get("result_id") != "PANEITZ_HIGHER_DERIVATIVE_ANOMALY_COLUMN"
        or paneitz["claim_flags"][
            "PANEITZ_FULL_FOUR_COORDINATE_COLUMN_VERIFIED"
        ]
        is not True
        or paneitz["claim_flags"]["HEALTHY_CANCELLATION_EXISTS"] is not False
        or paneitz["claim_flags"]["HIGHER_DERIVATIVE_GAUGE_COLUMN_VERIFIED"]
        is not False
    ):
        raise ValueError("Paneitz matter-selection boundary drifted")
    rows = []
    for candidate in (
        "real_conformal_scalar",
        "ordinary_homogeneous_conformal_compensator_scalar",
        "left_Weyl_fermion",
        "right_Weyl_fermion",
        "Dirac_fermion",
        "Abelian_gauge_vector",
    ):
        rows.append(
            {
                "candidate": candidate,
                "field_content_status": "CERTIFIED",
                "coefficient_status": "CERTIFIED",
                "strict_cancellation_status": "OBSTRUCTED",
                "healthy_standard_sign": True,
                "vector": source["matter_vectors_absolute_determinant"][candidate][
                    "vector"
                ],
                "physical_price": "added healthy spectator field content",
                "Lorentzian_QME_status": "NO_CERTIFIED_MAP",
            }
        )
    rows.extend(
        [
            {
                "candidate": "healthy_chiral_gauge_representation_assignment",
                "field_content_status": "OPEN",
                "coefficient_status": "CERTIFIED",
                "strict_cancellation_status": "OBSTRUCTED",
                "healthy_standard_sign": True,
                "vector": "projects to the certified empty nonnegative Weyl-matter cone",
                "physical_price": (
                    "no representation enumeration: gauge constraints only "
                    "shrink the already-empty joint domain"
                ),
                "Lorentzian_QME_status": "NO_CERTIFIED_MAP",
            },
            {
                "candidate": "Yang_Mills_adjoint_vector",
                "field_content_status": "CERTIFIED",
                "coefficient_status": "CERTIFIED",
                "strict_cancellation_status": "OBSTRUCTED",
                "healthy_standard_sign": True,
                "vector": "dim(ad G) times complete Abelian vector row",
                "physical_price": "added interacting gauge complex and group choice",
                "Lorentzian_QME_status": "NO_CERTIFIED_MAP",
            },
            {
                "candidate": "formal_negative_multiplicity",
                "field_content_status": "NOT_APPLICABLE",
                "coefficient_status": "CERTIFIED",
                "strict_cancellation_status": "CERTIFIED",
                "healthy_standard_sign": False,
                "vector": source["signed_determinant_lattice"][
                    "complete_parameterization"
                ],
                "physical_price": "inverse determinant or wrong-statistics power",
                "Lorentzian_QME_status": "NO_CERTIFIED_MAP",
            },
            {
                "candidate": "shifting_Wess_Zumino_compensator",
                "field_content_status": "CERTIFIED",
                "coefficient_status": "NOT_APPLICABLE",
                "strict_cancellation_status": "NOT_APPLICABLE",
                "healthy_standard_sign": False,
                "vector": "not a lattice column",
                "physical_price": "changes BV complex and local counterterm algebra",
                "Lorentzian_QME_status": "NO_CERTIFIED_MAP",
            },
            {
                "candidate": "real_Paneitz_scalar_P4",
                "field_content_status": "CERTIFIED",
                "coefficient_status": "CERTIFIED",
                "strict_cancellation_status": "OPEN",
                "healthy_standard_sign": False,
                "vector": paneitz["verified_column"]["coordinates"],
                "physical_price": (
                    "fourth-order opposite-residue/Krein-indefinite scalar"
                ),
                "Lorentzian_QME_status": "NO_CERTIFIED_MAP",
            },
            {
                "candidate": "standard_plus_Paneitz_projected_cancellation",
                "field_content_status": "CERTIFIED",
                "coefficient_status": "CERTIFIED",
                "strict_cancellation_status": "CERTIFIED",
                "healthy_standard_sign": False,
                "vector": paneitz["projected_anomaly_lattice"][
                    "first_solution_by_minimal_vector_count"
                ]["multiplicities"],
                "physical_price": (
                    "61 vectors plus 191 Paneitz scalars; cancellation is "
                    "only in the nontrivial quotient coordinates"
                ),
                "Lorentzian_QME_status": "NO_CERTIFIED_MAP",
            },
            {
                "candidate": "higher_derivative_conformal_gauge_field",
                "field_content_status": "OPEN",
                "coefficient_status": "NO_CERTIFIED_MAP",
                "strict_cancellation_status": "OPEN",
                "healthy_standard_sign": False,
                "vector": "NO_CERTIFIED_MAP",
                "physical_price": (
                    "complete off-shell BV, gauge-fixed elliptic, zero-mode "
                    "and two-route coefficient carrier required"
                ),
                "Lorentzian_QME_status": "NO_CERTIFIED_MAP",
            },
        ]
    )
    return {
        "schema": "quantum-weyl-matter-selection-atlas-table-v1",
        "generated_by": Path(__file__).relative_to(ROOT).as_posix(),
        "generated_by_sha256": _sha(Path(__file__)),
        "status_vocabulary": STATUSES,
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "source": {
            "path": SOURCE.relative_to(ROOT).as_posix(),
            "result_id": source["result_id"],
            "sha256": _sha(SOURCE),
        },
        "joint_gauge_selection_source": {
            "path": JOINT_SOURCE.relative_to(ROOT).as_posix(),
            "result_id": joint["result_id"],
            "sha256": _sha(JOINT_SOURCE),
        },
        "Paneitz_higher_derivative_source": {
            "path": PANEITZ_SOURCE.relative_to(ROOT).as_posix(),
            "result_id": paneitz["result_id"],
            "sha256": _sha(PANEITZ_SOURCE),
        },
        "strict_gravity_status": "OBSTRUCTED",
        "rows": rows,
        "claim_boundary": (
            "Selection by local Euclidean anomaly coordinates only. No row is "
            "a particle, Lorentzian state, phenomenology, GUT or unitarity claim."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    text = json.dumps(build(), indent=2, sort_keys=True) + "\n"
    if args.emit:
        OUTPUT.write_text(text, encoding="utf-8")
    if args.check and (
        not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != text
    ):
        raise SystemExit("stale matter-selection atlas table")
    print("quantum matter-selection atlas table: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
