#!/usr/bin/env python3
"""Exact no-go for cancelling the pure-Weyl anomaly with standard unitary matter."""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
INPUT = HERE / "certificates/REGULATED_REPOSITORY_BV_SLAVNOV_BREAKING.json"
OUTPUT = HERE / "certificates/UNITARY_CONFORMAL_MATTER_CANCELLATION_NO_GO.json"
SCHEMA = HERE / "schema/unitary-conformal-matter-cancellation-no-go-v1.schema.json"

BASIS = ("ANOM_OMEGA_C2", "ANOM_OMEGA_E4")
GRAVITY = (Fraction(199, 30), Fraction(-87, 20))
SPECIES = {
    "real_conformal_scalar": (Fraction(1, 120), Fraction(-1, 360)),
    "Weyl_fermion": (Fraction(1, 40), Fraction(-11, 720)),
    "Dirac_fermion": (Fraction(1, 20), Fraction(-11, 360)),
    "gauge_vector": (Fraction(1, 10), Fraction(-31, 180)),
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _q(value: Fraction) -> dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}


def _scaled(vector: tuple[Fraction, Fraction], scale: int = 720) -> list[int]:
    return [int(scale * entry) for entry in vector]


def build() -> dict[str, Any]:
    breaking = json.loads(INPUT.read_text())
    if (
        breaking.get("result_id") != "REGULATED_REPOSITORY_BV_SLAVNOV_BREAKING"
        or breaking.get("classification", {}).get("status") != "NONTRIVIAL"
        or breaking.get("qme_disposition", {}).get("status")
        != "OBSTRUCTED_STRICT_FIELD_CONTENT"
    ):
        raise ValueError("strict-field-content breaking input drifted")
    imported = tuple(
        Fraction(
            breaking["coefficients"][key]["numerator"],
            breaking["coefficients"][key]["denominator"],
        )
        for key in BASIS
    )
    if imported != GRAVITY:
        raise ValueError("gravity anomaly vector drifted")

    for species, vector in SPECIES.items():
        if vector[0] <= 0 or vector[1] >= 0:
            raise ValueError(f"standard-sign matter cone drifted: {species}")

    scale = 720
    scaled_gravity = _scaled(GRAVITY, scale)
    scaled_species = {name: _scaled(vector, scale) for name, vector in SPECIES.items()}
    if scaled_gravity != [4776, -3132]:
        raise ValueError("integer-normalized gravity vector drifted")

    result = {
        "schema": "quantum-weyl-unitary-conformal-matter-cancellation-no-go-v1",
        "result_id": "UNITARY_CONFORMAL_MATTER_CANCELLATION_NO_GO",
        "result_state": "NO_NONNEGATIVE_STANDARD_UNITARY_FREE_MATTER_CANCELLATION",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "classical_commit": breaking["classical_commit"],
        "basis": list(BASIS),
        "gravity_vector": [_q(value) for value in GRAVITY],
        "matter_generators": {
            name: {
                "statistics_and_reality": {
                    "real_conformal_scalar": "REAL_BOSON_STANDARD_SIGN",
                    "Weyl_fermion": "TWO_COMPONENT_COMPLEX_FERMION_STANDARD_SIGN",
                    "Dirac_fermion": "FOUR_COMPONENT_COMPLEX_FERMION_STANDARD_SIGN",
                    "gauge_vector": "REAL_GAUGE_VECTOR_WITH_STANDARD_BRST_GHOSTS",
                }[name],
                "vector": [_q(value) for value in vector],
            }
            for name, vector in SPECIES.items()
        },
        "cancellation_equations": {
            "variables": ["N_s", "N_W", "N_D", "N_v"],
            "domain": "NONNEGATIVE_REAL_CONE; INTEGER_MULTIPLICITIES_A_SUBSET",
            "rational": [
                "199/30 + N_s/120 + N_W/40 + N_D/20 + N_v/10 = 0",
                "-87/20 - N_s/360 - 11 N_W/720 - 11 N_D/360 - 31 N_v/180 = 0",
            ],
            "integer_scale": scale,
            "integer_rows": [
                [scaled_gravity[0]] + [scaled_species[name][0] for name in SPECIES],
                [scaled_gravity[1]] + [scaled_species[name][1] for name in SPECIES],
            ],
        },
        "separating_witnesses": [
            {
                "functional": [1, 0],
                "gravity_value": _q(GRAVITY[0]),
                "matter_generator_values": {
                    name: _q(vector[0]) for name, vector in SPECIES.items()
                },
                "conclusion": "C2_COORDINATE_STRICTLY_POSITIVE_ON_GRAVITY_PLUS_NONNEGATIVE_MATTER_CONE",
            },
            {
                "functional": [0, -1],
                "gravity_value": _q(-GRAVITY[1]),
                "matter_generator_values": {
                    name: _q(-vector[1]) for name, vector in SPECIES.items()
                },
                "conclusion": "MINUS_E4_COORDINATE_STRICTLY_POSITIVE_ON_GRAVITY_PLUS_NONNEGATIVE_MATTER_CONE",
            },
        ],
        "classification": {
            "solution_set": "EMPTY",
            "strength": "SEPARATING_DUAL_CONE_WITNESS_OVER_NONNEGATIVE_REALS",
            "integer_search_required": False,
            "qme_status": "REMAINS_OBSTRUCTED_IN_DECLARED_MATTER_CLASS",
        },
        "external_coefficient_provenance": {
            "reference": "https://arxiv.org/abs/hep-th/9912122",
            "formula": "c=(N_s+6N_D+12N_v)/120; a=(N_s+11N_D+62N_v)/360; Weyl fermion is one half Dirac",
            "convention_map": "repository E4 coordinate equals -a",
        },
        "dependency": {
            "path": str(INPUT.relative_to(ROOT)),
            "result_id": breaking["result_id"],
            "sha256": _sha256(INPUT),
        },
        "next_gate": "CERTIFIED_WESS_ZUMINO_COMPENSATOR_EXTENSION_OR_NONSTANDARD_NONUNITARY_MATTER_PROPOSAL",
        "claim_boundary": (
            "This exact cone-separation theorem rules out cancellation of the certified pure-Weyl "
            "one-loop local Euclidean BV anomaly by any nonnegative collection of free, massless, "
            "standard-sign real conformal scalars, Weyl or Dirac fermions, and gauge vectors in "
            "the matched anomaly convention. It does not cover interacting fixed points, nonunitary "
            "or wrong-sign fields, higher-spin conformal fields, boundary anomalies, compensator "
            "trivialization, Lorentzian products, or a particle theory."
        ),
    }
    validate(result)
    return result


def validate(value: dict[str, Any]) -> None:
    if (
        value.get("result_id") != "UNITARY_CONFORMAL_MATTER_CANCELLATION_NO_GO"
        or value.get("result_state")
        != "NO_NONNEGATIVE_STANDARD_UNITARY_FREE_MATTER_CANCELLATION"
        or value.get("classification", {}).get("solution_set") != "EMPTY"
        or value.get("classification", {}).get("qme_status")
        != "REMAINS_OBSTRUCTED_IN_DECLARED_MATTER_CLASS"
        or value.get("cancellation_equations", {}).get("integer_rows")
        != [[4776, 6, 18, 36, 72], [-3132, -2, -11, -22, -124]]
        or len(value.get("separating_witnesses", [])) != 2
        or any(
            witness.get("gravity_value", {}).get("numerator", 0) <= 0
            or any(
                item.get("numerator", 0) <= 0
                for item in witness.get("matter_generator_values", {}).values()
            )
            for witness in value.get("separating_witnesses", [])
        )
    ):
        raise ValueError("unitary conformal matter no-go certificate drifted")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = json.dumps(build(), indent=2, sort_keys=True) + "\n"
    if args.emit:
        OUTPUT.write_text(rendered)
    if args.check and (not OUTPUT.exists() or OUTPUT.read_text() != rendered):
        raise SystemExit(f"stale matter cancellation certificate: {OUTPUT}")
    print("UNITARY CONFORMAL MATTER CANCELLATION: EMPTY NONNEGATIVE CONE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
