#!/usr/bin/env python3
"""Support-local minimal BV clock contraction on the positive Berger phase.

At the rotating Berger background define normalized clock fluctuations

    Theta = delta(theta)/omega,       R = delta(rho)/rho_bar.

For the temporal diffeomorphism ghost tau and Weyl ghost sigma,

    q tau = Theta,                    q sigma = -R.

The differential field redefinition

    h_hat = h - L_{Theta n} g_bar + 2 R g_bar

removes both gauge columns from the metric row.  Since the background is a
static product, n is parallel and this transformation is a first-order local
operator with a first-order local inverse.  Its cotangent lift is BV
canonical.  Gauge invariance and formal self-adjointness then split the
quadratic Hessian into a retained dressed-metric block and two zero clock
rows, so the two field/ghost doublets and their antifield duals contract.

This certificate includes every *minimal* clock-dual row.  It deliberately
does not claim the retained dressed-metric Hessian coefficients, gauge-fixed
nonminimal rows, Green hyperbolicity, or stability.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp

try:
    from d_quotient_classical.backreacted_clock.berger_retained_minimal_layout import (
        BergerRetainedMinimalLayout,
    )
except ModuleNotFoundError:  # Direct script execution from its own directory.
    from berger_retained_minimal_layout import BergerRetainedMinimalLayout


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE_PATH = (
    ROOT
    / "d_quotient_classical"
    / "certificates"
    / "BERGER_MINIMAL_BV_CLOCK_SDR.json"
)
REPORT_PATH = (
    ROOT
    / "d_quotient_classical"
    / "reports"
    / "berger-minimal-bv-clock-sdr.md"
)
SCHEMA_PATH = (
    ROOT
    / "d_quotient_classical"
    / "schema"
    / "berger-minimal-bv-clock-sdr-v1.schema.json"
)


def _matrix_digest(matrix: sp.MatrixBase) -> str:
    payload = {
        "shape": list(matrix.shape),
        "entries": [
            [row, column, str(sp.factor(value))]
            for (row, column), value in sorted(
                sp.SparseMatrix(matrix).todok().items()
            )
        ],
    }
    encoded = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode()
    return hashlib.sha256(encoded).hexdigest()


def _exact_matrices() -> dict[str, Any]:
    eta = sp.diag(-1, 1, 1, 1)
    pairs = tuple((mu, nu) for mu in range(4) for nu in range(mu, 4))
    p = sp.Matrix(sp.symbols("p0:4", real=True))
    rho, omega = sp.symbols("rho omega", nonzero=True, real=True)

    # The unit future normal is n^mu=(1,0,0,0), hence n_mu=(-1,0,0,0).
    n_cov = sp.Matrix([-1, 0, 0, 0])
    metric_vector = sp.Matrix([eta[mu, nu] for mu, nu in pairs])
    temporal_gauge = sp.Matrix(
        [p[mu] * n_cov[nu] + p[nu] * n_cov[mu] for mu, nu in pairs]
    )
    spatial_gauge = sp.zeros(10, 3)
    for row, (mu, nu) in enumerate(pairs):
        for spatial in range(3):
            index = spatial + 1
            spatial_gauge[row, spatial] = (
                p[mu] * (1 if nu == index else 0)
                + p[nu] * (1 if mu == index else 0)
            )
    weyl_gauge = 2 * metric_vector

    # Old field order: (h_10, delta_rho, delta_theta).
    # New field order: (h_hat_10, R, Theta).
    field_map = sp.eye(12)
    field_map[:10, 10] = 2 * metric_vector / rho
    field_map[:10, 11] = -temporal_gauge / omega
    field_map[10, 10] = 1 / rho
    field_map[11, 11] = 1 / omega
    if sp.factor(field_map.det()) != 1 / (rho * omega):
        raise AssertionError("clock field map determinant drifted")

    # Ghost order: (xi_perp^1,xi_perp^2,xi_perp^3,tau,sigma).
    old_gauge = sp.zeros(12, 5)
    old_gauge[:10, :3] = spatial_gauge
    old_gauge[:10, 3] = temporal_gauge
    old_gauge[:10, 4] = weyl_gauge
    old_gauge[10, 4] = -rho
    old_gauge[11, 3] = omega
    new_gauge = sp.simplify(field_map * old_gauge)
    expected_gauge = sp.zeros(12, 5)
    expected_gauge[:10, :3] = spatial_gauge
    expected_gauge[10, 4] = -1
    expected_gauge[11, 3] = 1
    if new_gauge != expected_gauge:
        raise AssertionError("dressed metric did not remove temporal/Weyl columns")

    # Full minimal coordinate order is ghosts_5, fields_12, antifields_12,
    # ghost-antifields_5.  The cotangent lift uses F^{-T} on antifields.
    total_dimension = 34
    canonical_pairing = sp.zeros(total_dimension)
    ghost_slice = slice(0, 5)
    field_slice = slice(5, 17)
    antifield_slice = slice(17, 29)
    ghost_antifield_slice = slice(29, 34)
    canonical_pairing[ghost_slice, ghost_antifield_slice] = sp.eye(5)
    canonical_pairing[ghost_antifield_slice, ghost_slice] = -sp.eye(5)
    canonical_pairing[field_slice, antifield_slice] = sp.eye(12)
    canonical_pairing[antifield_slice, field_slice] = -sp.eye(12)

    canonical_map = sp.eye(total_dimension)
    canonical_map[field_slice, field_slice] = field_map
    canonical_map[antifield_slice, antifield_slice] = field_map.inv().T
    transformed_pairing = sp.simplify(
        canonical_map.inv().T * canonical_pairing * canonical_map.inv()
    )
    if transformed_pairing != canonical_pairing:
        raise AssertionError("clock field transformation is not BV canonical")

    # Isolated clock order:
    # (tau,sigma,Theta,R,Theta*,R*,tau*,sigma*).
    incidence = sp.diag(1, -1)
    q_clock = sp.zeros(8)
    q_clock[2:4, 0:2] = incidence
    q_clock[6:8, 4:6] = -incidence.T
    omega_clock = sp.zeros(8)
    omega_clock[0:2, 6:8] = sp.eye(2)
    omega_clock[6:8, 0:2] = -sp.eye(2)
    omega_clock[2:4, 4:6] = sp.eye(2)
    omega_clock[4:6, 2:4] = -sp.eye(2)
    homotopy = sp.zeros(8)
    homotopy[0:2, 2:4] = incidence.inv()
    homotopy[4:6, 6:8] = -incidence.T.inv()
    identity = sp.eye(8)
    zero = sp.zeros(8)
    if q_clock * q_clock != zero:
        raise AssertionError("clock q1 is not nilpotent")
    if sp.simplify(q_clock.T * omega_clock + omega_clock * q_clock) != zero:
        raise AssertionError("clock q1 is not cyclic")
    if sp.simplify(q_clock * homotopy + homotopy * q_clock) != identity:
        raise AssertionError("clock contraction identity failed")
    if homotopy * homotopy != zero:
        raise AssertionError("clock homotopy is not square zero")
    if sp.simplify(homotopy.T * omega_clock + omega_clock * homotopy) != zero:
        raise AssertionError("clock homotopy is not cyclic")

    fixture = {
        rho: 1,
        omega: sp.Rational(3, 4),
        p[0]: 2,
        p[1]: 1,
        p[2]: 0,
        p[3]: 0,
    }
    if sp.factor(field_map.det().subs(fixture)) != sp.Rational(4, 3):
        raise AssertionError("rational clock field-map fixture drifted")
    if old_gauge.subs(fixture).rank() != 5 or new_gauge.subs(fixture).rank() != 5:
        raise AssertionError("rational clock incidence lost rank")

    return {
        "field_map": field_map,
        "old_gauge": old_gauge,
        "new_gauge": new_gauge,
        "canonical_map": canonical_map,
        "canonical_pairing": canonical_pairing,
        "q_clock": q_clock,
        "omega_clock": omega_clock,
        "homotopy": homotopy,
        "fixture_field_map": field_map.subs(fixture),
    }


@dataclass(frozen=True)
class BergerMinimalBVClockSDR:
    payload: dict[str, Any]

    @classmethod
    def build(cls) -> "BergerMinimalBVClockSDR":
        matrices = _exact_matrices()
        retained_layout = BergerRetainedMinimalLayout.build()
        payload: dict[str, Any] = {
            "schema": "pure-weyl-berger-minimal-bv-clock-sdr-v1",
            "result_id": "BERGER_MINIMAL_BV_CLOCK_SDR",
            "setting_id": "compact_positive_berger_clock_fixed_coupling_linearized",
            "phase_space_id": "positive_berger_fixed_coupling_linearized_solutions",
            "claim_status": "CERTIFIED_MINIMAL_CLOCK_SECTOR_SDR",
            "dependency_tags": ["LOCAL-ALGEBRAIC"],
            "background_inputs": {
                "rho_nonzero": True,
                "omega_nonzero": True,
                "normal_parallel": "n=partial_t is parallel on the static product Berger cylinder",
                "fixed_coupling_D_verdict": "D_GAUGE",
            },
            "field_coordinates": {
                "normalized_phase": "Theta=delta(theta)/omega",
                "normalized_modulus": "R=delta(rho)/rho_bar",
                "dressed_metric": "h_hat=h-L_{Theta n}g_bar+2R g_bar",
                "inverse": "h=h_hat+L_{Theta n}g_bar-2R g_bar; delta(rho)=rho_bar R; delta(theta)=omega Theta",
                "determinant": "1/(rho_bar omega)",
                "maximum_differential_order": 1,
                "support_local": True,
            },
            "gauge_incidence": {
                "ghost_split": "xi=xi_perp+tau n together with Weyl ghost sigma",
                "raw": [
                    "K1(xi_perp,tau,sigma)=(L_{xi_perp}g_bar+L_{tau n}g_bar+2 sigma g_bar,-rho_bar sigma,omega tau)",
                ],
                "dressed": [
                    "q1(xi_perp)=L_{xi_perp}g_bar",
                    "q1(tau)=Theta",
                    "q1(sigma)=-R",
                ],
                "clock_incidence_matrix": [[1, 0], [0, -1]],
                "clock_incidence_determinant": -1,
                "temporal_and_weyl_columns_removed_from_metric": True,
            },
            "canonical_antifield_lift": {
                "metric": "h_hat*=h*",
                "phase": "Theta*=omega theta*+K_t^sharp h*",
                "modulus": "R*=rho_bar rho*-2 tr_g(h*)",
                "temporal_operator": "K_t Theta=L_{Theta n}g_bar",
                "formal_adjoint": "K_t^sharp h*=-2 n_nu nabla_mu h*^(mu nu)",
                "canonical_pairing_preserved": True,
                "maximum_differential_order": 1,
            },
            "minimal_row_layout": [
                {"degree": -1, "dimension": 3, "name": "spatial_diff_ghost", "retained": True},
                {"degree": -1, "dimension": 1, "name": "temporal_diff_ghost_tau", "retained": False},
                {"degree": -1, "dimension": 1, "name": "weyl_ghost_sigma", "retained": False},
                {"degree": 0, "dimension": 10, "name": "dressed_metric_h_hat", "retained": True},
                {"degree": 0, "dimension": 1, "name": "clock_phase_Theta", "retained": False},
                {"degree": 0, "dimension": 1, "name": "clock_modulus_R", "retained": False},
                {"degree": 1, "dimension": 10, "name": "dressed_metric_antifield", "retained": True},
                {"degree": 1, "dimension": 1, "name": "clock_phase_antifield", "retained": False},
                {"degree": 1, "dimension": 1, "name": "clock_modulus_antifield", "retained": False},
                {"degree": 2, "dimension": 3, "name": "spatial_diff_ghost_antifield", "retained": True},
                {"degree": 2, "dimension": 1, "name": "temporal_diff_ghost_antifield", "retained": False},
                {"degree": 2, "dimension": 1, "name": "weyl_ghost_antifield", "retained": False},
            ],
            "clock_block": {
                "ordered_rows": ["tau", "sigma", "Theta", "R", "Theta*", "R*", "tau*", "sigma*"],
                "q1_maps": [
                    "q1(tau)=Theta",
                    "q1(sigma)=-R",
                    "q1(Theta*)=-tau*",
                    "q1(R*)=sigma*",
                ],
                "homotopy_maps": [
                    "s(Theta)=tau",
                    "s(R)=-sigma",
                    "s(tau*)=-Theta*",
                    "s(sigma*)=R*",
                ],
                "identities": [
                    "q1^2=0",
                    "q1 s+s q1=1_clock",
                    "s^2=0",
                    "q1^T Omega+Omega q1=0",
                    "s^T Omega+Omega s=0",
                ],
                "minimal_clock_rows_complete": True,
            },
            "hessian_split_argument": {
                "input": "the coupled background solves the Euler-Lagrange equations and the quadratic Hessian is formally self-adjoint",
                "noether_statement": "H R_gauge=0",
                "consequence": "in dressed variables the Theta and R columns vanish; formal self-adjointness makes their rows vanish, so H=H_retained direct_sum 0_clock",
                "retained_operator": "the actual ten-component dressed-metric Hessian H_retained",
                "retained_coefficients_emitted": False,
            },
            "sdr": {
                "full_minimal_dimension": 34,
                "contracted_clock_dimension": 8,
                "retained_minimal_dimension": 26,
                "projection": "delete tau,sigma,Theta,R and their four BV-dual rows in dressed coordinates",
                "inclusion": "set those eight clock coordinates to zero",
                "identity": "i p=1-q1 s-s q1",
                "support_preservation": "all entries are algebraic or first-order differential operators and obey supp(Tu) subset supp(u)",
                "support_categories": ["compact", "spacelike-compact", "smooth"],
            },
            "retained_layout_ref": {
                "result_id": retained_layout.payload["result_id"],
                "schema": retained_layout.payload["schema"],
                "payload_sha256": retained_layout.digest,
                "component_count": len(retained_layout.payload["component_rows"]),
                "immediate_gate": retained_layout.payload["gate_split"]["immediate_gate"],
                "subsequent_gate": retained_layout.payload["gate_split"]["subsequent_gate"],
            },
            "operator_fingerprints": {
                name: _matrix_digest(matrices[name])
                for name in (
                    "field_map",
                    "old_gauge",
                    "new_gauge",
                    "canonical_map",
                    "canonical_pairing",
                    "q_clock",
                    "omega_clock",
                    "homotopy",
                    "fixture_field_map",
                )
            },
            "rational_fixture": {
                "rho_bar": "1",
                "omega": "3/4",
                "symbol_covector": "p=(2,1,0,0)",
                "field_map_determinant": "4/3",
                "raw_gauge_rank": 5,
                "dressed_gauge_rank": 5,
            },
            "flags": {
                "minimal_clock_field_ghost_rows_complete": True,
                "minimal_clock_antifield_identity_rows_complete": True,
                "canonical_antifield_transformation_exact": True,
                "support_local_clock_SDR_exact": True,
                "retained_dressed_metric_q1_coefficients_complete": False,
                "gauge_fixed_nonminimal_rows_complete": False,
                "retained_operator_stability_proved": False,
                "causal_green_homotopy_constructed": False,
                "full_Berger_clock_BV_theorem": False,
            },
            "next_gate": "BERGER_RETAINED_MINIMAL_OPERATOR",
            "not_established": [
                "the coefficientwise ten-component dressed-metric Hessian and its Noether row",
                "the gauge-fixed antighost, multiplier, and auxiliary rows",
                "the kinetic-sign and characteristic audit of the retained operator",
                "retarded or advanced Green homotopies",
                "nonlinear q2 or the parked CLASSICAL_SUPPORT_LOCAL_Q1_Q2_EXPORT",
            ],
            "claim_boundary": "The theorem constructs the exact support-local cyclic SDR of the temporal-diffeomorphism/Weyl clock doublets and all their minimal BV-dual rows on the rho_bar*omega nonzero Berger chart. It does not emit the retained dressed-metric Hessian coefficients, nonminimal gauge-fixed rows, Green homotopies, stability, nonlinear operations, or a complete classical export.",
        }
        result = cls(payload)
        result.verify()
        return result

    def verify(self) -> None:
        p = self.payload
        required = {
            "schema", "result_id", "setting_id", "phase_space_id",
            "claim_status", "dependency_tags", "background_inputs",
            "field_coordinates", "gauge_incidence", "canonical_antifield_lift",
            "minimal_row_layout", "clock_block", "hessian_split_argument",
            "sdr", "operator_fingerprints", "rational_fixture", "flags",
            "retained_layout_ref", "next_gate", "not_established", "claim_boundary",
        }
        if set(p) != required:
            raise AssertionError("Berger minimal clock SDR key set drifted")
        flags = p["flags"]
        for key in (
            "minimal_clock_field_ghost_rows_complete",
            "minimal_clock_antifield_identity_rows_complete",
            "canonical_antifield_transformation_exact",
            "support_local_clock_SDR_exact",
        ):
            if flags[key] is not True:
                raise AssertionError(f"proved minimal clock flag dropped: {key}")
        for key in (
            "retained_dressed_metric_q1_coefficients_complete",
            "gauge_fixed_nonminimal_rows_complete",
            "retained_operator_stability_proved",
            "causal_green_homotopy_constructed",
            "full_Berger_clock_BV_theorem",
        ):
            if flags[key] is not False:
                raise AssertionError(f"open Berger BV flag promoted: {key}")
        if p["sdr"]["full_minimal_dimension"] != 34:
            raise AssertionError("minimal row dimension drifted")
        if p["sdr"]["contracted_clock_dimension"] != 8:
            raise AssertionError("clock contraction dimension drifted")
        layout = BergerRetainedMinimalLayout.build()
        if p["retained_layout_ref"]["payload_sha256"] != layout.digest:
            raise AssertionError("retained layout fingerprint drifted")
        if p["retained_layout_ref"]["component_count"] != 26:
            raise AssertionError("retained layout component count drifted")
        if p["retained_layout_ref"]["subsequent_gate"] != "BERGER_NONMINIMAL_COMPLETION":
            raise AssertionError("retained/nonminimal gate split drifted")
        if p["next_gate"] != "BERGER_RETAINED_MINIMAL_OPERATOR":
            raise AssertionError("Berger clock next gate drifted")

    def certificate_text(self) -> str:
        return json.dumps(self.payload, indent=2, sort_keys=True) + "\n"

    def report_text(self) -> str:
        return r"""# Support-local minimal BV contraction of the Berger clock

The positive Berger clock fixes the temporal-diffeomorphism and Weyl gauge
directions locally.  Normalize its two scalar fluctuations by

\[
\Theta=\frac{\delta\theta}{\omega},
\qquad
R=\frac{\delta\rho}{\bar\rho}.
\]

In the shifted BV-complex convention used here, if \(\tau\) is the temporal
diffeomorphism ghost and \(\sigma\) the Weyl ghost, then

\[
q_1\tau=\Theta,
\qquad
q_1\sigma=-R.
\]

The dressed metric

\[
\widehat h=h-\mathcal L_{\Theta n}\bar g+2R\bar g
\]

has gauge incidence

\[
K_1^{\rm dressed}(\xi_\perp,\tau,\sigma)
=\mathcal L_{\xi_\perp}\bar g
\quad\text{in the metric row}.
\]

Thus its temporal and Weyl gauge columns vanish exactly.  The transformation
is first-order and support-local.  Its inverse is

\[
h=\widehat h+\mathcal L_{\Theta n}\bar g-2R\bar g.
\]

The cotangent lift is BV canonical:

\[
\widehat h^*=h^*,
\qquad
\Theta^*=\omega\theta^*+K_t^\sharp h^*,
\qquad
R^*=\bar\rho\rho^*-2\operatorname{tr}_{\bar g}h^*,
\]

where

\[
K_t\Theta=\mathcal L_{\Theta n}\bar g,
\qquad
K_t^\sharp h^*=-2n_\nu\nabla_\mu h^{*\mu\nu}.
\]

In dressed coordinates the eight clock rows are

\[
(\tau,\sigma,\Theta,R,\Theta^*,R^*,\tau^*,\sigma^*).
\]

Their nonzero differential and homotopy maps are

\[
\begin{aligned}
q_1\tau&=\Theta,& q_1\sigma&=-R,
&q_1\Theta^*&=-\tau^*,&q_1R^*&=\sigma^*,\\
s\Theta&=\tau,&sR&=-\sigma,
&s\tau^*&=-\Theta^*,&s\sigma^*&=R^*.
\end{aligned}
\]

They satisfy exactly

\[
q_1^2=0,
\qquad
q_1s+sq_1=1_{\rm clock},
\qquad
s^2=0,
\]

and both \(q_1\) and \(s\) have the required cyclic adjoint relation.  The
full 34-dimensional minimal complex therefore retracts support-locally onto a
26-dimensional dressed-metric/spatial-diffeomorphism minimal complex.

This is the complete minimal clock-sector SDR, not the complete Berger BV
theorem.  The retained ten-component dressed-metric Hessian, nonminimal
gauge-fixed rows, stability analysis, and causal Green homotopies remain the
next gate: `BERGER_RETAINED_MINIMAL_OPERATOR`.  The nonminimal rows are a
separate subsequent gate, `BERGER_NONMINIMAL_COMPLETION`.
"""


def _write(result: BergerMinimalBVClockSDR) -> None:
    CERTIFICATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    CERTIFICATE_PATH.write_text(result.certificate_text())
    REPORT_PATH.write_text(result.report_text())


def _check(result: BergerMinimalBVClockSDR) -> None:
    result.verify()
    if CERTIFICATE_PATH.read_text() != result.certificate_text():
        raise AssertionError("Berger minimal clock SDR certificate drifted")
    if REPORT_PATH.read_text() != result.report_text():
        raise AssertionError("Berger minimal clock SDR report drifted")


def _guards(result: BergerMinimalBVClockSDR) -> None:
    mutations = [
        ("drop antifield rows", ("flags", "minimal_clock_antifield_identity_rows_complete"), False),
        ("break support locality", ("flags", "support_local_clock_SDR_exact"), False),
        ("promote retained q1", ("flags", "retained_dressed_metric_q1_coefficients_complete"), True),
        ("promote nonminimal", ("flags", "gauge_fixed_nonminimal_rows_complete"), True),
        ("promote stability", ("flags", "retained_operator_stability_proved"), True),
        ("promote Green homotopy", ("flags", "causal_green_homotopy_constructed"), True),
        ("promote full theorem", ("flags", "full_Berger_clock_BV_theorem"), True),
        ("skip next gate", ("next_gate",), "FULL_BERGER_CLOCK_THEOREM"),
    ]
    for name, path, value in mutations:
        payload = deepcopy(result.payload)
        target: Any = payload
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
        try:
            BergerMinimalBVClockSDR(payload).verify()
        except AssertionError:
            continue
        raise AssertionError(f"mutation guard failed: {name}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    result = BergerMinimalBVClockSDR.build()
    if args.check:
        _check(result)
    else:
        _write(result)
    if args.guards:
        _guards(result)
    print("BERGER_MINIMAL_BV_CLOCK_SDR: PASS")
    print("minimal clock rows: 8/8 contracted")
    print("retained q1/nonminimal/stability/Green: OPEN")


if __name__ == "__main__":
    main()
