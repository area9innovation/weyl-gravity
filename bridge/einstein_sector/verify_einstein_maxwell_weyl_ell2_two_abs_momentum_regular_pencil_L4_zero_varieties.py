"""Independent verifier for the candidate-7/11/19 regular-pencil varieties."""
from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path

import jsonschema
import sympy as sp

from bridge.einstein_sector.einstein_maxwell_weyl_two_abs_momentum_axial_axial_L4_matrix import (
    certified_nonzero_interval,
)


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_regular_pencil_L4_zero_varieties.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_ell2_two_abs_momentum_regular_pencil_L4_zero_varieties.schema.json"
PARENT = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_cross_fibre_amplitude_system.json"


def parse(value: str) -> sp.Expr:
    return sp.sympify(value, locals={"sqrt": sp.sqrt, "pi": sp.pi})


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def det2(matrix: sp.Matrix) -> sp.Expr:
    return matrix[0, 0] * matrix[1, 1] - matrix[0, 1] * matrix[1, 0]


def adj2(matrix: sp.Matrix) -> sp.Matrix:
    return sp.Matrix([[matrix[1, 1], -matrix[0, 1]], [-matrix[1, 0], matrix[0, 0]]])


def matrices(fibre: dict[str, object]) -> dict[str, sp.Matrix]:
    conversion = parse(fibre["coefficient_coordinate"]["axisymmetric_to_reduced_conversion"])
    result = {}
    for target in fibre["target_equations"]:
        for term in target["terms"]:
            key = term["first_parity"][0] + term["second_parity"][0]
            rows = []
            for component in term["coefficient_matrices"]:
                source = sp.Matrix([[parse(value) * conversion for value in row] for row in component])
                rows.append(list(source if source.rows == 1 else source.T))
            if fibre["first_branch_multiplicity_per_parity"] == 2:
                key = key[::-1]
            result[key] = sp.Matrix(rows)
    return result


def sign(value: sp.Expr) -> str:
    witness = certified_nonzero_interval(value)
    if witness is None:
        raise AssertionError("verifier found a zero pencil invariant")
    bounds, _ = witness
    return "positive" if bounds[0] > 0 else "negative"


def parse_fraction(value: str) -> Fraction:
    numerator, denominator = value.split("/")
    return Fraction(int(numerator), int(denominator))


def verify() -> None:
    certificate = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    jsonschema.validate(certificate, schema)
    if certificate["schema_sha256"] != sha(SCHEMA):
        raise AssertionError("regular-pencil schema hash changed")
    parent_path = ROOT / certificate["provenance"]["parent"]
    if parent_path != PARENT or certificate["provenance"]["parent_sha256"] != sha(PARENT):
        raise AssertionError("regular-pencil parent provenance changed")
    parent = json.loads(PARENT.read_text())
    fibres = {item["candidate_index"]: item for item in parent["physical_fibres"]}
    if certificate["summary"]["classified_candidates"] != [7, 11, 19]:
        raise AssertionError("regular-pencil candidate census changed")
    for record in certificate["decompositions"]:
        candidate = record["candidate_index"]
        fibre = fibres[candidate]
        current = matrices(fibre)
        stored_matrices = {
            key: sp.Matrix([[parse(entry) for entry in row] for row in matrix])
            for key, matrix in record["internal_matrices"].items()
        }
        if stored_matrices != current:
            raise AssertionError(f"stored internal matrices changed for candidate {candidate}")
        determinants = {key: det2(value) for key, value in current.items()}
        denominator = determinants["ap"] * determinants["aa"]
        product = adj2(current["ap"]) * current["pa"] * adj2(current["aa"]) * current["pp"]
        trace = (product[0, 0] + product[1, 1]) / denominator
        determinant = determinants["pa"] * determinants["pp"] / denominator
        invariants = {
            **{f"det_{key}": value for key, value in determinants.items()},
            "trace_square_pencil": trace,
            "determinant_square_pencil": determinant,
            "discriminant_square_pencil": trace**2 - 4 * determinant,
        }
        stored = record["exact_interval_witnesses"]
        for key, value in invariants.items():
            if sign(value) != stored[key]["sign"]:
                raise AssertionError(f"pencil sign changed for candidate {candidate}: {key}")
            lower = parse_fraction(stored[key]["lower"])
            upper = parse_fraction(stored[key]["upper"])
            numerical = sp.N(value, 80)
            if not (sp.N(lower, 80) < numerical < sp.N(upper, 80)):
                raise AssertionError(f"stored interval stopped enclosing candidate {candidate}: {key}")
        if any(stored[key]["sign"] != "positive" for key in (
            "trace_square_pencil", "determinant_square_pencil", "discriminant_square_pencil"
        )):
            raise AssertionError("four-real-root criterion failed")
        zero = record["zero_variety"]
        if zero["component_dimensions_over_C"] != [20, 10, 10, 10, 10, 10]:
            raise AssertionError("regular-pencil component dimensions changed")
        if len(zero["irreducible_components_over_C"]) != 6 or not zero["all_mixed_components_real_supported"]:
            raise AssertionError("regular-pencil component decomposition changed")
    classification = certificate["classification"]
    if not (
        classification["three_regular_pencil_L4_zero_varieties_classified"]
        and classification["all_m_irreducible_decomposition_classified"]
        and classification["four_distinct_real_pencil_roots_certified"]
    ):
        raise AssertionError("regular-pencil theorem was weakened")
    if (
        classification["candidate_13_zero_variety_classified"]
        or classification["same_fibre_quadratic_sources_classified"]
        or classification["taub_common_zero_intersection_classified"]
        or classification["complete_two_fibre_tangent_cone_classified"]
        or classification["smooth_secular_classified"]
        or classification["causal_or_quantum_claim"]
    ):
        raise AssertionError("regular-pencil theorem exceeded its scope")
    print("EINSTEIN_MAXWELL_WEYL_ELL2_TWO_ABS_MOMENTUM_REGULAR_PENCIL_L4_ZERO_VARIETIES independent verification: PASS")


if __name__ == "__main__":
    verify()
