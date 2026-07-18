#!/usr/bin/env python3
"""Build the C2-visible repository coefficient match on Euclidean Schwarzschild."""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

from spectral.euclidean.coefficient_reconstruction import (
    ricci_flat_operator_beta1,
    spin_two_factor_ledger,
)
from spectral.euclidean.nonconformal_coefficient_match_receiver import (
    validate_nonconformal_coefficient_match,
)
from spectral.euclidean.repository_euclidean_elliptic_complex import (
    OUTPUT as ELLIPTIC_COMPLEX,
)


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERTIFICATES = HERE / "certificates"
OUTPUT = CERTIFICATES / "REPOSITORY_NONCONFORMALLY_FLAT_OR_RICCI_FLAT_FULL_BV_OPERATOR_MEASURE_COEFFICIENT_MATCH.json"
BACKGROUND_OUTPUT = CERTIFICATES / "REPOSITORY_C2_VISIBLE_BACKGROUND_ELIGIBILITY.json"
MEASURE_OUTPUT = CERTIFICATES / "REPOSITORY_LOCAL_BV_MEASURE_LEDGER.json"
REGULATOR_OUTPUT = CERTIFICATES / "REPOSITORY_LOCAL_B4_REGULATOR.json"
ZERO_MODE_OUTPUT = CERTIFICATES / "REPOSITORY_ZERO_MODE_LEDGER.json"
PARITY_OUTPUT = CERTIFICATES / "REPOSITORY_PARITY_WARD_IDENTITY.json"

MULTIPLICITY = CERTIFICATES / "REPOSITORY_FULL_BV_MULTIPLICITY_LEDGER.json"
ROUND_EULER = CERTIFICATES / "REPOSITORY_ROUND_S4_EULER_COEFFICIENT.json"
SNAPSHOT = ROOT / "quantum-weyl/classical_import/certificates/REPOSITORY_CLASSICAL_SNAPSHOT_COMPATIBILITY.json"
BH0 = ROOT / "black_hole_programme/certificates/BH0_STATIC_SPHERICAL_BACKGROUND.json"
YORK = CERTIFICATES / "YORK_HODGE_NONMINIMAL_BEREZINIAN_MATCH.json"
NONMINIMAL = ROOT / "quantum-weyl/local_bv/certificates/GENERAL_NONMINIMAL_GAUGE_FIXED_CONTRACTION.json"
ROUND_ZERO_MODES = CERTIFICATES / "ROUND_S4_STANDARD_FACTOR_ZERO_MODE_LEDGER.json"
VOLUME_LOCALITY = CERTIFICATES / "ROUND_S4_CONFORMAL_ZERO_MODE_VOLUME_LOCALITY.json"
STANDARD_ANOMALY = CERTIFICATES / "WEYL_GRAVITON_ANOMALY_COEFFICIENTS_D_DESCENT.json"
SLAVNOV_BASIS = ["ANOM_OMEGA_C2", "ANOM_OMEGA_E4", "ANOM_OMEGA_C_DUAL_C", "ANOM_OMEGA_BOX_R"]
SLAVNOV_COEFFICIENTS = {
    "ANOM_OMEGA_C2": {"numerator": 199, "denominator": 30},
    "ANOM_OMEGA_E4": {"numerator": -87, "denominator": 20},
    "ANOM_OMEGA_C_DUAL_C": {"numerator": 0, "denominator": 1},
    "ANOM_OMEGA_BOX_R": {"numerator": 0, "denominator": 1},
}


def _canonical_bytes(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _q(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def _proof(path: Path, *, data: bool = False) -> dict[str, str]:
    return {
        "format": "JSON_DATA" if data else "JSON_PROOF",
        "path": str(path.relative_to(ROOT)),
        "sha256": _sha256(path),
    }


def _generated_proof(path: Path, value: dict[str, Any]) -> dict[str, str]:
    return {
        "format": "JSON_PROOF",
        "path": str(path.relative_to(ROOT)),
        "sha256": hashlib.sha256(_canonical_bytes(value)).hexdigest(),
    }


def _with_digest(value: dict[str, Any]) -> dict[str, Any]:
    value["proof_sha256"] = _canonical_hash(value)
    return value


def background_eligibility(commit: str) -> dict[str, Any]:
    return _with_digest({
        "schema": "quantum-weyl-c2-visible-background-eligibility-v1",
        "result_id": "REPOSITORY_C2_VISIBLE_BACKGROUND_ELIGIBILITY",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "classical_commit": commit,
        "geometry": "Euclidean Schwarzschild local chart at beta=1, r=4",
        "analytic_continuation": "t=-i tau from the certified gamma=k=0 Schwarzschild control",
        "domain": "compactly supported local calculation in r>2, away from bolt and infinity",
        "exact_invariants": {
            "R": _q(0),
            "Ricci_squared": _q(0),
            "C2": _q(Fraction(3, 256)),
            "E4": _q(Fraction(3, 256)),
            "CdualC": _q(0),
            "identity": "Ricci=0 implies E4=C2=Riemann_squared; BH0 gives C2=48 beta^2/r^6",
        },
        "source_artifact": _proof(BH0),
        "eligibility": {
            "dimension": 4,
            "signature": "EUCLIDEAN",
            "Ricci_flat": True,
            "C2_nonzero": True,
            "closed_or_compact_support_policy": "LOCAL_COMPACT_SUPPORT",
        },
        "claim_boundary": "This certifies a local C2-visible Euclidean Ricci-flat curvature carrier by exact analytic continuation and scalar invariants. It does not certify a black-hole quantum state, a global Euclidean determinant, bolt regularity, thermodynamics, QME, or Lorentzian quantum theory.",
    })


def local_measure(commit: str) -> dict[str, Any]:
    return _with_digest({
        "schema": "quantum-weyl-local-bv-measure-ledger-v1",
        "result_id": "REPOSITORY_LOCAL_BV_MEASURE_LEDGER",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "classical_commit": commit,
        "domain": "nonzero local symbol modes with compact support",
        "factor_bundle_ranks": [5, 1, 5, 3],
        "determinant_exponents": ["-1/2", "+1/2", "-1/2", "+1/2"],
        "York_Hodge_Delta0_cancellation": True,
        "nonminimal_quartet_superdeterminant": "1",
        "residual_measure_factor": "field-independent local normalization",
        "proof_artifacts": [_proof(YORK), _proof(NONMINIMAL), _proof(MULTIPLICITY, data=True)],
        "claim_boundary": "This is the local nonzero-mode BV measure used for b4. It does not normalize the noncompact conformal group, fix a global determinant phase, or define Lorentzian time-ordered products.",
    })


def local_regulator(commit: str) -> dict[str, Any]:
    return _with_digest({
        "schema": "quantum-weyl-local-b4-regulator-v1",
        "result_id": "REPOSITORY_LOCAL_B4_REGULATOR",
        "dependency_tags": ["EUCLIDEAN-SPECTRAL"],
        "classical_commit": commit,
        "regularization": "covariant parity-even second-order heat-kernel b4 on the four factor blocks",
        "analytic_route": "EUCLIDEAN_ELLIPTIC",
        "locality": "support-local coefficient on a Ricci-flat curvature jet",
        "factor_count": 4,
        "factor_ids": [row["target_factor_id"] for row in json.loads(MULTIPLICITY.read_text())["standard_factor_map"]],
        "BoxR_scheme": "set to zero by the declared local R2 counterterm convention",
        "global_phase_policy": "not used in local b4; locally constant spectral-cut phases have zero local variation",
        "source_artifacts": [_proof(STANDARD_ANOMALY, data=True), _proof(ELLIPTIC_COMPLEX)],
        "claim_boundary": "This fixes the local covariant b4 prescription and the removable BoxR scheme only. It does not fix the global determinant phase, collective-coordinate volume, regulated antibracket insertion, QME, or Lorentzian continuation.",
    })


def zero_modes(commit: str) -> dict[str, Any]:
    return _with_digest({
        "schema": "quantum-weyl-local-zero-mode-ledger-v1",
        "result_id": "REPOSITORY_ZERO_MODE_LEDGER",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "classical_commit": commit,
        "policy": "LOCAL_COMPACT_SUPPORT_NO_GLOBAL_KERNEL_SUBTRACTION",
        "local_b4_modified_by_finite_zero_modes": False,
        "global_Euclidean_Schwarzschild_zero_modes": "NOT_COMPUTED_NOT_USED",
        "stabilizer_volume": "NOT_NORMALIZED_NOT_USED_IN_LOCAL_B4",
        "consistency_artifacts": [_proof(ROUND_ZERO_MODES), _proof(VOLUME_LOCALITY)],
        "claim_boundary": "Finite-dimensional kernel subtraction and noncompact symmetry volume do not change the local b4 density on a fixed stabilizer stratum. Global Euclidean-Schwarzschild collective coordinates, determinants, and phases remain open.",
    })


def parity_ward(commit: str) -> dict[str, Any]:
    return _with_digest({
        "schema": "quantum-weyl-repository-parity-ward-identity-v1",
        "result_id": "REPOSITORY_PARITY_WARD_IDENTITY",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "classical_commit": commit,
        "analytic_route": "EUCLIDEAN_ELLIPTIC",
        "coefficient_basis": SLAVNOV_BASIS,
        "coefficients_sha256": _canonical_hash(SLAVNOV_COEFFICIENTS),
        "regulator": "real parity-even tensor Laplacians with scalar curvature shifts",
        "orientation_tensor_insertions": 0,
        "Hodge_star_insertions": 0,
        "ward_equation": "p=-p",
        "ward_matrix": [[2]],
        "ward_rank": 1,
        "CdualC_coefficient": _q(0),
        "source_artifact": _proof(STANDARD_ANOMALY, data=True),
        "claim_boundary": "The parity-odd local coefficient vanishes for the declared real parity-even heat-kernel regulator. This does not constrain parity-breaking regulators or boundary eta invariants.",
    })


def _factor_contributions() -> list[dict[str, Any]]:
    standard_rows = {row["factor_id"]: row for row in spin_two_factor_ledger()}
    beta2 = ricci_flat_operator_beta1(2)
    beta1 = ricci_flat_operator_beta1(1)
    beta0 = ricci_flat_operator_beta1(0)
    ricci_flat = {
        "physical_depth_0": beta2 - beta1,
        "ghost_depth_0": -beta0,
        "physical_depth_1": beta2 - beta1,
        "ghost_depth_1": -(beta1 - beta0),
    }
    rows = []
    multiplicity = json.loads(MULTIPLICITY.read_text())
    for mapping in multiplicity["standard_factor_map"]:
        target = mapping["target_factor_id"]
        repository_id = mapping["repository_factor_ids"][0]
        a_piece = Fraction(standard_rows[target]["signed_a_contribution"])
        beta_piece = ricci_flat[target]
        rows.append({
            "factor_id": repository_id,
            "standard_factor_id": target,
            "ricci_flat_beta1_contribution": _q(beta_piece),
            "round_S4_a_contribution": _q(a_piece),
            "coordinates": {
                "C2": _q(beta_piece + a_piece),
                "E4": _q(-a_piece),
                "CdualC": _q(0),
                "BoxR": _q(0),
            },
        })
    return rows


def build() -> tuple[dict[str, Any], ...]:
    ledger = json.loads(MULTIPLICITY.read_text())
    commit = ledger["classical_commit"]
    background = background_eligibility(commit)
    measure = local_measure(commit)
    regulator = local_regulator(commit)
    zero = zero_modes(commit)
    parity = parity_ward(commit)
    detailed = _factor_contributions()
    factor_rows = [
        {"factor_id": row["factor_id"], "coordinates": row["coordinates"]}
        for row in detailed
    ]
    totals = {
        name: sum(
            (Fraction(row["coordinates"][name]["numerator"], row["coordinates"][name]["denominator"])
             for row in detailed),
            Fraction(0),
        )
        for name in ("C2", "E4", "CdualC", "BoxR")
    }
    value = {
        "schema": "quantum-weyl-repository-nonconformal-coefficient-match-input-v1",
        "result_id": "REPOSITORY_NONCONFORMALLY_FLAT_OR_RICCI_FLAT_FULL_BV_OPERATOR_MEASURE_COEFFICIENT_MATCH",
        "result_state": "C2_VISIBLE_FULL_BV_LOCAL_COEFFICIENT_MATCHED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "classical_commit": commit,
        "analytic_route": "EUCLIDEAN_ELLIPTIC",
        "background": {
            "geometry": "Euclidean Schwarzschild local Ricci-flat chart at beta=1, r=4",
            "dimension": 4,
            "signature": "EUCLIDEAN",
            "C2_visibility": "NONZERO_LOCAL_DENSITY",
            "boundary_policy": "LOCAL_CLOSED_OR_COMPACT_SUPPORT",
            "eligibility_artifact": _generated_proof(BACKGROUND_OUTPUT, background),
        },
        "operator_and_measure": {
            "formulation": "FOURTH_ORDER_METRIC",
            "complete_elliptic_complex_artifact": _proof(ELLIPTIC_COMPLEX),
            "full_BV_multiplicity_artifact": _proof(MULTIPLICITY, data=True),
            "local_measure_artifact": _generated_proof(MEASURE_OUTPUT, measure),
            "local_b4_regulator_artifact": _generated_proof(REGULATOR_OUTPUT, regulator),
            "zero_mode_ledger_artifact": _generated_proof(ZERO_MODE_OUTPUT, zero),
            "auxiliary_fourth_order_match_artifact": None,
        },
        "coefficient_result": {
            "convention": "(4 pi)^(-2) [c C2-a E4+p CdualC+b BoxR]",
            "basis": ["C2", "E4", "CdualC", "BoxR"],
            "coefficients": {name: _q(value) for name, value in totals.items()},
            "factor_contributions": factor_rows,
            "factor_sum_verified": True,
        },
        "consistency": {
            "parity_status": "WARD_VERIFIED",
            "parity_artifact": _generated_proof(PARITY_OUTPUT, parity),
            "round_S4_Euler_cross_check": {"numerator": -87, "denominator": 20},
            "round_S4_cross_check_artifact": _proof(ROUND_EULER, data=True),
        },
        "classical_snapshot_compatibility_artifact": _proof(SNAPSHOT),
        "claim_flags": {
            "REPOSITORY_C2_COEFFICIENT_COMPUTED": True,
            "REPOSITORY_LOCAL_EFFECTIVE_ACTION_VECTOR_COMPUTED": True,
            "REPOSITORY_BV_ANOMALY_COEFFICIENT_COMPUTED": False,
            "REGULATED_SLAVNOV_BREAKING_COMPUTED": False,
            "QME_DISPOSITION": False,
            "LORENTZIAN_CERTIFIED": False,
        },
        "claim_boundary": "This LOCAL-ALGEBRAIC and EUCLIDEAN-SPECTRAL result binds the exact repository elliptic complex and full-BV multiplicity ledger to a C2-visible local Euclidean Ricci-flat carrier. It derives c=199/30, a=87/20 and p=0 factor by factor; BoxR=0 is the declared removable-counterterm scheme. It is a local effective-action coefficient, not yet the regulated BV Slavnov insertion, QME disposition, Lorentzian quantum theory, particle state, or black-hole thermodynamic result.",
    }
    value["proof_sha256"] = _canonical_hash({
        key: value[key]
        for key in (
            "classical_commit", "analytic_route", "background", "operator_and_measure",
            "coefficient_result", "consistency", "classical_snapshot_compatibility_artifact",
        )
    })
    calculation = _with_digest({
        "schema": "quantum-weyl-ricci-flat-factor-calculation-v1",
        "result_id": "REPOSITORY_RICCI_FLAT_FACTORWISE_B4_CALCULATION",
        "unconstrained_beta1": {f"spin_{spin}": _q(ricci_flat_operator_beta1(spin)) for spin in (0, 1, 2)},
        "factor_contributions": detailed,
        "totals": {name: _q(number) for name, number in totals.items()},
        "identities": {
            "ricci_flat_sum_is_c_minus_a": _q(totals["C2"] + totals["E4"]),
            "expected_c_minus_a": _q(Fraction(137, 60)),
            "round_S4_a": _q(Fraction(87, 20)),
            "derived_c": _q(totals["C2"]),
        },
        "claim_boundary": "Exact factor arithmetic for the declared repository mapping; scientific promotion occurs only in the separately validated coefficient-match artifact.",
    })
    return background, measure, regulator, zero, parity, calculation, value


CALCULATION_OUTPUT = CERTIFICATES / "REPOSITORY_RICCI_FLAT_FACTORWISE_B4_CALCULATION.json"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    values = build()
    paths = (BACKGROUND_OUTPUT, MEASURE_OUTPUT, REGULATOR_OUTPUT, ZERO_MODE_OUTPUT, PARITY_OUTPUT, CALCULATION_OUTPUT, OUTPUT)
    rendered = {path: _canonical_bytes(value) for path, value in zip(paths, values)}
    if args.emit:
        for path, data in rendered.items():
            path.write_bytes(data)
    if args.check:
        stale = [str(path) for path, data in rendered.items() if not path.exists() or path.read_bytes() != data]
        if stale:
            raise SystemExit(f"stale repository Ricci-flat coefficient artifacts: {stale}")
    if all(path.exists() and path.read_bytes() == data for path, data in rendered.items()):
        receipt = validate_nonconformal_coefficient_match(values[-1], repository_root=ROOT)
        print(f"repository Ricci-flat coefficient match: PASS ({receipt['coefficients']})")
    else:
        print("repository Ricci-flat coefficient match: BUILT (emit before semantic validation)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
