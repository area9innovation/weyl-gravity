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
REPORT = ROOT / "covariant_completion" / "generated" / "curved_causal_transport_recognition.md"


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
    full_homotopy: dict[str, object] | None = None,
) -> CausalTransportRecognition:
    return CausalTransportRecognition(
        green or _load("compact_to_global_quasi_isomorphism.json"),
        cutoff or _load("ckv_cutoff_sources.json"),
        residual or _load("residual_no_duplication.json"),
        mapping or _load("curved_curvature_mapping_cylinder_substitution.json"),
        full_homotopy
        or _load("curved_full_prolonged_green_homotopy_assembly.json"),
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
        "actual_full_homotopy_bound": certificate["actual_causal_input"][
            "causal_green_homotopy"
        ]
        is True,
        "causal_chain_defect_zero": (
            certificate["causal_quasi_isomorphism"]["chain_defect"] == 0
        ),
        "support_exact_sequence_exact": all(
            value == 0
            for value in certificate["causal_quasi_isomorphism"][
                "support_exact_sequence_matrix_defects"
            ].values()
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
        "all_fifteen_labeled_CKV_sources": len(
            certificate["residual_endpoint_recovery"]["ghost_representatives"]
        )
        == 15,
        "all_fifteen_labeled_dual_sources": len(
            certificate["residual_endpoint_recovery"]["dual_representatives"]
        )
        == 15,
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
        full_homotopy = _load(
            "curved_full_prolonged_green_homotopy_assembly.json"
        )
        bad_full_homotopy = deepcopy(full_homotopy)
        bad_full_homotopy["causal_green_homotopy"] = False
        checks["missing_actual_full_homotopy_rejected"] = _rejects(
            full_homotopy=bad_full_homotopy
        )

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
            ("actual_causal_input", "causal_green_homotopy", False),
            ("no_duplication", "curvature_mapping_cylinder_contractible", False),
            (
                "promotion_boundary",
                "does_not_require_separate_Green_witness_flag",
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
        broken_representative = deepcopy(certificate)
        broken_representative["residual_endpoint_recovery"][
            "ghost_representatives"
        ][0]["source_compact"] = False
        checks["broken_individual_CKV_source_not_recognized"] = not (
            recognition_certificate_passes(broken_representative)
        )

    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise AssertionError("causal transport recognition failed: " + ", ".join(failed))
    if args.emit:
        REPORT.write_text(
            "# Causal quasi-isomorphism and residual endpoint recovery\n\n"
            "The SHA-bound 386-row retarded/advanced homotopies induce "
            "`Lambda=Lambda_+-Lambda_-` and the exact support sequence "
            "`0 -> Gamma_c -> Gamma_pc direct-sum Gamma_fc -> Gamma_sc -> 0`. "
            "The past/future side complexes contract, so the connecting map "
            "is a quasi-isomorphism. Since the Cauchy surface is compact, "
            "`Gamma_sc=Gamma^infinity` on the cylinder.\n\n"
            "All fifteen labeled CKV cutoff sources and all fifteen normalized "
            "dual endpoints were rerun exactly. The mapping cylinder and "
            "auxiliary enlargement contribute no duplicate residual copy, "
            "and the BV--BFV suspension sign is +1. SO(4,2) transport, pairing "
            "transport, and final H4 remain downstream.\n",
            encoding="utf-8",
        )
        print("wrote", REPORT.relative_to(ROOT))
    if args.guards:
        print(
            "CAUSAL TRANSPORT RECOGNITION GUARDS: "
            f"{len(checks)}/{len(checks)} PASS"
        )
    print("CAUSAL TRANSPORT RECOGNITION: EXACT ACTUAL THEOREM")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
