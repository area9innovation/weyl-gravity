#!/usr/bin/env python3
"""Independent verifier for the Berger physical-helicity filtered quotient."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_46_STF2_PHYSICAL_HELICITY_FILTERED_QUOTIENT_V1.json"
SCHEMA = ROOT / "d_quotient_classical/schema/berger-retained-46-stf2-physical-helicity-filtered-quotient-v1.schema.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _matrix(record: list[list[str]]) -> sp.Matrix:
    return sp.Matrix([[sp.sympify(value) for value in row] for row in record])


def verify() -> dict:
    value = json.loads(OUTPUT.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    for dependency in value["dependency_refs"].values():
        path = ROOT / dependency["path"]
        if _sha256(path) != dependency["sha256"]:
            raise ValueError(f"physical-helicity dependency drifted: {path}")
    for path_text, expected in value["provenance"]["source_manifest"].items():
        path = ROOT / path_text
        if _sha256(path) != expected:
            raise ValueError(f"physical-helicity source drifted: {path}")

    n1, n2, n3 = sp.symbols("n1 n2 n3")
    relation = n1**2 + n2**2 + n3**2 - 1
    groebner = sp.groebner([relation], n1, n2, n3, order="grlex", domain=sp.QQ)

    def reduce_polynomial(expression: sp.Expr) -> sp.Expr:
        return sp.factor(groebner.reduce(sp.expand(expression))[1])

    chart = value["null_cone_chart"]
    ptt = _matrix(chart["TT_projector_6x6"])
    field = _matrix(chart["field_projector_10x10"])
    equation = _matrix(chart["equation_projector_10x10"])
    if any(reduce_polynomial(entry) != 0 for entry in ptt * ptt - ptt):
        raise ValueError("independent TT idempotence replay failed")
    if reduce_polynomial(sp.trace(ptt)) != 2:
        raise ValueError("independent TT rank replay failed")
    if any(reduce_polynomial(entry) != 0 for entry in field * field - field):
        raise ValueError("independent field-projector replay failed")
    if any(reduce_polynomial(entry) != 0 for entry in equation * equation - equation):
        raise ValueError("independent equation-projector replay failed")
    if equation != field.T:
        raise ValueError("cyclic transpose relation failed")

    standard = {n1: 1, n2: 0, n3: 0}
    if field.subs(standard).rank() != 2 or equation.subs(standard).rank() != 2:
        raise ValueError("standard-fibre physical rank failed")
    fibre = value["normalized_standard_null_fibre"]
    if fibre["induced_cyclic_pairing"] != [["1", "0"], ["0", "1"]]:
        raise ValueError("normalized physical pairing drifted")
    generator = sp.Matrix(fibre["little_group_generator"])
    if generator**2 != -4 * sp.eye(2):
        raise ValueError("helicity-two little-group replay failed")
    if value["full_Berger_null_symbol_cohomology"]["cohomology_dimensions"] != [0, 6, 6, 0]:
        raise ValueError("full Berger null cohomology was collapsed to the physical pair")
    if value["filtered_principal_module"]["generalized_wave_rank_over_Q_sqrt10"] != 4:
        raise ValueError("polarization/generalized-wave rank distinction failed")

    artifact = value["V2_receiving_contract"]["artifact"]
    if _sha256(ROOT / artifact["path"]) != artifact["sha256"]:
        raise ValueError("V2 receiving artifact drifted")
    if value["V2_receiving_contract"]["raw_10x10_diagonalization_authorized"]:
        raise ValueError("raw V2 diagonalization was incorrectly authorized")
    flags = value["claim_flags"]
    for name in (
        "GLOBAL_TWO_COLUMN_HELICITY_FRAME_CERTIFIED",
        "V2_FILTERED_DESCENT_COMPUTED",
        "SUBPRINCIPAL_BRANCH_ANCHOR_AVAILABLE",
        "BRANCH_PROJECTOR_ACCEPTED",
        "ELL3_BRANCH_MIXING_AUTHORIZED",
        "QUANTUM_CLAIM",
    ):
        if flags[name]:
            raise ValueError(f"physical-helicity certificate overpromoted {name}")
    return value


if __name__ == "__main__":
    verify()
    print("BERGER_RETAINED_46_STF2_PHYSICAL_HELICITY_FILTERED_QUOTIENT_V1 independent verification: PASS")
