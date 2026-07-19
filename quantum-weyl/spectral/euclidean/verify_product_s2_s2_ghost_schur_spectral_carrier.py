#!/usr/bin/env python3
"""Independent matrix verifier for the S2 x S2 Schur spectral carrier."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERTIFICATE = HERE / "certificates/PRODUCT_S2_S2_GHOST_SCHUR_SPECTRAL_CARRIER.json"
SCHEMA = HERE / "schema/product-s2-s2-ghost-schur-spectral-carrier-v1.schema.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _q(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def _det(matrix: list[list[Fraction]]) -> Fraction:
    if len(matrix) == 1:
        return matrix[0][0]
    if len(matrix) == 2:
        return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]
    raise AssertionError("fixture uses only one- and two-dimensional exact sectors")


def _matrix_ratio(k1: Fraction, k2: Fraction, ell: int, emm: int) -> Fraction:
    a = k1 * ell * (ell + 1)
    b = k2 * emm * (emm + 1)
    lam = a + b
    active = []
    if ell:
        active.append((a, k1))
    if emm:
        active.append((b, k2))
    size = len(active)
    h0 = [[Fraction(0) for _ in range(size)] for _ in range(size)]
    h = [[Fraction(0) for _ in range(size)] for _ in range(size)]
    for row, (_, curvature) in enumerate(active):
        h0[row][row] = lam
        h[row][row] = lam - 2 * curvature
        for column, (divergence_eigenvalue, _) in enumerate(active):
            h0[row][column] += divergence_eigenvalue / 2
            h[row][column] += divergence_eigenvalue / 2
    return _det(h) / _det(h0)


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

    k1 = Fraction(1)
    k2 = Fraction(2)
    for row in payload["anisotropic_exact_modes"]:
        ratio = _matrix_ratio(k1, k2, row["ell"], row["m"])
        assert ratio == _q(row["paired_vector_times_schur_ratio"])
        if row["status"] == "REGULAR":
            assert _q(row["minimal_vector_ratio"]) * _q(row["schur_eigenvalue"]) == ratio
        else:
            assert _q(row["minimal_vector_ratio"]) == 0
            assert ratio == Fraction(1, 3)

    # Recompute the finite rectangular product directly from the full exact
    # vector matrices, without calling the producer's Schur factorization.
    product = Fraction(1)
    mode_count = 0
    exceptional_dimension = 0
    for ell in range(4):
        for emm in range(4):
            if ell == emm == 0:
                continue
            degeneracy = (2 * ell + 1) * (2 * emm + 1)
            ratio = _matrix_ratio(k1, k2, ell, emm)
            product *= ratio**degeneracy
            mode_count += degeneracy
            if (ell, emm) in {(1, 0), (0, 1)}:
                exceptional_dimension += degeneracy
    fixture = payload["finite_cutoff_fixture"]
    assert product == _q(fixture["paired_vector_times_schur_product"])
    assert mode_count == fixture["scalar_harmonic_multiplicity_including_exceptional"] == 255
    assert exceptional_dimension == fixture["exceptional_matched_dimension"] == 6

    # The equal-curvature mode formula independently matches the declared
    # Einstein Schur ratio on a regular mixed mode.
    k = Fraction(3)
    ell, emm = 2, 1
    lam = k * (ell * (ell + 1) + emm * (emm + 1))
    schur_direct = Fraction(2, 3) + Fraction(1, 3) * lam / (lam - 2 * k)
    schur_einstein = (lam - Fraction(4, 3) * k) / (lam - 2 * k)
    assert schur_direct == schur_einstein

    # Independent substitution of the product curvature invariants into the
    # already certified local residue formula.
    r_scalar = 2 * (k1 + k2)
    ricci_squared = 2 * (k1 * k1 + k2 * k2)
    normalized_volume = 1 / (k1 * k2)  # (4pi)^-2 Vol[S2 x S2]
    residue = normalized_volume * (r_scalar * r_scalar + 2 * ricci_squared) / 27
    assert residue == Fraction(28, 27)
    assert residue == _q(payload["residue_crosscheck"]["fixture_value"])

    flags = payload["claim_flags"]
    assert flags["PRODUCT_SPECTRAL_MEASURE_SUPPLIED"] is True
    assert flags["MATCHED_ZERO_POLE_POLICY_COMPUTED"] is True
    assert flags["INFINITE_DET3_VALUE_COMPUTED"] is False
    assert flags["FULL_COUPLED_GHOST_DETERMINANT_COMPUTED"] is False
    assert flags["LORENTZIAN_CERTIFIED"] is False
    print("PRODUCT S2xS2 GHOST SCHUR SPECTRAL CARRIER: INDEPENDENT PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
