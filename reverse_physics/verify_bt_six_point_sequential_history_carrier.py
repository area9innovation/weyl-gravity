#!/usr/bin/env python3
"""Independent verification of the BT sequential-history channel carrier."""
import hashlib
import json
import os
import sys

import sympy as sp
from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(ROOT, "reverse_physics/certificates/REVERSE_PHYSICS_BT_SIX_POINT_SEQUENTIAL_HISTORY_CARRIER_V1.json")
SCHEMA = os.path.join(ROOT, "reverse_physics/schema/reverse-physics-bt-six-point-sequential-history-carrier-v1.schema.json")


def load(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def file_hash(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def parsed_matrix(rows):
    return sp.Matrix([[sp.Rational(value) for value in row] for row in rows])


def verify(certificate):
    size = 10
    incidence = sp.Matrix(size, size, lambda i, j: int(i != j))
    residue = incidence / 4
    gram = 2 * residue.T * residue
    sequential = sp.Rational(9, 8) * sp.eye(size)
    interference = gram - sequential
    carrier = certificate["exact_channel_carrier"]
    boundary = certificate["sequential_interference_boundary"]
    finite = certificate["finite_time_shell_normalization"]
    interpretation = certificate["interpretation"]
    omega, duration, energy = sp.symbols("omega T E", positive=True)
    window_norm = sp.integrate(
        4 * sp.sin(omega * duration / 2) ** 2 / omega**2,
        (omega, -sp.oo, sp.oo),
    )
    shell_coefficient = sp.simplify(
        (2 * sp.pi * duration) / (4 * energy**2) * (2 * energy)
    )
    checks = {
        "schema_validation": not list(Draft202012Validator(load(SCHEMA)).iter_errors(certificate)),
        "all_input_hashes_match": all(row["sha256"] == file_hash(row["path"]) for row in certificate["provenance"]["inputs"]),
        "incidence_recomputed": parsed_matrix(carrier["incidence_matrix"]) == incidence,
        "residue_inverse_recomputed": parsed_matrix(carrier["residue_map_inverse"]) == residue.inv(),
        "gram_recomputed": parsed_matrix(carrier["complete_channel_gram"]) == gram,
        "gram_determinant_recomputed": sp.Rational(carrier["complete_channel_gram_determinant"]) == gram.det(),
        "gram_spectrum_recomputed": gram.eigenvals() == {sp.Rational(81, 8): 1, sp.Rational(1, 8): 9},
        "fixed_residue_norm_recomputed": (2 * residue[:, 0].dot(residue[:, 0])) == sp.Rational(9, 8),
        "interference_recomputed": parsed_matrix(carrier["interference_gram"]) == interference,
        "interference_inertia_recomputed": interference.eigenvals() == {sp.Integer(9): 1, sp.Integer(-1): 9},
        "double_poles_are_diagonal": all(sequential[i, j] == 0 for i in range(size) for j in range(size) if i != j),
        "finite_time_normalization_is_typed": finite["status"] == "UNIVERSAL_FINITE_TIME_NORMALIZATION_NOT_BT_DYNAMICAL_AFFILIATION",
        "finite_time_total_weight_recomputed": window_norm == 2 * sp.pi * duration,
        "shell_jacobian_coefficient_is_consistent": shell_coefficient == sp.pi * duration / energy and finite["coefficient_match"] == "epsilon_s=E/T" and finite["BT_leading_sequential_history"] == "(9*pi*T/(8*E))*delta(s)",
        "interference_is_not_promoted": "indefinite" in boundary["connected_interference"] and interpretation["connected_interference_distribution"] == "NOT_PRESCRIBED",
        "physical_completion_remains_open": interpretation["BT_dynamical_Moller_affiliation"] == "NOT_CONSTRUCTED" and interpretation["finite_inclusive_probability"] == "NOT_CONSTRUCTED",
        "claim_boundary_is_preserved": "anything LORENTZIAN-CAUSAL" in certificate["does_not_establish"] and interpretation["Eq19_all_orders"] == "NOT_PROVED",
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
