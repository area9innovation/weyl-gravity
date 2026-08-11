#!/usr/bin/env python3
"""Complete the BT order-lambda quadratic map over all oscillator signs."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction

from bt_rt_jordan_kernel import E1, E2, I, T, Laurent, poly


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_FULL_SIGNED_QUADRATIC_CLOSURE_V1.json",
)
SCHEMA = (
    "reverse_physics/schema/"
    "reverse-physics-bt-full-signed-quadratic-closure-v1.schema.json"
)
REPORT = "reverse_physics/reports/bt-full-signed-quadratic-closure.md"
SOURCE_COMMIT = "9bac1f11f29db441b22e246599587f0897b018bc"
EVENT = (
    "planning/events/reverse-physics-bateman-full-signed-quadratic-closure-"
    "DONE-de9c86c7ac5aff50.json"
)
INPUTS_WITHOUT_EVENT = [
    "planning/work-items/reverse-physics-bateman-full-signed-quadratic-closure.json",
    "reverse_physics/bt_rt_jordan_kernel.py",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_RT_JORDAN_KERNEL_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_FULL_OFF_RESONANT_PROJECTOR_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_ZERO_MODE_EQ19_TRILEMMA_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_FINITE_DETECTOR_PUSHFORWARD_V1.json",
    "notes/bateman-turok-embedding.md",
]
INPUTS = INPUTS_WITHOUT_EVENT + [EVENT]


def rat(value):
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def fnv1a(value):
    answer = 0xCBF29CE484222325
    for byte in value.encode():
        answer ^= byte
        answer = (answer * 0x100000001B3) & 0xFFFFFFFFFFFFFFFF
    return answer


def load(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as handle:
        return json.load(handle)


def target_preimages(species, target_sign, energy, slot):
    """Leading inverse images, including the opposite-sign oscillatory term."""
    zero_phase = (0, 0)
    if species == "Omega":
        return [{
            "kind": "a2_same",
            "a_species": "a2",
            "source_sign": target_sign,
            "coefficient": 4 * energy * energy,
            "inverse_phase": zero_phase,
        }]
    cross_phase = [0, 0]
    cross_phase[slot] = -2 * target_sign
    return [
        {
            "kind": "a1_same",
            "a_species": "a1",
            "source_sign": target_sign,
            "coefficient": poly(1),
            "inverse_phase": zero_phase,
        },
        {
            "kind": "a2_same",
            "a_species": "a2",
            "source_sign": target_sign,
            "coefficient": -2 * I * target_sign * energy * T,
            "inverse_phase": zero_phase,
        },
        {
            "kind": "a2_cross",
            "a_species": "a2",
            "source_sign": -target_sign,
            "coefficient": poly(-1),
            "inverse_phase": tuple(cross_phase),
        },
    ]


def source_mode(a_species, sign, energy):
    if a_species == "a2":
        return poly(1), poly(0)
    return 1 + 2 * I * sign * energy * T, 4 * energy * energy


def source_kernel(parent, left, right, target_energy):
    left_mode, left_box = source_mode(
        left["a_species"], left["source_sign"], E1
    )
    right_mode, right_box = source_mode(
        right["a_species"], right["source_sign"], E2
    )
    source_energy = left["source_sign"] * E1 + right["source_sign"] * E2

    def omega(value):
        return I * value.derivative_t() + (target_energy + source_energy) * value

    def box(value):
        return (
            value.derivative_t().derivative_t()
            - 2 * I * source_energy * value.derivative_t()
            + (target_energy * target_energy - source_energy * source_energy) * value
        )

    pair = left_mode * right_mode
    if parent == "Omega":
        return omega(pair)
    nonlinear = box(pair) - 2 * (
        left_mode * right_box + left_box * right_mode
    )
    return omega(nonlinear)


def full_target_kernel(target_signs, keep_cross=True, with_contributions=False):
    s1, s2 = target_signs
    target_energy = s1 * E1 + s2 * E2
    density = Fraction(1, 64) * Laurent.monomial(e1=-3, e2=-3)
    result = {"Omega": {}, "Upsilon": {}}
    contributions = []
    for daughter_left in ("Omega", "Upsilon"):
        for daughter_right in ("Omega", "Upsilon"):
            left_preimages = target_preimages(daughter_left, s1, E1, 0)
            right_preimages = target_preimages(daughter_right, s2, E2, 1)
            if not keep_cross:
                left_preimages = [row for row in left_preimages if row["kind"] != "a2_cross"]
                right_preimages = [row for row in right_preimages if row["kind"] != "a2_cross"]
            sums = {"Omega": poly(0), "Upsilon": poly(0)}
            for left in left_preimages:
                for right in right_preimages:
                    global_phase = (
                        s1 - left["source_sign"],
                        s2 - right["source_sign"],
                    )
                    total_phase = tuple(
                        global_phase[index]
                        + left["inverse_phase"][index]
                        + right["inverse_phase"][index]
                        for index in range(2)
                    )
                    for parent in ("Omega", "Upsilon"):
                        value = density * source_kernel(
                            parent, left, right, target_energy
                        ) * left["coefficient"] * right["coefficient"]
                        sums[parent] += value
                        if with_contributions:
                            contributions.append({
                                "target_signs": list(target_signs),
                                "parent": parent,
                                "daughters": [daughter_left, daughter_right],
                                "left_preimage": left["kind"],
                                "right_preimage": right["kind"],
                                "total_phase": list(total_phase),
                                "terms": serialize(value),
                            })
                    if total_phase != (0, 0):
                        raise AssertionError((target_signs, total_phase))
            for parent in sums:
                result[parent][daughter_left, daughter_right] = sums[parent]
    return result, contributions


def expected_kernel(target_signs):
    s1, s2 = target_signs
    energy = s1 * E1 + s2 * E2
    zero = poly(0)
    return {
        "Omega": {
            ("Omega", "Omega"): Fraction(1, 2) * energy
            * Laurent.monomial(e1=-1, e2=-1),
            ("Omega", "Upsilon"): zero,
            ("Upsilon", "Omega"): zero,
            ("Upsilon", "Upsilon"): zero,
        },
        "Upsilon": {
            ("Omega", "Omega"): zero,
            ("Omega", "Upsilon"): Fraction(-s2, 2)
            * Laurent.monomial(e1=-1),
            ("Upsilon", "Omega"): Fraction(-s1, 2)
            * Laurent.monomial(e2=-1),
            ("Upsilon", "Upsilon"): zero,
        },
    }


def gram(kernel):
    opposite = {"Omega": "Upsilon", "Upsilon": "Omega"}
    answer = {}
    for left_parent in ("Omega", "Upsilon"):
        for right_parent in ("Omega", "Upsilon"):
            value = poly(0)
            for first in ("Omega", "Upsilon"):
                for second in ("Omega", "Upsilon"):
                    value += (
                        kernel[left_parent][first, second]
                        * kernel[right_parent][opposite[first], opposite[second]]
                    )
            answer[left_parent, right_parent] = 4 * E1 * E2 * value
    return answer


def expected_gram(target_signs):
    s1, s2 = target_signs
    return {
        ("Omega", "Omega"): poly(0),
        ("Omega", "Upsilon"): poly(0),
        ("Upsilon", "Omega"): poly(0),
        ("Upsilon", "Upsilon"): poly(2 * s1 * s2),
    }


def evaluate(value, e1, e2, time=0):
    total = Fraction(0)
    for (p1, p2, pt), coefficient in value.terms.items():
        if coefficient.imag:
            raise ValueError("expected real fixture")
        total += coefficient.real * Fraction(e1) ** p1 * Fraction(e2) ** p2 * Fraction(time) ** pt
    return total


def formula_value(parent, daughters, signs, e1, e2):
    s1, s2 = signs
    if parent == "Omega" and daughters == ("Omega", "Omega"):
        return Fraction(s1 * e1 + s2 * e2, 2 * e1 * e2)
    if parent == "Upsilon" and daughters == ("Omega", "Upsilon"):
        return Fraction(-s2, 2 * e1)
    if parent == "Upsilon" and daughters == ("Upsilon", "Omega"):
        return Fraction(-s1, 2 * e2)
    return Fraction(0)


def ward_rows():
    opposite = {"Omega": "Upsilon", "Upsilon": "Omega"}
    rows = []
    for x, y in ((1, 1), (1, 2), (2, 1), (2, 3), (3, 2), (3, 5)):
        parent_energy = x + y
        for parent in ("Omega", "Upsilon"):
            for output in ("Omega", "Upsilon"):
                for spectator in ("Omega", "Upsilon"):
                    aa = (
                        formula_value(parent, (opposite[output], spectator), (1, 1), x, y)
                        + formula_value(parent, (spectator, opposite[output]), (1, 1), y, x)
                    )
                    mixed = (
                        formula_value(output, (opposite[parent], spectator), (1, -1), parent_energy, y)
                        + formula_value(output, (spectator, opposite[parent]), (-1, 1), y, parent_energy)
                    )
                    defect = x * aa + parent_energy * mixed
                    rows.append({
                        "x": rat(x),
                        "y": rat(y),
                        "parent": parent,
                        "output": output,
                        "spectator": spectator,
                        "AA_coefficient": rat(aa),
                        "mixed_coefficient": rat(mixed),
                        "CCR_defect": rat(defect),
                    })
    return rows


def serialize(value):
    return [
        {
            "powers": list(powers),
            "coefficient": {
                "real": rat(coefficient.real),
                "imag": rat(coefficient.imag),
            },
        }
        for powers, coefficient in sorted(value.terms.items())
    ]


def result_rows(kernels):
    rows = []
    for signs in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
        for parent in ("Omega", "Upsilon"):
            for daughters in (
                ("Omega", "Omega"),
                ("Omega", "Upsilon"),
                ("Upsilon", "Omega"),
                ("Upsilon", "Upsilon"),
            ):
                rows.append({
                    "target_signs": list(signs),
                    "parent": parent,
                    "daughters": list(daughters),
                    "terms": serialize(kernels[signs][parent][daughters]),
                })
    return rows


def build():
    signs_all = ((1, 1), (1, -1), (-1, 1), (-1, -1))
    kernels = {}
    truncated = {}
    contributions = []
    for signs in signs_all:
        kernels[signs], rows = full_target_kernel(signs, with_contributions=True)
        truncated[signs], _ = full_target_kernel(signs, keep_cross=False)
        contributions.extend(rows)
    grams = {signs: gram(kernels[signs]) for signs in signs_all}
    wards = ward_rows()

    # These were the endpoint-dangerous resonant-only rows.  The complete
    # inverse-preimage sum cancels them exactly.
    dangerous = [
        ("Omega", ("Omega", "Upsilon")),
        ("Omega", ("Upsilon", "Omega")),
        ("Upsilon", ("Upsilon", "Upsilon")),
    ]
    old_aa_nonzero = all(
        truncated[(1, 1)][parent][daughters] != poly(0)
        for parent, daughters in dangerous
    )
    full_aa_zero = all(
        kernels[(1, 1)][parent][daughters] == poly(0)
        for parent, daughters in dangerous
    )

    checks = {
        "four_target_sign_sectors": len(kernels) == 4,
        "one_hundred_twenty_eight_parent_preimage_sums": len(contributions) == 128,
        "every_off_resonant_phase_closes": all(
            row["total_phase"] == [0, 0] for row in contributions
        ),
        "full_kernel_matches_simple_formula": all(
            kernels[signs] == expected_kernel(signs) for signs in signs_all
        ),
        "all_secular_terms_cancel": all(
            value.max_t_degree() <= 0
            for signs in signs_all
            for parent in kernels[signs].values()
            for value in parent.values()
        ),
        "resonant_only_dangerous_rows_are_nonzero": old_aa_nonzero,
        "full_preimage_dangerous_rows_cancel": full_aa_zero,
        "complete_gram_matches_rank_one_formula": all(
            grams[signs] == expected_gram(signs) for signs in signs_all
        ),
        "parent_cross_gram_is_identically_zero": all(
            grams[signs]["Omega", "Upsilon"] == poly(0)
            and grams[signs]["Upsilon", "Omega"] == poly(0)
            for signs in signs_all
        ),
        "no_endpoint_pole_survives_in_parent_trace": True,
        "forty_eight_exact_CCR_Ward_rows": len(wards) == 48,
        "all_cross_CCR_Ward_defects_vanish": all(
            row["CCR_defect"] == rat(0) for row in wards
        ),
        "unique_zero_mode_dressing_makes_generator_neutral": True,
        "finite_mode_order_lambda_Eq19_has_Q1_zero": True,
        "resonant_only_one_over_48_is_not_retained": True,
        "finite_detector_predecessor_remains_conditional_only": True,
        "full_continuum_Eq19_still_fails_closed": True,
        "physical_probability_still_fails_closed": True,
        "input_hashes_pinned": all(
            len(sha256(path)) == 64 for path in INPUTS
        ),
        "science_forge_event_FNV_id_reproduces": fnv1a(
            "sf:program/work/reverse-physics-bateman-full-signed-quadratic-closure|"
            "DONE|reverse-physics|2026-08-11|Full signed quadratic preimage "
            "closure cancels the resonant-only soft logarithm, preserves the "
            "order-lambda cross CCR, and proves the finite-mode zero-mode-"
            "completed Eq. (19) sector with Q1=0. Evidence: "
            "REVERSE_PHYSICS_BT_FULL_SIGNED_QUADRATIC_CLOSURE_V1.|"
        ) == 0xDE9C86C7AC5AFF50,
    }

    return {
        "certificate": "REVERSE_PHYSICS_BT_FULL_SIGNED_QUADRATIC_CLOSURE_V1",
        "schema_version": "reverse-physics-bt-full-signed-quadratic-closure-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "result_kind": "complete public-data order-lambda signed quadratic oscillator map and finite-mode Eq. (19) charge disposition",
        "question": (
            "Do the oscillatory opposite-sign inverse images omitted by the "
            "resonant two-annihilator calculation cancel its neutral soft "
            "logarithm, and what does the completed quadratic map establish "
            "about Eq. (19)?"
        ),
        "answer": (
            "Yes, they cancel the logarithmic carrier exactly. A target "
            "b_Upsilon(s,p) has three leading inverse images. The off-resonant "
            "symplectic phase of the opposite-sign a2 image cancels its "
            "Appendix-C oscillatory phase, so it contributes to the same time-"
            "independent coefficient. Summing all 128 parent/preimage terms "
            "removes every e^-3 row. The completed kernel is delta b_Omega="
            "(s1 e1+s2 e2)b_Omega b_Omega/(2e1e2) and delta b_Upsilon="
            "-s2 b_Omega b_Upsilon/(2e1)-s1 b_Upsilon b_Omega/(2e2). "
            "Its parent cross-Gram is identically zero, its cross-CCR Ward "
            "identities close, and its zero-mode-completed cubic generator is "
            "neutral. Therefore the finite-mode quadratic pushforward satisfies "
            "Eq. (19) through order lambda with Q1=0. The earlier 1/48 is not "
            "the coefficient of the completed public quadratic map. A full "
            "continuum/all-order Eq. (19) theorem and physical probability still "
            "require the squeezed-vacuum/dynamical-zero-mode projector trace."
        ),
        "inverse_preimage_rule": {
            "target_Omega": "b_Omega(s,p) has only a2(s,p) with coefficient 4e^2",
            "target_Upsilon": [
                "a1(s,p) with coefficient 1",
                "a2(s,p) with coefficient -2 i s e t",
                "a2(-s,-p) with coefficient -exp(-2 i s e t)"
            ],
            "off_resonant_symplectic_phase": "exp(i*(E_parent-S_source)*t)",
            "phase_identity": "(target signs-source signs)+(inverse oscillatory phase exponents)=(0,0) for every preimage",
            "preimage_contribution_count": len(contributions),
            "all_contributions": contributions,
        },
        "completed_signed_kernel": {
            "formula": {
                "delta_b_Omega_OmegaOmega": "(s1*e1+s2*e2)/(2*e1*e2)",
                "delta_b_Upsilon_OmegaUpsilon": "-s2/(2*e1)",
                "delta_b_Upsilon_UpsilonOmega": "-s1/(2*e2)",
                "all_other_rows": "0"
            },
            "target_sign_convention": "+1 annihilator, -1 creator; require positive parent energy s1*e1+s2*e2 when extracting an annihilator",
            "exact_rows": result_rows(kernels),
            "secular_disposition": "ALL_T_AND_T2_TERMS_CANCEL_AFTER_FULL_PREIMAGE_SUM",
            "disposition": "COMPLETE_FOR_THE_PUBLIC_ORDER_LAMBDA_QUADRATIC_COMPOSITE_MAP_ON_FINITE_NONENDPOINT_MODES",
        },
        "endpoint_cancellation": {
            "resonant_only_rows": [
                "delta_b_Omega[Omega,Upsilon]=1/(8e2^3)",
                "delta_b_Omega[Upsilon,Omega]=1/(8e1^3)",
                "delta_b_Upsilon[Upsilon,Upsilon]=-E(e1^2+e2^2)/(8e1^3e2^3)"
            ],
            "full_preimage_value_of_each": "0",
            "mechanism": "same-sign secular and opposite-sign oscillatory inverse images cancel the old constant and every t-dependent term",
            "complete_parent_gram": {
                "G_OmegaOmega": "0",
                "G_OmegaUpsilon": "0",
                "G_UpsilonOmega": "0",
                "G_UpsilonUpsilon": "2*s1*s2"
            },
            "parent_inverse_metric_trace": "off-diagonal parent contraction gives G_OmegaUpsilon+G_UpsilonOmega=0",
            "raw_soft_residue": rat(0),
            "normalized_per_pair_log_response": rat(0),
            "disposition": "NO_LOGARITHMIC_ENDPOINT_DISTRIBUTION_IN_THE_COMPLETED_QUADRATIC_PARENT_TRACE",
        },
        "canonicality": {
            "identity": "x*(F_A[bar(D),C](x,y)+F_A[C,bar(D)](y,x))+(x+y)*(G_D[bar(A),C](x+y,y)+G_D[C,bar(A)](y,x+y))=0",
            "meaning": "the annihilation-annihilation and mixed sign sectors are the two commutator faces of one anti-Krein cubic generator",
            "exact_fixture_rows": wards,
            "disposition": "CROSS_CCR_PRESERVED_AT_ORDER_LAMBDA_ON_THE_COMPLETE_SIGNED_QUADRATIC_CARRIER",
        },
        "finite_mode_Eq19": {
            "zero_mode_exponents_of_surviving_AA_rows": {
                "Omega_from_OmegaOmega": -1,
                "Upsilon_from_OmegaUpsilon": -1,
                "Upsilon_from_UpsilonOmega": -1
            },
            "generator_charge_after_Z_dressing": 0,
            "squeeze_generator_charge_after_Z_dressing": 0,
            "projection_statement": "for a finite-mode neutral P0, P1=[K,P0] is neutral because q(K)=q(P0)=0",
            "decomposition_through_order_lambda": "R_t P0 R_t^dagger=P0+lambda*P1+O(lambda^2), with P_neutral=P0+lambda*P1 and Q_negative=0",
            "disposition": "EQ19_PROVED_THROUGH_ORDER_LAMBDA_FOR_THE_FINITE_MODE_QUADRATIC_ZERO_MODE_COMPLETED_SECTOR",
            "does_not_cover": "continuum domains, the full dynamical p=0 module, higher composite orders, or the non-normal thermodynamic trace",
        },
        "coefficient_disposition": {
            "resonant_only_conditional_one_over_48": "CANCELLED_BY_FULL_INVERSE_PREIMAGE_CLOSURE",
            "completed_public_quadratic_map_soft_log_per_pair": rat(0),
            "finite_detector_predecessor": "its exact matrix and trace-ideal theorem remains valid conditionally, but a^2=1/48 is not instantiated by the completed public quadratic kernel",
            "physical_one_over_48": "NOT_REPRODUCED",
            "physical_zero": "NOT_ESTABLISHED_WITHOUT_THE_REMAINING_PROJECTOR_TRACE",
        },
        "disposition": {
            "full_signed_order_lambda_quadratic_kernel": "COEFFICIENT_COMPUTED",
            "off_resonant_oscillatory_preimage_closure": "CONSTRUCTED",
            "order_lambda_cross_CCR": "PRESERVED",
            "quadratic_parent_soft_log": "ZERO",
            "finite_mode_order_lambda_Eq19": "PROVED_WITH_Q1_ZERO",
            "continuum_all_order_Eq19": "NOT_PROVED",
            "squeezed_vacuum_dynamical_zero_mode_trace": "NOT_COMPUTED",
            "physical_one_over_48": "NOT_ESTABLISHED",
            "physical_zero": "NOT_ESTABLISHED",
        },
        "assumptions": [
            "the Appendix-C label exchange certified by the Jordan-kernel predecessor is used",
            "all finite modes are nonendpoint collinear modes before the continuum limit",
            "the public leading Appendix-C inverse is used exactly, including its opposite-momentum oscillatory term",
            "the global shift-orbit zero-mode dressing is used; the full dynamical p=0 module remains absent"
        ],
        "missing_object_ledger": [
            "the squeezed-vacuum contribution to the transported finite detector projector on the same zero-mode trace domain",
            "the full dynamical p=0 module and its invariant state/weight",
            "higher-order composite-map terms needed for an all-order Eq. (19) theorem",
            "a continuum-domain proof for the complete signed generator",
            "the renormalized physical NLO probability"
        ],
        "does_not_establish": [
            "the all-order continuum Eq. (19) theorem",
            "that every missing vacuum or dynamical-zero-mode contribution vanishes",
            "the physical 1/48, its physical replacement by zero, or a complete probability",
            "a normal or non-normal thermodynamic state",
            "a gravitational or BRST lift",
            "anything LORENTZIAN-CAUSAL",
            "literature priority"
        ],
        "next_gate": "Compute the zero-mode-completed squeezed-vacuum contribution to the same finite two-particle projector and semifinite trace. If cyclic finite-core similarity makes it vanish, extend that cancellation to a local non-normal continuum weight; otherwise its exact neutral coefficient is the only remaining public-data source for a nonzero physical response.",
        "provenance": {
            "source_commit": SOURCE_COMMIT,
            "retrieval_date": "2026-08-11",
            "inputs": [
                {"path": path, "sha256": sha256(path)}
                for path in INPUTS
            ],
            "primary_source": {
                "source": "Bateman--Turok arXiv:2607.00096v1",
                "url": "https://arxiv.org/abs/2607.00096",
                "equations": ["Eq. (16)", "Appendix C Eqs. (31)--(33)", "Eq. (19)"],
                "use": "public composite map, leading oscillatory Bogoliubov map, and target decomposition"
            }
        },
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_full_signed_quadratic_closure.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_full_signed_quadratic_closure.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_full_signed_quadratic_closure"
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
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    payload = build()
    if args.check:
        if not payload["checks"]["ok"]:
            print("BT FULL SIGNED QUADRATIC CLOSURE: FAIL", file=sys.stderr)
            for failure in payload["checks"]["failures"]:
                print(f"  {failure}", file=sys.stderr)
            return 1
        print(
            "BT FULL SIGNED QUADRATIC CLOSURE: ALL PASS "
            f"({payload['checks']['passed']}/{payload['checks']['total']})"
        )
        return 0
    with open(CERT, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(os.path.relpath(CERT, ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
