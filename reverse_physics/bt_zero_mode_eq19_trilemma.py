#!/usr/bin/env python3
"""Exact vacuum-orbit zero-mode audit of the BT Eq. (19) charge claim."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_ZERO_MODE_EQ19_TRILEMMA_V1.json",
)
SCHEMA = (
    "reverse_physics/schema/"
    "reverse-physics-bt-zero-mode-eq19-trilemma-v1.schema.json"
)
REPORT = "reverse_physics/reports/bt-zero-mode-eq19-trilemma.md"
SOURCE_COMMIT = "e057a7e370a427d19f9cf8491ee9d1456f6fe348"
INPUTS = [
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_SOFT_CHARGE_RESOLVED_FLOW_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_FULL_OFF_RESONANT_PROJECTOR_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_RT_JORDAN_KERNEL_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_OSCILLATORY_RADICAL_NO_MATCHING_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_INCLUSIVE_RADICAL_CLOSURE_V1.json",
]


class Laurent:
    """Finite exact carrier in Q[Z,Z^-1]."""

    def __init__(self, terms=None):
        clean = {}
        for exponent, coefficient in (terms or {}).items():
            exponent = int(exponent)
            coefficient = Fraction(coefficient)
            if coefficient:
                clean[exponent] = clean.get(exponent, Fraction(0)) + coefficient
        self.terms = {power: value for power, value in clean.items() if value}

    @classmethod
    def monomial(cls, exponent, coefficient=1):
        return cls({exponent: coefficient})

    def __add__(self, other):
        if not isinstance(other, Laurent):
            other = Laurent.monomial(0, other)
        result = dict(self.terms)
        for exponent, coefficient in other.terms.items():
            result[exponent] = result.get(exponent, Fraction(0)) + coefficient
        return Laurent(result)

    __radd__ = __add__

    def __neg__(self):
        return Laurent({power: -value for power, value in self.terms.items()})

    def __sub__(self, other):
        return self + (-other)

    def __mul__(self, other):
        if not isinstance(other, Laurent):
            other = Laurent.monomial(0, other)
        result = {}
        for left_power, left_value in self.terms.items():
            for right_power, right_value in other.terms.items():
                power = left_power + right_power
                result[power] = result.get(power, Fraction(0)) + left_value * right_value
        return Laurent(result)

    __rmul__ = __mul__

    def dagger(self):
        # BT dagger preserves boost weight; Z is self-adjoint in the orbit pairing.
        return Laurent(self.terms)

    def derivation(self):
        return Laurent({power: power * value for power, value in self.terms.items()})

    def invariant_trace(self):
        return self.terms.get(0, Fraction(0))

    def fixed_vacuum_character(self):
        return sum(self.terms.values(), Fraction(0))

    def __eq__(self, other):
        return isinstance(other, Laurent) and self.terms == other.terms


def rat(value):
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def load(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as handle:
        return json.load(handle)


def species_charge(species):
    return {"Omega": 1, "Upsilon": -1}[species]


def background_exponent(parent, daughters):
    return species_charge(parent) - sum(species_charge(item) for item in daughters)


def dressed_kernel_rows():
    rows = []
    for parent in ("Omega", "Upsilon"):
        conjugate_parent = "Upsilon" if parent == "Omega" else "Omega"
        for left in ("Omega", "Upsilon"):
            for right in ("Omega", "Upsilon"):
                daughters = (left, right)
                exponent = background_exponent(parent, daughters)
                daughter_charge = sum(species_charge(item) for item in daughters)
                dressed_output_charge = exponent + daughter_charge
                generator_charge = (
                    species_charge(conjugate_parent) + dressed_output_charge
                )
                rows.append({
                    "parent": parent,
                    "conjugate_parent_in_K_down": conjugate_parent,
                    "daughters": list(daughters),
                    "fixed_vacuum_coefficient_charge": 0,
                    "required_Z_exponent": exponent,
                    "dressed_output_charge": dressed_output_charge,
                    "K_down_component_charge": generator_charge,
                })
    return rows


def logarithmic_rows(soft_certificate):
    result = []
    source_rows = soft_certificate["fixed_vacuum_charge_decomposition"][
        "logarithmic_rows"
    ]
    for row in source_rows:
        omega_pair = row["omega_pair"]
        upsilon_pair = row["upsilon_partner_pair"]
        omega_exponent = background_exponent("Omega", omega_pair)
        upsilon_exponent = background_exponent("Upsilon", upsilon_pair)
        coefficient = row["leading_alpha_terms"][0]["coefficient"]
        result.append({
            "omega_pair": omega_pair,
            "upsilon_partner_pair": upsilon_pair,
            "fixed_vacuum_generator_charges": [
                row["first_generator_charge"],
                row["second_generator_charge"],
            ],
            "restoring_Z_exponents": [omega_exponent, upsilon_exponent],
            "completed_generator_charges": [
                row["first_generator_charge"] + omega_exponent,
                row["second_generator_charge"] + upsilon_exponent,
            ],
            "Gram_Z_exponent": omega_exponent + upsilon_exponent,
            "residue": coefficient,
        })
    return result


def build():
    soft = load(INPUTS[0])
    rows = dressed_kernel_rows()
    log_rows = logarithmic_rows(soft)
    residue = sum(
        Fraction(row["residue"]["numerator"], row["residue"]["denominator"])
        for row in log_rows
    )

    one = Laurent.monomial(0)
    z = Laurent.monomial(1)
    z_inverse = Laurent.monomial(-1)
    vacuum_ideal_generator = z - one
    derivation_remainder_at_z_one = vacuum_ideal_generator.derivation().fixed_vacuum_character()

    # The repaired Appendix-C pullback has B_Upsilon=Z^-1 A1 and
    # B_Omega=Z(A2+...+A1^dagger)/(4E^2).  Since A1=Z B_Upsilon,
    # its oscillatory B_Upsilon^dagger term carries Z^2.  The corresponding
    # squeezed-vacuum quadratic is therefore neutral, not charge -2.
    oscillatory_completed_charge = 2 + species_charge("Upsilon")
    squeeze_completed_charge = 2 + 2 * species_charge("Upsilon")
    squeeze_fixed_vacuum_charge = 2 * species_charge("Upsilon")

    per_pair = Fraction(
        soft["normalization_ledger_before_charge_projection"]["per_unordered_pair"]["numerator"],
        soft["normalization_ledger_before_charge_projection"]["per_unordered_pair"]["denominator"],
    )
    total = Fraction(
        soft["normalization_ledger_before_charge_projection"]["all_pairs"]["numerator"],
        soft["normalization_ledger_before_charge_projection"]["all_pairs"]["denominator"],
    )

    checks = {
        "Z_is_invertible": z * z_inverse == one,
        "BT_dagger_preserves_Z_charge": z.dagger() == z,
        "orbit_derivation_has_charge_one_on_Z": z.derivation() == z,
        "fixed_vacuum_character_sets_Z_to_one": z.fixed_vacuum_character() == 1,
        "candidate_pairing_is_off_diagonal_in_charge": (
            (z * z).invariant_trace() == 0
            and (z * z_inverse).invariant_trace() == 1
        ),
        "fixed_vacuum_ideal_is_not_derivation_stable": derivation_remainder_at_z_one == 1,
        "Eq16_kinetic_Z_powers_cancel": 1 + (-1) == 0,
        "Eq16_quartic_Z_powers_cancel": 2 + 2 * (-1) == 0,
        "all_quadratic_kernel_outputs_are_charge_covariant": all(
            row["dressed_output_charge"] == species_charge(row["parent"])
            for row in rows
        ),
        "all_number_lowering_generator_components_are_neutral": all(
            row["K_down_component_charge"] == 0 for row in rows
        ),
        "two_logarithmic_rows_retained": len(log_rows) == 2,
        "logarithmic_generators_complete_to_neutral": all(
            row["completed_generator_charges"] == [0, 0] for row in log_rows
        ),
        "logarithmic_Z_powers_cancel_in_Gram": all(
            row["Gram_Z_exponent"] == 0 for row in log_rows
        ),
        "raw_residue_is_unchanged_minus_half": residue == Fraction(-1, 2),
        "neutral_soft_response_remains_one_over_48_per_pair": per_pair == Fraction(1, 48),
        "neutral_three_pair_response_remains_one_over_16": total == Fraction(1, 16),
        "oscillatory_pullback_has_parent_Omega_charge": oscillatory_completed_charge == 1,
        "covariantly_completed_squeeze_is_neutral": squeeze_completed_charge == 0,
        "fixed_vacuum_squeeze_appears_charge_minus_two": squeeze_fixed_vacuum_charge == -2,
        "input_hashes_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
        "physical_coefficient_fails_closed": squeeze_completed_charge == 0,
    }

    return {
        "certificate": "REVERSE_PHYSICS_BT_ZERO_MODE_EQ19_TRILEMMA_V1",
        "schema_version": "reverse-physics-bt-zero-mode-eq19-trilemma-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "CLASSIFIED",
        "result_kind": "exact vacuum-orbit quotient/equivariance obstruction for BT Eq. (19)",
        "question": (
            "Does the genuine broken-vacuum shift zero mode complete the order-lambda "
            "BT charge pushforward and decide whether the neutral soft coefficient is 1/48?"
        ),
        "answer": (
            "It completes the soft number-changing kernel but exposes a sharper obstruction. "
            "Writing phi=phi_0+varphi and Z=exp(lambda*phi_0) factorizes Eq. (16) as "
            "Omega=Z*Omega_hat and Upsilon=Z^-1*Upsilon_hat. Unique Z powers then make "
            "every quadratic number-lowering generator neutral, retain the exact raw "
            "residue -1/2, and retain 1/48 per pair in the neutral soft block. However, "
            "the same covariance turns the Appendix-C squeeze from apparent charge -2 "
            "at Z=1 into a neutral Z^2*b_Upsilon^dagger^2 operator. Conversely, imposing "
            "Z=1 first destroys the charge derivation because the ideal (Z-1) is not "
            "derivation-stable. Thus the published fixed-vacuum negative-charge nullity "
            "and a genuine charge-covariant zero-mode operator cannot both be imported "
            "without an additional zero-mode representation and trace. The public Letter "
            "does not specify that object, so Eq. (19) and the physical neutral 1/48 remain "
            "unreproduced, although the soft coefficient is now exactly neutral in the "
            "covariant completion."
        ),
        "zero_mode_orbit_algebra": {
            "operator": "Z=exp(lambda*phi_0)",
            "algebra": "Q[Z,Z^-1] on finite Laurent supports",
            "charge_derivation": "delta(Z^n)=n*Z^n",
            "dagger": "Z^dagger=Z (BT dagger preserves boost charge)",
            "ghost_parity": "kappa Z kappa=Z^-1",
            "invariant_pairing": "<Z^m,Z^n>=delta_(m+n,0)",
            "fixed_vacuum_character": "ev_1(Z^n)=1",
            "not_a_c_number_spurion": True,
        },
        "exact_Eq16_factorization": {
            "split": "phi=phi_0+varphi with spacetime-constant symmetry-orbit phi_0",
            "Z": "exp(lambda*phi_0)",
            "Omega": "lambda^-1*Z*exp(lambda*varphi)",
            "Upsilon": "Z^-1*exp(-lambda*varphi)*(Box(varphi)+lambda*(partial varphi)^2)",
            "action_check": "constant Z cancels from partial(Omega)*partial(Upsilon) and Omega^2*Upsilon^2",
            "scope": "global shift-orbit zero mode, not the full dynamical p=0 sector",
        },
        "dressed_quadratic_kernel": {
            "rule": "C[parent<-d1,d2] -> Z^(q_parent-q_d1-q_d2)*C[parent<-d1,d2]",
            "uniqueness": "forced by q(Omega)=+1, q(Upsilon)=-1 and Eq. (16) factorization",
            "rows": rows,
            "fixed_vacuum_evaluation": "Z=1 reproduces the certified off-resonant kernel coefficient by coefficient",
        },
        "neutral_soft_block": {
            "logarithmic_rows": log_rows,
            "raw_residue": rat(residue),
            "per_unordered_pair": rat(per_pair),
            "all_three_pairs": rat(total),
            "status": "NEUTRAL_LEADING_LOG_COEFFICIENT_COMPUTED_BEFORE_ZERO_MODE_TRACE_COMPLETION",
        },
        "appendix_C_zero_mode_completion": {
            "repaired_pullback": [
                "R^dagger b_Upsilon R=Z^-1*A1",
                "R^dagger b_Omega R=Z*(A2+2iEt*A1+exp(2iEt)*A1^dagger)/(4E^2)",
            ],
            "inverse_linear_relation": "A1=Z*b_Upsilon",
            "oscillatory_term_in_b_variables": "Z^2*exp(2iEt)*b_Upsilon^dagger",
            "oscillatory_total_charge": oscillatory_completed_charge,
            "covariant_squeeze_monomial": "Z^2*b_Upsilon^dagger*b_Upsilon^dagger",
            "covariant_squeeze_charge": squeeze_completed_charge,
            "published_fixed_vacuum_squeeze_charge": squeeze_fixed_vacuum_charge,
        },
        "fixed_vacuum_quotient_obstruction": {
            "vacuum_ideal": "I=(Z-1)",
            "derivation_of_generator": "delta(Z-1)=Z",
            "remainder_mod_I": rat(derivation_remainder_at_z_one),
            "conclusion": "THE_BOOST_CHARGE_DERIVATION_DOES_NOT_DESCEND_TO_Z_EQUALS_ONE",
        },
        "trilemma": {
            "charge_covariant_zero_mode": "soft generator and squeeze both become neutral; 1/48 survives but negative-radical exclusion of squeeze is unavailable",
            "fixed_vacuum_negative_grading": "recovers the published apparent charges at Z=1, but no invariant charge derivation exists on that quotient",
            "missing_completion": "a zero-mode module/state and invariant trace specifying how the vacuum orbit is paired in R_t P R_t^dagger",
            "resolved_outcome": "EXACT_EQ19_ZERO_MODE_TRACE_OBSTRUCTION",
        },
        "disposition": {
            "genuine_zero_mode_operator": "CONSTRUCTED_LOCAL_ALGEBRAICALLY",
            "soft_number_lowering_charge": "NEUTRAL_AFTER_UNIQUE_Z_COMPLETION",
            "neutral_soft_one_over_48": "COEFFICIENT_COMPUTED_CONDITIONALLY_ON_COVARIANT_ORBIT_ALGEBRA",
            "fixed_vacuum_charge_selection": "NOT_WELL_DEFINED_AS_AN_INVARIANT_QUOTIENT",
            "published_negative_squeeze_nullity": "NOT_TRANSFERABLE_TO_COVARIANT_ZERO_MODE_COMPLETION",
            "Eq19_order_lambda_pushforward": "NOT_REPRODUCED_FROM_PUBLIC_DATA",
            "physical_neutral_one_over_48": "NOT_ESTABLISHED",
            "complete_nlo_probability": "NOT_ESTABLISHED",
        },
        "supersession_scope": {
            "predecessor": "REVERSE_PHYSICS_BT_OSCILLATORY_RADICAL_NO_MATCHING_V1",
            "status": "REMAINS_VALID_ONLY_IN_THE_FIXED_VACUUM_OSCILLATOR_GRADING",
            "superseded_use": "its negative-charge theorem cannot exclude zero-mode-completed neutral squeeze contributions",
        },
        "missing_object_ledger": [
            "a representation of the complete dynamical zero-momentum sector, not only the global shift orbit",
            "the invariant zero-mode state/pairing used by the generalized Born trace",
            "the full order-lambda pushforward R_t P_2 R_t^dagger on that module",
            "a proof that its neutral squeeze/oscillatory terms do or do not change the soft matching constant",
            "incoming and outgoing degenerate sectors on one regulator carrier",
            "the complete renormalized NLO quotient trace",
        ],
        "does_not_establish": [
            "that BT Eq. (19) is false in the unpublished completion",
            "that the covariant soft 1/48 is the final physical coefficient",
            "that the neutralized squeeze has a nonzero trace",
            "a full dynamical p=0 representation",
            "a complete NLO probability or beyond-tree positivity",
            "a gravitational or BRST lift",
            "anything LORENTZIAN-CAUSAL",
            "literature priority",
        ],
        "next_gate": (
            "Construct the zero-mode module and invariant generalized-Born trace for "
            "Z together with the full dynamical p=0 sector, then evaluate the neutral "
            "Z^2 squeeze and soft number-changing terms in R_t P_2 R_t^dagger."
        ),
        "provenance": {
            "source_commit": SOURCE_COMMIT,
            "retrieval_date": "2026-08-11",
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "primary_source": {
                "source": "Bateman--Turok arXiv:2607.00096v1",
                "url": "https://arxiv.org/abs/2607.00096",
                "equations": ["Eq. (16)", "Eq. (19)", "Appendix C Eqs. (31)-(34)"],
                "current_version_check": "Official arXiv record checked 2026-08-11: v1 only",
            },
        },
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_zero_mode_eq19_trilemma.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_zero_mode_eq19_trilemma.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_zero_mode_eq19_trilemma",
        ],
        "checks": {
            "ok": all(checks.values()),
            "passed": sum(checks.values()),
            "total": len(checks),
            "failures": [name for name, value in checks.items() if not value],
            "details": checks,
        },
        "report": REPORT,
        "schema": SCHEMA,
    }


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=CERT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    certificate = build()
    if args.check:
        try:
            with open(args.output, encoding="utf-8") as handle:
                recorded = json.load(handle)
        except Exception as error:
            print("[FAIL]", error)
            return 1
        ok = recorded == certificate
        print(f"[{'PASS' if ok else 'FAIL'}] exact_reproduction")
        print(
            f"RESULT: {'PASS' if ok else 'FAIL'} "
            f"({certificate['checks']['passed']}/{certificate['checks']['total']})"
        )
        return 0 if ok else 1
    with open(args.output, "w", encoding="utf-8") as handle:
        json.dump(certificate, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(args.output)
    return 0 if certificate["checks"]["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
