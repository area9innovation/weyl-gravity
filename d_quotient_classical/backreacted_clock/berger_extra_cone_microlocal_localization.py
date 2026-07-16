#!/usr/bin/env python3
"""Microlocal and homological localization of the raw endpoint extra cone."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json

import sympy as sp

from d_quotient_classical.backreacted_clock.berger_causal_witness_preflight import _matrix_from_record, _symbol
from d_quotient_classical.backreacted_clock.berger_linearized_bach_pbw import ROOT
from d_quotient_classical.backreacted_clock.berger_metric_lower_by_two_biwave import (
    CERTIFICATE_PATH as NORMAL_FORM_CERTIFICATE,
)
from d_quotient_classical.backreacted_clock.berger_raw_endpoint_metric_cone_no_go import (
    CERTIFICATE_PATH as CONE_CERTIFICATE,
    _exact_data as _cone_data,
)


CERTIFICATE_PATH = ROOT / "d_quotient_classical/certificates/BERGER_EXTRA_CONE_MICROLOCAL_LOCALIZATION.json"
REPORT_PATH = ROOT / "d_quotient_classical/reports/berger-extra-cone-microlocal-localization.md"


def _sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _dependency(path):
    payload = json.loads(path.read_text())
    return {"result_id": payload["result_id"], "sha256": _sha256(path)}


def _load_artifact(record):
    path = ROOT / record["path"]
    if _sha256(path) != record["sha256"]:
        raise AssertionError(f"artifact digest drifted: {path}")
    return _matrix_from_record(json.loads(path.read_text()))


def _entries(vector):
    return [[index, str(sp.factor(value))] for index, value in enumerate(vector) if value != 0]


def _exact_data():
    cone = _cone_data()
    p = sp.symbols("p0:4")
    point = {p[0]: sp.sqrt(2), p[1]: 1, p[2]: 0, p[3]: 0}
    principal = cone["principal"].subs(point)
    right = principal.nullspace()
    left = principal.T.nullspace()
    if len(right) != 1 or len(left) != 1:
        raise AssertionError("extra characteristic is not simple")
    right = right[0]
    left = left[0]
    if sp.simplify(principal * right) != sp.zeros(13, 1):
        raise AssertionError("right characteristic vector failed")
    if sp.simplify(left.T * principal) != sp.zeros(1, 13):
        raise AssertionError("left characteristic covector failed")

    retained_h = right[:10, 0]
    clock = right[10:12, 0]
    graph = right[12, 0]
    if retained_h == sp.zeros(10, 1) or clock == sp.zeros(2, 1):
        raise AssertionError("extra characteristic did not mix retained and clock rows")
    if graph != 0:
        raise AssertionError("normalized extra characteristic unexpectedly uses y")

    # At the extra cone q=-1, the retained A10 principal q^2 I is invertible.
    q_at_point = -point[p[0]] ** 2 + point[p[1]] ** 2
    retained_image = sp.simplify(q_at_point ** 2 * retained_h)
    if retained_image == sp.zeros(10, 1):
        raise AssertionError("raw null vector became a retained metric characteristic")

    # Independently form the local retained 20-row companion principal
    # [[qI,0],[sigma_2(V2),qI]].  Its determinant is q^20 and it is invertible
    # on the raw extra cone because q=-1 there.
    normal = json.loads(NORMAL_FORM_CERTIFICATE.read_text())
    remainder = _load_artifact(normal["normal_form"]["artifacts"]["lower_by_two_remainder"])
    remainder2 = _symbol(remainder, 2)
    q = -p[0] ** 2 + p[1] ** 2 + p[2] ** 2 + p[3] ** 2
    companion = sp.zeros(20)
    companion[:10, :10] = q * sp.eye(10)
    companion[10:, :10] = remainder2
    companion[10:, 10:] = q * sp.eye(10)
    companion_at_point = companion.subs(point)
    if companion_at_point.rank() != 20:
        raise AssertionError("retained companion inherited the raw extra cone")

    # For F=p0^2-2|p|^2, the Hamilton base velocity is
    # dx/dt=(partial_p F)/(partial_p0 F), of magnitude sqrt(2).
    spatial_norm = p[1] ** 2 + p[2] ** 2 + p[3] ** 2
    extra = p[0] ** 2 - 2 * spatial_norm
    temporal_hamilton = sp.diff(extra, p[0]).subs(point)
    spatial_hamilton = sp.Matrix([sp.diff(extra, p[index]).subs(point) for index in range(1, 4)])
    speed_squared = sp.factor((spatial_hamilton.dot(spatial_hamilton)) / temporal_hamilton ** 2)
    if speed_squared != 2:
        raise AssertionError("extra Hamilton speed drifted")

    return {
        "right": right,
        "left": left,
        "retained_h": retained_h,
        "clock": clock,
        "retained_image": retained_image,
        "companion_rank": int(companion_at_point.rank()),
        "speed_squared": speed_squared,
    }


def build():
    data = _exact_data()
    payload = {
        "schema": "pure-weyl-berger-extra-cone-microlocal-localization-v1",
        "result_id": "BERGER_EXTRA_CONE_MICROLOCAL_LOCALIZATION",
        "setting_id": json.loads(CONE_CERTIFICATE.read_text())["setting_id"],
        "claim_status": "CERTIFIED_SIMPLE_REAL_CHARACTERISTIC_MIXED_WITNESS_ARTIFACT_RETAINED_ROUTE_EXACT",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {
            "metric_cone_no_go": _dependency(CONE_CERTIFICATE),
            "metric_normal_form": _dependency(NORMAL_FORM_CERTIFICATE),
        },
        "microlocal_necessity": {
            "theorem_used": "a Green inverse on arbitrary sources supported in a prescribed cone cannot have a simple real principal characteristic whose Hamilton bicharacteristic exits that cone",
            "hypotheses_checked": [
                "real homogeneous extra factor F=p0^2-2|p|^2",
                "rank drop exactly one",
                "nonzero left and right characteristic polarizations",
                "dF nonzero at (sqrt(2),1,0,0)",
            ],
            "hamilton_speed_squared": str(data["speed_squared"]),
            "conclusion": "no arbitrary-source L13 Green inverse supported in the background metric cone",
        },
        "characteristic_polarization": {
            "row_order": ["h00", "h01", "h02", "h03", "h11", "h12", "h13", "h22", "h23", "h33", "R", "Theta", "y"],
            "right_null_vector_nonzero_entries": _entries(data["right"]),
            "left_null_covector_nonzero_entries": _entries(data["left"]),
            "retained_metric_projection_nonzero": True,
            "clock_projection_nonzero": True,
            "graph_y_component_zero": True,
            "retained_A10_principal_image_nonzero": True,
        },
        "homological_interpretation": {
            "important_correction": "the bad L13 polarization is mixed; the selector projection does not kill it and it must not be called a pure clock mode",
            "what_is_contractible": "the clock/graph rows in the BV differential, not the characteristic polarization of this particular witness operator",
            "correct_operation": "apply the certified BV SDR and construct a different witness/chain homotopy on the retained complex; do not project L13 solutions",
            "retained_companion": "C20=[[Box_2,-I10],[V_2,Box_2]]",
            "retained_companion_principal_determinant": "q^20",
            "retained_companion_rank_on_raw_extra_cone": data["companion_rank"],
            "raw_extra_cone_survives_retained_companion": False,
        },
        "exact_checks": {
            "right_null_vector_exact": True,
            "left_null_covector_exact": True,
            "simple_rank_one_characteristic_exact": True,
            "hamilton_speed_sqrt_two_exact": True,
            "raw_polarization_mixes_retained_and_clock_rows": True,
            "selector_does_not_kill_raw_polarization": True,
            "raw_polarization_not_characteristic_for_retained_A10": True,
            "retained_companion_has_no_raw_extra_cone": True,
        },
        "flags": {
            "BERGER_EXTRA_CONE_MICROLOCAL_LOCALIZATION": True,
            "BERGER_RAW_EXTRA_MODE_PURE_CLOCK": False,
            "BERGER_RETAINED_BIWAVE_COMPANION_EXACT": True,
            "BERGER_RETAINED_BIWAVE_CAUSAL_RESOLVENT": False,
            "BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY": False,
        },
        "next_gate": "BERGER_RETAINED_BIWAVE_VOLTERRA_RESOLVENT",
        "claim_boundary": "This theorem closes the microlocal implication and corrects the localization language. The raw extra polarization is a mixed artifact of the chosen clock-coupled witness, not a pure clock vector. The BV clock rows remain contractible and the retained companion removes the extra cone, but convergence, causal Green operators and the retained chain homotopy remain open.",
    }
    return payload


def _text(payload):
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def _report():
    return r"""# Berger extra cone: microlocal and homological localization

The additional characteristic of the raw analytic endpoint is of real
principal type. At \((p_0,p_1,p_2,p_3)=(\sqrt2,1,0,0)\), the principal matrix
has rank twelve and exact right polarization

\[
v=-2\sqrt2,h_{00}-\frac{29}{20}h_{01}
-\frac{9\sqrt2}{20}h_{11}-\frac{27\sqrt2}{16}R+\Theta.
\]

Its Hamilton speed is \(\sqrt2\), so the standard real-principal-type
propagation argument upgrades the algebraic determinant result to a genuine
obstruction to metric-cone-supported inverses on arbitrary sources.

The homological interpretation needs one correction: this polarization is
not a pure clock vector, and the selector projection does not kill it. It has
nonzero retained metric and clock components. What is contractible is the
clock/graph subcomplex of the BV differential, not this polarization of the
chosen witness operator. Consequently the correct operation is to apply the
BV SDR and build a new retained witness, not to project solutions of
\(L_{13}\).

That retained local companion is

\[
\mathcal C_{20}=\begin{pmatrix}\Box_2&-I\\V_2&\Box_2\end{pmatrix}.
\]

Its principal determinant is \(q^{20}\), and it has full rank twenty on the
raw \(\sqrt2\) cone. Thus the unwanted cone is absent after changing to the
correct retained analytic presentation. The remaining gate is the causal
Volterra estimate, not another algebraic characteristic search.
"""


def verify(payload):
    if any(value is not True for value in payload["exact_checks"].values()):
        raise AssertionError("an extra-cone localization check dropped")
    if payload["flags"]["BERGER_RAW_EXTRA_MODE_PURE_CLOCK"] is not False:
        raise AssertionError("mixed raw polarization was mislabeled pure clock")
    if payload["flags"]["BERGER_RETAINED_BIWAVE_CAUSAL_RESOLVENT"] is not False:
        raise AssertionError("causal resolvent was promoted by a symbol theorem")
    if payload["next_gate"] != "BERGER_RETAINED_BIWAVE_VOLTERRA_RESOLVENT":
        raise AssertionError("next gate drifted")


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
        raise AssertionError("extra-cone localization outputs drifted")
    if args.guards:
        mutants = [
            ("pure clock", ("flags", "BERGER_RAW_EXTRA_MODE_PURE_CLOCK"), True),
            ("causal promotion", ("flags", "BERGER_RETAINED_BIWAVE_CAUSAL_RESOLVENT"), True),
            ("drop microlocal check", ("exact_checks", "hamilton_speed_sqrt_two_exact"), False),
        ]
        for name, path, replacement in mutants:
            mutant = deepcopy(payload)
            mutant[path[0]][path[1]] = replacement
            try:
                verify(mutant)
            except AssertionError:
                continue
            raise AssertionError(f"mutation guard accepted: {name}")
    print("BERGER_EXTRA_CONE_MICROLOCAL_LOCALIZATION: PASS")


if __name__ == "__main__":
    main()
