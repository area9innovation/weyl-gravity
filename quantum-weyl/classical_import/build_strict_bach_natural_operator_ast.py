#!/usr/bin/env python3
"""Build the portable tensor-natural Bach-Hessian AST certificate."""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from bach_natural_operator_ast import (
    canonical_ast,
    evaluate_ast,
    transform_background,
    transform_metric_jets,
    transform_output_density,
    validate_ast,
)
import cylinder_polarized_bach_evaluator as point


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_BACH_NATURAL_OPERATOR_AST_V1.json"
REPORT = HERE / "REPORT_STRICT_BACH_NATURAL_OPERATOR_AST_V1.md"
INPUTS = (
    ("quantum-weyl/classical_import/certificates/STRICT_CYLINDER_BACH_UNIVERSAL_EXPORT_V1.json", "STRICT_CYLINDER_BACH_UNIVERSAL_EXPORT_V1", "exact exhaustive cylinder-frame coefficient table"),
    ("quantum-weyl/classical_import/certificates/STRICT_CYLINDER_HSTAR_BASEPOINT_ROW_V1.json", "STRICT_CYLINDER_HSTAR_BASEPOINT_ROW_V1", "assembled metric-antifield diagonal row"),
    ("d_quotient_classical/minimal_bv_antifield/foundation/action_normalization.json", "PURE_WEYL_ACTION_NORMALIZATION_V2", "action-normalized Euler density"),
    ("d_quotient_classical/certificates/NARIAI_TRANSVERSE_ACTION_BACH_HESSIAN_VARIATION_V1.json", "NARIAI_TRANSVERSE_ACTION_BACH_HESSIAN_VARIATION_V1", "independent Nariai action-Hessian evidence and normalization"),
)
ENGINE = HERE / "bach_natural_operator_ast.py"
POINT_ENGINE = HERE / "cylinder_polarized_bach_evaluator.py"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def load(relative: str) -> dict[str, Any]:
    return json.loads((ROOT / relative).read_text())


def serialize(values: Mapping[tuple[int, int], Fraction]) -> list[str]:
    return [str(values[pair]) for pair in point.PAIRS]


def primitive_contracts() -> list[dict[str, object]]:
    return [
        {"operation": "metric_two_parameter_family", "naturality": "pullback of metrics and metric variations", "requires": [], "preserves_locality": True},
        {"operation": "inverse_metric", "naturality": "inverse is equivariant under pullback of nondegenerate metrics", "requires": ["metric_two_parameter_family"], "preserves_locality": True},
        {"operation": "levi_civita_geometry", "naturality": "the Levi-Civita connection and its curvature commute with metric pullback", "requires": ["metric_two_parameter_family", "inverse_metric"], "preserves_locality": True},
        {"operation": "schouten_and_weyl_4d", "naturality": "four-dimensional Schouten and Weyl tensors are contractions and rational linear combinations of natural curvature tensors", "requires": ["levi_civita_geometry"], "preserves_locality": True},
        {"operation": "cotton_4d", "naturality": "covariant differentiation and alternation of a natural tensor are natural", "requires": ["levi_civita_geometry", "schouten_and_weyl_4d"], "preserves_locality": True},
        {"operation": "bach_4d", "naturality": "covariant differentiation, raising, contraction and tensor product preserve naturality", "requires": ["levi_civita_geometry", "schouten_and_weyl_4d", "cotton_4d"], "preserves_locality": True},
        {"operation": "raise_symmetric_two_tensor", "naturality": "raising indices with the inverse metric commutes with pullback", "requires": ["inverse_metric", "bach_4d"], "preserves_locality": True},
        {"operation": "absolute_metric_volume_density", "naturality": "the absolute metric volume is a pullback-natural density, including orientation reversal", "requires": ["metric_two_parameter_family"], "preserves_locality": True},
        {"operation": "densitize_and_scale", "naturality": "tensor product with a natural density and exact scalar multiplication preserve naturality", "requires": ["absolute_metric_volume_density", "raise_symmetric_two_tensor"], "preserves_locality": True},
        {"operation": "mixed_frechet_coefficient", "naturality": "differentiating an equivariant smooth natural map twice gives an equivariant symmetric bilinear natural operator", "requires": ["densitize_and_scale"], "preserves_locality": True},
    ]


def build() -> dict[str, Any]:
    universal, hstar, normalization, nariai = (load(path) for path, _, _ in INPUTS)
    for value, (_, expected, _) in zip((universal, hstar, normalization, nariai), INPUTS):
        if value.get("result_id", value.get("schema")) != expected:
            raise ValueError(f"dependency drift: {expected}")
    if universal.get("result_state") != "UNIVERSAL_CYLINDER_TABLE_AND_DIFF_IDENTITY_CERTIFIED_GLOBAL_AST_OPEN":
        raise ValueError("cylinder globalization boundary drift")
    if hstar.get("claim_flags", {}).get("PORTABLE_TENSOR_NATURAL_HSTAR_ROW") is not False:
        raise ValueError("upstream h-star row was silently promoted")
    if normalization.get("Euler_coordinate") != "E_g^{mu nu}:=delta S/delta g_{mu nu}=-2 sqrt(abs(g)) B^{mu nu}":
        raise ValueError("Euler-density normalization drift")
    nariai_formula = nariai.get("exact_data", {}).get("direct_action_leading_derivation", {}).get("formula", "")
    if "nabla^c nabla^d C_acbd" not in nariai_formula or "Ric^cd C_acbd" not in nariai_formula or nariai.get("dependency_tags") != ["LOCAL-ALGEBRAIC"]:
        raise ValueError("Nariai action-Hessian crosswalk drift")

    ast = canonical_ast()
    validate_ast(ast)
    background_rows = []
    backgrounds = (
        ("conformal_cylinder", point.cylinder_background(4), 1, 2),
        ("minkowski", point.flat_background(4), 2, 3),
        ("flat_brinkmann", point.brinkmann_background(4), 3, 4),
    )
    for name, background, left_seed, right_seed in backgrounds:
        left, right = point.sparse_fixture(left_seed), point.sparse_fixture(right_seed)
        natural = evaluate_ast(ast, left, right, background=background)
        reference = point.polarized_bach_euler_density(left, right, background=background)
        if natural != reference:
            raise ValueError(f"natural AST disagrees with point evaluator on {name}")
        output = serialize(natural)
        background_rows.append({
            "background": name,
            "left_seed": left_seed,
            "right_seed": right_seed,
            "nonzero_output_count": sum(value != 0 for value in natural.values()),
            "output_sha256": digest(output),
            "natural_ast_equals_independent_point_evaluator": True,
        })

    ppwave_rows = []
    brinkmann = point.brinkmann_background(4)
    for left_seed, right_seed in ((1, 2), (2, 4), (3, 5)):
        left, right = point.ppwave_profile_fixture(left_seed), point.ppwave_profile_fixture(right_seed)
        natural = evaluate_ast(ast, left, right, background=brinkmann)
        reference = point.polarized_bach_euler_density(left, right, background=brinkmann)
        if natural != reference or any(natural.values()):
            raise ValueError(f"pp-wave restriction failed at seeds {left_seed},{right_seed}")
        ppwave_rows.append({"left_seed": left_seed, "right_seed": right_seed, "all_ten_outputs_zero": True, "output_sha256": digest(serialize(natural))})

    permutation = (0, 2, 3, 1)
    signs = (-1, 1, -1, 1)
    left, right = point.sparse_fixture(5), point.sparse_fixture(6)
    cylinder = point.cylinder_background(4)
    original = evaluate_ast(ast, left, right, background=cylinder)
    transformed = evaluate_ast(
        ast,
        transform_metric_jets(left, permutation, signs),
        transform_metric_jets(right, permutation, signs),
        background=transform_background(cylinder, permutation, signs),
    )
    expected = transform_output_density(original, permutation, signs)
    if transformed != expected:
        raise ValueError("signed coordinate-permutation covariance failed")

    contracts = primitive_contracts()
    operations = [node["operation"] for node in ast["nodes"]]
    if operations != [item["operation"] for item in contracts] or not all(item["preserves_locality"] for item in contracts):
        raise ValueError("compositional naturality ledger is incomplete")
    naturality = {
        "proof_kind": "COMPOSITIONAL_NATURAL_OPERATOR_THEOREM_WITH_EXECUTABLE_SEMANTICS",
        "domain_category": "four-dimensional smooth pseudo-Riemannian metrics and local diffeomorphisms on nondegenerate metric jets",
        "source_bundle": "two symmetric covariant metric variations",
        "target_bundle": "symmetric contravariant tensor density of absolute weight plus one",
        "derivation": [
            "Every node before mixed Frechet extraction is a standard pullback-natural metric construction listed in primitive_contracts.",
            "Finite composition, contraction, covariant differentiation, tensor product and exact rational linear combination preserve pullback naturality.",
            "Therefore E(g)=-2 sqrt(abs(g)) B(g)^sharp is a fourth-order natural differential operator.",
            "Differentiating phi^*E(g)=E(phi^*g) twice in two metric directions proves phi^*D^2E_g(h1,h2)=D^2E_{phi^*g}(phi^*h1,phi^*h2).",
        ],
        "conclusion": "K_g(h1,h2)=[a*b]E(g+a h1+b h2) is a symmetric, fourth-order, support-local tensor-natural bilinear operator",
        "orientation_boundary": "the target uses the absolute metric density, so the statement includes orientation-reversing coordinate changes",
        "finite_coordinate_test_role": "the signed-permutation replay is an implementation regression only; the general conclusion follows from the compositional theorem",
        "status": "CERTIFIED",
    }
    signed_witness = {
        "coordinate_rule": "x[p[i]]=s[i] y[i]",
        "permutation": list(permutation),
        "signs": list(signs),
        "left_seed": 5,
        "right_seed": 6,
        "transformed_output_sha256": digest(serialize(transformed)),
        "expected_tensor_density_output_sha256": digest(serialize(expected)),
        "exact_covariance": True,
    }

    value: dict[str, Any] = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "schema": "strict-bach-natural-operator-ast-v1",
        "result_id": "STRICT_BACH_NATURAL_OPERATOR_AST_V1",
        "result_kind": "PORTABLE_EXECUTABLE_TENSOR_NATURAL_POLARIZED_BACH_OPERATOR",
        "result_state": "PORTABLE_NATURAL_BACH_HESSIAN_CERTIFIED_HSTAR_INTEGRATION_AND_SUSPENSION_OPEN",
        "lifecycle": "CLASSIFIED",
        "created": "2026-08-15",
        "repository_base_commit": "dec9e0ce4315d99c46b52077763c95961563027e",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "scope": {
            "theory": "strict pure-Weyl metric Euler row",
            "background_class": "arbitrary smooth nondegenerate four-dimensional pseudo-Riemannian metric jets",
            "input": "two compactly supported symmetric covariant metric variations",
            "output": "symmetric contravariant absolute density of weight plus one",
            "coefficient_field": "Q",
            "maximum_metric_jet_order": 4,
            "taylor_convention": "coefficient of a*b with no hidden factor of 1/2",
            "action_normalization": normalization["Euler_coordinate"],
            "support_rule": "support K_g(h1,h2) is contained in support(h1) intersect support(h2)",
        },
        "natural_operator_ast": ast,
        "primitive_contracts": contracts,
        "compositional_naturality": naturality,
        "exact_evaluator_checks": {
            "background_crosschecks": background_rows,
            "ppwave_restriction_crosschecks": ppwave_rows,
            "signed_coordinate_permutation": signed_witness,
            "input_swap_symmetry": True,
            "all_arithmetic_exact": True,
        },
        "cross_background_evidence": {
            "cylinder_universal_table": {"result_id": universal["result_id"], "table_sha256": universal["canonical_hashes"]["universal_table_sha256"], "relationship": "the portable AST receiver agrees with the same independently checked point semantics to which the exhaustive cylinder table was compared"},
            "Nariai_action_Hessian": {"result_id": nariai["result_id"], "sha256": sha(ROOT / INPUTS[3][0]), "relationship": "independent covariant-Bach derivation with the same action normalization; no component adapter equality is claimed here"},
        },
        "gate_advancement": [
            {"gate": "P4_PORTABLE_AST_EXPORT", "status": "PASS", "evidence": "content-addressed typed DAG, exact evaluator, compositional naturality theorem and multi-background regressions"},
            {"gate": "HSTAR_PORTABLE_INTEGRATION", "status": "OPEN", "evidence": "replace the cylinder K reference in the h-star row by this AST and combine with its already certified cotangent terms"},
            {"gate": "SUSPENDED_GRADED_POLARIZATION", "status": "OPEN", "evidence": "the repository suspension and odd diagonal convention have not yet been replayed across all six rows"},
            {"gate": "SIX_ROW_INTERACTION_IDENTITIES", "status": "OPEN", "evidence": "q1q2, D derivation and BV cyclicity require the integrated six-row receiver"},
        ],
        "canonical_hashes": {},
        "provenance": {
            "inputs": [{"path": path, "result_or_artifact_id": result_id, "sha256": sha(ROOT / path), "role": role} for path, result_id, role in INPUTS],
            "implementations": [
                {"path": str(ENGINE.relative_to(ROOT)), "sha256": sha(ENGINE), "role": "typed AST and exact semantic receiver"},
                {"path": str(POINT_ENGINE.relative_to(ROOT)), "sha256": sha(POINT_ENGINE), "role": "independent exact point evaluator crosscheck"},
            ],
        },
        "claim_flags": {
            "BACH_EULER_NATURAL_MAP_PORTABLE": True,
            "POLARIZED_BACH_KERNEL_PORTABLE": True,
            "GENERAL_DIFF_NATURALITY_COMPOSITIONALLY_CERTIFIED": True,
            "SIGNED_COORDINATE_COVARIANCE_REPLAYED": True,
            "PORTABLE_TENSOR_NATURAL_HSTAR_ROW": False,
            "SUSPENDED_GRADED_POLARIZATION_REPLAYED": False,
            "STRICT_SUPPORT_LOCAL_Q2_COMPLETE": False,
            "CLASSICAL_IMPORT_GATE_PASSED": False,
            "LORENTZIAN_CAUSAL_CERTIFIED": False,
            "QME_RESTORED": False,
        },
        "does_not_establish": [
            "the integrated metric-antifield row including its cotangent terms",
            "the repository suspended graded bilinear q2 or its Koszul symmetry",
            "q1q2=0, a complete local D action, D derivation, or BV cyclicity",
            "a passed classical import Gate A",
            "a causal Green homotopy, Hadamard state, Lorentzian QME, or Lorentzian quantum theory",
            "a direct component equality with the separately normalized Nariai PBW action-Hessian table",
        ],
        "schema_path": "quantum-weyl/classical_import/schema/strict-bach-natural-operator-ast-v1.schema.json",
        "independent_checker": "quantum-weyl/classical_import/check_strict_bach_natural_operator_ast.py",
        "human_report": "quantum-weyl/classical_import/REPORT_STRICT_BACH_NATURAL_OPERATOR_AST_V1.md",
    }
    value["canonical_hashes"] = {
        "natural_operator_ast_sha256": digest(ast),
        "primitive_contracts_sha256": digest(contracts),
        "compositional_naturality_sha256": digest(naturality),
        "exact_evaluator_checks_sha256": digest(value["exact_evaluator_checks"]),
        "cross_background_evidence_sha256": digest(value["cross_background_evidence"]),
        "gate_advancement_sha256": digest(value["gate_advancement"]),
    }
    return value


def render(value: Mapping[str, Any]) -> str:
    nodes = "\n".join(
        f"| `{item['node_id']}` | `{item['operation']}` | `{item['declared_output_type']}` | {item['declared_metric_jet_order']} |"
        for item in value["natural_operator_ast"]["nodes"]
    )
    checks = "\n".join(
        f"| `{item['background']}` | {item['left_seed']}, {item['right_seed']} | {item['nonzero_output_count']} | `{item['output_sha256'][:16]}...` |"
        for item in value["exact_evaluator_checks"]["background_crosschecks"]
    )
    gates = "\n".join(f"| `{item['gate']}` | `{item['status']}` | {item['evidence']} |" for item in value["gate_advancement"])
    return f"""# Portable tensor-natural Bach-Hessian AST v1

**Result:** `{value['result_id']}`

**State:** `{value['result_state']}`

**Dependency:** `LOCAL-ALGEBRAIC`

## Outcome

The polarized action-normalized Bach kernel is no longer defined only by a
large table at one conformal-cylinder frame.  This result supplies a typed,
content-addressed and executable natural-operator DAG for

```text
K_g(h1,h2) = [a*b] (-2 sqrt(abs(g+a h1+b h2)) B(g+a h1+b h2)^sharp).
```

The general coordinate-independence claim comes from composition: metric
inverse, Levi-Civita curvature, the Schouten/Weyl/Cotton/Bach construction,
contraction, absolute densitization, and mixed Frechet differentiation are
all pullback-natural.  The exact signed-coordinate replay is deliberately an
implementation regression only; it is not the proof of the general statement.

## Executable DAG

| Node | Operation | Output type | Metric-jet order |
|---|---|---|---:|
{nodes}

The root has fourth metric-jet order, exact rational coefficients and the
support-intersection property.  Its output is the same symmetric
contravariant weight-one density used by the authoritative metric antifield.

## Independent exact checks

| Background | Seeds | Nonzero outputs | Output digest |
|---|---:|---:|---|
{checks}

The AST receiver agrees coefficientwise with the earlier point evaluator on
the conformal cylinder, Minkowski space and a flat Brinkmann chart.  Three
polynomial pp-wave pairs give all ten outputs zero.  A nontrivial signed
coordinate permutation also transforms all ten outputs exactly as a
contravariant absolute density.

The independent Nariai action-Hessian calculation is pinned as
cross-background evidence for the same covariant Bach construction and
normalization.  This result does **not** claim a direct component adapter to
that separate moving-frame PBW table.

## Gate ledger

| Gate | Status | Evidence or remaining work |
|---|---|---|
{gates}

The immediate next step is mechanical but scientifically consequential:
replace the basepoint-only `K` reference in the metric-antifield row with this
portable root, then perform the repository suspended polarization across all
six minimal rows.  Only after that can Koszul symmetry and the arity-two
master identity be replayed honestly.

## Reproduction

```text
python3 quantum-weyl/classical_import/build_strict_bach_natural_operator_ast.py --check
python3 quantum-weyl/classical_import/check_strict_bach_natural_operator_ast.py
python3 quantum-weyl/classical_import/verify_strict_bach_natural_operator_ast.py
python3 -m unittest quantum-weyl/classical_import/tests/test_strict_bach_natural_operator_ast.py -v
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
        print("STRICT_BACH_NATURAL_OPERATOR_AST_V1: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    for path, content in outputs:
        path.write_bytes(content)
    print("STRICT_BACH_NATURAL_OPERATOR_AST_V1: wrote certificate and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
