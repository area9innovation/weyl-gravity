#!/usr/bin/env python3
"""Solve the complete aligned twist--electric global self-source."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import jsonschema
import sympy as sp

from bridge.einstein_sector.einstein_maxwell_weyl_homogeneous_twist_balanced_second_order import (
    _apply_row,
)
from bridge.einstein_sector.einstein_maxwell_weyl_polar_full_tensor import (
    _generic_rows as _polar_rows,
)


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_global_orbit_self_second_order.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_global_orbit_self_second_order.schema.json"
INPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_global_orbit_self_source_fixture.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _expr(value: str, local: dict[str, sp.Symbol]) -> sp.Expr:
    return sp.factor(sp.sympify(value, locals=local))


def build() -> dict[str, object]:
    source_record = json.loads(INPUT.read_text(encoding="utf-8"))
    if not source_record["classification"]["direct_four_dimensional_source"]:
        raise AssertionError("direct global source input changed")

    position, velocity, charge, time = sp.symbols("A B Q_e t", real=True)
    local = {"A": position, "B": velocity, "Q_e": charge, "t": time}
    sources = {
        block: {name: _expr(value, local) for name, value in rows.items()}
        for block, rows in source_record["projected_action_sources"].items()
    }

    rows, symbols = _polar_rows()
    eigenvalue, momentum, frequency, a_time, mixed, a_space, maxwell = symbols

    l1_fields = {
        a_time: -velocity * charge,
        mixed: sp.Integer(0),
        a_space: velocity * charge,
        maxwell: sp.Integer(0),
    }
    l1_remainders: dict[str, sp.Expr] = {}
    for name, row in rows.items():
        image = sp.factor(
            row.subs({eigenvalue: 2, momentum: 0, frequency: 0, **l1_fields})
        )
        l1_remainders[name] = sp.factor(image + sources["polar_L1"].get(name, 0))
        if l1_remainders[name] != 0:
            raise AssertionError(f"polar L1 correction failed in {name}")

    amplitude = position + velocity * time
    l2_fields = {
        a_time: -sp.Rational(5, 6) * velocity**2,
        mixed: sp.Integer(0),
        a_space: sp.Rational(5, 6) * velocity**2 - sp.Rational(2, 3) * amplitude**2,
        maxwell: -sp.Rational(7, 36) * velocity**2,
    }
    l2_remainders: dict[str, sp.Expr] = {}
    for name, row in rows.items():
        image = _apply_row(
            row.subs({eigenvalue: 6, momentum: 0}),
            l2_fields,
            frequency,
            time,
        )
        l2_remainders[name] = sp.factor(image + sources["polar_L2"].get(name, 0))
        if l2_remainders[name] != 0:
            raise AssertionError(f"polar L2 correction failed in {name}")

    if any(value != 0 for value in sources["axial_L1"].values()):
        raise AssertionError("global self-source acquired an axial L1 component")

    obstruction = sp.factor(4 * velocity**2 - 3 * charge**2)
    expected_l0 = {
        "metric_00": obstruction / 6,
        "metric_01": sp.Integer(0),
        "metric_11": -obstruction / 6,
        "sphere_trace": obstruction / 6,
        "maxwell_0": sp.Integer(0),
        "maxwell_1": sp.Integer(0),
    }
    if set(sources["homogeneous_L0"]) != set(expected_l0) or any(
        sp.factor(sources["homogeneous_L0"][name] - expected_l0[name]) != 0
        for name in expected_l0
    ):
        raise AssertionError("homogeneous obstruction factorization changed")

    return {
        "schema": "einstein-maxwell-weyl-global-orbit-self-second-order-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_GLOBAL_ORBIT_SELF_SECOND_ORDER",
        "result_state": "ALIGNED_TWIST_ELECTRIC_GLOBAL_SELF_SOURCE_EXACTLY_SOLVED_ON_ITS_TAUB_CONE",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "scope": "real aligned ell=1 twist position A, twist velocity B and homogeneous electric tangent Q_e at k=0 on the fixed N=2 magnetic bundle, before final residual quotient",
        "first_order_taub_condition": {
            "equation": "4*B**2-3*Q_e**2=0",
            "normalization_audit": "the twist harmonic is Y_10=cos(theta), with integral Y_10^2=4*pi/3; restoring the omitted current factors gives 2*L*(4*pi/3)*B^2-2*pi*L*Q_e^2=0",
            "constant_twist_position": "A is unconstrained because it has zero time-translation moment map when A and B are aligned",
        },
        "homogeneous_L0": {
            "source_factor": str(obstruction),
            "source_rows": {name: str(value) for name, value in expected_l0.items()},
            "zero_frequency_linear_operator": "zero on the homogeneous (C,K,U) coefficient block",
            "verdict": "OBSTRUCTED off 4*B**2=3*Q_e**2; identically zero on that cone",
        },
        "second_order_correction": {
            "homogeneous_L0": {"C2": "0", "K2": "0", "U2": "0"},
            "polar_L1": {
                "A_t2": str(l1_fields[a_time]),
                "B2": "0",
                "C_t2": str(l1_fields[a_space]),
                "U2": "0",
                "all_eight_row_remainders": {name: str(value) for name, value in l1_remainders.items()},
            },
            "axial_L1": {"source": "identically zero", "correction": "zero"},
            "polar_L2": {
                "A_t2": str(l2_fields[a_time]),
                "B2": "0",
                "C_t2": str(l2_fields[a_space]),
                "U2": str(l2_fields[maxwell]),
                "all_eight_row_remainders": {name: str(value) for name, value in l2_remainders.items()},
            },
        },
        "classification": {
            "complete_aligned_global_self_source_classified": True,
            "electric_twist_exceptional_polar_L1_source_removable": True,
            "twist_self_polar_L2_source_removable": True,
            "global_self_second_order_extendible_iff_taub_condition": True,
            "full_global_extra_orbit_coefficient_explicit": False,
        },
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "input": {"path": str(INPUT.relative_to(ROOT)), "sha256": _sha256(INPUT)},
        },
        "claim_boundary": "This theorem closes the aligned global/global self-source only. It does not add extra-primary self-products or global-extra cross-products and therefore does not yet make the complete certified global-extra orbit coefficient-explicit.",
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_global_orbit_self_second_order --check",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_global_orbit_self_second_order.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_global_orbit_self_second_order",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    payload = build()
    jsonschema.Draft202012Validator(json.loads(SCHEMA.read_text(encoding="utf-8"))).validate(payload)
    if arguments.write:
        OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    elif json.loads(OUTPUT.read_text(encoding="utf-8")) != payload:
        raise AssertionError("global-orbit second-order certificate is stale")
    print("EINSTEIN_MAXWELL_WEYL_GLOBAL_ORBIT_SELF_SECOND_ORDER: PASS")


if __name__ == "__main__":
    main()
