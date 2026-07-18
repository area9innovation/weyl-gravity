#!/usr/bin/env python3
"""Independent replay of the Weyl-graviton BoxR scheme conversion."""

from __future__ import annotations

from copy import deepcopy
from fractions import Fraction
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = HERE / "certificates/WEYL_GRAVITON_BOX_R_SCHEME_CONVERSION.json"
SCHEMA = HERE / "schema/weyl-graviton-box-r-scheme-conversion-v1.schema.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _fraction(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def _linear(value: dict[str, object]) -> tuple[Fraction, Fraction]:
    return _fraction(value["rational"]), _fraction(value["log_3_over_2"])


def verify() -> dict[str, object]:
    value = json.loads(OUTPUT.read_text())
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(value)
    for record in value["dependencies"].values():
        path = ROOT / record["path"]
        if not path.is_file() or _sha256(path) != record["sha256"]:
            raise ValueError(f"BoxR dependency drifted: {path}")

    rows = value["heat_kernel_row_reconstruction"]
    h = _linear(rows["tensor_H"])
    y = _linear(rows["gauge_weight_Y"])
    m = _linear(rows["diffeomorphism_ghost_M"])
    raw = tuple(2 * h[i] - y[i] - 2 * m[i] for i in range(2))
    if raw != (Fraction(-159, 80), Fraction(7, 2)):
        raise ValueError("BoxR H/Y/M independent replay failed")

    conversion = _linear(
        value["repository_scheme_conversion"]["raw_to_BoxR_zero_counterterm"]
    )
    if conversion != tuple(entry / 12 for entry in raw):
        raise ValueError("BoxR primitive conversion replay failed")

    raw_r2 = _linear(
        value["anomaly_induced_local_R2_cross_check"]["raw_scheme_local_R2_coefficient"]
    )
    target_r2 = _linear(
        value["anomaly_induced_local_R2_cross_check"]["repository_BoxR_zero_coefficient"]
    )
    if (
        raw_r2 != (Fraction(391, 960), Fraction(-7, 24))
        or tuple(raw_r2[i] + conversion[i] for i in range(2))
        != (Fraction(29, 120), Fraction())
        or target_r2 != (Fraction(29, 120), Fraction())
    ):
        raise ValueError("BoxR anomaly-induced R2 cross-check failed")

    witness = value["exact_nonzero_sign_witness"]
    lower = _fraction(witness["lower_bound"])
    upper = _fraction(witness["upper_bound"])
    if not (
        lower == Fraction(77, 192)
        and upper == Fraction(391, 960)
        and Fraction(7, 2) * upper - Fraction(159, 80) < 0
    ):
        raise ValueError("BoxR sign witness replay failed")
    return value


def mutation_guards(value: dict[str, object]) -> None:
    for key in (
        "ABSOLUTE_DRESSED_RHAT2_NORMALIZATION_FIXED",
        "NONLOCAL_R2_FORM_FACTOR_COMPUTED",
        "COMPLETE_RENORMALIZED_Q1_SUPPLIED",
        "RESIDUAL_TRANSFER_AUTHORIZED",
    ):
        mutant = deepcopy(value)
        mutant["claim_flags"][key] = True
        try:
            Draft202012Validator(json.loads(SCHEMA.read_text())).validate(mutant)
        except Exception:
            continue
        raise ValueError(f"BoxR schema accepted forbidden promotion: {key}")


def main() -> None:
    value = verify()
    mutation_guards(value)
    print("Weyl-graviton BoxR scheme conversion independent replay: PASS")


if __name__ == "__main__":
    main()
