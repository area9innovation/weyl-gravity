#!/usr/bin/env python3
"""Independent verifier for finite-time BT active-loop affiliation."""
from __future__ import annotations

import hashlib
import json
import os
import sys

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_FINITE_TIME_ACTIVE_LOOP_AFFILIATION_V1.json",
)
SCHEMA = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-finite-time-active-loop-affiliation-v1.schema.json",
)


def load(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def file_hash(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def square(row):
    return sp.factor(row[0] ** 2 - sum(value**2 for value in row[1:]))


def verify(certificate):
    inputs = certificate["provenance"]["inputs"]
    imported = {
        os.path.basename(row["path"]): load(os.path.join(ROOT, row["path"]))
        for row in inputs
    }
    tagged = imported["REVERSE_PHYSICS_BT_TAGGED_SPECTATOR_PHYSICAL_PACKET_PROBABILITY_V1.json"]
    covariant = imported["REVERSE_PHYSICS_BT_AUXILIARY_ACTIVE_ONE_LOOP_MSBAR_V1.json"]
    spectator = imported["REVERSE_PHYSICS_BT_TAGGED_PACKET_NORMAL_ORDERED_SPECTATOR_REDUCTION_V1.json"]

    # Rebuild the ordered two-time integral without using the producer's
    # already reduced one-dimensional expression.
    T, d, t1, t2 = sp.symbols("T d t1 t2", positive=True, real=True)
    ordered = sp.integrate(
        sp.integrate(sp.sin(d * (t1 - t2)), (t2, 0, t1)), (t1, 0, T)
    ) / T
    target = 1 / d - sp.sin(d * T) / (T * d**2)

    # Method-distinct convolution check.  The derivative of log(x)+C(T*x)
    # is the dispersive kernel, and C vanishes at infinity.  This fixes the
    # convolution including its additive constant.
    x = sp.symbols("x", positive=True)
    Cx = sp.sin(T * x) / (T * x) - sp.Ci(T * x)
    convolution_derivative = sp.diff(sp.log(x) + Cx, x)

    # Reconstruct the three physical channel momenta directly from the exact
    # tagged witness, rather than trusting the recorded gap strings.
    witness = tagged["exact_tagged_spectator_witness"]
    incoming = [sp.Matrix([sp.Rational(value) for value in row]) for row in witness["incoming_momenta"]]
    outgoing = [sp.Matrix([sp.Rational(value) for value in row]) for row in witness["outgoing_momenta"]]
    momenta = {
        "s": incoming[1] + incoming[2],
        "t": incoming[1] - outgoing[1],
        "u": incoming[1] - outgoing[2],
    }
    invariants = {name: square(row) for name, row in momenta.items()}
    gaps = {}
    for name, row in momenta.items():
        radius = sp.sqrt(sum(value**2 for value in row[1:]))
        gaps[name] = tuple(sorted((sp.Abs(row[0] - radius), sp.Abs(row[0] + radius)), key=sp.default_sort_key))

    z = sp.symbols("z", positive=True)
    C = sp.sin(z) / z - sp.Ci(z)
    A = z * sp.sin(z) - sp.cos(z) - z**2 * sp.Ci(z)
    a, b = sp.symbols("a b", positive=True)
    J = (A.subs(z, b * sp.sqrt(1 - a)) - A.subs(z, b * sp.sqrt(a))) / b**2

    ordered_row = certificate["ordered_dyson_kernel"]
    fejer = certificate["fejer_affiliation"]
    bubble = certificate["finite_time_bubble"]
    fixture = certificate["tagged_fixture"]
    window = certificate["hard_window"]
    packet = certificate["compact_packet"]
    interpretation = certificate["interpretation"]
    limits = certificate["does_not_establish"]
    predecessor_values = [value for name, value in imported.items() if name.startswith("REVERSE_PHYSICS_")]
    checks = {
        "schema_validation": not list(Draft202012Validator(load(SCHEMA)).iter_errors(certificate)),
        "all_input_hashes_match": all(row["sha256"] == file_hash(row["path"]) for row in inputs),
        "six_predecessors_pass": len(predecessor_values) == 6 and all(row["checks"]["ok"] for row in predecessor_values),
        "dependency_tags_are_exact": certificate["dependency_tags"] == ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL", "REDUCED-MODE"],
        "lifecycle_is_coefficient_computed": certificate["lifecycle_state"] == "COEFFICIENT_COMPUTED",
        "ordered_double_integral_is_rebuilt": sp.simplify(ordered - target) == 0,
        "ordered_kernel_record_is_exact": ordered_row["dispersive_interference"] == "Im(D_T)/T=1/delta-sin(delta*T)/(T*delta^2)",
        "resonant_dispersive_value_is_zero": sp.limit(target, d, 0) == 0 and ordered_row["resonant_value"].startswith("Kdisp_T(0)=0"),
        "convolution_derivative_matches_dispersive_kernel": sp.simplify(convolution_derivative - target.subs(d, x)) == 0,
        "transient_derivative_is_rebuilt": sp.simplify(sp.diff(C, z) + sp.sin(z) / z**2) == 0,
        "fejer_unit_mass_is_recorded": fejer["normalization"] == "int_R K_T(nu)dnu=1",
        "fejer_hilbert_transform_is_recorded": fejer["hilbert_transform"].endswith("=1/delta-sin(delta*T)/(T*delta^2)"),
        "renormalization_order_is_explicit": "MSbar first" in fejer["renormalization_order"],
        "finite_time_bubble_formula_is_exact": bubble["general_formula"] == "B_T,MSbar(P0,p)=log(mu^2/abs(P0^2-p^2))+2-C(T*abs(P0-p))-C(T*abs(P0+p))",
        "finite_scheme_boundary_is_retained": "finite local scheme shift" in bubble["finite_counterterm"],
        "covariant_boundary_is_retained": "B_MSbar" in bubble["large_time_boundary"] and covariant["interpretation"]["hard_log_match"] == "EXACT",
        "tagged_invariants_are_rebuilt": invariants == {"s": sp.Rational(64, 25), "t": sp.Rational(-32, 25), "u": sp.Rational(-32, 25)},
        "tagged_light_cone_gaps_are_rebuilt": gaps == {"s": (sp.Rational(4, 5), sp.Rational(16, 5)), "t": (4 * sp.sqrt(2) / 5, 4 * sp.sqrt(2) / 5), "u": (4 * sp.sqrt(2) / 5, 4 * sp.sqrt(2) / 5)},
        "tagged_frame_dependence_is_explicit": "frame dependent" in fixture["frame"],
        "tagged_bubble_sum_is_exact": fixture["bubble_sum"] == "B_s,T+B_t,T+B_u,T=L_*+6-C(4*kappa*T/5)-C(16*kappa*T/5)-4*C(4*sqrt(2)*kappa*T/5)",
        "tagged_loop_normalization_is_exact": fixture["local_loop_click"].startswith("q_loop,T^(6)=125*lambda^6*DeltaOmega/[16384*pi^4*kappa^2*Area]"),
        "tagged_covariant_limit_is_exact": fixture["large_time_boundary"].endswith("(L_*+6)/(16384*pi^4*kappa^2*Area)"),
        "window_antiderivative_is_rebuilt": sp.simplify(sp.diff(A, z) - 2 * z * C) == 0,
        "window_integral_derivative_is_rebuilt": sp.simplify(sp.diff(J, a) + C.subs(z, b * sp.sqrt(a)) + C.subs(z, b * sp.sqrt(1-a))) == 0,
        "window_is_explicitly_active_COM": window["definition"].startswith("active two-body center frame"),
        "compact_packet_bound_is_recorded": packet["bound"] == "abs(B_T)<=2+max_abs_log+2/(T*d_gap) for every T>0",
        "spectator_zero_is_imported": spectator["interpretation"]["spectator_order_lambda2_packet_kernel"] == "ZERO_IN_DECLARED_SCHEME" and interpretation["normal_ordered_spectator_loop"] == "ZERO_IN_DECLARED_SCHEME",
        "finite_duration_affiliation_is_promoted_only_scoped": interpretation["finite_duration_BT_Dyson_affiliation"] == "PROVED_ON_SELECTED_ENERGY_DIAGONAL_HARD_CARRIER",
        "q6_is_only_ready_for_assembly": interpretation["complete_tagged_q6_probability"] == "READY_FOR_SEPARATE_ASSEMBLY",
        "Eq19_gravity_Lorentzian_boundaries_are_exact": interpretation["general_Eq19"] == "NOT_PROVED" and interpretation["gravity_or_BV_BRST_transfer"] == "NOT_CONSTRUCTED" and interpretation["Lorentzian_causal_claim"] == "NOT_ESTABLISHED",
        "all_time_and_switching_boundaries_are_explicit": any("arbitrary temporal switching" in row for row in limits) and any("all-time" in row for row in limits),
        "next_gate_is_q6_assembly": certificate["next_gate"].startswith("Assemble q_tag^(6)") and "only then promote" in certificate["next_gate"],
    }
    return {name: bool(value) for name, value in checks.items()}


def main():
    checks = verify(load(CERT))
    failures = [name for name, ok in checks.items() if not ok]
    print("checks %d/%d" % (sum(checks.values()), len(checks)))
    print("RESULT:", "PASS" if not failures else "FAIL")
    if failures:
        print("failures:", ", ".join(failures))
    return int(bool(failures))


if __name__ == "__main__":
    sys.exit(main())
