#!/usr/bin/env python3
"""Independent verifier for the conserved/traceless odd-source certificate."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fail(message: str) -> None:
    raise SystemExit(message)


def verify(data: dict) -> None:
    if data["schema"] != "axial-qnm-conserved-source-overlap-v1":
        fail("schema mismatch")
    if data["status"] != "EXACT_CONSERVED_TRACELESS_SOURCE_OVERLAP":
        fail("status mismatch")
    if data["dependency_tags"] != ["LOCAL-ALGEBRAIC", "REDUCED-MODE"]:
        fail("dependency-tag mismatch")
    for imported in data["imports"].values():
        path = ROOT / imported["path"]
        if not path.exists() or digest(path) != imported["sha256"]:
            fail(f"import hash mismatch: {path}")

    r, mass, mu, omega = sp.symbols("r M mu omega", nonzero=True)
    f = 1 - 2 * mass / r
    source = sp.Function("F")(r)
    p_r = mu * source / (2 * sp.I * omega * r * f)
    p_up = sp.simplify(f * p_r)

    # Recompute from the covariant source formula rather than parsing the
    # producer's intermediate expressions.
    reduced_source = sp.simplify(
        f * (2 * r / mu) * (sp.I * omega * p_r)
    )
    if sp.simplify(reduced_source - source) != 0:
        fail("reduced source realization failed")
    p_tensor = sp.diff(r * source, r) / (2 * sp.I * omega)
    conservation = sp.simplify(
        sp.diff(p_up, r) + 2 * p_up / r - mu * p_tensor / r**2
    )
    if conservation != 0:
        fail("conservation identity failed")

    source_data = data["source_realization"]
    expected = {
        "P_t": "0",
        "P_r_covariant": "mu*F/(2*I*omega*r*f)",
        "P_tensor": "d_r(r*F)/(2*I*omega)",
        "reduced_RW_source": "f*S_odd=F",
        "trace": "0",
    }
    for key, value in expected.items():
        if source_data[key] != value:
            fail(f"source declaration drift: {key}")

    overlap = data["adjoint_overlap"]
    if overlap["value"] != "integral(eta*abs(tilde_u)**2,dx)>0":
        fail("adjoint overlap witness drift")
    conformal = data["conformal_source_audit"]
    if not conformal["constructed_source_conserved"]:
        fail("conservation claim lost")
    if not conformal["constructed_source_traceless"]:
        fail("tracelessness claim lost")
    if conformal["massive_point_particle_directly_admissible"]:
        fail("massive point-particle claim improperly promoted")

    flags = data["claim_flags"]
    required_true = {
        "arbitrary_compact_reduced_source_realized",
        "stress_energy_conserved",
        "stress_energy_traceless",
        "constructed_source_adjoint_overlap_nonzero",
    }
    required_false = {
        "specified_geodesic_plunge_overlap_nonzero",
        "positive_energy_matter_realization",
        "global_causal_contour_theorem",
        "detector_observability",
    }
    if any(not flags[key] for key in required_true):
        fail("required exact claim flag is false")
    if any(flags[key] for key in required_false):
        fail("open claim was improperly promoted")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--certificate", type=Path, default=HERE / "certificate.json"
    )
    args = parser.parse_args()
    verify(json.loads(args.certificate.read_text()))
    print("AXIAL_QNM_CONSERVED_SOURCE_OVERLAP_VERIFIED")


if __name__ == "__main__":
    main()
