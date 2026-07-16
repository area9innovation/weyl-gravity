"""Fail-closed arrival adapter for the complete Berger 54-row classical q2.

This module defines the portable bilinear PBW handoff and independently checks
its structural binding to the already imported unary complex, D action,
pairing, and contraction.  It does not import the in-progress classical
producer and does not claim that a support-local q2 exists before a committed
classical certificate is supplied.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any

import sympy as sp
from sympy.polys.polyerrors import PolynomialError

TRANSFER_ROOT = Path(__file__).resolve().parent
ROOT = TRANSFER_ROOT.parents[1]
if str(TRANSFER_ROOT) not in sys.path:
    sys.path.insert(0, str(TRANSFER_ROOT))

try:
    from . import berger_gauge_fixed_nonminimal_import as gauge_fixed_import
except ImportError:
    import berger_gauge_fixed_nonminimal_import as gauge_fixed_import

UNARY_IMPORT_PATH = (
    TRANSFER_ROOT / "certificates" / "BERGER_GAUGE_FIXED_NONMINIMAL_IMPORT.json"
)
D_IMPORT_PATH = TRANSFER_ROOT / "certificates" / "BERGER_54_ROW_LOCAL_D_IMPORT.json"
INPUT_SCHEMA_PATH = (
    TRANSFER_ROOT
    / "schema"
    / "berger-54-row-support-local-q2-portable-v1.schema.json"
)

INPUT_SCHEMA = "pure-weyl-berger-54-row-support-local-q2-portable-v1"
SETTING_ID = "compact_positive_berger_clock_fixed_coupling_linearized"
CONVENTION = "suspended-graded-symmetric-factorial-v1"
COEFFICIENT_RING = (
    "Q(alpha_B,u,v)[e0,e1,e2,e3]_PBW with u=c/a^2, v=1/c"
)
ORDERED_PBW_BASIS = "e0^n0 e1^n1 e2^n2 e3^n3"
REQUIRED_PROOF_CHECKS = (
    "q2_row_completeness",
    "q2_koszul_symmetry",
    "q1_q2_arity_two_nilpotency",
    "D_q2_derivation",
    "BV_cyclicity_q2",
)

ALPHA_B, U, V = sp.symbols("alpha_B u v", nonzero=True)
_ALLOWED_CHARACTERS = re.compile(r"[0-9A-Za-z_+\-*/() ]+")
_TOKEN = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


def canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _require_fields(value: object, fields: set[str], name: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != fields:
        raise ValueError(f"{name} fields drifted")
    return value


@lru_cache(maxsize=None)
def parse_coefficient(value: str) -> sp.Expr:
    if (
        not isinstance(value, str)
        or not value
        or _ALLOWED_CHARACTERS.fullmatch(value) is None
        or set(_TOKEN.findall(value)) - {"alpha_B", "u", "v"}
    ):
        raise ValueError("q2 coefficient uses an undeclared expression token")
    try:
        expression = sp.sympify(
            value,
            locals={"alpha_B": ALPHA_B, "u": U, "v": V},
        )
        polynomial = sp.Poly(expression, ALPHA_B, U, V, domain=sp.QQ)
    except (sp.SympifyError, PolynomialError, TypeError, ValueError) as exc:
        raise ValueError("q2 coefficient is not an exact declared polynomial") from exc
    normalized = sp.factor(polynomial.as_expr())
    if normalized == 0:
        raise ValueError("q2 record retains a zero coefficient")
    return normalized


@dataclass(frozen=True)
class PBWBilinearTerm:
    left_exponents: tuple[int, int, int, int]
    right_exponents: tuple[int, int, int, int]
    coefficient: sp.Expr


@dataclass(frozen=True)
class PBWBilinearEntry:
    output: int
    left: int
    right: int
    terms: tuple[PBWBilinearTerm, ...]


@dataclass(frozen=True)
class ParsedBergerQ2:
    classical_commit: str
    row_ids: tuple[str, ...]
    degrees: tuple[int, ...]
    maximum_total_jet_order: int
    entries: tuple[PBWBilinearEntry, ...]
    q2_sha256: str
    term_count: int


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON input is not an object: {path}")
    return value


def load_prerequisites() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    unary = _load_json(UNARY_IMPORT_PATH)
    d_action = _load_json(D_IMPORT_PATH)
    classical_unary = gauge_fixed_import._git_json(
        gauge_fixed_import.CERTIFICATE_RELATIVE
    )
    if (
        unary.get("result_state")
        != "COMPLETE_CLASSICAL_UNARY_PACKAGE_IMPORTED_NONLINEAR_INPUT_BLOCKED"
        or d_action.get("result_state")
        != "COMPLETE_54_ROW_LOCAL_D_ACTION_IMPORTED_SUPPORT_LOCAL_Q2_BLOCKED"
        or unary.get("setting_id") != SETTING_ID
        or d_action.get("setting_id") != SETTING_ID
    ):
        raise ValueError("Berger unary/D prerequisite identity drifted")
    unary_hashes = unary.get("map_hashes", {})
    d_hashes = d_action.get("operator_hashes", {})
    for unary_name, d_name in (
        ("q1_sha256", "q1_sha256"),
        ("iota_sha256", "iota_sha256"),
        ("pi_sha256", "pi_sha256"),
        ("S_sha256", "S_sha256"),
        ("pairing_sha256", "pairing_sha256"),
    ):
        if unary_hashes.get(unary_name) != d_hashes.get(d_name):
            raise ValueError(f"Berger unary/D prerequisite hash mismatch: {unary_name}")
    rows = classical_unary.get("row_layout", {}).get("component_rows")
    if (
        not isinstance(rows, list)
        or len(rows) != 54
        or [row.get("index") for row in rows] != list(range(54))
    ):
        raise ValueError("authoritative Berger 54-row layout drifted")
    return unary, d_action, classical_unary


def expected_dependency_refs(
    unary: dict[str, Any], d_action: dict[str, Any]
) -> dict[str, Any]:
    unary_hashes = unary["map_hashes"]
    d_hashes = d_action["operator_hashes"]
    return {
        "gauge_fixed_54_row": {
            "result_id": unary["classical_result"]["result_id"],
            "certificate_sha256": unary["classical_result"]["certificate_sha256"],
        },
        "local_D_54_row": {
            "result_id": d_action["classical_result"]["result_id"],
            "certificate_sha256": d_action["classical_result"]["certificate_sha256"],
        },
        "operator_hashes": {
            "q1_sha256": unary_hashes["q1_sha256"],
            "D54_sha256": d_hashes["D54_sha256"],
            "iota_sha256": unary_hashes["iota_sha256"],
            "pi_sha256": unary_hashes["pi_sha256"],
            "S_sha256": unary_hashes["S_sha256"],
            "pairing_sha256": unary_hashes["pairing_sha256"],
        },
    }


def _validate_proof_artifacts(
    proof_checks: list[dict[str, Any]], repository_root: Path
) -> None:
    observed = []
    root = repository_root.resolve()
    for index, item in enumerate(proof_checks):
        check = _require_fields(
            item, {"check_id", "status", "proof_artifact"}, f"proof_checks[{index}]"
        )
        observed.append(check["check_id"])
        if check["status"] != "VERIFIED":
            raise ValueError("q2 proof check is not VERIFIED")
        artifact = _require_fields(
            check["proof_artifact"], {"path", "sha256"}, "q2 proof artifact"
        )
        path = (root / artifact["path"]).resolve()
        if root not in path.parents or not path.is_file():
            raise ValueError("q2 proof artifact is missing or outside the repository")
        if hashlib.sha256(path.read_bytes()).hexdigest() != artifact["sha256"]:
            raise ValueError("q2 proof artifact hash mismatch")
    if observed != list(REQUIRED_PROOF_CHECKS):
        raise ValueError("q2 proof-check inventory or order drifted")


def _parse_exponents(value: object, name: str) -> tuple[int, int, int, int]:
    if (
        not isinstance(value, list)
        or len(value) != 4
        or any(type(count) is not int or count < 0 for count in value)
    ):
        raise ValueError(f"{name} is not a four-axis PBW exponent vector")
    return tuple(value)  # type: ignore[return-value]


def parse_portable_q2(
    payload: dict[str, Any], *, repository_root: Path | None = None
) -> ParsedBergerQ2:
    """Validate, bind, and parse a prospective authoritative q2 handoff."""

    required = {
        "schema",
        "result_id",
        "setting_id",
        "claim_status",
        "classical_commit",
        "dependency_tags",
        "dependency_refs",
        "operator_semantics",
        "support_category",
        "row_layout",
        "q2",
        "proof_checks",
        "canonical_hashes",
        "flags",
        "claim_boundary",
    }
    _require_fields(payload, required, "portable Berger q2")
    if (
        payload["schema"] != INPUT_SCHEMA
        or payload["result_id"] != "BERGER_54_ROW_SUPPORT_LOCAL_Q2"
        or payload["setting_id"] != SETTING_ID
        or payload["claim_status"]
        != "CERTIFIED_COMPLETE_SUPPORT_LOCAL_Q2_ARITY_TWO_IDENTITIES"
        or payload["dependency_tags"] != ["LOCAL-ALGEBRAIC"]
        or not isinstance(payload["classical_commit"], str)
        or re.fullmatch(r"[0-9a-f]{40}", payload["classical_commit"]) is None
    ):
        raise ValueError("portable Berger q2 identity or setting drifted")

    unary, d_action, classical_unary = load_prerequisites()
    if payload["dependency_refs"] != expected_dependency_refs(unary, d_action):
        raise ValueError("portable Berger q2 dependency binding drifted")
    semantics = _require_fields(
        payload["operator_semantics"],
        {
            "portable_name",
            "arity",
            "degree",
            "factorial_convention",
            "coefficient_ring",
            "ordered_pbw_basis",
            "not_quantum_loop_operator",
        },
        "q2 operator semantics",
    )
    if semantics != {
        "portable_name": "classical_binary_q2",
        "arity": 2,
        "degree": 1,
        "factorial_convention": CONVENTION,
        "coefficient_ring": COEFFICIENT_RING,
        "ordered_pbw_basis": ORDERED_PBW_BASIS,
        "not_quantum_loop_operator": True,
    }:
        raise ValueError("portable Berger q2 operator semantics drifted")

    support = _require_fields(
        payload["support_category"],
        {
            "spacetime_dimension",
            "locality",
            "invariant_frame",
            "maximum_total_jet_order",
        },
        "q2 support category",
    )
    maximum_order = support["maximum_total_jet_order"]
    if (
        support["spacetime_dimension"] != 4
        or support["locality"] != "SUPPORT_LOCAL_POLYDIFFERENTIAL"
        or support["invariant_frame"] != "berger_left_invariant_frame"
        or type(maximum_order) is not int
        or maximum_order < 0
    ):
        raise ValueError("portable Berger q2 support category drifted")

    authoritative_rows = classical_unary["row_layout"]["component_rows"]
    expected_row_ids = [row["row_id"] for row in authoritative_rows]
    degrees = tuple(row["degree"] for row in authoritative_rows)
    layout = _require_fields(
        payload["row_layout"],
        {"total_rows", "degree_ranks", "row_ids"},
        "q2 row layout",
    )
    if (
        layout["total_rows"] != 54
        or layout["degree_ranks"] != [5, 22, 22, 5]
        or layout["row_ids"] != expected_row_ids
    ):
        raise ValueError("portable Berger q2 row layout drifted")

    q2 = _require_fields(
        payload["q2"], {"shape", "entries", "row_completeness", "sha256"}, "q2"
    )
    if (
        q2["shape"] != [54, 54, 54]
        or not isinstance(q2["entries"], list)
        or not q2["entries"]
    ):
        raise ValueError("portable Berger q2 shape drifted")
    q2_body = {
        "shape": q2["shape"],
        "entries": q2["entries"],
        "row_completeness": q2["row_completeness"],
    }
    if q2["sha256"] != canonical_hash(q2_body):
        raise ValueError("portable Berger q2 record hash mismatch")

    entries: list[PBWBilinearEntry] = []
    previous_key: tuple[int, int, int] | None = None
    raw_by_key: dict[
        tuple[int, int, int], dict[tuple[tuple[int, ...], tuple[int, ...]], sp.Expr]
    ] = {}
    output_counts = [0] * 54
    for entry_index, raw_entry in enumerate(q2["entries"]):
        entry = _require_fields(
            raw_entry, {"output", "left", "right", "terms"}, f"q2 entry {entry_index}"
        )
        key = (entry["output"], entry["left"], entry["right"])
        if (
            any(type(index) is not int or not 0 <= index < 54 for index in key)
            or previous_key is not None
            and key <= previous_key
            or not isinstance(entry["terms"], list)
            or not entry["terms"]
        ):
            raise ValueError("q2 entries are noncanonical, duplicate, or out of range")
        if degrees[key[0]] != degrees[key[1]] + degrees[key[2]] + 1:
            raise ValueError("q2 entry violates cohomological degree one")
        previous_key = key
        output_counts[key[0]] += 1
        parsed_terms: list[PBWBilinearTerm] = []
        term_map: dict[tuple[tuple[int, ...], tuple[int, ...]], sp.Expr] = {}
        previous_term: tuple[tuple[int, ...], tuple[int, ...]] | None = None
        for term_index, raw_term in enumerate(entry["terms"]):
            term = _require_fields(
                raw_term,
                {"left_exponents", "right_exponents", "coefficient"},
                f"q2 entry {entry_index} term {term_index}",
            )
            left_exponents = _parse_exponents(
                term["left_exponents"], "left_exponents"
            )
            right_exponents = _parse_exponents(
                term["right_exponents"], "right_exponents"
            )
            term_key = (left_exponents, right_exponents)
            if previous_term is not None and term_key <= previous_term:
                raise ValueError("q2 PBW terms are noncanonical or duplicate")
            if sum(left_exponents) + sum(right_exponents) > maximum_order:
                raise ValueError("q2 PBW term exceeds declared total jet order")
            coefficient = parse_coefficient(term["coefficient"])
            parsed_terms.append(
                PBWBilinearTerm(left_exponents, right_exponents, coefficient)
            )
            term_map[term_key] = coefficient
            previous_term = term_key
        raw_by_key[key] = term_map
        entries.append(PBWBilinearEntry(*key, tuple(parsed_terms)))

    completeness = q2["row_completeness"]
    if (
        not isinstance(completeness, list)
        or len(completeness) != 54
        or any(
            _require_fields(item, {"output", "status", "entry_count"}, "row completeness")
            != {
                "output": expected_row_ids[index],
                "status": "COMPLETE",
                "entry_count": output_counts[index],
            }
            for index, item in enumerate(completeness)
        )
    ):
        raise ValueError("q2 row-completeness ledger drifted")

    for (output, left, right), terms in raw_by_key.items():
        parity_sign = -1 if (degrees[left] & 1) and (degrees[right] & 1) else 1
        partner = raw_by_key.get((output, right, left), {})
        expected_partner = {
            (right_word, left_word): sp.factor(parity_sign * coefficient)
            for (left_word, right_word), coefficient in terms.items()
        }
        if partner != expected_partner:
            raise ValueError("q2 graded Koszul symmetry failed")

    proof_checks = payload["proof_checks"]
    if not isinstance(proof_checks, list):
        raise ValueError("q2 proof checks are not a list")
    _validate_proof_artifacts(proof_checks, repository_root or ROOT)
    hashes = _require_fields(
        payload["canonical_hashes"],
        {"row_layout_sha256", "q2_sha256", "proof_checks_sha256"},
        "q2 canonical hashes",
    )
    if hashes != {
        "row_layout_sha256": canonical_hash(layout),
        "q2_sha256": q2["sha256"],
        "proof_checks_sha256": canonical_hash(proof_checks),
    }:
        raise ValueError("portable Berger q2 canonical hash ledger drifted")
    flags = _require_fields(
        payload["flags"],
        {
            "CLASSICAL_SUPPORT_LOCAL_Q2_COMPLETE_54_ROWS",
            "ARITY_TWO_IDENTITIES_CLASSICALLY_VERIFIED",
            "RESIDUAL_TRANSFER_EXECUTED",
            "QUANTUM_CORRECTION_INCLUDED",
        },
        "q2 flags",
    )
    if flags != {
        "CLASSICAL_SUPPORT_LOCAL_Q2_COMPLETE_54_ROWS": True,
        "ARITY_TWO_IDENTITIES_CLASSICALLY_VERIFIED": True,
        "RESIDUAL_TRANSFER_EXECUTED": False,
        "QUANTUM_CORRECTION_INCLUDED": False,
    }:
        raise ValueError("portable Berger q2 claim boundary drifted")
    return ParsedBergerQ2(
        classical_commit=payload["classical_commit"],
        row_ids=tuple(expected_row_ids),
        degrees=degrees,
        maximum_total_jet_order=maximum_order,
        entries=tuple(entries),
        q2_sha256=q2["sha256"],
        term_count=sum(len(entry.terms) for entry in entries),
    )


def build_readiness_payload() -> dict[str, Any]:
    unary, d_action, classical_unary = load_prerequisites()
    row_ids = [
        row["row_id"] for row in classical_unary["row_layout"]["component_rows"]
    ]
    dependencies = expected_dependency_refs(unary, d_action)
    return {
        "schema": "quantum-weyl-berger-54-row-q2-arrival-readiness-v1",
        "result_id": "BERGER_54_ROW_Q2_ARRIVAL_READINESS",
        "result_state": "PORTABLE_CONSUMER_AND_MUTATION_RAIL_READY_CLASSICAL_Q2_INPUT_BLOCKED",
        "lifecycle_layer": "CLASSICAL_BV_IMPORT",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "setting_id": SETTING_ID,
        "generality_assessment": {
            "target": "G2_FULL_SUPPORT_LOCAL_LOW_ARITY_COMPLEX_ON_ONE_BACKGROUND",
            "achieved": "G2_INPUT_CONSUMER_READINESS_ONLY",
            "promotion_to_G2_authorized": False,
        },
        "prerequisite_binding": {
            "total_rows": 54,
            "row_ids_sha256": canonical_hash(row_ids),
            "dependency_refs": dependencies,
            "unary_and_D_hashes_consistent": True,
        },
        "consumer_capabilities": {
            "strict_portable_schema": True,
            "exact_PBW_coefficient_parser": True,
            "canonical_record_hash_verification": True,
            "all_54_rows_bound_to_authoritative_layout": True,
            "cohomological_degree_check": True,
            "total_jet_bound_check": True,
            "graded_Koszul_symmetry_check": True,
            "proof_artifact_hash_verification": True,
            "nonzero_field_field_to_equation_fixture": True,
            "independent_q1_q2_identity_execution": False,
            "independent_D_q2_derivation_execution": False,
            "independent_BV_cyclicity_execution": False,
            "ND2_physical_execution": False,
        },
        "input_gate": {
            "classical_q2_export_available": False,
            "scientific_fixture_substitution_allowed": False,
            "status": "INPUT_BLOCKED",
            "next_action_on_arrival": "pin committed classical export, parse and bind it, then implement and run the exact operator-valued q1/q2, D/q2, cyclicity, transfer, and Cartan chain",
        },
        "claim_flags": {
            "ARRIVAL_ADAPTER_READY": True,
            "CLASSICAL_SUPPORT_LOCAL_Q2_IMPORTED": False,
            "ARITY_TWO_IDENTITIES_INDEPENDENTLY_REPLAYED": False,
            "TRANSFERRED_ELL2_COMPUTED": False,
            "INTERACTING_CARTAN_VERDICT": False,
            "QUANTUM_CLAIM": False,
        },
        "provenance": {
            "portable_input_schema": str(INPUT_SCHEMA_PATH.relative_to(ROOT)),
            "portable_input_schema_sha256": hashlib.sha256(
                INPUT_SCHEMA_PATH.read_bytes()
            ).hexdigest(),
            "unary_import_certificate": str(UNARY_IMPORT_PATH.relative_to(ROOT)),
            "unary_import_sha256": hashlib.sha256(UNARY_IMPORT_PATH.read_bytes()).hexdigest(),
            "D_import_certificate": str(D_IMPORT_PATH.relative_to(ROOT)),
            "D_import_sha256": hashlib.sha256(D_IMPORT_PATH.read_bytes()).hexdigest(),
        },
        "next_gate": "IMPORT_COMMITTED_BERGER_54_ROW_SUPPORT_LOCAL_Q2",
        "claim_boundary": "This LOCAL-ALGEBRAIC readiness certificate fixes and tests the portable 54-row bilinear PBW arrival contract against the authoritative unary, D, pairing, and contraction hashes. Its nonzero fixture is implementation-only. No classical q2 is imported, no operator-valued arity-two identity is independently replayed, and no transfer, Cartan, physical, causal, or quantum verdict is authorized.",
    }
