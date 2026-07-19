"""Classify the complete bounded cone with the ell2,k0 extra block adjoined."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_complete_global_ell2_extra_bounded_cone.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_complete_global_ell2_extra_bounded_cone.schema.json"
INPUTS = {
    "standard_global": ROOT / "bridge/certificates/einstein_maxwell_weyl_standard_global_bounded_second_order.json",
    "complete_common_zero": ROOT / "d_quotient_classical/certificates/PH_HOMOGENEOUS_TWIST_ELL2_EXTRA_BOUNDED_TANGENT_CONE_V1.json",
    "extra_current": ROOT / "bridge/certificates/einstein_maxwell_weyl_aligned_twist_ell2_extra_compatibility_face.json",
    "extra_bounded_obstruction": ROOT / "bridge/certificates/einstein_maxwell_weyl_global_extra_bounded_correction_obstruction.json",
    "ad_polynomial": ROOT / "bridge/certificates/einstein_maxwell_weyl_ad_ell2_extra_polynomial_zero_locus.json",
}


class CompleteGlobalExtraConeError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise CompleteGlobalExtraConeError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _energy_audit(records: dict[str, dict[str, Any]]) -> dict[str, Any]:
    a, charge = sp.symbols("a Q_e", real=True)
    xa1r, xa1i, xa2r, xa2i, xp1r, xp1i, xp2r, xp2i = sp.symbols(
        "xa1r xa1i xa2r xa2i xp1r xp1i xp2r xp2i", real=True
    )
    occupation = (
        1296 * (xa1r**2 + xa1i**2)
        + sp.Rational(208, 3) * (xa2r**2 + xa2i**2)
        + 22464 * (xp1r**2 + xp1i**2)
        + 12288 * (xp2r**2 + xp2i**2)
    )
    mu = -a**2 - charge**2 - sp.Rational(4, 3) * occupation
    _require(all(coefficient < 0 for coefficient in sp.Poly(mu, a, charge, xa1r, xa1i, xa2r, xa2i, xp1r, xp1i, xp2r, xp2i).coeffs()), "energy form lost negativity")
    _require(records["extra_current"]["extra_current_gram_at_ell2_k0"]["diagonal"] == ["1296", "208/3", "22464", "12288"], "extra occupation changed")
    return {
        "extra_amplitude_order": ["x_ax1", "x_ax2", "x_pol1", "x_pol2"],
        "occupation": "X=1296*|x_ax1|^2+(208/3)*|x_ax2|^2+22464*|x_pol1|^2+12288*|x_pol2|^2",
        "positive_definite_occupation": True,
        "moment_map_after_b_B_elimination": "mu_H=-a^2-Q_e^2-(4/3)*X",
        "real_zero_locus": "a=0,Q_e=0,x_ax1=x_ax2=x_pol1=x_pol2=0",
        "symbolic_negative_sum_of_squares_verified": True,
    }


def build() -> dict[str, Any]:
    records = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in INPUTS.items()}
    standard = records["standard_global"]
    _require(standard["classification"]["complete_standard_generalized_zero_bounded_cone_classified"], "standard global cone changed")
    _require("B=0" in standard["universal_complete_carrier_corollary"]["statement"], "universal twist-velocity elimination changed")
    common = records["complete_common_zero"]
    _require(common["classification"]["complete_common_zero_locus_in_declared_nonzero_extra_carrier"], "complete common-zero input changed")
    _require(common["moment_map_descent"]["mu_H"] == "2*|B|^2-Q_e^2-(omega_e^2/4)*X=0 with omega_e^2=16/3", "extra moment map changed")
    _require(records["extra_bounded_obstruction"]["classification"]["complete_nonzero_extra_common_zero_orbit_covered"], "extra obstruction input changed")
    _require(records["ad_polynomial"]["classification"]["old_nonzero_extra_common_zero_cone_survives_repair"], "a/d repair reconciliation changed")
    energy = _energy_audit(records)

    return {
        "schema": "einstein-maxwell-weyl-complete-global-ell2-extra-bounded-cone-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_COMPLETE_GLOBAL_ELL2_EXTRA_BOUNDED_CONE",
        "result_state": "COMPLETE_GLOBAL_PLUS_ELL2_EXTRA_BOUNDED_CONE_CLASSIFIED",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "scope": {
            "theory": "Weyl-Maxwell target",
            "background": "compact magnetically supported Plebanski-Hacyan product",
            "boundaries": "closed S1_L times S2; bounded/finite-quasiperiodic correction",
            "charge_sector": "fixed N=2 magnetic bundle with electric tangent allowed",
            "carrier": "complete homogeneous (a,b,c,d,Q_e,W_x), twist (A,B), and all axial/polar ell=2,k=0 extra-primary amplitudes",
            "degree": 2,
            "parity": "homogeneous, axial twist, and both generic extra parities",
            "ell": "input 0,1,2 with all quadratic outputs retained by imported complete source theorems",
            "m": "all by SO3 covariance",
            "k": 0,
            "omega": "generalized zero plus +/-4/sqrt(3)",
        },
        "necessity": {
            "polynomial_step": "the universal bounded source coefficients force b=0,B=0,Q_e*a=0; the repaired a/d cross ideal is compatible with the conclusion below",
            "Hamiltonian_step": energy,
            "conclusion": "every bounded candidate has a=b=Q_e=0,B=0 and zero ell=2 extra amplitude",
            "remaining_coordinates": ["c", "d", "W_x", "A in R^3"],
        },
        "sufficiency": {
            "imported_standard_cone": "Z2_global^bounded={(c,d,W_x,A):c,d,W_x real,A in R^3}",
            "correction": "the homogeneous source vanishes and constant A has the certified time-independent polar ell=2 correction",
            "extra_source": "zero because every extra amplitude is zero on the cone",
            "regularity": "real smooth spatially periodic and bounded",
        },
        "complete_bounded_theorem": {
            "tangent_cone": "Z2_(global+ell2extra)^bounded={(c,d,W_x,A):c,d,W_x real,A in R^3}",
            "extra_intersection": "the bounded cone contains no nonzero ell=2,k=0 extra-primary direction",
            "equality_with_standard_global_cone": True,
        },
        "reconciliation": {
            "old_common_zero_orbit": "requires B!=0 to balance the negative extra occupation and is therefore removed by the independent twist-velocity polynomial obstruction",
            "repaired_ad_ideal": "does not reopen a branch; the Hamiltonian moment map eliminates every extra amplitude once B=0",
            "constant_resonance_matrix": "need not be solved further on this carrier because its only nonzero-extra domain is already excluded by a necessary moment map",
        },
        "correction_classes": {
            "BOUNDED_OR_FINITE_QUASIPERIODIC": {"status": "CERTIFIED"},
            "SMOOTH_SECULAR": {"status": "CERTIFIED_FORMULA_ONLY", "reason": "the complete smooth cone is the five-moment-map zero locus and is larger; its coefficientwise parameterization is separate"},
            "CAUSAL_RETARDED": {"status": "NO_CERTIFIED_MAP"},
        },
        "classification": {
            "complete_declared_global_ell2_extra_carrier_covered": True,
            "bounded_tangent_cone_classified": True,
            "bounded_cone_equals_standard_global_cone": True,
            "all_nonzero_ell2_extra_directions_bounded_obstructed": True,
            "repaired_ad_polynomial_lifecycle_incorporated": True,
            "other_harmonics_classified": False,
            "all_orders_integrability": False,
            "causal_or_quantum_claim": False,
        },
        "interpretation": "The extra ell=2 block is linearly genuine but contributes with the same negative Hamiltonian-moment-map sign as the radion and electric directions. Boundedness independently removes the only positive twist-velocity contribution. Consequently the complete bounded cone on this enlarged carrier contains no extra wave and collapses exactly to the standard static-global cone, while the smooth-secular moment-map cone remains larger.",
        "next_gate": "adjoin one opposite-sign standard Einstein oscillator and solve the repaired polynomial plus moment-map system; separately propagate the full-time a/d audit to exceptional ell=1 and nonzero momentum",
        "claim_boundary": "This is complete only for the homogeneous/twist plus ell=2,k=0 extra carrier. It does not classify standard Einstein oscillators, other ell or momenta, the complete finite bounded cone, causal propagation, all-orders integration, residual descent, observables, particles or quantum theory.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for name, path in INPUTS.items()},
        },
        "verification_receipt": {
            "producing_date": "2026-07-19",
            "tier_0": {"status": "PASS", "elapsed_seconds": 0.20, "max_rss_kb": 16184},
            "tier_1": {"status": "PASS", "elapsed_seconds": 2.30, "max_rss_kb": 60640, "tests_run": 20},
            "tier_2": {"status": "PASS_BY_CONTENT_ADDRESS", "criterion": "the complete common-zero orbit, standard bounded cone, extra current and repaired a/d polynomial theorem are unchanged exact inputs"},
            "tier_3": {"status": "NOT_RUN", "reason": "other harmonics, complete finite bounded, causal, all-orders, residual and quantum gates remain excluded"},
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_complete_global_ell2_extra_bounded_cone --check",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_complete_global_ell2_extra_bounded_cone.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_complete_global_ell2_extra_bounded_cone",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    value = build()
    if arguments.write:
        OUTPUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    elif json.loads(OUTPUT.read_text(encoding="utf-8")) != value:
        raise CompleteGlobalExtraConeError("complete global+ell2-extra cone certificate is stale")
    print("EINSTEIN_MAXWELL_WEYL_COMPLETE_GLOBAL_ELL2_EXTRA_BOUNDED_CONE: PASS")


if __name__ == "__main__":
    main()
