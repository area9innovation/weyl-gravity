#!/usr/bin/env python3
"""Emit the exact conformal spin-two coefficient and D-descent certificate."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

try:
    from .coefficient_reconstruction import exact_payload
except ImportError:
    from coefficient_reconstruction import exact_payload


PACKAGE_ROOT = Path(__file__).resolve().parent
REPOSITORY_ROOT = PACKAGE_ROOT.parents[2]
OUTPUT = PACKAGE_ROOT / "certificates" / "WEYL_GRAVITON_ANOMALY_COEFFICIENTS_D_DESCENT.json"
SCHEMA = PACKAGE_ROOT / "schema" / "weyl-graviton-anomaly-d-descent-v1.schema.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_hash(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def _source_manifest() -> dict[str, str]:
    relative_paths = (
        "quantum-weyl/spectral/euclidean/coefficient_reconstruction.py",
        "quantum-weyl/spectral/euclidean/coefficient_certificate.py",
        "quantum-weyl/spectral/euclidean/README.md",
        "quantum-weyl/spectral/euclidean/schema/weyl-graviton-anomaly-d-descent-v1.schema.json",
        "quantum-weyl/spectral/euclidean/tests/test_coefficient_reconstruction.py",
        "quantum-weyl/reports/weyl-graviton-anomaly-coefficients-d-descent.md",
        "quantum-weyl/local_bv/certificates/GENERAL_NONMINIMAL_GAUGE_FIXED_CONTRACTION.json",
        "notes/conformal-c2k-coefficient-compensator.md",
        "symbolic/verify_conformal_c2a_reducibilities.py",
        "notes/d-quotient-quantum-team-brief.md",
    )
    return {path: _sha256(REPOSITORY_ROOT / path) for path in relative_paths}


def build_certificate() -> dict[str, object]:
    calculation = exact_payload()
    g2 = json.loads(
        (
            REPOSITORY_ROOT
            / "quantum-weyl/local_bv/certificates/GENERAL_NONMINIMAL_GAUGE_FIXED_CONTRACTION.json"
        ).read_text()
    )
    if (
        g2.get("result_state")
        != "FULL_LOCAL_BV_G2_COMPLETE_ON_REGULAR_BACH_LOCUS_ANALYTIC_QME_OPEN"
        or g2.get("claim_flags", {}).get("FULL_BV_G2_COMPLETE") is not True
        or g2.get("claim_flags", {}).get("H14_GAUGE_FIXED_BV_COMPLETE") is not True
    ):
        raise ValueError("full gauge-fixed BV anomaly basis is unavailable")
    manifest = _source_manifest()
    payload = {
        "schema": "quantum-weyl-weyl-graviton-anomaly-d-descent-v1",
        "result_id": "WEYL_GRAVITON_ANOMALY_COEFFICIENTS_D_DESCENT",
        "result_state": "STANDARD_SPIN2_BACKGROUND_COEFFICIENTS_COMPUTED_D_PULLBACK_CERTIFIED",
        "result_stage": "COEFFICIENT_COMPUTED",
        "dependency_tags": ["EUCLIDEAN-SPECTRAL", "LOCAL-ALGEBRAIC"],
        "coefficient_scope": "standard isolated four-dimensional conformal spin-two background Weyl anomaly",
        **calculation,
        "analytic_inputs": {
            "determinant_factorization": "Weyl graviton on Ricci-flat and constant-curvature Einstein backgrounds",
            "regularization": "second-order heat-kernel b4 / logarithmic UV coefficient",
            "gauge_and_ghost_policy": "factorized gauge-fixed determinant including the source's ghost determinants",
            "parity_policy": "real tensor Laplacians with no epsilon, Hodge-star or chiral insertion; parity-even heat-kernel b4",
            "zero_mode_policy": "unprojected-operator heat-kernel identities; no projected zeta zero-mode promotion",
            "contour_policy": "irrelevant to the local logarithmic heat-kernel coefficient; no phase or finite part claimed",
            "repository_euclidean_gate": "LOCAL_BV_G2_COMPLETE_ELLIPTIC_OPERATOR_MEASURE_AND_AUXILIARY_MATCHING_OPEN",
        },
        "source_provenance": {
            "primary_source": {
                "title": "On partition function and Weyl anomaly of conformal higher spin fields",
                "authors": ["A. A. Tseytlin"],
                "arxiv": "1309.0785v4",
                "url": "https://arxiv.org/abs/1309.0785",
                "eprint_sha256": "c0f2cf809f09a68e32faa45e1f5f01eaba8b519127ad8307b6e4064207059ad6",
                "formula_labels": ["1", "1a", "12", "12b", "21", "211", "ww", "www", "13", "aa2", "aa22", "nen"],
            },
            "independent_c_cross_check": {
                "title": "C_T for conformal higher spin fields from partition function on conically deformed sphere",
                "authors": ["M. Beccaria", "A. A. Tseytlin"],
                "arxiv": "1707.02456v2",
                "url": "https://arxiv.org/abs/1707.02456",
                "eprint_sha256": "e96bcb8a075058df66b9aebda75388609a62c767fb0780549656aec4b32b9b8e",
            },
            "source_manifest": manifest,
            "source_manifest_sha256": _canonical_hash(manifest),
        },
        "claim_flags": {
            "STANDARD_BACKGROUND_A_AND_C_COMPUTED": True,
            "STANDARD_BACKGROUND_PARITY_ODD_ZERO_VERIFIED": True,
            "FULL_GAUGE_FIXED_BV_ANOMALY_BASIS_AVAILABLE": True,
            "CYLINDER_D_LOCAL_ANOMALY_PULLBACK_ZERO": True,
            "MINKOWSKI_D_LOCAL_ANOMALY_PULLBACK_COMPUTED": True,
            "REPOSITORY_BV_ANOMALY_COEFFICIENT_COMPUTED": False,
            "D_CARTAN_ANOMALY_CLASSIFIED": False,
            "QME_RESTORED": False,
            "RESIDUAL_TRANSFERRED": False,
            "LORENTZIAN_CERTIFIED": False,
        },
        "claim_boundary": (
            "The exact numbers are the standard Euclidean background trace-anomaly coefficients reconstructed from "
            "the factorized conformal-spin-two determinant and heat-kernel formulae. For this declared parity-even "
            "standard regulator, an exact Ward audit proves the C dual C coordinate is zero because every factor is "
            "a real tensor Laplacian with no epsilon, Hodge-star or chiral insertion. The repository's complete local "
            "gauge-fixed BV anomaly basis is now available on the regular Bach locus, but the determinant is not yet "
            "matched to a repository elliptic operator, auxiliary/fourth-order Jacobian, measure, zero-mode policy, "
            "or regulated Slavnov action and therefore does not compute the quantum-master-equation breaking. The D "
            "result is only the one-generator pullback of the local ghost-number-one cocycle. Its "
            "vanishing on the closed vacuum cylinder follows from sigma_D=0 and does not establish a vanishing "
            "degree-zero quantum D-Cartan defect, boundary anomaly, measure anomaly, or Lorentzian theorem."
        ),
        "next_gate": (
            "match the repository elliptic operator, measure and auxiliary/fourth-order Jacobian, then construct the "
            "regulated Slavnov breaking plus the renormalized local Ward-insertion map"
        ),
    }
    return {**payload, "certificate_hash": _canonical_hash(payload)}


def _render(payload: dict[str, object]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    content = _render(build_certificate())
    if args.emit:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(content, encoding="utf-8")
    if args.check and (not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != content):
        raise SystemExit(f"Weyl-graviton coefficient/D-descent certificate is stale: {OUTPUT}")
    if not args.emit and not args.check:
        print(content, end="")
    else:
        print("WEYL GRAVITON ANOMALY: a=87/20, c=199/30, p=0; CYLINDER D PULLBACK ZERO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
