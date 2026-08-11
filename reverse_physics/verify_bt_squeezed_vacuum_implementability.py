#!/usr/bin/env python3
"""Independent verifier for the BT squeezed-vacuum topology obstruction."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_SQUEEZED_VACUUM_IMPLEMENTABILITY_V1.json",
)
SCHEMA = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-squeezed-vacuum-implementability-v1.schema.json",
)


def load(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def fraction(value):
    return Fraction(value["numerator"], value["denominator"])


def sha256(relative_path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative_path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def multiply(left, right):
    return [
        [sum(left[i][k] * right[k][j] for k in range(2)) for j in range(2)]
        for i in range(2)
    ]


def verify(path):
    certificate = load(path)
    schema = load(SCHEMA)
    checks = {}

    checks["strict_schema"] = not list(
        Draft202012Validator(schema).iter_errors(certificate)
    )

    # Classify a charge-exchanging 2x2 fundamental symmetry without importing
    # the producer: kappa=[[0,a],[b,0]], J=[[0,1],[1,0]].
    # Involution gives ab=1 and J*kappa=diag(b,a), so positivity gives a,b>0.
    family = certificate.get("fundamental_symmetry_family", {})
    j = [[Fraction(0), Fraction(1)], [Fraction(1), Fraction(0)]]
    independent_fixtures = []
    for rho in (Fraction(1, 2), Fraction(1), Fraction(2), Fraction(3)):
        kappa = [[Fraction(0), rho], [1 / rho, Fraction(0)]]
        metric = multiply(j, kappa)
        independent_fixtures.append((rho, multiply(kappa, kappa), metric))
    identity = [[Fraction(1), Fraction(0)], [Fraction(0), Fraction(1)]]
    checks["independent_fundamental_symmetry_classification"] = (
        family.get("kappa_rho") == [["0", "rho"], ["rho^-1", "0"]]
        and family.get("positive_Hilbert_metric_J_kappa")
        == [["rho^-1", "0"], ["0", "rho"]]
        and all(square == identity for _, square, _ in independent_fixtures)
        and all(metric[0][0] > 0 and metric[1][1] > 0 for _, _, metric in independent_fixtures)
    )

    # Reconstruct all finite-box factors directly from the published 1/2 and
    # (2p)^-3 factors plus two b=sqrt(2pV)c normalizations.
    paper_half = Fraction(1, 2)
    denominator = Fraction(1, 8)
    two_mode_normalizations = Fraction(2)
    ordered_q = paper_half * denominator * two_mode_normalizations
    unordered_amplitude = 2 * ordered_q
    ordered_norm = unordered_amplitude**2 / 2
    finite = certificate.get("finite_box_carrier", {})
    norm = certificate.get("direct_vacuum_norm", {})
    checks["independent_finite_box_normalization"] = (
        ordered_q == Fraction(1, 8)
        and unordered_amplitude == Fraction(1, 4)
        and ordered_norm == Fraction(1, 32)
        and fraction(finite.get("ordered_Q_coefficient", {})) == ordered_q
        and fraction(finite.get("unordered_pair_amplitude", {})) == unordered_amplitude
        and fraction(norm.get("ordered_sum_coefficient", {})) == ordered_norm
    )

    # Wick contraction: the ordered p and -p summands combine before squaring.
    # The continuum density uses 4*pi/(2*pi)^3=(1/2)pi^-2.
    sphere_measure = Fraction(1, 2)
    density = ordered_norm * sphere_measure
    checks["independent_two_particle_norm"] = (
        density == Fraction(1, 64)
        and fraction(norm.get("density_coefficient_times_pi_minus_two", {})) == density
        and norm.get("radial_integrand_power") == 2 - 4 == -2
        and norm.get("infrared_disposition") == "DIVERGES_AS_EPSILON_INVERSE"
        and norm.get("ultraviolet_disposition") == "CONVERGES_AS_LAMBDA_TO_INFINITY"
    )

    # The six vectors +/-e_i form the lowest nonzero shell. Substitution of
    # p_min=2*pi/L into the ordered norm gives 3/(256*pi^4) m^2 L^4.
    lowest = norm.get("lowest_shell", {})
    shell = Fraction(6) * ordered_norm / 16
    checks["independent_lowest_shell_bound"] = (
        shell == Fraction(3, 256)
        and lowest.get("ordered_momentum_count") == 6
        and fraction(lowest.get("coefficient_times_pi_minus_four", {})) == shell
        and lowest.get("density_lower_bound") == "3m^2 L/(256pi^4)"
    )

    # A commutator can hit either creator. Hence beta=2*(1/8)p^-2 and
    # beta^2=1/16 p^-4, exactly twice the direct ordered norm.
    pair = certificate.get("pair_block_cross_check", {})
    beta = 2 * ordered_q
    hs = beta**2
    hs_density = hs * sphere_measure
    checks["independent_pair_block"] = (
        beta == Fraction(1, 4)
        and hs == Fraction(1, 16)
        and hs == 2 * ordered_norm
        and hs_density == Fraction(1, 32)
        and fraction(pair.get("beta_coefficient", {})) == beta
        and fraction(pair.get("ordered_Hilbert_Schmidt_coefficient", {})) == hs
        and fraction(pair.get("density_coefficient_times_pi_minus_two", {})) == hs_density
        and "density itself" in pair.get("volume_boundary", "")
        and pair.get("disposition") == "NOT_HILBERT_SCHMIDT_IN_THE_MASSLESS_IR_LIMIT"
    )

    topology = certificate.get("topology_boundary", {})
    checks["independent_equivalent_topology_boundary"] = (
        family.get("uniform_equivalence_condition")
        == "there exist constants 0<m<=rho(p)<=M<infinity"
        and topology.get("integrability_condition") == "alpha>1/2"
        and "rho^-1 unbounded" in topology.get("why_not_a_repair_here", "")
    )

    nullity = certificate.get("Krein_nullity_audit", {})
    disposition = certificate.get("disposition", {})
    checks["nullity_and_claim_boundary"] = (
        nullity.get("conclusion")
        == "KREIN_NULL_DOES_NOT_IMPLY_A_VECTOR_IN_THE_POSITIVE_FOCK_TOPOLOGY"
        and disposition.get("massless_infinite_volume_positive_topology_vector")
        == "OBSTRUCTED_ON_ORDINARY_FOCK_KREIN_CARRIER"
        and disposition.get("ordinary_Fock_Bogoliubov_implementer")
        == "OBSTRUCTED_BY_NON_HILBERT_SCHMIDT_PAIR_BLOCK"
        and disposition.get("local_operator_algebra_homomorphism") == "NOT_REFUTED"
        and disposition.get("Eq19_in_extended_representation") == "NOT_DECIDED"
        and disposition.get("physical_neutral_one_over_48") == "NOT_ESTABLISHED"
    )

    zero_mode = certificate.get("zero_mode_completion", {})
    checks["zero_mode_scope"] = (
        zero_mode.get("disposition")
        == "DOES_NOT_CURE_THE_RADIAL_DIVERGENCE_ON_THAT_CANDIDATE_MODULE"
        and "not the |p|^-2 pair amplitude" in zero_mode.get("effect_on_squeeze", "")
        and "not analyzed" in zero_mode.get("caveat", "")
    )

    inputs = certificate.get("provenance", {}).get("inputs", [])
    checks["input_hashes"] = len(inputs) == 4 and all(
        item.get("sha256") == sha256(item.get("path", "")) for item in inputs
    )

    exclusions = certificate.get("does_not_establish", [])
    checks["fail_closed_exclusions"] = (
        any("Eq. (19) is false" in item for item in exclusions)
        and any("finite-volume" in item for item in exclusions)
        and any("LORENTZIAN-CAUSAL" in item for item in exclusions)
        and len(certificate.get("missing_object_ledger", [])) >= 6
    )

    ok = all(checks.values())
    for name, value in checks.items():
        print(f"[{'PASS' if value else 'FAIL'}] {name}")
    print(f"RESULT: {'PASS' if ok else 'FAIL'} ({sum(checks.values())}/{len(checks)})")
    return ok


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", default=CERT)
    args = parser.parse_args(argv)
    return 0 if verify(args.verify) else 1


if __name__ == "__main__":
    sys.exit(main())
