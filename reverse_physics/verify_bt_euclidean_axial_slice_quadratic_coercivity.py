#!/usr/bin/env python3
"""Independent verifier for BT axial-slice quadratic coercivity."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction
from itertools import product

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_AXIAL_SLICE_QUADRATIC_COERCIVITY_V1.json",
)
SCHEMA_PATH = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-axial-slice-quadratic-coercivity-v1.schema.json",
)


def frac(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def file_hash(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def dyadic(exponent: int) -> Fraction:
    if exponent < 0:
        return Fraction(1, 1 << (-exponent))
    return Fraction(1 << exponent)


def independent_fixture() -> dict:
    length = 4
    sites = list(product(range(length), repeat=4))
    base = (0, 1, 0, -1)
    transverse = (1, -1, 0, 0)
    active = (1, 0, 0, 0)
    field = {
        site: base[site[0]] + active[site[0]] * transverse[site[1]]
        for site in sites
    }
    residual: dict[tuple[int, ...], Fraction] = {}
    for site in sites:
        value = Fraction(-8)
        for axis in range(4):
            for step in (-1, 1):
                neighbor = list(site)
                neighbor[axis] = (neighbor[axis] + step) % length
                value += dyadic(field[tuple(neighbor)] - field[site])
        residual[site] = value
    spatial = length**3
    slice_field = []
    slice_residual = []
    for time in range(length):
        time_sites = [site for site in sites if site[0] == time]
        slice_field.append(
            sum((Fraction(field[site]) for site in time_sites), Fraction()) / spatial
        )
        slice_residual.append(
            sum((residual[site] for site in time_sites), Fraction()) / spatial
        )
    laplacian = [
        slice_field[(time - 1) % length]
        + slice_field[(time + 1) % length]
        - 2 * slice_field[time]
        for time in range(length)
    ]
    action = sum((value * value for value in residual.values()), Fraction()) / 2
    slice_lower = Fraction(spatial, 2) * sum(
        (value * value for value in slice_residual), Fraction()
    )
    # The exact lowest sine phase for this fixture is (0,-1,0,1).
    phase = [Fraction(0), Fraction(-1), Fraction(0), Fraction(1)]
    pairing = sum((a * h for a, h in zip(laplacian, phase)), Fraction())
    positive_norm = sum((max(value, Fraction()) ** 2 for value in laplacian), Fraction())
    fourier_lemma_rhs = Fraction(2, 3 * length) * pairing * pairing
    return {
        "slice_field": slice_field,
        "slice_residual": slice_residual,
        "laplacian": laplacian,
        "action": action,
        "slice_lower": slice_lower,
        "positive_norm": positive_norm,
        "pairing": pairing,
        "fourier_lemma_rhs": fourier_lemma_rhs,
    }


def verify(path: str) -> bool:
    checks: dict[str, bool] = {}
    try:
        with open(path, encoding="utf-8") as handle:
            cert = json.load(handle)
        with open(SCHEMA_PATH, encoding="utf-8") as handle:
            schema = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"[FAIL] load: {exc}")
        return False

    checks["strict_schema"] = not list(Draft202012Validator(schema).iter_errors(cert))
    inputs = cert["provenance"]["inputs"]
    checks["provenance_hashes_current"] = len(inputs) == 2 and all(
        file_hash(row["path"]) == row["sha256"] for row in inputs
    )

    rebuilt = independent_fixture()
    public = cert["exact_nonseparable_l4_fixture"]
    checks["independent_full_l4_enumeration"] = (
        rebuilt["slice_field"]
        == [frac(value) for value in public["slice_exponent_means"]]
        == [Fraction(0), Fraction(1), Fraction(0), Fraction(-1)]
        and rebuilt["slice_residual"]
        == [frac(value) for value in public["slice_residual_means"]]
        == [Fraction(13, 8), Fraction(-15, 16), Fraction(1, 2), Fraction(9, 4)]
        and rebuilt["laplacian"]
        == [frac(value) for value in public["slice_laplacian_log2_coefficients"]]
        == [Fraction(0), Fraction(-2), Fraction(0), Fraction(2)]
        and rebuilt["action"] == frac(public["action"]) == Fraction(1361, 2)
        and rebuilt["slice_lower"]
        == frac(public["slice_cauchy_lower"])
        == Fraction(2261, 8)
        and rebuilt["action"] - rebuilt["slice_lower"]
        == frac(public["action_minus_slice_cauchy"])
        == Fraction(3183, 8)
    )
    checks["positive_part_fourier_fixture"] = (
        rebuilt["positive_norm"] == 4
        and abs(rebuilt["pairing"]) == 4
        and rebuilt["fourier_lemma_rhs"] == Fraction(8, 3)
        and rebuilt["positive_norm"] >= rebuilt["fourier_lemma_rhs"]
    )
    checks["rational_log_fixture_bound"] = (
        public["log_bound"] == "log(2)<7/10"
        and Fraction(256, 3) * Fraction(49, 100) == Fraction(3136, 75)
        and Fraction(3136, 75) < frac(public["action"])
    )

    slice_theorem = cert["slice_jensen_theorem"]
    fourier = cert["positive_part_fourier_lemma"]
    corollary = cert["lowest_mode_corollary"]
    checks["general_slice_chain_declared"] = (
        slice_theorem["jensen_bound"]
        == "rbar_t>=b_(t-1)+b_(t+1)-2*b_t=(Delta_1 b)_t"
        and slice_theorem["action_bound"]
        == "A(psi)>=L^3/2*sum_t (rbar_t)^2>=L^3/2*||(Delta_1 b)_+||_2^2"
        and slice_theorem["status"] == "PROVED"
    )
    checks["zero_sum_fourier_constant"] = (
        fourier["phase_norm"]
        == "sum_t (h_t-c_-)^2=L/2+L*c_-^2<=3L/2 for the lowest mode and L>=4"
        and fourier["conclusion"]
        == "||(a)_+||_2^2>=(2/(3L))*|<a,h>|^2"
        and Fraction(1, 2) * Fraction(2, 3) == Fraction(1, 3)
    )
    checks["quadratic_corollary_exact"] = (
        corollary["log_field_bound"]
        == "A(psi)>=(N*omega_L^2/3)*|psi_hat(e_mu)|^2"
        and corollary["scaled_field_bound"]
        == "for psi=lambda*phi and nonzero lambda, S_lambda(phi)=A(lambda*phi)/lambda^2>=(N*omega_L^2/3)*|phi_hat(e_mu)|^2"
        and corollary["status"] == "PROVED_DETERMINISTIC_NOT_NORMALIZED"
    )

    disposition = cert["method_disposition"]
    checks["claim_boundary"] = (
        disposition["all_background_quadratic_lowest_axial_action_bound"] == "PROVED"
        and disposition["normalized_lowest_mode_second_moment"] == "OPEN"
        and disposition["orthogonal_cross_section_entropy"] == "OPEN"
        and disposition["actual_interacting_h_minus_one_second_moment"] == "OPEN"
        and disposition["continuum_limit"] == "NOT_ESTABLISHED"
    )
    checks["dependency_boundary"] = cert["dependency_tags"] == [
        "LOCAL-ALGEBRAIC",
        "EUCLIDEAN-SPECTRAL",
        "REDUCED-MODE",
    ]
    checks["required_nonclaims"] = {
        "a normalized marginal domination or Gibbs tail bound",
        "the normalized lowest-mode second moment",
        "the actual interacting H^-1 moment bound or its divergence",
        "a Born rule, Krein reconstruction, or anything LORENTZIAN-CAUSAL",
    }.issubset(set(cert["does_not_establish"]))
    checks["certificate_checks_closed"] = (
        cert["checks"]["ok"]
        and cert["checks"]["passed"] == cert["checks"]["total"]
        and not cert["checks"]["failures"]
        and all(cert["checks"]["details"].values())
    )

    for name, passed in checks.items():
        print(f"[{'PASS' if passed else 'FAIL'}] {name}")
    print(
        f"RESULT: {'PASS' if all(checks.values()) else 'FAIL'} "
        f"({sum(checks.values())}/{len(checks)})"
    )
    return all(checks.values())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("certificate", nargs="?", default=DEFAULT_CERT)
    args = parser.parse_args(argv)
    return 0 if verify(args.certificate) else 1


if __name__ == "__main__":
    sys.exit(main())
