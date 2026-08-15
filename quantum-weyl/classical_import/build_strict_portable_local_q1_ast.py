#!/usr/bin/env python3
"""Build the portable Bach-flat strict pure-Weyl local q1 certificate."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from local_q1_bach_flat import (
    DEGREES,
    PARITIES,
    SYMBOLS,
    canonical_ast,
    digest,
    exact_fixture_record,
    standard_backgrounds,
    validate_ast,
)


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_PORTABLE_LOCAL_Q1_AST_V1.json"
REPORT = HERE / "REPORT_STRICT_PORTABLE_LOCAL_Q1_AST_V1.md"
INPUTS = (
    (
        "quantum-weyl/classical_import/certificates/STRICT_BACH_NATURAL_OPERATOR_AST_V1.json",
        "STRICT_BACH_NATURAL_OPERATOR_AST_V1",
        "portable action-normalized Bach Euler map and Hessian parent",
    ),
    (
        "quantum-weyl/classical_import/certificates/STRICT_SIX_ROW_SUSPENDED_Q2_AST_V1.json",
        "STRICT_SIX_ROW_SUSPENDED_Q2_AST_V1",
        "common suspension, grading, and generator convention",
    ),
    (
        "d_quotient_classical/certificates/CLASSICAL_MINIMAL_BV_ANTIFIELD_EXPORT_V2.json",
        "CLASSICAL_MINIMAL_BV_ANTIFIELD_EXPORT_V2",
        "authoritative strict minimal BV Q rows and derived Noether atoms",
    ),
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(relative: str) -> dict[str, Any]:
    return json.loads((ROOT / relative).read_text())


def build() -> dict[str, Any]:
    bach, q2, exported = (load(path) for path, _, _ in INPUTS)
    for value, (_, result_id, _) in zip((bach, q2, exported), INPUTS):
        if value.get("result_id") != result_id:
            raise ValueError(f"dependency drift: {result_id}")
    if bach.get("claim_flags", {}).get("BACH_EULER_NATURAL_MAP_PORTABLE") is not True:
        raise ValueError("portable Bach Euler map unavailable")
    if q2.get("convention") != "suspended-graded-symmetric-factorial-v1":
        raise ValueError("q2 suspension convention drift")

    ast = canonical_ast()
    validate_ast(ast)
    generators = [
        {
            "symbol": symbol,
            "local_tangent_degree": DEGREES[symbol],
            "Grassmann_parity": PARITIES[symbol],
            "q1_output_status": "ZERO" if symbol in ast["zero_output_rows"] else "NONZERO",
        }
        for symbol in SYMBOLS
    ]
    source_symbols = {
        "g": "h",
        "xi": "c",
        "omega": "omega",
        "g_star": "h_star",
        "xi_star": "c_star",
        "omega_star": "omega_star",
    }
    source_by_symbol = {item["symbol"]: item for item in exported["generators"]}
    for source, target in source_symbols.items():
        row = source_by_symbol[source]
        if -row["ghost_number"] != DEGREES[target] or row["Grassmann_parity"] != PARITIES[target]:
            raise ValueError(f"source grading drift: {source}")

    fixtures = [
        exact_fixture_record(
            name,
            background,
            vector_seed=vector_seed,
            scalar_seed=scalar_seed,
            metric_seed=metric_seed,
        )
        for name, background, vector_seed, scalar_seed, metric_seed in standard_backgrounds()
    ]
    proof_checks = [
        {
            "check_id": "q1_component_coverage",
            "status": "VERIFIED",
            "evidence": "five nonzero unary components and the two zero ghost rows cover all six minimal outputs",
        },
        {
            "check_id": "q1_cohomological_degree_one",
            "status": "VERIFIED",
            "evidence": "each nonzero component has degree(output)-degree(input)=1 and odd parity",
        },
        {
            "check_id": "q1_squared_zero",
            "status": "VERIFIED_ON_DECLARED_BACH_FLAT_NATURAL_COMPLEX",
            "evidence": "compositional Diff/Weyl covariance and Noether adjoint identities, with exact independent fixtures on three Bach-flat backgrounds",
        },
        {
            "check_id": "q1_q2_arity_two_nilpotency",
            "status": "NOT_REPLAYED",
            "evidence": "the common arity-two receiver must differentiate all five q1 components against the twenty-two ordered q2 components",
        },
    ]
    value: dict[str, Any] = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "schema": "strict-portable-local-q1-ast-v1",
        "result_id": "STRICT_PORTABLE_LOCAL_Q1_AST_V1",
        "result_kind": "PORTABLE_BACH_FLAT_MINIMAL_BV_UNARY_COMPLEX",
        "result_state": "PORTABLE_Q1_AND_Q1_SQUARED_CERTIFIED_ARITY_TWO_IDENTITY_OPEN",
        "lifecycle": "CLASSIFIED",
        "created": "2026-08-15",
        "repository_base_commit": "b06af47e",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "convention": "suspended-graded-symmetric-factorial-v1",
        "scope": {
            "theory": "strict pure-Weyl minimal Diff x Weyl BV theory",
            "background_class": "smooth nondegenerate four-dimensional Bach-flat pseudo-Riemannian metrics",
            "background_equation": "E_g(gbar)=0",
            "carrier": "compactly supported smooth minimal BV sections with external graded-commutative coefficients",
            "coefficient_field": "Q for exact fixtures; tensor-natural real smooth operator semantics",
            "maximum_input_jet_order": 4,
            "maximum_noether_fixture_metric_jet_order": 5,
            "support_rule": "every unary output support lies in the support of its input",
        },
        "generator_ledger": generators,
        "local_q1_ast": ast,
        "square_zero_theorem": {
            "status": "CERTIFIED",
            "background_hypothesis": "E_g(gbar)=0",
            "compositions": [
                {"source": "c", "intermediate": "h", "target": "h_star", "identity": "B_linear R_diff=0", "result": "ZERO"},
                {"source": "omega", "intermediate": "h", "target": "h_star", "identity": "B_linear R_weyl=0", "result": "ZERO"},
                {"source": "h", "intermediate": "h_star", "target": "c_star", "identity": "N_diff_linear B_linear=0", "result": "ZERO"},
                {"source": "h", "intermediate": "h_star", "target": "omega_star", "identity": "N_weyl_linear B_linear=0", "result": "ZERO"},
                {"source": "h_star", "intermediate": "c_star or omega_star", "target": "zero", "identity": "q1 has no output rows c or omega, equivalently q1(c_star)=q1(omega_star)=0", "result": "ZERO"},
            ],
            "derivation": [
                "The natural Euler density is Diff-equivariant; differentiating at a solution kills infinitesimal Diff gauge directions.",
                "The four-dimensional Weyl action is invariant; differentiating its Euler trace identity at a solution kills infinitesimal Weyl gauge directions.",
                "The formal adjoints of the two gauge maps are the Diff and Weyl Noether operators, so both annihilate the linearized Euler map.",
                "The background field equation is essential: away from the Bach-flat locus the linearized gauge identities acquire Lie or Weyl transport of E_g(gbar).",
            ],
            "exact_fixture_records": fixtures,
        },
        "proof_checks": proof_checks,
        "canonical_hashes": {},
        "provenance": {
            "inputs": [
                {
                    "path": path,
                    "result_or_artifact_id": result_id,
                    "sha256": sha(ROOT / path),
                    "role": role,
                }
                for path, result_id, role in INPUTS
            ],
            "implementation": [
                {
                    "path": "quantum-weyl/classical_import/local_q1_bach_flat.py",
                    "sha256": sha(HERE / "local_q1_bach_flat.py"),
                    "role": "typed AST and exact fixture evaluator",
                }
            ],
        },
        "claim_flags": {
            "PORTABLE_LOCAL_Q1_AST_CERTIFIED": True,
            "Q1_SQUARED_ZERO_CERTIFIED": True,
            "BACH_FLAT_BACKGROUND_HYPOTHESIS_EXPLICIT": True,
            "Q1_Q2_ARITY_TWO_NILPOTENCY_REPLAYED": False,
            "STRICT_FULL_LOCAL_D_ACTION_CERTIFIED": False,
            "BV_CYCLICITY_Q1_REPLAYED": False,
            "STRICT_SUPPORT_LOCAL_Q2_COMPLETE": False,
            "CLASSICAL_IMPORT_GATE_PASSED": False,
            "LORENTZIAN_CAUSAL_CERTIFIED": False,
            "QME_RESTORED": False,
        },
        "does_not_establish": [
            "q1q2=0 or any nonlinear master identity",
            "the local D action, D equivariance, or BV cyclicity",
            "q1 nilpotency away from a Bach-flat background without the corresponding curved/tadpole terms",
            "the complete seven-proof SUPPORT_LOCAL_Q2_EXPORT_CONTRACT",
            "a passed classical import Gate A",
            "a causal Green homotopy, Hadamard state, Lorentzian QME, positivity, or Lorentzian quantum theory",
        ],
        "schema_path": "quantum-weyl/classical_import/schema/strict-portable-local-q1-ast-v1.schema.json",
        "independent_checker": "quantum-weyl/classical_import/check_strict_portable_local_q1_ast.py",
        "human_report": "quantum-weyl/classical_import/REPORT_STRICT_PORTABLE_LOCAL_Q1_AST_V1.md",
    }
    value["canonical_hashes"] = {
        "generator_ledger_sha256": digest(generators),
        "local_q1_ast_sha256": digest(ast),
        "square_zero_theorem_sha256": digest(value["square_zero_theorem"]),
        "proof_checks_sha256": digest(proof_checks),
    }
    return value


def render(value: Mapping[str, Any]) -> str:
    components = "\n".join(
        f"| `{item['component_id']}` | `{item['input']}` | `{item['output']}` | `{item['operator_node']}` |"
        for item in value["local_q1_ast"]["components"]
    )
    fixtures = "\n".join(
        f"| `{item['background']}` | `{item['checks']['background_Bach_flat']}` | `{item['checks']['B_linear_after_R_diff_zero']}` | `{item['checks']['B_linear_after_R_weyl_zero']}` | `{item['checks']['N_diff_linear_after_B_linear_zero']}` | `{item['checks']['N_weyl_linear_after_B_linear_zero']}` |"
        for item in value["square_zero_theorem"]["exact_fixture_records"]
    )
    return f"""# Portable Bach-flat strict local q1 AST v1

**Result:** `{value['result_id']}`

**State:** `{value['result_state']}`

**Dependency:** `LOCAL-ALGEBRAIC`

## Outcome

The strict minimal pure-Weyl unary BV differential is now serialized in the
same suspended convention as the six-row `q2` ledger. It has five nonzero
background-linear components. There are no components whose outputs are the
Diff or Weyl ghost slots, and there are no components taking either ghost-
antifield slot as input. Thus the displayed tangent chain starts with the two
ghost directions and stops after the two ghost-antifield directions.

On the explicitly declared Bach-flat background class, `q1^2=0` is certified
compositionally from naturality and the two Noether identities. An exact
coordinate-jet receiver independently replays every nontrivial composition on
the conformal cylinder, Minkowski space, and flat Brinkmann coordinates. This
is a portable unary theorem, not a claim that the nonlinear arity-two identity
has already been checked.

## Nonzero unary components

| Component | Input | Output | Operator |
|---|---|---|---|
{components}

In tangent-complex direction, the formulas are
`q1(c)=L_c gbar`, `q1(omega)=2 omega gbar`, `q1(h)=B_linear(h)`,
`q1(h_star)=N_diff_linear(h_star)+N_weyl_linear(h_star)`, and
`q1(c_star)=q1(omega_star)=0`. Here `B_linear` is the first Frechet derivative
of the already certified action-normalized natural Bach Euler map. This is the
transpose orientation of the BRST vector field acting on coordinate
functions, so the direction is stated explicitly to avoid conflating them.

## Exact square-zero fixtures

| Background | Bach-flat | Diff gauge | Weyl gauge | Diff Noether | Weyl Noether |
|---|---|---|---|---|---|
{fixtures}

These finite fixtures are regression witnesses. Generality comes from the
typed natural maps and the differentiated covariance/Noether identities, not
from extrapolating three coordinate examples.

## Why Bach-flat matters

At a solution, differentiating Diff and Weyl covariance gives
`B_linear R_diff=0` and `B_linear R_weyl=0`. Away from a solution those
compositions contain transport or Weyl rescaling of `E_g(gbar)`. The present
unary complex therefore does not silently claim an off-shell background
complex.

## Next gate

The exact next calculation is `[q1,q2]=0`. It must differentiate all five unary
components against the twenty-two ordered components in
`STRICT_SIX_ROW_SUSPENDED_Q2_AST_V1`, including the Bach Hessian and both
Noether variations. The certificate keeps that flag false.

## Reproduction

```text
PYTHONPATH=quantum-weyl/classical_import python3 quantum-weyl/classical_import/build_strict_portable_local_q1_ast.py --check
PYTHONPATH=quantum-weyl/classical_import python3 quantum-weyl/classical_import/check_strict_portable_local_q1_ast.py
PYTHONPATH=quantum-weyl/classical_import python3 quantum-weyl/classical_import/verify_strict_portable_local_q1_ast.py
python3 -m unittest quantum-weyl/classical_import/tests/test_strict_portable_local_q1_ast.py -v
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
    stale = [
        str(path.relative_to(ROOT))
        for path, content in outputs
        if not path.is_file() or path.read_bytes() != content
    ]
    if args.check:
        print(
            "STRICT_PORTABLE_LOCAL_Q1_AST_V1: "
            + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale))
        )
        return bool(stale)
    for path, content in outputs:
        path.write_bytes(content)
    print("STRICT_PORTABLE_LOCAL_Q1_AST_V1: wrote certificate and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
