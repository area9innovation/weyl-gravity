#!/usr/bin/env python3
"""Independently verify the compact-product Einstein atlas fragment."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[3]
ATLAS = Path(__file__).with_name("einstein-compact-product-atlas-fragment.json")
SCHEMA = ROOT / "residual_atlas/schema/residual-atlas-fragment-v1.schema.json"
GENERATOR = Path(__file__).with_name("generate_einstein_atlas_fragment.py")
STATUSES = {"CERTIFIED", "OBSTRUCTED", "OPEN", "NOT_APPLICABLE", "NO_CERTIFIED_MAP"}
SCOPE = {"theory", "background", "boundaries", "charge_sector", "carrier", "degree", "parity", "ell", "m", "k", "omega"}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify() -> None:
    value = json.loads(ATLAS.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    if value["generated_by_sha256"] != _sha256(GENERATOR):
        raise AssertionError("atlas generator hash mismatch")
    if set(value["status_vocabulary"]) != STATUSES:
        raise AssertionError("status vocabulary changed")
    by_id = {}
    for entry in value["entries"]:
        if set(entry["scope"]) != SCOPE:
            raise AssertionError(f"incomplete scope: {entry['id']}")
        if entry["id"] in by_id:
            raise AssertionError(f"duplicate stable identifier: {entry['id']}")
        by_id[entry["id"]] = entry
        for evidence in entry["evidence"]:
            path = ROOT / evidence["path"]
            payload = json.loads(path.read_text(encoding="utf-8"))
            if evidence["sha256"] != _sha256(path) or evidence["result_id"] != payload["result_id"]:
                raise AssertionError(f"stale evidence link: {entry['id']}")

    generic_extra = by_id["einstein.ph.wm.extra.generic_p_primary"]
    if generic_extra["descriptions"]["nonlinear"] != "OBSTRUCTED":
        raise AssertionError("generic pure-extra nonlinear status drifted")
    if generic_extra["mode_data"]["second_order"]["bounded_or_finite_quasiperiodic"]["status"] != "OBSTRUCTED":
        raise AssertionError("generic pure-extra bounded verdict drifted")
    if generic_extra["mode_data"]["second_order"]["causal_retarded"]["status"] != "OPEN":
        raise AssertionError("causal claim was overpromoted")

    balanced = by_id["einstein.ph.wm.mixed.ell2_k0_balanced_jet"]
    if balanced["mode_data"]["second_order"]["bounded_or_finite_quasiperiodic"]["status"] != "CERTIFIED":
        raise AssertionError("balanced jet lost its certified correction")

    independence = by_id["einstein.ph.wm.mixed.twist_exceptional_independence"]
    if independence["mode_data"]["taub_maps"]["status"] != "CERTIFIED":
        raise AssertionError("independence witness lost mu=0")
    if independence["mode_data"]["resonance"]["status"] != "CERTIFIED":
        raise AssertionError("independence witness lost R!=0")
    if "mu_X(u)=0 but R_bounded(u)!=0" not in independence["mode_data"]["resonance"]["statement"]:
        raise AssertionError("independence formula is absent")

    difference_census = by_id["einstein.ph.wm.interaction.exceptional_ell1_k0_difference_frequency_census"]
    if difference_census["mode_data"]["resonance"]["status"] != "CERTIFIED":
        raise AssertionError("exceptional difference-frequency census was lost")
    if "Twenty-seven exact resultant" not in difference_census["mode_data"]["resonance"]["statement"]:
        raise AssertionError("exceptional exact elimination witness was hidden")
    if difference_census["mode_data"]["second_order"]["bounded_or_finite_quasiperiodic"]["status"] != "OPEN":
        raise AssertionError("exceptional coefficientwise bounded cone was over-promoted")
    if difference_census["mode_data"]["second_order"]["causal_retarded"]["status"] != "NO_CERTIFIED_MAP":
        raise AssertionError("exceptional difference-frequency causal lifecycle was over-promoted")

    d_cross = by_id["einstein.ph.wm.interaction.d_times_ell2_extra"]
    if d_cross["mode_data"]["resonance"]["status"] != "CERTIFIED" or d_cross["descriptions"]["nonlinear"] != "OPEN":
        raise AssertionError("d-cross compatibility boundary drifted")

    bridge = by_id["einstein.ph.bridge.relative_branch_dictionary_v1"]
    if bridge["mode_data"]["resonance"]["status"] != "CERTIFIED":
        raise AssertionError("compact-product linear bridge 1 was not activated")
    if "noncyclic three-form all-row triangle" not in bridge["mode_data"]["resonance"]["statement"]:
        raise AssertionError("exact bridge lifecycle is absent")
    if "NONCYCLIC_THREE_FORM_LINEAR_TRIANGLE_CERTIFIED" not in bridge["claim_boundary"]:
        raise AssertionError("global covariant-map lifecycle is absent")
    if "causal Green data and q2/q3 relative compatibility remain open" not in bridge["claim_boundary"]:
        raise AssertionError("downstream compact-product gates were over-promoted")
    if bridge["descriptions"]["observational"] != "NO_CERTIFIED_MAP" or bridge["descriptions"]["quantum"] != "NO_CERTIFIED_MAP":
        raise AssertionError("downstream bridges borrowed the linear lifecycle")

    abd = by_id["einstein.ph.wm.interaction.abd_times_ell2_extra"]
    if abd["mode_data"]["resonance"]["status"] != "OPEN" or abd["descriptions"]["nonlinear"] != "OPEN":
        raise AssertionError("a,b,d matrix lifecycle drifted")

    complete_matrix = by_id["einstein.ph.wm.interaction.homogeneous_twist_times_ell2_extra"]
    if complete_matrix["mode_data"]["resonance"]["status"] != "OPEN":
        raise AssertionError("superseded homogeneous/twist resonance matrix was over-promoted")
    if complete_matrix["mode_data"]["second_order"]["bounded_or_finite_quasiperiodic"]["status"] != "OPEN":
        raise AssertionError("complete source matrix over-promoted the tangent cone")

    aligned = by_id["einstein.ph.wm.mixed.aligned_twist_ell2_extra_compatibility_face"]
    if aligned["mode_data"]["taub_maps"]["status"] != "CERTIFIED" or aligned["mode_data"]["resonance"]["status"] != "CERTIFIED":
        raise AssertionError("aligned common-zero face lost a certified compatibility gate")
    if aligned["mode_data"]["second_order"]["bounded_or_finite_quasiperiodic"]["status"] != "OBSTRUCTED":
        raise AssertionError("aligned orbit lost the bounded correction obstruction")
    if aligned["mode_data"]["second_order"]["smooth_secular"]["status"] != "CERTIFIED":
        raise AssertionError("aligned orbit lost the smooth-secular extension")
    smooth_statement = aligned["mode_data"]["second_order"]["smooth_secular"]["statement"]
    if "all 20 C4 extra/extra bilinear generators" not in smooth_statement:
        raise AssertionError("complete coefficient-explicit orbit ledger is absent")
    if "no additional off-axis branch" not in aligned["mode_data"]["resonance"]["statement"]:
        raise AssertionError("complete common-zero classification is absent")

    finite_generic = by_id["einstein.ph.wm.mixed.finite_generic_all_momenta_smooth_cone"]
    finite_second_order = finite_generic["mode_data"]["second_order"]
    if finite_second_order["smooth_secular"]["status"] != "CERTIFIED":
        raise AssertionError("finite generic smooth-secular theorem was lost")
    if finite_second_order["bounded_or_finite_quasiperiodic"]["status"] != "OPEN":
        raise AssertionError("finite generic bounded zero locus was over-promoted")
    if finite_second_order["causal_retarded"]["status"] != "OPEN":
        raise AssertionError("finite generic causal theorem was over-promoted")
    if "multiple |k| fibres" not in finite_second_order["smooth_secular"]["statement"]:
        raise AssertionError("multi-fibre scope is absent")

    complete_finite = by_id["einstein.ph.wm.complete_finite_harmonic_smooth_cone"]
    complete_second_order = complete_finite["mode_data"]["second_order"]
    if complete_second_order["smooth_secular"]["status"] != "CERTIFIED":
        raise AssertionError("complete finite smooth theorem was lost")
    if complete_second_order["bounded_or_finite_quasiperiodic"]["status"] != "OPEN":
        raise AssertionError("complete finite bounded cone was over-promoted")
    if complete_second_order["causal_retarded"]["status"] != "NO_CERTIFIED_MAP":
        raise AssertionError("complete finite causal theorem was over-promoted")
    if "P_(j,r)" not in complete_finite["mode_data"]["resonance"]["statement"]:
        raise AssertionError("polynomial bounded obstruction ledger is absent")

    standard_global = by_id["einstein.ph.wm.standard.global_bounded_cone"]
    global_second_order = standard_global["mode_data"]["second_order"]
    if global_second_order["bounded_or_finite_quasiperiodic"]["status"] != "CERTIFIED":
        raise AssertionError("standard global bounded cone was lost")
    if global_second_order["causal_retarded"]["status"] != "NO_CERTIFIED_MAP":
        raise AssertionError("standard global causal lifecycle was over-promoted")
    if "complete a/d polynomial maps" not in standard_global["claim_boundary"]:
        raise AssertionError("remaining polynomial gate was hidden")
    if "Q_e*a=0" not in standard_global["claim_boundary"]:
        raise AssertionError("universal electric-radion polynomial condition was hidden")

    electric_wilson = by_id["einstein.ph.wm.interaction.electric_wilson_complete_oscillator_transport"]
    transport_second_order = electric_wilson["mode_data"]["second_order"]
    if transport_second_order["bounded_or_finite_quasiperiodic"]["status"] != "CERTIFIED":
        raise AssertionError("complete electric/Wilson bounded transport was lost")
    if transport_second_order["causal_retarded"]["status"] != "NO_CERTIFIED_MAP":
        raise AssertionError("electric/Wilson causal lifecycle was over-promoted")
    if "a/d polynomial maps" not in electric_wilson["claim_boundary"]:
        raise AssertionError("remaining transport gate was hidden")

    circumference = by_id["einstein.ph.wm.interaction.circumference_complete_oscillator_column"]
    circumference_second_order = circumference["mode_data"]["second_order"]
    if circumference_second_order["bounded_or_finite_quasiperiodic"]["status"] != "CERTIFIED":
        raise AssertionError("circumference bounded zero locus was lost")
    if circumference_second_order["smooth_secular"]["status"] != "CERTIFIED":
        raise AssertionError("circumference smooth transport was lost")
    if circumference_second_order["causal_retarded"]["status"] != "NO_CERTIFIED_MAP":
        raise AssertionError("circumference causal lifecycle was over-promoted")
    if "R_(j,a), not P_(j,r)" not in circumference["mode_data"]["resonance"]["statement"]:
        raise AssertionError("circumference obstruction was assigned to the wrong ledger")

    d_column = by_id["einstein.ph.wm.interaction.d_times_ell2_extra"]
    if "d*z2=0" not in d_column["mode_data"]["second_order"]["bounded_or_finite_quasiperiodic"]["statement"]:
        raise AssertionError("full-time d polynomial condition was hidden")
    if "not a complete bounded d-column theorem" not in d_column["claim_boundary"]:
        raise AssertionError("old d constant projection was over-promoted")
    abd_column = by_id["einstein.ph.wm.interaction.abd_times_ell2_extra"]
    if abd_column["mode_data"]["resonance"]["status"] != "OPEN":
        raise AssertionError("superseded abd bounded matrix remained certified")
    if "superseded" not in abd_column["claim_boundary"]:
        raise AssertionError("abd full-time repair lifecycle was hidden")
    general_minus = by_id["einstein.ph.wm.interaction.abd_times_generic_k0_einstein_minus_pivot_fixtures"]
    if general_minus["mode_data"]["resonance"]["status"] != "CERTIFIED":
        raise AssertionError("multi-ell minus pivot fixtures were lost")
    if general_minus["descriptions"]["nonlinear"] != "OPEN":
        raise AssertionError("multi-ell fixtures over-promoted the nonlinear theorem")
    if "symbolic functional-form or degree bound" not in general_minus["mode_data"]["second_order"]["bounded_or_finite_quasiperiodic"]["statement"]:
        raise AssertionError("general-ell proof gate was hidden")
    ad_zero = by_id["einstein.ph.wm.interaction.ad_ell2_extra_polynomial_zero_locus"]
    if ad_zero["mode_data"]["resonance"]["status"] != "CERTIFIED":
        raise AssertionError("repaired a/d polynomial ideal was lost")
    if "<a*z_ax1,a*z_ax2,a*z_pol1,a*z_pol2,d*z_pol2>" not in ad_zero["mode_data"]["resonance"]["statement"]:
        raise AssertionError("repaired a/d generators were hidden")
    if ad_zero["mode_data"]["second_order"]["bounded_or_finite_quasiperiodic"]["status"] != "OPEN":
        raise AssertionError("a/d cross ideal over-promoted the bounded cone")
    complete_global_ell2 = by_id["einstein.ph.wm.mixed.complete_global_ell2_extra_bounded_cone"]
    complete_global_second = complete_global_ell2["mode_data"]["second_order"]
    if complete_global_second["bounded_or_finite_quasiperiodic"]["status"] != "CERTIFIED":
        raise AssertionError("complete global+ell2 bounded cone was lost")
    if "{(c,d,W_x,A)}" not in complete_global_second["bounded_or_finite_quasiperiodic"]["statement"]:
        raise AssertionError("complete global+ell2 cone was hidden")
    if complete_global_second["causal_retarded"]["status"] != "NO_CERTIFIED_MAP":
        raise AssertionError("global+ell2 causal lifecycle was over-promoted")
    aligned_global_wave = by_id["einstein.ph.wm.mixed.aligned_global_axial_ell2_minus_extra_bounded_cone"]
    aligned_second = aligned_global_wave["mode_data"]["second_order"]
    if aligned_second["bounded_or_finite_quasiperiodic"]["status"] != "CERTIFIED":
        raise AssertionError("aligned global-wave bounded cone was lost")
    if "x_minus=" not in aligned_second["bounded_or_finite_quasiperiodic"]["statement"]:
        raise AssertionError("aligned global-wave occupation cone was hidden")
    if aligned_second["causal_retarded"]["status"] != "NO_CERTIFIED_MAP":
        raise AssertionError("aligned global-wave causal lifecycle was over-promoted")
    superseded_ell2_aggregates = {
        "einstein.ph.wm.mixed.global_axial_ell2_all_m_minus_extra_bounded_cone",
        "einstein.ph.wm.mixed.global_ell2_all_m_both_parity_bounded_cone",
    }
    for identifier in superseded_ell2_aggregates:
        entry = by_id[identifier]
        second = entry["mode_data"]["second_order"]
        if entry["descriptions"]["nonlinear"] != "OBSTRUCTED":
            raise AssertionError(f"historical ell2 aggregate was not obstructed: {identifier}")
        if second["bounded_or_finite_quasiperiodic"]["status"] != "OBSTRUCTED":
            raise AssertionError(f"historical ell2 bounded verdict survived: {identifier}")
        if "SUPERSEDED BY" not in entry["claim_boundary"]:
            raise AssertionError(f"historical ell2 successor was not named: {identifier}")
    fixed_global = by_id["einstein.ph.wm.mixed.global_fixed_ell_k0_bounded_cone"]
    fixed_second = fixed_global["mode_data"]["second_order"]
    if fixed_global["descriptions"]["nonlinear"] != "CERTIFIED":
        raise AssertionError("complete fixed-ell global cone was not promoted")
    if fixed_global["mode_data"]["resonance"]["status"] != "CERTIFIED":
        raise AssertionError("fixed-ell global twist resonance was not closed")
    if fixed_second["bounded_or_finite_quasiperiodic"]["status"] != "CERTIFIED":
        raise AssertionError("complete fixed-ell global bounded cone was hidden")
    if fixed_second["causal_retarded"]["status"] != "NO_CERTIFIED_MAP":
        raise AssertionError("fixed-ell global causal lifecycle was over-promoted")
    if "historical A=0 restriction is superseded" not in fixed_global["claim_boundary"]:
        raise AssertionError("fixed-ell global replacement lifecycle is absent")
    finite_global = by_id["einstein.ph.wm.mixed.global_finite_harmonic_k0_bounded_cone"]
    finite_second = finite_global["mode_data"]["second_order"]
    if finite_global["descriptions"]["nonlinear"] != "CERTIFIED" or finite_global["mode_data"]["resonance"]["status"] != "CERTIFIED":
        raise AssertionError("finite multi-ell constant-twist lifecycle was not promoted")
    if finite_second["bounded_or_finite_quasiperiodic"]["status"] != "CERTIFIED":
        raise AssertionError("finite multi-ell constant-twist cone was hidden")
    if "c,W_x,A" not in finite_second["bounded_or_finite_quasiperiodic"]["statement"]:
        raise AssertionError("finite multi-ell free twist position was hidden")
    if finite_second["causal_retarded"]["status"] != "NO_CERTIFIED_MAP":
        raise AssertionError("finite multi-ell causal lifecycle was over-promoted")
    exceptional_ad = by_id["einstein.ph.wm.interaction.exceptional_ell1_ad_resonance_pivots"]
    exceptional_ad_second = exceptional_ad["mode_data"]["second_order"]
    if exceptional_ad["descriptions"]["nonlinear"] != "OPEN":
        raise AssertionError("exceptional a/d pivot row over-promoted the bounded cone")
    if exceptional_ad["mode_data"]["resonance"]["status"] != "CERTIFIED" or "a*t pivot" not in exceptional_ad["mode_data"]["resonance"]["statement"]:
        raise AssertionError("exceptional a/d direct pivot was hidden")
    if exceptional_ad_second["bounded_or_finite_quasiperiodic"]["status"] != "OPEN" or "exceptional-times-ell2-extra" not in exceptional_ad_second["bounded_or_finite_quasiperiodic"]["statement"]:
        raise AssertionError("exceptional difference collision was not fail-closed")
    if exceptional_ad_second["causal_retarded"]["status"] != "NO_CERTIFIED_MAP":
        raise AssertionError("exceptional a/d causal lifecycle was over-promoted")
    exceptional_difference = by_id["einstein.ph.wm.interaction.exceptional_ell1_ell2_extra_difference_matrix"]
    exceptional_difference_second = exceptional_difference["mode_data"]["second_order"]
    if exceptional_difference["descriptions"]["nonlinear"] != "OPEN":
        raise AssertionError("exceptional difference matrix over-promoted the bounded cone")
    if exceptional_difference["mode_data"]["resonance"]["status"] != "CERTIFIED" or "six adjoint projections vanish" not in exceptional_difference["mode_data"]["resonance"]["statement"]:
        raise AssertionError("exceptional sparse difference matrix was hidden")
    if exceptional_difference_second["bounded_or_finite_quasiperiodic"]["status"] != "OPEN" or "all-m tensor" not in exceptional_difference_second["bounded_or_finite_quasiperiodic"]["statement"]:
        raise AssertionError("exceptional all-m/L2 gate was not fail-closed")
    if exceptional_difference_second["causal_retarded"]["status"] != "NO_CERTIFIED_MAP":
        raise AssertionError("exceptional difference causal lifecycle was over-promoted")
    exceptional_ellipse = by_id["einstein.ph.wm.mixed.exceptional_axisymmetric_resonance_ellipse"]
    ellipse_second = exceptional_ellipse["mode_data"]["second_order"]
    if exceptional_ellipse["descriptions"]["nonlinear"] != "OPEN" or exceptional_ellipse["mode_data"]["taub_maps"]["status"] != "OBSTRUCTED":
        raise AssertionError("exceptional resonance ellipse lifecycle changed")
    if "16*r_x^2+3*r_p^2=115*d^2" not in exceptional_ellipse["mode_data"]["resonance"]["statement"]:
        raise AssertionError("exceptional resonance ellipse was hidden")
    if ellipse_second["bounded_or_finite_quasiperiodic"]["status"] != "OPEN" or ellipse_second["causal_retarded"]["status"] != "NO_CERTIFIED_MAP":
        raise AssertionError("exceptional resonance ellipse exceeded its correction class")
    exceptional_minus = by_id["einstein.ph.wm.mixed.exceptional_ellipse_einstein_minus_frequency_gate"]
    exceptional_minus_second = exceptional_minus["mode_data"]["second_order"]
    if exceptional_minus["descriptions"]["nonlinear"] != "OBSTRUCTED" or exceptional_minus["mode_data"]["taub_maps"]["status"] != "CERTIFIED":
        raise AssertionError("exceptional Einstein-minus lifecycle changed")
    if "Forty exact algebraic comparisons" not in exceptional_minus["mode_data"]["resonance"]["statement"]:
        raise AssertionError("exceptional Einstein-minus frequency census was hidden")
    if exceptional_minus_second["bounded_or_finite_quasiperiodic"]["status"] != "OBSTRUCTED" or "same-shell adjoint pairing" not in exceptional_minus_second["bounded_or_finite_quasiperiodic"]["statement"]:
        raise AssertionError("exceptional Einstein-minus obstruction was hidden")
    if exceptional_minus_second["smooth_secular"]["status"] != "CERTIFIED" or "secular shell term" not in exceptional_minus_second["smooth_secular"]["statement"]:
        raise AssertionError("exceptional Einstein-minus correction-class distinction was hidden")
    if exceptional_minus_second["causal_retarded"]["status"] != "NO_CERTIFIED_MAP":
        raise AssertionError("exceptional Einstein-minus causal lifecycle was over-promoted")
    fixed_ell_twist = by_id["einstein.ph.wm.interaction.fixed_ell_constant_twist_factorization"]
    if fixed_ell_twist["descriptions"]["nonlinear"] != "CERTIFIED":
        raise AssertionError("fixed-ell bounded lifecycle was not promoted")
    if fixed_ell_twist["mode_data"]["resonance"]["status"] != "CERTIFIED":
        raise AssertionError("fixed-ell angular factorization was lost")
    if "Q_(ell,+)=Q_(ell,-)=0" not in fixed_ell_twist["mode_data"]["resonance"]["statement"]:
        raise AssertionError("fixed-ell zero multiplicity matrices were hidden")
    if fixed_ell_twist["mode_data"]["second_order"]["bounded_or_finite_quasiperiodic"]["status"] != "CERTIFIED":
        raise AssertionError("fixed-ell bounded cone was hidden")
    travelling_twist = by_id["einstein.ph.wm.interaction.nonzero_k_constant_twist_same_shell"]
    if travelling_twist["descriptions"]["nonlinear"] != "CERTIFIED":
        raise AssertionError("nonzero-k twist same-shell theorem was not registered")
    if travelling_twist["mode_data"]["resonance"]["status"] != "CERTIFIED":
        raise AssertionError("nonzero-k twist resonance functional was hidden")
    if "exactly m_A=0" not in travelling_twist["mode_data"]["resonance"]["statement"]:
        raise AssertionError("nonzero-k twist kernel was hidden")
    if travelling_twist["mode_data"]["second_order"]["bounded_or_finite_quasiperiodic"]["status"] != "OPEN":
        raise AssertionError("nonzero-k full bounded gate was over-promoted")
    if travelling_twist["mode_data"]["second_order"]["causal_retarded"]["status"] != "NO_CERTIFIED_MAP":
        raise AssertionError("nonzero-k twist causal lifecycle was over-promoted")
    aligned_phase = by_id["einstein.ph.wm.interaction.twist_aligned_opposite_momentum_resonance_gate"]
    aligned_phase_second = aligned_phase["mode_data"]["second_order"]
    if aligned_phase["descriptions"]["nonlinear"] != "OPEN":
        raise AssertionError("twist-aligned phase gate over-promoted the bounded cone")
    if aligned_phase["mode_data"]["taub_maps"]["status"] != "CERTIFIED":
        raise AssertionError("twist-aligned common-zero witness was hidden")
    if aligned_phase["mode_data"]["resonance"]["status"] != "CERTIFIED" or "dynamical adjoint coefficient remains OPEN" not in aligned_phase["mode_data"]["resonance"]["statement"]:
        raise AssertionError("twist-aligned phase divisor was not fail-closed")
    if aligned_phase_second["bounded_or_finite_quasiperiodic"]["status"] != "OPEN" or aligned_phase_second["smooth_secular"]["status"] != "CERTIFIED":
        raise AssertionError("twist-aligned correction-class split changed")
    if aligned_phase_second["causal_retarded"]["status"] != "NO_CERTIFIED_MAP":
        raise AssertionError("twist-aligned causal lifecycle was over-promoted")
    aligned_obstruction = by_id["einstein.ph.wm.interaction.twist_aligned_opposite_momentum_bounded_obstruction"]
    aligned_obstruction_second = aligned_obstruction["mode_data"]["second_order"]
    if aligned_obstruction["descriptions"]["nonlinear"] != "OBSTRUCTED":
        raise AssertionError("twist-aligned bounded fixture was not marked obstructed")
    if aligned_obstruction["mode_data"]["taub_maps"]["status"] != "CERTIFIED":
        raise AssertionError("twist-aligned obstruction lost its common-zero audit")
    if aligned_obstruction_second["bounded_or_finite_quasiperiodic"]["status"] != "OBSTRUCTED":
        raise AssertionError("twist-aligned nonzero resonant functional was hidden")
    if aligned_obstruction_second["smooth_secular"]["status"] != "CERTIFIED":
        raise AssertionError("twist-aligned smooth correction lifecycle changed")
    if aligned_obstruction_second["causal_retarded"]["status"] != "NO_CERTIFIED_MAP":
        raise AssertionError("twist-aligned obstruction gained an uncertified causal map")
    repair = by_id["einstein.ph.wm.interaction.constant_twist_ell2_projector_repair"]
    if repair["descriptions"]["nonlinear"] != "CERTIFIED":
        raise AssertionError("constant-twist projector repair was not promoted")
    if repair["mode_data"]["resonance"]["status"] != "CERTIFIED" or "*dY_21" not in repair["mode_data"]["resonance"]["statement"]:
        raise AssertionError("corrected harmonic-type theorem was hidden")
    if repair["mode_data"]["second_order"]["bounded_or_finite_quasiperiodic"]["status"] != "CERTIFIED":
        raise AssertionError("corrected constant-twist product cone was lost")
    if "R_A^3" not in repair["mode_data"]["second_order"]["bounded_or_finite_quasiperiodic"]["statement"]:
        raise AssertionError("corrected spectator formula was hidden")

    superseded = {
        "einstein.ph.wm.interaction.constant_twist_wave_counterexample",
        "einstein.ph.wm.interaction.constant_twist_ell2_extra_position_zero_locus",
        "einstein.ph.wm.interaction.constant_twist_ell2_einstein_position_zero_locus",
        "einstein.ph.wm.interaction.constant_twist_ell2_moment_resonance_cone",
        "einstein.ph.wm.mixed.constant_twist_ell2_complete_bounded_cone",
    }
    for identifier in superseded:
        entry = by_id[identifier]
        if entry["descriptions"]["nonlinear"] != "OBSTRUCTED":
            raise AssertionError(f"superseded row was not fail-closed: {identifier}")
        if entry["mode_data"]["resonance"]["status"] != "OBSTRUCTED":
            raise AssertionError(f"superseded resonance was not withdrawn: {identifier}")
        if "SUPERSEDED BY" not in entry["claim_boundary"]:
            raise AssertionError(f"supersession link is absent: {identifier}")

    regenerated = {
        "einstein.ph.wm.mixed.twist_position_velocity_ell2_complete_bounded_cone",
        "einstein.ph.wm.mixed.twist_circumference_wilson_ell2_complete_bounded_cone",
        "einstein.ph.wm.mixed.d_twist_ell2_complete_bounded_cone",
        "einstein.ph.wm.mixed.complete_global_twist_ell2_bounded_cone",
    }
    for identifier in regenerated:
        entry = by_id[identifier]
        if entry["descriptions"]["nonlinear"] != "CERTIFIED":
            raise AssertionError(f"downstream successor was not regenerated: {identifier}")
        if entry["mode_data"]["second_order"]["bounded_or_finite_quasiperiodic"]["status"] != "CERTIFIED":
            raise AssertionError(f"downstream exact cone was not re-certified: {identifier}")
        if "REGENERATED" not in entry["claim_boundary"]:
            raise AssertionError(f"regeneration reason is absent: {identifier}")

    crosswalk = by_id["einstein.crosswalk.compact_product_to_asymptotic_or_vacuum_cylinder"]
    if crosswalk["evidence"] or set(crosswalk["descriptions"].values()) != {"NO_CERTIFIED_MAP"}:
        raise AssertionError("cross-background fail-closed entry changed")


if __name__ == "__main__":
    verify()
    print("EINSTEIN_COMPACT_PRODUCT_RESIDUAL_ATLAS_FRAGMENT_V1 independent verification: PASS")
