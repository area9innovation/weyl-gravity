#!/usr/bin/env python3
"""Export exact sparse Berger Green-kernel series matrices for recoil binding."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp

from closed_universe_observers.generate_berger_peter_weyl_form_laplacian import laplacian


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = PACKAGE / "certificates/BERGER_RECOIL_EXACT_MODE_KERNEL_PAYLOAD.json"
SCHEMA = PACKAGE / "schema/berger-recoil-exact-mode-kernel-payload-v1.schema.json"
REPORT = PACKAGE / "reports/berger-recoil-exact-mode-kernel-payload.md"
DEPENDENCIES = {
    "spectral": PACKAGE / "certificates/BERGER_PETER_WEYL_FORM_LAPLACIAN_ENGINE.json",
    "kernels": PACKAGE / "certificates/BERGER_FINITE_MODE_MAXWELL_EMITTER_GREEN_KERNELS.json",
    "word": PACKAGE / "certificates/BERGER_COMPLETE_PER_SHELL_RECOIL_OPERATOR_WORD.json",
}
SOURCE_FILES = [
    Path(__file__), PACKAGE / "generate_berger_peter_weyl_form_laplacian.py",
    PACKAGE / "verify_berger_recoil_exact_mode_kernel_payload.py",
    PACKAGE / "tests/test_berger_recoil_exact_mode_kernel_payload.py", SCHEMA, REPORT,
]
MU2 = sp.Symbol("mu_squared", positive=True)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sparse(matrix: sp.Matrix) -> list[dict[str, Any]]:
    return [
        {"row": row, "column": column, "value": sp.sstr(matrix[row, column])}
        for row in range(matrix.rows)
        for column in range(matrix.cols)
        if matrix[row, column] != 0
    ]


def _block(two_j: int, form_degree: int, family: str, wrong_sign: bool = False) -> dict[str, Any]:
    base = laplacian(two_j, form_degree)
    mass_squared = sp.Integer(0) if family == "Maxwell" else MU2
    operator = base + mass_squared * sp.eye(base.rows)
    sign = 1 if wrong_sign else -1
    coefficients = []
    for order in range(6):
        coefficients.append(
            {
                "series_order": order,
                "tau_power": 2 * order + 1,
                "operator_power": order,
                "scalar_factor": sp.sstr(sp.Rational(sign**order, sp.factorial(2 * order + 1))),
            }
        )
    recurrence_defects = 0
    for order in range(5):
        current = sp.Rational(sign**order, sp.factorial(2 * order + 1))
        following = sp.Rational(sign ** (order + 1), sp.factorial(2 * order + 3))
        defect = sp.simplify((2 * order + 3) * (2 * order + 2) * following + current)
        recurrence_defects += int(defect != 0)
    return {
        "two_j": two_j,
        "form_degree": form_degree,
        "family": family,
        "dimension": operator.rows,
        "mass_squared": sp.sstr(mass_squared),
        "operator_nonzero_entries": _sparse(operator),
        "series_coefficients": coefficients,
        "recurrence_defect_count_through_order4": recurrence_defects,
    }


def build() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    required = {
        "spectral": "EXACT_FORM_LAPLACIAN_BLOCKS_EXPORTED",
        "kernels": "MODE_CAUCHY_JUMP_AND_ODE_CERTIFIED",
        "word": "COMPLETE_MODEWISE_RECOIL_SCALAR_INTEGRAND_EXPORTED",
    }
    for name, flag in required.items():
        if values[name].get("flags", {}).get(flag) is not True:
            raise AssertionError(f"dependency dropped: {name}.{flag}")
    blocks = [
        _block(two_j, degree, family)
        for two_j in range(5)
        for family, degrees in (("Maxwell", (0, 1)), ("massive_two_form", (1, 2)))
        for degree in degrees
    ]
    if len(blocks) != 20 or any(block["recurrence_defect_count_through_order4"] for block in blocks):
        raise AssertionError("exact kernel payload recurrence failed")
    mutation = _block(0, 1, "Maxwell", wrong_sign=True)
    if mutation["recurrence_defect_count_through_order4"] == 0:
        raise AssertionError("kernel-series sign mutation escaped")
    payload_hash = hashlib.sha256(json.dumps(blocks, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    boundary = (
        "This exact LOCAL-ALGEBRAIC/LORENTZIAN-CAUSAL result exports machine-readable "
        "sparse Berger form-Laplacian operators and the first six exact factored "
        "sine-kernel matrix coefficients c_n A^n for Maxwell degrees 0,1 and massive-two-form "
        "degrees 1,2 at two_j=0,...,4. Massive blocks retain one declared symbolic "
        "positive mu_squared. All 20 blocks satisfy the exact Green-series recurrence "
        "through order four, and a sign mutation is detected. This is the algebraic "
        "carrier needed by the interval convolution engine, not an interval enclosure: "
        "no mass range, truncation remainder, switch multiplication, detector/profile "
        "contraction, I_abc value, recoil record, cone, Bridge 3 or quantum claim is exported."
    )
    return {
        "schema": "closed-universe-berger-recoil-exact-mode-kernel-payload-v1",
        "result_id": "BERGER_RECOIL_EXACT_MODE_KERNEL_PAYLOAD",
        "setting_id": values["word"]["setting_id"],
        "claim_status": "EXACT_ALGEBRAIC_FINITE_MODE_KERNEL_PAYLOAD_EXPORTED_INTERVAL_BINDING_OPEN",
        "atlas_status": "CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {name: {"path": str(path.relative_to(ROOT)), "result_id": values[name]["result_id"], "sha256": _sha256(path)} for name, path in DEPENDENCIES.items()},
        "mode_scope": {
            "theory": "classical pure-Weyl gravity plus Berger clock, Maxwell detector and massive two-form emitters",
            "background": "compact positive Berger clock at fixed coupling",
            "boundaries": "R x S3; finite mode blocks and no spatial boundary",
            "charge_sector": "fixed-coupling Berger sector",
            "carrier": "exact sparse form-Laplacian matrices and factored sine-kernel coefficients c_n A^n",
            "degree": "Maxwell 0,1 and massive-two-form 1,2",
            "parity": "all finite form polarizations",
            "ell": "two_j=0,1,2,3,4",
            "m": "all representation rows",
            "k": "all representation columns",
            "omega": "tau powers 1,3,5,7,9,11 with symbolic positive mu_squared on massive blocks",
        },
        "symbolic_parameters": [{"name": "mu_squared", "domain": "positive_real", "specialization_status": "DEFERRED"}],
        "blocks": blocks,
        "payload_sha256": payload_hash,
        "mutation_results": [{"name": "flip_kernel_series_power_sign", "detected": True, "defect_count": mutation["recurrence_defect_count_through_order4"]}],
        "flags": {
            "EXACT_SPARSE_MODE_OPERATORS_EXPORTED": True,
            "EXACT_SINE_KERNEL_SERIES_COEFFICIENTS_EXPORTED": True,
            "MAXWELL_AND_MASSIVE_BLOCKS_TWO_J0_TO_4_EXPORTED": True,
            "MASS_RANGE_DECLARED": False,
            "INTERVAL_KERNEL_ENCLOSURES_EXPORTED": False,
            "ACTUAL_SWITCH_AND_DETECTOR_BINDING_EXPORTED": False,
            "FOUR_RECOIL_SCALAR_INTERVALS_EXPORTED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "INTERVAL_ENCLOSE_ALGEBRAIC_KERNEL_PAYLOAD_AND_BIND_SWITCH_PROFILE_FACTORS",
        "claim_boundary": boundary,
        "provenance": {"source_commit": "WORKTREE", "source_manifest": [{"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for path in SOURCE_FILES]},
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
        raise SystemExit("stale exact mode-kernel payload")
    print("BERGER_RECOIL_EXACT_MODE_KERNEL_PAYLOAD generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
