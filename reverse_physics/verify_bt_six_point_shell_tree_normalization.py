#!/usr/bin/env python3
"""Independent verifier for the BT six-point shell tree normalization."""
import hashlib
import json
import os
import sys
from fractions import Fraction

import sympy as sp
from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(ROOT, "reverse_physics/certificates/REVERSE_PHYSICS_BT_SIX_POINT_SHELL_TREE_NORMALIZATION_V1.json")
SCHEMA = os.path.join(ROOT, "reverse_physics/schema/reverse-physics-bt-six-point-shell-tree-normalization-v1.schema.json")


def load(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def file_hash(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def gaussian_multiply(left, right):
    """Multiply exact Gaussian integers encoded as (real, imaginary)."""
    a, b = left
    c, d = right
    return (a * c - b * d, a * d + b * c)


def gaussian_power(value, exponent):
    out = (Fraction(1), Fraction(0))
    for _ in range(exponent):
        out = gaussian_multiply(out, value)
    return out


def independent_topology_factors():
    cubic = (Fraction(0), Fraction(-2))
    quartic = (Fraction(0), Fraction(-4))
    propagator = (Fraction(0), Fraction(-1))
    return {
        "V4_V4": gaussian_multiply(gaussian_power(quartic, 2), propagator),
        "V3_V3_V4": gaussian_multiply(
            gaussian_multiply(gaussian_power(cubic, 2), quartic),
            gaussian_power(propagator, 2),
        ),
        "V3_V3_V3_V3": gaussian_multiply(
            gaussian_power(cubic, 4), gaussian_power(propagator, 3)
        ),
    }


def verify(certificate):
    topology = certificate["tree_topology_normalization"]
    shell = certificate["finite_shell_coefficient"]
    dimensions = certificate["dimensional_and_detector_audit"]
    strength = certificate["effective_strength_split"]
    source = certificate["public_source_audit"]
    result = certificate["interpretation"]
    factors = independent_topology_factors()
    common = (Fraction(0), Fraction(16))
    density = common[0] ** 2 + common[1] ** 2
    reduced_norm = Fraction(9, 8)
    residue = density * reduced_norm
    duration, energy, coupling = sp.symbols("T E lambda", positive=True)
    finite_norm = residue * sp.pi * coupling**8 * duration / energy
    outgoing_shell_density = sp.Rational(3, 320) / (2 * sp.pi) ** 5
    phase_coefficient = sp.factor(finite_norm.subs(energy, 1) * outgoing_shell_density)
    checks = {
        "schema_validation": not list(Draft202012Validator(load(SCHEMA)).iter_errors(certificate)),
        "input_hashes_match": all(row["sha256"] == file_hash(row["path"]) for row in certificate["provenance"]["inputs"]),
        "topology_factors_recomputed_as_gaussian_integers": factors == {"V4_V4": common, "V3_V3_V4": (0, -16), "V3_V3_V3_V3": common},
        "stored_topology_signs_match": topology["reduced_recursion_relative_signs"] == [1, -1, 1],
        "common_amplitude_is_sixteen_i": topology["common_amplitude_multiplier"] == "16*i*lambda^4",
        "density_multiplier_recomputed": density == 256 and topology["common_density_multiplier"] == "256*lambda^8",
        "residue_norm_recomputed": residue == 288 and shell["BT_fixed_channel_residue_norm"] == "288*lambda^8",
        "finite_shell_norm_recomputed": finite_norm == 288 * sp.pi * coupling**8 * duration / energy,
        "phase_coefficient_recomputed": phase_coefficient == 27 * coupling**8 * duration / (320 * sp.pi**4),
        "identical_preflight_recomputed": sp.factor(phase_coefficient / 6) == 9 * coupling**8 * duration / (640 * sp.pi**4),
        "stored_phase_coefficient_matches": shell["labeled_phase_weighted_coefficient"] == "27*lambda^8*T/(320*pi^4)",
        "mass_dimension_balance_recomputed": dimensions["T_over_E_mass_dimension"] + dimensions["outgoing_shell_density_mass_dimension"] == -2,
        "incoming_weight_closes_dimension": dimensions["phase_weighted_coefficient_mass_dimension"] + dimensions["required_incoming_projector_cell_weight_mass_dimension"] == 0,
        "tree_coupling_is_dimensionless": dimensions["lambda_mass_dimension"] == 0,
        "three_particle_cell_is_fail_closed": dimensions["three_particle_public_status"] == "NO_INCOMING_CHARACTERISTIC_CELL_OR_3_TO_3_FLUX_NORMALIZATION_SPECIFIED",
        "effective_strength_split_preserved": strength["status"] == "HAMILTONIAN_PART_FIXED_INCOMING_PROJECTOR_NORMALIZATION_OPEN",
        "source_scope_is_v1": source["current_arxiv_version"] == "v1 only" and "checked Letter" in source["inference_boundary"],
        "hamiltonian_part_is_computed": result["six_point_tree_coupling_normalization"] == "COMPUTED",
        "dimensionless_probability_remains_open": result["dimensionless_three_to_three_detector_probability"] == "NOT_COMPUTED",
        "global_and_eq19_gates_remain_open": result["global_multichannel_probability"] == "NOT_CONSTRUCTED" and result["Eq19_all_orders"] == "NOT_PROVED",
        "lorentzian_boundary_is_explicit": "anything LORENTZIAN-CAUSAL" in certificate["does_not_establish"],
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
