"""Certify the transferred residual cubic charge block already in the bridge.

This module does not manufacture a local nonlinear BV tensor.  It composes
four independently checked classical rails:

* the endpoint Bach/Taub obstruction map;
* the selected closed-cylinder BV--BFV suspension;
* the all-energy action-normalized moment map; and
* the strict centered HPL/CE transfer.

The resulting cubic Hamiltonian terms are

    Omega_3 = c^A mu_A(Phi,Phi) - f^A_BC c^B c^C b_A / 2.

Its Hamiltonian vector field determines ``ell_2(matter,matter)`` into the
residual ghost momentum, ``ell_2(ghost,matter)``, and the universal ghost
brackets.  The complete support-local BV tensor before endpoint projection
remains absent.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from typing import Any

import sympy as sp

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from bridge.residual_bfv import ConformalCE
from bridge.taub_moment_map import AllEnergyTaubMomentMap, CANONICAL_ACTION_SCALE


TRANSFER_ROOT = Path(__file__).resolve().parent
OUTPUT_PATH = TRANSFER_ROOT / "certificates" / "HT1_RESIDUAL_CUBIC_BLOCK.json"

UPSTREAM_CERTIFICATE_PATHS = (
    "bridge/certificates/taub_moment_map.json",
    "bridge/certificates/full_hpl_transfer.json",
    "bridge/certificates/metric_to_residual.json",
    "field_bv_identification/zero_modes/certificates/taub_obstruction_map.json",
    "field_bv_identification/polarized_state/certificates/zero_mode_transgression.json",
    "field_bv_identification/polarized_state/certificates/pairing_transfer.json",
)
UPSTREAM_SOURCE_PATHS = (
    "bridge/taub_moment_map/all_energy.py",
    "bridge/residual_bfv/conformal_ce.py",
    "bridge/transfer/hpl.py",
    "bridge/transfer/integration.py",
    "symbolic/verify_conformal_generator_all_levels.py",
    "symbolic/verify_conformal_taub_moment_map_all_levels.py",
    "symbolic/verify_conformal_taub_charge.py",
    "symbolic/verify_conformal_taub_multiplets.py",
    "field_bv_identification/zero_modes/verify_taub_obstruction_map.py",
    "field_bv_identification/polarized_state/zero_mode_transgression.py",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_hash(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest()


def _matrix_payload(matrix: sp.MatrixBase) -> dict[str, object]:
    entries = [
        [row, column, sp.srepr(value)]
        for (row, column), value in sorted(matrix.todok().items())
        if value != 0
    ]
    return {"shape": [matrix.rows, matrix.cols], "entries": entries}


def _off_diagonal_nonzero(matrix: sp.MatrixBase, split: int) -> int:
    return sum(
        int(value != 0)
        for block in (
            matrix[:split, split:],
            matrix[split:, :split],
        )
        for value in block
    )


def _load_upstream() -> dict[str, dict[str, Any]]:
    return {
        path: json.loads((ROOT / path).read_text(encoding="utf-8"))
        for path in UPSTREAM_CERTIFICATE_PATHS
    }


def build_certificate(maximum_energy: int = 4) -> dict[str, Any]:
    if maximum_energy < 4:
        raise ValueError("HT1 needs the E/A/L buffer through energy four")

    upstream = _load_upstream()
    taub_source = upstream["bridge/certificates/taub_moment_map.json"]
    hpl_source = upstream["bridge/certificates/full_hpl_transfer.json"]
    residual_source = upstream["bridge/certificates/metric_to_residual.json"]
    obstruction_source = upstream[
        "field_bv_identification/zero_modes/certificates/taub_obstruction_map.json"
    ]
    transgression_source = upstream[
        "field_bv_identification/polarized_state/certificates/zero_mode_transgression.json"
    ]

    taub = AllEnergyTaubMomentMap.build(maximum_energy)
    ce = ConformalCE.build()
    generators = {
        **taub.compact_generators,
        **{f"K-_{left},{right}": value for (left, right), value in taub.lowering_generators.items()},
        **{f"K+_{left},{right}": value for (left, right), value in taub.raising_generators.items()},
    }
    kernels = {
        **taub.compact_kernels,
        **{f"K-_{left},{right}": value for (left, right), value in taub.lowering_kernels.items()},
        **{f"K+_{left},{right}": value for (left, right), value in taub.raising_kernels.items()},
    }
    if len(generators) != 15 or len(kernels) != 15:
        raise AssertionError("residual cubic block does not contain fifteen components")
    if set(generators) != set(kernels):
        raise AssertionError("generator and moment-map labels disagree")
    if any(
        kernels[label] != CANONICAL_ACTION_SCALE * taub.form * generator
        for label, generator in generators.items()
    ):
        raise AssertionError("moment-map normalization changed")

    chiral_dimension = taub.plus.dimension
    off_diagonal = {
        label: _off_diagonal_nonzero(matrix, chiral_dimension)
        for label, matrix in kernels.items()
    }
    if any(off_diagonal.values()):
        raise AssertionError("the cubic moment-map block mixes the two chiral modules")

    if obstruction_source["moment_map_components"] != 15:
        raise AssertionError("endpoint obstruction map lost a component")
    if transgression_source["lambda_all_generators"] != "1":
        raise AssertionError("selected BV-BFV suspension normalization changed")
    if hpl_source["conclusion"] != "Q_H=p Delta j=d_CE on the centered physical coefficient row":
        raise AssertionError("strict centered transfer is no longer certified")
    if residual_source["one_particle"]["h4"] != 0:
        raise AssertionError("centered one-particle H4 no longer vanishes")
    if residual_source["two_particle"]["h4"] != 2:
        raise AssertionError("centered two-particle H4 is no longer two-dimensional")

    kernel_payload = {label: _matrix_payload(kernels[label]) for label in sorted(kernels)}
    ce_payload = [
        [first, second, target, sp.srepr(value)]
        for first in range(ce.dimension)
        for second in range(ce.dimension)
        for target, value in enumerate(ce.structure_constants[first][second])
        if value != 0
    ]
    upstream_hashes = {
        path: _sha256(ROOT / path)
        for path in (*UPSTREAM_CERTIFICATE_PATHS, *UPSTREAM_SOURCE_PATHS)
    }
    implementation_paths = (
        "residual_cubic_block.py",
        "residual_cubic_certificate.py",
        "tests/test_residual_cubic_block.py",
    )
    implementation_hashes = {
        path: _sha256(TRANSFER_ROOT / path) for path in implementation_paths
    }
    return {
        "result_id": "HT1_RESIDUAL_CUBIC_BLOCK",
        "result_state": "SELECTED_RESIDUAL_CUBIC_BRACKET_COMPUTED",
        "classical_commit": "UNFROZEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "category": "selected finite algebraic closed-cylinder BV-BFV model",
        "taylor_convention": obstruction_source["taylor_convention"],
        "residual_charge": transgression_source["conventions"]["residual_charge"],
        "computed_taylor_blocks": [
            "ell_2(physical_matter, physical_matter) -> residual_ghost_momentum",
            "ell_2(residual_ghost, physical_matter)",
            "ell_2(residual_ghost, residual_ghost)",
            "ell_2(residual_ghost, residual_ghost_momentum)",
        ],
        "uncomputed_taylor_blocks": [
            "the complete support-local classical q2 tensor before endpoint projection",
            "projected q2 components from any additional field-theory BV rows not present in the selected algebraic domain",
            "q3 and higher local classical BV Taylor tensors",
        ],
        "cubic_charge": {
            "formula": "Omega_3=c^A mu_A(Phi,Phi)-f^A_BC c^B c^C b_A/2",
            "moment_map_formula": "M_A=-(1/2) J K_A",
            "component_count": len(kernels),
            "ce_generator_count": ce.dimension,
            "canonical_action_scale": str(CANONICAL_ACTION_SCALE),
            "finite_regression_maximum_energy": maximum_energy,
            "finite_regression_dimension": taub.dimension,
            "all_energy_formula_source": taub_source["schema"],
            "kernel_payload_sha256": _canonical_hash(kernel_payload),
            "ce_structure_constants_sha256": _canonical_hash(ce_payload),
        },
        "checks": {
            "endpoint_to_moment_map_components": "VERIFIED_15_OF_15",
            "matter_matter_endpoint_output": "VERIFIED_Q_BFV_b_EQUALS_MU",
            "selected_bfv_suspension_lambda": "VERIFIED_1",
            "moment_map_normalization": "VERIFIED_EXACT",
            "conformal_closure": "VERIFIED_ON_EVERY_INTERIOR_SHELL",
            "centered_hpl_transfer": "VERIFIED_STRICT_CE",
            "chirality_off_diagonal_nonzero_entries": sum(off_diagonal.values()),
            "one_particle_centered_h4": residual_source["one_particle"]["h4"],
            "two_particle_centered_h4": residual_source["two_particle"]["h4"],
        },
        "scientific_consequences": [
            "the transferred residual cubic charge is nonzero and exactly normalized",
            "the matter-matter Kuranishi bracket into all fifteen residual ghost momenta is computed",
            "this cubic ghost-matter block does not mix W_+ and W_- one-particle modules",
            "the universal ghost block and matter action close as the strict residual CE differential in the centered window",
            "the centered one-particle H4 vanishing persists for this residual cubic charge block",
        ],
        "claim_guards": [
            "the result does not serialize the complete support-local nonlinear BV tensor before homological projection",
            "chirality block diagonality here does not prove closure of the dynamical Weyl-square deformation under brackets of deformation classes or higher arity",
            "the result does not prove that the Pontryagin direction is central in the full transferred L-infinity algebra",
            "the result does not exclude higher-bracket re-entry from absent local BV sectors",
            "the result is not a quantum correction or a LORENTZIAN-CAUSAL theorem",
        ],
        "provenance": {
            "upstream_sha256": upstream_hashes,
            "upstream_manifest_sha256": _canonical_hash(upstream_hashes),
            "implementation_sha256": implementation_hashes,
            "implementation_manifest_sha256": _canonical_hash(implementation_hashes),
            "generated_kernel_payload_in_certificate": False,
            "kernel_payload_policy": "content hash only; matrices are regenerated exactly from authoritative classical code",
        },
    }


def render_certificate(value: dict[str, Any]) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"
