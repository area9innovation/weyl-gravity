#!/usr/bin/env python3
"""Generate the fail-closed operational-observer residual-atlas fragment."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent
ROOT = PACKAGE.parent
OUTPUT = HERE / "observer-atlas-fragment.json"
SCHEMA = ROOT / "residual_atlas/schema/residual-atlas-fragment-v1.schema.json"
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
    "green_weighted": PACKAGE / "certificates/BERGER_GREEN_WEIGHTED_DETECTOR_CODERIVATIVE.json",
    "tail_obstruction": PACKAGE / "certificates/BERGER_TWO_J4_PROFILE_TAIL_OBSTRUCTION.json",
    "adaptive_route": PACKAGE / "certificates/BERGER_ADAPTIVE_PETER_WEYL_ROUTE_PREFLIGHT.json",
    "streaming_sectors": PACKAGE / "certificates/BERGER_STREAMABLE_POLARIZATION_SECTORS.json",
    "polarization_recurrence": PACKAGE / "certificates/BERGER_POLARIZATION_CLEBSCH_GORDAN_RECURRENCE.json",
    "high_order_moments": PACKAGE / "certificates/BERGER_HIGH_ORDER_PROFILE_MOMENT_RAIL.json",
    "scalar_stream": PACKAGE / "certificates/BERGER_CLOCK_INTEGRATED_SCALAR_STREAM_TWO_J139.json",
    "scalar_s2": PACKAGE / "certificates/BERGER_CLOCK_WEIGHTED_SCALAR_STREAM_S2_TWO_J139.json",
    "scalar_s4": PACKAGE / "certificates/BERGER_CLOCK_WEIGHTED_SCALAR_STREAM_S4_TWO_J139.json",
    "scalar_s6": PACKAGE / "certificates/BERGER_CLOCK_WEIGHTED_SCALAR_STREAM_S6_TWO_J139.json",
    "scalar_s8": PACKAGE / "certificates/BERGER_CLOCK_WEIGHTED_SCALAR_STREAM_S8_TWO_J139.json",
    "scalar_s10": PACKAGE / "certificates/BERGER_CLOCK_WEIGHTED_SCALAR_STREAM_S10_TWO_J139.json",
    "branch_obstruction": ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_36_RESIDUAL_BRANCH_LOCAL_PROJECTOR_OBSTRUCTION_V1.json",
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
            "operational_observable": {"detector_response": "M_ab=Q_a[d G_A,ret g_b delta(h_b K_b^(0))]", "response_rank": 2, "emitter_preparation": "u_a=(-p_a,L_a q_a), detector-selected positive-energy Cauchy dual", "clock_and_rod_dependence": "exact switches h0,h1 and detector profiles f_a rho_a J_a; u1 is later than D0 so M_01=0", "relational_redshift_contribution": "not separately evaluated for the massive-emitter preparation pair", "recoil_backreaction_order": "absolute g^2 response vanishes; first feedback is absolute g^3 (relative g^2); coefficient OPEN", "survives_gauge_reduction": "leading record is Maxwell-gauge compatible and cyclic; fixed-background K quotient and full Dirac reduction OPEN", "profile_green_boundary_dependencies": "operator-defined compact Cauchy profiles; full coderivative and finite-mode advanced Maxwell image certified through two_j=4 with uniform temporal-kernel remainder; uniform small tail at that cutoff is OBSTRUCTED and the massive image is OPEN"},
            "tangent_cone": {"restriction_status": "OPEN", "linearly_detectable_but_nonlinearly_obstructed": "OPEN", "balanced_detectable_combinations": "OPEN", "observer_source_channel": "emitter stress and reciprocal clock source are certified q2 channels; whether they supply or remove a tangent-cone obstruction is OPEN", "correction_classes": {"bounded_or_quasiperiodic": "OPEN", "smooth_secular": "OPEN", "causal_or_retarded": "OPEN"}},
            "evidence": _evidence("rank", "profiles", "form", "green_weighted", "tail_obstruction", "recoil", "stress"),
        },
        {
            "id": "observer.berger.detector_form_modes.two_j_0_to_4",
            "scope": _scope(carrier="finite-mode advanced Maxwell image of the full detector coderivative", degree=1, parity="polarization-dependent Maxwell one-form image", ell="SU(2) two_j=0,1,2,3,4", m="all representation rows", k="all representation columns", omega="advanced sine/cosine kernel, series order five with uniform remainder"),
            "descriptions": {"causal": "CERTIFIED", "symplectic": "OPEN", "nonlinear": "NOT_APPLICABLE", "observational": "OPEN", "quantum": "OPEN"},
            "operational_observable": {"detector_response": "finite-mode advanced Maxwell covector image only; no per-mode detector response rank yet", "response_rank": "OPEN", "emitter_preparation": "input field A_a^adv for the detector-selected massive preparation", "clock_and_rod_dependence": "exact dR0_1/dR1_2 profiles and flat clock bumps; uniform on the matching h0/h1 switch intervals", "relational_redshift_contribution": "NOT_APPLICABLE at this Green-image input gate", "recoil_backreaction_order": "input to absolute-g^3 coefficient; not an evaluated recoil", "survives_gauge_reduction": "finite source is the full four-dimensional coderivative, but full spatial-sum gauge reduction remains OPEN", "profile_green_boundary_dependencies": "temporal derivative is cosine-kernel weighted by boundary-flat integration by parts; sine spatial-coderivative block and entire-series remainder certified through two_j=4; uniform small profile tail is OBSTRUCTED at this cutoff"},
            "tangent_cone": {"restriction_status": "NOT_APPLICABLE", "linearly_detectable_but_nonlinearly_obstructed": "NOT_APPLICABLE", "balanced_detectable_combinations": "NOT_APPLICABLE", "observer_source_channel": "coefficient input only", "correction_classes": {"bounded_or_quasiperiodic": "NOT_APPLICABLE", "smooth_secular": "NOT_APPLICABLE", "causal_or_retarded": "NOT_APPLICABLE"}},
            "evidence": _evidence("form", "green_weighted", "tail_obstruction"),
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
            "id": "observer.berger.detector_profile_tail.two_j4_cutoff",
            "scope": _scope(carrier="clock-center normalized detector one-form profile and its Peter-Weyl energy split", degree=1, parity="either selected detector polarization", ell="retained two_j=0,1,2,3,4 versus omitted two_j>=5", m="all representation rows", k="all representation columns", omega="fixed clock-center spatial slice"),
            "descriptions": {"causal": "OBSTRUCTED", "symplectic": "NOT_APPLICABLE", "nonlinear": "NOT_APPLICABLE", "observational": "OPEN", "quantum": "NOT_APPLICABLE"},
            "operational_observable": {"detector_response": "no full response: the two_j<=4 window omits more than 0.9999975 of the clock-center profile Fourier energy", "response_rank": "OPEN", "emitter_preparation": "adaptive high-mode expansion or physical-space Green chain required", "clock_and_rod_dependence": "exact radius 1/128 and either clock-center detector polarization", "relational_redshift_contribution": "NOT_APPLICABLE", "recoil_backreaction_order": "absolute-g^3 coefficient remains blocked by the unresolved full profile", "survives_gauge_reduction": "NOT_APPLICABLE at this profile-resolution obstruction", "profile_green_boundary_dependencies": "finite two_j<=4 Green image remains certified, but uniform promotion to the full compact profile is OBSTRUCTED at that cutoff"},
            "tangent_cone": {"restriction_status": "NOT_APPLICABLE", "linearly_detectable_but_nonlinearly_obstructed": "NOT_APPLICABLE", "balanced_detectable_combinations": "NOT_APPLICABLE", "observer_source_channel": "NOT_APPLICABLE", "correction_classes": {"bounded_or_quasiperiodic": "NOT_APPLICABLE", "smooth_secular": "NOT_APPLICABLE", "causal_or_retarded": "NOT_APPLICABLE"}},
            "evidence": _evidence("tail_obstruction"),
        },
        {
            "id": "observer.berger.detector_profile.adaptive_cutoff_preflight",
            "scope": _scope(carrier="streamed symmetry-reduced Peter-Weyl detector contractions after the two_j<=4 obstruction", degree=1, parity="either selected detector polarization", ell="necessary capacity rail through at least two_j=138; convergence cutoff OPEN", m="all representation rows", k="all representation columns", omega="modewise advanced Maxwell kernels; full tail OPEN"),
            "descriptions": {"causal": "OPEN", "symplectic": "NOT_APPLICABLE", "nonlinear": "NOT_APPLICABLE", "observational": "OPEN", "quantum": "NOT_APPLICABLE"},
            "operational_observable": {"detector_response": "streamed adaptive route selected; all scalar inputs to the finite temporal Green polynomial are evaluated but no full Green-weighted detector response", "response_rank": "OPEN for the recoil-corrected response", "emitter_preparation": "existing detector-selected massive Cauchy pair; clock-weighted scalar coefficients for powers 0,2,4,6,8,10 are evaluated through two_j=139", "clock_and_rod_dependence": "radius-1/128 rod profile fixes the necessary two_j>=138 capacity rail; normalized joint clock moments are enclosed without assuming clock/profile independence", "relational_redshift_contribution": "OPEN until the full same-background response is evaluated", "recoil_backreaction_order": "absolute g^3 operator exact; coefficient remains OPEN", "survives_gauge_reduction": "OPEN for the completed Green-weighted mode sum", "profile_green_boundary_dependencies": "each of the six clock-power streams reconstructs 9,870 diagonal scalar values through two_j=139 from 4,970 validated intervals; the five weighted rails use E[s^p]<=E[s^p sec(lambda s)^(2k)]<=cos(lambda)^(-2k)E[s^p]; polarization/Green charge-block composition, the tail beyond two_j=138, and full Maxwell/massive images remain OPEN"},
            "tangent_cone": {"restriction_status": "NOT_APPLICABLE at the bandwidth-route preflight", "linearly_detectable_but_nonlinearly_obstructed": "NOT_APPLICABLE", "balanced_detectable_combinations": "NOT_APPLICABLE", "observer_source_channel": "NOT_APPLICABLE", "correction_classes": {"bounded_or_quasiperiodic": "NOT_APPLICABLE", "smooth_secular": "NOT_APPLICABLE", "causal_or_retarded": "NOT_APPLICABLE"}},
            "evidence": _evidence("adaptive_route", "streaming_sectors", "polarization_recurrence", "high_order_moments", "scalar_stream", "scalar_s2", "scalar_s4", "scalar_s6", "scalar_s8", "scalar_s10"),
        },
        {
            "id": "observer.crosswalk.berger_physical_branch_to_detector",
            "scope": _scope(carrier="same-background Berger physical-branch dictionary to relational detector, redshift, memory and recoil records", degree="crosswalk", parity="all", ell="all", m="all", k="all", omega="all"),
            "descriptions": {name: "NO_CERTIFIED_MAP" for name in DESCRIPTIONS},
            "operational_observable": {"detector_response": "NO_CERTIFIED_MAP", "response_rank": "NO_CERTIFIED_MAP", "emitter_preparation": "NO_CERTIFIED_MAP", "clock_and_rod_dependence": "Berger apparatus exists, but no physical-branch-labelled Berger mode dictionary exists", "relational_redshift_contribution": "NO_CERTIFIED_MAP", "recoil_backreaction_order": "NO_CERTIFIED_MAP", "survives_gauge_reduction": "NO_CERTIFIED_MAP", "profile_green_boundary_dependencies": "Bridge 3 is inactive until a same-background Berger branch dictionary lands"},
            "tangent_cone": {"restriction_status": "NO_CERTIFIED_MAP", "linearly_detectable_but_nonlinearly_obstructed": "NO_CERTIFIED_MAP", "balanced_detectable_combinations": "NO_CERTIFIED_MAP", "exceptional_resonant_operational_signature": "NO_CERTIFIED_MAP", "observer_source_channel": "NO_CERTIFIED_MAP", "correction_classes": {"bounded_or_quasiperiodic": "NO_CERTIFIED_MAP", "smooth_secular": "NO_CERTIFIED_MAP", "causal_or_retarded": "NO_CERTIFIED_MAP"}},
            "evidence": _evidence("branch_obstruction"),
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


OBSERVER_STATUSES = {
    "observer.berger.cg4.circular_maxwell_plane": ["CERTIFIED", "CERTIFIED", "CERTIFIED", "CERTIFIED", "CERTIFIED", "OPEN", "CERTIFIED", "CERTIFIED", "OPEN", "OPEN", "OPEN", "NOT_APPLICABLE", "OPEN"],
    "observer.berger.massive_emitter.preparation_pair": ["CERTIFIED", "CERTIFIED", "CERTIFIED", "CERTIFIED", "OPEN", "OPEN", "OPEN", "OPEN", "OPEN", "OPEN", "OPEN", "NOT_APPLICABLE", "OPEN"],
    "observer.berger.detector_form_modes.two_j_0_to_4": ["OPEN", "OPEN", "OPEN", "CERTIFIED", "NOT_APPLICABLE", "OPEN", "OPEN", "OPEN", "NOT_APPLICABLE", "NOT_APPLICABLE", "NOT_APPLICABLE", "NOT_APPLICABLE", "NOT_APPLICABLE"],
    "observer.berger.second_order_cone_restriction": ["OPEN", "OPEN", "OPEN", "OPEN", "OPEN", "OPEN", "OPEN", "OPEN", "OPEN", "OPEN", "OPEN", "NOT_APPLICABLE", "OPEN"],
    "observer.berger.detector_profile_tail.two_j4_cutoff": ["OBSTRUCTED", "OPEN", "OPEN", "CERTIFIED", "NOT_APPLICABLE", "OPEN", "NOT_APPLICABLE", "OBSTRUCTED", "NOT_APPLICABLE", "NOT_APPLICABLE", "NOT_APPLICABLE", "NOT_APPLICABLE", "NOT_APPLICABLE"],
    "observer.berger.detector_profile.adaptive_cutoff_preflight": ["OPEN", "OPEN", "OPEN", "CERTIFIED", "NOT_APPLICABLE", "OPEN", "OPEN", "OPEN", "NOT_APPLICABLE", "NOT_APPLICABLE", "NOT_APPLICABLE", "NOT_APPLICABLE", "NOT_APPLICABLE"],
    "observer.crosswalk.berger_physical_branch_to_detector": ["NO_CERTIFIED_MAP"] * 13,
    "observer.crosswalk.compact_product_exceptional_resonance_to_berger": ["NO_CERTIFIED_MAP"] * 13,
}
OBSERVER_FIELDS = [
    "detector_response", "response_rank", "emitter_preparation",
    "clock_and_rod_dependence", "relational_redshift_contribution",
    "recoil_backreaction_order", "survives_gauge_reduction",
    "profile_green_boundary_dependencies",
    "detector_restriction_to_second_order_cone",
    "linearly_detectable_but_nonlinearly_obstructed",
    "balanced_detectable_combinations",
    "exceptional_resonant_operational_signature", "observer_source_channel",
]


def _claim(status: str, statement: object) -> dict[str, str]:
    if status not in STATUSES:
        raise AssertionError(f"invalid claim status: {status}")
    return {"status": status, "statement": str(statement)}


def _shared_entry(raw: dict) -> dict:
    operational = raw["operational_observable"]
    cone = raw["tangent_cone"]
    correction = cone["correction_classes"]
    statements = [
        operational["detector_response"], operational["response_rank"],
        operational["emitter_preparation"], operational["clock_and_rod_dependence"],
        operational["relational_redshift_contribution"], operational["recoil_backreaction_order"],
        operational["survives_gauge_reduction"], operational["profile_green_boundary_dependencies"],
        cone["restriction_status"], cone["linearly_detectable_but_nonlinearly_obstructed"],
        cone["balanced_detectable_combinations"],
        cone.get("exceptional_resonant_operational_signature", "No exceptional-resonance question applies within this Berger carrier."),
        cone["observer_source_channel"],
    ]
    observer_data = {
        field: _claim(status, statement)
        for field, status, statement in zip(OBSERVER_FIELDS, OBSERVER_STATUSES[raw["id"]], statements)
    }
    restriction = observer_data["detector_restriction_to_second_order_cone"]["statement"]
    mode_data = {
        "dispersion": _claim(raw["descriptions"]["causal"], f"carrier={raw['scope']['carrier']}; omega={raw['scope']['omega']}; {operational['detector_response']}"),
        "lee_wald": _claim(raw["descriptions"]["symplectic"], operational["survives_gauge_reduction"]),
        "taub_maps": _claim(raw["descriptions"]["nonlinear"], f"{operational['recoil_backreaction_order']}; detector restriction={restriction}"),
        "resonance": observer_data["exceptional_resonant_operational_signature"],
        "second_order": {
            "equation": "L_barPhi v = -(1/2) D^2 E_barPhi[u,u]",
            "bounded_or_finite_quasiperiodic": _claim(correction["bounded_or_quasiperiodic"], f"O_detector|Z2^C: {restriction}"),
            "smooth_secular": _claim(correction["smooth_secular"], f"O_detector|Z2^C: {restriction}"),
            "causal_retarded": _claim(correction["causal_or_retarded"], f"O_detector|Z2^C: {restriction}"),
        },
    }
    return {
        "id": raw["id"], "scope": raw["scope"], "descriptions": raw["descriptions"],
        "mode_data": mode_data, "observer_data": observer_data,
        "evidence": raw["evidence"],
        "claim_boundary": f"{operational['profile_green_boundary_dependencies']} {operational['recoil_backreaction_order']} {restriction}",
    }


def build() -> dict:
    generated_by = str(Path(__file__).relative_to(ROOT))
    value = {
        "schema": "pure-weyl-residual-atlas-fragment-v1", "schema_version": "1.0.0",
        "team": "closed_universe_observer", "generated_by": generated_by,
        "generated_by_sha256": _sha256(Path(__file__)), "status_vocabulary": STATUSES,
        "description_axes": DESCRIPTIONS, "entries": [_shared_entry(row) for row in entries()],
        "verification_commands": [
            "python3 residual_atlas/validate_fragment.py closed_universe_observers/atlas/observer-atlas-fragment.json",
            "python3 -m closed_universe_observers.atlas.verify_observer_atlas_fragment",
        ],
    }
    required_scope = {"theory", "background", "boundaries", "charge_sector", "carrier", "degree", "parity", "ell", "m", "k", "omega"}
    for entry in value["entries"]:
        if set(entry["scope"]) != required_scope:
            raise AssertionError(f"incomplete mode scope: {entry['id']}")
        if set(entry["descriptions"]) != set(DESCRIPTIONS) or any(status not in STATUSES for status in entry["descriptions"].values()):
            raise AssertionError(f"invalid lifecycle status: {entry['id']}")
        if set(entry["observer_data"]) != set(OBSERVER_FIELDS):
            raise AssertionError(f"incomplete observer column: {entry['id']}")
        if not entry["evidence"] and "crosswalk" not in entry["id"]:
            raise AssertionError(f"unsupported atlas claim: {entry['id']}")
    return value


def main() -> int:
    value = build()
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    OUTPUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    print(f"wrote {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
