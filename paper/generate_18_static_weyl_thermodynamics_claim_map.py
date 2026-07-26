#!/usr/bin/env python3
"""Generate the Paper 18 claim map from its authoritative exact certificates."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper" / "18-static-bach-flat-black-hole-thermodynamics.tex"
OUTPUT = ROOT / "paper" / "18-static-bach-flat-black-hole-thermodynamics-claim-map.json"
CERT_DIR = ROOT / "black_hole_programme" / "certificates"

CERTIFICATES = {
    "BH0": CERT_DIR / "BH0_STATIC_SPHERICAL_BACKGROUND.json",
    "BH1": CERT_DIR / "BH1_LEE_WALD_PREFLIGHT.json",
    "BH1A": CERT_DIR / "BH1A_NORMALIZED_GENERATOR.json",
    "BH1B": CERT_DIR / "BH1B_DYNAMICAL_EXTENSION.json",
    "P18": CERT_DIR / "PAPER18_STATIC_FIRST_LAW_PROMOTION.json",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build() -> dict:
    certs = {name: load(path) for name, path in CERTIFICATES.items()}
    return {
        "schema": "paper18-static-weyl-thermodynamics-claim-map-v1",
        "paper": rel(PAPER),
        "title": "Residual-Basic Charges and Simultaneous Horizon First Laws on the Mannheim-Kazanas Family",
        "scope": {
            "background": "static spherical pure-Weyl gravity; Laurent-class background theorem and Mannheim-Kazanas charge component",
            "phase_space": "regular local quotient charts of the Mannheim-Kazanas static parameter slice plus the complete linear l=0 conformal/diffeomorphism gauge sector at charge level",
            "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
            "arithmetic": "exact symbolic rational and polynomial identities",
        },
        "claims": [
            {
                "id": "P18-C1",
                "statement": "Within the declared Laurent ansatz, Bach-flatness is equivalent to c2=c3=0 and w^2+3*u*gamma=1.",
                "evidence": ["BH0"],
                "status": "UNCONDITIONAL_WITHIN_DECLARED_LAURENT_CLASS",
                "used_in_main_theorem": True,
            },
            {
                "id": "P18-C2",
                "statement": "On the full Laurent locus the Einstein sheet requires gamma=0 and w=1; gamma=0 alone is sufficient only on the Mannheim-Kazanas component through w=1.",
                "evidence": ["BH0", "manuscript scalar-curvature calculation"],
                "status": "EXACT_MANUSCRIPT_CORRECTION_TO_LEGACY_CERTIFICATE_WORDING",
                "used_in_main_theorem": True,
            },
            {
                "id": "P18-C3",
                "statement": "The bare chart-normalized Iyer-Wald one-form is radially constant but non-closed on the static parameter family.",
                "evidence": ["BH1"],
                "status": "EXACT_STATIC_PARAMETER_SLICE",
                "used_in_main_theorem": True,
            },
            {
                "id": "P18-C4",
                "statement": "Residual basicness forces N=u*f(J); for N=u the corrected charge is exact with the displayed Hamiltonian.",
                "evidence": ["BH1A", "P18"],
                "status": "EXACT_ON_DECLARED_REGULAR_LOCAL_QUOTIENT_CHARTS",
                "used_in_main_theorem": True,
            },
            {
                "id": "P18-C5",
                "statement": "The displayed Hamiltonian, Wald entropy, and signed temperature obey dH=T_h*dS_h at every simple horizon simultaneously.",
                "evidence": ["BH1A", "P18"],
                "status": "EXACT_STATIC_PARAMETER_SLICE",
                "used_in_main_theorem": True,
            },
            {
                "id": "P18-C6",
                "statement": "Arbitrary linear spherical Weyl and diffeomorphism directions have zero corrected charge; conformal directions also have zero entropy variation and zero corrected pairing with parameter modes.",
                "evidence": ["BH1B", "P18"],
                "status": "EXACT_LINEAR_CHARGE_LEVEL_L0",
                "used_in_main_theorem": True,
            },
        ],
        "does_not_establish": [
            "completeness beyond the Laurent ansatz",
            "a preferred physical mass or asymptotic clock",
            "a nonlinear or second-order physical-process first law",
            "the bilinear radiative symplectic flux matrix",
            "stability, quasinormal ringing, Hawking radiation, or a quantum theorem",
        ],
        "evidence": {
            name: {
                "path": rel(path),
                "sha256": sha256(path),
                "result_token": certs[name]["result_token"],
                "dependency_tags": certs[name]["dependency_tags"],
                "lifecycle": certs[name]["declaration"]["lifecycle"],
                "verification_command": certs[name]["verification_command"],
            }
            for name, path in CERTIFICATES.items()
        },
        "independence_profile": {
            "producer_and_verifier_code": "separate implementations",
            "curvature_representation": "verifier uses an independent Schouten/Kulkarni-Nomizu Weyl construction",
            "arithmetic_backend": "exact SymPy certificate backends plus an independent Python-standard-library fractions.Fraction sparse Laurent-polynomial rail",
            "mathematical_derivation": "independent recomputation of tensor identities, entropy, reductions, and mutations where recorded by each certificate",
        },
        "release_boundary": {
            "paper_status": "WORKING_DRAFT",
            "immutable_archive": False,
            "expert_peer_review": False,
            "certificate_lifecycle_note": "BH1, BH1A, and BH1B retain their historical PREFLIGHT lifecycle labels; P18 is an append-only CLASSIFIED successor scoped only to the paper's static theorem and linear spherical charge audit.",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--out", type=Path, default=OUTPUT)
    args = parser.parse_args()
    text = json.dumps(build(), indent=2, sort_keys=True) + "\n"
    if args.check:
        if not args.out.exists() or args.out.read_text(encoding="utf-8") != text:
            raise SystemExit(f"stale claim map: regenerate {args.out}")
        print(f"PASS current {args.out}")
        return
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
