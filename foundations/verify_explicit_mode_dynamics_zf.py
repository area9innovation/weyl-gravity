#!/usr/bin/env python3
"""Verifier for explicit reduced-mode Krein and C*-dynamics in ZF."""
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

from foundations.check_explicit_mode_dynamics import check

RESULT = ROOT / "foundations/results/FOUNDATIONAL_EXPLICIT_MODE_DYNAMICS_ZF_V1.json"
SCHEMA = ROOT / "foundations/schema/foundational-explicit-mode-dynamics-zf-v1.schema.json"
REPORT = ROOT / "foundations/reports/explicit-mode-dynamics-zf.md"
CHECKER = ROOT / "foundations/check_explicit_mode_dynamics.py"
ENERGY = ROOT / "foundations/results/FOUNDATIONAL_EXPLICIT_ENERGY_SPECTRAL_FRAGMENT_ZF_V1.json"
KREIN = ROOT / "foundations/results/FOUNDATIONAL_KREIN_EXPLICIT_J_ZF_V1.json"
CUBE = ROOT / "foundations/results/FOUNDATIONAL_INTERSECTION_CUBE_V0.json"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(), filename=str(path))
    found = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and node.module != "__future__":
            found.add(node.module.split(".")[0])
    return found


def acyclic(dag: dict[str, Any]) -> bool:
    nodes = [item.get("id") for item in dag.get("nodes", [])]
    if not nodes or len(nodes) != len(set(nodes)):
        return False
    outgoing = {node: [] for node in nodes}
    indegree = {node: 0 for node in nodes}
    for edge in dag.get("edges", []):
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


def verify(
    *,
    result: dict[str, Any] | None = None,
    report: str | None = None,
    energy: dict[str, Any] | None = None,
    krein: dict[str, Any] | None = None,
    cube: dict[str, Any] | None = None,
) -> tuple[list[str], list[str]]:
    result = load(RESULT) if result is None else result
    report = REPORT.read_text() if report is None else report
    energy = load(ENERGY) if energy is None else energy
    krein = load(KREIN) if krein is None else krein
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
        result.get("result_id") != "FOUNDATIONAL_EXPLICIT_MODE_DYNAMICS_ZF_V1"
        or result.get("lifecycle") != "SUFFICIENCY_PROVED"
        or result.get("dependency_tags") != ["LOCAL-ALGEBRAIC", "REDUCED-MODE"]
    ):
        errors.append("identity/lifecycle/dependency tags")
    checks.append("identity and reduced-mode boundary")

    for pin in result.get("provenance", {}).get("inputs", []):
        path = ROOT / pin.get("path", "")
        if not path.is_file() or sha256(path) != pin.get("sha256"):
            errors.append("provenance " + str(pin.get("path")))
    if energy.get("result_id") != "FOUNDATIONAL_EXPLICIT_ENERGY_SPECTRAL_FRAGMENT_ZF_V1":
        errors.append("energy source identity")
    if not energy.get("claim_flags", {}).get("explicit_energy_self_adjointness_route_classified"):
        errors.append("energy source not established")
    coordinate = energy.get("coordinate_proof", {})
    if coordinate.get("operator") is not None:
        errors.append("unexpected energy operator field")
    if "energy(i)" not in coordinate.get("functional_calculus_formula", ""):
        errors.append("coordinate functional calculus source")
    if krein.get("result_id") != "FOUNDATIONAL_KREIN_EXPLICIT_J_ZF_V1" or not krein.get("claim_flags", {}).get("zf_one_particle_completion_sufficient"):
        errors.append("Krein source identity/sufficiency")
    checks.append("content-pinned energy and Krein carrier sources")

    group = result.get("coordinate_unitary_group", {})
    if group.get("foundation") != "ZF" or group.get("choice_status") != "NO_CHOICE_OPERATION":
        errors.append("unitary-group foundation")
    for token in ("exp(-it energy(i))", "U_t U_s=U_(t+s)", "U_t^dagger_0 J U_t=J", "-iD"):
        if token not in " ".join(str(value) for value in group.values()):
            errors.append("unitary-group token " + token)
    continuity = " ".join(group.get("strong_continuity_proof", []))
    for token in ("finite energy-coordinate head", "tail norm", "finitely many"):
        if token not in continuity:
            errors.append("strong continuity token " + token)
    checks.append("coordinate group, J-unitarity, domain, and strong continuity")

    algebra = result.get("cstar_dynamics", {})
    if algebra.get("foundation") != "ZF" or algebra.get("choice_status") != "NO_CHOICE_OPERATION":
        errors.append("C*-dynamics foundation")
    for token in ("alpha_t(A)=U_t A U_t^dagger_0", "energy(i)-energy(j)", "2epsilon", "-i[D,E_ij]"):
        if token not in " ".join(str(value) for value in algebra.values()):
            errors.append("C*-dynamics token " + token)
    checks.append("automorphism, point-norm continuity, and finite-core derivation")
    foundation = result.get("continuity_and_foundations", {})
    if foundation.get("sufficient_base") != "ZF with the already imported real/complex scalar and l2 completion" or foundation.get("choice_principle_added") != "NONE" or foundation.get("weakest_base_status") != "NOT_CLASSIFIED":
        errors.append("continuity foundation/choice boundary")
    checks.append("ZF sufficiency without weakest-base promotion")

    checker_errors, summary = check(result)
    errors.extend("checker " + item for item in checker_errors)
    if summary.get("matrix_units") != 324 or summary.get("matrix_unit_composition_checks") != 5832 or summary.get("nontrivial_degree_matrix_units") != 274:
        errors.append("exact checker summary")
    if imports(CHECKER) != {"hashlib", "json", "pathlib", "typing"}:
        errors.append("checker import boundary")
    lowered = CHECKER.read_text().lower()
    for forbidden in ("numpy", "sympy", "cmath", "float(", "random", "urlopen", "requests"):
        if forbidden in lowered:
            errors.append("checker forbidden token " + forbidden)
    checks.append("independent exact Laurent-degree rail")

    if not acyclic(result.get("proof_dependency_dag", {})):
        errors.append("proof DAG")
    cube_cells = {
        (item.get("foundation"), item.get("carrier"), item.get("obligation")): item
        for item in cube.get("cells", [])
    }
    for promotion in result.get("cube_promotions", []):
        coordinate_key = tuple(promotion.get(key) for key in ("foundation", "carrier", "obligation"))
        cell = cube_cells.get(coordinate_key, {})
        if cell.get("status") != "LOCAL_RESULT" or result.get("result_id") not in cell.get("evidence", []):
            errors.append("cube promotion not applied " + "/".join(str(value) for value in coordinate_key))
    checks.append("acyclic proof DAG and four applied cube promotions")

    flags = result.get("claim_flags", {})
    for key in (
        "explicit_strongly_continuous_unitary_group_constructed",
        "explicit_j_unitary_group_constructed",
        "explicit_point_norm_cstar_dynamics_constructed",
        "explicit_fock_unitary_group_constructed",
    ):
        if flags.get(key) is not True:
            errors.append("positive flag " + key)
    for key in (
        "choice_or_countable_choice_used",
        "weakest_base_proved",
        "nonlinear_bt_dynamics_constructed",
        "interacting_dynamics_constructed",
        "causal_propagation_constructed",
        "physical_state_selected",
        "lorentzian_claim",
    ):
        if flags.get(key) is not False:
            errors.append("boundary flag " + key)
    checks.append("free-dynamics and fail-closed physical boundaries")

    for token in (
        "FOUNDATIONAL_EXPLICIT_MODE_DYNAMICS_ZF_V1",
        "strongly continuous Hilbert-unitary and `J`-unitary group",
        "point-norm continuous one-parameter group",
        "5,832 product-degree identities",
        "Stone's theorem is not being invoked",
        "Four cube cells filled",
        "Not mapped",
        "Priority gap",
        "Local result",
        "LORENTZIAN-CAUSAL",
    ):
        if token not in report:
            errors.append("report token " + token)
    checks.append("human report theorem, promotions, and boundaries")
    return errors, checks


def main() -> int:
    errors, checks = verify()
    print("FOUNDATIONAL_EXPLICIT_MODE_DYNAMICS_ZF_V1: " + ("PASS" if not errors else "FAIL"))
    for item in checks if not errors else errors:
        print("  - " + item)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
