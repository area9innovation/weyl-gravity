#!/usr/bin/env python3
"""Independent structural audit for the relative observable functor."""

from __future__ import annotations

import hashlib
import json

from d_quotient_classical.relative import relative_residual_observable_functor as producer


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

    triangle = dependencies["linear_triangle"]
    if triangle["acceptance_flags"]["OFF_SHELL_CHAIN_MAP_ALL_BV_ROWS"] is not True:
        raise AssertionError("observable pullback lacks an all-row chain map")
    sectors = value["relative_detectors"]["sectors"]
    if [item["basis_rank"] for item in sectors] != [2, 2, 2, 2]:
        raise AssertionError("relative detector ranks drifted")
    if not all(item["orthogonal_to_einstein_image"] and item["nonradical"] and item["pullback_zero"] for item in sectors):
        raise AssertionError("a detector does not descend to the cofiber")
    if value["classification"]["causal_green_relative_functor"] is not False:
        raise AssertionError("reduced-mode detectors were mislabeled causal")
    return {"status": "PASS", "detector_sectors": len(sectors), "pullback": "CHAIN_MAP", "causal": False}


def main() -> None:
    print(json.dumps(verify(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
