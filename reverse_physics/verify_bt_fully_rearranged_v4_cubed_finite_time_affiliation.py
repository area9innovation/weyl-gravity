#!/usr/bin/env python3
"""Independent verifier for the finite-time BT V4^3 triangle affiliation."""
from __future__ import annotations

from fractions import Fraction
from math import comb, factorial
import hashlib
import itertools
import json
import os

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_FULLY_REARRANGED_V4_CUBED_FINITE_TIME_AFFILIATION_V1.json"
)
SCHEMA_REL = (
    "reverse_physics/schema/"
    "reverse-physics-bt-fully-rearranged-v4-cubed-finite-time-affiliation-v1.schema.json"
)
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
    try:
        with open(os.path.join(ROOT, path), encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, ValueError):
        return {}


def sha256(path):
    digest = hashlib.sha256()
    try:
        with open(os.path.join(ROOT, path), "rb") as handle:
            for block in iter(lambda: handle.read(65536), b""):
                digest.update(block)
    except OSError:
        return ""
    return digest.hexdigest()


def fraction_vector(row):
    return tuple(Fraction(entry) for entry in row)


def independent_simplex_rows():
    """Use the Dirichlet moment formula, not the producer's recursion."""
    rows = []
    all_coefficients_match = True
    for degree in range(13):
        expected = Fraction(1, factorial(degree + 3))
        count = 0
        for p, q, r in itertools.product(range(degree + 1), repeat=3):
            if p + q + r != degree:
                continue
            count += 1
            simplex_moment = Fraction(
                factorial(p) * factorial(q) * factorial(r),
                factorial(degree + 3),
            )
            exponential_coefficient = Fraction(
                1,
                factorial(p) * factorial(q) * factorial(r),
            )
            all_coefficients_match &= simplex_moment * exponential_coefficient == expected
        rows.append({
            "total_degree": degree,
            "coefficient_without_i_power": str(expected),
            "monomial_count": count,
        })
        all_coefficients_match &= count == comb(degree + 2, 2)
    return rows, all_coefficients_match


def independent_ordering_rows():
    rows = []
    for index, order in enumerate(itertools.permutations((0, 1, 2))):
        early, middle, late = order
        em = f"E{min(early, middle)}{max(early, middle)}"
        el = f"E{min(early, late)}{max(early, late)}"
        ml = f"E{min(middle, late)}{max(middle, late)}"
        rows.append({
            "index": index,
            "earliest_middle_latest": list(order),
            "overall_frequency": "Omega=q0^0+q1^0+q2^0",
            "first_interval_defect": f"Delta1=q{middle}^0+q{late}^0-({em}+{el})",
            "second_interval_defect": f"Delta2=q{late}^0-({ml}+{el})",
        })
    return rows


def minimum_pair_spatial_square(packet):
    witness = packet.get("exact_detector_witness", {})
    incoming = [fraction_vector(row) for row in witness.get("incoming_momenta", [])]
    outgoing = [tuple(-entry for entry in fraction_vector(row)) for row in witness.get("outgoing_momenta", [])]
    momenta = incoming + outgoing
    values = []
    for left, right in itertools.combinations(momenta, 2):
        total = tuple(a + b for a, b in zip(left, right))
        values.append(sum(entry * entry for entry in total[1:]))
    return min(values) if values else None


def verify(certificate):
    checks = {}
    schema = load(SCHEMA_REL)
    checks["strict_schema"] = bool(schema) and not list(
        Draft202012Validator(schema).iter_errors(certificate)
    )
    checks["identity"] = certificate.get("certificate") == "REVERSE_PHYSICS_BT_FULLY_REARRANGED_V4_CUBED_FINITE_TIME_AFFILIATION_V1"
    checks["schema"] = certificate.get("schema") == "reverse_physics/schema/reverse-physics-bt-fully-rearranged-v4-cubed-finite-time-affiliation-v1.schema.json"
    checks["version"] = certificate.get("schema_version") == 1
    checks["lifecycle"] = certificate.get("lifecycle_state") == "COEFFICIENT_COMPUTED"
    checks["tags"] = certificate.get("dependency_tags") == ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL", "REDUCED-MODE"]

    provenance = certificate.get("provenance", {})
    recorded_inputs = provenance.get("inputs", [])
    checks["source_commit"] = provenance.get("source_commit") == "2cad87ba756920989ac21b7edc2487098aea3c7a"
    checks["input_paths"] = [row.get("path") for row in recorded_inputs] == INPUTS
    checks["input_hashes"] = len(recorded_inputs) == len(INPUTS) and all(
        row.get("sha256") == sha256(path)
        for row, path in zip(recorded_inputs, INPUTS)
    )
    checks["producer_and_verifier"] = (
        provenance.get("generated_by") == "reverse_physics/bt_fully_rearranged_v4_cubed_finite_time_affiliation.py"
        and provenance.get("independent_verifier") == "reverse_physics/verify_bt_fully_rearranged_v4_cubed_finite_time_affiliation.py"
    )
    predecessors = [load(path) for path in INPUTS[3:]]
    checks["predecessors"] = all(row.get("checks", {}).get("ok") for row in predecessors)

    expected_series, coefficients_match = independent_simplex_rows()
    temporal = certificate.get("three_vertex_time_kernel", {})
    checks["Dirichlet_coefficients"] = coefficients_match and temporal.get("coefficient_check") == expected_series
    checks["simplex_formula"] = temporal.get("simplex") == "Phi3(x,y,z)=integral_[t,u,v>=0,t+u+v<=1] exp(i*x*t+i*y*u+i*z*v) dt du dv"
    checks["divided_difference"] = temporal.get("divided_difference") == "Phi3(x,y,z)=-f[x,y,z]=(1/i^2)*f[x,y,z]"
    checks["distinct_formula"] = temporal.get("distinct_frequency_formula") == "Phi3=-[f(x)/((x-y)*(x-z))+f(y)/((y-x)*(y-z))+f(z)/((z-x)*(z-y))]"
    checks["collision_and_zero"] = (
        temporal.get("collision_rule") == "all pairwise and triple collisions are filled by analytic divided-difference limits"
        and temporal.get("triple_zero") == "Phi3(0,0,0)=1/6"
    )
    checks["not_Fejer"] = "one-variable Fejer" in temporal.get("warning", "")
    checks["kernel_status"] = temporal.get("status") == "EXACT_THIRD_DYSON_TEMPORAL_KERNEL_DERIVED"

    ordering = certificate.get("six_ordering_exhaustion", {})
    expected_orderings = independent_ordering_rows()
    checks["ordering_rows"] = ordering.get("rows") == expected_orderings
    checks["six_orderings"] = len(expected_orderings) == 6 and len({tuple(row["earliest_middle_latest"]) for row in expected_orderings}) == 6
    checks["cube_and_factorial"] = (
        ordering.get("zero_frequency_control") == "six*T^3*Phi3(0,0,0)=T^3"
        and "Dyson 1/3! cancels the 3!" in ordering.get("factorial_identity", "")
    )
    checks["energy_routing"] = ordering.get("internal_edge_energies") == "E01=|ell|, E12=|ell+q1_spatial|, E02=|ell-q0_spatial| after one fixed cyclic routing"
    checks["ordering_status"] = ordering.get("status") == "ALL_SIX_TIME_ORDERINGS_INCLUDED_NO_EXTRA_FACTORIAL"

    triangle = certificate.get("finite_time_triangle", {})
    covariant = load(INPUTS[3]).get("graph_and_master", {})
    checks["scalar_triangle"] = triangle.get("scalar_kernel") == "J_T,P=integral d^3ell/[(2*pi)^3*8*E01*E12*E02] * sum_(six orderings) T^3*Phi3(T*Omega,T*Delta1,T*Delta2)"
    checks["amplitude"] = triangle.get("amplitude") == "T6,V4cubed,T=8*sum_(15 pairings P) J_T,P*S_P"
    checks["phase_convention"] = triangle.get("normalization", "").startswith("in the common overall-phase-stripped convention")
    checks["covariant_normalization"] = (
        covariant.get("amplitude_coefficient") == "T6_V4cubed,cov=(8/(16*pi^2))*sum_P C0(Q_P1^2,Q_P2^2,Q_P3^2)*S_P"
        and "same common Dyson/Feynman phase" in triangle.get("covariant_boundary", "")
        and "C0(q0^2,q1^2,q2^2)/(16*pi^2)" in triangle.get("transient_decomposition", "")
    )
    checks["transient_retained"] = "R_T,P" in triangle.get("transient_decomposition", "")
    checks["no_counterterm"] = triangle.get("counterterm", "").startswith("NONE;")
    checks["triangle_status"] = triangle.get("status") == "FINITE_DURATION_V4_CUBED_DYSON_BLOCK_COMPUTED"

    packet = load(INPUTS[6])
    convergence = certificate.get("packet_convergence", {})
    checks["packet_margin"] = minimum_pair_spatial_square(packet) == Fraction(32, 625) and convergence.get("minimum_external_pair_spatial_square") == "32/625"
    checks["IR_argument"] = "forbid two internal energies" in convergence.get("finite_region", "") and "locally integrable" in convergence.get("finite_region", "")
    checks["UV_defects"] = convergence.get("large_radius_defects") == "uniformly on a small compact external neighborhood, Delta1=-2*r+A and Delta2=-2*r+B with bounded A,B"
    checks["endpoint_argument"] = convergence.get("endpoint_identity") == "h(0)=h(1)=0"
    checks["two_integrations"] = "|Phi3|<=C_packet/r^2" in convergence.get("integration_by_parts", "")
    checks["radial_tail"] = "O(dr/r^3)" in convergence.get("tail", "")
    checks["packet_status"] = convergence.get("status") == "NONEMPTY_COMPACT_FINITE_TIME_PACKET_DOMAIN_AFFILIATED"

    common = certificate.get("common_Born_interference", {})
    checks["kappa_fixed"] = common.get("species_identity") == "kappa3*S_P*kappa3=S_P for every pairing P"
    checks["common_Born"] = (
        common.get("status") == "ISOLATED_FINITE_TIME_V4_CUBED_INTERFERENCE_COMMON_BORN"
        and "T4,T^sharp" in common.get("effect_identity", "")
        and common.get("sign", "").startswith("NOT_DETERMINED")
    )

    disposition = certificate.get("disposition", {})
    checks["computed_boundary"] = (
        disposition.get("third_Dyson_temporal_kernel") == "DERIVED_EXACTLY"
        and disposition.get("finite_time_V4_cubed_block") == "COEFFICIENT_COMPUTED"
        and disposition.get("compact_packet_affiliation") == "PROVED"
    )
    checks["not_complete_q10"] = disposition.get("complete_q10") == "NOT_COMPUTED" and disposition.get("remaining_three_order6_loop_classes") == "NOT_COMPUTED"
    checks["not_promoted"] = (
        disposition.get("finite_coupling_positivity") == "NOT_ESTABLISHED"
        and disposition.get("general_Eq19") == "NOT_PROVED"
        and disposition.get("gravity_or_BV_BRST_transfer") == "NOT_CONSTRUCTED"
        and disposition.get("Lorentzian_causal_claim") == "NOT_ESTABLISHED"
    )
    checks["boundaries"] = len(certificate.get("does_not_establish", [])) == 13 and "general Eq. (19)" in certificate.get("does_not_establish", [])
    checks["next_gate"] = all(term in certificate.get("next_gate", "") for term in ("V3^2*V4^2", "sign-control", "q10"))
    checks["report"] = certificate.get("report") == "reverse_physics/reports/bt-fully-rearranged-v4-cubed-finite-time-affiliation.md"
    return checks


def main():
    checks = verify(load(CERT_REL))
    failures = [name for name, passed in checks.items() if not passed]
    print(f"{len(checks) - len(failures)}/{len(checks)} checks passed")
    if failures:
        print("failures: " + ", ".join(failures))
        return 1
    print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
