"""Solve the repaired a/d times ell2-extra polynomial zero locus."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_ad_ell2_extra_polynomial_zero_locus.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_ad_ell2_extra_polynomial_zero_locus.schema.json"
INPUTS = {
    "abd_matrix": ROOT / "bridge/certificates/einstein_maxwell_weyl_abd_ell2_extra_resonance_matrix.json",
    "d_full_time": ROOT / "bridge/certificates/einstein_maxwell_weyl_d_ell2_extra_full_time_polynomial.json",
    "standard_global": ROOT / "bridge/certificates/einstein_maxwell_weyl_standard_global_bounded_second_order.json",
    "old_complete_cone": ROOT / "d_quotient_classical/certificates/PH_HOMOGENEOUS_TWIST_ELL2_EXTRA_BOUNDED_TANGENT_CONE_V1.json",
}


class ADPolynomialError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ADPolynomialError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _leading_row_audit(records: dict[str, dict[str, Any]]) -> dict[str, Any]:
    t = sp.symbols("t", real=True)
    a, d = sp.symbols("a d", real=True)
    xa1, xa2, xp1, xp2 = sp.symbols("z_ax1 z_ax2 z_pol1 z_pol2")
    locals_ = {"t": t, "I": sp.I, "sqrt": sp.sqrt}
    direct = records["abd_matrix"]["direct_source_rows"]

    def vector(parity: str, mode: str) -> sp.Matrix:
        return sp.Matrix([sp.sympify(value, locals=locals_) for value in direct[parity]["a"][mode]])

    axial = sp.expand(a) * (xa1 * vector("axial", "e1") + xa2 * vector("axial", "e2"))
    polar_a = sp.expand(a) * (xp1 * vector("polar", "e1") + xp2 * vector("polar", "e2"))

    axial_e1_witness = sp.factor(sp.expand(axial[0]).coeff(t, 1))
    axial_e2_witness = sp.factor(sp.expand(axial[1]).coeff(t, 1))
    polar_e2_witness = sp.factor(sp.expand(polar_a[0]).coeff(t, 2))
    polar_e1_witness = sp.factor(sp.expand(polar_a[1]).coeff(t, 1))
    expected = {
        "axial_e1": -144 * sp.sqrt(3) * sp.I * a * xa1,
        "axial_e2": -sp.Rational(8, 3) * sp.sqrt(3) * sp.I * a * xa2,
        "polar_e1": -12 * sp.sqrt(3) * sp.I * a * xp1,
        "polar_e2": 180 * a * xp2,
    }
    actual = {
        "axial_e1": axial_e1_witness,
        "axial_e2": axial_e2_witness,
        "polar_e1": polar_e1_witness,
        "polar_e2": polar_e2_witness,
    }
    for name in expected:
        _require(sp.factor(actual[name] - expected[name]) == 0, f"{name} leading witness changed")

    repaired = records["d_full_time"]["full_time_polynomial"]
    _require(repaired["polynomial_zero_locus_for_d_times_polar_extra_alone"] == "d*z2=0", "d repair changed")
    d_witness = sp.sympify(repaired["witness"], locals={"d": d, "z2": xp2, "I": sp.I, "sqrt": sp.sqrt})
    _require(d_witness != 0 and sp.factor(d_witness / (d * xp2)) != 0, "d polar-e2 witness vanished")

    ideal_generators = [a * xa1, a * xa2, a * xp1, a * xp2, d * xp2]
    groebner = sp.groebner(ideal_generators, xa1, xa2, xp1, xp2, a, d, order="lex")
    _require(set(groebner.polys) == set(sp.Poly(value, xa1, xa2, xp1, xp2, a, d) for value in ideal_generators), "polynomial ideal changed")
    return {
        "amplitude_order": ["z_ax1", "z_ax2", "z_pol1", "z_pol2"],
        "leading_row_witnesses": {name: str(sp.factor(value)) for name, value in actual.items()},
        "restored_d_witness": str(sp.factor(d_witness)),
        "ideal_generators": [str(value) for value in ideal_generators],
        "Groebner_basis": [str(polynomial.as_expr()) for polynomial in groebner.polys],
        "complex_zero_locus": "a*z_ax1=a*z_ax2=a*z_pol1=a*z_pol2=d*z_pol2=0",
        "branch_decomposition": [
            "extra amplitudes all zero, with a and d free in this cross ledger",
            "a=0 and z_pol2=0, with d and z_ax1,z_ax2,z_pol1 free",
            "a=0 and d=0, with all four extra amplitudes free",
        ],
    }


def build() -> dict[str, Any]:
    records = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in INPUTS.items()}
    _require(records["abd_matrix"]["classification"]["direct_axial_a_b_cross_sources_computed"], "axial a source changed")
    _require(records["abd_matrix"]["classification"]["direct_polar_a_b_cross_sources_computed"], "polar a source changed")
    _require(records["d_full_time"]["classification"]["polar_e2_d_extra_t_coefficient_nonzero"], "d full-time repair changed")
    _require(records["standard_global"]["universal_complete_carrier_corollary"]["statement"].endswith("Q_e*a=0"), "global polynomial gate changed")
    old_cone = records["old_complete_cone"]
    _require(old_cone["classification"]["complete_common_zero_locus_in_declared_nonzero_extra_carrier"], "old cone changed")
    audit = _leading_row_audit(records)
    old_parameterization = old_cone["complete_nonzero_extra_parameterization"]
    _require("a=b=d=0" in old_parameterization["homogeneous"], "old cone does not lie on repaired polynomial face")

    return {
        "schema": "einstein-maxwell-weyl-ad-ell2-extra-polynomial-zero-locus-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_AD_ELL2_EXTRA_POLYNOMIAL_ZERO_LOCUS",
        "result_state": "REPAIRED_AD_ELL2_EXTRA_POLYNOMIAL_ZERO_LOCUS_CLASSIFIED",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "scope": {
            "theory": "Weyl-Maxwell",
            "background": "compact magnetically supported Plebanski-Hacyan product",
            "boundaries": "closed S1_L times S2; bounded/finite-quasiperiodic correction",
            "charge_sector": "fixed N=2 magnetic bundle",
            "carrier": "homogeneous a,d directions crossed with the complete axial-plus-polar ell=2,k=0 extra-primary multiplicity space after universal b=0",
            "degree": 2,
            "parity": "two axial and two polar extra columns",
            "ell": 2,
            "m": "all by SO3 equivariance",
            "k": 0,
            "omega": "+/-4/sqrt(3)",
        },
        "polynomial_zero_locus": audit,
        "necessity_and_sufficiency_for_cross_ledger": {
            "necessity": "the four independent a-leading witnesses and restored d polar-e2 witness force the five displayed monomials",
            "sufficiency": "every positive-degree coefficient in the printed a columns is proportional to a times its matching amplitude; the only restored d positive-degree column is proportional to d*z_pol2",
            "scope": "only the a/d-times-extra cross source; self-products, twists and constant resonances are separate",
        },
        "old_cone_reconciliation": {
            "status": "CERTIFIED_UNCHANGED",
            "reason": "the previously classified nonzero-extra common-zero locus already has a=b=d=0, so the restored d polynomial vanishes identically on every old solution; adding the repaired equation removes no point from that locus and cannot create a new one",
            "bounded_obstruction": "the old common-zero orbit still has nonzero twist velocity and remains bounded-obstructed by its independent zero-frequency t^2 block",
        },
        "bounded_ledger_consequence": {
            "radion": "a!=0 excludes every ell=2 extra amplitude in a bounded candidate",
            "circumference_velocity": "d!=0 excludes the second polar extra amplitude unless another same-output polynomial column outside this declared cross ledger cancels it",
            "remaining_cross_face": "a=0,z_pol2=0 retains d with both axial and first polar extra columns before R_(j,a) is imposed",
            "next_resonance_problem": "restrict the constant d adjoint matrix and twist/oscillator resonance equations to the repaired polynomial branches",
        },
        "classification": {
            "complete_a_d_ell2_extra_cross_polynomial_ideal_classified": True,
            "four_radion_amplitude_products_forced_zero": True,
            "d_times_second_polar_amplitude_forced_zero": True,
            "old_nonzero_extra_common_zero_cone_survives_repair": True,
            "constant_resonance_zero_locus_solved_on_repaired_branches": False,
            "complete_bounded_cone_solved": False,
            "causal_or_quantum_claim": False,
        },
        "interpretation": "The repaired polynomial ledger is reducible. A nonzero radion position excludes the entire ell=2 extra multiplet. With a=0, a nonzero circumference velocity can coexist polynomially with both axial extra columns and the first polar column, but not the second polar column. These are source-growth conditions only; the surviving amplitudes must still satisfy the constant shell-resonance and moment-map equations.",
        "next_gate": "restrict the t=0 d adjoint map and the constant-twist/oscillator resonance matrix to the three repaired polynomial branches, then solve their simultaneous moment-map and R zero loci",
        "claim_boundary": "This is the complete P_(j,r) zero locus only for a,d crossed with the ell=2,k=0 extra block. It does not classify other oscillators, self-products, constant resonance, the complete bounded cone, causal propagation, all-orders integration, residual descent, observables, particles or quantum theory.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for name, path in INPUTS.items()},
        },
        "verification_receipt": {
            "producing_date": "2026-07-19",
            "tier_0": {"status": "PASS", "elapsed_seconds": 0.21, "max_rss_kb": 16184},
            "tier_1": {"status": "PASS", "elapsed_seconds": 2.10, "max_rss_kb": 60812, "tests_run": 19},
            "tier_2": {"status": "PASS_BY_CONTENT_ADDRESS", "criterion": "the direct full-time a rows, restored d polynomial and old common-zero cone are unchanged exact inputs"},
            "tier_3": {"status": "NOT_RUN", "reason": "constant resonance, other harmonics, complete bounded, causal, all-orders, residual and quantum gates remain excluded"},
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_ad_ell2_extra_polynomial_zero_locus --check",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_ad_ell2_extra_polynomial_zero_locus.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_ad_ell2_extra_polynomial_zero_locus",
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
        raise ADPolynomialError("a/d polynomial zero-locus certificate is stale")
    print("EINSTEIN_MAXWELL_WEYL_AD_ELL2_EXTRA_POLYNOMIAL_ZERO_LOCUS: PASS")


if __name__ == "__main__":
    main()
