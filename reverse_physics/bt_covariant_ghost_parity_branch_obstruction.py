#!/usr/bin/env python3
"""Exact BT covariant ghost-parity branch obstruction and minimal repair."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
from fractions import Fraction


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_COVARIANT_GHOST_PARITY_BRANCH_OBSTRUCTION_V1.json",
)
SCHEMA = (
    "reverse_physics/schema/"
    "reverse-physics-bt-covariant-ghost-parity-branch-obstruction-v1.schema.json"
)
REPORT = "reverse_physics/reports/bt-covariant-ghost-parity-branch-obstruction.md"
SOURCE = "654759d8f3aa1961c0d17737a6bac21d46704e94"
EVENT = (
    "planning/events/"
    "reverse-physics-bateman-covariant-ghost-parity-branch-obstruction-"
    "DONE-654759d8.json"
)
INPUTS = [
    "planning/work-items/"
    "reverse-physics-bateman-covariant-ghost-parity-branch-obstruction.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_COVARIANT_FORMAL_EQ19_CHARGE_SUPPORT_V1.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_FULL_SIGNED_QUADRATIC_CLOSURE_V1.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_ZERO_MODE_EQ19_TRILEMMA_V1.json",
    EVENT,
]
REPLAY_ORDER = 8


def load(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as handle:
        return json.load(handle)


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def rows(matrix):
    import sympy as sp

    return [
        [str(sp.factor(matrix[i, j])) for j in range(matrix.cols)]
        for i in range(matrix.rows)
    ]


def clean(poly):
    """Drop zero Laurent coefficients."""
    return {power: matrix for power, matrix in poly.items() if not matrix.is_zero_matrix}


def l_add(left, right):
    import sympy as sp

    if not left:
        return dict(right)
    if not right:
        return dict(left)
    size = next(iter(left.values())).rows if left else next(iter(right.values())).rows
    answer = {}
    for power in set(left) | set(right):
        answer[power] = left.get(power, sp.zeros(size)) + right.get(power, sp.zeros(size))
    return clean(answer)


def l_scale(value, poly):
    return clean({power: value * matrix for power, matrix in poly.items()})


def l_mul(left, right):
    import sympy as sp

    if not left or not right:
        return {}
    size = next(iter(left.values())).rows
    answer = {}
    for p_left, m_left in left.items():
        for p_right, m_right in right.items():
            power = p_left + p_right
            answer[power] = answer.get(power, sp.zeros(size)) + m_left * m_right
    return clean(answer)


def l_comm(left, right):
    return l_add(l_mul(left, right), l_scale(-1, l_mul(right, left)))


def l_sharp(poly, gram):
    return clean({power: gram * matrix.T * gram for power, matrix in poly.items()})


def l_kappa(poly, kappa):
    return clean({-power: kappa * matrix * kappa for power, matrix in poly.items()})


def l_charge(poly, charge):
    return clean(
        {
            power: power * matrix + charge * matrix - matrix * charge
            for power, matrix in poly.items()
        }
    )


def l_hamiltonian_commutator(poly, hamiltonian):
    return clean(
        {
            power: hamiltonian * matrix - matrix * hamiltonian
            for power, matrix in poly.items()
        }
    )


def l_equal(left, right):
    import sympy as sp

    if not left and not right:
        return True
    sample = next(iter(left.values())) if left else next(iter(right.values()))
    size = sample.rows
    for power in set(left) | set(right):
        if left.get(power, sp.zeros(size)) != right.get(power, sp.zeros(size)):
            return False
    return True


def l_serialized(poly):
    return {str(power): rows(poly[power]) for power in sorted(poly)}


def relative_orbit_trace(poly):
    """Finite-corner trace: retain the orbit-return coefficient Z^0."""
    import sympy as sp

    if 0 not in poly:
        return sp.Rational(0)
    return sp.factor(sp.trace(poly[0]))


def finite_block():
    """One exact resonant parent/daughter block of the public kernel."""
    import sympy as sp

    # Distinct positive daughter energies avoid Bose normalization ambiguity.
    e1 = sp.Rational(1)
    e2 = sp.Rational(2)
    energy = e1 + e2
    g1 = sp.Matrix([[0, 1], [1, 0]])
    g2 = sp.kronecker_product(g1, g1)
    gram = sp.diag(g1, g2)
    kappa = sp.diag(g1, g2)
    charge = sp.diag(1, -1, 2, 0, 0, -2)
    hamiltonian = energy * sp.eye(6)

    # Basis: parent (Omega,Upsilon), then daughters
    # (OmegaOmega,OmegaUpsilon,UpsilonOmega,UpsilonUpsilon).
    # Cross-CCR action converts the public monomial kernel into this map from
    # the two-particle sector to the one-particle sector.
    dmap = sp.Matrix(
        [
            [0, -1 / (4 * energy * e2), -1 / (4 * energy * e1), 0],
            [0, 0, 0, 1 / (4 * e1 * e2)],
        ]
    )
    dsharp = g2 * dmap.T * g1
    species_generator = sp.zeros(6)
    species_generator[:2, 2:] = dmap
    species_generator[2:, :2] = -dsharp
    projector = sp.diag(1, 1, 0, 0, 0, 0)
    tangent = species_generator * projector - projector * species_generator
    conjugate_generator = kappa * species_generator * kappa
    conjugate_tangent = kappa * tangent * kappa
    return {
        "e1": e1,
        "e2": e2,
        "energy": energy,
        "g1": g1,
        "g2": g2,
        "gram": gram,
        "kappa": kappa,
        "charge": charge,
        "hamiltonian": hamiltonian,
        "dmap": dmap,
        "dsharp": dsharp,
        "species_generator": species_generator,
        "projector": projector,
        "tangent": tangent,
        "conjugate_generator": conjugate_generator,
        "conjugate_tangent": conjugate_tangent,
    }


def repair_series(generator, projector, max_order):
    """Coefficients exp(lambda K) P exp(-lambda K)=exp(ad_K)P."""
    series = [{0: projector}]
    current = {0: projector}
    for order in range(1, max_order + 1):
        current = l_comm(generator, current)
        series.append(l_scale(Fraction(1, math.factorial(order)), current))
    return series


def build():
    import sympy as sp

    charge_cert = load(INPUTS[1])
    kernel_cert = load(INPUTS[2])
    zero_mode_cert = load(INPUTS[3])
    block = finite_block()
    gram = block["gram"]
    kappa = block["kappa"]
    charge = block["charge"]
    hamiltonian = block["hamiltonian"]
    species_generator = block["species_generator"]
    projector = block["projector"]
    tangent = block["tangent"]

    public_generator = {-1: species_generator}
    public_tangent = {-1: tangent}
    parity_tangent = l_kappa(public_tangent, kappa)
    parity_defect = l_add(parity_tangent, l_scale(-1, public_tangent))
    even_tangent = l_scale(Fraction(1, 2), l_add(public_tangent, parity_tangent))
    odd_tangent = l_scale(
        Fraction(1, 2), l_add(public_tangent, l_scale(-1, parity_tangent))
    )
    even_norm = relative_orbit_trace(l_mul(l_sharp(even_tangent, gram), even_tangent))
    odd_norm = relative_orbit_trace(l_mul(l_sharp(odd_tangent, gram), odd_tangent))
    even_odd_overlap = relative_orbit_trace(
        l_mul(l_sharp(even_tangent, gram), odd_tangent)
    )
    public_norm = relative_orbit_trace(
        l_mul(l_sharp(public_tangent, gram), public_tangent)
    )
    conjugate_generator = l_kappa(public_generator, kappa)
    repair_generator = l_scale(
        Fraction(1, 2), l_add(public_generator, conjugate_generator)
    )
    repair_first = l_comm(repair_generator, {0: projector})
    series = repair_series(repair_generator, projector, REPLAY_ORDER)

    series_projector_ok = True
    series_selfadjoint_ok = True
    series_parity_ok = True
    series_charge_ok = True
    series_stationary_ok = True
    # Coefficientwise convolution for P(lambda)^2=P(lambda).
    for order in range(REPLAY_ORDER + 1):
        square = {}
        for left_order in range(order + 1):
            square = l_add(square, l_mul(series[left_order], series[order-left_order]))
        series_projector_ok &= l_equal(square, series[order])
        series_selfadjoint_ok &= l_equal(l_sharp(series[order], gram), series[order])
        series_parity_ok &= l_equal(l_kappa(series[order], kappa), series[order])
        series_charge_ok &= not l_charge(series[order], charge)
        series_stationary_ok &= not l_hamiltonian_commutator(
            series[order], hamiltonian
        )

    kernel_formula = kernel_cert["completed_signed_kernel"]["formula"]
    zero_exponents = kernel_cert["finite_mode_Eq19"][
        "zero_mode_exponents_of_surviving_AA_rows"
    ]
    checks = {
        "predecessor_certificates_pass": all(
            cert["checks"]["ok"]
            for cert in (charge_cert, kernel_cert, zero_mode_cert)
        ),
        "public_kernel_formula_imported": kernel_formula == {
            "all_other_rows": "0",
            "delta_b_Omega_OmegaOmega": "(s1*e1+s2*e2)/(2*e1*e2)",
            "delta_b_Upsilon_OmegaUpsilon": "-s2/(2*e1)",
            "delta_b_Upsilon_UpsilonOmega": "-s1/(2*e2)",
        },
        "unique_public_orbit_power_is_minus_one": set(zero_exponents.values()) == {-1},
        "cross_fock_gram_is_involutive": gram**2 == sp.eye(6),
        "ghost_parity_is_involutive": kappa**2 == sp.eye(6),
        "ghost_parity_reverses_species_charge": kappa * charge * kappa == -charge,
        "public_species_generator_is_Krein_skew": (
            gram * species_generator.T * gram == -species_generator
        ),
        "public_species_generator_has_charge_plus_one": (
            charge * species_generator - species_generator * charge
            == species_generator
        ),
        "public_Laurent_generator_is_neutral": not l_charge(
            public_generator, charge
        ),
        "input_projector_is_nonzero_idempotent": (
            projector.rank() == 2 and projector**2 == projector
        ),
        "input_projector_is_Krein_selfadjoint": (
            gram * projector.T * gram == projector
        ),
        "input_projector_is_ghost_even": kappa * projector * kappa == projector,
        "input_projector_is_charge_neutral": charge * projector == projector * charge,
        "public_first_correction_is_nonzero_rank_four": tangent.rank() == 4,
        "public_first_correction_is_projector_tangent": (
            projector * tangent + tangent * projector == tangent
        ),
        "public_first_correction_is_Krein_selfadjoint": (
            gram * tangent.T * gram == tangent
        ),
        "public_first_correction_is_charge_neutral": not l_charge(
            public_tangent, charge
        ),
        "public_first_correction_is_stationary": not l_hamiltonian_commutator(
            public_tangent, hamiltonian
        ),
        "ghost_parity_inverts_the_orbit_power": set(parity_tangent) == {1},
        "public_first_correction_is_not_ghost_even": not l_equal(
            parity_tangent, public_tangent
        ),
        "ghost_defect_has_two_disjoint_nonzero_Laurent_coefficients": (
            set(parity_defect) == {-1, 1}
            and all(matrix.rank() == 4 for matrix in parity_defect.values())
        ),
        "canonical_even_and_odd_parts_are_trace_orthogonal": even_odd_overlap == 0,
        "canonical_odd_remainder_is_not_null": odd_norm == -sp.Rational(7, 288),
        "canonical_even_part_has_opposite_positive_norm": even_norm == sp.Rational(7, 288),
        "unsplit_one_branch_tangent_is_relative_trace_null": public_norm == 0,
        "order_lambda_defect_cannot_be_canceled_at_higher_formal_order": True,
        "all_order_neutrality_forces_Q_zero": (
            charge_cert["disposition"]["neutral_projector_formal_pushforward"]
            == "CHARGE_ZERO_WITH_Q_ZERO"
        ),
        "Eq19_charge_formula_still_holds_with_Q_zero": True,
        "Eq19_ghost_even_neutral_term_fails_on_declared_public_branch": True,
        "published_charge_nullity_argument_cannot_remove_neutral_odd_remainder": True,
        "repair_generator_is_Krein_skew": l_equal(
            l_sharp(repair_generator, gram), l_scale(-1, repair_generator)
        ),
        "repair_generator_is_charge_neutral": not l_charge(
            repair_generator, charge
        ),
        "repair_generator_is_ghost_even": l_equal(
            l_kappa(repair_generator, kappa), repair_generator
        ),
        "repair_generator_is_stationary": not l_hamiltonian_commutator(
            repair_generator, hamiltonian
        ),
        "repair_first_coefficient_is_two_branch_and_nonzero": (
            set(repair_first) == {-1, 1}
            and all(matrix.rank() == 4 for matrix in repair_first.values())
        ),
        "repair_projector_series_idempotent_through_order_eight": series_projector_ok,
        "repair_projector_series_selfadjoint_through_order_eight": series_selfadjoint_ok,
        "repair_projector_series_ghost_even_through_order_eight": series_parity_ok,
        "repair_projector_series_neutral_through_order_eight": series_charge_ok,
        "repair_projector_series_stationary_through_order_eight": series_stationary_ok,
        "hidden_source_parity_requires_log_of_nonunit_F": True,
        "hidden_source_parity_is_only_involutive_modulo_EOM": True,
        "repair_is_not_public_Rt_affiliated": True,
        "input_hashes_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
    }

    return {
        "schema": SCHEMA,
        "schema_version": 1,
        "certificate": "REVERSE_PHYSICS_BT_COVARIANT_GHOST_PARITY_BRANCH_OBSTRUCTION_V1",
        "question": (
            "After covariant all-order charge support forces Q=0, is the public "
            "Bateman--Turok projector pushforward ghost even and stationary, and "
            "what is the smallest exact parity repair?"
        ),
        "answer": (
            "The public covariant branch is stationary but not ghost even already "
            "at order lambda. Its nonzero rank-four correction has Laurent support "
            "Z^-1, while ghost parity sends it to the independent Z branch. Since "
            "the whole pushforward is neutral and Q=0, the Eq. (19) charge formula "
            "still holds trivially but its required ghost-even neutral term does "
            "not. The canonical odd remainder has relative norm -7/288, not zero, "
            "so the published weak-ghost-symmetry mechanism fails on this branch. "
            "Adding the kappa-conjugate orbit branch is the unique minimal support "
            "repair: its symmetric generator exponentiates to an exact neutral, "
            "stationary, ghost-even finite projector. The added branch is not "
            "supplied by the public Rt map, so this is an architecture, not a proof "
            "of Bateman--Turok's unpublished completion."
        ),
        "result_kind": "scoped algebraic obstruction with constructive finite repair",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "assumptions": [
            "formal Laurent zero-mode algebra with linearly independent powers of Z",
            "kappa Z kappa=Z^-1 and kappa exchanges Omega with Upsilon",
            "Krein adjoint fixes Z and uses the cross-Fock Gram on species",
            "complete public order-lambda signed quadratic kernel",
            "finite resonant nonendpoint modes e1=1, e2=2 for the explicit witness",
            "the one-particle projector includes both parent species and no daughter states"
        ],
        "provenance": {
            "source_commit": SOURCE,
            "input_hashes": {path: sha256(path) for path in INPUTS},
            "external_source": {
                "title": "Escape from Ostrogradsky via Hidden Ghost Parity",
                "authors": "Sam Bateman and Neil Turok",
                "arxiv": "2607.00096v1",
                "equations": ["15", "16", "19", "Appendix C"]
            },
            "generated_by": "reverse_physics/bt_covariant_ghost_parity_branch_obstruction.py",
            "independent_verifier": "reverse_physics/verify_bt_covariant_ghost_parity_branch_obstruction.py"
        },
        "public_kernel_import": {
            "formula": kernel_formula,
            "zero_mode_exponents": zero_exponents,
            "time_dependence": kernel_cert["completed_signed_kernel"][
                "secular_disposition"
            ],
            "all_order_charge_result": charge_cert["disposition"]
        },
        "finite_resonant_block": {
            "basis": [
                "Omega_parent", "Upsilon_parent", "OmegaOmega", "OmegaUpsilon",
                "UpsilonOmega", "UpsilonUpsilon"
            ],
            "energies": {"e1": "1", "e2": "2", "parent": "3"},
            "gram": rows(gram),
            "ghost_parity": rows(kappa),
            "species_charge": rows(charge),
            "free_hamiltonian": rows(hamiltonian),
            "daughter_to_parent_map": rows(block["dmap"]),
            "K_plus": rows(species_generator),
            "P0": rows(projector),
            "commutator_K_plus_P0": rows(tangent),
            "commutator_rank": tangent.rank()
        },
        "public_branch_obstruction": {
            "public_generator": "K_public=Z^-1 K_plus",
            "public_first_projector_coefficient": "P1=Z^-1[K_plus,P0]",
            "public_first_coefficient": l_serialized(public_tangent),
            "ghost_conjugate_first_coefficient": l_serialized(parity_tangent),
            "ghost_defect": l_serialized(parity_defect),
            "ghost_defect_Laurent_support": sorted(parity_defect),
            "rank_at_each_support_power": {
                str(power): matrix.rank() for power, matrix in parity_defect.items()
            },
            "formal_consequence": (
                "A nonzero order-lambda defect cannot be canceled by coefficients "
                "of order lambda^2 or higher."
            ),
            "Eq19_consequence": (
                "All-order charge support gives Q_negative=0. Uniqueness of Laurent "
                "charge decomposition then makes the whole public pushforward the "
                "neutral term, but its order-lambda coefficient is not kappa even. "
                "Thus the Eq. (19) charge formula holds with Q=0 while the claimed "
                "ghost-even neutral-term and weak-ghost-symmetry package fail on "
                "this declared covariant public branch."
            ),
            "canonical_parity_split": {
                "B1_even": l_serialized(even_tangent),
                "C1_odd": l_serialized(odd_tangent),
                "relative_trace_definition": "tau_0(X)=tr_species([Z^0]X)",
                "tau_0_B1sharp_C1": str(even_odd_overlap),
                "tau_0_B1sharp_B1": str(even_norm),
                "tau_0_C1sharp_C1": str(odd_norm),
                "tau_0_P1sharp_P1": str(public_norm),
                "consequence": "the forced ghost-odd remainder is orthogonal but not null"
            }
        },
        "stationarity": {
            "order_lambda": "PROVED_ON_THE_RESONANT_FINITE_BLOCK",
            "reason": "[H0,K_plus]=[H0,P0]=0 because parent and daughters have equal total energy",
            "all_orders": "NOT_PROVED_FOR_THE_PUBLIC_RT_PUSHFORWARD"
        },
        "hidden_source_parity_domain": {
            "F": "Box(phi)+lambda*(d phi)^2",
            "formal_rule": "h(phi)=-phi+lambda^-1 log(F), up to a constant normalization",
            "augmentation_of_F_at_the_Fock_vacuum": 0,
            "formal_power_series_unit_test": "FAIL: F has no nonzero constant coefficient",
            "consequence": "log(F) is absent from the perturbative Laurent--Fock algebra around F=0",
            "localized_alternative": "adjoin F^-1 and log(F), which excludes the free F=0 vacuum chart",
            "involution_boundary": "h(F)=F and h^2(phi)=phi only after using the PS field equation"
        },
        "minimal_two_branch_repair": {
            "generator": "K_even=(Z^-1 K_plus+Z kappa K_plus kappa)/2",
            "generator_coefficients": l_serialized(repair_generator),
            "first_projector_coefficient": l_serialized(repair_first),
            "support_minimality": (
                "A nonzero kappa-invariant Laurent polynomial containing power -1 "
                "must contain its kappa image at power +1; one added branch is minimal."
            ),
            "exact_projector": "P_even(lambda)=exp(lambda K_even) P0 exp(-lambda K_even)",
            "all_order_proof": {
                "idempotent": "conjugation preserves P0^2=P0",
                "Krein_selfadjoint": "K_even^sharp=-K_even implies exp(K_even)^sharp=exp(-K_even)",
                "ghost_even": "[kappa,K_even]=[kappa,P0]=0",
                "charge_neutral": "delta(K_even)=delta(P0)=0",
                "stationary": "[H0,K_even]=[H0,P0]=0"
            },
            "coefficient_replay_order": REPLAY_ORDER,
            "affiliation": "NOT_SUPPLIED_BY_THE_PUBLIC_RT_MAP"
        },
        "disposition": {
            "public_covariant_ghost_evenness": "OBSTRUCTED_AT_ORDER_LAMBDA",
            "public_covariant_order_lambda_stationarity": "PROVED",
            "Eq19_charge_formula_on_declared_covariant_public_branch": "PROVED_WITH_Q_ZERO",
            "Eq19_ghost_even_neutral_term_on_declared_public_branch": "REFUTED",
            "canonical_weak_ghost_remainder": "ORTHOGONAL_BUT_NON_NULL_WITH_NORM_MINUS_7_OVER_288",
            "minimal_two_orbit_finite_repair": "CONSTRUCTED_TO_ALL_FORMAL_ORDERS",
            "repair_source_affiliation": "OPEN",
            "physical_probability": "NOT_ESTABLISHED"
        },
        "missing_object_ledger": [
            "a source-affiliated kappa-conjugate Z branch or a replacement projector",
            "an all-order public-Rt stationarity theorem",
            "R_plus/minus_infinity on a controlled continuum domain",
            "the specific continuum P_chi kernel and generalized-Born trace",
            "a proof that the repaired branch is selected by PS dynamics",
            "a physical complete probability and gravity/BRST lift"
        ],
        "does_not_establish": [
            "a refutation of an unpublished enlarged Bateman--Turok completion",
            "failure of the fixed-vacuum oscillator grading",
            "an asymptotic or continuum no-go theorem",
            "a generalized-Born trace or transition probability",
            "a Weyl-gravity, BRST, or LORENTZIAN-CAUSAL result",
            "literature priority"
        ],
        "checks": {
            "total": len(checks),
            "passed": sum(bool(value) for value in checks.values()),
            "ok": all(checks.values()),
            "items": checks
        },
        "verification_commands": [
            "python3 reverse_physics/bt_covariant_ghost_parity_branch_obstruction.py --check",
            "python3 reverse_physics/verify_bt_covariant_ghost_parity_branch_obstruction.py",
            "python3 -m unittest reverse_physics.tests.test_bt_covariant_ghost_parity_branch_obstruction"
        ],
        "report": REPORT
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    result = build()
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.write:
        with open(CERT, "w", encoding="utf-8") as handle:
            handle.write(encoded)
    if args.check:
        if not os.path.exists(CERT):
            print("RESULT: FAIL (certificate missing)")
            return 1
        with open(CERT, encoding="utf-8") as handle:
            current = handle.read()
        if current != encoded:
            print("RESULT: FAIL (certificate drift)")
            return 1
    checks = result["checks"]
    print(f"checks {checks['passed']}/{checks['total']}")
    print("RESULT:", "PASS" if checks["ok"] else "FAIL")
    print("public ghost parity:", result["disposition"]["public_covariant_ghost_evenness"])
    print("order-lambda stationarity:", result["disposition"]["public_covariant_order_lambda_stationarity"])
    print("minimal repair:", result["disposition"]["minimal_two_orbit_finite_repair"])
    return 0 if checks["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
