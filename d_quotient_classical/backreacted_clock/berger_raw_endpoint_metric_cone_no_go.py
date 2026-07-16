#!/usr/bin/env python3
"""Exact metric-cone no-go for a Green inverse of the full L13 endpoint.

The result is intentionally scoped to an inverse on arbitrary thirteen-row
sources with support in the background metric cone.  It does not obstruct a
BV chain homotopy after the contractible clock/graph sector is removed.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json

import sympy as sp

from d_quotient_classical.backreacted_clock.berger_causal_witness_preflight import _matrix_from_record, _symbol
from d_quotient_classical.backreacted_clock.berger_linearized_bach_pbw import ALPHA_B, ROOT, U, V
from d_quotient_classical.backreacted_clock.berger_raw_endpoint_rank_one_wave_extension import (
    CERTIFICATE_PATH as EXTENSION_CERTIFICATE,
)
from d_quotient_classical.backreacted_clock.berger_metric_lower_by_two_biwave import (
    CERTIFICATE_PATH as NORMAL_FORM_CERTIFICATE,
)


CERTIFICATE_PATH = ROOT / "d_quotient_classical/certificates/BERGER_RAW_ENDPOINT_METRIC_CONE_NO_GO.json"
REPORT_PATH = ROOT / "d_quotient_classical/reports/berger-raw-endpoint-metric-cone-no-go.md"


def _sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _dependency(path):
    payload = json.loads(path.read_text())
    return {"result_id": payload["result_id"], "sha256": _sha256(path)}


def _load_l13():
    extension = json.loads(EXTENSION_CERTIFICATE.read_text())
    artifact = extension["prolongation"]["artifacts"]["prolonged_L13"]
    path = ROOT / artifact["path"]
    if _sha256(path) != artifact["sha256"]:
        raise AssertionError("L13 artifact digest drifted")
    return _matrix_from_record(json.loads(path.read_text()))


def _exact_data():
    l13 = _load_l13()
    p = sp.symbols("p0:4")
    fixture = {U: 3 * sp.sqrt(10) / 20, V: 2 * sp.sqrt(10) / 3, ALPHA_B: 5}
    wave = -p[0] ** 2 + p[1] ** 2 + p[2] ** 2 + p[3] ** 2
    spatial_norm = p[1] ** 2 + p[2] ** 2 + p[3] ** 2
    extra = p[0] ** 2 - 2 * spatial_norm

    # Douglis column/row weights for (h_10,R,Theta,y) and their equations.
    column_weights = [4] * 10 + [2, 1, 2]
    row_weights = [0] * 10 + [0, 1, 2]
    principal = sp.zeros(13)
    for row in range(13):
        for column in range(13):
            order = column_weights[column] - row_weights[row]
            principal[row, column] = sp.factor(sum(
                coefficient.subs(fixture) * sp.prod(p[axis] for axis in word)
                for _, word, coefficient in l13[row][column].terms
                if len(word) == order
            ))

    # The sparse clock incidence reduces the 13x13 determinant to four scalar
    # contractions.  Here b=B_Theta, d=B_R, c=C_Theta and f is the actual
    # defining row -F2.  For a=wave^2,
    # det = -wave*a^8*((a-cb)fd+(fb)(cd)).
    b = _symbol([[l13[row][11]] for row in range(10)], 1).subs(fixture)
    d = _symbol([[l13[row][10]] for row in range(10)], 2).subs(fixture)
    c = _symbol([[l13[11][column] for column in range(10)]], 3).subs(fixture)
    f = _symbol([[l13[12][column] for column in range(10)]], 2).subs(fixture)
    contractions = {
        "c_b": sp.factor((c * b)[0]),
        "f_d": sp.factor((f * d)[0]),
        "f_b": sp.factor((f * b)[0]),
        "c_d": sp.factor((c * d)[0]),
    }
    bracket = sp.factor(
        (wave ** 2 - contractions["c_b"]) * contractions["f_d"]
        + contractions["f_b"] * contractions["c_d"]
    )
    expected_bracket = sp.Rational(3, 100) * wave ** 3 * extra
    if sp.expand(bracket - expected_bracket) != 0:
        raise AssertionError("bordered determinant contraction drifted")
    determinant = sp.factor(-wave * (wave ** 2) ** 8 * bracket)
    expected_determinant = sp.factor(-sp.Rational(3, 100) * wave ** 20 * extra)
    if sp.expand(determinant - expected_determinant) != 0:
        raise AssertionError("Douglis determinant identity failed")

    # The additional factor is genuine: away from the metric characteristic
    # cone it gives a simple rank-one symbol kernel.
    rank_extra = int(principal.subs({p[0]: sp.sqrt(2), p[1]: 1, p[2]: 0, p[3]: 0}).rank())
    rank_off = int(principal.subs({p[0]: 2, p[1]: 1, p[2]: 0, p[3]: 0}).rank())
    if (rank_extra, rank_off) != (12, 13):
        raise AssertionError("extra characteristic rank certificate drifted")
    return {
        "principal": principal,
        "column_weights": column_weights,
        "row_weights": row_weights,
        "contractions": contractions,
        "bracket": bracket,
        "determinant": determinant,
        "rank_extra": rank_extra,
        "rank_off": rank_off,
    }


def build():
    data = _exact_data()
    payload = {
        "schema": "pure-weyl-berger-raw-endpoint-metric-cone-no-go-v1",
        "result_id": "BERGER_RAW_ENDPOINT_METRIC_CONE_NO_GO",
        "setting_id": json.loads(EXTENSION_CERTIFICATE.read_text())["setting_id"],
        "claim_status": "CERTIFIED_FULL_ENDPOINT_METRIC_CAUSAL_INVERSE_NO_GO_HYBRID_CHAIN_ROUTE_OPEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {
            "rank_one_extension": _dependency(EXTENSION_CERTIFICATE),
            "metric_normal_form": _dependency(NORMAL_FORM_CERTIFICATE),
        },
        "douglis_symbol": {
            "row_order": ["metric_10", "modulus", "phase", "graph"],
            "column_order": ["h_10", "R", "Theta", "y"],
            "column_weights": data["column_weights"],
            "row_weights": data["row_weights"],
            "nonzero_entries": len(data["principal"].todok()),
            "scalar_contractions": {key: str(value) for key, value in data["contractions"].items()},
            "bordered_bracket": str(data["bracket"]),
            "determinant": "-(3/100)(-p0^2+|p|^2)^20(p0^2-2|p|^2)",
            "metric_characteristic_multiplicity": 20,
            "extra_characteristic": "p0^2=2|p|^2",
            "extra_characteristic_speed": "sqrt(2)",
            "rank_on_generic_extra_characteristic": data["rank_extra"],
            "rank_off_characteristic": data["rank_off"],
        },
        "no_go": {
            "ruled_out": "advanced/retarded inverse of the complete analytic L13 endpoint on arbitrary thirteen-row sources with support contained in the background metric causal cone",
            "reason": "the simple extra characteristic p0^2=2|p|^2 carries a genuine rank-one symbol kernel and propagates at speed sqrt(2)>1",
            "scope_guard": "this does not obstruct a BV chain homotopy after algebraically contracting the clock/graph sector, nor a Green inverse relative to the wider characteristic cone",
            "architectural_consequence": "do not require G13_pm as the causal theorem; contract the acyclic clock/graph incidence first and construct Lambda on the retained complex",
        },
        "exact_checks": {
            "complete_L13_imported": True,
            "douglis_weights_typed": True,
            "bordered_determinant_reduction_exact": True,
            "full_determinant_factorization_exact": True,
            "extra_cone_is_simple_off_metric_cone": True,
            "extra_speed_exceeds_metric_light_speed": True,
        },
        "flags": {
            "BERGER_RAW_ENDPOINT_METRIC_CONE_NO_GO": True,
            "BERGER_RAW_ENDPOINT_EXTENSION_GREEN_OPERATORS": False,
            "BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY": False,
        },
        "next_gate": "BERGER_HYBRID_RETAINED_CAUSAL_CHAIN_HOMOTOPY",
        "claim_boundary": "This is a principal causal-support obstruction for an inverse of the complete L13 endpoint on arbitrary sources. It does not claim that the contractible clock mode is physical, and it does not obstruct the support-local hybrid BV contraction that removes that mode before causal propagation.",
    }
    return payload


def _text(payload):
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def _report():
    return r"""# Raw Berger endpoint: metric-cone Green no-go

For the exact analytic endpoint in variables \((h_{10},R,\Theta,y)\), the
Douglis principal determinant is

\[
\det\sigma_{\rm D}(L_{13})
=-\frac{3}{100}
(-p_0^2+|\mathbf p|^2)^{20}
(p_0^2-2|\mathbf p|^2).
\]

The additional factor is genuine: at \(p_0^2=2|\mathbf p|^2\), away from the
metric characteristic cone, the principal matrix has rank twelve. Therefore
arbitrary endpoint sources excite a characteristic travelling at speed
\(\sqrt2\). The complete \(L_{13}\) cannot possess advanced and retarded
inverses whose supports stay inside the background metric cone.

This is not a physical superluminality claim. The extra characteristic sits
in the clock/graph incidence that is already acyclic in the BV complex. The
correct causal theorem is consequently hybrid: contract that sector by the
certified support-local homotopy first, then construct causal chain homotopies
on the retained complex. Requiring a metric-causal \(G_{13,\pm}\) on arbitrary
thirteen-row sources is an unnecessarily strong—and now exactly impossible—
intermediate gate.
"""


def verify(payload):
    if any(value is not True for value in payload["exact_checks"].values()):
        raise AssertionError("an exact metric-cone no-go check dropped")
    if payload["flags"]["BERGER_RAW_ENDPOINT_EXTENSION_GREEN_OPERATORS"] is not False:
        raise AssertionError("impossible endpoint Green gate was promoted")
    if payload["next_gate"] != "BERGER_HYBRID_RETAINED_CAUSAL_CHAIN_HOMOTOPY":
        raise AssertionError("hybrid next gate drifted")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    payload = build()
    verify(payload)
    if args.write:
        CERTIFICATE_PATH.write_text(_text(payload))
        REPORT_PATH.write_text(_report())
    if args.check and (CERTIFICATE_PATH.read_text() != _text(payload) or REPORT_PATH.read_text() != _report()):
        raise AssertionError("metric-cone no-go outputs drifted")
    if args.guards:
        for key in ("full_determinant_factorization_exact", "extra_cone_is_simple_off_metric_cone"):
            mutant = deepcopy(payload)
            mutant["exact_checks"][key] = False
            try:
                verify(mutant)
            except AssertionError:
                continue
            raise AssertionError(f"mutation guard accepted: {key}")
    print("BERGER_RAW_ENDPOINT_METRIC_CONE_NO_GO: PASS")


if __name__ == "__main__":
    main()
