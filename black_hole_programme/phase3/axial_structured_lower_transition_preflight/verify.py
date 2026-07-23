#!/usr/bin/env python3
"""Independent fail-closed verifier for the structured-lower preflight."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from .structured_reference import verify_exact_fixture


SCHEMA = "phase3-axial-structured-lower-preflight-v1"
SOURCE_SCHEMA = "phase3-axial-structured-lower-preflight-source-v1"
WITHDRAWAL_SCHEMA = "phase3-axial-structured-lower-preflight-withdrawal-v1"
GENERATOR = 7315


class VerificationError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationError(message)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def verify_source(source: str, metadata: dict[str, Any]) -> bool:
    require(metadata.get("schema") == SOURCE_SCHEMA, "wrong source schema")
    require(metadata.get("generator") == GENERATOR, "shared generator changed")
    require(
        metadata.get("omega_cell") == ["1/2", "129/256"],
        "shared omega cell changed",
    )
    require(
        metadata.get("source_sha256") == sha256_bytes(source.encode()),
        "generated source hash differs",
    )
    required = (
        "let lg:IvAffineResult=ivam_mul_checked(g,oldc);",
        "let lk:IvAffineResult=ivam_mul_checked(ak,oldl);",
        "let rl:IvAffineResult=ivam_add_checked(lg.value,lk.value);",
        "let tl:f64=beta*hf*tl0;",
        "ivam_pad_remainder(sl,tl)",
        "ivam_rebase_dyadic(cc.value,128)",
        "ivam_rebase_dyadic(kk.value,128)",
        "ivam_rebase_dyadic(low.value,128)",
        "ivam_block_lower(pcorr.value,plorr.value,pkorr.value)",
        "ivam_full_column_rank_cells(uc,16)",
        "ivam_full_column_rank_cells(uk,16)",
        "u.generator!=7315",
    )
    for witness in required:
        require(witness in source, f"missing method witness: {witness}")
    require(
        "ivam_full_column_rank_cells(u," not in source,
        "full 12x12 interval rank was reintroduced",
    )
    require(
        "rr.lo!=0.0 || rr.hi!=0.0" in source,
        "exact-zero upper-right audit missing",
    )
    require(verify_exact_fixture(), "exact constant block fixture failed")
    require(
        not verify_exact_fixture("omit_kernel_lower"),
        "omitted kernel-lower mutation escaped exact fixture",
    )
    require(
        not verify_exact_fixture("swap_order"),
        "multiplication-order mutation escaped exact fixture",
    )
    return True


def verify_certificate(
    certificate: dict[str, Any],
    source: str,
    metadata: dict[str, Any],
) -> bool:
    verify_source(source, metadata)
    require(certificate.get("schema") == SCHEMA, "wrong certificate schema")
    require(certificate.get("status") == "PREFLIGHT_PASS", "not a pass")
    require(certificate.get("generator") == GENERATOR, "certificate generator changed")
    require(
        certificate.get("omega_cell") == ["1/2", "129/256"],
        "certificate omega cell changed",
    )
    result = certificate.get("first_microfactor", {})
    require(result.get("domain") == ["0", "1/8"], "wrong radial microinterval")
    require(result.get("panels") == 8, "wrong panel count")
    require(result.get("order") == 12, "wrong Taylor order")
    require(result.get("dyadic_rebase_bits") == 128, "wrong rebase precision")
    require(result.get("carrier_rank") == 8, "carrier rank not certified")
    require(result.get("kernel_rank") == 4, "kernel rank not certified")
    require(result.get("upper_right_exact_zero") is True, "upper right not zero")
    require(result.get("rank_argument") == "block-lower-determinant", "wrong rank proof")
    require(
        result.get("full_12x12_interval_rank_used") is False,
        "full rank enclosure was used",
    )
    require(float(result.get("max_width")) >= 0.0, "invalid width")
    proof = certificate.get("proof_contract", {})
    require(proof.get("outward_tails") is True, "tails not outward")
    require(proof.get("shared_generator") is True, "generator not shared")
    require(proof.get("dyadic_rebasing") is True, "rebasing missing")
    require(proof.get("constant_block_exact_fixture") is True, "exact fixture missing")
    require(proof.get("mutations_rejected") == [
        "omit-kernel-times-lower",
        "swap-multiplication-order",
        "drop-tail",
        "break-generator",
    ], "mutation ledger differs")
    require(
        certificate.get("source_sha256") == metadata["source_sha256"],
        "certificate source hash differs",
    )
    limits = certificate.get("does_not_establish", [])
    require(
        "useful full-chain widths" in limits
        and "global horizon-to-infinity connection" in limits,
        "claim boundary broadened",
    )
    return True


def verify_withdrawal(
    certificate: dict[str, Any],
    withdrawal: dict[str, Any],
    source: str,
) -> bool:
    require(certificate.get("schema") == SCHEMA, "wrong certificate schema")
    require(
        certificate.get("status") == "WITHDRAWN_LAYOUT_DEFECT",
        "certificate is not marked withdrawn",
    )
    require(
        withdrawal.get("schema") == WITHDRAWAL_SCHEMA,
        "wrong withdrawal schema",
    )
    require(
        withdrawal.get("status") == "WITHDRAWN_LAYOUT_DEFECT",
        "withdrawal disposition changed",
    )
    defect = withdrawal.get("defect", {})
    require(defect.get("producer_operation") == "sl_compose", "wrong defect site")
    require(
        defect.get("incorrect_extractor") == "gc_affine_submatrix",
        "wrong defective extractor",
    )
    require(
        "fn sl_compose" in source
        and "let lc:IvAffineMat=gc_affine_submatrix(left,0);" in source
        and "ivam_block_lower(ccr.value,lr.value,kkr.value)" in source,
        "withdrawn layout defect is not present in the retained source",
    )
    superseded = certificate.get("withdrawal", {}).get("supersedes_claims", [])
    require(len(superseded) == 3, "superseded-claim ledger incomplete")
    require(
        withdrawal.get("disposition", {}).get("scientific_claim")
        == "No structured-transition pass remains from this package.",
        "withdrawal claim boundary changed",
    )
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--certificate", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--metadata", type=Path, required=True)
    args = parser.parse_args()
    try:
        certificate = json.loads(args.certificate.read_text())
        source = args.source.read_text()
        if certificate.get("status") == "WITHDRAWN_LAYOUT_DEFECT":
            withdrawal = json.loads(
                (args.certificate.parent / "withdrawal.json").read_text()
            )
            verify_withdrawal(certificate, withdrawal, source)
            print("WITHDRAWN: structured-lower layout defect")
            return 4
        verify_certificate(certificate, source, json.loads(args.metadata.read_text()))
    except (OSError, json.JSONDecodeError, VerificationError) as exc:
        print(f"REFUSED: {exc}")
        return 3
    print("PASS structured-lower preflight")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
