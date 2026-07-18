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

    crosswalk = by_id["einstein.crosswalk.compact_product_to_asymptotic_or_vacuum_cylinder"]
    if crosswalk["evidence"] or set(crosswalk["descriptions"].values()) != {"NO_CERTIFIED_MAP"}:
        raise AssertionError("cross-background fail-closed entry changed")


if __name__ == "__main__":
    verify()
    print("EINSTEIN_COMPACT_PRODUCT_RESIDUAL_ATLAS_FRAGMENT_V1 independent verification: PASS")
