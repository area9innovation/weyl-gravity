#!/usr/bin/env python3
"""Verifier for the explicit Krein state/selection separation in ZF."""
from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from foundations.check_krein_state_selection import check

RESULT = ROOT / "foundations/results/FOUNDATIONAL_KREIN_STATE_SELECTION_ZF_V1.json"
SCHEMA = ROOT / "foundations/schema/foundational-krein-state-selection-zf-v1.schema.json"
REPORT = ROOT / "foundations/reports/krein-state-selection-zf.md"
CHECKER = ROOT / "foundations/check_krein_state_selection.py"
KREIN_SOURCE = ROOT / "foundations/results/FOUNDATIONAL_KREIN_EXPLICIT_J_ZF_V1.json"
CSTAR_SOURCE = ROOT / "foundations/results/FOUNDATIONAL_BT_SEPARABLE_STATE_CHAIN_ZF_V1.json"
FOCK_SOURCE = ROOT / "analytic_completion/certificates/fock_fundamental_symmetry.json"
CUBE = ROOT / "foundations/results/FOUNDATIONAL_INTERSECTION_CUBE_V0.json"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def acyclic(dag: dict[str, Any]) -> bool:
    nodes = [node.get("id") for node in dag.get("nodes", [])]
    if not nodes or len(nodes) != len(set(nodes)):
        return False
    edges = dag.get("edges", [])
    outgoing = {node: [] for node in nodes}
    indegree = {node: 0 for node in nodes}
    for edge in edges:
        source, target = edge.get("from"), edge.get("to")
        if source not in outgoing or target not in outgoing:
            return False
        outgoing[source].append(target)
        indegree[target] += 1
    ready = [node for node in nodes if indegree[node] == 0]
    seen = 0
    while ready:
        node = ready.pop()
        seen += 1
        for target in outgoing[node]:
            indegree[target] -= 1
            if indegree[target] == 0:
                ready.append(target)
    return seen == len(nodes)


def imported_modules(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(), filename=str(path))
    modules = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and node.module != "__future__":
            modules.add(node.module.split(".")[0])
    return modules


def verify(
    *,
    result: dict[str, Any] | None = None,
    report: str | None = None,
    krein_source: dict[str, Any] | None = None,
    cstar_source: dict[str, Any] | None = None,
    fock_source: dict[str, Any] | None = None,
    cube: dict[str, Any] | None = None,
) -> tuple[list[str], list[str]]:
    result = load(RESULT) if result is None else result
    report = REPORT.read_text() if report is None else report
    krein_source = load(KREIN_SOURCE) if krein_source is None else krein_source
    cstar_source = load(CSTAR_SOURCE) if cstar_source is None else cstar_source
    fock_source = load(FOCK_SOURCE) if fock_source is None else fock_source
    cube = load(CUBE) if cube is None else cube
    errors: list[str] = []
    checks: list[str] = []

    schema = load(SCHEMA)
    try:
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(result)
    except Exception as exc:
        errors.append("schema " + str(exc).splitlines()[0])
    checks.append("Draft 2020-12 schema")

    if (
        result.get("result_id") != "FOUNDATIONAL_KREIN_STATE_SELECTION_ZF_V1"
        or result.get("result_kind") != "FOUNDATIONAL_DEPENDENCY_CERTIFICATE"
        or result.get("lifecycle") != "SUFFICIENCY_PROVED"
        or result.get("dependency_tags") != ["LOCAL-ALGEBRAIC", "REDUCED-MODE"]
    ):
        errors.append("identity/lifecycle/dependency tags")
    checks.append("identity and reduced-mode boundary")

    source_by_path = {
        str(KREIN_SOURCE.relative_to(ROOT)): krein_source,
        str(CSTAR_SOURCE.relative_to(ROOT)): cstar_source,
        str(FOCK_SOURCE.relative_to(ROOT)): fock_source,
    }
    for pin in result.get("provenance", {}).get("inputs", []):
        path = ROOT / pin.get("path", "")
        if not path.is_file() or sha256(path) != pin.get("sha256") or pin.get("path") not in source_by_path:
            errors.append("provenance " + str(pin.get("path")))
    if krein_source.get("result_id") != "FOUNDATIONAL_KREIN_EXPLICIT_J_ZF_V1":
        errors.append("Krein source identity")
    krein_flags = krein_source.get("claim_flags", {})
    if not krein_flags.get("zf_one_particle_completion_sufficient") or not krein_flags.get("zf_explicit_bosonic_fock_sufficient"):
        errors.append("Krein carrier source not sufficient")
    if cstar_source.get("result_id") != "FOUNDATIONAL_BT_SEPARABLE_STATE_CHAIN_ZF_V1":
        errors.append("C*-state source identity")
    cstar_flags = cstar_source.get("claim_flags", {})
    if not cstar_flags.get("explicit_zf_states_constructed") or not cstar_flags.get("explicit_corner_gns_constructed"):
        errors.append("C*-state/GNS source not established")
    if fock_source.get("fundamental_symmetry_square") != 1 or not fock_source.get("fundamental_symmetry_self_adjoint"):
        errors.append("Fock source symmetry")
    checks.append("content-pinned carrier, Fock, and C*-state sources")

    typed = result.get("typed_products", {})
    if typed.get("operator_involution_used_for_state_positivity") != "Hilbert adjoint dagger_0":
        errors.append("state positivity adjoint")
    if typed.get("krein_adjoint") != "A^sharp=J A^dagger_0 J":
        errors.append("Krein adjoint typing")
    construction = result.get("state_construction", {})
    if construction.get("foundation") != "ZF" or construction.get("choice_status") != "NO_CHOICE_OPERATION":
        errors.append("foundation/choice classification")
    for token in ("sigma[v,Av]", "||Av||_0^2", "trace one"):
        if token not in " ".join(str(construction.get(key, "")) for key in construction):
            errors.append("state construction token " + token)
    checks.append("typed state formula, normalization, and positivity")

    checker_errors, summary = check(result)
    errors.extend("checker " + item for item in checker_errors)
    if summary.get("integer_matrices_checked") != 625 or summary.get("states_distinguished_by_positive_projection") != [1, 0]:
        errors.append("exact checker summary")
    if result.get("finite_exact_witness", {}).get("state_formulas") != {
        "omega_p": "omega_p(A)=[p,Ap]=A_11",
        "omega_n": "omega_n(A)=-[n,An]=A_22",
    }:
        errors.append("finite state formulas")
    if imported_modules(CHECKER) != {"fractions", "hashlib", "itertools", "json", "pathlib", "typing"}:
        errors.append("checker import boundary")
    lowered = CHECKER.read_text().lower()
    for forbidden in ("numpy", "sympy", "float(", "random", "urlopen", "requests"):
        if forbidden in lowered:
            errors.append("checker forbidden token " + forbidden)
    checks.append("independent 625-matrix exact rail and dependency guard")

    obstruction = result.get("selection_obstruction", {})
    if obstruction.get("relation") != "NOT_IMPLIED_BY_CARRIER":
        errors.append("selection relation")
    proof_text = " ".join(obstruction.get("proof", []))
    for token in ("c_+", "c_-", "every natural N", "tr(rho)=0", "tr(rho)=1"):
        if token not in proof_text:
            errors.append("selection proof token " + token)
    if "singular non-density-operator states" not in obstruction.get("does_not_rule_out", []):
        errors.append("singular-state boundary")
    checks.append("density-state symmetry obstruction and singular-state boundary")

    if not acyclic(result.get("proof_dependency_dag", {})):
        errors.append("proof DAG")
    promotions = result.get("cube_promotions", [])
    if len(promotions) != 3 or any(item.get("new_status") != "LOCAL_RESULT" for item in promotions):
        errors.append("cube promotions")
    cube_cells = {
        (item.get("foundation"), item.get("carrier"), item.get("obligation")): item
        for item in cube.get("cells", [])
    }
    for promotion in promotions:
        coordinate = tuple(promotion.get(key) for key in ("foundation", "carrier", "obligation"))
        cell = cube_cells.get(coordinate, {})
        if cell.get("status") != promotion.get("new_status") or result.get("result_id") not in cell.get("evidence", []):
            errors.append("cube promotion not applied " + "/".join(str(item) for item in coordinate))
    checks.append("acyclic dependency DAG and applied promotion manifest")

    flags = result.get("claim_flags", {})
    for key in (
        "explicit_zf_krein_vector_states_constructed",
        "explicit_rank_one_density_witnesses_constructed",
        "explicit_fock_coordinate_states_constructed",
    ):
        if flags.get(key) is not True:
            errors.append("positive flag " + key)
    for key in (
        "state_existence_requires_choice_here",
        "j_alone_selects_unique_state",
        "sign_permutation_invariant_density_state_exists",
        "singular_state_nonexistence_proved",
        "physical_weyl_state_selected",
        "generalized_born_rule_derived",
        "interacting_state_constructed",
        "lorentzian_claim",
    ):
        if flags.get(key) is not False:
            errors.append("boundary flag " + key)
    if len(result.get("does_not_establish", [])) < 9:
        errors.append("claim boundary size")
    checks.append("state-existence versus physical-selection flags")

    for token in (
        "FOUNDATIONAL_KREIN_STATE_SELECTION_ZF_V1",
        "sigma [v, A v] = (v, A v)_0",
        "625 two-by-two integer matrices",
        "Why J alone does not select a density state",
        "singular invariant states",
        "Three cube cells closed",
        "Pieces only",
        "Priority gap",
        "Local result",
        "LORENTZIAN-CAUSAL",
    ):
        if token not in report:
            errors.append("report token " + token)
    checks.append("human-readable theorem, promotions, and boundaries")
    return errors, checks


def main() -> int:
    errors, checks = verify()
    print("FOUNDATIONAL_KREIN_STATE_SELECTION_ZF_V1: " + ("PASS" if not errors else "FAIL"))
    for item in checks if not errors else errors:
        print("  - " + item)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
