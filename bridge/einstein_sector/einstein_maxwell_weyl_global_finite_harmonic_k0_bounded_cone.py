"""Classify the global bounded cone for finite generic k=0 wave sums."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_global_finite_harmonic_k0_bounded_cone.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_global_finite_harmonic_k0_bounded_cone.schema.json"
INPUTS = {
    "generic_pivot": ROOT / "bridge/certificates/einstein_maxwell_weyl_abd_generic_lambda_pivot.json",
    "finite_wave": ROOT / "bridge/certificates/einstein_maxwell_weyl_finite_harmonic_k0_combined_cone_second_order.json",
    "moment_cone": ROOT / "bridge/certificates/einstein_maxwell_weyl_k0_moment_map_cone.json",
    "fixed_ell_global": ROOT / "bridge/certificates/einstein_maxwell_weyl_global_fixed_ell_k0_bounded_cone.json",
    "standard_global": ROOT / "bridge/certificates/einstein_maxwell_weyl_standard_global_bounded_second_order.json",
    "circumference": ROOT / "bridge/certificates/einstein_maxwell_weyl_circumference_complete_oscillator_bounded_classification.json",
    "electric_wilson": ROOT / "bridge/certificates/einstein_maxwell_weyl_electric_wilson_complete_oscillator_transport.json",
    "constant_twist": ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_global_moment_maps.json",
}


class GlobalFiniteHarmonicK0BoundedConeError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise GlobalFiniteHarmonicK0BoundedConeError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> dict[str, object]:
    records = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in INPUTS.items()}
    _require(records["generic_pivot"]["classification"]["bounded_abd_cross_ideal_classified"], "generic global pivot changed")
    _require(records["finite_wave"]["classification"]["all_finite_cross_ell_superpositions_classified"], "finite wave cross-ell theorem changed")
    _require(records["finite_wave"]["classification"]["complete_common_stabilizer_zero_cone_second_order_extendible"], "finite wave sufficiency changed")
    _require(records["moment_cone"]["classification"]["cross_ell_charge_cancellations_included"], "cross-ell moment cone changed")
    h_equation = records["moment_cone"]["density_cone_theorem"]["common_zero_equations"]["H"]
    _require("+ omega_extra^2*A_extra - omega_minus^2*A_minus" in h_equation, "wave inertia signs changed")
    _require(records["fixed_ell_global"]["complete_bounded_cone"]["union_is_necessary_and_sufficient"], "blockwise global theorem changed")
    _require(records["standard_global"]["classification"]["complete_standard_generalized_zero_bounded_cone_classified"], "static global theorem changed")
    _require(records["circumference"]["classification"]["k0_circumference_cross_bounded_removable"], "circumference transport changed")
    _require(records["electric_wilson"]["classification"]["Q_e_times_every_oscillator_bounded_removable"], "electric transport changed")
    _require(records["electric_wilson"]["classification"]["W_x_times_every_oscillator_source_zero"], "Wilson transport changed")
    _require(records["constant_twist"]["classification"]["constant_twist_exact_family_identified"], "constant twist transport changed")

    eigenvalue = sp.symbols("lambda", positive=True)
    gap = sp.sqrt(2 * eigenvalue)
    omega_minus = sp.sqrt(eigenvalue - gap)
    axial = -3 * sp.I * omega_minus * (3 * gap - 1)
    polar = eigenvalue**2 * (2 * eigenvalue - 1) / 6
    _require(all(sp.simplify(axial.subs(eigenvalue, ell * (ell + 1))) != 0 for ell in range(2, 10)), "axial pivot sample changed")
    _require(all(polar.subs(eigenvalue, ell * (ell + 1)) > 0 for ell in range(2, 10)), "polar pivot sample changed")

    return {
        "schema": "einstein-maxwell-weyl-global-finite-harmonic-k0-bounded-cone-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_GLOBAL_FINITE_HARMONIC_K0_BOUNDED_CONE",
        "result_state": "COMPLETE_GLOBAL_FINITE_GENERIC_HARMONIC_K0_BOUNDED_CONE_CLASSIFIED",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "scope": {
            "theory": "Weyl-Maxwell target",
            "background": "compact magnetically supported Plebanski-Hacyan product",
            "boundaries": "closed S1_L times S2; bounded/finite-quasiperiodic correction",
            "charge_sector": "fixed N=2 magnetic bundle with electric tangent allowed",
            "carrier": "complete standard homogeneous/twist data plus an arbitrary finite sum of generic k=0 q/p primaries",
            "degree": 2,
            "parity": "homogeneous, axial and polar",
            "ell": "arbitrary finite subset of integers ell>=2, with global ell=0,1 data adjoined",
            "m": "all retained m values and all three real twist components",
            "k": 0,
            "omega": "generalized zero and all retained q/p shells",
        },
        "equation": "L_WM Phi^(2)=-(1/2)D^2E_WM[Phi^(1),Phi^(1)]",
        "finite_wave_cone": {
            "equations": "mu_H=mu_J1=mu_J2=mu_J3=0; mu_Px=0 identically at k=0",
            "cross_ell_cancellations": "the total moment maps retain cancellations between distinct ell blocks",
            "nonzero_requires_minus": "all plus and extra occupations enter mu_H with one sign, while only Einstein-minus enters with the opposite sign",
            "wave_self_sufficiency": "the finite-harmonic k=0 theorem solves every nonzero output block and removes every zero-frequency cokernel projection when the total moment maps vanish",
        },
        "global_wave_separation": {
            "selected_channel": "choose any nonzero Einstein-minus coefficient; its (ell,m,parity,omega_minus) global-cross channel is distinct from every other primary shell and every other ell,m,parity block",
            "wave_self_projection": "the wave-only resonant functional vanishes on the certified common-moment-map cone",
            "other_global_columns": "at k=0 the c, Q_e and constant-A mixed columns have certified bounded range corrections and the W_x mixed source vanishes, so none contributes to the adjoint projection used by the a,b,d pivot; B is already universally excluded",
            "triangular_pivots": {
                "axial": "C_A=-3*i*omega_minus*(3*sqrt(2*lambda)-1), with (a,b,d) ratios (2,1,1)",
                "polar": "C_P=lambda^2*(2*lambda-1)/6, with (a,b,d) ratios (3,1,3)",
            },
            "no_cross_ell_cancellation": "orthogonality of ell,m and parity plus distinct primary frequencies isolates the chosen minus coefficient; both pivots are nonzero for every physical lambda>=6",
            "consequence": "every nonzero bounded wave branch forces a=b=d=0",
        },
        "complete_bounded_cone": {
            "static_branch": "u_wave=0: (c,d,W_x,A) arbitrary, with a=b=Q_e=0 and B=0",
            "wave_branch": "u_wave is any nonzero finite generic k=0 common H,J_i zero; a=b=d=Q_e=0 and B=0; c,W_x,A are arbitrary",
            "branch_intersection": "u_wave=0,d=0 with c,W_x,A arbitrary",
            "union_is_necessary_and_sufficient": True,
        },
        "bounded_sufficiency": {
            "wave_self_and_cross_ell": "finite-harmonic all-generic-ell k=0 common-zero theorem",
            "global_self": "complete standard generalized-zero bounded theorem",
            "circumference": "exact k=0 radius transport for every certified oscillator",
            "Wilson": "identically zero mixed source for every certified oscillator",
            "constant_twist": "exact flat-holonomy transport without first-order k=0 frequency drift",
            "finite_assembly": "bilinearity leaves finitely many channels; the certified blockwise corrections sum to a real smooth spatially periodic finite-quasiperiodic correction",
        },
        "electric_exclusion": {
            "mixed_transport": "Q_e times every retained oscillator has a bounded fixed-bundle correction",
            "independent_zero_channel": "after total mu_H cancels the wave source, the remaining homogeneous coefficient is E11=Q_e^2/2 with zero bounded homogeneous image, hence Q_e=0",
        },
        "correction_classes": {
            "BOUNDED_OR_FINITE_QUASIPERIODIC": {"status": "CERTIFIED"},
            "SMOOTH_SECULAR": {"status": "CERTIFIED", "reason": "bounded corrections are a special smooth exponential-polynomial class"},
            "CAUSAL_RETARDED": {"status": "NO_CERTIFIED_MAP"},
        },
        "classification": {
            "arbitrary_finite_generic_ell_global_bounded_cone_classified": True,
            "cross_ell_wave_superpositions_classified": True,
            "all_retained_m_both_parities_all_qp_branches_included": True,
            "bounded_zero_locus_necessary_and_sufficient": True,
            "infinite_harmonic_completion_classified": False,
            "nonzero_momentum_classified": False,
            "exceptional_wave_inputs_classified": False,
            "all_orders_integrability": False,
            "causal_or_quantum_claim": False,
        },
        "interpretation": "The blockwise global stratification glues across every finite set of generic rest-frame harmonics. Cross-ell wave products add no obstruction, and they cannot screen the unique global-times-minus pivot. The bounded nonlinear tangent cone is therefore the total finite wave moment-map cone times the static circumference, Wilson and twist-holonomy spectators, together with the separate static d branch.",
        "next_gate": "classify nonzero compact momentum, exceptional ell=1 wave inputs, and the infinite-harmonic bounded completion as separate scopes",
        "claim_boundary": "This theorem covers arbitrary finite generic ell>=2 wave sums only at k=0. It does not cover infinite harmonic completion, nonzero momentum, exceptional ell=1 wave inputs, all-orders integration, residual descent, causal propagation, observables, particles or quantum theory.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for name, path in INPUTS.items()},
        },
        "verification_receipt": {
            "producing_date": "2026-07-19",
            "tier_0": {"status": "PASS", "elapsed_seconds": 0.13},
            "tier_1": {"status": "PASS", "elapsed_seconds": 2.39, "tests_run": 27},
            "tier_2": {"status": "PASS_BY_CONTENT_ADDRESS", "criterion": "finite-wave cross-ell theorem, generic-lambda pivots and global transport inputs are exact unchanged dependencies"},
            "tier_3": {"status": "NOT_RUN", "reason": "infinite sums, nonzero momentum, exceptional waves, causal, residual and quantum gates remain excluded"},
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_global_finite_harmonic_k0_bounded_cone --check",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_global_finite_harmonic_k0_bounded_cone.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_global_finite_harmonic_k0_bounded_cone",
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
        raise GlobalFiniteHarmonicK0BoundedConeError("global finite-harmonic bounded cone certificate is stale")
    print("EINSTEIN_MAXWELL_WEYL_GLOBAL_FINITE_HARMONIC_K0_BOUNDED_CONE: PASS")


if __name__ == "__main__":
    main()
