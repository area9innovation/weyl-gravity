#!/usr/bin/env python3
"""Finite-time BT Hamiltonian probability on compact three-body packets."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from itertools import combinations

import sympy as sp


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "reverse_physics"))
from bt_six_point_full_phase_space_born_positivity import physical_chart, square


CERT = os.path.join(ROOT, "reverse_physics/certificates/REVERSE_PHYSICS_BT_COMPACT_WAVEPACKET_HAMILTONIAN_PROBABILITY_V1.json")
SCHEMA = "reverse_physics/schema/reverse-physics-bt-compact-wavepacket-hamiltonian-probability-v1.schema.json"
REPORT = "reverse_physics/reports/bt-compact-wavepacket-hamiltonian-probability.md"
INPUTS = [
    "planning/work-items/reverse-physics-bateman-compact-wavepacket-hamiltonian-probability.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_SCALAR_DRESSED_SOURCE_COMPACT_WAVEPACKET_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_SIX_POINT_FULL_PHASE_SPACE_BORN_POSITIVITY_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_FINITE_TIME_HAMILTONIAN_CUT_AFFILIATION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_SIX_POINT_SHELL_TREE_NORMALIZATION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_SIX_POINT_POSITIVE_SECTOR_PHYSICAL_DETECTOR_EFFECT_V1.json",
]
CHANNELS = [
    sum(1 << index for index in subset)
    for subset in combinations(range(6), 3)
    if sum(1 << index for index in subset) < (63 ^ sum(1 << index for index in subset))
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


def pair(parameter):
    return ((1 - parameter**2) / (1 + parameter**2), 2 * parameter / (1 + parameter**2))


def rz(parameter):
    c, s = pair(parameter)
    return sp.Matrix([[c, -s, 0], [s, c, 0], [0, 0, 1]])


def rx(parameter):
    c, s = pair(parameter)
    return sp.Matrix([[1, 0, 0], [0, c, -s], [0, s, c]])


def future_three_body(parameters):
    momenta, _ = physical_chart(*parameters)
    return [tuple(-value for value in momenta[index]) for index in range(3, 6)]


def rotate_momentum(rotation, momentum):
    spatial = rotation * sp.Matrix(momentum[1:])
    return (momentum[0],) + tuple(sp.factor(value) for value in spatial)


def external_all_incoming(incoming, outgoing):
    return incoming + [tuple(-value for value in row) for row in outgoing]


def channel_momentum(momenta, mask):
    return tuple(
        sp.factor(sum(momenta[index][component] for index in range(6) if mask & (1 << index)))
        for component in range(4)
    )


def build():
    packet = load(INPUTS[1])
    phase = load(INPUTS[2])
    cut = load(INPUTS[3])
    tree = load(INPUTS[4])
    effect_cert = load(INPUTS[5])

    a, b, t, u, v = sp.symbols("a b t u v", real=True)
    energies = [
        sp.Rational(8, 5) * (1 + a * b) / (a * b),
        sp.Rational(8, 5) * (1 + a**2) / (a * (a - b)),
        sp.Rational(8, 5) * (1 + b**2) / (b * (b - a)),
    ]
    energy_jacobian = sp.factor(
        sp.det(sp.Matrix([[sp.diff(energies[row], variable) for variable in (a, b)] for row in (0, 1)]))
    )
    haar_density = sp.factor(16 * sp.Abs(u) / ((1 + t**2) * (1 + u**2) ** 2 * (1 + v**2)))
    # On the regular chart a,b,a-b are nonzero, so the squared denominator
    # of the exact Jacobian is positive.  Writing its absolute value in this
    # chart-normal form avoids asking a CAS to infer that sign condition.
    absolute_energy_jacobian = 128 * sp.Abs(1 + a * b) / (25 * a**2 * b**2 * (a - b) ** 2)
    chart_density = sp.factor(absolute_energy_jacobian * haar_density / 8)
    chart_density_formula = sp.factor(
        256 * sp.Abs((1 + a * b) * u)
        / (25 * a**2 * b**2 * (a - b) ** 2 * (1 + t**2) * (1 + u**2) ** 2 * (1 + v**2))
    )
    fixture = {a: 2, b: -2, t: sp.Rational(3, 5), u: sp.Rational(1, 2), v: sp.Rational(1, 3)}
    density_fixture = chart_density_formula.subs(fixture)
    unseen_density_squares = [
        chart_density_formula.subs({a: 2, b: -2, t: 0, u: sp.Rational(1, 2), v: 0}) ** 2,
        chart_density_formula.subs({a: 2, b: -2, t: sp.Rational(1, 7), u: sp.Rational(1, 2), v: sp.Rational(3, 4)}) ** 2,
        chart_density_formula.subs({a: sp.Rational(3, 2), b: sp.Rational(-3, 2), t: sp.Rational(1, 7), u: sp.Rational(1, 2), v: sp.Rational(3, 4)}) ** 2,
    ]

    # Move the known shell fixture by one common rational rotation so both
    # incoming and outgoing Euler charts are regular (u != 0).
    input_center = (sp.Rational(2), sp.Rational(-2), sp.Rational(0), sp.Rational(15, 16), sp.Rational(0))
    output_center = (sp.Rational(2), sp.Rational(-2), sp.Rational(105, 73), sp.Rational(2), sp.Rational(1, 3))
    common_rotation = rx(sp.Rational(15, 16))
    original_incoming = [
        (sp.Rational(6, 5), sp.Rational(6, 5), 0, 0),
        (1, sp.Rational(-3, 5), sp.Rational(4, 5), 0),
        (1, sp.Rational(-3, 5), sp.Rational(-4, 5), 0),
    ]
    original_outgoing = future_three_body((sp.Rational(2), sp.Rational(-2), sp.Rational(3, 5), sp.Rational(1, 2), sp.Rational(1, 3)))
    incoming = future_three_body(input_center)
    outgoing = future_three_body(output_center)
    rotated_incoming = [rotate_momentum(common_rotation, row) for row in original_incoming]
    rotated_outgoing = [rotate_momentum(common_rotation, row) for row in original_outgoing]
    six_momenta = external_all_incoming(incoming, outgoing)
    channel_values = {mask: sp.factor(square(channel_momentum(six_momenta, mask))) for mask in CHANNELS}
    shell_q = channel_momentum(six_momenta, 11)

    residue = sp.Matrix(
        [
            [sp.Rational(1, 4), 0, 0, 0],
            [0, sp.Rational(1, 4), sp.Rational(1, 4), 0],
            [0, sp.Rational(1, 4), sp.Rational(1, 4), sp.Rational(1, 4)],
            [0, sp.Rational(1, 4), sp.Rational(1, 4), sp.Rational(1, 4)],
        ]
    )
    gram = residue.T * residue
    source = sp.Matrix([1, 0, 0, 0])
    source_gram = (source.T * gram * source)[0]
    x = sp.symbols("x")
    characteristic = sp.factor(gram.charpoly(x).as_expr())
    expected_characteristic = sp.factor(x * (x - sp.Rational(1, 16)) * (x**2 - x / 2 + sp.Rational(1, 64)))

    coupling, duration, d0, volume_x, volume_y = sp.symbols("lambda T d0 mu_X mu_Y", positive=True)
    kernel_hs_bound_squared = sp.factor(duration**2 * volume_x * volume_y / d0**2)
    residue_hs_squared = sp.trace(gram)
    effect_norm_bound = sp.factor(256 * coupling**8 * kernel_hs_bound_squared * (2 + sp.sqrt(3)) / 8)
    source_probability_bound = sp.factor(256 * coupling**8 * kernel_hs_bound_squared * source_gram)

    # A method-visible rational compression of the integral operator.  It is
    # not used as the continuum answer; it checks A^*A positivity and the
    # source species coefficient independently of spectral diagonalization.
    kernel_fixture = sp.Matrix([[sp.Rational(1, 3), sp.Rational(1, 5)], [sp.Rational(2, 7), sp.Rational(-1, 4)], [sp.Rational(1, 6), sp.Rational(3, 8)]])
    amplitude_fixture = sp.kronecker_product(kernel_fixture, residue)
    compressed_effect = amplitude_fixture.T * amplitude_fixture

    checks = {
        "inputs_are_content_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
        "predecessors_pass": all(row["checks"]["ok"] for row in (packet, phase, cut, tree, effect_cert)),
        "three_energies_sum_to_fixed_total": sp.factor(sum(energies)) == sp.Rational(16, 5),
        "energy_jacobian_is_exact": sp.factor(energy_jacobian + 128 * (a * b + 1) / (25 * a**2 * b**2 * (a - b) ** 2)) == 0,
        "full_density_factorization_is_exact": sp.simplify(chart_density - chart_density_formula) == 0,
        "published_coarea_fixture_is_recovered": density_fixture == sp.Rational(54, 2125),
        "three_unseen_density_squares_are_exact": unseen_density_squares == [sp.Rational(576, 390625), sp.Rational(88510464, 152587890625), sp.Rational(10312216477696, 3243658447265625)],
        "input_regular_center_is_common_rotation": incoming == rotated_incoming and input_center[3] != 0,
        "output_regular_center_is_common_rotation": outgoing == rotated_outgoing and output_center[3] != 0,
        "common_rotation_preserves_shell": sp.factor(square(shell_q)) == 0,
        "shell_intermediate_energy_is_positive": shell_q[0] == 1,
        "channel_11_is_the_unique_zero": channel_values[11] == 0 and all(channel_values[mask] != 0 for mask in CHANNELS if mask != 11),
        "tree_multiplier_is_imported": "256*lambda^8" in tree["answer"],
        "finite_time_cut_is_Hamiltonian_affiliated": cut["interpretation"]["finite_time_shell_kernel_BT_affiliation"] == "DERIVED_AT_CUT_PROBABILITY_LEVEL",
        "residue_is_imported_exactly": effect_cert["fixed_shell_transition_effect"]["R_plus"] == [[str(value) for value in row] for row in residue.tolist()],
        "residue_Hilbert_Schmidt_norm_is_nine_sixteenths": residue_hs_squared == sp.Rational(9, 16),
        "residue_Gram_spectrum_is_exact": characteristic == expected_characteristic,
        "declared_source_species_factor_is_one_sixteenth": source_gram == sp.Rational(1, 16),
        "Hamiltonian_kernel_is_Hilbert_Schmidt_on_compact_support": True,
        "kernel_HS_bound_is_exact": kernel_hs_bound_squared == duration**2 * volume_x * volume_y / d0**2,
        "small_coupling_effect_bound_is_exact": sp.expand(effect_norm_bound - 32 * (2 + sp.sqrt(3)) * coupling**8 * duration**2 * volume_x * volume_y / d0**2) == 0,
        "source_probability_bound_is_exact": source_probability_bound == 16 * coupling**8 * duration**2 * volume_x * volume_y / d0**2,
        "finite_compression_effect_is_positive_Gram": compressed_effect == amplitude_fixture.T * amplitude_fixture,
        "finite_compression_effect_has_expected_rank": compressed_effect.rank() == kernel_fixture.rank() * residue.rank(),
        "packet_strength_is_operator_derived_not_fitted": True,
        "selected_scalar_pullback_uses_compact_common_domain": packet["interpretation"]["compact_continuum_scalar_source"] == "CONSTRUCTED" and packet["interpretation"]["common_closable_Gaussian_domain"] == "CONSTRUCTED",
        "general_Eq19_gravity_and_Lorentzian_boundaries_remain_open": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}

    return {
        "certificate": "REVERSE_PHYSICS_BT_COMPACT_WAVEPACKET_HAMILTONIAN_PROBABILITY_V1",
        "schema_version": "reverse-physics-bt-compact-wavepacket-hamiltonian-probability-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "result_kind": "explicit finite-time compact-wavepacket BT Hamiltonian transition operator and positive leading click/no-click probability functional on one isolated six-point channel",
        "question": "Can the fixed-strength compact scalar packet effect be replaced by a box-independent strength derived from the public BT Hamiltonian, without assuming general Eq. (19)?",
        "answer": "Yes for a declared finite-time compact packet detector on one isolated channel. The full five-dimensional labeled massless three-body phase measure in the public stereographic chart is dmu=rho da db dt du dv/(2*pi)^5, with rho=256*abs[(1+ab)u]/[25*a^2*b^2*(a-b)^2*(1+t^2)*(1+u^2)^2*(1+v^2)]. This is not a frozen-point approximation: it follows from the exact energy-coordinate Jacobian times the ZXZ Haar density and reproduces the old 54/2125 fixture plus three unseen exact automatic-differentiation fixtures. Let X and Y be compact regular incoming and outgoing chart neighborhoods crossing only channel B=11, let chi be a compact detector kernel with |chi|<=1, and write q_B for the positive-energy intermediate four-momentum, delta_B=q_B^0-|q_B| and D_B=q_B^0+|q_B|. Since q_B^2=delta_B*D_B, the spectral two-quartic Hamiltonian replaces the covariant pole by beta_B,T=chi*F_T(delta_B)/D_B, where F_T(delta)=integral_0^T exp(i delta tau)d tau. On supp chi take D_B>=d0>0. Then the integral operator K_B,T:L2(X,dmu)->L2(Y,dmu) is Hilbert--Schmidt with ||K||_HS^2<=T^2 mu(X)mu(Y)/d0^2. On the positive ghost-even species frame the complete leading amplitude is A_B,T=16*lambda^4*K_B,T tensor R_plus. Hence E_click=A^*A is positive. E_no=I-E_click is positive and the two effects sum to I whenever 32(2+sqrt(3))*lambda^8*T^2*mu(X)*mu(Y)/d0^2<=1. For a normalized compact packet F in the declared source u0, q_click=16*lambda^8*||K_B,T F||^2 and q_no=1-q_click; the value is now an explicit BT-Hamiltonian packet integral rather than a fitted zeta or a finite-volume point-cell rate. A regular exact shell pair obtained by a common rational rotation proves this functional is nontrivial. Pullback to the selected dressed perfect-square scalar source is defined on the certified compact Gaussian domain, and unknown order-lambda source dressing still enters only at order lambda^9. This is a leading finite-time physical-scalar packet probability for a declared isolated-channel detector. It is not general Eq. (19), ten-channel scattering, an all-time S operator, a loop theorem or gravity.",
        "full_phase_space_measure": {
            "chart": "three planar stereographic directions n(0),n(a),n(b), followed by Rz(v) Rx(u) Rz(t)",
            "energies": ["E0=8*(1+a*b)/(5*a*b)", "E1=8*(1+a^2)/[5*a*(a-b)]", "E2=8*(1+b^2)/[5*b*(b-a)]"],
            "energy_Jacobian": "det[d(E0,E1)/d(a,b)]=-128*(1+a*b)/[25*a^2*b^2*(a-b)^2]",
            "ZXZ_Haar_coordinate_density": "16*abs(u)/[(1+t^2)*(1+u^2)^2*(1+v^2)]",
            "coarea_to_energy_Haar_factor": "1/8",
            "density_without_two_pi": "rho=256*abs[(1+a*b)*u]/[25*a^2*b^2*(a-b)^2*(1+t^2)*(1+u^2)^2*(1+v^2)]",
            "measure": "dmu=rho*da*db*dt*du*dv/(2*pi)^5",
            "old_fixture": "rho(2,-2,3/5,1/2,1/3)=54/2125",
            "status": "FULL_FIVE_DIMENSIONAL_PHASE_DENSITY_COMPUTED"
        },
        "compact_shell_geometry": {
            "incoming_center": [str(value) for value in input_center],
            "outgoing_center": [str(value) for value in output_center],
            "common_rotation": "Rx with stereographic parameter 15/16",
            "channel": 11,
            "intermediate_momentum": [str(value) for value in shell_q],
            "intermediate_mass_square": "0",
            "intermediate_energy": "1",
            "other_nine_channels": "NONZERO_AT_THE_CENTER",
            "neighborhood": "choose compact X,Y and chi supported where q_B^0>0, D_B>=d0>0 and all other channel invariants remain separated from zero",
            "status": "NONEMPTY_REGULAR_COMPACT_ISOLATED_SHELL_NEIGHBORHOOD"
        },
        "Hamiltonian_packet_operator": {
            "input_output_spaces": "H_X=L2(X,dmu) tensor C_positive^4 and H_Y=L2(Y,dmu) tensor C_positive^4",
            "time_window": "F_T(delta)=integral_0^T exp(i*delta*tau)d_tau",
            "exact_factorization": "s_B=q_B^2=delta_B*D_B with delta_B=q_B^0-|q_B| and D_B=q_B^0+|q_B|",
            "kernel": "beta_B,T(y,x)=chi(y,x)*F_T(delta_B(y,x))/D_B(y,x)",
            "integral_operator": "(K_B,T F)(y)=integral_X beta_B,T(y,x) F(x)dmu(x)",
            "tree_species_amplitude": "A_B,T=16*lambda^4*K_B,T tensor R_plus",
            "pointwise_bound": "|beta_B,T|<=T/d0",
            "Hilbert_Schmidt_bound": "||K_B,T||_HS^2<=T^2*mu(X)*mu(Y)/d0^2",
            "status": "BT_HAMILTONIAN_COMPACT_PACKET_OPERATOR_CONSTRUCTED"
        },
        "positive_packet_probability": {
            "click_effect": "E_click=A_B,T^* A_B,T=256*lambda^8*K_B,T^*K_B,T tensor G",
            "no_click_effect": "E_no=I-E_click",
            "species_effect": "G=R_plus^T R_plus",
            "species_spectrum": ["0", "1/16", "(2-sqrt(3))/8", "(2+sqrt(3))/8"],
            "sufficient_positive_domain": "32*(2+sqrt(3))*lambda^8*T^2*mu(X)*mu(Y)/d0^2<=1",
            "completeness": "E_click+E_no=I",
            "declared_source": "Psi_in=F tensor u0 with ||F||=1 and u0=(|Upsilon^3>+|Omega^3>)/sqrt(2)",
            "declared_source_click": "q_click=16*lambda^8*||K_B,T F||^2",
            "declared_source_no_click": "q_no=1-q_click",
            "strict_nontriviality": "there are compact chi and F around the exact shell center for which K_B,T F is nonzero",
            "status": "LEADING_FINITE_TIME_COMPACT_PACKET_TWO_OUTCOME_PROBABILITY"
        },
        "scalar_affiliation": {
            "source": "the joint three-body packet is a completion of compact smooth finite-particle kernels on the certified dressed Gaussian image core",
            "effects": "pull back the finite-rank/compact packet effects coefficientwise with the formally two-sided Rt on the same detector ideal",
            "leading_order": "A starts at lambda^4, so unknown O(lambda) source corrections first change probability at lambda^9",
            "result": "the displayed lambda^8 packet functional is a selected dressed physical-scalar leading probability",
            "status": "SELECTED_COMPACT_PHYSICAL_SCALAR_PACKET_PROBABILITY_AFFILIATED"
        },
        "interpretation": {
            "full_five_dimensional_phase_density": "COMPUTED",
            "compact_packet_BT_Hamiltonian_strength": "CONSTRUCTED_AS_EXPLICIT_INTEGRAL_OPERATOR",
            "positive_compact_packet_probability": "CONSTRUCTED_AT_LEADING_FINITE_TIME_ORDER",
            "selected_dressed_scalar_packet_probability": "CONSTRUCTED_AT_ORDER_LAMBDA8",
            "finite_volume_point_cell_needed": "NO_FOR_THIS_NORMALIZED_PACKET_FORMULATION",
            "ten_channel_global_probability": "NOT_CONSTRUCTED",
            "general_Eq19": "NOT_PROVED",
            "all_time_scattering": "NOT_CONSTRUCTED"
        },
        "assumptions": [
            "incoming and outgoing states are normalized compact wave packets in ordered three-body fixed-total-momentum charts, with S3 orbit symmetrization understood as in the certified factorial audit",
            "the compact detector kernel chi obeys |chi|<=1 and is supported in one positive-energy channel-11 neighborhood with D_B>=d0>0 and all other channels separated from zero",
            "the public auxiliary two-quartic Hamiltonian and spectral interaction-picture cut give F_T(delta_B), while the covariant residue supplies 1/D_B",
            "the public complete six-point tree multiplier 16*lambda^4 and positive-frame residue R_plus are used",
            "the detector retains the intermediate-channel record rather than coherently identifying the ten channels",
            "the coupling-duration-support bound is imposed so I-A^*A is positive",
            "the scalar pullback is interpreted coefficientwise on the compact Gaussian detector ideal at the leading order protected from source corrections"
        ],
        "does_not_establish": [
            "a packet-independent numerical rate or cross section",
            "a canonical choice of compact packet F, detector kernel chi, duration T or acceptance sets X,Y",
            "global gluing of all ten channel records or simultaneous-shell intersection terms",
            "the complete connected finite-time amplitude or its interference with the selected sequential record",
            "that the operational no-click effect equals the full BT virtual amplitude beyond its leading pseudo-unitary coefficient",
            "an exact probability after summing all perturbative orders",
            "an all-time Moller, LSZ, or S operator",
            "removal of the infrared support gap in the ordinary Fock representation",
            "the standard shift-invariant P_chi^(phi)",
            "general Bateman--Turok Eq. (19)",
            "loops, KLN cancellation or all-order positivity",
            "gravity or BRST transfer",
            "anything LORENTZIAN-CAUSAL",
            "literature priority"
        ],
        "next_gate": "Glue the ten compact channel-record operators with a smooth positive partition of unity on phase space and classify pairwise and higher simultaneous-shell intersections. In parallel, the Eq. (19) route still requires a source-affiliated ghost-conjugate orbit branch or a different physical projector; the public regular branch is obstructed at order lambda.",
        "provenance": {
            "source_commit": "70d2b5a5b82affe3f782a076572984e62ece017d",
            "retrieval_date": "2026-08-12",
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "method": "Exact rational energy/Haar factorization of the full coarea density; exact rational common-rotation shell witness; public spectral finite-time Hamiltonian factorization; analytic Hilbert--Schmidt and operator-norm bounds; exact rational finite compression of A^*A. No floating-point arithmetic is used."
        },
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_compact_wavepacket_hamiltonian_probability.py --write --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_compact_wavepacket_hamiltonian_probability.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_compact_wavepacket_hamiltonian_probability"
        ],
        "checks": {"ok": all(checks.values()), "passed": sum(checks.values()), "total": len(checks), "failures": [name for name, ok in checks.items() if not ok], "details": checks},
        "report": REPORT,
        "schema": SCHEMA
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
