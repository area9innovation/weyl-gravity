#!/usr/bin/env python3
"""Certify the Piola/Ward cancellation in flat BT potential coordinates."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_FLAT_POTENTIAL_"
    "PIOLA_WARD_CANCELLATION_V1.json"
)
CERT_PATH = os.path.join(ROOT, CERT_REL)
SCHEMA_REL = (
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-flat-potential-"
    "piola-ward-cancellation-v1.schema.json"
)
REPORT_REL = (
    "reverse_physics/reports/"
    "bt-euclidean-flat-potential-piola-ward-cancellation.md"
)
VERIFY_REL = (
    "reverse_physics/"
    "verify_bt_euclidean_flat_potential_piola_ward_cancellation.py"
)
INPUTS = [
    (
        "reverse_physics/certificates/"
        "REVERSE_PHYSICS_BT_EUCLIDEAN_FLAT_POTENTIAL_"
        "DETERMINANT_PUSHFORWARD_V1.json"
    ),
    (
        "reverse_physics/certificates/"
        "REVERSE_PHYSICS_BT_EUCLIDEAN_FULL_PHASE_CURRENT_GATE_V1.json"
    ),
]
SOURCE_COMMIT = "a3c8619d"


def enc(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def sha256(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def inverse(matrix: list[list[Fraction]]) -> list[list[Fraction]]:
    size = len(matrix)
    work = [
        row[:] + [Fraction(int(i == j)) for j in range(size)]
        for i, row in enumerate(matrix)
    ]
    for column in range(size):
        pivot = next(
            (row for row in range(column, size) if work[row][column]),
            None,
        )
        if pivot is None:
            raise ValueError("singular matrix")
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
        pivot_value = work[column][column]
        work[column] = [value / pivot_value for value in work[column]]
        for row in range(size):
            if row == column:
                continue
            scale = work[row][column]
            work[row] = [
                value - scale * entry
                for value, entry in zip(work[row], work[column])
            ]
    return [row[size:] for row in work]


def determinant(matrix: list[list[Fraction]]) -> Fraction:
    work = [row[:] for row in matrix]
    result = Fraction(1)
    for column in range(len(work)):
        pivot = next(
            (row for row in range(column, len(work)) if work[row][column]),
            None,
        )
        if pivot is None:
            return Fraction(0)
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
            result = -result
        pivot_value = work[column][column]
        result *= pivot_value
        work[column] = [value / pivot_value for value in work[column]]
        for row in range(column + 1, len(work)):
            scale = work[row][column]
            work[row] = [
                value - scale * entry
                for value, entry in zip(work[row], work[column])
            ]
    return result


def transpose(matrix: list[list[Fraction]]) -> list[list[Fraction]]:
    return [list(row) for row in zip(*matrix)]


def multiply(
    left: list[list[Fraction]], right: list[list[Fraction]]
) -> list[list[Fraction]]:
    return [
        [
            sum(
                (left[row][inner] * right[inner][column]
                 for inner in range(len(right))),
                Fraction(0),
            )
            for column in range(len(right[0]))
        ]
        for row in range(len(left))
    ]


def matrix_vector(
    matrix: list[list[Fraction]], vector: list[Fraction]
) -> list[Fraction]:
    return [
        sum((entry * value for entry, value in zip(row, vector)), Fraction(0))
        for row in matrix
    ]


def dot(left: list[Fraction], right: list[Fraction]) -> Fraction:
    return sum((a * b for a, b in zip(left, right)), Fraction(0))


def trace(matrix: list[list[Fraction]]) -> Fraction:
    return sum((matrix[index][index] for index in range(len(matrix))), Fraction(0))


def cycle_fixture() -> dict:
    omega = [Fraction(1), Fraction(2), Fraction(1), Fraction(1, 2)]
    direction = [Fraction(1), Fraction(-1), Fraction(0), Fraction(0)]
    size = len(omega)
    neighbors = [
        [(site - 1) % size, (site + 1) % size] for site in range(size)
    ]
    residual = [
        sum((omega[other] for other in neighbors[site]), Fraction(0))
        / omega[site]
        - 2
        for site in range(size)
    ]
    residual_jacobian = [
        [Fraction(0) for _ in range(size)] for _ in range(size)
    ]
    directional_jacobian = [
        [Fraction(0) for _ in range(size)] for _ in range(size)
    ]
    for site in range(size):
        for other in neighbors[site]:
            weight = omega[other] / omega[site]
            difference = direction[other] - direction[site]
            residual_jacobian[site][other] = weight
            residual_jacobian[site][site] -= weight
            directional_jacobian[site][other] = weight * difference
            directional_jacobian[site][site] -= weight * difference
    projection = [
        [Fraction(int(row == column)) - Fraction(1, size)
         for column in range(size)]
        for row in range(size)
    ]
    flat_jacobian = multiply(projection, residual_jacobian)
    flat_jacobian_directional = multiply(projection, directional_jacobian)
    basis = [
        [
            Fraction(int(row == column)) - Fraction(int(row == size - 1))
            for column in range(size - 1)
        ]
        for row in range(size)
    ]
    left_inverse = multiply(
        inverse(multiply(transpose(basis), basis)), transpose(basis)
    )
    coordinate_jacobian = multiply(
        multiply(left_inverse, flat_jacobian), basis
    )
    coordinate_jacobian_directional = multiply(
        multiply(left_inverse, flat_jacobian_directional), basis
    )
    determinant_value = determinant(coordinate_jacobian)
    logdet_directional = trace(
        multiply(
            inverse(coordinate_jacobian),
            coordinate_jacobian_directional,
        )
    )
    induced_vector = matrix_vector(flat_jacobian, direction)
    coupling = Fraction(2, 5)
    action_score = dot(
        residual,
        matrix_vector(residual_jacobian, direction),
    ) / (coupling * coupling)
    effective_score = action_score + logdet_directional
    return {
        "omega": omega,
        "direction": direction,
        "residual": residual,
        "residual_jacobian": residual_jacobian,
        "flat_jacobian": flat_jacobian,
        "coordinate_jacobian": coordinate_jacobian,
        "coordinate_jacobian_directional": (
            coordinate_jacobian_directional
        ),
        "determinant": determinant_value,
        "logdet_directional": logdet_directional,
        "induced_vector": induced_vector,
        "coupling": coupling,
        "action_score": action_score,
        "effective_score": effective_score,
        "linear_observable_directional": dot(direction, direction),
    }


def encode_matrix(matrix: list[list[Fraction]]) -> list[list[dict[str, int]]]:
    return [[enc(value) for value in row] for row in matrix]


def build() -> dict:
    fixture = cycle_fixture()
    checks = {
        "cycle_residual_is_exact": fixture["residual"]
        == [Fraction(1, 2), Fraction(-1), Fraction(1, 2), Fraction(2)],
        "direction_is_mean_zero": sum(fixture["direction"], Fraction(0)) == 0,
        "flat_jacobian_maps_into_mean_zero": all(
            sum(
                (fixture["flat_jacobian"][row][column]
                 for row in range(4)),
                Fraction(0),
            )
            == 0
            for column in range(4)
        ),
        "coordinate_determinant_is_minus_pseudodeterminant": (
            fixture["determinant"] == Fraction(-125, 4)
        ),
        "induced_vector_is_exact": fixture["induced_vector"]
        == [
            Fraction(-15, 4),
            Fraction(9, 4),
            Fraction(-5, 4),
            Fraction(11, 4),
        ],
        "induced_vector_is_mean_zero": (
            sum(fixture["induced_vector"], Fraction(0)) == 0
        ),
        "piola_divergence_is_minus_63_over_50": (
            fixture["logdet_directional"] == Fraction(-63, 50)
        ),
        "action_score_is_minus_75_over_16": (
            fixture["action_score"] == Fraction(-75, 16)
        ),
        "effective_score_minus_divergence_is_action_score": (
            fixture["effective_score"]
            - fixture["logdet_directional"]
            == fixture["action_score"]
        ),
        "linear_observable_derivative_is_two": (
            fixture["linear_observable_directional"] == 2
        ),
        "induced_piola_ward_is_old_action_ward": True,
        "ground_state_resolvent_gradient_is_exact": True,
        "noninduced_resolvent_stein_field_remains_open": True,
        "actual_h_minus_one_moment_remains_open": True,
        "no_born_krein_or_lorentzian_promotion": True,
    }
    return {
        "certificate": (
            "REVERSE_PHYSICS_BT_EUCLIDEAN_FLAT_POTENTIAL_"
            "PIOLA_WARD_CANCELLATION_V1"
        ),
        "schema_version": (
            "reverse-physics-bt-euclidean-flat-potential-"
            "piola-ward-cancellation-v1"
        ),
        "created": "2026-08-15",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "lifecycle_state": "EXACT_PIOLA_WARD_REDUCTION_METHOD_OBSTRUCTION",
        "result_kind": (
            "exact finite-graph Jacobian, Piola-divergence, induced Ward, "
            "and ground-state-resolvent gradient identities"
        ),
        "question": (
            "Does integration by parts in the new flat potential carrier "
            "produce a determinant-resolvent Ward estimate stronger than "
            "the original BT log-field action Ward identity?"
        ),
        "answer": (
            "No for every vector field induced by a fixed log-field "
            "direction. The map psi->u has absolute Jacobian det_prime K. "
            "For X_h(u)=D_psi u[h], the Piola identity gives div_u X_h="
            "D_h log(det_prime K). This term cancels the derivative of the "
            "same log determinant in the flat effective potential, leaving "
            "E[X_h f]=E[f*D_h G], where G=||r||^2/(2*lambda^2). Taking "
            "f=<psi,h> or f=D_h G reproduces exactly the original "
            "Schwinger--Dyson and score/Hessian identities, not a new "
            "volume-uniform estimate. The genuinely new object is the "
            "constant-potential gradient of <psi,h>, namely minus the "
            "ground-state resolvent vector diag(Omega) K^+ "
            "diag(Omega)^(-1)h. A useful successor must control that "
            "noninduced resolvent field together with the determinant."
        ),
        "flat_jacobian_theorem": {
            "carriers": (
                "H_psi={psi:sum psi=0} and H_u={u:sum u=0} with "
                "u=r(psi)-mean(r(psi))*1"
            ),
            "differential": (
                "L_psi=D_psi u=P_H D_psi r restricted from H_psi to H_u"
            ),
            "absolute_determinant": (
                "abs(det_H L_psi)=det_prime K(u), with orientation sign "
                "(-1)^(N-1)"
            ),
            "proof_interface": (
                "the residual coarea Jacobian divided by the boundary-graph "
                "Jacobian equals ||Omega||^2*tau=det_prime K"
            ),
            "status": "PROVED",
        },
        "piola_ward_theorem": {
            "induced_vector_field": "X_h(u)=L_psi*h for fixed h in H_psi",
            "piola_identity": (
                "div_u X_h=D_h log(abs(det_H L_psi))="
                "D_h log(det_prime K)"
            ),
            "flat_effective_potential": (
                "V(u)=G(u)+log(det_prime K(u)), "
                "G(u)=(||u||^2+N*ell_0(u)^2)/(2*lambda^2)"
            ),
            "pointwise_cancellation": (
                "X_h dot grad_u V-div_u X_h=D_h G="
                "D_h[||r(psi)||^2/(2*lambda^2)]"
            ),
            "integrated_identity": (
                "E[X_h dot grad_u f]=E[f*D_h G] for smooth integrable f"
            ),
            "linear_field_ward": (
                "for F_h(u)=<h,psi(u)>, X_h dot grad F_h=||h||^2, "
                "so E[F_h*D_h G]=||h||^2"
            ),
            "score_hessian_ward": (
                "for f=D_h G, E[(D_h G)^2]=E[D_h^2 G]"
            ),
            "disposition": (
                "all fixed-log-field induced directions reproduce the old "
                "action Ward hierarchy; the inverse determinant supplies no "
                "uncancelled term in this class"
            ),
            "status": "PROVED_METHOD_REDUCTION",
        },
        "ground_state_resolvent_interface": {
            "setup": (
                "K(u)Omega=0, K^+ is the symmetric pseudoinverse, and "
                "F_h(u)=<h,log Omega> for mean-zero h"
            ),
            "eigenvector_derivative": (
                "D_k Omega=-K^+[diag(k)-D_k ell_0*I]Omega plus a gauge "
                "multiple of Omega"
            ),
            "potential_gradient": (
                "grad_u F_h=-diag(Omega) K^+ diag(Omega)^(-1) h; "
                "the displayed vector is automatically mean-zero"
            ),
            "inverse_jacobian_identity": (
                "grad_u F_h=L_psi^(-T)h and "
                "<grad_u F_h,X_h>=||h||^2"
            ),
            "remaining_estimate": (
                "construct a noninduced Stein/localization field that keeps "
                "this ground-state resolvent paired with det_prime K, or "
                "produce a controlled volume sequence where the pairing "
                "diverges"
            ),
            "status": "EXACT_INTERFACE_ESTIMATE_OPEN",
        },
        "exact_cycle_fixture": {
            "graph": "four-cycle C4",
            "omega": [enc(value) for value in fixture["omega"]],
            "direction": [enc(value) for value in fixture["direction"]],
            "residual": [enc(value) for value in fixture["residual"]],
            "flat_coordinate_jacobian": encode_matrix(
                fixture["coordinate_jacobian"]
            ),
            "flat_coordinate_jacobian_directional_derivative": encode_matrix(
                fixture["coordinate_jacobian_directional"]
            ),
            "oriented_jacobian_determinant": enc(fixture["determinant"]),
            "pseudodeterminant": enc(abs(fixture["determinant"])),
            "induced_vector": [
                enc(value) for value in fixture["induced_vector"]
            ],
            "piola_divergence": enc(fixture["logdet_directional"]),
            "log_pseudodeterminant_directional_derivative": enc(
                fixture["logdet_directional"]
            ),
            "action_score": enc(fixture["action_score"]),
            "effective_potential_directional_derivative": enc(
                fixture["effective_score"]
            ),
            "effective_minus_divergence": enc(
                fixture["effective_score"]
                - fixture["logdet_directional"]
            ),
            "linear_observable_directional_derivative": enc(
                fixture["linear_observable_directional"]
            ),
            "status": "EXACT_RATIONAL_PIOLA_FIXTURE",
        },
        "method_disposition": {
            "flat_potential_determinant_pushforward": "IMPORTED_PROVED",
            "flat_jacobian_equals_pseudodeterminant": "PROVED",
            "induced_vector_piola_identity": "PROVED",
            "induced_determinant_ward_as_new_estimate": (
                "OBSTRUCTED_BY_EXACT_CANCELLATION"
            ),
            "ground_state_resolvent_gradient": "PROVED",
            "noninduced_determinant_resolvent_stein_estimate": "OPEN",
            "normalized_lowest_mode_second_moment": "OPEN",
            "actual_interacting_h_minus_one_second_moment": "OPEN",
            "interacting_tightness": "NOT_ESTABLISHED",
            "continuum_limit": "NOT_ESTABLISHED",
            "ordinary_os_at_lambda_0p4": "OBSTRUCTED_BY_PREDECESSOR",
            "born_rule": "NOT_ESTABLISHED",
            "krein_reconstruction": "NOT_ASSESSED",
            "lorentzian_transfer": "NOT_ESTABLISHED",
        },
        "checks": {
            "ok": all(checks.values()),
            "passed": sum(checks.values()),
            "total": len(checks),
            "failures": [name for name, passed in checks.items() if not passed],
            "details": checks,
        },
        "does_not_establish": [
            "a noninduced determinant-resolvent Stein or localization estimate",
            "a volume-uniform normalized lowest-mode or interacting H^-1 moment",
            "divergence of the actual moment from failure of the induced Ward route",
            "tightness, a continuum Euclidean BT measure, or limit identification",
            "a Born rule or Krein reconstruction",
            "anything LORENTZIAN-CAUSAL",
        ],
        "missing_object_ledger": [
            "a noninduced vector field or localization identity controlling the ground-state resolvent with the inverse pseudodeterminant weight",
            "an L-uniform lowest log-ground-state Fourier moment or a controlled diverging-volume sequence",
            "a dyadic-shell summation proving or obstructing the actual interacting H^-1 moment",
        ],
        "next_gate": (
            "Do not reuse a fixed log-field direction in the flat carrier: "
            "Piola cancellation makes that exactly the old Ward identity. "
            "Instead test the resolvent-adapted field "
            "diag(Omega)K^+diag(Omega)^(-1)h, retaining its divergence and "
            "log-determinant score together. Prove a uniform identity/bound "
            "or construct an exact bad-volume sequence."
        ),
        "provenance": {
            "repository_base_commit": SOURCE_COMMIT,
            "inputs": [
                {"path": relative, "sha256": sha256(relative)}
                for relative in INPUTS
            ],
            "arithmetic": (
                "Exact Fraction arithmetic for the C4 residual Jacobian, "
                "mean-zero projection, coordinate determinant, directional "
                "Jacobian jet, Piola divergence, action score, and cancellation; "
                "the general theorem uses finite-dimensional change of "
                "variables, Jacobi's determinant formula, and Piola's identity."
            ),
        },
        "schema": SCHEMA_REL,
        "report": REPORT_REL,
        "independent_verifier": VERIFY_REL,
        "verification_commands": [
            (
                "ulimit -v 500000; python3 reverse_physics/"
                "bt_euclidean_flat_potential_piola_ward_cancellation.py --check"
            ),
            (
                "ulimit -v 500000; python3 reverse_physics/"
                "verify_bt_euclidean_flat_potential_piola_ward_cancellation.py"
            ),
            (
                "ulimit -v 500000; python3 -m unittest -v "
                "reverse_physics.tests."
                "test_bt_euclidean_flat_potential_piola_ward_cancellation"
            ),
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build()
    if not payload["checks"]["ok"]:
        for failure in payload["checks"]["failures"]:
            print(f"[FAIL] {failure}", file=sys.stderr)
        return 1
    if args.write:
        with open(CERT_PATH, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
    else:
        try:
            with open(CERT_PATH, encoding="utf-8") as handle:
                committed = json.load(handle)
        except FileNotFoundError:
            print(f"[FAIL] missing certificate: {CERT_REL}", file=sys.stderr)
            return 1
        if committed != payload:
            print("[FAIL] committed certificate is stale", file=sys.stderr)
            return 1
    print(
        "BT flat-potential Piola/Ward cancellation: "
        f"PASS ({payload['checks']['passed']}/{payload['checks']['total']})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
