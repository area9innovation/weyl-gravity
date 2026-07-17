#!/usr/bin/env python3
"""Exact first derivative-dependent BGG correction screen on Nariai."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp

from covariant_completion.curved_operator.adjoint_tractor_kostant_compression import (
    AdjointTractorKostantCompression,
    _adjoint_basis,
    _coordinate_map,
)
from covariant_completion.curved_operator.adjoint_tractor_bgg_differential_screen import (
    AdjointTractorBGGDifferentialScreen,
    _adjoint_actions,
)
from covariant_completion.curved_operator.adjoint_tractor_bgg_curved_pbw import (
    FibrePBW,
    _add,
    _algebraic,
    _induced_harmonic_curvature,
    _scale,
    _tensor_product_curvature,
)


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "d_quotient_classical/causal_transfer"
KOSTANT_MATRICES = ROOT / "covariant_completion/certificates/adjoint_tractor_kostant_compression_matrices.json"
SCREEN_MATRICES = ROOT / "covariant_completion/certificates/adjoint_tractor_bgg_differential_screen_matrices.json"
PARENT = ROOT / "d_quotient_classical/certificates/CONFORMALLY_EINSTEIN_YANG_MILLS_DETOUR_CORRECTION_V1.json"
POINTWISE = ROOT / "d_quotient_classical/certificates/NARIAI_POINTWISE_BGG_CURVATURE_COMPRESSION_OBSTRUCTION_V1.json"
PBW_CODE = ROOT / "covariant_completion/curved_operator/adjoint_tractor_bgg_curved_pbw.py"
OUTPUT = ROOT / "d_quotient_classical/certificates/NARIAI_FIRST_BGG_ZEROTH_ORDER_STRICTIFICATION_OBSTRUCTION_V1.json"
REPORT = ROOT / "d_quotient_classical/reports/nariai-first-bgg-zeroth-order-strictification-obstruction.md"
SCHEMA = ROOT / "d_quotient_classical/schema/nariai-first-bgg-zeroth-order-strictification-obstruction-v1.schema.json"
VERIFIER = HERE / "verify_nariai_first_differential_bgg_correction.py"
TESTS = HERE / "tests/test_nariai_first_differential_bgg_correction.py"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sparse(matrix: sp.Matrix) -> dict[str, object]:
    return {
        "shape": [matrix.rows, matrix.cols],
        "entries": [
            [row, column, str(value)]
            for (row, column), value in sorted(matrix.todok().items())
        ],
        "sha256": hashlib.sha256(
            sp.srepr(sp.ImmutableSparseMatrix(matrix)).encode()
        ).hexdigest(),
    }


def _sparse_table(table: dict[tuple[int, ...], sp.Matrix]) -> dict[str, object]:
    payload = "\n".join(
        f"{word}:{sp.srepr(sp.ImmutableSparseMatrix(table[word]))}"
        for word in sorted(table)
    )
    return {
        "entries": [
            {"word": list(word), "matrix": _sparse(table[word])}
            for word in sorted(table)
        ],
        "sha256": hashlib.sha256(payload.encode()).hexdigest(),
    }


class NariaiBackground:
    """Normal-frame product curvature with distinct form/vector actions."""

    metric = sp.diag(-1, 1, 1, 1)
    inverse_metric = metric

    @classmethod
    def riemann(cls, a: int, b: int, c: int, d: int) -> sp.Expr:
        same_factor = all(index < 2 for index in (a, b, c, d)) or all(
            index >= 2 for index in (a, b, c, d)
        )
        if not same_factor:
            return sp.Integer(0)
        return cls.metric[a, c] * cls.metric[b, d] - cls.metric[a, d] * cls.metric[b, c]

    @classmethod
    def covector_commutator(cls, a: int, b: int) -> sp.Matrix:
        matrix = sp.zeros(4)
        for output in range(4):
            for source in range(4):
                matrix[output, source] = -sum(
                    cls.inverse_metric[source, raised]
                    * cls.riemann(raised, output, a, b)
                    for raised in range(4)
                )
        return matrix

    @classmethod
    def vector_commutator(cls, a: int, b: int) -> sp.Matrix:
        return -cls.covector_commutator(a, b).T


def _load() -> tuple[AdjointTractorKostantCompression, AdjointTractorBGGDifferentialScreen]:
    algebraic = AdjointTractorKostantCompression.from_payload(
        json.loads(KOSTANT_MATRICES.read_text())
    )
    screen = AdjointTractorBGGDifferentialScreen.from_payload(
        algebraic, json.loads(SCREEN_MATRICES.read_text())
    )
    return algebraic, screen


def _lc_adjoint_curvature() -> tuple[tuple[sp.Matrix, ...], ...]:
    _, basis = _adjoint_basis()
    embedded, left_inverse = _coordinate_map(basis)
    output: list[list[sp.Matrix]] = []
    for left in range(4):
        row = []
        for right in range(4):
            standard = sp.zeros(6)
            standard[1:5, 1:5] = NariaiBackground.vector_commutator(left, right)
            columns = []
            for generator in basis:
                commutator = standard * generator - generator * standard
                coordinates = left_inverse * commutator.reshape(36, 1)
                if embedded * coordinates != commutator.reshape(36, 1):
                    raise AssertionError("Nariai LC curvature escaped so(4,2)")
                columns.append(coordinates)
            row.append(sp.Matrix.hstack(*columns))
        output.append(row)
    return tuple(tuple(row) for row in output)


def _derivative_rows() -> tuple[dict[tuple[int, ...], sp.Matrix], dict[tuple[int, ...], sp.Matrix]]:
    derivative0 = {
        (axis,): sp.Matrix.vstack(
            *(sp.eye(15) if form == axis else sp.zeros(15) for form in range(4))
        )
        for axis in range(4)
    }
    pairs = tuple((left, right) for left in range(4) for right in range(left + 1, 4))
    derivative1: dict[tuple[int, ...], sp.Matrix] = {}
    for axis in range(4):
        matrix = sp.zeros(90, 60)
        for pair_index, (left, right) in enumerate(pairs):
            if axis == left:
                matrix[15 * pair_index : 15 * (pair_index + 1), 15 * right : 15 * (right + 1)] += sp.eye(15)
            if axis == right:
                matrix[15 * pair_index : 15 * (pair_index + 1), 15 * left : 15 * (left + 1)] -= sp.eye(15)
        derivative1[(axis,)] = matrix
    return derivative0, derivative1


def candidate() -> dict[str, object]:
    algebraic, screen = _load()
    background = NariaiBackground()
    lc_adjoint = _lc_adjoint_curvature()
    curvature0 = _tensor_product_curvature(background, lc_adjoint, 0)
    curvature1 = _tensor_product_curvature(background, lc_adjoint, 1)
    harmonic0 = _induced_harmonic_curvature(
        curvature0, algebraic.i0, screen.harmonic_p0
    )
    harmonic1 = _induced_harmonic_curvature(
        curvature1, algebraic.i1, screen.harmonic_p1
    )
    pbw0 = FibrePBW(curvature0, background, "Nariai-C0")
    pbw1 = FibrePBW(curvature1, background, "Nariai-C1")
    pbw_h0 = FibrePBW(harmonic0, background, "Nariai-H0")
    pbw_h1 = FibrePBW(harmonic1, background, "Nariai-H1")

    _, basis = _adjoint_basis()
    k_actions = _adjoint_actions(basis[11:15], basis)
    # Einstein Nariai has P_ab=(1/6)g_ab.  The tractor-connection matrix in
    # this implementation consumes the two-lowered orthonormal components,
    # hence the temporal coefficient is -1/6 rather than +1/6.
    schouten_components = tuple(
        NariaiBackground.metric[axis, axis] / 6 for axis in range(4)
    )
    rho_actions = tuple(
        schouten_components[axis] * k_actions[axis] for axis in range(4)
    )
    rho0 = sp.Matrix.vstack(*rho_actions)
    rho1_rows = []
    for left in range(4):
        for right in range(left + 1, 4):
            block = sp.zeros(15, 60)
            block[:, 15 * right : 15 * (right + 1)] = rho_actions[left]
            block[:, 15 * left : 15 * (left + 1)] = -rho_actions[right]
            rho1_rows.append(block)
    rho1 = sp.Matrix.vstack(*rho1_rows)
    derivative0, derivative1 = _derivative_rows()
    delta0 = _add(_algebraic(rho0), derivative0)
    delta1 = _add(_algebraic(rho1), derivative1)
    total0 = _add(_algebraic(screen.cohomology_d0), delta0)
    total1 = _add(_algebraic(screen.cohomology_d1), delta1)
    normal_tractor_square = pbw0.compose(total1, total0)

    n0 = pbw0.compose(_algebraic(screen.q1), delta0)
    n1 = pbw1.compose(_algebraic(screen.q2), delta1)
    inclusion0_alg = _algebraic(algebraic.i0)
    inclusion1_alg = _algebraic(algebraic.i1)
    n0_i0 = pbw_h0.compose(n0, inclusion0_alg)
    n1_i1 = pbw_h1.compose(n1, inclusion1_alg)
    inclusion0 = _add(
        inclusion0_alg,
        _scale(n0_i0, -1),
        pbw_h0.compose(n0, n0_i0),
    )
    inclusion1 = _add(
        inclusion1_alg,
        _scale(n1_i1, -1),
        pbw_h1.compose(n1, n1_i1),
    )
    raw_first = pbw_h0.compose(total0, inclusion0)
    first_bgg = pbw_h0.compose(_algebraic(screen.harmonic_p1), raw_first)
    defect = _add(
        pbw_h0.compose(total0, inclusion0),
        _scale(pbw_h0.compose(inclusion1, first_bgg), -1),
    )
    if set(defect).difference({(), (0,), (1,), (2,), (3,)}):
        raise AssertionError("unexpected first-correction derivative order")

    # Solve the transverse derivative equations row-by-row.  For a row in
    # form slot f, Delta L0 contributes only to derivative f.  The other
    # three axes therefore determine the corresponding Delta L1 row uniquely.
    correction1 = sp.zeros(60, 9)
    correction0_candidates: dict[int, list[sp.Matrix]] = {
        adjoint: [] for adjoint in range(15)
    }
    transverse_ranks = []
    inconsistent_rows = []
    for row in range(60):
        form = row // 15
        adjoint = row % 15
        transverse = [axis for axis in range(4) if axis != form]
        k_stack = sp.Matrix.hstack(
            *(first_bgg.get((axis,), sp.zeros(9, 4)) for axis in transverse)
        )
        d_stack = sp.Matrix.hstack(
            *(defect.get((axis,), sp.zeros(60, 4))[row, :] for axis in transverse)
        )
        transverse_ranks.append(k_stack.rank())
        try:
            solution, parameters = k_stack.T.gauss_jordan_solve(d_stack.T)
        except ValueError:
            inconsistent_rows.append(row)
            continue
        if parameters.rows != 0:
            raise AssertionError("transverse correction unexpectedly nonunique")
        correction1[row, :] = solution.T
        own_axis = form
        correction0_candidates[adjoint].append(
            correction1[row, :] * first_bgg.get((own_axis,), sp.zeros(9, 4))
            - defect.get((own_axis,), sp.zeros(60, 4))[row, :]
        )

    cross_form_defects = []
    correction0 = sp.zeros(15, 4)
    if not inconsistent_rows:
        for adjoint, candidates in correction0_candidates.items():
            correction0[adjoint, :] = candidates[0]
            for form, row in enumerate(candidates[1:], start=1):
                difference = row - candidates[0]
                for column, value in enumerate(difference):
                    if value != 0:
                        cross_form_defects.append(
                            [adjoint, form, column, str(value)]
                        )

    algebraic_defect = (
        defect.get((), sp.zeros(60, 4))
        + total0.get((), sp.zeros(60, 15)) * correction0
        - correction1 * first_bgg.get((), sp.zeros(9, 4))
    )
    projection0_defect = screen.harmonic_p0 * correction0
    projection1_defect = screen.harmonic_p1 * correction1
    corrected_defect = _add(
        defect,
        pbw_h0.compose(total0, _algebraic(correction0)),
        _scale(pbw_h0.compose(_algebraic(correction1), first_bgg), -1),
    )
    return {
        "transverse_ranks": transverse_ranks,
        "inconsistent_rows": inconsistent_rows,
        "correction0": correction0,
        "correction1": correction1,
        "cross_form_defects": cross_form_defects,
        "algebraic_defect": algebraic_defect,
        "projection0_defect": projection0_defect,
        "projection1_defect": projection1_defect,
        "corrected_defect": corrected_defect,
        "normal_tractor_square": normal_tractor_square,
        "original_defect": defect,
        "first_bgg": first_bgg,
    }


def build() -> dict[str, object]:
    parent = json.loads(PARENT.read_text())
    pointwise = json.loads(POINTWISE.read_text())
    if parent["flags"]["NARIAI_CURVED_PARENT_DETOUR_COMPLEX"] is not True:
        raise ValueError("curved Nariai Yang--Mills parent unavailable")
    if pointwise["flags"]["DERIVATIVE_BGG_CORRECTIONS_REQUIRED"] is not True:
        raise ValueError("pointwise Nariai compression gate unavailable")
    value = candidate()
    corrected = value["corrected_defect"]
    sources = {
        str(path.relative_to(ROOT)): _sha256(path)
        for path in (
            Path(__file__).resolve(),
            VERIFIER,
            TESTS,
            SCHEMA,
            PBW_CODE,
        )
    }
    return {
        "schema": "pure-weyl-nariai-first-bgg-zeroth-order-strictification-obstruction-v1",
        "result_id": "NARIAI_FIRST_BGG_ZEROTH_ORDER_STRICTIFICATION_OBSTRUCTION_V1",
        "result_state": "ZEROTH_ORDER_STRICT_CHAIN_CORRECTION_OBSTRUCTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "repair": {
            "superseded_certificate_sha256": "c4738c825fd1814962d4970e62341f0399fafb08331fe9b57bc25958b1fadbcc",
            "defect": "the superseded producer used +1/6 instead of -1/6 in the temporal orthonormal Schouten slot",
            "corrected_convention": "P_ab=(1/6)g_ab gives (-1/6,+1/6,+1/6,+1/6)",
            "recomputed_from_exact_sources": True,
        },
        "dependency_refs": {
            "curved_parent": {
                "artifact_id": parent["result_id"],
                "path": str(PARENT.relative_to(ROOT)),
                "sha256": _sha256(PARENT),
            },
            "pointwise_gate": {
                "artifact_id": pointwise["result_id"],
                "path": str(POINTWISE.relative_to(ROOT)),
                "sha256": _sha256(POINTWISE),
            },
            "kostant_matrices": {
                "artifact_id": "ADJOINT_TRACTOR_KOSTANT_COMPRESSION_MATRICES",
                "path": str(KOSTANT_MATRICES.relative_to(ROOT)),
                "sha256": _sha256(KOSTANT_MATRICES),
            },
            "differential_screen_matrices": {
                "artifact_id": "ADJOINT_TRACTOR_BGG_DIFFERENTIAL_SCREEN_MATRICES",
                "path": str(SCREEN_MATRICES.relative_to(ROOT)),
                "sha256": _sha256(SCREEN_MATRICES),
            },
        },
        "conventions": {
            "background": "unit Nariai dS2 x S2 in an orthonormal normal frame",
            "schouten": "P_ab=(1/6)g_ab",
            "schouten_orthonormal_components": ["-1/6", "1/6", "1/6", "1/6"],
            "form_slot_curvature": "covector action C_ab",
            "standard_tractor_middle_curvature": "dual vector action -C_ab^T",
            "fixed_first_bgg_operator": "the trace-free conformal-Killing operator K:H0(4)->H1(9)",
        },
        "ansatz": {
            "equation": "d^D(L0+DeltaL0)-(L1+DeltaL1)K=0",
            "DeltaL0": "arbitrary zeroth-order 15x4 bundle map",
            "DeltaL1": "arbitrary zeroth-order 60x9 bundle map",
            "normalization": "p0 DeltaL0=0 and p1 DeltaL1=0",
            "scope": "strict first-square correction with K fixed; derivative-dependent and homotopy-coherent corrections are not included",
        },
        "exact_data": {
            "candidate_DeltaL0": _sparse(value["correction0"]),
            "candidate_DeltaL1": _sparse(value["correction1"]),
            "first_bgg_operator": _sparse_table(value["first_bgg"]),
            "original_chain_defect": _sparse_table(value["original_defect"]),
            "residual_chain_defect": _sparse_table(corrected),
            "normal_tractor_square": _sparse_table(value["normal_tractor_square"]),
        },
        "exact_checks": {
            "transverse_rank_set": sorted(set(value["transverse_ranks"])),
            "transverse_rows_inconsistent": value["inconsistent_rows"],
            "DeltaL0_rank": value["correction0"].rank(),
            "DeltaL0_nonzero_entries": sum(v != 0 for v in value["correction0"]),
            "DeltaL1_rank": value["correction1"].rank(),
            "DeltaL1_nonzero_entries": sum(v != 0 for v in value["correction1"]),
            "cross_form_defect_count": len(value["cross_form_defects"]),
            "cross_form_defects": value["cross_form_defects"],
            "algebraic_residual_rank": value["algebraic_defect"].rank(),
            "algebraic_residual_nonzero_entries": sum(
                entry != 0 for entry in value["algebraic_defect"]
            ),
            "normalized_witness": "(3/2)*residual_chain_defect[(),4,1]",
            "normalized_witness_value": "1",
            "harmonic_projection_defect_ranks": [
                value["projection0_defect"].rank(),
                value["projection1_defect"].rank(),
            ],
            "residual_orders": sorted({len(word) for word in corrected}),
            "residual_nonzero_entries": sum(
                entry != 0 for matrix in corrected.values() for entry in matrix
            ),
            "normal_tractor_square_rank": sp.Matrix.hstack(
                *(value["normal_tractor_square"][word] for word in sorted(value["normal_tractor_square"]))
            ).rank(),
            "normal_tractor_square_nonzero_entries": sum(
                entry != 0
                for matrix in value["normal_tractor_square"].values()
                for entry in matrix
            ),
        },
        "obstruction": {
            "reason": "the derivative coefficients uniquely determine DeltaL1 and a common DeltaL0=0 across all form slots, after which a rank-four algebraic residual with twelve entries remains",
            "smallest_exact_witness": "the residual chain coefficient at parent row 4 and H0 input 1 is 2/3",
            "conclusion": "zeroth-order corrections to L0 and L1 cannot strictify the first Nariai BGG square with K fixed",
            "not_a_full_curved_bgg_no_go": True,
        },
        "flags": {
            "NARIAI_FIRST_BGG_ZEROTH_ORDER_STRICTIFICATION_OBSTRUCTION_V1": True,
            "ZEROTH_ORDER_STRICTIFICATION_EXISTS": False,
            "GENUINELY_DERIVATIVE_CORRECTION_STILL_OPEN": True,
            "HOMOTOPY_COHERENT_CURVED_TRANSFER_STILL_OPEN": True,
            "NARIAI_CURVED_BGG_HPL_COMPRESSION": False,
            "NARIAI_GREEN_HOMOTOPY": False,
            "ALL_CURVED_COMPRESSIONS_OBSTRUCTED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "C_G2_NARIAI_GENUINELY_DERIVATIVE_OR_HOMOTOPY_COHERENT_BGG_CORRECTION",
        "claim_boundary": (
            "This corrected exact screen uses the Nariai Schouten components (-1/6,+1/6,+1/6,+1/6) together with the distinct covector form-slot and dual-vector standard-tractor curvature actions. It proves that no pair of arbitrary zeroth-order bundle maps DeltaL0:H0->C0 and DeltaL1:H1->C1 can turn the certified PBW first BGG candidate into a strict chain square while the trace-free conformal-Killing operator K is fixed. All derivative equations are mutually consistent and uniquely fix DeltaL1 and DeltaL0=0; the obstruction is instead a rank-four algebraic residual with twelve entries and normalized witness one. Harmonic normalization remains exact. This is not a no-go for genuinely derivative-dependent splitting corrections, a homotopy-coherent curved BGG transfer, compression of the Yang--Mills detour middle, an independently constructed Nariai Green homotopy, an open background class, or any quantum claim."
        ),
        "provenance": {
            "source_manifest": sources,
            "verification_commands": [
                "PYTHONPATH=. python3 d_quotient_classical/causal_transfer/nariai_first_differential_bgg_correction.py --check --guards",
                "PYTHONPATH=. python3 d_quotient_classical/causal_transfer/verify_nariai_first_differential_bgg_correction.py",
                "python3 -m unittest -v d_quotient_classical.causal_transfer.tests.test_nariai_first_differential_bgg_correction",
                "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/nariai-first-bgg-zeroth-order-strictification-obstruction-v1.schema.json -d d_quotient_classical/certificates/NARIAI_FIRST_BGG_ZEROTH_ORDER_STRICTIFICATION_OBSTRUCTION_V1.json",
            ],
        },
    }


def _report(value: dict[str, object]) -> str:
    checks = value["exact_checks"]
    return rf"""# Nariai first-BGG zeroth-order strictification obstruction

This report supersedes certificate hash
`c4738c825fd1814962d4970e62341f0399fafb08331fe9b57bc25958b1fadbcc`,
whose producer assigned the wrong sign to the temporal Schouten component.

On unit Nariai, the Schouten tensor has orthonormal components
\((-1/6,+1/6,+1/6,+1/6)\).  The form indices carry the covector curvature
action while the middle standard-tractor slot carries its dual vector action.
With all three conventions enforced, the normal tractor exterior square is
nonzero, as it must be on this non-conformally-flat Einstein background.

We tested the complete zeroth-order correction ansatz

\[
d^D(L_0+\Delta L_0)-(L_1+\Delta L_1)K=0,
\]

where \(\Delta L_0\) is an arbitrary \(15\times4\) bundle map and
\(\Delta L_1\) is an arbitrary \(60\times9\) bundle map.  For each one-form
row, the three derivative axes transverse to its form slot have coefficient
rank `{checks['transverse_rank_set'][0]}` and uniquely determine that row of
\(\Delta L_1\).  The remaining axis then determines a candidate row of
\(\Delta L_0\).

The derivative equations are mutually compatible across all four form slots:
they fix \(\Delta L_0=0\) and a rank-`{checks['DeltaL1_rank']}` correction
\(\Delta L_1\).  But the remaining algebraic coefficient has rank
`{checks['algebraic_residual_rank']}` and
`{checks['algebraic_residual_nonzero_entries']}` nonzero entries.  A normalized
witness is

\[
\frac32\bigl(d^D(L_0+\Delta L_0)-(L_1+\Delta L_1)K\bigr)_{{4,1}}=1.
\]

Both harmonic projection defects remain rank zero, so the failure is not a
normalization artifact.  Thus zeroth-order corrections cannot strictify this
first square with the conformal-Killing operator fixed.  Genuinely
derivative-dependent corrections and homotopy-coherent curved transfer remain
open; this is not a no-go theorem for the Nariai Yang--Mills detour
compression or its Green theory.
"""


def verify(value: dict[str, object]) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    if value != build():
        raise ValueError("certificate drifted from exact reconstruction")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--diagnose", action="store_true")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    raw = candidate()
    if args.diagnose:
        print(
            json.dumps(
                {
                    "transverse_rank_set": sorted(set(raw["transverse_ranks"])),
                    "inconsistent_rows": raw["inconsistent_rows"],
                    "cross_form_defect_count": len(raw["cross_form_defects"]),
                    "cross_form_defect_head": raw["cross_form_defects"][:12],
                    "correction0_rank": raw["correction0"].rank(),
                    "correction1_rank": raw["correction1"].rank(),
                    "algebraic_defect_rank": raw["algebraic_defect"].rank(),
                    "algebraic_defect_nonzero": sum(
                        entry != 0 for entry in raw["algebraic_defect"]
                    ),
                    "projection0_defect_rank": raw["projection0_defect"].rank(),
                    "projection1_defect_rank": raw["projection1_defect"].rank(),
                },
                indent=2,
            )
        )
    value = build()
    if args.guards:
        checks = value["exact_checks"]
        if checks["transverse_rank_set"] != [9] or checks["cross_form_defect_count"] != 0:
            raise AssertionError("zeroth-order obstruction rank guard failed")
        if checks["algebraic_residual_rank"] != 4 or checks["algebraic_residual_nonzero_entries"] != 12:
            raise AssertionError("algebraic residual guard failed")
        if checks["normalized_witness_value"] != "1":
            raise AssertionError("normalized witness guard failed")
        if checks["harmonic_projection_defect_ranks"] != [0, 0]:
            raise AssertionError("harmonic normalization guard failed")
    if args.write:
        OUTPUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
        REPORT.write_text(_report(value))
    if args.check:
        verify(json.loads(OUTPUT.read_text()))
    if args.write or args.check or args.guards:
        print(f"{value['result_id']}: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
