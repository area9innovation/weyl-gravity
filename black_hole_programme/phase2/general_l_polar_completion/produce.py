#!/usr/bin/env python3
"""Join six exact branch checkpoints into the scoped polar frontier."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "certificate.json"
V1_CERT = ROOT / "black_hole_programme/phase2/general_l_polar/certificate.json"
BRANCH_DIR = HERE / "branch_artifacts"
V1_SHA256 = "49b224aec8ee358dd4f0c096063d83ee00b2571b222009f73eadd84241a23ab2"
V1_COMMIT = "e5e372f0feabb5faaf91888241d04efab66d46c1"
V1_BLOB = "324fe1839d1c5e9d8e6257f409204fd7d74abee5"
SUBOBJECTS = {
    "carrier_conventions": ("/exact_symbolic_lambda_result/generic_carrier_asymptotics", "19d366a23c4130a763926a36a83afc37aa5ef1db8f5a08259ca477a01dbf43d1"),
    "ricci_reconstruction": ("/exact_symbolic_lambda_result/ricci_to_metric_reconstruction", "98959867cb94dfb739e6ee05d136f6400762f8b52b08ec7dea86d44b06344cc4"),
    "seven_metric_rows": ("/exact_symbolic_lambda_result/ricci_to_metric_reconstruction/metric_rows", "02a034fb0cf8218bce77a5d3f37b5ea0a18c45875580e75a8d9c3212b96ce009"),
    "dependent_source_rows": ("/exact_symbolic_lambda_result/ricci_to_metric_reconstruction/source_dependent_components", "5d6a6e651d8413fc5d44fb8557ccd71d29e92aba1e1a5d0701657af919093708"),
    "depth2_pilot": ("/exact_symbolic_lambda_result/bounded_sourced_lift_depth2_pilot", "64a90838487b83a3a3ed03a95e75e43d0b16f40aba82cbf1c194a8af051cceb7"),
}
EXPECTED_BRANCHES = {
    ("zero", 0): (7, 3), ("zero", 1): (8, 4), ("zero", 2): (9, 5),
    ("oscillatory", 0): (9, 5), ("oscillatory", 1): (8, 4),
    ("oscillatory", 2): (9, 5),
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json_hash(value: object) -> str:
    encoded = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
    ).encode("utf-8")
    return sha256_bytes(encoded)


def pointer(document: object, path: str) -> object:
    value = document
    for token in path.strip("/").split("/"):
        value = value[token]  # type: ignore[index]
    return value


def verify_v1() -> dict:
    raw = V1_CERT.read_bytes()
    if sha256_bytes(raw) != V1_SHA256:
        raise RuntimeError("v1 certificate content drift")
    document = json.loads(raw)
    bindings = {}
    for name, (path, expected) in SUBOBJECTS.items():
        actual = canonical_json_hash(pointer(document, path))
        if actual != expected:
            raise RuntimeError(f"v1 subobject drift: {name}")
        bindings[name] = {"json_pointer": path, "canonical_json_sha256": expected}
    return {
        "commit": V1_COMMIT,
        "certificate": {
            "path": str(V1_CERT.relative_to(ROOT)), "git_blob": V1_BLOB,
            "sha256": V1_SHA256,
        },
        "subobjects": bindings,
    }


def verify_payload_hash(branch: dict) -> None:
    scope = branch["payload_sha256_scope"]
    payload = {key: branch[key] for key in scope}
    if canonical_json_hash(payload) != branch["payload_sha256"]:
        raise RuntimeError(f"branch payload hash drift: {branch['sector']}:{branch['index']}")


def load_branches(imported_v1: dict) -> list[dict]:
    rows = []
    for (sector, index), (carrier_depth, metric_depth) in EXPECTED_BRANCHES.items():
        path = BRANCH_DIR / f"{sector}-{index}.json"
        raw = path.read_bytes()
        branch = json.loads(raw)
        verify_payload_hash(branch)
        if (branch["sector"], branch["index"]) != (sector, index):
            raise RuntimeError(f"branch identity drift: {path}")
        if (branch["carrier_depth"], branch["metric_depth"]) != (carrier_depth, metric_depth):
            raise RuntimeError(f"branch depth drift: {path}")
        if branch["imported_v1"] != imported_v1:
            raise RuntimeError(f"branch v1 binding drift: {path}")
        metric = branch["metric_reconstruction"]
        if not metric["original_seven_row_residuals_zero"]:
            raise RuntimeError(f"seven-row closure weakened: {path}")
        if metric["physical_domain_exceptional_set"]:
            raise RuntimeError(f"unclassified physical pivot wall: {path}")
        if branch["complete_log_classification"] or branch["constructed_log_degree"] != 0:
            raise RuntimeError(f"log boundary drift: {path}")
        rows.append({
            "sector": sector, "branch_index": index,
            "artifact_path": str(path.relative_to(ROOT)),
            "artifact_sha256": sha256_bytes(raw),
            "payload_sha256": branch["payload_sha256"],
            "carrier_power": branch["sigma"],
            "metric_base_power": metric["base"],
            "carrier_depth": carrier_depth, "metric_depth": metric_depth,
            "constructed_log_degree": 0,
            "complete_log_classification": False,
            "all_seven_rows_through_metric_depth": True,
            "metric_order_ranks": [w["rank"] for w in metric["per_order_affine_rank_witnesses"]],
            "metric_order_nullities": [w["nullity"] for w in metric["per_order_affine_rank_witnesses"]],
            "physical_domain_exceptional_set": [],
            "pivot_denominator_factors": metric["pivot_denominator_factors"],
            "safe_tail_ledger": branch["safe_tail_ledger"],
        })
    return rows


def build() -> dict:
    imported_v1 = verify_v1()
    branches = load_branches(imported_v1)
    return {
        "schema": "phase2-black-hole-general-l-polar-canonical-log-free-frontier-v1",
        "result_id": "PHASE2_BLACK_HOLE_GENERAL_L_POLAR_CANONICAL_LOG_FREE_FRONTIER_V1",
        "lifecycle": "CLASSIFIED_PARTIAL",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "imported_v1": imported_v1,
        "scope": {
            "parity": "polar/even", "mass_normalization": "M=1",
            "frequency": "real omega!=0", "representations": "Lambda=ell*(ell+1), integer ell>=2",
            "correction_class": "six constructed canonical log-free finite inverse-radial jets",
        },
        "method": {
            "coefficient_domain": "QQ(I)(Lambda,omega)",
            "carrier": "two-order moving exact recurrence with faster-mode freedoms fixed by the canonical zero choice",
            "metric": "per-order affine fraction-field solve of all seven original Ricci rows",
            "rank_witness": "serialized compact augmented matrix, exact RREF, pivots, particular solution and nullspace at each order",
            "payload_hash": "SHA-256 over the explicitly scoped canonical UTF-8 JSON payload",
            "global_cancel_or_groebner": False,
        },
        "canonical_log_free_frontier": branches,
        "physical_domain_pivot_disposition": {
            "exceptional_set": [],
            "domain": "real omega!=0 and Lambda=ell*(ell+1), integer ell>=2",
            "nonwall_factors": [
                "Lambda", "Lambda-2", "Lambda-3", "omega",
                "Lambda**2-2*Lambda-12*I*omega",
                "Lambda**2-2*Lambda-256*omega**4+I*(64*omega**3+12*omega)",
                "Delta",
            ],
            "delta_proof": "For x=omega**2>0, Im(Delta)=12*omega*(Lambda-128*x**2-24*x-3). On Im(Delta)=0, Re(Delta)=128*x**2*(16384*x**4+6144*x**3+1088*x**2+112*x+1)>0.",
            "reading": "No pivot denominator in the six constructed representatives vanishes on the declared physical domain.",
        },
        "physical_conjugation": {
            "map": "I -> -I", "fixed_symbols": ["Lambda", "m", "omega", "alpha"],
            "omega_is_not_negated": True,
        },
        "mass_restoration": {
            "dimensionless_variables": "rho=r/M and varpi=M*omega",
            "rule": "Restore generic M by expressing powers in rho and replacing serialized omega by varpi; amplitude normalization is branch-conventional.",
            "current_normalization": "not applicable: no EE/EX/XX current table is promoted",
        },
        "resonant_log_discrepancy": {
            "v1": "At depth 2, oscillatory branch 1 in the eliminated triangular splitting has log_degree=1 and nonzero log coefficients.",
            "this_frontier": "The moving-carrier canonical splitting constructs a log-free representative through metric depth 4.",
            "next_order_compatibility": {
                "agreement_orders": [0, 1],
                "first_different_terminal_order": 2,
                "left_null_defect": "3*Lambda - 48*omega**2 + 15 + 12*I*omega",
                "physical_domain_proof": "Im(defect)=12*omega!=0 for real omega!=0",
                "verdict": "the v1 terminal depth-2 carrier jet is nowhere extendible on the declared physical domain",
            },
            "status": "NONEXTENDIBLE_SHALLOW_SOURCE_ARTIFACT",
            "consequence": "The old log is not an extendible branch witness; an all-order log-module and branch-specialized current theorem are still not claimed.",
        },
        "first_remaining_exact_object": "POLAR_RESONANT_LOG_MODULE_AND_REPRESENTATIVE_SHIFT_INVARIANT_EE_EX_XX_CURRENT",
        "unavailable_theorem_fields": [
            "complete resonant log-degree and carrier-splitting classification",
            "explicit homogeneous Einstein basis jets and seven-row classification",
            "representative-shift law for the polar current",
            "branch-specialized EE/EX/XX leading table",
            "exact current exceptional set",
            "parity-complete Schwarzschild disposition",
        ],
        "does_not_establish": [
            "a generic polar finite-pairing or Einstein-selection theorem",
            "asymptotic phase space, finite norm, or flux", "scattering",
            "QNM or ringdown", "stability", "particles", "positivity", "quantum theory",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build()
    if args.check:
        if json.loads(OUTPUT.read_text()) != payload:
            raise RuntimeError("certificate regeneration drift")
    else:
        OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print("polar canonical log-free frontier certificate: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
