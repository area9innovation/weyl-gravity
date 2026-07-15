"""Emit and reproduce the dimension-four curvature candidate catalogues."""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

from .algebra import canonical_sha256
from .dimension_four_candidates import dimension_four_candidate_analysis
from .tensors import TensorExpression


PACKAGE_ROOT = Path(__file__).resolve().parent
QUANTUM_ROOT = PACKAGE_ROOT.parent
DETAILED_PATH = (
    PACKAGE_ROOT
    / "certificates"
    / "LOCAL_DIMENSION_FOUR_CANDIDATE_CATALOGUE_CERTIFICATE.json"
)
COUNTERTERM_RESULT_PATH = (
    QUANTUM_ROOT / "certificates" / "COUNTERTERM_CANDIDATES_DIMENSION_FOUR.json"
)
ANOMALY_RESULT_PATH = (
    QUANTUM_ROOT / "certificates" / "ANOMALY_CANDIDATES_DIMENSION_FOUR.json"
)
COUNTERTERM_PATH = (
    QUANTUM_ROOT
    / "counterterms"
    / "ghost_number_0"
    / "COUNTERTERM_CANDIDATES.json"
)
ANOMALY_PATH = (
    QUANTUM_ROOT
    / "anomalies"
    / "ghost_number_1"
    / "ANOMALY_CANDIDATES.json"
)
SCHEMA_PATH = PACKAGE_ROOT / "schema" / "dimension_four_candidate_certificate.schema.json"
CATALOGUE_SCHEMA_PATH = PACKAGE_ROOT / "schema" / "candidate_catalogue.schema.json"


def _source_manifest() -> dict[str, str]:
    paths = (
        "algebra.py",
        "brst.py",
        "curvature.py",
        "dimension_four_candidates.py",
        "dimension_four_candidate_certificate.py",
        "hodge.py",
        "horizontal_forms.py",
        "metadata.py",
        "quotient.py",
        "specialization.py",
        "strict_descent.py",
        "tensors.py",
        "weyl_decomposition.py",
        "weyl_target.py",
        "schema/candidate_catalogue.schema.json",
        "schema/dimension_four_candidate_certificate.schema.json",
        "tests/test_dimension_four_candidates.py",
        "tests/test_dimension_four_candidate_certificate.py",
        "tests/test_weyl_target.py",
    )
    return {
        path: hashlib.sha256((PACKAGE_ROOT / path).read_bytes()).hexdigest()
        for path in paths
    }


def _fraction(value: Fraction) -> dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}


def _matrix(rows: tuple[tuple[Fraction, ...], ...]) -> list[list[dict[str, int]]]:
    return [[_fraction(value) for value in row] for row in rows]


def _catalogue(result_id: str, sector: str, candidates: tuple[dict[str, object], ...]) -> dict[str, Any]:
    return {
        "result_id": result_id,
        "classical_commit": "UNFROZEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "status": "CANDIDATES_GENERATED_NOT_COHOMOLOGY",
        "sector": sector,
        "scope": (
            "Antifield-independent four-dimensional curvature densities at "
            "mass dimension four."
        ),
        "candidate_count": len(candidates),
        "candidates": list(candidates),
        "proof_certificate": (
            "quantum-weyl/local_bv/certificates/"
            "LOCAL_DIMENSION_FOUR_CANDIDATE_CATALOGUE_CERTIFICATE.json"
        ),
        "not_computed": [
            "full H^{g,4}(s|d) coboundary quotient and intrinsic Euler anomaly descent",
            "antifield, equation-of-motion, gauge-fixing, Diff, and mixed sectors",
            "one-loop coefficients and QME status",
            "cylinder restriction and residual transfer",
        ],
    }


def build_counterterm_catalogue() -> dict[str, Any]:
    analysis = dimension_four_candidate_analysis()
    return _catalogue(
        "COUNTERTERM_CANDIDATE_CATALOGUE_DIMENSION_FOUR",
        "ghost_number_0",
        analysis["counterterms"],
    )


def build_anomaly_catalogue() -> dict[str, Any]:
    analysis = dimension_four_candidate_analysis()
    return _catalogue(
        "ANOMALY_CANDIDATE_CATALOGUE_DIMENSION_FOUR",
        "ghost_number_1",
        analysis["anomalies"],
    )


def build_certificate() -> dict[str, Any]:
    analysis = dimension_four_candidate_analysis()
    target = analysis["target_analysis"]
    curvature = analysis["quadratic_curvature_analysis"]
    expected_target = {
        "raw_pairing_count": 105,
        "tracefree_ambient_dimension": 2,
        "relation_count": 2,
        "relation_rank": 1,
        "quotient_dimension": 1,
    }
    for parity in ("even", "odd"):
        actual = {name: target[parity][name] for name in expected_target}
        if actual != expected_target:
            raise AssertionError(f"{parity} target-native quotient drifted: {actual}")
    expected_ansatz = {
        "raw_pairing_count": 105,
        "symmetry_canonical_monomial_count": 4,
        "nonzero_unique_bianchi_relation_count": 2,
        "bianchi_relation_rank": 1,
        "quotient_dimension": 3,
        "named_representative_rank": 3,
    }
    actual_ansatz = {name: curvature[name] for name in expected_ansatz}
    if actual_ansatz != expected_ansatz:
        raise AssertionError(f"dimension-four ansatz drifted: {actual_ansatz}")
    if analysis["closed_kernel_dimension"] != 2:
        raise AssertionError("Weyl-closed kernel dimension drifted")
    if target["cotton_dimension_four_scalar_count"] != 0:
        raise AssertionError("a tracefree dimension-four Cotton scalar appeared")

    counterterms = build_counterterm_catalogue()
    anomalies = build_anomaly_catalogue()
    counterterm_ids = [record["class_id"] for record in counterterms["candidates"]]
    anomaly_ids = [record["class_id"] for record in anomalies["candidates"]]
    expected_counterterms = ["CT_C2", "CT_E4", "CT_C_DUAL_C", "CT_BOX_R"]
    expected_anomalies = [
        "ANOM_OMEGA_C2",
        "ANOM_OMEGA_E4",
        "ANOM_OMEGA_C_DUAL_C",
        "ANOM_OMEGA_BOX_R",
    ]
    if counterterm_ids != expected_counterterms or anomaly_ids != expected_anomalies:
        raise AssertionError("candidate identifier ledger drifted")
    diff_descent_statuses = {
        record["class_id"]: record["diff_descent_status"]
        for record in counterterms["candidates"] + anomalies["candidates"]
    }
    if set(diff_descent_statuses.values()) != {"NONZERO_COMPLETE"}:
        raise AssertionError("universal Diff descent ledger drifted")
    intrinsic_statuses = {
        record["class_id"]: record["intrinsic_weyl_descent_status"]
        for record in counterterms["candidates"] + anomalies["candidates"]
    }
    if intrinsic_statuses["ANOM_OMEGA_C2"] != "TRIVIAL":
        raise AssertionError("type-B Weyl descent terminology drifted")
    if intrinsic_statuses["ANOM_OMEGA_E4"] != "PENDING_TYPE_A_TRANSGRESSION":
        raise AssertionError("type-A Weyl descent boundary drifted")

    source_manifest = _source_manifest()
    return {
        "result_id": "LOCAL_DIMENSION_FOUR_CANDIDATE_CATALOGUE_CERTIFICATE",
        "result_state": "CANDIDATES_GENERATED_NOT_COHOMOLOGY",
        "classical_commit": "UNFROZEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "scope": (
            "Generated antifield-independent mass-dimension-four curvature "
            "candidates and target-native even/odd Weyl carriers."
        ),
        "checks": {
            "quadratic_riemann_ansatz": "GENERATED",
            "integrated_weyl_variation_kernel": "VERIFIED",
            "target_native_even_weyl_quotient": "VERIFIED",
            "target_native_odd_dual_weyl_quotient": "VERIFIED",
            "named_even_to_target_native_bridge": "VERIFIED",
            "dual_weyl_epsilon_correspondence": "VERIFIED",
            "hodge_square_signatures": "VERIFIED",
            "dimension_four_cotton_scalar_absence": "VERIFIED",
            "box_r_divergence_witness": "VERIFIED",
            "omega_box_r_trivialization": "VERIFIED_MOD_D",
            "strict_density_diff_descent": "VERIFIED",
            "full_local_bv_cohomology": "NOT_COMPUTED",
        },
        "target_native_quotients": {
            "even": {
                **expected_target,
                "representative_sha256": TensorExpression.monomial(
                    target["even"]["representative"]
                ).canonical_hash(),
                "relations_sha256": canonical_sha256(
                    [relation.canonical_payload() for relation in target["even"]["relations"]]
                ),
            },
            "odd": {
                **expected_target,
                "representative_sha256": TensorExpression.monomial(
                    target["odd"]["representative"]
                ).canonical_hash(),
                "relations_sha256": canonical_sha256(
                    [relation.canonical_payload() for relation in target["odd"]["relations"]]
                ),
            },
            "cotton_dimension_four_scalar_count": 0,
            "cotton_cyclic_relation_sha256": target["cotton_cyclic_relation"].canonical_hash(),
            "weyl_cotton_differential_relation_sha256": target[
                "weyl_cotton_differential_relation"
            ].canonical_hash(),
            "explicit_hodge_companion_sha256": target[
                "explicit_hodge_companion"
            ].canonical_hash(),
            "named_even_weyl_restriction_sha256": analysis[
                "c2_weyl_restriction"
            ].canonical_hash(),
            "euclidean_hodge_square_sha256": target["hodge_square"][
                "euclidean"
            ].canonical_hash(),
            "lorentzian_hodge_square_sha256": target["hodge_square"][
                "lorentzian"
            ].canonical_hash(),
        },
        "generated_ansatz": {
            **expected_ansatz,
            "named_basis": list(analysis["named_basis"]),
            "named_coordinates": _matrix(analysis["named_coordinates"]),
            "local_weyl_variation": _matrix(analysis["local_weyl_variation"]),
            "integrated_weyl_variation": _matrix(
                analysis["integrated_weyl_variation"]
            ),
            "closed_kernel_dimension": 2,
            "closed_kernel": _matrix(analysis["closed_kernel"]),
            "conventional_closed_basis": _matrix(
                analysis["conventional_closed_basis"]
            ),
        },
        "catalogues": {
            "counterterm_result_id": counterterms["result_id"],
            "counterterm_candidate_ids": counterterm_ids,
            "counterterm_catalogue_sha256": canonical_sha256(counterterms),
            "anomaly_result_id": anomalies["result_id"],
            "anomaly_candidate_ids": anomaly_ids,
            "anomaly_catalogue_sha256": canonical_sha256(anomalies),
            "omega_box_r_trivialization_coefficient": _fraction(
                analysis["box_anomaly_trivialization_coefficient"]
            ),
            "box_r_primitive": analysis["box_r_primitive"].canonical_payload(),
        },
        "canonical_hashes": {
            "source_manifest_sha256": canonical_sha256(source_manifest),
            "counterterms_sha256": canonical_sha256(counterterms["candidates"]),
            "anomalies_sha256": canonical_sha256(anomalies["candidates"]),
        },
        "not_computed": counterterms["not_computed"],
        "assumptions": [
            "The catalogue is restricted to antifield-independent curvature densities at mass dimension four.",
            "Closure is tested only in the scalar Weyl sector modulo covariant total derivatives.",
            "The compressed DualWeyl carrier is accepted only after its explicit epsilon-over-two audit.",
            "Only Box R and omega Box R are marked exact, each with an explicit stored primitive; no other candidate is promoted to a local BV class.",
        ],
    }


def _result_envelope(*, result_id: str, ghost_number: int, representative: str) -> dict[str, Any]:
    return {
        "result_id": result_id,
        "classical_commit": "UNFROZEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "lifecycle_status": "CLASSIFIED",
        "ghost_number": ghost_number,
        "form_degree": 4,
        "antifield_number": 0,
        "parity": "mixed",
        "representative": representative,
        "cohomology_status": "NOT_COMPUTED",
        "diff_descent_status": "NONZERO_COMPLETE",
        "intrinsic_weyl_descent_status": "MIXED_BY_CANDIDATE",
        "coefficient_status": "NOT_COMPUTED",
        "residual_projection_status": "NOT_COMPUTED",
        "proof_certificate": (
            "quantum-weyl/local_bv/certificates/"
            "LOCAL_DIMENSION_FOUR_CANDIDATE_CATALOGUE_CERTIFICATE.json"
        ),
        "assumptions": [
            "Antifield-independent curvature sector only; CLASSIFIED refers to the finite candidate catalogue, not H^{g,4}(s|d)."
        ],
        "notes": (
            "The quadratic ansatz and Weyl-closed kernel are generated exactly. "
            "Universal Diff completion is verified. Intrinsic Weyl status and class exactness are resolved per candidate; the complete quotient and coefficients remain NOT_COMPUTED."
        ),
    }


def build_counterterm_result_envelope() -> dict[str, Any]:
    return _result_envelope(
        result_id="COUNTERTERM_CANDIDATES_DIMENSION_FOUR",
        ghost_number=0,
        representative="generated C2, E4, C-dual-C, and Box R counterterm candidates",
    )


def build_anomaly_result_envelope() -> dict[str, Any]:
    return _result_envelope(
        result_id="ANOMALY_CANDIDATES_DIMENSION_FOUR",
        ghost_number=1,
        representative="generated omega times C2, E4, C-dual-C, and Box R anomaly candidates",
    )


def _render(value: dict[str, Any]) -> str:
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs = {
        DETAILED_PATH: _render(build_certificate()),
        COUNTERTERM_RESULT_PATH: _render(build_counterterm_result_envelope()),
        ANOMALY_RESULT_PATH: _render(build_anomaly_result_envelope()),
        COUNTERTERM_PATH: _render(build_counterterm_catalogue()),
        ANOMALY_PATH: _render(build_anomaly_catalogue()),
    }
    if args.emit:
        for path, content in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
    if args.check:
        for path, content in outputs.items():
            if path.read_text(encoding="utf-8") != content:
                raise SystemExit(f"dimension-four candidate artifact is stale: {path}")
    if not args.emit and not args.check:
        print(outputs[DETAILED_PATH], end="")
    else:
        print("LOCAL DIMENSION-FOUR CANDIDATES: EXACT CHECKS PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
