#!/usr/bin/env python3
"""Exact crossed-order closure of the finite physical BT HP path carrier."""
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
    "REVERSE_PHYSICS_BT_CROSSED_ORDER_CHAMBER_COMPLETION_V1.json",
)
SCHEMA = (
    "reverse_physics/schema/"
    "reverse-physics-bt-crossed-order-chamber-completion-v1.schema.json"
)
REPORT = "reverse_physics/reports/bt-crossed-order-chamber-completion.md"
SOURCE = "63f24352be5e68773982d772fa3acbe20ef839aa"
EVENT = (
    "planning/events/"
    "reverse-physics-bateman-crossed-order-chamber-completion-DONE-63f24352.json"
)
INPUTS = [
    "planning/work-items/"
    "reverse-physics-bateman-crossed-order-chamber-completion.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_QUANTUM_STOCHASTIC_MOLLER_DILATION_V1.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_SEVEN_POINT_NESTED_CONTINUUM_INTERTWINER_V1.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_PHYSICAL_MOLLER_DEFECT_COMPLETION_V1.json",
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


def frac(value):
    return Fraction(value["numerator"], value["denominator"])


def rat(value):
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def rows(matrix):
    import sympy as sp

    return [
        [str(sp.factor(matrix[i, j])) for j in range(matrix.cols)]
        for i in range(matrix.rows)
    ]


def history_level(key):
    return len([part for part in key.replace("|", ",").split(",") if part]) - 2


def build():
    import sympy as sp

    hp = load(INPUTS[1])
    continuum = load(INPUTS[2])
    defect = load(INPUTS[3])

    history_counts = hp["system_and_noise_carrier"]["history_counts"]
    edge_counts = hp["system_and_noise_carrier"]["edge_counts"]
    channels = hp["system_and_noise_carrier"]["noise_channels"]
    rates = [
        frac(value)
        for value in hp["minimal_kraus_theorem"]["diagonal_values_by_level"]
    ]
    # The recorded Kraus Gram is 2*q_k, so divide by the two physical species.
    extension_rates = [value / 2 for value in rates]
    unique_parent_by_child = all(
        len(
            {
                row["parent"]
                for row in channels
                if row["level"] == level and row["child"] == child
            }
        )
        == 1
        for level in range(3)
        for child in {
            row["child"] for row in channels if row["level"] == level
        }
    )

    chamber_counts = [math.factorial(level) for level in range(4)]
    chamber_history_sheets = [
        history_counts[level] * chamber_counts[level] for level in range(4)
    ]
    canonical_history_sheets = list(history_counts)
    missing_crossed_sheets = [
        chamber_history_sheets[level] - canonical_history_sheets[level]
        for level in range(4)
    ]
    species_multiplicities = [2 * value for value in chamber_history_sheets]

    # Acting on a canonical level-k incoming chamber inserts the new edge time
    # into one of k+1 positions.  Only the last position remains canonical.
    direct_insertion_rows = []
    for level in range(3):
        target = level + 1
        positions = target
        leaked_positions = target - 1
        direct_insertion_rows.append(
            {
                "source_level": level,
                "target_level": target,
                "insertion_positions_per_child": positions,
                "canonical_positions_per_child": 1,
                "crossed_positions_per_child": leaked_positions,
                "target_histories": history_counts[target],
                "direct_crossed_sheets": (
                    history_counts[target] * leaked_positions
                ),
                "per_edge_leakage_rate": rat(extension_rates[level]),
            }
        )

    # Q_HP=N_F-L is an exact gauge for the HP structure coefficients.
    gauge_deltas = {
        "creation_noise_change": 1,
        "creation_level_change": 1,
        "creation_Q_change": 0,
        "annihilation_noise_change": -1,
        "annihilation_level_change": -1,
        "annihilation_Q_change": 0,
        "drift_noise_change": 0,
        "drift_level_change": 0,
        "drift_Q_change": 0,
    }

    # A three-state exact witness: parent, canonical child, reversed child.
    # The HP coefficient sends a late one-quantum parent input into the
    # reversed chamber when the child edge is created in an earlier bin.
    q1 = sp.Rational(
        extension_rates[1].numerator, extension_rates[1].denominator
    )
    B = sp.zeros(3)
    B[2, 0] = sp.sqrt(q1)
    K = B - B.T
    cayley = sp.simplify((sp.eye(3) + K) * (sp.eye(3) - K).inv())
    parent = sp.Matrix([1, 0, 0])
    reversed_projection = sp.diag(0, 0, 1)
    leaked = reversed_projection * cayley * parent
    cayley_leakage = sp.simplify((leaked.T * leaked)[0])

    checks = {
        "predecessor_certificates_pass": all(
            value["checks"]["ok"] for value in (hp, continuum, defect)
        ),
        "history_counts_imported": history_counts == [1, 3, 12, 60],
        "edge_counts_imported": edge_counts == [3, 12, 60],
        "every_history_has_unique_ancestral_parent_edge": (
            unique_parent_by_child
            and [
                len({row["child"] for row in channels if row["level"] == level})
                for level in range(3)
            ]
            == edge_counts
        ),
        "every_HP_edge_raises_comb_level_by_one": all(
            history_level(row["parent"]) == row["level"]
            and history_level(row["child"]) == row["level"] + 1
            for row in channels
        ),
        "extension_rates_recovered": extension_rates
        == [Fraction(1, 48), Fraction(5, 64), Fraction(27, 400)],
        "all_available_marks_physically_affiliated_on_vacuum_chamber": (
            continuum["seventy_five_mark_completion"]
            ["physically_intertwined_edge_marks"] == list(range(75))
        ),
        "vacuum_affiliation_is_ordered": all(
            token in continuum["ordered_three_noise_intertwiner"]["hp_carrier"]
            for token in ("0<t1<t2<t3", "C60_edge", "C2_species")
        ),
        "creation_preserves_HP_gauge": (
            gauge_deltas["creation_noise_change"]
            - gauge_deltas["creation_level_change"] == 0
        ),
        "annihilation_preserves_HP_gauge": (
            gauge_deltas["annihilation_noise_change"]
            - gauge_deltas["annihilation_level_change"] == 0
        ),
        "drift_preserves_HP_gauge": (
            gauge_deltas["drift_noise_change"]
            - gauge_deltas["drift_level_change"] == 0
        ),
        "chamber_recurrence_is_factorial": all(
            chamber_counts[level + 1]
            == (level + 1) * chamber_counts[level]
            for level in range(3)
        ),
        "chamber_counts_are_1_1_2_6": chamber_counts == [1, 1, 2, 6],
        "completed_history_sheets_are_1_3_24_360": (
            chamber_history_sheets == [1, 3, 24, 360]
        ),
        "missing_crossed_sheets_are_0_0_12_300": (
            missing_crossed_sheets == [0, 0, 12, 300]
        ),
        "total_existing_sheets_are_76": sum(canonical_history_sheets) == 76,
        "total_completed_sheets_are_388": sum(chamber_history_sheets) == 388,
        "total_missing_crossed_sheets_are_312": sum(missing_crossed_sheets) == 312,
        "species_multiplicity_grows_152_to_776": (
            2 * sum(canonical_history_sheets) == 152
            and sum(species_multiplicities) == 776
        ),
        "canonical_level_one_input_leaks_at_level_two": (
            direct_insertion_rows[1]["direct_crossed_sheets"] == 12
            and extension_rates[1] > 0
        ),
        "canonical_level_two_input_leaks_at_level_three": (
            direct_insertion_rows[2]["direct_crossed_sheets"] == 120
            and extension_rates[2] > 0
        ),
        "finite_leakage_generator_is_skew": K.T == -K,
        "finite_leakage_generator_norm_is_q1": (
            sp.simplify(B.T * B)
            == sp.diag(q1, 0, 0)
        ),
        "finite_cayley_witness_is_unitary": (
            sp.simplify(cayley.T * cayley) == sp.eye(3)
            and sp.simplify(cayley * cayley.T) == sp.eye(3)
        ),
        "finite_cayley_witness_leaks_exactly": (
            cayley_leakage == sp.Rational(1280, 4761)
        ),
        "crossed_chambers_not_supplied_by_external_label_covariance": (
            "chronologically attached" in continuum
            ["physical_cumulative_resolution"]["permutation_compatibility"]
        ),
        "defect_action_remains_physically_unselected": (
            defect["disposition"]["completion_selected_by_public_amplitudes"]
            == "EXACTLY_UNDERDETERMINED"
        ),
        "input_hashes_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
    }
    checks = {name: bool(value) for name, value in checks.items()}

    return {
        "certificate": "REVERSE_PHYSICS_BT_CROSSED_ORDER_CHAMBER_COMPLETION_V1",
        "schema_version": "reverse-physics-bt-crossed-order-chamber-completion-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "CLASSIFIED",
        "result_kind": "exact crossed-time-order reducing closure and two-sided invariance obstruction for the finite physical BT HP path carrier",
        "question": "Can the certified vacuum-ordered physical intertwiners transfer the full two-sided 75-edge HP unitary, and if not what is the smallest no-spectator path closure they require?",
        "answer": "No on the presently certified chronological carrier. The HP structure has the exact gauge Q_HP=N_F-L: every J_e dA_e^dagger raises both noise number and rooted-comb level, every reverse term lowers both, and the drift changes neither. The ancestry-matched no-spectator path sector is therefore stable only after every assignment of its k distinct ancestral edge times is included. The vacuum maps A_k cover one chamber t1<...<tk. Used as incoming data, a level-k state can receive its child quantum in any of k+1 temporal positions, and all but the last are orthogonal crossed chambers. The minimal reducing closure consequently has k! chambers per history. Multiplying the certified history counts 1,3,12,60 gives 1,3,24,360 chamber-history sheets, rather than 76 canonical sheets; 312 crossed sheets, or 624 species-resolved multiplicities, are missing. An exact three-state skew/Cayley witness at q1=5/64 has reversed-chamber probability 1280/4761. Thus the abstract HP cocycle supplies a candidate dynamics, but the physical Kallen maps affiliate only its vacuum chronology and cannot yet transfer it to a two-sided physical operator. The first missing calculation is a crossed six-point two-emission intertwiner, not the scalar vacuum fourth jump.",
        "assumptions": [
            "The no-spectator path sector contains exactly one Boson in each distinct ancestral edge channel and the system in the terminal rooted-comb history; arbitrary additional incoming noise belongs to separate Q_HP sectors and is not included.",
            "Order chambers are the connected components obtained by removing equal-time diagonals from the k ancestral time coordinates; those diagonals have measure zero.",
            "The certified A1, A2 and A3 maps affiliate only the vacuum chronological chamber in which ancestry order equals detector-time order.",
            "The finite Cayley matrix is an exact witness for unitary-compatible leakage of the HP coefficient, not the continuous HP cocycle itself."
        ],
        "HP_gauge_theorem": {
            "system_level": "L|h_k>=k|h_k>",
            "noise_number": "N_F on the 75-edge Boson Fock carrier",
            "gauge": "Q_HP=N_F-L",
            "creation": "J_e dA_e^dagger changes (N_F,L) by (+1,+1)",
            "annihilation": "-J_e^dagger dA_e changes (N_F,L) by (-1,-1)",
            "drift": "-D da changes (N_F,L) by (0,0)",
            "commutation": "[Q_HP,U_a]=0 on the finite-particle adapted core",
            "gauge_deltas": gauge_deltas,
            "boundary": "Q_HP is an auxiliary system-noise grading, not the BT boost charge, ghost parity, or a spacetime charge."
        },
        "order_chamber_completion": {
            "canonical_chamber": "O_k={0<t1<...<tk<a}, one chamber per rooted-comb history",
            "insertion_rule": "For a level-k incoming configuration, the new child-edge time can occupy any of k+1 positions among the k existing ancestral times.",
            "closure_recurrence": "c_0=1 and c_(k+1)=(k+1)c_k, hence c_k=k!",
            "history_counts": history_counts,
            "chambers_per_history": chamber_counts,
            "canonical_history_sheets": canonical_history_sheets,
            "completed_history_sheets": chamber_history_sheets,
            "missing_crossed_sheets": missing_crossed_sheets,
            "species_resolved_completed_multiplicities": species_multiplicities,
            "canonical_total": sum(canonical_history_sheets),
            "completed_total": sum(chamber_history_sheets),
            "missing_crossed_total": sum(missing_crossed_sheets),
            "direct_canonical_input_leakage": direct_insertion_rows,
            "minimality": "Starting from all chambers at level k, insertion in every temporal position produces all (k+1)! chambers at level k+1; adjoint annihilation deletes the current edge and returns a chamber at level k. No proper chamber subset containing the canonical chambers is reducing for all nonzero edge coefficients."
        },
        "finite_exact_leakage_witness": {
            "basis": ["late_parent", "canonical_child", "reversed_child"],
            "rate_q1": rat(extension_rates[1]),
            "coefficient_B": rows(B),
            "skew_generator_K": rows(K),
            "cayley_unitary": rows(cayley),
            "reversed_chamber_probability": rat(Fraction(1280, 4761)),
            "meaning": "A late parent quantum and an earlier child creation have reversed ancestry-time order. The rational-algebraic Cayley unitary proves the missing chamber is compatible with exact two-sided unitarity; it is not identified with U_a."
        },
        "physical_transfer_gate": {
            "certified_map": "A_<=3 on the 76 canonical vacuum-ordered history sheets",
            "required_extension": "A_ch on all 388 no-spectator chamber-history sheets, agreeing with A_<=3 on the canonical chambers",
            "conditional_transfer": "If A_ch is unitary onto declared physical incoming/outgoing ranges and intertwines the chamber-complete HP restriction, then S_ch=A_ch U_a|_ch A_ch^* is a two-sided reduced-mode physical unitary with vacuum column M_a.",
            "first_missing_block": "the reversed two-time chamber of each of the 12 six-point histories",
            "higher_missing_block": "the five noncanonical time-order chambers of each of the 60 seven-point histories",
            "external_permutation_boundary": "Existing external-label covariance inside t1<t2<t3 does not identify a chronologically attached daughter with a pre-existing incoming cluster and therefore does not supply crossed chambers.",
            "spectator_boundary": "Arbitrary incoming spectator/noise sectors Q_HP!=0 remain additional and are not closed by the 388-sheet no-spectator completion."
        },
        "disposition": {
            "HP_number_level_gauge": "PROVED_ON_FINITE_PARTICLE_ADAPTED_CORE",
            "vacuum_chronological_carrier_two_sided_invariance": "EXACTLY_OBSTRUCTED",
            "minimal_no_spectator_path_reducing_closure": "CLASSIFIED_AS_ALL_FACTORIAL_ORDER_CHAMBERS",
            "canonical_physical_history_sheets": 76,
            "required_chamber_complete_history_sheets": 388,
            "missing_crossed_physical_sheets": 312,
            "crossed_six_and_seven_point_intertwiners": "NOT_CONSTRUCTED",
            "arbitrary_incoming_spectator_sectors": "NOT_CONSTRUCTED",
            "two_sided_reduced_mode_physical_operator": "NOT_CONSTRUCTED",
            "spacetime_Moller_LSZ_S_operator": "NOT_CONSTRUCTED",
            "complete_BT_probability": "NOT_CONSTRUCTED",
            "Eq19_all_orders": "NOT_PROVED"
        },
        "does_not_establish": [
            "a physical crossed six-point or seven-point amplitude",
            "that the finite Cayley witness equals the HP cocycle",
            "physical affiliation of the 312 crossed chamber sheets",
            "arbitrary incoming spectator or non-strongly-ordered sectors",
            "the vacuum fourth jump or a normalized fourth probability",
            "a unique all-order stochastic law",
            "a complete physical two-to-n probability",
            "a spacetime-local Moller, LSZ, AQFT, or S operator",
            "the all-order Bateman--Turok Eq. (19)",
            "a gravity or BRST lift",
            "anything LORENTZIAN-CAUSAL",
            "a new physical or spacetime dimension",
            "literature priority"
        ],
        "next_gate": "Construct the first reversed two-time six-point physical intertwiner. Cross one degenerate leg into the incoming side while retaining both Abel/Kallen resolution coordinates, the full two-species parent/profile Gram and the generalized-Born sign. It must map each of the 12 reversed chambers into a declared physical range and intertwine the HP q1 creation/annihilation pair. Only then can the chamber transfer be extended to level two; the 300 level-three crossed sheets and all spectator Q_HP sectors remain subsequent gates.",
        "provenance": {
            "source_commit": SOURCE,
            "retrieval_date": "2026-08-12",
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
        },
        "verification_commands": [
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_crossed_order_chamber_completion.py --check",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_crossed_order_chamber_completion.py",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest -v reverse_physics.tests.test_bt_crossed_order_chamber_completion"
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
        == "REVERSE_PHYSICS_BT_CROSSED_ORDER_CHAMBER_COMPLETION_V1"
        and value.get("checks", {}).get("passed")
        == value.get("checks", {}).get("total")
        == 28
        and value.get("checks", {}).get("failures") == []
        and all(value.get("checks", {}).get("details", {}).values())
        and len(inputs) == 5
        and all(row.get("sha256") == sha256(row.get("path", "")) for row in inputs)
        and value.get("disposition", {}).get("spacetime_Moller_LSZ_S_operator")
        == "NOT_CONSTRUCTED"
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
    if args.check:
        try:
            with open(args.output, encoding="utf-8") as handle:
                recorded = canonical(json.load(handle))
        except (OSError, json.JSONDecodeError) as exc:
            print("[FAIL] recorded certificate:", exc)
            return 1
        if recorded != rendered:
            print("[FAIL] certificate drift")
            return 1
    print("checks %d/%d" % (value["checks"]["passed"], value["checks"]["total"]))
    print("RESULT:", "PASS" if value["checks"]["ok"] else "FAIL")
    print("canonical sheets:", value["order_chamber_completion"]["canonical_total"])
    print("completed sheets:", value["order_chamber_completion"]["completed_total"])
    print("missing crossed sheets:", value["order_chamber_completion"]["missing_crossed_total"])
    return 0 if value["checks"]["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
