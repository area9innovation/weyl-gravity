#!/usr/bin/env python3
"""Build the exact benchmark contract for the missing polarized Bach kernel."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_POLARIZED_BACH_KERNEL_BENCHMARK_V1.json"
REPORT = HERE / "REPORT_STRICT_POLARIZED_BACH_KERNEL_BENCHMARK_V1.md"
INPUTS = (
    ("covariant_completion/certificates/linearized_bach.json", "LINEARIZED_BACH_CYLINDER", "cylinder action normalization and exhaustive unary jet controls"),
    ("quantum-weyl/transfer/certificates/HT1B_LOCAL_BACH_SEED_LIFT.json", "HT1B_LOCAL_BACH_SEED_LIFT", "two nonzero mode-specialized local cylinder channels"),
    ("quantum-weyl/transfer/certificates/HT1B_DIRECT_CURVATURE_AUDIT.json", "HT1B_DIRECT_CURVATURE_AUDIT", "independent direct-curvature probe evaluation"),
    ("bridge/certificates/ppwave_bach_branch_closure.json", "PPWAVE_BACH_BRANCH_CLOSURE", "arbitrary-profile exact nonlinear zero slice"),
    ("d_quotient_classical/certificates/NARIAI_TRANSVERSE_ACTION_BACH_HESSIAN_VARIATION_V1.json", "NARIAI_TRANSVERSE_ACTION_BACH_HESSIAN_VARIATION_V1", "complete restricted-background Hessian-variation method fixture"),
    ("d_quotient_classical/certificates/CLASSICAL_MINIMAL_BV_ANTIFIELD_EXPORT_V2.json", "CLASSICAL_MINIMAL_BV_ANTIFIELD_EXPORT_V2", "authoritative metric-antifield tensor type"),
    ("quantum-weyl/classical_import/certificates/STRICT_Q2_KINEMATIC_COTANGENT_AST_V1.json", "STRICT_Q2_KINEMATIC_COTANGENT_AST_V1", "five-row partial q2 export and open h-star boundary"),
)


def load(path: str) -> dict[str, Any]:
    return json.loads((ROOT / path).read_text())


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def _source_checks() -> tuple[dict[str, Any], ...]:
    linear, lift, direct, ppwave, nariai, antifield, partial = (load(path) for path, _, _ in INPUTS)
    if linear.get("category") != "natural local operators on the conformal cylinder":
        raise ValueError("linearized cylinder Bach source drift")
    if linear.get("construction") != "B_lin=-2[nabla^c nabla^d C_1(acbd)+(1/2)Ric^{cd}C_1(acbd)]":
        raise ValueError("linearized Bach formula drift")
    if lift.get("result_id") != INPUTS[1][1] or lift.get("result_state") != "LOCAL_METRIC_SEEDS_COMPUTED_FULL_BV_LIFT_BLOCKED":
        raise ValueError("HT1B seed source drift")
    if direct.get("result_id") != INPUTS[2][1] or direct["checks"].get("arbitrary_input_bilinear_bach_tensor") != "NOT_COMPUTED":
        raise ValueError("direct-curvature audit boundary drift")
    if ppwave.get("result_id") != INPUTS[3][1] or not ppwave["restricted_nonlinear_tensor"].get("q2_identically_zero_for_arbitrary_ppwave_profiles"):
        raise ValueError("pp-wave exact zero slice drift")
    if nariai.get("result_id") != INPUTS[4][1] or not nariai["exact_checks"].get("lower_completion_unique_all_rows"):
        raise ValueError("Nariai Hessian-variation source drift")
    generators = {item["symbol"]: item for item in antifield.get("generators", [])}
    if generators.get("g_star", {}).get("tensor_type", {}).get("symmetry") != "symmetric_contravariant_density":
        raise ValueError("metric-antifield output type drift")
    if partial.get("result_id") != INPUTS[6][1] or partial["claim_flags"].get("SIXTH_METRIC_ANTIFIELD_ROW_PORTABLE"):
        raise ValueError("partial q2 boundary drift")
    return linear, lift, direct, ppwave, nariai, antifield, partial


def build() -> dict[str, Any]:
    linear, lift, direct, ppwave, nariai, antifield, partial = _source_checks()
    channels = [
        {
            "channel_id": item["channel_id"],
            "external_modes": item["external_modes"],
            "bilinear_taylor_convention": item["bilinear_taylor_convention"],
            "local_radial_density": item["local_radial_density"],
            "integrated_taub_charge": item["integrated_taub_charge"],
            "raw_residual_kernel_entry": item["raw_residual_kernel_entry"],
            "canonical_residual_kernel_entry": item["canonical_residual_kernel_entry"],
        }
        for item in lift["seed_payload"]["direct_local_channels"]
    ]
    probes = [
        {
            "side": item["side"],
            "reverse": item["reverse"],
            "probe": item["probe"],
            "local_radial_density": item["local_radial_density"],
            "integrated_action_coefficient": item["integrated_action_coefficient"],
        }
        for item in direct["direct_probe_results"]
    ]
    nariai_direct = nariai["exact_data"]["direct_action_leading_derivation"]
    nariai_full = nariai["exact_data"]["identified_full_action_variation"]
    nariai_noether = nariai["exact_data"]["lower_order_noether_completion"]
    gstar = next(item for item in antifield["generators"] if item["symbol"] == "g_star")

    fixtures = [
        {
            "fixture_id": "CYLINDER_LINEARIZED_ACTION_NORMALIZATION",
            "evidence_class": "UNARY_FORMULA_AND_EXHAUSTIVE_JET_CONTROL",
            "background": "conformal cylinder R x S3",
            "input_scope": "arbitrary metric one-jet through differential order four",
            "expected": {
                "construction": linear["construction"],
                "normalization": linear["normalization"],
                "gauge_maximum_order": linear["gauge_jet_test"]["maximum_order"],
                "principal_maximum_order": linear["principal_jet_test"]["maximum_order"],
                "principal_tracefree_components": linear["principal_jet_test"]["tracefree_input_components"],
            },
            "acceptance_role": "fixes the unary convention and fourth-order principal normalization used by the same geometric pipeline",
            "cannot_establish": "any quadratic coefficient of the arbitrary-input polarized kernel",
            "dependency_tags": ["LOCAL-ALGEBRAIC"],
        },
        {
            "fixture_id": "CYLINDER_HT1B_NONZERO_MODE_CHANNELS",
            "evidence_class": "NONZERO_MODE_SPECIALIZED_LOCAL_DENSITY_AND_INTEGRATED_PROJECTION",
            "background": "conformal cylinder R x S3 in a stereographic radial chart",
            "input_scope": "two named mixed E/A/L mode pairs, not arbitrary-support inputs",
            "expected": {"channel_count": len(channels), "channels": channels},
            "acceptance_role": "detects a zero or wrongly normalized nonlinear evaluator on two independent physical channels",
            "cannot_establish": "the unprojected ten-component tensor or any untested coefficient",
            "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        },
        {
            "fixture_id": "CYLINDER_DIRECT_CURVATURE_PROBES",
            "evidence_class": "DIRECT_EXACT_CURVATURE_PROBES",
            "background": "conformal cylinder R x S3 in a stereographic radial chart",
            "input_scope": "six forward slice/gauge probes and two reverse slice probes for the two HT1B channels",
            "expected": {"probe_count": len(probes), "probes": probes},
            "acceptance_role": "independently reevaluates local curvature densities and distinguishes nonzero slice currents from vanishing integrated gauge probes",
            "cannot_establish": "arbitrary-input completeness or reverse local densities without reverse gauge probes",
            "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        },
        {
            "fixture_id": "PPWAVE_ARBITRARY_PROFILE_ZERO_SLICE",
            "evidence_class": "ARBITRARY_PROFILE_RESTRICTED_NONLINEAR_ZERO",
            "background": ppwave["geometry"]["metric"],
            "input_scope": ppwave["geometry"]["support_scope"],
            "expected": {
                "taylor_convention": ppwave["restricted_nonlinear_tensor"]["Taylor_convention"],
                "q2_entries": ppwave["restricted_nonlinear_tensor"]["q2_entries"],
                "all_higher_taylor_coefficients_zero": ppwave["restricted_nonlinear_tensor"]["all_higher_Taylor_coefficients_zero"],
            },
            "acceptance_role": "rejects spurious nonlinear terms on an infinite-dimensional exact slice",
            "cannot_establish": "any nonaligned interaction coefficient or complete BV q2",
            "dependency_tags": ["LOCAL-ALGEBRAIC"],
        },
        {
            "fixture_id": "NARIAI_TRANSVERSE_HESSIAN_VARIATION",
            "evidence_class": "RESTRICTED_BACKGROUND_COMPLETE_HESSIAN_VARIATION",
            "background": nariai_direct["background"],
            "input_scope": nariai_direct["tangent"],
            "expected": {
                "action_normalization": nariai_direct["action_normalization"],
                "orders_above_two_absent": nariai_direct["orders_above_two_absent"],
                "authoritative_order_two_sha256": nariai_direct["authoritative_order_two"]["sha256"],
                "full_variation_sha256": nariai_full["sha256"],
                "full_variation_nonzero_coefficients": nariai_full["nonzero_coefficients"],
                "coefficient_map_shape": nariai_noether["coefficient_map_shape"],
                "coefficient_map_rank": nariai_noether["coefficient_map_rank"],
                "unique_completion": nariai_noether["unique_completion"],
            },
            "acceptance_role": "cross-background method benchmark for direct leading derivation plus differentiated-Noether completion",
            "cannot_establish": "the cylinder kernel, a rank-310 SDR, or causal transfer",
            "dependency_tags": ["LOCAL-ALGEBRAIC"],
        },
    ]

    pipeline = [
        {"order": 1, "operation": "metric_inverse", "output": "g^ab", "maximum_metric_jet_order": 0},
        {"order": 2, "operation": "levi_civita_connection", "output": "Gamma^a_bc", "maximum_metric_jet_order": 1},
        {"order": 3, "operation": "curvature", "output": "R^a_bcd, Ric_ab, R", "maximum_metric_jet_order": 2},
        {"order": 4, "operation": "weyl_tensor", "output": "C_abcd", "maximum_metric_jet_order": 2},
        {"order": 5, "operation": "bach_standard", "output": "B_standard_ab=nabla^c nabla^d C_acbd+(1/2)Ric^cd C_acbd", "maximum_metric_jet_order": 4},
        {"order": 6, "operation": "action_normalize", "output": "B_action_ab=-2 B_standard_ab", "maximum_metric_jet_order": 4},
        {"order": 7, "operation": "raise_and_densitize", "output": "E^ab=sqrt(-g) g^(a mu) g^(b nu) B_action_munu", "maximum_metric_jet_order": 4},
        {"order": 8, "operation": "polarized_coefficient", "output": "K^ab[h1,h2]=coefficient of a*b in E^ab(gbar+a h1+b h2)", "maximum_metric_jet_order": 4},
    ]
    gates = [
        {"gate_id": "TYPE_AND_EXACTNESS", "requirement": "ten symmetric contravariant density outputs with exact rational/algebraic coefficients and no floats", "status": "NOT_RUN_NO_GENERAL_EVALUATOR"},
        {"gate_id": "ARBITRARY_INPUT_COMPLETENESS", "requirement": "all 10 x 10 unordered metric-component input pairs and all coefficient jets through total differential order four are addressable", "status": "NOT_RUN_NO_GENERAL_EVALUATOR"},
        {"gate_id": "POLARIZATION_SYMMETRY", "requirement": "K[h1,h2]=K[h2,h1] under the declared coefficient-of-a*b convention", "status": "NOT_RUN_NO_GENERAL_EVALUATOR"},
        {"gate_id": "SUPPORT_INTERSECTION", "requirement": "the local bidifferential AST contains no inverse differential operator and obeys supp K(u,v) subset supp(u) intersection supp(v)", "status": "NOT_RUN_NO_GENERAL_EVALUATOR"},
        {"gate_id": "DIFFERENTIATED_WEYL_IDENTITY", "requirement": "the twice-polarized identity derived from g_ab E^ab(g)=0 vanishes, including the two unary cross terms", "status": "NOT_RUN_NO_GENERAL_EVALUATOR"},
        {"gate_id": "DIFFERENTIATED_DIFF_NOETHER_IDENTITY", "requirement": "the twice-polarized covariant-divergence identity vanishes with connection and density variations retained", "status": "NOT_RUN_NO_GENERAL_EVALUATOR"},
        {"gate_id": "CYLINDER_UNARY_NORMALIZATION", "requirement": "the shared pipeline reproduces the exhaustive action-normalized linearized cylinder operator", "status": "NOT_RUN_NO_GENERAL_EVALUATOR"},
        {"gate_id": "PPWAVE_ZERO_SLICE", "requirement": "the evaluator returns zero for arbitrary aligned pp-wave profile pairs before projection", "status": "NOT_RUN_NO_GENERAL_EVALUATOR"},
        {"gate_id": "HT1B_NONZERO_CHANNELS", "requirement": "mode adapters and exact S3 integration reproduce both nonzero local-density/Taub channels", "status": "NOT_RUN_NO_GENERAL_EVALUATOR"},
        {"gate_id": "NARIAI_PORTABILITY", "requirement": "a background-generic implementation reproduces the restricted Nariai Hessian-variation hash; cylinder-only implementations must mark this NOT_APPLICABLE, never PASS", "status": "NOT_RUN_NO_GENERAL_EVALUATOR"},
    ]
    value: dict[str, Any] = {
        "schema": "strict-polarized-bach-kernel-benchmark-v1",
        "result_id": "STRICT_POLARIZED_BACH_KERNEL_BENCHMARK_V1",
        "result_kind": "EXACT_MULTI_FIXTURE_ACCEPTANCE_CONTRACT",
        "result_state": "BENCHMARK_CONTRACT_CERTIFIED_GENERAL_KERNEL_ABSENT",
        "lifecycle": "CLASSIFIED",
        "created": "2026-08-15",
        "repository_base_commit": "99d4020850ef9cd394a5cfd9e1001228f430e2e2",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "question": "What exact evidence can falsify a candidate arbitrary-input polarized second Bach evaluator, and what remains missing after all existing fixtures are combined?",
        "answer": "Five complementary fixture classes constrain normalization, nonzero projections, direct local densities, an infinite-dimensional exact zero slice, and a complete restricted-background Hessian variation. They are a strong falsification suite but do not reconstruct the general cylinder tensor. The missing object is still an exact arbitrary-input, support-local, ten-output symmetric contravariant density K^ab[h1,h2] through metric-jet order four, together with differentiated Diff/Weyl identities.",
        "target_contract": {
            "theory": "strict pure-Weyl minimal Diff x Weyl BV theory",
            "background": "unit conformal cylinder R x S3",
            "inputs": "two arbitrary compactly supported smooth symmetric covariant metric perturbations h1_ab and h2_ab",
            "taylor_convention": "coefficient of a*b in E(gbar+a*h1+b*h2), with no hidden factor of 1/2",
            "action_normalization": "B_action=-2 B_standard",
            "output": {"symbol": "h_star", "component_count": 10, "tensor_type": gstar["tensor_type"], "form_degree": gstar["form_degree"], "Weyl_weight": gstar["Weyl_weight"]},
            "maximum_metric_jet_order": 4,
            "support_rule": "supp K(h1,h2) subset supp(h1) intersection supp(h2) for compact inputs",
            "coefficient_policy": "exact rational or algebraic arithmetic only; numeric approximation is a distinct non-certifying type",
        },
        "candidate_program_contract": pipeline,
        "fixture_ledger": fixtures,
        "acceptance_gates": gates,
        "coverage_diagnosis": {
            "fixture_count": len(fixtures),
            "cylinder_fixture_count": 3,
            "nonzero_cylinder_channel_count": len(channels),
            "direct_curvature_probe_count": len(probes),
            "arbitrary_profile_zero_slices": 1,
            "restricted_complete_hessian_variations": 1,
            "general_arbitrary_input_cylinder_tensor_available": False,
            "why_not_reconstructible": [
                "two projected nonzero mode channels do not determine ten tensor outputs over all fourth-order input jets",
                "a zero theorem on the aligned pp-wave slice contains no information about nonaligned coefficients",
                "the Nariai result varies one fixed tangent in a nine-row transverse frame on a different background",
                "the unary cylinder operator fixes first variation and normalization, not the second variation",
            ],
        },
        "implementation_stages": [
            {"stage": "P0_BIVARIATE_EXACT_JETS", "deliverable": "exact a,b coefficient algebra with coordinate derivatives through order four", "status": "OPEN"},
            {"stage": "P1_CYLINDER_GEOMETRIC_PIPELINE", "deliverable": "executable inverse/connection/curvature/Weyl/Bach/raise-density pipeline at a homogeneous cylinder chart", "status": "OPEN"},
            {"stage": "P2_LOCAL_IDENTITIES", "deliverable": "independent polarization, differentiated Weyl and Diff Noether replays", "status": "OPEN"},
            {"stage": "P3_PHYSICAL_FIXTURE_ADAPTERS", "deliverable": "pp-wave restriction and HT1B mode/integration adapters", "status": "OPEN"},
            {"stage": "P4_PORTABLE_AST_EXPORT", "deliverable": "content-addressed tensor-natural component payload consumable by the strict q2 receiver", "status": "OPEN"},
        ],
        "canonical_hashes": {},
        "provenance": {"inputs": [{"path": path, "result_or_artifact_id": result_id, "sha256": sha(ROOT / path), "role": role} for path, result_id, role in INPUTS]},
        "claim_flags": {
            "MULTI_FIXTURE_BENCHMARK_CONTRACT_CERTIFIED": True,
            "GENERAL_ARBITRARY_INPUT_CYLINDER_BACH_KERNEL_AVAILABLE": False,
            "STRICT_HSTAR_Q2_ROW_PORTABLE": False,
            "STRICT_SUPPORT_LOCAL_Q2_COMPLETE": False,
            "CLASSICAL_IMPORT_GATE_PASSED": False,
            "LORENTZIAN_CAUSAL_CERTIFIED": False,
            "QME_RESTORED": False,
        },
        "does_not_establish": [
            "the arbitrary-input polarized second Bach tensor on the conformal cylinder",
            "a portable h-star q2 component row or complete six-row support-local q2",
            "polarization symmetry or differentiated Diff/Weyl identities for a candidate evaluator",
            "that the reduced-mode HT1B channels determine unprojected local coefficients",
            "that the pp-wave zero slice constrains nonaligned nonlinear interactions",
            "that the Nariai transverse variation is a cylinder or open-background theorem",
            "a passed classical import gate, causal Green homotopy, Hadamard state, restored QME, or Lorentzian quantum theory",
        ],
        "independent_checker": "quantum-weyl/classical_import/check_strict_polarized_bach_benchmark.py",
        "human_report": "quantum-weyl/classical_import/REPORT_STRICT_POLARIZED_BACH_KERNEL_BENCHMARK_V1.md",
    }
    value["canonical_hashes"] = {
        "target_contract_sha256": digest(value["target_contract"]),
        "candidate_program_contract_sha256": digest(pipeline),
        "fixture_ledger_sha256": digest(fixtures),
        "acceptance_gates_sha256": digest(gates),
        "coverage_diagnosis_sha256": digest(value["coverage_diagnosis"]),
        "implementation_stages_sha256": digest(value["implementation_stages"]),
    }
    return value


def render(value: dict[str, Any]) -> str:
    fixtures = "\n".join(
        f"| `{item['fixture_id']}` | `{item['evidence_class']}` | {item['acceptance_role']} | {item['cannot_establish']} |"
        for item in value["fixture_ledger"]
    )
    gates = "\n".join(f"| `{item['gate_id']}` | `{item['status']}` | {item['requirement']} |" for item in value["acceptance_gates"])
    pipeline = "\n".join(f"{item['order']}. **`{item['operation']}`** → `{item['output']}`" for item in value["candidate_program_contract"])
    stages = "\n".join(f"| `{item['stage']}` | `{item['status']}` | {item['deliverable']} |" for item in value["implementation_stages"])
    return f"""# Strict polarized Bach-kernel benchmark v1

**Result:** `{value['result_id']}`

**State:** `{value['result_state']}`

**Dependencies:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`

## Outcome

{value['answer']}

This distinction matters: a candidate that returns zero passes the pp-wave
slice but fails the two nonzero cylinder channels; a mode-table replay passes
those channels but fails arbitrary-input completeness; and a cylinder-only
program cannot claim the Nariai portability gate. No existing result is being
silently promoted into the missing tensor.

## Target object

The target is the coefficient of `a*b` in the action Euler density

```text
E^ab(gbar + a h1 + b h2),
E^ab = sqrt(-g) g^(a mu) g^(b nu) B_action_munu,
B_action = -2 B_standard.
```

It has ten symmetric contravariant density outputs, accepts two arbitrary
compactly supported symmetric metric perturbations, uses metric jets through
order four, and must obey the support-intersection rule. The coefficient-of-
`a*b` convention contains no hidden factor of `1/2`.

## Existing falsification fixtures

| Fixture | Evidence class | What it can test | What it cannot establish |
|---|---|---|---|
{fixtures}

## Candidate geometric program

{pipeline}

The program is a construction contract, not a claim that these operations
have already been serialized or evaluated for arbitrary inputs.

## Fail-closed acceptance gates

| Gate | Current state | Required evidence |
|---|---|---|
{gates}

In particular, the nonlinear Weyl identity is not a naive trace-free test.
Twice differentiating `g_ab E^ab(g)=0` also produces two cross terms involving
the unary Bach operator. The Diff identity likewise retains variations of the
connection and density. Both must be replayed in their differentiated form.

## Construction sequence

| Stage | State | Deliverable |
|---|---|---|
{stages}

## Reproduction

```text
python3 quantum-weyl/classical_import/build_strict_polarized_bach_benchmark.py --check
python3 quantum-weyl/classical_import/check_strict_polarized_bach_benchmark.py
python3 quantum-weyl/classical_import/verify_strict_polarized_bach_benchmark.py
python3 -m unittest quantum-weyl/classical_import/tests/test_strict_polarized_bach_benchmark.py -v
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
        print("STRICT_POLARIZED_BACH_KERNEL_BENCHMARK_V1: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    for path, content in outputs:
        path.write_bytes(content)
    print("STRICT_POLARIZED_BACH_KERNEL_BENCHMARK_V1: wrote certificate and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
