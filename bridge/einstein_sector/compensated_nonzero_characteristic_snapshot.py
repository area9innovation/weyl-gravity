"""Exact nonzero-characteristic cohomology snapshot of the compensated BV symbol.

The snapshot consumes only the canonical JSON operator export through its
independent verifier.  At representative rational characteristic covectors it
constructs explicit cohomology inclusions, projections, and contracting
homotopies.  The odd BV pairing is correctly evaluated between the p and -p
fibers.  The p=0 fiber is recorded only as an open global-mode ledger.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp

from bridge.einstein_sector.verify_compensated_minimal_bv_operator_export import (
    load_verified_export,
)


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "bridge/certificates/compensated_nonzero_characteristic_snapshot.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/compensated_nonzero_characteristic_snapshot.schema.json"
OPERATOR_EXPORT = ROOT / "bridge/certificates/compensated_minimal_bv_operator_export.json"
INDEPENDENT_VERIFIER = ROOT / "bridge/einstein_sector/verify_compensated_minimal_bv_operator_export.py"
MINIMAL_CERTIFICATE = ROOT / "bridge/certificates/compensated_quadratic_minimal_bv.json"


class CharacteristicSnapshotError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise CharacteristicSnapshotError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _zero(matrix: sp.MatrixBase) -> bool:
    return sp.SparseMatrix(matrix.applyfunc(sp.simplify)).nnz() == 0


def _record(matrix: sp.MatrixBase) -> dict[str, Any]:
    entries = [
        [row, column, str(sp.factor(value))]
        for (row, column), value in sorted(sp.SparseMatrix(matrix).todok().items())
    ]
    body = {"shape": list(matrix.shape), "entries": entries}
    digest = hashlib.sha256(json.dumps(body, separators=(",", ":"), sort_keys=True).encode("utf-8")).hexdigest()
    return {**body, "sha256": digest}


DEGREE_BLOCKS = ((-1, 0, 5), (0, 5, 16), (1, 16, 27), (2, 27, 32))


def _cohomology_dimensions(q: sp.MatrixBase) -> dict[str, int]:
    ranks = [q[5:16, 0:5].rank(), q[16:27, 5:16].rank(), q[27:32, 16:27].rank()]
    dimensions = [5 - ranks[0], 11 - ranks[1] - ranks[0], 11 - ranks[2] - ranks[1], 5 - ranks[2]]
    return {str(degree): dimension for (degree, _, _), dimension in zip(DEGREE_BLOCKS, dimensions)}


def _contraction(q: sp.MatrixBase) -> tuple[sp.Matrix, sp.Matrix, sp.Matrix]:
    n = q.rows
    rank = q.rank()
    z_columns = q.nullspace()
    cycles = sp.Matrix.hstack(*z_columns) if z_columns else sp.zeros(n, 0)

    complement_columns: list[sp.Matrix] = []
    span = cycles
    span_rank = span.rank()
    identity = sp.eye(n)
    for column in range(n):
        candidate = identity[:, column]
        enlarged = span.row_join(candidate)
        enlarged_rank = enlarged.rank()
        if enlarged_rank > span_rank:
            complement_columns.append(candidate)
            span = enlarged
            span_rank = enlarged_rank
        if len(complement_columns) == rank:
            break
    complement = sp.Matrix.hstack(*complement_columns) if complement_columns else sp.zeros(n, 0)
    boundaries = q * complement
    _require(boundaries.rank() == rank, "chosen cycle complement does not map isomorphically to boundaries")

    representatives: list[sp.Matrix] = []
    span = boundaries
    span_rank = span.rank()
    for candidate in z_columns:
        enlarged = span.row_join(candidate)
        enlarged_rank = enlarged.rank()
        if enlarged_rank > span_rank:
            representatives.append(candidate)
            span = enlarged
            span_rank = enlarged_rank
    inclusion = sp.Matrix.hstack(*representatives) if representatives else sp.zeros(n, 0)
    _require(inclusion.cols == n - 2 * rank, "cohomology dimension changed")

    basis = boundaries.row_join(inclusion).row_join(complement)
    _require(basis.shape == (n, n) and basis.rank() == n, "contraction basis is singular")
    inverse = basis.inv()
    projection = inverse[rank : rank + inclusion.cols, :]
    coordinate_homotopy = sp.zeros(n)
    coordinate_homotopy[rank + inclusion.cols : n, 0:rank] = sp.eye(rank)
    homotopy = basis * coordinate_homotopy * inverse

    _require(_zero(projection * inclusion - sp.eye(inclusion.cols)), "pi i != 1")
    _require(_zero(inclusion * projection - (sp.eye(n) - q * homotopy - homotopy * q)), "i pi contraction identity failed")
    _require(_zero(q * inclusion), "representative is not closed")
    _require(_zero(projection * q), "projection is not a chain map")
    _require(_zero(homotopy * homotopy), "s^2 != 0")
    _require(_zero(homotopy * inclusion), "s i != 0")
    _require(_zero(projection * homotopy), "pi s != 0")
    return inclusion, projection, homotopy


def _degree_dimensions(inclusion: sp.MatrixBase) -> dict[str, int]:
    dimensions = {str(degree): 0 for degree, _, _ in DEGREE_BLOCKS}
    for column in range(inclusion.cols):
        supports = [degree for degree, start, stop in DEGREE_BLOCKS if any(inclusion[row, column] != 0 for row in range(start, stop))]
        _require(len(supports) == 1, "cohomology representative mixes chain degrees")
        dimensions[str(supports[0])] += 1
    return dimensions


def _substitution(symbols: dict[str, sp.Symbol], momentum: tuple[int, int, int, int]) -> dict[sp.Symbol, int]:
    return {
        symbols["p0"]: momentum[0], symbols["p1"]: momentum[1],
        symbols["p2"]: momentum[2], symbols["p3"]: momentum[3],
        symbols["c1"]: -1, symbols["alpha"]: -1, symbols["v"]: 1,
    }


def _branch(name: str, momentum: tuple[int, int, int, int], q_symbol: sp.MatrixBase, pairing: sp.MatrixBase, symbols: dict[str, sp.Symbol]) -> dict[str, Any]:
    plus_sub = _substitution(symbols, momentum)
    minus_sub = _substitution(symbols, tuple(-entry for entry in momentum))
    q_plus = sp.Matrix(q_symbol.subs(plus_sub))
    q_minus = sp.Matrix(q_symbol.subs(minus_sub))
    i_plus, pi_plus, s_plus = _contraction(q_plus)
    i_minus, pi_minus, s_minus = _contraction(q_minus)
    _require(_cohomology_dimensions(q_plus) == _degree_dimensions(i_plus), "block and representative cohomology dimensions differ")
    _require(_cohomology_dimensions(q_minus) == _degree_dimensions(i_minus), "minus-fiber dimensions differ")
    induced_pairing = sp.simplify(i_minus.T * pairing * i_plus)
    _require(induced_pairing.rank() == i_plus.cols, "p/-p odd BV cohomology pairing is degenerate")
    return {
        "name": name,
        "parameters": {"p": list(momentum), "p_squared": momentum[0] ** 2 - sum(value ** 2 for value in momentum[1:]), "c1": -1, "alpha": -1, "v": 1},
        "ranks": {
            "gauge": q_plus[5:16, 0:5].rank(),
            "hessian": q_plus[16:27, 5:16].rank(),
            "noether": q_plus[27:32, 16:27].rank(),
            "q": q_plus.rank(),
        },
        "cohomology_dimensions": _degree_dimensions(i_plus),
        "plus_contraction": {"inclusion": _record(i_plus), "pi_cl": _record(pi_plus), "homotopy": _record(s_plus)},
        "minus_contraction": {"inclusion": _record(i_minus), "pi_cl": _record(pi_minus), "homotopy": _record(s_minus)},
        "momentum_reversing_odd_bv_pairing": _record(induced_pairing),
        "pairing_rank": induced_pairing.rank(),
        "status": "PASS",
    }


def build_certificate() -> dict[str, Any]:
    _, matrices, symbols = load_verified_export(OPERATOR_EXPORT)
    q_symbol = matrices["q"]
    pairing = matrices["pairing"]
    generic = _branch("generic_noncharacteristic", (2, 1, 0, 0), q_symbol, pairing, symbols)
    massless = _branch("nonzero_null_characteristic", (1, 0, 0, 1), q_symbol, pairing, symbols)
    massive = _branch("second_characteristic_root", (0, 1, 0, 0), q_symbol, pairing, symbols)

    zero_q = sp.Matrix(q_symbol.subs(_substitution(symbols, (0, 0, 0, 0))))
    zero_ledger = {
        "parameters": {"p": [0, 0, 0, 0], "c1": -1, "alpha": -1, "v": 1},
        "ranks": {
            "gauge": zero_q[5:16, 0:5].rank(), "hessian": zero_q[16:27, 5:16].rank(),
            "noether": zero_q[27:32, 16:27].rank(), "q": zero_q.rank(),
        },
        "fiber_cohomology_dimensions": _cohomology_dimensions(zero_q),
        "status": "RECORDED_NOT_PROMOTED",
        "reason": "the zero symbol mixes reducibility/Killing data with global and boundary-sensitive modes; a finite fiber rank is not their physical classification",
    }
    _require(generic["cohomology_dimensions"] == {"-1": 0, "0": 0, "1": 0, "2": 0}, "generic fiber is not acyclic")
    _require(massless["cohomology_dimensions"] == {"-1": 0, "0": 2, "1": 2, "2": 0}, "null fiber changed")
    _require(massive["cohomology_dimensions"] == {"-1": 0, "0": 5, "1": 5, "2": 0}, "second root fiber changed")
    _require(zero_ledger["fiber_cohomology_dimensions"] == {"-1": 4, "0": 10, "1": 10, "2": 4}, "zero ledger changed")

    payload = {
        "schema": "compensated-nonzero-characteristic-snapshot-v1",
        "schema_path": "bridge/einstein_sector/schema/compensated_nonzero_characteristic_snapshot.schema.json",
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "COMPENSATED_NONZERO_CHARACTERISTIC_CLASSICAL_SNAPSHOT",
        "result_state": "SCOPED_EXACT_SNAPSHOT_CERTIFIED_GLOBAL_CLASSICAL_FREEZE_OPEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "provenance": {
            "input_base_commit": "25364fb760ed869f193983eb179ad3b120b52557",
            "generator_path": "bridge/einstein_sector/compensated_nonzero_characteristic_snapshot.py",
            "generator_sha256": _sha256(Path(__file__)),
        },
        "inputs": {
            "operator_export": {"path": str(OPERATOR_EXPORT.relative_to(ROOT)), "sha256": _sha256(OPERATOR_EXPORT)},
            "independent_operator_verifier": {"path": str(INDEPENDENT_VERIFIER.relative_to(ROOT)), "sha256": _sha256(INDEPENDENT_VERIFIER)},
            "minimal_bv_certificate": {"path": str(MINIMAL_CERTIFICATE.relative_to(ROOT)), "sha256": _sha256(MINIMAL_CERTIFICATE)},
        },
        "domain": {
            "kind": "exact finite symbol fibers at declared rational covectors",
            "coefficient_specialization": "c1=alpha=-1, v=1",
            "formal_adjoint_pairing_rule": "cohomology at p pairs with cohomology at -p",
            "interpretation_limit": "representative algebraic characteristic fibers, not a covariant mass-shell bundle or Hilbert space",
        },
        "branches": {"generic": generic, "massless": massless, "second_root": massive},
        "zero_momentum_ledger": zero_ledger,
        "theorem": {
            "generic_noncharacteristic_cohomology": [0, 0, 0, 0],
            "nonzero_null_cohomology": [0, 2, 2, 0],
            "second_root_cohomology": [0, 5, 5, 0],
            "explicit_data": "each promoted branch contains exact inclusions, pi_cl projections, homotopies, and the nondegenerate p/-p odd BV pairing",
            "physical_reading": "the two degree-zero null classes are the local symbol precursors of helicity +/-2; identifying a positive-frequency graviton space requires a separate Lorentzian causal/asymptotic certificate",
        },
        "verdict": "NONZERO_NULL_2_PLUS_SECOND_ROOT_5_SYMBOL_COHOMOLOGY_WITH_EXACT_CONTRACTIONS",
        "claim_flags": {
            "operator_export_independently_verified": True,
            "generic_noncharacteristic_acyclicity_exact": True,
            "nonzero_null_two_degree_zero_classes_exact": True,
            "second_root_five_degree_zero_classes_exact": True,
            "branch_representatives_projections_homotopies_exact": True,
            "momentum_reversing_odd_bv_pairings_nondegenerate": True,
            "zero_momentum_fiber_recorded": True,
            "zero_momentum_global_modes_classified": False,
            "covariant_characteristic_bundle_constructed": False,
            "physical_cauchy_symplectic_pairing_computed_here": False,
            "ordinary_graviton_hilbert_space_constructed": False,
            "classical_import_freeze_complete": False,
            "lorentzian_causal_claim": False,
            "quantum_claim": False,
        },
        "missing_object_ledger": [
            "covariantize the representative-frame contractions over each nonzero characteristic component",
            "classify p=0 reducibility, Killing, compact-cylinder, and boundary modes in the chosen function space",
            "construct the physical Cauchy/radiative symplectic form separately from the odd BV pairing",
            "construct the sourced-defect chain map and matter-inclusive complex",
            "construct nonminimal gauge fixing and causal Green data before any LORENTZIAN-CAUSAL promotion",
        ],
        "scope_guards": [
            "REDUCED-MODE records exact symbol fibers only and supplies no LORENTZIAN-CAUSAL claim",
            "the second root is an algebraic p_squared=-1 fixture in signature (+---), not a positive-energy particle assertion",
            "the odd BV pairing couples p to -p and is not a norm or physical radiative symplectic form",
            "the p=0 dimensions are a fail-closed ledger and do not classify global physical states",
        ],
        "verification_command": "python3 -m bridge.einstein_sector.compensated_nonzero_characteristic_snapshot --verify bridge/certificates/compensated_nonzero_characteristic_snapshot.json",
    }
    return payload


def verify_certificate(path: Path = DEFAULT_OUTPUT) -> None:
    actual = json.loads(path.read_text(encoding="utf-8"))
    _require(actual == build_certificate(), f"characteristic snapshot is stale or altered: {path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    if args.write:
        DEFAULT_OUTPUT.write_text(json.dumps(build_certificate(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.verify:
        verify_certificate(args.verify)
    if not args.write and not args.verify:
        parser.error("one of --write or --verify is required")


if __name__ == "__main__":
    main()
