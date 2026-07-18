#!/usr/bin/env python3
"""Independent consumer for the relative-open Bach-flat parent theorem."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from d_quotient_classical.causal_transfer.nariai_first_differential_bgg_correction import ROOT
from d_quotient_classical.causal_transfer.nariai_yang_mills_parent_green_homotopy import (
    abstract_kernel,
    _serialize_matrix,
)


OUTPUT = ROOT / "d_quotient_classical/certificates/BACH_FLAT_PARENT_GREEN_STABILITY_V1.json"
SCHEMA = ROOT / "d_quotient_classical/schema/bach-flat-parent-green-stability-v1.schema.json"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify() -> None:
    value = json.loads(OUTPUT.read_text())
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(value)
    dependencies = {}
    for name, dependency in value["dependency_refs"].items():
        path = ROOT / dependency["path"]
        if _sha(path) != dependency["sha256"]:
            raise AssertionError(f"dependency drifted: {dependency['artifact_id']}")
        dependencies[name] = json.loads(path.read_text())
    for relative, digest in value["source_manifest"].items():
        if _sha(ROOT / relative) != digest:
            raise AssertionError(f"source drifted: {relative}")

    if dependencies["yang_mills_detour"]["exact_checks"]["left_composition_identity_exact"] is not True:
        raise AssertionError("left detour identity missing")
    if dependencies["yang_mills_detour"]["exact_checks"]["right_composition_identity_exact"] is not True:
        raise AssertionError("right detour identity missing")
    if dependencies["nariai_parent_control"]["flags"]["NARIAI_PARENT_GREEN_HOMOTOPY"] is not True:
        raise AssertionError("Nariai parent control missing")
    if dependencies["abstract_causal_transfer"]["flags"]["ABSTRACT_CAUSAL_TRANSFER_CERTIFIED"] is not True:
        raise AssertionError("abstract causal-transfer theorem missing")

    radius = Fraction(value["background_class"]["radius"])
    lapse = [Fraction(item) for item in value["global_hyperbolicity"]["lapse_interval"]]
    spatial = [Fraction(item) for item in value["global_hyperbolicity"]["spatial_metric_eigenvalue_interval"]]
    speed = Fraction(value["global_hyperbolicity"]["exact_speed_majorant"])
    consumer = value["nonconstant_consumer"]
    if radius != Fraction(1, 4) or lapse != [Fraction(3, 4), Fraction(5, 4)]:
        raise AssertionError("lapse-radius arithmetic drifted")
    if spatial != [Fraction(3, 4), Fraction(5, 4)]:
        raise AssertionError("spatial-radius arithmetic drifted")
    if speed != Fraction(29, 16) or not speed < 2:
        raise AssertionError("causal cone majorant drifted")
    if Fraction(consumer["lapse_deviation_sup"]) != Fraction(1, 10):
        raise AssertionError("consumer lapse bound drifted")
    if Fraction(consumer["spatial_relative_deviation_sup"]) != Fraction(21, 100):
        raise AssertionError("consumer spatial bound drifted")
    if not (Fraction(1, 10) < radius and Fraction(21, 100) < radius):
        raise AssertionError("consumer is outside the declared ball")

    kernel = abstract_kernel()
    if not all(kernel["checks"].values()):
        raise AssertionError("universal parent algebra failed")
    parent = value["universal_parent"]
    if parent["abstract_Q"] != _serialize_matrix(kernel["q"]):
        raise AssertionError("serialized parent differential drifted")
    if parent["backward_witness"] != _serialize_matrix(kernel["witness"]):
        raise AssertionError("serialized parent witness drifted")
    if parent["wave_anticommutator"] != _serialize_matrix(kernel["wave"]):
        raise AssertionError("serialized parent wave drifted")
    if not all(value["exact_checks"].values()):
        raise AssertionError("serialized exact check failed")
    if value["flags"]["BACH_FLAT_PARENT_RELATIVE_G3_CLASS"] is not True:
        raise AssertionError("relative class theorem not promoted")
    if value["flags"]["METRIC_BACH_GREEN_HOMOTOPY_ON_CLASS"] is not False:
        raise AssertionError("metric theorem was overpromoted")
    for forbidden in (
        "OPEN_CLASS_IN_FULL_METRIC_SPACE", "RANK_310_SDR_ON_CLASS",
        "UNIFORM_HIGHER_SOBOLEV_ESTIMATES", "HADAMARD_STATE",
        "NONLINEAR_EXTENSION", "QUANTUM_CLAIM",
    ):
        if value["flags"][forbidden] is not False:
            raise AssertionError(f"forbidden downstream promotion: {forbidden}")
    print("BACH_FLAT_PARENT_GREEN_STABILITY_V1: independently verified")


if __name__ == "__main__":
    verify()
