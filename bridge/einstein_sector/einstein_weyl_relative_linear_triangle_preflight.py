"""Exact preflight for the relative Einstein--Weyl linear triangle.

This certificate deliberately separates the covariant principal-symbol map,
a complete off-shell generic-axial map, and the open full curved map.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp

from bridge.einstein_sector.einstein_maxwell_product_tangent_preflight import _principal_complex
from bridge.einstein_sector.einstein_maxwell_weyl_axial_operator import _generic_rows


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "bridge/certificates/einstein_weyl_relative_linear_triangle_preflight.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein_weyl_relative_linear_triangle_preflight.schema.json"
INPUTS = {
    "principal_complex": ROOT / "bridge/certificates/einstein_maxwell_product_tangent_preflight.json",
    "formal_solution_inclusion": ROOT / "bridge/certificates/einstein_maxwell_chevreton_formal_linearization.json",
    "standard_pairing": ROOT / "bridge/certificates/einstein_maxwell_weyl_standard_harmonic_symplectic_inclusion.json",
    "generic_axial_operator": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_operator.json",
    "generic_axial_physical_ring": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_physical_ring.json",
    "generic_axial_pairing": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_lee_wald_completion.json",
    "quadratic_charge_fixtures": ROOT / "bridge/certificates/einstein_maxwell_second_order_inclusion.json",
    "quadratic_axial_channel": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_quadratic_channel_preflight.json",
}


class RelativeTrianglePreflightError(RuntimeError):
    """Raised when a relative-chain or import check fails."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RelativeTrianglePreflightError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _zero(matrix: sp.MatrixBase) -> bool:
    return matrix.applyfunc(lambda value: sp.factor(sp.expand(value))) == sp.zeros(matrix.rows, matrix.cols)


def _matrix_strings(matrix: sp.MatrixBase) -> list[list[str]]:
    return [[str(sp.factor(matrix[row, column])) for column in range(matrix.cols)] for row in range(matrix.rows)]


def _mapping_cone(data: dict[str, sp.Matrix | sp.Expr]) -> dict[str, Any]:
    """Build Cone(f)^n=W^n+E^(n+1) for the four-term principal complexes."""

    gauge_e = data["gauge_e"]
    hessian_e = data["hessian_e"]
    noether_e = data["noether_e"]
    gauge_w = data["gauge_w"]
    hessian_w = data["hessian_w"]
    noether_w = data["noether_w"]
    ghost_map = data["ghost_map"]
    field_map = data["field_map"]
    equation_map = data["equation_map"]
    identity_map = data["identity_map"]
    matrices = (gauge_e, hessian_e, noether_e, gauge_w, hessian_w, noether_w, ghost_map, field_map, equation_map, identity_map)
    _require(all(isinstance(matrix, sp.MatrixBase) for matrix in matrices), "principal matrix payload changed")

    differentials = [
        sp.Matrix.vstack(ghost_map, -gauge_e),
        sp.Matrix.vstack(
            sp.Matrix.hstack(gauge_w, field_map),
            sp.Matrix.hstack(sp.zeros(hessian_e.rows, gauge_w.cols), -hessian_e),
        ),
        sp.Matrix.vstack(
            sp.Matrix.hstack(hessian_w, equation_map),
            sp.Matrix.hstack(sp.zeros(noether_e.rows, hessian_w.cols), -noether_e),
        ),
        sp.Matrix.hstack(noether_w, identity_map),
    ]
    squares = [differentials[index + 1] * differentials[index] for index in range(3)]
    _require(all(_zero(square) for square in squares), "principal mapping cone lost nilpotency")
    dimensions = [5, 20, 28, 19, 6]
    ranks = [matrix.rank() for matrix in differentials]
    cohomology = [
        dimension - (ranks[index] if index < len(ranks) else 0) - (ranks[index - 1] if index > 0 else 0)
        for index, dimension in enumerate(dimensions)
    ]
    return {
        "degree_labels": ["-1", "0", "1", "2", "3"],
        "dimensions": dimensions,
        "differential_ranks": ranks,
        "cohomology_dimensions": cohomology,
        "all_three_cone_squares_zero": True,
    }


def _generic_axial_chain_map() -> dict[str, Any]:
    """Construct an exact ungauged axial chain map over Q[lambda,k,omega]."""

    rows, symbols = _generic_rows()
    eigenvalue, momentum, frequency = symbols["lambda"], symbols["k"], symbols["omega"]
    coefficients = sp.Matrix([symbols["h_t"], symbols["h_x"], symbols["q_t"], symbols["q_x"]])
    source_hessian = sp.Matrix([
        [momentum**2 + eigenvalue, momentum * frequency, 2, 0],
        [momentum * frequency, frequency**2 - eigenvalue, 0, -2],
        [eigenvalue, 0, momentum**2 + eigenvalue, momentum * frequency],
        [0, -eigenvalue, momentum * frequency, frequency**2 - eigenvalue],
    ])
    target_hessian = sp.Matrix([
        eigenvalue * rows["metric_t"],
        -eigenvalue * rows["metric_x"],
        rows["maxwell_t"],
        rows["maxwell_x"],
    ]).jacobian(coefficients)
    reduced_equation_map = (target_hessian * source_hessian.inv()).applyfunc(lambda value: sp.factor(sp.cancel(value)))
    _require(_zero(target_hessian - reduced_equation_map * source_hessian), "reduced axial equation square failed")
    denominators = sorted({str(sp.factor(sp.denom(value))) for value in reduced_equation_map})
    _require(denominators == ["1", "2", "4"], "axial equation map acquired a physical denominator")

    imaginary = sp.I
    projection = sp.Matrix([
        [1, 0, imaginary * frequency / 2, 0, 0, 0],
        [0, 1, -imaginary * momentum / 2, 0, 0, 0],
        [0, 0, -imaginary * frequency / 2, 1, 0, imaginary * frequency],
        [0, 0, imaginary * momentum / 2, 0, 1, -imaginary * momentum],
    ])
    gauge = sp.Matrix([
        [-imaginary * frequency, 0],
        [imaginary * momentum, 0],
        [2, 0],
        [0, -imaginary * frequency],
        [0, imaginary * momentum],
        [1, 1],
    ])

    def adjoint(matrix: sp.MatrixBase) -> sp.Matrix:
        return matrix.subs({frequency: -frequency, momentum: -momentum}, simultaneous=True).T

    projection_adjoint = adjoint(projection)
    noether = adjoint(gauge)
    selector = sp.zeros(4, 6)
    selector[0, 0] = selector[1, 1] = selector[2, 3] = selector[3, 4] = 1
    _require(selector * projection_adjoint == sp.eye(4), "polynomial projection splitting changed")
    source_ungauged = (projection_adjoint * source_hessian * projection).applyfunc(sp.factor)
    target_ungauged = (projection_adjoint * target_hessian * projection).applyfunc(sp.factor)
    equation_map = (projection_adjoint * reduced_equation_map * selector).applyfunc(sp.factor)
    identity_map = sp.zeros(2)
    _require(_zero(source_ungauged * gauge), "source axial gauge identity failed")
    _require(_zero(target_ungauged * gauge), "target axial gauge identity failed")
    _require(_zero(noether * source_ungauged), "source axial Noether identity failed")
    _require(_zero(noether * target_ungauged), "target axial Noether identity failed")
    _require(_zero(target_ungauged - equation_map * source_ungauged), "ungauged field/equation square failed")
    _require(_zero(noether * equation_map - identity_map * noether), "ungauged equation/identity square failed")
    return {
        "domain": "generic axial ell>=2 Fourier-polynomial block before the final residual quotient",
        "complex_dimensions": {"source": [2, 6, 6, 2], "target": [2, 6, 6, 2]},
        "ghost_map": "identity on the axial Diff and U(1) parameters",
        "field_map": "identity on (h_t,h_x,h_2,q_t,q_x,b)",
        "reduced_equation_map_order": ["metric_t", "metric_x", "Maxwell_t", "Maxwell_x"],
        "reduced_equation_map": _matrix_strings(reduced_equation_map),
        "ungauged_equation_map_order": ["h_t", "h_x", "h_2", "q_t", "q_x", "b"],
        "ungauged_equation_map": _matrix_strings(equation_map),
        "identity_map": _matrix_strings(identity_map),
        "degreewise_map_ranks": [2, 6, equation_map.rank(), 0],
        "degreewise_injective": False,
        "injectivity_boundary": "the ghost and field maps are injective; the equation and identity lifts are not, so no strict short exact sequence of axial complexes is claimed",
        "chain_squares": {"ghost_field": "PASS", "field_equation": "PASS", "equation_identity": "PASS", "source_and_target_nilpotency": "PASS"},
        "denominators": denominators,
        "does_not_invert": ["k", "omega", "lambda", "lambda-2", "Einstein dispersion q", "extra dispersion p"],
        "verdict": "STRICT_OFFSHELL_POLYNOMIAL_CHAIN_MAP_IN_GENERIC_AXIAL_BLOCK",
    }


def build_certificate() -> dict[str, Any]:
    records = {name: _load(path) for name, path in INPUTS.items()}
    expected_ids = {
        "principal_complex": "EINSTEIN_MAXWELL_PRODUCT_TANGENT_PREFLIGHT",
        "formal_solution_inclusion": "EINSTEIN_MAXWELL_CHEVRETON_FORMAL_LINEARIZATION",
        "standard_pairing": "EINSTEIN_MAXWELL_WEYL_STANDARD_HARMONIC_SYMPLECTIC_INCLUSION",
        "generic_axial_operator": "EINSTEIN_MAXWELL_WEYL_AXIAL_OPERATOR",
        "generic_axial_physical_ring": "EINSTEIN_MAXWELL_WEYL_AXIAL_PHYSICAL_RING",
        "generic_axial_pairing": "EINSTEIN_MAXWELL_WEYL_AXIAL_LEE_WALD_COMPLETION",
        "quadratic_charge_fixtures": "EINSTEIN_MAXWELL_SECOND_ORDER_INCLUSION_TEST",
        "quadratic_axial_channel": "EINSTEIN_MAXWELL_WEYL_AXIAL_QUADRATIC_CHANNEL_PREFLIGHT",
    }
    for name, expected in expected_ids.items():
        _require(records[name].get("result_id") == expected, f"{name} import changed")
    _require(records["formal_solution_inclusion"]["classification"]["off_shell_BV_chain_map_constructed"] is False, "formal-inclusion boundary changed")
    _require(records["standard_pairing"]["classification"]["restricted_target_form_nondegenerate"] is True, "standard pairing import changed")
    _require(records["generic_axial_physical_ring"]["classification"]["Einstein_image_equals_complete_q_primary_summand_on_every_physical_fiber"] is True, "axial primary decomposition changed")

    alpha_b, kappa = sp.symbols("alpha_B kappa", nonzero=True, real=True)
    nonnull_cone = _mapping_cone(_principal_complex((1, 2, 3, 5), alpha_b, kappa))
    null_cone = _mapping_cone(_principal_complex((1, 0, 0, 1), alpha_b, kappa))
    _require(nonnull_cone["cohomology_dimensions"] == [0, 0, 0, 0, 0], "nonnull cone exactness changed")
    _require(null_cone["cohomology_dimensions"] == [0, 0, 4, 4, 0], "null cone cohomology changed")
    axial_map = _generic_axial_chain_map()

    return {
        "schema": "einstein-weyl-relative-linear-triangle-preflight-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "EINSTEIN_WEYL_RELATIVE_LINEAR_TRIANGLE_PREFLIGHT",
        "result_state": "PRINCIPAL_AND_GENERIC_AXIAL_OFFSHELL_CHAIN_MAPS_CERTIFIED_FULL_CURVED_ALL_SECTOR_TRIANGLE_OPEN",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for name, path in INPUTS.items()},
        },
        "degree_inventory": {
            "Einstein_Maxwell": {"dimensions": [5, 14, 14, 5], "degrees": ["Diff+U1 ghosts", "metric+connection fields", "metric+Maxwell equations", "Diff+U1 identities"]},
            "Weyl_Maxwell": {"dimensions": [6, 14, 14, 6], "degrees": ["Diff+U1+Weyl ghosts", "metric+connection fields", "metric+Maxwell equations", "Diff+U1+trace identities"]},
        },
        "map_disposition": {
            "common_background": "compactified magnetically supported Plebanski-Hacyan electrovacuum on the fixed U(1) bundle",
            "full_curved_solution_map": "ALL_FORMAL_JACOBI_FIELDS_INCLUDED",
            "full_curved_offshell_chain_map": "OPEN_NOT_CONSTRUCTED_AND_NOT_OBSTRUCTED",
            "principal_symbol": "STRICT_CHAIN_MAP",
            "generic_axial_ell_ge_2": "STRICT_OFFSHELL_POLYNOMIAL_CHAIN_MAP",
            "requested_EINSTEIN_WEYL_RELATIVE_LINEAR_TRIANGLE_V1": "NOT_YET_CERTIFIED",
        },
        "normalized_full_curved_defect": {
            "ghost_field_defect": "0 exactly for the common Diff x U(1) action and sigma_Weyl=0, including i_xi Fbar",
            "field_equation_defect": "Delta_1=H_WM*iota_field-iota_equation*H_EM",
            "principal_normalization": "sigma(iota_equation)=diag(alpha_B*kappa*Q_p,identity_Maxwell)",
            "certified_principal_symbol": "sigma(Delta_1)=0",
            "certified_on_shell_property": "Delta_1 Phi=0 whenever H_EM Phi=0",
            "unresolved_question": "whether lower-order differential rows complete iota_equation so Delta_1 vanishes identically",
            "identity_defect": "Delta_2=N_WM*iota_equation-iota_identity*N_EM remains open with the same lower-order completion",
            "obstruction_witness": None,
        },
        "principal_mapping_cofiber": {
            "convention": "Cone(iota)^n=W^n direct_sum E^(n+1), d_Cone=[[d_W,iota],[0,-d_E]]",
            "general_square_formula": "d_Cone^2 has upper-right block d_W*iota-iota*d_E and all other blocks zero",
            "nonnull_fixture": nonnull_cone,
            "null_fixture": null_cone,
            "interpretation": "the noncharacteristic principal cone is exact; at a null covector the relative BV symbol carries four field-side and four equation-side classes, not merely the two extra target field polarizations",
        },
        "generic_axial_offshell_triangle": axial_map,
        "generic_axial_solution_cofiber": {
            "physical_ring_result": "Einstein image is the complete q-primary target summand for every ell>=2 and every allowed compact momentum, including k=0",
            "cofiber": "(R_phys[omega]/(p))^2 with p=omega^2-k^2-lambda+2/3",
            "pairing": "direct four-dimensional Lee-Wald extra block is nonradical with positive-frequency current inertia (2,0)",
            "full_target_current_inertia": "(3,1)",
            "scope": "generic axial reduced modes only; no causal, particle, or quantum claim",
        },
        "global_curved_cofiber_gate": {
            "ordinary_mapping_cone_status": "NOT_YET_A_CERTIFIED_COMPLEX",
            "reason": "outside the principal and generic axial sectors the lower-order equation and identity maps have not been constructed, so the cone square is the unresolved normalized chain defect",
            "permitted_object": "a defect-marked cone precomplex whose square records Delta; do not compute or quote its cohomology",
            "strict_short_exact_sequence": False,
        },
        "sector_ledger": [
            {"sector": "generic axial ell>=2, all allowed k", "map": "strict off-shell polynomial", "cofiber": "two p-primary cyclic summands", "pairing": "direct Lee-Wald nonradical", "O2": "selected channels only"},
            {"sector": "polar standard Einstein image", "map": "on-shell complete", "cofiber": "extra target branch open", "pairing": "Einstein-image pullback complete", "O2": "selected axial-polar channel removable"},
            {"sector": "ell=1 exceptional", "map": "on-shell complete", "cofiber": "target complement not classified", "pairing": "Einstein-image pullback complete", "O2": "open"},
            {"sector": "ell=0 and global twists", "map": "on-shell complete", "cofiber": "target complement not classified", "pairing": "Einstein-image pullback complete", "O2": "fixed-charge radion and duality fixtures obstructed; charge-relaxed extensions exist"},
            {"sector": "boundaries or asymptotic domains", "map": "open", "cofiber": "open", "pairing": "boundary terms open", "O2": "open"},
        ],
        "quadratic_export": {
            "status": "PARTIAL_FIXTURES_NOT_A_BILINEAR_ON_COMPLETE_RELATIVE_COHOMOLOGY",
            "fixed_charge": "certified radion and Maxwell-duality obstructions plus selected extra-mode Taub fixtures",
            "variable_charge": "explicit radion and duality extensions",
            "generic_axial_mixed_channel": "one selected nonresonant source block is explicitly removable",
        },
        "classification": {
            "principal_BV_chain_map_and_cone_certified": True,
            "generic_axial_offshell_chain_map_certified": True,
            "generic_axial_solution_cofiber_and_pairing_certified": True,
            "full_curved_all_sector_chain_map_certified": False,
            "full_curved_chain_map_obstructed": False,
            "global_mapping_cofiber_complex_certified": False,
            "relative_O2_complete": False,
            "relative_linear_triangle_V1_certified": False,
            "quantum_import_gate_satisfied": False,
        },
        "next_gate": "derive or obstruct the lower-order curved equation and identity row maps in the polar, exceptional, and global blocks; only then assemble the global cone and compare its action-derived form",
        "claim_boundary": "This LOCAL-ALGEBRAIC/REDUCED-MODE preflight certifies the exact principal mapping cone and a strict polynomial off-shell chain map with solution cofiber and direct pairing in the generic axial block. It does not certify EINSTEIN_WEYL_RELATIVE_LINEAR_TRIANGLE_V1, a full curved all-sector cone, polar/exceptional/global relative cohomology, boundary closure, residual observables, a complete quadratic obstruction map, causal propagation, particles, or a quantum lift.",
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_weyl_relative_linear_triangle_preflight --verify bridge/certificates/einstein_weyl_relative_linear_triangle_preflight.json",
            "python3 bridge/einstein_sector/verify_einstein_weyl_relative_linear_triangle_preflight.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_weyl_relative_linear_triangle_preflight",
        ],
    }


def verify_certificate(path: Path = DEFAULT_OUTPUT) -> None:
    _require(_load(path) == build_certificate(), f"relative triangle preflight stale or altered: {path}")


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
