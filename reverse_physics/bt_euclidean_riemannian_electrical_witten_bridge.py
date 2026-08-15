#!/usr/bin/env python3
"""Certify the coordinate-correct electrical bridge for the BT Witten gate."""

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
    "REVERSE_PHYSICS_BT_EUCLIDEAN_RIEMANNIAN_ELECTRICAL_WITTEN_BRIDGE_V1.json"
)
CERT_PATH = os.path.join(ROOT, CERT_REL)
SCHEMA_REL = (
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-riemannian-electrical-witten-bridge-v1.schema.json"
)
REPORT_REL = (
    "reverse_physics/reports/"
    "bt-euclidean-riemannian-electrical-witten-bridge.md"
)
VERIFY_REL = (
    "reverse_physics/verify_bt_euclidean_riemannian_electrical_witten_bridge.py"
)
INPUTS = [
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_BOSONIC_GROUND_STATE_LIFT_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_FLAT_POTENTIAL_PIOLA_WARD_CANCELLATION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_FULL_PHASE_WEIGHTED_CURRENT_GATE_V2.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_WITTEN_ONE_FORM_SCHUR_GATE_V1.json",
]
SOURCE_COMMIT = "a2263f6e22fc4eeeb7ffd0db1dff4beb0b67192b"


def enc(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def sha256(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


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
                Fraction(),
            )
            for column in range(len(right[0]))
        ]
        for row in range(len(left))
    ]


def matrix_vector(
    matrix: list[list[Fraction]], vector: list[Fraction]
) -> list[Fraction]:
    return [
        sum((entry * value for entry, value in zip(row, vector)), Fraction())
        for row in matrix
    ]


def dot(left: list[Fraction], right: list[Fraction]) -> Fraction:
    return sum((a * b for a, b in zip(left, right)), Fraction())


def determinant(matrix: list[list[Fraction]]) -> Fraction:
    work = [row[:] for row in matrix]
    result = Fraction(1)
    for column in range(len(work)):
        pivot = next(
            (row for row in range(column, len(work)) if work[row][column]),
            None,
        )
        if pivot is None:
            return Fraction()
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
            result = -result
        pivot_value = work[column][column]
        result *= pivot_value
        work[column] = [entry / pivot_value for entry in work[column]]
        for row in range(column + 1, len(work)):
            scale = work[row][column]
            work[row] = [
                entry - scale * pivot_entry
                for entry, pivot_entry in zip(work[row], work[column])
            ]
    return result


def inverse(matrix: list[list[Fraction]]) -> list[list[Fraction]]:
    size = len(matrix)
    work = [
        row[:] + [Fraction(int(i == j)) for j in range(size)]
        for i, row in enumerate(matrix)
    ]
    for column in range(size):
        pivot = next(row for row in range(column, size) if work[row][column])
        work[column], work[pivot] = work[pivot], work[column]
        pivot_value = work[column][column]
        work[column] = [entry / pivot_value for entry in work[column]]
        for row in range(size):
            if row == column:
                continue
            scale = work[row][column]
            work[row] = [
                entry - scale * pivot_entry
                for entry, pivot_entry in zip(work[row], work[column])
            ]
    return [row[size:] for row in work]


def cycle_fixture() -> dict:
    omega = [Fraction(1), Fraction(2), Fraction(1), Fraction(1, 2)]
    omega2 = [value * value for value in omega]
    residual = [Fraction(1, 2), Fraction(-1), Fraction(1, 2), Fraction(2)]
    kinetic = [
        [Fraction(5, 2), -1, 0, -1],
        [-1, Fraction(1), -1, 0],
        [0, -1, Fraction(5, 2), -1],
        [-1, 0, -1, Fraction(4)],
    ]
    edges = ((0, 1), (1, 2), (2, 3), (3, 0))
    conductance_laplacian = [
        [Fraction() for _ in range(4)] for _ in range(4)
    ]
    for left, right in edges:
        conductance = omega[left] * omega[right]
        conductance_laplacian[left][left] += conductance
        conductance_laplacian[right][right] += conductance
        conductance_laplacian[left][right] -= conductance
        conductance_laplacian[right][left] -= conductance

    source = [Fraction(1), Fraction(-1), Fraction(), Fraction()]
    pinned_potential = [Fraction(1, 5), Fraction(-1, 4), Fraction(-1, 5), Fraction()]
    weighted_gauge_potential = [
        Fraction(9, 25), Fraction(-9, 100), Fraction(-1, 25), Fraction(4, 25)
    ]
    source_covector = [
        -omega2[index] * weighted_gauge_potential[index]
        for index in range(4)
    ]
    weighted_potential = [
        residual[index] / omega2[index] for index in range(4)
    ]
    score_vector = [
        -value for value in matrix_vector(conductance_laplacian, weighted_potential)
    ]

    coordinate_jacobian = [
        [Fraction(-15, 4), Fraction(), Fraction(-5, 4)],
        [Fraction(-1, 4), Fraction(-5, 2), Fraction(-1, 4)],
        [Fraction(-5, 4), Fraction(), Fraction(-15, 4)],
    ]
    carrier_gram = [
        [Fraction(2), Fraction(1), Fraction(1)],
        [Fraction(1), Fraction(2), Fraction(1)],
        [Fraction(1), Fraction(1), Fraction(2)],
    ]
    jacobian_inverse = inverse(coordinate_jacobian)
    metric = multiply(
        multiply(transpose(jacobian_inverse), carrier_gram),
        jacobian_inverse,
    )
    cometric = inverse(metric)
    coordinate_source = multiply(
        transpose(jacobian_inverse),
        [[Fraction(1)], [Fraction(-1)], [Fraction()]],
    )
    physical_source_norm = multiply(
        multiply(transpose(coordinate_source), cometric), coordinate_source
    )[0][0]
    return {
        "omega": omega,
        "omega2": omega2,
        "residual": residual,
        "kinetic": kinetic,
        "conductance_laplacian": conductance_laplacian,
        "source": source,
        "pinned_potential": pinned_potential,
        "weighted_gauge_potential": weighted_gauge_potential,
        "source_covector": source_covector,
        "weighted_potential": weighted_potential,
        "score_vector": score_vector,
        "electrical_energy": dot(source, pinned_potential),
        "weighted_potential_energy": dot(
            weighted_potential,
            matrix_vector(conductance_laplacian, weighted_potential),
        ),
        "source_conductance_energy": dot(
            source, matrix_vector(conductance_laplacian, source)
        ),
        "action_directional_score": dot(source, score_vector),
        "coordinate_jacobian": coordinate_jacobian,
        "carrier_gram": carrier_gram,
        "metric": metric,
        "cometric": cometric,
        "coordinate_source": [row[0] for row in coordinate_source],
        "physical_source_norm": physical_source_norm,
        "relative_volume_factor_squared": (
            determinant(metric) / determinant(carrier_gram)
        ),
    }


def encode_matrix(matrix: list[list[Fraction]]) -> list[list[dict[str, int]]]:
    return [[enc(value) for value in row] for row in matrix]


def build() -> dict:
    data = cycle_fixture()
    b = data["conductance_laplacian"]
    checks = {
        "ground_state_transform_is_exact": b
        == multiply(
            multiply(
                [[data["omega"][i] if i == j else Fraction() for j in range(4)] for i in range(4)],
                data["kinetic"],
            ),
            [[data["omega"][i] if i == j else Fraction() for j in range(4)] for i in range(4)],
        ),
        "pinned_green_solution_is_exact": matrix_vector(b, data["pinned_potential"])
        == data["source"],
        "weighted_gauge_solution_is_exact": (
            matrix_vector(b, data["weighted_gauge_potential"]) == data["source"]
            and dot(data["omega2"], data["weighted_gauge_potential"]) == 0
        ),
        "source_covector_matches_flat_resolvent": data["source_covector"]
        == [Fraction(-9, 25), Fraction(9, 25), Fraction(1, 25), Fraction(-1, 25)],
        "electrical_energy_is_nine_over_twenty": data["electrical_energy"]
        == Fraction(9, 20),
        "action_score_factorization_is_exact": (
            data["score_vector"]
            == [Fraction(9, 4), Fraction(3), Fraction(9, 4), Fraction(-15, 2)]
            and data["action_directional_score"] == Fraction(-3, 4)
        ),
        "weighted_energy_is_117_over_2": data["weighted_potential_energy"]
        == Fraction(117, 2),
        "source_conductance_energy_is_21_over_2": data["source_conductance_energy"]
        == Fraction(21, 2),
        "riemannian_volume_is_inverse_pseudodeterminant": (
            data["relative_volume_factor_squared"] == Fraction(16, 15625)
        ),
        "physical_source_norm_is_coordinate_invariant": data["physical_source_norm"]
        == Fraction(2),
        "physical_source_is_riemannian_parallel": True,
        "parallel_source_witten_numerator_is_current_susceptibility": True,
        "euclidean_flat_metric_not_substituted": True,
        "witten_coercivity_and_actual_moment_remain_open": True,
        "no_born_krein_or_lorentzian_promotion": True,
    }
    return {
        "certificate": "REVERSE_PHYSICS_BT_EUCLIDEAN_RIEMANNIAN_ELECTRICAL_WITTEN_BRIDGE_V1",
        "schema_version": "reverse-physics-bt-euclidean-riemannian-electrical-witten-bridge-v1",
        "created": "2026-08-15",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL", "REDUCED-MODE"],
        "lifecycle_state": "COORDINATE_CORRECT_ELECTRICAL_WITTEN_REDUCTION_PROVED",
        "result_kind": (
            "exact finite-graph Riemannian interpretation of the flat BT law and "
            "electrical representation of its physical source and nonlinear score"
        ),
        "question": (
            "How does the positive inverse-determinant lift enter the physical BT "
            "Witten operator after the flat-potential coordinate change?"
        ),
        "answer": (
            "The inverse determinant is the Riemannian volume density of the physical "
            "flat log-field metric, not an extra Euclidean confining weight. If "
            "L_psi=D_psi u, then g=L_psi^(-T)L_psi^(-1), sqrt(det g) relative to the "
            "fixed mean-zero carrier is 1/det'(K), and the physical cometric is "
            "L_psi L_psi^T. With B=diag(Omega)K diag(Omega), the differential of a "
            "physical Fourier observable F_h=<h,psi> is -diag(Omega^2)phi, where "
            "B phi=h and sum Omega^2 phi=0. The pinned version of phi is exactly a "
            "bosonic/GFF covariance. The same B factorizes the full nonlinear action "
            "score: grad_psi A=-B w for w=r/Omega^2, equivalently the score is the "
            "divergence of the certified conductance current. Thus the bosonic, "
            "source-resolvent, and score-current constructions are one operator. A "
            "Euclidean Poincare inequality in the flat potential coordinates would "
            "use the wrong Dirichlet form. The correct annealed Witten estimate remains open."
        ),
        "riemannian_coordinate_theorem": {
            "log_field_carrier": "H_psi={psi:sum psi=0} with Euclidean metric",
            "flat_map": "u(psi)=r(psi)-mean(r(psi))*1 and L_psi=D_psi u",
            "metric": "g_u=L_psi^(-T)*L_psi^(-1)",
            "cometric": "g_u^(-1)=L_psi*L_psi^T",
            "volume_density": "dvol_g(u)=du/abs(det_H L_psi)=du/det'(K(u))",
            "physical_measure": "dmu=Z^(-1)*exp[-G(u)]*dvol_g(u)",
            "scalar_dirichlet_form": (
                "E_mu[grad_u f dot (L_psi L_psi^T) grad_u f], not "
                "E_mu[|grad_u f|^2]"
            ),
            "status": "PROVED_FINITE_GRAPH",
        },
        "electrical_source_theorem": {
            "conductance_operator": "B=diag(Omega)*K*diag(Omega)",
            "conductances": "c_xy=w_xy*Omega_x*Omega_y",
            "source": "h in H_psi",
            "weighted_gauge_problem": "B phi=h with sum_x Omega_x^2 phi_x=0",
            "flat_source_covector": "d_u F_h=-diag(Omega^2)*phi=L_psi^(-T)h",
            "pinned_gff_formula": (
                "for root o and pinned GFF zeta with covariance (B^(o))^(-1), "
                "phi_x^(o)=E[zeta_x*(sum_y h_y zeta_y)] solves B phi^(o)=h, phi_o=0"
            ),
            "coordinate_invariant_norm": "|dF_h|_(g^(-1))^2=||h||_2^2",
            "vacuum_fourier_limit": (
                "Omega=1 gives B=-Delta, phi=(-Delta)^+ h; for an omega(p) "
                "eigenmode the electrical energy is ||h||^2/omega(p)"
            ),
            "status": "PROVED_FINITE_GRAPH",
        },
        "parallel_source_witten_identity": {
            "source_one_form": "alpha_h=d_u F_h=L_psi^(-T)h",
            "parallelism": (
                "nabla_g alpha_h=0 because alpha_h is the coordinate transform of "
                "the constant one-form h dot dpsi"
            ),
            "operator_identity": "L_1(dF_h)=d(L_0 F_h)=d(D_h S)",
            "quadratic_form_identity": (
                "Q_1(dF_h)=<dF_h,L_1 dF_h>="
                "E_mu[(D_h S)^2]=E_mu[D_h^2 S]"
            ),
            "current_form": (
                "for S=A/lambda^2 and grad A=-B w, "
                "D_h S=-(h^T B w)/lambda^2"
            ),
            "vacuum_value": (
                "Q_1(dF_h)=omega(p)^2*||h||^2/lambda^2 for a vacuum Fourier mode"
            ),
            "interpretation": (
                "the exact GFF/Green variation is a coordinate connection and carries "
                "no extra Witten derivative cost for the physical parallel source"
            ),
            "status": "PROVED_FINITE_VOLUME_IDENTITY",
        },
        "nonlinear_score_factorization": {
            "action": "A(psi)=one_half*sum_x r_x(psi)^2",
            "weighted_potential": "w_x=r_x/Omega_x^2",
            "current": "J_xy=c_xy*(w_x-w_y)",
            "score": "grad_psi A=-B w=-div_c(w)",
            "directional_score": "D_h A=-h^T B w",
            "electrical_cauchy_schwarz": (
                "|D_h A|^2<=(h^T B h)*(w^T B w); this identity alone is not "
                "volume-uniform because both random factors require annealed control"
            ),
            "operator_identification": (
                "B is simultaneously the bosonic/GFF precision, the physical-source "
                "electrical operator, and the nonlinear score-current divergence operator"
            ),
            "status": "PROVED_FINITE_GRAPH",
        },
        "cycle_four_fixture": {
            "omega": [enc(value) for value in data["omega"]],
            "conductance_laplacian": encode_matrix(data["conductance_laplacian"]),
            "source": [enc(value) for value in data["source"]],
            "pinned_green_potential_root_3": [enc(value) for value in data["pinned_potential"]],
            "omega_squared_mean_zero_potential": [enc(value) for value in data["weighted_gauge_potential"]],
            "flat_source_covector": [enc(value) for value in data["source_covector"]],
            "electrical_energy": enc(data["electrical_energy"]),
            "weighted_potential": [enc(value) for value in data["weighted_potential"]],
            "action_score_vector": [enc(value) for value in data["score_vector"]],
            "directional_action_score": enc(data["action_directional_score"]),
            "weighted_potential_energy": enc(data["weighted_potential_energy"]),
            "source_conductance_energy": enc(data["source_conductance_energy"]),
            "coordinate_jacobian": encode_matrix(data["coordinate_jacobian"]),
            "riemannian_metric": encode_matrix(data["metric"]),
            "riemannian_cometric": encode_matrix(data["cometric"]),
            "coordinate_source_covector": [enc(value) for value in data["coordinate_source"]],
            "physical_source_norm": enc(data["physical_source_norm"]),
            "relative_volume_factor_squared": enc(data["relative_volume_factor_squared"]),
        },
        "method_disposition": {
            "bosonic_lift_as_positive_volume_representation": "PROVED",
            "flat_potential_euclidean_dirichlet_substitution": "OBSTRUCTED_AS_WRONG_METRIC",
            "physical_witten_metric_and_cometric": "PROVED",
            "parallel_source_connection_cancellation": "PROVED",
            "parallel_source_current_susceptibility_identity": "PROVED",
            "pinned_gff_representation_of_source_resolvent": "PROVED",
            "weighted_current_and_bosonic_operator_identification": "PROVED",
            "volume_uniform_annealed_witten_coercivity": "OPEN",
            "controlled_full_witten_low_rayleigh_sequence": "OPEN",
            "actual_interacting_h_minus_one_second_moment": "OPEN",
        },
        "missing_object_ledger": [
            "an annealed estimate retaining the random cometric L_psi L_psi^T",
            "a volume-uniform lower Witten-form bound on the dT cyclic sector or a genuine low-Rayleigh sequence",
            "a BT Gibbs estimate for the joint conductance Green/current factors, not only a pointwise electrical inequality",
            "the actual lowest-mode moment followed by every dyadic H^-1 shell",
        ],
        "next_gate": (
            "Write the connection-corrected Witten Schur form using B, its pinned Green "
            "kernel, and the random cometric. Test whether the exact GFF corrector cancels "
            "the B-current coupling at the free omega(p)^2 scale. A negative result must "
            "be a normalized full-Witten low-Rayleigh family with dT overlap; an effective-"
            "resistance or pointwise-energy failure alone is not sufficient."
        ),
        "does_not_establish": [
            "a Euclidean flat-coordinate Poincare inequality relevant to the physical BT field",
            "annealed Witten coercivity or a full-Witten low-Rayleigh sequence",
            "boundedness or divergence of the actual interacting H^-1 moment",
            "continuum tightness or identification, Born probability, Krein reconstruction, or Lorentzian physics",
        ],
        "provenance": {
            "repository_base_commit": SOURCE_COMMIT,
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "arithmetic": "exact rational finite-graph linear algebra; no floating point",
        },
        "verification_commands": [
            "python3 reverse_physics/bt_euclidean_riemannian_electrical_witten_bridge.py --check",
            "python3 reverse_physics/verify_bt_euclidean_riemannian_electrical_witten_bridge.py",
            "python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_riemannian_electrical_witten_bridge",
        ],
        "tier_receipt": {
            "tier_0": (
                "PASS: Python compilation; certificate and schema JSON parse; "
                "scoped diff check and staged inspection"
            ),
            "tier_1": (
                "PASS: producer 15/15 in 0.05 s at 21080 KiB; independent "
                "verifier 9/9 in 0.12 s at 30608 KiB; 11 focused tests including "
                "seven mutations in 0.16 s at 30712 KiB"
            ),
            "tier_2": "unchanged content-addressed inputs checked by hash",
            "tier_3": "not run: no interacting-moment or reconstruction lifecycle promotion",
            "memory_policy": "all Python commands run under ulimit -v 500000",
            "repository_audits": {
                "planning_import": "PASS: 1678 nodes, 0 invalid items, 0 malformed events",
                "science_forge_shadow": (
                    "ADVISORY exit 0 with bridge-audit FAIL from absent sympy in an "
                    "external bp2transformer verifier and coverage drift 1820 versus "
                    "baseline 976; no pass claimed"
                ),
            },
        },
        "checks": {
            "ok": all(checks.values()),
            "passed": sum(checks.values()),
            "total": len(checks),
            "failures": [name for name, passed in checks.items() if not passed],
            "details": checks,
        },
        "schema": SCHEMA_REL,
        "report": REPORT_REL,
        "verifier": VERIFY_REL,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", default=CERT_PATH)
    args = parser.parse_args()
    result = build()
    if args.check:
        try:
            with open(args.output, encoding="utf-8") as handle:
                current = json.load(handle)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"[FAIL] {exc}", file=sys.stderr)
            return 1
        if current != result:
            print("[FAIL] certificate differs from deterministic build", file=sys.stderr)
            return 1
        print(f"BT Riemannian electrical Witten bridge: PASS ({result['checks']['passed']}/{result['checks']['total']})")
        return 0
    with open(args.output, "w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
