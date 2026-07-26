#!/usr/bin/env python3
"""Build the append-only Paper 18 theorem-promotion certificate.

The historical BH1/BH1A/BH1B PREFLIGHT records remain unchanged.  This
paper-specific successor binds their exact results, the independent
standard-library algebra rail, and the released manuscript artifacts.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "certificates" / "PAPER18_STATIC_FIRST_LAW_PROMOTION.json"
SCHEMA = HERE / "schema" / "paper18-static-first-law-promotion-v1.schema.json"
PAPER_TEX = ROOT / "paper" / "18-static-bach-flat-black-hole-thermodynamics.tex"
PAPER_PDF = ROOT / "paper" / "18-static-bach-flat-black-hole-thermodynamics.pdf"
STDLIB_RECEIPT = ROOT / "reports" / "PAPER18_STDLIB_ALGEBRA_RECEIPT.json"
EVIDENCE = {
    "BH0": HERE / "certificates" / "BH0_STATIC_SPHERICAL_BACKGROUND.json",
    "BH1": HERE / "certificates" / "BH1_LEE_WALD_PREFLIGHT.json",
    "BH1A": HERE / "certificates" / "BH1A_NORMALIZED_GENERATOR.json",
    "BH1B": HERE / "certificates" / "BH1B_DYNAMICAL_EXTENSION.json",
    "P18_STDLIB": STDLIB_RECEIPT,
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build() -> dict:
    for path in (SCHEMA, PAPER_TEX, PAPER_PDF, *EVIDENCE.values()):
        if not path.exists():
            raise SystemExit(f"missing promotion input: {path}")
    records = {name: load(path) for name, path in EVIDENCE.items()}
    return {
        "schema": "paper18-static-first-law-promotion-v1",
        "schema_path": rel(SCHEMA),
        "schema_sha256": sha256(SCHEMA),
        "result_id": "PAPER18_STATIC_FIRST_LAW_PROMOTION",
        "result_token": "PAPER18_STATIC_FIRST_LAW_CLASSIFIED",
        "declaration": {
            "lifecycle": "CLASSIFIED",
            "scope": "Paper 18 exact Mannheim-Kazanas static parameter theorem and linear spherical charge audit",
            "historical_certificates_unchanged": True,
            "expert_peer_reviewed": False,
        },
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "promoted_claims": [
            {
                "id": "P18-C1",
                "statement": "The Bach-flat locus is complete within the declared six-term Laurent ansatz.",
            },
            {
                "id": "P18-C4",
                "statement": "On each declared regular local quotient chart, residual basicness fixes N=u*f(J), and u*F=dH.",
            },
            {
                "id": "P18-C5",
                "statement": "The residual-basic Hamiltonian obeys dH=T_h*dS_h at every locally labelled simple horizon.",
            },
            {
                "id": "P18-C6",
                "statement": "The complete linear spherical conformal/diffeomorphism gauge sector does not change the charge theorem.",
            },
        ],
        "evidence": {
            name: {
                "path": rel(path),
                "sha256": sha256(path),
                "result_token": records[name]["result_token"],
            }
            for name, path in EVIDENCE.items()
        },
        "paper_artifacts": {
            "source": {"path": rel(PAPER_TEX), "sha256": sha256(PAPER_TEX)},
            "pdf": {"path": rel(PAPER_PDF), "sha256": sha256(PAPER_PDF)},
        },
        "independence_profile": {
            "code": "separate programme producers, certificate verifiers, claim-map verifier, and Paper 18 standard-library verifier",
            "representation": "independent curvature construction plus an independent sparse Laurent-polynomial representation for the charge and first-law core",
            "arithmetic_backend": "SymPy exact algebra for programme certificates; Python fractions.Fraction only for the Paper 18 independent algebra rail",
            "derivation": "the paper prints the reduced Bach rows and exact first-law quotients; verifiers recompute rather than parse expected prose",
        },
        "claim_flags": {
            "laurent_classification_certified": True,
            "residual_basic_normalization_certified": True,
            "simultaneous_static_first_law_certified": True,
            "linear_spherical_gauge_audit_certified": True,
            "physical_process_first_law_certified": False,
            "radiative_flux_certified": False,
        },
        "does_not_establish": [
            "completeness of static Bach vacua beyond the Laurent ansatz",
            "a preferred physical mass or asymptotic clock",
            "a nonlinear or second-order physical-process first law",
            "a bilinear radiative flux law",
            "stability, Hawking radiation, or a quantum theorem",
            "expert peer review or journal acceptance",
        ],
        "provenance": {
            "engine_path": rel(Path(__file__).resolve()),
            "engine_sha256": sha256(Path(__file__).resolve()),
        },
        "verification_command": "python3 black_hole_programme/verify_paper18_static_first_law_promotion.py",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--out", type=Path, default=OUTPUT)
    args = parser.parse_args()
    text = json.dumps(build(), indent=2, sort_keys=True) + "\n"
    if args.check:
        if not args.out.exists() or args.out.read_text(encoding="utf-8") != text:
            raise SystemExit(f"stale promotion certificate: regenerate {args.out}")
        print(f"PASS current {args.out}")
        return
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
