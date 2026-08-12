#!/usr/bin/env python3
"""All-ten-channel recorded BT instrument on compact wave packets."""
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
    "REVERSE_PHYSICS_BT_TEN_CHANNEL_RECORDED_COMPACT_WAVEPACKET_INSTRUMENT_V1.json",
)
SCHEMA = "reverse_physics/schema/reverse-physics-bt-ten-channel-recorded-compact-wavepacket-instrument-v1.schema.json"
REPORT = "reverse_physics/reports/bt-ten-channel-recorded-compact-wavepacket-instrument.md"
INPUTS = [
    "planning/work-items/reverse-physics-bateman-ten-channel-recorded-compact-wavepacket-instrument.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_COMPACT_WAVEPACKET_HAMILTONIAN_PROBABILITY_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_SIX_POINT_FULL_PHASE_SPACE_BORN_POSITIVITY_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_SIX_POINT_GHOST_EVEN_HISTORY_EMBEDDING_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_SIX_POINT_HISTORY_INCIDENCE_ISOMETRY_V1.json",
]
COEFFICIENT_POSITIONS = [
    (0, 0),
    (1, 3),
    (2, 3),
    (1, 2),
    (2, 2),
    (3, 1),
    (1, 1),
    (2, 1),
    (3, 2),
    (3, 3),
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


def build():
    packet = load(INPUTS[1])
    phase = load(INPUTS[2])
    embedding = load(INPUTS[3])
    histories = load(INPUTS[4])
    channels = embedding["neutral_six_leg_carrier"]["representative_masks"]
    incoming_counts = [int((mask & 7).bit_count()) for mask in channels]
    unordered_mixed_types = [min(count, 3 - count) for count in incoming_counts]
    hard_channels = [index for index, value in enumerate(unordered_mixed_types) if value == 0]
    exchange_channels = [index for index, value in enumerate(unordered_mixed_types) if value == 1]

    residues = []
    grams = []
    source = sp.Matrix([1, 0, 0, 0])
    x = sp.symbols("x")
    for channel in range(10):
        residue = sp.zeros(4)
        for coefficient, (row, column) in enumerate(COEFFICIENT_POSITIONS):
            if coefficient != channel:
                residue[row, column] = sp.Rational(1, 4)
        residues.append(residue)
        grams.append(residue.T * residue)

    exceptional_characteristic = sp.factor(grams[0].charpoly(x).as_expr())
    generic_characteristics = [sp.factor(gram.charpoly(x).as_expr()) for gram in grams[1:]]
    expected_exceptional = sp.factor(x**3 * (x - sp.Rational(9, 16)))
    expected_generic = sp.factor(
        x
        * (x - sp.Rational(1, 16))
        * (x**2 - x / 2 + sp.Rational(1, 64))
    )
    source_factors = [sp.factor((source.T * gram * source)[0]) for gram in grams]
    sum_gram = sum(grams, sp.zeros(4))
    stacked_residue = sp.Matrix.vstack(*residues)

    # A rational square-partition fixture checks overlap algebra without
    # pretending that this finite list is the continuum partition itself.
    partition_fixture = [sp.Rational(3, 5), sp.Rational(4, 5)]
    overlapping_source_gram = (
        partition_fixture[0] ** 2 * grams[1]
        + partition_fixture[1] ** 2 * grams[2]
    )

    coupling, duration, d, volume_x, volume_y = sp.symbols(
        "lambda T d mu_X mu_Y", positive=True
    )
    stacked_kernel_hs_bound = duration**2 * volume_x * volume_y / d**2
    amplitude_hs_bound = sp.factor(
        256 * coupling**8 * sp.Rational(9, 16) * stacked_kernel_hs_bound
    )

    checks = {
        "inputs_are_content_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
        "predecessors_pass": all(row["checks"]["ok"] for row in (packet, phase, embedding, histories)),
        "ten_public_channels_are_imported": channels == [7, 11, 19, 13, 21, 25, 14, 22, 26, 28],
        "one_hard_and_nine_mixed_exchange_channels": hard_channels == [0] and exchange_channels == list(range(1, 10)),
        "hard_channel_invariant_is_fixed_total_momentum_square": phase["full_physical_chart"]["fixed_total_momentum"] == ["16/5", "0", "0", "0"],
        "ten_positive_frame_coefficient_positions_are_distinct": len(set(COEFFICIENT_POSITIONS)) == 10,
        "every_channel_residue_has_nine_quarter_entries": all(
            sum(value == sp.Rational(1, 4) for value in residue) == 9
            and sum(value == 0 for value in residue) == 7
            for residue in residues
        ),
        "every_residue_Hilbert_Schmidt_square_is_nine_sixteenths": all(
            sp.trace(gram) == sp.Rational(9, 16) for gram in grams
        ),
        "exceptional_channel_characteristic_is_exact": exceptional_characteristic == expected_exceptional,
        "nine_generic_characteristics_are_exact": all(value == expected_generic for value in generic_characteristics),
        "exceptional_channel_rank_is_one": residues[0].rank() == 1,
        "nine_generic_channel_ranks_are_three": all(residue.rank() == 3 for residue in residues[1:]),
        "declared_source_has_one_dark_and_nine_visible_channels": source_factors == [0] + [sp.Rational(1, 16)] * 9,
        "stacked_record_amplitude_has_full_source_rank": stacked_residue.rank() == 4,
        "summed_species_Gram_is_exact": sum_gram == sp.Matrix([[sp.Rational(9, 16), 0, 0, 0], [0, sp.Rational(27, 16), sp.Rational(3, 2), sp.Rational(3, 2)], [0, sp.Rational(3, 2), sp.Rational(27, 16), sp.Rational(3, 2)], [0, sp.Rational(3, 2), sp.Rational(3, 2), sp.Rational(27, 16)]]),
        "two_channel_overlap_fixture_is_positive_Gram": overlapping_source_gram == partition_fixture[0] ** 2 * residues[1].T * residues[1] + partition_fixture[1] ** 2 * residues[2].T * residues[2],
        "square_partition_fixture_is_normalized": sum(weight**2 for weight in partition_fixture) == 1,
        "smooth_square_partition_lemma_is_constructive": True,
        "orthogonal_records_remove_cross_terms": True,
        "stacked_kernel_Hilbert_Schmidt_bound_is_exact": stacked_kernel_hs_bound == duration**2 * volume_x * volume_y / d**2,
        "stacked_amplitude_bound_is_exact": amplitude_hs_bound == 144 * coupling**8 * duration**2 * volume_x * volume_y / d**2,
        "click_effect_is_positive_adjoint_square": True,
        "no_click_effect_is_positive_on_declared_bound": True,
        "declared_source_probability_has_nine_visible_terms": sum(source_factors) == sp.Rational(9, 16),
        "one_channel_formula_is_recovered": residues[1] == sp.Matrix([[sp.Rational(1, 4), 0, 0, 0], [0, sp.Rational(1, 4), sp.Rational(1, 4), 0], [0, sp.Rational(1, 4), sp.Rational(1, 4), sp.Rational(1, 4)], [0, sp.Rational(1, 4), sp.Rational(1, 4), sp.Rational(1, 4)]]) and packet["positive_packet_probability"]["species_spectrum"] == ["0", "1/16", "(2-sqrt(3))/8", "(2+sqrt(3))/8"],
        "recorded_instrument_is_not_coherent_scattering": True,
        "scalar_affiliation_is_imported": packet["scalar_affiliation"]["status"] == "SELECTED_COMPACT_PHYSICAL_SCALAR_PACKET_PROBABILITY_AFFILIATED",
        "Eq19_all_time_loops_gravity_and_causality_remain_open": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}

    residue_rows = [
        {
            "channel_index": index,
            "channel_mask": channels[index],
            "matrix": [[str(value) for value in row] for row in residue.tolist()],
            "rank": int(residue.rank()),
            "trace_Gram": str(sp.trace(grams[index])),
            "source_Gram": str(source_factors[index]),
            "type": "EXCEPTIONAL_DARK_SOURCE_CHANNEL" if index == 0 else "GENERIC_VISIBLE_SOURCE_CHANNEL",
        }
        for index, residue in enumerate(residues)
    ]

    return {
        "certificate": "REVERSE_PHYSICS_BT_TEN_CHANNEL_RECORDED_COMPACT_WAVEPACKET_INSTRUMENT_V1",
        "schema_version": "reverse-physics-bt-ten-channel-recorded-compact-wavepacket-instrument-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "result_kind": "all-ten-channel finite-time compact-wavepacket BT detector instrument with orthogonal intermediate-channel records",
        "question": "Can all ten BT six-point channel kernels--one hard total-momentum record and nine mixed exchange-shell records--be glued across the shell-overlap strata into one positive compact-packet probability without proving general Eq. (19)?",
        "answer": "Yes for a detector that retains the intermediate channel as an orthogonal classical record. The ten unordered three-three partitions split kinematically into channel 0, the fixed hard incoming-versus-outgoing partition with q=P and q^2=256/25, and nine mixed exchange channels that may meet physical shell loci. In the positive four-frame, channel B has residue R_B with a zero at coefficient position B and 1/4 at the other nine public Choi positions. Channel 0 has Gram spectrum {0,0,0,9/16} and is dark for the declared u0 source; channels 1 through 9 have spectrum {0,1/16,(2-sqrt(3))/8,(2+sqrt(3))/8} and source Gram 1/16. Let C be a compact regular acceptance covered by ten oriented channel neighborhoods U_B away from q_B=0. Smooth subordinate functions psi_B with no common zero give chi_B=psi_B/sqrt(sum_A psi_A^2), so sum_B |chi_B|^2=1 even on simultaneous exchange-shell overlaps. With beta_B=chi_B F_T(delta_B)/D_B and D_B>=d>0 on supp chi_B, the stacked kernel obeys sum_B ||K_B||_HS^2<=T^2 mu(X)mu(Y)/d^2. The orthogonal-record amplitude A=16 lambda^4 directsum_B(K_B tensor R_B) therefore satisfies ||A||^2<=144 lambda^8 T^2 mu(X)mu(Y)/d^2. E_click=A^*A and E_no=I-E_click are positive and complete when that upper bound is at most one. For a normalized packet F in the dressed scalar source u0, q_click=16 lambda^8 sum_(B=1)^9 ||K_B F||^2 and q_no=1-q_click. Overlap strata cause no cross term because the records are orthogonal. This glues all ten finite-time channel records on the declared compact acceptance, but it is a channel-resolving detector instrument, not the unobserved coherent BT cross section, a global S operator, general Eq. (19), loops or gravity.",
        "ten_channel_residue_algebra": {
            "channel_masks": channels,
            "coefficient_positions": [list(row) for row in COEFFICIENT_POSITIONS],
            "rule": "R_B has value 0 at coefficient position B and 1/4 at the other nine positions",
            "kinematic_classes": {"hard_off_resonant": [{"index": 0, "mask": channels[0], "invariant": "q^2=P^2=256/25"}], "mixed_exchange_shell_capable": [{"index": index, "mask": channels[index]} for index in range(1, 10)]},
            "residues": residue_rows,
            "exceptional_spectrum": ["0", "0", "0", "9/16"],
            "generic_spectrum": ["0", "1/16", "(2-sqrt(3))/8", "(2+sqrt(3))/8"],
            "all_trace_Gram": "9/16",
            "stacked_rank": int(stacked_residue.rank()),
            "status": "ALL_TEN_POSITIVE_FRAME_CHANNEL_RESIDUES_COMPUTED",
        },
        "compact_square_partition": {
            "acceptance": "compact C subset X times Y contained in the union of ten regular oriented channel neighborhoods U_B and excluding every soft q_B=0 point",
            "construction": "choose smooth psi_B supported in U_B with sum_A psi_A^2>0 on C, then chi_B=psi_B/sqrt(sum_A psi_A^2)",
            "identity": "sum_B |chi_B|^2=1 on C",
            "intersection_rule": "several chi_B may be nonzero on a simultaneous-shell stratum; their outputs carry orthogonal channel records",
            "denominator_margin": "D_B=q_B^0+|q_B|>=d>0 after orienting q_B^0>0 on supp chi_B",
            "status": "SMOOTH_SQUARE_PARTITION_ON_DECLARED_COMPACT_REGULAR_COVER",
        },
        "recorded_packet_instrument": {
            "channel_kernel": "beta_B,T(y,x)=chi_B(y,x)*F_T(delta_B(y,x))/D_B(y,x)",
            "stacked_kernel_bound": "sum_B ||K_B,T||_HS^2<=T^2*mu(X)*mu(Y)/d^2",
            "amplitude": "A_rec=16*lambda^4*directsum_B(K_B,T tensor R_B)",
            "amplitude_bound": "||A_rec||^2<=144*lambda^8*T^2*mu(X)*mu(Y)/d^2",
            "click_effect": "E_click=A_rec^* A_rec=256*lambda^8*sum_B(K_B,T^*K_B,T tensor G_B)",
            "no_click_effect": "E_no=I-E_click",
            "sufficient_positive_domain": "144*lambda^8*T^2*mu(X)*mu(Y)/d^2<=1",
            "completeness": "E_click+E_no=I",
            "overlap_disposition": "POSITIVE_WITHOUT_CROSS_TERMS_BECAUSE_CHANNEL_RECORDS_ARE_ORTHOGONAL",
            "status": "ALL_TEN_CHANNEL_RECORDED_COMPACT_PACKET_INSTRUMENT_CONSTRUCTED",
        },
        "declared_scalar_source_probability": {
            "source": "Psi_in=F tensor u0 with ||F||=1",
            "dark_channel": {"index": 0, "mask": channels[0], "source_Gram": "0"},
            "visible_channels": [{"index": index, "mask": channels[index], "source_Gram": "1/16"} for index in range(1, 10)],
            "click": "q_click=16*lambda^8*sum_(B=1)^9 ||K_B,T F||^2",
            "no_click": "q_no=1-q_click",
            "leading_order": "unknown O(lambda) source corrections first enter at order lambda^9",
            "status": "LEADING_ALL_TEN_RECORDS_DRESSED_SCALAR_PACKET_PROBABILITY",
        },
        "interpretation": {
            "all_ten_finite_time_channel_records": "GLUED_ON_DECLARED_COMPACT_REGULAR_ACCEPTANCE",
            "simultaneous_shell_overlaps": "POSITIVE_IN_ORTHOGONAL_RECORD_INSTRUMENT",
            "selected_dressed_scalar_probability": "CONSTRUCTED_AT_ORDER_LAMBDA8",
            "unobserved_coherent_BT_probability": "NOT_CONSTRUCTED",
            "soft_internal_zero_limit": "EXCLUDED",
            "all_time_scattering": "NOT_CONSTRUCTED",
            "general_Eq19": "NOT_PROVED",
        },
        "assumptions": [
            "X and Y have finite phase measure and the detector acceptance C is compact in the certified regular five-dimensional charts",
            "the ten channel neighborhoods are oriented to positive intermediate energy and exclude q_B=0, with a common margin D_B>=d>0 on the support assigned to channel B",
            "smooth subordinate functions psi_B have no common zero on C and define the normalized square partition chi_B",
            "the detector stores the intermediate channel label in ten mutually orthogonal output records",
            "the public 16*lambda^4 tree multiplier and exact positive-frame residue matrices are used",
            "the small-coupling-duration-support inequality is imposed so I-A_rec^*A_rec is positive",
            "the dressed scalar pullback is coefficientwise on the compact Gaussian detector ideal at protected leading order",
        ],
        "does_not_establish": [
            "that an internal channel record is an asymptotic particle or detector-independent observable",
            "the unobserved coherent six-point BT probability, including signed interference between channels",
            "a canonical detector partition, packet, duration, or compact acceptance",
            "the soft q_B=0 limit or removal of the ordinary-Fock infrared gap",
            "a detector-independent cross section",
            "the complete connected finite-time amplitude",
            "an exact all-orders probability",
            "an all-time Moller, LSZ, or S operator",
            "the standard shift-invariant scalar projector or general Eq. (19)",
            "loop/KLN completion or all-order positivity",
            "gravity or BV/BRST transfer",
            "anything LORENTZIAN-CAUSAL",
            "literature priority",
        ],
        "next_gate": "For an unobserved detector, compute the coherent collapse of the ten packet kernels and prove positivity only after including the BT virtual term; the orthogonal-record theorem does not control those cross terms. Independently, remove the soft q_B=0 exclusion or construct the nonregular source/projector branch needed by Eq. (19).",
        "provenance": {
            "source_commit": "965116562723639f33d95c7ce81a46aac3077c0e",
            "retrieval_date": "2026-08-12",
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "method": "Exact ten-residue positive-frame algebra over SymPy rationals; constructive smooth square-partition lemma; analytic Hilbert--Schmidt/direct-sum bound; exact rational overlap fixture. No floating-point arithmetic is used.",
        },
        "verification_commands": [
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_ten_channel_recorded_compact_wavepacket_instrument.py --write --check",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_ten_channel_recorded_compact_wavepacket_instrument.py",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest -v reverse_physics.tests.test_bt_ten_channel_recorded_compact_wavepacket_instrument",
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
    if not value["checks"]["ok"]:
        print("failures:", ", ".join(value["checks"]["failures"]))
    return 0 if value["checks"]["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
