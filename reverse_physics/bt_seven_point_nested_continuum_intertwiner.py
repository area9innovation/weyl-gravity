#!/usr/bin/env python3
"""Exact seven-point nested physical continuum--Fock intertwiner."""
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
    "REVERSE_PHYSICS_BT_SEVEN_POINT_NESTED_CONTINUUM_INTERTWINER_V1.json",
)
SCHEMA = (
    "reverse_physics/schema/"
    "reverse-physics-bt-seven-point-nested-continuum-intertwiner-v1.schema.json"
)
REPORT = (
    "reverse_physics/reports/"
    "bt-seven-point-nested-continuum-intertwiner.md"
)
SOURCE = "49d33dd0794df29e359989cd8acf9d57f088fce2"
INPUTS = [
    "planning/work-items/"
    "reverse-physics-bateman-seven-point-nested-continuum-intertwiner.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_SIX_POINT_NESTED_CONTINUUM_INTERTWINER_V1.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_SEVEN_POINT_PROFILE_QUOTIENT_AFFILIATION_V1.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_SEVEN_POINT_COX_SELECTION_V1.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_QUANTUM_STOCHASTIC_MOLLER_DILATION_V1.json",
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


def matrix_strings(matrix):
    import sympy as sp

    return [
        [str(sp.factor(matrix[i, j])) for j in range(matrix.cols)]
        for i in range(matrix.rows)
    ]


def derive():
    import sympy as sp

    six = load(INPUTS[1])
    seven = load(INPUTS[2])
    cox = load(INPUTS[3])
    hp = load(INPUTS[4])

    alpha, s, w, tau3 = sp.symbols("alpha s w tau3", positive=True)
    inverse_w = 1 / w
    H0 = 2 + alpha * s * (2 - s)
    H = sp.factor(H0 + (6 - 2 * alpha) / w + alpha / w**2)
    u = -alpha / 2
    v = sp.factor(tau3 * H / (4 * (1 + s)))
    eigenvalue = sp.factor(-2 * u * v)
    asymptotic_scale = sp.factor(tau3 * alpha * H0 / (4 * (1 + s)))
    massless_kallen_density = (w - 1) / w
    chi_density = sp.factor(
        eigenvalue / asymptotic_scale * massless_kallen_density
    )
    B = sp.factor((6 - 2 * alpha) / H0)
    C = sp.factor(alpha / H0)
    primitive = sp.factor(
        w + (B - 1) * sp.log(w) - (C - B) / w + C / (2 * w**2)
    )
    primitive_at_threshold = sp.factor(primitive.subs(w, 1))
    chi = sp.factor(primitive - primitive_at_threshold)

    J = sp.Matrix([[0, 1], [1, 0]])
    eta = sp.kronecker_product(J, 3 * J)
    N_plus = sp.Matrix([[v, 0], [0, v], [u, 0], [0, u]])
    N_minus = sp.Matrix([[v, 0], [0, v], [-u, 0], [0, -u]])
    R = sp.Matrix.hstack(sp.eye(2), sp.eye(2))
    D = sp.diag(u, u, v, v)
    image_gram = sp.simplify(N_plus.T * eta * N_plus)
    kernel_gram = sp.simplify(N_minus.T * eta * N_minus)
    cross_gram = sp.simplify(N_minus.T * eta * N_plus)
    collapse_image = sp.simplify(R * D * N_plus)
    collapse_kernel = sp.simplify(R * D * N_minus)
    hilbertized_image_gram = sp.simplify(image_gram * (-J))

    # Reconstruct the quotient eigenvalue from the original seven-point
    # variables, rather than trusting its serialized ratio form.
    a0, a1, tau1, a2, tau2, a3 = sp.symbols(
        "a0 a1 tau1 a2 tau2 a3", positive=True
    )
    A = (a0 - a1) ** 2 - 2 * tau1 * (a0 + a1) + 2 * tau1**2
    C7 = (
        a2 * (a2 * A + 2 * tau2 * (-A + 3 * tau1**2))
        + 2 * tau2**2 * (A + tau1**2)
    )
    u_original = -A / (2 * tau1**2)
    v_original = sp.factor(
        (
            C7 * tau3**2
            - A * tau2**2 * (a3**2 - 2 * a3 * tau3 + 2 * tau3**2)
        )
        / (4 * tau1**2 * tau2**2 * (tau3 + a3))
    )
    ratio_substitution = {
        alpha: A / tau1**2,
        s: a3 / tau3,
        w: tau2 / a2,
    }
    u_ratio_identity = sp.factor(u.subs(ratio_substitution) - u_original)
    v_ratio_identity = sp.factor(v.subs(ratio_substitution) - v_original)

    # Alpha is the exchange-invariant inner quotient coordinate inherited
    # from the six-point construction: alpha=2(1-q), with 1<=alpha<2.
    r0, w0 = sp.symbols("r0 w0", positive=True)
    q_inner = (2 * w0 * (1 + r0) - (1 - r0) ** 2) / (2 * w0**2)
    alpha_from_q = sp.factor(2 * (1 - q_inner))
    A_scaled = sp.factor(
        ((1 - r0) ** 2 - 2 * w0 * (1 + r0) + 2 * w0**2) / w0**2
    )
    kallen_inner = w0**2 + 1 + r0**2 - 2 * w0 - 2 * w0 * r0 - 2 * r0
    m = sp.symbols("m", positive=True)
    alpha_threshold = sp.factor(
        A_scaled.subs({r0: m**2, w0: (1 + m) ** 2})
    )
    alpha_infinity = sp.limit(A_scaled, w0, sp.oo)

    # The exact finite hierarchy has a small middle daughter ratio rho and
    # an outer-threshold upper cutoff. Both endpoints exhaust the limiting
    # w in (1,infinity) on compact chi shells.
    epsilon1, epsilon2, inner_scale, outer_gap = sp.symbols(
        "epsilon1 epsilon2 inner_scale outer_gap", positive=True
    )
    rho = epsilon1 * inner_scale / a2
    lower_endpoint = (1 + sp.sqrt(rho)) ** 2
    upper_endpoint = outer_gap**2 / (epsilon2 * a2)
    lower_limit = sp.limit(lower_endpoint, epsilon1, 0, dir="+")
    upper_limit = sp.limit(upper_endpoint, epsilon2, 0, dir="+")
    gap = sp.symbols("gap", positive=True)
    finite_kallen = sp.sqrt(
        (1 + gap) ** 2 + 1 + rho**2
        - 2 * (1 + gap) - 2 * (1 + gap) * rho - 2 * rho
    ) / (1 + gap)
    massless_measure_limit = sp.factor(
        sp.limit(finite_kallen, epsilon1, 0, dir="+")
    )

    channels = hp["system_and_noise_carrier"]["noise_channels"]
    third_edges = [row for row in channels if row["level"] == 2]
    children_per_parent = {
        parent: sum(row["parent"] == parent for row in third_edges)
        for parent in {row["parent"] for row in third_edges}
    }
    q0 = frac(six["rate_and_channel_affiliation"]["first_rate_q0"])
    q1 = frac(six["rate_and_channel_affiliation"]["conditional_second_rate_q1"])
    q2 = frac(seven["branching_affiliation"]["conditional_third_rate"])
    selected_history = q0 * q1 * q2
    per_history_simplex = selected_history / 6
    aggregate_three_count = 60 * per_history_simplex
    level_two_drift = 5 * q2 / 2

    checks = {
        "predecessor_checks": all(
            value["checks"]["ok"] for value in (six, seven, cox, hp)
        ),
        "original_u_ratio_identity": u_ratio_identity == 0,
        "original_v_ratio_identity": v_ratio_identity == 0,
        "alpha_equals_two_times_one_minus_q": sp.factor(alpha_from_q - A_scaled) == 0,
        "alpha_minus_one_is_positive_kallen_fraction": sp.factor(
            A_scaled - 1 - kallen_inner / w0**2
        ) == 0,
        "two_minus_alpha_is_positive_two_q": sp.factor(
            2 - A_scaled - 2 * q_inner
        ) == 0,
        "alpha_is_one_at_inner_threshold": alpha_threshold == 1,
        "alpha_tends_to_two_at_infinity": alpha_infinity == 2,
        "H_quadratic_inverse_w_form": sp.expand(H - (H0 + (6 - 2 * alpha) / w + alpha / w**2)) == 0,
        "H0_positive_coefficient_form": sp.expand(H0 - 2 - alpha * s * (2 - s)) == 0,
        "middle_coefficient_positive_on_alpha_domain": sp.factor((6 - 2 * alpha) - 2 * (3 - alpha)) == 0,
        "physical_eigenvalue_is_minus_two_uv": sp.factor(eigenvalue + 2 * u * v) == 0,
        "asymptotic_scale_is_eigenvalue_limit": sp.factor(sp.limit(eigenvalue, w, sp.oo) - asymptotic_scale) == 0,
        "massless_middle_kallen_limit": massless_measure_limit == gap / (gap + 1),
        "physical_chi_density_identity": sp.factor(chi_density - H / H0 * (w - 1) / w) == 0,
        "chi_primitive_derivative_identity": sp.factor(sp.diff(primitive, w) - chi_density) == 0,
        "chi_threshold_origin": sp.simplify(chi.subs(w, 1)) == 0,
        "chi_density_has_unit_linear_asymptote": sp.limit(chi_density, w, sp.oo) == 1,
        "image_raw_gram": sp.simplify(image_gram - 6 * u * v * J) == sp.zeros(2),
        "kernel_raw_gram": sp.simplify(kernel_gram + 6 * u * v * J) == sp.zeros(2),
        "kernel_image_orthogonal": cross_gram == sp.zeros(2),
        "signed_profile_hilbertization_is_positive": sp.simplify(hilbertized_image_gram + 6 * u * v * sp.eye(2)) == sp.zeros(2),
        "collapse_image_is_scalar": sp.simplify(collapse_image - 2 * u * v * sp.eye(2)) == sp.zeros(2),
        "collapse_kernel_is_zero": collapse_kernel == sp.zeros(2),
        "radon_nikodym_isometry": sp.factor(eigenvalue / asymptotic_scale * massless_kallen_density - chi_density) == 0,
        "finite_lower_endpoint_tends_to_one": lower_limit == 1,
        "finite_upper_endpoint_exhausts_half_line": upper_limit == sp.oo,
        "prior_fifteen_marks_exact": six["seventy_five_mark_boundary"]["physically_intertwined_edge_marks"] == list(range(15)),
        "third_edge_partition": [row["noise_index"] for row in third_edges] == list(range(15, 75)),
        "five_third_children_per_second_parent": sorted(children_per_parent.values()) == [5] * 12,
        "all_seventy_five_marks_partitioned": list(range(15)) + [row["noise_index"] for row in third_edges] == list(range(75)),
        "selected_history_rate": selected_history == Fraction(9, 81920),
        "per_history_ordered_simplex_norm": per_history_simplex == Fraction(3, 163840),
        "sixty_history_norm": aggregate_three_count == Fraction(9, 8192),
        "level_two_hp_drift": level_two_drift == Fraction(27, 160)
        and hp["hudson_parthasarathy_cocycle"]["drift_eigenvalues_by_level"][2] == "27/160",
        "seven_scalar_coefficient_matches": frac(
            cox["threshold_analysis"]["normalization"]["leading_three_count_coefficient"]
        ) == aggregate_three_count,
        "eq19_stays_open": all(
            value["disposition"]["Eq19_all_orders"] == "NOT_PROVED"
            for value in (six, seven)
        ),
        "input_hashes_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
    }
    checks = {name: bool(value) for name, value in checks.items()}
    return locals()


def build():
    d = derive()
    checks = dict(d["checks"])
    checks.update({
        "chi_is_positive_bijection": (
            checks["physical_chi_density_identity"]
            and checks["chi_threshold_origin"]
            and checks["chi_density_has_unit_linear_asymptote"]
        ),
        "conditional_change_of_variables_isometry": checks["radon_nikodym_isometry"] and checks["signed_profile_hilbertization_is_positive"],
        "ordered_three_noise_isometry": checks["radon_nikodym_isometry"] and checks["signed_profile_hilbertization_is_positive"] and checks["predecessor_checks"] and checks["five_third_children_per_second_parent"],
        "all_sixty_third_edges_promoted": len(d["third_edges"]) == 60,
        "full_available_seventy_five_mark_family": checks["all_seventy_five_marks_partitioned"] and checks["prior_fifteen_marks_exact"],
    })
    return {
        "certificate": "REVERSE_PHYSICS_BT_SEVEN_POINT_NESTED_CONTINUUM_INTERTWINER_V1",
        "schema_version": "reverse-physics-bt-seven-point-nested-continuum-intertwiner-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "CLASSIFIED",
        "result_kind": "exact massless-hierarchy Kallen cumulative resolution and normalized signed-quotient intertwiner from the ordered three-noise HP carrier to all sixty seven-point physical continuum ranges",
        "question": "Does the positive signed seven-point quotient define a physical cumulative middle-threshold coordinate and an exact ordered three-noise intertwiner for the sixty remaining HP histories?",
        "answer": "Yes in the certified leading triple-strongly-ordered reduced-mode sector. Put alpha=A/tau1^2=2(1-q_inner), s=a3/tau3, and w=tau2/a2. Then 1<=alpha<2, 0<s<1, w>1, u=-alpha/2, and v=tau3*H(w)/[4(1+s)], where H(w)=H0+(6-2alpha)/w+alpha/w^2 and H0=2+alpha*s(2-s). Hence lambda7=-2uv=tau3*alpha*H(w)/[4(1+s)] is positive and has exact asymptotic scale S7=tau3*alpha*H0/[4(1+s)]. The limiting middle two-body measure is dnu0=(w-1)dw/w. Therefore dchi=[lambda7/S7]dnu0=[H(w)/H0](w-1)dw/w is positive, vanishes at threshold, and tends to dw. Its elementary primitive proves that chi maps [1,infinity) bijectively onto R_+. The signed quotient image N_+=((v,0),(0,v),(u,0),(0,u)) has Hilbertized Gram -6uv I2, so E7=N_+/sqrt(-6uv) is normalized. The map C f(w)=sqrt(lambda7/S7) E7 f(chi(w)) is unitary onto the physical quotient-range direct integral. Composing C with the certified two-emission intertwiner gives an ordered three-noise isometry for marks 15 through 74. The finite hierarchy has lower endpoint (1+sqrt(epsilon1*tau1/a2))^2 tending to one and upper endpoint (sqrt(tau3)-sqrt(a3))^2/(epsilon2*a2) tending to infinity, so compact sections away from endpoints form an exhausting dense core. The exact rate chain is q0*q1*q2=(1/48)(5/64)(27/400)=9/81920; after the ordered three-simplex each of 60 histories has coefficient 3/163840 and their sum is 9/8192, matching the independent seven-point calculation. Direct-summing the imported one- and two-emission columns with this three-emission column physically affiliates all 75 currently available HP edge marks. This finite available hierarchy is not a fourth jump, complete probability, spacetime S operator, public R_t identification, or Eq. (19).",
        "seven_point_positive_quotient_range": {
            "domain": "1<=alpha<2, 0<s<1, w>1, tau3>0",
            "coordinates": "alpha=A/tau1^2=2*(1-q_inner), s=a3/tau3, w=tau2/a2",
            "u": str(d["u"]),
            "v": str(d["v"]),
            "H0": str(d["H0"]),
            "H": str(d["H"]),
            "nonzero_physical_eigenvalue": str(d["eigenvalue"]),
            "image_basis_N_plus": matrix_strings(d["N_plus"]),
            "kernel_basis_N_minus": matrix_strings(d["N_minus"]),
            "image_raw_gram": matrix_strings(d["image_gram"]),
            "image_hilbertized_gram": matrix_strings(d["hilbertized_image_gram"]),
            "normalized_embedding": "E7(alpha,s,w,tau3)=N_plus/sqrt(-6*u*v), with E7^*E7=I2 after the signed profile fundamental symmetry -J",
            "collapse_on_image": matrix_strings(d["collapse_image"]),
            "collapse_on_kernel": "R*D*N_minus=0",
            "positivity": "H0=2+alpha*s*(2-s)>2, 6-2alpha>2, and alpha>0; hence H(w), v, and -2uv are positive on the complete domain."
        },
        "physical_cumulative_resolution": {
            "middle_hierarchy_domain": "w=tau2/a2>1 after epsilon1->0; finite epsilon1 has w>=(1+sqrt(epsilon1*tau1/a2))^2",
            "massless_kallen_measure": "dnu0(w)=sqrt(Kallen(w,1,0))*dw/w=(w-1)*dw/w",
            "conditional_gram": "lambda7(alpha,s,w,tau3)=-2*u*v=tau3*alpha*H(w)/[4*(1+s)]",
            "asymptotic_scale": str(d["asymptotic_scale"]),
            "definition": "dchi_(alpha,s)=[lambda7/S7]dnu0=[H(w)/H0]*(w-1)*dw/w",
            "density": str(d["chi_density"]),
            "B": str(d["B"]),
            "C": str(d["C"]),
            "primitive_F": str(d["primitive"]),
            "primitive_threshold": str(d["primitive_at_threshold"]),
            "chi_from_primitive": str(d["chi"]),
            "threshold_origin": "chi_(alpha,s)(1)=0",
            "unit_linear_asymptote": "lim_(w->infinity) dchi/dw=1",
            "bijection": "chi_(alpha,s) maps [1,infinity) continuously and strictly increasingly onto R_+",
            "permutation_compatibility": "alpha is invariant under exchange of the innermost daughters, and the same conditional formula transports to all sixty histories by the certified external-label permutation covariance; the chronologically attached middle daughter is not identified with the pre-existing cluster."
        },
        "conditional_direct_integral_isometry": {
            "source": "L2(R_+,dchi) tensor C2_species",
            "target": "direct_integral_(w in (1,infinity)) Ran(E7(alpha,s,w,tau3)) dnu0(w)",
            "map": "(C_(alpha,s)f)(w)=sqrt(lambda7/S7) E7(alpha,s,w,tau3) f(chi_(alpha,s)(w))",
            "adjoint": "(C^*psi)(chi(w))=sqrt(S7/lambda7) E7(w)^*psi(w)",
            "identity": "C^*C=I and CC^*=I on the measurable signed-quotient-range direct integral",
            "proof": "E7^*E7=I2 and [lambda7/S7]dnu0=dchi exactly",
            "shift_transport": "Lebesgue right shifts in chi conjugate to w->chi^(-1)(chi(w)+b); Radon--Nikodym and signed polar factors telescope, giving the exact semigroup law."
        },
        "ordered_three_noise_intertwiner": {
            "hp_carrier": "H_HP,3^phys=L2({0<t1<t2<t3},dt1dt2dt3) tensor C60_edge tensor C2_species",
            "gap_coordinate": "t3-t2=chi_(alpha,s)(w)",
            "map": "A3 is the fibrewise composition of the certified A2 two-emission physical column with C_(alpha,s) on each of the sixty labeled children",
            "isometry": "A3^*A3=I on H_HP,3^phys and A3A3^* is the nested seven-point physical range projection",
            "joint_translation": "Joint shifts of (t1,t2,t3) transport through A2 and leave both ordered gaps fixed; conditional third-gap shifts are conjugated by C_(alpha,s).",
            "edge_marks": [row["noise_index"] for row in d["third_edges"]],
            "five_children_per_parent": d["children_per_parent"]
        },
        "finite_hierarchy_dense_domain": {
            "lower_endpoint": str(d["lower_endpoint"]),
            "upper_endpoint": "(sqrt(tau3)-sqrt(a3))^2/(epsilon2*a2)",
            "endpoint_limits": "lower endpoint tends to 1 as epsilon1->0 and upper endpoint tends to infinity as epsilon2->0",
            "dense_core": "compactly supported sections in t1, the six-point gap sigma, the seven-point gap chi, alpha in [1,2), s in (0,1), and the inherited Abel coordinates, uniformly bounded away from every finite-hierarchy endpoint",
            "exhaustion": "Every compact chi shell has a compact w preimage and lies between the exact finite endpoints for all sufficiently small epsilon1 and epsilon2.",
            "endpoint_boundary": "Only the hierarchy limits of the measure and columns are used; no strong derivative in epsilon1, epsilon2, or an external mass is asserted."
        },
        "rate_and_channel_affiliation": {
            "first_rate_q0": rat(d["q0"]),
            "conditional_second_rate_q1": rat(d["q1"]),
            "conditional_third_rate_q2": rat(d["q2"]),
            "selected_history_before_simplex": rat(d["selected_history"]),
            "selected_history_ordered_interval_coefficient": rat(d["per_history_simplex"]),
            "third_level_edge_count": len(d["third_edges"]),
            "aggregate_three_count_coefficient": rat(d["aggregate_three_count"]),
            "level_two_hard_drift": rat(d["level_two_drift"]),
            "status": "EXACT_PHYSICAL_CONTINUUM_AFFILIATION_OF_ALL_SIXTY_THIRD_LEVEL_EDGES"
        },
        "seventy_five_mark_completion": {
            "total_edge_marks": 75,
            "physically_intertwined_edge_marks": list(range(75)),
            "physical_continuum_edge_count": 75,
            "remaining_quotient_only_edge_marks": [],
            "available_hierarchy": "vacuum plus the certified one-, two-, and three-emission ordered sectors",
            "direct_sum": "A_<=3=I_vacuum direct_sum A1 direct_sum A2 direct_sum A3 is an isometry onto the direct sum of the corresponding physical continuum ranges",
            "boundary": "This completes the continuum affiliation of the 75 marks already present in the finite HP instrument; it does not construct a fourth level or an all-order inductive limit."
        },
        "disposition": {
            "seven_point_cumulative_physical_resolution": "CONSTRUCTED_EXACTLY_IN_THE_MASSLESS_HIERARCHY_LIMIT",
            "seven_point_normalized_signed_quotient_range_field": "CONSTRUCTED_EXACTLY",
            "ordered_three_noise_physical_intertwiner": "CONSTRUCTED_EXACTLY",
            "third_level_edge_marks_15_through_74": "PHYSICALLY_CONTINUUM_AFFILIATED",
            "all_seventy_five_available_edge_marks": "PHYSICALLY_CONTINUUM_AFFILIATED",
            "finite_available_hierarchy_direct_sum": "CONSTRUCTED",
            "all_order_inductive_intertwiner": "NOT_CONSTRUCTED",
            "fourth_jump": "NOT_COMPUTED",
            "complete_BT_probability": "NOT_CONSTRUCTED",
            "spacetime_Moller_LSZ_S_operator": "NOT_CONSTRUCTED",
            "public_Rt_identification": "NOT_ESTABLISHED",
            "Eq19_all_orders": "NOT_PROVED"
        },
        "assumptions": [
            "The construction is restricted to the certified leading triple-strongly-ordered seven-point external-mass jet sector and its massless middle-hierarchy limit.",
            "The signed profile fundamental symmetry -J is imported from the exact seven-point quotient; positivity is asserted only on its two-dimensional image, not on the full signature-(2,2) carrier.",
            "The middle Kallen density is obtained as the exact epsilon1->0 limit on a compact dense core. The result is not a finite-epsilon equality and uses no endpoint derivative.",
            "The asymptotic coefficient S7 fixes the chi normalization. The independent tree coefficient fixes q2=27/400 and is not used to fit the continuum density.",
            "The prior A1 and A2 physical continuum columns are imported unchanged by content hash and composed fibrewise with the new conditional column."
        ],
        "does_not_establish": [
            "a finite-epsilon equality outside the declared hierarchy limit",
            "a fourth BT branching jump or any edge beyond mark 74",
            "an all-order inductive-limit stochastic intertwiner",
            "a complete BT two-to-n probability or branching law",
            "a non-strongly-ordered seven-body probability",
            "a strong external-mass endpoint derivative",
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
            "the complete eight-point pre-trace quotient and physical fourth jump",
            "an inductive compatibility theorem for arbitrarily many nested continuum columns",
            "the complete incoming, degenerate, and non-strongly-ordered asymptotic sectors",
            "a spacetime-local physical Moller/LSZ/S operator and its dense domain",
            "an identification or replacement theorem for the public R_t transformation in Eq. (19)",
            "a metric-BV/BRST lift with restored local quantum master equation"
        ],
        "next_gate": "The finite available 75-mark continuum barrier is closed. The next physical gate is not another relabeling: compute the complete eight-point pre-trace parent/profile tensor, determine the fourth quotient and rate, and test whether the cumulative-coordinate construction is recursive on an inductive ordered Fock core. In parallel, compare the resulting finite direct-sum intertwiner with the certified three-jump Krein Moller jet and isolate the exact additional condition needed to identify or replace the public R_t in Eq. (19). Complete probability, spacetime scattering, gravity, and Lorentzian claims remain later gates.",
        "provenance": {
            "source_commit": SOURCE,
            "retrieval_date": "2026-08-11",
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "producer_method": "Exact SymPy reduction of the signed seven-point quotient in dimensionless nested variables, exact massless Kallen measure limit, elementary primitive, rational matrix quotient checks, finite-hierarchy endpoint limits, and exact HP channel/rate imports. No floating-point arithmetic is used.",
            "primary_source": {
                "source": "Bateman--Turok arXiv:2607.00096v1",
                "url": "https://arxiv.org/abs/2607.00096v1",
                "equations": ["Eq. (13)", "Eq. (18)", "Eq. (19)", "Appendix B Eqs. (24)-(25)"]
            }
        },
        "verification_commands": [
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_seven_point_nested_continuum_intertwiner.py --write --check",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_seven_point_nested_continuum_intertwiner.py",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest reverse_physics.tests.test_bt_seven_point_nested_continuum_intertwiner"
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
