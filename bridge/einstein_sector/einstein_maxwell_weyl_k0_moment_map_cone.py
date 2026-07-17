"""Exact generic k=0 Einstein--extra common moment-map cone."""

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
DEFAULT_OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_k0_moment_map_cone.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_k0_moment_map_cone.schema.json"
INPUTS = {
    "moment_map_bridge": ROOT / "bridge/certificates/einstein_maxwell_weyl_moment_map_taub_bridge.json",
    "stabilizer": ROOT / "bridge/certificates/einstein_maxwell_weyl_plebanski_hacyan_stabilizer.json",
    "axial_current": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_lee_wald_completion.json",
    "polar_current": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_lee_wald_gate.json",
    "balanced_fixture": ROOT / "bridge/certificates/einstein_maxwell_weyl_balanced_ell0_second_order.json",
}


class K0MomentMapConeError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise K0MomentMapConeError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _frequency_record() -> dict[str, Any]:
    eigenvalue = sp.symbols("lambda", positive=True, real=True)
    omega_minus_squared = eigenvalue - sp.sqrt(2 * eigenvalue)
    omega_extra_squared = eigenvalue - sp.Rational(2, 3)
    omega_plus_squared = eigenvalue + sp.sqrt(2 * eigenvalue)
    return {
        "physical_domain": "lambda=ell*(ell+1), ell>=2",
        "omega_minus_squared": str(omega_minus_squared),
        "omega_extra_squared": str(omega_extra_squared),
        "omega_plus_squared": str(omega_plus_squared),
        "exact_gaps": {
            "omega_extra_squared_minus_omega_minus_squared": str(
                sp.sqrt(2 * eigenvalue) - sp.Rational(2, 3)
            ),
            "omega_plus_squared_minus_omega_extra_squared": str(
                sp.sqrt(2 * eigenvalue) + sp.Rational(2, 3)
            ),
        },
        "ordering": "0<omega_minus<omega_extra<omega_plus for every physical lambda>=6",
    }


def _density_cone_theorem() -> dict[str, Any]:
    return {
        "gram_normalized_amplitude_matrices": {
            "C_plus_ell": "Mat_(2 x (2ell+1))(C): one Einstein-plus copy in each parity",
            "C_extra_ell": "Mat_(4 x (2ell+1))(C): two p-primary copies in each parity",
            "C_minus_ell": "Mat_(2 x (2ell+1))(C): one Einstein-minus copy in each parity",
        },
        "density_matrices": {
            "rho_plus_ell": "C_plus_ell^dagger*C_plus_ell >= 0, rank<=2",
            "rho_extra_ell": "C_extra_ell^dagger*C_extra_ell >= 0, rank<=4",
            "rho_minus_ell": "C_minus_ell^dagger*C_minus_ell >= 0, rank<=2",
        },
        "spin_moments": {
            "occupation": "A_s,ell=tr(rho_s,ell)",
            "angular": "j_s,ell,a=tr(rho_s,ell*T_ell,a), a=1,2,3, with T_ell,a Hermitian",
        },
        "common_zero_equations": {
            "P_x": "identically zero because k=0",
            "H": "sum_ell(omega_plus^2*A_plus + omega_extra^2*A_extra - omega_minus^2*A_minus)=0",
            "J_a": "sum_ell(omega_plus*j_plus,a + omega_extra*j_extra,a - omega_minus*j_minus,a)=0 for a=1,2,3",
        },
        "classification": "The full finite-harmonic generic k=0 common-zero cone is exactly the inverse image of these four linear equations inside the product of the displayed positive-semidefinite rank strata.",
        "reconstruction": "Every allowed density matrix has a factorization rho=C^dagger*C with the displayed rank bound, and hence reconstructs amplitudes; two factorizations differ by an internal partial isometry and have identical stabilizer moment maps.",
        "cross_ell_rule": "Rotations preserve ell, but the total J_a and H charges are sums over ell; the equations retain every allowed cancellation between distinct ell blocks.",
        "real_field_rule": "Negative-frequency amplitudes are fixed by conjugation, so the positive-frequency density data classify real linear fields.",
    }


def _neutral_subcone() -> dict[str, Any]:
    regressions: dict[str, Any] = {}
    for ell in range(2, 13):
        eigenvalue = sp.Integer(ell * (ell + 1))
        omega_minus_squared = eigenvalue - sp.sqrt(2 * eigenvalue)
        omega_extra_squared = eigenvalue - sp.Rational(2, 3)
        omega_plus_squared = eigenvalue + sp.sqrt(2 * eigenvalue)
        representation = _rotation_representation(ell)
        zero_index = ell
        vector = sp.zeros(2 * ell + 1, 1)
        vector[zero_index] = 1
        angular = representation["angular_form"]
        expectations = {
            "J3": sp.simplify((vector.T * angular * representation["J0"] * vector)[0]),
            "Jplus": sp.simplify((vector.T * angular * representation["Jplus"] * vector)[0]),
            "Jminus": sp.simplify((vector.T * angular * representation["Jminus"] * vector)[0]),
        }
        _require(all(value == 0 for value in expectations.values()), f"ell={ell} m=0 spin changed")
        a_plus, a_extra = sp.symbols("a_plus a_extra", nonnegative=True, real=True)
        a_minus = sp.factor(
            (omega_plus_squared * a_plus + omega_extra_squared * a_extra)
            / omega_minus_squared
        )
        energy = sp.simplify(
            omega_plus_squared * a_plus
            + omega_extra_squared * a_extra
            - omega_minus_squared * a_minus
        )
        _require(energy == 0, f"ell={ell} neutral balance changed")
        regressions[str(ell)] = {
            "lambda": str(eigenvalue),
            "all_three_rotation_expectations_zero": True,
            "energy_remainder": str(energy),
        }
    return {
        "parameters": "for any fixed ell>=2 choose a_plus,a_extra>=0, not both zero",
        "densities": "rho_plus=a_plus*|ell,0><ell,0|, rho_extra=a_extra*|ell,0><ell,0|, rho_minus=a_minus*|ell,0><ell,0|",
        "a_minus": "(omega_plus^2*a_plus+omega_extra^2*a_extra)/omega_minus^2",
        "moment_maps": {"H": "0", "P_x": "0", "J_1": "0", "J_2": "0", "J_3": "0"},
        "dimension_before_overall_scaling": 2,
        "paper91_ray": "ell=2, a_plus=0 is the certified balanced Einstein-minus/extra ray; it is a boundary ray of this two-parameter rotationally neutral cone",
        "all_ell_proof": "T_3|ell,0>=0 and T_plus/minus move m=0 to orthogonal m=+/-1 states; the displayed a_minus solves H exactly",
        "exact_regressions": regressions,
    }


def _scope_boundaries() -> dict[str, Any]:
    return {
        "classified": [
            "all generic ell>=2 k=0 axial and polar Einstein-plus, Einstein-minus, and extra p-primary amplitudes",
            "all m and every cancellation between ell blocks",
            "the complete H,J_1,J_2,J_3 common-zero equations with P_x identically zero",
        ],
        "not_yet_classified": [
            "which non-neutral density-cone strata solve the full quadratic Weyl-Maxwell source equation",
            "opposite nonzero momentum standing waves",
            "ell=0, ell=1, homogeneous, twist, electric-charge, and Wilson-line blocks",
            "all-orders integrability or a stabilizer quotient",
        ],
    }


def build_certificate() -> dict[str, Any]:
    records = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in INPUTS.items()}
    _require(
        records["moment_map_bridge"]["classification"]["generic_H_Px_J_selection_rules_certified"],
        "moment-map selection rules changed",
    )
    _require(
        records["axial_current"]["full_solution_pairing"]["Einstein_branch_signature_for_lambda_ge_6"]
        == [1, 1],
        "axial Einstein inertia changed",
    )
    _require(
        records["axial_current"]["full_solution_pairing"]["extra_branch_signature_for_lambda_ge_6"]
        == [2, 0],
        "axial extra inertia changed",
    )
    _require(
        records["polar_current"]["shell_pairing"]["Einstein_block_inertia"] == [1, 1],
        "polar Einstein inertia changed",
    )
    _require(
        records["polar_current"]["shell_pairing"]["extra_positive_frequency_inertia"] == [2, 0],
        "polar extra inertia changed",
    )
    _require(
        records["balanced_fixture"]["classification"]["complete_second_order_extension_constructed"],
        "balanced fixture changed",
    )
    return {
        "schema": "einstein-maxwell-weyl-k0-moment-map-cone-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "EINSTEIN_MAXWELL_WEYL_FULL_GENERIC_K0_MOMENT_MAP_CONE",
        "result_state": "FULL_GENERIC_K0_COMMON_STABILIZER_ZERO_CONE_CLASSIFIED",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G3_ALL_GENERIC_ELL_K0_DENSITY_CONE",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {
                name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)}
                for name, path in INPUTS.items()
            },
        },
        "domain": "finite-harmonic generic ell>=2 locally gauge-reduced real Weyl-Maxwell stationary solutions at k=0 on fixed P_N, before stabilizer quotient",
        "frequencies": _frequency_record(),
        "density_cone_theorem": _density_cone_theorem(),
        "rotationally_neutral_subcone": _neutral_subcone(),
        "scope_boundaries": _scope_boundaries(),
        "classification": {
            "full_generic_k0_common_zero_cone_classified": True,
            "all_ell_all_m_both_parities_and_all_extra_polarizations_included": True,
            "cross_ell_charge_cancellations_included": True,
            "paper91_balanced_ray_embedded_in_general_cone": True,
            "full_quadratic_source_solvability_on_cone_classified": False,
            "opposite_momentum_standing_waves_classified": False,
            "exceptional_global_blocks_classified": False,
            "absolute_stabilizer_quotient_certified": False,
            "Lorentzian_causal_or_quantum_claim": False,
        },
        "interpretation": "The Paper 91 balanced ray is not isolated at the level of quadratic stabilizer charges. The complete generic k=0 common-zero set is a rank-constrained spectrahedral cone, and every ell has a two-parameter rotationally neutral Einstein-plus/extra/Einstein-minus subcone. This is a moment-map/Taub-zero classification, not a theorem that every point solves the full second-order source equation.",
        "next_gate": "evaluate the complete quadratic Weyl-Maxwell source on the density-cone strata, beginning with the rotationally neutral fixed-ell faces; then classify opposite-momentum and exceptional/global blocks",
        "claim_boundary": "This LOCAL-ALGEBRAIC/REDUCED-MODE theorem classifies the full generic k=0 common H,P_x,J_i zero cone. It does not promote Taub-zero points to second-order solutions, classify nonzero opposite momenta or exceptional/global blocks, perform a stabilizer quotient, or establish a causal or quantum result.",
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_k0_moment_map_cone --verify bridge/certificates/einstein_maxwell_weyl_k0_moment_map_cone.json",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_k0_moment_map_cone.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_k0_moment_map_cone",
        ],
    }


def verify_certificate(path: Path = DEFAULT_OUTPUT) -> None:
    payload = json.loads(path.read_text(encoding="utf-8"))
    _require(payload == build_certificate(), f"k=0 moment-map cone certificate stale: {path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    if args.write:
        DEFAULT_OUTPUT.write_text(
            json.dumps(build_certificate(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    if args.verify:
        verify_certificate(args.verify)
    if not args.write and not args.verify:
        parser.error("one of --write or --verify is required")


if __name__ == "__main__":
    main()
