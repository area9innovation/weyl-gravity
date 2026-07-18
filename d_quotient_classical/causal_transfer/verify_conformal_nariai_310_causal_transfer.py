#!/usr/bin/env python3
"""Independent consumer for the conformal Nariai all-row transfer."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp

from d_quotient_classical.causal_transfer.nariai_first_differential_bgg_correction import ROOT


OUTPUT = ROOT / "d_quotient_classical/certificates/CONFORMAL_NARIAI_310_CAUSAL_TRANSFER_V1.json"
SCHEMA = ROOT / "d_quotient_classical/schema/conformal-nariai-310-causal-transfer-v1.schema.json"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify() -> None:
    value = json.loads(OUTPUT.read_text())
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(value)
    dependencies = {}
    for name, record in value["dependency_refs"].items():
        path = ROOT / record["path"]
        if _sha(path) != record["sha256"]:
            raise AssertionError(f"dependency drifted: {record['artifact_id']}")
        dependencies[name] = json.loads(path.read_text())
    for relative, digest in value["source_manifest"].items():
        if _sha(ROOT / relative) != digest:
            raise AssertionError(f"source drifted: {relative}")
    if dependencies["finite_conformal_BV_transport"]["flags"]["G3_OPEN_BACKGROUND_CLASS"] is not True:
        raise AssertionError("finite conformal BV map unavailable")
    if dependencies["nariai_all_row_causal_control"]["flags"]["NARIAI_REPAIRED_310_GREEN_HOMOTOPY"] is not True:
        raise AssertionError("Nariai all-row homotopy unavailable")
    if dependencies["nariai_all_row_causal_control"]["flags"]["NARIAI_METRIC_DESCENT_RECOVERS_ENDPOINT"] is not True:
        raise AssertionError("Nariai metric descent unavailable")
    if dependencies["bach_flat_parent_stability"]["flags"]["BACH_FLAT_PARENT_RELATIVE_G3_CLASS"] is not True:
        raise AssertionError("parent stability unavailable")

    r, a = sp.symbols("r a", nonzero=True, real=True)
    tangent = sp.Matrix([[r, 0, 0], [0, 1, 0], [0, -a, 1]])
    cotangent = tangent.inv().T
    odd = sp.zeros(6)
    odd[:3, 3:] = sp.eye(3)
    odd[3:, :3] = -sp.eye(3)
    full = sp.diag(tangent, cotangent)
    if sp.simplify(full.T * odd * full - odd) != sp.zeros(6):
        raise AssertionError("finite BV map is not canonical")
    r1, r2, a1, a2 = sp.symbols("r1 r2 a1 a2", nonzero=True, real=True)
    t1 = tangent.subs({r: r1, a: a1})
    t2 = tangent.subs({r: r2, a: a2})
    composed = tangent.subs({r: r1 * r2, a: a1 + a2})
    if sp.simplify(t2 * t1 - composed) != sp.zeros(3):
        raise AssertionError("finite conformal group law failed")
    record = value["finite_BV_canonical_map"]
    if record["finite_fixture_tangent_matrix"] != [[str(x) for x in row] for row in tangent.tolist()]:
        raise AssertionError("tangent fixture drifted")
    if record["finite_fixture_cotangent_matrix"] != [[str(x) for x in row] for row in cotangent.tolist()]:
        raise AssertionError("cotangent fixture drifted")

    radius = Fraction(value["background_class"]["conformal_radius"])
    omega_interval = [Fraction(item) for item in value["background_class"]["Omega_interval"]]
    deviation = Fraction(value["background_class"]["max_spatial_ADM_deviation"])
    if radius != Fraction(1, 9) or omega_interval != [Fraction(8, 9), Fraction(10, 9)]:
        raise AssertionError("conformal radius arithmetic drifted")
    if deviation != Fraction(19, 81) or not deviation < Fraction(1, 4):
        raise AssertionError("conformal class is outside parent ADM ball")
    consumer = value["nonconstant_consumer"]
    if Fraction(consumer["lapse_deviation_sup"]) != Fraction(1, 10):
        raise AssertionError("consumer lapse drifted")
    if Fraction(consumer["spatial_ADM_deviation_sup"]) != Fraction(21, 100):
        raise AssertionError("consumer spatial deviation drifted")
    if not Fraction(1, 10) < radius:
        raise AssertionError("consumer outside conformal class")

    if not all(value["exact_checks"].values()):
        raise AssertionError("serialized exact check failed")
    required = (
        "G3_OPEN_CONFORMAL_NARIAI_CLASS", "METRIC_BACH_GREEN_HOMOTOPY_ON_CONFORMAL_CLASS",
        "RANK_310_GREEN_HOMOTOPY_ON_CONFORMAL_CLASS", "RANK_310_SDR_ON_CONFORMAL_CLASS",
        "METRIC_DESCENT_ON_CONFORMAL_CLASS",
    )
    if any(value["flags"][name] is not True for name in required):
        raise AssertionError("required conformal-class promotion missing")
    forbidden = (
        "ALL_BACH_FLAT_ADM_BALL_METRIC_THEOREM", "TRANSVERSE_BACH_FLAT_DEFORMATIONS",
        "FIXED_UNTRANSFORMED_GAUGE_FERMION", "UNIFORM_HIGHER_SOBOLEV_ESTIMATES",
        "HADAMARD_STATE", "NONLINEAR_EXTENSION", "QUANTUM_CLAIM",
    )
    if any(value["flags"][name] is not False for name in forbidden):
        raise AssertionError("claim boundary overpromoted")
    print("CONFORMAL_NARIAI_310_CAUSAL_TRANSFER_V1: independently verified")


if __name__ == "__main__":
    verify()
