#!/usr/bin/env python3
"""Independent dependency and normalization audit for global charge replay."""

from __future__ import annotations

import hashlib
import json

from d_quotient_classical.relative import einstein_weyl_relative_global_five_charge_replay as producer


def verify() -> dict[str, object]:
    value = json.loads(producer.OUTPUT.read_text())
    producer.validate(value)
    dependencies = {}
    for name, artifact in value["dependencies"].items():
        path = producer.ROOT / artifact["path"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != artifact["sha256"]:
            raise AssertionError(f"dependency hash mismatch: {name}")
        dependencies[name] = json.loads(path.read_text())
    for relative, expected in value["provenance"]["source_manifest"].items():
        if hashlib.sha256((producer.ROOT / relative).read_bytes()).hexdigest() != expected:
            raise AssertionError(f"source manifest mismatch: {relative}")
    complete = dependencies["complete_charge_q2"]
    replay = value["complete_replay"]
    if replay["output_basis"] != complete["operation"]["output_basis"] or replay["output_dimension"] != 5:
        raise AssertionError("charge output drifted")
    expected_blocks = set(complete["operation"]["blocks"])
    if {record["block"] for record in replay["blocks"]} != expected_blocks:
        raise AssertionError("complete standard block replay is incomplete")
    if value["classification"]["serialized_coordinate_primitive_global_smoothness_asserted"] is not False:
        raise AssertionError("coordinate primitive was overpromoted")
    if value["classification"]["direct_support_local_map_to_constant_charges"] is not False:
        raise AssertionError("global integral was mislabeled support local")
    return {"status": "PASS", "blocks": len(expected_blocks), "charges": replay["output_dimension"]}


def main() -> None:
    print(json.dumps(verify(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
