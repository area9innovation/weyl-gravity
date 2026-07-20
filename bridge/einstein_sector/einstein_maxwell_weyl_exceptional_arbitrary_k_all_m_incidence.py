"""Certify the all-m incidence geometry of the locked exceptional resonance."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/EINSTEIN_MAXWELL_WEYL_EXCEPTIONAL_ARBITRARY_K_ALL_M_INCIDENCE_V1.json"
ATLAS = ROOT / "residual_atlas/einstein-exceptional-arbitrary-k-all-m-incidence-fragment.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein-maxwell-weyl-exceptional-arbitrary-k-all-m-incidence-v1.schema.json"
INPUT = ROOT / "bridge/certificates/EINSTEIN_MAXWELL_WEYL_EXCEPTIONAL_ARBITRARY_K_LOCKED_RESONANCE_V1.json"


class AllMIncidenceError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AllMIncidenceError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    _require(isinstance(value, dict), f"expected object: {path}")
    return value


def _matrix_strings(matrix: sp.MatrixBase) -> list[list[str]]:
    return [
        [str(sp.factor(matrix[row, column])) for column in range(matrix.cols)]
        for row in range(matrix.rows)
    ]


def _coordinates(matrix: sp.Matrix, basis: list[sp.Matrix]) -> sp.Matrix:
    columns = sp.Matrix.hstack(*(value.reshape(9, 1) for value in basis))
    solution, parameters = columns.gauss_jordan_solve(matrix.reshape(9, 1))
    _require(parameters.rows == 0, "STF coordinate solve became nonunique")
    return solution


def _representation_certificate() -> dict[str, Any]:
    one = sp.Integer(1)
    half = sp.Rational(1, 2)
    basis = [
        sp.diag(one, -one, 0),
        sp.Matrix([[0, one, 0], [one, 0, 0], [0, 0, 0]]),
        sp.Matrix([[0, 0, one], [0, 0, 0], [one, 0, 0]]),
        sp.Matrix([[0, 0, 0], [0, 0, one], [0, one, 0]]),
        sp.diag(-half, -half, one),
    ]
    generators = [
        sp.Matrix([[0, 0, 0], [0, 0, -1], [0, 1, 0]]),
        sp.Matrix([[0, 0, 1], [0, 0, 0], [-1, 0, 0]]),
        sp.Matrix([[0, -1, 0], [1, 0, 0], [0, 0, 0]]),
    ]
    v2_generators = []
    for generator in generators:
        columns = [
            _coordinates(generator * tensor - tensor * generator, basis)
            for tensor in basis
        ]
        v2_generators.append(sp.Matrix.hstack(*columns))

    product_generators = [
        sp.kronecker_product(generator, sp.eye(5))
        + sp.kronecker_product(sp.eye(3), v2_generator)
        for generator, v2_generator in zip(generators, v2_generators, strict=True)
    ]
    canonical = sp.zeros(3, 15)
    for vector_index in range(3):
        vector = sp.eye(3)[:, vector_index]
        for tensor_index, tensor in enumerate(basis):
            canonical[:, 5 * vector_index + tensor_index] = tensor * vector
    for generator, product_generator in zip(generators, product_generators, strict=True):
        _require(
            generator * canonical == canonical * product_generator,
            "the Cartesian Yx map ceased to intertwine rotations",
        )

    variables = sp.symbols("t0:45")
    unknown = sp.Matrix(3, 15, variables)
    equations: list[sp.Expr] = []
    for generator, product_generator in zip(generators, product_generators, strict=True):
        equations.extend(list(generator * unknown - unknown * product_generator))
    coefficient_matrix, _ = sp.linear_eq_to_matrix(equations, variables)
    hom_dimension = len(variables) - coefficient_matrix.rank()
    _require(hom_dimension == 1, "Hom_SO3(V1 tensor V2,V1) multiplicity changed")

    axis_vector = sp.Matrix([0, 0, 1])
    axis_tensor = basis[4]
    _require(axis_tensor * axis_vector == axis_vector, "axisymmetric normalization changed")
    return {
        "V1_basis": ["e_x", "e_y", "e_z"],
        "V2_STF_basis": [_matrix_strings(value) for value in basis],
        "V1_generators": [_matrix_strings(value) for value in generators],
        "V2_generators": [_matrix_strings(value) for value in v2_generators],
        "intertwiner": "B(x,Y)=Y*x",
        "intertwiner_matrix": _matrix_strings(canonical),
        "equivariance_defect": "0",
        "intertwiner_linear_system_rank": coefficient_matrix.rank(),
        "intertwiner_unknown_count": len(variables),
        "Hom_SO3_dimension": hom_dimension,
        "Clebsch_Gordan_check": "V_1 tensor V_2 = V_1 direct-sum V_2 direct-sum V_3",
        "axisymmetric_normalization": "x=e_z and Y=diag(-1/2,-1/2,1)*y give B(x,Y)=y*e_z",
    }


def _incidence_certificate() -> dict[str, Any]:
    y0, y1, y2, y3, y4 = sp.symbols("y0:5")
    tensor = sp.Matrix(
        [
            [y0 - y4 / 2, y1, y2],
            [y1, -y0 - y4 / 2, y3],
            [y2, y3, y4],
        ]
    )
    x0, x1, x2 = sp.symbols("x0:3")
    vector = sp.Matrix([x0, x1, x2])
    equations = tensor * vector
    rank_three = sp.diag(1, 1, -2)
    rank_two = sp.diag(1, -1, 0)
    isotropic = sp.Matrix([1, sp.I, 0])
    rank_one = isotropic * isotropic.T
    _require(sp.trace(tensor) == 0 and tensor == tensor.T, "generic tensor left STF space")
    _require(rank_three.det() != 0, "rank-three witness degenerated")
    _require(rank_two.rank() == 2 and sp.trace(rank_two) == 0, "rank-two witness changed")
    _require(rank_one.rank() == 1 and sp.trace(rank_one) == 0, "rank-one witness changed")
    return {
        "generic_STF_tensor": _matrix_strings(tensor),
        "one_vector_kernel_equations": [str(sp.factor(value)) for value in equations],
        "two_vector_common_zero": "Y*conj(x_ax)=0 and Y*conj(x_pol)=0",
        "necessary_and_sufficient_locked_carrier_incidence": "conj(x_ax),conj(x_pol) belong to ker(Y)",
        "rank_strata": [
            {
                "rank_Y": 3,
                "condition": "det(Y) != 0",
                "fibre": "x_ax=x_pol=0",
                "witness_Y": _matrix_strings(rank_three),
            },
            {
                "rank_Y": 2,
                "condition": "det(Y)=0 and at least one 2x2 minor is nonzero",
                "fibre": "conj(x_ax),conj(x_pol) lie in the one-complex-dimensional ker(Y)",
                "witness_Y": _matrix_strings(rank_two),
            },
            {
                "rank_Y": 1,
                "condition": "all 2x2 minors vanish and Y != 0; over C, Y=c*v*v^T with v^T*v=0",
                "fibre": "conj(x_ax),conj(x_pol) lie in the two-complex-dimensional ker(Y)",
                "witness_Y": _matrix_strings(rank_one),
            },
            {
                "rank_Y": 0,
                "condition": "Y=0",
                "fibre": "x_ax and x_pol arbitrary",
                "witness_Y": _matrix_strings(sp.zeros(3)),
            },
        ],
        "real_coefficient_slice": "a nonzero real symmetric traceless Y has rank two or three; complex rank-one strata are allowed for positive-frequency amplitudes",
    }


def build_certificate() -> dict[str, Any]:
    locked = _load(INPUT)
    _require(
        _sha256(INPUT) == "28d59ff4ff14eeed10ef03b7cf10faed14ab815a7a72f3f265d0ce65870d42dc",
        "locked-resonance input hash changed",
    )
    _require(
        locked["classification"]["two_nonzero_locked_adjoint_functionals_certified"],
        "locked coefficient theorem changed",
    )
    _require(
        not locked["classification"]["all_m_tensor_assembled"],
        "upstream certificate already claims all-m completion",
    )
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "schema": "einstein-maxwell-weyl-exceptional-arbitrary-k-all-m-incidence-v1",
        "result_id": "EINSTEIN_MAXWELL_WEYL_EXCEPTIONAL_ARBITRARY_K_ALL_M_INCIDENCE_V1",
        "result_state": "LOCKED_EXCEPTIONAL_GENERIC_ALL_M_DIFFERENCE_FUNCTIONAL_AND_INCIDENCE_CERTIFIED",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G3_LOCKED_EXCEPTIONAL_ELL1_K_BY_GENERIC_ELL2_2K_ALL_M",
        "scope": {
            "theory": "Weyl-Maxwell target",
            "background": "compact magnetically supported Plebanski-Hacyan product",
            "boundaries": "one fixed closed S1_L times S2 before final residual quotient",
            "charge_sector": "fixed N=2 magnetic bundle",
            "carrier": "exceptional axial and polar ell=1 extra amplitudes at k crossed with the unique contributing transported polar-extra e2 ell=2 STF amplitude at 2k",
            "degree": 2,
            "parity": "both exceptional parities; all eight exceptional/generic branch-parity columns tested",
            "ell": "1 x 2 -> L=1 difference block",
            "m": "all m through the exact Cartesian V1 and STF V2 carriers",
            "k": "every allowed k=2*pi*n/L paired with the distinct 2k fibre on the same circumference",
            "omega": "omega_e(k), 2*omega_e(k), and difference output omega_e(k)",
        },
        "representation_theorem": _representation_certificate(),
        "all_m_functionals": {
            "variables": {
                "x_ax": "complex V1 exceptional-axial positive-frequency coefficient vector at k",
                "x_pol": "complex V1 exceptional-polar positive-frequency coefficient vector at k",
                "Y": "complex STF V2 coefficient tensor of the transported ell2 polar-extra e2 primary at 2k",
            },
            "axial_output": "R_ax(k)=-(768/5)*Y*conj(x_ax)",
            "polar_output": "R_pol(k)=-(864/5)*Y*conj(x_pol)",
            "six_other_branch_parity_functionals": "0",
            "normalization_source": "the axisymmetric direct four-dimensional coefficient matrix in the imported locked-resonance theorem",
            "necessity": "each displayed V1 output coefficient must vanish for a bounded finite-quasiperiodic correction",
        },
        "incidence_theorem": _incidence_certificate(),
        "coverage_ledger": {
            "locked_k_by_2k_all_m_difference_block": "CERTIFIED",
            "locked_two_fibre_difference_common_zero": "CERTIFIED",
            "five_stabilizer_moment_maps_on_locked_carrier": "OPEN",
            "exceptional_self_doubling_and_positive_positive_rows": "CERTIFIED upstream only at k=0; arbitrary-k simultaneous join OPEN",
            "homogeneous_a_d_columns": "arbitrary-k OPEN",
            "twist_position_and_velocity_columns": "arbitrary-k OPEN",
            "electric_and_Wilson_columns": "CERTIFIED upstream",
            "other_generic_branches_and_output_collisions": "OPEN",
            "multiple_abs_momentum_union": "OPEN",
        },
        "classification": {
            "locked_input_imported_by_exact_hash": True,
            "Hom_SO3_V1_tensor_V2_to_V1_dimension_one_certified": True,
            "all_m_locked_difference_tensor_assembled": True,
            "six_axisymmetric_zero_columns_promoted_to_all_m_zero_maps": True,
            "two_nonzero_axisymmetric_columns_promoted_with_exact_normalization": True,
            "locked_two_fibre_difference_incidence_classified": True,
            "enlarged_bounded_common_zero_with_moment_maps_classified": False,
            "all_exceptional_cross_columns_computed": False,
            "multiple_abs_momentum_full_cone_classified": False,
            "causal_all_orders_residual_observer_particle_quantum_claim": False,
        },
        "provenance": {
            "producer_path": str(Path(__file__).relative_to(ROOT)),
            "producer_sha256": _sha256(Path(__file__)),
            "schema_path": str(SCHEMA.relative_to(ROOT)),
            "schema_sha256": _sha256(SCHEMA),
            "inputs": {
                "locked_resonance": {
                    "path": str(INPUT.relative_to(ROOT)),
                    "result_id": locked["result_id"],
                    "sha256": _sha256(INPUT),
                }
            },
        },
        "verification_commands": [
            "PYTHONPATH=. python3 -m bridge.einstein_sector.einstein_maxwell_weyl_exceptional_arbitrary_k_all_m_incidence --check",
            "PYTHONPATH=. python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_exceptional_arbitrary_k_all_m_incidence.py",
            "PYTHONPATH=. python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_exceptional_arbitrary_k_all_m_incidence -v",
        ],
        "next_gate": "compute the arbitrary-k homogeneous a/d and twist columns, then intersect this kernel-incidence variety with every colliding resonance row and all five stabilizer moment maps",
        "claim_boundary": "This theorem exactly classifies the all-m locked k-by-2k difference functional and its zero set on the sharply declared two-fibre carrier. It is not the complete exceptional bounded cone: arbitrary-k homogeneous/twist columns, exceptional self rows, other wave collisions, the five-moment-map intersection and larger multiple-|k| unions remain open. It makes no infinite-harmonic, causal, all-orders, residual, observer, particle, positivity or quantum claim.",
    }


def _render(value: dict[str, Any]) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def build_atlas(certificate: dict[str, Any]) -> dict[str, Any]:
    evidence = {
        "path": str(OUTPUT.relative_to(ROOT)),
        "result_id": certificate["result_id"],
        "sha256": hashlib.sha256(_render(certificate).encode()).hexdigest(),
    }
    return {
        "schema": "pure-weyl-residual-atlas-fragment-v1",
        "schema_version": "1.0.0",
        "team": "einstein_boundary",
        "generated_by": str(Path(__file__).relative_to(ROOT)),
        "generated_by_sha256": _sha256(Path(__file__)),
        "status_vocabulary": ["CERTIFIED", "OBSTRUCTED", "OPEN", "NOT_APPLICABLE", "NO_CERTIFIED_MAP"],
        "description_axes": ["causal", "symplectic", "nonlinear", "observational", "quantum"],
        "entries": [
            {
                "id": "einstein.ph.wm.interaction.exceptional_arbitrary_k_all_m_locked_incidence",
                "scope": certificate["scope"],
                "descriptions": {
                    "causal": "NO_CERTIFIED_MAP",
                    "symplectic": "CERTIFIED",
                    "nonlinear": "OPEN",
                    "observational": "NO_CERTIFIED_MAP",
                    "quantum": "NO_CERTIFIED_MAP",
                },
                "mode_data": {
                    "dispersion": {
                        "status": "CERTIFIED",
                        "statement": "The locked same-background k-by-2k shell identity is imported by exact hash.",
                    },
                    "lee_wald": {
                        "status": "CERTIFIED",
                        "statement": "The nonradical input blocks and adjoint output projection are imported from the locked theorem.",
                    },
                    "taub_maps": {
                        "status": "OPEN",
                        "statement": "The five stabilizer maps have not yet been intersected with this all-m incidence variety.",
                    },
                    "resonance": {
                        "status": "CERTIFIED",
                        "statement": "The two all-m rows are exact multiples of Y*conj(x); the other six branch-parity maps vanish.",
                    },
                    "second_order": {
                        "equation": "L_barPhi v = -(1/2) D^2 E_barPhi[u,u]",
                        "bounded_or_finite_quasiperiodic": {
                            "status": "OPEN",
                            "statement": "This difference-row zero set is classified exactly, but the enlarged carrier has additional open rows and moment maps.",
                        },
                        "smooth_secular": {
                            "status": "CERTIFIED",
                            "statement": "The imported finite-harmonic smooth-secular theorem applies after stabilizer moments vanish.",
                        },
                        "causal_retarded": {
                            "status": "NO_CERTIFIED_MAP",
                            "statement": "No causal/retarded compact-product correction complex is certified.",
                        },
                    },
                },
                "evidence": [evidence],
                "claim_boundary": certificate["claim_boundary"],
            }
        ],
        "verification_commands": [
            "PYTHONPATH=. python3 -m bridge.einstein_sector.einstein_maxwell_weyl_exceptional_arbitrary_k_all_m_incidence --check",
            "python3 residual_atlas/validate_fragment.py residual_atlas/einstein-exceptional-arbitrary-k-all-m-incidence-fragment.json",
            "PYTHONPATH=. python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_exceptional_arbitrary_k_all_m_incidence.py",
        ],
    }


def verify_output() -> None:
    certificate = build_certificate()
    atlas = build_atlas(certificate)
    schema = _load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(certificate)
    _require(OUTPUT.read_text(encoding="utf-8") == _render(certificate), "certificate is stale")
    _require(ATLAS.read_text(encoding="utf-8") == _render(atlas), "atlas fragment is stale")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    if arguments.check:
        verify_output()
        print("EINSTEIN_MAXWELL_WEYL_EXCEPTIONAL_ARBITRARY_K_ALL_M_INCIDENCE_V1: PASS")
    else:
        certificate = build_certificate()
        OUTPUT.write_text(_render(certificate), encoding="utf-8")
        ATLAS.write_text(_render(build_atlas(certificate)), encoding="utf-8")
        print(f"wrote {OUTPUT.relative_to(ROOT)}")
        print(f"wrote {ATLAS.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
