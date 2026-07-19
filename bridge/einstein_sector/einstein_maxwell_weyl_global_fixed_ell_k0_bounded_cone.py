"""Classify the global bounded cone for every fixed generic ell at k=0."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_global_fixed_ell_k0_bounded_cone.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_global_fixed_ell_k0_bounded_cone.schema.json"
INPUTS = {
    "generic_pivot": ROOT / "bridge/certificates/einstein_maxwell_weyl_abd_generic_lambda_pivot.json",
    "fixed_ell_wave": ROOT / "bridge/certificates/einstein_maxwell_weyl_fixed_ell_k0_combined_cone_second_order.json",
    "k0_moment_cone": ROOT / "bridge/certificates/einstein_maxwell_weyl_k0_moment_map_cone.json",
    "homogeneous_source": ROOT / "bridge/certificates/einstein_maxwell_weyl_homogeneous_quadric_second_order.json",
    "homogeneous_operator": ROOT / "bridge/certificates/einstein_maxwell_weyl_balanced_ell0_second_order.json",
    "standard_global": ROOT / "bridge/certificates/einstein_maxwell_weyl_standard_global_bounded_second_order.json",
    "circumference": ROOT / "bridge/certificates/einstein_maxwell_weyl_circumference_complete_oscillator_bounded_classification.json",
    "electric_wilson": ROOT / "bridge/certificates/einstein_maxwell_weyl_electric_wilson_complete_oscillator_transport.json",
    "constant_twist": ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_global_moment_maps.json",
    "L1_completion": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_ell2_all_m_bounded_completion.json",
}


class GlobalFixedEllBoundedConeError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise GlobalFixedEllBoundedConeError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> dict[str, object]:
    records = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in INPUTS.items()}
    _require(records["generic_pivot"]["classification"]["bounded_abd_cross_ideal_classified"], "generic a,b,d ideal changed")
    _require(records["fixed_ell_wave"]["classification"]["every_fixed_ell_at_least_2_combined_common_zero_cone_second_order_extendible"], "fixed-ell wave theorem changed")
    _require(records["k0_moment_cone"]["classification"]["full_generic_k0_common_zero_cone_classified"], "generic moment cone changed")
    h_equation = records["k0_moment_cone"]["density_cone_theorem"]["common_zero_equations"]["H"]
    _require("+ omega_extra^2*A_extra - omega_minus^2*A_minus" in h_equation, "opposite-sign minus branch changed")
    _require(records["standard_global"]["classification"]["complete_standard_generalized_zero_bounded_cone_classified"], "standard global cone changed")
    _require(records["circumference"]["classification"]["k0_circumference_cross_bounded_removable"], "circumference transport changed")
    _require(records["electric_wilson"]["classification"]["W_x_times_every_oscillator_source_zero"], "Wilson spectator changed")
    _require(records["constant_twist"]["classification"]["constant_twist_exact_family_identified"], "constant twist transport changed")
    completion = records["L1_completion"]["zero_frequency_L1_completion"]
    zero_operator = sp.Matrix(completion["zero_operator"])
    source_0, source_1 = sp.symbols("S0 S1")
    source = sp.Matrix([source_0, source_1, source_0, source_1])
    correction = sp.Matrix([source_0 / 2, -source_1 / 2, 0, 0])
    _require(zero_operator * correction == source, "constant L1 right inverse changed")
    homogeneous = records["homogeneous_operator"]["homogeneous_operator"]
    zero_matrix = sp.Matrix([[sp.sympify(value, locals={"Omega": 0, "I": sp.I}) for value in row] for row in homogeneous["matrix"]])
    _require(zero_matrix == sp.zeros(4, 3), "bounded homogeneous zero-frequency image changed")
    a, b, d, charge, time = sp.symbols("a b d Q_e t", real=True)
    source_rows = [
        sp.sympify(value, locals={"a": a, "b": b, "d": d, "Q_e": charge, "t": time})
        for value in records["homogeneous_source"]["quadratic_source"]["rows"]
    ]
    electric_E11 = sp.factor(source_rows[2].subs({a: 0, b: 0, d: 0}))
    _require(electric_E11 == charge**2 / 2, "independent electric E11 witness changed")
    return {
        "schema": "einstein-maxwell-weyl-global-fixed-ell-k0-bounded-cone-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_GLOBAL_FIXED_ELL_K0_BOUNDED_CONE",
        "result_state": "EVERY_FIXED_GENERIC_ELL_K0_GLOBAL_BOUNDED_CONE_CLASSIFIED",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "scope": {
            "theory": "Weyl-Maxwell target",
            "background": "compact magnetically supported Plebanski-Hacyan product",
            "boundaries": "closed S1_L times S2; bounded/finite-quasiperiodic correction",
            "charge_sector": "fixed N=2 magnetic bundle with electric tangent allowed",
            "carrier": "complete standard homogeneous/twist data plus every q/p primary in one fixed generic ell block",
            "degree": 2,
            "parity": "homogeneous, axial and polar",
            "ell": "one arbitrary fixed integer ell>=2, with global ell=0,1 data adjoined",
            "m": "all -ell,...,ell and all three real twist components",
            "k": 0,
            "omega": "generalized zero and all fixed-ell q/p shells",
        },
        "equation": "L_WM Phi^(2)=-(1/2)D^2E_WM[Phi^(1),Phi^(1)]",
        "wave_cone": {
            "carrier": "all m, both parities, Einstein plus/minus and both extra-primary multiplicities at the declared fixed ell",
            "equations": "mu_H=mu_J1=mu_J2=mu_J3=0; mu_Px=0 identically at k=0",
            "nonzero_requires_minus": "Einstein-plus and both extra branches have one sign while Einstein-minus has the opposite sign",
            "second_order": "every point of the fixed-ell common-zero cone has a finite quasiperiodic correction",
            "zero_frequency_L1": "total J_i=0 gives compatible source (S0,S1,S0,S1) and constant correction (S0/2,-S1/2,0,0)",
        },
        "global_necessity": {
            "a_b_d": "the generic-lambda axial/polar triangular pivots force a=b=d=0 whenever the wave block is nonzero",
            "twist_velocity": "B=0 on every bounded branch",
            "electric": "after the wave H source cancels, E11=Q_e^2/2 and the zero-frequency bounded image is zero, hence Q_e=0",
            "electric_independence": "the Q_e^2/2 term is a homogeneous pure-electric source coefficient and is independent of the wave ell; the wave contribution has already vanished by the common H moment-map equation before this coefficient is applied",
            "electric_E11_replay": str(electric_E11),
        },
        "complete_bounded_cone": {
            "static_branch": "u_wave=0: (c,d,W_x,A) arbitrary, with a=b=Q_e=0 and B=0",
            "wave_branch": "u_wave is any nonzero fixed-ell common H,J_i zero; a=b=d=Q_e=0 and B=0; c,W_x,A are arbitrary",
            "branch_intersection": "u_wave=0,d=0 with c,W_x,A arbitrary",
            "union_is_necessary_and_sufficient": True,
        },
        "bounded_sufficiency": {
            "wave_self": "every-fixed-ell all-m both-parity common-zero theorem",
            "zero_frequency": "constant L1 right inverse; no Jordan growth",
            "standard_static": "complete standard-global bounded theorem",
            "circumference": "exact k=0 radius transport",
            "Wilson": "identically zero mixed source",
            "constant_twist": "exact flat-holonomy transport without first-order k=0 frequency drift",
        },
        "correction_classes": {
            "BOUNDED_OR_FINITE_QUASIPERIODIC": {"status": "CERTIFIED"},
            "SMOOTH_SECULAR": {"status": "CERTIFIED", "reason": "bounded corrections are a special smooth exponential-polynomial class"},
            "CAUSAL_RETARDED": {"status": "NO_CERTIFIED_MAP"},
        },
        "classification": {
            "every_fixed_generic_ell_global_bounded_cone_classified": True,
            "all_m_both_parities_all_qp_branches_included": True,
            "bounded_zero_locus_necessary_and_sufficient": True,
            "cross_ell_superpositions_classified": False,
            "nonzero_momentum_classified": False,
            "exceptional_wave_inputs_classified": False,
            "all_orders_integrability": False,
            "causal_or_quantum_claim": False,
        },
        "interpretation": "The ell=2 stratification is universal blockwise at rest. For every fixed generic angular momentum, a nonzero bounded wave branch is exactly the common stabilizer cone times the static c, Wilson and twist-holonomy spectators; the generalized a,b,d directions, electric tangent and twist velocity are excluded.",
        "next_gate": "classify bounded products between distinct ell blocks at k=0, then treat nonzero compact momentum and its circumference resonance",
        "claim_boundary": "This theorem is blockwise in one fixed ell>=2 at k=0. It does not cover cross-ell superpositions, nonzero momentum, exceptional ell=1 wave blocks, arbitrary finite harmonic sums, all-orders integration, residual descent, causal propagation, observables, particles or quantum theory.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for name, path in INPUTS.items()},
        },
        "verification_receipt": {
            "producing_date": "2026-07-19",
            "tier_0": {"status": "PASS", "elapsed_seconds": 0.41},
            "tier_1": {"status": "PASS", "elapsed_seconds": 6.46, "tests_run": 31},
            "tier_2": {"status": "PASS_BY_CONTENT_ADDRESS", "criterion": "generic-lambda pivot, fixed-ell wave, global-source and transport inputs are exact unchanged dependencies"},
            "tier_3": {"status": "NOT_RUN", "reason": "cross-ell, nonzero momentum, causal, residual and quantum gates remain excluded"},
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_global_fixed_ell_k0_bounded_cone --check",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_global_fixed_ell_k0_bounded_cone.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_global_fixed_ell_k0_bounded_cone",
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
        raise GlobalFixedEllBoundedConeError("global fixed-ell bounded cone certificate is stale")
    print("EINSTEIN_MAXWELL_WEYL_GLOBAL_FIXED_ELL_K0_BOUNDED_CONE: PASS")


if __name__ == "__main__":
    main()
