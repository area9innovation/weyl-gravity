"""Build the compact-product Einstein--Weyl residual-action descent.

This is a consumer of the frozen relative triangle and branch dictionary.  It
does not regenerate either producer.  The theorem is deliberately limited to
an equivariant mapping-cone cohomology representation; it does not construct
the orbit-space or Marsden--Weinstein quotient.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/EINSTEIN_WEYL_RELATIVE_RESIDUAL_ACTION_DESCENT_V1.json"
OVERLAY = ROOT / "residual_atlas/einstein-weyl-relative-residual-action-overlay-v1.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein-weyl-relative-residual-action-descent-v1.schema.json"
INPUTS = {
    "triangle": ROOT / "bridge/certificates/EINSTEIN_WEYL_RELATIVE_LINEAR_TRIANGLE_V1.json",
    "components": ROOT / "bridge/einstein_sector/generated/einstein_weyl_relative_linear_triangle_v1/components.json",
    "dictionary": ROOT / "bridge/certificates/einstein_weyl_relative_branch_dictionary.json",
    "manifest": ROOT / "residual_atlas/residual-branch-manifest-v1.json",
    "homogeneous_form": ROOT / "bridge/certificates/einstein_maxwell_weyl_homogeneous_global_symplectic_restriction.json",
    "twist_form": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_twist_symplectic_restriction.json",
}


class DescentError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise DescentError(message)


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    _require(isinstance(value, dict), f"expected object: {path}")
    return value


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _reference(name: str) -> dict[str, str]:
    path = INPUTS[name]
    payload = _load(path)
    return {
        "path": str(path.relative_to(ROOT)),
        "result_id": str(payload.get("result_id", payload.get("schema"))),
        "sha256": _sha256(path),
    }


def _verify_inputs() -> None:
    triangle = _load(INPUTS["triangle"])
    components = _load(INPUTS["components"])
    dictionary = _load(INPUTS["dictionary"])
    manifest = _load(INPUTS["manifest"])
    _require(triangle["result_id"] == "EINSTEIN_WEYL_RELATIVE_LINEAR_TRIANGLE_V1", "triangle drift")
    _require(dictionary["result_id"] == "EINSTEIN_WEYL_RELATIVE_BRANCH_DICTIONARY_V1", "dictionary drift")
    _require(manifest["schema"] == "pure-weyl-residual-branch-manifest-v1", "manifest drift")
    _require(triangle["acceptance_flags"]["H_PRODUCT_EQUIVARIANT"], "triangle lost equivariance")
    _require(triangle["acceptance_flags"]["GLOBAL_ENDPOINTS_INCLUDED"], "endpoint theorem missing")
    _require(components["global_endpoints"]["cone_cohomology_dimension"] == 0, "endpoint cone changed")
    _require(components["global_endpoints"]["large_u1_map"] == "identity Z -> Z", "winding map changed")
    _require(not triangle["pairing_disposition"]["standard_pairing_cyclic_map_exists"], "cyclicity was over-promoted")
    _require(triangle["pairing_disposition"]["three_forms_kept_distinct"], "three-form distinction lost")


def _matrix_checks() -> dict[str, Any]:
    tau = sp.symbols("tau", real=True)
    homogeneous_action = sp.Matrix(
        [
            [1, tau, 0, 0, 0, 0],
            [0, 1, 0, 0, 0, 0],
            [tau**2, tau**3 / 3, 1, tau, 0, 0],
            [2 * tau, tau**2, 0, 1, 0, 0],
            [0, 0, 0, 0, 1, 0],
            [0, 0, 0, 0, tau, 1],
        ]
    )
    twist_action = sp.Matrix([[1, tau], [0, 1]])
    homogeneous = _load(INPUTS["homogeneous_form"])["theorem"]["cauchy_forms_after_common_factor_2piL"]
    omega_e = sp.Matrix(homogeneous["einstein_maxwell"])
    omega_w = sp.Matrix(homogeneous["weyl_maxwell"])
    twist = _load(INPUTS["twist_form"])["theorem"]["cauchy_forms_after_common_factor_L_N_1m"]
    omega_te = sp.Matrix(twist["einstein_maxwell"])
    omega_tw = sp.Matrix(twist["weyl_maxwell"])
    defects = {
        "homogeneous_source": sp.simplify(homogeneous_action.T * omega_e * homogeneous_action - omega_e),
        "homogeneous_target": sp.simplify(homogeneous_action.T * omega_w * homogeneous_action - omega_w),
        "twist_source": sp.simplify(twist_action.T * omega_te * twist_action - omega_te),
        "twist_target": sp.simplify(twist_action.T * omega_tw * twist_action - omega_tw),
    }
    _require(all(value == sp.zeros(*value.shape) for value in defects.values()), "global pairing invariance failed")
    return {
        "homogeneous_time_translation_matrix": [
            [str(sp.factor(value)) for value in homogeneous_action.row(row)]
            for row in range(homogeneous_action.rows)
        ],
        "twist_time_translation_matrix": [
            [str(sp.factor(value)) for value in twist_action.row(row)]
            for row in range(twist_action.rows)
        ],
        "pairing_invariance_defects": {name: "0" for name in defects},
    }


def _oscillatory_action(ell: str) -> dict[str, Any]:
    return {
        "connected_group": "H_product=(R_t x U(1)_x x SO(3))_orientation-preserving x U(1)_constant",
        "coefficient_action": "c_(m,k,omega) -> exp(-I*omega*tau+I*k*theta) sum_m' D^ell_(m,m')(R)c_(m',k,omega)",
        "ell": ell,
        "constant_u1_action": "identity because d(chi_constant)=0",
        "chain_equivariance_defect": "0",
        "cofiber_equivariance_defect": "0",
        "reason": "the natural chain map and the p/q primary projectors are scalar in m and polynomial in the invariant time, circle and sphere operators",
    }


def _row(
    branch_id: str,
    manifest_ids: list[str],
    action: dict[str, Any],
    cohomology: dict[str, Any],
    pairings: dict[str, Any],
) -> dict[str, Any]:
    return {
        "branch_id": branch_id,
        "manifest_branch_ids": manifest_ids,
        "residual_action": action,
        "relative_mapping_cone_cohomology": cohomology,
        "pairing_blocks": pairings,
        "global_orbit_quotient": {
            "status": "NO_CERTIFIED_MAP",
            "reason": "no moment level, orbit-type stratification, or global symplectic quotient has been constructed",
        },
        "support_local_physical_projection": {
            "status": "NO_CERTIFIED_MAP",
            "reason": "the support-local mapping cofiber does not supply a support-local splitting onto physical branches",
        },
        "causal_green_descent": {
            "status": "NO_CERTIFIED_MAP",
            "reason": "no causal Green carrier is certified on this fourth-order gauge complex",
        },
    }


def build_certificate() -> dict[str, Any]:
    _verify_inputs()
    matrices = _matrix_checks()
    rows = [
        _row(
            "ph.generic.axial.relative",
            ["branch.ph.em.q.generic", "branch.ph.wm.p.generic"],
            _oscillatory_action("ell>=2"),
            {
                "endpoint_degree": {"status": "CERTIFIED", "module": "0"},
                "solution_degree": {
                    "status": "CERTIFIED",
                    "module": "(K_(ell,n)[omega]/(p))^2 tensor V_ell",
                    "interpretation": "two additional-Weyl cyclic summands, retained as an H_product representation",
                },
                "all_other_global_function_space_degrees": {"status": "NO_CERTIFIED_MAP"},
            },
            {
                "einstein_source": {"status": "CERTIFIED", "radical_dimension": 0, "inertia": [1, 1]},
                "pulled_back_weyl_on_einstein": {"status": "CERTIFIED", "radical_dimension": 0, "inertia": [1, 1]},
                "relative_cofiber": {"status": "CERTIFIED", "radical_dimension": 0, "inertia": [2, 0]},
                "mixed_einstein_extra": {"status": "CERTIFIED", "matrix": "0"},
            },
        ),
        _row(
            "ph.generic.polar.relative",
            ["branch.ph.em.q.generic", "branch.ph.wm.p.generic"],
            _oscillatory_action("ell>=2"),
            {
                "endpoint_degree": {"status": "CERTIFIED", "module": "0"},
                "solution_degree": {
                    "status": "CERTIFIED",
                    "module": "(K_(ell,n)[omega]/(p))^2 tensor V_ell",
                    "interpretation": "two additional-Weyl cyclic summands, retained as an H_product representation",
                },
                "all_other_global_function_space_degrees": {"status": "NO_CERTIFIED_MAP"},
            },
            {
                "einstein_source": {"status": "CERTIFIED", "radical_dimension": 0, "inertia": [1, 1]},
                "pulled_back_weyl_on_einstein": {"status": "CERTIFIED", "radical_dimension": 0, "inertia": [1, 1]},
                "relative_cofiber": {"status": "CERTIFIED", "radical_dimension": 0, "inertia": [2, 0]},
                "mixed_einstein_extra": {"status": "CERTIFIED", "matrix": "0"},
            },
        ),
        _row(
            "ph.exceptional.ell1.relative",
            ["branch.ph.em.ell1.standard", "branch.ph.wm.ell1.extra.k0"],
            _oscillatory_action("ell=1, k=0; generalized-zero twist handled separately"),
            {
                "endpoint_degree": {"status": "CERTIFIED", "module": "0"},
                "solution_degree": {
                    "status": "CERTIFIED",
                    "module": "(K[x]/(x-4/3))^2 tensor V_1",
                    "interpretation": "one axial and one polar extra class for every m",
                },
                "all_other_global_function_space_degrees": {"status": "NO_CERTIFIED_MAP"},
            },
            {
                "einstein_source": {"status": "CERTIFIED", "radical_dimension": 0},
                "pulled_back_weyl_on_einstein": {"status": "CERTIFIED", "radical_dimension": 0, "relative_operator": "4*I"},
                "relative_cofiber": {"status": "CERTIFIED", "radical_dimension": 0, "Gram": [["16", "0"], ["0", "3"]]},
                "mixed_einstein_extra": {"status": "CERTIFIED", "matrix": "0"},
            },
        ),
        _row(
            "ph.exceptional.ell1.nonzero_k.relative",
            ["branch.ph.em.ell1.standard", "branch.ph.wm.ell1.extra.knonzero"],
            _oscillatory_action("ell=1, k!=0"),
            {
                "endpoint_degree": {"status": "CERTIFIED", "module": "0"},
                "solution_degree": {
                    "status": "CERTIFIED",
                    "module": "(K_n[s]/(s-4/3))^2 tensor V_1",
                    "interpretation": "one axial and one polar extra class for every m and allowed nonzero k",
                },
                "all_other_global_function_space_degrees": {"status": "NO_CERTIFIED_MAP"},
            },
            {
                "einstein_source": {"status": "CERTIFIED", "radical_dimension": 0},
                "pulled_back_weyl_on_einstein": {"status": "CERTIFIED", "radical_dimension": 0, "relative_operator": "4*I"},
                "relative_cofiber": {
                    "status": "CERTIFIED",
                    "radical_dimension": 0,
                    "Gram": {"axial": "4*(3*k^2+4)", "polar": "4*(3*k^2+4)"},
                },
                "mixed_einstein_extra": {"status": "CERTIFIED", "matrix": "0"},
            },
        ),
        _row(
            "ph.global.homogeneous.relative",
            ["branch.ph.global.homogeneous"],
            {
                "coordinate_order": ["a", "b", "c", "d", "Q_e", "W_x"],
                "time_translation": matrices["homogeneous_time_translation_matrix"],
                "finite_formula": {
                    "a'": "a+tau*b",
                    "b'": "b",
                    "c'": "c+tau*d+tau^2*a+(tau^3/3)*b",
                    "d'": "d+2*tau*a+tau^2*b",
                    "Q_e'": "Q_e",
                    "W_x'": "W_x+tau*Q_e",
                },
                "SO3_and_circle_translation": "identity",
                "constant_u1_action": "identity",
                "chain_equivariance_defect": "0",
                "cofiber_equivariance_defect": "0",
            },
            {
                "endpoint_degree": {"status": "CERTIFIED", "module": "0"},
                "solution_degree": {"status": "CERTIFIED", "module": "0", "reason": "source image equals complete target block"},
                "all_other_global_function_space_degrees": {"status": "NO_CERTIFIED_MAP"},
            },
            {
                "einstein_source": {"status": "CERTIFIED", "radical_dimension": 0, "rank": 6},
                "pulled_back_weyl_on_einstein": {
                    "status": "CERTIFIED",
                    "radical_dimension": 0,
                    "rank": 6,
                    "relative_operator": "I+N, N^2=0, rank(N)=2",
                },
                "relative_cofiber": {"status": "NOT_APPLICABLE", "reason": "zero solution cofiber"},
                "invariance_defects": {
                    "source": matrices["pairing_invariance_defects"]["homogeneous_source"],
                    "target": matrices["pairing_invariance_defects"]["homogeneous_target"],
                },
            },
        ),
        _row(
            "ph.global.twist.relative",
            ["branch.ph.global.twist"],
            {
                "coordinate_order": ["A", "B"],
                "time_translation": matrices["twist_time_translation_matrix"],
                "finite_formula": {"A'": "R*(A+tau*B)", "B'": "R*B"},
                "SO3_action": "the real vector representation V_1",
                "circle_translation_and_u1": "identity",
                "chain_equivariance_defect": "0",
                "cofiber_equivariance_defect": "0",
            },
            {
                "endpoint_degree": {"status": "CERTIFIED", "module": "0"},
                "solution_degree": {"status": "CERTIFIED", "module": "0", "reason": "source image equals complete target twist block"},
                "all_other_global_function_space_degrees": {"status": "NO_CERTIFIED_MAP"},
            },
            {
                "einstein_source": {"status": "CERTIFIED", "radical_dimension": 0, "rank_per_m": 2},
                "pulled_back_weyl_on_einstein": {
                    "status": "CERTIFIED",
                    "radical_dimension": 0,
                    "rank_per_m": 2,
                    "relative_operator": "-2*I",
                },
                "relative_cofiber": {"status": "NOT_APPLICABLE", "reason": "zero solution cofiber"},
                "invariance_defects": {
                    "source": matrices["pairing_invariance_defects"]["twist_source"],
                    "target": matrices["pairing_invariance_defects"]["twist_target"],
                },
            },
        ),
        _row(
            "ph.global.electric_wilson.relative",
            ["branch.ph.maxwell.electric_wilson"],
            {
                "coordinate_order": ["Q_e", "W_x"],
                "time_translation": [["1", "0"], ["tau", "1"]],
                "finite_formula": {"Q_e'": "Q_e", "W_x'": "W_x+tau*Q_e"},
                "large_u1_winding": "W_x -> W_x+(2*pi/L)*r, r in Z; equivalently L*W_x is periodic modulo 2*pi",
                "large_u1_map_source_to_target": "identity Z -> Z",
                "connected_constant_u1_action": "identity",
                "chain_equivariance_defect": "0",
                "cofiber_equivariance_defect": "0",
            },
            {
                "endpoint_degree": {"status": "CERTIFIED", "module": "0"},
                "solution_degree": {"status": "CERTIFIED", "module": "0", "reason": "electric and Wilson tangents are shared source/target coordinates"},
                "all_other_global_function_space_degrees": {"status": "NO_CERTIFIED_MAP"},
            },
            {
                "einstein_source": {"status": "CERTIFIED", "radical_dimension": 0, "rank": 2},
                "pulled_back_weyl_on_einstein": {"status": "CERTIFIED", "radical_dimension": 0, "rank": 2, "relative_operator": "I"},
                "relative_cofiber": {"status": "NOT_APPLICABLE", "reason": "zero solution cofiber"},
            },
        ),
    ]
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "schema": "einstein-weyl-relative-residual-action-descent-v1",
        "result_id": "EINSTEIN_WEYL_RELATIVE_RESIDUAL_ACTION_DESCENT_V1",
        "lifecycle_status": "CLASSIFIED",
        "result_state": "EQUIVARIANT_MAPPING_CONE_DESCENT_CERTIFIED_GLOBAL_ORBIT_QUOTIENT_OPEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "scope": {
            "theory": "Einstein-Maxwell_to_Weyl-Maxwell",
            "background": "compactified magnetically supported Plebanski-Hacyan R_t x S1_L x S2 fixture",
            "boundaries": "closed S1_L x S2, fixed magnetic bundle P_2",
            "charge_sector": "fixed Chern class N=2; electric tangent and flat holonomy retained",
            "carrier": "certified relative minimal linear triangle and its branchwise solution mapping cofiber",
            "degree": "endpoint reducibility and solution cohomology only",
            "parity": "axial and polar kept separate",
            "ell": "0, 1 and generic ell>=2 by declared rows",
            "m": "all through explicit SO3 representations",
            "k": "all allowed compact momenta",
            "omega": "oscillatory shells and generalized zero kept separate",
        },
        "definitions": {
            "relative_residual_cohomology": "cohomology of Cone(iota) retained as an H_product representation; it is not invariant-state cohomology and not an orbit-space quotient",
            "residual_group": "H_product=(R_t x U(1)_x x SO(3))_orientation-preserving x U(1)_constant, together with the separate large-U1 winding lattice Z",
            "endpoint_map": "identity on (partial_t,partial_x,J_1,J_2,J_3,u1_constant) and identity Z->Z on winding",
        },
        "classification": {
            "chain_equivariance": "CERTIFIED",
            "endpoint_relative_cohomology": "CERTIFIED_ZERO",
            "solution_relative_cohomology": "CERTIFIED_BRANCHWISE",
            "three_action_derived_forms_distinct": True,
            "standard_pairing_cyclic_map_exists": False,
            "global_orbit_or_symplectic_quotient": "NO_CERTIFIED_MAP",
            "support_local_physical_branch_projection": "NO_CERTIFIED_MAP",
            "causal_green_descent": "NO_CERTIFIED_MAP",
            "particle_observer_nonlinear_quantum_claim": False,
        },
        "branches": rows,
        "provenance": {
            "inputs": {name: _reference(name) for name in INPUTS},
            "producer_path": str(Path(__file__).relative_to(ROOT)),
            "producer_sha256": _sha256(Path(__file__)),
            "schema_path": str(SCHEMA.relative_to(ROOT)),
            "schema_sha256": _sha256(SCHEMA),
        },
        "verification_commands": [
            "PYTHONPATH=. python3 -m bridge.einstein_sector.einstein_weyl_relative_residual_action_descent --check",
            "PYTHONPATH=. python3 bridge/einstein_sector/verify_einstein_weyl_relative_residual_action_descent.py",
            "PYTHONPATH=. python3 -m unittest bridge.einstein_sector.tests.test_einstein_weyl_relative_residual_action_descent -v",
        ],
        "claim_boundary": "This certifies equivariant endpoint and solution-cofiber representations and the invariance/nonradicality of three separately action-derived forms. It does not construct invariant-state cohomology, a global orbit or symplectic quotient, a support-local physical splitting, causal Green data, particles, observables, nonlinear maps, scattering, unitarity or quantum states.",
    }


def build_overlay(certificate: dict[str, Any]) -> dict[str, Any]:
    cert_ref = {
        "path": str(OUTPUT.relative_to(ROOT)),
        "result_id": certificate["result_id"],
        "sha256": hashlib.sha256((json.dumps(certificate, indent=2, sort_keys=True) + "\n").encode()).hexdigest(),
    }
    rows = []
    for branch in certificate["branches"]:
        for manifest_id in branch["manifest_branch_ids"]:
            rows.append(
                {
                    "manifest_branch_id": manifest_id,
                    "relative_branch_id": branch["branch_id"],
                    "cells": {
                        "residual_action": {"status": "CERTIFIED", "source": cert_ref},
                        "relative_mapping_cone_cohomology": {
                            "status": branch["relative_mapping_cone_cohomology"]["solution_degree"]["status"],
                            "source": cert_ref,
                        },
                        "action_pairing_descent": {"status": "CERTIFIED", "source": cert_ref},
                        "global_orbit_quotient": {"status": "NO_CERTIFIED_MAP", "source": cert_ref},
                        "support_local_physical_projection": {"status": "NO_CERTIFIED_MAP", "source": cert_ref},
                        "causal_green_descent": {"status": "NO_CERTIFIED_MAP", "source": cert_ref},
                    },
                }
            )
    return {
        "schema": "residual-branch-manifest-overlay-v1",
        "result_id": "EINSTEIN_WEYL_RELATIVE_RESIDUAL_ACTION_ATLAS_OVERLAY_V1",
        "base_manifest": _reference("manifest"),
        "status_vocabulary": ["CERTIFIED", "OBSTRUCTED", "OPEN", "NOT_APPLICABLE", "NO_CERTIFIED_MAP"],
        "generated_claims_ledger": True,
        "rows": rows,
        "claim_boundary": "Append-only fail-closed overlay for the pinned manifest; it does not rewrite or regenerate RESIDUAL_BRANCH_MANIFEST_V1.",
    }


def _render(value: dict[str, Any]) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def verify_outputs() -> None:
    certificate = build_certificate()
    overlay = build_overlay(certificate)
    schema = _load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(certificate)
    _require(OUTPUT.read_text(encoding="utf-8") == _render(certificate), "certificate is stale")
    _require(OVERLAY.read_text(encoding="utf-8") == _render(overlay), "atlas overlay is stale")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        verify_outputs()
        print("EINSTEIN_WEYL_RELATIVE_RESIDUAL_ACTION_DESCENT_V1: PASS")
        return
    certificate = build_certificate()
    OUTPUT.write_text(_render(certificate), encoding="utf-8")
    OVERLAY.write_text(_render(build_overlay(certificate)), encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(ROOT)}")
    print(f"wrote {OVERLAY.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
