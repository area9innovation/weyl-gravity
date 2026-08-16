#!/usr/bin/env python3
"""Independent receiver for the represented D-finite M3R comparison."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from math import factorial
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_ENDPOINT_TO_RESIDUAL_SPECTRAL_COMPARISON_V1.json"
BINDING = HERE / "certificates/STRICT_386_COMMON_ENDPOINT_SDR_BINDING_V1.json"
DFINITE = HERE / "certificates/STRICT_DFINITE_RESIDUAL_SDR_V1.json"
TYPE_AUDIT = HERE / "certificates/STRICT_RESIDUAL_SDR_TYPE_AND_LOCALITY_AUDIT_V1.json"
ZERO_MODES = HERE / "certificates/STRICT_RESIDUAL_ZERO_MODE_PAYLOAD_V1.json"
PREIMAGES = ROOT / "bridge/certificates/cylinder_metric_preimages.json"
BGG = ROOT / "bridge/certificates/cylinder_bgg_blocks.json"
PREIMAGE_SOURCE = ROOT / "bridge/metric_preimages/all_energy.py"
PREIMAGE_PRODUCER = ROOT / "symbolic/verify_conformal_cylinder_preimages.py"
BGG_PRODUCER = ROOT / "symbolic/verify_conformal_cylinder_bgg_blocks.py"
DEPENDENCIES = (
    BINDING, DFINITE, TYPE_AUDIT, ZERO_MODES, PREIMAGES, BGG,
    PREIMAGE_SOURCE, PREIMAGE_PRODUCER, BGG_PRODUCER,
)
ENERGIES = tuple(range(2, 7))
FAMILY_DATA = (
    ("E", 2, lambda n: (n + 2, n - 2)),
    ("A", 3, lambda n: (n, n - 2)),
    ("L", 4, lambda n: (n, n - 4)),
)
CHIRALITIES = (("W_PLUS", "+"), ("W_MINUS", "-"))

Sparse = dict[tuple[int, int], Fraction]


def digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def lowering_norm_squared(two_j: int, two_m: int) -> int:
    steps = (two_j - two_m) // 2
    return factorial(steps) * factorial(two_j) // factorial(two_j - steps)


def expected_basis() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    records: list[dict[str, Any]] = []
    levels: list[dict[str, Any]] = []
    global_index = 0
    for energy in ENERGIES:
        level_start = global_index
        chirality_dimensions: dict[str, int] = {}
        family_dimensions: dict[str, dict[str, int]] = {}
        for chirality, sign in CHIRALITIES:
            chirality_index = 0
            family_dimensions[chirality] = {}
            for family, minimum, spin_formula in FAMILY_DATA:
                if energy < minimum:
                    continue
                positive_left, positive_right = spin_formula(energy)
                two_j_left, two_j_right = (
                    (positive_left, positive_right)
                    if chirality == "W_PLUS"
                    else (positive_right, positive_left)
                )
                start = chirality_index
                for two_m_left in range(two_j_left, -two_j_left - 1, -2):
                    for two_m_right in range(two_j_right, -two_j_right - 1, -2):
                        left_steps = (two_j_left - two_m_left) // 2
                        right_steps = (two_j_right - two_m_right) // 2
                        norm = (
                            lowering_norm_squared(two_j_left, two_m_left)
                            * lowering_norm_squared(two_j_right, two_m_right)
                        )
                        generic = f"E{energy}:{chirality}:{chirality_index}"
                        represented = (
                            f"E{energy}:{chirality}:{family}:"
                            f"mL2={two_m_left}:mR2={two_m_right}"
                        )
                        records.append({
                            "global_index": global_index,
                            "energy": energy,
                            "chirality": chirality,
                            "chirality_sign": sign,
                            "family": family,
                            "two_j_left": two_j_left,
                            "two_j_right": two_j_right,
                            "two_m_left": two_m_left,
                            "two_m_right": two_m_right,
                            "left_lowering_steps": left_steps,
                            "right_lowering_steps": right_steps,
                            "unnormalized_lowering_norm_squared": norm,
                            "normalization": f"1/sqrt({norm})",
                            "chirality_index": chirality_index,
                            "dfinite_residual_label": generic,
                            "represented_residual_label": represented,
                            "metric_preimage_name": f"h[{represented}]",
                            "curvature_basis_name": f"U[{represented}]=C1(h[{represented}])",
                        })
                        global_index += 1
                        chirality_index += 1
                family_dimensions[chirality][family] = chirality_index - start
            chirality_dimensions[chirality] = chirality_index
        levels.append({
            "energy": energy,
            "global_start": level_start,
            "global_stop": global_index,
            "dimension": global_index - level_start,
            "chirality_dimensions": chirality_dimensions,
            "family_dimensions": family_dimensions,
        })
    return records, levels


def parse_sparse(value: dict[str, Any], name: str) -> tuple[int, int, Sparse, list[str]]:
    errors: list[str] = []
    rows, columns = value.get("rows"), value.get("columns")
    if value.get("name") != name or not isinstance(rows, int) or not isinstance(columns, int):
        return 0, 0, {}, ["matrix header " + name]
    result: Sparse = {}
    for entry in value.get("entries", []):
        if not isinstance(entry, list) or len(entry) != 3:
            errors.append("matrix entry " + name)
            continue
        row, column, raw = entry
        try:
            coefficient = Fraction(raw)
        except (ValueError, ZeroDivisionError, TypeError):
            errors.append("matrix coefficient " + name)
            continue
        if not isinstance(row, int) or not isinstance(column, int) or not (0 <= row < rows and 0 <= column < columns):
            errors.append("matrix coordinate " + name)
        elif coefficient == 0 or (row, column) in result:
            errors.append("matrix support " + name)
        else:
            result[row, column] = coefficient
    return rows, columns, result, errors


def multiply(left: Sparse, right: Sparse) -> Sparse:
    right_rows: dict[int, list[tuple[int, Fraction]]] = {}
    for (row, column), coefficient in right.items():
        right_rows.setdefault(row, []).append((column, coefficient))
    result: Sparse = {}
    for (row, middle), coefficient in left.items():
        for column, other in right_rows.get(middle, []):
            key = (row, column)
            result[key] = result.get(key, Fraction(0)) + coefficient * other
            if result[key] == 0:
                del result[key]
    return result


def identity(size: int) -> Sparse:
    return {(index, index): Fraction(1) for index in range(size)}


def check(value: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    pins = {
        item.get("path"): item.get("sha256")
        for item in value.get("provenance", {}).get("inputs", [])
    }
    for path in DEPENDENCIES:
        relative = str(path.relative_to(ROOT))
        if pins.get(relative) != hashlib.sha256(path.read_bytes()).hexdigest():
            errors.append("dependency hash " + relative)

    binding = json.loads(BINDING.read_text(encoding="utf-8"))
    dfinite = json.loads(DFINITE.read_text(encoding="utf-8"))
    type_audit = json.loads(TYPE_AUDIT.read_text(encoding="utf-8"))
    zero_modes = json.loads(ZERO_MODES.read_text(encoding="utf-8"))
    preimages = json.loads(PREIMAGES.read_text(encoding="utf-8"))
    bgg = json.loads(BGG.read_text(encoding="utf-8"))
    if binding.get("result_id") != "STRICT_386_COMMON_ENDPOINT_SDR_BINDING_V1" or binding.get("claim_flags", {}).get("M3L_COMMON_ENDPOINT_SDR_BOUND") is not True:
        errors.append("M3L dependency")
    if dfinite.get("result_id") != "STRICT_DFINITE_RESIDUAL_SDR_V1" or dfinite.get("claim_flags", {}).get("STRICT_DFINITE_RESIDUAL_SDR_PORTABLE") is not True:
        errors.append("D-finite SDR dependency")
    if type_audit.get("claim_flags", {}).get("M3_TYPED_SPLIT_REQUIRED") is not True:
        errors.append("M3 type split dependency")

    records, levels = expected_basis()
    if value.get("ordered_residual_basis") != records:
        errors.append("independent represented-basis reconstruction")
    if value.get("level_blocks") != levels:
        errors.append("independent level-block reconstruction")
    if len(records) != 470 or len({item["represented_residual_label"] for item in records}) != 470:
        errors.append("470-mode basis bijection")

    generic = [label for block in dfinite.get("blocks", []) for label in block.get("residual_basis", [])]
    if [item["dfinite_residual_label"] for item in records] != generic:
        errors.append("D-finite ordered crosswalk")
    expected_level_dimensions = [10, 40, 82, 136, 202]
    if [item["dimension"] for item in levels] != expected_level_dimensions:
        errors.append("E/A/L level dimensions")
    if preimages.get("level_dimensions_2_through_6") != expected_level_dimensions:
        errors.append("preimage level dimensions")
    bgg_levels = {item.get("energy"): item for item in bgg.get("levels", [])}
    for energy, dimension in zip(ENERGIES, expected_level_dimensions):
        if bgg_levels.get(energy, {}).get("dim_kerB_mod_imK") != dimension:
            errors.append(f"BGG quotient dimension E{energy}")
    for item in preimages.get("records", []):
        if item.get("family") not in {"E", "A", "L"} or not item.get("curvature_pivot") or item.get("right_inverse") != f"R_n(U_{item.get('family')},n,M)=h_{item.get('family')},n,M":
            errors.append("highest-weight preimage record")

    pi_iota_defects = q_iota_defects = pi_q_defects = 0
    expected_offsets: list[dict[str, int]] = []
    expected_minimal: list[dict[str, int]] = []
    for block in dfinite.get("blocks", []):
        energy = block.get("energy")
        full = block.get("full_dimension")
        residual = block.get("residual_dimension")
        matrices = block.get("matrices", {})
        _, _, q0, q_errors = parse_sparse(matrices.get("q0", {}), "q0")
        _, _, iota, i_errors = parse_sparse(matrices.get("iota_cl", {}), "iota_cl")
        _, _, pi, p_errors = parse_sparse(matrices.get("pi_cl", {}), "pi_cl")
        errors.extend(f"E{energy} {error}" for error in q_errors + i_errors + p_errors)
        if isinstance(residual, int):
            pi_iota = multiply(pi, iota)
            expected_identity = identity(residual)
            pi_iota_defects += sum(
                pi_iota.get(entry) != expected_identity.get(entry)
                for entry in set(pi_iota) | set(expected_identity)
            )
        q_iota_defects += len(multiply(q0, iota))
        pi_q_defects += len(multiply(pi, q0))
        sectors = {item.get("name"): item for item in block.get("full_sectors", [])}
        start = sectors.get("metric_tf", {}).get("start", -1) + block.get("dimensions", {}).get("gauge", 0)
        expected_offsets.append({
            "energy": energy,
            "metric_tf_physical_start": start,
            "metric_tf_physical_stop": start + residual,
        })
        scalar = block.get("dimensions", {}).get("scalar", 0)
        expected_minimal.append({
            "energy": energy,
            "dfinite_full_dimension": full,
            "test_nonminimal_dimension_excluded": 2 * scalar,
            "represented_endpoint_complex_dimension": full - 2 * scalar,
            "residual_dimension": residual,
        })

    comparison = value.get("comparison", {})
    source = comparison.get("source", {})
    target = comparison.get("target", {})
    if source.get("level_dimensions") != expected_minimal or source.get("total_dimension") != sum(item["represented_endpoint_complex_dimension"] for item in expected_minimal):
        errors.append("represented endpoint domain dimensions")
    if source.get("compact_support") is not False or source.get("arbitrary_smooth_completion") is not False:
        errors.append("source-domain firewall")
    if target.get("dimension") != 470 or target.get("ordered_basis_hash") != digest([item["represented_residual_label"] for item in records]):
        errors.append("residual target dictionary")
    if comparison.get("physical_offsets") != expected_offsets:
        errors.append("physical BGG offsets")
    if comparison.get("harmonic_restriction", {}).get("position_space_support_local") is not False:
        errors.append("harmonic restriction locality")
    if comparison.get("sha256") != digest({key: item for key, item in comparison.items() if key != "sha256"}):
        errors.append("comparison digest")

    zero_names = {
        *zero_modes.get("zero_mode_basis", {}).get("canonical_generator_order", []),
        *zero_modes.get("zero_mode_basis", {}).get("canonical_dual_order", []),
    }
    represented_names = {item["represented_residual_label"] for item in records}
    zero_overlap = len(zero_names.intersection(represented_names))
    support = value.get("support_and_zero_mode_policy", {})
    if (
        support.get("harmonic_analysis_support_local") is not False
        or support.get("excluded_energies") != [0, 1]
        or support.get("zero_modes_are_not_inserted_into_the_470_basis") is not True
        or zero_overlap
    ):
        errors.append("support/zero-mode policy")

    expected_replay = {
        "energy_blocks": 5,
        "represented_residual_coordinates": 470,
        "ordered_crosswalk_defects": 0,
        "duplicate_represented_labels": 0,
        "level_dimension_defects": 0,
        "dfinite_pi_iota_identity_defects": pi_iota_defects,
        "dfinite_q0_iota_chain_defects": q_iota_defects,
        "dfinite_pi_q0_chain_defects": pi_q_defects,
        "nonzero_highest_weight_pivot_failures": 0,
        "zero_mode_overlap_defects": zero_overlap,
    }
    if value.get("exact_replay") != expected_replay or any(
        count for key, count in expected_replay.items() if key.endswith("defects") or key.endswith("failures")
    ):
        errors.append("exact replay")

    flags = value.get("claim_flags", {})
    for key in (
        "M3L_COMMON_ENDPOINT_SDR_BOUND", "M3R_TYPED_RESIDUAL_COMPARISON_CONSTRUCTED",
        "M3R_ORDERED_470_MODE_CROSSWALK_BIJECTIVE", "M3R_CHAIN_IDENTITIES_REPLAYED",
        "M3R_ZERO_MODE_POLICY_EXPLICIT",
    ):
        if flags.get(key) is not True:
            errors.append("positive flag " + key)
    for key in (
        "HARMONIC_ANALYSIS_SUPPORT_LOCAL", "RAW_ALL_MAGNETIC_COORDINATE_MATRICES_SERIALIZED",
        "ALL_ENERGY_OR_SMOOTH_COMPLETION_CERTIFIED", "M4R_TYPED_RESIDUAL_CYCLICITY_COMPLETE",
        "NEW_GATE_A_TOP_LEVEL_HASH_ACCEPTED", "CLASSICAL_IMPORT_GATE_PASSED",
        "FULL_COMPLEX_HADAMARD_STATE_CONSTRUCTED", "QME_RESTORED",
        "RESIDUAL_QUANTUM_TRANSFER_AUTHORIZED",
    ):
        if flags.get(key) is not False:
            errors.append("fail-closed flag " + key)
    gate = value.get("gate_disposition", {})
    if gate.get("M3R_TYPED_RESIDUAL_COMPARISON") != "COMPLETE_IN_REPRESENTED_DFINITE_ENERGIES_2_THROUGH_6" or gate.get("classical_import_gate_a_status") != "FAIL_CLOSED":
        errors.append("gate disposition")
    strength = value.get("foundational_strength", {})
    if strength.get("choice_dependency_fixed_cutoff") != "none" or not str(strength.get("smooth_or_all_energy_extension", "")).startswith("not certified"):
        errors.append("foundational-strength boundary")

    expected_digest = digest({
        key: value.get(key)
        for key in (
            "scope", "comparison", "representation_conventions", "level_blocks",
            "ordered_residual_basis", "exact_replay", "support_and_zero_mode_policy",
            "foundational_strength", "gate_disposition", "claim_flags",
        )
    })
    if value.get("independent_checker", {}).get("expected_digest") != expected_digest:
        errors.append("independent digest")
    return errors


def main() -> int:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    errors = check(value)
    print("STRICT_ENDPOINT_TO_RESIDUAL_SPECTRAL_COMPARISON: " + ("PASS" if not errors else "FAIL"))
    for error in errors:
        print("  - " + error)
    if not errors:
        print("  - 470 represented E/A/L modes crosswalked exactly")
        print("  - pi iota and both q0 chain identities replayed in the D-finite category")
        print("  - support locality, smooth completion, M4R and Gate A remain fail closed")
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
