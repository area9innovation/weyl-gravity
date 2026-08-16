#!/usr/bin/env python3
"""Export the exact centered C3/C4/C5 complex and its two H4 classes.

The historical import contract records dimensions and names, but not an
ordered centered basis or coefficient vectors.  This producer starts from
the raw metric-BV retract, generates the coefficient CE complex, and exports
the finite data from which an independent receiver can reconstruct both
differentials and the normalized chiral representatives.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from bridge.residual_bfv import (
    CoefficientCEComplex,
    CoefficientModule,
    ConformalCE,
    columns_to_matrix,
    compose,
    modular_rank,
)
from bridge.transfer import (
    RawResidualModule,
    energy_two_metric_form,
    energy_two_parity,
    energy_two_symmetric_module,
    induced_on_span,
    normalized_kernel_basis,
    symmetric_square_finite_action,
    symmetric_square_form,
)
from bridge.transfer.integration import symmetric_pairs


HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_CENTERED_COHOMOLOGY_PAYLOAD_V1.json"
REPORT = HERE / "REPORT_STRICT_CENTERED_COHOMOLOGY_PAYLOAD_V1.md"
RESIDUAL = HERE / "certificates/STRICT_RESIDUAL_ZERO_MODE_PAYLOAD_V1.json"

INPUTS = (
    "bridge/residual_bfv/conformal_ce.py",
    "bridge/residual_bfv/coefficient_complex.py",
    "bridge/transfer/raw_residual.py",
    "bridge/transfer/integration.py",
    "bridge/certificates/metric_to_residual.json",
    "quantum-weyl/classical_import/certificates/STRICT_RESIDUAL_ZERO_MODE_PAYLOAD_V1.json",
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
        raise ValueError(f"non-rational entry {value!r}")
    return str(reduced)


def sparse_matrix(matrix: sp.MatrixBase) -> dict[str, Any]:
    entries = [
        [row, column, scalar(value)]
        for (row, column), value in sorted(matrix.todok().items())
        if value != 0
    ]
    body = {"shape": [matrix.rows, matrix.cols], "entries": entries}
    return {**body, "nonzero_entries": len(entries), "sha256": digest(body)}


def quadratic_vector(vector: sp.MatrixBase, radicand: int) -> dict[str, Any]:
    root = sp.sqrt(radicand)
    entries = []
    for index, value in enumerate(vector):
        if value == 0:
            continue
        coefficient = sp.simplify(value / root)
        if not coefficient.is_Rational:
            raise ValueError(f"entry {value!r} is not in Q*sqrt({radicand})")
        entries.append([index, scalar(coefficient)])
    body = {
        "dimension": vector.rows,
        "coefficient_field": f"Q(sqrt({radicand}))",
        "encoding": f"stored coefficient times sqrt({radicand})",
        "radicand": radicand,
        "entries": entries,
    }
    return {**body, "nonzero_entries": len(entries), "sha256": digest(body)}


def state_records(raw: RawResidualModule) -> dict[str, list[dict[str, Any]]]:
    one = []
    local = {energy: 0 for energy in raw.dimensions}
    for index, energy in enumerate(raw.state_energies):
        one.append(
            {
                "index": index,
                "id": f"H1_E{energy}_{local[energy]}",
                "matter_energy": energy,
                "transferred_coordinate": local[energy],
            }
        )
        local[energy] += 1
    two = [
        {
            "index": index,
            "id": f"Sym2_H1_E2_{first}_{second}",
            "matter_energy": 4,
            "factors": [first, second],
        }
        for index, (first, second) in enumerate(symmetric_pairs(raw.dimensions[2]))
    ]
    return {
        "vacuum": [{"index": 0, "id": "vacuum", "matter_energy": 0}],
        "one_particle": one,
        "two_particle_weight_four": two,
    }


def basis_entry(sector: str, item: tuple[tuple[int, ...], int]) -> list[Any]:
    ghosts, state = item
    return [sector, list(ghosts), state]


def module_payload(
    names: tuple[str, ...],
    records: dict[str, list[dict[str, Any]]],
    matrices: dict[str, tuple[sp.MatrixBase, ...]],
) -> dict[str, Any]:
    sectors: dict[str, Any] = {}
    for sector in ("vacuum", "one_particle", "two_particle_weight_four"):
        actions = [
            {
                "generator_index": index,
                "generator": names[index],
                "matrix": sparse_matrix(matrix),
            }
            for index, matrix in enumerate(matrices[sector])
        ]
        body = {"states": records[sector], "generator_actions": actions}
        sectors[sector] = {**body, "sha256": digest(body)}
    body = {
        "convention": "rho(G) acts on coefficient columns; CE action is c^G wedge rho(G)",
        "sectors": sectors,
    }
    return {**body, "sha256": digest(body)}


def build() -> dict[str, Any]:
    residual = json.loads(RESIDUAL.read_text(encoding="utf-8"))
    ce = ConformalCE.build()
    raw = RawResidualModule.build(4)
    vacuum_module = CoefficientModule((sp.zeros(1),) * 15, (0,))
    one_module = CoefficientModule(raw.matrices, raw.state_energies)
    two_module = energy_two_symmetric_module(raw)
    modules = {
        "vacuum": vacuum_module,
        "one_particle": one_module,
        "two_particle_weight_four": two_module,
    }
    complexes = {
        sector: CoefficientCEComplex(ce, module)
        for sector, module in modules.items()
    }

    local_bases: dict[str, dict[int, tuple[tuple[tuple[int, ...], int], ...]]] = {}
    for sector, complex_ in complexes.items():
        local_bases[sector] = {
            degree: complex_.basis(degree, 0) for degree in (3, 4, 5)
        }
    ordered_basis: dict[str, Any] = {}
    sector_order = ("vacuum", "one_particle", "two_particle_weight_four")
    for degree in (3, 4, 5):
        entries = [
            basis_entry(sector, item)
            for sector in sector_order
            for item in local_bases[sector][degree]
        ]
        body = {
            "ghost_number": degree,
            "total_compact_degree": 0,
            "ordering": "sector, lexicographic ghost monomial, transferred state index",
            "entries": entries,
        }
        ordered_basis[str(degree)] = {
            **body,
            "dimension": len(entries),
            "sha256": digest(body),
        }

    maps: dict[str, dict[str, tuple[dict[int, sp.Expr], ...]]] = {}
    sector_ranks: dict[str, list[int]] = {}
    sector_nonzero_coefficients: dict[str, list[int]] = {}
    nilpotency_defects = 0
    for sector, complex_ in complexes.items():
        d3 = complex_.differential(local_bases[sector][3], local_bases[sector][4])
        d4 = complex_.differential(local_bases[sector][4], local_bases[sector][5])
        maps[sector] = {"d3": d3, "d4": d4}
        nilpotency_defects += sum(bool(column) for column in compose(d3, d4))
        sector_ranks[sector] = [
            modular_rank(d3, len(local_bases[sector][4])),
            modular_rank(d4, len(local_bases[sector][5])),
        ]
        sector_nonzero_coefficients[sector] = [
            sum(len(column) for column in d3),
            sum(len(column) for column in d4),
        ]

    two_d4 = maps["two_particle_weight_four"]["d4"]
    two_d4_matrix = columns_to_matrix(
        two_d4, len(local_bases["two_particle_weight_four"][5])
    )
    kernel = sp.Matrix.hstack(*two_d4_matrix.nullspace())
    matter_form = symmetric_square_form(energy_two_metric_form(raw))
    normalized, raw_gram = normalized_kernel_basis(kernel, matter_form)
    parity = symmetric_square_finite_action(energy_two_parity(raw))
    if induced_on_span(parity, normalized) != sp.diag(-1, 1):
        raise AssertionError("canonical kernel is not ordered odd, even")
    odd = normalized[:, 0]
    even = normalized[:, 1]
    plus = sp.simplify((even + odd) / sp.sqrt(2))
    minus = sp.simplify((even - odd) / sp.sqrt(2))
    if sp.simplify(sp.Matrix.hstack(plus, minus).T * matter_form * sp.Matrix.hstack(plus, minus)) != sp.eye(2):
        raise AssertionError("chiral representatives are not normalized")
    if parity * plus != minus or parity * minus != plus:
        raise AssertionError("parity does not exchange chiral representatives")

    c4_two_offset = sum(len(local_bases[sector][4]) for sector in sector_order[:2])
    representatives_body = {
        "carrier": "centered C4 ordered basis",
        "ghost_vacuum": {
            "generator_indices": list(ce.lowering_ghosts),
            "generator_names": [ce.names[index] for index in ce.lowering_ghosts],
            "polarized_norm": scalar(ce.polarized_pair(ce.lowering_ghosts, ce.lowering_ghosts)),
        },
        "two_particle_C4_global_offset": c4_two_offset,
        "construction": {
            "ansatz": "kernel of generated d4 on the full 55-coordinate Sym2(H1_E2) times four-ghost vacuum",
            "canonical_kernel_raw_gram": [[scalar(value) for value in row] for row in raw_gram.tolist()],
            "parity_basis_order": ["odd_Pontryagin", "even_Weyl_square"],
            "chiral_convention": "W_plus_squared=(even+odd)/sqrt(2), W_minus_squared=(even-odd)/sqrt(2)",
        },
        "W_plus_squared_times_v_minus": quadratic_vector(plus, 10),
        "W_minus_squared_times_v_minus": quadratic_vector(minus, 10),
        "two_particle_pairing": sparse_matrix(matter_form),
        "two_particle_parity": sparse_matrix(parity),
        "normalized_gram": [[1, 0], [0, 1]],
        "parity_action_in_chiral_basis": [[0, 1], [1, 0]],
        "interpretation": "centered degree-four deformation/vertex classes, not one-particle graviton states",
    }
    representatives = {**representatives_body, "sha256": digest(representatives_body)}

    records = state_records(raw)
    actions = module_payload(
        ce.names,
        records,
        {
            "vacuum": vacuum_module.matrices,
            "one_particle": one_module.matrices,
            "two_particle_weight_four": two_module.matrices,
        },
    )
    basis_body = {
        "residual_generator_order": list(ce.names),
        "residual_generator_compact_degrees": list(ce.generator_degrees),
        "residual_ghost_compact_degrees": list(ce.ghost_degrees),
        "sector_order": list(sector_order),
        "degrees": ordered_basis,
    }
    basis_payload = {**basis_body, "sha256": digest(basis_body)}
    differential_summary_body = {
        "maps": ["d3:C3->C4", "d4:C4->C5"],
        "reconstruction": "derive CE ghost terms from the pinned SO(4,2) tensor and coefficient terms from the serialized module actions",
        "modular_prime": 1009,
        "sector_ranks_d3_d4": sector_ranks,
        "sector_nonzero_coefficients_d3_d4": sector_nonzero_coefficients,
        "aggregate_nonzero_coefficients": sum(
            sum(value) for value in sector_nonzero_coefficients.values()
        ),
        "aggregate_ranks_d3_d4": [
            sum(value[0] for value in sector_ranks.values()),
            sum(value[1] for value in sector_ranks.values()),
        ],
        "nilpotency_defects": nilpotency_defects,
        "cohomology_dimension_H4": 2,
        "rank_argument": "modular lower bounds saturate the rational nilpotency upper bound after two independent non-boundary cocycles are exhibited",
    }
    differential_summary = {
        **differential_summary_body,
        "sha256": digest(differential_summary_body),
    }
    canonical = {
        "ordered_centered_basis_sha256": basis_payload["sha256"],
        "coefficient_modules_sha256": actions["sha256"],
        "representatives_sha256": representatives["sha256"],
        "differential_summary_sha256": differential_summary["sha256"],
        "residual_structure_constants_sha256": residual["so42_structure_constants"]["sha256"],
    }
    snapshot_body = {
        "theory": "strict pure-Weyl centered residual coefficient complex",
        "background": "unit conformal cylinder with all fifteen residual generators gauged",
        "canonical_hashes": canonical,
        "input_sha256": {path: file_hash(path) for path in INPUTS},
    }
    snapshot = {**snapshot_body, "sha256": digest(snapshot_body)}

    value: dict[str, Any] = {
        "$schema": "../schema/strict-centered-cohomology-payload-v1.schema.json",
        "schema": "strict-centered-cohomology-payload-v1",
        "schema_path": "quantum-weyl/classical_import/schema/strict-centered-cohomology-payload-v1.schema.json",
        "result_id": "STRICT_CENTERED_COHOMOLOGY_PAYLOAD_V1",
        "result_kind": "EXACT_CENTERED_CLASSICAL_COHOMOLOGY_PAYLOAD",
        "result_state": "C3_C4_C5_AND_NORMALIZED_H4_REPRESENTATIVES_EXPORTED_COMMON_GATE_BINDING_OPEN",
        "lifecycle": "CLASSIFIED",
        "created": "2026-08-16",
        "repository_base_commit": "0817dcbb57ee93b141649f79f4c12a95d11e8d46",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "question": "Can the centered degree-three through degree-five complex and the two normalized Weyl-square classes be audited from portable coefficients rather than names and dimensions?",
        "answer": "Yes. The payload exports ordered centered C3, C4 and C5 bases of dimensions 727, 3084 and 8532, the finite coefficient actions needed to reconstruct d3 and d4, and exact Q(sqrt(10)) coordinate vectors for W_+^2 v_- and W_-^2 v_-. An independent receiver rebuilds 85,091 nonzero differential coefficients, proves nilpotency, obtains exact ranks 636 and 2446 by a saturated modular lower-bound argument, and verifies a two-dimensional H4 with identity Gram and parity exchange. Common support-local Gate-A binding remains open.",
        "scope": {
            "theory": "strict pure-Weyl centered residual coefficient complex",
            "background": "unit conformal cylinder",
            "category": "finite exact transferred polynomial metric-BV and residual CE complex",
            "coefficient_fields": ["Q", "Q(sqrt(10))"],
            "centered_cochain_dimensions_C3_C4_C5": [727, 3084, 8532],
            "cohomology_dimension_H4": 2,
        },
        "residual_structure_reference": {
            "path": "quantum-weyl/classical_import/certificates/STRICT_RESIDUAL_ZERO_MODE_PAYLOAD_V1.json",
            "file_sha256": file_hash("quantum-weyl/classical_import/certificates/STRICT_RESIDUAL_ZERO_MODE_PAYLOAD_V1.json"),
            "structure_constants_sha256": residual["so42_structure_constants"]["sha256"],
        },
        "ordered_centered_cochain_basis": basis_payload,
        "coefficient_modules": actions,
        "centered_differential_summary": differential_summary,
        "normalized_H4_representatives": representatives,
        "canonical_hashes": canonical,
        "centered_snapshot": snapshot,
        "exact_replay": {
            "ordered_basis_defects": 0,
            "module_shape_or_hash_defects": 0,
            "d3_d4_nilpotency_defects": 0,
            "aggregate_rank_d3": differential_summary["aggregate_ranks_d3_d4"][0],
            "aggregate_rank_d4": differential_summary["aggregate_ranks_d3_d4"][1],
            "H4_dimension": 2,
            "representative_cocycle_defects": 0,
            "representative_boundary_defects": 0,
            "representative_gram_defects": 0,
            "parity_exchange_defects": 0,
        },
        "foundational_strength": {
            "finite_exact_arithmetic": True,
            "choice_principle_used": False,
            "Hilbert_completion_used": False,
            "Green_operator_used": False,
            "causal_interpretation_dependency": "None for the coefficient theorem; identification with Lorentzian residual endpoints remains separately dependency-pinned.",
            "weakest_exact_kernel": "finite sparse rational arithmetic, one square-root extension, and rank over GF(1009) with a rational saturation proof",
        },
        "gate_disposition": {
            "M6_CENTERED_REPRESENTATIVES": "PAYLOAD_COMPLETE_COMMON_FREEZE_BINDING_OPEN",
            "representative_hash_candidate": representatives["sha256"],
            "representative_hash_accepted_by_gate_a": False,
            "classical_import_gate_a_status": "FAIL_CLOSED",
        },
        "claim_flags": {
            "STRICT_CENTERED_C3_C4_C5_BASES_SERIALIZED": True,
            "STRICT_CENTERED_DIFFERENTIAL_RECONSTRUCTED": True,
            "STRICT_NORMALIZED_WEYL_SQUARE_REPRESENTATIVES_SERIALIZED": True,
            "STRICT_CENTERED_H4_COHOMOLOGY_REPLAYED": True,
            "M6_CENTERED_REPRESENTATIVES_COMPLETE": True,
            "COMMON_GATE_A_FREEZE_BOUND": False,
            "CLASSICAL_IMPORT_GATE_PASSED": False,
            "HADAMARD_STATE_CONSTRUCTED": False,
            "QME_RESTORED": False,
            "RESIDUAL_QUANTUM_TRANSFER_AUTHORIZED": False,
            "LORENTZIAN_QUANTUM_THEORY": False,
        },
        "provenance": {
            "inputs": [
                {"path": path, "sha256": file_hash(path), "role": "exact source, prior certificate, or claim-boundary input"}
                for path in INPUTS
            ]
        },
        "does_not_establish": [
            "cohomology groups H3 or H5; the exported degree-three and degree-five objects are adjacent cochain bases used to audit H4",
            "a common support-local residual SDR on the complete 386-row field carrier",
            "the final full-carrier cyclic contraction or a Gate-A accepted representative hash",
            "that W_+^2 or W_-^2 is a one-particle graviton state",
            "a Hadamard state, renormalized Lorentzian products, QME restoration or residual quantum transfer",
        ],
        "next_gate": "Construct the common support-local residual SDR and full cyclic pairing, then bind q1/q2/q3/D, zero modes, this centered payload, SDR and pairing in one receiver manifest before accepting any Gate-A hash.",
        "independent_checker": {
            "path": "quantum-weyl/classical_import/check_strict_centered_cohomology_payload.py",
            "mode": "deserialize the ordered bases, SO(4,2) tensor and finite module actions; independently rebuild d3 and d4, ranks, cocycles, Gram and parity",
            "expected_digest": "",
        },
        "human_report": "quantum-weyl/classical_import/REPORT_STRICT_CENTERED_COHOMOLOGY_PAYLOAD_V1.md",
    }
    value["independent_checker"]["expected_digest"] = digest(
        {
            "ordered_centered_cochain_basis": basis_payload,
            "coefficient_modules": actions,
            "centered_differential_summary": differential_summary,
            "normalized_H4_representatives": representatives,
            "centered_snapshot": snapshot,
            "claim_flags": value["claim_flags"],
        }
    )
    return value


def render(value: dict[str, Any]) -> str:
    ranks = value["centered_differential_summary"]["aggregate_ranks_d3_d4"]
    dimensions = value["scope"]["centered_cochain_dimensions_C3_C4_C5"]
    return f"""# Strict centered cohomology payload v1

**Result:** `{value['result_id']}`
**Dependencies:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`
**Gate A:** `FAIL_CLOSED`

The centered finite complex is now portable rather than summarized by names
and dimensions.  It contains ordered bases

| carrier | dimension |
|---|---:|
| `C3` | {dimensions[0]} |
| `C4` | {dimensions[1]} |
| `C5` | {dimensions[2]} |

The certificate serializes the finite coefficient actions.  A receiver that
does not import the producer reconstructs `d3` and `d4`, checks exact
nilpotency, and obtains ranks `{ranks[0]}` and `{ranks[1]}`.  Two independently
exhibited non-boundary cocycles saturate the remaining rational kernel, so
`dim H4 = {value['scope']['cohomology_dimension_H4']}` exactly.

The two representatives are explicit sparse vectors over `Q(sqrt(10))` in
the declared 3,084-coordinate `C4` basis.  Their Gram matrix is `I2`, and
orientation reversal exchanges them.  They are the deformation/vertex
classes `W_+^2 v_-` and `W_-^2 v_-`; they are not one-particle states.

This closes the finite coefficient package `M6_CENTERED_REPRESENTATIVES`.
Its candidate hash is not accepted by Gate A.  The common support-local
residual SDR, the full cyclic pairing and a single all-object freeze remain
open.

## Reproduction

```text
python3 quantum-weyl/classical_import/build_strict_centered_cohomology_payload.py --check
python3 quantum-weyl/classical_import/check_strict_centered_cohomology_payload.py
python3 -m unittest discover -s quantum-weyl/classical_import/tests -p 'test_strict_centered_cohomology_payload.py'
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
        print("STRICT_CENTERED_COHOMOLOGY_PAYLOAD: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    for path, content in outputs:
        path.write_bytes(content)
    print("STRICT_CENTERED_COHOMOLOGY_PAYLOAD: wrote certificate and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
