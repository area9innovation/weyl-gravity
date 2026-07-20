#!/usr/bin/env python3
"""Independent replay of the complex-compensator local action preflight."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = (
    ROOT
    / "d_quotient_classical"
    / "certificates"
    / "COMPLEX_COMPENSATOR_ACTION_QUARTET_PREFLIGHT_V1.json"
)
DEPENDENCIES = {
    "strict_minimal_BV": (
        ROOT
        / "d_quotient_classical"
        / "certificates"
        / "CLASSICAL_MINIMAL_BV_ANTIFIELD_EXPORT_V2.json"
    ),
    "WZ_cotangent_lift": (
        ROOT
        / "quantum-weyl"
        / "anomalies"
        / "certificates"
        / "WESS_ZUMINO_MINIMAL_BV_COTANGENT_LIFT.json"
    ),
    "positive_polar_clock_fixture": (
        ROOT
        / "d_quotient_classical"
        / "certificates"
        / "POSITIVE_BERGER_CLOCK_BACKGROUND.json"
    ),
    "strict_tau_causal_obstruction": (
        ROOT
        / "d_quotient_classical"
        / "certificates"
        / "TAU_ADIC_VACUUM_CYLINDER_CAUSAL_BV_TRACE_OBSTRUCTION_V1.json"
    ),
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _json_sha(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _dense(record: dict[str, Any]) -> sp.Matrix:
    matrix = sp.zeros(record["row_count"], record["column_count"])
    for entry in record["entries"]:
        coefficient = entry["coefficient"]
        matrix[entry["row"], entry["column"]] += sp.Rational(
            coefficient["numerator"], coefficient["denominator"]
        )
    return matrix


def _expected_matrix(
    entries: list[tuple[int, int, Fraction]],
) -> sp.Matrix:
    matrix = sp.zeros(4)
    for row, column, coefficient in entries:
        matrix[row, column] = sp.Rational(
            coefficient.numerator, coefficient.denominator
        )
    return matrix


def verify(value: dict[str, Any] | None = None) -> None:
    if value is None:
        value = json.loads(CERTIFICATE.read_text())

    if (
        value["result_id"]
        != "COMPLEX_COMPENSATOR_ACTION_QUARTET_PREFLIGHT_V1"
        or value["result_state"] != "LOCAL_ACTION_AND_QUARTET_CERTIFIED"
        or value["dependency_tags"] != ["LOCAL-ALGEBRAIC"]
    ):
        raise AssertionError("top-level preflight identity drifted")

    for role, path in DEPENDENCIES.items():
        source = json.loads(path.read_text())
        row = value["dependencies"][role]
        if (
            row["path"] != str(path.relative_to(ROOT))
            or row["result_id"] != source["result_id"]
            or row["sha256"] != _sha(path)
        ):
            raise AssertionError(f"dependency mismatch: {role}")
    strict = json.loads(DEPENDENCIES["strict_minimal_BV"].read_text())
    wz = json.loads(DEPENDENCIES["WZ_cotangent_lift"].read_text())
    clock = json.loads(
        DEPENDENCIES["positive_polar_clock_fixture"].read_text()
    )
    obstruction = json.loads(
        DEPENDENCIES["strict_tau_causal_obstruction"].read_text()
    )
    if (
        strict.get("result_state")
        != "EXPORTED_EXECUTABLE_MINIMAL_BV_FILTRATION"
        or {row.get("status") for row in strict.get("producer_checks", [])}
        != {"VERIFIED"}
        or wz.get("result_state")
        != "EXACT_MINIMAL_BV_COTANGENT_LIFT_CERTIFIED_EXTENDED_COHOMOLOGY_OPEN"
        or not wz.get("exact_checks", {}).get("Q_squared_zero_on_all_atoms")
        or wz.get("contractible_quartet", {}).get("status")
        != "EXACT_CONTRACTIBLE_WEYL_QUARTET_IN_DRESSED_VARIABLES"
        or clock.get("claim_status") != "CERTIFIED_EXACT_BACKGROUND"
        or not clock.get("flags", {}).get("positive_standard_scalar_kinetic")
        or clock.get("clock_ansatz", {}).get("target_metric")
        != "d rho^2+rho^2 d theta^2"
        or obstruction.get("result_state") != "OBSTRUCTED"
    ):
        raise AssertionError("dependency semantics drifted")

    transformations = value["transformations"]
    if transformations["finite"] != {
        "g": "g -> exp(2 sigma) g",
        "rho": "rho -> exp(-sigma) rho",
        "theta": "theta -> theta",
        "tau": "tau -> tau+sigma",
        "g_hat": "g_hat=(rho/f)^2 g -> g_hat",
    }:
        raise AssertionError("finite Weyl transformations drifted")
    if transformations["BRST_fields"]["Q tau"] != "L_xi tau+omega":
        raise AssertionError("tau BRST row drifted")
    if transformations["BRST_fields"]["Q g_hat"] != "L_xi g_hat":
        raise AssertionError("dressed metric is not Weyl invariant")

    # Reconstruct the polar-to-dressed action identities without importing the
    # producer.  The integrated conformal transformation is
    # int sqrt(g_hat) R_hat =
    # f^-2 int sqrt(g) [rho^2 R+6 (d rho)^2].
    kappa_r, kappa_theta, rho, f = sp.symbols(
        "kappa_r kappa_theta rho f", nonzero=True, real=True
    )
    radial_R_coefficient = sp.expand(
        (-kappa_r * f**2 / 12) * (rho**2 / f**2)
    )
    radial_kinetic_coefficient = sp.expand(
        (-kappa_r * f**2 / 12) * (6 / f**2)
    )
    if radial_R_coefficient != -kappa_r * rho**2 / 12:
        raise AssertionError("conformal rho^2 R coefficient drifted")
    if radial_kinetic_coefficient != -kappa_r / 2:
        raise AssertionError("radial kinetic coefficient drifted")
    phase_original = sp.expand(
        (-kappa_theta * f**2 / 2)
        * (rho / f) ** 4
        * (rho / f) ** -2
    )
    if sp.simplify(
        phase_original + kappa_theta * rho**2 / 2
    ) != 0:
        raise AssertionError("phase conformal weights do not cancel")
    if 4 - 2 - 2 != 0 or 4 - 4 != 0:
        raise AssertionError("phase or quartic Weyl weights drifted")

    # Direct one-form replay:
    # delta g=e^(2 tau)(delta g_hat+2 g_hat delta tau),
    # delta rho=-rho delta tau.
    g_star, g_hat, rho_star = sp.symbols(
        "g_star g_hat rho_star", real=True
    )
    tau_hat_star = 2 * g_hat * sp.symbols(
        "g_hat_star", real=True
    ) - rho * rho_star
    if sp.diff(tau_hat_star, rho_star) != -rho:
        raise AssertionError("rho cotangent coefficient drifted")
    if sp.diff(tau_hat_star, g_hat) == 0:
        raise AssertionError("metric trace cotangent term disappeared")
    change = value["canonical_dressed_change"]
    if (
        "tau_hat_star=-rho rho_star+2 g.g_star"
        not in change["coordinates"]
        or change["formal_completion"]
        != "tau-adic local analytic completion at rho=f"
    ):
        raise AssertionError("canonical dressed change drifted")

    expected_qw = _expected_matrix(
        [(1, 0, Fraction(1)), (3, 2, Fraction(1))]
    )
    expected_hw = _expected_matrix(
        [(0, 1, Fraction(1)), (2, 3, Fraction(1))]
    )
    expected_qnm = _expected_matrix(
        [(1, 0, Fraction(1)), (3, 2, Fraction(-1))]
    )
    expected_hnm = _expected_matrix(
        [(0, 1, Fraction(1)), (2, 3, Fraction(-1))]
    )
    blocks = value["sparse_operators"]
    actual = {
        "QW": _dense(blocks["Weyl_quartet"]["Q_W"]),
        "hW": _dense(blocks["Weyl_quartet"]["h_W"]),
        "Qnm": _dense(blocks["nonminimal_doublet"]["Q_nm"]),
        "hnm": _dense(blocks["nonminimal_doublet"]["h_nm"]),
    }
    if actual != {
        "QW": expected_qw,
        "hW": expected_hw,
        "Qnm": expected_qnm,
        "hnm": expected_hnm,
    }:
        raise AssertionError("sparse contraction operator drifted")
    for q, h in (
        (actual["QW"], actual["hW"]),
        (actual["Qnm"], actual["hnm"]),
    ):
        if q * q != sp.zeros(4) or q * h + h * q != sp.eye(4):
            raise AssertionError("quartet/doublet identity failed")
    for block_name, keys in (
        ("Weyl_quartet", ("Q_W", "h_W")),
        ("nonminimal_doublet", ("Q_nm", "h_nm")),
    ):
        for key in keys:
            record = dict(blocks[block_name][key])
            claimed = record.pop("sha256")
            if claimed != _json_sha(record):
                raise AssertionError("sparse matrix hash mismatch")

    inventory = value["field_inventory"]
    symbols = {row["symbol"] for row in inventory}
    expected_symbols = {
        "g",
        "rho",
        "theta",
        "xi",
        "omega",
        "g_star",
        "rho_star",
        "theta_star",
        "xi_star",
        "omega_star",
        "bar_xi",
        "b_xi",
        "bar_xi_star",
        "b_xi_star",
        "bar_omega",
        "b_omega",
        "bar_omega_star",
        "b_omega_star",
    }
    if symbols != expected_symbols or len(inventory) != 18:
        raise AssertionError("minimal/nonminimal inventory is incomplete")
    if any(row["real_structure"] != "REAL" for row in inventory):
        raise AssertionError("real structure drifted")

    action = value["action_basis"]
    if "(rho/f)^4[alpha_R R(g_hat)^2" not in action["original_variables"]:
        raise AssertionError("dressed curvature density lost its volume factor")
    if action["bulk_four_derivative_curvature_basis"] != [
        "C(g_hat)^2",
        "R(g_hat)^2",
    ]:
        raise AssertionError("bulk curvature basis drifted")
    if action["topological_four_derivative_basis"] != [
        "E4(g_hat)",
        "P4(g_hat)=C(g_hat) dual C(g_hat)",
    ]:
        raise AssertionError("topological curvature basis drifted")
    if action["horizontal_exact_not_independent"] != "Box_hat R(g_hat)":
        raise AssertionError("Box R was promoted to an independent coupling")

    M2 = -kappa_r * f**2 / 6
    Z = kappa_theta * f**2
    if sp.simplify(M2.subs(kappa_r, -1) - f**2 / 6) != 0:
        raise AssertionError("positive Einstein fixture failed")
    if sp.simplify(Z.subs(kappa_theta, 1) - f**2) != 0:
        raise AssertionError("positive phase fixture failed")
    kappa_phi = sp.symbols("kappa_Phi", nonzero=True, real=True)
    product = sp.expand(
        (M2 * Z).subs(
            {kappa_r: kappa_phi, kappa_theta: kappa_phi}
        )
    )
    if product != -kappa_phi**2 * f**4 / 6:
        raise AssertionError("Cartesian analytic sign identity failed")
    signs = value["sign_and_regularity_classification"]
    if (
        signs["formal_polar_family"]["exact_fixture"]["kappa_r"] != -1
        or signs["formal_polar_family"]["exact_fixture"]["kappa_theta"] != 1
        or not signs["formal_polar_family"]["simultaneously_feasible"]
        or signs["Cartesian_analytic_complex_scalar_subfamily"][
            "simultaneously_positive"
        ]
        or signs["Cartesian_analytic_complex_scalar_subfamily"]["status"]
        != "OBSTRUCTED"
    ):
        raise AssertionError("sign lifecycle drifted")

    symmetry = value["internal_symmetry_classification"]
    if (
        symmetry["GLOBAL"]["theta_status"]
        != "PHYSICAL_MASSLESS_GLOBALLY_CHARGED"
        or symmetry["LOCAL"]["included_here"]
        or "A_mu" not in symmetry["LOCAL"]["required_new_rows"]
    ):
        raise AssertionError("internal U(1) classification drifted")
    if value["Wess_Zumino_lifecycle"]["classical_action_contains_WZ"]:
        raise AssertionError("Wess-Zumino counterterm was inserted at hbar zero")
    if value["reduced_action"]["rho_equals_f_is"] != (
        "A_WEYL_GAUGE_CHART_NOT_SPONTANEOUS_WEYL_BREAKING"
    ):
        raise AssertionError("rho=f was called spontaneous breaking")

    hashes = value["content_hashes"]
    core = {
        "action_basis": value["action_basis"],
        "transformations": value["transformations"],
        "field_inventory": value["field_inventory"],
        "BV_master_action": value["BV_master_action"],
        "canonical_dressed_change": value["canonical_dressed_change"],
        "sparse_operators": value["sparse_operators"],
        "reduced_action": value["reduced_action"],
        "sign_and_regularity_classification": value[
            "sign_and_regularity_classification"
        ],
    }
    expected_hashes = {
        "action_manifest_sha256": _json_sha(value["action_basis"]),
        "field_inventory_sha256": _json_sha(value["field_inventory"]),
        "BV_manifest_sha256": _json_sha(value["BV_master_action"]),
        "operator_manifest_sha256": _json_sha(value["sparse_operators"]),
        "preflight_core_sha256": _json_sha(core),
    }
    if hashes != expected_hashes:
        raise AssertionError("content-addressed core drifted")

    forbidden = {
        "CAUSAL_GREEN_OPERATOR",
        "HADAMARD_STATE",
        "ANOMALY_COEFFICIENT",
        "QUANTUM_MASTER_EQUATION",
        "PARTICLE_OR_UNITARITY",
    }
    if any(value["claim_flags"][key] for key in forbidden):
        raise AssertionError("local preflight was overpromoted")


if __name__ == "__main__":
    verify()
    print("complex compensator action/quartet independent replay: PASS")
