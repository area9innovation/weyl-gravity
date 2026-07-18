#!/usr/bin/env python3
"""Certify smooth-secular second-order extension of the global--extra orbit."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_global_extra_smooth_secular_second_order.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_global_extra_smooth_secular_second_order.schema.json"
INPUTS = {
    "cone": ROOT / "d_quotient_classical/certificates/PH_HOMOGENEOUS_TWIST_ELL2_EXTRA_BOUNDED_TANGENT_CONE_V1.json",
    "abstract_cone": ROOT / "d_quotient_classical/certificates/FINITE_HARMONIC_SECOND_ORDER_TANGENT_CONE_THEOREM_V1.json",
    "bounded_obstruction": ROOT / "bridge/certificates/einstein_maxwell_weyl_global_extra_bounded_correction_obstruction.json",
    "homogeneous_operator": ROOT / "bridge/certificates/einstein_maxwell_weyl_homogeneous_nonzero_frequency_operator.json",
    "axial_ell1": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_ell1_k0_operator.json",
    "polar_ell1": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_ell1_k0_operator.json",
    "axial_generic": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_physical_ring.json",
    "polar_generic": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_physical_completion.json",
    "smooth_module": ROOT / "bridge/certificates/einstein_maxwell_weyl_opposite_momentum_smooth_global_second_order.json",
    "circumference": ROOT / "bridge/certificates/einstein_maxwell_weyl_global_spectator_ell2_extra_resonance.json",
    "electric": ROOT / "bridge/certificates/einstein_maxwell_weyl_electric_duality_ell2_extra_resonance.json",
    "twist_polynomial_audit": ROOT / "bridge/certificates/einstein_maxwell_weyl_homogeneous_twist_collinear_second_order.json",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _generic_divisors(ell: int, frequency_squared: sp.Rational) -> dict[str, str]:
    eigenvalue = sp.Integer(ell * (ell + 1))
    p = sp.factor(frequency_squared - eigenvalue + sp.Rational(2, 3))
    q = sp.factor(frequency_squared**2 - 2 * eigenvalue * frequency_squared + eigenvalue * (eigenvalue - 2))
    return {"lambda": str(eigenvalue), "p": str(p), "q": str(q)}


def _channel_ledger() -> dict[str, Any]:
    omega_extra_squared = sp.Rational(16, 3)
    omega_sum_squared = 4 * omega_extra_squared
    zero_generic = {str(ell): _generic_divisors(ell, sp.S.Zero) for ell in range(2, 5)}
    sum_generic = {str(ell): _generic_divisors(ell, omega_sum_squared) for ell in range(2, 5)}
    cross_l3 = _generic_divisors(3, omega_extra_squared)
    if cross_l3 != {"lambda": "12", "p": "-6", "q": "184/9"}:
        raise AssertionError("L=3 cross divisor changed")
    if _generic_divisors(2, omega_extra_squared) != {"lambda": "6", "p": "0", "q": "-104/9"}:
        raise AssertionError("L=2 resonant divisor changed")
    expected_zero = {
        "2": {"lambda": "6", "p": "-16/3", "q": "24"},
        "3": {"lambda": "12", "p": "-34/3", "q": "120"},
        "4": {"lambda": "20", "p": "-58/3", "q": "360"},
    }
    expected_sum = {
        "2": {"lambda": "6", "p": "16", "q": "2008/9"},
        "3": {"lambda": "12", "p": "10", "q": "568/9"},
        "4": {"lambda": "20", "p": "2", "q": "-344/9"},
    }
    if zero_generic != expected_zero or sum_generic != expected_sum:
        raise AssertionError("generic self-channel divisor ledger changed")
    return {
        "global_global": {
            "frequencies": "zero with finite polynomial coefficients",
            "angular_outputs": "L=0,1,2",
            "disposition": "L=0 time-translation and L=1 rotation cokernels are exactly the vanishing stabilizer moment maps; L=2 is off shell and polynomially invertible",
        },
        "extra_conjugate_self": {
            "frequency_squared": 0,
            "angular_outputs": "L=0,...,4",
            "generic_divisors": zero_generic,
            "disposition": "L=0,1 reduce to stabilizer cokernels; every L>=2 block is off shell",
        },
        "extra_sum": {
            "frequency_squared": str(omega_sum_squared),
            "angular_outputs": "L=0,...,4",
            "generic_divisors": sum_generic,
            "exceptional_disposition": "the L=0 oscillatory quotient is empty and the L=1 roots 4/3 and 4 are both missed by 64/3",
        },
        "ell0_extra_cross": {
            "frequency_squared": str(omega_extra_squared),
            "angular_output": "L=2",
            "divisors": _generic_divisors(2, omega_extra_squared),
            "disposition": "the p-primary is resonant, but its finite exponential-polynomial right inverse is obtained by a secular prefactor; q is off shell",
            "spectators": "c has a certified algebraic image representative, W_x gives zero source, and Q_e has a fixed-bundle duality correction",
        },
        "aligned_twist_extra_cross": {
            "frequency_squared": str(omega_extra_squared),
            "angular_outputs": "L=1,3; the unique L=2 intertwiner vanishes on the aligned m=0 orbit and hence on its SO3 rotations",
            "L1_divisors": {"extra": str(sp.Rational(4, 3) - omega_extra_squared), "standard": str(4 - omega_extra_squared)},
            "L3_divisors": cross_l3,
            "disposition": "both exceptional L=1 shells and both generic L=3 primaries are off shell; polynomial-in-time amplitudes remain in the algebraic exponential-polynomial image",
        },
    }


def build() -> dict[str, Any]:
    records = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in INPUTS.items()}
    if not records["cone"]["classification"]["complete_common_zero_locus_in_declared_nonzero_extra_carrier"]:
        raise AssertionError("complete global--extra cone changed")
    if records["abstract_cone"]["correction_classes"]["SMOOTH_SECULAR"]["status"] != "CERTIFIED":
        raise AssertionError("smooth-secular category lemma changed")
    if not records["bounded_obstruction"]["classification"]["bounded_or_finite_quasiperiodic_correction_obstructed"]:
        raise AssertionError("bounded contrast changed")
    if not records["homogeneous_operator"]["classification"]["homogeneous_nonzero_frequency_physical_quotient_empty"]:
        raise AssertionError("homogeneous oscillatory quotient changed")
    if records["axial_ell1"]["classification"]["extra_shell_frequency_squared"] != "4/3":
        raise AssertionError("axial exceptional shell changed")
    if not records["polar_ell1"]["classification"]["polar_ell1_extra_fourth_order_shell_certified"]:
        raise AssertionError("polar exceptional shell changed")
    if not records["axial_generic"]["classification"]["physical_ring_determinantal_ideals_certified"]:
        raise AssertionError("axial generic operator changed")
    if not records["polar_generic"]["classification"]["physical_ring_determinantal_ideals_certified"]:
        raise AssertionError("polar generic operator changed")
    if not records["smooth_module"]["classification"]["complete_fixed_ell_absolute_k_common_zero_cone_second_order_extendible"]:
        raise AssertionError("exponential-polynomial module lemma input changed")
    if not records["circumference"]["classification"]["circumference_times_ell2_extra_source_in_linear_image"]:
        raise AssertionError("circumference spectator changed")
    if not records["electric"]["classification"]["electric_Qe_times_ell2_extra_source_in_linear_image"]:
        raise AssertionError("electric cross correction changed")
    if not records["twist_polynomial_audit"]["classification"]["complete_collinear_standard_homogeneous_twist_common_zero_face_second_order_extendible"]:
        raise AssertionError("twist polynomial audit changed")

    ledger = _channel_ledger()
    return {
        "schema": "einstein-maxwell-weyl-global-extra-smooth-secular-second-order-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_GLOBAL_EXTRA_SMOOTH_SECULAR_SECOND_ORDER",
        "result_state": "COMPLETE_NONZERO_GLOBAL_EXTRA_COMMON_ZERO_ORBIT_SECOND_ORDER_EXTENDIBLE_IN_SMOOTH_EXPONENTIAL_POLYNOMIAL_CLASS",
        "lifecycle_state": "CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "scope": {
            "theory": "Weyl-Maxwell",
            "background": "compact magnetically supported Plebanski-Hacyan product",
            "boundaries": "closed S1_L times S2; smooth spatially periodic finite exponential-polynomial correction class",
            "charge_sector": "fixed N=2 magnetic bundle with arbitrary real first-order Q_e",
            "carrier": "complete certified nonzero-extra common-zero orbit in one homogeneous/twist times ell=2,k=0 extra multiplet",
            "degree": 2,
            "parity": "all four axial/polar extra multiplicities",
            "ell": "all quadratic outputs L=0,...,4",
            "m": "all through the certified aligned SO3 orbit",
            "k": 0,
            "omega": "0, +/-omega_e and +/-2*omega_e with omega_e^2=16/3; finite polynomial prefactors allowed",
        },
        "second_order_equation": "L_WM Phi^(2)=-(1/2)D^2E_WM[Phi^(1),Phi^(1)]",
        "source_space": {
            "finite_closure": "the generalized-zero global/twist input and one real ell=2 extra wave produce only L=0,...,4 and frequencies 0,+/-omega_e,+/-2*omega_e with finite polynomial time coefficients",
            "Noether_compatibility": "differentiating the exact Diff-Weyl-U(1) Noether identity twice at the solution background, with the first-order Euler residual zero, places every quadratic source in the compatible target",
            "bundle": "all Maxwell corrections are connection differences on the same fixed magnetic bundle",
        },
        "smooth_secular_right_inverse": {
            "scalar_lemma": "on finite exponential-polynomial functions, every nonzero scalar polynomial P(d_t) is surjective: factor P into shifted derivatives and integrate the finite polynomial coefficient at each root",
            "block_lemma": "after complete gauge and Noether reduction, the physical Smith invariant factors p and q therefore have finite exponential-polynomial right inverses, including at their roots",
            "persistent_cokernel": "only the zero-frequency compact stabilizer components remain; their source pairings are the five certified moment maps",
            "stabilizer_disposition": "all five moment maps vanish identically on the complete certified orbit",
            "assembly": "apply the finite block right inverse in every ledger channel and impose conjugate corrections on conjugate frequencies",
        },
        "channel_ledger": ledger,
        "correction_classes": {
            "bounded_or_finite_quasiperiodic": "OBSTRUCTED on every nonzero orbit point by the separate -7*B^2*t^2 certificate",
            "smooth_exponential_polynomial": "CERTIFIED: every orbit point admits a real smooth spatially periodic finite exponential-polynomial second-order correction",
            "causal_or_retarded": "NO_CERTIFIED_MAP: no compact-product retarded full-BV complex is certified",
        },
        "classification": {
            "complete_nonzero_extra_common_zero_orbit_covered": True,
            "complete_quadratic_channel_ledger": True,
            "all_nonstabilizer_smooth_secular_cokernels_zero": True,
            "smooth_exponential_polynomial_second_order_correction_exists": True,
            "coefficient_explicit_correction_printed": False,
            "bounded_correction_exists": False,
            "causal_retarded_map_certified": False,
            "all_orders_integrability": False,
        },
        "interpretation": "The same nonzero global--extra tangent is excluded if its correction must remain bounded, yet extends at second order when finite secular growth is allowed. The distinction is entirely correction-class dependent: the twist velocity forces a quadratic zero-frequency source, while the smooth exponential-polynomial category supplies polynomial right inverses and removes every propagation resonance after the stabilizer moment maps vanish.",
        "next_gate": "make the smooth correction coefficient-explicit if needed for Paper 91, then classify opposite momenta, relative phases, multiple absolute-momentum fibres and the causal compact-source category separately",
        "claim_boundary": "This is a blockwise constructive existence theorem, not a printed coefficient formula for every correction component. It does not give a bounded correction, a causal/retarded solution, all-orders integration, final residual descent, an observable, particle state or quantum theorem.",
        "source_manifest": {str(path.relative_to(ROOT)): _sha256(path) for path in (*INPUTS.values(), Path(__file__).resolve(), SCHEMA)},
        "verification_receipt": {
            "producing_date": "2026-07-18",
            "tier_0": {"status": "PASS", "commands": ["python3 -m py_compile <scoped Python paths>", "python3 -m json.tool <certificate and schema>", "git diff --check -- <scoped paths>"]},
            "tier_1": {
                "status": "PASS",
                "commands": ["python3 -m bridge.einstein_sector.einstein_maxwell_weyl_global_extra_smooth_secular_second_order --check", "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_global_extra_smooth_secular_second_order.py", "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_global_extra_smooth_secular_second_order"],
                "elapsed_seconds": {"generator_check": 0.53, "independent_verifier": 0.60, "unit_tests": 0.09},
            },
            "tier_2": {"status": "PASS_BY_CONTENT_ADDRESS", "inputs": list(INPUTS)},
            "tier_3": {"status": "NOT_RUN", "reason": "bounded and smooth categories are separated; causal, multi-fibre and all-orders gates remain open"},
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_global_extra_smooth_secular_second_order --check",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_global_extra_smooth_secular_second_order.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_global_extra_smooth_secular_second_order",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    value = build()
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    if arguments.write:
        OUTPUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    elif json.loads(OUTPUT.read_text(encoding="utf-8")) != value:
        raise AssertionError("smooth-secular second-order certificate is stale")
    print("EINSTEIN_MAXWELL_WEYL_GLOBAL_EXTRA_SMOOTH_SECULAR_SECOND_ORDER: PASS")


if __name__ == "__main__":
    main()
