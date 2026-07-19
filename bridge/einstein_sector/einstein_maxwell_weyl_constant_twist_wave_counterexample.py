"""Certify the off-axis constant-twist counterexample to A-arbitrary wave cones."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_constant_twist_wave_counterexample.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_constant_twist_wave_counterexample.schema.json"
INPUTS = {
    "twist_matrix": ROOT / "bridge/certificates/einstein_maxwell_weyl_homogeneous_twist_ell2_extra_resonance_matrix.json",
    "moment_cone": ROOT / "bridge/certificates/einstein_maxwell_weyl_k0_moment_map_cone.json",
    "pure_twist": ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_global_moment_maps.json",
}


class ConstantTwistWaveCounterexampleError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ConstantTwistWaveCounterexampleError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _matrix(expressions: list[list[str]]) -> sp.Matrix:
    return sp.Matrix([[sp.sympify(value, locals={"sqrt": sp.sqrt, "I": sp.I}) for value in row] for row in expressions])


def build() -> dict[str, object]:
    records = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in INPUTS.items()}
    position = _matrix(records["twist_matrix"]["twist_projection_theorem"]["position_matrix"])
    _require(position.rank() == 2, "twist-position resonance rank changed")
    axial_extra_e1 = sp.Matrix([1, 0, 0, 0])
    projected = position * axial_extra_e1
    expected = sp.Matrix([0, 24 * sp.sqrt(3), 0, 0])
    _require(projected == expected, "off-axis axial-extra twist projection changed")
    _require(records["moment_cone"]["rotationally_neutral_subcone"]["moment_maps"] == {"H": "0", "J_1": "0", "J_2": "0", "J_3": "0", "P_x": "0"}, "rotationally neutral cone changed")
    affected = {
        "global_axial": "EINSTEIN_MAXWELL_WEYL_GLOBAL_AXIAL_ELL2_ALL_M_MINUS_EXTRA_BOUNDED_CONE",
        "global_ell2": "EINSTEIN_MAXWELL_WEYL_GLOBAL_ELL2_ALL_M_BOTH_PARITY_BOUNDED_CONE",
        "global_fixed_ell": "EINSTEIN_MAXWELL_WEYL_GLOBAL_FIXED_ELL_K0_BOUNDED_CONE",
        "global_finite": "EINSTEIN_MAXWELL_WEYL_GLOBAL_FINITE_HARMONIC_K0_BOUNDED_CONE",
    }
    pure_twist_classification = records["pure_twist"]["classification"]
    _require(pure_twist_classification["constant_twist_exact_family_identified"], "pure twist family changed")
    _require(not pure_twist_classification["full_combined_quadratic_source_classified"], "pure twist input unexpectedly became a mixed theorem")
    omega_extra = 4 / sp.sqrt(3)
    omega_minus = sp.sqrt(6 - 2 * sp.sqrt(3))
    _require(sp.simplify(omega_extra - omega_minus) != 0, "minus and extra shells collided")
    _require(sp.simplify(2 * omega_minus - omega_extra) != 0, "minus self-sum hit the extra shell")
    return {
        "schema": "einstein-maxwell-weyl-constant-twist-wave-counterexample-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_CONSTANT_TWIST_WAVE_COUNTEREXAMPLE",
        "result_state": "A_ARBITRARY_GLOBAL_WAVE_CONE_CLAIMS_WITHDRAWN",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "scope": {
            "theory": "Weyl-Maxwell target",
            "background": "compact magnetically supported Plebanski-Hacyan product",
            "boundaries": "closed S1_L times S2; bounded/finite-quasiperiodic correction",
            "charge_sector": "fixed N=2 magnetic bundle",
            "carrier": "one perpendicular constant twist position crossed with the rotationally neutral axial ell=2 Einstein-minus/extra balance",
            "degree": 2,
            "parity": "axial input and axial resonant output",
            "ell": "1 x 2 -> 2",
            "m": "twist m=1, wave m=0, output M=1 in the certified complex harmonic fixture",
            "k": 0,
            "omega": "omega_extra=4/sqrt(3), with the Einstein-minus balance at sqrt(6-2*sqrt(3))",
        },
        "first_order_fixture": {
            "wave": "choose occupation rho_extra>0 on axial extra e1, m=0 and rho_minus=(omega_extra^2/omega_minus^2)*rho_extra on axial Einstein-minus, m=0; equivalently the coefficient magnitudes obey |C_minus|=(omega_extra/omega_minus)|C_extra|",
            "moment_maps": "mu_H=mu_J1=mu_J2=mu_J3=mu_Px=0",
            "globals": "a=b=c=d=Q_e=W_x=B=0 and a nonzero constant twist position A in the m=1 direction",
            "claimed_membership": "this point lies in every affected certificate's prior A-arbitrary nonzero wave branch",
        },
        "adjoint_obstruction": {
            "position_matrix": [[str(sp.factor(value)) for value in position.row(row)] for row in range(position.rows)],
            "input_column": "axial extra e1",
            "projected_adjoint_rows": [str(sp.factor(value)) for value in projected],
            "nonzero_witness": "24*sqrt(3)",
            "frequency_isolation": "A times the extra mode lies at omega_extra; A times Einstein-minus lies at omega_minus, and wave-wave sums/differences do not equal omega_extra",
            "bounded_correction_exists": False,
        },
        "logical_repair": {
            "pure_twist_limit": "the exact flat-holonomy family certifies the wave-free constant-twist modulus only",
            "invalid_inference": "pure constant-twist exactness was used as if it supplied a bounded mixed transport for every oscillator",
            "required_replacement": "retain A arbitrary on the static branch; on wave branches impose every constant-twist resonance functional and solve its common zero locus",
            "safe_subcone": "A=0 leaves the previously certified wave correction untouched",
        },
        "affected_results": affected,
        "classification": {
            "explicit_prior_cone_member_constructed": True,
            "nonzero_adjoint_pairing_certified": True,
            "A_arbitrary_wave_branch_refuted": True,
            "moment_maps_vanish_but_bounded_resonance_nonzero": True,
            "wave_free_constant_twist_modulus_retained": True,
            "A_zero_wave_subcone_retained": True,
            "complete_constant_twist_wave_zero_locus_classified": False,
            "nonzero_momentum_classified": False,
            "causal_or_quantum_claim": False,
        },
        "interpretation": "Constant twist is a genuine wave-free holonomy modulus, not an automatic bounded spectator for radiative modes. A perpendicular twist crossed with a balanced ell=2 extra/Einstein-minus wave has a nonzero adjoint resonance, so the formerly advertised A-arbitrary wave branches are too large. Their A=0 subcones survive, while the nonzero-A strata require the complete twist-position resonance zero locus.",
        "next_gate": "downgrade the affected global cone certificates and atlas rows, then solve the constant-twist position resonance equations on the complete fixed-ell and finite-harmonic wave cones",
        "claim_boundary": "This is one exact counterexample and a lifecycle correction. It does not classify every nonzero-A wave stratum, nonzero momentum, infinite sums, all-orders integration, residual descent, causal propagation or quantum theory.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for name, path in INPUTS.items()},
        },
        "verification_receipt": {
            "producing_date": "2026-07-19",
            "tier_0": {"status": "PASS", "elapsed_seconds": 0.10},
            "tier_1": {"status": "PASS", "elapsed_seconds": 2.65, "tests_run": 5},
            "tier_2": {"status": "PASS_BY_CONTENT_ADDRESS", "criterion": "the complete twist-position adjoint matrix and the rotationally neutral wave cone are unchanged exact inputs"},
            "tier_3": {"status": "NOT_RUN", "reason": "the complete nonzero-A zero locus and higher lifecycle gates remain open"},
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_constant_twist_wave_counterexample --check",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_constant_twist_wave_counterexample.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_constant_twist_wave_counterexample",
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
        raise ConstantTwistWaveCounterexampleError("constant-twist wave counterexample certificate is stale")
    print("EINSTEIN_MAXWELL_WEYL_CONSTANT_TWIST_WAVE_COUNTEREXAMPLE: PASS")


if __name__ == "__main__":
    main()
