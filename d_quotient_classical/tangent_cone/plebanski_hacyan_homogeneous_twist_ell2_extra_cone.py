#!/usr/bin/env python3
"""Classify the declared homogeneous/twist times ell=2 extra common-zero cone."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp
from sympy.physics.wigner import clebsch_gordan


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "d_quotient_classical/certificates/PH_HOMOGENEOUS_TWIST_ELL2_EXTRA_BOUNDED_TANGENT_CONE_V1.json"
SCHEMA = ROOT / "d_quotient_classical/schema/ph-homogeneous-twist-ell2-extra-bounded-tangent-cone-v1.schema.json"
INPUTS = {
    "resonance": ROOT / "bridge/certificates/einstein_maxwell_weyl_homogeneous_twist_ell2_extra_resonance_matrix.json",
    "abd": ROOT / "bridge/certificates/einstein_maxwell_weyl_abd_ell2_extra_resonance_matrix.json",
    "moment_maps": ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_global_moment_maps.json",
    "axial_pairing": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_extra_green_pairing.json",
    "polar_pairing": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_lee_wald_gate.json",
    "abstract_cone": ROOT / "d_quotient_classical/certificates/FINITE_HARMONIC_SECOND_ORDER_TANGENT_CONE_THEOREM_V1.json",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _parse(value: str, t: sp.Symbol) -> sp.Expr:
    return sp.sympify(value, locals={"t": t, "I": sp.I, "sqrt": sp.sqrt})


def _angular_map(q: int) -> sp.Matrix:
    modes = list(range(-2, 3))
    fixture = clebsch_gordan(1, 2, 2, 1, 0, 1)
    return sp.Matrix(
        5,
        5,
        lambda row, column: sp.simplify(clebsch_gordan(1, 2, 2, q, modes[column], modes[row]) / fixture)
        if modes[column] + q == modes[row]
        else 0,
    )


def exact_classification() -> dict[str, Any]:
    records = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in INPUTS.items()}
    resonance = records["resonance"]
    abd = records["abd"]
    moment_maps = records["moment_maps"]
    if not resonance["classification"]["complete_homogeneous_twist_bounded_resonance_matrix"]:
        raise AssertionError("complete resonance matrix changed")
    if moment_maps["axial_twist"]["mu_H"] != "2*|B|^2":
        raise AssertionError("twist energy normalization changed")
    if moment_maps["homogeneous_ell0"]["mu_H"] != "-Q_e**2 - a**2 - b**2 + b*d":
        raise AssertionError("homogeneous moment map changed")
    if not resonance["complete_matrix_disposition"]["Q_e_column"].startswith("REMOVABLE"):
        raise AssertionError("electric-variation resonance disposition changed")

    lam, k, omega = sp.symbols("lambda k omega", real=True)
    substitutions = {lam: 6, k: 0, omega: 4 / sp.sqrt(3)}
    axial_gram = sp.Matrix([
        [sp.sympify(value.replace("lambda", "lam"), locals={"lam": lam, "k": k, "omega": omega}).subs(substitutions) for value in row]
        for row in records["axial_pairing"]["pairing"]["normalized_Gram"]
    ])
    polar_gram = sp.Matrix([
        [sp.sympify(value.replace("lambda", "lam"), locals={"lam": lam, "k": k, "omega_e": omega}).subs(substitutions) for value in row]
        for row in records["polar_pairing"]["shell_pairing"]["extra_Hermitian_current_Gram"]
    ])
    expected_axial = sp.diag(1296, sp.Rational(208, 3))
    expected_polar = sp.diag(22464, 12288)
    if sp.simplify(axial_gram - expected_axial) != sp.zeros(2) or sp.simplify(polar_gram - expected_polar) != sp.zeros(2):
        raise AssertionError("ell=2,k=0 extra occupation changed")

    t = sp.symbols("t", real=True)
    profiles = abd["projected_resonance_polynomials"]
    order = (("axial", 0), ("axial", 1), ("polar", 0), ("polar", 1))
    diagonal = {
        profile: sp.diag(*[_parse(profiles[parity][profile][branch], t) for parity, branch in order])
        for profile in ("a", "b", "d")
    }
    d_a = diagonal["a"].applyfunc(lambda value: sp.expand(value).coeff(t, 1))
    d_b2 = diagonal["b"].applyfunc(lambda value: sp.expand(value).coeff(t, 2))
    d_d = diagonal["d"]
    if sp.simplify(d_b2 - d_a / 2) != sp.zeros(4) or d_b2.det() == 0 or d_d.det() == 0:
        raise AssertionError("homogeneous polynomial leading matrices changed")

    theorem = resonance["twist_projection_theorem"]
    position = sp.Matrix([[_parse(value, t) for value in row] for row in theorem["position_matrix"]])
    velocity = sp.Matrix([[_parse(value, t) for value in row] for row in theorem["velocity_matrix"]])
    v0 = velocity.subs(t, 0)
    v1 = velocity.diff(t)
    if sp.simplify(v1 - position) != sp.zeros(4):
        raise AssertionError("velocity leading matrix no longer equals the position matrix")

    angular = {q: _angular_map(q) for q in (-1, 0, 1)}
    if angular[0][2, 2] != 0 or angular[1][3, 2] != 1:
        raise AssertionError("Clebsch--Gordan normalization changed")

    # Rotate every nonzero real twist velocity to B=e_z.  The overall norm is
    # restored in the final homogeneous parameterization.  The t^2 equation
    # first forces b=0.  For a != 0, each m block is a four-dimensional pencil.
    a = sp.symbols("a", real=True)
    pencil_data: dict[str, Any] = {}
    for mode in (-2, -1, 0, 1, 2):
        coefficient = angular[0][mode + 2, mode + 2]
        pencil = a * d_a + coefficient * position
        determinant = sp.factor(pencil.det())
        nonzero_roots = [root for root in sp.solve(determinant, a) if root != 0]
        uncancellable = []
        for root in nonzero_roots:
            kernel = pencil.subs(a, root).nullspace()
            if len(kernel) != 1:
                raise AssertionError("nonzero-a pencil kernel changed")
            vector = kernel[0]
            # Output row polar_w1 is identically zero in the position matrix.
            # The kernel has no polar_e1 component and a nonzero polar_e2
            # component, so the V0 term cannot be cancelled by A or d.
            witness = sp.simplify(coefficient * v0[2, 3] * vector[3])
            if witness == 0 or vector[2] != 0:
                raise AssertionError("nonzero-a exclusion witness changed")
            uncancellable.append(str(witness))
        pencil_data[str(mode)] = {
            "clebsch_gordan": str(coefficient),
            "determinant": str(determinant),
            "nonzero_candidate_roots": [str(root) for root in nonzero_roots],
            "constant_polar_w1_witnesses": uncancellable,
        }

    # With a=b=0, the t coefficient is (P tensor T_B)C=0.  Its exact
    # 12-column kernel carries the only remaining candidates.  Write
    # A=A_parallel e_z+A_perp e_x and reduce the constant coefficient.
    t_b = angular[0]
    leading = sp.kronecker_product(position, t_b)
    kernel_basis = sp.Matrix.hstack(*leading.nullspace())
    if leading.rank() != 8 or kernel_basis.shape != (20, 12):
        raise AssertionError("leading twist kernel changed")
    d, a_parallel, a_perp = sp.symbols("d a_parallel a_perp", real=True)
    t_a = a_parallel * angular[0] + a_perp * (angular[-1] - angular[1]) / sp.sqrt(2)
    constant = (
        d * sp.kronecker_product(d_d, sp.eye(5))
        + sp.kronecker_product(position, t_a)
        + sp.kronecker_product(v0, t_b)
    )
    reduced = sp.simplify(constant * kernel_basis)

    d_rows = (0, 1, 2, 3, 4, 7, 10, 11, 12, 13, 14, 17)
    d_minor = sp.factor(reduced[list(d_rows), :].det())
    expected_d_minor = sp.Rational(663364720915390660608, 625) * d**12
    if sp.simplify(d_minor - expected_d_minor) != 0:
        raise AssertionError("d-exclusion minor changed")

    offaxis_rows = (1, 5, 6, 8, 9, 11, 15, 16, 18, 19)
    offaxis_columns = (0, 1, 2, 3, 5, 6, 7, 8, 10, 11)
    offaxis_minor = sp.factor(reduced[list(offaxis_rows), list(offaxis_columns)].subs(d, 0).det())
    expected_offaxis = sp.Rational(44965136684798705664, 125) * sp.sqrt(3) * a_perp**2
    if sp.simplify(offaxis_minor - expected_offaxis) != 0:
        raise AssertionError("off-axis rank minor changed")

    aligned_rows = (5, 6, 8, 9, 15, 16, 18, 19)
    aligned_columns = (2, 3, 5, 6, 7, 8, 10, 11)
    aligned_minor = sp.factor(
        reduced[list(aligned_rows), list(aligned_columns)].subs({d: 0, a_perp: 0}).det()
    )
    expected_aligned = sp.Rational(7252694328213504, 625)
    if sp.simplify(aligned_minor - expected_aligned) != 0:
        raise AssertionError("aligned rank minor changed")

    offaxis_kernel = reduced.subs({d: 0, a_perp: 1}).nullspace()
    aligned_kernel = reduced.subs({d: 0, a_perp: 0}).nullspace()
    if len(offaxis_kernel) != 2 or len(aligned_kernel) != 4:
        raise AssertionError("rank-stratum nullities changed")
    full_offaxis_kernel = [sp.simplify(kernel_basis * vector) for vector in offaxis_kernel]
    for vector in full_offaxis_kernel:
        support = [index for index, value in enumerate(vector) if value != 0]
        if any(index % 5 != 2 for index in support):
            raise AssertionError("off-axis resonance kernel left m=0")
        internal = sp.Matrix([vector[5 * index + 2] for index in range(4)])
        if sp.simplify(position * internal) != sp.zeros(4, 1):
            raise AssertionError("off-axis internal vector left ker(P)")

    return {
        "coefficient_elimination": {
            "b": {
                "verdict": "b=0 for every nonzero extra amplitude",
                "reason": "the t^2 coefficient is b*D_b2*C and D_b2 is invertible",
                "det_D_b2": str(sp.factor(d_b2.det())),
            },
            "a": {
                "verdict": "a=0",
                "mode_pencils": pencil_data,
                "reason": "every nonzero-a pencil kernel has an uncancellable polar_w1 constant coefficient",
            },
            "d": {
                "verdict": "d=0",
                "normalized_B_axis_minor_rows_zero_based": list(d_rows),
                "minor": str(d_minor),
            },
        },
        "rank_stratification": {
            "leading_rank": leading.rank(),
            "leading_kernel_dimension": kernel_basis.shape[1],
            "off_axis": {
                "condition": "A_perp != 0 after B=e_z normalization",
                "reduced_rank": 10,
                "kernel_dimension": 2,
                "minor": str(offaxis_minor),
                "kernel_description": "C is m=0 about B and its internal multiplicity vector lies in ker(P)",
            },
            "aligned": {
                "condition": "A_perp=0",
                "reduced_rank": 8,
                "kernel_dimension": 4,
                "minor": str(aligned_minor),
                "kernel_description": "C is m=0 about B with an arbitrary four-component axial/polar multiplicity vector",
            },
        },
        "moment_map_descent": {
            "mu_Px": "0 identically at k=0",
            "mu_J": "the resonance kernel is m=0 and has zero extra angular expectation; mu_J=-4*A cross B therefore forces A_perp=0",
            "mu_H": "2*|B|^2-Q_e^2-(omega_e^2/4)*X=0 with omega_e^2=16/3",
        },
        "complete_nonzero_extra_parameterization": {
            "axis": "choose n in S^2",
            "extra": "choose nonzero x in C^4 on the ell=2,m=0 harmonic about n, with the negative-frequency conjugate fixed by reality",
            "occupation": "X=1296*|x_a1|^2+(208/3)*|x_a2|^2+22464*|x_p1|^2+12288*|x_p2|^2",
            "homogeneous": "a=b=d=0; c and W_x are arbitrary spectators; Q_e is arbitrary real electric variation",
            "twist": "A=alpha*n and B=beta*n with alpha real and beta nonzero",
            "energy_balance": "beta^2=Q_e^2/2+(2/3)*X",
            "orbit_statement": "every nonzero-extra common-zero solution in the declared carrier is an SO(3) rotation of this family",
        },
    }


def build() -> dict[str, Any]:
    result = exact_classification()
    sources = {str(path.relative_to(ROOT)): _sha256(path) for path in (*INPUTS.values(), Path(__file__).resolve(), SCHEMA)}
    return {
        "schema": "ph-homogeneous-twist-ell2-extra-bounded-tangent-cone-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA),
        "result_id": "PH_HOMOGENEOUS_TWIST_ELL2_EXTRA_BOUNDED_TANGENT_CONE_V1",
        "result_state": "COMPLETE_DECLARED_NONZERO_EXTRA_COMMON_ZERO_LOCUS_IS_ALIGNED_SO3_ORBIT",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "scope": {
            "theory": "Weyl-Maxwell",
            "background": "compact magnetically supported Plebanski-Hacyan product",
            "boundaries": "closed S1_L times S2; bounded or finite-quasiperiodic correction class",
            "charge_sector": "fixed N=2 magnetic bundle with real electric tangent Q_e allowed",
            "carrier": "one k=0 homogeneous/twist block crossed with one positive-frequency ell=2 extra-primary multiplet and its reality conjugate",
            "degree": 2,
            "parity": "all four axial/polar extra multiplicities",
            "ell": "(0 or 1) x 2 -> resonant L=2",
            "m": "all m modulo the exact SO(3) action",
            "k": 0,
            "omega": "generalized-zero global/twist data crossed with omega_e=4/sqrt(3)",
        },
        **result,
        "classification": {
            "complete_common_zero_locus_in_declared_nonzero_extra_carrier": True,
            "off_axis_branch_exists": False,
            "aligned_SO3_orbit_is_complete": True,
            "electric_variation_included": True,
            "bounded_second_order_right_inverse_constructed": False,
            "smooth_secular_right_inverse_constructed": False,
            "causal_retarded_right_inverse_constructed": False,
            "final_residual_or_quantum_claim": False,
        },
        "correction_class_gate": {
            "bounded_or_finite_quasiperiodic": "NECESSARY COMMON-ZERO LOCUS CERTIFIED; sufficiency is OPEN because the complete nonresonant q2 source and blockwise bounded right inverses are not exported",
            "smooth_secular": "OPEN: secular right inverses and admissible-growth bounds are not exported",
            "causal_retarded": "NO_CERTIFIED_MAP: no compact-product retarded BV complex is certified",
            "missing_for_next_gate": [
                "complete nonresonant q2 source on the aligned SO3 orbit",
                "content-addressed inverse or homotopy for every selected off-shell output block",
                "Noether/gauge compatibility of the assembled correction",
            ],
        },
        "interpretation": "The completed resonance matrix and all five stabilizer maps cut the declared nonzero-extra cone exactly to the aligned SO(3) orbit. There is no hidden off-axis branch. This is a necessary bounded tangent-cone theorem, not yet a second-order solution theorem.",
        "next_gate": "import the complete nonresonant q2 output and exact off-shell block inverses, then construct and verify the bounded second-order correction on the certified aligned orbit",
        "claim_boundary": "This LOCAL-ALGEBRAIC/REDUCED-MODE theorem classifies only the common zero locus in the declared single-k=0 homogeneous/twist times ell=2 extra carrier. It does not construct a second-order correction, cover opposite momenta or multiple fibres, activate either cyclic Bridge 2, descend to final cohomology, or establish causal, observational, particle or quantum claims.",
        "source_manifest": sources,
        "verification_receipt": {
            "producing_date": "2026-07-18",
            "tier_0": {"status": "PASS", "commands": ["python3 -m py_compile <scoped Python paths>", "python3 -m json.tool <certificate and schema>", "git diff --check -- <scoped paths>"]},
            "tier_1": {"status": "PASS", "commands": ["python3 -m d_quotient_classical.tangent_cone.plebanski_hacyan_homogeneous_twist_ell2_extra_cone --check", "python3 d_quotient_classical/tangent_cone/verify_plebanski_hacyan_homogeneous_twist_ell2_extra_cone.py", "python3 -m unittest d_quotient_classical.tangent_cone.tests.test_plebanski_hacyan_homogeneous_twist_ell2_extra_cone"]},
            "tier_2": {"status": "NOT_RUN", "reason": "all imported tensors are unchanged and content-addressed; this theorem is an exact elimination on their certified projections"},
            "tier_3": {"status": "NOT_RUN", "reason": "no lifecycle promotion beyond REDUCED-MODE CLASSIFIED and no second-order sufficiency claim"},
        },
        "verification_commands": [
            "python3 -m d_quotient_classical.tangent_cone.plebanski_hacyan_homogeneous_twist_ell2_extra_cone --check",
            "python3 d_quotient_classical/tangent_cone/verify_plebanski_hacyan_homogeneous_twist_ell2_extra_cone.py",
            "python3 -m unittest d_quotient_classical.tangent_cone.tests.test_plebanski_hacyan_homogeneous_twist_ell2_extra_cone",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    value = build()
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    if arguments.write:
        OUTPUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    elif json.loads(OUTPUT.read_text(encoding="utf-8")) != value:
        raise AssertionError("Plebanski-Hacyan tangent-cone certificate is stale")
    print("PH_HOMOGENEOUS_TWIST_ELL2_EXTRA_BOUNDED_TANGENT_CONE_V1: PASS")


if __name__ == "__main__":
    main()
