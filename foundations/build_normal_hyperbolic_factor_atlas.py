#!/usr/bin/env python3
"""Generate the bounded literature and dependency atlas for a Green factor theorem."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FOUNDATIONS = ROOT / "foundations"
LEDGER = FOUNDATIONS / "literature-causal-green-atlas-v1.json"
RESULT = FOUNDATIONS / "results/FOUNDATIONAL_NORMAL_HYPERBOLIC_FACTOR_ATLAS_V1.json"
REPORT = FOUNDATIONS / "reports/normal-hyperbolic-factor-foundations.md"
INPUTS = [
    FOUNDATIONS / "literature-ledger.json",
    FOUNDATIONS / "literature-supplement-known-attempts-v1.json",
    FOUNDATIONS / "literature-expansion-v2.json",
    FOUNDATIONS / "results/FOUNDATIONAL_TYPED_BIWAVE_GREEN_DEPENDENCY_AUDIT_V1.json",
    FOUNDATIONS / "results/FOUNDATIONAL_FINITE_GRAPH_WAVE_CAUSALITY_V1.json",
]

SOURCES = [
    {
        "id": "baer-2015", "source_kind": "PRIMARY_RESEARCH", "year": 2015,
        "citation": "Christian Bär, Green-hyperbolic operators on globally hyperbolic spacetimes, Communications in Mathematical Physics 333 (2015), 1585-1615.",
        "stable_url": "https://arxiv.org/abs/1310.0738",
        "artifact": {"status": "CONTENT_PINNED", "locator": "https://arxiv.org/pdf/1310.0738", "sha256": "879948318de8b4a5a74b52179f78120d074bc7773734b82495b6db4c363f4c99"},
        "bears_on": ["CARRIER_GEOMETRY", "PHYSICAL_POSTULATES", "TARGET_CLAIMS"],
        "supported_statements": ["Normally hyperbolic wave operators are Green-hyperbolic on globally hyperbolic spacetimes; advanced and retarded maps have the declared support and extend continuously to several support classes.", "For symmetric hyperbolic systems the paper proves Cauchy uniqueness, existence, finite propagation and continuous dependence."],
        "boundary": "This is a classical smooth/distributional theorem. It does not code the proof in second-order arithmetic, eliminate Choice, give a Bishop-constructive proof, or construct the Weyl metric BV propagator."
    },
    {
        "id": "muehlhoff-2010", "source_kind": "PRIMARY_RESEARCH", "year": 2011,
        "citation": "Rainer Mühlhoff, Cauchy Problem and Green's Functions for First Order Differential Operators and Algebraic Quantization, Journal of Mathematical Physics 52 (2011), 022303.",
        "stable_url": "https://arxiv.org/abs/1001.4091",
        "artifact": {"status": "CONTENT_PINNED", "locator": "https://arxiv.org/pdf/1001.4091", "sha256": "5854613e375d64cfddf98ced287f12a8819a21a48db4bf89f24fa8ed0040cda7"},
        "bears_on": ["CARRIER_GEOMETRY", "PHYSICAL_POSTULATES", "TARGET_CLAIMS"],
        "supported_statements": ["Prenormally hyperbolic first-order operators have unique advanced and retarded Green functions and a globally well-posed Cauchy problem under the stated globally hyperbolic hypotheses."],
        "boundary": "The reduction imports the normally-hyperbolic second-order theorem and remains classical; it is not a foundational-strength or Weyl-BV result."
    },
    {
        "id": "selivanova-selivanov-2013", "source_kind": "PRIMARY_RESEARCH", "year": 2017,
        "citation": "Svetlana Selivanova and Victor Selivanov, Computing Solution Operators of Boundary-value Problems for Some Linear Hyperbolic Systems of PDEs, Logical Methods in Computer Science 13(4:13) (2017).",
        "stable_url": "https://arxiv.org/abs/1305.2494",
        "artifact": {"status": "CONTENT_PINNED", "locator": "https://arxiv.org/pdf/1305.2494", "sha256": "71a4628b9e151eeb444f4db3c2d87cd2ad2f7d86e404bea9b3662da570f568be"},
        "bears_on": ["LOGIC", "CARRIER_GEOMETRY", "PHYSICAL_POSTULATES", "TARGET_CLAIMS"],
        "supported_statements": ["For symmetric hyperbolic systems on a cube with computable coefficients, the Cauchy solution operator is computable in the stated TTE representations; dissipative boundary-value problems are also treated under additional hypotheses.", "The proof uses rational finite-difference approximants with effective error estimates rather than an explicit solution formula."],
        "boundary": "A TTE computability theorem is not a Bishop-constructive derivation, an RCA_0 upper bound or reversal, or a theorem for globally hyperbolic manifolds and advanced/retarded Green support."
    },
    {
        "id": "selivanova-selivanov-2018", "source_kind": "PRIMARY_RESEARCH", "year": 2020,
        "citation": "Svetlana Selivanova and Victor Selivanov, Bit Complexity of Computing Solutions for Symmetric Hyperbolic Systems of PDEs with Guaranteed Precision, 2020.",
        "stable_url": "https://arxiv.org/abs/1807.03140",
        "artifact": {"status": "CONTENT_PINNED", "locator": "https://arxiv.org/pdf/1807.03140", "sha256": "9943569bd492d28d2ad8c70b30e4f85a852fe0e5c9fc7b7e034186691fd5893c"},
        "bears_on": ["LOGIC", "CARRIER_GEOMETRY", "PHYSICAL_POSTULATES", "TARGET_CLAIMS"],
        "supported_statements": ["The symmetric-hyperbolic computability programme admits explicit bit-complexity upper bounds under the paper's representations and coefficient hypotheses."],
        "boundary": "Complexity of represented solution operators neither supplies strict causal Green support nor calibrates a subsystem of second-order arithmetic."
    },
    {
        "id": "kostrykin-potthoff-schrader-2011", "source_kind": "PRIMARY_RESEARCH", "year": 2011,
        "citation": "Vadim Kostrykin, Jürgen Potthoff, and Robert Schrader, Finite propagation speed for solutions of the wave equation on metric graphs, 2011.",
        "stable_url": "https://arxiv.org/abs/1106.0817",
        "artifact": {"status": "CONTENT_PINNED", "locator": "https://arxiv.org/pdf/1106.0817", "sha256": "53c5f52ca32e7b9a0839287c154109d3bc04650f1eb11ceecea195fca5d33f47"},
        "bears_on": ["INFINITY", "CARRIER_GEOMETRY", "PHYSICAL_POSTULATES", "TARGET_CLAIMS"],
        "supported_statements": ["A class of self-adjoint Laplace operators on metric graphs has existence and uniqueness for the wave equation and strict finite propagation, proved by localized energy methods."],
        "boundary": "Metric graphs retain continuous edges and Hilbert/Sobolev analysis. They are not finite exact algebra, a continuum-limit theorem, or a choice-free construction."
    },
    {
        "id": "nachtergaele-raz-schlein-sims-2007", "source_kind": "PRIMARY_RESEARCH", "year": 2009,
        "citation": "Bruno Nachtergaele, Hillel Raz, Benjamin Schlein, and Robert Sims, Lieb-Robinson Bounds for Harmonic and Anharmonic Lattice Systems, Communications in Mathematical Physics 286 (2009), 1073-1098.",
        "stable_url": "https://arxiv.org/abs/0712.3820",
        "artifact": {"status": "CONTENT_PINNED", "locator": "https://arxiv.org/pdf/0712.3820", "sha256": "613ff5cc8af3f7b9734a2ca1912f33624b59050204e108071c4d200285179114"},
        "bears_on": ["INFINITY", "CARRIER_GEOMETRY", "PHYSICAL_POSTULATES", "TARGET_CLAIMS"],
        "supported_statements": ["Harmonic and specified anharmonic lattice systems satisfy Lieb-Robinson bounds, including exponentially small commutators outside an effective cone for Weyl observables."],
        "boundary": "An exponentially small tail is not strict support and is not an advanced/retarded Green operator. The result must not be promoted to continuum Lorentzian causality."
    },
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_digest(result: dict[str, Any]) -> str:
    payload = {key: result[key] for key in ("dependency_chain", "framework_findings", "cell_actions", "evidence_overlays", "bounded_search")}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def build_ledger() -> dict[str, Any]:
    return {
        "schema_version": "foundational-causal-green-literature-v1",
        "ledger_id": "FOUNDATIONAL_CAUSAL_GREEN_LITERATURE_V1",
        "created": "2026-08-12",
        "repository_base_commit": "1ec0ae4b25c0cb53859263613a8dc6a56fb85709",
        "method": {
            "scope": "Primary literature for classical, computable, Choice-sensitive, reverse-mathematical, and finite/discrete existence, evolution, Green maps, and propagation support.",
            "selection": "A source is direct only for the exact represented object it proves. Computability, constructive derivability, reverse-mathematical implication, strict support, and Lieb-Robinson decay are distinct result types.",
            "pinning": "Six openly retrievable arXiv PDF byte streams were fetched and SHA-256 hashed on 2026-08-12 without vendoring.",
            "verification_boundary": "A content hash identifies consulted bytes but does not verify a theorem. Negative search findings are bounded query results, never literature-absence claims."
        },
        "entries": SOURCES,
        "unresolved": ["No direct reverse-mathematical subsystem classification of the normally-hyperbolic Cauchy/Green theorem was located.", "No Bishop-style constructive proof of the globally hyperbolic advanced/retarded theorem was located.", "ZF operator theory does not by itself remove Choice from the analytic PDE proof.", "Finite graph cones, metric-graph finite propagation, and Lieb-Robinson bounds remain distinct."],
    }


def build_result() -> dict[str, Any]:
    result = {
        "schema_version": "foundational-normal-hyperbolic-factor-atlas-v1",
        "result_id": "FOUNDATIONAL_NORMAL_HYPERBOLIC_FACTOR_ATLAS_V1",
        "result_kind": "LITERATURE_AND_FOUNDATIONAL_DEPENDENCY_ATLAS",
        "lifecycle": "LITERATURE_SCOPED",
        "created": "2026-08-12",
        "repository_base_commit": "1ec0ae4b25c0cb53859263613a8dc6a56fb85709",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "target": "One scalar or finite-rank normally-hyperbolic factor on a globally hyperbolic spacetime, with existence, uniqueness, continuity, advanced/retarded maps, and causal support kept separate.",
        "answer": "Classical existence and strict causal support are directly established in the reviewed smooth and metric-graph literature. Computable solution operators are directly established for represented symmetric-hyperbolic systems, but the reviewed computability papers do not construct globally hyperbolic advanced/retarded Green maps. No direct second-order-arithmetic reversal or Bishop-style global Green theorem was located in the bounded search. Choice-sensitive Hilbert-space results show that the ambient operator theory cannot be treated as automatically choice-free. Exact finite graph-step Green kernels are separately certified locally.",
        "dependency_chain": [
            {"id": "CODED_GEOMETRY", "object": "globally hyperbolic spacetime, Cauchy surface, finite-rank bundle and causal relation", "classical": "USED", "computable": "MANIFOLD_VERSION_NOT_FOUND", "reverse_math": "NOT_FORMALIZED", "choice": "NOT_CLASSIFIED"},
            {"id": "OPERATOR_DATA", "object": "normally/symmetric-hyperbolic operator with domains and coefficient representation", "classical": "EXPLICIT", "computable": "DIRECT_FOR_CUBE_SYSTEMS", "reverse_math": "NOT_FORMALIZED", "choice": "ZF_HILBERT_ADJACENT_ONLY"},
            {"id": "ENERGY_ESTIMATE", "object": "local and finite-slab energy estimate", "classical": "DIRECT", "computable": "EFFECTIVE_ESTIMATES_IN_REPRESENTED_SYSTEM", "reverse_math": "NO_SUBSYSTEM_BOUND", "choice": "NOT_CLASSIFIED"},
            {"id": "CAUCHY_EXISTENCE", "object": "global solution for compactly supported Cauchy data", "classical": "DIRECT", "computable": "DIRECT_FOR_CUBE_SYSTEMS", "reverse_math": "NO_SUBSYSTEM_BOUND", "choice": "NOT_CLASSIFIED"},
            {"id": "UNIQUENESS", "object": "Cauchy uniqueness", "classical": "DIRECT", "computable": "USED_AND_EFFECTIVE_IN_SCOPE", "reverse_math": "NO_SUBSYSTEM_BOUND", "choice": "NOT_CLASSIFIED"},
            {"id": "CONTINUITY", "object": "continuous dependence in declared topologies", "classical": "DIRECT", "computable": "DIRECT_IN_TTE_REPRESENTATIONS", "reverse_math": "REPRESENTATION_NOT_CODED", "choice": "COMPLETION_DEPENDENCE_OPEN"},
            {"id": "FINITE_PROPAGATION", "object": "strict support inside the causal cone", "classical": "DIRECT", "computable": "NOT_A_STATED_OUTPUT_OF_REVIEWED_TTE_THEOREM", "reverse_math": "NOT_FORMALIZED", "choice": "NOT_CLASSIFIED"},
            {"id": "GREEN_MAPS", "object": "advanced and retarded right/left inverses on test sections", "classical": "DIRECT", "computable": "NOT_LOCATED", "reverse_math": "NOT_FORMALIZED", "choice": "NOT_CLASSIFIED"},
            {"id": "DISTRIBUTIONAL_EXTENSION", "object": "continuous extension and formal-adjoint reversal", "classical": "DIRECT", "computable": "NOT_LOCATED", "reverse_math": "NOT_FORMALIZED", "choice": "DUALITY_AND_COMPLETION_OPEN"},
        ],
        "framework_findings": [
            {"framework": "CLASSICAL_STANDARD", "status": "DIRECT_RESULT", "evidence": ["baer-2015", "muehlhoff-2010"], "establishes": ["Cauchy existence", "uniqueness", "continuous dependence for symmetric hyperbolic systems", "advanced/retarded Green maps for normally/prenormally hyperbolic operators", "strict causal support"], "does_not_establish": ["weakest base", "choice avoidance", "full Weyl BV propagator"]},
            {"framework": "COMPUTABLE_TTE", "status": "DIRECT_UPPER_BOUND_IN_REPRESENTATION", "evidence": ["weihrauch-zhong-2002", "selivanova-selivanov-2013", "selivanova-selivanov-2018"], "establishes": ["computable wave or symmetric-hyperbolic solution operators under specified representations and regularity", "effective finite-difference convergence in the stated cube systems"], "does_not_establish": ["Bishop constructive derivability", "RCA_0 proof", "advanced/retarded maps on globally hyperbolic manifolds", "strict causal-support computability"]},
            {"framework": "BISHOP_CONSTRUCTIVE", "status": "BOUNDED_SEARCH_NO_DIRECT_THEOREM", "evidence": [], "establishes": [], "does_not_establish": ["literature absence", "impossibility", "a constructive no-go"]},
            {"framework": "REVERSE_MATHEMATICS", "status": "BOUNDED_SEARCH_NO_DIRECT_REVERSAL", "evidence": ["brown-simpson-1986", "humphreys-simpson-1996", "humphreys-simpson-1999", "brattka-2008"], "establishes": ["nearby Banach/Hilbert principles have representation-sensitive strengths ranging from WKL_0 to stronger comprehension"], "does_not_establish": ["an RCA_0 upper bound", "a WKL_0 or ACA_0 lower bound for hyperbolic PDE"]},
            {"framework": "ZF_WITHOUT_COUNTABLE_CHOICE", "status": "ADJACENT_OPERATOR_THEORY_ONLY", "evidence": ["blackadar-farah-karagila-2026"], "establishes": ["substantial Hilbert/operator theory can be developed in ZF and familiar basis behavior can fail without countable Choice"], "does_not_establish": ["ZF construction of Sobolev spaces and Green maps", "choice-free hyperbolic PDE"]},
            {"framework": "FINITE_OR_DISCRETE", "status": "THREE_DISTINCT_RESULTS", "evidence": ["FOUNDATIONAL_FINITE_GRAPH_WAVE_CAUSALITY_V1", "kostrykin-potthoff-schrader-2011", "nachtergaele-raz-schlein-sims-2007"], "establishes": ["exact graph-step support for the local finite recurrence", "strict finite propagation for specified metric-graph waves", "exponential Lieb-Robinson cones for specified lattice systems"], "does_not_establish": ["that these three support notions are equivalent", "a continuum limit", "Lorentzian Green support from a Lieb-Robinson tail"]},
        ],
        "bounded_search": {
            "date": "2026-08-12",
            "queries": ["reverse mathematics wave equation", "reverse mathematics partial differential equations", "constructive mathematics hyperbolic partial differential equations existence", "computable symmetric hyperbolic systems", "Choice Hilbert spaces operator theory", "finite propagation discrete wave equation graph"],
            "screened_primary_records": 13,
            "included_new_records": 6,
            "negative_finding_rule": "NO_DIRECT_THEOREM means none was identified among the screened results; it never means that no such literature exists.",
        },
        "cell_actions": [
            {"coordinate": "CLASSICAL_STANDARD|HILBERT_OPERATOR|CAUSAL_PROPAGATION_GREEN", "old": "NOT_MAPPED", "new": "LITERATURE_RESULT", "evidence": ["kostrykin-potthoff-schrader-2011"], "basis": "Self-adjoint Hilbert-space Laplacians on metric graphs have well-posed wave evolution and strict finite propagation."},
            {"coordinate": "FINITE_DISCRETE|HILBERT_OPERATOR|EVOLUTION_WELLPOSEDNESS", "old": "NOT_MAPPED", "new": "LITERATURE_RESULT", "evidence": ["kostrykin-potthoff-schrader-2011"], "basis": "The metric-graph theorem proves existence and uniqueness for the specified finite/network geometry."},
            {"coordinate": "FINITE_DISCRETE|HILBERT_OPERATOR|CAUSAL_PROPAGATION_GREEN", "old": "NOT_MAPPED", "new": "LITERATURE_RESULT", "evidence": ["kostrykin-potthoff-schrader-2011"], "basis": "The same theorem proves strict finite propagation under its local boundary conditions."},
            {"coordinate": "WEAK_ARITHMETIC|HILBERT_OPERATOR|GENERATOR_SPECTRAL_DYNAMICS", "old": "NOT_MAPPED", "new": "PIECES_ONLY", "evidence": ["FOUNDATIONAL_NORMAL_HYPERBOLIC_FACTOR_ATLAS_V1"], "basis": "Effective evolution and reverse functional-analysis ingredients exist, but no coded generator theorem or subsystem calibration was located."},
            {"coordinate": "WEAK_ARITHMETIC|HILBERT_OPERATOR|EVOLUTION_WELLPOSEDNESS", "old": "NOT_MAPPED", "new": "PIECES_ONLY", "evidence": ["FOUNDATIONAL_NORMAL_HYPERBOLIC_FACTOR_ATLAS_V1"], "basis": "Computable solution operators are adjacent, but no second-order-arithmetic upper bound or reversal was located."},
            {"coordinate": "WEAK_ARITHMETIC|HILBERT_OPERATOR|CAUSAL_PROPAGATION_GREEN", "old": "NOT_MAPPED", "new": "PIECES_ONLY", "evidence": ["FOUNDATIONAL_NORMAL_HYPERBOLIC_FACTOR_ATLAS_V1"], "basis": "Classical support and effective evolution exist separately; their combination has not been formalized over a weak subsystem."},
            {"coordinate": "CONSTRUCTIVE_COMPUTABLE|SMOOTH_DISTRIBUTIONAL|GENERATOR_SPECTRAL_DYNAMICS", "old": "PRIORITY_GAP", "new": "PIECES_ONLY", "evidence": ["selivanova-selivanov-2013", "selivanova-selivanov-2018"], "basis": "A represented symmetric-hyperbolic solution operator is computable, but an explicit computable generator/domain/spectral theorem is still missing."},
            {"coordinate": "WEAK_CHOICE_ZF|HILBERT_OPERATOR|CAUSAL_PROPAGATION_GREEN", "old": "NOT_MAPPED", "new": "PIECES_ONLY", "evidence": ["FOUNDATIONAL_NORMAL_HYPERBOLIC_FACTOR_ATLAS_V1", "blackadar-farah-karagila-2026"], "basis": "ZF Hilbert theory and classical causal PDE are known separately; the Sobolev/Green construction has not been proved choice-free."},
            {"coordinate": "FINITE_DISCRETE|FINITE_EXACT|CAUSAL_PROPAGATION_GREEN", "old": "PIECES_ONLY", "new": "LOCAL_RESULT", "evidence": ["FOUNDATIONAL_FINITE_GRAPH_WAVE_CAUSALITY_V1"], "basis": "Exact rational retarded/advanced kernels have a certified graph-step support cone on the displayed finite fixtures."},
        ],
        "evidence_overlays": [
            {"coordinate": "CLASSICAL_STANDARD|SMOOTH_DISTRIBUTIONAL|EVOLUTION_WELLPOSEDNESS", "evidence": ["baer-2015"], "basis": "The symmetric-hyperbolic Cauchy theorem gives existence, uniqueness and continuous dependence."},
            {"coordinate": "CLASSICAL_STANDARD|SMOOTH_DISTRIBUTIONAL|CAUSAL_PROPAGATION_GREEN", "evidence": ["baer-2015", "muehlhoff-2010"], "basis": "The normally- and prenormally-hyperbolic theorems give advanced/retarded Green maps with causal support."},
            {"coordinate": "CONSTRUCTIVE_COMPUTABLE|SMOOTH_DISTRIBUTIONAL|EVOLUTION_WELLPOSEDNESS", "evidence": ["selivanova-selivanov-2013", "selivanova-selivanov-2018"], "basis": "The represented symmetric-hyperbolic solution operator is computable with effective approximation and complexity bounds in the papers' scope."},
            {"coordinate": "CONSTRUCTIVE_COMPUTABLE|SMOOTH_DISTRIBUTIONAL|CAUSAL_PROPAGATION_GREEN", "evidence": ["selivanova-selivanov-2013"], "basis": "Computable evolution is direct evidence for one ingredient, while strict globally-hyperbolic Green support remains outside the theorem."},
            {"coordinate": "FINITE_DISCRETE|ALGEBRAIC_CSTAR|CAUSAL_PROPAGATION_GREEN", "evidence": ["nachtergaele-raz-schlein-sims-2007"], "basis": "Lieb-Robinson decay supplies an effective lattice cone, explicitly distinguished from strict support."},
        ],
        "provenance": {"inputs": [{"path": str(path.relative_to(ROOT)), "sha256": sha(path)} for path in INPUTS]},
        "independent_checker": {"path": "foundations/check_normal_hyperbolic_factor_atlas.py", "checks": ["source ID closure", "content-pin closure", "dependency-stage closure", "framework boundary closure", "nine status-changing cell actions", "five evidence overlays", "canonical digest"], "expected_digest": ""},
        "claim_flags": {"classical_factor_theorem_identified": True, "computable_upper_bound_identified": True, "finite_exact_support_constructed": True, "reverse_math_strength_proved": False, "bishop_constructive_green_theorem_identified": False, "choice_free_green_theorem_proved": False, "full_biwave_reversal_proved": False, "new_weyl_bv_propagator": False},
        "does_not_establish": ["literature completeness", "a weakest subsystem", "an RCA_0, WKL_0 or ACA_0 equivalence", "a Bishop-constructive globally hyperbolic Green theorem", "Choice avoidance for Sobolev/distribution theory", "a continuum limit from finite graphs", "a full off-shell Weyl metric BV propagator", "a BRST-compatible Hadamard state", "renormalized Lorentzian products or a Lorentzian QME"],
        "human_report": "foundations/reports/normal-hyperbolic-factor-foundations.md",
    }
    result["independent_checker"]["expected_digest"] = canonical_digest(result)
    return result


def render(result: dict[str, Any]) -> str:
    lines = [
        "# Normally-hyperbolic factor: foundations and literature atlas", "", f"**Result:** `{result['result_id']}`", "", "## Answer", "", result["answer"], "",
        "## Framework findings", "", "| Framework | Finding | Evidence | What is established | Boundary |", "|---|---|---|---|---|",
    ]
    for item in result["framework_findings"]:
        lines.append(f"| `{item['framework']}` | `{item['status']}` | {', '.join(f'`{x}`' for x in item['evidence']) or 'None assigned'} | {'; '.join(item['establishes']) or 'No positive theorem assigned.'} | {'; '.join(item['does_not_establish'])} |")
    lines += ["", "## Dependency chain", "", "| Stage | Classical | Computable | Reverse mathematics | Choice |", "|---|---|---|---|---|"]
    for item in result["dependency_chain"]:
        lines.append(f"| {item['object']} | `{item['classical']}` | `{item['computable']}` | `{item['reverse_math']}` | `{item['choice']}` |")
    lines += ["", "## Immediate cube impact", "", "| Coordinate | Old | New | Why |", "|---|---|---|---|"]
    for item in result["cell_actions"]:
        lines.append(f"| `{item['coordinate']}` | `{item['old']}` | `{item['new']}` | {item['basis']} |")
    lines += ["", "## New primary-source corpus", "", "| ID | Primary record | Content pin | Direct point |", "|---|---|---|---|"]
    for source in SOURCES:
        lines.append(f"| `{source['id']}` | [{source['citation']}]({source['stable_url']}) | `{source['artifact']['sha256']}` | {source['supported_statements'][0]} |")
    lines += ["", "## Bounded negative findings", "", "The search did not locate a direct reverse-mathematical subsystem theorem or a Bishop-style globally hyperbolic Green theorem. This is a bounded corpus result, not an absence or impossibility claim.", "", f"The search screened **{result['bounded_search']['screened_primary_records']} primary records** and retained **{result['bounded_search']['included_new_records']} new records**. Queries: " + "; ".join(f"`{x}`" for x in result["bounded_search"]["queries"]) + ".", "", "## Reproduction", "", "```text", "python3 foundations/build_normal_hyperbolic_factor_atlas.py --check", "python3 foundations/check_normal_hyperbolic_factor_atlas.py", "python3 foundations/verify_normal_hyperbolic_factor_atlas.py", "```", "", "## Boundaries", ""]
    lines.extend(f"- This does not establish {item}." for item in result["does_not_establish"])
    return "\n".join(lines) + "\n"


def generated() -> tuple[bytes, bytes, bytes]:
    ledger, result = build_ledger(), build_result()
    return (json.dumps(ledger, indent=2, ensure_ascii=False) + "\n").encode(), (json.dumps(result, indent=2, ensure_ascii=False) + "\n").encode(), render(result).encode()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    values = generated()
    outputs = list(zip((LEDGER, RESULT, REPORT), values))
    stale = [str(path.relative_to(ROOT)) for path, content in outputs if not path.is_file() or path.read_bytes() != content]
    if args.check:
        if stale:
            print("FOUNDATIONAL_NORMAL_HYPERBOLIC_FACTOR_ATLAS_V1: stale: " + ", ".join(stale))
            return 1
        print("FOUNDATIONAL_NORMAL_HYPERBOLIC_FACTOR_ATLAS_V1: generated artifacts current")
        return 0
    for path, content in outputs:
        path.write_bytes(content)
    print("FOUNDATIONAL_NORMAL_HYPERBOLIC_FACTOR_ATLAS_V1: wrote ledger, result, and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
