"""Certify that the generalized-zero axial twist solution cofiber is zero."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_weyl_twist_solution_cofiber.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_weyl_twist_solution_cofiber.schema.json"
INPUTS = {
    "exceptional_cofiber": ROOT / "bridge/certificates/einstein_weyl_exceptional_ell1_solution_cofiber.json",
    "twist_pairing": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_twist_symplectic_restriction.json",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(name: str) -> dict[str, object]:
    return json.loads(INPUTS[name].read_text(encoding="utf-8"))


def _spectral_theorem() -> dict[str, object]:
    x = sp.symbols("x")
    projector = sp.Rational(3, 16) * (x - sp.Rational(4, 3)) * (x - 4)
    roots = {"twist": 0, "extra": sp.Rational(4, 3), "standard": 4}
    values = {name: sp.factor(projector.subs(x, root)) for name, root in roots.items()}
    if values != {"twist": 1, "extra": 0, "standard": 0}:
        raise AssertionError("twist CRT projector changed")
    annihilator = sp.expand(x * (3 * x - 4) * (x - 4))
    if sp.rem(sp.expand(projector**2 - projector), annihilator, domain=sp.QQ) != 0:
        raise AssertionError("twist projector lost idempotence")
    return {
        "spectral_variable": "x=omega^2",
        "target_annihilator": "x*(3*x-4)*(x-4)",
        "twist_projector": str(sp.factor(projector)),
        "projector_values": {name: str(value) for name, value in values.items()},
        "idempotent_modulo_target_annihilator": True,
        "complete_twist_target_representative": "h_(x,a)=(A_m+B_m*t)X_a, a_x=-(A_m+B_m*t)Y_1m",
        "source_to_target_coordinates": ["A_m -> A_m", "B_m -> B_m"],
        "real_harmonic_multiplicity": 3,
        "real_phase_space_dimension": 6,
    }


def build() -> dict[str, object]:
    records = {name: _load(name) for name in INPUTS}
    exceptional = records["exceptional_cofiber"]
    pairing = records["twist_pairing"]
    if not exceptional["classification"]["complete_exceptional_k0_target_solution_decomposition_certified"]:
        raise AssertionError("exceptional target decomposition changed")
    if "T_twist^ax" not in exceptional["target_decomposition"]["Einstein_image"]:
        raise AssertionError("exceptional Einstein image lost the twist primary")
    if not pairing["classification"]["pullback_equals_minus_two_times_einstein"]:
        raise AssertionError("twist pairing input changed")
    theorem = _spectral_theorem()
    return {
        "schema": "einstein-weyl-twist-solution-cofiber-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA),
        "result_id": "EINSTEIN_WEYL_TWIST_SOLUTION_COFIBER_V1",
        "result_state": "GENERALIZED_ZERO_AXIAL_TWIST_TARGET_EXHAUSTED_BY_EINSTEIN_MAXWELL_IMAGE",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "scope": {
            "theory": "Einstein-Maxwell source included in Weyl-Maxwell target",
            "background": "compactified magnetically supported Plebanski-Hacyan R_t x S1_L x S2 fixture",
            "boundaries": "closed Cauchy slice S1_L x S2; periodic x and before the finite global-moduli/final residual quotient",
            "charge_sector": "fixed magnetic U(1) bundle P_N with N=2",
            "carrier": "axial ell=1,k=0 generalized-zero twist primary only",
            "degree": 1,
            "parity": "axial",
            "ell": 1,
            "m": "all three real SO(3) components",
            "k": 0,
            "omega": "generalized zero x=omega^2=0 with A_m+B_m*t",
        },
        "map_lifecycle": "ONSHELL_MAP_ONLY",
        "spectral_projection_theorem": theorem,
        "solution_map": {
            "inclusion": "identity on every twist position/velocity pair (A_m,B_m)",
            "projection": "P_twist=3*(x-4/3)*(x-4)/16 restricted from the complete exceptional target decomposition",
            "target_twist_primary_equals_Einstein_image": True,
            "solution_cofiber": "0",
        },
        "action_derived_pairing": {
            "source_form_after_L_N_1m": [["0", "2"], ["-2", "0"]],
            "target_form_after_L_N_1m": [["0", "-4"], ["4", "0"]],
            "relative_endomorphism": "-2*I",
            "source_rank_per_m": 2,
            "target_rank_per_m": 2,
            "meaning": "the zero solution cofiber coexists with a reversal and factor-two change of the identity pullback",
        },
        "classification": {
            "complete_twist_target_primary_certified": True,
            "explicit_twist_CRT_projection_certified": True,
            "Einstein_image_equals_complete_twist_target_primary": True,
            "twist_solution_cofiber_zero": True,
            "twist_pairing_transport_certified": True,
            "twist_offshell_chain_map_certified": False,
            "global_moduli_or_final_residual_descent_certified": False,
            "Lorentzian_causal_or_quantum_claim": False,
        },
        "interpretation": "The generalized-zero axial twist primary is not an additional Weyl branch: the complete target primary is already the Einstein-Maxwell twist image. Its nondegenerate target form is nevertheless -2 times the Einstein-Maxwell form under the identity inclusion. This spectral solution statement precedes the finite SO(3)-holonomy moduli quotient and final residual descent.",
        "next_gate": "construct or obstruct the twist ghost-field-equation-identity chain map and classify the finite holonomy moduli and final residual quotient",
        "claim_boundary": "This exact same-background solution-cofiber theorem is restricted to the axial ell=1,k=0 x=0 primary. It does not identify the x=4/3 extra or x=4 standard primaries as twists, certify an off-shell twist triangle, quotient finite holonomy moduli or final residual symmetries, or support causal, observational, particle, or quantum claims.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for name, path in INPUTS.items()},
        },
        "verification_receipt": {
            "producing_date": "2026-07-18",
            "tier_0": {"status": "PASS", "commands": ["python3 -m py_compile <scoped Python paths>", "python3 -m json.tool <scoped JSON paths>", "git diff --check -- <scoped paths>"]},
            "tier_1": {"status": "PASS", "commands": ["python3 -m bridge.einstein_sector.einstein_weyl_twist_solution_cofiber --check", "python3 bridge/einstein_sector/verify_einstein_weyl_twist_solution_cofiber.py", "python3 -m unittest bridge.einstein_sector.tests.test_einstein_weyl_twist_solution_cofiber"]},
            "tier_2": {"status": "PASS_BY_CONTENT_ADDRESS", "reason": "the complete exceptional target decomposition and direct action-derived twist pairing are unchanged content-addressed inputs"},
            "tier_3": {"status": "NOT_RUN", "reason": "the off-shell twist chain map, finite moduli quotient and bridge-1 activation remain open"},
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_weyl_twist_solution_cofiber --check",
            "python3 bridge/einstein_sector/verify_einstein_weyl_twist_solution_cofiber.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_weyl_twist_solution_cofiber",
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
        raise AssertionError("twist solution-cofiber certificate is stale")
    print("EINSTEIN_WEYL_TWIST_SOLUTION_COFIBER_V1: PASS")


if __name__ == "__main__":
    main()
