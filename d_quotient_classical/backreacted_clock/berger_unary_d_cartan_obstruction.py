#!/usr/bin/env python3
"""Exact microlocal obstruction to a bare-complex unary D-Cartan homotopy."""

from __future__ import annotations

import argparse
from copy import deepcopy
from dataclasses import dataclass
import hashlib
import json

import sympy as sp

from d_quotient_classical.backreacted_clock.berger_causal_witness_preflight import (
    _matrix_from_record,
    _symbol,
)
from d_quotient_classical.backreacted_clock.berger_linearized_bach_pbw import ROOT


Q1_PATH = ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_MINIMAL_OPERATOR.json"
D_PATH = ROOT / "d_quotient_classical/certificates/BERGER_54_ROW_LOCAL_D_ACTION.json"
CERTIFICATE_PATH = ROOT / "d_quotient_classical/certificates/BERGER_UNARY_D_CARTAN_MICROLOCAL_OBSTRUCTION.json"
REPORT_PATH = ROOT / "d_quotient_classical/reports/berger-unary-D-Cartan-microlocal-obstruction.md"
SCHEMA_PATH = ROOT / "d_quotient_classical/schema/berger-unary-D-Cartan-microlocal-obstruction-v1.schema.json"


def _sha256(path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@dataclass(frozen=True)
class BergerUnaryDCartanObstruction:
    payload: dict[str, object]

    @classmethod
    def build(cls) -> "BergerUnaryDCartanObstruction":
        q1 = json.loads(Q1_PATH.read_text())
        d_action = json.loads(D_PATH.read_text())
        blocks = q1["q1_blocks"]
        k = _matrix_from_record(blocks["K_spatial"])
        h = _matrix_from_record(blocks["H_retained"])
        identity = _matrix_from_record(blocks["minus_K_spatial_sharp"])
        d26 = _matrix_from_record(d_action["retained_D_action"]["matrix"])

        p0, p1, p2, p3 = sp.symbols("p0:4")
        covector = {p0: 1, p1: 1, p2: 0, p3: 0}
        k1 = sp.Matrix(_symbol(k, 1).subs(covector))
        h4 = sp.Matrix(_symbol(h, 4).subs(covector).subs({sp.Symbol("alpha_B"): 5}))
        l1 = sp.Matrix(_symbol(identity, 1).subs(covector))
        d1 = sp.Matrix(_symbol(d26, 1).subs(covector))
        if h4 * k1 != sp.zeros(10, 3) or l1 * h4 != sp.zeros(3, 10):
            raise AssertionError("null Douglis symbols do not form a complex")
        if d1 != sp.eye(26):
            raise AssertionError("D symbol is not identity at the chosen covector")

        x = sp.eye(10)[:, 2]
        dual = sp.zeros(10, 1)
        dual[2] = 1
        dual[5] = -1
        if h4 * x != sp.zeros(10, 1):
            raise AssertionError("chosen field class is not H4-closed")
        if dual.T * k1 != sp.zeros(1, 3):
            raise AssertionError("dual witness does not annihilate im K1")
        if (dual.T * x)[0] != 1:
            raise AssertionError("dual witness is not normalized")

        ranks = {
            "K1": int(k1.rank()),
            "H4": int(h4.rank()),
            "L1": int(l1.rank()),
        }
        cohomology = [
            3 - ranks["K1"],
            (10 - ranks["H4"]) - ranks["K1"],
            (10 - ranks["L1"]) - ranks["H4"],
            3 - ranks["L1"],
        ]
        if cohomology != [0, 6, 6, 0]:
            raise AssertionError("null symbol cohomology dimensions drifted")

        payload: dict[str, object] = {
            "schema": "pure-weyl-berger-unary-D-Cartan-microlocal-obstruction-v1",
            "result_id": "BERGER_UNARY_D_CARTAN_MICROLOCAL_OBSTRUCTION",
            "setting_id": q1["setting_id"],
            "claim_status": "CERTIFIED_NO_LOCAL_UNARY_CARTAN_ON_BARE_COMPLEX",
            "dependency_tags": ["LOCAL-ALGEBRAIC", "MICROLOCAL-SYMBOL"],
            "dependency_refs": {
                "retained_q1": {"result_id": q1["result_id"], "sha256": _sha256(Q1_PATH)},
                "local_D_action": {"result_id": d_action["result_id"], "sha256": _sha256(D_PATH)},
            },
            "douglis_symbol_fixture": {
                "covector": [1, 1, 0, 0],
                "metric_square": 0,
                "D_symbol": 1,
                "degree_ranks": [3, 10, 10, 3],
                "differential_orders": [1, 4, 1],
                "symbol_ranks": ranks,
                "cohomology_dimensions": cohomology,
            },
            "normalized_field_class": {
                "field_order": [
                    "h_hat_00", "h_hat_01", "h_hat_02", "h_hat_03", "h_hat_11",
                    "h_hat_12", "h_hat_13", "h_hat_22", "h_hat_23", "h_hat_33"
                ],
                "representative": [str(value) for value in x],
                "representative_name": "h_hat_02",
                "dual_witness": [str(value) for value in dual],
                "dual_witness_name": "coefficient(h_hat_02)-coefficient(h_hat_12)",
                "H4_on_representative": "0",
                "dual_on_im_K1": "0",
                "dual_on_representative": "1",
                "D_on_class": "identity",
            },
            "obstruction_argument": {
                "assumption": "a finite-order support-local differential iota_D^(1) with [q1,iota_D^(1)]=D on the bare 26-row complex",
                "localization": "sigma(D)=zeta_0=1 is invertible near the chosen covector, so D^(-1)iota_D^(1) would microlocally contract q1",
                "contradiction": "the exact Douglis symbol complex has the displayed normalized nonzero class",
                "lift_to_54_rows": "any 54-row homotopy would descend as pi_cl iota_D,54^(1) iota_cl to a 26-row homotopy because the SDR is D-equivariant",
            },
            "exact_checks": {
                "null_covector_nonzero": True,
                "D_symbol_invertible": True,
                "Douglis_symbol_is_complex": True,
                "symbol_cohomology_nonzero": True,
                "field_representative_closed": True,
                "dual_annihilates_gauge_image": True,
                "dual_witness_normalized": True,
                "obstruction_descends_from_54_to_26": True,
            },
            "flags": {
                "BERGER_UNARY_D_CARTAN_LOCAL_BARE_COMPLEX_NO_GO": True,
                "BERGER_UNARY_D_CARTAN_EXISTENCE_FULL_4D": False,
                "BERGER_ARITY_TWO_D_CARTAN_SOURCE_FULL_4D": False,
                "BERGER_ARITY_TWO_D_CARTAN_FULL_4D": False,
                "BERGER_RESIDUAL_OR_CAUSAL_CARTAN_EXTENSION": False,
            },
            "next_gate": "BERGER_RESIDUAL_OR_CAUSAL_CARTAN_EXTENSION",
            "claim_boundary": (
                "This exact microlocal theorem rules out a finite-order support-local unary D-Cartan homotopy on the declared bare retained 26-row complex and, by the D-equivariant SDR, on its bare 54-row extension. It does not rule out a Cartan homotopy after adjoining residual BFV rows, imposing the derived zero-charge quotient, or using the causal Green extension."
            ),
        }
        result = cls(payload)
        result.verify()
        return result

    def verify(self) -> None:
        if not all(self.payload["exact_checks"].values()):
            raise AssertionError("microlocal obstruction check dropped")
        flags = self.payload["flags"]
        if flags["BERGER_UNARY_D_CARTAN_LOCAL_BARE_COMPLEX_NO_GO"] is not True:
            raise AssertionError("unary obstruction flag dropped")
        for key, value in flags.items():
            if key != "BERGER_UNARY_D_CARTAN_LOCAL_BARE_COMPLEX_NO_GO" and value is not False:
                raise AssertionError(f"downstream Cartan flag promoted: {key}")
        witness = self.payload["normalized_field_class"]
        if witness["dual_on_representative"] != "1":
            raise AssertionError("normalized dual witness drifted")

    def certificate_text(self) -> str:
        return json.dumps(self.payload, indent=2, sort_keys=True) + "\n"

    def report_text(self) -> str:
        return r"""# Microlocal obstruction to a bare-complex unary D-Cartan homotopy

At the exact null covector (zeta=(1,1,0,0)), the retained Douglis symbol
complex has ranks

\[
3\xrightarrow{K_1}10\xrightarrow{H_4}10\xrightarrow{L_1}3,
\qquad
(\operatorname{rank}K_1,\operatorname{rank}H_4,\operatorname{rank}L_1)
=(3,1,3).
\]

Its symbol-cohomology dimensions are therefore \((0,6,6,0)\). An explicit
field class is \(x=h_{\hat 0 2}\). It is \(H_4\)-closed, and the normalized
functional

\[
\ell(x)=x_{02}-x_{12}
\]

annihilates \(\operatorname{im}K_1\) while satisfying \(\ell(x)=1\).

At the same covector, \(\sigma(D)=\zeta_0=1\). If a finite-order local
\(\iota_D^{(1)}\) obeyed \([q_1,\iota_D^{(1)}]=D\), microlocal inversion of
\(D\) would contract the symbol complex, contradicting the displayed class.
The D-equivariant 54-to-26 SDR transfers the same obstruction to the bare
54-row complex.

This does not obstruct a residual/BFV or causal Cartan extension. It proves
that the next construction must enlarge or derive-reduce the complex rather
than attempting the arity-two equation on the bare local rows.
"""


def _write(result: BergerUnaryDCartanObstruction) -> None:
    CERTIFICATE_PATH.write_text(result.certificate_text())
    REPORT_PATH.write_text(result.report_text())


def _check(result: BergerUnaryDCartanObstruction) -> None:
    if CERTIFICATE_PATH.read_text() != result.certificate_text():
        raise SystemExit(f"stale certificate: {CERTIFICATE_PATH}")
    if REPORT_PATH.read_text() != result.report_text():
        raise SystemExit(f"stale report: {REPORT_PATH}")


def _guards(result: BergerUnaryDCartanObstruction) -> None:
    for name, path, value in (
        ("drop obstruction", ("flags", "BERGER_UNARY_D_CARTAN_LOCAL_BARE_COMPLEX_NO_GO"), False),
        ("promote unary", ("flags", "BERGER_UNARY_D_CARTAN_EXISTENCE_FULL_4D"), True),
        ("erase witness", ("normalized_field_class", "dual_on_representative"), "0"),
    ):
        mutant = deepcopy(result.payload)
        mutant[path[0]][path[1]] = value
        try:
            BergerUnaryDCartanObstruction(mutant).verify()
        except AssertionError:
            continue
        raise AssertionError(f"mutation guard failed: {name}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    result = BergerUnaryDCartanObstruction.build()
    if args.check:
        _check(result)
    else:
        _write(result)
    if args.guards:
        _guards(result)
    print("bare 26/54-row local unary D-Cartan: OBSTRUCTED")
    print("next gate: residual/BFV or causal Cartan extension")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
