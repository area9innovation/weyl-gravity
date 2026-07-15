"""Reproduce the exact Schouten-zero Weyl-image certificate."""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

from .algebra import canonical_sha256
from .curvature import RIEMANN
from .tensors import TensorExpression, TensorFactor, TensorMonomial
from .weyl_decomposition import (
    expand_riemann_factors,
    riemann_to_schouten_zero_weyl,
    schouten_zero_projection,
)
from .weyl_image import schouten_zero_weyl_image_analysis


PACKAGE_ROOT = Path(__file__).resolve().parent
QUANTUM_ROOT = PACKAGE_ROOT.parent
DETAILED_PATH = (
    PACKAGE_ROOT
    / "certificates"
    / "LOCAL_SCHOUTEN_ZERO_WEYL_IMAGE_CERTIFICATE.json"
)
RESULT_PATH = (
    QUANTUM_ROOT / "certificates" / "LOCAL_SCHOUTEN_ZERO_WEYL_IMAGE.json"
)
SCHEMA_PATH = PACKAGE_ROOT / "schema" / "weyl_image_certificate.schema.json"


def _source_manifest() -> dict[str, str]:
    paths = (
        "__init__.py",
        "curvature.py",
        "four_dimensional.py",
        "quotient.py",
        "six_derivative.py",
        "specialization.py",
        "tensors.py",
        "weyl_decomposition.py",
        "weyl_image.py",
        "weyl_image_certificate.py",
        "schema/weyl_image_certificate.schema.json",
        "tests/test_weyl_decomposition.py",
        "tests/test_weyl_image.py",
        "tests/test_weyl_image_certificate.py",
    )
    return {
        path: hashlib.sha256((PACKAGE_ROOT / path).read_bytes()).hexdigest()
        for path in paths
    }


def _fraction(value: Fraction) -> dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}


def _matrix(
    rows: tuple[tuple[Fraction, ...], ...],
) -> list[list[dict[str, int]]]:
    return [[_fraction(value) for value in row] for row in rows]


def _decomposition_projection_audit() -> dict[str, str]:
    witnesses = {
        "algebraic": TensorExpression.monomial(
            TensorMonomial((TensorFactor(RIEMANN, (0, 1, 2, 3)),))
        ),
        "differentiated": TensorExpression.monomial(
            TensorMonomial(
                (TensorFactor(RIEMANN, (0, 1, 2, 3), (4,)),)
            )
        ),
    }
    hashes = {}
    for name, witness in witnesses.items():
        expanded_projection = schouten_zero_projection(
            expand_riemann_factors(witness)
        )
        factorized_projection = riemann_to_schouten_zero_weyl(witness)
        if expanded_projection != factorized_projection:
            raise AssertionError("factorized Schouten-zero projection drifted")
        hashes[name] = expanded_projection.canonical_hash()
    return hashes


def build_certificate() -> dict[str, Any]:
    analysis = schouten_zero_weyl_image_analysis()
    expected = {
        "source_dimension": 8,
        "target_ambient_dimension": 17,
        "mapped_relation_count": 106,
        "target_relation_rank": 16,
        "target_dimension": 1,
        "induced_map_rank": 1,
        "kernel_dimension": 7,
        "sector_image_ranks": {
            "R3": 1,
            "nablaR_nablaR": 1,
            "R_nabla2R": 1,
        },
        "sector_nonzero_ambient_images": {
            "R3": 5,
            "nablaR_nablaR": 6,
            "R_nabla2R": 6,
        },
    }
    actual = {name: analysis[name] for name in expected}
    if actual != expected:
        raise AssertionError(f"Schouten-zero image ledger drifted: {actual}")
    expected_map = (
        (
            Fraction(0),
            Fraction(0),
            Fraction(1, 3),
            Fraction(1, 6),
            Fraction(0),
            Fraction(0),
            Fraction(0),
            Fraction(1),
        ),
    )
    if analysis["induced_map"] != expected_map:
        raise AssertionError("induced Schouten-zero image matrix drifted")

    odd = analysis["odd_companion"]
    if odd.parity_transform() != -odd:
        raise AssertionError("odd Hodge companion parity drifted")
    decomposition_audit = _decomposition_projection_audit()
    source_manifest = _source_manifest()
    return {
        "result_id": "LOCAL_SCHOUTEN_ZERO_WEYL_IMAGE_CERTIFICATE",
        "result_state": "SCHOUTEN_ZERO_IMAGE_VERIFIED",
        "classical_commit": "UNFROZEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "scope": (
            "Exact induced image of the certified four-dimensional integrated "
            "order-six Riemann quotient after setting the Schouten tensor and "
            "all of its covariant derivatives to zero."
        ),
        "checks": {
            "explicit_riemann_decomposition": "VERIFIED",
            "differentiated_projection_factorization": "VERIFIED",
            "mapped_relation_closure": "VERIFIED",
            "induced_map_surjectivity": "VERIFIED",
            "exact_kernel_witnesses": "VERIFIED",
            "all_sector_image_ranks": "VERIFIED",
            "odd_hodge_companion": "CONSTRUCTED",
            "unrestricted_weyl_jet_quotient": "NOT_COMPUTED",
            "parity_odd_single_epsilon_enumeration": "NOT_COMPUTED",
            "local_cohomology_H_s_mod_d": "NOT_COMPUTED",
        },
        "image": {
            **expected,
            "mapped_family_counts": {
                name: len(relations)
                for name, relations in analysis["mapped_families"].items()
            },
            "cumulative_reduction": list(analysis["cumulative_reduction"]),
            "induced_map": _matrix(analysis["induced_map"]),
            "target_representative": analysis[
                "representative"
            ].canonical_payload(),
            "target_representative_sha256": TensorExpression.monomial(
                analysis["representative"]
            ).canonical_hash(),
        },
        "kernel": {
            "dimension": analysis["kernel_dimension"],
            "coordinate_vectors": _matrix(analysis["kernel"]),
            "witnesses": [
                {
                    "sha256": expression.canonical_hash(),
                    "expression": expression.canonical_payload(),
                }
                for expression in analysis["kernel_expressions"]
            ],
        },
        "odd_companion": {
            "status": "CONSTRUCTED_NOT_A_COMPLETE_BASIS",
            "parity": "odd",
            "sha256": odd.canonical_hash(),
            "expression": odd.canonical_payload(),
        },
        "decomposition_projection_audit": decomposition_audit,
        "canonical_hashes": {
            "mapped_relations_sha256": canonical_sha256(
                [
                    relation.canonical_payload()
                    for relation in analysis["mapped_relations"]
                ]
            ),
            "induced_map_sha256": canonical_sha256(
                _matrix(analysis["induced_map"])
            ),
            "kernel_sha256": canonical_sha256(
                [
                    expression.canonical_payload()
                    for expression in analysis["kernel_expressions"]
                ]
            ),
            "source_manifest_sha256": canonical_sha256(source_manifest),
        },
        "not_computed": [
            "the unrestricted local Weyl-jet quotient with nonzero Cotton "
            "completion",
            "an exhaustive parity-odd single-epsilon basis and its relations",
            "Weyl-BRST closure, antifield descent, and H^{g,4}(s|d)",
            "counterterm or anomaly coefficients, QME restoration, and "
            "residual transfer",
        ],
        "assumptions": [
            "The source is the certified eight-dimensional four-dimensional "
            "integrated Riemann quotient.",
            "Schouten and every covariant derivative of Schouten are set to "
            "zero after the exact Ricci decomposition.",
            "The resulting differential Bianchi identities also impose "
            "Cotton=0, so this image is narrower than unrestricted Weyl-jet "
            "algebra.",
            "The odd Hodge companion proves existence of a nonzero odd "
            "expression but not completeness of the odd sector.",
        ],
    }


def build_result_envelope() -> dict[str, Any]:
    return {
        "result_id": "LOCAL_SCHOUTEN_ZERO_WEYL_IMAGE",
        "classical_commit": "UNFROZEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "lifecycle_status": "CLASSIFIED",
        "ghost_number": 0,
        "form_degree": 4,
        "antifield_number": 0,
        "parity": "even",
        "representative": (
            "rank-one Schouten-zero image of the 4D order-six Riemann quotient"
        ),
        "cohomology_status": "NOT_COMPUTED",
        "descent_status": "NOT_COMPUTED",
        "coefficient_status": "NOT_COMPUTED",
        "residual_projection_status": "NOT_COMPUTED",
        "proof_certificate": (
            "quantum-weyl/local_bv/certificates/"
            "LOCAL_SCHOUTEN_ZERO_WEYL_IMAGE_CERTIFICATE.json"
        ),
        "assumptions": [
            "Schouten and all of its covariant derivatives vanish; this is "
            "not the unrestricted Weyl-jet quotient."
        ],
        "notes": (
            "LOCAL-ALGEBRAIC restriction theorem only. The exact 8-to-1 "
            "surjection has a seven-dimensional kernel and all three sectors "
            "reach the surviving class. BRST cohomology remains NOT_COMPUTED."
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
            raise SystemExit("detailed Schouten-zero Weyl-image certificate is stale")
        if RESULT_PATH.read_text(encoding="utf-8") != result:
            raise SystemExit("common Schouten-zero Weyl-image result is stale")
    if not args.emit and not args.check:
        print(detailed, end="")
    else:
        print("LOCAL SCHOUTEN-ZERO WEYL IMAGE: EXACT CHECKS PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
