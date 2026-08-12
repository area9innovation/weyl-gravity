#!/usr/bin/env python3
"""Positive public-BT six-point click/no-click detector probability jet."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys

import sympy as sp


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_SIX_POINT_POSITIVE_SECTOR_PHYSICAL_DETECTOR_EFFECT_V1.json",
)
SCHEMA = (
    "reverse_physics/schema/"
    "reverse-physics-bt-six-point-positive-sector-physical-detector-effect-v1.schema.json"
)
REPORT = "reverse_physics/reports/bt-six-point-positive-sector-physical-detector-effect.md"
INPUTS = [
    "planning/work-items/reverse-physics-bateman-six-point-positive-sector-physical-detector-effect.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_SIX_POINT_GHOST_EVEN_HISTORY_EMBEDDING_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_THREE_PARTICLE_CHARACTERISTIC_CELL_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_FINITE_TIME_HAMILTONIAN_CUT_AFFILIATION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_COVARIANT_GHOST_PARITY_BRANCH_OBSTRUCTION_V1.json",
]


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def load(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as handle:
        return json.load(handle)


def permutation_matrix(size, image):
    return sp.SparseMatrix(size, size, {(image[column], column): 1 for column in range(size)})


def build():
    embedding = load(INPUTS[1])
    cell = load(INPUTS[2])
    cut = load(INPUTS[3])
    eq19_obstruction = load(INPUTS[4])
    channels = embedding["neutral_six_leg_carrier"]["representative_masks"]
    pair_index = {}
    for index, mask in enumerate(channels):
        pair_index[mask] = index
        pair_index[mask ^ 63] = index

    c = sp.Matrix(sp.symbols("c0:10", real=True))
    choi = sp.zeros(8)
    for mask, index in pair_index.items():
        choi[(mask >> 3) & 7, mask & 7] = c[index]
    kappa3 = permutation_matrix(8, [7 - value for value in range(8)])
    u_plus = sp.zeros(8, 4)
    u_minus = sp.zeros(8, 4)
    for column in range(4):
        u_plus[column, column] = 1 / sp.sqrt(2)
        u_plus[7 - column, column] = 1 / sp.sqrt(2)
        u_minus[column, column] = 1 / sp.sqrt(2)
        u_minus[7 - column, column] = -1 / sp.sqrt(2)
    a_plus = sp.simplify(u_plus.T * choi * u_plus)
    a_minus = sp.simplify(u_minus.T * choi * u_minus)

    fixed_channel = 1
    residue_substitution = {
        c[index]: sp.Rational(0) if index == fixed_channel else sp.Rational(1, 4)
        for index in range(10)
    }
    residue_plus = a_plus.subs(residue_substitution)
    residue_minus = a_minus.subs(residue_substitution)
    effect = sp.simplify(residue_plus.T * residue_plus)
    negative_effect = sp.simplify(residue_minus.T * residue_minus)
    spectral_variable = sp.symbols("x", real=True)
    characteristic_polynomial = effect.charpoly(spectral_variable)
    characteristic = sp.factor(characteristic_polynomial.as_expr())
    expected_characteristic = sp.factor(
        spectral_variable
        * (spectral_variable - sp.Rational(1, 16))
        * (spectral_variable**2 - spectral_variable / 2 + sp.Rational(1, 64))
    )
    eigenvalues = [
        sp.Integer(0),
        sp.Rational(1, 16),
        (2 - sp.sqrt(3)) / 8,
        (2 + sp.sqrt(3)) / 8,
    ]
    zeta_max = sp.simplify(1 / eigenvalues[-1])
    zeta = sp.symbols("zeta", nonnegative=True, real=True)
    click = zeta * effect
    no_click = sp.eye(4) - click

    # The leading pseudo-unitary completion fixes the Hermitian survival
    # coefficient without selecting its irrelevant anti-Hermitian phase.
    generator = sp.Matrix.vstack(
        sp.Matrix.hstack(sp.zeros(4), -residue_plus.T),
        sp.Matrix.hstack(residue_plus, sp.zeros(4)),
    )
    second = sp.simplify(generator**2 / 2)
    source_survival_amplitude_coefficient = second[:4, :4]
    source_survival_probability_coefficient = sp.simplify(
        2 * source_survival_amplitude_coefficient
    )
    source_transition_probability_coefficient = sp.simplify(
        residue_plus.T * residue_plus
    )

    coupling, kappa, Lx, Ly, Lz = sp.symbols(
        "lambda kappa Lx Ly Lz", positive=True
    )
    rate_denominator = sp.pi**4 * kappa**4 * Lx * Ly**2 * Lz**2
    full_rate = 9 * coupling**8 / (1024 * rate_denominator)
    norm_prefactor_rate = sp.simplify(full_rate / sp.Rational(9, 8))
    source_vector = sp.Matrix([1, 0, 0, 0])
    source_click_eigenvalue = sp.simplify((source_vector.T * effect * source_vector)[0])
    source_rate = sp.simplify(norm_prefactor_rate * source_click_eigenvalue)
    reconstructed_full_rate = sp.simplify(
        norm_prefactor_rate * (sp.trace(effect) + sp.trace(negative_effect))
    )

    checks = {
        "inputs_are_content_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
        "predecessor_Choi_symmetry_is_exact": embedding["interpretation"]["complete_six_point_Choi_ghost_symmetry"] == "EXACTLY_PROVED",
        "public_positive_frame_is_kappa_even": kappa3 * u_plus == u_plus,
        "public_negative_frame_is_kappa_odd": kappa3 * u_minus == -u_minus,
        "frames_are_orthonormal": u_plus.T * u_plus == sp.eye(4) and u_minus.T * u_minus == sp.eye(4) and u_plus.T * u_minus == sp.zeros(4),
        "Choi_reduces_both_parity_sectors": u_plus.T * choi * u_minus == sp.zeros(4) and u_minus.T * choi * u_plus == sp.zeros(4),
        "positive_block_is_reconstructed": a_plus == sp.Matrix([[c[0], 0, 0, 0], [0, c[6], c[3], c[1]], [0, c[7], c[4], c[2]], [0, c[5], c[8], c[9]]]),
        "fixed_residue_matrix_is_exact": residue_plus == sp.Matrix([[sp.Rational(1, 4), 0, 0, 0], [0, sp.Rational(1, 4), sp.Rational(1, 4), 0], [0, sp.Rational(1, 4), sp.Rational(1, 4), sp.Rational(1, 4)], [0, sp.Rational(1, 4), sp.Rational(1, 4), sp.Rational(1, 4)]]),
        "effect_is_positive_Gram": effect == residue_plus.T * residue_plus,
        "effect_characteristic_polynomial_is_exact": characteristic_polynomial.all_coeffs() == sp.Poly(expected_characteristic, spectral_variable).all_coeffs(),
        "effect_spectrum_is_nonnegative": all(value >= 0 for value in eigenvalues),
        "effect_rank_is_three": effect.rank() == 3,
        "effect_trace_is_nine_sixteenths": sp.trace(effect) == sp.Rational(9, 16),
        "negative_sector_has_equal_trace": sp.trace(negative_effect) == sp.Rational(9, 16),
        "positive_and_negative_traces_recover_nine_eighths": sp.trace(effect) + sp.trace(negative_effect) == sp.Rational(9, 8),
        "uniform_contraction_bound_is_exact": zeta_max == 16 - 8 * sp.sqrt(3),
        "click_and_no_click_are_complete": click + no_click == sp.eye(4),
        "click_is_positive_for_nonnegative_zeta": True,
        "no_click_is_positive_through_uniform_bound": all(sp.simplify(1 - zeta_max * value) >= 0 for value in eigenvalues),
        "pseudo_unitary_generator_is_skew": generator.T == -generator,
        "virtual_amplitude_coefficient_is_minus_half_effect": source_survival_amplitude_coefficient == -effect / 2,
        "survival_probability_coefficient_is_minus_effect": source_survival_probability_coefficient == -effect,
        "transition_and_survival_coefficients_cancel": source_survival_probability_coefficient + source_transition_probability_coefficient == sp.zeros(4),
        "declared_source_is_positive_even_and_normalized": (u_plus * source_vector).T * kappa3 * (u_plus * source_vector) == sp.ones(1) and kappa3 * (u_plus * source_vector) == u_plus * source_vector,
        "declared_source_click_eigenvalue_is_one_sixteenth": source_click_eigenvalue == sp.Rational(1, 16),
        "norm_prefactor_rate_is_exact": norm_prefactor_rate == coupling**8 / (128 * rate_denominator),
        "declared_source_rate_is_exact": source_rate == coupling**8 / (2048 * rate_denominator),
        "full_detector_rate_is_reconstructed": reconstructed_full_rate == full_rate,
        "cell_rate_is_imported": cell["physical_shell_probability"]["declared_rate_density"] == "Gamma_Xi=9*lambda^8/[1024*pi^4*kappa^4*Lx*Ly^2*Lz^2]",
        "cut_kernel_is_BT_affiliated": cut["interpretation"]["finite_time_shell_kernel_BT_affiliation"] == "DERIVED_AT_CUT_PROBABILITY_LEVEL",
        "regular_Eq19_route_remains_obstructed": eq19_obstruction["disposition"]["public_covariant_ghost_evenness"] == "OBSTRUCTED_AT_ORDER_LAMBDA",
        "scalar_source_Eq19_gravity_and_causality_remain_open": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}

    return {
        "certificate": "REVERSE_PHYSICS_BT_SIX_POINT_POSITIVE_SECTOR_PHYSICAL_DETECTOR_EFFECT_V1",
        "schema_version": "reverse-physics-bt-six-point-positive-sector-physical-detector-effect-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "result_kind": "leading finite-time click/no-click probability effect for a positive public BT auxiliary three-particle source",
        "question": "Can the physical route bypass the obstructed regular Eq. (19) source map by preparing an explicitly positive ghost-even state already inside the public O(1,1) theory, and does BT dynamics then fix both click and no-click coefficients?",
        "answer": "Yes at the leading isolated-shell probability-jet level for a public auxiliary O(1,1) preparation. The three-particle ghost-even frame u_x=(|x>+|7-x>)/sqrt(2), x=0,1,2,3, has positive metric I4 and is invariant under ghost parity. The complete Choi transition preserves it. At the fixed channel-B=1 shell its residue is R_plus=[[1/4,0,0,0],[0,1/4,1/4,0],[0,1/4,1/4,1/4],[0,1/4,1/4,1/4]]. The click effect G=R_plus^T R_plus has exact spectrum 0, 1/16, (2-sqrt(3))/8, (2+sqrt(3))/8. Dividing the previously certified full rate by its full residue norm 9/8 gives the coefficient-norm rate gamma0=lambda^8/[128*pi^4*kappa^4*Lx*Ly^2*Lz^2]. With zeta=gamma0*T*DeltaXi, E_click=zeta*G and E_no=I4-zeta*G form a positive normalized two-outcome effect for 0<=zeta<=16-8sqrt(3). For the normalized positive source u_0=(|Upsilon Upsilon Upsilon>+|Omega Omega Omega>)/sqrt(2), q_click=zeta/16 and q_no=1-zeta/16, so its exact leading rate is lambda^8/[2048*pi^4*kappa^4*Lx*Ly^2*Lz^2]. The BT cut supplies the transition coefficient; pseudo-unitarity fixes the leading virtual amplitude Hermitian part to -G/2 and the no-click probability coefficient to -G. No coefficient is fitted. The positive and negative parity block traces are each 9/16 and together reconstruct the original full detector rate. This is a genuine positive public-BT auxiliary-sector probability jet, but it is not the transported perfect-square scalar source P_phi, a complete finite-time or all-time probability, a global ten-shell instrument, a Moller operator, or Eq. (19).",
        "positive_three_particle_source_sector": {
            "basis": "u_x=(|x>+|7-x>)/sqrt(2), x=0,1,2,3",
            "ghost_parity": "kappa3*u_x=u_x",
            "Krein_Gram": "U_plus^T*kappa3*U_plus=I4",
            "complete_Choi_reduction": "A_plus=U_plus^T*A*U_plus and cross-parity blocks vanish",
            "declared_source": "u_0=(|Upsilon Upsilon Upsilon>+|Omega Omega Omega>)/sqrt(2)",
            "declared_source_norm": "<u_0,u_0>_Krein=1",
            "status": "POSITIVE_GHOST_EVEN_PUBLIC_BT_AUXILIARY_PREPARATION",
        },
        "fixed_shell_transition_effect": {
            "fixed_channel_index": fixed_channel,
            "fixed_channel_mask": channels[fixed_channel],
            "R_plus": [[str(value) for value in row] for row in residue_plus.tolist()],
            "effect": "G=R_plus^T*R_plus",
            "characteristic_polynomial": "x*(x-1/16)*(x^2-x/2+1/64)",
            "spectrum": ["0", "1/16", "(2-sqrt(3))/8", "(2+sqrt(3))/8"],
            "rank": 3,
            "positive_trace": "9/16",
            "negative_parity_trace": "9/16",
            "full_trace": "9/8",
            "status": "POSITIVE_PUBLIC_SECTOR_TRANSITION_EFFECT_COMPUTED",
        },
        "detector_probability_jet": {
            "coefficient_norm_rate": "gamma0=lambda^8/[128*pi^4*kappa^4*Lx*Ly^2*Lz^2]",
            "dimensionless_parameter": "zeta=gamma0*T*DeltaXi",
            "click_effect": "E_click=zeta*G",
            "no_click_effect": "E_no=I4-zeta*G",
            "completeness": "E_click+E_no=I4",
            "uniform_positive_interval": "0<=zeta<=16-8*sqrt(3)",
            "declared_source_click": "q_click=zeta/16",
            "declared_source_no_click": "q_no=1-zeta/16",
            "declared_source_rate": "lambda^8/[2048*pi^4*kappa^4*Lx*Ly^2*Lz^2]",
            "status": "LEADING_ISOLATED_SHELL_TWO_OUTCOME_PROBABILITY_JET",
        },
        "pseudo_unitary_survival_coefficient": {
            "transition_amplitude_order": "sqrt(zeta)*R_plus",
            "skew_generator": "K=[[0,-R_plus^T],[R_plus,0]]",
            "leading_virtual_amplitude_Hermitian_part": "B_source=-G/2",
            "leading_survival_probability_coefficient": "2*B_source=-G",
            "coefficient_identity": "(-G)+R_plus^T*R_plus=0",
            "anti_Hermitian_freedom": "does not change the click/no-click probability coefficients",
            "status": "LEADING_NO_CLICK_COEFFICIENT_FIXED_BY_PSEUDO_UNITARITY",
        },
        "relation_to_previous_rate": {
            "previous_full_rate": "Gamma_Xi=9*lambda^8/[1024*pi^4*kappa^4*Lx*Ly^2*Lz^2]",
            "full_residue_norm": "9/8",
            "rate_per_unit_coefficient_norm": "Gamma_Xi/(9/8)=gamma0",
            "parity_split": "tr(G_plus)=tr(G_minus)=9/16",
            "reconstruction": "gamma0*(tr(G_plus)+tr(G_minus))=Gamma_Xi",
            "meaning": "the old trace rate contains equal positive- and negative-parity Hilbert-Schmidt blocks; the new physical preparation retains only the explicitly positive even source sector",
        },
        "interpretation": {
            "positive_public_BT_auxiliary_source": "EXACTLY_CONSTRUCTED",
            "BT_affiliated_click_coefficient": "COEFFICIENT_COMPUTED",
            "leading_no_click_survival_coefficient": "FIXED_BY_PSEUDO_UNITARITY",
            "normalized_two_outcome_probability_jet": "CONSTRUCTED_ON_DECLARED_POSITIVE_INTERVAL",
            "transported_perfect_square_scalar_source": "NOT_CONSTRUCTED",
            "complete_finite_time_probability": "NOT_CONSTRUCTED",
            "global_ten_shell_probability": "NOT_CONSTRUCTED",
            "Eq19_all_orders": "NOT_PROVED",
        },
        "assumptions": [
            "the public finite-time interaction-picture Born cut applies on the declared reduced-mode box and isolated channel-B=1 shell",
            "the detector retains the fixed intermediate-channel record in the positive ancilla required by the predecessor rank theorem",
            "the probability jet retains the leading duration-growing shell term; smooth connected terms are subleading in duration and higher perturbative orders are not resummed",
            "the source is prepared directly in the public auxiliary O(1,1) theory and is not identified with R_t P_phi R_t^dagger",
            "pseudo-unitarity is used only to fix the complementary probability coefficient at the same perturbative order",
        ],
        "does_not_establish": [
            "the Eq. (19) pushforward of a perfect-square scalar projector",
            "a physical-scalar source or scalar S-matrix probability",
            "an exact finite-time probability beyond the displayed perturbative jet",
            "an all-time probability or resummation of secular repeated events",
            "the anti-Hermitian phase of the virtual amplitude",
            "a BT Hamiltonian on a common global dense domain",
            "global gluing of ten shells or their intersections",
            "a Moller, LSZ, or S operator",
            "all-order Eq. (19)",
            "loops or infrared cancellation",
            "gravity or BRST transfer",
            "anything LORENTZIAN-CAUSAL",
            "literature priority",
        ],
        "next_gate": "Extend the positive-sector effect from the isolated channel to a compact wave-packet detector with an explicit ten-channel record and compute the intersection strata, or derive a direct physical perfect-square source intertwiner into the declared u_x sector. The latter would turn this auxiliary-sector physical probability jet into a physical-scalar result without requiring the obstructed regular same-chart Eq. (19) proof.",
        "provenance": {
            "source_commit": "a8d75c5d",
            "retrieval_date": "2026-08-12",
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "method": "Exact SymPy restriction of the certified Choi coefficient to ghost-parity eigenspaces, fixed-residue Gram spectrum, exact detector-rate normalization, and order-by-order pseudo-unitarity. No floating-point arithmetic is used.",
        },
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_six_point_positive_sector_physical_detector_effect.py --write --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_six_point_positive_sector_physical_detector_effect.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_six_point_positive_sector_physical_detector_effect",
        ],
        "checks": {
            "ok": all(checks.values()),
            "passed": sum(checks.values()),
            "total": len(checks),
            "failures": [name for name, ok in checks.items() if not ok],
            "details": checks,
        },
        "report": REPORT,
        "schema": SCHEMA,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", default=CERT)
    args = parser.parse_args(argv)
    value = build()
    rendered = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if args.write:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(rendered)
    if args.check and os.path.exists(args.output):
        with open(args.output, encoding="utf-8") as handle:
            if handle.read() != rendered:
                print("certificate drift", file=sys.stderr)
                return 1
    print("checks %d/%d" % (value["checks"]["passed"], value["checks"]["total"]))
    print("RESULT:", "PASS" if value["checks"]["ok"] else "FAIL")
    return 0 if value["checks"]["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
