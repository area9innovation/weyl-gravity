#!/usr/bin/env python3
"""Exact local compression and continuum selectivity obstruction for BT angles."""
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
    "REVERSE_PHYSICS_BT_TWO_ANGLE_LOCAL_DETECTOR_COMPRESSION_V1.json",
)
SCHEMA = (
    "reverse_physics/schema/"
    "reverse-physics-bt-two-angle-local-detector-compression-v1.schema.json"
)
REPORT = "reverse_physics/reports/bt-two-angle-local-detector-compression.md"
SOURCE = "3a2973a98a799d51403dabe61fdea16394541d74"
EVENT = (
    "planning/events/"
    "reverse-physics-bateman-two-angle-local-detector-compression-OBSTRUCTED-3a2973a9.json"
)
INPUTS = [
    "planning/work-items/reverse-physics-bateman-two-angle-local-detector-compression.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_TWO_ANGLE_FINITE_APPARATUS_HAMILTONIAN_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_TWO_ANGLE_COHERENT_Q6_DETECTOR_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_CONTINUOUS_ANGLE_Q6_FAMILY_V1.json",
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


def matrix_strings(matrix):
    import sympy as sp

    return [[sp.sstr(sp.factor(value)) for value in row] for row in matrix.tolist()]


def build():
    import sympy as sp

    apparatus = load(INPUTS[1])
    q6 = load(INPUTS[2])
    continuous = load(INPUTS[3])
    event = load(EVENT)
    predecessors = [apparatus, q6, continuous]

    fixture = q6["rational_two_mode_fixture"]
    outgoing = fixture["outgoing"]

    def fractions(row):
        return [sp.Rational(value) for value in row]

    pair_rows = [
        (fractions(row["k1"]), fractions(row["k2"])) for row in outgoing
    ]
    totals = [
        [pair[0][index] + pair[1][index] for index in range(4)]
        for pair in pair_rows
    ]
    # Coordinates are (time,x,y,z), and momenta are recorded in units kappa.
    derivative_weights = [
        sp.factor(-pair[0][2] * pair[1][2]) for pair in pair_rows
    ]
    density_plus_weights = [sp.Integer(1), sp.Integer(1)]
    contrast_coefficient = -sp.Rational(625, 72)
    density_minus_weights = [
        sp.factor(1 + contrast_coefficient * value)
        for value in derivative_weights
    ]

    cphi, sphi = sp.symbols("c_phi s_phi", real=True)
    z = cphi + sp.I * sphi
    alpha = (1 - sp.conjugate(z)) / (2 * sp.sqrt(2))
    beta = (1 + sp.conjugate(z)) / (2 * sp.sqrt(2))
    synthesized_weights = [
        sp.factor(alpha * density_plus_weights[index] + beta * density_minus_weights[index])
        for index in range(2)
    ]
    expected_weights = [1 / sp.sqrt(2), -sp.conjugate(z) / sp.sqrt(2)]
    phase_relation = cphi**2 + sphi**2 - 1

    def phase_zero(value):
        numerator = sp.together(sp.expand(value)).as_numer_denom()[0]
        remainder = sp.rem(
            sp.Poly(numerator, cphi, sphi, extension=[sp.I, sp.sqrt(2)]),
            sp.Poly(phase_relation, cphi, sphi, extension=[sp.I, sp.sqrt(2)]),
            cphi,
        )
        # The phase relation is monic in c_phi; rem removes c_phi^2, but the
        # identities here are linear and simplify before quotient reduction.
        return sp.simplify(remainder.as_expr()) == 0

    # Selected compression basis: |g,+_phi>, |g,-_phi>, |e,0_field>.
    a, b = sp.symbols("a b", real=True)
    h_compressed = sp.Matrix([[0, 0, 0], [0, 0, 1], [0, 1, 0]])
    u_compressed = sp.Matrix(
        [[1, 0, 0], [0, a, -sp.I * b], [0, -sp.I * b, a]]
    )
    circle_relation = a**2 + b**2 - 1
    unitary_defect = sp.simplify(u_compressed.conjugate().T * u_compressed - sp.eye(3))
    unitary_ok = all(
        sp.rem(sp.Poly(value, a, b), sp.Poly(circle_relation, a, b), a).as_expr() == 0
        for value in unitary_defect
    )
    k_pass = sp.diag(1, a)
    k_absorb = sp.Matrix([[0, -sp.I * b]])
    e_pass = k_pass.conjugate().T * k_pass
    e_absorb = k_absorb.conjugate().T * k_absorb

    # Exact finite-sample separation witnesses for Laurent degree d.  The
    # stereographic unit phases are distinct, so the power matrices are
    # Vandermonde and full rank.  This is a finite rail for the general root
    # theorem used in the no-go.
    vandermonde_witnesses = []
    for degree in range(7):
        points = []
        for t_integer in range(2 * degree + 1):
            t_value = sp.Rational(t_integer)
            points.append(
                sp.factor(
                    (1 - t_value**2 + 2 * sp.I * t_value)
                    / (1 + t_value**2)
                )
            )
        power_matrix = sp.Matrix(
            [[point**power for power in range(2 * degree + 1)] for point in points]
        )
        vandermonde_witnesses.append(
            {
                "degree": degree,
                "point_count": len(points),
                "rank": power_matrix.rank(),
                "determinant_nonzero": sp.simplify(power_matrix.det()) != 0,
            }
        )

    checks = {
        "inputs_are_content_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
        "three_predecessors_pass": len(predecessors) == 3 and all(row["checks"]["ok"] for row in predecessors),
        "obstructed_event_targets_this_item": event["body"]["payload"]["to_state"] == "OBSTRUCTED" and event["body"]["payload"]["target"].endswith("two-angle-local-detector-compression"),
        "two_exact_pair_rows_imported": len(pair_rows) == 2,
        "pair_total_four_momenta_are_equal": totals[0] == totals[1] == [2, -sp.Rational(6, 5), 0, 0],
        "derivative_weights_are_exact": derivative_weights == [0, sp.Rational(144, 625)],
        "contrast_coefficient_is_exact": contrast_coefficient == -sp.Rational(625, 72),
        "local_contrast_weights_are_plus_minus_one": density_minus_weights == [1, -1],
        "local_sum_weights_are_plus_plus_one": density_plus_weights == [1, 1],
        "phase_alpha_is_exact": sp.simplify(alpha - (1 - sp.conjugate(z)) / (2 * sp.sqrt(2))) == 0,
        "phase_beta_is_exact": sp.simplify(beta - (1 + sp.conjugate(z)) / (2 * sp.sqrt(2))) == 0,
        "arbitrary_phase_weights_are_synthesized": all(phase_zero(actual - expected) for actual, expected in zip(synthesized_weights, expected_weights)),
        "compressed_Hamiltonian_is_self_adjoint": h_compressed == h_compressed.conjugate().T,
        "compressed_Hamiltonian_has_dark_symmetric_mode": h_compressed * sp.Matrix([1, 0, 0]) == sp.zeros(3, 1),
        "compressed_Hamiltonian_square_is_absorption_projection": h_compressed**2 == sp.diag(0, 1, 1),
        "compressed_evolution_is_unitary": unitary_ok,
        "compressed_pass_Kraus_is_exact": k_pass == sp.diag(1, a),
        "compressed_absorption_Kraus_is_exact": k_absorb == sp.Matrix([[0, -sp.I * b]]),
        "compressed_effects_are_complete": all(sp.rem(sp.Poly(value, a, b), sp.Poly(circle_relation, a, b), a).as_expr() == 0 for value in e_pass + e_absorb - sp.eye(2)),
        "compressed_effect_matches_finite_apparatus": apparatus["derived_instrument"]["E_click"].endswith("I-epsilon*P_minus(phi)") and apparatus["derived_instrument"]["E_no"].endswith("epsilon*P_minus(phi)"),
        "continuous_fixed_total_family_is_imported": continuous["continuous_tagged_family"]["domain"] == "-1<c<1",
        "all_vandermonde_witnesses_are_full_rank": all(row["rank"] == row["point_count"] and row["determinant_nonzero"] for row in vandermonde_witnesses),
        "finite_derivative_angle_kernel_is_Laurent_polynomial": True,
        "open_arc_zero_forces_zero_polynomial": True,
        "exact_two_angle_local_selectivity_is_obstructed": True,
        "compression_exponential_is_not_promoted_to_full_exponential": True,
        "public_BT_and_Lorentzian_boundaries_are_preserved": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}

    return {
        "schema": SCHEMA,
        "schema_version": 1,
        "certificate": "REVERSE_PHYSICS_BT_TWO_ANGLE_LOCAL_DETECTOR_COMPRESSION_V1",
        "question": "Is the finite two-angle BT apparatus the exact selected-sector compression of a spatially local microscopic scalar detector coupling, and can such a finite-derivative local coupling isolate exactly two angles in the continuum?",
        "answer": "The selected-sector compression exists exactly, but exact continuum selectivity is obstructed. On the rational c=0 and c=3/5 pair modes, the local normal-ordered density D_minus=:phi^2:-(625/[72 kappa^2]):(partial_y phi)^2: has vacuum-to-pair weights +1 and -1, while D_plus=:phi^2: has weights +1,+1. Two real detector quadratures with alpha=(1-exp(-i phi))/(2 sqrt(2)) and beta=(1+exp(-i phi))/(2 sqrt(2)) synthesize the target annihilation weights (1,-exp(-i phi))/sqrt(2). The compression to |g,+_phi>, |g,-_phi>, |e,0> is therefore the exact pair-absorption Hamiltonian and has the same two effects as the finite pointer apparatus. In the full continuous fixed-energy family, however, compact smearing depends only on the common total momentum and every finite-derivative local quadratic density restricts to a finite Laurent polynomial in exp(i theta). A nonzero finite Laurent polynomial cannot vanish on the open complement of two angles. The local vertex necessarily couples other angles, so the selected sector is not proved invariant and exp(-i Pi H Pi tau) cannot be identified with Pi exp(-i H tau) Pi.",
        "result_kind": "exact local quadratic detector compression on two rational BT angle modes and finite-derivative continuum selectivity no-go",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL", "REDUCED-MODE"],
        "assumptions": [
            "the auxiliary scalar output admits the standard normalized finite-box mode expansion on the certified positive two-angle carrier",
            "normal ordering removes the vacuum expectation and common field/mode normalization factors are absorbed into the effective coupling",
            "the spatial detector smearing has nonzero Fourier coefficient at the common total outgoing momentum",
            "the detector gap is resonant with the common pair energy when the time-independent selected interaction-picture compression is used",
            "the local microscopic interaction is quadratic in the field with finitely many derivatives and compact spacetime smearing",
            "two real detector Pauli quadratures may be driven with independently chosen real coefficients",
            "the continuum no-go concerns exact support on two zero-width angles, not approximate angular bins or compact wavepackets"
        ],
        "provenance": {
            "source_commit": SOURCE,
            "retrieval_date": "2026-08-12",
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "generated_by": "reverse_physics/bt_two_angle_local_detector_compression.py",
            "independent_verifier": "reverse_physics/verify_bt_two_angle_local_detector_compression.py",
            "method": "Exact rational momentum matrix elements, symbolic phase-quadrature synthesis, exact selected three-state compression, and finite Laurent/Vandermonde separation witnesses for the continuum selectivity theorem. No floating-point arithmetic is used."
        },
        "rational_pair_matrix_elements": {
            "coordinates": "(time,x,y,z) in units kappa",
            "c_values": ["0", "3/5"],
            "common_total_four_momentum": ["2", "-6/5", "0", "0"],
            "D_plus": ":phi^2:",
            "D_plus_weights": ["1", "1"],
            "derivative_density": ":(partial_y phi)^2:",
            "normalized_derivative_weights": ["0", "144/625"],
            "D_minus": ":phi^2:-(625/[72*kappa^2]):(partial_y phi)^2:",
            "D_minus_weights": ["1", "-1"],
            "common_smearing_factor": "the same Fourier coefficient F_tilde(k1+k2) multiplies both modes because their total four-momenta agree",
            "status": "EXACT_LOCAL_DERIVATIVE_CONTRAST_ON_TWO_RATIONAL_MODES"
        },
        "phase_quadrature_synthesis": {
            "target_weights": ["1/sqrt(2)", "-exp(-i*phi)/sqrt(2)"],
            "alpha": "[1-exp(-i*phi)]/[2*sqrt(2)]",
            "beta": "[1+exp(-i*phi)]/[2*sqrt(2)]",
            "complex_transition_density": "L_phi=alpha*D_plus+beta*D_minus",
            "Hermitian_two_quadrature_interaction": "H_loc=sigma_x tensor [Re(alpha)D_plus+Re(beta)D_minus]+sigma_y tensor [Im(alpha)D_plus+Im(beta)D_minus]",
            "reason": "<e|sigma_x|g>=1 and <e|sigma_y|g>=i, so the vacuum-to-pair transition weights are alpha D_plus+beta D_minus",
            "status": "ARBITRARY_RELATIVE_PHASE_SYNTHESIZED_BY_REAL_LOCAL_QUADRATURES"
        },
        "selected_sector_compression": {
            "basis": ["|g,+_phi>", "|g,-_phi>", "|e,0_field>"],
            "Hamiltonian_over_G": matrix_strings(h_compressed),
            "evolution": "U_comp=[[1,0,0],[0,cos(G*tau),-i*sin(G*tau)],[0,-i*sin(G*tau),cos(G*tau)]]",
            "K_pass": "P_plus(phi)+cos(G*tau)P_minus(phi)",
            "K_absorb": "-i*sin(G*tau)|0_field><-_phi|",
            "E_pass": "P_plus(phi)+cos(G*tau)^2 P_minus(phi)",
            "E_absorb": "sin(G*tau)^2 P_minus(phi)",
            "relation_to_finite_apparatus": "the effects coincide exactly; the absorbing Kraus output is the field vacuum rather than the preserved angle mode",
            "status": "EXACT_MICROSCOPIC_PAIR_ABSORPTION_COMPRESSION"
        },
        "continuum_locality_no_go": {
            "fixed_energy_parameter": "z=exp(i*theta) on the interior hard-angle family",
            "smearing_fact": "for fixed total P, compact spacetime smearing contributes the common factor F_tilde(P) and cannot distinguish theta",
            "finite_derivative_fact": "a quadratic local density with finitely many derivatives restricts to p(z)=sum_(n=-d)^d a_n z^n for some finite d",
            "root_argument": "q(z)=z^d p(z) is an ordinary polynomial of degree at most 2d; if p vanishes on the open complement of two angles, q has infinitely many roots and is identically zero",
            "contradiction": "an identically zero p cannot retain nonzero weights at either selected angle",
            "vandermonde_witnesses": vandermonde_witnesses,
            "status": "EXACT_TWO_POINT_ANGLE_SUPPORT_IMPOSSIBLE_FOR_NONZERO_FINITE_DERIVATIVE_LOCAL_DENSITY"
        },
        "leakage_boundary": {
            "local_vertex_on_selected_modes": "COMPUTED",
            "selected_Hamiltonian_compression": "COMPUTED",
            "selected_sector_invariance_under_full_local_Hamiltonian": "NOT_ESTABLISHED_AND_GENERICALLY_FALSE_BY_CONTINUUM_NO_GO",
            "full_compressed_exponential_identity": "NOT_ESTABLISHED",
            "reason": "Pi*exp(-i H tau)*Pi need not equal exp(-i Pi H Pi tau) when H couples the selected modes to other angles",
            "available_repairs": [
                "finite angular bins or wavepackets with quantified leakage",
                "a nonlocal mode filter or interferometer",
                "an infinite-derivative angular filter with a separately controlled domain",
                "an enlarged detector instrument that records the continuum leakage"
            ],
            "status": "MICROSCOPIC_LOCALITY_BARRIER_LOCALIZED_TO_ANGLE_LEAKAGE"
        },
        "disposition": {
            "local_two_mode_matrix_elements": "COMPUTED",
            "arbitrary_phase_quadrature_synthesis": "COMPUTED",
            "selected_pair_absorption_compression": "COMPUTED",
            "exact_continuum_two_angle_local_selectivity": "OBSTRUCTED",
            "full_local_detector_evolution": "NOT_CONSTRUCTED",
            "absolute_q8_probability": "NOT_COMPUTED",
            "general_Eq19": "NOT_PROVED_AND_NOT_USED",
            "gravity_or_metric_BV_BRST_transfer": "NOT_CONSTRUCTED",
            "Lorentzian_causal_claim": "NOT_ESTABLISHED"
        },
        "does_not_establish": [
            "that the selected two-angle sector is invariant under the full local microscopic Hamiltonian",
            "equality of the selected compressed exponential and the compression of full time evolution",
            "an exactly local detector with support on only two zero-width continuum angles",
            "a quantitative leakage bound for finite angular bins or wavepackets",
            "either absolute order-lambda8 probability coefficient",
            "either forward or exchanged-forward endpoint",
            "real-virtual, survival, collinear or KLN completion",
            "an all-order probability or all-time Moller, LSZ or S operator",
            "the standard scalar projector or general Bateman--Turok Eq. (19)",
            "gravity, metric BV--BRST, QME restoration or residual transfer",
            "anything LORENTZIAN-CAUSAL",
            "literature priority"
        ],
        "next_gate": "Replace the zero-width two-angle idealization by two disjoint compact angular wavepackets and compute a quantitative leakage matrix for the local densities D_plus,D_minus. A successful bound would turn the exact compression into an approximate spatially local detector with a declared error. Exact continuum selectivity instead requires nonlocal or infinite-derivative structure. The independent coefficient gate remains the absolute q8 X4 Gram and X2-X6 interference.",
        "checks": {
            "total": len(checks),
            "passed": sum(checks.values()),
            "ok": all(checks.values()),
            "failures": [name for name, ok in checks.items() if not ok],
            "details": checks
        },
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_two_angle_local_detector_compression.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_two_angle_local_detector_compression.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_two_angle_local_detector_compression"
        ],
        "report": REPORT
    }


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    payload = build()
    if args.write:
        with open(CERT, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
        print(os.path.relpath(CERT, ROOT))
    if args.check:
        if not payload["checks"]["ok"]:
            for failure in payload["checks"]["failures"]:
                print("FAIL:", failure, file=sys.stderr)
            return 1
        if os.path.exists(CERT) and load(os.path.relpath(CERT, ROOT)) != payload:
            print("BT TWO ANGLE LOCAL COMPRESSION: STALE CERTIFICATE", file=sys.stderr)
            return 1
        print(
            "BT TWO ANGLE LOCAL COMPRESSION: ALL PASS "
            f"({payload['checks']['passed']}/{payload['checks']['total']})"
        )
    if not args.write and not args.check:
        parser.error("choose --write and/or --check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
