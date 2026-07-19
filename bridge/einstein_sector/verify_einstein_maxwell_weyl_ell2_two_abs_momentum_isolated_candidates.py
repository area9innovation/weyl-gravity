#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_isolated_candidates.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_ell2_two_abs_momentum_isolated_candidates.schema.json"


def independently_enumerate() -> list[dict[str, object]]:
    input_offsets = {
        "q_minus": 6 - 2 * sp.sqrt(3),
        "p_extra": sp.Rational(16, 3),
        "q_plus": 6 + 2 * sp.sqrt(3),
    }
    target_offsets: dict[tuple[int, str], sp.Expr] = {
        (1, "standard"): sp.Integer(4),
        (1, "extra"): sp.Rational(4, 3),
    }
    for output_ell in range(2, 5):
        eigenvalue = output_ell * (output_ell + 1)
        target_offsets[(output_ell, "q_minus")] = eigenvalue - sp.sqrt(2 * eigenvalue)
        target_offsets[(output_ell, "p_extra")] = eigenvalue - sp.Rational(2, 3)
        target_offsets[(output_ell, "q_plus")] = eigenvalue + sp.sqrt(2 * eigenvalue)

    rows: list[dict[str, object]] = []
    for relative_sign in (-1, 1):
        n_1, n_2 = 1, 2 * relative_sign
        for first_name, first_offset in input_offsets.items():
            for second_name, second_offset in input_offsets.items():
                for (output_ell, target_name), target_offset in target_offsets.items():
                    difference = target_offset - first_offset - second_offset
                    rho_coefficient = sp.radsimp(
                        n_1**2 * second_offset
                        + n_2**2 * first_offset
                        - n_1 * n_2 * difference
                    )
                    constant = sp.radsimp(4 * first_offset * second_offset - difference**2)
                    if sp.simplify(rho_coefficient) == 0:
                        continue
                    rho = sp.factor(sp.radsimp(-constant / (4 * rho_coefficient)))
                    if rho.is_positive is not True:
                        continue
                    unsquared_sign = sp.factor(sp.radsimp(2 * n_1 * n_2 * rho + difference))
                    if unsquared_sign.is_positive is True:
                        temporal_channel = "SUM"
                    elif unsquared_sign.is_negative is True:
                        temporal_channel = "DIFFERENCE"
                    else:
                        raise AssertionError(f"undecided exact sign: {unsquared_sign}")
                    rows.append({
                        "relative_spatial_sign": relative_sign,
                        "canonical_signed_momenta": [n_1, n_2],
                        "first_branch": first_name,
                        "second_branch": second_name,
                        "output_ell": output_ell,
                        "target_branch": target_name,
                        "rho": str(rho),
                        "rho_positive_exact": True,
                        "unsquared_sign": str(unsquared_sign),
                        "admissible_temporal_channel": temporal_channel,
                    })
    return rows


def verify() -> None:
    value = json.loads(CERT.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    for item in value["provenance"]["inputs"].values():
        path = ROOT / item["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == item["sha256"]
    independent = independently_enumerate()
    assert independent == value["candidate_ledger"]["rows"]
    assert len(independent) == 21
    assert len({row["rho"] for row in independent}) == 21
    assert all(row["rho_positive_exact"] for row in independent)
    assert {row["admissible_temporal_channel"] for row in independent} == {"SUM", "DIFFERENCE"}
    classification = value["classification"]
    assert classification["all_positive_candidates_decided_exactly"]
    assert not classification["floating_point_sign_decision_used"]
    assert not classification["projected_source_coefficients_computed"]


if __name__ == "__main__":
    verify()
    print("EINSTEIN_MAXWELL_WEYL_ELL2_TWO_ABS_MOMENTUM_ISOLATED_CANDIDATES independent verification: PASS")
