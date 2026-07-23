#!/usr/bin/env python3
"""Independent fail-closed verifier for the moving-lower preflight."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from .layout_reference import verify_layout_fixtures


SCHEMA = "phase3-axial-moving-lower-preflight-v1"
SOURCE_SCHEMA = "phase3-axial-moving-lower-source-v1"
GENERATOR = 7315
BASELINE_WIDTH = 621.8840812306481


class VerificationError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationError(message)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def verify_source(source: str, metadata: dict[str, Any]) -> bool:
    require(metadata.get("schema") == SOURCE_SCHEMA, "wrong source schema")
    require(metadata.get("generator") == GENERATOR, "wrong generator")
    require(metadata.get("omega_cell") == ["1/2", "129/256"], "wrong omega cell")
    require(metadata.get("frame_count") == 9, "wrong shared-frame count")
    require(
        metadata.get("formula") == "Ck1^-1*(L*Cc0+Uk*D0-D1*Wc)",
        "wrong moving-lower formula",
    )
    require(metadata.get("source_sha256") == digest(source.encode()), "source hash")
    required = (
        "fn ml_block_part(a:borrow IvAffineMat,kind:i64)->IvAffineMat",
        "fn ml_compose(left:borrow IvAffineMat,right:borrow IvAffineMat)",
        "let uc:IvAffineMat=ml_block_part(u,0);",
        "let uk:IvAffineMat=ml_block_part(u,1);",
        "let lower:IvAffineMat=ml_block_part(u,2);",
        "let lcc0:IvAffineResult=ivam_mul_checked(lower,cc0);",
        "let ukd0:IvAffineResult=ivam_mul_checked(uk,d0);",
        "let d1wc:IvAffineResult=ivam_mul_checked(d1,wc0.value);",
        "let wl0:IvAffineResult=ivam_solve_rect(ck1,rhs.value);",
        "moving=match(ml_compose(step,moving))",
        "ivam_rebase_dyadic(low0.value,128)",
        "let count:i64=4;",
        "ml_restrict_global(",
        "u.generator!=7315",
    )
    for witness in required:
        require(witness in source, f"missing witness: {witness}")
    require("fn sl_compose(" not in source, "superseded compose retained")
    require("fn sl_first_microfactor(" not in source, "superseded main retained")
    require(
        "let uc:IvAffineMat=gc_affine_submatrix(u,0);" not in source,
        "interleaved extractor applied to contiguous transition",
    )
    require(
        "let lower:IvAffineMat=gc_affine_submatrix(u,2);" not in source,
        "interleaved lower extractor applied to contiguous transition",
    )
    require(verify_layout_fixtures(), "exact layout oracle failed")
    return True


def verify_certificate(
    certificate: dict[str, Any],
    source: str,
    metadata: dict[str, Any],
    metadata_bytes: bytes | None = None,
) -> bool:
    verify_source(source, metadata)
    require(certificate.get("schema") == SCHEMA, "wrong certificate schema")
    require(certificate.get("status") == "PREFLIGHT_PASS", "not a pass")
    layout = certificate.get("layout_contract", {})
    require(
        layout.get("coefficient_and_frame_layout") == "standard-real-interleaved-12",
        "standard layout not typed",
    )
    require(
        layout.get("structured_transition_layout")
        == "contiguous-block-lower-8+4",
        "structured layout not typed",
    )
    require(layout.get("upper_right_exact_zero") is True, "upper zero not proved")
    require(
        layout.get("predecessor_interleaved_extractor_rejected") is True,
        "layout mutation not rejected",
    )
    method = certificate.get("method", {})
    require(method.get("generator") == GENERATOR, "certificate generator")
    require(method.get("omega_subcells") == 4, "wrong omega subdivision")
    require(method.get("radial_panels") == 8, "wrong radial panel count")
    require(method.get("taylor_order") == 12, "wrong Taylor order")
    require(method.get("dyadic_rebase_bits") == 128, "wrong rebase bits")
    require(
        method.get("rank_argument") == "block-lower-diagonal-ranks",
        "wrong rank proof",
    )
    require(
        method.get("full_12x12_interval_rank_used") is False,
        "full interval rank was used",
    )
    result = certificate.get("result", {})
    width = float(result.get("piecewise_moving_lower_width", float("inf")))
    baseline = float(result.get("baseline_unframed_lower_width", -1.0))
    require(baseline == BASELINE_WIDTH, "baseline changed")
    require(0.0 < width < baseline, "width contraction not proved")
    require(float(result.get("contraction_factor", 0.0)) > 1000.0, "weak contraction")
    cells = result.get("subcells", [])
    require(len(cells) == 4, "missing subcell results")
    require([cell.get("index") for cell in cells] == [0, 1, 2, 3], "cell order")
    for cell in cells:
        require(cell.get("carrier_rank") == 8, "carrier rank")
        require(cell.get("kernel_rank") == 4, "kernel rank")
        require(0.0 < float(cell.get("lower_width", -1.0)) <= width, "cell width")
    proof = certificate.get("proof_contract", {})
    require(proof.get("outward_local_tails") is True, "tails not outward")
    require(proof.get("global_remainder_retained_outward") is True, "remainder lost")
    require(proof.get("independent_exact_layout_oracle") is True, "oracle absent")
    require(
        proof.get("mutations_rejected")
        == [
            "interleaved-extractor-on-contiguous-block",
            "drop-D1-Wc-term",
            "break-generator",
            "erase-width-improvement",
            "change-source-hash",
        ],
        "mutation ledger differs",
    )
    provenance = certificate.get("provenance", {})
    require(provenance.get("source_sha256") == digest(source.encode()), "cert source hash")
    if metadata_bytes is not None:
        require(
            provenance.get("source_metadata_sha256") == digest(metadata_bytes),
            "metadata hash",
        )
    require(
        provenance.get("frame_table_import_is_data_only") is True,
        "predecessor import not scoped to data",
    )
    require(
        provenance.get("superseded_predecessor_certificate_used") is False,
        "invalid predecessor certificate used",
    )
    limits = certificate.get("does_not_establish", [])
    require("all 224 infinity microfactors" in limits, "global scope broadened")
    require("global horizon-to-infinity connection" in limits, "connection promoted")
    require("physical channel or flux classification" in limits, "physics promoted")
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--certificate", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--metadata", type=Path, required=True)
    args = parser.parse_args()
    try:
        metadata_bytes = args.metadata.read_bytes()
        verify_certificate(
            json.loads(args.certificate.read_text()),
            args.source.read_text(),
            json.loads(metadata_bytes),
            metadata_bytes,
        )
    except (OSError, json.JSONDecodeError, VerificationError) as exc:
        print(f"REFUSED: {exc}")
        return 3
    print("PASS moving-lower preflight")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

