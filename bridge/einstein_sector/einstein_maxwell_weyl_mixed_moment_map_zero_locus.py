"""Exact mixed q/p moment-map cone and minimal balanced fixture."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp

from bridge.einstein_sector.einstein_maxwell_weyl_plebanski_hacyan_stabilizer import (
    _rotation_representation,
)


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_mixed_moment_map_zero_locus.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_mixed_moment_map_zero_locus.schema.json"
INPUTS = {
    "moment_map_bridge": ROOT / "bridge/certificates/einstein_maxwell_weyl_moment_map_taub_bridge.json",
    "stabilizer": ROOT / "bridge/certificates/einstein_maxwell_weyl_plebanski_hacyan_stabilizer.json",
    "axial_pairing": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_lee_wald_completion.json",
    "extra_fixture": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_extra_ell2_taub.json",
    "Einstein_fixture": ROOT / "bridge/certificates/einstein_maxwell_weyl_hermitian_axial_polar_ell2_taub.json",
    "polar_operator": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_physical_completion.json",
}


class MixedMomentMapZeroLocusError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise MixedMomentMapZeroLocusError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical(value: sp.Expr) -> sp.Expr:
    return sp.factor(sp.sqrtdenest(sp.radsimp(value)))


def _nonzero_algebraic_witness(value: sp.Expr) -> dict[str, str | bool]:
    value = _canonical(value)
    variable = sp.symbols("z")
    polynomial = sp.Poly(sp.minpoly(value, variable), variable)
    constant = polynomial.eval(0)
    _require(constant != 0, f"algebraic nonzero witness failed for {value}")
    return {
        "value": str(value),
        "minimal_polynomial": str(polynomial.as_expr()),
        "constant_coefficient": str(constant),
        "nonzero": True,
    }


def _same_travelling_block_cone() -> dict[str, Any]:
    eigenvalue, momentum = sp.symbols("lambda k", positive=True, real=True)
    omega_plus, omega_extra, omega_minus = sp.symbols(
        "omega_plus omega_extra omega_minus", positive=True, real=True
    )
    occupation_plus, occupation_extra, occupation_minus = sp.symbols(
        "A_plus A_extra A_minus", nonnegative=True, real=True
    )
    energy_equation = (
        omega_plus**2 * occupation_plus
        + omega_extra**2 * occupation_extra
        - omega_minus**2 * occupation_minus
    )
    momentum_equation = (
        omega_plus * occupation_plus
        + omega_extra * occupation_extra
        - omega_minus * occupation_minus
    )
    eliminated = sp.expand(energy_equation - omega_minus * momentum_equation)
    expected = (
        omega_plus * (omega_plus - omega_minus) * occupation_plus
        + omega_extra * (omega_extra - omega_minus) * occupation_extra
    )
    _require(sp.expand(eliminated - expected) == 0, "H/P_x cone elimination changed")

    mass_minus = eigenvalue - sp.sqrt(2 * eigenvalue)
    mass_extra = eigenvalue - sp.Rational(2, 3)
    mass_plus = eigenvalue + sp.sqrt(2 * eigenvalue)
    _require(
        sp.simplify(mass_extra - mass_minus - (sp.sqrt(2 * eigenvalue) - sp.Rational(2, 3))) == 0,
        "minus/extra mass gap changed",
    )
    return {
        "occupation_definition": "after exact Gram factorization, A_plus,A_extra,A_minus are sums of nonnegative squared amplitudes over m, parity, and the two extra polarizations; the Einstein-minus current contributes with the opposite sign",
        "frequencies": {
            "omega_minus_squared": "k^2+lambda-sqrt(2*lambda)",
            "omega_extra_squared": "k^2+lambda-2/3",
            "omega_plus_squared": "k^2+lambda+sqrt(2*lambda)",
            "strict_order_for_lambda_at_least_6": "0<omega_minus<omega_extra<omega_plus",
        },
        "zero_equations_after_common_positive_factor_removed": {
            "H": str(energy_equation),
            "P_x_over_k": str(momentum_equation),
        },
        "elimination": str(eliminated),
        "positivity_argument": "for k!=0 the P_x equation is available; both coefficients in the eliminated equation are strictly positive, so A_plus=A_extra=0, and then either original equation gives A_minus=0",
        "verdict": "THE_COMMON_H_PX_ZERO_LOCUS_IN_ONE_FIXED_NONZERO_K_TRAVELLING_BLOCK_IS_ZERO",
        "rotation_constraints_needed_for_no_go": False,
        "scope": "one fixed (k,ell) travelling block, allowing all m, both parities, both Einstein branches, and both extra polarizations; cancellations between distinct k blocks are not included",
    }


def _minimal_balanced_fixture(records: dict[str, Any]) -> dict[str, Any]:
    root = sp.sqrt(3)
    omega_minus_squared = 6 - 2 * root
    omega_extra_squared = sp.Rational(16, 3)
    einstein_taub = sp.sympify(
        records["Einstein_fixture"]["weyl_maxwell_taub"]["cosine_amplitude_matrix_A_P"][0][0],
        locals={"sqrt": sp.sqrt},
    )
    extra_taub = sp.sympify(
        records["extra_fixture"]["quadratic_source"]["constant_lapse_Taub_matrix"][1][1]
    )
    _require(einstein_taub > 0 and extra_taub < 0, "fixture Taub signs changed")
    extra_amplitude_squared = _canonical(-einstein_taub / extra_taub)
    expected_ratio = sp.Rational(27, 52) * (5 * root - 6)
    _require(_canonical(extra_amplitude_squared - expected_ratio) == 0, "balanced amplitude changed")
    extra_amplitude = sp.sqrt(extra_amplitude_squared)
    total_taub = _canonical(einstein_taub + extra_taub * extra_amplitude_squared)
    _require(total_taub == 0, "balanced fixture did not cancel H")

    rotation = _rotation_representation(2)
    magnetic_zero = sp.Matrix([0, 0, 1, 0, 0])
    angular_form = rotation["angular_form"]
    rotation_expectations = {
        name: _canonical((magnetic_zero.T * angular_form * matrix * magnetic_zero)[0])
        for name, matrix in {
            "J3": rotation["J0"],
            "Jplus": rotation["Jplus"],
            "Jminus": rotation["Jminus"],
        }.items()
    }
    _require(all(value == 0 for value in rotation_expectations.values()), "m=0 rotation moment map changed")
    return {
        "labels": "axial ell=2,m=0,k=0; Einstein-minus q-primary plus the second axial extra p-primary representative",
        "Einstein_minus": {
            "representative_Ht_Hx_Qt_Qx": ["0", "-2", "0", "2*sqrt(3)"],
            "frequency_squared": str(omega_minus_squared),
            "raw_cosine_amplitude": "1",
            "constant_lapse_Taub_coefficient": str(_canonical(einstein_taub)),
        },
        "extra_e2": {
            "representative_Ht_Hx_Qt_Qx": ["0", "-2/3", "0", "6"],
            "frequency_squared": str(omega_extra_squared),
            "raw_cosine_amplitude_squared": str(extra_amplitude_squared),
            "positive_amplitude": str(extra_amplitude),
            "constant_lapse_Taub_coefficient_per_unit_amplitude": str(extra_taub),
        },
        "common_moment_maps": {
            "H": str(total_taub),
            "P_x": "0 because k=0",
            "J3": str(rotation_expectations["J3"]),
            "J1": "0 from the separate Jplus and Jminus expectations",
            "J2": "0 from the separate Jplus and Jminus expectations",
            "all_five_zero": True,
        },
        "important_distinction": "q/p Lee-Wald mixed entries vanish; this is additive cancellation of diagonal charges, not a q-p interference term",
        "nonzero_real_linear_tangent": True,
    }


def _quadratic_channel_ledger() -> dict[str, Any]:
    root = sp.sqrt(3)
    omega_minus = sp.sqrt(6 - 2 * root)
    omega_extra = sp.Rational(4, 1) / root
    squared_frequencies = {
        "zero": sp.Integer(0),
        "Einstein_self_sum_2omega_minus": _canonical(4 * omega_minus**2),
        "extra_self_sum_2omega_extra": _canonical(4 * omega_extra**2),
        "cross_sum_omega_extra_plus_omega_minus": _canonical((omega_extra + omega_minus) ** 2),
        "cross_difference_omega_extra_minus_omega_minus": _canonical((omega_extra - omega_minus) ** 2),
    }
    audits: dict[str, Any] = {}
    for channel, frequency_squared in squared_frequencies.items():
        outputs: dict[str, Any] = {}
        for ell in (2, 4):
            eigenvalue = ell * (ell + 1)
            p_value = _canonical(frequency_squared - eigenvalue + sp.Rational(2, 3))
            q_value = _canonical(
                frequency_squared**2
                - 2 * eigenvalue * frequency_squared
                + eigenvalue * (eigenvalue - 2)
            )
            outputs[str(ell)] = {
                "p": _nonzero_algebraic_witness(p_value),
                "q": _nonzero_algebraic_witness(q_value),
                "polar_gauge_fixed_Hessian_invertible": True,
            }
        audits[channel] = {
            "frequency_squared": str(frequency_squared),
            "generic_outputs": outputs,
        }
    return {
        "input_parity": "axial times axial is polar/even",
        "axisymmetric_angular_outputs": [0, 2, 4],
        "frequency_channels": audits,
        "generic_ell_2_and_4_conclusion": "every channel is off both p and q target shells, so the certified 4x4 action Hessian is invertible and these source blocks admit unique gauge-fixed corrections once their coefficients are inserted",
        "ell_0_exceptional_conclusion": "not decided by the generic determinant; the homogeneous source/operator and fixed-charge rows must be computed directly",
    }


def build_certificate() -> dict[str, Any]:
    records = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in INPUTS.items()}
    _require(records["moment_map_bridge"]["result_id"] == "EINSTEIN_MAXWELL_WEYL_MOMENT_MAP_TAUB_BRIDGE", "moment-map input changed")
    _require(records["stabilizer"]["result_id"] == "EINSTEIN_MAXWELL_WEYL_PLEBANSKI_HACYAN_STABILIZER_DESCENT", "stabilizer input changed")
    _require(records["axial_pairing"]["full_solution_pairing"]["Einstein_branch_signature_for_lambda_ge_6"] == [1, 1], "Einstein inertia changed")
    _require(records["polar_operator"]["classification"]["physical_ring_determinantal_ideals_certified"] is True, "polar determinant gate changed")
    return {
        "schema": "einstein-maxwell-weyl-mixed-moment-map-zero-locus-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "EINSTEIN_MAXWELL_WEYL_MIXED_MOMENT_MAP_ZERO_LOCUS",
        "result_state": "SAME_K_TRAVELLING_ZERO_LOCUS_TRIVIAL_AND_MINIMAL_K0_BALANCED_FIXTURE_CERTIFIED",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G2_GENERIC_SAME_K_CONE_PLUS_G1_ELL2_K0_BALANCED_FIXTURE",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for name, path in INPUTS.items()},
        },
        "domain": "generic locally gauge-reduced axial/polar q/p-primary stationary solution space on the fixed compact magnetic bundle, with the five Plebanski-Hacyan stabilizers retained",
        "same_nonzero_k_travelling_block": _same_travelling_block_cone(),
        "minimal_k0_balanced_fixture": _minimal_balanced_fixture(records),
        "quadratic_preflight": _quadratic_channel_ledger(),
        "classification": {
            "same_nonzero_k_travelling_common_H_Px_zero_locus_trivial": True,
            "nonzero_k_cancellations_across_distinct_momenta_classified": False,
            "minimal_nonzero_all_five_moment_map_zero_fixture_constructed": True,
            "generic_ell2_ell4_output_shell_resonances_excluded": True,
            "ell0_quadratic_source_and_correction_computed": False,
            "complete_second_order_extension_constructed": False,
            "remaining_adjoint_obstruction_exhibited": False,
            "absolute_stabilizer_quotient_certified": False,
            "causal_or_quantum_claim": False,
        },
        "interpretation": "The first mixed common-zero tangent exists, but only as charge balance between diagonal Einstein-minus and extra-primary contributions; it is not q-p interference. A single nonzero-k travelling block cannot balance both energy and momentum because the three shell frequencies are strictly ordered. The minimal k=0,m=0 fixture clears all five stabilizer/Taub charges. Its ell=2 and ell=4 quadratic outputs are automatically removable off shell; the only remaining second-order gate is the exceptional homogeneous ell=0 channel.",
        "next_gate": "compute the complete ell=0 quadratic source of the declared balanced fixture and solve the homogeneous fixed-bundle Weyl-Maxwell equation or exhibit an exceptional adjoint witness",
        "claim_boundary": "This LOCAL-ALGEBRAIC/REDUCED-MODE result classifies one-block H/P_x charge balance, constructs one exact all-stabilizer-zero fixture, and excludes generic polar shell resonance in its ell=2,4 outputs. It does not yet decide the homogeneous ell=0 source, full second-order extension, distinct-momentum standing waves, a stabilizer quotient, causal propagation, or quantum theory.",
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_mixed_moment_map_zero_locus --verify bridge/certificates/einstein_maxwell_weyl_mixed_moment_map_zero_locus.json",
            "python3 -m bridge.einstein_sector.verify_einstein_maxwell_weyl_mixed_moment_map_zero_locus",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_mixed_moment_map_zero_locus",
        ],
    }


def verify_certificate(path: Path = DEFAULT_OUTPUT) -> None:
    _require(json.loads(path.read_text(encoding="utf-8")) == build_certificate(), f"mixed zero-locus certificate stale or altered: {path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    if args.write:
        DEFAULT_OUTPUT.write_text(json.dumps(build_certificate(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.verify:
        verify_certificate(args.verify)
    if not args.write and not args.verify:
        parser.error("one of --write or --verify is required")


if __name__ == "__main__":
    main()
