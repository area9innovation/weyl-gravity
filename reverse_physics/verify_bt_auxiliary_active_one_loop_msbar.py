#!/usr/bin/env python3
"""Independent verifier for the auxiliary active MSbar one-loop result."""
from __future__ import annotations

import hashlib
import itertools
import json
import os
import sys

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(ROOT, "reverse_physics/certificates/REVERSE_PHYSICS_BT_AUXILIARY_ACTIVE_ONE_LOOP_MSBAR_V1.json")
SCHEMA = os.path.join(ROOT, "reverse_physics/schema/reverse-physics-bt-auxiliary-active-one-loop-msbar-v1.schema.json")


def load(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def file_hash(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def verify(certificate):
    inputs = certificate["provenance"]["inputs"]
    imported = {os.path.basename(row["path"]): load(os.path.join(ROOT, row["path"])) for row in inputs}
    hard = imported["REVERSE_PHYSICS_BT_UV_HARD_SCATTERING_LAW_V1.json"]
    source = imported["bateman_turok_hamiltonian_source_v1.json"]
    charge = imported["REVERSE_PHYSICS_CHARGE_GRADING_LOOP_STABILITY_V1.json"]

    # Rebuild the one-loop channel tensor by choosing the two external fields
    # at the left vertex.  A like pair leaves a like internal pair and has one
    # cross matching after the symmetry factor; an unlike pair has two.
    assignments = list(itertools.combinations(range(4), 2))
    channel_pairs = [((0, 1), (2, 3)), ((0, 2), (1, 3)), ((0, 3), (1, 2))]
    rows = []
    expected_recorded_rows = []
    for omega_labels in assignments:
        species = ["O" if i in omega_labels else "U" for i in range(4)]
        weights = []
        for left, _right in channel_pairs:
            like = species[left[0]] == species[left[1]]
            weights.append(2 if like else 4)
        rows.append(tuple(weights))
        expected_recorded_rows.append({"Omega_labels": list(omega_labels), "s": weights[0], "t": weights[1], "u": weights[2]})

    column_sums = tuple(sum(row[j] for row in rows) for j in range(3))
    tree_norm = 6 * 2 * 2
    Bs, Bt, Bu = sp.symbols("Bs Bt Bu", real=True)
    tree_loop = 2 * sum(row[0]*Bs + row[1]*Bt + row[2]*Bu for row in rows)
    relative = sp.simplify(2*tree_loop/(16*sp.pi**2*tree_norm))

    # Method-distinct endpoint evaluation using the beta-function derivative.
    alpha = sp.symbols("alpha", positive=True)
    beta_integral = sp.gamma(alpha)**2 / sp.gamma(2*alpha)
    endpoint_sum = sp.limit(sp.diff(beta_integral, alpha), alpha, 1)
    bubble_constant = -endpoint_sum

    lam, s, Ls, Lt, Lu = sp.symbols("lambda s Ls Lt Lu", positive=True)
    born = 3*lam**4/(32*sp.pi**2*s)
    full = sp.factor(born * 5*lam**2*(Ls+Lt+Lu+3*bubble_constant)/(24*sp.pi**2))
    expected = 5*lam**6*(Ls+Lt+Lu+6)/(256*sp.pi**4*s)

    a = sp.symbols("a", positive=True)
    c = 1-2*a
    recorded_window = 2*c - 2*(1-a)*sp.log(1-a) + 2*a*sp.log(a)

    species = certificate["species_enumeration"]
    bubble = certificate["msbar_bubble"]
    active = certificate["active_virtual_probability"]
    fixture = certificate["tagged_fixture"]
    kernel = certificate["compact_kernel"]
    interpretation = certificate["interpretation"]
    limits = certificate["does_not_establish"]
    checks = {
        "schema_validation": not list(Draft202012Validator(load(SCHEMA)).iter_errors(certificate)),
        "all_input_hashes_match": all(row["sha256"] == file_hash(row["path"]) for row in inputs),
        "imported_certificates_pass": all(value["checks"]["ok"] for name, value in imported.items() if name.startswith("REVERSE_PHYSICS_")),
        "dependency_tags_are_exact": certificate["dependency_tags"] == ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL", "REDUCED-MODE"],
        "lifecycle_is_coefficient_computed": certificate["lifecycle_state"] == "COEFFICIENT_COMPUTED",
        "auxiliary_action_is_imported": "Omega^2 Upsilon^2" in source["public_inputs"]["auxiliary_action"],
        "cross_metric_is_imported": "W^{OmegaOmega} = W^{UpsilonUpsilon} = 0" in charge["structural_inputs"]["their_wightman"],
        "six_assignments_are_independently_enumerated": len(rows) == 6,
        "every_row_has_244_pattern": all(sorted(row) == [2, 4, 4] for row in rows),
        "recorded_rows_match_independent_enumeration": species["bubble_weights"] == expected_recorded_rows,
        "channel_sums_are_twenty": column_sums == (20, 20, 20) and species["channel_column_sums"] == {"s": 20, "t": 20, "u": 20},
        "tree_norm_is_twenty_four": tree_norm == 24 and species["tree_norm"] == 24,
        "tree_loop_pairing_is_forty_sum": sp.expand(tree_loop - 40*(Bs+Bt+Bu)) == 0,
        "relative_factor_is_five_over_twenty_four": sp.simplify(relative/((Bs+Bt+Bu)/sp.pi**2)) == sp.Rational(5, 24),
        "beta_derivative_gives_endpoint_sum_minus_two": bubble_constant == 2,
        "recorded_bubble_constant_is_plus_two": bubble["real_bubble"] == "B_X=L_X+2, L_X=log(mu^2/abs(X))",
        "three_channel_constant_is_plus_six": bubble["three_channel_sum"].endswith("+6"),
        "complete_density_is_rebuilt": sp.simplify(full-expected) == 0,
        "recorded_complete_density_is_exact": active["complete_msbar_density"] == "d_sigma_active,MSbar^(6)/dOmega=5*lambda^6*(L_s+L_t+L_u+6)/(256*pi^4*s)",
        "hard_log_is_independently_matched": active["logarithmic_part"].replace("L_s", "Ls").replace("L_t", "Lt").replace("L_u", "Lu") == hard["certified_inputs"]["projected_hard_log"],
        "callan_symanzik_residual_is_zero": hard["callan_symanzik_certificate"]["residual"]["numerator"] == 0,
        "window_integral_is_independently_rebuilt": sp.simplify(sp.diff(recorded_window, a)-2*sp.log(a)-2*sp.log(1-a)) == 0 and sp.simplify(recorded_window.subs(a, sp.Rational(1, 2))) == 0,
        "central_fixture_contains_finite_six": "(L_*+6)" in fixture["local_click"],
        "compact_kernel_is_only_covariant": kernel["status"] == "COVARIANT_COMPACT_HARD_PACKET_KERNEL_CONSTRUCTED" and interpretation["finite_duration_BT_Dyson_affiliation"] == "NOT_PROVED",
        "finite_scheme_boundary_is_explicit": "finite coupling redefinition" in bubble["finite_scheme_freedom"] and "scheme independence" in limits[3],
        "complete_q6_is_not_promoted": interpretation["complete_tagged_q6_probability"] == "NOT_COMPUTED",
        "Eq19_gravity_Lorentzian_boundaries_are_exact": interpretation["general_Eq19"] == "NOT_PROVED" and interpretation["gravity_or_BV_BRST_transfer"] == "NOT_CONSTRUCTED" and interpretation["Lorentzian_causal_claim"] == "NOT_ESTABLISHED",
        "next_gate_is_finite_duration_affiliation": "second-order finite-duration Dyson kernel" in certificate["next_gate"] and "Only then" in certificate["next_gate"],
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
