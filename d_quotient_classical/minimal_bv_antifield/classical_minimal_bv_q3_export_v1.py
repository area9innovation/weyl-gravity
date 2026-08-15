#!/usr/bin/env python3
"""Export the action-derived arity-three Taylor component of minimal Weyl BV.

The authoritative minimal master action has exactly one source of cubic and
higher Taylor coefficients in its Hamiltonian vector field: the pure metric
Euler row.  The gauge, ghost and cotangent terms are at most quadratic after
taking the BV Hamiltonian derivative.  This exporter records that fact as a
typed, support-local natural-operator AST on the same six-generator carrier
as ``CLASSICAL_MINIMAL_BV_ANTIFIELD_EXPORT_V2``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "d_quotient_classical/minimal_bv_antifield"
PARENT = ROOT / "d_quotient_classical/certificates/CLASSICAL_MINIMAL_BV_ANTIFIELD_EXPORT_V2.json"
ACTION = HERE / "foundation/action_normalization.json"
RESULT = ROOT / "d_quotient_classical/certificates/CLASSICAL_MINIMAL_BV_Q3_EXPORT_V1.json"
REPORT = ROOT / "d_quotient_classical/reports/classical-minimal-bv-q3-export-v1.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def recorded_digest(value: Mapping[str, Any]) -> str:
    return digest({key: item for key, item in value.items() if key != "sha256"})


def natural_operator_ast() -> dict[str, Any]:
    nodes = [
        {
            "node_id": "g_abc",
            "operation": "metric_three_parameter_family",
            "inputs": [],
            "parameters": {
                "base": "gbar",
                "directions": ["h1", "h2", "h3"],
                "formal_parameters": ["a", "b", "c"],
            },
            "declared_output_type": "symmetric_covariant_2",
            "declared_metric_jet_order": 0,
        },
        {
            "node_id": "g_inverse",
            "operation": "inverse_metric",
            "inputs": ["g_abc"],
            "parameters": {},
            "declared_output_type": "symmetric_contravariant_2",
            "declared_metric_jet_order": 0,
        },
        {
            "node_id": "geometry",
            "operation": "levi_civita_geometry",
            "inputs": ["g_abc", "g_inverse"],
            "parameters": {
                "curvature_sign": "R^a_bcd=partial_c Gamma^a_db-partial_d Gamma^a_cb+Gamma^e_db Gamma^a_ce-Gamma^e_cb Gamma^a_de"
            },
            "declared_output_type": "levi_civita_geometry_bundle",
            "declared_metric_jet_order": 2,
        },
        {
            "node_id": "P_and_C",
            "operation": "schouten_and_weyl_4d",
            "inputs": ["geometry"],
            "parameters": {
                "schouten": "P_ab=(Ric_ab-(R/6)g_ab)/2",
                "weyl": "C_abcd=R_abcd-(g_ac P_db-g_ad P_cb-g_bc P_da+g_bd P_ca)",
            },
            "declared_output_type": "schouten_cov2_and_weyl_cov4_bundle",
            "declared_metric_jet_order": 2,
        },
        {
            "node_id": "Cotton",
            "operation": "cotton_4d",
            "inputs": ["geometry", "P_and_C"],
            "parameters": {"formula": "A_cab=nabla_c P_ab-nabla_a P_bc"},
            "declared_output_type": "cotton_covariant_3",
            "declared_metric_jet_order": 3,
        },
        {
            "node_id": "B_lower",
            "operation": "bach_4d",
            "inputs": ["geometry", "P_and_C", "Cotton"],
            "parameters": {"formula": "B_ab=nabla^c A_cab+P^cd C_acbd"},
            "declared_output_type": "symmetric_covariant_2",
            "declared_metric_jet_order": 4,
        },
        {
            "node_id": "B_upper",
            "operation": "raise_symmetric_two_tensor",
            "inputs": ["g_inverse", "B_lower"],
            "parameters": {"formula": "B^ab=g^ac g^bd B_cd"},
            "declared_output_type": "symmetric_contravariant_2",
            "declared_metric_jet_order": 4,
        },
        {
            "node_id": "volume",
            "operation": "absolute_metric_volume_density",
            "inputs": ["g_abc"],
            "parameters": {"formula": "sqrt(abs(det(g)))"},
            "declared_output_type": "absolute_metric_density_weight_plus_1",
            "declared_metric_jet_order": 0,
        },
        {
            "node_id": "E_g",
            "operation": "densitize_and_scale",
            "inputs": ["volume", "B_upper"],
            "parameters": {
                "coefficient": -2,
                "formula": "E^ab=-2 sqrt(abs(g)) B^ab",
            },
            "declared_output_type": "symmetric_contravariant_density_weight_plus_1",
            "declared_metric_jet_order": 4,
        },
        {
            "node_id": "q3_hstar_hhh",
            "operation": "mixed_third_frechet_coefficient",
            "inputs": ["E_g"],
            "parameters": {
                "coefficient": "[a*b*c]",
                "directions": ["h1", "h2", "h3"],
                "hidden_factorial": False,
                "diagonal_relation": "D3E(h,h,h)=6*[t^3]E(g+t h)",
            },
            "declared_output_type": "symmetric_trilinear_metric_jet_operator_to_symmetric_contravariant_density_weight_plus_1",
            "declared_metric_jet_order": 4,
        },
    ]
    return {
        "schema": "pure-weyl-minimal-bv-q3-natural-operator-ast-v1",
        "expression_schema_version": "canonical-natural-metric-operator-v1",
        "spacetime_dimension": 4,
        "coefficient_field": "Q",
        "nodes": nodes,
        "root_node": "q3_hstar_hhh",
        "canonical_node_sha256": digest(nodes),
    }


def build() -> dict[str, Any]:
    parent = json.loads(PARENT.read_text())
    action = json.loads(ACTION.read_text())
    if parent.get("result_id") != "CLASSICAL_MINIMAL_BV_ANTIFIELD_EXPORT_V2":
        raise ValueError("authoritative minimal BV parent drift")
    q2_zero = next(
        (item for item in parent.get("producer_checks", []) if item.get("check_id") == "Q_squared_zero"),
        {},
    )
    if q2_zero.get("status") != "VERIFIED":
        raise ValueError("minimal BV nilpotency parent is not accepted")
    expected_terms = [
        "integral g_star^{mu nu}(L_xi g_{mu nu}+2 omega g_{mu nu})",
        "integral xi_star_mu xi^nu partial_nu xi^mu",
        "integral omega_star xi^nu partial_nu omega",
    ]
    if action.get("minimal_master_terms") != expected_terms:
        raise ValueError("minimal master-action term drift")
    if action.get("Euler_coordinate") != "E_g^{mu nu}:=delta S/delta g_{mu nu}=-2 sqrt(abs(g)) B^{mu nu}":
        raise ValueError("Euler normalization drift")

    generators = parent.get("generators", [])
    symbols = [item.get("symbol") for item in generators]
    if symbols != ["g", "xi", "omega", "g_star", "xi_star", "omega_star"]:
        raise ValueError("minimal carrier drift")

    ast = natural_operator_ast()
    degree_ledger = [
        {
            "master_action_summand": action["action"],
            "hamiltonian_Q_rows": ["g_star"],
            "maximum_Q_taylor_arity": "unbounded",
            "q3_contribution": "D^3 E_g(h1,h2,h3)",
            "reason": "the non-polynomial metric Euler map is the metric derivative of the pure-Weyl action",
        },
        {
            "master_action_summand": expected_terms[0],
            "hamiltonian_Q_rows": ["g", "g_star", "xi_star", "omega_star"],
            "maximum_Q_taylor_arity": 2,
            "q3_contribution": "ZERO",
            "reason": "the summand is cubic in BV coordinates, so one Hamiltonian derivative is at most quadratic",
        },
        {
            "master_action_summand": expected_terms[1],
            "hamiltonian_Q_rows": ["xi", "xi_star"],
            "maximum_Q_taylor_arity": 2,
            "q3_contribution": "ZERO",
            "reason": "the summand is cubic in BV coordinates, so one Hamiltonian derivative is at most quadratic",
        },
        {
            "master_action_summand": expected_terms[2],
            "hamiltonian_Q_rows": ["omega", "xi_star", "omega_star"],
            "maximum_Q_taylor_arity": 2,
            "q3_contribution": "ZERO",
            "reason": "the summand is cubic in BV coordinates, so one Hamiltonian derivative is at most quadratic",
        },
    ]
    rows = [
        {
            "output_generator": symbol,
            "q3_status": "NONZERO_NATURAL_OPERATOR" if symbol == "g_star" else "IDENTICALLY_ZERO_BY_MASTER_ACTION_DEGREE",
            "accepted_input_generators": ["g", "g", "g"] if symbol == "g_star" else [],
            "operator_root": "q3_hstar_hhh" if symbol == "g_star" else None,
        }
        for symbol in symbols
    ]
    support = {
        "carrier": "six-generator minimal BV carrier",
        "rows": rows,
        "nonzero_row_count": 1,
        "nonzero_ordered_component_count": 1,
        "graded_symmetry": "ordinary S3 symmetry because all three metric inputs are even",
        "support_rule": "support q3(h1,h2,h3) is contained in support(h1) intersect support(h2) intersect support(h3)",
        "maximum_metric_jet_order": 4,
        "sha256": "",
    }
    support["sha256"] = recorded_digest(support)

    value: dict[str, Any] = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "schema": "classical-minimal-bv-q3-export-v1",
        "result_id": "CLASSICAL_MINIMAL_BV_Q3_EXPORT_V1",
        "result_kind": "AUTHORITATIVE_ACTION_DERIVED_MINIMAL_BV_ARITY_THREE_EXPORT",
        "result_state": "MINIMAL_BV_Q3_EXPORTED_ARITY_THREE_REPLAY_AND_NONMINIMAL_STABILIZATION_OPEN",
        "lifecycle": "CLASSIFIED",
        "created": "2026-08-15",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "scope": {
            "theory": "four-dimensional strict pure-Weyl minimal BV theory",
            "background_class": "arbitrary smooth Bach-flat nondegenerate pseudo-Riemannian backgrounds for the pointed Taylor complex",
            "carrier_dimension": 6,
            "coefficient_field": "Q",
            "taylor_convention": "suspended graded-symmetric factorial convention; q3 is the third Frechet derivative",
            "action_normalization": action["Euler_coordinate"],
        },
        "natural_operator_ast": ast,
        "master_action_degree_ledger": degree_ledger,
        "minimal_q3_support": support,
        "authority_chain": {
            "source_action": action["result_id"],
            "source_minimal_bv_export": parent["result_id"],
            "source_Q_squared_zero_status": q2_zero["status"],
            "derivation": [
                "Take the BV Hamiltonian vector field of the pinned minimal master action.",
                "Taylor-expand that same Q at a Bach-flat background without changing carrier or conventions.",
                "Every master-action term containing antifields is cubic, hence contributes at most q2 after one Hamiltonian derivative.",
                "The unique q3 component is the third Frechet derivative of the action-normalized metric Euler density.",
            ],
            "not_a_competing_BV_complex": True,
        },
        "claim_flags": {
            "AUTHORITATIVE_MINIMAL_BV_Q3_EXPORTED": True,
            "ARBITRARY_THREE_METRIC_INPUTS_DECLARED": True,
            "ALL_SIX_MINIMAL_OUTPUT_ROWS_CLASSIFIED": True,
            "SUPPORT_LOCALITY_DECLARED": True,
            "EXACT_COMPONENT_RECEIVER_REPLAYED": False,
            "ARITY_THREE_Q_SQUARED_IDENTITY_REPLAYED": False,
            "CYCLIC_QUARTIC_VERTEX_REPLAYED": False,
            "STRICT_386_NONMINIMAL_Q3_STABILIZED": False,
            "LORENTZIAN_CAUSAL_CERTIFIED": False,
            "QME_RESTORED": False,
        },
        "canonical_hashes": {},
        "provenance": {
            "inputs": [
                {"path": str(PARENT.relative_to(ROOT)), "result_id": parent["result_id"], "sha256": sha(PARENT)},
                {"path": str(ACTION.relative_to(ROOT)), "result_id": action["result_id"], "sha256": sha(ACTION)},
            ],
            "producer": {
                "path": str(Path(__file__).resolve().relative_to(ROOT)),
                "sha256": sha(Path(__file__).resolve()),
            },
        },
        "does_not_establish": [
            "an independent exact component execution of the natural-operator AST",
            "the coefficientwise arity-three identity q1 q3 plus q2 q2 plus q3 q1 equals zero",
            "quartic BV cyclicity in the quantum receiver convention",
            "a cyclic stabilization or L-infinity equivalence on the 386-row nonminimal carrier",
            "causal compatibility of q3 with a Green homotopy",
            "a Hadamard state, renormalized time-ordered products, QME restoration, or a Lorentzian quantum theory",
        ],
        "next_gate": "Independently execute this AST on arbitrary three-input jets, reproduce the diagonal cubic witness, then replay the complete minimal arity-three identity before stabilizing it to 386 rows.",
        "human_report": "d_quotient_classical/reports/classical-minimal-bv-q3-export-v1.md",
    }
    value["canonical_hashes"] = {
        "natural_operator_ast_sha256": digest(ast),
        "master_action_degree_ledger_sha256": digest(degree_ledger),
        "minimal_q3_support_sha256": digest(support),
        "authority_chain_sha256": digest(value["authority_chain"]),
    }
    return value


def render(value: Mapping[str, Any]) -> str:
    rows = "\n".join(
        f"| `{item['output_generator']}` | `{item['q3_status']}` | "
        f"{', '.join(item['accepted_input_generators']) or 'none'} |"
        for item in value["minimal_q3_support"]["rows"]
    )
    return f"""# Classical minimal-BV q3 export v1

**Result:** `{value['result_id']}`

**State:** `{value['result_state']}`
**Dependency:** `LOCAL-ALGEBRAIC`

## Result

The authoritative pure-Weyl minimal master action determines the entire
arity-three Taylor component on its six-generator carrier.  Exactly one row
is nonzero:

```text
q3(h1,h2,h3) = D^3[-2 sqrt(abs(g)) B(g)^sharp](h1,h2,h3)
```

All antifield-dependent master-action summands are cubic, so their BV
Hamiltonian derivatives are at most quadratic.  They generate q1 and q2 but
no q3.  This is an export from the existing certified classical complex. It
is not a reconstruction of a second BV complex.

| Output row | q3 status | Accepted inputs |
|---|---|---|
{rows}

The natural-operator root is symmetric, fourth order and support-local.  On
diagonal input the convention is `D3E(h,h,h)=6*[t^3]E(g+t h)`.

## Boundary

This producer classifies and exports the complete minimal q3, but does not
count its own construction as an independent component replay.  The
coefficientwise arity-three identity, quartic cyclicity, and the 386-row
nonminimal stabilization remain open and fail closed.

## Reproduction

```text
python3 d_quotient_classical/minimal_bv_antifield/classical_minimal_bv_q3_export_v1.py --check
python3 d_quotient_classical/minimal_bv_antifield/check_classical_minimal_bv_q3_export_v1.py
```

## Does not establish

""" + "\n".join(f"- {item}." for item in value["does_not_establish"]) + "\n"


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
        print("CLASSICAL_MINIMAL_BV_Q3_EXPORT_V1: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    for path, content in outputs:
        path.write_bytes(content)
    print("CLASSICAL_MINIMAL_BV_Q3_EXPORT_V1: wrote certificate and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
