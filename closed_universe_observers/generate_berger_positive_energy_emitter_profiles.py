#!/usr/bin/env python3
"""Select compact emitter Cauchy data by positive-energy duality."""

from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
from typing import Any
from jsonschema import Draft202012Validator
import sympy as sp

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = PACKAGE / "certificates/BERGER_POSITIVE_ENERGY_DETECTOR_SELECTED_EMITTER_PROFILES.json"
SCHEMA = PACKAGE / "schema/berger-positive-energy-detector-selected-emitter-profiles-v1.schema.json"
REPORT = PACKAGE / "reports/berger-positive-energy-detector-selected-emitter-profiles.md"
DEPENDENCIES = {
    "covectors": PACKAGE / "certificates/BERGER_EXACT_DETECTOR_SMEARINGS_AND_ADVANCED_COVECTORS.json",
    "switches": PACKAGE / "certificates/BERGER_EXACT_NORMALIZED_EMITTER_SWITCH_PROFILES.json",
    "rank_two": PACKAGE / "certificates/BERGER_DYNAMICAL_EMITTER_CAUCHY_RANK_TWO.json",
    "emitter_model": PACKAGE / "certificates/BERGER_POLARIZATION_TWO_FORM_EMITTER_HANDOFF.json",
}
SOURCE_FILES = {"producer": Path(__file__), "verifier": PACKAGE / "verify_berger_positive_energy_emitter_profiles.py", "tests": PACKAGE / "tests/test_berger_positive_energy_emitter_profiles.py", "schema": SCHEMA, "report": REPORT}

def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def energy_dual_audit(*, flip_dual_sign: bool = False, delete_configuration_term: bool = False) -> dict[str, Any]:
    lam, mass2 = sp.symbols("lambda m2", positive=True)
    L = lam + mass2
    omega = sp.Matrix([[0, 1], [-1, 0]])
    dual = sp.Matrix([[0, -1], [0 if delete_configuration_term else L, 0]])
    if flip_dual_sign:
        dual = -dual
    gram = sp.simplify(omega * dual)
    expected = sp.diag(L, 1)
    return {
        "cauchy_order": ["q", "p"],
        "spatial_operator": "L_a=Delta_(2,Sigma)^co-closed+m_a^2",
        "symplectic_matrix": [[str(x) for x in omega.row(i)] for i in range(2)],
        "positive_energy_dual_matrix": [[sp.sstr(x) for x in dual.row(i)] for i in range(2)],
        "selected_profile": "u_a=(-p_a,L_a q_a)",
        "omega_times_dual": [[sp.sstr(x) for x in gram.row(i)] for i in range(2)],
        "energy": "<p_a,p_a>+<q_a,L_a q_a>",
        "strictly_positive_for_nonzero_covector_data": gram == expected,
        "mass_gap": "L_a>=m_a^2>0",
    }

def support_audit() -> dict[str, Any]:
    rows = [
        {"id": "u_0", "cauchy_slice_physical_time": "1/8", "switch_start": "7/48", "gap": "1/48"},
        {"id": "u_1", "cauchy_slice_physical_time": "7/24", "switch_start": "5/16", "gap": "1/48"},
    ]
    defects = [sp.Rational(x["switch_start"]) - sp.Rational(x["cauchy_slice_physical_time"]) - sp.Rational(x["gap"]) for x in rows]
    return {
        "profiles": rows,
        "all_slice_gap_defects_zero": all(x == 0 for x in defects),
        "support_statement": "Cauchy(V_a^adv) is supported in the causal past shadow of compact w_a; applying p->-p and the differential spatial operator L_a does not enlarge support",
        "constraint_statement": "delta_Sigma q_a=delta_Sigma p_a=0 and [delta_Sigma,L_a]=0 imply delta_Sigma u_a=0",
        "compact_and_constraint_compatible": True,
        "receiver_adjacent_no_wrap_scope": "the slices are exactly 1/48 before their switches and remain in the previously certified receiver-adjacent causal patches",
    }

def build() -> dict[str, Any]:
    values = {k: json.loads(p.read_text()) for k,p in DEPENDENCIES.items()}
    required = {"covectors":"ADVANCED_DETECTOR_TO_EMITTER_COVECTOR_OPERATOR_EXPORTED", "switches":"EXACT_H0_H1_SWITCH_PROFILES_SERIALIZED", "rank_two":"DYNAMICAL_EMITTER_LEADING_RECORD_MATRIX_RANK_TWO_CERTIFIED", "emitter_model":"SPECIFIC_DYNAMICAL_EMITTER_MODEL_SELECTED"}
    for name, flag in required.items():
        if values[name].get("flags",{}).get(flag) is not True: raise AssertionError(f"dependency flag dropped: {name}.{flag}")
    energy = energy_dual_audit(); support = support_audit()
    sign = energy_dual_audit(flip_dual_sign=True); missing = energy_dual_audit(delete_configuration_term=True)
    if not energy["strictly_positive_for_nonzero_covector_data"] or not support["all_slice_gap_defects_zero"]: raise AssertionError("positive-energy profile selection failed")
    if sign["strictly_positive_for_nonzero_covector_data"] or missing["strictly_positive_for_nonzero_covector_data"]: raise AssertionError("energy-dual mutation escaped")
    boundary = "This exact LOCAL-ALGEBRAIC/LORENTZIAN-CAUSAL certificate converts each already-fixed advanced detector covector with physical massive-two-form Cauchy data v_a=(q_a,p_a) into the detector-selected preparation u_a=(-p_a,L_a q_a), where L_a=Delta_(2,Sigma)^co-closed+m_a^2. The Cauchy symplectic pairing is ell_a(u_a)=||p_a||^2+<q_a,L_a q_a>>0 for every nonzero covector because m_a^2>0. The construction uses no response normalization, preserves the co-closed constraint, and does not enlarge the compact receiver-adjacent causal support. Exact slices lie 1/48 before each emitter switch. This exports an operator-defined compact Cauchy profile, not evaluated coordinate or harmonic coefficients. It does not evaluate the advanced Green images, compute the absolute-g^3 recoil coefficient, construct the PBW q2 payload, solve backreaction, establish finite-parameter Green theory or the full Dirac algebra, or make a quantum claim."
    return {
        "schema":"closed-universe-berger-positive-energy-detector-selected-emitter-profiles-v1", "result_id":"BERGER_POSITIVE_ENERGY_DETECTOR_SELECTED_EMITTER_PROFILES", "setting_id":values["rank_two"]["setting_id"], "claim_status":"OPERATOR_DEFINED_DETECTOR_SELECTED_COMPACT_CAUCHY_PROFILES_EXPORTED_HARMONIC_EVALUATION_OPEN", "dependency_tags":["LOCAL-ALGEBRAIC","LORENTZIAN-CAUSAL"],
        "dependency_refs":{k:{"path":str(p.relative_to(ROOT)),"result_id":values[k]["result_id"],"sha256":_sha256(p)} for k,p in DEPENDENCIES.items()},
        "positive_energy_dual":energy, "causal_support_and_constraint":support,
        "selection_rule":{"advanced_data":"v_a=Cauchy(G_Ea,adv[g_a h_a d G_A,adv delta(chi_a P_a)])", "profile":"u_a=(-p_a,L_a q_a)", "response":"kappa_a=ell_a(u_a)=E_a[v_a]>0", "adaptive_response_normalization":False},
        "mutation_results":[{"name":"flip_positive_energy_dual_sign","detected":True},{"name":"delete_Lq_configuration_term","detected":True}],
        "flags":{"OPERATOR_DEFINED_DETECTOR_SELECTED_COMPACT_CAUCHY_PROFILES_EXPORTED":True,"LEADING_DIAGONAL_RESPONSES_POSITIVE_ENERGY_WITNESSES":True,"CO_CLOSED_CONSTRAINT_PRESERVED":True,"CAUSAL_SUPPORT_NOT_ENLARGED":True,"HARMONIC_COEFFICIENTS_EVALUATED":False,"ADVANCED_GREEN_IMAGES_EVALUATED":False,"DETECTOR_RECOIL_NUMERICAL_COEFFICIENT_EVALUATED":False,"QUANTUM_CLAIM":False},
        "next_gate":"EXPAND_THE_FIXED_ADVANCED_COVECTORS_AND_POSITIVE_ENERGY_DUALS_IN_BERGER_PETER_WEYL_MODES_WITH_VALIDATED_TAIL_BOUNDS", "claim_boundary":boundary,
        "provenance":{"source_commit":"WORKTREE","source_manifest":[{"path":str(p.relative_to(ROOT)),"sha256":_sha256(p)} for p in SOURCE_FILES.values()]}
    }

def main() -> int:
    ap=argparse.ArgumentParser(description=__doc__); ap.add_argument("--emit",action="store_true"); ap.add_argument("--check",action="store_true"); args=ap.parse_args()
    value=build(); schema=json.loads(SCHEMA.read_text()); Draft202012Validator.check_schema(schema); Draft202012Validator(schema).validate(value); rendered=json.dumps(value,indent=2,sort_keys=True)+"\n"
    if args.emit: CERTIFICATE.write_text(rendered)
    if args.check and (not CERTIFICATE.exists() or CERTIFICATE.read_text()!=rendered): raise SystemExit("stale positive-energy emitter profile certificate")
    print("BERGER_POSITIVE_ENERGY_DETECTOR_SELECTED_EMITTER_PROFILES generation: PASS"); return 0
if __name__=="__main__": raise SystemExit(main())
