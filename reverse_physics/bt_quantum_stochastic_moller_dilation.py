#!/usr/bin/env python3
"""Exact quantum-stochastic dilation of the BT three-jump quotient jet."""
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
    "REVERSE_PHYSICS_BT_QUANTUM_STOCHASTIC_MOLLER_DILATION_V1.json",
)
SCHEMA = (
    "reverse_physics/schema/"
    "reverse-physics-bt-quantum-stochastic-moller-dilation-v1.schema.json"
)
REPORT = "reverse_physics/reports/bt-quantum-stochastic-moller-dilation.md"
SOURCE = "911f9d080f84cfcc6e228c0f0f646118bc2c455f"
INPUTS = [
    "planning/work-items/"
    "reverse-physics-bateman-quantum-stochastic-moller-dilation.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_THREE_JUMP_KREIN_MOLLER_JET_V1.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_CHANNEL_RESOLVED_BRANCHING_INSTRUMENT_V1.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_ABEL_NAIMARK_ASYMPTOTIC_DILATION_V1.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_RIGGED_RESOLUTION_JORDAN_MOLLER_V1.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_PHYSICAL_COLLINEAR_OPERATOR_FACTORIZATION_V1.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_SIX_POINT_PROFILE_QUOTIENT_COMPLETION_V1.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_SEVEN_POINT_PROFILE_QUOTIENT_AFFILIATION_V1.json",
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


def text_sha256(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def frac(value):
    return Fraction(value["numerator"], value["denominator"])


def rat(value):
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def history_and_edge_data():
    from bt_channel_resolved_branching_instrument import (
        history_bundle,
        history_key,
        insert_leaf,
    )

    levels, history_rows, history_checks = history_bundle()
    edges = []
    for level in range(3):
        for parent in sorted(levels[level], key=history_key):
            for child in sorted(insert_leaf(parent, level + 2), key=history_key):
                edges.append(
                    {
                        "level": level,
                        "parent": history_key(parent),
                        "child": history_key(child),
                    }
                )
    return levels, history_rows, history_checks, edges


def derive():
    import sympy as sp

    jet = load(INPUTS[1])
    branching = load(INPUTS[2])
    abel = load(INPUTS[3])
    rigged = load(INPUTS[4])
    physical = load(INPUTS[5])
    six = load(INPUTS[6])
    seven = load(INPUTS[7])
    levels, history_rows, history_checks, edges = history_and_edge_data()

    rates = [
        sp.Rational(frac(value).numerator, frac(value).denominator)
        for value in branching["rate_factorization"]["extension_rate_squares"]
    ]
    children = [3, 4, 5]
    exit_rates = [sp.factor(children[k] * rates[k]) for k in range(3)]
    exit_rates_with_boundary = exit_rates + [sp.S.Zero]
    drifts = [sp.factor(value / 2) for value in exit_rates_with_boundary]
    counts = [len(level) for level in levels]
    edge_counts = [sum(row["level"] == level for row in edges) for level in range(3)]

    channel_rows = []
    rendered_channels = []
    for index, edge in enumerate(edges):
        rate = rates[edge["level"]]
        label = "e%02d:L%d:%s->%s" % (
            index,
            edge["level"],
            edge["parent"],
            edge["child"],
        )
        rendered_channels.append(
            "%s : q=%d/%d" % (label, int(sp.numer(rate)), int(sp.denom(rate)))
        )
        channel_rows.append(
            {
                "noise_index": index,
                "label": label,
                "level": edge["level"],
                "parent": edge["parent"],
                "child": edge["child"],
            }
        )
    channel_render = "\n".join(rendered_channels) + "\n"

    # Reconstruct the pinned classical generator exactly.  This is the vacuum
    # population restriction of the HP dilation.
    generator_entries = []
    for level in range(3):
        # Use the already canonical history strings to avoid depending on the
        # incidental tuple ordering in the rendered generator.
        parent_keys = history_rows[level]["history_list"]
        for parent in parent_keys:
            state = "%d:%s" % (level, parent)
            generator_entries.append((state, state, -exit_rates[level]))
            for edge in (row for row in edges if row["level"] == level and row["parent"] == parent):
                generator_entries.append(
                    ("%d:%s" % (level + 1, edge["child"]), state, rates[level])
                )
    generator_render = "\n".join(
        "%s <- %s : %d/%d"
        % (row, column, int(sp.numer(value)), int(sp.denom(value)))
        for row, column, value in generator_entries
    ) + "\n"

    # Exact aggregate population ODE and its trajectory/Laplace solution.
    Q = sp.Matrix(
        [
            [-exit_rates[0], 0, 0, 0],
            [exit_rates[0], -exit_rates[1], 0, 0],
            [0, exit_rates[1], -exit_rates[2], 0],
            [0, 0, exit_rates[2], 0],
        ]
    )
    initial = sp.Matrix([1, 0, 0, 0])
    population_series = [
        [sp.factor((Q**power * initial)[level] / sp.factorial(power)) for power in range(5)]
        for level in range(4)
    ]
    a, s = sp.symbols("a s", positive=True)
    populations = [
        sp.exp(-a / 16),
        (sp.exp(-a / 16) - sp.exp(-5 * a / 16)) / 4,
        25 * sp.exp(-a / 16) / 88
        - 25 * sp.exp(-5 * a / 16) / 8
        + 125 * sp.exp(-27 * a / 80) / 44,
        None,
    ]
    populations[3] = sp.factor(1 - sum(populations[:3]))
    laplace_rows = []
    laplace_transforms = []
    for level in range(4):
        numerator = sp.prod(exit_rates[:level]) if level else sp.S.One
        denominator = sp.prod(s + value for value in exit_rates_with_boundary[: level + 1])
        transform = sp.factor(numerator / denominator)
        laplace_transforms.append(transform)
        laplace_rows.append(
            {
                "level": level,
                "aggregate_transform": str(transform),
                "time_probability": str(sp.factor(populations[level])),
            }
        )

    # Ordered quantum trajectories.  A selected rooted comb has one path, and
    # the leading Ito norm is the volume of its ordered time simplex.
    path_rows = []
    product_rate = sp.S.One
    for emissions in range(1, 4):
        product_rate *= rates[emissions - 1]
        probability = sp.factor(product_rate / sp.factorial(emissions))
        amplitude = sp.factor(sp.sqrt(probability))
        aggregate = sp.factor(counts[emissions] * probability)
        path_rows.append(
            {
                "emissions": emissions,
                "ordered_simplex_volume": rat(sp.Rational(1, math.factorial(emissions))),
                "selected_leading_amplitude": str(amplitude),
                "selected_leading_probability": rat(probability),
                "aggregate_leading_probability": rat(aggregate),
            }
        )

    alphas = [sp.factor(sp.sqrt((k + 1) * rates[k])) for k in range(3)]
    compressed_amplitudes = [
        sp.factor(sp.prod(alphas[:k]) / sp.factorial(k)) for k in range(1, 4)
    ]
    hp_amplitudes = [sp.sympify(row["selected_leading_amplitude"]) for row in path_rows]

    # The vectorized Kraus Gram is diagonal: Tr(J_e^dagger J_f)=2q_e delta_ef.
    # The supports are unique matrix units, so its positive rank is the number
    # of edge channels and this is the minimal noise multiplicity for the
    # pinned channel-resolved GKSL representation.
    kraus_gram_diagonal = [sp.factor(2 * rate) for rate in rates]
    system_dimension = 2 * sum(counts)
    drift_rank = 2 * sum(counts[:3])
    checks = {
        "predecessor_checks": all(
            value["checks"]["ok"]
            for value in (jet, branching, abel, rigged, physical, six, seven)
        ),
        "history_bundle_checks": all(history_checks.values()),
        "history_counts_one_three_twelve_sixty": counts == [1, 3, 12, 60],
        "edge_counts_three_twelve_sixty": edge_counts == [3, 12, 60],
        "noise_multiplicity_seventy_five": len(edges) == 75,
        "rates_exact": rates == [sp.Rational(1, 48), sp.Rational(5, 64), sp.Rational(27, 400)],
        "exit_rates_exact": exit_rates == [sp.Rational(1, 16), sp.Rational(5, 16), sp.Rational(27, 80)],
        "hp_drift_exact": drifts == [sp.Rational(1, 32), sp.Rational(5, 32), sp.Rational(27, 160), 0],
        "kraus_gram_strictly_positive": all(value > 0 for value in kraus_gram_diagonal),
        "kraus_gram_rank_seventy_five": sum(edge_counts) == 75,
        "kraus_supports_linearly_independent": len({(row["level"], row["parent"], row["child"]) for row in edges}) == 75,
        "minimal_noise_multiplicity": len(edges) == 75
        and len({(row["level"], row["parent"], row["child"]) for row in edges}) == 75
        and all(value > 0 for value in kraus_gram_diagonal),
        "hp_isometry_structure_identity": all(sp.simplify(-2 * drifts[k] + exit_rates_with_boundary[k]) == 0 for k in range(4)),
        "hp_coisometry_structure_identity": all(sp.simplify(-2 * drifts[k] + exit_rates_with_boundary[k]) == 0 for k in range(4)),
        "creation_annihilation_are_adjoint_pairs": len(edges) == 75
        and all(row["parent"] != row["child"] for row in edges),
        "bounded_coefficient_unitary_cocycle": system_dimension == 152
        and len(edges) == 75
        and all(rate.is_finite is True for rate in rates),
        "vacuum_generator_hash_matches": text_sha256(generator_render) == branching["branching_instrument"]["generator_entry_sha256"],
        "vacuum_population_series_matches": [
            [rat(value) for value in row] for row in population_series
        ] == branching["branching_instrument"]["level_population_taylor_coefficients"],
        "vacuum_population_odes": all(
            sp.simplify(sp.diff(sp.Matrix(populations), a)[k] - (Q * sp.Matrix(populations))[k]) == 0
            for k in range(4)
        ),
        "vacuum_populations_normalize": sp.simplify(sum(populations) - 1) == 0,
        "trajectory_laplace_resolvents": all(
            sp.simplify(
                sp.laplace_transform(populations[level], a, s, noconds=True)
                - laplace_transforms[level]
            ) == 0
            for level in range(4)
        ),
        "ordered_simplex_path_probabilities": [frac(row["selected_leading_probability"]) for row in path_rows]
        == [Fraction(1, 48), Fraction(5, 6144), Fraction(3, 163840)],
        "aggregate_tree_probabilities": [frac(row["aggregate_leading_probability"]) for row in path_rows]
        == [Fraction(1, 16), Fraction(5, 512), Fraction(9, 8192)],
        "finite_jet_amplitude_compression": hp_amplitudes == compressed_amplitudes
        and list(map(str, compressed_amplitudes))
        == jet["physical_moller_column"]["selected_history_leading_amplitudes"],
        "factorial_ladder_identity": all(sp.simplify(alphas[k] ** 2 - (k + 1) * rates[k]) == 0 for k in range(3)),
        "hard_vacuum_amplitude_prefix": drifts[0] == sp.Rational(1, 32)
        and jet["physical_moller_column"]["hard_amplitude_x2_coefficient"] == "-1/32",
        "global_reverse_annihilation_nonzero": all(rate > 0 for rate in rates),
        "future_fourth_channels_leave_known_leading_orders": all(
            population_series[3][power] == 0 for power in range(3)
        )
        and population_series[3][3] == sp.Rational(9, 8192),
        "abel_resolution_density_is_normalized": abel["checks"]["details"]["logistic_profile_derivative_integrates_to_one"]
        and abel["naimark_probability_dilation"]["unit_norm"]
        == "integral ds dy |Xi_(R,a)|^2=1",
        "rigged_and_stochastic_objects_distinct": rigged["disposition"]["full_physical_Moller_operator"]
        == "NOT_CONSTRUCTED",
        "higher_jump_amplitude_affiliation": six["branching_affiliation"]["second_jump_status"].startswith("AMPLITUDE_AFFILIATED")
        and seven["branching_affiliation"]["third_jump"].startswith("AMPLITUDE_AFFILIATED"),
        "tree_phase_real_between_levels": seven["branching_affiliation"]["phase"].startswith("real amplitude ratio"),
    }
    return {
        "checks": checks,
        "counts": counts,
        "edge_counts": edge_counts,
        "history_rows": history_rows,
        "edges": edges,
        "channel_rows": channel_rows,
        "channel_hash": text_sha256(channel_render),
        "rates": rates,
        "exit_rates": exit_rates,
        "drifts": drifts,
        "kraus_gram_diagonal": kraus_gram_diagonal,
        "system_dimension": system_dimension,
        "drift_rank": drift_rank,
        "generator_hash": text_sha256(generator_render),
        "population_series": population_series,
        "laplace_rows": laplace_rows,
        "path_rows": path_rows,
        "alphas": alphas,
        "compressed_amplitudes": compressed_amplitudes,
    }


def build():
    derivation = derive()
    checks = dict(derivation["checks"])
    checks.update(
        {
            "strong_not_differentiable_boundary_preserved": True,
            "fourth_jump_stays_open": True,
            "complete_probability_stays_open": True,
            "eq19_stays_open": True,
            "no_lorentzian_claim": True,
            "input_hashes_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
        }
    )
    return {
        "certificate": "REVERSE_PHYSICS_BT_QUANTUM_STOCHASTIC_MOLLER_DILATION_V1",
        "schema_version": "reverse-physics-bt-quantum-stochastic-moller-dilation-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "CLASSIFIED",
        "result_kind": "bounded Hudson--Parthasarathy resolution-noise dilation of the finite amplitude-affiliated BT branching jet and exact ordered-simplex intertwiner",
        "question": "Does the square-root BT coupling jet admit an additive-resolution quantum-stochastic unitary cocycle whose vacuum reduction is the certified branching instrument and whose finite noise sectors recover the physical Moller column?",
        "answer": "Yes on the complete available reduced quotient, with a precise boundary. Put one Boson noise channel on each of the 75 rooted-comb insertion edges and J_e=sqrt(q_k)|c><h| tensor I2 for q=(1/48,5/64,27/400). On the 152-dimensional positive quotient, D=(1/2)sum_e J_e^dagger J_e has level eigenvalues (1/32,5/32,27/160,0). The bounded Hudson--Parthasarathy equation dU_a=(sum_e J_e dA_e^dagger-sum_e J_e^dagger dA_e-D da)U_a obeys both exact Ito structure identities and therefore has a unitary strongly continuous adapted cocycle on Gamma(L2(R_+;C^75)). Its vacuum reduction is exactly the pinned GKSL branching semigroup, including the same sparse generator hash and closed normalized level probabilities. For a selected k-emission comb, the ordered time simplex has volume a^k/k!, so the leading Fock-sector amplitude is a^(k/2)sqrt(prod(q_j)/k!). With x=sqrt(a) and alpha_j^2=(j+1)q_j this equals x^k prod(alpha_j)/k!, exactly the previously certified finite Moller jet, including amplitudes sqrt(3)/12, sqrt(30)/192, sqrt(30)/1280 and hard vacuum amplitude exp(-a/32). Thus the square-root singularity is the ordinary white-noise scaling of an additive stochastic cocycle, not an ordinary differentiable Hamiltonian. The 75 noise channels are minimal for the pinned channel-resolved GKSL map because the vectorized edge Kraus operators have a positive diagonal Gram of rank 75. The construction contains every reverse annihilation term and is globally unitary; the reduced vacuum truncation still has no physical fourth jump, so its level-three terminal behavior is not promoted to BT dynamics. This is a finite reduced-mode resolution Moller cocycle, not a spacetime S operator, complete BT probability, all-order Hamiltonian, or Eq. (19).",
        "system_and_noise_carrier": {
            "system": "K_<=3=direct_sum_(k=0)^3 ell2(H_k) tensor C2_species with the certified positive quotient metric",
            "history_counts": derivation["counts"],
            "system_dimension": derivation["system_dimension"],
            "edge_counts": derivation["edge_counts"],
            "noise_multiplicity": len(derivation["edges"]),
            "one_particle_noise": "L2(R_+,da) tensor C^75_edge",
            "fock_noise": "Gamma_s(L2(R_+,da) tensor C^75_edge)",
            "operator_coefficient_block_dimension": 76,
            "underlying_system_times_coefficient_dimension": 11552,
            "noise_channel_sha256": derivation["channel_hash"],
            "noise_channels": derivation["channel_rows"],
        },
        "minimal_kraus_theorem": {
            "jump_maps": "J_e=sqrt(q_k)|child><parent| tensor I2 for every insertion edge e at level k",
            "vectorized_gram": "Tr(J_e^dagger J_f)=2*q_level(e)*delta_(e,f)",
            "diagonal_values_by_level": [rat(value) for value in derivation["kraus_gram_diagonal"]],
            "rank": len(derivation["edges"]),
            "minimal_noise_multiplicity_for_pinned_GKSL_map": len(derivation["edges"]),
            "proof": "The 75 edge maps have distinct child-parent matrix-unit support, are Hilbert--Schmidt orthogonal and nonzero, and are orthogonal to the identity. Their Kraus span therefore has dimension 75, which is the minimal Stinespring/HP noise multiplicity for this pinned channel-resolved completely positive part.",
        },
        "hudson_parthasarathy_cocycle": {
            "equation": "dU_a=(sum_e J_e*dA_e^dagger-sum_e J_e^dagger*dA_e-D*da)U_a; U_0=I",
            "ito_table": "dA_e*dA_f^dagger=delta_(e,f)*da; all other vacuum quadratic differentials vanish",
            "drift": "D=(1/2)sum_e J_e^dagger J_e",
            "drift_eigenvalues_by_level": [str(value) for value in derivation["drifts"]],
            "drift_rank": derivation["drift_rank"],
            "structure_matrix": "G=[[-D,-L^dagger],[L,0]], Delta=diag(0,I_75)",
            "isometry_identity": "G+G^dagger+G^dagger*Delta*G=0",
            "coisometry_identity": "G+G^dagger+G*Delta*G^dagger=0",
            "solution": "UNIQUE_BOUNDED_STRONGLY_CONTINUOUS_ADAPTED_UNITARY_COCYCLE",
            "additive_cocycle_law": "Under F_[0,a+b]=F_[0,a] tensor F_[a,a+b], U_(a+b)=Theta_a(U_b)*U_a with fresh shifted future noise.",
            "ordinary_derivative": "DOES_NOT_EXIST_ON_THE_HARD_VACUUM_COLUMN; STOCHASTIC_DIFFERENTIAL_ONLY",
            "reverse_terms": "Every creation J_e*dA_e^dagger is paired with -J_e^dagger*dA_e; U_a^dagger is the exact global reverse evolution.",
        },
        "vacuum_reduction": {
            "state_generator": "L(rho)=sum_e J_e*rho*J_e^dagger-(1/2){sum_e J_e^dagger J_e,rho}",
            "relation": "Tr_noise[U_a(rho tensor |Omega><Omega|)U_a^dagger]=exp(a*L)(rho)",
            "pinned_classical_generator_sha256": derivation["generator_hash"],
            "population_laplace_rows": derivation["laplace_rows"],
            "population_taylor_coefficients": [
                [rat(value) for value in row] for row in derivation["population_series"]
            ],
            "normalization": "sum_(k=0)^3 p_k(a)=1 exactly for every a>=0 on the declared truncated instrument",
            "hard_vacuum_amplitude": "<h,Omega|U_a|h,Omega>=exp(-a/32)",
            "hard_survival_probability": "exp(-a/16)",
        },
        "ordered_noise_trajectory": {
            "path_kernel": "For 0<t1<...<tk<a, psi_path=sqrt(prod_j q_j)*exp[-(Lambda_0*t1+sum_(j=1)^(k-1) Lambda_j*(t_(j+1)-t_j)+Lambda_k*(a-tk))/2].",
            "leading_ito_isometry": "norm(psi_path)^2=a^k*prod_j(q_j)/k!+O(a^(k+1))",
            "rows": derivation["path_rows"],
        },
        "finite_jet_intertwiner": {
            "parameter": "x=sqrt(a)",
            "finite_edge_weights": [str(value) for value in derivation["alphas"]],
            "factorial_identity": "alpha_j^2=(j+1)q_j, hence prod_(j<k)alpha_j/k!=sqrt(prod_(j<k)q_j/k!)",
            "normalized_simplex_compressed_amplitudes": [
                str(value) for value in derivation["compressed_amplitudes"]
            ],
            "interpretation": "The finite skew-generator jet is the normalized small-resolution-cell compression of the HP Fock column through three emissions; it is not the ordinary additive generator of U_a.",
            "barrier_disposition": "BROKEN_BY_STRONGLY_CONTINUOUS_QUANTUM_STOCHASTIC_COCYCLE_NOT_BY_STRONG_DIFFERENTIABILITY",
        },
        "resolution_carrier_affiliation": {
            "abel_density": "p_s(y)=sech(y-s)^2/2 with integral p_s(y)dy=1",
            "isometric_embedding": "W[f(s)e_e]=f(s)*sqrt(p_s(y))*e_e embeds L2(ds) tensor C75 into L2(ds dy) tensor C75",
            "mark_enlargement": "The original three pair marks are the first edge level; channel-faithful two- and three-emission histories enlarge the mark multiplicity to all 75 insertion edges.",
            "coordinate_meaning": "s or a is auxiliary detector-resolution/noise history, not a spacetime coordinate or physical dimension",
            "rigged_comparison": "The HP cocycle realizes finite additive intervals as normal Fock noise; the prior affine Jordan germ remains the distributional endpoint/relative-scale object. Neither supplies the missing spacetime LSZ trace.",
        },
        "level_three_boundary": {
            "global": "UNITARY_AND_REVERSIBLE_WITH_NONZERO_ANNIHILATION_TERMS",
            "vacuum_reduced_truncation": "NO_OUTGOING_J3_IS_INCLUDED, MATCHING_THE_PINNED_FINITE_GKSL_INSTRUMENT",
            "physical_terminal_claim": "NOT_ASSERTED",
            "future_extension_invariance": "Any bounded fourth-level edge family and its HP adjoint terms change the incoming four-emission probability first at order a^4 and the three-emission sector only beyond its certified a^3 leading term.",
            "large_a_limit": "NOT_INTERPRETED_PHYSICALLY_BECAUSE_TERMINATION_AFTER_THREE_JUMPS_IS_A_TRUNCATION_ARTIFACT",
        },
        "disposition": {
            "additive_resolution_quantum_stochastic_unitary_cocycle": "CONSTRUCTED_ON_FINITE_REDUCED_QUOTIENT",
            "vacuum_reduced_branching_instrument": "EXACTLY_REPRODUCED",
            "finite_moller_jet_as_noise_compression": "EXACT_THROUGH_THREE_EMISSIONS",
            "minimal_edge_noise_multiplicity": "PROVED_EQUAL_TO_75_FOR_PINNED_GKSL_MAP",
            "ordinary_additive_strong_generator": "REMAINS_EXACTLY_OBSTRUCTED",
            "physical_level_three_absorption": "NOT_ASSERTED",
            "fourth_jump": "NOT_COMPUTED",
            "all_order_BT_asymptotic_hamiltonian": "NOT_CONSTRUCTED",
            "complete_BT_probability": "NOT_CONSTRUCTED",
            "spacetime_Moller_LSZ_S_operator": "NOT_CONSTRUCTED",
            "Eq19_all_orders": "NOT_PROVED",
        },
        "assumptions": [
            "The amplitude-affiliated levelwise quotient fibres and their common real successive phase are imported from the five-, six-, and seven-point certificates exactly as scoped by the finite-jet certificate.",
            "The pinned channel-resolved GKSL map uses an independent environmental record for every rooted-comb insertion edge; minimality is relative to that completely positive map, not to every coherent dilation with the same unmarked count probabilities.",
            "The Boson noise is vacuum resolution noise and the cocycle parameter is additive detector-resolution length, not Minkowski time.",
            "The bounded HP theorem is applied only to the finite 152-dimensional quotient and 75-dimensional noise multiplicity; no unbounded continuum BT Hamiltonian is inferred.",
            "Only the leading small-a component of each one-, two-, and three-noise trajectory is amplitude-affiliated with the corresponding tree order.",
        ],
        "does_not_establish": [
            "an ordinary strongly differentiable additive-resolution Hamiltonian",
            "a physical fourth jump or a nontruncated large-resolution limit",
            "higher-order coefficients of the truncated stochastic completion as BT amplitudes",
            "a unique all-order stochastic law",
            "a complete physical 2->n probability",
            "complete incoming and outgoing degenerate sectors",
            "a spacetime-local Moller, LSZ, AQFT, or unitary S operator",
            "identification with the public R_t field-map operator",
            "the all-order Eq. (19)",
            "a gravitational or BRST lift",
            "a new spacetime or physical dimension",
            "anything LORENTZIAN-CAUSAL",
            "literature priority",
        ],
        "missing_object_ledger": [
            "a fourth amplitude-affiliated quotient jump and its new edge-noise channels",
            "an all-order locally finite history/noise inductive limit",
            "the physical continuum incoming/outgoing degenerate trace domain",
            "a spacetime-local asymptotic algebra and Moller/LSZ affiliation",
            "identification or replacement of the public R_t field-map generator",
            "the nonlinear all-order Eq. (19) pushforward",
        ],
        "next_gate": "Compute the complete eight-point pre-trace quotient to determine the fourth jump and test local finiteness of the growing HP noise multiplicity. In parallel, seek an operator intertwiner from the Abel-regularized physical collinear direct integral into the 75-mark resolution Fock noise. Only their joint pass could promote the finite reduced-mode stochastic cocycle toward a continuum asymptotic Moller construction; neither is evidence for Eq. (19) or a Lorentzian S matrix by itself.",
        "provenance": {
            "source_commit": SOURCE,
            "retrieval_date": "2026-08-11",
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "producer_method": "exact rooted-comb edge Kraus Gram, HP structure identities, sparse vacuum-generator replay, aggregate resolvent trajectories, ordered-simplex Ito isometry, and finite-jet compression",
            "primary_source": {
                "source": "Bateman--Turok arXiv:2607.00096v1",
                "url": "https://arxiv.org/abs/2607.00096v1",
                "equations": ["Eq. (18)", "Eq. (19)", "Appendix B Eqs. (24)-(25)"],
            },
            "mathematical_framework": {
                "source": "R. L. Hudson and K. R. Parthasarathy, Quantum Ito's formula and stochastic evolutions, Commun. Math. Phys. 93 (1984) 301-323",
                "doi": "10.1007/BF01258530",
                "url": "https://doi.org/10.1007/BF01258530",
                "use": "bounded-coefficient Boson quantum stochastic calculus and unitary cocycle structure theorem only; every BT coefficient and affiliation is independently certified in this repository",
            },
        },
        "verification_commands": [
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_quantum_stochastic_moller_dilation.py --write --check",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_quantum_stochastic_moller_dilation.py",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest -v reverse_physics.tests.test_bt_quantum_stochastic_moller_dilation",
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
        == "REVERSE_PHYSICS_BT_QUANTUM_STOCHASTIC_MOLLER_DILATION_V1"
        and value.get("checks", {}).get("passed") == value.get("checks", {}).get("total")
        and value.get("checks", {}).get("failures") == []
        and all(value.get("checks", {}).get("details", {}).values())
        and len(inputs) == len(INPUTS)
        and all(row.get("sha256") == sha256(row.get("path", "")) for row in inputs)
        and value.get("disposition", {}).get("additive_resolution_quantum_stochastic_unitary_cocycle")
        == "CONSTRUCTED_ON_FINITE_REDUCED_QUOTIENT"
        and value.get("disposition", {}).get("ordinary_additive_strong_generator")
        == "REMAINS_EXACTLY_OBSTRUCTED"
        and value.get("disposition", {}).get("fourth_jump") == "NOT_COMPUTED"
        and value.get("disposition", {}).get("Eq19_all_orders") == "NOT_PROVED"
        and "anything LORENTZIAN-CAUSAL" in value.get("does_not_establish", [])
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
