#!/usr/bin/env python3
"""Certify the Lorentzian time/spatial form-block signs on Berger modes."""

from __future__ import annotations

import argparse
from math import comb
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp

from closed_universe_observers.generate_berger_peter_weyl_form_laplacian import (
    d_matrix,
    laplacian,
)


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = PACKAGE / "certificates/BERGER_SPACETIME_FORM_BLOCK_SIGN_BRIDGE.json"
SCHEMA = PACKAGE / "schema/berger-spacetime-form-block-sign-bridge-v1.schema.json"
REPORT = PACKAGE / "reports/berger-spacetime-form-block-sign-bridge.md"
DEPENDENCIES = {
    "de_rham": PACKAGE / "certificates/BERGER_PETER_WEYL_FORM_LAPLACIAN_ENGINE.json",
    "kernels": PACKAGE / "certificates/BERGER_FINITE_MODE_MAXWELL_EMITTER_GREEN_KERNELS.json",
    "emitter": PACKAGE / "certificates/BERGER_POLARIZATION_TWO_FORM_EMITTER_HANDOFF.json",
    "coupling_stripped": PACKAGE / "certificates/BERGER_COUPLING_STRIPPED_DETECTOR_SELECTED_PREPARATIONS.json",
}
SOURCE_FILES = [
    Path(__file__),
    PACKAGE / "verify_berger_spacetime_form_block_sign_bridge.py",
    PACKAGE / "tests/test_berger_spacetime_form_block_sign_bridge.py",
    SCHEMA,
    REPORT,
]
AUDIT_MAX_TWO_J = 4


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _dim(two_j: int, degree: int) -> int:
    return (two_j + 1) * comb(3, degree) if 0 <= degree <= 3 else 0


def _spatial_d(two_j: int, degree: int) -> sp.Matrix:
    if 0 <= degree <= 2:
        return d_matrix(two_j, degree)
    return sp.zeros(_dim(two_j, degree + 1), _dim(two_j, degree))


def spacetime_d(two_j: int, degree: int, z: sp.Expr) -> sp.Matrix:
    """d on dt wedge V_(degree-1) direct_sum V_degree."""
    left = _dim(two_j, degree - 1)
    middle = _dim(two_j, degree)
    right = _dim(two_j, degree + 1)
    top = sp.Matrix.hstack(-_spatial_d(two_j, degree - 1), z * sp.eye(middle))
    bottom = sp.Matrix.hstack(sp.zeros(right, left), _spatial_d(two_j, degree))
    return sp.Matrix.vstack(top, bottom)


def spacetime_delta(two_j: int, degree: int, z: sp.Expr, *, wrong_time_sign: bool = False) -> sp.Matrix:
    """delta on dt wedge V_(degree-1) direct_sum V_degree."""
    low = _dim(two_j, degree - 2)
    middle = _dim(two_j, degree - 1)
    high = _dim(two_j, degree)
    top = sp.Matrix.hstack(-_spatial_d(two_j, degree - 2).conjugate().T, sp.zeros(low, high))
    time_sign = -1 if wrong_time_sign else 1
    bottom = sp.Matrix.hstack(time_sign * z * sp.eye(middle), _spatial_d(two_j, degree - 1).conjugate().T)
    return sp.Matrix.vstack(top, bottom)


def _defect_count(matrix: sp.Matrix) -> int:
    return sum(sp.simplify(value) != 0 for value in matrix)


def block_audit(two_j: int, *, wrong_time_sign: bool = False) -> dict[str, Any]:
    z = sp.symbols("z", real=True)
    d_squared = []
    for degree in range(3):
        d_squared.append(_defect_count(spacetime_d(two_j, degree + 1, z) * spacetime_d(two_j, degree, z)))
    delta_squared = []
    for degree in range(2, 5):
        delta_squared.append(
            _defect_count(
                spacetime_delta(two_j, degree - 1, z, wrong_time_sign=wrong_time_sign)
                * spacetime_delta(two_j, degree, z, wrong_time_sign=wrong_time_sign)
            )
        )
    wave_defects = []
    for degree in (1, 2):
        wave = (
            spacetime_delta(two_j, degree + 1, z, wrong_time_sign=wrong_time_sign)
            * spacetime_d(two_j, degree, z)
            + spacetime_d(two_j, degree - 1, z)
            * spacetime_delta(two_j, degree, z, wrong_time_sign=wrong_time_sign)
        )
        expected = sp.diag(
            z**2 * sp.eye(_dim(two_j, degree - 1)) + laplacian(two_j, degree - 1),
            z**2 * sp.eye(_dim(two_j, degree)) + laplacian(two_j, degree),
        )
        wave_defects.append(_defect_count(wave - expected))
    return {
        "two_j": two_j,
        "spacetime_dimensions_by_degree": [
            _dim(two_j, degree - 1) + _dim(two_j, degree) for degree in range(5)
        ],
        "d_squared_defect_counts_degrees_0_to_2": d_squared,
        "delta_squared_defect_counts_degrees_2_to_4": delta_squared,
        "wave_diagonalization_defect_counts_degrees_1_2": wave_defects,
    }


def build() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    required = {
        "de_rham": "GENERIC_FINITE_PETER_WEYL_DE_RHAM_BLOCK_CONSTRUCTOR",
        "kernels": "MODE_CAUCHY_JUMP_AND_ODE_CERTIFIED",
        "emitter": "SPECIFIC_DYNAMICAL_EMITTER_MODEL_SELECTED",
        "coupling_stripped": "COUPLING_STRIPPED_FIXED_PREPARATIONS_EXPORTED",
    }
    for name, flag in required.items():
        if values[name].get("flags", {}).get(flag) is not True:
            raise AssertionError(f"dependency dropped: {name}.{flag}")
    audits = [block_audit(two_j) for two_j in range(AUDIT_MAX_TWO_J + 1)]
    if any(
        any(row[key])
        for row in audits
        for key in (
            "d_squared_defect_counts_degrees_0_to_2",
            "delta_squared_defect_counts_degrees_2_to_4",
            "wave_diagonalization_defect_counts_degrees_1_2",
        )
    ):
        raise AssertionError("spacetime form-block sign audit failed")
    mutation = block_audit(1, wrong_time_sign=True)
    if not any(mutation["wave_diagonalization_defect_counts_degrees_1_2"]):
        raise AssertionError("wrong temporal coderivative sign escaped")

    boundary = (
        "This exact LOCAL-ALGEBRAIC/LORENTZIAN-CAUSAL sign bridge lifts the "
        "authoritative Berger spatial de Rham matrices to the ultrastatic "
        "clock-metric splitting of spacetime forms. For a k-form written as "
        "dt wedge alpha_(k-1)+beta_k, it certifies "
        "d(alpha,beta)=(partial_t beta-d_Sigma alpha,d_Sigma beta) and "
        "delta(alpha,beta)=(-delta_Sigma alpha,partial_t alpha+delta_Sigma "
        "beta). Exact mode audits through two_j=4 give d^2=delta^2=0 and "
        "(d delta+delta d)=diag(partial_t^2+Delta_(k-1),partial_t^2+Delta_k) "
        "for Maxwell one-forms and emitter two-forms; flipping the temporal "
        "coderivative sign is detected. This fixes the component signs and "
        "matches the existing sine-kernel wave convention. It does not "
        "evaluate profile coefficients, time convolutions, massive Green "
        "images, per-shell recoil contractions, four scalar intervals, "
        "tangent-cone restriction, Bridge 3, nonlinear all-orders stability "
        "or a quantum claim."
    )
    return {
        "schema": "closed-universe-berger-spacetime-form-block-sign-bridge-v1",
        "result_id": "BERGER_SPACETIME_FORM_BLOCK_SIGN_BRIDGE",
        "setting_id": values["coupling_stripped"]["setting_id"],
        "claim_status": "EXACT_LORENTZIAN_SPACETIME_D_DELTA_BLOCK_SIGNS_AND_WAVE_DIAGONALIZATION_EXPORTED",
        "atlas_status": "CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {
            name: {
                "path": str(path.relative_to(ROOT)),
                "result_id": values[name]["result_id"],
                "sha256": _sha256(path),
            }
            for name, path in DEPENDENCIES.items()
        },
        "form_split": {
            "spacetime_k_form": "dt wedge alpha_(k-1)+beta_k",
            "lorentzian_pairing": "-<alpha,alpha_prime>_Sigma+<beta,beta_prime>_Sigma",
            "d": "(alpha,beta)->(partial_t beta-d_(k-1) alpha,d_k beta)",
            "delta": "(alpha,beta)->(-d_(k-2)^dagger alpha,partial_t alpha+d_(k-1)^dagger beta)",
            "wave": "d delta+delta d=diag(partial_t^2+Delta_(k-1),partial_t^2+Delta_k)",
            "switch_product_rule": "delta(h(alpha,beta))=h delta(alpha,beta)+(0,partial_t h alpha)",
        },
        "matrix_formulas": {
            "Dhat_k": "[[-d_(k-1), z I_k],[0,d_k]]",
            "Deltahat_k": "[[-d_(k-2)^dagger,0],[z I_(k-1),d_(k-1)^dagger]]",
            "temporal_symbol": "z=partial_t commuting with stationary spatial blocks",
        },
        "audited_blocks": audits,
        "mutation_results": [
            {
                "name": "flip_temporal_coderivative_sign",
                "detected": True,
                "wave_defect_counts": mutation["wave_diagonalization_defect_counts_degrees_1_2"],
            }
        ],
        "flags": {
            "EXACT_SPACETIME_D_BLOCKS_EXPORTED": True,
            "EXACT_SPACETIME_CODERIVATIVE_BLOCKS_EXPORTED": True,
            "SPACETIME_D_AND_DELTA_NILPOTENCY_AUDITED": True,
            "MAXWELL_AND_MASSIVE_WAVE_BLOCK_DIAGONALIZATION_EXPORTED": True,
            "RECOIL_SWITCH_PRODUCT_RULE_COMPONENT_SIGNS_EXPORTED": True,
            "COMPLETE_MODEWISE_RECOIL_SCALAR_INTEGRAND_EXPORTED": False,
            "FOUR_RECOIL_SCALAR_INTERVALS_EXPORTED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "SERIALIZE_THE_FIXED_TILDE_U_B_PER_SHELL_RECOIL_OPERATOR_WORD_USING_THE_EXACT_SPACETIME_BLOCKS",
        "claim_boundary": boundary,
        "provenance": {
            "source_commit": "WORKTREE",
            "source_manifest": [
                {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)}
                for path in SOURCE_FILES
            ],
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    rendered = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if args.emit:
        CERTIFICATE.write_text(rendered)
    if args.check and (not CERTIFICATE.exists() or CERTIFICATE.read_text() != rendered):
        raise SystemExit("stale Berger spacetime form-block sign bridge")
    print("BERGER_SPACETIME_FORM_BLOCK_SIGN_BRIDGE generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
