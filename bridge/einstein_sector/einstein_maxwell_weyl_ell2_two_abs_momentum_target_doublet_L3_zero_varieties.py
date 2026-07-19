"""Classify the candidate-1/16 scalar-input target-doublet L=3 varieties."""
from __future__ import annotations

import argparse, hashlib, json
from pathlib import Path
import sympy as sp

from bridge.einstein_sector.einstein_maxwell_weyl_two_abs_momentum_axial_axial_L4_matrix import certified_nonzero_interval, fraction_string

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_target_doublet_L3_zero_varieties.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_ell2_two_abs_momentum_target_doublet_L3_zero_varieties.schema.json"
PARENT = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_cross_fibre_amplitude_system.json"


def sha(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()
def parse(x: str) -> sp.Expr: return sp.sympify(x, locals={"sqrt": sp.sqrt, "pi": sp.pi})


def interval(x: sp.Expr) -> dict[str, object]:
    witness = certified_nonzero_interval(x)
    if witness is None: raise AssertionError("nonzero target row vanished")
    bounds, digits = witness
    return {"lower": fraction_string(bounds[0]), "upper": fraction_string(bounds[1]), "decimal_digits": digits, "excludes_zero": bounds[0] > 0 or bounds[1] < 0}


def build() -> dict[str, object]:
    parent = json.loads(PARENT.read_text())
    fibres = [f for f in parent["physical_fibres"] if f["candidate_index"] in (1, 16)]
    if [f["candidate_index"] for f in fibres] != [1, 16]: raise AssertionError("target-doublet L3 census changed")
    rows = []
    for fibre in fibres:
        if (fibre["output_ell"], fibre["first_branch_multiplicity_per_parity"], fibre["second_branch_multiplicity_per_parity"], fibre["target_cokernel_dimension_per_parity"]) != (3,1,1,2): raise AssertionError("target-doublet scope changed")
        c = {term["first_parity"][0]+term["second_parity"][0]: [parse(v[0][0]) for v in term["coefficient_matrices"]] for target in fibre["target_equations"] for term in target["terms"]}
        if not all((c["pp"][j] + 3*c["aa"][j]).equals(0) and (c["pa"][j] + c["ap"][j]).equals(0) for j in range(2)): raise AssertionError("target row relations changed")
        witnesses = {f"same_{j}": interval(c["aa"][j]) for j in range(2)} | {f"cross_{j}": interval(c["ap"][j]) for j in range(2)}
        rows.append({"candidate_index": fibre["candidate_index"], "fibre_id": fibre["fibre_id"], "rho": fibre["rho"], "coefficients": {k:[sp.sstr(x) for x in v] for k,v in c.items()}, "phase_normalization": "sqrt(pi)", "nonzero_intervals": witnesses, "zero_variety": {"ambient_dimension_over_C":20,"dimension_over_C":12,"irreducible_components_over_C":1}})
    return {
        "schema":"einstein-maxwell-weyl-ell2-two-abs-momentum-target-doublet-L3-zero-varieties-v1", "schema_path":str(SCHEMA.relative_to(ROOT)), "schema_sha256":sha(SCHEMA),
        "result_id":"EINSTEIN_MAXWELL_WEYL_ELL2_TWO_ABS_MOMENTUM_TARGET_DOUBLET_L3_ZERO_VARIETIES", "dependency_tags":["LOCAL-ALGEBRAIC","REDUCED-MODE"], "lifecycle_state":"CLASSIFIED", "generality_level":"G2",
        "scope":{"theory":"Weyl-Maxwell target","background":"candidate-1 and candidate-16 compact Plebanski-Hacyan products","boundaries":"closed S1_L times S2 before final residual quotient","charge_sector":"fixed N=2 magnetic bundle","carrier":"scalar-input target-doublet all-m L3 cross-|n| blocks","degree":2,"parity":"both","ell":"2 times 2 -> L=3","m":"all","k":"row-specific signed |n|=1,2","omega":"positive-frequency SUM"},
        "target_reduction":{"relations":["c_pp[j]=-3*c_aa[j]","c_pa[j]=-c_ap[j]"],"independent_equations":["T1(A_a,B_a)-3*T1(A_p,B_p)=0","T1(A_a,B_p)-T1(A_p,B_a)=0"],"factorization":["T1(A_a-sqrt(3)A_p,B_a+sqrt(3)B_p)=0","T1(A_a+sqrt(3)A_p,B_a-sqrt(3)B_p)=0"]},
        "representation_theorem":"T1 is the binary-quartic Jacobian; T1(f,g)=0 iff f and g are proportional. Each factor is therefore a 5x2 rank-at-most-one determinantal cone of dimension six, and their product is irreducible of dimension twelve.",
        "decompositions":rows,
        "summary":{"classified_physical_fibres":2,"dimension_per_fibre_over_C":12,"irreducible_components_per_fibre_over_C":1},
        "classification":{"both_target_doublet_L3_zero_varieties_classified":True,"all_m_irreducible_decomposition_classified":True,"target_rows_reduced_exactly":True,"other_nineteen_parent_fibre_zero_varieties_classified":False,"same_fibre_quadratic_sources_classified":False,"taub_common_zero_intersection_classified":False,"complete_two_fibre_tangent_cone_classified":False,"smooth_secular_classified":False,"causal_or_quantum_claim":False},
        "provenance":{"parent":str(PARENT.relative_to(ROOT)),"parent_sha256":sha(PARENT)},
        "claim_boundary":"This certificate classifies candidates 1 and 16 only. Aggregate progress belongs to the atlas; same-fibre, Taub and correction classes remain fail-closed."
    }


def main() -> None:
    p=argparse.ArgumentParser(); g=p.add_mutually_exclusive_group(required=True); g.add_argument("--write",action="store_true"); g.add_argument("--check",action="store_true"); a=p.parse_args()
    rendered=json.dumps(build(),indent=2,sort_keys=True)+"\n"
    if a.write: OUTPUT.write_text(rendered)
    elif not OUTPUT.exists() or OUTPUT.read_text()!=rendered: raise AssertionError("target-doublet L3 certificate stale")
    print("EINSTEIN_MAXWELL_WEYL_ELL2_TWO_ABS_MOMENTUM_TARGET_DOUBLET_L3_ZERO_VARIETIES: PASS")
if __name__=="__main__": main()
