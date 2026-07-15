#!/usr/bin/env python3
"""Emit the first exact REDUCED-MODE Berger arity-two Cartan verdict."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

try:
    from .berger_reduced_mode_cartan import build_verdict
except ImportError:
    from berger_reduced_mode_cartan import build_verdict


TRANSFER_ROOT = Path(__file__).resolve().parent
ROOT = TRANSFER_ROOT.parents[1]
OUTPUT = TRANSFER_ROOT / "certificates" / "BERGER_FIRST_ARITY_TWO_CARTAN_VERDICT.json"
IMPORT_CERTIFICATE = TRANSFER_ROOT / "certificates" / "BERGER_RATIONAL_FIXTURE_Q2_D_IMPORT.json"
UNARY_IMPORT = TRANSFER_ROOT / "certificates" / "BERGER_GAUGE_FIXED_NONMINIMAL_IMPORT.json"
EINSTEIN_INCIDENCE = ROOT / "bridge/certificates/berger_einstein_incidence.json"
EINSTEIN_INCIDENCE_COMMIT = "7e87281c416f4c4f98edfe61ae05829f4b48593a"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _fraction(value) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def _sparse(operator, complex_) -> dict[str, object]:
    entries = []
    for output, left, right in complex_.coordinate_slots(operator.degree):
        value = operator.entries[output][left][right]
        if value:
            entries.append([output, left, right, _fraction(value)])
    coordinates = [_fraction(value) for value in complex_.coordinates(operator)]
    return {
        "degree": operator.degree,
        "coordinate_convention": "graded-symmetric i<=j; odd diagonal omitted",
        "coordinate_count": len(coordinates),
        "coordinate_sha256": _canonical_hash(coordinates),
        "nonzero_entries": entries,
    }


def _source_manifest() -> dict[str, str]:
    paths = (
        "arity_two_cartan.py",
        "berger_rational_fixture_q2_d_import.py",
        "berger_rational_fixture_q2_d_import_certificate.py",
        "schema/berger-rational-fixture-q2-d-import-v1.schema.json",
        "tests/test_berger_rational_fixture_q2_d_import.py",
        "berger_reduced_mode_cartan.py",
        "berger_reduced_mode_cartan_certificate.py",
        "schema/berger-first-arity-two-cartan-verdict-v1.schema.json",
        "tests/test_berger_reduced_mode_cartan.py",
        "../reports/berger-first-arity-two-cartan-verdict.md",
    )
    return {path: _sha256(TRANSFER_ROOT / path) for path in paths}


def build_certificate() -> dict[str, Any]:
    verdict = build_verdict()
    receipt = verdict.import_receipt
    checked_import = json.loads(IMPORT_CERTIFICATE.read_text())
    checked_core = dict(checked_import)
    checked_core.pop("consumer_provenance", None)
    if checked_core != receipt:
        raise ValueError("checked Berger reduced-mode import certificate is stale")
    unary_import = json.loads(UNARY_IMPORT.read_text())
    if (
        unary_import.get("coverage", {}).get("total_rows") != 54
        or unary_import.get("nd2_gate", {}).get("unary_nonminimal_prerequisite_satisfied") is not True
    ):
        raise ValueError("quantum 54-row unary import is not complete")
    incidence = json.loads(EINSTEIN_INCIDENCE.read_text())
    if incidence.get("result_state") != "EXACT_BACKGROUND_NONINCIDENCE_CERTIFIED_TANGENT_EMBEDDING_NOT_APPLICABLE":
        raise ValueError("Berger Einstein-incidence boundary drifted")

    data = verdict.data
    source = verdict.engine_classification.source
    primitive = verdict.primitive
    correction_identity = (
        data.complex.differential(primitive, name="[q1,iota_D_2]").entries
        == source.scaled(-1, name="minus_A_D_2").entries
    )
    if not correction_identity:
        raise AssertionError("Berger exact primitive identity failed")
    source_manifest = _source_manifest()
    rational_q1 = [[_fraction(value) for value in row] for row in data.complex.q1.entries]
    return {
        "schema": "quantum-weyl-berger-first-arity-two-cartan-verdict-v1",
        "result_id": "BERGER_FIRST_ARITY_TWO_CARTAN_VERDICT",
        "result_state": "INTERACTING_CARTAN_EXISTS_ON_CENTERED_REDUCED_MODE_BLOCK",
        "lifecycle_layer": "INTERACTING",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "setting_id": "compact_positive_berger_clock_rational_fixture_stationary_homogeneous",
        "scientific_input": {
            "status": "IMPORTED_EXACT_ACTION_DERIVED_BLOCK",
            "result_id": receipt["result_id"],
            "classical_commit": receipt["classical_source"]["commit"],
            "certificate_sha256": _sha256(IMPORT_CERTIFICATE),
            "synthetic_fixture_used_for_verdict": False,
        },
        "adapter": {
            "scope": "one stationary homogeneous six-row physical-shape block",
            "source_coefficient_ring": "Q",
            "solver_coefficient_ring": "Q",
            "basis_change": "IDENTITY_AFTER_CLASSICAL_RATIONAL_COORDINATE_u",
            "rational_q1": rational_q1,
            "rational_q1_sha256": _canonical_hash(rational_q1),
            "q1_rank": verdict.q1_rank,
            "q2_independent_nonzero_count": receipt["imported_block"]["q2_nonzero_canonical_count"],
            "rational_q2": _sparse(data.q2, data.complex),
            "general_PBW_engine_extended": False,
        },
        "cartan_equation": {
            "source_definition": "A_D^(2)=[q2,iota_D]-L_D^(2)",
            "equation": "[q1,iota_D^(2)]=-A_D^(2)",
            "iota_D": "zero linear operator on the centered D-weight-zero block",
            "L_D": "zero linear operator on the centered D-weight-zero block",
            "L_D_2": "zero: the declared D action is linear and trivial on every retained row",
            "engine_classification": verdict.engine_classification.status,
            "source": _sparse(source, data.complex),
            "binary_verdict": "ADMISSIBLE_EXACT_PRIMITIVE",
            "primitive": {
                **_sparse(primitive, data.complex),
                "operator": "iota_D^(2)=0",
                "D_weight": 0,
                "field_support": [],
                "admissibility": "AUTOMATIC_ZERO_IN_EVERY_HOMOGENEOUS_LINEAR_ADMISSIBILITY_SUBSPACE",
            },
            "obstruction_witness": None,
            "exact_checks": {
                **data.checks(),
                "source_zero": source.is_zero(),
                "primitive_zero": primitive.is_zero(),
                "primitive_identity": correction_identity,
                "primitive_admissible_on_declared_block": True,
            },
        },
        "field_and_weight_content": {
            "D_weight": 0,
            "fields": ["delta_u (rationalized Berger squashing metric mode)", "delta_N (lapse)", "delta_rho (conformal scalar clock amplitude)"],
            "equations": ["E_u", "E_N", "E_rho"],
            "all_row_weights": [0, 0, 0, 0, 0, 0],
            "q2_mixes_metric_lapse_clock": True,
        },
        "physical_interpretation": {
            "degree_zero_cohomology_dimension": 0,
            "degree_one_cohomology_dimension": 0,
            "unreduced_stationary_hessian_inertia": {"positive": 1, "negative": 2, "zero": 0},
            "introduces_negative_physical_direction": False,
            "negative_direction_reason": "the two negative Hessian directions lie in an acyclic rank-three Koszul--Tate block and do not survive as physical cohomology",
            "einstein_extra_weyl_coupling": {
                "status": "NOT_APPLICABLE_AT_NON_EINSTEIN_BERGER_BASE_POINT",
                "coupling_established": False,
                "reason": "the six homogeneous rows have no Einstein/extra-Weyl radiative branch decomposition; the background non-incidence certificate makes a same-base-point Einstein tangent sector not applicable",
            },
        },
        "claim_flags": {
            "BERGER_REDUCED_MODE_ARITY_TWO_CARTAN_EXISTS": True,
            "BERGER_SUPPORT_LOCAL_ARITY_TWO_CARTAN_EXISTS": False,
            "NONZERO_WEIGHT_D_OBSTRUCTION_TESTED": False,
            "EINSTEIN_EXTRA_WEYL_BRANCH_COUPLING_CLASSIFIED": False,
            "NEGATIVE_PHYSICAL_DIRECTION_INTRODUCED": False,
            "ND2_FULL_PHYSICAL_EXECUTION_AUTHORIZED": False,
            "QME_RESTORED": False,
            "LORENTZIAN_CERTIFIED": False,
        },
        "reduced_mode_limitation": "The verdict covers only the stationary SU(2)_L x U(1)_R homogeneous six-row D-weight-zero action block. D is trivial here, so the result cannot test a nonzero-weight obstruction. It omits the other 48 gauge-fixed rows, the support-local polydifferential q2, radiative Einstein/extra-Weyl branch labels, causal/Hadamard data, residual transfer, and quantum corrections.",
        "next_gate": "IMPORT_A_NONZERO_D_WEIGHT_OR_SUPPORT_LOCAL_Q2_BLOCK_AND_REPEAT_THE_EXACT_CARTAN_CLASSIFICATION",
        "provenance": {
            "classical_sources": receipt["classical_source"]["artifacts"],
            "classical_sources_sha256": _canonical_hash(receipt["classical_source"]["artifacts"]),
            "reduced_mode_quantum_import": {"path": str(IMPORT_CERTIFICATE.relative_to(ROOT)), "sha256": _sha256(IMPORT_CERTIFICATE)},
            "unary_quantum_import": {"path": str(UNARY_IMPORT.relative_to(ROOT)), "sha256": _sha256(UNARY_IMPORT)},
            "einstein_incidence": {"commit": EINSTEIN_INCIDENCE_COMMIT, "path": str(EINSTEIN_INCIDENCE.relative_to(ROOT)), "sha256": _sha256(EINSTEIN_INCIDENCE)},
            "source_manifest": source_manifest,
            "source_manifest_sha256": _canonical_hash(source_manifest),
            "schema": "quantum-weyl/transfer/schema/berger-first-arity-two-cartan-verdict-v1.schema.json",
        },
    }


def _render(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    content = _render(build_certificate())
    if args.emit:
        OUTPUT.write_text(content)
    if args.check and OUTPUT.read_text() != content:
        raise SystemExit(f"Berger arity-two Cartan verdict is stale: {OUTPUT}")
    if not args.emit and not args.check:
        print(content, end="")
    else:
        print("BERGER FIRST ARITY-TWO CARTAN: ADMISSIBLE EXACT PRIMITIVE (REDUCED-MODE)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
