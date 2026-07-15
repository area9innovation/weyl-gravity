"""Reproduce the exact local-curvature specialization foundation receipt."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from .algebra import canonical_sha256
from .curvature import EPSILON, RIEMANN
from .hodge import Signature
from .six_derivative import six_derivative_curvature_analysis
from .specialization import (
    RelationFamily,
    SpecializationTower,
    TensorOccurrence,
    epsilon_pair_expansion,
    reduce_epsilon_pair_in_monomial,
    replace_riemann_by_weyl,
    schouten_antisymmetrization,
)
from .tensors import TensorExpression, TensorFactor, TensorMonomial, TensorSpec


PACKAGE_ROOT = Path(__file__).resolve().parent
QUANTUM_ROOT = PACKAGE_ROOT.parent
DETAILED_PATH = (
    PACKAGE_ROOT
    / "certificates"
    / "LOCAL_SPECIALIZATION_FOUNDATIONS_CERTIFICATE.json"
)
RESULT_PATH = QUANTUM_ROOT / "certificates" / "LOCAL_SPECIALIZATION_FOUNDATIONS.json"
SCHEMA_PATH = PACKAGE_ROOT / "schema" / "specialization_certificate.schema.json"


def _source_manifest() -> dict[str, str]:
    paths = (
        "__init__.py",
        "curvature.py",
        "hodge.py",
        "quotient.py",
        "six_derivative.py",
        "specialization.py",
        "specialization_certificate.py",
        "tensors.py",
        "schema/specialization_certificate.schema.json",
        "tests/test_specialization.py",
        "tests/test_specialization_certificate.py",
    )
    return {
        path: hashlib.sha256((PACKAGE_ROOT / path).read_bytes()).hexdigest()
        for path in paths
    }


def _universal_tower() -> SpecializationTower:
    analysis = six_derivative_curvature_analysis()
    provenance = {
        "R3_bianchi": "generated algebraic Bianchi action on all cubic pairing orbits",
        "nablaR_nablaR_bianchi": "generated algebraic and differential Bianchi action on the once-differentiated sector",
        "R_nabla2R_bianchi": "generated algebraic and outer-differential Bianchi action on the second-derivative bridge",
        "integration_by_parts": "generated covariant total divergences",
        "covariant_commutators": "generated declared-sign contracted derivative commutators",
    }
    families = tuple(
        RelationFamily(name, tuple(relations), provenance[name])
        for name, relations in analysis["relation_sets"].items()
    )
    tower = SpecializationTower.start(
        "dimension_independent_integrated",
        analysis["quotient"].basis,
        families,
    )
    if tower.current.dimension != 10:
        raise AssertionError("universal six-derivative specialization import drifted")
    return tower


def _controlled_projection_tower() -> SpecializationTower:
    even = [TensorSpec.without_slot_symmetry(f"projection_even_{index}", 0) for index in range(3)]
    odd = TensorSpec.without_slot_symmetry(
        "projection_odd", 0, spacetime_parity=1
    )
    basis = tuple(
        TensorMonomial((TensorFactor(spec, ()),)) for spec in (*even, odd)
    )
    first = RelationFamily(
        "controlled_universal_relation",
        (TensorExpression({basis[0]: 1, basis[1]: -1}),),
        "controlled algebraic witness; not a geometric identity",
    )
    second = RelationFamily(
        "controlled_dimension_relation",
        (TensorExpression({basis[1]: 1, basis[2]: -1}),),
        "controlled specialization witness; not a Schouten identity",
        ("infrastructure test only",),
    )
    tower = SpecializationTower.start("controlled_raw", basis)
    tower = tower.extend("controlled_universal", (first,))
    return tower.extend("controlled_specialized", (second,))


def build_certificate() -> dict[str, Any]:
    universal = _universal_tower()
    controlled = _controlled_projection_tower()
    if [stage.dimension for stage in controlled.stages] != [4, 3, 2]:
        raise AssertionError("controlled specialization dimensions drifted")
    if [len(stage.projection_kernel) for stage in controlled.stages[1:]] != [1, 1]:
        raise AssertionError("controlled projection kernels drifted")

    quotient = universal.current.quotient
    representatives = {
        f"universal_free_{position:02d}": TensorExpression.monomial(
            quotient.basis[column]
        )
        for position, column in enumerate(quotient.free_columns)
    }
    representative_ledger = universal.current.representative_ledger(representatives)

    generic = TensorSpec.without_slot_symmetry("schouten_rank_5_witness", 5)
    generic_monomial = TensorMonomial(
        (TensorFactor(generic, (0, 1, 2, 3, 4)),)
    )
    occurrences = tuple(
        TensorOccurrence(0, "slots", position) for position in range(5)
    )
    antisymmetrization = schouten_antisymmetrization(
        generic_monomial, occurrences, dimension=4
    )
    if len(antisymmetrization.terms) != 120:
        raise AssertionError("five-index antisymmetrization is not exhaustive")

    traced = TensorExpression.monomial(
        TensorMonomial((TensorFactor(RIEMANN, (0, 1, 0, 1)),))
    )
    untraced = TensorExpression.monomial(
        TensorMonomial((TensorFactor(RIEMANN, (0, 1, 2, 3)),))
    )
    traced_weyl = replace_riemann_by_weyl(traced)
    untraced_weyl = replace_riemann_by_weyl(untraced)
    if traced_weyl or not untraced_weyl:
        raise AssertionError("tracefree Weyl reduction witness failed")

    epsilon_square = TensorExpression.monomial(
        TensorMonomial(
            (
                TensorFactor(EPSILON, (0, 1, 2, 3)),
                TensorFactor(EPSILON, (0, 1, 2, 3)),
            )
        )
    )
    epsilon_monomial = next(iter(epsilon_square.terms))
    epsilon_contractions = {
        signature.value: reduce_epsilon_pair_in_monomial(
            epsilon_monomial, 0, 1, signature
        ).canonical_payload()
        for signature in (Signature.EUCLIDEAN, Signature.LORENTZIAN)
    }
    scalar = TensorMonomial(())
    contraction_values = {
        signature.value: int(
            reduce_epsilon_pair_in_monomial(
                epsilon_monomial, 0, 1, signature
            ).terms[scalar]
        )
        for signature in (Signature.EUCLIDEAN, Signature.LORENTZIAN)
    }
    if contraction_values != {"EUCLIDEAN": 24, "LORENTZIAN": -24}:
        raise AssertionError("epsilon-pair contraction normalization drifted")

    source_manifest = _source_manifest()
    return {
        "result_id": "LOCAL_SPECIALIZATION_FOUNDATIONS_CERTIFICATE",
        "result_state": "SPECIALIZATION_INFRASTRUCTURE_VERIFIED",
        "classical_commit": "UNFROZEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "scope": (
            "Exact staged quotient projections, kernels, relation provenance, "
            "named coordinates, dimension-checked antisymmetrization, tracefree "
            "Weyl reduction, and signature-aware epsilon-pair elimination."
        ),
        "checks": {
            "exact_nullspace": "VERIFIED",
            "immutable_specialization_tower": "VERIFIED",
            "projection_surjectivity": "VERIFIED",
            "projection_rank_nullity": "VERIFIED",
            "relation_family_provenance": "VERIFIED",
            "parity_block_preservation": "VERIFIED",
            "named_representative_coordinates": "VERIFIED",
            "five_index_antisymmetrization_primitive": "VERIFIED",
            "tracefree_weyl_reduction": "VERIFIED",
            "epsilon_pair_elimination": "VERIFIED",
            "signature_separation": "VERIFIED",
            "four_dimensional_schouten_quotient": "NOT_COMPUTED",
            "four_dimensional_weyl_invariant_basis": "NOT_COMPUTED",
            "local_cohomology_H_s_mod_d": "NOT_COMPUTED",
        },
        "universal_import": {
            "ambient_dimension": len(universal.ambient_basis),
            "quotient_dimension": universal.current.dimension,
            "parity_block_dimensions": universal.current.parity_block_dimensions,
            "family_names": [
                family.name for family in universal.current.families
            ],
            "tower": universal.canonical_payload(),
            "named_representatives": representative_ledger,
        },
        "controlled_projection_witness": {
            "role": "INFRASTRUCTURE_ONLY_NOT_GEOMETRIC_INPUT",
            "stage_dimensions": [stage.dimension for stage in controlled.stages],
            "tower": controlled.canonical_payload(),
        },
        "schouten_primitive": {
            "dimension": 4,
            "antisymmetrized_occurrence_count": 5,
            "generated_permutation_count": 120,
            "relation_term_count_after_canonicalization": len(
                antisymmetrization.terms
            ),
            "relation_sha256": antisymmetrization.canonical_hash(),
        },
        "tracefree_weyl": {
            "traced_riemann_input_sha256": traced.canonical_hash(),
            "traced_weyl_status": "ZERO",
            "untraced_weyl_status": "NONZERO",
            "untraced_weyl_sha256": untraced_weyl.canonical_hash(),
        },
        "epsilon_reduction": {
            "matching_count": 24,
            "euclidean_matching_sha256": canonical_sha256(
                [
                    term.canonical_payload()
                    for term in epsilon_pair_expansion(Signature.EUCLIDEAN)
                ]
            ),
            "lorentzian_matching_sha256": canonical_sha256(
                [
                    term.canonical_payload()
                    for term in epsilon_pair_expansion(Signature.LORENTZIAN)
                ]
            ),
            "complete_contraction_values": contraction_values,
            "complete_contraction_payloads": epsilon_contractions,
        },
        "canonical_hashes": {
            "universal_tower_sha256": universal.canonical_payload()[
                "tower_sha256"
            ],
            "controlled_tower_sha256": controlled.canonical_payload()[
                "tower_sha256"
            ],
            "source_manifest_sha256": canonical_sha256(source_manifest),
        },
        "not_computed": [
            "generated four-dimensional Schouten relation family on the order-six curvature basis",
            "four-dimensional quotient ranks and named conventional invariant basis",
            "parity-odd Weyl invariant enumeration",
            "Weyl BRST closure, antifield descent, and H^{g,4}(s|d)",
        ],
        "assumptions": [
            "The specialization tower keeps one canonical ambient monomial basis and only appends named relation families.",
            "The controlled projection witness tests infrastructure and is never included in a geometric quotient.",
            "The epsilon convention is epsilon_abcd epsilon^{efgh}=sigma delta_abcd^{efgh}, with sigma fixed by signature.",
            "The tracefree Weyl replacement is a tensor specialization primitive, not yet the full map from Riemann invariant coordinates to Weyl invariant coordinates.",
        ],
    }


def build_result_envelope() -> dict[str, Any]:
    return {
        "result_id": "LOCAL_SPECIALIZATION_FOUNDATIONS",
        "classical_commit": "UNFROZEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "lifecycle_status": "CLASSIFIED",
        "ghost_number": 0,
        "form_degree": 0,
        "antifield_number": 0,
        "parity": "mixed",
        "representative": "exact staged local-curvature specialization infrastructure",
        "cohomology_status": "NOT_COMPUTED",
        "descent_status": "NOT_COMPUTED",
        "coefficient_status": "NOT_COMPUTED",
        "residual_projection_status": "NOT_COMPUTED",
        "proof_certificate": (
            "quantum-weyl/local_bv/certificates/"
            "LOCAL_SPECIALIZATION_FOUNDATIONS_CERTIFICATE.json"
        ),
        "assumptions": [
            "No four-dimensional Schouten relation has yet been applied to the universal curvature quotient."
        ],
        "notes": (
            "LOCAL-ALGEBRAIC infrastructure only. Exact specialization maps, "
            "kernels, parity blocks, tracefree-Weyl reduction, and epsilon-pair "
            "elimination are verified; the 4D invariant and BRST quotients remain NOT_COMPUTED."
        ),
    }


def _render(value: dict[str, Any]) -> str:
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    detailed = _render(build_certificate())
    result = _render(build_result_envelope())
    if args.emit:
        DETAILED_PATH.parent.mkdir(parents=True, exist_ok=True)
        RESULT_PATH.parent.mkdir(parents=True, exist_ok=True)
        DETAILED_PATH.write_text(detailed, encoding="utf-8")
        RESULT_PATH.write_text(result, encoding="utf-8")
    if args.check:
        if DETAILED_PATH.read_text(encoding="utf-8") != detailed:
            raise SystemExit("detailed specialization foundation certificate is stale")
        if RESULT_PATH.read_text(encoding="utf-8") != result:
            raise SystemExit("common specialization foundation result is stale")
    if not args.emit and not args.check:
        print(detailed, end="")
    else:
        print("LOCAL SPECIALIZATION FOUNDATIONS: EXACT CHECKS PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
