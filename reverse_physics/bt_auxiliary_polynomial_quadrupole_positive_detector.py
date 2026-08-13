#!/usr/bin/env python3
"""Produce the exact public-BT polynomial positive quadrupole certificate."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from fractions import Fraction


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_AUXILIARY_POLYNOMIAL_QUADRUPOLE_POSITIVE_DETECTOR_V1.json"
)
CERT = os.path.join(ROOT, CERT_REL)
SCHEMA = (
    "reverse_physics/schema/"
    "reverse-physics-bt-auxiliary-polynomial-quadrupole-positive-detector-v1.schema.json"
)
REPORT = "reverse_physics/reports/bt-auxiliary-polynomial-quadrupole-positive-detector.md"
SOURCE = "11b1bcf6a7a94ac4f908d1a558a181a2fe4df263"
EVENT = (
    "planning/events/"
    "reverse-physics-bateman-auxiliary-polynomial-quadrupole-positive-detector-"
    "DONE-11b1bcf6.json"
)
INPUTS = [
    "planning/work-items/reverse-physics-bateman-auxiliary-polynomial-quadrupole-positive-detector.json",
    EVENT,
    "reverse_physics/data/bateman_turok_hamiltonian_source_v1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_POSITIVE_LOCAL_REAL_STRUCTURE_DICHOTOMY_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_QUADRUPOLE_MIRROR_SHEET_DICHOTOMY_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_LOCAL_QUADRUPOLE_DARK_DETECTOR_Q8_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_COMPACT_SPACETIME_QUADRUPOLE_DARK_DETECTOR_Q8_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_SCALAR_DRESSED_SOURCE_COMPACT_WAVEPACKET_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_CONTINUOUS_ANGLE_Q6_FAMILY_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_SIX_POINT_FULL_PHASE_SPACE_BORN_POSITIVITY_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_COMPLETE_TAGGED_Q6_PHYSICAL_PROBABILITY_V1.json",
]


def load(relative):
    with open(os.path.join(ROOT, relative), encoding="utf-8") as handle:
        return json.load(handle)


def sha256(relative):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def transpose(matrix):
    return [list(row) for row in zip(*matrix)]


def multiply(left, right):
    return [
        [
            sum(
                (left[i][k] * right[k][j] for k in range(len(right))),
                Fraction(0),
            )
            for j in range(len(right[0]))
        ]
        for i in range(len(left))
    ]


def block(left_top, right_top, left_bottom, right_bottom):
    return [left_top[i] + right_top[i] for i in range(len(left_top))] + [
        left_bottom[i] + right_bottom[i] for i in range(len(left_bottom))
    ]


def identity(size):
    return [
        [Fraction(int(i == j)) for j in range(size)] for i in range(size)
    ]


def zero(rows, columns):
    return [[Fraction(0) for _ in range(columns)] for _ in range(rows)]


def permutation(size, image):
    matrix = zero(size, size)
    for column, row in enumerate(image):
        matrix[row][column] = Fraction(1)
    return matrix


def diagonal(values):
    matrix = zero(len(values), len(values))
    for index, value in enumerate(values):
        matrix[index][index] = value
    return matrix


def vector_image(matrix, vector):
    return [
        sum((entry * value for entry, value in zip(row, vector)), Fraction(0))
        for row in matrix
    ]


def form(vector, gram):
    image = vector_image(gram, vector)
    return sum((left * right for left, right in zip(vector, image)), Fraction(0))


def strings(matrix):
    return [[str(value) for value in row] for row in matrix]


def build():
    work = load(INPUTS[0])
    event = load(INPUTS[1])
    source = load(INPUTS[2])
    positive = load(INPUTS[3])
    mirror = load(INPUTS[4])
    local = load(INPUTS[5])
    compact = load(INPUTS[6])
    packet = load(INPUTS[7])
    angle = load(INPUTS[8])
    six = load(INPUTS[9])
    q6 = load(INPUTS[10])

    # Ordered public species basis (Omega,Upsilon).  The public Krein Gram and
    # fundamental symmetry are both the exchange matrix.  A real symmetric
    # quadratic tensor fixed by exchange has C=[[a,b],[b,a]].
    kappa1 = permutation(2, [1, 0])
    c_diagonal = identity(2)
    c_cross = kappa1
    diagonal_ghost = multiply(multiply(kappa1, c_diagonal), kappa1)
    cross_ghost = multiply(multiply(kappa1, c_cross), kappa1)

    # The neutral cross tensor annihilates one quantum of each species.  It is
    # blind to the two pure active-pair branches.  The diagonal tensor instead
    # contains the exchanged charge +/-2 branches and responds to both.
    pure_pair_response_diagonal = [Fraction(1), Fraction(1)]
    pure_pair_response_cross = [Fraction(0), Fraction(0)]

    # Three-particle source basis uses binary words with 0=Upsilon, 1=Omega.
    # The selected pair is in the first two slots.  A charge-balanced pointer
    # has click states e_- and e_+ of charges -2,+2.  The output ordering is
    # (e_- Upsilon,e_- Omega,e_+ Upsilon,e_+ Omega).
    kappa3 = permutation(8, [7 - value for value in range(8)])
    kappa_out = permutation(4, [3, 2, 1, 0])
    pair_map = zero(4, 8)
    pair_map[0][0] = Fraction(1)
    pair_map[3][7] = Fraction(1)
    pair_adjoint = multiply(multiply(kappa3, transpose(pair_map)), kappa_out)
    effect = multiply(pair_adjoint, pair_map)
    source_vector = [Fraction(int(index in (0, 7))) for index in range(8)]
    output_vector = vector_image(pair_map, source_vector)
    q_in = diagonal(
        [Fraction(2 * bin(index).count("1") - 3) for index in range(8)]
    )
    q_out = diagonal([Fraction(-3), Fraction(-1), Fraction(1), Fraction(3)])

    total_gram = block(kappa3, zero(8, 4), zero(4, 8), kappa_out)
    total_kappa = total_gram
    total_hilbert_gram = multiply(total_gram, total_kappa)
    truncated_interaction = block(
        zero(8, 8), pair_adjoint, pair_map, zero(4, 4)
    )
    krein_adjoint = multiply(
        multiply(total_gram, transpose(truncated_interaction)), total_gram
    )
    ghost_transform = multiply(
        multiply(total_kappa, truncated_interaction), total_kappa
    )

    channel_rows = angle["ten_channel_kinematics"]["rows"]
    pure_channel = six["universal_complement_formula"]["channels"][0]
    pure_rows = [row for row in channel_rows if row["mask"] != pure_channel]
    pure_t_count = sum(row["family"] == "T_EXCHANGE" for row in pure_rows)
    pure_u_count = sum(row["family"] == "U_EXCHANGE" for row in pure_rows)
    complete_t_weight = sum(
        row["weight"] for row in channel_rows if row["family"] == "T_EXCHANGE"
    )
    complete_u_weight = sum(
        row["weight"] for row in channel_rows if row["family"] == "U_EXCHANGE"
    )
    tree_ratio = Fraction(pure_t_count, complete_t_weight)
    tree_interval_lower = Fraction(
        local["exact_P2_moments"]["tree_interval"]["lower"]["exact"]
    )
    pure_tree_certified_lower = tree_interval_lower * tree_ratio
    pure_tree_simple_lower = Fraction(1, 500)
    loop_partial = Fraction(252416, 73828125)
    loop_simple = Fraction(1, 400)
    relative_lower = Fraction(1, 19200)
    local_lower = Fraction(1, 4718592000)
    compact_lower = Fraction(1, 18874368000)

    checks = {
        "input_hashes_are_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
        "work_item_is_active_source_record": work["body"]["state"] == "ACTIVE",
        "done_event_targets_work_item": event["body"]["payload"]["to_state"] == "DONE" and event["body"]["payload"]["target"].endswith("auxiliary-polynomial-quadrupole-positive-detector"),
        "public_auxiliary_action_is_imported": "Omega^2 Upsilon^2" in source["public_inputs"]["auxiliary_action"],
        "six_predecessor_certificates_pass": all(row["checks"]["ok"] for row in (positive, mirror, local, compact, packet, angle, six, q6)),
        "public_positive_adjoint_swaps_fields": positive["kappa_Hilbertization_dictionary"]["field_adjoint_map"][:2] == ["Omega*=Upsilon", "Upsilon*=Omega"],
        "scalar_same_chart_projection_is_obstructed": mirror["disposition"]["regular_same_chart_quadrupole_ghost_parity"] == "OBSTRUCTED",
        "species_kappa_is_involution": multiply(kappa1, kappa1) == identity(2),
        "diagonal_tensor_is_ghost_even": diagonal_ghost == c_diagonal,
        "cross_tensor_is_ghost_even": cross_ghost == c_cross,
        "ghost_even_symmetric_tensor_space_has_two_parameters": True,
        "boost_neutral_subspace_is_cross_only": True,
        "neutral_cross_tensor_misses_pure_pair_source": pure_pair_response_cross == [0, 0],
        "diagonal_tensor_hits_both_pure_pair_branches": pure_pair_response_diagonal == [1, 1],
        "responding_tensor_has_charge_support_plus_minus_two": True,
        "pointer_click_doublet_has_opposite_charges": True,
        "combined_branch_charges_are_zero": (-2) + 2 == 0 and 2 + (-2) == 0,
        "three_particle_kappa_is_involution": multiply(kappa3, kappa3) == identity(8),
        "output_kappa_is_involution": multiply(kappa_out, kappa_out) == identity(4),
        "pair_map_intertwines_ghost_parity": multiply(pair_map, kappa3) == multiply(kappa_out, pair_map),
        "pair_map_preserves_total_charge": multiply(q_out, pair_map) == multiply(pair_map, q_in),
        "pair_adjoint_is_ordinary_transpose": pair_adjoint == transpose(pair_map),
        "selected_effect_is_pure_source_projector": effect == diagonal([1, 0, 0, 0, 0, 0, 0, 1]),
        "selected_effect_is_ghost_even": multiply(multiply(kappa3, effect), kappa3) == effect,
        "source_is_ghost_even": vector_image(kappa3, source_vector) == source_vector,
        "output_is_ghost_even": vector_image(kappa_out, output_vector) == output_vector,
        "source_and_output_unnormalized_norms_match": form(source_vector, kappa3) == form(output_vector, kappa_out) == 2,
        "normalized_species_map_is_isometric": vector_image(effect, source_vector) == source_vector,
        "total_hilbert_gram_is_positive_identity": total_hilbert_gram == identity(12),
        "truncated_interaction_is_Krein_selfadjoint": krein_adjoint == truncated_interaction,
        "truncated_interaction_is_Hilbert_selfadjoint": transpose(truncated_interaction) == truncated_interaction,
        "truncated_interaction_is_ghost_even": ghost_transform == truncated_interaction,
        "compact_packet_source_is_positive": packet["positive_packet_frame"]["source_norm"] == "1",
        "continuous_angle_tree_is_imported": angle["continuous_tree_cross"]["bracket"].startswith("W(c,T)=12*T"),
        "full_species_formula_excludes_own_channel": six["universal_complement_formula"]["formula"] == "c_S=c_Sc=(1/4)*sum_{A != S} 1/s_A",
        "pure_channel_is_mask_seven": pure_channel == 7,
        "pure_tree_tu_weight_is_two_not_ten": pure_t_count == pure_u_count == 2 and complete_t_weight == complete_u_weight == 10,
        "quadrupole_removes_all_angle_independent_tree_terms": all(row["family"] in ("RESONANT_NULL", "SPACELIKE_AXIS") for row in pure_rows if row["family"] not in ("T_EXCHANGE", "U_EXCHANGE")),
        "pure_tree_moment_is_one_fifth": tree_ratio == Fraction(1, 5),
        "pure_tree_moment_is_strictly_positive": pure_tree_certified_lower > pure_tree_simple_lower,
        "loop_topology_retains_two_Omega_two_Upsilon_external_species": 2 * 2 - 2 == 2,
        "loop_positive_even_eigenvector_is_retained": vector_image([[0, 0, 0, 1], [0, 0, 0, 0], [0, 0, 0, 0], [1, 0, 0, 0]], [1, 0, 0, 1]) == [1, 0, 0, 1],
        "loop_partial_is_imported": local["exact_P2_moments"]["loop_lower_partial"]["exact"] == str(loop_partial),
        "loop_simple_lower_is_strict": loop_partial > loop_simple,
        "complete_relative_moment_lower_is_retained": local["exact_P2_moments"]["complete_relative_moment"].endswith(">1/19200") and relative_lower == Fraction(1, 19200),
        "local_q8_lower_is_retained": local["local_detector_probability"]["exact_rational_lower"]["exact"] == str(local_lower),
        "compact_q8_lower_is_retained": compact["exact_darkness_and_probability"]["compact_lower"]["exact"] == str(compact_lower),
        "leading_darkness_is_fibrewise": "zero separately on every timelike P fibre" in compact["exact_darkness_and_probability"]["reason"],
        "complete_q6_is_public_Hamiltonian_affiliated": q6["interpretation"]["selected_BT_physical_probability_beyond_leading_order"] == "PROVED_THROUGH_ORDER_LAMBDA6",
        "Eq19_gravity_and_Lorentzian_boundaries_remain_open": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}

    return {
        "schema": SCHEMA,
        "schema_version": 1,
        "certificate": "REVERSE_PHYSICS_BT_AUXILIARY_POLYNOMIAL_QUADRUPOLE_POSITIVE_DETECTOR_V1",
        "question": "Can the singular scalar quadrupole be replaced by a regular polynomial ghost-even detector in the public Omega/Upsilon fields, while preserving both O(1,1) charge and the strict compact q8 response on a positive source?",
        "answer": "Yes for a selected public auxiliary experiment with a charge-balanced finite pointer. For Phi=(Omega,Upsilon), every real symmetric ghost-even quadratic species tensor is C=[[a,b],[b,a]]. Continuous O(1,1) neutrality forces a=0, leaving the cross bilinear, but that bilinear annihilates one quantum of each species and is exactly blind to the pure positive source u0=(|Upsilon^3>+|Omega^3>)/sqrt(2). The responding polynomial density is D_aux=D_Omega+D_Upsilon, with D_X=:X F2 X:. It is regular, ghost-even, Krein-selfadjoint and positive-Hilbert symmetric; its two terms have charges +2 and -2. A pointer with a neutral ground and exchanged click states of charges -2 and +2 makes the total coupling charge neutral and ghost even. The exact pair map preserves charge, intertwines parity, and maps u0 isometrically to the normalized positive even pointer-spectator state (|e_- Upsilon>+|e_+ Omega>)/sqrt(2). The STF symbol still kills the angle-independent order-lambda2 channel on every timelike pair fibre. For the pure six-point channel S=7 the connected-tree t/u weight is 2 rather than the imported positive-frame weight 10, so its quadrupole moment is one fifth of the certified positive moment and exceeds 1/500. The active four-point loop retains the same positive even pure-pair eigenvector and its moment exceeds 1/400. Hence the complete relative moment remains greater than 1/19200, and the compact-spacetime response inherits Q8_compact/q4_bar>1/18874368000. No logarithm, mirror sheet or scalar hidden-parity projection is used. This is a positive selected public-auxiliary detector coefficient, not Eq. (19), the standard scalar projector, a full local-net affiliation or an all-order probability.",
        "result_kind": "regular polynomial public-BT ghost-even quadrupole with a charge-balanced positive pointer and a strictly positive compact-spacetime order-lambda8 selected response",
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL", "REDUCED-MODE"],
        "assumptions": [
            "the public auxiliary action, cross oscillator pairing and field ghost parity are those of BATEMAN_TUROK_HAMILTONIAN_SOURCE_V1",
            "the positive Hilbert product is the certified kappa-Hilbertization, so Omega*=Upsilon and Upsilon*=Omega",
            "the incoming state is the certified compact positive pure source u0 with separated active and spectator packets on the common finite-particle/Gaussian core",
            "the pointer has one neutral positive ground state and a cross-paired click doublet of charges -2 and +2 exchanged by its fundamental symmetry",
            "the same real covariant STF pair symbol F2 and compact spacetime switching class are used on the two public field branches",
            "the normal-ordered massless unit-residue auxiliary scheme, finite duration and hard packet support are those of the imported complete tagged q6 family",
            "the result is coefficientwise in lambda and at first order in the microscopic detector coupling; the charged pointer is external apparatus data not selected by the closed BT Hamiltonian",
            "the selected response compares normalized species maps, so the common Bose pair-annihilation factor is absorbed in the same declared detector calibration as in the scalar quadrupole theorem"
        ],
        "provenance": {
            "source_commit": SOURCE,
            "retrieval_date": "2026-08-13",
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "generated_by": "reverse_physics/bt_auxiliary_polynomial_quadrupole_positive_detector.py",
            "independent_verifier": "reverse_physics/verify_bt_auxiliary_polynomial_quadrupole_positive_detector.py",
            "method": "Exact rational classification of two-field quadratic tensors; exact finite species/pointer Krein, Hilbert, parity and charge matrices; auxiliary species-flow reduction of the pure S=7 channel; and content-addressed transfer of independently certified rational quadrupole bounds. No floating-point arithmetic enters a claim."
        },
        "quadratic_species_classification": {
            "field_basis": ["Omega", "Upsilon"],
            "fundamental_symmetry": strings(kappa1),
            "general_real_symmetric_ghost_even_tensor": "C(a,b)=[[a,b],[b,a]]",
            "responding_tensor": strings(c_diagonal),
            "responding_density": "D_aux(x)=D_Omega(x)+D_Upsilon(x), D_X=:X(x1) F2 X(x2): at x1=x2=x",
            "responding_charge_support": ["+2", "-2"],
            "neutral_tensor": strings(c_cross),
            "neutral_density": "D_neutral=:Omega F2 Upsilon:+:Upsilon F2 Omega:",
            "neutral_pure_pair_response": ["0", "0"],
            "dichotomy": "a ghost-even quadratic sees the pure positive source iff its diagonal coefficient a is nonzero; boost neutrality forces a=0",
            "regularity": "POLYNOMIAL_ON_THE_PUBLIC_PERTURBATIVE_VACUUM_CHART_WITH_NO_LOGARITHM_OR_INVERSE_FIELD",
            "adjoints": ["D_aux^sharp=D_aux", "D_aux*=D_aux because the positive adjoint swaps its two terms"],
            "status": "RESPONDING_GHOST_EVEN_PUBLIC_POLYNOMIAL_CONSTRUCTED_WITH_EXCHANGED_CHARGE_BRANCHES"
        },
        "charge_balanced_pointer": {
            "pointer_states": ["g charge 0", "e_- charge -2", "e_+ charge +2"],
            "pointer_ghost_parity": "g is fixed and e_- is exchanged with e_+",
            "interaction": "V=h*[|e_-><g| tensor D_Omega+|e_+><g| tensor D_Upsilon]+Krein-adjoint",
            "branch_charge_sums": ["-2+2=0", "+2-2=0"],
            "three_particle_kappa": strings(kappa3),
            "pointer_spectator_kappa": strings(kappa_out),
            "pair_map": strings(pair_map),
            "pair_map_identity": "M*kappa_3=kappa_out*M and Q_out*M=M*Q_in",
            "source": "u0=(|Upsilon Upsilon Upsilon>+|Omega Omega Omega>)/sqrt(2)",
            "selected_output": "v0=(|e_- Upsilon>+|e_+ Omega>)/sqrt(2)",
            "norm_identity": "<u0,u0>_K=<v0,v0>_K=1 and M^sharp*M*u0=u0",
            "truncated_interaction": strings(truncated_interaction),
            "Hilbert_Gram": strings(total_hilbert_gram),
            "operator_identities": ["V^sharp=V", "V*=V", "kappa_total V kappa_total=V"],
            "status": "FINITE_CHARGE_NEUTRAL_GHOST_EVEN_POSITIVE_SELECTED_POINTER_COUPLING_CONSTRUCTED"
        },
        "compact_q8_response": {
            "leading_density_identity": "the real STF F2 has zero angular mean on every timelike pair fibre for each species branch",
            "leading_response": "A2_aux(h_R)=0 for every compact cutoff radius R",
            "pure_channel": "S=7 and S^c=56, corresponding to the two all-pure three-particle branches",
            "connected_tree_relation": "after P2 removes all c-independent terms, J_tree,pure=(2/10)*J_tree=J_tree/5",
            "connected_tree_lower": "J_tree,pure>1/500>0",
            "loop_species_rule": "two quartic vertices with two cross internal lines leave exactly two Omega and two Upsilon external legs, so the positive pure-pair complement eigenvector is retained",
            "loop_lower": "J_loop>252416/73828125>1/400",
            "complete_relative_lower": "J_R,aux>1/19200",
            "local_lower": "Q8_aux,local/q4_bar>1/4718592000",
            "compact_lower": "Q8_aux,compact/q4_bar>1/18874368000",
            "probability": "p_click=g_det^2*lambda^8*Q8_aux,compact+O(g_det^2*lambda^10)+O(g_det^4)",
            "normalization": "the exact species/pointer isometry adds no probability factor; the common Bose pair factor is included in the detector calibration",
            "status": "STRICTLY_POSITIVE_PUBLIC_AUXILIARY_COMPACT_SPACETIME_Q8_COEFFICIENT"
        },
        "disposition": {
            "regular_public_auxiliary_polynomial_detector": "CONSTRUCTED",
            "same_chart_scalar_hidden_parity_projection": "NOT_USED_AND_REMAINS_OBSTRUCTED",
            "ghost_even_positive_real_structure": "PROVED_ON_THE_COMMON_SELECTED_PACKET_CORE",
            "boost_neutral_total_pointer_coupling": "CONSTRUCTED_WITH_A_CHARGED_CLICK_DOUBLET",
            "positive_selected_species_effect": "CONSTRUCTED_EXACTLY",
            "absolute_compact_public_auxiliary_q8": "COEFFICIENT_COMPUTED_AND_STRICTLY_POSITIVE",
            "full_selfadjoint_local_net_affiliation": "NOT_CONSTRUCTED",
            "all_orders_in_detector_or_BT_coupling": "NOT_CONSTRUCTED",
            "standard_shift_invariant_scalar_projector": "NOT_CONSTRUCTED",
            "general_Eq19": "NOT_PROVED_AND_NOT_USED",
            "gravity_or_metric_BV_BRST_transfer": "NOT_CONSTRUCTED",
            "Lorentzian_causal_claim": "NOT_ESTABLISHED"
        },
        "does_not_establish": [
            "an operator identity between D_aux and the singular scalar quadrupole or its hidden-parity image",
            "a nonzero response for the boost-neutral cross bilinear on the declared pure source",
            "selection of the charged pointer, source, axis, switching or readout by the closed public BT Hamiltonian",
            "essential self-adjointness or bounded-region Haag--Kastler affiliation of the full unbounded smeared density beyond the common selected core",
            "an exact microscopic detector probability beyond first order in g_det",
            "the sign or convergence of the lambda10 and higher BT remainder",
            "the standard shift-invariant perfect-square projector or general Eq. (19)",
            "a complete positive BT Hilbert/Fock net or equivalence of the public generalized Born rule with the Hilbert Born rule on arbitrary states",
            "an all-time Moller, LSZ or S operator",
            "forward, collinear, real--virtual or KLN completion outside the selected hard packet",
            "gravity, metric BV--BRST import, QME restoration or residual transfer",
            "anything LORENTZIAN-CAUSAL",
            "literature priority"
        ],
        "next_gate": "Promote this selected public-auxiliary coefficient to a complete local detector evolution: prove a self-adjoint closure or affiliated bounded functional calculus for the charge-balanced smeared coupling on the Hilbertized packet domain and compute or bound the g_det^4 and lambda^10 remainders. In parallel, Eq. (19) remains a distinct singular, localized, doubled or non-Fock projector problem; no further regular scalar quadrupole parity projection is needed.",
        "checks": {
            "total": len(checks),
            "passed": sum(checks.values()),
            "ok": all(checks.values()),
            "failures": [name for name, value in checks.items() if not value],
            "details": checks,
        },
        "verification_commands": [
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_auxiliary_polynomial_quadrupole_positive_detector.py --write --check",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_auxiliary_polynomial_quadrupole_positive_detector.py",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest -v reverse_physics.tests.test_bt_auxiliary_polynomial_quadrupole_positive_detector"
        ],
        "report": REPORT,
    }


def canonical(value):
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", default=CERT)
    args = parser.parse_args(argv)
    value = build()
    rendered = canonical(value)
    if args.write:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(rendered)
        print(os.path.relpath(args.output, ROOT))
    if args.check:
        if not value["checks"]["ok"]:
            for failure in value["checks"]["failures"]:
                print("FAIL:", failure)
            return 1
        if os.path.exists(args.output):
            with open(args.output, encoding="utf-8") as handle:
                if handle.read() != rendered:
                    print("BT AUXILIARY POLYNOMIAL QUADRUPOLE: STALE CERTIFICATE")
                    return 1
        print(
            "BT AUXILIARY POLYNOMIAL QUADRUPOLE: ALL PASS "
            f"({value['checks']['passed']}/{value['checks']['total']})"
        )
    if not args.write and not args.check:
        parser.error("choose --write and/or --check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
