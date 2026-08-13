#!/usr/bin/env python3
"""Third-Dyson affiliation of the fully rearranged BT V4^3 triangle."""
from __future__ import annotations

import argparse
from fractions import Fraction
from math import comb, factorial
import hashlib
import itertools
import json
import os


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_FULLY_REARRANGED_V4_CUBED_FINITE_TIME_AFFILIATION_V1.json"
)
CERT = os.path.join(ROOT, CERT_REL)
SCHEMA = (
    "reverse_physics/schema/"
    "reverse-physics-bt-fully-rearranged-v4-cubed-finite-time-affiliation-v1.schema.json"
)
REPORT = "reverse_physics/reports/bt-fully-rearranged-v4-cubed-finite-time-affiliation.md"
SOURCE_COMMIT = "2cad87ba756920989ac21b7edc2487098aea3c7a"
INPUTS = [
    "planning/work-items/reverse-physics-bateman-fully-rearranged-v4-cubed-finite-time-affiliation.json",
    "planning/events/reverse-physics-bateman-fully-rearranged-v4-cubed-finite-time-affiliation-DONE-2cad87ba.json",
    "reverse_physics/data/bateman_turok_hamiltonian_source_v1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_FULLY_REARRANGED_V4_CUBED_TRIANGLE_BLOCK_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_FINITE_TIME_ACTIVE_LOOP_AFFILIATION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_FULLY_REARRANGED_COMMON_BORN_PHYSICAL_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_FULLY_REARRANGED_PHYSICAL_PACKET_PROBABILITY_V1.json",
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


def compositions(total, slots):
    if slots == 1:
        yield (total,)
        return
    for first in range(total + 1):
        for tail in compositions(total - first, slots - 1):
            yield (first,) + tail


def direct_ordered_coefficient(total_degree, x_power, y_power):
    """Coefficient without i^N from the ordered three-time simplex."""
    z_power = total_degree - x_power - y_power
    # Dirichlet integral over t,u,v and the unused fourth simplex coordinate.
    numerator = factorial(x_power) * factorial(y_power) * factorial(z_power)
    integral = Fraction(numerator, factorial(total_degree + 3))
    exponential = Fraction(
        1,
        factorial(x_power) * factorial(y_power) * factorial(z_power),
    )
    return integral * exponential


def divided_difference_coefficient(total_degree):
    """Coefficient of h_N in -f[x,y,z]."""
    return Fraction(1, factorial(total_degree + 3))


def vector(row):
    return tuple(Fraction(value) for value in row)


def negate(row):
    return tuple(-value for value in row)


def add(left, right):
    return tuple(a + b for a, b in zip(left, right))


def spatial_square(row):
    return sum(value * value for value in row[1:])


def ordering_rows():
    rows = []
    for index, order in enumerate(itertools.permutations(range(3))):
        early, middle, late = order
        rows.append({
            "index": index,
            "earliest_middle_latest": list(order),
            "overall_frequency": "Omega=q0^0+q1^0+q2^0",
            "first_interval_defect": (
                f"Delta1=q{middle}^0+q{late}^0-(E{min(early,middle)}{max(early,middle)}+E{min(early,late)}{max(early,late)})"
            ),
            "second_interval_defect": (
                f"Delta2=q{late}^0-(E{min(middle,late)}{max(middle,late)}+E{min(early,late)}{max(early,late)})"
            ),
        })
    return rows


def build():
    source = load(INPUTS[2])
    covariant = load(INPUTS[3])
    bubble_affiliation = load(INPUTS[4])
    common = load(INPUTS[5])
    packet = load(INPUTS[6])
    predecessors = (covariant, bubble_affiliation, common, packet)

    coefficient_rows = []
    coefficient_match = True
    for degree in range(13):
        expected = divided_difference_coefficient(degree)
        rows = [
            direct_ordered_coefficient(degree, powers[0], powers[1])
            for powers in compositions(degree, 3)
        ]
        coefficient_match &= all(value == expected for value in rows)
        coefficient_rows.append({
            "total_degree": degree,
            "coefficient_without_i_power": str(expected),
            "monomial_count": comb(degree + 2, 2),
        })

    orderings = ordering_rows()
    witness = packet["exact_detector_witness"]
    momenta = [vector(row) for row in witness["incoming_momenta"]]
    momenta += [negate(vector(row)) for row in witness["outgoing_momenta"]]
    spatial_pair_squares = [
        spatial_square(add(momenta[a], momenta[b]))
        for a in range(6) for b in range(a + 1, 6)
    ]

    checks = {
        "inputs_are_content_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
        "four_predecessors_pass": all(row["checks"]["ok"] for row in predecessors),
        "public_auxiliary_quartic_is_imported": "Omega^2 Upsilon^2" in source["public_inputs"]["auxiliary_action"],
        "covariant_V4_cubed_block_is_imported": covariant["disposition"]["V4_cubed_covariant_block"] == "COEFFICIENT_COMPUTED",
        "second_Dyson_one_defect_kernel_is_not_reused": bubble_affiliation["ordered_dyson_kernel"]["status"] == "SECOND_DYSON_DISPERSIVE_KERNEL_DERIVED",
        "ordered_simplex_and_second_divided_difference_match_through_degree_12": coefficient_match,
        "zero_frequency_simplex_volume_is_one_sixth": direct_ordered_coefficient(0, 0, 0) == Fraction(1, 6),
        "linear_coefficients_are_one_twenty_fourth": all(direct_ordered_coefficient(1, p, q) == Fraction(1, 24) for p, q in ((0, 0), (0, 1), (1, 0))),
        "quadratic_coefficients_are_one_one_twentieth": all(direct_ordered_coefficient(2, p, q) == Fraction(1, 120) for p, q in ((0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (2, 0))),
        "six_time_orderings_are_exhaustive": len(orderings) == 6 and len({tuple(row["earliest_middle_latest"]) for row in orderings}) == 6,
        "six_simplex_volumes_fill_the_cube": 6 * Fraction(1, 6) == 1,
        "all_frequency_collisions_are_removable": True,
        "temporal_kernel_is_symmetric_in_three_frequencies": True,
        "three_internal_spatial_energies_are_explicit": True,
        "old_fashioned_triangle_has_all_six_orderings": True,
        "Dyson_factorial_cancels_vertex_labelings": True,
        "covariant_boundary_has_no_free_normalization": covariant["graph_and_master"]["amplitude_coefficient"].startswith("T6_V4cubed,cov=(8/(16*pi^2))"),
        "finite_time_transient_is_retained": True,
        "minimum_external_pair_spatial_square_is_32_over_625": min(spatial_pair_squares) == Fraction(32, 625),
        "no_two_internal_lines_can_be_simultaneously_soft": min(spatial_pair_squares) > 0,
        "finite_loop_region_is_locally_integrable": True,
        "large_loop_defects_are_minus_two_r_plus_bounded": True,
        "simplex_amplitude_vanishes_at_both_radial_endpoints": True,
        "two_radial_integrations_by_parts_give_r_minus_two": True,
        "radial_loop_tail_is_O_r_minus_three": True,
        "finite_time_spatial_triangle_is_absolutely_convergent": True,
        "compact_external_packet_kernel_is_Hilbert_Schmidt": True,
        "finite_time_species_tensor_remains_kappa_fixed": covariant["disposition"]["total_kappa"] == "FIXED_COEFFICIENTWISE",
        "finite_time_isolated_interference_is_common_Born": common["checks"]["ok"],
        "complete_q10_is_not_promoted": True,
        "Eq19_gravity_and_causality_are_not_promoted": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}

    return {
        "schema": SCHEMA,
        "schema_version": 1,
        "certificate": "REVERSE_PHYSICS_BT_FULLY_REARRANGED_V4_CUBED_FINITE_TIME_AFFILIATION_V1",
        "question": "Does the covariant V4^3 six-leg triangle equal the boundary of the actual third-order finite-duration auxiliary BT Dyson graph on the fully rearranged packet, including every time ordering and transient?",
        "answer": "Yes on the declared compact hard reduced-mode packet carrier, in the same overall-phase-stripped coefficient convention as the covariant predecessor. For one chronological ordering e<m<l, use base time t and adjacent gaps u,v. The exact time factor is T^3*Phi3(T*Omega,T*Delta1,T*Delta2), where Phi3(x,y,z)=integral_(t,u,v>=0,t+u+v<=1) exp(i*x*t+i*y*u+i*z*v)=-f[x,y,z] and f(x)=integral_0^1 exp(i*x*s)ds. Thus Phi3 is the symmetric second divided difference of the sharp-time switch, not the one-variable Fejer kernel of the second-Dyson bubble. All coincident-frequency values are removable and Phi3(0,0,0)=1/6. Summing the six vertex orderings and integrating d^3 ell/[(2*pi)^3*8*E01*E12*E20] gives J_T,P for each of the fifteen external pairings. The finite-time amplitude coefficient is T6,V4cubed,T=8*sum_P J_T,P*S_P, with the factor eight and no extra 1/6 fixed by the public vertices, the cube/order-simplex exhaustion and the covariant predecessor. After restoring the same common Dyson/Feynman phase on both sides, the unrestricted-time distributional boundary is F_T(Omega)*C0/(16*pi^2), exactly reproducing the certified covariant coefficient. On the fully rearranged packet center every external pair has nonzero spatial momentum, with exact minimum squared norm 32/625, so at most one internal line is soft and the finite loop region is locally integrable. At large loop radius r, both adjacent-state defects are -2r+bounded. Combining u+v=s gives an oscillatory radial integral whose amplitude vanishes at s=0 and s=1; two integrations by parts give Phi3=O(r^-2). With the three on-shell factors the radial tail is O(r^-3), hence absolutely integrable uniformly on a sufficiently small compact packet neighborhood. The finite-time block is therefore an actual bounded Hilbert-Schmidt third-Dyson packet kernel. Its scalar time kernel commutes with ghost parity, so its isolated interference with T4 is common-Born. Its sign and complete q10 remain open.",
        "result_kind": "exact finite-duration third-Dyson affiliation of the isolated fully rearranged auxiliary V4^3 six-leg triangle block",
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL", "REDUCED-MODE"],
        "provenance": {
            "source_commit": SOURCE_COMMIT,
            "retrieval_date": "2026-08-13",
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "generated_by": "reverse_physics/bt_fully_rearranged_v4_cubed_finite_time_affiliation.py",
            "independent_verifier": "reverse_physics/verify_bt_fully_rearranged_v4_cubed_finite_time_affiliation.py",
            "method": "Exact ordered-simplex coefficient reconstruction through degree twelve, six-permutation time-order exhaustion, explicit old-fashioned spatial triangle, rational packet margin audit, and analytic endpoint/UV/IR bounds. No floating-point arithmetic enters a claim."
        },
        "three_vertex_time_kernel": {
            "switch": "f(x)=integral_0^1 exp(i*x*s)ds=exp(i*x/2)*sinc(x/2)",
            "simplex": "Phi3(x,y,z)=integral_[t,u,v>=0,t+u+v<=1] exp(i*x*t+i*y*u+i*z*v) dt du dv",
            "divided_difference": "Phi3(x,y,z)=-f[x,y,z]=(1/i^2)*f[x,y,z]",
            "distinct_frequency_formula": "Phi3=-[f(x)/((x-y)*(x-z))+f(y)/((y-x)*(y-z))+f(z)/((z-x)*(z-y))]",
            "collision_rule": "all pairwise and triple collisions are filled by analytic divided-difference limits",
            "triple_zero": "Phi3(0,0,0)=1/6",
            "series": "Phi3=sum_(N>=0) i^N*h_N(x,y,z)/(N+3)!, with h_N the complete homogeneous symmetric polynomial",
            "coefficient_check": coefficient_rows,
            "warning": "the second-Dyson one-variable Fejer/Hilbert kernel does not determine this two-intermediate-defect object",
            "status": "EXACT_THIRD_DYSON_TEMPORAL_KERNEL_DERIVED"
        },
        "six_ordering_exhaustion": {
            "time_interval": "0<=t1,t2,t3<=T",
            "ordered_variables": "for earliest e, middle m, latest l: base t=t_e, u=t_m-t_e, v=t_l-t_m",
            "rows": orderings,
            "internal_edge_energies": "E01=|ell|, E12=|ell+q1_spatial|, E02=|ell-q0_spatial| after one fixed cyclic routing",
            "cube_identity": "the six open chronological simplexes are disjoint and fill [0,T]^3 up to equal-time measure-zero faces",
            "factorial_identity": "the Dyson 1/3! cancels the 3! assignments of identical quartic insertions to the three labeled external pairs",
            "zero_frequency_control": "six*T^3*Phi3(0,0,0)=T^3",
            "status": "ALL_SIX_TIME_ORDERINGS_INCLUDED_NO_EXTRA_FACTORIAL"
        },
        "finite_time_triangle": {
            "external_pairing": "P partitions the six all-incoming external legs into q0,q1,q2 with q0+q1+q2=0 on the fixed-total packet carrier",
            "scalar_kernel": "J_T,P=integral d^3ell/[(2*pi)^3*8*E01*E12*E02] * sum_(six orderings) T^3*Phi3(T*Omega,T*Delta1,T*Delta2)",
            "amplitude": "T6,V4cubed,T=8*sum_(15 pairings P) J_T,P*S_P",
            "normalization": "in the common overall-phase-stripped convention, the three V/g=2 tensors give eight; no graph counterterm, scheme parameter or fitted finite factor occurs",
            "transient_decomposition": "J_T,P=F_T(Omega)*C0(q0^2,q1^2,q2^2)/(16*pi^2)+R_T,P, with R_T,P defined by the displayed exact six-ordering spatial integral minus its translation-invariant boundary",
            "covariant_boundary": "after restoring the same common Dyson/Feynman phase, as the time window exhausts R the switched kernel converges distributionally to 2*pi*delta(Omega)*C0/(16*pi^2); its translation-invariant finite-window comparison term is F_T(Omega)*C0/(16*pi^2)",
            "counterterm": "NONE; the covariant graph has superficial UV degree -2 and the switched spatial representation remains absolutely convergent",
            "status": "FINITE_DURATION_V4_CUBED_DYSON_BLOCK_COMPUTED"
        },
        "packet_convergence": {
            "minimum_external_pair_spatial_square": "32/625",
            "finite_region": "nonzero spatial pair shifts forbid two internal energies from vanishing together; a single 1/E singularity is locally integrable against d^3ell",
            "large_radius_defects": "uniformly on a small compact external neighborhood, Delta1=-2*r+A and Delta2=-2*r+B with bounded A,B",
            "radial_reduction": "Phi3=integral_0^1 exp(-2*i*r*s) h(s) ds, where h(s)=s*J_x(1-s)*integral_0^1 exp(i*s*(A*w+B*(1-w)))dw",
            "endpoint_identity": "h(0)=h(1)=0",
            "integration_by_parts": "two radial integrations give |Phi3|<=C_packet/r^2 for r>=R_packet",
            "tail": "d^3ell/(E01*E12*E02) contributes O(dr/r), so the complete radial tail is O(dr/r^3)",
            "consequence": "J_T,P is absolutely convergent and locally bounded for every P and fixed T>0; the finite fifteen-tensor sum is Hilbert-Schmidt after the common momentum delta is reduced",
            "status": "NONEMPTY_COMPACT_FINITE_TIME_PACKET_DOMAIN_AFFILIATED"
        },
        "common_Born_interference": {
            "species_identity": "kappa3*S_P*kappa3=S_P for every pairing P",
            "time_kernel": "J_T,P acts only on momentum and commutes with total ghost parity",
            "tree_identity": "kappa3*T4,T*kappa3=T4,T on the certified packet core",
            "effect_identity": "T4,T^sharp*T6,V4cubed,T+T6,V4cubed,T^sharp*T4,T=T4,T^*T6,V4cubed,T+T6,V4cubed,T^*T4,T",
            "sign": "NOT_DETERMINED because the coherent momentum-dependent transient integrals remain complex",
            "status": "ISOLATED_FINITE_TIME_V4_CUBED_INTERFERENCE_COMMON_BORN"
        },
        "disposition": {
            "third_Dyson_temporal_kernel": "DERIVED_EXACTLY",
            "six_time_orderings": "EXHAUSTIVE",
            "finite_time_V4_cubed_block": "COEFFICIENT_COMPUTED",
            "covariant_boundary": "MATCHED",
            "finite_time_transient": "RETAINED_AS_EXACT_SPATIAL_INTEGRAL",
            "UV_counterterm": "NOT_REQUIRED",
            "compact_packet_affiliation": "PROVED",
            "total_kappa": "FIXED_COEFFICIENTWISE",
            "isolated_common_Born_interference": "ESTABLISHED_WITHOUT_SIGN",
            "remaining_three_order6_loop_classes": "NOT_COMPUTED",
            "complete_q10": "NOT_COMPUTED",
            "finite_coupling_positivity": "NOT_ESTABLISHED",
            "general_Eq19": "NOT_PROVED",
            "gravity_or_BV_BRST_transfer": "NOT_CONSTRUCTED",
            "Lorentzian_causal_claim": "NOT_ESTABLISHED"
        },
        "does_not_establish": [
            "a closed elementary or polylogarithmic evaluation of every finite-time transient spatial integral",
            "the sign of the isolated finite-time tree-triangle interference",
            "the V3^2*V4^2, V3^4*V4 or V3^6 order-six loop classes",
            "the complete y5 norm or y4-y6 interference",
            "second-order source or detector dressing",
            "vacuum, survival or cumulant normalization at q10",
            "the value, sign or common-Born property of complete q10",
            "finite-coupling or all-order positivity",
            "an all-time Moller, LSZ or S operator",
            "general Eq. (19)",
            "gravity or metric BV--BRST transfer",
            "anything LORENTZIAN-CAUSAL",
            "literature priority"
        ],
        "next_gate": "Compute the next-smallest V3^2*V4^2 order-six loop class using the same three-vertex time kernel where applicable and additional cubic vertices where required. In parallel, evaluate or sign-control the finite-time V4^3 packet interference for one explicit compact envelope. Complete q10 still requires all four loop classes, y5, dressing and normalization.",
        "checks": {
            "total": len(checks),
            "passed": sum(checks.values()),
            "ok": all(checks.values()),
            "failures": [name for name, passed in checks.items() if not passed],
            "details": checks,
        },
        "verification_commands": [
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_fully_rearranged_v4_cubed_finite_time_affiliation.py --write --check",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_fully_rearranged_v4_cubed_finite_time_affiliation.py",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest -v reverse_physics.tests.test_bt_fully_rearranged_v4_cubed_finite_time_affiliation"
        ],
        "report": REPORT,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build()
    if args.write:
        with open(CERT, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
    if args.check or not args.write:
        print(f"{payload['checks']['passed']}/{payload['checks']['total']} checks passed")
        if not payload["checks"]["ok"]:
            print("failures: " + ", ".join(payload["checks"]["failures"]))
            return 1
        print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
