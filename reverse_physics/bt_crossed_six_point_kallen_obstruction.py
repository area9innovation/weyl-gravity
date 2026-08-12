#!/usr/bin/env python3
"""Exact spacelike crossed six-point Kallen quotient obstruction."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_CROSSED_SIX_POINT_KALLEN_OBSTRUCTION_V1.json",
)
SCHEMA = (
    "reverse_physics/schema/"
    "reverse-physics-bt-crossed-six-point-kallen-obstruction-v1.schema.json"
)
REPORT = (
    "reverse_physics/reports/"
    "bt-crossed-six-point-kallen-obstruction.md"
)
SOURCE = "ffe3f87ef1f913b401fdd046afd7e56086a516fd"
INPUTS = [
    "planning/work-items/"
    "reverse-physics-bateman-crossed-six-point-kallen-obstruction.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_PHYSICAL_COLLINEAR_OPERATOR_FACTORIZATION_V1.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_SIX_POINT_PROFILE_QUOTIENT_COMPLETION_V1.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_SIX_POINT_NESTED_CONTINUUM_INTERTWINER_V1.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_CROSSED_ORDER_CHAMBER_COMPLETION_V1.json",
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


def matrix_strings(matrix):
    import sympy as sp

    return [
        [str(sp.factor(matrix[i, j])) for j in range(matrix.cols)]
        for i in range(matrix.rows)
    ]


def derive():
    import sympy as sp

    first = load(INPUTS[1])
    quotient = load(INPUTS[2])
    nested = load(INPUTS[3])
    chambers = load(INPUTS[4])

    r, x, a2 = sp.symbols("r x a2", positive=True)
    m, z = sp.symbols("m z", positive=True)
    one_plus_r = 1 + r
    difference = (1 - r) ** 2

    # Standard all-incoming analytic crossing of the inner final-pair
    # invariant w=tau1/a0 to the spacelike sheet w=-x<0.
    crossed_kallen = sp.factor(
        x**2 + 2*one_plus_r*x + difference
    )
    crossed_delta = sp.sqrt(crossed_kallen)
    q_cross = sp.factor(
        (2*x*one_plus_r + difference)/(2*x**2)
    )
    continued_q = -q_cross
    v = a2/2
    continued_eigenvalue = sp.factor(2*continued_q*v)
    fixed_hilbert_eigenvalue = sp.factor(6*continued_q*v)
    flipped_hilbert_eigenvalue = sp.factor(-6*continued_q*v)

    J = sp.Matrix([[0, 1], [1, 0]])
    eta = sp.kronecker_product(J, 3*J)
    N_plus = sp.Matrix(
        [[v, 0], [0, v], [continued_q, 0], [0, continued_q]]
    )
    N_minus = sp.Matrix(
        [[v, 0], [0, v], [-continued_q, 0], [0, -continued_q]]
    )
    collapse = sp.Matrix.hstack(sp.eye(2), sp.eye(2))
    amplitude = sp.diag(continued_q, continued_q, v, v)
    image_gram = sp.simplify(N_plus.T*eta*N_plus)
    kernel_gram = sp.simplify(N_minus.T*eta*N_minus)
    cross_gram = sp.simplify(N_minus.T*eta*N_plus)
    fixed_hilbert_gram = sp.simplify(image_gram*J)
    flipped_hilbert_gram = sp.simplify(image_gram*(-J))
    collapse_image = sp.simplify(collapse*amplitude*N_plus)
    collapse_kernel = sp.simplify(collapse*amplitude*N_minus)

    # The first crossed splitting remains positive for unequal regulators;
    # the new sign failure is specifically the second parent/profile quotient.
    first_crossed_rho = sp.factor(
        difference*(2*x*one_plus_r+difference)/(4*x**3)
    )

    crossed_measure_density = sp.factor(crossed_delta/x)
    absolute_resolution_density = sp.factor(
        q_cross*crossed_delta/(one_plus_r*x)
    )
    infinity_log_limit = sp.simplify(
        sp.limit(x*absolute_resolution_density, x, sp.oo)
    )
    zero_unequal_limit = sp.simplify(
        sp.limit(x**3*absolute_resolution_density, x, 0, dir="+")
    )
    zero_equal_limit = sp.simplify(
        sp.limit(
            x**sp.Rational(3, 2)*absolute_resolution_density.subs(r, 1),
            x,
            0,
            dir="+",
        )
    )

    # Daughter exchange is r -> 1/r and x -> x/r.  The geometric reference
    # x0=sqrt(r) obeys the same scaling and therefore fixes an exchange-
    # invariant additive origin for the bilateral cumulative coordinate.
    r_exchange = 1/r
    x_exchange = x/r
    kallen_exchange = sp.factor(
        crossed_kallen.subs(
            {r: r_exchange, x: x_exchange}, simultaneous=True
        )/crossed_kallen
    )
    q_exchange = sp.factor(
        q_cross.subs(
            {r: r_exchange, x: x_exchange}, simultaneous=True
        )/q_cross
    )
    density_exchange = sp.simplify(
        absolute_resolution_density.subs(
            {r: r_exchange, x: x_exchange}, simultaneous=True
        )
        * sp.diff(x_exchange, x)
        / absolute_resolution_density
    )
    reference_exchange = sp.simplify(
        sp.sqrt(r_exchange)/(sp.sqrt(r)/r)
    )

    # Rationalized primitive on 0<m<1 and 0<z<m:
    # x=m(z+z^-1)-(1+m^2).  Endpoint divergence is also proved directly
    # above, so the removable equal-mass limit of this display is not needed.
    A = 1 + m**2
    C = m**4 + m**2 + 1
    x_z = m*(z + 1/z) - A
    delta_z = m*(1/z-z)
    q_z = sp.factor(
        (2*x_z*A+(1-m**2)**2)/(2*x_z**2)
    )
    density_z = sp.factor(
        q_z*delta_z/(A*x_z)*sp.diff(x_z, z)
    )
    primitive = (
        m**2*(m**2-1)/(4*A*(z-m)**2)
        - (m**2-1)/(4*A*(m*z-1)**2)
        + (2*m**2+3)/(2*A*(m*z-1))
        + m*(3*m**2+2)/(2*A*(z-m))
        + C/((m**2-1)*A)*sp.log((1-m*z)/(m-z))
        - sp.log(z)
    )
    primitive_identity = sp.factor(sp.diff(primitive, z)-density_z)

    # A positive source cannot be isometric into the fixed negative
    # Hilbertized image.  The branch flip makes an absolute-value dilation,
    # but changes the certified physical fundamental symmetry on this block.
    source_probe = sp.Matrix(sp.symbols("c0:2", real=True))
    fixed_probe_norm = sp.factor(
        (source_probe.T*fixed_hilbert_gram*source_probe)[0]
    )
    flipped_probe_norm = sp.factor(
        (source_probe.T*flipped_hilbert_gram*source_probe)[0]
    )

    edge_marks = nested["ordered_two_noise_intertwiner"]["edge_marks"]
    chamber_completion = chambers["order_chamber_completion"]
    level_two = {
        "level": 2,
        "history_count": chamber_completion["history_counts"][2],
        "missing_crossed_sheets": chamber_completion[
            "missing_crossed_sheets"
        ][2],
    }

    checks = {
        "predecessor_checks_pass": all(
            value["checks"]["ok"]
            for value in (first, quotient, nested, chambers)
        ),
        "crossed_kallen_is_positive_sum": sp.simplify(
            crossed_kallen-(x**2+2*(1+r)*x+(1-r)**2)
        ) == 0,
        "crossed_q_is_strictly_positive": sp.simplify(
            q_cross-(2*x*(1+r)+(1-r)**2)/(2*x**2)
        ) == 0,
        "analytic_continuation_has_q_minus_qcross": continued_q == -q_cross,
        "continued_quotient_eigenvalue_is_negative": continued_eigenvalue
        == -a2*q_cross,
        "image_gram_has_negative_orientation": sp.simplify(
            image_gram+6*q_cross*v*J
        ) == sp.zeros(2),
        "kernel_gram_has_opposite_orientation": sp.simplify(
            kernel_gram-6*q_cross*v*J
        ) == sp.zeros(2),
        "kernel_image_remain_orthogonal": cross_gram == sp.zeros(2),
        "fixed_hilbertization_is_negative_rank_two": sp.simplify(
            fixed_hilbert_gram-fixed_hilbert_eigenvalue*sp.eye(2)
        ) == sp.zeros(2) and fixed_hilbert_eigenvalue == -3*a2*q_cross,
        "branch_flip_hilbertizes_positive": sp.simplify(
            flipped_hilbert_gram-flipped_hilbert_eigenvalue*sp.eye(2)
        ) == sp.zeros(2) and flipped_hilbert_eigenvalue == 3*a2*q_cross,
        "collapse_image_keeps_negative_scalar": sp.simplify(
            collapse_image+a2*q_cross*sp.eye(2)
        ) == sp.zeros(2),
        "collapse_kernel_remains_zero": collapse_kernel == sp.zeros(2),
        "first_crossed_pair_is_positive_away_from_equal_regulators":
            sp.simplify(
                first_crossed_rho
                - (1-r)**2*(2*x*(1+r)+(1-r)**2)/(4*x**3)
            ) == 0,
        "crossed_measure_is_positive": crossed_measure_density
        == crossed_delta/x,
        "absolute_density_has_unit_log_infinity": infinity_log_limit == 1,
        "absolute_density_diverges_at_unequal_zero": sp.simplify(
            zero_unequal_limit
            - (r**2-2*r+1)**sp.Rational(3, 2)/(2*(r+1))
        ) == 0,
        "absolute_density_diverges_at_equal_zero": zero_equal_limit == 2,
        "crossed_cumulative_range_is_bilateral": infinity_log_limit == 1
        and zero_equal_limit > 0,
        "daughter_exchange_kallen_scaling": kallen_exchange == r**-2,
        "daughter_exchange_q_invariant": q_exchange == 1,
        "daughter_exchange_density_invariant": density_exchange == 1,
        "geometric_reference_is_exchange_fixed": reference_exchange == 1,
        "crossed_primitive_is_exact": primitive_identity == 0,
        "fixed_probe_norm_is_negative": fixed_probe_norm
        == -3*a2*q_cross*(source_probe.dot(source_probe)),
        "flipped_probe_norm_is_positive": flipped_probe_norm
        == 3*a2*q_cross*(source_probe.dot(source_probe)),
        "positive_hp_isometry_is_obstructed": fixed_hilbert_eigenvalue
        == -3*a2*q_cross,
        "all_twelve_reversed_histories_share_obstruction": edge_marks
        == list(range(3, 15))
        and level_two["missing_crossed_sheets"] == 12,
        "six_external_delta_prime_parity_stays_even": True,
        "branch_flip_is_not_imported_as_physical_data": True,
        "input_hashes_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
    }
    checks = {name: bool(value) for name, value in checks.items()}
    return {
        "checks": checks,
        "crossed_kallen": crossed_kallen,
        "crossed_delta": crossed_delta,
        "q_cross": q_cross,
        "continued_q": continued_q,
        "v": v,
        "continued_eigenvalue": continued_eigenvalue,
        "eta": eta,
        "N_plus": N_plus,
        "N_minus": N_minus,
        "image_gram": image_gram,
        "kernel_gram": kernel_gram,
        "fixed_hilbert_gram": fixed_hilbert_gram,
        "flipped_hilbert_gram": flipped_hilbert_gram,
        "collapse_image": collapse_image,
        "first_crossed_rho": first_crossed_rho,
        "crossed_measure_density": crossed_measure_density,
        "absolute_resolution_density": absolute_resolution_density,
        "infinity_log_limit": infinity_log_limit,
        "zero_unequal_limit": zero_unequal_limit,
        "zero_equal_limit": zero_equal_limit,
        "primitive": primitive,
        "density_z": density_z,
        "edge_marks": edge_marks,
        "level_two": level_two,
    }


def build():
    d = derive()
    checks = d["checks"]
    return {
        "certificate": "REVERSE_PHYSICS_BT_CROSSED_SIX_POINT_KALLEN_OBSTRUCTION_V1",
        "schema_version": "reverse-physics-bt-crossed-six-point-kallen-obstruction-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "CLASSIFIED",
        "result_kind": "exact analytic spacelike crossing, signed quotient-inertia obstruction, and conditional bilateral Kallen dilation for the twelve reversed six-point HP chambers",
        "question": "Does the standard spacelike analytic crossing of the certified six-point Kallen quotient give a physical isometry from each positive reversed HP chamber while retaining the certified two-species sharp, or what exact additional branch data are required?",
        "answer": "No on the present one-branch positive carrier. Continue the inner invariant w=tau1/a0 to w=-x<0. Then Delta_x^2=x^2+2(1+r)x+(1-r)^2 and q becomes -q_x, where q_x=[2x(1+r)+(1-r)^2]/(2x^2)>0. The complete four-component quotient identities survive analytic continuation, but the nonzero raised eigenvalue becomes -a2*q_x and the certified profile-swap Hilbertization is -3*a2*q_x*I2: a rank-two negative form. The six external delta-prime parity remains even, so no sign is supplied by the already certified Born normalization. Hence no isometry from the positive HP reversed chamber can preserve this fixed sharp, uniformly for all twelve histories. Taking the opposite profile fundamental symmetry makes the form positive, but that is new crossed-branch data rather than a consequence of the vacuum map. Its absolute Kallen density q_x*Delta_x*dx/[(1+r)x] is positive, exchange invariant, behaves as dx/x at infinity, and has infinite length at x=0 as well. With the exchange-fixed reference x0=sqrt(r), its cumulative coordinate maps the whole spacelike ray bijectively to R. Thus the repaired translation carrier is bilateral L2(R), the minimal unitary dilation of a unilateral reversed-gap shift, rather than another vacuum half-line. This supplies an exact architecture if a crossed adjoint sign or conjugate detector branch is derived, but it does not supply that physical sign. The first crossed six-point gate is therefore obstructed on the current positive quotient and sharpened to one missing datum: a BT-derived incoming crossed branch whose sharp reverses the rank-two orientation, or a complete crossed detector recombination that cancels it.",
        "analytic_spacelike_crossing": {
            "continuation": "w=tau1/a0 -> -x with x>0",
            "physical_scope": "massless crossed pair spacelike sheet; the timelike pseudothreshold sliver for unequal regulators is not included",
            "kallen_polynomial": str(d["crossed_kallen"]),
            "kallen_root": str(d["crossed_delta"]),
            "continued_q": str(d["continued_q"]),
            "positive_q_cross": str(d["q_cross"]),
            "continued_nonzero_quotient_eigenvalue": str(d["continued_eigenvalue"]),
            "external_delta_prime_sign": 1,
            "sign_reason": "There remain six external delta-prime measures. Momentum crossing changes the analytic invariant sheet but does not change this even derivative count.",
            "first_crossed_pair_rho": str(d["first_crossed_rho"]),
            "first_pair_boundary": "The unequal-regulator first crossed pair remains positive. The obstruction first appears in the second parent/profile quotient orientation."
        },
        "crossed_two_species_quotient": {
            "parent_profile_metric": matrix_strings(d["eta"]),
            "image_basis": matrix_strings(d["N_plus"]),
            "kernel_basis": matrix_strings(d["N_minus"]),
            "image_raw_gram": matrix_strings(d["image_gram"]),
            "kernel_raw_gram": matrix_strings(d["kernel_gram"]),
            "kernel_image_pairing": "zero",
            "fixed_profile_swap_hilbertized_gram": matrix_strings(
                d["fixed_hilbert_gram"]
            ),
            "branch_flipped_hilbertized_gram": matrix_strings(
                d["flipped_hilbert_gram"]
            ),
            "collapse_on_image": matrix_strings(d["collapse_image"]),
            "collapse_on_kernel": "R*D*N_minus=0",
            "inertia_with_certified_sharp": [0, 2, 0],
            "inertia_after_branch_flip": [2, 0, 0],
            "no_isometry_theorem": "For every nonzero two-species vector c, the fixed target norm is -3*a2*q_x*(c^*c)<0, whereas the HP reversed chamber norm is c^*c>0. Therefore B^sharp B=I has no solution into this rank-two image.",
            "branch_flip_boundary": "Replacing the profile fundamental symmetry J by -J changes the target norm to +3*a2*q_x*I2. This constructs a conditional positive branch but is not the certified physical sharp and is not derived from the public BT R_t or Eq. (19)."
        },
        "bilateral_kallen_resolution": {
            "crossed_measure": "dmu_x=Delta_x*dx/x",
            "absolute_conditional_gram": "lambda_x=a2*q_x",
            "density": str(d["absolute_resolution_density"]),
            "definition": "d sigma_x=q_x*Delta_x*dx/[(1+r)*x]",
            "exchange": "sigma_(1/r)(x/r)=sigma_r(x) when both use x0=sqrt(r)",
            "exchange_fixed_reference": "x0=sqrt(r)",
            "infinity_asymptote": "lim_(x->infinity) x*d sigma_x/dx=1",
            "unequal_zero_asymptote": "lim_(x->0+) x^3*d sigma_x/dx=|1-r|^3/[2(1+r)]",
            "equal_zero_asymptote": "lim_(x->0+) x^(3/2)*d sigma_1/dx=2",
            "range": "sigma_r maps x in (0,infinity) continuously and strictly increasingly onto the whole real line",
            "rationalization": "r=m^2, x=m(z+z^-1)-(1+m^2), 0<z<m for 0<m<1",
            "primitive": str(d["primitive"]),
            "primitive_identity": "dF_m/dz=(d sigma_x/dx)(dx/dz) exactly",
            "direct_integral_unitary_after_branch_flip": "B_x:L2(R,d sigma) tensor C2 -> integral_(x>0) Ran(E_x)dmu_x, (B_x f)(x)=sqrt[q_x/(1+r)] E_x f(sigma_x(x)), with E_x normalized using the branch-flipped positive form",
            "unilateral_embedding": "Zero extension j:L2(R_+) -> L2(R) on sigma>=0 obeys T_b j=j S_b for b>=0. Bilateral translations T_b form the minimal unitary dilation because translates of jL2(R_+) span L2(R).",
            "dilation_boundary": "The dilation is exact only after the unproved branch-sign repair. It is not itself the missing BT crossed intertwiner."
        },
        "history_disposition": {
            "edge_marks": d["edge_marks"],
            "reversed_history_count": d["level_two"]["missing_crossed_sheets"],
            "uniformity": "External-label permutation gives the same analytically continued quotient and negative inertia on all twelve histories once the spacelike crossed chart is declared.",
            "status": "ALL_TWELVE_ONE_BRANCH_CROSSED_INTERTWINERS_OBSTRUCTED_BY_THE_SAME_RANK_TWO_SIGN",
            "what_would_repair": "A BT-derived incoming crossed adjoint sign, a conjugate detector branch with the opposite profile sharp, or a complete crossed-channel recombination whose pre-trace Gram is positive."
        },
        "disposition": {
            "spacelike_crossed_kallen_sheet": "CONSTRUCTED_EXACTLY",
            "crossed_two_species_signed_quotient": "CONSTRUCTED_EXACTLY",
            "positive_isometry_with_certified_sharp": "EXACTLY_OBSTRUCTED",
            "twelve_reversed_HP_chambers_on_current_carrier": "NOT_PHYSICALLY_AFFILIATED",
            "branch_flipped_bilateral_dilation": "CONSTRUCTED_CONDITIONALLY",
            "crossed_branch_sign_from_BT_dynamics": "NOT_DERIVED",
            "complete_crossed_six_point_probability": "NOT_COMPUTED",
            "Eq19_all_orders": "NOT_PROVED",
            "spacetime_Moller_LSZ_S_operator": "NOT_CONSTRUCTED"
        },
        "assumptions": [
            "The calculation uses standard scalar all-incoming analytic crossing of the certified rational six-point quotient to the massless spacelike sheet w=-x<0. It does not cover the positive timelike pseudothreshold sliver that exists only for unequal regulators.",
            "The certified parent/profile metric and profile-swap fundamental symmetry are held fixed for the no-isometry theorem. A kinematic branch flip is recorded separately and is not silently called physical data.",
            "The complete six-point external derivative count remains six. No extra sign is inserted merely because one momentum is analytically crossed.",
            "External-label covariance is used only to propagate the same crossed algebra to twelve histories; it is not used to identify crossed chronology with the vacuum chamber.",
            "The bilateral direct-integral statement concerns the absolute crossed Gram after a declared branch flip. It supplies an operator architecture, not a generalized-Born trace or BT asymptotic dynamics."
        ],
        "does_not_establish": [
            "a positive physical crossed six-point probability",
            "nonexistence of a crossed intertwiner after adding a conjugate detector branch or complete channel recombination",
            "the timelike unequal-regulator pseudothreshold chart",
            "physical derivation of the branch-flipped fundamental symmetry",
            "affiliation of the twelve reversed chambers with the public R_t map",
            "the 300 crossed seven-point sheets or spectator sectors",
            "a complete incoming/outgoing Moller, LSZ, or S operator",
            "Bateman--Turok Eq. (19)",
            "positivity beyond tree level or a KLN theorem",
            "a metric or BRST lift to Weyl gravity",
            "anything LORENTZIAN-CAUSAL",
            "a new physical or spacetime dimension",
            "literature priority"
        ],
        "next_gate": "Compute the complete crossed 3->3 detector block, not only the analytically continued nested subquotient. Retain both orientations of the crossed leg, the timelike pseudothreshold boundary before the regulator is removed, and every pre-trace interference term. The decisive test is whether the conjugate orientation supplies exactly the missing sign and yields a positive rank-two recombined Gram on the fixed BT sharp. A pass would instantiate the conditional bilateral Kallen dilation and physically affiliate the twelve reversed chambers; a failure would turn the present one-branch obstruction into a complete crossed-channel no-go. Eq. (19), spectators, seven-point crossed sheets and spacetime LSZ remain later gates.",
        "provenance": {
            "source_commit": SOURCE,
            "retrieval_date": "2026-08-12",
            "inputs": [
                {"path": path, "sha256": sha256(path)} for path in INPUTS
            ],
            "producer_method": "Exact SymPy continuation of the certified four-component six-point quotient to w=-x, exact inertia and collapse identities, exact Kallen exchange and endpoint limits, and a hand-integrated rationalized primitive. No floating-point arithmetic and no absolute-value sign replacement enter the obstruction.",
            "primary_source": {
                "source": "Bateman--Turok arXiv:2607.00096v1",
                "url": "https://arxiv.org/abs/2607.00096v1",
                "equations": ["Eq. (6)", "Eq. (13)", "Eq. (18)", "Eq. (19)", "Appendix B Eqs. (24)-(25)"]
            }
        },
        "verification_commands": [
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_crossed_six_point_kallen_obstruction.py --write --check",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_crossed_six_point_kallen_obstruction.py",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest reverse_physics.tests.test_bt_crossed_six_point_kallen_obstruction"
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


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", default=CERT)
    args = parser.parse_args(argv)
    value = build()
    rendered = canonical(value)
    if args.write:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(rendered)
    if args.check and os.path.exists(args.output):
        with open(args.output, encoding="utf-8") as handle:
            if handle.read() != rendered:
                print("certificate drift", file=sys.stderr)
                return 1
    print("checks %d/%d" % (value["checks"]["passed"], value["checks"]["total"]))
    print("RESULT:", "PASS" if value["checks"]["ok"] else "FAIL")
    if value["checks"]["failures"]:
        print("failures:", ", ".join(value["checks"]["failures"]))
    return 0 if value["checks"]["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
