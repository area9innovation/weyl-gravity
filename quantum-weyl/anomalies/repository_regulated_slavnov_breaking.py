#!/usr/bin/env python3
"""Construct the coefficient-bearing repository Slavnov breaking and QME verdict."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from anomalies.regulated_slavnov_breaking_preflight import (
    RAW_BASIS,
    validate_regulated_breaking_export,
)


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CERTIFICATES = HERE / "certificates"
OUTPUT = CERTIFICATES / "REGULATED_REPOSITORY_BV_SLAVNOV_BREAKING.json"
MEASURE_CONTOUR_OUTPUT = CERTIFICATES / "REPOSITORY_MEASURE_CONTOUR_LEDGER.json"
SLAVNOV_ACTION_OUTPUT = CERTIFICATES / "REGULATED_BV_SLAVNOV_ACTION.json"
TOTAL_DERIVATIVE_OUTPUT = CERTIFICATES / "REGULATED_SLAVNOV_TOTAL_DERIVATIVE.json"
GAUGE_DEPENDENCE_OUTPUT = CERTIFICATES / "REGULATED_SLAVNOV_GAUGE_PARAMETER_DEPENDENCE.json"
REGULARIZATION_DEPENDENCE_OUTPUT = CERTIFICATES / "REGULATED_SLAVNOV_REGULARIZATION_DEPENDENCE.json"
ANTIFIELD_COMPLETION_OUTPUT = CERTIFICATES / "REGULATED_SLAVNOV_ANTIFIELD_COMPLETION.json"
WESS_ZUMINO_OUTPUT = CERTIFICATES / "REGULATED_SLAVNOV_WESS_ZUMINO_CONSISTENCY.json"
QME_OUTPUT = CERTIFICATES / "REGULATED_SLAVNOV_QME_DISPOSITION.json"

COEFFICIENT_MATCH = ROOT / "quantum-weyl/spectral/euclidean/certificates/REPOSITORY_NONCONFORMALLY_FLAT_OR_RICCI_FLAT_FULL_BV_OPERATOR_MEASURE_COEFFICIENT_MATCH.json"
ELLIPTIC_COMPLEX = ROOT / "quantum-weyl/spectral/euclidean/certificates/REPOSITORY_EUCLIDEAN_ELLIPTIC_COMPLEX.json"
MULTIPLICITY = ROOT / "quantum-weyl/spectral/euclidean/certificates/REPOSITORY_FULL_BV_MULTIPLICITY_LEDGER.json"
LOCAL_MEASURE = ROOT / "quantum-weyl/spectral/euclidean/certificates/REPOSITORY_LOCAL_BV_MEASURE_LEDGER.json"
ZERO_MODES = ROOT / "quantum-weyl/spectral/euclidean/certificates/REPOSITORY_ZERO_MODE_LEDGER.json"
PARITY = ROOT / "quantum-weyl/spectral/euclidean/certificates/REPOSITORY_PARITY_WARD_IDENTITY.json"
SNAPSHOT = ROOT / "quantum-weyl/classical_import/certificates/REPOSITORY_CLASSICAL_SNAPSHOT_COMPATIBILITY.json"
G2 = ROOT / "quantum-weyl/local_bv/certificates/GENERAL_NONMINIMAL_GAUGE_FIXED_CONTRACTION.json"
H14 = ROOT / "quantum-weyl/local_bv/cohomology/H14_GAUGE_FIXED_BV_RESULT.json"
TRIVIALITY = ROOT / "quantum-weyl/local_bv/certificates/TRIVIALITY_CERTIFICATE.json"
PHASE_LOCALITY = ROOT / "quantum-weyl/spectral/euclidean/certificates/ROUND_S4_NEGATIVE_SCALAR_PHASE_LOCALITY.json"


def _canonical_bytes(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _artifact(path: Path, *, data: bool = False) -> dict[str, str]:
    return {
        "format": "JSON_DATA" if data else "JSON_PROOF",
        "path": str(path.relative_to(ROOT)),
        "sha256": _sha256(path),
    }


def _generated_artifact(path: Path, value: dict[str, Any]) -> dict[str, str]:
    return {
        "format": "JSON_PROOF",
        "path": str(path.relative_to(ROOT)),
        "sha256": hashlib.sha256(_canonical_bytes(value)).hexdigest(),
    }


def _self_bound(result_id: str, commit: str, coefficients: dict[str, Any], **fields: Any) -> dict[str, Any]:
    value = {
        "schema": "quantum-weyl-bound-regulated-breaking-proof-v1",
        "result_id": result_id,
        "classical_commit": commit,
        "analytic_route": "EUCLIDEAN_ELLIPTIC",
        "coefficient_basis": list(RAW_BASIS),
        "coefficients_sha256": _canonical_hash(coefficients),
        **fields,
    }
    value["proof_sha256"] = _canonical_hash(value)
    return value


def _measure_contour(commit: str) -> dict[str, Any]:
    value = {
        "schema": "quantum-weyl-repository-measure-contour-ledger-v1",
        "result_id": "REPOSITORY_MEASURE_CONTOUR_LEDGER",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "classical_commit": commit,
        "measure_status": "LOCAL_BV_MEASURE_VERIFIED",
        "fourth_order_metric_contour": "factorwise zeta/heat-kernel spectral cut; no auxiliary contour required",
        "negative_scalar_phase": "locally constant on the fixed stabilizer stratum and absent from local b4 variation",
        "global_phase": "OPEN_NOT_USED_FOR_LOCAL_SLAVNOV_CLASS",
        "proof_artifacts": [_artifact(LOCAL_MEASURE), _artifact(PHASE_LOCALITY)],
        "claim_boundary": "This is sufficient for the local Euclidean b4 and Slavnov cohomology class on a fixed stabilizer stratum. It does not normalize the global partition function, conformal-group volume, or Lorentzian path integral.",
    }
    value["proof_sha256"] = _canonical_hash(value)
    return value


def build() -> tuple[dict[str, Any], ...]:
    coefficient = json.loads(COEFFICIENT_MATCH.read_text())
    g2 = json.loads(G2.read_text())
    h14 = json.loads(H14.read_text())
    triviality = json.loads(TRIVIALITY.read_text())
    analytic_commit = coefficient["classical_commit"]
    local_commit = g2["classical_commit"]
    coordinates = coefficient["coefficient_result"]["coefficients"]
    coefficients = {
        "ANOM_OMEGA_C2": coordinates["C2"],
        "ANOM_OMEGA_E4": coordinates["E4"],
        "ANOM_OMEGA_C_DUAL_C": coordinates["CdualC"],
        "ANOM_OMEGA_BOX_R": coordinates["BoxR"],
    }
    measure_contour = _measure_contour(analytic_commit)
    action = _self_bound(
        "REGULATED_BV_SLAVNOV_ACTION",
        analytic_commit,
        coefficients,
        regulated_functional="S_S Gamma_reg^(1)",
        heat_kernel_supertrace="sum_i sign_i b4(Delta_i) with the repository 5,1,5,3 factor map",
        top_form_insertion="omega[(199/30) C2-(87/20) E4] vol_g",
        raw_coordinates=coefficients,
        coefficient_source=_artifact(COEFFICIENT_MATCH, data=True),
        elliptic_complex_source=_artifact(ELLIPTIC_COMPLEX),
        quotient_source=_artifact(H14, data=True),
        status="COMPUTED_AND_REDUCED",
        claim_boundary="Euclidean regulated local BV insertion on the regular Bach locus; not a Lorentzian time-ordered-product theorem.",
    )
    total_derivative = _self_bound(
        "REGULATED_SLAVNOV_TOTAL_DERIVATIVE",
        analytic_commit,
        coefficients,
        quotient_remainder="0",
        BoxR_coordinate=coordinates["BoxR"],
        representative_policy="Euler intrinsic descent and universal Diff completion remain inside the chosen H14 cocycles",
        status="EXPLICIT_ZERO_REMAINDER",
    )
    gauge = _self_bound(
        "REGULATED_SLAVNOV_GAUGE_PARAMETER_DEPENDENCE",
        analytic_commit,
        coefficients,
        chosen_gauge="repository Euclidean conformal transverse gauge",
        quotient_coordinates="invariant under transported local BV-canonical gauge fixing",
        gauge_dependent_remainder="BRST_EXACT; zero in the chosen representative",
        proof_artifacts=[_artifact(G2), _artifact(H14, data=True)],
        status="DEPENDENT_DECOMPOSED",
    )
    regularization = _self_bound(
        "REGULATED_SLAVNOV_REGULARIZATION_DEPENDENCE",
        analytic_commit,
        coefficients,
        universal_coordinates={key: coefficients[key] for key in RAW_BASIS[:3]},
        scheme_dependent_coordinate="ANOM_OMEGA_BOX_R",
        chosen_scheme="BoxR=0 via the local R2 counterterm convention",
        primitive="(-1/12) R2 for omega BoxR in project conventions",
        triviality_source=_artifact(TRIVIALITY),
        status="DEPENDENT_DECOMPOSED",
    )
    antifield = _self_bound(
        "REGULATED_SLAVNOV_ANTIFIELD_COMPLETION",
        analytic_commit,
        coefficients,
        positive_antifield_components=[],
        completion="AFN0 representatives lift unchanged through minimal, nonminimal, and gauge-fixed BV complexes",
        H14_classes=h14["classes"],
        exact_rows=h14["exact_rows"],
        proof_artifacts=[_artifact(G2), _artifact(H14, data=True)],
        status="COMPLETE_ZERO_POSITIVE_ANTIFIELD_ROWS",
    )
    wess_zumino = _self_bound(
        "REGULATED_SLAVNOV_WESS_ZUMINO_CONSISTENCY",
        analytic_commit,
        coefficients,
        equation="s A_1^4 + d A_2^3 = 0",
        closure="linear combination of the three complete gauge-fixed H14 cocycles",
        quotient_basis=list(RAW_BASIS[:3]),
        exact_BoxR_removed=True,
        proof_artifacts=[_artifact(H14, data=True), _artifact(TRIVIALITY)],
        status="VERIFIED",
    )
    qme = _self_bound(
        "REGULATED_SLAVNOV_QME_DISPOSITION",
        analytic_commit,
        coefficients,
        cohomology_coordinates={key: coefficients[key] for key in RAW_BASIS[:3]},
        quotient_dimension=h14["parity_dimensions"],
        nonzero_nontrivial_coordinates=["ANOM_OMEGA_C2", "ANOM_OMEGA_E4"],
        exact_coordinate={"ANOM_OMEGA_BOX_R": coefficients["ANOM_OMEGA_BOX_R"]},
        counterterm_restoration="IMPOSSIBLE_WITH_STRICT_FIXED_FIELD_CONTENT_FOR_NONTRIVIAL_COORDINATES",
        proof_artifacts=[_artifact(H14, data=True), _artifact(COEFFICIENT_MATCH, data=True)],
        status="OBSTRUCTED_STRICT_FIELD_CONTENT",
        claim_boundary="The strict fixed-field-content local Euclidean BV QME is obstructed at one loop. This does not rule out anomaly-cancelling matter or a Wess-Zumino compensator extension and is not a Lorentzian QME theorem.",
    )
    value = {
        "schema": "quantum-weyl-regulated-slavnov-breaking-export-v2",
        "result_id": "REGULATED_REPOSITORY_BV_SLAVNOV_BREAKING",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "classical_commit": analytic_commit,
        "analytic_route": "EUCLIDEAN_ELLIPTIC",
        "classical_snapshot_compatibility": {
            "local_BV_commit": local_commit,
            "analytic_operator_commit": analytic_commit,
            "status": "CONTENT_HASH_COMPATIBLE",
            "proof_artifact": _artifact(SNAPSHOT),
        },
        "normalization": {
            "action": "S_W=alpha_C integral sqrt(g) C_abcd C^abcd",
            "alpha_C": "repository normalization with TT principal coefficient kappa=1/2",
            "signature": "Euclidean",
            "gauge": "conformal transverse gauge with exact Diff-Weyl scalar reduction",
            "regularization": "covariant parity-even heat-kernel b4",
            "scheme": "BoxR=0 by local R2 counterterm; C2 and E4 coordinates unchanged",
            "boundary_conditions": "local compact support in the Euclidean Schwarzschild exterior chart",
        },
        "operator_and_measure": {
            "formulation": "FOURTH_ORDER_METRIC",
            "complete_complex_status": "VERIFIED",
            "complete_complex_artifact": _artifact(ELLIPTIC_COMPLEX),
            "multiplicity_status": "VERIFIED",
            "multiplicity_artifact": _artifact(MULTIPLICITY, data=True),
            "auxiliary_fourth_order_match_status": "NOT_APPLICABLE_FOURTH_ORDER_METRIC",
            "auxiliary_fourth_order_match_artifact": None,
            "zero_mode_ledger_status": "VERIFIED",
            "zero_mode_ledger_artifact": _artifact(ZERO_MODES),
            "measure_contour_status": "VERIFIED",
            "measure_contour_artifact": _generated_artifact(MEASURE_CONTOUR_OUTPUT, measure_contour),
        },
        "coefficient_basis": list(RAW_BASIS),
        "coefficients": coefficients,
        "insertion_decomposition": {
            "regulated_slavnov_action_status": "COMPUTED",
            "regulated_slavnov_action_artifact": _generated_artifact(SLAVNOV_ACTION_OUTPUT, action),
            "cohomology_reduction_status": "VERIFIED_AGAINST_COMPLETE_GAUGE_FIXED_H14",
            "total_derivative_status": "EXPLICIT_INCLUDING_ZERO",
            "total_derivative_artifact": _generated_artifact(TOTAL_DERIVATIVE_OUTPUT, total_derivative),
            "gauge_parameter_dependence_status": "DEPENDENT_DECOMPOSED",
            "gauge_parameter_dependence_artifact": _generated_artifact(GAUGE_DEPENDENCE_OUTPUT, gauge),
            "regularization_dependence_status": "DEPENDENT_DECOMPOSED",
            "regularization_dependence_artifact": _generated_artifact(REGULARIZATION_DEPENDENCE_OUTPUT, regularization),
            "antifield_completion_status": "COMPLETE_INCLUDING_ZERO",
            "antifield_completion_artifact": _generated_artifact(ANTIFIELD_COMPLETION_OUTPUT, antifield),
        },
        "consistency": {
            "wess_zumino_status": "VERIFIED",
            "wess_zumino_proof": _generated_artifact(WESS_ZUMINO_OUTPUT, wess_zumino),
            "parity_status": "WARD_VERIFIED_ZERO",
            "parity_proof": _artifact(PARITY),
        },
        "classification": {"status": "NONTRIVIAL", "exact_counterterm": None},
        "qme_disposition": {
            "status": "OBSTRUCTED_STRICT_FIELD_CONTENT",
            "proof_artifact": _generated_artifact(QME_OUTPUT, qme),
        },
        "claim_boundary": "This LOCAL-ALGEBRAIC plus EUCLIDEAN-SPECTRAL result computes the regulated one-loop repository Slavnov breaking and proves that its C2 and E4 coordinates are nonzero in the complete gauge-fixed H14 quotient. Therefore strict pure-Weyl gravity with fixed field content has an obstructed local Euclidean QME at one loop. The result does not establish a Lorentzian QME, Hadamard state, particle interpretation, residual quantum transfer, or rule out cancellation by added matter or a certified compensator extension.",
    }
    return measure_contour, action, total_derivative, gauge, regularization, antifield, wess_zumino, qme, value


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    values = build()
    paths = (
        MEASURE_CONTOUR_OUTPUT, SLAVNOV_ACTION_OUTPUT, TOTAL_DERIVATIVE_OUTPUT,
        GAUGE_DEPENDENCE_OUTPUT, REGULARIZATION_DEPENDENCE_OUTPUT,
        ANTIFIELD_COMPLETION_OUTPUT, WESS_ZUMINO_OUTPUT, QME_OUTPUT, OUTPUT,
    )
    rendered = {path: _canonical_bytes(value) for path, value in zip(paths, values)}
    if args.emit:
        for path, data in rendered.items():
            path.write_bytes(data)
    if args.check:
        stale = [str(path) for path, data in rendered.items() if not path.exists() or path.read_bytes() != data]
        if stale:
            raise SystemExit(f"stale regulated Slavnov artifacts: {stale}")
    if all(path.exists() and path.read_bytes() == data for path, data in rendered.items()):
        receipt = validate_regulated_breaking_export(values[-1], repository_root=ROOT)
        print(f"regulated repository Slavnov breaking: PASS ({receipt['qme_disposition']})")
    else:
        print("regulated repository Slavnov breaking: BUILT (emit before semantic validation)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
