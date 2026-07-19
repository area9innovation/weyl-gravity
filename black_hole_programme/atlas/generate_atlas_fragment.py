#!/usr/bin/env python3
"""Generate the fail-closed black-hole residual-atlas fragment.

Conforms to `residual_atlas/schema/residual-atlas-fragment-v1.schema.json`.
Statuses are derived from the certificates in
`black_hole_programme/certificates/` (pinned by result id and sha256).
Fail-closed rules:

- a status supported by a certificate that is absent on disk degrades to
  OPEN and its evidence pin is omitted;
- perturbative radiative fields stay OPEN until the dynamical complex
  (BH-2A) exists;
- relations to other backgrounds or carrier languages without an explicit
  crosswalk are NO_CERTIFIED_MAP;
- the compact second-order tangent-cone theorem is NOT imported as a
  horizon theorem: every black-hole `second_order` claim is OPEN or
  NO_CERTIFIED_MAP until a horizon/boundary-flux analogue is certified.

Run:  python3 black_hole_programme/atlas/generate_atlas_fragment.py
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PKG = HERE.parent
ROOT = PKG.parent
OUT = HERE / "black-hole-atlas-fragment.json"

STATUSES = ["CERTIFIED", "OBSTRUCTED", "OPEN", "NOT_APPLICABLE", "NO_CERTIFIED_MAP"]
DESCRIPTIONS = ["causal", "symplectic", "nonlinear", "observational", "quantum"]
SECOND_ORDER_EQUATION = "L_barPhi v = -(1/2) D^2 E_barPhi[u,u]"

CERTS = {
    "BH0": PKG / "certificates" / "BH0_STATIC_SPHERICAL_BACKGROUND.json",
    "BH1": PKG / "certificates" / "BH1_LEE_WALD_PREFLIGHT.json",
    "BH1A": PKG / "certificates" / "BH1A_NORMALIZED_GENERATOR.json",
    "BH1B": PKG / "certificates" / "BH1B_DYNAMICAL_EXTENSION.json",
    "BH2A": PKG / "certificates" / "BH2A_AXIAL_OPERATOR.json",
    "BH2AR": PKG / "certificates" / "BH2A_HORIZON_REACH.json",
    "BH2AF": PKG / "certificates" / "BH2A_FLUX_MATRIX.json",
    "BH2AC": PKG / "certificates" / "BH2A_CROSS_FLUX.json",
    "BH2AD": PKG / "certificates" / "BH2A_CAUSAL_DISPOSITION.json",
    "BH2BP": PKG / "certificates" / "BH2B_POLAR_SPLIT.json",
    "BH2BR": PKG / "certificates" / "BH2B_POLAR_REACH.json",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _evidence(*keys):
    rows = []
    for key in keys:
        if not CERTS[key].exists():
            continue
        payload = json.loads(CERTS[key].read_text(encoding="utf-8"))
        rows.append({
            "path": str(CERTS[key].relative_to(ROOT)),
            "result_id": payload["result_id"],
            "sha256": _sha256(CERTS[key]),
        })
    return rows


def _gated(status, statement_if_present, statement_if_absent, *required):
    """Fail-closed claim: degrade to OPEN when evidence is missing."""
    if all(CERTS[key].exists() for key in required):
        return {"status": status, "statement": statement_if_present}
    return {"status": "OPEN", "statement": statement_if_absent}


def _claim(status, statement):
    return {"status": status, "statement": statement}


def _gstat(status, *required):
    return status if all(CERTS[key].exists() for key in required) else "OPEN"


SECOND_ORDER_OPEN = {
    "equation": SECOND_ORDER_EQUATION,
    "bounded_or_finite_quasiperiodic": _claim(
        "OPEN", "no black-hole second-order tangent-cone object exists"),
    "smooth_secular": _claim(
        "OPEN", "no black-hole second-order tangent-cone object exists"),
    "causal_retarded": _claim(
        "OPEN", "no causal exterior second-order theory exists"),
}

SECOND_ORDER_NO_MAP = {
    "equation": SECOND_ORDER_EQUATION,
    "bounded_or_finite_quasiperiodic": _claim(
        "NO_CERTIFIED_MAP",
        "the compact tangent-cone theorem is not a horizon theorem; no crosswalk exists"),
    "smooth_secular": _claim(
        "NO_CERTIFIED_MAP",
        "the compact tangent-cone theorem is not a horizon theorem; no crosswalk exists"),
    "causal_retarded": _claim(
        "NO_CERTIFIED_MAP",
        "the compact tangent-cone theorem is not a horizon theorem; no crosswalk exists"),
}

BASE_SCOPE = {
    "theory": "pure-Weyl gravity S = alpha Int sqrt(-g) C_abcd C^abcd",
    "background": "MK static spherical Bach vacuum, working gauge b = 1/a; Schwarzschild and three-horizon fixture controls",
    "boundaries": "exterior chart with fixed-falloff ensembles {gamma, k fixed}; horizons as simple roots of B; no asymptotic completion imposed",
    "charge_sector": "normalized generator chi = u d_t, u = beta(2 - 3 beta gamma); H = -16 pi alpha beta^2 D2",
    "carrier": "metric perturbations of the static spherical chart",
}


def _scope(**kw):
    s = dict(BASE_SCOPE)
    s.update(kw)
    return s


def entries():
    E = []

    E.append({
        "id": "bh.background.static-family",
        "scope": _scope(carrier="background metric B(r)", degree="background",
                        parity="even", ell=0, m=0, k="n/a", omega=0),
        "descriptions": {
            "causal": "OPEN",
            "symplectic": _gstat("CERTIFIED", "BH0", "BH1", "BH1A"),
            "nonlinear": "OPEN",
            "observational": "OPEN",
            "quantum": "OPEN",
        },
        "mode_data": {
            "dispersion": _claim("NOT_APPLICABLE", "static background, no dispersion relation"),
            "lee_wald": _gated(
                "CERTIFIED",
                "exact static charges, Wald entropy, and first law dH = T dS at every simple horizon in the normalized-generator frame",
                "static Lee-Wald structure pending certificates",
                "BH1", "BH1A"),
            "taub_maps": _claim("NOT_APPLICABLE", "no Taub construction on this background"),
            "resonance": _claim("NOT_APPLICABLE", "static background"),
            "second_order": SECOND_ORDER_OPEN,
        },
        "evidence": _evidence("BH0", "BH1", "BH1A", "BH1B"),
        "claim_boundary": "exact Bach-flat three-parameter family, Laurent-class complete; residual gauge rank 2 with single invariant J = u^2 disc(Q); no causal exterior initial-boundary theorem, no physical matter/clock frame, no completeness beyond the Laurent class; symplectic status is the static and l=0-dynamical charge level only"
                          + ("; frame-independence of charge and entropy certified at the linear level" if CERTS["BH1B"].exists() else "; frame-independence pending the BH-1B certificate"),
    })

    E.append({
        "id": "bh.mode.l0.parameter",
        "scope": _scope(degree=1, parity="even", ell=0, m=0, k="n/a", omega=0),
        "descriptions": {
            "causal": "OPEN",
            "symplectic": _gstat("CERTIFIED", "BH1", "BH1A"),
            "nonlinear": "OPEN",
            "observational": "OPEN",
            "quantum": "OPEN",
        },
        "mode_data": {
            "dispersion": _claim("CERTIFIED", "omega = 0 static tangent modes d_beta, d_gamma, d_k of the solution family"),
            "lee_wald": _gated(
                "CERTIFIED",
                "exact r-independent charges u*F_beta, u*F_gamma, u*F_k; first law at every simple horizon; static pair current omega^r = 48 alpha/(19 r^2) at the fixture",
                "pending certificates", "BH1", "BH1A"),
            "taub_maps": _claim("NO_CERTIFIED_MAP", "no crosswalk to compact Taub structures exists"),
            "resonance": _claim("OPEN", "no resonant/stationary cokernel object exists for the exterior"),
            "second_order": SECOND_ORDER_OPEN,
        },
        "evidence": _evidence("BH1", "BH1A"),
        "claim_boundary": "static slice only; no time-dependent excitation of the parameters is certified beyond the l=0 gauge sectors",
    })

    E.append({
        "id": "bh.mode.l0.conformal-gauge",
        "scope": _scope(degree=1, parity="even", ell=0, m=0, k="n/a",
                        omega="arbitrary omega(t,r)"),
        "descriptions": {
            "causal": "NOT_APPLICABLE",
            "symplectic": _gstat("CERTIFIED", "BH1B"),
            "nonlinear": "OPEN",
            "observational": "NOT_APPLICABLE",
            "quantum": "OPEN",
        },
        "mode_data": {
            "dispersion": _claim("NOT_APPLICABLE", "pure gauge: on-shell for every omega(t,r) by exact conformal covariance"),
            "lee_wald": _gated(
                "CERTIFIED",
                "zero charge componentwise, zero entropy shift on the symbolic family, exact null direction of the corrected presymplectic current",
                "pending the BH-1B certificate", "BH1B"),
            "taub_maps": _claim("NOT_APPLICABLE", "gauge direction"),
            "resonance": _claim("NOT_APPLICABLE", "gauge direction"),
            "second_order": SECOND_ORDER_OPEN,
        },
        "evidence": _evidence("BH1B"),
        "claim_boundary": "linear level only; the nonlinear conformal orbit and any physical-frame selection are open",
    })

    E.append({
        "id": "bh.mode.l0.diffeo-gauge",
        "scope": _scope(degree=1, parity="even", ell=0, m=0, k="n/a",
                        omega="arbitrary a(t,r), b(t,r)"),
        "descriptions": {
            "causal": "NOT_APPLICABLE",
            "symplectic": _gstat("CERTIFIED", "BH1B"),
            "nonlinear": "OPEN",
            "observational": "NOT_APPLICABLE",
            "quantum": "OPEN",
        },
        "mode_data": {
            "dispersion": _claim("NOT_APPLICABLE", "pure gauge"),
            "lee_wald": _gated(
                "CERTIFIED",
                "exact Noether identity; identically vanishing charge form via the identity route with polynomial-witness cross-validation; zero flux",
                "pending the BH-1B certificate", "BH1B"),
            "taub_maps": _claim("NOT_APPLICABLE", "gauge direction"),
            "resonance": _claim("NOT_APPLICABLE", "gauge direction"),
            "second_order": SECOND_ORDER_OPEN,
        },
        "evidence": _evidence("BH1B"),
        "claim_boundary": "linear level only; time-dependent l=0 diffeomorphisms are proper gauge on the certified sector",
    })

    E.append({
        "id": "bh.mode.axial.einstein-branch",
        "scope": _scope(degree=1, parity="odd", ell=">=2", m="all", k="n/a",
                        omega="dynamical"),
        "descriptions": {
            "causal": "OPEN",
            "symplectic": _gstat("CERTIFIED", "BH2AF"),
            "nonlinear": "OPEN",
            "observational": "OPEN",
            "quantum": "OPEN",
        },
        "mode_data": {
            "dispersion": _gated(
                "CERTIFIED",
                "axial l=2 Einstein rows derived exactly; Regge-Wheeler master equation with V = B(6/r^2 - 6m/r^3) reproduced; branch injects exactly into the Bach kernel (delta B = (1/2) Box dRic + C.dRic on the Ricci-flat background)",
                "operator pending certificate", "BH2A"),
            "lee_wald": _gated(
                "CERTIFIED",
                "general axial bilinear F^t, F^r certified with the off-shell 4-alpha identity; RW-block on-shell flux -192*pi*alpha*(w1^2-w2^2)*psi1*psi2/(5*w1*w2*r) vanishes for conjugate pairs, while exact real-frequency fixtures certify nonzero Einstein x extra and extra x extra horizon flux",
                "mixed/extra horizon-flux fixtures not yet certified", "BH2AF", "BH2AC"),
            "taub_maps": _claim("NO_CERTIFIED_MAP", "no crosswalk to compact structures"),
            "resonance": _claim("OPEN", "no exterior cokernel object"),
            "second_order": SECOND_ORDER_OPEN,
        },
        "evidence": _evidence("BH2A", "BH2AF", "BH2AC"),
        "claim_boundary": "Schwarzschild axial l=2 only: the action-derived Lee-Wald current, conjugate-pair RW null theorem, and nonzero mixed/extra horizon-flux fixtures are certified; symbolic frequency dependence, the full exterior initial-boundary problem, stability and ringdown remain open",
    })

    E.append({
        "id": "bh.mode.axial.extra-fourth-order-branch",
        "scope": _scope(degree=1, parity="odd", ell=2, m="all", k="n/a",
                        omega="dynamical"),
        "descriptions": {desc: (_gstat("CERTIFIED", "BH2AD") if desc == "causal"
                                else ("OPEN" if desc != "symplectic" else _gstat("CERTIFIED", "BH2AC")))
                         for desc in DESCRIPTIONS},
        "mode_data": {
            "dispersion": _gated(
                "CERTIFIED",
                "extra branch identified exactly: carrier psi_ab = delta Ric_ab satisfies the second-order Lichnerowicz-type equation (1/2) Box psi + C.psi = 0 on the Ricci-flat background (axial l=2); the naive split is OBSTRUCTED on non-Einstein backgrounds",
                "operator pending certificate", "BH2A"),
            "lee_wald": _gated(
                "CERTIFIED",
                "fixture-level horizon flux closed: extra-branch Hermitian norm nonzero with i*F^r = +|v| pi alpha > 0 for alpha > 0 (omega in {3/5, 2/7}; verifier adds 1/2), Einstein x extra cross pairing nonzero; RW block certified null, so all pairing lives in the mixed and extra sectors; symbolic omega-dependence and outer boundary OPEN",
                "extra-block and cross-block flux values and signs remain open", "BH2AC"),
            "taub_maps": _claim("NO_CERTIFIED_MAP", "must not be identified with the compact-cylinder extra branch without an explicit crosswalk"),
            "resonance": _claim("OPEN", "no exterior cokernel object"),
            "second_order": SECOND_ORDER_OPEN,
        },
        "evidence": _evidence("BH2A", "BH2AR", "BH2AC", "BH2AD"),
        "claim_boundary": "Schwarzschild m=1, axial l=2, symbolic real frequency: the extra branch is horizon-regular, carries nonzero fixture-level horizon flux, and is bounded and luminal with Einstein-like leading falloff at infinity; no local causal decay or regularity condition removes it. Complex frequencies, general l/m, the full exterior initial-boundary problem, stability and ringdown remain OPEN"
                          if all(CERTS[key].exists() for key in ("BH2AR", "BH2AC", "BH2AD")) else "operator-level identification only (Schwarzschild, l=2): horizon reach, domains, flux, causal disposition all OPEN",
    })

    E.append({
        "id": "bh.mode.polar",
        "scope": _scope(degree=1, parity="even", ell=2, m="all", k="n/a",
                        omega="dynamical"),
        "descriptions": {desc: "OPEN" for desc in DESCRIPTIONS},
        "mode_data": {
            "dispersion": _gated(
                "CERTIFIED",
                "polar l=2 rows derived; general branch-split identity delta B = (1/2) Box dRic + C.dRic - (1/6) grad grad dR - (1/12) g Box dR certified componentwise: Einstein branch injects, polar extra branch = trace-coupled second-order Lichnerowicz system",
                "no even-parity exterior operator exists in the repository", "BH2BP"),
            "lee_wald": _claim("OPEN", "polar flux blocks open"),
            "taub_maps": _claim("NO_CERTIFIED_MAP", "no crosswalk to compact structures"),
            "resonance": _claim("OPEN", "no exterior cokernel object"),
            "second_order": SECOND_ORDER_OPEN,
        },
        "evidence": _evidence("BH2BP"),
        "claim_boundary": "operator-level split only (Schwarzschild, l=2): Zerilli benchmark, Einstein-branch polar flux, causal disposition all OPEN; the polar extra branch has its own entry",
    })

    E.append({
        "id": "bh.mode.polar.extra-fourth-order-branch",
        "scope": _scope(degree=1, parity="even", ell=2, m="all", k="n/a",
                        omega="dynamical, real omega != 0"),
        "descriptions": {desc: "OPEN" for desc in DESCRIPTIONS},
        "mode_data": {
            "dispersion": _gated(
                "CERTIFIED",
                "polar extra branch identified exactly: trace-coupled carrier (psi_ab, S) with the certified operator (1/2) Box psi + C.psi - (1/6) DD S - (1/12) g Box S = 0 and Bianchi constraint; exact identities (tracelessness + divergence) reduce the system to 3 second-order equations in 4 functions, the underdeterminacy being linearized conformal gauge; on the traceless slice r = 2m is a regular singular point with residue spectrum {0 (x3), 1-4imw, -1-4imw, -3-4imw} and a TWO-parameter physical ingoing-regular family after quotienting the regular conformal-gauge direction: the polar extra branch reaches the future horizon",
                "no polar extra-branch horizon-reach certificate exists", "BH2BP", "BH2BR"),
            "lee_wald": _claim("OPEN", "polar flux blocks open"),
            "taub_maps": _claim("NO_CERTIFIED_MAP", "must not be identified with compact structures without an explicit crosswalk"),
            "resonance": _claim("OPEN", "no exterior cokernel object"),
            "second_order": SECOND_ORDER_OPEN,
        },
        "evidence": _evidence("BH2BP", "BH2BR"),
        "claim_boundary": "Schwarzschild (symbolic m), polar l=2, real omega != 0: horizon reach certified (two-parameter physical ingoing-regular family modulo conformal gauge); omega = 0, Zerilli benchmark, flux matrix and signs, outer boundary, causal disposition, general l, stability all OPEN"
                          if CERTS["BH2BR"].exists() else "operator-level identification only: horizon reach OPEN",
    })

    E.append({
        "id": "bh.crosswalk.compact-cylinder",
        "scope": _scope(background="crosswalk: MK exterior <-> compact cylinder/Berger backgrounds",
                        carrier="mode identification map", degree="crosswalk",
                        parity="n/a", ell="n/a", m="n/a", k="n/a", omega="n/a"),
        "descriptions": {desc: "NO_CERTIFIED_MAP" for desc in DESCRIPTIONS},
        "mode_data": {
            "dispersion": _claim("NO_CERTIFIED_MAP", "no mode identification across backgrounds exists"),
            "lee_wald": _claim("NO_CERTIFIED_MAP", "no pairing crosswalk exists"),
            "taub_maps": _claim("NO_CERTIFIED_MAP", "no crosswalk exists"),
            "resonance": _claim("NO_CERTIFIED_MAP", "no crosswalk exists"),
            "second_order": SECOND_ORDER_NO_MAP,
        },
        "evidence": [],
        "claim_boundary": "the compact moment-map/tangent-cone theorem is not a horizon theorem; the black-hole analogue (global charges + horizon/boundary flux constraints + resonant or stationary cokernel) is deferred until the BH-2A linear phase space and adjoint problem exist, and must decide which compact terms are replaced by ADM, horizon or quasilocal charges",
    })

    E.append({
        "id": "bh.bridge.compact-branch-comparison",
        "scope": _scope(background="bridge stage 6: compact branch data <-> black-hole exterior radiation",
                        carrier="invariant branch factors, Lee-Wald signs, limiting data", degree="bridge",
                        parity="n/a", ell="n/a", m="n/a", k="n/a", omega="n/a"),
        "descriptions": {desc: "NO_CERTIFIED_MAP" for desc in DESCRIPTIONS},
        "mode_data": {
            "dispersion": _claim("NO_CERTIFIED_MAP", "bridge inactive; no native exterior modes exist yet"),
            "lee_wald": _claim("NO_CERTIFIED_MAP", "Lee-Wald sign comparison requires the BH-2A flux matrix"),
            "taub_maps": _claim("NO_CERTIFIED_MAP", "the compact Taub cone is not imported as a horizon theorem"),
            "resonance": _claim("NO_CERTIFIED_MAP", "bridge inactive"),
            "second_order": SECOND_ORDER_NO_MAP,
        },
        "evidence": [],
        "claim_boundary": "ladder stage 6 activation gate: an independently closed exterior/asymptotic phase space with boundary-preserving generators, charges and fluxes (BH-2A+); until then every comparison axis is NO_CERTIFIED_MAP and no mode is identified across backgrounds by name",
    })

    return E


def main() -> None:
    fragment = {
        "schema": "pure-weyl-residual-atlas-fragment-v1",
        "schema_version": "1.0.0",
        "team": "black_hole",
        "generated_by": "black_hole_programme/atlas/generate_atlas_fragment.py",
        "generated_by_sha256": _sha256(Path(__file__).resolve()),
        "status_vocabulary": STATUSES,
        "description_axes": DESCRIPTIONS,
        "entries": entries(),
        "verification_commands": [
            "python3 residual_atlas/validate_fragment.py black_hole_programme/atlas/black-hole-atlas-fragment.json",
            "python3 black_hole_programme/atlas/generate_atlas_fragment.py",
        ],
    }
    OUT.write_text(json.dumps(fragment, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
