#!/usr/bin/env python3
"""Build the five-row strict pure-Weyl kinematic/cotangent q2 AST candidate."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_Q2_KINEMATIC_COTANGENT_AST_V1.json"
REPORT = HERE / "REPORT_STRICT_Q2_KINEMATIC_COTANGENT_AST_V1.md"
INPUTS = (
    ("d_quotient_classical/certificates/CLASSICAL_MINIMAL_BV_ANTIFIELD_EXPORT_V2.json", "CLASSICAL_MINIMAL_BV_ANTIFIELD_EXPORT_V2", "exact source Q rows and signs"),
    ("quantum-weyl/classical_import/certificates/CLASSICAL_MINIMAL_BV_ANTIFIELD_IMPORT_V2.json", "CLASSICAL_MINIMAL_BV_ANTIFIELD_IMPORT_V2", "independent replay of the source export"),
    ("field_bv_identification/certificates/minimal_bv_chain.json", "pure-weyl-field-bv-minimal-chain-v1", "displayed strict minimal master action"),
    ("quantum-weyl/classical_import/certificates/STRICT_SUPPORT_LOCAL_Q2_D_READINESS_V1.json", "STRICT_SUPPORT_LOCAL_Q2_D_READINESS_V1", "six-row readiness and hard-kernel separation"),
    ("quantum-weyl/classical_import/certificates/SUPPORT_LOCAL_Q2_EXPORT_CONTRACT.json", "SUPPORT_LOCAL_Q2_EXPORT_CONTRACT", "complete receiver contract kept fail closed"),
)
SYMBOLS = ("h", "c", "omega", "h_star", "c_star", "omega_star")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def load(relative: str) -> dict[str, Any]:
    return json.loads((ROOT / relative).read_text())


def primitive(operator_id: str, output: str, inputs: list[str], jets: list[int], formula: str, source_atoms: list[str], action_term: str, euler_variable: str) -> dict[str, Any]:
    return {
        "operator_id": operator_id,
        "output": output,
        "inputs": inputs,
        "maximum_input_jet_orders": jets,
        "coordinate_formula": formula,
        "source_atoms": source_atoms,
        "variational_origin": {"master_term_id": action_term, "Euler_variable": euler_variable, "BV_coordinate_sign": "fixed by the receiver-replayed source Q row"},
        "support_rule": "output support is contained in the intersection of all input supports",
    }


def component(component_id: str, output: str, inputs: list[str], operator_id: str, coefficient: int = 1) -> dict[str, Any]:
    return {
        "component_id": component_id,
        "output": output,
        "inputs": inputs,
        "coefficient": coefficient,
        "operator_id": operator_id,
    }


def build() -> dict[str, Any]:
    exported = load(INPUTS[0][0])
    imported = load(INPUTS[1][0])
    minimal = load(INPUTS[2][0])
    readiness = load(INPUTS[3][0])
    contract = load(INPUTS[4][0])
    if exported.get("result_id") != INPUTS[0][1] or exported.get("result_state") != "EXPORTED_EXECUTABLE_MINIMAL_BV_FILTRATION":
        raise ValueError("strict antifield source export drift")
    if imported.get("result_id") != INPUTS[1][1] or imported["independent_replay"]["status"] != "EXECUTABLE_V2_EXPORT_INDEPENDENTLY_REPLAYED":
        raise ValueError("strict antifield receiver replay drift")
    if imported["independent_replay"]["canonical_hashes"] != exported["canonical_hashes"]:
        raise ValueError("source and receiver canonical hashes differ")
    if minimal.get("schema") != INPUTS[2][1] or readiness.get("result_id") != INPUTS[3][1]:
        raise ValueError("strict master-action or readiness input drift")
    if contract.get("result_id") != INPUTS[4][1]:
        raise ValueError("complete q2 receiver contract drift")

    rows = {row["source_atom"]: row["image"]["terms"] for row in exported["differential"]["Q"]["rows"]}
    expected = {
        "g": [(2, ("g", "omega")), (1, ("Lie_g",))],
        "xi": [(1, ("bracket_xi",))],
        "omega": [(1, ("Lie_omega",))],
        "xi_star": [(1, ("N_xi",)), (1, ("Lie_xi_star",))],
        "omega_star": [(1, ("N_omega",)), (1, ("Lie_omega_star",))],
    }
    for symbol, terms in expected.items():
        actual = [(term["coefficient"], tuple(term["factors"])) for term in rows[symbol]]
        if actual != terms:
            raise ValueError(f"source Q row drift: {symbol}")

    definitions = [
        primitive("odd_vector_half_bracket", "c^mu", ["c", "c"], [0, 1], "c^rho partial_rho c^mu = (1/2)[c,c]^mu", ["bracket_xi"], "A_DIFF_GHOST", "c_star"),
        primitive("scalar_lie_transport", "omega", ["c", "omega"], [0, 1], "c^rho partial_rho omega", ["Lie_omega"], "A_DIFF_WEYL_GHOST", "omega_star"),
        primitive("metric_lie_transport", "h_mu_nu", ["c", "h"], [1, 1], "c^rho partial_rho h_mu_nu + h_rho_nu partial_mu c^rho + h_mu_rho partial_nu c^rho", ["Lie_g"], "A_DIFF_METRIC", "h_star"),
        primitive("weyl_metric_product", "h_mu_nu", ["omega", "h"], [0, 0], "omega * h_mu_nu", ["g", "omega"], "A_WEYL_METRIC", "h_star"),
        primitive("metric_antifield_diff_noether", "c_star_lambda", ["h", "h_star"], [1, 1], "h_star^mu_nu partial_lambda h_mu_nu - 2 partial_mu(h_star^mu_nu h_lambda_nu)", ["N_xi"], "A_DIFF_METRIC", "c"),
        primitive("covector_density_lie_transport", "c_star_lambda", ["c", "c_star"], [1, 1], "c^rho partial_rho c_star_lambda + c_star_rho partial_lambda c^rho + (partial_rho c^rho)c_star_lambda", ["Lie_xi_star"], "A_DIFF_GHOST", "c"),
        primitive("weyl_antifield_gradient", "c_star_lambda", ["omega", "omega_star"], [1, 0], "omega_star partial_lambda omega", ["N_xi"], "A_DIFF_WEYL_GHOST", "c"),
        primitive("metric_antifield_trace_pair", "omega_star", ["h", "h_star"], [0, 0], "h_mu_nu h_star^mu_nu", ["N_omega"], "A_WEYL_METRIC", "omega"),
        primitive("scalar_density_lie_transport", "omega_star", ["c", "omega_star"], [1, 1], "partial_rho(c^rho omega_star)", ["Lie_omega_star"], "A_DIFF_WEYL_GHOST", "omega"),
    ]
    components = [
        component("q2_c_cc", "c", ["c", "c"], "odd_vector_half_bracket"),
        component("q2_omega_comega", "omega", ["c", "omega"], "scalar_lie_transport"),
        component("q2_h_ch", "h", ["c", "h"], "metric_lie_transport"),
        component("q2_h_omegah", "h", ["omega", "h"], "weyl_metric_product", 2),
        component("q2_cstar_hhstar", "c_star", ["h", "h_star"], "metric_antifield_diff_noether"),
        component("q2_cstar_ccstar", "c_star", ["c", "c_star"], "covector_density_lie_transport"),
        component("q2_cstar_omegaomegastar", "c_star", ["omega", "omega_star"], "weyl_antifield_gradient"),
        component("q2_omegastar_hhstar", "omega_star", ["h", "h_star"], "metric_antifield_trace_pair", 2),
        component("q2_omegastar_comegastar", "omega_star", ["c", "omega_star"], "scalar_density_lie_transport"),
    ]
    row_ledger = [
        {"output": symbol, "status": ("OPEN_HARD_BACH_AND_COTANGENT_ROW" if symbol == "h_star" else "DIAGONAL_POLYNOMIAL_SERIALIZED"), "component_ids": [item["component_id"] for item in components if item["output"] == symbol]}
        for symbol in SYMBOLS
    ]
    proof_gates = [
        {"check_id": "source_sign_and_coefficient_crosswalk", "status": "RECEIVER_REPLAYED", "scope": "five source Q rows in the executable antifield export"},
        {"check_id": "operator_inventory_and_tensor_types", "status": "RECEIVER_REPLAYED", "scope": "nine declared tensor-natural primitives"},
        {"check_id": "exact_coefficients_and_jet_bounds", "status": "RECEIVER_REPLAYED", "scope": "nine serialized components, maximum total input jet order two"},
        {"check_id": "five_row_diagonal_completeness", "status": "RECEIVER_REPLAYED", "scope": "c, omega, h, c_star and omega_star only"},
        {"check_id": "q2_koszul_symmetry", "status": "NOT_REPLAYED", "scope": "suspended polarization and odd diagonal convention remain to be implemented"},
        {"check_id": "q1_q2_arity_two_nilpotency", "status": "NOT_REPLAYED", "scope": "requires the polarized six-row q2 including the Bach row"},
        {"check_id": "D_q2_derivation", "status": "NOT_REPLAYED", "scope": "full local D is not serialized"},
        {"check_id": "BV_cyclicity_q2", "status": "NOT_REPLAYED", "scope": "requires polarized components and the common support-local pairing"},
    ]
    value: dict[str, Any] = {
        "schema": "strict-q2-kinematic-cotangent-ast-v1",
        "result_id": "STRICT_Q2_KINEMATIC_COTANGENT_AST_V1",
        "result_kind": "PARTIAL_DIAGONAL_TAYLOR_COMPONENT_EXPORT",
        "result_state": "FIVE_OF_SIX_MINIMAL_ROWS_SERIALIZED_POLARIZATION_OPEN",
        "lifecycle": "CLASSIFIED",
        "created": "2026-08-15",
        "repository_base_commit": "88dcdd26fc53b46db7ebe0300fe54e19e8365858",
        "classical_commit": exported["classical_commit"],
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "scope": {
            "theory": "strict pure-Weyl minimal Diff x Weyl BV theory",
            "background": "g=gbar and ghosts/antifields zero; formulas are local coordinate representatives about any smooth background chart",
            "carrier": "compactly supported smooth minimal BV sections, with one compact and one smooth input allowed",
            "support_rule": "supp P(u,v) subset supp(u) intersection supp(v) for two compact inputs",
            "coefficient_field": "Q",
            "maximum_serialized_input_jet_order": 1,
            "maximum_serialized_total_jet_order": 2,
            "expression_schema_version": "strict-pure-weyl-tensor-natural-diagonal-v1",
            "taylor_boundary": "serialized expressions are the quadratic diagonal polynomial in Q(epsilon Phi); the suspended graded bilinear polarization is not yet claimed",
        },
        "generator_ledger": [
            {"symbol": "h", "role": "metric", "local_tangent_degree": 0, "BV_ghost_number": 0, "Grassmann_parity": 0},
            {"symbol": "c", "role": "diffeomorphism_ghost", "local_tangent_degree": -1, "BV_ghost_number": 1, "Grassmann_parity": 1},
            {"symbol": "omega", "role": "weyl_ghost", "local_tangent_degree": -1, "BV_ghost_number": 1, "Grassmann_parity": 1},
            {"symbol": "h_star", "role": "metric_antifield", "local_tangent_degree": 1, "BV_ghost_number": -1, "Grassmann_parity": 1},
            {"symbol": "c_star", "role": "diffeomorphism_ghost_antifield", "local_tangent_degree": 2, "BV_ghost_number": -2, "Grassmann_parity": 0},
            {"symbol": "omega_star", "role": "weyl_ghost_antifield", "local_tangent_degree": 2, "BV_ghost_number": -2, "Grassmann_parity": 0},
        ],
        "source_crosswalk": {
            "source_Q_rows": expected,
            "source_canonical_hashes": exported["canonical_hashes"],
            "receiver_canonical_hashes": imported["independent_replay"]["canonical_hashes"],
            "master_action": minimal["master_action"]["minimal_master_action"],
            "master_term_dictionary": {
                "A_DIFF_METRIC": "h_star^mu_nu (c^rho partial_rho h_mu_nu + h_rho_nu partial_mu c^rho + h_mu_rho partial_nu c^rho)",
                "A_WEYL_METRIC": "2 h_star^mu_nu omega h_mu_nu",
                "A_DIFF_GHOST": "c_star_mu c^rho partial_rho c^mu",
                "A_DIFF_WEYL_GHOST": "omega_star c^rho partial_rho omega"
            },
        },
        "operator_definitions": definitions,
        "components": components,
        "row_ledger": row_ledger,
        "proof_gates": proof_gates,
        "next_hard_kernel": {
            "output": "h_star",
            "required_terms": ["polarized second Bach variation D^2 Bach[h,h]", "metric-antifield Diff cotangent action", "metric-antifield Weyl cotangent action"],
            "maximum_metric_jet_order": 4,
            "status": "OPEN_NOT_SERIALIZED",
        },
        "canonical_hashes": {},
        "provenance": {"inputs": [{"path": path, "result_or_artifact_id": result_id, "sha256": sha(ROOT / path), "role": role} for path, result_id, role in INPUTS]},
        "claim_flags": {
            "FIVE_DIAGONAL_Q2_ROWS_PORTABLE": True,
            "SIXTH_METRIC_ANTIFIELD_ROW_PORTABLE": False,
            "SUSPENDED_GRADED_POLARIZATION_REPLAYED": False,
            "STRICT_SUPPORT_LOCAL_Q2_COMPLETE": False,
            "STRICT_FULL_LOCAL_D_ACTION_CERTIFIED": False,
            "CLASSICAL_IMPORT_GATE_PASSED": False,
            "QME_RESTORED": False,
            "LORENTZIAN_QUANTUM_THEORY": False,
        },
        "does_not_establish": [
            "a complete six-row support-local q2", "the polarized second Bach variation",
            "Koszul symmetry under the repository suspension convention", "the arity-two master identity",
            "a full local D action or its derivation identity", "BV cyclicity on a common local pairing",
            "Gate A, a causal Green homotopy, a Hadamard state, QME restoration or a Lorentzian quantum theory",
        ],
        "independent_checker": "quantum-weyl/classical_import/check_strict_q2_kinematic_cotangent_ast.py",
        "human_report": "quantum-weyl/classical_import/REPORT_STRICT_Q2_KINEMATIC_COTANGENT_AST_V1.md",
    }
    value["canonical_hashes"] = {
        "generator_ledger_sha256": digest(value["generator_ledger"]),
        "operator_definitions_sha256": digest(definitions),
        "components_sha256": digest(components),
        "row_ledger_sha256": digest(row_ledger),
        "proof_gates_sha256": digest(proof_gates),
        "source_crosswalk_sha256": digest(value["source_crosswalk"]),
    }
    return value


def render(value: dict[str, Any]) -> str:
    rows = "\n".join(f"| `{row['output']}` | `{row['status']}` | {len(row['component_ids'])} |" for row in value["row_ledger"])
    primitives = "\n".join(f"| `{item['operator_id']}` | `{', '.join(item['inputs'])}` | `{item['output']}` | {item['coordinate_formula']} |" for item in value["operator_definitions"])
    gates = "\n".join(f"| `{item['check_id']}` | `{item['status']}` | {item['scope']} |" for item in value["proof_gates"])
    return f"""# Strict q2 kinematic/cotangent AST v1

**Result:** `{value['result_id']}`

**State:** `{value['result_state']}`

**Dependency:** `LOCAL-ALGEBRAIC`

## Outcome

The exact, receiver-replayed minimal-BV `Q` export fixes the signs and rational
coefficients of five non-Bach quadratic rows. This result turns those rows into
a portable tensor-natural diagonal Taylor polynomial with nine named local
operators and explicit coordinate formulas. The sixth, metric-antifield row is
kept open because it contains the polarized second Bach variation through
fourth metric-jet order.

This is intentionally not presented as a complete `q2`. The expressions are
the quadratic diagonal polynomial in `Q(epsilon Phi)`. The repository's
suspended graded polarization—especially the odd ghost diagonal—must be
implemented and replayed before Koszul symmetry or any arity-two identity can
be claimed.

## Row coverage

| Output | Status | Components |
|---|---|---:|
{rows}

## Portable operator dictionary

| Operator | Inputs | Output | Coordinate representative |
|---|---|---|---|
{primitives}

All coefficients are integers, all serialized operators have input jet order
at most one, and every binary term obeys the support-intersection rule.

## Receiver checks and open gates

| Check | Status | Scope or boundary |
|---|---|---|
{gates}

## Next construction

Derive the `h_star` row as two separately auditable pieces: the polarized
`D^2 Bach[h,h]` kernel through metric-jet order four, and the Diff/Weyl
cotangent terms. Then implement the suspended polarization and replay all seven
checks required by `SUPPORT_LOCAL_Q2_EXPORT_CONTRACT` on the six-row payload.

## Reproduction

```text
python3 quantum-weyl/classical_import/build_strict_q2_kinematic_cotangent_ast.py --check
python3 quantum-weyl/classical_import/check_strict_q2_kinematic_cotangent_ast.py
python3 quantum-weyl/classical_import/verify_strict_q2_kinematic_cotangent_ast.py
python3 -m unittest quantum-weyl/classical_import/tests/test_strict_q2_kinematic_cotangent_ast.py
```

## Does not establish

""" + "\n".join(f"- {item}." for item in value["does_not_establish"]) + "\n"


def generated() -> tuple[bytes, bytes]:
    value = build()
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode(), render(value).encode()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs = tuple(zip((RESULT, REPORT), generated()))
    stale = [str(path.relative_to(ROOT)) for path, content in outputs if not path.is_file() or path.read_bytes() != content]
    if args.check:
        print("STRICT_Q2_KINEMATIC_COTANGENT_AST_V1: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    for path, content in outputs:
        path.write_bytes(content)
    print("STRICT_Q2_KINEMATIC_COTANGENT_AST_V1: wrote certificate and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
