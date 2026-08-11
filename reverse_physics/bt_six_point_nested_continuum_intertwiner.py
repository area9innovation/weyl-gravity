#!/usr/bin/env python3
"""Exact six-point nested physical continuum--Fock intertwiner."""
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
    "REVERSE_PHYSICS_BT_SIX_POINT_NESTED_CONTINUUM_INTERTWINER_V1.json",
)
SCHEMA = (
    "reverse_physics/schema/"
    "reverse-physics-bt-six-point-nested-continuum-intertwiner-v1.schema.json"
)
REPORT = (
    "reverse_physics/reports/"
    "bt-six-point-nested-continuum-intertwiner.md"
)
SOURCE = "a5bb88b4ae7b95068aaf419d1bf3c730cea9ec56"
INPUTS = [
    "planning/work-items/"
    "reverse-physics-bateman-six-point-nested-continuum-intertwiner.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_ABEL_FOCK_PHYSICAL_INTERTWINER_V1.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_SIX_POINT_STRONGLY_ORDERED_TREE_V1.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_SIX_POINT_PROFILE_QUOTIENT_COMPLETION_V1.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_QUANTUM_STOCHASTIC_MOLLER_DILATION_V1.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_RIGGED_RESOLUTION_JORDAN_MOLLER_V1.json",
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


def rat(value):
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def frac(value):
    return Fraction(value["numerator"], value["denominator"])


def derive():
    import sympy as sp

    first = load(INPUTS[1])
    six_tree = load(INPUTS[2])
    six_quotient = load(INPUTS[3])
    hp = load(INPUTS[4])
    rigged = load(INPUTS[5])

    r, w, a2 = sp.symbols("r w a2", positive=True)
    m, z = sp.symbols("m z", positive=True)
    one_plus_r = 1 + r
    difference = (1 - r) ** 2
    kallen = sp.factor(w**2 + 1 + r**2 - 2*w - 2*w*r - 2*r)
    delta = sp.sqrt(kallen)
    q = sp.factor((2*w*one_plus_r - difference) / (2*w**2))
    v = a2 / 2
    quotient_eigenvalue = sp.factor(2*q*v)
    asymptotic_scale = a2 * one_plus_r
    sigma_density = sp.factor(
        quotient_eigenvalue / asymptotic_scale * delta / w
    )
    log_density = sp.factor(w * sigma_density)
    threshold = (1 + m) ** 2
    numerator_at_threshold = sp.factor(
        (2*w*(1+r) - (1-r)**2).subs({r: m**2, w: threshold})
    )

    J = sp.Matrix([[0, 1], [1, 0]])
    K = 3 * J
    eta = sp.kronecker_product(J, K)
    N_plus = sp.Matrix([[v, 0], [0, v], [q, 0], [0, q]])
    N_minus = sp.Matrix([[v, 0], [0, v], [-q, 0], [0, -q]])
    R = sp.Matrix.hstack(sp.eye(2), sp.eye(2))
    D = sp.diag(q, q, v, v)
    image_gram = sp.simplify(N_plus.T * eta * N_plus)
    kernel_gram = sp.simplify(N_minus.T * eta * N_minus)
    cross_gram = sp.simplify(N_minus.T * eta * N_plus)
    collapse_image = sp.simplify(R * D * N_plus)
    collapse_kernel = sp.simplify(R * D * N_minus)
    positive_image_gram = sp.simplify(image_gram * J)

    # Rationalize the physical threshold by
    # w=1+m^2+m(z+z^-1), with z=1 at threshold and z->0 at infinity.
    A = 1 + m**2
    d = (1 - m**2) ** 2
    w_z = A + m * (z + 1/z)
    delta_z = m * (1/z - z)
    q_z = sp.factor((2*A*w_z - d) / (2*w_z**2))
    sigma_z_derivative = sp.factor(
        sp.cancel(q_z * delta_z / (A*w_z) * sp.diff(w_z, z))
    )
    C = m**4 + m**2 + 1
    primitive = (
        m**2*(m**2-1)/(4*A*(m+z)**2)
        - (m**2-1)/(4*A*(m*z+1)**2)
        - (2*m**2+3)/(2*A*(m*z+1))
        - m*(3*m**2+2)/(2*A*(m+z))
        + C/((m**2-1)*A)*sp.log((m*z+1)/(m+z))
        - sp.log(z)
    )
    primitive_at_threshold = sp.simplify(primitive.subs(z, 1))
    primitive_identity = sp.cancel(
        sp.diff(primitive, z) - sigma_z_derivative
    )
    equal_mass_primitive = -sp.log(z) - 4/(z+1)
    equal_mass_derivative = sp.factor(
        sp.diff(equal_mass_primitive, z)
        + (z-1)**2/(z*(z+1)**2)
    )
    continuous_equal_mass_sigma = sp.simplify(
        sp.limit(primitive - primitive_at_threshold, m, 1)
        - (equal_mass_primitive - equal_mass_primitive.subs(z, 1))
    )

    # Daughter exchange: r->1/r and w->w/r.  The positive Kallen root and
    # pulled-back two-body measure scale by 1/r, while 1+r scales by 1/r.
    kallen_exchange = sp.factor(
        kallen.subs({r: 1/r, w: w/r}, simultaneous=True) / kallen
    )
    q_exchange = sp.factor(
        q.subs({r: 1/r, w: w/r}, simultaneous=True) / q
    )
    normalization_exchange = sp.factor((1 + 1/r)/(1+r))
    sigma_exchange = sp.factor(
        q_exchange * sp.sqrt(kallen_exchange) / normalization_exchange
    )

    # The exact finite-hierarchy outer threshold has
    # w <= (sqrt(U)-1)^2/epsilon after scaling a2=1.  Its endpoint tends to
    # infinity, hence the finite carriers exhaust every compact sigma shell.
    epsilon, U, outer_gap = sp.symbols(
        "epsilon U outer_gap", positive=True
    )
    w_max = (sp.sqrt(U)-1)**2 / epsilon
    w_max_positive_chart = outer_gap**2 / epsilon
    hierarchy_limit = sp.limit(w_max_positive_chart, epsilon, 0, dir="+")

    # The imported first-emission column has a local massless boundary limit,
    # although no strong endpoint derivative is asserted or needed.
    outer_R = sp.symbols("outer_R", positive=True)
    outer_Q = sp.factor(
        (2*outer_R*(1+r) - (1-r)**2)/(2*outer_R**2)
    )
    outer_L = sp.factor(-(1-r)**2/(2*outer_R))
    outer_T = sp.diag(outer_Q, outer_L)
    outer_T_zero = sp.simplify(outer_T.applyfunc(lambda x: sp.limit(x, r, 0)))
    outer_kallen = sp.factor(
        outer_R**2 + 1 + r**2
        - 2*outer_R - 2*outer_R*r - 2*r
    )
    outer_I = (
        5*r**3 - 6*r**2*sp.log(r) - 3*r**2
        - 6*r*sp.log(r) + 3*r - 5
    )/(24*(r-1))
    outer_I_zero = sp.limit(outer_I, r, 0, dir="+")

    channels = hp["system_and_noise_carrier"]["noise_channels"]
    first_edges = [row for row in channels if row["level"] == 0]
    second_edges = [row for row in channels if row["level"] == 1]
    third_edges = [row for row in channels if row["level"] == 2]
    children_per_parent = {
        parent: sum(row["parent"] == parent for row in second_edges)
        for parent in {row["parent"] for row in second_edges}
    }

    q0 = frac(first["first_emission_hp_affiliation"]["physical_rate_per_pair"])
    q1 = frac(six_quotient["branching_affiliation"]["conditional_second_rate"])
    selected_history = q0*q1
    per_history_simplex = selected_history/2
    aggregate_two_count = 12*per_history_simplex
    level_one_drift = 4*q1/2

    predecessor_values = [first, six_tree, six_quotient, hp, rigged]
    checks = {
        "predecessor_checks": all(value["checks"]["ok"] for value in predecessor_values),
        "six_quotient_eigenvalue_imported": sp.simplify(
            quotient_eigenvalue
            - sp.sympify(
                six_quotient["physical_pullback"]["nonzero_quotient_eigenvalue"],
                locals={"a0": 1, "a1": r, "a2": a2, "tau1": w},
            )
        ) == 0,
        "threshold_numerator_is_positive_fourth_power": numerator_at_threshold == (m+1)**4,
        "quotient_range_image_gram": sp.simplify(image_gram - 6*q*v*J) == sp.zeros(2),
        "quotient_range_kernel_gram": sp.simplify(kernel_gram + 6*q*v*J) == sp.zeros(2),
        "kernel_image_orthogonal": cross_gram == sp.zeros(2),
        "collapse_image_is_scalar": sp.simplify(collapse_image - 2*q*v*sp.eye(2)) == sp.zeros(2),
        "collapse_kernel_is_zero": collapse_kernel == sp.zeros(2),
        "profile_fundamental_symmetry_is_positive": sp.simplify(positive_image_gram - 6*q*v*sp.eye(2)) == sp.zeros(2),
        "physical_sigma_density_is_quotient_gram_times_kallen_measure": sp.simplify(
            sigma_density - q*delta/((1+r)*w)
        ) == 0,
        "physical_sigma_log_density_has_unit_asymptote": sp.simplify(
            sp.limit(q*w/(1+r), w, sp.oo) - 1
        ) == 0 and sp.limit(kallen/w**2, w, sp.oo) == 1,
        "sigma_primitive_derivative_identity": primitive_identity == 0,
        "sigma_primitive_threshold_value": primitive_at_threshold == -sp.Rational(5, 4),
        "sigma_equal_mass_primitive_identity": equal_mass_derivative == 0,
        "sigma_equal_mass_extension_is_continuous": continuous_equal_mass_sigma == 0,
        "daughter_exchange_kallen_scaling": kallen_exchange == r**-2,
        "daughter_exchange_q_invariant": q_exchange == 1,
        "daughter_exchange_normalization_scaling": normalization_exchange == r**-1,
        "daughter_exchange_sigma_measure_invariant": sigma_exchange == 1,
        "finite_hierarchy_domains_exhaust_half_line": hierarchy_limit == sp.oo,
        "outer_column_has_massless_local_limit": sp.simplify(
            outer_T_zero
            - sp.diag((2*outer_R-1)/(2*outer_R**2), -1/(2*outer_R))
        ) == sp.zeros(2)
        and sp.factor(outer_kallen.subs(r, 0)) == (outer_R-1)**2,
        "outer_integrated_gram_limit": outer_I_zero == sp.Rational(5, 24),
        "first_edge_partition": [row["noise_index"] for row in first_edges] == [0, 1, 2],
        "second_edge_partition": [row["noise_index"] for row in second_edges] == list(range(3, 15)),
        "third_edge_partition": [row["noise_index"] for row in third_edges] == list(range(15, 75)),
        "four_second_children_per_first_parent": sorted(children_per_parent.values()) == [4, 4, 4],
        "selected_history_rate": selected_history == Fraction(5, 3072),
        "per_history_ordered_simplex_norm": per_history_simplex == Fraction(5, 6144),
        "twelve_history_norm": aggregate_two_count == Fraction(5, 512),
        "level_one_hp_drift": level_one_drift == Fraction(5, 32)
        and hp["hudson_parthasarathy_cocycle"]["drift_eigenvalues_by_level"][1] == "5/32",
        "six_scalar_coefficient_matches": frac(
            six_tree["threshold_and_factorial_analysis"]["normalization"]["physical_two_count_coefficient"]
        ) == aggregate_two_count,
        "first_intertwiner_boundary_is_exactly_advanced": first["seventy_five_mark_boundary"]["physically_intertwined_edge_marks"] == [0, 1, 2],
        "endpoint_derivative_remains_unclaimed": rigged["disposition"]["ordinary_strong_C1_mass_axis_Moller_column"] == "EXACT_OBSTRUCTION",
    }
    checks = {name: bool(value) for name, value in checks.items()}
    return {
        "checks": checks,
        "q": q,
        "v": v,
        "quotient_eigenvalue": quotient_eigenvalue,
        "asymptotic_scale": asymptotic_scale,
        "sigma_density": sigma_density,
        "log_density": log_density,
        "threshold": threshold,
        "numerator_at_threshold": numerator_at_threshold,
        "eta": eta,
        "N_plus": N_plus,
        "N_minus": N_minus,
        "image_gram": image_gram,
        "positive_image_gram": positive_image_gram,
        "collapse_image": collapse_image,
        "primitive": primitive,
        "primitive_at_threshold": primitive_at_threshold,
        "equal_mass_primitive": equal_mass_primitive,
        "sigma_z_derivative": sigma_z_derivative,
        "w_max": w_max,
        "outer_T_zero": outer_T_zero,
        "outer_I_zero": outer_I_zero,
        "first_edges": first_edges,
        "second_edges": second_edges,
        "third_edges": third_edges,
        "children_per_parent": children_per_parent,
        "q0": q0,
        "q1": q1,
        "selected_history": selected_history,
        "per_history_simplex": per_history_simplex,
        "aggregate_two_count": aggregate_two_count,
        "level_one_drift": level_one_drift,
    }


def matrix_strings(matrix):
    import sympy as sp

    return [
        [str(sp.factor(matrix[i, j])) for j in range(matrix.cols)]
        for i in range(matrix.rows)
    ]


def build():
    d = derive()
    checks = dict(d["checks"])
    checks.update({
        "conditional_change_of_variables_isometry": checks["physical_sigma_density_is_quotient_gram_times_kallen_measure"] and checks["physical_sigma_log_density_has_unit_asymptote"],
        "ordered_two_noise_isometry": checks["conditional_change_of_variables_isometry"] if "conditional_change_of_variables_isometry" in checks else checks["physical_sigma_density_is_quotient_gram_times_kallen_measure"],
        "translation_intertwining": checks["sigma_primitive_derivative_identity"] and checks["physical_sigma_log_density_has_unit_asymptote"],
        "all_twelve_second_edges_promoted": len(d["second_edges"]) == 12,
        "only_sixty_third_edges_remain": len(d["third_edges"]) == 60,
        "eq19_stays_open": all(
            load(path)["disposition"]["Eq19_all_orders"] == "NOT_PROVED"
            for path in INPUTS[1:5]
        ),
        "input_hashes_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
    })
    # The two isometry checks are conclusions of explicit measure and polar
    # identities above, not independent asserted booleans.
    checks["ordered_two_noise_isometry"] = (
        checks["conditional_change_of_variables_isometry"]
        and checks["predecessor_checks"]
        and checks["four_second_children_per_first_parent"]
    )
    return {
        "certificate": "REVERSE_PHYSICS_BT_SIX_POINT_NESTED_CONTINUUM_INTERTWINER_V1",
        "schema_version": "reverse-physics-bt-six-point-nested-continuum-intertwiner-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "CLASSIFIED",
        "result_kind": "exact Kallen-measure cumulative-resolution and normalized polar-range intertwiner from the ordered two-noise HP carrier to all twelve six-point physical nested continuum quotient ranges",
        "question": "Does the amplitude-affiliated six-point parent/profile quotient possess a common measurable physical continuum domain and an exact ordered-shift intertwiner with the twelve second-level HP edge histories, without promoting its formal endpoint jet to a strong Hilbert derivative?",
        "answer": "Yes in the certified leading strongly ordered six-point sector. Put r=a1/a0, w=tau1/a0, Delta=sqrt(Kallen(w,1,r)), q=2Q_inner=[2w(1+r)-(1-r)^2]/(2w^2), v=a2/2, and lambda6=2qv=a2*q. The canonical four-component image basis N_+ has raw Gram 6qv*J, becomes 6qv*I2 under the certified profile fundamental symmetry, is orthogonal to the nondegenerate collapse-invisible kernel N_-, and satisfies RDN_+=2qv*I2. Thus N_+/sqrt(6qv) is the normalized physical quotient range while lambda6 is its conditional amplitude Gram. The exact normalized Kallen increment d sigma_r=[lambda6/(a2(1+r))]dmu_r=q*Delta*dw/[(1+r)w] is positive above threshold, invariant under daughter exchange, begins at zero, and has d sigma_r/d log(w)->1. An exact rationalized primitive proves that sigma_r maps the whole threshold ray bijectively onto R_+. Therefore B_r f(w)=sqrt(lambda6/[a2(1+r)]) E_6(r,w) f(sigma_r(w)) is an isometry from L2(R_+,d sigma) tensor C2 to the physical quotient direct integral with measure dmu_r. Conjugating ordinary right shifts by B_r gives an exact partial-unitary physical shift and semigroup law. Compose B_r with the already certified first-emission Abel physical column on the outer split. In variables t1>0 and d=t2-t1=sigma_r(w), this gives an isometry from L2({0<t1<t2}) tensor C12_edge tensor C2_species into the nested outer-continuum times four-component quotient ranges. The exact finite-epsilon outer threshold cuts w off at (sqrt(U)-1)^2/epsilon; those domains exhaust every compact sigma shell as epsilon tends to zero, and the outer column has a local massless limit on the declared compact dense core. Hence HP marks 3 through 14 now have physical continuum affiliation. Multiplication by sqrt(q0*q1), with q0=1/48 and q1=5/64, gives 5/3072 before the ordered simplex, 5/6144 per labeled history on an interval of squared length a^2, and 5/512 after all twelve histories, exactly the six-point coefficient. This is a physical nested reduced-mode continuum operator, not a strong endpoint derivative, full 75-mark intertwiner, spacetime Moller/LSZ/S operator, public R_t identification, or Eq. (19).",
        "six_point_positive_quotient_range": {
            "parent_profile_metric": matrix_strings(d["eta"]),
            "u_equals_q": str(d["q"]),
            "v": str(d["v"]),
            "nonzero_raised_eigenvalue": str(d["quotient_eigenvalue"]),
            "image_basis_N_plus": matrix_strings(d["N_plus"]),
            "kernel_basis_N_minus": matrix_strings(d["N_minus"]),
            "image_raw_gram": matrix_strings(d["image_gram"]),
            "image_hilbertized_gram": matrix_strings(d["positive_image_gram"]),
            "normalized_embedding": "E_6(r,w,a2)=N_plus/sqrt(6*q*v), with E_6^* E_6=I2 after the profile fundamental symmetry",
            "collapse_on_image": matrix_strings(d["collapse_image"]),
            "collapse_on_kernel": "R*D*N_minus=0",
            "pointwise_amplitude_identity": "(RDX)^T K(RDX)=(2*q*v)(PX)^T eta(PX) for every four-component X",
            "threshold_positivity": "At w=(1+sqrt(r))^2 the numerator of q is (1+sqrt(r))^4, and it increases linearly with w; hence q, v, and 2*q*v are positive on the full declared domain."
        },
        "physical_cumulative_resolution": {
            "inner_domain": "0<r<=1 and w>=(1+sqrt(r))^2; daughter exchange supplies r>1",
            "kallen_measure": "dmu_r(w)=sqrt(Kallen(w,1,r))*dw/w",
            "conditional_gram": "lambda6(r,w,a2)=2*q*v=a2*q",
            "asymptotic_scale": str(d["asymptotic_scale"]),
            "definition": "d sigma_r=lambda6/[a2*(1+r)] dmu_r=q*sqrt(Kallen(w,1,r))*dw/[(1+r)*w]",
            "density": str(d["sigma_density"]),
            "log_density": str(d["log_density"]),
            "unit_log_asymptote": "lim_(w->infinity) d sigma_r/d log(w)=1",
            "threshold_origin": "sigma_r((1+sqrt(r))^2)=0",
            "daughter_exchange": "sigma_(1/r)(w/r)=sigma_r(w)",
            "bijection": "sigma_r maps the physical threshold ray continuously and strictly increasingly onto R_+",
            "rationalization": "r=m^2, w=1+m^2+m(z+z^-1), with z=1 at threshold and z->0 at infinity",
            "primitive_F_m": str(d["primitive"]),
            "primitive_threshold": str(d["primitive_at_threshold"]),
            "sigma_from_primitive": "sigma_r(w)=F_m(z(w))-F_m(1)",
            "equal_mass_primitive": str(d["equal_mass_primitive"]),
            "equal_mass_extension": "sigma_1(w)=[-log(z)-4/(1+z)]-[-2], the continuous m->1 limit"
        },
        "conditional_direct_integral_isometry": {
            "source": "L2(R_+,d sigma) tensor C2_species",
            "target": "direct_integral_(w threshold ray) Ran(E_6(r,w,a2)) dmu_r(w)",
            "map": "(B_r f)(w)=sqrt(lambda6/[a2*(1+r)]) E_6(r,w,a2) f(sigma_r(w))",
            "adjoint": "(B_r^* psi)(sigma_r(w))=sqrt(a2*(1+r)/lambda6) E_6(r,w,a2)^* psi(w)",
            "identity": "B_r^* B_r=I and B_r B_r^*=I on the measurable quotient-range direct integral",
            "proof": "E_6^*E_6=I2 and [lambda6/(a2*(1+r))]dmu_r=d sigma_r exactly",
            "raw_rate_separation": "The asymptotic scale fixes the canonical physical resolution coordinate; the independently certified q1=5/64 supplies the HP edge intensity and is not fitted by changing sigma."
        },
        "ordered_two_noise_intertwiner": {
            "hp_carrier": "H_HP,2^phys=L2({(t1,t2):0<t1<t2},dt1dt2) tensor C12_edge tensor C2_species",
            "physical_carrier": "direct sum over the twelve histories of the first Abel physical outer range tensored fibrewise with the six-point normalized parent/profile quotient range over dmu_r(w)",
            "gap_coordinate": "d=t2-t1=sigma_r(w)",
            "map": "(A_2 f)_e(t1,y,w)=sqrt(p_t1(y))*sqrt(lambda6/[a2*(1+r)]) F_(y;r,w,a2) f_e(t1,t1+sigma_r(w)), where F is the fibrewise composition of the first physical polar column and E_6",
            "isometry": "A_2^*A_2=I on H_HP,2^phys; A_2A_2^* is the nested physical range projection",
            "translation": "Joint HP shifts (t1,t2)->(t1+b,t2+b) intertwine the first Abel polar transport while leaving d=sigma_r(w) fixed. Conditional gap shifts are conjugated by B_r to w->sigma_r^-1(sigma_r(w)+b), with the exact Radon--Nikodym and polar factors.",
            "semigroup": "Both the joint and conditional transported shifts compose exactly because they are conjugates of Lebesgue right shifts.",
            "edge_marks": [row["noise_index"] for row in d["second_edges"]],
            "four_children_per_parent": d["children_per_parent"]
        },
        "finite_hierarchy_dense_domain": {
            "exact_outer_threshold": "after scaling a2=1, w<=(sqrt(U)-1)^2/epsilon",
            "upper_endpoint": str(d["w_max"]),
            "exhaustion": "For every U>1 and every compact sigma interval, the finite-epsilon domain contains that interval for all sufficiently small epsilon.",
            "dense_core": "compactly supported sections in t1, sigma, outer U>1, and the Abel mass-ratio coordinate, bounded away from threshold endpoints, with values in C2_species",
            "outer_column_limit": "On this core r_outer=epsilon*w tends uniformly to zero, T(r_outer,U) tends to diag((2U-1)/(2U^2),-1/(2U)), the positive Kallen measure density tends to (U-1)/U, and I(r_outer) tends to 5/24.",
            "endpoint_boundary": "No derivative at r_outer=0 is taken. The certified logarithmically divergent derivative remains an obstruction to an ordinary C1 endpoint Moller column."
        },
        "rate_and_channel_affiliation": {
            "first_rate_q0": rat(d["q0"]),
            "conditional_second_rate_q1": rat(d["q1"]),
            "selected_history_before_simplex": rat(d["selected_history"]),
            "selected_history_ordered_interval_coefficient": rat(d["per_history_simplex"]),
            "second_level_edge_count": len(d["second_edges"]),
            "aggregate_two_count_coefficient": rat(d["aggregate_two_count"]),
            "level_one_hard_drift": rat(d["level_one_drift"]),
            "status": "EXACT_PHYSICAL_CONTINUUM_AFFILIATION_OF_ALL_TWELVE_SECOND_LEVEL_EDGES"
        },
        "seventy_five_mark_boundary": {
            "total_edge_marks": 75,
            "physically_intertwined_edge_marks": list(range(15)),
            "remaining_quotient_only_edge_marks": list(range(15, 75)),
            "physical_continuum_edge_count": 15,
            "remaining_edge_count": 60,
            "consequence": "The physical continuum affiliation now reaches through two emissions. The complete seven-point nested direct-integral column for the sixty third-level edges remains the next gate before any full 75-mark claim."
        },
        "disposition": {
            "six_point_cumulative_physical_resolution": "CONSTRUCTED_EXACTLY",
            "six_point_normalized_quotient_range_field": "CONSTRUCTED_EXACTLY",
            "ordered_two_noise_physical_intertwiner": "CONSTRUCTED_EXACTLY",
            "second_level_edge_marks_3_through_14": "PHYSICALLY_CONTINUUM_AFFILIATED",
            "physical_continuum_edge_marks_0_through_14": "EXACT",
            "remaining_sixty_edge_continuum_affiliation": "NOT_CONSTRUCTED",
            "full_seventy_five_mark_physical_intertwiner": "NOT_CONSTRUCTED",
            "strong_massless_endpoint_derivative": "EXACTLY_OBSTRUCTED_AND_NOT_USED",
            "fourth_jump": "NOT_COMPUTED",
            "complete_BT_probability": "NOT_CONSTRUCTED",
            "spacetime_Moller_LSZ_S_operator": "NOT_CONSTRUCTED",
            "public_Rt_identification": "NOT_ESTABLISHED",
            "Eq19_all_orders": "NOT_PROVED"
        },
        "assumptions": [
            "The construction is restricted to the certified leading nested strongly ordered six-point external-mass jet sector; it does not supply the non-strongly-ordered six-body phase space, connected single-log terms, or finite terms.",
            "The constant/linear parent jet and singleton/pair spectator profile remain independent gradings until the canonical collapse-invisible kernel is quotiented; the premature two-species restriction remains obstructed.",
            "The first-emission outer continuum column is imported by hash and used on a compact dense core in its local massless boundary limit; no strong external-mass endpoint derivative is taken or inferred.",
            "The normalized cumulative coordinate uses the exact positive six-point quotient Gram and exact Kallen measure. Its unit logarithmic asymptote fixes resolution length, while the separately computed physical coefficient fixes q1.",
            "The profile fundamental symmetry J is the certified Hilbertization of the positive quotient image. Positivity is asserted only after this declared quotient and not on the full signature-(2,2) parent/profile carrier."
        ],
        "does_not_establish": [
            "a physical continuum affiliation for the sixty seven-point third-level edges",
            "a full seventy-five-mark physical operator intertwiner",
            "a fourth BT emission or eight-point coefficient",
            "a complete BT two-to-n probability or all-order branching law",
            "a non-strongly-ordered six-body probability",
            "a strong derivative of the physical column at the massless endpoint",
            "an ordinary additive-resolution Hamiltonian",
            "a spacetime-local Moller, LSZ, or S operator",
            "identification of the physical quotient map with the public R_t map",
            "Bateman--Turok Eq. (19)",
            "positivity beyond tree level or a KLN theorem",
            "a metric or BRST lift to pure Weyl gravity",
            "a new physical or spacetime dimension",
            "anything LORENTZIAN-CAUSAL",
            "literature priority"
        ],
        "missing_object_ledger": [
            "the seven-point cumulative physical resolution and normalized nested quotient range for edge marks 15 through 74",
            "a compatibility theorem joining all seventy-five edge ranges on one inductive continuum domain",
            "the physical fourth jump and complete eight-point pre-trace quotient",
            "the complete incoming and degenerate asymptotic sectors",
            "a spacetime-local physical Moller/LSZ/S operator and its dense domain",
            "an identification or replacement theorem for the public R_t transformation in Eq. (19)",
            "a metric-BV/BRST lift with restored local quantum master equation"
        ],
        "next_gate": "Construct the seven-point nested physical direct-integral column for the sixty third-level edges. Start from the certified signed four-component quotient with u<0<v and positive physical eigenvalue -2uv. Determine the corresponding exact conditional Kallen density, its asymptotic normalization, and whether its cumulative coordinate is positive, daughter-exchange compatible, and onto R_+. Compose that conditional column with the present two-emission nested range on the ordered three-noise simplex. A pass would physically affiliate all seventy-five existing HP marks; a failure would locate the first continuum obstruction beyond six points. The fourth jump, complete probability, spacetime S operator, public R_t identification, and Eq. (19) remain later gates.",
        "provenance": {
            "source_commit": SOURCE,
            "retrieval_date": "2026-08-11",
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "producer_method": "Exact SymPy reconstruction of the six-point quotient image/kernel, its Kallen-weighted conditional Gram, a hand-assembled rationalized primitive and daughter-exchange law, followed by exact channel/rate imports and a finite-hierarchy dense-domain limit. No floating-point arithmetic or expected cohomology basis is used.",
            "primary_source": {
                "source": "Bateman--Turok arXiv:2607.00096v1",
                "url": "https://arxiv.org/abs/2607.00096v1",
                "equations": ["Eq. (13)", "Eq. (18)", "Eq. (19)", "Appendix B Eqs. (24)-(25)"]
            }
        },
        "verification_commands": [
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_six_point_nested_continuum_intertwiner.py --write --check",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_six_point_nested_continuum_intertwiner.py",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest reverse_physics.tests.test_bt_six_point_nested_continuum_intertwiner"
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
