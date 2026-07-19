#!/usr/bin/env python3
"""Independent structural audit of the relative current/cofiber assembly."""

from __future__ import annotations

import hashlib
import json

from d_quotient_classical.relative import einstein_weyl_relative_current_cofiber_assembly as producer


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

    assembly = value["unary_assembly"]
    if assembly["mapping_cofiber_rows"] != sum(assembly["mapping_cofiber_degree_dimensions"]):
        raise AssertionError("mapping cofiber row arithmetic failed")
    if assembly["current_cone_rows"] != sum(assembly["current_cone_degree_dimensions"]):
        raise AssertionError("current cone row arithmetic failed")
    if assembly["assembled_rows"] != assembly["mapping_cofiber_rows"] + assembly["current_cone_rows"]:
        raise AssertionError("assembled row arithmetic failed")

    obstruction = dependencies["direct_f2_obstruction"]
    defect = dependencies["arity_two_defect"]
    if obstruction["classification"]["smooth_periodic_full_domain_f2_exists"] is not False:
        raise AssertionError("f2 obstruction was not imported")
    if defect["checks"]["strict_arity_two_defect_zero"] is not False:
        raise AssertionError("nonzero defect was lost")
    if value["classification"]["full_relative_arity_two_morphism_constructed"] is not False:
        raise AssertionError("charge receiver was mislabeled as a full morphism")
    if value["projection_argument"]["unary_operator"] != "q1_prime=q1_Weyl direct_sum d_H":
        raise AssertionError("the block-diagonal hypothesis is not explicit")
    return {
        "status": "PASS",
        "assembled_rows": assembly["assembled_rows"],
        "charges": len(value["homotopy_moment_map_square"]["charge_basis"]),
        "direct_f2_repaired": False,
    }


def main() -> None:
    print(json.dumps(verify(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
