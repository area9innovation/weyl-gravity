#!/usr/bin/env python3
"""Independent audit of the changed-action complex-compensator causal parent.

This verifier deliberately does not import the producer.  It reconstructs
the rational background tuning, the eight-row endpoint identities, the
iterated Green inverse and the fail-closed claim boundary from the emitted
certificate and immutable dependencies.
"""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, ValidationError
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = (
    ROOT
    / "d_quotient_classical"
    / "certificates"
    / "COMPLEX_COMPENSATOR_VACUUM_CYLINDER_CAUSAL_PARENT_V1.json"
)
SCHEMA = (
    ROOT
    / "d_quotient_classical"
    / "schema"
    / "complex-compensator-vacuum-cylinder-causal-parent-v1.schema.json"
)
DEPENDENCIES = {
    "action_preflight": (
        ROOT
        / "d_quotient_classical"
        / "certificates"
        / "COMPLEX_COMPENSATOR_ACTION_QUARTET_PREFLIGHT_V1.json"
    ),
    "strict_tau_trace_obstruction": (
        ROOT
        / "d_quotient_classical"
        / "certificates"
        / "TAU_ADIC_VACUUM_CYLINDER_CAUSAL_BV_TRACE_OBSTRUCTION_V1.json"
    ),
    "strict_386_Green_homotopy": (
        ROOT
        / "covariant_completion"
        / "certificates"
        / "curved_full_prolonged_green_homotopy_assembly.json"
    ),
    "strict_30_endpoint": (
        ROOT
        / "covariant_completion"
        / "certificates"
        / "curved_prolonged_metric_endpoint_complex.json"
    ),
    "causal_transfer_theorem": (
        ROOT
        / "d_quotient_classical"
        / "certificates"
        / "GREEN_HYPERBOLIC_CYCLIC_TRANSFER_THEOREM_V1.json"
    ),
}
SOURCE_COMMITS = {
    "action_preflight": "306ff78a2001f23124d412e9a2f41531bec74f78",
    "strict_tau_trace_obstruction": (
        "2b834dc751d6948366fd5c3d99174c268fa50d21"
    ),
    "strict_386_Green_homotopy": (
        "c5f811e120bc05198baa35a9b5491d8a46ae1295"
    ),
    "strict_30_endpoint": "6ebd72043d61dd3ca9a8cd571321424408762cd5",
    "causal_transfer_theorem": (
        "59ef411a0d6cbdd079853333c224f57385cbe98f"
    ),
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _fraction(record: dict[str, int]) -> Fraction:
    return Fraction(record["numerator"], record["denominator"])


def _operator(record: dict[str, Any], symbols: dict[str, sp.Expr]) -> sp.Matrix:
    matrix = sp.zeros(record["row_count"], record["column_count"])
    for entry in record["entries"]:
        matrix[entry["row"], entry["column"]] += symbols[
            entry["coefficient"]
        ]
    return matrix


def _pairing(record: dict[str, Any]) -> sp.Matrix:
    matrix = sp.zeros(record["row_count"], record["column_count"])
    for entry in record["entries"]:
        matrix[entry["row"], entry["column"]] += sp.Rational(
            entry["coefficient"]["numerator"],
            entry["coefficient"]["denominator"],
        )
    return matrix


def _check_matrix_hash(record: dict[str, Any]) -> None:
    core = dict(record)
    claimed = core.pop("sha256")
    if claimed != _digest(core):
        raise AssertionError("sparse operator hash mismatch")


def _verify_dependencies(value: dict[str, Any]) -> None:
    loaded: dict[str, dict[str, Any]] = {}
    for role, path in DEPENDENCIES.items():
        source = json.loads(path.read_text())
        loaded[role] = source
        row = value["dependencies"][role]
        if row != {
            "path": str(path.relative_to(ROOT)),
            "artifact_id": source.get("result_id", source.get("schema")),
            "sha256": _sha(path),
            "source_commit": SOURCE_COMMITS[role],
        }:
            raise AssertionError(f"dependency mismatch: {role}")

    preflight = loaded["action_preflight"]
    if (
        preflight["result_state"] != "LOCAL_ACTION_AND_QUARTET_CERTIFIED"
        or not preflight["claim_flags"]["RADIAL_QUARTET_CERTIFIED"]
        or not preflight["claim_flags"][
            "FORMAL_POLAR_EINSTEIN_PHASE_SIGN_FEASIBLE"
        ]
        or preflight["claim_flags"]["CAUSAL_GREEN_OPERATOR"]
    ):
        raise AssertionError("action preflight semantics drifted")

    obstruction = loaded["strict_tau_trace_obstruction"]
    if (
        obstruction["result_state"] != "OBSTRUCTED"
        or obstruction["scalar_trace_obstruction"]["principal_symbol"][
            "dressed_trace_Hessian"
        ]
        != "0 for every nonzero covector"
        or not obstruction["claim_flags"][
            "COMPLETE_DECLARED_FINITE_DIFFERENTIAL_CLASS_OBSTRUCTED"
        ]
    ):
        raise AssertionError("strict tau obstruction semantics drifted")

    green = loaded["strict_386_Green_homotopy"]
    if (
        green["dimension_ledger"]["identity"] != "386=356+30"
        or green["dimension_ledger"]["algebraically_contracted"] != 356
        or green["dimension_ledger"]["causal_endpoint"] != 30
        or green["causal_green_homotopy"] is not True
    ):
        raise AssertionError("strict Green carrier semantics drifted")
    if loaded["strict_30_endpoint"]["dimension"] != 30:
        raise AssertionError("strict endpoint rank drifted")

    transfer = loaded["causal_transfer_theorem"]
    cylinder = transfer["consumer_replays"]["conformal_cylinder"]
    if (
        transfer["result_state"]
        != "SHARP_ABSTRACT_THEOREM_WITH_TOY_CYLINDER_AND_CURVED_CONSUMERS"
        or transfer["conclusions"]["lift"]
        != "Lambda_C,+/-=h+i Lambda_E,+/- p"
        or transfer["conclusions"]["support"]
        != "supp Lambda_C,+/- f is contained in J^+/-(supp f)"
        or cylinder["cyclic_SDR"] is not True
        or cylinder["same_sided_support"] is not True
    ):
        raise AssertionError("causal transfer theorem semantics drifted")


def _verify_action(value: dict[str, Any]) -> None:
    action = value["background_and_action"]
    couplings = action["couplings"]
    R0 = _fraction(action["unit_cylinder"]["scalar_curvature"])
    M2 = _fraction(couplings["M_P_squared"])
    alpha = _fraction(couplings["alpha_R"])
    V0 = _fraction(couplings["V0"])

    if (
        R0 != 6
        or M2 != Fraction(1, 6)
        or alpha != Fraction(-1, 144)
        or V0 != Fraction(1, 4)
        or _fraction(couplings["kappa_r"]) != -1
        or _fraction(couplings["kappa_theta"]) != 1
        or _fraction(couplings["f"]) != 1
        or _fraction(couplings["lambda"]) != 1
    ):
        raise AssertionError("changed-action rational fixture drifted")

    F = M2 * R0 / 2 + alpha * R0**2 - V0
    F_prime = M2 / 2 + 2 * alpha * R0
    F_second = 2 * alpha
    if (
        F != 0
        or F_prime != 0
        or F_second != Fraction(-1, 72)
        or _fraction(action["background_equations"]["F_R0"]) != F
        or _fraction(action["background_equations"]["F_prime_R0"])
        != F_prime
        or _fraction(action["background_equations"]["F_second_R0"])
        != F_second
    ):
        raise AssertionError("cylinder double-root equations failed")

    # delta R=-3 P2 u and (1/2)F''(delta R)^2 give
    # (1/2) u H_u u with H_u=9 F'' P2^2.
    trace_hessian = 9 * F_second
    if (
        trace_hessian != Fraction(-1, 8)
        or _fraction(
            action["quadratic_variation"]["trace_Hessian_coefficient"]
        )
        != trace_hessian
        or action["quadratic_variation"]["strict_complement_change"]
        != "ZERO because F(R0)=F'(R0)=0"
    ):
        raise AssertionError("trace Hessian reconstruction failed")

    solution = action["uniqueness_in_declared_action"]
    if (
        solution["symbolic_conditions"] != ["F(R0)=0", "F'(R0)=0"]
        or solution["symbolic_solution"]
        != ["alpha_R=-M_P^2/(4 R0)", "V0=M_P^2 R0/4"]
        or solution["conformal_rho2_R_alone_suffices"]
    ):
        raise AssertionError("declared-action uniqueness ledger drifted")


def _verify_endpoint(value: dict[str, Any]) -> None:
    endpoint = value["scalar_phase_endpoint"]
    if endpoint["basis"] != [
        "sigma",
        "u=phi_trace-2tau",
        "v=phi_trace",
        "theta",
        "u_star",
        "v_star",
        "theta_star",
        "sigma_star",
    ] or endpoint["degrees"] != [-1, 0, 0, 0, 1, 1, 1, 2]:
        raise AssertionError("scalar/phase basis drifted")

    H_u, H_theta = sp.symbols("H_u H_theta", nonzero=True)
    Gu_p, Gu_m, Gt_p, Gt_m = sp.symbols(
        "Gu_p Gu_m Gt_p Gt_m", nonzero=True
    )
    symbols = {
        "1": sp.Integer(1),
        "-1": sp.Integer(-1),
        "H_u": H_u,
        "H_theta": H_theta,
        "G_u_plus": Gu_p,
        "G_u_minus": Gu_m,
        "G_theta_plus": Gt_p,
        "G_theta_minus": Gt_m,
    }
    q = _operator(endpoint["Q_changed"], symbols)
    expected_q = sp.zeros(8)
    expected_q[2, 0] = 1
    expected_q[4, 1] = H_u
    expected_q[6, 3] = H_theta
    expected_q[7, 5] = -1
    if q != expected_q or q * q != sp.zeros(8):
        raise AssertionError("endpoint differential failed")

    pairing = _pairing(endpoint["odd_pairing"])
    if pairing.det() != 1 or q.T * pairing + pairing * q != sp.zeros(8):
        raise AssertionError("endpoint odd cyclic pairing failed")

    substitutions = {
        Gu_p * H_u: 1,
        Gu_m * H_u: 1,
        Gt_p * H_theta: 1,
        Gt_m * H_theta: 1,
    }
    for name in ("Lambda_plus", "Lambda_minus"):
        homotopy = _operator(endpoint[name], symbols)
        defect = (q * homotopy + homotopy * q).applyfunc(
            lambda item: sp.expand(item).subs(substitutions)
        )
        if defect != sp.eye(8):
            raise AssertionError(f"{name} chain contraction failed")

    for name in (
        "Q_changed",
        "Lambda_plus",
        "Lambda_minus",
        "odd_pairing",
    ):
        _check_matrix_hash(endpoint[name])

    dictionary = endpoint["operator_dictionary"]
    if dictionary != {
        "H_u": "-(1/8) P_2^2",
        "P_2": "Box+2",
        "G_u_plus": "-8 G_2_plus G_2_plus",
        "G_u_minus": "-8 G_2_minus G_2_minus",
        "H_theta": "P_0=Box",
        "G_theta_plus": "G_0_plus",
        "G_theta_minus": "G_0_minus",
    }:
        raise AssertionError("Green operator dictionary drifted")

    # Independent scalar multiplication: (-P2^2/8)(-8 G2^2)=1
    # in either ordering when P2 G2=G2 P2=1.
    P2, G2 = sp.symbols("P2 G2", nonzero=True)
    inverse_product = sp.expand(
        (-P2**2 / 8) * (-8 * G2**2)
    ).subs(P2 * G2, 1)
    if inverse_product != 1:
        raise AssertionError("iterated Green inverse normalization failed")
    if (
        endpoint["support"]["iterated_biwave"]
        != "supp(G_2_pm G_2_pm f) subset "
        "J_pm(J_pm(supp f))=J_pm(supp f)"
    ):
        raise AssertionError("iterated causal-support statement drifted")


def _verify_carrier_and_boundary(value: dict[str, Any]) -> None:
    carrier = value["complete_carrier"]
    if (
        carrier["full_rank"] != 390
        or carrier["strict_rows_imported"] != 386
        or carrier["algebraically_contracted_rank"] != 356
        or carrier["causal_endpoint_rank"] != 34
        or carrier["identity"] != "390=356+34"
        or carrier["endpoint_degree_ranks"] != [5, 12, 12, 5]
        or sum(carrier["endpoint_degree_ranks"]) != 34
        or carrier["minimal_rank"] != 70
    ):
        raise AssertionError("complete carrier ledger failed")
    if [row["symbol"] for row in carrier["new_rows"]] != [
        "tau",
        "tau_hat_star",
        "theta",
        "theta_star",
    ]:
        raise AssertionError("new field rows drifted")

    lift = value["full_Green_homotopy"]
    if (
        lift["strict_complement_rank"] != 26
        or lift["new_scalar_phase_rank"] != 8
        or lift["endpoint_identity"] != "34=26+8"
        or lift["side_conditions"]
        != [
            "p_34 i_34=1",
            "S_356 i_34=0",
            "p_34 S_356=0",
            "S_356^2=0",
        ]
        or "no infinite Neumann correction is required"
        not in lift["HPL_reason"]
    ):
        raise AssertionError("full Green lift ledger failed")

    old = value["old_obstruction_disposition"]
    if (
        old["status"] != "KILLED_BY_NONZERO_CLASSICAL_TRACE_HESSIAN"
        or old["not_a_zero_mode_removal"] is not True
        or old["old_Stokes_functional_is_now_a_cocycle_dual"] is not False
        or "(Box+2)^2 f=0 vanishes" not in old["compact_support_kernel"]
    ):
        raise AssertionError("old obstruction was not correctly disposed")

    flags = value["claim_flags"]
    required = {
        "CHANGED_CLASSICAL_ACTION",
        "COMPLETE_390_ROW_CAUSAL_BV_PARENT",
        "RADIAL_QUARTET_CONTRACTED",
        "DRESSED_TRACE_CAUSALLY_PAIRED",
        "PHASE_CAUSAL_WAVE_BLOCK",
    }
    forbidden = {
        "RAW_D_CARTAN",
        "BERGER_SPECIALIZATION",
        "HADAMARD_STATE",
        "QME",
        "POSITIVITY",
        "PARTICLE_SCATTERING_UNITARITY",
    }
    if not all(flags[name] for name in required):
        raise AssertionError("a certified classical flag was demoted")
    if any(flags[name] for name in forbidden):
        raise AssertionError("an open claim was promoted")
    if value["action_identity"]["Wess_Zumino_in_classical_action"]:
        raise AssertionError("an hbar Wess-Zumino term entered classical data")
    boundary = value["claim_boundary"]
    for phrase in (
        "one exact changed-action unit-cylinder fixture",
        "not strict pure Weyl gravity",
        "not claimed stable or positive",
        "Hadamard/Feynman states",
        "remain unproved",
    ):
        if phrase not in boundary:
            raise AssertionError(f"claim boundary lost: {phrase}")


def _verify_hashes(value: dict[str, Any]) -> None:
    core = {
        "action_identity": value["action_identity"],
        "background_and_action": value["background_and_action"],
        "complete_carrier": value["complete_carrier"],
        "linearized_BV_operator": value["linearized_BV_operator"],
        "scalar_phase_endpoint": value["scalar_phase_endpoint"],
        "full_Green_homotopy": value["full_Green_homotopy"],
        "old_obstruction_disposition": value[
            "old_obstruction_disposition"
        ],
    }
    expected = {
        "action_specialization_sha256": _digest(
            value["background_and_action"]
        ),
        "scalar_endpoint_sha256": _digest(value["scalar_phase_endpoint"]),
        "carrier_manifest_sha256": _digest(value["complete_carrier"]),
        "causal_parent_core_sha256": _digest(core),
    }
    if value["content_hashes"] != expected:
        raise AssertionError("certificate content hashes failed")


def verify(value: dict[str, Any] | None = None) -> None:
    if value is None:
        value = json.loads(CERTIFICATE.read_text())
    if (
        value["schema"]
        != "pure-weyl-complex-compensator-vacuum-cylinder-causal-parent-v1"
        or value["result_id"]
        != "COMPLEX_COMPENSATOR_VACUUM_CYLINDER_CAUSAL_PARENT_V1"
        or value["result_state"]
        != "CHANGED_ACTION_CAUSAL_BV_PARENT_CERTIFIED"
        or value["dependency_tags"]
        != ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"]
    ):
        raise AssertionError("top-level result identity drifted")
    try:
        Draft202012Validator(
            json.loads(SCHEMA.read_text())
        ).validate(value)
    except ValidationError as exc:
        raise AssertionError(
            f"strict schema validation failed: {exc.message}"
        ) from exc
    _verify_dependencies(value)
    _verify_action(value)
    _verify_endpoint(value)
    _verify_carrier_and_boundary(value)
    _verify_hashes(value)
    if set(value["exact_checks"].values()) != {True}:
        raise AssertionError("an exact check is not true")


def main() -> None:
    verify()
    value = json.loads(CERTIFICATE.read_text())
    print(
        "complex compensator vacuum-cylinder causal parent independent "
        f"verification: PASS ({value['content_hashes']['causal_parent_core_sha256']})"
    )


if __name__ == "__main__":
    main()
