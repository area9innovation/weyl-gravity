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
    if abd["mode_data"]["resonance"]["status"] != "CERTIFIED" or abd["descriptions"]["nonlinear"] != "OPEN":
        raise AssertionError("a,b,d matrix lifecycle drifted")

    complete_matrix = by_id["einstein.ph.wm.interaction.homogeneous_twist_times_ell2_extra"]
    if complete_matrix["mode_data"]["resonance"]["status"] != "CERTIFIED":
        raise AssertionError("complete homogeneous/twist resonance matrix was lost")
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
    if "a-times-all and d-times-nonzero-k polynomial maps" not in standard_global["claim_boundary"]:
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

    crosswalk = by_id["einstein.crosswalk.compact_product_to_asymptotic_or_vacuum_cylinder"]
    if crosswalk["evidence"] or set(crosswalk["descriptions"].values()) != {"NO_CERTIFIED_MAP"}:
        raise AssertionError("cross-background fail-closed entry changed")


if __name__ == "__main__":
    verify()
    print("EINSTEIN_COMPACT_PRODUCT_RESIDUAL_ATLAS_FRAGMENT_V1 independent verification: PASS")
