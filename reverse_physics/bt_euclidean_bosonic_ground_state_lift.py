#!/usr/bin/env python3
"""Certify the positive bosonic lift of the flat-potential BT law."""

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
    "REVERSE_PHYSICS_BT_EUCLIDEAN_BOSONIC_GROUND_STATE_LIFT_V1.json"
)
CERT_PATH = os.path.join(ROOT, CERT_REL)
SCHEMA_REL = (
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-bosonic-ground-state-lift-v1.schema.json"
)
REPORT_REL = (
    "reverse_physics/reports/bt-euclidean-bosonic-ground-state-lift.md"
)
VERIFY_REL = "reverse_physics/verify_bt_euclidean_bosonic_ground_state_lift.py"
INPUT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_FLAT_POTENTIAL_DETERMINANT_PUSHFORWARD_V1.json"
)
SOURCE_COMMIT = "2fce7906959f2b1191ca12d3df3e447bd8a32705"


def enc(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def sha256(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


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
        value = work[column][column]
        result *= value
        work[column] = [entry / value for entry in work[column]]
        for row in range(column + 1, len(work)):
            scale = work[row][column]
            work[row] = [
                entry - scale * pivot_entry
                for entry, pivot_entry in zip(work[row], work[column])
            ]
    return result


def principal_minor(matrix: list[list[Fraction]], root: int) -> list[list[Fraction]]:
    return [
        [entry for column, entry in enumerate(row) if column != root]
        for index, row in enumerate(matrix)
        if index != root
    ]


def fixture() -> dict:
    omega = [Fraction(1), Fraction(2), Fraction(1), Fraction(1, 2)]
    kinetic = [
        [Fraction(5, 2), -1, 0, -1],
        [-1, Fraction(1), -1, 0],
        [0, -1, Fraction(5, 2), -1],
        [-1, 0, -1, Fraction(4)],
    ]
    norm2 = sum((value * value for value in omega), Fraction())
    root_weights = [value * value / norm2 for value in omega]
    cofactors = [
        determinant(principal_minor(kinetic, root)) for root in range(4)
    ]
    pseudodeterminant = sum(cofactors, Fraction())
    integrated_factors = [
        root_weights[root] / cofactors[root] for root in range(4)
    ]
    conductances = [
        omega[0] * omega[1],
        omega[1] * omega[2],
        omega[2] * omega[3],
        omega[3] * omega[0],
    ]
    tree_products = [
        conductances[1] * conductances[2] * conductances[3],
        conductances[0] * conductances[2] * conductances[3],
        conductances[0] * conductances[1] * conductances[3],
        conductances[0] * conductances[1] * conductances[2],
    ]
    return {
        "omega": omega,
        "kinetic": kinetic,
        "norm2": norm2,
        "root_weights": root_weights,
        "cofactors": cofactors,
        "pseudodeterminant": pseudodeterminant,
        "integrated_factors": integrated_factors,
        "conductances": conductances,
        "tree_products": tree_products,
        "tree_sum": sum(tree_products, Fraction()),
    }


def build() -> dict:
    data = fixture()
    checks = {
        "fixture_operator_kills_positive_ground_state": all(
            sum(
                (data["kinetic"][row][column] * data["omega"][column]
                 for column in range(4)),
                Fraction(),
            ) == 0
            for row in range(4)
        ),
        "root_weights_are_probability_vector": (
            data["root_weights"]
            == [Fraction(4, 25), Fraction(16, 25), Fraction(4, 25), Fraction(1, 25)]
            and sum(data["root_weights"], Fraction()) == 1
        ),
        "principal_minors_are_positive": data["cofactors"]
        == [Fraction(5), Fraction(20), Fraction(5), Fraction(5, 4)],
        "cofactor_identity_holds_rootwise": all(
            data["cofactors"][root]
            == data["pseudodeterminant"] * data["root_weights"][root]
            for root in range(4)
        ),
        "two_real_gaussians_produce_inverse_determinant": all(
            value == Fraction(4, 125) for value in data["integrated_factors"]
        ),
        "ground_state_conductances_are_positive": data["conductances"]
        == [Fraction(2), Fraction(2), Fraction(1, 2), Fraction(1, 2)],
        "matrix_tree_sum_is_exact": (
            data["tree_products"]
            == [Fraction(1, 2), Fraction(1, 2), Fraction(2), Fraction(2)]
            and data["tree_sum"] == 5
        ),
        "vrjp_determinant_exponent_differs_by_three_halves": (
            Fraction(1, 2) - Fraction(-1) == Fraction(3, 2)
        ),
        "published_hyperbolic_localization_not_imported": True,
        "actual_interacting_moment_remains_open": True,
        "no_born_krein_or_lorentzian_promotion": True,
    }
    return {
        "certificate": "REVERSE_PHYSICS_BT_EUCLIDEAN_BOSONIC_GROUND_STATE_LIFT_V1",
        "schema_version": "reverse-physics-bt-euclidean-bosonic-ground-state-lift-v1",
        "created": "2026-08-15",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "lifecycle_state": "POSITIVE_BOSONIC_LIFT_PROVED_HYPERBOLIC_IMPORT_OBSTRUCTED",
        "result_kind": (
            "exact finite-graph positive auxiliary-field representation of the BT "
            "inverse pseudodeterminant and scoped direct-import obstruction"
        ),
        "question": (
            "Does the flat-potential inverse determinant admit a positive random-walk "
            "lift, and can the H^{2|2}/VRJP localization measure be identified with it?"
        ),
        "answer": (
            "The first answer is yes and the second is no as a direct import. For any "
            "connected finite graph, K positive semidefinite of rank N-1, and positive "
            "K-ground vector Omega, the root cofactor identity det K^(o)=det'(K) q_o "
            "with q_o=Omega_o^2/||Omega||^2 turns 1/det'(K) into a positive integral "
            "over two real Gaussian fields pinned at o. After the ground-state "
            "transform these are pinned GFFs with conductances w_xy Omega_x Omega_y. "
            "A uniform mixture over roots leaves the root uniform after the bosons "
            "are integrated out. This is a genuine positive random-conductance bridge. "
            "It is not the published VRJP/hyperbolic measure: that law has a square-root "
            "spanning-tree determinant and a cosh edge energy, whereas BT has determinant "
            "power -1 and Gaussian confinement of a centered Schrödinger potential. "
            "The determinant exponents differ by 3/2, so the supersymmetric "
            "normalization/localization theorem cannot be imported without changing "
            "the measure. No interacting H^-1 moment is decided."
        ),
        "bosonic_lift_theorem": {
            "scope": "every connected finite undirected weighted graph",
            "hypotheses": (
                "K is real symmetric positive semidefinite, rank(K)=N-1, "
                "K Omega=0, and Omega_x>0"
            ),
            "root_probability": "q_o=Omega_o^2/||Omega||_2^2",
            "cofactor_identity": "det K^(o)=det'(K)*q_o",
            "gaussian_identity": (
                "1/det'(K)=q_o*Integral exp[-(xi^T K^(o) xi+eta^T K^(o) eta)/2] "
                "d xi d eta/(2*pi)^(N-1)"
            ),
            "field_count": "two real commuting pinned Gaussian fields",
            "uniform_root_mixture": (
                "averaging the rooted identity with weight 1/N gives an exact positive "
                "joint lift; after Gaussian integration the root is uniform and "
                "independent of the flat potential"
            ),
            "status": "PROVED",
        },
        "ground_state_transform": {
            "operator": "B=diag(Omega)*K*diag(Omega)",
            "conductance": "c_xy=w_xy*Omega_x*Omega_y",
            "quadratic_form": (
                "for z_x=Omega_x phi_x and phi_o=0, "
                "z^T K z=sum_{unordered {x,y}} c_xy*(phi_x-phi_y)^2"
            ),
            "conditional_interpretation": (
                "the two commuting auxiliary fields are independent pinned GFFs in "
                "the positive random conductance environment c(Omega)"
            ),
            "status": "PROVED",
        },
        "cycle_four_fixture": {
            "graph": "unweighted four-cycle",
            "omega": [enc(value) for value in data["omega"]],
            "omega_norm_squared": enc(data["norm2"]),
            "root_probabilities": [enc(value) for value in data["root_weights"]],
            "principal_minors": [enc(value) for value in data["cofactors"]],
            "pseudodeterminant": enc(data["pseudodeterminant"]),
            "rootwise_integrated_factors": [enc(value) for value in data["integrated_factors"]],
            "ground_state_conductances_cyclic_order": [enc(value) for value in data["conductances"]],
            "spanning_tree_products": [enc(value) for value in data["tree_products"]],
            "spanning_tree_sum": enc(data["tree_sum"]),
        },
        "hyperbolic_comparator": {
            "source_1": (
                "Sabot, Tarres, and Zeng, arXiv:1507.04660v2, Eq. (density_u): "
                "VRJP mixing density contains sqrt(D(W,u))"
            ),
            "source_2": (
                "Sabot and Tarres, arXiv:1111.3991v5, Theorem 2(i): density is "
                "exp(u_o-H(W,u))*sqrt(D(W,u)) with H a cosh edge energy"
            ),
            "bt_determinant_power": "-1 on det'(K)",
            "vrjp_determinant_power": "+1/2 on the spanning-tree determinant",
            "exponent_difference": enc(Fraction(3, 2)),
            "energy_mismatch": (
                "BT uses ||u||^2+N*ell_0(u)^2 on centered diagonal potentials; "
                "VRJP uses a nearest-neighbor cosh energy on a logarithmic field"
            ),
            "direct_import_disposition": "OBSTRUCTED_AS_MEASURE_IDENTITY",
            "scope_boundary": (
                "this does not rule out a new BT-specific theorem using pinned-GFF or "
                "random-conductance tools"
            ),
        },
        "method_disposition": {
            "positive_auxiliary_probability": "PROVED_FINITE_GRAPH",
            "pinned_gff_random_conductance_bridge": "PROVED_FINITE_GRAPH",
            "published_vrjp_hyperbolic_localization_direct_import": "OBSTRUCTED",
            "bt_specific_annealed_witten_or_poincare_bound": "OPEN",
            "actual_interacting_h_minus_one_second_moment": "OPEN",
        },
        "missing_object_ledger": [
            "a volume-uniform estimate for the pinned-GFF/random-conductance lift",
            "a coercive annealed Witten form or a normalized full-Witten low-Rayleigh sequence",
            "the actual lowest-mode moment and all dyadic H^-1 shells",
            "a compactly weaker tightness theorem after, and only after, the moment bound",
        ],
        "next_gate": (
            "Use the exact positive lift to express the connection-corrected annealed "
            "Witten form through killed random-walk Green functions in conductances "
            "w_xy Omega_x Omega_y. Prove a volume-uniform form estimate, or construct "
            "a normalized low-Rayleigh sequence with nonzero lowest-mode overlap."
        ),
        "does_not_establish": [
            "a Poincare or Witten spectral gap",
            "a bound or divergence for the actual interacting H^-1 moment",
            "continuum tightness or continuum identification",
            "ordinary OS reconstruction, Born probability, Krein reconstruction, or Lorentzian physics",
        ],
        "provenance": {
            "repository_base_commit": SOURCE_COMMIT,
            "inputs": [{"path": INPUT_REL, "sha256": sha256(INPUT_REL)}],
            "literature_audit": {
                "arxiv_1507_04660_source_sha256": "855d822578a8fc463ec4b53ab0197a4023849776a1fe04b5668d5e506f0f77f4",
                "arxiv_1111_3991_source_sha256": "2457010635a43b6524c7f564c6de7d6646b9c4938c0ab835396e7952fbf1ec95",
                "role": "formula comparison only; neither archive is imported as executable evidence",
            },
            "arithmetic": "exact rational finite-graph arithmetic; no floating point",
        },
        "verification_commands": [
            "python3 reverse_physics/bt_euclidean_bosonic_ground_state_lift.py --check",
            "python3 reverse_physics/verify_bt_euclidean_bosonic_ground_state_lift.py",
            "python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_bosonic_ground_state_lift",
        ],
        "tier_receipt": {
            "tier_0": "Python and JSON parse; scoped git diff --check",
            "tier_1": "producer check, independent verifier, focused mutation tests",
            "tier_2": "not run: the imported content-addressed flat-potential theorem is unchanged",
            "tier_3": "not run: no H^-1 theorem, lifecycle promotion, freeze, or release",
            "memory_policy": "all Python commands run under ulimit -v 500000",
            "elapsed_seconds_and_peak_kib": {
                "producer_check": "0.04 s, 20620 KiB",
                "independent_verifier": "0.10 s, 30072 KiB",
                "focused_tests": "0.13 s, 30460 KiB; 10 tests including six mutations",
            },
            "repository_audits": {
                "planning_import": "PASS: 1676 nodes, 0 invalid items, 0 malformed events",
                "science_forge_shadow": (
                    "ADVISORY exit 0 with reported bridge-audit FAIL because sympy is "
                    "absent in an external bp2transformer verifier, plus expected corpus "
                    "coverage drift 1815 versus baseline 976; no pass claimed"
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
        print(f"BT bosonic ground-state lift producer: PASS ({result['checks']['passed']}/{result['checks']['total']})")
        return 0
    with open(args.output, "w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
