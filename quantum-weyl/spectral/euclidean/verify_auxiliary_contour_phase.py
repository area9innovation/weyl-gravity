"""Independent verifier for the standard TT auxiliary contour certificate."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERTIFICATE = HERE / "certificates/STANDARD_TT_AUXILIARY_CONTOUR_PHASE.json"
SCHEMA = HERE / "schema/standard-tt-auxiliary-contour-phase-v1.schema.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _fraction(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def verify() -> dict:
    value = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    completion = value["finite_mode_identity"]["completion"]
    for coefficient in completion["completion_residual"].values():
        if _fraction(coefficient["real"]) != 0 or _fraction(coefficient["imaginary"]) != 0:
            raise ValueError("auxiliary square completion residual drifted")
    rays = value["convergence_rays"]
    if (
        rays["canonical"]["Re_exp_2i_theta_sign"] != -1
        or rays["canonical"]["absolutely_convergent"] is not True
        or rays["real_axis_negative_control"]["Re_exp_2i_theta_sign"] != 1
        or rays["real_axis_negative_control"]["absolutely_convergent"] is not False
        or rays["stokes_boundary_control"]["Re_exp_2i_theta_sign"] != 0
    ):
        raise ValueError("auxiliary convergence-ray classification drifted")
    mutant = value["negative_controls"]["wrong_auxiliary_sign"]
    mutant_y2 = mutant["completion_residual"]["y2"]
    if (
        mutant["completion_verified"] is not False
        or _fraction(mutant_y2["real"]) != -1
        or _fraction(mutant_y2["imaginary"]) != 0
    ):
        raise ValueError("auxiliary-sign mutation was not exposed")
    contour = value["oriented_normalized_contour"]
    if (
        contour["residual_modewise_phase"] != "PLUS_ONE_BY_ORIENTED_NORMALIZED_MEASURE"
        or contour["background_dependent_log_coefficient"]
        != "ZERO_FOR_THE_NORMALIZED_ALGEBRAIC_IDENTITY_BLOCK"
    ):
        raise ValueError("normalized contour phase drifted")
    for relative, digest in value["provenance"]["source_sha256"].items():
        if _sha256(ROOT / relative) != digest:
            raise ValueError(f"auxiliary contour source hash drifted: {relative}")
    return value


def main() -> int:
    verify()
    print("independent standard TT auxiliary contour verifier: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
