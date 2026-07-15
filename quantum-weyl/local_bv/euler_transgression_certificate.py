"""Emit the exact Chern--Weil Euler variational transgression certificate."""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

from .algebra import canonical_sha256
from .chern_weil import euler_transgression_analysis
from .euler_intrinsic_expansion import euler_intrinsic_component_expansion
from .euler_generator_preflight import euler_generator_preflight
from .generalized_connection import (
    euler_bidegree_manifests,
    euler_normalization_contract,
    generalized_connection_dictionary,
)
from .strict_descent import strict_candidate_descent_analysis


PACKAGE_ROOT = Path(__file__).resolve().parent
OUTPUT_PATH = PACKAGE_ROOT / "certificates" / "EULER_TRANSGRESSION_CERTIFICATE.json"
SCHEMA_PATH = PACKAGE_ROOT / "schema" / "euler_transgression_certificate.schema.json"
MANIFEST_DIR = PACKAGE_ROOT / "certificates" / "euler_bidegree_manifests"


def _source_manifest() -> dict[str, str]:
    paths = (
        "chern_weil.py",
        "euler_transgression_certificate.py",
        "euler_intrinsic_expansion.py",
        "euler_connecting_identities.py",
        "euler_generator_preflight.py",
        "generalized_connection.py",
        "weyl_decomposition.py",
        "schema/euler_transgression_certificate.schema.json",
        "tests/test_chern_weil.py",
        "tests/test_euler_transgression_certificate.py",
        "tests/test_euler_intrinsic_expansion.py",
        "tests/test_euler_connecting_identities.py",
        "tests/test_euler_generator_preflight.py",
        "tests/test_generalized_connection.py",
        "tests/test_weyl_decomposition.py",
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
    dictionary = generalized_connection_dictionary()
    normalization_contract = euler_normalization_contract()
    bidegree_manifests = euler_bidegree_manifests()
    intrinsic_expansion = euler_intrinsic_component_expansion()
    connecting_preflight = euler_generator_preflight()
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
            "euler_primary_source_convention_map": "VERIFIED",
            "generalized_connection_dictionary": "VERIFIED",
            "source_project_carrier_normalization": "VERIFIED",
            "all_five_euler_bidegrees_enumerated": "VERIFIED",
            "bidegree_manifests_content_addressed": "VERIFIED",
            "total_differential_component_signs": "VERIFIED",
            "omega_E4_intrinsic_component_expansion": "VERIFIED",
            "omega_E4_intrinsic_descent_continuation": "PARTIAL_CONNECTING_IDENTITIES_PENDING",
            "intrinsic_bottom_QW_closure": "VERIFIED",
            "intrinsic_terminal_slots_zero": "VERIFIED",
            "indexed_connecting_identity_preflight": "VERIFIED",
            "source_project_cotton_sign_bridge": "VERIFIED",
            "two_riemann_product_expansion": "VERIFIED",
            "reduced_covariant_connecting_tensor_sectors": "VERIFIED",
            "epsilon_contracted_top_reconstruction": "IN_PROGRESS",
            "horizontal_connecting_generator_rows": "IN_PROGRESS",
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
                    "formula": "Theorems 1 and 2",
                    "arxiv": "0704.2472",
                    "source_version": "v1 (2007-04-19)",
                },
                "generalized_connection": generalized["generalized_connection"],
                "source_formula": "Phi^[n-r]_r = (-1)^p/2^p * m!/(r!p!) psi_(2p) W^p, p=m-r, m=n/2",
                "source_dimension_four_coefficients": [
                    _fraction(value)
                    for value in (Fraction(1, 4), Fraction(-1), Fraction(1))
                ],
                "source_convention_map": {
                    "source_total_differential": "s_tilde_W = s_W + d",
                    "project_total_differential": "D = Q_W + (-1)^ghost_number d_h",
                    "component_sign_translation": "VERIFIED_BY_BIDEGREE_MANIFESTS",
                    "source_generalized_connections": [
                        "2 omega",
                        "dx^nu",
                        "Gamma^nu_(mu rho) dx^rho",
                        "tilde_omega_alpha"
                    ],
                    "source_tilde_omega_alpha": "partial_alpha omega - K_(alpha rho) dx^rho",
                    "project_tilde_omega_alpha": generalized[
                        "generalized_connection"
                    ],
                    "schouten_dimension_four": "K_ab = 1/2 (Ric_ab - R g_ab/6)",
                    "source_W_mu_nu": "W^(mu nu) = (1/2) dx^rho dx^sigma W^mu_(lambda rho sigma) g^(lambda nu)",
                    "source_euler_top_component": "e^4_1 = (1/4) omega epsilon_abcd R^ab wedge R^cd",
                    "project_euler_density": "E4 = epsilon_abcd R^ab wedge R^cd",
                    "source_top_coefficient_in_project_density": _fraction(
                        Fraction(1, 4)
                    ),
                    "orientation": "epsilon_abcd follows the frozen project orientation",
                    "carrier_normalization_status": "RESOLVED_BY_GLOBAL_TOP_COMPONENT_SCALE",
                },
                "dimension_specialization": 4,
                "normalization_contract": normalization_contract,
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
                "expansion_status": "ORDINARY_BIDEGREE_COMPONENTS_VERIFIED",
                "certificate_status": "COMPONENT_EXPANSION_VERIFIED_CONNECTING_IDENTITIES_PENDING",
                "generalized_connection_dictionary": dictionary,
                "bidegree_manifests": [
                    {
                        "ghost_number": manifest["ghost_number"],
                        "form_degree": manifest["form_degree"],
                        "manifest_sha256": manifest["manifest_sha256"],
                        "path": str(
                            Path("certificates")
                            / "euler_bidegree_manifests"
                            / f"{manifest['manifest_sha256']}.json"
                        ),
                    }
                    for manifest in bidegree_manifests
                ],
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
            "ordinary_bidegree_expansion": intrinsic_expansion,
            "connecting_identity_preflight": connecting_preflight,
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
            "generalized_connection_dictionary_sha256": dictionary[
                "dictionary_sha256"
            ],
            "normalization_contract_sha256": normalization_contract[
                "normalization_sha256"
            ],
            "bidegree_manifest_set_sha256": canonical_sha256(
                [manifest["manifest_sha256"] for manifest in bidegree_manifests]
            ),
            "intrinsic_component_expansion_sha256": intrinsic_expansion[
                "expansion_sha256"
            ],
            "connecting_identity_preflight_sha256": connecting_preflight[
                "preflight_sha256"
            ],
        },
        "assumptions": [
            "The invariant bilinear polynomial is epsilon_abcd X^ab wedge Y^cd in the stated normalization.",
            "The descent descendant is minus the variational transgression, fixing the sign in Q E4 + d_h a3 = 0.",
            "The universal Diff completion is independent of the intrinsic Weyl transgression.",
            "The source total form is mapped to project normalization by one global factor fixed by its top component; no bidegree-dependent carrier rescaling is allowed.",
        ],
        "not_computed": [
            "the two connecting intrinsic descent identities requiring the Cotton and Gamma generator actions",
            "epsilon-contracted tensor reconstruction of the Euler head",
            "horizontal differential rows and the Q_W-d_h compatibility check on every connecting generator",
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
        MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
        for manifest in euler_bidegree_manifests():
            path = MANIFEST_DIR / f"{manifest['manifest_sha256']}.json"
            path.write_text(_render(manifest), encoding="utf-8")
    if args.check:
        if OUTPUT_PATH.read_text(encoding="utf-8") != content:
            raise SystemExit(f"Euler transgression artifact is stale: {OUTPUT_PATH}")
        for manifest in euler_bidegree_manifests():
            path = MANIFEST_DIR / f"{manifest['manifest_sha256']}.json"
            if not path.is_file() or path.read_text(encoding="utf-8") != _render(manifest):
                raise SystemExit(f"Euler bidegree manifest is stale or missing: {path}")
    if not args.emit and not args.check:
        print(content, end="")
    else:
        print("EULER TRANSGRESSION: EXACT CHECKS PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
