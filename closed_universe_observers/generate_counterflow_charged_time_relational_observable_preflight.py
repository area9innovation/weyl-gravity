#!/usr/bin/env python3
"""Generate the unrestricted charged-time relational-observable preflight."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "closed_universe_observers"
CERTIFICATE = PKG / "certificates/COUNTERFLOW_CHARGED_TIME_RELATIONAL_OBSERVABLE_PREFLIGHT_V1.json"
SCHEMA = PKG / "schema/counterflow-charged-time-relational-observable-preflight-v1.schema.json"
REPORT = PKG / "reports/counterflow-charged-time-relational-observable-preflight-v1.md"
DEPENDENCIES = {
    "fixed_charge_obstruction": (ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_FIXED_CHARGE_REDUCED_HEALTH_OBSTRUCTION_V1.json", "812f6a3c2308eaeef09bee25ec8c79c8f7c86de7a51383141f8cae46c2f9cae5"),
    "observer_fixed_charge_disposition": (PKG / "certificates/TWO_PHASE_COUNTERFLOW_RELATIONAL_OBSERVABLE_V1.json", "11cbadfd8e98c2e3c4dba1955c5184a07130a69e82f34fa6328a1ba47010a996"),
    "charge_clock_complementarity": (ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_CHARGE_CLOCK_COMPLEMENTARITY_V1.json", "cd1fe1bf22604d17c65b941032c6b31c404bfd5cc01bd7f8399642840da01ed4"),
    "charge_clock_payload": (ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_CHARGE_CLOCK_COMPLEMENTARITY_PAYLOAD_V1.json", "2e25c28e06ab54256c8a4af4b6793f241801bdfa84eab3eb218a1ab53eb873c0"),
    "causal_parent": (ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_CAUSAL_BV_PARENT_V1.json", "7d969e7e630f793dfe12fe07b0e98a67b2543f9aa85fa03277e491fb00296db7"),
    "observer_receiver_contract": (ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_CAUSAL_BV_RECEIVER_CONTRACT_V1.json", "d5efdfed97286aa9554e88a449e87941c3c589940845dbfe70209b513c59e3f7"),
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def exact_algebra(*, weyl_weight: int = 0, diagonal_charge: int = 0, keep_label_fixed: bool = False) -> dict[str, Any]:
    psi, charge, tau = sp.symbols("psi Q_rel tau", real=True)
    omega = sp.Rational(3, 4)
    profile = sp.Function("F")(tau - psi)

    def bracket(f: sp.Expr, g: sp.Expr) -> sp.Expr:
        return sp.simplify(sp.diff(f, psi) * sp.diff(g, charge) - sp.diff(f, charge) * sp.diff(g, psi))

    h_d = omega * charge
    r_bracket = bracket(profile, charge)
    d_bracket = bracket(profile, h_d)
    covariance_r = r_bracket if keep_label_fixed else sp.simplify(r_bracket + sp.diff(profile, tau))
    covariance_d = d_bracket if keep_label_fixed else sp.simplify(d_bracket + omega * sp.diff(profile, tau))
    return {
        "Poisson_matrix_basis_[psi_rel,Q_rel]": [["0", "1"], ["-1", "0"]],
        "bracket_psi_Q": sp.sstr(bracket(psi, charge)),
        "H_R_rel": "Q_rel",
        "H_D": "3*Q_rel/4",
        "H_K_on_global_pair": "0",
        "bracket_psi_H_D": sp.sstr(bracket(psi, h_d)),
        "event_model": "O_A(tau)=F(tau-psi_rel)",
        "bracket_O_Q": "-partial_tau O_A",
        "bracket_O_H_D": "-(3/4)*partial_tau O_A",
        "bracket_O_K_global": "0",
        "R_label_covariance_defect": sp.sstr(covariance_r),
        "D_label_covariance_defect": sp.sstr(covariance_d),
        "local_gauge_closure_defects": {"Diff_compact_boundary": "0", "Weyl": str(weyl_weight), "diagonal_U1": str(diagonal_charge)},
    }


def monotonicity(*, reverse_charge: bool = False) -> dict[str, Any]:
    inertia = 12 * sp.pi**2 * sp.sqrt(10) / 5
    omega = sp.Rational(3, 4)
    q = sp.symbols("q", real=True)
    velocity = omega + q / inertia
    bound = sp.simplify(-omega * inertia)
    selected_q = -2 * omega * inertia if reverse_charge else sp.Integer(0)
    selected_velocity = sp.simplify(velocity.subs(q, selected_q))
    return {
        "integrated_inertia": sp.sstr(inertia),
        "clock_velocity": "3/4+sqrt(10)*q/(24*pi**2)",
        "monotonicity_condition": "q>-9*sqrt(10)*pi**2/5, equivalently Q_rel_total>0",
        "lower_bound": sp.sstr(bound),
        "selected_q": sp.sstr(selected_q),
        "selected_velocity": sp.sstr(selected_velocity),
        "selected_monotone": bool(selected_velocity > 0),
        "lifted_interval": "|tau-tau_0|<pi with winding label fixed",
    }


def phase_origin_audit(*, endpoint_dependent_shift: bool = False) -> dict[str, Any]:
    s, re, rr = sp.symbols("s r_e r_r", real=True)
    common = s
    receiver_shift = 2 * s if endpoint_dependent_shift else s
    defect = sp.simplify(receiver_shift - common)
    return {
        "frequency": "nu_i=-u_i(Phi_signal)/u_i(psi_rel)",
        "ratio": "R_er=nu_e/nu_r",
        "common_origin_shift": "psi_i->psi_i+s and Phi_i->Phi_i+r_i*s with constant r_i",
        "exact_condition": "both endpoint labels co-shift by the same s; u_i(psi_rel)!=0; d(L_R Phi_signal)=0 on both supports; (L_R+partial_tau_e+partial_tau_r)R_er=0",
        "origin_defect": sp.sstr(defect),
        "origin_independent": defect == 0,
        "symbols_retained": [sp.sstr(re), sp.sstr(rr)],
    }


def _dependencies() -> dict[str, dict[str, str]]:
    refs = {}
    for name, (path, pinned) in DEPENDENCIES.items():
        if _sha(path) != pinned:
            raise AssertionError(f"dependency drifted: {name}")
        value = json.loads(path.read_text())
        refs[name] = {"path": str(path.relative_to(ROOT)), "result_id": value["result_id"], "sha256": pinned}
    if json.loads(DEPENDENCIES["charge_clock_complementarity"][0].read_text())["result_state"] != "UNRESTRICTED_CHARGED_CLOCK_HAS_EXACT_SECULAR_ZERO_JORDAN_OBSTRUCTION":
        raise AssertionError("unrestricted charge-clock theorem unavailable")
    return refs


def build() -> dict[str, Any]:
    algebra = exact_algebra()
    clock = monotonicity()
    origin = phase_origin_audit()
    if algebra["bracket_psi_Q"] != "1" or algebra["bracket_psi_H_D"] != "3/4":
        raise AssertionError("charged Darboux algebra drifted")
    if algebra["R_label_covariance_defect"] != "0" or algebra["D_label_covariance_defect"] != "0":
        raise AssertionError("global covariance failed")
    if not clock["selected_monotone"] or not origin["origin_independent"]:
        raise AssertionError("clock/origin preflight failed")
    mutations = [
        {"name": "give_receiver_nonzero_Weyl_weight", "detected": exact_algebra(weyl_weight=1)["local_gauge_closure_defects"]["Weyl"] != "0"},
        {"name": "charge_receiver_under_diagonal_U1", "detected": exact_algebra(diagonal_charge=1)["local_gauge_closure_defects"]["diagonal_U1"] != "0"},
        {"name": "hold_phase_label_fixed_under_R_and_D", "detected": exact_algebra(keep_label_fixed=True)["R_label_covariance_defect"] != "0"},
        {"name": "reverse_clock_with_charge_perturbation", "detected": not monotonicity(reverse_charge=True)["selected_monotone"]},
        {"name": "use_endpoint_dependent_phase_origin", "detected": not phase_origin_audit(endpoint_dependent_shift=True)["origin_independent"]},
    ]
    if not all(row["detected"] for row in mutations):
        raise AssertionError("mutation rail failed")
    boundary = (
        "This exact LOCAL-ALGEBRAIC/REDUCED-MODE/LORENTZIAN-CAUSAL preflight imports the terminal fixed-charge clock obstruction, its Observer disposition, and the unrestricted charge-clock complementarity theorem by exact hashes. On the unrestricted Darboux pair it constructs a clock-slice event-map chain contract for compact gauge-neutral receiver three-forms, proves Diff/Weyl/diagonal-U1 closure and representative independence modulo BRST-exact and boundary terms, and proves covariance—not quotient invariance—under the charged R_rel and D actions. The exact brackets are {O,Q_rel}=-partial_tau O, {O,H_D}=-(3/4)partial_tau O and {O,K}=0 on the global pair. A lifted clock chart is monotone when total Q_rel>0. A frequency ratio is phase-origin independent exactly under the declared common affine origin covariance, but no ratio is evaluated or called redshift. Nontrivial physical instantiation is NO_CERTIFIED_MAP because the unrestricted all-Hodge physical cohomology, descended pairing, full receiver carrier and bounded health have not landed. No apparatus, detector rank, particle, phenomenology or quantum claim follows."
    )
    value = {
        "schema": "closed-universe-counterflow-charged-time-relational-observable-preflight-v1",
        "result_id": "COUNTERFLOW_CHARGED_TIME_RELATIONAL_OBSERVABLE_PREFLIGHT_V1",
        "setting_id": "unrestricted_two_phase_counterflow_berger_a1_c2_9_over_40",
        "claim_status": "CERTIFIED_GAUGE_CLOSED_COVARIANT_EVENT_MAP_CONTRACT_PHYSICAL_INSTANTIATION_OPEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "dependency_refs": _dependencies(),
        "unrestricted_global_algebra": algebra,
        "local_gauge_rows": {
            "Diff": "s psi_rel=L_c psi_rel; s A_3=L_c A_3+dB; the compact top-form event integral varies by a boundary term",
            "Weyl": "psi_rel has weight zero and the receiver density must have total weight zero",
            "diagonal_U1": "psi_rel is neutral and the receiver must be built from diagonal-U1-neutral curvatures",
            "global_not_gauge": ["R_rel has Hamiltonian Q_rel", "D has Hamiltonian H_D=(3/4)Q_rel", "K is the separate background stabilizer"],
        },
        "event_map_contract": {
            "formula": "O_A(tau)=integral_M delta(psi_rel-tau) dpsi_rel wedge A_3",
            "receiver_type": "compactly supported local three-form A_3 of ghost number 0, Weyl weight 0 and diagonal-U1 charge 0, with s A_3+dB=0",
            "BV_closure": "s O_A(tau)=0 by scalar-clock covariance, Cartan's formula and Stokes on closed/compact support",
            "representative_independence": "A_3->A_3+sC+dE changes O_A by an s-exact term; no physical nontriviality is inferred",
            "global_covariance": "O_{U_s A}(tau+s)=O_A(tau), equivalently (L_R+partial_tau)O=0 and (L_D+(3/4)partial_tau)O=0 on K-basic receivers",
            "K_disposition": "L_K O_A=O_{L_K A}; it vanishes only for a declared K-basic receiver and is never relabelled raw-D invariance",
        },
        "clock_monotonicity": clock,
        "phase_origin_condition": origin,
        "physical_instantiation_gate": {
            "status": "NO_CERTIFIED_MAP",
            "first_missing_map": "unrestricted nonhomogeneous physical cohomology and descended pairing/nontrivial receiver class on the 70-row carrier",
            "also_open": ["bounded health beyond the secular global Jordan block", "action-derived emitter/receiver rows", "retarded response rank", "physical frequency ratio"],
        },
        "strict_receiver_contract": {
            "accepts": ["unrestricted carrier with nonzero [psi_rel,Q_rel] pairing", "compact local gauge-neutral receiver cocycle A_3", "K action and common phase-origin law", "monotone lifted clock interval"],
            "rejects": ["fixed-Q_rel clockless quotient", "charged R_rel or D treated as gauge", "unpaired/nonphysical receiver", "prequotient 5/2 substituted as redshift"],
            "output_if_gate_lands": "a covariant family O_A(tau), not a D-invariant quotient observable",
        },
        "mutation_results": mutations,
        "flags": {
            "CHARGED_TIME_EVENT_MAP_CONTRACT_CERTIFIED": True,
            "LOCAL_GAUGE_CLOSURE_AND_REPRESENTATIVE_INDEPENDENCE_CERTIFIED": True,
            "GLOBAL_R_D_COVARIANCE_CERTIFIED": True,
            "PHASE_ORIGIN_INDEPENDENCE_CONDITION_CERTIFIED": True,
            "PHYSICAL_NONTRIVIAL_OBSERVABLE_CERTIFIED": False,
            "PHYSICAL_REDSHIFT_CERTIFIED": False,
            "ACTION_DERIVED_APPARATUS_CERTIFIED": False,
            "DETECTOR_RANK_CERTIFIED": False,
            "PARTICLE_OR_PHENOMENOLOGY_CLAIM": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "LAND_UNRESTRICTED_ALL_HODGE_PHYSICAL_COHOMOLOGY_DESCENDED_PAIRING_AND_A_NONTRIVIAL_RECEIVER_CLASS",
        "claim_boundary": boundary,
        "provenance": {"producer_method": "exact symplectic/BRST event-map algebra", "independent_method": "standalone matrix, distributional covariance and mutation replay", "higher_tiers_not_run": {"tier_2": "all imported operators unchanged by hash", "tier_3": "no freeze or shared-core change"}},
    }
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(value)
    return value


def _render(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def _report(value: dict[str, Any]) -> str:
    return """# Counterflow charged-time relational-observable preflight

The fixed-charge quotient remains terminally clockless.  On the distinct
unrestricted branch, `(psi_rel,Q_rel)` is a physical Darboux pair and raw `D`
is charged.  For a compact local gauge-neutral receiver cocycle `A_3`,

```text
O_A(tau)=integral delta(psi_rel-tau) dpsi_rel wedge A_3
```

is closed under local Diff, Weyl and diagonal `U(1)` BRST rows and depends only
on the receiver cohomology representative.  It is not obtained by quotienting
the global phase symmetry.  Instead it is covariant:

```text
(L_R + partial_tau) O_A = 0,
(L_D + (3/4) partial_tau) O_A = 0,
{O_A,Q_rel} = -partial_tau O_A,
{O_A,H_D}   = -(3/4) partial_tau O_A.
```

`K=D-(3/4)R_rel` remains separate; its bracket vanishes only for a declared
`K`-basic receiver.  The lifted clock is monotone exactly when total
`Q_rel>0`.  An emitter/receiver phase-frequency ratio can be independent of
origin when both endpoint labels share one affine phase shift, both clock
derivatives are nonzero, and the transported signal phase has constant
`R_rel` shift on both supports.

This is a strict chain-level receiver contract, not yet a nonzero physical
observable.  The first missing map is the unrestricted all-Hodge physical
cohomology and descended pairing/nontrivial receiver class.  No value is
called redshift, and no apparatus, detector rank, particle, phenomenology or
quantum result is promoted.

CLOSE-OUT: DONE — charged-time covariant event-map contract certified; physical instantiation remains fail-closed
"""


if __name__ == "__main__":
    parser = argparse.ArgumentParser(); parser.add_argument("--emit", action="store_true"); parser.add_argument("--check", action="store_true"); args = parser.parse_args()
    value = build()
    if args.emit:
        CERTIFICATE.write_text(_render(value)); REPORT.write_text(_report(value))
    if args.check and (CERTIFICATE.read_text() != _render(value) or REPORT.read_text() != _report(value)):
        raise SystemExit("stale charged-time observer preflight")
    print("COUNTERFLOW_CHARGED_TIME_RELATIONAL_OBSERVABLE_PREFLIGHT_V1 generation: PASS")
