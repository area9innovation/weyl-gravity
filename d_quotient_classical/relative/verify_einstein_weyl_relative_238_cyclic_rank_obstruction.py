#!/usr/bin/env python3
"""Independent rank replay for the proposed 238-row cyclic carrier."""

from __future__ import annotations

import hashlib
import json

from d_quotient_classical.relative import einstein_weyl_relative_238_cyclic_rank_obstruction as producer


def verify() -> dict[str, object]:
    value = json.loads(producer.OUTPUT.read_text())
    producer.validate(value)
    for name, artifact in value["dependencies"].items():
        path = producer.ROOT / artifact["path"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != artifact["sha256"]:
            raise AssertionError(f"dependency drift: {name}")
    for relative, expected in value["provenance"]["source_manifest"].items():
        if hashlib.sha256((producer.ROOT / relative).read_bytes()).hexdigest() != expected:
            raise AssertionError(f"source drift: {relative}")
    triangle = json.loads(producer.DEPENDENCIES["linear_triangle_components"].read_text())
    carrier = json.loads(producer.DEPENDENCIES["de_rham_carrier"].read_text())
    cofiber = [*triangle["mapping_cofiber"]["degree_dimensions"], 0]
    current = carrier["carrier"]["degree_ranks_minus2_to3"]
    combined = [cofiber[index] + current[index] for index in range(6)]
    deficits = [abs(combined[index] - combined[5-index]) for index in range(3)]
    if combined != [10,45,78,69,31,5] or deficits != [5,14,9] or sum(deficits) != 28:
        raise AssertionError("independent degree-one pairing audit failed")
    return {"status": "PASS", "combined_rows": sum(combined), "rank_deficits": deficits, "minimum_added_rows": 28}


def main() -> None:
    print(json.dumps(verify(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
