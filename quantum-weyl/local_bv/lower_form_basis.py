"""Lower-form carrier inventory for the dimension-four AFN0 production run.

The inventory assembles three independently certified inputs:

* the universal Diff towers in the descent database;
* the nonzero intrinsic Euler components and their Diff completions; and
* the explicit ``Box R`` and ``omega Box R`` primitive/current carriers.

This closes forward/reverse coverage for the *current candidate carrier
algebra*.  It deliberately does not call that algebra the exhaustive ambient
local-form basis needed for a complete relative-cohomology quotient.
"""

from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
import hashlib
import json
from pathlib import Path

from .algebra import canonical_sha256


PACKAGE_ROOT = Path(__file__).resolve().parent
REPOSITORY_ROOT = PACKAGE_ROOT.parents[1]
DESCENT_DATABASE_PATH = PACKAGE_ROOT / "descent" / "DESCENT_DATABASE_DIMENSION_FOUR.json"
EULER_CERTIFICATE_PATH = PACKAGE_ROOT / "certificates" / "EULER_TRANSGRESSION_CERTIFICATE.json"
TRIVIALITY_CERTIFICATE_PATH = PACKAGE_ROOT / "certificates" / "TRIVIALITY_CERTIFICATE.json"
CANDIDATE_CERTIFICATE_PATH = (
    PACKAGE_ROOT
    / "certificates"
    / "LOCAL_DIMENSION_FOUR_CANDIDATE_CATALOGUE_CERTIFICATE.json"
)


def _load(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"lower-form dependency is not an object: {path}")
    return payload


def _fraction(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def _universal_coefficient(order: int) -> Fraction:
    if not 0 <= order <= 4:
        raise ValueError("universal contraction order is outside 0,...,4")
    factorial = 1
    for factor in range(2, order + 1):
        factorial *= factor
    return Fraction(-1 if order % 2 else 1, factorial)


def _carrier(
    *,
    source_id: str,
    source_kind: str,
    source_component: str,
    source_hash: str,
    ghost_number: int,
    form_degree: int,
    parity: str,
    contraction_order: int,
    coefficient: Fraction,
    sector: str,
) -> dict[str, object]:
    payload = {
        "carrier_id": (
            f"{sector}:{source_id}:{source_kind}:{source_component}:"
            f"I_XI_{contraction_order}"
        ),
        "sector": sector,
        "source_id": source_id,
        "source_kind": source_kind,
        "source_component": source_component,
        "source_sha256": source_hash,
        "ghost_number": ghost_number + contraction_order,
        "form_degree": form_degree - contraction_order,
        "total_degree": ghost_number + form_degree,
        "parity": parity,
        "contraction_order": contraction_order,
        "coefficient": _fraction(coefficient),
        "verification_status": "HASH_BOUND_SOURCE_AND_BIDEGREE_VERIFIED",
    }
    if payload["form_degree"] < 0:
        raise ValueError("universal contraction exceeds source form degree")
    return {**payload, "carrier_sha256": canonical_sha256(payload)}


def _orbit(
    *,
    source_id: str,
    source_kind: str,
    source_component: str,
    source_hash: str,
    ghost_number: int,
    form_degree: int,
    parity: str,
    sector: str,
) -> list[dict[str, object]]:
    return [
        _carrier(
            source_id=source_id,
            source_kind=source_kind,
            source_component=source_component,
            source_hash=source_hash,
            ghost_number=ghost_number,
            form_degree=form_degree,
            parity=parity,
            contraction_order=order,
            coefficient=_universal_coefficient(order),
            sector=sector,
        )
        for order in range(form_degree + 1)
    ]


def _universal_candidate_carriers(
    database: dict[str, object],
    candidate_certificate: dict[str, object],
) -> list[dict[str, object]]:
    if not (
        candidate_certificate.get("result_id")
        == "LOCAL_DIMENSION_FOUR_CANDIDATE_CATALOGUE_CERTIFICATE"
        and candidate_certificate.get("checks", {}).get(
            "strict_density_diff_descent"
        )
        == "VERIFIED"
    ):
        raise ValueError("candidate catalogue dependency is incomplete")
    catalogues = candidate_certificate.get("catalogues", {})
    candidates = {
        *catalogues.get("counterterm_candidate_ids", []),
        *catalogues.get("anomaly_candidate_ids", []),
    }
    entries = database.get("entries")
    if not isinstance(entries, list):
        raise ValueError("descent database has no entry list")
    if {str(entry.get("representative_id")) for entry in entries} != candidates:
        raise ValueError("descent database and candidate catalogue disagree")
    carriers: list[dict[str, object]] = []
    for entry in entries:
        source_id = str(entry["representative_id"])
        expected = _orbit(
            source_id=source_id,
            source_kind="TOP_REPRESENTATIVE",
            source_component="a_top",
            source_hash=str(entry["basis_manifest_hash"]),
            ghost_number=int(entry["ghost_number"]),
            form_degree=int(entry["form_degree"]),
            parity=str(entry["parity"]),
            sector="COCYCLE",
        )
        tower = entry.get("diff_tower")
        if not isinstance(tower, list) or len(tower) != len(expected):
            raise ValueError(f"universal Diff tower length drifted: {source_id}")
        for order, (stored, generated) in enumerate(zip(tower, expected)):
            if not (
                stored.get("ghost_number") == generated["ghost_number"]
                and stored.get("form_degree") == generated["form_degree"]
                and stored.get("coefficient") == _fraction(_universal_coefficient(order))
            ):
                raise ValueError(f"universal Diff tower row drifted: {source_id}")
        carriers.extend(expected)
    return carriers


def _intrinsic_euler_carriers(
    database: dict[str, object],
    euler_certificate: dict[str, object],
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    entries = {
        str(entry["representative_id"]): entry
        for entry in database["entries"]
    }
    if not (
        euler_certificate.get("result_id") == "EULER_TRANSGRESSION_CERTIFICATE"
        and euler_certificate.get("checks", {}).get(
            "omega_E4_intrinsic_descent_continuation"
        )
        == "NONTRIVIAL_COMPLETE"
    ):
        raise ValueError("Euler intrinsic dependency is incomplete")

    carriers: list[dict[str, object]] = []
    structural_zeros: list[dict[str, object]] = []

    counterterm_rows = entries["CT_E4"]["intrinsic_tower"]
    if not (
        len(counterterm_rows) == 1
        and counterterm_rows[0]["ghost_number"] == 1
        and counterterm_rows[0]["form_degree"] == 3
    ):
        raise ValueError("Euler counterterm transgression row drifted")
    counterterm_hash = canonical_sha256(counterterm_rows[0])
    carriers.extend(
        _orbit(
            source_id="CT_E4",
            source_kind="INTRINSIC_EULER_COMPONENT",
            source_component="theta_E",
            source_hash=counterterm_hash,
            ghost_number=1,
            form_degree=3,
            parity="even",
            sector="COCYCLE",
        )
    )

    expansion = euler_certificate["euler_intrinsic_transgression"][
        "ordinary_bidegree_expansion"
    ]
    if not (
        expansion.get("result_id") == "EULER_INTRINSIC_BIDEGREE_EXPANSION"
        and expansion.get("claim_boundary", {}).get("intrinsic_tower_status")
        == "COMPLETE"
    ):
        raise ValueError("embedded Euler ordinary-bidegree expansion is incomplete")
    components = {
        (int(row["ghost_number"]), int(row["form_degree"])): row
        for row in expansion["components"]
    }
    database_rows = entries["ANOM_OMEGA_E4"]["intrinsic_tower"]
    if {(int(row["ghost_number"]), int(row["form_degree"])) for row in database_rows} != {
        (2, 3),
        (3, 2),
        (4, 1),
        (5, 0),
    }:
        raise ValueError("Euler anomaly intrinsic bidegree coverage drifted")
    for bidegree in ((2, 3), (3, 2), (4, 1), (5, 0)):
        component = components[bidegree]
        if component["term_count"] == 0:
            zero_payload = {
                "source_id": "ANOM_OMEGA_E4",
                "ghost_number": bidegree[0],
                "form_degree": bidegree[1],
                "reason": component["component_status"],
                "verification_status": "STRUCTURALLY_ZERO_VERIFIED",
            }
            structural_zeros.append(
                {**zero_payload, "zero_sha256": canonical_sha256(zero_payload)}
            )
            continue
        carriers.extend(
            _orbit(
                source_id="ANOM_OMEGA_E4",
                source_kind="INTRINSIC_EULER_COMPONENT",
                source_component=f"a{bidegree[0]}{bidegree[1]}",
                source_hash=canonical_sha256(component),
                ghost_number=bidegree[0],
                form_degree=bidegree[1],
                parity="even",
                sector="COCYCLE",
            )
        )
    return carriers, structural_zeros


def _boundary_carriers(
    triviality_certificate: dict[str, object],
) -> list[dict[str, object]]:
    if triviality_certificate.get("result_id") != "TRIVIALITY_CERTIFICATE":
        raise ValueError("triviality dependency has the wrong result id")
    rows = triviality_certificate.get("trivializations", {})
    if not all(rows.get(key, {}).get("class_status") == "EXACT" for key in (
        "CT_BOX_R",
        "ANOM_OMEGA_BOX_R",
    )):
        raise ValueError("Box R trivialization rows are incomplete")
    counterterm = rows["CT_BOX_R"]
    anomaly = rows["ANOM_OMEGA_BOX_R"]
    carriers = _orbit(
        source_id="CT_BOX_R",
        source_kind="EXACT_CURRENT",
        source_component="nabla_R",
        source_hash=canonical_sha256(counterterm["primitive"]),
        ghost_number=0,
        form_degree=3,
        parity="even",
        sector="BOUNDARY",
    )
    carriers.extend(
        _orbit(
            source_id="ANOM_OMEGA_BOX_R",
            source_kind="BRST_PRIMITIVE",
            source_component="R_squared",
            source_hash=canonical_sha256(
                {
                    "primitive": anomaly["primitive"],
                    "coefficient": anomaly["primitive_coefficient"],
                }
            ),
            ghost_number=0,
            form_degree=4,
            parity="even",
            sector="BOUNDARY",
        )
    )
    carriers.extend(
        _orbit(
            source_id="ANOM_OMEGA_BOX_R",
            source_kind="EXACT_CURRENT",
            source_component="R_domega_minus_omega_dR",
            source_hash=canonical_sha256(anomaly["current"]),
            ghost_number=1,
            form_degree=3,
            parity="even",
            sector="BOUNDARY",
        )
    )
    return carriers


def _bidegree_inventory(
    carriers: list[dict[str, object]],
) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str, int, int], int] = {}
    for carrier in carriers:
        key = (
            str(carrier["sector"]),
            str(carrier["parity"]),
            int(carrier["ghost_number"]),
            int(carrier["form_degree"]),
        )
        grouped[key] = grouped.get(key, 0) + 1
    return [
        {
            "sector": sector,
            "parity": parity,
            "ghost_number": ghost_number,
            "form_degree": form_degree,
            "total_degree": ghost_number + form_degree,
            "carrier_count": count,
        }
        for (sector, parity, ghost_number, form_degree), count in sorted(grouped.items())
    ]


@lru_cache(maxsize=1)
def lower_form_carrier_analysis() -> dict[str, object]:
    database = _load(DESCENT_DATABASE_PATH)
    euler_certificate = _load(EULER_CERTIFICATE_PATH)
    triviality_certificate = _load(TRIVIALITY_CERTIFICATE_PATH)
    candidate_certificate = _load(CANDIDATE_CERTIFICATE_PATH)
    universal = _universal_candidate_carriers(database, candidate_certificate)
    intrinsic, structural_zeros = _intrinsic_euler_carriers(
        database, euler_certificate
    )
    boundaries = _boundary_carriers(triviality_certificate)
    carriers = sorted(
        [*universal, *intrinsic, *boundaries], key=lambda row: row["carrier_id"]
    )
    ids = [str(row["carrier_id"]) for row in carriers]
    if len(ids) != len(set(ids)):
        raise AssertionError("lower-form carrier ids are not unique")
    if (len(universal), len(intrinsic), len(boundaries), len(carriers)) != (
        40,
        11,
        13,
        64,
    ):
        raise AssertionError("lower-form carrier inventory count drifted")
    lower_count = sum(int(row["form_degree"]) < 4 for row in carriers)
    if lower_count != 55:
        raise AssertionError("strict lower-form carrier count drifted")

    source_artifacts = []
    for path in (
        DESCENT_DATABASE_PATH,
        EULER_CERTIFICATE_PATH,
        TRIVIALITY_CERTIFICATE_PATH,
        CANDIDATE_CERTIFICATE_PATH,
    ):
        payload = _load(path)
        source_artifacts.append(
            {
                "path": str(path.relative_to(REPOSITORY_ROOT)),
                "result_id": payload["result_id"],
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "canonical_sha256": canonical_sha256(payload),
            }
        )

    payload = {
        "result_id": "AFN0_LOWER_FORM_CARRIER_PRECERTIFICATE",
        "result_state": "CANDIDATE_AND_EXACT_BOUNDARY_CARRIERS_COMPLETE_AMBIENT_BASIS_OPEN",
        "classical_commit": "UNFROZEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "scope_label": "AFN0_ONLY",
        "declared_carrier_algebra": {
            "generators": [
                "certified dimension-four top representatives",
                "universal contractions i_xi^k/k!",
                "nonzero intrinsic Euler components",
                "explicit Box R and omega Box R primitives and currents",
            ],
            "coverage": "FORWARD_AND_REVERSE_COMPLETE_FOR_DECLARED_CARRIER_ALGEBRA",
            "ambient_local_form_basis": "IN_PROGRESS",
        },
        "source_artifacts": source_artifacts,
        "counts": {
            "universal_candidate_carriers": len(universal),
            "intrinsic_euler_carriers": len(intrinsic),
            "exact_boundary_carriers": len(boundaries),
            "all_carriers": len(carriers),
            "strict_lower_form_carriers": lower_count,
            "structurally_zero_euler_components": len(structural_zeros),
        },
        "bidegree_inventory": _bidegree_inventory(carriers),
        "carriers": carriers,
        "structural_zeros": structural_zeros,
        "checks": {
            "descent_database_candidate_set_agreement": "VERIFIED",
            "universal_diff_coefficients_and_bidegrees": "VERIFIED",
            "intrinsic_euler_component_coverage": "VERIFIED",
            "intrinsic_euler_universal_diff_completion": "VERIFIED",
            "exact_BoxR_boundary_carriers": "VERIFIED",
            "carrier_ids_unique": "VERIFIED",
            "forward_reverse_declared_carrier_span_agreement": "VERIFIED",
        },
        "total_complex_gates": {
            "LOWER_FORM_CANDIDATE_CARRIER_COVERAGE": "COMPLETE",
            "LOWER_FORM_EXACT_BOUNDARY_CARRIER_COVERAGE": "COMPLETE",
            "LOWER_FORM_AMBIENT_COCYCLE_BASIS_EXHAUSTIVE": "IN_PROGRESS",
            "LOWER_FORM_AMBIENT_BOUNDARY_BASIS_EXHAUSTIVE": "IN_PROGRESS",
            "PRODUCTION_Q_DH_MATRICES": "NOT_COMPUTED",
            "TOTAL_COMPLEX_EXHAUSTIVE": "NOT_COMPUTED",
        },
        "claim_boundary": [
            "complete means complete only for the explicitly declared candidate and exact-boundary carrier algebra",
            "mixed Weyl-Diff, unrestricted ghost-derivative, and additional generalized-connection ambient monomials remain to be generated",
            "no relative class or complete nontriviality witness is promoted",
        ],
    }
    return {**payload, "analysis_sha256": canonical_sha256(payload)}
