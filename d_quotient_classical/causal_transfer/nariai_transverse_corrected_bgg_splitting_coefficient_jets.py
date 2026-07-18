#!/usr/bin/env python3
"""Derive transverse corrected-BGG splitting coefficient jets on Nariai.

The canonical HPL inclusions are recomputed in the associative coefficient-jet
PBW algebra.  The automorphism correction in degree one is then determined,
jet by jet, by the strict natural identity

    d_aut L0 = L1_corrected K

together with the fixed BGG normalization.  No interpolation of point values
is used.
"""

from __future__ import annotations

import argparse
from functools import lru_cache
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp

from covariant_completion.curved_operator.adjoint_tractor_bgg_curved_pbw import (
    _add,
    _algebraic,
    _scale,
)
from covariant_completion.curved_operator.adjoint_tractor_bgg_differential_screen import (
    _adjoint_actions,
)
from covariant_completion.curved_operator.adjoint_tractor_kostant_compression import (
    _adjoint_basis,
    _coordinate_map,
)
from d_quotient_classical.causal_transfer.coefficient_jet_pbw import (
    CoefficientJetPBW,
    JetLinearizedOperator,
    jet_add,
    jet_scale,
    parallel_zero_variation,
)
from d_quotient_classical.causal_transfer.nariai_automorphism_prolongation_first_two_rows import (
    fixture as automorphism_fixture,
)
from d_quotient_classical.causal_transfer.nariai_first_differential_bgg_correction import (
    NariaiBackground,
    _derivative_rows,
)
from d_quotient_classical.causal_transfer.nariai_transverse_coordinate_curvature_jets import (
    orthonormal_covector_jet,
)
from d_quotient_classical.causal_transfer.nariai_transverse_curvature_incidence_variation import (
    exact_variation,
)
from d_quotient_classical.causal_transfer.nariai_transverse_jet_aware_middle_schur_variation import (
    _pbw_layers,
)
from d_quotient_classical.causal_transfer.nariai_yang_mills_middle_compression import (
    fixture as middle_fixture,
)


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUTPUT = ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_CORRECTED_BGG_SPLITTING_COEFFICIENT_JETS_V1.json"
REPORT = ROOT / "d_quotient_classical/reports/nariai-transverse-corrected-bgg-splitting-coefficient-jets.md"
SCHEMA = ROOT / "d_quotient_classical/schema/nariai-transverse-corrected-bgg-splitting-coefficient-jets-v1.schema.json"
VERIFIER = HERE / "verify_nariai_transverse_corrected_bgg_splitting_coefficient_jets.py"
TESTS = HERE / "tests/test_nariai_transverse_corrected_bgg_splitting_coefficient_jets.py"
REQUIREMENTS = ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_COEFFICIENT_JET_PBW_REQUIREMENTS_V1.json"
OLD_POINT_DATA = ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_JET_AWARE_MIDDLE_SCHUR_VARIATION_V1.json"
BACKEND = HERE / "coefficient_jet_pbw.py"
COORDINATE_JETS = HERE / "nariai_transverse_coordinate_curvature_jets.py"


Table = dict[tuple[int, ...], sp.Matrix]


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _count(table: Table) -> int:
    return sum(value != 0 for matrix in table.values() for value in matrix)


def _clean(table: Table) -> Table:
    return {
        word: matrix.applyfunc(sp.expand)
        for word, matrix in table.items()
        if matrix != sp.zeros(*matrix.shape)
    }


def _sparse(matrix: sp.Matrix) -> dict[str, Any]:
    return {
        "shape": [matrix.rows, matrix.cols],
        "rank": matrix.rank(),
        "entries": [
            [row, column, str(value)]
            for (row, column), value in sorted(matrix.todok().items())
        ],
        "sha256": hashlib.sha256(
            sp.srepr(sp.ImmutableSparseMatrix(matrix)).encode()
        ).hexdigest(),
    }


def _sparse_operator_coefficient(matrix: sp.Matrix) -> dict[str, Any]:
    """Serialize an operator coefficient without an unnecessary rank solve."""

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


def _table(table: Table) -> dict[str, Any]:
    payload = "\n".join(
        f"{word}:{sp.srepr(sp.ImmutableSparseMatrix(table[word]))}"
        for word in sorted(table)
    )
    return {
        "orders": sorted({len(word) for word in table}),
        "nonzero_coefficients": _count(table),
        "entries": [
            {
                "word": list(word),
                "matrix": _sparse_operator_coefficient(table[word]),
            }
            for word in sorted(table)
        ],
        "sha256": hashlib.sha256(payload.encode()).hexdigest(),
    }


def _deserialize_table(record: dict[str, Any]) -> Table:
    output = {}
    for entry in record["entries"]:
        matrix = sp.zeros(*entry["matrix"]["shape"])
        for row, column, value in entry["matrix"]["entries"]:
            matrix[row, column] = sp.sympify(value)
        output[tuple(entry["word"])] = matrix
    return output


def _difference(left: Table, right: Table) -> Table:
    if not left:
        return _scale(right, -1) if right else {}
    if not right:
        return dict(left)
    return _add(left, _scale(right, -1))


def _base_operators():
    middle = middle_fixture()
    automorphism = automorphism_fixture()
    algebraic = middle["algebraic"]
    screen = middle["screen"]
    layers = _pbw_layers()
    pbw = {name: CoefficientJetPBW(layer) for name, layer in layers.items()}

    _, basis = _adjoint_basis()
    k_actions = _adjoint_actions(basis[11:15], basis)
    rho = tuple(
        NariaiBackground.metric[axis, axis] * k_actions[axis] / 6
        for axis in range(4)
    )
    rho0 = sp.Matrix.vstack(*rho)
    rho1_rows = []
    for left in range(4):
        for right in range(left + 1, 4):
            block = sp.zeros(15, 60)
            block[:, 15 * right : 15 * (right + 1)] = rho[left]
            block[:, 15 * left : 15 * (left + 1)] = -rho[right]
            rho1_rows.append(block)
    rho1 = sp.Matrix.vstack(*rho1_rows)
    derivative0, derivative1 = _derivative_rows()
    delta0 = _add(_algebraic(rho0), derivative0)
    delta1 = _add(_algebraic(rho1), derivative1)
    total0 = _add(_algebraic(screen.cohomology_d0), delta0)

    zero = parallel_zero_variation
    n0 = pbw["C0"].compose(
        zero(_algebraic(screen.q1), "q1"),
        zero(delta0, "tractor-delta0"),
        "n0",
    )
    n1 = pbw["C1"].compose(
        zero(_algebraic(screen.q2), "q2"),
        zero(delta1, "tractor-delta1"),
        "n1",
    )
    i0 = zero(_algebraic(algebraic.i0), "i0")
    i1 = zero(_algebraic(algebraic.i1), "i1")
    n0_i0 = pbw["H0"].compose(n0, i0, "n0-i0")
    n1_i1 = pbw["H1"].compose(n1, i1, "n1-i1")
    inclusion0 = jet_add(
        i0,
        jet_scale(n0_i0, -1),
        pbw["H0"].compose(n0, n0_i0, "n0-square-i0"),
        name="L0-HPL",
    )
    inclusion1 = jet_add(
        i1,
        jet_scale(n1_i1, -1),
        pbw["H1"].compose(n1, n1_i1, "n1-square-i1"),
        name="L1-HPL",
    )
    if inclusion0.base != middle["inclusion0"] or inclusion1.base != middle["inclusion1"]:
        raise AssertionError("base HPL inclusion drifted")
    return middle, automorphism, screen, pbw, total0, inclusion0, inclusion1


def _incidence_provider(screen):
    _, basis = _adjoint_basis()
    embedded, left_inverse = _coordinate_map(basis)
    point = exact_variation()["delta_curvature_incidence"]
    point_matrix = sp.zeros(*point["shape"])
    for row, column, value in point["entries"]:
        point_matrix[row, column] = sp.sympify(value)

    @lru_cache(maxsize=None)
    def provider(word: tuple[int, ...]) -> Table:
        if not word:
            incidence = point_matrix
        else:
            incidence = sp.zeros(60, 4)
            for left in range(4):
                for right in range(left + 1, 4):
                    covector = orthonormal_covector_jet(word, left, right)
                    standard = sp.zeros(6)
                    standard[1:5, 1:5] = -covector.T
                    coordinates = left_inverse * standard.reshape(36, 1)
                    if embedded * coordinates != standard.reshape(36, 1):
                        raise AssertionError("incidence jet escaped so(4,2)")
                    incidence[15 * left : 15 * (left + 1), right] = coordinates
                    incidence[15 * right : 15 * (right + 1), left] = -coordinates
        return _algebraic(incidence * screen.harmonic_p0)

    return provider


def _solve_algebraic_correction(defect: Table, gauge: Table) -> sp.Matrix:
    unexpected = [word for word in defect if len(word) != 1]
    if unexpected:
        raise AssertionError(f"correction defect has non-gauge orders: {unexpected}")
    axes = tuple((axis,) for axis in range(4))
    k_stack = sp.Matrix.hstack(*(gauge[word] for word in axes))
    correction = sp.zeros(60, 9)
    for row in range(60):
        right = sp.Matrix.hstack(
            *(defect.get(word, sp.zeros(60, 4))[row, :] for word in axes)
        )
        solution, parameters = k_stack.T.gauss_jordan_solve(right.T)
        if parameters.rows:
            raise AssertionError("degree-one correction lost uniqueness")
        correction[row, :] = solution.T
    reconstructed = {
        word: correction * gauge[word]
        for word in axes
        if correction * gauge[word] != sp.zeros(60, 4)
    }
    if _difference(defect, reconstructed):
        raise AssertionError("degree-one correction did not reconstruct defect")
    return correction


@lru_cache(maxsize=1)
def operator_data():
    middle, automorphism, screen, pbw, total0, inclusion0, inclusion1 = _base_operators()
    incidence_base = _difference(total0, automorphism["d_aut"])
    incidence = JetLinearizedOperator(
        incidence_base,
        _incidence_provider(screen),
        "I_Omega-p0",
    )
    d_aut = jet_add(
        parallel_zero_variation(total0, "total0"),
        jet_scale(incidence, -1),
        name="d_aut",
    )
    gauge = parallel_zero_variation(middle["first_bgg"], "K")
    raw_defect = jet_add(
        pbw["H0"].compose(d_aut, inclusion0, "d_aut-L0"),
        jet_scale(pbw["H0"].compose(inclusion1, gauge, "L1raw-K"), -1),
        name="raw-first-square",
    )
    correction_base = automorphism["corrected_l1"][()] - middle["inclusion1"][()]
    if _solve_algebraic_correction(raw_defect.base, gauge.base) != correction_base:
        raise AssertionError("base correction no longer follows from the strict square")

    @lru_cache(maxsize=None)
    def correction_provider(word: tuple[int, ...]) -> Table:
        correction = _solve_algebraic_correction(raw_defect.delta(word), gauge.base)
        return {} if correction == sp.zeros(60, 9) else _algebraic(correction)

    correction = JetLinearizedOperator(
        _algebraic(correction_base), correction_provider, "Delta-L1"
    )
    corrected_l1 = jet_add(inclusion1, correction, name="L1-corrected")
    first_square = jet_add(
        pbw["H0"].compose(d_aut, inclusion0, "d-aut-L0-final"),
        jet_scale(pbw["H0"].compose(corrected_l1, gauge, "L1-K-final"), -1),
        name="first-square-final",
    )
    return {
        "middle": middle,
        "automorphism": automorphism,
        "screen": screen,
        "pbw": pbw,
        "L0": inclusion0,
        "L1_raw": inclusion1,
        "L1_correction": correction,
        "L1_corrected": corrected_l1,
        "d_aut": d_aut,
        "K": gauge,
        "raw_defect": raw_defect,
        "first_square": first_square,
    }


@lru_cache(maxsize=1)
def exact_data() -> dict[str, Any]:
    value = operator_data()
    requirements = json.loads(REQUIREMENTS.read_text())["exact_data"]["nariai_replay_requirements"]
    l0_words = tuple(tuple(word) for word in requirements["corrected_L0_positive_coefficient_jet_words_required_for_first_square"])
    l1_words = tuple(tuple(word) for word in requirements["corrected_L1_positive_coefficient_jet_words_required_for_associativity"])
    all_words = ((),) + tuple(sorted(set(l0_words) | set(l1_words), key=lambda word: (len(word), word)))

    first_square_checks = {}
    for word in all_words:
        defect = value["first_square"].delta(word)
        if defect:
            raise AssertionError(f"corrected first square failed at coefficient jet {word}")
        first_square_checks[str(word)] = 0
    if value["first_square"].base:
        raise AssertionError("corrected first-square base drifted")

    l0_jets = {str(word): _table(value["L0"].delta(word)) for word in ((),) + l0_words}
    l1_jets = {str(word): _table(value["L1_corrected"].delta(word)) for word in ((),) + l1_words}
    correction_jets = {str(word): _table(value["L1_correction"].delta(word)) for word in ((),) + l1_words}

    old = json.loads(OLD_POINT_DATA.read_text())["exact_data"]["operator_variations"]
    old_l0 = _deserialize_table(old["corrected_L0"])
    old_l1 = _deserialize_table(old["corrected_L1"])
    l0_point_defect = _difference(value["L0"].delta(()), old_l0)
    l1_point_defect = _difference(value["L1_corrected"].delta(()), old_l1)

    return {
        "derivation": {
            "L0": "finite covariant HPL series i0-n0 i0+n0^2 i0 in the coefficient-jet PBW algebra",
            "L1_raw": "finite covariant HPL series i1-n1 i1+n1^2 i1 in the coefficient-jet PBW algebra",
            "L1_correction": "unique algebraic left factor of the strict-square defect against the fixed conformal-Killing operator at each ordered coefficient jet",
            "incidence_zero_jet": "independent exact moving-frame curvature-incidence variation",
            "incidence_positive_jets": "coordinate covariant curvature recurrence transformed to the background orthonormal frame; base positive curvature jets vanish",
            "interpolation_used": False,
        },
        "coefficient_jets": {
            "L0": l0_jets,
            "L1_corrected": l1_jets,
            "L1_algebraic_correction": correction_jets,
        },
        "strict_square": {
            "identity": "d_aut L0 = L1_corrected K",
            "base_defect_coefficients": _count(value["first_square"].base),
            "coefficient_jet_defects": first_square_checks,
            "all_required_jets_zero": True,
        },
        "superseded_point_replay_comparison": {
            "L0_point_defect": _table(l0_point_defect),
            "L1_point_defect": _table(l1_point_defect),
            "old_point_values_authoritative_after_associative_replay": not l0_point_defect and not l1_point_defect,
        },
        "disposition": {
            "corrected_splitting_coefficient_jets_complete": True,
            "associative_M_L1_K_replay_ready": True,
            "middle_and_schur_replayed": False,
            "rank_310_transverse_SDR_decided": False,
        },
    }


def build() -> dict[str, Any]:
    data = exact_data()
    refs = {}
    for key, path, result_id in (
        ("coefficient_jet_requirements", REQUIREMENTS, "NARIAI_TRANSVERSE_COEFFICIENT_JET_PBW_REQUIREMENTS_V1"),
        ("superseded_point_replay", OLD_POINT_DATA, "NARIAI_TRANSVERSE_JET_AWARE_MIDDLE_SCHUR_VARIATION_V1"),
    ):
        payload = json.loads(path.read_text())
        if payload["result_id"] != result_id:
            raise AssertionError(f"dependency drifted: {key}")
        refs[key] = {"path": str(path.relative_to(ROOT)), "result_id": result_id, "sha256": _sha(path)}
    sources = (Path(__file__).resolve(), VERIFIER, TESTS, SCHEMA, BACKEND, COORDINATE_JETS)
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "schema": "nariai-transverse-corrected-bgg-splitting-coefficient-jets-v1",
        "schema_version": "1.0.0",
        "result_id": "NARIAI_TRANSVERSE_CORRECTED_BGG_SPLITTING_COEFFICIENT_JETS_V1",
        "result_state": "CORRECTED_BGG_SPLITTING_COEFFICIENT_JETS_EXACT",
        "lifecycle_state": "CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "dependency_refs": refs,
        "exact_data": data,
        "exact_checks": {
            "no_interpolation": not data["derivation"]["interpolation_used"],
            "strict_square_all_required_jets": data["strict_square"]["all_required_jets_zero"],
            "splitting_jets_complete": data["disposition"]["corrected_splitting_coefficient_jets_complete"],
            "middle_not_overclaimed": not data["disposition"]["middle_and_schur_replayed"],
            "rank_310_not_overclaimed": not data["disposition"]["rank_310_transverse_SDR_decided"],
        },
        "flags": {
            "NARIAI_TRANSVERSE_CORRECTED_SPLITTING_COEFFICIENT_JETS": True,
            "NARIAI_TRANSVERSE_STRICT_FIRST_SQUARE_COEFFICIENT_JETS": True,
            "NARIAI_TRANSVERSE_ASSOCIATIVE_PBW_REPLAY": False,
            "TRANSVERSE_COMPLETE_RANK_310_SDR_FIRST_VARIATION": False,
            "TRANSVERSE_CAUSAL_TRANSFER": False,
        },
        "next_gate": "NARIAI_TRANSVERSE_ASSOCIATIVE_MIDDLE_SHIFTED_CHAIN_SCHUR_REPLAY",
        "claim_boundary": "This certificate derives the corrected L0/L1 covariant coefficient jets required by the transverse replay and proves the strict first-square identity through every required ordered jet. It uses the finite covariant HPL series and the unique normalized degree-one correction; it does not interpolate point data. It does not yet replay the Yang-Mills middle, shifted chain, compressed Schur operator, complete rank-310 SDR, support, or causal transfer.",
        "source_manifest": {str(path.relative_to(ROOT)): _sha(path) for path in sources},
        "verification_commands": [
            "python3 -m d_quotient_classical.causal_transfer.nariai_transverse_corrected_bgg_splitting_coefficient_jets --check",
            "python3 d_quotient_classical/causal_transfer/verify_nariai_transverse_corrected_bgg_splitting_coefficient_jets.py",
            "python3 -m unittest d_quotient_classical.causal_transfer.tests.test_nariai_transverse_corrected_bgg_splitting_coefficient_jets",
            "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/nariai-transverse-corrected-bgg-splitting-coefficient-jets-v1.schema.json -d d_quotient_classical/certificates/NARIAI_TRANSVERSE_CORRECTED_BGG_SPLITTING_COEFFICIENT_JETS_V1.json",
        ],
    }


def report(payload: dict[str, Any]) -> str:
    comparison = payload["exact_data"]["superseded_point_replay_comparison"]
    return rf"""# Transverse corrected-BGG splitting coefficient jets

The missing corrected splitting jets are now derived rather than fitted.  The
degree-zero and raw degree-one splittings come from the finite covariant HPL
series in the associative coefficient-jet PBW algebra.  At every ordered jet,
the remaining degree-one algebraic correction is the unique normalized left
factor of the strict-square defect against the fixed conformal-Killing map.

The result proves

\[
d_{{\rm aut}}L_0=L_1^{{\rm corrected}}K
\]

at the base and through all four required `L0` jets and all fourteen required
`L1` jets.  The comparison with the superseded point-only replay has
`{comparison['L0_point_defect']['nonzero_coefficients']}` `L0` and
`{comparison['L1_point_defect']['nonzero_coefficients']}` `L1` point
coefficients.  The next gate is the associative parent-middle, shifted-chain,
and compressed-Schur replay; no rank-310 SDR or causal theorem is claimed.
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build()
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
    if args.write:
        OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        REPORT.write_text(report(payload))
    if args.check and json.loads(OUTPUT.read_text()) != payload:
        raise AssertionError("corrected splitting coefficient-jet artifact is stale")
    print("NARIAI_TRANSVERSE_CORRECTED_BGG_SPLITTING_COEFFICIENT_JETS_V1: PASS")


if __name__ == "__main__":
    main()
