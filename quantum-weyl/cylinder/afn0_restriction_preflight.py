"""Exact AFN0 local-to-cylinder restriction preflight.

This module proves the background/order and parity facts that do not require
the still-missing frozen ``pi_cl`` and centered representative vectors.  It
does not emit a local-to-residual cohomology map.
"""

from __future__ import annotations

import hashlib
import json
from functools import lru_cache
from pathlib import Path

import sympy as sp

from bridge.cylinder_harmonics.linearized_geometry import (
    DIMENSION,
    INDICES,
    LinearizedCylinderGeometry,
    canonical,
    tensor_get,
)


PACKAGE_ROOT = Path(__file__).resolve().parent
REPOSITORY_ROOT = PACKAGE_ROOT.parents[1]

H04_CERTIFICATE = (
    "quantum-weyl/local_bv/certificates/AFN0_H04_CANONICAL_QUOTIENT.json"
)
PREIMAGE_CERTIFICATE = "bridge/certificates/cylinder_metric_preimages.json"
METRIC_TO_RESIDUAL = "bridge/certificates/metric_to_residual.json"
COMPLETED_H4 = "analytic_completion/certificates/completed_H4.json"


def _sha256(relative_path: str) -> str:
    return hashlib.sha256((REPOSITORY_ROOT / relative_path).read_bytes()).hexdigest()


def _load(relative_path: str) -> dict[str, object]:
    payload = json.loads((REPOSITORY_ROOT / relative_path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"cylinder input is not an object: {relative_path}")
    return payload


def _background_weyl(geometry: LinearizedCylinderGeometry) -> dict[tuple[int, ...], sp.Expr]:
    metric = geometry.metric
    ricci = geometry.ricci
    scalar = geometry.scalar_curvature
    output: dict[tuple[int, ...], sp.Expr] = {}
    for a in INDICES:
        for b in INDICES:
            for c in INDICES:
                for d in INDICES:
                    riemann_lower = sum(
                        metric[a, upper]
                        * tensor_get(geometry.riemann_mixed, upper, b, c, d)
                        for upper in INDICES
                    )
                    value = riemann_lower
                    value -= (
                        metric[a, c] * ricci[d, b]
                        - metric[a, d] * ricci[c, b]
                        - metric[b, c] * ricci[d, a]
                        + metric[b, d] * ricci[c, a]
                    ) / 2
                    value += scalar * (
                        metric[a, c] * metric[d, b]
                        - metric[a, d] * metric[c, b]
                    ) / 6
                    value = canonical(value)
                    if value != 0:
                        output[a, b, c, d] = value
    return output


def _background_curvature_audit(
    geometry: LinearizedCylinderGeometry,
) -> dict[str, object]:
    metric = geometry.metric
    for a in INDICES:
        for b in INDICES:
            expected_ricci = 0 if 0 in (a, b) else 2 * metric[a, b]
            if canonical(geometry.ricci[a, b] - expected_ricci) != 0:
                raise AssertionError("R x S3 Ricci product identity failed")
            for c in INDICES:
                for d in INDICES:
                    riemann_lower = canonical(
                        sum(
                            metric[a, upper]
                            * tensor_get(
                                geometry.riemann_mixed, upper, b, c, d
                            )
                            for upper in INDICES
                        )
                    )
                    expected_riemann = (
                        0
                        if 0 in (a, b, c, d)
                        else metric[a, c] * metric[b, d]
                        - metric[a, d] * metric[b, c]
                    )
                    if canonical(riemann_lower - expected_riemann) != 0:
                        raise AssertionError("R x S3 constant-curvature identity failed")
    ricci_squared = canonical(
        sum(
            geometry.inverse[a, c]
            * geometry.inverse[b, d]
            * geometry.ricci[a, b]
            * geometry.ricci[c, d]
            for a in INDICES
            for b in INDICES
            for c in INDICES
            for d in INDICES
        )
    )
    riemann_squared = sp.Integer(12)
    euler = canonical(
        riemann_squared - 4 * ricci_squared + geometry.scalar_curvature**2
    )
    if (riemann_squared, ricci_squared, geometry.scalar_curvature, euler) != (
        12,
        12,
        6,
        0,
    ):
        raise AssertionError("R x S3 curvature invariant normalization drifted")
    return {
        "riemann_product_identity": "R_ijkl=g_ik g_jl-g_il g_jk; time components zero",
        "ricci_product_identity": "Ric_ij=2 g_ij; time components zero",
        "riemann_squared": int(riemann_squared),
        "ricci_squared": int(ricci_squared),
        "scalar_curvature": int(geometry.scalar_curvature),
        "euler_density": int(euler),
    }


@lru_cache(maxsize=1)
def afn0_restriction_preflight() -> dict[str, object]:
    h04 = _load(H04_CERTIFICATE)
    preimages = _load(PREIMAGE_CERTIFICATE)
    metric_to_residual = _load(METRIC_TO_RESIDUAL)
    completed_h4 = _load(COMPLETED_H4)
    if h04["result_state"] != "COMPLETE_AFN0_COVARIANT_COUNTERTERM_CANDIDATE_QUOTIENT":
        raise ValueError("H04 input is not the complete covariant AFN0 candidate quotient")
    if preimages["right_inverse_identity"] != "C1 R_n=id on E/A/L curvature image blocks":
        raise ValueError("cylinder C1 right-inverse identity drifted")
    if preimages["parity_completion"]["orientation"] != -1:
        raise ValueError("cylinder parity orientation drifted")
    two_particle = metric_to_residual["two_particle"]
    if two_particle["h4"] != 2 or two_particle["parity"] != [-1, 1]:
        raise ValueError("two-particle residual parity ledger drifted")
    centered = completed_h4["centered"]
    if centered["classes"] != ["W_+^2", "W_-^2"] or centered[
        "normalized_gram"
    ] != [[1, 0], [0, 1]]:
        raise ValueError("centered H4 evidence drifted")

    geometry = LinearizedCylinderGeometry()
    background_weyl = _background_weyl(geometry)
    curvature_audit = _background_curvature_audit(geometry)
    if background_weyl:
        raise AssertionError("Einstein cylinder background is not conformally flat")
    if geometry.scalar_curvature != 6:
        raise AssertionError("Einstein cylinder scalar curvature convention drifted")

    local_classes = {
        row["representative_id"]: row
        for sector in (h04["even_sector"], h04["odd_sector"])
        for row in sector["classes"]
    }
    if set(local_classes) != {"CT_C2", "CT_E4", "CT_C_DUAL_C"}:
        raise ValueError("H04 local class basis drifted")

    # Since C(gbar)=0, differentiating either quadratic Weyl density once
    # gives zero and its Hessian is the polarization of the indicated C1
    # pairing.  This is an exact algebraic consequence, not a mode fit.
    expansion_ledger = {
        "CT_C2": {
            "order_h0": "ZERO_FROM_C_GBAR_ZERO",
            "order_h1": "ZERO_FROM_C_GBAR_ZERO",
            "order_h2": "C1(h)_abcd C1(k)^abcd",
            "parity": "even",
        },
        "CT_C_DUAL_C": {
            "order_h0": "ZERO_FROM_C_GBAR_ZERO",
            "order_h1": "ZERO_FROM_C_GBAR_ZERO",
            "order_h2": "C1(h)_abcd star_C1(k)^abcd",
            "parity": "odd",
        },
        "CT_E4": {
            "order_h0": "ZERO_ON_RxS3_BACKGROUND",
            "order_h1": "TOTAL_DERIVATIVE_VARIATION",
            "order_h2": "TOPOLOGICAL_TRANSGRESSION_REQUIRES_BOUNDARY_POLICY",
            "parity": "even_topological",
        },
    }
    parity_support = {
        "source_basis": ["CT_C2", "CT_C_DUAL_C"],
        "target_evidence_basis": ["e_even", "o_odd"],
        "support_matrix": [["ALLOWED_NONZERO", "ZERO_BY_PARITY"], ["ZERO_BY_PARITY", "ALLOWED_NONZERO"]],
        "e_even_definition": "(W_+^2+W_-^2)/sqrt(2)",
        "o_odd_definition": "(W_+^2-W_-^2)/sqrt(2)",
        "parity_geometry": "orientation_reversal_alpha_exchange_gamma",
        "normalization_matrix": None,
        "normalization_status": "UNDEFINED_PENDING_FROZEN_REPRESENTATIVE_VECTORS_AND_PI_CL",
    }
    blockers = {
        "portable_pi_cl": "MISSING_FROM_FROZEN_QUANTUM_CLASSICAL_IMPORT",
        "normalized_W_plus_squared_vector": "MISSING",
        "normalized_W_minus_squared_vector": "MISSING",
        "centered_H3_basis": "MISSING",
        "centered_H5_basis": "MISSING",
        "parity_Ward_identity": "NOT_COMPUTED",
        "Euler_boundary_policy": "NOT_FROZEN",
    }
    if any(
        value is None
        for row in parity_support["support_matrix"]
        for value in row
    ):
        raise AssertionError("parity support matrix is incomplete")
    source_hashes = {
        path: _sha256(path)
        for path in (
            H04_CERTIFICATE,
            PREIMAGE_CERTIFICATE,
            METRIC_TO_RESIDUAL,
            COMPLETED_H4,
        )
    }
    return {
        "result_id": "AFN0_CYLINDER_RESTRICTION_PREFLIGHT",
        "result_state": "STRUCTURAL_RESTRICTION_VERIFIED_PROJECTION_BLOCKED",
        "classical_commit": "UNFROZEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "scope_label": "AFN0_CYLINDER_PREFLIGHT_ONLY",
        "background": {
            "metric": "-dt^2+dOmega_3^2",
            "scalar_curvature": 6,
            "weyl_nonzero_component_count": len(background_weyl),
            "conformal_flatness": "VERIFIED_EXACTLY",
            "curvature_audit": curvature_audit,
        },
        "expansion_ledger": expansion_ledger,
        "curvature_pipeline": {
            "linearized_map": "C1",
            "right_inverse_identity": preimages["right_inverse_identity"],
            "families": ["E", "A", "L"],
            "chirality_hodge_eigenvalues": preimages["parity_completion"][
                "hodge_eigenvalues"
            ],
            "parity_completion": preimages["parity_completion"],
        },
        "parity_support": parity_support,
        "topological_and_exact_rows": {
            "CT_E4": "WITHHELD_PENDING_BOUNDARY_POLICY",
            "CT_BOX_R": "ZERO_IN_RELATIVE_QUOTIENT_BY_EXPLICIT_D_H_PRIMITIVE",
        },
        "residual_evidence": {
            "classes": centered["classes"],
            "normalized_gram": centered["normalized_gram"],
            "two_particle_parity": two_particle["parity"],
            "accepted_as_frozen_quantum_import": False,
        },
        "projection_blockers": blockers,
        "local_to_cylinder_map_status": "NOT_COMPUTED",
        "residual_projection_status": "BLOCKED_FAIL_CLOSED",
        "source_sha256": source_hashes,
        "claim_boundary": [
            "This certificate proves background order counting and parity support only.",
            "It does not define r_cyl on cohomology or apply pi_cl.",
            "Allowed-nonzero support entries are not normalized projection coefficients.",
            "It is AFN0 and does not include antifield completion, anomaly coefficients, QME restoration, or Lorentzian causal quantization.",
        ],
    }
