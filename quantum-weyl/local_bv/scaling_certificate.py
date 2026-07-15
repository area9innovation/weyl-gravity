"""Reproduce the local-algebra scaling and tensor-product foundation receipt."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from .algebra import canonical_sha256
from .covariant_derivatives import covariant_commutator_relation_in_monomial
from .curvature import (
    RIEMANN,
    pair_partitions,
    riemann_product_contraction_from_pairing,
)
from .pairing_orbits import identical_factor_group, signed_pairing_orbits
from .tensors import (
    CANONICALIZATION_CACHE_MAXSIZE,
    TensorExpression,
    TensorFactor,
    TensorMonomial,
    TensorSpec,
)


PACKAGE_ROOT = Path(__file__).resolve().parent
QUANTUM_ROOT = PACKAGE_ROOT.parent
DETAILED_PATH = (
    PACKAGE_ROOT
    / "certificates"
    / "LOCAL_ALGEBRA_SCALING_FOUNDATIONS_CERTIFICATE.json"
)
RESULT_PATH = QUANTUM_ROOT / "certificates" / "LOCAL_ALGEBRA_SCALING_FOUNDATIONS.json"
SCHEMA_PATH = PACKAGE_ROOT / "schema" / "scaling_certificate.schema.json"


def _source_manifest() -> dict[str, str]:
    paths = (
        "__init__.py",
        "covariant_derivatives.py",
        "curvature.py",
        "pairing_orbits.py",
        "quotient.py",
        "scaling_certificate.py",
        "schema/scaling_certificate.schema.json",
        "schema_validation.py",
        "tensors.py",
        "tests/test_covariant_derivatives.py",
        "tests/test_pairing_orbits.py",
        "tests/test_scaling_certificate.py",
        "tests/test_schema_validation.py",
        "tests/test_tensor_products.py",
    )
    return {
        path: hashlib.sha256((PACKAGE_ROOT / path).read_bytes()).hexdigest()
        for path in paths
    }


def _tensor_product_receipt() -> tuple[dict[str, Any], str]:
    vector = TensorSpec.without_slot_symmetry("V", 1)
    covector = TensorSpec.without_slot_symmetry("W", 1)
    left = TensorExpression.monomial(
        TensorMonomial((TensorFactor(vector, (0,)),))
    )
    right = TensorExpression.monomial(
        TensorMonomial((TensorFactor(covector, (0,)),))
    )
    disjoint = left.tensor_product(right)
    contracted = left.tensor_product(right, index_map={0: 0})
    if any(term.is_complete_contraction() for term in disjoint.terms):
        raise AssertionError("default tensor product collided abstract indices")
    if not all(term.is_complete_contraction() for term in contracted.terms):
        raise AssertionError("explicit tensor-product contraction failed")

    base = TensorMonomial(
        (
            TensorFactor(RIEMANN, (0, 1, 1, 2)),
            TensorFactor(RIEMANN, (2, 4, 3, 4)),
        )
    )
    mixed = covariant_commutator_relation_in_monomial(base, 0, 0, 3)
    factor_counts = sorted({len(term.factors) for term in mixed.terms})
    if factor_counts != [2, 3] or not all(
        term.is_complete_contraction() for term in mixed.terms
    ):
        raise AssertionError("contracted commutator did not mix R nabla^2 R and R^3")
    return (
        {
            "default_index_policy": "ALPHA_RENAME_RIGHT_DISJOINTLY",
            "explicit_contraction_policy": "RIGHT_INDEX_MAP_REQUIRED",
            "default_product_complete_contraction": False,
            "mapped_product_complete_contraction": True,
            "contracted_commutator_term_count": len(mixed.terms),
            "contracted_commutator_factor_counts": factor_counts,
            "contracted_commutator_all_terms_complete": True,
            "contracted_commutator_relation": mixed.canonical_payload(),
        },
        mixed.canonical_hash(),
    )


def build_certificate() -> dict[str, Any]:
    pairings = tuple(pair_partitions(tuple(range(12))))
    actions = identical_factor_group(RIEMANN, 3)
    orbits = signed_pairing_orbits(pairings, actions)
    expected = {
        "raw_pairing_count": 10395,
        "signed_group_order": 3072,
        "orbit_count": 33,
        "vanishing_orbit_count": 20,
        "nonvanishing_orbit_count": 13,
    }
    actual = {
        "raw_pairing_count": len(pairings),
        "signed_group_order": len(actions),
        "orbit_count": len(orbits),
        "vanishing_orbit_count": sum(orbit.vanishes for orbit in orbits),
        "nonvanishing_orbit_count": sum(not orbit.vanishes for orbit in orbits),
    }
    if actual != expected:
        raise AssertionError(f"cubic orbit ledger drifted: {actual}")
    if sum(orbit.size for orbit in orbits) != len(pairings):
        raise AssertionError("cubic signed orbits do not cover all pairings")

    representative_payloads: list[dict[str, object]] = []
    orbit_ledger: list[dict[str, object]] = []
    for orbit in orbits:
        sign, canonical = riemann_product_contraction_from_pairing(
            orbit.canonical_pairing, 3
        ).canonicalize()
        if bool(sign) == orbit.vanishes or (canonical is None) != orbit.vanishes:
            raise AssertionError("orbit-first result disagrees with monomial canonicalizer")
        if canonical is not None:
            representative_payloads.append(canonical.canonical_payload())
        orbit_ledger.append(
            {
                "canonical_pairing": [list(pair) for pair in orbit.canonical_pairing],
                "orbit_size": orbit.size,
                "vanishes": orbit.vanishes,
            }
        )
    if len({canonical_sha256(item) for item in representative_payloads}) != 13:
        raise AssertionError("nonzero cubic orbit representatives are not distinct")

    tensor_product, commutator_hash = _tensor_product_receipt()
    source_manifest = _source_manifest()
    full_partition = [
        {
            "members": [[list(pair) for pair in member] for member in orbit.members],
            "signs_to_canonical": list(orbit.signs_to_canonical),
        }
        for orbit in orbits
    ]
    action_payload = [
        {"positions": list(action.positions), "sign": action.sign}
        for action in actions
    ]
    return {
        "result_id": "LOCAL_ALGEBRA_SCALING_FOUNDATIONS_CERTIFICATE",
        "result_state": "INFRASTRUCTURE_VERIFIED",
        "classical_commit": "UNFROZEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "scope": (
            "Collision-safe tensor products; contraction-aware commutators; "
            "signed orbit-first exhaustive generation of cubic Riemann contractions."
        ),
        "checks": {
            "tensor_product_alpha_renaming": "VERIFIED",
            "explicit_index_contraction": "VERIFIED",
            "contracted_commutator_Rnabla2R_R3_mixing": "VERIFIED",
            "cubic_pairing_exhaustion": "VERIFIED",
            "signed_orbit_partition": "VERIFIED",
            "orbit_representative_canonicalizer_crosscheck": "VERIFIED",
            "algebraic_bianchi_cubic_quotient": "NOT_COMPUTED",
            "six_derivative_mixed_quotient": "NOT_COMPUTED",
            "local_cohomology_H_s_mod_d": "NOT_COMPUTED",
        },
        "tensor_product": tensor_product,
        "cubic_orbits": {
            **actual,
            "covered_pairing_count": sum(orbit.size for orbit in orbits),
            "representatives_cross_checked": len(orbits),
            "raw_monomial_canonicalizations_avoided": len(pairings) - len(orbits),
            "canonicalization_cache_max_entries": CANONICALIZATION_CACHE_MAXSIZE,
            "orbit_size_histogram": {
                str(size): count
                for size, count in sorted(Counter(orbit.size for orbit in orbits).items())
            },
            "orbit_ledger": orbit_ledger,
            "nonzero_canonical_representatives": representative_payloads,
        },
        "canonical_hashes": {
            "signed_group_sha256": canonical_sha256(action_payload),
            "signed_orbit_partition_sha256": canonical_sha256(full_partition),
            "nonzero_cubic_representatives_sha256": canonical_sha256(
                representative_payloads
            ),
            "contracted_commutator_relation_sha256": commutator_hash,
            "source_manifest_sha256": canonical_sha256(source_manifest),
        },
        "not_computed": [
            "algebraic Bianchi quotient of the thirteen nonzero cubic symmetry orbits",
            "integration-by-parts and commutator quotient joining R^3 to (nabla Riemann)^2",
            "dimension-dependent Schouten identities",
            "Weyl BRST curvature rows, antifields, descent, and H^{g,4}(s|d)",
        ],
        "assumptions": [
            "The Riemann tensor has the declared eight-element signed intrinsic symmetry group.",
            "All three cubic Riemann factors are Grassmann even and interchangeable.",
            "Orbit-first generation changes enumeration cost, not the exact contraction space.",
            "The bounded monomial canonicalization cache may evict entries without changing canonical results.",
        ],
    }


def build_result_envelope() -> dict[str, Any]:
    return {
        "result_id": "LOCAL_ALGEBRA_SCALING_FOUNDATIONS",
        "classical_commit": "UNFROZEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "lifecycle_status": "CLASSIFIED",
        "ghost_number": 0,
        "form_degree": 0,
        "antifield_number": 0,
        "parity": "even",
        "representative": "exact tensor-product and signed cubic-pairing orbit infrastructure",
        "cohomology_status": "NOT_COMPUTED",
        "descent_status": "NOT_COMPUTED",
        "coefficient_status": "NOT_COMPUTED",
        "residual_projection_status": "NOT_COMPUTED",
        "proof_certificate": (
            "quantum-weyl/local_bv/certificates/"
            "LOCAL_ALGEBRA_SCALING_FOUNDATIONS_CERTIFICATE.json"
        ),
        "assumptions": [
            "This classifies contraction orbits only, not cubic invariants modulo Bianchi identities or local BRST cohomology."
        ],
        "notes": (
            "LOCAL-ALGEBRAIC infrastructure only. The mixed six-derivative "
            "quotient and H^{g,4}(s|d) remain NOT_COMPUTED."
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
            raise SystemExit("detailed scaling certificate is stale")
        if RESULT_PATH.read_text(encoding="utf-8") != result:
            raise SystemExit("common scaling result envelope is stale")
    if not args.emit and not args.check:
        print(detailed, end="")
    else:
        print("LOCAL ALGEBRA SCALING FOUNDATIONS: EXACT CHECKS PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
