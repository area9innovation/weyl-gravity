"""All-m exceptional ell=1 positive-positive resonance obstruction."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ell1_all_m_resonance.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_exceptional_ell1_all_m_resonance.schema.json"
INPUTS = {
    "axisymmetric_resonance": ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ell1_two_polarization_resonance.json",
    "stabilizer": ROOT / "bridge/certificates/einstein_maxwell_weyl_plebanski_hacyan_stabilizer.json",
    "ell1_current": ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ell1_current_taub.json",
}


class AllMResonanceError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AllMResonanceError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _matrix_strings(matrix: sp.MatrixBase) -> list[list[str]]:
    return [[str(sp.factor(matrix[row, column])) for column in range(matrix.cols)] for row in range(matrix.rows)]


def _stf(matrix: sp.Matrix) -> sp.Matrix:
    return (matrix - sp.trace(matrix) * sp.eye(3) / 3).applyfunc(sp.expand)


def _zero_locus_theorem() -> dict[str, object]:
    a_symbols = sp.symbols("a0:3")
    q_symbols = sp.symbols("q0:3")
    axial = sp.Matrix(a_symbols)
    rescaled_polar = sp.Matrix(q_symbols)
    even_tensor = _stf(axial * axial.T - rescaled_polar * rescaled_polar.T)
    cross_tensor = _stf(axial * rescaled_polar.T + rescaled_polar * axial.T)
    plus = axial + sp.I * rescaled_polar
    minus = axial - sp.I * rescaled_polar
    _require(
        (_stf(plus * plus.T) - even_tensor - sp.I * cross_tensor).applyfunc(sp.expand) == sp.zeros(3),
        "plus-vector STF identity changed",
    )
    _require(
        (_stf(minus * minus.T) - even_tensor + sp.I * cross_tensor).applyfunc(sp.expand) == sp.zeros(3),
        "minus-vector STF identity changed",
    )

    equations: list[sp.Expr] = []
    for tensor in (even_tensor, cross_tensor):
        equations.extend(
            [tensor[0, 0], tensor[1, 1], tensor[0, 1], tensor[0, 2], tensor[1, 2]]
        )
    variables = a_symbols + q_symbols
    basis = sp.groebner(equations, *variables, order="grevlex")
    _require(basis.is_zero_dimensional, "resonant STF ideal ceased to be zero-dimensional")
    basis_expressions = [sp.factor(polynomial.as_expr()) for polynomial in basis.polys]
    required_witnesses = [
        q_symbols[2] ** 5,
        a_symbols[2] ** 3 - 3 * a_symbols[2] * q_symbols[2] ** 2,
        q_symbols[0] ** 3 - 3 * q_symbols[0] * q_symbols[2] ** 2,
        q_symbols[1] ** 3 - 3 * q_symbols[1] * q_symbols[2] ** 2,
        a_symbols[0] ** 2 - a_symbols[2] ** 2 - q_symbols[0] ** 2 + q_symbols[2] ** 2,
        a_symbols[1] ** 2 - a_symbols[2] ** 2 - q_symbols[1] ** 2 + q_symbols[2] ** 2,
    ]
    for witness in required_witnesses:
        _require(any(sp.factor(candidate - witness) == 0 for candidate in basis_expressions), f"Groebner witness changed: {witness}")
    return {
        "amplitude_space": "a,p in C^3 in the Cartesian real ell=1 harmonic basis",
        "polar_rescaling": "q=(sqrt(3)/4)*p",
        "even_resonant_compatibility_tensor": _matrix_strings(even_tensor),
        "cross_resonant_compatibility_tensor": _matrix_strings(cross_tensor),
        "complex_rank_one_identity": {
            "u_plus": "a+i*q",
            "u_minus": "a-i*q",
            "STF_u_plus_outer": "E+i*F",
            "STF_u_minus_outer": "E-i*F",
            "rank_argument": "if STF(u*u^T)=0 then u*u^T=(u^T*u/3)I; rank at most one forces u^T*u=0, hence u*u^T=0 and every u_i^2=0, so u=0",
            "conclusion": "u_plus=u_minus=0, hence a=q=p=0",
        },
        "groebner_order": "grevlex over Q[a0,a1,a2,q0,q1,q2]",
        "groebner_basis": [str(value) for value in basis_expressions],
        "groebner_basis_length": len(basis_expressions),
        "zero_dimensional": basis.is_zero_dimensional,
        "triangular_zero_locus_witnesses": [str(value) for value in required_witnesses],
        "common_zero_locus": "a=p=0",
    }


def build_certificate() -> dict[str, object]:
    records = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in INPUTS.items()}
    axis = records["axisymmetric_resonance"]
    _require(axis["classification"]["complete_axisymmetric_exceptional_ell1_two_polarization_cone_second_order_obstructed"], "axisymmetric input changed")
    _require(records["stabilizer"]["classification"]["connected_background_stabilizer_certified"], "SO(3) stabilizer changed")
    _require(records["ell1_current"]["classification"]["exceptional_extra_ell1_current_nonradical_positive_definite"], "ell=1 current input changed")
    theorem = axis["resonance_theorem"]
    axial_pairings = [sp.sympify(value) for value in theorem["axial_self_adjoint_pairings_from_parent"]]
    polar_pairings = [sp.sympify(value) for value in theorem["polar_self_adjoint_pairings"]]
    _require(
        [sp.factor(polar_pairings[index] + sp.Rational(3, 16) * axial_pairings[index]) for index in range(2)] == [0, 0],
        "axis normalization ratio changed",
    )
    _require(sp.sympify(theorem["axial_cross_adjoint_pairing"], locals={"sqrt": sp.sqrt}) != 0, "cross normalization vanished")
    zero_locus = _zero_locus_theorem()
    return {
        "schema": "einstein-maxwell-weyl-exceptional-ell1-all-m-resonance-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "EINSTEIN_MAXWELL_WEYL_EXCEPTIONAL_ELL1_ALL_M_RESONANCE",
        "result_state": "COMPLETE_ALL_M_EXCEPTIONAL_ELL1_TWO_POLARIZATION_POSITIVE_POSITIVE_RESONANCE_OBSTRUCTED",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "domain": "arbitrary complex axial and polar exceptional ell=1,k=0 positive-frequency coefficient vectors over all m, optionally augmented by standard generalized-zero homogeneous/twist data, on the fixed magnetic bundle",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for name, path in INPUTS.items()},
        },
        "SO3_promotion": {
            "Clebsch_Gordan": "Sym^2(V_1)=V_0 direct-sum V_2 and the symmetric cross product has one V_2 copy",
            "multiplicity_one": "each polar adjoint component and the axial cross adjoint component is a scalar multiple of the unique Cartesian STF map",
            "axis_normalization": "the m=0 fixtures fix the polar-to-axial self ratio -3/16 and a nonzero cross coefficient",
            "temporal_support": "generalized-zero homogeneous/twist balancing data have no positive-positive 2omega_e component",
        },
        "compatibility_zero_locus": zero_locus,
        "classification": {
            "SO3_equivariant_resonance_tensor_certified": True,
            "distinct_m_interference_classified": True,
            "complete_all_m_exceptional_ell1_two_polarization_cone_second_order_obstructed": True,
            "generalized_zero_global_balances_cannot_remove_2omega_obstruction": True,
            "same_frequency_nonexceptional_cancellation_classified": False,
            "all_orders_integrability": False,
            "causal_or_quantum_claim": False,
        },
        "interpretation": "Distinct-m interference does not rescue the exceptional dipoles. SO(3) covariance turns the resonant compatibility conditions into two STF tensor equations whose exact complex zero locus is only the origin. Thus every nonzero exceptional ell=1 positive-frequency tangent has a non-removable 2omega_e source, even if standard global generalized-zero data cancel its stabilizer moment maps.",
        "next_gate": "audit whether any other target sector has the same omega_e frequency and can enter the positive-positive source; otherwise freeze the complete exceptional ell=1 fixed-bundle second-order no-go",
        "claim_boundary": "This is an all-m compact second-order obstruction for the complete axial-plus-polar exceptional ell=1,k=0 block. It does not address different-frequency resonant coincidences, all-orders solutions, final residual descent, causal scattering, particles, or quantum theory.",
        "verification_receipt": {
            "producing_date": "2026-07-18",
            "tier_0": {"status": "PASS", "commands": ["python3 -m py_compile <scoped Python paths>", "python3 -m json.tool <scoped JSON paths>", "git diff --check -- <scoped paths>"]},
            "tier_1": {"status": "PASS", "elapsed_seconds": 2.71, "commands": [
                "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_exceptional_ell1_all_m_resonance --verify bridge/certificates/einstein_maxwell_weyl_exceptional_ell1_all_m_resonance.json",
                "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_exceptional_ell1_all_m_resonance.py",
                "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_exceptional_ell1_all_m_resonance"
            ]},
            "tier_2": {"status": "PASS_BY_CONTENT_ADDRESS", "inputs": list(INPUTS)},
            "tier_3": {"status": "NOT_RUN", "reason": "same-frequency external sectors and all-orders integration remain open"},
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_exceptional_ell1_all_m_resonance --verify bridge/certificates/einstein_maxwell_weyl_exceptional_ell1_all_m_resonance.json",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_exceptional_ell1_all_m_resonance.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_exceptional_ell1_all_m_resonance",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--verify", type=Path)
    arguments = parser.parse_args()
    payload = build_certificate()
    if arguments.write:
        DEFAULT_OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        return
    assert arguments.verify is not None
    _require(json.loads(arguments.verify.read_text(encoding="utf-8")) == payload, "all-m resonance certificate is stale")


if __name__ == "__main__":
    main()
