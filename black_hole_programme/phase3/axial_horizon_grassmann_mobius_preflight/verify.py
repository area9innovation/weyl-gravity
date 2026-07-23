#!/usr/bin/env python3
"""Independent fail-closed verifier for the one-shell Mobius preflight."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
SCHEMA = "phase3-axial-horizon-grassmann-mobius-preflight-v1"
SOURCE_SCHEMA = "phase3-axial-horizon-grassmann-mobius-source-v1"
GENERATOR = 7315


class VerificationError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationError(message)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def verify_source(source: str, metadata: dict[str, Any]) -> None:
    require(metadata.get("schema") == SOURCE_SCHEMA, "source schema")
    require(metadata.get("generator") == GENERATOR, "source generator")
    require(metadata.get("omega_cell") == ["1/2", "129/256"], "omega cell")
    require(
        metadata.get("rho_cell") == ["1/4194304", "1/2097152"],
        "rho cell",
    )
    require(
        metadata.get("pivot_real_block_rows") == [1, 2, 8, 5, 6, 10],
        "pivot row crosswalk",
    )
    require(
        metadata.get("graph_real_block_rows") == [0, 3, 9, 4, 7, 11],
        "graph row crosswalk",
    )
    require(metadata.get("dyadic_rebase_bits") == 128, "rebase bits")
    require(metadata.get("omega_subcells") == 4, "omega subcells")
    require(metadata.get("chart_norm_limit") == 2, "chart norm")
    require(metadata.get("source_sha256") == digest(source.encode()), "source hash")
    witnesses = (
        "fn hm_i(k:i64)->i64{",
        "fn hm_j(k:i64)->i64{",
        "fn hm_right_solve(b:borrow IvAffineMat,a:borrow IvAffineMat)->HmResult{",
        "let at:IvAffineMat=ivam_transpose(a);",
        "let xt:IvAffineResult=ivam_solve_rect(at,bt);",
        "let x0:IvAffineMat=ivam_transpose(xt.value);",
        "let a:IvAffineResult=ivam_mul_checked(pij,z);",
        "let m0:IvAffineResult=ivam_add_checked(pii,a.value);",
        "let n0:IvAffineResult=ivam_add_checked(pji,b.value);",
        "let solved:HmResult=hm_right_solve(n.value,m.value);",
        "ivam_rebase_dyadic(m0.value,128)",
        "ivam_rebase_dyadic(n0.value,128)",
        "ivam_rebase_dyadic(dn.value,128)",
        "if(w.generator!=7315)",
        "if(!hm_intersects(z,zg))",
        "!hm_intersects(z,direct_graph.z)",
    )
    for witness in witnesses:
        require(witness in source, f"missing source witness: {witness}")
    require(
        "let solved:HmResult=hm_right_solve(m.value,n.value);" not in source,
        "left/right operands reversed",
    )
    require(
        "let m0:IvAffineResult=ivam_add_checked(pii,z);" not in source,
        "Phi_IJ Z term absent",
    )


def verify_certificate(
    certificate: dict[str, Any],
    source: str,
    metadata: dict[str, Any],
    metadata_bytes: bytes,
) -> bool:
    verify_source(source, metadata)
    require(certificate.get("schema") == SCHEMA, "certificate schema")
    require(
        certificate.get("status") in {"PREFLIGHT_PASS", "METHOD_SHORTFALL"},
        "unknown lifecycle",
    )
    method = certificate.get("method", {})
    require(method.get("generator") == GENERATOR, "certificate generator")
    chart = method.get("complex_chart", {})
    require(
        chart.get("pivot_real_block_rows") == [1, 2, 8, 5, 6, 10],
        "certificate pivot rows",
    )
    require(
        chart.get("graph_real_block_rows") == [0, 3, 9, 4, 7, 11],
        "certificate graph rows",
    )
    require(method.get("dyadic_rebase_bits") == 128, "certificate rebase")
    require(method.get("omega_subcells") == 4, "certificate subcells")
    require(method.get("chart_norm_limit") == 2.0, "certificate norm limit")
    require(method.get("minimum_width_improvement") == 2.0, "width threshold")
    provenance = certificate.get("provenance", {})
    require(provenance.get("source_sha256") == digest(source.encode()), "cert source hash")
    require(
        provenance.get("source_metadata_sha256") == digest(metadata_bytes),
        "metadata hash",
    )
    require(provenance.get("predecessor_certificate_used") is False, "bad predecessor")
    mutations = certificate.get("proof_contract", {}).get("mutations_rejected")
    require(
        mutations
        == [
            "wrong-left-solve",
            "drop-Phi_IJ-Z",
            "wrong-standard-interleaved-row-crosswalk",
            "break-generator",
            "erase-column-gauge-invariance",
            "omit-rebase128",
        ],
        "mutation ledger",
    )
    limits = certificate.get("does_not_establish", [])
    require("a horizon-to-r4 map or horizon-to-infinity connection" in limits, "r4 promoted")
    require(
        "scattering, flux-sign, stability, ghost, positivity, CPT or unitarity"
        in limits,
        "physics promoted",
    )
    if certificate["status"] == "PREFLIGHT_PASS":
        gates = certificate.get("gates", {})
        require(all(gates.values()), "a pass gate is false")
        rows = certificate.get("result", {}).get("panels", [])
        require(len(rows) == 64, "panel count")
        require(
            [(row["subcell"], row["index"]) for row in rows]
            == [(q, p) for q in range(4) for p in range(16)],
            "panel order",
        )
        require(all(row["rank"] == 6 for row in rows), "panel rank")
        require(all(row["chart_norm_upper"] < 2.0 for row in rows), "panel norm")
        subcells = certificate["result"].get("subcells", [])
        require([row["index"] for row in subcells] == list(range(4)), "subcell order")
        require(
            all(row["width_improvement"] >= 2.0 for row in subcells),
            "weak width result",
        )
        require(certificate["result"]["first_failed_gate"] is None, "pass has failure")
    else:
        require(
            bool(certificate.get("result", {}).get("first_failed_gate")),
            "shortfall lacks first failed gate",
        )
        require(len(certificate.get("establishes", [])) == 1, "shortfall overclaims")
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--certificate", type=Path, default=HERE / "certificate.json")
    parser.add_argument("--source", type=Path, default=HERE / "mobius_first_shell.forge")
    parser.add_argument("--metadata", type=Path, default=HERE / "source_metadata.json")
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
    print("PASS independent one-shell Grassmann/Mobius verifier")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
