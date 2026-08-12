#!/usr/bin/env python3
"""Independent checks of the typed BT six-point history incidence isometry."""
import hashlib
import json
import os
import sys

import sympy as sp
from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(ROOT, "reverse_physics/certificates/REVERSE_PHYSICS_BT_SIX_POINT_HISTORY_INCIDENCE_ISOMETRY_V1.json")
SCHEMA = os.path.join(ROOT, "reverse_physics/schema/reverse-physics-bt-six-point-history-incidence-isometry-v1.schema.json")


def load(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def file_hash(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def permutation_matrix(permutation):
    size = len(permutation)
    return sp.SparseMatrix(size, size, {(permutation[index], index): 1 for index in range(size)})


def independently_construct():
    edges = []
    for species in range(10):
        for channel in range(10):
            if channel != species:
                edges.append((species, channel))
    edge_index = {edge: index for index, edge in enumerate(edges)}
    W = sp.SparseMatrix(90, 10, {(edge_index[(species, channel)], channel): sp.Rational(1, 3) for species, channel in edges})
    C = sp.SparseMatrix(10, 90, {(species, edge_index[(species, channel)]): 1 for species, channel in edges})
    return edges, edge_index, W, C


def equivariance(permutation, edges, edge_index, W, C):
    P = permutation_matrix(permutation)
    history_permutation = [edge_index[(permutation[species], permutation[channel])] for species, channel in edges]
    Q = permutation_matrix(history_permutation)
    return Q * W == W * P and P * C == C * Q


def verify(certificate):
    edges, edge_index, W, C = independently_construct()
    I10, I90 = sp.eye(10), sp.eye(90)
    B = sp.Rational(3, 4) * W
    residue = C * B
    Pcoh = C.T * C / 9
    Phist = W * W.T
    generator = sp.SparseMatrix.vstack(
        sp.SparseMatrix.hstack(sp.zeros(10), -W.T),
        sp.SparseMatrix.hstack(W, sp.zeros(90)),
    )
    mu, q = sp.symbols("mu q", real=True)
    Pmu = ((1 - mu) * I90 + mu * C.T * C) / 9
    pullback = sp.simplify(W.T * Pmu * W)
    expected_pullback = ((9 - 8 * mu) * I10 + 8 * mu * sp.ones(10)) / 81
    complete_effect = sp.simplify((1 - q) * I10 + q * W.T * Pmu * W + q * W.T * (I90 - Pmu) * W)
    listed_edges = [(row["species_assignment"], row["intermediate_channel"]) for row in certificate["typed_history_carrier"]["allowed_histories"]]
    edge_hash = hashlib.sha256(json.dumps(certificate["typed_history_carrier"]["allowed_histories"], sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    roots = sp.solve(9 * sp.Symbol("w", real=True) ** 2 - 1)
    checks = {
        "schema_validation": not list(Draft202012Validator(load(SCHEMA)).iter_errors(certificate)),
        "all_input_hashes_match": all(row["sha256"] == file_hash(row["path"]) for row in certificate["provenance"]["inputs"]),
        "history_ledger_reconstructed": listed_edges == edges and len(set(edges)) == 90,
        "history_ledger_hash_matches": edge_hash == certificate["typed_history_carrier"]["allowed_histories_sha256"],
        "isometry_reconstructed": W.T * W == I10,
        "collapse_reconstructs_residue": residue == (sp.ones(10) - I10) / 4,
        "collapse_normalization_reconstructed": (C / 3) * (C / 3).T == I10,
        "history_projection_reconstructed": Phist**2 == Phist and Phist.rank() == 10,
        "coherent_projection_reconstructed": Pcoh**2 == Pcoh and Pcoh.rank() == 10,
        "range_is_transverse_to_collapse_kernel": (C * W).det() != 0,
        "cycle_equivariance": equivariance(list(range(1, 10)) + [0], edges, edge_index, W, C),
        "transposition_equivariance": equivariance([1, 0] + list(range(2, 10)), edges, edge_index, W, C),
        "nonnegative_equal_edge_weight_is_unique": roots == [-sp.Rational(1, 3), sp.Rational(1, 3)] and max(roots) == sp.Rational(1, 3),
        "resolved_and_coherent_grams_reconstructed": 2 * B.T * B == sp.Rational(9, 8) * I10 and 2 * B.T * C.T * C * B == sp.ones(10) + sp.Rational(1, 8) * I10,
        "signed_interference_is_their_difference": 2 * B.T * (C.T * C - I90) * B == sp.ones(10) - I10,
        "normalized_effect_pullback_reconstructed": pullback == expected_pullback,
        "normalized_effect_endpoint_spectra": Pmu.subs(mu, 0).eigenvals() == {sp.Rational(1, 9): 90} and Pmu.subs(mu, 1).eigenvals() == {1: 10, 0: 80},
        "normalized_effect_complement_endpoints_are_positive": (I90 - Pmu.subs(mu, 0)).is_positive_semidefinite and (I90 - Pmu.subs(mu, 1)).is_positive_semidefinite,
        "skew_generator_reconstructed": generator.T == -generator and generator**3 == -generator,
        "three_effect_completeness_reconstructed": complete_effect == I10,
        "finite_instrument_is_not_spacetime_promoted": certificate["finite_channel_instrument"]["status"] == "EXACT_NORMALIZED_FINITE_CHANNEL_LABEL_INSTRUMENT_NOT_BT_TIME_AFFILIATED",
        "defect_and_physical_gates_remain_open": certificate["moller_defect_relation"]["global_status"] == "NOT_FIXED" and certificate["interpretation"]["finite_inclusive_probability"] == "NOT_CONSTRUCTED",
        "claim_boundary_is_preserved": "anything LORENTZIAN-CAUSAL" in certificate["does_not_establish"] and certificate["interpretation"]["Eq19_all_orders"] == "NOT_PROVED",
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
