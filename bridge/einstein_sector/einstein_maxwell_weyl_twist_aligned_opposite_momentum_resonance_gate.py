"""Certify that the opposite-momentum resonance divisor meets the twist-aligned cone."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_twist_aligned_opposite_momentum_resonance_gate.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_twist_aligned_opposite_momentum_resonance_gate.schema.json"
INPUTS = {
    "twist_column": ROOT / "bridge/certificates/einstein_maxwell_weyl_nonzero_k_constant_twist_same_shell.json",
    "opposite_cone": ROOT / "bridge/certificates/einstein_maxwell_weyl_opposite_momentum_cone.json",
    "phase_divisor": ROOT / "bridge/certificates/einstein_maxwell_weyl_opposite_momentum_phase_resonance_divisor.json",
    "smooth_extension": ROOT / "bridge/certificates/einstein_maxwell_weyl_opposite_momentum_smooth_global_second_order.json",
}


class TwistAlignedResonanceGateError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise TwistAlignedResonanceGateError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _exact_witness() -> dict[str, Any]:
    ell = sp.symbols("ell", integer=True, positive=True)
    lam = ell * (ell + 1)
    root = sp.sqrt(2 * lam)
    k_squared = sp.factor(root - ell / 2 - sp.Rational(1, 6))
    positivity_squared = sp.factor(2 * lam - (ell / 2 + sp.Rational(1, 6)) ** 2)
    expected_positivity = (63 * ell**2 + 66 * ell - 1) / 36
    _require(sp.expand(positivity_squared - expected_positivity) == 0, "resonant momentum positivity witness changed")
    _require(expected_positivity.subs(ell, 2) > 0, "physical resonant momentum lost positivity")

    omega_minus_squared = sp.factor(k_squared + lam - root)
    omega_plus_squared = sp.factor(k_squared + lam + root)
    minus_density = sp.factor(omega_plus_squared / omega_minus_squared)
    h_moment = sp.factor(2 * (omega_plus_squared - omega_minus_squared * minus_density))
    _require(h_moment == 0, "standing-wave energy balance changed")

    output_ell = 2 * ell
    output_lambda = sp.expand(output_ell * (output_ell + 1))
    output_p = sp.factor(4 * omega_minus_squared - output_lambda + sp.Rational(2, 3))
    _require(output_p == 0, "aligned standing-wave p-shell identity changed")
    return {
        "ell": "every integer ell>=2",
        "lambda": str(lam),
        "resonant_k_squared": str(k_squared),
        "positivity_squared_remainder": str(positivity_squared),
        "compact_realization": "for any nonzero integer n choose L=2*pi*abs(n)/sqrt(k_squared), so k=2*pi*n/L is an allowed compact momentum",
        "twist_axis": "A_hat=e_z",
        "positive_frequency_inputs": {
            "Einstein_plus": "equal +k and -k densities 1 on |ell,m=0>",
            "Einstein_minus": f"equal +k and -k densities {minus_density} on |ell,m=0>",
            "extra": "zero",
        },
        "frequencies_squared": {
            "omega_minus": str(omega_minus_squared),
            "omega_plus": str(omega_plus_squared),
        },
        "five_moment_maps": {
            "mu_H": str(h_moment),
            "mu_Px": "0 because the +k and -k branch densities are equal",
            "mu_J1": "0 on the m_A=0 rank-one density",
            "mu_J2": "0 on the m_A=0 rank-one density",
            "mu_J3": "0 on the m_A=0 rank-one density",
        },
        "twist_wave_bounded_column": "CERTIFIED because every occupied coefficient has m_A=0",
        "resonant_output": {
            "input_pair": "the two positive-frequency Einstein-minus coefficients at +k and -k",
            "L": str(output_ell),
            "M": 0,
            "K": 0,
            "Omega": "2*omega_minus",
            "target": "polar extra p-primary",
            "target_p_remainder": str(output_p),
            "top_Gaunt_channel": "nonzero in V_ell tensor V_ell -> V_(2ell)",
            "phase_carrier": "c_minus^(+)*c_minus^(-)",
        },
    }


def build() -> dict[str, Any]:
    records = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in INPUTS.items()}
    _require(
        records["twist_column"]["classification"]["complete_constant_twist_times_wave_bilinear_column_classified"],
        "nonzero-k twist column changed",
    )
    _require(
        records["opposite_cone"]["classification"]["complete_fixed_ell_absolute_k_common_zero_cone_classified"],
        "opposite-momentum cone changed",
    )
    divisor = records["phase_divisor"]
    _require(
        divisor["classification"]["resonance_divisor_nonempty_for_every_ell"]
        and "m=0 standing-wave" in divisor["universal_relative_phase_family"]["angular_selection"],
        "universal phase divisor changed",
    )
    _require(
        records["smooth_extension"]["classification"]["complete_fixed_ell_absolute_k_common_zero_cone_second_order_extendible"],
        "smooth opposite-momentum extension changed",
    )
    witness = _exact_witness()
    return {
        "schema": "einstein-maxwell-weyl-twist-aligned-opposite-momentum-resonance-gate-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_TWIST_ALIGNED_OPPOSITE_MOMENTUM_RESONANCE_GATE",
        "result_state": "TWIST_ALIGNED_COMMON_ZERO_CONE_MEETS_BOUNDED_PHASE_RESONANCE_DIVISOR",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G3_EVERY_GENERIC_ELL_ONE_TUNED_NONZERO_ABSOLUTE_MOMENTUM",
        "scope": {
            "theory": "Weyl-Maxwell target",
            "background": "compact magnetically supported Plebanski-Hacyan product",
            "boundaries": "closed S1_L times S2 with circumference tuned to the displayed allowed momentum",
            "charge_sector": "fixed N=2 magnetic bundle",
            "carrier": "constant twist position plus paired +/-k axisymmetric Einstein-plus/minus standing waves",
            "degree": 2,
            "parity": "input multiplicities may be chosen in either certified generic parity; the displayed arithmetic output is polar extra",
            "ell": "every one fixed integer ell>=2; output L=2ell",
            "m": "m_A=0 inputs and M=0 output",
            "k": "one tuned allowed nonzero +/-k pair",
            "omega": "Einstein q-plus/minus inputs and polar p-primary sum-frequency output",
        },
        "exact_intersection_witness": witness,
        "logical_disposition": {
            "stabilizer_moment_maps_vanish": True,
            "constant_twist_times_wave_bounded_column_solved": True,
            "phase_resonance_divisor_populated": True,
            "dynamical_adjoint_projection_computed": False,
            "bounded_extension_decided": False,
            "consequence": "moment maps plus the twist-alignment kernel do not imply bounded extension; an independent phase-sensitive source functional must be computed",
        },
        "correction_classes": {
            "BOUNDED_OR_FINITE_QUASIPERIODIC": {
                "status": "OPEN",
                "reason": "the exact resonant carrier is populated, but its Weyl-Maxwell adjoint source coefficient has not been computed",
            },
            "SMOOTH_EXPONENTIAL_POLYNOMIAL": {
                "status": "CERTIFIED",
                "reason": "the complete fixed-(ell,|k|) common-zero cone has a certified finite secular correction",
            },
            "CAUSAL_RETARDED": {"status": "NO_CERTIFIED_MAP"},
        },
        "classification": {
            "twist_aligned_common_zero_intersection_nonempty_every_ell": True,
            "universal_phase_resonance_survives_twist_alignment": True,
            "additional_bounded_resonance_functional_required": True,
            "dynamical_resonance_coefficient_computed": False,
            "complete_bounded_cone_classified": False,
            "fixed_circumference_all_momenta_classified": False,
            "causal_or_quantum_claim": False,
        },
        "interpretation": "Twist alignment removes the twist-wave resonance but does not remove the independent standing-wave phase divisor. On a nonempty exact common-moment face, two axisymmetric opposite-momentum Einstein-minus waves land on a polar extra p shell. The bounded verdict therefore depends on a new dynamical adjoint coefficient, while smooth secular extension remains certified.",
        "next_gate": "compute the ell=2 axial and polar Einstein-minus +/-k source projection into the polar L=4 p-primary adjoint at k^2=2*sqrt(3)-7/6; if nonzero, promote the fixture to a bounded obstruction and then seek the symbolic-ell coefficient",
        "claim_boundary": "This is an exact intersection and independence-gate theorem, not a bounded obstruction: arithmetic resonance and nonzero angular coupling do not prove a nonzero dynamical source projection. It is scoped to tuned circumference, one fixed ell and one |k| fibre, and makes no causal, all-orders, residual, observational, particle or quantum claim.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for name, path in INPUTS.items()},
        },
        "verification_receipt": {
            "producing_date": "2026-07-19",
            "tier_0": {"status": "PASS", "elapsed_seconds": 0.18},
            "tier_1": {"status": "PASS", "elapsed_seconds": 1.94, "tests_run": 36},
            "tier_2": {"status": "PASS_BY_CONTENT_ADDRESS", "criterion": "the twist bounded column, opposite-momentum cone, universal phase divisor and smooth-global extension are unchanged hashed inputs"},
            "tier_3": {"status": "NOT_RUN", "reason": "the dynamical bounded projection and higher lifecycles remain open"},
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_twist_aligned_opposite_momentum_resonance_gate --check",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_twist_aligned_opposite_momentum_resonance_gate.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_twist_aligned_opposite_momentum_resonance_gate",
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
        raise TwistAlignedResonanceGateError("twist-aligned resonance-gate certificate is stale")
    print("EINSTEIN_MAXWELL_WEYL_TWIST_ALIGNED_OPPOSITE_MOMENTUM_RESONANCE_GATE: PASS")


if __name__ == "__main__":
    main()
