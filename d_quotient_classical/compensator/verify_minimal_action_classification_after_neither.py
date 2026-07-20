#!/usr/bin/env python3
"""Independent replay of the minimal compensator-action locus theorem."""

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
    / "d_quotient_classical"
    / "certificates"
    / "COMPENSATOR_MINIMAL_ACTION_CLASSIFICATION_AFTER_NEITHER_V1.json"
)
SCHEMA = (
    ROOT
    / "d_quotient_classical"
    / "schema"
    / "compensator-minimal-action-classification-after-neither-v1.schema.json"
)
EXPECTED_IMPORTS = {
    "action_preflight": {
        "path": "d_quotient_classical/certificates/COMPLEX_COMPENSATOR_ACTION_QUARTET_PREFLIGHT_V1.json",
        "result_id": "COMPLEX_COMPENSATOR_ACTION_QUARTET_PREFLIGHT_V1",
        "sha256": "a537e31bf667520443903551b5bf2596dff9a1c35fade88d2ffc1e89c1e0b836",
        "source_commit": "306ff78a2001f23124d412e9a2f41531bec74f78",
    },
    "positive_Berger_clock": {
        "path": "d_quotient_classical/certificates/POSITIVE_BERGER_CLOCK_BACKGROUND.json",
        "result_id": "POSITIVE_BERGER_CLOCK_BACKGROUND",
        "sha256": "35e1bb8a56b0591b3dd00aa8f22c328ad826ecd341c290564cfd1a68fcc3e687",
        "source_commit": "bb5738d6e3e30a68adcc9a70c35dac089079e3db",
    },
    "strict_trace_obstruction": {
        "path": "d_quotient_classical/certificates/TAU_ADIC_VACUUM_CYLINDER_CAUSAL_BV_TRACE_OBSTRUCTION_V1.json",
        "result_id": "TAU_ADIC_VACUUM_CYLINDER_CAUSAL_BV_TRACE_OBSTRUCTION_V1",
        "sha256": "db1f998a0920adb94cf4fcbffb1b9eb2ea6537876aff9513aac4e4d9ec2b51b9",
        "source_commit": "2b834dc751d6948366fd5c3d99174c268fa50d21",
    },
    "candidate_AB_comparison": {
        "path": "d_quotient_classical/certificates/COMPENSATOR_CANDIDATE_AB_NEITHER_COMPARISON_V1.json",
        "result_id": "COMPENSATOR_CANDIDATE_AB_NEITHER_COMPARISON_V1",
        "sha256": "5e253ebe424dd43e308622044d93af72fd6de911b927f354977413957dbb16c4",
        "source_commit": "af86eb2ce4190e48fda2d276298de844bb50f4f7",
        "lifecycle_commit": "165d339946e36e5f2d30370a6f8d9370e1a87e89",
    },
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _dense(record: dict[str, Any], symbols: dict[str, sp.Expr] | None = None) -> sp.Matrix:
    value = sp.zeros(record["row_count"], record["column_count"])
    for entry in record["entries"]:
        value[entry["row"], entry["column"]] = sp.sympify(
            entry["coefficient"], locals=symbols or {}
        )
    return value


def _check_matrix_hash(record: dict[str, Any]) -> None:
    core = {key: value for key, value in record.items() if key != "sha256"}
    if record["sha256"] != _digest(core):
        raise AssertionError("serialized matrix hash drifted")


def _reconstruct_stationary() -> tuple[sp.Matrix, sp.Matrix, sp.Matrix]:
    cylinder = sp.Matrix([[0, 36, 3, 0, -1], [0, 12, -1, 0, 1]])
    R = sp.Rational(151, 80)
    omega = sp.Rational(3, 4)
    metric = [-1, 1, 1, 1]
    ricci = [
        0,
        sp.Rational(71, 80),
        sp.Rational(71, 80),
        sp.Rational(9, 80),
    ]
    bach = [
        sp.Rational(961, 9600),
        sp.Rational(403, 9600),
        sp.Rational(403, 9600),
        sp.Rational(31, 1920),
    ]
    rows = []
    for index in (0, 1, 3):
        g = metric[index]
        rows.append(
            [
                bach[index],
                4 * R * ricci[index] - R**2 * g,
                ricci[index] - R * g / 2,
                -(omega**2) / 2,
                -1 if index == 0 else 1,
            ]
        )
    berger = sp.Matrix(rows)
    return cylinder, berger, cylinder.col_join(berger)


def verify(value: dict[str, Any] | None = None) -> None:
    payload = value if value is not None else json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)

    for name, expected in EXPECTED_IMPORTS.items():
        row = payload["dependencies"][name]
        for key, target in expected.items():
            if row[key] != target:
                raise AssertionError(f"{name} pinned {key} drifted")
        path = ROOT / row["path"]
        if _sha(path) != row["sha256"]:
            raise AssertionError(f"{name} content hash drifted")
    comparison = json.loads(
        (
            ROOT
            / payload["dependencies"]["candidate_AB_comparison"]["path"]
        ).read_text()
    )
    if (
        comparison["terminal_selection"] != "NEITHER"
        or not comparison["claim_flags"]["NEITHER_SELECTED"]
        or comparison["strict_downstream_disposition"][
            "selected_action_hash"
        ]
        is not None
    ):
        raise AssertionError("terminal comparison dependency drifted")

    declared = payload["action_family"]
    if (
        declared["coefficient_basis_mod_topology"]
        != ["alpha_B", "alpha_R", "M_P_squared", "Z_theta", "V0"]
        or "at most two compensator derivatives" not in declared["declared_scope"]
        or "higher-than-two-derivative theta operators"
        not in declared["outside_declared_minimal_class"]
        or "fixed flux or lambda_HT superselection"
        not in declared["outside_declared_minimal_class"]
    ):
        raise AssertionError("declared minimal action class drifted")
    if (
        payload["action_family_sha256"] != _digest(declared)
        or payload["content_hashes"]["action_family_sha256"]
        != payload["action_family_sha256"]
    ):
        raise AssertionError("action-family content hash drifted")

    cylinder, berger, stacked = _reconstruct_stationary()
    serialized = payload["stationary_background_equations"]
    if _dense(serialized["unit_cylinder"]["matrix"]) != cylinder:
        raise AssertionError("unit-cylinder Euler rows drifted")
    if _dense(serialized["frozen_Berger_clock"]["matrix"]) != berger:
        raise AssertionError("Berger Euler rows drifted")
    if _dense(serialized["no_HT_stacked_system"]["matrix"]) != stacked:
        raise AssertionError("stacked stationary matrix drifted")
    for record in (
        serialized["unit_cylinder"]["matrix"],
        serialized["frozen_Berger_clock"]["matrix"],
        serialized["no_HT_stacked_system"]["matrix"],
    ):
        _check_matrix_hash(record)
    if (
        sp.factor(stacked.det()) != -sp.Rational(91791, 81920)
        or stacked.rank() != 5
        or stacked.nullspace()
    ):
        raise AssertionError("exact stationary separator failed")

    # Independent fixture controls: the original Berger action solves only the
    # Berger rows; Candidate A solves only the cylinder rows.
    original_berger = sp.Matrix(
        [5, 0, -sp.Rational(1, 6), 1, sp.Rational(119, 1920)]
    )
    candidate_a = sp.Matrix(
        [5, -sp.Rational(1, 144), sp.Rational(1, 6), 1, sp.Rational(1, 4)]
    )
    if berger * original_berger != sp.zeros(3, 1):
        raise AssertionError("original Berger fixture regression failed")
    if cylinder * candidate_a != sp.zeros(2, 1):
        raise AssertionError("Candidate-A cylinder regression failed")
    if cylinder * original_berger == sp.zeros(2, 1):
        raise AssertionError("Berger fixture was silently promoted to cylinder")
    if berger * candidate_a == sp.zeros(3, 1):
        raise AssertionError("Candidate A was silently promoted to Berger")

    operators = payload["quadratic_and_global_analysis"]
    P, D, M, gamma = sp.symbols("P D M gamma", nonzero=True)
    scalar = operators["scalar_auxiliary"]
    scalar_h = _dense(scalar["operator_H_of_P"], {"P": P, "M": M})
    scalar_velocity = _dense(scalar["velocity_Hessian"])
    scalar_evolution = _dense(
        scalar["D_evolution_matrix"], {"M": M}
    )
    if (
        sp.factor(scalar_h.det()) != -9 * P**2
        or scalar_velocity.eigenvals() != {-3: 1, 3: 1}
        or scalar["velocity_inertia"] != [1, 1, 0]
    ):
        raise AssertionError("scalar auxiliary Hessian/sign drifted")
    for record in (
        scalar["operator_H_of_P"],
        scalar["velocity_Hessian"],
        scalar["D_evolution_matrix"],
    ):
        _check_matrix_hash(record)
    identity4 = sp.eye(4)
    nilpotent_part = scalar_evolution**2 - 2 * identity4
    if nilpotent_part == sp.zeros(4) or nilpotent_part**2 != sp.zeros(4):
        raise AssertionError("scalar minimal polynomial/Jordan replay failed")
    if sp.factor(scalar_evolution.charpoly().as_expr()) != (
        sp.Symbol("lambda") ** 2 - 2
    ) ** 2:
        # SymPy's charpoly generator is a fresh symbol; compare coefficients.
        if scalar_evolution.charpoly().all_coeffs() != [1, 0, -4, 0, 4]:
            raise AssertionError("scalar characteristic polynomial drifted")

    ht = operators["HT_topological"]
    ht_h = _dense(ht["operator_H_of_D"], {"D": D, "gamma": gamma})
    ht_velocity = _dense(ht["velocity_Hessian"])
    kernel = sp.Matrix([D / 2, 1, 0])
    if (
        ht_h * kernel != sp.zeros(3, 1)
        or ht_h.rank() != 2
        or ht_velocity != sp.zeros(3)
        or ht["velocity_inertia"] != [0, 0, 3]
    ):
        raise AssertionError("HT polynomial kernel drifted")
    for record in (ht["operator_H_of_D"], ht["velocity_Hessian"]):
        _check_matrix_hash(record)
    if ht["zero_frequency_kernel"] != ["0", "1", "0"]:
        raise AssertionError("HT H3 zero mode drifted")

    combined = operators["combined_auxiliary_HT"]
    combined_h = _dense(
        combined["operator_H_of_P_D"],
        {"P": P, "D": D, "M": M, "gamma": gamma},
    )
    _check_matrix_hash(combined["operator_H_of_P_D"])
    _check_matrix_hash(combined["velocity_Hessian"])
    if sp.factor(combined_h.det()) != -9 * gamma**2 * D**2 * P**2:
        raise AssertionError("combined principal determinant drifted")
    spectral = sp.Symbol("spectral")
    expected_combined_characteristic = (
        spectral**4
        - 12 * spectral**3 / M
        + spectral**2 * (gamma**2 * D**2 - 9 * P**2 - 4 * gamma**2)
        + spectral * (48 * gamma**2 - 12 * gamma**2 * D**2) / M
        - 9 * gamma**2 * D**2 * P**2
    )
    if sp.expand(
        combined_h.charpoly(spectral).as_expr()
        - expected_combined_characteristic
    ) != 0:
        raise AssertionError("combined characteristic polynomial drifted")
    cyclic_vector = sp.Matrix([0, 1, 0, 0])
    krylov = sp.Matrix.hstack(
        cyclic_vector,
        combined_h * cyclic_vector,
        combined_h**2 * cyclic_vector,
        combined_h**3 * cyclic_vector,
    )
    if sp.factor(krylov.det()) != -108 * D * P**3 * gamma**3:
        raise AssertionError("combined minimal polynomial witness drifted")
    combined_zero = combined_h.subs(D, 0)
    if combined_zero * sp.Matrix([0, 0, 1, 0]) != sp.zeros(4, 1):
        raise AssertionError("combined global D-zero kernel drifted")

    topology = payload["topology"]
    if (
        topology["ordinary_de_Rham_betti_H0_to_H4"] != [1, 0, 0, 1, 0]
        or topology["compact_support_betti_Hc0_to_Hc4"]
        != [0, 1, 0, 0, 1]
        or topology["small_gauge_exact"]
        or topology["Berger_raw_D_shift"] != "L_D A3_bar=vol_Berger"
    ):
        raise AssertionError("topological/global separator drifted")

    classification = payload["seven_gate_classification"]
    selection = payload["selection"]
    if (
        classification["all_seven_gate_good_locus"] != "EMPTY"
        or classification["epsilon_HT_zero"]["stationary_coefficient_locus"]
        != "ZERO_VECTOR_ONLY"
        or classification["epsilon_HT_one"]["decisive_failure_gates"]
        != [3, 5, 6, 7]
        or selection["candidate_C_selected"]
        or selection["candidate_C_action"] is not None
        or selection["candidate_C_action_hash"] is not None
        or selection["hybrid_selected"]
        or selection["downstream_selected_action_work_authorized"]
        or payload["claim_flags"]["UNIVERSAL_COMPENSATOR_NO_GO"]
        or payload["claim_flags"]["HADAMARD_OR_QUANTUM_RESULT"]
    ):
        raise AssertionError("empty-locus claim boundary drifted")
    expected_content_hashes = {
        "action_family_sha256": _digest(payload["action_family"]),
        "stationary_system_sha256": _digest(
            payload["stationary_background_equations"]
        ),
        "quadratic_global_sha256": _digest(
            payload["quadratic_and_global_analysis"]
        ),
        "classification_sha256": _digest(
            payload["seven_gate_classification"]
        ),
    }
    if payload["content_hashes"] != expected_content_hashes:
        raise AssertionError("classification content hashes drifted")


if __name__ == "__main__":
    verify()
    print(
        "COMPENSATOR_MINIMAL_ACTION_CLASSIFICATION_AFTER_NEITHER_V1 "
        "INDEPENDENT REPLAY: PASS"
    )
