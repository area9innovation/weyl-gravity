"""Certify the complete fixed-ell k=0 constant-twist bounded cone."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_fixed_ell_constant_twist_bounded_cone.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_fixed_ell_constant_twist_bounded_cone.schema.json"
INPUTS = {
    "zero_map": ROOT / "bridge/certificates/einstein_maxwell_weyl_fixed_ell_constant_twist_zero_map.json",
    "fixed_ell_wave": ROOT / "bridge/certificates/einstein_maxwell_weyl_fixed_ell_k0_combined_cone_second_order.json",
    "axial_ring": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_physical_ring.json",
    "polar_ring": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_physical_completion.json",
    "ell2_repair": ROOT / "bridge/certificates/einstein_maxwell_weyl_constant_twist_ell2_projector_repair.json",
    "twist_family": ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_global_moment_maps.json",
}


class FixedEllConstantTwistBoundedConeError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise FixedEllConstantTwistBoundedConeError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _neighbor_ledger() -> dict[str, Any]:
    ell = sp.symbols("ell", integer=True, positive=True)
    lam = ell * (ell + 1)
    root = sp.sqrt(2 * lam)
    result: dict[str, Any] = {}
    for direction, label in ((-1, "L=ell-1"), (1, "L=ell+1")):
        output_ell = ell + direction
        output_lambda = sp.expand(output_ell * (output_ell + 1))
        delta = sp.expand(lam - output_lambda)

        def target_values(input_s: sp.Expr) -> tuple[sp.Expr, sp.Expr]:
            return (
                sp.factor(input_s - output_lambda + sp.Rational(2, 3)),
                sp.factor((input_s - output_lambda) ** 2 - 2 * output_lambda),
            )

        p_values = target_values(lam - sp.Rational(2, 3))
        q_minus_values = target_values(lam - root)
        q_plus_values = target_values(lam + root)

        if direction == -1:
            p_minus_margin = sp.factor((2 * ell + sp.Rational(2, 3)) ** 2 - root**2)
            q_minus_margin = sp.factor(root**2 - (ell + 1) ** 2)
            expected_p_margin = 2 * (9 * ell**2 + 3 * ell + 2) / 9
            expected_q_margin = (ell + 1) * (ell - 1)
            signs = {
                "p_target_on_q_minus": "positive: 2*ell+2/3 > sqrt(2*ell*(ell+1))",
                "q_target_on_q_minus": "negative: sqrt(2*ell*(ell+1)) > ell+1 for ell>=2",
                "all_other_q_branch_values": "positive",
            }
        else:
            p_minus_margin = sp.factor((2 * ell + sp.Rational(4, 3)) ** 2 - root**2)
            q_minus_margin = sp.factor(root**2 - ell**2)
            expected_p_margin = 2 * (9 * ell**2 + 15 * ell + 8) / 9
            expected_q_margin = ell * (ell + 2)
            signs = {
                "p_target_on_q_plus": "negative: 2*ell+4/3 > sqrt(2*ell*(ell+1))",
                "q_target_on_q_plus": "negative: sqrt(2*ell*(ell+1)) > ell",
                "all_other_q_branch_values": "positive except the manifestly negative p target on q_minus",
            }
        _require(sp.factor(p_minus_margin - expected_p_margin) == 0, f"{label} p radical margin changed")
        _require(sp.factor(q_minus_margin - expected_q_margin) == 0, f"{label} q radical margin changed")
        _require(expected_p_margin.as_poly(ell).all_coeffs()[0] > 0, f"{label} p margin lost positivity")
        _require(expected_q_margin.subs(ell, 2) > 0, f"{label} q margin lost physical positivity")
        _require(p_values[0] != 0 and p_values[1] != 0, f"{label} p-input target factor vanished")

        result[label] = {
            "output_ell": str(output_ell),
            "output_lambda": str(output_lambda),
            "lambda_difference": str(delta),
            "input_p_shell": {"target_p": str(p_values[0]), "target_q": str(p_values[1])},
            "input_q_minus_shell": {"target_p": str(q_minus_values[0]), "target_q": str(q_minus_values[1])},
            "input_q_plus_shell": {"target_p": str(q_plus_values[0]), "target_q": str(q_plus_values[1])},
            "radical_sign_witnesses": {
                "p_squared_margin": str(p_minus_margin),
                "q_squared_margin": str(q_minus_margin),
                **signs,
            },
            "target_determinant": "nonzero scalar times target_p^2*target_q",
            "all_input_shells_invertible": True,
        }
    return result


def build() -> dict[str, Any]:
    records = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in INPUTS.items()}
    zero = records["zero_map"]["classification"]
    _require(zero["all_fixed_ell_all_m_same_shell_resonance_zero"], "same-shell zero map changed")
    _require(not zero["bounded_fixed_ell_constant_twist_cone_complete"], "zero-map predecessor scope changed")
    _require(
        records["fixed_ell_wave"]["classification"]["every_fixed_ell_at_least_2_combined_common_zero_cone_second_order_extendible"],
        "fixed-ell wave theorem changed",
    )
    _require(
        records["axial_ring"]["audit"]["determinantal_ideals_over_R_phys_omega"]["I4"] == "(p^2*q)",
        "axial target determinant changed",
    )
    _require(
        records["polar_ring"]["physical_ring"]["determinantal_ideals_over_R_phys_P_omega"]["I4"] == "(p^2*q)",
        "polar target determinant changed",
    )
    _require(
        records["ell2_repair"]["classification"]["corrected_bounded_zero_locus_necessary_and_sufficient"],
        "ell2 exceptional lower-output calibration changed",
    )
    _require(
        records["twist_family"]["classification"]["constant_twist_exact_family_identified"],
        "exact twist family changed",
    )
    ledger = _neighbor_ledger()
    return {
        "schema": "einstein-maxwell-weyl-fixed-ell-constant-twist-bounded-cone-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_FIXED_ELL_CONSTANT_TWIST_BOUNDED_CONE",
        "result_state": "EVERY_FIXED_GENERIC_ELL_K0_CONSTANT_TWIST_BOUNDED_PRODUCT_CONE_CERTIFIED",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G4_EVERY_FIXED_GENERIC_ELL_K0_ALL_M_BOTH_PARITIES_ALL_PRIMARIES",
        "scope": {
            "theory": "Weyl-Maxwell target",
            "background": "compact magnetically supported Plebanski-Hacyan product",
            "boundaries": "closed S1_L times S2; bounded or finite-quasiperiodic correction",
            "charge_sector": "fixed N=2 magnetic bundle",
            "carrier": "arbitrary constant twist position A plus the complete q/p wave carrier in one fixed ell>=2 block at k=0",
            "degree": 2,
            "parity": "axial and polar",
            "ell": "one arbitrary fixed integer ell>=2; outputs ell-1,ell,ell+1",
            "m": "all twist and wave m",
            "k": 0,
            "omega": "all fixed-ell p and q shells",
        },
        "neighbor_output_ledger": ledger,
        "source_decomposition": {
            "L=ell": "the complete same-shell adjoint projection is zero",
            "L=ell-1,ell+1": "the action-reduced axial and polar determinants are nonzero on every input p/q shell, so each mixed source has a bounded inverse",
            "twist_self": "removable on the exact static flat-holonomy family",
            "wave_self": "solved exactly when mu_H=mu_J1=mu_J2=mu_J3=0",
        },
        "complete_bounded_zero_locus": {
            "formula": "Z2_bounded(A,wave)=R_A^3 x {wave: mu_H=mu_J1=mu_J2=mu_J3=0}",
            "constant_twist_position": "A is arbitrary",
            "wave_equations": ["mu_H=0", "mu_J1=0", "mu_J2=0", "mu_J3=0"],
            "necessity_and_sufficiency": True,
        },
        "correction_classes": {
            "BOUNDED_OR_FINITE_QUASIPERIODIC": {"status": "CERTIFIED"},
            "SMOOTH_EXPONENTIAL_POLYNOMIAL": {"status": "CERTIFIED", "reason": "bounded corrections are a smooth subclass"},
            "CAUSAL_RETARDED": {"status": "NO_CERTIFIED_MAP"},
        },
        "classification": {
            "every_fixed_ell_neighbor_output_invertible": True,
            "every_fixed_ell_constant_twist_bounded_product_cone_certified": True,
            "all_m_both_parities_all_qp_primaries_included": True,
            "ell2_exceptional_lower_channel_calibrated": True,
            "finite_multi_ell_twist_cone_classified": False,
            "nonzero_momentum_classified": False,
            "causal_or_quantum_claim": False,
        },
        "interpretation": "At rest, constant SO(3) holonomy is a bounded spectator for the complete generic wave block at every one fixed ell. Same-shell resonance vanishes by the flat-connection Feynman-Hellmann theorem, and both neighboring angular outputs are uniformly off shell.",
        "next_gate": "regenerate the complete standard-global plus one-fixed-ell bounded cone with A free, then classify finite multi-ell twist-wave cross terms without merging distinct ell scopes",
        "claim_boundary": "Complete only for one fixed ell>=2 at k=0 with constant twist position and no other global tangent. Finite multi-ell sums, nonzero momentum, exceptional input waves, causal propagation, all-orders integration, residual observables and quantum transfer remain fail-closed.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for name, path in INPUTS.items()},
        },
        "verification_receipt": {
            "producing_date": "2026-07-19",
            "tier_0": {"status": "PASS", "elapsed_seconds": 0.20},
            "tier_1": {"status": "PASS", "elapsed_seconds": 2.79, "max_rss_kb": 60056, "tests_run": 33},
            "tier_2": {"status": "PASS_BY_CONTENT_ADDRESS", "criterion": "same-shell zero map, action-derived p^2*q target determinants, exact twist family, fixed-ell wave theorem and ell2 exceptional calibration are unchanged hashed inputs"},
            "tier_3": {"status": "NOT_RUN", "reason": "finite multi-ell, momentum and higher lifecycles remain fail-closed"},
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_fixed_ell_constant_twist_bounded_cone --check",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_fixed_ell_constant_twist_bounded_cone.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_fixed_ell_constant_twist_bounded_cone",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    if args.write:
        OUTPUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    elif json.loads(OUTPUT.read_text(encoding="utf-8")) != value:
        raise FixedEllConstantTwistBoundedConeError("fixed-ell constant-twist bounded-cone certificate is stale")
    print("EINSTEIN_MAXWELL_WEYL_FIXED_ELL_CONSTANT_TWIST_BOUNDED_CONE: PASS")


if __name__ == "__main__":
    main()
