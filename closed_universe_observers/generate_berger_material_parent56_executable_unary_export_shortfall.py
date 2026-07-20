#!/usr/bin/env python3
"""Export the derivable material-parent unary data and certify its first gap."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
CERTIFICATE = P / "certificates/BERGER_MATERIAL_PARENT56_EXECUTABLE_UNARY_EXPORT_SHORTFALL.json"
PAYLOAD = P / "certificates/BERGER_MATERIAL_PARENT56_EXECUTABLE_UNARY_EXPORT_SHORTFALL_PAYLOAD.json"
SCHEMA = P / "schema/berger-material-parent56-executable-unary-export-shortfall-v1.schema.json"
REPORT = P / "reports/berger-material-parent56-executable-unary-export-shortfall.md"
DEPENDENCIES = {
    "parent": P / "certificates/BERGER_DYNAMICAL_APPARATUS_PARENT.json",
    "parent_payload": P / "certificates/BERGER_DYNAMICAL_APPARATUS_PARENT_PAYLOAD.json",
    "input_shortfall": P / "certificates/BERGER_APPARATUS_160_EXECUTABLE_UNARY_EXPORT_INPUT_SHORTFALL.json",
    "input_shortfall_payload": P / "certificates/BERGER_APPARATUS_160_EXECUTABLE_UNARY_EXPORT_INPUT_SHORTFALL_PAYLOAD.json",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _rows(parent: dict[str, Any]) -> list[dict[str, Any]]:
    physical = parent["carrier"]["physical_even_rows"]
    cotangent = parent["carrier"]["odd_cotangent_rows"]
    return [
        {
            "index": index,
            "row_id": row,
            "degree": int(index >= 28),
            "parity": "odd" if index >= 28 else "even",
            "role": "cotangent" if index >= 28 else "physical",
        }
        for index, row in enumerate(physical + cotangent)
    ]


def _internal_hessian(physical: list[str]) -> tuple[sp.Matrix, list[dict[str, Any]]]:
    s, omega = sp.symbols("s Omega_K")
    j = sp.Matrix([[0, -1], [1, 0]])
    d = s * sp.eye(2) + omega * j
    hessian = sp.zeros(28)
    blocks = []
    pairs = []
    for detector in range(2):
        pairs.extend([
            (f"detector_{detector}_orientation", [f"rod_orientation_{detector}_{i}" for i in range(2)], [f"rod_momentum_{detector}_{i}" for i in range(2)]),
            (f"detector_{detector}_polarization", [f"polarization_{detector}_{i}" for i in range(2)], [f"polarization_momentum_{detector}_{i}" for i in range(2)]),
        ])
    for emitter in range(2):
        pairs.append((f"emitter_{emitter}_phase", [f"emitter_phase_{emitter}_{i}" for i in range(2)], [f"emitter_phase_momentum_{emitter}_{i}" for i in range(2)]))
    for block_id, coordinate, momentum in pairs:
        x = [physical.index(name) for name in coordinate]
        y = [physical.index(name) for name in momentum]
        for left in range(2):
            for right in range(2):
                hessian[y[left], x[right]] = d[left, right]
                hessian[x[left], y[right]] = -d[left, right]
        blocks.append({"id": block_id, "coordinate_rows": coordinate, "momentum_rows": momentum, "operator": [["s", "-Omega_K"], ["Omega_K", "s"]]})
    for detector in range(2):
        m = physical.index(f"memory_{detector}")
        lam = physical.index(f"memory_multiplier_{detector}")
        hessian[lam, m] = s
        hessian[m, lam] = -s
        blocks.append({"id": f"detector_{detector}_memory", "coordinate_rows": [physical[m]], "momentum_rows": [physical[lam]], "operator": [["s"]]})
    return hessian, blocks


def _sparse_entries(matrix: sp.Matrix, output_shift: int = 0) -> list[dict[str, Any]]:
    return [
        {"output": output_shift + row, "input": col, "coefficient": sp.sstr(sp.factor(matrix[row, col]))}
        for row in range(matrix.rows) for col in range(matrix.cols) if matrix[row, col] != 0
    ]


def _nonzero_count(matrix: sp.Matrix) -> int:
    return sum(int(value != 0) for value in matrix)


def build_payload() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    for cert_name, payload_name in (("parent", "parent_payload"), ("input_shortfall", "input_shortfall_payload")):
        if sha256(DEPENDENCIES[payload_name]) != values[cert_name]["payload_ref"]["sha256"]:
            raise AssertionError(f"{cert_name} payload hash mismatch")
    parent = values["parent_payload"]
    physical = parent["carrier"]["physical_even_rows"]
    cotangent = parent["carrier"]["odd_cotangent_rows"]
    if cotangent != [f"{row}_plus" for row in physical] or len(physical) != 28:
        raise AssertionError("parent row ordering drifted")
    rows = _rows(parent)
    pairing = [
        entry
        for index in range(28)
        for entry in (
            {"left": index, "right": index + 28, "coefficient": "1"},
            {"left": index + 28, "right": index, "coefficient": "-1"},
        )
    ]
    pairing_matrix = sp.zeros(56)
    for entry in pairing:
        pairing_matrix[entry["left"], entry["right"]] = sp.sympify(entry["coefficient"])
    hessian, blocks = _internal_hessian(physical)
    s, omega = sp.symbols("s Omega_K")
    formal_adjoint = hessian.T.applyfunc(lambda value: sp.expand(value.subs(s, -s)))
    if formal_adjoint != hessian:
        raise AssertionError("internal quadratic variation is not formally self-adjoint")
    q1 = sp.zeros(56)
    q1[28:56, 0:28] = hessian
    q1_entries = _sparse_entries(hessian, 28)
    j = sp.Matrix([[0, -1], [1, 0]])
    k_physical = sp.zeros(28)
    for block in blocks:
        if len(block["coordinate_rows"]) != 2:
            continue
        for names in (block["coordinate_rows"], block["momentum_rows"]):
            indices = [physical.index(name) for name in names]
            k_physical.extract(indices, indices)
            for a in range(2):
                for b in range(2):
                    k_physical[indices[a], indices[b]] = j[a, b]
    k_full = sp.diag(k_physical, k_physical)
    k_defect = k_full * q1 - q1 * k_full
    detector = sp.zeros(2, 56)
    detector[0, physical.index("memory_0")] = 1
    detector[1, physical.index("memory_1")] = 1

    local_action = parent["local_action"]
    available = set(local_action)
    missing_interface_fields = [
        "F_a_base_row_dictionary",
        "F_a_detector_profile_functionals",
        "mixed_lambda_F_sparse_unary_entries",
        "mixed_lambda_F_support_and_zero_mode_blocks",
    ]
    decisive = [
        {"detector": 0, "derivative": "d2S/(d memory_multiplier_0 d F_0_0)", "coefficient": "-1", "row_status": "NO_CERTIFIED_MAP"},
        {"detector": 0, "derivative": "d2S/(d F_0_0 d memory_multiplier_0)", "coefficient": "-1", "row_status": "NO_CERTIFIED_MAP"},
        {"detector": 1, "derivative": "d2S/(d memory_multiplier_1 d F_1_1)", "coefficient": "-1", "row_status": "NO_CERTIFIED_MAP"},
        {"detector": 1, "derivative": "d2S/(d F_1_1 d memory_multiplier_1)", "coefficient": "-1", "row_status": "NO_CERTIFIED_MAP"},
    ]
    return {
        "schema": "closed-universe-berger-material-parent56-executable-unary-export-shortfall-payload-v1",
        "result_id": "BERGER_MATERIAL_PARENT56_EXECUTABLE_UNARY_EXPORT_SHORTFALL_PAYLOAD",
        "coefficient_domain": {
            "ring": "Q[Omega_K,s]",
            "formal_adjoint": {"s": "-s", "Omega_K": "Omega_K"},
            "pbw_order": ["Omega_K", "s"],
        },
        "carrier": {
            "rows": rows,
            "row_count": 56,
            "pairing_entries": pairing,
            "pairing_rank": int(pairing_matrix.rank()),
            "real_involution": "identity on all declared real rows",
            "K_Berger_action": _sparse_entries(k_full),
        },
        "derivable_internal_unary": {
            "scope": "six D_K doublet Hessians and two lambda_a*d_tau*m_a memory Hessians only",
            "blocks": blocks,
            "sparse_entries": q1_entries,
            "entry_count": len(q1_entries),
            "generic_matrix_canonical_sha256": canonical_sha256(q1_entries),
            "zero_mode_sparse_entries": _sparse_entries(hessian.subs(s, 0), 28),
            "zero_mode_matrix_canonical_sha256": canonical_sha256(_sparse_entries(hessian.subs(s, 0), 28)),
            "generic_rank_over_Q_Omega_s": int(hessian.rank()),
            "zero_mode_rank_over_Q_Omega": int(hessian.subs(s, 0).rank()),
            "q1_squared_defect_count": _nonzero_count(q1 * q1),
            "formal_cyclicity_defect_count": _nonzero_count(formal_adjoint - hessian),
            "real_defect_count": 0,
            "K_commutator_defect_count": _nonzero_count(k_defect),
        },
        "detector_smearing_partial_map": {
            "matrix_shape": [2, 56],
            "sparse_entries": _sparse_entries(detector),
            "selected_rows": ["memory_0", "memory_1"],
            "internal_chain_defect_count": _nonzero_count(detector * q1),
            "coordinate_selection_rank": int(detector.rank()),
            "full_action_chain_map": "NO_CERTIFIED_MAP because the mixed lambda-F unary interface has no row realization",
        },
        "first_missing_variational_object": {
            "status": "NO_CERTIFIED_MAP",
            "object": "row-indexed mixed background-readout Hessian from -lambda_a Pbar_a dot F_a",
            "reason": "F_a is named in the quadratic action but no dependency maps its two components and detector profiles to base unary rows or support sectors",
            "available_local_action_fields": sorted(available),
            "missing_interface_fields": missing_interface_fields,
            "nonzero_unplaceable_derivatives": decisive,
            "background_polarizations": local_action["background_polarizations"],
        },
        "disposition": {
            "canonical_56_row_dictionary_and_pairing": "CERTIFIED",
            "six_D_K_and_two_memory_internal_unary_blocks": "CERTIFIED",
            "complete_action_derived_material_parent_unary": "NO_CERTIFIED_MAP",
            "complete_detector_smearing_chain_map": "NO_CERTIFIED_MAP",
            "replacement_and_160_row_consumers": "NOT_REACHED",
        },
    }


def build_certificate(payload: dict[str, Any]) -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    payload_text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    return {
        "schema": "closed-universe-berger-material-parent56-executable-unary-export-shortfall-v1",
        "result_id": "BERGER_MATERIAL_PARENT56_EXECUTABLE_UNARY_EXPORT_SHORTFALL",
        "setting_id": values["parent"]["setting_id"],
        "claim_status": "SHORTFALL_MISSING_MIXED_BACKGROUND_READOUT_HESSIAN_ROW_INTERFACE",
        "atlas_status": "NO_CERTIFIED_MAP",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "dependency_refs": {
            name: {"path": str(path.relative_to(ROOT)), "result_id": values[name]["result_id"], "sha256": sha256(path)}
            for name, path in DEPENDENCIES.items()
        },
        "payload_ref": {
            "path": str(PAYLOAD.relative_to(ROOT)),
            "result_id": payload["result_id"],
            "sha256": hashlib.sha256(payload_text.encode()).hexdigest(),
            "canonical_sha256": canonical_sha256(payload),
        },
        "gate_results": payload["disposition"],
        "next_gate": "EXPORT_F_A_BASE_ROW_AND_DETECTOR_PROFILE_INTERFACE_FOR_MIXED_LAMBDA_F_HESSIAN",
        "claim_boundary": (
            "This exact LOCAL-ALGEBRAIC/REDUCED-MODE result performs the requested material-parent-56 executable-unary audit and stops at the first action coefficient that cannot be placed on certified rows. It imports the dynamical apparatus parent and the executable-unary input audit by content hash. The parent supplies an ordered list of twenty-eight real physical rows and their twenty-eight odd cotangents, so the exporter certifies a canonical 56-row dictionary, degrees, parities and all fifty-six signed odd-pairing entries; the pairing has exact rank fifty-six. From the explicit internal quadratic terms it independently derives six first-order D_K doublet Hessians and two lambda_a*d_tau*m_a memory Hessians over Q[Omega_K,s]. Their normalized sparse q1 entries, formal adjoint convention, generic and s=0 matrices, support block labels, real involution and K_Berger action are serialized. The internal matrix has zero nilpotency, formal cyclicity, real and K-commutator defects. The two-by-fifty-six coordinate detector map selecting memory_0 and memory_1 has rank two and is a chain map for this internal block. These partial positive results do not make the full material parent executable. The same declared action contains the quadratic background readout term -lambda_a Pbar_a dot F_a. With Pbar_0=(1,0) and Pbar_1=(0,1), its quadratic variation has four ordered nonzero derivatives, of coefficient -1, between memory_multiplier_0 and F_0_0 and between memory_multiplier_1 and F_1_1. F_a is not among the fifty-six rows, and no imported payload maps its components or detector profile functionals to exact base row indices, coefficient factors, support sectors or zero-mode blocks. Consequently those nonzero Hessian entries cannot be serialized without guessing an old-theory carrier identification. A method-distinct verifier differentiates the displayed mixed term directly and confirms the unplaceable derivatives while rebuilding the internal Hessian and pairing without importing the producer. The full action-derived q1, full detector chain identity and material-parent producer therefore remain NO_CERTIFIED_MAP; the replacement producer and 160-row quotient are NOT_REACHED. This is a missing variational interface, not a nilpotency or cyclicity obstruction. No isolated material cohomology, combined physical theory, q2, q3, Z2, memory, redshift, recoil, causal propagator, particle, positivity or quantum claim is made."
        ),
        "provenance": {
            "generator_command": "python3 -m closed_universe_observers.generate_berger_material_parent56_executable_unary_export_shortfall --write",
            "independent_verifier_command": "python3 -m closed_universe_observers.verify_berger_material_parent56_executable_unary_export_shortfall",
            "source_sha256": sha256(Path(__file__)),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    payload = build_payload()
    certificate = build_certificate(payload)
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(certificate)
    if args.write:
        PAYLOAD.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        CERTIFICATE.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n")
        REPORT.write_text("# Material-parent-56 executable unary export shortfall\n\nThe internal D_K and memory Hessians and the complete pairing are exact. The full unary stops at the nonzero mixed lambda-F background-readout Hessian because F_a has no certified base-row/profile interface.\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
