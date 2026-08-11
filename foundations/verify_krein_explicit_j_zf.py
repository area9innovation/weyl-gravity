#!/usr/bin/env python3
"""Verifier for the explicit Krein/Fock construction in ZF."""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from foundations.check_krein_explicit_j import check


RESULT_PATH = ROOT / "foundations/results/FOUNDATIONAL_KREIN_EXPLICIT_J_ZF_V1.json"
SCHEMA_PATH = ROOT / "foundations/schema/foundational-krein-explicit-j-zf-v1.schema.json"
REPORT_PATH = ROOT / "foundations/reports/krein-explicit-j-zf-audit.md"
CHECKER_PATH = ROOT / "foundations/check_krein_explicit_j.py"
ONE_PARTICLE_PATH = ROOT / "analytic_completion/certificates/one_particle_krein.json"
FOCK_PATH = ROOT / "analytic_completion/certificates/fock_fundamental_symmetry.json"
LITERATURE_PATH = ROOT / "foundations/literature-ledger.json"
SOURCE_LEDGER_PATH = ROOT / "symbolic/conformal-paper-verification.sha256"
SHA256 = re.compile(r"^[0-9a-f]{64}$")
GIT_HASH = re.compile(r"^[0-9a-f]{40}$")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def imported_modules(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and node.module != "__future__":
            modules.add(node.module.split(".")[0])
    return modules


def dag_is_acyclic(nodes: set[str], edges: list[dict[str, Any]]) -> bool:
    outgoing: dict[str, list[str]] = {node: [] for node in nodes}
    indegree = {node: 0 for node in nodes}
    for edge in edges:
        source, target = edge.get("from"), edge.get("to")
        if source not in nodes or target not in nodes:
            return False
        outgoing[source].append(target)
        indegree[target] += 1
    ready = [node for node, degree in indegree.items() if degree == 0]
    visited = 0
    while ready:
        node = ready.pop()
        visited += 1
        for target in outgoing[node]:
            indegree[target] -= 1
            if indegree[target] == 0:
                ready.append(target)
    return visited == len(nodes)


def verify(
    *,
    result: dict[str, Any] | None = None,
    one_particle: dict[str, Any] | None = None,
    fock: dict[str, Any] | None = None,
    literature: dict[str, Any] | None = None,
    report_text: str | None = None,
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    checks: list[str] = []
    result = load_json(RESULT_PATH) if result is None else result
    one_particle = load_json(ONE_PARTICLE_PATH) if one_particle is None else one_particle
    fock = load_json(FOCK_PATH) if fock is None else fock
    literature = load_json(LITERATURE_PATH) if literature is None else literature
    report_text = REPORT_PATH.read_text(encoding="utf-8") if report_text is None else report_text
    load_json(SCHEMA_PATH)
    checks.append("schema, result, source certificates, literature ledger, and report parse")

    if result.get("result_id") != "FOUNDATIONAL_KREIN_EXPLICIT_J_ZF_V1":
        errors.append("result id mismatch")
    if result.get("result_kind") != "FOUNDATIONAL_DEPENDENCY_CERTIFICATE":
        errors.append("result kind mismatch")
    if result.get("lifecycle") != "SUFFICIENCY_PROVED":
        errors.append("lifecycle is not SUFFICIENCY_PROVED")
    if result.get("dependency_tags") != ["LOCAL-ALGEBRAIC", "REDUCED-MODE"]:
        errors.append("dependency tags must be LOCAL-ALGEBRAIC and REDUCED-MODE only")
    if not GIT_HASH.fullmatch(result.get("repository_base_commit", "")):
        errors.append("repository base commit is not a full hash")
    context = result.get("programme_context", {})
    if context.get("coverage_matrix") != "FOUNDATIONAL_COVERAGE_MATRIX_V0":
        errors.append("coverage-matrix link mismatch")
    if context.get("opportunity_realized") != "OP-KREIN-EXPLICIT-J-AUDIT":
        errors.append("opportunity link mismatch")
    if context.get("predecessor") != "FOUNDATIONAL_FREE_BV_ENERGY2_PRA_SDR_V1":
        errors.append("predecessor link mismatch")
    checks.append("identity, lifecycle, dependency boundary, and programme links")

    layers = {item.get("id"): item for item in result.get("layer_classification", [])}
    expected_layers = {
        "FINITE-J": ("PRA", "PROVED_FOR_FIXED_FORMULAS", "NO_CHOICE_OPERATION"),
        "COUNTABLE-KREIN-J": ("ZF", "PROVED_BY_EXPLICIT_CONSTRUCTION_AND_PINNED_ZF_THEOREM", "COUNTABLE_CHOICE_NOT_USED"),
        "BOSONIC-FOCK-J": ("ZF", "PROVED_BY_EXPLICIT_OCCUPATION_CONSTRUCTION", "COUNTABLE_CHOICE_NOT_USED"),
    }
    if set(layers) != set(expected_layers):
        errors.append("layer ids drifted")
    for layer_id, expected in expected_layers.items():
        layer = layers.get(layer_id, {})
        actual = (layer.get("base_theory"), layer.get("status"), layer.get("choice_status"))
        if actual != expected or layer.get("relation") != "SUFFICIENT_OVER_BASE":
            errors.append(f"layer classification drifted: {layer_id}")
    commitments = result.get("first_new_commitments", {})
    if commitments.get("sufficient_foundation_used_here") != "ZF":
        errors.append("countable construction foundation drifted")
    if commitments.get("choice_principle_added") != "NONE":
        errors.append("a choice principle was silently added")
    if commitments.get("weakest_subsystem_status") != "NOT_CLASSIFIED":
        errors.append("weakest subsystem was promoted")
    checks.append("finite PRA and countable ZF sufficiency remain distinct")

    avoidance = result.get("avoidance_classification", {})
    if avoidance.get("relation") != "AVOIDED_BY_REFORMULATION":
        errors.append("avoidance relation drifted")
    if avoidance.get("status") != "PROVED_FOR_DISPLAYED_CARRIERS":
        errors.append("avoidance scope drifted")
    avoided = set(avoidance.get("apparent_dependencies_avoided", []))
    for required in (
        "Axiom of Choice",
        "Countable Choice",
        "Zorn lemma",
        "existential selection of a fundamental decomposition",
        "existential selection of an orthonormal basis",
    ):
        if required not in avoided:
            errors.append(f"missing avoidance control: {required}")
    if not avoidance.get("precise_boundary"):
        errors.append("avoidance result lacks a precise boundary")
    checks.append("explicit-coordinate avoidance relation and boundary")

    checker_errors, summary = check(result)
    errors.extend(f"integer checker: {error}" for error in checker_errors)
    expected_digest = result.get("independent_checker", {}).get("expected_cutoff_digest")
    if summary.get("cutoff_witness_digest") != expected_digest or not SHA256.fullmatch(str(expected_digest)):
        errors.append("cutoff witness digest mismatch")
    if (summary.get("positive_dimensions"), summary.get("negative_dimensions")) != (1540, 2200):
        errors.append("signature regression mismatch")
    if summary.get("two_mode_sym2_signs") != [1, -1, 1]:
        errors.append("Fock sign control mismatch")
    checks.append("independent exact mode and occupation checker")

    permitted = set(result.get("independent_checker", {}).get("permitted_runtime_modules", []))
    actual_imports = imported_modules(CHECKER_PATH)
    if actual_imports != permitted:
        errors.append(f"checker imports {sorted(actual_imports)} but permits {sorted(permitted)}")
    checker_source = CHECKER_PATH.read_text(encoding="utf-8").lower()
    for forbidden in ("import sympy", "import numpy", "float(", "eigen", "linear_solve", "urlopen", "requests"):
        if forbidden in checker_source:
            errors.append(f"checker contains forbidden operation token: {forbidden}")
    checks.append("checker dependency and forbidden-operation guard")

    witness = result.get("mode_witness", {})
    regression = witness.get("regression", {})
    source_regression = one_particle.get("regression", {})
    if source_regression.get("level_dimensions") != regression.get("level_dimensions"):
        errors.append("one-particle level regression disagrees")
    if source_regression.get("positive_dimensions_through_cutoff") != regression.get("positive_dimensions_through_cutoff"):
        errors.append("one-particle positive signature disagrees")
    if source_regression.get("negative_dimensions_through_cutoff") != regression.get("negative_dimensions_through_cutoff"):
        errors.append("one-particle negative signature disagrees")
    if one_particle.get("fundamental_symmetry") != "+1 on E and -1 on A,L in both chiralities":
        errors.append("one-particle source sign formula drifted")
    if not all(one_particle.get(key) is True for key in (
        "fundamental_symmetry_self_adjoint", "positive_index_infinite", "negative_index_infinite"
    )) or one_particle.get("fundamental_symmetry_square") != 1 or one_particle.get("fundamental_symmetry_norm") != 1:
        errors.append("one-particle source properties drifted")
    controls = result.get("fock_construction", {}).get("finite_controls", {})
    if fock.get("sample", {}).get("dimension_Sym2_H2") != controls.get("dimension_sym2_of_energy2"):
        errors.append("Fock dimension control disagrees")
    if fock.get("sample", {}).get("two_mode_Sym2_signature") != controls.get("two_mode_sym2_occupation_signs"):
        errors.append("Fock signature control disagrees")
    if not all(fock.get(key) is True for key in ("fundamental_symmetry_self_adjoint", "normalized_occupation_basis_checked")):
        errors.append("Fock source properties drifted")
    checks.append("foundational witness agrees with both published source certificates")

    for item in result.get("provenance", {}).get("inputs", []):
        path = ROOT / item.get("path", "")
        expected = item.get("sha256")
        if not path.is_file():
            errors.append(f"missing provenance input: {item.get('path')}")
        elif not SHA256.fullmatch(str(expected)) or sha256(path) != expected:
            errors.append(f"provenance hash mismatch: {item.get('path')}")
    checks.append("all local source content hashes")

    source_ledger = SOURCE_LEDGER_PATH.read_text(encoding="utf-8")
    for line in (
        "c52f8b2fcee6573e55e72402008779fd706311b77e2463a774b9eb16ce12b374  analytic_completion/certificates/one_particle_krein.json",
        "6b40128129cfe9469b5c1adcb4b4b1a44c416c37b6e53c8e58f963e99b65a9a3  analytic_completion/certificates/fock_fundamental_symmetry.json",
        "2cba1dd1c3141516d3c1a4ec3c6be71460e4dfe82298c094c748defda9d9579d  symbolic/verify_conformal_energy_mode_krein.py",
    ):
        if line not in source_ledger:
            errors.append(f"source verification ledger missing line: {line}")
    checks.append("pre-existing source verification ledger agrees")

    literature_claim = result.get("literature_dependency", {})
    if sha256(LITERATURE_PATH) != literature_claim.get("local_ledger_sha256"):
        errors.append("literature-ledger content hash mismatch")
    entry = next((item for item in literature.get("entries", []) if item.get("id") == literature_claim.get("source_id")), None)
    if entry is None:
        errors.append("pinned ZF Hilbert source is absent")
    elif entry.get("artifact", {}).get("sha256") != literature_claim.get("pinned_pdf_sha256"):
        errors.append("pinned ZF Hilbert artifact hash mismatch")
    required_theorems = {"Theorem 1.0.2", "Corollary 1.0.3", "Proposition 3.0.4", "Proposition 5.1.3"}
    if not required_theorems <= set(literature_claim.get("theorems_used", [])):
        errors.append("ZF Hilbert derivation omits a required theorem pin")
    checks.append("literature identity, artifact hash, and theorem-level pins")

    dag = result.get("proof_dependency_dag", {})
    node_ids = [node.get("id") for node in dag.get("nodes", [])]
    if not node_ids or len(node_ids) != len(set(node_ids)):
        errors.append("DAG node ids are missing or duplicated")
    if not dag_is_acyclic(set(node_ids), dag.get("edges", [])):
        errors.append("proof dependency graph is cyclic or has dangling edges")
    required_kinds = {"EXPLICIT_PHYSICAL_ENCODING", "PRIMITIVE_RECURSIVE_FORMULA", "ZF_HILBERT_THEOREM", "COORDINATE_OPERATOR", "AVOIDANCE_CONSEQUENCE", "BOUNDARY"}
    if not required_kinds <= {node.get("kind") for node in dag.get("nodes", [])}:
        errors.append("proof DAG omits a required dependency kind")
    checks.append("acyclic proof DAG separates formulas, ZF theorems, and consequences")

    flags = result.get("claim_flags", {})
    for flag in (
        "finite_integral_j_verified",
        "explicit_mode_index_countable_in_zf",
        "zf_one_particle_completion_sufficient",
        "zf_explicit_bosonic_fock_sufficient",
    ):
        if flags.get(flag) is not True:
            errors.append(f"proved flag is not true: {flag}")
    for flag in (
        "choice_or_countable_choice_used_for_displayed_carriers",
        "weakest_base_proved",
        "arbitrary_krein_space_classified",
        "trace_or_state_constructed",
        "physical_probability_constructed",
        "constructive_weyl_qft",
        "lorentzian_claim",
    ):
        if flags.get(flag) is not False:
            errors.append(f"claim flag must fail closed: {flag}")
    if len(result.get("does_not_establish", [])) < 7:
        errors.append("global claim boundary is too small")
    checks.append("positive result and fail-closed boundary flags")

    for token in (
        "FOUNDATIONAL_KREIN_EXPLICIT_J_ZF_V1",
        "SUFFICIENT_OVER_BASE",
        "AVOIDED_BY_REFORMULATION",
        "Primitive Recursive Arithmetic",
        "Countable Choice",
        "Proposition 3.0.4",
        "ell^2(I)",
        "Gamma_s(J)",
        "not the weakest",
        "LORENTZIAN-CAUSAL",
    ):
        if token not in report_text:
            errors.append(f"report missing required token: {token}")
    checks.append("human report mirrors theorem, route, and exclusions")
    return errors, checks


def main() -> int:
    errors, checks = verify()
    if errors:
        print("FOUNDATIONAL_KREIN_EXPLICIT_J_ZF_V1: FAIL")
        for error in errors:
            print(f"  - {error}")
        return 1
    print(f"FOUNDATIONAL_KREIN_EXPLICIT_J_ZF_V1: PASS ({len(checks)}/{len(checks)} checks)")
    for item in checks:
        print(f"  - {item}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
