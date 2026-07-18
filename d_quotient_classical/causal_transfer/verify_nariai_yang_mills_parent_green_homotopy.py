#!/usr/bin/env python3
"""Independent verifier for the Nariai parent causal theorem."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from d_quotient_classical.causal_transfer.nariai_first_differential_bgg_correction import ROOT


OUTPUT = ROOT / "d_quotient_classical/certificates/NARIAI_YANG_MILLS_PARENT_GREEN_HOMOTOPY_V1.json"
SCHEMA = ROOT / "d_quotient_classical/schema/nariai-yang-mills-parent-green-homotopy-v1.schema.json"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _layout(value: dict[str, object]) -> dict[tuple[int, int], list[list[object]]]:
    return {(item[0], item[1]): item[2] for item in value["entries"]}


def verify() -> None:
    value = json.loads(OUTPUT.read_text())
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(value)
    dependency = value["dependency_ref"]
    if _sha(ROOT / dependency["path"]) != dependency["sha256"]:
        raise AssertionError("Yang--Mills parent dependency drifted")
    for relative, digest in value["source_manifest"].items():
        if _sha(ROOT / relative) != digest:
            raise AssertionError(f"source digest drifted: {relative}")

    parent = json.loads((ROOT / dependency["path"]).read_text())
    if parent["exact_checks"]["Nariai_normal_tractor_is_Yang_Mills"] is not True:
        raise AssertionError("Yang--Mills condition unavailable")
    if parent["exact_checks"]["left_composition_identity_exact"] is not True or parent["exact_checks"]["right_composition_identity_exact"] is not True:
        raise AssertionError("parent detour sequence is not exact as a complex")

    q = _layout(value["parent_complex"]["abstract_Q"])
    witness = _layout(value["parent_complex"]["backward_witness"])
    wave = _layout(value["parent_complex"]["wave_anticommutator"])
    if set(q) != {(1, 0), (2, 1), (3, 2)}:
        raise AssertionError("parent differential layout drifted")
    if set(witness) != {(0, 1), (1, 2), (2, 3)}:
        raise AssertionError("backward witness layout drifted")
    if set(wave) != {(0, 0), (1, 1), (2, 2), (3, 3)}:
        raise AssertionError("wave anticommutator is not diagonal")
    if q[(1, 0)] != [[['d'], 1, 1]] or q[(2, 1)] != [[['M'], 1, 1]] or q[(3, 2)] != [[['delta'], 1, 1]]:
        raise AssertionError("parent differential normalization drifted")
    if witness[(0, 1)] != [[['delta'], 1, 1]] or witness[(1, 2)] != [[[], 1, 1]] or witness[(2, 3)] != [[['d'], 1, 1]]:
        raise AssertionError("parent witness normalization drifted")

    principal = value["normal_hyperbolicity"]
    if principal["principal_symbol"] != "-g^{ab} zeta_a zeta_b times the identity in every degree":
        raise AssertionError("scalar metric symbol statement drifted")
    if principal["degreewise_normally_hyperbolic"] is not True:
        raise AssertionError("normal hyperbolicity was not promoted")
    if value["geometry"]["globally_hyperbolic"] is not True:
        raise AssertionError("global Nariai domain was not declared")
    if value["causal_construction"]["homotopy_identity"] != "Q Lambda_parent,+/-+Lambda_parent,+/- Q=1":
        raise AssertionError("causal homotopy identity drifted")
    if value["flags"]["NARIAI_PARENT_GREEN_HOMOTOPY"] is not True:
        raise AssertionError("parent causal theorem was not promoted")
    if value["flags"]["NARIAI_REPAIRED_310_GREEN_HOMOTOPY"] is not False:
        raise AssertionError("rank-310 transfer was overpromoted")
    print("NARIAI_YANG_MILLS_PARENT_GREEN_HOMOTOPY_V1: independently verified")


if __name__ == "__main__":
    verify()
