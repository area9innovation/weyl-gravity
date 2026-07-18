#!/usr/bin/env python3
"""Certify the parity-even third-curvature Weyl carrier manifest.

This receipt imports the five pure-gravity conformal carriers of covariant
perturbation theory and independently replays their S3 label modules and the
single four-dimensional nonlocal identity.  It does not compute any of the
repository one-loop form-factor functions.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import itertools
import json
from pathlib import Path
from typing import Any, Iterable

from jsonschema import Draft202012Validator


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUTPUT = HERE / "certificates/FOUR_DIMENSIONAL_THIRD_CURVATURE_WEYL_CARRIER_MANIFEST.json"
SCHEMA = HERE / "schema/four-dimensional-third-curvature-weyl-carrier-manifest-v1.schema.json"
DEPENDENCIES = {
    "algebraic_C3": HERE / "certificates/FOUR_DIMENSIONAL_ALGEBRAIC_CUBIC_WEYL_CARRIERS.json",
    "covariant_C2_log": HERE / "certificates/CURVATURE_SQUARED_COVARIANT_LOG_GAMMA1.json",
    "FV_conformized_C2_log": HERE / "certificates/FV_CONFORMIZED_C2_LOG_GAMMA1.json",
    "FV_Ricci_sector": HERE / "certificates/FV_ANOMALY_ACTION_RICCI_SECTOR.json",
}

Permutation = tuple[int, int, int]
S3: tuple[Permutation, ...] = tuple(itertools.permutations(range(3)))
IDENTITY: Permutation = (0, 1, 2)


def _compose(left: Permutation, right: Permutation) -> Permutation:
    return tuple(left[right[index]] for index in range(3))  # type: ignore[return-value]


def _cycle_type(value: Permutation) -> str:
    fixed = sum(value[index] == index for index in range(3))
    if fixed == 3:
        return "identity"
    if fixed == 1:
        return "transposition"
    return "three_cycle"


def _cosets(subgroup: Iterable[Permutation]) -> tuple[tuple[Permutation, ...], ...]:
    subgroup = tuple(subgroup)
    unseen = set(S3)
    result = []
    while unseen:
        representative = min(unseen)
        coset = tuple(sorted(_compose(representative, item) for item in subgroup))
        result.append(coset)
        unseen.difference_update(coset)
    return tuple(sorted(result))


def _action_matrix(
    group_element: Permutation,
    cosets: tuple[tuple[Permutation, ...], ...],
) -> list[list[int]]:
    result = [[0 for _ in cosets] for _ in cosets]
    lookup = {frozenset(coset): index for index, coset in enumerate(cosets)}
    for source, coset in enumerate(cosets):
        image = frozenset(_compose(group_element, item) for item in coset)
        result[lookup[image]][source] = 1
    return result


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
    return rank


def _q(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def _matrix_q(matrix: list[list[Fraction]]) -> list[list[dict[str, int]]]:
    return [[_q(entry) for entry in row] for row in matrix]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _reference(path: Path) -> dict[str, str]:
    payload = json.loads(path.read_text())
    return {
        "path": str(path.relative_to(ROOT)),
        "result_id": str(payload["result_id"]),
        "sha256": _sha256(path),
    }


def _subgroups() -> dict[str, tuple[Permutation, ...]]:
    return {
        "S3": S3,
        "S2_23": (IDENTITY, (0, 2, 1)),
        "S2_12": (IDENTITY, (1, 0, 2)),
        "C3": (IDENTITY, (1, 2, 0), (2, 0, 1)),
    }


def _carrier_rows() -> list[dict[str, Any]]:
    return [
        {
            "carrier_id": "I10",
            "source_structure": 10,
            "formula": "K1_mu^alpha K2_alpha^beta K3_beta^mu",
            "explicit_derivative_order": 0,
            "stabilizer": "S3",
            "source_symmetry_equation": "CPT-IV (2.55)",
            "coefficient_status": "NOT_COMPUTED",
        },
        {
            "carrier_id": "I24",
            "source_structure": 24,
            "formula": "K1_munu nabla^mu K2_alphabeta nabla^nu K3^alphabeta",
            "explicit_derivative_order": 2,
            "stabilizer": "S2_23",
            "source_symmetry_equation": "CPT-IV (2.69)",
            "coefficient_status": "NOT_COMPUTED",
        },
        {
            "carrier_id": "I25",
            "source_structure": 25,
            "formula": "K1_munu nabla_alpha K2_beta^mu nabla^beta K3^alpha_nu",
            "explicit_derivative_order": 2,
            "stabilizer": "S2_23",
            "source_symmetry_equation": "CPT-IV (2.70)",
            "coefficient_status": "NOT_COMPUTED",
        },
        {
            "carrier_id": "I28",
            "source_structure": 28,
            "formula": "nabla_mu K1_alphalambda nabla_nu K2_beta^lambda nabla^alpha nabla^beta K3^munu",
            "explicit_derivative_order": 4,
            "stabilizer": "S2_12",
            "source_symmetry_equation": "CPT-IV (2.73)",
            "coefficient_status": "NOT_COMPUTED",
        },
        {
            "carrier_id": "I29",
            "source_structure": 29,
            "formula": "nabla_lambda nabla_sigma K1_alphabeta nabla^alpha nabla^beta K2_munu nabla^mu nabla^nu K3^lambdasigma",
            "explicit_derivative_order": 6,
            "stabilizer": "C3",
            "source_symmetry_equation": "CPT-IV (2.74)",
            "coefficient_status": "NOT_COMPUTED",
        },
    ]


def _permutation_modules(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, int]]:
    subgroups = _subgroups()
    modules = []
    raw_character = {name: 0 for name in ("identity", "transposition", "three_cycle")}
    representatives = {
        name: next(item for item in S3 if _cycle_type(item) == name)
        for name in raw_character
    }
    for row in rows:
        cosets = _cosets(subgroups[row["stabilizer"]])
        matrices = {
            name: _action_matrix(element, cosets)
            for name, element in representatives.items()
        }
        character = {
            name: sum(matrix[index][index] for index in range(len(matrix)))
            for name, matrix in matrices.items()
        }
        for name, value in character.items():
            raw_character[name] += value
        dimension = len(cosets)
        projector = [
            [Fraction(1, dimension) for _ in range(dimension)]
            for _ in range(dimension)
        ]
        modules.append(
            {
                "carrier_id": row["carrier_id"],
                "stabilizer": row["stabilizer"],
                "stabilizer_order": len(subgroups[row["stabilizer"]]),
                "generic_label_orbit_dimension": dimension,
                "cosets": [[[entry + 1 for entry in permutation] for permutation in coset] for coset in cosets],
                "character_by_cycle_type": character,
                "trivial_projector": _matrix_q(projector),
                "trivial_projector_rank": _rank(projector),
            }
        )
    return modules, raw_character


def _multiplicities(character: dict[str, int]) -> dict[str, int]:
    irreducibles = {
        "trivial": {"identity": 1, "transposition": 1, "three_cycle": 1},
        "sign": {"identity": 1, "transposition": -1, "three_cycle": 1},
        "standard": {"identity": 2, "transposition": 0, "three_cycle": -1},
    }
    class_sizes = {"identity": 1, "transposition": 3, "three_cycle": 2}
    result = {}
    for name, irrep in irreducibles.items():
        numerator = sum(
            class_sizes[cycle] * character[cycle] * irrep[cycle]
            for cycle in class_sizes
        )
        if numerator % 6:
            raise ValueError("nonintegral S3 multiplicity")
        result[name] = numerator // 6
    return result


def _four_dimensional_relation() -> dict[str, Any]:
    # Polynomials are keyed by exponent triples of (Box1, Box2, Box3).
    coefficients = {
        "I10": {
            "2,0,0": _q(Fraction(-1, 12)),
            "0,2,0": _q(Fraction(-1, 12)),
            "0,0,2": _q(Fraction(-1, 12)),
            "1,1,0": _q(Fraction(1, 6)),
            "1,0,1": _q(Fraction(1, 6)),
            "0,1,1": _q(Fraction(1, 6)),
        },
        "I24": {"1,0,0": _q(Fraction(-1, 2))},
        "I25": {
            "1,0,0": _q(Fraction(1, 2)),
            "0,1,0": _q(Fraction(-1, 2)),
            "0,0,1": _q(Fraction(-1, 2)),
        },
        "I28": {"0,0,0": _q(1)},
    }
    return {
        "source": "CPT-IV Appendix equation (A.35), restricted to the pure-K scalar-flat conformal sector",
        "form_factor_symmetry": "COMPLETELY_S3_SYMMETRIC_ARBITRARY_FUNCTION",
        "coefficient_polynomials": coefficients,
        "absent_carrier": "I29",
        "elimination_choice": "REMOVE_TRIVIAL_S3_COMPONENT_OF_I28",
        "relation_rank": 1,
        "scope": "integrated modulo total derivatives and O(curvature^4), with labelled Box_i and the declared inverse domain",
    }


def build() -> dict[str, Any]:
    dependencies = {
        name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()
    }
    algebraic = dependencies["algebraic_C3"]
    ricci = dependencies["FV_Ricci_sector"]
    if (
        algebraic["decision"]["zero_derivative_algebraic_C3_carriers"]
        != "CERTIFIED_COMPLETE"
        or algebraic["tensor_carriers"]["parity_dimensions"]
        != {"even": 1, "odd": 1}
        or ricci["decision"]["independent_nonlocal_R2_form_factor"]
        != "NOT_AN_INDEPENDENT_DATUM_IN_DECLARED_FV_CONFORMAL_DECOMPOSITION"
    ):
        raise ValueError("third-curvature manifest dependency drifted")

    rows = _carrier_rows()
    modules, raw_character = _permutation_modules(rows)
    raw_multiplicities = _multiplicities(raw_character)
    raw_dimension = sum(row["generic_label_orbit_dimension"] for row in modules)
    if raw_dimension != 12 or raw_multiplicities != {"trivial": 5, "sign": 1, "standard": 3}:
        raise ValueError("raw third-curvature S3 module drifted")
    quotient_character = dict(raw_character)
    for cycle in quotient_character:
        quotient_character[cycle] -= 1
    quotient_multiplicities = _multiplicities(quotient_character)
    if quotient_multiplicities != {"trivial": 4, "sign": 1, "standard": 3}:
        raise ValueError("four-dimensional third-curvature quotient drifted")

    source_rows = {
        "K_definition": "K_munu=(2/Box) nabla^beta nabla^alpha C_alpha_mu_beta_nu",
        "K_properties": ["K_mu^mu=0", "nabla^mu K_munu=O(curvature^2)"],
        "carrier_equation": "Conformal Decomposition (33)",
        "symmetry_equations": ["CPT-IV (2.55)", "CPT-IV (2.69)", "CPT-IV (2.70)", "CPT-IV (2.73)", "CPT-IV (2.74)"],
        "four_dimensional_identity": "CPT-IV (A.35)",
    }
    source_digest = hashlib.sha256(
        json.dumps(
            {"source_rows": source_rows, "carriers": rows},
            sort_keys=True,
            separators=(",", ":"),
        ).encode()
    ).hexdigest()

    result = {
        "schema": "quantum-weyl-four-dimensional-third-curvature-weyl-carrier-manifest-v1",
        "result_id": "FOUR_DIMENSIONAL_THIRD_CURVATURE_WEYL_CARRIER_MANIFEST",
        "result_state": "PARITY_EVEN_THIRD_CURVATURE_WEYL_CARRIER_MANIFEST_COMPLETE_COEFFICIENT_FUNCTIONS_OPEN",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["EUCLIDEAN-SPECTRAL"],
        "classical_commit": algebraic["classical_commit"],
        "scope": {
            "dimension": 4,
            "signature": "EUCLIDEAN",
            "curvature_order": 3,
            "parity": "EVEN_ONLY",
            "background": "noncompact asymptotically flat scalar-flat conformal representative",
            "boundary_policy": "surface terms vanish",
            "inverse_policy": "Box inverse and every labelled form factor act on a declared kernel-free source complement",
            "order_policy": "commutators of Box_i with derivatives are O(curvature^4) and are excluded at the certified order",
        },
        "derived_tensor": {
            "symbol": "K_munu",
            "definition": source_rows["K_definition"],
            "properties": source_rows["K_properties"],
            "collision_warning": "K_munu is the nonlocal transverse-tracefree Ricci/Weyl contraction used by the source; it is not the four-index Weyl tensor C_munurhosigma",
        },
        "carrier_manifest": rows,
        "permutation_modules": modules,
        "raw_module": {
            "carrier_labeled_function_count": 5,
            "generic_label_orbit_dimension": raw_dimension,
            "character_by_cycle_type": raw_character,
            "irreducible_multiplicities": raw_multiplicities,
        },
        "four_dimensional_identity": _four_dimensional_relation(),
        "quotient_module": {
            "generic_label_orbit_dimension": raw_dimension - 1,
            "character_by_cycle_type": quotient_character,
            "irreducible_multiplicities": quotient_multiplicities,
            "carrier_labeled_description": "five carrier-labeled functions with one arbitrary completely symmetric functional relation; choose a section by deleting the trivial S3 component of I28",
        },
        "algebraic_anchor": {
            "carrier_id": "I29",
            "status": "INEXCLUDABLE_SIX_DERIVATIVE_ROW_WITH_LOCAL_C3_LINEAGE",
            "source_statement": "CPT-IV after (A.35) identifies I29 as absent from the 4D constraint and as the row whose local version is the unique algebraic C3 contraction",
            "normalization_to_C3_EVEN": "NOT_COMPUTED",
            "odd_anchor": "NOT_CLASSIFIED_IN_THIS_PARITY_EVEN_MANIFEST",
        },
        "coefficient_gate": {
            "repository_factor_functions": {
                row["carrier_id"]: "NOT_COMPUTED" for row in rows
            },
            "finite_C2_normalization": "NOT_FIXED",
            "absolute_dressed_Rhat2_normalization": "NOT_FIXED",
            "complete_Gamma1": "NO_CERTIFIED_FUNCTIONAL",
            "complete_Q1": "NO_CERTIFIED_OPERATOR",
            "residual_transfer": "FORBIDDEN",
            "minimal_missing_input": "the five carrier-labeled repository form-factor functions modulo the exact S3 stabilizers and the single 4D symmetric relation",
        },
        "source_provenance": {
            "formula_digest": source_digest,
            "sources": [
                {
                    "arxiv": "0911.1168",
                    "title": "Covariant Perturbation Theory (IV). Third Order in the Curvature",
                    "equations": ["(2.55)", "(2.69)", "(2.70)", "(2.73)", "(2.74)", "(A.35)"],
                    "role": "complete third-curvature basis symmetries and the four-dimensional nonlocal identity",
                },
                {
                    "arxiv": "gr-qc/9510037",
                    "title": "Conformal Decomposition of the Effective Action and Covariant Curvature Expansion",
                    "equations": ["(29)", "(33)", "(41)"],
                    "role": "five pure-gravity conformal carriers in the K_munu basis",
                },
                {
                    "arxiv": "hep-th/9510205",
                    "title": "Partial Summation of the Nonlocal Expansion for the Gravitational Effective Action in 4 Dimensions",
                    "equations": ["(9)", "(12)", "(24)", "(30)"],
                    "role": "Weyl-sector sufficiency and Ricci-scalar dependence in the declared conformal decomposition",
                },
            ],
        },
        "dependencies": {name: _reference(path) for name, path in DEPENDENCIES.items()},
        "claim_flags": {
            "PARITY_EVEN_THIRD_CURVATURE_CARRIER_MANIFEST_COMPLETE": True,
            "FIVE_SOURCE_CARRIERS_IMPORTED": True,
            "PERMUTATION_MODULE_QUOTIENT_REPLAYED": True,
            "FOUR_DIMENSIONAL_FUNCTIONAL_IDENTITY_REPLAYED": True,
            "PARITY_ODD_DERIVATIVE_CARRIER_MANIFEST_COMPLETE": False,
            "REPOSITORY_CUBIC_FORM_FACTOR_FUNCTIONS_COMPUTED": False,
            "REPOSITORY_CUBIC_COEFFICIENTS_COMPUTED": False,
            "COMPLETE_RENORMALIZED_GAMMA1_SUPPLIED": False,
            "COMPLETE_RENORMALIZED_Q1_SUPPLIED": False,
            "RESIDUAL_TRANSFER_AUTHORIZED": False,
            "LORENTZIAN_CERTIFIED": False,
        },
        "next_gate": "REPOSITORY_PARITY_EVEN_THIRD_CURVATURE_FACTOR_FORM_FUNCTIONS_AND_COEFFICIENTS",
        "claim_boundary": (
            "This EUCLIDEAN-SPECTRAL receipt imports the complete parity-even pure-gravity third-curvature conformal carrier list of covariant perturbation theory on the declared four-dimensional noncompact asymptotically flat scalar-flat representative. It distinguishes the source's nonlocal symmetric tensor K_munu=(2/Box)nabla nabla C from the four-index Weyl tensor. The five carrier labels are I10, I24, I25, I28 and I29, with exact S3, S2_23, S2_23, S2_12 and C3 stabilizers. Their generic labelled permutation modules have dimensions 1,3,3,3,2 and total dimension twelve. The four-dimensional integrated identity with arbitrary completely symmetric form factor removes one trivial S3 component, chosen here as the symmetric part of I28, leaving eleven generic labelled channels with irreducible multiplicities four trivial, one sign and three standard. I29 is absent from that identity and anchors the unique local algebraic even C3 lineage, but its normalization is not inferred. This is a source-derived carrier and permutation-quotient certificate, not a computation of the five repository form-factor functions or their coefficients. It does not classify the parity-odd derivative-decorated sector, fix finite C2 or absolute dressed Rhat2 normalizations, supply complete Gamma1 or Q1, define global inverse or kernel data, construct renormalized products, authorize residual transfer, or establish a Lorentzian QME, Hadamard state, positivity, particle, scattering, or unitarity theorem."
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
        value["raw_module"]["generic_label_orbit_dimension"] != 12
        or value["quotient_module"]["generic_label_orbit_dimension"] != 11
        or value["four_dimensional_identity"]["relation_rank"] != 1
        or flags["PARITY_EVEN_THIRD_CURVATURE_CARRIER_MANIFEST_COMPLETE"] is not True
        or any(
            flags[name] is not False
            for name in (
                "PARITY_ODD_DERIVATIVE_CARRIER_MANIFEST_COMPLETE",
                "REPOSITORY_CUBIC_FORM_FACTOR_FUNCTIONS_COMPUTED",
                "REPOSITORY_CUBIC_COEFFICIENTS_COMPUTED",
                "COMPLETE_RENORMALIZED_GAMMA1_SUPPLIED",
                "COMPLETE_RENORMALIZED_Q1_SUPPLIED",
                "RESIDUAL_TRANSFER_AUTHORIZED",
                "LORENTZIAN_CERTIFIED",
            )
        )
    ):
        raise ValueError("third-curvature Weyl manifest crossed its claim boundary")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = json.dumps(build(), indent=2, sort_keys=True) + "\n"
    if args.emit:
        OUTPUT.write_text(rendered)
    if args.check and (not OUTPUT.exists() or OUTPUT.read_text() != rendered):
        raise SystemExit(f"stale third-curvature Weyl manifest: {OUTPUT}")
    print("THIRD-CURVATURE WEYL MANIFEST: 5 EVEN CARRIERS; 12 -> 11 LABEL CHANNELS; COEFFICIENTS OPEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
