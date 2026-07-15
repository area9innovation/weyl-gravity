"""Fail-closed evidence import for the partial Berger clock-sector SDR.

The classical theorem contracts exactly eight minimal clock rows.  It does
not yet export portable operator entries suitable for the ND2 assembler.
This importer therefore verifies the theorem, its coverage, its fingerprints,
and its scope while deliberately refusing to manufacture a complete
``classical_contraction`` artifact.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import subprocess
from typing import Any

try:
    from .total_d_disposition import validate_total_d_disposition
except ImportError:
    from total_d_disposition import validate_total_d_disposition


TRANSFER_ROOT = Path(__file__).resolve().parent
ROOT = TRANSFER_ROOT.parents[1]
CLASSICAL_ROOT = ROOT / "d_quotient_classical"
THEOREM_COMMIT = "f6e8a2b0802b99f323382e4b7d494a41ca571e47"
REGISTRATION_COMMIT = "5530cb209359ba158aa8dda4743c6c9c9b171985"
CLASSICAL_CERTIFICATE = (
    CLASSICAL_ROOT / "certificates" / "BERGER_MINIMAL_BV_CLOCK_SDR.json"
)
CLASSICAL_SCHEMA = (
    CLASSICAL_ROOT / "schema" / "berger-minimal-bv-clock-sdr-v1.schema.json"
)
CLASSICAL_PRODUCER = (
    CLASSICAL_ROOT / "backreacted_clock" / "berger_minimal_bv_clock_sdr.py"
)
CLASSICAL_INDEPENDENT_VERIFIER = (
    CLASSICAL_ROOT
    / "backreacted_clock"
    / "verify_berger_minimal_bv_clock_sdr_independent.py"
)
CLASSICAL_TEST = (
    CLASSICAL_ROOT
    / "backreacted_clock"
    / "tests"
    / "test_berger_minimal_bv_clock_sdr.py"
)
CLASSICAL_REPORT = (
    CLASSICAL_ROOT / "reports" / "berger-minimal-bv-clock-sdr.md"
)
PROGRAMME_CONTRIBUTION = (
    ROOT
    / "d_quotient_programme"
    / "contributions"
    / "classical-berger-minimal-bv-clock-sdr.json"
)
PROGRAMME_STATUS = (
    ROOT
    / "d_quotient_programme"
    / "certificates"
    / "D_QUOTIENT_PROGRAMME_STATUS.json"
)
TOTAL_D_CERTIFICATE = (
    TRANSFER_ROOT / "certificates" / "BERGER_TOTAL_D_DISPOSITION.json"
)

SCHEMA_ID = "quantum-weyl-berger-clock-partial-sdr-import-v1"
EXPECTED_FINGERPRINTS = {
    "canonical_map",
    "canonical_pairing",
    "field_map",
    "fixture_field_map",
    "homotopy",
    "new_gauge",
    "old_gauge",
    "omega_clock",
    "q_clock",
}
EXPECTED_CLOCK_ROWS = (
    "tau",
    "sigma",
    "Theta",
    "R",
    "Theta*",
    "R*",
    "tau*",
    "sigma*",
)
EXPECTED_Q1_MAPS = (
    "q1(tau)=Theta",
    "q1(sigma)=-R",
    "q1(Theta*)=-tau*",
    "q1(R*)=sigma*",
)
EXPECTED_HOMOTOPY_MAPS = (
    "s(Theta)=tau",
    "s(R)=-sigma",
    "s(tau*)=-Theta*",
    "s(sigma*)=R*",
)
EXPECTED_IDENTITIES = {
    "q1^2=0",
    "q1 s+s q1=1_clock",
    "s^2=0",
    "q1^T Omega+Omega q1=0",
    "s^T Omega+Omega s=0",
}
PORTABLE_SCHEMA_ID = "quantum-weyl-berger-clock-partial-sdr-portable-v1"
PORTABLE_OPERATOR_IDS = {
    "field_map",
    "field_map_inverse",
    "canonical_cotangent_lift",
    "q1_clock",
    "s_clock",
    "iota_cl_partial",
    "pi_cl_partial",
    "cyclic_pairing_clock",
}
PORTABLE_BASE_CHECKS = {
    "field_map_inverse",
    "canonical_cotangent_lift",
    "q1_squared_zero",
    "q1_iota_chain_map",
    "pi_q1_chain_map",
    "pi_iota_identity",
    "partial_contraction_identity",
    "s_squared_zero",
    "q1_cyclicity",
    "s_cyclicity",
    "row_completeness",
    "support_locality",
}
_NUMERATOR = re.compile(r"^-?[0-9]+(\*[a-zA-Z_][a-zA-Z0-9_]*(\^-?[0-9]+)?)*$")
_DENOMINATOR = re.compile(r"^[1-9][0-9]*(\*[a-zA-Z_][a-zA-Z0-9_]*(\^[1-9][0-9]*)?)*$")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _require_hash(value: object, label: str) -> str:
    if (
        not isinstance(value, str)
        or len(value) != 64
        or any(char not in "0123456789abcdef" for char in value)
    ):
        raise ValueError(f"{label} hash is invalid")
    return value


def _require_fields(value: object, fields: set[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != fields:
        raise ValueError(f"{label} has the wrong field set")
    return value


def _load(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot load Berger clock SDR input: {path}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"Berger clock SDR input is not an object: {path}")
    return value


def _git_blob(relative: str, *, commit: str) -> bytes:
    prefix = subprocess.run(
        ["git", "rev-parse", "--show-prefix"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    result = subprocess.run(
        ["git", "show", f"{commit}:{prefix}{relative}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    return result.stdout


def _git_blob_sha256(relative: str, *, commit: str) -> str:
    return hashlib.sha256(_git_blob(relative, commit=commit)).hexdigest()


def _load_git_json(relative: str, *, commit: str) -> dict[str, Any]:
    try:
        value = json.loads(_git_blob(relative, commit=commit))
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid pinned JSON at {commit}: {relative}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"pinned JSON is not an object at {commit}: {relative}")
    return value


def _validate_classical_theorem(value: object) -> dict[str, Any]:
    payload = _require_fields(
        value,
        {
            "schema",
            "result_id",
            "setting_id",
            "phase_space_id",
            "claim_status",
            "dependency_tags",
            "background_inputs",
            "field_coordinates",
            "gauge_incidence",
            "canonical_antifield_lift",
            "minimal_row_layout",
            "clock_block",
            "hessian_split_argument",
            "sdr",
            "operator_fingerprints",
            "rational_fixture",
            "flags",
            "next_gate",
            "not_established",
            "claim_boundary",
        },
        "classical Berger clock SDR",
    )
    if (
        payload["schema"] != "pure-weyl-berger-minimal-bv-clock-sdr-v1"
        or payload["result_id"] != "BERGER_MINIMAL_BV_CLOCK_SDR"
        or payload["setting_id"]
        != "compact_positive_berger_clock_fixed_coupling_linearized"
        or payload["phase_space_id"]
        != "positive_berger_fixed_coupling_linearized_solutions"
        or payload["claim_status"] != "CERTIFIED_MINIMAL_CLOCK_SECTOR_SDR"
        or payload["dependency_tags"] != ["LOCAL-ALGEBRAIC"]
    ):
        raise ValueError("classical Berger clock SDR identity or scope drifted")

    block = _require_fields(
        payload["clock_block"],
        {
            "ordered_rows",
            "q1_maps",
            "homotopy_maps",
            "identities",
            "minimal_clock_rows_complete",
        },
        "classical Berger clock block",
    )
    if tuple(block["ordered_rows"]) != EXPECTED_CLOCK_ROWS:
        raise ValueError("classical Berger clock row order drifted")
    if tuple(block["q1_maps"]) != EXPECTED_Q1_MAPS:
        raise ValueError("classical Berger clock q1 maps drifted")
    if tuple(block["homotopy_maps"]) != EXPECTED_HOMOTOPY_MAPS:
        raise ValueError("classical Berger clock homotopy maps drifted")
    if set(block["identities"]) != EXPECTED_IDENTITIES or len(block["identities"]) != 5:
        raise ValueError("classical Berger clock identities drifted")
    if block["minimal_clock_rows_complete"] is not True:
        raise ValueError("classical Berger clock rows are incomplete")

    sdr = _require_fields(
        payload["sdr"],
        {
            "full_minimal_dimension",
            "contracted_clock_dimension",
            "retained_minimal_dimension",
            "projection",
            "inclusion",
            "identity",
            "support_preservation",
            "support_categories",
        },
        "classical Berger clock SDR ledger",
    )
    if (
        sdr["full_minimal_dimension"] != 34
        or sdr["contracted_clock_dimension"] != 8
        or sdr["retained_minimal_dimension"] != 26
        or sdr["identity"] != "i p=1-q1 s-s q1"
        or sdr["support_categories"] != ["compact", "spacelike-compact", "smooth"]
    ):
        raise ValueError("classical Berger clock SDR coverage drifted")

    flags = _require_fields(
        payload["flags"],
        {
            "minimal_clock_field_ghost_rows_complete",
            "minimal_clock_antifield_identity_rows_complete",
            "canonical_antifield_transformation_exact",
            "support_local_clock_SDR_exact",
            "retained_dressed_metric_q1_coefficients_complete",
            "gauge_fixed_nonminimal_rows_complete",
            "retained_operator_stability_proved",
            "causal_green_homotopy_constructed",
            "full_Berger_clock_BV_theorem",
        },
        "classical Berger clock SDR flags",
    )
    proved = {
        "minimal_clock_field_ghost_rows_complete",
        "minimal_clock_antifield_identity_rows_complete",
        "canonical_antifield_transformation_exact",
        "support_local_clock_SDR_exact",
    }
    open_flags = set(flags) - proved
    if any(flags[key] is not True for key in proved) or any(
        flags[key] is not False for key in open_flags
    ):
        raise ValueError("classical Berger clock SDR flags crossed their claim boundary")

    fingerprints = payload["operator_fingerprints"]
    if not isinstance(fingerprints, dict) or set(fingerprints) != EXPECTED_FINGERPRINTS:
        raise ValueError("classical Berger operator fingerprint inventory drifted")
    for name, digest in fingerprints.items():
        _require_hash(digest, f"classical Berger operator {name}")
    if payload["next_gate"] != "BERGER_RETAINED_Q1_AND_NONMINIMAL_COMPLETION":
        raise ValueError("classical Berger clock SDR next gate drifted")
    return payload


def _validate_portable_operator(value: object, operator_id: str) -> dict[str, Any]:
    operator = _require_fields(
        value,
        {
            "operator_id",
            "domain_basis_indices",
            "codomain_basis_indices",
            "cohomological_degree",
            "maximum_differential_order",
            "entries",
            "canonical_sha256",
        },
        f"portable Berger operator {operator_id}",
    )
    if operator["operator_id"] != operator_id:
        raise ValueError(f"portable Berger operator id drifted: {operator_id}")
    for field in ("domain_basis_indices", "codomain_basis_indices"):
        indices = operator[field]
        if (
            not isinstance(indices, list)
            or not indices
            or any(type(index) is not int or not 0 <= index < 34 for index in indices)
            or len(indices) != len(set(indices))
            or indices != sorted(indices)
        ):
            raise ValueError(f"portable Berger operator {operator_id} has invalid {field}")
    if type(operator["cohomological_degree"]) is not int:
        raise ValueError(f"portable Berger operator {operator_id} degree is invalid")
    maximum_order = operator["maximum_differential_order"]
    if type(maximum_order) is not int or maximum_order not in (0, 1):
        raise ValueError(f"portable Berger operator {operator_id} order is invalid")
    if not isinstance(operator["entries"], list):
        raise ValueError(f"portable Berger operator {operator_id} entries are invalid")
    slots: set[tuple[int, int, tuple[int, ...]]] = set()
    for raw_entry in operator["entries"]:
        entry = _require_fields(
            raw_entry,
            {"output", "input", "multiindex", "coefficient"},
            f"portable Berger operator {operator_id} entry",
        )
        if (
            type(entry["output"]) is not int
            or entry["output"] not in operator["codomain_basis_indices"]
        ):
            raise ValueError(f"portable Berger operator {operator_id} output escaped its basis")
        if (
            type(entry["input"]) is not int
            or entry["input"] not in operator["domain_basis_indices"]
        ):
            raise ValueError(f"portable Berger operator {operator_id} input escaped its basis")
        multiindex = entry["multiindex"]
        if (
            not isinstance(multiindex, list)
            or len(multiindex) != 4
            or any(type(order) is not int or order < 0 for order in multiindex)
            or sum(multiindex) > maximum_order
        ):
            raise ValueError(f"portable Berger operator {operator_id} multiindex is invalid")
        coefficient = _require_fields(
            entry["coefficient"],
            {"numerator", "denominator"},
            f"portable Berger operator {operator_id} coefficient",
        )
        if (
            not isinstance(coefficient["numerator"], str)
            or _NUMERATOR.fullmatch(coefficient["numerator"]) is None
            or not isinstance(coefficient["denominator"], str)
            or _DENOMINATOR.fullmatch(coefficient["denominator"]) is None
        ):
            raise ValueError(f"portable Berger operator {operator_id} coefficient is invalid")
        slot = (entry["output"], entry["input"], tuple(multiindex))
        if slot in slots:
            raise ValueError(f"portable Berger operator {operator_id} has duplicate entries")
        slots.add(slot)
    digest_payload = dict(operator)
    digest = _require_hash(
        digest_payload.pop("canonical_sha256"),
        f"portable Berger operator {operator_id}",
    )
    if digest != _canonical_hash(digest_payload):
        raise ValueError(f"portable Berger operator {operator_id} canonical hash mismatch")
    return operator


def validate_portable_partial_sdr(value: object) -> dict[str, Any]:
    """Validate a future portable 8/34 clock-SDR export without promoting it."""

    payload = _require_fields(
        value,
        {
            "schema",
            "result_id",
            "theorem_source_commit",
            "setting_id",
            "phase_space_id",
            "generator_id",
            "boundary_conditions_sha256",
            "dependency_tags",
            "convention",
            "coefficient_ring",
            "basis",
            "coverage",
            "operators",
            "D_equivariance",
            "proof_checks",
            "canonical_hashes",
            "source_manifest",
            "source_manifest_sha256",
            "claim_boundary",
        },
        "portable Berger clock SDR",
    )
    if (
        payload["schema"] != PORTABLE_SCHEMA_ID
        or payload["result_id"] != "BERGER_CLOCK_PARTIAL_SDR_PORTABLE_EXPORT"
        or payload["setting_id"]
        != "compact_positive_berger_clock_fixed_coupling_linearized"
        or payload["phase_space_id"]
        != "positive_berger_fixed_coupling_linearized_solutions"
        or payload["generator_id"] != "D_compact"
        or payload["dependency_tags"] != ["LOCAL-ALGEBRAIC"]
    ):
        raise ValueError("portable Berger clock SDR identity or scope drifted")
    if (
        not isinstance(payload["theorem_source_commit"], str)
        or len(payload["theorem_source_commit"]) != 40
        or any(char not in "0123456789abcdef" for char in payload["theorem_source_commit"])
    ):
        raise ValueError("portable Berger theorem commit is invalid")
    _require_hash(payload["boundary_conditions_sha256"], "portable Berger boundary")

    convention = _require_fields(
        payload["convention"],
        {
            "classical_grading",
            "transfer_suspension",
            "parity_rule",
            "derivative_symbol",
            "formal_adjoint",
            "basis_order_is_authoritative",
        },
        "portable Berger convention",
    )
    if (
        convention["classical_grading"] != "shifted-bv-cohomological-v1"
        or convention["transfer_suspension"]
        != "suspended-graded-symmetric-factorial-v1"
        or convention["parity_rule"] != "cohomological-degree-mod-2"
        or convention["derivative_symbol"] not in ("p_mu=partial_mu", "p_mu=i_partial_mu")
        or not isinstance(convention["formal_adjoint"], str)
        or not convention["formal_adjoint"]
        or convention["basis_order_is_authoritative"] is not True
    ):
        raise ValueError("portable Berger convention is incomplete")
    ring = _require_fields(
        payload["coefficient_ring"],
        {"ring", "localized_units", "assumptions", "floating_point_forbidden"},
        "portable Berger coefficient ring",
    )
    if ring != {
        "ring": "Q[rho_bar,omega,rho_bar^-1,omega^-1]",
        "localized_units": ["rho_bar", "omega"],
        "assumptions": ["rho_bar!=0", "omega!=0"],
        "floating_point_forbidden": True,
    }:
        raise ValueError("portable Berger coefficient ring drifted")

    basis = payload["basis"]
    if not isinstance(basis, list) or len(basis) != 34:
        raise ValueError("portable Berger basis must contain 34 rows")
    symbols: list[str] = []
    contracted_indices: list[int] = []
    for expected_index, raw_row in enumerate(basis):
        row = _require_fields(
            raw_row,
            {"index", "symbol", "cohomological_degree", "parity", "sector", "retained"},
            "portable Berger basis row",
        )
        if (
            type(row["index"]) is not int
            or row["index"] != expected_index
            or not isinstance(row["symbol"], str)
            or not row["symbol"]
        ):
            raise ValueError("portable Berger basis order or symbol is invalid")
        if (
            type(row["cohomological_degree"]) is not int
            or type(row["parity"]) is not int
            or row["parity"] not in (0, 1)
            or row["parity"] != row["cohomological_degree"] % 2
        ):
            raise ValueError("portable Berger basis grading or parity is invalid")
        if row["sector"] not in (
            "spatial-diffeomorphism",
            "dressed-metric",
            "clock-contractible",
        ) or type(row["retained"]) is not bool:
            raise ValueError("portable Berger basis sector is invalid")
        if (row["sector"] == "clock-contractible") is row["retained"]:
            raise ValueError("portable Berger basis retention disagrees with its sector")
        if not row["retained"]:
            contracted_indices.append(expected_index)
        symbols.append(row["symbol"])
    if len(symbols) != len(set(symbols)) or len(contracted_indices) != 8:
        raise ValueError("portable Berger basis symbols or contracted coverage drifted")

    coverage = _require_fields(
        payload["coverage"],
        {
            "full_minimal_dimension",
            "contracted_clock_dimension",
            "retained_minimal_dimension",
            "contracted_basis_indices",
            "complete_classical_contraction",
        },
        "portable Berger coverage",
    )
    if coverage != {
        "full_minimal_dimension": 34,
        "contracted_clock_dimension": 8,
        "retained_minimal_dimension": 26,
        "contracted_basis_indices": contracted_indices,
        "complete_classical_contraction": False,
    }:
        raise ValueError("portable Berger coverage was promoted or drifted")

    operators = _require_fields(
        payload["operators"],
        PORTABLE_OPERATOR_IDS,
        "portable Berger operator inventory",
    )
    for operator_id in sorted(PORTABLE_OPERATOR_IDS):
        _validate_portable_operator(operators[operator_id], operator_id)

    equivariance = _require_fields(
        payload["D_equivariance"],
        {"status", "D_action", "commutators", "nd2_equivariant_use_authorized"},
        "portable Berger D-equivariance",
    )
    commutators = _require_fields(
        equivariance["commutators"],
        {"D_q1", "D_s_cl", "D_pi_cl", "D_iota_cl"},
        "portable Berger D commutators",
    )
    checks = payload["proof_checks"]
    if (
        not isinstance(checks, list)
        or any(not isinstance(check, str) for check in checks)
        or len(checks) != len(set(checks))
    ):
        raise ValueError("portable Berger proof checks are invalid")
    if any(not isinstance(value, str) for value in commutators.values()):
        raise ValueError("portable Berger D commutators are invalid")
    if equivariance["status"] == "OPEN":
        if (
            equivariance["D_action"] is not None
            or set(commutators.values()) != {"OPEN"}
            or equivariance["nd2_equivariant_use_authorized"] is not False
            or set(checks) != PORTABLE_BASE_CHECKS
        ):
            raise ValueError("open portable Berger D-equivariance was not fail-closed")
    elif equivariance["status"] == "VERIFIED":
        _validate_portable_operator(equivariance["D_action"], "D_action")
        if (
            set(commutators.values()) != {"ZERO_EXACT"}
            or equivariance["nd2_equivariant_use_authorized"] is not True
            or set(checks) != PORTABLE_BASE_CHECKS | {"D_equivariance"}
        ):
            raise ValueError("verified portable Berger D-equivariance is incomplete")
    else:
        raise ValueError("portable Berger D-equivariance status is invalid")

    hashes = _require_fields(
        payload["canonical_hashes"],
        {"basis", "operators", "coefficient_ring", "convention", "proof_checks"},
        "portable Berger canonical hashes",
    )
    for key, component in (
        ("basis", basis),
        ("operators", operators),
        ("coefficient_ring", ring),
        ("convention", convention),
        ("proof_checks", checks),
    ):
        if _require_hash(hashes[key], f"portable Berger {key}") != _canonical_hash(component):
            raise ValueError(f"portable Berger {key} canonical hash mismatch")
    manifest = payload["source_manifest"]
    if not isinstance(manifest, dict) or not manifest:
        raise ValueError("portable Berger source manifest is required")
    for path, digest in manifest.items():
        if not isinstance(path, str) or not path:
            raise ValueError("portable Berger source manifest path is invalid")
        _require_hash(digest, "portable Berger source manifest")
    if _require_hash(payload["source_manifest_sha256"], "portable Berger source manifest") != _canonical_hash(manifest):
        raise ValueError("portable Berger source manifest canonical hash mismatch")
    if not isinstance(payload["claim_boundary"], str) or not payload["claim_boundary"]:
        raise ValueError("portable Berger claim boundary is required")
    return payload


def build_partial_sdr_import() -> dict[str, Any]:
    certificate_relative = CLASSICAL_CERTIFICATE.relative_to(ROOT).as_posix()
    classical = _validate_classical_theorem(
        _load_git_json(certificate_relative, commit=THEOREM_COMMIT)
    )
    total_D = validate_total_d_disposition(_load(TOTAL_D_CERTIFICATE))
    contribution_relative = PROGRAMME_CONTRIBUTION.relative_to(ROOT).as_posix()
    programme_relative = PROGRAMME_STATUS.relative_to(ROOT).as_posix()
    contribution = _load_git_json(
        contribution_relative,
        commit=REGISTRATION_COMMIT,
    )
    programme = _load_git_json(programme_relative, commit=REGISTRATION_COMMIT)
    if (
        total_D.status != "D_GAUGE"
        or not total_D.D_quotient_authorized
        or total_D.setting_id != classical["setting_id"]
        or total_D.phase_space_id != classical["phase_space_id"]
    ):
        raise ValueError("Berger clock SDR and total-D scopes do not agree")

    expected_evidence = {
        "path": certificate_relative,
        "commit": THEOREM_COMMIT,
        "sha256": _git_blob_sha256(certificate_relative, commit=THEOREM_COMMIT),
    }
    if (
        contribution.get("schema") != "pure-weyl-d-quotient-team-contribution-v1"
        or contribution.get("team_id") != "classical"
        or contribution.get("setting_id")
        != "compact_positive_berger_clock_minimal_bv_sdr"
        or contribution.get("generator_id") != "D_compact"
        or contribution.get("phase_space_id") != classical["phase_space_id"]
        or contribution.get("lifecycle_layer") != "CLASSICAL_BV"
        or contribution.get("claim_status") != "CERTIFIED"
        or contribution.get("verdict") != "MINIMAL_CLOCK_SECTOR_SDR"
        or contribution.get("dependency_tags") != ["LOCAL-ALGEBRAIC"]
        or contribution.get("evidence") != expected_evidence
    ):
        raise ValueError("Berger clock SDR programme contribution drifted")
    registered = next(
        (
            row
            for row in programme.get("team_contributions", [])
            if row.get("path") == contribution_relative
        ),
        None,
    )
    registered_setting = next(
        (
            row
            for row in programme.get("setting_ledger", [])
            if row.get("setting_id")
            == "compact_positive_berger_clock_minimal_bv_sdr"
        ),
        None,
    )
    if (
        registered is None
        or registered.get("payload") != contribution
        or registered.get("sha256")
        != _git_blob_sha256(contribution_relative, commit=REGISTRATION_COMMIT)
        or registered_setting is None
        or registered_setting.get("status") != "CERTIFIED"
        or registered_setting.get("verdict") != "MINIMAL_CLOCK_SECTOR_SDR"
        or registered_setting.get("phase_space_id") != classical["phase_space_id"]
    ):
        raise ValueError("Berger clock SDR programme registration is incomplete")

    classical_paths = (
        CLASSICAL_CERTIFICATE,
        CLASSICAL_SCHEMA,
        CLASSICAL_PRODUCER,
        CLASSICAL_INDEPENDENT_VERIFIER,
        CLASSICAL_TEST,
        CLASSICAL_REPORT,
    )
    source_artifacts = []
    for path in classical_paths:
        relative = path.relative_to(ROOT).as_posix()
        theorem_hash = _git_blob_sha256(relative, commit=THEOREM_COMMIT)
        source_artifacts.append({"path": relative, "sha256": theorem_hash})

    return {
        "schema": SCHEMA_ID,
        "result_id": "BERGER_CLOCK_PARTIAL_SDR_IMPORT",
        "lifecycle_layer": "CLASSICAL_BV",
        "claim_status": "IMPORTED_EVIDENCE_ONLY",
        "result_state": "PARTIAL_CLOCK_SECTOR_SDR_AVAILABLE_PORTABLE_MAPS_BLOCKED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "setting_id": classical["setting_id"],
        "phase_space_id": classical["phase_space_id"],
        "generator_id": "D_compact",
        "boundary_conditions_sha256": total_D.boundary_conditions_sha256,
        "classical_theorem_commit": THEOREM_COMMIT,
        "coverage": {
            "full_minimal_dimension": 34,
            "contracted_clock_dimension": 8,
            "retained_minimal_dimension": 26,
            "contracted_rows": list(EXPECTED_CLOCK_ROWS),
            "coverage_status": "PARTIAL_CLOCK_SECTOR_ONLY",
        },
        "verified_evidence": {
            "support_local": True,
            "cyclic": True,
            "canonical_cotangent_lift": True,
            "q1_squared_zero": True,
            "contraction_identity_on_clock_block": True,
            "homotopy_squared_zero": True,
            "operator_fingerprints": classical["operator_fingerprints"],
        },
        "portable_map_gate": {
            "map_payload_status": "FINGERPRINTS_AND_FORMULAS_ONLY",
            "operator_fingerprint_reconstruction_check": "NOT_COMPUTED",
            "coefficient_ring_declared": False,
            "differential_symbol_convention_declared": False,
            "grading_bridge_declared": False,
            "portable_q1_clock": "NOT_AVAILABLE",
            "portable_s_clock": "NOT_AVAILABLE",
            "portable_iota_cl": "NOT_AVAILABLE",
            "portable_pi_cl": "NOT_AVAILABLE",
            "portable_pairing": "NOT_AVAILABLE",
            "D_action_on_clock_block": "NOT_AVAILABLE",
            "D_equivariance_checks": "NOT_COMPUTED",
        },
        "nd2_gate": {
            "partial_clock_sector_sdr": "AVAILABLE_EVIDENCE_ONLY",
            "complete_classical_contraction": "NOT_AVAILABLE",
            "classical_contraction_artifact_satisfied": False,
            "physical_execution_authorized": False,
            "next_gate": "PORTABLE_CLOCK_SDR_MAP_EXPORT_THEN_BERGER_RETAINED_Q1_AND_NONMINIMAL_COMPLETION",
        },
        "provenance": {
            "classical_source_artifacts": source_artifacts,
            "programme_registration": {
                "status": "VERIFIED",
                "registration_commit": REGISTRATION_COMMIT,
                "contribution_path": contribution_relative,
                "contribution_sha256": _git_blob_sha256(
                    contribution_relative,
                    commit=REGISTRATION_COMMIT,
                ),
                "programme_status_path": programme_relative,
                "programme_status_sha256": _git_blob_sha256(
                    programme_relative,
                    commit=REGISTRATION_COMMIT,
                ),
            },
            "total_D_disposition": {
                "path": TOTAL_D_CERTIFICATE.relative_to(ROOT).as_posix(),
                "sha256": _sha256(TOTAL_D_CERTIFICATE),
                "classical_commit": total_D.classical_commit,
            },
            "portable_receiving_schema": "quantum-weyl/transfer/schema/berger-clock-partial-sdr-portable-v1.schema.json",
        },
        "not_established": [
            "portable coefficient-level clock maps independently consumable by ND2",
            "independent comparison of reconstructed operators with all emitted fingerprints",
            "D-equivariance of q1, s_cl, pi_cl, and iota_cl on the clock block",
            "the retained dressed-metric q1 coefficients and Noether row",
            "the nonminimal gauge-fixed contraction",
            "the complete Berger classical contraction artifact",
            "nonlinear q2, admissibility, stability, or a causal Green homotopy",
        ],
        "claim_boundary": (
            "This import recognizes the exact cyclic eight-row clock-sector SDR and its "
            "34-to-26 coverage statement. The source certificate exports formulas and "
            "fingerprints rather than portable operator entries, so it cannot satisfy "
            "the ND2 classical_contraction artifact or authorize physical execution."
        ),
    }
