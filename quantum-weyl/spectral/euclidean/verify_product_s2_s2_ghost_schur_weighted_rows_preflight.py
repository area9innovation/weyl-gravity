#!/usr/bin/env python3
"""Independent verifier for the product weighted-row numerical preflight."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERTIFICATE = HERE / "certificates/PRODUCT_S2_S2_GHOST_SCHUR_WEIGHTED_ROWS_PREFLIGHT.json"
SCHEMA = HERE / "schema/product-s2-s2-ghost-schur-weighted-rows-preflight-v1.schema.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _q(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def _gamma(count: int) -> Fraction:
    unit_roundoff = Fraction(1, 2**53)
    product = count * unit_roundoff
    return product / (1 - product)


def _residues() -> tuple[Fraction, Fraction]:
    """Recombine independently supplied heat-moment residues."""

    r10_2, r01_2 = Fraction(1, 3), Fraction(1, 6)
    r10_3, r01_3 = Fraction(1, 4), Fraction(1, 4)
    r20_4, r11_4, r02_4 = Fraction(1, 6), Fraction(1, 12), Fraction(1, 6)
    residue_k = (
        Fraction(2, 3) * (r10_2 + 2 * r01_2)
        + Fraction(4, 3) * (r10_3 + 4 * r01_3)
    )
    residue_k2 = Fraction(4, 9) * (r20_4 + 4 * r11_4 + 4 * r02_4)
    return residue_k, residue_k2


def _power_four_lattice_tail(cutoff: int) -> Fraction:
    x0 = Fraction(2 * cutoff + 3, 2)
    sum_5 = x0**-5 + Fraction(1, 4) * x0**-4
    sum_6 = x0**-6 + Fraction(1, 5) * x0**-5
    return Fraction(1, 3) * sum_5 + Fraction(2, 3) * sum_6 + Fraction(1, 12) * sum_5 + Fraction(1, 12) * sum_6


def _tails(cutoff: int) -> tuple[Fraction, Fraction]:
    x0 = Fraction(2 * cutoff + 3, 2)
    q_min = x0 * x0 + Fraction(1, 2)
    lam_min = q_min - Fraction(3, 4)
    comparison = 1 - Fraction(3, 4) / q_min
    lattice = _power_four_lattice_tail(cutoff)
    after_k3 = Fraction(1, 3) * (
        Fraction(16) / (1 - Fraction(2) / lam_min)
        + Fraction(256) / (1 - Fraction(4) / lam_min)
    )
    after_k2 = Fraction(1, 3) * (
        Fraction(8) / (1 - Fraction(2) / lam_min)
        + Fraction(64) / (1 - Fraction(4) / lam_min)
    )
    after_k1 = Fraction(1, 3) * (
        Fraction(4) / (1 - Fraction(2) / lam_min)
        + Fraction(16) / (1 - Fraction(4) / lam_min)
    )
    k2_remainder = Fraction(8, 3) * after_k2 + after_k1**2
    return (
        after_k3 * lattice / comparison**4,
        k2_remainder * lattice / comparison**4,
    )


def _stable_partial(cutoff: int) -> tuple[float, float]:
    r_k = 0.0
    r_k2 = 0.0
    for ell in range(cutoff + 1):
        a = ell * (ell + 1)
        for emm in range(cutoff + 1):
            if (ell, emm) in {(0, 0), (1, 0), (0, 1)}:
                continue
            b = 2 * emm * (emm + 1)
            lam = a + b
            k1 = (2.0 / 3.0) * (a + 2 * b) / lam**2
            k2 = (4.0 / 3.0) * (a + 4 * b) / lam**3
            after_k2 = 0.0
            after_k3 = 0.0
            if ell:
                after_k2 += (a / lam) * (2 / lam) ** 3 / (1 - 2 / lam)
                after_k3 += (a / lam) * (2 / lam) ** 4 / (1 - 2 / lam)
            if emm:
                after_k2 += (b / lam) * (4 / lam) ** 3 / (1 - 4 / lam)
                after_k3 += (b / lam) * (4 / lam) ** 4 / (1 - 4 / lam)
            after_k2 /= 3
            after_k3 /= 3
            degeneracy = (2 * ell + 1) * (2 * emm + 1)
            r_k += degeneracy * after_k3
            r_k2 += degeneracy * (
                k2 * k2 + 2 * (k1 + k2) * after_k2 + after_k2 * after_k2
            )
    return r_k, r_k2


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

    residue_k, residue_k2 = _residues()
    assert residue_k == Fraction(19, 9) == _q(payload["exact_pole_replay"]["Res_R_K"])
    assert residue_k2 == Fraction(14, 27) == _q(payload["exact_pole_replay"]["Res_R_K2"])

    remainder = payload["trace_class_remainders"]
    bounds = remainder["bounds"]
    cutoff = remainder["rectangular_cutoff"]
    assert cutoff == 2400
    assert _q(bounds["power_four_lattice_tail"]) == _power_four_lattice_tail(cutoff)
    tail_k, tail_k2 = _tails(cutoff)
    assert _q(bounds["R_K_exterior_tail_bound"]) == tail_k
    assert _q(bounds["FP_R_K2_exterior_tail_bound"]) == tail_k2
    assert _q(bounds["ordinary_summation_gamma"]) == _gamma(bounds["summand_count"])
    assert _q(bounds["derived_rounding_bound"]) < _q(bounds["declared_rounding_cushion"])

    # A smaller, independently recomputed rectangle must agree with the stored
    # large rectangle within its own exact exterior bound and both roundoff cushions.
    check_cutoff = 300
    check_k, check_k2 = _stable_partial(check_cutoff)
    check_tail_k, check_tail_k2 = _tails(check_cutoff)
    cushion = float(_q(bounds["declared_rounding_cushion"]))
    assert abs(float(remainder["R_K_partial"]) - check_k) < float(check_tail_k) + 2 * cushion
    assert abs(float(remainder["FP_R_K2_partial"]) - check_k2) < float(check_tail_k2) + 2 * cushion

    intervals = payload["numerical_candidate_intervals"]
    for row in ("R_Delta_K", "FP_R_Delta_K2", "low_order_split_R_K_minus_half_R_K2"):
        assert float(intervals[row]["lower"]) < float(intervals[row]["upper"])
    assert float(intervals["R_Delta_K"]["lower"]) < -2.240660268 < float(intervals["R_Delta_K"]["upper"])
    assert float(intervals["FP_R_Delta_K2"]["lower"]) < 1.966971853 < float(intervals["FP_R_Delta_K2"]["upper"])

    flags = payload["claim_flags"]
    assert flags["PRODUCT_WEIGHTED_TRACE_POLES_REPLAYED"] is True
    assert flags["PRODUCT_TRACE_CLASS_REMAINDER_TAILS_RIGOROUSLY_BOUNDED"] is True
    assert flags["PRODUCT_HEAT_EULER_MACLAURIN_REMAINDER_RIGOROUSLY_BOUNDED"] is False
    assert flags["PRODUCT_WEIGHTED_R_K_COMPUTED"] is False
    assert flags["PRODUCT_FINITE_PART_R_K2_COMPUTED"] is False
    assert flags["COMPLETE_RENORMALIZED_Q1_SUPPLIED"] is False
    assert flags["LORENTZIAN_CERTIFIED"] is False
    print("PRODUCT S2xS2 SCHUR WEIGHTED ROWS: INDEPENDENT PREFLIGHT PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
