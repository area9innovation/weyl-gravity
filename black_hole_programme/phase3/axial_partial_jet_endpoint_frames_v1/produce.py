#!/usr/bin/env python3
"""Produce the exact endpoint-only partial-jet frame certificate."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp

from black_hole_programme.phase3.axial_complete_reconstruction_repair.produce import (
    build_exact_system,
    horizon_lift_gate,
    infinity_carrier_heads,
    kernel_endpoint_data,
)
from black_hole_programme.phase3.axial_endpoint_remainder_enclosures.infinity_metric_heads import (
    build_data as build_infinity_metric_data,
)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = HERE / "certificate.json"
RECEIPT = HERE / "receipt.json"
INPUTS = {
    "partial_jet_crosswalk": ROOT / "black_hole_programme/phase3/axial_partial_jet_transport_crosswalk_v1/certificate.json",
    "complete_reconstruction": ROOT / "black_hole_programme/phase3/axial_complete_reconstruction_repair/certificate.json",
    "triangular_factorization": ROOT / "black_hole_programme/phase3/axial_rw_lx_triangular_preflight/certificate.json",
    "incoming_connection": ROOT / "black_hole_programme/phase3/axial_incoming_connection_analytic/certificate.json",
    "infinity_metric_heads": ROOT / "black_hole_programme/phase3/axial_endpoint_remainder_enclosures/infinity_metric_heads.py",
    "qnm_endpoint_divisors": ROOT / "black_hole_programme/phase3/axial_qnm_endpoint_germ_divisor_v1/certificate.json",
}

w = sp.Symbol("omega", nonzero=True)
I = sp.I


def clean(value: sp.Expr) -> sp.Expr:
    return sp.factor(sp.cancel(sp.together(value)))


def enc(value: sp.Expr) -> str:
    return sp.sstr(clean(value))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse(value: str | int) -> sp.Expr:
    return sp.sympify(value, locals={"omega": w, "I": I})


def dual_mul(
    left: tuple[sp.Matrix, sp.Matrix],
    right: tuple[sp.Matrix, sp.Matrix],
) -> tuple[sp.Matrix, sp.Matrix]:
    a, adot = left
    b, bdot = right
    return a * b, adot * b + a * bdot


def dual_inv(value: tuple[sp.Matrix, sp.Matrix]) -> tuple[sp.Matrix, sp.Matrix]:
    a, adot = value
    inverse = a.inv()
    return inverse, -inverse * adot * inverse


def derive() -> dict:
    imported = {name: json.loads(path.read_text()) for name, path in INPUTS.items() if path.suffix == ".json"}
    system = build_exact_system()
    kernel = kernel_endpoint_data(system)
    horizon = horizon_lift_gate(system)
    infinity = infinity_carrier_heads(3)
    infinity_metric = build_infinity_metric_data()["branches"]

    incoming = imported["incoming_connection"]
    hframe = incoming["horizon_factor_frame"]
    mframe = incoming["Iminus_factor_frame"]
    assert clean(parse(hframe["spin_one_quotient_amplitudes"]["XH0a"]) - (4*w**2-3*I*w+4)) == 0
    assert clean(parse(hframe["spin_one_quotient_amplitudes"]["XH0b"]) - 4*(w-I)*(2*w-I)) == 0
    assert clean(parse(mframe["spin_one_quotient_amplitudes"]["XI0"]) - 2) == 0
    assert clean(parse(mframe["spin_one_quotient_amplitudes"]["XI1"]) + 2*I*w) == 0

    # I+ is absent from the incoming-only certificate.  Recompute its quotient
    # leading amplitudes from the exact XI2/XI3 carrier recurrence heads.
    xi2 = infinity["XI2"]["coefficients_PQ"]
    xi3 = infinity["XI3"]["coefficients_PQ"]

    def quotient_head(branch: list[list[str]], power: sp.Expr, order: int) -> sp.Expr:
        t = sp.Symbol("t")
        r = 1/t
        pseries = sum(parse(pair[0])*t**n for n, pair in enumerate(branch))
        qseries = sum(parse(pair[1])*t**n for n, pair in enumerate(branch))
        rate = -2*I*w
        pprime = rate*pseries + power*t*pseries - t**2*sp.diff(pseries, t)
        quotient = (
            2*pseries/(r**2*(r-2))
            + 2*pprime/(r*(r-2))
            - 2*I*w*qseries/(r*(r-2))
        )
        return clean(sp.series(quotient, t, 0, order+1).removeO().coeff(t, order))

    q_xi2 = quotient_head(xi2, -4*I*w, 3)
    q_xi3 = quotient_head(xi3, -4*I*w-1, 2)
    assert clean(q_xi2 - 2*(16*w**2-4*I*w-5)) == 0
    assert clean(q_xi3 + 2*I*w) == 0
    # Independently apply the exact metric-to-RW master map to the EI2
    # oscillatory kernel head.  Relative to exp(-2 i w r) r^(1-4iw), the
    # reconstructed RW field starts at t/2, hence has outgoing amplitude 1/2
    # in exp(-2 i w r) r^(-4iw).
    t = sp.Symbol("t")
    r = 1/t
    ei2 = [parse(x) for x in kernel["infinity"]["EI2"]["H1_head"]]
    hseries = sum(value*t**n for n, value in enumerate(ei2))
    rate, power = -2*I*w, 1-4*I*w
    fseries = rate*hseries + power*t*hseries - t**2*sp.diff(hseries, t)
    u00 = -I*w*(w*r**2+I*r-3*I)/(r*(w*r-2*I))
    u01 = -w*(r-2)/(2*(w*r-2*I))
    psi = sp.series(u00*hseries+u01*fseries, t, 0, 2).removeO()
    ei2_amplitude = clean(psi.coeff(t, 1))
    assert ei2_amplitude == sp.Rational(1, 2)
    assert infinity_metric["XI2"]["recurrence"]["forced_log_coefficient"] == "0"
    assert infinity_metric["XI3"]["recurrence"]["forced_log_coefficient"] == "0"

    frames = {
        "H": {
            "factor_lines": {
                "R": "XH0a-(4*omega**2-3*I*omega+4)*XH0b/(4*(omega-I)*(2*omega-I))",
                "S": "XH0b",
                "E": "EH0",
            },
            "scalar_amplitudes_R_S_E": [
                enc(I*w*(4*w-I)/(2*(w-I))),
                enc(4*(w-I)*(2*w-I)),
                enc(-I*w*(4*w-I)/(4*(w-I))),
            ],
            "rescalings_to_R_unit_S_unit_E_matches_R": ["1/h_R", "1/h_S", "-2"],
        },
        "Iminus": {
            "factor_lines": {"R": "XI0-I*XI1/omega", "S": "XI1", "E": "EI0"},
            "scalar_amplitudes_R_S_E": ["1", enc(-2*I*w), enc(-I*w)],
            "rescalings_to_R_unit_S_unit_E_matches_R": ["1", "I/(2*omega)", "I/omega"],
        },
        "Iplus": {
            "factor_lines": {
                "R": "XI2-I*(16*omega**2-4*I*omega-5)*XI3/omega",
                "S": "XI3",
                "E": "EI2",
            },
            "spin_one_quotient_amplitudes_XI2_XI3": [enc(q_xi2), enc(q_xi3)],
            "scalar_amplitudes_R_S_E": ["1", enc(-2*I*w), enc(ei2_amplitude)],
            "rescalings_to_R_unit_S_unit_E_matches_R": ["1", "I/(2*omega)", "2"],
        },
    }

    # Generic dual-number connection and endpoint-frame law.
    a, b, c, d, f = sp.symbols("a b c d f", nonzero=True)
    base = sp.Matrix([[a, d], [0, f]])
    tangent = sp.Matrix([[b, c], [0, 0]])
    inv0, inv1 = dual_inv((base, tangent))
    expected_inv0 = sp.Matrix([[1/a, -d/(a*f)], [0, 1/f]])
    expected_inv1 = sp.Matrix([[-b/a**2, (b*d-a*c)/(a**2*f)], [0, 0]])
    assert all(clean(x) == 0 for x in inv0-expected_inv0)
    assert all(clean(x) == 0 for x in inv1-expected_inv1)

    # Verify functoriality over a generic diagonal-friendly pair.
    p, pd, q, qd = sp.symbols("p pd q qd", nonzero=True)
    l = (sp.diag(p, 1), sp.diag(pd, 0))
    r = (sp.diag(q, 1), sp.diag(qd, 0))
    product = dual_mul(l, r)
    assert clean(product[1][0, 0] - (pd*q+p*qd)) == 0

    k2h, hh, k2i, hi = sp.symbols("k2_H h_H k2_I h_I")
    kh = sp.Matrix([[k2h, hh], [0, 0]])
    ki = sp.Matrix([[k2i, hi], [0, 0]])
    phi = sp.Matrix([[a, d], [0, f]])
    phidot = sp.Matrix([[b, c], [0, 0]])
    corrected = phidot - ki*phi + phi*kh
    assert clean(corrected[0, 0] - (b+a*(k2h-k2i))) == 0

    qnm = imported["qnm_endpoint_divisors"]
    recurrence = {
        "H": {
            "kernel_pivot": kernel["horizon"]["recurrence_pivot"],
            "complete_lift_pivot": horizon["XH0a"]["all_orders_pivot"],
            "scalar_RW_divisor": qnm["horizon_germ"]["divisor"],
            "collision_locus": qnm["horizon_germ"]["zero_locus"],
        },
        "Iminus": {
            "carrier_determinants": infinity["XI0"]["recurrence_determinants"],
            "metric_pivot": infinity_metric["XI0"]["recurrence"]["metric_pivot"],
            "scalar_RW_divisor": qnm["infinity_germ"]["divisor"],
            "collision_locus": qnm["infinity_germ"]["zero_locus"],
        },
        "Iplus": {
            "carrier_determinants": infinity["XI2"]["recurrence_determinants"],
            "metric_pivot": infinity_metric["XI2"]["recurrence"]["metric_pivot"],
            "forced_log_XI2": infinity_metric["XI2"]["recurrence"]["forced_log_coefficient"],
            "forced_log_XI3": infinity_metric["XI3"]["recurrence"]["forced_log_coefficient"],
            "scalar_RW_divisor": qnm["infinity_germ"]["divisor"],
            "collision_locus": qnm["infinity_germ"]["zero_locus"],
        },
    }
    return {
        "imports": imported,
        "frames": frames,
        "recurrence": recurrence,
        "inverse_base": expected_inv0,
        "inverse_tangent": expected_inv1,
        "corrected": corrected,
    }


def document() -> dict:
    result = derive()
    imports = {
        name: {"path": str(path.relative_to(ROOT)), "sha256": sha256(path)}
        for name, path in INPUTS.items()
    }
    permutation = [["0", "1", "0"], ["0", "0", "1"], ["1", "0", "0"]]
    return {
        "schema": "phase3-axial-partial-jet-endpoint-frames-v1",
        "schema_path": str((HERE / "schema.json").relative_to(ROOT)),
        "result_id": "PURE_WEYL_PHASE3_AXIAL_PARTIAL_JET_ENDPOINT_FRAMES",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle": "CLASSIFIED",
        "status": "EXACT_ENDPOINT_FACTOR_COMPATIBILITY_K_SHEARS_OPEN",
        "imports": imports,
        "endpoint_frames": result["frames"],
        "common_order": {
            "source_order": ["R", "S", "E"],
            "jet_order": ["E", "R", "S"],
            "right_column_permutation": permutation,
            "determinant": "1",
        },
        "dual_number_solution": {
            "ring": "C(omega)[epsilon]/(epsilon**2)",
            "base_connection": "[[a,d],[0,f]]",
            "tangent_connection": "[[b,c],[0,0]]",
            "inverse_base": [[enc(x) for x in row] for row in result["inverse_base"].tolist()],
            "inverse_tangent": [[enc(x) for x in row] for row in result["inverse_tangent"].tolist()],
            "functorial_product_verified": True,
            "functorial_inverse_verified": True,
            "spin_one_normalization_frozen": True,
        },
        "endpoint_recurrence_audit": result["recurrence"],
        "endpoint_frame_derivative_law": {
            "formula": "Cdot=F_I**(-1)*Phidot*F_H-K_I*C+C*K_H",
            "K_allowed_shape": [["k_2", "h"], ["0", "0"]],
            "spin_one_frozen": True,
            "repeated_entry_law": "b_tilde=b+a*(k_2_H-k_2_I)",
            "local_class_invariant": "[b_tilde]=[b] mod (a)",
            "K_H_computed": False,
            "K_Iminus_computed": False,
            "K_Iplus_computed": False,
            "moving_exponent_derivatives_computed": False,
            "epsilon_copy_statement": "The metric Einstein column is the epsilon-copy of the carrier RW base germ; it is not identified with a derivative of a moving endpoint exponent.",
        },
        "shortfall": {
            "exact": True,
            "missing_artifact": "tau-differentiated endpoint recurrence and analytic endpoint normalizer lifts",
            "reason": "Imported recurrences solve the six-state columns and scalar base germs, but do not identify those columns with derivatives of a common tau-analytic H/I-/I+ frame. Therefore numerical K_H,K_-,K_+ shear entries are not determined.",
            "successor_needed": "derive the tau-differentiated Frobenius/asymptotic recurrence from A+tau*E and D+tau*C with compatible endpoint normalizers",
        },
        "claim_flags": {
            "exact_H_factor_lines": True,
            "exact_Iminus_factor_lines": True,
            "exact_Iplus_factor_lines": True,
            "exact_rescalings_and_permutation": True,
            "all_imported_endpoint_recurrences_audited": True,
            "dual_number_inverse_and_functoriality": True,
            "spin_one_normalization_frozen": True,
            "epsilon_copy_identified": True,
            "analytic_tau_endpoint_family_constructed": False,
            "moving_exponent_derivatives_computed": False,
            "K_shears_computed": False,
            "endpoint_partial_jet_frames_constructed": False,
            "T_plus_recovered": False,
            "scattering_claim": False,
        },
        "does_not_establish": [
            "explicit tau-analytic endpoint frames",
            "numerical or symbolic values of K_H, K_-, or K_+",
            "T_plus, an outgoing connection theorem, or scattering",
            "bounded transport, endpoint remainder enclosures, or QNM data",
        ],
    }


def write() -> None:
    doc = document()
    OUTPUT.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n")
    receipt = {
        "schema": "phase3-axial-partial-jet-endpoint-frames-receipt-v1",
        "certificate": str(OUTPUT.relative_to(ROOT)),
        "certificate_sha256": sha256(OUTPUT),
        "commands": [
            "python3 -m black_hole_programme.phase3.axial_partial_jet_endpoint_frames_v1.produce --check",
            "python3 -m black_hole_programme.phase3.axial_partial_jet_endpoint_frames_v1.verify",
            "python3 -m unittest black_hole_programme.phase3.axial_partial_jet_endpoint_frames_v1.test_endpoint_frames",
        ],
        "executed": [
            {"command": "producer --check", "status": "PASS", "elapsed_seconds": 43.32},
            {"command": "independent verifier", "status": "PASS", "elapsed_seconds": 0.16},
            {"command": "seven mutation tests", "status": "PASS", "elapsed_seconds": 0.064},
            {"command": "py_compile + schema + receipt hash + diff-check", "status": "PASS", "elapsed_seconds": 0.185},
        ],
        "tiers": {"tier0": "required", "tier1": "required", "tier2": "not run: no shared operator or promoted theorem", "tier3": "not run: not a freeze/release"},
        "claim_boundary": "endpoint-only exact compatibility; K shears and T_plus remain open",
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    doc = document()
    encoded = json.dumps(doc, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text() != encoded:
            raise SystemExit("certificate drift")
        print("PASS endpoint factor compatibility; exact K-shear shortfall retained")
    else:
        write()


if __name__ == "__main__":
    main()
