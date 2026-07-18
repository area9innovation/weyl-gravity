#!/usr/bin/env python3
"""Independent verifier for the round-S4 Schur zeta factorization."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import mpmath as mp


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERTIFICATE = HERE / "certificates/ROUND_S4_GHOST_SCHUR_ZETA_FACTORIZATION.json"
SCHEMA = HERE / "schema/round-s4-ghost-schur-zeta-factorization-v1.schema.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _variable_part_derivative(c2: mp.mpf, terms: int = 320) -> mp.mpf:
    """Derivative at zero of the shift-dependent spectral-zeta part.

    This is an independent Hurwitz-zeta continuation of
    sum d_l[(l+3/2)^2-c2]^-s for l>=2.  The k=1 and k=2 terms are
    handled separately because their Hurwitz factors have a pole at one.
    """

    q = mp.mpf(7) / 2
    psi = mp.digamma(q)
    total = c2 / 3 * mp.zeta(-1, q) + c2 * psi / 12
    total += c2**2 / 3 * (
        -psi / 2 + mp.mpf(1) / 4 - mp.zeta(3, q) / 8
    )
    for k in range(3, terms + 1):
        total += c2**k / (3 * k) * (
            mp.zeta(2 * k - 3, q) - mp.zeta(2 * k - 1, q) / 4
        )
    return total


def main() -> int:
    payload = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)

    for reference in payload["dependencies"].values():
        path = ROOT / reference["path"]
        assert path.is_file()
        assert _sha256(path) == reference["sha256"]
        source = json.loads(path.read_text())
        assert (source.get("result_id") or source.get("schema")) == reference["result_id"]

    # Independent exact residue replay.
    volume = Fraction(8, 3)  # coefficient of pi^2 in Vol(S4)
    heat_prefactor = Fraction(1, 16)  # coefficient of pi^-2 in (4pi)^-2
    wres_q_minus_2 = 2 * volume * heat_prefactor
    assert wres_q_minus_2 == Fraction(1, 3)
    square_difference = Fraction(4**2 - 6**2)
    defect = -Fraction(1, 4) * square_difference * wres_q_minus_2
    assert defect == Fraction(5, 3)
    assert payload["local_residue_derivation"]["exact_factorization_defect"] == {
        "numerator": 5,
        "denominator": 3,
    }

    # Independent spectral-zeta continuation, not the producer's residue
    # calculation.  Delta-4 corresponds to c2=25/4 and Delta-6 to c2=33/4.
    mp.mp.dps = 70
    derivative_a = _variable_part_derivative(mp.mpf(25) / 4)
    derivative_b = _variable_part_derivative(mp.mpf(33) / 4)
    zeta_ratio = -derivative_a + derivative_b
    stored_ratio = mp.mpf(
        payload["factorization_result"]["zeta_determinant_ratio_decimal"]
    )
    assert abs(zeta_ratio - stored_ratio) < mp.mpf("2e-42")

    weighted = mp.mpf(
        payload["factorization_result"]["weighted_modified_determinant"]
    )
    assert abs(zeta_ratio - weighted - mp.mpf(5) / 3) < mp.mpf("7e-48")

    flags = payload["claim_flags"]
    assert flags["ROUND_S4_ZETA_WEIGHTED_FACTORIZATION_DEFECT_COMPUTED"] is True
    assert flags["ROUND_S4_ZETA_FACTORIZED_SCHUR_RATIO_COMPUTED"] is True
    assert flags["GENERIC_NONCOMMUTING_ZETA_FACTORIZATION_DEFECT_COMPUTED"] is False
    assert flags["GENERIC_BACKGROUND_FINITE_SCHUR_ROWS_COMPUTED"] is False
    assert flags["COMPLETE_RENORMALIZED_Q1_SUPPLIED"] is False
    assert flags["LORENTZIAN_CERTIFIED"] is False
    print("ROUND S4 GHOST SCHUR ZETA FACTORIZATION: INDEPENDENT PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
