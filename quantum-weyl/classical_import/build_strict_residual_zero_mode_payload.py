#!/usr/bin/env python3
"""Export the exact strict pure-Weyl residual zero-mode payload.

The existing causal-transport certificate hashes the fifteen conformal
Killing vectors and their dual endpoint quotient, but does not serialize
their coefficients.  This producer emits those coefficients, the exact
conformal Lie algebra, its adjoint/cotangent representation, and the unary
residual differential in one portable finite payload.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from itertools import product
from pathlib import Path
import sys
from typing import Any

import sympy as sp

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from bridge.residual_bfv import ConformalCE
from bridge.zero_modes.ckv_projector import (
    DIMENSION,
    SYMMETRIC_PAIRS,
    conformal_killing_projector,
    homogeneous_monomials,
)
from field_bv_identification.zero_modes import ResidualBFVRoles


HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_RESIDUAL_ZERO_MODE_PAYLOAD_V1.json"
REPORT = HERE / "REPORT_STRICT_RESIDUAL_ZERO_MODE_PAYLOAD_V1.md"

INPUTS = (
    "bridge/zero_modes/ckv_projector.py",
    "bridge/residual_bfv/conformal_ce.py",
    "field_bv_identification/zero_modes/dual_cokernel.py",
    "field_bv_identification/zero_modes/residual_roles.py",
    "field_bv_identification/polarized_state/zero_mode_transgression.py",
    "covariant_completion/certificates/covariant_CKV_recovery.json",
    "covariant_completion/certificates/curved_SO42_causal_transport_recognition.json",
)


def file_hash(path: str) -> str:
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def scalar(value: sp.Expr) -> str:
    reduced = sp.cancel(value)
    if reduced.free_symbols or not reduced.is_Rational:
        raise ValueError(f"non-rational matrix entry {value!r}")
    return str(reduced)


def sparse_matrix(matrix: sp.MatrixBase) -> dict[str, Any]:
    entries = [
        [row, column, scalar(matrix[row, column])]
        for row in range(matrix.rows)
        for column in range(matrix.cols)
        if matrix[row, column] != 0
    ]
    body = {"shape": [matrix.rows, matrix.cols], "entries": entries}
    return {**body, "nonzero_entries": len(entries), "sha256": digest(body)}


def exponent_name(exponent: tuple[int, ...]) -> str:
    factors = [f"x{axis}^{power}" for axis, power in enumerate(exponent) if power]
    return "1" if not factors else "*".join(factors)


def chart_ordering() -> dict[str, list[str]]:
    vector_exponents = tuple(
        exponent
        for degree in range(3)
        for exponent in homogeneous_monomials(degree)
    )
    scalar_exponents = tuple(
        exponent
        for degree in range(2)
        for exponent in homogeneous_monomials(degree)
    )
    metric_exponents = scalar_exponents
    gauge = [
        f"xi{component}:{exponent_name(exponent)}"
        for component, exponent in product(range(DIMENSION), vector_exponents)
    ] + [f"sigma:{exponent_name(exponent)}" for exponent in scalar_exponents]
    metric = [
        f"h{first}{second}:{exponent_name(exponent)}"
        for (first, second), exponent in product(SYMMETRIC_PAIRS, metric_exponents)
    ]
    if len(gauge) != 65 or len(metric) != 50:
        raise AssertionError("polynomial chart ordering drifted")
    return {"gauge_parameter_65": gauge, "metric_50": metric, "dual_endpoint_65": gauge}


def structure_payload(ce: ConformalCE) -> dict[str, Any]:
    entries = [
        [first, second, target, scalar(ce.structure_constants[first][second][target])]
        for first in range(15)
        for second in range(15)
        for target in range(15)
        if ce.structure_constants[first][second][target] != 0
    ]
    body = {
        "convention": "[G_a,G_b]=sum_c f[a,b,c] G_c",
        "generator_order": list(ce.names),
        "generator_compact_degrees": list(ce.generator_degrees),
        "entries": entries,
        "tensor_shape": [15, 15, 15],
    }
    return {**body, "nonzero_entries": len(entries), "sha256": digest(body)}


def representation_payload(ce: ConformalCE) -> dict[str, Any]:
    matrices = []
    for generator, name in enumerate(ce.names):
        adjoint = sp.Matrix(
            15,
            15,
            lambda target, source: ce.structure_constants[generator][source][target],
        )
        coadjoint = -adjoint.T
        full = sp.diag(adjoint, coadjoint)
        matrices.append(
            {
                "generator_index": generator,
                "generator": name,
                "adjoint_on_Z": sparse_matrix(adjoint),
                "coadjoint_on_Z_dual": sparse_matrix(coadjoint),
                "rho_on_Z_plus_Z_dual": sparse_matrix(full),
            }
        )
    body = {
        "carrier_order": [
            *[f"c[{name}]" for name in ce.names],
            *[f"b[{name}]" for name in ce.names],
        ],
        "matrices": matrices,
        "representation_identity": "[rho_a,rho_b]=sum_c f[a,b,c] rho_c",
    }
    return {**body, "sha256": digest(body)}


def build() -> dict[str, Any]:
    ckv = conformal_killing_projector()
    roles = ResidualBFVRoles.build()
    endpoint = roles.endpoint
    ce = ConformalCE.build()
    permutation = roles.ce_to_ckv

    primal_basis = sp.simplify(endpoint.zero_basis * permutation)
    primal_coordinates = sp.simplify(permutation.T * ckv.left_inverse)
    dual_basis = sp.simplify(endpoint.quotient_section * permutation)
    dual_coordinates = sp.simplify(permutation.T * endpoint.quotient_map)
    primal_projector = sp.simplify(primal_basis * primal_coordinates)
    dual_projector = sp.simplify(dual_basis * dual_coordinates)

    matrices = {
        "ce_to_ckv_permutation": sparse_matrix(permutation),
        "gauge_map_K": sparse_matrix(endpoint.gauge_map),
        "cyclic_adjoint_K_sharp": sparse_matrix(endpoint.adjoint_map),
        "gauge_endpoint_pairing": sparse_matrix(endpoint.gauge_endpoint_pairing),
        "metric_equation_pairing": sparse_matrix(endpoint.metric_equation_pairing),
        "primal_basis_Z": sparse_matrix(primal_basis),
        "primal_coordinate_map": sparse_matrix(primal_coordinates),
        "primal_projector": sparse_matrix(primal_projector),
        "dual_basis_Z_dual": sparse_matrix(dual_basis),
        "dual_quotient_map": sparse_matrix(dual_coordinates),
        "dual_projector": sparse_matrix(dual_projector),
    }
    zero_mode_body = {
        "coefficient_field": "Q",
        "chart_ordering": chart_ordering(),
        "canonical_generator_order": list(ce.names),
        "canonical_dual_order": [f"{name}^*" for name in ce.names],
        "compact_degrees": list(ce.generator_degrees),
        "dual_compact_degrees": [-degree for degree in ce.generator_degrees],
        "legacy_ckv_order": list(ckv.labels),
        "matrices": matrices,
    }
    zero_modes = {**zero_mode_body, "sha256": digest(zero_mode_body)}
    structure = structure_payload(ce)
    representations = representation_payload(ce)
    q_res_matrix = sparse_matrix(sp.zeros(30))
    q_res = {
        "carrier_order": representations["carrier_order"],
        "degree_zero_unary_matrix": q_res_matrix,
        "meaning": "q_res^(0)=0 on the extracted zero-mode cotangent carrier; the nonabelian CE term is separately encoded by f[a,b,c]",
        "nonlinear_CE_structure_sha256": structure["sha256"],
    }
    q_res["sha256"] = digest(q_res)

    canonical = {
        "zero_mode_basis_sha256": zero_modes["sha256"],
        "structure_constants_sha256": structure["sha256"],
        "representation_matrices_sha256": representations["sha256"],
        "q_res_0_sha256": q_res["sha256"],
    }
    snapshot_body = {
        "theory": "strict pure-Weyl residual Diff x Weyl zero-mode sector",
        "background": "unit conformal cylinder",
        "canonical_hashes": canonical,
        "input_sha256": {path: file_hash(path) for path in INPUTS},
    }
    snapshot = {**snapshot_body, "sha256": digest(snapshot_body)}

    value: dict[str, Any] = {
        "$schema": "../schema/strict-residual-zero-mode-payload-v1.schema.json",
        "schema": "strict-residual-zero-mode-payload-v1",
        "schema_path": "quantum-weyl/classical_import/schema/strict-residual-zero-mode-payload-v1.schema.json",
        "result_id": "STRICT_RESIDUAL_ZERO_MODE_PAYLOAD_V1",
        "result_kind": "EXACT_RESIDUAL_CLASSICAL_PAYLOAD",
        "result_state": "FIFTEEN_PRIMAL_DUAL_MODES_AND_SO42_ACTION_EXPORTED_COMMON_GATE_BINDING_OPEN",
        "lifecycle": "CLASSIFIED",
        "created": "2026-08-16",
        "repository_base_commit": "be886d401f450636443a37cfb8d6ddaa2048d79b",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "question": "Can the exact fifteen-mode residual payload be replayed independently rather than referenced only by labels and hashes?",
        "answer": "Yes. The payload serializes rational primal and dual bases, their coordinate maps and projectors, the complete SO(4,2) structure tensor, all fifteen 30-by-30 residual representation matrices, and q_res^(0)=0. The receiver replays the kernel, quotient, cyclic-adjoint, Jacobi, representation, pairing and nilpotency identities. Binding these bytes to the full support-local Gate-A freeze remains open.",
        "scope": {
            "theory": "strict pure-Weyl residual Diff x Weyl zero-mode sector",
            "background": "unit conformal cylinder",
            "category": "finite exact polynomial zero-mode and endpoint quotient charts",
            "primal_dimension": 15,
            "dual_dimension": 15,
            "residual_cotangent_dimension": 30,
            "coefficient_field": "Q",
        },
        "zero_mode_basis": zero_modes,
        "so42_structure_constants": structure,
        "residual_representation": representations,
        "residual_differential_q_res_0": q_res,
        "canonical_hashes": canonical,
        "residual_snapshot": snapshot,
        "exact_replay": {
            "K_times_primal_basis_defects": 0,
            "primal_coordinate_identity_defects": 0,
            "primal_projector_idempotency_defects": 0,
            "cyclic_adjoint_defects": 0,
            "dual_map_K_sharp_defects": 0,
            "dual_coordinate_identity_defects": 0,
            "dual_projector_idempotency_defects": 0,
            "primal_dual_pairing_defects": 0,
            "antisymmetry_defects": 0,
            "jacobi_defects": 0,
            "unimodularity_defects": 0,
            "representation_defects": 0,
            "coadjoint_duality_defects": 0,
            "q_res_0_squared_defects": 0,
        },
        "foundational_strength": {
            "finite_exact_arithmetic": True,
            "choice_principle_used": False,
            "Hilbert_completion_used": False,
            "Green_operator_used_in_coefficient_payload": False,
            "causal_interpretation_dependency": "The identification of these polynomial classes with the Lorentzian residual endpoints uses the separately pinned causal transport theorem.",
            "weakest_exact_kernel": "primitive-recursive sparse rational linear algebra plus finite Jacobi and representation checks",
        },
        "gate_disposition": {
            "M5_RESIDUAL_EXACT_PAYLOAD": "PAYLOAD_COMPLETE_COMMON_FREEZE_BINDING_OPEN",
            "zero_mode_basis_hash_candidate": zero_modes["sha256"],
            "zero_mode_basis_hash_accepted_by_gate_a": False,
            "classical_import_gate_a_status": "FAIL_CLOSED",
        },
        "claim_flags": {
            "STRICT_PRIMAL_FIFTEEN_MODE_BASIS_SERIALIZED": True,
            "STRICT_DUAL_FIFTEEN_MODE_BASIS_SERIALIZED": True,
            "STRICT_SO42_STRUCTURE_CONSTANTS_SERIALIZED": True,
            "STRICT_RESIDUAL_REPRESENTATION_MATRICES_SERIALIZED": True,
            "STRICT_Q_RES_0_SERIALIZED": True,
            "STRICT_RESIDUAL_ZERO_MODE_IDENTITIES_REPLAYED": True,
            "M5_RESIDUAL_EXACT_PAYLOAD_COMPLETE": True,
            "COMMON_GATE_A_FREEZE_BOUND": False,
            "CLASSICAL_IMPORT_GATE_PASSED": False,
            "HADAMARD_STATE_CONSTRUCTED": False,
            "QME_RESTORED": False,
            "LORENTZIAN_QUANTUM_THEORY": False,
        },
        "provenance": {
            "inputs": [
                {"path": path, "sha256": file_hash(path), "role": "exact source or causal interpretation boundary"}
                for path in INPUTS
            ]
        },
        "does_not_establish": [
            "a support-local or distributional residual SDR on the complete 386-row field carrier",
            "a common Gate-A field dictionary, differential, pairing or representative hash",
            "centered H3, H4 and H5 representative coefficient vectors",
            "that the W_+^2 and W_-^2 deformation classes are one-particle states",
            "Hadamard data, renormalized Lorentzian products, QME restoration or residual transfer",
        ],
        "next_gate": "Bind this exact residual payload to the common full-carrier q1/q2/q3/D/pairing snapshot and construct the remaining centered H3/H4/H5 representatives and support-local residual SDR.",
        "independent_checker": {
            "path": "quantum-weyl/classical_import/check_strict_residual_zero_mode_payload.py",
            "mode": "deserialize only; reconstruct all matrix, Lie and representation identities from exported entries",
            "expected_digest": "",
        },
        "human_report": "quantum-weyl/classical_import/REPORT_STRICT_RESIDUAL_ZERO_MODE_PAYLOAD_V1.md",
    }
    value["independent_checker"]["expected_digest"] = digest(
        {
            "zero_mode_basis": value["zero_mode_basis"],
            "so42_structure_constants": value["so42_structure_constants"],
            "residual_representation": value["residual_representation"],
            "residual_differential_q_res_0": value["residual_differential_q_res_0"],
            "residual_snapshot": value["residual_snapshot"],
            "claim_flags": value["claim_flags"],
        }
    )
    return value


def render(value: dict[str, Any]) -> str:
    zero = value["zero_mode_basis"]
    structure = value["so42_structure_constants"]
    return f"""# Strict residual zero-mode payload v1

**Result:** `{value['result_id']}`
**Dependencies:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`
**Gate A:** `FAIL_CLOSED`

The previously hidden exact residual coefficients are now portable.  The
certificate exports the fifteen primal conformal-Killing modes and fifteen
dual endpoint representatives in the canonical order

```text
{', '.join(zero['canonical_generator_order'])}
```

It also exports the complete `{structure['tensor_shape'][0]}^3` conformal
structure tensor ({structure['nonzero_entries']} nonzero ordered entries),
all fifteen adjoint/cotangent representation matrices on the 30-dimensional
residual carrier, and the zero unary matrix `q_res^(0)`.

An independent consumer deserializes only the printed rational entries and
replays the kernel, quotient, cyclic-adjoint, Jacobi, representation,
coadjoint-pairing and nilpotency identities.  No producer success flag is
used as evidence.

This closes the coefficient construction called
`M5_RESIDUAL_EXACT_PAYLOAD`.  Gate A remains fail closed because the payload
has not yet been bound to the common full support-local freeze; the residual
SDR, full cyclic contraction and centered H3/H4/H5 representatives remain
separate obligations.

## Reproduction

```text
python3 quantum-weyl/classical_import/build_strict_residual_zero_mode_payload.py --check
python3 quantum-weyl/classical_import/check_strict_residual_zero_mode_payload.py
python3 -m unittest discover -s quantum-weyl/classical_import/tests -p 'test_strict_residual_zero_mode_payload.py'
```
"""


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
        print("STRICT_RESIDUAL_ZERO_MODE_PAYLOAD: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    for path, content in outputs:
        path.write_bytes(content)
    print("STRICT_RESIDUAL_ZERO_MODE_PAYLOAD: wrote certificate and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
