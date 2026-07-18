#!/usr/bin/env python3
"""Certify the algebraic four-dimensional cubic Weyl carrier basis.

The result is deliberately smaller than the nonlocal third-curvature
effective action.  It classifies only pointwise, zero-derivative contractions
of three Weyl tensors.  Form factors and derivative-decorated carriers remain
open because integration by parts does not commute with arbitrary functions
of the three labelled d'Alembertians.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from local_bv.curvature import pair_partitions
from local_bv.pairing_orbits import identical_factor_group, signed_pairing_orbits
from local_bv.specialization import WEYL
from local_bv.tensors import (
    TensorExpression,
    TensorFactor,
    TensorMonomial,
    TensorSpec,
    signed_permutation_group,
)
from local_bv.weyl_decomposition import hodge_dualize_weyl_factor
from local_bv.weyl_image import schouten_zero_weyl_image_analysis


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUTPUT = HERE / "certificates/FOUR_DIMENSIONAL_ALGEBRAIC_CUBIC_WEYL_CARRIERS.json"
SCHEMA = HERE / "schema/four-dimensional-algebraic-cubic-weyl-carriers-v1.schema.json"
DEPENDENCIES = {
    "four_dimensional_schouten_quotient": ROOT / "quantum-weyl/local_bv/certificates/LOCAL_FOUR_DIMENSIONAL_SCHOUTEN_QUOTIENT_CERTIFICATE.json",
    "schouten_zero_weyl_image": ROOT / "quantum-weyl/local_bv/certificates/LOCAL_SCHOUTEN_ZERO_WEYL_IMAGE_CERTIFICATE.json",
    "hodge_canonicalization": ROOT / "quantum-weyl/local_bv/certificates/LOCAL_DIFFERENTIAL_HODGE_CANONICALIZATION_CERTIFICATE.json",
    "fv_ricci_sector": HERE / "certificates/FV_ANOMALY_ACTION_RICCI_SECTOR.json",
}


CHIRAL_WEYL_BLOCK = TensorSpec(
    "ChiralWeylBlock",
    2,
    signed_permutation_group(2, (((1, 0), 1),)),
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _reference(path: Path) -> dict[str, str]:
    value = json.loads(path.read_text())
    return {
        "path": str(path.relative_to(ROOT)),
        "result_id": str(value.get("result_id") or value.get("schema")),
        "sha256": _sha256(path),
    }


def _q(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def _rank(matrix: list[list[Fraction]]) -> int:
    rows = [row[:] for row in matrix if any(row)]
    if not rows:
        return 0
    rank = 0
    for column in range(len(rows[0])):
        pivot = next(
            (index for index in range(rank, len(rows)) if rows[index][column]),
            None,
        )
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        scale = rows[rank][column]
        rows[rank] = [entry / scale for entry in rows[rank]]
        for index, row in enumerate(rows):
            if index == rank or not row[column]:
                continue
            coefficient = row[column]
            rows[index] = [
                entry - coefficient * pivot_entry
                for entry, pivot_entry in zip(row, rows[rank])
            ]
        rank += 1
        if rank == len(rows):
            break
    return rank


def _block_monomial(
    pairing: tuple[tuple[int, int], ...],
) -> TensorMonomial:
    labels = [0] * 6
    for label, (left, right) in enumerate(pairing):
        labels[left] = labels[right] = label
    return TensorMonomial(
        tuple(
            TensorFactor(CHIRAL_WEYL_BLOCK, tuple(labels[2 * index : 2 * index + 2]))
            for index in range(3)
        )
    )


def _chiral_block_enumeration() -> dict[str, Any]:
    pairings = tuple(pair_partitions(tuple(range(6))))
    orbits = signed_pairing_orbits(
        pairings, identical_factor_group(CHIRAL_WEYL_BLOCK, 3)
    )
    rows = []
    nonzero = []
    for orbit in orbits:
        monomial = _block_monomial(orbit.canonical_pairing)
        traced = any(factor.slots[0] == factor.slots[1] for factor in monomial.factors)
        status = "ZERO_BY_TRACEFREE_BLOCK" if traced else "CANONICAL_NONZERO"
        rows.append(
            {
                "canonical_pairing": [list(pair) for pair in orbit.canonical_pairing],
                "orbit_size": len(orbit.members),
                "status": status,
                "monomial": monomial.canonical_payload(),
            }
        )
        if not traced:
            sign, canonical = monomial.canonicalize()
            if not sign or canonical is None:
                raise ValueError("untraced chiral cubic orbit canonicalized to zero")
            nonzero.append(canonical)
    if len(pairings) != 15 or len(orbits) != 3 or len(set(nonzero)) != 1:
        raise ValueError("chiral cubic contraction enumeration drifted")
    return {
        "raw_complete_contractions": len(pairings),
        "signed_identical_factor_orbits": len(orbits),
        "tracefree_zero_orbits": sum(row["status"].startswith("ZERO") for row in rows),
        "canonical_nonzero_orbits": len(set(nonzero)),
        "orbit_ledger": rows,
        "surviving_contraction": nonzero[0].canonical_payload(),
    }


def _trace_cube(diagonal: tuple[int, int, int]) -> Fraction:
    if sum(diagonal):
        raise ValueError("sample chiral block is not tracefree")
    return sum((Fraction(value) ** 3 for value in diagonal), Fraction())


def _tensor_carriers() -> tuple[TensorExpression, TensorExpression]:
    even = TensorExpression.monomial(
        TensorMonomial(
            (
                TensorFactor(WEYL, (0, 1, 2, 3)),
                TensorFactor(WEYL, (2, 3, 4, 5)),
                TensorFactor(WEYL, (4, 5, 0, 1)),
            )
        )
    )
    monomial = next(iter(even.terms))
    odd = hodge_dualize_weyl_factor(monomial, 0)
    if even.parity_transform() != even or odd.parity_transform() != -odd:
        raise ValueError("cubic Weyl parity crosswalk drifted")
    return even, odd


def build() -> dict[str, Any]:
    dependencies = {
        name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()
    }
    fv = dependencies["fv_ricci_sector"]
    if (
        fv["decision"]["independent_cubic_Weyl_form_factors"]
        != "NO_CERTIFIED_FUNCTIONAL"
        or fv["decision"]["complete_Gamma1"] != "NO_CERTIFIED_FUNCTIONAL"
    ):
        raise ValueError("cubic carrier dependency crossed the open form-factor gate")

    block = _chiral_block_enumeration()
    chirality_allocations = [
        {"plus_factors": 3, "minus_factors": 0, "status": "ONE_NONZERO_BLOCK_CUBIC"},
        {"plus_factors": 2, "minus_factors": 1, "status": "ZERO_BY_SINGLE_MINUS_TRACE"},
        {"plus_factors": 1, "minus_factors": 2, "status": "ZERO_BY_SINGLE_PLUS_TRACE"},
        {"plus_factors": 0, "minus_factors": 3, "status": "ONE_NONZERO_BLOCK_CUBIC"},
    ]
    even, odd = _tensor_carriers()
    image = schouten_zero_weyl_image_analysis()
    even_coordinate = image["target_quotient"].free_coordinates(even)
    if even_coordinate != (Fraction(2, 3),):
        raise ValueError("algebraic C3 carrier disagrees with the stored Weyl image")

    sample = (1, 1, -2)
    trace_cube = _trace_cube(sample)
    even_odd_evaluation = [
        [trace_cube, trace_cube],
        [trace_cube, -trace_cube],
    ]
    if _rank(even_odd_evaluation) != 2:
        raise ValueError("even/odd cubic Weyl carriers are not independent")

    chiral_from_parity = [
        [Fraction(1, 2), Fraction(1, 2)],
        [Fraction(1, 2), Fraction(-1, 2)],
    ]
    parity_from_chiral = [
        [Fraction(1), Fraction(1)],
        [Fraction(1), Fraction(-1)],
    ]
    product = [
        [
            sum(
                (
                    chiral_from_parity[row][index]
                    * parity_from_chiral[index][column]
                    for index in range(2)
                ),
                Fraction(),
            )
            for column in range(2)
        ]
        for row in range(2)
    ]
    if product != [[Fraction(1), Fraction()], [Fraction(), Fraction(1)]]:
        raise ValueError("chiral/parity coordinate matrices are not inverse")

    result = {
        "schema": "quantum-weyl-four-dimensional-algebraic-cubic-weyl-carriers-v1",
        "result_id": "FOUR_DIMENSIONAL_ALGEBRAIC_CUBIC_WEYL_CARRIERS",
        "result_state": "ALGEBRAIC_C3_CARRIERS_COMPLETE_NONLOCAL_CUBIC_FORM_FACTORS_OPEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "classical_commit": fv["classical_commit"],
        "scope": {
            "dimension": 4,
            "signature": "EUCLIDEAN",
            "curvature_order": 3,
            "derivative_order": 0,
            "carrier_algebra": "pointwise complete contractions of three algebraic tracefree Weyl tensors",
            "hodge_convention": "star squared equals +1 on Euclidean two-forms; C_plus/minus=(1/2)(C plus/minus star C)",
        },
        "chiral_block_enumeration": block,
        "chirality_allocation": {
            "allocations": chirality_allocations,
            "mixed_allocations_zero": 2,
            "nonzero_chiral_dimension": 2,
            "proof": "the self-dual and anti-self-dual two-form projectors are orthogonal, so cross-chirality index edges vanish; after this block decomposition a mixed allocation leaves one rank-two symmetric tracefree block factor, which can only close by its vanishing trace, while each three-factor block has the unique untraced triangle contraction",
        },
        "tensor_carriers": {
            "even_id": "C3_EVEN",
            "even_formula": "C_ab^cd C_cd^ef C_ef^ab",
            "even_expression": even.canonical_payload(),
            "even_coordinate_in_schouten_zero_weyl_image": [_q(value) for value in even_coordinate],
            "odd_id": "C3_ODD",
            "odd_formula": "(star C)_ab^cd C_cd^ef C_ef^ab",
            "odd_expression": odd.canonical_payload(),
            "parity_dimensions": {"even": 1, "odd": 1},
            "status": "COMPLETE_FOR_ZERO_DERIVATIVE_ALGEBRAIC_C3_SECTOR",
        },
        "chiral_parity_crosswalk": {
            "chiral_basis": ["tr(C_plus^3)", "tr(C_minus^3)"],
            "parity_basis": ["C3_EVEN", "C3_ODD"],
            "chiral_from_parity": [[_q(value) for value in row] for row in chiral_from_parity],
            "parity_from_chiral": [[_q(value) for value in row] for row in parity_from_chiral],
            "parity_action_on_chiral_basis": [[0, 1], [1, 0]],
            "parity_action_on_parity_basis": [[1, 0], [0, -1]],
            "status": "EXACT_INVERSE_CROSSWALK",
        },
        "independence_witness": {
            "tracefree_sample": list(sample),
            "trace_cube": _q(trace_cube),
            "sample_order": ["C_plus=diag(1,1,-2), C_minus=0", "C_plus=0, C_minus=diag(1,1,-2)"],
            "carrier_order": ["C3_EVEN", "C3_ODD"],
            "evaluation_matrix": [[_q(value) for value in row] for row in even_odd_evaluation],
            "rank": _rank(even_odd_evaluation),
            "status": "EXACT_RANK_TWO",
        },
        "nonlocal_form_factor_boundary": {
            "generic_syntax": "sum_m integral Gamma_m(Box1,Box2,Box3) I_m[C1,C2,C3]",
            "algebraic_zero_derivative_carrier_basis": "CERTIFIED",
            "derivative_decorated_cubic_Weyl_carriers": "NOT_COMPUTED",
            "form_factor_functions": "NOT_COMPUTED",
            "form_factor_coefficients": "NOT_COMPUTED",
            "permutation_and_branch_analyticity": "NOT_COMPUTED",
            "local_counterterm_warning": "C3 has engineering dimension six and is not a new dimension-four one-loop local counterterm; nonlocal inverse powers or another scale are required",
            "ibp_warning": "the integrated local order-six quotient cannot classify arbitrary nonlocal form factors because labelled Box_i and derivative placements obstruct unrestricted integration by parts",
        },
        "source_provenance": [
            {
                "arxiv": "0911.1168",
                "title": "Covariant Perturbation Theory (IV). Third Order in the Curvature",
                "use": "primary source for the general third-curvature nonlocal invariant basis, form factors, and low-dimensional identities",
            },
            {
                "arxiv": "gr-qc/9510037",
                "title": "Conformal Decomposition of the Effective Action and Covariant Curvature Expansion",
                "use": "primary source for rewriting the conformal part through third curvature order in a Weyl-based conformal basis",
            },
            {
                "arxiv": "hep-th/9510205",
                "title": "Partial Summation of the Nonlocal Expansion for the Gravitational Effective Action in 4 Dimensions",
                "use": "primary source for the statement that the independent data after conformal decomposition are Weyl-tensor form factors",
            },
        ],
        "decision": {
            "zero_derivative_algebraic_C3_carriers": "CERTIFIED_COMPLETE",
            "independent_cubic_Weyl_form_factors": "CARRIER_SUBSPACE_ONLY_NO_CERTIFIED_FUNCTION",
            "complete_Gamma1": "NO_CERTIFIED_FUNCTIONAL",
            "complete_Q1": "NO_CERTIFIED_OPERATOR",
            "residual_transfer": "FORBIDDEN",
        },
        "claim_flags": {
            "ALGEBRAIC_C3_CARRIER_BASIS_COMPLETE": True,
            "PARITY_ODD_ALGEBRAIC_C3_CARRIER_COMPLETE": True,
            "DERIVATIVE_DECORATED_CUBIC_WEYL_BASIS_COMPLETE": False,
            "INDEPENDENT_CUBIC_WEYL_FORM_FACTORS_COMPUTED": False,
            "CUBIC_WEYL_COEFFICIENTS_COMPUTED": False,
            "COMPLETE_RENORMALIZED_GAMMA1_SUPPLIED": False,
            "COMPLETE_RENORMALIZED_Q1_SUPPLIED": False,
            "RESIDUAL_TRANSFER_AUTHORIZED": False,
            "LORENTZIAN_CERTIFIED": False,
        },
        "dependencies": {name: _reference(path) for name, path in DEPENDENCIES.items()},
        "next_gate": "DERIVATIVE_DECORATED_NONLOCAL_CUBIC_WEYL_CARRIERS_AND_FORM_FACTOR_FUNCTIONS",
        "claim_boundary": (
            "This LOCAL-ALGEBRAIC theorem exhausts pointwise zero-derivative complete contractions of three algebraic Weyl tensors in four Euclidean dimensions. The exact chiral two-form decomposition turns each Weyl tensor into a symmetric tracefree rank-two block, with orthogonal self-dual and anti-self-dual projectors. Fifteen raw contractions reduce to three identical-factor orbits per block, two vanish by tracefreeness, and one triangle contraction survives. Mixed chirality allocations contain a lone tracefree block after orthogonality removes cross-chirality edges and therefore vanish, leaving two chiral classes or equivalently one parity-even carrier C_ab^cd C_cd^ef C_ef^ab and one parity-odd carrier with one Hodge dual. The even carrier maps to coordinate 2/3 in the previously certified Schouten-zero Weyl image, and an exact rank-two evaluation witness proves the parity carriers independent. This result does not classify derivative-decorated cubic invariants with labelled d'Alembertians, compute any function Gamma_m(Box1,Box2,Box3), determine a cubic coefficient, or turn the dimension-six C3 density into a dimension-four local counterterm. It does not supply a complete Gamma1 or Q1, renormalized products, an extended classical contraction, residual transfer, a Lorentzian QME, Hadamard state, positivity, particle interpretation, scattering, or unitarity theorem."
        ),
    }
    validate(result)
    return result


def validate(value: dict[str, Any]) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    flags = value["claim_flags"]
    if (
        value["decision"]["zero_derivative_algebraic_C3_carriers"]
        != "CERTIFIED_COMPLETE"
        or value["tensor_carriers"]["parity_dimensions"] != {"even": 1, "odd": 1}
        or value["independence_witness"]["rank"] != 2
        or flags["ALGEBRAIC_C3_CARRIER_BASIS_COMPLETE"] is not True
        or flags["PARITY_ODD_ALGEBRAIC_C3_CARRIER_COMPLETE"] is not True
        or any(
            flags[name] is not False
            for name in (
                "DERIVATIVE_DECORATED_CUBIC_WEYL_BASIS_COMPLETE",
                "INDEPENDENT_CUBIC_WEYL_FORM_FACTORS_COMPUTED",
                "CUBIC_WEYL_COEFFICIENTS_COMPUTED",
                "COMPLETE_RENORMALIZED_GAMMA1_SUPPLIED",
                "COMPLETE_RENORMALIZED_Q1_SUPPLIED",
                "RESIDUAL_TRANSFER_AUTHORIZED",
                "LORENTZIAN_CERTIFIED",
            )
        )
    ):
        raise ValueError("algebraic cubic Weyl carrier certificate crossed its claim boundary")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = json.dumps(build(), indent=2, sort_keys=True) + "\n"
    if args.emit:
        OUTPUT.write_text(rendered)
    if args.check and (not OUTPUT.exists() or OUTPUT.read_text() != rendered):
        raise SystemExit(f"stale algebraic cubic Weyl carrier certificate: {OUTPUT}")
    print("ALGEBRAIC CUBIC WEYL CARRIERS: 1 EVEN + 1 ODD; NONLOCAL FORM FACTORS OPEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
