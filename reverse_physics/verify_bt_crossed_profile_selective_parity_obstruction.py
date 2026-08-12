#!/usr/bin/env python3
"""Independent verifier for the crossed profile-selective parity obstruction."""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
import sys

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_CROSSED_PROFILE_SELECTIVE_PARITY_OBSTRUCTION_V1.json",
)
SCHEMA = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-crossed-profile-selective-parity-obstruction-v1.schema.json",
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
    predecessors = [load(os.path.join(ROOT, row["path"])) for row in inputs[1:]]
    same = certificate["same_carrier_classification"]
    prefix_data = certificate["prefix_obstruction"]
    public_data = certificate["public_ghost_parity_test"]
    escape = certificate["escape_architectures"]
    disposition = certificate["disposition"]

    q, v = sp.symbols("q v", positive=True)
    z = sp.symbols("z")
    local = {"q": q, "v": v, "z": z}

    def expression(value):
        return sp.sympify(value, locals=local)

    def matrix(value):
        return sp.Matrix([[expression(entry) for entry in row] for row in value])

    J = sp.Matrix([[0, 1], [1, 0]])
    K = 3*J
    eta = sp.kronecker_product(J, K)
    I = sp.eye(2)
    Rp = sp.Matrix.hstack(I, I)
    Rm = sp.Matrix.hstack(I, -I)
    D = sp.diag(-q, -q, v, v)
    G = sp.simplify(D.T*Rp.T*K*Rp*D)
    A = sp.simplify(eta.inv()*G)
    Sp = sp.diag(1, 1, -1, -1)
    Arepaired = sp.simplify(eta.inv()*Sp.T*G*Sp)
    h = sp.Matrix([0, sp.Rational(1, 2), sp.Rational(1, 2), 0])
    hnorm = sp.factor((h.T*eta*h)[0])

    rows = []
    for signs in itertools.product((-1, 1), repeat=4):
        C = sp.diag(*signs)
        metric = C.T*eta*C
        metric_type = (
            "KREIN_ISOMETRY" if metric == eta else
            "KREIN_ANTI_ISOMETRY" if metric == -eta else
            "MIXED_METRIC_BREAKING"
        )
        characteristic = sp.factor(
            (eta.inv()*C.T*G*C).charpoly(z).as_expr()
        )
        rows.append(
            {
                "signs": list(signs),
                "metric_type": metric_type,
                "prefix_gram_preserved": sp.factor(
                    (C*h).T*eta*(C*h)
                )[0] == hnorm,
                "exact_R_minus_collapse": Rp*C == Rm,
                "phase_equivalent_R_minus_collapse": (
                    Rp*C == Rm or Rp*C == -Rm
                ),
                "raised_characteristic_polynomial": str(characteristic),
                "repairs_nonzero_spectrum": sp.simplify(
                    characteristic-z**2*(z-2*q*v)**2
                ) == 0,
            }
        )

    W9 = matrix(public_data["neutral_degree_four_metric"])
    kappa9 = matrix(public_data["neutral_degree_four_ghost_parity"])
    selected = matrix(public_data["selected_odd_columns"])
    selected_metric = sp.simplify(selected.T*W9*selected)
    selected_action = sp.simplify(
        selected_metric.inv()*selected.T*W9*kappa9*selected
    )

    recorded_rows = same["diagonal_unit_sign_census"]
    counts = {
        kind: sum(row["metric_type"] == kind for row in rows)
        for kind in (
            "KREIN_ISOMETRY",
            "KREIN_ANTI_ISOMETRY",
            "MIXED_METRIC_BREAKING",
        )
    }
    checks = {
        "schema_validation": True,
        "all_input_hashes_match": all(
            row["sha256"] == sha256(row["path"]) for row in inputs
        ),
        "predecessors_pass": all(value["checks"]["ok"] for value in predecessors),
        "metric_reconstructs": matrix(same["metric_eta"]) == eta,
        "profile_metric_reconstructs": matrix(same["profile_metric_K"]) == K,
        "crossed_D_reconstructs": matrix(same["crossed_amplitude_D"]) == D,
        "R_plus_reconstructs": matrix(same["outgoing_style_collapse_R_plus"]) == Rp,
        "R_minus_reconstructs": matrix(same["repaired_collapse_R_minus"]) == Rm,
        "base_raised_pullback_reconstructs": sp.simplify(
            matrix(same["base_raised_pullback"])-A
        ) == sp.zeros(4),
        "base_spectrum_is_negative_rank_two": sp.simplify(
            expression(same["base_characteristic_polynomial"])
            - z**2*(z+2*q*v)**2
        ) == 0,
        "isometry_similarity_lemma_is_stated": (
            "C^-1*A_plus*C" in same["isometry_lemma"]
            and "unchanged" in same["isometry_lemma"]
        ),
        "anti_isometry_sign_lemma_is_stated": (
            "-C^-1*A_plus*C" in same["anti_isometry_lemma"]
            and "reverses sign" in same["anti_isometry_lemma"]
        ),
        "all_sixteen_sign_rows_recomputed": recorded_rows == rows,
        "sign_census_reconstructs": (
            counts["KREIN_ISOMETRY"] == 4
            and counts["KREIN_ANTI_ISOMETRY"] == 4
            and counts["MIXED_METRIC_BREAKING"] == 8
            and sum(row["repairs_nonzero_spectrum"] for row in rows) == 4
        ),
        "all_repairs_are_anti_krein": all(
            row["metric_type"] == "KREIN_ANTI_ISOMETRY"
            for row in rows if row["repairs_nonzero_spectrum"]
        ),
        "no_anti_repair_preserves_prefix_gram": all(
            not row["prefix_gram_preserved"]
            for row in rows if row["metric_type"] == "KREIN_ANTI_ISOMETRY"
        ),
        "R_minus_unique_up_to_phase": sum(
            row["phase_equivalent_R_minus_collapse"] for row in rows
        ) == 2,
        "prefix_reconstructs": sp.Matrix(
            [expression(value) for value in prefix_data["prefix_vector"]]
        ) == h,
        "prefix_is_nonnull_three_halves": (
            expression(prefix_data["prefix_gram"]) == hnorm
            == sp.Rational(3, 2)
        ),
        "canonical_parent_parity_reconstructs": matrix(
            prefix_data["canonical_parent_parity"]
        ) == Sp,
        "canonical_parent_parity_is_anti_krein": Sp.T*eta*Sp == -eta,
        "canonical_parent_parity_changes_collapse": Rp*Sp == Rm,
        "repaired_spectrum_reconstructs": (
            sp.simplify(matrix(prefix_data["repaired_raised_pullback"])-Arepaired)
            == sp.zeros(4)
            and sp.simplify(
                expression(prefix_data["repaired_characteristic_polynomial"])
                - z**2*(z-2*q*v)**2
            ) == 0
        ),
        "transformed_prefix_gram_is_negative_three_halves": (
            sp.Matrix(
                [expression(value) for value in prefix_data["transformed_prefix"]]
            ) == Sp*h
            and expression(prefix_data["transformed_prefix_gram"])
            == -sp.Rational(3, 2)
        ),
        "general_prefix_no_go_is_explicit": (
            "every anti-isometry" in prefix_data["general_no_go"]
            and "3/2 is nonzero" in prefix_data["general_no_go"]
        ),
        "regular_limit_no_go_is_explicit": (
            "continuous family" in prefix_data["regular_localization_no_go"]
            and "eta=-eta" in prefix_data["regular_localization_no_go"]
        ),
        "public_degree_four_parity_is_involutive_isometry": (
            kappa9*kappa9 == sp.eye(9)
            and sp.simplify(kappa9.T*W9*kappa9-W9) == sp.zeros(9)
        ),
        "public_selected_plane_reconstructs": (
            selected_metric == -sp.eye(2)
            and selected_action == -sp.eye(2)
            and matrix(public_data["selected_metric"]) == selected_metric
            and matrix(public_data["selected_ghost_action"]) == selected_action
        ),
        "ghost_odd_plane_still_preserves_metric": sp.simplify(
            selected_action.T*selected_metric*selected_action-selected_metric
        ) == sp.zeros(2),
        "same_carrier_and_public_composite_routes_closed": (
            escape["regular_same_carrier_parity"] == "EXACTLY_OBSTRUCTED"
            and escape["inherited_public_symmetric_power_ghost_parity"]
            == "EXACTLY_OBSTRUCTED_AS_SIGN_REPAIR"
        ),
        "doubled_and_nonfactorizing_routes_remain_open": (
            escape["doubled_cross_paired_source"]
            == "ALGEBRAICALLY_POSSIBLE_NEW_CARRIER_NOT_BT_DERIVED"
            and escape["nonfactorizing_crossed_three_to_three_pretrace_term"]
            == "NOT_COMPUTED"
        ),
        "claim_boundary_remains_fail_closed": (
            disposition["twelve_reversed_physical_intertwiners"]
            == "NOT_CONSTRUCTED"
            and disposition["complete_crossed_probability"] == "NOT_COMPUTED"
            and disposition["Eq19_all_orders"] == "NOT_PROVED"
            and disposition["spacetime_Moller_LSZ_S_operator"]
            == "NOT_CONSTRUCTED"
        ),
        "next_gate_is_nonfactorizing_pretrace": (
            "complete 220-tree external-mass jet" in certificate["next_gate"]
            and "before the coherent R_plus collapse" in certificate["next_gate"]
            and "all twelve reversed histories" in certificate["next_gate"]
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
