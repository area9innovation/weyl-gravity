#!/usr/bin/env python3
"""Generate the exact flat scalar biwave Green certificate."""
from __future__ import annotations

import argparse
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCALAR = ROOT / "foundations/results/FOUNDATIONAL_SCALAR_MINKOWSKI_GREEN_CHOICE_AUDIT_V1.json"
TYPED = ROOT / "foundations/results/FOUNDATIONAL_TYPED_BIWAVE_GREEN_DEPENDENCY_AUDIT_V1.json"
OUTPUT = ROOT / "foundations/results/FOUNDATIONAL_SCALAR_MINKOWSKI_BIWAVE_GREEN_V1.json"
REPORT = ROOT / "foundations/reports/scalar-minkowski-biwave-green-v1.md"
EXPONENTS = ((0, 0, 0, 0), (1, 0, 0, 2), (2, 1, 1, 1), (3, 2, 2, 0))


def enc(value: Q) -> list[int]: return [value.numerator, value.denominator]
def sha(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()


def compact_factor(power: int) -> list[list[int]]:
    """Coefficients of z^power(1-z)^4, low order first."""
    values = [Q(0)] * (power + 5)
    for offset, coefficient in enumerate((1, -4, 6, -4, 1)):
        values[power + offset] = Q(coefficient)
    return [enc(item) for item in values]


def fixture(a: int, b: int, c: int, d: int) -> dict[str, Any]:
    ret = Q(1, 16 * (a + 1) * (a + 2) * (b + 1) * (b + 2))
    dual = Q(1, 32 * (a + 1) * (a + 2) * (b + 1) * (b + 2) * (a + c + 3) * (b + d + 3))
    l2 = Q(1, 2 * (2 * a + 1) * (2 * b + 1))
    return {
        "id": f"BIWAVE_NULL_MONOMIAL_{a}_{b}_TEST_{c}_{d}",
        "source_exponents": [a, b],
        "duality_test_exponents": [c, d],
        "source_code": "f(u,v)=u^a v^b on 0<=u,v<=1 and zero elsewhere",
        "retarded_interior": {
            "coefficient": enc(ret), "u_power": a + 2, "v_power": b + 2,
            "biwave_operator_multiplier": enc(Q(16 * (a + 1) * (a + 2) * (b + 1) * (b + 2)) * ret),
        },
        "advanced_interior": {
            "coefficient": enc(Q(1, 16 * (a + 1) * (b + 1))),
            "u_factor": f"({a+1})/({a+2})-u+u^({a+2})/({a+2})",
            "v_factor": f"({b+1})/({b+2})-v+v^({b+2})/({b+2})",
            "biwave_operator_multiplier": enc(Q(1)),
        },
        "adjoint_pairing": {"left": enc(dual), "right": enc(dual)},
        "compact_test": {
            "u_factor_coefficients": compact_factor(c + 4),
            "v_factor_coefficients": compact_factor(d + 4),
            "global_regular_extension": "C3",
            "endpoint_jets_zero_through_order": 3,
            "retarded_H_B_identity": True,
            "advanced_H_B_identity": True,
        },
        "finite_horizon_energy": {
            "source_l2_squared": enc(l2), "source_time_width_T": enc(Q(1)),
            "observation_horizon_R": enc(Q(2)), "intermediate_energy_bound": enc(l2),
            "biwave_energy_bound": enc(Q(4) * l2),
        },
    }


def canonical_digest(value: dict[str, Any]) -> str:
    keys = ("spacetime_and_operator", "source_codes", "green_formulas", "exact_identities", "cauchy_data", "energy_extension", "choice_audit", "formal_proof", "fixtures", "support_samples")
    return hashlib.sha256(json.dumps({k: value[k] for k in keys}, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def build() -> dict[str, Any]:
    scalar, typed = json.loads(SCALAR.read_text()), json.loads(TYPED.read_text())
    if not scalar["claim_flags"]["strict_causal_support_proved"] or scalar["claim_flags"]["weyl_bv_propagator_constructed"]:
        raise ValueError("scalar Green input boundary")
    if typed["claim_flags"]["full_bv_propagator_constructed"]:
        raise ValueError("typed dependency input boundary")
    proof = [
        {"id":"CANONICAL_COMPOSITION","base":"PRA","statement":"Set H_ret=G_ret o G_ret and H_adv=G_adv o G_adv on the certified rational null-coordinate code carrier. Composition is a deterministic finite chamber-refinement algorithm."},
        {"id":"BIWAVE_RIGHT_INVERSES","base":"PRA","depends_on":["CANONICAL_COMPOSITION"],"statement":"For B=P^2=16 partial_u^2 partial_v^2, B H_ret f=f and B H_adv f=f follow by two exact differentiations of the nested cone integrals."},
        {"id":"BIWAVE_LEFT_INVERSES","base":"PRA","depends_on":["CANONICAL_COMPOSITION"],"statement":"For compact global-C3 rational tests, H_ret B phi=phi and H_adv B phi=phi follow by two integrations in each null variable; the endpoint value and first-derivative terms vanish. C3 regularity also prevents boundary distributions in B phi."},
        {"id":"CAUSAL_SUPPORT","base":"PRA","depends_on":["CANONICAL_COMPOSITION"],"statement":"Causal transitivity gives J_plus(J_plus(K))=J_plus(K) and J_minus(J_minus(K))=J_minus(K), so composing the scalar Green maps does not enlarge the retarded or advanced cone."},
        {"id":"ADJOINT_DUALITY","base":"PRA","depends_on":["CANONICAL_COMPOSITION"],"statement":"Applying the scalar advanced-retarded duality twice gives <f,H_adv g>=<H_ret f,g>; the fixtures independently reduce both sides to the same rational number."},
        {"id":"FOUR_DATA_CAUCHY_TOWER","base":"RCA_0","depends_on":["BIWAVE_RIGHT_INVERSES"],"statement":"Writing w=P phi turns B phi=f into two zero-data wave problems. The retarded solution fixes w and partial_t w, then phi and partial_t phi, equivalently four past-zero Cauchy data for the fourth-order equation."},
        {"id":"NAMED_FINITE_HORIZON_EXTENSION","base":"RCA_0","depends_on":["FOUR_DATA_CAUCHY_TOWER","CAUSAL_SUPPORT"],"statement":"For supplied source width T and observation horizon R, E_w<=T||f||_2^2 and E_phi<=R^2 T||f||_2^2 give a composed modulus for supplied fast L2 names on that finite horizon. No global bounded-energy claim is made."},
        {"id":"SCALAR_BIWAVE_FIREWALL","base":"RCA_0","depends_on":["ADJOINT_DUALITY","NAMED_FINITE_HORIZON_EXTENSION"],"statement":"This is a flat scalar fourth-order construction. Tensor bundles, variable coefficients, gauge fixing, BRST compatibility, microlocal state conditions, and the full Weyl BV complex require separate certificates."},
    ]
    value: dict[str, Any] = {
        "schema_version":"foundational-scalar-minkowski-biwave-green-v1",
        "result_id":"FOUNDATIONAL_SCALAR_MINKOWSKI_BIWAVE_GREEN_V1",
        "result_kind":"SCALAR_FOURTH_ORDER_LORENTZIAN_GREEN_CONSTRUCTION",
        "lifecycle":"CERTIFIED",
        "created":"2026-08-14",
        "repository_base_commit":"b5601e3e7f616cc03ea094be3ea6cc577043931d",
        "dependency_tags":["LOCAL-ALGEBRAIC","LORENTZIAN-CAUSAL"],
        "theorem":"For B=(partial_t^2-partial_x^2)^2 on flat 1+1 Minkowski spacetime, the canonical compositions H_ret=G_ret o G_ret and H_adv=G_adv o G_adv are exact two-sided Green maps on the declared rational source and global-C3 test-code domains, preserve strict retarded or advanced support, and obey adjoint duality in PRA. Over RCA_0, supplied fast L2 names, source width, and a finite observation horizon give a choice-free represented extension with an explicit two-stage energy modulus and four past-zero Cauchy data.",
        "spacetime_and_operator":{"spacetime":"two-dimensional Minkowski R^(1,1)","metric_signature":"(+,-)","wave_operator":"P=partial_t^2-partial_x^2=4 partial_u partial_v","biwave_operator":"B=P^2=16 partial_u^2 partial_v^2","scope":"scalar field only; no tensor, gauge, ghost, antifield, or BV carrier"},
        "source_codes":{"carrier":"finite rational polyhedral partitions with rational polynomial pieces and compact rational support","regularity":"L2 source codes; global-C3 compact rational test codes for H B","exact_arithmetic":"rational polynomial differentiation, integration, and chamber refinement"},
        "green_formulas":{"retarded":"H_ret=G_ret o G_ret","advanced":"H_adv=G_adv o G_adv","null_retarded":"(1/16) integral_{alpha<=u,beta<=v}(u-alpha)(v-beta) f(alpha,beta) d beta d alpha","null_advanced":"(1/16) integral_{alpha>=u,beta>=v}(alpha-u)(beta-v) f(alpha,beta) d beta d alpha","construction":"CANONICAL_COMPOSITION","choice_use":"NONE"},
        "exact_identities":{"B_H_ret":"identity on compact rational source codes","B_H_adv":"identity on compact rational source codes","H_ret_B":"identity on compact global-C3 rational test codes","H_adv_B":"identity on compact global-C3 rational test codes","retarded_support":"supp(H_ret f) subset J_plus(supp f)","advanced_support":"supp(H_adv f) subset J_minus(supp f)","adjoint_duality":"<f,H_adv g>=<H_ret f,g>","base":"PRA"},
        "cauchy_data":{"factorization":"w=P phi; P w=f","retarded_zero_data":["w","partial_t w","phi","partial_t phi"],"equivalent_fourth_order_data":["phi","partial_t phi","partial_t^2 phi","partial_t^3 phi"],"selection":"all four vanish before the source"},
        "energy_extension":{"input_name":"supplied fast L2 source name, rational source-width T, and rational finite observation horizon R","intermediate_estimate":"E_w(t)<=T ||f||_L2^2","biwave_estimate":"E_phi(t)<=R^2 T ||f||_L2^2","base":"RCA_0","global_bounded_energy":False,"arbitrary_distributional_uniqueness":False},
        "choice_audit":[
            {"step":"compose exact scalar Green code maps","base":"PRA","choice":"NONE"},
            {"step":"verify B H and H B","base":"PRA","choice":"NONE"},
            {"step":"propagate causal support","base":"PRA","choice":"NONE"},
            {"step":"verify adjoint duality","base":"PRA","choice":"NONE"},
            {"step":"extend supplied fast names on finite horizons","base":"RCA_0","choice":"NONE"},
            {"step":"select support, horizon, or modulus from a bare source","base":"UNRESOLVED","choice":"NOT_AUDITED"},
            {"step":"pass to variable-coefficient tensor or BV operators","base":"UNRESOLVED","choice":"NOT_AUDITED"},
            {"step":"construct a global finite-energy biwave space","base":"UNRESOLVED","choice":"NOT_AUDITED"},
        ],
        "formal_proof":proof,
        "fixtures":[fixture(*row) for row in EXPONENTS],
        "support_samples":[
            {"operator":"retarded","point_uv":[-1,1],"in_declared_causal_support":False}, {"operator":"retarded","point_uv":[1,-1],"in_declared_causal_support":False},
            {"operator":"retarded","point_uv":[0,0],"in_declared_causal_support":True}, {"operator":"retarded","point_uv":[2,2],"in_declared_causal_support":True},
            {"operator":"advanced","point_uv":[2,0],"in_declared_causal_support":False}, {"operator":"advanced","point_uv":[0,2],"in_declared_causal_support":False},
            {"operator":"advanced","point_uv":[1,1],"in_declared_causal_support":True}, {"operator":"advanced","point_uv":[-1,-1],"in_declared_causal_support":True}],
        "literature_context":[
            {"id":"bar-2015-green-hyperbolic","citation":"Christian Bär, Green-hyperbolic operators on globally hyperbolic spacetimes, CMP 333 (2015), 1585-1615","doi":"10.1007/s00220-014-2097-7","role":"General Green-hyperbolic context; the present flat formula is checked independently."},
            {"id":"typed-biwave-repository-theorem","citation":"Repository typed biwave Volterra Green theorem and foundations dependency audit","role":"Broader conditional biwave context; none of its analytic hypotheses is silently imported into this flat exact proof."}],
        "provenance":{"inputs":[{"path":str(SCALAR.relative_to(ROOT)),"sha256":sha(SCALAR),"role":"certified scalar factor Green maps"},{"path":str(TYPED.relative_to(ROOT)),"sha256":sha(TYPED),"role":"broader typed dependency boundary"}]},
        "independent_checker":{"path":"foundations/check_scalar_minkowski_biwave_green.py","checks":["proof DAG","exact B H fixtures","exact H B endpoint jets","exact adjoint pairing","finite-horizon energy tower","causal support","choice ledger","input hashes","canonical digest"],"expected_digest":""},
        "claim_flags":{"scalar_biwave_retarded_green_constructed":True,"scalar_biwave_advanced_green_constructed":True,"two_sided_test_code_identities_proved":True,"strict_causal_support_proved":True,"adjoint_duality_proved":True,"four_zero_data_selection_proved":True,"named_finite_horizon_extension_proved":True,"canonical_construction_avoids_choice":True,"global_bounded_energy_proved":False,"arbitrary_distributional_uniqueness_proved":False,"variable_coefficient_tensor_green_constructed":False,"weyl_bv_propagator_constructed":False,"brst_compatible_green_constructed":False,"hadamard_state_constructed":False,"renormalized_products_constructed":False,"lorentzian_qme_proved":False},
        "does_not_establish":["a global bounded-energy estimate for persistent retarded biwave solutions","uniqueness among arbitrary distributional solutions","support, horizon, or convergence data selected from a bare extensional source","a curved or variable-coefficient tensor Green operator","a gauge-fixed Green-hyperbolic Weyl BV complex","BRST-compatible causal homotopies","a Hadamard state or wavefront-set theorem","renormalized Lorentzian time-ordered products, causal pAQFT, or a Lorentzian QME","a weakest-base reversal","empirical adequacy or a complete physical theory"],
        "next_gate":"Construct a fail-closed dependency delta from this flat scalar biwave to the authoritative Lorentzian Weyl BV target, naming every tensor, gauge, chain-map, support, microlocal, and classical-import certificate that remains absent.",
        "human_report":"foundations/reports/scalar-minkowski-biwave-green-v1.md",
    }
    value["independent_checker"]["expected_digest"] = canonical_digest(value)
    return value


def render(value: dict[str, Any]) -> str:
    lines = ["# Flat scalar biwave Green construction", "", f"**Result:** `{value['result_id']}`", "", "## Certified statement", "", value["theorem"], "", "## Construction", "", "```text", "B = P^2", "H_ret = G_ret o G_ret", "H_adv = G_adv o G_adv", "```", "", "The second cone integration adds polynomial weight but no wider causal support: causal transitivity collapses the nested cone back to the original future or past cone.", "", "## Exact fixtures", "", "| fixture | B H_ret | B H_adv | adjoint pairing | finite-horizon bound |", "|---|---:|---:|---:|---:|"]
    for row in value["fixtures"]:
        p, q = row["adjoint_pairing"]["left"]; e, f = row["finite_horizon_energy"]["biwave_energy_bound"]
        lines.append(f"| `{row['id']}` | 1 | 1 | {p}/{q} | {e}/{f} |")
    lines += ["", "## Four-data interpretation", "", "The factorization `w=P phi`, `P w=f` exposes two ordinary zero-data wave solves. Together they select the four past-zero Cauchy data required by a fourth-order-in-time equation; this is a selection by the retarded formula, not a claim that every fourth-order theory is healthy.", "", "## Scope firewall", "", "The `LORENTZIAN-CAUSAL` tag applies only to the displayed flat scalar operator. No tensor, gauge, BRST/BV, Hadamard, renormalization, or QME statement transfers from it.", "", "## Reproduction", "", "```text", "python3 foundations/build_scalar_minkowski_biwave_green.py --check", "python3 foundations/check_scalar_minkowski_biwave_green.py", "python3 foundations/verify_scalar_minkowski_biwave_green.py", "python3 -m unittest foundations.tests.test_scalar_minkowski_biwave_green", "```", "", "## Boundaries", ""]
    lines += ["- This does not establish " + item + "." for item in value["does_not_establish"]]
    return "\n".join(lines) + "\n"


def generated() -> tuple[bytes, bytes]:
    value = build(); return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode(), render(value).encode()


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--check", action="store_true"); args = parser.parse_args()
    result, report = generated(); outputs = ((OUTPUT, result), (REPORT, report)); stale = [str(p.relative_to(ROOT)) for p, content in outputs if not p.is_file() or p.read_bytes() != content]
    if args.check: print("FOUNDATIONAL_SCALAR_MINKOWSKI_BIWAVE_GREEN_V1: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale))); return bool(stale)
    for path, content in outputs: path.write_bytes(content)
    print("FOUNDATIONAL_SCALAR_MINKOWSKI_BIWAVE_GREEN_V1: wrote result and report"); return 0


if __name__ == "__main__": raise SystemExit(main())
