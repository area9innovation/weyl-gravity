#!/usr/bin/env python3
"""Export the exact radial part of the nonlinear Berger clock chart."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
CERTIFICATE = P / "certificates/BERGER_NONLINEAR_CLOCK_RADIAL_CANONICAL_MAP_F2_F3.json"
SCHEMA = P / "schema/berger-nonlinear-clock-radial-canonical-map-f2-f3-v1.schema.json"
REPORT = P / "reports/berger-nonlinear-clock-radial-canonical-map-f2-f3.md"
DEPENDENCIES = {
    "component_contract": P / "certificates/BERGER_108_ROW_COMPONENT_JET_CONTRACT.json",
    "completed_unary": P / "certificates/BERGER_108_ROW_NONLINEAR_CLOCK_SECOND_JET.json",
    "scalarization_obstruction": P / "certificates/BERGER_108_ROW_APPARATUS_Q2_Q3_SCALARIZATION_OBSTRUCTION.json",
    "linear_clock_sdr": ROOT / "d_quotient_classical/certificates/BERGER_MINIMAL_BV_CLOCK_SDR.json",
}
SOURCE_FILES = [
    Path(__file__),
    P / "verify_berger_nonlinear_clock_radial_canonical_map_f2_f3.py",
    P / "tests/test_berger_nonlinear_clock_radial_canonical_map_f2_f3.py",
    SCHEMA,
    REPORT,
]

METRIC_ROWS = tuple(range(5, 15))
R_ROW = 15
METRIC_DUAL_ROWS = tuple(range(27, 37))
R_DUAL_ROW = 37
ETA_COMPONENTS = (-1, 0, 0, 0, 1, 0, 0, 1, 0, 1)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def taylor_entries(*, delete_cubic_trace: bool = False) -> dict[str, list[dict[str, Any]]]:
    """Return canonical graded-symmetric F2/F3 components.

    Entries store one representative of a graded-symmetric input multiset in
    the factorial convention F(x)=F1 x+F2(x,x)/2+F3(x,x,x)/6+... .  No term
    contains two odd inputs, so ordinary and Koszul multiset representatives
    coincide on this radial block.
    """

    f2: list[dict[str, Any]] = []
    f3: list[dict[str, Any]] = []

    def add(target, output, inputs, coefficient, role):
        if coefficient:
            target.append({"output_row": output, "input_rows": sorted(inputs), "coefficient": coefficient, "role": role})

    for index, (metric, dual, eta) in enumerate(zip(METRIC_ROWS, METRIC_DUAL_ROWS, ETA_COMPONENTS, strict=True)):
        add(f2, metric, (R_ROW, metric), 2, "metric field radial product")
        add(f2, metric, (R_ROW, R_ROW), -6 * eta, "metric field conformal trace")
        add(f2, dual, (R_ROW, dual), -2, "metric cotangent inverse Jacobian")
        add(f2, R_DUAL_ROW, (metric, dual), -2, "radial cotangent field derivative")
        add(f2, R_DUAL_ROW, (R_ROW, dual), 6 * eta, "radial cotangent trace derivative")

        add(f3, metric, (R_ROW, R_ROW, metric), 2, "metric field radial product")
        add(f3, metric, (R_ROW, R_ROW, R_ROW), 0 if delete_cubic_trace else -12 * eta, "metric field conformal trace")
        add(f3, dual, (R_ROW, R_ROW, dual), 6, "metric cotangent inverse Jacobian")
        add(f3, R_DUAL_ROW, (R_ROW, metric, dual), 2, "radial cotangent field derivative")
        add(f3, R_DUAL_ROW, (R_ROW, R_ROW, dual), -12 * eta, "radial cotangent trace derivative")
    return {"F2": f2, "F3": f3}


def exact_chart_audit(*, delete_cubic_trace: bool = False, omit_radial_cotangent: bool = False) -> dict[str, Any]:
    r, h, y, eta = sp.symbols("R H Y eta")
    true_metric = sp.expand((1 + r) ** 2 * h - r**2 * (3 + 2 * r) * eta)
    expected = h + 2 * r * h - 3 * r**2 * eta + r**2 * h - 2 * r**3 * eta
    if delete_cubic_trace:
        expected += 2 * r**3 * eta
    chart_defect = sp.expand(true_metric - expected)

    t = sp.symbols("t")
    inverse = sp.series(
        (t * y + (t * r) ** 2 * (3 + 2 * t * r) * eta) / (1 + t * r) ** 2,
        t,
        0,
        4,
    ).removeO().subs(t, 1).expand()
    inverse_expected = y - 2 * r * y + 3 * r**2 * y + 3 * r**2 * eta - 4 * r**3 * eta
    inverse_defect = sp.expand(inverse - inverse_expected)

    hs = sp.symbols("H0:10")
    ps = sp.symbols("P0:10")
    a = (1 + r) ** 2
    b = [2 * (1 + r) * (value - 3 * r * component) for value, component in zip(hs, ETA_COMPONENTS, strict=True)]
    new_p = [value / a for value in ps]
    radial_p = sp.Symbol("P_R")
    new_radial_p = radial_p if omit_radial_cotangent else radial_p - sum(value * momentum for value, momentum in zip(b, ps, strict=True)) / a
    d_h_defects = [sp.simplify(new_p[index] * a - ps[index]) for index in range(10)]
    d_r_defect = sp.simplify(sum(new_p[index] * b[index] for index in range(10)) + new_radial_p - radial_p)
    mutation_value = sp.simplify(d_r_defect.subs({r: 0, hs[0]: 1, ps[0]: 1, **{value: 0 for value in (*hs[1:], *ps[1:])}}))

    return {
        "physical_relation": "gHat=(1+R)^2 g with g=eta+H-2 R eta in the linearly dressed carrier",
        "exact_metric_map": sp.sstr(true_metric),
        "cubic_metric_map": sp.sstr(expected),
        "metric_map_defect": sp.sstr(chart_defect),
        "metric_map_defect_count": int(chart_defect != 0),
        "inverse_through_cubic": sp.sstr(inverse),
        "inverse_expected": sp.sstr(inverse_expected),
        "inverse_defect": sp.sstr(inverse_defect),
        "inverse_defect_count": int(inverse_defect != 0),
        "cotangent_lift": {
            "H_true_star": "(1+R)^(-2) H_linear_star",
            "R_true_star": "R_linear_star-2(H-3 R eta).H_linear_star/(1+R)",
            "canonical_one_form_identity": "H_true_star.dH_true+R_true_star.dR=H_linear_star.dH+R_linear_star.dR",
            "dH_coefficient_defect_count": sum(value != 0 for value in d_h_defects),
            "dR_coefficient_defect": sp.sstr(d_r_defect),
            "dR_coefficient_defect_count": int(d_r_defect != 0),
            "mutation_fixture_value": sp.sstr(mutation_value),
        },
    }


def build() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    required = {
        "component_contract": "CANONICAL_108_ROW_COMPONENT_CROSSWALK_CERTIFIED",
        "completed_unary": "COMPLETE_FIRST_BIDEGREE_UNARY_GATE",
        "scalarization_obstruction": "NONLINEAR_CLOCK_COORDINATE_JET_NONUNIQUENESS_CERTIFIED",
        "linear_clock_sdr": "canonical_antifield_transformation_exact",
    }
    for name, flag in required.items():
        if values[name].get("flags", {}).get(flag) is not True:
            raise AssertionError(f"dependency flag dropped: {name}.{flag}")

    entries = taylor_entries()
    audit = exact_chart_audit()
    trace_mutation = exact_chart_audit(delete_cubic_trace=True)
    cotangent_mutation = exact_chart_audit(omit_radial_cotangent=True)
    if audit["metric_map_defect_count"] or audit["inverse_defect_count"]:
        raise AssertionError("radial metric chart failed")
    if audit["cotangent_lift"]["dH_coefficient_defect_count"] or audit["cotangent_lift"]["dR_coefficient_defect_count"]:
        raise AssertionError("radial cotangent lift is not canonical")
    if not trace_mutation["metric_map_defect_count"]:
        raise AssertionError("cubic trace mutation was not detected")
    if not cotangent_mutation["cotangent_lift"]["dR_coefficient_defect_count"]:
        raise AssertionError("cotangent mutation was not detected")
    if len(entries["F2"]) != 38 or len(entries["F3"]) != 38:
        raise AssertionError("radial Taylor support changed")

    radial_map = values["completed_unary"]["second_jet_derivation"]["radial_metric_map"]
    if radial_map != "H_true=H+2*R*H-3*R^2*eta+O(3)":
        raise AssertionError("completed unary radial quadratic map drifted")
    boundary = (
        "This exact LOCAL-ALGEBRAIC certificate closes the radial subgate of the nonlinear Berger clock chart. "
        "Starting from the certified linear dressing h=H-2 R eta and the invariant physical metric relation "
        "gHat=(1+R)^2 g, it derives H_true=H+2 R H-3 R^2 eta+R^2 H-2 R^3 eta exactly. Its quadratic "
        "truncation is precisely the radial map used by BERGER_108_ROW_NONLINEAR_CLOCK_SECOND_JET. The result "
        "serializes all 38 graded-symmetric F2 and 38 F3 component entries on metric, radial, metric-cotangent "
        "and radial-cotangent rows in the factorial convention. The nonlinear cotangent lift is derived as the "
        "inverse transpose of the exact field Jacobian; its canonical one-form identity vanishes coefficientwise, "
        "while deletion of the radial cotangent correction is detected. The inverse field chart is checked through "
        "cubic order and deletion of the -2 R^3 eta term is detected. This does not supply the temporal relational-"
        "time F2/F3 retraction, transport the detector/emitter action tensors, export complete scalar q2/q3, replay "
        "the arity identities, prove K_Berger equivariance or observer-morphism stability, restrict detector response "
        "to Z2, promote nonlinear rank, activate physical Bridge 3, establish finite-parameter causality, or make a "
        "quantum claim. The scalar interaction lift remains NO_CERTIFIED_MAP until the temporal chart is fixed."
    )
    return {
        "schema": "closed-universe-berger-nonlinear-clock-radial-canonical-map-f2-f3-v1",
        "result_id": "BERGER_NONLINEAR_CLOCK_RADIAL_CANONICAL_MAP_F2_F3",
        "setting_id": values["completed_unary"]["setting_id"],
        "claim_status": "CERTIFIED_RADIAL_F2_F3_AND_COTANGENT_LIFT_TEMPORAL_OPEN",
        "atlas_status": "CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "dependency_refs": {name: {"path": str(path.relative_to(ROOT)), "result_id": values[name]["result_id"], "sha256": sha256(path)} for name, path in DEPENDENCIES.items()},
        "radial_chart": audit,
        "taylor_payload": {
            "factorial_convention": "F=F1+F2/2!+F3/3!+...",
            "component_rows": {"metric": list(METRIC_ROWS), "radial": R_ROW, "metric_cotangent": list(METRIC_DUAL_ROWS), "radial_cotangent": R_DUAL_ROW},
            "parity": {"metric_and_radial": "even", "metric_and_radial_cotangents": "odd"},
            "F2": entries["F2"],
            "F3": entries["F3"],
            "F2_entry_count": len(entries["F2"]),
            "F3_entry_count": len(entries["F3"]),
            "canonical_sha256": canonical_sha256(entries),
        },
        "mutation_results": [
            {"name": "delete_cubic_minus_2_R3_eta", "detected": trace_mutation["metric_map_defect_count"] > 0, "defect": trace_mutation["metric_map_defect"]},
            {"name": "omit_radial_cotangent_correction", "detected": cotangent_mutation["cotangent_lift"]["dR_coefficient_defect_count"] > 0, "fixture_value": cotangent_mutation["cotangent_lift"]["mutation_fixture_value"]},
        ],
        "activation_disposition": {
            "radial_F2_F3_certified": True,
            "temporal_F2_F3_certified": False,
            "complete_clock_canonical_map_certified": False,
            "scalar_q2_q3_transport_authorized": False,
            "detector_response_on_second_order_cone_authorized": False,
            "physical_branch_bridge_activated": False,
        },
        "flags": {
            "RADIAL_NONLINEAR_CLOCK_F2_F3_EXPORTED": True,
            "RADIAL_NONLINEAR_CLOCK_COTANGENT_LIFT_CANONICAL": True,
            "COMPLETED_UNARY_RADIAL_MAP_REPRODUCED": True,
            "TEMPORAL_NONLINEAR_CLOCK_F2_F3_EXPORTED": False,
            "COMPLETE_NONLINEAR_CLOCK_CANONICAL_MAP_EXPORTED": False,
            "SCALAR_APPARATUS_Q2_Q3_TRANSPORT_AUTHORIZED": False,
            "TANGENT_CONE_OBSERVER_RESPONSE_AUTHORIZED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "DERIVE_TEMPORAL_RELATIONAL_TIME_RETRACTION_F2_F3_AND_BV_COTANGENT_LIFT",
        "claim_boundary": boundary,
        "provenance": {"source_commit": "WORKTREE", "source_manifest": [{"path": str(path.relative_to(ROOT)), "sha256": sha256(path)} for path in SOURCE_FILES]},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    rendered = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if args.emit:
        CERTIFICATE.write_text(rendered)
    if args.check and (not CERTIFICATE.exists() or CERTIFICATE.read_text() != rendered):
        raise SystemExit("stale Berger nonlinear clock radial F2/F3 certificate")
    print("BERGER_NONLINEAR_CLOCK_RADIAL_CANONICAL_MAP_F2_F3 generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
