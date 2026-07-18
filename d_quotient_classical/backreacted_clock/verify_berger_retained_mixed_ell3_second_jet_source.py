#!/usr/bin/env python3
"""Independent exact replay of the retained mixed-ell3 order-two source."""

from __future__ import annotations

import json

from d_quotient_classical.backreacted_clock import (
    berger_retained_mixed_ell3_second_jet_redefinition as second,
)


def verify() -> dict:
    value = json.loads(second.OUTPUT.read_text())
    second.validate(value)
    for relative, digest in value["dependency_refs"].items():
        if second.zero._sha256(second.ROOT / relative) != digest:
            raise ValueError(f"dependency digest drifted: {relative}")
    print("BERGER_RETAINED_MIXED_ELL3_SECOND_JET_SOURCE_V1 verification: PASS")
    return value


if __name__ == "__main__":
    verify()
