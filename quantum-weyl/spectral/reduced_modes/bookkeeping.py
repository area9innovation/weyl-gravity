#!/usr/bin/env python3
"""Build the fail-closed reduced E/A/L spectral bookkeeping ledger.

This executable imports data, not conclusions, from the existing classical
and reduced-field certificates.  It independently checks the exact branch
multiplicities, character identity, low-energy exceptions, Krein signs and
residue formulae.  It deliberately does not evaluate a determinant.

The emitted object is tagged ``REDUCED-MODE``.  It cannot support a
Lorentzian causal, QME, anomaly-cancellation, or gauge-independence claim.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp


ROOT = Path(__file__).resolve().parents[3]
RESULT_OUTPUT = (
    ROOT / "quantum-weyl" / "certificates" / "REDUCED_MODE_SPECTRAL_BOOTSTRAP.json"
)
LEDGER_OUTPUT = (
    ROOT
    / "quantum-weyl"
    / "spectral"
    / "reduced_modes"
    / "certificates"
    / "eal_branch_ledger.json"
)

FIELD_DICTIONARY = (
    ROOT / "covariant_completion" / "certificates" / "EAL_multiplicity_match.json"
)
CURVATURE_CHARACTER = (
    ROOT
    / "covariant_completion"
    / "certificates"
    / "curved_EAL_spectrum_all_level.json"
)
BRANCH_RESIDUES = (
    ROOT / "covariant_completion" / "certificates" / "branch_residue_operators.json"
)

N = sp.symbols("N", integer=True, positive=True)
Q = sp.symbols("q")

EXPECTED = {
    "E": {
        "minimum_energy": 2,
        "field_origin": "lower-frequency TT Bach branch",
        "multiplicity": 2 * (N - 1) * (N + 3),
        "source_multiplicity": "2(r+1)(r+5)=2(N-1)(N+3)",
        "krein_sign": 1,
        "residue": 4 * (N + 1),
        "source_residue": "R_E(N)=4(N+1)",
        "elliptic_order": 1,
        "zero_mode_exclusion": "NONE_WITHIN_REDUCED_E_BRANCH",
    },
    "A": {
        "minimum_energy": 3,
        "field_origin": "transverse-vector metric branch",
        "multiplicity": 2 * (N - 1) * (N + 1),
        "source_multiplicity": "2(r+1)(r+3)=2(N-1)(N+1)",
        "krein_sign": -1,
        "residue": 2 * (N**2 - 4),
        "source_residue": "R_A(N)=2(N^2-4)",
        "elliptic_order": 2,
        "zero_mode_exclusion": (
            "N=2 TRANSVERSE-VECTOR KILLING BAND EXCLUDED: "
            "symgrad(Killing)=0"
        ),
    },
    "L": {
        "minimum_energy": 4,
        "field_origin": "upper-frequency TT Bach branch",
        "multiplicity": 2 * (N - 3) * (N + 1),
        "source_multiplicity": "2(r+1)(r+5)=2(N-3)(N+1)",
        "krein_sign": -1,
        "residue": 4 * (N - 1),
        "source_residue": "R_L(N)=4(N-1)",
        "elliptic_order": 1,
        "zero_mode_exclusion": "NONE_WITHIN_REDUCED_L_BRANCH",
    },
}


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _relative(path: Path) -> str:
    return str(path.relative_to(ROOT))


def _assert_upstream() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    fields = _load(FIELD_DICTIONARY)
    curvature = _load(CURVATURE_CHARACTER)
    residues = _load(BRANCH_RESIDUES)

    if fields.get("schema") != "pure-weyl-eal-field-dictionary-v1":
        raise AssertionError("unexpected E/A/L field-dictionary schema")
    if curvature.get("schema") != "pure-weyl-curvature-eal-spectrum-all-level-v1":
        raise AssertionError("unexpected all-level curvature-spectrum schema")
    if residues.get("schema") != "pure-weyl-branch-residues-v1":
        raise AssertionError("unexpected branch-residue schema")
    if not (
        fields.get("all_energy_symbolic")
        and fields.get("parity_complete")
        and curvature.get("all_level_not_finite_cutoff")
        and curvature.get("EAL_curvature_spectrum_match")
        and residues.get("normalization_fixed_all_levels")
    ):
        raise AssertionError("an upstream exact/all-level guard is false")

    field_branches = fields.get("branches", {})
    residue_branches = residues.get("branches", {})
    curvature_branches = {
        branch["family"]: branch for branch in curvature.get("branches", ())
    }
    if set(field_branches) != set(EXPECTED):
        raise AssertionError("field branch inventory drifted")
    if set(residue_branches) != set(EXPECTED):
        raise AssertionError("residue branch inventory drifted")
    if set(curvature_branches) != set(EXPECTED):
        raise AssertionError("curvature branch inventory drifted")

    for family, expected in EXPECTED.items():
        field = field_branches[family]
        residue = residue_branches[family]
        curvature_branch = curvature_branches[family]
        if field.get("minimum_energy") != expected["minimum_energy"]:
            raise AssertionError(f"{family} minimum energy drifted")
        if field.get("field_origin") != expected["field_origin"]:
            raise AssertionError(f"{family} field origin drifted")
        if field.get("multiplicity") != expected["source_multiplicity"]:
            raise AssertionError(f"{family} multiplicity record drifted")
        if residue.get("energy_form") != expected["source_residue"]:
            raise AssertionError(f"{family} residue formula drifted")
        if residue.get("krein_sign") != expected["krein_sign"]:
            raise AssertionError(f"{family} Krein sign drifted")
        if residue.get("elliptic_order") != expected["elliptic_order"]:
            raise AssertionError(f"{family} residue order drifted")
        if curvature_branch.get("minimum_energy") != expected["minimum_energy"]:
            raise AssertionError(f"{family} curvature threshold drifted")
        one_chiral = sp.sympify(
            curvature_branch.get("one_chirality_dimension"), locals={"n": N}
        )
        if sp.expand(2 * one_chiral - expected["multiplicity"]) != 0:
            raise AssertionError(f"{family} parity-complete multiplicity mismatch")
        residue_expression = expected["residue"]
        if sp.simplify(residue_expression.subs(N, expected["minimum_energy"])) <= 0:
            raise AssertionError(f"{family} residue is not positive at threshold")

    correction = fields.get("important_correction", "")
    if "N=2 Killing band" not in correction or "symgrad(Killing)=0" not in correction:
        raise AssertionError("A-branch Killing-band exclusion is missing")
    return fields, curvature, residues


def _characters() -> dict[str, sp.Expr]:
    branches = {
        "E": 2 * Q**2 * (5 - 3 * Q) / (1 - Q) ** 3,
        "A": 2 * Q**3 * (8 - 9 * Q + 3 * Q**2) / (1 - Q) ** 3,
        "L": 2 * Q**4 * (5 - 3 * Q) / (1 - Q) ** 3,
    }
    total = sp.factor(sum(branches.values(), sp.Integer(0)))
    signed = sp.factor(branches["E"] - branches["A"] - branches["L"])
    expected_total = 2 * Q**2 * (5 + 5 * Q - 4 * Q**2) / (1 - Q) ** 3
    expected_signed = 2 * Q**2 * (4 * Q**2 - 11 * Q + 5) / (1 - Q) ** 3
    if sp.simplify(total - expected_total) != 0:
        raise AssertionError("unsigned character identity failed")
    if sp.simplify(signed - expected_signed) != 0:
        raise AssertionError("signed character identity failed")

    for energy in range(2, 41):
        coefficient = sp.expand(sp.series(total, Q, 0, energy + 1).removeO()).coeff(
            Q, energy
        )
        direct = sum(
            expected["multiplicity"].subs(N, energy)
            for expected in EXPECTED.values()
            if energy >= expected["minimum_energy"]
        )
        if coefficient != direct:
            raise AssertionError(f"character coefficient mismatch at N={energy}")
    return {**branches, "total": total, "signed": signed}


def build_certificate() -> dict[str, Any]:
    _, curvature, _ = _assert_upstream()
    characters = _characters()

    upstream_one_chiral = sp.sympify(
        curvature["symbolic_character"]["E_plus_A_plus_L"],
        locals={"q": Q},
    )
    if sp.simplify(characters["total"] - 2 * upstream_one_chiral) != 0:
        raise AssertionError("parity-complete/upstream character mismatch")

    low_energies = list(range(2, 7))
    low_dimensions = [
        int(
            sum(
                expected["multiplicity"].subs(N, energy)
                for expected in EXPECTED.values()
                if energy >= expected["minimum_energy"]
            )
        )
        for energy in low_energies
    ]
    if low_dimensions != curvature["low_level_regression"]["physical_dimensions"]:
        raise AssertionError("low-level dimension regression failed")

    branches = []
    for family, expected in EXPECTED.items():
        branches.append(
            {
                "family": family,
                "compact_frequency": "N",
                "minimum_energy": expected["minimum_energy"],
                "field_origin": expected["field_origin"],
                "parity_complete_multiplicity": str(
                    sp.factor(expected["multiplicity"])
                ),
                "krein_sign": expected["krein_sign"],
                "positive_residue": str(sp.factor(expected["residue"])),
                "residue_elliptic_order": expected["elliptic_order"],
                "zero_mode_exclusion": expected["zero_mode_exclusion"],
                "kinetic_eigenvalue_status": "NOT_COMPUTED",
                "determinant_phase_status": "NOT_COMPUTED",
                "determinant_contribution_status": "NOT_COMPUTED",
            }
        )

    sources = [FIELD_DICTIONARY, CURVATURE_CHARACTER, BRANCH_RESIDUES]
    return {
        "schema": "quantum-weyl-reduced-mode-ledger-v1",
        "result_id": "REDUCED_MODE_EAL_BRANCH_LEDGER",
        "result_stage": "CLASSIFIED",
        "calculation_kind": "BOOKKEEPING_BOOTSTRAP",
        "dependency_tags": ["REDUCED-MODE"],
        "classical_commit": "UNFROZEN",
        "classical_freeze_status": "NOT_IMPORTED",
        "publishable_quantum_result": False,
        "cohomology_status": "NOT_APPLICABLE",
        "coefficient_status": "NOT_COMPUTED",
        "regularization_status": "NOT_COMPUTED",
        "claim_boundary": {
            "lorentzian_causal_claim": False,
            "qme_claim": False,
            "anomaly_cancellation_claim": False,
            "gauge_fixing_independence_claim": False,
            "euclidean_ellipticity_claim": False,
        },
        "branches": branches,
        "character": {
            "exact_arithmetic": True,
            "parity_complete": True,
            "branch_characters": {
                family: str(sp.factor(characters[family]))
                for family in ("E", "A", "L")
            },
            "unsigned": str(sp.factor(characters["total"])),
            "signed": str(sp.factor(characters["signed"])),
            "coefficient_regression_range": [2, 40],
            "low_energy_dimensions": dict(zip(map(str, low_energies), low_dimensions)),
        },
        "global_bookkeeping": {
            "complete_zero_mode_policy": "NOT_COMPUTED",
            "ghost_multiplicities": "NOT_COMPUTED",
            "auxiliary_multiplicities": "NOT_COMPUTED",
            "measure_normalization": "NOT_COMPUTED",
            "contour_policy": "NOT_COMPUTED",
            "analytic_extrapolation": "NOT_COMPUTED",
            "rational_reconstruction": "NOT_COMPUTED",
        },
        "upstream_receipts": [
            {
                "path": _relative(path),
                "sha256": _digest(path),
            }
            for path in sources
        ],
        "proof_certificate": _relative(LEDGER_OUTPUT),
        "assumptions": [
            "The three hashed upstream certificates are the current reduced-field inputs.",
            "The overall Weyl-action convention is the one recorded by the branch-residue certificate.",
        ],
        "notes": (
            "This result classifies exact reduced branch bookkeeping only. "
            "CLASSIFIED here is not a classification of H^(0,4)(s|d) or "
            "H^(1,4)(s|d), and no determinant or one-loop coefficient has been computed."
        ),
    }


def build_result_envelope() -> dict[str, Any]:
    """Return the repository-wide result-schema envelope for the ledger."""

    return {
        "result_id": "REDUCED_MODE_SPECTRAL_BOOTSTRAP",
        "classical_commit": "UNFROZEN",
        "dependency_tags": ["REDUCED-MODE"],
        "lifecycle_status": "CLASSIFIED",
        "ghost_number": 0,
        "form_degree": 0,
        "antifield_number": 0,
        "parity": "mixed",
        "representative": "parity-complete E/A/L reduced branch ledger",
        "cohomology_status": "NOT_COMPUTED",
        "descent_status": "NOT_COMPUTED",
        "coefficient_status": "NOT_COMPUTED",
        "residual_projection_status": "NOT_COMPUTED",
        "proof_certificate": _relative(LEDGER_OUTPUT),
        "assumptions": [
            "The detailed ledger verifies the hashes of all imported reduced-mode inputs."
        ],
        "notes": (
            "Bookkeeping classification only: no determinant, local BV "
            "cohomology, one-loop coefficient, Euclidean ellipticity, Lorentzian "
            "causal construction, anomaly cancellation, or QME result."
        ),
    }


def _verify_envelope(certificate: dict[str, Any]) -> None:
    if certificate.get("dependency_tags") != ["REDUCED-MODE"]:
        raise AssertionError("bootstrap must carry exactly the REDUCED-MODE tag")
    if certificate.get("coefficient_status") != "NOT_COMPUTED":
        raise AssertionError("bootstrap illegally promoted a coefficient")
    if certificate.get("publishable_quantum_result") is not False:
        raise AssertionError("unfrozen classical input cannot be publishable")
    boundary = certificate.get("claim_boundary", {})
    if any(boundary.values()):
        raise AssertionError("bootstrap crossed a forbidden claim boundary")
    if certificate.get("classical_freeze_status") != "NOT_IMPORTED":
        raise AssertionError("Branch C must not invent the classical freeze")
    if any(
        branch.get("determinant_contribution_status") != "NOT_COMPUTED"
        for branch in certificate.get("branches", ())
    ):
        raise AssertionError("a determinant contribution was silently promoted")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true", help="write the deterministic ledger")
    parser.add_argument("--check", action="store_true", help="check the committed ledger is current")
    args = parser.parse_args()

    certificate = build_certificate()
    _verify_envelope(certificate)
    result = build_result_envelope()
    rendered_ledger = json.dumps(certificate, indent=2, sort_keys=True) + "\n"
    rendered_result = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.emit:
        LEDGER_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        RESULT_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        LEDGER_OUTPUT.write_text(rendered_ledger, encoding="utf-8")
        RESULT_OUTPUT.write_text(rendered_result, encoding="utf-8")
        print("wrote", _relative(LEDGER_OUTPUT))
        print("wrote", _relative(RESULT_OUTPUT))
    if args.check:
        if not LEDGER_OUTPUT.exists():
            raise AssertionError(
                f"missing generated ledger: {_relative(LEDGER_OUTPUT)}"
            )
        if not RESULT_OUTPUT.exists():
            raise AssertionError(
                f"missing result envelope: {_relative(RESULT_OUTPUT)}"
            )
        if LEDGER_OUTPUT.read_text(encoding="utf-8") != rendered_ledger:
            raise AssertionError("generated reduced-mode ledger is stale")
        if RESULT_OUTPUT.read_text(encoding="utf-8") != rendered_result:
            raise AssertionError("generated reduced-mode result envelope is stale")
    print("REDUCED-MODE SPECTRAL BOOTSTRAP: ALL EXACT GUARDS PASS")
    print("COEFFICIENTS: NOT_COMPUTED; LORENTZIAN/QME CLAIMS: FALSE")


if __name__ == "__main__":
    main()
