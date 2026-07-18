#!/usr/bin/env python3
"""Independent replay of the reduced vacuum-cylinder Bridge-4 certificate."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUTPUT = HERE / "certificates/VACUUM_CYLINDER_REDUCED_BRIDGE4_HADAMARD.json"
SCHEMA = HERE / "schema/vacuum-cylinder-reduced-bridge4-hadamard-v1.schema.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify() -> dict[str, object]:
    value = json.loads(OUTPUT.read_text())
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(value)

    for record in value["dependencies"].values():
        path = ROOT / record["path"]
        if not path.is_file() or _sha256(path) != record["sha256"]:
            raise ValueError(f"Bridge-4 dependency drifted: {path}")

    expected = {
        "E": (2, 1, 4 * (sp.Symbol("n") + 1)),
        "A": (3, -1, 2 * (sp.Symbol("n") ** 2 - 4)),
        "L": (4, -1, 4 * (sp.Symbol("n") - 1)),
    }
    n = sp.Symbol("n", positive=True, real=True)
    r = sp.Symbol("r", positive=True, real=True)
    t = sp.Symbol("t", real=True)
    for family, (minimum, sign, _) in expected.items():
        row = value["branch_data"][family]
        if row["minimum_energy"] != minimum or row["krein_sign"] != sign:
            raise ValueError(f"{family} branch label drifted")
        j = sp.Matrix([[0, -1 / n], [n, 0]])
        omega = sign * r * sp.Matrix([[0, 1], [-1, 0]])
        if j**2 != -sp.eye(2) or sp.simplify(j.T * omega * j - omega) != sp.zeros(2):
            raise ValueError(f"{family} complex structure replay failed")
        normalization = 1 / sp.sqrt(2 * r * n)
        mode = sp.Matrix([normalization, -sp.I * n * normalization])
        norm = sp.simplify(sp.I * (sp.conjugate(mode).T * omega * mode)[0])
        if norm != sign:
            raise ValueError(f"{family} Krein norm replay failed")
        wightman = sign * sp.exp(-sp.I * n * t) / (2 * r * n)
        causal = -sign * sp.sin(n * t) / (r * n)
        if sp.simplify(sp.diff(wightman, t, 2) + n**2 * wightman) != 0:
            raise ValueError(f"{family} bisolution replay failed")
        if sp.simplify(
            sp.expand_complex(
                wightman - wightman.subs(t, -t) - sp.I * causal
            )
        ) != 0:
            raise ValueError(f"{family} CCR replay failed")

    flags = value["claim_flags"]
    if (
        flags["VACUUM_CYLINDER_REDUCED_BRIDGE4_ACTIVATED"] is not True
        or flags["REDUCED_KREIN_HADAMARD_TWO_POINT_CERTIFIED"] is not True
        or flags["FULL_BV_BRST_HADAMARD_STATE_CERTIFIED"] is not False
        or flags["POSITIVE_GRAVITON_HILBERT_SPACE_CERTIFIED"] is not False
        or value["decision"]["Bridge_4_full_BV"] != "NO_CERTIFIED_MAP"
        or value["decision"]["Bridge_4_Berger"] != "NO_CERTIFIED_MAP"
    ):
        raise ValueError("reduced Bridge-4 boundary replay failed")
    return value


def mutation_guards(value: dict[str, object]) -> None:
    for key in (
        "FULL_BV_BRST_HADAMARD_STATE_CERTIFIED",
        "POSITIVE_GRAVITON_HILBERT_SPACE_CERTIFIED",
        "BERGER_BRIDGE4_CERTIFIED",
    ):
        mutant = deepcopy(value)
        mutant["claim_flags"][key] = True
        try:
            Draft202012Validator(json.loads(SCHEMA.read_text())).validate(mutant)
        except Exception:
            continue
        raise ValueError(f"schema accepted forbidden promotion: {key}")


def main() -> None:
    value = verify()
    mutation_guards(value)
    print("Vacuum-cylinder reduced Bridge-4 independent replay: PASS")


if __name__ == "__main__":
    main()
