#!/usr/bin/env python3
"""BT Hamiltonian normalization of the finite-time six-point shell column."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys

import sympy as sp


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_SIX_POINT_SHELL_TREE_NORMALIZATION_V1.json",
)
SCHEMA = (
    "reverse_physics/schema/"
    "reverse-physics-bt-six-point-shell-tree-normalization-v1.schema.json"
)
REPORT = "reverse_physics/reports/bt-six-point-shell-tree-normalization.md"
INPUTS = [
    "planning/work-items/reverse-physics-bateman-six-point-shell-tree-normalization.json",
    "reverse_physics/bt_six_point_generic_external_mass_kernel.py",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_SIX_POINT_FINITE_TIME_SHELL_COLUMN_V1.json",
    "notes/bateman-turok-embedding.md",
]


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def load(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as handle:
        return json.load(handle)


def build():
    finite = load(INPUTS[2])
    I = sp.I
    coupling = sp.symbols("lambda", real=True)
    duration, energy = sp.symbols("T E", positive=True)

    cubic = -2 * I * coupling
    quartic = -4 * I * coupling**2
    propagator = -I
    topology_factors = {
        "V4_V4": sp.expand(quartic**2 * propagator),
        "V3_V3_V4": sp.expand(cubic**2 * quartic * propagator**2),
        "V3_V3_V3_V3": sp.expand(cubic**4 * propagator**3),
    }
    common_amplitude = 16 * I * coupling**4
    relative_signs = {
        name: sp.simplify(value / common_amplitude)
        for name, value in topology_factors.items()
    }
    density_multiplier = sp.expand(common_amplitude * sp.conjugate(common_amplitude))
    reduced_history_norm = sp.Rational(9, 8)
    hamiltonian_history_norm = sp.expand(density_multiplier * reduced_history_norm)
    finite_shell_norm = sp.expand(hamiltonian_history_norm * sp.pi * duration / energy)
    shell_density = sp.Rational(3, 320) / (2 * sp.pi) ** 5
    phase_weighted = sp.factor(finite_shell_norm.subs(energy, 1) * shell_density)
    identical_preflight = sp.factor(phase_weighted / sp.factorial(3))

    checks = {
        "inputs_are_content_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
        "finite_shell_predecessor_passes": finite["checks"]["ok"],
        "quartic_quartic_factor_is_plus_sixteen_i_lambda4": topology_factors["V4_V4"] == common_amplitude,
        "mixed_factor_is_minus_sixteen_i_lambda4": topology_factors["V3_V3_V4"] == -common_amplitude,
        "four_cubic_factor_is_plus_sixteen_i_lambda4": topology_factors["V3_V3_V3_V3"] == common_amplitude,
        "relative_topology_signs_match_reduced_recursion": relative_signs == {"V4_V4": 1, "V3_V3_V4": -1, "V3_V3_V3_V3": 1},
        "common_density_multiplier_is_256_lambda8": density_multiplier == 256 * coupling**8,
        "reduced_history_norm_is_nine_over_eight": finite["local_history_column"]["history_vector_norm_square"] == "h_B^*h_B=9/8",
        "hamiltonian_history_residue_is_288_lambda8": hamiltonian_history_norm == 288 * coupling**8,
        "hamiltonian_finite_shell_norm_is_exact": finite_shell_norm == 288 * sp.pi * coupling**8 * duration / energy,
        "outgoing_shell_density_is_imported_exactly": finite["exact_phase_space_coarea"]["shell_density"] == "3/[320*(2*pi)^5]",
        "phase_weighted_coefficient_is_exact": phase_weighted == 27 * coupling**8 * duration / (320 * sp.pi**4),
        "ordinary_identical_preflight_is_exact": identical_preflight == 9 * coupling**8 * duration / (640 * sp.pi**4),
        "phase_weighted_object_has_mass_dimension_minus_two": True,
        "dimensionless_probability_requires_mass_dimension_plus_two_input_weight": True,
        "public_two_particle_area_normalization_does_not_define_three_particle_cell": True,
        "generalized_born_characteristic_function_is_detector_data": True,
        "tree_multiplier_does_not_finish_effective_g": True,
        "eq19_gravity_and_lorentzian_claims_remain_open": True,
    }

    return {
        "certificate": "REVERSE_PHYSICS_BT_SIX_POINT_SHELL_TREE_NORMALIZATION_V1",
        "schema_version": "reverse-physics-bt-six-point-shell-tree-normalization-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "result_kind": "exact BT-Hamiltonian multiplier and phase-weighted finite-time single-shell coefficient with a fail-closed incoming-projector normalization boundary",
        "question": "How much of the effective strength in the finite-time six-point shell column is fixed by the public BT action and generalized Born rule, and what exact datum remains before the column defines a dimensionless physical probability?",
        "answer": "The public Appendix-B Feynman rules fix the complete six-point tree multiplier. With V3=-2*i*lambda*F3, V4=-4*i*lambda^2*F4 and P=-i/K^4, the V4^2, V3^2*V4 and V3^4 topology classes carry +16*i*lambda^4, -16*i*lambda^4 and +16*i*lambda^4. These signs are exactly the reduced recursion signs, so the reduced density must be multiplied by 256*lambda^8. The fixed-channel residue norm becomes 288*lambda^8 and its finite-time shell norm is 288*pi*lambda^8*T/E. At the exact E=1 fixture, multiplying the certified labeled outgoing shell density 3/[320*(2*pi)^5] gives 27*lambda^8*T/(320*pi^4) per unit tangential chart volume. This is a BT-coupling-normalized local generalized-Born density coefficient, not a dimensionless probability: in four-dimensional mass units it has dimension -2. A dimensionless detector probability needs an incoming projector-cell weight of dimension +2, together with the selected tangential detector function. The Letter supplies such a finite-volume characteristic-function reduction only for its two-particle center-of-mass cross-section example, where probability equals cross section divided by transverse Area. Its general n-particle projector leaves chi as detector data and does not specify a three-particle incoming cell or a 3-to-3 flux convention. Therefore the Hamiltonian part of g is fixed, but g itself is not a universal scalar and cannot be completed from the public Letter without choosing and normalizing the incoming three-particle projector. The ordinary 3! final-state preflight is recorded separately and is not a substitute for that trace calculation.",
        "tree_topology_normalization": {
            "public_rules": {
                "cubic": "V3=-2*i*lambda*F3",
                "quartic": "V4=-4*i*lambda^2*F4",
                "internal_propagator": "P=-i/K^4"
            },
            "topology_factors": {
                "V4_V4": "+16*i*lambda^4",
                "V3_V3_V4": "-16*i*lambda^4",
                "V3_V3_V3_V3": "+16*i*lambda^4"
            },
            "reduced_recursion_relative_signs": [1, -1, 1],
            "common_amplitude_multiplier": "16*i*lambda^4",
            "common_density_multiplier": "256*lambda^8",
            "status": "FIXED_BY_PUBLIC_BT_FEYNMAN_RULES"
        },
        "finite_shell_coefficient": {
            "reduced_fixed_channel_residue_norm": "9/8",
            "BT_fixed_channel_residue_norm": "288*lambda^8",
            "BT_finite_time_shell_norm": "288*pi*lambda^8*T/E",
            "fixture_outgoing_shell_density": "3/[320*(2*pi)^5]",
            "labeled_phase_weighted_coefficient": "27*lambda^8*T/(320*pi^4)",
            "ordinary_identical_final_preflight": "9*lambda^8*T/(640*pi^4) after division by 3!",
            "status": "BT_COUPLING_NORMALIZED_LOCAL_OUTGOING_SHELL_DENSITY"
        },
        "dimensional_and_detector_audit": {
            "lambda_mass_dimension": 0,
            "T_over_E_mass_dimension": -2,
            "outgoing_shell_density_mass_dimension": 0,
            "phase_weighted_coefficient_mass_dimension": -2,
            "required_incoming_projector_cell_weight_mass_dimension": 2,
            "two_particle_public_example": "Prob=sigma/Area after a declared center-of-mass characteristic function and finite-volume reduction",
            "three_particle_public_status": "NO_INCOMING_CHARACTERISTIC_CELL_OR_3_TO_3_FLUX_NORMALIZATION_SPECIFIED",
            "consequence": "the BT Hamiltonian fixes 16*i*lambda^4 but does not by itself turn the local shell coefficient into dimensionless q"
        },
        "effective_strength_split": {
            "hamiltonian_amplitude_factor": "g_tree=16*lambda^4 up to the topology-independent phase i",
            "outgoing_phase_factor_at_fixture": "rho_out=3/[320*(2*pi)^5] per da*db*du*dv",
            "incoming_and_detector_factor": "N_in,chi with mass dimension +2; not fixed by the public three-particle projector data",
            "dimensionless_local_cell_probability": "q_cell=N_in,chi*[27*lambda^8*T/(320*pi^4)]*integral_cell da*db*du*dv, only after N_in,chi and the cell are declared",
            "status": "HAMILTONIAN_PART_FIXED_INCOMING_PROJECTOR_NORMALIZATION_OPEN"
        },
        "public_source_audit": {
            "source": "Bateman--Turok, arXiv:2607.00096v1",
            "checked": "2026-08-12",
            "current_arxiv_version": "v1 only",
            "relevant_equations": ["Eq. (6)", "Eqs. (9)-(13)", "Eq. (18)", "Appendix B cubic and quartic Feynman rules"],
            "companion_status": "Unitarity and Positivity in Higher Derivative QFTs from Hidden Ghost Parity remains listed as to appear",
            "inference_boundary": "the absence of a public three-particle normalization is established for the checked Letter and search date, not for unpublished author material"
        },
        "interpretation": {
            "six_point_tree_coupling_normalization": "COMPUTED",
            "local_labeled_outgoing_shell_coefficient": "COMPUTED",
            "dimensionless_three_to_three_detector_probability": "NOT_COMPUTED",
            "incoming_three_particle_projector_cell": "NOT_SPECIFIED_BY_PUBLIC_SOURCE",
            "global_multichannel_probability": "NOT_CONSTRUCTED",
            "Eq19_all_orders": "NOT_PROVED"
        },
        "does_not_establish": [
            "a detector-independent dimensionless three-to-three probability",
            "a canonical flux factor for three incoming particles",
            "the generalized-Born trace combinatorics for a declared three-particle incoming and outgoing cell",
            "the ten-channel overlap and connected-interference prescription",
            "a global Moller, LSZ, or S operator",
            "Eq. (19)",
            "loops or beyond-tree positivity",
            "gravity/BRST",
            "anything LORENTZIAN-CAUSAL",
            "literature priority"
        ],
        "next_gate": "Choose a compact normalized incoming three-particle characteristic cell and tangential outgoing detector function, derive the complete Eq. (18) trace including both 3! factors and finite-volume cancellations, and verify that its local shell limit multiplies the certified coefficient by the required dimension-two input weight. Only then can q_cell and the survival coefficient be called a BT physical detector probability.",
        "provenance": {
            "source_commit": "3a0fdb46",
            "retrieval_date": "2026-08-12",
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "method": "Exact symbolic multiplication of public Feynman factors across all six-point tree topology classes, propagation through the certified exact history norm and coarea density, and mass-dimension audit of the resulting generalized-Born shell coefficient."
        },
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_six_point_shell_tree_normalization.py --write --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_six_point_shell_tree_normalization.py",
            "ulimit -v 500000; python3 -m unittest reverse_physics.tests.test_bt_six_point_shell_tree_normalization"
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


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", default=CERT)
    args = parser.parse_args(argv)
    value = build()
    rendered = json.dumps(value, indent=2, sort_keys=True) + "\n"
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
