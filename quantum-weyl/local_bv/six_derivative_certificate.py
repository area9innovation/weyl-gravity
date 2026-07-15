"""Reproduce the cubic and mixed six-derivative curvature quotient receipt."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from .algebra import canonical_sha256
from .curvature import (
    curvature_product_bianchi_analysis,
    two_derivative_curvature_analysis,
)
from .six_derivative import six_derivative_curvature_analysis


PACKAGE_ROOT = Path(__file__).resolve().parent
QUANTUM_ROOT = PACKAGE_ROOT.parent
DETAILED_PATH = (
    PACKAGE_ROOT
    / "certificates"
    / "LOCAL_SIX_DERIVATIVE_CURVATURE_QUOTIENT_CERTIFICATE.json"
)
RESULT_PATH = QUANTUM_ROOT / "certificates" / "LOCAL_SIX_DERIVATIVE_CURVATURE_QUOTIENT.json"
SCHEMA_PATH = PACKAGE_ROOT / "schema" / "six_derivative_certificate.schema.json"


def _source_manifest() -> dict[str, str]:
    paths = (
        "__init__.py",
        "covariant_derivatives.py",
        "curvature.py",
        "pairing_orbits.py",
        "quotient.py",
        "schema/six_derivative_certificate.schema.json",
        "schema_validation.py",
        "six_derivative.py",
        "six_derivative_certificate.py",
        "tensors.py",
        "tests/test_cubic_curvature.py",
        "tests/test_six_derivative.py",
        "tests/test_six_derivative_certificate.py",
        "tests/test_two_derivative_curvature.py",
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


def _relation_hashes(relation_sets: dict[str, tuple[object, ...]]) -> dict[str, str]:
    return {
        f"{name}_sha256": canonical_sha256(
            sorted(
                (relation.canonical_payload() for relation in relations),
                key=canonical_sha256,
            )
        )
        for name, relations in relation_sets.items()
    }


def _sparse_rref_payload(rref: list[list[object]]) -> list[list[dict[str, int]]]:
    return [
        [
            {"column": column, **_fraction_payload(value)}
            for column, value in enumerate(row)
            if value
        ]
        for row in rref
    ]


def build_certificate() -> dict[str, Any]:
    cubic = curvature_product_bianchi_analysis(3)
    bridge = two_derivative_curvature_analysis()
    combined = six_derivative_curvature_analysis()
    expected_cubic = {
        "raw_pairing_count": 10_395,
        "signed_orbit_count": 33,
        "symmetry_vanishing_orbit_count": 20,
        "symmetry_nonzero_orbit_count": 13,
        "generated_nonzero_bianchi_relation_count": 10,
        "bianchi_relation_rank": 5,
        "quotient_dimension": 8,
    }
    expected_bridge = {
        "raw_pairing_count": 945,
        "symmetry_canonical_monomial_count": 14,
        "algebraic_bianchi_relation_count": 6,
        "algebraic_bianchi_rank": 3,
        "differential_bianchi_relation_count": 16,
        "differential_bianchi_rank": 8,
        "combined_relation_rank": 8,
        "quotient_dimension": 6,
    }
    for expected, analysis, label in (
        (expected_cubic, cubic, "cubic"),
        (expected_bridge, bridge, "bridge"),
    ):
        actual = {name: analysis[name] for name in expected}
        if actual != expected:
            raise AssertionError(f"{label} six-derivative ledger drifted: {actual}")
    if combined["combined_relation_rank"] != 29 or combined["quotient_dimension"] != 10:
        raise AssertionError("integrated six-derivative quotient drifted")
    if combined["local_normal_form_before_total_derivatives"][
        "dimension_with_degree_one_sector"
    ] != 17:
        raise AssertionError("local order-six normal-form cross-check drifted")

    quotient = combined["quotient"]
    source_manifest = _source_manifest()
    return {
        "result_id": "LOCAL_SIX_DERIVATIVE_CURVATURE_QUOTIENT_CERTIFICATE",
        "result_state": "INVARIANT_QUOTIENT_VERIFIED",
        "classical_commit": "UNFROZEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "scope": (
            "Dimension-independent parity-even scalar contractions in R^3, "
            "(nabla Riemann)^2, and Riemann nabla^2 Riemann, modulo intrinsic "
            "symmetries, Bianchi identities, total derivatives, and declared-sign "
            "covariant commutators."
        ),
        "checks": {
            "cubic_pairing_exhaustion": "VERIFIED",
            "cubic_algebraic_bianchi_quotient": "VERIFIED",
            "second_derivative_bridge_exhaustion": "VERIFIED",
            "outer_differential_bianchi": "VERIFIED",
            "integration_by_parts_relations": "VERIFIED",
            "contracted_commutator_relations": "VERIFIED",
            "commutator_collision_regression": "VERIFIED",
            "local_order_six_normal_form": "VERIFIED",
            "integrated_six_derivative_quotient": "VERIFIED",
            "four_dimensional_schouten_quotient": "NOT_COMPUTED",
            "weyl_tracefree_specialization": "NOT_COMPUTED",
            "local_cohomology_H_s_mod_d": "NOT_COMPUTED",
        },
        "cubic_R3": expected_cubic,
        "second_derivative_bridge": expected_bridge,
        "combined": {
            "sector_basis_dimensions_before_relations": combined[
                "sector_basis_dimensions_before_relations"
            ],
            "total_basis_dimension_before_relations": combined[
                "total_basis_dimension_before_relations"
            ],
            "relation_counts": combined["relation_counts"],
            "cumulative_reduction": combined["cumulative_reduction"],
            "local_normal_form_before_total_derivatives": combined[
                "local_normal_form_before_total_derivatives"
            ],
            "combined_relation_rank": combined["combined_relation_rank"],
            "quotient_dimension": combined["quotient_dimension"],
            "final_sector_ranks": combined["final_sector_ranks"],
            "final_derivative_union_rank": combined["final_derivative_union_rank"],
            "derivative_classes_outside_cubic_span": combined[
                "derivative_classes_outside_cubic_span"
            ],
            "canonical_basis": [
                monomial.canonical_payload() for monomial in quotient.basis
            ],
            "relation_rref_sparse": _sparse_rref_payload(quotient.rref),
            "pivot_columns": list(quotient.pivots),
            "free_columns": list(quotient.free_columns),
        },
        "independent_crosscheck": {
            "reference": "https://arxiv.org/abs/0805.1595",
            "reference_basis": "dimension-independent FKWC rank-zero order-six basis",
            "local_dimension_including_omitted_degree_one_sector": 17,
            "integrated_dimension_modulo_total_divergences": 10,
            "status": "MATCH",
            "role": "INDEPENDENT_CROSSCHECK_NOT_PROOF_INPUT",
        },
        "canonical_hashes": {
            "combined_basis_sha256": canonical_sha256(
                [monomial.canonical_payload() for monomial in quotient.basis]
            ),
            "combined_rref_sha256": canonical_sha256(
                _sparse_rref_payload(quotient.rref)
            ),
            "source_manifest_sha256": canonical_sha256(source_manifest),
            **_relation_hashes(combined["relation_sets"]),
        },
        "not_computed": [
            "four-dimensional dimension-dependent Schouten identities",
            "tracefree Weyl specialization and parity-odd epsilon sectors",
            "Weyl BRST variations and derivative-bounded ghost-number ansatz",
            "antifield/Koszul-Tate rows, descent, and H^{g,4}(s|d)",
            "cylinder restriction, coefficients, QME restoration, and Lorentzian causal products",
        ],
        "assumptions": [
            "Repeated lowered labels contract through a covariantly constant inverse metric.",
            "The declared commutator convention is [nabla_a,nabla_b]T_c = -R^d{}_{cab}T_d.",
            "The quotient is dimension-independent; no four-dimensional Schouten identity is installed.",
            "The degree-one order-six scalar box-box-R is omitted because the integrated quotient treats it as a total divergence.",
        ],
    }


def build_result_envelope() -> dict[str, Any]:
    return {
        "result_id": "LOCAL_SIX_DERIVATIVE_CURVATURE_QUOTIENT",
        "classical_commit": "UNFROZEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "lifecycle_status": "CLASSIFIED",
        "ghost_number": 0,
        "form_degree": 4,
        "antifield_number": 0,
        "parity": "even",
        "representative": "generated dimension-independent integrated order-six curvature quotient",
        "cohomology_status": "NOT_COMPUTED",
        "descent_status": "NOT_COMPUTED",
        "coefficient_status": "NOT_COMPUTED",
        "residual_projection_status": "NOT_COMPUTED",
        "proof_certificate": (
            "quantum-weyl/local_bv/certificates/"
            "LOCAL_SIX_DERIVATIVE_CURVATURE_QUOTIENT_CERTIFICATE.json"
        ),
        "assumptions": [
            "The ten-dimensional integrated invariant quotient is not H^{0,4}(s|d) and has not yet been specialized by four-dimensional Schouten identities."
        ],
        "notes": (
            "LOCAL-ALGEBRAIC only. Cubic and derivative curvature invariant "
            "infrastructure is classified; BRST closure, exactness, descent, "
            "antifields, anomaly classes, and coefficients remain NOT_COMPUTED."
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
            raise SystemExit("detailed six-derivative certificate is stale")
        if RESULT_PATH.read_text(encoding="utf-8") != result:
            raise SystemExit("common six-derivative result envelope is stale")
    if not args.emit and not args.check:
        print(detailed, end="")
    else:
        print("LOCAL SIX-DERIVATIVE CURVATURE QUOTIENT: EXACT CHECKS PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
