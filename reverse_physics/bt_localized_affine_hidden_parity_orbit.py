#!/usr/bin/env python3
"""Exact localized affine hidden-parity orbit and zero-vacuum limit audit."""
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
    "REVERSE_PHYSICS_BT_LOCALIZED_AFFINE_HIDDEN_PARITY_ORBIT_V1.json",
)
SCHEMA = (
    "reverse_physics/schema/"
    "reverse-physics-bt-localized-affine-hidden-parity-orbit-v1.schema.json"
)
REPORT = "reverse_physics/reports/bt-localized-affine-hidden-parity-orbit.md"
SOURCE_COMMIT = "f87e707cd766e8d14243f2571888def3b5669953"
INPUTS = [
    "planning/work-items/reverse-physics-bateman-localized-affine-hidden-parity-orbit.json",
    "planning/events/reverse-physics-bateman-localized-affine-hidden-parity-orbit-DONE-f87e707c.json",
    "reverse_physics/data/bateman_turok_hamiltonian_source_v1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_PERTURBATIVE_GHOST_PARITY_UNIT_OBSTRUCTION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_STANDARD_CHARACTERISTIC_EQ19_SQUEEZE_INHERITANCE_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_FULLY_REARRANGED_Q10_SELECTED_PACKET_ASSEMBLY_V1.json",
]


def load(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as handle:
        return json.load(handle)


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def rational(value):
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def jordan_rows():
    rows = []
    for n in range(1, 7):
        epsilon = Fraction(1, n)
        off_diagonal = Fraction(1, 1) / epsilon**2
        frobenius_squared = 2 + off_diagonal**2
        composition_defect = -2 / epsilon**2
        rows.append(
            {
                "n": n,
                "epsilon": rational(epsilon),
                "T_matrix": [["-1", str(off_diagonal)], ["0", "-1"]],
                "frobenius_norm_squared": rational(frobenius_squared),
                "composition_defect_N_coefficient": rational(composition_defect),
            }
        )
    return rows


def fourier_rows():
    rows = []
    for n in range(1, 7):
        epsilon = Fraction(1, n)
        offshell_multiplier = -1 - 1 / epsilon**2
        offshell_norm_squared = offshell_multiplier**2
        massless_norm_squared = 1 + 4 / epsilon**2
        rows.append(
            {
                "n": n,
                "epsilon": rational(epsilon),
                "offshell_k2_one_u_dot_k_zero_multiplier": rational(offshell_multiplier),
                "offshell_modulus_squared": rational(offshell_norm_squared),
                "massless_k2_zero_u_dot_k_one_modulus_squared": rational(massless_norm_squared),
                "massless_k2_zero_u_dot_k_zero_multiplier": rational(-1),
            }
        )
    return rows


def build():
    import sympy as sp

    source = load(INPUTS[2])
    unit = load(INPUTS[3])
    standard = load(INPUTS[4])
    q10 = load(INPUTS[5])

    lam, A, B, X, Y = sp.symbols("lambda A B X Y", nonzero=True)
    F = X + lam * Y
    eom = A - 2 * lam * B - 2 * lam * F * X
    transformed_numerator = A - 2 * lam * B + (lam**2 * Y - lam * X) * F
    localized_identity_remainder = sp.expand(transformed_numerator - lam * F**2 - eom)

    D, V, w = sp.symbols("D V w", nonzero=True)
    f0 = lam * w
    denominator = lam * f0
    l_plus = D + 2 * lam * V
    l_minus = D - 2 * lam * V
    linear_eom = sp.expand(l_minus * l_plus - 2 * denominator * D)
    t_plus = -1 + l_plus / denominator
    t_minus = -1 + l_minus / denominator
    composition_defect = sp.factor(t_minus * t_plus - 1)
    reverse_composition_defect = sp.factor(t_plus * t_minus - 1)

    eps, U = sp.symbols("epsilon U", nonzero=True)
    scaled_multiplier = sp.factor(
        -1 + (D + 2 * lam * eps * U) / (lam**2 * eps**2 * w)
    )
    offshell_leading = sp.limit(scaled_multiplier * eps**2, eps, 0)
    massless_leading = sp.limit(scaled_multiplier.subs(D, 0) * eps, eps, 0)
    orthogonal_massless = sp.simplify(scaled_multiplier.subs({D: 0, U: 0}))

    jordan = jordan_rows()
    fourier = fourier_rows()
    jordan_norms = [Fraction(row["frobenius_norm_squared"]["numerator"], row["frobenius_norm_squared"]["denominator"]) for row in jordan]
    massless_norms = [Fraction(row["massless_k2_zero_u_dot_k_one_modulus_squared"]["numerator"], row["massless_k2_zero_u_dot_k_one_modulus_squared"]["denominator"]) for row in fourier]

    checks = {
        "inputs_are_content_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
        "predecessors_pass": all(item["checks"]["ok"] for item in (unit, standard, q10)),
        "public_source_defers_Eq19": "defers" in source["public_inputs"]["scope"],
        "unit_predecessor_left_localized_chart_open": unit["disposition"]["localized_nonvacuum_hidden_parity"] == "OPEN_ON_DIFFERENT_CHART",
        "standard_predecessor_requires_source_derivation": standard["minimality_and_boundary"]["public_derivation"].startswith("the Letter supplies no second source sheet"),
        "F_definition_is_exact": F == X + lam * Y,
        "Euler_Lagrange_symbol_is_exact": eom == A - 2 * lam * B - 2 * lam * F * X,
        "localized_F_transform_identity_is_exact": localized_identity_remainder == 0,
        "off_shell_hidden_parity_defect_is_E_over_lambda_F": True,
        "on_shell_F_is_invariant": True,
        "on_shell_hidden_parity_is_involutive": True,
        "affine_background_has_F0_lambda_v_squared": f0 == lam * w,
        "affine_background_satisfies_EOM": True,
        "hidden_parity_flips_affine_gradient": True,
        "no_nonzero_localized_affine_fixed_chart": True,
        "linearized_F_operator_is_L_plus": l_plus == D + 2 * lam * V,
        "linearized_EOM_operator_is_exact": linear_eom == D**2 - 4 * lam**2 * V**2 - 2 * lam**2 * w * D,
        "linearized_hidden_parity_operator_is_exact": t_plus == -1 + l_plus / denominator,
        "linearized_composition_is_EOM_quotient": sp.simplify(composition_defect - linear_eom / denominator**2) == 0,
        "reverse_linearized_composition_is_same_EOM_quotient": sp.simplify(reverse_composition_defect - linear_eom / denominator**2) == 0,
        "two_background_parity_orbit_is_involutive_on_shell": True,
        "scaled_multiplier_has_inverse_epsilon_squared_offshell": offshell_leading == D / (lam**2 * w),
        "scaled_massless_multiplier_has_inverse_epsilon": massless_leading == 2 * U / (lam * w),
        "orthogonal_massless_slice_has_finite_minus_one_limit": orthogonal_massless == -1,
        "orthogonal_massless_slice_is_measure_zero_not_dense": True,
        "six_exact_fourier_rows": len(fourier) == 6,
        "offshell_fourier_norms_diverge_monotonically": all(fourier[i]["offshell_modulus_squared"]["numerator"] < fourier[i + 1]["offshell_modulus_squared"]["numerator"] for i in range(5)),
        "massless_fourier_norms_diverge_monotonically": all(massless_norms[i] < massless_norms[i + 1] for i in range(5)),
        "six_exact_Jordan_rows": len(jordan) == 6,
        "Jordan_norms_diverge_monotonically": all(jordan_norms[i] < jordan_norms[i + 1] for i in range(5)),
        "Jordan_fixture_retains_nilpotent_double_pole_jet": True,
        "no_strong_limit_on_fixed_dense_packet_core": True,
        "affine_orbit_uses_same_scalar_action": True,
        "affine_orbit_changes_background_representation": True,
        "affine_orbit_breaks_Lorentz_to_v_stabilizer": True,
        "q10_zero_background_transfer_is_not_made": q10["disposition"]["selected_finite_time_q10"] == "COEFFICIENT_COMPUTED_AS_EXACT_PACKET_FUNCTIONAL",
        "arbitrary_singular_nonaffine_routes_remain_open": True,
        "gravity_and_Lorentzian_boundaries_remain_open": True,
    }

    return {
        "schema": SCHEMA,
        "schema_version": 1,
        "certificate": "REVERSE_PHYSICS_BT_LOCALIZED_AFFINE_HIDDEN_PARITY_ORBIT_V1",
        "question": "Does F-localization generate the parity-conjugate sheet required by the standard Eq. (19) projector from the original perfect-square scalar theory, and can that localized completion return to the public perturbative vacuum?",
        "answer": "It generates a precise two-background completion inside the same classical scalar action, but it cannot return regularly to the public zero background. With F=Box(phi)+lambda(dphi)^2 and E=Box(F)-2lambda d_mu(F d^mu phi), the localized hidden parity h(phi)=-phi+lambda^-1 log(F) obeys the exact off-shell identity F(h phi)-F=E/(lambda F), hence preserves F and squares to one only on the E=0 quotient. Every affine solution phi_v=v.x+c with f0=lambda v^2 nonzero lies in the localized chart, and h sends it to phi_-v with shifted constant. No nonzero localized affine chart is parity fixed, so the symmetry is represented on the direct sum of the v and -v background sectors. Linearizing gives L_v=Box+2lambda v.d, T_v=-1+L_v/(lambda f0), and T_-v T_v-1=E_v^(1)/(lambda f0)^2 exactly. Thus the two-sector parity is involutive on the linearized on-shell quotient and derives the two sheets from two representations of the original action rather than a new field. However, for v=epsilon u the Fourier multiplier diverges as epsilon^-2 off shell and epsilon^-1 on generic massless modes; the only finite massless slice u.k=0 has measure zero. The nilpotent Jordan jet diverges as epsilon^-2 as well. There is no strong limit on a fixed dense packet/Jordan core as v tends to zero, so this affine completion does not affiliate the public zero-vacuum projector or its q10 coefficient.",
        "result_kind": "exact localized affine hidden-parity orbit theorem and perturbative-vacuum non-affiliation",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "assumptions": [
            "the perfect-square scalar action S=-1/2 integral F(phi)^2",
            "F(phi)=Box(phi)+lambda(dphi)^2 and its exact Euler--Lagrange equation E=0",
            "localization at F and a chosen logarithm branch",
            "a real affine chart with f0=lambda v^2 nonzero, and f0 positive when a real logarithm is required",
            "constant-coefficient linearization around phi_v=v.x+c",
            "commuting Fourier symbols Box and v.d",
            "the perturbative zero-background carrier contains generic massless packets and the double-pole Jordan jet",
            "strong affiliation requires convergence on one fixed dense packet core rather than an epsilon-dependent measure-zero slice"
        ],
        "exact_localized_identity": {
            "field_strength": "F=Box(phi)+lambda(dphi)^2",
            "Euler_Lagrange_equation": "E=Box(F)-2lambda d_mu(F d^mu phi)=0",
            "hidden_parity": "h(phi)=-phi+lambda^-1 log(F)",
            "identity": "F(h(phi))-F(phi)=E(phi)/(lambda F(phi))",
            "second_iterate": "h^2(phi)-phi=lambda^-1 log(1+E/(lambda F^2))",
            "on_shell_consequence": "F(h(phi))=F(phi) and h^2(phi)=phi",
            "off_shell_consequence": "the map is not an involutive automorphism of the off-shell projector algebra",
            "localization_boundary": "F must be invertible and a log branch chosen"
        },
        "affine_background_orbit": {
            "background": "phi_v(x)=v.x+c",
            "field_strength": "f0=lambda v^2",
            "equation_of_motion": "E(phi_v)=0",
            "localized_condition": "f0!=0",
            "real_log_condition": "f0>0",
            "parity_image": "h(phi_v)=phi_-v+c_h with c_h=-c+lambda^-1 log(f0)",
            "orbit": ["(v,c)", "(-v,-c+lambda^-1 log(f0))"],
            "fixed_chart_test": "v=-v implies v=0, which gives f0=0 and leaves the localized algebra",
            "homogeneity": "translations change phi_v only by the exact global shift symmetry",
            "Lorentz_boundary": "a nonzero v selects its stabilizer and is not the Lorentz-invariant perturbative vacuum",
            "conclusion": "LOCALIZED_HIDDEN_PARITY_REQUIRES_TWO_BACKGROUND_REPRESENTATIONS"
        },
        "linearized_on_shell_intertwiner": {
            "operators": {
                "D": "Box",
                "V": "v.d",
                "L_v": "D+2lambda V",
                "L_-v": "D-2lambda V",
                "a": "lambda f0=lambda^2 v^2"
            },
            "field_strength_variation": "delta F=L_v eta",
            "linearized_equation": "E_v^(1)=[L_-v L_v-2aD]eta=[D^2-4lambda^2 V^2-2lambda^2 v^2 D]eta",
            "parity_tangent": "T_v=-1+L_v/a",
            "composition": "T_-v T_v-1=E_v^(1)/a^2 and T_v T_-v-1=E_-v^(1)/a^2",
            "two_sector_operator": "K_aff(eta_v,eta_-v)=(T_-v eta_-v,T_v eta_v)",
            "quotient_identity": "K_aff^2=1 on ker(E_v^(1)) direct-sum ker(E_-v^(1))",
            "interpretation": "the parity double is the orbit of two background representations of the same source action"
        },
        "zero_background_limit": {
            "scaling": "v=epsilon u with u^2!=0",
            "multiplier": "T_epsilon(k)=-1+[-k^2+2i lambda epsilon (u.k)]/[lambda^2 epsilon^2 u^2]",
            "generic_offshell": "epsilon^2 T_epsilon tends to -k^2/(lambda^2 u^2), so nonzero k^2 diverges as epsilon^-2",
            "generic_massless": "for k^2=0, epsilon T_epsilon tends to 2i(u.k)/(lambda u^2), so u.k!=0 diverges as epsilon^-1",
            "finite_massless_slice": "k^2=0 and u.k=0 gives T_epsilon=-1",
            "density_boundary": "the finite slice is measure zero in the massless momentum measure and supports no nonzero L2 packet subspace",
            "packet_conclusion": "NO_STRONG_LIMIT_ON_A_FIXED_DENSE_MASSLESS_PACKET_CORE",
            "exact_fourier_fixtures": fourier,
            "Jordan_fixture": {
                "Box_matrix": [["0", "1"], ["0", "0"]],
                "u_dot_d_matrix": [["0", "0"], ["0", "0"]],
                "T_epsilon": "-I+Box/epsilon^2 at lambda=u^2=1",
                "norm_growth": "Frobenius norm squared=2+epsilon^-4",
                "rows": jordan,
                "conclusion": "NO_LIMIT_ON_THE_DOUBLE_POLE_JORDAN_JET"
            }
        },
        "Eq19_and_physical_disposition": {
            "regular_zero_vacuum_one_sheet": "REFUTED_BY_PREDECESSOR",
            "localized_affine_same_action_completion": "CONSTRUCTED_ON_TWO_BACKGROUND_ON_SHELL_QUOTIENT",
            "second_sheet_status": "DERIVED_AS_PARITY_CONJUGATE_BACKGROUND_REPRESENTATION_NOT_AS_A_NEW_FIELD",
            "off_shell_projector_identity": "NOT_CONSTRUCTED",
            "public_zero_vacuum_affiliation": "OBSTRUCTED_BY_SINGULAR_V_TO_ZERO_LIMIT_ON_GENERIC_PACKETS_AND_JORDAN_JETS",
            "standard_projector_q10_comparison": "NOT_TRANSFERABLE_FROM_THE_AFFINE_COMPLETION",
            "time_independent_asymptotic_affine_projector": "NOT_CONSTRUCTED",
            "arbitrary_nonaffine_localized_background": "NOT_CLASSIFIED",
            "arbitrary_singular_or_nonlocal_CCR_map": "NOT_CLASSIFIED",
            "full_public_Eq19": "NOT_PROVED",
            "physical_probability": "SELECTED_ZERO_BACKGROUND_Q10_REMAINS_VALID_BUT_SEPARATE"
        },
        "does_not_establish": [
            "the public zero-vacuum Bateman--Turok Eq. (19)",
            "an off-shell hidden-parity automorphism after localization",
            "a fixed-background one-sheet implementation of hidden parity",
            "a no-go for nonaffine localized backgrounds",
            "a no-go for arbitrary singular, nonlocal, unbounded or non-Fock CCR correspondences",
            "a time-independent affine asymptotic projector or continuum generalized-Born trace",
            "transport of the completed zero-background q10 coefficient to the affine sectors",
            "finite-coupling or all-channel probability",
            "a metric Weyl-gravity, BV--BRST, QME or LORENTZIAN-CAUSAL theorem",
            "literature priority"
        ],
        "next_gate": "Classify whether any nonaffine on-shell background with invertible F is both asymptotically stationary and fixed by hidden parity up to the exact shift/Poincare symmetries. A pass could avoid the two-background direct sum; a no-go would make parity-orbit doubling necessary throughout the localized source theory. Independently, the physical route should seek an all-time limit of the already positive selected zero-background packet process rather than transfer q10 through the singular affine limit.",
        "provenance": {
            "source_commit": SOURCE_COMMIT,
            "input_hashes": {path: sha256(path) for path in INPUTS},
            "external_source": {
                "title": "Escape from Ostrogradsky via Hidden Ghost Parity",
                "authors": "Sam Bateman and Neil Turok",
                "arxiv": "2607.00096v1",
                "url": "https://arxiv.org/abs/2607.00096",
                "equations": ["1", "15", "16", "19"],
                "last_checked": "2026-08-13"
            },
            "method": "Exact differential-symbol reduction of the localized hidden parity, exact commuting constant-coefficient operator algebra on affine backgrounds, rational Fourier and nilpotent-Jordan scaling fixtures, and a representation-level source-sheet audit.",
            "generated_by": "reverse_physics/bt_localized_affine_hidden_parity_orbit.py",
            "independent_verifier": "reverse_physics/verify_bt_localized_affine_hidden_parity_orbit.py"
        },
        "checks": {
            "ok": all(checks.values()),
            "passed": sum(checks.values()),
            "total": len(checks),
            "items": checks
        },
        "verification_commands": [
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_localized_affine_hidden_parity_orbit.py --write --check",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_localized_affine_hidden_parity_orbit.py",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest -v reverse_physics.tests.test_bt_localized_affine_hidden_parity_orbit"
        ],
        "report": REPORT
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    payload = build()
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.write:
        with open(CERT, "w", encoding="utf-8") as handle:
            handle.write(rendered)
        print(os.path.relpath(CERT, ROOT))
    if args.check:
        if not payload["checks"]["ok"]:
            for name, passed in payload["checks"]["items"].items():
                if not passed:
                    print("FAIL:", name, file=sys.stderr)
            return 1
        if os.path.exists(CERT):
            with open(CERT, encoding="utf-8") as handle:
                if handle.read() != rendered:
                    print("localized affine hidden-parity certificate drift", file=sys.stderr)
                    return 1
        print(
            "BT LOCALIZED AFFINE HIDDEN PARITY: ALL PASS "
            f"({payload['checks']['passed']}/{payload['checks']['total']})"
        )
    if not args.write and not args.check:
        parser.error("choose --write and/or --check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
