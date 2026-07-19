"""Independent verifier for the all-ell standard-branch collision census."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_symbolic_ell_standard_branch_collision_census.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify() -> None:
    payload = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    schema_path = ROOT / payload["schema_path"]
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
    assert payload["schema_sha256"] == _sha256(schema_path)
    for item in payload["provenance"]["inputs"].values():
        path = ROOT / item["path"]
        assert item["sha256"] == _sha256(path)

    ell = sp.symbols("ell", integer=True, positive=True)
    lam = ell * (ell + 1)
    root = sp.sqrt(2 * lam)
    shift = ell / 2 + sp.Rational(1, 6)
    k2 = root - shift
    minus2 = lam - shift
    plus2 = minus2 + 2 * root
    product = sp.sqrt(minus2 * plus2)
    mixed_sum0 = 2 * (minus2 + root + product)
    mixed_sum2 = sp.factor(mixed_sum0 - 4 * k2)
    mixed_diff0 = sp.factor(2 * (minus2 + root - product))
    mixed_diff2 = sp.factor(mixed_diff0 - 4 * k2)
    top_lam = 2 * ell * (2 * ell + 1)
    top_p = top_lam - sp.Rational(2, 3)
    top_root = sp.sqrt(2 * top_lam)
    top_qplus = top_lam + top_root

    lower_rhs = ell**2 - ell / 2 - sp.Rational(1, 2) + root
    lower_gap = sp.factor(minus2 * plus2 - lower_rhs**2)
    assert sp.factor(lower_gap - sp.Rational(2, 9) * (9 * ell * root + 3 * root + 9 * ell**3 - 6 * ell**2 - 12 * ell - 1)) == 0
    assert sp.factor(mixed_sum2 - top_p - 2 * (product - lower_rhs)) == 0
    assert sp.factor(4 * lam - mixed_sum2 - 2 * (minus2 + root - product)) == 0

    h = 4 * root - 2 * ell - sp.Rational(4, 3)
    h_norm = sp.factor((63 * ell**2 + 75 * ell + 4) ** 2 - 2 * lam * (36 * ell + 24) ** 2)
    assert h_norm == 1377 * ell**4 + 3402 * ell**3 + 1521 * ell**2 - 552 * ell + 16
    assert sp.factor(mixed_sum0 - mixed_sum2 - 4 * k2) == 0

    denominator = minus2 + root + product
    assert sp.simplify(mixed_diff0 - 4 * lam / denominator) == 0
    assert sp.factor(root**2 - (ell + sp.Rational(1, 3)) ** 2 - (9 * ell**2 + 12 * ell - 1) / 9) == 0
    assert sp.factor((lam + 2 * shift) ** 2 - 4 * root**2 - (9 * ell**4 + 36 * ell**3 - 30 * ell**2 - 60 * ell + 1) / 9) == 0
    assert sp.factor(root**2 - (ell / 2 + sp.Rational(2, 3)) ** 2 - (63 * ell**2 + 48 * ell - 16) / 36) == 0

    # Exact fibres guard the strict ordering implementation without serving as proof by scan.
    for value in range(2, 33):
        substitutions = {ell: value}
        assert bool(sp.N((mixed_sum2 - top_p).subs(substitutions)) > 0)
        assert bool(sp.N((top_qplus - mixed_sum2).subs(substitutions)) > 0)
        assert bool(sp.N((mixed_sum0 - top_qplus).subs(substitutions)) > 0)
        assert bool(sp.N((mixed_diff0 - sp.Rational(4, 3)).subs(substitutions)) > 0)
        assert bool(sp.N((2 - mixed_diff0).subs(substitutions)) > 0)
        assert bool(sp.N(mixed_diff2.subs(substitutions)) < 0)

    classification = payload["classification"]
    assert classification["all_standard_qminus_qplus_input_pairs_covered"]
    assert classification["all_sum_difference_and_K0_K2k_channels_covered"]
    assert classification["qplus_involving_characteristic_collisions_excluded"]
    assert classification["unique_nonzero_frequency_standard_branch_collision_is_qminus_L2ell_p"]
    assert not classification["complete_bounded_second_order_extension_certified"]
    assert not classification["extra_primary_or_multiple_abs_momentum_inputs_classified"]
    assert not classification["causal_or_quantum_claim"]
    print("EINSTEIN_MAXWELL_WEYL_SYMBOLIC_ELL_STANDARD_BRANCH_COLLISION_CENSUS verifier: PASS")


if __name__ == "__main__":
    verify()
