"""Fail-closed preflight for the polar off-shell Einstein--Weyl triangle."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp

from bridge.einstein_sector.einstein_maxwell_polar_master_complex import _matrix


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "bridge/certificates/einstein_weyl_polar_offshell_operator_preflight.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein_weyl_polar_offshell_operator_preflight.schema.json"
INPUTS = {
    "source_polar_operator": ROOT / "bridge/certificates/einstein_maxwell_polar_master_complex.json",
    "target_current_on_Einstein_image": ROOT / "bridge/certificates/weyl_maxwell_polar_arbitrary_lambda_fixture.json",
    "polar_pullback": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_all_ell_symplectic_restriction.json",
    "relative_triangle_preflight": ROOT / "bridge/certificates/einstein_weyl_relative_linear_triangle_preflight.json",
}


class PolarOffshellPreflightError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise PolarOffshellPreflightError(message)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _matrix_strings(matrix: sp.MatrixBase) -> list[list[str]]:
    return [[str(sp.factor(matrix[row, column])) for column in range(matrix.cols)] for row in range(matrix.rows)]


def _gauge_contraction() -> dict[str, Any]:
    source_operator, (eigenvalue, momentum, frequency) = _matrix()
    # Source Diff gauge: G=h_A=0, leaving (A,B,C,K,U).  A target Weyl
    # parameter s acts as (-2s,0,2s,2s,0).  The choice s=-K/2 sets K'=0.
    field_map = sp.Matrix([
        [1, 0, 0, 1, 0],
        [0, 1, 0, 0, 0],
        [0, 0, 1, -1, 0],
        [0, 0, 0, 0, 1],
    ])
    weyl_vector = sp.Matrix([-1, 0, 1, 1, 0])
    _require(field_map.rank() == 4, "target polar gauge contraction lost rank")
    _require(field_map.nullspace() == [weyl_vector], "target polar Weyl kernel changed")
    source_image = (source_operator * weyl_vector).applyfunc(sp.factor)
    _require(source_image[6] == -1, "source polar operator no longer separates the Weyl kernel")
    return {
        "source_gauge_fixed_coordinates": ["A", "B", "C", "K", "U"],
        "target_gauge_fixed_coordinates": ["A+K", "B", "C-K", "U"],
        "target_field_map": _matrix_strings(field_map),
        "target_field_map_rank": field_map.rank(),
        "target_field_map_kernel": [str(value) for value in weyl_vector],
        "kernel_interpretation": "the kernel is the residual pure-Weyl metric direction (-1,0,1,1,0) on the source Diff gauge slice",
        "source_operator_on_kernel": [str(value) for value in source_image],
        "source_kernel_intersection": "zero because the sphere-tracefree Einstein row equals -1 on the Weyl vector",
        "induced_map_on_Einstein_solution_kernel_injective": True,
        "no_division_used": True,
        "symbols": {"lambda": str(eigenvalue), "k": str(momentum), "omega": str(frequency)},
    }


def build_certificate() -> dict[str, Any]:
    records = {name: _load(path) for name, path in INPUTS.items()}
    _require(records["source_polar_operator"]["result_id"] == "COMPACT_EM_POLAR_MASTER_COMPLEX", "source polar input changed")
    _require(records["target_current_on_Einstein_image"]["result_id"] == "WEYL_MAXWELL_POLAR_ARBITRARY_LAMBDA_FIXTURE", "polar current input changed")
    _require(records["polar_pullback"]["result_id"] == "EINSTEIN_MAXWELL_WEYL_POLAR_ALL_ELL_SYMPLECTIC_RESTRICTION", "polar pullback input changed")
    _require(records["relative_triangle_preflight"]["classification"]["full_curved_all_sector_chain_map_certified"] is False, "relative triangle gate changed")
    contraction = _gauge_contraction()
    current = records["target_current_on_Einstein_image"]["current"]
    _require(len(current["coefficient_matrix"]) == 2, "restricted current dimension changed")
    return {
        "schema": "einstein-weyl-polar-offshell-operator-preflight-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "EINSTEIN_WEYL_POLAR_OFFSHELL_OPERATOR_PREFLIGHT",
        "result_state": "TARGET_WEYL_GAUGE_CONTRACTION_CERTIFIED_FULL_POLAR_EULER_OPERATOR_MISSING",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for name, path in INPUTS.items()},
        },
        "domain": "generic polar ell>=2 compact Fourier-polynomial block on the fixed magnetic bundle, before final residual quotient",
        "available_exact_inputs": {
            "Einstein_Maxwell": "complete 8-by-5 gauge-fixed polar equation matrix on (A,B,C,K,U)",
            "Weyl_Maxwell_current": "2-by-2 direct Lee-Wald current only after reconstruction onto Einstein master representatives",
            "Weyl_Maxwell_full_Euler_operator": None,
        },
        "target_Weyl_gauge_contraction": contraction,
        "why_the_current_is_not_the_operator": {
            "restricted_domain": "the current fixture substitutes the two Einstein master representatives and assumes nonzero mu before the separately certified mu=0 closure",
            "missing_information": [
                "the four independent target gauge-fixed Euler rows",
                "algebraic lower-order terms not recoverable from a Green current alone",
                "the extra target characteristic and invariant factors",
                "the equation and Noether row maps needed for an off-shell chain square",
            ],
            "verdict": "THE_EXISTING_POLAR_CURRENT_CANNOT_CERTIFY_A_POLAR_OFFSHELL_CHAIN_MAP",
        },
        "operator_acceptance_contract": {
            "target_coordinates": ["A+K", "B", "C-K", "U"],
            "required_target_operator": "a polynomial 4-by-4 action-normalized Weyl-Maxwell Hessian L_WM^P(lambda,k,omega)",
            "required_properties": [
                "direct four-dimensional tensor derivation before Einstein branch substitution",
                "formal self-adjointness under (omega,k)->(-omega,-k) and transpose",
                "no inversion of k, omega, lambda-2, or either characteristic polynomial",
                "exact determinant and physical-ring invariant-factor audit",
            ],
            "source_operator": "the certified 8-by-5 Einstein-Maxwell polar equation matrix E_P",
            "field_map": "S_P:(A,B,C,K,U)->(A+K,B,C-K,U)",
            "chain_square_to_solve": "L_WM^P*S_P=J_P*E_P for a polynomial 4-by-8 equation-row map J_P",
            "ungauged_lift": "lift through the three source polar Diff ghosts and four target Diff x Weyl ghosts, then verify the equation/identity square",
            "cofiber_gate": "construct the polar mapping cone only after these squares vanish; otherwise retain the normalized defect",
        },
        "recommended_computation": {
            "method": "directly linearize 3*B_ab-T_ab and Maxwell on independent polar coefficients, impose G=h_A=K'=0 only after deriving the tensor rows, and retain arbitrary omega and k",
            "fixtures": ["ell=2", "ell=3", "ell=4"],
            "promotion_rule": "interpolate in lambda only after proving the natural-operator degree bound and checking absence of hidden denominators",
        },
        "classification": {
            "correct_target_polar_field_slice_certified": True,
            "source_solution_kernel_injects_through_target_Weyl_slice": True,
            "full_target_polar_Euler_operator_constructed": False,
            "polar_offshell_chain_map_constructed": False,
            "polar_offshell_chain_map_obstructed": False,
            "polar_mapping_cofiber_constructed": False,
            "paper_A_freeze_affected": False,
            "quantum_import_gate_satisfied": False,
        },
        "next_gate": "compute the independent four-dimensional target polar Euler operator on the four-coordinate Weyl gauge slice, then solve or obstruct the polynomial row factorization L_WM^P S_P=J_P E_P",
        "claim_boundary": "This preflight certifies the correct polar Weyl gauge contraction and proves that its field kernel contains no Einstein-Maxwell solution. It does not construct the target polar Bach-Maxwell Euler operator, an off-shell polar chain map, a polar cofiber, an extra polar solution, a causal theory, or a quantum lift. It does not alter the theorem-frozen scope of Paper A, which excludes the polar extra branch.",
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_weyl_polar_offshell_operator_preflight --verify bridge/certificates/einstein_weyl_polar_offshell_operator_preflight.json",
            "python3 bridge/einstein_sector/verify_einstein_weyl_polar_offshell_operator_preflight.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_weyl_polar_offshell_operator_preflight",
        ],
    }


def verify_certificate(path: Path = DEFAULT_OUTPUT) -> None:
    _require(_load(path) == build_certificate(), f"polar off-shell preflight stale or altered: {path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    if args.write:
        DEFAULT_OUTPUT.write_text(json.dumps(build_certificate(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.verify:
        verify_certificate(args.verify)
    if not args.write and args.verify is None:
        parser.error("one of --write or --verify is required")


if __name__ == "__main__":
    main()
