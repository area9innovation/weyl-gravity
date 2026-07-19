#!/usr/bin/env python3
"""Independent replay of the cyclic five-current BV cone."""

from __future__ import annotations

import hashlib
import json

from d_quotient_classical.relative import einstein_weyl_relative_cyclic_five_current_cone as producer


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
    data = producer.exact_data()
    rows, pairing = data["row_layout"], data["pairing"]
    if len(rows) != 50 or [sum(row["degree"] == d for row in rows) for d in (-1, 0, 1, 2)] != [5, 20, 20, 5]:
        raise AssertionError("row layout is incomplete")
    if any(rows[row["dual_row"]]["dual_row"] != row["index"] for row in rows):
        raise AssertionError("duality is not involutive")
    matrix = {(term["left_row"], term["right_row"]): int(term["coefficient"]) for term in pairing}
    if len(matrix) != 50 or any(matrix[(j, i)] != -coefficient for (i, j), coefficient in matrix.items()):
        raise AssertionError("odd pairing is not skew and nondegenerate")
    for name, record in value["cyclic_completion"]["generator_records"].items():
        if data["records"][name]["current_sha256"] != record["current_sha256"]:
            raise AssertionError(f"current digest mismatch: {name}")
        if "(-partial)^a" not in record["formal_adjoint_recipe"]:
            raise AssertionError(f"formal-adjoint recipe missing: {name}")
    generated = json.loads(producer.GENERATED.read_text())
    if hashlib.sha256((json.dumps(generated, indent=2, sort_keys=True) + "\n").encode()).hexdigest() != value["generated_layout"]["sha256"]:
        raise AssertionError("generated layout hash mismatch")
    return {"status": "PASS", "rows": 50, "pairing_terms": 50, "generators": 5}


def main() -> None:
    print(json.dumps(verify(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
