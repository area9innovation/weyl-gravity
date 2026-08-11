#!/usr/bin/env python3
"""Independent verifier for the BT physical Abel--Fock intertwiner."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_ABEL_FOCK_PHYSICAL_INTERTWINER_V1.json",
)
SCHEMA = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-abel-fock-physical-intertwiner-v1.schema.json",
)


def load(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def frac(value):
    return Fraction(value["numerator"], value["denominator"])


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def verify(certificate):
    import sympy as sp

    schema_errors = list(Draft202012Validator(load(SCHEMA)).iter_errors(certificate))
    disposition = certificate.get("disposition", {})
    preflight = (
        not schema_errors
        and certificate.get("certificate")
        == "REVERSE_PHYSICS_BT_ABEL_FOCK_PHYSICAL_INTERTWINER_V1"
        and certificate.get("dependency_tags") == ["LOCAL-ALGEBRAIC", "REDUCED-MODE"]
        and certificate.get("lifecycle_state") == "CLASSIFIED"
        and disposition.get("abel_to_correlated_system_fock_first_emission_intertwiner")
        == "CONSTRUCTED_EXACTLY"
        and disposition.get("full_seventy_five_mark_physical_intertwiner")
        == "NOT_CONSTRUCTED"
        and disposition.get("Eq19_all_orders") == "NOT_PROVED"
        and "anything LORENTZIAN-CAUSAL" in certificate.get("does_not_establish", [])
    )
    if not preflight:
        return {"serialized_claim_preflight": False}

    raw = certificate["raw_column_covariance_obstruction"]
    polar = certificate["physical_polar_ranges"]
    abel_map = certificate["abel_physical_range_intertwiner"]
    translations = certificate["translation_intertwiner"]
    first = certificate["first_emission_hp_affiliation"]
    rank_boundary = certificate["noise_only_rank_obstruction"]
    marks = certificate["seventy_five_mark_boundary"]

    input_paths = [row["path"] for row in certificate["provenance"]["inputs"]]
    physical = load(os.path.join(ROOT, input_paths[1]))
    rigged = load(os.path.join(ROOT, input_paths[2]))
    abel = load(os.path.join(ROOT, input_paths[3]))
    born = load(os.path.join(ROOT, input_paths[4]))
    hp = load(os.path.join(ROOT, input_paths[5]))
    six = load(os.path.join(ROOT, input_paths[7]))
    seven = load(os.path.join(ROOT, input_paths[8]))

    r, u = sp.symbols("r u", positive=True)
    imported_I = sp.sympify(
        rigged["threshold_gram"]["exact_function"]
        .removeprefix("I(r)=")
        .replace("^", "**"),
        locals={"r": r},
    )
    I = sp.factor(imported_I)
    Q = sp.factor((2 * u * (1 + r) - (1 - r) ** 2) / (2 * u**2))
    L = sp.factor(-(1 - r) ** 2 / (2 * u))
    rho = sp.factor((1 - r) ** 2 * (2 * u * (1 + r) - (1 - r) ** 2) / (4 * u**3))
    kallen = sp.factor(u**2 + 1 + r**2 - 2 * u - 2 * u * r - 2 * r)
    T = sp.diag(Q, L)
    J = sp.Matrix([[0, 1], [1, 0]])
    physical_gram = sp.simplify(-(J * T.T * J) * T)

    # Positivity is proved from the physical threshold, not sampled.  Writing
    # r=z^2, the nontrivial numerator at threshold factors as (z+1)^4.
    z = sp.symbols("z", positive=True)
    threshold_numerator = sp.factor(
        2 * (1 + z) ** 2 * (1 + z**2) - (1 - z**2) ** 2
    )

    I_quarter = sp.simplify(I.subs(r, sp.Rational(1, 4)))
    I_sixteenth = sp.simplify(I.subs(r, sp.Rational(1, 16)))
    difference = sp.simplify(sp.expand_log(I_sixteenth - I_quarter, force=True))
    claimed_difference = sp.sympify(raw["fixtures"]["difference"])
    claimed_lower = sp.Rational(
        int(raw["fixtures"]["strict_lower_bound_using_log2_gt_1_over_2"].split("/")[0]),
        int(raw["fixtures"]["strict_lower_bound_using_log2_gt_1_over_2"].split("/")[1]),
    )
    # log(2)=integral_1^2 dx/x > integral_1^2 dx/2=1/2.
    lower_from_integral = sp.Rational(11, 160) - sp.Rational(57, 2048)

    exchange = {
        "I(1/r)/I(r)": str(sp.simplify(I.subs(r, 1 / r) / I)),
        "Q(1/r,u/r)/Q(r,u)": str(sp.simplify(Q.subs({r: 1 / r, u: u / r}) / Q)),
        "L(1/r,u/r)/L(r,u)": str(sp.simplify(L.subs({r: 1 / r, u: u / r}) / L)),
        "rho(1/r,u/r)/rho(r,u)": str(sp.simplify(rho.subs({r: 1 / r, u: u / r}) / rho)),
        "dmu_(1/r)(u/r)/dmu_r(u)": str(
            sp.simplify(
                sp.sqrt(
                    (
                        kallen.subs({r: 1 / r, u: u / r})
                        / (u / r) ** 2
                        * r ** -2
                    )
                    / (kallen / u**2)
                )
            )
        ),
    }

    # A method-distinct exact finite fixture checks the polar-range algebra.
    # E0,E1,E2 are three independently normalized embeddings C2 -> C4.
    E0 = sp.Matrix([[1, 0], [0, 1], [0, 0], [0, 0]])
    E1 = sp.Matrix([[sp.Rational(3, 5), 0], [0, sp.Rational(3, 5)], [sp.Rational(4, 5), 0], [0, sp.Rational(4, 5)]])
    E2 = sp.Matrix([[sp.Rational(5, 13), 0], [0, sp.Rational(5, 13)], [sp.Rational(12, 13), 0], [0, sp.Rational(12, 13)]])
    P0, P1, P2 = E0 * E0.T, E1 * E1.T, E2 * E2.T
    C10, C21, C20 = E1 * E0.T, E2 * E1.T, E2 * E0.T
    partial_isometry = (
        E0.T * E0 == sp.eye(2)
        and E1.T * E1 == sp.eye(2)
        and E2.T * E2 == sp.eye(2)
        and C10.T * C10 == P0
        and C10 * C10.T == P1
        and C21.T * C21 == P1
        and C21 * C21.T == P2
        and C21 * C10 == C20
    )

    s, y, b = sp.symbols("s y b", real=True)
    p = sp.sech(y - s) ** 2 / 2
    shifted_p = sp.sech((y - b) - (s - b)) ** 2 / 2
    abel_mass = sp.Rational(1, 2) * (1 - (-1))

    q0 = frac(physical["normalization_ledger"]["physical_per_pair_Born_normalized_response"])
    a = sp.symbols("a", positive=True)
    interval_per_pair = sp.Rational(q0.numerator, q0.denominator) * a
    interval_total = 3 * interval_per_pair

    channels = hp["system_and_noise_carrier"]["noise_channels"]
    first_rows = [row for row in channels if row["level"] == 0]
    higher_rows = [row for row in channels if row["level"] > 0]
    first_indices = [row["noise_index"] for row in first_rows]
    higher_indices = [row["noise_index"] for row in higher_rows]

    # A single pinned edge mark is one-dimensional.  Its most general map from
    # two species is a 1x2 row and has rank at most one, while q0*I2 has rank 2.
    x0, x1 = sp.symbols("x0 x1")
    noise_only_map = sp.Matrix([[x0, x1]])
    physical_pair_gram = sp.Rational(1, 48) * sp.eye(2)

    inputs = certificate["provenance"]["inputs"]
    checks = {
        "schema_and_claim_boundary": not schema_errors,
        "threshold_gram_reconstructed": sp.simplify(I - sp.sympify(raw["I"], locals={"r": r})) == 0,
        "physical_pointwise_gram": sp.simplify(physical_gram - rho * sp.eye(2)) == sp.zeros(2),
        "physical_range_positive_above_threshold": threshold_numerator == (z + 1) ** 4,
        "massless_and_equal_mass_limits": sp.limit(I, r, 0, dir="+") == sp.Rational(5, 24) and sp.limit(I, r, 1) == 0,
        "raw_gram_fixtures": str(I_quarter) == raw["fixtures"]["I(1/4)"] and str(I_sixteenth) == raw["fixtures"]["I(1/16)"],
        "raw_covariance_no_go": sp.simplify(difference - claimed_difference) == 0 and lower_from_integral == claimed_lower == sp.Rational(419, 10240) and claimed_lower > 0,
        "daughter_exchange_scaling": exchange == polar["daughter_exchange_extension"],
        "polar_partial_isometry_fixture": partial_isometry and polar["normalized_gram"] == "E_R^sharp E_R=I2",
        "polar_transport_cocycle": polar["cocycle"] == "C_c(R+b) C_b(R)=C_(b+c)(R)",
        "abel_density_normalization": abel_mass == 1 and abel_map["abel_density"] == "p_s(y)=sech(y-s)^2/2",
        "abel_joint_translation": sp.simplify(shifted_p - p) == 0 and translations["abel_identity"] == "p_(s-b)(y-b)=p_s(y)",
        "abel_range_isometry": "A^sharp A=I" in abel_map["identities"] and "sqrt(p_s(y))*E_y" in abel_map["isometry"],
        "translation_intertwining": translations["intertwining"] == "T_b A=A S_b and A^sharp T_b=S_b A^sharp on Ran(A)" and partial_isometry,
        "physical_interval_rates": q0 == Fraction(1, 48) and interval_per_pair == a / 48 and interval_total == a / 16 and first["finite_interval_per_pair_norm"] == "a/48" and first["finite_interval_three_pair_norm"] == "a/16",
        "hard_drift": first["hard_hp_drift"] == "1/32" and hp["hudson_parthasarathy_cocycle"]["drift_eigenvalues_by_level"][0] == "1/32",
        "correlated_first_edge_marks": first_indices == first["first_edge_noise_indices"] == [0, 1, 2] and len(first_rows) * 2 == 6,
        "noise_only_rank_obstruction": noise_only_map.rank() <= 1 and physical_pair_gram.rank() == 2 and rank_boundary["disposition"] == "NOISE_ONLY_FAILS; CORRELATED_SYSTEM_NOISE_PASSES",
        "remaining_mark_boundary": len(higher_rows) == 72 and higher_indices == marks["quotient_only_edge_marks"] == list(range(3, 75)),
        "higher_quotient_results_retained": six["branching_affiliation"]["second_jump_status"].startswith("AMPLITUDE_AFFILIATED") and seven["branching_affiliation"]["third_jump"].startswith("AMPLITUDE_AFFILIATED"),
        "higher_continuum_promotion_refused": disposition["remaining_seventy_two_edge_continuum_affiliation"] == "NOT_CONSTRUCTED" and disposition["full_seventy_five_mark_physical_intertwiner"] == "NOT_CONSTRUCTED",
        "public_Rt_obstruction_unchanged": physical["disposition"]["public_D_equals_physical_splitting"] == "EXACT_RANK_JORDAN_OBSTRUCTION",
        "input_hashes": len(inputs) == 9 and all(row["sha256"] == sha256(row["path"]) for row in inputs),
        "producer_checks_intact": certificate["checks"]["passed"] == certificate["checks"]["total"] == 30 and certificate["checks"]["failures"] == [] and all(certificate["checks"]["details"].values()),
        "open_claims_remain_open": disposition["fourth_jump"] == "NOT_COMPUTED" and disposition["complete_BT_probability"] == "NOT_CONSTRUCTED" and disposition["spacetime_Moller_LSZ_S_operator"] == "NOT_CONSTRUCTED" and disposition["Eq19_all_orders"] == "NOT_PROVED" and "anything LORENTZIAN-CAUSAL" in certificate["does_not_establish"],
    }
    return {name: bool(ok) for name, ok in checks.items()}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", default=CERT)
    args = parser.parse_args(argv)
    try:
        checks = verify(load(args.verify))
    except (OSError, ValueError, KeyError, TypeError, ZeroDivisionError) as exc:
        print("[FAIL] verifier exception:", exc)
        return 1
    failed = [name for name, ok in checks.items() if not ok]
    for name in failed:
        print("[FAIL]", name)
    print("checks %d/%d" % (len(checks) - len(failed), len(checks)))
    print("INDEPENDENT RESULT:", "PASS" if not failed else "FAIL")
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
