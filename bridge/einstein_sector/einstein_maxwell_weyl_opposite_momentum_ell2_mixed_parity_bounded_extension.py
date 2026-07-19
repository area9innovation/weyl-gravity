"""Certify one tuned mixed-parity bounded second-order extension."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_opposite_momentum_ell2_mixed_parity_bounded_extension.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_opposite_momentum_ell2_mixed_parity_bounded_extension.schema.json"
INPUTS = {
    "parity_matrix": ROOT / "bridge/certificates/einstein_maxwell_weyl_opposite_momentum_ell2_parity_resonance_matrix.json",
    "twist_gate": ROOT / "bridge/certificates/einstein_maxwell_weyl_twist_aligned_opposite_momentum_resonance_gate.json",
    "twist_column": ROOT / "bridge/certificates/einstein_maxwell_weyl_nonzero_k_constant_twist_same_shell.json",
    "ell0_nonzero": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_ell0_nonzero_fourier.json",
    "ell0_oscillatory": ROOT / "bridge/certificates/einstein_maxwell_weyl_homogeneous_nonzero_frequency_operator.json",
    "finite_generic": ROOT / "bridge/certificates/einstein_maxwell_weyl_finite_generic_smooth_global_second_order.json",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _nonzero_witness(value: sp.Expr, variable: sp.Symbol) -> dict[str, str]:
    polynomial = sp.Poly(sp.minpoly(value, variable), variable)
    constant = sp.factor(polynomial.nth(0))
    _require(constant != 0, f"nonzero witness collapsed for {value}")
    return {
        "residual": str(sp.factor(value)),
        "minimal_polynomial": str(polynomial.as_expr()),
        "minimal_polynomial_constant": str(constant),
    }


def _collision_census() -> dict[str, Any]:
    root = sp.sqrt(3)
    k_squared = 2 * root - sp.Rational(7, 6)
    omega_minus_squared = sp.Rational(29, 6)
    omega_plus_squared = omega_minus_squared + 4 * root
    omega_minus = sp.sqrt(omega_minus_squared)
    omega_plus = sp.sqrt(omega_plus_squared)
    frequency_squares = {
        "zero": sp.Integer(0),
        "two_omega_minus": 4 * omega_minus_squared,
        "two_omega_plus": 4 * omega_plus_squared,
        "omega_plus_plus_omega_minus": sp.expand((omega_plus + omega_minus) ** 2),
        "omega_plus_minus_omega_minus": sp.expand((omega_plus - omega_minus) ** 2),
    }
    momentum_squares = {"K_zero": sp.Integer(0), "K_two_k": 4 * k_squared}
    x = sp.Symbol("x")
    checks: list[dict[str, Any]] = []
    collisions: list[dict[str, str]] = []

    # This deliberately over-approximates the axisymmetric parity selection by
    # retaining L=1,3.  A unique collision in the larger carrier is therefore
    # also unique in the actual quadratic source.
    for momentum_name, output_k_squared in momentum_squares.items():
        for frequency_name, output_omega_squared in frequency_squares.items():
            for output_ell in range(1, 5):
                if output_ell == 1:
                    target_residuals = {
                        "exceptional_four": output_omega_squared - output_k_squared - 4,
                        "exceptional_four_thirds": output_omega_squared - output_k_squared - sp.Rational(4, 3),
                    }
                else:
                    output_lambda = output_ell * (output_ell + 1)
                    target_residuals = {
                        "p": output_omega_squared - output_k_squared - output_lambda + sp.Rational(2, 3),
                        "q": (output_omega_squared - output_k_squared - output_lambda) ** 2 - 2 * output_lambda,
                    }
                for target, residual in target_residuals.items():
                    residual = sp.expand(residual)
                    collision = residual.equals(0) is True
                    row: dict[str, Any] = {
                        "frequency": frequency_name,
                        "momentum": momentum_name,
                        "ell": output_ell,
                        "target": target,
                        "collision": collision,
                    }
                    if collision:
                        row["residual"] = "0"
                        collisions.append({key: str(row[key]) for key in ("frequency", "momentum", "ell", "target")})
                    else:
                        row["nonzero_witness"] = _nonzero_witness(residual, x)
                    checks.append(row)

    expected = [
        {
            "frequency": "two_omega_minus",
            "momentum": "K_zero",
            "ell": "4",
            "target": "p",
        }
    ]
    _require(collisions == expected, f"collision set changed: {collisions}")
    cross_minpoly = sp.Poly(sp.minpoly(frequency_squares["omega_plus_plus_omega_minus"], x), x)
    _require(
        cross_minpoly.as_expr() == 9 * x**4 - 348 * x**3 + 2500 * x**2 - 16704 * x + 20736,
        "cross-frequency minimal polynomial changed",
    )
    return {
        "input": {
            "k_squared": str(k_squared),
            "omega_minus_squared": str(omega_minus_squared),
            "omega_plus_squared": str(omega_plus_squared),
        },
        "frequency_squares": {name: str(sp.factor(value)) for name, value in frequency_squares.items()},
        "momentum_squares": {name: str(sp.factor(value)) for name, value in momentum_squares.items()},
        "cross_frequency_minimal_polynomial": str(cross_minpoly.as_expr()),
        "overcomplete_angular_range": "L=1,2,3,4; odd L are retained even though the declared m=0 parity carrier does not need them",
        "checks": checks,
        "check_count": len(checks),
        "collisions": collisions,
    }


def build() -> dict[str, Any]:
    records = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in INPUTS.items()}
    parity = records["parity_matrix"]
    _require(parity["classification"]["complete_tuned_L4_two_parity_resonance_matrix_certified"], "parity matrix changed")
    _require(parity["null_locus"]["mixed_L4_resonance_null_face_nonempty"], "mixed null face changed")
    _require(records["twist_gate"]["classification"]["twist_aligned_common_zero_intersection_nonempty_every_ell"], "twist gate changed")
    _require(records["twist_column"]["classification"]["complete_constant_twist_times_wave_bilinear_column_classified"], "twist column changed")
    _require(records["ell0_nonzero"]["classification"]["Diff_Weyl_U1_complex_exact_at_every_nonzero_Fourier_pair"], "ell=0 nonzero Fourier exactness changed")
    _require(records["ell0_oscillatory"]["classification"]["homogeneous_nonzero_frequency_physical_quotient_empty"], "homogeneous oscillatory quotient changed")
    generic = records["finite_generic"]
    _require(generic["classification"]["complete_reduced_adjoint_cokernel_decomposition_certified"], "generic cokernel theorem changed")
    _require(generic["complete_adjoint_cokernel_decomposition"]["zero_block"]["decomposition"].startswith("coker L_zero = span"), "zero-block stabilizer decomposition changed")

    census = _collision_census()
    return {
        "schema": "einstein-maxwell-weyl-opposite-momentum-ell2-mixed-parity-bounded-extension-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_OPPOSITE_MOMENTUM_ELL2_MIXED_PARITY_BOUNDED_EXTENSION",
        "result_state": "ONE_TUNED_TWIST_ALIGNED_MIXED_PARITY_TANGENT_HAS_BOUNDED_SECOND_ORDER_EXTENSION",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G1_EXPLICIT_ELL2_TUNED_NONZERO_MOMENTUM_MIXED_PARITY_FIXTURE",
        "scope": {
            "theory": "Weyl-Maxwell target",
            "background": "compact magnetically supported Plebanski-Hacyan product",
            "boundaries": "closed S1_L times S2 with k^2=2*sqrt(3)-7/6 allowed",
            "charge_sector": "fixed N=2 magnetic bundle",
            "carrier": "one constant twist position, paired m=0 Einstein-minus axial/polar waves at +/-k, and paired m=0 Einstein-plus balancing waves",
            "degree": 2,
            "parity": "mixed axial/polar Einstein-minus input; one normalized Einstein-plus multiplicity",
            "ell": "input ell=2; every quadratic output L=0,...,4",
            "m": "axisymmetric about the twist axis",
            "k": "+/-sqrt(2*sqrt(3)-7/6); output K=0,+/-2k",
            "omega": "q-minus and q-plus inputs; every zero, sum and difference output frequency",
        },
        "declared_tangent": {
            "twist": "any one nonzero constant twist position, rotated to A_hat=e_z",
            "Einstein_minus_raw_coefficients": "choose p_+=p_-=1 and a_+=a_-=sqrt(3), where p is polar and a is axial",
            "Einstein_plus_balance": "choose equal +/-k axisymmetric positive-frequency amplitudes in any one normalized q-plus multiplicity, with total positive Hamiltonian occupation equal to the absolute q-minus Hamiltonian occupation",
            "reality": "adjoin the complex-conjugate negative-frequency modes",
            "moment_maps": {
                "H": "zero by the declared q-plus/q-minus occupation balance",
                "P_x": "zero because every occupied branch has equal +k and -k occupation",
                "J_1_J_2_J_3": "zero because every wave coefficient lies in m_A=0 and constant twist position carries no stabilizer charge",
            },
        },
        "collision_census": census,
        "bounded_blockwise_proof": {
            "twist_self": "removable on the exact static constant-twist branch",
            "twist_wave": "the complete nonzero-k twist-column theorem kills every same-shell source on m_A=0 and supplies bounded inverses for the neighboring outputs",
            "wave_wave_zero_block": "the complete reduced zero-block cokernel is stab^*; all five declared moment maps vanish",
            "wave_wave_L0_nonzero_Fourier": "the direct exceptional complex is exact modulo Diff-Weyl-U1 at every nonzero Fourier pair",
            "wave_wave_nonzero_frequency": "the exact census finds only one p/q or exceptional shell collision in an angular over-approximation",
            "unique_collision": "L=4,K=0,Omega=2omega_- on the p-primary",
            "unique_collision_projection": "both independent L=4 adjoint functionals vanish at a_+=sqrt(3)p_+ and a_-=sqrt(3)p_-",
            "conclusion": "every finite quadratic source block is in the image of a bounded harmonic inverse, so their finite real sum is a bounded finite-quasiperiodic second-order correction",
        },
        "correction_classes": {
            "BOUNDED_OR_FINITE_QUASIPERIODIC": {
                "status": "CERTIFIED",
                "equation": "L_WM Phi^(2)=-(1/2)D^2E_WM[Phi^(1),Phi^(1)]",
                "scope": "the one declared tuned mixed-parity tangent",
            },
            "SMOOTH_EXPONENTIAL_POLYNOMIAL": {
                "status": "CERTIFIED",
                "reason": "the bounded correction is already in this larger class",
            },
            "CAUSAL_RETARDED": {"status": "NO_CERTIFIED_MAP"},
        },
        "classification": {
            "complete_exact_collision_census_for_declared_tangent": True,
            "unique_nonzero_frequency_collision_is_L4_p_two_omega_minus": True,
            "unique_collision_canceled_on_mixed_parity_null_face": True,
            "one_nonzero_tuned_bounded_second_order_tangent_certified": True,
            "general_mixed_null_face_classified": False,
            "other_ell_or_momentum_fibres_classified": False,
            "all_orders_integrability": False,
            "causal_or_quantum_claim": False,
        },
        "interpretation": "The phase-sensitive obstruction is not definite after axial and polar Einstein-minus multiplicities are combined. On one exact 3:1 mixed-parity face its two L=4 resonant projections cancel, and an exhaustive shell census shows that every other quadratic block is boundedly invertible after the five Taub maps vanish. This supplies a genuine bounded second-order jet, not merely a smooth secular extension.",
        "next_gate": "classify the full coefficient zero locus of all bounded resonance matrices at this tuned fibre, then extend the collision-and-source analysis to symbolic ell and multiple |k| fibres",
        "claim_boundary": "This is one explicit bounded second-order extension on a tuned compact fibre. It does not classify the full mixed cone, arbitrary phases, other ell or circumference values, exceptional input modes beyond the declared twist, all-orders integration, causal propagation, scattering, residual particles or quantum theory.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for name, path in INPUTS.items()},
        },
        "verification_receipt": {
            "producing_date": "2026-07-19",
            "tier_1": {"status": "PENDING", "tests_run": 0},
            "tier_2": {"status": "PASS_BY_CONTENT_ADDRESS", "criterion": "all direct quadratic coefficients and exceptional operators are unchanged certified inputs; this producer adds exact collision arithmetic and blockwise assembly"},
            "tier_3": {"status": "NOT_RUN", "reason": "the theorem is one tuned bounded second-order jet, not a cone freeze or higher-lifecycle promotion"},
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_opposite_momentum_ell2_mixed_parity_bounded_extension --check",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_opposite_momentum_ell2_mixed_parity_bounded_extension.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_opposite_momentum_ell2_mixed_parity_bounded_extension",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    payload = build()
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
    if arguments.write:
        OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    elif json.loads(OUTPUT.read_text(encoding="utf-8")) != payload:
        raise AssertionError("mixed-parity bounded-extension certificate is stale")
    print("EINSTEIN_MAXWELL_WEYL_OPPOSITE_MOMENTUM_ELL2_MIXED_PARITY_BOUNDED_EXTENSION: PASS")


if __name__ == "__main__":
    main()
