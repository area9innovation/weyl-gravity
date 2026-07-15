#!/usr/bin/env python3
"""Verify the principal rank-14/Weyl--Cotton symbol comparison."""

from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.curved_operator.rank14_weyl_cotton_symbol_audit import (  # noqa: E402
    Rank14WeylCottonSymbolAudit,
)


OUTPUT = (
    ROOT
    / "covariant_completion"
    / "certificates"
    / "curved_rank14_weyl_cotton_symbol_audit.json"
)
HELICITY = (
    ROOT / "covariant_completion" / "certificates" / "curved_helicity_two_channel.json"
)
CHAIN = (
    ROOT
    / "covariant_completion"
    / "certificates"
    / "curved_curvature_auxiliary_chain_map.json"
)
RANK14 = (
    ROOT
    / "covariant_completion"
    / "certificates"
    / "curved_expanded_relative_witness_rank14_curvature_presentation.json"
)


def _rejects_full_equivalence(certificate: dict[str, object]) -> bool:
    candidate = deepcopy(certificate)
    candidate["image_kernel_comparison"]["image_equals_compatible_kernel"] = True
    comparison = candidate["image_kernel_comparison"]
    return not (
        comparison["image_equals_compatible_kernel"]
        and comparison["generic_image_rank"]
        == comparison["generic_compatible_rank"]
    )


def _rejects_false_compatibility(certificate: dict[str, object]) -> bool:
    candidate = deepcopy(certificate)
    candidate["image_kernel_comparison"]["image_is_contained_in_compatible_kernel"] = True
    claimed = candidate["image_kernel_comparison"][
        "image_is_contained_in_compatible_kernel"
    ]
    observed = candidate["causal_strata"]["generic_timelike_(2,1,0,0)"][
        "compatibility_curvature_defect_rank"
    ]
    return not (claimed and observed == 0)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--guards", action="store_true")
    parser.add_argument("--claim-equivalence", action="store_true")
    args = parser.parse_args()
    if args.claim_equivalence:
        raise SystemExit(
            "REFUSED: rank(C1,div C1)=5 while the generic compatible-source "
            "kernel has rank 12"
        )

    audit = Rank14WeylCottonSymbolAudit.build()
    helicity = json.loads(HELICITY.read_text(encoding="utf-8"))
    chain = json.loads(CHAIN.read_text(encoding="utf-8"))
    rank14 = json.loads(RANK14.read_text(encoding="utf-8"))
    certificate = audit.certificate(
        helicity_certificate=helicity,
        chain_certificate=chain,
        rank14_certificate=rank14,
    )
    if args.emit:
        OUTPUT.write_text(
            json.dumps(certificate, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print("wrote", OUTPUT.relative_to(ROOT))

    domain = certificate["rank14_domain"]
    descended = certificate["descended_curvature_map"]
    compatible = certificate["compatible_source_symbol"]
    comparison = certificate["image_kernel_comparison"]
    decision = certificate["decision"]
    checks = {
        "rank14_domain": domain["generic_rank"] == 14
        and domain["gauge_annihilation_defect"] == 0,
        "rank5_curvature_image": descended["generic_rank"] == 5
        and descended["generic_kernel_rank_on_F14"] == 9,
        "fraction_field_descent": descended["fraction_field_factor_defect"] == 0,
        "local_temporal_prolongation": descended["local_factor_defect"] == 0
        and not descended["unprolonged_factor_is_polynomial"],
        "compatible_kernel_rank12": compatible["generic_row_rank"] == 14
        and compatible["generic_kernel_rank"] == 12,
        "syzygy_search_stopped_after_failed_containment": not compatible[
            "polynomial_syzygy_basis_emitted"
        ],
        "off_shell_constraint_defect": comparison[
            "K_weighted_R_generic_defect_rank"
        ] == 3
        and not comparison["image_is_contained_in_compatible_kernel"],
        "common_core_rank2": comparison["generic_common_core_rank"] == 2
        and comparison["generic_compatible_mod_common_core_rank"] == 10,
        "equation_cone_exact": certificate["exact_chain_square_replacement"][
            "equation_cone"
        ]["exact"],
        "equivalence_rejected": not decision[
            "strict_differential_equivalence_SR_equals_1_possible_for_this_R"
        ],
        "no_overpromotion": not decision["full_rank14_green_problem_solved"]
        and not certificate["status_flags_promoted"],
    }
    if args.guards:
        checks["false_full_equivalence_rejected"] = _rejects_full_equivalence(
            certificate
        )
        checks["false_raw_compatibility_rejected"] = _rejects_false_compatibility(
            certificate
        )

    for name, passed in checks.items():
        print(f"[{'PASS' if passed else 'FAIL'}] {name}")
    print(
        "RANK-14/WEYL-COTTON SYMBOL AUDIT: "
        f"{sum(checks.values())}/{len(checks)} PASS"
    )
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
