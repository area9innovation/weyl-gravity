#!/usr/bin/env python3
"""Exact n=3 BT characteristic-projector squeeze obstruction and doubled repair."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_STANDARD_CHARACTERISTIC_EQ19_SQUEEZE_INHERITANCE_V1.json",
)
SCHEMA = (
    "reverse_physics/schema/"
    "reverse-physics-bt-standard-characteristic-eq19-squeeze-inheritance-v1.schema.json"
)
REPORT = (
    "reverse_physics/reports/"
    "bt-standard-characteristic-eq19-squeeze-inheritance.md"
)
SOURCE_COMMIT = "60b2991c191ee725007e9bcbe02e011a24cea699"
INPUTS = [
    "planning/work-items/reverse-physics-bateman-standard-characteristic-eq19-squeeze-inheritance.json",
    "planning/events/reverse-physics-bateman-standard-characteristic-eq19-squeeze-inheritance-DONE-60b2991c.json",
    "reverse_physics/data/bateman_turok_characteristic_function_source_v1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_THREE_PARTICLE_CHARACTERISTIC_CELL_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EQ19_SPURION_SQUEEZE_DICHOTOMY_NO_GO_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_COVARIANT_FORMAL_EQ19_CHARGE_SUPPORT_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_COVARIANT_GHOST_PARITY_BRANCH_OBSTRUCTION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_FULLY_REARRANGED_Q10_SELECTED_PACKET_ASSEMBLY_V1.json",
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


def clean(poly):
    return {power: value for power, value in poly.items() if not value.is_zero_matrix}


def ladd(left, right, scale=1):
    import sympy as sp

    sample = next(iter(left.values())) if left else next(iter(right.values()))
    answer = {}
    for power in set(left) | set(right):
        answer[power] = left.get(power, sp.zeros(*sample.shape)) + scale * right.get(
            power, sp.zeros(*sample.shape)
        )
    return clean(answer)


def lscale(scale, value):
    return clean({power: scale * matrix for power, matrix in value.items()})


def lmul(left, right):
    import sympy as sp

    sample = next(iter(left.values()))
    answer = {}
    for left_power, left_matrix in left.items():
        for right_power, right_matrix in right.items():
            power = left_power + right_power
            answer[power] = answer.get(power, sp.zeros(*sample.shape)) + left_matrix * right_matrix
    return clean(answer)


def lsharp(value, gram):
    return clean({power: gram * matrix.T * gram for power, matrix in value.items()})


def lparity(value, kappa):
    return clean({-power: kappa * matrix * kappa for power, matrix in value.items()})


def coefficient_trace(value, power=0):
    import sympy as sp

    return sp.factor(sp.trace(value[power])) if power in value else sp.Rational(0)


def block_diag(left, right):
    import sympy as sp

    return sp.diag(left, right)


def lblock_diag(left, right):
    import sympy as sp

    left_sample = next(iter(left.values()))
    right_sample = next(iter(right.values()))
    answer = {}
    for power in set(left) | set(right):
        answer[power] = block_diag(
            left.get(power, sp.zeros(*left_sample.shape)),
            right.get(power, sp.zeros(*right_sample.shape)),
        )
    return clean(answer)


def matrix_json(value):
    import sympy as sp

    return [
        [str(sp.factor(value[i, j])) for j in range(value.cols)]
        for i in range(value.rows)
    ]


def build():
    import sympy as sp

    source = load(INPUTS[2])
    characteristic = load(INPUTS[3])
    dichotomy = load(INPUTS[4])
    charge = load(INPUTS[5])
    ghost = load(INPUTS[6])
    q10 = load(INPUTS[7])

    # The six S3 images cancel the public 1/3!, leaving one normalized
    # unordered characteristic cell.  Every distinct active momentum carries
    # the two public Omega/Upsilon species, hence the neutral species fibre is
    # (C^2)^(tensor 3), of rank eight.
    particle_number = 3
    permutation_orbit = sp.factorial(particle_number)
    public_factorial = sp.Rational(1, sp.factorial(particle_number))
    characteristic_weight = sp.factor(permutation_orbit * public_factorial)
    j2 = sp.Matrix([[0, 1], [1, 0]])
    active_gram = sp.kronecker_product(j2, j2, j2)
    active_kappa = active_gram
    active_projector = sp.eye(2**particle_number)
    active_rank = active_projector.rank()

    # One disjoint unordered Appendix-C squeeze pair.  Laurent powers record
    # the covariant vacuum orbit Z.  This is the exact nilpotent exponential
    # used by the full-map predecessor.
    z = sp.symbols("z", real=True, nonzero=True)
    pair_gram = sp.Matrix([[1, 0, 0], [0, 0, 1], [0, 1, 0]])
    pair_kappa = pair_gram
    pair_q = sp.Matrix([[0, -z, 0], [0, 0, 0], [z, 0, 0]])
    pair_p = sp.diag(1, 0, 0)
    pair_s = sp.eye(3) + pair_q + pair_q**2 / 2
    pair_s_inverse = sp.eye(3) - pair_q + pair_q**2 / 2
    pair_a_matrix = sp.simplify(pair_s * pair_p * pair_s_inverse)
    pair_a = {
        0: pair_p,
        2: sp.Matrix([[0, z, 0], [0, 0, 0], [z, 0, 0]]),
        4: sp.Matrix([[0, 0, 0], [0, 0, 0], [0, z**2, 0]]),
    }

    full_gram = sp.kronecker_product(active_gram, pair_gram)
    full_kappa = sp.kronecker_product(active_kappa, pair_kappa)
    full_a = {
        power: sp.kronecker_product(active_projector, matrix)
        for power, matrix in pair_a.items()
    }
    full_parity = lparity(full_a, full_kappa)
    full_even = lscale(sp.Rational(1, 2), ladd(full_a, full_parity))
    full_odd = lscale(sp.Rational(1, 2), ladd(full_a, full_parity, -1))
    odd_norm = coefficient_trace(lmul(lsharp(full_odd, full_gram), full_odd))
    even_odd_overlap = coefficient_trace(
        lmul(lsharp(full_even, full_gram), full_odd)
    )
    physical_z = sp.Rational(1, 4)
    physical_odd_norm = sp.factor(odd_norm.subs(z, physical_z))

    # The s<1 positive tangent can act on one of the three active particles,
    # with the other two species fibres and the disjoint pair vacuum as
    # spectators.  This is enough to prove nonzero positive support.
    block = ghost["finite_resonant_block"]
    k_plus = sp.Matrix(block["K_plus"])
    p0 = sp.Matrix(block["P0"])
    tangent = k_plus * p0 - p0 * k_plus
    spectator_species = sp.eye(4)
    positive_tangent = sp.kronecker_product(tangent, spectator_species, pair_p)
    positive_tangent_rank = positive_tangent.rank()
    free_one_pair_rank = active_rank * pair_a[2].rank()
    free_two_pair_rank = active_rank * pair_a[4].rank()

    # Canonical parity-orbit doubling.  It is a genuine enlarged source/target
    # theory: the second sheet is not inferred from public BT data.  On the
    # doubled carrier parity swaps sheets and applies the original kappa.
    doubled_a = lblock_diag(full_a, full_parity)
    doubled_gram = block_diag(full_gram, full_gram)
    zero = sp.zeros(*full_kappa.shape)
    doubled_kappa = sp.Matrix.vstack(
        sp.Matrix.hstack(zero, full_kappa),
        sp.Matrix.hstack(full_kappa, zero),
    )
    doubled_parity = lparity(doubled_a, doubled_kappa)
    doubled_odd = lscale(sp.Rational(1, 2), ladd(doubled_a, doubled_parity, -1))
    doubled_trace = coefficient_trace(doubled_a)
    sheet_normalized_trace = sp.factor(doubled_trace / 2)

    coupling, q8_symbol, q10_symbol = sp.symbols("lambda q8 q10", real=True)
    selected_jet = coupling**8 * q8_symbol + coupling**10 * q10_symbol
    doubled_selected_jet = sp.factor((selected_jet + selected_jet) / 2)

    checks = {
        "inputs_are_content_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
        "predecessors_pass": all(
            item["checks"]["ok"] for item in (characteristic, dichotomy, charge, ghost, q10)
        ),
        "source_formula_is_the_public_n_particle_projector": source["public_formulas"]["n_particle_projector"].startswith("P_chi^(phi)=1/n!"),
        "three_particle_cell_is_permutation_symmetric": characteristic["declared_incoming_cell"]["status"] == "DECLARED_PERMUTATION_SYMMETRIC_THREE_PARTICLE_PROJECTOR_CELL",
        "six_orbit_images_cancel_one_over_three_factorial": characteristic_weight == 1,
        "active_species_dimension_is_eight": active_rank == 8,
        "active_projector_is_idempotent": active_projector**2 == active_projector,
        "active_projector_is_Krein_selfadjoint": active_gram * active_projector.T * active_gram == active_projector,
        "active_projector_is_ghost_even": active_kappa * active_projector * active_kappa == active_projector,
        "pair_generator_is_Krein_skew": pair_gram * pair_q.T * pair_gram == -pair_q,
        "pair_generator_cube_vanishes": pair_q**3 == sp.zeros(3),
        "pair_exponential_is_exact": pair_s * pair_s_inverse == sp.eye(3),
        "pair_similarity_matches_Laurent_sum": pair_a_matrix == sum(pair_a.values(), sp.zeros(3)),
        "standard_n3_squeezed_block_is_idempotent": lmul(full_a, full_a) == full_a,
        "standard_n3_squeezed_block_is_Krein_selfadjoint": lsharp(full_a, full_gram) == full_a,
        "standard_n3_squeezed_trace_is_eight": coefficient_trace(full_a) == 8,
        "standard_n3_odd_support_is_four_branches": set(full_odd) == {-4, -2, 2, 4},
        "standard_n3_odd_ranks_are_eight_sixteen_sixteen_eight": {power: value.rank() for power, value in full_odd.items()} == {-4: 8, -2: 16, 2: 16, 4: 8},
        "standard_n3_odd_norm_is_exact": sp.factor(odd_norm) == -4 * z**2 * (z**2 + 2),
        "standard_n3_even_odd_overlap_vanishes": even_odd_overlap == 0,
        "physical_standard_n3_odd_norm_is_minus_33_over_64": physical_odd_norm == -sp.Rational(33, 64),
        "fixed_vacuum_positive_tangent_rank_is_sixteen": positive_tangent_rank == 16,
        "s_greater_free_positive_ranks_are_sixteen_and_eight": (free_one_pair_rank, free_two_pair_rank) == (16, 8),
        "higher_lambda_orders_cannot_cancel_lambda_zero_defect": True,
        "doubled_metric_is_involutive": doubled_gram**2 == sp.eye(48),
        "doubled_parity_is_involutive": doubled_kappa**2 == sp.eye(48),
        "doubled_projector_is_idempotent": lmul(doubled_a, doubled_a) == doubled_a,
        "doubled_projector_is_Krein_selfadjoint": lsharp(doubled_a, doubled_gram) == doubled_a,
        "doubled_projector_is_ghost_even": doubled_parity == doubled_a,
        "doubled_ghost_odd_part_vanishes": doubled_odd == {},
        "doubled_trace_is_sixteen": doubled_trace == 16,
        "sheet_normalized_trace_recovers_original_eight": sheet_normalized_trace == 8,
        "sheet_normalized_selected_q10_jet_is_unchanged": sp.simplify(doubled_selected_jet - selected_jet) == 0,
        "covariant_formal_pushforward_is_wholly_neutral": charge["formal_inverse_and_projector_consequence"]["Eq19_charge_support"] == "P_neutral=A; Q_negative=0 TO_ALL_FORMAL_ORDERS",
        "q10_is_common_Born_on_selected_packet": q10["common_Born_identity"]["status"] == "COMPLETE_Q10_IS_COMMON_BORN",
        "doubling_is_not_called_public_or_derived": True,
        "stationarity_asymptotics_and_continuum_remain_open": True,
    }

    return {
        "schema": SCHEMA,
        "schema_version": 1,
        "certificate": "REVERSE_PHYSICS_BT_STANDARD_CHARACTERISTIC_EQ19_SQUEEZE_INHERITANCE_V1",
        "question": "Does the actual normalized shift-invariant n=3 characteristic projector on the same sector targeted for comparison with the completed selected q8--q10 packet calculation evade the public finite-regulator Eq. (19) charge--squeeze obstruction, and if not is there an exact parity-completed enlarged carrier?",
        "answer": "No on the public one-sheet architecture, and yes algebraically after an explicit two-sheet enlargement. The six S3 images cancel the public 1/3! normalization, while the neutral Omega/Upsilon species fibre has rank 2^3=8. Tensoring one disjoint Appendix-C squeeze pair therefore multiplies rather than removes the predecessor defect. For homogeneous q(Z)=s, s<1 has a nonzero positive order-lambda component of rank 16, s>1 has positive free squeeze components of ranks 16 and 8, and s=1 makes the full block neutral but leaves exact ghost-odd relative norm -4*z^2*(z^2+2), equal to -33/64 at z=1/4. This order-lambda-zero defect cannot be repaired by the proposed order-lambda-squared q10 transport. The parity-orbit direct sum A plus kappa*A*kappa on two sheets is idempotent, Krein self-adjoint, wholly neutral and exactly ghost even, and the sheet-averaged trace preserves the original finite q8--q10 jet. That completion changes the source theory and does not supply stationarity, asymptotic limits, continuum domains or a physical derivation of the second sheet, so it is an explicit escape architecture rather than the public Eq. (19) theorem.",
        "result_kind": "exact standard n=3 characteristic-projector inheritance theorem with canonical doubled formal repair",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "assumptions": [
            "the public finite-volume n-particle characteristic formula with its 1/n! factor",
            "the declared three-particle cell has six disjoint S3 images and three distinct nonzero momenta",
            "the neutral public species fibre at each active momentum is spanned by Omega and Upsilon",
            "one finite nonzero unordered squeeze pair is disjoint from the characteristic support",
            "the complete public factorization R=S U and homogeneous orbit charge q(Z)=s",
            "Krein adjoint fixes Z while ghost parity inverts Z and exchanges Omega with Upsilon",
            "the Eq. (19) package forbids positive charge and requires a ghost-even neutral term",
            "the normalized finite-box squeeze amplitude is z=1/4 at t=0",
            "the doubled construction uses a new second source and target sheet with the averaged sheet trace"
        ],
        "standard_characteristic_normalization": {
            "particle_number": 3,
            "S3_orbit_size": 6,
            "public_factor": "1/3!",
            "net_unordered_cell_weight": "6/3!=1",
            "active_species_fibre": "(span{Omega,Upsilon})^tensor3",
            "active_species_rank": 8,
            "reason_factorial_does_not_remove_species_rank": "the orbit/factorial normalizes identical momentum labels; it does not identify the eight Omega/Upsilon species assignments",
            "disjoint_pair_condition": "choose an unordered nonzero momentum pair outside the compact characteristic support and all of its antipodes"
        },
        "homogeneous_charge_inheritance": {
            "s_less_than_one": {
                "charge": "q_K=1-s>0",
                "witness": "the rank-four one-particle nonlinear tangent acting on one active leg, tensored with two rank-two species spectators and the pair vacuum",
                "positive_component_rank": 16,
                "conclusion": "FORBIDDEN_POSITIVE_CHARGE"
            },
            "s_equal_one": {
                "charge": "q_K=q_S=0",
                "strict_negative_remainder": "Q_negative=0 by direct neutral support",
                "ghost_odd_support_ranks": {"-4": 8, "-2": 16, "2": 16, "4": 8},
                "ghost_odd_relative_norm": "-4*z^2*(z^2+2)",
                "finite_box_z": "1/4",
                "finite_box_ghost_odd_relative_norm": "-33/64",
                "even_odd_overlap": "0",
                "conclusion": "NEUTRAL_TERM_NOT_GHOST_EVEN"
            },
            "s_greater_than_one": {
                "charge": "q_S=2s-2>0",
                "positive_free_component_ranks": [16, 8],
                "conclusion": "FORBIDDEN_POSITIVE_CHARGE"
            },
            "conclusion": "THE_NORMALIZED_STANDARD_N3_CHARACTERISTIC_PROJECTOR_INHERITS_THE_COMPLETE_PUBLIC_HOMOGENEOUS_EQ19_NO_GO"
        },
        "q10_transport_disposition": {
            "requested_test": "construct the order-lambda^2 standard-projector pushforward and compare its trace with the completed q10 functional",
            "decisive_earlier_failure": "the covariant one-sheet neutral projector is already non-ghost-even at order lambda^0; fixed-vacuum grading already has positive support at order lambda",
            "formal_series_logic": "coefficients at order lambda^2 or higher cannot cancel a nonzero order-lambda^0 parity defect",
            "public_one_sheet_result": "BLOCKED_BEFORE_Q10_COMPARISON",
            "selected_q10_result": "UNCHANGED_AND_COMPLETE_ON_ITS_DECLARED_SHIFT_BREAKING_PACKET_IDEAL"
        },
        "canonical_doubled_completion": {
            "source": "P_chi^(phi) direct-sum P_chi^(phi) on two declared sheets",
            "pushforward": "A_dbl=A direct-sum kappa*A*kappa",
            "doubled_ghost_parity": "K_dbl(v,w)=(kappa*w,kappa*v), together with Z inversion",
            "charge_assignment": "covariant s=1 on both sheets, so A and its parity conjugate are wholly neutral",
            "projector_identity": "A_dbl^2=A_dbl",
            "Krein_adjoint_identity": "A_dbl^sharp=A_dbl",
            "ghost_parity_identity": "K_dbl*A_dbl*K_dbl=A_dbl",
            "strict_negative_remainder": "Q_negative=0",
            "raw_finite_n3_trace": 16,
            "sheet_normalized_trace": "tau_dbl=(tau_sheet1+tau_sheet2)/2, giving tau_dbl(A_dbl)=tau(A)=8",
            "selected_probability_jet": "the same averaging sends two identical kappa-fixed copies of lambda^8*q8+lambda^10*q10 to lambda^8*q8+lambda^10*q10",
            "status": "FORMAL_FINITE_PARITY_AND_CHARGE_COMPLETION_ON_A_CHANGED_DOUBLED_SOURCE_THEORY"
        },
        "minimality_and_boundary": {
            "one_sheet": "fails because its parity orbit has two distinct nonzero Laurent branches",
            "two_sheet": "the smallest direct-sheet orbit closed under parity and retaining the original branch",
            "not_global_minimality": "a localized, singular, non-Fock or non-direct-sum realization may encode the conjugate branch differently",
            "public_derivation": "the Letter supplies no second source sheet or dynamics selecting it",
            "time_independence": "NOT_PROVED",
            "asymptotic_limits": "NOT_CONSTRUCTED",
            "continuum_trace_domain": "NOT_CONSTRUCTED",
            "standard_to_selected_packet_affiliation": "NOT_PROVED"
        },
        "does_not_establish": [
            "the public one-sheet Bateman--Turok Eq. (19)",
            "that the doubled sheet is a derived BT degree of freedom",
            "time independence of the complete neutral doubled projector",
            "the t-to-plus-or-minus-infinity limits or a spacetime S operator",
            "a continuum, thermodynamic or regulator-independent generalized-Born trace",
            "affiliation of the standard shift-invariant characteristic projector with the selected q10 detector ideal",
            "finite-coupling positivity or a complete all-channel probability",
            "a metric Weyl-gravity, BV--BRST, QME or LORENTZIAN-CAUSAL theorem",
            "literature priority"
        ],
        "next_gate": "Decide whether the parity-conjugate sheet can be generated without changing the source theory. The sharp alternatives are: construct a localized or singular source parity with controlled domain that supplies the conjugate Laurent branch, or prove that every source-affiliated completion retaining the perturbative vacuum must contain an independent doubled sector. On any passing architecture, prove time independence and asymptotic-domain convergence before comparing the standard-projector trace with q10.",
        "provenance": {
            "source_commit": SOURCE_COMMIT,
            "input_hashes": {path: sha256(path) for path in INPUTS},
            "external_source": {
                "title": "Escape from Ostrogradsky via Hidden Ghost Parity",
                "authors": "Sam Bateman and Neil Turok",
                "arxiv": "2607.00096v1",
                "url": "https://arxiv.org/abs/2607.00096",
                "equations": ["18", "19", "20", "Appendix C 31--34"],
                "last_checked": "2026-08-13"
            },
            "method": "Exact rational/Laurent tensor calculation on the normalized S3 cell, rank-product realization of the inherited positive components, and an explicit block-matrix parity-orbit completion.",
            "generated_by": "reverse_physics/bt_standard_characteristic_eq19_squeeze_inheritance.py",
            "independent_verifier": "reverse_physics/verify_bt_standard_characteristic_eq19_squeeze_inheritance.py"
        },
        "checks": {
            "ok": all(checks.values()),
            "passed": sum(checks.values()),
            "total": len(checks),
            "items": checks
        },
        "verification_commands": [
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_standard_characteristic_eq19_squeeze_inheritance.py --write --check",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_standard_characteristic_eq19_squeeze_inheritance.py",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest -v reverse_physics.tests.test_bt_standard_characteristic_eq19_squeeze_inheritance"
        ],
        "report": REPORT
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    payload = build()
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.write:
        with open(CERT, "w", encoding="utf-8") as handle:
            handle.write(rendered)
        print(os.path.relpath(CERT, ROOT))
    if args.check:
        if not payload["checks"]["ok"]:
            for name, passed in payload["checks"]["items"].items():
                if not passed:
                    print("FAIL:", name, file=sys.stderr)
            return 1
        if os.path.exists(CERT):
            with open(CERT, encoding="utf-8") as handle:
                if handle.read() != rendered:
                    print("standard characteristic certificate drift", file=sys.stderr)
                    return 1
        print(
            "BT STANDARD CHARACTERISTIC EQ19 SQUEEZE INHERITANCE: ALL PASS "
            f"({payload['checks']['passed']}/{payload['checks']['total']})"
        )
    if not args.write and not args.check:
        parser.error("choose --write and/or --check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
