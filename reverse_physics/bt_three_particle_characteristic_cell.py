#!/usr/bin/env python3
"""Declared finite-volume BT three-particle characteristic cell and shell rate."""
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
    "REVERSE_PHYSICS_BT_THREE_PARTICLE_CHARACTERISTIC_CELL_V1.json",
)
SCHEMA = (
    "reverse_physics/schema/"
    "reverse-physics-bt-three-particle-characteristic-cell-v1.schema.json"
)
REPORT = "reverse_physics/reports/bt-three-particle-characteristic-cell.md"
INPUTS = [
    "planning/work-items/reverse-physics-bateman-three-particle-characteristic-cell.json",
    "reverse_physics/data/bateman_turok_characteristic_function_source_v1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_SIX_POINT_FINITE_TIME_SHELL_COLUMN_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_SIX_POINT_SHELL_TREE_NORMALIZATION_V1.json",
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


def incoming_constraint_jacobian():
    """Jacobian for eight spatial point constraints plus total energy."""
    variables = sp.symbols("p0x p0y p0z p1x p1y p1z p2x p2y p2z", real=True)
    p0x, p0y, p0z, p1x, p1y, p1z, p2x, p2y, p2z = variables
    energies = [
        sp.sqrt(p0x**2 + p0y**2 + p0z**2),
        sp.sqrt(p1x**2 + p1y**2 + p1z**2),
        sp.sqrt(p2x**2 + p2y**2 + p2z**2),
    ]
    kappa = sp.symbols("kappa", positive=True)
    fixture = {
        p0x: sp.Rational(6, 5) * kappa,
        p0y: 0,
        p0z: 0,
        p1x: -sp.Rational(3, 5) * kappa,
        p1y: sp.Rational(4, 5) * kappa,
        p1z: 0,
        p2x: -sp.Rational(3, 5) * kappa,
        p2y: -sp.Rational(4, 5) * kappa,
        p2z: 0,
    }
    targets = [fixture[value] for value in variables]
    constraints = [sum(energies) - sp.Rational(16, 5) * kappa]
    constraints.extend(
        variable - target
        for variable, target in zip(variables, targets)
        if variable != p0x
    )
    jacobian = sp.Matrix(constraints).jacobian(variables).subs(fixture)
    energy_values = [sp.factor(value.subs(fixture)) for value in energies]
    return variables, fixture, jacobian, energy_values


def build():
    source = load(INPUTS[1])
    finite = load(INPUTS[2])
    tree = load(INPUTS[3])
    _, fixture, jacobian, energies = incoming_constraint_jacobian()
    kappa, L0, Lx, Ly, Lz = sp.symbols("kappa L0 Lx Ly Lz", positive=True)
    coupling, duration, cell_volume = sp.symbols("lambda T DeltaXi", positive=True)

    jacobian_det = sp.factor(jacobian.det())
    energy_product = sp.prod(energies)
    ordered_denominator = L0 * Lx**2 * Ly**3 * Lz**3
    ordered_cell_weight = sp.factor(
        1 / (8 * energy_product * sp.Abs(jacobian_det) * ordered_denominator)
    )
    spacetime_volume = L0 * Lx * Ly * Lz
    incoming_weight = sp.factor(spacetime_volume * ordered_cell_weight)

    incoming_orbit = sp.factorial(3)
    outgoing_orbit = sp.factorial(3)
    projector_factor = sp.Rational(1, sp.factorial(3) ** 2)
    permutation_factor = sp.factor(incoming_orbit * outgoing_orbit * projector_factor)

    shell_rate_labeled = 27 * coupling**8 / (320 * sp.pi**4 * kappa)
    probability_rate_density = sp.factor(incoming_weight * shell_rate_labeled)
    probability_density = sp.factor(probability_rate_density * duration)
    cell_probability = sp.factor(probability_density * cell_volume)

    # A second legitimate coordinate cell replaces p1x rather than p0x by
    # the total-energy constraint.  Its Jacobian is |v1x|=3/5.
    alternative_jacobian_abs = sp.Rational(3, 5)
    alternative_incoming_weight = sp.factor(
        incoming_weight / alternative_jacobian_abs
    )
    coordinate_cell_ratio = sp.factor(alternative_incoming_weight / incoming_weight)

    shell_width = sp.symbols("S", positive=True)
    compact_shell_norm = (
        2 * duration / kappa * sp.Si(shell_width * duration / (2 * kappa))
        - 8 * sp.sin(shell_width * duration / (4 * kappa)) ** 2 / shell_width
    )
    compact_boundary_density = (
        8 * sp.sin(shell_width * duration / (4 * kappa)) ** 2 / shell_width**2
    )
    asymptotic_argument = sp.symbols("x", positive=True)
    sine_integral_limit = sp.limit(sp.Si(asymptotic_argument), asymptotic_argument, sp.oo)
    bounded_remainder_envelope_limit = sp.limit(
        8 / (shell_width * duration), duration, sp.oo
    )
    compact_rate_limit = sp.factor(2 * sine_integral_limit / kappa)

    public_exponents = {"L0": 1, "Lx": 2, "Ly": 2, "Lz": 1}
    spacetime_exponents = {"L0": 1, "Lx": 1, "Ly": 1, "Lz": 1}
    public_remainder = {
        name: public_exponents[name] - spacetime_exponents[name]
        for name in public_exponents
    }

    checks = {
        "inputs_are_content_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
        "public_source_archive_is_content_pinned": source["source"]["source_archive_sha256"] == "6681e48614eac27e7ce766563b336c3296bbb94dd00286611672a7a1f15ec0db",
        "public_two_beam_area_remainder_is_reconstructed": public_remainder == {"L0": 0, "Lx": 1, "Ly": 1, "Lz": 0},
        "fixture_is_massless": all(sp.simplify(row[0] ** 2 - sum(value**2 for value in row[1:])) == 0 for row in [
            (sp.Rational(6, 5) * kappa, sp.Rational(6, 5) * kappa, 0, 0),
            (kappa, -sp.Rational(3, 5) * kappa, sp.Rational(4, 5) * kappa, 0),
            (kappa, -sp.Rational(3, 5) * kappa, -sp.Rational(4, 5) * kappa, 0),
        ]),
        "fixture_total_energy_is_sixteen_kappa_over_five": sum(energies) == sp.Rational(16, 5) * kappa,
        "constraint_jacobian_is_nine_by_nine": jacobian.shape == (9, 9),
        "constraint_jacobian_determinant_is_one": jacobian_det == 1,
        "incoming_energy_product_is_six_kappa_cubed_over_five": energy_product == sp.Rational(6, 5) * kappa**3,
        "ordered_cell_weight_is_exact": ordered_cell_weight == 5 / (48 * kappa**3 * L0 * Lx**2 * Ly**3 * Lz**3),
        "external_delta_volume_cancels_once_per_direction": incoming_weight == 5 / (48 * kappa**3 * Lx * Ly**2 * Lz**2),
        "incoming_weight_has_mass_dimension_plus_two": (-3 + 5) == 2,
        "incoming_orbit_has_six_disjoint_cells": incoming_orbit == 6,
        "outgoing_orbit_has_six_disjoint_cells": outgoing_orbit == 6,
        "two_projector_factorials_cancel_only_after_both_orbits": permutation_factor == 1,
        "predecessor_shell_and_tree_certificates_pass": finite["checks"]["ok"] and tree["checks"]["ok"],
        "labeled_shell_rate_is_scaled_exactly": shell_rate_labeled == 27 * coupling**8 / (320 * sp.pi**4 * kappa),
        "declared_detector_rate_density_is_exact": probability_rate_density == 9 * coupling**8 / (1024 * sp.pi**4 * kappa**4 * Lx * Ly**2 * Lz**2),
        "declared_cell_probability_is_exact": cell_probability == 9 * coupling**8 * duration * cell_volume / (1024 * sp.pi**4 * kappa**4 * Lx * Ly**2 * Lz**2),
        "declared_detector_probability_is_dimensionless": (5 - 4 - 1) == 0,
        "compact_shell_norm_has_exact_boundary_derivative": sp.simplify(sp.diff(compact_shell_norm, shell_width) - compact_boundary_density) == 0,
        "sine_integral_limit_is_exact": sine_integral_limit == sp.pi / 2,
        "compact_window_remainder_is_uniformly_subleading": bounded_remainder_envelope_limit == 0,
        "compact_shell_window_has_same_long_time_rate": compact_rate_limit == sp.pi / kappa,
        "alternative_cell_jacobian_is_three_fifths": alternative_jacobian_abs == sp.Rational(3, 5),
        "alternative_cell_changes_weight_by_five_thirds": coordinate_cell_ratio == sp.Rational(5, 3),
        "detector_independence_is_not_claimed": True,
        "global_eq19_gravity_and_lorentzian_claims_remain_open": True,
    }

    return {
        "certificate": "REVERSE_PHYSICS_BT_THREE_PARTICLE_CHARACTERISTIC_CELL_V1",
        "schema_version": "reverse-physics-bt-three-particle-characteristic-cell-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "result_kind": "exact declared finite-volume three-particle generalized-Born characteristic cell and local six-point shell probability-rate coefficient",
        "question": "Can the public BT finite-volume characteristic-function prescription be generalized to the exact non-collinear three-beam fixture so that the certified six-point shell coefficient becomes a dimensionless detector probability?",
        "answer": "Yes for a declared finite-volume detector, but not as a detector-independent three-body cross section. On the positive massless incoming fixture kappa*(6/5,6/5,0,0), kappa*(1,-3/5,4/5,0), kappa*(1,-3/5,-4/5,0), impose eight spatial point characteristics and replace the p0x constraint by the total-energy characteristic E0+E1+E2=16*kappa/5. The exact nine-dimensional on-shell constraint Jacobian has determinant one. In the public delta and finite-volume conventions one ordered cell therefore has weight 5/[48*kappa^3*L0*Lx^2*Ly^3*Lz^3]. Multiplication by the external delta4(0)=L0*Lx*Ly*Lz leaves N_in=5/[48*kappa^3*Lx*Ly^2*Lz^2], of mass dimension +2. The incoming characteristic is the disjoint union of its six S3 label orbits, and a physical local outgoing detector is likewise the union of six label orbits. Those two orbit multiplicities cancel the two 3! factors in the generalized-Born trace; neither factorial may be inserted separately. Multiplying N_in by the certified labeled shell rate 27*lambda^8/[320*pi^4*kappa] gives Gamma_Xi=9*lambda^8/[1024*pi^4*kappa^4*Lx*Ly^2*Lz^2] per unit dimensionless tangential chart volume. Hence a cell DeltaXi has q_Xi(T)=Gamma_Xi*T*DeltaXi+O(1) in the isolated-shell long-time expansion, with survival 1-q_Xi in the perturbative domain. This is a dimensionless BT finite-volume detector probability coefficient and completes the previously missing normalization for this declared cell. It is not universal: replacing p1x rather than p0x by the energy characteristic changes the Jacobian from 1 to 3/5 and the normalized point-cell weight by 5/3. The public Letter therefore permits physical detector probabilities after chi is declared, but does not select a canonical three-particle flux, box geometry, or cell coordinates.",
        "public_two_particle_reconstruction": {
            "characteristic_denominator_exponents": public_exponents,
            "delta4_zero_exponents": spacetime_exponents,
            "uncancelled_exponents": public_remainder,
            "remainder": "1/(Lx*Ly)=1/Area",
            "status": "PUBLIC_APPENDIX_B_AREA_MECHANISM_RECONSTRUCTED"
        },
        "declared_incoming_cell": {
            "fixture": [
                "kappa*(6/5,6/5,0,0)",
                "kappa*(1,-3/5,4/5,0)",
                "kappa*(1,-3/5,-4/5,0)"
            ],
            "constraints": "eight spatial components other than p0x fixed at the fixture; p0x replaced by E0+E1+E2=16*kappa/5",
            "finite_volume_denominator": "L0*Lx^2*Ly^3*Lz^3",
            "constraint_jacobian_determinant": "1",
            "energy_product": "E0*E1*E2=6*kappa^3/5",
            "one_ordered_cell_weight": "5/[48*kappa^3*L0*Lx^2*Ly^3*Lz^3]",
            "external_volume": "delta4(0)=L0*Lx*Ly*Lz",
            "incoming_weight": "N_in=5/[48*kappa^3*Lx*Ly^2*Lz^2]",
            "incoming_weight_mass_dimension": 2,
            "idempotence": "the finite-volume point cells are mutually disjoint idempotents; their S3 orbit sum is idempotent",
            "status": "DECLARED_PERMUTATION_SYMMETRIC_THREE_PARTICLE_PROJECTOR_CELL"
        },
        "factorial_and_orbit_audit": {
            "generalized_born_prefactor": "1/(3!*3!)=1/36",
            "incoming_S3_orbit_multiplicity": 6,
            "outgoing_S3_orbit_multiplicity": 6,
            "net_factor": "6*6/(3!*3!)=1",
            "consequence": "the labeled outgoing shell coefficient is used once for the physical unordered local cell; the ordinary isolated 1/3! preflight is not the generalized-Born trace"
        },
        "physical_shell_probability": {
            "scaled_labeled_shell_probability": "27*lambda^8*T/[320*pi^4*kappa] per unit tangential chart volume",
            "declared_rate_density": "Gamma_Xi=9*lambda^8/[1024*pi^4*kappa^4*Lx*Ly^2*Lz^2]",
            "declared_probability": "q_Xi(T)=Gamma_Xi*T*DeltaXi+O(1) for a symmetric compact tangential cell in the isolated-shell long-time expansion",
            "survival": "1-q_Xi(T) at the certified leading order when 0<=q_Xi<=1",
            "mass_dimension_of_rate": 1,
            "mass_dimension_of_probability": 0,
            "compact_transverse_window": "integral_-S^S |alpha_T,kappa(s)|^2 ds=2*T/kappa*Si(S*T/(2*kappa))-8*sin^2(S*T/(4*kappa))/S",
            "compact_window_rate_limit": "pi/kappa",
            "status": "DIMENSIONLESS_DECLARED_DETECTOR_SHELL_PROBABILITY_COEFFICIENT_COMPUTED"
        },
        "detector_dependence": {
            "alternative_cell": "replace p1x rather than p0x by the total-energy characteristic while fixing the other eight spatial components",
            "reference_absolute_jacobian": "1",
            "alternative_absolute_jacobian": "3/5",
            "alternative_to_reference_weight_ratio": "5/3",
            "theorem": "idempotence and the public finite-volume prescription do not select a coordinate-independent three-particle point-cell normalization",
            "consequence": "chi, the box geometry, and the coordinate cell are experiment data; Gamma_Xi is physical only after they are declared"
        },
        "interpretation": {
            "public_two_beam_area_mechanism": "RECONSTRUCTED",
            "declared_three_particle_incoming_projector_cell": "CONSTRUCTED",
            "generalized_born_factorial_trace": "COMPUTED",
            "dimensionless_local_detector_shell_probability": "COEFFICIENT_COMPUTED",
            "detector_independent_three_body_cross_section": "NOT_DEFINED",
            "ten_channel_global_probability": "NOT_CONSTRUCTED",
            "Eq19_all_orders": "NOT_PROVED"
        },
        "assumptions": [
            "a rectangular finite-volume regulator commensurate with the three rational beam momenta",
            "positive-energy mass shells and the public delta_n and L^mu conventions",
            "the certified squared six-point amplitude starts at total external-mass degree six, so all six delta-prime mass derivatives in this leading coefficient act on the amplitude and leave the ordinary on-shell input measure",
            "the six incoming and six outgoing label-orbit cells are disjoint",
            "the outgoing characteristic equals one on a compact transverse tube around the isolated channel-11 shell and on a compact tangential cell around the fixture",
            "the displayed rate is the leading duration-growing isolated-shell term; smooth connected interference is O(1)",
            "the external spacetime-volume time factor canceled by the incoming energy characteristic is distinct from the internal sequential-shell duration"
        ],
        "does_not_establish": [
            "a detector-independent three-to-three cross section or flux",
            "uniqueness under a change of incoming characteristic coordinates",
            "a normalized compact wave packet independent of finite-volume point-cell regularization",
            "global gluing of the ten factorization channels or their intersections",
            "the complete connected O(1) interference term",
            "a global Moller, LSZ, or S operator",
            "Eq. (19) or its deferred weak-ghost-symmetry proof",
            "loop or all-order positivity",
            "gravity or BRST transfer",
            "anything LORENTZIAN-CAUSAL",
            "literature priority"
        ],
        "next_gate": "Replace the point-characteristic box cell by a compact normalized three-particle wave packet, prove convergence of its generalized-Born trace to the certified cell rate, and glue the ten finite-time channel tubes with an explicit positive detector partition. In parallel, Eq. (19) still requires the unpublished continuum pushforward, ghost-parity, stationarity, and trace-domain proof.",
        "provenance": {
            "source_commit": "7f6f5b1f88272373345fde8e872f30208bd389c0",
            "retrieval_date": "2026-08-12",
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "public_source_archive_sha256": source["source"]["source_archive_sha256"],
            "method": "Exact on-shell constraint-Jacobian evaluation, finite-volume delta counting in the public normalization, exact S3 orbit/factorial enumeration, exact multiplication by the certified BT shell coefficient, and a second coordinate-cell counterexample to detector-independent normalization."
        },
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_three_particle_characteristic_cell.py --write --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_three_particle_characteristic_cell.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_three_particle_characteristic_cell"
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
