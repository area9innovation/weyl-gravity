"""Reproduce the differential-Bianchi, commutator, and Hodge certificate."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from .algebra import canonical_sha256
from .covariant_derivatives import (
    COMMUTATOR_CONVENTION,
    covariant_commutator_relation,
)
from .curvature import one_derivative_curvature_analysis
from .hodge import Signature, TwoFormHodge
from .quotient import RelationQuotient
from .tensors import TensorFactor, TensorSpec


PACKAGE_ROOT = Path(__file__).resolve().parent
QUANTUM_ROOT = PACKAGE_ROOT.parent
DETAILED_PATH = (
    PACKAGE_ROOT
    / "certificates"
    / "LOCAL_DIFFERENTIAL_HODGE_CANONICALIZATION_CERTIFICATE.json"
)
RESULT_PATH = (
    QUANTUM_ROOT
    / "certificates"
    / "LOCAL_DIFFERENTIAL_HODGE_CANONICALIZATION.json"
)


def _source_manifest() -> dict[str, str]:
    paths = (
        "__init__.py",
        "covariant_derivatives.py",
        "curvature.py",
        "differential_hodge_certificate.py",
        "hodge.py",
        "quotient.py",
        "tensors.py",
        "schema/differential_hodge_certificate.schema.json",
        "tests/test_covariant_derivatives.py",
        "tests/test_differential_curvature.py",
        "tests/test_differential_hodge_certificate.py",
        "tests/test_hodge.py",
    )
    return {
        path: hashlib.sha256((PACKAGE_ROOT / path).read_bytes()).hexdigest()
        for path in paths
    }


def _fraction_payload(value: object) -> dict[str, int]:
    return {
        "numerator": int(value.numerator),
        "denominator": int(value.denominator),
    }


def _relation_set_hash(relations: tuple[object, ...]) -> str:
    payloads = sorted(
        [relation.canonical_payload() for relation in relations],
        key=canonical_sha256,
    )
    return canonical_sha256(payloads)


def _commutator_receipt() -> tuple[dict[str, Any], dict[str, str]]:
    receipts: dict[str, Any] = {}
    hashes: dict[str, str] = {}
    for rank, expected_terms in ((0, 2), (1, 3), (2, 4)):
        spec = TensorSpec.without_slot_symmetry(f"T{rank}", rank)
        factor = TensorFactor(spec, tuple(range(rank)))
        left, right = rank + 1, rank + 2
        relation = covariant_commutator_relation(factor, left, right)
        reversed_relation = covariant_commutator_relation(factor, right, left)
        if len(relation.terms) != expected_terms or relation != -reversed_relation:
            raise AssertionError(f"rank-{rank} commutator witness drifted")
        quotient = RelationQuotient(relation.terms, (relation,))
        if quotient.relation_rank != 1 or any(quotient.free_coordinates(relation)):
            raise AssertionError(f"rank-{rank} commutator quotient failed")
        name = f"covariant_rank_{rank}"
        receipts[name] = {
            "term_count": len(relation.terms),
            "curvature_action_term_count": rank,
            "antisymmetric_in_derivative_indices": True,
            "relation_rank": quotient.relation_rank,
            "quotient_dimension": quotient.quotient_dimension,
            "relation": relation.canonical_payload(),
        }
        hashes[f"commutator_rank_{rank}_sha256"] = relation.canonical_hash()
    return (
        {
            "convention": COMMUTATOR_CONVENTION,
            "all_tensor_slots": "COVARIANT",
            "witnesses": receipts,
        },
        hashes,
    )


def build_certificate() -> dict[str, Any]:
    analysis = one_derivative_curvature_analysis()
    expected = {
        "raw_pairing_count": 945,
        "symmetry_canonical_monomial_count": 12,
        "algebraic_bianchi_relation_count": 6,
        "algebraic_bianchi_rank": 3,
        "differential_bianchi_relation_count": 16,
        "differential_bianchi_rank": 8,
        "combined_relation_rank": 8,
        "quotient_dimension": 4,
    }
    for key, value in expected.items():
        if analysis[key] != value:
            raise AssertionError(f"one-derivative curvature {key} drifted")

    quotient = analysis["quotient"]
    differential = {
        "generator": (
            "all perfect matchings of ten slots in "
            "(nabla Riemann)(nabla Riemann)"
        ),
        **{key: analysis[key] for key in expected},
        "canonical_basis": [
            monomial.canonical_payload() for monomial in quotient.basis
        ],
        "relation_rref": [
            [_fraction_payload(value) for value in row] for row in quotient.rref
        ],
        "pivot_columns": list(quotient.pivots),
        "free_columns": list(quotient.free_columns),
        "basis_was_generated": True,
        "ibp_or_commutator_reduction_applied": False,
    }
    commutator, commutator_hashes = _commutator_receipt()
    hodge = {
        signature.value: TwoFormHodge(signature).verify() for signature in Signature
    }
    relation_sets = analysis["relation_sets"]
    source_manifest = _source_manifest()
    return {
        "result_id": "LOCAL_DIFFERENTIAL_HODGE_CANONICALIZATION_CERTIFICATE",
        "result_state": "INFRASTRUCTURE_VERIFIED",
        "classical_commit": "UNFROZEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "scope": (
            "Finite exact (nabla Riemann)^2 contractions modulo intrinsic, "
            "algebraic-Bianchi, and differential-Bianchi relations; declared-sign "
            "covariant commutator witnesses; Euclidean/Lorentzian two-form Hodge "
            "and chiral-projector algebra with parity exchange."
        ),
        "checks": {
            "one_derivative_pairing_generation": "VERIFIED",
            "algebraic_bianchi_on_derivative_sector": "VERIFIED",
            "differential_bianchi_quotient": "VERIFIED",
            "exact_rational_relation_reduction": "VERIFIED",
            "covariant_commutator_declared_sign": "VERIFIED",
            "commutator_antisymmetry": "VERIFIED",
            "hodge_signature_square": "VERIFIED",
            "chiral_projectors": "VERIFIED",
            "parity_exchanges_chiralities": "VERIFIED",
            "ibp_commutator_mixing_with_cubic_curvature": "NOT_COMPUTED",
            "dimension_dependent_schouten_quotient": "NOT_COMPUTED",
            "local_cohomology_H_s_mod_d": "NOT_COMPUTED",
            "antifield_rows": "BLOCKED",
        },
        "one_derivative_curvature": differential,
        "covariant_commutator": commutator,
        "hodge": hodge,
        "canonical_hashes": {
            "one_derivative_basis_sha256": canonical_sha256(
                [monomial.canonical_payload() for monomial in quotient.basis]
            ),
            "algebraic_bianchi_relations_sha256": _relation_set_hash(
                relation_sets["algebraic_bianchi"]
            ),
            "differential_bianchi_relations_sha256": _relation_set_hash(
                relation_sets["differential_bianchi"]
            ),
            "hodge_receipt_sha256": canonical_sha256(hodge),
            "source_manifest_sha256": canonical_sha256(source_manifest),
            **commutator_hashes,
        },
        "not_computed": [
            "integration-by-parts and commutator reduction mixing (nabla Riemann)^2 with cubic curvature",
            "complete six-derivative scalar invariant quotient",
            "dimension-dependent Schouten identities",
            "Hodge action on the complete Weyl tensor with tracefree quotient",
            "Weyl BRST variations and derivative-bounded ghost-number ansatz",
            "antifield and Koszul-Tate differential",
            "counterterm or anomaly cohomology H^{g,4}(s|d)",
            "descent, cylinder restriction, coefficients, QME, and Lorentzian causal products",
        ],
        "assumptions": [
            "Riemann convention is fixed by the displayed covariant commutator formula.",
            "All commutator witness tensor slots are covariant and initially undifferentiated.",
            "The epsilon contraction convention is epsilon_abcd epsilon^{cdef} = 2 sigma delta_ab^{ef}, with sigma=+1 Euclidean and -1 Lorentzian.",
            "The finite derivative quotient contains exactly two once-differentiated Riemann factors before IBP/commutator mixing.",
        ],
    }


def build_result_envelope() -> dict[str, Any]:
    return {
        "result_id": "LOCAL_DIFFERENTIAL_HODGE_CANONICALIZATION",
        "classical_commit": "UNFROZEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "lifecycle_status": "CLASSIFIED",
        "ghost_number": 0,
        "form_degree": 0,
        "antifield_number": 0,
        "parity": "mixed",
        "representative": "generated differential-curvature quotient and exact Hodge/chiral infrastructure",
        "cohomology_status": "NOT_COMPUTED",
        "descent_status": "NOT_COMPUTED",
        "coefficient_status": "NOT_COMPUTED",
        "residual_projection_status": "NOT_COMPUTED",
        "proof_certificate": (
            "quantum-weyl/local_bv/certificates/"
            "LOCAL_DIFFERENTIAL_HODGE_CANONICALIZATION_CERTIFICATE.json"
        ),
        "assumptions": [
            "The detailed certificate is a finite local-algebra result, not a six-derivative or BRST-cohomology classification."
        ],
        "notes": (
            "LOCAL-ALGEBRAIC only. IBP/commutator mixing with R^3, antifields, "
            "descent, cohomology, coefficients, cylinder projection, QME, and "
            "Lorentzian causal construction remain NOT_COMPUTED."
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
            raise SystemExit("detailed differential/Hodge certificate is stale")
        if RESULT_PATH.read_text(encoding="utf-8") != result:
            raise SystemExit("common differential/Hodge result envelope is stale")
    if not args.emit and not args.check:
        print(detailed, end="")
    else:
        print("LOCAL DIFFERENTIAL/HODGE CANONICALIZATION: EXACT CHECKS PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
