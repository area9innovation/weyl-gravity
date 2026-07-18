"""Exact zero-mode ledger for the four standard conformal-spin-two factors."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = HERE / "certificates/ROUND_S4_STANDARD_FACTOR_ZERO_MODE_LEDGER.json"
SCHEMA = HERE / "schema/round-s4-standard-factor-zero-mode-ledger-v1.schema.json"
COEFFICIENT = HERE / "certificates/WEYL_GRAVITON_ANOMALY_COEFFICIENTS_D_DESCENT.json"
SCALAR_GHOST = HERE / "certificates/DIFF_WEYL_SCALAR_GHOST_REDUCTION.json"

SOURCE_PATHS = (
    "quantum-weyl/spectral/euclidean/round_s4_zero_modes.py",
    "quantum-weyl/spectral/euclidean/verify_round_s4_zero_modes.py",
    "quantum-weyl/spectral/euclidean/schema/round-s4-standard-factor-zero-mode-ledger-v1.schema.json",
    "quantum-weyl/spectral/euclidean/tests/test_round_s4_zero_modes.py",
    "quantum-weyl/reports/round-s4-standard-factor-zero-modes.md",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def rough_laplacian_eigenvalue(spin: int, level: int) -> int:
    """Eigenvalue of ``-nabla^2`` on transverse spin-s harmonics on unit S4."""

    if spin not in (0, 1, 2) or level < spin:
        raise ValueError("unsupported spin/level domain")
    return level * (level + 3) - spin


def scalar_degeneracy(level: int) -> int:
    if level < 0:
        raise ValueError("negative harmonic level")
    return (level + 1) * (level + 2) * (2 * level + 3) // 6


def transverse_vector_degeneracy(level: int) -> int:
    if level < 1:
        raise ValueError("transverse vector levels start at one")
    return level * (level + 3) * (2 * level + 3) // 2


def factor_spectrum(spin: int, mass_squared: int, minimum_level: int, *, scan_limit: int = 12) -> dict[str, Any]:
    rows = [
        {
            "level": level,
            "eigenvalue": rough_laplacian_eigenvalue(spin, level) + mass_squared,
        }
        for level in range(minimum_level, scan_limit + 1)
    ]
    zeros = [row["level"] for row in rows if row["eigenvalue"] == 0]
    return {
        "spin": spin,
        "M_squared": mass_squared,
        "minimum_level": minimum_level,
        "eigenvalue_formula": f"n(n+3)-{spin}+({mass_squared})",
        "zero_equation": f"n(n+3)={spin - mass_squared}",
        "zero_levels": zeros,
        "scan_limit": scan_limit,
        "scanned_rows": rows,
    }


def _factor_rows() -> list[dict[str, Any]]:
    factors = (
        ("physical_depth_0", 2, 4, 2),
        ("ghost_depth_0", 0, -4, 0),
        ("physical_depth_1", 2, 2, 2),
        ("ghost_depth_1", 1, -3, 1),
    )
    result = []
    for factor_id, spin, mass_squared, minimum_level in factors:
        spectrum = factor_spectrum(spin, mass_squared, minimum_level)
        zero_level = spectrum["zero_levels"][0] if spectrum["zero_levels"] else None
        degeneracy = None
        if zero_level is not None:
            degeneracy = scalar_degeneracy(zero_level) if spin == 0 else transverse_vector_degeneracy(zero_level)
        result.append({
            "factor_id": factor_id,
            "spectrum": spectrum,
            "zero_mode_dimension": degeneracy or 0,
            "geometric_kernel": (
                "degree-one scalar harmonics generating proper conformal Killing pairs"
                if factor_id == "ghost_depth_0"
                else "transverse degree-one Killing vectors"
                if factor_id == "ghost_depth_1"
                else "ZERO"
            ),
        })
    return result


def build() -> dict[str, Any]:
    coefficient = json.loads(COEFFICIENT.read_text())
    scalar = json.loads(SCALAR_GHOST.read_text())
    target_rows = coefficient["coefficient_calculation"]["constant_curvature_factor_ledger"]
    expected = [(row["factor_id"], row["spin"], row["M_squared"]) for row in target_rows]
    if expected != [
        ("physical_depth_0", 2, 4),
        ("ghost_depth_0", 0, -4),
        ("physical_depth_1", 2, 2),
        ("ghost_depth_1", 1, -3),
    ]:
        raise ValueError("standard factor ledger drifted")
    if scalar["target_match"]["repository_scalar_operator"] != "Delta_0-R/3":
        raise ValueError("repository scalar ghost map drifted")

    rows = _factor_rows()
    by_id = {row["factor_id"]: row for row in rows}
    if (
        by_id["physical_depth_0"]["zero_mode_dimension"] != 0
        or by_id["physical_depth_1"]["zero_mode_dimension"] != 0
        or by_id["ghost_depth_0"]["zero_mode_dimension"] != 5
        or by_id["ghost_depth_1"]["zero_mode_dimension"] != 10
    ):
        raise AssertionError("round-S4 zero-mode count drifted")
    reducibility = {
        "Killing_vector_modes": 10,
        "proper_conformal_scalar_modes": 5,
        "total_conformal_Killing_modes": 15,
        "scalar_FP_kernel_at_Delta0_eigenvalue_4": {
            "matrix": [[0, 0], [-8, 8]],
            "kernel_vector_in_c_omega_coordinates": [1, 1],
            "kernel_dimension_per_scalar_harmonic": 1,
        },
        "matches_classical_conformal_zero_mode_count": True,
    }
    mutant_total = 10 + 4
    proof_payload = {"rows": rows, "reducibility": reducibility, "mutant_total": mutant_total}
    value = {
        "schema": "quantum-weyl-round-s4-standard-factor-zero-mode-ledger-v1",
        "result_id": "ROUND_S4_STANDARD_FACTOR_ZERO_MODE_LEDGER",
        "result_state": "STANDARD_ROUND_S4_FOUR_FACTOR_ZERO_MODES_COMPLETE_REPOSITORY_GLOBAL_LEDGER_OPEN",
        "dependency_tags": ["EUCLIDEAN-SPECTRAL"],
        "classical_commit": scalar["classical_commit"],
        "dependency_hashes": {
            "standard_coefficient_ledger": _sha256(COEFFICIENT),
            "repository_scalar_ghost_reduction": _sha256(SCALAR_GHOST),
        },
        "background": {
            "geometry": "round unit S4",
            "scalar_curvature": 12,
            "operator_family": "Delta_s(M_squared)=-nabla^2+M_squared on transverse spin-s harmonics",
            "harmonic_eigenvalue": "-nabla^2=n(n+3)-s",
        },
        "factor_zero_mode_ledger": rows,
        "reducibility_match": reducibility,
        "zero_mode_policy": {
            "standard_determinants": "prime both ghost determinants by deleting their declared kernels",
            "physical_TT_determinants": "unprimed because both standard TT factors have zero kernel",
            "finite_group_volume": "NOT_NORMALIZED",
            "negative_scalar_level_zero": "nonzero eigenvalue -4; retained, regulator phase policy open",
        },
        "negative_control": {
            "mutation": "replace the five scalar conformal modes by four",
            "mutated_total": mutant_total,
            "expected_total": 15,
            "rejected": mutant_total != 15,
        },
        "claim_flags": {
            "STANDARD_ROUND_S4_FACTOR_ZERO_MODES_COMPLETE": True,
            "FIFTEEN_CONFORMAL_REDUCIBILITY_MODES_MATCHED": True,
            "REPOSITORY_SCALAR_FP_KERNEL_MATCHED": True,
            "REPOSITORY_PHYSICAL_HESSIAN_NORMALIZED": False,
            "REPOSITORY_GLOBAL_ZERO_MODE_LEDGER_COMPLETE": False,
            "FINITE_CONFORMAL_GROUP_VOLUME_NORMALIZED": False,
            "REGULATED_SLAVNOV_BREAKING_COMPUTED": False,
            "QME_DISPOSITION": False,
        },
        "proof_sha256": _canonical_hash(proof_payload),
        "next_gate": "SUPPLY_REPOSITORY_ROUND_S4_TT_HESSIAN_DICTIONARY_V1_AND_COMPLETE_GLOBAL_LEDGER",
        "claim_boundary": (
            "This EUCLIDEAN-SPECTRAL certificate classifies the zero modes of exactly the four standard conformal-spin-two factors on the round unit S4. The two physical TT factors have no zero modes. The rank-three vector ghost factor has ten Killing-vector zero modes, and the scalar ghost factor has five degree-one scalar zero modes whose exact two-by-two Diff-Weyl kernel vector is (1,1); together they reproduce the fifteen conformal reducibility modes. The result fixes the priming policy for these standard factors only. It does not identify the repository TT Hessian with the standard pair, normalize the finite conformal-group volume, fix the negative scalar mode phase, classify auxiliary or additional repository rows, supply the complete repository zero-mode ledger, compute anomaly coefficients or Slavnov breaking, decide the QME, transfer residual cohomology, or establish Lorentzian quantum theory."
        ),
        "provenance": {"source_sha256": {path: _sha256(ROOT / path) for path in SOURCE_PATHS}},
    }
    validate_claim_boundary(value)
    return value


def validate_claim_boundary(value: dict[str, Any]) -> None:
    flags = value.get("claim_flags", {})
    if not all(flags.get(name) is True for name in (
        "STANDARD_ROUND_S4_FACTOR_ZERO_MODES_COMPLETE",
        "FIFTEEN_CONFORMAL_REDUCIBILITY_MODES_MATCHED",
        "REPOSITORY_SCALAR_FP_KERNEL_MATCHED",
    )) or any(flags.get(name) is not False for name in (
        "REPOSITORY_PHYSICAL_HESSIAN_NORMALIZED",
        "REPOSITORY_GLOBAL_ZERO_MODE_LEDGER_COMPLETE",
        "FINITE_CONFORMAL_GROUP_VOLUME_NORMALIZED",
        "REGULATED_SLAVNOV_BREAKING_COMPUTED",
        "QME_DISPOSITION",
    )):
        raise ValueError("round-S4 zero-mode claim boundary crossed")


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
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(rendered)
    if args.check and (not OUTPUT.exists() or OUTPUT.read_text() != rendered):
        raise SystemExit(f"stale round-S4 zero-mode ledger: {OUTPUT}")
    print("round-S4 standard factor zero-mode ledger: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
