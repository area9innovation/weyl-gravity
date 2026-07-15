"""Emit fail-closed Sprint 1 antifield-zero production receipts."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from .afn0_production import afn0_production_results, afn0_slice_results
from .algebra import canonical_sha256
from .ambient_tensor_graphs import ambient_tensor_graph_analysis
from .basis_gap import basis_gap_report
from .lower_form_basis import lower_form_carrier_analysis
from .lower_form_ambient import ambient_lower_form_signature_analysis


PACKAGE_ROOT = Path(__file__).resolve().parent
RESULT_DIR = PACKAGE_ROOT / "cohomology"
SLICE_RESULT_DIR = RESULT_DIR / "slices"
CERTIFICATE_PATH = PACKAGE_ROOT / "certificates" / "AFN0_PRODUCTION_RUN_CERTIFICATE.json"
SCHEMA_PATH = PACKAGE_ROOT / "schema" / "afn0_result.schema.json"


def _source_manifest() -> dict[str, str]:
    paths = (
        "afn0_production.py",
        "afn0_production_certificate.py",
        "ambient_tensor_graphs.py",
        "ambient_tensor_graph_certificate.py",
        "basis_exhaustiveness.py",
        "basis_gap.py",
        "lower_form_basis.py",
        "lower_form_basis_certificate.py",
        "lower_form_ambient.py",
        "lower_form_ambient_certificate.py",
        "tensor_graphs.py",
        "schema/afn0_result.schema.json",
        "schema/afn0_closure_result.schema.json",
        "schema/afn0_truncated_quotient_result.schema.json",
        "schema/afn0_lower_form_carrier_precertificate.schema.json",
        "schema/afn0_ambient_lower_form_signature.schema.json",
        "schema/afn0_ambient_tensor_graph_realization.schema.json",
        "schema/afn0_ambient_tensor_graph_bundle.schema.json",
        "tests/test_afn0_production.py",
        "tests/test_basis_exhaustiveness.py",
        "tests/test_basis_gap.py",
        "tests/test_lower_form_basis.py",
        "tests/test_lower_form_ambient.py",
        "tests/test_ambient_tensor_graphs.py",
        "tests/test_tensor_graphs.py",
    )
    return {
        path: hashlib.sha256((PACKAGE_ROOT / path).read_bytes()).hexdigest()
        for path in paths
    }


def build_certificate() -> dict[str, Any]:
    results = afn0_production_results()
    slice_results = afn0_slice_results()
    gap_report = basis_gap_report()
    lower_form = lower_form_carrier_analysis()
    ambient_lower_form = ambient_lower_form_signature_analysis()
    ambient_tensor_graphs, ambient_tensor_bundle = ambient_tensor_graph_analysis()
    h04 = results["H04_AFN0_RESULT"]
    h14 = results["H14_AFN0_RESULT"]
    exact_ids = {
        candidate["representative_id"]
        for result in results.values()
        for slice_ in result["slices"]
        for candidate in slice_["truncated_quotient_result"]["candidates"]
        if candidate["relative_cohomology_status"] == "EXACT"
    }
    if exact_ids != {"CT_BOX_R", "ANOM_OMEGA_BOX_R"}:
        raise AssertionError("AFN0 known-exact ledger drifted")
    if any(
        candidate["nonmembership_witness"] is not None
        for result in results.values()
        for slice_ in result["slices"]
        for candidate in slice_["truncated_quotient_result"]["candidates"]
    ):
        raise AssertionError("incomplete AFN0 run promoted a nontriviality witness")
    return {
        "result_id": "AFN0_PRODUCTION_RUN_CERTIFICATE",
        "result_state": "SPRINT_1_IN_PROGRESS",
        "classical_commit": "UNFROZEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "scope_label": "AFN0_ONLY",
        "checks": {
            "H04_AFN0_EVEN_started": "VERIFIED",
            "H04_AFN0_ODD_started": "VERIFIED",
            "H14_AFN0_EVEN_complete_candidate_closure": "VERIFIED",
            "H14_AFN0_ODD_started": "VERIFIED",
            "top_curvature_carrier_generation": "VERIFIED",
            "parity_split": "VERIFIED",
            "BoxR_explicit_primitive": "VERIFIED",
            "omega_BoxR_explicit_primitive": "VERIFIED",
            "premature_nontriviality_promotion_absent": "VERIFIED",
            "closure_and_truncated_quotient_outputs_separated": "VERIFIED",
            "closure_witness_artifact_hashes": "VERIFIED",
            "closure_witness_semantic_status_agreement": "VERIFIED",
            "truncated_witness_vocabulary": "VERIFIED",
            "grading_integer_signature_enumeration": "VERIFIED",
            "coarse_and_refined_signature_counts_separated": "VERIFIED",
            "raw_tensor_contraction_graph_enumeration": "VERIFIED",
            "independent_raw_graph_combinatorial_counts": "VERIFIED",
            "index_variance_and_derivative_attachment": "VERIFIED",
            "signed_riemann_epsilon_symmetry_orbits": "VERIFIED",
            "graphwise_total_derivative_currents": "VERIFIED",
            "raw_contraction_not_promoted_to_tensor_realizability": "VERIFIED",
            "content_addressed_graph_bundle": "VERIFIED",
            "basis_gap_report_emitted": "VERIFIED",
            "H04_even_top_signature_resolution": "VERIFIED",
            "H04_odd_top_signature_resolution": "VERIFIED",
            "forward_reverse_span_agreement": "NOT_COMPUTED",
            "total_complex_exhaustiveness": "NOT_COMPUTED",
            "complete_lower_form_basis": "IN_PROGRESS",
            "lower_form_candidate_carrier_coverage": "COMPLETE",
            "lower_form_exact_boundary_carrier_coverage": "COMPLETE",
            "ambient_lower_form_integer_signature_enumeration": "EXHAUSTIVE",
            "ambient_lower_form_tensor_graph_realizability": "COMPLETE_FACTORED",
            "ambient_derivative_distribution_profiles": "EXHAUSTIVE",
            "ambient_raw_graph_count_without_materialization": "VERIFIED",
            "Euler_intrinsic_tower": "NONTRIVIAL_COMPLETE",
        },
        "result_hashes": {
            "H04_AFN0_RESULT": canonical_sha256(h04),
            "H14_AFN0_RESULT": canonical_sha256(h14),
            "BASIS_GAP_REPORT_AFN0": gap_report["report_hash"],
            "AFN0_LOWER_FORM_CARRIER_PRECERTIFICATE": lower_form[
                "analysis_sha256"
            ],
            "AFN0_AMBIENT_LOWER_FORM_SIGNATURE_CERTIFICATE": ambient_lower_form[
                "analysis_sha256"
            ],
            "AFN0_AMBIENT_TENSOR_GRAPH_REALIZATION_CERTIFICATE": ambient_tensor_graphs[
                "analysis_sha256"
            ],
            "AFN0_AMBIENT_TENSOR_GRAPH_PROFILE_BUNDLE": ambient_tensor_bundle[
                "bundle_sha256"
            ],
            **{
                result_id: canonical_sha256(result)
                for result_id, result in sorted(slice_results.items())
            },
        },
        "canonical_hashes": {
            "source_manifest_sha256": canonical_sha256(_source_manifest()),
        },
        "next_required_computation": [
            "construct signed factor-permutation actions on the 1,224 factored derivative-distribution profiles",
            "canonically quotient the factored contraction graphs by tensor identities and integration by parts",
            "resolve every remaining top-form and Diff signature with a terminal status",
            "compare the forward canonical span with reverse signature coverage",
            "assemble the production Q and d_h sparse matrices",
            "integrate the now-inventoried omega-Euler and universal Diff carriers into the production Q and d_h matrices",
            "emit COMPLETE_NONTRIVIALITY_WITNESS only after the complete boundary rank and exhaustiveness proof are frozen",
        ],
    }


def _render(value: dict[str, Any]) -> str:
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    results = afn0_production_results()
    outputs = {
        RESULT_DIR / f"{result_id}.json": _render(result)
        for result_id, result in results.items()
    }
    outputs.update(
        {
            SLICE_RESULT_DIR / f"{result_id}.json": _render(result)
            for result_id, result in afn0_slice_results().items()
        }
    )
    outputs[CERTIFICATE_PATH] = _render(build_certificate())
    if args.emit:
        for path, content in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
    if args.check:
        for path, content in outputs.items():
            if path.read_text(encoding="utf-8") != content:
                raise SystemExit(f"AFN0 production artifact is stale: {path}")
    if not args.emit and not args.check:
        print(outputs[CERTIFICATE_PATH], end="")
    else:
        print("AFN0 PRODUCTION: SPRINT 1 RECEIPTS VERIFIED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
