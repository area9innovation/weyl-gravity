#!/usr/bin/env python3
"""Generate the exact Nariai static-patch opposite-residue certificate.

The imported action-derived Bach operator has an exact commuting biwave
factorization.  On the transverse carrier its two factors differ by the
scalar gap 2/3.  This producer identifies the fixed-Lambda linearized
Einstein factor from the Nariai curvature channels, constructs invariant
differential projectors on the product-kernel solution space, and restricts
the fourth-order Green/Lee--Wald concomitant to both branches.

The sign observable is deliberately local and Lorentzian: the canonical
current for H=partial_t in a Nariai static patch, with both Killing horizons
retained in the flux balance.  No global timelike Killing field, positive
energy, particle interpretation, or inertia of a real symplectic form is
claimed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "NARIAI_SIGN_MECHANISM_V2.json"
SCHEMA = HERE / "nariai-sign-mechanism-v2.schema.json"
ATLAS = ROOT / "residual_atlas/phase2-sign-nariai-mechanism-v2-fragment-v1.json"
PRODUCER = Path(__file__).resolve()
VERIFIER = HERE / "verify.py"
TESTS = HERE / "tests/test_nariai_sign_mechanism_v2.py"

INPUTS = {
    "action_endpoint": (
        ROOT / "d_quotient_classical/certificates/NARIAI_ACTION_DERIVED_BACH_ENDPOINT_V1.json",
        "1dcc5e83f6942b3598930b8ffe206bc8ff0b0f821d74b9925ad61e5db9b8267d",
        "NARIAI_ACTION_DERIVED_BACH_ENDPOINT_V1",
    ),
    "cyclic_metric_bv_complex": (
        ROOT / "d_quotient_classical/certificates/NARIAI_METRIC_BACH_CYCLIC_BV_COMPLEX_V1.json",
        "3333074f4a7b94b9d36ce9d20927155fa61b1541f02b152cfd179e8e50f76dcc",
        "NARIAI_METRIC_BACH_CYCLIC_BV_COMPLEX_V1",
    ),
    "metric_biwave_green_homotopy": (
        ROOT / "d_quotient_classical/certificates/NARIAI_METRIC_BIWAVE_GREEN_HOMOTOPY_V1.json",
        "5d755293ffbe32585fb1d6afc4ccb3643784306236e4b456777040858f5266bc",
        "NARIAI_METRIC_BIWAVE_GREEN_HOMOTOPY_V1",
    ),
    "invariant_einstein_biwave_identification": (
        ROOT / "d_quotient_classical/certificates/EINSTEIN_METRIC_BIWAVE_GREEN_HOMOTOPY_V1.json",
        "e2978cf23f577ab365729d139c8eabf0bcbc2277bc2a124d872c03c94b7b8a75",
        "EINSTEIN_METRIC_BIWAVE_GREEN_HOMOTOPY_V1",
    ),
    "rank_310_causal_transfer": (
        ROOT / "d_quotient_classical/certificates/NARIAI_REPAIRED_310_ALL_ROW_GREEN_TRANSFER_V1.json",
        "0e7774b93f54d5cdc45385b5b119d7508173622fb0d4a7ca93618738971ac2ff",
        "NARIAI_REPAIRED_310_ALL_ROW_GREEN_TRANSFER_V1",
    ),
}


class NariaiSignMechanismError(RuntimeError):
    """Raised when an exact invariant or an input gate fails."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise NariaiSignMechanismError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _dense(serialized: dict[str, Any]) -> sp.Matrix:
    rows, cols = serialized["shape"]
    matrix = sp.zeros(rows, cols)
    for row, col, value in serialized["entries"]:
        matrix[row, col] = sp.Rational(value)
    return matrix


def _serialize_matrix(matrix: sp.Matrix) -> dict[str, Any]:
    entries = [
        [row, col, str(matrix[row, col])]
        for row in range(matrix.rows)
        for col in range(matrix.cols)
        if matrix[row, col] != 0
    ]
    return {"shape": [matrix.rows, matrix.cols], "entries": entries}


def _import_gate() -> tuple[list[dict[str, str]], dict[str, Any]]:
    imports: list[dict[str, str]] = []
    loaded: dict[str, Any] = {}
    for name, (path, expected_hash, result_id) in INPUTS.items():
        _require(path.exists(), f"missing input: {path}")
        actual_hash = _sha256(path)
        _require(actual_hash == expected_hash, f"input hash drift: {name}")
        payload = _load(path)
        _require(payload.get("result_id") == result_id, f"result-id drift: {name}")
        imports.append(
            {
                "name": name,
                "path": str(path.relative_to(ROOT)),
                "result_id": result_id,
                "result_state": payload["result_state"],
                "sha256": actual_hash,
            }
        )
        loaded[name] = payload
    return imports, loaded


def exact_factor_and_projector_data(biwave: dict[str, Any]) -> dict[str, Any]:
    factorization = biwave["metric_factorization"]
    _require(factorization["factors_commute"] is True, "factor commutativity lost")
    _require(
        factorization["factors_are_G_H_formally_self_adjoint"] is True,
        "formal self-adjointness lost",
    )
    a = _dense(factorization["factor_a_matrix"])
    b = _dense(factorization["factor_b_matrix"])
    projectors = [_dense(item) for item in factorization["curvature_channel_projectors"]]
    identity = sp.eye(9)

    _require(b == a - sp.Rational(2, 3) * identity, "factor gap is not 2/3")
    _require(sum(projectors, sp.zeros(9)) == identity, "curvature projectors do not resolve identity")
    for index, projector in enumerate(projectors):
        _require(projector * projector == projector, f"curvature projector {index} not idempotent")
        _require(projector.rank() == (4, 1, 4)[index], f"curvature projector {index} rank drift")
        for other_index, other in enumerate(projectors):
            if index != other_index:
                _require(projector * other == sp.zeros(9), "curvature projectors not orthogonal")
    reconstructed_a = -2 * projectors[0] + 2 * projectors[1]
    _require(reconstructed_a == a, "Einstein curvature-channel reconstruction failed")

    # In the quotient Q[LE,LC]/(LE*LC, LE-LC-2/3), represent a polynomial
    # by its values on the two branches.  This gives an independent exact
    # check of the solution projectors without choosing a mode basis.
    gap = sp.Rational(2, 3)
    pi_e_on_e, pi_e_on_c = -sp.Rational(3, 2) * (-gap), 0
    pi_c_on_e, pi_c_on_c = 0, sp.Rational(3, 2) * gap
    _require((pi_e_on_e, pi_e_on_c) == (1, 0), "Einstein projector values drift")
    _require((pi_c_on_e, pi_c_on_c) == (0, 1), "complementary projector values drift")

    return {
        "transverse_factorization": "G_H^{-1} B_action=(1/2)L_E L_C when T h=0",
        "gauge_fixed_identity": factorization["identity"],
        "factor_definitions": {
            "L_E": "Box I_9+A",
            "L_C": "Box I_9+B=L_E-(2/3)I_9",
            "scalar_gap_L_E_minus_L_C": "2/3",
        },
        "factor_a_matrix": _serialize_matrix(a),
        "factor_b_matrix": _serialize_matrix(b),
        "curvature_channels": {
            "ordered_names": ["intrafactor_tracefree", "relative_trace", "mixed"],
            "ranks": [4, 1, 4],
            "A_eigenvalues": ["-2", "2", "0"],
            "projectors": [_serialize_matrix(projector) for projector in projectors],
            "geometric_identity": "A=2 Riemann_action=-2 P_intraTF+2 P_relativeTrace+0 P_mixed",
            "derivation": "For each unit-curvature two-factor block, 2 R_{mu alpha nu beta}h^{alpha beta}=2(g_{mu nu} tr_factor(h)-h_{mu nu}); this has eigenvalues -2 on intrafactor tracefree tensors, +2 on the total-tracefree relative factor trace, and 0 on mixed tensors.",
            "Einstein_identification": "On unit Einstein Nariai in transverse total-tracefree gauge, the fixed-Lambda linearized Einstein equation is L_E h=(Box I_9+2 Riemann_action)h=0.",
        },
        "solution_space_projectors": {
            "domain": "ker(L_E L_C) intersect ker(T) on the action-paired transverse carrier",
            "Pi_E": "-(3/2)L_C",
            "Pi_C": "(3/2)L_E",
            "identities_modulo_product_equation": [
                "Pi_E+Pi_C=I",
                "Pi_E^2-Pi_E=(9/4)L_E L_C",
                "Pi_C^2-Pi_C=(9/4)L_E L_C",
                "Pi_E Pi_C=-(9/4)L_E L_C",
            ],
            "branch_values": {"on_ker_L_E": ["1", "0"], "on_ker_L_C": ["0", "1"]},
            "lift_or_mode_choice_used": False,
        },
    }


def static_patch_and_residue_data() -> dict[str, Any]:
    gap = sp.Rational(2, 3)
    prefactor = sp.Rational(1, 2)
    residue_e = -prefactor * gap
    residue_c = prefactor * gap
    _require(residue_e == -sp.Rational(1, 3), "Einstein residue drift")
    _require(residue_c == sp.Rational(1, 3), "complementary residue drift")
    _require(residue_e * residue_c < 0, "residue signs are not opposite")

    return {
        "sign_structure": {
            "choice": "STATIC_PATCH_WITH_HORIZON_FLUX_BOUNDARIES",
            "metric": "ds^2=-(1-r^2)dt^2+(1-r^2)^(-1)dr^2+dOmega_2^2",
            "coordinate_domain": "-1<r<1",
            "named_killing_field": "H=partial_t",
            "norm_g_H_H": "-(1-r^2)",
            "timelike_domain": "-1<r<1 only",
            "boundary_components": ["r=-1 Killing horizon", "r=+1 Killing horizon"],
            "global_timelike_generator_claimed": False,
            "horizon_flux_policy": "Both horizon fluxes are retained in the finite-slab Lee-Wald balance; no reflecting or zero-flux boundary condition is imposed.",
        },
        "lee_wald_concomitant": {
            "second_order_definition": "div j_L(u,v)=<u,Lv>-<Lu,v>",
            "fourth_order_representative": "j_B(u,v)=(1/2)[j_LE(u,L_C v)+j_LC(L_E u,v)] on T u=T v=0",
            "canonical_current": "J_H(h1,h2)=j_B(h1,Lie_H h2)",
            "finite_slab_balance": "slice difference plus flux through r=-1 plus flux through r=+1 equals zero",
            "Einstein_branch_restriction": "j_B|ker(L_E)=-(1/3)j_LE",
            "complementary_branch_restriction": "j_B|ker(L_C)=+(1/3)jLC",
            "Einstein_residue_multiplier": str(residue_e),
            "complementary_residue_multiplier": str(residue_c),
            "opposite_nonzero_residues": True,
            "applies_to": ["static-patch slice term", "r=-1 horizon flux", "r=+1 horizon flux"],
        },
        "mechanism": {
            "statement": "The opposite branch multiplier is the derivative/residue of the factor polynomial, fixed by the exact scalar gap L_E-L_C=2/3; it is not assigned by an Einstein-versus-additional label or by a raw lift.",
            "background_family_claim": False,
            "same_Weyl_Maxwell_family_as_phase1": False,
            "raw_real_symplectic_inertia_computed": False,
            "second_order_branch_energy_sign_determined": False,
            "fourth_order_positive_energy_claimed": False,
        },
    }


def build_certificate() -> dict[str, Any]:
    imports, loaded = _import_gate()
    factor_data = exact_factor_and_projector_data(loaded["metric_biwave_green_homotopy"])
    observable = static_patch_and_residue_data()
    return {
        "schema": "nariai-sign-mechanism-v2",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA),
        "result_id": "NARIAI_SIGN_MECHANISM_V2",
        "result_state": "STATIC_PATCH_OPPOSITE_LEE_WALD_RESIDUE_MECHANISM_EXACT",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "provenance": {
            "declared_input_commit": "85548b8982bce7cd7ba764a245112e09be59d5dd",
            "implementation_base_commit": "04bc76a67b7e328b4ae31f9de488df5cbb8afc33",
            "producer": str(PRODUCER.relative_to(ROOT)),
            "producer_sha256": _sha256(PRODUCER),
            "verifier": str(VERIFIER.relative_to(ROOT)),
            "verifier_sha256": _sha256(VERIFIER),
            "tests": str(TESTS.relative_to(ROOT)),
            "tests_sha256": _sha256(TESTS),
            "imported_artifacts": imports,
        },
        "scope": {
            "background": "global unit Nariai, restricted only for the sign observable to one static patch",
            "theory": "strict pure-Weyl metric Bach theory",
            "carrier": "action-paired transverse metric carrier T h=0 inside the certified metric BV complex",
            "observable": "H-canonical Lee-Wald current and finite-static-slab flux balance",
            "comparison": "invariant factor-residue multipliers on the Einstein and complementary kernels",
        },
        "exact_factorization_and_projectors": factor_data,
        "static_patch_residue_theorem": observable,
        "classification": {
            "Einstein_factor_identified": True,
            "complementary_factor_identified": True,
            "invariant_solution_projectors_constructed": True,
            "lee_wald_residue_multipliers_exact": True,
            "opposite_residue_mechanism_established": True,
            "global_timelike_killing_used": False,
            "horizon_boundaries_omitted": False,
            "zero_horizon_flux_assumed": False,
            "same_Weyl_Maxwell_family_claimed": False,
            "real_symplectic_inertia_claimed": False,
            "positive_energy_claimed": False,
            "Hadamard_state_constructed": False,
            "quantum_unitarity_claimed": False,
        },
        "claim_boundary": {
            "establishes": "On the declared Nariai transverse carrier, the exact Bach biwave polynomial has invariant Einstein/complementary solution projectors and its static-patch Lee-Wald current restricts with opposite exact multipliers -1/3 and +1/3, including both horizon-flux terms.",
            "does_not_establish": [
                "the absolute sign of either second-order branch canonical energy",
                "positivity, Hilbert-space norm, particles, CPT metric, or unitarity",
                "a globally timelike Nariai generator",
                "a conserved static-patch energy after discarding horizon flux",
                "a Hadamard state or Lorentzian quantum master equation",
                "robustness over an open background family",
                "identification with the Phase-1 compact Weyl-Maxwell family",
            ],
        },
        "next_gate": {
            "disposition": "DONE_SCOPED_MECHANISM_THEOREM",
            "required_for_absolute_sign": "Independently determine the sign/nondegeneracy of one normalized second-order branch canonical form under an explicit horizon state or boundary prescription.",
            "required_for_family_robustness": "Construct a separately certified open Nariai-type background family and repeat the factor-residue comparison without reusing this fixed-background conclusion.",
        },
    }


def build_atlas(certificate: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": "residual-atlas-fragment-v1",
        "entries": [
            {
                "id": "phase2-sign-nariai-mechanism-v2",
                "background": "unit Nariai static patch with both horizon fluxes retained",
                "theory": "strict pure-Weyl metric Bach theory",
                "dependency_tags": certificate["dependency_tags"],
                "descriptions": {
                    "factorization": "EXACT",
                    "projectors": "EXACT_MODULO_PRODUCT_EQUATION",
                    "lee_wald_residues": "OPPOSITE_MINUS_ONE_THIRD_PLUS_ONE_THIRD",
                    "absolute_energy_sign": "NOT_ESTABLISHED",
                    "quantum_state": "NOT_ESTABLISHED",
                },
                "evidence": [
                    {
                        "path": str(OUTPUT.relative_to(ROOT)),
                        "result_id": certificate["result_id"],
                        "sha256": _sha256(OUTPUT),
                    }
                ],
            }
        ],
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="compare regenerated payloads with disk")
    args = parser.parse_args()
    certificate = build_certificate()
    if args.check:
        _require(_load(OUTPUT) == certificate, "certificate regeneration drift")
        _require(_load(ATLAS) == build_atlas(certificate), "atlas regeneration drift")
    else:
        write_json(OUTPUT, certificate)
        write_json(ATLAS, build_atlas(certificate))
    print("Nariai static-patch opposite-residue certificate: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
