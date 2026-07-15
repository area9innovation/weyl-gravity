"""Reproduce the exact local curvature canonicalization certificate."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from .algebra import canonical_sha256
from .curvature import (
    EPSILON,
    RIEMANN,
    named_quadratic_representatives,
    quadratic_curvature_analysis,
)
from .quotient import RelationQuotient
from .tensors import (
    TensorExpression,
    TensorFactor,
    TensorMonomial,
    TensorSpec,
    total_covariant_derivative,
)


PACKAGE_ROOT = Path(__file__).resolve().parent
QUANTUM_ROOT = PACKAGE_ROOT.parent
DETAILED_PATH = (
    PACKAGE_ROOT
    / "certificates"
    / "LOCAL_CURVATURE_CANONICALIZATION_CERTIFICATE.json"
)
RESULT_PATH = QUANTUM_ROOT / "certificates" / "LOCAL_CURVATURE_CANONICALIZATION.json"


def _source_manifest() -> dict[str, str]:
    paths = (
        "__init__.py",
        "curvature.py",
        "curvature_certificate.py",
        "quotient.py",
        "tensors.py",
        "schema/curvature_certificate.schema.json",
        "tests/test_curvature.py",
        "tests/test_curvature_certificate.py",
        "tests/test_ibp.py",
        "tests/test_tensors.py",
    )
    return {
        path: hashlib.sha256((PACKAGE_ROOT / path).read_bytes()).hexdigest()
        for path in paths
    }


def _fraction_payload(value: object) -> dict[str, int]:
    fraction = value if hasattr(value, "numerator") else int(value)
    return {
        "numerator": int(fraction.numerator),
        "denominator": int(fraction.denominator),
    }


def _ibp_receipt() -> tuple[dict[str, Any], TensorExpression]:
    scalar_a = TensorSpec.without_slot_symmetry("A", 0)
    scalar_b = TensorSpec.without_slot_symmetry("B", 0)
    vector = TensorMonomial(
        (
            TensorFactor(scalar_a, ()),
            TensorFactor(scalar_b, (), derivatives=(7,)),
        )
    )
    divergence = total_covariant_derivative(vector, 7)
    quotient = RelationQuotient(divergence.terms, (divergence,))
    if len(divergence.terms) != 2 or quotient.relation_rank != 1:
        raise AssertionError("exact covariant Leibniz/IBP relation drifted")
    if quotient.quotient_dimension != 1 or any(quotient.free_coordinates(divergence)):
        raise AssertionError("total divergence does not vanish in the IBP quotient")
    return (
        {
            "vector_factor_count": 2,
            "leibniz_term_count": len(divergence.terms),
            "relation_rank": quotient.relation_rank,
            "quotient_dimension": quotient.quotient_dimension,
            "total_divergence_coordinates": [
                _fraction_payload(value)
                for value in quotient.free_coordinates(divergence)
            ],
        },
        divergence,
    )


def _parity_receipt() -> tuple[dict[str, Any], TensorExpression]:
    epsilon = TensorExpression.monomial(
        TensorMonomial((TensorFactor(EPSILON, (0, 1, 2, 3)),))
    )
    riemann = TensorExpression.monomial(
        TensorMonomial((TensorFactor(RIEMANN, (0, 1, 2, 3)),))
    )
    if epsilon.parity_transform() != -epsilon:
        raise AssertionError("orientation tensor is not parity odd")
    if riemann.parity_transform() != riemann:
        raise AssertionError("Riemann tensor is not parity even")
    if epsilon.parity_transform().parity_transform() != epsilon:
        raise AssertionError("spacetime parity is not an involution")
    return (
        {
            "epsilon_signed_symmetry_group_order": len(EPSILON.intrinsic_symmetries),
            "riemann_signed_symmetry_group_order": len(RIEMANN.intrinsic_symmetries),
            "epsilon_eigenvalue": -1,
            "riemann_eigenvalue": 1,
            "parity_squared": 1,
        },
        epsilon,
    )


def build_certificate() -> dict[str, Any]:
    analysis = quadratic_curvature_analysis()
    expected = {
        "raw_pairing_count": 105,
        "symmetry_canonical_monomial_count": 4,
        "bianchi_relation_rank": 1,
        "quotient_dimension": 3,
        "named_representative_rank": 3,
    }
    for key, value in expected.items():
        if analysis[key] != value:
            raise AssertionError(f"quadratic curvature invariant {key} drifted")
    if analysis["named_representative_rank"] != analysis["quotient_dimension"]:
        raise AssertionError("named curvature representatives do not span the quotient")

    quotient = analysis["quotient"]
    ibp, divergence = _ibp_receipt()
    parity, epsilon = _parity_receipt()
    source_manifest = _source_manifest()
    relations = sorted(
        [relation.canonical_payload() for relation in analysis["relations"]],
        key=lambda payload: canonical_sha256(payload),
    )
    named_coordinates = {
        name: [_fraction_payload(value) for value in quotient.free_coordinates(expression)]
        for name, expression in named_quadratic_representatives().items()
    }
    quadratic = {
        "generator": "all perfect matchings of eight slots in Riemann tensor squared",
        "raw_pairing_count": analysis["raw_pairing_count"],
        "symmetry_canonical_monomial_count": analysis[
            "symmetry_canonical_monomial_count"
        ],
        "nonzero_unique_bianchi_relation_count": analysis[
            "nonzero_unique_bianchi_relation_count"
        ],
        "bianchi_relation_rank": analysis["bianchi_relation_rank"],
        "quotient_dimension": analysis["quotient_dimension"],
        "named_representatives": list(analysis["named_representatives"]),
        "named_representative_rank": analysis["named_representative_rank"],
        "canonical_basis": [
            monomial.canonical_payload() for monomial in quotient.basis
        ],
        "relation_rref": [
            [_fraction_payload(value) for value in row] for row in quotient.rref
        ],
        "pivot_columns": list(quotient.pivots),
        "free_columns": list(quotient.free_columns),
        "named_representative_free_coordinates": named_coordinates,
        "basis_was_generated": True,
    }
    return {
        "result_id": "LOCAL_CURVATURE_CANONICALIZATION_CERTIFICATE",
        "result_state": "INFRASTRUCTURE_VERIFIED",
        "classical_commit": "UNFROZEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "scope": (
            "Finite exact abstract-index monomials; signed Riemann and epsilon "
            "symmetries; graded factor order; dummy renaming; algebraic Bianchi "
            "quotient; covariant total-derivative/IBP quotient; spacetime parity."
        ),
        "checks": {
            "exact_rational_relation_reduction": "VERIFIED",
            "signed_tensor_symmetries": "VERIFIED",
            "graded_factor_ordering": "VERIFIED",
            "dummy_index_renaming": "VERIFIED",
            "free_index_order_preservation": "VERIFIED",
            "algebraic_bianchi_quotient": "VERIFIED",
            "total_derivative_leibniz": "VERIFIED",
            "integration_by_parts_quotient": "VERIFIED",
            "spacetime_parity_involution": "VERIFIED",
            "differential_bianchi": "NOT_COMPUTED",
            "covariant_derivative_commutators": "NOT_COMPUTED",
            "hodge_dual_normalization": "NOT_COMPUTED",
            "local_cohomology_H_s_mod_d": "NOT_COMPUTED",
            "antifield_rows": "BLOCKED",
        },
        "quadratic_curvature": quadratic,
        "integration_by_parts": ibp,
        "parity": parity,
        "canonical_hashes": {
            "quadratic_basis_sha256": canonical_sha256(
                [monomial.canonical_payload() for monomial in quotient.basis]
            ),
            "bianchi_relations_sha256": canonical_sha256(relations),
            "ibp_relation_sha256": divergence.canonical_hash(),
            "parity_odd_epsilon_sha256": epsilon.canonical_hash(),
            "source_manifest_sha256": canonical_sha256(source_manifest),
        },
        "not_computed": [
            "dimension-dependent Schouten identities beyond the generated quadratic scalar sector",
            "differential Bianchi identities and covariant derivative commutators",
            "Hodge-star normalization and chiral Weyl projectors",
            "Weyl BRST variations of curvature tensors",
            "general derivative-bounded invariant ansatz generation",
            "antifield and Koszul-Tate differential",
            "counterterm cohomology H^{0,4}(s|d)",
            "anomaly cohomology H^{1,4}(s|d)",
            "descent equations and cylinder restriction",
        ],
        "assumptions": [
            "Repeated lowered labels denote contraction with a covariantly constant inverse metric.",
            "The certified parity-even quadratic scalar sector is in four spacetime dimensions and contains two Riemann factors with no covariant derivatives.",
            "The covariant derivative is even and obeys Leibniz; its commutator is outside this certificate.",
            "The epsilon tensor is covariantly constant and odd under orientation reversal.",
        ],
    }


def build_result_envelope() -> dict[str, Any]:
    return {
        "result_id": "LOCAL_CURVATURE_CANONICALIZATION",
        "classical_commit": "UNFROZEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "lifecycle_status": "CLASSIFIED",
        "ghost_number": 0,
        "form_degree": 0,
        "antifield_number": 0,
        "parity": "mixed",
        "representative": "generated abstract-index curvature and total-derivative quotient infrastructure",
        "cohomology_status": "NOT_COMPUTED",
        "descent_status": "NOT_COMPUTED",
        "coefficient_status": "NOT_COMPUTED",
        "residual_projection_status": "NOT_COMPUTED",
        "proof_certificate": (
            "quantum-weyl/local_bv/certificates/"
            "LOCAL_CURVATURE_CANONICALIZATION_CERTIFICATE.json"
        ),
        "assumptions": [
            "The detailed certificate is infrastructure, not a local-BRST cohomology classification."
        ],
        "notes": (
            "Exact LOCAL-ALGEBRAIC canonicalization only. Antifields, descent, "
            "counterterm/anomaly cohomology, coefficients, cylinder projection, "
            "QME restoration, and Lorentzian causal claims are NOT_COMPUTED."
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
            raise SystemExit("detailed curvature certificate is stale")
        if RESULT_PATH.read_text(encoding="utf-8") != result:
            raise SystemExit("common curvature result envelope is stale")
    if not args.emit and not args.check:
        print(detailed, end="")
    else:
        print("LOCAL CURVATURE CANONICALIZATION: EXACT CHECKS PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
