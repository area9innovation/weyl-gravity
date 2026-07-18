#!/usr/bin/env python3
"""Independent scope and identity audit for the global rank-310 HPL result."""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_GLOBAL_HPL_RANK310_CAUSAL_VARIATION_V1.json"
SCHEMA = ROOT / "d_quotient_classical/schema/nariai-transverse-global-hpl-rank310-causal-variation-v1.schema.json"


def main() -> None:
    payload = json.loads(OUTPUT.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
    defects = payload["finite_fixture"]["identity_defects"]
    if len(defects) != 14 or any(defects.values()):
        raise AssertionError("cyclic HPL finite audit is incomplete")
    comparison = payload["hpl_normalized_SDR"]["pointwise_geometric_comparison_defects"]
    if set(comparison) != {"inclusion_dot", "projection_dot", "homotopy_dot", "metric_q_dot"}:
        raise AssertionError("geometric comparison coverage drifted")
    if any(comparison.values()):
        raise AssertionError("HPL/geometric comparison failed")
    if "Hdot+Idot" not in payload["rank310_formal_causal_homotopy"]["variation"]:
        raise AssertionError("rank-310 transfer formula drifted")
    if not payload["flags"]["TRANSVERSE_GLOBAL_RANK310_SDR_VARIATION"]:
        raise AssertionError("global SDR variation flag is false")
    if not payload["flags"]["TRANSVERSE_FORMAL_RANK310_CAUSAL_VARIATION"]:
        raise AssertionError("formal causal variation flag is false")
    if payload["flags"]["TRANSVERSE_CAUSAL_TRANSFER"]:
        raise AssertionError("exact causal family was overclaimed")
    print("NARIAI_TRANSVERSE_GLOBAL_HPL_RANK310_CAUSAL_VARIATION_V1: independently verified")


if __name__ == "__main__":
    main()
