#!/usr/bin/env python3
"""Exact replay of the retained mixed-ell3 first-jet primitive."""

from __future__ import annotations

import json

from d_quotient_classical.backreacted_clock import (
    berger_retained_mixed_ell3_first_jet_redefinition as first,
)


def verify() -> dict:
    value = json.loads(first.OUTPUT.read_text())
    first.validate(value)
    for name, record in value["dependency_refs"].items():
        if first.zero._sha256(first.ROOT / record["path"]) != record["sha256"]:
            raise ValueError(f"dependency digest drifted: {name}")
    for relative, digest in value["provenance"]["source_manifest"].items():
        if first.zero._sha256(first.ROOT / relative) != digest:
            raise ValueError(f"source digest drifted: {relative}")
    print("BERGER_RETAINED_MIXED_ELL3_FIRST_JET_REDEFINITION_V1 verification: PASS")
    return value


if __name__ == "__main__":
    verify()
