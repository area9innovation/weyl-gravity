#!/usr/bin/env python3
"""Action-derived stationary Berger q2/D block for immediate ND2 ingestion.

This is deliberately a ``REDUCED-MODE`` artifact.  It restricts the exact
homogeneous Berger action to the stationary D-weight-zero variations
``(delta c, delta N, delta rho)`` at the rational fixture.  The Hessian is
the six-row unary Koszul--Tate block and the third action derivative is its
arity-two Taylor coefficient.  It is not the complete support-local q2.
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
BACKGROUND = ROOT / "d_quotient_classical/certificates/POSITIVE_BERGER_CLOCK_BACKGROUND.json"
UNARY = ROOT / "d_quotient_classical/certificates/BERGER_GAUGE_FIXED_NONMINIMAL_COMPLETION.json"
CERTIFICATE_PATH = ROOT / "d_quotient_classical/certificates/BERGER_RATIONAL_FIXTURE_Q2_D_BLOCK.json"
REPORT_PATH = ROOT / "d_quotient_classical/reports/berger-rational-fixture-q2-d-block.md"
SCHEMA_PATH = ROOT / "d_quotient_classical/schema/berger-rational-fixture-q2-d-block-v1.schema.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _matrix_rows(matrix: sp.MatrixBase) -> list[list[str]]:
    return [[str(sp.factor(matrix[row, column])) for column in range(matrix.cols)] for row in range(matrix.rows)]


def _exact_data() -> dict[str, object]:
    c, lapse, rho, omega = sp.symbols("c N rho omega", positive=True, real=True)
    alpha_b = sp.Rational(5)
    quartic = sp.Rational(119, 480)
    scalar_curvature = (4 - c**2) / 2
    weyl_squared = 4 * (1 - c**2) ** 2 / 3
    reduced_lagrangian = sp.factor(
        lapse * c * (
            alpha_b * weyl_squared / 8
            + rho**2 * omega**2 / (2 * lapse**2)
            - scalar_curvature * rho**2 / 12
            - quartic * rho**4 / 4
        )
    )
    fields = (c, lapse, rho)
    fixture = {
        c: 3 * sp.sqrt(10) / 20,
        lapse: 1,
        rho: 1,
        omega: sp.Rational(3, 4),
    }
    gradient = sp.Matrix([sp.factor(sp.diff(reduced_lagrangian, field).subs(fixture)) for field in fields])
    if gradient != sp.zeros(3, 1):
        raise AssertionError("rational fixture is not stationary in the declared block")
    hessian = sp.Matrix(3, 3, lambda row, column: sp.factor(sp.diff(reduced_lagrangian, fields[row], fields[column]).subs(fixture)))
    cubic = [[[sp.factor(sp.diff(reduced_lagrangian, fields[out], fields[left], fields[right]).subs(fixture)) for right in range(3)] for left in range(3)] for out in range(3)]
    if hessian != hessian.T or any(cubic[a][b][d] != cubic[d][b][a] for a in range(3) for b in range(3) for d in range(3)):
        raise AssertionError("action derivatives lost symmetry")
    if hessian.det() == 0:
        raise AssertionError("stationary fixture Hessian is degenerate")

    q1 = sp.zeros(6)
    q1[3:6, 0:3] = hessian
    pairing = sp.zeros(6)
    pairing[0:3, 3:6] = sp.eye(3)
    pairing[3:6, 0:3] = -sp.eye(3)
    d_action = sp.zeros(6)
    if q1 * q1 != sp.zeros(6):
        raise AssertionError("fixture q1 is not nilpotent")
    if q1.T * pairing + pairing * q1 != sp.zeros(6):
        raise AssertionError("fixture q1 is not cyclic")
    if q1 * d_action - d_action * q1 != sp.zeros(6):
        raise AssertionError("fixture D action does not commute with q1")

    q2 = [[[sp.S.Zero for _ in range(6)] for _ in range(6)] for _ in range(6)]
    for output in range(3):
        for left in range(3):
            for right in range(3):
                q2[3 + output][left][right] = cubic[output][left][right]

    # With q2 supported only on two field inputs and one equation output,
    # every arity-two q^2 term vanishes coefficientwise.  Check rather than
    # rely on that description.
    for output in range(6):
        for left in range(6):
            for right in range(6):
                defect = sum(q1[output, middle] * q2[middle][left][right] for middle in range(6))
                defect += sum(q2[output][middle][right] * q1[middle, left] for middle in range(6))
                defect += sum(q2[output][left][middle] * q1[middle, right] for middle in range(6))
                if sp.factor(defect) != 0:
                    raise AssertionError(f"arity-two nilpotency failed at {(output, left, right)}")

    # The action trilinear C(a,b,c)=<q2(a,b),c> is the negative of the
    # symmetric third derivative on field inputs.
    cyclic_tensor = [[[sp.S.Zero for _ in range(6)] for _ in range(6)] for _ in range(6)]
    for left in range(6):
        for right in range(6):
            for third in range(6):
                cyclic_tensor[left][right][third] = sp.factor(sum(pairing[output, third] * q2[output][left][right] for output in range(6)))
    for a in range(3):
        for b in range(3):
            for d in range(3):
                if cyclic_tensor[a][b][d] != cyclic_tensor[b][d][a] or cyclic_tensor[a][b][d] != cyclic_tensor[b][a][d]:
                    raise AssertionError("fixture q2 cyclic tensor is not symmetric")

    q2_entries = []
    for output in range(6):
        for left in range(6):
            for right in range(left, 6):
                if q2[output][left][right] != 0:
                    q2_entries.append({"output": output, "left": left, "right": right, "coefficient": str(q2[output][left][right])})
    return {
        "lagrangian": reduced_lagrangian,
        "gradient": gradient,
        "hessian": hessian,
        "cubic": cubic,
        "q1": q1,
        "q2_entries": q2_entries,
        "pairing": pairing,
        "d_action": d_action,
    }


@dataclass(frozen=True)
class BergerRationalFixtureQ2DBlock:
    payload: dict[str, object]

    @classmethod
    def build(cls) -> "BergerRationalFixtureQ2DBlock":
        data = _exact_data()
        rows = [
            {"index": 0, "row_id": "delta_c_w0", "degree": 0, "parity": 0, "D_weight": 0, "role": "field"},
            {"index": 1, "row_id": "delta_N_w0", "degree": 0, "parity": 0, "D_weight": 0, "role": "field"},
            {"index": 2, "row_id": "delta_rho_w0", "degree": 0, "parity": 0, "D_weight": 0, "role": "field"},
            {"index": 3, "row_id": "E_c_w0", "degree": 1, "parity": 1, "D_weight": 0, "role": "equation"},
            {"index": 4, "row_id": "E_N_w0", "degree": 1, "parity": 1, "D_weight": 0, "role": "equation"},
            {"index": 5, "row_id": "E_rho_w0", "degree": 1, "parity": 1, "D_weight": 0, "role": "equation"},
        ]
        payload: dict[str, object] = {
            "schema": "pure-weyl-berger-rational-fixture-q2-d-block-v1",
            "result_id": "BERGER_RATIONAL_FIXTURE_Q2_D_BLOCK",
            "setting_id": "compact_positive_berger_clock_rational_fixture_stationary_homogeneous",
            "claim_status": "CERTIFIED_REDUCED_MODE_Q2_D_BLOCK",
            "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
            "dependency_refs": {
                "background": {"result_id": "POSITIVE_BERGER_CLOCK_BACKGROUND", "sha256": _sha256(BACKGROUND)},
                "complete_unary": {"result_id": "BERGER_GAUGE_FIXED_NONMINIMAL_COMPLETION", "sha256": _sha256(UNARY)},
            },
            "scope": {
                "category": "stationary SU(2)_L x U(1)_R homogeneous D-weight-zero block",
                "not_support_local_q2": True,
                "spatial_mode": "homogeneous invariant",
                "D_weights": [0],
                "closure": "all q1 and q2 outputs remain in the six declared rows",
                "limitation": "D acts trivially on this centered block; this tests exact ingestion and BV identities, not a nonzero-weight D obstruction",
            },
            "action_derivation": {
                "authoritative_restriction": "S/(16pi^2)=int dt N c{alpha_B C^2/8+rho^2 omega^2/(2N^2)-R rho^2/12-lambda rho^4/4}",
                "reduced_lagrangian": str(data["lagrangian"]),
                "variables": ["c", "N", "rho"],
                "held_fixed": {"alpha_B": "5", "lambda": "119/480", "omega": "3/4"},
                "background": {"c": "3*sqrt(10)/20", "N": "1", "rho": "1", "q": "9/40"},
                "stationary_gradient": [str(value) for value in data["gradient"]],
                "q1_rule": "H_ij=d_i d_j L at the fixture",
                "q2_rule": "C_ijk=d_i d_j d_k L at the fixture in q=q1+q2/2+... convention",
                "residual_fit_used": False,
            },
            "row_layout": rows,
            "classical_unary_q1": {"matrix": _matrix_rows(data["q1"]), "degree": 1, "rank": int(data["q1"].rank())},
            "classical_binary_q2": {"degree": 1, "graded_symmetric": True, "entries": data["q2_entries"]},
            "D_action_cl": {"matrix": _matrix_rows(data["d_action"]), "degree": 0, "weight_rule": "D x=w(x)x", "weights": [0, 0, 0, 0, 0, 0]},
            "cyclic_pairing": {"matrix": _matrix_rows(data["pairing"]), "rank": int(data["pairing"].rank()), "convention": "<field_i,equation_j>=delta_ij; reverse block=-delta_ij"},
            "exact_checks": {
                "action_stationary_on_fixture": True,
                "q1_squared_zero": True,
                "q1_D_commutator_zero": True,
                "q1_q2_arity_two_nilpotency": True,
                "q2_cyclic": True,
                "pairing_nondegenerate": True,
                "D_weight_conservation": True,
                "declared_mode_block_closed": True,
                "all_coefficients_exact_Q_sqrt10": True,
            },
            "flags": {
                "BERGER_RATIONAL_FIXTURE_Q2_D_BLOCK": True,
                "CLASSICAL_REDUCED_MODE_Q2_D": True,
                "CLASSICAL_SUPPORT_LOCAL_Q2": False,
                "BERGER_LOCAL_D_ACTION_EQUIVARIANT": False,
                "CLASSICAL_SUPPORT_LOCAL_Q1_Q2_EXPORT": False,
                "ND2_PHYSICAL_EXECUTION_AUTHORIZED": False,
            },
            "next_gate": "ND2_REDUCED_MODE_FIXTURE_IMPORT",
            "claim_boundary": "This exact action-derived six-row stationary homogeneous fixture supplies a nonzero q2, the centered local D action, cyclic pairing, weights, and an admissible closed REDUCED-MODE block. It is not the complete support-local q2, its D action is zero because every retained row has weight zero, and it authorizes no physical ND2 or quantum conclusion.",
        }
        result = cls(payload)
        result.verify()
        return result

    def verify(self) -> None:
        if any(value is not True for value in self.payload["exact_checks"].values()):
            raise AssertionError("rational q2/D exact check dropped")
        if self.payload["scope"]["not_support_local_q2"] is not True:
            raise AssertionError("reduced fixture was presented as support-local q2")
        flags = self.payload["flags"]
        if flags["BERGER_RATIONAL_FIXTURE_Q2_D_BLOCK"] is not True or flags["CLASSICAL_REDUCED_MODE_Q2_D"] is not True:
            raise AssertionError("reduced q2/D theorem dropped")
        for key in ("CLASSICAL_SUPPORT_LOCAL_Q2", "BERGER_LOCAL_D_ACTION_EQUIVARIANT", "CLASSICAL_SUPPORT_LOCAL_Q1_Q2_EXPORT", "ND2_PHYSICAL_EXECUTION_AUTHORIZED"):
            if flags[key] is not False:
                raise AssertionError(f"reduced fixture crossed full gate: {key}")
        if self.payload["next_gate"] != "ND2_REDUCED_MODE_FIXTURE_IMPORT":
            raise AssertionError("rational q2/D next gate drifted")

    def certificate_text(self) -> str:
        return json.dumps(self.payload, indent=2, sort_keys=True) + "\n"

    def report_text(self) -> str:
        return r"""# Rational Berger fixture q2/D block

The exact homogeneous reduced action is restricted to stationary variations
of ((c,N,\rho)) at

\[
q=\frac9{40},\quad \alpha_B=5,\quad
\lambda=\frac{119}{480},\quad \omega=\frac34.
\]

Its Hessian and third derivative give a six-row Koszul--Tate block and a
nonzero exact (q_2). The canonical field--equation pairing makes the cubic
tensor cyclic. Every row has (D)-weight zero, so the block is closed and
the (D)-derivation identities hold exactly.

This is an immediately ingestible `REDUCED-MODE` identity fixture. It is not
the full support-local (q_2), and because (D) acts trivially it does not
test a nonzero-weight Cartan obstruction.
"""


def _write(result: BergerRationalFixtureQ2DBlock) -> None:
    CERTIFICATE_PATH.write_text(result.certificate_text())
    REPORT_PATH.write_text(result.report_text())


def _check(result: BergerRationalFixtureQ2DBlock) -> None:
    if CERTIFICATE_PATH.read_text() != result.certificate_text() or REPORT_PATH.read_text() != result.report_text():
        raise AssertionError("rational q2/D artifact drifted")


def _guards(result: BergerRationalFixtureQ2DBlock) -> None:
    for name, path, value in (
        ("promote support local", ("flags", "CLASSICAL_SUPPORT_LOCAL_Q2"), True),
        ("promote D equivariance", ("flags", "BERGER_LOCAL_D_ACTION_EQUIVARIANT"), True),
        ("promote physical ND2", ("flags", "ND2_PHYSICAL_EXECUTION_AUTHORIZED"), True),
        ("erase reduced scope", ("scope", "not_support_local_q2"), False),
    ):
        mutant = deepcopy(result.payload)
        target = mutant
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
        try:
            BergerRationalFixtureQ2DBlock(mutant).verify()
        except AssertionError:
            continue
        raise AssertionError(f"mutation guard accepted: {name}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    result = BergerRationalFixtureQ2DBlock.build()
    if args.write:
        _write(result)
    if args.check:
        _check(result)
    if args.guards:
        _guards(result)
    print("BERGER_RATIONAL_FIXTURE_Q2_D_BLOCK: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
