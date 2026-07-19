#!/usr/bin/env python3
"""Export the exact temporal Berger clock field retraction through cubic order."""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
CERTIFICATE = P / "certificates/BERGER_NONLINEAR_CLOCK_TEMPORAL_FIELD_F2_F3.json"
SCHEMA = P / "schema/berger-nonlinear-clock-temporal-field-f2-f3-v1.schema.json"
REPORT = P / "reports/berger-nonlinear-clock-temporal-field-f2-f3.md"
DEPENDENCIES = {
    "component_contract": P / "certificates/BERGER_108_ROW_COMPONENT_JET_CONTRACT.json",
    "completed_unary": P / "certificates/BERGER_108_ROW_NONLINEAR_CLOCK_SECOND_JET.json",
    "scalarization_obstruction": P / "certificates/BERGER_108_ROW_APPARATUS_Q2_Q3_SCALARIZATION_OBSTRUCTION.json",
    "radial_chart": P / "certificates/BERGER_NONLINEAR_CLOCK_RADIAL_CANONICAL_MAP_F2_F3.json",
    "linear_clock_sdr": ROOT / "d_quotient_classical/certificates/BERGER_MINIMAL_BV_CLOCK_SDR.json",
}
SOURCE_FILES = [
    Path(__file__),
    P / "verify_berger_nonlinear_clock_temporal_field_f2_f3.py",
    P / "tests/test_berger_nonlinear_clock_temporal_field_f2_f3.py",
    SCHEMA,
    REPORT,
]

PAIRS = ((0, 0), (0, 1), (0, 2), (0, 3), (1, 1), (1, 2), (1, 3), (2, 2), (2, 3), (3, 3))
METRIC_ROW = {pair: 5 + index for index, pair in enumerate(PAIRS)}
THETA_ROW = 16
ETA = {(0, 0): -1, (1, 1): 1, (2, 2): 1, (3, 3): 1}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


class TemporalJetChart:
    """Finite exact jet algebra for y0=x0+Theta(x), yi=xi.

    Every field jet has Taylor degree one.  Truncation is by total field
    degree, while derivative multiindices remain exact PBW labels.
    """

    def __init__(self, *, omit_quadratic_inverse_shift: bool = False, flip_inverse_jacobian_sign: bool = False):
        self.theta_symbols: dict[tuple[int | None, int], sp.Symbol] = {}
        self.metric_symbols: dict[tuple[tuple[int, int], int], sp.Symbol] = {}
        for spatial in (None, 1, 2, 3):
            for n0 in range(4):
                self.theta(spatial, n0)
        for pair in PAIRS:
            for n0 in range(3):
                self.metric(pair, n0)
        self.symbols = tuple(self.theta_symbols.values()) + tuple(self.metric_symbols.values())
        theta = self.theta(None, 0)
        theta_0 = self.theta(None, 1)
        theta_00 = self.theta(None, 2)
        quadratic = 0 if omit_quadratic_inverse_shift else theta * theta_0
        self.shift = self.truncate(
            -theta + quadratic - theta * theta_0**2 - sp.Rational(1, 2) * theta**2 * theta_00
        )
        self.u = self.evaluate(tuple(self.theta(None, n0) for n0 in range(1, 4)))
        self.v = {
            spatial: self.evaluate(tuple(self.theta(spatial, n0) for n0 in range(3)))
            for spatial in (1, 2, 3)
        }
        sign = 1 if flip_inverse_jacobian_sign else -1
        self.q = self.truncate(1 + sign * self.u + self.u**2 + sign * self.u**3)
        self.a = {spatial: self.truncate(-self.q * self.v[spatial]) for spatial in (1, 2, 3)}

    def theta(self, spatial: int | None, n0: int) -> sp.Symbol:
        key = (spatial, n0)
        if key not in self.theta_symbols:
            prefix = "Theta" if spatial is None else f"Theta_{spatial}"
            self.theta_symbols[key] = sp.Symbol(prefix + "_0" * n0)
        return self.theta_symbols[key]

    def metric(self, pair: tuple[int, int], n0: int) -> sp.Symbol:
        pair = tuple(sorted(pair))
        key = (pair, n0)
        if key not in self.metric_symbols:
            self.metric_symbols[key] = sp.Symbol(f"H_{pair[0]}{pair[1]}" + "_0" * n0)
        return self.metric_symbols[key]

    def truncate(self, expression: sp.Expr, maximum_degree: int = 3) -> sp.Expr:
        polynomial = sp.Poly(sp.expand(expression), *self.symbols)
        return sp.Add(*(
            coefficient * sp.prod(symbol**power for symbol, power in zip(self.symbols, monomial, strict=True))
            for monomial, coefficient in polynomial.terms()
            if sum(monomial) <= maximum_degree
        ))

    def homogeneous(self, expression: sp.Expr, degree: int) -> sp.Expr:
        polynomial = sp.Poly(self.truncate(expression), *self.symbols)
        return sp.Add(*(
            coefficient * sp.prod(symbol**power for symbol, power in zip(self.symbols, monomial, strict=True))
            for monomial, coefficient in polynomial.terms()
            if sum(monomial) == degree
        ))

    def evaluate(self, time_jets: tuple[sp.Symbol, sp.Symbol, sp.Symbol]) -> sp.Expr:
        value, first, second = time_jets
        return self.truncate(value + self.shift * first + sp.Rational(1, 2) * self.shift**2 * second)

    def raw_metric_at_inverse_point(self, i: int, j: int) -> sp.Expr:
        pair = tuple(sorted((i, j)))
        value = ETA.get(pair, 0) + self.evaluate(tuple(self.metric(pair, n0) for n0 in range(3)))
        # The certified linear temporal dressing is h_raw=H-B(Theta),
        # B_00=2 e0 Theta and B_0i=ei Theta.
        if pair == (0, 0):
            value -= 2 * self.u
        elif pair[0] == 0:
            value -= self.v[pair[1]]
        return self.truncate(value)

    def pulled_metric(self, i: int, j: int) -> sp.Expr:
        if (i, j) == (0, 0):
            return self.truncate(self.q**2 * self.raw_metric_at_inverse_point(0, 0))
        if i == 0:
            return self.truncate(
                self.q * (
                    self.raw_metric_at_inverse_point(0, j)
                    + self.a[j] * self.raw_metric_at_inverse_point(0, 0)
                )
            )
        return self.truncate(
            self.raw_metric_at_inverse_point(i, j)
            + self.a[i] * self.raw_metric_at_inverse_point(0, j)
            + self.a[j] * self.raw_metric_at_inverse_point(i, 0)
            + self.a[i] * self.a[j] * self.raw_metric_at_inverse_point(0, 0)
        )

    def metric_correction(self, pair: tuple[int, int]) -> sp.Expr:
        return self.truncate(self.pulled_metric(*pair) - ETA.get(pair, 0) - self.metric(pair, 0))

    def atom(self, symbol: sp.Symbol) -> dict[str, Any]:
        for (spatial, n0), candidate in self.theta_symbols.items():
            if symbol == candidate:
                pbw = [n0, 0, 0, 0]
                if spatial is not None:
                    pbw[spatial] = 1
                return {"row": THETA_ROW, "pbw": pbw, "label": str(symbol)}
        for (pair, n0), candidate in self.metric_symbols.items():
            if symbol == candidate:
                return {"row": METRIC_ROW[pair], "pbw": [n0, 0, 0, 0], "label": str(symbol)}
        raise AssertionError(f"unregistered symbol: {symbol}")

    def payload(self) -> dict[str, list[dict[str, Any]]]:
        result = {"F2": [], "F3": []}
        for pair in PAIRS:
            correction = self.metric_correction(pair)
            polynomial = sp.Poly(correction, *self.symbols)
            for monomial, coefficient in polynomial.terms():
                degree = sum(monomial)
                if degree not in (2, 3):
                    continue
                atoms = []
                multiplicities = []
                for symbol, power in zip(self.symbols, monomial, strict=True):
                    if power:
                        atoms.extend(self.atom(symbol) for _ in range(power))
                        multiplicities.append(power)
                atoms.sort(key=lambda item: (item["row"], item["pbw"], item["label"]))
                # For F=F1+Fn(x,...,x)/n!, one multiset component is the
                # polynomial coefficient times the product of multiplicity
                # factorials.
                component = coefficient * math.prod(math.factorial(value) for value in multiplicities)
                result[f"F{degree}"].append({
                    "output_row": METRIC_ROW[pair],
                    "output_component": f"{pair[0]}{pair[1]}",
                    "inputs": atoms,
                    "coefficient": str(component),
                })
        for key in result:
            result[key].sort(key=lambda item: (
                item["output_row"],
                tuple((atom["row"], tuple(atom["pbw"]), atom["label"]) for atom in item["inputs"]),
                item["coefficient"],
            ))
        return result

    def payload_reconstruction_audit(self, *, use_full_arity_factorial: bool = False) -> dict[str, Any]:
        """Re-expand the serialized multiset components into polynomials."""
        payload = self.payload()
        by_label = {str(symbol): symbol for symbol in self.symbols}
        reconstructed = {pair: sp.Integer(0) for pair in PAIRS}
        for degree in (2, 3):
            for entry in payload[f"F{degree}"]:
                symbols = [by_label[atom["label"]] for atom in entry["inputs"]]
                multiplicities = Counter(symbols)
                denominator = math.factorial(degree) if use_full_arity_factorial else math.prod(
                    math.factorial(value) for value in multiplicities.values()
                )
                pair = PAIRS[entry["output_row"] - 5]
                reconstructed[pair] += sp.Rational(entry["coefficient"]) * sp.prod(symbols) / denominator
        defects = {
            f"{i}{j}": sp.expand(reconstructed[(i, j)] - self.metric_correction((i, j)))
            for i, j in PAIRS
        }
        return {
            "convention": "polynomial coefficient = symmetric component / product(input multiplicity factorials)",
            "defect_component_count": sum(value != 0 for value in defects.values()),
            "defect_term_count": sum(len(sp.Add.make_args(value)) for value in defects.values() if value != 0),
        }


def phase_inverse_audit(*, omit_cubic_terms: bool = False) -> dict[str, Any]:
    theta, theta_0, theta_00, theta_000 = sp.symbols("Theta Theta_0 Theta_00 Theta_000")
    symbols = (theta, theta_0, theta_00, theta_000)
    shift = -theta + theta * theta_0
    if not omit_cubic_terms:
        shift += -theta * theta_0**2 - sp.Rational(1, 2) * theta**2 * theta_00
    z = sp.Symbol("z")
    substituted = shift + theta + shift * theta_0 + sp.Rational(1, 2) * shift**2 * theta_00 + sp.Rational(1, 6) * shift**3 * theta_000
    residual = sp.series(substituted.subs({symbol: z * symbol for symbol in symbols}), z, 0, 4).removeO().subs(z, 1).expand()
    return {
        "clock_equation": "s+Theta(y0+s,y)=0",
        "inverse_shift_through_cubic": str(sp.expand(shift)),
        "residual_through_cubic": str(residual),
        "residual_term_count": len(sp.Add.make_args(residual)) if residual != 0 else 0,
    }


def field_chart_audit(*, omit_quadratic_inverse_shift: bool = False, flip_inverse_jacobian_sign: bool = False) -> dict[str, Any]:
    chart = TemporalJetChart(
        omit_quadratic_inverse_shift=omit_quadratic_inverse_shift,
        flip_inverse_jacobian_sign=flip_inverse_jacobian_sign,
    )
    corrections = {f"{i}{j}": chart.metric_correction((i, j)) for i, j in PAIRS}
    linear = {name: chart.homogeneous(value, 1) for name, value in corrections.items()}
    counts = {
        degree: sum(len(sp.Poly(chart.homogeneous(value, degree), *chart.symbols).terms()) for value in corrections.values())
        for degree in (1, 2, 3)
    }
    return {
        "coordinate_map": "y0=x0+Theta(x), yi=xi",
        "inverse_jacobian": {
            "K00": "q=1/(1+Theta_0(x(y)))",
            "K0i": "a_i=-q Theta_i(x(y))",
            "Ki0": "0",
            "Kij": "delta_ij",
        },
        "linear_raw_metric": "g_raw=eta+H-B(Theta), B00=2 e0 Theta, B0i=ei Theta, Bij=0",
        "linear_metric_defect_count": sum(value != 0 for value in linear.values()),
        "quadratic_monomial_count": counts[2],
        "cubic_monomial_count": counts[3],
        "per_component_counts": {
            name: {
                "degree_1": len(sp.Poly(chart.homogeneous(value, 1), *chart.symbols).terms()) if linear[name] != 0 else 0,
                "degree_2": len(sp.Poly(chart.homogeneous(value, 2), *chart.symbols).terms()),
                "degree_3": len(sp.Poly(chart.homogeneous(value, 3), *chart.symbols).terms()),
            }
            for name, value in corrections.items()
        },
        "correction_expressions": {name: str(value) for name, value in corrections.items()},
    }


def build() -> dict[str, Any]:
    dependencies = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    required = {
        "component_contract": "CANONICAL_108_ROW_COMPONENT_CROSSWALK_CERTIFIED",
        "completed_unary": "COMPLETE_FIRST_BIDEGREE_UNARY_GATE",
        "scalarization_obstruction": "NONLINEAR_CLOCK_COORDINATE_JET_NONUNIQUENESS_CERTIFIED",
        "radial_chart": "RADIAL_NONLINEAR_CLOCK_COTANGENT_LIFT_CANONICAL",
        "linear_clock_sdr": "canonical_antifield_transformation_exact",
    }
    for name, flag in required.items():
        if dependencies[name].get("flags", {}).get(flag) is not True:
            raise AssertionError(f"dependency flag dropped: {name}.{flag}")

    phase = phase_inverse_audit()
    phase_mutation = phase_inverse_audit(omit_cubic_terms=True)
    chart = TemporalJetChart()
    payload = chart.payload()
    reconstruction = chart.payload_reconstruction_audit()
    factorial_mutation = chart.payload_reconstruction_audit(use_full_arity_factorial=True)
    audit = field_chart_audit()
    shift_mutation = field_chart_audit(omit_quadratic_inverse_shift=True)
    jacobian_mutation = field_chart_audit(flip_inverse_jacobian_sign=True)
    if phase["residual_term_count"] != 0 or phase_mutation["residual_term_count"] == 0:
        raise AssertionError("temporal phase inversion audit failed")
    if audit["linear_metric_defect_count"] != 0:
        raise AssertionError("linear temporal dressing was not reproduced")
    if audit["quadratic_monomial_count"] != 36 or audit["cubic_monomial_count"] != 96:
        raise AssertionError("temporal metric Taylor support changed")
    if len(payload["F2"]) != 36 or len(payload["F3"]) != 96:
        raise AssertionError("temporal factorial payload support changed")
    if reconstruction["defect_component_count"] != 0:
        raise AssertionError("temporal factorial payload does not reconstruct the field chart")
    if factorial_mutation["defect_component_count"] == 0:
        raise AssertionError("full-arity factorial mutation was not detected")
    if shift_mutation["correction_expressions"] == audit["correction_expressions"]:
        raise AssertionError("quadratic inverse-shift mutation was not detected")
    if jacobian_mutation["linear_metric_defect_count"] == 0:
        raise AssertionError("inverse-Jacobian sign mutation was not detected")

    boundary = (
        "This exact LOCAL-ALGEBRAIC certificate closes the field-coordinate half of the temporal nonlinear Berger "
        "clock chart. The physical clock condition y0=x0+Theta(x), yi=xi uniquely fixes the inverse shift through "
        "total cubic degree as s=-Theta+Theta Theta_0-Theta Theta_0^2-(Theta^2 Theta_00)/2. Substitution into "
        "s+Theta(y0+s,y)=0 has zero cubic residual; deleting the cubic terms is detected. Pulling the linearly "
        "dressed raw metric g=eta+H-B(Theta), B00=2 e0 Theta and B0i=ei Theta, through the exact inverse Jacobian "
        "cancels every linear correction and produces 36 quadratic plus 96 cubic metric-jet monomials. These are "
        "serialized as graded-symmetric F2/F3 components on metric rows 5--14 and Theta row 16 with exact ordered "
        "Berger PBW derivative labels and the factorial convention. Omitting the quadratic inverse-shift term changes "
        "the cubic field payload, and flipping the inverse-Jacobian sign destroys the linear cancellation. This field "
        "chart is not yet a BV canonical map: because it depends on derivatives of Theta and H, its signed-pairing "
        "cotangent lift requires the formal adjoint of the differential Jacobian and coefficientwise integration by "
        "parts. No temporal cotangent payload is asserted here. Consequently the combined radial-temporal canonical "
        "map, scalar apparatus q2/q3 transport, arity replay, K_Berger equivariance, observer-morphism stability, "
        "detector restriction to Z2, nonlinear rank, physical Bridge 3, finite-parameter causal and quantum claims "
        "remain fail-closed. No compact-product mode is identified with a Berger carrier row."
    )
    return {
        "schema": "closed-universe-berger-nonlinear-clock-temporal-field-f2-f3-v1",
        "result_id": "BERGER_NONLINEAR_CLOCK_TEMPORAL_FIELD_F2_F3",
        "setting_id": dependencies["completed_unary"]["setting_id"],
        "claim_status": "CERTIFIED_TEMPORAL_FIELD_F2_F3_BV_COTANGENT_OPEN",
        "atlas_status": "CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "dependency_refs": {
            name: {"path": str(path.relative_to(ROOT)), "result_id": dependencies[name]["result_id"], "sha256": sha256(path)}
            for name, path in DEPENDENCIES.items()
        },
        "phase_inverse": phase,
        "temporal_field_chart": audit,
        "taylor_payload": {
            "factorial_convention": "F=F1+F2/2!+F3/3!+...; a multiset component equals its polynomial coefficient times the factorials of input multiplicities",
            "component_rows": {"metric": list(METRIC_ROW.values()), "temporal_clock": THETA_ROW},
            "pbw_convention": "e0^n0 e1^n1 e2^n2 e3^n3; e0 commutes with the Berger spatial frame",
            "F2": payload["F2"],
            "F3": payload["F3"],
            "F2_entry_count": len(payload["F2"]),
            "F3_entry_count": len(payload["F3"]),
            "canonical_sha256": canonical_sha256(payload),
            "reconstruction_audit": reconstruction,
        },
        "mutation_results": [
            {"name": "delete_cubic_inverse_shift_terms", "detected": phase_mutation["residual_term_count"] > 0, "residual": phase_mutation["residual_through_cubic"]},
            {"name": "omit_quadratic_inverse_shift_term", "detected": shift_mutation["correction_expressions"] != audit["correction_expressions"]},
            {"name": "flip_inverse_jacobian_linear_sign", "detected": jacobian_mutation["linear_metric_defect_count"] > 0, "linear_defect_count": jacobian_mutation["linear_metric_defect_count"]},
            {"name": "replace_multiplicity_factorials_by_full_arity_factorial", "detected": factorial_mutation["defect_component_count"] > 0, "defect_component_count": factorial_mutation["defect_component_count"]},
        ],
        "activation_disposition": {
            "temporal_field_F2_F3_certified": True,
            "temporal_BV_cotangent_lift_certified": False,
            "complete_clock_canonical_map_certified": False,
            "scalar_q2_q3_transport_authorized": False,
            "detector_response_on_second_order_cone_authorized": False,
            "physical_branch_bridge_activated": False,
        },
        "flags": {
            "TEMPORAL_NONLINEAR_CLOCK_FIELD_F2_F3_EXPORTED": True,
            "TEMPORAL_CLOCK_PHASE_INVERSE_CUBIC_CERTIFIED": True,
            "LINEAR_TEMPORAL_DRESSING_REPRODUCED": True,
            "TEMPORAL_NONLINEAR_CLOCK_COTANGENT_LIFT_CANONICAL": False,
            "COMPLETE_NONLINEAR_CLOCK_CANONICAL_MAP_EXPORTED": False,
            "SCALAR_APPARATUS_Q2_Q3_TRANSPORT_AUTHORIZED": False,
            "TANGENT_CONE_OBSERVER_RESPONSE_AUTHORIZED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "DERIVE_SIGNED_PAIRING_TEMPORAL_DIFFERENTIAL_COTANGENT_LIFT_F2_F3",
        "claim_boundary": boundary,
        "provenance": {
            "source_commit": "WORKTREE",
            "source_manifest": [{"path": str(path.relative_to(ROOT)), "sha256": sha256(path)} for path in SOURCE_FILES],
        },
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
        raise SystemExit("stale Berger nonlinear clock temporal field F2/F3 certificate")
    print("BERGER_NONLINEAR_CLOCK_TEMPORAL_FIELD_F2_F3 generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
