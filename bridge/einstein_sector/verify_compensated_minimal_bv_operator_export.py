"""Independent consumer verifier for the compensated minimal BV export.

Deliberately does not import either the operator constructor or its exporter.
It reconstructs every matrix from the JSON sparse entries and rechecks the
chain, adjoint, cyclicity, and contraction identities exactly.
"""

from __future__ import annotations

import argparse
import functools
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = ROOT / "bridge/certificates/compensated_minimal_bv_operator_export.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/compensated_minimal_bv_operator_export.schema.json"


class IndependentOperatorVerificationError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise IndependentOperatorVerificationError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _zero(matrix: sp.MatrixBase) -> bool:
    return sp.SparseMatrix(matrix.applyfunc(sp.simplify)).nnz() == 0


def _parse_matrices(payload: dict[str, Any]) -> tuple[dict[str, sp.SparseMatrix], dict[str, sp.Symbol]]:
    symbols = {name: sp.Symbol(name, nonzero=name in {"c1", "alpha", "v"}) for name in payload["symbols"]}
    allowed = set(symbols.values())
    matrices: dict[str, sp.SparseMatrix] = {}
    for name, record in payload["matrices"].items():
        shape = record.get("shape")
        entries = record.get("entries")
        _require(
            isinstance(shape, list) and len(shape) == 2 and all(isinstance(x, int) and x >= 0 for x in shape),
            f"invalid shape: {name}",
        )
        _require(isinstance(entries, list), f"invalid entry list: {name}")
        seen: set[tuple[int, int]] = set()
        parsed: dict[tuple[int, int], sp.Expr] = {}
        previous = (-1, -1)
        for item in entries:
            _require(isinstance(item, list) and len(item) == 3, f"invalid sparse entry: {name}")
            row, column, expression = item
            _require(isinstance(row, int) and isinstance(column, int) and isinstance(expression, str), f"invalid sparse entry types: {name}")
            _require(0 <= row < shape[0] and 0 <= column < shape[1], f"out-of-bounds entry: {name}")
            _require((row, column) > previous, f"entries are not canonically sorted: {name}")
            _require((row, column) not in seen, f"duplicate entry: {name}")
            value = sp.sympify(expression, locals=symbols)
            _require(value.free_symbols <= allowed, f"undeclared symbol in {name}")
            _require(value != 0, f"explicit zero in {name}")
            _require(str(sp.factor(value)) == expression, f"noncanonical expression in {name}[{row},{column}]")
            seen.add((row, column))
            parsed[(row, column)] = value
            previous = (row, column)
        body = {"shape": shape, "entries": entries}
        digest = hashlib.sha256(json.dumps(body, separators=(",", ":"), sort_keys=True).encode("utf-8")).hexdigest()
        _require(record.get("sha256") == digest, f"canonical matrix hash mismatch: {name}")
        matrices[name] = sp.SparseMatrix(shape[0], shape[1], parsed)
    return matrices, symbols


@functools.lru_cache(maxsize=2)
def load_verified_export(path: Path = DEFAULT_INPUT) -> tuple[dict[str, Any], dict[str, sp.SparseMatrix], dict[str, sp.Symbol]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    for key in schema["required"]:
        _require(key in payload, f"export is missing {key}")
    _require(payload["schema"] == schema["$id"], "schema id mismatch")
    _require(payload["schema_sha256"] == _sha256(SCHEMA_PATH), "schema hash mismatch")
    _require(payload["dependency_tags"] == ["LOCAL-ALGEBRAIC"], "dependency tags changed")
    _require(payload["symbols"] == ["p0", "p1", "p2", "p3", "c1", "alpha", "v"], "symbol inventory changed")
    _require(
        payload["formal_adjoint"] == {"p0": "-p0", "p1": "-p1", "p2": "-p2", "p3": "-p3"},
        "formal adjoint changed",
    )
    expected_matrices = set(schema["properties"]["matrices"]["required"])
    _require(set(payload["matrices"]) == expected_matrices, "matrix inventory mismatch")
    expected_order = [
        {"name": "ghosts", "start": 0, "stop": 5, "degree": -1},
        {"name": "fields", "start": 5, "stop": 16, "degree": 0},
        {"name": "antifields", "start": 16, "stop": 27, "degree": 1},
        {"name": "ghost_antifields", "start": 27, "stop": 32, "degree": 2},
    ]
    _require(payload["coordinate_order"] == expected_order, "coordinate order changed")

    for item in [payload["provenance"], *payload["inputs"].values()]:
        candidate = ROOT / item.get("generator_path", item.get("path", ""))
        _require(candidate.is_file(), f"provenance path is missing: {candidate}")
        _require(item.get("generator_sha256", item.get("sha256")) == _sha256(candidate), f"provenance hash mismatch: {candidate}")

    matrices, symbols = _parse_matrices(payload)
    expected_shapes = {
        "metric_operator": (10, 10), "field_map": (11, 11),
        "original_action_hessian": (11, 11), "field_gram": (11, 11),
        "ghost_gram": (5, 5), "gauge": (11, 5), "hessian": (11, 11),
        "noether": (5, 11), "q": (32, 32), "pairing": (32, 32),
        "inclusion": (32, 28), "pi_cl": (28, 32), "homotopy": (32, 32),
        "reduced_q": (28, 28), "reduced_pairing": (28, 28),
    }
    _require(all(matrices[name].shape == shape for name, shape in expected_shapes.items()), "matrix shape mismatch")

    metric = matrices["metric_operator"]
    field_map = matrices["field_map"]
    field_gram = matrices["field_gram"]
    ghost_gram = matrices["ghost_gram"]
    gauge = matrices["gauge"]
    hessian = matrices["hessian"]
    noether = matrices["noether"]
    q = matrices["q"]
    pairing = matrices["pairing"]
    inclusion = matrices["inclusion"]
    projection = matrices["pi_cl"]
    homotopy = matrices["homotopy"]
    reduced_q = matrices["reduced_q"]

    _require(_zero(hessian[:10, :10] - metric) and _zero(hessian[10:11, :]), "Hessian block does not reproduce K_EW")
    expected_original = field_map[:10, :].T * field_gram[:10, :10] * metric * field_map[:10, :]
    _require(_zero(matrices["original_action_hessian"] - expected_original), "original-field Hessian transformation failed")
    _require(_zero(hessian * gauge), "H R != 0")
    _require(_zero(gauge.T * field_gram * hessian), "Noether identity failed")

    p_flip = {symbols[name]: -symbols[name] for name in ("p0", "p1", "p2", "p3")}
    expected_noether = -ghost_gram.inv() * gauge.subs(p_flip, simultaneous=True).T * field_gram
    _require(_zero(noether - expected_noether), "Noether block is not the declared formal adjoint")

    block_q = sp.zeros(32)
    block_q[5:16, 0:5] = gauge
    block_q[16:27, 5:16] = hessian
    block_q[27:32, 16:27] = noether
    _require(_zero(q - block_q), "full q does not equal its exported blocks")
    _require(_zero(q * q), "q^2 != 0")
    _require(pairing.rank() == 32, "full BV pairing is degenerate")
    _require(_zero(q.subs(p_flip, simultaneous=True).T * pairing + pairing * q), "formal cyclicity failed")

    _require(_zero(projection * inclusion - sp.eye(28)), "pi_cl i != 1")
    _require(_zero(inclusion * projection - (sp.eye(32) - q * homotopy - homotopy * q)), "contraction identity failed")
    _require(_zero(homotopy * homotopy), "s^2 != 0")
    _require(_zero(homotopy * inclusion), "s i != 0")
    _require(_zero(projection * homotopy), "pi_cl s != 0")
    _require(_zero(reduced_q - projection * q * inclusion), "reduced q mismatch")
    _require(_zero(q * inclusion - inclusion * reduced_q), "inclusion chain map failed")
    _require(_zero(projection * q - reduced_q * projection), "projection chain map failed")
    expected_reduced_pairing = inclusion.T * pairing * inclusion
    _require(_zero(matrices["reduced_pairing"] - expected_reduced_pairing), "reduced pairing mismatch")
    _require(expected_reduced_pairing.rank() == 28, "reduced pairing is degenerate")

    flags = payload["claim_flags"]
    _require(flags == {
        "actual_sparse_entries_exported": True,
        "source_fingerprints_reproduced": True,
        "independent_consumer_verification_in_this_artifact": False,
        "characteristic_cohomology_in_this_artifact": False,
        "physical_symplectic_pairing_in_this_artifact": False,
        "lorentzian_causal_claim": False,
        "quantum_claim": False,
    }, "claim flags changed")
    return payload, matrices, symbols


def verify(path: Path = DEFAULT_INPUT) -> None:
    load_verified_export(path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", type=Path, default=DEFAULT_INPUT)
    args = parser.parse_args()
    verify(args.verify)


if __name__ == "__main__":
    main()
