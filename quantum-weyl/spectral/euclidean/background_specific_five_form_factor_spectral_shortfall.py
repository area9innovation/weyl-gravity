#!/usr/bin/env python3
"""Certify the first missing global datum for a background-specific evaluation."""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERTIFICATE = (
    HERE
    / "certificates/BACKGROUND_SPECIFIC_FIVE_FORM_FACTOR_SPECTRAL_REALIZATION_SHORTFALL.json"
)
SCHEMA = (
    HERE
    / "schema/background-specific-five-form-factor-spectral-realization-shortfall-v1.schema.json"
)
EXPECTED_RESOLVENT = (
    HERE
    / "certificates/SCALAR_FLAT_BERGER_S1_S3_PRIMED_SCHUR_RESOLVENT.json"
)

INPUTS = {
    "independent_family_audit": {
        "path": "quantum-weyl/spectral/euclidean/certificates/"
        "PARAMETERIZED_PARITY_EVEN_FIVE_FORM_FACTOR_FAMILY_INDEPENDENT_AUDIT.json",
        "result_id": "PARAMETERIZED_PARITY_EVEN_FIVE_FORM_FACTOR_FAMILY_INDEPENDENT_AUDIT",
        "sha256": "254670931510a3d70a63556bd4734f3ce32486ad0d810143f04e88756cff7aaf",
    },
    "Schur_resummation": {
        "path": "quantum-weyl/spectral/euclidean/certificates/"
        "GENERIC_BACKGROUND_GHOST_LONGITUDINAL_SCHUR_RESUMMATION.json",
        "result_id": "GENERIC_BACKGROUND_GHOST_LONGITUDINAL_SCHUR_RESUMMATION",
        "sha256": "b40ec3a8bd3a21d8e0ece7c98f98e1776e8c47d557b8c8b5427e422b60c65a78",
    },
    "Schur_scale": {
        "path": "quantum-weyl/spectral/euclidean/certificates/"
        "GENERIC_BACKGROUND_GHOST_SCHUR_WEIGHTED_TRACE_SCALE.json",
        "result_id": "GENERIC_BACKGROUND_GHOST_SCHUR_WEIGHTED_TRACE_SCALE",
        "sha256": "8073ad3800d4ad9662232769efeb45971e49b5eaf1f4b933714245d85771bd1d",
    },
    "round_holdout": {
        "path": "quantum-weyl/spectral/euclidean/certificates/"
        "ROUND_S4_GHOST_SCHUR_FINITE_WEIGHTED_TRACES.json",
        "result_id": "ROUND_S4_GHOST_SCHUR_FINITE_WEIGHTED_TRACES",
        "sha256": "b16768333e62f624720130d1c922b42772f10bf7ad10ee1ac27832c847588591",
    },
    "product_holdout": {
        "path": "quantum-weyl/spectral/euclidean/certificates/"
        "PRODUCT_S2_S2_GHOST_SCHUR_SPECTRAL_CARRIER.json",
        "result_id": "PRODUCT_S2_S2_GHOST_SCHUR_SPECTRAL_CARRIER",
        "sha256": "e7337ea8bd7fa3f06b6d0d965d0da4e64ce980ff987465755cc4187e2d4cfeee",
    },
    "product_full_BV_boundary": {
        "path": "quantum-weyl/spectral/euclidean/certificates/"
        "PRODUCT_S2_S2_FULL_BV_JOIN_BOUNDARY.json",
        "result_id": "PRODUCT_S2_S2_FULL_BV_JOIN_BOUNDARY",
        "sha256": "4de9509d60a8f899fd2b6a2aa708c436598097db4cddb3e377135bc5bff24dcc",
    },
    "Berger_geometry_source": {
        "path": "d_quotient_classical/backreacted_clock/positive_berger_clock.py",
        "result_id": None,
        "sha256": "53832afdc1703ea82efaf34a3ab9324d87ee5db4fc35d4c4ae3932a96b09da7d",
    },
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _fraction(value: Fraction) -> dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}


def _validate_inputs() -> dict[str, dict[str, Any]]:
    imported: dict[str, dict[str, Any]] = {}
    for name, reference in INPUTS.items():
        path = ROOT / reference["path"]
        if not path.is_file() or _sha256(path) != reference["sha256"]:
            raise AssertionError(f"input drift: {name}")
        if reference["result_id"] is not None:
            payload = json.loads(path.read_text())
            if payload["result_id"] != reference["result_id"]:
                raise AssertionError(f"result-id drift: {name}")
        imported[name] = dict(reference)
    return imported


def build() -> dict[str, Any]:
    imports = _validate_inputs()
    if EXPECTED_RESOLVENT.exists():
        raise AssertionError(
            "the declared missing Berger resolvent now exists; rerun its receiver"
        )

    # Closed Berger formulas at a=1,c=2:
    # Ric=diag(0,(2a^2-c^2)/(2a^4),(2a^2-c^2)/(2a^4),c^2/(2a^4)).
    ricci = [Fraction(0), Fraction(-1), Fraction(-1), Fraction(2)]
    scalar = sum(ricci)
    ricci_squared = sum(entry * entry for entry in ricci)
    weyl_squared = Fraction(4 * (1 - 4) ** 2, 3)
    if (scalar, ricci_squared, weyl_squared) != (
        Fraction(0),
        Fraction(6),
        Fraction(12),
    ):
        raise AssertionError("scalar-flat Berger specialization drifted")

    audit = json.loads(
        (ROOT / INPUTS["independent_family_audit"]["path"]).read_text()
    )
    kernel_dimension = audit["global_completion_audit"][
        "universal_combination_kernel_dimension"
    ]
    if kernel_dimension != 0:
        raise AssertionError("independent family audit no longer forces global data")

    return {
        "$schema": "../schema/background-specific-five-form-factor-spectral-realization-shortfall-v1.schema.json",
        "schema": "quantum-weyl-background-specific-five-form-factor-spectral-realization-shortfall-v1",
        "result_id": "BACKGROUND_SPECIFIC_FIVE_FORM_FACTOR_SPECTRAL_REALIZATION_SHORTFALL",
        "source_commit": "ed265d70c",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "imports": imports,
        "candidate_background": {
            "background_id": "EUCLIDEAN_SCALAR_FLAT_BERGER_S1_S3_A1_C2",
            "manifold": "S1_(length 2*pi) x SU(2)",
            "metric": "g=dtheta^2+sigma1^2+sigma2^2+4 sigma3^2",
            "Maurer_Cartan_convention": (
                "[e1,e2]=2e3, [e2,e3]=(1/2)e1, [e3,e1]=(1/2)e2"
            ),
            "dimension": 4,
            "signature": "Euclidean",
            "orientation": "dtheta wedge sigma1 wedge sigma2 wedge sigma3",
            "boundary": "EMPTY",
            "compact": True,
            "a": _fraction(Fraction(1)),
            "c": _fraction(Fraction(2)),
            "ricci_orthonormal_diagonal": [_fraction(value) for value in ricci],
            "scalar_curvature": _fraction(scalar),
            "ricci_squared": _fraction(ricci_squared),
            "weyl_squared": _fraction(weyl_squared),
            "non_Einstein": True,
            "non_conformally_flat": True,
            "reference_scale": "mu_0=1 in a^(-1) units",
            "candidate_contour": (
                "Q=Delta_0+Pi_0 positive; det3/log use the Agmon ray "
                "exp(i*pi/2) R_+ and the phase continuous from S_L(t)=I+tK; "
                "the spectral payload must certify primed invertibility and crossings"
            ),
        },
        "local_scale_rows": {
            "Wres_K_density_without_(4pi)^-2": _fraction(Fraction(8, 3)),
            "Wres_K2_density_without_(4pi)^-2": _fraction(Fraction(4, 9)),
            "dlogmu_logDet3_density_without_(4pi)^-2": _fraction(
                Fraction(22, 9)
            ),
            "status": "EXACT_LOCAL_ROWS_ONLY",
        },
        "candidate_inventory": [
            {
                "background": "flat T4",
                "complete_elementary_spectrum": True,
                "scalar_flat": True,
                "Schur_sensitive_curvature_rank": 0,
                "terminal_status": "DEGENERATE_CANNOT_SELECT_AFFINE_PARAMETERS",
            },
            {
                "background": "round S4",
                "complete_reference_Schur_rows": True,
                "scalar_flat": False,
                "terminal_status": "SPECIAL_HOLDOUT_NOT_RECEIVER_DATUM",
            },
            {
                "background": "S2(1) x S2(2)",
                "complete_product_mode_formula": True,
                "scalar_flat": False,
                "same_background_full_BV_join": False,
                "terminal_status": "SPECIAL_HOLDOUT_NOT_RECEIVER_DATUM",
            },
            {
                "background": "Euclidean scalar-flat Berger S1 x S3 at a=1,c=2",
                "exact_metric_and_curvature": True,
                "scalar_flat": True,
                "Schur_sensitive_curvature_rank": "NONZERO",
                "complete_primed_Schur_resolvent": False,
                "terminal_status": "FIRST_ANALYTIC_CARRIER_MISSING",
            },
        ],
        "receiver_audit": {
            "metric_content_addressed": True,
            "compact_oriented_boundaryless": True,
            "scalar_flat_exact": True,
            "nonzero_Ricci_and_Weyl": True,
            "reference_scale_declared": True,
            "complete_primed_resolvent_or_spectral_measure": False,
            "normalized_zero_mode_projectors": False,
            "insertion_eigenprojectors_through_third_variation": False,
            "certified_analytic_continuation_or_tail": False,
            "five_background_specific_functions_evaluated": False,
            "special_background_interpolation_used": False,
        },
        "first_missing_spectral_theorem": {
            "result_id": "SCALAR_FLAT_BERGER_S1_S3_PRIMED_SCHUR_RESOLVENT",
            "expected_path": (
                "quantum-weyl/spectral/euclidean/certificates/"
                "SCALAR_FLAT_BERGER_S1_S3_PRIMED_SCHUR_RESOLVENT.json"
            ),
            "present": False,
            "operator": "S_L=I+(1/3) Delta_0^(-1) delta W d",
            "required_blocks": [
                "Fourier n and SU(2) representation (j,m) block matrices for Delta_0 and delta W d",
                "self-adjoint domains and the normalized primed scalar/vector projectors",
                "all zero and matched zero-pole modes with finite determinant factors",
                "spectral eigenprojectors and derivative-insertion matrix elements through third metric variation",
                "uniform high-mode estimates supporting det3 and weighted-trace continuation",
                "certified interval or exact evaluation of the finite trace rows at mu_0",
                "orientation, phase and contour covariance under the declared real parity-even regulator",
            ],
            "why_first": (
                "the metric already supplies exact nonzero local curvature rows, but "
                "the independently frozen zero-dimensional universal kernel makes "
                "the smoothing-sensitive primed spectral datum mandatory before "
                "any finite background-specific coordinate can be selected"
            ),
        },
        "shortfall_theorem": {
            "status": "NO_TRACTABLE_REPOSITORY_DATUM_MEETS_RECEIVER",
            "universal_kernel_dimension": kernel_dimension,
            "candidate_metric_passes_geometric_gate": True,
            "expected_resolvent_absent": True,
            "background_specific_evaluation_authorized": False,
            "minimal_external_request": (
                "planning/forge-requests/scalar-flat-berger-spectral-measure.json"
            ),
        },
        "claim_flags": {
            "EXACT_SCALAR_FLAT_NONTRIVIAL_COMPACT_CANDIDATE_SELECTED": True,
            "FIRST_MISSING_GLOBAL_SPECTRAL_OBJECT_IDENTIFIED": True,
            "BACKGROUND_SPECIFIC_FIVE_FUNCTION_VALUES_COMPUTED": False,
            "SPECIAL_BACKGROUND_INTERPOLATION_USED": False,
            "UNIVERSAL_TABLE_PROMOTED": False,
            "QME_OR_LORENTZIAN_PROMOTED": False,
        },
        "claim_boundary": (
            "This LOCAL-ALGEBRAIC/EUCLIDEAN-SPECTRAL shortfall theorem selects "
            "an exact compact scalar-flat non-Einstein, non-conformally-flat "
            "Berger product and proves the first missing receiver object is its "
            "complete primed Schur resolvent with insertion eigenprojectors and "
            "certified finite-trace continuation. It computes only local residue "
            "and scale densities. It does not compute the five finite functions, "
            "a universal table, Gamma1/Q1, a QME, or any Lorentzian, Hadamard, "
            "state, particle, scattering or unitarity result."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build()
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not CERTIFICATE.is_file() or CERTIFICATE.read_text() != rendered:
            raise AssertionError("certificate drift")
    else:
        CERTIFICATE.write_text(rendered)
    print("BACKGROUND-SPECIFIC FIVE-FORM-FACTOR SPECTRAL SHORTFALL: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
