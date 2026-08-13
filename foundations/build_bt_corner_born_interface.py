#!/usr/bin/env python3
"""Build the finite-corner state-representation to Born-rule interface."""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
FOUNDATIONS = ROOT / "foundations"
STATE_SOURCE = FOUNDATIONS / "results/FOUNDATIONAL_BT_SEPARABLE_STATE_CHAIN_ZF_V1.json"
BORN_SOURCE = ROOT / "reverse_physics/certificates/REVERSE_PHYSICS_BT_SEMIFINITE_RELATIVE_BORN_WEIGHT_V1.json"
OUTPUT = FOUNDATIONS / "results/FOUNDATIONAL_BT_CORNER_BORN_INTERFACE_V1.json"
REPORT = FOUNDATIONS / "reports/bt-corner-born-interface.md"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_digest(value: dict[str, Any]) -> str:
    body = dict(value)
    body.pop("canonical_digest", None)
    return hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def fraction(value: Fraction) -> dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}


def transpose(value: tuple[tuple[Fraction, ...], ...]) -> tuple[tuple[Fraction, ...], ...]:
    return tuple(zip(*value))


def product(left: tuple[tuple[Fraction, ...], ...], right: tuple[tuple[Fraction, ...], ...]) -> tuple[tuple[Fraction, ...], ...]:
    return tuple(tuple(sum((a * b for a, b in zip(row, column)), Fraction()) for column in transpose(right)) for row in left)


def matrix_sum(values: list[tuple[tuple[Fraction, ...], ...]]) -> tuple[tuple[Fraction, ...], ...]:
    size = len(values[0])
    return tuple(tuple(sum((value[row][column] for value in values), Fraction()) for column in range(size)) for row in range(size))


def trace(value: tuple[tuple[Fraction, ...], ...]) -> Fraction:
    return sum((value[index][index] for index in range(len(value))), Fraction())


def sharp(value: tuple[tuple[Fraction, ...], ...], j: tuple[tuple[Fraction, ...], ...]) -> tuple[tuple[Fraction, ...], ...]:
    return product(product(j, transpose(value)), j)


def witness() -> dict[str, Any]:
    z = Fraction()
    o = Fraction(1)
    j = ((o, z, z), (z, o, z), (z, z, -o))
    s = ((Fraction(3, 5), Fraction(-4, 5), z), (Fraction(4, 5), Fraction(3, 5), z), (z, z, o))
    incoming = ((o, z, z), (z, z, z), (z, z, z))
    outputs = [
        ((o, z, z), (z, z, z), (z, z, z)),
        ((z, z, z), (z, o, z), (z, z, z)),
        ((z, z, z), (z, z, z), (z, z, o)),
    ]
    processes = [product(product(output, s), incoming) for output in outputs]
    effects = [product(sharp(process, j), process) for process in processes]
    probabilities = [trace(effect) for effect in effects]
    state_probabilities = [trace(product(product(incoming, product(sharp(s, j), product(output, s))), incoming)) for output in outputs]
    assert probabilities == state_probabilities == [Fraction(9, 25), Fraction(16, 25), Fraction()]
    assert sum(probabilities, Fraction()) == 1
    assert matrix_sum(outputs) == ((o, z, z), (z, o, z), (z, z, o))
    j_null = ((z, o), (o, z))
    b = ((Fraction(3, 5), z), (z, Fraction(3, 5)))
    c = ((z, Fraction(4, 5)), (z, z))
    a = matrix_sum([b, c])
    null_traces = {
        "Tr(C^sharp C)": trace(product(sharp(c, j_null), c)),
        "Tr(B^sharp C)": trace(product(sharp(b, j_null), c)),
        "Tr(C^sharp B)": trace(product(sharp(c, j_null), b)),
        "Tr(B^sharp B)": trace(product(sharp(b, j_null), b)),
        "Tr(A^sharp A)": trace(product(sharp(a, j_null), a)),
    }
    assert sharp(c, j_null) == c
    assert list(null_traces.values()) == [z, z, z, Fraction(18, 25), Fraction(18, 25)]
    return {
        "arithmetic": "EXACT_RATIONAL",
        "fundamental_symmetry": "J=diag(1,1,-1)",
        "incoming_corner": "P_in=diag(1,0,0), r=Tr(P_in)=1",
        "cross_krein_isometry": "S=[[3/5,-4/5,0],[4/5,3/5,0],[0,0,1]]",
        "output_partition": ["P_1=diag(1,0,0)", "P_2=diag(0,1,0)", "P_3=diag(0,0,1)"],
        "probabilities": [fraction(item) for item in probabilities],
        "probability_sum": fraction(sum(probabilities, Fraction())),
        "nonzero_weak_null_remainder": {
            "fundamental_symmetry": "J_null=[[0,1],[1,0]]",
            "B": "(3/5)1",
            "C": "(4/5)E_01, C!=0, C^sharp=C",
            "traces": {key: fraction(item) for key, item in null_traces.items()},
            "conclusion": "The public quadratic weight equals the positive B-sector weight even with a nonzero trace-null remainder.",
        },
        "identities": {
            "cross_krein_isometry": "S^sharp S=1",
            "effect_map": "E_i=(P_i S P_in)^sharp(P_i S P_in)=P_in S^sharp P_i S P_in",
            "same_state_evaluation": "p_i=omega_P_in(S^sharp P_i S)=Tr(E_i)/r",
            "normalization": "sum_i p_i=omega_P_in(S^sharp S)=omega_P_in(1)=1",
        },
    }


def build() -> dict[str, Any]:
    state = load(STATE_SOURCE)
    born = load(BORN_SOURCE)
    if state.get("result_id") != "FOUNDATIONAL_BT_SEPARABLE_STATE_CHAIN_ZF_V1":
        raise ValueError("state source identity")
    theorem = born.get("conditional_Born_theorem", {})
    if theorem.get("disposition") != "PROVED_ON_FINITE_DETECTOR_IDEAL_UNDER_WEAK_GHOST_HYPOTHESES":
        raise ValueError("Born source disposition")
    source_input_audit = []
    for item in born.get("provenance", {}).get("inputs", []):
        path = ROOT / item["path"]
        actual = sha(path)
        source_input_audit.append({
            "path": item["path"],
            "recorded_sha256": item["sha256"],
            "actual_sha256": actual,
            "status": "MATCH" if actual == item["sha256"] else "DRIFT",
        })
    drift = [item for item in source_input_audit if item["status"] == "DRIFT"]
    if [item["path"] for item in drift] != ["notes/bateman-turok-embedding.md"]:
        raise ValueError("unexpected predecessor provenance drift")
    value = {
        "schema_version": "foundational-bt-corner-born-interface-v1",
        "result_id": "FOUNDATIONAL_BT_CORNER_BORN_INTERFACE_V1",
        "result_kind": "CERTIFIED_CROSS_CELL_INTERFACE",
        "lifecycle": "SUFFICIENCY_PROVED",
        "created": "2026-08-13",
        "repository_base_commit": "64d2a94daf3070e1e422d71d69142161e14c11ff",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "question": "Does the explicitly represented finite detector-corner state extend to a normalized Born-type probability rule for the same corner when the public Krein process satisfies the certified weak-ghost hypotheses?",
        "answer": "Yes, conditionally and exactly on the finite detector ideal. The state-representation source and the Born theorem use the identical normalized corner functional omega_P(T)=Tau(PTP)/Tau(P). For a finite J-even incoming projection P_in, a cross-Krein isometry S, an exhaustive finite output partition P_i, and the certified weak-ghost decomposition, the event map sends P_i to E_i=(P_i S P_in)^sharp(P_i S P_in). The same omega_P_in evaluates p_i=Tau(E_i)/Tau(P_in); the imported theorem proves p_i>=0 and sum_i p_i=1. An independent rational witness gives (9/25,16/25,0). The relation is a CONDITIONAL_BRIDGE between the algebraic state-representation and Krein probability-rule cells, not an identification of their full carriers or an unconditional rule for arbitrary processes.",
        "interface": {
            "id": "STATE_TO_PROBABILITY",
            "label": "Finite detector-corner state representation to conditional Krein Born rule",
            "status": "CERTIFIED",
            "relation": "CONDITIONAL_BRIDGE",
            "source_coordinates": [
                {"foundation": "CLASSICAL_STANDARD", "carrier": "ALGEBRAIC_CSTAR", "obligation": "STATE_REPRESENTATION"}
            ],
            "target_coordinates": [
                {"foundation": "CLASSICAL_STANDARD", "carrier": "KREIN_INDEFINITE", "obligation": "PROBABILITY_RULE"}
            ],
            "carrier_transition": "ALGEBRAIC_CSTAR_TO_KREIN_INDEFINITE_VIA_SHARED_FINITE_COMPANION_CORNER",
            "scope": "Finite-trace detector corners and finite exhaustive output partitions satisfying the five displayed hypotheses.",
            "evidence": ["FOUNDATIONAL_BT_CORNER_BORN_INTERFACE_V1"],
        },
        "shared_object_ledger": [
            {"id": "H0", "object": "the companion Hilbertized detector carrier", "source_role": "GNS/state representation carrier", "target_role": "carrier on which J, P_in, S, and P_i act", "identity_status": "IDENTICAL_OBJECT"},
            {"id": "TAU", "object": "the faithful normal semifinite trace Tau", "source_role": "normalizes the finite corner state", "target_role": "normalizes finite process weights", "identity_status": "IDENTICAL_OBJECT"},
            {"id": "P_IN", "object": "a finite-rank J-even incoming projection with r=Tau(P_in)>0", "source_role": "defines omega_P_in", "target_role": "defines A_i=P_i S P_in", "identity_status": "IDENTICAL_OBJECT"},
            {"id": "OMEGA_P", "object": "omega_P(T)=Tau(PTP)/Tau(P)", "source_role": "represented normal corner state", "target_role": "the functional evaluating every event effect", "identity_status": "IDENTICAL_OBJECT"},
        ],
        "typed_maps": [
            {"id": "CORNER_STATE", "from": "(Tau,P_in)", "to": "omega_P_in", "type": "NORMALIZED_POSITIVE_FUNCTIONAL", "formula": "omega_P_in(T)=Tau(P_in T P_in)/r"},
            {"id": "EVENT_EFFECT", "from": "(P_i,S,P_in)", "to": "E_i", "type": "PUBLIC_KREIN_PROCESS_EFFECT", "formula": "E_i=(P_i S P_in)^sharp(P_i S P_in)"},
            {"id": "PROBABILITY", "from": "(omega_P_in,E_i)", "to": "p_i", "type": "NORMALIZED_EVENT_PROBABILITY", "formula": "p_i=omega_P_in(S^sharp P_i S)=Tau(E_i)/r"},
        ],
        "hypotheses": theorem["hypotheses"],
        "proof_obligations": [
            {"id": "SOURCE_STATE_NORMALIZED", "status": "PASS", "evidence": "The state source constructs omega_P for every finite nonzero P."},
            {"id": "SHARED_OBJECT_IDENTITY", "status": "PASS", "evidence": "Both pinned sources use the same l2(Z) companion carrier, semifinite trace, finite projection, and corner formula."},
            {"id": "EVENT_MAP_TYPED", "status": "PASS", "evidence": "Krein-self-adjoint P_i and P_in type E_i as the quadratic process effect on the shared finite corner."},
            {"id": "POSITIVITY", "status": "PASS", "evidence": theorem["positivity_proof"]},
            {"id": "NORMALIZATION", "status": "PASS", "evidence": theorem["normalization_proof"]},
            {"id": "EXACT_NONTRIVIAL_WITNESS", "status": "PASS", "evidence": "The independent three-output rational fixture yields 9/25, 16/25, and 0."},
            {"id": "NONZERO_WEAK_NULL_REMAINDER", "status": "PASS", "evidence": "A second exact fixture has C!=0, all three null/cross traces zero, and Tr(A^sharp A)=Tr(B^sharp B)=18/25."},
        ],
        "exact_witness": witness(),
        "proof_authority": {
            "status": "INDEPENDENT_REDERIVATION",
            "meaning": "The foundations checker re-derives the event-effect identity, probability normalization, and both rational fixtures. It does not treat a reproduction of the predecessor producer as verification.",
            "general_argument": [
                "Krein-self-adjoint projections give A_i^sharp A_i=P_in S^sharp P_i S P_in.",
                "Exhaustiveness and cross-Krein isometry give sum_i Tau(A_i^sharp A_i)=Tau(P_in)=r.",
                "The weak decomposition and three trace-null identities give Tau(A_i^sharp A_i)=Tau(B_i^* B_i)>=0.",
            ],
        },
        "predecessor_source_audit": {
            "verifier_status": "PROVENANCE_DRIFT",
            "input_audit": source_input_audit,
            "drift_scope": "The only mismatch is the evolving narrative note notes/bateman-turok-embedding.md; all three mathematical/work-item inputs match their recorded hashes.",
            "claim_boundary": "The predecessor verifier is not reported as passing. Its theorem statement is independently re-derived here, and the stale note pin is not used as mathematical evidence.",
        },
        "provenance": {
            "inputs": [
                {"path": str(STATE_SOURCE.relative_to(ROOT)), "sha256": sha(STATE_SOURCE), "role": "explicit separable detector state and GNS representation"},
                {"path": str(BORN_SOURCE.relative_to(ROOT)), "sha256": sha(BORN_SOURCE), "role": "conditional finite-ideal public Krein Born theorem"},
                {"path": "notes/bateman-turok-embedding.md", "sha256": sha(ROOT / "notes/bateman-turok-embedding.md"), "role": "audited narrative drift input; not mathematical proof authority"},
            ]
        },
        "independent_checker": {
            "path": "foundations/check_bt_corner_born_interface.py",
            "checks": ["source identities and hashes", "shared corner formula", "exact rational cross-Krein isometry", "event-effect identity", "same-state evaluation", "probability positivity and normalization", "claim boundaries"],
        },
        "claim_flags": {
            "cross_cell_interface_certified": True,
            "same_corner_state_used_on_both_sides": True,
            "event_effect_map_constructed": True,
            "conditional_probabilities_nonnegative": True,
            "conditional_probabilities_normalized": True,
            "interface_independent_rederivation_passed": True,
            "predecessor_note_only_provenance_drift_recorded": True,
            "legacy_semifinite_source_verifier_passed": False,
            "arbitrary_krein_process_probability_rule": False,
            "physical_thermodynamic_state_selected": False,
            "all_order_bt_probability_constructed": False,
            "lorentzian_claim": False,
        },
        "does_not_establish": [
            "a probability rule for arbitrary Krein operators without the five displayed hypotheses",
            "identity of the full algebraic C* and Krein carriers",
            "a canonical choice of the finite incoming projection",
            "a thermodynamic normal state or finite trace of the identity",
            "the nonlinear Bateman-Turok Eq. (19), a complete NLO probability, or an all-order process",
            "a gravitational, BV-BRST, QME, residual-transfer, or LORENTZIAN-CAUSAL result",
            "empirical agreement or a complete physical theory",
            "repair or successful replay of the predecessor certificate's stale narrative-note provenance pin",
        ],
        "human_report": "foundations/reports/bt-corner-born-interface.md",
    }
    value["canonical_digest"] = canonical_digest(value)
    return value


def render(value: dict[str, Any]) -> str:
    probabilities = value["exact_witness"]["probabilities"]
    formatted = ", ".join(f"{item['numerator']}/{item['denominator']}" for item in probabilities)
    lines = [
        "# Certified BT finite-corner state-to-probability interface",
        "",
        f"**Result:** `{value['result_id']}`",
        "",
        "**Lifecycle:** `SUFFICIENCY_PROVED`",
        "",
        "**Dependency tags:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`",
        "",
        "## Result",
        "",
        value["answer"],
        "",
        "This closes one precise cross-cell interface:",
        "",
        "```text",
        "CLASSICAL_STANDARD × ALGEBRAIC_CSTAR × STATE_REPRESENTATION",
        "             -- CONDITIONAL_BRIDGE -->",
        "CLASSICAL_STANDARD × KREIN_INDEFINITE × PROBABILITY_RULE",
        "```",
        "",
        "## Why it is genuinely the same state",
        "",
        "The shared-object ledger pins the carrier, semifinite trace, incoming",
        "projection, and normalized corner functional on both sides. The target does",
        "not introduce a second expectation functional: it evaluates every event effect",
        "with the source state `omega_P_in`.",
        "",
        "For `A_i=P_i S P_in`, the bridge is",
        "",
        "```text",
        "E_i=A_i^sharp A_i=P_in S^sharp P_i S P_in",
        "p_i=omega_P_in(S^sharp P_i S)=Tau(E_i)/Tau(P_in).",
        "```",
        "",
        "The weak-ghost argument is re-derived under five explicit hypotheses. The",
        "independent exact witness gives probabilities",
        f"`({formatted})`, summing to one.",
        "A second exact fixture retains a nonzero weak null remainder while all null and",
        "cross traces vanish and the public weight remains `18/25`.",
        "",
        "## Why the relation is conditional",
        "",
        "The state exists for every finite nonzero corner, but arbitrary Krein process",
        "effects need not be positive. Cross-Krein isometry, an exhaustive finite output",
        "partition, paired-domain preservation, and weak ghost orthogonality are real",
        "extra hypotheses. The certified relation is therefore `CONDITIONAL_BRIDGE`,",
        "not `IDENTICAL_OBJECT` or an unconditional generalized Born theorem.",
        "",
        "## Predecessor provenance audit",
        "",
        "The legacy semifinite certificate's verifier currently fails its input-hash rail",
        "because the narrative embedding note evolved after the certificate was issued.",
        "Its three mathematical/work-item inputs still match. This result records that",
        "failure rather than calling it a pass, and independently re-derives the algebraic",
        "interface and both exact fixtures. It does not repair or relock the predecessor.",
        "",
        "## Verification",
        "",
        "```text",
        "python3 foundations/build_bt_corner_born_interface.py --check",
        "python3 foundations/check_bt_corner_born_interface.py",
        "python3 foundations/verify_bt_corner_born_interface.py",
        "python3 -m unittest foundations.tests.test_bt_corner_born_interface",
        "```",
        "",
        "## Boundaries",
        "",
        *["- This does not establish " + item + "." for item in value["does_not_establish"]],
        "",
    ]
    return "\n".join(lines)


def generated() -> tuple[bytes, bytes]:
    value = build()
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode(), render(value).encode()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result_bytes, report_bytes = generated()
    outputs = ((OUTPUT, result_bytes), (REPORT, report_bytes))
    stale = [str(path.relative_to(ROOT)) for path, content in outputs if not path.is_file() or path.read_bytes() != content]
    if args.check:
        if stale:
            print("FOUNDATIONAL_BT_CORNER_BORN_INTERFACE_V1: stale: " + ", ".join(stale))
            return 1
        print("FOUNDATIONAL_BT_CORNER_BORN_INTERFACE_V1: generated artifacts current")
        return 0
    for path, content in outputs:
        path.write_bytes(content)
    print("FOUNDATIONAL_BT_CORNER_BORN_INTERFACE_V1: wrote result and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
