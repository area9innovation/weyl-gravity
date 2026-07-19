#!/usr/bin/env python3
"""Independent consumer for the finite-charge locality obstruction."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_FINITE_CHARGE_SUPPORT_LOCAL_LIFT_OBSTRUCTION_V1.json"
SCHEMA = ROOT / "d_quotient_classical/schema/relative-finite-charge-support-local-lift-obstruction-v1.schema.json"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify() -> dict:
    value = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    for relative, expected in value["provenance"]["source_manifest"].items():
        if _sha(ROOT / relative) != expected:
            raise AssertionError(f"source hash drifted: {relative}")
    dependencies = {}
    for name, artifact in value["dependencies"].items():
        path = ROOT / artifact["path"]
        if _sha(path) != artifact["sha256"]:
            raise AssertionError(f"dependency hash drifted: {artifact['path']}")
        dependencies[name] = json.loads(path.read_text())
    if dependencies["complete_charge_q2"]["operation"]["output_dimension"] != 5:
        raise AssertionError("charge dimension drifted")
    if dependencies["receiver_preflight"]["charge_fibre"]["dimension"] != 5:
        raise AssertionError("receiver dimension drifted")
    if dependencies["taub_descent"]["classification"]["gauge_descent_from_noether_identity"] is not True:
        raise AssertionError("Noether descent drifted")
    half = sp.sympify(dependencies["f2_obstruction"]["taub_pairing"]["relative_half_delta2_pairing"])
    full = sp.simplify(2 * half)
    witness = value["contradiction_witness"]
    if sp.simplify(sp.sympify(witness["half_diagonal_charge"]) - half) != 0:
        raise AssertionError("half-charge witness drifted")
    if sp.simplify(sp.sympify(witness["q2_diagonal_charge"]) - full) != 0 or full == 0:
        raise AssertionError("nonzero q2 witness replay failed")
    proof = value["support_locality_lemma"]["proof"]
    required = ("compactly supported output", "nonzero constant section", "finite jets", "B=0")
    joined = " ".join(proof)
    if any(text not in joined for text in required):
        raise AssertionError("support-locality proof ledger is incomplete")
    flags = value["classification"]
    if flags["direct_five_charge_support_local_lift_exists"] is not False:
        raise AssertionError("impossible direct lift promoted")
    if flags["local_noether_current_coefficients_exported"] is not False:
        raise AssertionError("unexported current promoted")
    return {"status": "PASS", "charge_dimension": 5, "q2_witness": str(sp.factor(full)), "direct_local_lift": False, "minimal_local_rows": ["horizontal_3_form_current", "horizontal_4_form_divergence"]}


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2, sort_keys=True))
