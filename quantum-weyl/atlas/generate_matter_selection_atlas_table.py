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
OUTPUT = HERE / "matter-selection-atlas-table.json"
STATUSES = ["CERTIFIED", "OBSTRUCTED", "OPEN", "NOT_APPLICABLE", "NO_CERTIFIED_MAP"]


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> dict[str, Any]:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    if (
        source.get("result_id") != "MATTER_CONTENT_ANOMALY_CANCELLATION_LATTICE"
        or source["claim_flags"]["HEALTHY_NONNEGATIVE_CANCELLATION_EXISTS"]
        is not False
        or source["claim_flags"]["COMPENSATOR_IS_STRICT_CANCELLATION"] is not False
    ):
        raise ValueError("matter-selection source boundary drifted")
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
                "candidate": "higher_derivative_conformal_matter",
                "field_content_status": "OPEN",
                "coefficient_status": "NO_CERTIFIED_MAP",
                "strict_cancellation_status": "OPEN",
                "healthy_standard_sign": False,
                "vector": "NO_CERTIFIED_MAP",
                "physical_price": "new BV complex and kinetic-sign analysis required",
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
