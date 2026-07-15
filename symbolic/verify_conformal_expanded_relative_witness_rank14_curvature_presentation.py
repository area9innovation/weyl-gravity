#!/usr/bin/env python3
"""Verify the projector-free rank-14 curvature/Green presentation."""

from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.curved_operator.expanded_relative_witness_rank14_curvature_presentation import (  # noqa: E402
    ExpandedRelativeRank14CurvaturePresentation,
)


CERTIFICATES = ROOT / "covariant_completion" / "certificates"
RANK34 = CERTIFICATES / "curved_expanded_relative_witness_rank34_module.json"
HELICITY = CERTIFICATES / "curved_helicity_two_channel.json"
STATE_MAP = CERTIFICATES / "curved_curvature_auxiliary_chain_map.json"
OUTPUT = (
    CERTIFICATES
    / "curved_expanded_relative_witness_rank14_curvature_presentation.json"
)


def _load(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"certificate is not an object: {path}")
    return value


def _rejects(
    audit: ExpandedRelativeRank14CurvaturePresentation,
    rank34: dict[str, object],
    helicity: dict[str, object],
    state_map: dict[str, object],
) -> bool:
    try:
        audit.certificate(
            rank34_certificate=rank34,
            helicity_certificate=helicity,
            state_map_certificate=state_map,
            reverify=False,
        )
    except AssertionError:
        return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--guards", action="store_true")
    parser.add_argument("--claim-full-green", action="store_true")
    args = parser.parse_args()
    if args.claim_full_green:
        raise SystemExit(
            "REFUSED: the curved lower-order L14, degree-minus-one V14, "
            "cotangent adjoint and all-row insertion are not certified"
        )

    rank34 = _load(RANK34)
    helicity = _load(HELICITY)
    state_map = _load(STATE_MAP)
    audit = ExpandedRelativeRank14CurvaturePresentation.build()
    certificate = audit.certificate(
        rank34_certificate=rank34,
        helicity_certificate=helicity,
        state_map_certificate=state_map,
        reverify=False,
    )
    if args.emit:
        OUTPUT.write_text(
            json.dumps(certificate, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print("wrote", OUTPUT.relative_to(ROOT))

    quotient = certificate["projector_free_quotient"]
    induced = certificate["induced_operator"]
    filtration = certificate["rank7_local_filtration"]
    green = certificate["presented_quotient_green_algebra"]
    physical = certificate["physical_biwave_restriction"]
    curvature = certificate["curvature_presentation"]
    direct = certificate["direct_Weyl_Cotton_retraction_obstruction"]
    lift = certificate["compatible_source_lifting"]
    boundary = certificate["precise_boundary"]
    checks = {
        "quotient_rank14": quotient["generic_rank"] == 14
        and quotient["P14_B_vector_defect"] == 0,
        "projector_free": not quotient["transverse_projector_used"]
        and not quotient["helicity_projector_used"],
        "induced_identity": induced["identity_defect"] == 0
        and induced["polynomial_coefficients"],
        "triangular_biwave_incidence": induced["block_form"]
        == "[[L7,0],[R7,L7]]",
        "rank5_wave": filtration["STF_submodule_invariant"]
        and filtration["STF_operator"] == "(Delta-partial_t^2) I5",
        "rank4_temporal": filtration["zero_speed_algebraic_multiplicity"] == 4
        and filtration["scalar_determinant"] == "2 partial_t^4",
        "rank10_light": filtration["light_sector_algebraic_multiplicity"] == 10,
        "rank7_green": green["rank7_left_defect"] == 0
        and green["rank7_right_defect"] == 0,
        "rank14_green_algebra": green["rank14_left_defect"] == 0
        and green["rank14_right_defect"] == 0,
        "physical_biwave": physical["identity_defect"] == 0
        and physical["Weyl_helicity_isomorphism"],
        "local_C1_prolongation": curvature[
            "local_prolonged_identity_defect"
        ] == 0,
        "descended_R_rank_ledger": curvature[
            "descended_R_ranks_generic_timelike_spacelike_null"
        ] == [5, 5, 5, 5],
        "direct_SR_rank_obstruction": not direct[
            "direct_SR_equals_identity_possible"
        ]
        and direct["rank_obstruction"] == "5 < 14"
        and not direct["SDR_constructed_here"],
        "causal_compatible_lift": lift["P14_R_plus_minus"] == "identity"
        and lift["left_defect_lies_in_certified_gauge_submodule"]
        and not lift["spatial_or_elliptic_inverse_used"],
        "full_boundary_visible": boundary["principal_module_only"]
        and not boundary["curved_lower_order_L14_derived"]
        and not boundary["all_BV_rows_inserted"],
        "no_overpromotion": not certificate["prolonged_green_witness"]
        and not certificate["curvature_causal_green_operators"]
        and not certificate["causal_green_homotopy"],
        "scoped_atomic_flags_promoted": certificate["status_flags_promoted"]
        == certificate["warranted_atomic_flags"]
        and all(certificate["warranted_atomic_flags"].values()),
    }
    if args.guards:
        bad_rank34 = deepcopy(rank34)
        bad_rank34["local_differential_submodule"]["intertwining_defect"] = 1
        bad_helicity = deepcopy(helicity)
        bad_helicity["linearized_Weyl_symbol"]["is_isomorphism"] = False
        bad_state = deepcopy(state_map)
        bad_state["first_chain_relation_exact"] = False
        checks.update(
            {
                "broken_rank34_input_rejected": _rejects(
                    audit, bad_rank34, helicity, state_map
                ),
                "broken_helicity_input_rejected": _rejects(
                    audit, rank34, bad_helicity, state_map
                ),
                "broken_state_map_rejected": _rejects(
                    audit, rank34, helicity, bad_state
                ),
            }
        )

    for name, passed in checks.items():
        print(f"[{'PASS' if passed else 'FAIL'}] {name}")
    print(f"RANK-14 CURVATURE PRESENTATION: {sum(checks.values())}/{len(checks)} PASS")
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
