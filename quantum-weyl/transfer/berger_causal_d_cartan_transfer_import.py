"""Pinned import of the conditional causal Berger D-Cartan transfer theorem."""

from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any

from local_bv.schema_validation import validate_instance


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CLASSICAL_COMMIT = "f6c42ce5e65318d6e982223999abdcefad10edb5"
SETTING_ID = "compact_positive_berger_clock_fixed_coupling_linearized"
CLASSICAL_CERTIFICATE = "d_quotient_classical/certificates/BERGER_CAUSAL_D_CARTAN_TRANSFER.json"
CLASSICAL_SCHEMA = "d_quotient_classical/schema/berger-causal-D-Cartan-transfer-v1.schema.json"
CLASSICAL_DEPENDENCIES = (
    "d_quotient_classical/certificates/BERGER_54_ROW_CAUSAL_HOMOTOPY_REDUCTION.json",
    "d_quotient_classical/certificates/BERGER_54_ROW_LOCAL_D_ACTION.json",
    "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_Q2.json",
    "d_quotient_classical/certificates/BERGER_UNARY_D_CARTAN_MICROLOCAL_OBSTRUCTION.json",
)
CLASSICAL_SOURCES = (
    CLASSICAL_CERTIFICATE,
    CLASSICAL_SCHEMA,
    *CLASSICAL_DEPENDENCIES,
    "d_quotient_classical/backreacted_clock/berger_causal_d_cartan_transfer.py",
    "d_quotient_classical/backreacted_clock/verify_berger_causal_d_cartan_transfer.py",
    "d_quotient_classical/backreacted_clock/tests/test_berger_causal_d_cartan_transfer.py",
    "d_quotient_classical/reports/berger-causal-D-Cartan-transfer.md",
)
QUANTUM_INPUTS = {
    "D_and_causal_reduction": HERE / "certificates/BERGER_54_ROW_D_CAUSAL_INPUT_IMPORT.json",
    "full_q2_replay": HERE / "certificates/BERGER_SUPPORT_LOCAL_Q2_SCIENTIFIC_REPLAY.json",
    "retained_q2_transfer": HERE / "certificates/BERGER_RETAINED_26_Q2_TRANSFER.json",
    "bare_unary_obstruction": HERE / "certificates/BERGER_UNARY_D_CARTAN_MICROLOCAL_OBSTRUCTION_IMPORT.json",
}


@lru_cache(maxsize=1)
def _git_prefix() -> str:
    return subprocess.run(
        ["git", "rev-parse", "--show-prefix"], cwd=ROOT, check=True,
        capture_output=True, text=True,
    ).stdout.strip()


def _git_blob(relative: str) -> bytes:
    result = subprocess.run(
        ["git", "show", f"{CLASSICAL_COMMIT}:{_git_prefix()}{relative}"],
        cwd=ROOT, check=False, capture_output=True,
    )
    if result.returncode:
        raise ValueError(f"missing pinned causal-transfer artifact: {relative}")
    return result.stdout


def _git_json(relative: str) -> dict[str, Any]:
    value = json.loads(_git_blob(relative))
    if not isinstance(value, dict):
        raise ValueError(f"pinned JSON is not an object: {relative}")
    return value


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _artifact(relative: str) -> dict[str, str]:
    return {"path": relative, "commit": CLASSICAL_COMMIT, "sha256": _sha256_bytes(_git_blob(relative))}


Polynomial = dict[tuple[str, ...], Fraction]


def _rewrite(terms: Polynomial) -> Polynomial:
    pending = {word: coefficient for word, coefficient in terms.items() if coefficient}
    while True:
        output: Polynomial = {}
        changed = False
        for word, coefficient in pending.items():
            replacement = None
            for index in range(len(word) - 1):
                pair = word[index:index + 2]
                prefix, suffix = word[:index], word[index + 2:]
                if pair == ("Q", "L"):
                    replacement = ((prefix + suffix, coefficient), (prefix + ("L", "Q") + suffix, -coefficient))
                    break
                if pair == ("Q", "D"):
                    replacement = ((prefix + ("D", "Q") + suffix, coefficient),)
                    break
                if pair == ("Q", "A"):
                    replacement = ((prefix + ("A", "R") + suffix, coefficient),)
                    break
            if replacement is None:
                output[word] = output.get(word, Fraction()) + coefficient
            else:
                changed = True
                for new_word, new_coefficient in replacement:
                    output[new_word] = output.get(new_word, Fraction()) + new_coefficient
        pending = {word: coefficient for word, coefficient in output.items() if coefficient}
        if not changed:
            return pending


def _formal_checks() -> dict[str, bool]:
    unary = {("Q", "L", "D"): Fraction(1), ("L", "D", "Q"): Fraction(1), ("D",): Fraction(-1)}
    binary = {("Q", "L", "A"): Fraction(-1), ("L", "A", "R"): Fraction(-1), ("A",): Fraction(1)}
    complement = {"ONE_54": 1, "IOTA_PI": -1}
    endpoint = {"IOTA_PI": 1}
    total = {key: complement.get(key, 0) + endpoint.get(key, 0) for key in set(complement) | set(endpoint)}
    return {
        "unary_noncommutative_rewrite_zero": not _rewrite(unary),
        "arity_two_noncommutative_rewrite_zero": not _rewrite(binary),
        "conditional_54_row_lift_reduces_to_identity": {key: value for key, value in total.items() if value} == {"ONE_54": 1},
    }


def validate_import(source: dict[str, Any], schema: dict[str, Any], inputs: dict[str, dict[str, Any]]) -> dict[str, bool]:
    errors = validate_instance(source, schema)
    if errors:
        raise ValueError(f"causal D-Cartan source schema validation failed: {errors}")
    expected_fields = {
        "arity_two_transfer", "claim_boundary", "claim_status", "dependency_refs",
        "dependency_tags", "endpoint_assumptions", "exact_checks", "flags", "next_gate",
        "result_id", "route_split", "schema", "setting_id", "unary_transfer",
    }
    if set(source) != expected_fields:
        raise ValueError("causal D-Cartan source fields drifted")
    if (
        schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema"
        or schema.get("additionalProperties") is not False
        or source.get("result_id") != "BERGER_CAUSAL_D_CARTAN_TRANSFER"
        or source.get("claim_status") != "CERTIFIED_CONDITIONAL_TRANSFER_ENDPOINT_OPEN"
        or source.get("setting_id") != SETTING_ID
        or source.get("dependency_tags") != ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"]
    ):
        raise ValueError("causal D-Cartan source identity drifted")
    refs = source["dependency_refs"]
    expected_ref_ids = {
        "causal_54_to_26_reduction": (CLASSICAL_DEPENDENCIES[0], "BERGER_54_ROW_CAUSAL_HOMOTOPY_REDUCTION"),
        "local_D_action": (CLASSICAL_DEPENDENCIES[1], "BERGER_54_ROW_LOCAL_D_ACTION"),
        "classical_binary_q2": (CLASSICAL_DEPENDENCIES[2], "BERGER_SUPPORT_LOCAL_Q2"),
        "bare_unary_obstruction": (CLASSICAL_DEPENDENCIES[3], "BERGER_UNARY_D_CARTAN_MICROLOCAL_OBSTRUCTION"),
    }
    for name, (path, result_id) in expected_ref_ids.items():
        if refs.get(name) != {"result_id": result_id, "sha256": _sha256_bytes(_git_blob(path))}:
            raise ValueError(f"causal D-Cartan dependency drifted: {name}")
    expected_flags = {
        "BERGER_CAUSAL_D_CARTAN_TRANSFER_THEOREM": True,
        "BERGER_CAUSAL_UNARY_D_CARTAN_CONDITIONAL": True,
        "BERGER_CAUSAL_ARITY_TWO_SOURCE_CLOSED_CONDITIONAL": True,
        "BERGER_CAUSAL_ARITY_TWO_RAW_PRIMITIVE_CONDITIONAL": True,
        "BERGER_CAUSAL_ARITY_TWO_CYCLIC_COMPLETION": False,
        "BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY": False,
        "BERGER_CAUSAL_D_CARTAN_EXTENSION": False,
        "BERGER_RESIDUAL_BFV_D_CARTAN_EXTENSION": False,
    }
    if source["flags"] != expected_flags or source.get("next_gate") != "BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY":
        raise ValueError("causal D-Cartan lifecycle boundary drifted")
    if (
        source["unary_transfer"].get("definition") != "iota_D,s^(1)=Lambda_s D"
        or source["arity_two_transfer"].get("raw_primitive") != "iota_D,s,raw^(2)=-Lambda_s A_D,s^(2)"
        or source["endpoint_assumptions"].get("status") != "BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY remains false"
    ):
        raise ValueError("causal D-Cartan formula or endpoint assumption drifted")
    d_input = inputs["D_and_causal_reduction"]
    q2_input = inputs["full_q2_replay"]
    retained = inputs["retained_q2_transfer"]
    obstruction = inputs["bare_unary_obstruction"]
    if (
        d_input.get("result_state") != "CLASSICAL_D_ACTION_IMPORTED_CAUSAL_ENDPOINT_REDUCED"
        or d_input.get("conditional_causal_lift", {}).get("endpoint_status") != "NOT_CONSTRUCTED"
        or d_input.get("quantum_execution_authorized") is not False
        or q2_input.get("claim_flags", {}).get("SCIENTIFIC_ARITY_TWO_IDENTITIES_INDEPENDENTLY_REPLAYED") is not True
        or retained.get("claim_flags", {}).get("CLASSICAL_RETAINED_26_Q2_TRANSFERRED") is not True
        or retained.get("claim_flags", {}).get("LORENTZIAN_CAUSAL_EXTENSION_COMPUTED") is not False
        or obstruction.get("claim_flags", {}).get("BERGER_UNARY_D_CARTAN_LOCAL_BARE_COMPLEX_NO_GO") is not True
    ):
        raise ValueError("quantum-side causal transfer inputs are incomplete or promoted")
    checks = _formal_checks()
    if not all(checks.values()):
        raise ValueError("independent causal D-Cartan rewrite failed")
    return checks


def build_import() -> dict[str, Any]:
    source = _git_json(CLASSICAL_CERTIFICATE)
    schema = _git_json(CLASSICAL_SCHEMA)
    inputs = {name: json.loads(path.read_text()) for name, path in QUANTUM_INPUTS.items()}
    checks = validate_import(source, schema, inputs)
    return {
        "schema": "quantum-weyl-berger-causal-d-cartan-transfer-import-v1",
        "result_id": "BERGER_CAUSAL_D_CARTAN_TRANSFER_IMPORT",
        "result_state": "CONDITIONAL_CAUSAL_UNARY_AND_RAW_ARITY_TWO_TRANSFER_IMPORTED_ENDPOINT_OPEN",
        "lifecycle_layer": "CLASSICAL_BV_CONDITIONAL_CAUSAL_TRANSFER",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "setting_id": SETTING_ID,
        "formulas": {
            "unary": source["unary_transfer"]["definition"],
            "lift_54": source["unary_transfer"]["lift_54"],
            "arity_two_source": source["arity_two_transfer"]["source"],
            "arity_two_raw_primitive": source["arity_two_transfer"]["raw_primitive"],
        },
        "independent_exact_checks": checks,
        "endpoint_status": {
            "bare_local_unary_complex": "OBSTRUCTED",
            "conditional_transfer_theorem": "CERTIFIED",
            "raw_arity_two_primitive": "CONDITIONAL_NONCYCLIC",
            "cyclic_arity_two_completion": "NOT_CONSTRUCTED",
            "retained_26_row_causal_green_homotopy": "NOT_CONSTRUCTED",
            "causal_D_Cartan_extension": "NOT_CONSTRUCTED",
        },
        "claim_flags": {**source["flags"], "QUANTUM_CLAIM": False},
        "source_next_gate": "BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY",
        "active_endpoint_gate": "BERGER_RAW_ENDPOINT_EXTENSION_GREEN_OPERATORS",
        "provenance": {
            "classical_commit": CLASSICAL_COMMIT,
            "classical_sources": {path: _artifact(path) for path in CLASSICAL_SOURCES},
            "quantum_inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for name, path in QUANTUM_INPUTS.items()},
        },
        "claim_boundary": (
            "Imports and independently verifies the universal-algebra proof that a D-equivariant "
            "retained causal contraction would supply unary and raw arity-two Cartan primitives. "
            "The endpoint Green homotopy, cyclic binary completion, causal extension, residual/BFV "
            "extension, Hadamard data, QME restoration, and quantum theory remain unconstructed."
        ),
    }
