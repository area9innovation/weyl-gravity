#!/usr/bin/env python3
"""Produce the Phase-3 validated-connection substrate preflight.

The numerical calculation in this file is deliberately *unvalidated*.  Its
purpose is to exercise the actual axial reconstruction ODE and quantify what
would have to be enclosed.  The scientific result of this work item is the
API/capability obstruction recorded beside it, not the displayed digits.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

import mpmath as mp


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
FORGE_ROOT = Path("/home/alstrup/area9/tango/forge")
OUTPUT = HERE / "certificate.json"
SCHEMA = HERE / "schema.json"

IVODE = FORGE_ROOT / "lib/math/ivode.forge"
IVMAT = FORGE_ROOT / "lib/math/ivmat.forge"
INTERVAL = FORGE_ROOT / "lib/math/interval.forge"
COMPLETENESS = FORGE_ROOT / "lib/math/COMPLETENESS.md"
WORK_ITEM = ROOT / "planning/work-items/phase3-validated-connection-substrate-preflight.json"

SCHEMA_NAME = "phase3-validated-connection-substrate-preflight-v1"
RESULT_ID = "PURE_WEYL_PHASE3_VALIDATED_CONNECTION_SUBSTRATE_PREFLIGHT"
RESULT_TOKEN = "BLOCKED_MISSING_VALIDATED_COUPLED_FUNDAMENTAL_FLOW"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def forge_commit() -> str:
    return subprocess.check_output(
        ["git", "-C", str(FORGE_ROOT), "rev-parse", "HEAD"], text=True
    ).strip()


def rhs(r: mp.mpf, y: list[mp.mpc], omega: mp.mpf) -> list[mp.mpc]:
    """First-order form of the certified axial/polar reconstruction master ODE."""
    f, fp = y
    c2 = r * r - 2 * r
    c1 = 2j * omega * r * r + 2 * r + 2
    c0 = 6j * omega * r - 6
    return [fp, -(c1 * fp + c0 * f) / c2]


def rk4_column(n: int, initial: tuple[int, int], omega: mp.mpf) -> list[mp.mpc]:
    a, b = mp.mpf(3), mp.mpf(4)
    h = (b - a) / n
    r = a
    y = [mp.mpc(initial[0]), mp.mpc(initial[1])]
    for _ in range(n):
        k1 = rhs(r, y, omega)
        k2 = rhs(r + h / 2, [y[i] + h * k1[i] / 2 for i in range(2)], omega)
        k3 = rhs(r + h / 2, [y[i] + h * k2[i] / 2 for i in range(2)], omega)
        k4 = rhs(r + h, [y[i] + h * k3[i] for i in range(2)], omega)
        y = [y[i] + h * (k1[i] + 2 * k2[i] + 2 * k3[i] + k4[i]) / 6 for i in range(2)]
        r += h
    return y


def fundamental(n: int, omega: mp.mpf) -> mp.matrix:
    cols = [rk4_column(n, (1, 0), omega), rk4_column(n, (0, 1), omega)]
    return mp.matrix([[cols[j][i] for j in range(2)] for i in range(2)])


def p_integral(omega: mp.mpf) -> mp.mpc:
    # Integral from 3 to 4 of
    # P=(2*i*w*r^2+2*r+2)/(r^2-2*r).
    return -mp.log(mp.mpf(4) / 3) + 3 * mp.log(2) + 2j * omega * (1 + 2 * mp.log(2))


def current_defect(phi: mp.matrix, omega: mp.mpf) -> mp.matrix:
    j0 = mp.matrix([[0, 1], [-1, 0]])
    j1 = mp.e ** p_integral(omega) * j0
    return phi.transpose() * j1 * phi - j0


def maxabs(a: mp.matrix) -> mp.mpf:
    return max(abs(a[i, j]) for i in range(a.rows) for j in range(a.cols))


def encode_complex(z: mp.mpc, digits: int = 40) -> dict[str, str]:
    return {"re": mp.nstr(mp.re(z), digits), "im": mp.nstr(mp.im(z), digits)}


def encode_matrix(a: mp.matrix, digits: int = 40) -> list[list[dict[str, str]]]:
    return [[encode_complex(a[i, j], digits) for j in range(a.cols)] for i in range(a.rows)]


def build() -> dict:
    mp.mp.dps = 80
    omega = mp.mpf(3) / 5
    ns = [256, 512, 1024]
    phis = {n: fundamental(n, omega) for n in ns}
    defects = {n: current_defect(phis[n], omega) for n in ns}

    # A deliberately ill-conditioned exact outer basis.  It is not asserted to
    # be a physical infinity basis; it measures the amplification that the
    # eventual certified endpoint basis solve must enclose.
    eps = mp.mpf(1) / 1000
    bout = mp.matrix([[1, 1], [1, 1 + eps]])
    bout_inv = bout ** -1
    connections = {n: bout_inv * phis[n] for n in ns}
    phi_delta = maxabs(phis[1024] - phis[512])
    conn_delta = maxabs(connections[1024] - connections[512])

    # Decimal-indistinguishability control.  Normalize the best approximate
    # fundamental matrix onto the exact 2x2 Wronskian identity, then perturb one
    # entry below the printed precision.  Both matrices print identically, but
    # only one has the imposed conservation identity.  Thus rounded agreement
    # can never certify a zero current defect.
    target_det = mp.e ** (-p_integral(omega))
    normalized = phis[1024] * mp.sqrt(target_det / mp.det(phis[1024]))
    mutated = mp.matrix(normalized)
    decimal_delta = mp.mpf("1e-15")
    mutated[0, 0] += decimal_delta
    fmt = lambda z: f"{float(mp.re(z)):.12g},{float(mp.im(z)):.12g}"
    same_print = all(
        fmt(normalized[i, j]) == fmt(mutated[i, j]) for i in range(2) for j in range(2)
    )

    paths = [IVODE, IVMAT, INTERVAL, COMPLETENESS]
    provenance = {
        str(p.relative_to(FORGE_ROOT)): {"sha256": sha256(p)} for p in paths
    }

    return {
        "schema": SCHEMA_NAME,
        "result_id": RESULT_ID,
        "result_token": RESULT_TOKEN,
        "lifecycle": "OBSTRUCTED",
        "dependency_tags": ["REDUCED-MODE"],
        "declaration": {
            "theory": "pure Weyl gravity",
            "background": "Schwarzschild, M=1",
            "sector": "representative l=2 axial reconstruction master equation",
            "frequency": "center hat_omega=M*omega=3/5 of frozen downstream interval [1/2,3/4]",
            "radial_box": ["3", "4"],
            "basis": "identity at r=3; exact rational conditioning stress basis [[1,1],[1,1001/1000]] at r=4",
            "claim_kind": "SUBSTRATE_CAPABILITY_OBSTRUCTION",
        },
        "axial_system": {
            "ode": "(r^2-2r)F''+(2*i*omega*r^2+2r+2)F'+(6*i*omega*r-6)F=0",
            "first_order": "Y'=[[0,1],[-c0/c2,-c1/c2]]Y",
            "current": "J(r)=exp(integral_3^r(c1/c2)ds)*[[0,1],[-1,0]]",
            "conservation_identity": "Phi(r)^T J(r) Phi(r)=J(3)",
            "provenance": "BH2C_METRIC_ALL_ORDERS certified master ODE; this preflight does not promote it to a global scattering equation",
        },
        "landed_capabilities": {
            "scalar_validated_ivp": {
                "available": True,
                "signature": "ode_integrate(f: fn(Iv, Iv) -> Iv, t0: f64, y0: Iv, t_end: f64, n: i64) -> Option<OdeCert>",
            },
            "interval_matrix_algebra": {"available": True, "module": "math/ivmat"},
            "exact_rational_center_solve": {"available": True, "module": "math/ivmat"},
            "coupled_vector_validated_ivp": {"available": False},
            "validated_fundamental_matrix": {"available": False},
            "validated_complex_ivp": {"available": False, "note": "real block representation is sufficient once vector IVP exists"},
            "wrapping_control": {"available": False},
            "validated_boundary_value_connection": {"available": False},
            "certified_endpoint_series_remainder": {"available": False},
        },
        "uncontrolled_pilot": {
            "method": "80-decimal fixed-step RK4; no interval/truncation enclosure",
            "mpmath_version": mp.__version__,
            "steps": ns,
            "fundamental_matrix_n1024": encode_matrix(phis[1024]),
            "current_defect_max": {str(n): mp.nstr(maxabs(defects[n]), 18) for n in ns},
            "successive_fundamental_difference_max": mp.nstr(phi_delta, 18),
            "basis_condition_infinity_exact": "4004001/1000",
            "successive_connection_difference_max": mp.nstr(conn_delta, 18),
            "basis_error_amplification_observed": mp.nstr(conn_delta / phi_delta, 18),
            "evidence_status": "UNCONTROLLED_NUMERIC_OBSERVATION",
        },
        "rounded_output_counterexample": {
            "printed_digits": 12,
            "entry_perturbation": mp.nstr(decimal_delta, 5),
            "same_printed_matrix": same_print,
            "normalized_current_defect_max": mp.nstr(maxabs(current_defect(normalized, omega)), 18),
            "mutated_current_defect_max": mp.nstr(maxabs(current_defect(mutated, omega)), 18),
            "conclusion": "matching printed digits and a small residual cannot certify current conservation",
        },
        "obstruction": {
            "minimal_missing_primitive": "validated real vector linear IVP with fundamental-matrix enclosure and wrapping control on a finite nonsingular interval",
            "reason": "the scalar Iv state cannot represent the coupled 4-real-dimensional axial flow or correlations among the 16 fundamental-matrix entries",
            "request": "planning/forge-requests/phase3-validated-connection-substrate.json",
            "broad_parent_request": "sf:forge-request/validated-vector-bvp-connection-flux",
        },
        "claim_flags": {
            "landed_substrate_audited": True,
            "representative_uncontrolled_flow_computed": True,
            "validated_fundamental_matrix_enclosed": False,
            "endpoint_basis_error_enclosed": False,
            "current_conservation_defect_enclosed": False,
            "global_connection_constructed": False,
            "scattering_claim": False,
        },
        "does_not_establish": [
            "a rigorous enclosure of any axial trajectory or connection coefficient",
            "endpoint Frobenius or infinity-series truncation bounds",
            "horizon-to-infinity matching, finite flux, scattering, stability or positivity",
            "failure of a future validated solver; the result identifies the first missing primitive",
        ],
        "provenance": {
            "forge_commit": forge_commit(),
            "forge_sources": provenance,
            "physics_input_commit": json.loads(WORK_ITEM.read_text())["body"]["input_commit"],
            "work_item_sha256": sha256(WORK_ITEM),
        },
        "verification": {
            "producer": "python3 black_hole_programme/phase3/validated_connection_preflight/produce.py --check",
            "independent": "python3 black_hole_programme/phase3/validated_connection_preflight/verify.py",
            "mutation": "python3 black_hole_programme/phase3/validated_connection_preflight/verify.py --self-test-mutation",
            "forge_gate": "FORGE_LIB=/home/alstrup/area9/tango/forge/lib forge -test black_hole_programme/phase3/validated_connection_preflight",
        },
    }


def canonical_bytes(payload: dict) -> bytes:
    return (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    data = canonical_bytes(build())
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_bytes() != data:
            raise SystemExit("certificate drift")
        print("PASS producer replay")
        return 0
    OUTPUT.write_bytes(data)
    print(OUTPUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
