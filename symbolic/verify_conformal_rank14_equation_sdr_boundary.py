#!/usr/bin/env python3
"""Verify the fail-closed rank-14 equation-SDR boundary certificate."""

from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.curved_operator.rank14_equation_sdr_boundary import (  # noqa: E402
    certificate_from_verified_inputs,
)


CERTIFICATES = ROOT / "covariant_completion" / "certificates"
OUTPUT = CERTIFICATES / "curved_rank14_equation_sdr_boundary.json"


def _load(name: str) -> dict[str, object]:
    with (CERTIFICATES / name).open(encoding="utf-8") as handle:
        return json.load(handle)


def _checks(certificate: dict[str, object]) -> dict[str, bool]:
    state = certificate["proposed_state_SDR_audit"]
    cone = certificate["correct_equation_complex"]
    closure = certificate["auxiliary_derived_closure"]
    relative = certificate["canonical_relative_cone"]
    typed = certificate["requested_AF_candidate_type_audit"]
    physical = certificate["null_physical_regression"]
    ledger = certificate["minimum_mapping_cone_ledger"]
    decision = certificate["decision"]
    return {
        "F14_to_U9": state["F14_rank"] == 14
        and state["R_rank"] == 5
        and state["U9_equals_kernel_R_rank"] == 9,
        "off_shell_defect": state["K_R_generic_defect_rank"] == 3
        and state["im_R_intersection_K12_rank"] == 2,
        "invalid_quotient_rejected": not state[
            "claimed_V7_equals_K12_mod_imR_is_defined"
        ]
        and state["strict_SR_state_retraction_rejected"],
        "correct_complex": cone["objects"]
        == ["U_WC[26]", "F_WC[26]+C_WC[14]", "I_WC[14]"]
        and cone["identity"] == "N_curv E_curv=0",
        "PBW_lower_order": cone["commuting_symbol_defect_nonzero"]
        and cone["unit_S3_PBW_correction_exact"]
        and cone["all_curvature_lower_order_terms_included"],
        "adjoints": cone["formal_adjoints_included"]
        and len(cone["equation_adjoint_sha256"]) == 64
        and len(cone["identity_adjoint_sha256"]) == 64,
        "chain_squares": closure["first_square_exact"]
        and closure["second_square_exact"],
        "canonical_relative_cone": relative["closure_exact"]
        and relative["support_local"]
        and not relative["requires_projector"],
        "typed_AF_formula": not typed["literally_typed"]
        and typed["corrected_pair_is_N_closed"]
        and not typed["A_F_alone_is_R_src_closed"]
        and not typed["candidate_T_rel_defined"],
        "physical_H2": physical["H2_rank"] == 2
        and physical["R_restricted_to_H2"] == "(1/4) I2"
        and physical["R_restricted_to_H2_invertible"],
        "minimal_ledger": ledger[
            "off_shell_constraint_directions_that_must_be_retained"
        ]
        == 3
        and ledger["generic_compatible_complement_after_true_common_core"] == 10
        and ledger["field_kernel_requiring_equation_homotopy_rank"] == 9,
        "cyclic_duals": ledger[
            "minimum_new_primal_rows_if_auxiliary_equation_rows_are_not_reused"
        ]
        == ledger["minimum_cyclic_dual_rows_in_that_case"]
        == 3,
        "no_overpromotion": not decision["rank14_equation_SDR_constructed"]
        and not decision["rank14_green_operators_constructed"]
        and certificate["status_flags_promoted"] == [],
        "fail_closed": certificate["fail_closed"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()

    certificate = certificate_from_verified_inputs(
        symbol_certificate=_load("curved_rank14_weyl_cotton_symbol_audit.json"),
        helicity_certificate=_load("curved_helicity_two_channel.json"),
        equation_chain_certificate=_load("curved_curvature_auxiliary_chain_map.json"),
        identity_chain_certificate=_load(
            "curved_curvature_identity_chain_map.json"
        ),
        cycle_gate_certificate=_load("curved_rank14_equation_cycle_gate.json"),
    )
    checks = _checks(certificate)
    if not all(checks.values()):
        raise AssertionError(
            "rank-14 equation SDR boundary failed: "
            + ", ".join(name for name, passed in checks.items() if not passed)
        )

    guards: dict[str, bool] = {}
    if args.guards:
        bad = deepcopy(certificate)
        bad["proposed_state_SDR_audit"][
            "claimed_V7_equals_K12_mod_imR_is_defined"
        ] = True
        guards["false_state_quotient_rejected"] = not all(_checks(bad).values())
        bad = deepcopy(certificate)
        bad["correct_equation_complex"]["unit_S3_PBW_correction_exact"] = False
        guards["missing_curvature_correction_rejected"] = not all(
            _checks(bad).values()
        )
        bad = deepcopy(certificate)
        bad["decision"]["rank14_equation_SDR_constructed"] = True
        guards["premature_SDR_promotion_rejected"] = not all(_checks(bad).values())
        bad_equation = _load("curved_curvature_auxiliary_chain_map.json")
        bad_equation["schema"] = "forged-unrelated-certificate"
        try:
            certificate_from_verified_inputs(
                symbol_certificate=_load(
                    "curved_rank14_weyl_cotton_symbol_audit.json"
                ),
                helicity_certificate=_load("curved_helicity_two_channel.json"),
                equation_chain_certificate=bad_equation,
                identity_chain_certificate=_load(
                    "curved_curvature_identity_chain_map.json"
                ),
                cycle_gate_certificate=_load(
                    "curved_rank14_equation_cycle_gate.json"
                ),
            )
        except AssertionError:
            guards["forged_equation_schema_rejected"] = True
        else:
            guards["forged_equation_schema_rejected"] = False
        bad_identity = _load("curved_curvature_identity_chain_map.json")
        bad_identity["schema"] = "forged-unrelated-certificate"
        try:
            certificate_from_verified_inputs(
                symbol_certificate=_load(
                    "curved_rank14_weyl_cotton_symbol_audit.json"
                ),
                helicity_certificate=_load("curved_helicity_two_channel.json"),
                equation_chain_certificate=_load(
                    "curved_curvature_auxiliary_chain_map.json"
                ),
                identity_chain_certificate=bad_identity,
                cycle_gate_certificate=_load(
                    "curved_rank14_equation_cycle_gate.json"
                ),
            )
        except AssertionError:
            guards["forged_identity_schema_rejected"] = True
        else:
            guards["forged_identity_schema_rejected"] = False
        if not all(guards.values()):
            raise AssertionError("rank-14 equation SDR mutation guard failed")

    if args.emit:
        OUTPUT.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "certificate": str(OUTPUT.relative_to(ROOT)),
                "checks": checks,
                "guards": guards,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
