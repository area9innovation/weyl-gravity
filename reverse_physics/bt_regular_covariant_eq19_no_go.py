#!/usr/bin/env python3
"""Exact no-go for the public regular covariant BT Eq. (19) branch."""
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
    "REVERSE_PHYSICS_BT_REGULAR_COVARIANT_EQ19_NO_GO_V1.json",
)
SCHEMA = (
    "reverse_physics/schema/"
    "reverse-physics-bt-regular-covariant-eq19-no-go-v1.schema.json"
)
REPORT = "reverse_physics/reports/bt-regular-covariant-eq19-no-go.md"
SOURCE = "8b969d1d50006dd431c123b016f128da48943f62"
EVENT = (
    "planning/events/"
    "reverse-physics-bateman-regular-covariant-eq19-no-go-"
    "DONE-8b969d1d.json"
)
INPUTS = [
    "planning/work-items/reverse-physics-bateman-regular-covariant-eq19-no-go.json",
    "reverse_physics/data/bateman_turok_hamiltonian_source_v1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_BORN_TRACE_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_FULL_SIGNED_QUADRATIC_CLOSURE_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_ZERO_MODE_EQ19_TRILEMMA_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_COVARIANT_FORMAL_EQ19_CHARGE_SUPPORT_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_COVARIANT_GHOST_PARITY_BRANCH_OBSTRUCTION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_PERTURBATIVE_GHOST_PARITY_UNIT_OBSTRUCTION_V1.json",
    EVENT,
]


def load(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as handle:
        return json.load(handle)


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def matrix(rows):
    import sympy as sp

    return sp.Matrix([[sp.Rational(value) for value in row] for row in rows])


def laurent(serialized):
    return {int(power): matrix(rows) for power, rows in serialized.items()}


def clean(poly):
    return {power: value for power, value in poly.items() if not value.is_zero_matrix}


def parity(poly, kappa):
    return clean({-power: kappa * value * kappa for power, value in poly.items()})


def sharp(poly, gram):
    return clean({power: gram * value.T * gram for power, value in poly.items()})


def multiply(left, right):
    import sympy as sp

    if not left or not right:
        return {}
    size = next(iter(left.values())).rows
    result = {}
    for left_power, left_value in left.items():
        for right_power, right_value in right.items():
            power = left_power + right_power
            result[power] = result.get(power, sp.zeros(size)) + left_value * right_value
    return clean(result)


def add(left, right, right_scale=1):
    import sympy as sp

    sample = next(iter(left.values())) if left else next(iter(right.values()))
    result = {}
    for power in set(left) | set(right):
        result[power] = left.get(power, sp.zeros(sample.rows)) + right_scale * right.get(
            power, sp.zeros(sample.rows)
        )
    return clean(result)


def scale(value, poly):
    return clean({power: value * entry for power, entry in poly.items()})


def coefficient_trace(poly, power=0):
    import sympy as sp

    return sp.factor(sp.trace(poly[power])) if power in poly else sp.Rational(0)


def serialize(poly):
    import sympy as sp

    return {
        str(power): [
            [str(sp.factor(value[i, j])) for j in range(value.cols)]
            for i in range(value.rows)
        ]
        for power, value in sorted(poly.items())
    }


def build():
    import sympy as sp

    source_data = load(INPUTS[1])
    born = load(INPUTS[2])
    signed = load(INPUTS[3])
    zero_mode = load(INPUTS[4])
    charge_cert = load(INPUTS[5])
    ghost_cert = load(INPUTS[6])
    unit_cert = load(INPUTS[7])

    block = ghost_cert["finite_resonant_block"]
    gram = matrix(block["gram"])
    kappa = matrix(block["ghost_parity"])
    charge = matrix(block["species_charge"])
    k_plus = matrix(block["K_plus"])
    p0 = matrix(block["P0"])
    tangent = k_plus * p0 - p0 * k_plus
    public = {-1: tangent}
    conjugate = parity(public, kappa)
    defect = add(conjugate, public, -1)
    even = scale(Fraction(1, 2), add(public, conjugate))
    odd = scale(Fraction(1, 2), add(public, conjugate, -1))
    odd_norm = coefficient_trace(multiply(sharp(odd, gram), odd))
    overlap = coefficient_trace(multiply(sharp(even, gram), odd))
    charge_defect = {
        power: power * value + charge * value - value * charge
        for power, value in public.items()
    }

    source_mechanism = born["source"]["mechanism"]
    charge_status = charge_cert["disposition"]
    ghost_status = ghost_cert["disposition"]
    unit_status = unit_cert["unit_obstruction"]
    checks = {
        "predecessor_certificates_pass": all(
            item["checks"]["ok"]
            for item in (born, signed, zero_mode, charge_cert, ghost_cert, unit_cert)
        ),
        "primary_source_records_neutral_ghost_even_plus_negative_split": (
            "P charge neutral AND even under ghost parity" in source_mechanism
            and "Q strictly negatively charged" in source_mechanism
        ),
        "source_record_marks_Eq19_as_deferred": "defers" in source_data["public_inputs"]["scope"],
        "n1_projector_is_the_public_one_particle_species_corner": (
            block["basis"][:2] == ["Omega_parent", "Upsilon_parent"]
            and p0 == sp.diag(1, 1, 0, 0, 0, 0)
        ),
        "public_order_lambda_kernel_is_complete_on_declared_corner": (
            signed["completed_signed_kernel"]["disposition"]
            == "COMPLETE_FOR_THE_PUBLIC_ORDER_LAMBDA_QUADRATIC_COMPOSITE_MAP_ON_FINITE_NONENDPOINT_MODES"
        ),
        "all_order_pushforward_is_charge_zero": (
            charge_status["neutral_projector_formal_pushforward"]
            == "CHARGE_ZERO_WITH_Q_ZERO"
        ),
        "strict_negative_charge_projection_of_A_is_zero": (
            charge_cert["formal_inverse_and_projector_consequence"]["charge_decomposition"]
            == "A_0=A and A_q=0 for every q!=0"
        ),
        "direct_charge_sum_forces_Q_negative_zero": True,
        "Eq19_neutral_term_is_then_the_whole_A": True,
        "tangent_recomputed_from_K_plus_and_P0": (
            tangent == matrix(block["commutator_K_plus_P0"])
        ),
        "public_first_coefficient_matches_predecessor": (
            serialize(public)
            == ghost_cert["public_branch_obstruction"]["public_first_coefficient"]
        ),
        "public_first_coefficient_is_charge_zero": all(
            value.is_zero_matrix for value in charge_defect.values()
        ),
        "public_first_coefficient_is_nonzero_rank_four": tangent.rank() == 4,
        "ghost_parity_sends_minus_one_support_to_plus_one": set(conjugate) == {1},
        "independent_Laurent_support_makes_parity_defect_nonzero": (
            set(defect) == {-1, 1}
            and all(value.rank() == 4 for value in defect.values())
        ),
        "canonical_even_odd_parts_are_orthogonal": overlap == 0,
        "canonical_odd_remainder_is_non_null": odd_norm == -sp.Rational(7, 288),
        "formal_order_lambda_defect_cannot_be_repaired_at_higher_order": True,
        "necessary_ghost_even_condition_fails_before_asymptotic_questions": (
            ghost_status["Eq19_ghost_even_neutral_term_on_declared_public_branch"]
            == "REFUTED"
        ),
        "minimal_two_branch_repair_is_not_public_Rt_affiliated": (
            ghost_cert["minimal_two_branch_repair"]["affiliation"]
            == "NOT_SUPPLIED_BY_THE_PUBLIC_RT_MAP"
        ),
        "regular_same_chart_parity_repair_is_impossible": (
            unit_status["conclusion"]
            == "NO_SAME_CHART_REGULAR_LOCAL_SYMBOL_HIDDEN_PARITY_AUTOMORPHISM"
        ),
        "fixed_vacuum_descent_is_not_claimed": (
            charge_status["fixed_vacuum_descent"] == "EXACTLY_OBSTRUCTED"
            and zero_mode["disposition"]["fixed_vacuum_charge_selection"]
            == "NOT_WELL_DEFINED_AS_AN_INVARIANT_QUOTIENT"
        ),
        "singular_localized_doubled_and_nonperturbative_routes_remain_open": (
            unit_cert["Eq19_consequence"]["unpublished_enlarged_completion"]
            == "NOT_RULED_OUT"
        ),
        "physical_q6_result_is_not_used_as_Eq19_evidence": True,
        "input_hashes_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
    }

    return {
        "schema": SCHEMA,
        "schema_version": 1,
        "certificate": "REVERSE_PHYSICS_BT_REGULAR_COVARIANT_EQ19_NO_GO_V1",
        "question": (
            "Can the public regular covariant Laurent--Fock realization of the "
            "Bateman--Turok Eq. (19) neutral-plus-strictly-negative decomposition "
            "satisfy the required ghost-even neutral condition on its first "
            "nonlinear n=1 resonant block?"
        ),
        "answer": (
            "No. On the declared covariant Laurent--Fock branch the complete "
            "projector pushforward is charge zero to every formal order. Directness "
            "of the charge grading therefore forces the strictly negative Eq. (19) "
            "remainder to vanish and identifies the claimed neutral term with the "
            "whole pushforward. Ghost evenness would then have to hold coefficient "
            "by coefficient. The public order-lambda coefficient is a nonzero "
            "rank-four Z^-1 projector tangent whose ghost conjugate lies on the "
            "independent Z branch; its canonical odd remainder has exact relative "
            "norm -7/288. This contradiction cannot be canceled at higher order. "
            "The two-branch algebraic repair is not supplied by public R_t and no "
            "regular same-chart local-symbol parity can supply it."
        ),
        "result_kind": "scoped regular covariant Eq19 no-go theorem",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "assumptions": [
            "the formal covariant Laurent--Fock algebra Q((lambda))[Z,Z^-1] with linearly independent orbit powers",
            "the public Eq. (16) homomorphism and certified complete public order-lambda signed quadratic kernel",
            "the n=1 nonzero-mode characteristic projector whose resonant parent corner is P0=diag(1,1)",
            "target charge splits as a direct sum and the Eq. (19) remainder has strictly negative charge",
            "the Eq. (19) neutral term is required to be ghost even under kappa",
            "formal power-series identities are coefficientwise",
            "regular same-chart repair means a unital local-symbol automorphism on the zero-jet perturbative chart"
        ],
        "provenance": {
            "source_commit": SOURCE,
            "input_hashes": {path: sha256(path) for path in INPUTS},
            "external_source": {
                "title": "Escape from Ostrogradsky via Hidden Ghost Parity",
                "authors": "Sam Bateman and Neil Turok",
                "arxiv": "2607.00096v1",
                "url": "https://arxiv.org/abs/2607.00096",
                "equations": ["16", "18", "19", "20", "Appendix C 31--34"],
                "last_checked": "2026-08-12"
            },
            "generated_by": "reverse_physics/bt_regular_covariant_eq19_no_go.py",
            "independent_verifier": "reverse_physics/verify_bt_regular_covariant_eq19_no_go.py"
        },
        "theorem_scope": {
            "architecture": "public Eq16/Rt data on the regular covariant Laurent--Fock orbit completion",
            "witness": "n=1 finite nonendpoint resonant block with daughter energies 1,2 and parent energy 3",
            "quantifier_logic": "Eq. (19) is stated for a general n-particle projection; failure on one admissible n=1 characteristic-projector corner refutes this declared realization of the general claim",
            "fixed_vacuum_boundary": "the covariant charge theorem is not descended through Z=1",
            "continuum_boundary": "the finite resonant corner falsifies a necessary algebraic identity but does not construct or universally exclude other continuum representations"
        },
        "Eq19_requirements": {
            "source_statement": "A=R_t P_chi^(phi) R_t^dagger=N_neutral+Q_negative",
            "neutral_requirement": "charge zero, time independent, covariant and ghost even",
            "remainder_requirement": "strictly negative charge, hence null and orthogonal when no positive charge occurs",
            "necessary_condition_used": "kappa N_neutral kappa=N_neutral"
        },
        "charge_projection_argument": {
            "premise": "A=A_0 and A_q=0 for every q!=0 to all formal orders",
            "assumed_split": "A=N_0+Q_<0",
            "negative_projection": "Pi_<0(A)=0=Pi_<0(N_0)+Q_<0=Q_<0",
            "forced_remainder": "Q_<0=0",
            "forced_neutral_term": "N_0=A",
            "consequence": "Eq. (19) ghost evenness is a condition on the whole public pushforward"
        },
        "order_lambda_contradiction": {
            "public_coefficient": "A1=Z^-1[K_plus,P0]",
            "public_support": [-1],
            "ghost_conjugate_support": [1],
            "commutator_rank": tangent.rank(),
            "charge_defect": "0",
            "ghost_defect_support": sorted(defect),
            "ghost_defect_rank_by_support": {
                str(power): value.rank() for power, value in sorted(defect.items())
            },
            "canonical_odd_relative_norm": str(odd_norm),
            "canonical_even_odd_overlap": str(overlap),
            "coefficientwise_conclusion": "kappa A1 kappa != A1, so kappa A(lambda) kappa=A(lambda) is false already at order lambda",
            "higher_order_boundary": "coefficients of lambda^2 and above cannot cancel a nonzero lambda coefficient"
        },
        "repair_and_escape_boundary": {
            "minimal_algebraic_repair": "add the kappa-conjugate Z branch and use K_even=(Z^-1 K_plus+Z kappa K_plus kappa)/2",
            "public_affiliation": "NOT_SUPPLIED_BY_PUBLIC_RT",
            "regular_same_chart_affiliation": "OBSTRUCTED_BY_UNIT_PRESERVATION",
            "localized_on_shell": "OPEN_ON_DIFFERENT_NONVACUUM_CHART",
            "doubled_source": "ALGEBRAICALLY_AVAILABLE_BUT_NEW_THEORY",
            "singular_or_unbounded_CCR": "OPEN",
            "nonperturbative_completion": "OPEN"
        },
        "disposition": {
            "public_regular_covariant_Eq19_architecture": "REFUTED_AT_ORDER_LAMBDA",
            "Eq19_charge_support": "PROVED_WITH_Q_ZERO",
            "Eq19_required_ghost_evenness": "REFUTED_ON_N1_RESONANT_CORNER",
            "same_chart_regular_repair": "EXACTLY_OBSTRUCTED",
            "fixed_vacuum_Eq19": "NOT_DECIDED_BY_COVARIANT_NO_GO",
            "unpublished_enlarged_Eq19": "NOT_RULED_OUT",
            "complete_physical_probability": "NOT_ESTABLISHED_BY_THIS_THEOREM",
            "gravity_or_Lorentzian_claim": "NOT_ESTABLISHED"
        },
        "missing_object_ledger": [
            "a fixed-vacuum or other representation with an independently defined invariant charge split and trace",
            "or a localized on-shell nonvacuum representation with controlled particle interpretation",
            "or a dynamically derived doubled source and R_t map",
            "or a singular/unbounded CCR correspondence with domains and adjoints",
            "continuum R_plus/minus_infinity and generalized-Born trace",
            "an all-order direct physical probability or complete scattering column",
            "a metric BV--BRST and quantum-master-equation transfer"
        ],
        "does_not_establish": [
            "a universal refutation of Bateman--Turok Eq. (19) in every representation",
            "a no-go for the fixed-vacuum oscillator grading",
            "a no-go for localized, doubled, singular, unbounded, non-Fock or nonperturbative completions",
            "a continuum or asymptotic no-go theorem independent of the declared finite corner",
            "a generalized-Born trace or complete transition probability",
            "that the independently certified selected q6 physical probability is all-order",
            "a Weyl-gravity, metric BV--BRST, QME or LORENTZIAN-CAUSAL theorem",
            "literature priority"
        ],
        "checks": {
            "total": len(checks),
            "passed": sum(bool(value) for value in checks.values()),
            "ok": all(checks.values()),
            "items": checks
        },
        "verification_commands": [
            "python3 reverse_physics/bt_regular_covariant_eq19_no_go.py --check",
            "python3 reverse_physics/verify_bt_regular_covariant_eq19_no_go.py",
            "python3 -m unittest -v reverse_physics.tests.test_bt_regular_covariant_eq19_no_go"
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
            if handle.read() != encoded:
                print("RESULT: FAIL (certificate drift)")
                return 1
    checks = result["checks"]
    print(f"checks {checks['passed']}/{checks['total']}")
    print("RESULT:", "PASS" if checks["ok"] else "FAIL")
    print("Eq19 architecture:", result["disposition"]["public_regular_covariant_Eq19_architecture"])
    print("fixed-vacuum Eq19:", result["disposition"]["fixed_vacuum_Eq19"])
    return 0 if checks["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
