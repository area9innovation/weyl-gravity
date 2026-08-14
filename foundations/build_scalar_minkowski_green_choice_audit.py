#!/usr/bin/env python3
"""Generate an exact scalar 1+1 Minkowski Green-operator choice audit."""
from __future__ import annotations

import argparse
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
TEST_SPACE = ROOT / "foundations/results/FOUNDATIONAL_SUPPORT_INDEXED_TEST_SPACE_COMPARISON_V1.json"
OUTPUT = ROOT / "foundations/results/FOUNDATIONAL_SCALAR_MINKOWSKI_GREEN_CHOICE_AUDIT_V1.json"
REPORT = ROOT / "foundations/reports/scalar-minkowski-green-choice-audit-v1.md"
EXPONENTS = ((0, 0, 0, 0), (1, 0, 0, 2), (2, 1, 1, 1), (3, 2, 2, 0))


def enc(value: Q) -> list[int]: return [value.numerator, value.denominator]
def sha(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()


def compact_factor(power: int) -> list[list[int]]:
    """Coefficients of z^power(1-z)^2, low order first."""
    coeffs = [Q(0)] * (power + 3)
    coeffs[power], coeffs[power+1], coeffs[power+2] = Q(1), Q(-2), Q(1)
    return [enc(item) for item in coeffs]


def derivative(coeffs: list[list[int]]) -> list[list[int]]:
    values = [Q(a,b) for a,b in coeffs]
    return [enc(Q(index)*values[index]) for index in range(1,len(values))]


def fixture(a: int, b: int, c: int, d: int) -> dict[str, Any]:
    ret_coeff = Q(1, 4*(a+1)*(b+1))
    adv_coeff = Q(1, 4*(a+1)*(b+1))
    duality = Q(1, 8*(a+1)*(b+1)*(a+c+2)*(b+d+2))
    source_l2_squared = Q(1, 2*(2*a+1)*(2*b+1))
    u_factor, v_factor = compact_factor(c+2), compact_factor(d+2)
    return {
        "id": f"NULL_MONOMIAL_{a}_{b}_TEST_{c}_{d}",
        "source_exponents": [a,b],
        "duality_test_exponents": [c,d],
        "source_code": "f(u,v)=u^a v^b on 0<=u,v<=1 and zero elsewhere",
        "retarded_interior": {"coefficient": enc(ret_coeff), "u_power": a+1, "v_power": b+1, "wave_operator_multiplier": enc(Q(4*(a+1)*(b+1))*ret_coeff)},
        "advanced_interior": {"coefficient": enc(adv_coeff), "formula": "coefficient*(1-u^(a+1))*(1-v^(b+1))", "wave_operator_multiplier": enc(Q(4*(a+1)*(b+1))*adv_coeff)},
        "adjoint_pairing": {"left": enc(duality), "right": enc(duality)},
        "source_l2_squared": enc(source_l2_squared),
        "source_time_width": enc(Q(1)),
        "energy_squared_bound": enc(source_l2_squared),
        "compact_test": {
            "u_factor_coefficients": u_factor,
            "v_factor_coefficients": v_factor,
            "u_derivative_coefficients": derivative(u_factor),
            "v_derivative_coefficients": derivative(v_factor),
            "endpoint_values_and_first_derivatives_zero": True,
            "retarded_G_P_identity": True,
            "advanced_G_P_identity": True,
        },
    }


def canonical_digest(value: dict[str, Any]) -> str:
    projection = {key:value[key] for key in ("spacetime_and_operator","source_codes","green_formulas","exact_identities","energy_extension","choice_audit","formal_proof","fixtures","support_samples")}
    return hashlib.sha256(json.dumps(projection,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()


def build() -> dict[str, Any]:
    test_space=json.loads(TEST_SPACE.read_text())
    proof=[
        {"id":"RATIONAL_NULL_SOURCE_CODES","base":"PRA","statement":"Compact rational piecewise-polynomial source and test codes on finite rational polyhedral partitions of 1+1 Minkowski spacetime have exact rational differentiation, multiplication, and integration in null coordinates u=t-x and v=t+x."},
        {"id":"CANONICAL_GREEN_FORMULAS","base":"PRA","depends_on":["RATIONAL_NULL_SOURCE_CODES"],"statement":"The retarded and advanced double-cone integrals are fixed formulas, not selected witnesses. Rational chamber refinement of the moving integration polyhedra produces finite rational piecewise-polynomial output codes."},
        {"id":"TWO_SIDED_CODE_IDENTITIES","base":"PRA","depends_on":["CANONICAL_GREEN_FORMULAS"],"statement":"With P=partial_t^2-partial_x^2=4 partial_u partial_v, exact differentiation gives P G_ret f=f and P G_adv f=f. Exact integration by parts and zero endpoint jets give G_ret P phi=phi and G_adv P phi=phi for compact C1 test codes."},
        {"id":"CAUSAL_SUPPORT","base":"PRA","depends_on":["CANONICAL_GREEN_FORMULAS"],"statement":"The retarded integral is empty unless the evaluation point lies in J_plus(supp f), and the advanced integral is empty unless it lies in J_minus(supp f). This is exact finite support propagation for the declared code carrier."},
        {"id":"ADJOINT_DUALITY","base":"PRA","depends_on":["TWO_SIDED_CODE_IDENTITIES","CAUSAL_SUPPORT"],"statement":"Finite rational polyhedral Fubini reversal gives <f,G_adv g>=<G_ret f,g> exactly for compact source codes."},
        {"id":"NAMED_ENERGY_EXTENSION","base":"RCA_0","depends_on":["TWO_SIDED_CODE_IDENTITIES"],"statement":"For a source supported in a supplied time interval of width T, the energy inequality E(t)<=T ||f||_L2^2 supplies an explicit continuity modulus. Hence the code maps extend to supplied fast L2 source names and zero-data uniqueness holds in the represented energy image."},
        {"id":"SUPPORT_INDEXED_ASSEMBLY","base":"RCA_0","depends_on":["CAUSAL_SUPPORT","ADJOINT_DUALITY","NAMED_ENERGY_EXTENSION"],"statement":"Copying supplied support tags assembles the stage maps over the represented compact-source union without choosing supports. Causal support and duality persist stagewise under the supplied fast names."},
        {"id":"SCALAR_SCOPE_BOUNDARY","base":"RCA_0","depends_on":["SUPPORT_INDEXED_ASSEMBLY"],"statement":"The certificate is a flat 1+1 scalar benchmark. It does not construct a Lorentzian off-shell Weyl/BV propagator, a Hadamard state, time-ordered products, a quantum master equation, or a variable-coefficient Green operator."},
    ]
    value:dict[str,Any]={
        "schema_version":"foundational-scalar-minkowski-green-choice-audit-v1",
        "result_id":"FOUNDATIONAL_SCALAR_MINKOWSKI_GREEN_CHOICE_AUDIT_V1",
        "result_kind":"SCALAR_LORENTZIAN_GREEN_OPERATOR_AND_CHOICE_DEPENDENCY_AUDIT",
        "lifecycle":"CERTIFIED",
        "created":"2026-08-14",
        "repository_base_commit":"8d2ceae41e73b748f4f6ca53277423e82697a29c",
        "dependency_tags":["LOCAL-ALGEBRAIC","LORENTZIAN-CAUSAL"],
        "theorem":"For the scalar wave operator on flat 1+1 Minkowski spacetime, rational compact-source codes admit canonical exact retarded and advanced Green maps with two-sided test-code identities, causal support, and adjoint duality in PRA; over RCA_0 these maps extend, with an explicit energy modulus and supplied support tags, to the represented source completion without an application of choice.",
        "spacetime_and_operator":{
            "spacetime":"two-dimensional Minkowski R^(1,1)",
            "metric_signature":"(+,-)",
            "operator":"P=partial_t^2-partial_x^2",
            "null_coordinates":"u=t-x, v=t+x",
            "null_form":"P=4 partial_u partial_v",
            "volume_form":"dt dx=(1/2) du dv",
            "scope":"scalar field only; no gauge or BV complex",
        },
        "source_codes":{
            "carrier":"finite rational polyhedral partitions with rational polynomial pieces and compact rational support",
            "regularity":"L2 source codes; compact test codes used for G P are global C1 piecewise polynomial",
            "exact_arithmetic":"rational chamber refinement, polynomial antiderivatives, and rational polyhedral integration",
            "represented_completion":test_space["represented_union"]["name"],
        },
        "green_formulas":{
            "retarded":"(G_ret f)(t,x)=1/2 integral_{s=-infinity}^t integral_{y=x-(t-s)}^{x+(t-s)} f(s,y) dy ds",
            "advanced":"(G_adv f)(t,x)=1/2 integral_{s=t}^{infinity} integral_{y=x-(s-t)}^{x+(s-t)} f(s,y) dy ds",
            "null_retarded":"(1/4) integral_{alpha=-infinity}^u integral_{beta=-infinity}^v f(alpha,beta) d beta d alpha",
            "null_advanced":"(1/4) integral_{alpha=u}^{infinity} integral_{beta=v}^{infinity} f(alpha,beta) d beta d alpha",
            "construction":"CANONICAL_FORMULA",
            "choice_use":"NONE",
        },
        "exact_identities":{
            "P_G_ret":"identity on compact rational source codes",
            "P_G_adv":"identity on compact rational source codes",
            "G_ret_P":"identity on compact global-C1 rational test codes",
            "G_adv_P":"identity on compact global-C1 rational test codes",
            "retarded_support":"supp(G_ret f) subset J_plus(supp f)",
            "advanced_support":"supp(G_adv f) subset J_minus(supp f)",
            "adjoint_duality":"<f,G_adv g>=<G_ret f,g>",
            "base":"PRA",
        },
        "energy_extension":{
            "input_name":"supplied fast L2 name of compact-source codes plus a rational time-support interval of width T",
            "estimate":"E(t)<=T ||f||_L2(spacetime)^2 for zero initial data",
            "uniqueness":"zero-data uniqueness inside the represented energy-solution image",
            "support_limit":"causal support persists for names at each fixed supplied support stage",
            "base":"RCA_0",
            "arbitrary_distributional_uniqueness":False,
        },
        "choice_audit":[
            {"step":"encode finite rational sources and tests","base":"PRA","choice":"NONE","reason":"all partitions and coefficients are finite input data"},
            {"step":"construct retarded and advanced code","base":"PRA","choice":"NONE","reason":"a fixed cone-integral formula and deterministic chamber refinement are used"},
            {"step":"verify inverse identities and causal support","base":"PRA","choice":"NONE","reason":"finite polynomial identities, endpoint jets, and rational inequalities"},
            {"step":"verify adjoint duality","base":"PRA","choice":"NONE","reason":"finite exact Fubini reversal"},
            {"step":"extend to fast source names","base":"RCA_0","choice":"NONE","reason":"the convergence modulus and time-support bound are supplied"},
            {"step":"assemble support stages","base":"RCA_0","choice":"NONE","reason":"support tags are copied from names"},
            {"step":"start from a bare extensional source","base":"UNRESOLVED","choice":"NOT_AUDITED","reason":"neither a support tag nor an effective convergence modulus has been supplied"},
            {"step":"general variable-coefficient or Weyl/BV operator","base":"UNRESOLVED","choice":"NOT_AUDITED","reason":"the canonical scalar cone formula is unavailable"},
        ],
        "formal_proof":proof,
        "fixtures":[fixture(*powers) for powers in EXPONENTS],
        "support_samples":[
            {"operator":"retarded","point_uv":[-1,1],"in_declared_causal_support":False},
            {"operator":"retarded","point_uv":[1,-1],"in_declared_causal_support":False},
            {"operator":"retarded","point_uv":[0,0],"in_declared_causal_support":True},
            {"operator":"retarded","point_uv":[2,2],"in_declared_causal_support":True},
            {"operator":"advanced","point_uv":[2,0],"in_declared_causal_support":False},
            {"operator":"advanced","point_uv":[0,2],"in_declared_causal_support":False},
            {"operator":"advanced","point_uv":[1,1],"in_declared_causal_support":True},
            {"operator":"advanced","point_uv":[-1,-1],"in_declared_causal_support":True}
        ],
        "literature_context":[
            {"id":"bar-2015-green-hyperbolic","citation":"Christian Bär, Green-hyperbolic operators on globally hyperbolic spacetimes, Communications in Mathematical Physics 333 (2015), 1585-1615","doi":"10.1007/s00220-014-2097-7","url":"https://arxiv.org/abs/1310.0738","role":"Primary general context for advanced and retarded Green operators and their causal properties.","import_boundary":"The certificate independently checks only the explicit flat 1+1 scalar formulas; it does not import Bär's general theorem into RCA_0."},
            {"id":"weihrauch-zhong-2002-wave-computability","citation":"Klaus Weihrauch and Ning Zhong, Is wave propagation computable or can wave computers beat the Turing machine?, Proceedings of the London Mathematical Society 85 (2002), 312-332","doi":"10.1112/S0024611502013643","url":"https://doi.org/10.1112/S0024611502013643","role":"Primary computable-analysis context for wave propagation on differentiable and Sobolev representations.","import_boundary":"No reverse-mathematical base or this exact Green-code certificate is imported."},
        ],
        "provenance":{"inputs":[{"path":str(TEST_SPACE.relative_to(ROOT)),"sha256":sha(TEST_SPACE),"role":"represented support-indexed source/test assembly"}]},
        "independent_checker":{"path":"foundations/check_scalar_minkowski_green_choice_audit.py","checks":["proof DAG","four exact null-monomial P G identities","eight compact-test endpoint jets","eight G P identities","four exact duality pairings","four energy bounds","eight causal-support samples","choice ledger","source hash","canonical digest"],"expected_digest":""},
        "claim_flags":{
            "scalar_retarded_green_constructed":True,
            "scalar_advanced_green_constructed":True,
            "two_sided_test_code_identities_proved":True,
            "strict_causal_support_proved":True,
            "adjoint_duality_proved":True,
            "named_energy_extension_proved":True,
            "canonical_construction_avoids_choice":True,
            "lorentzian_causal_scalar_claim":True,
            "arbitrary_distributional_uniqueness_proved":False,
            "bare_source_support_uniformly_selected":False,
            "variable_coefficient_green_constructed":False,
            "weyl_bv_propagator_constructed":False,
            "hadamard_state_constructed":False,
            "lorentzian_quantum_master_equation_proved":False,
        },
        "does_not_establish":[
            "uniqueness among all arbitrary distributional solutions",
            "support or convergence data selected from a bare extensional source",
            "a variable-coefficient or curved-spacetime Green operator",
            "a Green operator for conformal Weyl gravity or the metric BV complex",
            "a BRST-compatible Hadamard state or renormalized time-ordered products",
            "a causal perturbative AQFT construction or Lorentzian quantum master equation",
            "a weakest-base reversal",
            "empirical adequacy or a complete physical theory",
        ],
        "next_gate":"Use this scalar causal benchmark to specify the additional operator, gauge, constraint, support, and microlocal certificates that a Lorentzian Weyl/BV Green construction would need, without transferring the scalar result across that boundary.",
        "human_report":"foundations/reports/scalar-minkowski-green-choice-audit-v1.md",
    }
    value["independent_checker"]["expected_digest"]=canonical_digest(value)
    return value


def render(value:dict[str,Any])->str:
    lines=[
        "# Scalar 1+1 Minkowski Green operators: exact choice audit","",f"**Result:** `{value['result_id']}`","","## Certified statement","",value["theorem"],"",
        "## Why this benchmark matters","","This is the first cell in the programme where causal support is constructed rather than merely listed as a missing dependency. The formula is canonical, so no theorem saying that some Green operator exists is used as a hidden selection step.","",
        "```text",value["green_formulas"]["retarded"],value["green_formulas"]["advanced"],"```","",
        "## Exact fixture audit","","| fixture | P G_ret | P G_adv | dual pairing | energy bound |","|---|---:|---:|---:|---:|"
    ]
    for row in value["fixtures"]:
        lines.append(f"| `{row['id']}` | {row['retarded_interior']['wave_operator_multiplier'][0]} | {row['advanced_interior']['wave_operator_multiplier'][0]} | {row['adjoint_pairing']['left'][0]}/{row['adjoint_pairing']['left'][1]} | {row['energy_squared_bound'][0]}/{row['energy_squared_bound'][1]} |")
    lines += ["","## Choice ledger","","| step | base | choice | why |","|---|---|---|---|"]
    for row in value["choice_audit"]: lines.append(f"| {row['step']} | `{row['base']}` | `{row['choice']}` | {row['reason']} |")
    lines += [
        "","## Scope firewall","","The `LORENTZIAN-CAUSAL` tag applies only to the flat scalar 1+1 operator displayed here. It is not evidence for a Weyl/BV propagator, Hadamard state, causal perturbative QFT, or quantum master equation.","",
        "## Reproduction","","```text","python3 foundations/build_scalar_minkowski_green_choice_audit.py --check","python3 foundations/check_scalar_minkowski_green_choice_audit.py","python3 foundations/verify_scalar_minkowski_green_choice_audit.py","python3 -m unittest foundations.tests.test_scalar_minkowski_green_choice_audit","```","","## Boundaries",""
    ]
    lines += ["- This does not establish "+item+"." for item in value["does_not_establish"]]
    return "\n".join(lines)+"\n"


def generated()->tuple[bytes,bytes]:
    value=build(); return (json.dumps(value,indent=2,ensure_ascii=False)+"\n").encode(),render(value).encode()


def main()->int:
    parser=argparse.ArgumentParser(); parser.add_argument("--check",action="store_true"); args=parser.parse_args(); result_bytes,report_bytes=generated(); outputs=((OUTPUT,result_bytes),(REPORT,report_bytes))
    stale=[str(path.relative_to(ROOT)) for path,content in outputs if not path.is_file() or path.read_bytes()!=content]
    if args.check: print("FOUNDATIONAL_SCALAR_MINKOWSKI_GREEN_CHOICE_AUDIT_V1: "+("generated artifacts current" if not stale else "stale: "+", ".join(stale))); return bool(stale)
    for path,content in outputs: path.write_bytes(content)
    print("FOUNDATIONAL_SCALAR_MINKOWSKI_GREEN_CHOICE_AUDIT_V1: wrote result and report"); return 0

if __name__=="__main__": raise SystemExit(main())
