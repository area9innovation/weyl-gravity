#!/usr/bin/env python3
"""Independent replay of the abstract cyclic causal-transfer package."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
DEFAULT = ROOT / "d_quotient_classical/certificates/ABSTRACT_CYCLIC_CAUSAL_TRANSFER.json"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sharp(a: sp.Matrix, j_domain: sp.Matrix, j_codomain: sp.Matrix) -> sp.Matrix:
    return j_domain.inv() * a.T * j_codomain


def _is_zero(a: sp.Matrix) -> bool:
    return all(sp.simplify(entry) == 0 for entry in a)


def verify(path: Path) -> None:
    data = json.loads(path.read_text())
    for dependency in data["dependency_refs"].values():
        target = ROOT / dependency["path"]
        if _sha(target) != dependency["sha256"]:
            raise AssertionError(f"dependency digest drifted: {target}")
    for source in data["source_manifest"].values():
        target = ROOT / source["path"]
        if _sha(target) != source["sha256"]:
            raise AssertionError(f"source digest drifted: {target}")

    d = sp.Matrix([[0, 0], [1, 0]])
    q = sp.zeros(4)
    q[2, 0] = q[3, 1] = 1
    i = sp.zeros(4, 2)
    i[0, 0] = i[2, 1] = 1
    p = sp.zeros(2, 4)
    p[0, 0] = p[1, 2] = 1
    h = sp.zeros(4)
    h[1, 3] = 1
    endpoint = sp.Matrix([[0, 1], [0, 0]])
    transferred = h + i * endpoint * p
    if not _is_zero(q * h + h * q - (sp.eye(4) - i * p)):
        raise AssertionError("independent SDR identity failed")
    if not _is_zero(q * transferred + transferred * q - sp.eye(4)):
        raise AssertionError("independent transferred homotopy failed")

    j_e = sp.Matrix([[0, 1], [1, 0]])
    j_c = sp.Matrix([[0, 0, 1, 0], [0, 0, 0, 1], [1, 0, 0, 0], [0, 1, 0, 0]])
    if not _is_zero(_sharp(i, j_e, j_c) - p):
        raise AssertionError("independent cyclic SDR adjoint failed")
    if not _is_zero(_sharp(transferred, j_c, j_c) - transferred):
        raise AssertionError("independent transferred cyclic adjoint failed")

    n = sp.zeros(4)
    n[0, 1] = 1
    n[3, 2] = -1
    u = sp.eye(4) + n
    u_inverse = sp.eye(4) - n
    if not _is_zero(u * u_inverse - sp.eye(4)):
        raise AssertionError("independent finite shear inverse failed")
    if not _is_zero(_sharp(u, j_c, j_c) - u_inverse):
        raise AssertionError("independent cyclic shear failed")
    q_u = u * q * u_inverse
    lambda_u = u * transferred * u_inverse
    if not _is_zero(q_u * lambda_u + lambda_u * q_u - sp.eye(4)):
        raise AssertionError("independent sheared homotopy failed")

    if not all(data["exact_checks"].values()):
        raise AssertionError("certificate exact check dropped")
    if data["flags"]["ABSTRACT_CAUSAL_TRANSFER_CERTIFIED"] is not True:
        raise AssertionError("abstract theorem not promoted")
    for forbidden in (
        "SECOND_NONCYLINDER_DETOUR_CONSUMER",
        "G3_OPEN_BACKGROUND_CLASS",
        "TIMELIKE_BOUNDARY_VERSION",
        "HADAMARD_TRANSFER",
        "QUANTUM_CLAIM",
    ):
        if data["flags"][forbidden] is not False:
            raise AssertionError(f"forbidden promotion: {forbidden}")
    if "K_Berger" not in data["berger_consumer"]["generator_scope"]:
        raise AssertionError("Berger generator correction absent")
    print("ABSTRACT_CYCLIC_CAUSAL_TRANSFER independent verification: PASS")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", nargs="?", type=Path, default=DEFAULT)
    args = parser.parse_args()
    verify(args.path)


if __name__ == "__main__":
    main()
