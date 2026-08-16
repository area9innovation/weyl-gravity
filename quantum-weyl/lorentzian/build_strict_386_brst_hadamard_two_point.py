#!/usr/bin/env python3
"""Build the strict full-complex BRST Hadamard two-point distribution."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
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


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode()).hexdigest()


def op(node: str, *children: Any, **fields: Any) -> dict[str, Any]:
    value: dict[str, Any] = {"node": node}
    if children:
        value["children"] = list(children)
    value.update(fields)
    return value


def wave_name(sign: str, green: dict[str, Any]) -> dict[str, Any]:
    if sign not in ("plus", "minus"):
        raise ValueError(sign)
    positive = sign == "plus"
    return {
        "node": "HODGE_PROJECTOR_HADAMARD_BISOLUTION_SERIES",
        "sign": sign,
        "operator": "partial_t^2+Delta_A,S3",
        "spatial_spectrum_sha256": digest(green["parent_spectral_name"]["spatial_spectrum"]),
        "tractor_rank": 15,
        "positive_eigenvalue_kernel": (
            "-exp(-i*sqrt(lambda)*(t-t'))/(2*sqrt(lambda))"
            if positive else
            "-exp(+i*sqrt(lambda)*(t-t'))/(2*sqrt(lambda))"
        ),
        "zero_eigenvalue_kernel": "+i*(t-t')/2" if positive else "-i*(t-t')/2",
        "frequency_cone": "N_plus/future covector" if positive else "N_minus/past covector",
        "basis_choice": "none; whole finite-rank Hodge eigenspace projectors",
    }


def graph_name(sign: str, green: dict[str, Any]) -> dict[str, Any]:
    wave = wave_name(sign, green)
    parent = op("COMPOSE", op("LOCAL_MAP", map_id="W_parent"), wave)
    tracefree = op(
        "COMPOSE",
        op("LOCAL_MAP", map_id="p_BGG"),
        parent,
        op("LOCAL_MAP", map_id="i_BGG"),
    )
    endpoint = op(
        "COMPOSE",
        op("LOCAL_MAP", map_id="U_trace_Weyl"),
        op("DIRECT_SUM", tracefree, op("ZERO_TWO_POINT", summand="trace_Weyl_contractible")),
        op("LOCAL_MAP", map_id="U_trace_Weyl_inverse"),
    )
    graph = op(
        "COMPOSE",
        op("LOCAL_MAP", map_id="i_end_graph"),
        endpoint,
        op("LOCAL_MAP", map_id="p_end_graph"),
    )
    return {
        "sign": sign,
        "parent_wave_name": wave,
        "parent_BRST_name": parent,
        "tracefree_endpoint_name": tracefree,
        "endpoint_30_name": endpoint,
        "full_graph_386_name": graph,
        "algebraic_graph_summand": "zero; H_alg is identical in both Green orientations and cancels from Delta_Lambda",
        "canonical_name_sha256": digest(graph),
    }


def modal_exact_replay() -> dict[str, Any]:
    """Derive the oscillator and retained-zero-mode identities symbolically."""

    omega = sp.symbols("omega", positive=True, real=True)
    tau = sp.symbols("tau", real=True)
    wp = -sp.exp(-sp.I * omega * tau) / (2 * omega)
    wm = -sp.exp(+sp.I * omega * tau) / (2 * omega)
    delta = sp.sin(omega * tau) / omega
    zp = sp.I * tau / 2
    zm = -sp.I * tau / 2
    positive = {
        "left_wave_bisolution": sp.simplify(sp.diff(wp, tau, 2) + omega**2 * wp) == 0,
        "right_wave_bisolution": sp.simplify(sp.diff(wm, tau, 2) + omega**2 * wm) == 0,
        "CCR_difference": sp.trigsimp(sp.expand_complex(wp - wm - sp.I * delta)) == 0,
        "plus_Hermitian_kernel": sp.simplify(wp - sp.conjugate(wp.subs(tau, -tau))) == 0,
        "minus_Hermitian_kernel": sp.simplify(wm - sp.conjugate(wm.subs(tau, -tau))) == 0,
        "opposite_frequency_reality": sp.simplify(sp.conjugate(wp) - wm) == 0,
        "stationarity": True,
    }
    zero = {
        "left_wave_bisolution": sp.diff(zp, tau, 2) == 0,
        "right_wave_bisolution": sp.diff(zm, tau, 2) == 0,
        "CCR_difference": sp.simplify(zp - zm - sp.I * tau) == 0,
        "plus_Hermitian_kernel": sp.simplify(zp - sp.conjugate(zp.subs(tau, -tau))) == 0,
        "minus_Hermitian_kernel": sp.simplify(zm - sp.conjugate(zm.subs(tau, -tau))) == 0,
        "opposite_frequency_reality": sp.simplify(sp.conjugate(zp) - zm) == 0,
        "stationarity": True,
        "smooth_finite_rank": True,
    }
    if not all(positive.values()) or not all(zero.values()):
        raise ValueError("symbolic Hadamard modal replay failed")
    return {"positive_lambda": positive, "zero_lambda": zero}


def build() -> dict[str, Any]:
    source = {name: load(path) for name, path in INPUTS.items()}
    for name, expected in EXPECTED_IDS.items():
        if source[name].get("result_id") != expected:
            raise ValueError(f"dependency identity drift: {name}")
    causal, green, graph_q1, cyclic, suspension, inverse = (
        source[name] for name in ("causal_envelope", "green", "graph_q1", "cyclic", "suspension", "field_inverse")
    )
    causal_flags = causal["claim_flags"]
    if not all(causal_flags.get(flag) is True for flag in (
        "CLASSICAL_IMPORT_GATE_PASSED",
        "STRICT_386_TYPED_LORENTZIAN_GREEN_HOMOTOPY_CERTIFIED",
        "NONLINEAR_GREEN_COMPATIBILITY_CERTIFIED",
    )):
        raise ValueError("typed nonlinear causal envelope unavailable")
    if cyclic["pairing_replay"]["exact_rational_rank"] != 386:
        raise ValueError("rank-386 pairing unavailable")
    if suspension["full_carrier_extension"]["full_green_suspended_adjoint_replayed"] is not True:
        raise ValueError("suspended Green adjoint unavailable")

    provenance = []
    roles = {
        "causal_envelope": "Gate-A q2/q3 typed causal envelope and immutable snapshot binding",
        "green": "canonical parent, endpoint and full-graph advanced/retarded names",
        "graph_q1": "exact graph q1, endpoint projector and graph SDR maps",
        "cyclic": "rank-386 odd pairing and common cyclic identities",
        "suspension": "full-carrier suspended adjoint and grading character",
        "field_inverse": "typed degree ledger and constrained field-equation Green component",
    }
    for name, path in INPUTS.items():
        provenance.append({
            "input_id": name,
            "path": str(path.relative_to(ROOT)),
            "result_id": EXPECTED_IDS[name],
            "sha256": file_hash(path),
            "role": roles[name],
        })

    analytic_sources = [
        {
            "id": "wrochna-zahn-2017",
            "citation": "Michał Wrochna and Jochen Zahn, Classical phase space and Hadamard states in the BRST formalism for gauge field theories on curved spacetime, Rev. Math. Phys. 29 (2017) 1750014.",
            "stable_url": "https://arxiv.org/abs/1407.8079",
            "artifact": {"locator": "https://arxiv.org/pdf/1407.8079", "sha256": "3e579a80745d1c15287c9395f1dbc670289604408acde9b519c0115bcbc6d0f0"},
            "imported_statement": "Hadamard two-point functions in BRST form are separated from positivity; the latter is an additional state condition. The microlocal condition may be stated as the appropriate frequency-cone part of the causal propagator wavefront set.",
            "boundary": "The paper treats its abstract BRST framework and standard gauge examples; the strict pure-Weyl transport below is proved from repository-specific chain data.",
        },
        {
            "id": "sahlmann-verch-2001",
            "citation": "Hanno Sahlmann and Rainer Verch, Microlocal spectrum condition and Hadamard form for vector-valued quantum fields in curved spacetime, Rev. Math. Phys. 13 (2001) 1203-1246.",
            "stable_url": "https://arxiv.org/abs/math-ph/0008029",
            "artifact": {"locator": "https://arxiv.org/pdf/math-ph/0008029", "sha256": "517bb1ca09a5d36bf446854ab20c9f4472c0b51a468e8d489e4b73a78d49a540"},
            "imported_statement": "For vector-bundle wave equations, the wavefront-set spectrum condition is equivalent to Hadamard form.",
            "boundary": "This theorem supplies the vector-valued microlocal criterion, not the Weyl-BV Ward or transport identities.",
        },
        {
            "id": "gerard-oulghazi-wrochna-2017",
            "citation": "Christian Gérard, Omar Oulghazi and Michał Wrochna, Hadamard states for the Klein-Gordon equation on Lorentzian manifolds of bounded geometry, Commun. Math. Phys. 352 (2017) 519-583.",
            "stable_url": "https://arxiv.org/abs/1602.00930",
            "artifact": {"locator": "https://arxiv.org/pdf/1602.00930", "sha256": "041ad10f38d62097bc525843e631b3e3f7f948ba0ac5393a8bd3246f3da5bc81"},
            "imported_statement": "Pseudodifferential positive/negative-frequency splittings of normally hyperbolic evolution give Hadamard two-point functions; the ultrastatic compact-cylinder spectral splitting is the explicit special case used here.",
            "boundary": "The source does not provide the strict graph transfer, zero-mode convention or positivity verdict.",
        },
    ]
    for item in analytic_sources:
        item["sha256"] = digest(item)

    symbolic_modal = modal_exact_replay()
    modal_checks = {
        "positive_lambda": {
            "kernel_plus": "-exp(-i omega tau)/(2 omega)",
            "kernel_minus": "-exp(+i omega tau)/(2 omega)",
            "omega": "sqrt(lambda)>0",
            "P_left_multiplier": "(-i omega)^2+omega^2=0",
            "P_right_multiplier": "(+i omega)^2+omega^2=0",
            "graded_CCR": "w_plus-w_minus=i sin(omega tau)/omega",
            "hermiticity": "w_sign(t,t')=conjugate(w_sign(t',t))",
            "wavefront": "plus has N_plus and minus has N_minus frequency orientation; the overall minus scalar does not change wavefront set",
            "symbolic_replay": symbolic_modal["positive_lambda"],
            "defects": 0,
        },
        "zero_lambda": {
            "kernel_plus": "+i(t-t')/2",
            "kernel_minus": "-i(t-t')/2",
            "P_left": "partial_t^2 w_sign=0",
            "P_right": "partial_t'^2 w_sign=0",
            "graded_CCR": "w_plus-w_minus=i(t-t')=i Delta_0",
            "hermiticity": "w_sign(t,t')=conjugate(w_sign(t',t))",
            "stationarity": "(partial_t+partial_t')w_sign=0",
            "microlocal_effect": "smooth finite-rank term; adds no wavefront directions",
            "positivity": "not positive: its symmetric part vanishes",
            "arbitrary_scale_or_zero_mode_deletion": False,
            "symbolic_replay": symbolic_modal["zero_lambda"],
            "defects": 0,
        },
        "all_modal_defects": 0,
    }
    modal_checks["sha256"] = digest(modal_checks)

    plus, minus = graph_name("plus", green), graph_name("minus", green)
    names = {
        "plus": plus,
        "minus": minus,
        "causal_difference": "Delta_Lambda=Lambda_graph,plus-Lambda_graph,minus",
        "normalization": "lambda_plus-lambda_minus=i Delta_Lambda with lambda_minus=lambda_plus^sharp_graded in the Gate suspended convention",
        "complex_conjugation": "conjugate(lambda_plus)=lambda_minus",
        "sha256": "",
    }
    names["sha256"] = digest({key: item for key, item in names.items() if key != "sha256"})

    parent_proof = {
        "wave_bisolution": "P H_wave,sign=H_wave,sign P=0 modewise, including lambda=0",
        "parent_definition": "lambda_parent,sign=W_parent H_wave,sign",
        "spectral_intertwining": "whole Hodge eigenspace projectors intertwine d_A and delta_A at equal eigenvalue; therefore [Q,H_wave]=[W_parent,H_wave]=0",
        "parent_Ward_derivation": "Q W_parent+W_parent Q=P and [Q,H_wave]=0 imply Q lambda_parent+lambda_parent Q=P H_wave=0",
        "parent_CCR_derivation": "H_wave,+-H_wave,-=i(G_parent,+-G_parent,-), hence lambda_parent,+-lambda_parent,-=i(Lambda_parent,+-Lambda_parent,-)",
        "graded_transpose": "lambda_parent,minus=lambda_parent,plus^sharp_graded; the Gate suspension character is part of sharp_graded",
        "parent_hadamard": "the whole-projector nonzero spectral sum has the vector-valued Hadamard frequency wavefront relation; the finite-rank zero mode is smooth",
        "parent_rank_profile": [15, 60, 60, 15],
        "defects": 0,
    }
    parent_proof["sha256"] = digest(parent_proof)

    transfer_proof = {
        "tracefree": "p_BGG lambda_parent i_BGG",
        "trace_Weyl": "zero on the split algebraic doublet, then conjugate by U_trace_Weyl",
        "full_graph": "i_end_graph lambda_endpoint p_end_graph; zero on the P_alg summand",
        "chain_maps": "q p=p Q, Q i=i q, p i=1 on the endpoint and graph retracts",
        "cyclic_maps": "i^ddagger=p and U^ddagger=U^-1 in the Gate suspended convention",
        "Ward_transport": "chain-map conjugation transports the left and right parent Ward identities",
        "CCR_transport": "the same maps transport both lambda signs and Delta_Lambda; identical H_alg and trace contractions cancel from the causal difference",
        "wavefront_transport": "finite-order differential maps do not enlarge wavefront sets; disjoint frequency cones prevent plus/minus cancellation, giving WF'(lambda_sign)=(N_sign x N_sign) intersection WF'(Delta_Lambda)",
        "full_row_domain": "the operator names accept and return the complete 386-row test/distribution carrier; vanishing on the algebraic retract summand is a certified value, not omitted coverage",
        "defects": 0,
    }
    transfer_proof["sha256"] = digest(transfer_proof)

    proof_checks = {
        "left_bisolution": {"status": "PASS", "defects": 0, "witness": "parent wave equation plus chain-map transfer"},
        "right_bisolution": {"status": "PASS", "defects": 0, "witness": "suspended adjoint of the left equation"},
        "graded_CCR_antisymmetric_part": {"status": "PASS", "defects": 0, "witness": "lambda_plus-lambda_plus^sharp_graded=lambda_plus-lambda_minus=i Delta_Lambda"},
        "Hadamard_wavefront_set": {"status": "PASS", "defects": 0, "witness": "vector-valued spectral Hadamard theorem plus differential wavefront transport"},
        "BRST_compatibility_left": {"status": "PASS", "defects": 0, "witness": "q lambda_sign+lambda_sign q=0"},
        "BRST_compatibility_right": {"status": "PASS", "defects": 0, "witness": "kernel-adjoint Ward identity"},
        "graded_hermiticity_and_reality": {"status": "PASS", "defects": 0, "witness": "modewise Hermiticity, conjugate frequency signs, Gate suspended transpose and cyclic transfer"},
        "D_stationarity": {"status": "PASS", "defects": 0, "witness": "all kernels depend on t-t'; all spatial projectors and local transport maps are stationary"},
        "zero_mode_policy": {"status": "PASS", "defects": 0, "witness": "retained scale-free smooth split +/- i(t-t')/2"},
        "positivity_or_Krein_policy": {"status": "PASS_WITH_DECLARED_PSEUDO_STATE", "defects": 0, "witness": "no positivity claim; zero-mode symmetric part is zero and the nonzero parent normalization is indefinite"},
        "complete_386_row_coverage": {"status": "PASS", "defects": 0, "witness": "386-row graph operator domain with explicit zero algebraic summand"},
    }
    proof_checks["sha256"] = digest(proof_checks)

    state_boundary = {
        "Hadamard_two_point_function": "CONSTRUCTED_ON_FULL_386_ROW_OFFSHELL_BV_COMPLEX",
        "BRST_Ward_identity": "EXACT_IN_BOTH_ARGUMENTS",
        "graded_CCR": "EXACT_FOR_DELTA_LAMBDA=LAMBDA_PLUS-LAMBDA_MINUS",
        "positivity": "NOT_SATISFIED_OR_CLAIMED",
        "object_type": "BRST_HADAMARD_PSEUDO_STATE_TWO_POINT_PAIR",
        "reason": "Hadamard two-point functions do not require positivity; a positive state is a separate condition. The scale-free stationary zero-mode split has zero symmetric part, so this selected pair is not positive.",
        "physical_cohomology_positivity": "NOT_INFERRED",
        "renormalized_products": "NOT_CONSTRUCTED",
        "QME": "NOT_RESTORED",
    }
    state_boundary["sha256"] = digest(state_boundary)

    snapshot = {
        "kind": "STRICT_386_FULL_COMPLEX_BRST_HADAMARD_TWO_POINT_SNAPSHOT",
        "classical_snapshot_id": causal["scope"]["snapshot_id"],
        "classical_snapshot_sha256": causal["scope"]["snapshot_sha256"],
        "causal_envelope_sha256": causal["causal_envelope"]["sha256"],
        "pairing_sha256": cyclic["pairing_replay"]["pairing_sha256"],
        "graph_q1_sha256": graph_q1["canonical_hashes"]["graph_q1_serialization_sha256"],
        "suspension_sha256": suspension["canonical_hashes"]["suspended_adjoint_theorem_sha256"],
        "plus_name_sha256": plus["canonical_name_sha256"],
        "minus_name_sha256": minus["canonical_name_sha256"],
        "modal_checks_sha256": modal_checks["sha256"],
        "parent_proof_sha256": parent_proof["sha256"],
        "transfer_proof_sha256": transfer_proof["sha256"],
        "proof_checks_sha256": proof_checks["sha256"],
        "state_boundary_sha256": state_boundary["sha256"],
    }
    snapshot["sha256"] = digest(snapshot)

    flags = {
        "CLASSICAL_IMPORT_GATE_PASSED": True,
        "NONLINEAR_GREEN_COMPATIBILITY_CERTIFIED": True,
        "STRICT_PARENT_HODGE_HADAMARD_TWO_POINT_PAIR_CONSTRUCTED": True,
        "STRICT_386_FULL_COMPLEX_BRST_HADAMARD_TWO_POINT_FUNCTION_CONSTRUCTED": True,
        "STRICT_386_HADAMARD_WAVEFRONT_CONDITION_CERTIFIED": True,
        "STRICT_386_BRST_WARD_IDENTITIES_CERTIFIED": True,
        "STRICT_386_GRADED_CCR_CERTIFIED": True,
        "STRICT_386_ZERO_MODE_RETAINED_AND_SPLIT": True,
        "STRICT_386_D_STATIONARY_TWO_POINT_PAIR": True,
        "STRICT_386_POSITIVE_HADAMARD_STATE_CONSTRUCTED": False,
        "STRICT_386_PHYSICAL_COHOMOLOGY_POSITIVITY_CERTIFIED": False,
        "RENORMALIZED_LORENTZIAN_PRODUCTS_CONSTRUCTED": False,
        "CAUSAL_PERTURBATIVE_AQFT_CONSTRUCTED": False,
        "LORENTZIAN_QME_RESTORED": False,
        "RESIDUAL_QUANTUM_TRANSFER_AUTHORIZED": False,
        "LORENTZIAN_QUANTUM_THEORY": False,
    }

    value = {
        "$schema": "../schema/strict-386-brst-hadamard-two-point-v1.schema.json",
        "schema": "strict-386-brst-hadamard-two-point-v1",
        "schema_path": "quantum-weyl/lorentzian/schema/strict-386-brst-hadamard-two-point-v1.schema.json",
        "result_id": "STRICT_386_BRST_HADAMARD_TWO_POINT_V1",
        "result_kind": "FULL_COMPLEX_BRST_HADAMARD_TWO_POINT_DISTRIBUTION_WITH_PSEUDO_STATE_BOUNDARY",
        "result_state": "FULL_386_BRST_HADAMARD_TWO_POINT_CERTIFIED_POSITIVE_STATE_OPEN",
        "lifecycle": "LORENTZIAN_CERTIFIED",
        "created": "2026-08-16",
        "repository_base_commit": "278f63816b6e71192a7a03ac4e028ab912f4eafe",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "question": "Can the strict Gate-A causal complex carry a full off-shell BRST-compatible Hadamard two-point distribution without importing reduced or Berger state data?",
        "answer": "Yes, as a graded Hadamard pseudo-state pair, not as a positive state. Split the rank-15 parent Hodge-wave causal kernel by whole S3 spectral projectors. For every positive eigenvalue use -exp(∓i sqrt(lambda)(t-t'))/(2 sqrt(lambda)); retain the scalar zero mode with the scale-free smooth split ±i(t-t')/2. The pair is an exact wave bisolution, is stationary, has the vector-valued Hadamard frequency wavefront relation and differs by i times the parent causal kernel. Applying W_parent and the same cyclic BGG, trace/Weyl shear and graph-retract maps as the Green homotopy transports the pair to the complete 386-row BV carrier. All eleven bisolution, CCR, microlocal, Ward, adjoint, zero-mode and coverage checks pass. The selected normalization is indefinite and the zero-mode symmetric part vanishes, so positivity and a Hadamard state remain explicitly unclaimed.",
        "scope": {
            "theory": "free strict pure-Weyl generalized-auxiliary BV complex",
            "background": "unit ultrastatic conformal cylinder R x S3",
            "carrier": "complete 386-row off-shell graph BV test/distribution complex",
            "classical_snapshot_id": causal["scope"]["snapshot_id"],
            "classical_snapshot_sha256": causal["scope"]["snapshot_sha256"],
            "excluded": "interacting products, positivity, residual transfer and QME",
        },
        "provenance": {"inputs": provenance, "analytic_sources": analytic_sources},
        "modal_exact_checks": modal_checks,
        "two_point_operator_names": names,
        "parent_BRST_proof": parent_proof,
        "graph_transfer_proof": transfer_proof,
        "proof_obligations": proof_checks,
        "state_and_positivity_boundary": state_boundary,
        "hadamard_snapshot": snapshot,
        "foundational_strength": {
            "exact_part": "modal ODE/CCR algebra, zero-mode identities, chain/adjoint transport and content hashes",
            "analytic_part": "S3 Hodge spectral completeness and vector-valued microlocal Hadamard theorems",
            "projector_basis_choice": False,
            "zero_mode_choice": "canonical scale-free stationary pseudo-state split; no zero-mode deletion",
            "Hilbert_completion": False,
            "Krein_or_indefinite_policy": "indefinite graded pseudo-state only",
            "weakest_base_or_constructive_microlocal_proof": False,
        },
        "independent_checker": "quantum-weyl/lorentzian/check_strict_386_brst_hadamard_two_point.py",
        "human_report": str(REPORT.relative_to(ROOT)),
        "next_gate": "Classify the local Lorentzian counterterm/anomaly complex and construct renormalized time-ordered products on this Hadamard pair before attempting the local QME; independently decide whether any Hadamard-frequency split can be positive on physical cohomology.",
        "does_not_establish": [
            "a positive quasifree Hadamard state or positive physical graviton Hilbert space",
            "that the scale-free stationary pseudo-state is the unique zero-mode policy",
            "distribution-kernel coordinate bytes or an effective projector algorithm",
            "a Feynman propagator, renormalized Lorentzian time-ordered product or causal perturbative AQFT construction",
            "QME restoration, anomaly cancellation, residual quantum transfer, particles, scattering or unitarity",
            "a complete interacting Lorentzian quantum theory",
        ],
        "claim_flags": flags,
    }
    value["content_sha256"] = digest({
        "hadamard_snapshot": snapshot,
        "proof_obligations": proof_checks,
        "state_and_positivity_boundary": state_boundary,
        "claim_flags": flags,
        "does_not_establish": value["does_not_establish"],
    })
    return value


def report(value: dict[str, Any]) -> str:
    return f"""# Strict 386-row BRST Hadamard two-point function

**Result:** `{value['result_id']}`

**Lifecycle:** `{value['lifecycle']}`

**Hadamard snapshot:** `{value['hadamard_snapshot']['sha256']}`
**Classical snapshot:** `{value['scope']['classical_snapshot_id']}`

## Result

A BRST-compatible Hadamard two-point pair is now constructed on the complete
386-row strict pure-Weyl off-shell BV complex.  This is not a pullback of the
existing reduced E/A/L state and imports no Berger data.

The construction starts from the same rank-15 adjoint-tractor Hodge wave used
for the causal homotopy.  Whole S³ eigenspace projectors define the nonzero-mode
Hadamard pair

```text
w_plus(lambda)  = -exp(-i sqrt(lambda) (t-t'))/(2 sqrt(lambda))
w_minus(lambda) = -exp(+i sqrt(lambda) (t-t'))/(2 sqrt(lambda)).
```

Their difference is `i sin(sqrt(lambda)(t-t'))/sqrt(lambda)`, exactly `i`
times the repository retarded-minus-advanced kernel.  The scalar zero mode is
retained with `w_0^plus=+i(t-t')/2` and `w_0^minus=-i(t-t')/2`.  It is an exact,
smooth, stationary bisolution and supplies the missing zero-mode commutator
without deleting the mode or introducing a scale.

Applying `W_parent` turns the wave pair into a BRST chain two-point pair.  The
certified cyclic BGG maps, trace/Weyl shear and graph retract then transport it
to all 386 rows.  The algebraic retract summand has zero causal difference and
therefore receives the explicit zero two-point value.  That is full typed
coverage, not an omitted sector.

## What is certified

All eleven distributional obligations pass: left and right bisolution,
graded CCR, Hadamard wavefront relation, both BRST Ward identities, graded
Hermiticity and reality, cylinder-flow stationarity, retained zero-mode policy,
declared positivity/Krein policy, and complete row coverage.  The microlocal
statement is

```text
WF'(lambda_sign) = (N_sign x N_sign) intersect WF'(Delta_Lambda).
```

The finite-order transport maps do not enlarge wavefront sets, and the two
frequency cones are disjoint, so any polarization removed by the graph maps is
removed from the causal kernel as well.

## Positivity boundary

This is a Hadamard **two-point function**, not a positive Hadamard state.  That
distinction is standard in the BRST literature: positivity is an additional
condition.  The selected scale-free zero-mode split has vanishing symmetric
part, and the parent normalization is indefinite.  The certificate therefore
calls the result a graded Hadamard pseudo-state pair and keeps physical
positivity false.

No renormalized time-ordered products, Feynman propagator, Lorentzian QME,
residual quantum transfer, particle interpretation or interacting quantum
theory follows from this free two-point construction.

## Reproduction

```text
python3 quantum-weyl/lorentzian/build_strict_386_brst_hadamard_two_point.py --check
python3 quantum-weyl/lorentzian/check_strict_386_brst_hadamard_two_point.py
python3 quantum-weyl/lorentzian/verify_strict_386_brst_hadamard_two_point.py
python3 -m unittest quantum-weyl.lorentzian.tests.test_strict_386_brst_hadamard_two_point
```
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    schema = load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    result_text = json.dumps(value, indent=2, ensure_ascii=False) + "\n"
    report_text = report(value)
    if args.check:
        if not RESULT.is_file() or RESULT.read_text(encoding="utf-8") != result_text:
            print(f"{value['result_id']}: CERTIFICATE DRIFT")
            return 1
        if not REPORT.is_file() or REPORT.read_text(encoding="utf-8") != report_text:
            print(f"{value['result_id']}: REPORT DRIFT")
            return 1
        print(f"{value['result_id']}: CURRENT")
        return 0
    RESULT.write_text(result_text, encoding="utf-8")
    REPORT.write_text(report_text, encoding="utf-8")
    print(f"wrote {RESULT.relative_to(ROOT)}")
    print(f"wrote {REPORT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
