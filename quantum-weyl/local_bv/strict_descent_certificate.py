"""Emit the partial dimension-four strict-density descent database."""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

from .algebra import canonical_sha256
from .horizontal_forms import (
    STRICT_DENSITY,
    HorizontalForm,
    StrictDensityBRSTDifferential,
    strict_density_algebra,
)
from .strict_descent import strict_candidate_descent_analysis


PACKAGE_ROOT = Path(__file__).resolve().parent
DETAILED_PATH = (
    PACKAGE_ROOT
    / "certificates"
    / "LOCAL_STRICT_DENSITY_DESCENT_CERTIFICATE.json"
)
DATABASE_PATH = (
    PACKAGE_ROOT / "descent" / "DESCENT_DATABASE_DIMENSION_FOUR_STRICT.json"
)
SCHEMA_PATH = PACKAGE_ROOT / "schema" / "strict_descent_certificate.schema.json"
DATABASE_SCHEMA_PATH = PACKAGE_ROOT / "schema" / "descent_database.schema.json"


def _source_manifest() -> dict[str, str]:
    paths = (
        "algebra.py",
        "brst.py",
        "horizontal_forms.py",
        "metadata.py",
        "strict_descent.py",
        "strict_descent_certificate.py",
        "schema/descent_database.schema.json",
        "schema/strict_descent_certificate.schema.json",
        "tests/test_horizontal_forms.py",
        "tests/test_strict_descent.py",
        "tests/test_strict_descent_certificate.py",
    )
    return {
        path: hashlib.sha256((PACKAGE_ROOT / path).read_bytes()).hexdigest()
        for path in paths
    }


def _fraction(value: Fraction) -> dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}


def _tower_payload(tower: dict[str, object]) -> dict[str, object]:
    return {
        "ghost_lift": tower["ghost_lift"],
        "descent_length": tower["descent_length"],
        "coefficients": [_fraction(value) for value in tower["coefficients"]],
        "brst_to_horizontal_ratios": [
            _fraction(value) for value in tower["brst_to_horizontal_ratios"]
        ],
        "form_degrees": list(tower["form_degrees"]),
        "ghost_numbers": list(tower["ghost_numbers"]),
        "tower_sha256": tower["tower_sha256"],
        "tower": [form.canonical_payload() for form in tower["tower"]],
    }


def _database_entry(
    class_id: str,
    *,
    ghost_number: int,
    status: str,
    length: int | str,
    tower_id: str,
    notes: str,
) -> dict[str, object]:
    return {
        "class_id": class_id,
        "ghost_number": ghost_number,
        "form_degree": 4,
        "antifield_number": 0,
        "descent_status": status,
        "descent_length": length,
        "tower_id": tower_id,
        "cohomology_status": "NOT_COMPUTED",
        "proof_certificate": (
            "quantum-weyl/local_bv/certificates/"
            "LOCAL_STRICT_DENSITY_DESCENT_CERTIFICATE.json"
        ),
        "notes": notes,
    }


def build_database() -> dict[str, Any]:
    entries = (
        _database_entry(
            "CT_C2",
            ghost_number=0,
            status="NONTRIVIAL",
            length=4,
            tower_id="STRICT_COUNTERTERM_DIFF_TOWER",
            notes="Nonzero universal Diff descent; cohomological nontriviality is not inferred.",
        ),
        _database_entry(
            "CT_E4",
            ghost_number=0,
            status="NOT_COMPUTED",
            length="NOT_COMPUTED",
            tower_id="NOT_COMPUTED",
            notes="Requires the separate Euler Weyl-current descent.",
        ),
        _database_entry(
            "CT_C_DUAL_C",
            ghost_number=0,
            status="NONTRIVIAL",
            length=4,
            tower_id="STRICT_COUNTERTERM_DIFF_TOWER",
            notes="Nonzero universal Diff descent for the strict parity-odd density.",
        ),
        _database_entry(
            "CT_BOX_R",
            ghost_number=0,
            status="TRIVIAL",
            length=0,
            tower_id="EXPLICIT_TOTAL_DERIVATIVE",
            notes="The density is d(nabla R).",
        ),
        _database_entry(
            "ANOM_OMEGA_C2",
            ghost_number=1,
            status="NONTRIVIAL",
            length=4,
            tower_id="STRICT_ANOMALY_DIFF_TOWER",
            notes="Nonzero universal Diff descent; anomaly nontriviality is not inferred.",
        ),
        _database_entry(
            "ANOM_OMEGA_E4",
            ghost_number=1,
            status="NOT_COMPUTED",
            length="NOT_COMPUTED",
            tower_id="NOT_COMPUTED",
            notes="Requires the nontrivial Euler Weyl descent.",
        ),
        _database_entry(
            "ANOM_OMEGA_C_DUAL_C",
            ghost_number=1,
            status="NONTRIVIAL",
            length=4,
            tower_id="STRICT_ANOMALY_DIFF_TOWER",
            notes="Nonzero universal Diff descent for the strict parity-odd ghost lift.",
        ),
        _database_entry(
            "ANOM_OMEGA_BOX_R",
            ghost_number=1,
            status="TRIVIAL",
            length=0,
            tower_id="OMEGA_BOX_R_TRIVIALIZATION",
            notes="Equals -(1/12) s(R^2) modulo d in the integrated Weyl sector.",
        ),
    )
    return {
        "result_id": "DESCENT_DATABASE_DIMENSION_FOUR_STRICT",
        "classical_commit": "UNFROZEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "result_state": "PARTIAL_DESCENT_DATABASE",
        "scope": (
            "Universal Diff descent for strict Weyl-invariant dimension-four "
            "densities and their Weyl-ghost lifts."
        ),
        "entry_count": len(entries),
        "entries": list(entries),
        "proof_certificate": (
            "quantum-weyl/local_bv/certificates/"
            "LOCAL_STRICT_DENSITY_DESCENT_CERTIFICATE.json"
        ),
        "not_computed": [
            "Euler Weyl-current descent",
            "antifield/Koszul-Tate completion",
            "cohomological nontriviality of strict candidates",
            "coefficients, QME status, and residual transfer",
        ],
    }


def build_certificate() -> dict[str, Any]:
    analysis = strict_candidate_descent_analysis()
    counterterm = analysis["counterterm"]
    anomaly = analysis["anomaly"]
    expected_coefficients = (
        Fraction(1),
        Fraction(-1),
        Fraction(1, 2),
        Fraction(-1, 6),
        Fraction(1, 24),
    )
    expected_ratios = (
        Fraction(1),
        Fraction(1, 2),
        Fraction(1, 3),
        Fraction(1, 4),
    )
    for tower in (counterterm, anomaly):
        if tower["coefficients"] != expected_coefficients:
            raise AssertionError("strict descent coefficients drifted")
        if tower["brst_to_horizontal_ratios"] != expected_ratios:
            raise AssertionError("strict descent proportionality drifted")

    algebra = strict_density_algebra(4)
    differential = StrictDensityBRSTDifferential(algebra)
    density = algebra.jet(STRICT_DENSITY)
    if differential.nilpotency_residual(density):
        raise AssertionError("strict density BRST row is not nilpotent")
    zero_form = HorizontalForm.coefficient(4, algebra.var(STRICT_DENSITY))
    if zero_form.horizontal_differential(algebra).horizontal_differential(algebra):
        raise AssertionError("horizontal differential is not nilpotent")
    sd = zero_form.horizontal_differential(algebra).brst(differential)
    ds = zero_form.brst(differential).horizontal_differential(algebra)
    if sd != ds:
        raise AssertionError("BRST and horizontal differential do not commute")

    database = build_database()
    source_manifest = _source_manifest()
    return {
        "result_id": "LOCAL_STRICT_DENSITY_DESCENT_CERTIFICATE",
        "result_state": "PARTIAL_DESCENT_DATABASE",
        "classical_commit": "UNFROZEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "scope": database["scope"],
        "checks": {
            "horizontal_d_squared": "VERIFIED",
            "density_brst_nilpotency": "VERIFIED",
            "brst_horizontal_commutation": "VERIFIED",
            "counterterm_tower_equations": "VERIFIED",
            "anomaly_tower_equations": "VERIFIED",
            "bottom_brst_closure": "VERIFIED",
            "euler_weyl_descent": "NOT_COMPUTED",
            "antifield_descent": "BLOCKED_CLASSICAL_EXPORT",
        },
        "towers": {
            "STRICT_COUNTERTERM_DIFF_TOWER": _tower_payload(counterterm),
            "STRICT_ANOMALY_DIFF_TOWER": _tower_payload(anomaly),
        },
        "database": {
            "result_id": database["result_id"],
            "entry_count": database["entry_count"],
            "sha256": canonical_sha256(database),
        },
        "canonical_hashes": {
            "source_manifest_sha256": canonical_sha256(source_manifest),
            "counterterm_tower_sha256": counterterm["tower_sha256"],
            "anomaly_tower_sha256": anomaly["tower_sha256"],
        },
        "not_computed": database["not_computed"],
        "assumptions": [
            "C^2 and C dual C are covariant strict Weyl-invariant top densities.",
            "NONTRIVIAL descent status means the stored descent tower is nonzero; it does not assert a nontrivial BV cohomology class.",
            "The Euler density is excluded because its Weyl variation has a separate nontrivial current descent.",
            "The coordinate BRST and horizontal differential commute; bicomplex totalization supplies the conventional grading sign.",
        ],
    }


def _render(value: dict[str, Any]) -> str:
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs = {
        DETAILED_PATH: _render(build_certificate()),
        DATABASE_PATH: _render(build_database()),
    }
    if args.emit:
        for path, content in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
    if args.check:
        for path, content in outputs.items():
            if path.read_text(encoding="utf-8") != content:
                raise SystemExit(f"strict descent artifact is stale: {path}")
    if not args.emit and not args.check:
        print(outputs[DETAILED_PATH], end="")
    else:
        print("LOCAL STRICT-DENSITY DESCENT: EXACT CHECKS PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
