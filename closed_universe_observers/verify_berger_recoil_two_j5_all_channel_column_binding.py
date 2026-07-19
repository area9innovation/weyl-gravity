#!/usr/bin/env python3
"""Independently verify the ``two_j=5`` all-channel-column binding ledger."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = PACKAGE / "certificates/BERGER_RECOIL_TWO_J5_ALL_CHANNEL_COLUMN_BINDING.json"
SCHEMA = PACKAGE / "schema/berger-recoil-two-j5-all-channel-column-binding-v1.schema.json"


def main() -> int:
    value = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    rows = [
        channel
        for column in value["base_partition_columns"]
        for channel in column["channels"]
    ]
    expected = {
        (f"I_{a}{b}{c}", k)
        for a in (0, 1)
        for b in (0, 1)
        for c in (0, 1)
        for k in range(6)
    }
    assert len(rows) == 48
    assert {(row["channel_id"], row["column"]) for row in rows} == expected
    zeros = [row for row in rows if row["causal_support_zero"]]
    assert len(zeros) == 24
    assert {row["channel_id"] for row in zeros} == {
        "I_001", "I_010", "I_011", "I_110"
    }
    assert all(
        Fraction(row["coefficient_block_interval"][part]["width"]) == 0
        for row in zeros
        for part in ("real", "imaginary")
    )
    allowed = [row for row in rows if not row["causal_support_zero"]]
    assert len(allowed) == 24
    assert all(row["coefficient_block_contains_zero"] for row in allowed)
    assert all(
        component["strictly_contracts"]
        for row in value["partition2_to_4_column0_refinement"]
        for component in row["components"].values()
    )
    assert all(row["passive_column_count"] == 6 for row in value["per_channel_coverage"])
    assert all(row["columns"] == list(range(6)) for row in value["per_channel_coverage"])
    assert all(
        shape["shape_ready_for_exact_shell_aggregator"]
        and not shape["couplings_supplied"]
        and all(columns == list(range(6)) for columns in shape["feedback_channels"].values())
        for shape in value["shell_aggregator_input_shapes"]
    )
    assert value["evaluation_contract"]["physical_mass_specialization"] is False
    assert value["evaluation_contract"]["hashed_exact_T_two_j138_stream_identification_status"] == "NO_CERTIFIED_MAP"
    for row in value["dependency_refs"].values():
        path = ROOT / row["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == row["sha256"]
    assert value["flags"]["ALL_48_TWO_J5_CHANNEL_COLUMN_BLOCKS_EVALUATED"]
    assert value["flags"]["ALL_CAUSALLY_ALLOWED_TWO_J5_BLOCKS_CONTAIN_ZERO"]
    assert value["flags"]["COLUMN0_ALLOWED_WIDTHS_STRICTLY_CONTRACT_2_TO_4"]
    assert not value["flags"]["TWO_J5_SHELL_SCALARS_WITH_COUPLINGS_EVALUATED"]
    assert not value["flags"]["COMPLETE_ALL_SHELL_PROVIDER_EXPORTED"]
    assert not value["flags"]["PHYSICAL_MASS_SPECIALIZATION_EXPORTED"]
    print("Berger recoil two_j5 all-channel-column binding verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
