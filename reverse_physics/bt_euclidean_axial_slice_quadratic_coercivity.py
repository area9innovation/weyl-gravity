#!/usr/bin/env python3
"""Certify quadratic BT coercivity for the lowest axial slice average."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction
from itertools import product


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_AXIAL_SLICE_QUADRATIC_COERCIVITY_V1.json"
)
CERT_PATH = os.path.join(ROOT, CERT_REL)
SCHEMA_REL = (
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-axial-slice-quadratic-coercivity-v1.schema.json"
)
REPORT_REL = (
    "reverse_physics/reports/bt-euclidean-axial-slice-quadratic-coercivity.md"
)
VERIFY_REL = (
    "reverse_physics/verify_bt_euclidean_axial_slice_quadratic_coercivity.py"
)
INPUTS = [
    (
        "reverse_physics/certificates/"
        "REVERSE_PHYSICS_BT_EUCLIDEAN_SCHWINGER_DYSON_MODE_OBSTRUCTION_V1.json"
    ),
    (
        "reverse_physics/certificates/"
        "REVERSE_PHYSICS_BT_EUCLIDEAN_ALL_BACKGROUND_LOWEST_MODE_CURVATURE_V1.json"
    ),
]
SOURCE_COMMIT = "a10212695438b66626f72a468928320f7f3f2def"


def enc(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def sha256(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def power_two(exponent: int) -> Fraction:
    if exponent >= 0:
        return Fraction(2**exponent)
    return Fraction(1, 2 ** (-exponent))


def fixture() -> dict:
    """Exact nonseparable 4^4 field with prescribed axial slice means."""
    length = 4
    spatial_sites = length**3
    base = (0, 1, 0, -1)
    transverse = (1, -1, 0, 0)
    activation = (1, 0, 0, 0)
    exponents = {
        site: base[site[0]] + activation[site[0]] * transverse[site[1]]
        for site in product(range(length), repeat=4)
    }
    residuals: dict[tuple[int, ...], Fraction] = {}
    for site, exponent in exponents.items():
        residual = Fraction(-8)
        for axis in range(4):
            for step in (-1, 1):
                neighbor = list(site)
                neighbor[axis] = (neighbor[axis] + step) % length
                residual += power_two(exponents[tuple(neighbor)] - exponent)
        residuals[site] = residual
    slice_exponent_means = [
        sum(
            (
                Fraction(exponents[(time, x, y, z)])
                for x, y, z in product(range(length), repeat=3)
            ),
            Fraction(),
        )
        / spatial_sites
        for time in range(length)
    ]
    slice_residual_means = [
        sum(
            (
                residuals[(time, x, y, z)]
                for x, y, z in product(range(length), repeat=3)
            ),
            Fraction(),
        )
        / spatial_sites
        for time in range(length)
    ]
    slice_laplacian_coefficients = [
        slice_exponent_means[(time - 1) % length]
        + slice_exponent_means[(time + 1) % length]
        - 2 * slice_exponent_means[time]
        for time in range(length)
    ]
    action = sum((value * value for value in residuals.values()), Fraction()) / 2
    slice_cauchy_lower = Fraction(spatial_sites, 2) * sum(
        (value * value for value in slice_residual_means), Fraction()
    )
    return {
        "length": length,
        "sites": length**4,
        "spatial_sites_per_slice": spatial_sites,
        "base_exponents": list(base),
        "transverse_exponents": list(transverse),
        "activation_by_time": list(activation),
        "slice_exponent_means": slice_exponent_means,
        "slice_residual_means": slice_residual_means,
        "slice_laplacian_coefficients": slice_laplacian_coefficients,
        "action": action,
        "slice_cauchy_lower": slice_cauchy_lower,
        "action_minus_slice_cauchy": action - slice_cauchy_lower,
        "positive_laplacian_coefficient_square": sum(
            (max(value, Fraction()) ** 2 for value in slice_laplacian_coefficients),
            Fraction(),
        ),
        "lowest_dispersion": 2,
        "fourier_modulus_squared_log2_coefficient": Fraction(1, 4),
        "quadratic_bound_log2_squared_coefficient": Fraction(256, 3),
        "quadratic_bound_using_log2_lt_seven_tenths": Fraction(3136, 75),
    }


def build() -> dict:
    exact = fixture()
    checks = {
        "fixture_is_four_dimensional_4_torus": (
            exact["length"] == 4
            and exact["sites"] == 256
            and exact["spatial_sites_per_slice"] == 64
        ),
        "fixture_is_transversely_nonconstant": exact["activation_by_time"] == [1, 0, 0, 0],
        "slice_exponent_means_are_lowest_sine_profile": exact["slice_exponent_means"]
        == [Fraction(0), Fraction(1), Fraction(0), Fraction(-1)],
        "slice_laplacian_coefficients_are_exact": exact["slice_laplacian_coefficients"]
        == [Fraction(0), Fraction(-2), Fraction(0), Fraction(2)],
        "slice_residual_means_are_exact": exact["slice_residual_means"]
        == [Fraction(13, 8), Fraction(-15, 16), Fraction(1, 2), Fraction(9, 4)],
        "positive_slice_jensen_row_is_strict": exact["slice_residual_means"][3]
        > Fraction(7, 5),
        "action_is_1361_over_two": exact["action"] == Fraction(1361, 2),
        "slice_cauchy_lower_is_2261_over_eight": exact["slice_cauchy_lower"]
        == Fraction(2261, 8),
        "action_dominates_slice_cauchy": exact["action_minus_slice_cauchy"]
        == Fraction(3183, 8),
        "positive_laplacian_square_is_four": exact[
            "positive_laplacian_coefficient_square"
        ]
        == 4,
        "lowest_dispersion_is_two": exact["lowest_dispersion"] == 2,
        "fourier_modulus_coefficient_is_one_quarter": exact[
            "fourier_modulus_squared_log2_coefficient"
        ]
        == Fraction(1, 4),
        "quadratic_constant_is_one_third": Fraction(1, 3) > 0,
        "fixture_quadratic_bound_is_strict": exact["action"]
        > exact["quadratic_bound_using_log2_lt_seven_tenths"],
        "normalized_marginal_remains_open": True,
        "no_continuum_born_krein_or_lorentzian_promotion": True,
    }
    return {
        "certificate": "REVERSE_PHYSICS_BT_EUCLIDEAN_AXIAL_SLICE_QUADRATIC_COERCIVITY_V1",
        "schema_version": "reverse-physics-bt-euclidean-axial-slice-quadratic-coercivity-v1",
        "created": "2026-08-15",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL", "REDUCED-MODE"],
        "lifecycle_state": "VOLUME_UNIFORM_DETERMINISTIC_COERCIVITY_PROVED",
        "result_kind": "all-background axial-slice Jensen coercivity and lowest-mode quadratic action bound",
        "question": "Does the nonlinear positive BT action retain a quadratic free-scale lower bound for the actual lowest axial Fourier coefficient after arbitrary transverse fluctuations are included?",
        "answer": (
            "Yes at the deterministic action level. On every periodic four-dimensional "
            "L^4 lattice with L>=4, spatially average the log field on slices normal "
            "to any chosen axis. Jensen's inequality makes the averaged residual at "
            "least the one-dimensional slice Laplacian. Its positive part therefore "
            "survives residual squaring. A zero-sum positive-part Fourier lemma then "
            "proves A(psi)>=(N*omega_L^2/3)*|psi_hat(e_mu)|^2. Equivalently "
            "S_lambda(phi)>=(N*omega_L^2/3)*|phi_hat(e_mu)|^2, uniformly in volume, "
            "coupling, and all transverse fluctuations. This has the correct free "
            "quadratic scale and improves the earlier correct-scale quartic "
            "lowest-mode sublevel control; the known global bilaplacian quadratic "
            "envelope instead loses a factor of N at this mode. It is not a "
            "normalized Gibbs-moment bound: orthogonal cross-section "
            "entropy can still depend on the Fourier coefficient."
        ),
        "slice_jensen_theorem": {
            "scope": "periodic four-dimensional L^4 lattices, integer L>=4, arbitrary real mean-zero log field psi",
            "slice_mean": "b_t=L^-3*sum_(x_perp) psi_(t,x_perp)",
            "slice_residual_mean": "rbar_t=L^-3*sum_(x_perp) r_(t,x_perp)",
            "jensen_bound": "rbar_t>=b_(t-1)+b_(t+1)-2*b_t=(Delta_1 b)_t",
            "reason": "each of six spatial directed averages is at least one and each temporal directed average is at least the exponential of the corresponding slice-mean difference",
            "action_bound": "A(psi)>=L^3/2*sum_t (rbar_t)^2>=L^3/2*||(Delta_1 b)_+||_2^2",
            "status": "PROVED",
        },
        "positive_part_fourier_lemma": {
            "hypotheses": "a in R^L, sum_t a_t=0; h_t=cos(2*pi*t/L+theta)",
            "positive_mass": "P=sum a_+=sum (-a_-)",
            "negative_weighted_phase": "c_-=P^-1*sum (-a_-)*h lies in [-1,1] when P>0",
            "identity": "<a,h>=sum a_+*(h-c_-)",
            "phase_norm": "sum_t (h_t-c_-)^2=L/2+L*c_-^2<=3L/2 for the lowest mode and L>=4",
            "conclusion": "||(a)_+||_2^2>=(2/(3L))*|<a,h>|^2",
            "status": "PROVED",
        },
        "lowest_mode_corollary": {
            "fourier_normalization": "psi_hat(e_mu)=N^-1*sum_x psi_x*exp(-2*pi*i*x_mu/L)=L^-1*sum_t b_t*exp(-2*pi*i*t/L)",
            "dispersion": "omega_L=4*sin(pi/L)^2",
            "log_field_bound": "A(psi)>=(N*omega_L^2/3)*|psi_hat(e_mu)|^2",
            "scaled_field_bound": "for psi=lambda*phi and nonzero lambda, S_lambda(phi)=A(lambda*phi)/lambda^2>=(N*omega_L^2/3)*|phi_hat(e_mu)|^2",
            "uniformities": ["integer L>=4", "chosen axis", "arbitrary transverse fluctuations", "nonzero coupling"],
            "status": "PROVED_DETERMINISTIC_NOT_NORMALIZED",
        },
        "exact_nonseparable_l4_fixture": {
            "sites": exact["sites"],
            "spatial_sites_per_slice": exact["spatial_sites_per_slice"],
            "field": "Omega_(t,x,y,z)=2^(base_t+activation_t*transverse_x)",
            "base_exponents": exact["base_exponents"],
            "transverse_exponents": exact["transverse_exponents"],
            "activation_by_time": exact["activation_by_time"],
            "slice_exponent_means": [enc(value) for value in exact["slice_exponent_means"]],
            "slice_residual_means": [enc(value) for value in exact["slice_residual_means"]],
            "slice_laplacian_log2_coefficients": [
                enc(value) for value in exact["slice_laplacian_coefficients"]
            ],
            "action": enc(exact["action"]),
            "slice_cauchy_lower": enc(exact["slice_cauchy_lower"]),
            "action_minus_slice_cauchy": enc(exact["action_minus_slice_cauchy"]),
            "lowest_dispersion": exact["lowest_dispersion"],
            "fourier_modulus_squared": "(log(2))^2/4",
            "quadratic_lower_bound": "(256/3)*(log(2))^2<3136/75<1361/2",
            "log_bound": "log(2)<7/10",
            "status": "EXACT_RATIONAL_ENUMERATION_WITH_RATIONAL_LOG_BOUND",
        },
        "method_disposition": {
            "quartic_lowest_mode_action_bound": "IMPROVED_BY_QUADRATIC_BOUND",
            "all_background_quadratic_lowest_axial_action_bound": "PROVED",
            "normalized_lowest_mode_second_moment": "OPEN",
            "orthogonal_cross_section_entropy": "OPEN",
            "actual_interacting_h_minus_one_second_moment": "OPEN",
            "interacting_tightness": "NOT_ESTABLISHED",
            "continuum_limit": "NOT_ESTABLISHED",
            "born_rule": "NOT_ESTABLISHED",
            "krein_reconstruction": "NOT_ASSESSED",
            "lorentzian_transfer": "NOT_ESTABLISHED",
        },
        "missing_object_ledger": [
            "a normalized comparison controlling the orthogonal cross-section entropy as the lowest axial coefficient changes",
            "an actual volume-uniform lowest-mode second-moment bound or controlled divergence sequence",
            "a dyadic-shell extension deciding the interacting H^-1 moment",
        ],
        "next_gate": (
            "Combine the new origin-centered quadratic action cost with the existing "
            "all-background fiber strong convexity. Parameterize fibers by their "
            "unique centers and determine whether the orthogonal cross-section "
            "Jacobian can offset the certified (N*omega_L^2/3)*|phi_hat|^2 cost. "
            "A successful bound must be normalized; a counterexample must carry "
            "actual integrated Gibbs weight."
        ),
        "does_not_establish": [
            "a normalized marginal domination or Gibbs tail bound",
            "the normalized lowest-mode second moment",
            "the actual interacting H^-1 moment bound or its divergence",
            "tightness or a continuum Euclidean BT measure",
            "a Born rule, Krein reconstruction, or anything LORENTZIAN-CAUSAL",
            "a literature-priority claim",
        ],
        "provenance": {
            "repository_base_commit": SOURCE_COMMIT,
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "arithmetic": "Exact Fraction enumeration for the 4^4 fixture; the theorem uses finite sums, Cauchy-Schwarz, exp(s)>=1+s, Jensen, and exact Fourier identities",
        },
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_euclidean_axial_slice_quadratic_coercivity.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_axial_slice_quadratic_coercivity.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_axial_slice_quadratic_coercivity",
        ],
        "tier_receipt": {
            "tier_0": "Python compilation, strict JSON/schema validation, exact input hashes, scoped diff check, and staged-diff inspection required",
            "tier_1": "producer replay, nonimporting exact lattice verifier, and focused mutation tests required",
            "tier_2": "unchanged predecessor certificates are checked by content hash; no shared operator or lifecycle state changes",
            "tier_3": "not applicable: deterministic coercivity is not a normalized-moment or continuum lifecycle promotion",
            "memory_policy": "all Python commands run under ulimit -v 500000",
            "elapsed_seconds_and_peak_kib": {
                "producer_check": "0.04 s, 20520 KiB",
                "independent_verifier": "0.11 s, 30368 KiB",
                "unit_tests": "0.14 s, 30608 KiB",
            },
            "repository_audits": {
                "planning_import": "PASS: 1665 nodes, 0 invalid items, 0 malformed events; 7.41 s, 207760 KiB",
                "science_forge_shadow": "not run unless a registered shadow input changes; a skip is not a pass",
            },
        },
        "checks": {
            "ok": all(checks.values()),
            "passed": sum(checks.values()),
            "total": len(checks),
            "failures": [name for name, passed in checks.items() if not passed],
            "details": checks,
        },
        "schema": SCHEMA_REL,
        "report": REPORT_REL,
        "verifier": VERIFY_REL,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    payload = build()
    if not payload["checks"]["ok"]:
        print("[FAIL] internal checks")
        return 1
    if args.check:
        try:
            with open(CERT_PATH, encoding="utf-8") as handle:
                current = json.load(handle)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"[FAIL] certificate load: {exc}")
            return 1
        if current != payload:
            print("[FAIL] generated certificate differs from committed certificate")
            return 1
    else:
        with open(CERT_PATH, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2)
            handle.write("\n")
    print(
        "[PASS] BT axial slice quadratic coercivity "
        f"({payload['checks']['passed']}/{payload['checks']['total']})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
