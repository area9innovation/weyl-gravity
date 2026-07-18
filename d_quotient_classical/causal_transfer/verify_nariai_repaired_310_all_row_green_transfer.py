#!/usr/bin/env python3
"""Independent consumer for the Nariai 310-row causal-transfer artifact."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from d_quotient_classical.causal_transfer.nariai_first_differential_bgg_correction import ROOT
import d_quotient_classical.causal_transfer.nariai_parent_detour_mapping_cone_repair as repair


OUTPUT = ROOT / "d_quotient_classical/certificates/NARIAI_REPAIRED_310_ALL_ROW_GREEN_TRANSFER_V1.json"
SCHEMA = ROOT / "d_quotient_classical/schema/nariai-repaired-310-all-row-green-transfer-v1.schema.json"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _endpoint() -> repair.Matrix:
    value = repair._zero(4, 4)
    value[0][1] = repair.O.atom("Lambda01")
    value[1][2] = repair.O.atom("Lambda12")
    value[2][3] = repair.O.atom("Lambda23")
    return value


def _replace_once(value: repair.O) -> tuple[repair.O, bool]:
    rules = {
        ("Lambda01", "K"): repair.O.identity(),
        ("K", "Lambda01"): repair.O.identity()
        + (repair.O.atom("Lambda12") * repair.O.atom("B")).scale(-1),
        ("B", "Lambda12"): repair.O.identity()
        + (repair.O.atom("Lambda23") * repair.O.atom("Ksharp")).scale(-1),
        ("Ksharp", "Lambda23"): repair.O.identity(),
    }
    for word, coefficient in value.terms:
        for old, replacement in rules.items():
            for index in range(len(word) - len(old) + 1):
                if word[index:index + len(old)] == old:
                    rest = value + repair.O._from_dict({word: -coefficient})
                    left = repair.O._from_dict({word[:index]: coefficient})
                    right = repair.O._from_dict({word[index + len(old):]: 1})
                    return rest + left * replacement * right, True
    return value, False


def _reduce(value: repair.O) -> repair.O:
    for _ in range(1000):
        value = repair._reduce(value)
        value, changed = _replace_once(value)
        if not changed:
            return repair._reduce(value)
    raise AssertionError("independent endpoint rewrite did not terminate")


def _zero(value: repair.Matrix) -> bool:
    return all(_reduce(entry) == repair.O.zero() for row in value for entry in row)


def verify() -> None:
    value = json.loads(OUTPUT.read_text())
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(value)
    for dependency in value["dependency_refs"].values():
        if _sha(ROOT / dependency["path"]) != dependency["sha256"]:
            raise AssertionError(f"dependency drifted: {dependency['artifact_id']}")
    for relative, digest in value["source_manifest"].items():
        if _sha(ROOT / relative) != digest:
            raise AssertionError(f"source drifted: {relative}")

    dependencies = {
        name: json.loads((ROOT / reference["path"]).read_text())
        for name, reference in value["dependency_refs"].items()
    }
    required_dependency_flags = (
        dependencies["rank_310_cyclic_sdr"]["flags"]["SUPPORT_LOCAL_AUTOMORPHISM_SDR"],
        dependencies["metric_causal_homotopy"]["flags"]["NARIAI_METRIC_CAUSAL_SUPPORT"],
        dependencies["metric_causal_homotopy"]["flags"]["NARIAI_METRIC_ADJOINT_REVERSAL"],
        dependencies["abstract_causal_transfer"]["flags"]["ABSTRACT_CYCLIC_ADJOINT_TRANSFER_CERTIFIED"],
    )
    if required_dependency_flags != (True, True, True, True):
        raise AssertionError("causal/cyclic transfer dependency is incomplete")

    kernel = repair.abstract_kernel()
    endpoint = _endpoint()
    endpoint_defect = repair._add(
        repair._add(
            repair._multiply(kernel["metric_q"], endpoint),
            repair._multiply(endpoint, kernel["metric_q"]),
        ),
        repair._scale(repair._identity(4), -1),
    )
    if not _zero(endpoint_defect):
        raise AssertionError("metric endpoint relation does not normalize to identity")

    transferred = {}
    for coordinate in ("split", "original"):
        prefix = "" if coordinate == "split" else "original_"
        q = kernel[prefix + "q"]
        inclusion = kernel[prefix + "inclusion"]
        projection = kernel[prefix + "projection"]
        homotopy = kernel[prefix + "homotopy"]
        if not repair._matrix_zero(repair._multiply(homotopy, homotopy), relations=True):
            raise AssertionError(f"{coordinate} H^2 != 0")
        if not repair._matrix_zero(repair._multiply(homotopy, inclusion), relations=True):
            raise AssertionError(f"{coordinate} H I != 0")
        if not repair._matrix_zero(repair._multiply(projection, homotopy), relations=True):
            raise AssertionError(f"{coordinate} P H != 0")
        causal = repair._add(
            homotopy,
            repair._multiply(repair._multiply(inclusion, endpoint), projection),
        )
        transferred[coordinate] = causal
        defect = repair._add(
            repair._add(repair._multiply(q, causal), repair._multiply(causal, q)),
            repair._scale(repair._identity(10), -1),
        )
        if not _zero(defect):
            raise AssertionError(f"{coordinate} all-row chain identity failed")
        descent = repair._add(
            repair._multiply(repair._multiply(projection, causal), inclusion),
            repair._scale(endpoint, -1),
        )
        if not repair._matrix_zero(descent, relations=True):
            raise AssertionError(f"{coordinate} metric descent failed")

    conjugated = repair._multiply(
        repair._multiply(kernel["transform"], transferred["split"]),
        kernel["transform_inverse"],
    )
    if not repair._matrix_zero(
        repair._add(transferred["original"], repair._scale(conjugated, -1)),
        relations=True,
    ):
        raise AssertionError("split/original causal homotopies are not conjugate")

    replay = value["formal_replay"]
    if replay["endpoint_homotopy"] != repair._serialize_matrix(endpoint):
        raise AssertionError("serialized endpoint homotopy drifted")
    if replay["split_transferred_homotopy"] != repair._serialize_matrix(transferred["split"]):
        raise AssertionError("serialized split homotopy drifted")
    if replay["original_transferred_homotopy"] != repair._serialize_matrix(transferred["original"]):
        raise AssertionError("serialized original homotopy drifted")

    carrier = value["carrier"]
    if sum(row["rank"] for row in carrier["row_coverage"]) != 310:
        raise AssertionError("row ledger does not sum to 310")
    expected_rows = [
        {
            "index": index,
            "name": name,
            "degree": degree,
            "rank": rank,
            "sector": (
                "metric_field_endpoint"
                if index in (3, 7)
                else "metric_ghost_plus_algebraic_complement"
                if index in (0, 9)
                else "algebraic_parent_cone"
            ),
        }
        for index, (name, degree, rank) in enumerate(
            zip(repair.BLOCK_NAMES, repair.BLOCK_DEGREES, repair.BLOCK_RANKS)
        )
    ]
    if carrier["row_coverage"] != expected_rows:
        raise AssertionError("ordered ten-block row ledger drifted")
    if [sum(row["rank"] for row in carrier["row_coverage"] if row["degree"] == degree) for degree in (-1, 0, 1, 2)] != [15, 140, 140, 15]:
        raise AssertionError("degree ledger drifted")
    if carrier["dropped_rows"]:
        raise AssertionError("a BV row was dropped")
    if not all(value["exact_checks"].values()):
        raise AssertionError("serialized certificate contains a failed check")
    if value["flags"]["NARIAI_REPAIRED_310_GREEN_HOMOTOPY"] is not True:
        raise AssertionError("rank-310 causal theorem not promoted")
    print("NARIAI_REPAIRED_310_ALL_ROW_GREEN_TRANSFER_V1: independently verified")


if __name__ == "__main__":
    verify()
