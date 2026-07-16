"""Pinned import of the restricted support-local pp-wave branch bracket."""

from __future__ import annotations

from functools import lru_cache
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any

import sympy as sp


TRANSFER_ROOT = Path(__file__).resolve().parent
ROOT = TRANSFER_ROOT.parents[1]
BRIDGE_COMMIT = "1c4eb856a191f5795e44c0ff1bc1afce644a9e88"
CERTIFICATE_RELATIVE = "bridge/certificates/ppwave_bach_branch_closure.json"
SCHEMA_RELATIVE = "bridge/einstein_sector/schema/ppwave_bach_branch_closure.schema.json"
PRODUCER_RELATIVE = "bridge/einstein_sector/ppwave_bach_branch_closure.py"
VERIFIER_RELATIVE = "bridge/einstein_sector/verify_ppwave_bach_branch_closure.py"
TEST_RELATIVE = "bridge/einstein_sector/tests/test_ppwave_bach_branch_closure.py"
REPORT_RELATIVE = "reports/ppwave-bach-branch-closure.md"


@lru_cache(maxsize=1)
def _git_prefix() -> str:
    return subprocess.run(
        ["git", "rev-parse", "--show-prefix"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _git_blob(relative: str) -> bytes:
    result = subprocess.run(
        ["git", "show", f"{BRIDGE_COMMIT}:{_git_prefix()}{relative}"],
        cwd=ROOT,
        check=False,
        capture_output=True,
    )
    if result.returncode:
        raise ValueError(f"missing pinned pp-wave bridge artifact {relative}")
    return result.stdout


def _git_json(relative: str) -> dict[str, Any]:
    value = json.loads(_git_blob(relative))
    if not isinstance(value, dict):
        raise ValueError(f"pinned pp-wave JSON is not an object: {relative}")
    return value


def _artifact(relative: str) -> dict[str, str]:
    return {
        "path": relative,
        "commit": BRIDGE_COMMIT,
        "sha256": hashlib.sha256(_git_blob(relative)).hexdigest(),
    }


def validate_bridge_payload(
    payload: object, schema: object
) -> tuple[dict[str, Any], dict[str, bool]]:
    """Independently check the branch algebra and fail-closed scope."""

    if not isinstance(payload, dict) or not isinstance(schema, dict):
        raise ValueError("pp-wave payload or schema is not an object")
    if (
        schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema"
        or schema.get("$id")
        != "https://area9.dk/schemas/ppwave-bach-branch-closure-v1.schema.json"
        or schema.get("additionalProperties") is not False
    ):
        raise ValueError("pp-wave schema identity or strictness drifted")
    if (
        payload.get("schema") != "ppwave-bach-branch-closure-v1"
        or payload.get("result_id") != "PPWAVE_BACH_BRANCH_CLOSURE"
        or payload.get("result_state")
        != "RESTRICTED_SUPPORT_LOCAL_EINSTEIN_EXTRA_WEYL_Q2_ZERO"
        or payload.get("dependency_tags") != ["LOCAL-ALGEBRAIC"]
    ):
        raise ValueError("pp-wave bridge result identity drifted")

    u, x, y = sp.symbols("u x y", real=True)
    f = sp.Function("f")(u)
    g = sp.Function("g")(u)
    einstein = f * (x**2 - y**2)
    extra = g * x**3
    a, b = sp.symbols("a b")

    def delta(value: sp.Expr) -> sp.Expr:
        return sp.factor(sp.diff(value, x, 2) + sp.diff(value, y, 2))

    _require_equal(delta(einstein), 0, "Einstein profile")
    _require_equal(delta(extra), 6 * x * g, "extra-Weyl Ricci profile")
    _require_equal(delta(delta(extra)), 0, "extra-Weyl Bach profile")
    bach = sp.factor(-delta(delta(a * einstein + b * extra)) / 4)
    _require_equal(bach, 0, "mixed exact Bach solution")
    q2 = {
        "Einstein_Einstein": sp.diff(bach, a, 2),
        "Einstein_extraWeyl": sp.diff(bach, a, b),
        "extraWeyl_extraWeyl": sp.diff(bach, b, 2),
    }
    declared_q2 = payload.get("restricted_nonlinear_tensor", {}).get("q2_entries")
    if declared_q2 != {name: str(value) for name, value in q2.items()}:
        raise ValueError("pp-wave restricted q2 coefficients drifted")

    branches = payload.get("branch_representatives", {})
    if (
        branches.get("Einstein", {}).get("Ricci_flat") is not True
        or branches.get("extra_Weyl", {}).get("Ricci_flat") is not False
        or branches.get("extra_Weyl", {}).get("Bach_flat") is not True
        or branches.get("sum_is_exact_Bach_solution") is not True
    ):
        raise ValueError("pp-wave branch labels or closure drifted")
    mixing = payload.get("branch_mixing_verdict", {})
    if mixing.get("restricted_branches_close_together") is not True or any(
        value != "ZERO"
        for name, value in mixing.items()
        if name != "restricted_branches_close_together"
    ):
        raise ValueError("pp-wave branch-mixing table drifted")
    transfer = payload.get("transfer_disposition", {})
    if (
        transfer.get("restricted_ell2")
        != "pi_cl q2(iota_cl tensor iota_cl)=0"
        or transfer.get("homotopy_choice_affects_result") is not False
    ):
        raise ValueError("pp-wave transferred ell2 drifted")

    exact_checks = payload.get("exact_checks", {})
    if not exact_checks or any(value is not True for value in exact_checks.values()):
        raise ValueError("pp-wave exact check dropped")
    flags = payload.get("flags", {})
    for name in (
        "RESTRICTED_SUPPORT_LOCAL_Q2_BLOCK",
        "ACTUAL_EINSTEIN_EXTRA_WEYL_BRANCH_LABELS",
        "RESTRICTED_TRANSFERRED_ELL2_COMPUTED",
    ):
        if flags.get(name) is not True:
            raise ValueError("pp-wave positive claim dropped")
    for name in (
        "FULL_SUPPORT_LOCAL_BV_Q2",
        "COMPLETE_54_ROW_TRANSFER",
        "WEYL_SQUARE_DEFORMATION_CENTRALITY_TESTED",
        "LORENTZIAN_CAUSAL_CERTIFIED",
        "QME_RESTORED",
    ):
        if flags.get(name) is not False:
            raise ValueError("pp-wave claim boundary drifted")
    return payload, {
        "strict_schema_identity": True,
        "pinned_artifact_hashes_available": True,
        "Einstein_branch_recomputed": True,
        "extra_Weyl_branch_recomputed": True,
        "mixed_exact_solution_recomputed": True,
        "restricted_q2_recomputed": True,
        "branch_mixing_table_zero": True,
        "restricted_ell2_zero_before_projection": True,
        "homotopy_independence_exact": True,
        "claim_boundary_fail_closed": True,
    }


def _require_equal(left: sp.Expr, right: sp.Expr | int, label: str) -> None:
    if sp.factor(left - right) != 0:
        raise ValueError(f"pp-wave {label} identity failed")


def build_import() -> dict[str, Any]:
    payload, checks = validate_bridge_payload(
        _git_json(CERTIFICATE_RELATIVE), _git_json(SCHEMA_RELATIVE)
    )
    return {
        "schema": "quantum-weyl-ppwave-branch-transfer-import-v1",
        "result_id": "PPWAVE_EINSTEIN_EXTRA_WEYL_TRANSFERRED_ELL2",
        "result_state": "RESTRICTED_SUPPORT_LOCAL_BRANCH_MIXING_ELL2_EXACTLY_ZERO",
        "lifecycle_layer": "INTERACTING",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "bridge_source": {
            "commit": BRIDGE_COMMIT,
            "artifacts": {
                name: _artifact(relative)
                for name, relative in (
                    ("certificate", CERTIFICATE_RELATIVE),
                    ("schema", SCHEMA_RELATIVE),
                    ("producer", PRODUCER_RELATIVE),
                    ("independent_verifier", VERIFIER_RELATIVE),
                    ("tests", TEST_RELATIVE),
                    ("report", REPORT_RELATIVE),
                )
            },
        },
        "exact_import_checks": checks,
        "support_local_block": {
            "geometry": payload["geometry"]["metric"],
            "profile_scope": payload["geometry"]["profile_dependence"],
            "q1": payload["restricted_nonlinear_tensor"]["q1"],
            "q2": payload["restricted_nonlinear_tensor"]["q2_entries"],
            "arbitrary_profile_not_mode_truncated": True,
            "full_BV_block": False,
        },
        "branch_content": payload["branch_representatives"],
        "transferred_bracket": {
            "formula": "ell2=pi_cl q2(iota_cl tensor iota_cl)",
            "Einstein_Einstein": "0",
            "Einstein_extraWeyl": "0",
            "extraWeyl_extraWeyl": "0",
            "homotopy_independent": True,
            "reason": "the restricted q2 vanishes before projection",
            "higher_restricted_brackets_from_classical_Bach_Taylor_tensors": "0",
        },
        "physical_interpretation": {
            "Einstein_and_extra_Weyl_close_on_declared_sector": True,
            "negative_direction_reintroduced_by_ell2": False,
            "extra_Weyl_pairing_sign_classified": False,
            "centered_Weyl_square_deformation_classes_tested": False,
            "one_particle_cohomology_statement": "NOT_ADDRESSED",
        },
        "claim_flags": {
            "RESTRICTED_SUPPORT_LOCAL_BRANCH_ELL2_COMPUTED": True,
            "ACTUAL_EINSTEIN_EXTRA_WEYL_MIXING_TESTED": True,
            "ALIGNED_PPWAVE_BRANCHES_CLOSE": True,
            "NONALIGNED_BRANCH_MIXING_CLASSIFIED": False,
            "FULL_SUPPORT_LOCAL_BV_Q2": False,
            "COMPLETE_54_ROW_TRANSFER": False,
            "WEYL_SQUARE_DEFORMATION_CENTRALITY_TESTED": False,
            "LORENTZIAN_CERTIFIED": False,
            "QME_RESTORED": False,
        },
        "claim_boundary": "This pinned LOCAL-ALGEBRAIC import computes the transferred ell2 on an arbitrary-profile, aligned Brinkmann pp-wave metric sector carrying genuine Einstein and non-Einstein biharmonic Weyl representatives. Exact Bach linearity makes every restricted branch-mixing entry zero before projection. It is not the complete support-local BV q2 or 54-row transfer and does not classify nonaligned vertices, centered Weyl-square deformation classes, pairing positivity, causal propagation, or quantum corrections.",
        "next_gate": "NONALIGNED_SUPPORT_LOCAL_BRANCH_BLOCK_OR_COMPLETE_54_ROW_Q2",
    }
