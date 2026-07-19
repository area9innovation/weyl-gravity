#!/usr/bin/env python3
"""Independent consumer for the common-slab rank-310 KS transfer."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp

from d_quotient_classical.causal_transfer.abstract_cyclic_causal_transfer import (
    exact_fixture as abstract_fixture,
)
from d_quotient_classical.causal_transfer.nariai_first_differential_bgg_correction import ROOT
from d_quotient_classical.causal_transfer.nariai_rank310_six_block_finite_hpl import (
    exact_fixture as hpl_fixture,
)


OUTPUT = ROOT / "d_quotient_classical/certificates/NARIAI_KS_RANK310_COMMON_SLAB_GREEN_TRANSFER_V1.json"
SCHEMA = ROOT / "d_quotient_classical/schema/nariai-ks-rank310-common-slab-green-transfer-v1.schema.json"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify() -> None:
    value = json.loads(OUTPUT.read_text())
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(value)
    for dependency in value["dependency_refs"].values():
        if _sha(ROOT / dependency["path"]) != dependency["sha256"]:
            raise AssertionError(f"dependency drifted: {dependency['artifact_id']}")
    for relative, digest in value["source_manifest"].items():
        if _sha(ROOT / relative) != digest:
            raise AssertionError(f"source drifted: {relative}")

    a0, a, b = sp.symbols("a0 a b", positive=True)
    inverse_epsilon = sp.diag(-1, a ** -2, b ** -2, b ** -2)
    inverse_zero = sp.diag(-1, a0 ** -2, 1, 1)
    u = sp.diag(1, a0 / a, 1 / b, 1 / b)
    if (u.T * inverse_zero * u - inverse_epsilon).applyfunc(sp.simplify) != sp.zeros(4):
        raise AssertionError("serialized KS fibre transport is not isometric")
    if u.inv() * u != sp.eye(4):
        raise AssertionError("serialized KS fibre transport is not invertible")

    hpl = hpl_fixture()
    if any(hpl["identity_defect_counts"].values()):
        raise AssertionError("finite six-block HPL relations failed")
    if len(hpl["delta_nonzero_blocks"]) != 6:
        raise AssertionError("six-block incidence lost a block")
    if len(hpl["metric_quadratic_cross_corrections"]) != 2:
        raise AssertionError("mandatory metric cross terms were dropped")
    if any(abstract_fixture()["identity_defects"].values()):
        raise AssertionError("abstract causal transfer failed")

    binding = value["natural_geometric_binding"]
    if binding["difference_block_count"] != 6:
        raise AssertionError("geometric binding does not enumerate six blocks")
    if binding["component_expanded_PBW_table_emitted"] is not False:
        raise AssertionError("natural binding was mislabeled as a PBW dump")
    registry = value["operator_registry"]
    expected = {
        ("Delta g", "epsilon_C0", "s_ker_p0", 1),
        ("Delta k", "epsilon_C0", "h_H1", 1),
        ("Delta M", "x_C1", "x_sharp_C1dual", 2),
        ("Delta B", "h_H1", "h_sharp_H1dual", 4),
        ("Delta gsharp", "s_sharp_ker_p0_dual", "epsilon_sharp_C0dual", 1),
        ("Delta ksharp", "h_sharp_H1dual", "epsilon_sharp_C0dual", 1),
    }
    actual = {
        (entry["name"], entry["source"], entry["target"], entry["order_bound"])
        for entry in registry
    }
    if actual != expected:
        raise AssertionError("typed six-block registry drifted")
    conjugation = value["coordinate_conjugation"]
    if "T_epsilon^{-1}" not in conjugation["original_differential"]:
        raise AssertionError("original-coordinate differential conjugation missing")
    flags = value["flags"]
    if flags["KS_COMMON_SLAB_RANK310_GREEN_HOMOTOPY"] is not True:
        raise AssertionError("rank-310 common-slab transfer not promoted")
    for forbidden in (
        "COMPONENT_EXPANDED_PBW_TABLE",
        "KS_NONZERO_WHOLE_CYLINDER_GREEN_THEOREM",
        "NON_EINSTEIN_BACH_FLAT_METRIC_TRANSFER",
        "HADAMARD_STATE",
        "QUANTUM_CLAIM",
    ):
        if flags[forbidden] is not False:
            raise AssertionError(f"forbidden promotion: {forbidden}")
    print("NARIAI_KS_RANK310_COMMON_SLAB_GREEN_TRANSFER_V1: independently verified")


if __name__ == "__main__":
    verify()
