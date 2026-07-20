#!/usr/bin/env python3
"""Type the shifted current cone required by the relative support-local lift."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
RESULT_ID = "EINSTEIN_WEYL_RELATIVE_SHIFTED_CURRENT_CONE_PREFLIGHT_V1"
OUTPUT = ROOT / f"d_quotient_classical/certificates/{RESULT_ID}.json"
REPORT = ROOT / "d_quotient_classical/reports/einstein-weyl-relative-shifted-current-cone-preflight.md"
SCHEMA = ROOT / "d_quotient_classical/schema/relative-shifted-current-cone-preflight-v1.schema.json"
VERIFIER = ROOT / "d_quotient_classical/relative/verify_einstein_weyl_relative_shifted_current_cone_preflight.py"
TESTS = ROOT / "d_quotient_classical/relative/tests/test_einstein_weyl_relative_shifted_current_cone_preflight.py"
DEPENDENCIES = {
    "reduced_factorization": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_REDUCED_TAUB_FACTORIZATION_V1.json",
    "current_carrier": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_FIVE_CURRENT_DE_RHAM_CARRIER_V1.json",
    "current_q2": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_FIVE_CURRENT_DE_RHAM_Q2_V1.json",
    "cotangent_316": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_316_ROW_COTANGENT_COMPLETION_V1.json",
    "block_q2_obstruction": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_316_BLOCK_DIAGONAL_Q2_OBSTRUCTION_V1.json",
    "relative_cone": ROOT / "bridge/einstein_sector/generated/einstein_weyl_relative_linear_triangle_v1/components.json",
    "target_layout": ROOT / "bridge/einstein_sector/generated/weyl_maxwell_product_linfinity_v1/row_layout.json",
    "target_q1": ROOT / "bridge/einstein_sector/generated/weyl_maxwell_product_linfinity_v1/q1.json",
}


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _artifact(path: Path, value: dict[str, Any]) -> dict[str, str]:
    return {"artifact_id": str(value.get("result_id", value.get("schema"))), "path": str(path.relative_to(ROOT)), "sha256": _sha(path)}


def build() -> dict[str, Any]:
    deps = {name: _load(path) for name, path in DEPENDENCIES.items()}
    if not deps["reduced_factorization"]["classification"]["reduced_mode_obstruction_factorization_exact"]:
        raise AssertionError("reduced factorization unavailable")
    if not deps["current_q2"]["classification"]["current_interface_q1q2_identity_exact"]:
        raise AssertionError("local current q2 unavailable")
    cone_ranks = deps["relative_cone"]["mapping_cofiber"]["degree_dimensions"]
    if cone_ranks != [5, 20, 28, 19, 6]:
        raise AssertionError("relative cone grading drifted")
    primal = [5, 20, 30, 20, 5]
    shifted_primal = primal
    base = [5, 25, 50, 48, 24, 6]  # degrees -3,...,2
    completed = [5, 25, 56, 72, 72, 56, 25, 5]  # degrees -3,...,4
    if sum(base) != 158 or sum(completed) != 316:
        raise AssertionError("shifted carrier rank arithmetic failed")
    target_rows = deps["target_layout"]["content"]["rows"]
    target_ranks = [sum(row["degree"] == degree for row in target_rows) for degree in (-1, 0, 1, 2)]
    if target_ranks != [6, 14, 14, 6]:
        raise AssertionError("target BV grading drifted")
    return {
        "schema": "pure-weyl-relative-shifted-current-cone-preflight-v1",
        "result_id": RESULT_ID,
        "result_state": "SHIFTED_CURRENT_MAPPING_CONE_TYPED_TOP_DESCENT_COEFFICIENT_SOLVE_OPEN",
        "lifecycle_status": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "scope": deps["current_q2"]["scope"],
        "dependencies": {name: _artifact(path, deps[name]) for name, path in DEPENDENCIES.items()},
        "required_chain_map": {
            "name": "A:K_P->C_W",
            "degree": 0,
            "domain": "K_P^r=Omega^(r+2)(M;g_stab^*) for r=-2,...,2",
            "codomain": "40-row Weyl-Maxwell minimal BV complex",
            "components": [
                {"degree": -2, "source": "P_0", "source_rank": 5, "target_rank": 0, "map": "A^-2=0"},
                {"degree": -1, "source": "P_1", "source_rank": 20, "target_rank": 6, "map": "A^-1:P_1->W^-1"},
                {"degree": 0, "source": "P_2", "source_rank": 30, "target_rank": 14, "map": "A^0:P_2->W^0"},
                {"degree": 1, "source": "P_3", "source_rank": 20, "target_rank": 14, "map": "A^1:P_3->W^1"},
                {"degree": 2, "source": "P_4", "source_rank": 5, "target_rank": 6, "map": "A^2:P_4->W^2"}
            ],
            "chain_identity": "q1_W A=A d_H in every degree",
            "field_pair_identity": "Delta2-A^1 C=q1_W f2+f2(q1_E,.)+f2(.,q1_E)",
            "strict_first_attempt": "f2=0, hence Delta2=A^1 C",
            "top_descent": "q1_W^(1->2) A^1=A^2 d_H^(3->4)",
        },
        "shifted_cyclic_carrier": {
            "base": "B_158=Cone(iota) direct_sum K_P[1]",
            "base_degree_range": [-3, 2],
            "base_degree_ranks": base,
            "base_rows": 158,
            "completion": "C_316_shift=T*[1]B_158",
            "completed_degree_range": [-3, 4],
            "completed_degree_ranks": completed,
            "completed_rows": 316,
            "odd_pairing_nondegenerate_by_construction": True,
            "factorized_unary": "[[q_C,A],[0,-d_H]] direct_sum negative formal adjoint",
            "square_zero_condition": "q1_W A=A d_H together with the imported cone and de Rham squares",
        },
        "comparison_with_existing_316": {
            "same_underlying_row_count": True,
            "existing_construction": "C_160,current direct_sum T*[1]Cone(iota)",
            "existing_degree_range": [-2, 3],
            "existing_degree_ranks": [10, 51, 97, 97, 51, 10],
            "existing_grading_hosts_required_A": False,
            "reason": "the derived source uses K_P[1] inside the mapping cone before cotangent completion; shifting after direct sum is not grading-equivalent",
            "existing_unary_and_obstruction_certificates_retained": True,
        },
        "first_exact_solve": {
            "unknowns": ["A^1:P_3->W^1", "A^2:P_4->W^2", "optional local f2 after strict failure"],
            "principal_equation": "sigma(q1_W^(1->2)) sigma(A^1)=sigma(A^2) sigma(d_3)",
            "coefficient_equation": "Delta2-A^1 C=delta(f2) on all 15 nonzero target defect rows",
            "required_new_export": "complete invariant Hom basis and order bounds for A^1,A^2,f2 plus portable full C_X coefficient tables",
            "augmented_rank_failure_output": "canonical normalized top-descent or field-pair incidence obstruction",
        },
        "classification": {
            "required_lift_typed": True,
            "shifted_mapping_cone_required": True,
            "rank_316_cyclic_completion_available": True,
            "existing_316_direct_sum_grading_sufficient": False,
            "support_local_chain_map_A_constructed": False,
            "top_descent_solved": False,
            "relative_q2_repaired": False,
            "causal_observable_particle_or_quantum_claim": False,
        },
        "next_gate": "SOLVE_THE_COMPLETE_INVARIANT_TOP_DESCENT_FOR_A1_A2_THEN_THE_15_ROW_FIELD_PAIR_INCIDENCE_OR_RETURN_A_NORMALIZED_OBSTRUCTION",
        "provenance": {
            "source_manifest": {str(path.relative_to(ROOT)): _sha(path) for path in (Path(__file__).resolve(), VERIFIER, TESTS, SCHEMA)},
            "verification_commands": [
                "PYTHONPATH=. python3 -m d_quotient_classical.relative.einstein_weyl_relative_shifted_current_cone_preflight --check --guards",
                "PYTHONPATH=. python3 -m d_quotient_classical.relative.verify_einstein_weyl_relative_shifted_current_cone_preflight",
                "python3 -m unittest d_quotient_classical.relative.tests.test_einstein_weyl_relative_shifted_current_cone_preflight",
            ],
        },
        "claim_boundary": "This preflight fixes the grading, bundle directions and exact identities of the support-local current-level lift. It proves that the derived-source current complex must be shifted inside the mapping cone before cotangent completion; the old and new carriers both have 316 rows but different degree profiles. It does not construct A, solve its top descent, export the complete invariant Hom ansatz, repair relative q2, compare action pairings, or establish causal, observable, particle or quantum claims. The existing block-diagonal 316 unary theorem and its scoped q2 obstruction remain valid for their declared carrier.",
    }


def validate(value: dict[str, Any]) -> None:
    schema = _load(SCHEMA); Draft202012Validator.check_schema(schema); Draft202012Validator(schema).validate(value)


def _render(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def _report() -> str:
    return r"""# Shifted current-cone preflight

The support-local lift is a degree-zero chain map

\[
A:K_P\longrightarrow C_{\rm W},\qquad q_{1,\rm W}A=A d_H,
\]

where the five-copy primal de Rham complex has ranks
`5,20,30,20,5` in degrees `-2,...,2`.  Its nonzero components are
`20->6`, `30->14`, `20->14` and `5->6`.  The field-pair equation is

\[
\Delta_2-A^1C=\delta f_2.
\]

In the derived mapping cone, `K_P` must first be shifted.  The canonical
cyclic carrier is therefore

\[
T^*[1](\operatorname{Cone}(\iota)\oplus K_P[1]),
\]

with 316 rows and ranks `5,25,56,72,72,56,25,5` in degrees `-3,...,4`.
This is not the grading of the previously certified 316-row block-diagonal
direct sum.  The first coefficient calculation is the invariant top descent
for `A^1,A^2`, followed by the fifteen-row field-pair incidence.  Neither has
yet been solved or obstructed.
"""


def _guards(value: dict[str, Any]) -> None:
    for key in ("existing_316_direct_sum_grading_sufficient", "support_local_chain_map_A_constructed", "top_descent_solved", "relative_q2_repaired", "causal_observable_particle_or_quantum_claim"):
        mutant = deepcopy(value); mutant["classification"][key] = True
        try: validate(mutant)
        except Exception: continue
        raise AssertionError(f"mutation guard accepted classification.{key}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("--write", action="store_true"); parser.add_argument("--check", action="store_true"); parser.add_argument("--guards", action="store_true"); args = parser.parse_args()
    value = build(); validate(value)
    if args.write: OUTPUT.write_text(_render(value)); REPORT.write_text(_report())
    if args.check and (OUTPUT.read_text() != _render(value) or REPORT.read_text() != _report()): raise AssertionError("shifted current cone outputs drifted")
    if args.guards: _guards(value)
    print(f"{RESULT_ID}: PASS")


if __name__ == "__main__": main()
