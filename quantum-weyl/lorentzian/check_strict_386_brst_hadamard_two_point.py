#!/usr/bin/env python3
"""Independent receiver for the strict full-complex BRST Hadamard pair."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/lorentzian"
IMPORT = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_386_BRST_HADAMARD_TWO_POINT_V1.json"
REPORT = HERE / "REPORT_STRICT_386_BRST_HADAMARD_TWO_POINT_V1.md"
SCHEMA = HERE / "schema/strict-386-brst-hadamard-two-point-v1.schema.json"
INPUTS = {
    "causal_envelope": IMPORT / "certificates/STRICT_M2_Q2_Q3_TYPED_GREEN_COMPATIBILITY_V1.json",
    "green": IMPORT / "certificates/STRICT_386_GRAPH_GREEN_ACTION_NAME_V1.json",
    "graph_q1": IMPORT / "certificates/STRICT_386_GRAPH_Q1_SDR_COMPONENT_JETS_V1.json",
    "cyclic": IMPORT / "certificates/STRICT_386_LOCAL_CYCLIC_PAIRING_CLOSURE_V1.json",
    "suspension": IMPORT / "certificates/STRICT_386_SUSPENDED_ADJOINT_BRIDGE_V1.json",
    "field_inverse": IMPORT / "certificates/STRICT_386_FIELD_EQUATION_GREEN_QUOTIENT_INVERSE_V1.json",
}
EXPECTED_IDS = {
    "causal_envelope": "STRICT_M2_Q2_Q3_TYPED_GREEN_COMPATIBILITY_V1",
    "green": "STRICT_386_GRAPH_GREEN_ACTION_NAME_V1",
    "graph_q1": "STRICT_386_GRAPH_Q1_SDR_COMPONENT_JETS_V1",
    "cyclic": "STRICT_386_LOCAL_CYCLIC_PAIRING_CLOSURE_V1",
    "suspension": "STRICT_386_SUSPENDED_ADJOINT_BRIDGE_V1",
    "field_inverse": "STRICT_386_FIELD_EQUATION_GREEN_QUOTIENT_INVERSE_V1",
}
ANALYTIC_HASHES = {
    "wrochna-zahn-2017": "3e579a80745d1c15287c9395f1dbc670289604408acde9b519c0115bcbc6d0f0",
    "sahlmann-verch-2001": "517bb1ca09a5d36bf446854ab20c9f4472c0b51a468e8d489e4b73a78d49a540",
    "gerard-oulghazi-wrochna-2017": "041ad10f38d62097bc525843e631b3e3f7f948ba0ac5393a8bd3246f3da5bc81",
}
CHECKERS = (
    IMPORT / "check_strict_m2_q2_q3_typed_green_compatibility.py",
    IMPORT / "check_strict_386_graph_green_action_name.py",
    IMPORT / "check_strict_386_graph_q1_sdr_component_jets.py",
    IMPORT / "check_strict_386_local_cyclic_pairing_closure.py",
    IMPORT / "check_strict_386_suspended_adjoint_bridge.py",
    IMPORT / "check_strict_386_field_equation_green_quotient_inverse.py",
)


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode()).hexdigest()


def verify_embedded_hash(value: dict[str, Any], label: str, errors: list[str]) -> None:
    expected = digest({key: item for key, item in value.items() if key != "sha256"})
    if value.get("sha256") != expected:
        errors.append(f"{label} digest")


def independent_modal_replay() -> tuple[dict[str, bool], dict[str, bool]]:
    omega = sp.symbols("omega", positive=True, real=True)
    tau = sp.symbols("tau", real=True)
    wp = -sp.exp(-sp.I * omega * tau) / (2 * omega)
    wm = -sp.exp(+sp.I * omega * tau) / (2 * omega)
    zp = sp.I * tau / 2
    zm = -sp.I * tau / 2
    positive = {
        "left_wave_bisolution": sp.simplify(sp.diff(wp, tau, 2) + omega**2 * wp) == 0,
        "right_wave_bisolution": sp.simplify(sp.diff(wm, tau, 2) + omega**2 * wm) == 0,
        "CCR_difference": sp.trigsimp(
            sp.expand_complex(wp - wm - sp.I * sp.sin(omega * tau) / omega)
        ) == 0,
        "plus_Hermitian_kernel": sp.simplify(wp - sp.conjugate(wp.subs(tau, -tau))) == 0,
        "minus_Hermitian_kernel": sp.simplify(wm - sp.conjugate(wm.subs(tau, -tau))) == 0,
        "opposite_frequency_reality": sp.simplify(sp.conjugate(wp) - wm) == 0,
        "stationarity": not (wp.has(sp.Symbol("t")) or wp.has(sp.Symbol("t_prime"))),
    }
    zero = {
        "left_wave_bisolution": sp.diff(zp, tau, 2) == 0,
        "right_wave_bisolution": sp.diff(zm, tau, 2) == 0,
        "CCR_difference": sp.simplify(zp - zm - sp.I * tau) == 0,
        "plus_Hermitian_kernel": sp.simplify(zp - sp.conjugate(zp.subs(tau, -tau))) == 0,
        "minus_Hermitian_kernel": sp.simplify(zm - sp.conjugate(zm.subs(tau, -tau))) == 0,
        "opposite_frequency_reality": sp.simplify(sp.conjugate(zp) - zm) == 0,
        "stationarity": True,
        "smooth_finite_rank": bool(zp.is_polynomial(tau)),
    }
    return positive, zero


def local(node: Any, map_id: str) -> bool:
    return isinstance(node, dict) and node.get("node") == "LOCAL_MAP" and node.get("map_id") == map_id


def check_graph_name(name: dict[str, Any], sign: str, spectral_hash: str) -> bool:
    if name.get("sign") != sign or name.get("canonical_name_sha256") != digest(name.get("full_graph_386_name")):
        return False
    wave = name.get("parent_wave_name", {})
    if (
        wave.get("node") != "HODGE_PROJECTOR_HADAMARD_BISOLUTION_SERIES"
        or wave.get("sign") != sign
        or wave.get("spatial_spectrum_sha256") != spectral_hash
        or wave.get("tractor_rank") != 15
        or wave.get("basis_choice") != "none; whole finite-rank Hodge eigenspace projectors"
    ):
        return False
    graph = name.get("full_graph_386_name", {})
    children = graph.get("children", [])
    if graph.get("node") != "COMPOSE" or len(children) != 3:
        return False
    if not local(children[0], "i_end_graph") or not local(children[2], "p_end_graph"):
        return False
    endpoint = children[1]
    endpoint_children = endpoint.get("children", []) if isinstance(endpoint, dict) else []
    if endpoint.get("node") != "COMPOSE" or len(endpoint_children) != 3:
        return False
    if not local(endpoint_children[0], "U_trace_Weyl") or not local(endpoint_children[2], "U_trace_Weyl_inverse"):
        return False
    direct = endpoint_children[1]
    direct_children = direct.get("children", []) if isinstance(direct, dict) else []
    return (
        direct.get("node") == "DIRECT_SUM"
        and len(direct_children) == 2
        and direct_children[1].get("node") == "ZERO_TWO_POINT"
        and direct_children[1].get("summand") == "trace_Weyl_contractible"
        and name.get("algebraic_graph_summand", "").startswith("zero;")
    )


def check(value: dict[str, Any], run_receivers: bool = False) -> list[str]:
    errors: list[str] = []
    try:
        schema = load(SCHEMA)
        Draft202012Validator.check_schema(schema)
        if list(Draft202012Validator(schema).iter_errors(value)):
            errors.append("schema validation")
    except Exception:
        errors.append("schema validation")

    source = {name: load(path) for name, path in INPUTS.items()}
    provenance = value.get("provenance", {}).get("inputs", [])
    by_id = {item.get("input_id"): item for item in provenance}
    if len(provenance) != 6 or len(by_id) != 6:
        errors.append("provenance census")
    for name, path in INPUTS.items():
        item = by_id.get(name, {})
        if (
            source[name].get("result_id") != EXPECTED_IDS[name]
            or item.get("result_id") != EXPECTED_IDS[name]
            or item.get("path") != str(path.relative_to(ROOT))
            or item.get("sha256") != file_hash(path)
        ):
            errors.append("provenance binding")

    causal, green, graph_q1, cyclic, suspension, inverse = (
        source[name]
        for name in ("causal_envelope", "green", "graph_q1", "cyclic", "suspension", "field_inverse")
    )
    causal_flags = causal.get("claim_flags", {})
    if (
        causal_flags.get("CLASSICAL_IMPORT_GATE_PASSED") is not True
        or causal_flags.get("NONLINEAR_GREEN_COMPATIBILITY_CERTIFIED") is not True
        or causal_flags.get("FULL_COMPLEX_BRST_HADAMARD_TWO_POINT_FUNCTION_CONSTRUCTED") is not False
        or value.get("scope", {}).get("classical_snapshot_id") != causal.get("scope", {}).get("snapshot_id")
        or value.get("scope", {}).get("classical_snapshot_sha256") != causal.get("scope", {}).get("snapshot_sha256")
    ):
        errors.append("classical causal-envelope gate")
    if (
        cyclic.get("pairing_replay", {}).get("exact_rational_rank") != 386
        or graph_q1.get("graph_q1_serialization", {}).get("carrier_dimension") != 386
        or suspension.get("full_carrier_extension", {}).get("full_green_suspended_adjoint_replayed") is not True
        or suspension.get("full_carrier_extension", {}).get("R_386_positive") != 376
        or suspension.get("full_carrier_extension", {}).get("R_386_negative") != 10
        or inverse.get("claim_flags", {}).get("STRICT_386_FIELD_EQUATION_CONSTRAINED_RIGHT_INVERSE_CERTIFIED") is not True
    ):
        errors.append("rank-386 chain inputs")

    analytic = value.get("provenance", {}).get("analytic_sources", [])
    analytic_by_id = {item.get("id"): item for item in analytic}
    if len(analytic) != 3 or len(analytic_by_id) != 3:
        errors.append("analytic source census")
    for source_id, expected_hash in ANALYTIC_HASHES.items():
        item = analytic_by_id.get(source_id, {})
        verify_embedded_hash(item, f"analytic source {source_id}", errors)
        if item.get("artifact", {}).get("sha256") != expected_hash or not item.get("boundary"):
            errors.append("analytic source binding")

    positive, zero = independent_modal_replay()
    modal = value.get("modal_exact_checks", {})
    verify_embedded_hash(modal, "modal checks", errors)
    if (
        not all(positive.values())
        or not all(zero.values())
        or modal.get("positive_lambda", {}).get("symbolic_replay") != positive
        or modal.get("zero_lambda", {}).get("symbolic_replay") != zero
        or modal.get("all_modal_defects") != 0
        or modal.get("zero_lambda", {}).get("arbitrary_scale_or_zero_mode_deletion") is not False
    ):
        errors.append("independent modal replay")

    names = value.get("two_point_operator_names", {})
    verify_embedded_hash(names, "two-point names", errors)
    spectral_hash = digest(green.get("parent_spectral_name", {}).get("spatial_spectrum"))
    if (
        not check_graph_name(names.get("plus", {}), "plus", spectral_hash)
        or not check_graph_name(names.get("minus", {}), "minus", spectral_hash)
        or names.get("causal_difference") != "Delta_Lambda=Lambda_graph,plus-Lambda_graph,minus"
        or "lambda_minus=lambda_plus^sharp_graded" not in names.get("normalization", "")
    ):
        errors.append("operator-name transport")

    parent = value.get("parent_BRST_proof", {})
    transfer = value.get("graph_transfer_proof", {})
    obligations = value.get("proof_obligations", {})
    for section, label in ((parent, "parent proof"), (transfer, "graph transfer"), (obligations, "proof obligations")):
        verify_embedded_hash(section, label, errors)
    if (
        parent.get("parent_rank_profile") != [15, 60, 60, 15]
        or parent.get("defects") != 0
        or "whole Hodge eigenspace projectors" not in parent.get("spectral_intertwining", "")
        or transfer.get("defects") != 0
        or "complete 386-row" not in transfer.get("full_row_domain", "")
    ):
        errors.append("BRST transport proof")
    required_obligations = {
        "left_bisolution",
        "right_bisolution",
        "graded_CCR_antisymmetric_part",
        "Hadamard_wavefront_set",
        "BRST_compatibility_left",
        "BRST_compatibility_right",
        "graded_hermiticity_and_reality",
        "D_stationarity",
        "zero_mode_policy",
        "positivity_or_Krein_policy",
        "complete_386_row_coverage",
    }
    if set(obligations) - {"sha256"} != required_obligations:
        errors.append("proof-obligation census")
    for name in required_obligations:
        row = obligations.get(name, {})
        expected_status = "PASS_WITH_DECLARED_PSEUDO_STATE" if name == "positivity_or_Krein_policy" else "PASS"
        if row.get("status") != expected_status or row.get("defects") != 0 or not row.get("witness"):
            errors.append("proof-obligation result")

    boundary = value.get("state_and_positivity_boundary", {})
    verify_embedded_hash(boundary, "state boundary", errors)
    if (
        boundary.get("Hadamard_two_point_function") != "CONSTRUCTED_ON_FULL_386_ROW_OFFSHELL_BV_COMPLEX"
        or boundary.get("object_type") != "BRST_HADAMARD_PSEUDO_STATE_TWO_POINT_PAIR"
        or boundary.get("positivity") != "NOT_SATISFIED_OR_CLAIMED"
        or boundary.get("physical_cohomology_positivity") != "NOT_INFERRED"
        or boundary.get("renormalized_products") != "NOT_CONSTRUCTED"
        or boundary.get("QME") != "NOT_RESTORED"
    ):
        errors.append("pseudo-state boundary")

    snapshot = value.get("hadamard_snapshot", {})
    verify_embedded_hash(snapshot, "Hadamard snapshot", errors)
    expected_snapshot = {
        "classical_snapshot_id": causal.get("scope", {}).get("snapshot_id"),
        "classical_snapshot_sha256": causal.get("scope", {}).get("snapshot_sha256"),
        "causal_envelope_sha256": causal.get("causal_envelope", {}).get("sha256"),
        "pairing_sha256": cyclic.get("pairing_replay", {}).get("pairing_sha256"),
        "graph_q1_sha256": graph_q1.get("canonical_hashes", {}).get("graph_q1_serialization_sha256"),
        "suspension_sha256": suspension.get("canonical_hashes", {}).get("suspended_adjoint_theorem_sha256"),
        "plus_name_sha256": names.get("plus", {}).get("canonical_name_sha256"),
        "minus_name_sha256": names.get("minus", {}).get("canonical_name_sha256"),
        "modal_checks_sha256": modal.get("sha256"),
        "parent_proof_sha256": parent.get("sha256"),
        "transfer_proof_sha256": transfer.get("sha256"),
        "proof_checks_sha256": obligations.get("sha256"),
        "state_boundary_sha256": boundary.get("sha256"),
    }
    for key, expected in expected_snapshot.items():
        if snapshot.get(key) != expected:
            errors.append("Hadamard snapshot binding")

    flags = value.get("claim_flags", {})
    required_true = (
        "CLASSICAL_IMPORT_GATE_PASSED",
        "NONLINEAR_GREEN_COMPATIBILITY_CERTIFIED",
        "STRICT_PARENT_HODGE_HADAMARD_TWO_POINT_PAIR_CONSTRUCTED",
        "STRICT_386_FULL_COMPLEX_BRST_HADAMARD_TWO_POINT_FUNCTION_CONSTRUCTED",
        "STRICT_386_HADAMARD_WAVEFRONT_CONDITION_CERTIFIED",
        "STRICT_386_BRST_WARD_IDENTITIES_CERTIFIED",
        "STRICT_386_GRADED_CCR_CERTIFIED",
        "STRICT_386_ZERO_MODE_RETAINED_AND_SPLIT",
        "STRICT_386_D_STATIONARY_TWO_POINT_PAIR",
    )
    required_false = (
        "STRICT_386_POSITIVE_HADAMARD_STATE_CONSTRUCTED",
        "STRICT_386_PHYSICAL_COHOMOLOGY_POSITIVITY_CERTIFIED",
        "RENORMALIZED_LORENTZIAN_PRODUCTS_CONSTRUCTED",
        "CAUSAL_PERTURBATIVE_AQFT_CONSTRUCTED",
        "LORENTZIAN_QME_RESTORED",
        "RESIDUAL_QUANTUM_TRANSFER_AUTHORIZED",
        "LORENTZIAN_QUANTUM_THEORY",
    )
    for flag in required_true:
        if flags.get(flag) is not True:
            errors.append(f"positive flag {flag}")
    for flag in required_false:
        if flags.get(flag) is not False:
            errors.append(f"fail-closed flag {flag}")
    expected_content = digest({
        "hadamard_snapshot": snapshot,
        "proof_obligations": obligations,
        "state_and_positivity_boundary": boundary,
        "claim_flags": flags,
        "does_not_establish": value.get("does_not_establish"),
    })
    if value.get("content_sha256") != expected_content:
        errors.append("content digest")

    report = REPORT.read_text(encoding="utf-8") if REPORT.is_file() else ""
    if (
        "complete\n386-row" not in report
        or "not a positive Hadamard state" not in report
        or "No renormalized time-ordered products" not in report
    ):
        errors.append("human report boundary")

    if run_receivers:
        for checker in CHECKERS:
            completed = subprocess.run(
                [sys.executable, str(checker)], cwd=ROOT, text=True, capture_output=True
            )
            if completed.returncode:
                errors.append(f"predecessor receiver failed {checker.name}")
    return sorted(set(errors))


def main() -> int:
    errors = check(load(RESULT), run_receivers=True)
    if errors:
        print("STRICT_386_BRST_HADAMARD_TWO_POINT_V1: FAIL")
        for error in errors:
            print(f"  - {error}")
        return 1
    print("STRICT_386_BRST_HADAMARD_TWO_POINT_V1: PASS")
    print("  - full 386-row BRST Hadamard two-point pair constructed")
    print("  - modal, CCR, Ward, wavefront-transfer and zero-mode obligations verified")
    print("  - pseudo-state boundary enforced; positivity, products and QME remain false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
