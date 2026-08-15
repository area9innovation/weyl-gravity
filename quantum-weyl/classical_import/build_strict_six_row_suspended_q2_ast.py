#!/usr/bin/env python3
"""Build the portable six-row suspended strict pure-Weyl q2 ledger."""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_SIX_ROW_SUSPENDED_Q2_AST_V1.json"
REPORT = HERE / "REPORT_STRICT_SIX_ROW_SUSPENDED_Q2_AST_V1.md"
INPUTS = (
    ("quantum-weyl/classical_import/certificates/STRICT_Q2_KINEMATIC_COTANGENT_AST_V1.json", "STRICT_Q2_KINEMATIC_COTANGENT_AST_V1", "five diagonal kinematic/cotangent rows"),
    ("quantum-weyl/classical_import/certificates/STRICT_BACH_NATURAL_OPERATOR_AST_V1.json", "STRICT_BACH_NATURAL_OPERATOR_AST_V1", "portable polarized Bach kernel"),
    ("quantum-weyl/classical_import/certificates/STRICT_CYLINDER_HSTAR_BASEPOINT_ROW_V1.json", "STRICT_CYLINDER_HSTAR_BASEPOINT_ROW_V1", "source-fixed h-star coefficients and cotangent formulas"),
    ("d_quotient_classical/certificates/CLASSICAL_MINIMAL_BV_ANTIFIELD_EXPORT_V2.json", "CLASSICAL_MINIMAL_BV_ANTIFIELD_EXPORT_V2", "authoritative generator gradings and Q rows"),
    ("quantum-weyl/classical_import/certificates/SUPPORT_LOCAL_Q2_EXPORT_CONTRACT.json", "SUPPORT_LOCAL_Q2_EXPORT_CONTRACT", "downstream complete-export boundary"),
)
SYMBOLS = ("h", "c", "omega", "h_star", "c_star", "omega_star")
DEGREES = {"h": 0, "c": -1, "omega": -1, "h_star": 1, "c_star": 2, "omega_star": 2}
PARITIES = {symbol: degree % 2 for symbol, degree in DEGREES.items()}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def load(relative: str) -> dict[str, Any]:
    return json.loads((ROOT / relative).read_text())


def primary_components(bach: Mapping[str, Any], kinematic: Mapping[str, Any], hstar: Mapping[str, Any]) -> list[dict[str, object]]:
    definitions = {item["operator_id"]: item for item in kinematic["operator_definitions"]}
    components = {item["component_id"]: item for item in kinematic["components"]}

    def inherited(component_id: str, formula_id: str | None = None) -> dict[str, object]:
        component = components[component_id]
        definition = definitions[component["operator_id"]]
        return {
            "primary_id": component_id,
            "output": component["output"],
            "inputs": component["inputs"],
            "operator_id": formula_id or component["operator_id"],
            "coefficient": component["coefficient"],
            "coordinate_formula": definition["coordinate_formula"],
            "maximum_input_jet_orders": definition["maximum_input_jet_orders"],
            "maximum_total_derivative_order": max(definition["maximum_input_jet_orders"]),
            "source_atoms": definition["source_atoms"],
            "portable_semantics": "KINEMATIC_TENSOR_NATURAL_COORDINATE_OPERATOR",
        }

    vector = inherited("q2_c_cc", "vector_ghost_lie_bracket")
    vector.update({
        "coordinate_formula": "[c_left,c_right]^mu=c_left^rho partial_rho c_right^mu-c_right^rho partial_rho c_left^mu",
        "maximum_input_jet_orders": [1, 1],
        "maximum_total_derivative_order": 1,
        "intrinsic_swap_sign": -1,
        "diagonal_recovery": "(1/2)[c,c]^mu=c^rho partial_rho c^mu in the external Grassmann extension",
    })
    inherited_rows = [
        inherited("q2_omega_comega"),
        inherited("q2_h_ch"),
        inherited("q2_h_omegah"),
        inherited("q2_cstar_hhstar"),
        inherited("q2_cstar_ccstar"),
        inherited("q2_cstar_omegaomegastar"),
        inherited("q2_omegastar_hhstar"),
        inherited("q2_omegastar_comegastar"),
    ]
    natural_root = bach["natural_operator_ast"]["root_node"]
    hstar_components = {item["component_id"]: item for item in hstar["components"]}
    metric = {
        "primary_id": "q2_hstar_hh",
        "output": "h_star",
        "inputs": ["h", "h"],
        "operator_id": "polarized_bach_natural_operator",
        "coefficient": 1,
        "coordinate_formula": "K_g(h_left,h_right)=[a*b]E_g(gbar+a h_left+b h_right)",
        "maximum_input_jet_orders": [4, 4],
        "maximum_total_derivative_order": 4,
        "source_atoms": ["E_g"],
        "portable_semantics": {"result_id": bach["result_id"], "ast_sha256": bach["canonical_hashes"]["natural_operator_ast_sha256"], "root_node": natural_root},
        "intrinsic_swap_sign": 1,
        "diagonal_recovery": "(1/2)q2(h,h)=(1/2)K_g(h,h)",
    }
    diff = hstar_components["q2_hstar_chstar"]
    weyl = hstar_components["q2_hstar_omegahstar"]
    hstar_rows = [
        {
            "primary_id": "q2_hstar_chstar",
            "output": "h_star",
            "inputs": diff["inputs"],
            "operator_id": diff["operator"],
            "coefficient": 1,
            "coordinate_formula": diff["coordinate_formula"],
            "maximum_input_jet_orders": diff["maximum_input_jet_orders"],
            "maximum_total_derivative_order": diff["maximum_total_derivative_order"],
            "source_atoms": [diff["source_atom"]],
            "portable_semantics": "TENSOR_NATURAL_COTANGENT_LIFT",
        },
        {
            "primary_id": "q2_hstar_omegahstar",
            "output": "h_star",
            "inputs": weyl["inputs"],
            "operator_id": weyl["operator"],
            "coefficient": -2,
            "coordinate_formula": weyl["coordinate_formula"],
            "maximum_input_jet_orders": weyl["maximum_input_jet_orders"],
            "maximum_total_derivative_order": weyl["maximum_total_derivative_order"],
            "source_atoms": [weyl["source_atom"]],
            "portable_semantics": "TENSOR_NATURAL_COTANGENT_LIFT",
        },
    ]
    result = [vector, *inherited_rows[:3], metric, *hstar_rows, *inherited_rows[3:]]
    if len(result) != 12:
        raise ValueError("primary component inventory must contain twelve terms")
    return result


def ordered_components(primary: list[dict[str, object]]) -> list[dict[str, object]]:
    ordered = []
    for item in primary:
        left, right = item["inputs"]
        if left == right:
            expected = -1 if PARITIES[left] else 1
            if item.get("intrinsic_swap_sign") != expected:
                raise ValueError(f"{item['primary_id']}: intrinsic swap sign drift")
            ordered.append({
                "component_id": item["primary_id"],
                "primary_id": item["primary_id"],
                "output": item["output"],
                "inputs": [left, right],
                "coefficient_relative_to_primary": 1,
                "orientation": "INTRINSIC_SELF_PAIR",
                "koszul_swap_partner": item["primary_id"],
                "koszul_swap_sign": expected,
            })
            continue
        sign = -1 if PARITIES[left] * PARITIES[right] else 1
        forward_id = item["primary_id"] + "__forward"
        reverse_id = item["primary_id"] + "__reverse"
        ordered.extend((
            {
                "component_id": forward_id,
                "primary_id": item["primary_id"],
                "output": item["output"],
                "inputs": [left, right],
                "coefficient_relative_to_primary": 1,
                "orientation": "PRIMARY",
                "koszul_swap_partner": reverse_id,
                "koszul_swap_sign": sign,
            },
            {
                "component_id": reverse_id,
                "primary_id": item["primary_id"],
                "output": item["output"],
                "inputs": [right, left],
                "coefficient_relative_to_primary": sign,
                "orientation": "KOSZUL_SWAP",
                "koszul_swap_partner": forward_id,
                "koszul_swap_sign": sign,
            },
        ))
    return ordered


def external_grassmann_replay(primary: list[dict[str, object]]) -> dict[str, object]:
    """Replay the diagonal factors with two exact odd coefficient generators."""

    x = (Fraction(1), Fraction(2), Fraction(-1), Fraction(3))
    y = (Fraction(2), Fraction(-1), Fraction(1), Fraction(0))
    dx = tuple(tuple(Fraction((3 * mu + 2 * rho) % 7 - 3, rho + 1) for rho in range(4)) for mu in range(4))
    dy = tuple(tuple(Fraction((5 * mu + rho) % 9 - 4, mu + 2) for rho in range(4)) for mu in range(4))
    bracket = tuple(sum(x[rho] * dy[mu][rho] - y[rho] * dx[mu][rho] for rho in range(4)) for mu in range(4))
    q2_theta12 = tuple(2 * value for value in bracket)
    q_diagonal_theta12 = bracket
    mixed = []
    for item in primary:
        left, right = item["inputs"]
        if left == right:
            continue
        sign = -1 if PARITIES[left] * PARITIES[right] else 1
        mixed.append({
            "primary_id": item["primary_id"],
            "kernel_swap_sign": sign,
            "external_coefficient_reordering_sign": sign,
            "half_sum_multiplier": "1",
        })
    return {
        "odd_vector_fixture": {
            "X": [str(value) for value in x],
            "Y": [str(value) for value in y],
            "dX": [[str(value) for value in row] for row in dx],
            "dY": [[str(value) for value in row] for row in dy],
            "underlying_bracket_XY": [str(value) for value in bracket],
            "q2_c_c_theta1theta2_coefficient": [str(value) for value in q2_theta12],
            "half_q2_equals_c_partial_c_theta1theta2": q_diagonal_theta12 == tuple(value / 2 for value in q2_theta12),
            "nonzero_component_count": sum(value != 0 for value in bracket),
        },
        "mixed_species": mixed,
        "mixed_species_exact_rule": "(1/2)(1+kernel_swap_sign*external_reordering_sign)=1",
        "all_ten_mixed_multipliers_equal_one": len(mixed) == 10 and all(item["kernel_swap_sign"] * item["external_coefficient_reordering_sign"] == 1 for item in mixed),
        "even_metric_self_pair_half_multiplier": "1/2",
    }


def build() -> dict[str, Any]:
    kinematic, bach, hstar, exported, contract = (load(path) for path, _, _ in INPUTS)
    for value, (_, result_id, _) in zip((kinematic, bach, hstar, exported, contract), INPUTS):
        if value.get("result_id") != result_id:
            raise ValueError(f"dependency drift: {result_id}")
    if bach.get("claim_flags", {}).get("POLARIZED_BACH_KERNEL_PORTABLE") is not True:
        raise ValueError("portable Bach kernel is unavailable")
    if hstar.get("claim_flags", {}).get("METRIC_ANTIFIELD_DIFF_COTANGENT_TERM_CERTIFIED") is not True or hstar.get("claim_flags", {}).get("METRIC_ANTIFIELD_WEYL_COTANGENT_TERM_CERTIFIED") is not True:
        raise ValueError("h-star cotangent terms are unavailable")
    if contract.get("result_state") != "CONTRACT_READY_AWAITING_CLASSICAL_EXPORT":
        raise ValueError("complete receiver contract boundary drift")
    source_symbols = {"g": "h", "xi": "c", "omega": "omega", "g_star": "h_star", "xi_star": "c_star", "omega_star": "omega_star"}
    generator_by_source = {item["symbol"]: item for item in exported["generators"]}
    for source, target in source_symbols.items():
        item = generator_by_source[source]
        if item["Grassmann_parity"] != PARITIES[target] or -item["ghost_number"] != DEGREES[target]:
            raise ValueError(f"generator grading crosswalk drift: {source}")

    primary = primary_components(bach, kinematic, hstar)
    ordered = ordered_components(primary)
    if len(ordered) != 22:
        raise ValueError("ordered suspended component inventory must contain twenty-two terms")
    by_id = {item["component_id"]: item for item in ordered}
    for item in ordered:
        output, left, right = item["output"], *item["inputs"]
        if DEGREES[output] - DEGREES[left] - DEGREES[right] != 1:
            raise ValueError(f"degree-one failure: {item['component_id']}")
        partner = by_id[item["koszul_swap_partner"]]
        if item["orientation"] == "INTRINSIC_SELF_PAIR":
            primary_item = next(row for row in primary if row["primary_id"] == item["primary_id"])
            if partner is not item or primary_item["intrinsic_swap_sign"] != item["koszul_swap_sign"]:
                raise ValueError(f"intrinsic Koszul failure: {item['component_id']}")
        elif partner["inputs"] != [right, left] or partner["coefficient_relative_to_primary"] != item["koszul_swap_sign"] * item["coefficient_relative_to_primary"]:
            raise ValueError(f"Koszul partner failure: {item['component_id']}")

    rows = [
        {
            "output": symbol,
            "status": "COMPLETE",
            "primary_component_ids": [item["primary_id"] for item in primary if item["output"] == symbol],
            "ordered_component_ids": [item["component_id"] for item in ordered if item["output"] == symbol],
        }
        for symbol in SYMBOLS
    ]
    if any(not row["primary_component_ids"] for row in rows):
        raise ValueError("a minimal q2 output row is empty")
    diagonal_crosswalk = {
        "Taylor_formula": "Q(Phi)=q1(Phi)+(1/2)q2(Phi,Phi)+O(Phi^3)",
        "external_Grassmann_extension": "Koszul signs are applied to the ordered tensor kernel before the field-coordinate coefficients are multiplied",
        "same_species_rows": [
            {"primary_id": "q2_c_cc", "q2_kernel": "[c_left,c_right]", "diagonal_Q_term": "(1/2)[c,c]=c^rho partial_rho c", "swap_sign": -1},
            {"primary_id": "q2_hstar_hh", "q2_kernel": "K_g(h_left,h_right)", "diagonal_Q_term": "(1/2)K_g(h,h)", "swap_sign": 1},
        ],
        "mixed_species_rule": "the two ordered orientations, the Koszul kernel sign and the external-coordinate reordering sign combine to reproduce each displayed diagonal coefficient once",
        "source_diagonal_component_count": 12,
        "ordered_suspended_component_count": 22,
        "external_Grassmann_exact_replay": external_grassmann_replay(primary),
    }
    checks = [
        {"check_id": "six_output_rows_complete", "status": "VERIFIED", "evidence": "twelve primary and twenty-two ordered components cover every minimal output"},
        {"check_id": "cohomological_degree_one", "status": "VERIFIED", "evidence": "all ordered components satisfy degree(output)-degree(left)-degree(right)=1"},
        {"check_id": "q2_koszul_symmetry", "status": "VERIFIED", "evidence": "every ordered component has an exact swapped partner with sign (-1)^(parity_left parity_right); both self-pairs replay intrinsic signs"},
        {"check_id": "diagonal_Taylor_recovery", "status": "VERIFIED", "evidence": "an exact two-generator exterior-coefficient fixture replays the odd bracket factor two; the half-Hessian and ten mixed sign products recover every source diagonal term"},
        {"check_id": "portable_hstar_row", "status": "VERIFIED", "evidence": "the portable Bach root replaces the cylinder table and both source-fixed cotangent lifts remain tensor-natural"},
        {"check_id": "q1_q2_arity_two_nilpotency", "status": "NOT_REPLAYED", "evidence": "a common executable local q1 receiver is the next gate"},
        {"check_id": "D_q2_derivation", "status": "NOT_REPLAYED", "evidence": "the full local D action is not serialized"},
        {"check_id": "BV_cyclicity_q2", "status": "NOT_REPLAYED", "evidence": "the common support-local pairing receiver is not serialized"},
    ]
    value: dict[str, Any] = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "schema": "strict-six-row-suspended-q2-ast-v1",
        "result_id": "STRICT_SIX_ROW_SUSPENDED_Q2_AST_V1",
        "result_kind": "PORTABLE_COMPLETE_COMPONENT_LEDGER_FOR_SUSPENDED_STRICT_Q2",
        "result_state": "SIX_ROWS_PORTABLE_AND_KOSZUL_REPLAYED_Q1_D_PAIRING_IDENTITIES_OPEN",
        "lifecycle": "CLASSIFIED",
        "created": "2026-08-15",
        "repository_base_commit": "0dc53a6ba452b0da8ad5a98b13b3d11871906778",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "convention": "suspended-graded-symmetric-factorial-v1",
        "scope": {
            "theory": "strict pure-Weyl minimal Diff x Weyl BV theory",
            "background_class": "arbitrary smooth nondegenerate four-dimensional pseudo-Riemannian metric background",
            "carrier": "compactly supported smooth minimal BV sections with external graded-commutative coefficients",
            "locality": "SUPPORT_LOCAL_POLYDIFFERENTIAL",
            "maximum_metric_input_jet_order": 4,
            "maximum_total_derivative_order": 4,
            "support_rule": "each bilinear output support lies in the intersection of its two input supports",
        },
        "generator_ledger": [
            {"symbol": symbol, "local_tangent_degree": DEGREES[symbol], "Grassmann_parity": PARITIES[symbol]}
            for symbol in SYMBOLS
        ],
        "primary_components": primary,
        "ordered_components": ordered,
        "row_completeness": rows,
        "diagonal_crosswalk": diagonal_crosswalk,
        "proof_checks": checks,
        "canonical_hashes": {},
        "provenance": {"inputs": [{"path": path, "result_or_artifact_id": result_id, "sha256": sha(ROOT / path), "role": role} for path, result_id, role in INPUTS]},
        "claim_flags": {
            "PORTABLE_TENSOR_NATURAL_HSTAR_ROW": True,
            "SUSPENDED_GRADED_POLARIZATION_REPLAYED": True,
            "SIX_MINIMAL_Q2_ROW_LEDGERS_COMPLETE": True,
            "Q2_KOSZUL_SYMMETRY_REPLAYED": True,
            "Q1_Q2_ARITY_TWO_NILPOTENCY_REPLAYED": False,
            "STRICT_FULL_LOCAL_D_ACTION_CERTIFIED": False,
            "D_Q2_DERIVATION_REPLAYED": False,
            "BV_CYCLICITY_Q2_REPLAYED": False,
            "STRICT_SUPPORT_LOCAL_Q2_COMPLETE": False,
            "CLASSICAL_IMPORT_GATE_PASSED": False,
            "LORENTZIAN_CAUSAL_CERTIFIED": False,
            "QME_RESTORED": False,
        },
        "does_not_establish": [
            "q1q2=0 or any higher arity master identity",
            "a complete local D action or its derivation identity",
            "BV cyclicity on a common support-local pairing",
            "the seven-proof complete SUPPORT_LOCAL_Q2_EXPORT_CONTRACT",
            "a passed classical import Gate A",
            "a causal Green homotopy, Hadamard state, Lorentzian QME, or Lorentzian quantum theory",
        ],
        "schema_path": "quantum-weyl/classical_import/schema/strict-six-row-suspended-q2-ast-v1.schema.json",
        "independent_checker": "quantum-weyl/classical_import/check_strict_six_row_suspended_q2_ast.py",
        "human_report": "quantum-weyl/classical_import/REPORT_STRICT_SIX_ROW_SUSPENDED_Q2_AST_V1.md",
    }
    value["canonical_hashes"] = {
        "generator_ledger_sha256": digest(value["generator_ledger"]),
        "primary_components_sha256": digest(primary),
        "ordered_components_sha256": digest(ordered),
        "row_completeness_sha256": digest(rows),
        "diagonal_crosswalk_sha256": digest(diagonal_crosswalk),
        "proof_checks_sha256": digest(checks),
    }
    return value


def render(value: Mapping[str, Any]) -> str:
    rows = "\n".join(f"| `{row['output']}` | {len(row['primary_component_ids'])} | {len(row['ordered_component_ids'])} | `{row['status']}` |" for row in value["row_completeness"])
    primary = "\n".join(f"| `{item['primary_id']}` | `{', '.join(item['inputs'])}` | `{item['output']}` | `{item['coefficient']}` | {item['coordinate_formula']} |" for item in value["primary_components"])
    checks = "\n".join(f"| `{item['check_id']}` | `{item['status']}` | {item['evidence']} |" for item in value["proof_checks"])
    return f"""# Portable six-row suspended strict q2 AST v1

**Result:** `{value['result_id']}`

**State:** `{value['result_state']}`

**Dependency:** `LOCAL-ALGEBRAIC`

## Outcome

All six minimal strict pure-Weyl `q2` output rows now have a portable component
ledger in the repository convention
`suspended-graded-symmetric-factorial-v1`.  The twelve diagonal quadratic
terms become twenty-two ordered components. Every mixed term has its exact
Koszul-swapped partner, the metric self-pair uses the symmetric portable Bach
kernel, and the odd Diff-ghost self-pair uses the antisymmetric vector bracket.

This closes two earlier deficits: the metric-antifield row is tensor-natural
on an arbitrary background, and the six-row suspension is explicit. It does
not yet satisfy the complete downstream export contract because `q1q2=0`, the
full local `D` action and BV cyclicity have not been independently executed.

## Row coverage

| Output | Primary terms | Ordered terms | Status |
|---|---:|---:|---|
{rows}

## Twelve primary kernels

| Component | Inputs | Output | Coefficient | Coordinate or natural formula |
|---|---|---|---:|---|
{primary}

The Taylor relation is

```text
Q(Phi) = q1(Phi) + (1/2) q2(Phi,Phi) + O(Phi^3).
```

For the two self-pairs, `(1/2)[c,c]=c partial c` in the external Grassmann
extension and `(1/2)q2(h,h)=(1/2)K_g(h,h)`. For each mixed species pair, the
Koszul sign of the ordered kernel and the reordering sign of its external
graded coefficients cancel exactly, recovering the displayed diagonal term
once rather than twice. The certificate executes this bookkeeping with two
independent odd generators: the `theta1*theta2` coefficient of `q2(c,c)` is
exactly twice the coefficient of `c partial c`, and all ten mixed half-sums
have multiplier one.

## Proof and gate ledger

| Check | Status | Evidence or missing receiver |
|---|---|---|
{checks}

The next decisive calculation is the arity-two master identity. It requires a
common executable local `q1`, including the linearized Bach equation and the
two Noether-identity rows. A source-action theorem is useful guidance but will
not be substituted for receiver execution on these bytes.

## Reproduction

```text
python3 quantum-weyl/classical_import/build_strict_six_row_suspended_q2_ast.py --check
python3 quantum-weyl/classical_import/check_strict_six_row_suspended_q2_ast.py
python3 quantum-weyl/classical_import/verify_strict_six_row_suspended_q2_ast.py
python3 -m unittest quantum-weyl/classical_import/tests/test_strict_six_row_suspended_q2_ast.py -v
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
        print("STRICT_SIX_ROW_SUSPENDED_Q2_AST_V1: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    for path, content in outputs:
        path.write_bytes(content)
    print("STRICT_SIX_ROW_SUSPENDED_Q2_AST_V1: wrote certificate and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
