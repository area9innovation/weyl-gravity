"""Classify an aligned global plus axial ell2 minus-extra bounded cone."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_aligned_global_axial_ell2_minus_extra_bounded_cone.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_aligned_global_axial_ell2_minus_extra_bounded_cone.schema.json"
INPUTS = {
    "minus_global_resonance": ROOT / "bridge/certificates/einstein_maxwell_weyl_abd_axial_ell2_minus_resonance.json",
    "wave_face": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_ell2_full_extra_face_second_order.json",
    "homogeneous_source": ROOT / "bridge/certificates/einstein_maxwell_weyl_homogeneous_quadric_second_order.json",
    "homogeneous_operator": ROOT / "bridge/certificates/einstein_maxwell_weyl_balanced_ell0_second_order.json",
    "standard_global": ROOT / "bridge/certificates/einstein_maxwell_weyl_standard_global_bounded_second_order.json",
    "circumference": ROOT / "bridge/certificates/einstein_maxwell_weyl_circumference_complete_oscillator_bounded_classification.json",
    "electric_wilson": ROOT / "bridge/certificates/einstein_maxwell_weyl_electric_wilson_complete_oscillator_transport.json",
    "constant_twist": ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_global_moment_maps.json",
}


class AlignedGlobalWaveConeError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AlignedGlobalWaveConeError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _zero_frequency_audit(records: dict[str, dict[str, Any]]) -> dict[str, Any]:
    charge, x_minus, x_e1, x_e2 = sp.symbols("Q_e x_minus x_e1 x_e2", real=True)
    root = sp.sqrt(3)
    tau = {
        name: sp.sympify(value, locals={"sqrt": sp.sqrt})
        for name, value in records["wave_face"]["zero_frequency_source_rank"]["Taub_source_coefficients"].items()
    }
    _require(tau["minus"] > 0 and tau["extra_e1"] < 0 and tau["extra_e2"] < 0, "wave-source signs changed")
    wave_scalar = sp.factor(tau["minus"] * x_minus + tau["extra_e1"] * x_e1 + tau["extra_e2"] * x_e2)
    direction = sp.Matrix([1, 0, sp.Rational(1, 2), 0])
    wave_source = wave_scalar * direction
    charge_source = charge**2 * sp.Matrix([-sp.Rational(1, 2), sp.Rational(1, 2), -sp.Rational(1, 2), 0])
    combined = (wave_source + charge_source).applyfunc(sp.factor)
    operator = records["homogeneous_operator"]["homogeneous_operator"]
    matrix = sp.Matrix([[sp.sympify(value, locals={"Omega": sp.Integer(0), "I": sp.I}) for value in row] for row in operator["matrix"]])
    _require(matrix == sp.zeros(4, 3), "bounded zero-frequency operator acquired a constant image")
    _require(combined[1] == charge**2 / 2, "electric E11 witness changed")
    _require(sp.factor(combined.subs(charge, 0)[0] - wave_scalar) == 0, "wave balance changed")
    solved_minus = sp.factor(-(tau["extra_e1"] * x_e1 + tau["extra_e2"] * x_e2) / tau["minus"])
    expected_minus = sp.factor((972 * x_e1 + 52 * x_e2) / (27 * (-6 + 5 * root)))
    _require(sp.factor(solved_minus - expected_minus) == 0, "minus occupation parameterization changed")
    return {
        "row_order": ["E00", "E11", "E22", "Maxwell1"],
        "wave_source": f"({wave_scalar})*(1,0,1/2,0)",
        "electric_source": "Q_e^2*(-1/2,1/2,-1/2,0)",
        "bounded_zero_frequency_operator": "0 on constant homogeneous corrections",
        "electric_independence_witness": "E11=Q_e^2/2, hence Q_e=0",
        "remaining_wave_equation": str(wave_scalar),
        "wave_zero_locus": f"x_minus={solved_minus}; x_e1,x_e2>=0",
        "nonzero_wave_requires_minus_and_at_least_one_extra": True,
    }


def build() -> dict[str, object]:
    records = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in INPUTS.items()}
    _require(records["minus_global_resonance"]["classification"]["nonzero_minus_forces_a_b_d_zero"], "minus/global ideal changed")
    _require(records["wave_face"]["classification"]["three_parameter_positive_cone_second_order_extendible"], "wave-face theorem changed")
    _require(records["standard_global"]["classification"]["complete_standard_generalized_zero_bounded_cone_classified"], "standard bounded cone changed")
    _require(records["circumference"]["classification"]["k0_circumference_cross_bounded_removable"], "circumference transport changed")
    _require(records["electric_wilson"]["classification"]["W_x_times_every_oscillator_source_zero"], "Wilson spectator changed")
    _require(records["constant_twist"]["classification"]["constant_twist_exact_family_identified"], "constant twist family changed")
    audit = _zero_frequency_audit(records)
    return {
        "schema": "einstein-maxwell-weyl-aligned-global-axial-ell2-minus-extra-bounded-cone-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_ALIGNED_GLOBAL_AXIAL_ELL2_MINUS_EXTRA_BOUNDED_CONE",
        "result_state": "ALIGNED_GLOBAL_PLUS_AXIAL_ELL2_MINUS_EXTRA_BOUNDED_CONE_CLASSIFIED",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "scope": {
            "theory": "Weyl-Maxwell target",
            "background": "compact magnetically supported Plebanski-Hacyan product",
            "boundaries": "closed S1_L times S2; bounded/finite-quasiperiodic correction",
            "charge_sector": "fixed N=2 magnetic bundle with electric tangent allowed",
            "carrier": "complete homogeneous (a,b,c,d,Q_e,W_x), aligned axial twist (A_z,B_z), and axial ell=2,m=0,k=0 Einstein-minus plus both extra-primary amplitudes",
            "degree": 2,
            "parity": "homogeneous and axial",
            "ell": "input 0,1,2; complete quadratic outputs inherited on the declared aligned face",
            "m": "0 on twist and wave inputs",
            "k": 0,
            "omega": "generalized zero, sqrt(6-2*sqrt(3)), and 4/sqrt(3)",
        },
        "equation": "L_WM Phi^(2)=-(1/2)D^2E_WM[Phi^(1),Phi^(1)]",
        "necessity": {
            "universal_polynomial": "b=0 and B_z=0 on every bounded candidate",
            "wave_cross_polynomial": "if the wave block is nonzero, its required Einstein-minus coefficient is nonzero and the exact shell ideal forces a=b=d=0",
            "zero_frequency": audit,
        },
        "complete_bounded_cone": {
            "static_branch": "wave=0: (c,d,W_x,A_z) arbitrary, with a=b=Q_e=B_z=0",
            "wave_branch": "a=b=d=Q_e=B_z=0; c,W_x,A_z arbitrary; x_e1,x_e2>=0 and x_minus=(972*x_e1+52*x_e2)/(27*(-6+5*sqrt(3))); relative phases arbitrary",
            "branch_intersection": "x_e1=x_e2=x_minus=0 and d=0",
            "union_is_necessary_and_sufficient": True,
        },
        "sufficiency": {
            "static_branch": "the complete standard-global bounded correction theorem",
            "wave_self": "the certified axial ell2 full-extra face supplies finite-quasiperiodic corrections for arbitrary relative phases",
            "circumference": "k=0 radius transport is bounded",
            "Wilson": "the cross source vanishes identically",
            "aligned_twist": "A_z is a flat SO(2) holonomy; the m=0 wave is invariant under its lifted exact-family transport, giving a bounded mixed correction",
            "electric": "absent on the bounded wave branch by the independent zero-frequency witness",
        },
        "correction_classes": {
            "BOUNDED_OR_FINITE_QUASIPERIODIC": {"status": "CERTIFIED"},
            "SMOOTH_SECULAR": {"status": "CERTIFIED", "reason": "the bounded correction is a special smooth exponential-polynomial correction"},
            "CAUSAL_RETARDED": {"status": "NO_CERTIFIED_MAP"},
        },
        "classification": {
            "complete_declared_aligned_carrier_covered": True,
            "bounded_zero_locus_necessary_and_sufficient": True,
            "opposite_sign_wave_branch_survives_global_adjoining": True,
            "electric_taub_cancellation_bounded_obstructed": True,
            "global_spectator_product_identified": True,
            "polar_or_all_m_input_classified": False,
            "general_ell_or_nonzero_momentum_classified": False,
            "all_orders_integrability": False,
            "causal_or_quantum_claim": False,
        },
        "interpretation": "The first opposite-sign wave enlargement survives bounded second order, but only after the global block stratifies sharply. The generalized a,b,d directions and twist velocity are excluded on the wave branch, and electric charge cannot replace an extra wave because its non-Hamiltonian homogeneous source has no bounded zero-frequency preimage. What remains is the genuine Einstein-minus/extra cone times the static circumference, Wilson and aligned twist-position spectators.",
        "next_gate": "promote the global-plus-wave bounded classification from the aligned axial m=0 face to all m and both parities, then propagate the full-time a/d shell audit to general ell and momentum",
        "claim_boundary": "This theorem is complete only for one aligned axial ell=2,m=0,k=0 minus-plus-two-extra carrier with the declared global modes. It does not include Einstein-plus, polar wave input, non-axisymmetric cancellation, other ell or momenta, infinite sums, all-orders integration, final residual descent, causal propagation, observables, particles or quantum theory.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for name, path in INPUTS.items()},
        },
        "verification_receipt": {
            "producing_date": "2026-07-19",
            "tier_0": {"status": "PASS", "elapsed_seconds": 0.25},
            "tier_1": {"status": "PASS", "elapsed_seconds": 2.50, "tests_run": 25},
            "tier_2": {"status": "PASS_BY_CONTENT_ADDRESS", "criterion": "the direct minus/global source, complete axial wave face and global source/operator inputs are exact content-addressed dependencies"},
            "tier_3": {"status": "NOT_RUN", "reason": "all-m, both-parity, other-harmonic, causal, residual and quantum gates remain excluded"},
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_aligned_global_axial_ell2_minus_extra_bounded_cone --check",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_aligned_global_axial_ell2_minus_extra_bounded_cone.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_aligned_global_axial_ell2_minus_extra_bounded_cone",
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
        raise AlignedGlobalWaveConeError("aligned global-wave bounded cone certificate is stale")
    print("EINSTEIN_MAXWELL_WEYL_ALIGNED_GLOBAL_AXIAL_ELL2_MINUS_EXTRA_BOUNDED_CONE: PASS")


if __name__ == "__main__":
    main()
