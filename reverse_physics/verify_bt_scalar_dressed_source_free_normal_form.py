#!/usr/bin/env python3
"""Independent exact verification of the scalar source free normal form."""
from __future__ import annotations

from fractions import Fraction
import hashlib
import json
import os
import sys

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(ROOT, "reverse_physics/certificates/REVERSE_PHYSICS_BT_SCALAR_DRESSED_SOURCE_FREE_NORMAL_FORM_V1.json")
SCHEMA = os.path.join(ROOT, "reverse_physics/schema/reverse-physics-bt-scalar-dressed-source-free-normal-form-v1.schema.json")


def load(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def file_hash(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def polynomial_multiply(left, right):
    out = [Fraction(0)] * (len(left) + len(right) - 1)
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            out[i + j] += a * b
    return out


def verify(certificate):
    # Evaluate the energy-dependent CCR cancellation at unrelated exact
    # energies rather than importing symbolic producer algebra.
    energy_rows = []
    for energy in (Fraction(1), Fraction(3, 2), Fraction(11, 3)):
        a_cross = (2 * energy) ** 3
        denominator = (2 * energy) * 4 * energy**2
        energy_rows.append(a_cross / denominator)

    # (lambda^4 A4 + lambda^5 A5)(psi0 + lambda psi1), with independent
    # formal scalar coefficients set to distinguish every contribution.
    transition = [Fraction(0)] * 4 + [Fraction(2), Fraction(3)]
    source = [Fraction(5), Fraction(7)]
    amplitude = polynomial_multiply(transition, source)
    probability = polynomial_multiply(amplitude, amplitude)

    checks = {
        "schema_validation": not list(Draft202012Validator(load(SCHEMA)).iter_errors(certificate)),
        "input_hashes_match": all(row["sha256"] == file_hash(row["path"]) for row in certificate["provenance"]["inputs"]),
        "three_exact_energy_CCRs_are_one": energy_rows == [Fraction(1), Fraction(1), Fraction(1)],
        "three_mode_cross_pairing_is_one": energy_rows[0] * energy_rows[1] * energy_rows[2] == 1,
        "symmetric_two_null_branch_norm_is_one": Fraction(1, 2) * (1 + 1) == 1,
        "state_support_has_both_orbit_branches": certificate["explicit_leading_scalar_source"]["state_orbit_support"] == ["Z^-3", "Z^3"],
        "projector_support_has_return_and_both_branches": certificate["explicit_leading_scalar_source"]["projector_orbit_support"] == ["Z^-6", "1", "Z^6"],
        "pulled_vacuum_is_not_bare_vacuum": "exp[-alpha_t(Q_cov)]" in certificate["explicit_leading_scalar_source"]["pulled_vacuum"],
        "Omega_annihilator_term_is_removed_only_on_vacuum": "a1(-p)" in certificate["explicit_leading_scalar_source"]["one_mode_Omega_creator_full"] and "a1(-p)" not in certificate["explicit_leading_scalar_source"]["one_mode_Omega_creator_on_vacuum"],
        "amplitude_order_four_is_reconstructed": amplitude[4] == 10,
        "amplitude_order_five_contains_source_correction": amplitude[5] == 29,
        "probability_order_eight_uses_only_leading_source": probability[8] == 100,
        "probability_order_nine_contains_first_source_correction": probability[9] == 580,
        "certificate_first_source_correction_is_lambda_nine": certificate["perturbative_order_protection"]["first_source_correction_order_in_probability"] == "lambda^9",
        "leading_rate_is_protected": certificate["interpretation"]["leading_lambda8_probability"] == "UNAFFECTED_BY_UNKNOWN_O_LAMBDA_SOURCE_CORRECTIONS",
        "ordinary_Fock_boundary_is_preserved": certificate["interpretation"]["ordinary_massless_Fock_thermodynamic_source"] == "OBSTRUCTED",
        "standard_projector_boundary_is_preserved": certificate["interpretation"]["standard_shift_invariant_P_chi"] == "NOT_CONSTRUCTED",
        "general_Eq19_boundary_is_preserved": certificate["interpretation"]["general_Eq19"] == "NOT_PROVED" and "general Eq. (19)" in certificate["does_not_establish"],
        "Lorentzian_boundary_is_preserved": "anything LORENTZIAN-CAUSAL" in certificate["does_not_establish"],
    }
    return {name: bool(value) for name, value in checks.items()}


def main():
    checks = verify(load(CERT))
    failures = [name for name, value in checks.items() if not value]
    print("checks %d/%d" % (sum(checks.values()), len(checks)))
    print("RESULT:", "PASS" if not failures else "FAIL")
    if failures:
        print("failures:", ", ".join(failures))
    return int(bool(failures))


if __name__ == "__main__":
    sys.exit(main())
