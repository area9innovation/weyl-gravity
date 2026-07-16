"""Exact differential-module guardrails for the axial extra-branch solve."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_operator_module_preflight.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_axial_operator_module_preflight.schema.json"
INPUTS = {
    "extra_branch_preflight": ROOT / "bridge/certificates/einstein_maxwell_weyl_extra_branch_preflight.json",
    "source_axial_complex": ROOT / "bridge/certificates/einstein_maxwell_axial_master_complex.json",
    "target_principal_complex": ROOT / "bridge/certificates/einstein_maxwell_product_tangent_preflight.json",
    "linear_inclusion": ROOT / "bridge/certificates/einstein_maxwell_chevreton_tangent.json",
    "background": ROOT / "bridge/certificates/einstein_maxwell_product_incidence.json",
}


class AxialOperatorModulePreflightError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AxialOperatorModulePreflightError(message)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _rows(matrix: sp.Matrix) -> list[list[str]]:
    return [[str(matrix[row, column]) for column in range(matrix.cols)] for row in range(matrix.rows)]


def _gauge_contraction() -> dict[str, Any]:
    derivative, momentum = sp.symbols("D k", commutative=True)
    imaginary = sp.I
    # u=(h_t,h_x,h_2,q_t,q_x,b), epsilon=(s,r).
    gauge = sp.Matrix(
        [
            [derivative, 0],
            [imaginary * momentum, 0],
            [2, 0],
            [0, derivative],
            [0, imaginary * momentum],
            [1, 1],
        ]
    )
    projection = sp.Matrix(
        [
            [1, 0, -derivative / 2, 0, 0, 0],
            [0, 1, -imaginary * momentum / 2, 0, 0, 0],
            [0, 0, derivative / 2, 1, 0, -derivative],
            [0, 0, imaginary * momentum / 2, 0, 1, -imaginary * momentum],
        ]
    )
    inclusion = sp.Matrix(
        [
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1],
            [0, 0, 0, 0],
        ]
    )
    homotopy = sp.Matrix(
        [
            [0, 0, sp.Rational(1, 2), 0, 0, 0],
            [0, 0, -sp.Rational(1, 2), 0, 0, 1],
        ]
    )
    identity_six = sp.eye(6)
    identity_four = sp.eye(4)
    identity_two = sp.eye(2)
    _require(projection * gauge == sp.zeros(4, 2), "axial invariants are not gauge invariant")
    _require(projection * inclusion == identity_four, "axial projection/inclusion identity failed")
    _require(identity_six - inclusion * projection == gauge * homotopy, "axial contraction identity failed")
    _require(homotopy * gauge == identity_two, "axial gauge homotopy identity failed")
    slice_action = sp.Matrix([[2, 0], [1, 1]])
    _require(slice_action.det() == 2, "axial algebraic gauge slice pivot changed")
    return {
        "ring_symbols": {"D": "partial_t", "k": "S1 Fourier momentum", "I": "sqrt(-1)"},
        "ungauged_coefficient_order": ["h_t", "h_x", "h_2", "q_t", "q_x", "b"],
        "gauge_parameter_order": ["s", "r"],
        "gauge_map_G": _rows(gauge),
        "invariant_order": ["H_t", "H_x", "Q_t", "Q_x"],
        "invariants": [
            "H_t=h_t-(D/2)h_2",
            "H_x=h_x-(I*k/2)h_2",
            "Q_t=q_t-D*(b-h_2/2)",
            "Q_x=q_x-I*k*(b-h_2/2)",
        ],
        "projection_K": _rows(projection),
        "slice_inclusion_J": _rows(inclusion),
        "gauge_homotopy_H": _rows(homotopy),
        "identities": {
            "K_G": "0",
            "K_J": "I_4",
            "I_6_minus_J_K": "G_H",
            "H_G": "I_2",
        },
        "algebraic_slice": "h_2=0 and b=0",
        "slice_parameter_matrix": [["2", "0"], ["1", "1"]],
        "slice_determinant": "2",
        "denominators_introduced": ["2"],
        "no_inverse_D": True,
        "no_inverse_k": True,
        "no_dispersion_denominator": True,
        "target_axial_Weyl_parameter": "none: a scalar Weyl variation is even parity and has zero projection to the odd axial block",
        "scope": "ell>=2, where h_2 X_(ab) is nonzero; ell=1 is a separate exceptional complex",
    }


def _operator_contract() -> dict[str, Any]:
    return {
        "base_ring_before_localization": "A=Q[I,lambda,k][D], D=partial_t",
        "generic_PID_for_invariant_factors": "R=Frac(Q[I,lambda,k])[D]",
        "involution_for_formal_adjoint": ["D^dagger=-D", "(I*k)^dagger=-I*k", "lambda^dagger=lambda"],
        "ungauged_complex": "A^2 --G--> A^6 --L_WM,ax--> A^r with L_WM,ax*G=0",
        "solution_cohomology": "ker(L_WM,ax on the declared temporal function space)/im(G); it is not identified with a bare matrix cokernel",
        "gauge_fixed_operator": "L_red is obtained through the certified K,J contraction without inverting D or k",
        "module_presentation": "compute exact invariant factors/Smith data of the gauge-fixed differential presentation over R, while retaining every localization denominator in A",
        "solution_extraction_order": [
            "construct and verify the differential presentation",
            "compute invariant factors, torsion, free parts, multiplicities, and primary decomposition",
            "stratify all localization and rank-exception loci in (lambda,k)",
            "only then substitute D=-I*omega to report dispersions and generalized/Jordan solutions",
        ],
        "forbidden": [
            "solving only det L(-I*omega)=0",
            "dividing by D, k, omega, a branch polynomial, or an unrecorded minor",
            "counting roots without geometric multiplicities and gauge quotient witnesses",
            "calling coker(L) the solution space without the declared solution functor",
        ],
    }


def _hessian_noether_green_rail() -> dict[str, Any]:
    return {
        "independent_derivations": {
            "Hessian_route": "take the exact second variation of the declared Weyl-Maxwell action and project to the ungauged axial coefficient basis",
            "equation_route": "linearize the Bach-Maxwell Euler-Lagrange tensors independently and project the complete odd-parity tensor rows",
            "required_equality": "the two coefficient operators agree exactly after the declared row normalization",
        },
        "required_identities": [
            "L_WM,ax*G=0 coefficientwise",
            "G^dagger*L_WM,ax=0 coefficientwise",
            "L_WM,ax=L_WM,ax^dagger after the field/equation density pairing is declared",
            "the Einstein source-image reconstruction is annihilated modulo its certified source equations",
            "d_t omega^t+I*k*omega^x=u^T L_WM,ax v-(L_WM,ax u)^T v for arbitrary off-shell coefficient jets",
        ],
        "normalization_requirements": [
            "record harmonic norms and every integration-by-parts factor",
            "retain background-flux metric/Maxwell mixing",
            "match the already certified on-shell Einstein restriction when both arguments lie in the source image",
        ],
        "target_operator_inserted": False,
        "Hessian_equation_equality_verified": False,
        "Noether_identities_verified": False,
        "Green_identity_verified": False,
        "source_image_annihilation_replayed": False,
    }


def _pivot_and_fixture_contract() -> dict[str, Any]:
    return {
        "generic_locus": "lambda*(lambda-2) != 0; k remains symbolic and may equal zero unless an explicitly recorded target minor requires a separate stratum",
        "mandatory_strata": [
            {"locus": "lambda=0", "meaning": "homogeneous ell=0; different tensor basis"},
            {"locus": "lambda=2", "meaning": "ell=1; h_2 absent and residual/global gauge changes"},
            {"locus": "k=0", "meaning": "zero Fourier block; retain twists and polynomial/Jordan solutions"},
            {"locus": "each target pivot numerator or denominator=0", "meaning": "rank/localization stratum to solve without the invalid pivot"},
            {"locus": "resultant/discriminant=0", "meaning": "colliding primary factors or enhanced Jordan multiplicity"},
        ],
        "denominator_ledger_rule": "store every factor inverted during row/column reduction with its source minor and solve its zero locus separately",
        "rank_rule": "certify generic and exceptional ranks by exact minors or normal forms, never by numerical samples",
        "current_guardrail_denominator_ledger": [{"factor": "2", "source": "algebraic (h_2,b) gauge slice", "zero_locus": "empty over characteristic zero"}],
        "ell2_independent_replay": {
            "harmonic": "Y_20=P_2(cos theta)",
            "momentum": "symbolic k",
            "temporal_variable": "off-shell D, or equivalently symbolic omega before any branch substitution",
            "route": "full four-dimensional tensor linearization, independent of the arbitrary-lambda harmonic reduction",
            "required_comparisons": [
                "all target coefficient rows at lambda=6",
                "gauge and Noether identities",
                "operator invariant factors and exceptional denominators",
                "Einstein-image annihilation and the complete mixed Lee-Wald matrix",
            ],
            "branch_substitution_allowed": False,
            "completed": False,
        },
    }


def build_certificate() -> dict[str, Any]:
    records = {name: _load(path) for name, path in INPUTS.items()}
    expected = {
        "extra_branch_preflight": "EINSTEIN_MAXWELL_WEYL_EXTRA_BRANCH_PREFLIGHT",
        "source_axial_complex": "COMPACT_EM_AXIAL_MASTER_COMPLEX",
        "target_principal_complex": "EINSTEIN_MAXWELL_PRODUCT_TANGENT_PREFLIGHT",
        "linear_inclusion": "EINSTEIN_MAXWELL_CHEVRETON_TANGENT",
        "background": "EINSTEIN_MAXWELL_PRODUCT_INCIDENCE",
    }
    for name, result_id in expected.items():
        _require(records[name]["result_id"] == result_id, f"{name} input changed")
    _require(records["source_axial_complex"]["classification"]["all_n_axial_master_complex_ell_ge_2"] is True, "source axial quotient incomplete")
    _require(records["extra_branch_preflight"]["classification"]["generic_axial_declared_first"] is True, "parent preflight priority changed")
    return {
        "schema": "einstein-maxwell-weyl-axial-operator-module-preflight-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "EINSTEIN_MAXWELL_WEYL_AXIAL_OPERATOR_MODULE_PREFLIGHT",
        "result_state": "EXACT_AXIAL_GAUGE_MODULE_CONTRACTED_OPERATOR_NOETHER_PIVOT_AND_ELL2_RAILS_FROZEN",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G2_GENERIC_AXIAL_OPERATOR_MODULE_PREFLIGHT",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for name, path in INPUTS.items()},
        },
        "domain": "generic axial ell>=2 coefficient complex for the candidate full fixed-bundle Weyl-Maxwell harmonic tangent, symbolic S1 momentum and exact temporal differential algebra, before final residual quotient",
        "gauge_module_contraction": _gauge_contraction(),
        "operator_module_contract": _operator_contract(),
        "hessian_noether_green_rail": _hessian_noether_green_rail(),
        "pivot_and_fixture_contract": _pivot_and_fixture_contract(),
        "classification": {
            "full_ungauged_axial_coefficient_module_frozen": True,
            "target_axial_gauge_module_frozen": True,
            "exact_gauge_contraction_without_D_or_k_inverse": True,
            "differential_module_solution_functor_frozen": True,
            "formal_adjoint_involution_frozen": True,
            "pivot_and_exceptional_locus_ledger_frozen": True,
            "independent_ell2_replay_contract_frozen": True,
            "target_axial_operator_constructed": False,
            "target_Hessian_Noether_Green_rails_passed": False,
            "ell2_full_tensor_replay_passed": False,
            "canonical_extra_quotient_computed": False,
            "extra_solution_or_particle_certified": False,
            "lorentzian_causal_or_quantum_theorem": False,
        },
        "interpretation": "The generic axial target solve now has an exact algebraic chassis. The odd-parity gauge module contracts from six coefficients to four invariants using only the harmless constant pivot 2, so no zero-momentum or zero-frequency modes can be lost by gauge fixing. The future fourth-order operator must pass independent Hessian, Noether, Green-identity, pivot-stratification, and full-tensor ell=2 rails before any frequency roots are interpreted.",
        "next_gate": "derive and insert the complete generic axial Weyl-Maxwell Hessian/operator in the frozen six-coefficient basis, pass the Noether and Green rails, and replay the independent full-tensor ell=2 fixture before quotient/root extraction",
        "claim_boundary": "This LOCAL-ALGEBRAIC/REDUCED-MODE preflight certifies the axial coefficient/gauge contraction and freezes exact operator-module, adjoint, pivot, and fixture rules. It does not construct the target axial operator, pass its Hessian/Noether/Green checks, compute an extra quotient or dispersion, or establish causal, particle, or quantum physics.",
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_axial_operator_module_preflight --verify bridge/certificates/einstein_maxwell_weyl_axial_operator_module_preflight.json",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_axial_operator_module_preflight.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_axial_operator_module_preflight",
        ],
    }


def verify_certificate(path: Path = DEFAULT_OUTPUT) -> None:
    _require(_load(path) == build_certificate(), f"stale axial operator-module preflight: {path}")


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
