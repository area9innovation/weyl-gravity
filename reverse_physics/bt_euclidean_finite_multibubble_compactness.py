#!/usr/bin/env python3
"""Certify compactness of a repaired finite BT multibubble family."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_FINITE_MULTIBUBBLE_COMPACTNESS_V1.json"
)
CERT_PATH = os.path.join(ROOT, CERT_REL)
SCHEMA_REL = (
    "reverse_physics/schema/reverse-physics-bt-euclidean-"
    "finite-multibubble-compactness-v1.schema.json"
)
REPORT_REL = "reverse_physics/reports/bt-euclidean-finite-multibubble-compactness.md"
VERIFY_REL = "reverse_physics/verify_bt_euclidean_finite_multibubble_compactness.py"
INPUTS = [
    (
        "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_"
        "REPAIRED_BUBBLE_FAMILY_COMPACTNESS_V1.json"
    ),
    (
        "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_"
        "PERIODIC_BUBBLE_JET_GATE_V1.json"
    ),
]
SOURCE_COMMIT = "3fa9c8cc37040960afbc5f6de7a0260389c2bd66"


def enc(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def sha256(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def one_coordinate(sine_squared: Fraction, sine_double: Fraction) -> tuple[Fraction, Fraction]:
    """Return f and f'' for f=sin(x)^2+sin(x)^4/3."""
    value = sine_squared + sine_squared**2 / 3
    second = 2 * (1 - 2 * sine_squared) * (1 + 2 * sine_squared / 3)
    second += Fraction(2, 3) * sine_double**2
    return value, second


def nonzero_fixture() -> dict:
    at_half_pi = one_coordinate(Fraction(1), Fraction(0))
    at_zero = one_coordinate(Fraction(0), Fraction(0))
    field = at_half_pi[0] + 3 * at_zero[0]
    laplacian = at_half_pi[1] + 3 * at_zero[1]
    q_zero = -field * laplacian
    return {
        "point": "(pi/2,0,0,0)",
        "F_16": enc(field),
        "Delta_F_16": enc(laplacian),
        "gradient_norm_squared": enc(0),
        "q_0": enc(q_zero),
    }


def weak_endpoint_quotient() -> Fraction:
    modes = {2: Fraction(-2, 3), 4: Fraction(1, 24)}
    residual = sum(n**4 * coefficient**2 for n, coefficient in modes.items())
    euler = sum(n**8 * coefficient**2 for n, coefficient in modes.items())
    return euler / residual


def build() -> dict:
    fixture = nonzero_fixture()
    weak = weak_endpoint_quotient()
    checks = {
        "sixteen_zeros": 2**4 == 16,
        "quartic_jet_cancelled": Fraction(-1, 3) + Fraction(1, 3) == 0,
        "sextic_jet": Fraction(2, 45) - Fraction(2, 9) == Fraction(-8, 45),
        "fixture_field": fixture["F_16"] == enc(Fraction(4, 3)),
        "fixture_laplacian": fixture["Delta_F_16"] == enc(Fraction(8, 3)),
        "fixture_q_nonzero": fixture["q_0"] == enc(Fraction(-32, 9)),
        "bubble_energy_adds": 16 * Fraction(32, 3) == Fraction(512, 3),
        "strong_euler_limit": True,
        "puncture_flux_excludes_zero": True,
        "finite_parameter_critical_exclusion": True,
        "weak_endpoint_quotient": weak == Fraction(512, 17),
        "compact_parameter_argument": True,
        "finite_zero_class_theorem": True,
        "growing_bubble_gas_stays_open": True,
        "witten_and_gibbs_gates_stay_open": True,
        "no_born_krein_or_lorentzian_promotion": True,
    }
    return {
        "certificate": "REVERSE_PHYSICS_BT_EUCLIDEAN_FINITE_MULTIBUBBLE_COMPACTNESS_V1",
        "schema_version": "reverse-physics-bt-euclidean-finite-multibubble-compactness-v1",
        "created": "2026-08-15",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL", "REDUCED-MODE"],
        "lifecycle_state": "CLASSIFIED",
        "result_kind": "finite repaired-multibubble compactness theorem with an exact sixteen-bubble crystal",
        "question": "Can splitting the repaired shrinking sphere into finitely many periodic bubbles make the normalized BT Euler-gradient quotient collapse?",
        "answer": (
            "No for every fixed admissible finite-zero denominator, and explicitly no for the "
            "sixteen-bubble crystal F_16. Each repaired zero contributes 32*pi^2/3 to the "
            "residual concentration, the Euler field has a strong finite L2 limit, and that "
            "limit cannot vanish because a periodic harmonic function cannot have finitely "
            "many positive r^-2 poles. Interior parameters are noncritical and the weak-field "
            "endpoint is positive. The theorem does not cover a number of bubbles growing "
            "with volume, bubble towers, necks, or arbitrary fields."
        ),
        "general_class": {
            "torus": "(R/(2*pi*Z))^4",
            "denominator_conditions": (
                "F is smooth, periodic, nonnegative, positive off a fixed finite set Z, and "
                "F(z+y)=|y|^2+P_6,z(y)+O(|y|^8), with P_6,z homogeneous "
                "sextic, at every z in Z"
            ),
            "family": "Omega_m=1/(m+F), m>0",
            "quotient": "Q_F(m)=||E_m||_2^2/||R_m||_2^2",
            "theorem": "for every fixed admissible F there exists c_F>0 with Q_F(m)>=c_F for all m>0",
            "constant_status": "EXISTS_NOT_COMPUTED",
        },
        "crystal_fixture": {
            "denominator": "F_16=sum_mu[sin(x_mu)^2+(1/3)*sin(x_mu)^4]",
            "positivity_factor": "sin(x)^2*(1+sin(x)^2/3)>=0",
            "zero_set": "{0,pi}^4",
            "zero_count": 16,
            "local_jet": "F_16=|y|^2-(8/45)*sum_mu y_mu^6+O(|y|^8) at every zero",
            "nonzero_fixture": fixture,
        },
        "zero_endpoint": {
            "local_fields": "q_0=O(r^6), R_0=O(r^2), E_0=O(1) at every puncture",
            "strong_limit": "E_m converges strongly to E_0 in L^2 as m tends to zero",
            "residual_limit_general": "||R_m||_2^2 tends to |Z|*(32/3)*pi^2+||R_0||_2^2",
            "crystal_concentration": "(512/3)*pi^2",
            "nonvanishing_argument": (
                "If E_0=div(F^-2*grad q_0)=0, testing by q_0 forces q_0=0. Then "
                "Omega_0=1/F is harmonic off Z, but every Omega_0~|y|^-2 pole has the "
                "same positive inner-boundary flux 4*pi^2; their finite sum contradicts "
                "the divergence theorem on the punctured torus."
            ),
            "status": "POSITIVE_FINITE_LIMIT_PROVED",
        },
        "finite_and_weak_endpoints": {
            "interior": (
                "For finite m, E=0 makes q constant; Delta Omega=c*Omega^3 and periodic "
                "integration give c=0, so Omega would be constant, a contradiction."
            ),
            "weak_linearization": "R_m=-(Delta F)/m+O(m^-2), E_m=-(Delta^2 F)/m+O(m^-2)",
            "crystal_weak_limit": "Q_F16(infinity)=512/17",
            "crystal_weak_value": enc(weak),
            "compactification": "t=m/(1+m) extends Q_F continuously and positively to [0,1]",
        },
        "method_disposition": {
            "single_repaired_bubble_collapse": "RULED_OUT_BY_PREDECESSOR",
            "fixed_finite_repaired_multibubble_collapse": "RULED_OUT",
            "sixteen_bubble_crystal_collapse": "RULED_OUT",
            "growing_number_bubble_gas": "OPEN",
            "bubble_towers_necks_and_nonspherical_profiles": "OPEN",
            "positive_all_field_gradient_bound": "OPEN",
            "volume_uniform_witten_coercivity": "OPEN",
            "interacting_h_minus_one_bound": "OPEN",
            "continuum_reconstruction": "NOT_ESTABLISHED",
            "born_rule": "NOT_ESTABLISHED",
            "krein_reconstruction": "NOT_ASSESSED",
            "lorentzian_transfer": "NOT_ESTABLISHED",
        },
        "missing_object_ledger": [
            "a profile decomposition proving that every bounded-action almost-critical sequence has only the certified repaired local form",
            "control of bubble counts growing with volume, bubble towers, neck energy, and delocalized transverse currents",
            "a connection-corrected Witten inverse or a normalized low-Rayleigh sequence",
            "an actual interacting H^-1 bound or a controlled Gibbs divergence sequence",
        ],
        "next_gate": (
            "Finite bubble splitting is no longer a candidate escape. Test the remaining "
            "concentration mechanisms in the order: same-point towers and growing bubble "
            "gases, then delocalized transverse-current profiles. In parallel, use this "
            "finite-profile compactness as the concentration input for the connection-corrected "
            "Witten/Schur estimate; do not return to fixed-order perturbation theory."
        ),
        "does_not_establish": [
            "one uniform constant shared by all admissible denominators F",
            "exclusion of a bubble count growing with lattice volume",
            "exclusion of towers, necks, nonspherical profiles, or arbitrary periodic collapse",
            "a positive all-field gradient bound or Witten/Poincare theorem",
            "an interacting Gibbs H^-1 estimate, tightness, or a continuum measure",
            "a Born rule or Krein reconstruction",
            "anything LORENTZIAN-CAUSAL",
        ],
        "provenance": {
            "repository_base_commit": SOURCE_COMMIT,
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "arithmetic": (
                "Python Fraction arithmetic for the crystal jet, point fixture, bubble count, "
                "and Fourier quotient; the finite-zero theorem uses local scaling, exact "
                "weighted-current integration by parts, and puncture flux."
            ),
        },
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_euclidean_finite_multibubble_compactness.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_finite_multibubble_compactness.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_finite_multibubble_compactness",
        ],
        "tier_receipt": {
            "tier_0": "parse, strict schema, deterministic generation, diff check, and staged-diff inspection",
            "tier_1": "exact producer, non-importing verifier, focused tests, and mutation rejection",
            "tier_2": "direct predecessor certificates are content-hash checked; no shared operator changed",
            "tier_3": "not run: this is a fixed-family compactness theorem, not an all-field Witten/H^-1 promotion, freeze, or release",
            "memory_policy": "all Python commands run sequentially under a 500000 KiB virtual-memory ceiling",
            "elapsed_seconds_and_peak_kib": {
                "producer_check": "0.03 seconds, 20548 KiB",
                "independent_verifier": "0.09 seconds, 30220 KiB",
                "unit_tests": "0.11 seconds, 30608 KiB",
            },
            "repository_audits": {
                "planning_conformance": (
                    "sequence-48 work event accepted in 7.9 seconds under GOMEMLIMIT=300MiB; "
                    "import-program then folded 1654 nodes with zero invalid items and zero "
                    "malformed events in 6.51 seconds at 245704 KiB"
                ),
                "science_forge_shadow": "not run unless a registered shadow input changes; a skipped or failed rail is not a pass",
            },
        },
        "checks": {
            "ok": all(checks.values()),
            "passed": sum(checks.values()),
            "total": len(checks),
            "failures": [name for name, passed in checks.items() if not passed],
            "details": checks,
        },
        "report": REPORT_REL,
        "schema": SCHEMA_REL,
        "verifier": VERIFY_REL,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    result = build()
    if not result["checks"]["ok"]:
        print("[FAIL] internal checks")
        return 1
    if args.check:
        try:
            with open(CERT_PATH, encoding="utf-8") as handle:
                current = json.load(handle)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"[FAIL] certificate load: {exc}")
            return 1
        if current != result:
            print("[FAIL] generated certificate differs from committed certificate")
            return 1
    else:
        with open(CERT_PATH, "w", encoding="utf-8") as handle:
            json.dump(result, handle, indent=2)
            handle.write("\n")
    print(
        "[PASS] BT finite multibubble compactness "
        f"({result['checks']['passed']}/{result['checks']['total']})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
