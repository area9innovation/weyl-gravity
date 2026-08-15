#!/usr/bin/env python3
"""Build the strict pure-Weyl cubic source witness and q3 source inventory."""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

import cylinder_cubic_bach_evaluator as cubic
import cylinder_polarized_bach_evaluator as point
from local_q1_q2_receiver import apply_q1, field_fixture


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_386_PURE_WEYL_Q3_WITNESS_V1.json"
REPORT = HERE / "REPORT_STRICT_386_PURE_WEYL_Q3_WITNESS_V1.md"

OBSTRUCTION = HERE / "certificates/STRICT_386_QUADRATIC_TRUNCATION_LAMBDA2_SOURCE_OBSTRUCTION_V1.json"
NATURAL_Q2 = HERE / "certificates/STRICT_BACH_NATURAL_OPERATOR_AST_V1.json"
PAIRING = HERE / "certificates/STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1.json"
ENDPOINT = HERE / "certificates/STRICT_386_ENDPOINT_Q1_CONTENT_BRIDGE_V1.json"
ACTION = ROOT / "d_quotient_classical/minimal_bv_antifield/foundation/action_normalization.json"
BERGER_Q3 = ROOT / "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_Q3.json"
BERGER_PAYLOAD = ROOT / "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_Q3_PAYLOAD.json"
ENGINE = HERE / "cylinder_cubic_bach_evaluator.py"
INPUTS = (
    (OBSTRUCTION, "STRICT_386_QUADRATIC_TRUNCATION_LAMBDA2_SOURCE_OBSTRUCTION_V1", "q2 Jacobiator and required q3 target"),
    (NATURAL_Q2, "STRICT_BACH_NATURAL_OPERATOR_AST_V1", "portable pure-Weyl action-normalized Bach map"),
    (PAIRING, "STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1", "strict 386-row carrier and pairing convention"),
    (ENDPOINT, "STRICT_386_ENDPOINT_Q1_CONTENT_BRIDGE_V1", "strict thirty-row endpoint bridge"),
    (ACTION, "PURE_WEYL_ACTION_NORMALIZATION_V2", "authoritative classical action normalization"),
    (BERGER_Q3, "BERGER_SUPPORT_LOCAL_Q3", "complete q3 comparison source on a different theory and background"),
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def recorded_digest(value: Mapping[str, Any]) -> str:
    return digest({key: item for key, item in value.items() if key != "sha256"})


def metric_payload(value: Mapping[tuple[int, int], point.Jet]) -> dict[tuple[int, int], dict[tuple[int, int, int, int], Fraction]]:
    return {
        pair: {
            alpha: coefficient
            for a_degree, b_degree, alpha, coefficient in value[pair].terms
            if a_degree == b_degree == 0
        }
        for pair in point.PAIRS
    }


def exact_cubic_fixture() -> dict[str, Any]:
    background = point.flat_background(7)
    generator = field_fixture("c", 1, 7)
    field = apply_q1("q1_h_c", generator, background, 6)
    data = cubic.diagonal_cubic_bach_data(
        metric_payload(field), background=background, output_coordinate_order=1
    )
    rows = [
        {
            "row_id": "h_star_" + str(pair[0]) + str(pair[1]),
            "component": list(pair),
            "terms": data["q3_metric_euler_density"][pair],
        }
        for pair in point.PAIRS
    ]
    payload = {
        "fixture_id": "FLAT_PURE_DIFF_GAUGE_SEED_1",
        "background": "four-dimensional flat metric diag(-1,1,1,1)",
        "input": "x=q1(c_seed_1)",
        "input_status": "q1(x)=0 exactly",
        "operator": "D^3 E_g(x,x,x), E_g=-2 sqrt(abs(g)) B(g)^sharp",
        "extraction": "6 times the coefficient of t^3 in E(g+t x)",
        "taylor_convention": "suspended-graded-symmetric-factorial-v1",
        "coefficient_field": "Q",
        "metric_output_rows": rows,
        "nonzero_metric_output_rows": sum(bool(row["terms"]) for row in rows),
        "metric_output_term_count": sum(len(row["terms"]) for row in rows),
        "q1_q3_diff_noether": data["q1_q3_diff_noether"],
        "q1_q3_weyl_noether": data["q1_q3_weyl_noether"],
        "nonlinear_weyl_identity_t3": data["nonlinear_weyl_identity_t3"],
    }
    payload["sha256"] = digest(payload)
    return payload


def build() -> dict[str, Any]:
    values = {path: json.loads(path.read_text()) for path, _, _ in INPUTS}
    for path, expected, _ in INPUTS:
        value = values[path]
        if value.get("result_id", value.get("schema")) != expected:
            raise ValueError(f"dependency identity drift: {path}")
    obstruction = values[OBSTRUCTION]
    natural = values[NATURAL_Q2]
    pairing = values[PAIRING]
    endpoint = values[ENDPOINT]
    action = values[ACTION]
    berger = values[BERGER_Q3]
    berger_payload = json.loads(BERGER_PAYLOAD.read_text())

    if action.get("Euler_coordinate") != "E_g^{mu nu}:=delta S/delta g_{mu nu}=-2 sqrt(abs(g)) B^{mu nu}":
        raise ValueError("pure-Weyl action normalization drift")
    if natural.get("scope", {}).get("theory") != "strict pure-Weyl metric Euler row":
        raise ValueError("natural pure-Weyl operator scope drift")
    if pairing.get("component_basis", {}).get("dimension") != 386:
        raise ValueError("strict carrier size drift")
    if endpoint.get("bridge", {}).get("endpoint_dimension", 30) != 30:
        raise ValueError("strict endpoint size drift")
    if berger.get("setting_id") != "compact_positive_berger_clock_fixed_coupling_linearized":
        raise ValueError("Berger setting drift")
    if berger_payload.get("shape") != [54, 54, 54, 54]:
        raise ValueError("Berger q3 payload shape drift")

    fixture = exact_cubic_fixture()
    source = obstruction["quadratic_truncation_disposition"]
    jacobiator = Fraction(source["witness_jacobiator_weyl_identity"])
    q1_q3 = Fraction(fixture["q1_q3_weyl_noether"])
    required = Fraction(source["required_q3_q1_image_on_witness"])
    if q1_q3 != required or q1_q3 + 3 * jacobiator:
        raise ValueError("cubic source does not cancel the certified Jacobiator")
    if any(Fraction(value) for value in fixture["q1_q3_diff_noether"].values()):
        raise ValueError("unexpected cubic Diff-Noether image")
    if Fraction(fixture["nonlinear_weyl_identity_t3"]):
        raise ValueError("nonlinear Weyl identity drift")

    compatibility = {
        "decision_rule": "A direct import requires the same classical theory, background class, carrier/convention, and a certified cyclic L-infinity map. Matching arity alone is insufficient.",
        "sources": [
            {
                "source_id": berger["result_id"],
                "theory": "Weyl gravity plus a positive rotating conformal clock",
                "background": berger["setting_id"],
                "carrier": "54-row gauge-fixed Berger BV complex",
                "coefficient_field": berger["derivation"]["coefficient_field"],
                "arity": "complete arbitrary-input q3 on its declared carrier",
                "strict_386_direct_import": False,
                "disposition": "NO_CERTIFIED_SAME_THEORY_CARRIER_MAP",
                "reasons": [
                    "the Berger source includes two clock fields and their Euler rows while the strict endpoint is pure Weyl",
                    "the Berger coefficients are specialized to one positive-clock Berger background rather than arbitrary pure-Weyl metric jets",
                    "the 54-row h_hat/R/Theta basis is not the 30-row pure-Weyl endpoint or its 386-row stabilization",
                    "no content-addressed cyclic L-infinity morphism between these theories and carriers is certified",
                    "the Berger certificate itself leaves the background-independent antifield Koszul-Tate export false",
                ],
                "nonexistence_claimed": False,
            },
            {
                "source_id": natural["result_id"],
                "theory": "strict pure Weyl",
                "background": "arbitrary nondegenerate four-dimensional metric jets",
                "carrier": "portable metric Euler row",
                "coefficient_field": "Q",
                "arity": "bilinear Hessian q2 only",
                "strict_386_direct_import": False,
                "disposition": "SAME_THEORY_PORTABLE_Q2_DOES_NOT_EXPORT_Q3",
                "reasons": ["the portable AST stops at the second Frechet derivative"],
                "nonexistence_claimed": False,
            },
            {
                "source_id": "STRICT_PURE_WEYL_CUBIC_BACH_RECEIVER_V1",
                "theory": "strict pure Weyl",
                "background": "flat metric fixture",
                "carrier": "ten metric-equation rows of the strict 30-row endpoint",
                "coefficient_field": "Q",
                "arity": "diagonal metric-sector q3 on one exact q1-closed input",
                "strict_386_direct_import": False,
                "disposition": "RECEIVER_DERIVED_WITNESS_CANCELLATION_CERTIFIED",
                "reasons": ["the computation realizes the required source cancellation but is not a full arbitrary-input or full-BV classical export"],
                "nonexistence_claimed": False,
            },
        ],
        "sha256": "",
    }
    compatibility["sha256"] = recorded_digest(compatibility)

    cancellation = {
        "q2_jacobiator_weyl_noether": str(jacobiator),
        "required_q1_q3": str(required),
        "computed_q1_q3": str(q1_q3),
        "arity_three_defect": str(q1_q3 + 3 * jacobiator),
        "q2_only_lambda2_source_defect": source["witness_source_closure_defect"],
        "full_lambda2_source_q1_defect_on_witness": str(Fraction(1, 2) * jacobiator + Fraction(1, 6) * q1_q3),
        "witness_source_closure": True,
        "general_full_source_closure": False,
        "sha256": "",
    }
    cancellation["sha256"] = recorded_digest(cancellation)

    export_contract = {
        "contract_id": "STRICT_PURE_WEYL_AUTHORITATIVE_Q3_EXPORT_V2",
        "now_established": [
            "the exact pure-Weyl metric-sector q3 normalization on the pinned diagonal witness",
            "the required -75760/9 q1 image and exact cancellation of the q2 Jacobiator",
            "the incompatibility of the existing Berger-plus-clock q3 as a direct strict pure-Weyl import under the currently certified maps",
        ],
        "still_required": [
            "an authoritative arbitrary-three-input pure-Weyl q3 on the complete classical minimal BV carrier",
            "all ghost, antifield, and Noether partner rows in the same suspended factorial convention as q1 and q2",
            "an exact coefficientwise arity-three identity on arbitrary inputs",
            "a content-addressed cyclic stabilization or L-infinity morphism from the authoritative minimal carrier to the 386-row graph carrier",
            "support-locality and derivative-order bounds followed by q3/Green support-domain checks",
        ],
        "minimum_regression": "the full export must reproduce q1(q3(x,x,x))_omega_star=-75760/9 on FLAT_PURE_DIFF_GAUGE_SEED_1",
        "authoritative_export_present": False,
        "sha256": "",
    }
    export_contract["sha256"] = recorded_digest(export_contract)

    foundations = {
        "classification": "FINITE_EXACT_RATIONAL_CUBIC_METRIC_JET_WITNESS",
        "finite_layer": "The cubic coefficient, ten metric rows, 41 exact rational terms, four Diff-Noether zeros, Weyl-Noether value, and cancellation are finite rational computations.",
        "choice_operation_added": False,
        "completion_or_infinite_sum_used": False,
        "analytic_green_layer_used": False,
        "weakest_complete_foundational_base": "PRA_UPPER_BOUND_FOR_FIXED_FIXTURE; UNCALIBRATED_FOR_ARBITRARY_INPUT_NATURAL_Q3",
        "sha256": "",
    }
    foundations["sha256"] = recorded_digest(foundations)

    flags = {
        "STRICT_PURE_WEYL_METRIC_Q3_DIAGONAL_WITNESS_DERIVED": True,
        "STRICT_PURE_WEYL_Q3_WITNESS_CANCELLATION_CERTIFIED": True,
        "STRICT_386_WITNESS_FULL_SOURCE_CLOSURE_CERTIFIED": True,
        "BERGER_Q3_DIRECT_STRICT_IMPORT_COMPATIBLE": False,
        "STRICT_386_AUTHORITATIVE_Q3_IMPORTED": False,
        "STRICT_386_ARBITRARY_INPUT_Q3_CERTIFIED": False,
        "STRICT_386_FULL_BV_ARITY_THREE_IDENTITY_CERTIFIED": False,
        "STRICT_386_GENERAL_FULL_WEYL_LAMBDA2_SOURCE_CLOSURE_CERTIFIED": False,
        "CLASSICAL_IMPORT_GATE_PASSED": False,
        "HADAMARD_STATE_CONSTRUCTED": False,
        "QME_RESTORED": False,
        "LORENTZIAN_QUANTUM_THEORY": False,
    }

    value: dict[str, Any] = {
        "$schema": "../schema/strict-386-pure-weyl-q3-witness-v1.schema.json",
        "schema": "strict-386-pure-weyl-q3-witness-v1",
        "schema_path": "quantum-weyl/classical_import/schema/strict-386-pure-weyl-q3-witness-v1.schema.json",
        "result_id": "STRICT_386_PURE_WEYL_Q3_WITNESS_V1",
        "result_kind": "EXACT_RECEIVER_DERIVED_PURE_WEYL_METRIC_Q3_WITNESS_AND_SOURCE_COMPATIBILITY_INVENTORY",
        "result_state": "METRIC_Q3_WITNESS_CANCELLATION_CERTIFIED_AUTHORITATIVE_FULL_BV_Q3_OPEN",
        "lifecycle": "CLASSIFIED",
        "created": "2026-08-15",
        "repository_base_commit": "f6e40e94b18a9efda1dc0aac60efaed0ac4b0789",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "question": "Can the required pure-Weyl q3 cancellation be constructed directly, and can any existing complete q3 be imported into the strict carrier?",
        "answer": "Yes for the pinned pure-Weyl metric witness, but not yet as a full authoritative import. Exact cubic differentiation of the action-normalized Bach Euler density gives 41 rational terms across all ten metric-equation rows and q1 q3=-75760/9, exactly cancelling three times the certified 75760/27 q2 Jacobiator. The full lambda-squared source is therefore q1-closed on this witness. The repository's complete Berger q3 cannot be directly imported: it belongs to Weyl gravity plus a positive clock at a fixed Berger background on a different 54-row carrier, and no same-theory cyclic carrier map is certified. Arbitrary-input full-BV q3 and its 386-row stabilization remain open.",
        "scope": {
            "theory": "strict pure-Weyl metric sector",
            "carrier": "strict thirty-row endpoint metric equation rows, interpreted inside the 386-row split carrier",
            "background": "flat four-dimensional Bach-flat metric",
            "input": "one exact q1-closed pure-diffeomorphism metric jet",
            "claim_type": "receiver-derived exact witness, not authoritative classical import",
        },
        "exact_cubic_fixture": fixture,
        "arity_three_cancellation": cancellation,
        "q3_source_compatibility": compatibility,
        "authoritative_q3_export_contract": export_contract,
        "foundational_strength": foundations,
        "claim_flags": flags,
        "does_not_establish": [
            "an authoritative arbitrary-input pure-Weyl q3 export",
            "the ghost, antifield, nonminimal, auxiliary, residual, or full 386-row q3 components",
            "the general arity-three L-infinity identity beyond the pinned diagonal metric witness",
            "general lambda-squared or all-order nonlinear source closure",
            "nonexistence of a future Berger-to-pure-Weyl relation; only the absence of a currently certified same-theory map is asserted",
            "q3 compatibility with retarded or advanced Green actions",
            "a passed classical import gate, analytic Moller map, Hadamard state, renormalized products, QME restoration, residual transfer, or Lorentzian quantum theory",
        ],
        "next_gate": "Export arbitrary-input action-derived pure-Weyl q3 on the authoritative minimal BV carrier, including every ghost/antifield partner; replay the full arity-three identity and then stabilize it through a content-addressed cyclic map to the 386-row graph carrier. The export must reproduce the pinned -75760/9 witness.",
        "canonical_hashes": {},
        "provenance": {
            "inputs": [
                {"path": str(path.relative_to(ROOT)), "result_or_artifact_id": expected, "sha256": sha(path), "role": role}
                for path, expected, role in INPUTS
            ]
            + [{"path": str(BERGER_PAYLOAD.relative_to(ROOT)), "result_or_artifact_id": berger_payload["schema"], "sha256": sha(BERGER_PAYLOAD), "role": "Berger q3 payload shape and coefficient-field comparison"}],
            "implementation": {"path": str(ENGINE.relative_to(ROOT)), "sha256": sha(ENGINE), "role": "exact Q[t]/(t^4) cubic Bach receiver"},
        },
        "independent_checker": {
            "path": "quantum-weyl/classical_import/check_strict_386_pure_weyl_q3_witness.py",
            "checks": [
                "dependency identities and hashes",
                "independent q2 Jacobiator regeneration",
                "exact cubic Bach receiver regeneration",
                "four Diff-Noether zeros and nonlinear Weyl trace identity",
                "-75760/9 arity-three and lambda-squared source cancellation",
                "Berger theory/background/carrier incompatibility boundary",
                "authoritative/full-BV/Hadamard/QME firewalls",
            ],
        },
        "human_report": "quantum-weyl/classical_import/REPORT_STRICT_386_PURE_WEYL_Q3_WITNESS_V1.md",
    }
    value["canonical_hashes"] = {
        "exact_cubic_fixture_sha256": recorded_digest(fixture),
        "arity_three_cancellation_sha256": recorded_digest(cancellation),
        "q3_source_compatibility_sha256": recorded_digest(compatibility),
        "authoritative_q3_export_contract_sha256": recorded_digest(export_contract),
        "foundational_strength_sha256": recorded_digest(foundations),
    }
    return value


def render(value: Mapping[str, Any]) -> str:
    fixture = value["exact_cubic_fixture"]
    cancellation = value["arity_three_cancellation"]
    sources = value["q3_source_compatibility"]["sources"]
    rows = "\n".join(
        f"| `{item['source_id']}` | {item['theory']} | {item['carrier']} | `{item['disposition']}` |"
        for item in sources
    )
    return f"""# Strict pure-Weyl q3 witness and source inventory v1

## Outcome

{value['answer']}

## Exact cancellation

```text
q2(x,q2(x,x))_omega_star = {cancellation['q2_jacobiator_weyl_noether']}
q1(q3(x,x,x))_omega_star = {cancellation['computed_q1_q3']}
q1 q3 + 3 q2 q2             = {cancellation['arity_three_defect']}
q1 S2                        = {cancellation['full_lambda2_source_q1_defect_on_witness']}
```

The cubic metric source has {fixture['metric_output_term_count']} exact rational
terms across {fixture['nonzero_metric_output_rows']} output rows.  All four
linear Diff-Noether images and the coefficient of the full nonlinear Weyl
trace identity vanish exactly.

## Why the existing complete q3 is not the strict import

| Source | Theory | Carrier | Disposition |
|---|---|---|---|
{rows}

The Berger result remains a valid complete q3 theorem on its own declared
Weyl-plus-clock carrier.  The incompatibility decision says that no currently
certified same-theory cyclic map authorizes its use as the pure-Weyl strict
q3.  It is not a nonexistence theorem for every possible future relation.

## Reproduction

```text
python3 quantum-weyl/classical_import/build_strict_386_pure_weyl_q3_witness.py --check
python3 quantum-weyl/classical_import/check_strict_386_pure_weyl_q3_witness.py
python3 quantum-weyl/classical_import/verify_strict_386_pure_weyl_q3_witness.py
python3 -m unittest quantum-weyl/classical_import/tests/test_strict_386_pure_weyl_q3_witness.py -v
```

## Boundaries

""" + "\n".join(f"- This does not establish {item}." for item in value["does_not_establish"]) + "\n"


def generated() -> tuple[bytes, bytes]:
    value = build()
    return (
        (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode(),
        render(value).encode(),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs = tuple(zip((RESULT, REPORT), generated()))
    stale = [str(path.relative_to(ROOT)) for path, content in outputs if not path.is_file() or path.read_bytes() != content]
    if args.check:
        print("STRICT_386_PURE_WEYL_Q3_WITNESS_V1: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    for path, content in outputs:
        path.write_bytes(content)
    print("STRICT_386_PURE_WEYL_Q3_WITNESS_V1: wrote certificate and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
