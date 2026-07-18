#!/usr/bin/env python3
"""Independent exact replay of the order-two physical primitive."""

from __future__ import annotations

import json

from d_quotient_classical.backreacted_clock import (
    berger_retained_mixed_ell3_second_jet_exact_primitive as primitive,
)


def verify() -> dict:
    value = json.loads(primitive.OUTPUT.read_text())
    primitive.validate(value)
    for relative, digest in value["dependency_refs"].items():
        if primitive.second.zero._sha256(primitive.ROOT / relative) != digest:
            raise ValueError(f"dependency digest drifted: {relative}")
    print("BERGER_RETAINED_MIXED_ELL3_SECOND_JET_EXACT_PRIMITIVE_V1 verification: PASS")
    return value


if __name__ == "__main__":
    verify()
