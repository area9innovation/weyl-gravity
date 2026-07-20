#!/usr/bin/env python3
"""Independent charge-lattice replay of the Level-4 Weyl-connection no-go."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = (
    ROOT
    / "d_quotient_classical/certificates/"
    "COMPENSATOR_INDEPENDENT_WEYL_CONNECTION_LEVEL4_NO_GO_V1.json"
)
SCHEMA = (
    ROOT
    / "d_quotient_classical/schema/"
    "compensator-independent-weyl-connection-level4-no-go-v1.schema.json"
)
LEVEL3_HASH = "2e687331b6985b3a84c54a0f05b210bee5e3ac06d5659b5603ac9bc25f61dfed"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _dense(record: dict[str, Any]) -> sp.Matrix:
    result = sp.zeros(record["row_count"], record["column_count"])
    for item in record["entries"]:
        result[item["row"], item["column"]] = sp.sympify(item["coefficient"])
    return result


def _charge_lattice_replay(payload: dict[str, Any]) -> None:
    a, b = sp.symbols("a b")
    # Reconstruct the action on log sqrt-scale(g), log rho and the normalized
    # longitudinal connection without importing the producer.
    columns = [
        sp.Matrix([1, -1, -1]),
        sp.Matrix([a, -b, -a]),
    ]
    G = sp.Matrix.hstack(*columns)
    if sp.factor(G[:2, :].det()) != a - b:
        raise AssertionError("INDEPENDENCE_MINOR_MISMATCH")
    if _dense(payload["gauge_rank_and_reducibility"]["gauge_symbol"]) != G:
        raise AssertionError("SERIALIZED_GAUGE_SYMBOL_MISMATCH")

    G_dep = G.subs(b, a)
    z = sp.Matrix([-a, 1])
    if G_dep.rank() != 1 or G_dep * z != sp.zeros(3, 1):
        raise AssertionError("REDUCIBILITY_REPLAY_MISMATCH")


def _constant_weight_replay(payload: dict[str, Any]) -> None:
    a, b = sp.symbols("a b")
    Delta = a - b
    # In four dimensions:
    # sqrt(g): 4a; g^-1: -2a; rho^2: -2b; rho^4: -4b;
    # R_W: -2a. Therefore all two-derivative compensator terms
    # have weight 2(a-b), and rho^4 has weight 4(a-b).
    weights = {
        "radial_kinetic": sp.factor(4 * a - 2 * a - 2 * b),
        "rho_squared_R_W": sp.factor(4 * a - 2 * b - 2 * a),
        "phase_kinetic": sp.factor(4 * a - 2 * a - 2 * b),
        "quartic_potential": sp.factor(4 * a - 4 * b),
    }
    expected = {
        "radial_kinetic": 2 * Delta,
        "rho_squared_R_W": 2 * Delta,
        "phase_kinetic": 2 * Delta,
        "quartic_potential": 4 * Delta,
    }
    if any(
        sp.simplify(weights[key] - expected[key]) != 0 for key in weights
    ):
        raise AssertionError("CONSTANT_WEIGHT_REPLAY_MISMATCH")
    serialized = payload["exact_Ward_locus"][
        "constant_candidate_Weyl_weights"
    ]
    Delta_symbol = sp.Symbol("Delta")
    expected_serialized = {
        "radial_kinetic": 2 * Delta_symbol,
        "rho_squared_R_W": 2 * Delta_symbol,
        "phase_kinetic": 2 * Delta_symbol,
        "quartic_potential": 4 * Delta_symbol,
    }
    for key, value in expected_serialized.items():
        if sp.factor(sp.sympify(serialized[key]) - value) != 0:
            raise AssertionError("SERIALIZED_WEIGHT_MISMATCH")


def _branch_elimination_replay(payload: dict[str, Any]) -> None:
    Delta, kr, kR, kt, lam, u = sp.symbols(
        "Delta kappa_r kappa_R kappa_theta lambda u"
    )
    # Saturate by Delta using 1-u Delta. The independent branch must force
    # every compensator coefficient to zero.
    ideal = [
        Delta * kr,
        Delta * kR,
        Delta * kt,
        Delta * lam,
        1 - u * Delta,
    ]
    gb = sp.groebner(ideal, u, Delta, kr, kR, kt, lam, order="lex")
    for coefficient in (kr, kR, kt, lam):
        if gb.reduce(coefficient)[1] != 0:
            raise AssertionError("INDEPENDENT_BRANCH_ELIMINATION_MISMATCH")
    forced = payload["exact_Ward_locus"]["complete_strata"][
        "Delta_nonzero"
    ]["forced_zero_coefficients"]
    if forced != ["kappa_r", "kappa_R", "kappa_theta", "lambda"]:
        raise AssertionError("SERIALIZED_FORCED_ZERO_SET_MISMATCH")


def verify(value: dict[str, Any] | None = None) -> None:
    payload = value if value is not None else json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)

    imported = payload["imports"]["level3_no_go"]
    import_path = ROOT / imported["path"]
    if _sha(import_path) != LEVEL3_HASH or imported["sha256"] != LEVEL3_HASH:
        raise AssertionError("LEVEL3_IMPORT_DRIFT")
    level3 = json.loads(import_path.read_text())
    if level3["terminal_verdict"]["selected_level3_action"]:
        raise AssertionError("LEVEL3_SELECTED_ACTION_CONTRADICTS_GATE")

    _charge_lattice_replay(payload)
    _constant_weight_replay(payload)
    _branch_elimination_replay(payload)

    for field, section in (
        ("imports_sha256", "imports"),
        ("action_sha256", "complete_minimal_action"),
        ("rank_sha256", "gauge_rank_and_reducibility"),
        ("ward_sha256", "exact_Ward_locus"),
        ("bv_sha256", "minimal_BV_data"),
        ("separator_sha256", "charge_and_cohomology_separator"),
        ("gates_sha256", "gate_disposition"),
        ("verdict_sha256", "terminal_verdict"),
    ):
        if payload["content_hashes"][field] != _digest(payload[section]):
            raise AssertionError(f"{field} drifted")

    if (
        payload["terminal_verdict"][
            "independent_trace_gauge_and_nonzero_clock_charge_intersection"
        ]
        != "EMPTY"
        or payload["terminal_verdict"]["selected_level4_action"]
        or payload["gate_disposition"]["selected_action"]
        or payload["gate_disposition"]["support_local_Green_parent"]
        or payload["gate_disposition"]["nonlinear_q2"]
        or any(payload["claim_flags"].values())
    ):
        raise AssertionError("CLAIM_BOUNDARY_DRIFT")


def main() -> None:
    verify()
    print(
        "COMPENSATOR_INDEPENDENT_WEYL_CONNECTION_LEVEL4_NO_GO_V1 "
        "independent charge-lattice replay: PASS"
    )


if __name__ == "__main__":
    main()
