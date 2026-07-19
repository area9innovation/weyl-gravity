#!/usr/bin/env python3
"""Certify the reusable Berger reality-folded contiguous-shell stop adapter."""

from __future__ import annotations

import argparse
from copy import deepcopy
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from closed_universe_observers.berger_recoil_first_omitted_shell_binding import (
    bind_first_omitted_shell_direct_carriers,
)
from closed_universe_observers.berger_recoil_interval_stream import (
    RationalInterval,
    compose_four_recoil_tail_radii,
)
from closed_universe_observers.berger_recoil_real_shell_extraction import (
    extract_real_channel_column_sum,
)
from closed_universe_observers.berger_recoil_reality_folded_stream import (
    STREAM_KEYS,
    _validated_representative_rows,
    run_reality_folded_shell_stream,
)
from closed_universe_observers.generate_berger_maxwell_energy_graph_norm_tail import (
    _graph_tail_upper,
)


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = PACKAGE / "certificates/BERGER_RECOIL_REALITY_FOLDED_SHELL_STREAM_ADAPTER.json"
SCHEMA = PACKAGE / "schema/berger-recoil-reality-folded-shell-stream-adapter-v1.schema.json"
REPORT = PACKAGE / "reports/berger-recoil-reality-folded-shell-stream-adapter.md"
DEPENDENCIES = {
    "two_j6_binding": PACKAGE / "certificates/BERGER_RECOIL_TWO_J6_REALITY_FOLDED_BINDING.json",
    "direct_gate": PACKAGE / "certificates/BERGER_RECOIL_DIRECT_SHELL_AND_TAIL_STOP_GATE.json",
    "first_omitted": PACKAGE / "certificates/BERGER_RECOIL_FIRST_OMITTED_SHELL_PROVIDER_TWO_J5.json",
    "detector_image": PACKAGE / "certificates/BERGER_GREEN_WEIGHTED_DETECTOR_CODERIVATIVE.json",
    "cross_remainder": PACKAGE / "certificates/BERGER_CROSS_WINDOW_DETECTOR_ADVANCED_MAXWELL_REMAINDER.json",
    "exact_kernels": PACKAGE / "certificates/BERGER_RECOIL_EXACT_MODE_KERNEL_PAYLOAD.json",
    "moments": PACKAGE / "certificates/BERGER_VALIDATED_FLAT_BUMP_MOMENT_ENCLOSURES.json",
    "profiles": PACKAGE / "certificates/BERGER_EXACT_DETECTOR_SMEARINGS_AND_ADVANCED_COVECTORS.json",
    "switches": PACKAGE / "certificates/BERGER_EXACT_NORMALIZED_EMITTER_SWITCH_PROFILES.json",
    "spectral": PACKAGE / "certificates/BERGER_PETER_WEYL_FORM_LAPLACIAN_ENGINE.json",
    "maxwell_tail": PACKAGE / "certificates/BERGER_MAXWELL_ENERGY_GRAPH_NORM_TAIL.json",
    "massive_constant": PACKAGE / "certificates/BERGER_MASSIVE_RECOIL_FINITE_SLAB_ENERGY_CONSTANT.json",
    "dual_norms": PACKAGE / "certificates/BERGER_DOWNSTREAM_MAXWELL_DETECTOR_DUAL_NORMS.json",
}
SOURCE_FILES = [
    Path(__file__),
    PACKAGE / "berger_recoil_reality_folded_stream.py",
    PACKAGE / "verify_berger_recoil_reality_folded_shell_stream_adapter.py",
    PACKAGE / "tests/test_berger_recoil_reality_folded_stream.py",
    PACKAGE / "tests/test_berger_recoil_reality_folded_shell_stream_adapter.py",
    SCHEMA,
    REPORT,
]
TWO_J = 6
VALIDATION_MASS_SQUARED = RationalInterval(Fraction(1), Fraction(2))
VALIDATION_COUPLINGS = {0: Fraction(1), 1: Fraction(1)}
PARTITION_COUNT = 2
RADICAL_BITS = 80
OUTWARD_BITS = 96


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _payload_hash(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _load() -> dict[str, dict[str, Any]]:
    return {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}


def _tail_radii_after_two_j6(
    values: dict[str, dict[str, Any]],
) -> dict[tuple[int, int], Fraction]:
    detector_duals = {
        index: Fraction(row["detector_energy_dual_norm_upper"])
        for index, row in enumerate(values["dual_norms"]["detector_dual_norms"])
    }
    source_norms = {
        index: Fraction(row["normalized_Delta1_H_second_derivative_L1_upper"])
        for index, row in enumerate(
            values["maxwell_tail"]["calculation"]["polarization_bounds"]
        )
    }
    maxwell_tails = {
        source: _graph_tail_upper(norm, TWO_J)
        for source, norm in source_norms.items()
    }
    massive_coefficients = {
        index: (
            Fraction(row["recoil_current_L1_m_inverse_squared_coefficient"]),
            Fraction(row["recoil_current_L1_m_inverse_coefficient"]),
        )
        for index, row in enumerate(values["massive_constant"]["switch_constants"])
    }
    return compose_four_recoil_tail_radii(
        detector_dual_norms=detector_duals,
        maxwell_tail_uppers=maxwell_tails,
        massive_tail_coefficients=massive_coefficients,
        masses={0: Fraction(1), 1: Fraction(1)},
        couplings=VALIDATION_COUPLINGS,
    )


def _raises(callable_value, text: str) -> bool:
    try:
        callable_value()
    except ValueError as error:
        return text in str(error)
    return False


def _partner_mutation_detected(completed: list[dict[str, Any]]) -> bool:
    mutated = deepcopy(completed)
    partner = next(bundle for bundle in mutated if bundle["column"] == TWO_J)
    row = next(item for item in partner["channels"] if item["channel_id"] == "I_000")
    row["coefficient_block_interval"]["real"]["upper"] = str(
        Fraction(row["coefficient_block_interval"]["real"]["upper"]) + 1
    )
    channel_rows = [
        item
        for bundle in mutated
        for item in bundle["channels"]
        if item["channel_id"] == "I_000"
    ]
    try:
        extract_real_channel_column_sum(channel_rows)
    except ValueError as error:
        return "conjugate carrier rectangles" in str(error)
    return False


def build() -> dict[str, Any]:
    values = _load()
    required = {
        "two_j6_binding": "ALL_56_TWO_J6_CHANNEL_COLUMN_BLOCKS_CERTIFIED",
        "direct_gate": "TAIL_AWARE_FOUR_STREAM_STOP_CALLABLE_EXPORTED",
        "first_omitted": "TWO_J4_TO_TWO_J5_DIRECT_CARRIER_CROSSWALK_CERTIFIED",
        "maxwell_tail": "MAXWELL_ENERGY_GRAPH_NORM_TAIL_EXPORTED",
        "massive_constant": "MASSIVE_FINITE_TIME_ENERGY_CONSTANT_EXPORTED",
        "dual_norms": "FOUR_SYMBOLIC_RECOIL_TAIL_RADII_EXPORTED",
    }
    for name, flag in required.items():
        if values[name].get("flags", {}).get(flag) is not True:
            raise AssertionError(f"dependency dropped: {name}.{flag}")

    carriers5 = bind_first_omitted_shell_direct_carriers(
        detector_image_certificate=values["detector_image"],
        cross_window_remainder_certificate=values["cross_remainder"],
        exact_kernel_certificate=values["exact_kernels"],
        first_omitted_shell_certificate=values["first_omitted"],
    )
    prior_completed = values["two_j6_binding"]["completed_columns"]
    representative_lookup = {
        bundle["column"]: bundle["channels"]
        for bundle in prior_completed
        if bundle["column"] <= TWO_J // 2
    }
    calls: list[int] = []

    def certified_representative_replay(two_j, column, direct_carriers):
        del direct_carriers
        if two_j != TWO_J:
            raise ValueError("validation replay is scoped to two_j=6")
        calls.append(column)
        return representative_lookup[column]

    tail_radii = _tail_radii_after_two_j6(values)
    replay = run_reality_folded_shell_stream(
        two_js=[TWO_J],
        carriers=carriers5,
        moment_certificate=values["moments"],
        detector_profile_certificate=values["profiles"],
        switch_certificate=values["switches"],
        spectral_certificate=values["spectral"],
        mass_squared_intervals={
            0: VALIDATION_MASS_SQUARED,
            1: VALIDATION_MASS_SQUARED,
        },
        couplings=VALIDATION_COUPLINGS,
        inverse_berger_volume=RationalInterval.point(1),
        tail_radii_by_two_j={TWO_J: tail_radii},
        goal={"type": "rank_two"},
        partition_count=PARTITION_COUNT,
        radical_bits=RADICAL_BITS,
        outward_bits=OUTWARD_BITS,
        representative_evaluator=certified_representative_replay,
    )
    history = replay["history"][0]
    folded = history["folded_shell"]
    prior_hash = _payload_hash(prior_completed)
    replay_hash = _payload_hash(folded["completed_columns"])
    if calls != [0, 1, 2, 3] or prior_hash != replay_hash:
        raise AssertionError("two_j=6 adapter replay drifted from its certified binding")
    if replay["evaluated_two_js"] != [TWO_J] or len(history["aggregate"]["aggregate_rows"]) != 4:
        raise AssertionError("adapter did not aggregate exactly one complete four-stream shell")
    if history["stop_evaluation"]["lifecycle_status"] != "OPEN":
        raise AssertionError("zero-containing validation replay unexpectedly stopped")

    complete_rows = representative_lookup[0]
    mutation_results = [
        {
            "name": "drop_one_reality_representative_channel",
            "detected": _raises(
                lambda: _validated_representative_rows(
                    two_j=TWO_J, column=0, rows=complete_rows[:-1]
                ),
                "all eight channels",
            ),
        },
        {
            "name": "declare_duplicate_or_noncontiguous_shell_sequence",
            "detected": _raises(
                lambda: run_reality_folded_shell_stream(
                    two_js=[TWO_J, TWO_J],
                    carriers=carriers5,
                    moment_certificate={},
                    detector_profile_certificate={},
                    switch_certificate={},
                    spectral_certificate={},
                    mass_squared_intervals={0: VALIDATION_MASS_SQUARED, 1: VALIDATION_MASS_SQUARED},
                    couplings=VALIDATION_COUPLINGS,
                    inverse_berger_volume=RationalInterval.point(1),
                    tail_radii_by_two_j={TWO_J: tail_radii},
                    goal={"type": "rank_two"},
                    partition_count=PARTITION_COUNT,
                    radical_bits=RADICAL_BITS,
                    outward_bits=OUTWARD_BITS,
                    shell_evaluator=lambda shell, carriers: {},
                ),
                "unique and contiguous",
            ),
        },
        {
            "name": "omit_tail_data_after_declared_shell",
            "detected": _raises(
                lambda: run_reality_folded_shell_stream(
                    two_js=[TWO_J],
                    carriers=carriers5,
                    moment_certificate={},
                    detector_profile_certificate={},
                    switch_certificate={},
                    spectral_certificate={},
                    mass_squared_intervals={0: VALIDATION_MASS_SQUARED, 1: VALIDATION_MASS_SQUARED},
                    couplings=VALIDATION_COUPLINGS,
                    inverse_berger_volume=RationalInterval.point(1),
                    tail_radii_by_two_j={},
                    goal={"type": "rank_two"},
                    partition_count=PARTITION_COUNT,
                    radical_bits=RADICAL_BITS,
                    outward_bits=OUTWARD_BITS,
                    shell_evaluator=lambda shell, carriers: {},
                ),
                "after every declared shell",
            ),
        },
        {
            "name": "alter_one_exact_reality_partner",
            "detected": _partner_mutation_detected(folded["completed_columns"]),
        },
        {
            "name": "identify_hashed_exact_T_carrier_by_mode_label",
            "detected": replay["hashed_exact_T_stream_identification_status"]
            == "NO_CERTIFIED_MAP",
        },
    ]
    if not all(row["detected"] for row in mutation_results):
        raise AssertionError("one or more fail-closed adapter mutations survived")

    boundary = (
        "This exact LOCAL-ALGEBRAIC/LORENTZIAN-CAUSAL interface certificate "
        "exports a reusable contiguous-shell adapter. For each declared shell it "
        "builds and binds all three direct carriers, evaluates only the independent "
        "SU(2) columns, derives every conjugate partner exactly, aggregates all four "
        "detector/source intervals and invokes the fail-closed tail stop before "
        "advancing. An actual carrier-building two_j=6 replay uses the 32 previously "
        "certified direct representative blocks and exactly reproduces all 56 blocks "
        "of BERGER_RECOIL_TWO_J6_REALITY_FOLDED_BINDING. Its aggregation uses exact "
        "unit couplings and unit inverse-volume normalization solely as an interface "
        "fixture; these are not physical Berger parameters. Tail radii are recomputed "
        "after retained two_j=6, and the rank-two stop remains OPEN. The direct carrier "
        "still has NO_CERTIFIED_MAP to the hashed exact-T stream. No physical recoil, "
        "sign, corrected rank, quotient descent, tangent-cone restriction, Bridge 3, "
        "nonlinear observer stability or quantum claim is inferred."
    )
    return {
        "schema": "closed-universe-berger-recoil-reality-folded-shell-stream-adapter-v1",
        "result_id": "BERGER_RECOIL_REALITY_FOLDED_SHELL_STREAM_ADAPTER",
        "setting_id": values["two_j6_binding"]["setting_id"],
        "claim_status": "GENERIC_CONTIGUOUS_REALITY_FOLDED_FOUR_STREAM_ADAPTER_CERTIFIED",
        "atlas_status": "CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {
            name: {
                "path": str(path.relative_to(ROOT)),
                "result_id": values[name]["result_id"],
                "sha256": _sha256(path),
            }
            for name, path in DEPENDENCIES.items()
        },
        "mode_scope": {
            **values["two_j6_binding"]["mode_scope"],
            "carrier": "successive content-addressed direct detector/cross-window/kernel shells with explicit SU(2) reality completion",
            "ell": "arbitrary caller-declared contiguous finite two_j sequence; certified replay at two_j=6",
            "m": "all representation rows in each declared shell",
            "k": "only k=0,...,floor(two_j/2) directly evaluated; all larger k exactly reality-derived",
            "omega": "caller-supplied rational mass-squared intervals; replay uses [1,2] at partition two",
        },
        "adapter_contract": {
            "module": "closed_universe_observers.berger_recoil_reality_folded_stream",
            "shell_callable": "evaluate_reality_folded_feedback_shell",
            "aggregation_callable": "aggregate_reality_folded_shell",
            "stream_callable": "run_reality_folded_shell_stream",
            "shell_sequence": "nonempty unique contiguous extension of all three direct-carrier cutoffs",
            "stop_frequency": "after every evaluated and four-entry-aggregated shell",
            "tail_requirement": "all four nonnegative radii after every declared shell",
            "hashed_exact_T_stream_identification_status": "NO_CERTIFIED_MAP",
        },
        "two_j6_validation_replay": {
            "two_j": TWO_J,
            "representative_columns_called": calls,
            "direct_channel_column_count": folded["direct_channel_column_count"],
            "exact_reality_derived_count": folded["reality_derived_channel_column_count"],
            "total_channel_column_count": sum(len(row["channels"]) for row in folded["completed_columns"]),
            "direct_shell_payload_sha256": history["direct_shell_payload_sha256"],
            "prior_completed_columns_sha256": prior_hash,
            "replayed_completed_columns_sha256": replay_hash,
            "completed_columns_exact_match": prior_hash == replay_hash,
            "real_channel_sums_sha256": _payload_hash(folded["real_channel_sums"]),
            "validation_parameters": {
                "mass_squared_intervals": {"0": VALIDATION_MASS_SQUARED.serialize(), "1": VALIDATION_MASS_SQUARED.serialize()},
                "couplings": {"0": "1", "1": "1"},
                "inverse_volume_interval": RationalInterval.point(1).serialize(),
                "inverse_volume_status": "UNIT_NORMALIZATION_INTERFACE_FIXTURE_NOT_PHYSICAL_BERGER_VOLUME",
                "partition_count": PARTITION_COUNT,
                "radical_bits": RADICAL_BITS,
                "outward_bits": OUTWARD_BITS,
            },
            "aggregate_rows": history["aggregate"]["aggregate_rows"],
            "tail_radii_after_two_j6": {
                f"{detector}{source}": str(tail_radii[(detector, source)])
                for detector, source in sorted(STREAM_KEYS)
            },
            "stop_evaluation": history["stop_evaluation"],
            "final_partial_intervals": replay["final_partial_intervals"],
        },
        "mutation_results": mutation_results,
        "flags": {
            "GENERIC_REALITY_FOLDED_DIRECT_SHELL_EVALUATOR_EXPORTED": True,
            "CONTIGUOUS_SUCCESSIVE_SHELL_STREAM_ADAPTER_EXPORTED": True,
            "ONLY_SU2_INDEPENDENT_COLUMNS_DIRECTLY_EVALUATED": True,
            "FOUR_SHELL_INTERVALS_AGGREGATED_PER_SHELL": True,
            "TAIL_STOP_INVOKED_AFTER_EVERY_EVALUATED_SHELL": True,
            "TWO_J6_ADAPTER_REPLAY_MATCHES_CERTIFIED_BINDING": True,
            "PHYSICAL_MASS_COUPLING_SPECIALIZATION_EXPORTED": False,
            "FOUR_PHYSICAL_RECOIL_INTERVALS_EXPORTED": False,
            "RECOIL_CORRECTED_RESPONSE_RANK_TWO_CERTIFIED": False,
            "TANGENT_CONE_RESTRICTION_EVALUATED": False,
            "NONLINEAR_OBSERVER_STABILITY_CERTIFIED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "AUDIT_AND_ACTIVATE_THE_DEFERRED_EXACT_NUMERICAL_INPUT_CONTRACT_WITHOUT_INVENTING_PHYSICAL_VALUES",
        "claim_boundary": boundary,
        "provenance": {
            "source_commit": "WORKTREE",
            "source_manifest": [
                {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)}
                for path in SOURCE_FILES
            ],
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    rendered = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if args.emit:
        CERTIFICATE.write_text(rendered)
    if args.check and (not CERTIFICATE.exists() or CERTIFICATE.read_text() != rendered):
        raise SystemExit("stale Berger reality-folded shell-stream adapter certificate")
    print("BERGER_RECOIL_REALITY_FOLDED_SHELL_STREAM_ADAPTER generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
