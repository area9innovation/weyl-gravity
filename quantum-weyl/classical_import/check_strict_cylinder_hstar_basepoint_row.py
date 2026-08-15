#!/usr/bin/env python3
"""Independent fast receiver for the cylinder metric-antifield basepoint row."""
from __future__ import annotations

from fractions import Fraction
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_CYLINDER_HSTAR_BASEPOINT_ROW_V1.json"
UNIVERSAL = HERE / "certificates/STRICT_CYLINDER_BACH_UNIVERSAL_EXPORT_V1.json"
EXPORT = ROOT / "d_quotient_classical/certificates/CLASSICAL_MINIMAL_BV_ANTIFIELD_EXPORT_V2.json"
IMPORT = HERE / "certificates/CLASSICAL_MINIMAL_BV_ANTIFIELD_IMPORT_V2.json"
NORMALIZATION = ROOT / "d_quotient_classical/minimal_bv_antifield/foundation/action_normalization.json"
PAIRS = tuple((mu, nu) for mu in range(4) for nu in range(mu, 4))
DIFF_FORMULA = "c^rho partial_rho h_star^{mu nu} - h_star^{rho nu} partial_rho c^mu - h_star^{mu rho} partial_rho c^nu + (partial_rho c^rho) h_star^{mu nu}"
ROW_FORMULA = "q2_diagonal(h_star)^{mu nu}=(1/2)K^{mu nu}[h,h]+Lie_c(h_star)^{mu nu}-2 omega h_star^{mu nu}"
FALSE_FLAGS = {
    "PORTABLE_TENSOR_NATURAL_HSTAR_ROW",
    "SUSPENDED_GRADED_POLARIZATION_REPLAYED",
    "STRICT_SUPPORT_LOCAL_Q2_COMPLETE",
    "CLASSICAL_IMPORT_GATE_PASSED",
    "LORENTZIAN_CAUSAL_CERTIFIED",
    "QME_RESTORED",
}


def _module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


UNIVERSAL_CHECK = _module("strict_cylinder_universal_upstream_check", HERE / "check_strict_cylinder_bach_universal_export.py")
POINT = _module("strict_cylinder_hstar_point_engine", HERE / "cylinder_polarized_bach_evaluator.py")


def digest(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(payload).hexdigest()


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def metric_fixture(seed: int) -> dict[tuple[int, int], dict[tuple[int, ...], Fraction]]:
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


def compact_diagonal(table: Mapping[str, Any], values: Mapping) -> dict[tuple[int, int], Fraction]:
    basis = table["input_basis"]
    rational = [Fraction(item) for item in table["coefficient_dictionary"]]

    def at(basis_id: int) -> Fraction:
        item = basis[basis_id]
        return Fraction(values.get(tuple(item["component_pair"]), {}).get(tuple(item["word"]), 0))

    output = {}
    for row in table["rows"]:
        polarized = Fraction(0)
        for left, right, coefficient_id in row["symmetric_bilinear_entries"]:
            term = rational[coefficient_id] * at(left) * at(right)
            polarized += term if left == right else 2 * term
        output[tuple(row["output_pair"])] = polarized / 2
    return output


def cotangent_fixture(seed: int) -> tuple[dict, dict, dict, dict, Fraction]:
    p = {pair: Fraction(((seed + 3 * index) % 13) - 6, seed + index + 2) for index, pair in enumerate(PAIRS)}
    dp = {(pair, rho): Fraction(((2 * seed + 5 * index + rho) % 17) - 8, seed + index + rho + 3) for index, pair in enumerate(PAIRS) for rho in range(4)}
    c = {rho: Fraction(((seed + 4 * rho) % 9) - 4, seed + rho + 2) for rho in range(4)}
    dc = {(upper, lower): Fraction(((3 * seed + 2 * upper + 5 * lower) % 19) - 9, seed + upper + lower + 3) for upper in range(4) for lower in range(4)}
    return p, dp, c, dc, Fraction(seed - 3, seed + 5)


def sym(values: Mapping[tuple[int, int], Fraction], left: int, right: int) -> Fraction:
    return values[(min(left, right), max(left, right))]


def dsym(values: Mapping[tuple[tuple[int, int], int], Fraction], left: int, right: int, derivative: int) -> Fraction:
    return values[((min(left, right), max(left, right)), derivative)]


def declared_lie(pair: tuple[int, int], fixture: tuple[dict, dict, dict, dict, Fraction]) -> Fraction:
    mu, nu = pair
    p, dp, c, dc, _ = fixture
    return (
        sum(c[rho] * dsym(dp, mu, nu, rho) for rho in range(4))
        - sum(sym(p, rho, nu) * dc[(mu, rho)] for rho in range(4))
        - sum(sym(p, mu, rho) * dc[(nu, rho)] for rho in range(4))
        + sum(dc[(rho, rho)] * sym(p, mu, nu) for rho in range(4))
    )


def negative_euler(pair: tuple[int, int], fixture: tuple[dict, dict, dict, dict, Fraction]) -> Fraction:
    mu, nu = pair
    p, dp, c, dc, _ = fixture
    # -Euler_h of p^{ab}(c^r d_r h_ab + h_rb d_a c^r + h_ar d_b c^r).
    product_derivative = sum(dsym(dp, mu, nu, rho) * c[rho] + sym(p, mu, nu) * dc[(rho, rho)] for rho in range(4))
    index_terms = sum(sym(p, rho, nu) * dc[(mu, rho)] + sym(p, mu, rho) * dc[(nu, rho)] for rho in range(4))
    return product_derivative - index_terms


def check(value: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    universal = json.loads(UNIVERSAL.read_text())
    exported = json.loads(EXPORT.read_text())
    imported = json.loads(IMPORT.read_text())
    normalization = json.loads(NORMALIZATION.read_text())
    upstream_errors = UNIVERSAL_CHECK.check(universal)
    if upstream_errors:
        errors.append(f"upstream universal table receiver failed: {upstream_errors[:2]}")

    if value.get("result_state") != "HSTAR_BASEPOINT_ROW_AND_DIFF_IDENTITY_ASSEMBLED_PORTABLE_GLOBALIZATION_AND_POLARIZATION_OPEN" or value.get("lifecycle") != "CLASSIFIED":
        errors.append("result state/lifecycle drift")
    if value.get("dependency_tags") != ["LOCAL-ALGEBRAIC"]:
        errors.append("dependency-tag promotion")
    scope = value.get("scope", {})
    if scope.get("row_formula") != ROW_FORMULA or scope.get("coefficient_field") != "Q":
        errors.append("row formula or exact coefficient field drift")
    if "not yet the suspended bilinear q2" not in scope.get("diagonal_Taylor_convention", "") or "homogeneous frame" not in scope.get("metric_kernel_boundary", "").lower():
        errors.append("diagonal/globalization boundary drift")

    expected_terms = [
        {"coefficient": -2, "factors": ["omega", "g_star"]},
        {"coefficient": 1, "factors": ["E_g"]},
        {"coefficient": 1, "factors": ["Lie_g_star"]},
    ]
    source_row = next(row for row in exported["differential"]["Q"]["rows"] if row["source_atom"] == "g_star")
    crosswalk = value.get("source_crosswalk", {})
    if source_row["image"]["terms"] != expected_terms or crosswalk.get("authoritative_Q_g_star_terms") != expected_terms:
        errors.append("authoritative g-star source row drift")
    if exported["canonical_hashes"] != imported.get("independent_replay", {}).get("canonical_hashes") or crosswalk.get("source_canonical_hashes") != exported["canonical_hashes"] or crosswalk.get("receiver_canonical_hashes") != exported["canonical_hashes"]:
        errors.append("source/receiver canonical hash crosswalk drift")
    if crosswalk.get("Euler_coordinate") != normalization.get("Euler_coordinate") or crosswalk.get("minimal_metric_master_term") != normalization.get("minimal_master_terms", [None])[0]:
        errors.append("action or Euler normalization crosswalk drift")
    expected_tensor = next(item for item in exported["generators"] if item["symbol"] == "g_star")["tensor_type"]
    if crosswalk.get("metric_antifield_tensor_type") != expected_tensor or scope.get("output", {}).get("tensor_type") != expected_tensor:
        errors.append("metric-antifield tensor type drift")

    expected_components = [
        ("q2_hstar_hh_basepoint", ["h", "h"], "1/2", "(1/2) K^{mu nu}[h,h]", "HOMOGENEOUS_BASEPOINT_ONLY", "E_g"),
        ("q2_hstar_chstar", ["c", "h_star"], "1", DIFF_FORMULA, "TENSOR_NATURAL", "Lie_g_star"),
        ("q2_hstar_omegahstar", ["omega", "h_star"], "-2", "-2 omega h_star^{mu nu}", "TENSOR_NATURAL", "omega*g_star"),
    ]
    components = value.get("components", [])
    actual_components = [(item.get("component_id"), item.get("inputs"), item.get("coefficient"), item.get("coordinate_formula"), item.get("portability"), item.get("source_atom")) for item in components]
    if actual_components != expected_components:
        errors.append("three-component h-star inventory/formula drift")
    if len(components) != 3 or any("intersection" not in item.get("support_rule", "") for item in components):
        errors.append("component support-locality declaration drift")

    reference = value.get("universal_table_reference", {})
    if reference != {
        "result_id": universal["result_id"],
        "universal_table_sha256": universal["canonical_hashes"]["universal_table_sha256"],
        "input_basis_count": 700,
        "symmetric_bilinear_term_count": 19401,
        "polarized_coefficient_convention": universal["scope"]["taylor_convention"],
        "diagonal_Taylor_multiplier": "1/2",
    }:
        errors.append("universal table reference or diagonal factor drift")

    checks = value.get("exact_checks", {})
    expected_gates = {
        "HSTAR_BASEPOINT_DIAGONAL_ASSEMBLY": "PASS",
        "TENSOR_NATURAL_GLOBALIZATION": "OPEN",
        "DIFFERENTIATED_DIFF_NOETHER": "PASS",
        "SUSPENDED_GRADED_POLARIZATION": "OPEN",
        "SIX_ROW_INTERACTION_IDENTITIES": "OPEN",
    }
    if {item.get("gate"): item.get("status") for item in value.get("gates", [])} != expected_gates:
        errors.append("gate ledger drift or false promotion")
    flags = value.get("claim_flags", {})
    true_flags = {"HSTAR_BASEPOINT_DIAGONAL_ROW_ASSEMBLED", "METRIC_ANTIFIELD_DIFF_COTANGENT_TERM_CERTIFIED", "METRIC_ANTIFIELD_WEYL_COTANGENT_TERM_CERTIFIED", "DIFFERENTIATED_DIFF_NOETHER_REPLAYED"}
    if any(flags.get(item) is not True for item in true_flags) or any(flags.get(item) is not False for item in FALSE_FLAGS):
        errors.append("claim boundary flag drift or promotion")
    missing = value.get("missing_object_ledger", [])
    if len(missing) != 3 or any(item.get("status") != "MISSING" for item in missing):
        errors.append("missing-object ledger shortened or promoted")
    expected_hashes = {
        "source_crosswalk_sha256": digest(crosswalk),
        "components_sha256": digest(components),
        "exact_checks_sha256": digest(checks),
        "gates_sha256": digest(value.get("gates")),
        "missing_object_ledger_sha256": digest(missing),
    }
    if value.get("canonical_hashes") != expected_hashes:
        errors.append("canonical hashes do not reproduce")
    run_expensive_replays = not errors

    records = checks.get("three_exact_hessian_diagonal_checks", [])
    if [item.get("seed") for item in records] != [1, 3, 5]:
        errors.append("diagonal Hessian check inventory drift")
    elif run_expensive_replays:
        for record in records:
            fixture = metric_fixture(record["seed"])
            compact = compact_diagonal(universal["universal_table"], fixture)
            point = {pair: coefficient / 2 for pair, coefficient in POINT.polarized_bach_euler_density(fixture, fixture).items()}
            serialized = [str(point[pair]) for pair in PAIRS]
            if compact != point or record.get("quadratic_diagonal_output") != serialized or record.get("output_sha256") != digest(serialized) or record.get("coefficient_relative_to_polarized_table") != "1/2":
                errors.append(f"diagonal Hessian factor/replay failed at seed {record['seed']}")

    cotangent_records = checks.get("three_diff_and_weyl_variational_cotangent_checks", [])
    if [item.get("seed") for item in cotangent_records] != [1, 2, 5]:
        errors.append("cotangent variational check inventory drift")
    elif run_expensive_replays:
        for record in cotangent_records:
            fixture = cotangent_fixture(record["seed"])
            direct = [declared_lie(pair, fixture) for pair in PAIRS]
            adjoint = [negative_euler(pair, fixture) for pair in PAIRS]
            p, _, _, _, omega = fixture
            weyl = [-2 * omega * p[pair] for pair in PAIRS]
            if direct != adjoint or record.get("diff_output_sha256") != digest([str(item) for item in direct]) or record.get("weyl_output_sha256") != digest([str(item) for item in weyl]) or record.get("negative_euler_equals_declared_cotangent") is not True:
                errors.append(f"cotangent variational replay failed at seed {record['seed']}")

    for item in value.get("provenance", {}).get("inputs", []):
        path = ROOT / item.get("path", "")
        if not path.is_file() or file_sha(path) != item.get("sha256"):
            errors.append(f"provenance drift: {item.get('path')}")
    if len(value.get("does_not_establish", [])) < 6:
        errors.append("does-not-establish ledger shortened")
    return errors


def main() -> int:
    value = json.loads(RESULT.read_text())
    errors = check(value)
    print("STRICT_CYLINDER_HSTAR_BASEPOINT_ROW_V1: " + ("PASS" if not errors else "FAIL"))
    if errors:
        for error in errors:
            print(f"  - {error}")
    else:
        print("  - exact 1/2 Hessian normalization and both cotangent signs replayed")
        print("  - Diff identity passes; globalization, polarization and remaining interaction identities stay open")
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
