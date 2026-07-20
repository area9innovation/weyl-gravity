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
    relative_candidate13 = by_id["einstein.ph.bridge.relative_candidate13_derived_source_crosswalk"]
    relative_candidate13_second = relative_candidate13["mode_data"]["second_order"]
    if relative_candidate13["descriptions"]["nonlinear"] != "CERTIFIED" or "same candidate-13" not in relative_candidate13["mode_data"]["dispersion"]["statement"]:
        raise AssertionError("relative candidate-13 crosswalk scope changed")
    if relative_candidate13["mode_data"]["taub_maps"]["status"] != "CERTIFIED" or "circle-pressure" not in relative_candidate13["mode_data"]["taub_maps"]["statement"]:
        raise AssertionError("relative candidate-13 current receiver was hidden")
    if relative_candidate13["mode_data"]["resonance"]["status"] != "CERTIFIED" or "separate 18-dimensional" not in relative_candidate13["mode_data"]["resonance"]["statement"]:
        raise AssertionError("relative candidate-13 resonance receiver was hidden")
    if relative_candidate13_second["bounded_or_finite_quasiperiodic"]["status"] != "CERTIFIED" or relative_candidate13_second["smooth_secular"]["status"] != "CERTIFIED" or relative_candidate13_second["causal_retarded"]["status"] != "NO_CERTIFIED_MAP":
        raise AssertionError("relative candidate-13 correction classes changed")
    if "exactly {0}" not in relative_candidate13_second["bounded_or_finite_quasiperiodic"]["statement"]:
        raise AssertionError("relative candidate-13 bounded zero locus was hidden")
    if "full-domain support-local f2 remains obstructed" not in relative_candidate13["claim_boundary"] or "arity three is not authorized" not in relative_candidate13["claim_boundary"]:
        raise AssertionError("relative candidate-13 morphism boundary changed")

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
    exceptional_single = by_id["einstein.ph.wm.mixed.exceptional_ellipse_single_minus_dressing_no_go"]
    exceptional_single_second = exceptional_single["mode_data"]["second_order"]
    if exceptional_single["descriptions"]["nonlinear"] != "OBSTRUCTED" or exceptional_single["mode_data"]["taub_maps"]["status"] != "CERTIFIED":
        raise AssertionError("exceptional single-minus lifecycle changed")
    if "every ell>=2" not in exceptional_single["mode_data"]["resonance"]["statement"]:
        raise AssertionError("generic-lambda d pivot was hidden")
    if exceptional_single_second["bounded_or_finite_quasiperiodic"]["status"] != "OBSTRUCTED" or "forces d=0" not in exceptional_single_second["bounded_or_finite_quasiperiodic"]["statement"]:
        raise AssertionError("single-minus no-go was hidden")
    if exceptional_single_second["smooth_secular"]["status"] != "CERTIFIED" or exceptional_single_second["causal_retarded"]["status"] != "NO_CERTIFIED_MAP":
        raise AssertionError("single-minus correction classes changed")
    exceptional_finite = by_id["einstein.ph.wm.mixed.exceptional_ellipse_finite_minus_dressing_no_go"]
    finite_second = exceptional_finite["mode_data"]["second_order"]
    if exceptional_finite["descriptions"]["nonlinear"] != "OBSTRUCTED" or "three-minus" not in exceptional_finite["mode_data"]["resonance"]["statement"]:
        raise AssertionError("finite-minus no-go was hidden")
    if finite_second["bounded_or_finite_quasiperiodic"]["status"] != "OBSTRUCTED" or finite_second["smooth_secular"]["status"] != "CERTIFIED" or finite_second["causal_retarded"]["status"] != "NO_CERTIFIED_MAP":
        raise AssertionError("finite-minus correction classes changed")
    exceptional_wiener = by_id["einstein.ph.wm.mixed.exceptional_ellipse_wiener_minus_dressing_no_go"]
    wiener_second = exceptional_wiener["mode_data"]["second_order"]
    if exceptional_wiener["descriptions"]["nonlinear"] != "OBSTRUCTED" or "Bohr-frequency" not in exceptional_wiener["mode_data"]["resonance"]["statement"]:
        raise AssertionError("Wiener-Bohr no-go was hidden")
    if wiener_second["bounded_or_finite_quasiperiodic"]["status"] != "OBSTRUCTED" or wiener_second["smooth_secular"]["status"] != "OPEN" or wiener_second["causal_retarded"]["status"] != "NO_CERTIFIED_MAP":
        raise AssertionError("Wiener-Bohr correction classes changed")
    exceptional_global = by_id["einstein.ph.wm.mixed.exceptional_ellipse_standard_global_minus_no_go"]
    global_second = exceptional_global["mode_data"]["second_order"]
    if exceptional_global["descriptions"]["nonlinear"] != "OBSTRUCTED" or "triangular a then d pivots" not in exceptional_global["mode_data"]["resonance"]["statement"]:
        raise AssertionError("standard-global no-go was hidden")
    if global_second["bounded_or_finite_quasiperiodic"]["status"] != "OBSTRUCTED" or global_second["smooth_secular"]["status"] != "OPEN" or global_second["causal_retarded"]["status"] != "NO_CERTIFIED_MAP":
        raise AssertionError("standard-global correction classes changed")
    exceptional_ell1 = by_id["einstein.ph.wm.mixed.exceptional_ellipse_ell1_oscillator_minus_no_go"]
    ell1_second = exceptional_ell1["mode_data"]["second_order"]
    if exceptional_ell1["descriptions"]["nonlinear"] != "OBSTRUCTED" or "fourteen exact" not in exceptional_ell1["mode_data"]["resonance"]["statement"]:
        raise AssertionError("ell1-oscillator no-go was hidden")
    if ell1_second["bounded_or_finite_quasiperiodic"]["status"] != "OBSTRUCTED" or ell1_second["smooth_secular"]["status"] != "OPEN" or ell1_second["causal_retarded"]["status"] != "NO_CERTIFIED_MAP":
        raise AssertionError("ell1-oscillator correction classes changed")
    complete_pair_census = by_id["einstein.ph.wm.interaction.complete_k0_pair_to_minus_nonresonance"]
    if complete_pair_census["descriptions"]["nonlinear"] != "OPEN":
        raise AssertionError("complete k0 pair census was over-promoted to a nonlinear theorem")
    if complete_pair_census["mode_data"]["resonance"]["status"] != "CERTIFIED":
        raise AssertionError("complete k0 pair census lost its certified resonance status")
    if complete_pair_census["mode_data"]["taub_maps"]["status"] != "NOT_APPLICABLE":
        raise AssertionError("complete k0 pair census silently acquired a Taub claim")
    if complete_pair_census["mode_data"]["second_order"]["bounded_or_finite_quasiperiodic"]["status"] != "OPEN":
        raise AssertionError("complete k0 pair census was promoted from arithmetic to bounded sufficiency")
    complete_k0_no_go = by_id["einstein.ph.wm.mixed.exceptional_ellipse_complete_k0_no_go"]
    if complete_k0_no_go["descriptions"]["nonlinear"] != "OBSTRUCTED":
        raise AssertionError("complete k0 exceptional no-go lost its obstruction lifecycle")
    if complete_k0_no_go["mode_data"]["resonance"]["status"] != "OBSTRUCTED":
        raise AssertionError("complete k0 exceptional resonant functional lost its obstruction status")
    complete_k0_second = complete_k0_no_go["mode_data"]["second_order"]
    if complete_k0_second["bounded_or_finite_quasiperiodic"]["status"] != "OBSTRUCTED":
        raise AssertionError("complete k0 bounded correction class lost its obstruction")
    if complete_k0_second["smooth_secular"]["status"] != "OPEN" or complete_k0_second["causal_retarded"]["status"] != "NO_CERTIFIED_MAP":
        raise AssertionError("complete k0 no-go exceeded its certified correction classes")
    if "Maximal finite-energy/Sobolev" not in complete_k0_no_go["claim_boundary"]:
        raise AssertionError("complete k0 no-go lost its topology boundary")
    sobolev_bohr = by_id["einstein.ph.wm.mixed.exceptional_ellipse_sobolev_bohr_complete_k0_no_go"]
    if sobolev_bohr["descriptions"]["nonlinear"] != "OBSTRUCTED":
        raise AssertionError("Sobolev-Bohr complete k0 no-go lost its lifecycle")
    if sobolev_bohr["mode_data"]["resonance"]["status"] != "OBSTRUCTED" or "Bochner-Fejer" not in sobolev_bohr["mode_data"]["resonance"]["statement"]:
        raise AssertionError("Sobolev-Bohr projection theorem was hidden")
    sobolev_second = sobolev_bohr["mode_data"]["second_order"]
    if sobolev_second["bounded_or_finite_quasiperiodic"]["status"] != "OBSTRUCTED" or sobolev_second["smooth_secular"]["status"] != "OPEN" or sobolev_second["causal_retarded"]["status"] != "NO_CERTIFIED_MAP":
        raise AssertionError("Sobolev-Bohr correction classes changed")
    if "Sharp energy/low-regularity" not in sobolev_bohr["claim_boundary"]:
        raise AssertionError("Sobolev-Bohr no-go lost its low-regularity boundary")
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
    multimomentum = by_id["einstein.ph.wm.interaction.finite_multimomentum_resonance_divisor"]
    if multimomentum["descriptions"]["nonlinear"] != "OPEN":
        raise AssertionError("finite multimomentum arithmetic was promoted to a tangent-cone theorem")
    if multimomentum["mode_data"]["resonance"]["status"] != "CERTIFIED" or "squared shell divisor is linear" not in multimomentum["mode_data"]["resonance"]["statement"]:
        raise AssertionError("finite multimomentum divisor was hidden")
    if multimomentum["mode_data"]["taub_maps"]["status"] != "NOT_APPLICABLE":
        raise AssertionError("finite multimomentum divisor silently acquired a Taub claim")
    multimomentum_second = multimomentum["mode_data"]["second_order"]
    if multimomentum_second["bounded_or_finite_quasiperiodic"]["status"] != "OPEN" or multimomentum_second["smooth_secular"]["status"] != "OPEN" or multimomentum_second["causal_retarded"]["status"] != "NO_CERTIFIED_MAP":
        raise AssertionError("finite multimomentum correction classes were over-promoted")
    two_fibre = by_id["einstein.ph.wm.interaction.ell2_two_abs_momentum_identity_audit"]
    if two_fibre["descriptions"]["nonlinear"] != "OPEN":
        raise AssertionError("two-absolute-momentum identity audit was promoted")
    if two_fibre["mode_data"]["resonance"]["status"] != "CERTIFIED" or "exceptional set is finite" not in two_fibre["mode_data"]["resonance"]["statement"]:
        raise AssertionError("two-absolute-momentum identity audit was hidden")
    if two_fibre["mode_data"]["taub_maps"]["status"] != "NOT_APPLICABLE":
        raise AssertionError("two-absolute-momentum identity audit silently acquired a Taub claim")
    two_fibre_second = two_fibre["mode_data"]["second_order"]
    if two_fibre_second["bounded_or_finite_quasiperiodic"]["status"] != "OPEN" or two_fibre_second["smooth_secular"]["status"] != "OPEN" or two_fibre_second["causal_retarded"]["status"] != "NO_CERTIFIED_MAP":
        raise AssertionError("two-absolute-momentum correction classes were over-promoted")
    candidates = by_id["einstein.ph.wm.interaction.ell2_two_abs_momentum_isolated_candidates"]
    if candidates["descriptions"]["nonlinear"] != "OPEN":
        raise AssertionError("two-absolute-momentum candidate ledger was promoted")
    if candidates["mode_data"]["resonance"]["status"] != "CERTIFIED" or "21 distinct positive algebraic rho" not in candidates["mode_data"]["resonance"]["statement"]:
        raise AssertionError("two-absolute-momentum candidate ledger was hidden")
    if candidates["mode_data"]["taub_maps"]["status"] != "NOT_APPLICABLE":
        raise AssertionError("two-absolute-momentum candidate ledger silently acquired a Taub claim")
    candidate_second = candidates["mode_data"]["second_order"]
    if candidate_second["bounded_or_finite_quasiperiodic"]["status"] != "OPEN" or candidate_second["smooth_secular"]["status"] != "OPEN" or candidate_second["causal_retarded"]["status"] != "NO_CERTIFIED_MAP":
        raise AssertionError("two-absolute-momentum candidate correction classes were over-promoted")
    scalar_collision = by_id["einstein.ph.wm.interaction.ell2_collision_scalar_separation_classification"]
    scalar_collision_second = scalar_collision["mode_data"]["second_order"]
    if scalar_collision["descriptions"]["nonlinear"] != "CERTIFIED" or "universal midpoint factorization" not in scalar_collision["mode_data"]["taub_maps"]["statement"]:
        raise AssertionError("collision scalar-separation split was hidden")
    if scalar_collision["mode_data"]["resonance"]["status"] != "OPEN":
        raise AssertionError("six same-sign resonance joins were over-promoted")
    if scalar_collision_second["bounded_or_finite_quasiperiodic"]["status"] != "CERTIFIED" or "indices 1-15" not in scalar_collision_second["bounded_or_finite_quasiperiodic"]["statement"] or "indices 16-21" not in scalar_collision_second["bounded_or_finite_quasiperiodic"]["statement"]:
        raise AssertionError("collision scalar bounded verdict changed")
    if scalar_collision_second["smooth_secular"]["status"] != "OPEN" or scalar_collision_second["causal_retarded"]["status"] != "NO_CERTIFIED_MAP" or "not a mode identification across backgrounds" not in scalar_collision["claim_boundary"]:
        raise AssertionError("collision scalar classifier exceeded scope")
    same_fibre = by_id["einstein.ph.wm.interaction.ell2_same_sign_collision_same_fibre_census"]
    same_fibre_second = same_fibre["mode_data"]["second_order"]
    if same_fibre["mode_data"]["resonance"]["status"] != "CERTIFIED" or "864 exact" not in same_fibre["mode_data"]["resonance"]["statement"]:
        raise AssertionError("same-sign same-fibre census was hidden")
    if same_fibre["mode_data"]["taub_maps"]["status"] != "NOT_APPLICABLE" or "equal-branch zero-frequency products" not in same_fibre["scope"]["omega"]:
        raise AssertionError("same-sign same-fibre census merged zero-frequency receivers")
    if same_fibre_second["bounded_or_finite_quasiperiodic"]["status"] != "CERTIFIED" or same_fibre_second["smooth_secular"]["status"] != "CERTIFIED" or same_fibre_second["causal_retarded"]["status"] != "NO_CERTIFIED_MAP":
        raise AssertionError("same-sign same-fibre correction classes changed")
    witnesses = by_id["einstein.ph.wm.interaction.ell2_same_sign_collision_bounded_witnesses"]
    witness_second = witnesses["mode_data"]["second_order"]
    if witnesses["mode_data"]["taub_maps"]["status"] != "CERTIFIED" or "Farkas dependence" not in witnesses["mode_data"]["taub_maps"]["statement"]:
        raise AssertionError("same-sign bounded Taub witnesses were hidden")
    if witnesses["mode_data"]["resonance"]["status"] != "CERTIFIED" or "candidate 21" not in witnesses["mode_data"]["resonance"]["statement"]:
        raise AssertionError("same-sign bounded resonance witnesses were hidden")
    if witness_second["bounded_or_finite_quasiperiodic"]["status"] != "CERTIFIED" or witness_second["smooth_secular"]["status"] != "CERTIFIED" or witness_second["causal_retarded"]["status"] != "NO_CERTIFIED_MAP":
        raise AssertionError("same-sign bounded witness correction classes changed")
    if "not a classification of their full real geometry" not in witnesses["claim_boundary"]:
        raise AssertionError("same-sign bounded witness row exceeded nonemptiness scope")
    scalar_rays = by_id["einstein.ph.wm.interaction.ell2_same_sign_scalar_extreme_rays"]
    scalar_ray_second = scalar_rays["mode_data"]["second_order"]
    if scalar_rays["mode_data"]["taub_maps"]["status"] != "CERTIFIED" or "exactly four" not in scalar_rays["mode_data"]["taub_maps"]["statement"]:
        raise AssertionError("same-sign scalar extreme rays were hidden")
    if scalar_rays["mode_data"]["resonance"]["status"] != "OPEN" or scalar_ray_second["bounded_or_finite_quasiperiodic"]["status"] != "OPEN" or scalar_ray_second["causal_retarded"]["status"] != "NO_CERTIFIED_MAP":
        raise AssertionError("same-sign scalar extreme-ray row exceeded its projection scope")
    ray_lifts = by_id["einstein.ph.wm.interaction.ell2_same_sign_extreme_ray_lifts"]
    ray_lift_second = ray_lifts["mode_data"]["second_order"]
    if ray_lifts["mode_data"]["resonance"]["status"] != "CERTIFIED" or "Ten lifts omit" not in ray_lifts["mode_data"]["resonance"]["statement"]:
        raise AssertionError("same-sign extreme-ray lifts were hidden")
    if ray_lift_second["bounded_or_finite_quasiperiodic"]["status"] != "CERTIFIED" or "24 scalar extreme rays" not in ray_lift_second["bounded_or_finite_quasiperiodic"]["statement"]:
        raise AssertionError("same-sign extreme-ray lift verdict changed")
    if ray_lift_second["causal_retarded"]["status"] != "NO_CERTIFIED_MAP" or "not a classification of arbitrary nonnegative sums" not in ray_lifts["claim_boundary"]:
        raise AssertionError("same-sign extreme-ray lift row exceeded ray-saturation scope")
    sections = by_id["einstein.ph.wm.interaction.ell2_same_sign_scalar_cone_sections"]
    section_second = sections["mode_data"]["second_order"]
    if sections["mode_data"]["resonance"]["status"] != "CERTIFIED" or "arbitrary scalar-cone occupations" not in sections["mode_data"]["resonance"]["statement"]:
        raise AssertionError("same-sign scalar-cone sections were hidden")
    if section_second["bounded_or_finite_quasiperiodic"]["status"] != "CERTIFIED" or "projects surjectively" not in section_second["bounded_or_finite_quasiperiodic"]["statement"]:
        raise AssertionError("same-sign scalar-cone section verdict changed")
    if section_second["causal_retarded"]["status"] != "NO_CERTIFIED_MAP" or "not a statement that every amplitude" not in sections["claim_boundary"]:
        raise AssertionError("same-sign scalar-cone section row exceeded occupation-surjectivity scope")
    fibre_product = by_id["einstein.ph.wm.interaction.ell2_same_sign_phase_parity_fibre_product"]
    fibre_second = fibre_product["mode_data"]["second_order"]
    if fibre_product["mode_data"]["resonance"]["status"] != "CERTIFIED" or "complex resonance varieties are decomposed" not in fibre_product["mode_data"]["resonance"]["statement"]:
        raise AssertionError("same-sign phase/parity resonance varieties were hidden")
    if fibre_product["mode_data"]["taub_maps"]["status"] != "CERTIFIED" or "all three lifted rotation" not in fibre_product["mode_data"]["taub_maps"]["statement"]:
        raise AssertionError("same-sign phase/parity moment-map factors were hidden")
    if fibre_second["bounded_or_finite_quasiperiodic"]["status"] != "CERTIFIED" or "necessary and sufficient" not in fibre_second["bounded_or_finite_quasiperiodic"]["statement"]:
        raise AssertionError("same-sign phase/parity fibre-product formula changed")
    if fibre_second["causal_retarded"]["status"] != "NO_CERTIFIED_MAP" or "not an irreducible real Hermitian" not in fibre_product["claim_boundary"]:
        raise AssertionError("same-sign phase/parity fibre-product row exceeded equational scope")
    resonance_faces = by_id["einstein.ph.wm.interaction.ell2_same_sign_resonance_face_fibres"]
    resonance_face_second = resonance_faces["mode_data"]["second_order"]
    if resonance_faces["mode_data"]["resonance"]["status"] != "CERTIFIED" or "component counts are 1,1,1,4,1,2" not in resonance_faces["mode_data"]["resonance"]["statement"]:
        raise AssertionError("same-sign resonance-face fibres were hidden")
    if resonance_faces["mode_data"]["taub_maps"]["status"] != "CERTIFIED" or resonance_face_second["bounded_or_finite_quasiperiodic"]["status"] != "CERTIFIED":
        raise AssertionError("same-sign resonance-face theorem hid the exact bounded fibre-product formula")
    if resonance_face_second["causal_retarded"]["status"] != "NO_CERTIFIED_MAP" or "not a real connected-component" not in resonance_faces["claim_boundary"]:
        raise AssertionError("same-sign resonance-face theorem exceeded its lifecycle scope")
    automatic_links = by_id["einstein.ph.wm.interaction.ell2_same_sign_automatic_face_rotation_links"]
    automatic_second = automatic_links["mode_data"]["second_order"]
    if automatic_links["mode_data"]["taub_maps"]["status"] != "CERTIFIED" or "nonempty connected zero fibre" not in automatic_links["mode_data"]["taub_maps"]["statement"]:
        raise AssertionError("same-sign automatic-face rotation topology was hidden")
    if automatic_links["mode_data"]["resonance"]["status"] != "CERTIFIED" or "full bilinear factor" not in automatic_links["mode_data"]["resonance"]["statement"]:
        raise AssertionError("same-sign automatic-face resonance condition changed")
    if automatic_second["bounded_or_finite_quasiperiodic"]["status"] != "CERTIFIED" or "nonempty and connected" not in automatic_second["bounded_or_finite_quasiperiodic"]["statement"]:
        raise AssertionError("same-sign automatic-face bounded-link verdict changed")
    if automatic_second["causal_retarded"]["status"] != "NO_CERTIFIED_MAP" or "only on automatic faces" not in automatic_links["claim_boundary"]:
        raise AssertionError("same-sign automatic-face theorem exceeded its scope")
    rotation_critical = by_id["einstein.ph.wm.interaction.ell2_same_sign_axisymmetric_rotation_critical_locus"]
    rotation_critical_second = rotation_critical["mode_data"]["second_order"]
    if rotation_critical["mode_data"]["taub_maps"]["status"] != "CERTIFIED" or "rank zero at the origin and exactly two" not in rotation_critical["mode_data"]["taub_maps"]["statement"]:
        raise AssertionError("same-sign axisymmetric rotation critical locus was hidden")
    if rotation_critical_second["bounded_or_finite_quasiperiodic"]["status"] != "CERTIFIED" or "critical" not in rotation_critical_second["bounded_or_finite_quasiperiodic"]["statement"]:
        raise AssertionError("same-sign axisymmetric critical section lost bounded status")
    if rotation_critical_second["causal_retarded"]["status"] != "NO_CERTIFIED_MAP" or "not a quadratic-normal-form" not in rotation_critical["claim_boundary"]:
        raise AssertionError("same-sign axisymmetric critical-locus theorem exceeded scope")
    rotation_normal = by_id["einstein.ph.wm.interaction.ell2_same_sign_automatic_face_rotation_normal_form"]
    rotation_normal_second = rotation_normal["mode_data"]["second_order"]
    if rotation_normal["mode_data"]["lee_wald"]["status"] != "CERTIFIED" or "(4N-2,4N-2,2)" not in rotation_normal["mode_data"]["lee_wald"]["statement"]:
        raise AssertionError("same-sign automatic-face normal-form inertia was hidden")
    if rotation_normal["mode_data"]["taub_maps"]["status"] != "CERTIFIED" or "hyperbolic" not in rotation_normal["mode_data"]["taub_maps"]["statement"]:
        raise AssertionError("same-sign automatic-face hyperbolic normal form changed")
    if rotation_normal_second["bounded_or_finite_quasiperiodic"]["status"] != "CERTIFIED" or "exact nonaxisymmetric arc" not in rotation_normal_second["bounded_or_finite_quasiperiodic"]["statement"]:
        raise AssertionError("same-sign automatic-face exact arc changed")
    if rotation_normal_second["causal_retarded"]["status"] != "NO_CERTIFIED_MAP" or "aligned angular slice" not in rotation_normal["claim_boundary"]:
        raise AssertionError("same-sign automatic-face normal-form theorem exceeded scope")
    full_internal = by_id["einstein.ph.wm.interaction.ell2_same_sign_automatic_face_full_internal_rotation_normal_form"]
    full_internal_second = full_internal["mode_data"]["second_order"]
    if "(4M-2,4M-2,2M-2N+2)" not in full_internal["mode_data"]["taub_maps"]["statement"]:
        raise AssertionError("full internal automatic-face inertia was hidden")
    if "two eigenlines" not in full_internal["mode_data"]["lee_wald"]["statement"] or "fifteen" not in full_internal_second["bounded_or_finite_quasiperiodic"]["statement"]:
        raise AssertionError("full internal automatic-face support theorem changed")
    if full_internal_second["causal_retarded"]["status"] != "NO_CERTIFIED_MAP" or "only at fixed occupations" not in full_internal["claim_boundary"]:
        raise AssertionError("full internal automatic-face theorem exceeded scope")
    full_rotation = by_id["einstein.ph.wm.interaction.ell2_same_sign_automatic_face_full_rotation_normal_form"]
    full_rotation_second = full_rotation["mode_data"]["second_order"]
    if full_rotation["mode_data"]["lee_wald"]["status"] != "CERTIFIED" or "(4D-2,4D-2,2D-N+2)" not in full_rotation["mode_data"]["lee_wald"]["statement"]:
        raise AssertionError("same-sign automatic-face full normal-form inertia was hidden")
    if full_rotation["mode_data"]["taub_maps"]["status"] != "CERTIFIED" or "internal polarization" not in full_rotation["mode_data"]["taub_maps"]["statement"]:
        raise AssertionError("same-sign automatic-face internal normal form changed")
    if full_rotation_second["bounded_or_finite_quasiperiodic"]["status"] != "CERTIFIED" or "complete rotation Hessian" not in full_rotation_second["bounded_or_finite_quasiperiodic"]["statement"]:
        raise AssertionError("same-sign automatic-face full Hessian bounded verdict changed")
    if full_rotation_second["causal_retarded"]["status"] != "NO_CERTIFIED_MAP" or "fixed node norms" not in full_rotation["claim_boundary"]:
        raise AssertionError("same-sign automatic-face full normal-form theorem exceeded scope")
    parity_workload = by_id["einstein.ph.wm.interaction.ell2_two_abs_momentum_parity_workload"]
    if parity_workload["descriptions"]["nonlinear"] != "OPEN":
        raise AssertionError("two-absolute-momentum parity workload was promoted")
    if parity_workload["mode_data"]["resonance"]["status"] != "CERTIFIED" or "56 odd-L" not in parity_workload["mode_data"]["resonance"]["statement"]:
        raise AssertionError("two-absolute-momentum parity workload was hidden")
    if "164 reduced scalar adjoint coefficient" not in parity_workload["mode_data"]["lee_wald"]["statement"]:
        raise AssertionError("two-absolute-momentum source workload count was hidden")
    if parity_workload["mode_data"]["taub_maps"]["status"] != "NOT_APPLICABLE":
        raise AssertionError("two-absolute-momentum parity workload silently acquired a Taub claim")
    workload_second = parity_workload["mode_data"]["second_order"]
    if workload_second["bounded_or_finite_quasiperiodic"]["status"] != "OPEN" or workload_second["smooth_secular"]["status"] != "OPEN" or workload_second["causal_retarded"]["status"] != "NO_CERTIFIED_MAP":
        raise AssertionError("two-absolute-momentum parity workload correction classes were over-promoted")
    candidate4 = by_id["einstein.ph.wm.interaction.ell2_two_abs_momentum_candidate4_axial_bounded_obstruction"]
    if candidate4["descriptions"]["nonlinear"] != "OBSTRUCTED":
        raise AssertionError("candidate-4 bounded obstruction was hidden")
    if candidate4["mode_data"]["resonance"]["status"] != "OBSTRUCTED" or "norm witness 3622" not in candidate4["mode_data"]["resonance"]["statement"]:
        raise AssertionError("candidate-4 nonzero cokernel witness was hidden")
    if candidate4["mode_data"]["taub_maps"]["status"] != "NOT_APPLICABLE":
        raise AssertionError("candidate-4 resonant functional was merged with the Taub maps")
    candidate4_second = candidate4["mode_data"]["second_order"]
    if candidate4_second["bounded_or_finite_quasiperiodic"]["status"] != "OBSTRUCTED" or candidate4_second["smooth_secular"]["status"] != "OPEN" or candidate4_second["causal_retarded"]["status"] != "NO_CERTIFIED_MAP":
        raise AssertionError("candidate-4 correction classes were silently merged")
    if "other 162 workload coefficients" not in candidate4["claim_boundary"]:
        raise AssertionError("candidate-4 claim boundary lost the unresolved workload")
    triplet = by_id["einstein.ph.wm.interaction.ell2_two_abs_momentum_axial_qminus_l4_triplet_obstruction"]
    if triplet["descriptions"]["nonlinear"] != "OBSTRUCTED":
        raise AssertionError("axial q-minus L4 triplet obstruction was hidden")
    if triplet["mode_data"]["resonance"]["status"] != "OBSTRUCTED" or "nonzero constant term excludes zero" not in triplet["mode_data"]["resonance"]["statement"]:
        raise AssertionError("axial q-minus L4 triplet nonzero cokernel witness was hidden")
    if "three fibres are not identified" not in triplet["mode_data"]["dispersion"]["statement"]:
        raise AssertionError("axial q-minus L4 triplet silently merged its circumference fibres")
    if triplet["mode_data"]["taub_maps"]["status"] != "NOT_APPLICABLE":
        raise AssertionError("axial q-minus L4 resonances were merged with Taub maps")
    triplet_second = triplet["mode_data"]["second_order"]
    if triplet_second["bounded_or_finite_quasiperiodic"]["status"] != "OBSTRUCTED" or triplet_second["smooth_secular"]["status"] != "OPEN" or triplet_second["causal_retarded"]["status"] != "NO_CERTIFIED_MAP":
        raise AssertionError("axial q-minus L4 correction classes were silently merged")
    if "other 160 workload coefficients" not in triplet["claim_boundary"]:
        raise AssertionError("axial q-minus L4 triplet lost its unresolved workload")
    axial_matrix = by_id["einstein.ph.wm.interaction.ell2_two_abs_momentum_axial_axial_l4_matrix"]
    if axial_matrix["descriptions"]["nonlinear"] != "OBSTRUCTED":
        raise AssertionError("complete axial-axial L4 basis obstruction was hidden")
    if axial_matrix["mode_data"]["resonance"]["status"] != "OBSTRUCTED" or "26 have exact rational intervals excluding zero" not in axial_matrix["mode_data"]["resonance"]["statement"]:
        raise AssertionError("axial-axial L4 interval witnesses were hidden")
    if "distinct rows are not identified" not in axial_matrix["mode_data"]["dispersion"]["statement"]:
        raise AssertionError("axial-axial L4 circumference rows were merged")
    if axial_matrix["mode_data"]["taub_maps"]["status"] != "NOT_APPLICABLE":
        raise AssertionError("axial-axial L4 resonances were merged with Taub maps")
    axial_matrix_second = axial_matrix["mode_data"]["second_order"]
    if axial_matrix_second["bounded_or_finite_quasiperiodic"]["status"] != "OBSTRUCTED" or axial_matrix_second["smooth_secular"]["status"] != "OPEN" or axial_matrix_second["causal_retarded"]["status"] != "NO_CERTIFIED_MAP":
        raise AssertionError("axial-axial L4 correction classes were silently merged")
    if "not its arbitrary-amplitude zero variety" not in axial_matrix["claim_boundary"]:
        raise AssertionError("axial-axial L4 matrix exceeded its basis-fixture scope")
    polar_matrix = by_id["einstein.ph.wm.interaction.ell2_two_abs_momentum_polar_polar_l4_matrix"]
    if polar_matrix["descriptions"]["nonlinear"] != "OBSTRUCTED":
        raise AssertionError("complete polar-polar L4 basis obstruction was hidden")
    if polar_matrix["mode_data"]["resonance"]["status"] != "OBSTRUCTED" or "26 have exact rational intervals excluding zero" not in polar_matrix["mode_data"]["resonance"]["statement"]:
        raise AssertionError("polar-polar L4 interval witnesses were hidden")
    if "distinct rows are not identified" not in polar_matrix["mode_data"]["dispersion"]["statement"]:
        raise AssertionError("polar-polar L4 circumference rows were merged")
    if polar_matrix["mode_data"]["taub_maps"]["status"] != "NOT_APPLICABLE":
        raise AssertionError("polar-polar L4 resonances were merged with Taub maps")
    polar_matrix_second = polar_matrix["mode_data"]["second_order"]
    if polar_matrix_second["bounded_or_finite_quasiperiodic"]["status"] != "OBSTRUCTED" or polar_matrix_second["smooth_secular"]["status"] != "OPEN" or polar_matrix_second["causal_retarded"]["status"] != "NO_CERTIFIED_MAP":
        raise AssertionError("polar-polar L4 correction classes were silently merged")
    if "two ordered cross-parity matrices" not in polar_matrix["claim_boundary"]:
        raise AssertionError("polar-polar L4 matrix hid the remaining parity workload")
    forward = by_id["einstein.ph.wm.interaction.ell2_two_abs_momentum_axial_polar_l4_matrix"]
    if forward["descriptions"]["nonlinear"] != "OBSTRUCTED" or "All 27 scalar adjoint coefficients" not in forward["mode_data"]["resonance"]["statement"]:
        raise AssertionError("forward cross-parity L4 matrix was hidden")
    if "reverse input order is not identified" not in forward["mode_data"]["dispersion"]["statement"] or "not the reverse order" not in forward["claim_boundary"]:
        raise AssertionError("forward cross-parity order was merged")
    forward_second = forward["mode_data"]["second_order"]
    if forward_second["bounded_or_finite_quasiperiodic"]["status"] != "OBSTRUCTED" or forward_second["smooth_secular"]["status"] != "OPEN" or forward_second["causal_retarded"]["status"] != "NO_CERTIFIED_MAP":
        raise AssertionError("forward cross-parity correction classes were merged")
    reverse = by_id["einstein.ph.wm.interaction.ell2_two_abs_momentum_polar_axial_l4_matrix"]
    if reverse["descriptions"]["nonlinear"] != "OBSTRUCTED" or "All 27 scalar adjoint coefficients" not in reverse["mode_data"]["resonance"]["statement"]:
        raise AssertionError("reverse cross-parity L4 matrix was hidden")
    if "explicit role substitution, not name matching" not in reverse["mode_data"]["dispersion"]["statement"] or "108 of 108 axisymmetric L4 basis coefficients" not in reverse["claim_boundary"]:
        raise AssertionError("reverse cross-parity role map or workload boundary was hidden")
    reverse_second = reverse["mode_data"]["second_order"]
    if reverse_second["bounded_or_finite_quasiperiodic"]["status"] != "OBSTRUCTED" or reverse_second["smooth_secular"]["status"] != "OPEN" or reverse_second["causal_retarded"]["status"] != "NO_CERTIFIED_MAP":
        raise AssertionError("reverse cross-parity correction classes were merged")
    completion = by_id["einstein.ph.wm.interaction.ell2_two_abs_momentum_nonaxisymmetric_l1_matrix"]
    completion_second = completion["mode_data"]["second_order"]
    if completion["descriptions"]["nonlinear"] != "OBSTRUCTED" or "All twelve exceptional L1 adjoint coefficients are nonzero" not in completion["mode_data"]["resonance"]["statement"]:
        raise AssertionError("complete cross-fibre branch-basis matrix was hidden")
    if completion["mode_data"]["taub_maps"]["status"] != "NOT_APPLICABLE":
        raise AssertionError("complete cross-fibre resonance functionals were merged with Taub maps")
    if completion_second["bounded_or_finite_quasiperiodic"]["status"] != "OBSTRUCTED" or completion_second["smooth_secular"]["status"] != "OPEN" or completion_second["causal_retarded"]["status"] != "NO_CERTIFIED_MAP":
        raise AssertionError("complete cross-fibre correction classes were merged")
    if "164 of 164 branch-basis scalar coefficients" not in completion["claim_boundary"] or "not the arbitrary-amplitude zero variety" not in completion["claim_boundary"]:
        raise AssertionError("complete cross-fibre basis row exceeded its amplitude scope")
    assembly = by_id["einstein.ph.wm.interaction.ell2_two_abs_momentum_cross_fibre_amplitude_system"]
    assembly_second = assembly["mode_data"]["second_order"]
    if assembly["descriptions"]["nonlinear"] != "OPEN" or "twenty-one pairwise distinct physical circumference" not in assembly["mode_data"]["dispersion"]["statement"]:
        raise AssertionError("cross-fibre amplitude background partition was hidden")
    if "54 target-parity/adjoint equations" not in assembly["mode_data"]["lee_wald"]["statement"] or "128 ordered branch-basis fixtures" not in assembly["mode_data"]["lee_wald"]["statement"] or "418 complex scalar magnetic" not in assembly["mode_data"]["lee_wald"]["statement"] or assembly["mode_data"]["resonance"]["status"] != "CERTIFIED":
        raise AssertionError("cross-fibre amplitude system was hidden")
    if assembly["mode_data"]["taub_maps"]["status"] != "OPEN" or assembly_second["bounded_or_finite_quasiperiodic"]["status"] != "OPEN" or assembly_second["smooth_secular"]["status"] != "OPEN" or assembly_second["causal_retarded"]["status"] != "NO_CERTIFIED_MAP":
        raise AssertionError("cross-fibre amplitude correction classes were merged")
    if "not an irreducible zero-variety decomposition" not in assembly["claim_boundary"]:
        raise AssertionError("cross-fibre amplitude system exceeded its zero-variety scope")
    scalar_l4 = by_id["einstein.ph.wm.interaction.ell2_two_abs_momentum_scalar_l4_zero_varieties"]
    scalar_l4_second = scalar_l4["mode_data"]["second_order"]
    if scalar_l4["descriptions"]["nonlinear"] != "OPEN" or "fibres 3,5,9,15,21" not in scalar_l4["mode_data"]["dispersion"]["statement"]:
        raise AssertionError("scalar L4 zero-variety scope was hidden")
    if scalar_l4["mode_data"]["resonance"]["status"] != "CERTIFIED" or "exactly four ten-dimensional linear components" not in scalar_l4["mode_data"]["resonance"]["statement"] or "two mixed proportionality sheets" not in scalar_l4["mode_data"]["resonance"]["statement"]:
        raise AssertionError("scalar L4 zero-variety decomposition was hidden")
    if scalar_l4["mode_data"]["taub_maps"]["status"] != "OPEN" or scalar_l4_second["bounded_or_finite_quasiperiodic"]["status"] != "OPEN" or scalar_l4_second["smooth_secular"]["status"] != "OPEN" or scalar_l4_second["causal_retarded"]["status"] != "NO_CERTIFIED_MAP":
        raise AssertionError("scalar L4 correction classes were merged")
    if "other sixteen fibres" not in scalar_l4["claim_boundary"] or "complete two-fibre tangent cone" not in scalar_l4["claim_boundary"]:
        raise AssertionError("scalar L4 decomposition exceeded scope")
    odd = by_id["einstein.ph.wm.interaction.ell2_two_abs_momentum_odd_l_highest_weight_zero_subspaces"]
    odd_second = odd["mode_data"]["second_order"]
    if odd["descriptions"]["nonlinear"] != "OPEN" or "three L1 difference carriers and six L3 sum carriers" not in odd["mode_data"]["dispersion"]["statement"]:
        raise AssertionError("odd-L highest-weight carrier typing was hidden")
    if odd["mode_data"]["resonance"]["status"] != "CERTIFIED" or "all 130 scalar equations" not in odd["mode_data"]["resonance"]["statement"]:
        raise AssertionError("odd-L highest-weight zero witness was hidden")
    if odd["mode_data"]["taub_maps"]["status"] != "OPEN" or odd_second["bounded_or_finite_quasiperiodic"]["status"] != "OPEN" or odd_second["smooth_secular"]["status"] != "OPEN" or odd_second["causal_retarded"]["status"] != "NO_CERTIFIED_MAP":
        raise AssertionError("odd-L witness correction classes were merged")
    if "not their complete irreducible ideals" not in odd["claim_boundary"] or "two-fibre tangent cone" not in odd["claim_boundary"]:
        raise AssertionError("odd-L witness exceeded scope")
    scalar_l3 = by_id["einstein.ph.wm.interaction.ell2_two_abs_momentum_scalar_l3_zero_variety"]
    scalar_l3_second = scalar_l3["mode_data"]["second_order"]
    if scalar_l3["descriptions"]["nonlinear"] != "OPEN" or "Candidate 2 remains one declared physical circumference" not in scalar_l3["mode_data"]["dispersion"]["statement"]:
        raise AssertionError("candidate-2 scalar L3 fibre scope was hidden")
    if scalar_l3["mode_data"]["resonance"]["status"] != "CERTIFIED" or "irreducible complex dimension-12" not in scalar_l3["mode_data"]["resonance"]["statement"] or "twenty minors" not in scalar_l3["mode_data"]["resonance"]["statement"]:
        raise AssertionError("candidate-2 scalar L3 ideal was hidden")
    if scalar_l3["mode_data"]["taub_maps"]["status"] != "OPEN" or scalar_l3_second["bounded_or_finite_quasiperiodic"]["status"] != "OPEN" or scalar_l3_second["smooth_secular"]["status"] != "OPEN" or scalar_l3_second["causal_retarded"]["status"] != "NO_CERTIFIED_MAP":
        raise AssertionError("candidate-2 scalar L3 correction classes were merged")
    if "other fifteen fibrewise ideals" not in scalar_l3["claim_boundary"] or "two-fibre tangent cone" not in scalar_l3["claim_boundary"]:
        raise AssertionError("candidate-2 scalar L3 theorem exceeded scope")
    scalar_l1 = by_id["einstein.ph.wm.interaction.ell2_two_abs_momentum_scalar_l1_zero_varieties"]
    scalar_l1_second = scalar_l1["mode_data"]["second_order"]
    if scalar_l1["descriptions"]["nonlinear"] != "OPEN" or "Candidates 14,17,20" not in scalar_l1["mode_data"]["dispersion"]["statement"]:
        raise AssertionError("scalar L1 fibre scope was hidden")
    if "lambda squared equal to 128/5" not in scalar_l1["mode_data"]["lee_wald"]["statement"]:
        raise AssertionError("scalar L1 parity-pencil normalization was hidden")
    if scalar_l1["mode_data"]["resonance"]["status"] != "CERTIFIED" or "irreducible complex dimension-14" not in scalar_l1["mode_data"]["resonance"]["statement"]:
        raise AssertionError("scalar L1 ideals were hidden")
    if scalar_l1["mode_data"]["taub_maps"]["status"] != "OPEN" or scalar_l1_second["bounded_or_finite_quasiperiodic"]["status"] != "OPEN" or scalar_l1_second["smooth_secular"]["status"] != "OPEN" or scalar_l1_second["causal_retarded"]["status"] != "NO_CERTIFIED_MAP":
        raise AssertionError("scalar L1 correction classes were merged")
    if "all 20 fibrewise cross-fibre resonance ideals are now classified" not in scalar_l1["claim_boundary"] or "two-fibre tangent cone" not in scalar_l1["claim_boundary"]:
        raise AssertionError("scalar L1 theorem exceeded scope")
    candidate4 = by_id["einstein.ph.wm.interaction.ell2_two_abs_momentum_candidate4_l4_zero_variety"]
    candidate4_second = candidate4["mode_data"]["second_order"]
    if candidate4["descriptions"]["nonlinear"] != "OPEN" or "Candidate 4 remains one declared physical circumference" not in candidate4["mode_data"]["dispersion"]["statement"]:
        raise AssertionError("candidate-4 L4 fibre scope was hidden")
    if candidate4["mode_data"]["resonance"]["status"] != "CERTIFIED" or "exactly four ten-dimensional linear components" not in candidate4["mode_data"]["resonance"]["statement"] or "plus or minus sqrt(3)" not in candidate4["mode_data"]["resonance"]["statement"]:
        raise AssertionError("candidate-4 L4 decomposition was hidden")
    if candidate4["mode_data"]["taub_maps"]["status"] != "OPEN" or candidate4_second["bounded_or_finite_quasiperiodic"]["status"] != "OPEN" or candidate4_second["smooth_secular"]["status"] != "OPEN" or candidate4_second["causal_retarded"]["status"] != "NO_CERTIFIED_MAP":
        raise AssertionError("candidate-4 L4 correction classes were merged")
    if "all 20 fibrewise cross-fibre resonance ideals are now classified" not in candidate4["claim_boundary"] or "two-fibre tangent cone" not in candidate4["claim_boundary"]:
        raise AssertionError("candidate-4 L4 theorem exceeded scope")
    doublet_l3 = by_id["einstein.ph.wm.interaction.ell2_two_abs_momentum_target_doublet_l3_zero_varieties"]
    doublet_l3_second = doublet_l3["mode_data"]["second_order"]
    if doublet_l3["descriptions"]["nonlinear"] != "OPEN" or "Candidates 1 and 16 remain two separately tuned" not in doublet_l3["mode_data"]["dispersion"]["statement"]:
        raise AssertionError("target-doublet L3 fibre scopes were hidden")
    if "four target-adjoint rows reduce exactly to two first-transvectant equations" not in doublet_l3["mode_data"]["lee_wald"]["statement"]:
        raise AssertionError("target-doublet L3 normal form was hidden")
    if doublet_l3["mode_data"]["resonance"]["status"] != "CERTIFIED" or "irreducible complex dimension-12" not in doublet_l3["mode_data"]["resonance"]["statement"]:
        raise AssertionError("target-doublet L3 ideals were hidden")
    if doublet_l3["mode_data"]["taub_maps"]["status"] != "OPEN" or doublet_l3_second["bounded_or_finite_quasiperiodic"]["status"] != "OPEN" or doublet_l3_second["smooth_secular"]["status"] != "OPEN" or doublet_l3_second["causal_retarded"]["status"] != "NO_CERTIFIED_MAP":
        raise AssertionError("target-doublet L3 correction classes were merged")
    if "all 20 fibrewise cross-fibre resonance ideals are now classified" not in doublet_l3["claim_boundary"] or "two-fibre tangent cone" not in doublet_l3["claim_boundary"]:
        raise AssertionError("target-doublet L3 theorem exceeded scope")
    multiplicity_l3 = by_id["einstein.ph.wm.interaction.ell2_two_abs_momentum_multiplicity_two_l3_zero_varieties"]
    multiplicity_l3_second = multiplicity_l3["mode_data"]["second_order"]
    if multiplicity_l3["descriptions"]["nonlinear"] != "OPEN" or "Candidates 6, 10 and 18 remain three separately tuned" not in multiplicity_l3["mode_data"]["dispersion"]["statement"]:
        raise AssertionError("multiplicity-two L3 fibre scopes were hidden")
    if "parity-pencil square of 384" not in multiplicity_l3["mode_data"]["lee_wald"]["statement"] or "one spectator quartic per parity" not in multiplicity_l3["mode_data"]["lee_wald"]["statement"]:
        raise AssertionError("multiplicity-two L3 reduction was hidden")
    if multiplicity_l3["mode_data"]["resonance"]["status"] != "CERTIFIED" or "irreducible complex dimension-22" not in multiplicity_l3["mode_data"]["resonance"]["statement"]:
        raise AssertionError("multiplicity-two L3 ideals were hidden")
    if multiplicity_l3["mode_data"]["taub_maps"]["status"] != "OPEN" or multiplicity_l3_second["bounded_or_finite_quasiperiodic"]["status"] != "OPEN" or multiplicity_l3_second["smooth_secular"]["status"] != "OPEN" or multiplicity_l3_second["causal_retarded"]["status"] != "NO_CERTIFIED_MAP":
        raise AssertionError("multiplicity-two L3 correction classes were merged")
    if "all 20 fibrewise cross-fibre resonance ideals are now classified" not in multiplicity_l3["claim_boundary"]:
        raise AssertionError("multiplicity-two L3 theorem exceeded scope")
    rank_one_l4 = by_id["einstein.ph.wm.interaction.ell2_two_abs_momentum_rank_one_branch_l4_zero_varieties"]
    rank_one_l4_second = rank_one_l4["mode_data"]["second_order"]
    if rank_one_l4["descriptions"]["nonlinear"] != "OPEN" or "Candidates 8 and 12 remain two separately tuned" not in rank_one_l4["mode_data"]["dispersion"]["statement"]:
        raise AssertionError("multiplicity-two L4 fibre scopes were hidden")
    if "squared row ratios 3/40 and 120" not in rank_one_l4["mode_data"]["lee_wald"]["statement"]:
        raise AssertionError("multiplicity-two L4 row reduction was hidden")
    if rank_one_l4["mode_data"]["resonance"]["status"] != "CERTIFIED" or "four complex dimension-20 components" not in rank_one_l4["mode_data"]["resonance"]["statement"]:
        raise AssertionError("multiplicity-two L4 ideals were hidden")
    if rank_one_l4["mode_data"]["taub_maps"]["status"] != "OPEN" or rank_one_l4_second["bounded_or_finite_quasiperiodic"]["status"] != "OPEN" or rank_one_l4_second["smooth_secular"]["status"] != "OPEN" or rank_one_l4_second["causal_retarded"]["status"] != "NO_CERTIFIED_MAP":
        raise AssertionError("multiplicity-two L4 correction classes were merged")
    if "all 20 cross-fibre ideals are now classified" not in rank_one_l4["claim_boundary"]:
        raise AssertionError("multiplicity-two L4 theorem exceeded scope")
    regular_l4 = by_id["einstein.ph.wm.interaction.ell2_two_abs_momentum_regular_pencil_l4_zero_varieties"]
    regular_l4_second = regular_l4["mode_data"]["second_order"]
    if regular_l4["descriptions"]["nonlinear"] != "OPEN" or "three separately tuned circumference fibres" not in regular_l4["mode_data"]["dispersion"]["statement"]:
        raise AssertionError("regular-pencil L4 fibre scopes were hidden")
    if "positive trace, determinant and discriminant" not in regular_l4["mode_data"]["lee_wald"]["statement"]:
        raise AssertionError("regular-pencil L4 exact root criterion was hidden")
    if regular_l4["mode_data"]["resonance"]["status"] != "CERTIFIED" or "exactly six real-supported linear components" not in regular_l4["mode_data"]["resonance"]["statement"]:
        raise AssertionError("regular-pencil L4 decomposition was hidden")
    if regular_l4["mode_data"]["taub_maps"]["status"] != "OPEN" or regular_l4_second["bounded_or_finite_quasiperiodic"]["status"] != "OPEN" or regular_l4_second["smooth_secular"]["status"] != "OPEN" or regular_l4_second["causal_retarded"]["status"] != "NO_CERTIFIED_MAP":
        raise AssertionError("regular-pencil L4 correction classes were merged")
    if "all 20 cross-fibre ideals are now classified" not in regular_l4["claim_boundary"]:
        raise AssertionError("regular-pencil L4 theorem exceeded scope")
    candidate13 = by_id["einstein.ph.wm.interaction.ell2_two_abs_momentum_candidate13_l4_incidence_reduction"]
    candidate13_second = candidate13["mode_data"]["second_order"]
    if candidate13["descriptions"]["nonlinear"] != "OBSTRUCTED" or "separately tuned circumference fibre" not in candidate13["mode_data"]["dispersion"]["statement"]:
        raise AssertionError("candidate-13 incidence fibre scope was hidden")
    if "four distinct nonzero real generalized roots" not in candidate13["mode_data"]["lee_wald"]["statement"] or "three-root cancellation witness" not in candidate13["mode_data"]["lee_wald"]["statement"]:
        raise AssertionError("candidate-13 exact pencil reduction was hidden")
    if candidate13["mode_data"]["resonance"]["status"] != "CERTIFIED" or "prime complex dimension-22 cone" not in candidate13["mode_data"]["resonance"]["statement"] or "splitting-jump strata are at most 20" not in candidate13["mode_data"]["resonance"]["statement"]:
        raise AssertionError("candidate-13 prime zero-variety theorem was hidden")
    if candidate13["mode_data"]["taub_maps"]["status"] != "CERTIFIED" or "only at the origin" not in candidate13["mode_data"]["taub_maps"]["statement"] or candidate13_second["bounded_or_finite_quasiperiodic"]["status"] != "OBSTRUCTED" or candidate13_second["smooth_secular"]["status"] != "OBSTRUCTED" or candidate13_second["causal_retarded"]["status"] != "NO_CERTIFIED_MAP":
        raise AssertionError("candidate-13 pure-extra Taub lifecycle changed")
    if "pure-extra Taub no-go" not in candidate13["claim_boundary"] or "larger mixed Einstein-extra" not in candidate13["claim_boundary"]:
        raise AssertionError("candidate-13 theorem boundary changed")
    candidate13_mixed = by_id["einstein.ph.wm.interaction.ell2_two_abs_momentum_candidate13_mixed_moment_resonance_null_witness"]
    candidate13_mixed_second = candidate13_mixed["mode_data"]["second_order"]
    if candidate13_mixed["scope"]["m"] != 0 or "Einstein-minus" not in candidate13_mixed["scope"]["carrier"]:
        raise AssertionError("candidate-13 mixed witness scope changed")
    if candidate13_mixed["mode_data"]["taub_maps"]["status"] != "CERTIFIED" or "J_1,J_2,J_3" not in candidate13_mixed["mode_data"]["taub_maps"]["statement"]:
        raise AssertionError("candidate-13 mixed moment-null witness was hidden")
    if candidate13_mixed["mode_data"]["resonance"]["status"] != "CERTIFIED" or "second-fibre-zero sheet" not in candidate13_mixed["mode_data"]["resonance"]["statement"]:
        raise AssertionError("candidate-13 mixed resonance-null witness was hidden")
    if candidate13_mixed_second["bounded_or_finite_quasiperiodic"]["status"] != "OPEN" or candidate13_mixed_second["smooth_secular"]["status"] != "OPEN" or candidate13_mixed_second["causal_retarded"]["status"] != "NO_CERTIFIED_MAP":
        raise AssertionError("candidate-13 mixed correction classes were merged")
    if "independence and activation witness" not in candidate13_mixed["claim_boundary"]:
        raise AssertionError("candidate-13 mixed witness exceeded scope")
    candidate13_same = by_id["einstein.ph.wm.interaction.ell2_two_abs_momentum_candidate13_same_fibre_resonance_census"]
    candidate13_same_second = candidate13_same["mode_data"]["second_order"]
    if candidate13_same["mode_data"]["resonance"]["status"] != "CERTIFIED" or "144 exact" not in candidate13_same["mode_data"]["resonance"]["statement"] or "homogeneous nonzero-frequency quotient" not in candidate13_same["mode_data"]["resonance"]["statement"]:
        raise AssertionError("candidate-13 same-fibre census was hidden")
    if candidate13_same["mode_data"]["taub_maps"]["status"] != "OPEN" or candidate13_same_second["bounded_or_finite_quasiperiodic"]["status"] != "OPEN" or candidate13_same_second["smooth_secular"]["status"] != "OPEN" or candidate13_same_second["causal_retarded"]["status"] != "NO_CERTIFIED_MAP":
        raise AssertionError("candidate-13 same-fibre correction classes were merged")
    if "complete nonzero-frequency same-fibre shell census" not in candidate13_same["claim_boundary"] or "K!=0 and K=0" not in candidate13_same["claim_boundary"]:
        raise AssertionError("candidate-13 same-fibre theorem boundary changed")
    candidate13_extension = by_id["einstein.ph.wm.interaction.ell2_two_abs_momentum_candidate13_mixed_bounded_extension"]
    candidate13_extension_second = candidate13_extension["mode_data"]["second_order"]
    if candidate13_extension["descriptions"]["nonlinear"] != "OBSTRUCTED":
        raise AssertionError("candidate-13 mixed extension lifecycle changed")
    if candidate13_extension["mode_data"]["taub_maps"]["status"] != "CERTIFIED" or "R_c is strictly negative" not in candidate13_extension["mode_data"]["taub_maps"]["statement"]:
        raise AssertionError("candidate-13 zero-block cokernel join was hidden")
    if candidate13_extension["mode_data"]["resonance"]["status"] != "CERTIFIED" or "other 20 collision circumferences are distinct" not in candidate13_extension["mode_data"]["resonance"]["statement"]:
        raise AssertionError("candidate-13 bounded resonance join was hidden")
    if candidate13_extension_second["bounded_or_finite_quasiperiodic"]["status"] != "OBSTRUCTED" or candidate13_extension_second["smooth_secular"]["status"] != "CERTIFIED" or candidate13_extension_second["causal_retarded"]["status"] != "NO_CERTIFIED_MAP":
        raise AssertionError("candidate-13 mixed correction classes changed")
    if "bounded-obstructed and smoothly second-order extendible" not in candidate13_extension["claim_boundary"] or "not the full candidate-13 mixed cone" not in candidate13_extension["claim_boundary"]:
        raise AssertionError("candidate-13 mixed extension exceeded scope")
    finite_zero = by_id["einstein.ph.wm.interaction.finite_generic_bounded_zero_block"]
    finite_zero_second = finite_zero["mode_data"]["second_order"]
    if finite_zero["descriptions"]["nonlinear"] != "CERTIFIED":
        raise AssertionError("finite-generic bounded zero-block lifecycle changed")
    if finite_zero["mode_data"]["taub_maps"]["status"] != "CERTIFIED" or "circle pressure" not in finite_zero["mode_data"]["taub_maps"]["statement"]:
        raise AssertionError("finite-generic pressure receiver was hidden")
    if finite_zero_second["bounded_or_finite_quasiperiodic"]["status"] != "CERTIFIED" or "R_c=0" not in finite_zero_second["bounded_or_finite_quasiperiodic"]["statement"]:
        raise AssertionError("finite-generic bounded zero-block theorem was hidden")
    if finite_zero_second["causal_retarded"]["status"] != "NO_CERTIFIED_MAP" or "nonzero-frequency resonances are excluded" not in finite_zero["claim_boundary"]:
        raise AssertionError("finite-generic zero-block scope was exceeded")
    candidate13_cone = by_id["einstein.ph.wm.interaction.ell2_two_abs_momentum_candidate13_complete_mixed_cone"]
    candidate13_cone_second = candidate13_cone["mode_data"]["second_order"]
    if candidate13_cone["descriptions"]["nonlinear"] != "CERTIFIED" or "complete finite generic candidate-13" not in candidate13_cone["mode_data"]["dispersion"]["statement"]:
        raise AssertionError("candidate-13 complete cone scope changed")
    if candidate13_cone["mode_data"]["taub_maps"]["status"] != "CERTIFIED" or "exactly the five stabilizers plus circle pressure" not in candidate13_cone["mode_data"]["taub_maps"]["statement"]:
        raise AssertionError("candidate-13 complete zero-block theorem was hidden")
    if candidate13_cone["mode_data"]["resonance"]["status"] != "CERTIFIED" or "18-coefficient prime" not in candidate13_cone["mode_data"]["resonance"]["statement"]:
        raise AssertionError("candidate-13 complete resonance theorem was hidden")
    if candidate13_cone_second["bounded_or_finite_quasiperiodic"]["status"] != "CERTIFIED" or "exactly {0}" not in candidate13_cone_second["bounded_or_finite_quasiperiodic"]["statement"] or candidate13_cone_second["smooth_secular"]["status"] != "CERTIFIED" or candidate13_cone_second["causal_retarded"]["status"] != "NO_CERTIFIED_MAP":
        raise AssertionError("candidate-13 complete correction classes changed")
    if "complete real bounded-origin" not in candidate13_cone["claim_boundary"] or "complex zero variety" not in candidate13_cone["claim_boundary"]:
        raise AssertionError("candidate-13 complete cone boundary changed")
    separator = by_id["einstein.ph.wm.interaction.candidate13_scalar_separation_no_go"]
    separator_second = separator["mode_data"]["second_order"]
    if separator["descriptions"]["nonlinear"] != "OBSTRUCTED" or "strictly positive occupation coefficient" not in separator["mode_data"]["taub_maps"]["statement"]:
        raise AssertionError("candidate-13 scalar separator was hidden")
    if separator["mode_data"]["resonance"]["status"] != "NOT_APPLICABLE" or separator_second["bounded_or_finite_quasiperiodic"]["status"] != "OBSTRUCTED" or separator_second["causal_retarded"]["status"] != "NO_CERTIFIED_MAP":
        raise AssertionError("candidate-13 scalar separator exceeded scope")
    l3 = by_id["einstein.ph.wm.interaction.ell2_two_abs_momentum_nonaxisymmetric_l3_matrix"]
    l3_second = l3["mode_data"]["second_order"]
    if l3["descriptions"]["nonlinear"] != "OBSTRUCTED" or "All 44 target-adjoint coefficients" not in l3["mode_data"]["resonance"]["statement"]:
        raise AssertionError("nonaxisymmetric L3 obstruction was hidden")
    if "multiplicity-one V3 carrier" not in l3["scope"]["m"] or "twelve nonaxisymmetric L1 coefficients" not in l3["claim_boundary"]:
        raise AssertionError("nonaxisymmetric L3 scope was merged")
    if l3["mode_data"]["taub_maps"]["status"] != "NOT_APPLICABLE" or l3_second["bounded_or_finite_quasiperiodic"]["status"] != "OBSTRUCTED" or l3_second["smooth_secular"]["status"] != "OPEN" or l3_second["causal_retarded"]["status"] != "NO_CERTIFIED_MAP":
        raise AssertionError("nonaxisymmetric L3 correction classes changed")
    aligned_phase = by_id["einstein.ph.wm.interaction.twist_aligned_opposite_momentum_resonance_gate"]
    aligned_phase_second = aligned_phase["mode_data"]["second_order"]
    if aligned_phase["descriptions"]["nonlinear"] != "OPEN":
        raise AssertionError("twist-aligned phase gate over-promoted the bounded cone")
    if aligned_phase["mode_data"]["taub_maps"]["status"] != "CERTIFIED":
        raise AssertionError("twist-aligned common-zero witness was hidden")
    if aligned_phase["mode_data"]["resonance"]["status"] != "CERTIFIED" or "does not import the later dynamical matrix" not in aligned_phase["mode_data"]["resonance"]["statement"]:
        raise AssertionError("twist-aligned phase divisor was not fail-closed")
    if aligned_phase_second["bounded_or_finite_quasiperiodic"]["status"] != "OPEN" or aligned_phase_second["smooth_secular"]["status"] != "CERTIFIED":
        raise AssertionError("twist-aligned correction-class split changed")
    if aligned_phase_second["causal_retarded"]["status"] != "NO_CERTIFIED_MAP":
        raise AssertionError("twist-aligned causal lifecycle was over-promoted")
    symbolic_self = by_id["einstein.ph.wm.interaction.symbolic_ell_qminus_self_collision"]
    symbolic_second = symbolic_self["mode_data"]["second_order"]
    if symbolic_self["descriptions"]["nonlinear"] != "OPEN":
        raise AssertionError("symbolic-ell shell arithmetic over-promoted bounded extension")
    if symbolic_self["mode_data"]["resonance"]["status"] != "CERTIFIED" or "unique q-minus self-product collision" not in symbolic_self["mode_data"]["resonance"]["statement"]:
        raise AssertionError("symbolic-ell collision uniqueness was hidden")
    if symbolic_second["bounded_or_finite_quasiperiodic"]["status"] != "OPEN" or symbolic_second["smooth_secular"]["status"] != "CERTIFIED":
        raise AssertionError("symbolic-ell correction-class boundary changed")
    if symbolic_second["causal_retarded"]["status"] != "NO_CERTIFIED_MAP":
        raise AssertionError("symbolic-ell collision row gained a causal map")
    symbolic_axial = by_id["einstein.ph.wm.interaction.symbolic_ell_axial_qminus_obstruction"]
    symbolic_axial_second = symbolic_axial["mode_data"]["second_order"]
    if symbolic_axial["descriptions"]["nonlinear"] != "OBSTRUCTED":
        raise AssertionError("symbolic-ell axial bounded obstruction was hidden")
    if symbolic_axial["mode_data"]["taub_maps"]["status"] != "CERTIFIED":
        raise AssertionError("symbolic-ell axial common-zero witness was hidden")
    if symbolic_axial["mode_data"]["resonance"]["status"] != "CERTIFIED" or "strictly positive" not in symbolic_axial["mode_data"]["resonance"]["statement"]:
        raise AssertionError("symbolic-ell axial source coefficient was hidden")
    if symbolic_axial_second["bounded_or_finite_quasiperiodic"]["status"] != "OBSTRUCTED" or symbolic_axial_second["smooth_secular"]["status"] != "CERTIFIED":
        raise AssertionError("symbolic-ell axial correction-class split changed")
    if symbolic_axial_second["causal_retarded"]["status"] != "NO_CERTIFIED_MAP":
        raise AssertionError("symbolic-ell axial obstruction gained a causal map")
    symbolic_parity = by_id["einstein.ph.wm.interaction.symbolic_ell_qminus_parity_resonance_matrix"]
    symbolic_parity_second = symbolic_parity["mode_data"]["second_order"]
    if symbolic_parity["mode_data"]["resonance"]["status"] != "CERTIFIED" or "two coordinate planes plus two nonzero mixed-parity sheets" not in symbolic_parity["mode_data"]["resonance"]["statement"]:
        raise AssertionError("symbolic-ell two-parity null variety was hidden")
    if symbolic_parity["descriptions"]["nonlinear"] != "OPEN" or symbolic_parity_second["bounded_or_finite_quasiperiodic"]["status"] != "OPEN":
        raise AssertionError("symbolic-ell null sheets were over-promoted")
    if symbolic_parity_second["smooth_secular"]["status"] != "CERTIFIED" or symbolic_parity_second["causal_retarded"]["status"] != "NO_CERTIFIED_MAP":
        raise AssertionError("symbolic-ell two-parity correction classes changed")
    standard_census = by_id["einstein.ph.wm.interaction.symbolic_ell_standard_branch_collision_census"]
    standard_second = standard_census["mode_data"]["second_order"]
    if standard_census["mode_data"]["resonance"]["status"] != "CERTIFIED" or "Every q-plus-involving" not in standard_census["mode_data"]["resonance"]["statement"]:
        raise AssertionError("symbolic standard-branch census was hidden")
    if standard_census["descriptions"]["nonlinear"] != "OPEN" or standard_second["bounded_or_finite_quasiperiodic"]["status"] != "OPEN":
        raise AssertionError("symbolic standard-branch census over-promoted bounded extension")
    if standard_second["smooth_secular"]["status"] != "CERTIFIED" or standard_second["causal_retarded"]["status"] != "NO_CERTIFIED_MAP":
        raise AssertionError("symbolic standard-branch correction classes changed")
    mixed_sheet = by_id["einstein.ph.wm.interaction.symbolic_ell_mixed_sheet_bounded_extension"]
    mixed_sheet_second = mixed_sheet["mode_data"]["second_order"]
    if mixed_sheet["descriptions"]["nonlinear"] != "CERTIFIED" or mixed_sheet_second["bounded_or_finite_quasiperiodic"]["status"] != "CERTIFIED":
        raise AssertionError("symbolic mixed-sheet bounded jets were hidden")
    if mixed_sheet["mode_data"]["taub_maps"]["status"] != "CERTIFIED" or mixed_sheet["mode_data"]["resonance"]["status"] != "CERTIFIED":
        raise AssertionError("symbolic mixed-sheet compatibility join changed")
    if mixed_sheet_second["causal_retarded"]["status"] != "NO_CERTIFIED_MAP" or "all-orders integration" not in mixed_sheet["claim_boundary"]:
        raise AssertionError("symbolic mixed-sheet higher lifecycle was over-promoted")
    tuned_cone = by_id["einstein.ph.wm.interaction.symbolic_ell_tuned_axisymmetric_bounded_cone"]
    tuned_second = tuned_cone["mode_data"]["second_order"]
    if tuned_cone["descriptions"]["nonlinear"] != "CERTIFIED" or tuned_second["bounded_or_finite_quasiperiodic"]["status"] != "CERTIFIED":
        raise AssertionError("symbolic tuned bounded cone was hidden")
    if "sharp" not in tuned_cone["mode_data"]["taub_maps"]["statement"] or "multiple |k|" not in tuned_cone["claim_boundary"]:
        raise AssertionError("symbolic tuned cone boundary changed")
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
    parity_matrix = by_id["einstein.ph.wm.interaction.opposite_momentum_ell2_parity_resonance_matrix"]
    parity_second = parity_matrix["mode_data"]["second_order"]
    if parity_matrix["mode_data"]["resonance"]["status"] != "CERTIFIED":
        raise AssertionError("two-parity L4 resonance matrix was hidden")
    if parity_matrix["descriptions"]["nonlinear"] != "OPEN" or parity_second["bounded_or_finite_quasiperiodic"]["status"] != "OPEN":
        raise AssertionError("mixed L4 null face was over-promoted")
    if parity_second["smooth_secular"]["status"] != "CERTIFIED" or parity_second["causal_retarded"]["status"] != "NO_CERTIFIED_MAP":
        raise AssertionError("two-parity correction classes changed")
    mixed_bounded = by_id["einstein.ph.wm.interaction.opposite_momentum_ell2_mixed_parity_bounded_extension"]
    mixed_bounded_second = mixed_bounded["mode_data"]["second_order"]
    if mixed_bounded["descriptions"]["nonlinear"] != "CERTIFIED":
        raise AssertionError("tuned mixed-parity bounded jet was not promoted")
    if mixed_bounded["mode_data"]["taub_maps"]["status"] != "CERTIFIED" or mixed_bounded["mode_data"]["resonance"]["status"] != "CERTIFIED":
        raise AssertionError("tuned mixed-parity proof inputs were hidden")
    if mixed_bounded_second["bounded_or_finite_quasiperiodic"]["status"] != "CERTIFIED":
        raise AssertionError("tuned mixed-parity bounded correction was hidden")
    if mixed_bounded_second["causal_retarded"]["status"] != "NO_CERTIFIED_MAP":
        raise AssertionError("tuned mixed-parity row gained an uncertified causal map")
    tuned_cone = by_id["einstein.ph.wm.interaction.opposite_momentum_ell2_tuned_axisymmetric_bounded_cone"]
    tuned_cone_second = tuned_cone["mode_data"]["second_order"]
    if tuned_cone["descriptions"]["nonlinear"] != "CERTIFIED":
        raise AssertionError("complete tuned axisymmetric cone was hidden")
    if tuned_cone["mode_data"]["taub_maps"]["status"] != "CERTIFIED" or tuned_cone["mode_data"]["resonance"]["status"] != "CERTIFIED":
        raise AssertionError("tuned cone necessity data changed")
    if tuned_cone_second["bounded_or_finite_quasiperiodic"]["status"] != "CERTIFIED":
        raise AssertionError("tuned cone sufficiency was hidden")
    if tuned_cone_second["causal_retarded"]["status"] != "NO_CERTIFIED_MAP" or "Extra p-primary inputs" not in tuned_cone["claim_boundary"]:
        raise AssertionError("tuned cone boundary was over-promoted")
    all_primary = by_id["einstein.ph.wm.interaction.opposite_momentum_ell2_tuned_all_primary_bounded_cone"]
    all_primary_second = all_primary["mode_data"]["second_order"]
    if all_primary["descriptions"]["nonlinear"] != "CERTIFIED":
        raise AssertionError("tuned all-primary cone was hidden")
    if all_primary["mode_data"]["taub_maps"]["status"] != "CERTIFIED" or all_primary["mode_data"]["resonance"]["status"] != "CERTIFIED":
        raise AssertionError("all-primary necessity data changed")
    if all_primary_second["bounded_or_finite_quasiperiodic"]["status"] != "CERTIFIED":
        raise AssertionError("all-primary sufficiency was hidden")
    if all_primary_second["causal_retarded"]["status"] != "NO_CERTIFIED_MAP" or "multiple |k|" not in all_primary["claim_boundary"]:
        raise AssertionError("all-primary cone boundary was over-promoted")
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
