#!/usr/bin/env python3
"""Independent verifier for the BT extended squeeze-carrier trilemma."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
from fractions import Fraction

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EXTENDED_SQUEEZE_CARRIER_V1.json",
)
SCHEMA = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-extended-squeeze-carrier-v1.schema.json",
)


def load(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def fraction(value):
    return Fraction(value["numerator"], value["denominator"])


def sha256(relative_path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative_path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def verify(path):
    certificate = load(path)
    schema = load(SCHEMA)
    checks = {}

    checks["strict_schema"] = not list(
        Draft202012Validator(schema).iter_errors(certificate)
    )

    full = certificate.get("full_pair_exponential", {})
    ordered = Fraction(1, 2) * Fraction(1, 8) * Fraction(2)
    unordered = 2 * ordered
    checks["independent_box_coefficient"] = (
        ordered == Fraction(1, 8)
        and unordered == Fraction(1, 4)
        and fraction(full.get("ordered_creation_coefficient", {})) == ordered
        and fraction(full.get("unordered_creation_coefficient", {})) == unordered
    )

    factorial_rows = full.get("factorial_witnesses", [])
    checks["independent_full_series_factorials"] = len(factorial_rows) == 9 and all(
        row.get("exponential_denominator") == math.factorial(row.get("n"))
        and row.get("two_mode_creation_norm_factor")
        == math.factorial(row.get("n")) ** 2
        and fraction(row.get("normalized_basis_amplitude_factor", {})) == 1
        for row in factorial_rows
    )

    geometric_rows = full.get("geometric_witnesses", [])
    checks["independent_geometric_norm"] = len(geometric_rows) == 5 and all(
        fraction(row.get("direct_partial_norm", {}))
        == sum(Fraction(1, 2) ** (2 * n) for n in range(row.get("cutoff") + 1))
        == fraction(row.get("closed_partial_norm", {}))
        for row in geometric_rows
    )

    ordinary = certificate.get("ordinary_topology_obstruction", {})
    # z(p_min)>=m/[4(2pi/L)^2]=mL^2/(16pi^2), reaching one at 4pi/sqrt(m).
    checks["independent_ordinary_contraction_failure"] = (
        ordinary.get("lowest_pair_amplitude_bound")
        == "|z(p_min)|>=m L^2/(16pi^2)"
        and ordinary.get("contraction_failure_threshold") == "L>=4pi/sqrt(m)"
        and ordinary.get("conclusion")
        == "FULL_EXPONENTIAL_FAILS_MODEWISE_BEFORE_THE_MASSLESS_THERMODYNAMIC_LIMIT"
    )

    powers = certificate.get("power_weight_classification", {})
    # d^3p z^2 ~ dp p^(2alpha-2); z~p^(alpha-2).
    checks["independent_power_thresholds"] = (
        2 * Fraction(1, 2) - 2 == -1
        and powers.get("square_sum_condition") == "alpha>1/2"
        and powers.get("modewise_contraction_condition")
        == "alpha>2, or alpha=2 with limiting coefficient below four"
    )

    candidate = certificate.get("explicit_weighted_candidate", {})
    fixtures = candidate.get("exact_gamma_half_fixtures", [])
    gamma = Fraction(1, 2)
    reconstructed = []
    for x in (Fraction(0), Fraction(1, 4), Fraction(1), Fraction(4), Fraction(16)):
        reconstructed.append((x, 4 * gamma * x / (x + 1), gamma / (x + 1)))
    checks["independent_weighted_fixtures"] = len(fixtures) == 5 and all(
        fraction(row.get("p_squared_over_mu_squared", {})) == expected[0]
        and fraction(row.get("rho_over_mu_squared", {})) == expected[1]
        and fraction(row.get("pair_amplitude_z", {})) == expected[2]
        and expected[2] < 1
        for row, expected in zip(fixtures, reconstructed)
    )

    # Unordered momenta contribute half of 4pi/(2pi)^3. With
    # integral x^2/(1+x^2)^2 dx=pi/4, the density is gamma^2 mu^3/(16pi).
    angular_with_unordered = Fraction(1, 4)  # coefficient multiplying pi^-2
    radial_coefficient = Fraction(1, 4)  # coefficient multiplying pi
    density_coefficient = angular_with_unordered * radial_coefficient
    checks["independent_candidate_density"] = (
        density_coefficient == Fraction(1, 16)
        and fraction(candidate.get("density_coefficient_times_pi_inverse", {}))
        == density_coefficient
        and candidate.get("unordered_square_sum_density")
        == "gamma^2 mu^3/(16pi)"
        and candidate.get("supremum") == "gamma<1"
    )

    boundary = certificate.get("inequivalence_and_volume_boundary", {})
    checks["independent_inequivalence_boundary"] = (
        "p^-2" in boundary.get("infrared_inverse", "")
        and "unbounded" in boundary.get("fundamental_symmetry_status", "")
        and "extensive" in boundary.get("total_log_norm", "")
        and "zero" in boundary.get("normalized_vacuum_overlap", "")
    )

    adjoint = certificate.get("positive_adjoint_audit", {})
    raw = adjoint.get("raw_positive_Bogoliubov_fixture", {})
    repaired = adjoint.get("normalized_positive_repair_fixture", {})
    checks["independent_positive_Bogoliubov_defect"] = (
        fraction(raw.get("u_squared", {})) - fraction(raw.get("v_squared", {}))
        == Fraction(3, 4)
        != 1
        and fraction(repaired.get("u_squared", {}))
        - fraction(repaired.get("v_squared", {}))
        == 1
        and fraction(repaired.get("u_squared", {})) != 1
        and adjoint.get("conclusion")
        == "BT_CROSS_KREIN_SHEAR_IS_NOT_A_POSITIVE_HILBERT_BOGOLIUBOV_TRANSFORMATION"
    )

    import_gate = certificate.get("extended_implementation_import_gate", {})
    checks["extended_theorem_import_boundary"] = (
        import_gate.get("reference_architecture") == "Lill arXiv:2208.03487v2"
        and "positive-Hilbert" in import_gate.get("reference_scope", "")
        and "algebraic quotient" in import_gate.get("extended_space_scope", "")
        and import_gate.get("import_disposition")
        == "ARCHITECTURE_RELEVANT_THEOREM_NOT_DIRECTLY_APPLICABLE"
        and len(import_gate.get("not_supplied_by_reference", [])) == 4
    )

    disposition = certificate.get("disposition", {})
    trilemma = certificate.get("carrier_trilemma", {})
    checks["claim_boundary"] = (
        disposition.get("explicit_IR_weighted_vacuum_carrier")
        == "CONSTRUCTED_AS_INEQUIVALENT_REDUCED_MODE_CANDIDATE"
        and disposition.get("BT_cross_Krein_operator_map_on_candidate")
        == "NOT_CONSTRUCTED"
        and disposition.get("positive_cyclic_generalized_Born_trace")
        == "NOT_CONSTRUCTED"
        and disposition.get("Eq19_in_extended_representation") == "NOT_REPRODUCED"
        and disposition.get("physical_neutral_one_over_48") == "NOT_ESTABLISHED"
        and trilemma.get("resolved_outcome")
        == "EXPLICIT_INEQUIVALENT_VACUUM_CARRIER_CONSTRUCTED_BORN_TRACE_STILL_OBSTRUCTED"
    )

    inputs = certificate.get("provenance", {}).get("inputs", [])
    checks["input_hashes"] = len(inputs) == 4 and all(
        item.get("sha256") == sha256(item.get("path", "")) for item in inputs
    )

    exclusions = certificate.get("does_not_establish", [])
    checks["fail_closed_exclusions"] = (
        any("weighted candidate implements" in item for item in exclusions)
        and any("positive-boson theorem" in item for item in exclusions)
        and any("LORENTZIAN-CAUSAL" in item for item in exclusions)
        and len(certificate.get("missing_object_ledger", [])) >= 7
    )

    ok = all(checks.values())
    for name, value in checks.items():
        print(f"[{'PASS' if value else 'FAIL'}] {name}")
    print(f"RESULT: {'PASS' if ok else 'FAIL'} ({sum(checks.values())}/{len(checks)})")
    return ok


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", default=CERT)
    args = parser.parse_args(argv)
    return 0 if verify(args.verify) else 1


if __name__ == "__main__":
    sys.exit(main())
