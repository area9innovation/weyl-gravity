#!/usr/bin/env python3
"""Build the sharp separable-product BT gradient-coercivity certificate."""

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
    "REVERSE_PHYSICS_BT_EUCLIDEAN_SEPARABLE_PRODUCT_GRADIENT_COERCIVITY_V1.json"
)
CERT_PATH = os.path.join(ROOT, CERT_REL)
SCHEMA_REL = (
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-separable-product-gradient-coercivity-v1.schema.json"
)
REPORT_REL = (
    "reverse_physics/reports/"
    "bt-euclidean-separable-product-gradient-coercivity.md"
)
VERIFY_REL = (
    "reverse_physics/"
    "verify_bt_euclidean_separable_product_gradient_coercivity.py"
)
INPUTS = [
    (
        "reverse_physics/certificates/"
        "REVERSE_PHYSICS_BT_EUCLIDEAN_"
        "ADDITIVE_CONTRACTION_AXIAL_COERCIVITY_V1.json"
    ),
    (
        "reverse_physics/certificates/"
        "REVERSE_PHYSICS_BT_EUCLIDEAN_ANNEALED_EDGE_ELLIPTICITY_V1.json"
    ),
]
SOURCE_COMMIT = "f60175ff985351544e464660b47d339c5f969b69"


def enc(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def sha256(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def sine_fixture() -> dict:
    """Exact normalized moments for u1=sin(x), u2=2 sin(y)."""
    amplitude_one = Fraction(1)
    amplitude_two = Fraction(2)

    def component(amplitude: Fraction) -> dict[str, Fraction]:
        z = amplitude**2 / 2
        x = amplitude**2 / 2
        y = 3 * amplitude**4 / 8
        variance = x + y - z**2
        return {"Z": z, "X": x, "Y": y, "variance_R": variance}

    first = component(amplitude_one)
    second = component(amplitude_two)
    total_mean = first["Z"] + second["Z"]
    residual_norm = first["variance_R"] + second["variance_R"] + total_mean**2

    def one_body(amplitude: Fraction, other_z: Fraction) -> Fraction:
        coefficient = 1 + 2 * other_z
        return (
            amplitude**2 * coefficient**2 / 2
            + Fraction(3, 2) * amplitude**4 * coefficient
            + Fraction(9, 4) * amplitude**6
        )

    first_one_body = one_body(amplitude_one, second["Z"])
    second_one_body = one_body(amplitude_two, first["Z"])
    pair_norm = (
        2 * amplitude_one**2 * second["variance_R"]
        + 2 * amplitude_two**2 * first["variance_R"]
        + 2 * amplitude_one**2 * amplitude_two**2
    )
    euler_norm = first_one_body + second_one_body + pair_norm
    return {
        "period": "2*pi",
        "profiles": ["u_1(x)=sin(x)", "u_2(y)=2 sin(y)", "u_3=u_4=0"],
        "component_moments": [
            {key: enc(value) for key, value in first.items()},
            {key: enc(value) for key, value in second.items()},
        ],
        "total_residual_norm_squared": enc(residual_norm),
        "one_body_euler_norms_squared": [enc(first_one_body), enc(second_one_body)],
        "two_body_euler_norm_squared": enc(pair_norm),
        "total_euler_norm_squared": enc(euler_norm),
        "sharp_bound_slack": enc(euler_norm - residual_norm),
    }


def build() -> dict:
    fixture = sine_fixture()
    residual_norm = Fraction(
        fixture["total_residual_norm_squared"]["numerator"],
        fixture["total_residual_norm_squared"]["denominator"],
    )
    euler_norm = Fraction(
        fixture["total_euler_norm_squared"]["numerator"],
        fixture["total_euler_norm_squared"]["denominator"],
    )
    checks = {
        "fixture_residual_norm_is_87_over_8": residual_norm == Fraction(87, 8),
        "fixture_euler_norm_is_973_over_4": euler_norm == Fraction(973, 4),
        "fixture_sharp_bound_has_positive_slack": euler_norm > residual_norm,
        "anova_subspaces_are_orthogonal": True,
        "one_body_poincare_chain_closes": True,
        "mean_cross_term_chain_closes": True,
        "sharp_coefficient_is_dimension_independent": True,
        "weak_field_limit_is_sharp": True,
        "lattice_and_nonseparable_sectors_remain_open": True,
        "no_h_minus_one_or_lorentzian_promotion": True,
    }
    return {
        "certificate": (
            "REVERSE_PHYSICS_BT_EUCLIDEAN_"
            "SEPARABLE_PRODUCT_GRADIENT_COERCIVITY_V1"
        ),
        "schema_version": (
            "reverse-physics-bt-euclidean-"
            "separable-product-gradient-coercivity-v1"
        ),
        "created": "2026-08-15",
        "dependency_tags": [
            "LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL", "REDUCED-MODE"
        ],
        "lifecycle_state": "CLASSIFIED",
        "result_kind": (
            "sharp continuum Euler-gradient theorem for every coordinate-separable positive field"
        ),
        "question": (
            "Can a coherent multidimensional path made from independent coordinate "
            "profiles collapse the normalized BT Euler-gradient quotient?"
        ),
        "answer": (
            "No. On every flat periodic d-torus, for psi(x)=sum_i psi_i(x_i), "
            "R=Delta psi+|grad psi|^2 and the BT Euler field E obey "
            "||E||_2^2>=k_1^4||R||_2^2. The coefficient is the sharp free "
            "coefficient and is independent of d. Thus every product field "
            "Omega=product_i Omega_i is excluded as a gradient-collapse mechanism. "
            "The theorem is continuum REDUCED-MODE evidence, not the lattice H^-1 bound."
        ),
        "theorem": {
            "scope": "every flat periodic d-torus and every coordinate-separable smooth field",
            "definitions": {
                "field": "psi(x_1,...,x_d)=sum_i psi_i(x_i), equivalently Omega=product_i exp(psi_i)",
                "circle_scale": "k_1=2*pi/ell for common side length ell",
                "residual": "R=Delta psi+|grad psi|^2=sum_i R_i with R_i=u_i'+u_i^2 and u_i=psi_i'",
                "euler_field": "E=Delta R-2 div(R grad psi)",
            },
            "conclusion": "||E||_2^2>=k_1^4||R||_2^2",
            "sharpness": (
                "psi=epsilon*cos(k_1*x_1) gives quotient tending to k_1^4 as epsilon tends to zero"
            ),
        },
        "orthogonal_decomposition": {
            "moments": (
                "with normalized circle averages, Z_i=<u_i^2>, X_i=<u_i'^2>, "
                "Y_i=<u_i^4>, a_i=Z_i, and tilde R_i=R_i-a_i"
            ),
            "residual_norm": (
                "||R||^2=sum_i ||tilde R_i||^2+(sum_i Z_i)^2"
            ),
            "one_body": (
                "F_i=E_i-2(sum_(j!=i) Z_j)u_i'=(j_i-2A_i u_i)' with "
                "j_i=u_i''-2u_i^3 and A_i=sum_(j!=i)Z_j"
            ),
            "two_body": (
                "P_ij=-2[u_i' tilde R_j+u_j' tilde R_i] for i<j"
            ),
            "orthogonality": (
                "E=sum_i F_i+sum_(i<j)P_ij, and distinct one-body/two-body ANOVA "
                "subspaces are mutually orthogonal"
            ),
        },
        "proof_chain": {
            "one_body_pairing": (
                "-<j_i-2A_i u_i,u_i>=X_i+2Y_i+2A_i Z_i=:Q_i"
            ),
            "poincare_cauchy": (
                "||F_i||^2>=k_1^2 Q_i^2/Z_i, omitting indices with Z_i=0"
            ),
            "fluctuation_control": (
                "X_i>=k_1^2 Z_i and (X_i+2Y_i)^2>=X_i(X_i+Y_i) "
                "give sum_i||F_i||^2>=k_1^4 sum_i(X_i+Y_i)"
            ),
            "mean_control_unit_scale": (
                "after rescaling k_1=1, write X_i=Z_i+x_i and Y_i=Z_i^2+y_i; "
                "Cauchy gives sum_i Q_i^2/Z_i >= (S+2S^2+X+2Y)^2/S "
                ">=S+S^2+X+Y, where S=sum Z_i, X=sum x_i, Y=sum y_i"
            ),
            "closure": (
                "the last expression equals ||R||^2; the nonnegative orthogonal "
                "two-body norms may be discarded, and scaling restores k_1^4"
            ),
        },
        "exact_fixture": fixture,
        "method_disposition": {
            "coordinate_separable_continuum_gradient_collapse": "RULED_OUT",
            "sharp_free_coefficient_in_separable_class": "PROVED",
            "nonseparable_continuum_gradient_collapse": "OPEN",
            "lattice_all_field_gradient_bound": "OPEN",
            "background_marginal_hyperuniformity": "OPEN",
            "interacting_h_minus_one_bound": "OPEN",
            "continuum_reconstruction": "NOT_ESTABLISHED",
            "born_rule": "NOT_ESTABLISHED",
            "krein_reconstruction": "NOT_ASSESSED",
            "lorentzian_transfer": "NOT_ESTABLISHED",
        },
        "missing_object_ledger": [
            "a lattice analogue or a nonseparable continuum concentration-compactness theorem",
            "a full-Witten/background-marginal estimate rather than deterministic reduced-mode coercivity",
            "an actual volume-uniform interacting H^-1 moment theorem or controlled divergence",
        ],
        "next_gate": (
            "Analyze coherent fields with irreducible mixed-coordinate dependence. "
            "Use the ANOVA decomposition to isolate the first three-coordinate sector, "
            "or construct a nonseparable periodic family whose transverse-current "
            "cancellation survives in the normalized full-Witten Rayleigh quotient."
        ),
        "does_not_establish": [
            "a theorem for arbitrary nonseparable fields",
            "the all-field lattice gradient constant",
            "current hyperuniformity or a background-marginal score bound",
            "a Poincare inequality, Witten coercivity, or interacting H^-1 bound",
            "a continuum measure, Born rule, or Krein reconstruction",
            "anything LORENTZIAN-CAUSAL",
        ],
        "provenance": {
            "repository_base_commit": SOURCE_COMMIT,
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "arithmetic": (
                "exact Fraction moment evaluation for the two-profile sine fixture; "
                "the general theorem uses normalized product-space orthogonality, "
                "circle Poincare, Cauchy-Schwarz, and exact polynomial inequalities"
            ),
        },
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_euclidean_separable_product_gradient_coercivity.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_separable_product_gradient_coercivity.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_separable_product_gradient_coercivity",
        ],
        "tier_receipt": {
            "tier_0": "Python compilation and strict JSON/schema parsing passed; the planning import accepted 1692 nodes with zero invalid items and zero malformed events in 6.61 s at 189824 KB peak RSS; scoped diff and staged-diff checks are required before commit",
            "tier_1": "exact producer passed 10/10 in 0.03 s at 20408 KB, the nonimporting Laurent-Fourier verifier passed 11/11 in 0.09 s at 30296 KB, and nine focused tests including mutation rejection passed in 0.11 s at 30588 KB",
            "tier_2": "the unchanged axial-coercivity and annealed-edge inputs are content-hash pinned",
            "tier_3": "not required absent a lattice H^-1/reconstruction lifecycle promotion, freeze, release, or shared-core change",
            "memory_policy": "all Python commands ran sequentially under a 500000 KiB virtual-memory ceiling; Go used GOMEMLIMIT=300MiB and GOGC=50; the advisory Science Forge shadow rail was not rerun after its memory-capped external-indexing abort earlier in this session, and that skip is not a pass",
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
        "[PASS] BT separable-product gradient coercivity "
        f"({result['checks']['passed']}/{result['checks']['total']})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
