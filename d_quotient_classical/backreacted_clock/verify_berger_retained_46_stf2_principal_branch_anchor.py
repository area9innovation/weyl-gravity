#!/usr/bin/env python3
"""Independent verifier for the rank-46 principal branch-anchor verdict."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_46_STF2_PRINCIPAL_BRANCH_ANCHOR_V1.json"
SCHEMA = ROOT / "d_quotient_classical/schema/berger-retained-46-stf2-principal-branch-anchor-v1.schema.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify() -> dict:
    value = json.loads(OUTPUT.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    for dependency in value["dependency_refs"].values():
        path = ROOT / dependency["path"]
        if _sha256(path) != dependency["sha256"]:
            raise ValueError(f"principal-anchor dependency drifted: {path}")
    for path_text, expected in value["provenance"]["source_manifest"].items():
        path = ROOT / path_text
        if _sha256(path) != expected:
            raise ValueError(f"principal-anchor source drifted: {path}")

    a, b = sp.symbols("a b")
    solutions = sp.solve(
        [sp.expand(a**2 - a), sp.expand((2 * a - 1) * b)],
        [a, b],
        dict=True,
    )
    normalized = sorted([[str(item[a]), str(item[b])] for item in solutions])
    if normalized != [["0", "0"], ["1", "0"]]:
        raise ValueError("principal idempotent replay failed")

    # In A=k[epsilon]/epsilon^2, epsilon*(1+b epsilon)=epsilon.
    section_constant, section_epsilon = sp.Integer(1), b
    defect_constant = sp.Integer(0) * section_constant
    defect_epsilon = sp.expand(section_constant + sp.Integer(0) * section_epsilon)
    if (defect_constant, defect_epsilon) != (0, 1):
        raise ValueError("principal section-defect replay failed")
    witness = value["normalized_obstruction_witness"]
    if witness["normalized_dual_functional"] != "coefficient_of(epsilon)":
        raise ValueError("principal witness functional drifted")
    if witness["normalized_evaluation"] != str(defect_epsilon):
        raise ValueError("principal witness normalization failed")

    rank36_path = ROOT / value["dependency_refs"]["rank_36_projector_obstruction"]["path"]
    rank36 = json.loads(rank36_path.read_text())
    if rank36["principal_filtered_module_audit"]["solutions_a_b"] != normalized:
        raise ValueError("principal audit disagrees with rank-36 authority")
    carrier_path = ROOT / value["dependency_refs"]["rank_46_STF2_graph_carrier"]["path"]
    carrier = json.loads(carrier_path.read_text())
    if carrier["flags"]["CYCLIC_GRAPH_SDR_46_TO_36"] is not True:
        raise ValueError("principal audit lost rank-46 graph SDR")
    if carrier["graph_construction"]["interpretation"].find("contractible") < 0:
        raise ValueError("principal audit lost contractible-complement boundary")
    physical_path = ROOT / value["dependency_refs"]["physical_helicity_filtered_quotient"]["path"]
    physical = json.loads(physical_path.read_text())
    if physical["null_cone_chart"]["projective_rank"] != 2:
        raise ValueError("principal audit lost the derived physical rank-two module")
    if physical["full_Berger_null_symbol_cohomology"]["cohomology_dimensions"] != [0, 6, 6, 0]:
        raise ValueError("principal audit collapsed full null cohomology to helicities")
    if physical["filtered_principal_module"]["generalized_wave_rank_over_Q_sqrt10"] != 4:
        raise ValueError("principal audit lost the generalized-wave rank distinction")

    flags = value["claim_flags"]
    if flags["FULL_RANK_46_PROJECTOR_OBSTRUCTED"]:
        raise ValueError("principal audit overpromoted to a full-projector no-go")
    if not flags["SUBPRINCIPAL_ANCHOR_REQUIRED"]:
        raise ValueError("principal audit omitted the subprincipal next gate")
    return value


if __name__ == "__main__":
    verify()
    print("BERGER_RETAINED_46_STF2_PRINCIPAL_BRANCH_ANCHOR_V1 independent verification: PASS")
