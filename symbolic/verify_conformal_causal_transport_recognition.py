#!/usr/bin/env python3
"""Emit and mutation-test the conditional causal transport recognition."""

from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.green_homotopy.causal_transport import (
    CausalTransportRecognition,
    recognition_certificate_passes,
)


CERTIFICATE_DIR = ROOT / "covariant_completion" / "certificates"
OUTPUT = CERTIFICATE_DIR / "curved_causal_transport_recognition.json"


def _load(name: str) -> dict[str, object]:
    value = json.loads((CERTIFICATE_DIR / name).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"{name} is not a certificate object")
    return value


def _build(
    *,
    green: dict[str, object] | None = None,
    cutoff: dict[str, object] | None = None,
    residual: dict[str, object] | None = None,
    mapping: dict[str, object] | None = None,
) -> CausalTransportRecognition:
    return CausalTransportRecognition(
        green or _load("compact_to_global_quasi_isomorphism.json"),
        cutoff or _load("ckv_cutoff_sources.json"),
        residual or _load("residual_no_duplication.json"),
        mapping or _load("curved_curvature_mapping_cylinder_substitution.json"),
    )


def _rejects(**kwargs: dict[str, object]) -> bool:
    try:
        _build(**kwargs).verify()
    except AssertionError:
        return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()

    recognition = _build()
    certificate = recognition.certificate()
    if args.emit:
        OUTPUT.write_text(
            json.dumps(certificate, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print("wrote", OUTPUT.relative_to(ROOT))

    checks = {
        "conditional_recognition_exact": recognition_certificate_passes(certificate),
        "causal_chain_defect_zero": (
            certificate["causal_quasi_isomorphism"]["chain_defect"] == 0
        ),
        "cylinder_sc_is_smooth": certificate["cylinder_specialization"][
            "Gamma_sc_equals_Gamma_smooth"
        ],
        "fifteen_ghosts": (
            certificate["residual_endpoint_recovery"]["ghost_rank"] == 15
        ),
        "fifteen_duals": (
            certificate["residual_endpoint_recovery"]["dual_endpoint_rank"] == 15
        ),
        "curvature_copy_contractible": certificate["no_duplication"][
            "curvature_mapping_cylinder_contractible"
        ],
        "green_construction_not_claimed": certificate["promotion_boundary"][
            "does_not_construct_Green_operators"
        ],
        "SO42_not_claimed": not certificate["promotion_boundary"][
            "SO42_equivariant_transport_proved"
        ],
        "current_not_claimed": not certificate["promotion_boundary"][
            "prolonged_current_comparison_proved"
        ],
    }
    if args.guards:
        green = _load("compact_to_global_quasi_isomorphism.json")
        bad_green = deepcopy(green)
        bad_green["green_homotopies"]["identity"] = "unproved"
        checks["broken_green_homotopy_rejected"] = _rejects(green=bad_green)

        cutoff = _load("ckv_cutoff_sources.json")
        for key, value in (
            ("source_compact", False),
            ("rank", 14),
            ("causal_recovery", "unproved"),
        ):
            bad_cutoff = deepcopy(cutoff)
            bad_cutoff["ghost_classes"][key] = value
            checks[f"broken_cutoff_{key}_rejected"] = _rejects(cutoff=bad_cutoff)

        residual = _load("residual_no_duplication.json")
        bad_residual = deepcopy(residual)
        bad_residual["bfv_replacement"]["one_bfv_momentum_copy"] = 30
        checks["duplicated_bfv_copy_rejected"] = _rejects(residual=bad_residual)

        mapping = _load("curved_curvature_mapping_cylinder_substitution.json")
        for key, value in (
            ("P_I", "unproved"),
            ("I_P_minus_identity", "unproved"),
            ("BV_pairing_defect", 1),
        ):
            bad_mapping = deepcopy(mapping)
            bad_mapping["kernel"][key] = value
            checks[f"broken_mapping_{key}_rejected"] = _rejects(mapping=bad_mapping)

        output_mutations = (
            ("conditional_theorem", "recognition_exact", False),
            ("causal_quasi_isomorphism", "chain_defect", 1),
            ("causal_quasi_isomorphism", "right_cohomology_inverse", False),
            ("cylinder_specialization", "Gamma_sc_equals_Gamma_smooth", False),
            ("residual_endpoint_recovery", "dual_endpoint_rank", 14),
            ("no_duplication", "curvature_mapping_cylinder_contractible", False),
            (
                "promotion_boundary",
                "does_not_promote_without_three_Green_flags",
                False,
            ),
            ("promotion_boundary", "SO42_equivariant_transport_proved", True),
        )
        for section, key, value in output_mutations:
            broken = deepcopy(certificate)
            broken[section][key] = value
            checks[f"broken_output_{key}_not_recognized"] = not (
                recognition_certificate_passes(broken)
            )

    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise AssertionError("causal transport recognition failed: " + ", ".join(failed))
    if args.guards:
        print(
            "CAUSAL TRANSPORT RECOGNITION GUARDS: "
            f"{len(checks)}/{len(checks)} PASS"
        )
    print("CAUSAL TRANSPORT RECOGNITION: EXACT CONDITIONAL THEOREM")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
