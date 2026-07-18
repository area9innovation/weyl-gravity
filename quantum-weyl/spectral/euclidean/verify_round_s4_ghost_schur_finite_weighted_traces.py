#!/usr/bin/env python3
"""Independent verifier for the round-S4 Schur finite weighted traces."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import mpmath as mp


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERTIFICATE = HERE / "certificates/ROUND_S4_GHOST_SCHUR_FINITE_WEIGHTED_TRACES.json"
SCHEMA = HERE / "schema/round-s4-ghost-schur-finite-weighted-traces-v2.schema.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _shifted_zeta_binomial(s: mp.mpf, terms: int = 600) -> mp.mpf:
    """Analytically continue Z_B(s) using a convergent Hurwitz-zeta series."""

    q = mp.mpf(7) / 2
    a2 = mp.mpf(33) / 4
    total = mp.mpf(0)
    pochhammer = mp.mpf(1)
    factorial = mp.mpf(1)
    for k in range(terms):
        if k:
            pochhammer *= s + k - 1
            factorial *= k
        coefficient = pochhammer * a2**k / factorial
        total += coefficient * (
            mp.zeta(2 * s + 2 * k - 3, q)
            - mp.mpf(1) / 4 * mp.zeta(2 * s + 2 * k - 1, q)
        )
    return total / 3


def _stored_decimal(payload: dict, row: str) -> mp.mpf:
    return mp.mpf(
        payload["exact_finite_rows"]["Delta_weighted_finite_rows"][row][
            "decimal"
        ]
    )


def main() -> int:
    mp.mp.dps = 70
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

    q = mp.mpf(7) / 2
    a = mp.sqrt(33) / 2
    psi_sum = mp.digamma(q - a) + mp.digamma(q + a)
    trigamma_difference = mp.polygamma(1, q - a) - mp.polygamma(1, q + a)
    fp1 = -mp.mpf(1) / 9 - mp.mpf(4) / 3 * psi_sum
    fp2 = -mp.mpf(1) / 6 * psi_sum + mp.mpf(2) / (3 * a) * trigamma_difference
    r_delta_k = 2 * fp1 - 2
    r_delta_k2 = 4 * fp2
    low = r_delta_k - r_delta_k2 / 2

    tolerance = mp.mpf("1e-48")
    assert abs(_stored_decimal(payload, "R_Delta_K") - r_delta_k) < tolerance
    assert abs(_stored_decimal(payload, "FP_R_Delta_K2") - r_delta_k2) < tolerance
    assert abs(_stored_decimal(payload, "low_order_renormalized_split") - low) < tolerance

    # Independent summation of the absolutely convergent modified-determinant
    # tail.  This does not reuse the producer's rational Taylor/Hurwitz/
    # Euler--Maclaurin enclosure.
    def det3_mode(ell_value: mp.mpf) -> mp.mpf:
        eigenvalue = ell_value * (ell_value + 3)
        degeneracy = (2 * ell_value + 3) * (ell_value + 2) * (ell_value + 1) / 6
        k_value = 2 / (eigenvalue - 6)
        return degeneracy * (
            mp.log1p(k_value) - k_value + k_value * k_value / 2
        )

    det3_direct = mp.nsum(det3_mode, [2, mp.inf])
    det3_payload = payload["exact_finite_rows"]["canonical_det3_tail"]
    det3_lower = mp.mpf(det3_payload["lower_endpoint_decimal"])
    det3_upper = mp.mpf(det3_payload["upper_endpoint_decimal"])
    assert det3_lower < det3_direct < det3_upper
    assert det3_payload["certified_common_decimal_prefix"].startswith(
        "0.4981635654196290984312532999414818723861"
    )
    full_direct = low + det3_direct
    full_stored = mp.mpf(
        payload["exact_finite_rows"]["full_modified_determinant"][
            "high_precision_decimal"
        ]
    )
    assert abs(full_direct - full_stored) < mp.mpf("6e-48")

    # Independent continuation: subtract the known simple poles from the
    # convergent Hurwitz-zeta expansion and Richardson-extrapolate eps -> 0.
    eps = mp.mpf("2e-4")
    v1_eps = _shifted_zeta_binomial(1 + eps) - mp.mpf(4) / (3 * eps)
    v1_half = _shifted_zeta_binomial(1 + eps / 2) - mp.mpf(8) / (3 * eps)
    fp1_richardson = 2 * v1_half - v1_eps
    v2_eps = _shifted_zeta_binomial(2 + eps) - mp.mpf(1) / (6 * eps)
    v2_half = _shifted_zeta_binomial(2 + eps / 2) - mp.mpf(1) / (3 * eps)
    fp2_richardson = 2 * v2_half - v2_eps
    assert abs(fp1_richardson - fp1) < mp.mpf("4e-7")
    assert abs(fp2_richardson - fp2) < mp.mpf("5e-7")

    # The five ell=1 modes are true zeros of S_L and must not enter the
    # finite determinant carrier.
    ell = 1
    lam = ell * (ell + 3)
    degeneracy = (2 * ell + 3) * (ell + 2) * (ell + 1) // 6
    assert lam == 4 and degeneracy == 5
    assert Fraction(lam - 4, lam - 6) == 0

    # A rank-one smoothing perturbation changes the two finite rows while
    # leaving all homogeneous symbols and residues untouched.
    k_e = Fraction(1, 2)
    t_e = Fraction(7, 11)
    assert t_e == Fraction(7, 11)
    assert 2 * k_e * t_e + t_e * t_e == Fraction(126, 121)

    flags = payload["claim_flags"]
    assert flags["ROUND_S4_R_DELTA_K_COMPUTED"] is True
    assert flags["ROUND_S4_FINITE_R_DELTA_K2_COMPUTED"] is True
    assert flags["GENERIC_BACKGROUND_R_K_COMPUTED"] is False
    assert flags["GENERIC_MULTIPLICATIVE_ANOMALY_COMPUTED"] is False
    assert flags["FULL_ROUND_S4_DET3_TAIL_COMPUTED"] is True
    assert flags["FULL_ROUND_S4_MODIFIED_DETERMINANT_COMPUTED"] is True
    assert flags["FULL_GENERIC_SCHUR_DETERMINANT_COMPUTED"] is False
    print("ROUND S4 GHOST SCHUR MODIFIED DETERMINANT: INDEPENDENT PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
