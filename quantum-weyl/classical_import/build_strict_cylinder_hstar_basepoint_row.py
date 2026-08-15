#!/usr/bin/env python3
"""Build the exact homogeneous-cylinder metric-antifield q2 row assembly."""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_CYLINDER_HSTAR_BASEPOINT_ROW_V1.json"
REPORT = HERE / "REPORT_STRICT_CYLINDER_HSTAR_BASEPOINT_ROW_V1.md"
INPUTS = (
    ("quantum-weyl/classical_import/certificates/STRICT_CYLINDER_BACH_UNIVERSAL_EXPORT_V1.json", "STRICT_CYLINDER_BACH_UNIVERSAL_EXPORT_V1", "exact polarized metric Euler-density table"),
    ("quantum-weyl/classical_import/certificates/STRICT_Q2_KINEMATIC_COTANGENT_AST_V1.json", "STRICT_Q2_KINEMATIC_COTANGENT_AST_V1", "five-row diagonal q2 package and tangent conventions"),
    ("d_quotient_classical/certificates/CLASSICAL_MINIMAL_BV_ANTIFIELD_EXPORT_V2.json", "CLASSICAL_MINIMAL_BV_ANTIFIELD_EXPORT_V2", "authoritative g-star Q row and tensor type"),
    ("quantum-weyl/classical_import/certificates/CLASSICAL_MINIMAL_BV_ANTIFIELD_IMPORT_V2.json", "CLASSICAL_MINIMAL_BV_ANTIFIELD_IMPORT_V2", "independent replay of the classical antifield export"),
    ("d_quotient_classical/minimal_bv_antifield/foundation/action_normalization.json", "PURE_WEYL_ACTION_NORMALIZATION_V2", "action, Euler-density and minimal-master-term normalization"),
)
PAIRS = tuple((mu, nu) for mu in range(4) for nu in range(mu, 4))
DIFF_FORMULA = "c^rho partial_rho h_star^{mu nu} - h_star^{rho nu} partial_rho c^mu - h_star^{mu rho} partial_rho c^nu + (partial_rho c^rho) h_star^{mu nu}"
WEYL_FORMULA = "-2 omega h_star^{mu nu}"
HESSIAN_FORMULA = "(1/2) K^{mu nu}[h,h]"
ROW_FORMULA = "q2_diagonal(h_star)^{mu nu}=(1/2)K^{mu nu}[h,h]+Lie_c(h_star)^{mu nu}-2 omega h_star^{mu nu}"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(payload).hexdigest()


def load(relative: str) -> dict[str, Any]:
    return json.loads((ROOT / relative).read_text())


def compact_apply(table: Mapping[str, Any], values: Mapping[tuple[int, int], Mapping[tuple[int, ...], Fraction]]) -> dict[tuple[int, int], Fraction]:
    basis = table["input_basis"]
    coefficients = [Fraction(value) for value in table["coefficient_dictionary"]]

    def coefficient(basis_id: int) -> Fraction:
        item = basis[basis_id]
        return Fraction(values.get(tuple(item["component_pair"]), {}).get(tuple(item["word"]), 0))

    output: dict[tuple[int, int], Fraction] = {}
    for row in table["rows"]:
        total = Fraction(0)
        for left, right, coefficient_id in row["symmetric_bilinear_entries"]:
            factor = coefficients[coefficient_id]
            total += factor * coefficient(left) * coefficient(right)
            if left != right:
                total += factor * coefficient(right) * coefficient(left)
        output[tuple(row["output_pair"])] = total / 2
    return output


def sparse_metric_fixture(seed: int) -> dict[tuple[int, int], dict[tuple[int, ...], Fraction]]:
    words = ((0, 0, 0, 0), (1, 0, 0, 0), (0, 1, 1, 0), (0, 0, 0, 3), (1, 1, 1, 1))
    result: dict[tuple[int, int], dict[tuple[int, ...], Fraction]] = {}
    for component, pair in enumerate(PAIRS):
        jets: dict[tuple[int, ...], Fraction] = {}
        for index, word in enumerate(words):
            numerator = ((seed + 2 * component + 3 * index) % 11) - 5
            if numerator:
                jets[word] = Fraction(numerator, seed + component + index + 2)
        if jets:
            result[pair] = jets
    return result


def cotangent_fixture(seed: int) -> tuple[dict[tuple[int, int], Fraction], dict[tuple[tuple[int, int], int], Fraction], dict[int, Fraction], dict[tuple[int, int], Fraction], Fraction]:
    p = {pair: Fraction(((seed + 3 * index) % 13) - 6, seed + index + 2) for index, pair in enumerate(PAIRS)}
    dp = {(pair, rho): Fraction(((2 * seed + 5 * index + rho) % 17) - 8, seed + index + rho + 3) for index, pair in enumerate(PAIRS) for rho in range(4)}
    c = {rho: Fraction(((seed + 4 * rho) % 9) - 4, seed + rho + 2) for rho in range(4)}
    dc = {(upper, lower): Fraction(((3 * seed + 2 * upper + 5 * lower) % 19) - 9, seed + upper + lower + 3) for upper in range(4) for lower in range(4)}
    omega = Fraction(seed - 3, seed + 5)
    return p, dp, c, dc, omega


def sym(values: Mapping[tuple[int, int], Fraction], left: int, right: int) -> Fraction:
    return values[(min(left, right), max(left, right))]


def dsym(values: Mapping[tuple[tuple[int, int], int], Fraction], left: int, right: int, derivative: int) -> Fraction:
    return values[((min(left, right), max(left, right)), derivative)]


def direct_lie(pair: tuple[int, int], fixture: tuple[dict, dict, dict, dict, Fraction]) -> Fraction:
    mu, nu = pair
    p, dp, c, dc, _ = fixture
    return (
        sum(c[rho] * dsym(dp, mu, nu, rho) for rho in range(4))
        - sum(sym(p, rho, nu) * dc[(mu, rho)] for rho in range(4))
        - sum(sym(p, mu, rho) * dc[(nu, rho)] for rho in range(4))
        + sum(dc[(rho, rho)] * sym(p, mu, nu) for rho in range(4))
    )


def negative_euler_from_diff_master(pair: tuple[int, int], fixture: tuple[dict, dict, dict, dict, Fraction]) -> Fraction:
    """Negative h-Euler derivative of integral h_star L_c h."""
    mu, nu = pair
    p, dp, c, dc, _ = fixture
    transport_adjoint = sum(
        dsym(dp, mu, nu, rho) * c[rho] + sym(p, mu, nu) * dc[(rho, rho)]
        for rho in range(4)
    )
    index_adjoint = (
        sum(sym(p, rho, nu) * dc[(mu, rho)] for rho in range(4))
        + sum(sym(p, mu, rho) * dc[(nu, rho)] for rho in range(4))
    )
    return transport_adjoint - index_adjoint


def build() -> dict[str, Any]:
    universal, partial, exported, imported, normalization = (load(path) for path, _, _ in INPUTS)
    for value, (_, result_id, _) in zip((universal, partial, exported, imported, normalization), INPUTS):
        if value.get("result_id", value.get("schema")) != result_id:
            raise ValueError(f"provenance result drift: {result_id}")
    if universal.get("result_state") != "UNIVERSAL_CYLINDER_TABLE_AND_DIFF_IDENTITY_CERTIFIED_GLOBAL_AST_OPEN":
        raise ValueError("universal table boundary drift")
    if partial.get("claim_flags", {}).get("SIXTH_METRIC_ANTIFIELD_ROW_PORTABLE") is not False:
        raise ValueError("partial q2 boundary was silently promoted")
    if imported.get("independent_replay", {}).get("status") != "EXECUTABLE_V2_EXPORT_INDEPENDENTLY_REPLAYED":
        raise ValueError("antifield receiver replay drift")
    if imported["independent_replay"]["canonical_hashes"] != exported["canonical_hashes"]:
        raise ValueError("source/receiver antifield hashes disagree")
    source_row = next(row for row in exported["differential"]["Q"]["rows"] if row["source_atom"] == "g_star")
    expected_terms = [
        {"coefficient": -2, "factors": ["omega", "g_star"]},
        {"coefficient": 1, "factors": ["E_g"]},
        {"coefficient": 1, "factors": ["Lie_g_star"]},
    ]
    if source_row["image"]["terms"] != expected_terms:
        raise ValueError("authoritative g-star Q row drift")
    if normalization.get("Euler_coordinate") != "E_g^{mu nu}:=delta S/delta g_{mu nu}=-2 sqrt(abs(g)) B^{mu nu}":
        raise ValueError("Euler-density normalization drift")
    if normalization.get("minimal_master_terms", [None])[0] != "integral g_star^{mu nu}(L_xi g_{mu nu}+2 omega g_{mu nu})":
        raise ValueError("metric master term drift")

    cotangent_checks = []
    for seed in (1, 2, 5):
        fixture = cotangent_fixture(seed)
        direct = [direct_lie(pair, fixture) for pair in PAIRS]
        adjoint = [negative_euler_from_diff_master(pair, fixture) for pair in PAIRS]
        if direct != adjoint:
            raise ValueError(f"Diff cotangent variational replay failed at seed {seed}")
        p, _, _, _, omega = fixture
        weyl_direct = [(-2) * omega * p[pair] for pair in PAIRS]
        weyl_negative_euler = [-2 * omega * p[pair] for pair in PAIRS]
        if weyl_direct != weyl_negative_euler:
            raise ValueError(f"Weyl cotangent variational replay failed at seed {seed}")
        cotangent_checks.append({
            "seed": seed,
            "diff_output_sha256": digest([str(item) for item in direct]),
            "weyl_output_sha256": digest([str(item) for item in weyl_direct]),
            "negative_euler_equals_declared_cotangent": True,
        })

    table = universal["universal_table"]
    diagonal_checks = []
    for seed in (1, 3, 5):
        diagonal = compact_apply(table, sparse_metric_fixture(seed))
        serialized = [str(diagonal[pair]) for pair in PAIRS]
        diagonal_checks.append({
            "seed": seed,
            "quadratic_diagonal_output": serialized,
            "output_sha256": digest(serialized),
            "coefficient_relative_to_polarized_table": "1/2",
        })

    components = [
        {
            "component_id": "q2_hstar_hh_basepoint",
            "inputs": ["h", "h"],
            "operator": "K_cylinder_basepoint",
            "coefficient": "1/2",
            "coordinate_formula": HESSIAN_FORMULA,
            "maximum_input_jet_orders": [4, 4],
            "maximum_total_derivative_order": 4,
            "source_atom": "E_g",
            "support_rule": "output support is contained in the intersection of both metric-input supports",
            "portability": "HOMOGENEOUS_BASEPOINT_ONLY",
        },
        {
            "component_id": "q2_hstar_chstar",
            "inputs": ["c", "h_star"],
            "operator": "contravariant_density_lie_transport",
            "coefficient": "1",
            "coordinate_formula": DIFF_FORMULA,
            "maximum_input_jet_orders": [1, 1],
            "maximum_total_derivative_order": 1,
            "source_atom": "Lie_g_star",
            "support_rule": "output support is contained in the intersection of the ghost and metric-antifield supports",
            "portability": "TENSOR_NATURAL",
        },
        {
            "component_id": "q2_hstar_omegahstar",
            "inputs": ["omega", "h_star"],
            "operator": "weyl_metric_antifield_product",
            "coefficient": "-2",
            "coordinate_formula": WEYL_FORMULA,
            "maximum_input_jet_orders": [0, 0],
            "maximum_total_derivative_order": 0,
            "source_atom": "omega*g_star",
            "support_rule": "output support is contained in the intersection of the Weyl-ghost and metric-antifield supports",
            "portability": "TENSOR_NATURAL",
        },
    ]
    source_crosswalk = {
        "authoritative_Q_g_star_terms": expected_terms,
        "source_canonical_hashes": exported["canonical_hashes"],
        "receiver_canonical_hashes": imported["independent_replay"]["canonical_hashes"],
        "metric_antifield_tensor_type": next(item for item in exported["generators"] if item["symbol"] == "g_star")["tensor_type"],
        "Euler_coordinate": normalization["Euler_coordinate"],
        "minimal_metric_master_term": normalization["minimal_master_terms"][0],
        "BV_antifield_coordinate_rule": "Q(g_star) is minus the h-Euler derivative of the metric gauge master terms, after integration by parts",
    }
    gates = [
        {"gate": "HSTAR_BASEPOINT_DIAGONAL_ASSEMBLY", "status": "PASS", "evidence": "all three source-fixed terms are serialized; the exact Hessian factor 1/2 and cotangent signs are replayed"},
        {"gate": "TENSOR_NATURAL_GLOBALIZATION", "status": "OPEN", "evidence": "the K term remains a one-frame component table without an SO(4)-isotropy/coordinate-change certificate"},
        {"gate": "DIFFERENTIATED_DIFF_NOETHER", "status": "PASS", "evidence": "all four background, unary and quadratic fifth-jet coordinate rows cancel in the universal engine and three independent point probes"},
        {"gate": "SUSPENDED_GRADED_POLARIZATION", "status": "OPEN", "evidence": "this artifact fixes the diagonal Taylor row, not the repository suspended bilinear sign convention"},
        {"gate": "SIX_ROW_INTERACTION_IDENTITIES", "status": "OPEN", "evidence": "q1q2=0, Koszul symmetry, D derivation and BV cyclicity await a portable six-row payload"},
    ]
    value: dict[str, Any] = {
        "schema": "strict-cylinder-hstar-basepoint-row-v1",
        "result_id": "STRICT_CYLINDER_HSTAR_BASEPOINT_ROW_V1",
        "result_kind": "EXACT_HOMOGENEOUS_BASEPOINT_DIAGONAL_TAYLOR_ROW_ASSEMBLY",
        "result_state": "HSTAR_BASEPOINT_ROW_AND_DIFF_IDENTITY_ASSEMBLED_PORTABLE_GLOBALIZATION_AND_POLARIZATION_OPEN",
        "lifecycle": "CLASSIFIED",
        "created": "2026-08-15",
        "repository_base_commit": "1b4b9350",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "scope": {
            "theory": "strict pure-Weyl minimal Diff x Weyl BV theory",
            "background": "unit conformal cylinder R x S3",
            "basepoint_chart": universal["scope"]["basepoint_chart"],
            "output": {"symbol": "h_star", "component_count": 10, "tensor_type": source_crosswalk["metric_antifield_tensor_type"], "form_degree": 4, "Weyl_weight": -2},
            "coefficient_field": "Q",
            "diagonal_Taylor_convention": "the epsilon^2 coefficient in Q(gbar+epsilon h, epsilon c, epsilon omega, epsilon h_star, ...); it is not yet the suspended bilinear q2",
            "row_formula": ROW_FORMULA,
            "metric_kernel_boundary": "K is exact and exhaustive only at the declared homogeneous frame; both cotangent terms are tensor-natural on arbitrary charts",
            "support_locality": "all three components are finite local differential products and contain no inverse differential operator",
        },
        "source_crosswalk": source_crosswalk,
        "components": components,
        "universal_table_reference": {
            "result_id": universal["result_id"],
            "universal_table_sha256": universal["canonical_hashes"]["universal_table_sha256"],
            "input_basis_count": table["counts"]["input_basis"],
            "symmetric_bilinear_term_count": table["counts"]["symmetric_bilinear_terms"],
            "polarized_coefficient_convention": universal["scope"]["taylor_convention"],
            "diagonal_Taylor_multiplier": "1/2",
        },
        "exact_checks": {
            "source_and_receiver_antifield_hashes_agree": True,
            "authoritative_g_star_row_replayed": True,
            "three_diff_and_weyl_variational_cotangent_checks": cotangent_checks,
            "three_exact_hessian_diagonal_checks": diagonal_checks,
            "all_component_coefficients_exact_rationals": True,
            "all_components_support_local": True,
        },
        "gates": gates,
        "canonical_hashes": {},
        "provenance": {"inputs": [{"path": path, "result_or_artifact_id": result_id, "sha256": sha(ROOT / path), "role": role} for path, result_id, role in INPUTS]},
        "claim_flags": {
            "HSTAR_BASEPOINT_DIAGONAL_ROW_ASSEMBLED": True,
            "METRIC_ANTIFIELD_DIFF_COTANGENT_TERM_CERTIFIED": True,
            "METRIC_ANTIFIELD_WEYL_COTANGENT_TERM_CERTIFIED": True,
            "PORTABLE_TENSOR_NATURAL_HSTAR_ROW": False,
            "DIFFERENTIATED_DIFF_NOETHER_REPLAYED": True,
            "SUSPENDED_GRADED_POLARIZATION_REPLAYED": False,
            "STRICT_SUPPORT_LOCAL_Q2_COMPLETE": False,
            "CLASSICAL_IMPORT_GATE_PASSED": False,
            "LORENTZIAN_CAUSAL_CERTIFIED": False,
            "QME_RESTORED": False,
        },
        "missing_object_ledger": [
            {"object": "SO(4)-isotropy-covariant globalization of K", "status": "MISSING", "blocks": "portable h-star row"},
            {"object": "suspended graded bilinear polarization of all six rows", "status": "MISSING", "blocks": "Koszul symmetry and complete q2 receiver"},
            {"object": "full local D action and common BV pairing replay", "status": "MISSING", "blocks": "D derivation, cyclicity and Gate A"},
        ],
        "does_not_establish": [
            "a coordinate-independent or SO(4)-isotropy-covariant globalization of the metric Hessian table",
            "the complete arity-two master identity beyond the now-certified differentiated Diff Noether row",
            "the repository suspended graded bilinear q2 or its Koszul symmetry",
            "a portable complete six-row support-local q2 or complete local D action",
            "BV cyclicity on a common support-local pairing or a passed classical import Gate A",
            "a Lorentzian causal Green homotopy, Hadamard state, restored QME, or Lorentzian quantum theory",
        ],
        "independent_checker": "quantum-weyl/classical_import/check_strict_cylinder_hstar_basepoint_row.py",
        "human_report": "quantum-weyl/classical_import/REPORT_STRICT_CYLINDER_HSTAR_BASEPOINT_ROW_V1.md",
    }
    value["canonical_hashes"] = {
        "source_crosswalk_sha256": digest(source_crosswalk),
        "components_sha256": digest(components),
        "exact_checks_sha256": digest(value["exact_checks"]),
        "gates_sha256": digest(gates),
        "missing_object_ledger_sha256": digest(value["missing_object_ledger"]),
    }
    return value


def render(value: Mapping[str, Any]) -> str:
    components = "\n".join(
        f"| `{item['component_id']}` | `{', '.join(item['inputs'])}` | `{item['coefficient']}` | `{item['portability']}` | {item['coordinate_formula']} |"
        for item in value["components"]
    )
    gates = "\n".join(f"| `{item['gate']}` | `{item['status']}` | {item['evidence']} |" for item in value["gates"])
    missing = "\n".join(f"| {item['object']} | `{item['status']}` | {item['blocks']} |" for item in value["missing_object_ledger"])
    return f"""# Strict cylinder metric-antifield basepoint row v1

**Result:** `{value['result_id']}`

**State:** `{value['result_state']}`

**Dependency:** `LOCAL-ALGEBRAIC`

## Outcome

The sixth strict minimal-BV diagonal Taylor row is now assembled at the
declared homogeneous cylinder frame:

```text
{value['scope']['row_formula']}
```

The exact classical export fixes `Q(g_star)=E_g+Lie_c(g_star)-2 omega g_star`.
The universal table stores the coefficient of `a*b`, hence the diagonal
`epsilon^2` coefficient is **one half** of `K[h,h]`. Both cotangent signs are
also recovered independently as minus the metric Euler derivative of the two
metric gauge master terms, including the density-divergence contribution.

This is real progress past a missing-row placeholder, but it is deliberately a
**basepoint assembly**, not a portable six-row `q2`: the large `K` table still
needs tensor-natural globalization and suspended graded polarization. The
separate universal fifth-jet calculation now certifies all four differentiated
Diff Noether rows exactly.

## Three components

| Component | Inputs | Coefficient | Portability | Formula |
|---|---|---:|---|---|
{components}

## Gate ledger

| Gate | Status | Evidence or missing proof |
|---|---|---|
{gates}

## Missing-object ledger

| Object | Status | Blocks |
|---|---|---|
{missing}

## Independent replay

The fast receiver checks the authoritative source row and the independent
classical-import hashes, re-derives the complete contravariant-density Lie
formula from the negative variational adjoint, replays the Weyl sign, evaluates
three exact diagonal Hessian fixtures with the factor `1/2`, pins the universal
table hash, and rejects every stronger lifecycle flag.

```text
python3 quantum-weyl/classical_import/build_strict_cylinder_hstar_basepoint_row.py --check
python3 quantum-weyl/classical_import/check_strict_cylinder_hstar_basepoint_row.py
python3 quantum-weyl/classical_import/verify_strict_cylinder_hstar_basepoint_row.py
python3 -m unittest quantum-weyl/classical_import/tests/test_strict_cylinder_hstar_basepoint_row.py -v
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
        print("STRICT_CYLINDER_HSTAR_BASEPOINT_ROW_V1: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    for path, content in outputs:
        path.write_bytes(content)
    print("STRICT_CYLINDER_HSTAR_BASEPOINT_ROW_V1: wrote certificate and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
