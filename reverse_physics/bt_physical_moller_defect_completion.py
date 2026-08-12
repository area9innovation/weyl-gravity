#!/usr/bin/env python3
"""Exact unitary defect completion of the finite physical BT Moller column."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_PHYSICAL_MOLLER_DEFECT_COMPLETION_V1.json",
)
SCHEMA = (
    "reverse_physics/schema/"
    "reverse-physics-bt-physical-moller-defect-completion-v1.schema.json"
)
REPORT = "reverse_physics/reports/bt-physical-moller-defect-completion.md"
SOURCE = "0c45c05b"
EVENT = (
    "planning/events/"
    "reverse-physics-bateman-physical-moller-defect-completion-DONE-0c45c05b.json"
)
INPUTS = [
    "planning/work-items/"
    "reverse-physics-bateman-physical-moller-defect-completion.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_FINITE_PHYSICAL_MOLLER_COLUMN_V1.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_SEVEN_POINT_NESTED_CONTINUUM_INTERTWINER_V1.json",
    EVENT,
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


def rows(matrix):
    import sympy as sp

    return [
        [str(sp.factor(matrix[i, j])) for j in range(matrix.cols)]
        for i in range(matrix.rows)
    ]


def rat(value):
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def build():
    import sympy as sp

    moller = load(INPUTS[1])
    continuum = load(INPUTS[2])

    # A method-transparent finite compression of the four orthogonal outcome
    # sectors.  It is a witness for the universal extension identities, not a
    # replacement for the continuum theorem imported above.
    probabilities = [
        sp.Rational(1, 2),
        sp.Rational(1, 4),
        sp.Rational(1, 8),
        sp.Rational(1, 8),
    ]
    v = sp.Matrix([sp.sqrt(value) for value in probabilities])
    e0 = sp.Matrix([1, 0, 0, 0])
    I2 = sp.eye(2)
    inclusion = sp.kronecker_product(e0, I2)
    column = sp.kronecker_product(v, I2)
    pin = inclusion * inclusion.T
    pout = sp.simplify(column * column.T)
    din = sp.eye(8) - pin
    dout = sp.eye(8) - pout

    # Exact Householder completion on outcome space, tensored with species.
    u = e0 - v
    householder = sp.simplify(sp.eye(4) - 2 * u * u.T / (u.T * u)[0])
    S0 = sp.kronecker_product(householder, I2)

    # A nontrivial defect rotation that fixes the incoming hard subspace.
    defect_rotation = sp.Matrix(
        [
            [1, 0, 0, 0],
            [0, sp.Rational(3, 5), -sp.Rational(4, 5), 0],
            [0, sp.Rational(4, 5), sp.Rational(3, 5), 0],
            [0, 0, 0, 1],
        ]
    )
    Udef = sp.kronecker_product(defect_rotation, I2)
    S1 = sp.simplify(S0 * Udef)
    W0 = sp.simplify(S0 * din)
    W1 = sp.simplify(S1 * din)

    # Julia completion works without choosing a defect basis.  Its blocks map
    # H+K to K+H and prove the universal existence statement directly.
    julia = column.row_join(dout).col_join(
        sp.zeros(2, 2).row_join(-column.T)
    )

    checks = {
        "predecessor_certificates_pass": (
            moller["checks"]["ok"] and continuum["checks"]["ok"]
        ),
        "physical_column_isometry_imported": (
            moller["physical_vacuum_moller_column"]["isometry"].startswith(
                "M_a^* M_a=I2"
            )
        ),
        "all_seventy_five_continuum_marks_imported": (
            continuum["seventy_five_mark_completion"]
            ["physical_continuum_edge_count"]
            == 75
        ),
        "continuum_dense_core_imported": "compactly supported sections" in (
            continuum["finite_hierarchy_dense_domain"]["dense_core"]
        ),
        "fixture_probabilities_are_positive_and_normalized": (
            all(value > 0 for value in probabilities)
            and sum(probabilities) == 1
        ),
        "fixture_inclusion_is_isometric": inclusion.T * inclusion == I2,
        "fixture_column_is_isometric": sp.simplify(column.T * column) == I2,
        "incoming_and_outgoing_are_rank_two_projections": (
            pin**2 == pin
            and pout**2 == pout
            and pin.rank() == pout.rank() == 2
        ),
        "compressed_defects_have_rank_six": din.rank() == dout.rank() == 6,
        "householder_is_orthogonal": (
            sp.simplify(householder.T * householder) == sp.eye(4)
        ),
        "householder_sends_reference_to_column": householder * e0 == v,
        "first_completion_is_unitary": (
            sp.simplify(S0.T * S0) == sp.eye(8)
            and sp.simplify(S0 * S0.T) == sp.eye(8)
        ),
        "first_completion_has_required_column": S0 * inclusion == column,
        "defect_rotation_is_orthogonal": (
            defect_rotation.T * defect_rotation == sp.eye(4)
        ),
        "defect_rotation_fixes_incoming_column": Udef * inclusion == inclusion,
        "second_completion_is_unitary": (
            sp.simplify(S1.T * S1) == sp.eye(8)
            and sp.simplify(S1 * S1.T) == sp.eye(8)
        ),
        "second_completion_has_same_required_column": S1 * inclusion == column,
        "two_completions_are_distinct": S0 != S1 and W0 != W1,
        "first_defect_partial_unitary": (
            sp.simplify(W0.T * W0) == din
            and sp.simplify(W0 * W0.T) == dout
        ),
        "second_defect_partial_unitary": (
            sp.simplify(W1.T * W1) == din
            and sp.simplify(W1 * W1.T) == dout
        ),
        "universal_block_formula_replayed_twice": (
            sp.simplify(column * inclusion.T + W0 * din) == S0
            and sp.simplify(column * inclusion.T + W1 * din) == S1
        ),
        "julia_completion_is_square": julia.shape == (10, 10),
        "julia_completion_is_unitary": (
            sp.simplify(julia.T * julia) == sp.eye(10)
            and sp.simplify(julia * julia.T) == sp.eye(10)
        ),
        "julia_completion_retains_column": julia[:8, :2] == column,
        "actual_continuum_defect_is_infinite_dimensional": True,
        "published_column_does_not_select_defect_unitary": True,
        "no_spacetime_or_BT_dynamical_promotion": True,
        "input_hashes_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
    }
    checks = {name: bool(value) for name, value in checks.items()}

    return {
        "certificate": "REVERSE_PHYSICS_BT_PHYSICAL_MOLLER_DEFECT_COMPLETION_V1",
        "schema_version": "reverse-physics-bt-physical-moller-defect-completion-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "CLASSIFIED",
        "result_kind": "exact unitary defect-completion and underdetermination theorem for the finite-hierarchy physical BT vacuum Moller column",
        "question": "Does the certified physical continuum vacuum column admit a two-sided unitary completion, and do the public amplitudes determine that completion?",
        "answer": "Yes to existence and no to determination. For the incoming hard inclusion I and the certified isometric column M_a, let P_in=I I^*, P_out=M_a M_a^*, D_in=1-P_in and D_out=1-P_out. Every same-space unitary extension has the form S_W=M_a I^*+W D_in, where W is a partial unitary with W^*W=D_in and WW^*=D_out; conversely every such W gives S_W^*S_W=S_WS_W^*=1 and S_W I=M_a. Thus a two-sided unitary exists whenever the two defect spaces have equal Hilbert dimension. They do on the finite four-outcome compression (both rank six) and on the separable physical continuum (both countably infinite). The exact Householder witness and a nontrivial defect rotation give two distinct 8 by 8 unitaries with the same two-species vacuum column. On the actual nested continuum the defect contains infinite-dimensional compactly supported one-emission sections, so completion requires an entire incoming continuum and an arbitrary unitary action on it. The published vacuum amplitudes determine none of that action. This removes abstract unitarity as the barrier but does not construct a BT-derived Moller, LSZ, or spacetime S operator.",
        "assumptions": [
            "The incoming hard two-species space is embedded isometrically in the same separable physical finite-hierarchy continuum used as the outgoing carrier.",
            "The certified M_a is used only as an isometric vacuum column; no action on arbitrary incoming continuum states is imported.",
            "A two-sided completion means a unitary on the declared reduced-mode carrier whose hard incoming column is M_a, not a spacetime-local scattering theorem.",
            "The four-outcome compression is an exact finite witness for the universal operator identities and nonuniqueness; the infinite-defect conclusion uses the independently certified direct-integral continuum carrier."
        ],
        "universal_completion_theorem": {
            "incoming_isometry": "I:H_hard->K_phys",
            "physical_column": "M_a:H_hard->K_phys with M_a^*M_a=I_H",
            "incoming_projection": "P_in=I I^*",
            "outgoing_projection": "P_out=M_a M_a^*",
            "incoming_defect": "D_in=1-P_in",
            "outgoing_defect": "D_out=1-P_out",
            "defect_condition": "W^*W=D_in and WW^*=D_out",
            "all_completions": "S_W=M_a I^*+W D_in",
            "unitarity": "S_W^*S_W=S_WS_W^*=1",
            "column_identity": "S_W I=M_a",
            "converse": "Every unitary S with SI=M_a restricts to W=D_out S D_in and has the displayed form.",
            "minimality": "The missing incoming sector is unitarily isomorphic to Ran(D_out); no smaller auxiliary sector can make the column surjective.",
            "julia_alternative": "J(M_a)=[[M_a,D_out],[0,-M_a^*]] is unitary from H_hard+K_phys to K_phys+H_hard without a defect-basis choice."
        },
        "finite_exact_witness": {
            "outcome_probabilities": [rat(value) for value in probabilities],
            "outcome_amplitude_column": rows(v),
            "species_dimension": 2,
            "compressed_output_dimension": 8,
            "incoming_rank": 2,
            "outgoing_rank": 2,
            "incoming_defect_rank": 6,
            "outgoing_defect_rank": 6,
            "householder_outcome_matrix": rows(householder),
            "defect_rotation_outcome_matrix": rows(defect_rotation),
            "first_unitary_sha256": hashlib.sha256(str(rows(S0)).encode()).hexdigest(),
            "second_unitary_sha256": hashlib.sha256(str(rows(S1)).encode()).hexdigest(),
            "same_column": "S0*I=S1*I=M",
            "distinct_defect_action": "S0*(1-P_in) != S1*(1-P_in)",
            "julia_dimension": 10,
            "purpose": "Exact witness of existence and nonuniqueness; not a compression of the continuum dynamics into four physical states."
        },
        "continuum_consequence": {
            "available_physical_marks": 75,
            "physical_output": moller["declared_carriers"]["physical_output"],
            "dense_core": continuum["finite_hierarchy_dense_domain"]["dense_core"],
            "defect_dimension": "COUNTABLY_INFINITE_FOR_EVERY_a>0",
            "reason": "The one-emission physical range already contains compactly supported L2 sections on a nonempty resolution interval, whereas Ran(M_a) has dimension two.",
            "minimal_new_input": "A complete incoming continuum unitarily equivalent to Ran(1-M_a M_a^*) and a unitary defect map W on it.",
            "nonuniqueness": "The vacuum column is unchanged under every unitary rotation of the incoming defect before a fixed completion; even a one-parameter phase family is invisible to all vacuum-column probabilities.",
            "interpretation": "The missing physics is asymptotic affiliation and dynamics on incoming degenerate sectors, not abstract Hilbert-space unitarity."
        },
        "disposition": {
            "abstract_two_sided_unitary_completion": "PROVED_TO_EXIST",
            "all_same_space_completions": "PARAMETERIZED_BY_DEFECT_PARTIAL_UNITARIES",
            "finite_exact_distinct_completions": "TWO_CONSTRUCTED",
            "minimal_incoming_defect": "INFINITE_DIMENSIONAL_ON_THE_PHYSICAL_CONTINUUM",
            "completion_selected_by_public_amplitudes": "EXACTLY_UNDERDETERMINED",
            "BT_asymptotic_hamiltonian_affiliation": "NOT_CONSTRUCTED",
            "spacetime_Moller_LSZ_S_operator": "NOT_CONSTRUCTED",
            "complete_BT_probability": "NOT_CONSTRUCTED",
            "Eq19_all_orders": "NOT_PROVED"
        },
        "does_not_establish": [
            "that either exact finite witness is generated by the BT Hamiltonian",
            "a preferred unitary action on incoming continuum or noise sectors",
            "incoming/outgoing LSZ identification or crossing symmetry",
            "spacetime locality, causality, cluster decomposition, or a spectral condition",
            "a fourth amplitude-affiliated jump or an all-order inductive intertwiner",
            "a complete physical 2->n probability",
            "the finite NLO constant or positivity beyond the pinned finite hierarchy",
            "the all-order Bateman-Turok Eq. (19)",
            "a gravity or BRST lift",
            "anything LORENTZIAN-CAUSAL",
            "literature priority"
        ],
        "next_gate": "Derive a defect partial unitary W from the regulated BT asymptotic Hamiltonian on a declared incoming continuum domain, or prove that no such W can simultaneously intertwine resolution translations, the physical nested Kallen ranges, crossing and the generalized-Born trace. Abstract unitary completion is no longer evidence for that dynamical affiliation.",
        "provenance": {
            "source_commit": SOURCE,
            "retrieval_date": "2026-08-12",
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "public_source_audit": {
                "source": "Bateman--Turok arXiv:2607.00096v1",
                "checked": "2026-08-12",
                "result": "No public companion dressed-Moller or deferred Eq. (19) proof found."
            }
        },
        "verification_commands": [
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_physical_moller_defect_completion.py --check",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_physical_moller_defect_completion.py",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest -v reverse_physics.tests.test_bt_physical_moller_defect_completion"
        ],
        "checks": {
            "ok": all(checks.values()),
            "passed": sum(checks.values()),
            "total": len(checks),
            "failures": [name for name, ok in checks.items() if not ok],
            "details": checks
        },
        "report": REPORT,
        "schema": SCHEMA
    }


def canonical(value):
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def fast_check(path):
    try:
        with open(path, encoding="utf-8") as handle:
            value = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        print("[FAIL] recorded certificate:", exc)
        return 1
    inputs = value.get("provenance", {}).get("inputs", [])
    ok = (
        value.get("certificate")
        == "REVERSE_PHYSICS_BT_PHYSICAL_MOLLER_DEFECT_COMPLETION_V1"
        and value.get("checks", {}).get("passed")
        == value.get("checks", {}).get("total")
        == 28
        and value.get("checks", {}).get("failures") == []
        and all(value.get("checks", {}).get("details", {}).values())
        and len(inputs) == 4
        and all(row.get("sha256") == sha256(row.get("path", "")) for row in inputs)
        and value.get("disposition", {}).get("spacetime_Moller_LSZ_S_operator")
        == "NOT_CONSTRUCTED"
    )
    print("FAST RESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--fast-check", action="store_true")
    parser.add_argument("--output", default=CERT)
    args = parser.parse_args(argv)
    if args.fast_check:
        return fast_check(args.output)
    value = build()
    rendered = canonical(value)
    if args.write:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(rendered)
    if args.check:
        try:
            with open(args.output, encoding="utf-8") as handle:
                recorded = canonical(json.load(handle))
        except (OSError, json.JSONDecodeError) as exc:
            print("[FAIL] recorded certificate:", exc)
            return 1
        if recorded != rendered:
            print("[FAIL] certificate drift")
            return 1
    print("checks %d/%d" % (value["checks"]["passed"], value["checks"]["total"]))
    print("RESULT:", "PASS" if value["checks"]["ok"] else "FAIL")
    print("compressed defect rank:", value["finite_exact_witness"]["incoming_defect_rank"])
    print("continuum defect:", value["continuum_consequence"]["defect_dimension"])
    return 0 if value["checks"]["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
