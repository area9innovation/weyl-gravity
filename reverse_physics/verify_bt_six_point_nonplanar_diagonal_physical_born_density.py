#!/usr/bin/env python3
"""Independent explicit-tree verifier for nonplanar diagonal BT positivity."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "reverse_physics"))

from verify_bt_six_point_planar_physical_born_density import explicit_tree_family


CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_SIX_POINT_NONPLANAR_DIAGONAL_PHYSICAL_BORN_DENSITY_V1.json",
)
SCHEMA = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-six-point-nonplanar-diagonal-physical-born-density-v1.schema.json",
)
FULL = 63


def load(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_fast(certificate):
    """Fast independent exact fixture rail for mutation and edit loops."""
    import sympy as sp

    errors = list(Draft202012Validator(load(SCHEMA)).iter_errors(certificate))
    if errors:
        return {"schema_validation": False}
    inputs = certificate["provenance"]["inputs"]
    hashes_match = all(
        row["sha256"] == sha256(row["path"]) for row in inputs
    )
    if not hashes_match:
        return {"schema_validation": True, "all_input_hashes_match": False}
    family = certificate["exact_nonplanar_family"]
    recorded = {row["mask"]: row for row in family["middle_coefficients"]}
    fixture_checks = []
    for parameter in (Fraction(1, 2), Fraction(3, 2)):
        result = explicit_tree_family(Fraction(1, 2), parameter)
        coefficients = {
            mask: value
            for mask, value in result["amplitude"].coefficients.items()
            if mask.bit_count() == 3
        }
        substitutions = {sp.Symbol("t"): sp.Rational(parameter.numerator, parameter.denominator)}
        fixture_checks.append(
            result["tree_count"] == 220
            and result["topology_counts"]
            == {(4, 0): 105, (2, 1): 105, (0, 2): 10}
            and all(
                coefficients[mask] == coefficients[FULL ^ mask]
                and Fraction(
                    int(coefficients[mask].numerator),
                    int(coefficients[mask].denominator),
                )
                == Fraction(
                    sp.Rational(
                        sp.sympify(recorded[mask]["coefficient"])
                        .subs(substitutions)
                    )
                )
                for mask in recorded
            )
        )
    interpretation = certificate["interpretation"]
    return {
        "schema_validation": True,
        "all_input_hashes_match": hashes_match,
        "two_independent_exact_nonplanar_fixtures": all(fixture_checks),
        "claim_boundary_remains_fail_closed": (
            interpretation["complete_two_parameter_nonplanar_family"]
            == "NOT_COMPUTED"
            and interpretation["integrated_normalized_probability"]
            == "NOT_COMPUTED"
            and interpretation["Eq19_all_orders"] == "NOT_PROVED"
        ),
    }


def verify(certificate):
    errors = list(Draft202012Validator(load(SCHEMA)).iter_errors(certificate))
    if errors:
        return {"schema_validation": False}
    inputs = certificate["provenance"]["inputs"]
    hashes_match = all(
        row["sha256"] == sha256(row["path"]) for row in inputs
    )
    if not hashes_match:
        return {"schema_validation": True, "all_input_hashes_match": False}

    result = explicit_tree_family(Fraction(1, 2))
    base = result["base"]
    amplitude = result["amplitude"]
    family = certificate["exact_nonplanar_family"]
    coefficients = {
        mask: value
        for mask, value in amplitude.coefficients.items()
        if mask.bit_count() == 3
    }
    representatives = [
        mask for mask in sorted(coefficients) if mask < (FULL ^ mask)
    ]
    recorded = {row["mask"]: row for row in family["middle_coefficients"]}
    squarefree = (amplitude * amplitude).coefficients.get(FULL, base.zero)
    square_sum = 2 * sum(
        (coefficients[mask] * coefficients[mask] for mask in representatives),
        base.zero,
    )
    gcd = coefficients[representatives[0]].numer
    for mask in representatives[1:]:
        gcd = gcd.gcd(coefficients[mask].numer)
    total_momentum = [
        sum((row[index] for row in result["momenta"]), base.zero)
        for index in range(4)
    ]
    mass_squares = [
        row[0] * row[0] - sum((entry * entry for entry in row[1:]), base.zero)
        for row in result["momenta"]
    ]
    outgoing_z = [row[3] for row in result["momenta"][3:]]
    topology_nontrivial = []
    topology_cancellation = []
    for mask in representatives:
        differences = []
        for topology in sorted(result["topology_amplitudes"]):
            values = result["topology_amplitudes"][topology].coefficients
            differences.append(
                values.get(mask, base.zero) - values.get(FULL ^ mask, base.zero)
            )
        topology_nontrivial.append(any(value != 0 for value in differences))
        topology_cancellation.append(sum(differences, base.zero) == 0)
    denominator_factors = squarefree.denom.factor_list()[1]
    interpretation = certificate["interpretation"]
    checks = {
        "schema_validation": True,
        "all_input_hashes_match": hashes_match,
        "independent_nullness_and_conservation": all(
            value == 0 for value in mass_squares + total_momentum
        ),
        "independent_out_of_plane_component_is_nonzero": any(
            value != 0 for value in outgoing_z
        ),
        "independent_invariants_match": (
            [str(value) for value in result["adjacent"]]
            == family["adjacent_invariants"]
            and [str(value) for value in result["triples"]]
            == family["triple_invariants"]
        ),
        "explicit_220_tree_topology_census": (
            result["tree_count"] == 220
            and result["topology_counts"]
            == {(4, 0): 105, (2, 1): 105, (0, 2): 10}
        ),
        "amplitude_support_matches": (
            len(amplitude.coefficients) == 42
            and sorted({mask.bit_count() for mask in amplitude.coefficients})
            == [3, 4, 5, 6]
        ),
        "ten_complement_equalities_reconstruct": (
            len(coefficients) == 20 and len(representatives) == 10
            and all(coefficients[mask] == coefficients[FULL ^ mask]
                    for mask in representatives)
        ),
        "recorded_middle_coefficients_match": (
            set(recorded) == set(representatives)
            and all(
                recorded[mask]["complement_mask"] == FULL ^ mask
                and recorded[mask]["coefficient"] == str(coefficients[mask])
                and recorded[mask]["complement_coefficient"]
                == str(coefficients[FULL ^ mask])
                for mask in representatives
            )
        ),
        "topology_antisymmetry_cancels_only_in_sum": (
            all(topology_nontrivial) and all(topology_cancellation)
        ),
        "independent_ten_square_identity": (
            squarefree == square_sum
            and str(squarefree) == family["squarefree_squared_amplitude"]
        ),
        "independent_gcd_is_one": gcd.degree() == 0
        and str(gcd.monic()) == "1",
        "independent_pole_factorization_is_even": (
            len(denominator_factors) == 10
            and all(multiplicity == 2
                    for _, multiplicity in denominator_factors)
            and [
                {"factor": str(factor), "multiplicity": multiplicity}
                for factor, multiplicity in denominator_factors
            ] == family["squarefree_denominator_factors"]
        ),
        "local_measure_decoupling_is_typed": (
            certificate["local_born_density"]["amplitude_minimum_mass_degree"]
            == 3
            and certificate["local_born_density"]
            ["squared_amplitude_minimum_mass_degree"] == 6
        ),
        "claim_boundary_remains_fail_closed": (
            interpretation["complete_two_parameter_nonplanar_family"]
            == "NOT_COMPUTED"
            and interpretation["integrated_normalized_probability"]
            == "NOT_COMPUTED"
            and interpretation["Eq19_all_orders"] == "NOT_PROVED"
            and any("LORENTZIAN-CAUSAL" in row
                    for row in certificate["does_not_establish"])
        ),
        "next_gate_requires_two_independent_parameters": (
            "two independent rotation parameters" in certificate["next_gate"]
            and "modular/interpolation" in certificate["next_gate"]
        ),
    }
    return {name: bool(value) for name, value in checks.items()}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", default=CERT)
    parser.add_argument("--fast", action="store_true")
    args = parser.parse_args(argv)
    checks = (verify_fast if args.fast else verify)(load(args.verify))
    for name, ok in checks.items():
        print(("PASS" if ok else "FAIL") + ": " + name)
    print("RESULT:", "PASS" if all(checks.values()) else "FAIL")
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
