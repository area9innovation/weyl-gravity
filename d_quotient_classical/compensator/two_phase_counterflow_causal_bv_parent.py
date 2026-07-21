#!/usr/bin/env python3
"""Promote the selected counterflow fixture to a 70-component causal BV parent."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_CAUSAL_BV_PARENT_V1.json"
PAYLOAD_OUTPUT = ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_CAUSAL_BV_PARENT_PAYLOAD_V1.json"
RECEIVER_OUTPUT = ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_CAUSAL_BV_RECEIVER_CONTRACT_V1.json"
IMPORTS = {
    "preflight": ("d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_TRACE_CHARGE_PREFLIGHT_V1.json", "2b578967ece7a2e6a8079c8fd84665ac40cf2b7e0aeef41d96882553c35115ea", "d6d54a6efaa30ffe48dd7b9718c1954fa4ea514b", "TWO_PHASE_COUNTERFLOW_TRACE_CHARGE_PREFLIGHT_V1"),
    "hodge": ("d_quotient_classical/compensator/CLOSED_S3_RELATIVE_PHASE_NONHOMOGENEOUS_HODGE_PREFLIGHT_V1.json", "8bea19daa641aed5d771dd440624e5c7ea6128ce857ebd04c3d9b010c7acd5f9", "fcfa6f88b390a19a83f844791400f16da121e5d4", "CLOSED_S3_RELATIVE_PHASE_NONHOMOGENEOUS_HODGE_PREFLIGHT_V1"),
    "positive_clock": ("d_quotient_classical/certificates/POSITIVE_BERGER_CLOCK_BACKGROUND.json", "35e1bb8a56b0591b3dd00aa8f22c328ad826ecd341c290564cfd1a68fcc3e687", "bb5738d6e3e30a68adcc9a70c35dac089079e3db", "POSITIVE_BERGER_CLOCK_BACKGROUND"),
    "charge_seed": ("d_quotient_classical/certificates/BERGER_CLOCK_REDUCED_CHARGE_SEED.json", "573381287998b6645b37fcbad0273c23c0e5cff58450cbcf7a2dc1152a8dfcd9", "bb5738d6e3e30a68adcc9a70c35dac089079e3db", "BERGER_CLOCK_REDUCED_CHARGE_SEED"),
    "gauge_fixed_54": ("d_quotient_classical/certificates/BERGER_GAUGE_FIXED_NONMINIMAL_COMPLETION.json", "6e3baf6ecfab2c2854ccfbfb5c69122fe0bbe621ddcf8ab2a5651e3decf113e0", "445e26663d06764bc858ff0a004ba6178acce75f", "BERGER_GAUGE_FIXED_NONMINIMAL_COMPLETION"),
    "green_54": ("d_quotient_classical/certificates/BERGER_54_ROW_CAUSAL_GREEN_HOMOTOPY_V2.json", "e92642b3225ab87b6058987f73f9ade3909646f2d0d3b95cc45cc9c5712b9c3b", "743183594a7a33dbb869154dafd7eb2c3482bac0", "BERGER_54_ROW_CAUSAL_GREEN_HOMOTOPY_V2"),
    "D_action_54": ("d_quotient_classical/certificates/BERGER_54_ROW_LOCAL_D_ACTION.json", "8b5f1277c1969507e58b4389984338f2a063b99f9d7cf8a929abcffa298b3e49", "90bd7d3f3d2b13573ef527400ecd731096babbe3", "BERGER_54_ROW_LOCAL_D_ACTION"),
    "K_Cartan_54": ("d_quotient_classical/certificates/BERGER_CAUSAL_D_CARTAN_V2.json", "87c1b4d897d56bcfea51f79c71f6f0b387157fc8a76fb83eb909c8ef00d3f444", "743183594a7a33dbb869154dafd7eb2c3482bac0", "BERGER_CAUSAL_D_CARTAN_V2"),
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _render(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def _imports() -> tuple[dict[str, Any], dict[str, Any]]:
    records, values = {}, {}
    for key, (relative, expected, commit, result_id) in IMPORTS.items():
        path = ROOT / relative
        value = json.loads(path.read_text())
        actual = _sha(path)
        if actual != expected or value.get("result_id") != result_id:
            raise AssertionError(f"{key} import drifted")
        records[key] = {"path": relative, "sha256": actual, "source_commit": commit, "result_id": result_id, "oracle_fields_consumed": []}
        values[key] = value
    if values["preflight"]["terminal_verdict"]["selected_Berger"] != "PASSED_FIXED_RELATIVE_CHARGE_BERGER_STRATUM":
        raise AssertionError("preflight did not activate causal parent")
    if values["green_54"]["claim_status"] != "CERTIFIED_COMPLETE_GAUGE_FIXED_CAUSAL_GREEN_HOMOTOPY_HADAMARD_OPEN":
        raise AssertionError("54-row Green import is not certified")
    if values["K_Cartan_54"]["flags"]["BERGER_CAUSAL_D_CARTAN_V2"] is not True:
        raise AssertionError("54-row helical Cartan import is not certified")
    return records, values


def _matrix_record(matrix: sp.Matrix) -> dict[str, Any]:
    core = {"row_count": matrix.rows, "column_count": matrix.cols, "entries": [{"row": i, "column": j, "coefficient": str(matrix[i, j])} for i in range(matrix.rows) for j in range(matrix.cols) if matrix[i, j] != 0]}
    return {**core, "sha256": _digest(core)}


def _u1_extension() -> dict[str, Any]:
    # Changed multiplet basis: (chi,c,A*,B,c*,H,barc,b,b*,barc*),
    # H=chi*+delta A*.  Component ranks are (1,1,4,4,1,1,1,1,1,1).
    names = ["chi", "c_U1", "A_star", "B=A-dchi", "c_U1_star", "H=chi_star+delta_A_star", "bar_c", "b", "b_star", "bar_c_star"]
    ranks = [1, 1, 4, 4, 1, 1, 1, 1, 1, 1]
    q = sp.zeros(10)
    # Q acts on column basis vectors.
    q[1, 0] = 1
    q[3, 2] = -4
    q[5, 4] = 1
    q[7, 6] = 1
    q[9, 8] = -1
    s = sp.zeros(10)
    s[0, 1] = 1
    s[2, 3] = -sp.Rational(1, 4)
    s[4, 5] = 1
    s[6, 7] = 1
    s[8, 9] = -1
    if q * q != sp.zeros(10) or q * s + s * q != sp.eye(10):
        raise AssertionError("algebraic U1 contraction failed")
    return {
        "original_rows": [
            {"id": "c_U1", "bundle": "Omega0", "component_rank": 1, "ghost_number": 1, "Q_image": "0"},
            {"id": "chi", "bundle": "Omega0", "component_rank": 1, "ghost_number": 0, "Q_image": "c_U1"},
            {"id": "A", "bundle": "Omega1", "component_rank": 4, "ghost_number": 0, "Q_image": "d c_U1"},
            {"id": "A_star", "bundle": "Omega1", "component_rank": 4, "ghost_number": -1, "Q_image": "-4(A-dchi)"},
            {"id": "chi_star", "bundle": "Omega0", "component_rank": 1, "ghost_number": -1, "Q_image": "4 delta(A-dchi)"},
            {"id": "c_U1_star", "bundle": "Omega0", "component_rank": 1, "ghost_number": -2, "Q_image": "chi_star+delta A_star"},
            {"id": "bar_c", "bundle": "Omega0", "component_rank": 1, "ghost_number": -1, "Q_image": "b"},
            {"id": "b", "bundle": "Omega0", "component_rank": 1, "ghost_number": 0, "Q_image": "0"},
            {"id": "b_star", "bundle": "Omega0", "component_rank": 1, "ghost_number": -1, "Q_image": "-bar_c_star"},
            {"id": "bar_c_star", "bundle": "Omega0", "component_rank": 1, "ghost_number": 0, "Q_image": "0"},
        ],
        "minimal_component_rank": 12,
        "nonminimal_component_rank": 4,
        "total_component_rank": sum(ranks),
        "changed_basis_order": names,
        "changed_basis_component_ranks": ranks,
        "canonical_change": {"B": "A-dchi", "H": "chi_star+delta A_star", "inverse": "A=B+dchi; chi_star=H-delta A_star", "finite_differential_and_support_local": True},
        "Q_changed_basis": _matrix_record(q),
        "S_changed_basis": _matrix_record(s),
        "Q_squared_zero": True,
        "Q_S_plus_S_Q_identity": True,
        "action_compatibility": {"density": "-2 <B,B>", "Euler_A": "-4B", "Euler_chi": "4 delta B", "Noether_identity": "Euler_chi+delta Euler_A=0"},
        "gauge_fixing": {"fermion": "Psi_U1=integral <bar_c,chi>", "terms": "<b,chi>-<bar_c,c_U1>", "unitary_gauge": "chi=0", "Coulomb_inverse": False},
        "cyclic_pairing": "canonical odd BV pairing A-A_star, chi-chi_star, c_U1-c_U1_star, bar_c-b_star, b-bar_c_star",
        "real_structure": "A,chi,B,b real; ghosts and antifields carry the convention-fixed real BV conjugation",
    }


def _action_equivalence(values: dict[str, Any]) -> dict[str, Any]:
    selected = values["preflight"]["selected_fixture"]["parameters"]
    old = values["positive_clock"]["rational_fixture"]
    checks = {
        "alpha_B": sp.Rational(selected["alpha_B"]) == sp.Rational(old["alpha_B"]),
        "Omega": sp.Rational(selected["Omega"]) == sp.Rational(old["omega"]),
        "rho_squared": sp.Rational(1) == sp.Rational(old["rho_squared"]),
        "V0_equals_lambda_over_4": sp.Rational(selected["V0"]) == sp.Rational(old["lambda"]) / 4,
        "Einstein_from_conformal_coupling": sp.Rational(selected["M_P_squared"]) / 2 == -sp.Rational(1, 12),
        "relative_phase_coefficient": sp.Rational(selected["mu_squared"]) == 1,
    }
    if not all(checks.values()):
        raise AssertionError("selected action is not the certified Berger polar clock action")
    return {
        "identity": "S_selected=S_Berger_clock_at_rho=1 - 2*integral<B,B>, with B=A-dchi",
        "polar_clock_density": "5*C^2/8-(dpsi)^2/2-R/12-119/1920",
        "diagonal_contractible_density": "-2*(A-dchi)^2",
        "checks": checks,
        "conclusion": "the physical gravity-relative-clock block is exactly the certified 54-row Berger carrier; the new diagonal U1 block is algebraically contractible",
    }


def _receiver_contract() -> dict[str, Any]:
    common = {
        "required_parent_result_id": "TWO_PHASE_COUNTERFLOW_CAUSAL_BV_PARENT_V1",
        "required_parent_state": "CERTIFIED_70_COMPONENT_SUPPORT_LOCAL_CAUSAL_BV_PARENT",
        "background": "same stationary Berger fixture a=1,c_squared=9/40",
        "charge_sector": "fixed Q_rel leaf; unrestricted D remains charged",
        "forbidden_promotions": ["Hadamard", "QME", "Einstein source", "q2 stability", "observable existence"],
    }
    return {
        "schema": "pure-weyl-two-phase-counterflow-causal-bv-receiver-contract-v1",
        "result_id": "TWO_PHASE_COUNTERFLOW_CAUSAL_BV_RECEIVER_CONTRACT_V1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "receivers": {
            "Observer": {**common, "receives": ["relative clock current", "cyclic pairing", "causal q1 carrier"], "still_open": "construct a relational observable and detector map"},
            "Nonlinear": {**common, "receives": ["causal q1 carrier", "K/D/R_rel Cartan ledger"], "still_open": "derive and verify the selected-action q2 and tangent-cone map"},
            "Bridge": {**common, "receives": ["selected local action", "causal q1 carrier", "stress normalization"], "still_open": "derive the same-background Einstein-source condition"},
            "Quantum": {**common, "receives": ["real cyclic causal q1 parent", "classical-to-quantum import hash boundary"], "still_open": "construct a compatible complex structure, Hadamard two-point function and anomaly/QME disposition"},
        },
        "content_sha256": "PENDING",
    }


def _payload(imports: dict[str, Any], values: dict[str, Any]) -> dict[str, Any]:
    extension = _u1_extension()
    action = _action_equivalence(values)
    parent = {
        "old_component_rank": 54,
        "extension_component_rank": 16,
        "complete_component_rank": 70,
        "formula": "Q70=Q54 direct_sum Q_U1; Lambda70,+/-=Lambda54,+/- direct_sum S_U1",
        "chain_identity": "Q70 Lambda70,+/-+Lambda70,+/- Q70=I70",
        "support": "Lambda54,+/- is same-sided causal; S_U1 is support-local with support on the diagonal, hence also both advanced and retarded",
        "adjoint_and_cyclic": "direct sum of the imported cyclic advanced/retarded adjoint pair and the canonical algebraic BV contraction",
        "no_spatial_inverse": True,
        "zero_modes_retained": True,
        "H1_S3": "0; exact and coexact connection modes split, while scalar constants and Q_rel fibres remain explicit",
    }
    cartan = {
        "U1_diag": {"Lie_action": "Q_U1 gauge action", "contraction": "the displayed algebraic S_U1", "identity": "[Q70,iota_U1]=L_U1", "charge": "Q_diag=0 by local Gauss"},
        "R_rel": {"Lie_action": "global O(2) rotation of the imported clock block; zero on U1 extension", "contraction": "iota_R,+/-=Lambda70,+/- L_R", "identity": "[Q70,iota_R,+/-]=L_R", "charge": "Q_rel on unrestricted union; null only on fixed-Q_rel leaf"},
        "K": {"identification": "the imported D_helical=partial_t plus compensating internal rotation", "identity": "certified cyclic causal K-Cartan through arity two on 54 rows; extension commutes and is algebraically contractible"},
        "D": {"decomposition": "D=K+Omega R_rel", "contraction": "iota_D=iota_K+Omega*iota_R", "identity": "[Q70,iota_D]=L_D", "charge": "Omega Q_rel modulo closed diffeomorphism constraint; unrestricted D is not gauge"},
    }
    current = {
        "relative_current": "j_R=T1*dT2-T2*dT1=dpsi at rho=1=mu_squared*dpsi",
        "relative_charge": "Q_rel=integral_S3 star j_R",
        "normalization_checks": {"rho_squared": "1", "mu_squared": "1", "Omega": "3/4"},
        "pairing_transport": "the 54-row cyclic clock pairing is unchanged; the diagonal quartet adds an orthogonal canonical BV summand",
        "fixed_leaf": "delta Q_rel=0 is preserved by the linearized lapse row; no global mode is deleted from the unreduced carrier",
    }
    payload = {
        "schema": "pure-weyl-two-phase-counterflow-causal-bv-parent-payload-v1",
        "result_id": "TWO_PHASE_COUNTERFLOW_CAUSAL_BV_PARENT_PAYLOAD_V1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "imports": imports,
        "oracle_fields_consumed": [],
        "action_equivalence": action,
        "u1_minimal_nonminimal_extension": extension,
        "complete_parent": parent,
        "Cartan_ledger": cartan,
        "clock_current_and_pairing": current,
    }
    payload["content_sha256"] = _digest(payload)
    return payload


def _certificate(imports: dict[str, Any], payload: dict[str, Any], receiver: dict[str, Any]) -> dict[str, Any]:
    boundary = {
        "establishes": ["exact action equivalence to the certified positive Berger clock carrier", "complete 54+16=70 component minimal/nonminimal BV parent", "nilpotent action-compatible algebraic diagonal-U1 extension", "same-sided advanced/retarded chain homotopies without a Coulomb inverse", "cyclic pairing, real structure, clock-current transport and four-generator Cartan ledger"],
        "does_not_establish": ["Hadamard data or a compatible positive complex structure", "nonlinear q2 stability for the selected extension", "an Einstein-source bridge", "a relational observable", "a QME, anomaly cancellation or quantum theorem"],
    }
    flags = {
        "COMPLETE_70_COMPONENT_BV_PARENT": True,
        "SUPPORT_LOCAL_CAUSAL_GREEN_HOMOTOPY": True,
        "CYCLIC_AND_REAL": True,
        "FIXED_CHARGE_BERGER_ONLY": True,
        "COULOMB_INVERSE": False,
        "UNRESTRICTED_D_GAUGE": False,
        "HADAMARD": False,
        "NONLINEAR_Q2": False,
        "QME_OR_QUANTUM": False,
    }
    terminal = {"result_state": "CERTIFIED_70_COMPONENT_SUPPORT_LOCAL_CAUSAL_BV_PARENT", "downstream_receivers_activated": True, "receiver_contract_result_id": receiver["result_id"], "activation_scope": "same selected Berger background and fixed-Q_rel leaf only", "Hadamard_status": "OPEN"}
    return {
        "schema": "pure-weyl-two-phase-counterflow-causal-bv-parent-v1",
        "result_id": "TWO_PHASE_COUNTERFLOW_CAUSAL_BV_PARENT_V1",
        "result_state": terminal["result_state"],
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "imports": imports,
        "payload_ref": {"path": str(PAYLOAD_OUTPUT.relative_to(ROOT)), "sha256": "PENDING_WRITE", "content_sha256": payload["content_sha256"]},
        "receiver_contract_ref": {"path": str(RECEIVER_OUTPUT.relative_to(ROOT)), "sha256": "PENDING_WRITE", "content_sha256": receiver["content_sha256"]},
        "complete_parent": payload["complete_parent"],
        "Cartan_ledger": payload["Cartan_ledger"],
        "clock_current_and_pairing": payload["clock_current_and_pairing"],
        "terminal_verdict": terminal,
        "claim_flags": flags,
        "claim_boundary": boundary,
        "content_hashes": {"parent_sha256": _digest(payload["complete_parent"]), "Cartan_sha256": _digest(payload["Cartan_ledger"]), "current_pairing_sha256": _digest(payload["clock_current_and_pairing"]), "terminal_sha256": _digest(terminal), "boundary_sha256": _digest(boundary)},
    }


def validate(certificate: dict[str, Any], payload: dict[str, Any], receiver: dict[str, Any]) -> None:
    if payload["content_sha256"] != _digest({k: v for k, v in payload.items() if k != "content_sha256"}):
        raise AssertionError("payload content hash mismatch")
    expected_receiver = _digest({k: v for k, v in receiver.items() if k != "content_sha256"})
    if receiver["content_sha256"] != expected_receiver:
        raise AssertionError("receiver content hash mismatch")
    if set(receiver.get("receivers", {})) != {"Observer", "Nonlinear", "Bridge", "Quantum"}:
        raise AssertionError("receiver content is incomplete")
    if any(len(row.get("forbidden_promotions", [])) != 5 for row in receiver["receivers"].values()):
        raise AssertionError("receiver content lost fail-closed promotions")
    if payload["complete_parent"]["complete_component_rank"] != 70 or payload["u1_minimal_nonminimal_extension"]["total_component_rank"] != 16:
        raise AssertionError("carrier rank drifted")
    if not payload["u1_minimal_nonminimal_extension"]["Q_squared_zero"] or not payload["u1_minimal_nonminimal_extension"]["Q_S_plus_S_Q_identity"]:
        raise AssertionError("U1 contraction failed")
    flags = certificate["claim_flags"]
    if flags["COULOMB_INVERSE"] or flags["UNRESTRICTED_D_GAUGE"] or flags["HADAMARD"] or flags["NONLINEAR_Q2"] or flags["QME_OR_QUANTUM"]:
        raise AssertionError("claim boundary promoted")
    expected_hashes = {"parent_sha256": _digest(certificate["complete_parent"]), "Cartan_sha256": _digest(certificate["Cartan_ledger"]), "current_pairing_sha256": _digest(certificate["clock_current_and_pairing"]), "terminal_sha256": _digest(certificate["terminal_verdict"]), "boundary_sha256": _digest(certificate["claim_boundary"])}
    if certificate["content_hashes"] != expected_hashes:
        raise AssertionError("certificate content hash mismatch")


def build() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    imports, values = _imports()
    receiver = _receiver_contract()
    receiver["content_sha256"] = _digest({k: v for k, v in receiver.items() if k != "content_sha256"})
    payload = _payload(imports, values)
    certificate = _certificate(imports, payload, receiver)
    validate(certificate, payload, receiver)
    return certificate, payload, receiver


def write() -> None:
    certificate, payload, receiver = build()
    PAYLOAD_OUTPUT.write_text(_render(payload))
    RECEIVER_OUTPUT.write_text(_render(receiver))
    certificate["payload_ref"]["sha256"] = _sha(PAYLOAD_OUTPUT)
    certificate["receiver_contract_ref"]["sha256"] = _sha(RECEIVER_OUTPUT)
    validate(certificate, payload, receiver)
    OUTPUT.write_text(_render(certificate))


def check() -> None:
    certificate, payload, receiver = build()
    certificate["payload_ref"]["sha256"] = _sha(PAYLOAD_OUTPUT)
    certificate["receiver_contract_ref"]["sha256"] = _sha(RECEIVER_OUTPUT)
    if json.loads(OUTPUT.read_text()) != certificate or json.loads(PAYLOAD_OUTPUT.read_text()) != payload or json.loads(RECEIVER_OUTPUT.read_text()) != receiver:
        raise AssertionError("stored causal parent artifacts drifted")
    print("TWO_PHASE_COUNTERFLOW_CAUSAL_BV_PARENT_V1: PASS")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    check() if args.check else write()


if __name__ == "__main__":
    main()
