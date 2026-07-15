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

from bridge.taub_moment_map import AllEnergyTaubMomentMap, CANONICAL_ACTION_SCALE
from symbolic.verify_conformal_global_brst_window import LieData, build_lie_data
from symbolic.verify_conformal_taub_multiplets import MAGNETIC_COMPONENTS


TRANSFER_ROOT = Path(__file__).resolve().parent
OUTPUT_PATH = TRANSFER_ROOT / "certificates" / "HT1_RESIDUAL_CUBIC_BLOCK.json"
SCHEMA_PATH = TRANSFER_ROOT / "schema" / "residual-cubic-block-v2.schema.json"

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
    "symbolic/verify_conformal_generator_ansatz.py",
    "symbolic/verify_conformal_global_brst_window.py",
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
        [int(row), int(column), sp.srepr(value)]
        for (row, column), value in sorted(matrix.todok().items())
        if value != 0
    ]
    return {
        "shape": [matrix.rows, matrix.cols],
        "scalar_format": "sympy-srepr-exact-v1",
        "entries": entries,
    }


def _exact_scalar(value: object) -> sp.Expr:
    if not isinstance(value, str) or "Float" in value:
        raise ValueError("portable transfer scalars must be exact SymPy srepr strings")
    result = sp.sympify(value)
    if result.atoms(sp.Float):
        raise ValueError("portable transfer payload contains floating-point data")
    return result


def _matrix_from_payload(value: object, label: str) -> sp.SparseMatrix:
    if not isinstance(value, dict):
        raise ValueError(f"{label} is not a matrix payload")
    if value.get("scalar_format") != "sympy-srepr-exact-v1":
        raise ValueError(f"{label} has an unsupported scalar format")
    shape = value.get("shape")
    entries = value.get("entries")
    if (
        not isinstance(shape, list)
        or len(shape) != 2
        or not all(isinstance(item, int) and item >= 0 for item in shape)
        or not isinstance(entries, list)
    ):
        raise ValueError(f"{label} has an invalid shape or entry list")
    parsed: dict[tuple[int, int], sp.Expr] = {}
    previous: tuple[int, int] | None = None
    for entry in entries:
        if not isinstance(entry, list) or len(entry) != 3:
            raise ValueError(f"{label} contains a malformed sparse entry")
        row, column, scalar = entry
        coordinate = (row, column)
        if (
            not isinstance(row, int)
            or not isinstance(column, int)
            or not 0 <= row < shape[0]
            or not 0 <= column < shape[1]
            or (previous is not None and coordinate <= previous)
        ):
            raise ValueError(f"{label} sparse coordinates are invalid or unsorted")
        parsed[coordinate] = _exact_scalar(scalar)
        if parsed[coordinate] == 0:
            raise ValueError(f"{label} serializes an explicit zero")
        previous = coordinate
    return sp.SparseMatrix(shape[0], shape[1], parsed)


def _tensor_payload(structure: tuple[tuple[tuple[sp.Expr, ...], ...], ...]) -> dict[str, object]:
    dimension = len(structure)
    return {
        "shape": [dimension, dimension, dimension],
        "scalar_format": "sympy-srepr-exact-v1",
        "entries": [
            [first, second, target, sp.srepr(value)]
            for first in range(dimension)
            for second in range(dimension)
            for target, value in enumerate(structure[first][second])
            if value != 0
        ],
    }


def _tensor_from_payload(value: object, dimension: int) -> tuple[tuple[tuple[sp.Expr, ...], ...], ...]:
    if not isinstance(value, dict):
        raise ValueError("structure constants are not a tensor payload")
    if value.get("shape") != [dimension, dimension, dimension]:
        raise ValueError("structure-constant tensor has the wrong shape")
    if value.get("scalar_format") != "sympy-srepr-exact-v1":
        raise ValueError("structure-constant tensor has an unsupported scalar format")
    entries = value.get("entries")
    if not isinstance(entries, list):
        raise ValueError("structure-constant entries are missing")
    raw = [
        [[sp.Integer(0) for _ in range(dimension)] for _ in range(dimension)]
        for _ in range(dimension)
    ]
    previous: tuple[int, int, int] | None = None
    for entry in entries:
        if not isinstance(entry, list) or len(entry) != 4:
            raise ValueError("structure constants contain a malformed sparse entry")
        first, second, target, scalar = entry
        coordinate = (first, second, target)
        if (
            not all(isinstance(item, int) and 0 <= item < dimension for item in coordinate)
            or (previous is not None and coordinate <= previous)
        ):
            raise ValueError("structure-constant coordinates are invalid or unsorted")
        raw[first][second][target] = _exact_scalar(scalar)
        if raw[first][second][target] == 0:
            raise ValueError("structure constants serialize an explicit zero")
        previous = coordinate
    return tuple(tuple(tuple(row) for row in matrix) for matrix in raw)


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


def _ordered_taub_data(
    taub: AllEnergyTaubMomentMap,
) -> tuple[tuple[str, ...], tuple[sp.Matrix, ...], tuple[sp.Matrix, ...]]:
    names = (
        "D",
        "Lx", "Ly", "Lz",
        "Rx", "Ry", "Rz",
        *(f"K-_{left}_{right}" for left, right in MAGNETIC_COMPONENTS),
        *(f"K+_{left}_{right}" for left, right in MAGNETIC_COMPONENTS),
    )
    generators = (
        *(taub.compact_generators[name] for name in names[:7]),
        *(taub.lowering_generators[component] for component in MAGNETIC_COMPONENTS),
        *(taub.raising_generators[component] for component in MAGNETIC_COMPONENTS),
    )
    kernels = (
        *(taub.compact_kernels[name] for name in names[:7]),
        *(taub.lowering_kernels[component] for component in MAGNETIC_COMPONENTS),
        *(taub.raising_kernels[component] for component in MAGNETIC_COMPONENTS),
    )
    return names, generators, kernels


def _certify_common_magnetic_basis(
    taub: AllEnergyTaubMomentMap,
) -> tuple[LieData, tuple[str, ...], tuple[sp.Matrix, ...], tuple[sp.Matrix, ...]]:
    plus = build_lie_data(1)
    minus = build_lie_data(-1)
    names, generators, kernels = _ordered_taub_data(taub)
    if plus.names != names or minus.names != names:
        raise AssertionError("magnetic BRST and Taub generator labels disagree")
    if plus.degrees != minus.degrees or plus.structure != minus.structure:
        raise AssertionError("the two chiral modules do not carry one common magnetic Lie algebra")
    for chirality, lie, offset, source in (
        ("plus", plus, 0, taub.plus),
        ("minus", minus, taub.plus.dimension, taub.minus),
    ):
        blocks = tuple(
            sp.Matrix(matrix[offset : offset + source.dimension, offset : offset + source.dimension])
            for matrix in generators
        )
        if blocks != lie.matrices:
            raise AssertionError(
                f"{chirality} magnetic BRST matrices do not equal the Taub generators"
            )
    return plus, names, generators, kernels


def _zero_on_sources(matrix: sp.MatrixBase, sources: tuple[int, ...]) -> bool:
    return not any(matrix[:, sources])


def _master_equation_checks(
    structure: tuple[tuple[tuple[sp.Expr, ...], ...], ...],
    generators: tuple[sp.Matrix, ...],
    kernels: tuple[sp.Matrix, ...],
    poisson_inverse: sp.MatrixBase,
    source_indices: tuple[int, ...],
) -> dict[str, object]:
    dimension = len(structure)
    if not (
        dimension == len(generators) == len(kernels) == 15
        and all(len(matrix) == dimension for matrix in structure)
    ):
        raise AssertionError("cubic master-equation input has the wrong dimension")
    antisymmetry_defects = sum(
        int(sp.simplify(structure[a][b][c] + structure[b][a][c]) != 0)
        for a in range(dimension)
        for b in range(dimension)
        for c in range(dimension)
    )
    jacobi_defects = sum(
        int(
            sp.simplify(
                sum(
                    structure[b][c][middle] * structure[a][middle][target]
                    + structure[c][a][middle] * structure[b][middle][target]
                    + structure[a][b][middle] * structure[c][middle][target]
                    for middle in range(dimension)
                )
            )
            != 0
        )
        for a in range(dimension)
        for b in range(dimension)
        for c in range(dimension)
        for target in range(dimension)
    )
    representation_defects = 0
    moment_map_defects = 0
    zero = sp.zeros(generators[0].rows)
    for first in range(dimension):
        for second in range(dimension):
            generator_target = sum(
                (
                    structure[first][second][target] * generators[target]
                    for target in range(dimension)
                ),
                zero,
            )
            representation_defects += int(
                not _zero_on_sources(
                    generators[first] * generators[second]
                    - generators[second] * generators[first]
                    - generator_target,
                    source_indices,
                )
            )
            kernel_target = sum(
                (
                    structure[first][second][target] * kernels[target]
                    for target in range(dimension)
                ),
                zero,
            )
            moment_map_defects += int(
                not _zero_on_sources(
                    kernels[first] * poisson_inverse * kernels[second]
                    - kernels[second] * poisson_inverse * kernels[first]
                    - kernel_target,
                    source_indices,
                )
            )
    if any((antisymmetry_defects, jacobi_defects, representation_defects, moment_map_defects)):
        raise AssertionError("the selected cubic BFV Hamiltonian fails its master equation")
    return {
        "bracket_half_formula": "{Omega_3,Omega_3}/2=cc({mu,mu}-f.mu)+cccb.Jacobi",
        "checked_source_column_count": len(source_indices),
        "structure_antisymmetry_defects": antisymmetry_defects,
        "ghost_jacobi_defects": jacobi_defects,
        "ghost_matter_representation_defects": representation_defects,
        "matter_moment_map_equivariance_defects": moment_map_defects,
        "total_nonzero_coefficient_blocks": 0,
        "status": "VERIFIED_EXACT_CUBIC_MASTER_EQUATION",
    }


def _build_transfer_payload(
    taub: AllEnergyTaubMomentMap,
    lie: LieData,
    names: tuple[str, ...],
    generators: tuple[sp.Matrix, ...],
    kernels: tuple[sp.Matrix, ...],
) -> dict[str, object]:
    symplectic_form = sp.Matrix(CANONICAL_ACTION_SCALE * taub.form)
    poisson_inverse = sp.Matrix(taub.form / CANONICAL_ACTION_SCALE)
    matter_basis = []
    for chirality, offset, space in (
        (1, 0, taub.plus),
        (-1, taub.plus.dimension, taub.minus),
    ):
        for mode in space.irreps:
            for local_index, (magnetic_left, magnetic_right) in enumerate(mode.basis):
                matter_basis.append(
                    {
                        "index": offset + space.offsets[mode.label] + local_index,
                        "chirality": chirality,
                        "tower": mode.label[0],
                        "energy": mode.energy,
                        "left_spin": sp.srepr(mode.left),
                        "right_spin": sp.srepr(mode.right),
                        "magnetic_left": sp.srepr(magnetic_left),
                        "magnetic_right": sp.srepr(magnetic_right),
                    }
                )
    return {
        "schema_version": 2,
        "scalar_format": "sympy-srepr-exact-v1",
        "basis": [
            {
                "index": index,
                "name": name,
                "generator_degree": lie.degrees[index],
                "ghost_degree": -lie.degrees[index],
                "generator_parity": "even",
                "ghost_parity": "odd",
                "ghost_momentum_parity": "odd",
            }
            for index, name in enumerate(names)
        ],
        "structure_constants": _tensor_payload(lie.structure),
        "matter_phase_space": {
            "basis": "W_plus_energy_lexicographic_then_W_minus_energy_lexicographic",
            "ordered_basis": matter_basis,
            "polarization": "independent_barPhi_Phi_blocks; displayed matrices are the off-diagonal pairing and Poisson blocks",
            "dimension": taub.dimension,
            "chiral_dimension": taub.plus.dimension,
            "finite_regression_maximum_energy": taub.maximum_energy,
            "master_equation_source_indices": list(taub.indices_through(3)),
            "canonical_action_scale": sp.srepr(CANONICAL_ACTION_SCALE),
            "action_scaled_symplectic_form": _matrix_payload(symplectic_form),
            "poisson_inverse": _matrix_payload(poisson_inverse),
        },
        "q2": {
            "ghost_ghost_to_ghost": {
                "convention": "ell_2(c_A,c_B)=f_AB^C c_C",
                "tensor": _tensor_payload(lie.structure),
            },
            "ghost_matter_to_matter": {
                "convention": "ell_2(c_A,Phi)=K_A Phi",
                "matrices": {
                    name: _matrix_payload(matrix)
                    for name, matrix in zip(names, generators)
                },
            },
            "matter_matter_to_ghost_momentum": {
                "convention": "mu_A(barPhi,Phi)=barPhi M_A Phi",
                "matrices": {
                    name: _matrix_payload(matrix)
                    for name, matrix in zip(names, kernels)
                },
            },
            "ghost_ghost_momentum_to_ghost_momentum": {
                "convention": "coadjoint action determined by f_AB^C",
                "tensor_reference": "structure_constants",
            },
        },
    }


def validate_transfer_payload(payload: object) -> dict[str, object]:
    """Fail-closed validation of the portable selected residual q2 payload."""

    if not isinstance(payload, dict) or payload.get("schema_version") != 2:
        raise ValueError("residual cubic payload has the wrong schema version")
    if payload.get("scalar_format") != "sympy-srepr-exact-v1":
        raise ValueError("residual cubic payload has the wrong scalar format")
    basis = payload.get("basis")
    if not isinstance(basis, list) or len(basis) != 15:
        raise ValueError("residual cubic payload needs fifteen ordered generators")
    expected_names = (
        "D", "Lx", "Ly", "Lz", "Rx", "Ry", "Rz",
        *(f"K-_{left}_{right}" for left, right in MAGNETIC_COMPONENTS),
        *(f"K+_{left}_{right}" for left, right in MAGNETIC_COMPONENTS),
    )
    names = tuple(item.get("name") if isinstance(item, dict) else None for item in basis)
    if names != expected_names or any(
        item.get("index") != index for index, item in enumerate(basis) if isinstance(item, dict)
    ):
        raise ValueError("residual cubic magnetic basis identity or ordering changed")
    expected_degrees = (0,) * 7 + (-1,) * 4 + (1,) * 4
    if tuple(item.get("generator_degree") for item in basis) != expected_degrees:
        raise ValueError("residual cubic generator grading changed")
    if any(
        item.get("ghost_degree") != -expected_degrees[index]
        or item.get("generator_parity") != "even"
        or item.get("ghost_parity") != "odd"
        or item.get("ghost_momentum_parity") != "odd"
        for index, item in enumerate(basis)
    ):
        raise ValueError("residual cubic degree/parity declarations changed")

    matter = payload.get("matter_phase_space")
    q2 = payload.get("q2")
    if not isinstance(matter, dict) or not isinstance(q2, dict):
        raise ValueError("residual cubic matter or q2 payload is missing")
    scale = _exact_scalar(matter.get("canonical_action_scale"))
    if scale != CANONICAL_ACTION_SCALE:
        raise ValueError("canonical action scale changed")
    dimension = matter.get("dimension")
    source_indices_raw = matter.get("master_equation_source_indices")
    if not isinstance(dimension, int) or not isinstance(source_indices_raw, list):
        raise ValueError("matter dimension or master-equation source window is invalid")
    source_indices = tuple(source_indices_raw)
    if not source_indices or any(
        not isinstance(index, int) or not 0 <= index < dimension for index in source_indices
    ):
        raise ValueError("master-equation source indices are invalid")
    matter_basis = matter.get("ordered_basis")
    if not isinstance(matter_basis, list) or len(matter_basis) != dimension:
        raise ValueError("ordered matter basis is missing or has the wrong dimension")
    for index, state in enumerate(matter_basis):
        if (
            not isinstance(state, dict)
            or state.get("index") != index
            or state.get("chirality") not in (-1, 1)
            or state.get("tower") not in ("E", "A", "L")
            or not isinstance(state.get("energy"), int)
        ):
            raise ValueError("ordered matter basis contains an invalid state")
        for key in ("left_spin", "right_spin", "magnetic_left", "magnetic_right"):
            _exact_scalar(state.get(key))
    if sum(state["chirality"] == 1 for state in matter_basis) != matter.get("chiral_dimension"):
        raise ValueError("ordered matter basis has the wrong chiral split")
    expected_sources = tuple(
        state["index"] for state in matter_basis if state["energy"] <= 3
    )
    if source_indices != expected_sources:
        raise ValueError("master-equation source window disagrees with the ordered matter basis")
    symplectic_form = _matrix_from_payload(
        matter.get("action_scaled_symplectic_form"), "action-scaled symplectic form"
    )
    poisson_inverse = _matrix_from_payload(matter.get("poisson_inverse"), "Poisson inverse")
    if symplectic_form.shape != (dimension, dimension) or poisson_inverse.shape != (dimension, dimension):
        raise ValueError("matter symplectic matrices have the wrong dimension")
    if symplectic_form * poisson_inverse != sp.eye(dimension):
        raise ValueError("action-scaled symplectic form and Poisson inverse do not invert")

    structure = _tensor_from_payload(payload.get("structure_constants"), 15)
    ghost_block = q2.get("ghost_ghost_to_ghost")
    action_block = q2.get("ghost_matter_to_matter")
    moment_block = q2.get("matter_matter_to_ghost_momentum")
    if not all(isinstance(block, dict) for block in (ghost_block, action_block, moment_block)):
        raise ValueError("portable q2 blocks are incomplete")
    if _tensor_from_payload(ghost_block.get("tensor"), 15) != structure:
        raise ValueError("ghost q2 tensor disagrees with the declared Lie algebra")
    action_payloads = action_block.get("matrices")
    moment_payloads = moment_block.get("matrices")
    if (
        not isinstance(action_payloads, dict)
        or not isinstance(moment_payloads, dict)
        or tuple(action_payloads) != names
        or tuple(moment_payloads) != names
    ):
        raise ValueError("portable q2 matrix components are missing or reordered")
    generators = tuple(
        sp.Matrix(_matrix_from_payload(action_payloads[name], f"generator {name}"))
        for name in names
    )
    kernels = tuple(
        sp.Matrix(_matrix_from_payload(moment_payloads[name], f"moment-map kernel {name}"))
        for name in names
    )
    if any(matrix.shape != (dimension, dimension) for matrix in (*generators, *kernels)):
        raise ValueError("portable q2 matrix has the wrong dimension")
    if any(kernel != symplectic_form * generator for generator, kernel in zip(generators, kernels)):
        raise ValueError("portable moment-map kernel normalization changed")
    return _master_equation_checks(
        structure,
        generators,
        kernels,
        poisson_inverse,
        source_indices,
    )


def validate_certificate(certificate: object) -> None:
    """Validate payload and bind every declared input to the current checkout."""

    if not isinstance(certificate, dict):
        raise ValueError("HT1 certificate is not an object")
    if certificate.get("dependency_tags") != ["LOCAL-ALGEBRAIC", "REDUCED-MODE"]:
        raise ValueError("HT1 dependency boundary changed")
    provenance = certificate.get("provenance")
    if not isinstance(provenance, dict):
        raise ValueError("HT1 provenance is missing")
    upstream = provenance.get("upstream_sha256")
    if not isinstance(upstream, dict) or any(
        _sha256(ROOT / path) != digest for path, digest in upstream.items()
    ):
        raise ValueError("HT1 upstream content hash mismatch")
    if _canonical_hash(upstream) != provenance.get("upstream_manifest_sha256"):
        raise ValueError("HT1 upstream manifest hash mismatch")
    implementation = provenance.get("implementation_sha256")
    if not isinstance(implementation, dict) or any(
        _sha256(TRANSFER_ROOT / path) != digest for path, digest in implementation.items()
    ):
        raise ValueError("HT1 implementation content hash mismatch")
    if _canonical_hash(implementation) != provenance.get("implementation_manifest_sha256"):
        raise ValueError("HT1 implementation manifest hash mismatch")
    payload = certificate.get("transfer_payload")
    if _canonical_hash(payload) != certificate.get("cubic_charge", {}).get("transfer_payload_sha256"):
        raise ValueError("HT1 portable payload content hash mismatch")
    validate_transfer_payload(payload)


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
    lie, names, generators, kernels = _certify_common_magnetic_basis(taub)
    if len(generators) != 15 or len(kernels) != 15:
        raise AssertionError("residual cubic block does not contain fifteen components")
    if any(
        kernel != CANONICAL_ACTION_SCALE * taub.form * generator
        for generator, kernel in zip(generators, kernels)
    ):
        raise AssertionError("moment-map normalization changed")

    chiral_dimension = taub.plus.dimension
    off_diagonal = {
        label: _off_diagonal_nonzero(matrix, chiral_dimension)
        for label, matrix in zip(names, kernels)
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

    transfer_payload = _build_transfer_payload(taub, lie, names, generators, kernels)
    master_equation = validate_transfer_payload(transfer_payload)
    upstream_hashes = {
        path: _sha256(ROOT / path)
        for path in (*UPSTREAM_CERTIFICATE_PATHS, *UPSTREAM_SOURCE_PATHS)
    }
    implementation_paths = (
        "residual_cubic_block.py",
        "residual_cubic_certificate.py",
        "schema/residual-cubic-block-v2.schema.json",
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
            "ce_generator_count": len(lie.names),
            "canonical_action_scale": str(CANONICAL_ACTION_SCALE),
            "finite_regression_maximum_energy": maximum_energy,
            "finite_regression_dimension": taub.dimension,
            "all_energy_formula_source": taub_source["schema"],
            "transfer_payload_sha256": _canonical_hash(transfer_payload),
        },
        "transfer_payload": transfer_payload,
        "checks": {
            "endpoint_to_moment_map_components": "VERIFIED_15_OF_15",
            "matter_matter_endpoint_output": "VERIFIED_Q_BFV_b_EQUALS_MU",
            "selected_bfv_suspension_lambda": "VERIFIED_1",
            "moment_map_normalization": "VERIFIED_EXACT",
            "common_magnetic_basis": "VERIFIED_ENTRYWISE_BOTH_CHIRALITIES",
            "conformal_closure": "VERIFIED_ON_EVERY_INTERIOR_SHELL",
            "cubic_master_equation": master_equation,
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
            "the complete selected cubic BFV Hamiltonian obeys its exact master equation on the certified finite regression window",
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
            "generated_kernel_payload_in_certificate": True,
            "kernel_payload_policy": "ordered exact sparse q2 payload plus content hash; regenerated from authoritative classical code",
            "schema": "quantum-weyl/transfer/schema/residual-cubic-block-v2.schema.json",
        },
    }


def render_certificate(value: dict[str, Any]) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"
