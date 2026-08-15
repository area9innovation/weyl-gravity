#!/usr/bin/env python3
"""Independent checker for the strict graph Green-action operator names."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_386_GRAPH_GREEN_ACTION_NAME_V1.json"

INPUTS = (
    HERE / "certificates/STRICT_386_GRAPH_Q1_SDR_COMPONENT_JETS_V1.json",
    ROOT / "covariant_completion/certificates/adjoint_tractor_green_transfer.json",
    ROOT / "covariant_completion/certificates/adjoint_tractor_bgg_curved_pbw.json",
    ROOT / "covariant_completion/certificates/curved_full_prolonged_green_homotopy_assembly.json",
    ROOT / "covariant_completion/certificates/adjoint_tractor_bgg_differential_screen_matrices.json",
    ROOT / "covariant_completion/certificates/adjoint_tractor_kostant_compression_matrices.json",
    ROOT / "covariant_completion/certificates/curved_prolonged_metric_endpoint_coefficients.json",
    ROOT / "foundations/literature-causal-green-atlas-v1.json",
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def differentiate(value: dict[tuple[str, int], int]) -> dict[tuple[str, int], int]:
    output: dict[tuple[str, int], int] = {}
    for (function, power), coefficient in value.items():
        key = (("cos", power + 1) if function == "sin" else ("sin", power + 1))
        signed = coefficient if function == "sin" else -coefficient
        output[key] = output.get(key, 0) + signed
    return {key: coefficient for key, coefficient in output.items() if coefficient}


def modal_replay() -> dict[str, str]:
    kernel = {("sin", -1): 1}
    first, second = differentiate(kernel), differentiate(differentiate(kernel))
    residual = dict(second)
    for (function, power), coefficient in kernel.items():
        key = (function, power + 2)
        residual[key] = residual.get(key, 0) + coefficient
        if residual[key] == 0:
            residual.pop(key)
    return {
        "positive_kernel_value_at_zero": "0",
        "positive_kernel_first_derivative_at_zero": str(first.get(("cos", 0), 0)),
        "positive_kernel_ode_residual": "0" if not residual else str(residual),
        "zero_kernel_value_at_zero": "0",
        "zero_kernel_first_derivative_at_zero": "1",
        "zero_kernel_ode_residual": "0",
    }


def local(node: Any, map_id: str) -> bool:
    return isinstance(node, dict) and node == {"node": "LOCAL_MAP", "map_id": map_id}


def action_shape(item: Any, sign: str) -> bool:
    if not isinstance(item, dict) or item.get("sign") != sign:
        return False
    parent = item.get("parent_green_name", {})
    if parent.get("node") != "HODGE_PROJECTOR_DUHAMEL_SERIES" or parent.get("sign") != sign:
        return False
    if parent.get("orientation") != ("future/retarded" if sign == "plus" else "past/advanced"):
        return False
    parent_h = item.get("parent_homotopy_name", {})
    if parent_h.get("node") != "COMPOSE" or not local(parent_h.get("children", [None])[0], "W_parent"):
        return False
    tf = item.get("tracefree_endpoint_name", {})
    if tf.get("node") != "COMPOSE" or len(tf.get("children", [])) != 3:
        return False
    if not local(tf["children"][0], "p_BGG") or not local(tf["children"][2], "i_BGG"):
        return False
    endpoint = item.get("endpoint_30_name", {})
    if endpoint.get("node") != "COMPOSE" or len(endpoint.get("children", [])) != 3:
        return False
    if not local(endpoint["children"][0], "U_trace_Weyl") or not local(endpoint["children"][2], "U_trace_Weyl_inverse"):
        return False
    full = item.get("full_graph_386_name", {})
    if full.get("node") != "SUM" or len(full.get("children", [])) != 2:
        return False
    if not local(full["children"][0], "H_alg_graph"):
        return False
    composed = full["children"][1]
    if composed.get("node") != "COMPOSE" or len(composed.get("children", [])) != 3:
        return False
    if not local(composed["children"][0], "i_end_graph") or not local(composed["children"][2], "p_end_graph"):
        return False
    return item.get("canonical_name_sha256") == digest(full)


def check(value: dict[str, Any] | None = None) -> list[str]:
    value = json.loads(RESULT.read_text()) if value is None else value
    errors: list[str] = []
    if value.get("result_id") != "STRICT_386_GRAPH_GREEN_ACTION_NAME_V1" or value.get("lifecycle") != "CLASSIFIED":
        errors.append("identity/lifecycle")
    if value.get("dependency_tags") != ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"]:
        errors.append("dependency tags")

    provenance = value.get("provenance", {}).get("inputs", [])
    if len(provenance) != len(INPUTS):
        errors.append("provenance count")
    for item, expected in zip(provenance, INPUTS):
        if item.get("path") != str(expected.relative_to(ROOT)) or item.get("sha256") != sha(expected):
            errors.append("provenance " + str(expected.relative_to(ROOT)))

    sources = value.get("analytic_sources", [])
    if [item.get("id") for item in sources] != ["baer-2015", "lauret-2018"]:
        errors.append("analytic source inventory")
    expected_source_hashes = {
        "baer-2015": "879948318de8b4a5a74b52179f78120d074bc7773734b82495b6db4c363f4c99",
        "lauret-2018": "6b20b886450706d72467121560662fda6f88b319323930f3270ed31741fcb244",
    }
    if any(item.get("artifact", {}).get("status") != "CONTENT_PINNED" or item.get("artifact", {}).get("sha256") != expected_source_hashes.get(item.get("id")) for item in sources):
        errors.append("analytic source content pins")
    if not any("Theorem 2.1" in item.get("supports", "") and "n=2" in item.get("supports", "") for item in sources):
        errors.append("S3 spectral-source specialization")

    carrier = value.get("carrier", {})
    if carrier.get("graph_rows") != 386 or carrier.get("tractor_rank") != 15 or carrier.get("parent_bundle_ranks") != [15, 60, 60, 15]:
        errors.append("carrier")
    spaces = value.get("represented_spaces", {})
    if spaces.get("source", {}).get("space") != "Gamma_c^infinity(M,F)" or "LF" not in spaces.get("source", {}).get("topology", ""):
        errors.append("source space/topology")
    if "Frechet" not in spaces.get("target", {}).get("topology", ""):
        errors.append("target topology")
    if spaces.get("distribution_kernel", {}).get("kernel_bytes_serialized") is not False:
        errors.append("kernel-byte boundary")

    spectral = value.get("parent_spectral_name", {})
    expected_spectrum = [
        ("SPATIAL_SCALAR", "k>=0", "k*(k+2)", "(k+1)^2", "k=0"),
        ("SPATIAL_EXACT_ONE_FORM", "k>=1", "k*(k+2)", "(k+1)^2", "none"),
        ("SPATIAL_COEXACT_ONE_FORM", "k>=1", "(k+1)^2", "2*k*(k+2)", "none"),
    ]
    actual_spectrum = [
        (item.get("branch"), item.get("index"), item.get("eigenvalue"), item.get("multiplicity_before_tractor_rank"), item.get("zero_mode"))
        for item in spectral.get("spatial_spectrum", [])
    ]
    if actual_spectrum != expected_spectrum or spectral.get("tractor_multiplicity") != 15:
        errors.append("Hodge spectrum")
    modes = spectral.get("modal_exact_checks", {})
    if any(modes.get(key) != expected for key, expected in modal_replay().items()):
        errors.append("modal Green replay")
    scalar = spectral.get("scalar_kernel", {})
    if scalar.get("plus") != "H(t-r) s_lambda(t-r)" or scalar.get("minus") != "-H(r-t) s_lambda(t-r)":
        errors.append("causal kernel orientation")
    convergence = spectral.get("convergence", {})
    if convergence.get("effective_uniform_rate_claimed") is not False or "continuous" not in convergence.get("operator_continuity", ""):
        errors.append("convergence boundary")

    names = value.get("operator_names", {})
    if not action_shape(names.get("plus"), "plus") or not action_shape(names.get("minus"), "minus"):
        errors.append("operator-name DAG")
    if names.get("plus", {}).get("canonical_name_sha256") == names.get("minus", {}).get("canonical_name_sha256"):
        errors.append("sign names conflated")

    replay = value.get("analytic_and_exact_replay", {})
    required = (
        "modal_inverse_jump_checked_exactly", "zero_mode_checked_exactly",
        "parent_two_sided_inverse_imported", "parent_LF_to_Frechet_continuity_imported",
        "parent_causal_support_imported", "curved_BGG_chain_maps_exact", "graph_SDR_exact",
        "endpoint_homotopy_identity_exact", "full_graph_homotopy_identity_exact",
        "advanced_retarded_adjoint_exact", "operator_name_digests_distinct",
    )
    if not all(replay.get(key) is True for key in required):
        errors.append("analytic/exact replay")

    strength = value.get("foundational_strength", {})
    if strength.get("weakest_base") != "NOT_ESTABLISHED" or strength.get("eigenvector_choice_operation") is not False or strength.get("physics_implies_choice_principle") is not False or strength.get("spectral_completeness_proof_formalized") is not False:
        errors.append("foundational boundary")
    if strength.get("Bishop_constructive_proof") is not False or strength.get("TTE_computability") is not False:
        errors.append("constructive/computable overclaim")

    gate = value.get("gate_disposition", {})
    if gate.get("endpoint_green_convergent_name_serialized") is not True or gate.get("full_graph_green_convergent_name_serialized") is not True:
        errors.append("convergent-name disposition")
    for key in ("receiver_executable_numeric_solver_serialized", "distribution_kernel_bytes_serialized", "one_common_unary_causal_snapshot_accepted"):
        if gate.get(key) is not False:
            errors.append("gate promotion " + key)
    if gate.get("classical_import_gate_a_status") != "FAIL_CLOSED":
        errors.append("Gate A promotion")

    flags = value.get("claim_flags", {})
    for key in ("STRICT_ENDPOINT_GREEN_CONVERGENT_NAME_SERIALIZED", "STRICT_FULL_GRAPH_GREEN_CONVERGENT_NAME_SERIALIZED", "STRICT_386_REPRESENTED_GREEN_ACTIONS_SERIALIZED"):
        if flags.get(key) is not True:
            errors.append("positive flag " + key)
    for key in ("STRICT_386_RECEIVER_EXECUTABLE_NUMERIC_GREEN_SOLVER", "STRICT_386_DISTRIBUTION_KERNEL_BYTES_SERIALIZED", "CLASSICAL_IMPORT_GATE_PASSED", "STRICT_386_LOCAL_D_CERTIFIED", "STRICT_386_Q2_GREEN_COMPATIBILITY_CERTIFIED", "HADAMARD_STATE_CONSTRUCTED", "RENORMALIZED_LORENTZIAN_PRODUCTS", "QME_RESTORED", "RESIDUAL_TRANSFERRED", "LORENTZIAN_QUANTUM_THEORY"):
        if flags.get(key) is not False:
            errors.append("claim promotion " + key)

    hashes = value.get("canonical_hashes", {})
    if hashes.get("plus_action_name_sha256") != names.get("plus", {}).get("canonical_name_sha256"):
        errors.append("plus hash")
    if hashes.get("minus_action_name_sha256") != names.get("minus", {}).get("canonical_name_sha256"):
        errors.append("minus hash")
    if hashes.get("represented_spaces_sha256") != digest(spaces) or hashes.get("transport_contract_sha256") != digest(value.get("transport_contract", {})):
        errors.append("content hashes")
    projection = (
        "carrier", "analytic_sources", "represented_spaces", "parent_spectral_name", "operator_names",
        "transport_contract", "analytic_and_exact_replay", "foundational_strength",
        "gate_disposition", "claim_flags", "does_not_establish", "next_gate",
        "canonical_hashes",
    )
    if value.get("independent_checker", {}).get("expected_digest") != digest({key: value[key] for key in projection}):
        errors.append("canonical projection digest")
    return errors


def main() -> int:
    errors = check()
    print("STRICT_386_GRAPH_GREEN_ACTION_NAME_V1: " + ("PASS" if not errors else "FAIL"))
    for error in errors:
        print("  - " + error)
    if not errors:
        print("  - parent, endpoint and 386-row sign-oriented convergent names replay")
        print("  - zero mode, topology, support, adjoint and promotion boundaries pass")
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
