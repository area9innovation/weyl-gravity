#!/usr/bin/env python3
"""Independent checks for the typed field-equation Green quotient inverse."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_386_FIELD_EQUATION_GREEN_QUOTIENT_INVERSE_V1.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def recorded_digest(value: dict[str, Any]) -> str:
    return digest({key: item for key, item in value.items() if key != "sha256"})


def independent_census() -> tuple[dict[str, int], dict[tuple[int, int], int], int]:
    basis = json.loads((HERE / "certificates/STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1.json").read_text())
    graph = json.loads((HERE / "certificates/STRICT_386_GRAPH_Q1_SDR_COMPONENT_JETS_V1.json").read_text())
    degrees = {row["index"]: row["degree"] for row in basis["component_basis"]["rows"]}
    degree_counts = {str(key): value for key, value in sorted(Counter(degrees.values()).items())}
    edges: Counter[tuple[int, int]] = Counter()
    defects = 0
    for table in graph["graph_q1_serialization"]["tables"]:
        for coefficient in table["coefficients"]:
            for target, source, *_ in coefficient["entries"]:
                pair = (degrees[source], degrees[target])
                edges[pair] += 1
                defects += pair[1] != pair[0] + 1
    return degree_counts, dict(edges), defects


def check(value: dict[str, Any] | None = None) -> list[str]:
    errors: list[str] = []
    if value is None:
        value = json.loads(RESULT.read_text())
    if value.get("result_id") != "STRICT_386_FIELD_EQUATION_GREEN_QUOTIENT_INVERSE_V1":
        return ["result identity drift"]

    for item in value.get("provenance", {}).get("inputs", []):
        path = ROOT / item["path"]
        if not path.is_file() or sha(path) != item["sha256"]:
            errors.append(f"dependency hash drift: {item['path']}")

    literature = value.get("literature_context", {})
    if literature.get("artifact", {}).get("sha256") != "8f43ffd1d381743001914e56facbc11afa38d24a0476cd05ab38e90435d2cecc":
        errors.append("Green-hyperbolic-complex literature pin drift")
    if "delta Lambda=id" not in literature.get("imported_statement", "") or "degeneracy" not in literature.get("imported_statement", ""):
        errors.append("literature type boundary drift")

    degree_counts, edges, defects = independent_census()
    typed = value.get("typed_complex", {})
    if typed.get("degree_counts") != degree_counts or defects or typed.get("q1_degree_step_defects") != 0:
        errors.append("graded carrier census drift")
    expected = {(-1, 0): 425, (0, 1): 3264, (1, 2): 425}
    for pair, count in expected.items():
        if edges.get(pair) != count:
            errors.append(f"q1 edge census drift: {pair}")
    if typed.get("gauge_map", {}).get("nonzero_rational_jet_coefficients") != 425:
        errors.append("gauge-map type/count drift")
    if typed.get("field_equation_operator", {}).get("nonzero_rational_jet_coefficients") != 3264:
        errors.append("field-equation type/count drift")
    if typed.get("noether_map", {}).get("nonzero_rational_jet_coefficients") != 425:
        errors.append("Noether-map type/count drift")
    if typed.get("exact_complex_identities") != ["K R=0", "N K=0"]:
        errors.append("complex identities drift")

    component = value.get("green_field_equation_component", {})
    if component.get("definition") != "G_sigma=pr_C0 Lambda_graph,sigma inc_C1":
        errors.append("Green component type drift")
    if component.get("component_bytes_flattened") is not False:
        errors.append("nonlocal component-byte overclaim")
    if set(component.get("orientations", {})) != {"plus", "minus"}:
        errors.append("causal orientations drift")

    identities = value.get("restricted_homotopy_identities", {})
    if identities.get("source_identity") != "K G_sigma + A_sigma N = identity_C1":
        errors.append("source identity drift")
    if identities.get("field_identity") != "G_sigma K + R C_sigma = identity_C0":
        errors.append("field identity drift")
    if identities.get("structural_defects") != 0 or identities.get("orientations_checked") != 2:
        errors.append("restricted identity replay drift")

    no_go = value.get("full_inverse_obstruction", {})
    if no_go.get("full_left_inverse_of_K_on_C0") is not False or no_go.get("full_right_inverse_of_K_on_C1") is not False:
        errors.append("full inverse over-promotion")
    if no_go.get("nonzero_gauge_coefficients") != edges.get((-1, 0)) or no_go.get("nonzero_noether_coefficients") != edges.get((1, 2)):
        errors.append("no-go nonzero witness drift")
    if "R=L K R=0" not in no_go.get("left_inverse_contradiction", "") or "N=N K J=0" not in no_go.get("right_inverse_contradiction", ""):
        errors.append("no-go derivation drift")

    nonlinear = value.get("nonlinear_consequence", {})
    if nonlinear.get("first_order_status") != "TYPED_AND_CERTIFIED_FOR_THE_CANDIDATE":
        errors.append("first-order type disposition drift")
    if nonlinear.get("lambda_squared_source_cocycle_certified") is not False:
        errors.append("lambda-squared closure over-promotion")
    if nonlinear.get("full_ungauge_fixed_two_sided_inverse_required") is not False:
        errors.append("incorrect nonlinear inverse requirement")
    if "N S_m=0" not in nonlinear.get("all_order_criterion", ""):
        errors.append("all-order source gate drift")

    foundations = value.get("foundational_strength", {})
    if foundations.get("choice_operation_added") is not False or foundations.get("quotient_requires_representative_selection") is not False:
        errors.append("choice/quotient foundation drift")
    if foundations.get("weakest_complete_foundational_base") != "NOT_ESTABLISHED":
        errors.append("weakest-base over-promotion")

    flags = value.get("claim_flags", {})
    required_true = (
        "STRICT_386_FIELD_EQUATION_GREEN_COMPONENT_TYPED",
        "STRICT_386_FIELD_EQUATION_CONSTRAINED_RIGHT_INVERSE_CERTIFIED",
        "STRICT_386_FIELD_EQUATION_QUOTIENT_LEFT_INVERSE_CERTIFIED",
        "STRICT_386_UNGAUGE_FIXED_TWO_SIDED_GREEN_INVERSE_OBSTRUCTED",
        "STRICT_386_CANDIDATE_FIRST_ORDER_YANG_FELDMAN_SOURCE_TYPED",
    )
    required_false = (
        "STRICT_386_UNGAUGE_FIXED_TWO_SIDED_GREEN_INVERSE_CONSTRUCTED",
        "STRICT_386_ALL_ORDER_NONLINEAR_SOURCE_CLOSURE_CERTIFIED",
        "STRICT_386_AUTHORITATIVE_FORMAL_MOLLER_MAP_CERTIFIED",
        "CLASSICAL_IMPORT_GATE_PASSED",
        "HADAMARD_STATE_CONSTRUCTED",
        "RENORMALIZED_LORENTZIAN_PRODUCTS",
        "QME_RESTORED",
        "RESIDUAL_TRANSFERRED",
        "LORENTZIAN_QUANTUM_THEORY",
    )
    for key in required_true:
        if flags.get(key) is not True:
            errors.append(f"required true flag missing: {key}")
    for key in required_false:
        if flags.get(key) is not False:
            errors.append(f"required false firewall missing: {key}")

    fields = {
        "literature_context_sha256": "literature_context",
        "typed_complex_sha256": "typed_complex",
        "green_component_sha256": "green_field_equation_component",
        "restricted_identities_sha256": "restricted_homotopy_identities",
        "full_inverse_obstruction_sha256": "full_inverse_obstruction",
        "nonlinear_consequence_sha256": "nonlinear_consequence",
        "foundational_strength_sha256": "foundational_strength",
        "authority_boundary_sha256": "authority_boundary",
        "typed_inverse_snapshot_sha256": "typed_inverse_snapshot",
    }
    hashes = value.get("canonical_hashes", {})
    for key, field in fields.items():
        if hashes.get(key) != recorded_digest(value.get(field, {})):
            errors.append(f"canonical hash drift: {key}")
    return errors


def main() -> int:
    errors = check()
    print("STRICT_386_FIELD_EQUATION_GREEN_QUOTIENT_INVERSE_V1: " + ("PASS" if not errors else "FAIL"))
    for error in errors:
        print(f"  - {error}")
    if not errors:
        print("  - 116-to-116 field/equation component and both causal orientations typed")
        print("  - constrained right inverse and quotient left inverse replay exactly")
        print("  - full ungauge-fixed inverse rejected; nonlinear source closure remains open")
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
