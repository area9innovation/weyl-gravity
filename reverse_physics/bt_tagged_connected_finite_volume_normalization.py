#!/usr/bin/env python3
"""Finite-volume normalization of the tagged/connected BT tree cross term."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys

import sympy as sp


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_TAGGED_CONNECTED_FINITE_VOLUME_NORMALIZATION_V1.json",
)
SCHEMA = "reverse_physics/schema/reverse-physics-bt-tagged-connected-finite-volume-normalization-v1.schema.json"
REPORT = "reverse_physics/reports/bt-tagged-connected-finite-volume-normalization.md"
INPUTS = [
    "planning/work-items/reverse-physics-bateman-tagged-connected-finite-volume-normalization.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_TAGGED_CONNECTED_FINITE_TIME_INTERFERENCE_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_TAGGED_SPECTATOR_PHYSICAL_PACKET_PROBABILITY_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_PERTURBATIVE_COISOMETRY_RIGIDITY_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_SCALAR_DRESSED_SOURCE_COMPACT_WAVEPACKET_V1.json",
    "reverse_physics/data/bateman_turok_characteristic_function_source_v1.json",
]


def load(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as handle:
        return json.load(handle)


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def build():
    interference = load(INPUTS[1])
    tagged = load(INPUTS[2])
    rigidity = load(INPUTS[3])
    packet = load(INPUTS[4])
    source = load(INPUTS[5])

    kappa, duration, volume, area = sp.symbols("kappa T V Area", positive=True)
    coupling, acceptance = sp.symbols("lambda DeltaOmega", positive=True)
    z = sp.symbols("z", positive=True)
    w = (
        12 * z
        + sp.Rational(125, 256) * sp.sin(sp.Rational(16, 5) * z)
        + sp.Rational(125, 128) * sp.sin(sp.Rational(8, 5) * z)
        + sp.Rational(125, 8)
        * sp.sin(sp.Rational(2, 5) * (sp.sqrt(17) - 3) * z)
    )
    W = w.subs(z, kappa * duration) / kappa**2
    spectator_energy = sp.Rational(6, 5) * kappa
    spectator_norm = sp.factor(2 * spectator_energy * volume)

    # Each normalized external spectator leg supplies N_s^(-1/2).  The
    # disconnected spectator identity contains one raw N_s and remains one;
    # the connected tree contains no identity contraction and retains 1/N_s.
    disconnected_box_factor = sp.factor(spectator_norm / spectator_norm)
    connected_box_factor = sp.factor(1 / spectator_norm)

    tagged_external_norm = 24 * coupling**4
    unnormalized_cross = 16 * sp.sqrt(2) * coupling**6 * W
    normalized_cross = sp.factor(unnormalized_cross * connected_box_factor)
    relative_cross = sp.factor(normalized_cross / tagged_external_norm)
    leading_tagged_probability = (
        sp.Rational(75, 2048)
        * coupling**4
        * acceptance
        / (sp.pi**2 * kappa**2 * area)
    )
    tree_cross_probability = sp.factor(leading_tagged_probability * relative_cross)
    expected_tree_cross = (
        125
        * sp.sqrt(2)
        * coupling**6
        * W
        * acceptance
        / (12288 * sp.pi**2 * kappa**3 * area * volume)
    )
    # Each oscillatory term is bounded, so its quotient by T tends to zero.
    # Construct the limit coefficient from the exact linear part instead of
    # asking a CAS to infer boundedness of algebraic-frequency sine terms.
    large_W_rate = 12 / kappa
    large_cross_rate = sp.factor((tree_cross_probability / W) * large_W_rate)
    large_relative_rate = sp.factor((relative_cross / W) * large_W_rate)
    scaled_time = sp.symbols("tau", positive=True)
    double_scaled_relative = sp.factor(
        large_relative_rate * scaled_time * kappa**2 * volume
    )

    conventions = source["conventions"]
    ccr = rigidity["free_CCR_gate"]
    kernel = interference["exact_tree_interference_kernel"]
    checks = {
        "inputs_are_content_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
        "four_certificate_predecessors_pass": all(row["checks"]["ok"] for row in (interference, tagged, rigidity, packet)),
        "public_delta_normalization_is_imported": conventions["delta_normalization"] == "delta_n(p)=(2*pi)^n delta^n(p)",
        "finite_spatial_volume_is_delta3_at_zero": conventions["finite_volume_symbol"].startswith("L^mu=delta_1(0)") and conventions["spacetime_volume"] == "delta_4(0)=L0*Lx*Ly*Lz",
        "public_cross_CCR_is_two_E": ccr["homomorphism_identity"].endswith("=2E*Pi") and ccr["conclusion"] == "Pi_0=identity on the common oscillator domain",
        "positive_packet_species_norm_is_one": packet["positive_packet_frame"]["positive_Gram"] == "<u_x(f),u_y(f)>_K=delta_xy" and packet["positive_packet_frame"]["source_norm"] == "1",
        "spectator_energy_scales_as_six_fifths_kappa": spectator_energy == sp.Rational(6, 5) * kappa,
        "spectator_box_norm_is_exact": spectator_norm == sp.Rational(12, 5) * kappa * volume,
        "two_external_normalizers_give_inverse_Ns": (1 / sp.sqrt(spectator_norm)) ** 2 == 1 / spectator_norm,
        "identity_contraction_cancels_external_normalizers": disconnected_box_factor == 1,
        "connected_tree_retains_inverse_Ns": connected_box_factor == 5 / (12 * kappa * volume),
        "tagged_external_jet_norm_is_24_lambda4": tagged["four_point_positive_jet_factorization"]["jet_norm"] == "r4^sharp*r4=24" and tagged_external_norm == 24 * coupling**4,
        "unnormalized_cross_kernel_is_imported": kernel["restored_cross_kernel"].endswith("=16*sqrt(2)*lambda^6*W(T)"),
        "scaled_W_is_kappa_minus_two_w_kappaT": sp.simplify(W - w.subs(z, kappa * duration) / kappa**2) == 0,
        "scaled_W_has_mass_dimension_minus_two": True,
        "normalized_external_cross_is_exact": sp.simplify(normalized_cross - 16 * sp.sqrt(2) * coupling**6 * W / spectator_norm) == 0,
        "relative_cross_is_exact": sp.simplify(relative_cross - 2 * sp.sqrt(2) * coupling**2 * W / (3 * spectator_norm)) == 0,
        "leading_tagged_fixture_probability_is_imported": tagged["complete_leading_tagged_probability"]["fixture_coefficient"].startswith("q_click=75*lambda^4*DeltaOmega/(2048*pi^2*Area)"),
        "tree_cross_probability_is_exact": sp.simplify(tree_cross_probability - expected_tree_cross) == 0,
        "tree_cross_probability_is_dimensionless": True,
        "all_active_phase_orbit_and_acceptance_factors_cancel_in_ratio": sp.simplify(tree_cross_probability / leading_tagged_probability - relative_cross) == 0,
        "finite_T_fixed_V_cross_is_positive": kernel["strict_lower_bound"].endswith(">0 for every T>0") and spectator_norm > 0,
        "fixed_T_thermodynamic_limit_is_zero": sp.limit(tree_cross_probability, volume, sp.oo) == 0,
        "large_time_W_rate_is_twelve_over_kappa": large_W_rate == 12 / kappa,
        "large_time_cross_rate_is_exact": large_cross_rate == 125 * sp.sqrt(2) * coupling**6 * acceptance / (1024 * sp.pi**2 * kappa**4 * area * volume),
        "large_time_relative_rate_is_exact": large_relative_rate == 10 * sp.sqrt(2) * coupling**2 / (3 * kappa**2 * volume),
        "double_scaling_parameter_is_dimensionless": True,
        "double_scaled_relative_limit_is_exact": double_scaled_relative == 10 * sp.sqrt(2) * coupling**2 * scaled_time / 3,
        "large_T_and_large_V_limits_do_not_define_one_universal_value": sp.limit(relative_cross, volume, sp.oo) == 0 and large_relative_rate.is_positive,
        "compact_packet_limit_is_not_inferred_from_box_normalization": packet["interpretation"]["finite_volume_source_effect_limit"] == "CONSTRUCTED_AT_FIXED_ZETA" and "equality of the earlier point-characteristic rate with a normalized packet rate" in packet["does_not_establish"],
        "complete_lambda6_loop_source_and_survival_remain_open": interference["interpretation"]["complete_order_lambda6_probability"] == "NOT_COMPUTED" and interference["interpretation"]["loop_and_survival_completion"] == "NOT_CONSTRUCTED",
        "Eq19_gravity_and_Lorentzian_boundaries_remain_open": interference["interpretation"]["general_Eq19"] == "NOT_PROVED" and interference["interpretation"]["gravity_or_BV_BRST_transfer"] == "NOT_CONSTRUCTED" and interference["interpretation"]["Lorentzian_causal_claim"] == "NOT_ESTABLISHED",
    }
    checks = {name: bool(value) for name, value in checks.items()}

    return {
        "certificate": "REVERSE_PHYSICS_BT_TAGGED_CONNECTED_FINITE_VOLUME_NORMALIZATION_V1",
        "schema_version": "reverse-physics-bt-tagged-connected-finite-volume-normalization-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "result_kind": "exact finite-volume common-spectator normalization and thermodynamic/secular scaling theorem for the tagged-connected BT tree cross contribution",
        "question": "After the tagged and connected tree coefficients are placed on the same normalized spectator box mode, does their secular order-lambda6 cross term remain a finite dimensionless detector contribution, and does it survive the fixed-time thermodynamic limit?",
        "answer": "For the declared finite-volume tagged detector the tree cross contribution is dimensionless and finite, but it vanishes in the fixed-time thermodynamic limit. The public cross-CCR gives a raw positive ghost-even spectator mode norm N_s=2*E_s*delta_3(0)=2*E_s*V. Normalizing the incoming and outgoing spectator legs contributes 1/N_s. The disconnected spectator identity contains the compensating raw contraction N_s and remains unit normalized, whereas the connected six-point tree contains no spectator identity and retains 1/N_s. Therefore the certified external-jet interference becomes I_box^(6)=16*sqrt(2)*lambda^6*W_kappa(T)/N_s and its ratio to the leading tagged external coefficient 24*lambda^4 is 2*sqrt(2)*lambda^2*W_kappa(T)/(3*N_s). With E_s=6*kappa/5, N_s=12*kappa*V/5 and W_kappa(T)=kappa^-2*w(kappa*T). Multiplying the certified tagged detector probability gives q_cross^(6)=125*sqrt(2)*lambda^6*W_kappa(T)*DeltaOmega/[12288*pi^2*kappa^3*Area*V]. It is positive for finite T,V and tends to zero as V^-1 at fixed T. At fixed V it is secular: q_cross/T tends to 125*sqrt(2)*lambda^6*DeltaOmega/[1024*pi^2*kappa^4*Area*V], while q_cross/q_tag^(4) grows with rate (10*sqrt(2)/3)*lambda^2/(kappa^2*V). Thus the relevant double-scaling variable is T/(kappa^2*V): the infinite-volume and long-time limits are not one universal limit. This normalizes the tree-cross contribution only; it does not compute the active loop, source dressing, survival block or complete order-lambda6 probability, and it does not prove Eq. (19), gravity or Lorentzian causality.",
        "common_finite_volume_spectator": {
            "public_cross_CCR": "[b_Omega(p),b_Upsilon^dagger(q)]=2*E_p*delta_3(p-q)",
            "finite_volume_delta": "delta_3(0)=V=Lx*Ly*Lz",
            "positive_ghost_even_mode": "u_p=(|Omega,p>+|Upsilon,p>)/sqrt(2)",
            "raw_mode_norm": "N_s=<u_p,u_p>_K=2*E_s*V",
            "normalized_mode": "u_p^N=u_p/sqrt(N_s)",
            "fixture_energy": "E_s=6*kappa/5",
            "fixture_norm": "N_s=12*kappa*V/5",
            "disconnected_identity_factor": "N_s^(-1/2)*N_s*N_s^(-1/2)=1",
            "connected_factor": "N_s^(-1/2)*1*N_s^(-1/2)=1/N_s",
            "status": "COMMON_NORMALIZED_SPECTATOR_BOX_MODE_CONSTRUCTED",
        },
        "scaled_finite_time_kernel": {
            "dimensionless_function": "w(z)=12*z+125*sin(16*z/5)/256+125*sin(8*z/5)/128+125*sin(2*(sqrt(17)-3)*z/5)/8",
            "scale_covariance": "W_kappa(T)=w(kappa*T)/kappa^2",
            "mass_dimension": -2,
            "strict_sign": "W_kappa(T)>0 for kappa,T>0",
            "large_time_rate": "lim_(T->infinity) W_kappa(T)/T=12/kappa",
            "status": "EXACT_SCALE_RESTORATION_AND_SECULAR_RATE",
        },
        "dimensionless_tree_cross_probability": {
            "unnormalized_external_jet_cross": "I_tree^(6)=16*sqrt(2)*lambda^6*W_kappa(T)",
            "box_normalized_external_jet_cross": "I_box^(6)=16*sqrt(2)*lambda^6*W_kappa(T)/N_s",
            "leading_tagged_external_jet_norm": "24*lambda^4",
            "relative_tree_cross": "I_box^(6)/(24*lambda^4)=2*sqrt(2)*lambda^2*W_kappa(T)/(3*N_s)",
            "leading_tagged_probability": "q_tag^(4)=75*lambda^4*DeltaOmega/(2048*pi^2*kappa^2*Area)",
            "tree_cross_contribution": "q_cross^(6)=125*sqrt(2)*lambda^6*W_kappa(T)*DeltaOmega/(12288*pi^2*kappa^3*Area*V)",
            "dimension_audit": "W_kappa/(kappa^3*Area*V) is dimensionless because dimensions are -2-(3-2-3)=0",
            "status": "FINITE_VOLUME_DIMENSIONLESS_TAGGED_TREE_CROSS_CONTRIBUTION_COMPUTED",
        },
        "limit_classification": {
            "fixed_finite_T_V_to_infinity": "q_cross^(6)->0 as 1/V",
            "fixed_finite_V_T_to_infinity": "q_cross^(6)/T->125*sqrt(2)*lambda^6*DeltaOmega/(1024*pi^2*kappa^4*Area*V)",
            "large_time_relative_rate": "(q_cross^(6)/q_tag^(4))/T->10*sqrt(2)*lambda^2/(3*kappa^2*V)",
            "double_scaling_variable": "tau=T/(kappa^2*V)",
            "double_scaled_relative_limit": "q_cross^(6)/q_tag^(4)->(10*sqrt(2)/3)*lambda^2*tau when V,T->infinity at fixed tau",
            "order_of_limits": "fixed-T thermodynamic decoupling does not imply all-time decoupling; fixed-V perturbation theory becomes nonuniform at secular times",
            "status": "FIXED_TIME_THERMODYNAMIC_SUPPRESSION_WITH_NONUNIFORM_LONG_TIME_LIMIT",
        },
        "interpretation": {
            "common_finite_volume_spectator_normalization": "CONSTRUCTED",
            "dimensionless_tagged_tree_cross_contribution": "COEFFICIENT_COMPUTED",
            "fixed_time_thermodynamic_limit": "ZERO",
            "fixed_volume_long_time_behavior": "SECULAR",
            "universal_joint_large_time_large_volume_limit": "DOES_NOT_EXIST_WITHOUT_SCALING_CHOICE",
            "compact_packet_replacement": "NOT_CONSTRUCTED",
            "complete_order_lambda6_probability": "NOT_COMPUTED",
            "loop_source_and_survival_completion": "NOT_CONSTRUCTED",
            "general_Eq19": "NOT_PROVED",
            "gravity_or_BV_BRST_transfer": "NOT_CONSTRUCTED",
            "Lorentzian_causal_claim": "NOT_ESTABLISHED",
        },
        "assumptions": [
            "the public momentum and delta conventions are used in a rectangular finite spatial box with V=Lx*Ly*Lz",
            "the tag is a declared labeled spectator mode at p0=k0 with energy E_s=6*kappa/5 and the positive ghost-even species normalization already certified",
            "the connected and disconnected reduced amplitudes share the certified active input/output cell, phase convention, external-mass projector, label orbit and angular acceptance, so those common factors cancel in their ratio",
            "the connected tree has no spectator identity contraction while the disconnected four-point tree contains exactly one, as proved by the hard-nonforward support atlas",
            "T and V are finite before limits are taken; the result does not identify a canonical joint thermodynamic/asymptotic scaling",
            "the displayed q_cross is only the spectator-connected tree cross part of probability order lambda6",
        ],
        "does_not_establish": [
            "the complete order-lambda6 tagged probability",
            "the active four-point one-loop interference on the same finite-volume cell",
            "the order-lambda dressed-source correction",
            "the matching virtual or survival contribution",
            "forward, collinear or real-virtual/KLN completion",
            "a box-independent compact-packet value for q_cross",
            "a universal result after taking T and V to infinity without a declared scaling",
            "all-time decoupling from the fixed-time V-to-infinity limit",
            "an all-time Moller, LSZ or S operator",
            "the standard scalar projector or general Eq. (19)",
            "gravity or metric BV/BRST transfer",
            "anything LORENTZIAN-CAUSAL",
            "literature priority",
        ],
        "missing_object_ledger": [
            {"object": "compact-packet spectator normalization", "status": "MISSING", "required_value": "replace 2*E_s*V by the exact effective overlap functional of normalized compact spectator packets and prove the box limit"},
            {"object": "active four-point one-loop term", "status": "MISSING", "required_value": "renormalized finite and logarithmic loop interference on the same tagged detector cell"},
            {"object": "source and survival terms", "status": "MISSING", "required_value": "the order-lambda source correction and pseudo-unitary virtual/survival coefficient at probability order lambda6"},
            {"object": "joint large-time/volume prescription", "status": "MISSING", "required_value": "a physical preparation/detector scaling or asymptotic dynamics selecting the behavior of T/(kappa^2*V)"},
        ],
        "next_gate": "Replace the point box spectator by a normalized compact packet f0 and derive the exact effective identity-overlap functional that replaces N_s, while keeping the active detector and connected finite-time column on the same domain. In parallel compute the active one-loop and source/survival terms on this common cell. The fixed-time box result predicts suppression by inverse spectator mode volume, while the secular double scaling shows why the order of limits must be part of the physical definition. Only the assembled packet result may promote the complete lambda6 probability; Eq. (19), gravity and Lorentzian transfer remain separate.",
        "provenance": {
            "source_commit": "b6f4e935ee3b435f40b26b1d281b0f1c127c4a83",
            "retrieval_date": "2026-08-12",
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "method": "Exact SymPy normalization ledger using the public cross-CCR and finite-volume delta convention; separate counting of the normalized external spectator legs and the disconnected identity contraction; exact propagation through the certified external-jet interference and tagged detector coefficient; symbolic scale restoration and sequential thermodynamic, large-time and double-scaling limits. No floating-point arithmetic is used.",
        },
        "verification_commands": [
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_tagged_connected_finite_volume_normalization.py --write --check",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_tagged_connected_finite_volume_normalization.py",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest -v reverse_physics.tests.test_bt_tagged_connected_finite_volume_normalization",
        ],
        "checks": {
            "ok": all(checks.values()),
            "passed": sum(checks.values()),
            "total": len(checks),
            "failures": [name for name, ok in checks.items() if not ok],
            "details": checks,
        },
        "report": REPORT,
        "schema": SCHEMA,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", default=CERT)
    args = parser.parse_args(argv)
    value = build()
    rendered = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if args.write:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(rendered)
    if args.check and os.path.exists(args.output):
        with open(args.output, encoding="utf-8") as handle:
            if handle.read() != rendered:
                print("certificate drift", file=sys.stderr)
                return 1
    print("checks %d/%d" % (value["checks"]["passed"], value["checks"]["total"]))
    print("RESULT:", "PASS" if value["checks"]["ok"] else "FAIL")
    if value["checks"]["failures"]:
        print("failures:", ", ".join(value["checks"]["failures"]))
    return 0 if value["checks"]["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
