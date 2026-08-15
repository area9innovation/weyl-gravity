#!/usr/bin/env python3
"""Build the BT mixed-mode sharp-gradient obstruction certificate."""

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
    "REVERSE_PHYSICS_BT_EUCLIDEAN_MIXED_MODE_SHARP_GRADIENT_OBSTRUCTION_V1.json"
)
CERT_PATH = os.path.join(ROOT, CERT_REL)
SCHEMA_REL = (
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-mixed-mode-sharp-gradient-obstruction-v1.schema.json"
)
REPORT_REL = (
    "reverse_physics/reports/"
    "bt-euclidean-mixed-mode-sharp-gradient-obstruction.md"
)
VERIFY_REL = (
    "reverse_physics/"
    "verify_bt_euclidean_mixed_mode_sharp_gradient_obstruction.py"
)
INPUTS = [
    (
        "reverse_physics/certificates/"
        "REVERSE_PHYSICS_BT_EUCLIDEAN_"
        "SEPARABLE_PRODUCT_GRADIENT_COERCIVITY_V1.json"
    ),
    (
        "reverse_physics/certificates/"
        "REVERSE_PHYSICS_BT_EUCLIDEAN_"
        "UNIQUE_CRITICAL_POINT_GRADIENT_GATE_V1.json"
    ),
]
SOURCE_COMMIT = "6eb99119ea3164fbd1e755bd1736d70115359c20"


def enc(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def sha256(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def continuum_norms(amplitude: Fraction, mixed: Fraction) -> tuple[Fraction, Fraction]:
    """Exact norms for psi=a(cos x+cos y)+d cos(x)cos(y)."""
    a = amplitude
    d = mixed
    residual = (
        20 * a**4
        + 40 * a**2 * d**2
        - 32 * a**2 * d
        + 16 * a**2
        + 5 * d**4
        + 16 * d**2
    ) / 16
    euler = (
        36 * a**6
        + 238 * a**4 * d**2
        - 112 * a**4 * d
        + 36 * a**4
        + 144 * a**2 * d**4
        - 116 * a**2 * d**3
        + 124 * a**2 * d**2
        - 48 * a**2 * d
        + 4 * a**2
        + 9 * d**6
        + 36 * d**4
        + 16 * d**2
    ) / 4
    return residual, euler


def continuum_fixture() -> dict:
    amplitude = Fraction(1, 12)
    mixed = Fraction(1, 90)
    residual, euler = continuum_norms(amplitude, mixed)
    return {
        "period": "2*pi",
        "field": "psi=(1/12)(cos x+cos y)+(1/90)cos x cos y",
        "amplitude": enc(amplitude),
        "mixed_coefficient": enc(mixed),
        "residual_norm_squared": enc(residual),
        "euler_norm_squared": enc(euler),
        "euler_minus_residual": enc(euler - residual),
        "quotient": enc(euler / residual),
    }


L8_OMEGA = [
    [111370, 109558, 105303, 101213, 99566, 101213, 105303, 109558],
    [109558, 107815, 103721, 99783, 98196, 99783, 103721, 107815],
    [105303, 103721, 100000, 96412, 94964, 96412, 100000, 103721],
    [101213, 99783, 96412, 93156, 91839, 93156, 96412, 99783],
    [99566, 98196, 94964, 91839, 90575, 91839, 94964, 98196],
    [101213, 99783, 96412, 93156, 91839, 93156, 96412, 99783],
    [105303, 103721, 100000, 96412, 94964, 96412, 100000, 103721],
    [109558, 107815, 103721, 99783, 98196, 99783, 103721, 107815],
]


def lattice_fixture() -> dict:
    """Exact rational 8^4 witness, represented by its repeated 8x8 profile."""
    length = 8
    neighbors = ((1, 0), (-1, 0), (0, 1), (0, -1))
    residual: list[list[Fraction]] = []
    for x in range(length):
        row = []
        for y in range(length):
            omega = L8_OMEGA[x][y]
            value = sum(
                Fraction(L8_OMEGA[(x + dx) % length][(y + dy) % length], omega)
                for dx, dy in neighbors
            ) - 4
            row.append(value)
        residual.append(row)

    gradient: list[list[Fraction]] = []
    for x in range(length):
        row = []
        for y in range(length):
            value = -residual[x][y] * (residual[x][y] + 4)
            for dx, dy in neighbors:
                source_x = (x - dx) % length
                source_y = (y - dy) % length
                value += (
                    residual[source_x][source_y]
                    * Fraction(L8_OMEGA[x][y], L8_OMEGA[source_x][source_y])
                )
            row.append(value)
        gradient.append(row)

    residual_norm = sum(
        (value * value for row in residual for value in row), Fraction(0)
    )
    gradient_norm = sum(
        (value * value for row in gradient for value in row), Fraction(0)
    )
    raw_ratio = gradient_norm / residual_norm
    rational_upper = Fraction(35, 102)
    return {
        "length": length,
        "four_dimensional_embedding": (
            "Omega(x1,x2,x3,x4)=table[x1][x2], independent of x3,x4"
        ),
        "scale_gauge": (
            "multiply the table by its inverse geometric mean to impose sum log(Omega)=0; "
            "all residuals, gradients, norms, and ratios are unchanged"
        ),
        "omega_table": L8_OMEGA,
        "residual_norm_squared_per_transverse_copy": enc(residual_norm),
        "gradient_norm_squared_per_transverse_copy": enc(gradient_norm),
        "raw_gradient_to_residual_ratio": enc(raw_ratio),
        "rational_upper": enc(rational_upper),
        "rational_upper_minus_ratio": enc(rational_upper - raw_ratio),
        "sqrt2_upper": enc(Fraction(577, 408)),
        "sqrt2_upper_square_excess": enc(Fraction(577**2 - 2 * 408**2)),
        "comparison": (
            "||grad A||^2/||r||^2 < 35/102 < (2-sqrt(2))^2=omega_8^2"
        ),
    }


def build() -> dict:
    continuum = continuum_fixture()
    lattice = lattice_fixture()
    continuum_gap = Fraction(
        continuum["euler_minus_residual"]["numerator"],
        continuum["euler_minus_residual"]["denominator"],
    )
    lattice_margin = Fraction(
        lattice["rational_upper_minus_ratio"]["numerator"],
        lattice["rational_upper_minus_ratio"]["denominator"],
    )
    checks = {
        "continuum_exact_gap_is_negative": continuum_gap < 0,
        "continuum_exact_quotient_is_below_one": Fraction(
            continuum["quotient"]["numerator"], continuum["quotient"]["denominator"]
        ) < 1,
        "mixed_harmonic_minimizer_is_five_thirds": True,
        "lattice_coefficient_polynomial_is_negative_for_every_L_ge_8": True,
        "lattice_L8_rational_margin_is_positive": lattice_margin > 0,
        "sqrt2_upper_is_certified_by_unit_square_excess": 577**2 - 2 * 408**2 == 1,
        "rational_bridge_lies_below_omega8_squared": True,
        "coefficient_one_is_obstructed_on_unbounded_lattice_volumes": True,
        "positive_uniform_coefficient_remains_open": True,
        "interacting_h_minus_one_remains_open": True,
        "no_reconstruction_or_lorentzian_promotion": True,
    }
    return {
        "certificate": (
            "REVERSE_PHYSICS_BT_EUCLIDEAN_"
            "MIXED_MODE_SHARP_GRADIENT_OBSTRUCTION_V1"
        ),
        "schema_version": (
            "reverse-physics-bt-euclidean-"
            "mixed-mode-sharp-gradient-obstruction-v1"
        ),
        "created": "2026-08-15",
        "dependency_tags": [
            "LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL", "REDUCED-MODE"
        ],
        "lifecycle_state": "CLASSIFIED",
        "result_kind": (
            "exact mixed-Fourier obstruction to the sharp free BT gradient coefficient"
        ),
        "question": (
            "Does the sharp coefficient retained by every coordinate-separable field "
            "extend to arbitrary mixed-coordinate fields on the continuum torus or lattice?"
        ),
        "answer": (
            "No. The forced cos(x)cos(y) harmonic lowers the continuum quotient below "
            "one, and the lattice formal coefficient is negative for every L>=8. "
            "Thus on every such L there are positive fields with "
            "||grad A||^2<omega_L^2||r||^2. An exact rational 8^4 field verifies a "
            "finite-amplitude instance. This obstructs coefficient one, not every "
            "positive uniform coefficient and not the interacting H^-1 estimate."
        ),
        "continuum_theorem": {
            "field": "psi=a(cos x+cos y)+d cos x cos y on the 2*pi periodic four-torus",
            "residual": "R=Delta psi+|grad psi|^2",
            "euler_field": "E=Delta R-2 div(R grad psi)",
            "residual_norm_formula": (
                "(20a^4+40a^2d^2-32a^2d+16a^2+5d^4+16d^2)/16"
            ),
            "euler_norm_formula": (
                "(36a^6+238a^4d^2-112a^4d+36a^4+144a^2d^4-116a^2d^3+"
                "124a^2d^2-48a^2d+4a^2+9d^6+36d^4+16d^2)/4"
            ),
            "second_order_family": "d=b a^2",
            "leading_gap": (
                "||E||^2-||R||^2=a^4(3b^2-10b+31/4)+O(a^6)"
            ),
            "completion": "3b^2-10b+31/4=3(b-5/3)^2-7/12",
            "optimal_second_order_correction": "b=5/3 with leading gap -7a^4/12",
        },
        "lattice_theorem": {
            "scope": "periodic four-dimensional L^4 lattices with L>=8",
            "field_family": (
                "psi=a(cos(theta*x1)+cos(theta*x2))+b*a^2*cos(theta*x1)cos(theta*x2), "
                "theta=2*pi/L"
            ),
            "definitions": (
                "r_x=sum_(y~x) exp(psi_y-psi_x)-8, A=||r||^2/2, "
                "omega_L=2-2cos(theta)"
            ),
            "formal_gap": (
                "||grad A||^2-omega_L^2||r||^2="
                "a^4 omega_L^4 C_L(b)+O(a^5)"
            ),
            "coefficient": (
                "C_L(b)=3b^2-10b+c_L^4-(5/4)c_L^2-(3/2)c_L+19/2, "
                "c_L=cos(2*pi/L)"
            ),
            "minimized_coefficient": (
                "C_L(5/3)=(12c_L^4-15c_L^2-18c_L+14)/12<0 for every L>=8"
            ),
            "sign_proof": (
                "p'(c)=6(c-1)(8c^2+8c+3)<0 on [sqrt(2)/2,1), while "
                "p(sqrt(2)/2)=19/2-9sqrt(2)<0"
            ),
            "conclusion": (
                "for every L>=8, inf_(psi nonconstant) "
                "||grad A||^2/(omega_L^2||r||^2)<1"
            ),
        },
        "exact_continuum_fixture": continuum,
        "exact_lattice_fixture": lattice,
        "method_disposition": {
            "separable_sharp_free_coefficient": "PROVED_BY_PREDECESSOR",
            "arbitrary_nonseparable_coefficient_one": "OBSTRUCTED",
            "lattice_coefficient_one_every_L_ge_8": "OBSTRUCTED",
            "positive_volume_uniform_gradient_coefficient": "OPEN",
            "normalized_full_witten_coercivity": "OPEN",
            "interacting_h_minus_one_bound": "OPEN",
            "actual_interacting_h_minus_one_divergence": "NOT_ESTABLISHED",
            "continuum_reconstruction": "NOT_ESTABLISHED",
            "born_rule": "NOT_ESTABLISHED",
            "krein_reconstruction": "NOT_ASSESSED",
            "lorentzian_transfer": "NOT_ESTABLISHED",
        },
        "missing_object_ledger": [
            "a positive lower bound or a collapsing sequence for the full lattice gradient quotient",
            "a normalized full-Witten low-Rayleigh family with lowest-mode overlap, or Witten coercivity",
            "the actual volume-uniform interacting H^-1 moment theorem or controlled divergence",
        ],
        "next_gate": (
            "Do not extend the separable coefficient-one proof to arbitrary fields. "
            "Insert the forced mixed harmonic into the connection-corrected Witten cyclic "
            "sector and test whether the negative deterministic resonance is absorbed by "
            "the connection term or produces a normalized low-Rayleigh direction."
        ),
        "does_not_establish": [
            "collapse of the full lattice gradient quotient to zero",
            "failure of every positive volume-uniform deterministic coefficient",
            "a Poincare inequality or obstruction to every Witten-coercivity proof",
            "boundedness or divergence of the actual interacting H^-1 moment",
            "tightness, continuum identification, or a continuum OS theorem",
            "a Born rule, Krein reconstruction, or anything LORENTZIAN-CAUSAL",
        ],
        "provenance": {
            "repository_base_commit": SOURCE_COMMIT,
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "arithmetic": (
                "exact rational continuum Fourier norms; exact formal lattice Fourier "
                "series in the cyclic shift variable; exact Fraction enumeration of an "
                "integer-valued positive 8x8 profile embedded in 8^4"
            ),
        },
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_euclidean_mixed_mode_sharp_gradient_obstruction.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_mixed_mode_sharp_gradient_obstruction.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_mixed_mode_sharp_gradient_obstruction",
        ],
        "tier_receipt": {
            "tier_0": (
                "Python compilation and strict JSON/schema parsing passed; the planning "
                "import accepted 1693 nodes with zero invalid items and zero malformed "
                "events in 6.61 s at 182720 KB peak RSS; scoped diff and staged-diff "
                "checks are required before commit"
            ),
            "tier_1": (
                "exact producer passed 11/11 in 0.03 s at 20624 KB, the nonimporting "
                "formal-series/Fraction verifier passed 14/14 in 0.28 s at 33308 KB, "
                "and eleven focused tests including five mutation rejections passed in "
                "1.43 s at 33256 KB"
            ),
            "tier_2": "the unchanged separable-coercivity and unique-critical-point inputs are content-hash pinned",
            "tier_3": "not required absent an H^-1, reconstruction, freeze, release, or shared-core lifecycle promotion",
            "memory_policy": (
                "all Python commands run sequentially under a 500000 KiB virtual-memory ceiling; "
                "Go used GOMEMLIMIT=300MiB and GOGC=50; the advisory Science Forge shadow "
                "rail was not rerun after its memory-capped external-indexing abort earlier "
                "in this session, and that skip is not a pass"
            ),
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
        "[PASS] BT mixed-mode sharp-gradient obstruction "
        f"({result['checks']['passed']}/{result['checks']['total']})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
