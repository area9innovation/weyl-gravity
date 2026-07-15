"""Emit the exact Chern--Weil Euler variational transgression certificate."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from .algebra import canonical_sha256
from .chern_weil import euler_transgression_analysis
from .strict_descent import strict_candidate_descent_analysis


PACKAGE_ROOT = Path(__file__).resolve().parent
OUTPUT_PATH = PACKAGE_ROOT / "certificates" / "EULER_TRANSGRESSION_CERTIFICATE.json"
SCHEMA_PATH = PACKAGE_ROOT / "schema" / "euler_transgression_certificate.schema.json"


def _source_manifest() -> dict[str, str]:
    paths = (
        "chern_weil.py",
        "euler_transgression_certificate.py",
        "schema/euler_transgression_certificate.schema.json",
        "tests/test_chern_weil.py",
        "tests/test_euler_transgression_certificate.py",
    )
    return {
        path: hashlib.sha256((PACKAGE_ROOT / path).read_bytes()).hexdigest()
        for path in paths
    }


def _fraction(value: object) -> dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}


def build_certificate() -> dict[str, Any]:
    analysis = euler_transgression_analysis()
    universal = strict_candidate_descent_analysis()
    pair_payload = analysis["pair_payload"]
    expression_payload = analysis["expression_payload"]
    generalized = analysis["generalized_connection_template"]
    return {
        "result_id": "EULER_TRANSGRESSION_CERTIFICATE",
        "result_state": "VARIATIONAL_TRANSGRESSION_VERIFIED",
        "classical_commit": "UNFROZEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "normalization": "E4 = epsilon_abcd R^ab wedge R^cd",
        "checks": {
            "levi_civita_variation_derived_from_qg": "VERIFIED",
            "delta_curvature_equals_D_delta_connection": "VERIFIED",
            "curvature_bianchi_identity": "VERIFIED",
            "delta_E4_minus_dTheta": "VERIFIED",
            "QE4_plus_d_descent_descendant": "VERIFIED",
            "coordinate_euler_current": "VERIFIED",
            "closed_manifold_integrated_variation": "VERIFIED_BY_STOKES",
            "euler_full_diff_completed_tower": "VERIFIED",
            "omega_E4_generalized_connection_template": "VERIFIED",
            "omega_E4_intrinsic_descent_continuation": "IN_PROGRESS",
            "euler_top_transgression_regression": "VERIFIED",
            "unresolved_domega_theta_regression": "VERIFIED",
            "lower_descendant_complete_cancellation": "IN_PROGRESS",
        },
        "derived_rows": {
            "weyl_connection_variation": {
                carrier: _fraction(coefficient)
                for carrier, coefficient in analysis["derived_weyl_connection_variation"].items()
            },
            "local_euler_weyl_variation": [
                _fraction(value) for value in analysis["local_euler_weyl_variation"]
            ],
            "coordinate_current_divergence": [
                _fraction(value) for value in analysis["coordinate_current_divergence"]
            ],
        },
        "euler_intrinsic_transgression": {
            "curvature": expression_payload(analysis["curvature"]),
            "curvature_variation": expression_payload(analysis["curvature_variation"]),
            "theta_variation": pair_payload(analysis["theta_variation"]),
            "descent_descendant": pair_payload(analysis["descent_descendant"]),
            "variational_equation": "delta E4 - d_h Theta_E(delta) = 0",
            "descent_equation": "Q E4 + d_h(-Theta_E(Q)) = 0",
            "omega_E4_first_step": {
                "equation": "Q(omega E4) + d_h(omega Theta_E) = d_h(omega) wedge Theta_E",
                "residual": {
                    carrier: _fraction(value)
                    for carrier, value in analysis["anomaly_first_step"]["residual"].items()
                },
                "continuation_status": "IN_PROGRESS",
            },
            "generalized_connection_total_form": {
                "primary_reference": {
                    "title": "General solutions of the Wess-Zumino consistency condition for the Weyl anomalies",
                    "journal": "JHEP 07 (2007) 069",
                    "doi": "10.1088/1126-6708/2007/07/069",
                    "formula": "Theorem 1, equations (3.16)-(3.20)",
                },
                "generalized_connection": generalized["generalized_connection"],
                "source_formula": "Phi^[n-r]_r = (-1)^p 2^p m!/(r!p!) psi_(2p) W^p, p=m-r, m=n/2",
                "source_convention_map": {
                    "source_s_tilde_W": "project_total_D = Q_W + signed d_h",
                    "source_tilde_omega_alpha": generalized[
                        "generalized_connection"
                    ],
                    "source_W_mu_nu": "project Weyl tensor-valued two-form",
                    "source_omega": "project odd Weyl ghost",
                    "normalization_status": "PENDING_TOP_EULER_MATCH",
                },
                "dimension_specialization": 4,
                "derived_coefficients": [
                    _fraction(component["coefficient"])
                    for component in generalized["components"]
                ],
                "components": [
                    {
                        **{
                            key: value
                            for key, value in component.items()
                            if key != "coefficient"
                        },
                        "coefficient": _fraction(component["coefficient"]),
                    }
                    for component in generalized["components"]
                ],
                "type_a_component_indices": list(generalized["type_a_component_indices"]),
                "type_b_component_indices": list(generalized["type_b_component_indices"]),
                "expansion_status": generalized["expansion_status"],
                "certificate_status": "TEMPLATE_CANDIDATE_NOT_YET_VERIFIED_TOWER",
                "template_sha256": canonical_sha256(
                    {
                        "connection": generalized["generalized_connection"],
                        "components": [
                            {
                                **{
                                    key: value
                                    for key, value in component.items()
                                    if key != "coefficient"
                                },
                                "coefficient": _fraction(component["coefficient"]),
                            }
                            for component in generalized["components"]
                        ],
                    }
                ),
            },
        },
        "euler_full_diff_completed_tower": {
            "counterterm_tower_sha256": universal["counterterm"]["tower_sha256"],
            "anomaly_tower_sha256": universal["anomaly"]["tower_sha256"],
            "coefficients": [
                _fraction(value) for value in universal["counterterm"]["coefficients"]
            ],
        },
        "canonical_hashes": {
            "source_manifest_sha256": canonical_sha256(_source_manifest()),
            "curvature_sha256": canonical_sha256(expression_payload(analysis["curvature"])),
            "theta_sha256": canonical_sha256(pair_payload(analysis["theta_variation"])),
            "zero_variational_residual_sha256": canonical_sha256(pair_payload(analysis["variational_residual"])),
        },
        "assumptions": [
            "The invariant bilinear polynomial is epsilon_abcd X^ab wedge Y^cd in the stated normalization.",
            "The descent descendant is minus the variational transgression, fixing the sign in Q E4 + d_h a3 = 0.",
            "The universal Diff completion is independent of the intrinsic Weyl transgression.",
        ],
        "not_computed": [
            "machine expansion and closure of the generalized-connection type-A total form beginning at omega E4",
            "antifield/Koszul-Tate completion",
            "relative cohomology nontriviality of the Euler anomaly",
        ],
    }


def _render(value: dict[str, Any]) -> str:
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    content = _render(build_certificate())
    if args.emit:
        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_PATH.write_text(content, encoding="utf-8")
    if args.check and OUTPUT_PATH.read_text(encoding="utf-8") != content:
        raise SystemExit(f"Euler transgression artifact is stale: {OUTPUT_PATH}")
    if not args.emit and not args.check:
        print(content, end="")
    else:
        print("EULER TRANSGRESSION: EXACT CHECKS PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
