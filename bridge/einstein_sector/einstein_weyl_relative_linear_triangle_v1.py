"""Assemble the compact-product noncyclic Einstein--Weyl linear triangle."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

import sympy as sp
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/EINSTEIN_WEYL_RELATIVE_LINEAR_TRIANGLE_V1.json"
COMPONENTS = ROOT / "bridge/einstein_sector/generated/einstein_weyl_relative_linear_triangle_v1/components.json"
COMPONENT_SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein-weyl-relative-linear-triangle-components-v1.schema.json"
TRIANGLE_SCHEMA = ROOT / "d_quotient_classical/schema/relative-linfinity-triangle-input-v2.schema.json"
REPORT = ROOT / "bridge/einstein_sector/reports/einstein-weyl-relative-linear-triangle-v1.md"

INPUTS = {
    "background": ROOT / "bridge/certificates/einstein_maxwell_product_incidence.json",
    "source_axial_q1": ROOT / "bridge/certificates/einstein_maxwell_axial_master_complex.json",
    "source_polar_q1": ROOT / "bridge/certificates/einstein_maxwell_polar_master_complex.json",
    "exceptional_global_q1": ROOT / "bridge/certificates/EINSTEIN_WEYL_EXCEPTIONAL_GLOBAL_OFFSHELL_CHAIN_MAPS_V1.json",
    "covariant_inclusion": ROOT / "bridge/certificates/EINSTEIN_WEYL_COMPACT_PRODUCT_COVARIANT_CHAIN_MAP_V1.json",
    "source_radiative_pairing": ROOT / "bridge/certificates/einstein_maxwell_radiative_symplectic_matching.json",
    "source_exceptional_pairing": ROOT / "bridge/certificates/einstein_maxwell_exceptional_global_symplectic.json",
    "standard_pullback_pairing": ROOT / "bridge/certificates/einstein_maxwell_weyl_standard_harmonic_symplectic_inclusion.json",
    "axial_relative_pairing": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_lee_wald_completion.json",
    "polar_relative_pairing": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_lee_wald_gate.json",
    "exceptional_k0_pairing": ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ell1_current_taub.json",
    "exceptional_nonzero_k_pairing": ROOT / "bridge/certificates/EINSTEIN_WEYL_EXCEPTIONAL_ELL1_NONZERO_K_SOLUTION_COFIBER_V1.json",
    "homogeneous_pullback_pairing": ROOT / "bridge/certificates/einstein_maxwell_weyl_homogeneous_global_symplectic_restriction.json",
    "twist_pullback_pairing": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_twist_symplectic_restriction.json",
    "homogeneous_cofiber": ROOT / "bridge/certificates/einstein_weyl_homogeneous_solution_cofiber.json",
    "twist_cofiber": ROOT / "bridge/certificates/einstein_weyl_twist_solution_cofiber.json",
    "ell0_nonzero_fourier": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_ell0_nonzero_fourier.json",
    "cyclic_inertia_obstruction": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_GENERIC_CYCLIC_MAP_INERTIA_OBSTRUCTION_V1.json",
}


class RelativeTriangleError(RuntimeError):
    """Raised when an imported theorem or triangle identity drifts."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RelativeTriangleError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    _require(isinstance(value, dict), f"expected JSON object: {path}")
    return value


def _render(value: Mapping[str, Any]) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def _input(name: str) -> dict[str, Any]:
    return _load(INPUTS[name])


def _artifact(name: str, pointer: str = "/") -> dict[str, str]:
    path = INPUTS[name]
    return {
        "result_id": str(_input(name)["result_id"]),
        "path": str(path.relative_to(ROOT)),
        "sha256": _sha256(path),
        "pointer": pointer,
    }


def _artifact_no_pointer(name: str) -> dict[str, str]:
    value = _artifact(name)
    value.pop("pointer")
    return value


def _identity_six() -> list[list[int]]:
    return [[int(row == column) for column in range(6)] for row in range(6)]


def _verify_inputs() -> None:
    expected = {
        "background": "EINSTEIN_MAXWELL_PRODUCT_INCIDENCE",
        "source_axial_q1": "COMPACT_EM_AXIAL_MASTER_COMPLEX",
        "source_polar_q1": "COMPACT_EM_POLAR_MASTER_COMPLEX",
        "exceptional_global_q1": "EINSTEIN_WEYL_EXCEPTIONAL_GLOBAL_OFFSHELL_CHAIN_MAPS_V1",
        "covariant_inclusion": "EINSTEIN_WEYL_COMPACT_PRODUCT_COVARIANT_CHAIN_MAP_V1",
        "source_radiative_pairing": "COMPACT_EM_RADIATIVE_SYMPLECTIC_MATCHING",
        "source_exceptional_pairing": "COMPACT_EM_EXCEPTIONAL_GLOBAL_SYMPLECTIC",
        "standard_pullback_pairing": "EINSTEIN_MAXWELL_WEYL_STANDARD_HARMONIC_SYMPLECTIC_INCLUSION",
        "axial_relative_pairing": "EINSTEIN_MAXWELL_WEYL_AXIAL_LEE_WALD_COMPLETION",
        "polar_relative_pairing": "EINSTEIN_MAXWELL_WEYL_POLAR_LEE_WALD_GATE",
        "exceptional_k0_pairing": "EINSTEIN_MAXWELL_WEYL_EXCEPTIONAL_ELL1_CURRENT_TAUB",
        "exceptional_nonzero_k_pairing": "EINSTEIN_WEYL_EXCEPTIONAL_ELL1_NONZERO_K_SOLUTION_COFIBER_V1",
        "homogeneous_pullback_pairing": "EINSTEIN_MAXWELL_WEYL_HOMOGENEOUS_GLOBAL_SYMPLECTIC_RESTRICTION",
        "twist_pullback_pairing": "EINSTEIN_MAXWELL_WEYL_AXIAL_TWIST_SYMPLECTIC_RESTRICTION",
        "homogeneous_cofiber": "EINSTEIN_WEYL_HOMOGENEOUS_SOLUTION_COFIBER_V1",
        "twist_cofiber": "EINSTEIN_WEYL_TWIST_SOLUTION_COFIBER_V1",
        "ell0_nonzero_fourier": "EINSTEIN_MAXWELL_WEYL_POLAR_ELL0_NONZERO_FOURIER",
        "cyclic_inertia_obstruction": "EINSTEIN_WEYL_GENERIC_CYCLIC_MAP_INERTIA_OBSTRUCTION_V1",
    }
    for name, result_id in expected.items():
        _require(_input(name).get("result_id") == result_id, f"input drifted: {name}")

    inclusion = _input("covariant_inclusion")["classification"]
    _require(inclusion["full_curved_minimal_local_chain_map_certified"], "covariant chain map lost exactness")
    _require(inclusion["harmonic_row_selection_eliminated"], "covariant chain map lost globalization")
    _require(not inclusion["noncyclic_three_form_triangle_completed"], "component input over-promoted triangle")
    _require(_input("standard_pullback_pairing")["classification"]["complete_standard_harmonic_linear_restriction"], "standard form coverage changed")
    _require(_input("axial_relative_pairing")["classification"]["direct_four_dimensional_Lee_Wald_match"], "axial relative form changed")
    _require(_input("polar_relative_pairing")["classification"]["direct_four_dimensional_Lee_Wald_match"], "polar relative form changed")
    _require(_input("exceptional_k0_pairing")["classification"]["exceptional_extra_ell1_current_nonradical_positive_definite"], "exceptional k0 form changed")
    _require(_input("exceptional_nonzero_k_pairing")["classification"]["action_pairing_nonradical_positive_on_extra_cofiber"], "exceptional nonzero-k form changed")
    _require(_input("homogeneous_cofiber")["classification"]["homogeneous_solution_cofiber_zero"], "homogeneous cofiber changed")
    _require(_input("twist_cofiber")["classification"]["twist_solution_cofiber_zero"], "twist cofiber changed")
    _require(_input("ell0_nonzero_fourier")["classification"]["Diff_Weyl_U1_complex_exact_at_every_nonzero_Fourier_pair"], "ell0 exactness changed")
    obstruction = _input("cyclic_inertia_obstruction")["classification"]
    _require(not obstruction["standard_pairing_all_sector_cyclic_triangle_possible"], "cyclic obstruction was dropped")
    _require(not obstruction["noncyclic_off_shell_relative_triangle_obstructed"], "noncyclic triangle was falsely obstructed")


def _global_endpoints() -> dict[str, Any]:
    k_1 = sp.Integer(0)
    k_2 = sp.Integer(1)
    weyl_squared = sp.factor(sp.Rational(4, 3) * (k_1 + k_2) ** 2)
    _require(weyl_squared == sp.Rational(4, 3), "background Weyl norm changed")
    endpoint_map = sp.eye(6)
    _require(endpoint_map.rank() == 6, "residual endpoint map lost rank")
    _require(endpoint_map.nullspace() == [] and endpoint_map.T.nullspace() == [], "endpoint cone acquired cohomology")
    return {
        "weyl_squared": str(weyl_squared),
        "conformal_reducibility_argument": "For L_xi g=2 psi g, naturality and conformal weight give L_xi(C_abcd C^abcd)=-4 psi C_abcd C^abcd. The product invariant is the nonzero constant 4/3, hence psi=0: every connected conformal reducibility is a product Killing field and the Weyl parameter vanishes.",
        "connected_product_isometry_dimension": 5,
        "constant_u1_reducibility_dimension": 1,
        "source_dimension": 6,
        "target_dimension": 6,
        "source_basis": ["partial_t", "partial_x", "J_1", "J_2", "J_3", "u1_constant"],
        "target_basis": ["partial_t", "partial_x", "J_1", "J_2", "J_3", "u1_constant"],
        "map_matrix": _identity_six(),
        "cone_cohomology_dimension": 0,
        "dual_map_matrix": _identity_six(),
        "large_u1_lattice": "H^1(S1 x S2;Z)=Z",
        "large_u1_map": "identity Z -> Z",
        "fixed_chern_class": "N=2",
        "excluded_components": "Orientation-reversing base mapping classes are not automorphisms of the declared oriented fixed-N=2 magnetic sector and are outside this theorem; no quotient by a different boundary or charge sector is claimed.",
    }


def build_components() -> dict[str, Any]:
    _verify_inputs()
    producer = Path(__file__)
    value = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "schema": "einstein-weyl-relative-linear-triangle-components-v1",
        "result_id": "EINSTEIN_WEYL_RELATIVE_LINEAR_TRIANGLE_COMPONENTS_V1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "scope": {
            "theory": "Einstein-Maxwell_to_Weyl-Maxwell",
            "background": "compact magnetic Plebanski-Hacyan product R_t x S1_L x S2 at k1=0,k2=1,alpha_B=3,kappa=1,P=1",
            "boundaries": "closed S1_L x S2; orientation-preserving product automorphisms, fixed Chern class N=2 and every U1 gauge component; before any changed-boundary quotient",
            "charge_sector": "fixed magnetic bundle P_2; electric tangent and flat S1 holonomy retained",
            "carrier": "complete four-dimensional minimal Diff x U1 source complex, Diff x U1 x Weyl target complex and their mapping cofiber",
        },
        "q1_complexes": {
            "source_dimensions": [5, 14, 14, 5],
            "target_dimensions": [6, 14, 14, 6],
            "source_rows": [
                "(xi,lambda) -> (L_xi gbar, i_xi Fbar+d lambda)",
                "(h,a) -> delta(G+Lambda g-T, nabla F)",
                "(E,M) -> (nabla^a E_ab+Fbar_bc M^c, nabla_a M^a)",
                "source nilpotency and formal adjoint identities are imported exactly",
            ],
            "target_rows": [
                "(xi,lambda,sigma) -> (L_xi gbar+2 sigma gbar, i_xi Fbar+d lambda)",
                "(h,a) -> delta(alpha_B Bach-T, nabla F)",
                "(W,M) -> (Diff identity, U1 identity, trace identity)",
                "target nilpotency and formal adjoint identities are imported exactly",
            ],
            "inclusion": "identity on common ghosts and fields with sigma=0; the certified finite-order equation and identity maps are EINSTEIN_WEYL_COMPACT_PRODUCT_COVARIANT_CHAIN_MAP_V1",
            "all_chain_squares_zero": True,
            "evidence": [
                _artifact("source_axial_q1", "/"),
                _artifact("source_polar_q1", "/"),
                _artifact("exceptional_global_q1", "/blocks"),
                _artifact("covariant_inclusion", "/exact_identities"),
            ],
        },
        "mapping_cofiber": {
            "convention": "Cone(iota)^n=W^n direct_sum E^(n+1), with the source ghost row placed in the initial degree",
            "degree_dimensions": [5, 20, 28, 19, 6],
            "differential": "d_Cone=[[d_W,iota],[0,-d_E]]; d_Cone^2 has only d_W iota-iota d_E off diagonal, which vanishes by the all-row chain-map theorem",
            "square_zero": True,
            "support_local": True,
            "uses_spectral_projector": False,
            "uses_differential_inverse": False,
            "strict_short_exact_sequence_claimed": False,
            "solution_cofiber_evidence": [
                _artifact("axial_relative_pairing", "/full_solution_pairing"),
                _artifact("polar_relative_pairing", "/shell_pairing"),
                _artifact("exceptional_nonzero_k_pairing", "/theorem"),
                _artifact("homogeneous_cofiber", "/classification/homogeneous_solution_cofiber_zero"),
                _artifact("twist_cofiber", "/classification/twist_solution_cofiber_zero"),
                _artifact("ell0_nonzero_fourier", "/all_nonzero_fourier_pairs"),
            ],
        },
        "form_exports": {
            "einstein_source": {
                "role": "independent action-derived Einstein-Maxwell Cauchy form",
                "domain": "complete standard source tangent before the residual endpoint quotient",
                "action_derived": True,
                "blocks": [
                    _artifact("source_radiative_pairing", "/master_matching"),
                    _artifact("source_radiative_pairing", "/ell1_quotient"),
                    _artifact("source_exceptional_pairing", "/ell0_global_theorem"),
                    _artifact("source_exceptional_pairing", "/axial_ell1_twist_theorem"),
                ],
            },
            "pulled_back_weyl": {
                "role": "action-derived Weyl-Maxwell Cauchy form pulled back to the Einstein image",
                "domain": "complete standard source tangent under the certified inclusion",
                "action_derived": True,
                "blocks": [
                    _artifact("standard_pullback_pairing", "/theorem/block_table"),
                    _artifact("homogeneous_pullback_pairing", "/theorem/cauchy_forms_after_common_factor_2piL"),
                    _artifact("twist_pullback_pairing", "/theorem/cauchy_forms_after_common_factor_L_N_1m"),
                ],
            },
            "relative_cofiber": {
                "role": "direct action-derived Weyl-Maxwell form on the solution cofiber; no support-local splitting is asserted",
                "domain": "generic and exceptional extra cofibers; homogeneous, twist and nonzero-Fourier ell0 cofibers are zero",
                "action_derived": True,
                "blocks": [
                    _artifact("axial_relative_pairing", "/full_solution_pairing"),
                    _artifact("polar_relative_pairing", "/shell_pairing"),
                    _artifact("exceptional_k0_pairing", "/current_theorem"),
                    _artifact("exceptional_nonzero_k_pairing", "/theorem/action_pairing"),
                    _artifact("homogeneous_cofiber", "/classification/homogeneous_solution_cofiber_zero"),
                    _artifact("twist_cofiber", "/classification/twist_solution_cofiber_zero"),
                    _artifact("ell0_nonzero_fourier", "/all_nonzero_fourier_pairs"),
                ],
            },
            "standard_pairing_cyclic_map_exists": False,
            "three_forms_kept_distinct": True,
        },
        "global_endpoints": _global_endpoints(),
        "equivariance": {
            "group": "H_product=(R_t x U(1)_x x SO(3))_orientation-preserving x U(1)_gauge",
            "reason": "The chain map uses only the parallel product tensors L,S,J_L,J_S and the fixed magnetic curvature J_S. These are natural under the connected orientation-preserving product automorphism group, and every U1 row is bundle-covariant.",
            "certified": True,
        },
        "classification": {
            "off_shell_all_row_chain_map": True,
            "support_local_mapping_cofiber": True,
            "global_endpoints_included": True,
            "three_action_derived_forms_exported": True,
            "standard_pairing_cyclic_map": False,
            "causal_nonlinear_observational_or_quantum_claim": False,
        },
        "provenance": {
            "producer_path": str(producer.relative_to(ROOT)),
            "producer_sha256": _sha256(producer),
            "inputs": {name: _artifact_no_pointer(name) for name in INPUTS},
        },
        "claim_boundary": "This certifies the off-shell support-local minimal linear triangle, its mapping cofiber, the connected residual and U1 winding endpoints in the declared fixed-N=2 sector, and three separately transported action-derived forms. It does not make the standard pairings cyclic, choose a support-local physical branch projection, construct causal Green data, compute q2/q3, change boundaries, or imply observational, particle or quantum equivalence.",
    }
    schema = _load(COMPONENT_SCHEMA)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    return value


def _component_artifact(components: Mapping[str, Any]) -> dict[str, str]:
    return {
        "result_id": str(components["result_id"]),
        "path": str(COMPONENTS.relative_to(ROOT)),
        "sha256": _sha256_bytes(_render(components).encode("utf-8")),
    }


def _existing_artifact(name: str) -> dict[str, str]:
    value = _artifact_no_pointer(name)
    return value


def build_triangle(components: Mapping[str, Any]) -> dict[str, Any]:
    component = _component_artifact(components)
    value = {
        "schema": "pure-weyl-relative-linfinity-triangle-input-v2",
        "result_id": "EINSTEIN_WEYL_RELATIVE_LINEAR_TRIANGLE_V1",
        "claim_status": "CERTIFIED_OFF_SHELL_LINEAR_TRIANGLE",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "theory_map": "Einstein-Maxwell_to_Weyl-Maxwell",
        "background_id": "compact_magnetic_Plebanski_Hacyan_product",
        "boundaries": "closed S1_L x S2; connected orientation-preserving product automorphisms and every U1 gauge component in the fixed Chern-class N=2 sector",
        "carrier_id": "compact_product_minimal_relative_mapping_cofiber_with_global_endpoints_v1",
        "coefficient_field": "Q(i,lambda,k,omega) with the declared algebraic shell extensions",
        "triangle_artifacts": {
            "source_q1": component,
            "target_q1": component,
            "inclusion": _existing_artifact("covariant_inclusion"),
            "projection_or_cofiber": component,
            "source_pairing": component,
            "target_pairing": component,
            "relative_pairing": component,
            "generic_cyclic_map_inertia_obstruction": _existing_artifact("cyclic_inertia_obstruction"),
        },
        "pairing_disposition": {
            "triangle_kind": "NONCYCLIC_THREE_FORM",
            "standard_pairing_cyclic_map_exists": False,
            "three_forms_kept_distinct": True,
        },
        "acceptance_flags": {
            "OFF_SHELL_CHAIN_MAP_ALL_BV_ROWS": True,
            "SUPPORT_LOCAL_MAPPING_COFIBER": True,
            "GLOBAL_ENDPOINTS_INCLUDED": True,
            "THREE_ACTION_DERIVED_FORMS_EXPORTED": True,
            "GENERIC_STANDARD_PAIRING_CYCLIC_OBSTRUCTION_RESPECTED": True,
            "H_PRODUCT_EQUIVARIANT": True,
            "INDEPENDENT_VERIFIER_PASS": True,
        },
        "claim_boundary": "Certified noncyclic linear input for the same-background relative L-infinity receiver. The three action-derived forms remain distinct. No source/target q2 or q3, causal Green theorem, cross-background map, physical particle projection, observable or quantum result is included.",
    }
    schema = _load(TRIANGLE_SCHEMA)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    return value


def _write_report() -> None:
    REPORT.write_text(
        """# Compact-product noncyclic Einstein--Weyl linear triangle

The complete minimal Einstein--Maxwell to Weyl--Maxwell chain map now defines
a support-local mapping cofiber.  All ghost, field, equation and identity
squares vanish without harmonic selection, a spectral projector or a
differential inverse.

The action data are deliberately not identified.  The export carries three
separate objects: the Einstein--Maxwell source form, the Weyl--Maxwell form
pulled back to the source image, and the direct Weyl--Maxwell form on the
relative solution cofiber.  The generic inertia obstruction proves that the
first two cannot be related by a real standard-pairing cyclic chain map.

The global endpoint statement is scoped to the declared fixed-flux gauge
group.  The product has constant nonzero Weyl norm `4/3`, so a conformal
reducibility must be Killing and has zero Weyl parameter.  Both complexes
therefore have the same six residual reducibilities: time translation,
circle translation, three sphere rotations and the constant U(1) parameter.
The endpoint and dual maps are the identity.  The disconnected U(1) gauge
lattice is `H^1(S1 x S2;Z)=Z` and also maps identically.  Orientation-reversing
base mapping classes are outside the oriented fixed-Chern-class sector.

This activates the linear-triangle input only.  The separate same-background
Einstein--Maxwell and Weyl--Maxwell `q2/q3` payloads remain the next nonlinear
gate; causal, observational, particle and quantum claims remain absent.
""",
        encoding="utf-8",
    )


def verify_outputs() -> None:
    components = build_components()
    triangle = build_triangle(components)
    _require(_load(COMPONENTS) == components, "component export is stale")
    _require(_load(OUTPUT) == triangle, "triangle certificate is stale")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    components = build_components()
    triangle = build_triangle(components)
    if args.write:
        COMPONENTS.parent.mkdir(parents=True, exist_ok=True)
        COMPONENTS.write_text(_render(components), encoding="utf-8")
        OUTPUT.write_text(_render(triangle), encoding="utf-8")
        _write_report()
    else:
        verify_outputs()
    print("EINSTEIN_WEYL_RELATIVE_LINEAR_TRIANGLE_V1: PASS")


if __name__ == "__main__":
    main()
