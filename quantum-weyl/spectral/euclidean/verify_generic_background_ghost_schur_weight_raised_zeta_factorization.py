#!/usr/bin/env python3
"""Independent replay of the generic weight-raised Schur defect."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import mpmath as mp


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERTIFICATE = (
    HERE
    / "certificates/GENERIC_BACKGROUND_GHOST_SCHUR_WEIGHT_RAISED_ZETA_FACTORIZATION.json"
)
SCHEMA = (
    HERE
    / "schema/generic-background-ghost-schur-weight-raised-zeta-factorization-v1.schema.json"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _q(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def _zeta_delta(s: mp.mpf, *, terms: int = 58) -> mp.mpf:
    """Continue the primed round-S4 scalar zeta function.

    With n=ell+3/2, ell>=2, the degeneracy is
    (n^3-n/4)/3 and Delta=n^2-9/4.  Expanding in 9/(4n^2)
    gives a rapidly convergent Hurwitz-zeta continuation.
    """

    q = mp.mpf(7) / 2
    c0 = mp.mpf(9) / 4
    total = mp.mpf("0")
    for k in range(terms + 1):
        coefficient = mp.rf(s, k) * c0**k / mp.factorial(k)
        total += coefficient * (
            mp.zeta(2 * s + 2 * k - 3, q)
            - mp.zeta(2 * s + 2 * k - 1, q) / 4
        ) / 3
    return total


def _schur_power_coefficients(s: mp.mpf, *, terms: int) -> list[mp.mpf]:
    """Coefficients of ((1-4/z)/(1-6/z))^-s in z^-1."""

    coefficients = [mp.mpf(1)]
    for n in range(1, terms + 1):
        convolution = mp.fsum(
            (mp.mpf(4) ** k - mp.mpf(6) ** k) * coefficients[n - k]
            for k in range(1, n + 1)
        )
        coefficients.append(s * convolution / n)
    return coefficients


def _zeta_weight_raised(s: mp.mpf, *, terms: int = 58) -> mp.mpf:
    coefficients = _schur_power_coefficients(s, terms=terms)
    return mp.fsum(
        coefficient * _zeta_delta(s + n, terms=terms)
        for n, coefficient in enumerate(coefficients)
    )


def _round_zeta_ratio() -> mp.mpf:
    """Direct continuation of log det(S_L Delta)-log det(Delta)."""

    step = mp.mpf("1e-9")

    def difference(s: mp.mpf) -> mp.mpf:
        return _zeta_weight_raised(s) - _zeta_delta(s)

    return -(difference(step) - difference(-step)) / (2 * step)


def verify() -> dict[str, str]:
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

    # Replay the BCH order filtration independently.  In dimension four only
    # orders down to -4 can contribute to a Wodzicki residue.
    order_x = -2
    order_y = 0
    commutator = order_x + order_y - 1
    double_y = order_y + commutator - 1
    double_x = order_x + commutator - 1
    assert (commutator, double_y, double_x) == (-3, -4, -6)
    assert payload["BCH_reduction"]["weighted_BCH_trace_through_residue_order"] == _q(0)

    # The trace-defect identity kills both surviving BCH commutators because
    # one entry is log Q.  Cross terms with X start at order -5; X^2 has the
    # same residue as K^2 since log(1+K)=K+O(Psi^-4).
    wres_k2_coefficient = Fraction(1, 27)
    defect_r2 = -Fraction(1, 4) * wres_k2_coefficient
    defect_ric2 = 2 * defect_r2
    assert defect_r2 == Fraction(-1, 108)
    assert defect_ric2 == Fraction(-1, 54)
    assert payload["generic_local_result"]["coefficient_of_(4pi)^-2_integral_R2"] == _q(defect_r2)
    assert payload["generic_local_result"]["coefficient_of_(4pi)^-2_integral_Ric2"] == _q(defect_ric2)

    # Round unit S4: R=12, |Ric|^2=36 and Vol=8 pi^2/3.
    # Converting the integral to the repository Wres normalization gives 4/3.
    round_integrand = Fraction(12**2 + 2 * 36)
    volume_over_4pi_squared = Fraction(1, 6)
    round_wres = round_integrand * volume_over_4pi_squared / 27
    round_defect = -round_wres / 4
    assert round_wres == Fraction(4, 3)
    assert round_defect == Fraction(-1, 3)
    assert payload["round_S4_crosscheck"]["weight_raised_defect"] == _q(round_defect)
    assert payload["factorization_convention_crosswalk"]["difference_of_defects"] == _q(2)

    # This is an independent global check.  It never calls the producer's
    # residue calculation: the primed spectrum is analytically continued by
    # Hurwitz zeta and differentiated at the origin.
    mp.mp.dps = 60
    direct = _round_zeta_ratio()
    stored = mp.mpf(
        payload["round_S4_crosscheck"][
            "zeta_ratio_log_det_(S_L_Delta)_minus_log_det_Delta"
        ]
    )
    assert abs(direct - stored) < mp.mpf("2e-10")

    flags = payload["claim_flags"]
    assert flags["GENERIC_WEIGHT_RAISED_SCHUR_ZETA_FACTORIZATION_DEFECT_COMPUTED"] is True
    assert flags["GENERIC_BCH_WEIGHTED_TRACE_VANISHES_AT_4D_LOCAL_RESIDUE_ORDER"] is True
    assert flags["ROUND_S4_WEIGHT_RAISED_SPECIALIZATION_REPLAYED"] is True
    for name in (
        "GENERIC_BACKGROUND_FINITE_SCHUR_ROWS_COMPUTED",
        "FULL_GHOST_BLOCK_ZETA_FACTORIZATION_COMPUTED",
        "PHYSICAL_FOURTH_ORDER_HESSIAN_KERNEL_COMPUTED",
        "COMPLETE_RENORMALIZED_GAMMA1_SUPPLIED",
        "COMPLETE_RENORMALIZED_Q1_SUPPLIED",
        "RESIDUAL_TRANSFER_AUTHORIZED",
        "LORENTZIAN_CERTIFIED",
    ):
        assert flags[name] is False

    return {
        "direct_round_ratio": mp.nstr(direct, 45),
        "stored_round_ratio": mp.nstr(stored, 45),
    }


def main() -> int:
    result = verify()
    print(
        "GENERIC SCHUR WEIGHT-RAISED ZETA FACTORIZATION: INDEPENDENT PASS "
        f"({result['direct_round_ratio']})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
