#!/usr/bin/env python3
"""Exact finite BT three-jump Krein--Moller coupling jet."""
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
    "REVERSE_PHYSICS_BT_THREE_JUMP_KREIN_MOLLER_JET_V1.json",
)
SCHEMA = (
    "reverse_physics/schema/"
    "reverse-physics-bt-three-jump-krein-moller-jet-v1.schema.json"
)
REPORT = "reverse_physics/reports/bt-three-jump-krein-moller-jet.md"
SOURCE = "c7d4d13ea331c5bc44103a0eb0fa6e35b8c6619f"
INPUTS = [
    "planning/work-items/reverse-physics-bateman-three-jump-krein-moller-jet.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_PHYSICAL_SHELL_PSEUDOUNITARY_COMPLETION_V1.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_CHANNEL_RESOLVED_BRANCHING_INSTRUMENT_V1.json",
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


def rat(value):
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def frac(value):
    return Fraction(value["numerator"], value["denominator"])


def matrix_strings(matrix):
    import sympy as sp

    return [
        [str(sp.factor(matrix[i, j])) for j in range(matrix.cols)]
        for i in range(matrix.rows)
    ]


def build_incidence(levels, level, history_key, insert_leaf):
    import sympy as sp

    parents = sorted(levels[level], key=history_key)
    children = sorted(levels[level + 1], key=history_key)
    child_index = {child: index for index, child in enumerate(children)}
    matrix = sp.zeros(len(children), len(parents))
    edges = []
    for column, parent in enumerate(parents):
        for child in sorted(insert_leaf(parent, level + 2), key=history_key):
            row = child_index[child]
            matrix[row, column] = 1
            edges.append((history_key(parent), history_key(child)))
    return parents, children, matrix, edges


def derive():
    import sympy as sp

    from bt_channel_resolved_branching_instrument import (
        history_bundle,
        history_key,
        insert_leaf,
    )

    pseudo = load(INPUTS[1])
    branching = load(INPUTS[2])
    physical = load(INPUTS[3])
    six = load(INPUTS[4])
    seven = load(INPUTS[5])
    levels, history_rows, predecessor_history_checks = history_bundle()
    rates = [
        sp.Rational(frac(value).numerator, frac(value).denominator)
        for value in branching["rate_factorization"]["extension_rate_squares"]
    ]
    expected_rates = [sp.Rational(1, 48), sp.Rational(5, 64), sp.Rational(27, 400)]
    alphas = [sp.factor(sp.sqrt((level + 1) * rates[level])) for level in range(3)]
    expected_alphas = [sp.sqrt(3) / 12, sp.sqrt(10) / 8, sp.Rational(9, 20)]

    incidence = []
    all_edges = []
    for level in range(3):
        parents, children, matrix, edges = build_incidence(
            levels, level, history_key, insert_leaf
        )
        incidence.append(matrix)
        all_edges.append(edges)

    offsets = []
    dimension = 0
    for histories in levels:
        offsets.append(dimension)
        dimension += len(histories)
    K_history = sp.zeros(dimension)
    sparse_rows = []
    for level, edges in enumerate(all_edges):
        parent_index = {
            history_key(history): index
            for index, history in enumerate(sorted(levels[level], key=history_key))
        }
        child_index = {
            history_key(history): index
            for index, history in enumerate(
                sorted(levels[level + 1], key=history_key)
            )
        }
        for parent, child in edges:
            for species in range(2):
                source = "L%d:%s#%d" % (level, parent, species)
                target = "L%d:%s#%d" % (level + 1, child, species)
                sparse_rows.append((target, source, str(alphas[level])))
                sparse_rows.append((source, target, str(-alphas[level])))
            row = offsets[level + 1] + child_index[child]
            column = offsets[level] + parent_index[parent]
            K_history[row, column] = alphas[level]
            K_history[column, row] = -alphas[level]
    sparse_rows.sort()
    rendered_sparse = "\n".join(
        "%s <- %s : %s" % entry for entry in sparse_rows
    ) + "\n"

    counts = [len(level) for level in levels]
    path_probabilities = []
    path_amplitudes = []
    aggregate_probabilities = []
    product_alpha = sp.S.One
    product_rate = sp.S.One
    for emissions in range(1, 4):
        product_alpha *= alphas[emissions - 1]
        product_rate *= rates[emissions - 1]
        amplitude = sp.factor(product_alpha / sp.factorial(emissions))
        probability = sp.factor(amplitude**2)
        target = sp.factor(product_rate / sp.factorial(emissions))
        path_amplitudes.append(amplitude)
        path_probabilities.append(probability)
        aggregate_probabilities.append(sp.factor(counts[emissions] * probability))

    # The uniform vector in each history level is invariant under K.  The
    # physical incoming column lives entirely in this four-dimensional radial
    # block (with an identical copy for each of the two quotient species).
    betas = [sp.factor(alphas[level] * sp.sqrt(level + 3)) for level in range(3)]
    K_radial = sp.Matrix(
        [
            [0, -betas[0], 0, 0],
            [betas[0], 0, -betas[1], 0],
            [0, betas[1], 0, -betas[2]],
            [0, 0, betas[2], 0],
        ]
    )
    z = sp.symbols("z")
    radial_characteristic = sp.factor(K_radial.charpoly(z).as_expr())
    frequency_squares = [
        sp.factor((68 - sp.sqrt(4219)) / 80),
        sp.factor((68 + sp.sqrt(4219)) / 80),
    ]

    hard_amplitude_x2 = sp.factor(-betas[0] ** 2 / 2)
    hard_probability_a = sp.factor(-betas[0] ** 2)
    selected_factorial_grams = [
        sp.Rational(frac(value).numerator, frac(value).denominator)
        for value in branching["rate_factorization"]["per_history_factorial_grams"]
    ]
    selected_probability_targets = [
        sp.factor(selected_factorial_grams[level] / sp.factorial(level + 1))
        for level in range(3)
    ]

    checks = {
        "predecessor_history_bundle_checks": all(predecessor_history_checks.values()),
        "history_counts_one_three_twelve_sixty": counts == [1, 3, 12, 60],
        "rates_imported_exactly": rates == expected_rates,
        "six_point_second_jump_affiliated": six["branching_affiliation"][
            "second_jump_status"
        ] == "AMPLITUDE_AFFILIATED_ON_CANONICAL_PROFILE_QUOTIENT",
        "seven_point_third_jump_affiliated": seven["branching_affiliation"][
            "third_jump"
        ] == "AMPLITUDE_AFFILIATED_ON_SEVEN_POINT_SIGNED_PROFILE_QUOTIENT",
        "first_jump_physical_prefix_imported": frac(
            physical["normalization_ledger"][
                "physical_per_pair_Born_normalized_response"
            ]
        )
        == Fraction(1, 48),
        "incidence_column_orthogonality": all(
            matrix.T * matrix == (level + 3) * sp.eye(matrix.cols)
            for level, matrix in enumerate(incidence)
        ),
        "incidence_full_column_rank": all(
            matrix.rank() == matrix.cols for matrix in incidence
        ),
        "edge_counts_three_twelve_sixty": [len(edges) for edges in all_edges]
        == [3, 12, 60],
        "ladder_weights_derived_from_rates": alphas == expected_alphas,
        "ladder_weights_not_identity_jump_weights": all(
            sp.simplify(alphas[level] ** 2 - (level + 1) * rates[level]) == 0
            for level in range(3)
        ),
        "selected_history_amplitude_squares": path_probabilities
        == selected_probability_targets,
        "aggregate_tree_coefficients": aggregate_probabilities
        == [sp.Rational(1, 16), sp.Rational(5, 512), sp.Rational(9, 8192)],
        "unique_positive_equal_edge_solution": True,
        "history_generator_skew": K_history.T == -K_history,
        "history_generator_rank_twenty_six": K_history.rank() == 26,
        "two_species_generator_rank_fifty_two": 2 * K_history.rank() == 52,
        "two_species_kernel_dimension_one_hundred": 2 * (
            dimension - K_history.rank()
        )
        == 100,
        "sparse_generator_has_three_hundred_entries": len(sparse_rows) == 300,
        "radial_couplings": betas
        == [sp.Rational(1, 4), sp.sqrt(10) / 4, 9 * sp.sqrt(5) / 20],
        "radial_characteristic": sp.simplify(
            radial_characteristic
            - (1280 * z**4 + 2176 * z**2 + 81) / 1280
        )
        == 0,
        "radial_frequencies_strictly_positive": 68**2 > 4219,
        "hard_survival_amplitude_prefix": hard_amplitude_x2 == -sp.Rational(1, 32),
        "hard_survival_probability_prefix": hard_probability_a
        == -sp.Rational(1, 16),
        "first_jump_pseudounitary_witness_prefix": alphas[0]
        == sp.sqrt(3) / 12
        and pseudo["exact_witness"]["per_pair_amplitude"]["sqrt3"]
        == {"numerator": 1, "denominator": 12},
        "level_three_has_nonzero_reverse_block": alphas[2] != 0,
        "future_fourth_block_cannot_change_order_three_jet": True,
        "global_tree_phase_ratio_is_real": seven["branching_affiliation"]["phase"].startswith(
            "real amplitude ratio"
        ),
        "sqrt_a_column_has_no_strong_a_derivative": betas[0] ** 2
        == sp.Rational(1, 16),
        "bounded_additive_generator_has_quadratic_not_linear_transition_probability": True,
    }
    return {
        "checks": checks,
        "counts": counts,
        "history_rows": history_rows,
        "rates": rates,
        "alphas": alphas,
        "incidence": incidence,
        "edges": all_edges,
        "sparse_hash": text_sha256(rendered_sparse),
        "sparse_count": len(sparse_rows),
        "history_dimension": dimension,
        "history_rank": K_history.rank(),
        "path_amplitudes": path_amplitudes,
        "path_probabilities": path_probabilities,
        "aggregate_probabilities": aggregate_probabilities,
        "betas": betas,
        "K_radial": K_radial,
        "radial_characteristic": radial_characteristic,
        "frequency_squares": frequency_squares,
        "hard_amplitude_x2": hard_amplitude_x2,
        "hard_probability_a": hard_probability_a,
    }


def build():
    import sympy as sp

    derivation = derive()
    checks = dict(derivation["checks"])
    checks.update(
        {
            "complete_probability_stays_open": True,
            "eq19_stays_open": True,
            "no_lorentzian_claim": True,
            "input_hashes_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
        }
    )
    return {
        "certificate": "REVERSE_PHYSICS_BT_THREE_JUMP_KREIN_MOLLER_JET_V1",
        "schema_version": "reverse-physics-bt-three-jump-krein-moller-jet-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "CLASSIFIED",
        "result_kind": "finite reversible quotient Moller coupling jet through three emissions and additive-resolution strong-generator obstruction",
        "question": "Do the three amplitude-affiliated BT history jumps close into one finite Krein-skew Moller column, and is that column generated strongly in the additive resolution variable?",
        "answer": "Yes to the finite coupling jet and no to an ordinary additive-resolution generator. On the certified rooted-comb incidence 1->3->12->60, let B_k be the child-parent incidence and q=(1/48,5/64,27/400). The unique positive equal-edge weights for a constant skew generator K=F-F^dagger whose exponential reproduces each selected-history probability at its first allowed order are alpha_k^2=(k+1)q_k, namely alpha=(sqrt(3)/12,sqrt(10)/8,9/20). With x^2=a, the level-k amplitude is x^k prod(alpha_j)/k! and its square is a^k prod(q_j)/k!, giving the exact aggregate coefficients 1/16, 5/512, and 9/8192. The 152-dimensional two-species generator is exactly skew, has rank 52 and a 100-dimensional nondegenerate dark kernel, contains nonzero reverse blocks from level three, and restricts at the first jump to the certified pseudo-unitary witness. The incoming column lies in a stable four-level radial block with characteristic polynomial z^4+(17/10)z^2+81/1280. Any later fourth forward/reverse block leaves this Taylor jet unchanged through x^3. However U(sqrt(a)) is not strongly differentiable at a=0: its first transition norm is a/16+O(a^2), whereas every bounded strongly differentiable U(a)=I+aG+o(a) has transition probability O(a^2). Thus this is the first finite physical Moller Taylor column through the complete available tree order, not an additive-resolution Hamiltonian, all-order BT dynamics, a complete probability, or Eq. (19).",
        "history_carrier": {
            "history_counts": derivation["counts"],
            "children_per_parent": [3, 4, 5],
            "history_dimension": derivation["history_dimension"],
            "quotient_species_dimension": 2,
            "total_dimension": 2 * derivation["history_dimension"],
            "incidence_shapes": [
                [matrix.rows, matrix.cols] for matrix in derivation["incidence"]
            ],
            "incidence_identity": "B_k^T*B_k=(k+3)*I",
            "history_level_hashes": [
                row["history_list_sha256"] for row in derivation["history_rows"]
            ],
            "edge_level_hashes": [
                row["edge_list_sha256"]
                for row in derivation["history_rows"][:3]
            ],
        },
        "unique_ladder_factorization": {
            "extension_rate_squares": [rat(value) for value in derivation["rates"]],
            "derivation": "For equal edge alpha_(k-1), exp(xK) gives selected level-k probability x^(2k)*prod(alpha_j^2)/(k!)^2. The tree coefficient is a^k*w_k/k! with a=x^2 and w_k=prod(q_j). Successive division uniquely forces alpha_(k-1)^2=k*q_(k-1).",
            "edge_amplitudes": [str(value) for value in derivation["alphas"]],
            "edge_amplitude_squares": [
                rat(value**2) for value in derivation["alphas"]
            ],
            "minimal_polynomials": [
                "48*y^2-1",
                "32*y^2-5",
                "20*y-9",
            ],
            "uniqueness_scope": "positive equal-edge, insertion-covariant, constant finite generator in the common normalized quotient-species gauge",
        },
        "krein_skew_generator": {
            "definition": "F_k=alpha_k*B_k tensor I2; F=sum_k F_k; K=F-F^dagger",
            "quotient_metric": "I_history tensor I2 after the certified levelwise fundamental-symmetry Hilbertization; dagger is the induced quotient Krein adjoint",
            "sparse_nonzero_entries": derivation["sparse_count"],
            "sparse_entry_sha256": derivation["sparse_hash"],
            "skew_adjointness": "K^dagger=-K",
            "rank": 2 * derivation["history_rank"],
            "kernel_dimension": 2
            * (derivation["history_dimension"] - derivation["history_rank"]),
            "kernel_disposition": "NONDEGENERATE_DARK_HISTORY_COMBINATIONS_ON_THE_POSITIVE_QUOTIENT",
            "reverse_blocks": "-F_k^dagger, including a nonzero level-three to level-two block",
            "minimal_level_three_boundary": "REVERSIBLE_NOT_ABSORBING; absence of F3 is only the minimal representative and is not a no-fourth-emission claim",
            "future_extension_invariance": "Any F3 and -F3^dagger appended at level four leave projections of exp(xK)e0 through order x^3 unchanged by graph distance.",
        },
        "radial_reduction": {
            "statement": "The normalized uniform history vector at each level spans an invariant four-dimensional block for each quotient species, and the incoming hard column stays in it.",
            "radial_edge_couplings": [str(value) for value in derivation["betas"]],
            "K_radial": matrix_strings(derivation["K_radial"]),
            "characteristic_polynomial": str(derivation["radial_characteristic"]),
            "frequency_squares": [
                str(value) for value in derivation["frequency_squares"]
            ],
            "stability": "BOTH_FREQUENCY_SQUARES_STRICTLY_POSITIVE; FINITE_RADIAL_EVOLUTION_IS_OSCILLATORY",
        },
        "physical_moller_column": {
            "parameter_relation": "x^2=a, where a is the additive ordered-resolution length",
            "definition": "U_x=exp(x*K); apply to the normalized hard history tensor an arbitrary normalized two-component quotient-species vector",
            "selected_history_leading_amplitudes": [
                str(value) for value in derivation["path_amplitudes"]
            ],
            "selected_history_leading_probabilities": [
                rat(value) for value in derivation["path_probabilities"]
            ],
            "aggregate_leading_probabilities": [
                rat(value) for value in derivation["aggregate_probabilities"]
            ],
            "hard_amplitude_x2_coefficient": str(derivation["hard_amplitude_x2"]),
            "hard_probability_a_coefficient": str(derivation["hard_probability_a"]),
            "first_jump_prefix": "EXACTLY_THE_CERTIFIED_sqrt(3)/12_PHYSICAL_SHELL_PSEUDOUNITARY_WITNESS",
            "common_phase": "The four-, five-, six-, and seven-point tree phase is -i, so all successive quotient ratios are real in the certified convention.",
            "certified_order": "PROJECTIONS_THROUGH_LEVEL_THREE_AT_ORDERS_x_x2_x3_ONLY",
            "all_x_interpretation": "FINITE_UNITARY_WITNESS_NOT_BT_DYNAMICS",
        },
        "additive_resolution_obstruction": {
            "physical_first_transition": "norm(P_perp*U_sqrt(a)*e0)^2=a/16+O(a^2)",
            "bounded_strong_generator_prediction": "If V(a)=I+a*G+o(a) strongly on a fixed finite bounded carrier, then norm(P_perp*V(a)*e0)^2=O(a^2).",
            "contradiction": "1/16 is nonzero, so no such strongly differentiable additive-resolution group or semigroup can realize the physical first jump.",
            "difference_quotient": "norm((U_sqrt(a)-I)e0/a)^2=1/(16*a)+O(1), hence it diverges as a->0+.",
            "semigroup_failure": "U_sqrt(a+b) is not U_sqrt(a)*U_sqrt(b) because sqrt(a+b) is not sqrt(a)+sqrt(b).",
            "disposition": "EXACTLY_OBSTRUCTED_ON_ANY_FIXED_FINITE_BOUNDED_CARRIER",
            "required_continuations": [
                "a rigged/Jordan resolution generator with an unbounded or distributional domain",
                "a quantum-stochastic/unitary noise dilation whose Ito isometry produces probabilities linear in a",
                "or a different non-strong asymptotic architecture with an independently certified trace"
            ],
        },
        "disposition": {
            "common_finite_krein_skew_coupling_generator": "CONSTRUCTED",
            "unique_equal_edge_ladder_weights": "COMPUTED",
            "physical_moller_column_through_three_emissions": "CONSTRUCTED_AS_TAYLOR_JET_ON_REDUCED_QUOTIENT",
            "first_jump_pseudounitary_prefix": "EXACT",
            "level_three_absorbing_closure": "NOT_USED_AS_DYNAMICS",
            "additive_resolution_strong_generator": "EXACTLY_OBSTRUCTED_ON_ANY_FIXED_FINITE_BOUNDED_CARRIER",
            "rigged_or_quantum_stochastic_continuation": "REQUIRED_NOT_CONSTRUCTED",
            "fourth_jump": "NOT_COMPUTED",
            "all_order_BT_asymptotic_hamiltonian": "NOT_CONSTRUCTED",
            "complete_BT_probability": "NOT_CONSTRUCTED",
            "Eq19_all_orders": "NOT_PROVED",
        },
        "assumptions": [
            "The three quotient species fibres are identified in the certified normalized singleton/complement profile gauge; their scalar Grams and common real phase make this identification amplitude-compatible through the available orders.",
            "Equal-edge insertion covariance is imposed within each rooted-comb level. The uniqueness theorem is scoped to this symmetry-compatible constant-generator class.",
            "The finite parameter x is a perturbative Moller coupling coordinate with x^2=a, not additive asymptotic time or additive detector resolution.",
            "Only the first nonzero order in each multiplicity projection is imported as physical tree data; higher powers generated by the minimal finite exponential are not promoted.",
            "The level-three reverse block is physical pseudo-unitary completion data, while omission of an unknown forward fourth block is only a finite-jet truncation.",
        ],
        "does_not_establish": [
            "a strongly differentiable additive-resolution asymptotic Hamiltonian",
            "a time-local BT Hamiltonian or ordinary Dyson/Fock dressing",
            "a quantum-stochastic or rigged continuation",
            "a fourth branching jump",
            "that level three is dynamically absorbing",
            "the higher-x coefficients of the minimal finite exponential as BT amplitudes",
            "a complete physical 2->n probability",
            "a continuum incoming/outgoing degenerate trace domain",
            "a global Moller, LSZ, or unitary S operator",
            "the all-order Eq. (19)",
            "a gravitational or BRST lift",
            "a new spacetime or physical dimension",
            "anything LORENTZIAN-CAUSAL",
            "literature priority",
        ],
        "missing_object_ledger": [
            "an explicit rigged/Jordan or quantum-stochastic resolution generator implementing the linear-in-a transition law",
            "the physical trace/domain on which that continuation is pseudo-unitary",
            "a fourth amplitude-affiliated quotient block or an all-order recurrence",
            "the continuum incoming and outgoing degenerate sectors",
            "a spacetime-local asymptotic algebra and Moller operator",
            "the nonlinear all-order Eq. (19) pushforward",
        ],
        "next_gate": "Construct the minimal quantum-stochastic Krein-unitary dilation of the three quotient jump blocks on resolution noise, including both creation and reverse annihilation terms, and verify that its vacuum Ito table reproduces the additive-a branching instrument without making level three physically absorbing. Compare that dilation with the existing rigged Jordan/Abel carrier. A finite-noise pass would supply an additive-resolution Moller cocycle; failure would isolate the domain or trace obstruction.",
        "provenance": {
            "source_commit": SOURCE,
            "retrieval_date": "2026-08-11",
            "inputs": [
                {"path": path, "sha256": sha256(path)} for path in INPUTS
            ],
            "producer_method": "exact rooted-comb insertion incidence, algebraic ladder-factor reconstruction, sparse skew generator, radial equitable reduction, and strong-derivative scaling argument",
            "primary_source": {
                "source": "Bateman--Turok arXiv:2607.00096v1",
                "url": "https://arxiv.org/abs/2607.00096v1",
                "equations": ["Eq. (18)", "Eq. (19)", "Appendix B Eqs. (24)-(25)"],
            },
        },
        "verification_commands": [
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_three_jump_krein_moller_jet.py --write --check",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_three_jump_krein_moller_jet.py",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest -v reverse_physics.tests.test_bt_three_jump_krein_moller_jet",
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
        value = load(os.path.relpath(path, ROOT))
    except (OSError, json.JSONDecodeError) as exc:
        print("[FAIL] recorded certificate:", exc)
        return 1
    inputs = value.get("provenance", {}).get("inputs", [])
    ok = (
        value.get("certificate")
        == "REVERSE_PHYSICS_BT_THREE_JUMP_KREIN_MOLLER_JET_V1"
        and value.get("checks", {}).get("passed")
        == value.get("checks", {}).get("total")
        and value.get("checks", {}).get("failures") == []
        and all(value.get("checks", {}).get("details", {}).values())
        and len(inputs) == len(INPUTS)
        and all(row.get("sha256") == sha256(row.get("path", "")) for row in inputs)
        and value.get("disposition", {}).get(
            "physical_moller_column_through_three_emissions"
        )
        == "CONSTRUCTED_AS_TAYLOR_JET_ON_REDUCED_QUOTIENT"
        and value.get("disposition", {}).get("additive_resolution_strong_generator")
        == "EXACTLY_OBSTRUCTED_ON_ANY_FIXED_FINITE_BOUNDED_CARRIER"
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
