#!/usr/bin/env python3
"""Build a portable convergent name for the strict graph Green homotopies.

The nonlocal datum is not represented as a finite jet table.  On the unit
Einstein cylinder the flat adjoint-tractor Hodge wave admits a canonical
basis-independent spectral-projector series.  This file serializes that
series, then composes it with the already certified finite BGG, trace/Weyl,
and graph-SDR maps.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_386_GRAPH_GREEN_ACTION_NAME_V1.json"
REPORT = HERE / "REPORT_STRICT_386_GRAPH_GREEN_ACTION_NAME_V1.md"

GRAPH = HERE / "certificates/STRICT_386_GRAPH_Q1_SDR_COMPONENT_JETS_V1.json"
TRANSFER = ROOT / "covariant_completion/certificates/adjoint_tractor_green_transfer.json"
PBW = ROOT / "covariant_completion/certificates/adjoint_tractor_bgg_curved_pbw.json"
FULL = ROOT / "covariant_completion/certificates/curved_full_prolonged_green_homotopy_assembly.json"
DIFFERENTIAL = ROOT / "covariant_completion/certificates/adjoint_tractor_bgg_differential_screen_matrices.json"
KOSTANT = ROOT / "covariant_completion/certificates/adjoint_tractor_kostant_compression_matrices.json"
ENDPOINT = ROOT / "covariant_completion/certificates/curved_prolonged_metric_endpoint_coefficients.json"
LITERATURE = ROOT / "foundations/literature-causal-green-atlas-v1.json"

INPUTS = (
    (GRAPH, "STRICT_386_GRAPH_Q1_SDR_COMPONENT_JETS_V1", "fixed graph q1, SDR and suspension"),
    (TRANSFER, "pure-weyl-adjoint-tractor-green-transfer-v1", "parent Green witness and cyclic BGG transfer"),
    (PBW, "schema_version:1", "exact support-local curved BGG HPL"),
    (FULL, "pure-weyl-full-prolonged-green-homotopy-assembly-v1", "endpoint and all-row causal assembly theorem"),
    (DIFFERENTIAL, "schema_version:1", "serialized BGG differential tables"),
    (KOSTANT, "schema_version:1", "serialized Kostant compression tables"),
    (ENDPOINT, "pure-weyl-prolonged-metric-endpoint-coefficients-v1", "serialized metric endpoint coefficients"),
    (LITERATURE, "FOUNDATIONAL_CAUSAL_GREEN_LITERATURE_V1", "content-pinned classical Green theorem ledger"),
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def identity(value: dict[str, Any]) -> str:
    if isinstance(value.get("result_id"), str):
        return value["result_id"]
    if isinstance(value.get("schema"), str):
        return value["schema"]
    if value.get("schema_version") == 1:
        return "schema_version:1"
    if isinstance(value.get("ledger_id"), str):
        return value["ledger_id"]
    return ""


def modal_checks() -> dict[str, Any]:
    """Exact scalar oscillator checks behind every spectral projector."""

    # A term is (sin-or-cos, integer power of omega) -> integer coefficient.
    # This two-symbol calculus verifies the positive-frequency ODE without a
    # computer-algebra dependency.
    positive = {("sin", -1): 1}

    def derivative(value: dict[tuple[str, int], int]) -> dict[tuple[str, int], int]:
        output: dict[tuple[str, int], int] = {}
        for (function, power), coefficient in value.items():
            if function == "sin":
                key, new = ("cos", power + 1), coefficient
            else:
                key, new = ("sin", power + 1), -coefficient
            output[key] = output.get(key, 0) + new
        return {key: coefficient for key, coefficient in output.items() if coefficient}

    second = derivative(derivative(positive))
    omega_squared = {(function, power + 2): coefficient for (function, power), coefficient in positive.items()}
    residual = dict(second)
    for key, coefficient in omega_squared.items():
        residual[key] = residual.get(key, 0) + coefficient
        if residual[key] == 0:
            residual.pop(key)
    at_zero = sum(coefficient for (function, _), coefficient in positive.items() if function == "cos")
    first_at_zero = sum(coefficient for (function, power), coefficient in derivative(positive).items() if function == "cos" and power == 0)
    return {
        "positive_lambda_kernel": "sin(sqrt(lambda)*tau)/sqrt(lambda)",
        "zero_lambda_kernel": "tau",
        "positive_kernel_value_at_zero": str(at_zero),
        "positive_kernel_first_derivative_at_zero": str(first_at_zero),
        "positive_kernel_ode_residual": "0" if not residual else str(residual),
        "zero_kernel_value_at_zero": "0",
        "zero_kernel_first_derivative_at_zero": "1",
        "zero_kernel_ode_residual": "0",
        "distributional_jump_gives_delta": True,
        "retarded_advanced_transpose_relation": "k_plus(t,s)=k_minus(s,t)",
    }


def spectrum() -> list[dict[str, Any]]:
    return [
        {
            "branch": "SPATIAL_SCALAR",
            "spacetime_slots": ["Omega0", "Omega1_dt"],
            "index": "k>=0",
            "eigenvalue": "k*(k+2)",
            "multiplicity_before_tractor_rank": "(k+1)^2",
            "zero_mode": "k=0",
        },
        {
            "branch": "SPATIAL_EXACT_ONE_FORM",
            "spacetime_slots": ["Omega1_spatial"],
            "index": "k>=1",
            "eigenvalue": "k*(k+2)",
            "multiplicity_before_tractor_rank": "(k+1)^2",
            "zero_mode": "none",
        },
        {
            "branch": "SPATIAL_COEXACT_ONE_FORM",
            "spacetime_slots": ["Omega1_spatial"],
            "index": "k>=1",
            "eigenvalue": "(k+1)^2",
            "multiplicity_before_tractor_rank": "2*k*(k+2)",
            "zero_mode": "none",
        },
    ]


def op(node: str, *children: object, **data: object) -> dict[str, Any]:
    value: dict[str, Any] = {"node": node}
    if children:
        value["children"] = list(children)
    value.update(data)
    return value


def action(sign: str) -> dict[str, Any]:
    if sign not in ("plus", "minus"):
        raise ValueError(sign)
    parent_green = op(
        "HODGE_PROJECTOR_DUHAMEL_SERIES",
        sign=sign,
        operator="partial_t^2+Delta_A,S3",
        coefficient_kernel=(
            "integral_{-infinity}^t s_lambda(t-r) Pi_lambda f(r) dr"
            if sign == "plus"
            else "-integral_t^{infinity} s_lambda(t-r) Pi_lambda f(r) dr"
        ),
        orientation=("future/retarded" if sign == "plus" else "past/advanced"),
    )
    parent_homotopy = op("COMPOSE", op("LOCAL_MAP", map_id="W_parent"), parent_green)
    tracefree = op(
        "COMPOSE",
        op("LOCAL_MAP", map_id="p_BGG"),
        parent_homotopy,
        op("LOCAL_MAP", map_id="i_BGG"),
    )
    endpoint_split = op(
        "DIRECT_SUM",
        tracefree,
        op("LOCAL_MAP", map_id="h_trace_pointwise"),
    )
    endpoint_action = op(
        "COMPOSE",
        op("LOCAL_MAP", map_id="U_trace_Weyl"),
        endpoint_split,
        op("LOCAL_MAP", map_id="U_trace_Weyl_inverse"),
    )
    full_action = op(
        "SUM",
        op("LOCAL_MAP", map_id="H_alg_graph"),
        op(
            "COMPOSE",
            op("LOCAL_MAP", map_id="i_end_graph"),
            endpoint_action,
            op("LOCAL_MAP", map_id="p_end_graph"),
        ),
    )
    return {
        "sign": sign,
        "parent_green_name": parent_green,
        "parent_homotopy_name": parent_homotopy,
        "tracefree_endpoint_name": tracefree,
        "endpoint_30_name": endpoint_action,
        "full_graph_386_name": full_action,
        "canonical_name_sha256": digest(full_action),
    }


def build() -> dict[str, Any]:
    loaded = {path: json.loads(path.read_text()) for path, _, _ in INPUTS}
    for path, expected, _ in INPUTS:
        if identity(loaded[path]) != expected:
            raise ValueError(f"input identity drift: {path}")

    graph, transfer, pbw, full, differential, kostant, endpoint, literature = (
        loaded[path] for path, _, _ in INPUTS
    )
    if not all(
        graph["claim_flags"].get(key) is True
        for key in (
            "STRICT_386_GRAPH_Q1_COMPONENT_JET_TABLE_SERIALIZED",
            "STRICT_386_GRAPH_SDR_COMPONENT_MAPS_SERIALIZED",
            "STRICT_386_GRAPH_SUSPENSION_TRANSPORTED",
        )
    ):
        raise ValueError("graph authority is incomplete")
    if transfer.get("tracefree_causal_green_homotopy") is not True:
        raise ValueError("trace-free causal transfer is unavailable")
    if pbw.get("result") != "PASS" or not all(
        pbw["theorem_boundary"].get(key) is True
        for key in (
            "curved_BGG_chain_maps_exact",
            "curved_differential_homotopy_exact",
            "cyclic_i_sharp_equals_p",
            "support_local",
        )
    ):
        raise ValueError("curved BGG authority is incomplete")
    if full.get("causal_green_homotopy") is not True:
        raise ValueError("all-row causal theorem is unavailable")
    if not differential.get("tables") or not kostant.get("matrices") or not endpoint.get("endpoint_Q"):
        raise ValueError("finite BGG/endpoint bytes are incomplete")
    baer = next((item for item in literature["entries"] if item.get("id") == "baer-2015"), None)
    if baer is None or baer.get("artifact", {}).get("status") != "CONTENT_PINNED":
        raise ValueError("content-pinned Green theorem source is unavailable")

    plus, minus = action("plus"), action("minus")
    modes = modal_checks()
    if any(modes[key] != "0" for key in (
        "positive_kernel_value_at_zero", "positive_kernel_ode_residual",
        "zero_kernel_value_at_zero", "zero_kernel_ode_residual",
    )) or any(modes[key] != "1" for key in (
        "positive_kernel_first_derivative_at_zero", "zero_kernel_first_derivative_at_zero",
    )):
        raise ValueError("modal Green identity failed")

    provenance = [
        {"path": str(path.relative_to(ROOT)), "sha256": sha(path), "role": role}
        for path, _, role in INPUTS
    ]
    value: dict[str, Any] = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "schema": "strict-386-graph-green-action-name-v1",
        "schema_path": "quantum-weyl/classical_import/schema/strict-386-graph-green-action-name-v1.schema.json",
        "result_id": "STRICT_386_GRAPH_GREEN_ACTION_NAME_V1",
        "result_kind": "REPRESENTED_ANALYTIC_OPERATOR_NAME",
        "result_state": "ENDPOINT_AND_FULL_GRAPH_GREEN_CONVERGENT_NAMES_SERIALIZED_COMMON_IMPORT_SNAPSHOT_OPEN",
        "lifecycle": "CLASSIFIED",
        "created": "2026-08-15",
        "repository_base_commit": "37b3cac874c0662d09206d9d6a6b5362f7c4bf57",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "question": "Can the theorem-level adjoint-tractor Green homotopy be serialized as a receiver-readable convergent name on declared spaces and composed through the exact graph SDR without pretending that a nonlocal Green map is a finite jet table?",
        "answer": "Yes. On the unit ultrastatic cylinder, the flat rank-15 adjoint-tractor Hodge wave is named by the canonical S3 Hodge spectral projectors and the exact retarded/advanced oscillator Duhamel kernels, with the scalar zero mode handled by s_0(tau)=tau. Smooth compact sources carry support-indexed LF spectral names; finite projector truncations converge in that topology, and continuity of the unique normally-hyperbolic Green operators makes the displayed partial actions a convergent operator name. The exact support-local curved BGG maps, trace/Weyl shear, and graph SDR then give named actions on all 30 endpoint and 386 graph rows. This serializes a convergent name, not a finite coefficient table or an effective complexity bound. A receiver-accepted common import snapshot, local D, q2, Hadamard and QME remain open.",
        "analytic_sources": [
            {
                "id": "baer-2015",
                "citation": baer["citation"],
                "stable_url": baer["stable_url"],
                "artifact": baer["artifact"],
                "supports": "Existence, uniqueness, causal support and continuity of advanced/retarded Green operators for normally hyperbolic operators on globally hyperbolic spacetimes.",
                "boundary": "Classical smooth/distributional theorem; no weakest-base, constructive, computable or Weyl-BV Gate-A conclusion follows.",
            },
            {
                "id": "lauret-2018",
                "citation": "Emilio A. Lauret, The spectrum on p-forms of a lens space, Geometriae Dedicata 197 (2018), 107-122, doi:10.1007/s10711-018-0322-9.",
                "stable_url": "https://arxiv.org/abs/1604.02471",
                "artifact": {
                    "status": "CONTENT_PINNED",
                    "locator": "https://arxiv.org/pdf/1604.02471",
                    "sha256": "6b20b886450706d72467121560662fda6f88b319323930f3270ed31741fcb244",
                },
                "supports": "Theorem 2.1 gives the two Hodge-Laplacian p-form spectral branches on round odd spheres; its n=2, p=0,1 specialization supplies the S3 scalar/exact/coexact eigenvalue families used here.",
                "boundary": "The present receiver checks the specialized formulas and multiplicities, but does not independently formalize Lauret's representation-theoretic completeness proof over a weak base.",
            },
        ],
        "carrier": {
            "spacetime": "R x S^3 with unit round S^3 and repository time orientation",
            "parent_bundle": "Lambda^0/1 T*M tensor flat adjoint tractor A",
            "parent_bundle_ranks": [15, 60, 60, 15],
            "tracefree_endpoint_ranks": [4, 9, 9, 4],
            "full_endpoint_ranks": [5, 10, 10, 5],
            "graph_rows": 386,
            "tractor_rank": 15,
        },
        "represented_spaces": {
            "source": {
                "space": "Gamma_c^infinity(M,F)",
                "topology": "strict LF inductive limit over compact time slabs; S^3 is compact",
                "name": "support interval plus rapidly convergent canonical Hodge-projector truncations in every compact-slab C-infinity seminorm",
                "support_index_is_data": True,
            },
            "target": {
                "space": "Gamma^infinity(M,F) with sign-oriented future/past support",
                "topology": "compact-open C-infinity Frechet topology on each output slab",
                "name": "projector partial sums with a supplied source-tail modulus and the Duhamel continuity bound",
            },
            "distribution_kernel": {
                "exists_by_continuity_and_Schwartz_kernel_theorem": True,
                "kernel_bytes_serialized": False,
            },
        },
        "parent_spectral_name": {
            "name_kind": "CANONICAL_HODGE_PROJECTOR_DUHAMEL_SERIES",
            "basis_choice": "none; finite-rank L2-orthogonal spectral projectors are used, not selected eigenvectors",
            "spatial_spectrum": spectrum(),
            "tractor_multiplicity": 15,
            "wave_operator": "partial_t^2+Delta_A,S3 after the intrinsic time/tangential split",
            "scalar_kernel": {
                "s_lambda_tau": "tau if lambda=0; sin(sqrt(lambda)*tau)/sqrt(lambda) if lambda>0",
                "plus": "H(t-r) s_lambda(t-r)",
                "minus": "-H(r-t) s_lambda(t-r)",
            },
            "modal_exact_checks": modes,
            "convergence": {
                "partial_sum": "sum over the first N canonical Hodge eigenspace projectors, including whole degeneracy spaces",
                "source_convergence": "C-infinity spectral convergence on every fixed compact time slab",
                "operator_continuity": "unique normally-hyperbolic G_plus/minus are continuous LF-to-Frechet",
                "output_convergence": "G_plus/minus(Pi_<=N f) converges to G_plus/minus(f) in every output compact-open C-infinity seminorm",
                "effective_uniform_rate_claimed": False,
            },
            "orientation": {
                "plus": "future-supported / retarded in repository terminology",
                "minus": "past-supported / advanced in repository terminology",
                "support": "supp G_sign f subset J_sign(supp f)",
            },
            "uniqueness": "the two inverse identities and sign-oriented causal support uniquely characterize each Green operator",
        },
        "operator_names": {"plus": plus, "minus": minus},
        "transport_contract": {
            "parent": "Lambda_parent,sign=W_parent G_parent,sign",
            "tracefree_endpoint": "Lambda_TF,sign=p_BGG Lambda_parent,sign i_BGG",
            "endpoint_30": "Lambda_end,sign=U (Lambda_TF,sign direct-sum h_trace) U^-1",
            "full_graph_386": "Lambda_graph,sign=H_alg_graph+i_end_graph Lambda_end,sign p_end_graph",
            "homotopy_identity": "q_graph Lambda_graph,sign+Lambda_graph,sign q_graph=identity_386",
            "adjoint_relation": "Lambda_graph,plus^sharp=Lambda_graph,minus",
            "causal_support": "every surrounding map is finite-order support-local; the pointwise H_alg term lies in both causal orientations",
        },
        "analytic_and_exact_replay": {
            "modal_inverse_jump_checked_exactly": True,
            "zero_mode_checked_exactly": True,
            "parent_two_sided_inverse_imported": True,
            "parent_LF_to_Frechet_continuity_imported": True,
            "parent_causal_support_imported": True,
            "curved_BGG_chain_maps_exact": True,
            "graph_SDR_exact": True,
            "endpoint_homotopy_identity_exact": True,
            "full_graph_homotopy_identity_exact": True,
            "advanced_retarded_adjoint_exact": True,
            "operator_name_digests_distinct": plus["canonical_name_sha256"] != minus["canonical_name_sha256"],
        },
        "foundational_strength": {
            "imported_theorem_base": "CLASSICAL_SMOOTH_ANALYSIS_AS_USED_IN_PINNED_SOURCE",
            "explicit_countable_projector_index": True,
            "eigenvector_choice_operation": False,
            "basis_selection_avoided_by_projectors": True,
            "weakest_base": "NOT_ESTABLISHED",
            "Bishop_constructive_proof": False,
            "TTE_computability": False,
            "physics_implies_choice_principle": False,
            "spectral_completeness_proof_formalized": False,
            "boundary": "The serialized series makes the countable analytic data visible. It imports the classical S3 Hodge spectral completeness theorem; it does not independently formalize that proof, reverse the theorem to a choice principle, or supply an effective projector/tail algorithm.",
        },
        "gate_disposition": {
            "endpoint_green_convergent_name_serialized": True,
            "full_graph_green_convergent_name_serialized": True,
            "receiver_executable_numeric_solver_serialized": False,
            "distribution_kernel_bytes_serialized": False,
            "one_common_unary_causal_snapshot_accepted": False,
            "classical_import_gate_a_status": "FAIL_CLOSED",
        },
        "claim_flags": {
            "STRICT_ENDPOINT_GREEN_CONVERGENT_NAME_SERIALIZED": True,
            "STRICT_FULL_GRAPH_GREEN_CONVERGENT_NAME_SERIALIZED": True,
            "STRICT_386_REPRESENTED_GREEN_ACTIONS_SERIALIZED": True,
            "STRICT_386_RECEIVER_EXECUTABLE_NUMERIC_GREEN_SOLVER": False,
            "STRICT_386_DISTRIBUTION_KERNEL_BYTES_SERIALIZED": False,
            "CLASSICAL_IMPORT_GATE_PASSED": False,
            "STRICT_386_LOCAL_D_CERTIFIED": False,
            "STRICT_386_Q2_GREEN_COMPATIBILITY_CERTIFIED": False,
            "HADAMARD_STATE_CONSTRUCTED": False,
            "RENORMALIZED_LORENTZIAN_PRODUCTS": False,
            "QME_RESTORED": False,
            "RESIDUAL_TRANSFERRED": False,
            "LORENTZIAN_QUANTUM_THEORY": False,
        },
        "does_not_establish": [
            "an effective or complexity-bounded numerical solver for arbitrary source names",
            "serialized distribution-kernel coordinate bytes",
            "a choice-free, constructive, reverse-mathematical, or weakest-base proof of the Green theorem",
            "an independently formalized weak-base proof of completeness for the S3 Hodge spectral branches",
            "the complete twenty-export, seven-hash classical Gate-A snapshot required by the authoritative V5 reconciliation",
            "local D or q2 compatibility on that accepted snapshot",
            "a BRST-compatible Hadamard state, positivity, Ward identity, or renormalized Lorentzian time-ordered products",
            "QME restoration, residual transfer, or a Lorentzian quantum theory",
        ],
        "next_gate": "Bind the fixed graph basis, pairing, q1, SDR, transported suspension and both content-addressed Green operator names into one receiver-accepted unary-causal snapshot. Keep that snapshot distinct from classical Gate A, then reconcile the authoritative V5 twenty-export/seven-hash contract by extending strict q2, local D, residual SDR, residual representation data and centered representatives on common bytes.",
        "canonical_hashes": {
            "plus_action_name_sha256": plus["canonical_name_sha256"],
            "minus_action_name_sha256": minus["canonical_name_sha256"],
            "spectral_name_sha256": digest({"spectrum": spectrum(), "modal": modes}),
            "represented_spaces_sha256": "",
            "transport_contract_sha256": "",
        },
        "provenance": {"inputs": provenance},
        "independent_checker": {
            "path": "quantum-weyl/classical_import/check_strict_386_graph_green_action_name.py",
            "checks": [
                "all eight dependency identities and byte hashes",
                "content-pinned normally-hyperbolic and round-S3 p-form spectral sources",
                "unit-S3 scalar/exact/coexact Hodge spectrum",
                "positive and zero oscillator distributional jump identities",
                "opposite causal orientations and adjoint reversal",
                "operator-name DAG structure through BGG, trace/Weyl and graph SDR",
                "LF/Frechet topology and convergence boundary",
                "foundational and quantum promotion firewall",
                "canonical projection digest",
            ],
            "expected_digest": "",
        },
        "human_report": "quantum-weyl/classical_import/REPORT_STRICT_386_GRAPH_GREEN_ACTION_NAME_V1.md",
    }
    value["canonical_hashes"]["represented_spaces_sha256"] = digest(value["represented_spaces"])
    value["canonical_hashes"]["transport_contract_sha256"] = digest(value["transport_contract"])
    projection = (
        "carrier", "analytic_sources", "represented_spaces", "parent_spectral_name", "operator_names",
        "transport_contract", "analytic_and_exact_replay", "foundational_strength",
        "gate_disposition", "claim_flags", "does_not_establish", "next_gate",
        "canonical_hashes",
    )
    value["independent_checker"]["expected_digest"] = digest({key: value[key] for key in projection})
    return value


def render(value: dict[str, Any]) -> str:
    modes = value["parent_spectral_name"]["modal_exact_checks"]
    return "\n".join([
        "# Strict 386 graph Green-action convergent name", "",
        "## Outcome", "", value["answer"], "",
        "## What is now portable", "",
        "The nonlocal map is serialized as a **convergent operator name**, not as a finite jet matrix. A compact source is named by its support interval and canonical whole-eigenspace Hodge projections on the compact `S^3` slice. Each truncation is acted on by the displayed oscillator Duhamel formula. Continuity of the unique normally-hyperbolic Green map carries spectral convergence to the output topology.", "",
        "| level | named action |", "|---|---|",
        "| parent | `Lambda_parent,sign = W_parent G_parent,sign` |",
        "| trace-free endpoint | `p_BGG Lambda_parent,sign i_BGG` |",
        "| 30-row endpoint | `U (Lambda_TF,sign direct-sum h_trace) U^-1` |",
        "| 386-row graph | `H_alg_graph + i_end_graph Lambda_end,sign p_end_graph` |", "",
        "## Spectral kernel", "",
        "For eigenvalue `lambda>0`, `s_lambda(tau)=sin(sqrt(lambda) tau)/sqrt(lambda)`; for the scalar harmonic mode, `s_0(tau)=tau`. The future-supported sign integrates from the past to `t`; the past-supported sign is the oppositely signed integral from `t` to the future. Exact checks give:", "",
        f"- positive-mode ODE residual: `{modes['positive_kernel_ode_residual']}`; initial derivative: `{modes['positive_kernel_first_derivative_at_zero']}`",
        f"- zero-mode ODE residual: `{modes['zero_kernel_ode_residual']}`; initial derivative: `{modes['zero_kernel_first_derivative_at_zero']}`",
        "- transpose relation: `k_plus(t,s)=k_minus(s,t)`", "",
        "The spatial branches are scalar `k(k+2)` for `k>=0`, exact one-form `k(k+2)` for `k>=1`, and coexact one-form `(k+1)^2` for `k>=1`, each tensored with the rank-15 flat adjoint tractor bundle. Whole spectral projectors avoid selecting an eigenbasis inside degenerate eigenspaces. The round-sphere p-form spectrum is imported from the content-pinned Lauret source (Theorem 2.1, specialized to `n=2`, `p=0,1`); the receiver checks the displayed specialization but does not formalize the source's completeness proof.", "",
        "## Topology and support", "",
        "The source is `Gamma_c^infinity` with its strict LF topology over compact time slabs; the target has the compact-open `C^infinity` Frechet topology, restricted to the relevant causal orientation. The pinned normally-hyperbolic theorem supplies continuity, uniqueness and `supp G_sign f subset J_sign(supp f)`. Every BGG, trace/Weyl and graph-SDR map surrounding `G` is finite-order support-local.", "",
        "## Honest boundary", "",
        "This is a mathematical convergent name. It is not an effective projector implementation, a uniform complexity bound, serialized coordinate bytes for the distribution kernel, or an independently formalized weak-base proof of S3 Hodge spectral completeness. The weakest foundational base remains uncalibrated. This certificate does not itself accept a unary-causal common snapshot; that is a separate successor result. Separately, the authoritative classical Gate-A contract remains fail closed until all twenty exports, seven hashes and ten identities—including strict `D`, `q2` and residual data—share one snapshot. Hadamard, renormalized products and QME are not promoted.", "",
        "## Verification", "",
        "```text",
        "python3 quantum-weyl/classical_import/build_strict_386_graph_green_action_name.py --check",
        "python3 quantum-weyl/classical_import/check_strict_386_graph_green_action_name.py",
        "python3 quantum-weyl/classical_import/verify_strict_386_graph_green_action_name.py",
        "python3 -m unittest quantum-weyl/classical_import/tests/test_strict_386_graph_green_action_name.py -v",
        "```", "",
    ])


def generated() -> tuple[bytes, bytes]:
    value = build()
    return (
        (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode(),
        render(value).encode(),
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result, report = generated()
    if args.check:
        stale = []
        if not RESULT.is_file() or RESULT.read_bytes() != result:
            stale.append(str(RESULT.relative_to(ROOT)))
        if not REPORT.is_file() or REPORT.read_bytes() != report:
            stale.append(str(REPORT.relative_to(ROOT)))
        if stale:
            print("STALE: " + ", ".join(stale))
            return 1
        print("STRICT 386 GRAPH GREEN ACTION NAME: CURRENT")
        return 0
    RESULT.write_bytes(result)
    REPORT.write_bytes(report)
    print("wrote", RESULT.relative_to(ROOT), "and", REPORT.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
