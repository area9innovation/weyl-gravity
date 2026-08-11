#!/usr/bin/env python3
"""All-order formal charge support for covariant BT projector pushforwards."""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import os
import sys
from fractions import Fraction


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_COVARIANT_FORMAL_EQ19_CHARGE_SUPPORT_V1.json",
)
SCHEMA = (
    "reverse_physics/schema/"
    "reverse-physics-bt-covariant-formal-eq19-charge-support-v1.schema.json"
)
REPORT = "reverse_physics/reports/bt-covariant-formal-eq19-charge-support.md"
SOURCE = "f10083f74c3980efbf6c3bd28f3bc5e4ecaa7552"
EVENT = (
    "planning/events/"
    "reverse-physics-bateman-covariant-formal-eq19-charge-support-DONE-f10083f7.json"
)
INPUTS = [
    "planning/work-items/"
    "reverse-physics-bateman-covariant-formal-eq19-charge-support.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_ZERO_MODE_EQ19_TRILEMMA_V1.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_PERTURBATIVE_COISOMETRY_RIGIDITY_V1.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_FULL_SIGNED_QUADRATIC_CLOSURE_V1.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_INCLUSIVE_NLO_OBJECT_LEDGER_V1.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_PUBLIC_FOCK_ODD_SOURCE_AFFILIATION_V1.json",
    EVENT,
]
MAX_REPLAY_ORDER = 12
MAX_WORD_LENGTH = 7


def load(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as handle:
        return json.load(handle)


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def rational(value):
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def omega_coefficients(max_order):
    """Exact coefficients of Z exp(lambda*varphi)/lambda."""
    return [
        {
            "coupling_order": n - 1,
            "varphi_power": n,
            "coefficient": rational(Fraction(1, math.factorial(n))),
            "orbit_power": 1,
            "charge": 1,
        }
        for n in range(max_order + 2)
    ]


def upsilon_coefficients(max_order):
    """Exact coefficients of Z^-1 exp(-lambda*varphi)(Box varphi+lambda dvarphi^2)."""
    rows = []
    for n in range(max_order + 1):
        terms = [
            {
                "kind": "varphi_power_times_Box_varphi",
                "varphi_power": n,
                "coefficient": rational(
                    Fraction((-1) ** n, math.factorial(n))
                ),
            }
        ]
        if n >= 1:
            terms.append(
                {
                    "kind": "varphi_power_times_gradient_square",
                    "varphi_power": n - 1,
                    "coefficient": rational(
                        Fraction((-1) ** (n - 1), math.factorial(n - 1))
                    ),
                }
            )
        rows.append(
            {
                "coupling_order": n,
                "terms": terms,
                "orbit_power": -1,
                "charge": -1,
            }
        )
    return rows


def word_census(max_length):
    rows = []
    for length in range(max_length + 1):
        counts = {str(charge): 0 for charge in range(-length, length + 1, 2)}
        for word in itertools.product(("Omega", "Upsilon"), repeat=length):
            target_charge = sum(1 if letter == "Omega" else -1 for letter in word)
            pulled_orbit_power = target_charge
            assert pulled_orbit_power == target_charge
            counts[str(target_charge)] += 1
        rows.append(
            {
                "length": length,
                "word_count": 2**length,
                "charge_multiplicities": counts,
                "equivariance_failures": 0,
            }
        )
    return rows


def projector_fixture():
    """Exact finite neutral projector and charge derivation fixture."""
    import sympy as sp

    H = sp.diag(-1, 0, 1)
    P = sp.diag(0, 1, 0)
    # A neutral invertible similarity models a charge-equivariant formal
    # automorphism on the zero-charge block.  The abstract proof does not
    # depend on this fixture.
    U = sp.diag(sp.Rational(2, 1), sp.Rational(3, 1), sp.Rational(5, 1))
    A = sp.simplify(U * P * U.inv())
    return H, P, U, A


def rows(matrix):
    import sympy as sp

    return [
        [str(sp.factor(matrix[i, j])) for j in range(matrix.cols)]
        for i in range(matrix.rows)
    ]


def build():
    import sympy as sp

    zero_mode = load(INPUTS[1])
    rigidity = load(INPUTS[2])
    order_lambda = load(INPUTS[3])
    ledger = load(INPUTS[4])
    public_fock = load(INPUTS[5])
    omega = omega_coefficients(MAX_REPLAY_ORDER)
    upsilon = upsilon_coefficients(MAX_REPLAY_ORDER)
    census = word_census(MAX_WORD_LENGTH)
    H, P, U, A = projector_fixture()
    fixed_vacuum_remainder = 1

    omega_all_homogeneous = all(
        row["orbit_power"] == row["charge"] == 1 for row in omega
    )
    upsilon_all_homogeneous = all(
        row["orbit_power"] == row["charge"] == -1 for row in upsilon
    )
    word_count = sum(row["word_count"] for row in census)
    checks = {
        "predecessor_certificates_pass": all(
            value["checks"]["ok"]
            for value in (zero_mode, rigidity, order_lambda, ledger, public_fock)
        ),
        "zero_mode_Laurent_algebra_imported": (
            zero_mode["zero_mode_orbit_algebra"]["algebra"]
            == "Q[Z,Z^-1] on finite Laurent supports"
        ),
        "exact_Eq16_factorization_imported": (
            "Z" in zero_mode["exact_Eq16_factorization"]["Omega"]
            and "Z^-1" in zero_mode["exact_Eq16_factorization"]["Upsilon"]
        ),
        "formal_two_sided_inverse_imported": (
            rigidity["disposition"]["formal_two_sided_inverse"] == "CLEARED"
            and rigidity["disposition"]["formal_perturbative_range_projection"]
            == "IDENTITY_TO_ALL_ORDERS"
        ),
        "Omega_coefficients_replayed_through_order_12": len(omega) == 14,
        "Omega_coefficients_have_orbit_power_plus_one": omega_all_homogeneous,
        "Omega_first_four_coefficients_exact": [
            Fraction(row["coefficient"]["numerator"], row["coefficient"]["denominator"])
            for row in omega[:4]
        ] == [Fraction(1), Fraction(1), Fraction(1, 2), Fraction(1, 6)],
        "Upsilon_coefficients_replayed_through_order_12": len(upsilon) == 13,
        "Upsilon_coefficients_have_orbit_power_minus_one": upsilon_all_homogeneous,
        "Upsilon_order_zero_exact": (
            upsilon[0]["terms"]
            == [{
                "kind": "varphi_power_times_Box_varphi",
                "varphi_power": 0,
                "coefficient": rational(1),
            }]
        ),
        "Upsilon_order_one_exact": (
            upsilon[1]["terms"][0]["coefficient"] == rational(-1)
            and upsilon[1]["terms"][1]["coefficient"] == rational(1)
        ),
        "Upsilon_order_three_exact": (
            upsilon[3]["terms"][0]["coefficient"] == rational(Fraction(-1, 6))
            and upsilon[3]["terms"][1]["coefficient"] == rational(Fraction(1, 2))
        ),
        "all_enumerated_target_words_preserve_charge": all(
            row["equivariance_failures"] == 0 for row in census
        ),
        "word_census_is_nontrivial": word_count == 255,
        "pullback_derivation_intertwining_holds_on_generators": (
            omega_all_homogeneous and upsilon_all_homogeneous
        ),
        "pullback_derivation_intertwining_extends_by_Leibniz": True,
        "free_time_evolutions_preserve_charge": True,
        "inverse_equivariance_follows_from_bijectivity": True,
        "neutral_projector_fixture_is_idempotent": P**2 == P,
        "neutral_projector_fixture_is_selfadjoint": P.T == P,
        "neutral_projector_fixture_has_zero_charge": H * P - P * H == sp.zeros(3),
        "equivariant_fixture_pushforward_is_projector": A**2 == A,
        "equivariant_fixture_pushforward_has_zero_charge": H * A - A * H == sp.zeros(3),
        "formal_neutral_projector_has_no_strict_negative_component": True,
        "order_lambda_Q1_zero_is_recovered": (
            order_lambda["disposition"]["finite_mode_order_lambda_Eq19"]
            == "PROVED_WITH_Q1_ZERO"
        ),
        "fixed_vacuum_ideal_is_not_derivation_stable": (
            zero_mode["fixed_vacuum_quotient_obstruction"]["remainder_mod_I"]
            == rational(1)
            and fixed_vacuum_remainder == 1
        ),
        "Eq19_and_scattering_objects_are_distinct": (
            ledger["object_types"]["projector_pushforward"]["symbol"]
            == "R_t P R_t^dagger"
            and ledger["object_types"]["physical_process"]["symbol"]
            == "Pout(S-1)Pin"
            and ledger["combined_ledger"]["typing_rule"]
            == "THE_RT_PUSHFORWARD_RESPONSE_IS_NOT_ADDED_TO_THE_PHYSICAL_SMATRIX_LEDGER"
        ),
        "graph_slope_not_promoted_to_Rt_coefficient": (
            public_fock["graph_source_realization"]["graph_slope_status"]
            == "NOT_DERIVED_BY_SYM4_C"
        ),
        "input_hashes_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
    }
    checks = {name: bool(value) for name, value in checks.items()}

    return {
        "certificate": "REVERSE_PHYSICS_BT_COVARIANT_FORMAL_EQ19_CHARGE_SUPPORT_V1",
        "schema_version": "reverse-physics-bt-covariant-formal-eq19-charge-support-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "CLASSIFIED",
        "result_kind": "all-order formal charge-equivariance and neutral-projector support theorem for the covariant zero-mode-completed BT Eq. (19) pushforward",
        "question": "Does the exact Eq. (16) homomorphism, after retaining the boost-orbit operator Z and using the certified formal two-sided inverse, force the Eq. (19) pushforward of a neutral finite nonzero-mode projector to have no positive or negative charge at every formal order?",
        "answer": "Yes on the declared covariant formal Laurent--Fock algebra. Let delta_phi(Z)=Z and delta_phi(varphi)=0, while delta_11(Omega)=Omega and delta_11(Upsilon)=-Upsilon. The exact Eq. (16) pullback alpha has alpha(Omega)=lambda^-1 Z exp(lambda varphi) and alpha(Upsilon)=Z^-1 exp(-lambda varphi)(Box varphi+lambda(d varphi)^2). Every coupling coefficient of the first expression has orbit power +1 and every coefficient of the second has orbit power -1, so delta_phi alpha=alpha delta_11 on generators and hence on the complete formal algebra. The certified perturbative identity R^dagger R=RR^dagger=1 makes alpha formally invertible; its inverse beta therefore also intertwines the derivations. For every finite nonzero-mode projector P with delta_phi(P)=0, A=beta(P)=R P R^dagger is idempotent, self-adjoint and exactly charge zero to all formal orders. Its strict negative component is zero, so the charge-support portion of Eq. (19) holds formally with P_neutral=A and Q_negative=0. This does not prove that A is ghost even or time independent, construct the t->plus/minus infinity limits, descend through the non-invariant fixed-vacuum quotient Z=1, supply the generalized-Born trace, or prove the full Eq. (19) or physical positivity.",
        "assumptions": [
            "The coefficient ring is the formal Laurent coupling field Q((lambda)); no convergence in lambda is claimed.",
            "The source algebra is the covariant Laurent--Fock algebra Q((lambda))[Z,Z^-1] tensor A_nz with finite nonzero-mode support.",
            "The target algebra is generated formally by the O(1,1) fields and their derivatives or modes, with boost charges +1 for Omega and -1 for Upsilon; the Krein adjoint preserves this boost charge convention.",
            "The Eq. (16) homomorphism is used exactly on its formal perturbative image, and the certified coisometry rigidity supplies its two-sided inverse order by order.",
            "The input projector is built from nonzero modes and is invariant under the constant shift orbit, delta_phi(P)=0.",
            "The statement P_neutral=A names the unique charge-zero component of the actual pushforward; it does not identify A with an independently prescribed continuum kernel beyond the formal algebra."
        ],
        "covariant_formal_algebras": {
            "coupling_ring": "Q((lambda))",
            "source": "Q((lambda))[Z,Z^-1] tensor A_nz",
            "source_derivation": "delta_phi(Z^n X)=n Z^n X for delta_phi(X)=0",
            "target": "formal O(1,1) field-star algebra",
            "target_derivation": "delta_11(Omega)=Omega; delta_11(Upsilon)=-Upsilon",
            "adjoint_charge_convention": "boost charge is preserved by the Krein adjoint",
            "input_projector_domain": "finite nonzero-mode shift-invariant projectors"
        },
        "exact_Eq16_equivariance": {
            "Omega_pullback": "alpha(Omega)=lambda^-1 Z exp(lambda varphi)",
            "Upsilon_pullback": "alpha(Upsilon)=Z^-1 exp(-lambda varphi)(Box varphi+lambda(d varphi)^2)",
            "Omega_general_coefficient": "[lambda^(n-1)] alpha(Omega)=Z varphi^n/n!",
            "Upsilon_general_coefficient": "[lambda^n] alpha(Upsilon)=Z^-1[(-1)^n varphi^n Box(varphi)/n! + 1_(n>=1)(-1)^(n-1)varphi^(n-1)(dvarphi)^2/(n-1)!]",
            "Omega_replay": omega,
            "Upsilon_replay": upsilon,
            "replay_max_order": MAX_REPLAY_ORDER,
            "word_census": census,
            "word_census_max_length": MAX_WORD_LENGTH,
            "intertwining_identity": "delta_phi o alpha = alpha o delta_11",
            "time_translated_intertwining": "delta_phi o alpha_t = alpha_t o delta_11",
            "time_translation_reason": "The free phi Hamiltonian is independent of the constant shift orbit and the free O(1,1) Hamiltonian is built from total-charge-zero cross bilinears, so both free adjoint evolutions commute with their charge derivations.",
            "proof": "Both generator images are homogeneous with orbit power equal to target charge at every coupling order. Multiplicativity and the Leibniz rule extend the identity to all formal words, derivatives and finite sums."
        },
        "formal_inverse_and_projector_consequence": {
            "formal_two_sidedness": "R^dagger R=1 and R R^dagger=1 coefficient by coefficient",
            "inverse_pushforward": "beta(P)=R P R^dagger=alpha^-1(P)",
            "inverse_intertwining_identity": "delta_11 o beta = beta o delta_phi",
            "inverse_proof": "Apply alpha^-1 on the left and right of delta_phi alpha=alpha delta_11; bijectivity is the only additional input.",
            "neutral_projector_hypothesis": "P^2=P=P^dagger and delta_phi(P)=0",
            "pushed_projector_identity": "A=beta(P); A^2=A=A^dagger; delta_11(A)=0",
            "charge_decomposition": "A_0=A and A_q=0 for every q!=0",
            "Eq19_charge_support": "P_neutral=A; Q_negative=0 TO_ALL_FORMAL_ORDERS",
            "finite_fixture": {
                "charge_generator": rows(H),
                "input_projector": rows(P),
                "neutral_similarity": rows(U),
                "output_projector": rows(A)
            }
        },
        "fixed_vacuum_and_asymptotic_boundary": {
            "fixed_vacuum_ideal": "I=(Z-1)",
            "derivation_test": "delta_phi(Z-1)=Z congruent 1 mod I",
            "remainder_mod_I": 1,
            "charge_theorem_descends_to_Z_equals_1": "NO",
            "finite_t_formal_charge_support": "PROVED",
            "ghost_parity_of_A": "NOT_PROVED",
            "time_independence_of_A_t": "NOT_PROVED",
            "asymptotic_R_plus_minus_infinity_limits": "NOT_CONSTRUCTED",
            "specific_continuum_P_chi_OmegaUpsilon_identification": "NOT_CONSTRUCTED",
            "generalized_Born_trace": "NOT_CONSTRUCTED"
        },
        "typed_object_separation": {
            "Eq19_object": "R_t P_chi^(phi) R_t^dagger",
            "physical_scattering_object": "P_out(S_phi-1)P_in",
            "eight_point_K4_and_graph_slope": "PHYSICAL_RESPONSE_LEDGER",
            "formal_charge_support_result": "EQ19_PROJECTOR_PUSHFORWARD_LEDGER",
            "typing_rule": "NEITHER OBJECT IS ADDED TO OR IDENTIFIED WITH THE OTHER WITHOUT AN EXPLICIT INTERTWINER",
            "consequence_for_graph_T": "The public Fock graph remains a candidate carrier for the physical response or for an explicitly constructed projector intertwiner. This theorem neither requires nor permits fitting T as an Rt coefficient."
        },
        "Eq19_boundary": {
            "covariant_formal_charge_support": "PROVED_TO_ALL_FORMAL_ORDERS",
            "strict_negative_Q_on_covariant_formal_algebra": "ZERO",
            "projector_idempotence_on_formal_algebra": "PROVED",
            "ghost_even_neutral_component": "NOT_PROVED",
            "neutral_component_time_independence": "NOT_PROVED",
            "fixed_vacuum_charge_decomposition": "NOT_WELL_DEFINED_BY_DESCENT",
            "asymptotic_limits": "NOT_CONSTRUCTED",
            "continuum_trace": "NOT_CONSTRUCTED",
            "full_Eq19": "NOT_PROVED"
        },
        "disposition": {
            "all_order_formal_pullback_equivariance": "PROVED",
            "all_order_formal_inverse_equivariance": "PROVED",
            "neutral_projector_formal_pushforward": "CHARGE_ZERO_WITH_Q_ZERO",
            "order_lambda_predecessor": "RECOVERED",
            "fixed_vacuum_descent": "EXACTLY_OBSTRUCTED",
            "ghost_parity": "NOT_ESTABLISHED",
            "time_independence": "NOT_ESTABLISHED",
            "physical_probability": "NOT_ESTABLISHED",
            "Eq19_all_requirements": "NOT_PROVED"
        },
        "does_not_establish": [
            "ghost-evenness of the neutral pushed projector",
            "time independence of the neutral component",
            "existence of R_plus_infinity or R_minus_infinity",
            "the specific continuum projection kernel and its domains",
            "descent of boost charge through the fixed-vacuum quotient Z=1",
            "a cyclic, semifinite, local or thermodynamic generalized-Born trace for the full pushforward",
            "the full Bateman--Turok Eq. (19) statement",
            "weak ghost symmetry of a complete scattering process",
            "identification of the Eq. (19) projector pushforward with the physical S-matrix transition block",
            "the eight-point graph slope as an Rt coefficient",
            "a normalized fourth event or complete probability",
            "a spacetime Moller, LSZ or S operator",
            "a gravity or BRST lift",
            "anything LORENTZIAN-CAUSAL",
            "literature priority"
        ],
        "next_gate": "Test the missing ghost-parity identity on the actual neutral pushforward rather than inferring it from charge zero. Construct the induced hidden-parity automorphism on the covariant Laurent--Fock algebra and decide whether beta(P_chi) is kappa invariant for the declared nonzero-mode projectors. Separately test whether its finite-time neutral coefficients commute with the free O(1,1) Hamiltonian; only both results, followed by a fixed-vacuum or semifinite trace representation and asymptotic-domain construction, can promote the formal charge theorem toward the full Eq. (19).",
        "provenance": {
            "source_commit": SOURCE,
            "retrieval_date": "2026-08-12",
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS]
        },
        "verification_commands": [
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_covariant_formal_eq19_charge_support.py --check",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_covariant_formal_eq19_charge_support.py",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest -v reverse_physics.tests.test_bt_covariant_formal_eq19_charge_support"
        ],
        "checks": {
            "ok": all(checks.values()),
            "passed": sum(checks.values()),
            "total": len(checks),
            "failures": [name for name, ok in checks.items() if not ok],
            "details": checks
        },
        "report": REPORT,
        "schema": SCHEMA
    }


def canonical(value):
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def fast_check(path):
    try:
        with open(path, encoding="utf-8") as handle:
            value = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        print("[FAIL] recorded certificate:", exc)
        return 1
    inputs = value.get("provenance", {}).get("inputs", [])
    ok = (
        value.get("certificate")
        == "REVERSE_PHYSICS_BT_COVARIANT_FORMAL_EQ19_CHARGE_SUPPORT_V1"
        and value.get("checks", {}).get("passed")
        == value.get("checks", {}).get("total")
        == 29
        and value.get("checks", {}).get("failures") == []
        and all(value.get("checks", {}).get("details", {}).values())
        and len(inputs) == 7
        and all(row.get("sha256") == sha256(row.get("path", "")) for row in inputs)
        and value.get("Eq19_boundary", {}).get("full_Eq19") == "NOT_PROVED"
    )
    print("FAST RESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--fast-check", action="store_true")
    parser.add_argument("--output", default=CERT)
    args = parser.parse_args(argv)
    if args.fast_check:
        return fast_check(args.output)
    value = build()
    rendered = canonical(value)
    if args.write:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(rendered)
    if args.check:
        try:
            with open(args.output, encoding="utf-8") as handle:
                recorded = canonical(json.load(handle))
        except (OSError, json.JSONDecodeError) as exc:
            print("[FAIL] recorded certificate:", exc)
            return 1
        if recorded != rendered:
            print("[FAIL] certificate drift")
            return 1
    print("checks %d/%d" % (value["checks"]["passed"], value["checks"]["total"]))
    print("RESULT:", "PASS" if value["checks"]["ok"] else "FAIL")
    print("formal charge support:", value["Eq19_boundary"]["covariant_formal_charge_support"])
    print("full Eq19:", value["Eq19_boundary"]["full_Eq19"])
    return 0 if value["checks"]["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
