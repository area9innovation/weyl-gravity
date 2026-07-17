#!/usr/bin/env python3
"""Independent action-to-payload cross-check for two Berger ``q3`` sectors.

This checker deliberately does not import the large ``q3`` producer.  It
derives the homogeneous lapse/radial density directly with SymPy, takes the
fourth action derivatives required by the declared factorial convention, and
compares all ordered ``(h_00,R)^3`` coefficients in two published output
rows.  It is a strategic cross-check, not a second full derivation of the
5.8-million-term operation.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
import gzip
import hashlib
import json
from itertools import product
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "d_quotient_classical/certificates/BERGER_Q3_ACTION_SECTOR_CROSSCHECK.json"
SCHEMA = ROOT / "d_quotient_classical/schema/berger-q3-action-sector-crosscheck-v1.schema.json"
Q3_CERTIFICATE = ROOT / "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_Q3.json"
Q3_MANIFEST = ROOT / "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_Q3_PAYLOAD.json"
Q3_PRODUCER = ROOT / "d_quotient_classical/backreacted_clock/berger_support_local_q2.py"
ROW_PATHS = {
    27: ROOT / "d_quotient_classical/generated/berger_support_local_q3/row_27.json.gz",
    37: ROOT / "d_quotient_classical/generated/berger_support_local_q3/row_37.json.gz",
}

H = 5
R = 15
ZERO_WORD = [0, 0, 0, 0]


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _fraction(value: object) -> Fraction:
    if isinstance(value, int):
        return Fraction(value)
    if not isinstance(value, dict):
        raise AssertionError(f"unsupported exact coefficient: {value!r}")
    rational = value["rational"]
    sqrt10 = value["sqrt10"]
    if sqrt10 != 0:
        raise AssertionError("selected action sector unexpectedly contains sqrt(10)")
    if isinstance(rational, int):
        return Fraction(rational)
    return Fraction(rational["numerator"], rational["denominator"])


def _published_sector(output: int) -> dict[tuple[int, int, int], Fraction]:
    with gzip.open(ROW_PATHS[output], "rt", encoding="utf-8") as handle:
        payload = json.load(handle)
    if payload["output"] != output:
        raise AssertionError("row output index drifted")
    selected: dict[tuple[int, int, int], Fraction] = {}
    for term in payload["terms"]:
        first, first_word, second, second_word, third, third_word, coefficient = term
        inputs = (first, second, third)
        if set(inputs) <= {H, R} and first_word == second_word == third_word == ZERO_WORD:
            selected[inputs] = _fraction(coefficient)
    if len(selected) != 8:
        raise AssertionError(f"expected eight ordered h/R terms in row {output}, found {len(selected)}")
    return selected


def _direct_density() -> tuple[sp.Symbol, sp.Symbol, sp.Expr]:
    """Return the independently written reduced density L(h,R).

    The dressed fields obey

        g_00 = -1 + h + 2 R,
        g_ij = (1 - 2 R) gbar_ij,
        rho = 1 + R.

    Thus N=sqrt(1-h-2R) and k=1-2R.  Constant lapse rescaling does
    not change the spatial curvature, while a constant spatial rescaling
    gives R(g)=Rbar/k and C(g)^2=Cbar^2/k^2.
    """

    h, radial = sp.symbols("h radial")
    q = sp.Rational(9, 40)
    alpha_b = sp.Integer(5)
    omega = sp.Rational(3, 4)
    quartic = sp.Rational(119, 480)
    k = 1 - 2 * radial
    lapse = sp.sqrt(1 - h - 2 * radial)
    rho = 1 + radial
    weyl_squared = sp.Rational(4, 3) * (1 - q) ** 2
    scalar_curvature = (4 - q) / 2
    density = lapse * k ** sp.Rational(3, 2) * (
        alpha_b * weyl_squared / (8 * k**2)
        + rho**2 * omega**2 / (2 * lapse**2)
        - scalar_curvature * rho**2 / (12 * k)
        - quartic * rho**4 / 4
    )
    return h, radial, sp.factor(density)


def _expected(output: int, inputs: tuple[int, int, int]) -> Fraction:
    h, radial, density = _direct_density()
    input_h = inputs.count(H)
    input_r = inputs.count(R)
    # Rows 27 and 37 use the frozen twice-Euler-density convention.  The
    # output derivative adds one h or R derivative to the three inputs.
    derivative_h = input_h + (output == 27)
    derivative_r = input_r + (output == 37)
    value = 2 * sp.diff(density, h, derivative_h, radial, derivative_r).subs(
        {h: 0, radial: 0}
    )
    value = sp.factor(value)
    if not value.is_Rational:
        raise AssertionError(f"direct action derivative is not rational: {value}")
    return Fraction(int(value.p), int(value.q))


def _text(payload: object) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def build() -> dict[str, object]:
    coefficients: list[dict[str, object]] = []
    for output, output_name in ((27, "h_hat_star_00"), (37, "R_star")):
        observed = _published_sector(output)
        for input_h in range(4):
            canonical_inputs = (H,) * input_h + (R,) * (3 - input_h)
            expected = _expected(output, canonical_inputs)
            ordered = [
                inputs
                for inputs in product((H, R), repeat=3)
                if inputs.count(H) == input_h
            ]
            values = {observed[inputs] for inputs in ordered}
            if values != {expected}:
                raise AssertionError(
                    f"action/payload mismatch output={output} input_h={input_h}: "
                    f"expected {expected}, observed {sorted(values)}"
                )
            coefficients.append(
                {
                    "output": output,
                    "output_row": output_name,
                    "input_h_count": input_h,
                    "input_R_count": 3 - input_h,
                    "ordered_permutations_checked": len(ordered),
                    "expected_from_direct_action": str(expected),
                    "observed_in_frozen_payload": str(next(iter(values))),
                }
            )

    q3 = json.loads(Q3_CERTIFICATE.read_text())
    if q3["result_id"] != "BERGER_SUPPORT_LOCAL_Q3":
        raise AssertionError("unexpected q3 certificate")
    return {
        "schema": "pure-weyl-berger-q3-action-sector-crosscheck-v1",
        "result_id": "BERGER_Q3_ACTION_SECTOR_CROSSCHECK",
        "claim_status": "CERTIFIED_STRATEGIC_INDEPENDENT_CROSSCHECK",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "setting_id": "rational_positive_berger_clock_homogeneous_lapse_radial_sector",
        "independent_method": {
            "producer_imported": False,
            "method": "direct SymPy fourth derivatives of an independently written homogeneous reduced action density",
            "variables": ["h_hat_00", "R"],
            "outputs": ["h_hat_star_00", "R_star"],
            "factorial_normalization": "twice-Euler-density q3 coefficient equals two times the fourth action derivative",
            "ordered_payload_coefficients_checked": 16,
            "independent_derivative_values": 8,
        },
        "source_manifest": {
            "crosscheck_source": {
                "path": str(Path(__file__).resolve().relative_to(ROOT)),
                "sha256": _sha256(Path(__file__).resolve()),
            },
            "q3_producer_under_test": {
                "path": str(Q3_PRODUCER.relative_to(ROOT)),
                "sha256": _sha256(Q3_PRODUCER),
            },
            "q3_certificate": {
                "path": str(Q3_CERTIFICATE.relative_to(ROOT)),
                "sha256": _sha256(Q3_CERTIFICATE),
            },
            "q3_payload_manifest": {
                "path": str(Q3_MANIFEST.relative_to(ROOT)),
                "sha256": _sha256(Q3_MANIFEST),
            },
            "q3_row_27": {
                "path": str(ROW_PATHS[27].relative_to(ROOT)),
                "sha256": _sha256(ROW_PATHS[27]),
            },
            "q3_row_37": {
                "path": str(ROW_PATHS[37].relative_to(ROOT)),
                "sha256": _sha256(ROW_PATHS[37]),
            },
        },
        "coefficients": coefficients,
        "exact_checks": {
            "direct_background_density_stationary": True,
            "all_eight_action_derivatives_match": True,
            "all_sixteen_ordered_payload_coefficients_match": True,
            "lapse_sector_checked": True,
            "dressed_radial_weyl_sector_checked": True,
            "q3_producer_not_imported": True,
        },
        "flags": {
            "BERGER_Q3_ACTION_SECTOR_CROSSCHECK": True,
            "FULL_INDEPENDENT_Q3_REDERIVATION": False,
            "THEOREM_FROZEN": False,
        },
        "verification_commands": [
            "PYTHONPATH=. python3 d_quotient_classical/backreacted_clock/berger_q3_action_sector_crosscheck.py --check --guards",
            "PYTHONPATH=. python3 d_quotient_classical/backreacted_clock/verify_berger_q3_action_sector_crosscheck.py",
            "PYTHONPATH=. pytest -q d_quotient_classical/backreacted_clock/tests/test_berger_q3_action_sector_crosscheck.py",
        ],
        "claim_boundary": "This independent exact calculation crosses the action-to-frozen-q3 boundary in the homogeneous lapse and dressed radial/Weyl sector: eight fourth action derivatives agree with sixteen ordered coefficients in two published q3 rows. It is not a second derivation of the complete 5,812,130-term q3 operation and does not freeze Paper IX.",
    }


def verify(payload: dict[str, object]) -> None:
    checks = payload["exact_checks"]
    if not isinstance(checks, dict) or not all(value is True for value in checks.values()):
        raise AssertionError("cross-check ledger contains a false result")
    flags = payload["flags"]
    if flags != {
        "BERGER_Q3_ACTION_SECTOR_CROSSCHECK": True,
        "FULL_INDEPENDENT_Q3_REDERIVATION": False,
        "THEOREM_FROZEN": False,
    }:
        raise AssertionError("cross-check flags were broadened")
    if len(payload["coefficients"]) != 8:
        raise AssertionError("coefficient ledger is incomplete")
    if sum(entry["ordered_permutations_checked"] for entry in payload["coefficients"]) != 16:
        raise AssertionError("ordered coefficient coverage drifted")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    payload = build()
    verify(payload)
    if args.write:
        CERTIFICATE.write_text(_text(payload))
    if args.check and CERTIFICATE.read_text() != _text(payload):
        raise AssertionError("q3 action-sector cross-check certificate drifted")
    if args.guards:
        mutant = json.loads(_text(payload))
        mutant["flags"]["FULL_INDEPENDENT_Q3_REDERIVATION"] = True
        try:
            verify(mutant)
        except AssertionError:
            pass
        else:
            raise AssertionError("scope mutation was accepted")
    print("BERGER_Q3_ACTION_SECTOR_CROSSCHECK: PASS")
    print("8 direct action derivatives; 16 ordered frozen q3 coefficients; exact agreement")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
