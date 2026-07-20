#!/usr/bin/env python3
"""Independent verifier for the regular-graph obstruction and endpoint descent."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys

try:
    from local_bv.schema_validation import validate_instance
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from local_bv.schema_validation import validate_instance

try:
    from .berger_regular_graph_intertwiner_endpoint_descent import (
        DEPENDENCIES,
        endpoint_source_pullback_replay,
        regular_graph_principal_replay,
        validate,
    )
    from .berger_regular_graph_intertwiner_endpoint_descent_certificate import (
        HERE,
        OUTPUT,
        build_certificate,
    )
except ImportError:
    from berger_regular_graph_intertwiner_endpoint_descent import (
        DEPENDENCIES,
        endpoint_source_pullback_replay,
        regular_graph_principal_replay,
        validate,
    )
    from berger_regular_graph_intertwiner_endpoint_descent_certificate import (
        HERE,
        OUTPUT,
        build_certificate,
    )


def verify() -> dict[str, object]:
    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    if payload != build_certificate():
        raise ValueError("regular graph/endpoint certificate does not reproduce")
    schema = json.loads(
        (
            HERE
            / "schema/berger-regular-graph-intertwiner-endpoint-descent-v1.schema.json"
        ).read_text(encoding="utf-8")
    )
    errors = validate_instance(payload, schema)
    if errors:
        raise ValueError(f"regular graph/endpoint schema failed: {errors}")
    validate(payload)
    for name, path in DEPENDENCIES.items():
        if payload["dependency_refs"][name]["sha256"] != hashlib.sha256(
            path.read_bytes()
        ).hexdigest():
            raise ValueError(f"regular graph/endpoint dependency drift: {name}")
    if regular_graph_principal_replay()["nondegenerate_graph_exists"]:
        raise ValueError("regular graph obstruction replay failed")
    if not endpoint_source_pullback_replay()["all_pass"]:
        raise ValueError("endpoint source pullback replay failed")
    mutant = deepcopy(payload)
    mutant["claim_flags"]["BERGER_26_ROW_BRST_HADAMARD"] = True
    try:
        validate(mutant)
    except ValueError:
        pass
    else:
        raise ValueError("BRST Hadamard overpromotion was accepted")
    return payload


def main() -> int:
    verify()
    print("BERGER REGULAR GRAPH/ENDPOINT independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
