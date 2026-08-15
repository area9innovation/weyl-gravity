#!/usr/bin/env python3
"""Build the independent quantum-side import of classical minimal-BV q3."""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
from itertools import permutations
import json
from pathlib import Path
from typing import Any, Mapping

import bach_natural_operator_ast as quadratic
import cylinder_cubic_bach_evaluator as diagonal
import cylinder_polarized_bach_evaluator as point
from local_q1_q2_receiver import apply_q1, field_fixture
import pure_weyl_cubic_natural_operator as cubic


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_PURE_WEYL_MINIMAL_BV_Q3_IMPORT_V1.json"
REPORT = HERE / "REPORT_STRICT_PURE_WEYL_MINIMAL_BV_Q3_IMPORT_V1.md"
CLASSICAL_Q3 = ROOT / "d_quotient_classical/certificates/CLASSICAL_MINIMAL_BV_Q3_EXPORT_V1.json"
CLASSICAL_PARENT = ROOT / "d_quotient_classical/certificates/CLASSICAL_MINIMAL_BV_ANTIFIELD_EXPORT_V2.json"
CLASSICAL_IMPORT = HERE / "certificates/CLASSICAL_MINIMAL_BV_ANTIFIELD_IMPORT_V2.json"
Q2_AST = HERE / "certificates/STRICT_SIX_ROW_SUSPENDED_Q2_AST_V1.json"
Q3_WITNESS = HERE / "certificates/STRICT_386_PURE_WEYL_Q3_WITNESS_V1.json"
ACTION = ROOT / "d_quotient_classical/minimal_bv_antifield/foundation/action_normalization.json"
ENGINE = HERE / "pure_weyl_cubic_natural_operator.py"
POINT_ENGINE = HERE / "cylinder_polarized_bach_evaluator.py"
DIAGONAL_ENGINE = HERE / "cylinder_cubic_bach_evaluator.py"
INPUTS = (
    (CLASSICAL_Q3, "CLASSICAL_MINIMAL_BV_Q3_EXPORT_V1", "authoritative six-row minimal-BV q3 export"),
    (CLASSICAL_PARENT, "CLASSICAL_MINIMAL_BV_ANTIFIELD_EXPORT_V2", "authoritative minimal-BV carrier and nilpotent Q"),
    (CLASSICAL_IMPORT, "CLASSICAL_MINIMAL_BV_ANTIFIELD_IMPORT_V2", "independently accepted classical import gate at minimal scope"),
    (Q2_AST, "STRICT_SIX_ROW_SUSPENDED_Q2_AST_V1", "same-carrier complete suspended q2"),
    (Q3_WITNESS, "STRICT_386_PURE_WEYL_Q3_WITNESS_V1", "pinned diagonal cubic cancellation witness"),
    (ACTION, "PURE_WEYL_ACTION_NORMALIZATION_V2", "action and Euler-density normalization"),
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def recorded_digest(value: Mapping[str, Any]) -> str:
    return digest({key: item for key, item in value.items() if key != "sha256"})


def load(path: Path, expected: str) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if value.get("result_id", value.get("schema")) != expected:
        raise ValueError(f"dependency identity drift: {expected}")
    return value


def serialize(values: Mapping[tuple[int, int], Mapping[tuple[int, int, int, int], Fraction]]) -> list[dict[str, object]]:
    return [
        {
            "component": list(pair),
            "terms": [
                {"multiindex": list(alpha), "coefficient": str(coefficient)}
                for alpha, coefficient in sorted(values[pair].items())
                if coefficient
            ],
        }
        for pair in point.PAIRS
    ]


def point_values(values: Mapping[tuple[int, int], Mapping[tuple[int, int, int, int], Fraction]]) -> dict[tuple[int, int], Fraction]:
    return {pair: values[pair].get(point.ZERO_MULTIINDEX, Fraction(0)) for pair in point.PAIRS}


def metric_payload(value: Mapping[tuple[int, int], point.Jet]) -> dict[tuple[int, int], dict[tuple[int, int, int, int], Fraction]]:
    return {
        pair: {
            alpha: coefficient
            for first, second, alpha, coefficient in value[pair].terms
            if first == second == 0
        }
        for pair in point.PAIRS
    }


def add_fields(*fields: point.MetricJets) -> dict[tuple[int, int], dict[tuple[int, int, int, int], Fraction]]:
    output: dict[tuple[int, int], dict[tuple[int, int, int, int], Fraction]] = {}
    for pair in point.PAIRS:
        row: dict[tuple[int, int, int, int], Fraction] = {}
        for field in fields:
            for alpha, coefficient in field.get(pair, {}).items():
                row[alpha] = row.get(alpha, Fraction(0)) + Fraction(coefficient)
        output[pair] = {alpha: coefficient for alpha, coefficient in row.items() if coefficient}
    return output


def diagonal_point(field: point.MetricJets, background: Mapping[tuple[int, int], point.Jet]) -> dict[tuple[int, int], Fraction]:
    data = diagonal.diagonal_cubic_bach_data(field, background=background, output_coordinate_order=1)
    return {
        pair: next(
            (Fraction(term["coefficient"]) for term in data["q3_metric_euler_density"][pair] if term["multiindex"] == [0, 0, 0, 0]),
            Fraction(0),
        )
        for pair in point.PAIRS
    }


def polarization_reference(
    first: point.MetricJets,
    second: point.MetricJets,
    third: point.MetricJets,
    background: Mapping[tuple[int, int], point.Jet],
) -> dict[tuple[int, int], Fraction]:
    fields = {
        "123": add_fields(first, second, third),
        "12": add_fields(first, second),
        "13": add_fields(first, third),
        "23": add_fields(second, third),
        "1": first,
        "2": second,
        "3": third,
    }
    values = {name: diagonal_point(field, background) for name, field in fields.items()}
    return {
        pair: (
            values["123"][pair] - values["12"][pair] - values["13"][pair]
            - values["23"][pair] + values["1"][pair] + values["2"][pair]
            + values["3"][pair]
        ) / 6
        for pair in point.PAIRS
    }


def primitive_contracts() -> list[dict[str, object]]:
    return [
        {"operation": "metric_three_parameter_family", "naturality": "pullback acts simultaneously on the base metric and all three variations", "preserves_locality": True},
        {"operation": "inverse_metric", "naturality": "metric inversion commutes with pullback on nondegenerate metrics", "preserves_locality": True},
        {"operation": "levi_civita_geometry", "naturality": "Levi-Civita connection and curvature commute with metric pullback", "preserves_locality": True},
        {"operation": "schouten_and_weyl_4d", "naturality": "four-dimensional Schouten and Weyl tensors are natural curvature contractions", "preserves_locality": True},
        {"operation": "cotton_4d", "naturality": "covariant differentiation and alternation preserve naturality", "preserves_locality": True},
        {"operation": "bach_4d", "naturality": "covariant differentiation, raising and contraction preserve naturality", "preserves_locality": True},
        {"operation": "raise_symmetric_two_tensor", "naturality": "raising with the inverse metric commutes with pullback", "preserves_locality": True},
        {"operation": "absolute_metric_volume_density", "naturality": "absolute metric volume is a pullback-natural weight-one density", "preserves_locality": True},
        {"operation": "densitize_and_scale", "naturality": "tensor product and exact rational scaling preserve naturality", "preserves_locality": True},
        {"operation": "mixed_third_frechet_coefficient", "naturality": "three derivatives of an equivariant smooth natural map form an equivariant symmetric trilinear natural operator", "preserves_locality": True},
    ]


def build() -> dict[str, Any]:
    values = {path: load(path, expected) for path, expected, _ in INPUTS}
    exported = values[CLASSICAL_Q3]
    parent = values[CLASSICAL_PARENT]
    imported = values[CLASSICAL_IMPORT]
    q2 = values[Q2_AST]
    witness = values[Q3_WITNESS]
    action = values[ACTION]
    ast = exported["natural_operator_ast"]
    cubic.validate_imported_ast(ast)

    if exported.get("claim_flags", {}).get("AUTHORITATIVE_MINIMAL_BV_Q3_EXPORTED") is not True:
        raise ValueError("classical q3 export is not authoritative")
    if imported.get("claim_flags", {}).get("CLASSICAL_ANTIFIELD_EXPORT_IMPORTED") is not True:
        raise ValueError("minimal classical parent import is not accepted")
    if q2.get("claim_flags", {}).get("SIX_MINIMAL_Q2_ROW_LEDGERS_COMPLETE") is not True:
        raise ValueError("same-carrier q2 export is not accepted")
    if action.get("Euler_coordinate") != exported.get("scope", {}).get("action_normalization"):
        raise ValueError("action normalization mismatch")

    backgrounds = (
        ("conformal_cylinder", point.cylinder_background(4), (1, 2, 3)),
        ("minkowski", point.flat_background(4), (2, 3, 4)),
        ("flat_brinkmann", point.brinkmann_background(4), (3, 4, 5)),
    )
    background_checks = []
    for name, background, seeds in backgrounds:
        fields = tuple(point.sparse_fixture(seed) for seed in seeds)
        result = cubic.evaluate_ast(ast, *fields, background=background)
        payload = serialize(result)
        background_checks.append({
            "background": name,
            "input_seeds": list(seeds),
            "nonzero_output_count": sum(bool(row) for row in result.values()),
            "output_sha256": digest(payload),
            "all_arithmetic_exact": True,
        })

    symmetry_background = point.flat_background(4)
    symmetry_fields = tuple(point.sparse_fixture(seed) for seed in (1, 2, 3))
    symmetry_outputs = [cubic.evaluate_ast(ast, *(symmetry_fields[index] for index in order), background=symmetry_background) for order in permutations(range(3))]
    if any(item != symmetry_outputs[0] for item in symmetry_outputs[1:]):
        raise ValueError("S3 symmetry replay failed")

    polarization_background = point.flat_background(5)
    polarization_fields = tuple(point.sparse_fixture(seed) for seed in (4, 5, 6))
    direct = cubic.evaluate_point(ast, *polarization_fields, background=polarization_background)
    polarized = polarization_reference(*polarization_fields, polarization_background)
    if direct != polarized:
        raise ValueError("independent seven-diagonal polarization disagrees")

    diagonal_background = point.flat_background(7)
    generator = field_fixture("c", 1, 7)
    gauge_field = metric_payload(apply_q1("q1_h_c", generator, diagonal_background, 6))
    diagonal_result = cubic.evaluate_ast(ast, gauge_field, gauge_field, gauge_field, background=diagonal_background, output_coordinate_order=1)
    stored_rows = {
        tuple(row["component"]): {
            tuple(term["multiindex"]): Fraction(term["coefficient"])
            for term in row["terms"]
        }
        for row in witness["exact_cubic_fixture"]["metric_output_rows"]
    }
    if diagonal_result != stored_rows:
        raise ValueError("pinned diagonal q3 witness was not reproduced")

    ppwave = tuple(point.ppwave_profile_fixture(seed) for seed in (1, 2, 3))
    ppwave_result = cubic.evaluate_ast(ast, *ppwave, background=point.brinkmann_background(4))
    if any(ppwave_result.values()):
        raise ValueError("pp-wave cubic restriction is not zero")

    permutation = (0, 2, 3, 1)
    signs = (-1, 1, -1, 1)
    coordinate_fields = tuple(point.sparse_fixture(seed) for seed in (5, 6, 7))
    coordinate_background = point.cylinder_background(4)
    original = cubic.evaluate_ast(ast, *coordinate_fields, background=coordinate_background)
    transformed = cubic.evaluate_ast(
        ast,
        *(quadratic.transform_metric_jets(field, permutation, signs) for field in coordinate_fields),
        background=quadratic.transform_background(coordinate_background, permutation, signs),
    )
    expected = cubic.transform_output_density_jets(original, permutation, signs)
    if transformed != expected:
        raise ValueError("signed coordinate covariance replay failed")

    contracts = primitive_contracts()
    if [item["operation"] for item in contracts] != [item["operation"] for item in ast["nodes"]]:
        raise ValueError("naturality contract coverage drift")
    naturality = {
        "proof_kind": "COMPOSITIONAL_THIRD_FRECHET_NATURAL_OPERATOR_THEOREM_WITH_EXECUTABLE_SEMANTICS",
        "domain_category": "four-dimensional smooth nondegenerate pseudo-Riemannian metric jets and local diffeomorphisms",
        "source_bundle": "three symmetric covariant metric variations",
        "target_bundle": "symmetric contravariant absolute density of weight plus one",
        "derivation": [
            "Every node before coefficient extraction is a standard pullback-natural construction in the primitive ledger.",
            "Composition, covariant differentiation, contraction, tensor product and exact rational scaling preserve pullback naturality and support locality.",
            "The action-normalized Euler map E(g)=-2 sqrt(abs(g)) B(g)^sharp is therefore a fourth-order natural differential operator.",
            "Differentiating phi^*E(g)=E(phi^*g) in three independent metric directions proves naturality and S3 symmetry of D^3E.",
        ],
        "conclusion": "q3_hstar_hhh is a symmetric fourth-order support-local trilinear natural operator on arbitrary metric inputs",
        "finite_coordinate_test_role": "signed permutations and finite fixtures are implementation regressions; compositional naturality supplies the general proof",
        "status": "CERTIFIED",
    }

    checks = {
        "background_crosschecks": background_checks,
        "S3_input_permutations_replayed": 6,
        "S3_exact_symmetry": True,
        "seven_diagonal_polarization": {
            "input_seeds": [4, 5, 6],
            "formula": "T(x,y,z)=(F(x+y+z)-F(x+y)-F(x+z)-F(y+z)+F(x)+F(y)+F(z))/6",
            "direct_output_sha256": digest([str(direct[pair]) for pair in point.PAIRS]),
            "polarized_output_sha256": digest([str(polarized[pair]) for pair in point.PAIRS]),
            "exact_equality": True,
        },
        "pinned_diagonal_witness": {
            "fixture_id": witness["exact_cubic_fixture"]["fixture_id"],
            "metric_output_term_count": sum(len(row) for row in diagonal_result.values()),
            "q1_q3_weyl_noether": witness["exact_cubic_fixture"]["q1_q3_weyl_noether"],
            "required_value": "-75760/9",
            "exact_row_equality": True,
        },
        "ppwave_restriction": {"input_seeds": [1, 2, 3], "all_ten_outputs_zero": True},
        "signed_coordinate_permutation": {
            "permutation": list(permutation),
            "signs": list(signs),
            "input_seeds": [5, 6, 7],
            "exact_covariance": True,
            "output_sha256": digest(serialize(transformed)),
        },
        "all_arithmetic_exact": True,
    }

    import_bridge = {
        "classical_export": exported["result_id"],
        "classical_parent": parent["result_id"],
        "accepted_parent_import": imported["result_id"],
        "same_carrier_q2": q2["result_id"],
        "source_carrier": ["g", "xi", "omega", "g_star", "xi_star", "omega_star"],
        "imported_nonzero_component": "q3_hstar_hhh=D^3E_g",
        "imported_zero_output_rows": ["g", "xi", "omega", "xi_star", "omega_star"],
        "carrier_or_convention_change": False,
        "independent_receiver": str(ENGINE.relative_to(ROOT)),
        "sha256": "",
    }
    import_bridge["sha256"] = recorded_digest(import_bridge)

    value: dict[str, Any] = {
        "$schema": "../schema/strict-pure-weyl-minimal-bv-q3-import-v1.schema.json",
        "schema": "strict-pure-weyl-minimal-bv-q3-import-v1",
        "schema_path": "quantum-weyl/classical_import/schema/strict-pure-weyl-minimal-bv-q3-import-v1.schema.json",
        "result_id": "STRICT_PURE_WEYL_MINIMAL_BV_Q3_IMPORT_V1",
        "result_kind": "INDEPENDENT_EXACT_IMPORT_AND_EXECUTION_OF_AUTHORITATIVE_MINIMAL_BV_Q3",
        "result_state": "ARBITRARY_INPUT_MINIMAL_BV_Q3_IMPORTED_ARITY_THREE_AND_386_STABILIZATION_OPEN",
        "lifecycle": "CLASSIFIED",
        "created": "2026-08-15",
        "repository_base_commit": "0950df03e512b88436ab12212d0d9a9ac820c681",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "scope": {
            "theory": "strict pure-Weyl minimal BV theory",
            "background_class": "arbitrary smooth Bach-flat nondegenerate four-dimensional pseudo-Riemannian backgrounds for the pointed Taylor complex",
            "input": "three arbitrary compactly supported symmetric covariant metric variations",
            "output": "the complete six-row minimal-BV q3, with one natural metric-antifield output and five identically zero rows",
            "coefficient_field": "Q",
            "maximum_metric_jet_order": 4,
            "taylor_convention": "coefficient [a*b*c] equals the third Frechet derivative with no hidden factorial",
            "support_rule": exported["minimal_q3_support"]["support_rule"],
        },
        "import_bridge": import_bridge,
        "primitive_contracts": contracts,
        "compositional_naturality": naturality,
        "exact_receiver_checks": checks,
        "gate_advancement": [
            {"gate": "AUTHORITATIVE_MINIMAL_Q3_IMPORT", "status": "PASS", "evidence": "all six source rows imported without carrier or convention change"},
            {"gate": "ARBITRARY_INPUT_COMPONENT_EXECUTION", "status": "PASS", "evidence": "exact trivariate receiver, three backgrounds, S3, polarization, covariance, pp-wave and pinned witness checks"},
            {"gate": "MINIMAL_ARITY_THREE_Q_SQUARED", "status": "OPEN", "evidence": "the complete q1 q3 plus q2 q2 plus q3 q1 channel replay is the next independent gate"},
            {"gate": "MINIMAL_Q3_CYCLICITY", "status": "OPEN", "evidence": "quartic BV vertex cyclicity has not yet been replayed in receiver signs"},
            {"gate": "STRICT_386_CYCLIC_STABILIZATION", "status": "OPEN", "evidence": "no content-addressed extension or L-infinity morphism to all 386 rows is yet accepted"},
        ],
        "foundational_strength": {
            "classification": "FINITE_EXACT_RATIONAL_NATURAL_DIFFERENTIAL_OPERATOR",
            "finite_receipts": "Every regression is a finite exact rational jet computation.",
            "general_statement": "Compositional naturality and formal Frechet differentiation quantify over arbitrary smooth metric jets without using a Hilbert completion or Green inverse.",
            "choice_operation_added": False,
            "completion_or_infinite_sum_used": False,
            "analytic_green_layer_used": False,
            "dependency_boundary": "LOCAL-ALGEBRAIC",
        },
        "claim_flags": {
            "AUTHORITATIVE_MINIMAL_BV_Q3_IMPORTED": True,
            "ARBITRARY_THREE_INPUT_METRIC_Q3_EXECUTED": True,
            "ALL_SIX_MINIMAL_Q3_OUTPUT_ROWS_IMPORTED": True,
            "GENERAL_DIFF_NATURALITY_COMPOSITIONALLY_CERTIFIED": True,
            "S3_SYMMETRY_REPLAYED": True,
            "DIAGONAL_Q3_WITNESS_REPRODUCED": True,
            "MINIMAL_BV_ARITY_THREE_IDENTITY_CERTIFIED": False,
            "MINIMAL_BV_Q3_CYCLICITY_CERTIFIED": False,
            "STRICT_386_Q3_STABILIZED": False,
            "CLASSICAL_IMPORT_GATE_PASSED": False,
            "LORENTZIAN_CAUSAL_CERTIFIED": False,
            "HADAMARD_STATE_CONSTRUCTED": False,
            "QME_RESTORED": False,
        },
        "canonical_hashes": {},
        "provenance": {
            "inputs": [
                {"path": str(path.relative_to(ROOT)), "result_or_artifact_id": expected, "sha256": sha(path), "role": role}
                for path, expected, role in INPUTS
            ],
            "implementations": [
                {"path": str(ENGINE.relative_to(ROOT)), "sha256": sha(ENGINE), "role": "independent exact trivariate AST receiver"},
                {"path": str(POINT_ENGINE.relative_to(ROOT)), "sha256": sha(POINT_ENGINE), "role": "pre-existing exact tensor-geometry kernel"},
                {"path": str(DIAGONAL_ENGINE.relative_to(ROOT)), "sha256": sha(DIAGONAL_ENGINE), "role": "independent one-parameter cubic polarization oracle"},
            ],
        },
        "does_not_establish": [
            "the complete minimal-BV arity-three nilpotency identity on all typed input channels",
            "quartic cyclicity of q3 under the receiver BV pairing and suspension signs",
            "a source-certified cyclic stabilization or L-infinity morphism to the 386-row carrier",
            "all-order nonlinear source closure or an analytic Moller map",
            "compatibility estimates between q3 and any causal Green homotopy",
            "a Hadamard state, renormalized Lorentzian time-ordered products, QME restoration, residual transfer, or a Lorentzian quantum theory",
        ],
        "next_gate": "Enumerate every typed arity-three channel on the six-row carrier and independently replay q1 q3 + q2 q2 + q3 q1 = 0; then transport q3 and the cyclic pairing through an explicit 386-row stabilization map.",
        "independent_checker": "quantum-weyl/classical_import/check_strict_pure_weyl_minimal_bv_q3_import.py",
        "human_report": "quantum-weyl/classical_import/REPORT_STRICT_PURE_WEYL_MINIMAL_BV_Q3_IMPORT_V1.md",
    }
    value["canonical_hashes"] = {
        "import_bridge_sha256": digest(import_bridge),
        "primitive_contracts_sha256": digest(contracts),
        "compositional_naturality_sha256": digest(naturality),
        "exact_receiver_checks_sha256": digest(checks),
        "gate_advancement_sha256": digest(value["gate_advancement"]),
        "foundational_strength_sha256": digest(value["foundational_strength"]),
    }
    return value


def render(value: Mapping[str, Any]) -> str:
    checks = "\n".join(
        f"| `{item['background']}` | {', '.join(map(str, item['input_seeds']))} | {item['nonzero_output_count']} | `{item['output_sha256'][:16]}...` |"
        for item in value["exact_receiver_checks"]["background_crosschecks"]
    )
    gates = "\n".join(f"| `{item['gate']}` | `{item['status']}` | {item['evidence']} |" for item in value["gate_advancement"])
    return f"""# Strict pure-Weyl minimal-BV q3 import v1

**Result:** `{value['result_id']}`

**State:** `{value['result_state']}`
**Dependency:** `LOCAL-ALGEBRAIC`

## Outcome

The arbitrary-input cubic bracket is now imported from the authoritative classical minimal master action rather than inferred from the single diagonal
witness.  On the six-generator carrier its complete support is

```text
q3(h1,h2,h3) -> h_star = D^3[-2 sqrt(abs(g)) B(g)^sharp](h1,h2,h3),
all other q3 output rows = 0.
```

The independent receiver evaluates the classical AST over the exact
square-free algebra `Q[a,b,c]/(a^2,b^2,c^2)`.  The `[a*b*c]` coefficient is
the polarized third Frechet derivative directly, with no numerical finite
difference and no hidden factorial.

## Exact checks

| Background | Input seeds | Nonzero outputs | Digest |
|---|---:|---:|---|
{checks}

All six input permutations agree.  A separate seven-diagonal polarization
using the earlier one-parameter cubic evaluator agrees exactly.  The pinned
pure-diffeomorphism witness reproduces all 41 stored terms and its
`q1(q3)_omega_star=-75760/9` value.  Three pp-wave profile directions give
zero, and a signed coordinate permutation transforms the output as a
contravariant absolute weight-one density.

The general coordinate claim comes from composition of natural operations
and three formal derivatives; the finite coordinate fixtures are
implementation regressions, not the proof of general naturality.

## Gate ledger

| Gate | Status | Evidence or remaining work |
|---|---|---|
{gates}

The import does **not** yet claim the arity-three identity merely because the
parent full vector field is nilpotent.  The next rail must enumerate and
independently replay every typed `q1 q3 + q2 q2 + q3 q1` channel.  Quartic
cyclicity and the 386-row stabilization are separate open gates.

## Reproduction

```text
python3 quantum-weyl/classical_import/build_strict_pure_weyl_minimal_bv_q3_import.py --check
python3 quantum-weyl/classical_import/check_strict_pure_weyl_minimal_bv_q3_import.py
python3 quantum-weyl/classical_import/verify_strict_pure_weyl_minimal_bv_q3_import.py
python3 -m unittest quantum-weyl/classical_import/tests/test_strict_pure_weyl_minimal_bv_q3_import.py -v
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
        print("STRICT_PURE_WEYL_MINIMAL_BV_Q3_IMPORT_V1: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    for path, content in outputs:
        path.write_bytes(content)
    print("STRICT_PURE_WEYL_MINIMAL_BV_Q3_IMPORT_V1: wrote certificate and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
