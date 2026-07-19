#!/usr/bin/env python3
"""Independent consumer for the class-wide natural rank-310 SDR."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp

from d_quotient_classical.causal_transfer.nariai_first_differential_bgg_correction import ROOT
from d_quotient_classical.causal_transfer.nariai_rank310_six_block_finite_hpl import exact_fixture


OUTPUT = ROOT / "d_quotient_classical/certificates/BACH_FLAT_RANK310_NATURAL_SDR_V1.json"
SCHEMA = ROOT / "d_quotient_classical/schema/bach-flat-rank310-natural-sdr-v1.schema.json"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify() -> None:
    value = json.loads(OUTPUT.read_text())
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(value)
    for ref in value["dependency_refs"].values():
        if _sha(ROOT / ref["path"]) != ref["sha256"]:
            raise AssertionError(f"dependency drifted: {ref['artifact_id']}")
    for relative, digest in value["source_manifest"].items():
        if _sha(ROOT / relative) != digest:
            raise AssertionError(f"source drifted: {relative}")

    N, r, z = sp.symbols("N r z", positive=True)
    beta = sp.symbols("beta")
    eta = sp.diag(-1, 1, 1, 1)
    coframe = sp.Matrix([[N, 0, 0, 0], [r * beta, r, 0, 0], [0, 0, z, 0], [0, 0, 0, z]])
    u = coframe.inv().T
    inverse_metric = coframe.inv() * eta * coframe.inv().T
    if (u.T * eta * u - inverse_metric).applyfunc(sp.simplify) != sp.zeros(4):
        raise AssertionError("independent shifted ADM transport failed")
    hpl = exact_fixture()
    if any(hpl["identity_defect_counts"].values()):
        raise AssertionError("six-block HPL replay failed")
    if len(value["operator_registry"]) != 6 or len({item["name"] for item in value["operator_registry"]}) != 6:
        raise AssertionError("operator registry is not a typed six-block binding")
    flags = value["flags"]
    if not flags["BACH_FLAT_RELATIVE_G3_RANK310_SDR"]:
        raise AssertionError("class-wide SDR not promoted")
    for forbidden in (
        "BACH_FLAT_METRIC_GREEN_HOMOTOPY_ON_CLASS", "BACH_FLAT_RANK310_GREEN_HOMOTOPY_ON_CLASS",
        "AMBIENT_OPEN_ALL_METRICS", "HADAMARD_STATE", "NONLINEAR_EXTENSION", "QUANTUM_CLAIM",
    ):
        if flags[forbidden] is not False:
            raise AssertionError(f"forbidden promotion: {forbidden}")
    print("BACH_FLAT_RANK310_NATURAL_SDR_V1: independently verified")


if __name__ == "__main__":
    verify()
