#!/usr/bin/env python3
import hashlib
import json
from fractions import Fraction

from closed_universe_observers.generate_berger_blockwise_temporal_functional_calculus_preflight import (
    CERTIFICATE,
    DEPENDENCIES,
    ROOT,
    build,
)


def main() -> int:
    value = json.loads(CERTIFICATE.read_text())
    assert value == build()
    for name, path in DEPENDENCIES.items():
        assert value["dependency_refs"][name]["sha256"] == hashlib.sha256(path.read_bytes()).hexdigest()
        assert value["dependency_refs"][name]["result_id"] == json.loads(path.read_text())["result_id"]
        assert value["dependency_refs"][name]["path"] == str(path.relative_to(ROOT))
    audit = value["microphase_remainder_audit"]
    assert Fraction(audit["cosine_geometric_ratio"]) < Fraction(1, 100)
    assert Fraction(audit["sine_geometric_ratio"]) < Fraction(1, 100)
    assert Fraction(audit["Delta1_cosine_microphase_remainder_upper"]) < Fraction(1, 10**17)
    assert value["flags"]["BLOCKWISE_TEMPORAL_FUNCTIONAL_CALCULUS_IMAGE_EXPORTED"] is False
    print("blockwise temporal functional-calculus preflight verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
