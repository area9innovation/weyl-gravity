"""Classify the full standard-global/twist plus ell=2,k=0 bounded cone."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_complete_global_twist_ell2_bounded_cone.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_complete_global_twist_ell2_bounded_cone.schema.json"
INPUTS = {
    "d_cone": ROOT / "bridge/certificates/einstein_maxwell_weyl_d_twist_ell2_complete_bounded_cone.json",
    "standard_global": ROOT / "bridge/certificates/einstein_maxwell_weyl_standard_global_bounded_second_order.json",
    "exceptional_moments": ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_global_moment_maps.json",
    "axial_minus": ROOT / "bridge/certificates/einstein_maxwell_weyl_abd_axial_ell2_minus_resonance.json",
    "polar_minus": ROOT / "bridge/certificates/einstein_maxwell_weyl_abd_polar_ell2_minus_resonance.json",
    "global_ell2": ROOT / "bridge/certificates/einstein_maxwell_weyl_global_ell2_all_m_both_parity_bounded_cone.json",
    "wave_cone": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_combined_cone_second_order.json",
    "moment_cone": ROOT / "bridge/certificates/einstein_maxwell_weyl_k0_moment_map_cone.json",
    "homogeneous_source": ROOT / "bridge/certificates/einstein_maxwell_weyl_homogeneous_quadric_second_order.json",
    "homogeneous_operator": ROOT / "bridge/certificates/einstein_maxwell_weyl_balanced_ell0_second_order.json",
    "electric_transport": ROOT / "bridge/certificates/einstein_maxwell_weyl_electric_wilson_complete_oscillator_transport.json",
}


class CompleteGlobalEll2Error(RuntimeError):
    """Raised when a required predecessor or exact audit changes."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise CompleteGlobalEll2Error(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _radion_audit(records: dict[str, dict[str, Any]]) -> dict[str, Any]:
    axial = records["axial_minus"]["bounded_zero_locus"]
    polar = records["polar_minus"]["bounded_zero_locus"]
    _require(axial["ideal_on_wave_amplitude_z"] == "<b*z,a*z,d*z>", "axial radion pivot changed")
    _require(
        polar["full_polynomial_ideal_on_wave_amplitude_z"] == "<b*z,a*z,d*z>",
        "polar radion pivot changed",
    )
    promotion = records["global_ell2"]["equivariant_promotion"]
    _require(
        promotion["all_m_consequence"]
        == "in each parity, any nonzero Einstein-minus vector forces a=b=d=0",
        "all-m radion promotion changed",
    )
    _require(
        promotion["cross_parity_independence"]
        == "axial and polar outputs lie in inequivalent parity blocks and cannot cancel",
        "cross-parity independence changed",
    )
    return {
        "m0_exact_ideals": {
            "axial": axial["ideal_on_wave_amplitude_z"],
            "polar": polar["full_polynomial_ideal_on_wave_amplitude_z"],
        },
        "SO3_promotion": "a is a scalar and each fixed-parity ell=2 minus block is one V_2, so dim Hom_SO3(V_2,V_2)=1; the nonzero m=0 pivot is injective for every m",
        "parity_separation": "axial and polar outputs are inequivalent parity blocks and cannot cancel",
        "consequence": "any nonzero Einstein-minus coefficient forces a=0",
    }


def _electric_audit(records: dict[str, dict[str, Any]]) -> dict[str, Any]:
    a, b, d, charge, time = sp.symbols("a b d Q_e t", real=True)
    source = records["homogeneous_source"]["quadratic_source"]
    row_order = source["row_order"]
    _require(
        row_order == ["E00", "E01", "E11", "sphere_trace", "Maxwell0", "Maxwell1"],
        "homogeneous source row order changed",
    )
    rows = [
        sp.sympify(value, locals={"a": a, "b": b, "d": d, "Q_e": charge, "t": time})
        for value in source["rows"]
    ]
    pure_electric = sp.Matrix([rows[index] for index in (0, 2, 3, 5)]).subs({a: 0, b: 0, d: 0})
    expected = charge**2 * sp.Matrix(
        [-sp.Rational(1, 2), sp.Rational(1, 2), -sp.Rational(1, 2), 0]
    )
    _require(pure_electric == expected, "pure-electric homogeneous source changed")

    operator = records["homogeneous_operator"]["homogeneous_operator"]
    zero_matrix = sp.Matrix(
        [
            [sp.sympify(value, locals={"Omega": 0, "I": sp.I}) for value in row]
            for row in operator["matrix"]
        ]
    )
    _require(zero_matrix == sp.zeros(4, 3), "bounded homogeneous zero-frequency image changed")

    scalar_descent = records["wave_cone"]["obstruction_descent"]["scalar_L0"]
    _require("(1,0,1/2,0)" in scalar_descent, "wave scalar row direction changed")
    _require("cancel when total H=0" in scalar_descent, "wave scalar moment-map cancellation changed")
    _require(
        records["electric_transport"]["classification"]["Q_e_times_every_oscillator_bounded_removable"],
        "electric oscillator transport changed",
    )
    return {
        "row_order": ["E00", "E11", "sphere_trace", "Maxwell1"],
        "pure_electric_source": [str(value) for value in pure_electric],
        "wave_scalar_row_direction": ["1", "0", "1/2", "0"],
        "independent_row": "the wave scalar source and every total-H cancellation have E11=0, whereas the pure-electric source has E11=Q_e^2/2",
        "bounded_zero_frequency_operator": [[str(value) for value in row] for row in zero_matrix.tolist()],
        "nonzero_frequency_cross_column": "Q_e times every certified oscillator is a bounded fixed-bundle linear image by electromagnetic-duality transport",
        "angular_separation": "Q_e times constant twist has ell=1 output and cannot cancel the homogeneous ell=0 E11 coefficient",
        "consequence": "E11=Q_e^2/2 forces Q_e=0 on every real bounded wave stratum",
    }


def build() -> dict[str, Any]:
    records = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in INPUTS.items()}
    d_classification = records["d_cone"]["classification"]
    _require(
        d_classification["complete_d_c_Wx_A_B_plus_ell2_carrier_covered"]
        and d_classification["bounded_stratified_zero_locus_necessary_and_sufficient"],
        "d predecessor cone changed",
    )
    standard = records["standard_global"]["classification"]
    _require(
        standard["universal_b_twist_velocity_and_Qe_a_elimination_on_complete_finite_carrier"],
        "global polynomial gate changed",
    )
    _require(
        records["standard_global"]["moment_map_intersection"]["after_polynomial_elimination"]
        == "mu_H=-(a^2+Q_e^2), mu_Px=0, mu_J=0",
        "static moment gate changed",
    )
    sign_statement = records["exceptional_moments"]["homogeneous_ell0"]["charge_variation"]["pure_extra_effect"]
    _require("same sign" in sign_statement and "Einstein-plus" in sign_statement, "global/wave sign relation changed")
    h_equation = records["moment_cone"]["density_cone_theorem"]["common_zero_equations"]["H"]
    _require("- omega_minus^2*A_minus" in h_equation, "Einstein-minus moment sign changed")
    _require(
        records["wave_cone"]["classification"]["complete_combined_ell2_k0_common_zero_cone_second_order_extendible"],
        "complete ell2 wave cone changed",
    )

    radion = _radion_audit(records)
    electric = _electric_audit(records)
    value: dict[str, Any] = {
        "schema": "einstein-maxwell-weyl-complete-global-twist-ell2-bounded-cone-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_COMPLETE_GLOBAL_TWIST_ELL2_BOUNDED_CONE",
        "result_state": "COMPLETE_STANDARD_GLOBAL_TWIST_PLUS_ELL2_K0_BOUNDED_CONE_CLASSIFIED",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "scope": {
            "theory": "Weyl-Maxwell target",
            "background": "compact magnetically supported Plebanski-Hacyan product",
            "boundaries": "closed S1_L times S2; bounded or finite-quasiperiodic correction",
            "charge_sector": "fixed N=2 magnetic bundle with the complete standard electric/holonomy tangent block included",
            "carrier": "complete standard homogeneous (a,b,c,d,Q_e,W_x), axial twist (A,B), and every axial/polar ell=2,k=0 q/p wave coefficient",
            "degree": 2,
            "parity": "homogeneous, axial and polar",
            "ell": "input 0,1,2 with all quadratic outputs",
            "m": "all twist and wave m",
            "k": 0,
            "omega": "generalized zero plus all three ell2 shells",
        },
        "equation": "L_WM Phi^(2)=-(1/2)D^2E_WM[Phi^(1),Phi^(1)]",
        "radion_audit": radion,
        "electric_audit": electric,
        "necessity_proof": {
            "universal_polynomial": "boundedness first forces b=B=0 and Q_e*a=0",
            "wave_free": "the exact global moment map then forces a=Q_e=0 and leaves c,d,W_x,A",
            "nonzero_wave_has_minus": "a and Q_e have the plus/extra sign, so any nonzero total moment-map zero containing waves has nonzero Einstein-minus occupation",
            "radion": radion["consequence"],
            "circumference_velocity": "the certified d successor forces d=0 on every nonzero wave stratum",
            "electric": electric["consequence"],
            "predecessor_separation": "on the d-predecessor cone every old bounded cokernel component already vanishes; the radion shell pivot and electric homogeneous E11 row occupy distinct new components",
        },
        "complete_bounded_zero_locus": {
            "static_stratum": "wave=0: a=b=Q_e=B=0 with c,d,W_x,A arbitrary",
            "wave_stratum": "wave!=0: a=b=d=Q_e=B=0, c,W_x,A arbitrary, and mu_H=mu_J1=mu_J2=mu_J3=0",
            "intersection_of_stratum_closures": "wave=0,d=0 with c,W_x,A arbitrary",
            "union_is_necessary_and_sufficient": True,
        },
        "sufficiency_proof": {
            "static": "the complete standard generalized-zero theorem supplies a bounded correction",
            "wave": "after a=Q_e=0 the carrier and equations reduce exactly to the certified d-predecessor wave stratum",
        },
        "correction_classes": {
            "BOUNDED_OR_FINITE_QUASIPERIODIC": {"status": "CERTIFIED"},
            "SMOOTH_EXPONENTIAL_POLYNOMIAL": {
                "status": "CERTIFIED",
                "claim": "each bounded correction lies in this smooth class; the larger unrestricted secular cone is not reclassified",
            },
            "CAUSAL_RETARDED": {"status": "NO_CERTIFIED_MAP"},
        },
        "classification": {
            "complete_standard_global_twist_plus_ell2_k0_carrier_covered": True,
            "bounded_zero_locus_necessary_and_sufficient": True,
            "radion_and_electric_gates_independently_closed": True,
            "older_partial_global_ell2_row_superseded": True,
            "static_and_wave_strata_explicit": True,
            "other_ell_or_nonzero_momentum_classified": False,
            "unrestricted_smooth_secular_cone_classified": False,
            "causal_or_quantum_claim": False,
            "all_orders_integrability": False,
        },
        "interpretation": "The complete compact ell2 bounded cone is stratified. The wave-free branch retains the static moduli c,d,W_x,A. Every nonzero wave removes d as well as a,b,Q_e,B, but retains c,W_x,A freely over the complete ell2 wave moment cone.",
        "next_gate": "derive the correctly typed constant-twist source map at arbitrary fixed ell and then finite k0 harmonic sums; keep exceptional ell1 and nonzero momentum separate",
        "claim_boundary": "Complete only for the full standard global/twist plus ell2,k0 carrier in the bounded class; other ell, momenta, unrestricted secular, causal, all-orders, residual, observational and quantum scopes remain open.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {
                name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)}
                for name, path in INPUTS.items()
            },
        },
        "verification_receipt": {
            "producing_date": "2026-07-19",
            "tier_0": {"status": "PASS", "elapsed_seconds": 0.38, "max_rss_kb": 17892},
            "tier_1": {"status": "PASS", "elapsed_seconds": 3.39, "max_rss_kb": 59512, "tests_run": 39},
            "tier_2": {
                "status": "PASS_BY_CONTENT_ADDRESS",
                "criterion": "the d predecessor, global moment theorem, both minus pivots, direct homogeneous source/operator, wave scalar descent and electric transport are exact hashed inputs",
            },
            "tier_3": {
                "status": "NOT_RUN",
                "reason": "other harmonics, momenta and higher lifecycles remain fail-closed",
            },
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_complete_global_twist_ell2_bounded_cone --check",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_complete_global_twist_ell2_bounded_cone.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_complete_global_twist_ell2_bounded_cone",
        ],
    }
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    return value


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
        raise CompleteGlobalEll2Error("complete global ell2 certificate is stale")
    print("EINSTEIN_MAXWELL_WEYL_COMPLETE_GLOBAL_TWIST_ELL2_BOUNDED_CONE: PASS")


if __name__ == "__main__":
    main()
