#!/usr/bin/env python3
"""Independent replay of the non-cylinder mixed-detour pilot."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
DEFAULT = ROOT / "d_quotient_classical/certificates/MINKOWSKI_DOUBLED_ADJOINT_TRACTOR_MIXED_DETOUR.json"
DEFAULT_CONSUMER = ROOT / "d_quotient_classical/certificates/MINKOWSKI_DOUBLED_ADJOINT_TRACTOR_CAUSAL_TRANSFER_CONSUMER.json"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _zero(a: sp.Matrix) -> bool:
    return all(sp.simplify(value) == 0 for value in a)


def _sharp(a: sp.Matrix, pairing: sp.Matrix) -> sp.Matrix:
    return pairing.inv() * a.T * pairing


def verify(path: Path, consumer_path: Path) -> None:
    data = json.loads(path.read_text())
    consumer = json.loads(consumer_path.read_text())
    for dependency in data["dependency_refs"].values():
        target = ROOT / dependency["path"]
        if _sha(target) != dependency["sha256"]:
            raise AssertionError(f"dependency drifted: {target}")
    for source in data["source_manifest"].values():
        target = ROOT / source["path"]
        if _sha(target) != source["sha256"]:
            raise AssertionError(f"source drifted: {target}")

    # Rebuild the flavor calculation without importing the producer.
    d = sp.Matrix([[0, 0], [1, 0]])
    lam = sp.Matrix([[0, 1], [0, 0]])
    a = sp.diag(1, -1)
    u = sp.Matrix([[1, 1], [0, 1]])
    u_inv = sp.Matrix([[1, -1], [0, 1]])
    h = u_inv.T * u_inv
    ub = sp.kronecker_product(u, sp.eye(2))
    ubi = sp.kronecker_product(u_inv, sp.eye(2))
    q = ub * sp.kronecker_product(a, d) * ubi
    l = ub * sp.kronecker_product(a, lam) * ubi
    j = sp.kronecker_product(h, sp.Matrix([[0, 1], [-1, 0]]))
    sigma = sp.kronecker_product(sp.eye(2), sp.diag(1, -1))
    if not _zero(q * q):
        raise AssertionError("independent mixed nilpotency failed")
    if not _zero(q * l + l * q - sp.eye(4)):
        raise AssertionError("independent mixed chain homotopy failed")
    if not _zero(_sharp(l, j) - sigma * l * sigma):
        raise AssertionError("independent mixed adjoint failed")
    if q[:2, 2:4] == sp.zeros(2):
        raise AssertionError("independent mixed coupling vanished")

    if not all(data["exact_checks"].values()):
        raise AssertionError("proof exact check dropped")
    if data["flags"]["SECOND_NONCYLINDER_DETOUR_CONSUMER"] is not True:
        raise AssertionError("second consumer flag dropped")
    if consumer["SDR"]["transfer_direction"] != "FULL_TO_ENDPOINT_DESCENT":
        raise AssertionError("consumer direction drifted")
    if consumer["complexes"]["full"]["degree_ranks"] != [30, 120, 120, 30]:
        raise AssertionError("doubled parent ranks drifted")
    if consumer["complexes"]["endpoint"]["degree_ranks"] != [8, 18, 18, 8]:
        raise AssertionError("doubled endpoint ranks drifted")
    if consumer["flags"]["CAUSAL_TRANSFER_REPLAYED"] is not True:
        raise AssertionError("generic consumer replay flag dropped")
    for forbidden in (
        "G3_OPEN_BACKGROUND_CLASS",
        "INTERACTING_MIXED_FIELD_THEORY",
        "HIGHER_SPIN_DISCOVERY",
        "TIMELIKE_BOUNDARY_VERSION",
        "HADAMARD_TRANSFER",
        "QUANTUM_CLAIM",
    ):
        if data["flags"][forbidden] is not False:
            raise AssertionError(f"forbidden pilot claim promoted: {forbidden}")
    print("MINKOWSKI_DOUBLED_ADJOINT_TRACTOR pilot independent verification: PASS")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", nargs="?", type=Path, default=DEFAULT)
    parser.add_argument("--consumer", type=Path, default=DEFAULT_CONSUMER)
    args = parser.parse_args()
    verify(args.path, args.consumer)


if __name__ == "__main__":
    main()
