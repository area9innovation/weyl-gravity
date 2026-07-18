#!/usr/bin/env python3
"""Focused independent verifier for the row-ID PBW chain-map export."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
PAYLOAD = ROOT / "bridge/einstein_sector/generated/einstein_weyl_compact_product_chain_map_pbw_v1/inclusion.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein-weyl-compact-product-chain-map-pbw-v1.schema.json"


def _load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict), path
    return value


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_sha256(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _unit_entry(entry: dict) -> bool:
    return entry["maximum_order"] == 0 and entry["terms"] == [
        {"word": [], "coefficient_jets": [{"word": [], "coefficient": "1"}]}
    ]


def verify(path: Path = PAYLOAD) -> None:
    payload = _load(path)
    schema = _load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)

    for artifact in payload["dependencies"].values():
        dependency = ROOT / artifact["path"]
        assert dependency.is_file(), dependency
        assert artifact["sha256"] == _sha256(dependency), dependency
    chain = _load(ROOT / payload["dependencies"]["certified_chain_map"]["path"])
    assert chain["result_id"] == "EINSTEIN_WEYL_COMPACT_PRODUCT_COVARIANT_CHAIN_MAP_V1"
    assert chain["chain_map"]["support_local"] is True
    assert chain["chain_map"]["uses_inverse_laplacian_curl_frequency_or_momentum"] is False
    assert chain["chain_map"]["operator_orders"] == {
        "metric_from_E": 2,
        "metric_from_M": 1,
        "maxwell": 0,
        "diff_identity": 2,
    }

    mapping = payload["map"]
    body = {key: mapping[key] for key in ("source_rows", "target_rows", "entries")}
    assert mapping["canonical_sha256"] == _canonical_sha256(body)
    source_rows = mapping["source_rows"]
    target_rows = mapping["target_rows"]
    assert [row["index"] for row in source_rows] == list(range(38))
    assert [row["index"] for row in target_rows] == list(range(40))
    source = {row["row_id"]: row for row in source_rows}
    target = {row["row_id"]: row for row in target_rows}
    assert len(source) == 38 and len(target) == 40
    assert set(target) - set(source) == {"sigma_W", "sigma_W_star"}
    for rows in (source_rows, target_rows):
        for row in rows:
            dual = rows[row["dual_row"]]
            assert dual["dual_row"] == row["index"]
            assert dual["degree"] + row["degree"] == 1
            assert dual["row_id"] == (
                row["row_id"][:-5] if row["row_id"].endswith("_star") else row["row_id"] + "_star"
            )

    entries = mapping["entries"]
    pairs = [(entry["output_row_id"], entry["input_row_id"]) for entry in entries]
    assert len(pairs) == len(set(pairs))
    by_pair = {pair: entry for pair, entry in zip(pairs, entries)}
    for entry in entries:
        output = target[entry["output_row_id"]]
        input_row = source[entry["input_row_id"]]
        assert output["index"] == entry["output_index"]
        assert input_row["index"] == entry["input_index"]
        assert output["degree"] == input_row["degree"]
        words = [tuple(term["word"]) for term in entry["terms"]]
        assert words == sorted(words) and len(words) == len(set(words))
        assert entry["maximum_order"] == max(map(len, words))
        for term in entry["terms"]:
            jets = term["coefficient_jets"]
            jet_words = [tuple(jet["word"]) for jet in jets]
            assert jet_words == sorted(jet_words, key=lambda word: (len(word), word))
            assert len(jet_words) == len(set(jet_words))

    common_identity_ids = [
        row_id for row_id, row in source.items() if row["degree"] in (-1, 0)
    ]
    for row_id in common_identity_ids:
        assert _unit_entry(by_pair[(row_id, row_id)])
        assert sum(output == row_id for output, _input in pairs) == 1
    for axis in range(4):
        row_id = f"A_{axis}_star"
        assert _unit_entry(by_pair[(row_id, row_id)])
    assert _unit_entry(by_pair[("lambda_cov_star", "lambda_cov_star")])
    assert all(output not in {"sigma_W", "sigma_W_star"} for output, _input in pairs)

    metric_outputs = {f"g_{a}{b}_star" for a in range(4) for b in range(a, 4)}
    equation_inputs = {
        row_id for row_id, row in source.items() if row["degree"] == 1
    }
    identity_inputs = {
        row_id for row_id, row in source.items() if row["degree"] == 2
    }
    for entry in entries:
        output_id = entry["output_row_id"]
        if output_id in metric_outputs:
            assert entry["input_row_id"] in equation_inputs
            assert entry["maximum_order"] <= 2
        elif output_id.startswith("c_") and output_id.endswith("_star"):
            assert entry["input_row_id"] in identity_inputs
            assert entry["maximum_order"] <= 2

    assert payload["checks"]["target_q1_composition_replayed"] is False
    assert payload["claim_status"] == "EXACT_PBW_REPRESENTATIVE_TARGET_Q1_REPLAY_PENDING"


if __name__ == "__main__":
    verify()
    print("compact-product Einstein--Weyl row-ID PBW consumer: PASS")
    print("serialized target q1 chain-square replay remains pending")
