#!/usr/bin/env python3
"""Generate the fail-closed operational-observer residual-atlas fragment."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent
ROOT = PACKAGE.parent
OUTPUT = HERE / "observer-atlas-fragment.json"
STATUSES = ["CERTIFIED", "OBSTRUCTED", "OPEN", "NOT_APPLICABLE", "NO_CERTIFIED_MAP"]
DESCRIPTIONS = ["causal", "symplectic", "nonlinear", "observational", "quantum"]
CERTIFICATES = {
    "tangent_cone": ROOT / "d_quotient_classical/certificates/FINITE_HARMONIC_SECOND_ORDER_TANGENT_CONE_THEOREM_V1.json",
    "redshift": ROOT / "d_quotient_classical/certificates/BERGER_DYNAMICAL_MAXWELL_REDSHIFT_MODE.json",
    "records": PACKAGE / "certificates/BERGER_CG4_TWO_RECORD_POISSON_ALGEBRA.json",
    "morphism": PACKAGE / "certificates/BERGER_AFFINE_K_OBSERVER_MORPHISM.json",
    "rank": PACKAGE / "certificates/BERGER_DYNAMICAL_EMITTER_CAUCHY_RANK_TWO.json",
    "profiles": PACKAGE / "certificates/BERGER_POSITIVE_ENERGY_DETECTOR_SELECTED_EMITTER_PROFILES.json",
    "form": PACKAGE / "certificates/BERGER_CLOCK_INTEGRATED_FORM_PROFILE_COEFFICIENTS.json",
    "recoil": PACKAGE / "certificates/BERGER_DYNAMICAL_EMITTER_RECOIL_ORDER_AND_INPUT_GATE.json",
    "stress": PACKAGE / "certificates/BERGER_EMITTER_STRESS_CLOCK_BACKREACTION_LEDGER.json",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _evidence(*names: str) -> list[dict[str, str]]:
    rows = []
    for name in names:
        path = CERTIFICATES[name]
        value = json.loads(path.read_text())
        rows.append({"path": str(path.relative_to(ROOT)), "result_id": value["result_id"], "sha256": _sha256(path)})
    return rows


BASE = {
    "theory": "classical pure-Weyl gravity plus positive scalar clock, Maxwell field, detector rods/memories and selected massive two-form emitters",
    "background": "compact positive Berger clock at fixed coupling",
    "boundaries": "R x S3; compact spatial slices, relationally compact detector and switch windows, no spatial boundary",
    "charge_sector": "fixed-coupling Berger clock sector; no compact-product charge fibre imported",
}


def _scope(**updates):
    value = dict(BASE); value.update(updates); return value


def entries() -> list[dict]:
    return [
        {
            "id": "observer.berger.cg4.circular_maxwell_plane",
            "scope": _scope(carrier="C-G4 two-phase source-free Maxwell plane mapped to two persistent memory records", degree=1, parity="circular Maxwell helicity in span(e1,e2)", ell="left-invariant one-form block", m="two real phase quadratures", k="curl eigenvalue -1/c", omega="+/- 1/c = +/-2 sqrt(10)/3"),
            "descriptions": {"causal": "CERTIFIED", "symplectic": "CERTIFIED", "nonlinear": "OPEN", "observational": "CERTIFIED", "quantum": "OPEN"},
            "operational_observable": {"detector_response": "phase-plane map N to persistent memories (m0,m1)", "response_rank": 2, "emitter_preparation": "source-free circular Maxwell cosine/sine phase pair; not identified with the massive-emitter Cauchy preparations", "clock_and_rod_dependence": "two disjoint clock-labelled normalized detector windows with detector-indexed rods", "relational_redshift_contribution": "C-G4 energy/redshift is a quadratic polynomial in the two records", "recoil_backreaction_order": "Maxwell stress begins at probe-amplitude order epsilon^2; no C-G4 second-order tangent-cone survival theorem", "survives_gauge_reduction": "CERTIFIED for Maxwell gauge and simultaneous affine-K family covariance; fixed-background linear-K descent OPEN", "profile_green_boundary_dependencies": "compact S3, exact C-G4 retarded mode and detector moments S0,C0,S1,C1; no spatial boundary"},
            "tangent_cone": {"restriction_status": "OPEN", "linearly_detectable_but_nonlinearly_obstructed": "OPEN", "balanced_detectable_combinations": "OPEN", "observer_source_channel": "Maxwell stress enters at second order, but its projection to Z2^C has not been computed", "correction_classes": {"bounded_or_quasiperiodic": "OPEN", "smooth_secular": "OPEN", "causal_or_retarded": "OPEN"}},
            "evidence": _evidence("redshift", "records", "morphism"),
        },
        {
            "id": "observer.berger.massive_emitter.preparation_pair",
            "scope": _scope(carrier="two compact positive-energy massive-two-form Cauchy preparations u0,u1 and the leading detector record map", degree=1, parity="real two-form polarization; no spatial parity decomposition certified", ell="compact Peter-Weyl superposition", m="all", k="all", omega="massive mode spectrum; unevaluated full profile"),
            "descriptions": {"causal": "CERTIFIED", "symplectic": "CERTIFIED", "nonlinear": "OPEN", "observational": "CERTIFIED", "quantum": "OPEN"},
            "operational_observable": {"detector_response": "M_ab=Q_a[d G_A,ret g_b delta(h_b K_b^(0))]", "response_rank": 2, "emitter_preparation": "u_a=(-p_a,L_a q_a), detector-selected positive-energy Cauchy dual", "clock_and_rod_dependence": "exact switches h0,h1 and detector profiles f_a rho_a J_a; u1 is later than D0 so M_01=0", "relational_redshift_contribution": "not separately evaluated for the massive-emitter preparation pair", "recoil_backreaction_order": "absolute g^2 response vanishes; first feedback is absolute g^3 (relative g^2); coefficient OPEN", "survives_gauge_reduction": "leading record is Maxwell-gauge compatible and cyclic; fixed-background K quotient and full Dirac reduction OPEN", "profile_green_boundary_dependencies": "operator-defined compact Cauchy profiles; form/spatial-coderivative coefficients certified through two_j=4; temporal Green weighting, high-mode tail and full advanced images OPEN"},
            "tangent_cone": {"restriction_status": "OPEN", "linearly_detectable_but_nonlinearly_obstructed": "OPEN", "balanced_detectable_combinations": "OPEN", "observer_source_channel": "emitter stress and reciprocal clock source are certified q2 channels; whether they supply or remove a tangent-cone obstruction is OPEN", "correction_classes": {"bounded_or_quasiperiodic": "OPEN", "smooth_secular": "OPEN", "causal_or_retarded": "OPEN"}},
            "evidence": _evidence("rank", "profiles", "form", "recoil", "stress"),
        },
        {
            "id": "observer.berger.detector_form_modes.two_j_0_to_4",
            "scope": _scope(carrier="clock-zero-moment detector one-form Fourier coefficients and spatial coderivatives", degree=1, parity="polarization-dependent form coefficients", ell="SU(2) two_j=0,1,2,3,4", m="all representation rows", k="all representation columns", omega="zero temporal moment only"),
            "descriptions": {"causal": "OPEN", "symplectic": "OPEN", "nonlinear": "NOT_APPLICABLE", "observational": "OPEN", "quantum": "OPEN"},
            "operational_observable": {"detector_response": "no per-mode detector response until temporal coderivative and Green kernel are composed", "response_rank": "OPEN", "emitter_preparation": "input coefficients for detector-selected preparation construction", "clock_and_rod_dependence": "exact dR0_1 and dR1_2 coframe gradients with validated odd secant moments", "relational_redshift_contribution": "NOT_APPLICABLE at this coefficient-only gate", "recoil_backreaction_order": "input to absolute-g^3 coefficient; not an evaluated recoil", "survives_gauge_reduction": "OPEN until the full four-dimensional coexact source is assembled", "profile_green_boundary_dependencies": "spatial block CERTIFIED through two_j=4; temporal Green weighting and infinite tail OPEN"},
            "tangent_cone": {"restriction_status": "NOT_APPLICABLE", "linearly_detectable_but_nonlinearly_obstructed": "NOT_APPLICABLE", "balanced_detectable_combinations": "NOT_APPLICABLE", "observer_source_channel": "coefficient input only", "correction_classes": {"bounded_or_quasiperiodic": "NOT_APPLICABLE", "smooth_secular": "NOT_APPLICABLE", "causal_or_retarded": "NOT_APPLICABLE"}},
            "evidence": _evidence("form"),
        },
        {
            "id": "observer.berger.second_order_cone_restriction",
            "scope": _scope(carrier="operational detector map restricted to Z2^C on the Berger 108-row carrier", degree=2, parity="all finite-harmonic sectors admitted by a future cone certificate", ell="finite but unspecified", m="finite but unspecified", k="finite but unspecified", omega="finite but correction-class dependent"),
            "descriptions": {"causal": "OPEN", "symplectic": "OPEN", "nonlinear": "OPEN", "observational": "OPEN", "quantum": "OPEN"},
            "operational_observable": {"detector_response": "O_detector|Z2^C not yet computed", "response_rank": "OPEN", "emitter_preparation": "only the unrestricted leading massive-emitter pair is certified", "clock_and_rod_dependence": "Berger apparatus only", "relational_redshift_contribution": "C-G4 redshift is detectable linearly; survival on Z2^C OPEN", "recoil_backreaction_order": "q2 stress/clock channels and g3 detector feedback known, cone projection OPEN", "survives_gauge_reduction": "OPEN on the nonlinear cone", "profile_green_boundary_dependencies": "depends on correction class C and full causal source images"},
            "tangent_cone": {"formula": "Z2^C={u: mu_X(u)=0 and R_j^C(u)=0}", "restriction_status": "OPEN", "linearly_detectable_but_nonlinearly_obstructed": "OPEN", "balanced_detectable_combinations": "OPEN", "observer_source_channel": "OPEN", "correction_classes": {"bounded_or_quasiperiodic": "OPEN", "smooth_secular": "OPEN", "causal_or_retarded": "OPEN"}},
            "evidence": _evidence("tangent_cone", "records", "rank", "recoil", "stress"),
        },
        {
            "id": "observer.crosswalk.compact_product_exceptional_resonance_to_berger",
            "scope": _scope(background="crosswalk: compact Einstein-Maxwell product exceptional resonance <-> positive Berger observer apparatus", carrier="background/carrier mode identification map", degree="crosswalk", parity="n/a", ell="n/a", m="n/a", k="n/a", omega="n/a"),
            "descriptions": {name: "NO_CERTIFIED_MAP" for name in DESCRIPTIONS},
            "operational_observable": {"detector_response": "NO_CERTIFIED_MAP", "response_rank": "NO_CERTIFIED_MAP", "emitter_preparation": "NO_CERTIFIED_MAP", "clock_and_rod_dependence": "NO_CERTIFIED_MAP", "relational_redshift_contribution": "NO_CERTIFIED_MAP", "recoil_backreaction_order": "NO_CERTIFIED_MAP", "survives_gauge_reduction": "NO_CERTIFIED_MAP", "profile_green_boundary_dependencies": "NO_CERTIFIED_MAP"},
            "tangent_cone": {"restriction_status": "NO_CERTIFIED_MAP", "linearly_detectable_but_nonlinearly_obstructed": "NO_CERTIFIED_MAP", "balanced_detectable_combinations": "NO_CERTIFIED_MAP", "exceptional_resonant_operational_signature": "NO_CERTIFIED_MAP", "observer_source_channel": "NO_CERTIFIED_MAP", "correction_classes": {"bounded_or_quasiperiodic": "NO_CERTIFIED_MAP", "smooth_secular": "NO_CERTIFIED_MAP", "causal_or_retarded": "NO_CERTIFIED_MAP"}},
            "evidence": [],
        },
    ]


def build() -> dict:
    value = {"schema": "pure-weyl-residual-atlas-fragment-v1", "team": "closed_universe_observer", "generated_by": str(Path(__file__).relative_to(ROOT)), "status_vocabulary": STATUSES, "descriptions": DESCRIPTIONS, "entries": entries()}
    required_scope = {"theory", "background", "boundaries", "charge_sector", "carrier", "degree", "parity", "ell", "m", "k", "omega"}
    for entry in value["entries"]:
        if set(entry["scope"]) != required_scope:
            raise AssertionError(f"incomplete mode scope: {entry['id']}")
        if set(entry["descriptions"]) != set(DESCRIPTIONS) or any(status not in STATUSES for status in entry["descriptions"].values()):
            raise AssertionError(f"invalid lifecycle status: {entry['id']}")
        if not entry["evidence"] and "crosswalk" not in entry["id"]:
            raise AssertionError(f"unsupported atlas claim: {entry['id']}")
    return value


def main() -> int:
    OUTPUT.write_text(json.dumps(build(), indent=2, sort_keys=True) + "\n")
    print(f"wrote {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
