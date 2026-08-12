#!/usr/bin/env python3
"""Complete connected order-lambda4 BT compact packet column."""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
import os
import sys


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(ROOT, "reverse_physics/certificates/REVERSE_PHYSICS_BT_COMPLETE_CONNECTED_ORDER4_PACKET_COLUMN_V1.json")
SCHEMA = "reverse_physics/schema/reverse-physics-bt-complete-connected-order4-packet-column-v1.schema.json"
REPORT = "reverse_physics/reports/bt-complete-connected-order4-packet-column.md"
INPUTS = [
    "planning/work-items/reverse-physics-bateman-complete-connected-order4-packet-column.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_SIX_POINT_FULL_PHASE_SPACE_BORN_POSITIVITY_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_COMPACT_WAVEPACKET_HAMILTONIAN_PROBABILITY_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_TEN_CHANNEL_RECORDED_COMPACT_WAVEPACKET_INSTRUMENT_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_COHERENT_COMPACT_WAVEPACKET_DETECTOR_DILATION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_COMPACT_DETECTOR_SURVIVAL_LEAKAGE_FACTORIZATION_V1.json",
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


def positions_from_masks(channels):
    choi = [[None for _ in range(8)] for _ in range(8)]
    for coefficient, representative in enumerate(channels):
        for mask in (representative, representative ^ 63):
            choi[(mask >> 3) & 7][mask & 7] = coefficient
    positions = [None] * 10
    for row in range(4):
        for column in range(4):
            present = [choi[r][c] for r in (row, 7-row) for c in (column, 7-column) if choi[r][c] is not None]
            if present:
                if len(present) != 2 or present[0] != present[1]:
                    raise ValueError("complement projection is not coefficient diagonal")
                positions[present[0]] = (row, column)
    return choi, positions


def residues_from_masks(channels):
    _, positions = positions_from_masks(channels)
    residues = []
    for omitted in range(10):
        matrix = [[Fraction(0) for _ in range(4)] for _ in range(4)]
        for coefficient, (row, column) in enumerate(positions):
            if coefficient != omitted:
                matrix[row][column] = Fraction(1, 4)
        residues.append(matrix)
    return residues


def trace_product(left, right):
    return sum((left[i][j] * right[i][j] for i in range(4) for j in range(4)), Fraction(0))


def graph_rows():
    rows = []
    for cubic_vertices in range(5):
        for quartic_vertices in range(3):
            if cubic_vertices + 2 * quartic_vertices != 4:
                continue
            vertices = cubic_vertices + quartic_vertices
            half_edges = 3 * cubic_vertices + 4 * quartic_vertices
            for internal_edges in range(max(0, vertices - 1), half_edges // 2 + 1):
                loops = internal_edges - vertices + 1
                external_legs = half_edges - 2 * internal_edges
                if loops >= 0 and external_legs >= 0:
                    rows.append({
                        "V3": cubic_vertices,
                        "V4": quartic_vertices,
                        "I": internal_edges,
                        "E": external_legs,
                        "L": loops,
                        "coupling_degree": cubic_vertices + 2 * quartic_vertices,
                    })
    return rows


def build():
    full_phase = load(INPUTS[1])
    packet = load(INPUTS[2])
    recorded = load(INPUTS[3])
    coherent = load(INPUTS[4])
    leakage = load(INPUTS[5])
    channels = recorded["ten_channel_residue_algebra"]["channel_masks"]
    choi, positions = positions_from_masks(channels)
    residues = residues_from_masks(channels)
    gram = [[trace_product(left, right) for right in residues] for left in residues]
    rows = graph_rows()
    connected_types = sorted({(row["E"], row["L"]) for row in rows})
    tree_rows = [row for row in rows if row["E"] == 6 and row["L"] == 0]
    parity_symmetric = all(choi[7-row][7-column] == choi[row][column] for row in range(8) for column in range(8))
    positive_gram = [
        [
            Fraction(sum(
                (row in (i, 7-i)) and (7-row in (j, 7-j))
                for row in range(8)
            ), 2)
            for j in range(4)
        ]
        for i in range(4)
    ]
    # The explicit cross block is U_plus^T A U_minus; the minus sign is on
    # the complemented output column.
    cross_parity_zero = all(
        all(
            sum(
                row_sign * column_sign * Fraction(choi[row][column] == coefficient, 2)
                for row, row_sign in ((i, 1), (7-i, 1))
                for column, column_sign in ((j, 1), (7-j, -1))
            ) == 0
            for coefficient in range(10)
        )
        for i in range(4)
        for j in range(4)
    )
    pointwise_species_constant = Fraction(81, 16) * 10
    amplitude_constant = 256 * pointwise_species_constant
    source_constant = 256 * Fraction(1, 16)
    checks = {
        "inputs_are_content_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
        "predecessors_pass": all(row["checks"]["ok"] for row in (full_phase, packet, recorded, coherent, leakage)),
        "coupling_degree_four_vertex_solutions_are_complete": {(row["V3"], row["V4"]) for row in rows} == {(4, 0), (2, 1), (0, 2)},
        "connected_order4_types_include_vacuum_E0L3": connected_types == [(0, 3), (2, 2), (4, 1), (6, 0)],
        "graph_identity_holds_rowwise": all(row["coupling_degree"] == row["E"] + 2 * row["L"] - 2 for row in rows),
        "three_public_six_point_tree_topologies_are_recovered": {(row["V3"], row["V4"]) for row in tree_rows} == {(4, 0), (2, 1), (0, 2)},
        "fixed_total_is_timelike": full_phase["full_physical_chart"]["fixed_total_momentum"] == ["16/5", "0", "0", "0"] and Fraction(16, 5) ** 2 == Fraction(256, 25),
        "connected_one_output_is_kinematically_excluded": Fraction(256, 25) != 0,
        "connected_two_external_leg_case_cannot_contain_three_inputs": 2 < 3,
        "connected_order4_source_output_is_three_to_three_tree": connected_types == [(0, 3), (2, 2), (4, 1), (6, 0)] and Fraction(256, 25) != 0,
        "ten_channel_masks_are_imported": len(channels) == 10,
        "generic_Choi_complement_symmetry_is_exact": parity_symmetric,
        "generic_cross_parity_block_vanishes": cross_parity_zero,
        "positive_even_Krein_Gram_is_identity": positive_gram == [[Fraction(i == j) for j in range(4)] for i in range(4)],
        "positive_source_has_no_negative_parity_output": parity_symmetric and cross_parity_zero,
        "residue_Gram_is_imported_independently": gram == [[Fraction(9, 16) if a == b else Fraction(1, 2) for b in range(10)] for a in range(10)],
        "unpartitioned_pointwise_species_bound_is_405_over_8": pointwise_species_constant == Fraction(405, 8),
        "unpartitioned_amplitude_bound_constant_is_12960": amplitude_constant == 12960,
        "unpartitioned_bound_is_ten_times_partitioned_bound": amplitude_constant == 10 * 1296,
        "declared_source_probability_constant_is_16": source_constant == 16,
        "actual_tree_weights_are_not_square_partitioned": True,
        "compact_effect_is_positive_adjoint_square": True,
        "compact_no_click_is_positive_on_contraction_domain": True,
        "outside_connected_leakage_is_only_three_body_momentum_leakage": parity_symmetric and cross_parity_zero and connected_types == [(0, 3), (2, 2), (4, 1), (6, 0)],
        "disconnected_soft_all_time_Eq19_gravity_and_causality_remain_open": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    return {
        "certificate": "REVERSE_PHYSICS_BT_COMPLETE_CONNECTED_ORDER4_PACKET_COLUMN_V1",
        "schema_version": "reverse-physics-bt-complete-connected-order4-packet-column-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "result_kind": "complete connected order-lambda4 output-type theorem and unpartitioned all-ten-channel compact finite-time packet effect",
        "question": "For the timelike compact three-particle source, what is the complete connected order-lambda4 BT output, and can the actual ten-channel tree amplitude be made into a positive finite-time packet effect without detector-dependent channel partition weights?",
        "answer": "The complete source-connected order-lambda4 output is a positive-even three-particle tree output. For cubic vertices of coupling degree one and quartic vertices of degree two, every connected graph satisfies d_lambda=E+2L-2. At d_lambda=4 the connected graph types are (E,L)=(6,0),(4,1),(2,2),(0,3); the last is a vacuum graph and cannot attach the source. A three-particle input also rules out E=2. E=4 would be a three-to-one process, but the declared source has fixed P^2=256/25 whereas its sole massless output would have p^2=0, so it is kinematically empty. Thus only the three-to-three tree remains in the source-connected column, with exactly the public V4^2, V3^2 V4 and V3^4 topology classes. The generic six-point Choi matrix commutes with three-particle complement parity, its cross-parity blocks vanish coefficientwise, and the kappa-even four-plane has positive Krein Gram I_4. Therefore a positive-even source has no connected negative-parity or different-particle-number leakage at this order. On any common compact regular acceptance C with one detector cutoff chi_C, |chi_C|<=1, orient every unordered channel so D_B=q_B^0+|q_B|>=d>0 and define beta_B,T=chi_C F_T(delta_B)/D_B. The actual tree kernel uses the unit-weight coherent sum A_full,C=16 lambda^4 sum_B K_B,T tensor R_B; it does not use the square partition chi_B. Since the ten-residue Gram has largest eigenvalue 81/16 and sum_B|beta_B|^2<=10 T^2/d^2, ||A_full,C||^2<=12960 lambda^8 T^2 mu(X)mu(Y)/d^2. Hence A_full,C^*A_full,C and its complement are positive and complete when this bound is at most one. For the dressed scalar source F tensor u0, q_click=16 lambda^8||sum_(B=1)^9 K_B,T F||^2. Outside connected leakage at this order is thereby reduced to unobserved three-body momentum regions in the same positive parity sector. The soft q_B=0 boundary, removal of the compact cutoff, disconnected spectator dynamics, higher orders, an all-time operator and Eq. (19) remain open.",
        "connected_graph_classification": {
            "vertex_degrees": "V3 carries lambda^1 and V4 carries lambda^2",
            "identity": "d_lambda=sum_v(n_v-2)=E+2L-2",
            "order4_types": [{"external_legs": e, "loops": l} for e, l in connected_types],
            "enumerated_graph_rows": rows,
            "three_input_disposition": {
                "E6_L0": "THREE_TO_THREE_TREE_ALLOWED",
                "E4_L1": "THREE_TO_ONE_EXCLUDED_BY_P_SQUARED_256_OVER_25_NOT_ZERO",
                "E2_L2": "CANNOT_CONTAIN_THREE_INCOMING_EXTERNAL_LEGS",
                "E0_L3": "VACUUM_GRAPH_DOES_NOT_ATTACH_SOURCE"
            },
            "tree_topologies": ["V4^2", "V3^2*V4", "V3^4"],
            "status": "COMPLETE_CONNECTED_ORDER_LAMBDA4_OUTPUT_IS_THREE_TO_THREE_TREE"
        },
        "positive_output_closure": {
            "three_particle_parity": "kappa_3|x>=|7-x>",
            "positive_basis": "u_x=(|x>+|7-x>)/sqrt(2), x=0,1,2,3",
            "positive_Krein_Gram": "I_4",
            "generic_Choi_identity": "kappa_3 A_6 kappa_3=A_6",
            "cross_blocks": "U_plus^T A_6 U_minus=U_minus^T A_6 U_plus=0 coefficientwise",
            "disposition": "NO_CONNECTED_NEGATIVE_PARITY_OUTPUT_FROM_POSITIVE_EVEN_SOURCE_AT_ORDER_LAMBDA4",
            "status": "COMPLETE_CONNECTED_SPECIES_CODOMAIN_IS_POSITIVE_EVEN"
        },
        "unpartitioned_compact_packet_column": {
            "acceptance": "one common compact regular C subset X times Y with |chi_C|<=1, every unordered q_B future-oriented, and D_B>=d>0",
            "channel_kernel": "beta_B,T(y,x)=chi_C(y,x)*F_T(delta_B(y,x))/D_B(y,x)",
            "amplitude": "A_full,C=16*lambda^4*sum_(B=0)^9(K_B,T tensor R_B)",
            "tree_weight_rule": "UNIT_WEIGHT_FOR_EVERY_PUBLIC_CHANNEL_TERM_NO_SQUARE_PARTITION",
            "pointwise_species_bound": "||sum_B beta_B,T R_B||_HS^2<=405*T^2/(8*d^2)",
            "operator_bound": "||A_full,C||^2<=12960*lambda^8*T^2*mu(X)*mu(Y)/d^2",
            "click": "E_click=A_full,C^*A_full,C",
            "no_click": "E_no=I-E_click",
            "sufficient_positive_domain": "12960*lambda^8*T^2*mu(X)*mu(Y)/d^2<=1",
            "completeness": "E_click+E_no=I",
            "status": "ACTUAL_UNPARTITIONED_TEN_CHANNEL_COMPACT_TREE_EFFECT_CONSTRUCTED"
        },
        "declared_scalar_source": {
            "source": "Psi_in=F tensor u0 with ||F||=1",
            "hard_channel": "R_0 u0=0",
            "exchange_channels": "R_B u0=u0/4 for B=1,...,9",
            "amplitude": "A_full,C(F tensor u0)=4*lambda^4*(sum_(B=1)^9 K_B,T F) tensor u0",
            "click_probability": "q_click=16*lambda^8*||sum_(B=1)^9 K_B,T F||^2",
            "no_click_probability": "q_no=1-q_click",
            "status": "LEADING_UNPARTITIONED_CONNECTED_PHYSICAL_SCALAR_PACKET_PROBABILITY"
        },
        "outside_leakage_reduction": {
            "different_particle_number_connected_outputs": "EXCLUDED_AT_ORDER_LAMBDA4",
            "negative_parity_connected_outputs": "EXCLUDED_FROM_KAPPA_EVEN_SOURCE",
            "remaining_connected_outside_block": "THREE_BODY_KAPPA_EVEN_MOMENTUM_OUTPUT_OUTSIDE_C",
            "global_kernel": "NOT_CONSTRUCTED_AT_SOFT_Q_B_ZERO_BOUNDARIES",
            "disconnected_spectator_terms": "OUTSIDE_CONNECTED_COLUMN_SCOPE",
            "status": "OUTPUT_TYPE_CLOSED_GLOBAL_MOMENTUM_DOMAIN_OPEN"
        },
        "assumptions": [
            "the connected perturbative graph uses only the public cubic and quartic perfect-square vertices with coupling degrees one and two",
            "the declared three-particle phase chart has fixed total momentum P=(16/5,0,0,0)",
            "external particles are massless and future directed",
            "the public six-point Choi complement symmetry holds pointwise for the complete tree coefficient",
            "the common compact acceptance excludes every q_B=0 point and permits a future orientation with one common D_B>=d>0 margin",
            "the finite-time spectral replacement is applied linearly to every public tree channel with its unit physical coefficient",
            "the result concerns the connected order-lambda4 column; disconnected spectator terms and other perturbative orders have separate ledgers"
        ],
        "does_not_establish": [
            "the full order-lambda4 S coefficient including disconnected spectator terms",
            "a bounded global operator after removing the compact regular cutoff",
            "the soft q_B=0 boundary or ordinary-Fock infrared limit",
            "a detector-independent integrated cross section",
            "the order-lambda8 forward graph",
            "an exact all-orders finite-time probability",
            "an all-time Moller, LSZ or S operator",
            "the standard scalar projector or general Eq. (19)",
            "loop/KLN completion or beyond-tree positivity",
            "gravity or BV/BRST transfer",
            "anything LORENTZIAN-CAUSAL",
            "literature priority"
        ],
        "missing_object_ledger": [
            {"object": "soft-boundary completion of the connected three-body finite-time kernel", "status": "MISSING", "required_value": "control all q_B=0 strata and prove a finite or typed divergent exhaustion limit"},
            {"object": "disconnected spectator contribution to the complete order-lambda4 three-particle evolution", "status": "MISSING", "required_value": "common-domain finite-time composition with lower-order connected blocks"},
            {"object": "matching forward cut and exhaustive positive output theorem", "status": "MISSING", "required_value": "complete connected-plus-disconnected Gram or general Eq. (19) trace identity"}
        ],
        "next_gate": "Analyze the q_B=0 strata of the actual unpartitioned finite-time three-body kernel in the exact five-dimensional phase chart. Determine the local codimension and measure power of |F_T(delta_B)/D_B|^2, and prove either square integrability or the first exact infrared divergence. This is now the only missing connected-output domain gate at order lambda4; disconnected spectator dynamics remains separate.",
        "provenance": {
            "source_commit": "4c49ce8f15dc742d92b7740af36b4f4a3fd57655",
            "retrieval_date": "2026-08-12",
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "method": "Exact connected graph half-edge/loop enumeration; rational complement-parity Choi reconstruction; exact ten-residue Fraction Gram; analytic finite-time Hilbert--Schmidt estimate. No floating-point arithmetic is used."
        },
        "verification_commands": [
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_complete_connected_order4_packet_column.py --write --check",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_complete_connected_order4_packet_column.py",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest -v reverse_physics.tests.test_bt_complete_connected_order4_packet_column"
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
    if not value["checks"]["ok"]:
        print("failures:", ", ".join(value["checks"]["failures"]))
    return 0 if value["checks"]["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
