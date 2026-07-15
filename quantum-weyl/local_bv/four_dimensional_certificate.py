"""Reproduce the exact four-dimensional order-six Schouten quotient receipt."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from .algebra import canonical_sha256
from .four_dimensional import four_dimensional_schouten_analysis


PACKAGE_ROOT = Path(__file__).resolve().parent
QUANTUM_ROOT = PACKAGE_ROOT.parent
DETAILED_PATH = (
    PACKAGE_ROOT
    / "certificates"
    / "LOCAL_FOUR_DIMENSIONAL_SCHOUTEN_QUOTIENT_CERTIFICATE.json"
)
RESULT_PATH = (
    QUANTUM_ROOT
    / "certificates"
    / "LOCAL_FOUR_DIMENSIONAL_SCHOUTEN_QUOTIENT.json"
)
SCHEMA_PATH = PACKAGE_ROOT / "schema" / "four_dimensional_certificate.schema.json"


def _source_manifest() -> dict[str, str]:
    paths = (
        "__init__.py",
        "curvature.py",
        "four_dimensional.py",
        "four_dimensional_certificate.py",
        "pairing_orbits.py",
        "quotient.py",
        "six_derivative.py",
        "specialization.py",
        "tensors.py",
        "schema/four_dimensional_certificate.schema.json",
        "tests/test_four_dimensional.py",
        "tests/test_four_dimensional_certificate.py",
    )
    return {
        path: hashlib.sha256((PACKAGE_ROOT / path).read_bytes()).hexdigest()
        for path in paths
    }


def _sector_payload(sector: dict[str, object]) -> dict[str, object]:
    return {
        name: sector[name]
        for name in (
            "basis_dimension",
            "candidate_count",
            "nonzero_candidate_count",
            "unique_nonzero_relation_count",
            "schouten_relation_rank_in_ambient_sector",
            "intrinsic_quotient_dimension_before_schouten",
            "intrinsic_quotient_dimension_after_schouten",
        )
    }


def build_certificate() -> dict[str, Any]:
    analysis = four_dimensional_schouten_analysis()
    expected = {
        "total_candidate_count": 3_328,
        "total_nonzero_candidate_count": 2_992,
        "unique_nonzero_relation_count": 72,
        "schouten_relation_rank_in_ambient_basis": 11,
        "universal_quotient_dimension": 10,
        "four_dimensional_quotient_dimension": 8,
        "schouten_rank_on_universal_quotient": 2,
        "sector_ranks_after_specialization": {
            "R3": 6,
            "nablaR_nablaR": 4,
            "R_nabla2R": 4,
        },
    }
    actual = {name: analysis[name] for name in expected}
    if actual != expected:
        raise AssertionError(f"four-dimensional Schouten ledger drifted: {actual}")
    expected_sectors = {
        "R3": {
            "basis_dimension": 13,
            "candidate_count": 2_496,
            "nonzero_candidate_count": 2_160,
            "unique_nonzero_relation_count": 36,
            "schouten_relation_rank_in_ambient_sector": 5,
            "intrinsic_quotient_dimension_before_schouten": 8,
            "intrinsic_quotient_dimension_after_schouten": 6,
        },
        "nablaR_nablaR": {
            "basis_dimension": 12,
            "candidate_count": 384,
            "nonzero_candidate_count": 384,
            "unique_nonzero_relation_count": 18,
            "schouten_relation_rank_in_ambient_sector": 3,
            "intrinsic_quotient_dimension_before_schouten": 4,
            "intrinsic_quotient_dimension_after_schouten": 4,
        },
        "R_nabla2R": {
            "basis_dimension": 14,
            "candidate_count": 448,
            "nonzero_candidate_count": 448,
            "unique_nonzero_relation_count": 18,
            "schouten_relation_rank_in_ambient_sector": 3,
            "intrinsic_quotient_dimension_before_schouten": 6,
            "intrinsic_quotient_dimension_after_schouten": 6,
        },
    }
    sectors = {
        name: _sector_payload(sector)
        for name, sector in analysis["sector_generation"].items()
    }
    if sectors != expected_sectors:
        raise AssertionError(f"sector Schouten ledgers drifted: {sectors}")

    family = analysis["relation_family"]
    tower = analysis["tower"]
    kernel_expressions = analysis["kernel_expressions"]
    if len(kernel_expressions) != 2:
        raise AssertionError("four-dimensional projection kernel dimension drifted")
    source_manifest = _source_manifest()
    return {
        "result_id": "LOCAL_FOUR_DIMENSIONAL_SCHOUTEN_QUOTIENT_CERTIFICATE",
        "result_state": "DIMENSIONAL_QUOTIENT_VERIFIED",
        "classical_commit": "UNFROZEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "scope": (
            "Parity-even scalar order-six Riemann contractions in spacetime "
            "dimension four, specialized from the exact dimension-independent "
            "integrated quotient by exhaustive five-index antisymmetrization."
        ),
        "checks": {
            "signed_pairing_coordinate_coverage": "VERIFIED",
            "endpoint_selection_exhaustion": "VERIFIED",
            "orbit_first_direct_tensor_crosscheck": "VERIFIED",
            "five_index_schouten_generation": "VERIFIED",
            "relation_family_provenance": "VERIFIED",
            "specialization_projection_surjectivity": "VERIFIED",
            "specialization_kernel_witnesses": "VERIFIED",
            "four_dimensional_integrated_quotient": "VERIFIED",
            "primary_literature_rank_crosscheck": "VERIFIED",
            "tracefree_weyl_specialization": "NOT_COMPUTED",
            "parity_odd_weyl_sector": "NOT_COMPUTED",
            "local_cohomology_H_s_mod_d": "NOT_COMPUTED",
        },
        "generation": {
            **expected,
            "sectors": sectors,
            "relation_family": family.canonical_payload(),
        },
        "specialization": {
            "tower": tower.canonical_payload(),
            "kernel_dimension": len(kernel_expressions),
            "kernel_witnesses": [
                {
                    "expression_sha256": expression.canonical_hash(),
                    "expression": expression.canonical_payload(),
                }
                for expression in kernel_expressions
            ],
        },
        "independent_crosscheck": {
            "reference": "https://arxiv.org/abs/0802.1274",
            "reference_table": "Table 1, order-six cases after Commute and after 4D",
            "reference_dimension_losses": {
                "nonproduct_R3_case_0_0_0": {"Commute": 5, "4D": 3},
                "case_1_1": {"Commute": 4, "4D": 4},
                "case_0_2": {"Commute": 3, "4D": 3},
            },
            "computed_dimension_losses": {
                "R3_including_three_product_classes": {"universal": 8, "4D": 6},
                "derivative_sectors_gain_no_new_dimensional_loss": True,
            },
            "status": "MATCH",
            "role": "INDEPENDENT_CROSSCHECK_NOT_PROOF_INPUT",
        },
        "canonical_hashes": {
            "schouten_relation_family_sha256": canonical_sha256(
                family.canonical_payload()
            ),
            "specialization_tower_sha256": tower.canonical_payload()[
                "tower_sha256"
            ],
            "kernel_witnesses_sha256": canonical_sha256(
                [expression.canonical_payload() for expression in kernel_expressions]
            ),
            "source_manifest_sha256": canonical_sha256(source_manifest),
        },
        "not_computed": [
            "tracefree-Weyl specialization of the four-dimensional quotient",
            "parity-odd single-epsilon invariant enumeration and dual reduction",
            "Weyl BRST variations and bounded ghost-number-zero/one ansatz",
            "antifield/Koszul-Tate descent and H^{g,4}(s|d)",
            "cylinder restriction, anomaly coefficients, QME restoration, and Lorentzian causal products",
        ],
        "assumptions": [
            "Every dimension-dependent scalar identity is generated by antisymmetrizing five distinct contracted index labels in dimension four.",
            "One endpoint from each selected contraction pair is exhaustive modulo the signed tensor-symmetry orbits.",
            "The universal quotient already imposes intrinsic symmetries, Bianchi identities, integration by parts, and the declared-sign covariant commutators.",
            "The eight-dimensional result is an invariant quotient, not H^{0,4}(s|d).",
        ],
    }


def build_result_envelope() -> dict[str, Any]:
    return {
        "result_id": "LOCAL_FOUR_DIMENSIONAL_SCHOUTEN_QUOTIENT",
        "classical_commit": "UNFROZEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "lifecycle_status": "CLASSIFIED",
        "ghost_number": 0,
        "form_degree": 4,
        "antifield_number": 0,
        "parity": "even",
        "representative": "generated four-dimensional integrated order-six Riemann invariant quotient",
        "cohomology_status": "NOT_COMPUTED",
        "descent_status": "NOT_COMPUTED",
        "coefficient_status": "NOT_COMPUTED",
        "residual_projection_status": "NOT_COMPUTED",
        "proof_certificate": (
            "quantum-weyl/local_bv/certificates/"
            "LOCAL_FOUR_DIMENSIONAL_SCHOUTEN_QUOTIENT_CERTIFICATE.json"
        ),
        "assumptions": [
            "The dimension-four Schouten quotient has not yet been specialized to tracefree Weyl tensors or tested for BRST closure."
        ],
        "notes": (
            "LOCAL-ALGEBRAIC only. Exhaustive five-index antisymmetrization "
            "reduces the universal integrated invariant quotient from dimension "
            "10 to 8; this is not a counterterm or anomaly cohomology basis."
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
            raise SystemExit("detailed four-dimensional certificate is stale")
        if RESULT_PATH.read_text(encoding="utf-8") != result:
            raise SystemExit("common four-dimensional result is stale")
    if not args.emit and not args.check:
        print(detailed, end="")
    else:
        print("LOCAL FOUR-DIMENSIONAL SCHOUTEN QUOTIENT: EXACT CHECKS PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
