#!/usr/bin/env python3
"""Independent consumer for the class-wide metric biwave homotopy."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp

from covariant_completion.minimal_witness.principal_symbols import MinimalWitnessPrincipalSymbols
from d_quotient_classical.causal_transfer.nariai_first_differential_bgg_correction import ROOT


OUTPUT = ROOT / "d_quotient_classical/certificates/BACH_FLAT_METRIC_BIWAVE_GREEN_HOMOTOPY_V1.json"
SCHEMA = ROOT / "d_quotient_classical/schema/bach-flat-metric-biwave-green-homotopy-v1.schema.json"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify() -> None:
    value = json.loads(OUTPUT.read_text())
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(value)
    for ref in value["dependency_refs"].values():
        if _sha(ROOT / ref["path"]) != ref["sha256"]:
            raise AssertionError(f"dependency drifted: {ref['artifact_id']}")
    for relative, digest in value["source_manifest"].items():
        if _sha(ROOT / relative) != digest:
            raise AssertionError(f"source drifted: {relative}")
    for ref in value["proof_artifacts"].values():
        if _sha(ROOT / ref["path"]) != ref["sha256"]:
            raise AssertionError(f"proof artifact drifted: {ref['path']}")

    principal = MinimalWitnessPrincipalSymbols.build()
    principal.verify()
    q4 = principal.covector_square**2
    if sp.simplify(principal.companion * principal.conformal_killing - q4 * sp.eye(4)) != sp.zeros(4):
        raise AssertionError("ghost biwave symbol failed")
    if sp.simplify(principal.bach + sp.Rational(1, 2) * principal.conformal_killing * principal.companion - sp.Rational(1, 2) * q4 * sp.eye(9)) != sp.zeros(9):
        raise AssertionError("metric biwave symbol failed")

    order = json.loads((ROOT / value["proof_artifacts"]["covariant_order_lemma"]["path"]).read_text())
    if order["claims"]["linearized_Bach_orders"] != [0, 1, 2, 4]:
        raise AssertionError("Bach order ledger drifted")
    if order["claims"]["third_order_absent"] is not True:
        raise AssertionError("order-three layer was not excluded")
    if value["flags"]["BACH_FLAT_RANK310_GREEN_HOMOTOPY_ON_CLASS"] is not False:
        raise AssertionError("downstream rank-310 transfer promoted prematurely")
    print("BACH_FLAT_METRIC_BIWAVE_GREEN_HOMOTOPY_V1: independently verified")


if __name__ == "__main__":
    verify()
