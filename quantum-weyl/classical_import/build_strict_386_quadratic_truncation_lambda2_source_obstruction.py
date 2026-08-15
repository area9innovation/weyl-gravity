#!/usr/bin/env python3
"""Build the exact lambda-squared source obstruction for the q2-only truncation."""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

import cylinder_polarized_bach_evaluator as point
from local_q1_q2_receiver import apply_primary_q2, apply_q1, field_fixture


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_386_QUADRATIC_TRUNCATION_LAMBDA2_SOURCE_OBSTRUCTION_V1.json"
REPORT = HERE / "REPORT_STRICT_386_QUADRATIC_TRUNCATION_LAMBDA2_SOURCE_OBSTRUCTION_V1.md"

Q2 = HERE / "certificates/STRICT_SIX_ROW_SUSPENDED_Q2_AST_V1.json"
Q1Q2 = HERE / "certificates/STRICT_LOCAL_Q1_Q2_IDENTITY_V1.json"
STABILIZED = HERE / "certificates/STRICT_386_STABILIZED_Q2_LIFT_PREFLIGHT_V1.json"
TYPED = HERE / "certificates/STRICT_386_FIELD_EQUATION_GREEN_QUOTIENT_INVERSE_V1.json"
FORMAL = HERE / "certificates/STRICT_386_POLARIZED_FORMAL_MOLLER_COEFFICIENTS_V1.json"
INPUTS = (
    (Q2, "STRICT_SIX_ROW_SUSPENDED_Q2_AST_V1", "complete minimal q2 ledger and factorial convention"),
    (Q1Q2, "STRICT_LOCAL_Q1_Q2_IDENTITY_V1", "exact arity-two identity"),
    (STABILIZED, "STRICT_386_STABILIZED_Q2_LIFT_PREFLIGHT_V1", "exact split stabilization and graph conjugation"),
    (TYPED, "STRICT_386_FIELD_EQUATION_GREEN_QUOTIENT_INVERSE_V1", "typed constrained/quotient Green inverse"),
    (FORMAL, "STRICT_386_POLARIZED_FORMAL_MOLLER_COEFFICIENTS_V1", "lambda-squared q2-only response diagnostic"),
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def recorded_digest(value: Mapping[str, Any]) -> str:
    return digest({key: item for key, item in value.items() if key != "sha256"})


def jet_payload(value: point.Jet) -> list[dict[str, Any]]:
    return [
        {
            "parameter_degrees": [a, b],
            "coordinate_multiindex": list(alpha),
            "coefficient": str(coefficient),
        }
        for a, b, alpha, coefficient in value.terms
    ]


def tensor_payload(value: Mapping[Any, point.Jet]) -> list[dict[str, Any]]:
    return [
        {"component": list(component) if isinstance(component, tuple) else component, "terms": jet_payload(value[component])}
        for component in sorted(value)
        if value[component].terms
    ]


def exact_fixture(seed: int = 1) -> dict[str, Any]:
    background = point.flat_background(7)
    gauge_parameter = field_fixture("c", seed, 7)
    field = apply_q1("q1_h_c", gauge_parameter, background, 6)
    linear_equation = apply_q1("q1_hstar_h", field, background, 1)
    quadratic_equation = apply_primary_q2("q2_hstar_hh", field, field, 1, background=background)
    jacobiator_diff = apply_primary_q2("q2_cstar_hhstar", field, quadratic_equation, 0, background=background)
    jacobiator_weyl = apply_primary_q2("q2_omegastar_hhstar", field, quadratic_equation, 0, background=background)
    if any(value.terms for value in linear_equation.values()):
        raise ValueError("fixture is not q1 closed")
    if any(value.terms for value in jacobiator_diff.values()):
        raise ValueError("unexpected Diff-identity Jacobiator component")
    if jacobiator_weyl.constant_term != Fraction(75760, 27) or len(jacobiator_weyl.terms) != 1:
        raise ValueError("Weyl-identity Jacobiator witness drift")
    payload = {
        "fixture_id": "FLAT_PURE_DIFF_GAUGE_SEED_1",
        "background": "four-dimensional flat metric diag(-1,1,1,1)",
        "generator": "c_seed_1 exact rational coordinate seven-jet",
        "field_definition": "x=q1(c_seed_1)",
        "field_status": "q1(x)=0 exactly",
        "field_terms": tensor_payload(field),
        "linear_equation_terms": tensor_payload(linear_equation),
        "quadratic_equation_terms": tensor_payload(quadratic_equation),
        "jacobiator_definition": "J2(x)=q2(x,q2(x,x))",
        "jacobiator_diff_identity_terms": tensor_payload(jacobiator_diff),
        "jacobiator_weyl_identity_terms": jet_payload(jacobiator_weyl),
        "jacobiator_weyl_identity_value": "75760/27",
        "nonzero": True,
    }
    payload["sha256"] = digest(payload)
    return payload


def build() -> dict[str, Any]:
    values = {path: json.loads(path.read_text()) for path, _, _ in INPUTS}
    for path, expected, _ in INPUTS:
        if values[path].get("result_id") != expected:
            raise ValueError(f"dependency identity drift: {path}")
    q2, q1q2, stabilized, typed, formal = (values[path] for path, _, _ in INPUTS)
    if q2.get("convention") != "suspended-graded-symmetric-factorial-v1":
        raise ValueError("q2 convention drift")
    if not q1q2["claim_flags"]["Q1_Q2_ARITY_TWO_NILPOTENCY_REPLAYED"]:
        raise ValueError("arity-two identity unavailable")
    if not stabilized["claim_flags"]["STRICT_386_STABILIZED_Q2_CANDIDATE_CONSTRUCTED"]:
        raise ValueError("stabilized candidate unavailable")
    if not typed["claim_flags"]["STRICT_386_FIELD_EQUATION_CONSTRAINED_RIGHT_INVERSE_CERTIFIED"]:
        raise ValueError("typed field inverse unavailable")

    fixture = exact_fixture()
    literature = {
        "id": "hohm-zwiebach-2017",
        "citation": "Olaf Hohm and Barton Zwiebach, L-infinity Algebras and Field Theory, Fortschritte der Physik 65 (2017), 1700014.",
        "stable_url": "https://arxiv.org/abs/1701.08824",
        "artifact": {
            "status": "CONTENT_PINNED",
            "locator": "https://arxiv.org/pdf/1701.08824",
            "sha256": "91006d01123242f2e5cb8c673cde0263caf2e3de6110f44e928167203240d893",
        },
        "imported_statement": "Equations (2.8) and (2.11) give the suspended odd-product arity-three identity and factorial Maurer-Cartan equation: for a degree-zero q1-closed input, q1 q3(x,x,x)+3 q2(x,q2(x,x))=0.",
        "application_boundary": "The source fixes the general L-infinity convention. The Weyl-specific fixture, exact rational Jacobiator and export requirement are independently derived from repository operators.",
    }
    literature["sha256"] = digest(literature)

    derivation = {
        "free_input": "q1(x)=0",
        "first_response_equation": "q1(r1)+(1/2)q2(x,x)=0",
        "lambda_squared_source_full": "S2=q2(x,r1)+(1/6)q3(x,x,x)",
        "arity_two_consequence": "q1(q2(x,r1))=(1/2)q2(x,q2(x,x))=(1/2)J2(x)",
        "arity_three_identity": "q1(q3(x,x,x))+3 J2(x)=0",
        "full_source_closure": "q1(S2)=(1/2)J2(x)+(1/6)(-3 J2(x))=0",
        "quadratic_truncation_source": "S2[q3=0]=q2(x,r1)",
        "quadratic_truncation_defect": "q1(S2[q3=0])=(1/2)J2(x)",
        "typed_noether_form": "N S2[q3=0]=(1/2)J2(x)",
        "structural_derivation_defects": 0,
    }
    derivation["sha256"] = digest(derivation)

    disposition = {
        "quadratic_only_lambda_squared_source_closed": False,
        "witness_jacobiator_weyl_identity": "75760/27",
        "witness_source_closure_defect": "37880/27",
        "required_q3_q1_image_on_witness": "-75760/9",
        "required_q3_relation": "q1(q3(x,x,x))=-3 q2(x,q2(x,x))",
        "q3_required_for_this_candidate": True,
        "obstruction_scope": "the q2-only truncation of the receiver-constructed stabilized candidate",
        "not_an_obstruction_to_full_weyl_theory": True,
        "reason": "An authoritative q3 satisfying the arity-three identity cancels the exact defect.",
    }
    disposition["sha256"] = digest(disposition)

    export_contract = {
        "contract_id": "STRICT_PURE_WEYL_AUTHORITATIVE_Q3_SOURCE_CLOSURE_EXPORT_V1",
        "producer_owner": "classical BV-BFV programme",
        "required_objects": [
            "the authoritative q2 and q3 Taylor components on the same declared classical carrier",
            "the suspended factorial and Koszul sign convention",
            "a content-addressed cyclic L-infinity morphism if the classical carrier differs from the 386-row receiver",
            "an exact arity-three replay q1 q3+q3 q1+q2 q2=0",
            "the image of the flat pure-Diff witness or an exact carrier crosswalk for it",
            "support-locality and derivative-order bounds for q3",
        ],
        "acceptance_checks": [
            "all source hashes independently resolve",
            "q1/q2/q3 carrier, degree and convention types agree",
            "the witness q3 image cancels -3 times the certified nonzero Jacobiator",
            "N S2=0 replays exactly before any Green action is applied",
            "no receiver-constructed q3 is relabelled as an authoritative import",
        ],
        "minimum_witness_target": "q1(q3(x,x,x))_omega_star=-75760/9 on FLAT_PURE_DIFF_GAUGE_SEED_1",
        "authoritative_export_present": False,
        "gate_disposition": "M2_SOURCE_Q3_ARITY_THREE_EXPORT_MISSING",
    }
    export_contract["sha256"] = digest(export_contract)

    foundations = {
        "classification": "FINITE_EXACT_RATIONAL_JET_OBSTRUCTION_OVER_A_CONTENT_PINNED_L_INFINITY_IDENTITY",
        "finite_layer": "The fixture, q1-closure, q2 compositions, rational nonzero witness and source-defect arithmetic are finite primitive-recursive calculations.",
        "analytic_green_layer_used_for_obstruction": False,
        "choice_operation_added": False,
        "completion_or_infinite_sum_used": False,
        "weakest_complete_foundational_base": "PRA_UPPER_BOUND_FOR_FIXED_FIXTURE; UNCALIBRATED_FOR_GENERAL_SMOOTH_OPERATOR_IDENTITY",
    }
    foundations["sha256"] = digest(foundations)

    authority = {
        "candidate_q2_only": True,
        "q1_closed_witness": True,
        "quadratic_truncation_obstruction_certified": True,
        "authoritative_q2_imported": False,
        "authoritative_q3_imported": False,
        "full_weyl_lambda_squared_source_closure_decided": False,
        "analytic_green_action_needed_for_obstruction": False,
        "classical_import_gate_a_status": "FAIL_CLOSED",
    }
    authority["sha256"] = digest(authority)

    flags = {
        "STRICT_386_Q2_ONLY_LAMBDA2_SOURCE_OBSTRUCTED": True,
        "STRICT_386_Q2_JACOBIATOR_NONZERO_WITNESS_CERTIFIED": True,
        "STRICT_386_AUTHORITATIVE_Q3_REQUIRED": True,
        "STRICT_386_AUTHORITATIVE_Q3_IMPORTED": False,
        "STRICT_386_FULL_WEYL_LAMBDA2_SOURCE_CLOSURE_CERTIFIED": False,
        "STRICT_386_AUTHORITATIVE_FORMAL_MOLLER_MAP_CERTIFIED": False,
        "CLASSICAL_IMPORT_GATE_PASSED": False,
        "HADAMARD_STATE_CONSTRUCTED": False,
        "QME_RESTORED": False,
        "LORENTZIAN_QUANTUM_THEORY": False,
    }

    value = {
        "$schema": "../schema/strict-386-quadratic-truncation-lambda2-source-obstruction-v1.schema.json",
        "schema": "strict-386-quadratic-truncation-lambda2-source-obstruction-v1",
        "schema_path": "quantum-weyl/classical_import/schema/strict-386-quadratic-truncation-lambda2-source-obstruction-v1.schema.json",
        "result_id": "STRICT_386_QUADRATIC_TRUNCATION_LAMBDA2_SOURCE_OBSTRUCTION_V1",
        "result_kind": "EXACT_Q2_ONLY_LAMBDA2_SOURCE_COCYCLE_OBSTRUCTION_AND_AUTHORITATIVE_Q3_EXPORT_CONTRACT",
        "result_state": "Q2_ONLY_SOURCE_OBSTRUCTED_Q3_CANCELLATION_NECESSARY_AUTHORITATIVE_Q3_OPEN",
        "lifecycle": "CLASSIFIED",
        "created": "2026-08-15",
        "repository_base_commit": "aa45be6ffca005e79c38c43dfafefe3c8c76a366",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "question": "Does the q2-only candidate source close at lambda squared on q1-closed fields, and if not what exact q3 datum is required?",
        "answer": "No. An exact q1-closed pure-diffeomorphism metric fixture has nonzero q2 Jacobiator 75760/27 in the Weyl Noether row. Therefore the q2-only lambda-squared source has exact closure defect 37880/27. This proves that the quadratic truncation cannot be a Weyl-BV Maurer-Cartan or Moller map by itself. It is not a no-go for full Weyl gravity: the suspended arity-three identity requires q1 q3=-3 q2 q2, which would cancel the defect. The next import is now precise: an authoritative classical q3 plus an exact arity-three carrier bridge, with witness target -75760/9.",
        "scope": {
            "theory": "strict pure-Weyl stabilized q2 receiver candidate",
            "carrier": "386-row graph candidate, evaluated through its exact split-conjugate minimal endpoint",
            "background": "flat four-dimensional Bach-flat metric",
            "input": "one exact q1-closed pure-Diff metric jet",
            "order": "lambda squared",
        },
        "literature_context": literature,
        "exact_q1_closed_fixture": fixture,
        "source_closure_derivation": derivation,
        "quadratic_truncation_disposition": disposition,
        "authoritative_q3_export_contract": export_contract,
        "foundational_strength": foundations,
        "authority_boundary": authority,
        "claim_flags": flags,
        "does_not_establish": [
            "that the receiver-constructed q2 is the authoritative nonlinear Weyl BV operation",
            "the authoritative q3 or any higher Taylor component",
            "failure of lambda-squared source closure in the full Weyl theory after q3 is included",
            "a no-go theorem against Weyl gravity, its BV complex or its physical spectrum",
            "an analytic Moller map, Hadamard state, renormalized products, QME restoration, residual transfer or Lorentzian quantum theory",
        ],
        "next_gate": "Export authoritative q2 and q3 from the classical BV-BFV programme on a content-addressed carrier, replay q1 q3+q3 q1+q2 q2=0, and require q1(q3(x,x,x))_omega_star=-75760/9 on the pinned witness before re-testing N S2=0.",
        "canonical_hashes": {},
        "provenance": {
            "inputs": [
                {"path": str(path.relative_to(ROOT)), "result_or_artifact_id": expected, "sha256": sha(path), "role": role}
                for path, expected, role in INPUTS
            ],
            "implementation": [
                {"path": "quantum-weyl/classical_import/cylinder_polarized_bach_evaluator.py", "sha256": sha(HERE / "cylinder_polarized_bach_evaluator.py"), "role": "exact natural Bach jet evaluator"},
                {"path": "quantum-weyl/classical_import/local_q1_q2_receiver.py", "sha256": sha(HERE / "local_q1_q2_receiver.py"), "role": "typed exact q1/q2 composition receiver"},
            ],
        },
        "independent_checker": {
            "path": "quantum-weyl/classical_import/check_strict_386_quadratic_truncation_lambda2_source_obstruction.py",
            "checks": [
                "dependency identities and content hashes",
                "independent exact regeneration of the q1-closed fixture",
                "nonzero q2 Jacobiator and rational source defect",
                "factorial arity-three cancellation arithmetic",
                "split-to-graph conjugation and authority boundary",
                "canonical section hashes and lifecycle firewalls",
            ],
        },
        "human_report": "quantum-weyl/classical_import/REPORT_STRICT_386_QUADRATIC_TRUNCATION_LAMBDA2_SOURCE_OBSTRUCTION_V1.md",
    }
    value["canonical_hashes"] = {
        "literature_context_sha256": recorded_digest(literature),
        "fixture_sha256": recorded_digest(fixture),
        "source_closure_derivation_sha256": recorded_digest(derivation),
        "quadratic_truncation_disposition_sha256": recorded_digest(disposition),
        "authoritative_q3_export_contract_sha256": recorded_digest(export_contract),
        "foundational_strength_sha256": recorded_digest(foundations),
        "authority_boundary_sha256": recorded_digest(authority),
    }
    return value


def render(value: Mapping[str, Any]) -> str:
    d = value["quadratic_truncation_disposition"]
    return "\n".join([
        "# Strict 386-row q2-only lambda-squared source obstruction", "", "## Outcome", "",
        value["answer"], "", "## Exact source calculation", "", "```text",
        value["source_closure_derivation"]["first_response_equation"],
        value["source_closure_derivation"]["lambda_squared_source_full"],
        value["source_closure_derivation"]["typed_noether_form"], "```", "",
        f"- Exact Jacobiator witness: `{d['witness_jacobiator_weyl_identity']}`.",
        f"- Exact q2-only source defect: `{d['witness_source_closure_defect']}`.",
        f"- Required `q1 q3` witness value: `{d['required_q3_q1_image_on_witness']}`.", "",
        "## Interpretation", "",
        "The quadratic receiver candidate is now exactly ruled out as a standalone Maurer--Cartan interaction. This is positive information about the import boundary: full Weyl gravity must supply the cubic Taylor component required by its arity-three identity.", "",
        "## Reproduction", "", "```text",
        "python3 quantum-weyl/classical_import/build_strict_386_quadratic_truncation_lambda2_source_obstruction.py --check",
        "python3 quantum-weyl/classical_import/check_strict_386_quadratic_truncation_lambda2_source_obstruction.py",
        "python3 quantum-weyl/classical_import/verify_strict_386_quadratic_truncation_lambda2_source_obstruction.py",
        "python3 -m unittest quantum-weyl/classical_import/tests/test_strict_386_quadratic_truncation_lambda2_source_obstruction.py -v",
        "```", "", "## Boundaries", "",
        *[f"- This does not establish {item}." for item in value["does_not_establish"]], "",
    ])


def generated() -> tuple[bytes, bytes]:
    value = build()
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode(), render(value).encode()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result, report = generated()
    stale = [str(path.relative_to(ROOT)) for path, content in ((RESULT, result), (REPORT, report)) if not path.is_file() or path.read_bytes() != content]
    if args.check:
        print("STRICT_386_QUADRATIC_TRUNCATION_LAMBDA2_SOURCE_OBSTRUCTION_V1: " + ("CURRENT" if not stale else "STALE: " + ", ".join(stale)))
        return bool(stale)
    RESULT.write_bytes(result)
    REPORT.write_bytes(report)
    print("STRICT_386_QUADRATIC_TRUNCATION_LAMBDA2_SOURCE_OBSTRUCTION_V1: wrote certificate and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
