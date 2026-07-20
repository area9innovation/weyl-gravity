#!/usr/bin/env python3
"""Independent exact replay of the relative deformation classification.

This verifier does not import the producer. It reconstructs every displayed
form, congruence, signature wall, and typed auxiliary embedding directly.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any

import sympy as sp

try:
    from local_bv.schema_validation import validate_instance
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from local_bv.schema_validation import validate_instance


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUTPUT = (
    HERE
    / "certificates/"
    "RELATIVE_EINSTEIN_WEYL_PAIRING_DEFORMATION_CLASSIFICATION.json"
)
SCHEMA = (
    HERE
    / "schema/"
    "relative-einstein-weyl-pairing-deformation-classification-v1.schema.json"
)
SOURCES = (
    "relative_einstein_weyl_pairing_deformation_classification.py",
    "relative_einstein_weyl_pairing_deformation_classification_certificate.py",
    "verify_relative_einstein_weyl_pairing_deformation_classification.py",
    "schema/relative-einstein-weyl-pairing-deformation-classification-v1.schema.json",
    "tests/test_relative_einstein_weyl_pairing_deformation_classification.py",
    "../reports/relative-einstein-weyl-pairing-deformation-classification.md",
)


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def _zero(matrix: sp.Matrix) -> bool:
    return all(sp.factor(sp.cancel(value)) == 0 for value in matrix)


def _matrix_strings(matrix: sp.Matrix) -> list[list[str]]:
    return [[sp.sstr(sp.factor(value)) for value in row] for row in matrix.tolist()]


def _pin_replay(value: dict[str, Any]) -> None:
    pin = value["input_pin"]
    prefix = subprocess.check_output(
        ["git", "rev-parse", "--show-prefix"], cwd=ROOT, text=True
    ).strip()
    blob = subprocess.check_output(
        ["git", "show", f"{pin['commit']}:{prefix}{pin['path']}"],
        cwd=ROOT,
    )
    source = json.loads(blob)
    if (
        hashlib.sha256(blob).hexdigest() != pin["sha256"]
        or source.get("result_id") != pin["result_id"]
        or source["claim_flags"][
            "ACTION_COMPATIBLE_CYCLIC_PUSHFORWARD_OBSTRUCTED_GENERICALLY"
        ]
        is not True
    ):
        raise ValueError("independent terminal-obstruction pin failed")


def _expected() -> dict[str, dict[str, Any]]:
    lam = sp.symbols("lambda", real=True)
    axial_E = sp.diag(lam, 2)
    axial_W = sp.Matrix([[lam, 3 * lam], [3 * lam, 2]])
    axial_delta = sp.diag(0, 9 * lam)
    axial_S = sp.Matrix([[1, -3], [0, 1]])
    polar_E = sp.Matrix([[1, -2], [-2, 2 * lam]])
    polar_W = sp.Matrix([[4, -3 * lam - 2], [-3 * lam - 2, 8 * lam]])
    polar_delta = sp.diag(
        0, sp.Rational(3, 4) * (lam - 2) * (3 * lam + 2)
    )
    polar_S = sp.Matrix(
        [[sp.Rational(1, 2), (3 * lam - 2) / 4], [0, 1]]
    )
    return {
        "axial": {
            "E": axial_E,
            "W": axial_W,
            "delta": axial_delta,
            "S": axial_S,
            "wall": 9 * lam - 2,
            "aux": sp.Integer(2),
            "J": sp.Matrix([[1, 0], [0, 0], [0, 1]]),
            "wall_dets": ["-lambda", "0", "lambda"],
        },
        "polar": {
            "E": polar_E,
            "W": polar_W,
            "delta": polar_delta,
            "S": polar_S,
            "wall": (lam - 2) * (9 * lam - 2) / 4,
            "aux": 2 * (lam - 2),
            "J": sp.Matrix([[sp.Rational(1, 2), -1], [0, 0], [0, 1]]),
            "wall_dets": ["-4", "0", "4"],
        },
    }


def _replay_sectors(value: dict[str, Any]) -> None:
    lam = sp.symbols("lambda", real=True)
    t = sp.symbols("t", real=True)
    rows = {row["sector"]: row for row in value["sector_classification"]}
    expected = _expected()
    if set(rows) != set(expected):
        raise ValueError("independent sector census failed")
    for name, data in expected.items():
        row = rows[name]
        E, W, delta, S = (
            data["E"],
            data["W"],
            data["delta"],
            data["S"],
        )
        if (
            row["Einstein_form"] != _matrix_strings(E)
            or row["Weyl_q_form"] != _matrix_strings(W)
            or row["minimal_target_pairing_repair"]["Delta"]
            != _matrix_strings(delta)
            or row["minimal_target_pairing_repair"]["cyclic_map_S"]
            != _matrix_strings(S)
        ):
            raise ValueError(f"{name} exact matrix mutation detected")
        if not _zero(S.T * (W + delta) * S - E):
            raise ValueError(f"{name} target congruence failed")
        if not _zero(S.T * W * S - (E - delta)):
            raise ValueError(f"{name} source congruence failed")
        extended = sp.diag(W, sp.Matrix([[data["aux"]]]))
        auxiliary = row["minimal_physical_auxiliary_repair"]
        if (
            auxiliary["extended_target_form"] != _matrix_strings(extended)
            or auxiliary["auxiliary_pairing"]
            != sp.sstr(sp.factor(data["aux"]))
            or auxiliary["inclusion_J"] != _matrix_strings(data["J"])
            or not _zero(data["J"].T * extended * data["J"] - E)
        ):
            raise ValueError(f"{name} typed auxiliary embedding failed")
        if int(delta.rank()) != 1:
            raise ValueError(f"{name} minimal rank failed")
        family = W + sp.diag(0, t)
        wall_dets = [
            sp.sstr(sp.factor(family.subs(t, data["wall"] + shift).det()))
            for shift in (-1, 0, 1)
        ]
        if (
            wall_dets != data["wall_dets"]
            or row["wall_mutations"]["determinants"] != wall_dets
        ):
            raise ValueError(f"{name} signature wall failed")
        fixture = (W + delta).subs(lam, 6)
        if (
            fixture[0, 0] <= 0
            or fixture.det() <= 0
            or row["minimal_target_pairing_repair"][
                "repaired_inertia_lambda_ge_6"
            ]
            != [2, 0, 0]
        ):
            raise ValueError(f"{name} positive-cone fixture failed")


def verify_payload(value: dict[str, Any]) -> None:
    errors = validate_instance(value, _load(SCHEMA))
    if errors:
        raise ValueError(f"relative deformation schema failed: {errors}")
    _pin_replay(value)
    _replay_sectors(value)
    if (
        value["global_deformation_theorem"]["minimal_pairing_change_rank"] != 1
        or value["global_deformation_theorem"][
            "contractible_auxiliary_verdict"
        ]
        != "NO_EFFECT_ON_COHOMOLOGY_INERTIA"
        or value["quadratic_action_disposition"][
            "standard_action_preserving_repair_class"
        ]
        != "EMPTY"
        or value["coefficient_gate"][
            "pairing_changed_reduced_matched_insertions_authorized"
        ]
        is not False
        or value["claim_flags"]["RELATIVE_QME_RESTORED"] is not False
    ):
        raise ValueError("independent changed-theory boundary failed")
    manifest = {
        path: hashlib.sha256((HERE / path).read_bytes()).hexdigest()
        for path in SOURCES
    }
    if value["provenance"]["source_manifest"] != manifest:
        raise ValueError("relative deformation source manifest drifted")


def verify() -> dict[str, Any]:
    value = _load(OUTPUT)
    verify_payload(value)
    print("relative Einstein--Weyl pairing deformation independent replay: PASS")
    return value


if __name__ == "__main__":
    verify()
