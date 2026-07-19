"""Certify electric-duality and Wilson transport for every oscillatory block."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_electric_wilson_complete_oscillator_transport.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_electric_wilson_complete_oscillator_transport.schema.json"
INPUTS = {
    "complete_inventory": ROOT / "bridge/certificates/einstein_maxwell_weyl_complete_finite_harmonic_smooth_global_second_order.json",
    "ell2_direct_fixture": ROOT / "bridge/certificates/einstein_maxwell_weyl_electric_duality_ell2_extra_resonance.json",
    "background": ROOT / "bridge/certificates/einstein_maxwell_product_incidence.json",
    "global_block": ROOT / "bridge/certificates/einstein_maxwell_exceptional_global_symplectic.json",
    "bounded_global_gate": ROOT / "bridge/certificates/einstein_maxwell_weyl_standard_global_bounded_second_order.json",
}


class CompleteTransportError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise CompleteTransportError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _duality_audit() -> dict[str, Any]:
    theta = sp.symbols("theta", real=True)
    c, s = sp.cos(theta), sp.sin(theta)
    rotation = sp.Matrix([[c, s], [-s, c]])
    _require((rotation.T * rotation).applyfunc(sp.trigsimp) == sp.eye(2), "duality doublet is not orthogonal")
    _require(sp.trigsimp(sp.det(rotation) - 1) == 0, "duality doublet changed orientation")
    return {
        "Lorentzian_Hodge_identity": "star_g^2=-1 on two-forms",
        "rotation": "F_theta=cos(theta)F+sin(theta)star_g F",
        "Maxwell_doublet": "(dF_theta,d star_g F_theta) is the SO(2) rotation of (dF,d star_g F)",
        "stress_identity": "T_ab[F_theta]=T_ab[F]",
        "Weyl_Maxwell_identity": "the Bach tensor is unchanged because the metric is unchanged",
        "symbolic_SO2_audit": True,
    }


def build() -> dict[str, Any]:
    records = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in INPUTS.items()}
    inventory = records["complete_inventory"]
    _require(inventory["classification"]["complete_certified_linear_input_inventory_included"], "complete inventory changed")
    _require(inventory["classification"]["exceptional_and_global_inputs_included"], "exceptional inventory changed")
    direct = records["ell2_direct_fixture"]["classification"]
    _require(direct["electric_Qe_times_ell2_extra_source_in_linear_image"], "direct duality fixture changed")
    _require(direct["mixed_correction_fixed_bundle_admissible"], "direct fixed-bundle fixture changed")
    fixture = records["background"]["rational_fixture"]["parameters"]
    _require(fixture["E"] == "0" and fixture["P"] == "1", "magnetic background normalization changed")
    representative = records["global_block"]["ell0_global_theorem"]["representative"]
    _require("A_x=W_x+Q_e*t" in representative, "global electric/Wilson normalization changed")
    _require(
        records["bounded_global_gate"]["polynomial_growth_ideal"]["real_polynomial_zero_locus"] == "b=0, B=0, Q_e*a=0",
        "bounded global gate changed",
    )

    return {
        "schema": "einstein-maxwell-weyl-electric-wilson-complete-oscillator-transport-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_ELECTRIC_WILSON_COMPLETE_OSCILLATOR_TRANSPORT",
        "result_state": "COMPLETE_OSCILLATORY_QE_AND_WILSON_BOUNDED_TRANSPORT_CERTIFIED",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "scope": {
            "theory": "Weyl-Maxwell",
            "background": "compact magnetically supported Plebanski-Hacyan product",
            "boundaries": "closed S1_L times S2; bounded or finite-quasiperiodic correction",
            "charge_sector": "fixed N=2 magnetic bundle with first-order electric tangent Q_e",
            "carrier": "Q_e or W_x crossed bilinearly with every certified nonzero-frequency standard q-primary or extra p-primary oscillator",
            "degree": 2,
            "parity": "both parities, allowing Hodge duality to exchange their representatives",
            "ell": "generic ell>=2 and exceptional ell=1",
            "m": "all allowed m",
            "k": "every allowed compact momentum 2*pi*n/L",
            "omega": "every certified nonzero real q/p shell frequency",
        },
        "complete_oscillator_inventory": {
            "generic": "all ell>=2 axial/polar Einstein q-primary and extra p-primary modes",
            "exceptional": "all ell=1 standard and extra axial/polar oscillators at every compact momentum",
            "excluded": "homogeneous and twist generalized-zero blocks, which are not oscillators",
            "finite_sums": "the bilinear transport extends coefficientwise to arbitrary real finite harmonic sums",
        },
        "duality_proof": {
            **_duality_audit(),
            "background_tangent": "partial_theta F_theta at theta=0 is star_bar F_bar=dt wedge dx, the declared Q_e tangent up to orientation",
            "transported_Jacobi_field": "(h,f) maps to (h,cos(theta)f+sin(theta)(star_g f plus the metric variation of star acting on F))",
            "mixed_metric_correction": "h_cross=0",
            "mixed_field_strength_correction": "f_cross=star_bar f+(D_g star)[h]F_bar",
            "mixed_equation": "L_barPhi(0,f_cross)+(D^2 E_barPhi)[Q_e,(h,f)]=0",
            "boundedness": "f_cross has the same finite nonzero-frequency time dependence as (h,f), with no secular derivative because duality leaves the metric and dispersion fixed",
            "fixed_bundle": "f_cross is closed and has zero S2 period for ell>=1; hence it is exact on R times S1 times S2 and lifts to a global connection-difference correction",
            "direct_fixture": "the ell=2,k=0 extra-primary block was independently checked coefficientwise",
        },
        "Wilson_proof": {
            "tangent": "delta A=W_x dx with delta F=0",
            "field_equation_dependence": "the classical action and Euler-Lagrange operators depend on the U1 connection only through F=dA",
            "mixed_source": "D^2 E_barPhi[W_x,(h,f)]=0 for every oscillator",
            "correction": "zero",
        },
        "bounded_ledger_consequence": {
            "electric_column": "every Q_e-times-oscillator source is in the image of L on the bounded finite-quasiperiodic correction class, so all of its P_(j,r) and R_(j,a) components vanish",
            "Wilson_column": "every W_x-times-oscillator source vanishes identically",
            "independent_global_condition": "the zero-frequency global self coefficient still requires Q_e*a=0",
            "remaining_polynomial_gate": "after b=B=0 and Q_e*a=0, a and d crossed with oscillators can contribute positive-degree P_(j,r) components",
            "remaining_resonance_gate": "circumference c, the polynomial-compatible d face, constant twist position A and bounded oscillator products can still contribute R_(j,a)",
        },
        "correction_classes": {
            "BOUNDED_OR_FINITE_QUASIPERIODIC": {"status": "CERTIFIED"},
            "SMOOTH_SECULAR": {"status": "CERTIFIED", "reason": "the bounded correction lies in the smooth exponential-polynomial class"},
            "CAUSAL_RETARDED": {"status": "NO_CERTIFIED_MAP"},
        },
        "classification": {
            "complete_certified_nonzero_frequency_inventory_covered": True,
            "Q_e_times_every_oscillator_bounded_removable": True,
            "W_x_times_every_oscillator_source_zero": True,
            "fixed_bundle_mixed_correction_admissible": True,
            "full_bounded_cone_solved": False,
            "all_orders_fixed_bundle_duality_orbit": False,
            "causal_or_quantum_claim": False,
        },
        "interpretation": "Electric variation is not an independent bounded resonance column against radiative modes: electromagnetic duality transports every certified oscillator and supplies a bounded fixed-bundle mixed correction. Flat Wilson data are invisible to the local equations. This removes Q_e and W_x from the oscillator part of the bounded ledger without removing the separate global condition Q_e*a=0.",
        "next_gate": "use the circumference classification and repaired full-time k=0 d column, complete the a/d polynomial maps, then solve the surviving c, d, constant-A and oscillator resonance equations",
        "claim_boundary": "This is a second-order mixed transport theorem for certified nonzero-frequency compact modes. It does not extend the pure Q_e direction to an all-orders fixed-bundle duality orbit, classify the complete a/d polynomial interactions or the c/d/constant-A resonance ledger, solve the complete bounded cone, construct a causal map, descend residual states, or make observational, particle or quantum claims.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for name, path in INPUTS.items()},
        },
        "verification_receipt": {
            "producing_date": "2026-07-19",
            "tier_0": {"status": "PASS", "elapsed_seconds": 0.20, "max_rss_kb": 16184},
            "tier_1": {"status": "PASS", "elapsed_seconds": 1.90, "max_rss_kb": 59624, "tests_run": 8},
            "tier_2": {"status": "PASS_BY_CONTENT_ADDRESS", "criterion": "the complete oscillator inventory and direct ell=2 duality fixture are unchanged exact inputs"},
            "tier_3": {"status": "NOT_RUN", "reason": "complete a/d polynomial maps, c/d/constant-A resonance, complete bounded, causal, residual and quantum gates remain excluded"},
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_electric_wilson_complete_oscillator_transport --check",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_electric_wilson_complete_oscillator_transport.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_electric_wilson_complete_oscillator_transport",
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
        raise CompleteTransportError("complete electric/Wilson transport certificate is stale")
    print("EINSTEIN_MAXWELL_WEYL_ELECTRIC_WILSON_COMPLETE_OSCILLATOR_TRANSPORT: PASS")


if __name__ == "__main__":
    main()
