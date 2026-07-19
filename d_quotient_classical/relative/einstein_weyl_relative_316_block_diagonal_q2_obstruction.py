#!/usr/bin/env python3
"""Certify the projected q2 obstruction on the block-diagonal 316-row carrier."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
RESULT_ID = "EINSTEIN_WEYL_RELATIVE_316_BLOCK_DIAGONAL_Q2_OBSTRUCTION_V1"
OUTPUT = ROOT / f"d_quotient_classical/certificates/{RESULT_ID}.json"
REPORT = ROOT / "d_quotient_classical/reports/einstein-weyl-relative-316-block-diagonal-q2-obstruction.md"
SCHEMA = ROOT / "d_quotient_classical/schema/relative-316-block-diagonal-q2-obstruction-v1.schema.json"
VERIFIER = ROOT / "d_quotient_classical/relative/verify_einstein_weyl_relative_316_block_diagonal_q2_obstruction.py"
TESTS = ROOT / "d_quotient_classical/relative/tests/test_einstein_weyl_relative_316_block_diagonal_q2_obstruction.py"
DEPENDENCIES = {
    "cotangent_completion": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_316_ROW_COTANGENT_COMPLETION_V1.json",
    "direct_f2_obstruction": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_F2_TAUB_OBSTRUCTION_V1.json",
    "current_cofiber_assembly": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_CURRENT_COFIBER_ASSEMBLY_V1.json",
    "five_current_q2": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_FIVE_CURRENT_DE_RHAM_Q2_V1.json",
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def _artifact(path: Path, payload: dict[str, Any]) -> dict[str, str]:
    return {"artifact_id": str(payload.get("result_id", payload.get("schema"))), "path": str(path.relative_to(ROOT)), "sha256": _sha(path)}


def build() -> dict[str, Any]:
    deps = {name: _load(path) for name, path in DEPENDENCIES.items()}
    completion = deps["cotangent_completion"]
    obstruction = deps["direct_f2_obstruction"]
    assembly = deps["current_cofiber_assembly"]
    if not completion["classification"]["canonical_316_row_unary_cyclic_carrier_exists"]:
        raise AssertionError("316-row unary carrier changed")
    if obstruction["taub_pairing"]["relative_half_delta2_pairing"] != "-54*(1 + sqrt(3))/5":
        raise AssertionError("Taub witness changed")
    if not assembly["classification"]["direct_f2_obstruction_preserved"]:
        raise AssertionError("block projection theorem changed")
    return {
        "schema": "pure-weyl-relative-316-block-diagonal-q2-obstruction-v1",
        "result_id": RESULT_ID,
        "result_state": "BLOCK_DIAGONAL_316_ROW_UNARY_CARRIER_CANNOT_SUPPORT_THE_FULL_DOMAIN_RELATIVE_Q2",
        "lifecycle_status": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "scope": completion["scope"],
        "dependencies": {name: _artifact(path, deps[name]) for name, path in DEPENDENCIES.items()},
        "projection_argument": {
            "unary_split": "q_316=q_current direct_sum q_C direct_sum (-q_C^sharp)",
            "projection": "p_W kills the current and cotangent summands and projects q_C to the Weyl target",
            "projected_arity_two_equation": "q1_W f2 + f2(q1_E,.) + (-1)^|.| f2(.,q1_E) = -Delta2",
            "current_or_cotangent_output_projects_to_zero": True,
            "projected_equation_is_the_certified_direct_f2_problem": True,
            "normalized_nonzero_witness": "-54*(1 + sqrt(3))/5",
            "conclusion": "a q2 on the block-diagonal 316-row carrier with the declared Einstein and Weyl restrictions would induce the impossible full-domain direct f2",
        },
        "classification": {
            "unary_316_cyclic_carrier_retained": True,
            "complete_full_domain_q2_on_block_diagonal_316_exists": False,
            "current_q2_interface_demoted": False,
            "derived_taub_zero_homotopy_pullback_obstructed": False,
            "nonzero_typed_unary_cross_incidence_obstructed": False,
            "modified_endpoint_or_background_obstructed": False,
            "causal_or_quantum_claim": False,
        },
        "admissible_successors": [
            "replace the block direct sum by a genuine derived Taub-zero homotopy pullback",
            "add a nonzero typed unary cross-incidence whose Weyl projection can absorb the defect",
            "modify the unary endpoint map or work on a background where the direct f2 witness vanishes"
        ],
        "next_gate": "CONSTRUCT_THE_DERIVED_TAUB_ZERO_HOMOTOPY_PULLBACK_OR_EMIT_ITS_FIRST_TYPED_UNARY_INCIDENCE_OBSTRUCTION",
        "provenance": {
            "source_manifest": {str(path.relative_to(ROOT)): _sha(path) for path in (Path(__file__).resolve(), VERIFIER, TESTS, SCHEMA)},
            "verification_commands": [
                "PYTHONPATH=. python3 -m d_quotient_classical.relative.einstein_weyl_relative_316_block_diagonal_q2_obstruction --check --guards",
                "PYTHONPATH=. python3 -m d_quotient_classical.relative.verify_einstein_weyl_relative_316_block_diagonal_q2_obstruction",
                "python3 -m unittest d_quotient_classical.relative.tests.test_einstein_weyl_relative_316_block_diagonal_q2_obstruction"
            ]
        },
        "claim_boundary": "This theorem obstructs only a complete full-domain relative q2 on the selected 316-row carrier while its unary operator remains block diagonal between the relative cone, its cotangent dual and the five-current resolution. Projection to the Weyl target reproduces the independently certified nonzero direct-f2 Taub witness, so neither a current-valued nor a cotangent-valued q2 output can cancel it. The exact unary cyclic carrier and scoped 188-row current q2 interface remain certified. The theorem does not obstruct a genuine derived Taub-zero homotopy pullback, a nonzero typed unary cross-incidence, a modified endpoint or background, causal propagation, observables, particles or quantum states.",
    }


def validate(value: dict[str, Any]) -> None:
    schema = _load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)


def _render(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def _report() -> str:
    return r"""# Projected q2 obstruction on the 316-row block carrier

The canonical cotangent completion repairs the unary cyclic carrier, but its
declared differential remains a direct sum between the current resolution,
the relative cone and the cone's cotangent dual.  Projecting an arity-two
identity to the Weyl target kills every current-valued and cotangent-valued
output.  What remains is exactly the old relative morphism equation

\[
q_{1,W}f_2+f_2(q_{1,E},\cdot)+(-1)^{|\cdot|}f_2(\cdot,q_{1,E})=-\Delta_2.
\]

The certified Taub functional evaluates its obstruction class to

\[
-\frac{54}{5}(1+\sqrt3)\ne0.
\]

Therefore no complete full-domain q2 with the declared source and target
restrictions exists on the block-diagonal 316-row unary carrier.  The unary
carrier and the scoped physical/current q2 theorem are unaffected.  The next
admissible construction must change the chain architecture: a derived
Taub-zero homotopy pullback, a nonzero typed unary cross-incidence, or a
different endpoint/background.
"""


def _guards(value: dict[str, Any]) -> None:
    for key in ("complete_full_domain_q2_on_block_diagonal_316_exists", "derived_taub_zero_homotopy_pullback_obstructed", "nonzero_typed_unary_cross_incidence_obstructed", "modified_endpoint_or_background_obstructed", "causal_or_quantum_claim"):
        mutant = deepcopy(value)
        mutant["classification"][key] = True
        try:
            validate(mutant)
        except Exception:
            continue
        raise AssertionError(f"mutation guard accepted classification.{key}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    value = build()
    validate(value)
    if args.write:
        OUTPUT.write_text(_render(value))
        REPORT.write_text(_report())
    if args.check and (OUTPUT.read_text() != _render(value) or REPORT.read_text() != _report()):
        raise AssertionError("316-row q2 obstruction outputs drifted")
    if args.guards:
        _guards(value)
    print(f"{RESULT_ID}: PASS")


if __name__ == "__main__":
    main()
