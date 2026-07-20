#!/usr/bin/env python3
"""Build the exact scoped minimal-compensator ladder synthesis."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = (
    ROOT
    / "d_quotient_classical/compensator/"
    "COMPENSATOR_MINIMAL_LADDER_SYNTHESIS_AFTER_LEVEL3B_V1.json"
)
CERTS = ROOT / "d_quotient_classical/certificates"

IMPORTS = {
    "action_preflight": (
        "COMPLEX_COMPENSATOR_ACTION_QUARTET_PREFLIGHT_V1",
        "LOCAL_ACTION_AND_QUARTET_CERTIFIED",
        "a537e31bf667520443903551b5bf2596dff9a1c35fade88d2ffc1e89c1e0b836",
        "306ff78a2001f23124d412e9a2f41531bec74f78",
    ),
    "changed_causal_parent": (
        "COMPLEX_COMPENSATOR_VACUUM_CYLINDER_CAUSAL_PARENT_V1",
        "CHANGED_ACTION_CAUSAL_BV_PARENT_CERTIFIED",
        "be7847102b7c219fd09865b68c4982c84e280e09c73364c509dcb9aaca91d6c4",
        "08ce0b87301b60a3ff717dfe7d285184a20c3820",
    ),
    "passive_trace_obstruction": (
        "TAU_ADIC_VACUUM_CYLINDER_CAUSAL_BV_TRACE_OBSTRUCTION_V1",
        "OBSTRUCTED",
        "db1f998a0920adb94cf4fcbffb1b9eb2ea6537876aff9513aac4e4d9ec2b51b9",
        "2b834dc751d6948366fd5c3d99174c268fa50d21",
    ),
    "candidate_A": (
        "COMPENSATOR_CANDIDATE_A_R2_AUXILIARY_SCALAR_OBSTRUCTION_V1",
        "OBSTRUCTED",
        "889c3c2870bb2b28dfe2e4e510526f8644c0b7358884d07fcad351199ae747c6",
        "5c642e2ad14d45f6074b1327c69707b7b9b08f5d",
    ),
    "candidate_B": (
        "COMPENSATOR_CANDIDATE_B_UNIMODULAR_THREEFORM_OBSTRUCTION_V1",
        "OBSTRUCTED",
        "e8a8aeb97398c3b8812b20118daa56850e32a516bf4e9db15c00b99cec7a8faa",
        "cc0e0036c6acce2bc3d8ba81057031d90a71333a",
    ),
    "candidate_AB": (
        "COMPENSATOR_CANDIDATE_AB_NEITHER_COMPARISON_V1",
        "NEITHER_MINIMAL_REPAIR_SELECTED",
        "5e253ebe424dd43e308622044d93af72fd6de911b927f354977413957dbb16c4",
        "af86eb2ce4190e48fda2d276298de844bb50f4f7",
    ),
    "minimal_family": (
        "COMPENSATOR_MINIMAL_ACTION_CLASSIFICATION_AFTER_NEITHER_V1",
        "SCOPED_MINIMAL_ACTION_GOOD_LOCUS_EMPTY",
        "41ce6db6ab8fc58f4cc1ecedb205f732fd3dcee645f9408506d3535545f7026a",
        "a5924e707352bab92db2caa4c19cf4223c60f0e3",
    ),
    "active_P2": (
        "COMPENSATOR_ACTIVE_CLOCK_PX2_LOCUS_V1",
        "SCOPED_QUADRATIC_ACTIVE_CLOCK_GOOD_LOCUS_EMPTY",
        "9ad148d6b632e215cd75636f5fd5b431fa85cf1698a63f725d8b3c9dfe61de89",
        "c770752d132accb4e3b2bb59884d6faf10335fc8",
    ),
    "active_P2_audit": (
        "COMPENSATOR_ACTIVE_CLOCK_PX2_INDEPENDENT_FREEZE_AUDIT_V1",
        "SCOPED_QUADRATIC_ACTIVE_CLOCK_NO_GO_INDEPENDENTLY_FROZEN",
        "9bda4b758616427bdbf401a499ffd2b7cd9dd69a87223f05fcdf636bb31cd533",
        "f64be4a5793764ebf8871d5f1a83bd736aed7fc1",
    ),
    "active_P2_stability": (
        "COMPENSATOR_ACTIVE_CLOCK_BACKGROUND_STABILITY_V1",
        "SCOPED_ACTION_SPACE_NO_GO_BACKGROUND_STABLE_WITH_FIRST_BIFURCATION",
        "8a3afc04d72427313fe8770936b03d4f4301277c9783a92e8df6d329e8c0ccba",
        "b0ee2bea23af4af809bc0a50956c3e37d944e72f",
    ),
    "braiding_visibility": (
        "COMPENSATOR_KINETIC_BRAIDING_QUADRATIC_VISIBILITY_V1",
        "SCOPED_LEVEL2_BRAIDING_CYLINDER_QUADRATIC_INVISIBLE",
        "bfce9fd2897511d43802c504ce10f9342b85f2e3d89ce9c4cb3e66b788905e10",
        "85a54362c8c82fd98810d07234e8c6a94e57f43b",
    ),
    "braiding_level2": (
        "COMPENSATOR_KINETIC_BRAIDING_LEVEL2_NO_GO_V1",
        "SCOPED_LEVEL2_KINETIC_BRAIDING_GOOD_LOCUS_EMPTY",
        "833d7e0266fc81df2d73e9b822db29e451d8df7f0ae9e0cbe06aa391d8dcf584",
        "db36f419b03ea467f7829c1464c17c800b8aa218",
    ),
    "literal_level3": (
        "COMPENSATOR_DEGENERATE_CURVATURE_COUPLING_LEVEL3_NO_GO_V1",
        "SCOPED_LEVEL3_LITERAL_CURVATURE_COUPLING_GOOD_LOCUS_EMPTY",
        "2e687331b6985b3a84c54a0f05b210bee5e3ac06d5659b5603ac9bc25f61dfed",
        "e77ee444450890dd1df720f70c5ef5ab202fe8cc",
    ),
    "correct_level3b": (
        "COMPENSATOR_CONVENTION_CORRECT_HORNDESKI_LEVEL3B_NO_GO_V1",
        "SCOPED_LEVEL3B_CORRECT_HORNDESKI_GOOD_LOCUS_EMPTY",
        "78258a1a76c81183699e8fe6923c8eccb79c030ec8174c7fe8716a97a923713c",
        "801bff0c49a3f293fcf9402d554939b761b71341",
    ),
    "real_connection_level4": (
        "COMPENSATOR_INDEPENDENT_WEYL_CONNECTION_LEVEL4_NO_GO_V1",
        "SCOPED_LEVEL4_INDEPENDENT_WEYL_CONNECTION_GOOD_LOCUS_EMPTY",
        "d1037ef2fa9222d02513d093c27a02e6fc5da71ec0b731d3b9b2cd2f51e52652",
        "255c53253d7d846ebbe33418d03bad791945dfd4",
    ),
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _cell(status: str, statement: str) -> dict[str, str]:
    return {"status": status, "statement": statement}


def _load_imports() -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    manifest: dict[str, Any] = {}
    payloads: dict[str, dict[str, Any]] = {}
    for key, (result_id, result_state, expected_hash, source_commit) in IMPORTS.items():
        path = CERTS / f"{result_id}.json"
        actual_hash = _sha(path)
        payload = json.loads(path.read_text())
        if actual_hash != expected_hash:
            raise AssertionError(f"{key} hash drifted")
        if payload.get("result_id") != result_id:
            raise AssertionError(f"{key} result_id drifted")
        if payload.get("result_state") != result_state:
            raise AssertionError(f"{key} result_state drifted")
        manifest[key] = {
            "path": str(path.relative_to(ROOT)),
            "result_id": result_id,
            "result_state": result_state,
            "sha256": actual_hash,
            "source_commit": source_commit,
        }
        payloads[key] = payload
    return manifest, payloads


def _assert_terminal_semantics(p: dict[str, dict[str, Any]]) -> None:
    if (
        p["candidate_A"]["supersession"]["supersedes_result_id"]
        != p["changed_causal_parent"]["result_id"]
        or p["candidate_A"]["supersession"]["superseded_claim"]
        != "complete rank-390 direct-sum causal BV parent and zero strict-complement change"
    ):
        raise AssertionError("Candidate-A supersession drifted")
    if p["candidate_AB"]["terminal_selection"] != "NEITHER":
        raise AssertionError("A/B terminal selection drifted")
    if (
        p["minimal_family"]["seven_gate_classification"][
            "all_seven_gate_good_locus"
        ]
        != "EMPTY"
        or p["minimal_family"]["selection"]["candidate_C_selected"]
    ):
        raise AssertionError("minimal-family terminal disposition drifted")
    if (
        p["active_P2"]["seven_gate_classification"]["all_seven_gate_good_locus"]
        != "EMPTY"
        or p["active_P2_audit"]["freeze_verdict"][
            "all_seven_gate_good_locus"
        ]
        != "EMPTY"
        or p["active_P2_stability"]["seven_gate_stability"]["good_locus"]
        != "EMPTY_FOR_EVERY_PARAMETER_POINT_IN_N_box"
    ):
        raise AssertionError("active-P2 terminal disposition drifted")
    if (
        p["braiding_visibility"]["terminal_verdict"][
            "cylinder_quadratic_visibility"
        ]
        != "IDENTICALLY_ZERO"
        or p["braiding_level2"]["terminal_verdict"][
            "common_seven_gate_good_locus"
        ]
        != "EMPTY"
    ):
        raise AssertionError("braiding terminal disposition drifted")
    corrected = p["literal_level3"]["convention_correct_control"]
    if (
        corrected["corrected_density"]
        != "F(X)R-2F_X[(Box theta)^2-(nabla_a nabla_b theta)^2]"
        or p["literal_level3"]["terminal_verdict"]["selected_level3_action"]
    ):
        raise AssertionError("literal/corrected convention boundary drifted")
    if (
        p["correct_level3b"]["terminal_verdict"][
            "common_cylinder_Berger_good_locus"
        ]
        != "EMPTY"
        or p["correct_level3b"]["terminal_verdict"]["selected_level3b_action"]
    ):
        raise AssertionError("Level-3b terminal disposition drifted")
    if (
        p["real_connection_level4"]["terminal_verdict"][
            "independent_trace_gauge_and_nonzero_clock_charge_intersection"
        ]
        != "EMPTY"
        or p["real_connection_level4"]["terminal_verdict"][
            "selected_level4_action"
        ]
    ):
        raise AssertionError("Level-4 terminal disposition drifted")


def _row(
    family_id: str,
    action: str,
    background: str,
    evidence: list[str],
    cylinder: tuple[str, str],
    berger: tuple[str, str],
    trace: tuple[str, str],
    inertia: tuple[str, str],
    principal: tuple[str, str],
    raw_d: tuple[str, str],
    clock: tuple[str, str],
    causal: tuple[str, str],
    verdict: str,
) -> dict[str, Any]:
    return {
        "family_id": family_id,
        "exact_action_ansatz": action,
        "exact_background_ansatz": background,
        "cylinder_stationarity": _cell(*cylinder),
        "Berger_stationarity": _cell(*berger),
        "dressed_trace_disposition": _cell(*trace),
        "reduced_scalar_inertia": _cell(*inertia),
        "principal_hyperbolicity": _cell(*principal),
        "raw_D_charge": _cell(*raw_d),
        "clock_health": _cell(*clock),
        "causal_parent_status": _cell(*causal),
        "terminal_verdict": verdict,
        "evidence_import_keys": evidence,
    }


def _theory_space_table() -> list[dict[str, Any]]:
    return [
        _row(
            "PASSIVE_TAU_ADIC_STRICT_ACTION",
            "S_W=alpha_C integral sqrt(-g) C(g)^2; tau extends the formal BV/Wess-Zumino algebra but adds no classical dressed-trace kinetic or new gauge generator",
            "g_bar=-dt^2+dOmega_3^2, tau_bar=0, closed S3 Cauchy surfaces",
            ["passive_trace_obstruction"],
            ("PASS", "The unit cylinder is Bach-flat for the strict C^2 action."),
            ("NOT_COMPUTED", "No passive-tau Berger causal completion is imported."),
            ("FAIL", "u=phi_trace-2tau is an arbitrary compact-support nonboundary class."),
            ("DEGENERATE", "The classical dressed-trace Hessian is zero at every nonzero covector."),
            ("FAIL", "No Green inverse exists on the dressed-trace row."),
            ("PASS_BUT_NOT_REPAIR", "Raw D commutes with the scalar change and the odd pairing is nondegenerate, but neither removes the homology."),
            ("NOT_APPLICABLE", "No active phase-clock background is part of this row."),
            ("OBSTRUCTED", "No advanced/retarded chain homotopy exists on the complete declared tau-adic carrier."),
            "OBSTRUCTED_PASSIVE_EXTENSION_ONLY",
        ),
        _row(
            "CANDIDATE_A_TUNED_R2_AUXILIARY",
            "integral sqrt(-g_hat)[alpha_B C^2/8+chi R-chi^2/(4 beta)+R/12-1/4-(nabla theta)^2/2], beta=-1/144, chi_bar=-1/12",
            "unit cylinder g_hat=-dt^2+dOmega_3^2, R=6, theta constant; the frozen positive Berger fixture is a different action",
            ["action_preflight", "changed_causal_parent", "candidate_A"],
            ("PASS", "The tuned density F(R)=R/12-R^2/144-1/4 has F(6)=F'(6)=0."),
            ("FAIL", "The frozen positive Berger fixture has nonzero changed-action Euler residuals."),
            ("PHYSICAL_REPLACEMENT", "The compact-support u class is removed but replaced by an ordinary/generalized scalaron sector."),
            ("FAIL", "The exact homogeneous velocity Hessian has eigenvalues -3,+3 and inertia (1,1,0)."),
            ("PARTIAL", "The reduced scalar block has support-local inverses; real repeated roots and the full mixed block prevent a healthy promotion."),
            ("FAIL", "The raw-D Hamiltonian has exact witnesses +3 and -3."),
            ("FAIL", "The positive Berger clock fixture is not a solution of this action."),
            ("SUPERSEDED", "The earlier complete rank-390 direct-sum claim is superseded; only the trace Schur complement and reduced Green identities survive."),
            "OBSTRUCTED_SPLIT_SCALAR_AND_BACKGROUND_MISMATCH",
        ),
        _row(
            "CANDIDATE_B_MINIMAL_HT_THREE_FORM",
            "S_base+integral lambda_HT(vol_g_hat-dA3), with small reducible A3 gauge tower and no fixed-flux/global quotient",
            "unit cylinder with A3_bar=t vol_S3 and constant theta; frozen Berger a=1,q=9/40,theta=3t/4",
            ["action_preflight", "passive_trace_obstruction", "candidate_B"],
            ("FAIL", "The HT multiplier cannot cancel the nonzero trace-free Ricci Euler row of the unit cylinder."),
            ("PARTIAL_FAIL", "The base Berger equations pass, but L_D A3_bar=vol_Berger is nonexact under the small gauge group."),
            ("FAIL", "u=(D/2)a and H_c^4/H^3 flux data survive."),
            ("DEGENERATE", "The topological velocity Hessian vanishes and uncontrolled flux histories remain."),
            ("FAIL", "The frozen background is off shell and the HT polynomial block has a nonzero kernel."),
            ("FAIL", "i_D Omega=V_S3 d lambda_HT is nonzero on the ambient topological phase space."),
            ("FAIL", "The Berger clock requires a nonexact global A3 shift or a new superselection/gauge quotient."),
            ("OBSTRUCTED", "No complete support-local parent exists in the declared small-gauge theory."),
            "OBSTRUCTED_TRACEFREE_EULER_AND_GLOBAL_FLUX",
        ),
        _row(
            "COMPLETE_MINIMAL_POLAR_PLUS_OPTIONAL_HT",
            "integral vol_g_hat[alpha_B C^2/8+alpha_R R^2+M_P^2 R/2-Z_theta(nabla theta)^2/2-V0+alpha_E E4], optionally plus normalized HT multiplier sector",
            "common unit cylinder with constant theta and frozen Berger a=1,q=9/40,theta=3t/4",
            ["candidate_A", "candidate_B", "candidate_AB", "minimal_family"],
            ("CLASSIFIED", "Cylinder stationarity gives M_P^2=-24alpha_R and V0=-36alpha_R."),
            ("FAIL_COMMON_LOCUS", "Without HT the stacked cylinder/Berger matrix is invertible; with HT the global flux gates fail."),
            ("FAIL", "alpha_R=0 retains dressed-trace homology; alpha_R nonzero replaces it by a split auxiliary scalar; HT retains global classes."),
            ("FAIL", "The auxiliary branch has split inertia and the HT branch has null topological directions."),
            ("FAIL", "Only the dynamically empty zero vector passes the common no-HT stationary equations; HT retains a polynomial kernel."),
            ("FAIL", "Auxiliary raw D has both signs; HT raw D is non-null without superselection."),
            ("FAIL", "No common healthy frozen-Berger clock survives in the declared minimal family."),
            ("OBSTRUCTED", "The complete seven-gate locus is empty; NEITHER Candidate A nor B nor a Candidate C is selected."),
            "SCOPED_MINIMAL_FAMILY_GOOD_LOCUS_EMPTY",
        ),
        _row(
            "ACTIVE_CLOCK_QUADRATIC_P_OF_X",
            "integral vol_g_hat[alpha_B C^2/8+alpha_R R^2+M_P^2 R/2+p0+p1 X+p2 X^2+alpha_E E4], X=(nabla theta)^2",
            "unit cylinder with theta constant and Berger a=1,q=9/40,theta=3t/4; stability box 15/16<kappa<17/16,1/5<q<1/4,2/3<nu<5/6",
            ["active_P2", "active_P2_audit", "active_P2_stability"],
            ("PASS_STATIONARITY", "At the frozen point the common coefficient locus is the exact one-dimensional P2 ray."),
            ("PASS_STATIONARITY", "The same ray solves all frozen Berger Euler rows and persists as a parameter-dependent ray on the exact open box."),
            ("PHYSICAL_REPLACEMENT", "For nonzero ray parameter the R2 auxiliary sector replaces the arbitrary trace class."),
            ("FAIL", "Every nonzero point retains the exact split gravity-auxiliary pair +3,-3."),
            ("FAIL_HEALTH", "The clock cone is hyperbolic on each background in opposite standard-sign half-lines; gravity remains split."),
            ("FAIL", "The raw-D Hamiltonian has parameter-independent witnesses +3 and -3."),
            ("FAIL_COMMON_SIGN", "Cylinder health requires t<0 while frozen Berger health requires t>0; on the open box the half-lines remain opposite."),
            ("NOT_REACHED", "No complete mixed support-local parent is promoted after the exact sign separator."),
            "SCOPED_P2_GOOD_LOCUS_EMPTY_AND_INDEPENDENTLY_FROZEN",
        ),
        _row(
            "LEVEL2_FIRST_NONEXACT_KINETIC_BRAIDING",
            "S_P2+beta integral sqrt(-g_hat) X Box_hat(theta), modulo the exact constant g0 boundary term",
            "constant-clock unit cylinder and frozen Berger a=1,q=9/40,theta=3t/4",
            ["braiding_visibility", "braiding_level2"],
            ("PASS_STATIONARITY", "The exact stationary locus is the old P2 ray plus the free beta axis."),
            ("PASS_STATIONARITY", "The braiding first variation vanishes on the frozen Berger background."),
            ("FAIL_NO_REPAIR", "The complete cylinder braiding Hessian is identically zero and cannot alter the imported trace disposition."),
            ("FAIL", "Pure braiding has zero pairing; every nonzero P2 component retains split inertia."),
            ("FAIL", "Pure braiding has zero cylinder principal block; the separate Berger scalar block has rank two only."),
            ("FAIL", "Nonzero P2 components retain +3,-3 raw-D witnesses; the pure beta axis has no cylinder dynamics."),
            ("FAIL", "Berger-only visibility cannot repair a required cylinder failure."),
            ("OBSTRUCTED", "The complete declared P2 plus linear-G family has empty seven-gate locus."),
            "SCOPED_LEVEL2_GOOD_LOCUS_EMPTY",
        ),
        _row(
            "LEVEL3_LITERAL_PLUS_FX",
            "S_P2+integral sqrt(-g_hat){F(X)R_hat+F_X[(Box_hat theta)^2-(nabla_hat nabla_hat theta)^2]}, F=f0+f1X",
            "active-clock homogeneous ADM fixture; collapsed f1=0 stratum imports the unit-cylinder/frozen-Berger P2 family",
            ["braiding_level2", "literal_level3"],
            ("FAIL_DEGENERACY", "Every active-clock f1 nonzero point has det H=-324 X^2 f1^2."),
            ("NOT_COMPUTED", "No novel literal coefficient reaches Berger stationarity; f1=0 is only the failed P2 family."),
            ("NOT_REACHED", "The novel stratum fails before a dressed-trace complex is selected."),
            ("FAIL", "The lapse-acceleration velocity block has rank two for X f1 nonzero."),
            ("FAIL", "The literal coefficient misses the exact degeneracy surface B=-2F_X."),
            ("NOT_REACHED", "No novel action-origin charge sector is constructed."),
            ("NOT_REACHED", "No novel active clock reaches the clock-health gate."),
            ("OBSTRUCTED", "No full BV unary or causal parent is built after the invariant degeneracy failure."),
            "SCOPED_LITERAL_ACTION_GOOD_LOCUS_EMPTY",
        ),
        _row(
            "LEVEL3B_CONVENTION_CORRECT_LINEAR_F_HORNDESKI",
            "S_P2+integral sqrt(-g_hat){F(X)R_hat-2F_X[(Box_hat theta)^2-(nabla_hat nabla_hat theta)^2]}, F=f0+f1X",
            "constant-clock unit cylinder; no Berger sample is needed because the complete cylinder physical locus is empty",
            ["literal_level3", "active_P2_audit", "passive_trace_obstruction", "correct_level3b"],
            ("PASS_STATIONARITY", "The complete cylinder locus has M_P,eff^2=-24alpha_R and p0=36alpha_R with five free coefficients."),
            ("NOT_COMPUTED_BUT_IRRELEVANT", "Every common cylinder/Berger solution is a subset of the already-empty cylinder physical locus."),
            ("FAIL", "alpha_R=0 retains arbitrary compact-support dressed-trace homology; alpha_R nonzero replaces it with a split auxiliary pair."),
            ("FAIL", "The corrected slope is clock-only and cannot change the R2 block congruent to diag(-6,6)."),
            ("PASS_DEGENERACY_FAIL_HEALTH", "The Horndeski lapse null vector is exact, but neither exhaustive cylinder stratum is healthy."),
            ("FAIL", "The alpha_R nonzero branch retains +3,-3 raw-D witnesses; the zero branch has no trace generator."),
            ("PARTIAL", "The exact clock symbol is -2(p1+6f1)omega^2+2(p1+2f1)k^2, but clock tuning cannot repair the metric trace block."),
            ("OBSTRUCTED", "No selected action or complete causal parent exists on the complete corrected linear-F family."),
            "SCOPED_CORRECT_HORNDESKI_GOOD_LOCUS_EMPTY",
        ),
        _row(
            "LEVEL4_MINIMAL_REAL_WEYL_CONNECTION",
            "integral sqrt(-g){alpha_C C^2/8+alpha_0 R_W^2+alpha_2 Ricci_W,TF^2-zeta F_W^2/4-kappa_r(D_W rho)^2/2-kappa_R rho^2 R_W/12-kappa_theta rho^2(nabla theta)^2/2-lambda rho^4/4}",
            "local covariant gauge-rank/Ward gate; no prior cylinder or Berger background is inherited",
            ["correct_level3b", "real_connection_level4"],
            ("NOT_COMPUTED", "The exact rank/charge separator closes before a replacement cylinder is selected."),
            ("NOT_COMPUTED", "The nonzero Berger phase charge is incompatible with the independent trace-gauge stratum before background equations."),
            ("FAIL", "Delta=0 gives no new trace gauge direction; Delta nonzero forces zero phase row and arbitrary compact-support phase homology."),
            ("FAIL", "Delta nonzero forces kappa_theta=0 and hence zero phase pairing."),
            ("FAIL", "The independent stratum has a zero phase principal row."),
            ("FAIL", "A nonzero phase clock charge requires kappa_theta nonzero and therefore Delta=0, where the second Weyl column is reducible."),
            ("FAIL", "No stratum has both a new dressed-trace gauge direction and a nonzero phase clock."),
            ("OBSTRUCTED", "The exact rank/charge intersection is empty; no Green parent or selected action follows."),
            "SCOPED_MINIMAL_REAL_CONNECTION_GOOD_LOCUS_EMPTY",
        ),
    ]


def build() -> dict[str, Any]:
    imports, payloads = _load_imports()
    _assert_terminal_semantics(payloads)
    table = _theory_space_table()
    if len({row["family_id"] for row in table}) != len(table):
        raise AssertionError("duplicate family id")
    imported_keys = set(imports)
    used_keys = {key for row in table for key in row["evidence_import_keys"]}
    if used_keys != imported_keys:
        raise AssertionError(
            f"terminal import coverage mismatch: unused={sorted(imported_keys-used_keys)} "
            f"missing={sorted(used_keys-imported_keys)}"
        )
    tested_union = {
        "notation": (
            "U_tested=T_passive union M_polar_(4 metric,2 scalar)^smallHT "
            "union P2_degree<=2 union (P2+G_degree<=1) union "
            "L3_literal(F_degree<=1,+F_X) union "
            "L3b_Horndeski(F_degree<=1,-2F_X) union "
            "L4_real_Weyl_connection_minimal"
        ),
        "exhaustive_components": [
            {
                "component": "T_passive",
                "proof": "The declared tau-adic extension changes the formal BV/WZ algebra but adds neither a classical trace kinetic nor a new gauge generator.",
            },
            {
                "component": "M_polar_(4 metric,2 scalar)^smallHT",
                "proof": "Global U(1), parity evenness, the derivative bounds and four-dimensional curvature identities give the complete C2,R2,R,phase-kinetic,potential basis plus the optional normalized minimal HT sector.",
            },
            {
                "component": "P2_degree<=2",
                "proof": "Shift symmetry and the degree-two bound in the single invariant X give exactly 1,X,X^2.",
            },
            {
                "component": "P2+G_degree<=1",
                "proof": "g0 Box(theta) is horizontally exact, so beta X Box(theta) is the complete first nonexact polynomial braiding family.",
            },
            {
                "component": "L3_literal(F_degree<=1,+F_X)",
                "proof": "F=f0+f1X and B=F_X exhaust the literal declared coefficient family; exact elimination intersects degeneracy only at f1=0.",
            },
            {
                "component": "L3b_Horndeski(F_degree<=1,-2F_X)",
                "proof": "The convention-correct linear-F family is exactly degenerate and its complete cylinder stationary locus is exhausted by alpha_R=0 or alpha_R nonzero.",
            },
            {
                "component": "L4_real_Weyl_connection_minimal",
                "proof": "The lowest-order parity-even real-connection invariants and polar scalar monomials are exhausted by the printed action; Delta=0 or Delta nonzero exhausts the gauge-rank strata.",
            },
        ],
        "not_a_closure_under_hybrids": (
            "The union contains exactly the separately declared action families. "
            "It does not include simultaneous nonzero braiding and Horndeski "
            "couplings, higher functions, extra fields or changed global quotients."
        ),
        "all_components_terminal_without_selected_action": True,
        "union_good_locus": "EMPTY_IN_EACH_DECLARED_COMPONENT",
    }
    convention_reconciliation = {
        "project_X": "X=g_hat^{ab}partial_a(theta)partial_b(theta)",
        "literal_level3": {
            "coefficient": "+F_X",
            "ADM_determinant": "-324 X^2 F_X^2",
            "status": "VALID_SCOPED_LITERAL_NO_GO",
        },
        "convention_correct_level3b": {
            "coefficient": "-2F_X",
            "ADM_determinant": "0",
            "lapse_velocity_null_vector": ["0", "1"],
            "status": "VALID_SEPARATE_HORNDESKI_NO_GO_AFTER_COMPLETE_CYLINDER_SEPARATOR",
        },
        "relation": (
            "The Level-3 result is not rewritten or used as the corrected verdict. "
            "Level-3b is a separate action theorem that rederives degeneracy and "
            "then fails on split R2 inertia or surviving trace homology."
        ),
    }
    out_of_order_level4 = {
        "science_commit": "255c53253d7d846ebbe33418d03bad791945dfd4",
        "logical_position": "after the terminal Level-3b disposition",
        "independence": (
            "Its rank/charge theorem does not inherit a Level-3b action or "
            "background. It is included only as the next separately declared "
            "minimal representation class."
        ),
        "status": "SCOPED_LEVEL4_RESULT_RESEQUENCED_WITHOUT_CHANGING_CONTENT",
    }
    untested = [
        "a separated real scale connection plus an independent compact internal U(1) connection charging theta",
        "simultaneously nonzero braiding and Horndeski curvature couplings",
        "G(X) beyond the first nonexact linear polynomial",
        "nonlinear F(X), G5 or general DHOST degeneracy classes",
        "extra compensators or other matter fields",
        "fixed-flux sectors, large/global three-form quotients or changed superselection sectors",
        "other backgrounds and fixed-charge reductions",
        "general metric-affine or complex gauge geometry",
    ]
    smallest_escape = {
        "mechanism": (
            "SEPARATED_SCALE_AND_INTERNAL_U1_CONNECTIONS_ON_ONE_COMPLEX_COMPENSATOR"
        ),
        "representation_reason": (
            "A real scale generator may contract the radial/dressed-trace "
            "direction while an independent compact U(1) generator acts "
            "additively on theta. Then the Level-4 Ward implication "
            "Delta*kappa_theta=0 no longer ties trace-gauge independence to a "
            "zero phase Hessian."
        ),
        "activation": "PREFLIGHT_ONLY",
        "does_not_establish": (
            "No action, stationary locus, healthy phase space, causal parent, "
            "nonlinear q2 or quantum consistency is inferred."
        ),
    }
    verdict = {
        "selected_action": False,
        "selected_level3b_action": False,
        "success_path_causal_completion_activated": False,
        "declared_minimal_ladder_good_locus": "EMPTY",
        "scope": "EXACTLY_U_tested",
        "next_gate": "SEPARATED_SCALE_U1_CONNECTION_PREFLIGHT",
        "result": "SCOPED_MINIMAL_COMPENSATOR_LADDER_EXHAUSTED_WITHOUT_SELECTED_ACTION",
    }
    value = {
        "schema": "pure-weyl-compensator-minimal-ladder-synthesis-after-level3b-v1",
        "result_id": "COMPENSATOR_MINIMAL_LADDER_SYNTHESIS_AFTER_LEVEL3B_V1",
        "result_state": (
            "SCOPED_MINIMAL_COMPENSATOR_LADDER_EXHAUSTED_WITHOUT_SELECTED_ACTION"
        ),
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "imports": imports,
        "theory_space_columns": [
            "cylinder_stationarity",
            "Berger_stationarity",
            "dressed_trace_disposition",
            "reduced_scalar_inertia",
            "principal_hyperbolicity",
            "raw_D_charge",
            "clock_health",
            "causal_parent_status",
        ],
        "theory_space_table": table,
        "tested_union": tested_union,
        "convention_reconciliation": convention_reconciliation,
        "out_of_order_level4_reconciliation": out_of_order_level4,
        "first_genuinely_untested_mechanisms": untested,
        "smallest_representation_level_escape": smallest_escape,
        "terminal_verdict": verdict,
        "exact_checks": {
            "all_fifteen_authoritative_imports_hash_pinned": True,
            "every_import_used_by_table": True,
            "nine_declared_family_rows_unique": True,
            "all_eight_required_gate_columns_present": True,
            "candidate_A_supersession_visible": True,
            "candidate_AB_neither_visible": True,
            "literal_and_corrected_conventions_separate": True,
            "Level3b_failure_path_selected": True,
            "Level4_logically_resequenced_without_content_change": True,
            "tested_union_not_closed_under_hybrids": True,
            "no_quantum_inference": True,
        },
        "claim_flags": {
            "ALL_COMPENSATOR_OR_SCALAR_TENSOR_THEORIES_EXCLUDED": False,
            "ARBITRARY_HYBRIDS_EXCLUDED": False,
            "SELECTED_CLASSICAL_ACTION": False,
            "COMPLETE_CAUSAL_PARENT_FOR_NEXT_ESCAPE": False,
            "NONLINEAR_Q2": False,
            "HADAMARD_ANOMALY_QME_OR_QUANTUM": False,
            "PARTICLE_SCATTERING_POSITIVITY_OR_UNITARITY": False,
        },
        "claim_boundary": (
            "This exact synthesis is a hash-pinned scope theorem for precisely "
            "U_tested. Each separately declared component has an empty good "
            "locus under its own printed background and gate assumptions. It "
            "does not form arbitrary hybrids, vary unprinted functions, or "
            "exclude all compensator, scalar-tensor, Horndeski, DHOST, "
            "metric-affine or changed-global-quotient theories. The historical "
            "rank-390 direct-sum causal claim is explicitly superseded by the "
            "full Candidate-A mixed Hessian. No selected action, nonlinear q2, "
            "Hadamard state, anomaly/QME result, particle space, scattering, "
            "positivity or unitarity theorem follows."
        ),
    }
    value["content_hashes"] = {
        "imports_sha256": _digest(value["imports"]),
        "table_sha256": _digest(value["theory_space_table"]),
        "tested_union_sha256": _digest(value["tested_union"]),
        "conventions_sha256": _digest(value["convention_reconciliation"]),
        "level4_sha256": _digest(value["out_of_order_level4_reconciliation"]),
        "untested_sha256": _digest(value["first_genuinely_untested_mechanisms"]),
        "escape_sha256": _digest(value["smallest_representation_level_escape"]),
        "verdict_sha256": _digest(value["terminal_verdict"]),
    }
    return value


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    if args.write:
        OUTPUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    elif json.loads(OUTPUT.read_text()) != value:
        raise AssertionError("minimal-ladder synthesis is stale")
    print("COMPENSATOR_MINIMAL_LADDER_SYNTHESIS_AFTER_LEVEL3B_V1: PASS")


if __name__ == "__main__":
    main()
