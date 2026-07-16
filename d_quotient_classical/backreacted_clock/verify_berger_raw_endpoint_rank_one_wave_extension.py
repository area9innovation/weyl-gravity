#!/usr/bin/env python3
"""Independent replay of the frozen rank-one wave prolongation."""

import hashlib
import json

from d_quotient_classical.backreacted_clock.berger_causal_witness_preflight import _matrix_from_record
from d_quotient_classical.backreacted_clock.berger_curved_witness_export import _is_zero, _one, _sparse_multiply, _zero
from d_quotient_classical.backreacted_clock.berger_linearized_bach_pbw import ROOT
from d_quotient_classical.backreacted_clock.berger_raw_clock_reattached_witness_transport import _subtract
from d_quotient_classical.backreacted_clock.berger_raw_endpoint_rank_one_wave_extension import CERTIFICATE_PATH


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
    transport_path = ROOT / "d_quotient_classical/certificates/BERGER_RAW_CLOCK_REATTACHED_WITNESS_TRANSPORT.json"
    if _sha256(transport_path) != certificate["dependency_refs"]["raw_witness_transport"]["sha256"]:
        raise AssertionError("raw witness dependency drifted")
    transport = json.loads(transport_path.read_text())
    p34 = _load(transport["operators"]["P34_raw"])
    l12 = [[p34[row][column] for column in range(5, 17)] for row in range(5, 17)]

    artifacts = certificate["prolongation"]["artifacts"]
    seed = _load(artifacts["modulus_seed_F2"])
    l13 = _load(artifacts["prolonged_L13"])
    u13 = _load(artifacts["field_shear_U13"])
    e13 = _load(artifacts["equation_shear_E13"])
    c13 = _subtract(_identity(13), _subtract(u13, _identity(13)))

    diagonal = _zero(13, 13)
    for row in range(12):
        for column in range(12):
            diagonal[row][column] = l12[row][column]
    diagonal[12][12] = _one()
    replay = _sparse_multiply(_sparse_multiply(e13, l13), c13)
    if not _is_zero(_subtract(replay, diagonal)):
        raise AssertionError("independent prolongation reduction failed")

    scalar_wave = e13[10][12]
    factored = _sparse_multiply([[scalar_wave]], seed)
    original_modulus = [[l12[10][column] for column in range(10)]]
    if not _is_zero(_subtract(original_modulus, [[entry.scale(-1) for entry in factored[0]]])):
        raise AssertionError("independent C_R=-Box F2 replay failed")
    if certificate["flags"]["BERGER_RAW_ENDPOINT_EXTENSION_GREEN_OPERATORS"] is not False:
        raise AssertionError("extension theorem promoted Green operators")
    print("independent rank-one Berger wave extension replay: PASS")
    print("extension Green operators remain open")


if __name__ == "__main__":
    verify()
