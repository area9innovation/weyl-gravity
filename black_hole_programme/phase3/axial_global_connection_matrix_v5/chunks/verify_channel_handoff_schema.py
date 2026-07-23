#!/usr/bin/env python3
"""Validate the frozen v6 channel handoff contract without inventing data."""
from __future__ import annotations

import json
import hashlib
import math
import struct
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

from jsonschema import Draft202012Validator


HERE = Path(__file__).resolve().parent
SCHEMA = HERE / "channel-handoff-v6.schema.json"
HANDOFF = HERE / "channel-handoff-v6.json"
ROOT = HERE.parents[3]


def load_validator() -> Draft202012Validator:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


def validate(document: dict) -> None:
    errors = sorted(load_validator().iter_errors(document), key=lambda e: list(e.path))
    if errors:
        path = ".".join(str(part) for part in errors[0].path) or "root"
        raise ValueError(f"{path}: {errors[0].message}")
    basis = document["basis"]
    raw, public = basis["raw_horizon_order"], basis["public_horizon_order"]
    if [raw[i] for i in basis["public_index_to_raw_index"]] != public:
        raise ValueError("basis: public/raw horizon crosswalk mismatch")
    if [public[i] for i in basis["raw_index_to_public_index"]] != raw:
        raise ValueError("basis: raw/public horizon crosswalk mismatch")

    cells = document["cells"]
    parent_lo, parent_hi = map(Fraction, document["parent_cell"]["omega_interval"])
    cursor = parent_lo
    unresolved = []
    replayed_witnesses: set[str] = set()
    for index, cell in enumerate(cells):
        if cell["cell_id"] != f"q{index}":
            raise ValueError("cells: ids are not ordered q0,q1,...")
        lo, hi = map(Fraction, cell["omega_interval"])
        if lo != cursor or hi <= lo:
            raise ValueError("cells: gap, overlap, or reversed interval")
        if Fraction(cell["center"]) != (lo + hi) / 2:
            raise ValueError("cells: wrong exact center")
        if Fraction(cell["radius"]) != (hi - lo) / 2:
            raise ValueError("cells: wrong exact radius")
        cursor = hi
        if cell["disposition"] == "CERTIFIED":
            if cell["validated_payload"] is None or cell["shortfall"] is not None:
                raise ValueError("cells: certified cell lacks a clean payload")
            _validate_payload(cell["validated_payload"], replayed_witnesses)
        else:
            unresolved.append(cell["cell_id"])
            if cell["validated_payload"] is not None or cell["shortfall"] is None:
                raise ValueError("cells: unresolved cell must be fail-closed")
    if cursor != parent_hi:
        raise ValueError("cells: exact cover does not reach parent upper bound")

    state = document["parent_classification"]
    all_resolved = not unresolved
    if state["all_cells_resolved"] != all_resolved:
        raise ValueError("parent_classification: wrong resolved flag")
    if state["exceptional_or_unresolved_cells"] != unresolved:
        raise ValueError("parent_classification: wrong unresolved-cell ledger")
    if state["parent_rank_inertia_promoted"] != all_resolved:
        raise ValueError("parent_classification: invalid parent promotion")
    expected_status = "CERTIFIED" if all_resolved else "SCOPED_SHORTFALL"
    if document["status"] != expected_status:
        raise ValueError("root: status does not match cell dispositions")


def _validate_payload(payload: dict, replayed_witnesses: set[str]) -> None:
    full = payload["connection"]["complex_6_by_3"]
    for name, selector in (("Cminus_3_by_3", (0, 1, 4)), ("Cplus_3_by_3", (2, 3, 5))):
        if payload["connection"][name] != [full[i] for i in selector]:
            raise ValueError(f"connection: {name} is not the frozen row projection")
    if payload["connection"]["realified_12_by_6"] != _realify(full):
        raise ValueError("connection: realified matrix does not match complex matrix")

    forms = payload["endpoint_forms"]
    expected = _complex_matrix_add(
        forms["GHplus_outward"], forms["gplus_pullback"],
        _complex_matrix_neg(forms["gminus_pullback"]),
    )
    defect = forms["conservation"]["defect"]
    _verify_structural_witness(
        forms["conservation"]["structural_identity_witness"],
        replayed_witnesses,
    )
    for i in range(3):
        for j in range(3):
            for part in ("re", "im"):
                if not _affine_contains(defect[i][j][part], expected[i][j][part]):
                    raise ValueError("endpoint_forms: conservation defect is not enclosed")
                lo, hi = _remainder(defect[i][j][part])
                center = float(Fraction(defect[i][j][part]["center"]))
                linear = abs(float(Fraction(defect[i][j][part]["linear"])))
                if center + lo - linear > 0.0 or center + hi + linear < 0.0:
                    raise ValueError("endpoint_forms: defect does not contain zero")
    for witness in payload["classification_witnesses"]["inertia"].values():
        if witness["positive"] + witness["negative"] + witness["zero"] != 3:
            raise ValueError("classification_witnesses: inertia does not sum to three")


def _safe_path(relative: str) -> Path:
    path = Path(relative)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError("structural witness: unsafe path")
    resolved = (ROOT / path).resolve()
    if ROOT.resolve() not in resolved.parents:
        raise ValueError("structural witness: path escapes root")
    return resolved


def _verify_structural_witness(reference: dict, replayed: set[str]) -> None:
    artifact_path = _safe_path(reference["path"])
    verifier_path = _safe_path(reference["verifier_path"])
    if not artifact_path.is_file() or not verifier_path.is_file():
        raise ValueError("structural witness: artifact or verifier missing")
    if hashlib.sha256(artifact_path.read_bytes()).hexdigest() != reference["sha256"]:
        raise ValueError("structural witness: artifact hash mismatch")
    if hashlib.sha256(verifier_path.read_bytes()).hexdigest() != (
        reference["verifier_sha256"]
    ):
        raise ValueError("structural witness: verifier hash mismatch")
    artifact = json.loads(artifact_path.read_text())
    if artifact.get("result_id") != reference["result_id"]:
        raise ValueError("structural witness: result id mismatch")
    claim = artifact
    for key in reference["certified_claim_path"]:
        if not isinstance(claim, dict) or key not in claim:
            raise ValueError("structural witness: certified claim path missing")
        claim = claim[key]
    if claim is not True:
        raise ValueError("structural witness: imported conservation claim is not true")
    command = reference["replay_command"]
    if command[0] != "python" or Path(command[1]).as_posix() != (
        Path(reference["verifier_path"]).as_posix()
    ):
        raise ValueError("structural witness: replay command/verifier mismatch")
    key = reference["verifier_sha256"] + ":" + reference["sha256"]
    if key not in replayed:
        completed = subprocess.run(
            [sys.executable, *command[1:]],
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=120,
            check=False,
        )
        if completed.returncode != 0:
            raise ValueError(
                "structural witness: independent replay failed: "
                + completed.stdout[-500:]
                + completed.stderr[-500:]
            )
        replayed.add(key)


def _float(bits: str) -> float:
    value = struct.unpack(">d", int(bits, 16).to_bytes(8, "big"))[0]
    if not math.isfinite(value):
        raise ValueError("nonfinite interval endpoint")
    return value


def _bits(value: float) -> str:
    return f"{struct.unpack('>Q', struct.pack('>d', value))[0]:016x}"


def _rational(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def _remainder(value: dict) -> tuple[float, float]:
    lo, hi = (_float(bits) for bits in value["remainder"])
    if lo > hi:
        raise ValueError("reversed interval remainder")
    return lo, hi


def _scalar_neg(value: dict) -> dict:
    lo, hi = _remainder(value)
    return {
        "center": _rational(-Fraction(value["center"])),
        "linear": _rational(-Fraction(value["linear"])),
        "remainder": [_bits(-hi), _bits(-lo)],
    }


def _scalar_add(*values: dict) -> dict:
    center = sum((Fraction(value["center"]) for value in values), Fraction())
    linear = sum((Fraction(value["linear"]) for value in values), Fraction())
    bounds = [_remainder(value) for value in values]
    return {
        "center": _rational(center),
        "linear": _rational(linear),
        "remainder": [_bits(sum(lo for lo, _ in bounds)), _bits(sum(hi for _, hi in bounds))],
    }


def _affine_contains(outer: dict, inner: dict) -> bool:
    if Fraction(outer["center"]) != Fraction(inner["center"]):
        return False
    if Fraction(outer["linear"]) != Fraction(inner["linear"]):
        return False
    olo, ohi = _remainder(outer)
    ilo, ihi = _remainder(inner)
    return olo <= ilo and ihi <= ohi


def _complex_matrix_neg(matrix: list) -> list:
    return [
        [
            {"re": _scalar_neg(value["re"]), "im": _scalar_neg(value["im"])}
            for value in row
        ]
        for row in matrix
    ]


def _complex_matrix_add(*matrices: list) -> list:
    return [
        [
            {
                "re": _scalar_add(*(matrix[i][j]["re"] for matrix in matrices)),
                "im": _scalar_add(*(matrix[i][j]["im"] for matrix in matrices)),
            }
            for j in range(len(matrices[0][0]))
        ]
        for i in range(len(matrices[0]))
    ]


def _realify(matrix: list) -> list:
    rows, cols = len(matrix), len(matrix[0])
    return [
        [
            (
                matrix[i][j]["re"] if i < rows and j < cols
                else _scalar_neg(matrix[i][j - cols]["im"]) if i < rows
                else matrix[i - rows][j]["im"] if j < cols
                else matrix[i - rows][j - cols]["re"]
            )
            for j in range(2 * cols)
        ]
        for i in range(2 * rows)
    ]


def main() -> int:
    load_validator()
    if not HANDOFF.exists():
        print("PASS schema; HANDOFF_NOT_POPULATED")
        return 0
    try:
        validate(json.loads(HANDOFF.read_text()))
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"REFUSED: {exc}")
        return 3
    print("PASS schema and populated handoff")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
