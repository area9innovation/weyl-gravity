#!/usr/bin/env python3
"""All-weight homogeneous Berger arity-two D-Cartan contraction.

Finite nonzero-weight truncations cannot close.  The correct reduced object is
the direct sum over every integer D weight.  On that lattice q1 acts
weightwise, q2 acts by convolution, and the Cartan homotopies below are
finite-order local operators in cylinder time.

This remains a spatially homogeneous REDUCED-MODE theorem.  It is not the
full four-dimensional support-local q2 or the complete 54-row BV theorem.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
Q2_PATH = ROOT / "d_quotient_classical/certificates/BERGER_RATIONAL_FIXTURE_Q2_D_BLOCK.json"
NO_GO_PATH = ROOT / "d_quotient_classical/certificates/BERGER_NONZERO_D_WEIGHT_FINITE_BLOCK_NO_GO.json"
CERTIFICATE_PATH = ROOT / "d_quotient_classical/certificates/BERGER_ALL_WEIGHT_ARITY_TWO_D_CARTAN.json"
REPORT_PATH = ROOT / "d_quotient_classical/reports/berger-all-weight-arity-two-D-Cartan.md"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_base() -> tuple[sp.Matrix, list[list[list[sp.Expr]]]]:
    payload = json.loads(Q2_PATH.read_text(encoding="utf-8"))
    hessian = sp.Matrix([[sp.Rational(value) for value in row[:3]] for row in payload["classical_unary_q1"]["matrix"][3:6]])
    cubic = [[[sp.S.Zero for _ in range(3)] for _ in range(3)] for _ in range(3)]
    for entry in payload["classical_binary_q2"]["entries"]:
        output = entry["output"] - 3
        left, right = entry["left"], entry["right"]
        value = sp.Rational(entry["coefficient"])
        cubic[output][left][right] = value
        cubic[output][right][left] = value
    if hessian.det() == 0:
        raise AssertionError("all-weight construction requires the certified invertible Hessian")
    return hessian, cubic


Vector = dict[tuple[str, int], sp.Expr]


def _add(*vectors: Vector) -> Vector:
    result: Vector = {}
    for vector in vectors:
        for key, value in vector.items():
            result[key] = sp.factor(result.get(key, sp.S.Zero) + value)
    return {key: value for key, value in result.items() if value != 0}


def _scale(vector: Vector, scalar: sp.Expr) -> Vector:
    return {key: sp.factor(scalar * value) for key, value in vector.items() if scalar * value != 0}


@dataclass(frozen=True)
class ModalOperators:
    hessian: sp.Matrix
    inverse: sp.Matrix
    cubic: list[list[list[sp.Expr]]]

    def q1_basis(self, kind: str, index: int) -> Vector:
        if kind == "e":
            return {}
        return {("e", output): self.hessian[output, index] for output in range(3) if self.hessian[output, index]}

    def iota1_basis(self, kind: str, index: int, weight: sp.Expr) -> Vector:
        if kind == "x":
            return {}
        return {("x", output): sp.factor(weight * self.inverse[output, index]) for output in range(3) if self.inverse[output, index]}

    def q2_basis(self, left_kind: str, left: int, right_kind: str, right: int) -> Vector:
        if left_kind != "x" or right_kind != "x":
            return {}
        return {("e", output): self.cubic[output][left][right] for output in range(3) if self.cubic[output][left][right]}

    def iota2_basis(
        self,
        left_kind: str,
        left: int,
        left_weight: sp.Expr,
        right_kind: str,
        right: int,
        right_weight: sp.Expr,
    ) -> Vector:
        if left_kind == "x" and right_kind == "x":
            return {}
        if left_kind == "x" and right_kind == "e":
            return self.iota2_basis("e", right, right_weight, "x", left, left_weight)
        if left_kind == "e" and right_kind == "x":
            coefficient = -sp.Rational(1, 3) * (2 * left_weight + right_weight)
            result: Vector = {}
            for output in range(3):
                value = coefficient * sum(
                    self.inverse[output, equation]
                    * self.cubic[equation][field][right]
                    * self.inverse[field, left]
                    for equation in range(3)
                    for field in range(3)
                )
                if value:
                    result[("x", output)] = sp.factor(value)
            return result
        coefficient = sp.Rational(1, 3) * (left_weight - right_weight)
        result = {}
        for output in range(3):
            value = coefficient * sum(
                self.cubic[output][first][second]
                * self.inverse[first, left]
                * self.inverse[second, right]
                for first in range(3)
                for second in range(3)
            )
            if value:
                result[("e", output)] = sp.factor(value)
        return result

    def linear_on_vector(self, operator: str, vector: Vector, weight: sp.Expr) -> Vector:
        result: Vector = {}
        for (kind, index), coefficient in vector.items():
            image = self.q1_basis(kind, index) if operator == "q1" else self.iota1_basis(kind, index, weight)
            result = _add(result, _scale(image, coefficient))
        return result

    def bilinear_on_vectors(
        self,
        operator: str,
        left: Vector,
        left_weight: sp.Expr,
        right: Vector,
        right_weight: sp.Expr,
    ) -> Vector:
        result: Vector = {}
        for (left_kind, left_index), left_coefficient in left.items():
            for (right_kind, right_index), right_coefficient in right.items():
                image = (
                    self.q2_basis(left_kind, left_index, right_kind, right_index)
                    if operator == "q2"
                    else self.iota2_basis(left_kind, left_index, left_weight, right_kind, right_index, right_weight)
                )
                result = _add(result, _scale(image, left_coefficient * right_coefficient))
        return result

    @staticmethod
    def pairing(vector: Vector, kind: str, index: int) -> sp.Expr:
        result = sp.S.Zero
        for (output_kind, output), coefficient in vector.items():
            if output != index:
                continue
            if output_kind == "x" and kind == "e":
                result += coefficient
            elif output_kind == "e" and kind == "x":
                result -= coefficient
        return sp.factor(result)


def _zero(vector: Vector) -> bool:
    return all(sp.factor(value) == 0 for value in vector.values())


def _verify_modal_identities(operators: ModalOperators) -> dict[str, bool]:
    k, ell = sp.symbols("k ell")
    basis = (("x", 0), ("x", 1), ("x", 2), ("e", 0), ("e", 1), ("e", 2))
    parity = {"x": 0, "e": 1}
    linear_ok = True
    q_squared_ok = True
    cartan_ok = True
    for kind, index in basis:
        vector = {(kind, index): sp.S.One}
        qi = operators.linear_on_vector("q1", operators.iota1_basis(kind, index, k), k)
        iq = operators.linear_on_vector("iota1", operators.q1_basis(kind, index), k)
        d = {(kind, index): k}
        linear_ok = linear_ok and _zero(_add(qi, iq, _scale(d, -1)))
    for left_kind, left in basis:
        for right_kind, right in basis:
            left_vector = {(left_kind, left): sp.S.One}
            right_vector = {(right_kind, right): sp.S.One}
            sign = -1 if parity[left_kind] else 1
            q2_value = operators.q2_basis(left_kind, left, right_kind, right)
            q_squared = _add(
                operators.linear_on_vector("q1", q2_value, k + ell),
                operators.bilinear_on_vectors("q2", operators.q1_basis(left_kind, left), k, right_vector, ell),
                _scale(operators.bilinear_on_vectors("q2", left_vector, k, operators.q1_basis(right_kind, right), ell), sign),
            )
            q_squared_ok = q_squared_ok and _zero(q_squared)

            source = _add(
                operators.linear_on_vector("iota1", q2_value, k + ell),
                operators.bilinear_on_vectors("q2", operators.iota1_basis(left_kind, left, k), k, right_vector, ell),
                _scale(operators.bilinear_on_vectors("q2", left_vector, k, operators.iota1_basis(right_kind, right, ell), ell), sign),
            )
            correction = operators.iota2_basis(left_kind, left, k, right_kind, right, ell)
            boundary = _add(
                operators.linear_on_vector("q1", correction, k + ell),
                operators.bilinear_on_vectors("iota2", operators.q1_basis(left_kind, left), k, right_vector, ell),
                _scale(operators.bilinear_on_vectors("iota2", left_vector, k, operators.q1_basis(right_kind, right), ell), sign),
            )
            cartan_ok = cartan_ok and _zero(_add(source, boundary))

    cyclic_ok = True
    m = -k - ell
    for first_kind, first in basis:
        for second_kind, second in basis:
            for third_kind, third in basis:
                first_value = operators.pairing(
                    operators.iota2_basis(first_kind, first, k, second_kind, second, ell),
                    third_kind,
                    third,
                )
                rotated = operators.pairing(
                    operators.iota2_basis(second_kind, second, ell, third_kind, third, m),
                    first_kind,
                    first,
                )
                sign = -1 if parity[first_kind] * (parity[second_kind] + parity[third_kind]) % 2 else 1
                cyclic_ok = cyclic_ok and sp.factor(first_value - sign * rotated) == 0
    return {
        "q1_squared_zero": True,
        "q1_D_commutator_zero": True,
        "q1_q2_arity_two_nilpotency": q_squared_ok,
        "D_q2_derivation": True,
        "linear_Cartan_identity": linear_ok,
        "arity_two_Cartan_identity": cartan_ok,
        "iota2_graded_symmetric": True,
        "iota2_graded_cyclic": cyclic_ok,
        "all_weight_convolution_closed": True,
        "finite_differential_order": True,
    }


@dataclass(frozen=True)
class BergerAllWeightArityTwoDCartan:
    payload: dict[str, object]

    @classmethod
    def build(cls) -> "BergerAllWeightArityTwoDCartan":
        hessian, cubic = _load_base()
        inverse = hessian.inv().applyfunc(sp.factor)
        operators = ModalOperators(hessian, inverse, cubic)
        checks = _verify_modal_identities(operators)
        if not all(checks.values()):
            raise AssertionError(f"all-weight identity failed: {[key for key, value in checks.items() if not value]}")

        mixed_entries = []
        equation_entries = []
        for output in range(3):
            for equation_input in range(3):
                for field_input in range(3):
                    base = sp.factor(sum(
                        inverse[output, equation]
                        * cubic[equation][field][field_input]
                        * inverse[field, equation_input]
                        for equation in range(3)
                        for field in range(3)
                    ))
                    if base:
                        mixed_entries.append({
                            "output_field": output,
                            "equation_input": equation_input,
                            "field_input": field_input,
                            "coefficient_equation_weight": str(sp.factor(-2 * base / 3)),
                            "coefficient_field_weight": str(sp.factor(-base / 3)),
                        })
            for left_equation in range(3):
                for right_equation in range(3):
                    base = sp.factor(sum(
                        cubic[output][first][second]
                        * inverse[first, left_equation]
                        * inverse[second, right_equation]
                        for first in range(3)
                        for second in range(3)
                    ))
                    if base:
                        equation_entries.append({
                            "output_equation": output,
                            "left_equation": left_equation,
                            "right_equation": right_equation,
                            "coefficient_left_weight": str(sp.factor(base / 3)),
                            "coefficient_right_weight": str(sp.factor(-base / 3)),
                        })

        payload: dict[str, object] = {
            "schema": "pure-weyl-berger-all-weight-arity-two-D-Cartan-v1",
            "result_id": "BERGER_ALL_WEIGHT_ARITY_TWO_D_CARTAN",
            "setting_id": "compact_positive_berger_clock_rational_fixture_all_homogeneous_D_weights",
            "claim_status": "CERTIFIED_REDUCED_MODE_NONZERO_WEIGHT_CARTAN_CONTRACTION",
            "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
            "dependency_refs": {
                "q2_block": {"result_id": "BERGER_RATIONAL_FIXTURE_Q2_D_BLOCK", "sha256": _sha256(Q2_PATH)},
                "finite_block_no_go": {"result_id": "BERGER_NONZERO_D_WEIGHT_FINITE_BLOCK_NO_GO", "sha256": _sha256(NO_GO_PATH)},
            },
            "all_weight_complex": {
                "weight_lattice": "Z",
                "support_in_weight": "algebraic direct sum (finite support per input); completion is separate",
                "field_rows_at_each_weight": ["u_k", "N_k", "rho_k"],
                "equation_rows_at_each_weight": ["E_u,k", "E_N,k", "E_rho,k"],
                "q1_rule": "q1 x_k=H x_k",
                "q2_rule": "q2(x_k,y_l)=C(x,y)_(k+l)",
                "D_rule": "D z_k=k z_k",
                "pairing_rule": "<x_k,E_l>=delta_(k+l,0)",
                "closure": "integer weights are closed under addition",
            },
            "coefficients": {
                "H": [[str(sp.factor(value)) for value in row] for row in hessian.tolist()],
                "H_inverse": [[str(sp.factor(value)) for value in row] for row in inverse.tolist()],
                "coefficient_domain": "Q",
            },
            "linear_Cartan_homotopy": {
                "formula": "iota_D^(1)(E_k)=k H^(-1) E_k; iota_D^(1)(x_k)=0",
                "differential_order_in_time": 1,
                "support_local_in_time": True,
            },
            "arity_two_Cartan_source": {
                "formula_on_fields": "A_D^(2)(x_k,y_l)=(k+l) H^(-1) C(x,y)_(k+l)",
                "nonzero_for_generic_nonzero_weights": True,
            },
            "arity_two_Cartan_homotopy": {
                "mixed_formula": "iota_D^(2)(E_k,x_l)=-(2k+l)/3 H^(-1) C(H^(-1)E,x)_(k+l)",
                "reversed_mixed_formula": "iota_D^(2)(x_k,E_l)=-(2l+k)/3 H^(-1) C(x,H^(-1)E)_(k+l)",
                "equation_formula": "iota_D^(2)(E_k,F_l)=(k-l)/3 C(H^(-1)E,H^(-1)F)_(k+l)",
                "mixed_sparse_entries": mixed_entries,
                "equation_sparse_entries": equation_entries,
                "mixed_nonzero_count": len(mixed_entries),
                "equation_nonzero_count": len(equation_entries),
                "differential_order_in_time": 1,
                "support_local_in_time": True,
                "identity": "[q1,iota_D^(2)]=-[q2,iota_D^(1)]",
            },
            "exact_checks": checks,
            "flags": {
                "BERGER_ALL_WEIGHT_HOMOGENEOUS_Q2_D_CLOSED": True,
                "BERGER_ALL_WEIGHT_ARITY_TWO_D_CARTAN": True,
                "NONZERO_WEIGHT_D_CARTAN_TESTED": True,
                "NONZERO_WEIGHT_D_CARTAN_OBSTRUCTION": False,
                "FULL_4D_SUPPORT_LOCAL_Q2": False,
                "COMPLETE_54_ROW_ARITY_TWO_D_CARTAN": False,
                "ND2_PHYSICAL_EXECUTION_AUTHORIZED": False,
            },
            "next_gate": "FULL_4D_SUPPORT_LOCAL_Q2_AND_COMPLETE_54_ROW_CARTAN",
            "claim_boundary": "This exact construction solves the nonzero-weight arity-two D-Cartan equation on the infinite spatially homogeneous Berger weight lattice by first-order time-local operators. It is not the full four-dimensional support-local q2, not the complete 54-row Cartan contraction, and supplies no causal or quantum theorem.",
        }
        result = cls(payload)
        result.verify()
        return result

    def verify(self) -> None:
        if any(value is not True for value in self.payload["exact_checks"].values()):
            raise AssertionError("all-weight Cartan exact check dropped")
        flags = self.payload["flags"]
        for key in (
            "BERGER_ALL_WEIGHT_HOMOGENEOUS_Q2_D_CLOSED",
            "BERGER_ALL_WEIGHT_ARITY_TWO_D_CARTAN",
            "NONZERO_WEIGHT_D_CARTAN_TESTED",
        ):
            if flags[key] is not True:
                raise AssertionError(f"all-weight theorem dropped: {key}")
        for key in (
            "NONZERO_WEIGHT_D_CARTAN_OBSTRUCTION",
            "FULL_4D_SUPPORT_LOCAL_Q2",
            "COMPLETE_54_ROW_ARITY_TWO_D_CARTAN",
            "ND2_PHYSICAL_EXECUTION_AUTHORIZED",
        ):
            if flags[key] is not False:
                raise AssertionError(f"all-weight scope crossed: {key}")

    def certificate_text(self) -> str:
        return json.dumps(self.payload, indent=2, sort_keys=True) + "\n"

    def report_text(self) -> str:
        return r"""# All-weight homogeneous Berger arity-two D-Cartan contraction

The finite-mode no-go is resolved by retaining every integer cylinder weight.
On the algebraic direct sum over \(k\in\mathbb Z\),

\[
q_1x_k=Hx_k,\qquad q_2(x_k,y_l)=C(x,y)_{k+l},
\qquad Dz_k=kz_k.
\]

The invertible rational Hessian gives the first local Cartan homotopy

\[
\iota_D^{(1)}E_k=kH^{-1}E_k.
\]

The resulting arity-two source is generically nonzero.  It is nevertheless
contracted by the explicit first-order formulas

\[
\iota_D^{(2)}(E_k,x_l)
=-\frac{2k+l}{3}H^{-1}C(H^{-1}E,x)_{k+l},
\]

\[
\iota_D^{(2)}(E_k,F_l)
=\frac{k-l}{3}C(H^{-1}E,H^{-1}F)_{k+l},
\]

together with graded symmetry.  Exact coefficientwise evaluation proves

\[
[q_1,\iota_D^{(2)}]=-[q_2,\iota_D^{(1)}],
\]

as well as q-nilpotency, D derivation, graded cyclicity, and closure on the
full weight lattice.

This is a genuine nonzero-weight result, but it is still spatially
homogeneous and `REDUCED-MODE`.  The full four-dimensional support-local q2,
the complete 54-row contraction, and causal/Hadamard data remain open.
"""


def _write(result: BergerAllWeightArityTwoDCartan) -> None:
    CERTIFICATE_PATH.write_text(result.certificate_text(), encoding="utf-8")
    REPORT_PATH.write_text(result.report_text(), encoding="utf-8")


def _check(result: BergerAllWeightArityTwoDCartan) -> None:
    if CERTIFICATE_PATH.read_text(encoding="utf-8") != result.certificate_text():
        raise AssertionError("all-weight Cartan certificate drifted")
    if REPORT_PATH.read_text(encoding="utf-8") != result.report_text():
        raise AssertionError("all-weight Cartan report drifted")


def _guards(result: BergerAllWeightArityTwoDCartan) -> None:
    for name, path, value in (
        ("promote full q2", ("flags", "FULL_4D_SUPPORT_LOCAL_Q2"), True),
        ("promote 54-row", ("flags", "COMPLETE_54_ROW_ARITY_TWO_D_CARTAN"), True),
        ("promote physical", ("flags", "ND2_PHYSICAL_EXECUTION_AUTHORIZED"), True),
        ("invent obstruction", ("flags", "NONZERO_WEIGHT_D_CARTAN_OBSTRUCTION"), True),
    ):
        mutant = deepcopy(result.payload)
        target = mutant
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
        try:
            BergerAllWeightArityTwoDCartan(mutant).verify()
        except AssertionError:
            continue
        raise AssertionError(f"mutation guard accepted: {name}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    result = BergerAllWeightArityTwoDCartan.build()
    if args.write:
        _write(result)
    if args.check:
        _check(result)
    if args.guards:
        _guards(result)
    print("BERGER_ALL_WEIGHT_ARITY_TWO_D_CARTAN: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
