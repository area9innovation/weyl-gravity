"""Independent verifier for arbitrary-radius axial-current conservation.

This module does not import the producer or its interpolation code.  It
independently:

* audits the localized-ring degree bound from the frozen flow, reconstruction
  row, and literal action expression;
* parses the serialized arbitrary-r current;
* differentiates it and checks all 36 rational residuals against the frozen
  repaired flow;
* checks all interpolation commitments and the independently frozen r=4
  current.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import jsonschema
import sympy as sp


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERTIFICATE = HERE / "certificate.json"
SCHEMA = HERE / "schema.json"
REPAIR = ROOT / "black_hole_programme/phase3/axial_complete_reconstruction_repair/certificate.json"
ACTION_CURRENT = ROOT / "black_hole_programme/certificates/BH2A_FLUX_MATRIX.json"
FIXED_CURRENT = ROOT / "black_hole_programme/phase3/axial_null_infinity_trace_preflight/certificate.json"


class VerificationError(RuntimeError):
    pass


def fail(message: str) -> None:
    raise VerificationError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_matrix_hash(matrix: sp.Matrix) -> str:
    payload = json.dumps(
        [[sp.sstr(sp.cancel(matrix[i, j])) for j in range(matrix.cols)]
         for i in range(matrix.rows)],
        separators=(",", ":"),
    ).encode()
    return hashlib.sha256(payload).hexdigest()


@dataclass(frozen=True)
class Bound:
    """Bound in the four-factor localized polynomial ring."""

    numerator_r: int
    numerator_omega: int
    er: int = 0
    e2: int = 0
    eg_minus: int = 0
    eg_plus: int = 0

    @property
    def denominator_r(self) -> int:
        return self.er + self.e2 + self.eg_minus + self.eg_plus

    @property
    def denominator_omega(self) -> int:
        return self.eg_minus + self.eg_plus

    def add(self, other: "Bound") -> "Bound":
        exponents = (
            max(self.er, other.er),
            max(self.e2, other.e2),
            max(self.eg_minus, other.eg_minus),
            max(self.eg_plus, other.eg_plus),
        )
        denominator_r = sum(exponents)
        denominator_omega = exponents[2] + exponents[3]
        return Bound(
            max(
                self.numerator_r + denominator_r - self.denominator_r,
                other.numerator_r + denominator_r - other.denominator_r,
            ),
            max(
                self.numerator_omega
                + denominator_omega - self.denominator_omega,
                other.numerator_omega
                + denominator_omega - other.denominator_omega,
            ),
            *exponents,
        )

    def multiply(self, other: "Bound") -> "Bound":
        return Bound(
            self.numerator_r + other.numerator_r,
            self.numerator_omega + other.numerator_omega,
            self.er + other.er,
            self.e2 + other.e2,
            self.eg_minus + other.eg_minus,
            self.eg_plus + other.eg_plus,
        )

    def radial_derivative(self) -> "Bound":
        increments = (
            int(self.er > 0),
            int(self.e2 > 0),
            int(self.eg_minus > 0),
            int(self.eg_plus > 0),
        )
        return Bound(
            max(0, self.numerator_r - 1) + sum(increments),
            self.numerator_omega + increments[2] + increments[3],
            self.er + increments[0],
            self.e2 + increments[1],
            self.eg_minus + increments[2],
            self.eg_plus + increments[3],
        )


ZERO_BOUND = Bound(0, 0)


def add_all(values: list[Bound]) -> Bound:
    result = ZERO_BOUND
    for value in values:
        result = result.add(value)
    return result


def localized_bound(expr: sp.Expr, r: sp.Symbol, omega: sp.Symbol) -> Bound:
    numerator, denominator = sp.fraction(sp.cancel(expr))
    exponents = [0, 0, 0, 0]
    factors = [
        r,
        r - 2,
        omega * r - 2 * sp.I,
        omega * r + 2 * sp.I,
    ]
    for index, factor in enumerate(factors):
        while True:
            quotient, remainder = sp.div(
                sp.Poly(denominator, r, domain="EX"),
                sp.Poly(factor, r, domain="EX"),
            )
            if not remainder.is_zero:
                break
            denominator = quotient.as_expr()
            exponents[index] += 1
    if sp.degree(denominator, r) not in (-sp.oo, 0):
        fail(f"degree audit found an undeclared radial denominator: {denominator}")
    try:
        polynomial = sp.Poly(numerator, r, omega)
    except sp.PolynomialError as exc:
        fail(f"degree audit numerator is not polynomial: {exc}")
    r_degree = polynomial.degree(r)
    omega_degree = polynomial.degree(omega)
    return Bound(
        0 if r_degree is sp.S.NegativeInfinity else max(0, int(r_degree)),
        0 if omega_degree is sp.S.NegativeInfinity else max(0, int(omega_degree)),
        *exponents,
    )


def audit_literal_current_bound() -> dict[str, int]:
    repair = json.loads(REPAIR.read_text())["complete_reconstruction"]
    r, omega = sp.symbols("r omega")
    states = sp.symbols("P Pp Q Qp H1 F")
    parse = {"r": r, "omega": omega, "I": sp.I}
    flow = sp.Matrix([
        [sp.sympify(entry, locals=parse) for entry in row]
        for row in repair["flow6"]
    ])
    h0 = sp.sympify(
        repair["H0_reconstruction"],
        locals={
            **parse,
            **dict(zip(("P", "Pp", "Q", "Qp", "H1", "F"), states)),
        },
    )
    inverse_B = localized_bound(1 / (1 - 2 / r), r, omega)

    def slot_rows(sign: int) -> dict[str, list[list[Bound]]]:
        signed_flow = flow.subs(omega, sign * omega)
        signed_h0 = h0.subs(omega, sign * omega)
        A = [[localized_bound(signed_flow[i, j], r, omega)
              for j in range(6)] for i in range(6)]
        h0_row = [
            localized_bound(sp.diff(signed_h0, state), r, omega)
            for state in states
        ]
        phase = localized_bound(
            sign * sp.I * omega / (1 - 2 / r),
            r,
            omega,
        )
        h1_row = [
            (Bound(0, 0) if index == 4 else ZERO_BOUND).add(
                inverse_B.multiply(h0_row[index])
            )
            for index in range(6)
        ]

        def differentiate(row: list[Bound]) -> list[Bound]:
            return [
                add_all(
                    [row[column].radial_derivative()]
                    + [row[q].multiply(A[q][column]) for q in range(6)]
                    + [phase.multiply(row[column])]
                )
                for column in range(6)
            ]

        def jets(row: list[Bound]) -> list[list[Bound]]:
            result = [row]
            for _ in range(3):
                result.append(differentiate(result[-1]))
            return result

        return {"h0": jets(h0_row), "h1": jets(h1_row)}

    plus_rows = slot_rows(1)
    minus_rows = slot_rows(-1)
    action = json.loads(ACTION_CURRENT.read_text())
    t, r_parse, mass, alpha = sp.symbols("t r m alpha")
    functions = {name: sp.Function(name)
                 for name in ("h0a", "h1a", "h0b", "h1b")}
    expression = sp.sympify(action["bilinear"]["F_r"], locals={
        "t": t,
        "r": r_parse,
        "m": mass,
        "alpha": alpha,
        "pi": sp.pi,
        "Derivative": sp.Derivative,
        **functions,
    }) / (sp.pi * alpha)
    expression = expression.subs(mass, 1)
    atoms = list({functions[name](t, r_parse) for name in functions})
    atoms += list(expression.atoms(sp.Derivative))
    encoded = {atom: sp.Symbol(f"jet_{index}")
               for index, atom in enumerate(atoms)}
    row_bounds: dict[sp.Symbol, tuple[str, list[Bound]]] = {}
    for atom, symbol in encoded.items():
        if isinstance(atom, sp.Derivative):
            function = atom.expr
            radial_order = sum(int(pair[1]) for pair in atom.args[1:]
                               if pair[0] == r_parse)
            time_order = sum(int(pair[1]) for pair in atom.args[1:]
                             if pair[0] == t)
        else:
            function = atom
            radial_order = time_order = 0
        name = str(function.func)
        field_name, side = name[:2], name[-1]
        rows = plus_rows if side == "a" else minus_rows
        omega_power = Bound(0, time_order)
        row_bounds[symbol] = (
            side,
            [value.multiply(omega_power)
             for value in rows[field_name][radial_order]],
        )

    K = [[ZERO_BOUND for _ in range(6)] for _ in range(6)]
    jet_symbols = set(row_bounds)
    for term in sp.Add.make_args(sp.expand(expression.xreplace(encoded))):
        present = list(term.free_symbols & jet_symbols)
        if len(present) != 2:
            fail("degree audit found a non-bilinear literal-current term")
        left, right = present
        if row_bounds[left][0] == "b":
            left, right = right, left
        coefficient = localized_bound(
            (term / (left * right)).subs(r_parse, r),
            r,
            omega,
        )
        for i in range(6):
            for j in range(6):
                K[i][j] = K[i][j].add(
                    coefficient
                    .multiply(row_bounds[left][1][i])
                    .multiply(row_bounds[right][1][j])
                )

    bounds = [entry for row in K for entry in row]
    er = max(item.er for item in bounds)
    e2 = max(item.e2 for item in bounds)
    eg_minus = max(item.eg_minus for item in bounds)
    eg_plus = max(item.eg_plus for item in bounds)
    common_r_degree = er + e2 + eg_minus + eg_plus
    return {
        "maximum_numerator_r_degree": max(
            item.numerator_r + common_r_degree - item.denominator_r
            for item in bounds
        ),
        "maximum_numerator_omega_degree": max(
            item.numerator_omega
            + eg_minus + eg_plus - item.denominator_omega
            for item in bounds
        ),
        "r": er,
        "r_minus_2": e2,
        "omega_r_minus_2I": eg_minus,
        "omega_r_plus_2I": eg_plus,
    }


def parse_current(doc: dict[str, Any]) -> tuple[sp.Matrix, sp.Symbol, sp.Symbol]:
    r, omega = sp.symbols("r omega", real=True)
    matrix = sp.Matrix([
        [sp.sympify(entry, locals={"r": r, "omega": omega, "I": sp.I})
         for entry in row]
        for row in doc["literal_current_reconstruction"]["matrix_without_pi_alpha"]
    ])
    return matrix, r, omega


def verify_document(doc: dict[str, Any], *, verify_hashes: bool = True) -> None:
    try:
        jsonschema.Draft202012Validator(json.loads(SCHEMA.read_text())).validate(doc)
    except jsonschema.ValidationError as exc:
        fail(f"schema violation: {exc.message}")

    if verify_hashes:
        for imported in doc["imports"].values():
            path = ROOT / imported["path"]
            if not path.is_file() or sha256(path) != imported["sha256"]:
                fail(f"input drift: {imported['path']}")

    audited = audit_literal_current_bound()
    reconstruction = doc["literal_current_reconstruction"]
    recorded_bound = {
        "maximum_numerator_r_degree": reconstruction["maximum_numerator_r_degree"],
        "maximum_numerator_omega_degree": reconstruction[
            "maximum_numerator_omega_degree"
        ],
        **reconstruction["denominator_exponents"],
    }
    if audited != recorded_bound:
        fail(f"localized-ring bound drift: audited={audited}, recorded={recorded_bound}")

    current, r, omega = parse_current(doc)
    denominator = (
        r**7
        * (r - 2)**6
        * (omega * r - 2 * sp.I)**4
        * (omega * r + 2 * sp.I)**4
    )
    observed = []
    for entry in current:
        cleared = sp.cancel(denominator * entry)
        try:
            polynomial = sp.Poly(cleared, r, omega)
        except sp.PolynomialError:
            fail("recorded current exceeds the declared common denominator")
        r_degree = polynomial.degree(r)
        omega_degree = polynomial.degree(omega)
        observed.append({
            "r": 0 if r_degree is sp.S.NegativeInfinity else int(r_degree),
            "omega": (
                0
                if omega_degree is sp.S.NegativeInfinity
                else int(omega_degree)
            ),
        })
    observed_matrix = [observed[index * 6:(index + 1) * 6]
                       for index in range(6)]
    if observed_matrix != reconstruction["observed_entry_numerator_degrees"]:
        fail("recorded entry degrees drift")
    if max(item["r"] for item in observed) > 29:
        fail("recorded current exceeds the radial interpolation degree")

    repair = json.loads(REPAIR.read_text())["complete_reconstruction"]
    flow = sp.Matrix([
        [sp.sympify(entry, locals={"r": r, "omega": omega, "I": sp.I})
         for entry in row]
        for row in repair["flow6"]
    ])
    residual = current.diff(r) + flow.subs(omega, -omega).T * current + current * flow
    failures = [
        (i, j) for i in range(6) for j in range(6)
        if sp.cancel(residual[i, j]) != 0
    ]
    if failures:
        fail(f"arbitrary-radius conservation residual nonzero: {failures[:3]}")

    if any(sp.cancel((current + current.conjugate().T)[i, j]) != 0
           for i in range(6) for j in range(6)):
        fail("arbitrary-radius current lost anti-Hermiticity")

    fixed_payload = json.loads(FIXED_CURRENT.read_text())
    fixed = sp.Matrix([
        [sp.sympify(entry, locals={"omega": omega, "I": sp.I}) for entry in row]
        for row in fixed_payload["exact_radial_current"]["matrix_without_pi_alpha"]
    ])
    if any(sp.cancel((current.subs(r, 4) - fixed)[i, j]) != 0
           for i in range(6) for j in range(6)):
        fail("arbitrary-radius current disagrees with the frozen r=4 current")

    samples = reconstruction["sample_radii"]
    radii = [item["radius"] for item in samples]
    if len(set(radii)) != 30 or radii != list(range(3, 33)):
        fail("interpolation nodes are not the canonical 30 distinct radii")
    for sample in samples:
        matrix_hash = canonical_matrix_hash(current.subs(r, sample["radius"]))
        if matrix_hash != sample["literal_matrix_sha256"]:
            fail(f"sample commitment drift at r={sample['radius']}")

    flags = doc["claim_flags"]
    if not flags["literal_action_current_reconstructed_for_arbitrary_r"]:
        fail("literal-current reconstruction flag is not certified")
    if not flags["repaired_six_state_current_conservation_certified"]:
        fail("conservation flag is not certified")
    if any(flags[name] for name in (
        "global_connection_constructed",
        "endpoint_flux_limits_certified",
        "scattering_or_stability_certified",
    )):
        fail("certificate promotes a claim beyond current conservation")
    limitations = " ".join(doc["does_not_establish"]).lower()
    for required in ("horizon", "endpoint", "connection", "stability"):
        if required not in limitations:
            fail(f"missing limitation: {required}")


def replay_literal_samples(doc: dict[str, Any]) -> None:
    # This is an exhaustive producer-provenance replay, intentionally separate
    # from the independent identity verifier above.
    from black_hole_programme.phase3.axial_null_infinity_trace_preflight.current_dag import (
        derive_rational_radius_current,
    )

    samples = doc["literal_current_reconstruction"]["sample_radii"]
    for sample in samples:
        current = derive_rational_radius_current(sp.Integer(sample["radius"]))
        if canonical_matrix_hash(current) != sample["literal_matrix_sha256"]:
            fail(f"literal action replay drift at r={sample['radius']}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--replay-literal-samples", action="store_true")
    args = parser.parse_args()
    document = json.loads(CERTIFICATE.read_text())
    verify_document(document)
    if args.replay_literal_samples:
        replay_literal_samples(document)
    print("PASS: independent exact arbitrary-radius current conservation verification")


if __name__ == "__main__":
    main()
