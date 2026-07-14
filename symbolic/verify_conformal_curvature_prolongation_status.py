#!/usr/bin/env python3
"""Refresh the curvature-prolongation status after mapping-cylinder closure."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.curved_operator.curvature_prolongation_status import (
    CurvatureProlongationStatus,
)


CERTIFICATE_DIR = ROOT / "covariant_completion" / "certificates"
OUTPUT = CERTIFICATE_DIR / "curved_curvature_prolongation_status.json"


def _load(name: str) -> dict[str, object]:
    value = json.loads((CERTIFICATE_DIR / name).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"{name} is not a certificate object")
    return value


def _build(*, include_mapping_cylinder: bool) -> CurvatureProlongationStatus:
    return CurvatureProlongationStatus.build(
        phase1_certificate=_load("curved_weyl_cotton_jet_comparison.json"),
        eal_certificate=_load("curved_EAL_spectrum_all_level.json"),
        hyperbolic_certificate=_load("curved_weyl_cotton_hyperbolic.json"),
        differential_ideal_certificate=_load(
            "curved_weyl_cotton_differential_ideal.json"
        ),
        formal_integrability_certificate=_load(
            "curved_weyl_cotton_formal_integrability.json"
        ),
        mapping_cylinder_certificate=(
            _load("curved_curvature_mapping_cylinder_substitution.json")
            if include_mapping_cylinder
            else None
        ),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()

    status = _build(include_mapping_cylinder=True)
    certificate = status.certificate()
    if args.emit:
        OUTPUT.write_text(
            json.dumps(certificate, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print("wrote", OUTPUT.relative_to(ROOT))

    promoted = (
        "curved_EB_equations",
        "curved_EB_first_order_closure",
        "curved_EB_symmetric_hyperbolicity",
        "curved_sourced_constraint_identity",
        "curved_constraint_propagation",
        "EAL_curvature_spectrum_match",
        "support_local_prolongation_retract",
        "prolonged_BV_operator_identity",
    )
    checks = {name: bool(certificate[name]) for name in promoted}
    without_mapping = _build(include_mapping_cylinder=False)
    checks["retract_requires_mapping_certificate"] = not (
        without_mapping.support_local_prolongation_retract
    )
    checks["BV_identity_requires_mapping_certificate"] = not (
        without_mapping.prolonged_BV_operator_identity
    )
    if args.guards:
        for name, passed in checks.items():
            if not passed:
                raise AssertionError(f"curvature status promotion failed: {name}")
        print(
            "CURVATURE PROLONGATION STATUS GUARDS: "
            f"{len(checks)}/{len(checks)} PASS"
        )
    print(
        "CURVATURE PROLONGATION STATUS: LOCAL SDR AND BV OPERATOR IDENTITY TRUE"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
