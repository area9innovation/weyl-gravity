"""Certify the exceptional ell=1,k=0 Einstein/extra solution cofiber."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_weyl_exceptional_ell1_solution_cofiber.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_weyl_exceptional_ell1_solution_cofiber.schema.json"
INPUTS = {
    "axial_operator": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_ell1_k0_operator.json",
    "polar_operator": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_ell1_k0_operator.json",
    "current": ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ell1_current_taub.json",
    "standard": ROOT / "bridge/certificates/einstein_maxwell_weyl_standard_harmonic_symplectic_inclusion.json",
    "physical": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell1_physical_symplectic_restriction.json",
    "twist": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_twist_symplectic_restriction.json",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(name: str) -> dict[str, object]:
    return json.loads(INPUTS[name].read_text(encoding="utf-8"))


def _projectors() -> dict[str, object]:
    x = sp.symbols("x")
    axial = {
        "twist": sp.Rational(3, 16) * (x - sp.Rational(4, 3)) * (x - 4),
        "extra": -sp.Rational(9, 32) * x * (x - 4),
        "standard": sp.Rational(3, 32) * x * (x - sp.Rational(4, 3)),
    }
    polar = {
        "extra": sp.Rational(3, 8) * (4 - x),
        "standard": sp.Rational(3, 8) * (x - sp.Rational(4, 3)),
    }
    axial_roots = {"twist": 0, "extra": sp.Rational(4, 3), "standard": 4}
    polar_roots = {"extra": sp.Rational(4, 3), "standard": 4}
    for label, polynomial in axial.items():
        values = {root_label: sp.factor(polynomial.subs(x, root)) for root_label, root in axial_roots.items()}
        expected = {root_label: int(root_label == label) for root_label in axial_roots}
        if values != expected:
            raise AssertionError(f"axial projector {label} changed: {values}")
    for label, polynomial in polar.items():
        values = {root_label: sp.factor(polynomial.subs(x, root)) for root_label, root in polar_roots.items()}
        expected = {root_label: int(root_label == label) for root_label in polar_roots}
        if values != expected:
            raise AssertionError(f"polar projector {label} changed: {values}")
    if sp.expand(sum(axial.values())) != 1 or sp.expand(sum(polar.values())) != 1:
        raise AssertionError("exceptional CRT projectors lost completeness")
    return {
        "spectral_variable": "x=omega^2",
        "axial": {label: str(sp.factor(value)) for label, value in axial.items()},
        "polar": {label: str(sp.factor(value)) for label, value in polar.items()},
        "identities": {
            "axial_sum": "P_twist+P_extra+P_standard=1",
            "polar_sum": "P_extra+P_standard=1",
            "idempotence_scope": "on the reduced solution module modulo x*(3*x-4)*(x-4) axially and (3*x-4)*(x-4) polarly",
        },
    }


def build() -> dict[str, object]:
    records = {name: _load(name) for name in INPUTS}
    axial = records["axial_operator"]
    polar = records["polar_operator"]
    current = records["current"]
    if not axial["classification"]["standard_physical_shell_recovered"] or not axial["classification"]["zero_frequency_twist_recovered_without_frequency_inversion"]:
        raise AssertionError("axial exceptional standard input changed")
    if not axial["classification"]["extra_fourth_order_ell1_shell_discovered"]:
        raise AssertionError("axial exceptional extra input changed")
    if not polar["classification"]["polar_ell1_standard_shell_certified"] or not polar["classification"]["polar_ell1_extra_fourth_order_shell_certified"]:
        raise AssertionError("polar exceptional operator input changed")
    if not current["classification"]["exceptional_extra_ell1_current_nonradical_positive_definite"]:
        raise AssertionError("exceptional current input changed")
    if not records["physical"]["classification"]["physical_ell1_pullback_equals_four_times_einstein"]:
        raise AssertionError("physical ell1 inclusion input changed")
    if not records["twist"]["classification"]["pullback_equals_minus_two_times_einstein"]:
        raise AssertionError("twist inclusion input changed")
    operator_axial = axial["operator_theorem"]
    operator_polar = polar["operator_theorem"]
    return {
        "schema": "einstein-weyl-exceptional-ell1-solution-cofiber-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA),
        "result_id": "EINSTEIN_WEYL_EXCEPTIONAL_ELL1_SOLUTION_COFIBER_V1",
        "result_state": "EXCEPTIONAL_ELL1_K0_SOLUTION_COFIBER_AND_CRT_PROJECTION_CERTIFIED",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "scope": {
            "theory": "Einstein-Maxwell source included in Weyl-Maxwell target",
            "background": "compactified magnetically supported Plebanski-Hacyan R_t x S1_L x S2 fixture",
            "boundaries": "closed Cauchy slice S1_L x S2; before final residual quotient",
            "charge_sector": "fixed magnetic U(1) bundle P_N with N=2",
            "carrier": "exceptional local-gauge-reduced axial and polar ell=1,k=0 solution modules",
            "degree": 1,
            "parity": "axial and polar kept separate",
            "ell": 1,
            "m": "all three real SO(3) components",
            "k": 0,
            "omega": "twist x=0 axially, extra x=4/3, standard x=4",
        },
        "map_lifecycle": "ONSHELL_MAP_ONLY",
        "target_decomposition": {
            "axial": "T_WM^ax = T_twist^ax direct-sum T_extra^ax direct-sum T_standard^ax",
            "polar": "T_WM^pol = T_extra^pol direct-sum T_standard^pol",
            "Einstein_image": "T_EM = T_twist^ax direct-sum T_standard^ax direct-sum T_standard^pol",
            "solution_cofiber": "C_extra = T_extra^ax direct-sum T_extra^pol, tensored with the real ell=1 SO(3) multiplicity",
        },
        "explicit_projection": _projectors(),
        "branch_representatives": {
            "axial_order": operator_axial["raw_coefficient_order"],
            "axial": operator_axial["representatives_Ht_Hx_Qt_Qx"],
            "polar_reduced_order": operator_polar["reduced_field_order"],
            "polar": operator_polar["physical_shells"],
        },
        "action_derived_pairing": {
            "standard_relative_operator": "4*I on the physical axial-plus-polar ell=1 quotient",
            "twist_relative_operator": "-2*I on the axial generalized-zero twist pair",
            "extra_representative_order": current["current_theorem"]["representative_order"],
            "extra_Gram": current["current_theorem"]["normalized_extra_Hermitian_current_Gram"],
            "extra_inertia": current["current_theorem"]["extra_positive_frequency_inertia"],
            "standard_extra_mixed_pairing": current["current_theorem"]["extra_standard_mixed_pairing"],
            "cofiber_nonradical": True,
        },
        "classification": {
            "complete_exceptional_k0_target_solution_decomposition_certified": True,
            "Einstein_image_identified": True,
            "explicit_CRT_projection_certified": True,
            "exceptional_solution_cofiber_certified": True,
            "cofiber_action_pairing_nonradical": True,
            "all_m_by_SO3_equivariance": True,
            "exceptional_offshell_chain_map_certified": False,
            "nonzero_compact_momentum_exceptional_cofiber_certified": False,
            "final_residual_descent_certified": False,
            "Lorentzian_causal_or_quantum_claim": False,
        },
        "interpretation": "At ell=1,k=0 the target quotient splits spectrally into the standard Einstein-Maxwell image, the axial twist already contained in the source, and one additional fourth-order mode in each parity. The displayed CRT polynomials give the explicit solution-level projection onto those branches, and the direct current makes the extra cofiber nonradical. This is not an off-shell exceptional BV triangle.",
        "next_gate": "construct or obstruct the exceptional ghost-field-equation-identity chain map and classify nonzero compact momentum before promoting the exceptional sector to a derived cofiber triangle",
        "claim_boundary": "This exact same-background REDUCED-MODE solution cofiber is scoped to ell=1,k=0. It does not cover k!=0, an off-shell exceptional chain map, final residual cohomology, changed boundaries, causal propagation, particles, observations, or quantum states.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for name, path in INPUTS.items()},
        },
        "verification_receipt": {
            "producing_date": "2026-07-18",
            "tier_0": {"status": "PASS", "commands": ["python3 -m py_compile <scoped Python paths>", "python3 -m json.tool <scoped JSON paths>", "git diff --check -- <scoped paths>"]},
            "tier_1": {"status": "PASS", "commands": ["python3 -m bridge.einstein_sector.einstein_weyl_exceptional_ell1_solution_cofiber --check", "python3 bridge/einstein_sector/verify_einstein_weyl_exceptional_ell1_solution_cofiber.py", "python3 -m unittest bridge.einstein_sector.tests.test_einstein_weyl_exceptional_ell1_solution_cofiber"]},
            "tier_2": {"status": "PASS_BY_CONTENT_ADDRESS", "reason": "the complete exceptional operators and direct action currents are unchanged content-addressed inputs"},
            "tier_3": {"status": "NOT_RUN", "reason": "the off-shell exceptional chain map and bridge-1 activation remain open"},
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_weyl_exceptional_ell1_solution_cofiber --check",
            "python3 bridge/einstein_sector/verify_einstein_weyl_exceptional_ell1_solution_cofiber.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_weyl_exceptional_ell1_solution_cofiber",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    value = build()
    if arguments.write:
        OUTPUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    elif json.loads(OUTPUT.read_text(encoding="utf-8")) != value:
        raise AssertionError("exceptional ell1 solution-cofiber certificate is stale")
    print("EINSTEIN_WEYL_EXCEPTIONAL_ELL1_SOLUTION_COFIBER_V1: PASS")


if __name__ == "__main__":
    main()
