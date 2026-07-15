"""Exact arity-two D-derivation defect on the selected HT1 residual model.

This module computes the full defect tensor

    L_D q2(x,y) - q2(L_D x,y) - q2(x,L_D y)

for every q2 block exported by HT1.  It does not substitute the selected
residual BFV model for the missing support-local classical BV tensor.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from typing import Any

import sympy as sp


TRANSFER_ROOT = Path(__file__).resolve().parent
ROOT = TRANSFER_ROOT.parents[1]
for search_root in (ROOT, TRANSFER_ROOT):
    if str(search_root) not in sys.path:
        sys.path.insert(0, str(search_root))

try:
    from .residual_cubic_block import _matrix_from_payload, _tensor_from_payload
except ImportError:  # direct ``python quantum-weyl/transfer/script.py`` execution
    from residual_cubic_block import _matrix_from_payload, _tensor_from_payload


OUTPUT_PATH = TRANSFER_ROOT / "certificates" / "ND1_SELECTED_RESIDUAL_D_DERIVATION.json"
SCHEMA_PATH = TRANSFER_ROOT / "schema" / "selected-residual-d-derivation-v1.schema.json"
HT1_PATH = TRANSFER_ROOT / "certificates" / "HT1_RESIDUAL_CUBIC_BLOCK.json"

DEPENDENCY_PATHS = (
    "notes/d-quotient-nonlinear-team-brief.md",
    "d_quotient_classical/certificates/CLASSICAL_D_QUOTIENT_STATUS.json",
    "quantum-weyl/classical_import/snapshots/bootstrap-v1.json",
    "quantum-weyl/transfer/certificates/HT1_RESIDUAL_CUBIC_BLOCK.json",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _exact(value: sp.Expr) -> str:
    value = sp.simplify(value)
    if value.atoms(sp.Float):
        raise ValueError("ND1 D-derivation calculation contains floating-point data")
    return sp.srepr(value)


def _sparse_defect(
    shape: tuple[int, ...], entries: list[list[object]]
) -> dict[str, object]:
    return {
        "shape": list(shape),
        "coordinate_order": [],
        "scalar_format": "sympy-srepr-exact-v1",
        "checked_coefficient_count": int(sp.prod(shape)),
        "entries": entries,
    }


def _matrix_entries(
    matrices: list[sp.Matrix],
) -> list[list[object]]:
    entries: list[list[object]] = []
    for first, matrix in enumerate(matrices):
        for (target, source), value in sorted(matrix.todok().items()):
            if value != 0:
                entries.append([first, source, target, _exact(value)])
    return entries


def _diagonal_weights(matrix: sp.Matrix, sector: str) -> list[sp.Expr]:
    if not matrix.is_diagonal():
        raise ValueError(f"ND1 D action on {sector} is not diagonal")
    return [sp.simplify(value) for value in matrix.diagonal()]


def _source_support_counts(
    structure: tuple[tuple[tuple[sp.Expr, ...], ...], ...],
    generators: list[sp.Matrix],
    kernels: list[sp.Matrix],
) -> dict[str, int]:
    structure_count = sum(
        value != 0
        for first in structure
        for second in first
        for value in second
    )
    return {
        "ghost_ghost_to_ghost": int(structure_count),
        "ghost_matter_to_matter": sum(len(matrix.todok()) for matrix in generators),
        "matter_matter_to_ghost_momentum": sum(len(matrix.todok()) for matrix in kernels),
        "ghost_ghost_momentum_to_ghost_momentum": int(structure_count),
    }


def analyze_selected_q2(payload: object) -> dict[str, Any]:
    """Compute every selected residual q2 D-defect coefficient exactly."""

    if not isinstance(payload, dict):
        raise ValueError("ND1 selected residual q2 payload is missing")
    if payload.get("schema_version") != 2 or payload.get("scalar_format") != "sympy-srepr-exact-v1":
        raise ValueError("ND1 selected residual q2 payload has the wrong exact schema")
    basis = payload["basis"]
    names = [item["name"] for item in basis]
    if names.count("D") != 1:
        raise ValueError("ND1 requires exactly one D generator")
    d_index = names.index("D")
    generator_count = len(names)
    matter_payload = payload["matter_phase_space"]
    matter_basis = matter_payload["ordered_basis"]
    matter_dimension = matter_payload["dimension"]
    structure = _tensor_from_payload(payload["structure_constants"], generator_count)
    action_payloads = payload["q2"]["ghost_matter_to_matter"]["matrices"]
    moment_payloads = payload["q2"]["matter_matter_to_ghost_momentum"]["matrices"]
    if set(action_payloads) != set(names) or set(moment_payloads) != set(names):
        raise ValueError("ND1 selected residual q2 matrix component set is incomplete")
    generators = [
        sp.Matrix(_matrix_from_payload(action_payloads[name], f"generator {name}"))
        for name in names
    ]
    kernels = [
        sp.Matrix(_matrix_from_payload(moment_payloads[name], f"kernel {name}"))
        for name in names
    ]

    adjoint_d = sp.zeros(generator_count)
    for source in range(generator_count):
        for target in range(generator_count):
            adjoint_d[target, source] = structure[d_index][source][target]
    coadjoint_d = -adjoint_d.T
    matter_d = generators[d_index]
    ghost_weights = _diagonal_weights(adjoint_d, "residual ghosts")
    momentum_weights = _diagonal_weights(coadjoint_d, "residual ghost momenta")
    matter_weights = _diagonal_weights(matter_d, "selected matter modes")
    if ghost_weights != [sp.Integer(item["generator_degree"]) for item in basis]:
        raise ValueError("ND1 adjoint D weights disagree with the generator grading")
    if matter_weights != [sp.Integer(item["energy"]) for item in matter_basis]:
        raise ValueError("ND1 matter D weights disagree with the ordered energy ledger")
    if momentum_weights != [-weight for weight in ghost_weights]:
        raise ValueError("ND1 ghost-momentum D weights are not coadjoint")

    ghost_defect_entries: list[list[object]] = []
    for first in range(generator_count):
        for second in range(generator_count):
            for target in range(generator_count):
                defect = sp.simplify(
                    sum(
                        adjoint_d[target, middle] * structure[first][second][middle]
                        - adjoint_d[middle, first] * structure[middle][second][target]
                        - adjoint_d[middle, second] * structure[first][middle][target]
                        for middle in range(generator_count)
                    )
                )
                if defect != 0:
                    ghost_defect_entries.append(
                        [first, second, target, _exact(defect)]
                    )

    zero_matter = sp.zeros(matter_dimension)
    ghost_matter_defects = []
    moment_defects = []
    for first in range(generator_count):
        d_on_ghost = sum(
            (
                adjoint_d[middle, first] * generators[middle]
                for middle in range(generator_count)
            ),
            zero_matter,
        )
        ghost_matter_defects.append(
            sp.simplify(matter_d * generators[first] - d_on_ghost - generators[first] * matter_d)
        )
        d_on_momentum = sum(
            (
                coadjoint_d[first, middle] * kernels[middle]
                for middle in range(generator_count)
            ),
            zero_matter,
        )
        moment_defects.append(
            sp.simplify(
                d_on_momentum + matter_d * kernels[first] - kernels[first] * matter_d
            )
        )

    coadjoint_defect_entries: list[list[object]] = []
    for ghost in range(generator_count):
        for source_momentum in range(generator_count):
            for target_momentum in range(generator_count):
                defect = sp.simplify(
                    sum(
                        coadjoint_d[target_momentum, middle]
                        * (-structure[ghost][middle][source_momentum])
                        - adjoint_d[middle, ghost]
                        * (-structure[middle][target_momentum][source_momentum])
                        - coadjoint_d[middle, source_momentum]
                        * (-structure[ghost][target_momentum][middle])
                        for middle in range(generator_count)
                    )
                )
                if defect != 0:
                    coadjoint_defect_entries.append(
                        [ghost, source_momentum, target_momentum, _exact(defect)]
                    )

    defect_tensors = {
        "ghost_ghost_to_ghost": _sparse_defect(
            (generator_count, generator_count, generator_count),
            ghost_defect_entries,
        ),
        "ghost_matter_to_matter": _sparse_defect(
            (generator_count, matter_dimension, matter_dimension),
            _matrix_entries(ghost_matter_defects),
        ),
        "matter_matter_to_ghost_momentum": _sparse_defect(
            (generator_count, matter_dimension, matter_dimension),
            _matrix_entries(moment_defects),
        ),
        "ghost_ghost_momentum_to_ghost_momentum": _sparse_defect(
            (generator_count, generator_count, generator_count),
            coadjoint_defect_entries,
        ),
    }
    coordinate_orders = {
        "ghost_ghost_to_ghost": ["ghost_input_1", "ghost_input_2", "ghost_output"],
        "ghost_matter_to_matter": ["ghost_input", "matter_input", "matter_output"],
        "matter_matter_to_ghost_momentum": ["ghost_momentum_output", "matter_ket_input", "matter_bra_input"],
        "ghost_ghost_momentum_to_ghost_momentum": ["ghost_input", "ghost_momentum_input", "ghost_momentum_output"],
    }
    for block, order in coordinate_orders.items():
        defect_tensors[block]["coordinate_order"] = order

    weight_violations: dict[str, list[list[int]]] = {
        block: [] for block in defect_tensors
    }
    for first in range(generator_count):
        for second in range(generator_count):
            for target in range(generator_count):
                if structure[first][second][target] != 0 and ghost_weights[target] != ghost_weights[first] + ghost_weights[second]:
                    weight_violations["ghost_ghost_to_ghost"].append([first, second, target])
                if structure[first][target][second] != 0 and momentum_weights[target] != ghost_weights[first] + momentum_weights[second]:
                    weight_violations["ghost_ghost_momentum_to_ghost_momentum"].append([first, second, target])
        for (target, source), value in generators[first].todok().items():
            if value != 0 and matter_weights[target] != ghost_weights[first] + matter_weights[source]:
                weight_violations["ghost_matter_to_matter"].append([first, source, target])
        for (bra, ket), value in kernels[first].todok().items():
            if value != 0 and momentum_weights[first] != -matter_weights[bra] + matter_weights[ket]:
                weight_violations["matter_matter_to_ghost_momentum"].append([first, ket, bra])

    support_counts = _source_support_counts(structure, generators, kernels)
    component_ledgers = []
    particle_changes = {
        "ghost_ghost_to_ghost": 0,
        "ghost_matter_to_matter": 0,
        "matter_matter_to_ghost_momentum": -2,
        "ghost_ghost_momentum_to_ghost_momentum": 0,
    }
    for block in defect_tensors:
        component_ledgers.append(
            {
                "block": block,
                "source_nonzero_component_count": support_counts[block],
                "D_weight_violation_count": len(weight_violations[block]),
                "D_weight_violations": weight_violations[block],
                "particle_number_convention": "matter=1; residual ghost=0; residual ghost momentum=0",
                "particle_number_change": particle_changes[block],
                "defect_nonzero_component_count": len(defect_tensors[block]["entries"]),
            }
        )

    total_defects = sum(len(tensor["entries"]) for tensor in defect_tensors.values())
    total_weight_violations = sum(len(items) for items in weight_violations.values())
    return {
        "schema_version": 1,
        "scope": "selected finite residual HT1 BFV q2 field domain",
        "D_generator_index": d_index,
        "D_generator_name": names[d_index],
        "D_action": {
            "ghost_basis_reference": "HT1 transfer_payload.basis order",
            "ghost_weights": [_exact(value) for value in ghost_weights],
            "ghost_momentum_weights": [_exact(value) for value in momentum_weights],
            "matter_basis_reference": "HT1 transfer_payload.matter_phase_space.ordered_basis order",
            "matter_ket_weights": [_exact(value) for value in matter_weights],
            "matter_bra_weights": [_exact(-value) for value in matter_weights],
            "ghost_momentum_action": "minus transpose of the ghost adjoint D action",
            "matter_bra_action": "contragredient minus transpose of the matter ket D action",
        },
        "component_ledgers": component_ledgers,
        "defect_tensors": defect_tensors,
        "checks": {
            "available_q2_block_count": len(defect_tensors),
            "source_nonzero_component_count": sum(support_counts.values()),
            "full_selected_defect_coefficient_count": sum(
                tensor["checked_coefficient_count"] for tensor in defect_tensors.values()
            ),
            "D_derivation_defect_nonzero_component_count": total_defects,
            "D_weight_violation_count": total_weight_violations,
            "D_pairing_weight_neutrality": (
                "VERIFIED_EXACT"
                if all(left + right == 0 for left, right in zip(ghost_weights, momentum_weights))
                and all(left + right == 0 for left, right in zip(matter_weights, [-value for value in matter_weights]))
                else "FAILED"
            ),
            "selected_cubic_master_equation": "VERIFIED_UPSTREAM_HT1_CERTIFICATE",
        },
        "selected_verdict": (
            "SELECTED_RESIDUAL_D_DERIVATION_HOLDS_AT_ARITY_TWO"
            if total_defects == 0 and total_weight_violations == 0
            else "SELECTED_RESIDUAL_D_DERIVATION_DEFECT_NONZERO"
        ),
    }


def build_certificate() -> dict[str, Any]:
    ht1 = json.loads(HT1_PATH.read_text(encoding="utf-8"))
    if ht1.get("checks", {}).get("cubic_master_equation", {}).get("status") != "VERIFIED_EXACT_CUBIC_MASTER_EQUATION":
        raise ValueError("ND1 HT1 cubic master-equation input is not certified")
    payload = ht1.get("transfer_payload")
    analysis = analyze_selected_q2(payload)
    dependency_hashes = {path: _sha256(ROOT / path) for path in DEPENDENCY_PATHS}
    implementation_paths = (
        "__init__.py",
        "d_derivation_defect.py",
        "d_derivation_certificate.py",
        "schema/selected-residual-d-derivation-v1.schema.json",
        "tests/test_d_derivation_defect.py",
    )
    implementation_hashes = {
        path: _sha256(TRANSFER_ROOT / path) for path in implementation_paths
    }
    certificate = {
        "result_id": "ND1_SELECTED_RESIDUAL_D_DERIVATION",
        "result_state": "SELECTED_RESIDUAL_Q2_D_DEFECT_COMPUTED_FULL_LOCAL_INPUT_BLOCKED",
        "classical_commit": "UNFROZEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "analysis_payload": analysis,
        "analysis_payload_sha256": _canonical_hash(analysis),
        "setting_verdict": "INPUT_GATE_BLOCKED",
        "established": [
            "the complete arity-two D-derivation defect tensor on every q2 block exported by HT1",
            "D weights and particle-number changes for every nonzero selected residual q2 component",
            "exact D-weight neutrality of the selected ghost-momentum and bra-ket pairings",
        ],
        "claim_guards": [
            "zero selected residual defect is not a proof that the support-local interacting BV D-quotient is stable",
            "the unrestricted P_lin sector remains D-charged according to the imported classical setting ledger",
            "no iota_D^(2) is constructed without the full q1/q2 tensors and imported contraction",
            "q3, the arity-three L-infinity identity, boundary terms, and matter clocks are not computed",
            "this classical selected-model result is not a quantum correction or a LORENTZIAN-CAUSAL theorem",
        ],
        "input_gates": {
            "support_local_q2": "BLOCKED_MISSING_ARBITRARY_INPUT_TENSOR",
            "ghost_metric_q2_rows": "BLOCKED_MISSING_CLASSICAL_EXPORT",
            "antifield_q2_rows": "BLOCKED_MISSING_CLASSICAL_EXPORT",
            "q1_and_contraction_pi_cl_iota_cl_s_cl": "BLOCKED_UNFROZEN_IMPORT_GATE",
            "portable_cyclic_pairing": "BLOCKED_INCOMPLETE_CLASSICAL_EXPORT",
            "q3_contact_and_exchange": "NOT_COMPUTED",
            "boundary_BFV_extension": "NOT_IMPORTED",
            "scalar_clock_extension": "NOT_IMPLEMENTED",
        },
        "next_gate": "import the complete support-local q2 and contraction, recompute the full arity-two D defect, then solve for iota_D^(2) or retain its obstruction class",
        "provenance": {
            "HT1_transfer_payload_sha256": ht1["cubic_charge"]["transfer_payload_sha256"],
            "dependency_sha256": dependency_hashes,
            "dependency_manifest_sha256": _canonical_hash(dependency_hashes),
            "implementation_sha256": implementation_hashes,
            "implementation_manifest_sha256": _canonical_hash(implementation_hashes),
            "schema": "quantum-weyl/transfer/schema/selected-residual-d-derivation-v1.schema.json",
        },
    }
    validate_certificate(certificate)
    return certificate


def validate_certificate(certificate: object) -> None:
    if not isinstance(certificate, dict):
        raise ValueError("ND1 selected D-derivation certificate is malformed")
    if certificate.get("result_state") != "SELECTED_RESIDUAL_Q2_D_DEFECT_COMPUTED_FULL_LOCAL_INPUT_BLOCKED":
        raise ValueError("ND1 selected D-derivation lifecycle was over-promoted")
    if certificate.get("dependency_tags") != ["LOCAL-ALGEBRAIC", "REDUCED-MODE"]:
        raise ValueError("ND1 selected D-derivation dependency boundary changed")
    analysis = certificate.get("analysis_payload")
    if _canonical_hash(analysis) != certificate.get("analysis_payload_sha256"):
        raise ValueError("ND1 selected D-derivation analysis hash mismatch")
    ht1 = json.loads(HT1_PATH.read_text(encoding="utf-8"))
    expected_analysis = analyze_selected_q2(ht1.get("transfer_payload"))
    if analysis != expected_analysis:
        raise ValueError("ND1 selected D-derivation analysis disagrees with HT1")
    if certificate.get("setting_verdict") != "INPUT_GATE_BLOCKED":
        raise ValueError("ND1 full interacting D-quotient verdict was over-promoted")
    gates = certificate.get("input_gates")
    expected_gates = {
        "support_local_q2",
        "ghost_metric_q2_rows",
        "antifield_q2_rows",
        "q1_and_contraction_pi_cl_iota_cl_s_cl",
        "portable_cyclic_pairing",
        "q3_contact_and_exchange",
        "boundary_BFV_extension",
        "scalar_clock_extension",
    }
    if (
        not isinstance(gates, dict)
        or set(gates) != expected_gates
        or any(
            not str(status).startswith(("BLOCKED", "NOT_"))
            for status in gates.values()
        )
    ):
        raise ValueError("ND1 missing full-local input gate was promoted")
    provenance = certificate.get("provenance")
    if not isinstance(provenance, dict):
        raise ValueError("ND1 selected D-derivation provenance is missing")
    if provenance.get("HT1_transfer_payload_sha256") != ht1["cubic_charge"]["transfer_payload_sha256"]:
        raise ValueError("ND1 HT1 transfer payload hash mismatch")
    for manifest_key, root in (
        ("dependency_sha256", ROOT),
        ("implementation_sha256", TRANSFER_ROOT),
    ):
        manifest = provenance.get(manifest_key)
        if not isinstance(manifest, dict) or any(
            _sha256(root / path) != digest for path, digest in manifest.items()
        ):
            raise ValueError(f"ND1 {manifest_key} content hash mismatch")
        if _canonical_hash(manifest) != provenance.get(manifest_key.replace("sha256", "manifest_sha256")):
            raise ValueError(f"ND1 {manifest_key} manifest hash mismatch")


def render_certificate(value: dict[str, Any]) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"
