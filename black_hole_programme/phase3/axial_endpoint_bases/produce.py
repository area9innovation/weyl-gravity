"""Exact Phase-3 axial endpoint-basis reconstruction gate.

The imported generic-ell Ricci carrier has a complete four-dimensional
formal endpoint basis.  This producer tests whether the imported metric
reconstruction is already complete enough to lift that basis.  It fails
closed at the first omitted equation: the advertised 3x3 metric system was
derived from the x-phi and r-phi Ricci rows and does not impose the v-phi
row.  Its polynomial generalized mode violates that row at ell=2 for every
real frequency in the frozen pilot interval.

No connection, flux, scattering, or stability statement is made here.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import sympy as sp

HERE = Path(__file__).resolve().parent
BH = HERE.parents[1]
ROOT = BH.parent
if str(BH) not in sys.path:
    sys.path.insert(0, str(BH))
CERTIFICATE = HERE / "certificate.json"
RECEIPT = HERE / "receipt.json"
SCHEMA = HERE / "schema.json"
REPAIR_INTERFACE = HERE / "repair-interface.json"

INPUTS = {
    "generic_axial_asymptotics": BH / "phase2/general_l_axial_asymptotics/certificate.json",
    "generic_axial_asymptotics_source": BH / "phase2/general_l_axial_asymptotics/general_l_axial_asymptotics.py",
    "corrected_axial_selection": BH / "phase2/general_l_axial_selection/certificate.json",
    "general_l_structural": BH / "certificates/BH2_GENERAL_L_STRUCTURAL.json",
    "linearized_bach": BH / "linearized_bach.py",
    "geometry": BH / "weyl_geometry.py",
}


class EndpointBasisError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise EndpointBasisError(message)


def cancel(expr):
    return sp.factor(sp.cancel(sp.together(expr)))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def axial_l2_vphi_row() -> tuple[sp.Expr, dict[str, sp.Symbol | sp.Function]]:
    """Derive delta Ric_{v phi}/S directly from delta Gamma.

    This deliberately does not call the linearized-Bach implementation.  The
    independent verifier uses that separate implementation as the second rail.
    The angular row is evaluated at x=1/2 after covariance guarantees that it
    is proportional to the nonzero l=2 axial harmonic S.
    """
    from weyl_geometry import Geometry

    v, r, x, ph = sp.symbols("v r x phi")
    omega = sp.Symbol("omega")
    B = 1 - 2 / r
    g = sp.zeros(4, 4)
    g[0, 0] = -B
    g[0, 1] = g[1, 0] = 1
    g[2, 2] = r**2 / (1 - x**2)
    g[3, 3] = r**2 * (1 - x**2)
    geo = Geometry([v, r, x, ph], g)
    gi, Gamma = geo.ginv, geo.Gamma
    h0 = sp.Function("h0")(v, r)
    h1 = sp.Function("h1")(v, r)
    S = -3 * x * (1 - x**2)
    h = sp.zeros(4, 4)
    h[0, 3] = h[3, 0] = h0 * S
    h[1, 3] = h[3, 1] = h1 * S

    dG = [[[sp.Integer(0)] * 4 for _ in range(4)] for _ in range(4)]
    for a in range(4):
        for b in range(4):
            for c in range(b, 4):
                value = sum(
                    gi[a, d] * (
                        geo.covd2(h, b, d, c)
                        + geo.covd2(h, c, b, d)
                        - geo.covd2(h, d, b, c)
                    )
                    for d in range(4) if gi[a, d] != 0
                ) / 2
                dG[a][b][c] = cancel(value)
                dG[a][c][b] = dG[a][b][c]

    def cov_dG(e: int, a: int, b: int, c: int):
        value = sp.diff(dG[a][b][c], [v, r, x, ph][e])
        for k in range(4):
            value += Gamma[a][e][k] * dG[k][b][c]
            value -= Gamma[k][e][b] * dG[a][k][c]
            value -= Gamma[k][e][c] * dG[a][b][k]
        return value

    # delta Ric_{v phi} = delta R^a_{v a phi}
    row = sum(cov_dG(a, a, 3, 0) - cov_dG(3, a, a, 0)
              for a in range(4))
    H0, H1 = sp.Function("H0")(r), sp.Function("H1")(r)
    phase = sp.exp(sp.I * omega * v)
    row = row.subs(x, sp.Rational(1, 2)) / S.subs(x, sp.Rational(1, 2))
    row = cancel(row.subs({h0: H0 * phase, h1: H1 * phase}).doit() / phase)
    return row, {"r": r, "omega": omega, "H0": H0, "H1": H1}


def expected_vphi_row(symbols: dict[str, sp.Symbol | sp.Function]) -> sp.Expr:
    r = symbols["r"]
    omega = symbols["omega"]
    H0 = symbols["H0"]
    H1 = symbols["H1"]
    I = sp.I
    return cancel((
        -omega**2 * r**3 * H1
        - I * omega * r**3 * sp.diff(H0, r)
        + I * omega * r**3 * sp.diff(H1, r)
        + 2 * I * omega * r**2 * H0
        + 2 * I * omega * r**2 * H1
        - 2 * I * omega * r**2 * sp.diff(H1, r)
        - 4 * I * omega * r * H1
        - r**3 * sp.diff(H0, r, 2)
        + 2 * r**2 * sp.diff(H0, r, 2)
        + 6 * r * H0 - 4 * H0
    ) / (2 * r**3))


def polynomial_mode_residual(row: sp.Expr, symbols: dict[str, sp.Symbol | sp.Function]):
    r = symbols["r"]
    omega = symbols["omega"]
    H0 = symbols["H0"]
    H1 = symbols["H1"]
    polynomial_h0 = -sp.I * omega * r + 2 + 2 / r
    residual = cancel(row.subs({H0: polynomial_h0, H1: 1}).doit())
    expected = 3 * sp.I * (omega - 2 * sp.I) / r**2
    require(sp.simplify(residual - expected) == 0,
            f"omitted-row residual changed: {residual}")
    return residual, polynomial_h0


def carrier_horizon_gate() -> dict:
    """Exact horizon residue and the only generic-real resonance check."""
    rho, r, omega = sp.symbols("rho r omega")
    I = sp.I
    Lambda = sp.Integer(6)
    A = sp.Matrix([
        [0, 1, 0, 0],
        [(Lambda*r - 4)/(r**2*(r - 2)), -2*I*omega*r/(r - 2),
         -2*I*omega/(r*(r - 2)), 0],
        [0, 0, 0, 1],
        [0, -2/(r - 2),
         (Lambda*r - 4 - 2*I*omega*r**2)/(r**2*(r - 2)),
         (-2*I*omega*r - 2)/(r - 2)],
    ])
    Ar = A.subs(r, 2 + rho)
    coeff = [Ar.applyfunc(lambda e: cancel(
        sp.series(e, rho, 0, 4).removeO().expand().coeff(rho, k - 1)))
        for k in range(4)]
    residue = coeff[0]
    z = sp.Symbol("z")
    charpoly = sp.factor(residue.charpoly(z).as_expr())
    expected = z**2 * (z + 4*I*omega) * (z + 2 + 4*I*omega)
    require(sp.simplify(charpoly - expected) == 0,
            f"carrier horizon charpoly changed: {charpoly}")
    require(len(residue.nullspace()) == 2,
            "regular zero eigenspace is not two-dimensional")

    lower = -2 - 4*I*omega
    v0 = (residue - lower*sp.eye(4)).nullspace()[0]
    P1 = (lower + 1)*sp.eye(4) - residue
    y1 = P1.inv() * coeff[1] * v0
    rhs2 = coeff[1] * y1 + coeff[2] * v0
    P2 = (lower + 2)*sp.eye(4) - residue
    left = P2.T.nullspace()
    require(len(left) == 1, "integer-spaced resonance cokernel changed")
    obstruction = cancel((left[0].T * rhs2)[0])
    require(obstruction == 0,
            f"singular carrier resonance forces a log: {obstruction}")

    n = sp.Symbol("n", integer=True, positive=True)
    determinants = {
        "regular_s0": sp.factor((n*sp.eye(4) - residue).det()),
        "singular_upper": sp.factor(((-4*I*omega+n)*sp.eye(4)-residue).det()),
        "singular_lower": sp.factor(((lower+n)*sp.eye(4)-residue).det()),
    }
    return {
        "state": ["P", "dP/dr", "Q", "dQ/dr"],
        "residue": [[sp.sstr(e) for e in residue.row(i)] for i in range(4)],
        "characteristic_polynomial": sp.sstr(charpoly),
        "branches": [
            {"label": "XH0a", "exponent": "0", "multiplicity": 1,
             "role": "additional carrier, future-horizon analytic"},
            {"label": "XH0b", "exponent": "0", "multiplicity": 1,
             "role": "additional carrier, future-horizon analytic"},
            {"label": "XHplus", "exponent": "-4*I*omega", "multiplicity": 1,
             "role": "additional carrier, singular/outgoing partner"},
            {"label": "XHminus", "exponent": "-2-4*I*omega", "multiplicity": 1,
             "role": "additional carrier, singular/outgoing partner"},
        ],
        "geometric_multiplicities": {"0": 2, "-4*I*omega": 1,
                                      "-2-4*I*omega": 1},
        "recurrence_determinants": {k: sp.sstr(v)
                                    for k, v in determinants.items()},
        "integer_spaced_resonance": {
            "from": "-2-4*I*omega", "to": "-4*I*omega", "order": 2,
            "cokernel_obstruction": sp.sstr(obstruction),
            "compatible": True, "logarithm_forced": False,
        },
        "real_nonzero_frequency_reading":
            "all four carrier branches are log-free; the only positive-order "
            "integer resonance is compatible",
    }


def carrier_infinity_gate(imported: dict) -> dict:
    carrier = imported["carrier"]
    require(carrier["characteristic_polynomial"] == "z**2*(2*I*omega + z)**2",
            "imported infinity characteristic polynomial changed")
    sectors = carrier["sectors"]
    require(all(not sector["logarithm_forced"] for sector in sectors.values()),
            "imported carrier infinity basis acquired a logarithm")
    return {
        "state": carrier["state"],
        "rates": carrier["rates"],
        "branches": [
            {"label": "XI0", "rate": "0", "power": "0",
             "role": "additional carrier, rate-zero top"},
            {"label": "XI1", "rate": "0", "power": "-1",
             "role": "additional carrier, rate-zero lower"},
            {"label": "XI2", "rate": "-2*I*omega",
             "power": "-4*I*omega",
             "role": "additional carrier, oscillatory top (M=1)"},
            {"label": "XI3", "rate": "-2*I*omega",
             "power": "-4*I*omega-1",
             "role": "additional carrier, oscillatory lower (M=1)"},
        ],
        "geometric_multiplicities": {"rate_0": 2,
                                      "rate_minus_2_i_omega": 2},
        "integer_spaced_resonances": {
            "rate_0_order_1": sectors["0"]["top_n1_resonance"],
            "oscillatory_order_1": sectors["-2*I*omega"]["top_n1_resonance"],
        },
        "logarithm_forced": False,
        "all_orders_basis": True,
        "radial_class": carrier["formal_class"],
    }


def build_repair_interface(row: sp.Expr, symbols: dict[str, sp.Symbol | sp.Function]) -> dict:
    """Machine-readable handoff for the complete-reconstruction successor."""
    return {
        "schema": "phase3-black-hole-axial-complete-reconstruction-repair-input-v1",
        "theory": "pure Weyl gravity; axial ell=2 on Schwarzschild M=1",
        "chart_and_phase": "ingoing EF (v,r,x,phi), Fourier phase exp(+i*omega*v)",
        "pilot_domain": "real omega in [1/2,3/4]",
        "corrected_sourced_lift_import": {
            "path": str(INPUTS["corrected_axial_selection"].relative_to(ROOT)),
            "sha256": sha256(INPUTS["corrected_axial_selection"]),
            "status": "REQUIRES_REAUDIT",
            "reading": "the Phase-2 verifier checks row_x, H1'=F and row_f; H1'=F is definitional, not the omitted vphi Ricci row. The polynomial control does not itself disprove the sourced X0 lift, but X0 has not passed the newly exposed compatibility equation.",
        },
        "carrier_state": ["P", "P_prime", "Q", "Q_prime"],
        "metric_state": ["H0", "H1", "F=H1_prime"],
        "carrier_ode_matrix": [
            ["0", "1", "0", "0"],
            ["(6*r-4)/(r^2*(r-2))", "-2*i*omega*r/(r-2)",
             "-2*i*omega/(r*(r-2))", "0"],
            ["0", "0", "0", "1"],
            ["0", "-2/(r-2)",
             "(6*r-4-2*i*omega*r^2)/(r^2*(r-2))",
             "(-2*i*omega*r-2)/(r-2)"],
        ],
        "divergence_constraint": {
            "c": "(r^2*(P_prime+Q_prime+i*omega*Q)+2*r*(P+Q-Q_prime)-2*Q)/4",
            "c_prime": "total r derivative after substituting the carrier ODE; it must be differentiated before any source placeholder replacement",
        },
        "differential_reconstruction_rows": {
            "H0_prime": "(-i*omega-2/r^2)*H1+(-1+2/r)*F+2*c",
            "H1_prime": "F",
            "F_prime": "-2*H0/(r*(r-2))+(6*r+4-2*i*omega*r^2-2*r)*H1/(r^2*(r-2))+(-4-2*i*omega*r^2)*F/(r*(r-2))+2*r*(c_prime-Q)/(r-2)",
        },
        "required_algebraic_row": {
            "equation": "delta_Ric_vphi_over_S2 = P",
            "left_hand_side": sp.sstr(row),
            "constraint": "C := delta_Ric_vphi_over_S2-P = 0",
            "role": "compatibility constraint reducing the apparent homogeneous dimension of the exposed three-state evolution",
        },
        "known_failed_vector": {
            "H1": "1", "H0": "-i*omega*r+2+2/r", "P": "0",
            "C": "3*i*(omega-2*i)/r^2",
        },
        "minimal_successor_obligations": [
            "derive C exactly from the three Ricci rows without source placeholders",
            "prove the propagation identity for C under the carrier and differential reconstruction equations",
            "impose C=0 and remove the spurious polynomial direction",
            "re-audit the corrected sourced X0 lift against delta Ric_{v phi}=P before preserving its Phase-2 promotion",
            "construct six independent complete Bach metric endpoint vectors: two Einstein-kernel vectors and four additional lifts",
            "retain the differentiated c_prime forcing and verify all three Ricci rows on every vector",
            "report every real or complex recurrence exception before any connection or flux consumer runs",
        ],
        "forbidden_promotions": [
            "no connection matrix from the two-row subsystem",
            "no finite-flux or scattering channel before the six-vector endpoint bases pass all three rows",
        ],
    }


def build_payload() -> dict:
    for path in INPUTS.values():
        require(path.exists(), f"missing input {path}")
    imported = json.loads(INPUTS["generic_axial_asymptotics"].read_text())
    corrected = json.loads(INPUTS["corrected_axial_selection"].read_text())
    require("2*r*(c'-Q)/(r-2*M)" in corrected["exact_metric_forcing"]["F_prime_source"],
            "corrected differentiated forcing was lost")
    row, symbols = axial_l2_vphi_row()
    expected = expected_vphi_row(symbols)
    require(sp.simplify(row - expected) == 0,
            "direct delta-Gamma rail changed the vphi row")
    residual, polynomial_h0 = polynomial_mode_residual(row, symbols)
    omega = symbols["omega"]

    provenance = {
        name: {"path": str(path.relative_to(ROOT)), "sha256": sha256(path)}
        for name, path in INPUTS.items()
    }
    repair_interface = build_repair_interface(row, symbols)
    return {
        "schema": "phase3-black-hole-axial-endpoint-bases-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "result_id": "PURE_WEYL_PHASE3_AXIAL_ENDPOINT_BASES",
        "result_token":
            "BH_PHASE3_AXIAL_ENDPOINT_METRIC_BASIS_OBSTRUCTED_BY_OMITTED_VPHI_ROW",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle": "CLASSIFIED",
        "declaration": {
            "theory": "pure Weyl gravity, S=alpha*integral sqrt(-g) C^2",
            "background": "Schwarzschild M=1 in ingoing Eddington-Finkelstein coordinates",
            "sector": "axial ell=2; carrier formulas imported from symbolic Lambda=ell(ell+1)",
            "frequency": "real dimensionless omega=M*omega in [1/2,3/4]",
            "phase": "Phase 3 endpoint-basis gate only",
        },
        "imported_operator_hashes": provenance,
        "carrier_endpoint_basis": {
            "horizon": carrier_horizon_gate(),
            "infinity": carrier_infinity_gate(imported),
            "dimension": 4,
            "complete_as_carrier_basis": True,
            "general_ell_reading":
                "the infinity carrier basis and its recurrences are exact for "
                "all ell>=2; the horizon residue is Lambda-independent by the "
                "imported structural theorem, and ell=2 is recomputed here",
        },
        "metric_reconstruction_gate": {
            "imported_state": imported["metric"]["state"],
            "imported_rows_used": ["delta Ric_{x phi}=c", "delta Ric_{r phi}=q"],
            "omitted_required_row": "delta Ric_{v phi}=p",
            "omitted_row_formula_ell2": sp.sstr(row),
            "advertised_polynomial_mode": {
                "H1": "1", "H0": sp.sstr(polynomial_h0),
                "imported_label": "generalized_polynomial_mode",
            },
            "exact_omitted_row_residual": sp.sstr(residual),
            "residual_zero_set": ["omega=2*I"],
            "pilot_interval_disjoint_from_zero_set": True,
            "differentiated_forcing_retained_in_corrected_X0":
                corrected["exact_metric_forcing"]["F_prime_source"],
            "consequence":
                "the imported 3x3 system contains a spurious solution of the "
                "two-row subsystem and cannot define the complete metric "
                "endpoint basis; the missing vphi differential-algebraic "
                "constraint must be incorporated before lifting all four carriers",
            "corrected_X0_disposition":
                "REQUIRES_REAUDIT: retaining c_prime repairs the differentiated "
                "forcing defect, but the Phase-2 verifier does not impose the "
                "newly exposed vphi compatibility row. The polynomial control "
                "does not itself disprove X0.",
            "successor_interface": str(REPAIR_INTERFACE.relative_to(ROOT)),
        },
        "disposition": {
            "carrier_endpoint_basis": "COMPLETE_FORMAL",
            "reconstructed_metric_endpoint_basis": "NOT_DEFINED",
            "stop_condition": "FIRST_EXACT_OBSTRUCTION",
            "next_required_object":
                "derive the full three-row Ricci reconstruction DAE, prove its "
                "constraint propagation, and rebuild the six-dimensional Bach "
                "metric endpoint basis without the spurious polynomial row",
        },
        "exceptional_set": {
            "real_pilot_interval": [],
            "excluded_frequency": ["omega=0"],
            "excluded_angular_representations": ["ell=0", "ell=1"],
            "complex_omitted_row_zero": ["omega=2*I"],
        },
        "claim_flags": {
            "carrier_horizon_basis_complete": True,
            "carrier_infinity_basis_complete": True,
            "carrier_logs_excluded_on_pilot_interval": True,
            "corrected_differentiated_forcing_imported": True,
            "corrected_X0_vphi_reaudit_required": True,
            "omitted_vphi_row_obstruction_certified": True,
            "complete_metric_endpoint_basis_certified": False,
            "horizon_to_infinity_connection_certified": False,
            "finite_flux_or_scattering_certified": False,
        },
        "does_not_establish": [
            "a complete reconstructed metric basis at either endpoint",
            "horizon-to-infinity matching or a connection matrix",
            "a finite-flux quotient, scattering channel, pole, stability, CPT, "
            "particle, or quantum statement",
            "convergence or summability of the formal infinity basis",
        ],
        "repair_interface": repair_interface,
        "verification": {
            "producer": "python3 black_hole_programme/phase3/axial_endpoint_bases/produce.py --check",
            "independent": "python3 black_hole_programme/phase3/axial_endpoint_bases/verify.py",
            "tests": "python3 -m unittest black_hole_programme.phase3.axial_endpoint_bases.tests.test_endpoint_bases",
        },
    }


def write_receipt(payload: dict) -> None:
    receipt = {
        "schema": "phase3-black-hole-axial-endpoint-bases-receipt-v1",
        "result_token": payload["result_token"],
        "input_sha256": {name: sha256(path) for name, path in INPUTS.items()},
        "source_sha256": {
            "produce.py": sha256(Path(__file__)),
            "schema.json": sha256(SCHEMA),
        },
        "tier0": "Python parse + JSON schema parse + scoped diff-check required at close-out",
        "tier1": [payload["verification"]["producer"],
                  payload["verification"]["independent"],
                  payload["verification"]["tests"]],
        "tier2": "not run: no imported operator or shared schema changed",
        "tier3": "not run: obstruction classification does not promote a scattering theorem",
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build_payload()
    encoded = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.check:
        require(CERTIFICATE.exists(), "missing certificate")
        require(CERTIFICATE.read_text() == encoded, "certificate is stale")
        expected_interface = json.dumps(payload["repair_interface"], indent=2,
                                        sort_keys=True) + "\n"
        require(REPAIR_INTERFACE.exists(), "missing repair interface")
        require(REPAIR_INTERFACE.read_text() == expected_interface,
                "repair interface is stale")
        print("PASS axial endpoint-basis obstruction certificate reproduces")
        return
    CERTIFICATE.write_text(encoded)
    REPAIR_INTERFACE.write_text(json.dumps(payload["repair_interface"], indent=2,
                                           sort_keys=True) + "\n")
    write_receipt(payload)
    print(f"wrote {CERTIFICATE}")
    print(payload["result_token"])


if __name__ == "__main__":
    main()
