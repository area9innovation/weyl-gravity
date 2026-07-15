"""Local on-shell branch projectors for the compensated flat TT theory.

For ``L=Box(Box+M2)`` with ``M2 != 0``, the solution-space operators

    Pi_E = 1 + Box/M2,       Pi_M = -Box/M2

are complementary differential projectors onto the massless Einstein and
massive spin-2 branches.  This module certifies their quotient-polynomial,
Cauchy-evolution, symplectic, support, infrared, and source identities.

The projectors are local inside the already reduced TT sector.  This does not
make the spatial TT projection from an unreduced metric local, and it is not a
full Diff x Weyl BV projector.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = (
    ROOT / "bridge" / "certificates" / "compensated_einstein_local_projectors.json"
)
SCHEMA_PATH = (
    ROOT
    / "bridge"
    / "einstein_sector"
    / "schema"
    / "compensated_einstein_local_projectors.schema.json"
)
INPUTS = {
    "causal_subsector": ROOT
    / "bridge"
    / "certificates"
    / "compensated_einstein_causal_subsector.json"
}


class CompensatedEinsteinLocalProjectorError(RuntimeError):
    """Raised when a projector identity or scope guard regresses."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise CompensatedEinsteinLocalProjectorError(message)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _polynomial_checks() -> dict[str, Any]:
    y, mass_squared = sp.symbols("y M2", nonzero=True)
    equation = y * (y + mass_squared)
    projector_e = 1 + y / mass_squared
    projector_m = -y / mass_squared

    def remainder(expr: sp.Expr) -> sp.Expr:
        numerator = sp.together(expr).as_numer_denom()[0]
        return sp.simplify(sp.rem(sp.Poly(numerator, y), sp.Poly(equation, y)).as_expr())

    _require(sp.simplify(projector_e + projector_m - 1) == 0, "projectors are not complete")
    _require(remainder(projector_e**2 - projector_e) == 0, "Einstein projector is not idempotent")
    _require(remainder(projector_m**2 - projector_m) == 0, "massive projector is not idempotent")
    _require(remainder(projector_e * projector_m) == 0, "projectors are not orthogonal")
    _require(remainder(y * projector_e) == 0, "Einstein image is not massless")
    _require(
        remainder((y + mass_squared) * projector_m) == 0,
        "massive image misses its Klein-Gordon branch",
    )

    return {
        "equation_ideal": "L(y)=y(y+M2)",
        "quotient_ring": "Q(M2)[y]/(y(y+M2)), with M2!=0",
        "einstein_projector": "Pi_E=1+y/M2",
        "massive_projector": "Pi_M=-y/M2",
        "completeness": "Pi_E+Pi_M=1 exactly",
        "on_shell_idempotence": ["Pi_E^2=Pi_E mod L", "Pi_M^2=Pi_M mod L"],
        "on_shell_orthogonality": "Pi_E Pi_M=0 mod L",
        "image_equations": ["y Pi_E=0 mod L", "(y+M2)Pi_M=0 mod L"],
        "status": "PASS",
    }


def _cauchy_projector_checks() -> dict[str, Any]:
    q, mass_squared = sp.symbols("q M2", positive=True)
    evolution = sp.Matrix(
        [
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1],
            [-q * (q + mass_squared), 0, -(2 * q + mass_squared), 0],
        ]
    )
    einstein_embedding = sp.Matrix([[1, 0], [0, 1], [-q, 0], [0, -q]])
    massive_embedding = sp.Matrix(
        [[1, 0], [0, 1], [-(q + mass_squared), 0], [0, -(q + mass_squared)]]
    )
    branch_basis = sp.Matrix.hstack(einstein_embedding, massive_embedding)
    split_e = sp.diag(1, 1, 0, 0)
    split_m = sp.diag(0, 0, 1, 1)
    projector_e = sp.simplify(branch_basis * split_e * branch_basis.inv())
    projector_m = sp.simplify(branch_basis * split_m * branch_basis.inv())

    _require(sp.simplify(projector_e + projector_m) == sp.eye(4), "Cauchy projectors are incomplete")
    _require(sp.simplify(projector_e**2 - projector_e) == sp.zeros(4), "Cauchy Pi_E not idempotent")
    _require(sp.simplify(projector_m**2 - projector_m) == sp.zeros(4), "Cauchy Pi_M not idempotent")
    _require(sp.simplify(projector_e * projector_m) == sp.zeros(4), "Cauchy projectors overlap")
    _require(sp.simplify(projector_e * evolution - evolution * projector_e) == sp.zeros(4), "Pi_E does not commute with evolution")
    _require(sp.simplify(projector_m * evolution - evolution * projector_m) == sp.zeros(4), "Pi_M does not commute with evolution")
    _require(
        sp.simplify(projector_e * einstein_embedding - einstein_embedding)
        == sp.zeros(4, 2),
        "Pi_E is not identity on Einstein data",
    )
    _require(
        sp.simplify(projector_e * massive_embedding) == sp.zeros(4, 2),
        "Pi_E retains massive data",
    )
    _require(
        sp.simplify(projector_m * massive_embedding - massive_embedding)
        == sp.zeros(4, 2),
        "Pi_M is not identity on massive data",
    )
    _require(
        sp.simplify(projector_m * einstein_embedding) == sp.zeros(4, 2),
        "Pi_M retains Einstein data",
    )

    expected_first_rows = sp.Matrix(
        [
            [(q + mass_squared) / mass_squared, 0, 1 / mass_squared, 0],
            [0, (q + mass_squared) / mass_squared, 0, 1 / mass_squared],
        ]
    )
    _require(
        sp.simplify(projector_e[:2, :] - expected_first_rows) == sp.zeros(2, 4),
        "Cauchy Pi_E does not realize h+chi/M2",
    )

    return {
        "cauchy_vector": "X=(h,d_t h,d_t^2 h,d_t^3 h)",
        "field_form": ["Pi_E h=h+chi/M2", "Pi_M h=-chi/M2", "chi=Box h"],
        "einstein_projector_matrix": [
            ["(q+M2)/M2", "0", "1/M2", "0"],
            ["0", "(q+M2)/M2", "0", "1/M2"],
            ["-q(q+M2)/M2", "0", "-q/M2", "0"],
            ["0", "-q(q+M2)/M2", "0", "-q/M2"],
        ],
        "massive_projector": "P_M=I_4-P_E",
        "identities": [
            "P_E^2=P_E",
            "P_M^2=P_M",
            "P_E P_M=P_M P_E=0",
            "P_E+P_M=I_4",
        ],
        "evolution": ["[P_E,A_4]=0", "[P_M,A_4]=0"],
        "branch_action": [
            "P_E I_E=I_E",
            "P_E I_M=0",
            "P_M I_M=I_M",
            "P_M I_E=0",
        ],
        "status": "PASS",
    }


def _symplectic_checks() -> dict[str, Any]:
    q, mass_squared, c1 = sp.symbols("q M2 c1", nonzero=True)
    einstein_embedding = sp.Matrix([[1, 0], [0, 1], [-q, 0], [0, -q]])
    massive_embedding = sp.Matrix(
        [[1, 0], [0, 1], [-(q + mass_squared), 0], [0, -(q + mass_squared)]]
    )
    branch_basis = sp.Matrix.hstack(einstein_embedding, massive_embedding)
    canonical = sp.Matrix([[0, 1], [-1, 0]])
    branch_form = sp.diag(c1 * canonical / 2, -c1 * canonical / 2)
    cauchy_form = sp.simplify(branch_basis.inv().T * branch_form * branch_basis.inv())
    projector_e = sp.simplify(branch_basis * sp.diag(1, 1, 0, 0) * branch_basis.inv())
    projector_m = sp.eye(4) - projector_e

    _require(
        sp.simplify(projector_e.T * cauchy_form - cauchy_form * projector_e)
        == sp.zeros(4),
        "Einstein projector is not symplectically self-adjoint",
    )
    _require(
        sp.simplify(projector_m.T * cauchy_form - cauchy_form * projector_m)
        == sp.zeros(4),
        "massive projector is not symplectically self-adjoint",
    )
    _require(
        sp.simplify(projector_e.T * cauchy_form * projector_m) == sp.zeros(4),
        "branch cross pairing survived projection",
    )
    _require(
        sp.simplify(einstein_embedding.T * cauchy_form * einstein_embedding)
        == c1 * canonical / 2,
        "Einstein projected form changed",
    )
    _require(
        sp.simplify(massive_embedding.T * cauchy_form * massive_embedding)
        == -c1 * canonical / 2,
        "massive projected form changed",
    )

    return {
        "self_adjointness": ["P_E^T Omega=Omega P_E", "P_M^T Omega=Omega P_M"],
        "cross_block": "P_E^T Omega P_M=0",
        "einstein_block": "I_E^T Omega I_E=(c1/2)J_2",
        "massive_block": "I_M^T Omega I_M=-(c1/2)J_2",
        "conclusion": "the local branch splitting is the certified symplectic block decomposition",
        "status": "PASS",
    }


def _source_checks() -> dict[str, Any]:
    y, mass_squared, source = sp.symbols("y M2 J", nonzero=True)
    h = sp.symbols("h")
    equation = sp.Eq(y * (y + mass_squared) * h, source)
    einstein_piece = (1 + y / mass_squared) * h
    massive_piece = -y * h / mass_squared
    substitution = {y**2 * h: source - mass_squared * y * h}

    einstein_equation = sp.expand(y * einstein_piece).subs(substitution)
    massive_equation = sp.expand((y + mass_squared) * massive_piece).subs(substitution)
    _require(sp.simplify(einstein_equation - source / mass_squared) == 0, "sourced Einstein split changed")
    _require(sp.simplify(massive_equation + source / mass_squared) == 0, "sourced massive split changed")
    _require(equation.rhs == source, "source premise changed")

    return {
        "sourced_equation": "Box(Box+M2)h=J",
        "projected_equations": [
            "Box(Pi_E h)=J/M2",
            "(Box+M2)(Pi_M h)=-J/M2",
        ],
        "einstein_only_condition": (
            "Pi_M h=0 is compatible with the displayed scalar TT source equation only when J=0"
        ),
        "interpretation": (
            "the projectors split a sourced response but a generic source excites both branches; "
            "a sourced Einstein defect must be defined relative to the sourced Einstein equation"
        ),
        "status": "PASS",
    }


def _validate_contract(payload: dict[str, Any]) -> None:
    schema = _load(SCHEMA_PATH)
    _require(
        schema.get("$id") == "compensated-einstein-local-projectors-v1",
        "wrong local-projector schema id",
    )
    for key in schema.get("required", []):
        _require(key in payload, f"local-projector certificate is missing {key}")
    _require(payload.get("schema") == schema.get("$id"), "schema mismatch")
    _require(payload.get("schema_sha256") == _sha256(SCHEMA_PATH), "schema hash mismatch")
    _require(
        payload.get("dependency_tags")
        == ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "wrong dependency tags",
    )
    _require(
        payload.get("provenance", {}).get("generator_sha256") == _sha256(Path(__file__)),
        "generator hash mismatch",
    )
    _require(
        payload.get("verdict") == "LOCAL_ON_SHELL_EINSTEIN_MASSIVE_PROJECTORS_CERTIFIED_TT_SCOPE",
        "local-projector verdict changed",
    )
    flags = payload.get("claim_flags", {})
    required_flags = schema.get("properties", {}).get("claim_flags", {}).get("required", [])
    _require(set(flags) == set(required_flags), "claim flag inventory mismatch")
    true_flags = {
        "on_shell_projectors_derived",
        "projector_idempotence_exact",
        "projector_completeness_exact",
        "projector_orthogonality_exact",
        "projectors_commute_with_free_evolution",
        "projectors_support_nonincreasing_in_reduced_tt",
        "symplectic_block_decomposition_exact",
        "projectors_regular_at_q_zero_for_nonzero_M2",
        "pure_weyl_limit_singular",
        "sourced_branch_equations_derived",
        "generic_source_excites_massive_branch",
        "tt_locality_boundary_declared",
    }
    _require(all(flags.get(name) is True for name in true_flags), "proved flag missing")
    _require(
        all(flags.get(name) is False for name in set(required_flags) - true_flags),
        "an open claim was promoted",
    )


def build_certificate() -> dict[str, Any]:
    causal = _load(INPUTS["causal_subsector"])
    _require(
        causal.get("verdict")
        == "LINEAR_FLAT_TT_EINSTEIN_SECTOR_CAUSALLY_CLOSED_AND_SYMPLECTIC",
        "causal-subsector premise changed",
    )
    _require(
        causal.get("claim_flags", {}).get("restricted_pairing_nondegenerate") is True
        and causal.get("claim_flags", {}).get("full_metric_diff_weyl_bv_complex_constructed")
        is False,
        "causal-subsector scope gate changed",
    )

    certificate = {
        "schema": "compensated-einstein-local-projectors-v1",
        "schema_path": (
            "bridge/einstein_sector/schema/"
            "compensated_einstein_local_projectors.schema.json"
        ),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "COMPENSATED_EINSTEIN_LOCAL_PROJECTORS",
        "result_state": "LOCAL_ON_SHELL_TT_BRANCH_SPLITTING_CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "provenance": {
            "input_base_commit": "4eecb219843281d0375b835d37e5b25e7b067039",
            "generator_path": (
                "bridge/einstein_sector/compensated_einstein_local_projectors.py"
            ),
            "generator_sha256": _sha256(Path(__file__)),
        },
        "inputs": {
            name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)}
            for name, path in INPUTS.items()
        },
        "domain": {
            "spacetime": "four-dimensional Minkowski space",
            "theory": "source-free constant-compensator Einstein-Weyl TT equation unless the source audit is invoked",
            "parameters": "M2=c1/alpha is nonzero; causal massive interpretation additionally assumes M2>0",
            "field_domain": "already transverse-traceless reduced metric amplitudes",
            "operator_domain": "smooth or distributional TT solutions on which constant-coefficient differential operators act",
        },
        "quotient_polynomial_theorem": _polynomial_checks(),
        "cauchy_projector_theorem": _cauchy_projector_checks(),
        "symplectic_projector_theorem": _symplectic_checks(),
        "support_and_ir_audit": {
            "position_space_operators": [
                "Pi_E=1+Box/M2",
                "Pi_M=-Box/M2",
            ],
            "differential_order": 2,
            "support_property": "supp(Pi_E f) subset supp(f) and supp(Pi_M f) subset supp(f)",
            "causal_consequence": "the free solution splitting introduces no spacelike or future-boundary tail",
            "q_zero": (
                "the projectors contain no inverse q or inverse |k| and are algebraically regular at q=0 for M2!=0"
            ),
            "existing_q_zero_exclusion": (
                "the prior helicity-wave-packet domain excludes k=0 because a global helicity frame and radiative polarization basis degenerate there, not because Pi_E or Pi_M is singular"
            ),
            "pure_weyl_limit": "M2->0 makes both projectors singular as the simple roots coalesce",
        },
        "source_audit": _source_checks(),
        "tt_locality_audit": {
            "local_statement": "Pi_E and Pi_M are local differential operators on already-TT fields",
            "nonlocal_step_not_used": (
                "constructing a spatial TT representative from a general metric perturbation can require inverse elliptic operators"
            ),
            "consequence": (
                "this certificate cannot be promoted to a local projector on the unreduced metric BV complex"
            ),
            "next_required_object": (
                "a gauge-covariant Einstein-defect subcomplex on the full Diff x Weyl BV fields, avoiding reliance on a nonlocal TT projection"
            ),
        },
        "verdict": "LOCAL_ON_SHELL_EINSTEIN_MASSIVE_PROJECTORS_CERTIFIED_TT_SCOPE",
        "claim_flags": {
            "on_shell_projectors_derived": True,
            "projector_idempotence_exact": True,
            "projector_completeness_exact": True,
            "projector_orthogonality_exact": True,
            "projectors_commute_with_free_evolution": True,
            "projectors_support_nonincreasing_in_reduced_tt": True,
            "symplectic_block_decomposition_exact": True,
            "projectors_regular_at_q_zero_for_nonzero_M2": True,
            "pure_weyl_limit_singular": True,
            "sourced_branch_equations_derived": True,
            "generic_source_excites_massive_branch": True,
            "tt_locality_boundary_declared": True,
            "local_projector_on_unreduced_metric_bv_complex": False,
            "spatial_tt_projection_proved_local": False,
            "generic_source_preserves_einstein_only_sector": False,
            "source_compatible_einstein_defect_complex_constructed": False,
            "reduced_retarded_green_split_constructed": False,
            "full_metric_diff_weyl_bv_projector_constructed": False,
            "nonlinear_projector_constructed": False,
            "null_infinity_projector_constructed": False,
            "einstein_scattering_equivalence_proved": False,
        },
        "scope_guards": [
            "the algebraic identities hold on shell modulo Box(Box+M2)",
            "support-nonincreasing locality applies to Pi_E and Pi_M on already-TT fields",
            "no locality claim is made for the spatial TT reduction of a general metric perturbation",
            "q=0 regularity of the branch projectors does not define a global helicity frame at zero momentum",
            "a generic source splits into oppositely sourced branches and does not preserve Pi_M h=0",
            "the M2->0 pure-Weyl limit is singular and retains the certified zero-pairing obstruction",
            "no full BV, nonlinear, boundary, scattering, or quantum projector is claimed",
        ],
        "verification_command": (
            "python3 -m bridge.einstein_sector.compensated_einstein_local_projectors "
            "--verify bridge/certificates/compensated_einstein_local_projectors.json"
        ),
    }
    _validate_contract(certificate)
    return certificate


def verify_certificate(path: Path = DEFAULT_OUTPUT) -> None:
    _require(_load(path) == build_certificate(), f"certificate is stale or altered: {path}")


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
