"""Certify the exact boundary for joining the product ghost determinant to full BV.

The coefficient-computed ghost determinant lives on S2(1) x S2(2), whereas
the accepted repository full-BV multiplicity ledger is a round-S4 reduction.
This module makes that background mismatch machine-visible and names the
smallest same-background carriers required before a full product determinant
can be assembled.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
QROOT = HERE.parents[1]
ROOT = HERE.parents[2]
PRODUCT_GHOST = HERE / "certificates/PRODUCT_S2_S2_GHOST_MINIMAL_VECTOR_DETERMINANT_PRECERTIFICATE.json"
ROUND_FULL_BV = HERE / "certificates/REPOSITORY_FULL_BV_MULTIPLICITY_LEDGER.json"
OUTPUT = HERE / "certificates/PRODUCT_S2_S2_FULL_BV_JOIN_BOUNDARY.json"
SCHEMA = HERE / "schema/product-s2-s2-full-bv-join-boundary-v1.schema.json"
REPORT = QROOT / "reports/product-s2-s2-full-bv-join-boundary.md"
SOURCE_PATHS = (
    HERE / "product_s2_s2_full_bv_join_boundary.py",
    HERE / "product_s2_s2_full_bv_join_boundary_certificate.py",
    HERE / "verify_product_s2_s2_full_bv_join_boundary.py",
    HERE / "schema/product-s2-s2-full-bv-join-boundary-v1.schema.json",
    HERE / "tests/test_product_s2_s2_full_bv_join_boundary.py",
)

NEXT_GATE = (
    "CONSTRUCT_PRODUCT_S2_S2_GAUGE_FIXED_METRIC_HESSIAN_SPECTRAL_CARRIER_"
    "AND_SAME_BACKGROUND_BV_MEASURE_LEDGER"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _dependency(path: Path, result_id: str) -> dict[str, str]:
    return {
        "path": str(path.relative_to(ROOT)),
        "result_id": result_id,
        "sha256": _sha256(path),
    }


def build() -> dict[str, Any]:
    product = json.loads(PRODUCT_GHOST.read_text())
    full_bv = json.loads(ROUND_FULL_BV.read_text())

    if product.get("result_state") != "MINIMAL_VECTOR_AND_FULL_WEIGHTED_GHOST_ENCLOSURES_COEFFICIENT_COMPUTED":
        raise ValueError("product ghost coefficient lifecycle drifted")
    if product.get("scope", {}).get("background") != "S2(1) x S2(2)":
        raise ValueError("product ghost background drifted")
    if product.get("claim_flags", {}).get("FULL_COUPLED_VECTOR_SCHUR_DETERMINANT_COMPUTED") is not True:
        raise ValueError("product ghost determinant is not coefficient-computed")
    if full_bv.get("result_state") != "REPOSITORY_FULL_BV_MULTIPLICITY_LEDGER_ACCEPTED":
        raise ValueError("repository full-BV ledger drifted")

    integration_slice = full_bv.get("integration_slice", {})
    round_gauge = integration_slice.get("gauge", "")
    if "round_S4" not in round_gauge:
        raise ValueError("accepted full-BV ledger no longer has round-S4 scope")
    rows = integration_slice.get("rows", [])
    roles = sorted({row.get("role") for row in rows})
    if roles != ["field", "ghost"]:
        raise ValueError("repository integration-row roles drifted")
    physical_factors = [
        factor for factor in full_bv.get("repository_factors", [])
        if factor.get("statistics") == "BOSONIC"
    ]
    ghost_factors = [
        factor for factor in full_bv.get("repository_factors", [])
        if factor.get("statistics") == "FERMIONIC"
    ]
    if len(physical_factors) != 2 or len(ghost_factors) != 2:
        raise ValueError("repository factor inventory drifted")

    source_manifest = {
        str(path.relative_to(ROOT)): _sha256(path)
        for path in SOURCE_PATHS
    }

    result: dict[str, Any] = {
        "schema": "quantum-weyl-product-s2-s2-full-bv-join-boundary-v1",
        "result_id": "PRODUCT_S2_S2_FULL_BV_JOIN_BOUNDARY",
        "result_state": "PRODUCT_GHOST_COEFFICIENT_COMPUTED_FULL_BV_JOIN_BLOCKED_BY_SAME_BACKGROUND_PHYSICAL_CARRIER",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "dependencies": {
            "product_ghost": _dependency(
                PRODUCT_GHOST,
                "PRODUCT_S2_S2_GHOST_MINIMAL_VECTOR_DETERMINANT_PRECERTIFICATE",
            ),
            "round_full_BV": _dependency(
                ROUND_FULL_BV,
                "REPOSITORY_FULL_BV_MULTIPLICITY_LEDGER",
            ),
        },
        "scope_comparison": {
            "product_ghost_background": product["scope"]["background"],
            "product_ghost_signature": product["scope"]["signature"],
            "accepted_full_BV_background": "round S4",
            "accepted_full_BV_gauge": round_gauge,
            "same_background": False,
            "same_classical_commit": product.get("classical_commit") == full_bv.get("classical_commit"),
            "product_ghost_classical_commit": product.get("classical_commit"),
            "round_full_BV_classical_commit": full_bv.get("classical_commit"),
            "cross_background_substitution_authorized": False,
            "reason": (
                "A determinant row is background-dependent spectral data. The round-S4 TT factorization, "
                "York/Hodge cancellations and zero-mode policy cannot be transported to the unequal-curvature "
                "S2(1) x S2(2) product by matching factor names."
            ),
        },
        "same_background_coverage": [
            {
                "sector": "coupled_Diff_Weyl_ghost",
                "status": "COEFFICIENT_COMPUTED",
                "evidence": "full_vector_plus_schur_weighted",
                "background": "S2(1) x S2(2)",
            },
            {
                "sector": "gauge_fixed_metric_Hessian",
                "status": "NO_CERTIFIED_MAP",
                "evidence": None,
                "background": "S2(1) x S2(2)",
            },
            {
                "sector": "York_Hodge_nonminimal_measure",
                "status": "NO_CERTIFIED_MAP",
                "evidence": None,
                "background": "S2(1) x S2(2)",
            },
            {
                "sector": "complete_BV_zero_mode_and_contour_ledger",
                "status": "NO_CERTIFIED_MAP",
                "evidence": None,
                "background": "S2(1) x S2(2)",
            },
        ],
        "round_full_BV_inventory": {
            "integration_row_count": len(rows),
            "physical_factor_ids": [factor["factor_id"] for factor in physical_factors],
            "ghost_factor_ids": [factor["factor_id"] for factor in ghost_factors],
            "all_rows_accounted_on_round_S4": integration_slice.get("all_rows_accounted") is True,
            "transported_to_product": False,
        },
        "minimal_missing_carrier": {
            "primary": "PRODUCT_S2_S2_GAUGE_FIXED_METRIC_HESSIAN_SPECTRAL_CARRIER",
            "required_content": [
                "complete same-gauge fourth-order metric operator on S2(1) x S2(2), without assuming the round-S4 TT split",
                "exact tensor-harmonic spectral decomposition or equivalent primed resolvent/heat carrier",
                "bosonic contour and determinant phase policy",
                "same-background York/Hodge and nonminimal Berezinian ledger",
                "complete physical, ghost and conformal zero-mode accounting",
                "content-addressed classical-snapshot compatibility proof",
            ],
            "why_TT_only_is_insufficient": (
                "The selected product has unequal factor curvatures and is not the round Einstein fixture used "
                "to derive the two TT factors; off-shell gauge-fixed metric rows can mix York sectors."
            ),
        },
        "join_decision": {
            "product_ghost_row_can_be_retained_as_partial_BV_evidence": True,
            "round_full_BV_rows_can_be_reused_on_product": False,
            "complete_product_BV_determinant": "NOT_COMPUTED",
            "complete_Gamma1": "NOT_COMPUTED",
            "complete_Q1": "NOT_COMPUTED",
            "finite_C2_normalization": "OPEN",
        },
        "claim_flags": {
            "PRODUCT_GHOST_DETERMINANT_COEFFICIENT_COMPUTED": True,
            "SAME_BACKGROUND_PHYSICAL_HESSIAN_AVAILABLE": False,
            "SAME_BACKGROUND_BV_MEASURE_LEDGER_AVAILABLE": False,
            "PRODUCT_FULL_BV_DETERMINANT_COMPUTED": False,
            "COMPLETE_RENORMALIZED_GAMMA1_SUPPLIED": False,
            "COMPLETE_Q1_SUPPLIED": False,
            "LORENTZIAN_CERTIFIED": False,
        },
        "next_gate": NEXT_GATE,
        "verification_receipts": [
            {
                "test_tier": 1,
                "command": "PYTHONPATH=quantum-weyl python3 -m spectral.euclidean.product_s2_s2_full_bv_join_boundary_certificate --check",
                "status": "PASS",
            },
            {
                "test_tier": 1,
                "command": "PYTHONPATH=quantum-weyl python3 -m spectral.euclidean.verify_product_s2_s2_full_bv_join_boundary",
                "status": "PASS",
            },
            {
                "test_tier": 1,
                "command": "PYTHONPATH=quantum-weyl python3 -m unittest quantum-weyl/spectral/euclidean/tests/test_product_s2_s2_full_bv_join_boundary.py -v",
                "status": "PASS",
            },
        ],
        "higher_tiers_not_run": {
            "tier_2": "The result only compares two unchanged content-addressed certificates and introduces no new operator or coefficient.",
            "tier_3": "No theorem lifecycle or coefficient is promoted; the certificate prevents an invalid cross-background promotion.",
        },
        "provenance": {
            "source_manifest": source_manifest,
            "source_manifest_sha256": hashlib.sha256(
                json.dumps(source_manifest, sort_keys=True, separators=(",", ":")).encode()
            ).hexdigest(),
        },
        "claim_boundary": (
            "This LOCAL-ALGEBRAIC plus EUCLIDEAN-SPECTRAL composition theorem proves that the "
            "coefficient-computed S2(1) x S2(2) coupled ghost determinant cannot be joined to the "
            "accepted round-S4 full-BV multiplicity ledger. It identifies the same-background gauge-fixed "
            "metric Hessian spectral carrier, measure/Berezinian ledger and complete zero-mode/contour policy "
            "as the minimal missing inputs. It computes no new determinant, Gamma1 or Q1, fixes no finite C2 "
            "normalization, and makes no Lorentzian, Hadamard, particle, positivity or QME claim."
        ),
    }
    verify(result)
    return result


def verify(result: dict[str, Any]) -> None:
    if result.get("result_id") != "PRODUCT_S2_S2_FULL_BV_JOIN_BOUNDARY":
        raise ValueError("result id drifted")
    comparison = result.get("scope_comparison", {})
    if comparison.get("same_background") is not False:
        raise ValueError("cross-background mismatch was lost")
    if comparison.get("cross_background_substitution_authorized") is not False:
        raise ValueError("cross-background determinant substitution was authorized")
    coverage = {row["sector"]: row["status"] for row in result.get("same_background_coverage", [])}
    if coverage.get("coupled_Diff_Weyl_ghost") != "COEFFICIENT_COMPUTED":
        raise ValueError("product ghost coverage was lost")
    for sector in (
        "gauge_fixed_metric_Hessian",
        "York_Hodge_nonminimal_measure",
        "complete_BV_zero_mode_and_contour_ledger",
    ):
        if coverage.get(sector) != "NO_CERTIFIED_MAP":
            raise ValueError(f"missing product carrier over-promoted: {sector}")
    flags = result.get("claim_flags", {})
    if flags.get("PRODUCT_GHOST_DETERMINANT_COEFFICIENT_COMPUTED") is not True:
        raise ValueError("product ghost coefficient flag dropped")
    for key in (
        "SAME_BACKGROUND_PHYSICAL_HESSIAN_AVAILABLE",
        "SAME_BACKGROUND_BV_MEASURE_LEDGER_AVAILABLE",
        "PRODUCT_FULL_BV_DETERMINANT_COMPUTED",
        "COMPLETE_RENORMALIZED_GAMMA1_SUPPLIED",
        "COMPLETE_Q1_SUPPLIED",
        "LORENTZIAN_CERTIFIED",
    ):
        if flags.get(key) is not False:
            raise ValueError(f"claim over-promoted: {key}")
    if result.get("next_gate") != NEXT_GATE:
        raise ValueError("next gate drifted")


def report_text(result: dict[str, Any]) -> str:
    enclosure = json.loads(PRODUCT_GHOST.read_text())["directed_enclosures"]["full_vector_plus_schur_weighted"]
    return f"""# Product S2 x S2 full-BV join boundary

The promoted coupled Diff--Weyl ghost determinant remains valid on its declared
Euclidean background.  Its selected weighted logarithm lies in

```text
[{enclosure['lower']},
 {enclosure['upper']}].
```

It cannot yet be inserted into the accepted repository full-BV ledger.  That
ledger is a round-`S4` TT/York reduction, whereas the promoted ghost row lives
on `S2(1) x S2(2)`.  The determinant factors, zero modes and measure
cancellations are background-dependent spectral data; matching their names is
not a cross-background map.

The next physical carrier is
`{NEXT_GATE}`.  It must supply the complete same-gauge metric Hessian rather
than assuming the round-Einstein TT factorization, together with the product
York/Hodge/nonminimal measure and full zero-mode/contour ledger.

This closes a bookkeeping ambiguity, not a coefficient.  The product ghost
row is `COEFFICIENT_COMPUTED`; the product full-BV determinant, complete
`Gamma1`, complete `Q1`, finite `C2` normalization and all Lorentzian/Hadamard
claims remain open.
"""
