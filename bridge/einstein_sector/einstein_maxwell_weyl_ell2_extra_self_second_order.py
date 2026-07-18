#!/usr/bin/env python3
"""Invert every nonstabilizer block in the canonical C4 extra self-source."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp

from bridge.einstein_sector.einstein_maxwell_weyl_axial_operator import _generic_rows as _axial_rows
from bridge.einstein_sector.einstein_maxwell_weyl_polar_full_tensor import _action_operator as _polar_action


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_extra_self_second_order.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_ell2_extra_self_second_order.schema.json"
INPUTS = {
    "source": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_extra_pair_source_fixture.json",
    "cone": ROOT / "d_quotient_classical/certificates/PH_HOMOGENEOUS_TWIST_ELL2_EXTRA_BOUNDED_TANGENT_CONE_V1.json",
    "global_self": ROOT / "bridge/certificates/einstein_maxwell_weyl_global_orbit_self_second_order.json",
    "polar_noether": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_ungauged_noether_lift.json",
}
GRAM = {"a1": sp.Integer(1296), "a2": sp.Rational(208, 3), "p1": sp.Integer(22464), "p2": sp.Integer(12288)}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _expr(value: str) -> sp.Expr:
    return sp.factor(sp.sympify(value, locals={"I": sp.I, "sqrt": sp.sqrt}))


def _vector(values: list[str]) -> sp.Matrix:
    return sp.Matrix([_expr(value) for value in values])


def _axial_action() -> tuple[sp.Matrix, dict[str, sp.Symbol]]:
    rows, symbols = _axial_rows()
    coefficients = sp.Matrix([symbols[name] for name in ("h_t", "h_x", "q_t", "q_x")])
    equations = sp.Matrix([rows[name] for name in ("metric_t", "metric_x", "maxwell_t", "maxwell_x")])
    matrix = (sp.diag(symbols["lambda"], -symbols["lambda"], 1, 1) * equations).jacobian(coefficients)
    return matrix.applyfunc(sp.factor), symbols


def _solve_block(matrix: sp.Matrix, source: sp.Matrix, label: str) -> dict[str, Any]:
    if matrix.det() == 0:
        raise AssertionError(f"unexpected singular extra-self block: {label}")
    correction = (-matrix.inv() * source).applyfunc(sp.factor)
    remainder = (matrix * correction + source).applyfunc(sp.factor)
    if remainder != sp.zeros(matrix.rows, 1):
        raise AssertionError(f"extra-self correction failed: {label}")
    return {
        "source_action_rows": [str(value) for value in source],
        "correction": [str(value) for value in correction],
        "remainder": [str(value) for value in remainder],
    }


def build() -> dict[str, Any]:
    records = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in INPUTS.items()}
    source_record = records["source"]
    if not source_record["classification"]["all_twenty_complex_bilinear_generators_computed"]:
        raise AssertionError("extra-pair source input changed")
    if not records["cone"]["classification"]["complete_common_zero_locus_in_declared_nonzero_extra_carrier"]:
        raise AssertionError("complete cone input changed")
    if not records["global_self"]["classification"]["global_self_second_order_extendible_iff_taub_condition"]:
        raise AssertionError("global self input changed")
    if not records["polar_noether"]["classification"]["ungauged_target_equation_Noether_complex_certified"]:
        raise AssertionError("polar Noether input changed")

    polar, (polar_lambda, polar_k, polar_omega) = _polar_action()
    axial, axial_symbols = _axial_action()
    ledger: dict[str, Any] = {}
    zero_homogeneous: dict[str, list[str]] = {}
    omega_symbol = sp.symbols("Omega", real=True)
    homogeneous = sp.Matrix(
        [
            [0, 0, 0],
            [-omega_symbol**4 / 2, omega_symbol**4 / 2, 0],
            [omega_symbol**4 / 4, -omega_symbol**4 / 4, 0],
            [0, 0, omega_symbol**2],
        ]
    )

    for name, source in source_record["bilinear_sources"].items():
        output_frequency = _expr(source["output_frequency"])
        entry: dict[str, Any] = {
            "output_parity": source["output_parity"],
            "output_frequency": str(output_frequency),
            "blocks": {},
        }
        if source["output_parity"] == "polar":
            homogeneous_source = _vector(source["homogeneous_rows_E00_E11_E22_Maxwell1"])
            if output_frequency == 0:
                zero_homogeneous[name] = [str(value) for value in homogeneous_source]
                entry["homogeneous_L0"] = {
                    "source_rows_E00_E11_E22_Maxwell1": [str(value) for value in homogeneous_source],
                    "disposition": "stabilizer component; assembled with the global source on the Taub cone",
                }
            else:
                if homogeneous_source[0] != 0 or sp.factor(homogeneous_source[1] + 2 * homogeneous_source[2]) != 0:
                    raise AssertionError(f"homogeneous Noether compatibility failed: {name}")
                correction = sp.Matrix(
                    [
                        sp.factor(2 * homogeneous_source[1] / output_frequency**4),
                        0,
                        sp.factor(-homogeneous_source[3] / output_frequency**2),
                    ]
                )
                remainder = (
                    homogeneous.subs(omega_symbol, output_frequency) * correction + homogeneous_source
                ).applyfunc(sp.factor)
                if remainder != sp.zeros(4, 1):
                    raise AssertionError(f"homogeneous sum correction failed: {name}")
                entry["homogeneous_L0"] = {
                    "source_rows_E00_E11_E22_Maxwell1": [str(value) for value in homogeneous_source],
                    "correction_C_K_U": [str(value) for value in correction],
                    "remainder": [str(value) for value in remainder],
                }
            for ell, values in source["action_rows_by_ell"].items():
                eigenvalue = int(ell) * (int(ell) + 1)
                matrix = polar.subs({polar_lambda: eigenvalue, polar_k: 0, polar_omega: output_frequency})
                entry["blocks"][f"polar_L{ell}"] = _solve_block(matrix, _vector(values), f"{name}:polar:L{ell}")
                entry["blocks"][f"polar_L{ell}"]["coefficient_order"] = ["A_t", "B", "C_t", "U"]
        else:
            for ell, values in source["action_rows_by_ell"].items():
                eigenvalue = int(ell) * (int(ell) + 1)
                matrix = axial.subs(
                    {
                        axial_symbols["lambda"]: eigenvalue,
                        axial_symbols["k"]: 0,
                        axial_symbols["omega"]: output_frequency,
                    }
                )
                entry["blocks"][f"axial_L{ell}"] = _solve_block(matrix, _vector(values), f"{name}:axial:L{ell}")
                entry["blocks"][f"axial_L{ell}"]["coefficient_order"] = ["H_t", "H_x", "Q_t", "Q_x"]
        ledger[name] = entry

    mode_order = source_record["mode_order"]
    parities = {
        name: source_record["canonical_representatives"][name]["parity"]
        for name in mode_order
    }
    for index, mode in enumerate(mode_order):
        name = f"zero:{mode}:{mode}"
        source = [_expr(value) for value in zero_homogeneous[name]]
        if sp.factor(source[0] + sp.Rational(16, 15) * GRAM[mode]) != 0:
            raise AssertionError(f"extra Taub normalization changed for {mode}")
        if source[1:] != [0, sp.factor(source[0] / 2), 0]:
            raise AssertionError(f"extra homogeneous row relation changed for {mode}")
        for other in mode_order[index + 1 :]:
            if parities[mode] == parities[other]:
                cross = [_expr(value) for value in zero_homogeneous[f"zero:{mode}:{other}"]]
                if cross != [0, 0, 0, 0]:
                    raise AssertionError(f"off-diagonal homogeneous interference appeared: {mode}/{other}")
            else:
                cross_source = source_record["bilinear_sources"][f"zero:{mode}:{other}"]
                if [_expr(value) for value in cross_source["maxwell_scalar_L0_rows_M0_M1"]] != [0, 0]:
                    raise AssertionError(f"mixed-parity homogeneous Maxwell source appeared: {mode}/{other}")

    return {
        "schema": "einstein-maxwell-weyl-ell2-extra-self-second-order-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_ELL2_EXTRA_SELF_SECOND_ORDER",
        "result_state": "CANONICAL_C4_EXTRA_SELF_SOURCE_COEFFICIENT_EXPLICIT_OUTSIDE_THE_SINGLE_TAUB_COMPONENT",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "scope": "arbitrary complex C4 axial/polar ell=2,m=0,k=0 extra-primary amplitude on the shared-axis representative of the complete global-extra orbit",
        "normalization_bridge": {
            "cone_basis_order": mode_order,
            "cone_Gram_diagonal": [str(GRAM[name]) for name in mode_order],
            "direct_fixture_to_cone_extra_amplitude": "x_raw=sqrt(5/2)*x because the direct P_2 fixture and the cone current use a common 2*pi-factored angular convention",
            "direct_fixture_to_cone_twist_amplitude": "B_raw=sqrt(3/2)*beta",
            "extra_homogeneous_E00_after_reality_and_normalization": "-(2/3)*X",
            "global_homogeneous_E00_after_normalization": "beta**2-Q_e**2/2",
            "combined_E00": "beta**2-Q_e**2/2-(2/3)*X",
            "cone_equation": "beta**2=Q_e**2/2+(2/3)*X",
            "combined_remainder_on_cone": "0",
        },
        "assembly_formula": {
            "sum_diagonal": "multiply the stored raw correction for sum:i:i by (5/16)*x_i**2",
            "sum_offdiagonal": "multiply the stored raw correction for sum:i:j by (5/8)*x_i*x_j",
            "zero_diagonal": "multiply the stored raw correction for zero:i:i by (5/8)*|x_i|**2",
            "zero_offdiagonal": "add (5/8)*(x_i*conjugate(x_j)*K_ij+conjugate(x_i)*x_j*conjugate(K_ij))",
            "negative_frequencies": "take the complex conjugate of every positive-frequency correction",
        },
        "bilinear_correction_ledger": ledger,
        "classification": {
            "complete_C4_extra_self_source_coefficient_explicit": True,
            "all_sum_blocks_solved": True,
            "all_zero_nonstabilizer_blocks_solved": True,
            "only_zero_homogeneous_stabilizer_component_remains": True,
            "zero_homogeneous_component_cancels_with_global_source_on_cone": True,
            "arbitrary_relative_phases_covered": True,
            "causal_retarded_or_all_orders_claim": False,
        },
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for name, path in INPUTS.items()},
        },
        "claim_boundary": "This coefficient-explicit theorem covers the extra/extra self-source on the aligned representative and its SO(3) orbit. Global/global and global-extra mixed corrections are separate inputs to the aggregate smooth-secular theorem. Bounded, causal, all-orders, final residual, observable and quantum claims remain excluded.",
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_ell2_extra_self_second_order --check",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_ell2_extra_self_second_order.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_ell2_extra_self_second_order",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    payload = build()
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
    if arguments.write:
        OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    elif json.loads(OUTPUT.read_text(encoding="utf-8")) != payload:
        raise AssertionError("extra-self second-order certificate is stale")
    print("EINSTEIN_MAXWELL_WEYL_ELL2_EXTRA_SELF_SECOND_ORDER: PASS")


if __name__ == "__main__":
    main()
