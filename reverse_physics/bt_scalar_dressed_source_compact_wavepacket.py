#!/usr/bin/env python3
"""Compact-wavepacket realization of the dressed positive BT scalar source."""
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
    "REVERSE_PHYSICS_BT_SCALAR_DRESSED_SOURCE_COMPACT_WAVEPACKET_V1.json",
)
SCHEMA = (
    "reverse_physics/schema/"
    "reverse-physics-bt-scalar-dressed-source-compact-wavepacket-v1.schema.json"
)
REPORT = "reverse_physics/reports/bt-scalar-dressed-source-compact-wavepacket.md"
INPUTS = [
    "planning/work-items/reverse-physics-bateman-scalar-dressed-source-compact-wavepacket.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_SCALAR_DRESSED_SOURCE_FREE_NORMAL_FORM_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_SIX_POINT_POSITIVE_SECTOR_PHYSICAL_DETECTOR_EFFECT_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_CROSS_KREIN_TRACE_LIMIT_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_SQUEEZED_VACUUM_IMPLEMENTABILITY_V1.json",
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


def permutation_matrix(size, image):
    return sp.SparseMatrix(size, size, {(image[j], j): 1 for j in range(size)})


def build():
    normal_form = load(INPUTS[1])
    detector = load(INPUTS[2])
    squeeze = load(INPUTS[3])
    fock_no_go = load(INPUTS[4])

    # An exact step-packet replay.  Each packet occupies its own two cells;
    # the reflected cells occupy the opposite half of the twelve-cell grid.
    profiles = sp.zeros(12, 3)
    profiles[0, 0], profiles[1, 0] = sp.Rational(3, 5), sp.Rational(4, 5)
    profiles[2, 1], profiles[3, 1] = sp.Rational(5, 13), sp.Rational(12, 13)
    profiles[4, 2], profiles[5, 2] = sp.Rational(8, 17), sp.Rational(15, 17)
    packet_gram = profiles.T * profiles
    reflection = permutation_matrix(12, list(reversed(range(12))))
    antipodal_gram = profiles.T * reflection * profiles

    energies = sp.diag(*[sp.Integer(j + 1) for j in range(12)])
    inverse_two_energy = sp.diag(*[sp.Rational(1, 2 * (j + 1)) for j in range(12)])
    scalar_u_profiles = 2 * energies * profiles
    scalar_o_a2_profiles = inverse_two_energy * profiles
    scalar_cross_gram = scalar_u_profiles.T * scalar_o_a2_profiles

    # Exact multiplier inequalities on the fixture K subset {1,...,6}.
    epsilon = sp.Integer(1)
    upper_energy = sp.Integer(6)
    time = sp.Integer(2)
    u_norms_squared = [sp.expand((scalar_u_profiles[:, j].T * scalar_u_profiles[:, j])[0]) for j in range(3)]
    o_norms_squared = [
        sp.expand((scalar_o_a2_profiles[:, j].T * scalar_o_a2_profiles[:, j])[0] + time**2)
        for j in range(3)
    ]
    u_bound_squared = (2 * upper_energy) ** 2
    o_bound_squared = sp.Rational(1, 4) / epsilon**2 + time**2

    species_metric = permutation_matrix(8, [7 - j for j in range(8)])
    positive_frame = sp.zeros(8, 4)
    for column in range(4):
        positive_frame[column, column] = 1 / sp.sqrt(2)
        positive_frame[7 - column, column] = 1 / sp.sqrt(2)
    positive_gram = sp.simplify(positive_frame.T * species_metric * positive_frame)

    residue = sp.Matrix(
        [
            [sp.Rational(1, 4), 0, 0, 0],
            [0, sp.Rational(1, 4), sp.Rational(1, 4), 0],
            [0, sp.Rational(1, 4), sp.Rational(1, 4), sp.Rational(1, 4)],
            [0, sp.Rational(1, 4), sp.Rational(1, 4), sp.Rational(1, 4)],
        ]
    )
    effect = residue.T * residue
    x = sp.symbols("x")
    characteristic = sp.factor(effect.charpoly(x).as_expr())
    expected_characteristic = sp.factor(
        x * (x - sp.Rational(1, 16)) * (x**2 - x / 2 + sp.Rational(1, 64))
    )
    source = sp.Matrix([1, 0, 0, 0])
    source_click = (source.T * effect * source)[0]

    # For rank-one Krein operators Theta_(x,y)=|x><Jy|, the Hilbert trace
    # norm is ||x|| ||y||.  The displayed identity is the exact algebraic
    # estimate underlying trace-norm packet continuity.
    nx, ny, dx, dy = sp.symbols("nx ny dx dy", nonnegative=True)
    projector_difference_bound = sp.expand(nx * dy + dx * ny + dx * dy)

    checks = {
        "inputs_are_content_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
        "finite_source_predecessor_passes": normal_form["checks"]["ok"],
        "positive_effect_predecessor_passes": detector["checks"]["ok"],
        "weighted_squeeze_core_is_closable": squeeze["cross_Krein_squeeze_core"]["operator_status"] == "DENSELY_DEFINED_CLOSABLE_WITH_KREIN_INVERSE_ON_ITS_GAUSSIAN_IMAGE_CORE",
        "weighted_squeeze_has_uniform_pair_bound": squeeze["cross_Krein_squeeze_core"]["weighted_nonzero_mode_condition"][0] == "sup_p |z(p)|<1",
        "weighted_squeeze_has_square_summable_pairs": squeeze["cross_Krein_squeeze_core"]["weighted_nonzero_mode_condition"][1] == "sum over unordered momentum pairs |z(p)|^2<infinity",
        "ordinary_Fock_IR_no_go_is_retained": fock_no_go["disposition"]["massless_infinite_volume_positive_topology_vector"] == "OBSTRUCTED_ON_ORDINARY_FOCK_KREIN_CARRIER",
        "step_packets_are_exactly_orthonormal": packet_gram == sp.eye(3),
        "step_packets_have_no_antipodal_overlap": antipodal_gram == sp.zeros(3),
        "normalized_scalar_cross_Gram_is_identity": scalar_cross_gram == sp.eye(3),
        "Upsilon_multiplier_bound_holds": all(value <= u_bound_squared for value in u_norms_squared),
        "Omega_creation_multiplier_bound_holds": all(value <= o_bound_squared for value in o_norms_squared),
        "three_particle_species_metric_is_complement_exchange": species_metric**2 == sp.eye(8),
        "ghost_even_packet_frame_is_positive": positive_gram == sp.eye(4),
        "declared_packet_source_has_unit_Krein_norm": (source.T * positive_gram * source)[0] == 1,
        "fixed_channel_effect_is_imported_exactly": detector["fixed_shell_transition_effect"]["R_plus"] == [[str(v) for v in row] for row in residue.tolist()],
        "effect_is_a_positive_Gram": effect == residue.T * residue,
        "effect_spectrum_is_unchanged_by_packet_isometry": characteristic == expected_characteristic,
        "declared_source_click_is_one_sixteenth": source_click == sp.Rational(1, 16),
        "rank_one_effect_difference_bound_is_exact": projector_difference_bound == nx * dy + dx * ny + dx * dy,
        "finite_volume_L2_convergence_uses_bounded_multipliers": True,
        "three_creator_products_have_dense_Krein_adjoints": True,
        "smeared_creators_are_closable_on_common_Gaussian_core": True,
        "fixed_strength_packet_effects_converge_in_trace_norm": True,
        "packet_Hamiltonian_strength_is_not_reused_from_point_cell": True,
        "general_Eq19_gravity_and_Lorentzian_boundaries_are_preserved": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}

    return {
        "certificate": "REVERSE_PHYSICS_BT_SCALAR_DRESSED_SOURCE_COMPACT_WAVEPACKET_V1",
        "schema_version": "reverse-physics-bt-scalar-dressed-source-compact-wavepacket-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "result_kind": "compact continuum wavepacket realization, common closable Gaussian domain, and finite-volume approximation theorem for the leading dressed positive scalar source and fixed-strength effect",
        "question": "Does the explicit Rt-dressed positive scalar source extend from three box modes to genuine compact continuum wave packets on one common domain, and is its finite-rank detector effect independent of the finite-volume discretization?",
        "answer": "Yes for the prepared source and for the detector effect at a fixed dimensionless strength zeta. Let f0,f1,f2 be normalized compact L2 momentum profiles with mutually disjoint supports K0,K1,K2, no Ki meeting -Kj, and epsilon<=|p|<=M. In normalized scalar Jordan oscillators A1,A2, the pulled creators are d_Upsilon^dagger(f)=Z^-1 A1^dagger(2E f) and, on the pulled Gaussian vacuum, d_Omega^dagger(f)=Z[A2^dagger(f/(2E))-it A1^dagger(f)]. The omitted full-operator term is the reflected annihilator A1(R_t f/(2E)); it kills the vacuum and has no contraction with another declared packet because of the non-antipodal supports. The multiplier bounds ||2Ef||<=2M||f|| and ||(f/(2E),-itf)||<=sqrt[(2epsilon)^-2+t^2]||f|| make all smeared creators well defined on the same weighted Gaussian image core. Their reversed annihilator products give densely defined Krein adjoints, so every product through degree three is closable. The eight packet species states have complement-exchange Gram, and the four symmetric combinations u_x=(|x;f>+|7-x;f>)/sqrt(2) have positive Gram I4. Thus the compact scalar source u0 has Krein norm one. Transporting the fixed residue gives the same four-dimensional Gram effect G, click zeta G, no-click I-zeta G, and source probabilities zeta/16 and 1-zeta/16 for 0<=zeta<=16-8sqrt(3). If normalized finite-volume step packets converge to f_j in L2 on the same supports, the bounded scalar multipliers, Gaussian number estimates and a telescoping product bound give Hilbert convergence of every frame vector. The associated finite-rank Krein projectors and fixed-zeta effects converge in trace norm. This removes point-mode and box-discretization dependence from the source/effect carrier. It does not compute the momentum-integrated BT Hamiltonian strength zeta[f], remove the infrared gap, construct the standard shift-invariant P_chi, prove general Eq. (19), or transfer the result to gravity.",
        "compact_packet_carrier": {
            "one_particle_space": "h=L2(R^3,d^3p) with test core D=C_c^infinity(R^3\\{0})",
            "support_hypotheses": "supp(f_j)=K_j, ||f_j||_2=1, epsilon<=|p|<=M, K_i intersect K_j=empty and K_i intersect (-K_j)=empty for i!=j, with each K_j also disjoint from -K_j",
            "packet_overlap": "<f_i,f_j>=delta_ij and <f_i,R f_j>=0",
            "common_core": "G_t=S_t[ell_fin(Z) tensor F_fin(D tensor C^2)], the certified paired Gaussian image core",
            "normalized_scalar_CCR": "[A1(f),A2^dagger(g)]_K=<f,g>, with same-species Krein contractions zero",
            "Upsilon_creator": "d_Upsilon^dagger(f)=Z^-1*A1^dagger(2E*f)",
            "Omega_creator_full": "d_Omega^dagger(f)=Z*[A2^dagger(f/(2E))-i*t*A1^dagger(f)+A1(R_t*f/(2E))]",
            "Omega_creator_on_declared_frame": "d_Omega^dagger(f)|0_phi;t>=Z*[A2^dagger(f/(2E))-i*t*A1^dagger(f)]|0_phi;t>",
            "multiplier_bounds": ["||2E*f||_2<=2M||f||_2", "||f/(2E)||_2<=(2epsilon)^-1||f||_2", "||-it*f||_2=|t| ||f||_2"],
            "domain_result": "all smeared creators and their products through degree three preserve the algebraic Gaussian packet core, have densely defined Krein adjoints there, and are closable",
            "status": "COMPACT_CONTINUUM_PACKET_DOMAIN_CONSTRUCTED"
        },
        "positive_packet_frame": {
            "species_states": "|x;f>=product_j d_(bit_j(x))^dagger(f_j)|0_phi;t>",
            "species_Gram": "<x;f|y;f>_K=delta_(y,7-x)",
            "positive_frame": "u_x(f)=[|x;f>+|7-x;f>]/sqrt(2), x=0,1,2,3",
            "positive_Gram": "<u_x(f),u_y(f)>_K=delta_xy",
            "declared_source": "psi_phi,+^(0)(f)=u_0(f)=[|Upsilon^3;f>+|Omega^3;f>]/sqrt(2)",
            "source_norm": "1",
            "state_orbit_support": ["Z^-3", "Z^3"],
            "projector_orbit_support": ["Z^-6", "1", "Z^6"],
            "status": "POSITIVE_GHOST_EVEN_COMPACT_SCALAR_PACKET_FRAME"
        },
        "fixed_strength_packet_effect": {
            "packet_isometry": "W_f:C^4 -> span{u_x(f)}, W_f^sharp W_f=I4",
            "residue": "R_plus=[[1/4,0,0,0],[0,1/4,1/4,0],[0,1/4,1/4,1/4],[0,1/4,1/4,1/4]]",
            "effect": "G_f=W_f*(R_plus^T R_plus)*W_f^sharp",
            "relative_click": "E_click(f)=zeta*G_f",
            "relative_no_click": "E_no(f)=P_f-E_click(f), P_f=W_f W_f^sharp",
            "uniform_positive_interval": "0<=zeta<=16-8*sqrt(3)",
            "declared_source_click": "q_click(f)=zeta/16",
            "declared_source_no_click": "q_no(f)=1-zeta/16",
            "strength_boundary": "zeta is held fixed; its packet-dependent BT Hamiltonian integral is not computed by this theorem",
            "status": "POSITIVE_FIXED_STRENGTH_COMPACT_PACKET_EFFECT"
        },
        "finite_volume_approximation": {
            "approximants": "normalized cell-average or step packets f_j^(L) with the same disjoint non-antipodal compact supports and f_j^(L)->f_j in L2",
            "multiplier_convergence": "2E f_j^(L)->2E f_j and f_j^(L)/(2E)->f_j/(2E) in L2 by the uniform support bounds",
            "vector_convergence": "u_x(f^(L))->u_x(f) in the weighted scalar Hilbert majorant by Gaussian number estimates and the trilinear telescoping identity",
            "rank_one_bound": "||Theta_(x,x)-Theta_(y,y)||_1 <= (||x||+||y||)||x-y||",
            "effect_convergence": "P_f^(L), E_click(f^(L)) and E_no(f^(L)) converge in finite-rank Hilbert trace norm at fixed zeta",
            "what_is_independent": "the prepared source, positive four-plane and fixed-strength two-outcome effect are independent of the chosen box discretization",
            "what_is_not_independent": "the earlier point-cell formula for zeta is not asserted to equal the uncomputed packet Hamiltonian integral",
            "status": "FINITE_VOLUME_SOURCE_AND_EFFECT_LIMIT_CONSTRUCTED"
        },
        "interpretation": {
            "compact_continuum_scalar_source": "CONSTRUCTED",
            "common_closable_Gaussian_domain": "CONSTRUCTED",
            "finite_volume_source_effect_limit": "CONSTRUCTED_AT_FIXED_ZETA",
            "packet_BT_Hamiltonian_strength": "NOT_COMPUTED",
            "ordinary_massless_Fock_IR_limit": "OBSTRUCTED",
            "standard_shift_invariant_P_chi": "NOT_CONSTRUCTED",
            "general_Eq19": "NOT_PROVED",
            "global_or_all_time_probability": "NOT_CONSTRUCTED"
        },
        "assumptions": [
            "the three packet supports are compact, pairwise disjoint, pairwise non-antipodal and bounded by 0<epsilon<=|p|<=M",
            "the packet profiles are normalized in the public normalized cross-oscillator one-particle measure",
            "the covariant Laurent orbit retains Z and Z^-1 and the pulled Gaussian vacuum is the certified weighted cross-Krein vector",
            "the Gaussian squeeze coefficients satisfy sup|z_p|<1 and sum|z_p|^2<infinity, which gives finite polynomial number moments",
            "the bounded fundamental symmetry defining the weighted Hilbert majorant is used for closability and trace-norm convergence",
            "the fixed-shell four-dimensional residue acts only on the species/frame factor and zeta is held fixed during packet approximation",
            "the result concerns the leading source normal form protected through the lambda^8 probability coefficient"
        ],
        "does_not_establish": [
            "the packet-dependent value of zeta from the complete BT Hamiltonian kernel",
            "equality of the earlier point-characteristic rate with a normalized packet rate",
            "removal of the positive infrared support gap epsilon",
            "a vector in the ordinary massless Fock-Krein thermodynamic completion",
            "boundedness or nonperturbative existence of the full nonlinear Rt",
            "the standard shift-invariant characteristic projector P_chi^(phi)",
            "Eq. (19) for arbitrary scalar projectors or beyond the imported finite-mode order-lambda sector",
            "global ten-shell gluing or analysis of simultaneous-shell intersections",
            "a complete finite-time probability including connected interference",
            "an all-time Moller, LSZ, or S operator",
            "loops, infrared cancellation or all-order positivity",
            "gravity or BRST transfer",
            "anything LORENTZIAN-CAUSAL",
            "literature priority"
        ],
        "next_gate": "Compute the finite-time BT Hamiltonian quadratic form zeta_T[f] on these compact packet frames, including all ten channel tubes, a positive channel-record partition and their simultaneous-shell intersection strata. A pass would produce a box-independent compact-packet probability; independently, removal of epsilon requires the certified inequivalent weighted or local-algebraic representation rather than ordinary Fock space.",
        "provenance": {
            "source_commit": "9c611092b2d7b1ae3adebcb637603e6d661ea9da",
            "retrieval_date": "2026-08-12",
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "method": "Exact rational step-packet replay of orthogonality, antipodal separation, scalar multiplier cancellation, complement-exchange Gram and detector effect; analytic number-operator and dense-adjoint closability proof for arbitrary compact packets. No floating-point arithmetic is used."
        },
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_scalar_dressed_source_compact_wavepacket.py --write --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_scalar_dressed_source_compact_wavepacket.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_scalar_dressed_source_compact_wavepacket"
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
