#!/usr/bin/env python3
"""Independently verify the Berger reality-folded shell-stream adapter."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = PACKAGE / "certificates/BERGER_RECOIL_REALITY_FOLDED_SHELL_STREAM_ADAPTER.json"
SCHEMA = PACKAGE / "schema/berger-recoil-reality-folded-shell-stream-adapter-v1.schema.json"


def _payload_hash(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _interval(value: Mapping[str, str]) -> tuple[Fraction, Fraction]:
    lower = Fraction(value["lower"])
    upper = Fraction(value["upper"])
    if lower > upper or Fraction(value["width"]) != upper - lower:
        raise SystemExit("malformed rational interval")
    return lower, upper


def _serialize(value: tuple[Fraction, Fraction]) -> dict[str, str]:
    lower, upper = value
    return {"lower": str(lower), "upper": str(upper), "width": str(upper - lower)}


def _add(*values: tuple[Fraction, Fraction]) -> tuple[Fraction, Fraction]:
    return sum((value[0] for value in values), Fraction(0)), sum(
        (value[1] for value in values), Fraction(0)
    )


def _multiply(
    left: tuple[Fraction, Fraction], right: tuple[Fraction, Fraction]
) -> tuple[Fraction, Fraction]:
    products = [a * b for a in left for b in right]
    return min(products), max(products)


def _scale(
    value: tuple[Fraction, Fraction], scalar: Fraction
) -> tuple[Fraction, Fraction]:
    return _multiply(value, (scalar, scalar))


def _audit_reality(completed: list[dict[str, Any]]) -> None:
    by_column = {bundle["column"]: bundle for bundle in completed}
    if set(by_column) != set(range(7)) or len(completed) != 7:
        raise SystemExit("completed two_j=6 column coverage drifted")
    for column in range(4, 7):
        source = {
            row["channel_id"]: row for row in by_column[6 - column]["channels"]
        }
        partner = {row["channel_id"]: row for row in by_column[column]["channels"]}
        if set(source) != set(partner) or len(partner) != 8:
            raise SystemExit("reality-partner channel coverage drifted")
        for channel, row in partner.items():
            original = source[channel]["coefficient_block_interval"]
            derived = row["coefficient_block_interval"]
            if derived["real"] != original["real"]:
                raise SystemExit("reality partner changed a real interval")
            original_imag = _interval(original["imaginary"])
            derived_imag = _interval(derived["imaginary"])
            if derived_imag != (-original_imag[1], -original_imag[0]):
                raise SystemExit("reality partner is not an exact conjugate")
            if (
                row.get("evaluation_method") != "EXACT_SU2_REALITY_DERIVATION"
                or row.get("direct_backend_evaluated") is not False
                or row.get("reality_source_column") != 6 - column
            ):
                raise SystemExit("reality provenance metadata drifted")


def _aggregate(
    completed: list[dict[str, Any]], detector: int, source: int
) -> dict[str, Any]:
    feedback_rows = []
    coupled = (Fraction(0), Fraction(0))
    for feedback in (0, 1):
        channel = f"I_{detector}{source}{feedback}"
        columns = []
        for bundle in sorted(completed, key=lambda row: row["column"]):
            row = next(item for item in bundle["channels"] if item["channel_id"] == channel)
            columns.append(_interval(row["coefficient_block_interval"]["real"]))
        bare = _add(*columns)
        coupled = _add(coupled, bare)
        feedback_rows.append(
            {
                "feedback_emitter": feedback,
                "passive_column_count": 7,
                "bare_column_sum": _serialize(bare),
                "feedback_coupling_square": "1",
                "coupled_column_sum": _serialize(bare),
            }
        )
    shell = _scale(coupled, Fraction(7))
    return {
        "feedback_rows": feedback_rows,
        "source_scaled_sum": _serialize(coupled),
        "peter_weyl_weight": _serialize((Fraction(7), Fraction(7))),
        "shell_interval": _serialize(shell),
    }


def _audit_stop(replay: dict[str, Any]) -> None:
    partial = {
        key: _interval(value)
        for key, value in replay["final_partial_intervals"].items()
    }
    tails = {
        key: Fraction(value)
        for key, value in replay["tail_radii_after_two_j6"].items()
    }
    padded = {
        key: (value[0] - tails[key], value[1] + tails[key])
        for key, value in partial.items()
    }
    determinant = _add(
        _multiply(padded["00"], padded["11"]),
        _scale(_multiply(padded["01"], padded["10"]), Fraction(-1)),
    )
    stop = replay["stop_evaluation"]
    if stop["tail_padded_intervals"] != {
        key: _serialize(value) for key, value in padded.items()
    }:
        raise SystemExit("tail-padded four-stream intervals drifted")
    if stop["witness"]["determinant_interval"] != _serialize(determinant):
        raise SystemExit("rank-two determinant interval drifted")
    if determinant[0] > 0 or determinant[1] < 0 or stop["stop"] is not False:
        raise SystemExit("zero-containing rank-two replay was promoted")


def main() -> int:
    value = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    for ref in list(value["dependency_refs"].values()) + value["provenance"]["source_manifest"]:
        path = ROOT / ref["path"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != ref["sha256"]:
            raise SystemExit(f"content hash drift: {ref['path']}")

    binding_path = ROOT / value["dependency_refs"]["two_j6_binding"]["path"]
    binding = json.loads(binding_path.read_text())
    completed = binding["completed_columns"]
    _audit_reality(completed)
    replay = value["two_j6_validation_replay"]
    completed_hash = _payload_hash(completed)
    if not (
        completed_hash == replay["prior_completed_columns_sha256"]
        == replay["replayed_completed_columns_sha256"]
    ):
        raise SystemExit("two_j=6 completed-column replay hash drifted")
    if _payload_hash(binding["two_j6_real_channel_sums"]) != replay["real_channel_sums_sha256"]:
        raise SystemExit("two_j=6 real-channel sums drifted")

    aggregate_rows = {
        (row["detector"], row["source_preparation"]): row
        for row in replay["aggregate_rows"]
    }
    if set(aggregate_rows) != {(0, 0), (0, 1), (1, 0), (1, 1)}:
        raise SystemExit("four-stream aggregate coverage drifted")
    for detector, source in sorted(aggregate_rows):
        expected = _aggregate(completed, detector, source)
        actual = aggregate_rows[(detector, source)]
        for key in ("feedback_rows", "source_scaled_sum", "peter_weyl_weight", "shell_interval"):
            if actual[key] != expected[key]:
                raise SystemExit(f"independent aggregate mismatch: {detector}{source}.{key}")
        if replay["final_partial_intervals"][f"{detector}{source}"] != expected["shell_interval"]:
            raise SystemExit("single-shell partial interval drifted")
    _audit_stop(replay)

    mutations = {row["name"]: row["detected"] for row in value["mutation_results"]}
    required_mutations = {
        "drop_one_reality_representative_channel",
        "declare_duplicate_or_noncontiguous_shell_sequence",
        "omit_tail_data_after_declared_shell",
        "alter_one_exact_reality_partner",
        "identify_hashed_exact_T_carrier_by_mode_label",
    }
    if set(mutations) != required_mutations or not all(mutations.values()):
        raise SystemExit("fail-closed mutation ledger drifted")
    if replay["validation_parameters"]["inverse_volume_status"] != "UNIT_NORMALIZATION_INTERFACE_FIXTURE_NOT_PHYSICAL_BERGER_VOLUME":
        raise SystemExit("unit-normalization fixture lost its nonphysical boundary")
    print("BERGER_RECOIL_REALITY_FOLDED_SHELL_STREAM_ADAPTER verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
