#!/usr/bin/env python3
"""Generate the content-addressed claim map for Paper 22."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = ROOT / "paper/22-bateman-turok-euclidean-torus-collapse.tex"
PDF = ROOT / "paper/22-bateman-turok-euclidean-torus-collapse.pdf"
OUTPUT = ROOT / "paper/22-bateman-turok-euclidean-torus-collapse-claim-map.json"
PREFIX = "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_"
AUTHORITIES = [
    PREFIX + "POLYNOMIAL_CONTRAST_HIERARCHY_OBSTRUCTION_V1.json",
    PREFIX + "TORUS_PHASE_PULLBACK_OBSTRUCTION_V1.json",
    PREFIX + "TENSOR_PHASE_HIERARCHY_OBSTRUCTION_V1.json",
    PREFIX + "TORUS_SPARSE_MAXIMA_FLOW_V1.json",
    PREFIX + "TORUS_TOP_BAND_FLOW_V1.json",
    PREFIX + "TORUS_DYADIC_STOPPING_FLOW_V1.json",
    PREFIX + "TORUS_EXTENSIVE_ACTION_GRADIENT_FLOOR_V1.json",
    PREFIX + "TORUS_SHARP_VIRIAL_DENSITY_GATE_V1.json",
    PREFIX + "TORUS_GLOBAL_VIRIAL_COMPATIBILITY_V1.json",
    PREFIX + "TORUS_QUADRATIC_VIRIAL_DENSITY_GATE_V1.json",
    PREFIX + "TORUS_RECIPROCAL_VIRIAL_LOCALIZATION_V1.json",
    PREFIX + "TORUS_CURVATURE_CUT_CONCENTRATION_V1.json",
    PREFIX + "TORUS_SMALL_ACTION_GRADIENT_FLOOR_V1.json",
    PREFIX + "TORUS_GREEN_TAIL_COUNTERFAMILY_V1.json",
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> dict:
    authorities = []
    for index, relative in enumerate(AUTHORITIES, start=83):
        path = ROOT / relative
        payload = json.loads(path.read_text())
        if payload.get("checks", {}).get("ok") is not True:
            raise ValueError(f"authority is not certified: {relative}")
        authorities.append(
            {
                "rf_number": index,
                "path": relative,
                "certificate": payload["certificate"],
                "sha256": sha256(path),
                "dependency_tags": payload["dependency_tags"],
                "does_not_establish": payload["does_not_establish"],
            }
        )

    final = json.loads((ROOT / AUTHORITIES[-1]).read_text())
    if final["research_disposition"]["all_field_torus_scaled_PL"] != "REFUTED":
        raise ValueError("final all-field disposition drifted")
    if final["research_disposition"]["complete_residual_gradient_free_scale_collapse"] != "PROVED":
        raise ValueError("final collapse disposition drifted")
    if final["dependency_tags"] != ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"]:
        raise ValueError("final dependency boundary drifted")
    if final["checks"]["passed"] != 9 or final["checks"]["total"] != 9:
        raise ValueError("final exact check count drifted")

    return {
        "schema": "paper-22-bateman-turok-torus-claim-map-v1",
        "result_id": "PAPER_22_BT_EUCLIDEAN_TORUS_COLLAPSE_DRAFT",
        "result_state": "DRAFT_WITH_CERTIFIED_ALL_FIELD_COUNTERFAMILY",
        "lifecycle_state": "WRITING_STARTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "headline_claim": (
            "The deterministic all-field BT torus scaled PL inequality is false: "
            "an explicit positive nonseparable polynomial-contrast family has "
            "positive bounded action and Q_n/omega_Ln^2 tending to zero."
        ),
        "manuscript": str(MANUSCRIPT.relative_to(ROOT)),
        "manuscript_sha256": sha256(MANUSCRIPT),
        "compiled_pdf": str(PDF.relative_to(ROOT)),
        "compiled_pdf_sha256": sha256(PDF),
        "authority_count": len(authorities),
        "authorities": authorities,
        "final_theorem": {
            "certificate": final["certificate"],
            "lifecycle_state": final["lifecycle_state"],
            "answer": final["answer"],
            "power_balance": final["power_balance"],
            "action_and_contrast": final["action_and_contrast"],
            "research_disposition": final["research_disposition"],
            "does_not_establish": final["does_not_establish"],
        },
        "claim_flags": {
            "ALL_FIELD_TORUS_SCALED_PL_REFUTED": True,
            "POSITIVE_ACTION_NONSEPARABLE_COUNTERFAMILY_CONSTRUCTED": True,
            "FULL_WITTEN_QUOTIENT_DECIDED": False,
            "GIBBS_TYPICALITY_ESTABLISHED": False,
            "INTERACTING_H_MINUS_ONE_FAILURE_ESTABLISHED": False,
            "CONTINUUM_RECONSTRUCTION_DECIDED": False,
            "BORN_OR_KREIN_RECONSTRUCTION_ESTABLISHED": False,
            "LORENTZIAN_CAUSAL_CLAIM": False,
        },
        "verification": {
            "producer": "python3 paper/generate_22_bateman_turok_torus_claim_map.py --check",
            "independent": "python3 paper/verify_22_bateman_turok_torus_claim_map.py",
            "affected_chain": "python3 -m unittest discover -s reverse_physics/tests -p 'test_bt_euclidean_torus_*.py'",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = json.dumps(build(), indent=2, sort_keys=True) + "\n"
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text() != rendered:
            raise SystemExit("Paper 22 claim map is stale")
        print("Paper 22 claim map: PASS")
    else:
        OUTPUT.write_text(rendered)
        print(f"wrote {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
