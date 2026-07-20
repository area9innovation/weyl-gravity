#!/usr/bin/env python3
"""Independent replay of the background-specific spectral shortfall."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERTIFICATE = (
    HERE
    / "certificates/BACKGROUND_SPECIFIC_FIVE_FORM_FACTOR_SPECTRAL_REALIZATION_SHORTFALL.json"
)
SCHEMA = (
    HERE
    / "schema/background-specific-five-form-factor-spectral-realization-shortfall-v1.schema.json"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _as_fraction(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def _derive_geometry() -> tuple[list[Fraction], Fraction, Fraction, Fraction]:
    """Derive Ricci and Weyl invariants from the orthonormal Lie brackets."""

    n = 4
    zero = Fraction(0)
    structure = [[[zero for _ in range(n)] for _ in range(n)] for _ in range(n)]
    for first, second, target, value in (
        (1, 2, 3, Fraction(2)),
        (2, 3, 1, Fraction(1, 2)),
        (3, 1, 2, Fraction(1, 2)),
    ):
        structure[first][second][target] = value
        structure[second][first][target] = -value

    connection = [
        [[zero for _ in range(n)] for _ in range(n)] for _ in range(n)
    ]
    for target in range(n):
        for derivative in range(n):
            for vector in range(n):
                connection[target][derivative][vector] = Fraction(1, 2) * (
                    structure[derivative][vector][target]
                    - structure[vector][target][derivative]
                    + structure[target][derivative][vector]
                )

    riemann = [
        [
            [[zero for _ in range(n)] for _ in range(n)]
            for _ in range(n)
        ]
        for _ in range(n)
    ]
    for target in range(n):
        for vector in range(n):
            for first in range(n):
                for second in range(n):
                    riemann[target][vector][first][second] = sum(
                        (
                            connection[mid][second][vector]
                            * connection[target][first][mid]
                            - connection[mid][first][vector]
                            * connection[target][second][mid]
                            - structure[first][second][mid]
                            * connection[target][mid][vector]
                        )
                        for mid in range(n)
                    )

    ricci = [
        [
            sum(riemann[index][first][index][second] for index in range(n))
            for second in range(n)
        ]
        for first in range(n)
    ]
    if any(ricci[i][j] for i in range(n) for j in range(n) if i != j):
        raise AssertionError("Berger Ricci tensor unexpectedly nondiagonal")
    ricci_diagonal = [ricci[index][index] for index in range(n)]
    scalar = sum(ricci_diagonal)
    ricci_squared = sum(value * value for value in ricci_diagonal)

    schouten = [
        [
            Fraction(1, 2)
            * (
                ricci[first][second]
                - (
                    scalar * Fraction(1, 6)
                    if first == second
                    else Fraction(0)
                )
            )
            for second in range(n)
        ]
        for first in range(n)
    ]
    weyl_squared = Fraction(0)
    for first in range(n):
        for second in range(n):
            for third in range(n):
                for fourth in range(n):
                    delta_13 = Fraction(int(first == third))
                    delta_14 = Fraction(int(first == fourth))
                    delta_23 = Fraction(int(second == third))
                    delta_24 = Fraction(int(second == fourth))
                    weyl = riemann[first][second][third][fourth] - (
                        delta_13 * schouten[fourth][second]
                        - delta_14 * schouten[third][second]
                        - delta_23 * schouten[fourth][first]
                        + delta_24 * schouten[third][first]
                    )
                    weyl_squared += weyl * weyl
    return ricci_diagonal, scalar, ricci_squared, weyl_squared


def verify(payload: dict[str, Any]) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    try:
        Draft202012Validator(schema).validate(payload)
    except ValidationError as error:
        raise ValueError(f"certificate schema validation failed: {error.message}") from error

    assert payload["dependency_tags"] == [
        "LOCAL-ALGEBRAIC",
        "EUCLIDEAN-SPECTRAL",
    ]
    for reference in payload["imports"].values():
        path = ROOT / reference["path"]
        assert path.is_file()
        assert _sha256(path) == reference["sha256"]
        if reference["result_id"] is not None:
            assert json.loads(path.read_text())["result_id"] == reference["result_id"]

    background = payload["candidate_background"]
    assert background["background_id"] == (
        "EUCLIDEAN_SCALAR_FLAT_BERGER_S1_S3_A1_C2"
    )
    ricci, scalar, ricci_squared, weyl_squared = _derive_geometry()
    assert ricci == [
        _as_fraction(value) for value in background["ricci_orthonormal_diagonal"]
    ]
    assert scalar == _as_fraction(background["scalar_curvature"]) == 0
    assert ricci_squared == _as_fraction(background["ricci_squared"]) == 6
    assert weyl_squared == _as_fraction(background["weyl_squared"]) == 12
    assert background["compact"] is True
    assert background["boundary"] == "EMPTY"
    assert background["non_Einstein"] is True
    assert background["non_conformally_flat"] is True
    assert "Agmon ray exp(i*pi/2)" in background["candidate_contour"]

    local = payload["local_scale_rows"]
    assert _as_fraction(local["Wres_K_density_without_(4pi)^-2"]) == (
        Fraction(4, 9) * ricci_squared
    )
    assert _as_fraction(local["Wres_K2_density_without_(4pi)^-2"]) == (
        Fraction(2, 27) * ricci_squared
    )
    assert _as_fraction(
        local["dlogmu_logDet3_density_without_(4pi)^-2"]
    ) == Fraction(22, 54) * ricci_squared

    inventory = {row["background"]: row for row in payload["candidate_inventory"]}
    assert inventory["flat T4"]["Schur_sensitive_curvature_rank"] == 0
    assert inventory["round S4"]["scalar_flat"] is False
    assert inventory["S2(1) x S2(2)"]["scalar_flat"] is False
    berger = inventory[
        "Euclidean scalar-flat Berger S1 x S3 at a=1,c=2"
    ]
    assert berger["scalar_flat"] is True
    assert berger["Schur_sensitive_curvature_rank"] == "NONZERO"
    assert berger["complete_primed_Schur_resolvent"] is False

    receiver = payload["receiver_audit"]
    assert all(
        receiver[key] is True
        for key in (
            "metric_content_addressed",
            "compact_oriented_boundaryless",
            "scalar_flat_exact",
            "nonzero_Ricci_and_Weyl",
            "reference_scale_declared",
        )
    )
    assert all(
        receiver[key] is False
        for key in (
            "complete_primed_resolvent_or_spectral_measure",
            "normalized_zero_mode_projectors",
            "insertion_eigenprojectors_through_third_variation",
            "certified_analytic_continuation_or_tail",
            "five_background_specific_functions_evaluated",
            "special_background_interpolation_used",
        )
    )

    missing = payload["first_missing_spectral_theorem"]
    expected = ROOT / missing["expected_path"]
    assert missing["result_id"] == "SCALAR_FLAT_BERGER_S1_S3_PRIMED_SCHUR_RESOLVENT"
    assert missing["present"] is False
    assert not expected.exists()
    assert len(missing["required_blocks"]) == 7

    theorem = payload["shortfall_theorem"]
    audit = json.loads(
        (
            ROOT
            / payload["imports"]["independent_family_audit"]["path"]
        ).read_text()
    )
    assert theorem["universal_kernel_dimension"] == audit[
        "global_completion_audit"
    ]["universal_combination_kernel_dimension"] == 0
    assert theorem["status"] == "NO_TRACTABLE_REPOSITORY_DATUM_MEETS_RECEIVER"
    assert theorem["expected_resolvent_absent"] is True
    assert theorem["background_specific_evaluation_authorized"] is False
    request = ROOT / theorem["minimal_external_request"]
    assert request.is_file()
    request_payload = json.loads(request.read_text())
    assert request_payload["id"] == "sf:forge-request/scalar-flat-berger-spectral-measure"
    assert request_payload["body"]["state"] == "REQUESTED"

    assert payload["claim_flags"] == {
        "EXACT_SCALAR_FLAT_NONTRIVIAL_COMPACT_CANDIDATE_SELECTED": True,
        "FIRST_MISSING_GLOBAL_SPECTRAL_OBJECT_IDENTIFIED": True,
        "BACKGROUND_SPECIFIC_FIVE_FUNCTION_VALUES_COMPUTED": False,
        "SPECIAL_BACKGROUND_INTERPOLATION_USED": False,
        "UNIVERSAL_TABLE_PROMOTED": False,
        "QME_OR_LORENTZIAN_PROMOTED": False,
    }


def main() -> int:
    verify(json.loads(CERTIFICATE.read_text()))
    print("BACKGROUND-SPECIFIC FIVE-FORM-FACTOR SHORTFALL REPLAY: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
