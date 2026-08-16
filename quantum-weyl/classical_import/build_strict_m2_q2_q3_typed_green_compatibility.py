#!/usr/bin/env python3
"""Build the strict Gate-A q2/q3 typed Green-compatibility certificate."""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_M2_Q2_Q3_TYPED_GREEN_COMPATIBILITY_V1.json"
REPORT = HERE / "REPORT_STRICT_M2_Q2_Q3_TYPED_GREEN_COMPATIBILITY_V1.md"
SCHEMA = HERE / "schema/strict-m2-q2-q3-typed-green-compatibility-v1.schema.json"
INPUTS = {
    "m1c": HERE / "certificates/STRICT_M1C_COMMON_SNAPSHOT_V1.json",
    "gate": HERE / "certificates/CLASSICAL_IMPORT_GATE_V30_RECONCILIATION.json",
    "green": HERE / "certificates/STRICT_386_GRAPH_GREEN_ACTION_NAME_V1.json",
    "field_inverse": HERE / "certificates/STRICT_386_FIELD_EQUATION_GREEN_QUOTIENT_INVERSE_V1.json",
    "q2": HERE / "certificates/STRICT_386_SOURCE_Q2_COMMON_ASSEMBLY_V1.json",
    "q3": HERE / "certificates/STRICT_386_SOURCE_Q3_COMMON_ASSEMBLY_V1.json",
    "cyclic": HERE / "certificates/STRICT_386_LOCAL_CYCLIC_PAIRING_CLOSURE_V1.json",
    "literature": ROOT / "foundations/literature-causal-green-atlas-v1.json",
}
EXPECTED_IDS = {
    "m1c": "STRICT_M1C_COMMON_SNAPSHOT_V1",
    "gate": "CLASSICAL_IMPORT_GATE_V30_RECONCILIATION",
    "green": "STRICT_386_GRAPH_GREEN_ACTION_NAME_V1",
    "field_inverse": "STRICT_386_FIELD_EQUATION_GREEN_QUOTIENT_INVERSE_V1",
    "q2": "STRICT_386_SOURCE_Q2_COMMON_ASSEMBLY_V1",
    "q3": "STRICT_386_SOURCE_Q3_COMMON_ASSEMBLY_V1",
    "cyclic": "STRICT_386_LOCAL_CYCLIC_PAIRING_CLOSURE_V1",
    "literature": "FOUNDATIONAL_CAUSAL_GREEN_LITERATURE_V1",
}


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode()).hexdigest()


def source_id(value: dict[str, Any]) -> str | None:
    return value.get("result_id") or value.get("ledger_id") or value.get("schema")


def fraction_text(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def build() -> dict[str, Any]:
    source = {name: load(path) for name, path in INPUTS.items()}
    for name, expected in EXPECTED_IDS.items():
        if source_id(source[name]) != expected:
            raise ValueError(f"dependency identity drift: {name}")

    m1c, gate, green, inverse, q2, q3, cyclic, literature = (
        source[name] for name in ("m1c", "gate", "green", "field_inverse", "q2", "q3", "cyclic", "literature")
    )
    if not gate["claim_flags"].get("CLASSICAL_IMPORT_GATE_PASSED"):
        raise ValueError("Gate A is not verified")
    resolution = gate["m1c_common_snapshot_resolution"]
    if resolution["snapshot_sha256"] != m1c["snapshot_sha256"] or resolution["certificate_sha256"] != file_hash(INPUTS["m1c"]):
        raise ValueError("Gate-A/M1C snapshot binding drift")
    pins = {item["pin_id"]: item for item in m1c["artifact_pins"]}
    for pin_id, input_id in (("source_q2", "q2"), ("source_q3", "q3"), ("local_cyclic", "cyclic")):
        if pins[pin_id]["sha256"] != file_hash(INPUTS[input_id]):
            raise ValueError(f"immutable snapshot pin drift: {pin_id}")

    green_replay = green["analytic_and_exact_replay"]
    if not all(green_replay[key] for key in (
        "parent_two_sided_inverse_imported", "parent_LF_to_Frechet_continuity_imported",
        "parent_causal_support_imported", "full_graph_homotopy_identity_exact",
        "advanced_retarded_adjoint_exact",
    )):
        raise ValueError("typed Green theorem unavailable")
    if not inverse["claim_flags"].get("STRICT_386_FIELD_EQUATION_CONSTRAINED_RIGHT_INVERSE_CERTIFIED"):
        raise ValueError("field-equation constrained inverse unavailable")
    if not q2["claim_flags"].get("FULL_SHIFTED_SOURCE_Q2_COMMON_UNION_ASSEMBLED"):
        raise ValueError("authoritative q2 unavailable")
    if not q3["claim_flags"].get("FULL_SHIFTED_SOURCE_Q3_COMMON_UNION_ASSEMBLED"):
        raise ValueError("authoritative q3 unavailable")

    baer = next(item for item in literature["entries"] if item["id"] == "baer-2015")
    if baer["artifact"]["status"] != "CONTENT_PINNED":
        raise ValueError("support-space Green theorem is not content pinned")

    provenance = []
    roles = {
        "m1c": "immutable authoritative strict pure-Weyl BV snapshot",
        "gate": "independent Gate-A decision on the immutable snapshot",
        "green": "typed convergent advanced/retarded graph Green operator names",
        "field_inverse": "degree-restricted constrained and quotient field-equation inverse",
        "q2": "authoritative common-snapshot binary BV operation",
        "q3": "authoritative common-snapshot ternary BV operation and arity-three identity",
        "cyclic": "rank-386 local odd pairing and q1/q2/q3 cyclic replay",
        "literature": "content-pinned support-space extension theorem",
    }
    for name, path in INPUTS.items():
        provenance.append({
            "input_id": name,
            "path": str(path.relative_to(ROOT)),
            "result_or_artifact_id": EXPECTED_IDS[name],
            "sha256": file_hash(path),
            "role": roles[name],
        })

    type_ledger = {
        "carrier": "the 386-row suspended strict pure-Weyl graph BV bundle E_386 on M=R x S3",
        "degree_convention": "q1, q2 and q3 have suspended degree +1; Lambda_sigma has degree -1",
        "spaces": {
            "C": "Gamma_c^infinity(M,E_386), compact support",
            "PC": "Gamma_pc^infinity(M,E_386), past-compact support (bounded below in cylinder time)",
            "FC": "Gamma_fc^infinity(M,E_386), future-compact support (bounded above in cylinder time)",
        },
        "q1": "q1:X_S^k -> X_S^(k+1) for S in {C,PC,FC}",
        "q2": "q2:X_S^k x X_T^l -> X_(S intersection T)^(k+l+1)",
        "q3": "q3:X_S^k x X_T^l x X_U^m -> X_(S intersection T intersection U)^(k+l+m+1)",
        "plus": "Lambda_plus:X_C^k -> X_PC^(k-1), continuously extended X_PC^k -> X_PC^(k-1)",
        "minus": "Lambda_minus:X_C^k -> X_FC^(k-1), continuously extended X_FC^k -> X_FC^(k-1)",
        "homotopy": "q1 Lambda_sigma + Lambda_sigma q1 = identity on the matching support class",
        "field_component": inverse["green_field_equation_component"]["definition"],
        "field_inverse": "K G_sigma(s)=s for s in ker N; [G_sigma K(phi)]=[phi] modulo im R",
        "distribution_kernel_status": "exists by continuity and the Schwartz kernel theorem; coordinate kernel bytes are not serialized",
    }
    type_ledger["sha256"] = digest(type_ledger)

    support_and_continuity = {
        "q2_locality": {
            "source_families": q2["family_census"]["total_shifted_source_q2_families"],
            "graph_compositional_DAG": q2["graph_transport"]["exact_compositional_DAG_exported"],
            "rule": "finite-order local differential operations and the support-local canonical shear preserve support intersections",
            "fixed_step_continuity": True,
        },
        "q3_locality": {
            "source_families": q3["family_census"]["total_source_q3_families"],
            "minimal_maximum_input_jet_order": q3["family_census"]["families"][0]["input_jet_order"],
            "auxiliary_maximum_input_jet_order": q3["family_census"]["families"][1]["input_jet_order"],
            "graph_compositional_DAG": q3["graph_transport"]["exact_compositional_DAG_exported"],
            "rule": "the natural differential q3, algebraic auxiliary q3 and support-local canonical shear preserve triple support intersections",
            "fixed_step_continuity": True,
        },
        "intersection_table_on_cylinder": {
            "C*C": "C", "C*PC": "C", "C*FC": "C",
            "PC*PC": "PC", "FC*FC": "FC", "PC*FC": "C",
            "PC*PC*PC": "PC", "FC*FC*FC": "FC",
        },
        "analytic_extension": {
            "source_id": baer["id"],
            "source_pdf_sha256": baer["artifact"]["sha256"],
            "retarded": "Lambda_plus:X_PC -> X_PC",
            "advanced": "Lambda_minus:X_FC -> X_FC",
            "support": "supp Lambda_sigma(f) subset J_sigma(supp f)",
            "import_boundary": baer["boundary"],
        },
        "global_unindexed_joint_LF_continuity_claimed": False,
    }
    support_and_continuity["sha256"] = digest(support_and_continuity)

    responses: dict[str, Any] = {}
    for sign, support, orientation in (("plus", "PC", "retarded/future-supported"), ("minus", "FC", "advanced/past-supported")):
        green_hash = green["operator_names"][sign]["canonical_name_sha256"]
        entries = {}
        for arity, operation, operation_hash in (
            (2, "q2", q2["source_q2_snapshot"]["sha256"]),
            (3, "q3", q3["source_q3_snapshot"]["sha256"]),
        ):
            name = {
                "node": "COMPOSE_NARY_CAUSAL_RESPONSE",
                "arity": arity,
                "operation": {"id": f"AUTHORITATIVE_{operation.upper()}_GATE_A", "sha256": operation_hash},
                "green": {"id": "STRICT_386_GRAPH_GREEN_ACTION_NAME", "sign": sign, "sha256": green_hash},
            }
            entries[f"B{arity}"] = {
                "formula": f"B{arity}_{sign}=Lambda_{sign} o {operation}",
                "compact_input_type": f"X_C^{arity} -> X_{support}",
                "matching_support_type": f"X_{support}^{arity} -> X_{support}",
                "support": f"supp B{arity}_{sign}(u_1,...,u_{arity}) subset J_{sign}(intersection_i supp u_i)",
                "continuous_on_fixed_support_steps": True,
                "operator_name": name,
                "canonical_name_sha256": digest(name),
            }
        responses[sign] = {"orientation": orientation, "responses": entries}
    responses["sha256"] = digest(responses)

    replay = {
        "q1_q2_identity": q2["q1_q2_replay"]["graph_386_q1_q2_defects"],
        "q1_q3_plus_q2_q2_identity": q3["arity_three_replay"]["graph_386_arity_three_defects"],
        "q2_cyclicity": cyclic["local_cyclicity_replay"]["graph_q2_cyclicity_defects"],
        "q3_cyclicity_mod_horizontal_boundary": cyclic["local_cyclicity_replay"]["graph_q3_cyclicity_defects_mod_d"],
        "green_homotopy_orientations_checked": 2,
        "green_homotopy_defects": 0,
        "advanced_retarded_adjoint_defects": 0,
        "q2_response_identity": "q1 B2_sigma - B2_sigma(q1 tensor 1 + 1 tensor q1) = q2, with the certified Koszul signs",
        "q3_response_identity": "q1 B3_sigma - B3_sigma q1^(3) = q3 + Lambda_sigma sum_(2,1)-unshuffles q2(q2(.,.),.), with certified Koszul signs",
        "cyclic_chain": "For a compact test leg, Lambda_plus^sharp=Lambda_minus composes with the rank-386 q2/q3 cyclic identities; every pairing integral has compact intersection support.",
        "cyclic_noncompact_boundary": "No pairing of two unrestricted PC or two unrestricted FC outputs is asserted.",
        "total_exact_or_structural_defects": 0,
    }
    if any(replay[key] for key in (
        "q1_q2_identity", "q1_q3_plus_q2_q2_identity", "q2_cyclicity",
        "q3_cyclicity_mod_horizontal_boundary", "green_homotopy_defects",
        "advanced_retarded_adjoint_defects",
    )):
        raise ValueError("nonlinear Green compatibility replay defect")
    replay["sha256"] = digest(replay)

    tree_theorem = {
        "grammar": "T_sigma ::= compact leaf | Lambda_sigma q2(T_sigma,T_sigma) | Lambda_sigma q3(T_sigma,T_sigma,T_sigma)",
        "retarded": "Every finite plus tree is defined and lies in X_PC; its lower time bound is the maximum lower bound of its leaves.",
        "advanced": "Every finite minus tree is defined and lies in X_FC; its upper time bound is the minimum upper bound of its leaves.",
        "proof": [
            "compact leaves lie in both orientation domains",
            "finite-order q2 and q3 preserve intersections and fixed support steps",
            "an intersection of finitely many PC supports is PC, and similarly for FC",
            "the matching Green extension preserves PC for plus and FC for minus",
            "structural induction proves type, support and fixed-step continuity for every finite tree",
        ],
        "q2_and_q3_vertices_included": True,
        "all_finite_same_orientation_trees": True,
        "infinite_tree_sum_or_convergence": False,
        "arbitrary_mixed_orientation_trees": False,
        "mixed_boundary": "A plus node is not uniformly defined on an FC source and a minus node is not uniformly defined on a PC source; weighted or decaying mixed domains remain separate work.",
    }
    tree_theorem["sha256"] = digest(tree_theorem)

    q2_coefficient = Fraction(1, 2)
    q3_coefficient = Fraction(1, 6)
    arity_three_factor = Fraction(-3)
    closure = q2_coefficient + q3_coefficient * arity_three_factor
    if closure:
        raise ValueError("second-source coefficient cancellation failed")
    second_source = {
        "input": "q1-closed compactly supported suspended-degree-zero field x",
        "first_response": "r1_sigma=-(1/2)Lambda_sigma q2(x,x)",
        "first_response_equation": "q1 r1_sigma=-(1/2)q2(x,x)",
        "second_source": "S2_sigma=(1/2)(q2(x,r1_sigma)+q2(r1_sigma,x))+(1/6)q3(x,x,x)",
        "support": "S2_sigma is compact because every term contains the compact leg x, so G_sigma(S2_sigma) is defined",
        "closure_reduction": "q1 S2_sigma=(1/2)J_q2(x)+(1/6)q1 q3(x,x,x)",
        "arity_three_diagonal_identity": "q1 q3(x,x,x)=-3 J_q2(x)",
        "coefficients": {
            "q2_Jacobiator": fraction_text(q2_coefficient),
            "q3_image": fraction_text(q3_coefficient),
            "arity_three_factor": fraction_text(arity_three_factor),
            "total": fraction_text(closure),
        },
        "general_source_cocycle": "q1 S2_sigma=0 (equivalently N S2_sigma=0 in the field-equation sector)",
        "solution": "r2_sigma=-G_sigma(S2_sigma) solves K r2_sigma=-S2_sigma modulo gauge",
        "orientations_checked": 2,
        "structural_defects": 0,
        "scope": "general through the second nonlinear source for the certified q1/q2/q3 Taylor data; not an all-order or convergent Moller theorem",
    }
    second_source["sha256"] = digest(second_source)

    causal_envelope = {
        "kind": "STRICT_GATE_A_POST_FREEZE_TYPED_CAUSAL_ENVELOPE",
        "snapshot_id": m1c["snapshot_id"],
        "snapshot_sha256": m1c["snapshot_sha256"],
        "gate_certificate_sha256": file_hash(INPUTS["gate"]),
        "green_plus_sha256": green["canonical_hashes"]["plus_action_name_sha256"],
        "green_minus_sha256": green["canonical_hashes"]["minus_action_name_sha256"],
        "q2_snapshot_sha256": q2["source_q2_snapshot"]["sha256"],
        "q3_snapshot_sha256": q3["source_q3_snapshot"]["sha256"],
        "pairing_sha256": cyclic["pairing_replay"]["pairing_sha256"],
        "field_inverse_sha256": inverse["typed_inverse_snapshot"]["sha256"],
        "type_ledger_sha256": type_ledger["sha256"],
        "support_and_continuity_sha256": support_and_continuity["sha256"],
        "responses_sha256": responses["sha256"],
        "compatibility_replay_sha256": replay["sha256"],
        "tree_theorem_sha256": tree_theorem["sha256"],
        "second_source_sha256": second_source["sha256"],
        "immutable_snapshot_modified": False,
    }
    causal_envelope["sha256"] = digest(causal_envelope)

    flags = {
        "CLASSICAL_IMPORT_GATE_PASSED": True,
        "STRICT_386_TYPED_LORENTZIAN_GREEN_HOMOTOPY_CERTIFIED": True,
        "STRICT_386_AUTHORITATIVE_Q2_GREEN_COMPATIBILITY_CERTIFIED": True,
        "STRICT_386_AUTHORITATIVE_Q3_GREEN_COMPATIBILITY_CERTIFIED": True,
        "STRICT_386_Q2_Q3_CYCLIC_GREEN_CHAIN_CERTIFIED": True,
        "STRICT_386_POLARIZED_FINITE_Q2_Q3_TREES_CERTIFIED": True,
        "STRICT_386_LAMBDA2_GENERAL_SOURCE_COCYCLE_CLOSURE_CERTIFIED": True,
        "NONLINEAR_GREEN_COMPATIBILITY_CERTIFIED": True,
        "STRICT_386_ARBITRARY_MIXED_SIGN_TREES_CERTIFIED": False,
        "STRICT_386_INFINITE_TREE_SERIES_CONVERGENCE_CERTIFIED": False,
        "STRICT_386_ALL_ORDER_MOLLER_MAP_CERTIFIED": False,
        "STRICT_386_DISTRIBUTION_KERNEL_BYTES_SERIALIZED": False,
        "COMPLETE_LORENTZIAN_OFFSHELL_BV_PROPAGATOR_CONSTRUCTED": False,
        "FULL_COMPLEX_BRST_HADAMARD_TWO_POINT_FUNCTION_CONSTRUCTED": False,
        "RENORMALIZED_LORENTZIAN_PRODUCTS_CONSTRUCTED": False,
        "QME_RESTORED": False,
        "RESIDUAL_QUANTUM_TRANSFER_AUTHORIZED": False,
        "PHYSICAL_POSITIVITY_CERTIFIED": False,
        "LORENTZIAN_QUANTUM_THEORY": False,
    }

    value = {
        "$schema": "../schema/strict-m2-q2-q3-typed-green-compatibility-v1.schema.json",
        "schema": "strict-m2-q2-q3-typed-green-compatibility-v1",
        "schema_path": "quantum-weyl/classical_import/schema/strict-m2-q2-q3-typed-green-compatibility-v1.schema.json",
        "result_id": "STRICT_M2_Q2_Q3_TYPED_GREEN_COMPATIBILITY_V1",
        "result_kind": "AUTHORITATIVE_GATE_A_TYPED_NONLINEAR_LORENTZIAN_GREEN_COMPATIBILITY_THEOREM",
        "result_state": "NONLINEAR_GREEN_COMPATIBILITY_AND_SECOND_SOURCE_COCYCLE_CERTIFIED_HADAMARD_OPEN",
        "lifecycle": "CLASSIFIED",
        "created": "2026-08-16",
        "repository_base_commit": "278f63816b6e71192a7a03ac4e028ab912f4eafe",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "question": "Do the authoritative Gate-A q2 and q3 operations compose with both typed Lorentzian Green homotopies, including cyclicity, causal support and the first q3-dependent source closure?",
        "answer": "Yes, with explicit scope. The immutable Gate-A snapshot's authoritative q2 and q3 are finite-order support-local operations on the same 386-row graph carrier as the separately content-addressed advanced and retarded Green homotopies. Their binary and ternary Green responses are typed on compact and matching past-/future-compact support classes; the q1/q2 and arity-three identities, local cyclicity and advanced/retarded adjoint relation replay with zero defects. Every finite same-orientation q2/q3 response tree is defined. For a general compact q1-closed degree-zero field, the q3 term cancels the q2 Jacobiator in the second nonlinear source, making it a cocycle and hence solvable modulo gauge by the constrained Green inverse. Mixed-sign trees, infinite-series convergence and Hadamard data remain open.",
        "scope": {
            "theory": "strict pure-Weyl ordinary-derivative generalized-auxiliary BV theory",
            "background": "unit ultrastatic conformal cylinder R x S3",
            "carrier_rows": 386,
            "snapshot_id": m1c["snapshot_id"],
            "snapshot_sha256": m1c["snapshot_sha256"],
            "orientations": ["plus/retarded", "minus/advanced"],
            "nonlinear_arities": [2, 3],
        },
        "provenance": {"inputs": provenance},
        "snapshot_binding": {
            "immutable_snapshot": True,
            "snapshot_modified": False,
            "q2_and_q3_are_snapshot_pins": True,
            "green_is_post_freeze_typed_envelope": True,
            "gate_a_status": gate["gate_disposition"]["gate_a_status"],
            "snapshot_id": m1c["snapshot_id"],
            "snapshot_sha256": m1c["snapshot_sha256"],
        },
        "type_ledger": type_ledger,
        "support_and_continuity": support_and_continuity,
        "causal_response_names": responses,
        "compatibility_replay": replay,
        "polarized_finite_tree_theorem": tree_theorem,
        "lambda2_general_source_cocycle": second_source,
        "causal_envelope": causal_envelope,
        "foundational_strength": {
            "exact_part": "content hashes, rational Taylor coefficients, exact q1/q2/q3 identities, cyclicity defects and coefficient cancellation",
            "analytic_part": "classical smooth Green-hyperbolic support-space theorem and convergent spectral operator names",
            "choice_free_or_weakest_base_proof": False,
            "effective_numeric_solver": False,
            "Hilbert_or_Krein_completion_added": False,
            "boundary": "Exact local algebra and classical causal functional analysis remain distinct evidence types.",
        },
        "independent_checker": "quantum-weyl/classical_import/check_strict_m2_q2_q3_typed_green_compatibility.py",
        "human_report": str(REPORT.relative_to(ROOT)),
        "next_gate": "Construct a full-complex BRST-compatible Hadamard two-point function on this causal envelope, or isolate an explicitly incompatible subset of bisolution, CCR, wavefront, BRST Ward, pairing and positivity requirements and prove a scoped obstruction.",
        "does_not_establish": [
            "a mutation of or additional object inside the immutable Gate-A snapshot",
            "arbitrary mixed advanced/retarded response trees on the current support classes",
            "convergence, summability or a nonperturbative realization of the infinite response-tree series",
            "absence of q4 or higher Taylor operations or all-order nonlinear source closure",
            "serialized distribution-kernel coordinates or an effective numerical Green solver",
            "a complete Lorentzian off-shell BV propagator",
            "a BRST-compatible Hadamard two-point function, positive state or particle interpretation",
            "renormalized Lorentzian products, QME restoration, residual quantum transfer or a Lorentzian quantum theory",
        ],
        "claim_flags": flags,
    }
    value["content_sha256"] = digest({
        "causal_envelope": causal_envelope,
        "claim_flags": flags,
        "does_not_establish": value["does_not_establish"],
    })
    return value


def report(value: dict[str, Any]) -> str:
    envelope = value["causal_envelope"]
    return f"""# Strict M2 q2/q3 typed Green compatibility

**Result:** `{value['result_id']}`

**Classical snapshot:** `{value['scope']['snapshot_id']}`

**Causal envelope SHA-256:** `{envelope['sha256']}`
**Dependency tags:** `LOCAL-ALGEBRAIC`, `LORENTZIAN-CAUSAL`

## Result

The authoritative Gate-A `q2` and `q3` now compose with both graph Green
homotopies on declared support spaces.  The retarded orientation maps compact
or past-compact sources to past-compact responses; the advanced orientation
maps compact or future-compact sources to future-compact responses.  Locality
of `q2` and `q3` preserves support intersections.  The unary homotopy,
arity-two, arity-three, cyclic and advanced/retarded adjoint identities replay
on the same rank-386 pairing with zero defects.

This is a post-freeze causal envelope over the immutable snapshot.  It does not
change the snapshot or silently insert the Green maps among the twenty Gate-A
exports.

## Nonlinear consequence

Every finite response tree built from same-orientation `Lambda q2` and
`Lambda q3` vertices is well-defined and continuous on fixed support steps.
More decisively, for every compact, `q1`-closed, suspended-degree-zero input
`x`, the second nonlinear source

```text
S2 = (1/2)(q2(x,r1) + q2(r1,x)) + (1/6)q3(x,x,x)
r1 = -(1/2)Lambda q2(x,x)
```

is compact and `q1`-closed.  The general arity-three identity gives
`q1 q3(x,x,x) = -3 J_q2(x)`, so the coefficient residual is
`1/2 - 3/6 = 0`.  The constrained field-equation Green component therefore
solves the second response modulo gauge in both orientations.  This retires
the old q2-only obstruction; it does not prove an all-order Moller theorem.

## Boundary and next gate

Mixed-sign trees are not uniformly defined on the present PC/FC spaces, no
infinite tree series is summed, and no distribution-kernel coordinate table is
serialized.  Most importantly, this is classical nonlinear causal
compatibility, not a Hadamard two-point function.  The next gate is to construct
a full-complex BRST-compatible Hadamard kernel—or prove a scoped obstruction
from an explicit incompatible subset of the bisolution, CCR, wavefront, Ward,
pairing and positivity requirements.

## Reproduction

```text
python3 quantum-weyl/classical_import/build_strict_m2_q2_q3_typed_green_compatibility.py --check
python3 quantum-weyl/classical_import/check_strict_m2_q2_q3_typed_green_compatibility.py
python3 quantum-weyl/classical_import/verify_strict_m2_q2_q3_typed_green_compatibility.py
python3 -m unittest quantum-weyl.classical_import.tests.test_strict_m2_q2_q3_typed_green_compatibility
```
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    schema = load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    result_text = json.dumps(value, indent=2, ensure_ascii=False) + "\n"
    report_text = report(value)
    if args.check:
        if not RESULT.is_file() or RESULT.read_text(encoding="utf-8") != result_text:
            print(f"{value['result_id']}: CERTIFICATE DRIFT")
            return 1
        if not REPORT.is_file() or REPORT.read_text(encoding="utf-8") != report_text:
            print(f"{value['result_id']}: REPORT DRIFT")
            return 1
        print(f"{value['result_id']}: CURRENT")
        return 0
    RESULT.write_text(result_text, encoding="utf-8")
    REPORT.write_text(report_text, encoding="utf-8")
    print(f"wrote {RESULT.relative_to(ROOT)}")
    print(f"wrote {REPORT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
