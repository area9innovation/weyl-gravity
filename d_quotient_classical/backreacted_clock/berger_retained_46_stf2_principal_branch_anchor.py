#!/usr/bin/env python3
"""Certify the principal filtered branch anchor on the rank-46 STF2 carrier."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "d_quotient_classical/backreacted_clock"
RANK36 = ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_36_RESIDUAL_BRANCH_LOCAL_PROJECTOR_OBSTRUCTION_V1.json"
CARRIER = ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_46_STF2_PROLONGATION_BRANCH_CARRIER_V1.json"
SOLVER_CONTRACT = ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_46_STF2_BRANCH_PROJECTOR_SOLVER_CONTRACT_V1.json"
OUTPUT = ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_46_STF2_PRINCIPAL_BRANCH_ANCHOR_V1.json"
REPORT = ROOT / "d_quotient_classical/reports/berger-retained-46-stf2-principal-branch-anchor.md"
SCHEMA = ROOT / "d_quotient_classical/schema/berger-retained-46-stf2-principal-branch-anchor-v1.schema.json"
VERIFIER = HERE / "verify_berger_retained_46_stf2_principal_branch_anchor.py"
TESTS = HERE / "tests/test_berger_retained_46_stf2_principal_branch_anchor.py"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise ValueError(f"dependency is not an object: {path}")
    return value


def _dependency(path: Path, value: dict) -> dict[str, str]:
    return {
        "artifact_id": value["result_id"],
        "path": str(path.relative_to(ROOT)),
        "sha256": _sha256(path),
    }


def _dual_number_idempotents() -> list[list[str]]:
    a, b = sp.symbols("a b")
    solutions = sp.solve(
        [sp.expand(a * a - a), sp.expand((2 * a - 1) * b)],
        [a, b],
        dict=True,
    )
    return sorted([[str(item[a]), str(item[b])] for item in solutions])


def _dual_multiply(left: tuple[sp.Expr, sp.Expr], right: tuple[sp.Expr, sp.Expr]):
    return (
        sp.expand(left[0] * right[0]),
        sp.expand(left[0] * right[1] + left[1] * right[0]),
    )


def _input_checks(rank36: dict, carrier: dict, contract: dict) -> dict[str, bool]:
    audit = rank36.get("principal_filtered_module_audit", {})
    if (
        audit.get("algebra") != "Q(sqrt(10))[epsilon]/(epsilon^2)"
        or audit.get("only_trivial_idempotents") is not True
        or audit.get("solutions_a_b") != [["0", "0"], ["1", "0"]]
    ):
        raise ValueError("rank-36 principal filtered-module authority drifted")
    if (
        carrier.get("result_state")
        != "CERTIFIED_CYCLIC_GRAPH_CARRIER_PROJECTOR_OPEN"
        or carrier.get("flags", {}).get("CYCLIC_GRAPH_SDR_46_TO_36") is not True
        or carrier.get("graph_construction", {}).get("interpretation")
        != "exact cyclic graph prolongation with a contractible STF2 complement; not a branch projector"
        or not all(carrier.get("exact_checks", {}).values())
    ):
        raise ValueError("rank-46 graph-carrier boundary drifted")
    if (
        contract.get("result_state")
        != "SOLVER_CONTRACT_FROZEN_PROJECTOR_VERDICT_NOT_RUN"
        or contract.get("principal_symbol_anchor", {}).get("real_physical_helicity_rank_each")
        != 2
        or contract.get("claim_flags", {}).get("BRANCH_PROJECTOR_ACCEPTED")
        is not False
    ):
        raise ValueError("rank-46 solver-contract boundary drifted")
    return {
        "rank_36_dual_number_principal_module_imported": True,
        "rank_36_only_trivial_principal_idempotents_imported": True,
        "rank_46_graph_SDR_imported": True,
        "rank_46_added_complement_contractible": True,
        "rank_46_retained_cohomology_unchanged": True,
        "rank_46_solver_contract_imported": True,
        "physical_helicity_rank_two_imported": True,
    }


def build() -> dict:
    rank36 = _load(RANK36)
    carrier = _load(CARRIER)
    contract = _load(SOLVER_CONTRACT)
    checks = _input_checks(rank36, carrier, contract)
    solutions = _dual_number_idempotents()
    b = sp.symbols("b")
    # epsilon * (1+b epsilon) modulo epsilon^2.
    section_defect = _dual_multiply((0, sp.Integer(1)), (sp.Integer(1), b))
    if solutions != [["0", "0"], ["1", "0"]] or section_defect != (0, 1):
        raise ValueError("principal nonsplitting calculation drifted")
    sources = {
        str(path.relative_to(ROOT)): _sha256(path)
        for path in (Path(__file__).resolve(), VERIFIER, TESTS, SCHEMA)
    }
    return {
        "schema": "pure-weyl-berger-retained-46-stf2-principal-branch-anchor-v1",
        "result_id": "BERGER_RETAINED_46_STF2_PRINCIPAL_BRANCH_ANCHOR_V1",
        "result_state": "PRINCIPAL_DIRECT_SUM_ANCHOR_OBSTRUCTED_FILTERED_SUBPRINCIPAL_GATE_REQUIRED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "dependency_refs": {
            "rank_36_projector_obstruction": _dependency(RANK36, rank36),
            "rank_46_STF2_graph_carrier": _dependency(CARRIER, carrier),
            "rank_46_projector_solver_contract": _dependency(SOLVER_CONTRACT, contract),
        },
        "exact_import_checks": checks,
        "principal_filtered_module": {
            "coefficient_field": "Q(sqrt(10))",
            "scalar_wave_polynomial": "epsilon=-p0^2+p1^2+p2^2+p3^2",
            "algebra": "A=Q(sqrt(10))[epsilon]/(epsilon^2)",
            "real_physical_helicity_multiplicity": 2,
            "Einstein_submodule": "E=epsilon A=ker(epsilon:A->A)",
            "extra_Weyl_quotient": "X=A/E",
            "exact_sequence": "0 -> E -> A -> X -> 0",
            "rank_46_effect": "the added STF2 graph complement is contractible, so it does not split this retained principal extension",
        },
        "idempotent_audit": {
            "generic_endomorphism": "c=a+b epsilon",
            "idempotence_equations": ["a^2=a", "(2a-1)b=0"],
            "solutions_a_b": solutions,
            "only_trivial_principal_idempotents": True,
            "forbidden_false_anchors": [
                "P_E=0, P_X=P_gravity",
                "P_E=P_gravity, P_X=0",
                "project only onto the contractible STF2 auxiliary doublet",
            ],
        },
        "normalized_obstruction_witness": {
            "attempted_section": "s(1)=1+b epsilon",
            "A_linearity_equation": "epsilon s(1)=s(epsilon . 1)=0",
            "exact_defect": "epsilon s(1)=epsilon",
            "normalized_dual_functional": "coefficient_of(epsilon)",
            "normalized_evaluation": "1",
            "annihilates_all_section_corrections": "coefficient_of(epsilon^2 b)=0",
            "D_weight": 0,
            "K_Berger_weight": 0,
            "field_content": "one repeated helicity-two Jordan chain, with real multiplicity two",
        },
        "scientific_disposition": {
            "principal_Einstein_extra_Weyl_direct_sum_anchor_exists": False,
            "principal_filtered_Einstein_in_extra_Weyl_extension_exists": True,
            "declared_225_coefficient_solver_authorized_as_currently_anchored": False,
            "full_rank_46_lower_order_projector_ruled_out": False,
            "reason_full_projector_not_ruled_out": "lower-order Berger terms may deform epsilon^2=0 and split coincident leading factors; the subprincipal extension must be computed exactly",
            "couples_Einstein_like_and_extra_Weyl": True,
            "negative_physical_direction_introduced": False,
            "negative_direction_scope": "a principal module extension changes no unary kinetic sign and supports no unitarity inference",
            "REDUCED_MODE_limitation": "frequency, TT, helicity or generalized-mode splittings may choose a nonlocal complement, but cannot be imported into this LOCAL-ALGEBRAIC verdict",
        },
        "required_subprincipal_anchor": {
            "input": "exact order-two Berger remainder V2 in A10=Box_2^2+V2 on the physical helicity quotient",
            "required_output": "nontrivial lower-order branch inclusion/dual normalization or normalized obstruction",
            "anti_triviality_conditions": [
                "both branch maps act nontrivially on the physical helicity quotient",
                "neither branch is the contractible STF2 doublet",
                "the branch filtration or splitting reproduces the exact V2 extension class",
                "real and K_Berger compatibility are exact",
            ],
        },
        "claim_flags": {
            "PRINCIPAL_FILTERED_MODULE_CERTIFIED": True,
            "NORMALIZED_PRINCIPAL_ANCHOR_OBSTRUCTION_FOUND": True,
            "PRINCIPAL_DIRECT_SUM_BRANCH_ANCHOR_ACCEPTED": False,
            "FULL_RANK_46_PROJECTOR_SOLVE_RUN": False,
            "FULL_RANK_46_PROJECTOR_OBSTRUCTED": False,
            "SUBPRINCIPAL_ANCHOR_REQUIRED": True,
            "ELL3_BRANCH_MIXING_AUTHORIZED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "BERGER_RETAINED_46_STF2_SUBPRINCIPAL_BRANCH_ANCHOR_OR_OBSTRUCTION_V1",
        "provenance": {
            "source_manifest": sources,
            "verification_commands": [
                "PYTHONPATH=. python3 d_quotient_classical/backreacted_clock/berger_retained_46_stf2_principal_branch_anchor.py --check --guards",
                "PYTHONPATH=. python3 d_quotient_classical/backreacted_clock/verify_berger_retained_46_stf2_principal_branch_anchor.py",
                "python3 -m unittest d_quotient_classical.backreacted_clock.tests.test_berger_retained_46_stf2_principal_branch_anchor",
                "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/berger-retained-46-stf2-principal-branch-anchor-v1.schema.json -d d_quotient_classical/certificates/BERGER_RETAINED_46_STF2_PRINCIPAL_BRANCH_ANCHOR_V1.json",
            ],
        },
        "claim_boundary": (
            "This exact LOCAL-ALGEBRAIC certificate decides only the principal-symbol branch-anchor "
            "gate for the landed rank-46 STF2 cyclic graph carrier. The repeated helicity-two wave "
            "module is the nonsplit dual-number extension 0 -> epsilon A -> A -> A/(epsilon) -> 0; "
            "the displayed coefficient-of-epsilon functional is a normalized witness against every "
            "principal A-linear section. Because the added STF2 graph complement is contractible, it "
            "does not by itself turn this filtration into an Einstein-like/extra-Weyl direct sum. "
            "This result blocks the currently stated principal direct-sum anchor and excludes trivial "
            "or auxiliary projectors from being called physical branches. It does not rule out an "
            "exact lower-order Berger splitting, filtered branch theory, enlarged mapping cylinder, "
            "or separately tagged REDUCED-MODE decomposition. It does not authorize ell3 mixing, "
            "infer a negative kinetic direction, restore a QME, or make a quantum claim."
        ),
    }


def validate(value: dict) -> None:
    if value.get("result_state") != (
        "PRINCIPAL_DIRECT_SUM_ANCHOR_OBSTRUCTED_FILTERED_SUBPRINCIPAL_GATE_REQUIRED"
    ):
        raise ValueError("principal-anchor state drifted")
    witness = value.get("normalized_obstruction_witness", {})
    if witness.get("normalized_evaluation") != "1":
        raise ValueError("principal-anchor witness lost normalization")
    flags = value.get("claim_flags", {})
    if (
        flags.get("PRINCIPAL_FILTERED_MODULE_CERTIFIED") is not True
        or flags.get("NORMALIZED_PRINCIPAL_ANCHOR_OBSTRUCTION_FOUND") is not True
        or flags.get("SUBPRINCIPAL_ANCHOR_REQUIRED") is not True
        or any(
            flags.get(name) is not False
            for name in (
                "PRINCIPAL_DIRECT_SUM_BRANCH_ANCHOR_ACCEPTED",
                "FULL_RANK_46_PROJECTOR_SOLVE_RUN",
                "FULL_RANK_46_PROJECTOR_OBSTRUCTED",
                "ELL3_BRANCH_MIXING_AUTHORIZED",
                "QUANTUM_CLAIM",
            )
        )
    ):
        raise ValueError("principal-anchor claim boundary drifted")


def _render(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def _report(value: dict) -> str:
    return """# Rank-46 STF2 principal branch-anchor verdict

The principal physical wave module is the dual-number module

```text
A = Q(sqrt(10))[epsilon]/(epsilon^2).
```

Its Einstein layer is the submodule `epsilon A`; the generalized extra-Weyl
layer is the quotient `A/(epsilon)`.  The exact sequence does not split.  An
attempted section has `s(1)=1+b epsilon`, while `A`-linearity requires
`epsilon s(1)=0`; instead the exact defect is `epsilon`.  Taking the
coefficient of `epsilon` is a normalized dual witness equal to one and it
annihilates every correction `b epsilon`.

The rank-46 STF2 addition is an exact contractible graph complement, so it
does not alter this principal extension.  Consequently a nonzero direct-sum
Einstein/extra-Weyl anchor cannot be fixed at principal order, and the current
225-coefficient solve must not accept the trivial zero/identity or auxiliary
projectors.  This is not yet a no-go for the full Berger projector: lower-order
terms can split coincident leading factors.  The next honest gate is the exact
subprincipal extension defined by `V2` in `A10=Box_2^2+V2`.
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    value = build()
    validate(value)
    schema = _load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    if args.write:
        OUTPUT.write_text(_render(value))
        REPORT.write_text(_report(value))
    if args.check:
        if OUTPUT.read_text() != _render(value):
            raise ValueError("principal-anchor certificate drifted")
        if REPORT.read_text() != _report(value):
            raise ValueError("principal-anchor report drifted")
    if args.guards:
        for flag in (
            "PRINCIPAL_DIRECT_SUM_BRANCH_ANCHOR_ACCEPTED",
            "FULL_RANK_46_PROJECTOR_OBSTRUCTED",
            "ELL3_BRANCH_MIXING_AUTHORIZED",
        ):
            mutant = deepcopy(value)
            mutant["claim_flags"][flag] = True
            try:
                validate(mutant)
            except ValueError:
                continue
            raise ValueError(f"principal-anchor overclaim mutation accepted: {flag}")
    print("BERGER_RETAINED_46_STF2_PRINCIPAL_BRANCH_ANCHOR_V1: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
