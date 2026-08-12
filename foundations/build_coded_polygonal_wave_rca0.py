#!/usr/bin/env python3
"""Generate the coded polygonal-cylinder wave upper-bound certificate."""
from __future__ import annotations

import argparse
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "foundations/results/FOUNDATIONAL_CODED_POLYGONAL_WAVE_RCA0_V1.json"
REPORT = ROOT / "foundations/reports/coded-polygonal-wave-rca0.md"

FIXTURES = [
    {"id": "TRIANGLE_RIGHT", "breaks": [[0, 1], [1, 2], [1, 1]], "right": [[1, 1], [-1, 1]], "left": [[0, 1], [0, 1]]},
    {"id": "QUARTER_MIXED", "breaks": [[0, 1], [1, 4], [1, 2], [3, 4], [1, 1]], "right": [[2, 1], [-1, 1], [-1, 1], [0, 1]], "left": [[1, 1], [1, 1], [-1, 1], [-1, 1]]},
    {"id": "NONUNIFORM_MIXED", "breaks": [[0, 1], [1, 6], [1, 2], [3, 4], [1, 1]], "right": [[3, 1], [-3, 2], [0, 1], [0, 1]], "left": [[0, 1], [3, 1], [-2, 1], [-2, 1]]},
]


def q(x: list[int]) -> Q: return Q(x[0], x[1])
def enc(x: Q) -> list[int]: return [x.numerator, x.denominator]


def fixture_summary(item: dict[str, Any]) -> dict[str, Any]:
    breaks = [q(x) for x in item["breaks"]]
    right, left = ([q(x) for x in item[name]] for name in ("right", "left"))
    widths = [b - a for a, b in zip(breaks, breaks[1:])]
    means = [sum((w * v for w, v in zip(widths, values)), Q()) for values in (right, left)]
    energies = [sum((w * v * v for w, v in zip(widths, values)), Q()) for values in (right, left)]
    constant = 4 * (len(right) * max((abs(x) for x in right), default=Q()) ** 2 + len(left) * max((abs(x) for x in left), default=Q()) ** 2)
    moduli = []
    for precision in range(1, 9):
        delta = min(min(widths) / 2, Q(1, 2 ** (2 * precision)) / constant) if constant else min(widths) / 2
        index = 0
        while Q(1, 2**index) > delta: index += 1
        moduli.append({"precision": precision, "time_name_index": index, "certified_delta": enc(Q(1, 2**index))})
    return {**item, "zero_mean_checks": [enc(x) for x in means], "chiral_energies": [enc(x) for x in energies], "total_energy": enc(sum(energies)), "minimum_cell_width": enc(min(widths)), "translation_bound_constant": enc(constant), "time_continuity_moduli": moduli}


def digest(fixtures: list[dict[str, Any]], proof: list[dict[str, Any]], diagonal: dict[str, Any]) -> str:
    payload = {"fixtures": fixtures, "formal_proof": proof, "diagonal_construction": diagonal}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def build() -> dict[str, Any]:
    fixtures = [fixture_summary(x) for x in FIXTURES]
    proof = [
        {"id": "FINITE_CODE", "base": "PRA", "statement": "Finite rational partitions, zero-mean step pairs, exact L2 inner products, polygonal primitives, and rational translations are primitive-recursively coded."},
        {"id": "RATIONAL_GROUP", "base": "PRA", "depends_on": ["FINITE_CODE"], "statement": "S_q(a,b)=(T_q a,T_-q b) is a rational-time group action on the dense code and preserves zero mean."},
        {"id": "ENERGY_ISOMETRY", "base": "PRA", "depends_on": ["RATIONAL_GROUP"], "statement": "The chiral energy d^2=integral(|a-a'|^2+|b-b'|^2) is exactly translation invariant; equivalently one half of integral(u_x^2+u_t^2) is conserved."},
        {"id": "CODE_MODULUS", "base": "PRA", "depends_on": ["FINITE_CODE"], "statement": "For a finite step pair p, d(S_q p,S_r p)^2 <= C_p |q-r| below half the minimum cell width, with primitive-recursive rational C_p and a displayed binary modulus."},
        {"id": "COMPLETION_NAME", "base": "RCA_0", "depends_on": ["ENERGY_ISOMETRY"], "statement": "A completed energy state is a fast Cauchy sequence of dense rational codes with d(p_i,p_j)^2<=4^-i for i<=j; applying a fixed rational translation termwise preserves its prescribed rate."},
        {"id": "REAL_TIME_EXTENSION", "base": "RCA_0", "depends_on": ["CODE_MODULUS", "COMPLETION_NAME"], "statement": "Given fast Cauchy names for a state and a real time, finite-code moduli provide a primitive-recursive diagonal name for S_t p."},
        {"id": "CAUCHY_EXISTENCE_UNIQUENESS", "base": "RCA_0", "depends_on": ["REAL_TIME_EXTENSION", "ENERGY_ISOMETRY"], "statement": "The diagonal name exists, is independent of representatives, conserves energy, has the initial value, obeys the group law, and is the unique continuous isometric extension of the dense rational-time action."},
    ]
    diagonal = {
        "inputs": "A state name (p_n) with d(p_i,p_j)<=2^-i and a real-time name (q_n) with |q_i-q_j|<=2^-i for i<=j.",
        "index_rule": "Choose a strictly increasing primitive-recursive m(k)>=k+4 so that, for the computed constants of p_(k+3) and p_(k+4), C*2^-m(k)<=2^-2(k+3).",
        "output": "z_k=S_q(m(k)) p_(k+3).",
        "adjacent_bound": "d(z_k,z_(k+1)) <= d(p_(k+3),p_(k+4)) + sqrt(C_(p_(k+4))*|q_m(k)-q_m(k+1)|) <= 2^-(k+2).",
        "fast_cauchy_bound": "For i<=j, telescoping the adjacent bounds gives d(z_i,z_j)<=2^-(i+1)<=2^-i.",
        "independence": "Interleave equivalent state or time names and repeat the same isometry/modulus estimate; the output distance is zero.",
        "logical_boundary": "All searches are bounded number searches over rational inequalities with supplied rates. No tree, subsequence, compactness, basis selection, or convergence-modulus extraction is used."
    }
    result = {
        "schema_version": "foundational-coded-polygonal-wave-rca0-v1", "result_id": "FOUNDATIONAL_CODED_POLYGONAL_WAVE_RCA0_V1",
        "result_kind": "CODED_SECOND_ORDER_ARITHMETIC_UPPER_BOUND", "lifecycle": "CERTIFIED", "created": "2026-08-12",
        "repository_base_commit": "a0c5fab221459d0938a8d66a91bf7386ab2b9fba", "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "theorem": "RCA_0 suffices for the represented mean-zero scalar wave Cauchy theorem on the coded circle completion of Q/Z: the dense carrier is rational periodic polygonal chiral data, completed states and real times are fast Cauchy names with prescribed rates, and the solution is the unique continuous isometric extension of exact rational translations.",
        "representation": {
            "geometry": "The spatial circle is the complete separable metric space coded by dense Q/Z with circular rational distance; time reals are fast Cauchy sequences of rationals.",
            "dense_state": "A pair (a,b) of zero-mean rational step functions on one finite rational partition. Their rational polygonal primitives are the right- and left-moving H1 profiles.",
            "completed_state": "A fast Cauchy sequence of dense pairs in the chiral L2 energy metric, coded by the rational condition d(p_i,p_j)^2<=4^-i for i<=j, supplied as part of the name.",
            "solution": "S_t(a,b)=(T_t a,T_-t b), corresponding to u(t,x)=f(x-t)+g(x+t) modulo the fixed mean-zero convention.",
            "energy": "E=integral(a^2+b^2)=one half integral(u_x^2+u_t^2).",
            "continuity_name": "Each finite code supplies C_p and a minimum cell width. These give an explicit time modulus; a primitive-recursive diagonal combines it with the two input Cauchy rates."
        },
        "formal_proof": proof, "diagonal_construction": diagonal, "fixtures": fixtures,
        "literature_context": [{
            "id": "fernandez-duque-shafer-yokoyama-2020", "source_kind": "PRIMARY_RESEARCH",
            "citation": "David Fernández-Duque, Paul Shafer, and Keita Yokoyama, Ekeland's variational principle in weak and strong systems of arithmetic, Selecta Mathematica 26 (2020), 68.",
            "stable_url": "https://arxiv.org/abs/1902.03915", "artifact": {"status": "CONTENT_PINNED", "locator": "https://arxiv.org/pdf/1902.03915", "sha256": "72579f36f47d21861a878568ee5d5199609a00e197e2d25e422011d387349638"},
            "supported_statement": "The paper records the standard RCA_0 coding of complete separable metric spaces by dense sets and of points by fast Cauchy sequences, and explicitly uses rational piecewise-linear functions as an equivalent dense presentation of C[a,b].",
            "boundary": "This source supplies the coding convention, not the polygonal wave theorem proved by the local certificate."
        }],
        "independent_checker": {"path": "foundations/check_coded_polygonal_wave_rca0.py", "checks": ["fixture closure", "zero-mean code", "exact rational translation group", "energy isometry", "explicit time-modulus inequality", "formal dependency DAG", "diagonal rate algebra", "forbidden-principle boundary", "canonical digest"], "expected_digest": digest(fixtures, proof, diagonal)},
        "claim_flags": {"rca0_upper_bound_for_declared_representation": True, "completed_energy_state_constructed": True, "real_time_solution_name_constructed": True, "energy_conservation_proved": True, "cauchy_uniqueness_in_declared_carrier": True, "weakest_base_proved": False, "reverse_lower_bound_proved": False, "representation_invariance_proved": False, "spacetime_distribution_constructed": False, "causal_green_operator_constructed": False, "choice_free_zf_theorem_proved": False, "new_lorentzian_claim": False},
        "does_not_establish": ["that RCA_0 is necessary or the weakest base", "a WKL_0, ACA_0, or Choice lower bound", "the same upper bound for bare finite-energy existence without a fast Cauchy name", "representation invariance", "a localized spacetime-distribution theorem", "finite propagation or an advanced/retarded Green map", "a variable-coefficient or curved-spacetime Cauchy theorem", "the biwave or metric-BV propagator", "a new LORENTZIAN-CAUSAL result"],
        "next_gate": "Formalize the coefficient-weak transport identity against a coded localized test class, then separate that from strict support and Green-map construction.",
        "human_report": "foundations/reports/coded-polygonal-wave-rca0.md"
    }
    return result


def render(r: dict[str, Any]) -> str:
    lines = ["# Coded polygonal scalar wave over RCA₀", "", f"**Result:** `{r['result_id']}`", "", "## Theorem", "", r["theorem"], "", "This closes the previous L2 formalization target for the declared representation. The supplied fast Cauchy rate is mathematical data; no modulus is extracted from bare convergence.", "", "## Representation", ""]
    lines += [f"- **{k.replace('_', ' ').title()}:** {v}" for k,v in r["representation"].items()]
    lines += ["", "## Proof ledger", "", "| Stage | Base | Statement |", "|---|---|---|"]
    lines += [f"| `{x['id']}` | `{x['base']}` | {x['statement']} |" for x in r["formal_proof"]]
    lines += ["", "## The diagonal construction", ""]
    lines += [f"- **{k.replace('_', ' ').title()}:** {v}" for k,v in r["diagonal_construction"].items()]
    lines += ["", "The adjacent estimate telescopes to the required fast Cauchy rate. Isometry makes the output independent of the chosen state representative; the same estimate makes it independent of the real-time name. The group law and energy identity hold first on rational dense codes and pass to names by this uniqueness argument.", "", "## Exact regression fixtures", "", "| Fixture | Chiral energies | Total | Moduli checked |", "|---|---|---|---:|"]
    for x in r["fixtures"]: lines.append(f"| `{x['id']}` | `{x['chiral_energies']}` | `{x['total_energy']}` | {len(x['time_continuity_moduli'])} |")
    source=r["literature_context"][0]
    lines += ["", "## Coding context", "", f"[{source['citation']}]({source['stable_url']}) records the RCA₀ fast-Cauchy completion convention and a rational polygonal dense presentation. Its consulted PDF is pinned as `{source['artifact']['sha256']}`. It does not prove this wave theorem.", "", "## Reproduction", "", "```text", "python3 foundations/build_coded_polygonal_wave_rca0.py --check", "python3 foundations/check_coded_polygonal_wave_rca0.py", "python3 foundations/verify_coded_polygonal_wave_rca0.py", "```", "", "## Boundaries", ""]
    lines += ["- This does not establish " + x + "." for x in r["does_not_establish"]]
    return "\n".join(lines)+"\n"


def generated():
    r=build(); return (json.dumps(r,indent=2,ensure_ascii=False)+"\n").encode(),render(r).encode()


def main():
    p=argparse.ArgumentParser();p.add_argument("--check",action="store_true");a=p.parse_args(); values=generated(); outputs=((OUTPUT,values[0]),(REPORT,values[1])); stale=[str(p.relative_to(ROOT)) for p,v in outputs if not p.is_file() or p.read_bytes()!=v]
    if a.check:
        if stale: print("FOUNDATIONAL_CODED_POLYGONAL_WAVE_RCA0_V1: stale: "+", ".join(stale));return 1
        print("FOUNDATIONAL_CODED_POLYGONAL_WAVE_RCA0_V1: generated artifacts current");return 0
    for p,v in outputs:p.write_bytes(v)
    print("FOUNDATIONAL_CODED_POLYGONAL_WAVE_RCA0_V1: wrote result and report");return 0


if __name__=="__main__":raise SystemExit(main())
