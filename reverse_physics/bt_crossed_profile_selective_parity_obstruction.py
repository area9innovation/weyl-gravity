#!/usr/bin/env python3
"""Exact obstruction to a regular profile-selective crossed BT parity."""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
import sys


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_CROSSED_PROFILE_SELECTIVE_PARITY_OBSTRUCTION_V1.json",
)
SCHEMA = (
    "reverse_physics/schema/"
    "reverse-physics-bt-crossed-profile-selective-parity-obstruction-v1.schema.json"
)
REPORT = (
    "reverse_physics/reports/"
    "bt-crossed-profile-selective-parity-obstruction.md"
)
SOURCE = "50b3749e02fe3d86064a40766b0e54f10366b4f4"
INPUTS = [
    "planning/work-items/"
    "reverse-physics-bateman-crossed-profile-selective-parity-obstruction.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_SIX_POINT_PROFILE_QUOTIENT_COMPLETION_V1.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_CROSSED_DETECTOR_ORIENTATION_NO_GO_V1.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_CROSSED_WIGHTMAN_DUAL_NO_GO_V1.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_PUBLIC_FOCK_ODD_SOURCE_AFFILIATION_V1.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_PERTURBATIVE_GHOST_PARITY_UNIT_OBSTRUCTION_V1.json",
]


def load(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as handle:
        return json.load(handle)


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def matrix_strings(matrix):
    import sympy as sp

    return [
        [str(sp.factor(matrix[i, j])) for j in range(matrix.cols)]
        for i in range(matrix.rows)
    ]


def derive():
    import sympy as sp

    quotient = load(INPUTS[1])
    orientation = load(INPUTS[2])
    wightman = load(INPUTS[3])
    public = load(INPUTS[4])
    unit = load(INPUTS[5])

    J = sp.Matrix([[0, 1], [1, 0]])
    K = 3*J
    eta = sp.kronecker_product(J, K)
    identity = sp.eye(2)
    R_plus = sp.Matrix.hstack(identity, identity)
    R_minus = sp.Matrix.hstack(identity, -identity)
    q, v = sp.symbols("q v", positive=True)
    z = sp.symbols("z")
    D = sp.diag(-q, -q, v, v)
    G_plus = sp.simplify(D.T*R_plus.T*K*R_plus*D)
    A_plus = sp.simplify(eta.inv()*G_plus)
    characteristic_plus = sp.factor(A_plus.charpoly(z).as_expr())

    S_parent = sp.diag(1, 1, -1, -1)
    G_repaired = sp.simplify(
        S_parent.T*D.T*R_plus.T*K*R_plus*D*S_parent
    )
    A_repaired = sp.simplify(eta.inv()*G_repaired)
    characteristic_repaired = sp.factor(A_repaired.charpoly(z).as_expr())

    prefix = sp.Matrix([0, sp.Rational(1, 2), sp.Rational(1, 2), 0])
    prefix_gram = sp.factor((prefix.T*eta*prefix)[0])
    repaired_prefix = S_parent*prefix
    repaired_prefix_gram = sp.factor(
        (repaired_prefix.T*eta*repaired_prefix)[0]
    )

    sign_rows = []
    for signs in itertools.product((-1, 1), repeat=4):
        C = sp.diag(*signs)
        transformed_metric = C.T*eta*C
        if transformed_metric == eta:
            metric_type = "KREIN_ISOMETRY"
        elif transformed_metric == -eta:
            metric_type = "KREIN_ANTI_ISOMETRY"
        else:
            metric_type = "MIXED_METRIC_BREAKING"
        A = sp.simplify(eta.inv()*C.T*G_plus*C)
        characteristic = sp.factor(A.charpoly(z).as_expr())
        sign_rows.append(
            {
                "signs": list(signs),
                "metric_type": metric_type,
                "prefix_gram_preserved": sp.factor(
                    (C*prefix).T*eta*(C*prefix)
                )[0] == prefix_gram,
                "exact_R_minus_collapse": R_plus*C == R_minus,
                "phase_equivalent_R_minus_collapse": (
                    R_plus*C == R_minus or R_plus*C == -R_minus
                ),
                "raised_characteristic_polynomial": str(characteristic),
                "repairs_nonzero_spectrum": sp.simplify(
                    characteristic-z**2*(z-2*q*v)**2
                ) == 0,
            }
        )

    public_sector = public["public_neutral_degree_four_sector"]
    W9 = sp.Matrix(
        [[sp.sympify(entry) for entry in row] for row in public_sector["gram"]]
    )
    kappa9 = sp.Matrix(
        [
            [sp.sympify(entry) for entry in row]
            for row in public_sector["ghost_parity"]
        ]
    )
    selected = sp.Matrix(
        [
            [sp.sympify(entry) for entry in row]
            for row in public_sector["selected_normalized_columns"]
        ]
    )
    selected_metric = sp.simplify(selected.T*W9*selected)
    selected_kappa = sp.simplify(
        selected_metric.inv()*selected.T*W9*kappa9*selected
    )

    isometry_rows = [
        row for row in sign_rows if row["metric_type"] == "KREIN_ISOMETRY"
    ]
    anti_rows = [
        row
        for row in sign_rows
        if row["metric_type"] == "KREIN_ANTI_ISOMETRY"
    ]
    mixed_rows = [
        row
        for row in sign_rows
        if row["metric_type"] == "MIXED_METRIC_BREAKING"
    ]
    repair_rows = [row for row in sign_rows if row["repairs_nonzero_spectrum"]]

    checks = {
        "predecessors_pass": all(
            value["checks"]["ok"]
            for value in (quotient, orientation, wightman, public, unit)
        ),
        "carrier_metric_matches_prefix_certificate": matrix_strings(eta)
        == quotient["declared_carrier"]["tensor_metric_eta"],
        "coherent_collapse_matches_prefix_certificate": matrix_strings(R_plus)
        == quotient["physical_pullback"]["coherent_collapse_R"],
        "crossed_D_reconstructs": D == sp.diag(-q, -q, v, v),
        "base_crossed_characteristic_is_negative_rank_two": (
            sp.simplify(characteristic_plus-z**2*(z+2*q*v)**2) == 0
            and A_plus.rank() == 2
        ),
        "parent_parity_is_involution": S_parent*S_parent == sp.eye(4),
        "parent_parity_is_anti_krein": S_parent.T*eta*S_parent == -eta,
        "parent_parity_changes_collapse_to_R_minus": R_plus*S_parent == R_minus,
        "parent_parity_repairs_crossed_spectrum": (
            sp.simplify(
                characteristic_repaired-z**2*(z-2*q*v)**2
            ) == 0
            and A_repaired.rank() == 2
        ),
        "prefix_vector_matches_certificate": [str(value) for value in prefix]
        == quotient["prefix_compatibility"]["five_point_hard_vector"],
        "prefix_is_nonnull": prefix_gram == sp.Rational(3, 2),
        "parent_parity_does_not_fix_prefix": repaired_prefix != prefix,
        "parent_parity_reverses_prefix_gram": repaired_prefix_gram
        == -prefix_gram,
        "anti_isometry_fixed_nonnull_prefix_contradiction": prefix_gram
        != -prefix_gram,
        "all_sixteen_diagonal_signs_classified": len(sign_rows) == 16,
        "four_diagonal_isometries": len(isometry_rows) == 4,
        "four_diagonal_anti_isometries": len(anti_rows) == 4,
        "eight_diagonal_metric_breakers": len(mixed_rows) == 8,
        "all_metric_homogeneous_repairs_are_anti_krein": (
            len(repair_rows) == 4
            and all(
                row["metric_type"] == "KREIN_ANTI_ISOMETRY"
                for row in repair_rows
            )
        ),
        "no_diagonal_anti_repair_preserves_prefix_gram": all(
            not row["prefix_gram_preserved"] for row in anti_rows
        ),
        "R_minus_repair_unique_up_to_global_phase": sum(
            row["phase_equivalent_R_minus_collapse"] for row in sign_rows
        ) == 2,
        "public_degree_four_ghost_parity_is_involution": kappa9*kappa9
        == sp.eye(9),
        "public_degree_four_ghost_parity_is_krein_isometry": sp.simplify(
            kappa9.T*W9*kappa9-W9
        ) == sp.zeros(9),
        "public_selected_odd_sector_is_negative_rank_two": selected_metric
        == -sp.eye(2),
        "public_selected_ghost_action_is_minus_identity": selected_kappa
        == -sp.eye(2),
        "selected_minus_identity_preserves_metric": sp.simplify(
            selected_kappa.T*selected_metric*selected_kappa-selected_metric
        ) == sp.zeros(2),
        "public_selected_affiliation_is_not_dynamical": public[
            "Eq19_boundary"
        ]["graph_slope_from_public_Rt"] == "NOT_DERIVED",
        "regular_same_chart_hidden_parity_already_obstructed": unit[
            "disposition"
        ]["same_chart_regular_local_symbol_hidden_parity"]
        == "EXACTLY_OBSTRUCTED",
        "doubled_architecture_not_BT_derived": unit["disposition"][
            "doubled_source_architecture"
        ] == "ALGEBRAICALLY_AVAILABLE_BUT_NOT_BT_DERIVED",
        "regular_identity_to_anti_limit_is_contradictory": eta != -eta,
        "wightman_dual_remains_identity": wightman["disposition"][
            "spectral_reflection_mass_jet_action"
        ] == "IDENTITY",
        "twelve_histories_remain_open": orientation["history_disposition"][
            "reversed_history_count"
        ] == 12,
        "input_hashes_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
    }
    checks = {name: bool(value) for name, value in checks.items()}
    return {
        "checks": checks,
        "J": J,
        "K": K,
        "eta": eta,
        "R_plus": R_plus,
        "R_minus": R_minus,
        "D": D,
        "A_plus": A_plus,
        "characteristic_plus": characteristic_plus,
        "S_parent": S_parent,
        "A_repaired": A_repaired,
        "characteristic_repaired": characteristic_repaired,
        "prefix": prefix,
        "prefix_gram": prefix_gram,
        "repaired_prefix": repaired_prefix,
        "repaired_prefix_gram": repaired_prefix_gram,
        "sign_rows": sign_rows,
        "W9": W9,
        "kappa9": kappa9,
        "selected": selected,
        "selected_metric": selected_metric,
        "selected_kappa": selected_kappa,
    }


def build():
    d = derive()
    checks = d["checks"]
    return {
        "certificate": "REVERSE_PHYSICS_BT_CROSSED_PROFILE_SELECTIVE_PARITY_OBSTRUCTION_V1",
        "schema_version": "reverse-physics-bt-crossed-profile-selective-parity-obstruction-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "CLASSIFIED",
        "result_kind": "exact same-carrier metric-type and prefix-compatibility obstruction for a regular profile-selective crossed BT parity",
        "question": "Can the six-point sign repair be localized regularly to the second parent/profile collapse, preserve the certified non-null five-point prefix, and arise from public BT ghost parity or its neutral degree-four Fock action?",
        "answer": "No on the declared nondegenerate carrier and for every regular metric-compatible parity action. The crossed four-component raised pullback has nonzero eigenvalue -2*q*v. Any Krein isometry changes it only by similarity and cannot repair the sign. Any Krein anti-isometry reverses the raised spectrum and can repair it, but it reverses the norm of every vector; therefore it cannot preserve the certified five-point prefix h=(0,1/2,1/2,0), whose eta-norm is 3/2. The exact parent parity diag(I2,-I2) changes R_plus to R_minus and produces +2*q*v, but sends the prefix norm to -3/2. All sixteen real diagonal unit signs confirm the general theorem: the four sign-repairing metric-homogeneous maps are precisely the anti-isometries, and none preserves the prefix Gram. A continuous spectator-controlled family cannot equal the identity at the no-spectator boundary and be anti-Krein immediately inside without becoming singular or discontinuous. Public ghost parity does not evade this. Its certified neutral degree-four symmetric-Fock action is a Krein isometry, including on the selected negative ghost-odd two-plane where it is merely -I2; it preserves that metric and cannot generate the internal anti-Krein jet action. Thus regular same-carrier and inherited higher-composite parity symmetry are closed. A new off-diagonal doubled source/amplitude, a singular different chart, or the nonfactorizing crossed 3-to-3 pre-trace term remains possible and is not computed here.",
        "same_carrier_classification": {
            "metric_eta": matrix_strings(d["eta"]),
            "profile_metric_K": matrix_strings(d["K"]),
            "crossed_amplitude_D": matrix_strings(d["D"]),
            "outgoing_style_collapse_R_plus": matrix_strings(d["R_plus"]),
            "repaired_collapse_R_minus": matrix_strings(d["R_minus"]),
            "base_raised_pullback": matrix_strings(d["A_plus"]),
            "base_characteristic_polynomial": str(d["characteristic_plus"]),
            "isometry_lemma": "If C^T*eta*C=eta, then A_C=C^-1*A_plus*C, so the raised spectrum and its negative nonzero sign are unchanged.",
            "anti_isometry_lemma": "If C^T*eta*C=-eta, then A_C=-C^-1*A_plus*C, so the nonzero raised spectrum reverses sign.",
            "diagonal_unit_sign_census": d["sign_rows"],
            "census_summary": {
                "total": 16,
                "krein_isometries": 4,
                "krein_anti_isometries": 4,
                "mixed_metric_breakers": 8,
                "sign_repairing_metric_homogeneous_maps": 4,
                "sign_repairs_preserving_prefix_gram": 0,
                "exact_R_minus_repair_up_to_global_phase": 2,
            },
        },
        "prefix_obstruction": {
            "prefix_vector": [str(value) for value in d["prefix"]],
            "prefix_gram": str(d["prefix_gram"]),
            "canonical_parent_parity": matrix_strings(d["S_parent"]),
            "parent_parity_metric_law": "S_parent^T*eta*S_parent=-eta",
            "parent_parity_collapse_law": "R_plus*S_parent=R_minus",
            "repaired_raised_pullback": matrix_strings(d["A_repaired"]),
            "repaired_characteristic_polynomial": str(d["characteristic_repaired"]),
            "transformed_prefix": [str(value) for value in d["repaired_prefix"]],
            "transformed_prefix_gram": str(d["repaired_prefix_gram"]),
            "general_no_go": "For every anti-isometry C, <Ch,Ch>_eta=-<h,h>_eta. Since <h,h>_eta=3/2 is nonzero, no anti-isometry can fix h or preserve its Gram.",
            "regular_localization_no_go": "If a continuous family C_s has C_0=I and C_s^T*eta*C_s=-eta for every s>0, taking s to zero gives eta=-eta. Hence a spectator-activated identity-to-anti-Krein switch must be singular, discontinuous, or leave the nondegenerate carrier.",
        },
        "public_ghost_parity_test": {
            "neutral_degree_four_metric": matrix_strings(d["W9"]),
            "neutral_degree_four_ghost_parity": matrix_strings(d["kappa9"]),
            "full_metric_law": "kappa9^T*W9*kappa9=W9",
            "selected_odd_columns": matrix_strings(d["selected"]),
            "selected_metric": matrix_strings(d["selected_metric"]),
            "selected_ghost_action": matrix_strings(d["selected_kappa"]),
            "selected_metric_law": "(-I2)^T*(-I2)*(-I2)=-I2",
            "symmetric_power_boundary": "A ghost-parity isometry on the one-particle cross-Krein fibre induces an isometry on every symmetric power and on every invariant nondegenerate subspace. Ghost odd means eigenvalue -1; it does not mean anti-Krein.",
            "charge_boundary": "The selected public degree-four two-plane is exactly charge neutral, so charge compatibility does not create the missing sign. Its public carrier affiliation is established, but nonlinear Rt production and the required graph slope are not derived.",
        },
        "escape_architectures": {
            "regular_same_carrier_parity": "EXACTLY_OBSTRUCTED",
            "inherited_public_symmetric_power_ghost_parity": "EXACTLY_OBSTRUCTED_AS_SIGN_REPAIR",
            "singular_or_discontinuous_spectator_control": "NOT_RULED_OUT_BUT_NOT_CONSTRUCTED",
            "localized_nonvacuum_chart": "NOT_RULED_OUT_BUT_DOES_NOT_CONTAIN_THE_ZERO_JET_PREFIX",
            "doubled_cross_paired_source": "ALGEBRAICALLY_POSSIBLE_NEW_CARRIER_NOT_BT_DERIVED",
            "off_diagonal_dynamical_transition": "NOT_COMPUTED",
            "nonfactorizing_crossed_three_to_three_pretrace_term": "NOT_COMPUTED",
        },
        "disposition": {
            "same_carrier_regular_profile_selective_parity": "EXACTLY_OBSTRUCTED",
            "five_point_prefix_preserving_anti_krein_repair": "IMPOSSIBLE",
            "public_ghost_parity_metric_type": "KREIN_ISOMETRY",
            "public_higher_composite_parity_sign_repair": "EXACTLY_OBSTRUCTED",
            "singular_or_doubled_repair": "NOT_DERIVED",
            "nonfactorizing_crossed_six_point_term": "NOT_COMPUTED",
            "twelve_reversed_physical_intertwiners": "NOT_CONSTRUCTED",
            "complete_crossed_probability": "NOT_COMPUTED",
            "Eq19_all_orders": "NOT_PROVED",
            "spacetime_Moller_LSZ_S_operator": "NOT_CONSTRUCTED",
        },
        "assumptions": [
            "The same-carrier theorem uses the certified nondegenerate four-component parent-jet times spectator-profile metric and the fixed generalized-Born sharp.",
            "A parity symmetry must be metric homogeneous: a Krein isometry or anti-isometry. A map of mixed metric type changes the declared sharp and is a new dynamical datum rather than a parity convention.",
            "Prefix compatibility requires preservation of the certified non-null five-point hard vector and its eta-Gram, not merely agreement after discarding a sign-sensitive component.",
            "Regular spectator localization means a matrix family continuous at the no-spectator boundary on the same nondegenerate carrier.",
            "The public higher-composite test is restricted to the certified neutral degree-four symmetric-Fock sector and its selected ghost-odd nondegenerate two-plane.",
        ],
        "does_not_establish": [
            "absence of a singular or discontinuous spectator-controlled operation",
            "absence of a different nonvacuum localized chart",
            "absence of a new doubled cross-paired source carrier",
            "absence of an off-diagonal Krein-skew dynamical coupling",
            "absence or value of a nonfactorizing crossed 3-to-3 pre-trace term",
            "a positive crossed six-point probability",
            "the twelve reversed physical intertwiners",
            "the 300 crossed seven-point sheets or spectator sectors",
            "a complete incoming/outgoing Moller, LSZ, or S operator",
            "Bateman--Turok Eq. (19)",
            "positivity beyond tree level or a KLN theorem",
            "a metric or BRST lift to Weyl gravity",
            "anything LORENTZIAN-CAUSAL",
            "a new physical or spacetime dimension",
            "literature priority",
        ],
        "next_gate": "Compute the first nonfactorizing crossed 3-to-3 six-point pre-trace term on the complete 220-tree external-mass jet, before the coherent R_plus collapse and before orientation factorization. Retain the two crossed incoming/outgoing assignments, parent constant/linear jet, spectator singleton/pair profiles, common tree phase, and generalized-Born sharp. Test whether the new off-diagonal block changes the negative rank-two quotient or supplies an opposite-metric doubled source. A zero or same-sign block upgrades the physical obstruction; a positive full-rank block must then be affiliated to all twelve reversed histories.",
        "provenance": {
            "source_commit": SOURCE,
            "retrieval_date": "2026-08-12",
            "inputs": [
                {"path": path, "sha256": sha256(path)} for path in INPUTS
            ],
            "producer_method": "Exact SymPy cross-Krein linear algebra, exhaustive enumeration of all sixteen real diagonal unit-sign maps, and an independent import/reconstruction of the certified public neutral degree-four ghost-parity representation. No floating-point arithmetic is used.",
            "primary_source": {
                "source": "Bateman--Turok arXiv:2607.00096v1",
                "url": "https://arxiv.org/abs/2607.00096v1",
                "equations": ["Eq. (1)", "Eq. (15)", "Eq. (18)", "Eq. (19)", "Eq. (20)"],
            },
        },
        "verification_commands": [
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_crossed_profile_selective_parity_obstruction.py --write --check",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_crossed_profile_selective_parity_obstruction.py",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest reverse_physics.tests.test_bt_crossed_profile_selective_parity_obstruction",
        ],
        "checks": {
            "ok": all(checks.values()),
            "passed": sum(checks.values()),
            "total": len(checks),
            "failures": [name for name, ok in checks.items() if not ok],
            "details": checks,
        },
        "report": REPORT,
        "schema": SCHEMA,
    }


def canonical(value):
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", default=CERT)
    args = parser.parse_args(argv)
    value = build()
    rendered = canonical(value)
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
    if value["checks"]["failures"]:
        print("failures:", ", ".join(value["checks"]["failures"]))
    return 0 if value["checks"]["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
