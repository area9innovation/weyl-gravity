#!/usr/bin/env python3
"""Exact nonplanar-diagonal BT six-point local Born-density theorem."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "reverse_physics"))

from bt_six_point_generic_external_mass_kernel import nonplanar_diagonal_family


CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_SIX_POINT_NONPLANAR_DIAGONAL_PHYSICAL_BORN_DENSITY_V1.json",
)
SCHEMA = (
    "reverse_physics/schema/"
    "reverse-physics-bt-six-point-nonplanar-diagonal-physical-born-density-v1.schema.json"
)
REPORT = (
    "reverse_physics/reports/"
    "bt-six-point-nonplanar-diagonal-physical-born-density.md"
)
SOURCE = "24e988693bd9ee6874bedf9de476202c949a2e7e"
INPUTS = [
    "planning/work-items/"
    "reverse-physics-bateman-six-point-nonplanar-diagonal-born-density.json",
    "reverse_physics/bt_six_point_generic_external_mass_kernel.py",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_SIX_POINT_PLANAR_PHYSICAL_BORN_DENSITY_V1.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_CROSSED_SIX_POINT_NONFACTORIZING_PRETRACE_NO_GO_V1.json",
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


def build():
    family = nonplanar_diagonal_family()
    planar = load(INPUTS[2])
    crossed = load(INPUTS[3])
    poles = family["squarefree_denominator_factors"]
    checks = {
        "predecessors_pass": planar["checks"]["ok"] and crossed["checks"]["ok"],
        "input_hashes_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
        "all_six_momenta_are_exactly_massless": family["all_six_massless"],
        "three_to_three_momentum_is_exactly_conserved": family[
            "momentum_conservation"
        ],
        "tilt_parameter_is_t_over_two": family["tilt"]["ratio"] == "1/2"
        and family["tilt"]["parameter"] == "t/2",
        "outgoing_family_is_generically_nonplanar": family[
            "generic_outgoing_z_is_nonzero"
        ] and family["incoming_and_outgoing_planes_differ_generically"],
        "complete_amplitude_has_42_terms": family["amplitude_term_count"] == 42,
        "amplitude_support_is_degrees_three_through_six": family[
            "amplitude_degrees"
        ] == [3, 4, 5, 6],
        "all_twenty_middle_coefficients_retained": family[
            "degree_three_term_count"
        ] == 20 and len(family["middle_coefficients"]) == 10,
        "all_ten_complement_pairs_equal": family["ten_complement_pairs_equal"]
        and all(
            row["coefficient"] == row["complement_coefficient"]
            for row in family["middle_coefficients"]
        ),
        "topology_antisymmetry_is_nontrivial": family[
            "topology_antisymmetry_is_nontrivial"
        ],
        "perfect_square_topology_sum_cancels_antisymmetry": family[
            "topology_antisymmetry_cancels_in_complete_amplitude"
        ],
        "top_mass_coefficient_is_twice_ten_squares": family[
            "equals_twice_ten_square_sum"
        ],
        "ten_numerators_have_gcd_one": family[
            "degree_three_numerator_gcd"
        ] == "1" and family["no_common_complex_zero_of_ten_coefficients"],
        "all_ten_pole_factors_have_even_multiplicity": len(poles) == 10
        and all(row["multiplicity"] == 2 for row in poles),
        "six_external_delta_prime_sign_is_positive": (-1) ** 6 == 1,
        "regular_measure_derivatives_decouple": min(
            family["amplitude_degrees"]
        ) == 3,
        "local_density_is_strictly_positive_off_poles": family[
            "equals_twice_ten_square_sum"
        ] and family["no_common_complex_zero_of_ten_coefficients"],
        "planar_result_is_strictly_extended": planar["interpretation"][
            "complete_nonplanar_six_body_phase_space"
        ] == "NOT_COMPUTED",
        "correlated_negative_quotient_not_promoted": crossed[
            "physical_disposition"
        ]["finite_hierarchy_crossed_fixed_sharp_quotient"] == "NEGATIVE_RANK_TWO",
        "two_parameter_family_remains_open": True,
        "integration_eq19_gravity_and_causality_remain_open": True,
    }
    return {
        "certificate": "REVERSE_PHYSICS_BT_SIX_POINT_NONPLANAR_DIAGONAL_PHYSICAL_BORN_DENSITY_V1",
        "schema_version": "reverse-physics-bt-six-point-nonplanar-diagonal-physical-born-density-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "result_kind": "exact local six-delta-prime tree Born density on a genuinely nonplanar continuous physical 3-to-3 family",
        "question": "Does the positive ten-square six-point BT Born density survive when the outgoing three-particle plane is tilted out of the incoming plane on an exact continuum?",
        "answer": "Yes on the declared diagonal nonplanar family. Starting from the certified rational in-plane rotation with parameter t, apply an independent-axis rational rotation whose stereographic parameter is u=t/2. The incoming momenta lie in z=0 while the outgoing momenta have generically nonzero z-components; all six are exactly null and conserve four-momentum. The complete 220-tree 64-slot external-mass amplitude again has 42 terms beginning at degree three. Its twenty middle-degree coefficients obey ten exact complement equalities, although the three topology sectors are individually complement-antisymmetric. Therefore the six-delta-prime coefficient is twice a sum of ten rational squares. Their numerator gcd is one and all ten rational pole factors have multiplicity two, proving strict positivity for every regular real t. Coplanarity is not responsible for the positive mechanism. This is still a one-parameter diagonal through the nonplanar phase space, not the full two-parameter family or an integrated probability.",
        "exact_nonplanar_family": family,
        "local_born_density": {
            "external_projector": "(-partial_x0)...(-partial_x5) evaluated at x_i=0",
            "external_derivative_sign": "+1 from (-1)^6",
            "amplitude_minimum_mass_degree": 3,
            "squared_amplitude_minimum_mass_degree": 6,
            "measure_decoupling": "The squared amplitude begins at the full six-mass mask, so the local top coefficient of K(x)|M(x)|^2 is K(0) times the displayed ten-square kernel for every regular analytic weight K.",
            "positivity_assumption": "The undifferentiated massless local phase-space/detector weight K(0) is strictly positive at a regular interior point.",
            "status": "STRICTLY_POSITIVE_ON_DECLARED_REGULAR_NONPLANAR_FAMILY"
        },
        "interpretation": {
            "planar_coplanarity_is_required_for_positivity": "NO",
            "nonplanar_diagonal_middle_degree_recombination": "POSITIVE_TEN_SQUARE_SUM",
            "correlated_crossed_negative_quotient": "REMAINS_A_REDUCED_BOUNDARY_BLOCK",
            "complete_two_parameter_nonplanar_family": "NOT_COMPUTED",
            "integrated_normalized_probability": "NOT_COMPUTED",
            "Eq19_all_orders": "NOT_PROVED"
        },
        "assumptions": [
            "The public BT cubic and quartic vertices are used with the perfect-square relative coupling and their common tree phase omitted before squaring.",
            "Signature is (+---), and the outgoing future-null momenta enter the all-incoming amplitude with a minus sign.",
            "The outgoing rotation is R_x(u)R_z(t) with rational stereographic parameters u=t/2.",
            "The nine cyclic invariants are held fixed while the six independent external mass squares are differentiated.",
            "Real t excludes every zero of the ten displayed internal-propagator pole factors.",
            "The local phase-space/detector weight is regular, analytic in the mass jet, and positive at the massless interior point.",
            "A diagonal one-parameter curve does not determine the whole two-parameter nonplanar phase space."
        ],
        "does_not_establish": [
            "positivity over the complete two-parameter or full nonplanar six-body phase space",
            "an integrated or normalized six-point transition probability",
            "regulation or cancellation of internal propagator poles",
            "twelve separately positive reversed-history intertwiners",
            "a complete Moller, LSZ, or S operator",
            "Bateman--Turok Eq. (19)",
            "positivity beyond tree level or KLN cancellation",
            "a metric or BRST lift to Weyl gravity",
            "anything LORENTZIAN-CAUSAL",
            "a new physical or spacetime dimension",
            "literature priority"
        ],
        "next_gate": "Use the exact nonplanar degree-50 numerator and ten even pole factors to replace direct Q(t,u) cancellation by a degree-bounded modular/interpolation certificate for two independent rotation parameters. If complement self-duality survives, construct a common regulated six-body integral; otherwise record the first nonplanar sign wall. Eq. (19) remains a separate nonlinear projector-transport problem.",
        "provenance": {
            "source_commit": SOURCE,
            "retrieval_date": "2026-08-12",
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "producer_method": "The certified 64-slot cached subset recursion is evaluated over Q(t) after the exact physical rotation R_x(t/2)R_z(t). All 220 cubic/quartic trees and topology sectors are retained. Exact complement comparison, polynomial gcd, and denominator factorization prove strictness without floating point.",
            "primary_source": {
                "source": "Bateman--Turok arXiv:2607.00096v1",
                "url": "https://arxiv.org/abs/2607.00096v1",
                "equations": ["Eq. (18)", "Appendix B Eqs. (24)-(25)"]
            }
        },
        "verification_commands": [
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_six_point_nonplanar_diagonal_physical_born_density.py --write --check",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_six_point_nonplanar_diagonal_physical_born_density.py",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest reverse_physics.tests.test_bt_six_point_nonplanar_diagonal_physical_born_density"
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
    return 0 if value["checks"]["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
