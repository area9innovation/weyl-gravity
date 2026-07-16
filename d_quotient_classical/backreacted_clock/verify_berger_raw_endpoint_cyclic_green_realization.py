#!/usr/bin/env python3
"""Independent replay of the 36-row cyclic analytic realization."""

import hashlib
import json

from d_quotient_classical.backreacted_clock.berger_causal_witness_preflight import _matrix_from_record
from d_quotient_classical.backreacted_clock.berger_curved_witness_export import _adjoint_matrix, _is_zero, _one, _sparse_multiply, _zero
from d_quotient_classical.backreacted_clock.berger_linearized_bach_pbw import ROOT
from d_quotient_classical.backreacted_clock.berger_raw_clock_reattached_witness_transport import _subtract
from d_quotient_classical.backreacted_clock.berger_raw_endpoint_cyclic_green_realization import CERTIFICATE_PATH


def _sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(reference):
    path = ROOT / reference["path"]
    if _sha256(path) != reference["sha256"]:
        raise AssertionError(f"artifact drifted: {path}")
    return _matrix_from_record(json.loads(path.read_text()))


def _identity(rank):
    result = _zero(rank, rank)
    for index in range(rank):
        result[index][index] = _one()
    return result


def verify():
    certificate = json.loads(CERTIFICATE_PATH.read_text())
    artifacts = certificate["artifacts"]
    p36 = _load(artifacts["analytic_P36"])
    pairing = _load(artifacts["analytic_pairing36"])
    i_sol = _load(artifacts["field_solution_inclusion"])
    p_sol = _load(artifacts["field_solution_projection"])
    i_src = _load(artifacts["field_source_inclusion"])
    p_src = _load(artifacts["field_source_projection"])
    homotopy = _load(artifacts["graph_homotopy_H13"])

    extension_path = ROOT / "d_quotient_classical/certificates/BERGER_RAW_ENDPOINT_RANK_ONE_WAVE_EXTENSION.json"
    if _sha256(extension_path) != certificate["dependency_refs"]["rank_one_wave_extension"]["sha256"]:
        raise AssertionError("rank-one extension dependency drifted")
    extension = json.loads(extension_path.read_text())
    l13 = _load(extension["prolongation"]["artifacts"]["prolonged_L13"])

    if not _is_zero(_subtract(_sparse_multiply(p_sol, i_sol), _identity(12))):
        raise AssertionError("solution graph p i failed")
    if not _is_zero(_subtract(_sparse_multiply(p_src, i_src), _identity(12))):
        raise AssertionError("source graph p i failed")
    if not _is_zero(_subtract(
        _subtract(_identity(13), _sparse_multiply(i_sol, p_sol)),
        _sparse_multiply(homotopy, l13),
    )):
        raise AssertionError("solution graph contraction failed")
    if not _is_zero(_subtract(
        _subtract(_identity(13), _sparse_multiply(i_src, p_src)),
        _sparse_multiply(l13, homotopy),
    )):
        raise AssertionError("source graph contraction failed")
    cyclic = _subtract(
        _sparse_multiply(_adjoint_matrix(p36), pairing),
        _sparse_multiply(pairing, p36),
    )
    if not _is_zero(cyclic):
        raise AssertionError("independent analytic cyclicity replay failed")
    if certificate["row_layout"]["analytic_realization_degree_ranks"] != [5, 13, 13, 5]:
        raise AssertionError("analytic ranks drifted")
    if certificate["flags"]["BERGER_RAW_ENDPOINT_EXTENSION_GREEN_OPERATORS"] is not False:
        raise AssertionError("analytic realization promoted Green operators")
    print("independent cyclic Berger Green-realization replay: PASS")
    print("advanced/retarded operators remain open")


if __name__ == "__main__":
    verify()
