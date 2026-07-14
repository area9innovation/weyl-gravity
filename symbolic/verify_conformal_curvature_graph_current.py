#!/usr/bin/env python3
"""Verify the exact graph-current theorem and its fail-closed boundary."""

from __future__ import annotations

from dataclasses import replace
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.curved_current.curvature_graph_current import (
    CurvatureGraphCurrentComparison,
)


CERTIFICATE = (
    ROOT
    / "covariant_completion"
    / "certificates"
    / "curved_curvature_graph_current.json"
)


def main() -> int:
    result = CurvatureGraphCurrentComparison.build()
    certificate = result.certificate(reverify=False)

    broken_inclusion = [row[:] for row in result.graph_inclusion]
    broken_inclusion[2][0] = broken_inclusion[2][0].zero()
    try:
        replace(result, graph_inclusion=broken_inclusion).verify(reverify_sdr=False)
    except AssertionError:
        graph_mutation_rejected = True
    else:
        graph_mutation_rejected = False

    broken_hessian = [row[:] for row in result.graph_hessian]
    broken_hessian[0][0] = broken_hessian[0][0].zero()
    try:
        replace(result, graph_hessian=broken_hessian).verify(reverify_sdr=False)
    except AssertionError:
        hessian_mutation_rejected = True
    else:
        hessian_mutation_rejected = False

    CERTIFICATE.write_text(
        json.dumps(certificate, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    exact = certificate["exact_identities"]
    support = certificate["support"]
    guards = {
        "graph_residual_vanishes_exactly": exact["R_I"] == "zero",
        "graph_Hessian_is_self_adjoint": (
            exact["graph_Hessian_adjoint_defect"] == "zero"
        ),
        "potential_pullback_is_exact": (
            exact["I_pullback_theta_parent_minus_theta_aux"] == "zero"
        ),
        "current_pullback_is_exact": (
            exact["I_pullback_omega_parent_minus_omega_aux"] == "zero"
        ),
        "compatible_improvement_is_local": (
            exact["improvement"] == "d beta+Q gamma with beta=0 and gamma=0"
        ),
        "support_local_in_all_categories": all(
            support[name] for name in ("compact", "spacelike_compact", "smooth_global")
        ),
        "no_nonlocal_inverse": not any(
            support[name]
            for name in ("inverse_Laplacian", "inverse_curl", "spectral_projector", "Green_operator")
        ),
        "PDE_and_Krein_pairings_not_conflated": not certificate[
            "pairing_separation"
        ]["identified_with_each_other"],
        "graph_subtheorem_certified": certificate[
            "curvature_graph_current_comparison"
        ],
        "complete_resolution_stays_fail_closed": not certificate[
            "prolonged_current_comparison"
        ],
        "action_level_blocker_is_explicit": len(
            certificate["action_level_blocker"]["missing"]
        ) == 3,
        "no_top_level_flag_promoted": certificate["flags_promoted_here"] == [],
        "broken_graph_rejected": graph_mutation_rejected,
        "broken_Hessian_rejected": hessian_mutation_rejected,
    }
    for name, passed in guards.items():
        print(f"[{'PASS' if passed else 'FAIL'}] {name}")
    print(f"certificate: {CERTIFICATE.relative_to(ROOT)}")
    print(
        "CURVATURE GRAPH CURRENT GUARDS: "
        f"{sum(guards.values())}/{len(guards)} PASS"
    )
    return 0 if all(guards.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
