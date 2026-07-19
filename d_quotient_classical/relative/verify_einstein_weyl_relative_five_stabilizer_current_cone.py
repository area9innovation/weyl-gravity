#!/usr/bin/env python3
"""Independent consumer for the five-stabilizer relative current cone."""

from __future__ import annotations

import hashlib
import json

from d_quotient_classical.relative import einstein_weyl_relative_five_stabilizer_current_cone as producer
from d_quotient_classical.relative.einstein_weyl_relative_five_stabilizer_current import (
    current_divergence,
    polarized_euler_source,
    polarized_noether_current,
    stabilizer_action,
    stabilizer_vectors,
)


def verify() -> dict[str, object]:
    value = json.loads(producer.OUTPUT.read_text())
    producer.validate(value)
    for name, artifact in value["dependencies"].items():
        path = producer.ROOT / artifact["path"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != artifact["sha256"]:
            raise AssertionError(f"dependency hash mismatch: {name}")
    for relative, expected in value["provenance"]["source_manifest"].items():
        if hashlib.sha256((producer.ROOT / relative).read_bytes()).hexdigest() != expected:
            raise AssertionError(f"source manifest mismatch: {relative}")
    replay = {}
    for name, vector in stabilizer_vectors().items():
        action = stabilizer_action(vector)
        current = polarized_noether_current(action)
        divergence = current_divergence(current)
        source = polarized_euler_source(action)
        defect = {
            key: divergence.get(key, 0) - source.get(key, 0)
            for key in set(divergence) | set(source)
            if divergence.get(key, 0) != source.get(key, 0)
        }
        if defect:
            raise AssertionError(f"{name} independent divergence defect: {next(iter(defect.items()))}")
        counts = [len(component) for component in current]
        if counts != value["records"][name]["current_component_term_counts"]:
            raise AssertionError(f"{name} current term-count drift")
        replay[name] = {"defects": 0, "current_terms": sum(counts)}
    return {"status": "PASS", "generator_count": len(replay), "replay": replay}


def main() -> None:
    print(json.dumps(verify(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
