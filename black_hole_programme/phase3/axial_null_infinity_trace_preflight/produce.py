"""Produce the exact axial null-infinity trace preflight certificate."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp

from .current_dag import derive_rational_radius_current, real_conjugate


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "certificate.json"
RECEIPT = HERE / "receipt.json"
SCHEMA = HERE / "schema.json"

INPUTS = {
    "literal_current": "black_hole_programme/certificates/BH2A_FLUX_MATRIX.json",
    "complete_reconstruction": "black_hole_programme/phase3/axial_complete_reconstruction_repair/certificate.json",
    "metric_heads": "black_hole_programme/phase3/axial_endpoint_remainder_enclosures/infinity-metric-heads.json",
    "endpoint_basis": "black_hole_programme/phase3/axial_endpoint_bases/certificate.json",
    "boundary_contract": "black_hole_programme/phase3/boundary_flux_contract/certificate.json",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def expr(value: sp.Expr) -> str:
    return sp.sstr(sp.factor(sp.cancel(value)))


def build_document() -> dict:
    J = derive_rational_radius_current(sp.Integer(4))
    omega = next(symbol for symbol in J.free_symbols if symbol.name == "omega")
    antihermitian = all(
        sp.simplify(J[i, j] + real_conjugate(J[j, i], omega)) == 0
        for i in range(6) for j in range(6)
    )
    if not antihermitian:
        raise RuntimeError("radial current is not anti-Hermitian")

    determinant = sp.factor(J.det())
    permutation = [2, 0, 1, 3, 4, 5]
    H_anchor = (-sp.I * J).subs(omega, sp.Rational(1, 2)).extract(
        permutation, permutation)
    previous = sp.Integer(1)
    pivots: list[sp.Expr] = []
    for size in range(1, 7):
        minor = sp.factor(H_anchor[:size, :size].det())
        pivots.append(sp.factor(minor / previous))
        previous = minor
    inertia = [sum(1 for pivot in pivots if pivot.is_positive),
               sum(1 for pivot in pivots if pivot.is_negative)]
    if inertia != [3, 3]:
        raise RuntimeError(f"unexpected anchor inertia {inertia}")

    imports = {
        name: {"path": path, "sha256": sha256(ROOT / path)}
        for name, path in INPUTS.items()
    }
    return {
        "schema": "phase3-black-hole-axial-null-infinity-trace-preflight-v1",
        "result_id": "PURE_WEYL_PHASE3_AXIAL_NULL_INFINITY_TRACE_PREFLIGHT_V1",
        "result_token": "RADIAL_CURRENT_EXACT_NULL_POLARIZATIONS_SEPARATED_WAVEPACKET_TRACE_OPEN",
        "lifecycle": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "declaration": {
            "theory": "strict linearized four-dimensional pure Weyl C^2 gravity",
            "background": "Schwarzschild exterior with M=1 in ingoing Eddington-Finkelstein coordinates",
            "sector": "axial ell=2, exp(+I*omega*v), real omega in [1/2,3/4]",
            "state_order": ["P", "dP/dr", "Q", "dQ/dr", "H1", "F"],
            "match_radius": "r=4",
        },
        "exact_radial_current": {
            "definition": "F^r(y,bar(z)) = pi*alpha_W*z^dagger*Jhat*y",
            "matrix_without_pi_alpha": [[expr(J[i, j]) for j in range(6)] for i in range(6)],
            "antihermitian": antihermitian,
            "determinant": expr(determinant),
            "real_frequency_rank": 6,
            "hermitian_form": "H=-I*pi*alpha_W*Jhat for the boundary convention I*F^r(bar(z),y), alpha_W>0",
            "anchor_permutation": permutation,
            "anchor_ldl_pivots_without_pi_alpha": [expr(value) for value in pivots],
            "anchor_inertia": inertia,
            "pilot_interval_inertia": [3, 3],
            "conservation_identity": "dJ/dr + A(-omega)^T*J + J*A(omega) = 0",
        },
        "endpoint_polarizations": {
            "horizon_column_order": ["XH0a", "XH0b", "XHplus", "XHminus", "EH0", "EHout"],
            "future_horizon_regular_columns": [0, 1, 4],
            "future_horizon_regular_dimension": 3,
            "infinity_column_order": ["XI0", "XI1", "XI2", "XI3", "EI0", "EI2"],
            "Iminus_incoming_rate_zero": ["XI0", "XI1", "EI0"],
            "Iplus_outgoing_rate_minus_2Iomega": ["XI2", "XI3", "EI2"],
            "phase_identity": "exp(I*omega*v)*exp(-2*I*omega*r)*r^(-4*I*omega) = 2^(-4*I*omega)*(1-2/r)^(4*I*omega)*exp(I*omega*u)",
            "warning": "The Iminus and Iplus polarizations are different endpoint traces and must not be cross-tested as one six-dimensional improper-density domain.",
        },
        "current_and_topology_distinction": {
            "coordinate_pullback": {
                "u": "F^u=F^t-B^(-1)*F^r",
                "v": "F^v=F^t+B^(-1)*F^r",
                "B": "1-2/r",
            },
            "radial_flux": "For two exact same-frequency on-shell solutions, F^r is independent of r; finite amplitudes therefore do not define a nontrivial radial-divergence map.",
            "raw_Fv": "The improper integral of the ingoing-EF component F^v on a v-adapted slice is a Cauchy-density diagnostic, not the flux through future or past null infinity.",
            "wave_packets": "A physical null trace must be defined after frequency superposition, separately at Iplus and Iminus, with a declared energy/flux topology.",
            "all_six_raw_test_disposition": "INVALID_ENDPOINT_MIXING",
        },
        "connection_conservation": {
            "common_radius_basis_relation": "B_H=B_I*T",
            "coordinate_orientation": "T^dagger*H_I*T=H_H",
            "outward_boundary_orientation": "T^dagger*H_I_out*T+H_H_out=0",
            "connection_matrix_status": "NOT_CONSTRUCTED",
        },
        "first_missing_estimate": {
            "status": "CERTIFIED_MISSING_DEPENDENCY",
            "statement": "Uniform joint (r,omega) bounds for the reconstructed endpoint expansions and their omega derivatives, followed by a stationary-phase/integration-by-parts estimate proving existence and continuity of the Iplus/Iminus wave-packet trace and Lee-Wald flux.",
            "required_output": "A bounded trace operator from a declared Schwartz or finite-energy spectral profile to separate Iplus and Iminus radiation data, with a finite conserved quadratic flux.",
            "why_formal_heads_are_insufficient": "Fixed-frequency polyhomogeneous heads do not control frequency integration, endpoint thresholds, omega derivatives, or the interchange of the r-to-infinity limit with the spectral integral.",
        },
        "imports": imports,
        "claim_flags": {
            "exact_six_state_radial_current": True,
            "radial_current_nondegenerate_on_pilot": True,
            "future_horizon_regular_selector": True,
            "null_infinity_phase_polarizations": True,
            "raw_Fv_rejected_as_null_flux": True,
            "wavepacket_trace_constructed": False,
            "global_connection_constructed": False,
            "scattering_channels_classified": False,
            "stability_or_CPT_established": False,
        },
        "does_not_establish": [
            "a wave-packet radiation phase space at Iplus or Iminus",
            "horizon-to-infinity matching or a global connection matrix",
            "a Schwarzschild scattering matrix or its flux inertia",
            "mode stability, pole exclusion, CPT positivity, particles, or quantum unitarity",
        ],
        "verification": {
            "producer": "python3 -m black_hole_programme.phase3.axial_null_infinity_trace_preflight.produce --check",
            "verifier": "python3 -m black_hole_programme.phase3.axial_null_infinity_trace_preflight.verify",
            "tests": "python3 -m pytest -q black_hole_programme/phase3/axial_null_infinity_trace_preflight/tests",
        },
    }


def write_document() -> dict:
    doc = build_document()
    OUTPUT.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n")
    receipt = {
        "schema": "phase3-black-hole-axial-null-infinity-trace-preflight-receipt-v1",
        "certificate": str(OUTPUT.relative_to(ROOT)),
        "certificate_sha256": sha256(OUTPUT),
        "producer_sha256": sha256(Path(__file__)),
        "schema_sha256": sha256(SCHEMA),
        "status": "PASS",
        "higher_tiers_not_run": "The package changes no shared operator; the imported exact operator hashes are frozen.",
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    return doc


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        expected = build_document()
        actual = json.loads(OUTPUT.read_text())
        if expected != actual:
            raise SystemExit("certificate drift")
        print("PASS: axial null-infinity trace preflight reproduces exactly")
    else:
        write_document()
        print(f"wrote {OUTPUT}")


if __name__ == "__main__":
    main()
