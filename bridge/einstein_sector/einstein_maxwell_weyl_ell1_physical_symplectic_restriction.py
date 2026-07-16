"""Certify the physical ell=1 Weyl--Maxwell quotient restriction."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell1_physical_symplectic_restriction.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_ell1_physical_symplectic_restriction.schema.json"
CURRENT_ENGINE = ROOT / "bridge/einstein_sector/weyl_maxwell_lee_wald_current.py"
FIXTURE_GENERATOR = ROOT / "bridge/einstein_sector/weyl_maxwell_ell1_exceptional_lee_wald_fixture.py"
INPUTS = {
    "direct_fixture": ROOT / "bridge/certificates/weyl_maxwell_ell1_exceptional_lee_wald_fixture.json",
    "einstein_radiative_form": ROOT / "bridge/certificates/einstein_maxwell_radiative_symplectic_matching.json",
    "polar_exceptional_complex": ROOT / "bridge/certificates/einstein_maxwell_polar_exceptional_complex.json",
    "axial_master_complex": ROOT / "bridge/certificates/einstein_maxwell_axial_master_complex.json",
    "standard_radiative_restriction": ROOT / "bridge/certificates/einstein_maxwell_weyl_radiative_symplectic_restriction.json",
    "polar_all_ell_restriction": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_all_ell_symplectic_restriction.json",
}


class WeylEll1PhysicalRestrictionError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise WeylEll1PhysicalRestrictionError(message)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _parse(value: str, momentum: sp.Symbol, frequency: sp.Symbol) -> sp.Expr:
    return sp.sympify(value, locals={"k": momentum, "omega": frequency})


def _matrix(rows: list[list[str]], momentum: sp.Symbol, frequency: sp.Symbol) -> sp.Matrix:
    return sp.Matrix(
        [[_parse(value, momentum, frequency) for value in row] for row in rows]
    )


def _restriction_theorem(records: dict[str, dict[str, Any]]) -> dict[str, Any]:
    momentum, frequency = sp.symbols("k omega", real=True)
    fixture = records["direct_fixture"]["direct_current"]
    source = records["einstein_radiative_form"]["ell1_quotient"]
    polar = records["polar_exceptional_complex"]["ell1_complex"]
    axial = records["axial_master_complex"]["ell1_quotient"]

    _require(
        polar["physical_reconstruction"] == "K=0: (A,B,C,U)=(-2Psi,0,2Psi,Psi)",
        "polar exceptional representative changed",
    )
    _require(
        axial["physical_dispersive_branch"] == "omega^2=k_n^2+4",
        "axial physical dispersion changed",
    )
    _require(
        source["polar_quotient_weight_without_N_over_2"] == "4",
        "Einstein polar quotient normalization changed",
    )
    source_axial_form = sp.Matrix(
        [[sp.sympify(value) for value in row] for row in source["axial_presymplectic_matrix_without_N_over_2"]]
    )
    source_polar_form = sp.Matrix(
        [[sp.sympify(value) for value in row] for row in source["polar_presymplectic_matrix_without_N_over_2"]]
    )
    axial_physical_vector = sp.Matrix([1, 1])
    polar_quotient_vector = sp.Matrix([0, 1])
    axial_source_weight = (axial_physical_vector.T * source_axial_form * axial_physical_vector)[0]
    polar_source_weight = (polar_quotient_vector.T * source_polar_form * polar_quotient_vector)[0]
    _require(axial_source_weight == 16, "Einstein axial physical weight changed")
    _require(polar_source_weight == 4, "Einstein polar physical weight changed")

    target_raw = {
        parity: _matrix(
            fixture[parity]["on_shell_integrated_coordinate_current_matrix"],
            momentum,
            frequency,
        )
        for parity in ("axial", "polar")
    }
    expected_target_raw = {
        "axial": sp.Matrix(
            [[-sp.Rational(256, 3) * sp.I * sp.pi * frequency, 0], [0, 0]]
        ),
        "polar": sp.Matrix(
            [[-sp.Rational(64, 3) * sp.I * sp.pi * frequency, 0], [0, 0]]
        ),
    }
    _require(target_raw == expected_target_raw, "direct ell=1 target matrices changed")

    harmonic_norm = sp.Rational(4, 3) * sp.pi
    source_raw_physical = {
        "axial": -sp.I * frequency * harmonic_norm * axial_source_weight,
        "polar": -sp.I * frequency * harmonic_norm * polar_source_weight,
    }
    target_raw_physical = {
        parity: target_raw[parity][0, 0] for parity in ("axial", "polar")
    }
    ratios = {
        parity: sp.simplify(target_raw_physical[parity] / source_raw_physical[parity])
        for parity in ("axial", "polar")
    }
    _require(ratios == {"axial": 4, "polar": 4}, "ell=1 quotient ratios changed")

    normalized_source = -sp.Rational(16, 3) * sp.I * sp.pi * frequency
    normalized_target = -sp.Rational(64, 3) * sp.I * sp.pi * frequency
    _require(
        sp.simplify(source_raw_physical["axial"] / 4 - normalized_source) == 0,
        "axial source normalization changed",
    )
    _require(
        sp.simplify(target_raw_physical["axial"] / 4 - normalized_target) == 0,
        "axial target normalization changed",
    )
    _require(source_raw_physical["polar"] == normalized_source, "polar source normalization changed")
    _require(target_raw_physical["polar"] == normalized_target, "polar target normalization changed")

    eigenvalue, mass = sp.symbols("lambda mu", real=True)
    polar_all_ell = records["polar_all_ell_restriction"]["restriction"]
    continuation_locals = {"lam": eigenvalue, "mu": mass}
    einstein_generic = sp.Matrix(
        [
            [sp.sympify(value.replace("lambda", "lam"), locals=continuation_locals) for value in row]
            for row in polar_all_ell["einstein_maxwell_off_shell_matrix"]
        ]
    ).subs(eigenvalue, 2)
    target_generic = sp.Matrix(
        [
            [sp.sympify(value.replace("lambda", "lam"), locals=continuation_locals) for value in row]
            for row in polar_all_ell["weyl_maxwell_off_shell_matrix"]
        ]
    ).subs({eigenvalue: 2, mass: 4})
    _require(einstein_generic == sp.Matrix([[1, -2], [-2, 4]]), "continued Einstein matrix changed")
    _require(target_generic == sp.Matrix([[8, -6], [-6, 8]]), "continued polar target matrix changed")
    gauge_vector = sp.Matrix([2, 1])
    physical_vector = sp.Matrix([-2, 1])
    quotient_vector = sp.Matrix([0, 1])
    generic_control = {
        "einstein_gauge_norm": (gauge_vector.T * einstein_generic * gauge_vector)[0],
        "target_gauge_norm": (gauge_vector.T * target_generic * gauge_vector)[0],
        "target_gauge_physical_cross": (gauge_vector.T * target_generic * physical_vector)[0],
        "physical_vector_ratio": sp.simplify(
            (physical_vector.T * target_generic * physical_vector)[0]
            / (physical_vector.T * einstein_generic * physical_vector)[0]
        ),
        "quotient_representative_naive_ratio": sp.simplify(
            (quotient_vector.T * target_generic * quotient_vector)[0]
            / (quotient_vector.T * einstein_generic * quotient_vector)[0]
        ),
    }
    _require(
        generic_control
        == {
            "einstein_gauge_norm": 0,
            "target_gauge_norm": 16,
            "target_gauge_physical_cross": -24,
            "physical_vector_ratio": 4,
            "quotient_representative_naive_ratio": 2,
        },
        "generic polar continuation diagnostic changed",
    )
    common_control = records["standard_radiative_restriction"]["theorem"]["all_ell_ge_2_classification"]["common_relative_weights"][0]
    common_control_at_two = sp.sympify(
        common_control.replace("lambda", "lam"), locals={"lam": eigenvalue}
    ).subs(eigenvalue, 2)
    _require(common_control_at_two == 4, "standard radiative plus-branch control changed")

    return {
        "dispersion": "omega^2=k_n^2+4",
        "harmonic_norm": "N_1m=integral_(S2)Y_1m^2 dOmega; direct fixture uses N_10=4*pi/3",
        "quotient_coordinates": {
            "axial_raw": "(H,Q)=(p_A,p_A)",
            "axial_normalized": "Psi_A=2*p_A",
            "polar": "Psi_P=U-K/2 with K=0",
            "normalization_reason": "both normalized Einstein quotient coordinate currents equal -16*I*pi*omega/3 for Y_10",
        },
        "direct_gauge_descent": {
            "amplitude_order": ["physical", "residual_gauge"],
            "axial_on_shell_target_matrix_raw": [
                [str(target_raw["axial"][row, column]) for column in range(2)]
                for row in range(2)
            ],
            "polar_on_shell_target_matrix_raw": [
                [str(target_raw["polar"][row, column]) for column in range(2)]
                for row in range(2)
            ],
            "both_gauge_rows_and_columns_zero": True,
            "interpretation": "the literal target current descends to both certified exceptional quotients; this is stronger than a vanishing gauge norm",
        },
        "parity_rows": {
            "axial": {
                "raw_einstein_coordinate_current": str(source_raw_physical["axial"]),
                "raw_weyl_maxwell_coordinate_current": str(target_raw_physical["axial"]),
                "normalized_einstein_coordinate_current": str(normalized_source),
                "normalized_weyl_maxwell_coordinate_current": str(normalized_target),
                "restriction_over_einstein": str(ratios["axial"]),
            },
            "polar": {
                "raw_einstein_coordinate_current": str(source_raw_physical["polar"]),
                "raw_weyl_maxwell_coordinate_current": str(target_raw_physical["polar"]),
                "normalized_einstein_coordinate_current": str(normalized_source),
                "normalized_weyl_maxwell_coordinate_current": str(normalized_target),
                "restriction_over_einstein": str(ratios["polar"]),
            },
        },
        "normalized_direct_sum_theorem": {
            "einstein_matrix": [[str(normalized_source), "0"], ["0", str(normalized_source)]],
            "weyl_maxwell_matrix": [[str(normalized_target), "0"], ["0", str(normalized_target)]],
            "relative_operator": [["4", "0"], ["0", "4"]],
            "identity": "Omega_WM|Sol_ell1_phys=4*Omega_EM|Sol_ell1_phys",
            "rank_per_real_spatial_harmonic": 2,
            "relative_coefficient_signature_per_real_spatial_harmonic": {
                "positive": 2,
                "negative": 0,
                "zero": 0,
            },
            "cross_parity_pairing": "0 by parity invariance: axial and polar ell=1 representatives have opposite spatial parity",
        },
        "generic_polar_lambda_to_2_failure": {
            "continued_matrix_at_mu_4": [["8", "-6"], ["-6", "8"]],
            **{key: str(value) for key, value in generic_control.items()},
            "verdict": "the generic ell>=2 polar matrix does not descend to the exceptional ell=1 quotient; the direct exceptional fixture is essential even though its physical quotient ratio independently returns 4",
        },
        "mode_counting": {
            "real_spatial_multiplicity_q": "q=3 for n=0 and q=6 for each n>0 cosine/sine Fourier pair",
            "oscillator_blocks": "2*q, one axial and one polar physical oscillator per real spatial harmonic",
            "real_phase_space_dimension": "4*q",
            "relative_coefficient_signature": "positive=2*q, negative=0, zero=0",
            "complex_reality_rule": "(n,m) is paired with (-n,-m) and is not counted twice",
        },
        "global_separation": {
            "physical_ell1_is_radiative": True,
            "axial_n0_zero_frequency_twist_included": False,
            "reason": "the twist is the separate zero-eigenvalue generalized global block; the present modes have omega^2=k_n^2+4",
        },
        "quantum_norm_boundary": {
            "positive_relative_classical_coefficient": True,
            "positive_frequency_complex_structure_constructed": False,
            "one_particle_norm_certified": False,
            "ghost_or_unitarity_theorem": False,
        },
    }


def build_certificate() -> dict[str, Any]:
    records = {name: _load(path) for name, path in INPUTS.items()}
    _require(
        records["direct_fixture"]["result_id"]
        == "WEYL_MAXWELL_ELL1_EXCEPTIONAL_LEE_WALD_FIXTURE",
        "direct fixture changed",
    )
    _require(
        records["polar_exceptional_complex"]["classification"]["ell1_residual_quotient_complete"] is True,
        "polar quotient input changed",
    )
    _require(
        records["einstein_radiative_form"]["classification"]["polar_ell1_gauge_kernel_and_quotient"] is True,
        "Einstein quotient pairing input changed",
    )
    theorem = _restriction_theorem(records)
    return {
        "schema": "einstein-maxwell-weyl-ell1-physical-symplectic-restriction-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "EINSTEIN_MAXWELL_WEYL_ELL1_PHYSICAL_SYMPLECTIC_RESTRICTION",
        "result_state": "PHYSICAL_ELL1_ALL_N_M_QUOTIENT_DESCENDED_NONDEGENERATE_FACTOR_FOUR_RESTRICTION",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G3_PHYSICAL_ELL1_ALL_N_M_QUOTIENT",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {
                name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)}
                for name, path in INPUTS.items()
            },
            "direct_implementation": {
                "current_engine": {"path": str(CURRENT_ENGINE.relative_to(ROOT)), "sha256": _sha256(CURRENT_ENGINE)},
                "fixture_generator": {"path": str(FIXTURE_GENERATOR.relative_to(ROOT)), "sha256": _sha256(FIXTURE_GENERATOR)},
            },
        },
        "domain": "all physical axial and polar ell=1 Einstein-Maxwell quotient modes, every m and periodic S1 momentum, on R_t x S1_L x S2 at fixed magnetic bundle, before the final residual SO(4,2) quotient",
        "theorem": theorem,
        "classification": {
            "physical_ell1_axial_restriction_computed": True,
            "physical_ell1_polar_restriction_computed": True,
            "all_n_m_by_symbolic_k_and_SO3": True,
            "target_current_descends_to_exceptional_quotient": True,
            "physical_ell1_restriction_nondegenerate": True,
            "physical_ell1_pullback_equals_four_times_einstein": True,
            "generic_polar_lambda_to_2_continuation_valid": False,
            "ordinary_physical_ell1_modes_removed_by_target_weyl_gauge": False,
            "axial_twist_restriction_computed": False,
            "homogeneous_restriction_computed": False,
            "complete_fourth_order_weyl_maxwell_phase_space_classified": False,
            "positive_frequency_complex_structure_constructed": False,
            "one_particle_norm_certified": False,
            "quantum_ghost_or_unitarity_theorem": False,
            "nonlinear_solution_embedding_certified": False,
            "final_residual_quotient_computed": False,
            "lorentzian_causal_or_scattering_theorem": False,
        },
        "interpretation": "The complete physical ell=1 axial-plus-polar Einstein-Maxwell quotient survives as a nondegenerate target subspace before the final residual quotient. After fixing source-normalized quotient coordinates, the literal Weyl-Maxwell pullback is exactly four times the Einstein-Maxwell form in both parities. This equality required a direct exceptional calculation: the generic polar ell>=2 matrix fails gauge descent at lambda=2. These massive ell=1 triplets are radiative modes, not the separate zero-frequency axial twist. The positive relative factor is classical and does not construct a one-particle norm or quantum theorem.",
        "next_gate": "compute the Weyl-Maxwell restriction on the six-dimensional homogeneous generalized block and on each axial-twist Darboux pair by direct Lee-Wald currents, keeping the two global result kinds separate",
        "claim_boundary": "This exact LOCAL-ALGEBRAIC/REDUCED-MODE theorem covers every physical ell=1 axial and polar quotient oscillator at symbolic periodic momentum and all m. It proves direct target gauge descent and factor-four matching. It excludes the zero-frequency axial twist, homogeneous generalized modes, extra fourth-order Weyl-Maxwell solutions, nonlinear closure, final SO(4,2) reduction, positive-frequency Hilbert space, causal scattering, and quantum theory.",
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_ell1_physical_symplectic_restriction --verify bridge/certificates/einstein_maxwell_weyl_ell1_physical_symplectic_restriction.json",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_ell1_physical_symplectic_restriction.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_ell1_physical_symplectic_restriction",
            "python3 -m bridge.einstein_sector.weyl_maxwell_ell1_exceptional_lee_wald_fixture --verify bridge/certificates/weyl_maxwell_ell1_exceptional_lee_wald_fixture.json",
        ],
    }


def verify_certificate(path: Path = DEFAULT_OUTPUT) -> None:
    _require(_load(path) == build_certificate(), f"stale physical ell=1 restriction certificate: {path}")


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
