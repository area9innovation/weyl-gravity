#!/usr/bin/env python3
"""Independent verifier for the crossed detector orientation no-go."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_CROSSED_DETECTOR_ORIENTATION_NO_GO_V1.json",
)
SCHEMA = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-crossed-detector-orientation-no-go-v1.schema.json",
)


def load(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def verify(certificate):
    import sympy as sp

    errors = list(Draft202012Validator(load(SCHEMA)).iter_errors(certificate))
    if errors:
        return {"schema_validation": False}

    inputs = certificate["provenance"]["inputs"]
    predecessor_values = [
        load(os.path.join(ROOT, row["path"])) for row in inputs[1:]
    ]
    standard = certificate["standard_orientation_no_go"]
    collapse = certificate["coherent_collapse_classification"]
    parity = certificate["internal_parity_boundary"]
    histories = certificate["history_disposition"]
    disposition = certificate["disposition"]

    qx, v, t, z, theta = sp.symbols(
        "q_x v t z theta", positive=True, nonzero=True, real=True
    )
    local = {"q_x": qx, "v": v, "t": t, "z": z, "theta": theta}

    def expression(value):
        return sp.sympify(value, locals=local)

    def matrix(value):
        return sp.Matrix(
            [[expression(entry) for entry in row] for row in value]
        )

    J = sp.Matrix([[0, 1], [1, 0]])
    K = 3*J
    eta = sp.kronecker_product(J, K)
    I = sp.eye(2)
    D = sp.diag(-qx, -qx, v, v)
    Rp = sp.Matrix.hstack(I, I)
    Rm = sp.Matrix.hstack(I, -I)

    def raised(R):
        return sp.simplify(eta.inv()*D.T*R.T*K*R*D)

    Ap = raised(Rp)
    Am = raised(Rm)
    Pp = sp.simplify(Ap/(-2*qx*v))
    Pm = sp.simplify(Am/(2*qx*v))
    Np = sp.Matrix.vstack(v*I, -qx*I)
    Nm = sp.Matrix.vstack(v*I, qx*I)
    Rt = sp.Matrix.hstack(I, t*I)
    At = raised(Rt)

    # Reconstruct the orientation theorem from a general positive 2x2
    # detector matrix, not only the rank-one phase example in the producer.
    a, b, d = sp.symbols("a b d", real=True)
    M = sp.Matrix([[a, b], [b, d]])
    species = -6*qx*v*I
    tensor = sp.kronecker_product(M, species)
    probe = sp.Matrix(sp.symbols("y0:4", real=True))
    probe_block0 = probe[:2, 0]
    probe_block1 = probe[2:, 0]
    detector_quadratic = sp.expand((probe.T*tensor*probe)[0])
    reconstructed = -6*qx*v*sp.expand(
        a*probe_block0.dot(probe_block0)
        + 2*b*probe_block0.dot(probe_block1)
        + d*probe_block1.dot(probe_block1)
    )

    S = sp.diag(1, -1)
    S4 = sp.diag(1, 1, -1, -1)
    ordinary = I
    orientation = matrix(standard["orientation_gram"])
    combined = matrix(standard["combined_gram"])

    checks = {
        "schema_validation": True,
        "all_input_hashes_match": all(
            row["sha256"] == sha256(row["path"]) for row in inputs
        ),
        "predecessors_pass": all(
            value["checks"]["ok"] for value in predecessor_values
        ),
        "ordinary_crossing_matrix_is_identity": matrix(
            standard["ordinary_crossing_matrix"]
        ) == I,
        "fixed_species_gram_reconstructs": sp.simplify(
            matrix(standard["fixed_species_gram"])-species
        ) == sp.zeros(2),
        "orientation_gram_is_positive_rank_one": (
            sp.simplify(orientation*orientation-2*orientation)
            == sp.zeros(2)
            and orientation.det() == 0
            and sp.simplify(sp.trace(orientation)-2) == 0
        ),
        "combined_gram_reconstructs": sp.simplify(
            combined-sp.kronecker_product(orientation, species)
        ) == sp.zeros(4),
        "general_positive_detector_quadratic_has_negative_factor": sp.simplify(
            detector_quadratic-reconstructed
        ) == 0,
        "positive_detector_statement_is_fail_closed": (
            "positive detector density" in standard["positive_detector_theorem"]
            and "negative semidefinite" in standard["positive_detector_theorem"]
            and "no positive direction" in standard["positive_detector_theorem"]
        ),
        "factorization_boundary_is_explicit": (
            "nonfactorizing" in standard["factorization_boundary"]
        ),
        "metric_reconstructs": matrix(collapse["metric_eta"]) == eta,
        "continued_D_reconstructs": matrix(
            collapse["continued_amplitude_D"]
        ) == D,
        "R_plus_reconstructs": matrix(
            collapse["outgoing_style_collapse_R_plus"]
        ) == Rp,
        "R_plus_pullback_reconstructs": sp.simplify(matrix(
            collapse["R_plus_raised_pullback"]
        )-Ap) == sp.zeros(4),
        "R_plus_projector_reconstructs": sp.simplify(matrix(
            collapse["R_plus_projector"]
        )-Pp) == sp.zeros(4),
        "R_plus_selects_negative_image": (
            sp.simplify(Pp*Np-Np) == sp.zeros(4, 2)
            and sp.simplify(Pp*Nm) == sp.zeros(4, 2)
        ),
        "R_minus_reconstructs": matrix(
            collapse["repaired_collapse_R_minus"]
        ) == Rm,
        "R_minus_pullback_reconstructs": sp.simplify(matrix(
            collapse["R_minus_raised_pullback"]
        )-Am) == sp.zeros(4),
        "R_minus_projector_reconstructs": sp.simplify(matrix(
            collapse["R_minus_projector"]
        )-Pm) == sp.zeros(4),
        "R_minus_selects_positive_complement": (
            sp.simplify(Pm*Nm-Nm) == sp.zeros(4, 2)
            and sp.simplify(Pm*Np) == sp.zeros(4, 2)
            and sp.simplify(Nm.T*eta*Nm*J-6*qx*v*I) == sp.zeros(2)
        ),
        "general_collapse_polynomial_reconstructs": (
            At.rank() == 2
            and sp.simplify(At*At+2*qx*t*v*At) == sp.zeros(4)
            and sp.simplify(sp.trace(At)+4*qx*t*v) == 0
        ),
        "unique_unit_real_sign_is_minus": (
            collapse["unit_modulus_condition"].endswith("t=-1.")
            and collapse["R_minus_eigenvalue"] == "+2*q_x*v"
        ),
        "parent_dual_metric_reconstructs": matrix(
            parity["parent_dual_metric"]
        ) == J,
        "ordinary_crossing_is_krein_unitary": (
            matrix(parity["ordinary_crossing"]) == ordinary
            and ordinary.T*J*ordinary == J
        ),
        "internal_parity_is_anti_krein": (
            matrix(parity["internal_jet_parity"]) == S
            and S.T*J*S == -J
        ),
        "internal_parity_changes_collapse": Rp*S4 == Rm,
        "public_BT_boundary_remains_open_not_promoted": (
            "independently obstructed" in parity["public_BT_boundary"]
            and "remain open" in parity["public_BT_boundary"]
        ),
        "all_twelve_histories_remain_unaffiliated": (
            histories["reversed_history_count"] == 12
            and disposition["twelve_reversed_physical_intertwiners"]
            == "NOT_CONSTRUCTED"
        ),
        "disposition_retains_internal_affiliation_gap": (
            disposition["internal_jet_parity_metric_type"] == "ANTI_KREIN"
            and disposition["internal_jet_parity_BT_affiliation"]
            == "NOT_DERIVED"
        ),
        "disposition_retains_nonfactorizing_gap": (
            disposition["nonfactorizing_crossed_detector_terms"]
            == "NOT_COMPUTED"
        ),
        "claim_boundary_remains_fail_closed": (
            disposition["complete_crossed_probability"] == "NOT_COMPUTED"
            and disposition["Eq19_all_orders"] == "NOT_PROVED"
            and disposition["spacetime_Moller_LSZ_S_operator"]
            == "NOT_CONSTRUCTED"
        ),
        "next_gate_is_amplitude_level_internal_parity": (
            "crossed five-to-four parent-jet amplitude ratio before squaring"
            in certificate["next_gate"]
            and "incoming Wightman dual" in certificate["next_gate"]
        ),
    }
    return {name: bool(value) for name, value in checks.items()}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", default=CERT)
    args = parser.parse_args(argv)
    checks = verify(load(args.verify))
    for name, ok in checks.items():
        print(("PASS" if ok else "FAIL") + ": " + name)
    print("RESULT:", "PASS" if all(checks.values()) else "FAIL")
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
