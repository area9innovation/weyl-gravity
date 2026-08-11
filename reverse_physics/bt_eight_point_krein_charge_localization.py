#!/usr/bin/env python3
"""Exact charge localization of the BT eight-point Krein profile lift."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EIGHT_POINT_KREIN_CHARGE_LOCALIZATION_V1.json",
)
SCHEMA = (
    "reverse_physics/schema/"
    "reverse-physics-bt-eight-point-krein-charge-localization-v1.schema.json"
)
REPORT = "reverse_physics/reports/bt-eight-point-krein-charge-localization.md"
SOURCE = "f9841cb4"
INPUTS = [
    "planning/work-items/reverse-physics-bateman-eight-point-krein-charge-localization.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EIGHT_POINT_PROFILE_POSITIVITY_OBSTRUCTION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_FULL_SIGNED_QUADRATIC_CLOSURE_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_ZERO_MODE_EQ19_TRILEMMA_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_FINITE_PHYSICAL_MOLLER_COLUMN_V1.json",
]


def rat(value):
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def frac(value):
    return Fraction(value["numerator"], value["denominator"])


def load(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as handle:
        return json.load(handle)


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def rows(matrix):
    return [[str(value) for value in row] for row in matrix.tolist()]


def build():
    import sympy as sp

    profile = load(INPUTS[1])
    eq19 = load(INPUTS[2])
    zero_mode = load(INPUTS[3])
    moller = load(INPUTS[4])
    lift = profile["fibrewise_krein_lift"]
    rho_q = frac(lift["rho"])
    rho = sp.Rational(rho_q.numerator, rho_q.denominator)
    G = sp.Matrix([[0, -rho], [-rho, -2]])
    J = sp.Matrix([[0, 1], [1, 0]])
    S = sp.Matrix([[1, 1], [0, -rho]])
    C = sp.Matrix([[-rho, -1], [0, 1]])
    H0 = sp.diag(1, -1)
    H = sp.simplify(S * H0 * S.inv())
    Pplus = sp.simplify((sp.eye(2) + H) / 2)
    Pminus = sp.simplify((sp.eye(2) - H) / 2)
    f2 = sp.Matrix([0, 1])
    fplus = sp.simplify(Pplus * f2)
    fminus = sp.simplify(Pminus * f2)

    kappa = [
        sp.Rational(value["numerator"], value["denominator"])
        for value in profile["orientation_audit"]["profile_coefficients"]
    ]
    amplitudes = [sp.sqrt(-value / 2) for value in kappa]
    eta = sp.diag(G, G)
    Hmodule = sp.diag(H, H)
    Pplus_module = sp.diag(Pplus, Pplus)
    Pminus_module = sp.diag(Pminus, Pminus)
    B = sp.zeros(4, 2)
    B[1, 0] = amplitudes[0]
    B[3, 1] = amplitudes[1]
    Bplus = sp.simplify(Pplus_module * B)
    Bminus = sp.simplify(Pminus_module * B)
    K4 = sp.diag(*kappa)
    plus_gram = sp.simplify(Bplus.T * eta * Bplus)
    minus_gram = sp.simplify(Bminus.T * eta * Bminus)
    cross_pm = sp.simplify(Bplus.T * eta * Bminus)
    cross_mp = sp.simplify(Bminus.T * eta * Bplus)
    reconstructed = sp.simplify(
        plus_gram + minus_gram + cross_pm + cross_mp
    )

    checks = {
        "all_predecessor_certificates_pass": all(
            value["checks"]["ok"] for value in (profile, eq19, zero_mode, moller)
        ),
        "rho_and_gram_replayed": (
            rho_q == Fraction(819, 4000)
            and rows(G) == lift["single_fibre_gram"]
        ),
        "charge_basis_is_invertible": S.det() == -rho != 0,
        "charge_basis_is_null_cross": sp.simplify(S.T * G * S) == rho**2 * J,
        "certified_missing_leg_reconstructs_gram": (
            moller["minimal_public_Rt_compression"]["missing_leg_C"]
            == [["-rho", "-1"], ["0", "1"]]
            and sp.simplify(C.T * J * C) == G
        ),
        "charge_generator_is_transport_through_missing_leg": (
            sp.simplify(C.inv() * H0 * C) == H
        ),
        "transported_charge_generator_is_involutive": H**2 == sp.eye(2),
        "charge_generator_preserves_gram": sp.simplify(H.T * G + G * H)
        == sp.zeros(2),
        "charge_projectors_are_complementary": (
            Pplus**2 == Pplus
            and Pminus**2 == Pminus
            and Pplus * Pminus == sp.zeros(2)
            and Pplus + Pminus == sp.eye(2)
        ),
        "canonical_negative_line_splits_into_both_charges": (
            fplus != sp.zeros(2, 1)
            and fminus != sp.zeros(2, 1)
            and fplus + fminus == f2
        ),
        "positive_charge_component_is_null": (fplus.T * G * fplus)[0] == 0,
        "negative_charge_component_is_null": (fminus.T * G * fminus)[0] == 0,
        "cross_charge_pairing_is_minus_one": (
            (fplus.T * G * fminus)[0]
            == (fminus.T * G * fplus)[0]
            == -1
        ),
        "full_negative_norm_is_cross_interference": (
            (f2.T * G * f2)[0] == -2
        ),
        "profile_forward_block_replayed": rows(B) == lift["forward_block_B"],
        "profile_charge_components_are_eigenblocks": (
            Hmodule * Bplus == Bplus and Hmodule * Bminus == -Bminus
        ),
        "one_sided_positive_pullback_is_zero": plus_gram == sp.zeros(2),
        "one_sided_negative_pullback_is_zero": minus_gram == sp.zeros(2),
        "cross_terms_reconstruct_full_profile_effect": (
            cross_pm == cross_mp == K4 / 2 and reconstructed == K4
        ),
        "negative_Q_identification_is_refuted": (
            minus_gram == sp.zeros(2) and K4.rank() == 2
        ),
        "finite_order_lambda_Q1_boundary_replayed": (
            eq19["finite_mode_Eq19"]["disposition"]
            == "EQ19_PROVED_THROUGH_ORDER_LAMBDA_FOR_THE_FINITE_MODE_QUADRATIC_ZERO_MODE_COMPLETED_SECTOR"
            and eq19["finite_mode_Eq19"]["decomposition_through_order_lambda"].endswith(
                "Q_negative=0"
            )
        ),
        "zero_mode_charge_warning_replayed": (
            zero_mode["disposition"]["fixed_vacuum_charge_selection"]
            == "NOT_WELL_DEFINED_AS_AN_INVARIANT_QUOTIENT"
        ),
    }
    checks = {name: bool(value) for name, value in checks.items()}

    return {
        "certificate": "REVERSE_PHYSICS_BT_EIGHT_POINT_KREIN_CHARGE_LOCALIZATION_V1",
        "schema_version": "reverse-physics-bt-eight-point-krein-charge-localization-v1",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "result_kind": "exact charge localization of the minimal eight-point profile Krein lift and scoped Eq. 19 Q-remainder obstruction",
        "question": "Can the minimal fibrewise Krein lift of the negative eight-point profile effect be the purely negatively charged, trace-null Q remainder in Bateman-Turok Eq. (19)?",
        "answer": "No on the declared forced cross-Krein fibre. The certified missing leg C=[[-rho,-1],[0,1]] obeys C^T J C=G_missing and transports the actual O(1,1) target charge generator by H_G=C^-1 diag(1,-1) C=[[1,2/rho],[0,-1]]. Equivalently, the invariant charge basis consists of the two null lines n_plus=(1,0) and n_minus=(1,-rho), with S^T G_missing S=rho^2 J. The canonical norm-minus-two vector f2 used by both profile amplitudes decomposes as Pi_plus f2=(1/rho,0) and Pi_minus f2=(-1/rho,1). Each one-sided component is null; their mutual pairing is -1, so the full norm -2 is entirely the sum of the two cross-charge pairings. Applying these projectors to the complete two-fixture forward block gives B_plus^sharp B_plus=0 and B_minus^sharp B_minus=0, while B_plus^sharp B_minus=B_minus^sharp B_plus=K4/2 and their sum is the exact rank-two negative profile effect. Therefore the lift cannot be the one-sided negatively charged null Q remainder: that projection has zero pullback. The nonzero effect localizes in charge-zero positive/negative interference and would require a neutral-sector completion or additional dynamical trace. This is a fibre-level reduced-mode obstruction, not a construction or refutation of the all-order Eq. (19) projector identity.",
        "assumptions": [
            "The O(1,1) target charge action is transported to the pullback fibre through the exact certified missing leg C; its eigenlines are null and have charges plus and minus one.",
            "The profile lift and its two hard evaluation idempotents are exactly those certified in the predecessor; no additional pre-trace channel terms are inserted.",
            "Identification with the Eq. (19) Q remainder requires one-sided negative charge and null self-pullback on this declared fibre.",
            "The calculation classifies fibre charge support only; operator domains, zero-mode dynamics, and the generalized-Born trace remain external gates."
        ],
        "charge_fibre": {
            "rho": rat(rho_q),
            "gram": rows(G),
            "certified_missing_leg_C": rows(C),
            "target_metric_J": rows(J),
            "missing_leg_pullback_identity": "C^T*J*C=G",
            "null_charge_basis_S": rows(S),
            "charge_basis_gram": rows(sp.simplify(S.T * G * S)),
            "charge_basis_gram_identity": "S^T*G*S=rho^2*J",
            "diagonal_charge_generator": rows(H0),
            "transported_charge_generator": rows(H),
            "transported_charge_generator_identity": "H_G=S*diag(1,-1)*S^-1",
            "physical_transport_identity": "H_G=C^-1*diag(1,-1)*C",
            "involution": "H_G^2=I",
            "gram_invariance": "H_G^T*G+G*H_G=0",
            "positive_projector": rows(Pplus),
            "negative_projector": rows(Pminus)
        },
        "canonical_negative_line": {
            "f2": rows(f2),
            "positive_component": rows(fplus),
            "negative_component": rows(fminus),
            "positive_self_pairing": rat(0),
            "negative_self_pairing": rat(0),
            "positive_negative_pairing": rat(-1),
            "negative_positive_pairing": rat(-1),
            "full_pairing": rat(-2),
            "localization": "FULL_NEGATIVE_NORM_IS_ENTIRELY_CROSS_CHARGE"
        },
        "profile_charge_decomposition": {
            "full_forward_block": rows(B),
            "positive_charge_block": rows(Bplus),
            "negative_charge_block": rows(Bminus),
            "positive_self_pullback": rows(plus_gram),
            "negative_self_pullback": rows(minus_gram),
            "positive_negative_pullback": rows(cross_pm),
            "negative_positive_pullback": rows(cross_mp),
            "full_profile_effect": rows(K4),
            "reconstruction": "B_plus^sharp*B_minus+B_minus^sharp*B_plus=K4",
            "one_sided_negative_Q_pullback": "ZERO",
            "nonzero_effect_charge": "ZERO_FROM_PLUS_MINUS_CROSS_PAIRING"
        },
        "Eq19_boundary": {
            "Q_remainder_identification": "EXACTLY_REFUTED_ON_DECLARED_FIBRE",
            "reason": "The pure negative-charge projection is null and has zero pullback, whereas the certified profile effect has rank two and is nonzero.",
            "finite_mode_order_lambda_sector": "PROVED_WITH_Q1_ZERO_IN_PREDECESSOR",
            "relation_to_order_lambda": "COMPATIBLE_BUT_NOT_DERIVED; THE FOURTH_PROFILE_BLOCK IS HIGHER_COMPOSITE_DATA",
            "required_successor": "A neutral-sector higher-composite contribution or additional zero-mode/dynamical trace that produces the cross-charge term while satisfying the complete projector identity."
        },
        "disposition": {
            "charge_generator_on_forced_fibre": "CONSTRUCTED_EXACTLY",
            "one_sided_charge_lines": "NULL",
            "fourth_profile_effect_charge_support": "CROSS_CHARGE_TOTAL_ZERO",
            "profile_lift_equals_negative_Q_remainder": "EXACTLY_FALSE_ON_DECLARED_FIBRE",
            "neutral_higher_composite_operator": "NOT_CONSTRUCTED",
            "generalized_Born_trace": "NOT_CONSTRUCTED",
            "physical_fourth_probability": "NOT_ESTABLISHED",
            "Eq19_all_orders": "NOT_PROVED"
        },
        "does_not_establish": [
            "failure of the full Bateman-Turok Eq. (19)",
            "nonexistence of a neutral higher-composite completion",
            "nonexistence of additional zero-mode or vacuum trace terms",
            "a charge-compatible all-order projector pushforward",
            "a normalized fourth-event probability",
            "a complete 2->6 probability",
            "a spacetime Moller, LSZ, or S operator",
            "a gravitational or BRST lift",
            "anything LORENTZIAN-CAUSAL",
            "literature priority"
        ],
        "next_gate": "Compute the first neutral higher-composite or zero-mode projector block capable of producing the certified plus/minus cross term. It must reproduce both hard-profile amplitudes, preserve the exact charge generator and cross-CCR, reduce to Q1=0 in the certified order-lambda sector, and pass the finite-projector idempotence and generalized-Born trace tests. A purely negative-charge candidate is now excluded on this fibre before any continuum calculation.",
        "provenance": {
            "source_commit": SOURCE,
            "retrieval_date": "2026-08-12",
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS]
        },
        "verification_commands": [
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_eight_point_krein_charge_localization.py --check",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_eight_point_krein_charge_localization.py",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest -v reverse_physics.tests.test_bt_eight_point_krein_charge_localization"
        ],
        "checks": {
            "ok": all(checks.values()),
            "passed": sum(checks.values()),
            "total": len(checks),
            "failures": [name for name, ok in checks.items() if not ok],
            "details": checks
        },
        "report": REPORT,
        "schema": SCHEMA
    }


def canonical(value):
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def fast_check(path):
    try:
        with open(path, encoding="utf-8") as handle:
            value = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        print("[FAIL] recorded certificate:", exc)
        return 1
    inputs = value.get("provenance", {}).get("inputs", [])
    ok = (
        value.get("certificate")
        == "REVERSE_PHYSICS_BT_EIGHT_POINT_KREIN_CHARGE_LOCALIZATION_V1"
        and value.get("checks", {}).get("passed")
        == value.get("checks", {}).get("total")
        == 22
        and value.get("checks", {}).get("failures") == []
        and all(value.get("checks", {}).get("details", {}).values())
        and len(inputs) == 5
        and all(row.get("sha256") == sha256(row.get("path", "")) for row in inputs)
        and value.get("disposition", {}).get("Eq19_all_orders") == "NOT_PROVED"
    )
    print("FAST RESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--fast-check", action="store_true")
    parser.add_argument("--output", default=CERT)
    args = parser.parse_args(argv)
    if args.fast_check:
        return fast_check(args.output)
    value = build()
    rendered = canonical(value)
    if args.write:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(rendered)
    if args.check:
        try:
            with open(args.output, encoding="utf-8") as handle:
                recorded = canonical(json.load(handle))
        except (OSError, json.JSONDecodeError) as exc:
            print("[FAIL] recorded certificate:", exc)
            return 1
        if recorded != rendered:
            print("[FAIL] certificate drift")
            return 1
    print("checks %d/%d" % (value["checks"]["passed"], value["checks"]["total"]))
    print("RESULT:", "PASS" if value["checks"]["ok"] else "FAIL")
    print("charge generator:", value["charge_fibre"]["transported_charge_generator"])
    print("localization:", value["canonical_negative_line"]["localization"])
    return 0 if value["checks"]["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
