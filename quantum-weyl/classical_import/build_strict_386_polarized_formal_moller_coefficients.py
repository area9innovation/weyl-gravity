#!/usr/bin/env python3
"""Build exact polarized formal Yang--Feldman coefficient evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from math import comb
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_386_POLARIZED_FORMAL_MOLLER_COEFFICIENTS_V1.json"
REPORT = HERE / "REPORT_STRICT_386_POLARIZED_FORMAL_MOLLER_COEFFICIENTS_V1.md"

TREES = HERE / "certificates/STRICT_386_RECURSIVE_CAUSAL_TREE_DOMAINS_V1.json"
RESPONSE = HERE / "certificates/STRICT_386_STABILIZED_Q2_GREEN_COMPOSITION_PREFLIGHT_V1.json"
Q2_IDENTITY = HERE / "certificates/STRICT_LOCAL_Q1_Q2_IDENTITY_V1.json"
INPUTS = (
    (TREES, "STRICT_386_RECURSIVE_CAUSAL_TREE_DOMAINS_V1", "finite polarized support-domain theorem"),
    (RESPONSE, "STRICT_386_STABILIZED_Q2_GREEN_COMPOSITION_PREFLIGHT_V1", "binary response and homotopy identity"),
    (Q2_IDENTITY, "STRICT_LOCAL_Q1_Q2_IDENTITY_V1", "suspended factorial convention and arity-two identity"),
)
MAX_LEAVES = 9


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def source_id(value: Mapping[str, Any]) -> str | None:
    return value.get("result_id") or value.get("certificate_id") or value.get("schema")


def frac(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def catalan(index: int) -> int:
    return comb(2 * index, index) // (index + 1)


def plane_trees(leaves: int, memo: dict[int, tuple[str, ...]]) -> tuple[str, ...]:
    if leaves not in memo:
        memo[leaves] = tuple(
            f"B({left},{right})"
            for split in range(1, leaves)
            for left in plane_trees(split, memo)
            for right in plane_trees(leaves - split, memo)
        )
    return memo[leaves]


def coefficient_table() -> list[dict[str, Any]]:
    memo: dict[int, tuple[str, ...]] = {1: ("x",)}
    rows = []
    weights = {1: Fraction(1)}
    for leaves in range(1, MAX_LEAVES + 1):
        if leaves > 1:
            weights[leaves] = -Fraction(1, 2) * sum(
                weights[left] * weights[leaves - left]
                for left in range(1, leaves)
            )
        trees = plane_trees(leaves, memo)
        per_tree = (-Fraction(1, 2)) ** (leaves - 1)
        rows.append({
            "coupling_power": leaves - 1,
            "leaves": leaves,
            "plane_tree_count": len(trees),
            "catalan_closed_form": catalan(leaves - 1),
            "coefficient_per_plane_tree": frac(per_tree),
            "commutative_scalar_collapse": frac(weights[leaves]),
            "recurrence_residual": "0",
            "canonical_tree_list_sha256": digest(list(trees)),
        })
    return rows


def build() -> dict[str, Any]:
    values = {path: json.loads(path.read_text()) for path, _, _ in INPUTS}
    for path, expected, _ in INPUTS:
        if source_id(values[path]) != expected:
            raise ValueError(f"dependency identity drift: {path}")
    trees, response, q2_identity = (values[path] for path, _, _ in INPUTS)
    tree_flags = trees["claim_flags"]
    if not tree_flags.get("STRICT_386_CANDIDATE_RETARDED_ALL_FINITE_Q2_TREES_CERTIFIED"):
        raise ValueError("retarded finite-tree theorem unavailable")
    if not tree_flags.get("STRICT_386_CANDIDATE_ADVANCED_ALL_FINITE_Q2_TREES_CERTIFIED"):
        raise ValueError("advanced finite-tree theorem unavailable")
    if not response["claim_flags"].get("STRICT_386_CANDIDATE_Q2_GREEN_RESPONSE_IDENTITY_VERIFIED"):
        raise ValueError("binary response identity unavailable")
    if q2_identity.get("convention") != "suspended-graded-symmetric-factorial-v1":
        raise ValueError("q2 factorial convention drift")

    literature = {
        "id": "hawkins-rejzner-2020",
        "citation": "Eli Hawkins and Kasia Rejzner, The Star Product in Interacting Quantum Field Theory, Letters in Mathematical Physics 110 (2020), 1257-1313.",
        "stable_url": "https://arxiv.org/abs/1612.09157",
        "artifact": {
            "status": "CONTENT_PINNED",
            "locator": "https://arxiv.org/pdf/1612.09157",
            "sha256": "8175a1e403cf4843c171a5df040f35decb591280cd19d1a099323c29f642957e",
        },
        "imported_statement": "Lemma 3.12: for formal lambda, the retarded Moller map satisfies the Yang-Feldman equation; its inverse is identity plus the retarded free Green response; Picard iteration converges lambda-adically, while nonperturbative inverse existence is a separate issue.",
        "application_boundary": "The paper treats an action-derived Euler-Lagrange interaction and a Green-hyperbolic free operator. It supplies the formal template, not Weyl-BV theory identity, the candidate q2, a full BV Green inverse, or a QME theorem.",
    }
    literature["sha256"] = digest(literature)

    convention = {
        "input": "a compactly supported smooth ghost-number-zero bosonic section x on the 386-row graph carrier",
        "orientation_symbol": "sigma in {plus(retarded), minus(advanced)}",
        "binary_response": "B_sigma(u,v)=Lambda_graph,sigma(q2_candidate(u,v))",
        "series": "R_sigma,lambda(x)=sum_{m>=0} lambda^m r_sigma,m(x)",
        "fixed_point": "R_sigma,lambda(x)=x-(lambda/2) B_sigma(R_sigma,lambda(x),R_sigma,lambda(x))",
        "inverse_name": "I_sigma,lambda(y)=y+(lambda/2) B_sigma(y,y)",
        "direction": "R is the formal inverse of I; this direction matches the retarded Yang-Feldman convention in the pinned template.",
        "factor_one_half_source": "suspended-graded-symmetric-factorial-v1 q2 convention",
        "terminology": "candidate polarized formal Yang-Feldman/Moller coefficients",
    }
    convention["sha256"] = digest(convention)

    recurrence = {
        "base": "r_sigma,0(x)=x",
        "step": "r_sigma,m(x)=-(1/2) sum_{i+j=m-1} B_sigma(r_sigma,i(x),r_sigma,j(x)) for m>=1",
        "triangular_uniqueness": "The coefficient of lambda^m depends only on coefficients of lower powers, hence exists uniquely by finite recursion.",
        "coefficientwise_residual": "[lambda^m](R-x+(lambda/2)B_sigma(R,R))=0 for every m>=0",
        "inverse_composition": "I_sigma,lambda(R_sigma,lambda(x))=x coefficientwise; uniqueness gives R_sigma,lambda(I_sigma,lambda(y))=y in the typed formal algebra whenever the compositions are admitted.",
        "picard_stabilization": "Starting at R^(0)=x, the coefficient of lambda^m in R^(k+1)=x-(lambda/2)B(R^(k),R^(k)) stabilizes by k=m.",
        "formal_topology": "lambda-adic only: for every N, a finite Picard iterate agrees modulo lambda^(N+1)",
        "analytic_norm_or_radius": "NOT_SUPPLIED",
    }
    recurrence["sha256"] = digest(recurrence)

    table = coefficient_table()
    tree_formula = {
        "formula": "r_sigma,m(x)=(-1/2)^m sum_{T in PBT_(m+1)} T[B_sigma;x]",
        "index_family": "plane full binary trees with m+1 leaves",
        "tree_count": "Catalan(m)",
        "all_orders_proof": "Root decomposition is a disjoint union over left-leaf counts 1 through m and reproduces the triangular recurrence.",
        "checked_through_leaves": MAX_LEAVES,
        "checked_rows": table,
        "low_orders": [
            "r_0=x",
            "r_1=-(1/2)B(x,x)",
            "r_2=(1/4)(B(x,B(x,x))+B(B(x,x),x))",
            "r_3=-(1/8) sum over the five four-leaf plane B-trees",
        ],
    }
    tree_formula["sha256"] = digest(tree_formula)

    orientations = {
        "plus": {
            "name": "retarded",
            "coefficient_support_for_m_ge_1": "past compact",
            "lower_time_bound": "max of the compact leaf lower bounds",
            "every_finite_coefficient_defined": True,
            "fixed_step_continuity": "continuous homogeneous polynomial of degree m+1 on every fixed compact leaf-support Frechet step",
        },
        "minus": {
            "name": "advanced",
            "coefficient_support_for_m_ge_1": "future compact",
            "upper_time_bound": "min of the compact leaf upper bounds",
            "every_finite_coefficient_defined": True,
            "fixed_step_continuity": "continuous homogeneous polynomial of degree m+1 on every fixed compact leaf-support Frechet step",
        },
    }
    orientations["sha256"] = digest(orientations)

    bv_diagnostic = {
        "assumption": "q1(x)=0 and x has suspended degree zero",
        "candidate_equation_tested": "E_lambda(R)=q1(R)+(lambda/2)q2_candidate(R,R)",
        "order_lambda_residual": "q1(r_1)+(1/2)q2(x,x)=0",
        "order_lambda_squared_residual": "(1/4)(B_sigma(x,q2(x,x))+B_sigma(q2(x,x),x))",
        "order_lambda_squared_zero_certified": False,
        "meaning": "The arity-two homotopy-response identity closes the first equation coefficient but does not by itself prove that the formal fixed point is a Maurer-Cartan solution. A typed field-equation Green inverse and the source q2/q3/higher L-infinity identities are still required.",
        "nonzero_claimed": False,
        "obstruction_or_missing_identity": "UNDECIDED",
    }
    bv_diagnostic["sha256"] = digest(bv_diagnostic)

    foundations = {
        "classification": "UNIFORM_PRIMITIVE_RECURSIVE_FORMAL_COEFFICIENT_SCHEMA_OVER_IMPORTED_CLASSICAL_GREEN_ANALYSIS",
        "fixed_order": "For each requested m, the tree set, exact rational weights, residual check and support proof are finite primitive-recursive data.",
        "formal_sequence": "Coding the whole coefficient family as an omega-sequence uses ordinary recursion/comprehension (available in ZF and standard weak second-order bases) but no choice function.",
        "lambda_adic_completion": "A formal-series type is a countable coefficient sequence; lambda-adic stabilization is not metric or analytic convergence.",
        "analytic_realization": "Every coefficient still imports the classical PC/FC Green-extension and smooth support-space theorem pinned by the predecessor.",
        "choice_operation_added": False,
        "infinite_analytic_sum_added": False,
        "weakest_complete_foundational_base": "NOT_ESTABLISHED",
    }
    foundations["sha256"] = digest(foundations)

    authority = {
        "candidate_q2_only": True,
        "formal_template_source_pinned": True,
        "action_derived_interaction_identity": False,
        "typed_field_equation_green_inverse": False,
        "authoritative_full_q2_imported": False,
        "q3_or_higher_operations_imported": False,
        "formal_moller_map_for_weyl_bv_certified": False,
        "classical_import_gate_a_status": "FAIL_CLOSED",
    }
    authority["sha256"] = digest(authority)

    flags = {
        "STRICT_386_CANDIDATE_POLARIZED_FORMAL_COEFFICIENTS_CERTIFIED": True,
        "STRICT_386_CANDIDATE_COEFFICIENTWISE_FIXED_POINT_VERIFIED": True,
        "STRICT_386_CANDIDATE_CATALAN_TREE_FORMULA_VERIFIED": True,
        "STRICT_386_CANDIDATE_FORMAL_INVERSE_VERIFIED": True,
        "STRICT_386_CANDIDATE_LAMBDA_ADIC_STABILIZATION_VERIFIED": True,
        "STRICT_386_CANDIDATE_ANALYTIC_SERIES_CONVERGENCE_CERTIFIED": False,
        "STRICT_386_CANDIDATE_NONPERTURBATIVE_MOLLER_MAP_CONSTRUCTED": False,
        "STRICT_386_WEYL_BV_MAURER_CARTAN_SERIES_CERTIFIED": False,
        "STRICT_386_AUTHORITATIVE_FORMAL_MOLLER_MAP_CERTIFIED": False,
        "STRICT_386_Q3_OR_HIGHER_CAUSAL_TREES_CERTIFIED": False,
        "CLASSICAL_IMPORT_GATE_PASSED": False,
        "HADAMARD_STATE_CONSTRUCTED": False,
        "RENORMALIZED_LORENTZIAN_PRODUCTS": False,
        "QME_RESTORED": False,
        "RESIDUAL_TRANSFERRED": False,
        "LORENTZIAN_QUANTUM_THEORY": False,
    }

    snapshot = {
        "kind": "STRICT_386_CANDIDATE_POLARIZED_FORMAL_YANG_FELDMAN_COEFFICIENT_SNAPSHOT",
        "orientation_count": 2,
        "convention_sha256": convention["sha256"],
        "recurrence_sha256": recurrence["sha256"],
        "tree_formula_sha256": tree_formula["sha256"],
        "orientations_sha256": orientations["sha256"],
        "bv_diagnostic_sha256": bv_diagnostic["sha256"],
        "foundations_sha256": foundations["sha256"],
        "authority_sha256": authority["sha256"],
        "receiver_status": "FORMAL_FIXED_POINT_COEFFICIENTS_ONLY_NOT_WEYL_BV_MOLLER_OR_GATE_A",
    }
    snapshot["sha256"] = digest(snapshot)

    value = {
        "$schema": "../schema/strict-386-polarized-formal-moller-coefficients-v1.schema.json",
        "schema": "strict-386-polarized-formal-moller-coefficients-v1",
        "schema_path": "quantum-weyl/classical_import/schema/strict-386-polarized-formal-moller-coefficients-v1.schema.json",
        "result_id": "STRICT_386_POLARIZED_FORMAL_MOLLER_COEFFICIENTS_V1",
        "result_kind": "CANDIDATE_POLARIZED_FORMAL_YANG_FELDMAN_COEFFICIENT_THEOREM_WITH_BV_PROMOTION_GATE",
        "result_state": "FORMAL_FIXED_POINT_COEFFICIENTS_CERTIFIED_MOLLER_AND_MAURER_CARTAN_PROMOTION_OPEN",
        "lifecycle": "CLASSIFIED",
        "created": "2026-08-15",
        "repository_base_commit": "5754b7b4aa89243078e0bb4967a276c3c79a690f",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "question": "Do the finite polarized q2/Green trees assemble into unique formal coefficients, and is that already a Weyl-BV Moller map?",
        "answer": "The coefficients do assemble uniquely. For each orientation the quadratic Yang-Feldman fixed-point equation has a unique lambda-adic formal inverse whose m-th coefficient is the exact sum of the Catalan(m) plane binary response trees with weight (-1/2)^m. Every coefficient is defined on the certified PC/FC support domain and is continuous on fixed support steps. This is formal convergence only. More importantly, it is not yet a Weyl-BV Moller theorem: the first BV equation coefficient closes, but at lambda squared the available identities leave an explicit B(q2) residual whose vanishing is not certified. The candidate lacks authoritative q2 identity, a typed field-equation Green inverse, and q3/higher source data.",
        "scope": {
            "theory": "strict pure-Weyl stabilized q2 candidate",
            "background": "unit ultrastatic vacuum conformal cylinder R x S3",
            "carrier": "fixed 386-row graph BV carrier",
            "inputs": "compactly supported smooth ghost-number-zero bosonic sections",
            "orientations": ["plus/retarded", "minus/advanced"],
            "completion": "formal lambda-adic coefficient sequence only",
        },
        "literature_template": literature,
        "formal_convention": convention,
        "coefficient_recurrence": recurrence,
        "catalan_tree_formula": tree_formula,
        "polarized_support_and_continuity": orientations,
        "bv_equation_diagnostic": bv_diagnostic,
        "foundational_strength": foundations,
        "authority_boundary": authority,
        "formal_coefficient_snapshot": snapshot,
        "claim_flags": flags,
        "does_not_establish": [
            "that the stabilized q2 candidate is the authoritative nonlinear classical Weyl BV operation",
            "that the action-derived hypotheses of the pinned Moller theorem hold for the candidate",
            "a typed inverse of the full Weyl-BV field-equation operator",
            "vanishing or nonvanishing of the displayed lambda-squared BV residual",
            "a Maurer-Cartan solution or a source-certified q2/q3/higher L-infinity solution",
            "analytic convergence, summability, a convergence radius, a nonperturbative inverse or a selected classical solution",
            "mixed-sign causal-difference recursion",
            "an accepted Gate-A q2 or formal-map hash",
            "a Hadamard state, positivity, renormalized Lorentzian products, QME restoration, residual transfer, unitarity or a Lorentzian quantum theory",
        ],
        "next_gate": "Source-certify the authoritative nonlinear brackets and type the Green homotopy on the actual field-equation sector. Replay the lambda-squared BV residual with q2/q3 identities; only if every coefficient of the interacting equation closes may these formal fixed-point coefficients be promoted to a Weyl-BV Moller map. Analytic convergence remains a later, independent gate.",
        "canonical_hashes": {
            "literature_template_sha256": literature["sha256"],
            "formal_convention_sha256": convention["sha256"],
            "coefficient_recurrence_sha256": recurrence["sha256"],
            "catalan_tree_formula_sha256": tree_formula["sha256"],
            "polarized_support_sha256": orientations["sha256"],
            "bv_equation_diagnostic_sha256": bv_diagnostic["sha256"],
            "foundational_strength_sha256": foundations["sha256"],
            "authority_boundary_sha256": authority["sha256"],
            "formal_coefficient_snapshot_sha256": snapshot["sha256"],
        },
        "provenance": {
            "inputs": [
                {"path": str(path.relative_to(ROOT)), "result_or_artifact_id": expected, "sha256": sha(path), "role": role}
                for path, expected, role in INPUTS
            ]
        },
        "independent_checker": {
            "path": "quantum-weyl/classical_import/check_strict_386_polarized_formal_moller_coefficients.py",
            "checks": [
                "dependency identities and hashes",
                "independent postfix plane-tree enumeration through nine leaves",
                "exact rational recurrence and Catalan closed form",
                "coefficientwise fixed-point residual and Picard stabilization",
                "polarized support and continuity inheritance",
                "lambda-squared BV residual derivation",
                "formal-versus-analytic and Moller/QME authority firewalls",
            ],
        },
        "human_report": "quantum-weyl/classical_import/REPORT_STRICT_386_POLARIZED_FORMAL_MOLLER_COEFFICIENTS_V1.md",
    }
    return value


def render(value: Mapping[str, Any]) -> str:
    rows = value["catalan_tree_formula"]["checked_rows"]
    lines = [
        "# Strict 386-row polarized formal Møller-coefficient gate", "", "## Outcome", "",
        value["answer"], "", "## Explicit convention", "", "```text",
        value["formal_convention"]["fixed_point"],
        value["coefficient_recurrence"]["step"], "```", "",
        "The word *Møller* is conditional here: the exact object is the candidate formal Yang--Feldman inverse defined by the displayed equation.", "",
        "## Exact coefficient census", "", "| Coupling power | Leaves | Plane trees | Weight per tree | Scalar collapse |", "|---:|---:|---:|---:|---:|",
    ]
    lines.extend(
        f"| {row['coupling_power']} | {row['leaves']} | {row['plane_tree_count']} | `{row['coefficient_per_plane_tree']}` | `{row['commutative_scalar_collapse']}` |"
        for row in rows
    )
    d = value["bv_equation_diagnostic"]
    lines += [
        "", "## The promotion gate discovered", "", "For a q1-closed degree-zero input:", "", "```text",
        d["order_lambda_residual"], d["order_lambda_squared_residual"], "```", "",
        "The first line closes exactly. The second expression is not certified to vanish and is not claimed nonzero. This is the first point where a formal response-tree inverse stops being automatically identifiable with a Weyl-BV Maurer--Cartan/Møller map.", "",
        "## Foundations", "", value["foundational_strength"]["fixed_order"], "",
        value["foundational_strength"]["lambda_adic_completion"], "",
        "## Reproduction", "", "```text",
        "python3 quantum-weyl/classical_import/build_strict_386_polarized_formal_moller_coefficients.py --check",
        "python3 quantum-weyl/classical_import/check_strict_386_polarized_formal_moller_coefficients.py",
        "python3 quantum-weyl/classical_import/verify_strict_386_polarized_formal_moller_coefficients.py",
        "python3 -m unittest quantum-weyl/classical_import/tests/test_strict_386_polarized_formal_moller_coefficients.py",
        "```", "", "## Boundaries", "",
    ]
    lines.extend(f"- This does not establish {item}." for item in value["does_not_establish"])
    lines += ["", "## Next gate", "", value["next_gate"], ""]
    return "\n".join(lines)


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
        print("STRICT_386_POLARIZED_FORMAL_MOLLER_COEFFICIENTS_V1: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    RESULT.write_bytes(result)
    REPORT.write_bytes(report)
    print("STRICT_386_POLARIZED_FORMAL_MOLLER_COEFFICIENTS_V1: wrote certificate and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
