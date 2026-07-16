#!/usr/bin/env python3
"""Consumer replay of the raw endpoint rank-one Schur preflight."""

import hashlib
import json

import sympy as sp

from d_quotient_classical.backreacted_clock.berger_causal_witness_preflight import _matrix_from_record, _symbol
from d_quotient_classical.backreacted_clock.berger_curved_witness_export import _sparse_multiply
from d_quotient_classical.backreacted_clock.berger_linearized_bach_pbw import ROOT
from d_quotient_classical.backreacted_clock.berger_raw_endpoint_green_preflight import CERTIFICATE_PATH


def verify():
    certificate = json.loads(CERTIFICATE_PATH.read_text())
    dependency = ROOT / "d_quotient_classical/certificates/BERGER_RAW_CLOCK_REATTACHED_WITNESS_TRANSPORT.json"
    if hashlib.sha256(dependency.read_bytes()).hexdigest() != certificate["dependency_ref"]["sha256"]:
        raise AssertionError("transport dependency drifted")
    transport = json.loads(dependency.read_text())
    reference = transport["operators"]["P34_raw"]
    path = ROOT / reference["path"]
    if hashlib.sha256(path.read_bytes()).hexdigest() != reference["sha256"]:
        raise AssertionError("raw P34 artifact drifted")
    p = _matrix_from_record(json.loads(path.read_text()))
    b = [[p[row][column] for column in range(15, 17)] for row in range(5, 15)]
    c = [[p[row][column] for column in range(5, 15)] for row in range(15, 17)]
    bc6 = _symbol(_sparse_multiply(b, c), 6)
    p0, p1, p2, p3 = sp.symbols("p0:4")
    wave = -p0**2 + p1**2 + p2**2 + p3**2
    if any(sp.rem(sp.factor(value), wave, p0) != 0 for value in bc6 if value != 0):
        raise AssertionError("a top Schur entry lost wave divisibility")
    if sp.simplify(bc6.subs({p0: 1, p1: 1, p2: 0, p3: 0})) != sp.zeros(10):
        raise AssertionError("null Schur symbol did not vanish")
    if sp.simplify(bc6.subs({p0: 2, p1: 1, p2: 3, p3: 1})).rank() != 1:
        raise AssertionError("generic Schur symbol rank drifted")
    if certificate["flags"]["BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY"] is not False:
        raise AssertionError("preflight promoted the causal theorem")
    print("independent raw endpoint Green preflight replay: PASS")


if __name__ == "__main__":
    verify()
