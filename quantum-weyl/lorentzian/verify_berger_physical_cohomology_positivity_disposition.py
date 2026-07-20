#!/usr/bin/env python3
"""Independent verifier for the physical positivity disposition."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

try:
    from local_bv.schema_validation import validate_instance
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from local_bv.schema_validation import validate_instance


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUTPUT = (
    HERE
    / "certificates/BERGER_PHYSICAL_COHOMOLOGY_POSITIVITY_DISPOSITION.json"
)
SCHEMA = (
    HERE
    / "schema/berger-physical-cohomology-positivity-disposition-v1.schema.json"
)
DEPENDENCIES = {
    "retained26_Ward_reduction": (
        HERE / "certificates/BERGER_RETAINED26_HADAMARD_WARD_REDUCTION.json"
    ),
    "regular_graph_obstruction": (
        HERE
        / "certificates/"
        "BERGER_REGULAR_GRAPH_INTERTWINER_OBSTRUCTION_AND_ENDPOINT_DESCENT.json"
    ),
    "rank40_auxiliary_covariance": (
        HERE
        / "certificates/"
        "BERGER_FULL_DILATION_HADAMARD_KREIN_CCR_COVARIANCE.json"
    ),
    "canonical_restriction_audit": (
        HERE
        / "certificates/BERGER_DILATION_TO_RETAINED26_RESTRICTION_AUDIT.json"
    ),
    "graded_state_space_contract": (
        HERE / "certificates/BERGER_GRADED_CAUSAL_STATE_SPACE_CONTRACT.json"
    ),
    "curvature_CCR_algebra": (
        HERE / "certificates/CURVATURE_IMAGE_PRESYMPLECTIC_CCR_ALGEBRA.json"
    ),
    "reduced_EAL_Krein_ledger": (
        ROOT / "analytic_completion/certificates/one_particle_krein.json"
    ),
}
SOURCE_PATHS = (
    "berger_physical_cohomology_positivity_disposition.py",
    "berger_physical_cohomology_positivity_disposition_certificate.py",
    "verify_berger_physical_cohomology_positivity_disposition.py",
    "schema/berger-physical-cohomology-positivity-disposition-v1.schema.json",
    "tests/test_berger_physical_cohomology_positivity_disposition.py",
    "../reports/berger-physical-cohomology-positivity-disposition.md",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _assert_payload(payload: dict[str, Any]) -> None:
    """Verify the conclusion without importing the producing implementation."""

    if payload["result_id"] != "BERGER_PHYSICAL_COHOMOLOGY_POSITIVITY_DISPOSITION":
        raise ValueError("wrong result id")
    if payload["dependency_tags"] != ["REDUCED-MODE", "LORENTZIAN-CAUSAL"]:
        raise ValueError("wrong dependency boundary")
    if payload["science_forge"]["stop_condition_status"] != (
        "SHORTFALL_PRECONDITION_NOT_MET"
    ):
        raise ValueError("wrong Science Forge disposition")

    dependencies = {name: _load(path) for name, path in DEPENDENCIES.items()}
    for name, path in DEPENDENCIES.items():
        reference = payload["dependency_refs"][name]
        if reference["sha256"] != _sha256(path):
            raise ValueError(f"dependency drift: {name}")

    ward_flags = dependencies["retained26_Ward_reduction"]["claim_flags"]
    if not (
        ward_flags["BERGER_26_ROW_HADAMARD_EXACT_CCR_CANDIDATE"] is True
        and ward_flags["BERGER_26_ROW_WARD_DEFECT_SMOOTH"] is True
        and ward_flags["BERGER_SMOOTH_Q26_WARD_COMPLETION"] is False
        and ward_flags["BERGER_26_ROW_BRST_HADAMARD"] is False
    ):
        raise ValueError("retained Ward premise is not fail-closed")
    graph_flags = dependencies["regular_graph_obstruction"]["claim_flags"]
    if not (
        graph_flags["BERGER_REGULAR_GRAPH_INTERTWINER_CLASS_COMPLETE"] is True
        and graph_flags[
            "BERGER_NONDEGENERATE_REGULAR_GRAPH_INTERTWINER_EXISTS"
        ]
        is False
    ):
        raise ValueError("graph obstruction premise failed")
    restriction_flags = dependencies["canonical_restriction_audit"][
        "claim_flags"
    ]
    if restriction_flags[
        "BERGER_CANONICAL_DILATION_SUMMAND_RESTRICTION_PRESERVES_CCR"
    ] is not False:
        raise ValueError("canonical restriction premise failed")
    if dependencies["rank40_auxiliary_covariance"][
        "transported_covariances"
    ]["full"][
        "state_space_status"
    ] != "INDEFINITE_KREIN_QUASIFREE_FUNCTIONAL_NOT_A_POSITIVE_STATE":
        raise ValueError("auxiliary Krein premise failed")
    if dependencies["graded_state_space_contract"][
        "positivity_and_krein_policy"
    ]["full_BV_positive_state"] != "NOT_CLAIMED":
        raise ValueError("graded positivity policy drift")
    if dependencies["curvature_CCR_algebra"]["claim_flags"][
        "CURVATURE_HADAMARD_STATE_CONSTRUCTED"
    ] is not False:
        raise ValueError("curvature Hadamard premise failed")
    if "not a distributional completion" not in dependencies[
        "reduced_EAL_Krein_ledger"
    ]["scope_guards"]:
        raise ValueError("reduced carrier scope drift")

    replay = payload["BRST_representative_change"]
    required_formulae = {
        "sector": "even ghost-number-zero homogeneous representatives",
        "first_exact_variation": (
            "B_Omega(f+q26 u,h)-B_Omega(f,h)="
            "<u,(q26sharp Omega26_plus+Omega26_plus q26)h>"
            "=<u,W26[H26_plus,q26]h> for q26 h=0"
        ),
        "second_exact_variation": (
            "B_Omega(f,h+q26 v)-B_Omega(f,h)="
            "<f,(q26sharp Omega26_plus+Omega26_plus q26)v>"
            "=<f,W26[H26_plus,q26]v> for q26 f=0"
        ),
    }
    if any(replay.get(key) != value for key, value in required_formulae.items()):
        raise ValueError("representative-change formula drift")
    if (
        replay["ward_defect_certified_pairing_null"] is not False
        or replay["pairing_descends"] is not False
        or replay["all_pass"] is not True
        or not all(replay["checks"].values())
    ):
        raise ValueError("uncertified Ward descent was promoted")

    rows = {row["carrier"]: row for row in payload["carrier_disposition"]}
    expected_carriers = {
        "retained_26_exact_CCR_candidate",
        "rank_40_auxiliary_Hermitian_dilation",
        "vacuum_cylinder_reduced_E_A_L_Krein_space",
        "curvature_image_CCR_algebra",
    }
    if set(rows) != expected_carriers:
        raise ValueError("declared carrier disposition is incomplete")
    if rows["retained_26_exact_CCR_candidate"]["physical_form"] != "UNDEFINED":
        raise ValueError("retained physical form was silently promoted")
    if rows["rank_40_auxiliary_Hermitian_dilation"]["physical_form"] != (
        "NO_CERTIFIED_MAP"
    ):
        raise ValueError("auxiliary form was called physical")
    if rows["vacuum_cylinder_reduced_E_A_L_Krein_space"][
        "positivity_status"
    ] != "REDUCED_MODE_KREIN_ONLY":
        raise ValueError("reduced sign crossed its carrier boundary")
    if rows["curvature_image_CCR_algebra"]["physical_form"] != (
        "NO_HADAMARD_TWO_POINT_FUNCTION"
    ):
        raise ValueError("curvature state was silently supplied")

    physical = payload["physical_cohomology"]
    if (
        physical["candidate_pairing_descent"] != "NOT_CERTIFIED"
        or physical["induced_sesquilinear_form"] != "UNDEFINED"
        or physical["complex_structure_classification"] != "NOT_ACTIVATED"
        or physical["positivity_verdict"] != "NOT_ACTIVATED_BEFORE_WARD_DESCENT"
    ):
        raise ValueError("physical positivity was over-promoted")
    permitted_true = {
        "BERGER_AUXILIARY_SIGNATURE_NOT_PHYSICAL_NORM",
        "BERGER_REDUCED_EAL_SIGN_NOT_BERGER_PHYSICAL_NORM",
    }
    flags = payload["claim_flags"]
    if {name for name, value in flags.items() if value is True} != permitted_true:
        raise ValueError("claim flags exceed the disposition")

    manifest = {path: _sha256(HERE / path) for path in SOURCE_PATHS}
    if payload["provenance"]["source_manifest"] != manifest:
        raise ValueError("source manifest drift")
    manifest_hash = hashlib.sha256(
        json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    if payload["provenance"]["source_manifest_sha256"] != manifest_hash:
        raise ValueError("source manifest hash drift")


def verify() -> dict[str, Any]:
    payload = _load(OUTPUT)
    schema_errors = validate_instance(payload, _load(SCHEMA))
    if schema_errors:
        raise ValueError(f"physical positivity schema failed: {schema_errors}")
    _assert_payload(payload)

    mutant = deepcopy(payload)
    mutant["claim_flags"]["BERGER_PHYSICAL_OBSERVABLE_POSITIVITY"] = True
    try:
        _assert_payload(mutant)
    except ValueError:
        pass
    else:
        raise ValueError("physical positivity overpromotion was accepted")

    mutant = deepcopy(payload)
    mutant["BRST_representative_change"][
        "ward_defect_certified_pairing_null"
    ] = True
    try:
        _assert_payload(mutant)
    except ValueError:
        pass
    else:
        raise ValueError("pairing-null Ward mutant was accepted")
    return payload


def main() -> int:
    verify()
    print("BERGER PHYSICAL POSITIVITY independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
