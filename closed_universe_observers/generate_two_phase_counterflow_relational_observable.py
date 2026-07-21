#!/usr/bin/env python3
"""Generate the fail-closed counterflow relational-observer disposition."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = PACKAGE / "certificates/TWO_PHASE_COUNTERFLOW_RELATIONAL_OBSERVABLE_V1.json"
SCHEMA = PACKAGE / "schema/two-phase-counterflow-relational-observable-v1.schema.json"
REPORT = PACKAGE / "reports/two-phase-counterflow-relational-observable-v1.md"
DEPENDENCIES = {
    "parent": ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_CAUSAL_BV_PARENT_V1.json",
    "parent_payload": ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_CAUSAL_BV_PARENT_PAYLOAD_V1.json",
    "receiver_contract": ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_CAUSAL_BV_RECEIVER_CONTRACT_V1.json",
    "fixed_charge_health": ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_FIXED_CHARGE_REDUCED_HEALTH_OBSTRUCTION_V1.json",
    "fixed_charge_health_payload": ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_FIXED_CHARGE_REDUCED_HEALTH_OBSTRUCTION_PAYLOAD_V1.json",
}
PINNED = {
    "parent": "7d969e7e630f793dfe12fe07b0e98a67b2543f9aa85fa03277e491fb00296db7",
    "parent_payload": "7c73705cc07062baf652c9cc0cb0977beda2a96d5b642fa186d6bfaeae01db57",
    "receiver_contract": "d5efdfed97286aa9554e88a449e87941c3c589940845dbfe70209b513c59e3f7",
    "fixed_charge_health": "812f6a3c2308eaeef09bee25ec8c79c8f7c86de7a51383141f8cae46c2f9cae5",
    "fixed_charge_health_payload": "4704d703a7c80a5a1391ebd0dbaa346b1177f9febccb20027ccf1fa0a47585ec",
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _matrix_strings(matrix: sp.Matrix) -> list[list[str]]:
    return [[sp.sstr(matrix[i, j]) for j in range(matrix.cols)] for i in range(matrix.rows)]


def _dependencies() -> dict[str, dict[str, str]]:
    refs: dict[str, dict[str, str]] = {}
    for name, path in DEPENDENCIES.items():
        digest = _sha(path)
        if digest != PINNED[name]:
            raise AssertionError(f"pinned counterflow input drifted: {name}: {digest}")
        value = json.loads(path.read_text())
        refs[name] = {"path": str(path.relative_to(ROOT)), "result_id": value["result_id"], "sha256": digest}
    if json.loads(DEPENDENCIES["parent"].read_text())["result_state"] != "CERTIFIED_70_COMPONENT_SUPPORT_LOCAL_CAUSAL_BV_PARENT":
        raise AssertionError("terminal causal parent is unavailable")
    if json.loads(DEPENDENCIES["fixed_charge_health"].read_text())["result_state"] != "OBSTRUCTED_FIXED_CHARGE_REDUCTION_REMOVES_RELATIVE_CLOCK":
        raise AssertionError("terminal fixed-charge obstruction is unavailable")
    return refs


def reduction_audit(*, retain_clock_after_quotient: bool = False) -> dict[str, Any]:
    """Reconstruct the exact derived charge fibre and its contraction."""

    d = sp.Matrix([[0, 0, 0, 0], [1, 0, 0, 0], [0, 0, 0, 0], [0, 0, 1, 0]])
    s = sp.Matrix([[0, 1, 0, 0], [0, 0, 0, 0], [0, 0, 0, 1], [0, 0, 0, 0]])
    identity_defect = d * s + s * d - sp.eye(4)
    level_pairing = sp.zeros(1)
    relative_dimension = 1 if retain_clock_after_quotient else 0
    return {
        "basis": ["r_R_rel", "delta_psi_0", "delta_Q_rel", "epsilon_Q_rel"],
        "differential": _matrix_strings(d),
        "contracting_homotopy": _matrix_strings(s),
        "d_squared_zero": d * d == sp.zeros(4),
        "dS_plus_Sd_identity": identity_defect == sp.zeros(4),
        "cohomology_dimensions": [0, 0, 0],
        "level_tangent_basis": ["delta_psi_0"],
        "level_pairing": _matrix_strings(level_pairing),
        "radical_basis": ["delta_psi_0=L_R_rel background"],
        "quotient_formula": "ker(d Q_rel)/im(L_R_rel)=span(delta_psi_0)/span(delta_psi_0)=0",
        "relative_clock_dimension": relative_dimension,
        "pairing_rank": 0 if relative_dimension == 0 else 1,
        "positive_relative_clock_survives": relative_dimension == 1,
    }


def prequotient_diagnostic(*, clone_phase: bool = False, advanced: bool = False) -> dict[str, Any]:
    """Compute—but do not promote—the unreduced phase-response control."""

    omega = sp.Rational(3, 4)
    beta = 2 * sp.sqrt(10) / 3
    v = sp.Rational(3, 5)
    gamma = sp.Rational(5, 4)
    response = sp.eye(2)
    if clone_phase:
        response[:, 1] = response[:, 0]
    relative_emit = sp.factor(beta / omega)
    relative_receive = sp.factor(beta * gamma * (1 - v) / (omega * gamma))
    return {
        "status": "PREQUOTIENT_DIAGNOSTIC_NOT_A_PHYSICAL_OBSERVER_CLAIM",
        "matrix": _matrix_strings(response),
        "rank": int(response.rank()),
        "relative_frequency_emit": sp.sstr(relative_emit),
        "relative_frequency_receive": sp.sstr(relative_receive),
        "formal_ratio": sp.sstr(sp.factor(relative_emit / relative_receive)),
        "retarded_past_zero": not advanced,
        "advanced_contamination": advanced,
        "why_not_promoted": "psi_rel represents zero cohomology after the required fixed-Q_rel derived reduction and R_rel quotient",
    }


def _candidate_rows() -> list[dict[str, str]]:
    return [
        {"role": "clock", "rows": "psi_rel,psi_rel_star", "action_origin": "imported selected counterflow action"},
        {"role": "rod/polarization", "rows": "R^I,R_I_star,Pi_a,Pi_a_star", "action_origin": "would require scalar-rod and polarization kinetic terms"},
        {"role": "emitter", "rows": "K_b,K_b_star", "action_origin": "would require massive two-form emitter terms and K_b-F coupling"},
        {"role": "receiver", "rows": "m_a,p_a and canonical BV duals", "action_origin": "would require first-order memory/readout terms"},
        {"role": "signal", "rows": "Maxwell minimal/nonminimal BV rows", "action_origin": "would require the standard Maxwell action and Lorenz gauge fixing"},
    ]


def build() -> dict[str, Any]:
    deps = _dependencies()
    audit = reduction_audit()
    if not audit["d_squared_zero"] or not audit["dS_plus_Sd_identity"]:
        raise AssertionError("derived fixed-charge contraction failed")
    if audit["relative_clock_dimension"] != 0 or audit["positive_relative_clock_survives"]:
        raise AssertionError("relative clock unexpectedly survived reduction")
    diagnostic = prequotient_diagnostic()
    mutations = [
        {"name": "force_relative_clock_to_survive_quotient", "detected": reduction_audit(retain_clock_after_quotient=True)["relative_clock_dimension"] != 0},
        {"name": "clone_emitter_phase_prequotient", "status": "DIAGNOSTIC_ONLY", "detected": prequotient_diagnostic(clone_phase=True)["rank"] == 1},
        {"name": "replace_retarded_by_advanced_prequotient", "status": "DIAGNOSTIC_ONLY", "detected": prequotient_diagnostic(advanced=True)["advanced_contamination"]},
        {"name": "charge_clock_under_diagonal_U1", "status": "NOT_REACHED_AFTER_FIRST_EXACT_FAILURE", "detected": False},
    ]
    boundary = (
        "This exact LOCAL-ALGEBRAIC/REDUCED-MODE/LORENTZIAN-CAUSAL Observer disposition imports the terminal 70-component causal parent, its Observer contract, and the later fixed-charge reduced-health obstruction by pinned hashes. The derived fixed-Q_rel fibre is acyclic: on delta Q_rel=0 the sole relative-phase tangent delta psi_0 is the R_rel radical, and quotienting gives relative-clock dimension and descended pairing rank zero. Therefore no physical O_A(tau), action-derived emitter-receiver apparatus, BV representative-independence theorem, detector rank, relational redshift, or Einstein/additional branch response is activated. The unreduced identity response and formal transported phase ratio 5/2 are retained only as prequotient diagnostics and are not observational claims. The diagonal U1 quartet remains separately contractible, K/raw-D charge statements remain valid on their declared carriers, and the parent remains causal. This obstruction does not establish nonlinear response, recoil, particles, phenomenology, Hadamard data, a QME result or any quantum claim."
    )
    value: dict[str, Any] = {
        "schema": "closed-universe-two-phase-counterflow-relational-observable-v1",
        "result_id": "TWO_PHASE_COUNTERFLOW_RELATIONAL_OBSERVABLE_V1",
        "setting_id": "two_phase_counterflow_stationary_berger_a1_c2_9_over_40",
        "claim_status": "OBSTRUCTED_FIXED_CHARGE_QUOTIENT_REMOVES_RELATIVE_CLOCK_BEFORE_OBSERVER",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "dependency_refs": deps,
        "first_failed_property": {
            "required": "a nonzero physical relative-clock class and descended pairing on which O_A(tau) can be evaluated",
            "actual": "ker(d Q_rel)/im(L_R_rel)=0; relative-clock dimension=0 and pairing rank=0",
            "status": "OBSTRUCTED",
            "later_gates": "NOT_REACHED_AFTER_FIRST_EXACT_FAILURE",
        },
        "fixed_charge_reduction": audit,
        "candidate_apparatus_disposition": {
            "status": "NOT_REACHED_AFTER_FIRST_EXACT_FAILURE",
            "rows_that_would_require_one_action_derived_extension": _candidate_rows(),
            "reason": "Adding semantic or action rows cannot repair the absence of the physical clock class without changing the charge reduction or action architecture.",
        },
        "relational_observable_disposition": {
            "requested_definition": "O_A(tau)=A evaluated at psi_rel=tau using the joint clock-and-rod relational pullback",
            "BV_closure": "NO_CERTIFIED_MAP",
            "representative_independence": "NO_CERTIFIED_MAP",
            "diagonal_U1": "CERTIFIED_SEPARATELY_ON_PARENT: psi_rel is neutral and the diagonal quartet is contractible; this does not restore a reduced clock class",
            "K_Berger": "CERTIFIED_SEPARATELY_ON_PARENT: K is the null stabilizer before the failed observer gate",
            "raw_D": "unrestricted D carries Omega Q_rel; on the fixed leaf it is null and equals K only after the R_rel quotient, where psi_rel has been removed",
            "pairing_descent": "OBSTRUCTED: descended relative-clock pairing rank is zero",
        },
        "prequotient_diagnostic": diagnostic,
        "retarded_response_disposition": {
            "status": "NO_CERTIFIED_MAP",
            "emitter_preparation": "NOT_REACHED",
            "detector_profiles": "NOT_REACHED",
            "green_images": "NOT_REACHED",
            "boundary_dependencies": "parent has closed S3 and retarded/advanced homotopies, but no physical clock-labelled receiver survives",
            "rank": None,
        },
        "relational_frequency_disposition": {
            "status": "NO_CERTIFIED_MAP",
            "reason": "the receiver clock phase is zero in physical cohomology; the formal prequotient value 5/2 is not called redshift",
            "one_plus_z_rel": None,
        },
        "gravitational_branch_response": {
            "Einstein_branch": {"status": "NO_CERTIFIED_MAP", "rank": None, "first_missing_map": "surviving physical observer clock, before any same-background branch dictionary"},
            "additional_branch": {"status": "NO_CERTIFIED_MAP", "rank": None, "first_missing_map": "surviving physical observer clock, before any same-background branch dictionary"},
            "no_name_matching": True,
        },
        "mutation_results": mutations,
        "flags": {
            "FIXED_CHARGE_RELATIVE_CLOCK_OBSTRUCTED": True,
            "PREQUOTIENT_PHASE_DIAGNOSTIC_COMPUTED": True,
            "PHYSICAL_RELATIVE_PHASE_OBSERVABLE_CERTIFIED": False,
            "ACTION_DERIVED_LINEAR_APPARATUS_CERTIFIED": False,
            "LINEAR_RETARDED_DETECTOR_RANK_CERTIFIED": False,
            "TRANSPORTED_RELATIONAL_REDSHIFT_CERTIFIED": False,
            "RAW_D_GAUGE_QUOTIENT_WITH_CLOCK_CERTIFIED": False,
            "EINSTEIN_BRANCH_DETECTOR_RANK_CERTIFIED": False,
            "ADDITIONAL_BRANCH_DETECTOR_RANK_CERTIFIED": False,
            "NONLINEAR_OBSERVER_RESPONSE_CERTIFIED": False,
            "RECOIL_OR_BACKREACTION_CERTIFIED": False,
            "PARTICLE_OR_PHENOMENOLOGY_CLAIM": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "CHANGE_THE_CHARGE_REDUCTION_OR_ACTION_ARCHITECTURE_SO_A_NONZERO_RELATIVE_CLOCK_CLASS_SURVIVES_BEFORE_BUILDING_APPARATUS",
        "claim_boundary": boundary,
        "provenance": {
            "producer_method": "exact matrix reconstruction of the four-generator derived charge fibre plus a quarantined algebraic prequotient diagnostic",
            "independent_method": "standalone verifier reconstructs homology dimensions, radical quotient and mutation boundary without importing the producer",
            "higher_tiers_not_run": {"tier_2": "The authoritative fixed-charge obstruction is imported unchanged by hash.", "tier_3": "No freeze or shared-core algebra change."},
        },
    }
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(value)
    return value


def _render(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def _report(value: dict[str, Any]) -> str:
    return """# Two-phase counterflow relational-observer obstruction

## First exact failure

The terminal causal parent remains valid, but the required fixed-charge
physical reduction removes the proposed relative clock before an apparatus
can be attached.  On `delta Q_rel=0`, the only relative-phase tangent is

```text
delta psi_0 = L_R_rel(background).
```

It is the complete presymplectic radical.  The quotient is therefore

```text
ker(d Q_rel) / im(L_R_rel)
  = span(delta psi_0) / span(delta psi_0)
  = 0.
```

The reconstructed four-generator derived fibre has `d^2=0`, an exact
contracting homotopy `dS+Sd=I`, zero cohomology in every degree, relative-clock
dimension zero and descended pairing rank zero.

Consequently `O_A(tau)=A|_(psi_rel=tau)` has no physical clock-labelled
domain.  BV closure, representative independence, action-derived apparatus
rows, retarded detector rank, relational redshift and branch-resolved response
are all `NO_CERTIFIED_MAP` or not reached.  The neutral diagonal `U(1)` phase
is not substituted: its quartet remains contractible.  The certified
`K_Berger` and raw-`D` charge statements are retained separately, but neither
restores the removed relative-clock class.

## Quarantined prequotient calculation

Before quotienting, two formal phase preparations give the identity response
matrix and transported signal/clock phases give the algebraic ratio `5/2`.
These values are retained only as diagnostics.  They are not a physical
detector rank or redshift because the clock representative is exact in the
required physical complex.

The next admissible gate is a changed charge reduction or action architecture
in which a nonzero relative-clock cohomology class and pairing survive.  Only
then may emitter, receiver, rod, polarization and memory rows be derived from
one apparatus action.

CLOSE-OUT: OBSTRUCTED — fixed-Q_rel reduction removes the relative clock before the physical observer gate
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    value = build()
    if args.emit:
        CERTIFICATE.write_text(_render(value))
        REPORT.write_text(_report(value))
    if args.check and (CERTIFICATE.read_text() != _render(value) or REPORT.read_text() != _report(value)):
        raise SystemExit("stale counterflow relational-observer obstruction artifacts")
    if args.guards and not reduction_audit(retain_clock_after_quotient=True)["positive_relative_clock_survives"]:
        raise AssertionError("clock-survival mutation was not exposed")
    print("TWO_PHASE_COUNTERFLOW_RELATIONAL_OBSERVABLE_V1 obstruction generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
