#!/usr/bin/env python3
"""Independent consumer for the candidate-13 category obstruction."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp

from d_quotient_classical.causal_transfer.nariai_first_differential_bgg_correction import ROOT


OUTPUT = ROOT / "d_quotient_classical/certificates/CANDIDATE13_REDUCED_SOURCE_SUPPORT_LOCAL_UPGRADE_OBSTRUCTION_V1.json"
SCHEMA = ROOT / "d_quotient_classical/schema/candidate13-reduced-source-support-local-upgrade-obstruction-v1.schema.json"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _support(vector: sp.Matrix) -> list[int]:
    return [index for index, value in enumerate(vector) if value != 0]


def verify() -> None:
    value = json.loads(OUTPUT.read_text())
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(value)
    for ref in value["dependency_refs"].values():
        if _sha(ROOT / ref["path"]) != ref["sha256"]:
            raise AssertionError(f"dependency drifted: {ref['artifact_id']}")
    for relative, digest in value["source_manifest"].items():
        if _sha(ROOT / relative) != digest:
            raise AssertionError(f"source drifted: {relative}")
    crosswalk_ref = value["dependency_refs"]["candidate13_derived_source"]
    crosswalk = json.loads((ROOT / crosswalk_ref["path"]).read_text())
    if not crosswalk["classification"]["bounded_derived_source_pullback_is_origin"]:
        raise AssertionError("bounded-origin refinement is not certified")
    if crosswalk["derived_source_pullback"]["CAUSAL_RETARDED"]["status"] != "NO_CERTIFIED_MAP":
        raise AssertionError("causal candidate-13 crosswalk was promoted")

    one = sp.ones(3, 1)
    mode = sp.Matrix([1, 2, 3])
    local = sp.Matrix([1, 0, 0])
    for projector in (one * one.T / 3, mode * mode.T / mode.dot(mode)):
        if projector * projector != projector:
            raise AssertionError("independent projector replay failed")
        if _support(projector * local) != [0, 1, 2]:
            raise AssertionError("support witness disappeared")
    if value["flags"]["ALTERNATIVE_LOCAL_COFIBER_GLOBALLY_OBSTRUCTED"] is not False:
        raise AssertionError("scoped obstruction was overgeneralized")
    if value["category_disposition"]["candidate13_bounded_pullback"] != "CERTIFIED_REDUCED_MODE_ORIGIN_ONLY":
        raise AssertionError("bounded pullback category drifted")
    print("CANDIDATE13_REDUCED_SOURCE_SUPPORT_LOCAL_UPGRADE_OBSTRUCTION_V1: independently verified")


if __name__ == "__main__":
    verify()
